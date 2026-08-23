from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import unicodedata
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .audio import probe
from .common import REPORTS_DIR, STATE_FILE, VoiceCloneError, read_json, sha256, write_json
from .profile import validate_profile
from .qwen3_mlx import synthesize as mlx_synthesize


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def status() -> dict:
    state = read_json(STATE_FILE) if STATE_FILE.is_file() else {}
    components = {
        "voice_clone": __version__,
        "mlx": package_version("mlx"),
        "mlx_audio": package_version("mlx-audio"),
    }
    expected = {"mlx": "0.32.0", "mlx_audio": "0.4.7"}
    valid = platform.system() == "Darwin" and platform.machine() == "arm64"
    valid = valid and all(components[key] == value for key, value in expected.items())
    return {"schema_version": 1, "installation_valid": valid, "components": components, "state": state}


def synthesize(profile_dir: Path, text: str, output: Path, manifest: Path | None = None) -> dict:
    profile = validate_profile(profile_dir)
    if profile["engine"] != "qwen3-mlx":
        raise VoiceCloneError("BLOQUEADO_VOZ: engine do perfil não disponível.")
    generated = mlx_synthesize(profile, profile_dir, text, output)
    technical = probe(output)
    if not technical["valid"]:
        output.unlink(missing_ok=True)
        raise VoiceCloneError("BLOQUEADO_VOZ: áudio gerado inválido.")
    result = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile_id": profile["profile_id"],
        "engine": profile["engine"],
        "model": profile["model"],
        "reference_sha256": profile["reference_sha256"],
        "text": text,
        "output": str(output),
        "output_sha256": sha256(output),
        "fallback_used": False,
        "generation": generated,
        "technical_validation": technical,
        "status": "AGUARDA_QA_HUMANO",
    }
    target = manifest or output.with_suffix(".manifest.json")
    write_json(target, result)
    return result


def verify(audio: Path, expected_text: str | None, manifest: Path | None = None) -> dict:
    technical = probe(audio)
    transcription = None
    text_match = None
    transcription_error = None
    if expected_text:
        try:
            import mlx_whisper
            transcription = str(mlx_whisper.transcribe(str(audio), path_or_hf_repo="mlx-community/whisper-small-mlx")["text"]).strip()
            def normalize(value: str) -> str:
                value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
                return re.sub(r"[^a-z0-9]+", " ", value).strip()
            text_match = round(SequenceMatcher(None, normalize(expected_text), normalize(transcription)).ratio(), 4)
        except (ImportError, OSError, KeyError, TypeError) as exc:
            transcription_error = str(exc)
    result = {
        "schema_version": 1,
        "audio": str(audio),
        "audio_sha256": sha256(audio),
        "technical": technical,
        "expected_text": expected_text,
        "transcription": transcription,
        "transcription_error": transcription_error,
        "text_match": text_match,
        "human_qa_required": True,
        "status": "AGUARDA_QA_HUMANO" if technical["valid"] else "BLOQUEADO_VOZ",
    }
    if manifest:
        prior = read_json(manifest)
        if prior.get("output_sha256") != result["audio_sha256"] or prior.get("fallback_used") is not False:
            result["status"] = "BLOQUEADO_VOZ"
    if text_match is not None and text_match < 0.85:
        result["status"] = "BLOQUEADO_VOZ"
    target = REPORTS_DIR / f"verify-{audio.stem}.json"
    write_json(target, result)
    return result
