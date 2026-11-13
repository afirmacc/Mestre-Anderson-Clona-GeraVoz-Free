"""Pronúncia: transforma o texto escrito no texto que a voz vai falar.

Ordem: dicionário (base do idioma < perfil < arquivo extra) e depois as regras automáticas
(números, dinheiro, horas, siglas, e-mails e sites, em `normalize`). Tudo só no texto falado:
a legenda e o roteiro continuam com a grafia certa.

Exemplo (português): "Admin" -> "Adimin", "app" -> "ápi", "R$ 10" -> "dez reais",
"afirma.cc" -> "afirma ponto cê cê".
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .common import read_json, write_json
from .normalize import lang_code, normalize

BASE_DIR = Path(__file__).parent / "dicionarios"


def base_entries(language: str | None) -> dict[str, str]:
    path = BASE_DIR / f"{lang_code(language)}.json"
    if not path.is_file():
        return {}
    return {str(k): str(v) for k, v in json.loads(path.read_text(encoding="utf-8")).get("entries", {}).items()}


def load(profile_dir: Path, extra: Path | None = None, language: str | None = None, base: bool = False) -> dict[str, str]:
    """Junta os dicionários; o mais específico vence (base < perfil < extra)."""
    entries: dict[str, str] = base_entries(language) if base else {}
    for path in (profile_dir / "pronunciation.json", extra):
        if path and path.is_file():
            data = read_json(path)
            for key, value in (data.get("entries") or {}).items():
                for existing in [k for k in entries if k.lower() == str(key).lower()]:
                    del entries[existing]
                entries[str(key)] = str(value)
    return entries


def apply(text: str, entries: dict[str, str], changes: list[dict] | None = None) -> str:
    """Troca termos inteiros, sem diferenciar maiúsculas, numa só passada (o que já foi trocado
    não é trocado de novo); quando dois termos se sobrepõem, vale o mais longo."""
    terms = sorted((term for term in entries if term), key=len, reverse=True)
    if not terms:
        return text
    lookup = {term.lower(): entries[term] for term in terms}
    # Não mexe em pedaço de e-mail ou de endereço (isso fica para as regras de endereço).
    pattern = r"(?<![\w.@])(" + "|".join(re.escape(term) for term in terms) + r")(?![\w@]|\.\w)"

    def swap(match: re.Match) -> str:
        spoken = lookup[match.group(1).lower()]
        if changes is not None:
            changes.append({"kind": "dicionário", "written": match.group(1), "spoken": spoken})
        return spoken

    return re.sub(pattern, swap, text, flags=re.IGNORECASE)


def speakable(text: str, profile_dir: Path, language: str | None = None, extra: Path | None = None,
              base: bool = True, rules: bool = True) -> tuple[str, list[dict]]:
    """Texto escrito -> (texto falado, lista de trocas feitas)."""
    entries = load(profile_dir, extra, language, base)
    changes: list[dict] = []
    spoken = apply(text, entries, changes)
    if rules:
        spoken, automatic = normalize(spoken, language, entries)
        changes.extend(automatic)
    return spoken, changes


def add(profile_dir: Path, term: str, spoken: str) -> dict:
    """Grava (ou troca) um termo no dicionário do perfil."""
    path = profile_dir / "pronunciation.json"
    data = read_json(path) if path.is_file() else {"schema_version": 1, "entries": {}}
    entries = data.setdefault("entries", {})
    for existing in [k for k in entries if k.lower() == term.lower()]:
        del entries[existing]
    entries[term] = spoken
    write_json(path, data)
    return {"profile_dictionary": str(path), "term": term, "spoken": spoken, "total": len(entries)}
