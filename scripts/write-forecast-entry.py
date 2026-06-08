#!/usr/bin/env python3
"""
QGIA Knowledge Spine — Forecast Ledger Writer
Phase 1.2: Validated append-only ledger entry writer.

Usage (CLI):
    python scripts/write-forecast-entry.py --help
    python scripts/write-forecast-entry.py \
        --theater Iran \
        --scenario-id IRN_REGIME_H1_HARDLINE_SURVIVAL \
        --scenario-label "Hardline survival" \
        --window 12m \
        --probability 0.42 \
        --previous-probability 0.40 \
        --distribution-type dirichlet_component \
        --distribution-params '{"concentration": 4.2}' \
        --data-quality 0.78 \
        --source-reliability 0.74 \
        --methodological-rigor 0.82 \
        --temporal-stability 0.71 \
        --notes "Khamenei succession signals shifted hardliner consolidation"

Usage (Python API):
    from scripts.write_forecast_entry import ForecastEntry, append_entry
    entry = ForecastEntry(...)
    append_entry(entry)
"""

import csv
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import structlog

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "data" / "forecast-ledger.jsonl"

# ---------------------------------------------------------------------------
# CCS formula weights (from probability-ledger-schema.md)
# CCS = (0.30 × DQ) + (0.25 × SR) + (0.25 × MR) + (0.20 × TS)
# ---------------------------------------------------------------------------
CCS_WEIGHTS = {"data_quality": 0.30, "source_reliability": 0.25,
               "methodological_rigor": 0.25, "temporal_stability": 0.20}

