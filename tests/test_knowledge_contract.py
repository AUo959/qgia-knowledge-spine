from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import knowledge_contract  # noqa: E402


class KnowledgeContractTests(unittest.TestCase):
    def test_tier_domain_mapping(self) -> None:
        self.assertEqual(knowledge_contract.get_tier_domain(1), "tier1-methodological-foundations")
        self.assertEqual(knowledge_contract.get_tier_domain(8), "tier2-theoretical-foundations")
        self.assertEqual(knowledge_contract.get_tier_domain(14), "tier3-regional-expertise")
        self.assertEqual(knowledge_contract.get_tier_domain(20), "tier4-functional-domains")

    def test_extract_metadata_skips_document_control_headers(self) -> None:
        sample = REPO_ROOT / "01_forecasting_methodologies.md"
        meta = knowledge_contract.extract_metadata(sample)
        self.assertFalse(meta["summary"].startswith("**QGIA Knowledge Spine"))
        self.assertIn("forecasting methodologies form the analytical backbone", meta["summary"].lower())

    def test_build_index_uses_git_timestamps_and_repo_paths(self) -> None:
        index = knowledge_contract.build_index(
            root=REPO_ROOT,
            generated_at="2026-04-18T00:00:00+00:00",
        )
        documents = {document["path"]: document for document in index["documents"]}
        self.assertEqual(
            documents["01_forecasting_methodologies.md"]["domain"],
            "tier1-methodological-foundations",
        )
        self.assertEqual(
            documents["frameworks/iran-war-scenario-taxonomy.md"]["domain"],
            "framework",
        )
        self.assertEqual(
            documents["schemas/probability-ledger-schema.md"]["domain"],
            "schema",
        )
        self.assertEqual(
            documents["methods/iran-regime-dirichlet-template.md"]["domain"],
            "method",
        )
        self.assertIn("T", documents["01_forecasting_methodologies.md"]["last_modified"])
        self.assertEqual(len(index["documents"]), 7)

    def test_bootstrap_forecast_ledger_allows_empty_history(self) -> None:
        failures = knowledge_contract.validate_forecast_ledger(REPO_ROOT)
        self.assertEqual(failures, [])

    def test_bootstrap_prior_table_is_versioned_and_empty(self) -> None:
        payload = knowledge_contract.load_json(REPO_ROOT / "data/priors/prior-table.json")
        self.assertEqual(payload["artifact_type"], "prior_table")
        self.assertEqual(payload["producer"], "qgia-knowledge-spine")
        self.assertEqual(payload["priors"], [])

    def test_bootstrap_calibration_report_declares_no_scored_history(self) -> None:
        payload = knowledge_contract.load_json(REPO_ROOT / "data/calibration/calibration-report.json")
        self.assertEqual(payload["artifact_type"], "calibration_report")
        self.assertEqual(payload["summary"]["resolved_forecast_count"], 0)
        self.assertIsNone(payload["summary"]["team_brier_score"])
        self.assertIsNone(payload["summary"]["expected_calibration_error"])

    def test_validate_repo_contract_passes(self) -> None:
        failures = knowledge_contract.validate_repo_contract(REPO_ROOT)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
