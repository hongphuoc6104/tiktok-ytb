import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import b2_illustrator


class B2IllustratorAssessmentTests(unittest.TestCase):
    def test_default_plan_is_read_only_and_unknown(self):
        config = b2_illustrator.load_config()
        plan = b2_illustrator.build_plan(config)
        self.assertTrue(plan["read_only"])
        self.assertFalse(plan["generation_submitted"])
        self.assertFalse(plan["tool"]["identity_verified"])
        self.assertTrue(plan["flow_constraints"]["live_ui_required"])
        self.assertEqual(plan["experiment_budget"]["max_credits"], 1050)
        self.assertIsNone(plan["experiment_budget"]["spent_credits"])
        self.assertFalse(plan["experiment_budget"]["generation_enabled"])
        self.assertIn("remix_or_custom_prompt", plan["capabilities"])
        self.assertIsNone(plan["capabilities"]["remix_or_custom_prompt"])

    def test_profile_metadata_does_not_confirm_live_flow_account(self):
        config = b2_illustrator.load_config()
        profile = b2_illustrator.inspect_profile(config)
        self.assertFalse(profile["ui_account_confirmed"])
        self.assertFalse(profile["secret_files_read"])

    def test_output_cannot_escape_experiment_results(self):
        config = b2_illustrator.load_config()
        with self.assertRaises(b2_illustrator.AssessmentError):
            b2_illustrator.validate_output_dir(config, str(Path(b2_illustrator.PROJECT_ROOT) / "runs" / "b2"))

    def test_record_stays_in_results(self):
        config = b2_illustrator.load_config()
        with tempfile.TemporaryDirectory(dir=b2_illustrator.MODULE_ROOT / "results") as temp:
            plan = b2_illustrator.build_plan(config, temp)
            destination = b2_illustrator.record_plan(plan, Path(temp))
            self.assertTrue(destination.is_file())
            self.assertEqual(json.loads(destination.read_text())["generation_submitted"], False)

    def test_subprocess_honors_json_record_flags(self):
        result = subprocess.run(
            [
                sys.executable,
                str(b2_illustrator.MODULE_ROOT / "b2_illustrator.py"),
                "inspect",
                "--format",
                "json",
                "--record",
            ],
            cwd=b2_illustrator.PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["generation_submitted"])
        self.assertTrue(Path(payload["recorded_to"]).is_file())

    def test_subprocess_rejects_production_output(self):
        result = subprocess.run(
            [
                sys.executable,
                str(b2_illustrator.MODULE_ROOT / "b2_illustrator.py"),
                "inspect",
                "--output-dir",
                str(b2_illustrator.PROJECT_ROOT / "runs" / "b2"),
            ],
            cwd=b2_illustrator.PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("output must stay under", result.stderr)


if __name__ == "__main__":
    unittest.main()
