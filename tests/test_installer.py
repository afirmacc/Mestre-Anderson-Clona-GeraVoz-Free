from __future__ import annotations

import unittest
from pathlib import Path


class InstallerContractTests(unittest.TestCase):
    def test_installer_contains_idempotence_guards(self) -> None:
        script = (Path(__file__).resolve().parents[1] / "installers" / "install-macos.sh").read_text()
        for contract in ("REUTILIZADO: ambiente Python", "REUTILIZADO: cache do modelo", "skill Hermes", "profiles"):
            self.assertIn(contract, script)

    def test_installer_regressions_from_external_validation(self) -> None:
        script = (Path(__file__).resolve().parents[1] / "installers" / "install-macos.sh").read_text()
        self.assertIn("model-cache/hub", script.replace('$MODEL_CACHE/', 'model-cache/'))
        self.assertIn("REUTILIZADO: pacote ia-skill-clonagem-voz", script)
        self.assertIn("cd -P", script)
        self.assertIn("SMOKE OK", script)
        self.assertIn("--smoke-profile", script)
        self.assertIn("VOICE_CLONE_INVOKING_PYTHON", script)


if __name__ == "__main__":
    unittest.main()
