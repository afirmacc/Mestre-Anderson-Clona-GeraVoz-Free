from __future__ import annotations

import unittest
from pathlib import Path


class InstallerContractTests(unittest.TestCase):
    def test_installer_contains_idempotence_guards(self) -> None:
        script = (Path(__file__).resolve().parents[1] / "installers" / "install-macos.sh").read_text()
        for contract in ("REUTILIZADO: ambiente Python", "REUTILIZADO: cache do modelo", "skill Hermes", "profiles"):
            self.assertIn(contract, script)


if __name__ == "__main__":
    unittest.main()
