from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_profile import write_voice

from voice_clone.common import VoiceCloneError
from voice_clone.wizard import run


def fake_synthesize(profile_dir, text, output, **kwargs):
    output.write_bytes(b"audio")
    return {"generation": {"fidelity": {"semitones": 0.2}}}


@unittest.skipIf(shutil.which("ffmpeg") is None, "FFmpeg ausente")
class WizardTests(unittest.TestCase):
    @patch("voice_clone.wizard._play")
    @patch("voice_clone.operations.synthesize", side_effect=fake_synthesize)
    def test_creates_ready_profile_from_existing_recording(self, _synth, _play) -> None:
        answers = iter(["Maria da Silva", "s", "", "AUTORIZO", "", "s"])
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", lambda *a: next(answers)):
            root = Path(temp)
            sample = root / "gravacao.wav"
            write_voice(sample, 40)
            result = run("pt", root / "perfis", input_file=sample)
            profile = json.loads((root / "perfis" / "maria-da-silva" / "profile.json").read_text())
            self.assertEqual(result["status"], "PRONTO")
            self.assertTrue(profile["human_approval"]["approved"])
            consent = (root / "perfis" / "maria-da-silva" / "consent.txt").read_text()
            self.assertIn("Maria da Silva", consent)
            self.assertIn("AUTORIZO", consent)

    def test_blocks_without_authorization(self) -> None:
        answers = iter(["Maria", "s", "", "nao"])
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", lambda *a: next(answers)):
            with self.assertRaises(VoiceCloneError):
                run("pt", Path(temp))


if __name__ == "__main__":
    unittest.main()
