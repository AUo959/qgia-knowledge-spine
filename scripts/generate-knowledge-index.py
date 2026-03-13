#!/usr/bin/env python3
"""Generate a knowledge-index.json for the QGIA Knowledge Spine.

Walks the repo root for numbered methodology documents (NN_*.md),
extracts metadata, and writes .aurora/knowledge-index.json.
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / ".aurora" / "knowledge-index.json"

SKIP_FILES = {"README.md", "STRUCTURE.md"}
NUMBERED_DOC_RE = re.compile(r"^(\d{2})_.*\.md$")

TIER_DOMAINS = {
    range(1, 7): "tier1-methodological-foundations",
    range(7, 13): "tier2-theoretical-foundations",
    range(13, 19): "tier3-regional-expertise",
    range(19, 25): "tier4-functional-domains",
}


def get_tier_domain(doc_number: int) -> str:
    for num_range, domain in TIER_DOMAINS.items():
        if doc_number in num_range:
            return domain
    return "unknown"


def extract_metadata(filepath: Path) -> dict | None:
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Extract H1 title
    title = None
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            break
    if not title:
        return None

    # Extract H2 headings as tags
    tags = []
    for line in lines:
        if line.startswith("## "):
            tag = line[3:].strip()
            tag = re.sub(r"[^a-zA-Z0-9\s-]", "", tag).strip().lower().replace(" ", "-")
            if tag:
                tags.append(tag)

    # Extract first non-heading paragraph as summary (max 300 chars)
    summary = ""
    in_paragraph = False
    para_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("---"):
            if in_paragraph:
                break
            continue
        if stripped == "":
            if in_paragraph:
                break
            continue
        in_paragraph = True
        para_lines.append(stripped)
    if para_lines:
        summary = " ".join(para_lines)
        if len(summary) > 300:
            summary = summary[:297] + "..."

    # Compute SHA-256 checksum (first 16 hex chars)
    content_bytes = text.encode("utf-8")
    checksum = hashlib.sha256(content_bytes).hexdigest()[:16]

    # Count words
    word_count = len(text.split())

    # Last modified time
    stat = filepath.stat()
    last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

    return {
        "title": title,
        "checksum": checksum,
        "word_count": word_count,
        "tags": tags,
        "summary": summary,
        "last_modified": last_modified,
    }


def main():
    documents = []

    for entry in sorted(REPO_ROOT.iterdir()):
        if entry.name in SKIP_FILES or entry.name.startswith("."):
            continue
        match = NUMBERED_DOC_RE.match(entry.name)
        if not match or not entry.is_file():
            continue

        doc_number = int(match.group(1))
        meta = extract_metadata(entry)
        if not meta:
            continue

        doc_id = f"qgia-spine:{entry.stem}"
        domain = get_tier_domain(doc_number)

        documents.append({
            "id": doc_id,
            "title": meta["title"],
            "domain": domain,
            "path": entry.name,
            "checksum": meta["checksum"],
            "word_count": meta["word_count"],
            "last_modified": meta["last_modified"],
            "tags": meta["tags"],
            "summary": meta["summary"],
        })

    index = {
        "version": "1.0.0",
        "source_repo": "qgia-knowledge-spine",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": documents,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Generated knowledge index with {len(documents)} documents at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
