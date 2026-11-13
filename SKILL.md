---
name: mestre-anderson-clona-geravoz-free
description: "Mestre Anderson Clona GeraVoz Free: clona uma voz autorizada e gera narração com IA 100% LOCAL e grátis, no próprio computador (Qwen3-TTS + MLX, Apple Silicon; nada vai para a nuvem, sem chave de API). Narra roteiros, falando certo: captação guiada da amostra, dicionário de pronúncia por idioma, números/siglas/sites por extenso, escuta automática de cada tomada (Whisper) e aprendizado da grafia certa de palavras difíceis na sua voz. Filtro de tom, volume igual, sem fallback, consentimento obrigatório. Use quando pedirem narração com a própria voz, voz clonada local, locução de vídeo sem ElevenLabs, ou clone de voz em português, inglês ou espanhol. Local voice cloning and script narration with your own consented voice."
version: 0.5.2
author: "Mestre Anderson Menezes de Oliveira · Afirma (https://afirma.cc)"
license: MIT
---

# Mestre Anderson Clona GeraVoz Free

IA 100% local: o modelo de voz e o Whisper rodam no computador da pessoa; nenhum áudio vai para a nuvem e não há chave de API. Serve para Claude Code, Codex, Hermes, Orca, OpenClaw e qualquer agente que leia `SKILL.md`.

Criada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc). Nasceu da produção real de vídeos narrados com a voz do autor; cada regra abaixo veio de um erro que aconteceu de verdade.

## Regras obrigatórias

- Só a própria voz ou uma voz **autorizada por escrito** (`templates/consentimento.txt`, `consent.en.txt`, `consentimiento.es.txt`). Sem consentimento: `BLOQUEADO_VOZ`.
- Amostras, perfis e áudios gerados ficam **fora do repositório**.
- Nunca usar fallback nem trocar a engine em silêncio. Se falhar, parar e dizer.
- A automação mede voz e pronúncia; **a aprovação final é humana**.
- Áudio sintético não pode ser usado para enganar (fraude, se passar por alguém, burlar autenticação por voz).

## IAs locais recomendadas

- Voz: **Qwen3-TTS 12Hz 1.7B Base 8bit (MLX)**, ~2,9 GB, padrão e usado em produção.
- Ouvido: **Whisper small MLX**, ~0,9 GB, padrão; o large-v3-turbo é opcional (`VOICE_CLONE_LISTEN_MODEL`), não testado.
- Mac Apple Silicon (testado no M2 Pro), ~6 GB de disco, 16 GB de memória recomendados.
- O agente só conduz o trabalho; o áudio nunca sai do computador.

## Primeiro uso (baixou a skill, quer a voz funcionando)

1. `command -v voice-clone`. Se não existir, rode o instalador que vem com a skill: `bash <pasta da skill>/installers/install-macos.sh` (pede confirmação antes de instalar algo ou baixar o modelo; segunda execução só revalida; cria o comando `voice-clone`). Se o computador já tem o Qwen3-TTS 1.7B Base 8bit baixado, use `--model-dir=<pasta>` e não baixa de novo.
2. Peça à pessoa para rodar **no terminal dela** (precisa do microfone e de respostas): `voice-clone criar-voz`. O assistente faz tudo: consentimento (a pessoa digita AUTORIZO), teste de volume de 5 s, leitura guiada, análise com regravação até ficar boa, perfil, frase de teste tocada na hora e aprovação. Nunca grave nem aprove no lugar da pessoa.
3. Já tem uma gravação boa? `voice-clone criar-voz --input gravacao.wav` (aceita .opus/.m4a/.mp3). Teste real: o melhor perfil saiu de um **áudio de WhatsApp** de ~30 s, celular perto da boca, lugar quieto. Para narrar, peça fala calma e mais grave que numa conversa (o clone copia o tom).
4. Pronto: `voice-clone narrate --profile ~/.local/share/voice-clone/profiles/<perfil> --script roteiro.txt --output-dir narracao/`.

## Fluxo detalhado (cada etapa avulsa)

Perfil padrão: `~/.local/share/voice-clone/profiles/<perfil>` (abaixo, `$P`).

