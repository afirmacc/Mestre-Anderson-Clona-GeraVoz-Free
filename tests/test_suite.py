from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.suite import BUILTIN_CASES, run_voice_suite


class SuiteTests(unittest.TestCase):
    @patch("voice_clone.suite.verify")
    @patch("voice_clone.suite.synthesize")
    def test_builtin_suite_reaches_human_qa(self, generate, verify) -> None:
        generate.return_value = {"fallback_used": False}
        verify.return_value = {"status": "AGUARDA_QA_HUMANO"}
        with tempfile.TemporaryDirectory() as temp:
            with patch("voice_clone.suite.REPORTS_DIR", Path(temp)):
                report = run_voice_suite(Path(temp) / "profile")
        self.assertEqual(report["status"], "AGUARDA_QA_HUMANO")
        self.assertEqual(generate.call_count, len(BUILTIN_CASES))

    @patch("voice_clone.suite.verify")
    @patch("voice_clone.suite.synthesize")
    def test_any_failed_case_blocks_suite(self, generate, verify) -> None:
        generate.return_value = {"fallback_used": False}
        verify.side_effect = [{"status": "BLOQUEADO_VOZ"}] + [
            {"status": "AGUARDA_QA_HUMANO"} for _ in BUILTIN_CASES[1:]
        ]
        with tempfile.TemporaryDirectory() as temp:
            with patch("voice_clone.suite.REPORTS_DIR", Path(temp)):
                report = run_voice_suite(Path(temp) / "profile")
        self.assertEqual(report["status"], "BLOQUEADO_VOZ")


if __name__ == "__main__":
    unittest.main()
