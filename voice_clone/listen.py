"""Escuta automática: transcreve cada tomada (Whisper local) e aponta as palavras que não
foram ouvidas como deveriam. É a forma de a skill perceber, sozinha, uma pronúncia errada.

O Whisper tende a "corrigir" o que ouve, então isto não substitui o ouvido humano: ele pega
os erros grosseiros (palavra trocada, engolida, sigla lida errado) e as palavras de baixa confiança.
"""
from __future__ import annotations

import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from .normalize import lang_code, normalize

DEFAULT_MODEL = os.environ.get("VOICE_CLONE_LISTEN_MODEL", "mlx-community/whisper-small-mlx")
LOW_CONFIDENCE = 0.35


def available() -> bool:
    try:
        import mlx_whisper  # noqa: F401
    except ImportError:
        return False
    return True


def plain(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def comparable(text: str, language: str | None) -> list[str]:
    """Palavras comparáveis: números por extenso, sem acento, sem pontuação."""
    spoken, _ = normalize(text, language, spell_acronyms=False)
    return plain(spoken).split()


def transcribe(path: Path, language: str | None = None, model: str | None = None) -> dict:
    import mlx_whisper

    result = mlx_whisper.transcribe(str(path), path_or_hf_repo=model or DEFAULT_MODEL,
                                    language=lang_code(language), word_timestamps=True,
                                    condition_on_previous_text=False)
    words = [{"word": w["word"].strip(), "probability": round(float(w.get("probability", 1.0)), 3)}
             for segment in result.get("segments", []) for w in segment.get("words", [])]
    return {"text": str(result.get("text", "")).strip(), "words": words}


def compare(written: str, heard: dict, language: str | None = None, changes: list[dict] | None = None) -> dict:
    """Compara o texto escrito com o que foi ouvido. Devolve nota (0–1) e palavras suspeitas."""
    expected = comparable(written, language)
    got = comparable(heard["text"], language)
    matcher = SequenceMatcher(None, expected, got, autojunk=False)
    suspects: list[str] = []
    for op, a1, a2, b1, b2 in matcher.get_opcodes():
        if op == "equal":
            continue
        if "".join(expected[a1:a2]) == "".join(got[b1:b2]):
            continue  # só espaçamento diferente ("e mail" x "email")
        if a2 > a1 and b2 > b1 and SequenceMatcher(None, " ".join(expected[a1:a2]), " ".join(got[b1:b2])).ratio() >= 0.8:
            continue  # grafia vizinha do mesmo som
        suspects.extend(expected[a1:a2])
    # Palavra trocada pelo dicionário vale se foi ouvida pela grafia certa OU pela grafia falada.
    heard_joined = "".join(got)
    for change in changes or []:
        written_form, spoken_form = "".join(plain(change["written"]).split()), "".join(plain(change["spoken"]).split())
        if written_form in heard_joined or (spoken_form and spoken_form in heard_joined):
            for part in plain(change["written"]).split():
                if part in suspects:
                    suspects.remove(part)
    low = [w["word"] for w in heard["words"] if w["probability"] < LOW_CONFIDENCE and plain(w["word"])]
    ratio = SequenceMatcher(None, " ".join(expected), " ".join(got)).ratio()
    return {"heard": heard["text"], "word_match": round(ratio, 3), "suspects": suspects,
            "low_confidence": low, "ok": not suspects and ratio >= 0.85}
