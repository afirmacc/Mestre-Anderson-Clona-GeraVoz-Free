from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from voice_clone.learn import scan, variants
from voice_clone.listen import compare
from voice_clone.normalize import normalize, number_words
from voice_clone.pronunciation import add, speakable


class NormalizeTests(unittest.TestCase):
    def test_numbers_in_three_languages(self) -> None:
        self.assertEqual(number_words(2026, "pt"), "dois mil e vinte e seis")
        self.assertEqual(number_words(1250, "pt"), "mil duzentos e cinquenta")
        self.assertEqual(number_words(101, "pt"), "cento e um")
        self.assertEqual(number_words(1250, "en"), "one thousand two hundred fifty")
        self.assertEqual(number_words(21, "es"), "veintiuno")

    def test_money_percent_hours_acronyms_and_addresses(self) -> None:
        spoken, changes = normalize("Custa R$ 19,90 com 30% às 10h30. CPF em afirma.cc", "Portuguese")
        self.assertIn("dezenove reais e noventa centavos", spoken)
        self.assertIn("trinta por cento", spoken)
        self.assertIn("dez horas e trinta", spoken)
        self.assertIn("cê pê éfe", spoken)
        self.assertIn("afirma ponto cê cê", spoken)
        self.assertEqual({c["kind"] for c in changes}, {"dinheiro", "porcentagem", "hora", "sigla", "endereço"})
        self.assertIn("nineteen dollars and ninety-nine cents", normalize("$19.99", "English")[0])


class DictionaryTests(unittest.TestCase):
    def test_base_dictionary_profile_wins_and_email_is_kept(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spoken, _ = speakable("Baixe o app Admin. Escreva para app@afirma.cc", root, "Portuguese")
            self.assertEqual(spoken, "Baixe o ápi Adimin. Escreva para ápi arroba afirma ponto cê cê")
            add(root, "Admin", "Ádmin")
            self.assertIn("Ádmin", speakable("Admin", root, "Portuguese")[0])
            self.assertEqual(json.loads((root / "pronunciation.json").read_text())["entries"], {"Admin": "Ádmin"})


class ListenTests(unittest.TestCase):
    def test_flags_swapped_word_and_accepts_respelled_one(self) -> None:
        heard = {"text": "O painel mostra o feedback no dashboard.", "words": []}
        changes = [{"kind": "dicionário", "written": "feedback", "spoken": "fídibéque"}]
        self.assertTrue(compare("O painel mostra o feedback no dashboard.", heard, "pt", changes)["ok"])
        wrong = {"text": "O painel mostra o fígado no dashboard.", "words": []}
        self.assertEqual(compare("O painel mostra o feedback no dashboard.", wrong, "pt", changes)["suspects"], ["feedback"])

    def test_numbers_written_or_spoken_match(self) -> None:
        heard = {"text": "São 30 por cento em 2026.", "words": []}
        self.assertTrue(compare("São 30% em 2026.", heard, "pt")["ok"])


class LearnTests(unittest.TestCase):
    def test_variants_start_with_the_word_itself(self) -> None:
        options = variants("Kindle", "Portuguese")
        self.assertEqual(options[0], "Kindle")
        self.assertIn("quindle", options)
        self.assertIn("cê pê éfe", variants("CPF", "Portuguese"))

    def test_scan_finds_foreign_words_but_not_known_or_addresses(self) -> None:
        found = [item["term"] for item in scan("O dashboard do app no Kindle. Acesse afirma.cc", "Portuguese", {"app": "ápi"})]
        self.assertEqual(found, ["dashboard", "Kindle"])


if __name__ == "__main__":
    unittest.main()
