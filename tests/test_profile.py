from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.common import VoiceCloneError, sha256
from voice_clone.profile import prepare_audio, validate_profile


class ProfileTests(unittest.TestCase):
    def test_invalid_profile_id_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            consent = root / "consent.txt"
            source.write_bytes(b"audio")
            consent.write_text("Autorização expressa e específica do titular.")
            with self.assertRaises(VoiceCloneError):
                prepare_audio(source, root / "profile", "Nome Inválido", consent)

    def test_profile_validation_checks_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reference = root / "reference.wav"
            consent = root / "consent.txt"
            reference.write_bytes(b"RIFF" + b"0" * 100)
            consent.write_text("Autorização expressa e específica do titular.")
            profile = {
                "profile_id": "teste-autorizado", "engine": "qwen3-mlx", "model": "modelo",
                "reference": reference.name, "reference_sha256": sha256(reference),
                "consent_file": consent.name, "consent_sha256": sha256(consent),
            }
            (root / "profile.json").write_text(json.dumps(profile))
            self.assertEqual(validate_profile(root)["profile_id"], "teste-autorizado")
            reference.write_bytes(b"alterado")
            with self.assertRaises(VoiceCloneError):
                validate_profile(root)

    @patch("voice_clone.profile.subprocess.run")
    def test_prepare_creates_private_profile(self, run) -> None:
        def fake_run(command, **kwargs):
            Path(command[-1]).write_bytes(b"RIFF" + b"0" * 60_000)
        run.side_effect = fake_run
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.m4a"
            consent = root / "consent-source.txt"
            source.write_bytes(b"source")
            consent.write_text("Autorização expressa e específica do titular.")
            target = root / "teste-autorizado"
            result = prepare_audio(source, target, "teste-autorizado", consent, "Texto exato")
            self.assertEqual(result["status"], "AGUARDA_TESTE")
            self.assertTrue((target / "profile.json").is_file())
            self.assertEqual(validate_profile(target)["reference_transcript"], "Texto exato")


if __name__ == "__main__":
    unittest.main()
