from __future__ import annotations

import importlib.metadata
import os
import platform
import re
import shutil
import sys
import unicodedata
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .audio import probe
from .common import REPORTS_DIR, STATE_FILE, VoiceCloneError, model_cache_path, read_json, sha256, write_json
from .profile import validate_profile
from . import fidelity
from . import listen
from .pronunciation import speakable
from .qwen3_mlx import generate_take, plausible_duration, write_wav
from .qwen3_mlx import synthesize as mlx_synthesize


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def status() -> dict:
    state = read_json(STATE_FILE) if STATE_FILE.is_file() else {}
    components = {
        "voice_clone": __version__,
        "mlx": package_version("mlx"),
        "mlx_audio": package_version("mlx-audio"),
        "mlx_whisper": package_version("mlx-whisper"),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "git": shutil.which("git"),
        "python_executable": sys.executable,
        "model_cache": str(model_cache_path()) if model_cache_path() else None,
        "state_file": str(STATE_FILE) if STATE_FILE.is_file() else None,
    }
    hermes_root = Path(os.environ.get("HERMES_SKILLS_DIR", Path.home() / ".hermes/skills/local"))
    hermes_target = hermes_root / "mestre-anderson-clona-geravoz-free"
    components["hermes_skill"] = str(hermes_target.resolve()) if (hermes_target / "SKILL.md").is_file() else None
    expected = {"mlx": "0.32.0", "mlx_audio": "0.4.7"}
    valid = platform.system() == "Darwin" and platform.machine() == "arm64"
    valid = valid and all(components[key] == value for key, value in expected.items())
    valid = valid and bool(components["mlx_whisper"] and components["ffmpeg"] and components["ffprobe"])
    valid = valid and bool(components["model_cache"] and components["state_file"] and components["hermes_skill"])
    missing = [key for key in ("mlx", "mlx_audio", "mlx_whisper", "ffmpeg", "ffprobe", "model_cache", "state_file", "hermes_skill") if not components[key]]
    return {"schema_version": 1, "installation_valid": valid, "missing": missing, "components": components, "state": state}


def _best_take(profile: dict, profile_dir: Path, spoken: str, output: Path, takes: int,
               max_semitones: float, max_timbre: float, language: str | None,
               written: str | None = None, changes: list[dict] | None = None, check_words: bool = True) -> dict:
    """Gera até `takes` tomadas e grava a melhor.

    Cada tomada passa por três filtros: duração plausível (descarta corte e balbucio), fidelidade
    da voz (tom e timbre da referência) e, com o Whisper instalado, escuta das palavras (aponta
    pronúncia errada). Para na primeira tomada que passa em tudo. Se nenhuma passar, grava a de
    melhor nota e marca para conferir.
    """
    import tempfile

    reference = fidelity.measure(profile_dir / profile["reference"])
    listening = check_words and listen.available()
    best = None
    attempts = []
    for number in range(1, takes + 1):
        samples, rate = generate_take(profile, profile_dir, spoken, language=language)
        seconds = len(samples) / rate
        if not plausible_duration(spoken, seconds):
            attempts.append({"take": number, "duration_seconds": round(seconds, 2), "discarded": "duration"})
            continue
        result = fidelity.distance(fidelity.measure_array(samples, rate), reference)
        attempt = {"take": number, "duration_seconds": round(seconds, 2), **result}
        voice_ok = fidelity.accepted(result, max_semitones, max_timbre)
        words = None
        score = result["score"]
        if listening and result["semitones"] <= max_semitones:
            with tempfile.TemporaryDirectory() as temp:
                probe_wav = Path(temp) / "tomada.wav"
                write_wav(probe_wav, samples, rate)
                words = listen.compare(written or spoken, listen.transcribe(probe_wav, language or profile.get("language")),
                                       language or profile.get("language"), changes)
            attempt["words"] = words
            score += 4 * len(words["suspects"]) + 10 * (1 - words["word_match"])
        elif listening:
            score += 20  # voz fora do tom: nem vale escutar, mas continua candidata se nada passar
        attempts.append(attempt)
        if best is None or score < best[0]:
            best = (score, result, words, samples, rate, number)
        if voice_ok and (words is None or words["ok"]):
            break
    if best is None:
        raise VoiceCloneError("BLOQUEADO_VOZ: nenhuma tomada com duração plausível para o texto.")
    _, result, words, samples, rate, number = best
    write_wav(output, samples, rate)
    return {
        "sample_rate": rate, "segments": 1, "duration_seconds": round(len(samples) / rate, 3),
        "chosen_take": number, "takes_tried": len(attempts), "attempts": attempts,
        "reference_f0_hz": round(reference["f0_hz"], 1),
        "fidelity": result, "fidelity_ok": fidelity.accepted(result, max_semitones, max_timbre),
        "words": words, "words_checked": listening,
        "words_ok": None if words is None else words["ok"],
    }


