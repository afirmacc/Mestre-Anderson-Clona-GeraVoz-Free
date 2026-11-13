# IA Skill — Clonagem de Voz Local

**Português** · [English](README.en.md) · [Español](README.es.md)

![versão](https://img.shields.io/badge/vers%C3%A3o-0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Claude%20%C2%B7%20Codex%20%C2%B7%20Hermes-6f42c1)
![local](https://img.shields.io/badge/processamento-100%25%20local-success)

Clone a **sua própria voz** no seu computador e narre roteiros inteiros com ela — sem ElevenLabs, sem pagar por caractere e sem enviar sua voz para nenhum serviço. Funciona como **skill para agentes de IA** (Claude Code, Codex, Hermes e outros) e como linha de comando.

> Criada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc)
> Nasceu da produção real dos vídeos do app *Combinado em Família*, narrados com a voz do autor. Cada padrão desta skill veio de um erro que aconteceu de verdade.

## Instalar como skill

```bash
npx skills add afirmacc/ia-skill-clonagem-voz
```

Instala para Claude Code, Codex, Hermes e outros agentes compatíveis com `SKILL.md`. Depois é só pedir ao agente: *"narre este roteiro com a minha voz"*.

## Instalar a ferramenta (macOS Apple Silicon)

```bash
git clone https://github.com/afirmacc/ia-skill-clonagem-voz.git
cd ia-skill-clonagem-voz
./installers/install-macos.sh
```

O instalador é idempotente: pede confirmação antes de instalar ferramentas ou baixar o modelo (Qwen3-TTS 1.7B, 8 bits, ~2 GB) e, na segunda execução, só revalida.

## Uso em 4 passos

```bash
# 1. Perfil: 15 a 40 s de fala natural, limpa, um falante só, com consentimento assinado
voice-clone prepare --input minha-voz.m4a --profile-id minha-voz \
  --consent consentimento.txt --language Portuguese

# 2. Uma fala (até 10 tomadas; grava a mais fiel ao seu tom e timbre)
voice-clone synthesize --profile ~/.local/share/voice-clone/profiles/minha-voz \
  --text "Olá! Esta é a minha voz." --output ola.wav

# 3. Um roteiro inteiro (uma fala por linha), já com volume igual entre as falas
voice-clone narrate --profile ~/.local/share/voice-clone/profiles/minha-voz \
  --script templates/roteiro-exemplo.txt --output-dir narracao/

# 4. Ouça as falas listadas em "to_review" no narracao/narration-report.json e regrave só elas
voice-clone narrate ... --only 3 7
```

## O que a 0.2.0 traz (lições da produção)

| Problema real | Solução na skill |
|---|---|
| Uma fala saiu com **outra voz**, 8 semitons acima | **Filtro de fidelidade:** mede tom (F0) e timbre de cada tomada contra a sua amostra; aceita até 1,2 semitom e timbre 4,3; tenta até 10 vezes e fica com a melhor |
| Com a transcrição da amostra, o modelo **cortava** a fala ou **balbuciava** 30 s | Não envia a transcrição por padrão |
| Tomadas cortadas ou com repetição | Descarta duração fora de 6–16 caracteres por segundo |
| **Volume pulando** entre as falas | Corta o silêncio das pontas e iguala tudo a −20 dB |
| "Admin" e "app" **pronunciados errado** | **Dicionário de pronúncia** (`"Admin": "Adimin"`, `"app": "ápi"`) só no áudio; a legenda continua certa |
| Parágrafos longos **derivavam** a voz | Roteiro em falas curtas (até ~42 caracteres) |

## Escrevendo um bom roteiro

- Uma ideia por fala, até umas 7 palavras.
- `.txt`: uma fala por linha. `.json`: `{"lines": [{"text": "Acesse afirma.cc", "speak": "Acesse afirma ponto cê cê."}]}` — `text` vai para a legenda, `speak` é como falar.
- Siglas, nomes estrangeiros e endereços: escreva como se fala.
- Exemplos em [`templates/`](templates/).

## Idiomas

Português, inglês, espanhol, francês, alemão, italiano, japonês, coreano, chinês e russo (Qwen3-TTS). Use `--language` no perfil ou em cada fala.

## Compatibilidade

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS + MLX | Usado em produção (0.2.0) |
| Linux + NVIDIA | Qwen3/PyTorch + CUDA | Planejado |
| Windows + WSL2 + NVIDIA | Backend Linux/CUDA | Planejado |
| Mac Intel / só CPU | — | Não validado |

Rode a geração num terminal comum do Mac: ela usa a GPU (Metal).

## Princípios

- **Local por padrão:** modelo e processamento no seu computador.
- **Consentimento obrigatório:** só a sua voz ou uma voz autorizada por escrito ([pt](templates/consentimento.txt) · [en](templates/consent.en.txt) · [es](templates/consentimiento.es.txt)).
- **Sem fallback silencioso:** se o perfil ou a engine falhar, para e avisa (`BLOQUEADO_VOZ`).
- **Aprovação humana:** a máquina mede integridade e fidelidade; quem aprova a voz é uma pessoa.
- **Privacidade:** amostras, perfis e áudios nunca vão para o Git (o `.gitignore` bloqueia).

## Uso responsável

Não use para clonar alguém sem autorização, fraude, se passar por outra pessoa, burlar autenticação por voz ou fabricar declarações de terceiros. Na dúvida sobre autorização ou identidade, o estado correto é `BLOQUEADO_VOZ`.

## Documentação

[Instalação](docs/INSTALACAO.md) · [Arquitetura](docs/ARQUITETURA.md) · [Compatibilidade](docs/COMPATIBILIDADE.md) · [Testes](docs/TESTES.md) · [Privacidade](docs/PRIVACIDADE.md) · [Plano operacional](docs/PLANO.md) · [Releases](docs/RELEASES.md) · [Roadmap](ROADMAP.md) · [Mudanças](CHANGELOG.md)

## Contribuir

Bem-vindas: novos backends locais (Linux/NVIDIA, Windows), outros idiomas na documentação, testes, acessibilidade, segurança e prevenção de abuso. Nunca envie amostras reais de voz, modelos, caches ou dados pessoais. Leia [CONTRIBUTING.md](CONTRIBUTING.md) e o [Código de Conduta](CODE_OF_CONDUCT.md). Contato: [app@afirma.cc](mailto:app@afirma.cc).

## Licença

MIT — veja [LICENSE](LICENSE). A licença do código não dá direito de usar a voz de ninguém nem substitui o consentimento. O modelo Qwen3-TTS é Apache 2.0.

## Créditos

Idealizada e criada por **Mestre Anderson Menezes de Oliveira**, da [Afirma](https://afirma.cc), para devolver à comunidade o conhecimento recebido de amigos, colaboradores e de quem compartilha tecnologia com generosidade. Com o apoio de Bellete Ritter de Oliveira.

Se esta skill te ajudou, dê uma ⭐ e cite: *Clonagem de Voz Local — Mestre Anderson Menezes de Oliveira · afirma.cc*.
