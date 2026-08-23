from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.operations import status


class StatusTests(unittest.TestCase):
    @patch("voice_clone.operations.package_version")
    @patch("voice_clone.operations.shutil.which")
    @patch("voice_clone.operations.model_cache_path")
    def test_status_requires_all_runtime_components(self, cache, which, package) -> None:
        package.side_effect = lambda name: {"mlx": "0.32.0", "mlx-audio": "0.4.7", "mlx-whisper": "0.4.3"}.get(name)
        which.side_effect = lambda name: f"/usr/bin/{name}"
        cache.return_value = Path("/cache/model")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "clonar-voz-local"
            skill.mkdir()
            (skill / "SKILL.md").write_text("skill")
            with patch.dict("os.environ", {"HERMES_SKILLS_DIR": temp}):
                with patch("voice_clone.operations.STATE_FILE", root / "missing-state.json"):
                    result = status()
        self.assertFalse(result["installation_valid"])
        self.assertIn("state_file", result["missing"])

    @patch("voice_clone.operations.package_version", return_value=None)
    @patch("voice_clone.operations.shutil.which", return_value=None)
    @patch("voice_clone.operations.model_cache_path", return_value=None)
    def test_status_lists_missing_model_whisper_and_ffmpeg(self, cache, which, package) -> None:
        result = status()
        for component in ("model_cache", "mlx_whisper", "ffmpeg", "ffprobe"):
            self.assertIn(component, result["missing"])


if __name__ == "__main__":
    unittest.main()