def synthesize(profile_dir: Path, text: str, output: Path, manifest: Path | None = None,
               takes: int = 1, max_semitones: float = fidelity.DEFAULT_MAX_SEMITONES,
               max_timbre: float = fidelity.DEFAULT_MAX_TIMBRE, language: str | None = None,
               pronunciation: Path | None = None, speak: str | None = None,
               base_dictionary: bool = True, rules: bool = True, check_words: bool = True) -> dict:
    """Sintetiza `text`. `speak` (opcional) é a grafia falada já pronta; sem ela, o texto passa
    pelo dicionário (base do idioma + perfil + extra) e pelas regras de números, siglas e endereços."""
    profile = validate_profile(profile_dir)
    if profile["engine"] != "qwen3-mlx":
        raise VoiceCloneError("BLOQUEADO_VOZ: engine do perfil não disponível.")
    lang = language or profile.get("language", "Portuguese")
    if speak:
        spoken, changes = speak, [{"kind": "roteiro", "written": text, "spoken": speak}]
    else:
        spoken, changes = speakable(text, profile_dir, lang, pronunciation, base_dictionary, rules)
    if takes > 1:
        generated = _best_take(profile, profile_dir, spoken, output, takes, max_semitones, max_timbre, language,
                               written=text, changes=changes, check_words=check_words)
    else:
        extra = {"language": language} if language else {}
        generated = mlx_synthesize(profile, profile_dir, spoken, output, **extra)
    technical = probe(output)
    if not technical["valid"]:
        output.unlink(missing_ok=True)
        raise VoiceCloneError("BLOQUEADO_VOZ: áudio gerado inválido.")
    status = "AGUARDA_QA_HUMANO"
    if takes > 1 and not generated.get("fidelity_ok"):
        status = "CONFERIR_FIDELIDADE"
    elif takes > 1 and generated.get("words_ok") is False:
        status = "CONFERIR_PRONUNCIA"
    result = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile_id": profile["profile_id"],
        "engine": profile["engine"],
        "model": profile["model"],
        "reference_sha256": profile["reference_sha256"],
        "text": text,
        "spoken_text": spoken,
        "pronunciation_changes": changes,
        "output": str(output),
        "output_sha256": sha256(output),
        "fallback_used": False,
        "generation": generated,
        "technical_validation": technical,
        "status": status,
    }
    if status == "CONFERIR_PRONUNCIA":
        result["hint"] = ("Palavras suspeitas: " + ", ".join(generated["words"]["suspects"]) +
                          ". Teste com: voice-clone pronounce --learn <palavra>, ou ajuste o dicionário do perfil.")
    target = manifest or output.with_suffix(".manifest.json")
    write_json(target, result)
    return result


