from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr

from voice_clone.cli import main, parser


class CliTests(unittest.TestCase):
    def test_all_public_commands_parse(self) -> None:
        cases = [
            ["doctor"], ["status"], ["install"], ["repair"], ["test"],
            ["profile", "validate", "--profile", "/tmp/profile"],
            ["prepare", "--input", "/tmp/a.wav", "--profile-id", "teste", "--consent", "/tmp/c.txt"],
            ["synthesize", "--profile", "/tmp/p", "--text", "Olá", "--output", "/tmp/o.wav"],
            ["verify", "--audio", "/tmp/o.wav"],
        ]
        for args in cases:
            with self.subTest(args=args):
                self.assertIsNotNone(parser().parse_args(args).command)

    def test_missing_profile_is_controlled(self) -> None:
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["profile", "validate", "--profile", "/path/that/does/not/exist"])
        self.assertEqual(code, 3)
        self.assertIn("BLOQUEADO_VOZ", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
