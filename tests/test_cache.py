from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.common import model_cache_path


class CacheTests(unittest.TestCase):
    def test_finds_huggingface_hub_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = root / "hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
            expected.mkdir(parents=True)
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertEqual(model_cache_path(), expected)

    def test_accepts_legacy_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = root / "models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
            expected.mkdir()
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertEqual(model_cache_path(), expected)


if __name__ == "__main__":
    unittest.main()
