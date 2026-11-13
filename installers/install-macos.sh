#!/usr/bin/env bash
set -euo pipefail

REPAIR=0
YES=0
SKIP_MODEL=0
SMOKE_PROFILE=""
MODEL_DIR=""
for arg in "$@"; do
  case "$arg" in
    --repair) REPAIR=1 ;;
    --yes) YES=1 ;;
    --skip-model) SKIP_MODEL=1 ;;
    --help|-h) echo "Uso: install-macos.sh [--yes] [--repair] [--skip-model] [--model-dir=PASTA] [--smoke-profile=PERFIL]"; exit 0 ;;
    --smoke-profile=*) SMOKE_PROFILE="${arg#*=}" ;;
    --model-dir=*) MODEL_DIR="${arg#*=}" ;;
    *) echo "Argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "BLOQUEADO_VOZ: esta versão suporta somente macOS Apple Silicon." >&2
  exit 3
fi

APP_DIR="${VOICE_CLONE_HOME:-$HOME/.local/share/voice-clone}"
DEFAULT_VENV="$APP_DIR/runtime/qwen3-mlx-py312"
VENV="$DEFAULT_VENV"
MODEL_CACHE="$APP_DIR/model-cache"
STATE="$APP_DIR/installation-state.json"
SCRIPT_DIR="$(cd -P "$(dirname "$0")" && pwd)"
if [[ -f "$SCRIPT_DIR/../pyproject.toml" ]]; then
  PROJECT_DIR="$(cd -P "$SCRIPT_DIR/.." && pwd)"
  SKILL_SOURCE="$PROJECT_DIR/SKILL.md"
else
  PROJECT_DIR=""
  SKILL_SOURCE="$SCRIPT_DIR/SKILL.md"
  if [[ -n "${VOICE_CLONE_INVOKING_PYTHON:-}" && -x "$VOICE_CLONE_INVOKING_PYTHON" ]]; then
    VENV="$(cd -P "$(dirname "$VOICE_CLONE_INVOKING_PYTHON")/.." && pwd)"
  fi
fi
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
  echo "REUTILIZADO: MLX 0.32.0, MLX-Audio 0.4.7 e MLX-Whisper"
else
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install "mlx==0.32.0" "mlx-audio==0.4.7" "numpy>=1.26,<3" "mlx-whisper>=0.4,<1"
fi

WANTED_VERSION=""
if [[ -n "$PROJECT_DIR" ]]; then
  WANTED_VERSION="$(sed -n 's/^version = "\(.*\)"/\1/p' "$PROJECT_DIR/pyproject.toml" | head -1)"
fi
INSTALLED_VERSION="$("$VENV/bin/python" -c 'import importlib.metadata as m; print(m.version("ia-skill-clonagem-voz"))' 2>/dev/null || true)"
if [[ -n "$INSTALLED_VERSION" && ( -z "$WANTED_VERSION" || "$INSTALLED_VERSION" == "$WANTED_VERSION" ) ]]; then
  echo "REUTILIZADO: pacote ia-skill-clonagem-voz $INSTALLED_VERSION"
elif [[ -n "$PROJECT_DIR" ]]; then
  "$VENV/bin/python" -m pip install --upgrade "$PROJECT_DIR"
  echo "ATUALIZADO: pacote ia-skill-clonagem-voz $WANTED_VERSION"
else
  echo "BLOQUEADO_VOZ: pacote instalado não corresponde ao instalador e não há fonte para reparo." >&2
  exit 3
fi

# Modelo completo = pesos presentes e nenhum download pela metade (pasta existir não basta).
model_ready() {
  local dir="$1"
  compgen -G "$dir/snapshots/*/*.safetensors" >/dev/null && ! compgen -G "$dir/blobs/*.incomplete" >/dev/null
}
download_model() {
  # snapshot_download retoma de onde parou. HTTP comum: o download "xet" travou em teste real.
  HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}" HF_HOME="$MODEL_CACHE" "$VENV/bin/python" -c \
    "from huggingface_hub import snapshot_download; snapshot_download('$1')"
}

QWEN_CACHE="$MODEL_CACHE/hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit"
if [[ -n "$MODEL_DIR" ]]; then
  MODEL_DIR="$(cd -P "$MODEL_DIR" 2>/dev/null && pwd || true)"
  if [[ -n "$MODEL_DIR" && -f "$MODEL_DIR/config.json" ]] && compgen -G "$MODEL_DIR/*.safetensors" >/dev/null; then
    printf '%s\n' "$MODEL_DIR" > "$APP_DIR/model-dir"
    echo "REUTILIZADO: modelo já existente em $MODEL_DIR (sem download)"
  else
    echo "BLOQUEADO_VOZ: --model-dir não tem config.json e *.safetensors do Qwen3-TTS." >&2
    exit 3
  fi
fi
LOCAL_MODEL=""
if [[ -f "$APP_DIR/model-dir" ]]; then
  LOCAL_MODEL="$(cat "$APP_DIR/model-dir")"
  if [[ ! -f "$LOCAL_MODEL/config.json" ]] || ! compgen -G "$LOCAL_MODEL/*.safetensors" >/dev/null; then
    echo "ATENÇÃO: o modelo indicado antes ($LOCAL_MODEL) sumiu; volto a usar o download."
    rm -f "$APP_DIR/model-dir"; LOCAL_MODEL=""
  fi
fi
if [[ "$SKIP_MODEL" -eq 0 && -z "$LOCAL_MODEL" ]]; then
  if model_ready "$QWEN_CACHE"; then
    echo "REUTILIZADO: cache do modelo"
  else
    confirm "Autoriza baixar aproximadamente 3 GB do modelo oficial (retoma se já começou)?" || exit 4
    download_model "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
    model_ready "$QWEN_CACHE" || { echo "BLOQUEADO_VOZ: download do modelo incompleto. Rode o instalador de novo." >&2; exit 3; }
  fi
