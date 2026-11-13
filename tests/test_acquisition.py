from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_profile import write_voice

from voice_clone.acquisition import analyze, guide


class AcquisitionTests(unittest.TestCase):
    def test_guide_has_reading_in_three_languages(self) -> None:
        for language in ("Portuguese", "English", "Spanish"):
            info = guide(language)
            self.assertGreater(len(info["reading"].split()), 80)
            self.assertTrue(info["tips"])

    def test_good_sample_passes_and_short_one_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            good, short = Path(temp) / "boa.wav", Path(temp) / "curta.wav"
            write_voice(good, 30)
            write_voice(short, 4)
            self.assertTrue(analyze(good)["ok"], analyze(good))
            self.assertFalse(analyze(short)["ok"])
            self.assertGreater(analyze(good)["snr_db"], 25)

    def test_quiet_voice_gets_volume_advice_not_noise_advice(self) -> None:
        import wave
        import numpy as np

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "baixa.wav"
            write_voice(path, 30)
            with wave.open(str(path), "rb") as handle:
                params, frames = handle.getparams(), handle.readframes(handle.getnframes())
            quiet = (np.frombuffer(frames, dtype=np.int16) * 0.04).astype(np.int16)
            with wave.open(str(path), "wb") as handle:
                handle.setparams(params)
                handle.writeframes(quiet.tobytes())
            result = analyze(path)
            text = " ".join(result["problems"] + result["warnings"])
            self.assertFalse(result["ok"])
            self.assertIn("Voz baixa", text)
            self.assertNotIn("Desligue ventilador", text)


if __name__ == "__main__":
    unittest.main()
