from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.common import VoiceCloneError
from voice_clone.operations import narrate


def fake_synthesize(profile_dir, text, output, manifest=None, **kwargs):
    output.write_bytes(b"audio")
    status = "CONFERIR_FIDELIDADE" if "difícil" in text else "AGUARDA_QA_HUMANO"
    return {"spoken_text": text, "status": status, "generation": {"chosen_take": 1, "fidelity": {"score": 1.0}}}


class NarrateTests(unittest.TestCase):
    @patch("voice_clone.operations.level", return_value={"gain_db": 0.0})
    @patch("voice_clone.operations.synthesize", side_effect=fake_synthesize)
    def test_txt_script_one_line_per_fala(self, synth, level) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "roteiro.txt"
            script.write_text("Primeira fala.\n\nUma fala difícil.\n")
            report = narrate(root, script, root / "saida")
            self.assertEqual([item["line"] for item in report["lines"]], [1, 2])
            self.assertEqual(report["to_review"], [2])
            self.assertTrue((root / "saida" / "narration-report.json").is_file())

    @patch("voice_clone.operations.level", return_value={"gain_db": 0.0})
    @patch("voice_clone.operations.synthesize", side_effect=fake_synthesize)
    def test_json_script_uses_speak_and_only(self, synth, level) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "roteiro.json"
            script.write_text(json.dumps({"lines": [{"text": "Um."}, {"text": "App", "speak": "Ápi"}]}))
            report = narrate(root, script, root / "saida", only=[2])
            self.assertEqual(len(report["lines"]), 1)
            self.assertEqual(report["lines"][0]["text"], "App")
            self.assertEqual(synth.call_args.args[1], "App")
            self.assertEqual(synth.call_args.kwargs["speak"], "Ápi")

    def test_empty_script_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script = Path(temp) / "vazio.txt"
            script.write_text("\n")
            with self.assertRaises(VoiceCloneError):
                narrate(Path(temp), script, Path(temp) / "saida")


if __name__ == "__main__":
    unittest.main()
