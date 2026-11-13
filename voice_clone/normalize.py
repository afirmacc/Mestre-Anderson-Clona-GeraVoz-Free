"""Texto escrito -> texto falado, por idioma: números, dinheiro, porcentagem, horas, siglas,
e-mails e endereços de site. O modelo de voz lê melhor por extenso do que em símbolos.

Cada troca é registrada (`changes`) para o usuário ver o que foi feito e corrigir no dicionário.
"""
from __future__ import annotations

import re

LANGS = {"portuguese": "pt", "pt": "pt", "pt-br": "pt", "english": "en", "en": "en",
         "spanish": "es", "es": "es"}


def lang_code(language: str | None) -> str:
    return LANGS.get((language or "pt").lower(), "pt")


# ---------- números por extenso ----------

_PT_UNITS = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
             "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
_PT_TENS = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
_PT_HUNDREDS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos",
                "setecentos", "oitocentos", "novecentos"]


def _pt_below_1000(n: int) -> str:
    if n == 100:
        return "cem"
    parts = []
    if n >= 100:
        parts.append(_PT_HUNDREDS[n // 100])
        n %= 100
    if n >= 20:
        parts.append(_PT_TENS[n // 10] + (f" e {_PT_UNITS[n % 10]}" if n % 10 else ""))
    elif n or not parts:
        parts.append(_PT_UNITS[n])
    return " e ".join(parts)


def _pt_number(n: int) -> str:
    if n < 1000:
        return _pt_below_1000(n)
    groups = []
    for size, one, many in ((10**9, "um bilhão", "bilhões"), (10**6, "um milhão", "milhões"), (1000, "mil", "mil")):
        if n >= size:
            count, n = divmod(n, size)
            groups.append(one if count == 1 else f"{_pt_number(count)} {many}")
    if n:
        joiner = " e " if n < 100 or n % 100 == 0 else " "
        return " ".join(groups) + joiner + _pt_below_1000(n)
    return " ".join(groups)


_EN_UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
             "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_EN_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def _en_number(n: int) -> str:
    if n < 20:
        return _EN_UNITS[n]
    if n < 100:
        return _EN_TENS[n // 10] + (f"-{_EN_UNITS[n % 10]}" if n % 10 else "")
    if n < 1000:
        return f"{_EN_UNITS[n // 100]} hundred" + (f" {_en_number(n % 100)}" if n % 100 else "")
    for size, name in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= size:
            head, rest = divmod(n, size)
            return f"{_en_number(head)} {name}" + (f" {_en_number(rest)}" if rest else "")
    return str(n)


_ES_UNITS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once",
             "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
             "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
             "veintiocho", "veintinueve"]
_ES_TENS = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
_ES_HUNDREDS = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos",
                "setecientos", "ochocientos", "novecientos"]


def _es_number(n: int) -> str:
    if n < 30:
        return _ES_UNITS[n]
    if n < 100:
        return _ES_TENS[n // 10] + (f" y {_ES_UNITS[n % 10]}" if n % 10 else "")
    if n < 1000:
        if n == 100:
            return "cien"
        return _ES_HUNDREDS[n // 100] + (f" {_es_number(n % 100)}" if n % 100 else "")
    if n < 10**6:
        head, rest = divmod(n, 1000)
        start = "mil" if head == 1 else f"{_es_number(head)} mil"
        return start + (f" {_es_number(rest)}" if rest else "")
    head, rest = divmod(n, 10**6)
    start = "un millón" if head == 1 else f"{_es_number(head)} millones"
    return start + (f" {_es_number(rest)}" if rest else "")


def number_words(n: int, lang: str) -> str:
    return {"pt": _pt_number, "en": _en_number, "es": _es_number}[lang](n)


# ---------- letras (siglas) ----------

LETTERS = {
    "pt": dict(zip("abcdefghijklmnopqrstuvwxyz", ["á", "bê", "cê", "dê", "é", "éfe", "gê", "agá", "i", "jota", "cá",
                                                   "éle", "ême", "êne", "ó", "pê", "quê", "érre", "ésse", "tê", "u",
                                                   "vê", "dáblio", "xis", "ípsilon", "zê"])),
    "en": dict(zip("abcdefghijklmnopqrstuvwxyz", ["ay", "bee", "see", "dee", "ee", "eff", "gee", "aitch", "eye", "jay",
                                                   "kay", "el", "em", "en", "oh", "pee", "cue", "ar", "ess", "tee",
                                                   "you", "vee", "double you", "ex", "why", "zee"])),
    "es": dict(zip("abcdefghijklmnopqrstuvwxyz", ["a", "be", "ce", "de", "e", "efe", "ge", "hache", "i", "jota", "ka",
                                                   "ele", "eme", "ene", "o", "pe", "cu", "erre", "ese", "te", "u", "uve",
                                                   "uve doble", "equis", "i griega", "zeta"])),
}

WORDS = {
    "pt": {"dot": "ponto", "at": "arroba", "slash": "barra", "percent": "por cento", "and": "e", "plus": "mais",
           "times": "vezes", "comma": "vírgula", "hours": "horas", "hour": "hora", "currency": ("real", "reais"),
           "cents": ("centavo", "centavos"), "dollar": ("dólar", "dólares")},
    "en": {"dot": "dot", "at": "at", "slash": "slash", "percent": "percent", "and": "and", "plus": "plus",
           "times": "times", "comma": "point", "hours": "hours", "hour": "hour", "currency": ("real", "reais"),
           "cents": ("cent", "cents"), "dollar": ("dollar", "dollars")},
    "es": {"dot": "punto", "at": "arroba", "slash": "barra", "percent": "por ciento", "and": "y", "plus": "más",
           "times": "veces", "comma": "coma", "hours": "horas", "hour": "hora", "currency": ("real", "reales"),
           "cents": ("centavo", "centavos"), "dollar": ("dólar", "dólares")},
}

# Partes de endereço que se falam como palavra (o resto, se for curto, é soletrado).
SPOKEN_PARTS = {"com", "org", "net", "gov", "edu", "info", "app", "dev", "io", "www"}


def spell(word: str, lang: str) -> str:
    names = LETTERS[lang]
    out = []
    for char in word.lower():
        if char in names:
            out.append(names[char])
        elif char.isdigit():
            out.append(number_words(int(char), lang))
    return " ".join(out)


def _address_part(part: str, lang: str, entries: dict[str, str]) -> str:
    low = part.lower()
    if low in {k.lower() for k in entries}:
        return next(v for k, v in entries.items() if k.lower() == low)
    if low == "www":
        return spell("www", lang)
    if low in SPOKEN_PARTS or len(low) > 3:
        return part
    return spell(low, lang)


def _say_address(text: str, lang: str, entries: dict[str, str]) -> str:
    w = WORDS[lang]
    text = re.sub(r"^https?://", "", text)
    pieces = []
    for chunk in re.split(r"(/)", text.rstrip("/")):
        if chunk == "/":
            pieces.append(w["slash"])
            continue
        if not chunk:
            continue
        user, _, host = chunk.rpartition("@")
        if user:
            pieces.append(" ".join(_address_part(p, lang, entries) for p in re.split(r"[._-]", user) if p) + f" {w['at']}")
        pieces.append(f" {w['dot']} ".join(_address_part(p, lang, entries) for p in host.split(".") if p))
    return " ".join(pieces)


ADDRESS = re.compile(r"\b(?:https?://)?(?:[\w-]+(?:\.[\w-]+)*@)?(?:[\w-]+\.)+(?:com|org|net|gov|edu|br|cc|io|app|"
                     r"dev|info|me|us|uk|es|pt|ar|mx|co|ai|tv|site|online|store|tech)\b(?:/[\w./-]*)?",
                     re.IGNORECASE)


def normalize(text: str, language: str | None = None, entries: dict[str, str] | None = None,
              spell_acronyms: bool = True) -> tuple[str, list[dict]]:
    """Devolve (texto falado, trocas). `entries` (dicionário) vence as regras automáticas."""
    lang = lang_code(language)
    entries = entries or {}
    known = {k.lower() for k in entries}
    w = WORDS[lang]
    changes: list[dict] = []

    def record(kind: str, source: str, spoken: str) -> str:
        if source != spoken:
            changes.append({"kind": kind, "written": source, "spoken": spoken})
        return spoken

    def address(match: re.Match) -> str:
        found = match.group(0)
        if found.lower() in known:
            return found
        return record("endereço", found, _say_address(found, lang, entries))

    text = ADDRESS.sub(address, text)

    def money(match: re.Match) -> str:
        symbol, whole, cents = match.group(1), int(re.sub(r"[.,]", "", match.group(2))), match.group(3)
        one, many = w["dollar"] if "$" in symbol and symbol.upper() != "R$" else w["currency"]
        spoken = f"{number_words(whole, lang)} {one if whole == 1 else many}"
        if cents and int(cents):
            c1, cn = w["cents"]
            spoken += f" {w['and']} {number_words(int(cents), lang)} {c1 if int(cents) == 1 else cn}"
        return record("dinheiro", match.group(0), spoken)

    if lang == "en":
        text = re.sub(r"(R\$|US\$|\$)\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{2}))?", money, text)
    else:
        text = re.sub(r"(R\$|US\$|\$)\s?(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{2}))?", money, text)

    def hours(match: re.Match) -> str:
        h, m = int(match.group(1)), match.group(2)
        spoken = f"{number_words(h, lang)} {w['hour'] if h == 1 else w['hours']}"
        if m and int(m):
            spoken += f" {w['and']} {number_words(int(m), lang)}"
        return record("hora", match.group(0), spoken)

    if lang in ("pt", "es"):
        text = re.sub(r"\b(\d{1,2})h(\d{2})?\b", hours, text)

    def percent(match: re.Match) -> str:
        return record("porcentagem", match.group(0), f"{_say_number(match.group(1), lang)} {w['percent']}")

    text = re.sub(r"(\d+(?:[.,]\d+)?)\s?%", percent, text)

    def times(match: re.Match) -> str:
        return record("vezes", match.group(0), f"{number_words(int(match.group(1)), lang)} {w['times']}")

    text = re.sub(r"\b(\d+)\s?x\b", times, text)

    def plain_number(match: re.Match) -> str:
        return record("número", match.group(0), _say_number(match.group(0), lang))

    text = re.sub(r"(?<![\w])\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\w])|(?<![\w.,])\d+(?:,\d+)?(?![\w])"
                  if lang != "en" else r"(?<![\w])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w])|(?<![\w.,])\d+(?:\.\d+)?(?![\w])",
                  plain_number, text)

    if spell_acronyms:
        def acronym(match: re.Match) -> str:
            found = match.group(0)
            if found.lower() in known:
                return found
            return record("sigla", found, spell(found, lang))

        text = re.sub(r"\b[A-Z]{2,5}\b", acronym, text)
    return text, changes


def _say_number(raw: str, lang: str) -> str:
    w = WORDS[lang]
    decimal_mark = "." if lang == "en" else ","
    thousands = "," if lang == "en" else "."
    whole, _, fraction = raw.replace(thousands, "").partition(decimal_mark)
    spoken = number_words(int(whole), lang)
    if fraction:
        spoken += f" {w['comma']} " + (" ".join(number_words(int(d), lang) for d in fraction)
                                      if fraction.startswith("0") else number_words(int(fraction), lang))
    return spoken
