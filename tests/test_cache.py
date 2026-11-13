from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_clone.common import model_cache_path


def complete(model: Path) -> None:
    (model / "snapshots/abc").mkdir(parents=True)
    (model / "snapshots/abc/model.safetensors").write_bytes(b"pesos")
    (model / "blobs").mkdir()


class CacheTests(unittest.TestCase):
    def test_finds_huggingface_hub_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = root / "hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
            complete(expected)
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertEqual(model_cache_path(), expected)

    def test_accepts_legacy_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = root / "models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
            complete(expected)
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertEqual(model_cache_path(), expected)

    def test_half_download_is_not_ready(self) -> None:
        # Teste real: o download travou no meio e a pasta existir não pode valer como modelo pronto.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            model = root / "hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
            (model / "blobs").mkdir(parents=True)
            (model / "blobs/abc.incomplete").write_bytes(b"")
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertIsNone(model_cache_path())
            complete_dir = model / "snapshots/abc"
            complete_dir.mkdir(parents=True)
            (complete_dir / "model.safetensors").write_bytes(b"pesos")
            with patch("voice_clone.common.MODEL_CACHE", root):
                self.assertIsNone(model_cache_path())

    def test_local_model_dir_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            local = root / "modelo"
            local.mkdir()
            (local / "config.json").write_text("{}")
            (local / "model.safetensors").write_bytes(b"pesos")
            (root / "model-dir").write_text(str(local))
            with patch("voice_clone.common.LOCAL_MODEL_FILE", root / "model-dir"), \
                 patch("voice_clone.common.MODEL_CACHE", root / "cache"):
                self.assertEqual(model_cache_path(), local)


if __name__ == "__main__":
    unittest.main()
