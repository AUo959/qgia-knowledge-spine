#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPO = "qgia-knowledge-spine"
NODE_DESIGNATION = "QGIA-SPINE"
NODE_ROLE = "spoke"
UPSTREAM_NODES = ("s.tag::constellation.prime", "s.tag::qgia.corpus")
LIVE_RUNTIME_URL = "https://www.perplexity.ai/spaces/foreign-policy-and-global-poli-_IZgsdmvSo2Yxe7LAZ5HSQ"
EXPECTED_PUBLISHED_CONTRACTS = (
    "knowledge-index",
    "forecast-ledger",
    "prior-table",
    "calibration-report",
    "resolution-policy",
)
EXPECTED_CONSUMED_CONTRACTS = (
    "constellation-event",
    "constellation-health",
    "evidence-record",
    "outcome-record",
)
INDEX_VERSION = "1.0.0"
SKIP_FILES = {"README.md", "STRUCTURE.md"}
NUMBERED_DOC_RE = re.compile(r"^(\d{2})_.*\.md$")
SUMMARY_METADATA_LINE = re.compile(r"^\*\*[^*]+\*\*:")
BOLD_ONLY_LINE = re.compile(r"^\*\*[^*]+\*\*$")
SUPPLEMENTAL_DOC_DIR_DOMAINS = {
    "frameworks": "framework",
    "schemas": "schema",
    "methods": "method",
}

TIER_DOMAINS = {
    range(1, 7): "tier1-methodological-foundations",
    range(7, 13): "tier2-theoretical-foundations",
    range(13, 19): "tier3-regional-expertise",
    range(19, 25): "tier4-functional-domains",
}


def iter_spine_documents(root: Path = REPO_ROOT) -> Iterable[Path]:
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if entry.name.startswith(".") or entry.name in SKIP_FILES:
            continue
        if entry.is_file() and NUMBERED_DOC_RE.match(entry.name):
            yield entry
            continue
        if entry.is_dir() and entry.name in SUPPLEMENTAL_DOC_DIR_DOMAINS:
            for md_file in sorted(entry.rglob("*.md")):
                if md_file.name not in SKIP_FILES:
                    yield md_file


def get_tier_domain(doc_number: int) -> str:
    for num_range, domain in TIER_DOMAINS.items():
        if doc_number in num_range:
            return domain
    return "unknown"


