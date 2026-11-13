from __future__ import annotations

from pathlib import Path
import os

from .common import MODEL_CACHE, VoiceCloneError

# Janela de duração plausível para o texto, em caracteres por segundo. Fora dela a tomada
# foi cortada (curta demais) ou o modelo balbuciou/repetiu (longa demais).
MIN_CHARS_PER_SECOND = 6.0
MAX_CHARS_PER_SECOND = 16.0

_MODEL_CACHE: dict[str, object] = {}


def _load(model_id: str):
    os.environ.setdefault("HF_HOME", str(MODEL_CACHE))
    try:
        from mlx_audio.tts.utils import load_model
    except ImportError as exc:
        raise VoiceCloneError("Backend MLX ausente. Execute voice-clone install.") from exc
    if model_id not in _MODEL_CACHE:
        _MODEL_CACHE[model_id] = load_model(model_id)
    return _MODEL_CACHE[model_id]


def reference_text(profile: dict) -> str | None:
    """Por padrão NÃO envia a transcrição da referência.

    Na produção, uma transcrição curta ou que não batia exatamente com a gravação de referência
    fez o modelo cortar a fala (0,2–1,4 s) ou balbuciar por 20–30 s. Sem transcrição o resultado
    foi estável. Use `use_reference_transcript: true` no perfil só com transcrição literal e completa.
    """
    if profile.get("use_reference_transcript") and profile.get("reference_transcript"):
        return str(profile["reference_transcript"])
    return None


def generate_take(profile: dict, profile_dir: Path, text: str, temperature: float = 0.60,
                  top_p: float = 0.90, repetition_penalty: float = 1.10, language: str | None = None):
    """Gera uma tomada e devolve (amostras float32, taxa)."""
    if not text.strip():
        raise VoiceCloneError("O texto de síntese não pode estar vazio.")
    try:
        import numpy as np
    except ImportError as exc:
        raise VoiceCloneError("numpy ausente. Execute voice-clone install.") from exc
    model = _load(profile["model"])
    reference = profile_dir / profile["reference"]
    results = list(model.generate(
        text=text,
        ref_audio=str(reference),
        ref_text=reference_text(profile),
        lang_code=language or profile.get("language", "Portuguese"),
        temperature=temperature,
        top_k=50,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        max_tokens=2048,
    ))
    if not results:
        raise VoiceCloneError("O modelo não retornou áudio; nenhum fallback foi usado.")
    rate = results[0].sample_rate
    if any(item.sample_rate != rate for item in results):
        raise VoiceCloneError("Segmentos com taxas de amostragem incompatíveis.")
    pause = np.zeros(int(rate * 0.18), dtype=np.float32)
    parts = []
    for index, item in enumerate(results):
        if index:
            parts.append(pause)
        parts.append(np.asarray(item.audio, dtype=np.float32))
    return np.concatenate(parts), rate


def plausible_duration(text: str, seconds: float) -> bool:
    chars = len(text.strip())
    return chars / MAX_CHARS_PER_SECOND <= seconds <= chars / MIN_CHARS_PER_SECOND


def write_wav(path: Path, samples, rate: int) -> None:
    try:
        from mlx_audio.audio_io import sf_write
    except ImportError:
        import wave
        import numpy as np

        path.parent.mkdir(parents=True, exist_ok=True)
        pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(rate)
            handle.writeframes(pcm.tobytes())
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    sf_write(path, samples, rate, format="wav")


def synthesize(profile: dict, profile_dir: Path, text: str, output: Path,
               temperature: float = 0.60, top_p: float = 0.90,
               repetition_penalty: float = 1.10, language: str | None = None) -> dict:
    """Uma tomada, sem filtro (compatibilidade com a 0.1). Prefira operations.synthesize."""
    samples, rate = generate_take(profile, profile_dir, text, temperature, top_p, repetition_penalty, language)
    write_wav(output, samples, rate)
    return {"sample_rate": rate, "segments": 1, "duration_seconds": round(len(samples) / rate, 3)}
