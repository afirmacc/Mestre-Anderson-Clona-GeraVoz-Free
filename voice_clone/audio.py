from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .common import VoiceCloneError


def probe(path: Path) -> dict:
    if not path.is_file():
        raise VoiceCloneError(f"Áudio não encontrado: {path}")
    command = ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
               "stream=codec_name,sample_rate,channels,duration", "-of", "json", str(path)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        stream = json.loads(result.stdout)["streams"][0]
    except (FileNotFoundError, subprocess.CalledProcessError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise VoiceCloneError("Não foi possível validar o áudio com ffprobe.") from exc
    duration = float(stream.get("duration") or 0)
    return {
        "codec": stream.get("codec_name"),
        "sample_rate": int(stream.get("sample_rate") or 0),
        "channels": int(stream.get("channels") or 0),
        "duration_seconds": round(duration, 3),
        "valid": duration > 0.2 and int(stream.get("channels") or 0) >= 1,
    }
