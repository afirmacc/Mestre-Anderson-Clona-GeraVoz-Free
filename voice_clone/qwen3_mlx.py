from __future__ import annotations

from pathlib import Path

from .common import VoiceCloneError


def synthesize(profile: dict, profile_dir: Path, text: str, output: Path,
               temperature: float = 0.60, top_p: float = 0.90,
               repetition_penalty: float = 1.10) -> dict:
    if not text.strip():
        raise VoiceCloneError("O texto de síntese não pode estar vazio.")
    try:
        import numpy as np
        from mlx_audio.audio_io import sf_write
        from mlx_audio.tts.utils import load_model
    except ImportError as exc:
        raise VoiceCloneError("Backend MLX ausente. Execute voice-clone install.") from exc
    reference = profile_dir / profile["reference"]
    model = load_model(profile["model"])
    results = list(model.generate(
        text=text,
        ref_audio=str(reference),
        ref_text=profile.get("reference_transcript") or None,
        lang_code=profile.get("language", "Portuguese"),
        temperature=temperature,
        top_k=50,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        max_tokens=2048,
    ))
    if not results:
        raise VoiceCloneError("O modelo não retornou áudio; nenhum fallback foi usado.")
    sample_rate = results[0].sample_rate
    if any(item.sample_rate != sample_rate for item in results):
        raise VoiceCloneError("Segmentos com taxas de amostragem incompatíveis.")
    pause = np.zeros(int(sample_rate * 0.18), dtype=np.float32)
    segments = []
    for index, item in enumerate(results):
        if index:
            segments.append(pause)
        segments.append(np.asarray(item.audio, dtype=np.float32))
    audio = np.concatenate(segments)
    output.parent.mkdir(parents=True, exist_ok=True)
    sf_write(output, audio, sample_rate, format="wav")
    return {"sample_rate": sample_rate, "segments": len(results), "duration_seconds": round(len(audio) / sample_rate, 3)}
