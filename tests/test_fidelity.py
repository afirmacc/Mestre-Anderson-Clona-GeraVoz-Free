from __future__ import annotations

import json
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy é dependência base desde a 0.2.0
    np = None

from voice_clone import fidelity
from voice_clone.common import sha256
from voice_clone.pronunciation import apply, load

RATE = 24000


def tone(hz: float, seconds: float = 1.5):
    t = np.arange(int(RATE * seconds)) / RATE
    # Fundamental + harmônicos, como uma vogal sustentada, com um leve ruído de fundo (como num microfone).
    noise = np.random.default_rng(7).normal(0, 0.01, t.size)
    return (0.5 * np.sin(2 * np.pi * hz * t) + 0.25 * np.sin(4 * np.pi * hz * t)
            + 0.12 * np.sin(6 * np.pi * hz * t) + noise).astype(np.float32)


def write(path: Path, samples) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes((samples * 32767).astype(np.int16).tobytes())


@unittest.skipIf(np is None, "numpy ausente")
class FidelityTests(unittest.TestCase):
    def test_measures_pitch(self) -> None:
        self.assertAlmostEqual(fidelity.measure_array(tone(124), RATE)["f0_hz"], 124, delta=3)

    def test_same_voice_is_accepted_and_shifted_voice_is_not(self) -> None:
        reference = fidelity.measure_array(tone(124), RATE)
        same = fidelity.distance(fidelity.measure_array(tone(125), RATE), reference)
        shifted = fidelity.distance(fidelity.measure_array(tone(199), RATE), reference)
        self.assertTrue(fidelity.accepted(same))
        self.assertGreater(shifted["semitones"], 7)
        self.assertFalse(fidelity.accepted(shifted))
        self.assertLess(same["score"], shifted["score"])

    def test_reads_wav(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "a.wav"
            write(path, tone(150))
            self.assertAlmostEqual(fidelity.measure(path)["f0_hz"], 150, delta=4)


@unittest.skipIf(np is None, "numpy ausente")
class BestTakeTests(unittest.TestCase):
    def make_profile(self, root: Path) -> None:
        write(root / "reference.wav", tone(124, 3))
        (root / "consent.txt").write_text("Autorização expressa e específica do titular.")
        data = {"profile_id": "perfil-teste", "engine": "qwen3-mlx", "model": "modelo-teste",
                "reference": "reference.wav", "reference_sha256": sha256(root / "reference.wav"),
                "consent_file": "consent.txt", "consent_sha256": sha256(root / "consent.txt")}
        (root / "profile.json").write_text(json.dumps(data))
        (root / "pronunciation.json").write_text(json.dumps({"entries": {"Admin": "Adimin"}}))

    @patch("voice_clone.operations.listen.available", return_value=False)
    @patch("voice_clone.operations.probe")
    @patch("voice_clone.operations.generate_take")
    def test_keeps_the_most_faithful_take(self, generate, audio_probe, _listen) -> None:
        # 1ª tomada: outra voz (199 Hz). 2ª: cortada. 3ª: a voz certa.
        generate.side_effect = [(tone(199), RATE), (tone(124, 0.2), RATE), (tone(125), RATE), (tone(124), RATE)]
        audio_probe.return_value = {"valid": True, "duration_seconds": 1.5, "sample_rate": RATE, "channels": 1}
        from voice_clone.operations import synthesize
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_profile(root)
            result = synthesize(root, "Abra o app Admin.", root / "out.wav", takes=10)
            self.assertEqual(result["spoken_text"], "Abra o ápi Adimin.")
            self.assertEqual(result["generation"]["chosen_take"], 3)
            self.assertEqual(result["generation"]["takes_tried"], 3)
            self.assertEqual(result["generation"]["attempts"][1]["discarded"], "duration")
            self.assertEqual(result["status"], "AGUARDA_QA_HUMANO")
            self.assertAlmostEqual(fidelity.measure(root / "out.wav")["f0_hz"], 125, delta=4)

    @patch("voice_clone.operations.listen.available", return_value=False)
    @patch("voice_clone.operations.probe")
    @patch("voice_clone.operations.generate_take")
    def test_flags_when_no_take_is_faithful(self, generate, audio_probe, _listen) -> None:
        generate.side_effect = [(tone(199), RATE), (tone(180), RATE)]
        audio_probe.return_value = {"valid": True}
        from voice_clone.operations import synthesize
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_profile(root)
            result = synthesize(root, "Uma fala curta.", root / "out.wav", takes=2)
            self.assertEqual(result["status"], "CONFERIR_FIDELIDADE")
            self.assertEqual(result["generation"]["chosen_take"], 2)


class PronunciationTests(unittest.TestCase):
    def test_replaces_whole_terms_only(self) -> None:
        entries = {"app": "ápi", "Admin": "Adimin"}
        self.assertEqual(apply("Baixe o App Admin. Aplicativo e administrador ficam.", entries),
                         "Baixe o ápi Adimin. Aplicativo e administrador ficam.")

    def test_longest_term_first_and_extra_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "pronunciation.json").write_text(json.dumps({"entries": {"site": "sáiti"}}))
            extra = root / "extra.json"
            extra.write_text(json.dumps({"entries": {"site.com.br": "site ponto com ponto bê érre"}}))
            entries = load(root, extra)
            self.assertEqual(apply("Acesse site.com.br ou o site.", entries),
                             "Acesse site ponto com ponto bê érre ou o sáiti.")


if __name__ == "__main__":
    unittest.main()
