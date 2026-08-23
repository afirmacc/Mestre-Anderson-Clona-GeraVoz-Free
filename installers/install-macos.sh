#!/usr/bin/env bash
set -euo pipefail

REPAIR=0
YES=0
SKIP_MODEL=0
for arg in "$@"; do
  case "$arg" in
    --repair) REPAIR=1 ;;
    --yes) YES=1 ;;
    --skip-model) SKIP_MODEL=1 ;;
    *) echo "Argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "BLOQUEADO_VOZ: esta versão suporta somente macOS Apple Silicon." >&2
  exit 3
fi

APP_DIR="${VOICE_CLONE_HOME:-$HOME/.local/share/voice-clone}"
VENV="$APP_DIR/runtime/qwen3-mlx-py312"
MODEL_CACHE="$APP_DIR/model-cache"
STATE="$APP_DIR/installation-state.json"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_SKILLS_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills/local}"
HERMES_TARGET="$HERMES_SKILLS_DIR/clonar-voz-local"

confirm() {
  if [[ "$YES" -eq 1 ]]; then return 0; fi
  printf '%s [s/N] ' "$1"
  read -r answer
  [[ "$answer" == "s" || "$answer" == "S" ]]
}

ensure_brew() {
  if command -v brew >/dev/null 2>&1; then return 0; fi
  echo "Homebrew ausente. A instalação exige o instalador oficial e altera o sistema."
  confirm "Autoriza instalar o Homebrew agora?" || exit 4
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
}

ensure_formula() {
  local formula="$1" command_name="$2"
  if command -v "$command_name" >/dev/null 2>&1; then
    echo "REUTILIZADO: $formula"
  else
    confirm "Autoriza instalar $formula pelo Homebrew?" || exit 4
    brew install "$formula"
  fi
}

mkdir -p "$APP_DIR/runtime" "$MODEL_CACHE" "$APP_DIR/reports" "$APP_DIR/profiles"
chmod 700 "$APP_DIR" "$APP_DIR/profiles"
ensure_brew
ensure_formula python@3.12 python3.12
ensure_formula ffmpeg ffmpeg
ensure_formula git git

if [[ ! -x "$VENV/bin/python" ]]; then
  python3.12 -m venv "$VENV"
  echo "CRIADO: ambiente Python"
else
  echo "REUTILIZADO: ambiente Python"
fi

if "$VENV/bin/python" - <<'PY' >/dev/null 2>&1
import importlib.metadata as m
assert m.version("mlx") == "0.32.0"
assert m.version("mlx-audio") == "0.4.7"
assert m.version("mlx-whisper")
PY
then
  echo "REUTILIZADO: MLX 0.32.0 e MLX-Audio 0.4.7"
else
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install "mlx==0.32.0" "mlx-audio==0.4.7" "numpy>=1.26,<3" "mlx-whisper>=0.4,<1"
fi

"$VENV/bin/python" -m pip install --no-deps --upgrade "$PROJECT_DIR"

if [[ "$SKIP_MODEL" -eq 0 ]]; then
  if [[ -d "$MODEL_CACHE/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit" ]]; then
    echo "REUTILIZADO: cache do modelo"
  else
    confirm "Autoriza baixar aproximadamente 3 GB do modelo oficial?" || exit 4
    HF_HOME="$MODEL_CACHE" "$VENV/bin/python" - <<'PY'
from mlx_audio.tts.utils import load_model
load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit")
PY
  fi
fi

VOICE_CLONE_HOME="$APP_DIR" "$VENV/bin/python" - <<PY
from datetime import datetime, timezone
from pathlib import Path
from voice_clone.common import write_json
write_json(Path("$STATE"), {
  "schema_version": 1,
  "installed_at": datetime.now(timezone.utc).isoformat(),
  "platform": "macOS-arm64",
  "backend": "qwen3-mlx",
  "repair": bool($REPAIR),
  "model_requested": not bool($SKIP_MODEL),
})
PY

mkdir -p "$HERMES_SKILLS_DIR"
if [[ -L "$HERMES_TARGET" && "$(readlink "$HERMES_TARGET")" == "$PROJECT_DIR" ]]; then
  echo "REUTILIZADO: integração Hermes"
elif [[ -e "$HERMES_TARGET" || -L "$HERMES_TARGET" ]]; then
  echo "ATENÇÃO: já existe uma skill Hermes em $HERMES_TARGET; ela foi preservada."
  echo "Revise-a manualmente antes de substituir ou remover."
else
  ln -s "$PROJECT_DIR" "$HERMES_TARGET"
  echo "CRIADO: vínculo da skill no Hermes"
fi

echo "Instalação/revalidação concluída."
echo "Execute: $VENV/bin/voice-clone status"
