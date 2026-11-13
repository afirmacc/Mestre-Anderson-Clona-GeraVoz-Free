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


if __name__ == "__main__":
    unittest.main()
