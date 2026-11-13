"""Captação da voz: texto de leitura por idioma, gravação guiada pelo microfone e análise da amostra.

A amostra é o que mais pesa no resultado. O texto de leitura cobre os sons do idioma (vogais
abertas e fechadas, nasais, lh/nh, r forte e fraco, s/z/x/ch/j), pergunta, exclamação e pausas
naturais, em ~40 s. A análise recusa amostra curta, estourada ou ruidosa e diz como regravar.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

from .common import VoiceCloneError
from .normalize import lang_code

READING = {
    "pt": (
        "Olá! Estou gravando esta leitura para criar a minha voz digital, com a minha autorização.\n"
        "Hoje o céu amanheceu limpo e a cidade acordou devagar.\n"
        "Você já reparou como o cheiro do café muda a manhã?\n"
        "Gosto de conversar com calma, rir das coisas simples e explicar cada ideia, passo a passo.\n"
        "A zebra e o jacaré dividiram uma xícara de chá, com jeito e sem pressa.\n"
        "O carro vermelho parou na rua estreita, perto da ponte velha.\n"
        "Será que amanhã vai chover? Quem sabe!\n"
        "Seja como for, sigo em frente: trabalho, família, amigos e um bom livro no fim do dia.\n"
        "Muito obrigado por ouvir."
    ),
    "en": (
        "Hello! I am recording this reading to create my digital voice, with my own permission.\n"
        "This morning the sky was clear and the city woke up slowly.\n"
        "Have you ever noticed how the smell of coffee changes the whole day?\n"
        "I like to talk calmly, laugh at simple things and explain each idea, step by step.\n"
        "The quick brown fox jumps over the lazy dog, then thinks about the weather.\n"
        "She sells fresh bread and cheese at the little shop near the bridge.\n"
        "Will it rain tomorrow? Who knows!\n"
        "Either way, I keep going: work, family, friends and a good book at the end of the day.\n"
        "Thank you very much for listening."
    ),
    "es": (
        "¡Hola! Estoy grabando esta lectura para crear mi voz digital, con mi propia autorización.\n"
        "Hoy el cielo amaneció despejado y la ciudad despertó despacio.\n"
        "¿Alguna vez notaste cómo el olor del café cambia la mañana?\n"
        "Me gusta conversar con calma, reírme de las cosas simples y explicar cada idea, paso a paso.\n"
        "El perro corre por la calle mientras la llave gira en la cerradura.\n"
        "Junto al río, un niño y su abuela comparten chocolate y churros.\n"
        "¿Lloverá mañana? ¡Quién sabe!\n"
        "Sea como sea, sigo adelante: trabajo, familia, amigos y un buen libro al final del día.\n"
        "Muchas gracias por escuchar."
    ),
}

TIPS = {
    "pt": ["Ambiente silencioso, sem ventilador, ar-condicionado ou TV.",
           "Microfone a um palmo da boca, sempre na mesma distância. O celular perto da boca (gravador ou áudio de WhatsApp) costuma dar uma amostra ótima.",
           "Leia com a sua voz de narrar: calma, no seu tom natural. Ler \"de teste\" deixa a voz tensa e mais aguda, e o clone copia isso.",
           "Pode errar e repetir a frase; não tem problema.",
           "Só você falando, sem música de fundo."],
    "en": ["Quiet room: no fan, air conditioning or TV.",
           "Microphone about a hand's width from your mouth, at a steady distance. A phone held close (voice memo or WhatsApp audio) usually gives a great sample.",
           "Read in your narration voice: calm, in your natural pitch. Reading \"for a test\" makes the voice tense and higher, and the clone copies that.",
           "It is fine to stumble and repeat a sentence.",
           "Only you speaking, no background music."],
    "es": ["Ambiente silencioso, sin ventilador, aire acondicionado ni TV.",
           "Micrófono a un palmo de la boca, siempre a la misma distancia. El celular cerca de la boca (grabadora o audio de WhatsApp) suele dar una muestra excelente.",
           "Lee con tu voz de narrar: con calma, en tu tono natural. Leer \"de prueba\" tensa la voz y la vuelve más aguda, y el clon copia eso.",
           "Puedes equivocarte y repetir la frase.",
           "Solo tú hablando, sin música de fondo."],
}


def guide(language: str | None = None) -> dict:
    lang = lang_code(language)
    return {"language": lang, "reading": READING[lang], "tips": TIPS[lang],
            "target_seconds": "25 a 40", "minimum_seconds": 15}


def _capture(output: Path, seconds: int, device: str) -> None:
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-f", "avfoundation", "-i", device,
               "-t", str(seconds), "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(output)]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise VoiceCloneError("FFmpeg não encontrado. Execute voice-clone install.") from exc
    except subprocess.CalledProcessError as exc:
        raise VoiceCloneError("Não consegui gravar. Libere o microfone para o Terminal em Ajustes do Sistema > "
                              "Privacidade e Segurança > Microfone, ou indique outro --device.") from exc
    except KeyboardInterrupt:
        pass
    if not output.is_file():
        raise VoiceCloneError("Nada foi gravado.")


def _levels(path: Path) -> tuple[float, float, float]:
    """(nível da fala em dB, pico 0–1, frames em dB) de uma gravação curta."""
    import numpy as np

    samples, rate = _read(path)
    frame = int(rate * 0.03)
    frames = samples[: samples.size // frame * frame].reshape(-1, frame)
    rms_db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    return float(np.percentile(rms_db, 90)), float(np.abs(samples).max()), rms_db


def level_check(seconds: int = 5, device: str = ":default", language: str | None = None) -> dict:
    """Teste rápido antes da leitura: 1,5 s de silêncio (mede o fundo) e 5 s de fala (mede a voz).

    O fundo é medido em silêncio de verdade. Medir no meio da fala deu alarme falso de
    "ruído alto" no teste real (fundo −38 dB no teste, −58 dB na gravação).
    """
    import tempfile

    import numpy as np

    first = READING[lang_code(language)].splitlines()[0]
    with tempfile.TemporaryDirectory() as temp:
        quiet, voice = Path(temp) / "silencio.wav", Path(temp) / "fala.wav"
        print("Fique em silêncio 2 segundos…")
        _capture(quiet, 2, device)
        _, _, quiet_db = _levels(quiet)
        print(f"Agora leia em voz de narrar ({seconds} s): \"{first}\"")
        _capture(voice, seconds, device)
        speech_db, peak, _ = _levels(voice)
    noise_db = float(np.median(quiet_db[len(quiet_db) // 4:]))  # pula o começo (clique de abrir o microfone)
    if peak >= 0.99:
        verdict, ready = "Estourando. Afaste o microfone ou baixe o volume de entrada.", False
    elif speech_db < -30:
        verdict, ready = ("Voz baixa. Chegue o microfone a um palmo da boca ou aumente o volume de entrada em "
                          "Ajustes do Sistema > Som > Entrada."), False
    elif noise_db > -50:
        verdict, ready = "Ruído de fundo alto. Desligue ventilador, ar ou TV, ou mude de lugar.", False
    elif speech_db - noise_db < 25:
        verdict, ready = "A voz está perto demais do ruído. Fale mais perto do microfone.", False
    else:
        verdict, ready = "Volume bom. Pode gravar.", True
    return {"speech_level_db": round(speech_db, 1), "noise_floor_db": round(noise_db, 1), "ready": ready,
            "verdict": verdict}


def record(output: Path, seconds: int = 45, device: str = ":default", language: str | None = None,
           check_level: bool = True) -> dict:
    """Grava do microfone (macOS, FFmpeg + AVFoundation): teste de volume, texto, gravação e análise."""
    info = guide(language)
    print("\n".join(f"• {tip}" for tip in info["tips"]) + "\n")
    if check_level:
        for attempt in range(3):
            check = level_check(device=device, language=language)
            print(f"→ {check['verdict']} (voz {check['speech_level_db']} dB, fundo {check['noise_floor_db']} dB)\n")
            if check["ready"]:
                break
            if attempt < 2:
                input("Ajuste e aperte Enter para testar de novo… ")
        else:
            raise VoiceCloneError("O volume não ficou bom em 3 testes. Ajuste o microfone e rode de novo "
                                  "(ou use --no-level-check por sua conta).")
    print(info["reading"] + "\n")
    print(f"Gravando {seconds} s… (Ctrl+C para parar antes)")
    output.parent.mkdir(parents=True, exist_ok=True)
    _capture(output, seconds, device)
    return analyze(output)


def _read(path: Path):
    import numpy as np

    try:
        with wave.open(str(path), "rb") as handle:
            rate, channels, width = handle.getframerate(), handle.getnchannels(), handle.getsampwidth()
            raw = handle.readframes(handle.getnframes())
    except (OSError, wave.Error) as exc:
        raise VoiceCloneError(f"WAV inválido: {path}") from exc
    if width != 2:
        raise VoiceCloneError("A análise espera WAV de 16 bits (o prepare já converte).")
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return samples, rate


def analyze(path: Path) -> dict:
    """Mede a amostra e diz, em linguagem simples, o que corrigir. `ok` falso = regravar."""
    import numpy as np

    samples, rate = _read(path)
    if samples.size < rate:
        raise VoiceCloneError("Amostra vazia ou com menos de 1 s.")
    frame = int(rate * 0.03)
    frames = samples[: samples.size // frame * frame].reshape(-1, frame)
    rms_db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    noise_db = float(np.percentile(rms_db, 10))
    speech_db = float(np.percentile(rms_db, 90))
    voiced = rms_db > max(noise_db + 12, -50)
    speech_seconds = float(voiced.sum() * frame / rate)
    total_seconds = samples.size / rate
    clipped = float((np.abs(samples) >= 0.995).mean() * 100)
    peak_db = float(20 * np.log10(np.abs(samples).max() + 1e-9))
    snr = speech_db - noise_db
    problems, warnings = [], []
    if speech_seconds < 15:
        # Teste real: 11 s de voz útil deram um clone ruim; o perfil bom tinha 26 s.
        problems.append(f"Pouca voz ({speech_seconds:.0f} s; o mínimo é 15). Leia o texto inteiro: 25 a 40 s de fala.")
    elif speech_seconds < 25:
        warnings.append(f"Voz curta ({speech_seconds:.0f} s). Com 25 a 40 s o clone fica mais estável.")
    if speech_seconds > 60:
        warnings.append("Amostra longa (mais de 60 s de voz). 25 a 40 s bastam; o excesso só deixa mais lento.")
    if clipped > 0.1:
        problems.append(f"Áudio estourado ({clipped:.2f}% saturado). Afaste o microfone ou baixe o ganho.")
    quiet = speech_db < -30 or peak_db < -18
    if quiet:
        # Teste real: amostra a -35 dB, mesmo com o volume igualado depois, gerou um clone ruim. Barra.
        problems.append(f"Voz baixa (nível {speech_db:.0f} dB; o ideal é entre −25 e −12). Chegue o microfone a um palmo "
                        "da boca ou aumente o volume de entrada em Ajustes do Sistema > Som > Entrada.")
    if snr < 15 and not quiet:
        problems.append(f"Ruído alto (voz só {snr:.0f} dB acima do fundo). Grave em lugar silencioso.")
    elif snr < 15:
        problems.append(f"A voz quase se mistura com o fundo ({snr:.0f} dB). Aumente o volume da voz e grave de novo.")
    elif snr < 25 and noise_db > -50:
        warnings.append(f"Ruído de fundo em {noise_db:.0f} dB (melhor abaixo de −50). Desligue ventilador, ar ou TV.")
    if total_seconds and speech_seconds / total_seconds < 0.5:
        warnings.append("Pouca fala reconhecida na gravação." + (" Com o volume baixo, parte da voz pode ter passado por "
                        "silêncio; resolva o volume primeiro." if quiet else " Comece a ler logo e corte as pausas longas."))
    return {
        "file": str(path), "total_seconds": round(total_seconds, 1), "speech_seconds": round(speech_seconds, 1),
        "noise_floor_db": round(noise_db, 1), "speech_level_db": round(speech_db, 1), "snr_db": round(snr, 1),
        "peak_db": round(peak_db, 1), "clipped_percent": round(clipped, 3),
        "problems": problems, "warnings": warnings, "ok": not problems,
    }
