"""Dicionário de pronúncia: troca, só no texto falado, palavras que o modelo lê errado.

Exemplo (português): "Admin" -> "Adimin", "app" -> "ápi", "combinadoemfamilia.com.br" ->
"combinado em família, ponto com, ponto bê érre". A legenda e o roteiro continuam com a grafia certa.
"""
from __future__ import annotations

import re
from pathlib import Path

from .common import read_json


def load(profile_dir: Path, extra: Path | None = None) -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in (profile_dir / "pronunciation.json", extra):
        if path and path.is_file():
            data = read_json(path)
            entries.update({str(k): str(v) for k, v in (data.get("entries") or {}).items()})
    return entries


def apply(text: str, entries: dict[str, str]) -> str:
    """Troca termos inteiros, sem diferenciar maiúsculas, numa só passada (o que já foi trocado
    não é trocado de novo); quando dois termos se sobrepõem, vale o mais longo."""
    terms = sorted((term for term in entries if term), key=len, reverse=True)
    if not terms:
        return text
    lookup = {term.lower(): entries[term] for term in terms}
    pattern = r"(?<![\w.])(" + "|".join(re.escape(term) for term in terms) + r")(?!\w)"
    return re.sub(pattern, lambda match: lookup[match.group(1).lower()], text, flags=re.IGNORECASE)
