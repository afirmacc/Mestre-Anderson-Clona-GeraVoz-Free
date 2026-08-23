from __future__ import annotations

import argparse

from . import __version__
from .doctor import diagnose, render_json, render_text


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="voice-clone")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Diagnostica o equipamento sem modificá-lo.")
    doctor.add_argument("--json", action="store_true", help="Retorna relatório JSON.")
    commands.add_parser("status", help="Mostra o estado detectado da instalação.")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = diagnose()
    if args.command == "doctor":
        print(render_json(result) if args.json else render_text(result))
        return 0
    if args.command == "status":
        print(render_text(result))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
