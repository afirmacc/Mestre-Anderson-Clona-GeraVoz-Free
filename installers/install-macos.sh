#!/usr/bin/env bash
set -euo pipefail

echo "Pré-lançamento: este instalador ainda opera somente em modo de diagnóstico."
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "BLOQUEADO: este instalador é exclusivo para macOS." >&2
  exit 2
fi

python3 -m voice_clone.cli doctor
echo "Nenhuma alteração foi feita. A instalação automática será liberada após os testes da versão 2."

