import json
import io
import unittest
from contextlib import redirect_stdout

from voice_clone.cli import main
from voice_clone.doctor import diagnose, render_json


class DoctorTests(unittest.TestCase):
    def test_diagnose_has_safe_fields(self):
        result = diagnose()
        self.assertTrue(result.system)
        self.assertTrue(result.architecture)
        self.assertGreaterEqual(result.disk_free_gb, 0)
        self.assertTrue(result.recommended_backend)

    def test_json_is_valid(self):
        payload = json.loads(render_json(diagnose()))
        self.assertIn("missing", payload)
        self.assertIn("skill_installed", payload)

    def test_cli_doctor(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = main(["doctor", "--json"])
        self.assertEqual(result, 0)
        payload = json.loads(stream.getvalue())
        self.assertIn(payload["compatibility"], {"release-candidate", "planejado", "experimental"})


if __name__ == "__main__":
    unittest.main()