def level(source: Path, target: Path, mean_db: float = -20.0) -> dict:
    """Iguala o volume médio de uma fala (sem isso a narração "pula" de volume entre falas)."""
    import subprocess

    def run(command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(command, check=True, capture_output=True, text=True)

    cut = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03"
    trimmed = target.with_suffix(".trim.wav")
    try:
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source), "-af", f"{cut},areverse,{cut},areverse", str(trimmed)])
        stats = run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(trimmed), "-af", "volumedetect", "-f", "null", "-"]).stderr
        current = float(re.search(r"mean_volume: (-?[\d.]+) dB", stats).group(1))
        seconds = probe(trimmed)["duration_seconds"]
        gain = mean_db - current
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(trimmed), "-af",
             f"volume={gain:.2f}dB,afade=t=in:d=0.02,afade=t=out:st={max(0.0, seconds - 0.06):.3f}:d=0.06,"
             "alimiter=limit=0.89:level=disabled", "-c:a", "pcm_s16le", str(target)])
    except (FileNotFoundError, subprocess.CalledProcessError, AttributeError) as exc:
        raise VoiceCloneError("FFmpeg não conseguiu nivelar a fala.") from exc
    finally:
        trimmed.unlink(missing_ok=True)
    return {"mean_db_before": current, "gain_db": round(gain, 2), "duration_seconds": seconds}


def narrate(profile_dir: Path, script: Path, output_dir: Path, takes: int = 10,
            max_semitones: float = fidelity.DEFAULT_MAX_SEMITONES, max_timbre: float = fidelity.DEFAULT_MAX_TIMBRE,
            language: str | None = None, only: list[int] | None = None, mean_db: float = -20.0,
            check_words: bool = True) -> dict:
    """Narração de um roteiro: uma fala por linha, cada uma com filtro de fidelidade e volume igualado.

    O roteiro pode ser .txt (uma fala por linha) ou .json ({"lines": [{"text": ..., "speak": ...}]}).
    `speak` (opcional) é a grafia de como se fala, só para a voz; `text` é a grafia certa (legenda).
    Falas curtas (até ~42 caracteres, uma ideia) saem bem mais estáveis do que parágrafos.
    """
    if script.suffix.lower() == ".json":
        lines = [dict(item) for item in read_json(script).get("lines", [])]
    else:
        lines = [{"text": line.strip()} for line in script.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise VoiceCloneError("Roteiro vazio.")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_lines = []
    for number, line in enumerate(lines, 1):
        if only and number not in only:
            continue
        raw = output_dir / f"line-{number:02d}.wav"
        result = synthesize(profile_dir, line["text"], raw, output_dir / f"line-{number:02d}.manifest.json",
                            takes=takes, max_semitones=max_semitones, max_timbre=max_timbre, language=language,
                            speak=line.get("speak"), check_words=check_words)
        leveled = output_dir / f"line-{number:02d}.leveled.wav"
        volume = level(raw, leveled, mean_db)
        report_lines.append({"line": number, "text": line["text"], "spoken_text": result["spoken_text"],
                             "status": result["status"], "fidelity": result["generation"].get("fidelity"),
                             "chosen_take": result["generation"].get("chosen_take"),
                             "words": result["generation"].get("words"),
                             "file": str(leveled), "volume": volume})
    report = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "script": str(script),
              "profile": str(profile_dir), "lines": report_lines,
              "to_review": [item["line"] for item in report_lines if item["status"] != "AGUARDA_QA_HUMANO"],
              "human_qa_required": True}
    write_json(output_dir / "narration-report.json", report)
    return report


