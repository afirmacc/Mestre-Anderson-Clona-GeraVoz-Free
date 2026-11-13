"""Fidelidade vocal: compara tom (F0) e timbre de uma tomada com a amostra de referência.

O modelo de clonagem às vezes devolve outra voz na mesma chamada (na prática, uma fala saiu
8 semitons acima da referência). Este módulo mede cada tomada para que só a mais fiel seja usada.
Depende apenas de numpy; o áudio é lido como WAV PCM.
"""
from __future__ import annotations

import math
import wave
from pathlib import Path

from .common import VoiceCloneError

# Limites da produção (voz masculina, português). O tom é o sinal decisivo: a troca de voz real
# saiu 8 semitons acima, com timbre ~10. O timbre varia com o conteúdo da frase (muito "s" mede
# mais longe), então o limite dele só pega mudança grosseira; 4,3 barrava tomadas boas.
DEFAULT_MAX_SEMITONES = 1.2   # distância máxima do tom mediano da referência
DEFAULT_MAX_TIMBRE = 6.0      # distância máxima do espectro médio em 24 faixas


def read_wav(path: Path):
    import numpy as np

    try:
        with wave.open(str(path), "rb") as handle:
            rate, channels, width = handle.getframerate(), handle.getnchannels(), handle.getsampwidth()
            raw = handle.readframes(handle.getnframes())
    except (OSError, wave.Error) as exc:
        raise VoiceCloneError(f"WAV inválido: {path}") from exc
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(width)
    if dtype is None:
        raise VoiceCloneError(f"Largura de amostra não suportada: {width * 8} bits")
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    peak = float(np.abs(samples).max()) if samples.size else 0.0
    return (samples / peak if peak else samples), rate


def measure_array(samples, rate: int) -> dict:
    """Tom mediano (Hz) e perfil de timbre (24 faixas logarítmicas, média removida)."""
    import numpy as np

    frame, hop = int(rate * 0.04), int(rate * 0.01)
    if samples.size < frame * 2:
        raise VoiceCloneError("Áudio curto demais para medir a voz.")
    starts = range(0, samples.size - frame, hop)
    energy = np.array([np.sqrt((samples[i:i + frame] ** 2).mean()) for i in starts])
    threshold = np.percentile(energy, 60)
    low, high = int(rate / 350), int(rate / 60)
    edges = np.geomspace(100, min(7000, rate / 2 - 1), 25)
    window = np.hanning(frame)
    freqs = np.fft.rfftfreq(2048, 1 / rate)
    pitches, spectra = [], []
    for k, i in enumerate(starts):
        if energy[k] < threshold:
            continue
        chunk = samples[i:i + frame] * window
        corr = np.correlate(chunk, chunk, "full")[frame - 1:]
        if corr[0] > 0:
            corr = corr / corr[0]
            lag = low + int(np.argmax(corr[low:high]))
            if corr[lag] > 0.45:
                pitches.append(rate / lag)
        power = np.abs(np.fft.rfft(chunk, 2048)) ** 2
        spectra.append([math.log(power[(freqs >= a) & (freqs < b)].mean() + 1e-9) for a, b in zip(edges[:-1], edges[1:])])
    if not spectra:
        raise VoiceCloneError("Não há voz suficiente no áudio para medir.")
    profile = np.mean(spectra, axis=0)
    return {"f0_hz": float(np.median(pitches)) if pitches else 0.0, "timbre": (profile - profile.mean()).tolist()}


def measure(path: Path) -> dict:
    samples, rate = read_wav(path)
    return measure_array(samples, rate)


def distance(take: dict, reference: dict) -> dict:
    import numpy as np

    if take["f0_hz"] <= 0 or reference["f0_hz"] <= 0:
        semitones = 99.0
    else:
        semitones = abs(12 * math.log2(take["f0_hz"] / reference["f0_hz"]))
    timbre = float(np.linalg.norm(np.array(take["timbre"]) - np.array(reference["timbre"])))
    return {"f0_hz": round(take["f0_hz"], 1), "semitones": round(semitones, 2), "timbre": round(timbre, 2),
            "score": round(semitones * 2 + timbre, 3)}


def accepted(result: dict, max_semitones: float = DEFAULT_MAX_SEMITONES, max_timbre: float = DEFAULT_MAX_TIMBRE) -> bool:
    return result["semitones"] <= max_semitones and result["timbre"] <= max_timbre
