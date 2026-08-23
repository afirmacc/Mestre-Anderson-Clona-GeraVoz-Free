from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

from . import __version__
from .common import PROFILES_DIR, VoiceCloneError
from .doctor import diagnose, render_json, render_text
from .operations import status as installation_status
from .operations import synthesize, verify
from .profile import prepare_audio, validate_profile
from .suite import run_voice_suite


def _print(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="voice-clone")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Diagnostica o equipamento sem modificá-lo.")
    doctor.add_argument("--json", action="store_true", help="Retorna relatório JSON.")
    commands.add_parser("status", help="Valida a instalação atual.")
    commands.add_parser("install", help="Executa o instalador idempotente do macOS.")
    commands.add_parser("repair", help="Repara somente componentes ausentes ou inválidos.")

    prepare = commands.add_parser("prepare", help="Cria um perfil privado a partir de amostra autorizada.")
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--profile-id", required=True)
    prepare.add_argument("--consent", type=Path, required=True)
    prepare.add_argument("--transcript")
    prepare.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)

    profile = commands.add_parser("profile", help="Opera perfis privados.")
    profile_commands = profile.add_subparsers(dest="profile_command", required=True)
    profile_validate = profile_commands.add_parser("validate")
    profile_validate.add_argument("--profile", type=Path, required=True)

    generate = commands.add_parser("synthesize", help="Sintetiza sem fallback usando o perfil declarado.")
    generate.add_argument("--profile", type=Path, required=True)
    text_group = generate.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text")
    text_group.add_argument("--text-file", type=Path)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--manifest", type=Path)

    check = commands.add_parser("verify", help="Valida integridade técnica e manifesto.")
    check.add_argument("--audio", type=Path, required=True)
    check.add_argument("--text")
    check.add_argument("--manifest", type=Path)

    test = commands.add_parser("test", help="Executa testes automatizados do pacote.")
    test.add_argument("--profile", type=Path)
    test.add_argument("--cases", type=Path)
    return root


def _run_installer(repair: bool = False) -> int:
    source_script = Path(__file__).resolve().parents[1] / "installers" / "install-macos.sh"
    wheel_script = Path(sysconfig.get_path("data")) / "share/ia-skill-clonagem-voz/install-macos.sh"
    script = source_script if source_script.is_file() else wheel_script
    if not script.is_file():
        raise VoiceCloneError("Instalador não incluído no pacote. Reinstale a versão oficial.")
    command = ["bash", str(script)] + (["--repair"] if repair else [])
    environment = os.environ.copy()
    environment["VOICE_CLONE_INVOKING_PYTHON"] = sys.executable
    return subprocess.run(command, check=False, env=environment).returncode


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            result = diagnose()
            print(render_json(result) if args.json else render_text(result))
        elif args.command == "status":
            _print(installation_status())
        elif args.command == "install":
            return _run_installer()
        elif args.command == "repair":
            return _run_installer(repair=True)
        elif args.command == "prepare":
            target = args.profiles_dir / args.profile_id
            _print(prepare_audio(args.input, target, args.profile_id, args.consent, args.transcript))
        elif args.command == "profile":
            _print(validate_profile(args.profile))
        elif args.command == "synthesize":
            text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
            _print(synthesize(args.profile, text, args.output, args.manifest))
        elif args.command == "verify":
            _print(verify(args.audio, args.text, args.manifest))
        elif args.command == "test":
            if args.profile:
                _print(run_voice_suite(args.profile, args.cases))
                return 0
            source_root = Path(__file__).resolve().parents[1]
            if (source_root / "tests").is_dir():
                command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
                return subprocess.run(command, cwd=source_root, check=False).returncode
            result = installation_status()
            _print(result)
            return 0 if result["installation_valid"] else 3
        else:
            return 2
        return 0
    except (VoiceCloneError, OSError) as exc:
        print(f"BLOQUEADO_VOZ: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
