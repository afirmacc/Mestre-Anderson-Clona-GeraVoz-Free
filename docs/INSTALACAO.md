# Instalação no macOS Apple Silicon

## Requisitos

- Mac Apple Silicon com macOS;
- 16 GB de memória unificada recomendados;
- 12 GB livres;
- internet para dependências e modelo;
- voz própria ou autorizada por escrito.

## Diagnóstico e instalação

```bash
python3 -m voice_clone.cli doctor
./installers/install-macos.sh
```

O instalador pede autorização antes de instalar Homebrew, Python 3.12, FFmpeg, Git ou baixar aproximadamente 3 GB do modelo. Ele cria um ambiente isolado em `~/.local/share/voice-clone` e nunca altera o Python do macOS.

Ao terminar, carrega o backend e o modelo como smoke test. Para também sintetizar com um perfil já autorizado:

```bash
./installers/install-macos.sh \
  --smoke-profile="$HOME/.local/share/voice-clone/profiles/minha-voz"
```

Para automação previamente autorizada:

```bash
./installers/install-macos.sh --yes
```

Use `--skip-model` somente para validar o bootstrap sem baixar o modelo.

## Idempotência e reparo

Execute o instalador novamente para revalidar. Ferramentas, ambiente, bibliotecas e cache válidos são reutilizados. Para correção seletiva:

```bash
voice-clone status
voice-clone repair
```

Perfis ficam fora do repositório em `~/.local/share/voice-clone/profiles` e não são apagados pelo reparo.

## Instalação pelo wheel

O wheel inclui instalador, skill Hermes, schemas e templates. Depois de instalar o pacote oficial com o extra MLX, a CLI localiza o instalador dentro do ambiente:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install 'ia-skill-clonagem-voz[mlx]'
voice-clone install
```

Enquanto a versão não estiver publicada no PyPI, use o wheel da release do GitHub. O clone continua sendo o caminho principal da release candidate.

## Criar perfil e gerar teste

```bash
voice-clone prepare \
  --input /caminho/amostra.m4a \
  --profile-id minha-voz \
  --consent /caminho/consentimento.txt \
  --transcript "Transcrição exata da amostra"

voice-clone profile validate \
  --profile ~/.local/share/voice-clone/profiles/minha-voz

voice-clone synthesize \
  --profile ~/.local/share/voice-clone/profiles/minha-voz \
  --text "Esta é uma geração local autorizada." \
  --output teste.wav

voice-clone verify \
  --audio teste.wav \
  --text "Esta é uma geração local autorizada." \
  --manifest teste.manifest.json

voice-clone test \
  --profile ~/.local/share/voice-clone/profiles/minha-voz
```

O estado máximo automático é `AGUARDA_QA_HUMANO`. Só uma pessoa autorizada pode aprovar timbre, naturalidade, ritmo e pronúncia.

## Hermes

Copie ou vincule a pasta do projeto para `~/.hermes/skills/local/mestre-anderson-clona-geravoz-free`, abra uma nova sessão ou use `/reset`, e confira com `hermes skills list`. O executor funciona independentemente do carregamento da skill pelo Hermes.