fi

WHISPER_CACHE="$MODEL_CACHE/hub/models--mlx-community--whisper-small-mlx"
SHARED_WHISPER="$HOME/.cache/huggingface/hub/models--mlx-community--whisper-small-mlx"
if [[ ! -e "$WHISPER_CACHE" && -d "$SHARED_WHISPER" ]] && compgen -G "$SHARED_WHISPER/snapshots/*/weights.*" >/dev/null; then
  mkdir -p "$MODEL_CACHE/hub"
  ln -s "$SHARED_WHISPER" "$WHISPER_CACHE"
  echo "REUTILIZADO: Whisper small que já estava no computador (~/.cache/huggingface)"
fi
if [[ "$SKIP_MODEL" -eq 0 ]]; then
  if compgen -G "$WHISPER_CACHE/snapshots/*/weights.*" >/dev/null && ! compgen -G "$WHISPER_CACHE/blobs/*.incomplete" >/dev/null; then
    echo "REUTILIZADO: ouvido automático (Whisper small)"
  elif confirm "Autoriza baixar o ouvido automático (Whisper small, ~500 MB) que confere a pronúncia?"; then
    download_model "mlx-community/whisper-small-mlx"
  else
    echo "IGNORADO: sem o Whisper a skill não confere a pronúncia de cada tomada."
  fi
fi

# Comando voice-clone no terminal (atalho em ~/.local/bin que já aponta para o modelo local).
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/voice-clone" <<WRAP
#!/bin/bash
export HF_HOME="\${HF_HOME:-$MODEL_CACHE}"
export VOICE_CLONE_HOME="\${VOICE_CLONE_HOME:-$APP_DIR}"
exec "$VENV/bin/voice-clone" "\$@"
WRAP
chmod +x "$BIN_DIR/voice-clone"
echo "PRONTO: comando $BIN_DIR/voice-clone"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    if confirm "Adicionar $BIN_DIR ao PATH no ~/.zprofile (para o comando voice-clone funcionar em qualquer terminal)?"; then
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zprofile"
      echo "ATUALIZADO: ~/.zprofile (abra um terminal novo)"
    else
      echo "Use o caminho completo: $BIN_DIR/voice-clone"
    fi
    ;;
esac

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
if [[ -n "$PROJECT_DIR" && -L "$HERMES_TARGET" && "$(cd -P "$HERMES_TARGET" && pwd)" == "$PROJECT_DIR" ]]; then
  echo "REUTILIZADO: integração Hermes"
elif [[ -e "$HERMES_TARGET" || -L "$HERMES_TARGET" ]]; then
  if [[ -f "$HERMES_TARGET/.voice-clone-managed" && -f "$SKILL_SOURCE" ]]; then
    cp "$SKILL_SOURCE" "$HERMES_TARGET/SKILL.md"
    echo "ATUALIZADO: integração Hermes gerenciada"
  else
    echo "ATENÇÃO: já existe uma skill Hermes em $HERMES_TARGET; ela foi preservada."
    echo "Revise-a manualmente antes de substituir ou remover."
  fi
elif [[ -n "$PROJECT_DIR" ]]; then
  ln -s "$PROJECT_DIR" "$HERMES_TARGET"
  echo "CRIADO: vínculo da skill no Hermes"
elif [[ -f "$SKILL_SOURCE" ]]; then
  mkdir -p "$HERMES_TARGET"
  cp "$SKILL_SOURCE" "$HERMES_TARGET/SKILL.md"
  touch "$HERMES_TARGET/.voice-clone-managed"
  echo "CRIADO: skill empacotada no Hermes"
else
  echo "BLOQUEADO_VOZ: recurso SKILL.md ausente no pacote." >&2
  exit 3
fi

if [[ "$SKIP_MODEL" -eq 0 ]]; then
  echo "Executando smoke test técnico..."
  HF_HOME="$MODEL_CACHE" VOICE_CLONE_HOME="$APP_DIR" "$VENV/bin/python" - <<'PY'
from mlx_audio.tts.utils import load_model
from voice_clone.common import DEFAULT_MODEL, local_model_dir
local = local_model_dir()
load_model(str(local) if local else DEFAULT_MODEL)
print("SMOKE OK: backend e modelo carregados")
PY

else
  echo "SMOKE IGNORADO: modelo omitido por --skip-model"
fi

if [[ -n "$SMOKE_PROFILE" ]]; then
  if [[ "$SKIP_MODEL" -eq 1 ]]; then
    echo "BLOQUEADO_VOZ: --smoke-profile não pode ser usado com --skip-model." >&2
    exit 3
  fi
  SMOKE_OUT="$APP_DIR/reports/install-smoke.wav"
  HF_HOME="$MODEL_CACHE" VOICE_CLONE_HOME="$APP_DIR" "$VENV/bin/voice-clone" synthesize \
    --profile "$SMOKE_PROFILE" \
    --text "Este é um teste local autorizado após a instalação." \
    --output "$SMOKE_OUT"
  HF_HOME="$MODEL_CACHE" VOICE_CLONE_HOME="$APP_DIR" "$VENV/bin/voice-clone" verify \
    --audio "$SMOKE_OUT" \
    --text "Este é um teste local autorizado após a instalação." \
    --manifest "$APP_DIR/reports/install-smoke.manifest.json"
fi

HF_HOME="$MODEL_CACHE" VOICE_CLONE_HOME="$APP_DIR" "$VENV/bin/voice-clone" status
echo "Instalação/revalidação concluída."
echo ""
echo "Próximo passo: crie a sua voz (num terminal comum, com o microfone liberado):"
echo "  voice-clone criar-voz"
