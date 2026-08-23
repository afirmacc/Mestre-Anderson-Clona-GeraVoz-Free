from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Diagnostic:
    system: str
    release: str
    architecture: str
    python: str
    memory_gb: float | None
    disk_free_gb: float
    commands: dict[str, str | None]
    hermes_skill_dir: str
    skill_installed: bool
    recommended_backend: str
    compatibility: str
    missing: list[str]


def _memory_gb() -> float | None:
    if platform.system() == "Darwin":
        try:
            value = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return round(int(value.strip()) / (1024**3), 2)
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
    return None


def diagnose() -> Diagnostic:
    system = platform.system()
    architecture = platform.machine()
    commands = {name: shutil.which(name) for name in ("python3", "ffmpeg", "git", "brew", "hermes", "nvidia-smi")}
    missing = [name for name in ("python3", "ffmpeg", "git") if not commands[name]]
    skill_dir = Path(os.environ.get("HERMES_SKILLS_DIR", Path.home() / ".hermes/skills/local")) / "clonar-voz-local"

    if system == "Darwin" and architecture == "arm64":
        backend, compatibility = "qwen3-mlx", "planejado"
    elif system == "Linux" and commands["nvidia-smi"]:
        backend, compatibility = "qwen3-cuda", "planejado"
    elif system == "Windows":
        backend, compatibility = "wsl2-cuda", "experimental"
    else:
        backend, compatibility = "cpu", "experimental"

    return Diagnostic(
        system=system,
        release=platform.release(),
        architecture=architecture,
        python=platform.python_version(),
        memory_gb=_memory_gb(),
        disk_free_gb=round(shutil.disk_usage(Path.home()).free / (1024**3), 2),
        commands=commands,
        hermes_skill_dir=str(skill_dir),
        skill_installed=(skill_dir / "SKILL.md").is_file(),
        recommended_backend=backend,
        compatibility=compatibility,
        missing=missing,
    )


def render_text(result: Diagnostic) -> str:
    lines = [
        f"Sistema: {result.system} {result.release} ({result.architecture})",
        f"Python: {result.python}",
        f"Memória: {result.memory_gb if result.memory_gb is not None else 'não detectada'} GB",
        f"Disco livre: {result.disk_free_gb} GB",
        f"Skill Hermes instalada: {'sim' if result.skill_installed else 'não'}",
        f"Backend recomendado: {result.recommended_backend} ({result.compatibility})",
    ]
    lines.append("Ausências: " + (", ".join(result.missing) if result.missing else "nenhuma dependência básica"))
    return "\n".join(lines)


def render_json(result: Diagnostic) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)

