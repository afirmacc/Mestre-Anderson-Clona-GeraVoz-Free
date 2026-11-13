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
from .operations import compare, narrate, synthesize, verify
from .profile import prepare_audio, validate_profile
from .suite import run_voice_suite


def _profile_language(profile: Path, language: str | None) -> str:
    if language:
        return language
    try:
        return validate_profile(profile).get("language", "Portuguese")
    except (VoiceCloneError, OSError):
        return "Portuguese"


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
    prepare.add_argument("--language", default="Portuguese",
                         help="Idioma da voz: Portuguese, English, Spanish, French, German, Italian, Japanese, Korean, Chinese, Russian.")
    prepare.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)

    wiz = commands.add_parser("criar-voz", aliases=["create-voice", "crear-voz"],
                              help="Assistente completo: teste de volume, leitura, análise, consentimento, perfil e teste de voz.")
    wiz.add_argument("--language", help="pt, en ou es (pergunta se faltar).")
    wiz.add_argument("--input", type=Path, help="Usar uma gravação já feita em vez de gravar agora.")
    wiz.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)
    wiz.add_argument("--device", default=":default")
    wiz.add_argument("--seconds", type=int, default=45)

    rec = commands.add_parser("record", help="Captação guiada: mostra o texto de leitura, grava o microfone e analisa a amostra.")
    rec.add_argument("--language", default="Portuguese")
    rec.add_argument("--guide", action="store_true", help="Só mostra o texto de leitura e as dicas, sem gravar.")
    rec.add_argument("--analyze", type=Path, help="Só analisa uma amostra já gravada (WAV).")
    rec.add_argument("--output", type=Path, default=Path("minha-voz.wav"))
    rec.add_argument("--seconds", type=int, default=45)
    rec.add_argument("--device", default=":default", help="Microfone no formato do AVFoundation (ex.: ':0').")
    rec.add_argument("--no-level-check", action="store_true", help="Pula o teste de volume de 5 s antes da gravação.")

    say = commands.add_parser("pronounce", help="Pronúncia: mostra como o texto será falado, acha palavras difíceis, "
                                                "aprende a grafia certa na sua voz e grava no dicionário do perfil.")
    say.add_argument("--profile", type=Path, required=True)
    say.add_argument("--language")
    say.add_argument("--text", help="Mostra como este texto será falado.")
    say.add_argument("--script", type=Path, help="Roteiro (.txt/.json): mostra as palavras difíceis ainda fora do dicionário.")
    say.add_argument("--add", nargs="+", metavar="TERMO=FALA", help="Grava no dicionário do perfil. Ex.: 'Admin=Adimin'.")
    say.add_argument("--learn", nargs="+", metavar="TERMO", help="Testa grafias de cada termo na sua voz e guarda a entendida.")
    say.add_argument("--learn-script", action="store_true", help="Com --script: aprende todas as palavras difíceis do roteiro.")
    say.add_argument("--output-dir", type=Path, help="Guarda os áudios de teste do --learn para ouvir.")
    say.add_argument("--no-save", action="store_true", help="No --learn, só relata; não grava no dicionário.")

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
    generate.add_argument("--takes", type=int, default=10,
                          help="Tomadas no máximo; grava a mais fiel ao tom e timbre da referência (1 = sem filtro).")
    generate.add_argument("--max-semitones", type=float, default=1.2)
    generate.add_argument("--max-timbre", type=float, default=6.0)
    generate.add_argument("--no-check-words", action="store_true", help="Não escuta as tomadas com o Whisper.")
    generate.add_argument("--language", help="Idioma desta fala (padrão: o do perfil).")
    generate.add_argument("--pronunciation", type=Path, help="Dicionário extra de pronúncia (JSON com 'entries').")

    script = commands.add_parser("narrate", help="Narra um roteiro: uma fala por linha, com filtro de fidelidade e volume igual.")
    script.add_argument("--profile", type=Path, required=True)
    script.add_argument("--script", type=Path, required=True, help=".txt (uma fala por linha) ou .json ({'lines': [{'text', 'speak'}]}).")
    script.add_argument("--output-dir", type=Path, required=True)
    script.add_argument("--takes", type=int, default=10)
    script.add_argument("--max-semitones", type=float, default=1.2)
    script.add_argument("--max-timbre", type=float, default=6.0)
    script.add_argument("--no-check-words", action="store_true", help="Não escuta as tomadas com o Whisper.")
    script.add_argument("--language")
    script.add_argument("--only", type=int, nargs="*", help="Regravar só estas falas (números a partir de 1).")

    comp = commands.add_parser("compare", help="Narra o mesmo roteiro em dois ou mais perfis e junta para ouvir lado a lado.")
    comp.add_argument("--profiles", type=Path, nargs="+", required=True)
    comp.add_argument("--script", type=Path, required=True)
    comp.add_argument("--output-dir", type=Path, required=True)
    comp.add_argument("--takes", type=int, default=10)
    comp.add_argument("--language")
    comp.add_argument("--no-check-words", action="store_true")

    check = commands.add_parser("verify", help="Valida integridade técnica e manifesto.")
    check.add_argument("--audio", type=Path, required=True)
    check.add_argument("--text")
    check.add_argument("--manifest", type=Path)

    test = commands.add_parser("test", help="Executa testes automatizados do pacote.")
    test.add_argument("--profile", type=Path)
    test.add_argument("--cases", type=Path)
    return root


