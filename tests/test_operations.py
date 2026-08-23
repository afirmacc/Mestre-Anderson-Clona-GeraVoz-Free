from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.common import VoiceCloneError, sha256
from voice_clone.operations import synthesize, verify


def make_profile(root: Path) -> None:
    reference = root / "reference.wav"
    consent = root / "consent.txt"
    reference.write_bytes(b"reference")
    consent.write_text("Autorização expressa e específica do titular.")
    data = {
        "profile_id": "perfil-teste", "engine": "qwen3-mlx", "model": "modelo-teste",
        "reference": reference.name, "reference_sha256": sha256(reference),
        "consent_file": consent.name, "consent_sha256": sha256(consent),
    }
    (root / "profile.json").write_text(json.dumps(data))


class OperationTests(unittest.TestCase):
    @patch("voice_clone.operations.probe")
    @patch("voice_clone.operations.mlx_synthesize")
    def test_manifest_never_uses_fallback(self, generate, audio_probe) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_profile(root)
            output = root / "output.wav"
            def fake_generate(profile, profile_dir, text, target):
                target.write_bytes(b"generated")
                return {"sample_rate": 24000, "segments": 1, "duration_seconds": 1.0}
            generate.side_effect = fake_generate
            audio_probe.return_value = {"valid": True, "duration_seconds": 1.0, "sample_rate": 24000, "channels": 1}
            result = synthesize(root, "Teste autorizado.", output)
            self.assertFalse(result["fallback_used"])
            self.assertEqual(result["status"], "AGUARDA_QA_HUMANO")

    @patch("voice_clone.operations.probe")
    def test_verify_blocks_manifest_mismatch(self, audio_probe) -> None:
        audio_probe.return_value = {"valid": True}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            audio = root / "audio.wav"
            audio.write_bytes(b"audio")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"output_sha256": "wrong", "fallback_used": False}))
            with patch("voice_clone.operations.REPORTS_DIR", root / "reports"):
                result = verify(audio, "Texto", manifest)
            self.assertEqual(result["status"], "BLOQUEADO_VOZ")

    @patch("voice_clone.operations.mlx_synthesize")
    def test_backend_failure_has_no_fallback(self, generate) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_profile(root)
            generate.side_effect = VoiceCloneError("backend indisponível")
            with self.assertRaises(VoiceCloneError):
                synthesize(root, "Teste", root / "output.wav")
            self.assertFalse((root / "output.wav").exists())


if __name__ == "__main__":
    unittest.main()