def git_last_modified(root: Path, relative_path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", relative_path.as_posix()],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    timestamp = result.stdout.strip()
    if timestamp:
        return timestamp
    absolute_path = root / relative_path
    return datetime.fromtimestamp(absolute_path.stat().st_mtime, tz=timezone.utc).isoformat()


def extract_metadata(filepath: Path) -> Dict[str, Any]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = None
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            break
    if not title:
        raise ValueError("Missing H1 title in %s" % filepath)

    tags = []
    for line in lines:
        if line.startswith("## "):
            tag = line[3:].strip()
            tag = re.sub(r"[^a-zA-Z0-9\s-]", "", tag).strip().lower().replace(" ", "-")
            if tag:
                tags.append(tag)

    summary = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("---"):
            continue
        if stripped.startswith("[!["):
            continue
        if BOLD_ONLY_LINE.match(stripped):
            continue
        if SUMMARY_METADATA_LINE.match(stripped):
            continue
        summary = stripped[:300]
        break

    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    word_count = len(text.split())

    return {
        "title": title,
        "checksum": checksum,
        "word_count": word_count,
        "tags": tags,
        "summary": summary,
    }


def domain_for_spine_document(relative_path: Path) -> str:
    top_level = relative_path.parts[0]
    if top_level in SUPPLEMENTAL_DOC_DIR_DOMAINS:
        return SUPPLEMENTAL_DOC_DIR_DOMAINS[top_level]
    match = NUMBERED_DOC_RE.match(top_level)
    if not match:
        raise ValueError("Unsupported spine document path: %s" % relative_path.as_posix())
    return get_tier_domain(int(match.group(1)))


def build_index(root: Path = REPO_ROOT, generated_at: Optional[str] = None) -> Dict[str, Any]:
    documents: List[Dict[str, Any]] = []

    for entry in iter_spine_documents(root):
        relative_path = entry.relative_to(root)
        meta = extract_metadata(entry)

        documents.append(
            {
                "id": "qgia-spine:%s" % entry.stem,
                "title": meta["title"],
                "domain": domain_for_spine_document(relative_path),
                "path": relative_path.as_posix(),
                "checksum": meta["checksum"],
                "word_count": meta["word_count"],
                "last_modified": git_last_modified(root, relative_path),
                "tags": meta["tags"],
                "summary": meta["summary"],
            }
        )

    return {
        "version": INDEX_VERSION,
        "source_repo": SOURCE_REPO,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "documents": documents,
    }


def write_index(index: Dict[str, Any], root: Path = REPO_ROOT) -> Path:
    out_path = root / ".aurora" / "knowledge-index.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return out_path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if not isinstance(payload, dict):
            raise ValueError("%s line %s must decode to a JSON object" % (path, line_no))
        records.append(payload)
    return records


def is_iso_datetime(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_forecast_ledger(root: Path) -> List[str]:
    failures: List[str] = []
    path = root / "data/forecasts/forecast-ledger.jsonl"
    try:
        records = parse_jsonl(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return ["forecast ledger invalid: %s" % exc]

    for index, record in enumerate(records):
        prefix = "forecast ledger record %s" % index
        if record.get("record_type") != "forecast":
            failures.append("%s must have record_type=forecast" % prefix)
        if not isinstance(record.get("forecast_id"), str):
            failures.append("%s missing forecast_id" % prefix)
        if not isinstance(record.get("revision_id"), str):
            failures.append("%s missing revision_id" % prefix)
        if not is_iso_datetime(record.get("opened_at")):
            failures.append("%s has invalid opened_at" % prefix)
        if not is_iso_datetime(record.get("target_resolves_by")):
            failures.append("%s has invalid target_resolves_by" % prefix)
    return failures


def validate_prior_table(root: Path) -> List[str]:
    failures: List[str] = []
    payload = load_json(root / "data/priors/prior-table.json")

    if payload.get("artifact_type") != "prior_table":
        failures.append("prior table must have artifact_type=prior_table")
    if not isinstance(payload.get("prior_table_id"), str):
        failures.append("prior table missing prior_table_id")
    if not is_iso_datetime(payload.get("generated_at")):
        failures.append("prior table has invalid generated_at")
    if not is_iso_datetime(payload.get("effective_from")):
        failures.append("prior table has invalid effective_from")
    if payload.get("producer") != SOURCE_REPO:
        failures.append("prior table producer mismatch: expected %s" % SOURCE_REPO)

    priors = payload.get("priors")
    if not isinstance(priors, list):
        failures.append("prior table priors must be a list")
        return failures

    for index, prior in enumerate(priors):
        prefix = "prior table entry %s" % index
        if not isinstance(prior, dict):
            failures.append("%s must be an object" % prefix)
            continue
        for key in ("prior_id", "hypothesis_id", "domain", "update_reason"):
            if not isinstance(prior.get(key), str) or not prior.get(key):
                failures.append("%s missing %s" % (prefix, key))
        for key in ("base_rate", "calibrated_rate"):
            value = prior.get(key)
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                failures.append("%s has invalid %s" % (prefix, key))
        evidence_window = prior.get("evidence_window")
        if not isinstance(evidence_window, dict):
            failures.append("%s missing evidence_window" % prefix)
        else:
            if not is_iso_datetime(evidence_window.get("start")):
                failures.append("%s has invalid evidence_window.start" % prefix)
            if not is_iso_datetime(evidence_window.get("end")):
                failures.append("%s has invalid evidence_window.end" % prefix)
    return failures


def validate_calibration_report(root: Path) -> List[str]:
    failures: List[str] = []
    payload = load_json(root / "data/calibration/calibration-report.json")

    if payload.get("artifact_type") != "calibration_report":
        failures.append("calibration report must have artifact_type=calibration_report")
    if not isinstance(payload.get("report_id"), str):
        failures.append("calibration report missing report_id")
    if payload.get("producer") != SOURCE_REPO:
        failures.append("calibration report producer mismatch: expected %s" % SOURCE_REPO)
    if not is_iso_datetime(payload.get("generated_at")):
        failures.append("calibration report has invalid generated_at")

    sample_window = payload.get("sample_window")
    if not isinstance(sample_window, dict):
        failures.append("calibration report missing sample_window")
    else:
        if not is_iso_datetime(sample_window.get("start")):
            failures.append("calibration report has invalid sample_window.start")
        if not is_iso_datetime(sample_window.get("end")):
            failures.append("calibration report has invalid sample_window.end")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        failures.append("calibration report missing summary")
        return failures

    resolved_count = summary.get("resolved_forecast_count")
    if not isinstance(resolved_count, int) or resolved_count < 0:
        failures.append("calibration report resolved_forecast_count must be an integer >= 0")
        return failures

    metric_fields = (
        "team_brier_score",
        "team_brier_skill_score",
        "expected_calibration_error",
    )
    for key in metric_fields:
        value = summary.get(key)
        if resolved_count == 0:
            if value is not None:
                failures.append("calibration report %s must be null when resolved_forecast_count is 0" % key)
            continue
        if not isinstance(value, (int, float)):
            failures.append("calibration report %s must be numeric when resolved_forecast_count > 0" % key)
    return failures


def validate_resolution_policy(root: Path) -> List[str]:
    failures: List[str] = []
    text = (root / "policies/resolution-policy.md").read_text(encoding="utf-8")
    required_phrases = (
        "Outcome States",
        "Evidence Hierarchy",
        "Ambiguity Handling",
        "Change Discipline",
    )
    for phrase in required_phrases:
        if phrase not in text:
            failures.append("resolution policy missing required section: %s" % phrase)
    return failures


def validate_repo_contract(root: Path = REPO_ROOT) -> List[str]:
    failures: List[str] = []

    required_paths = (
        ".aurora/constellation.json",
        ".aurora/closed-loop-bootstrap.json",
        ".aurora/knowledge-index.json",
        "README.md",
        "data/forecasts/forecast-ledger.jsonl",
        "data/priors/prior-table.json",
        "data/calibration/calibration-report.json",
        "policies/resolution-policy.md",
        "scripts/generate-knowledge-index.py",
        "scripts/validate-knowledge-contract.py",
    )
    for relative in required_paths:
        if not (root / relative).exists():
            failures.append("Missing required contract file: %s" % relative)

    if failures:
        return failures

    constellation = load_json(root / ".aurora" / "constellation.json")
    node = constellation.get("node", {})
    contracts = constellation.get("contracts", {})
    upstream = constellation.get("upstream", [])
    health = constellation.get("health", {})
    meta = constellation.get("meta", {})

    if node.get("designation") != NODE_DESIGNATION:
        failures.append(
            "constellation designation mismatch: expected %s, got %r"
            % (NODE_DESIGNATION, node.get("designation"))
        )
    if node.get("repo") != SOURCE_REPO:
        failures.append(
            "constellation repo mismatch: expected %s, got %r"
            % (SOURCE_REPO, node.get("repo"))
        )
    if node.get("role") != NODE_ROLE:
        failures.append(
            "constellation role mismatch: expected %s, got %r"
            % (NODE_ROLE, node.get("role"))
        )
    published = contracts.get("published", [])
    consumed = contracts.get("consumed", [])
    for contract_name in EXPECTED_PUBLISHED_CONTRACTS:
        if contract_name not in published:
            failures.append("constellation contracts must publish %s" % contract_name)
    for contract_name in EXPECTED_CONSUMED_CONTRACTS:
        if contract_name not in consumed:
            failures.append("constellation contracts must consume %s" % contract_name)
    for upstream_node in UPSTREAM_NODES:
        if upstream_node not in upstream:
            failures.append("constellation upstream must include %s" % upstream_node)
    if health.get("closed_loop_stage") != "spine-bootstrap":
        failures.append("constellation health.closed_loop_stage must be spine-bootstrap")
    if meta.get("contract_package_ref") != "qgia_knowledge_closed_loop_contract_v1":
        failures.append("constellation meta.contract_package_ref must be qgia_knowledge_closed_loop_contract_v1")
    runtime_targets = meta.get("runtime_targets")
    if not isinstance(runtime_targets, list) or not runtime_targets:
        failures.append("constellation meta.runtime_targets must declare at least one runtime target")
    else:
        matched_runtime = False
        for target in runtime_targets:
            if not isinstance(target, dict):
                continue
            if (
                target.get("platform") == "perplexity"
                and target.get("designation") == "declared-live-runtime"
                and target.get("verification") == "user-declared"
                and target.get("url") == LIVE_RUNTIME_URL
            ):
                matched_runtime = True
                break
        if not matched_runtime:
            failures.append("constellation meta.runtime_targets must include the declared Perplexity live runtime")

    bootstrap = load_json(root / ".aurora" / "closed-loop-bootstrap.json")
    if bootstrap.get("artifact") != "qgia_spine_closed_loop_bootstrap":
        failures.append("closed-loop bootstrap receipt has unexpected artifact id")
    if bootstrap.get("stage") != "spine-bootstrap":
        failures.append("closed-loop bootstrap receipt must declare stage spine-bootstrap")
    if bootstrap.get("contract_package_ref") != "qgia_knowledge_closed_loop_contract_v1":
        failures.append("closed-loop bootstrap receipt must reference qgia_knowledge_closed_loop_contract_v1")

    index = load_json(root / ".aurora" / "knowledge-index.json")
    if index.get("version") != INDEX_VERSION:
        failures.append(
            "knowledge index version mismatch: expected %s, got %r"
            % (INDEX_VERSION, index.get("version"))
        )
    if index.get("source_repo") != SOURCE_REPO:
        failures.append(
            "knowledge index source_repo mismatch: expected %s, got %r"
            % (SOURCE_REPO, index.get("source_repo"))
        )

    expected_index = build_index(root=root, generated_at=index.get("generated_at"))
    if index.get("documents") != expected_index.get("documents"):
        failures.append(
            "knowledge index is stale or inconsistent with repository content; rerun scripts/generate-knowledge-index.py"
        )

    for document in index.get("documents", []):
        summary = str(document.get("summary", "")).strip()
        path = str(document.get("path", ""))
        if summary.startswith("**QGIA Knowledge Spine"):
            failures.append("knowledge index summary still contains document-control metadata for %s" % path)
        if not summary:
            failures.append("knowledge index summary is empty for %s" % path)

    failures.extend(validate_forecast_ledger(root))
    failures.extend(validate_prior_table(root))
    failures.extend(validate_calibration_report(root))
    failures.extend(validate_resolution_policy(root))

    return failures


def main_generate() -> int:
    index = build_index()
    out_path = write_index(index)
    print("Generated knowledge index: %s documents -> %s" % (len(index["documents"]), out_path))
    return 0


def main_validate() -> int:
    failures = validate_repo_contract()
    if failures:
        print("Knowledge contract validation failed:")
        for failure in failures:
            print("- %s" % failure)
        return 1
    print("Knowledge contract validation passed.")
    return 0
