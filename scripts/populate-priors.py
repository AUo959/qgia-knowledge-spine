#!/usr/bin/env python3
"""
QGIA Knowledge Spine — Prior Table Populator
Phase 1.4: Reads forecast-ledger.jsonl and computes initialised Bayesian
prior distributions for each scenario, writing to data/priors/prior-table-runtime.json.

NOTE: This script writes to prior-table-runtime.json, NOT prior-table.json.
The bootstrap contract artifact (prior-table.json) must remain empty (priors: [])
per the knowledge contract test suite. Operational priors live in the runtime file.

Distribution logic:
  dirichlet_component rows  → grouped by (theater, window) and converted
                               to a Dirichlet concentration vector
  beta rows                 → individual Beta(alpha, beta) priors
  bernoulli rows            → Beta(alpha, beta) via moment matching
  hazard rows               → stored as raw probability with metadata

Usage:
    python scripts/populate-priors.py
    python scripts/populate-priors.py --ledger path/to/ledger.jsonl
    python scripts/populate-priors.py --dry-run
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import numpy as np
import structlog

log = structlog.get_logger()

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "data" / "forecast-ledger.jsonl"
PRIOR_TABLE_PATH = REPO_ROOT / "data" / "priors" / "prior-table-runtime.json"

# Prior table schema version
SCHEMA_VERSION = 1

# Dirichlet pseudo-count scale factor.
# Concentration vector = probability * DIRICHLET_SCALE.
# Scale=10 gives moderate informativeness; increase for stronger priors.
DIRICHLET_SCALE = 10.0

# Beta precision (kappa) for beta/bernoulli distributions.
# alpha = p * BETA_KAPPA, beta = (1-p) * BETA_KAPPA
# kappa=10 represents ~10 equivalent observations.
BETA_KAPPA = 10.0


# ---------------------------------------------------------------------------
# Ledger reader
# ---------------------------------------------------------------------------
def load_ledger(ledger_path: Path) -> list[dict]:
    """Read all valid JSONL rows from the ledger. Skips malformed lines."""
    rows = []
    if not ledger_path.exists():
        log.warning("ledger_not_found", path=str(ledger_path))
        return rows
    with open(ledger_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning("ledger_parse_error", line=i, error=str(e))
    log.info("ledger_loaded", row_count=len(rows), path=str(ledger_path))
    return rows


# ---------------------------------------------------------------------------
# Deduplication: take the most recent entry per (scenario_id, window)
# ---------------------------------------------------------------------------
def deduplicate_ledger(rows: list[dict]) -> list[dict]:
    """
    For each (scenario_id, window) pair, keep only the most recent row
    (by timestamp). This ensures priors reflect current probability state.
    """
    latest: dict[tuple, dict] = {}
    for row in rows:
        key = (row.get("scenario_id", ""), row.get("window", ""))
        existing = latest.get(key)
        if existing is None or row.get("timestamp", "") >= existing.get("timestamp", ""):
            latest[key] = row
    deduped = list(latest.values())
    log.info("ledger_deduplicated", original=len(rows), deduplicated=len(deduped))
    return deduped


# ---------------------------------------------------------------------------
# Distribution builders
# ---------------------------------------------------------------------------
def build_dirichlet_prior(group: list[dict]) -> dict:
    """
    Given a list of dirichlet_component rows sharing (theater, window),
    build a Dirichlet prior entry.
    """
    group_sorted = sorted(group, key=lambda r: r["scenario_id"])
    probs = np.array([r["probability"] for r in group_sorted])
    concentrations = (probs * DIRICHLET_SCALE).tolist()
    group_sum = float(np.sum(probs))
    mean_conf = float(np.mean([r.get("confidence_score", 0.0) for r in group_sorted]))

    scenarios = [
        {
            "scenario_id": r["scenario_id"],
            "scenario_label": r.get("scenario_label", ""),
            "probability": r["probability"],
            "concentration": round(c, 4),
        }
        for r, c in zip(group_sorted, concentrations)
    ]

    theater = group_sorted[0]["theater"]
    window = group_sorted[0]["window"]

    return {
        "prior_id": f"{theater.upper()}_{window}_DIRICHLET",
        "theater": theater,
        "window": window,
        "distribution": "dirichlet",
        "concentration_vector": [round(c, 4) for c in concentrations],
        "concentration_scale": DIRICHLET_SCALE,
        "group_sum_check": round(group_sum, 6),
        "group_sum_valid": abs(group_sum - 1.0) < 0.01,
        "mean_confidence_score": round(mean_conf, 4),
        "scenarios": scenarios,
        "source_scenario_ids": [r["scenario_id"] for r in group_sorted],
        "derived_from": "forecast-ledger.jsonl",
    }


def build_beta_prior(row: dict) -> dict:
    """
    Given a beta or bernoulli row, build a Beta(alpha, beta) prior entry
    via moment matching: alpha = p * kappa, beta = (1-p) * kappa.
    """
    p = row["probability"]
    alpha = round(p * BETA_KAPPA, 4)
    beta_param = round((1.0 - p) * BETA_KAPPA, 4)
    mean_p = alpha / (alpha + beta_param)
    variance = (alpha * beta_param) / ((alpha + beta_param) ** 2 * (alpha + beta_param + 1))

    return {
        "prior_id": f"{row['scenario_id']}_{row['window']}_BETA",
        "theater": row["theater"],
        "window": row["window"],
        "scenario_id": row["scenario_id"],
        "scenario_label": row.get("scenario_label", ""),
        "distribution": "beta",
        "alpha": alpha,
        "beta": beta_param,
        "kappa": BETA_KAPPA,
        "mean": round(mean_p, 6),
        "variance": round(float(variance), 6),
        "std_dev": round(float(np.sqrt(variance)), 6),
        "confidence_score": row.get("confidence_score", None),
        "derived_from": "forecast-ledger.jsonl",
    }


def build_hazard_prior(row: dict) -> dict:
    """Hazard-rate rows stored as raw probability with metadata."""
    return {
        "prior_id": f"{row['scenario_id']}_{row['window']}_HAZARD",
        "theater": row["theater"],
        "window": row["window"],
        "scenario_id": row["scenario_id"],
        "scenario_label": row.get("scenario_label", ""),
        "distribution": "hazard",
        "hazard_rate": row["probability"],
        "confidence_score": row.get("confidence_score", None),
        "derived_from": "forecast-ledger.jsonl",
    }


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------
def compute_priors(rows: list[dict]) -> list[dict]:
    """
    Route each row (or group of rows) to the appropriate distribution builder.
    Returns a list of prior dicts ready for the prior_table priors array.
    """
    priors = []

    dirichlet_groups: dict[tuple, list[dict]] = defaultdict(list)
    individual_rows: list[dict] = []

    for row in rows:
        dist_type = row.get("distribution_type", "")
        if dist_type == "dirichlet_component":
            key = (row["theater"], row["window"])
            dirichlet_groups[key].append(row)
        else:
            individual_rows.append(row)

    for (theater, window), group in sorted(dirichlet_groups.items()):
        prior = build_dirichlet_prior(group)
        log.info(
            "dirichlet_prior_built",
            prior_id=prior["prior_id"],
            scenarios=len(group),
            group_sum_valid=prior["group_sum_valid"],
            mean_confidence=prior["mean_confidence_score"],
        )
        priors.append(prior)

    for row in sorted(individual_rows, key=lambda r: r["scenario_id"]):
        dist_type = row.get("distribution_type", "")
        if dist_type in ("beta", "bernoulli"):
            prior = build_beta_prior(row)
            log.info(
                "beta_prior_built",
                prior_id=prior["prior_id"],
                alpha=prior["alpha"],
                beta=prior["beta"],
                mean=prior["mean"],
            )
        elif dist_type == "hazard":
            prior = build_hazard_prior(row)
            log.info("hazard_prior_built", prior_id=prior["prior_id"])
        else:
            log.warning("unknown_distribution_type", dist_type=dist_type,
                        scenario_id=row.get("scenario_id"))
            continue
        priors.append(prior)

    return priors


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------
def write_prior_table(priors: list[dict], output_path: Path, dry_run: bool = False) -> dict:
    """Construct and write the prior table JSON. Returns the written structure."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    table = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "prior_table_runtime",
        "prior_table_id": f"qgia.prior_table.{now[:10]}",
        "generated_at": now,
        "producer": "qgia-knowledge-spine",
        "effective_from": now,
        "dirichlet_scale": DIRICHLET_SCALE,
        "beta_kappa": BETA_KAPPA,
        "prior_count": len(priors),
        "theaters_covered": sorted(list({p.get("theater", "") for p in priors})),
        "priors": priors,
    }

    if dry_run:
        log.info("dry_run_mode", prior_count=len(priors), output_path=str(output_path))
        print(json.dumps(table, indent=2, ensure_ascii=False))
        return table

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log.info("prior_table_written", prior_count=len(priors), path=str(output_path))
    return table


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
@click.command()
@click.option("--ledger", default=str(LEDGER_PATH), help="Path to forecast-ledger.jsonl")
@click.option("--output", default=str(PRIOR_TABLE_PATH), help="Path to prior-table-runtime.json output")
@click.option("--dry-run", is_flag=True, default=False, help="Print output without writing")
def cli(ledger, output, dry_run):
    """Compute Bayesian prior distributions from the forecast ledger."""
    ledger_path = Path(ledger)
    output_path = Path(output)

    rows = load_ledger(ledger_path)
    if not rows:
        click.echo("ERROR: ledger is empty or not found. Run Phase 1.3 seed first.", err=True)
        sys.exit(1)

    rows = deduplicate_ledger(rows)
    priors = compute_priors(rows)

    result = write_prior_table(priors, output_path, dry_run=dry_run)

    if not dry_run:
        click.echo(f"[WRITTEN] {len(priors)} priors → {output_path}")
        for p in result["priors"]:
            dist = p["distribution"]
            prior_id = p["prior_id"]
            if dist == "dirichlet":
                valid = "✓" if p["group_sum_valid"] else "✗ SUM ERROR"
                click.echo(f"  [{dist.upper():<12}] {prior_id}  sum={p['group_sum_check']} {valid}")
            elif dist == "beta":
                click.echo(f"  [{dist.upper():<12}] {prior_id}  α={p['alpha']} β={p['beta']} mean={p['mean']}")
            else:
                click.echo(f"  [{dist.upper():<12}] {prior_id}")


if __name__ == "__main__":
    cli()