def _script_text(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return "\n".join(str(line.get("text", "")) for line in json.loads(path.read_text(encoding="utf-8")).get("lines", []))
    return path.read_text(encoding="utf-8")


def _pronounce(args) -> int:
    from .learn import learn, scan
    from .pronunciation import add, load, speakable

    language = _profile_language(args.profile, args.language)
    done = False
    if args.add:
        for item in args.add:
            term, sep, spoken = item.partition("=")
            if not sep or not term.strip() or not spoken.strip():
                raise VoiceCloneError(f"Use TERMO=FALA (recebido: {item}).")
            _print(add(args.profile, term.strip(), spoken.strip()))
        done = True
    if args.text:
        spoken, changes = speakable(args.text, args.profile, language)
        _print({"written": args.text, "spoken": spoken, "changes": changes})
        done = True
    terms = list(args.learn or [])
    if args.script:
        found = scan(_script_text(args.script), language, load(args.profile, language=language, base=True))
        _print({"script": str(args.script), "difficult_words": found,
                "next": "voice-clone pronounce --profile <perfil> --script <roteiro> --learn-script"})
        if args.learn_script:
            terms += [item["term"] for item in found]
        done = True
    if terms:
        _print(learn(args.profile, terms, language, save=not args.no_save, output_dir=args.output_dir))
        done = True
    if not done:
        raise VoiceCloneError("Diga o que fazer: --text, --script, --add ou --learn.")
    return 0


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
            _print(prepare_audio(args.input, target, args.profile_id, args.consent, args.transcript, args.language))
        elif args.command == "profile":
            _print(validate_profile(args.profile))
        elif args.command == "synthesize":
            text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
            _print(synthesize(args.profile, text, args.output, args.manifest, takes=args.takes,
                              max_semitones=args.max_semitones, max_timbre=args.max_timbre,
                              language=args.language, pronunciation=args.pronunciation,
                              check_words=not args.no_check_words))
        elif args.command == "narrate":
            _print(narrate(args.profile, args.script, args.output_dir, takes=args.takes,
                           max_semitones=args.max_semitones, max_timbre=args.max_timbre,
                           language=args.language, only=args.only, check_words=not args.no_check_words))
        elif args.command in ("criar-voz", "create-voice", "crear-voz"):
            from .wizard import run as create_voice
            _print(create_voice(args.language, args.profiles_dir, args.device, args.seconds, args.input))
        elif args.command == "compare":
            _print(compare(args.profiles, args.script, args.output_dir, args.takes, args.language,
                           not args.no_check_words))
        elif args.command == "record":
            from .acquisition import analyze, guide, record
            if args.guide:
                info = guide(args.language)
                print("\n".join(f"• {tip}" for tip in info["tips"]) + "\n\n" + info["reading"])
            elif args.analyze:
                _print(analyze(args.analyze))
            else:
                _print(record(args.output, args.seconds, args.device, args.language, not args.no_level_check))
        elif args.command == "pronounce":
            return _pronounce(args)
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
