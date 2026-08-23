# Instalação

## Situação atual

O instalador automático ainda não está liberado. O script macOS existente executa somente diagnóstico e não altera o equipamento.

## Instalação de desenvolvimento

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
voice-clone doctor
```

## Instalação no Hermes

Quando o pacote operacional estiver validado, a pasta da skill será copiada para:

```text
~/.hermes/skills/local/clonar-voz-local/
```

Depois, reinicie a sessão ou use `/reset` e confirme com `hermes skills list`.

## Idempotência

O instalador futuro deverá inventariar antes de agir. Componentes válidos serão reutilizados; itens ausentes serão instalados; itens quebrados serão reparados seletivamente. Perfis serão preservados.

## Mac sem dependências

O bootstrap deverá validar, nesta ordem: Apple Silicon, Command Line Tools, Homebrew, Python 3.12, FFmpeg, Git, ambiente virtual, MLX, MLX-Audio, modelo e Hermes.

Nenhum gerenciador ou pacote de sistema será instalado silenciosamente.