VALID_DISTRIBUTION_TYPES = {"beta", "dirichlet_component", "hazard", "bernoulli"}
VALID_WINDOWS = {"0-30d", "0-60d", "0-90d", "0-180d", "6m", "12m", "6-12m"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class ForecastEntry:
    theater: str
    scenario_id: str
    scenario_label: str
    window: str
    probability: float
    previous_probability: float
    distribution_type: str
    data_quality: float
    source_reliability: float
    methodological_rigor: float
    temporal_stability: float
    notes: str
    distribution_params: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    @property
    def delta_probability(self) -> float:
        return round(self.probability - self.previous_probability, 4)

    @property
    def confidence_score(self) -> float:
        return round(
            CCS_WEIGHTS["data_quality"] * self.data_quality
            + CCS_WEIGHTS["source_reliability"] * self.source_reliability
            + CCS_WEIGHTS["methodological_rigor"] * self.methodological_rigor
            + CCS_WEIGHTS["temporal_stability"] * self.temporal_stability,
            4,
        )

    def validate(self) -> None:
        """Raises ValueError on any schema violation."""
        errors = []

        if not self.theater.strip():
            errors.append("theater must be a non-empty string")

        if not self.scenario_id.strip():
            errors.append("scenario_id must be a non-empty string")

        if self.distribution_type not in VALID_DISTRIBUTION_TYPES:
            errors.append(
                f"distribution_type '{self.distribution_type}' not in "
                f"{VALID_DISTRIBUTION_TYPES}"
            )

        for prob_field, val in [
            ("probability", self.probability),
            ("previous_probability", self.previous_probability),
        ]:
            if not (0.0 <= val <= 1.0):
                errors.append(f"{prob_field} must be in [0.0, 1.0], got {val}")

        for score_field, val in [
            ("data_quality", self.data_quality),
            ("source_reliability", self.source_reliability),
            ("methodological_rigor", self.methodological_rigor),
            ("temporal_stability", self.temporal_stability),
        ]:
            if not (0.0 <= val <= 1.0):
                errors.append(f"{score_field} must be in [0.0, 1.0], got {val}")

        if errors:
            raise ValueError("ForecastEntry validation failed:\n  " + "\n  ".join(errors))

    def to_jsonl_row(self) -> str:
        """Return a single JSON line for appending to the ledger."""
        row = {
            "timestamp": self.timestamp,
            "theater": self.theater,
            "scenario_id": self.scenario_id,
            "scenario_label": self.scenario_label,
            "window": self.window,
            "probability": self.probability,
            "previous_probability": self.previous_probability,
            "delta_probability": self.delta_probability,
            "distribution_type": self.distribution_type,
            "distribution_params": json.dumps(self.distribution_params),
            "confidence_score": self.confidence_score,
            "data_quality": self.data_quality,
            "source_reliability": self.source_reliability,
            "methodological_rigor": self.methodological_rigor,
            "temporal_stability": self.temporal_stability,
            "notes": self.notes,
        }
        return json.dumps(row, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Update-rule gate
# ---------------------------------------------------------------------------
def _passes_update_rules(entry: ForecastEntry, ledger_path: Path) -> tuple[bool, str]:
    """
    Return (True, reason) if the entry should be written per QGIA update rules:
      - |delta| >= 0.03
      - scenario is new (no prior entries for this scenario_id + window)
      - notes signal a major exogenous shock or window roll
      - force flag is set (bypass via --force)
    Return (False, reason) if the entry would be a no-op write.
    """
    abs_delta = abs(entry.delta_probability)
    if abs_delta >= 0.03:
        return True, f"|delta| = {abs_delta:.4f} >= 0.03 threshold"

    if not ledger_path.exists() or ledger_path.stat().st_size < 5:
        return True, "ledger is empty — first entry always written"

    existing_ids = set()
    with open(ledger_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    row = json.loads(line)
                    existing_ids.add((row.get("scenario_id"), row.get("window")))
                except json.JSONDecodeError:
                    pass

    if (entry.scenario_id, entry.window) not in existing_ids:
        return True, "new scenario_id + window combination — initial entry written"

    shock_keywords = {"shock", "collapse", "strike", "decision", "escalat", "ceasefire",
                      "detonation", "coup", "invasion", "breakthrough", "window roll"}
    notes_lower = entry.notes.lower()
    if any(kw in notes_lower for kw in shock_keywords):
        return True, "notes contain exogenous shock keyword"

    return False, (
        f"|delta| = {abs_delta:.4f} < 0.03 and no shock keywords detected; "
        "entry skipped per update rules. Use --force to override."
    )


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------
def append_entry(entry: ForecastEntry, force: bool = False) -> dict:
    """
    Validate, gate, and append a forecast entry to the ledger.
    Returns a result dict with keys: written (bool), reason (str), path (str).
    """
    entry.validate()

    passes, reason = _passes_update_rules(entry, LEDGER_PATH)

    if not passes and not force:
        log.info("entry_skipped", reason=reason, scenario_id=entry.scenario_id)
        return {"written": False, "reason": reason, "path": str(LEDGER_PATH)}

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(entry.to_jsonl_row() + "\n")

    log.info(
        "entry_written",
        scenario_id=entry.scenario_id,
        theater=entry.theater,
        probability=entry.probability,
        confidence_score=entry.confidence_score,
        delta=entry.delta_probability,
        reason=reason,
    )
    return {"written": True, "reason": reason, "path": str(LEDGER_PATH)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
@click.command()
@click.option("--theater", required=True, help="Theater name (e.g. Iran, Ukraine, Venezuela)")
@click.option("--scenario-id", required=True, help="Canonical scenario identifier")
@click.option("--scenario-label", required=True, help="Human-readable scenario name")
@click.option("--window", required=True, help="Forecast horizon (e.g. 0-180d, 12m)")
@click.option("--probability", required=True, type=float, help="Current probability 0.00-1.00")
@click.option("--previous-probability", required=True, type=float, help="Previous probability 0.00-1.00")
@click.option("--distribution-type", required=True,
              type=click.Choice(["beta", "dirichlet_component", "hazard", "bernoulli"]),
              help="Distribution family")
@click.option("--distribution-params", default="{}", help="JSON string of distribution parameters")
@click.option("--data-quality", required=True, type=float, help="DQ score 0.00-1.00")
@click.option("--source-reliability", required=True, type=float, help="SR score 0.00-1.00")
@click.option("--methodological-rigor", required=True, type=float, help="MR score 0.00-1.00")
@click.option("--temporal-stability", required=True, type=float, help="TS score 0.00-1.00")
@click.option("--notes", required=True, help="Update rationale")
@click.option("--force", is_flag=True, default=False, help="Bypass update-rule gate")
def cli(
    theater, scenario_id, scenario_label, window, probability, previous_probability,
    distribution_type, distribution_params, data_quality, source_reliability,
    methodological_rigor, temporal_stability, notes, force
):
    """Append a validated forecast entry to the QGIA probability ledger."""
    try:
        params = json.loads(distribution_params)
    except json.JSONDecodeError as e:
        click.echo(f"ERROR: --distribution-params is not valid JSON: {e}", err=True)
        sys.exit(1)

    entry = ForecastEntry(
        theater=theater,
        scenario_id=scenario_id,
        scenario_label=scenario_label,
        window=window,
        probability=probability,
        previous_probability=previous_probability,
        distribution_type=distribution_type,
        distribution_params=params,
        data_quality=data_quality,
        source_reliability=source_reliability,
        methodological_rigor=methodological_rigor,
        temporal_stability=temporal_stability,
        notes=notes,
    )

    result = append_entry(entry, force=force)
    status = "WRITTEN" if result["written"] else "SKIPPED"
    click.echo(f"[{status}] {result['reason']}")
    if result["written"]:
        click.echo(f"  scenario_id   : {entry.scenario_id}")
        click.echo(f"  probability   : {entry.probability}")
        click.echo(f"  delta         : {entry.delta_probability:+.4f}")
        click.echo(f"  confidence    : {entry.confidence_score}")
        click.echo(f"  ledger path   : {result['path']}")


if __name__ == "__main__":
    cli()
