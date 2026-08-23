from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


APP_DIR = Path(os.environ.get("VOICE_CLONE_HOME", Path.home() / ".local/share/voice-clone"))
PROFILES_DIR = Path(os.environ.get("VOICE_CLONE_PROFILES", APP_DIR / "profiles"))
REPORTS_DIR = Path(os.environ.get("VOICE_CLONE_REPORTS", APP_DIR / "reports"))
STATE_FILE = APP_DIR / "installation-state.json"
MODEL_CACHE = APP_DIR / "model-cache"
MODEL_CACHE_NAMES = (
    "hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit",
    "models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit",
)


def model_cache_path() -> Path | None:
    for relative in MODEL_CACHE_NAMES:
        candidate = MODEL_CACHE / relative
        if candidate.is_dir():
            return candidate
    return None


class VoiceCloneError(RuntimeError):
    """Erro controlado que deve bloquear a geração em vez de usar fallback."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(temp, 0o600)
    temp.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VoiceCloneError(f"JSON inválido ou inacessível: {path}") from exc
    if not isinstance(value, dict):
        raise VoiceCloneError(f"Objeto JSON esperado: {path}")
    return value
