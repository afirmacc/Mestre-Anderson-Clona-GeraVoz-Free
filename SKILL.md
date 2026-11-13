---
name: clonar-voz-local
description: "Clona uma voz autorizada no próprio computador (Qwen3-TTS + MLX, Apple Silicon) e narra roteiros com a voz clonada: filtro de fidelidade de tom e timbre, dicionário de pronúncia, volume igual entre falas, sem fallback e com consentimento obrigatório. Use quando pedirem narração com a própria voz, voz clonada local, locução de vídeo sem ElevenLabs, ou clone de voz em português, inglês, espanhol e outros idiomas. Local voice cloning and script narration with your own consented voice."
version: 0.2.0
author: "Mestre Anderson Menezes de Oliveira · Afirma (https://afirma.cc)"
license: MIT
---

# Clonar voz local

Criada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc). Nasceu da produção real de vídeos narrados com a voz do autor; cada regra abaixo veio de um erro que aconteceu de verdade.

## Regras obrigatórias

- Só a própria voz ou uma voz **autorizada por escrito** (`templates/consentimento.txt`, `consent.en.txt`, `consentimiento.es.txt`). Sem consentimento: `BLOQUEADO_VOZ`.
- Amostras, perfis e áudios gerados ficam **fora do repositório** (o `.gitignore` já bloqueia `*.wav`, `voice-profiles/`, `consent.txt`).
- Nunca usar fallback nem trocar a engine em silêncio. Se falhar, parar e dizer.
- A automação mede integridade e fidelidade; **a aprovação da voz é humana**.
- Áudio sintético não pode ser usado para enganar (fraude, se passar por alguém, burlar autenticação por voz).

## Fluxo

1. `voice-clone doctor --json` → confira macOS Apple Silicon, memória, disco, FFmpeg. Se já estiver instalado, `voice-clone status`; não reinstale.
2. `voice-clone install` (idempotente; pede confirmação antes de baixar o modelo).
3. Perfil: 15 a 40 s de fala natural, limpa, um falante só (menos de 8 s é recusado).
   `voice-clone prepare --input amostra.m4a --profile-id minha-voz --consent consentimento.txt --language Portuguese`
4. Pronúncia: edite `pronunciation.json` na pasta do perfil (padrão `~/.local/share/voice-clone/profiles/<perfil>/`) (exemplo em `templates/pronunciation.example.json`). A chave é a grafia certa (legenda), o valor é como falar: `"Admin": "Adimin"`, `"app": "ápi"`.
5. Uma fala: `voice-clone synthesize --profile ~/.local/share/voice-clone/profiles/minha-voz --text "..." --output fala.wav` (padrão: até 10 tomadas, grava a mais fiel).
6. Roteiro inteiro: `voice-clone narrate --profile ~/.local/share/voice-clone/profiles/minha-voz --script roteiro.txt --output-dir narracao/` → `line-NN.leveled.wav` + `narration-report.json`. Regravar só algumas: `--only 3 7`.
7. Ouça as falas em `to_review` (status `CONFERIR_FIDELIDADE`) e peça a aprovação humana antes de publicar.

## Como escrever o roteiro (o que mais muda o resultado)

- **Falas curtas:** uma ideia por fala, até ~42 caracteres (umas 7 palavras). Parágrafo longo faz o modelo derivar a voz ou balbuciar.
- Uma fala por linha no `.txt`. No `.json`, `text` é a legenda e `speak` (opcional) é como falar: `{"text": "Acesse afirma.cc", "speak": "Acesse afirma ponto cê cê."}`.
- Siglas, nomes estrangeiros e endereços: escreva como se fala (no dicionário ou no `speak`).
- Números e datas por extenso quando a leitura for ambígua.

## Lições da produção (por que o padrão é assim)

| Problema que aconteceu | O que a skill faz |
|---|---|
| Com a transcrição da referência, o modelo cortava a fala (0,2 s) ou balbuciava 30 s | Não envia `ref_text` por padrão (`use_reference_transcript: false`) |
| Uma fala saiu com outra voz, 8 semitons acima | Mede tom (F0) e timbre de cada tomada; aceita até 1,2 semitom e timbre 4,3; até 10 tomadas |
| Tomadas cortadas ou repetidas | Descarta duração fora de 6–16 caracteres por segundo |
| Volume pulando entre falas | Corta silêncio das pontas e iguala a −20 dB de média, com limitador |
| "Admin" e "app" lidos errado | Dicionário de pronúncia só no texto falado; legenda fica com a grafia certa |

## Onde rodar

A geração usa a GPU (Metal). Rode `synthesize`/`narrate` num **terminal comum do Mac**; em sandbox de agente o MLX pode não enxergar a GPU. Se travar, pare e informe; não troque de engine.

## Idiomas

Qwen3-TTS fala português, inglês, espanhol, francês, alemão, italiano, japonês, coreano, chinês e russo. Defina no perfil (`--language`) ou por fala (`--language English`). Documentação: `README.md` (pt-BR), `README.en.md`, `README.es.md`.

Contrato completo de instalação, testes e recuperação: `docs/PLANO.md`.
