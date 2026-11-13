"""Aprender pronúncia: para cada palavra difícil, a skill fala algumas grafias na sua voz,
escuta cada uma (Whisper) e guarda no dicionário do perfil a que foi entendida como a palavra certa.

Também acha, num roteiro, as palavras com cara de difíceis (estrangeirismo, sigla, marca).
"""
from __future__ import annotations

import re
import tempfile
import unicodedata
from pathlib import Path

from . import fidelity, listen
from .common import VoiceCloneError, write_json
from .normalize import lang_code, spell
from .pronunciation import add, base_entries, load
from .profile import validate_profile
from .qwen3_mlx import generate_take, write_wav

CARRIER = {
    "pt": "Agora eu vou dizer {} com calma.",
    "en": "Now I am going to say {} slowly.",
    "es": "Ahora voy a decir {} con calma.",
}

_VOWELS = "aeiou"
_ACCENT = {"a": "á", "e": "ê", "i": "í", "o": "ó", "u": "ú"}
# Finais que o português e o espanhol aceitam sem vogal de apoio.
_OK_END = {"pt": set("aeiouáéíóúâêôãõrslmnz"), "es": set("aeiouáéíóúrslndz"), "en": set()}


def _plain(word: str) -> str:
    return unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode().lower()


def _adapt(term: str, lang: str) -> list[str]:
    """Grafias "abrasileiradas"/"castelhanizadas" de um termo estrangeiro."""
    if lang == "en":
        return []
    word = term.lower()
    for a, b in (("ph", "f"), ("th", "t"), ("sh", "x" if lang == "pt" else "sh"), ("ck", "k"), ("oo", "u"),
                 ("ee", "i"), ("ea", "i"), ("w", "u" if lang == "pt" else "gu"), ("y", "i")):
        word = word.replace(a, b)
    word = re.sub(r"([bcdfgjklmnpqrstvxz])\1", r"\1", word)  # consoante dobrada
    word = word.replace("k", "qu" if lang == "pt" else "k")
    options = []
    if word and word[-1] not in _OK_END[lang]:
        options.append(word + ("i" if lang == "pt" else "e"))
        options.append(word + ("e" if lang == "pt" else ""))
    else:
        options.append(word)
    stressed = []
    for option in options:
        first = next((i for i, c in enumerate(option) if c in _VOWELS), None)
        if first is not None:
            stressed.append(option[:first] + _ACCENT[option[first]] + option[first + 1:])
    return options + stressed


def variants(term: str, language: str | None, current: str | None = None, limit: int = 6) -> list[str]:
    lang = lang_code(language)
    found = [term]
    if current:
        found.append(current)
    base = {k.lower(): v for k, v in base_entries(language).items()}.get(term.lower())
    if base:
        found.append(base)
    if term.isupper() and 2 <= len(term) <= 5:
        found.append(spell(term, lang))
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", term)
    if len(parts) > 1:
        found.append(" ".join(parts))
    found.extend(_adapt(term, lang))
    unique = []
    for item in found:
        if item and item.lower() not in {u.lower() for u in unique}:
            unique.append(item)
    return unique[:limit]


def learn(profile_dir: Path, terms: list[str], language: str | None = None, takes: int = 2,
          save: bool = True, output_dir: Path | None = None) -> dict:
    """Testa as grafias de cada termo na voz do perfil e guarda a que foi ouvida certo."""
    if not listen.available():
        raise VoiceCloneError("Aprender pronúncia precisa do Whisper local (mlx-whisper). Execute voice-clone install.")
    profile = validate_profile(profile_dir)
    lang = language or profile.get("language", "Portuguese")
    carrier = CARRIER[lang_code(lang)]
    reference = fidelity.measure(profile_dir / profile["reference"])
    current = load(profile_dir, language=lang, base=False)
    results = []
    for term in terms:
        tried = []
        for spelling in variants(term, lang, current.get(term)):
            spoken = carrier.format(spelling)
            for take in range(1, takes + 1):
                samples, rate = generate_take(profile, profile_dir, spoken, language=language)
                voice = fidelity.distance(fidelity.measure_array(samples, rate), reference)
                with tempfile.TemporaryDirectory() as temp:
                    wav = Path(temp) / "palavra.wav"
                    write_wav(wav, samples, rate)
                    heard = listen.transcribe(wav, lang)
                    if output_dir:
                        output_dir.mkdir(parents=True, exist_ok=True)
                        write_wav(output_dir / f"{_plain(term)}-{len(tried) + 1:02d}.wav", samples, rate)
                target = "".join(_plain(term).split())
                heard_plain = "".join(listen.plain(heard["text"]).split())
                probability = min((w["probability"] for w in heard["words"]
                                   if target and _plain(w["word"]).strip(" .,!?") and
                                   _plain(w["word"]).strip(" .,!?") in target), default=0.0)
                # Aqui só importa se a palavra foi entendida; o tom de uma frase curta varia e não é o que se testa.
                ok = bool(target) and target in heard_plain
                tried.append({"spelling": spelling, "take": take, "heard": heard["text"], "understood": ok,
                              "confidence": probability, "semitones": voice["semitones"]})
                if ok:
                    break
            if tried and tried[-1]["understood"]:
                break  # a primeira grafia entendida basta (a própria palavra vem primeiro)
        winners = [t for t in tried if t["understood"]]
        choice = winners[0]["spelling"] if winners else None
        saved = None
        if choice and save and choice != term:
            saved = add(profile_dir, term, choice)
        results.append({"term": term, "chosen": choice, "saved": bool(saved), "tried": tried,
                        "already_right": choice == term,
                        "note": None if choice else "Nenhuma grafia foi entendida. Ouça os áudios e escreva à mão "
                                                    "com: voice-clone pronounce --add 'termo=como falar'"})
    report = {"schema_version": 1, "profile": str(profile_dir), "language": lang, "results": results}
    if output_dir:
        write_json(output_dir / "pronunciation-report.json", report)
    return report


# ---------- achar palavras difíceis num roteiro ----------

_FOREIGN = re.compile(r"(k|w|y|ph|th|sh|ck|oo|ee|[bcdfgpt]{2})", re.IGNORECASE)


def scan(text: str, language: str | None = None, entries: dict[str, str] | None = None) -> list[dict]:
    """Palavras com cara de difíceis para a voz que ainda não estão em nenhum dicionário."""
    lang = lang_code(language)
    from .normalize import ADDRESS

    known = {k.lower() for k in (entries or {})}
    text = ADDRESS.sub(" ", text)  # sites e e-mails já têm regra própria
    found: dict[str, str] = {}
    for word in re.findall(r"[A-Za-zÀ-ÿ][\w'-]*", text):
        low = word.lower()
        if low in known or low in found or len(word) < 2:
            continue
        reason = None
        if word.isupper() and len(word) <= 5:
            reason = "sigla"
        elif re.search(r"[a-z][A-Z]", word):
            reason = "marca/nome composto"
        elif lang in ("pt", "es") and _FOREIGN.search(low):
            reason = "parece estrangeira"
        elif lang in ("pt", "es") and low[-1] not in _OK_END[lang] and low[-1].isalpha():
            reason = "termina como palavra estrangeira"
        if reason:
            found[low] = reason
            found[word] = reason
    seen, result = set(), []
    for word in re.findall(r"[A-Za-zÀ-ÿ][\w'-]*", text):
        if word in found and word.lower() not in seen:
            seen.add(word.lower())
            result.append({"term": word, "reason": found[word]})
    return result
