# Mestre Anderson Clona GeraVoz Free

**Português** · [English](README.en.md) · [Español](README.es.md)

![version](https://img.shields.io/badge/vers%C3%A3o-0.5.0-blue)
![IA local](https://img.shields.io/badge/IA-100%25%20LOCAL-success)
![grátis](https://img.shields.io/badge/custo-0%20R%24-success)
![Agentes](https://img.shields.io/badge/agentes-Claude%20%C2%B7%20Codex%20%C2%B7%20Hermes%20%C2%B7%20Orca%20%C2%B7%20OpenClaw-6f42c1)

**Clone a sua voz e gere narrações com ela usando IA 100% LOCAL, de graça.** O modelo de voz (Qwen3-TTS) e o ouvido automático (Whisper) rodam **no seu próprio computador**: nada de nuvem, nada de chave de API, nada de pagar por caractere, e a sua voz **nunca sai da sua máquina**. Depois de instalado, funciona até sem internet.

Funciona como **skill** para os agentes **Claude Code, Codex, Hermes, Orca e OpenClaw** (e qualquer agente que leia `SKILL.md`), e também como linha de comando.

> Criada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc)
> Nasceu da produção real dos vídeos do app *Combinado em Família*, narrados com a voz do autor. Cada padrão desta skill veio de um erro que aconteceu de verdade.

## O que "IA local" quer dizer aqui

| | Esta skill | Serviços de voz na nuvem |
|---|---|---|
| Onde a voz é processada | No seu Mac (GPU Apple Silicon) | No servidor da empresa |
| Sua gravação sai do computador? | Nunca | Sim, é enviada |
| Custo | Grátis (código MIT, modelo Apache 2.0) | Assinatura ou por caractere |
| Chave de API / conta | Não precisa | Precisa |
| Funciona sem internet | Sim, depois de instalada | Não |

## Use no seu agente

```bash
# Claude Code, Codex, Hermes e OpenClaw de uma vez (instala para o seu usuário)
npx skills add afirmacc/Mestre-Anderson-Clona-GeraVoz-Free -g -a claude-code -a codex -a hermes-agent -a openclaw
```

- **Orca:** o Orca roda Claude Code e Codex por dentro e usa as mesmas skills; instalar para eles já basta.
- **Outro agente:** copie a pasta do repositório para a pasta de skills dele; o que vale é o `SKILL.md`.
- Depois é só pedir: *"crie a minha voz"* ou *"narre este roteiro com a minha voz"*.

## Comece em 3 passos

```bash
# 1. Baixe a skill (Claude Code, Codex, Hermes, Orca, OpenClaw…)
npx skills add afirmacc/Mestre-Anderson-Clona-GeraVoz-Free

# 2. Instale a ferramenta (macOS Apple Silicon). Pede confirmação antes de baixar o modelo (~3 GB).
git clone https://github.com/afirmacc/Mestre-Anderson-Clona-GeraVoz-Free.git && ./Mestre-Anderson-Clona-GeraVoz-Free/installers/install-macos.sh

# (Já tem o modelo Qwen3-TTS 1.7B Base 8bit no computador? Acrescente --model-dir=<pasta> e não baixa de novo.)

# 3. Crie a sua voz: o assistente guia tudo e toca o resultado no final
voice-clone criar-voz
```

O `criar-voz` faz, nesta ordem: consentimento (você digita AUTORIZO) → teste de volume de 5 s ("chegue mais perto" ou "pode gravar") → leitura guiada que cobre os sons do idioma → análise da amostra (regrava até ficar boa) → perfil → frase de teste tocada na hora → você aprova. Depois é só pedir ao seu agente: *"narre este roteiro com a minha voz"*, ou:

```bash
voice-clone narrate --profile ~/.local/share/voice-clone/profiles/<seu-perfil> --script roteiro.txt --output-dir narracao/
```

### Por que a captação importa tanto (caso real)

O modelo imita a amostra inteira: sala, microfone e jeito de falar. Com o mesmo modelo e o mesmo roteiro, uma amostra boa (fala a −13 dB, 26 s de voz, tom natural de narração) deu uma voz "nota mil"; uma amostra com o microfone longe (−35 dB, 11 s de voz, leitura tensa) deu uma voz ruim, mesmo com o volume igualado depois. Por isso a skill testa o volume antes, recusa voz baixa ou curta e pede para ler no seu tom de narrar.

## Passo a passo (cada etapa avulsa)

```bash
# 1. Captação: veja o texto de leitura (cobre os sons do português) e as dicas, grave e confira
voice-clone record --guide
voice-clone record --output minha-voz.wav          # ou grave no celular
voice-clone record --analyze minha-voz.wav         # duração, ruído, estouro: diz o que corrigir

# 2. Perfil (com consentimento assinado)
voice-clone prepare --input minha-voz.wav --profile-id minha-voz --consent consentimento.txt
P=~/.local/share/voice-clone/profiles/minha-voz

# 3. Pronúncia: acha as palavras difíceis do roteiro e aprende como a SUA voz deve falá-las
voice-clone pronounce --profile $P --script roteiro.txt
voice-clone pronounce --profile $P --script roteiro.txt --learn-script --output-dir aprender/

# 4. Narração: escuta cada tomada e fica com a que tem o seu tom e as palavras certas
voice-clone narrate --profile $P --script roteiro.txt --output-dir narracao/

# 5. Ouça as falas de "to_review" (narracao/narration-report.json) e regrave só elas
voice-clone narrate --profile $P --script roteiro.txt --output-dir narracao/ --only 3 7
```

## Falar certo: como a skill cuida da pronúncia

1. **Dicionário base por idioma** (pt, en, es) com as palavras que o modelo mais erra: app, Admin, site, WhatsApp, YouTube, Google, Wi-Fi, login, download, PIX… O dicionário do seu perfil vence o base.
2. **Regras automáticas:** `R$ 19,90` → "dezenove reais e noventa centavos", `30%` → "trinta por cento", `10h30`, `7x`, `2026`, siglas (`CPF` → "cê pê éfe"), sites (`afirma.cc` → "afirma ponto cê cê") e e-mails.
3. **Achar palavras difíceis** no roteiro antes de gravar (`pronounce --script`).
4. **Aprender na sua voz** (`pronounce --learn termo` ou `--learn-script`): a skill fala a palavra em algumas grafias, escuta com o Whisper e guarda no seu dicionário a que foi entendida.
5. **Escuta de cada tomada** na narração: palavra trocada ou engolida faz a skill tentar outra tomada; se nenhuma sair limpa, a fala vai para `to_review` com as palavras suspeitas.
6. **Ver antes de gravar:** `pronounce --text "..."` mostra exatamente o que será falado. Correção manual: `pronounce --add "Admin=Adimin"`.

A legenda continua sempre com a grafia certa.

## Lições da produção (por que o padrão é assim)

| Problema real | Solução na skill |
|---|---|
| Uma fala saiu com **outra voz**, 8 semitons acima | **Filtro de fidelidade:** mede tom (F0) e timbre de cada tomada contra a sua amostra; aceita até 1,2 semitom (o timbre só barra mudança grosseira); tenta até 10 vezes e fica com a melhor |
| Com a transcrição da amostra, o modelo **cortava** a fala ou **balbuciava** 30 s | Não envia a transcrição por padrão |
| Tomadas cortadas ou com repetição | Descarta duração fora de 6–16 caracteres por segundo |
| **Volume pulando** entre as falas | Corta o silêncio das pontas e iguala tudo a −20 dB |
| "Admin" e "app" **pronunciados errado** | Dicionário base, escuta automática e aprendizado da grafia na sua voz |
| Amostra baixa, curta ou lida com voz tensa deu **clone ruim** | Teste de volume, mínimo de 15 s de voz, voz baixa recusada, assistente `criar-voz` |
| Parágrafos longos **derivavam** a voz | Roteiro em falas curtas (até ~42 caracteres) |

## Escrevendo um bom roteiro

- Uma ideia por fala, até umas 7 palavras.
- Rode `voice-clone pronounce --script` antes de narrar.
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

Se esta skill te ajudou, dê uma ⭐ e cite: *Mestre Anderson Clona GeraVoz Free — Mestre Anderson Menezes de Oliveira · afirma.cc*.
