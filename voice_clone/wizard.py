"""`voice-clone criar-voz`: do zero até a voz pronta, num comando só.

Teste de volume → leitura guiada → análise (regrava até ficar boa) → consentimento → perfil →
frase de teste tocada na hora → a pessoa aprova (ou regrava com as dicas). Cada etapa existe
porque um erro real aconteceu sem ela: amostra baixa, pouca voz, voz tensa de "leitura de teste".
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

from .acquisition import analyze, guide, level_check, _capture
from .common import PROFILES_DIR, VoiceCloneError, read_json, write_json
from .normalize import lang_code

LANGUAGE_NAMES = {"pt": "Portuguese", "en": "English", "es": "Spanish"}
TEST_PHRASE = {
    "pt": "Olá! Esta é a minha voz digital, criada aqui no meu computador.",
    "en": "Hello! This is my digital voice, created right here on my computer.",
    "es": "¡Hola! Esta es mi voz digital, creada aquí en mi computadora.",
}


def _ask(question: str, default: str = "") -> str:
    answer = input(f"{question}{f' [{default}]' if default else ''}: ").strip()
    return answer or default


def _yes(question: str) -> bool:
    return input(f"{question} [s/N]: ").strip().lower() in {"s", "sim", "y", "yes"}


def _slug(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:40] or "minha-voz"


def _play(path: Path) -> None:
    if shutil.which("afplay"):
        subprocess.run(["afplay", str(path)], check=False)
    else:
        print(f"Ouça: {path}")


def consent_text(owner: str, own_voice: bool, purpose: str, language: str) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    who = "o próprio titular" if own_voice else _ask("Quem vai usar a voz (nome completo)")
    return (f"Titular da voz: {owner}\nResponsável pelo tratamento: {who}\nFinalidade autorizada: {purpose}\n"
            f"Ambientes/máquinas autorizados: este computador\nPrazo ou condição de revogação: até o titular pedir a exclusão\n"
            f"Data: {today}\nIdioma da voz: {language}\n"
            f"Confirmação expressa do titular: digitou AUTORIZO no assistente criar-voz em {today}\n")


def run(language: str | None = None, profiles_dir: Path = PROFILES_DIR, device: str = ":default",
        seconds: int = 45, input_file: Path | None = None) -> dict:
    from .operations import synthesize
    from .profile import prepare_audio

    lang = lang_code(language or _ask("Idioma da voz (pt, en, es)", "pt"))
    language_name = LANGUAGE_NAMES[lang]
    print("\n== 1. Quem é o dono da voz\n")
    owner = _ask("Nome completo do dono da voz")
    if not owner:
        raise VoiceCloneError("O nome do dono da voz é obrigatório.")
    own_voice = _yes("A voz é sua?")
    if not own_voice:
        print("Só continue com a pessoa presente e de acordo. Clonar alguém sem autorização é proibido.")
    purpose = _ask("Para que a voz será usada", "narração de vídeos e conteúdos próprios")
    print(f"\n{owner}, você autoriza criar e usar uma cópia digital da sua voz neste computador, "
          f"para: {purpose}? Digite AUTORIZO para confirmar.")
    if input("> ").strip().upper() != "AUTORIZO":
        raise VoiceCloneError("BLOQUEADO_VOZ: sem autorização expressa do dono da voz.")
    profile_id = _slug(_ask("Nome do perfil", _slug(owner)))
    target = profiles_dir / profile_id
    if (target / "profile.json").is_file() and not _yes(f"Já existe o perfil {profile_id}. Substituir?"):
        raise VoiceCloneError("Escolha outro nome de perfil.")

    work = Path(tempfile.mkdtemp(prefix="criar-voz-"))
    consent = work / "consentimento.txt"
    consent.write_text(consent_text(owner, own_voice, purpose, language_name), encoding="utf-8")

    info = guide(language_name)
    sample = input_file
    for attempt in range(1, 4):
        if sample is None:
            print("\n== 2. Teste de volume\n")
            print("\n".join(f"• {tip}" for tip in info["tips"]) + "\n")
            while True:
                check = level_check(device=device, language=language_name)
                print(f"→ {check['verdict']} (voz {check['speech_level_db']} dB, fundo {check['noise_floor_db']} dB)")
                if check["ready"] or not _yes("Ajustou? Testar de novo?"):
                    break
            print("\n== 3. Leitura (leia tudo com calma, no seu tom de narrar)\n")
            print(info["reading"] + "\n")
            input("Aperte Enter e comece a ler logo em seguida… ")
            sample = work / f"amostra-{attempt}.wav"
            print(f"Gravando {seconds} s… (Ctrl+C para parar quando terminar de ler)")
            _capture(sample, seconds, device)
        print("\n== 4. Análise da amostra\n")
        quality = analyze(sample)
        print(f"Voz: {quality['speech_seconds']} s · nível {quality['speech_level_db']} dB · "
              f"fundo {quality['noise_floor_db']} dB · estouro {quality['clipped_percent']}%")
        for line in quality["problems"]:
            print(f"✗ {line}")
        for line in quality["warnings"]:
            print(f"! {line}")
        if quality["ok"] and (not quality["warnings"] or not _yes("Tem avisos. Quer regravar para ficar melhor?")):
            break
        if input_file is not None:
            raise VoiceCloneError("A amostra informada não passou na análise. Grave de novo seguindo as dicas acima.")
        sample = None
    else:
        raise VoiceCloneError("A amostra não ficou boa em 3 tentativas. Revise o lugar e o microfone e rode de novo.")

    print("\n== 5. Criando o perfil\n")
    prepare_audio(sample, target, profile_id, consent, language=language_name)
    print(f"Perfil criado em {target}")

    print("\n== 6. Teste: ouça a sua voz digital\n")
    test = target / "teste-voz.wav"
    result = synthesize(target, TEST_PHRASE[lang], test, takes=10)
    _play(test)
    approved = _yes("Ficou parecida com você?")
    profile_path = target / "profile.json"
    data = read_json(profile_path)
    data["status"] = "PRONTO" if approved else "AGUARDA_TESTE"
    data["human_approval"] = {"approved": approved, "at": datetime.now().isoformat(), "test_file": str(test)}
    write_json(profile_path, data)
    shutil.rmtree(work, ignore_errors=True)
    if not approved:
        print("\nDicas para a próxima gravação: leia mais devagar, no seu tom de narrar (sem voz de 'teste'), "
              "a um palmo do microfone, em lugar silencioso. Rode de novo: voice-clone criar-voz")
    else:
        print(f"\nPronto! Para narrar um roteiro:\n  voice-clone narrate --profile {target} --script roteiro.txt "
              f"--output-dir narracao/")
    return {"profile": str(target), "status": data["status"], "test_file": str(test),
            "test_fidelity": result["generation"].get("fidelity"), "sample_quality": quality}