def compare(profiles: list[Path], script: Path, output_dir: Path, takes: int = 10, language: str | None = None,
            check_words: bool = True) -> dict:
    """Narra o mesmo roteiro em dois ou mais perfis e junta tudo para ouvir lado a lado.

    Gera `<perfil>.wav` (roteiro inteiro em cada voz), `lado-a-lado.wav` (fala 1 na voz A, fala 1
    na voz B, …) e `comparison-report.json` com a qualidade de cada amostra de referência. Na
    prática, a voz pior quase sempre vem da amostra (volume baixo, pouca voz, sala, tom tenso).
    """
    import subprocess

    from .acquisition import analyze

    if len(profiles) < 2:
        raise VoiceCloneError("Informe pelo menos dois perfis para comparar.")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary, per_line = [], []
    for profile_dir in profiles:
        profile = validate_profile(profile_dir)
        name = profile["profile_id"]
        report = narrate(profile_dir, script, output_dir / name, takes=takes, language=language, check_words=check_words)
        files = [Path(line["file"]) for line in report["lines"]]
        per_line.append(files)
        fidelity_lines = [line["fidelity"] for line in report["lines"] if line.get("fidelity")]
        summary.append({
            "profile": name,
            "sample": analyze(profile_dir / profile["reference"]),
            "mean_f0_hz": round(sum(f["f0_hz"] for f in fidelity_lines) / len(fidelity_lines), 1) if fidelity_lines else None,
            "mean_timbre": round(sum(f["timbre"] for f in fidelity_lines) / len(fidelity_lines), 2) if fidelity_lines else None,
            "to_review": report["to_review"],
            "file": str(output_dir / f"{name}.wav"),
        })
        _join(files, output_dir / f"{name}.wav", subprocess)
    _join([f for group in zip(*per_line) for f in group], output_dir / "lado-a-lado.wav", subprocess)
    result = {"schema_version": 1, "script": str(script), "profiles": summary,
              "side_by_side": str(output_dir / "lado-a-lado.wav"),
              "note": "A máquina mede; quem escolhe a voz é o ouvido. Compare também a amostra: volume, segundos de voz e ruído.",
              "human_qa_required": True}
    write_json(output_dir / "comparison-report.json", result)
    return result


def _join(files: list[Path], target: Path, subprocess) -> None:
    """Junta falas com 0,6 s de silêncio entre elas."""
    if not files:
        return
    inputs, labels = [], []
    for index, path in enumerate(files):
        inputs += ["-i", str(path)]
        labels.append(f"[{index}:a]apad=pad_dur=0.6[a{index}]")
    graph = ";".join(labels) + ";" + "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1"
    try:
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-c:a", "pcm_s16le", str(target)],
                       check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise VoiceCloneError("FFmpeg não conseguiu juntar as falas.") from exc


def verify(audio: Path, expected_text: str | None, manifest: Path | None = None) -> dict:
    technical = probe(audio)
    transcription = None
    text_match = None
    transcription_error = None
    if expected_text:
        try:
            import mlx_whisper
            transcription = str(mlx_whisper.transcribe(str(audio), path_or_hf_repo="mlx-community/whisper-small-mlx")["text"]).strip()
            def normalize(value: str) -> str:
                value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
                return re.sub(r"[^a-z0-9]+", " ", value).strip()
            text_match = round(SequenceMatcher(None, normalize(expected_text), normalize(transcription)).ratio(), 4)
        except (ImportError, OSError, KeyError, TypeError) as exc:
            transcription_error = str(exc)
    result = {
        "schema_version": 1,
        "audio": str(audio),
        "audio_sha256": sha256(audio),
        "technical": technical,
        "expected_text": expected_text,
        "transcription": transcription,
        "transcription_error": transcription_error,
        "text_match": text_match,
        "human_qa_required": True,
        "status": "AGUARDA_QA_HUMANO" if technical["valid"] else "BLOQUEADO_VOZ",
    }
    if manifest:
        prior = read_json(manifest)
        if prior.get("output_sha256") != result["audio_sha256"] or prior.get("fallback_used") is not False:
            result["status"] = "BLOQUEADO_VOZ"
    if text_match is not None and text_match < 0.85:
        result["status"] = "BLOQUEADO_VOZ"
    target = REPORTS_DIR / f"verify-{audio.stem}.json"
    write_json(target, result)
    return result