1. **Equipamento:** `voice-clone doctor --json`; `voice-clone status`.
2. **Captação:** `voice-clone record --guide` (texto e dicas), `voice-clone record --output minha-voz.wav` (teste de volume + gravação), `voice-clone record --analyze minha-voz.wav`.
3. **Perfil:** `voice-clone prepare --input minha-voz.wav --profile-id minha-voz --consent consentimento.txt --language Portuguese`.
4. **Pronúncia antes de gravar:** `pronounce --script roteiro.txt` (palavras difíceis), `--learn-script --output-dir aprender/` (aprende na voz), `--text "..."` (prévia), `--add "Admin=Adimin"` (manual).
5. **Narrar:** `voice-clone narrate --profile $P --script roteiro.txt --output-dir narracao/`.
6. **Conferir:** ouça as falas em `to_review` e regrave só elas com `--only 3 7`. Aprovação humana antes de publicar.
7. **Comparar vozes:** `voice-clone compare --profiles $P1 $P2 --script roteiro.txt --output-dir comparacao/` → `lado-a-lado.wav` e a qualidade de cada amostra.

## Por que uma voz sai pior que outra (caso real)

O modelo não "aprende" a pessoa: ele imita a amostra inteira, com sala, microfone e jeito de falar. Mesmo modelo, mesma skill, mesmo roteiro:

| | Perfil aprovado | Perfil reprovado |
|---|---|---|
| Nível da fala | −13 dB | −35 dB (microfone longe) |
| Voz acima do fundo | 58 dB | 22 dB |
| Voz útil | 26 s | 11 s |
| Tom | ~120 Hz (narração natural) | ~145 Hz (leitura tensa de "teste") |

Por isso a skill faz o teste de volume antes, recusa voz baixa e menos de 15 s de voz, e pede leitura no tom de narrar. Igualar o volume depois **não** recupera uma amostra ruim.

## Como o texto vira fala

1. Dicionário: base do idioma (`voice_clone/dicionarios/pt.json`, `en.json`, `es.json`, com app, Admin, WhatsApp, YouTube, Wi-Fi…) < dicionário do perfil < `--pronunciation` extra. Chave = grafia certa; valor = como falar.
2. Regras automáticas: `R$ 19,90` → "dezenove reais e noventa centavos"; `30%` → "trinta por cento"; `10h30` → "dez horas e trinta"; `7x` → "sete vezes"; `2026` → "dois mil e vinte e seis"; `CPF` → "cê pê éfe"; `afirma.cc` → "afirma ponto cê cê"; e-mail com "arroba".
3. No roteiro `.json`, `speak` substitui tudo isso naquela fala: `{"text": "Acesse afirma.cc", "speak": "Acesse afirma ponto cê cê."}`.

A legenda sempre usa o `text` (grafia certa).

## Escuta automática (cada tomada)

Com o `mlx-whisper` instalado, cada tomada com tom certo é transcrita e comparada com o texto. Palavra trocada, engolida ou ouvida com baixa confiança vira suspeita; a skill tenta outra tomada e, se nenhuma sair limpa, marca `CONFERIR_PRONUNCIA`. Desligar: `--no-check-words`. O Whisper às vezes "corrige" o que ouve, por isso o ouvido humano continua obrigatório.

## Como escrever o roteiro

- **Falas curtas:** uma ideia por fala, até ~42 caracteres. Parágrafo longo faz o modelo derivar a voz ou balbuciar.
- Uma fala por linha no `.txt`.
- Rode o `pronounce --script` antes de narrar.

## Lições da produção (por que o padrão é assim)

| Problema que aconteceu | O que a skill faz |
|---|---|
| Com a transcrição da referência, o modelo cortava a fala (0,2 s) ou balbuciava 30 s | Não envia `ref_text` por padrão |
| Uma fala saiu com outra voz, 8 semitons acima | Mede o tom de cada tomada (até 1,2 semitom) e o timbre (só mudança grosseira, até 6,0); até 10 tomadas |
| Tomadas cortadas ou repetidas | Descarta duração fora de 6–16 caracteres por segundo |
| Volume pulando entre falas | Iguala cada fala a −20 dB de média, com limitador |
| "Admin" e "app" lidos errado | Dicionário base + do perfil, escuta automática e aprendizado (`--learn`) |
| Amostra baixa/curta/tensa deu clone ruim | Teste de volume, mínimo de 15 s de voz, voz baixa recusada, dica de tom; assistente `criar-voz` |

## Onde rodar

A geração usa a GPU (Metal). Rode `narrate`, `synthesize` e `pronounce --learn` num **terminal comum do Mac**; em sandbox de agente o MLX pode não enxergar a GPU. Se travar, pare e informe; não troque de engine.

## Idiomas

Português, inglês e espanhol têm texto de leitura, dicionário base, números por extenso e documentação (`README.md`, `README.en.md`, `README.es.md`). O Qwen3-TTS também fala francês, alemão, italiano, japonês, coreano, chinês e russo (sem dicionário base ainda).

Contrato completo de instalação, testes e recuperação: `docs/PLANO.md`.
