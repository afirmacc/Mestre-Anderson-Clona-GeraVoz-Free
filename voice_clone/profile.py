from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .common import VoiceCloneError, sha256, write_json


PROFILE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def prepare_audio(source: Path, profile_dir: Path, profile_id: str, consent: Path,
                  transcript: str | None = None) -> dict:
    if not PROFILE_ID.fullmatch(profile_id):
        raise VoiceCloneError("profile-id deve usar letras minúsculas, números e hífens.")
    if not source.is_file() or not consent.is_file():
        raise VoiceCloneError("A amostra e o arquivo de consentimento são obrigatórios.")
    if consent.stat().st_size < 20:
        raise VoiceCloneError("O registro de consentimento está vazio ou insuficiente.")
    profile_dir.mkdir(parents=True, exist_ok=True)
    output = profile_dir / "reference.wav"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-vn", "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", str(output),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise VoiceCloneError("FFmpeg não encontrado. Execute voice-clone install.") from exc
    except subprocess.CalledProcessError as exc:
        raise VoiceCloneError(f"FFmpeg não conseguiu preparar a amostra: {exc.stderr.strip()}") from exc
    if output.stat().st_size < 48_000:
        output.unlink(missing_ok=True)
        raise VoiceCloneError("A amostra preparada é curta ou vazia demais.")
    consent_target = profile_dir / "consent.txt"
    consent_target.write_bytes(consent.read_bytes())
    profile = {
        "schema_version": 1,
        "profile_id": profile_id,
        "engine": "qwen3-mlx",
        "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
        "language": "Portuguese",
        "reference": "reference.wav",
        "reference_sha256": sha256(output),
        "reference_transcript": transcript,
        "consent_file": "consent.txt",
        "consent_sha256": sha256(consent_target),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "AGUARDA_TESTE",
    }
    write_json(profile_dir / "profile.json", profile)
    write_json(profile_dir / "pronunciation.json", {"schema_version": 1, "entries": {}})
    return profile


def validate_profile(profile_dir: Path) -> dict:
    from .common import read_json

    profile = read_json(profile_dir / "profile.json")
    required = {"profile_id", "engine", "model", "reference", "reference_sha256", "consent_file", "consent_sha256"}
    missing = sorted(required - profile.keys())
    if missing:
        raise VoiceCloneError("Campos ausentes no perfil: " + ", ".join(missing))
    reference = profile_dir / str(profile["reference"])
    consent = profile_dir / str(profile["consent_file"])
    if not reference.is_file() or sha256(reference) != profile["reference_sha256"]:
        raise VoiceCloneError("Referência ausente ou alterada.")
    if not consent.is_file() or sha256(consent) != profile["consent_sha256"]:
        raise VoiceCloneError("Consentimento ausente ou alterado.")
    if profile["engine"] != "qwen3-mlx":
        raise VoiceCloneError("Engine não suportada por esta versão.")
    return profile
