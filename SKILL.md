---
name: clonar-voz-local
description: "Clona uma voz autorizada no próprio computador (Qwen3-TTS + MLX, Apple Silicon) e narra roteiros com ela, falando certo: captação guiada da amostra, dicionário de pronúncia por idioma, números/siglas/sites por extenso, escuta automática de cada tomada (Whisper) e aprendizado da grafia certa de palavras difíceis na sua voz. Filtro de tom, volume igual, sem fallback, consentimento obrigatório. Use quando pedirem narração com a própria voz, voz clonada local, locução de vídeo sem ElevenLabs, ou clone de voz em português, inglês ou espanhol. Local voice cloning and script narration with your own consented voice."
version: 0.3.0
author: "Mestre Anderson Menezes de Oliveira · Afirma (https://afirma.cc)"
license: MIT
---

# Clonar voz local

Criada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc). Nasceu da produção real de vídeos narrados com a voz do autor; cada regra abaixo veio de um erro que aconteceu de verdade.

## Regras obrigatórias

- Só a própria voz ou uma voz **autorizada por escrito** (`templates/consentimento.txt`, `consent.en.txt`, `consentimiento.es.txt`). Sem consentimento: `BLOQUEADO_VOZ`.
- Amostras, perfis e áudios gerados ficam **fora do repositório**.
- Nunca usar fallback nem trocar a engine em silêncio. Se falhar, parar e dizer.
- A automação mede voz e pronúncia; **a aprovação final é humana**.
- Áudio sintético não pode ser usado para enganar (fraude, se passar por alguém, burlar autenticação por voz).

## Fluxo completo

Perfil padrão: `~/.local/share/voice-clone/profiles/<perfil>` (abaixo, `$P`).

1. **Equipamento:** `voice-clone doctor --json`. Já instalado? `voice-clone status`; não reinstale. Senão `voice-clone install`.
2. **Captação (o que mais pesa):** `voice-clone record --guide --language Portuguese` mostra o texto de leitura (cobre os sons do idioma) e as dicas. Grave com `voice-clone record --output minha-voz.wav` ou no celular, e confira com `voice-clone record --analyze minha-voz.wav` (duração, ruído, estouro). Amostra ruim é recusada com a explicação de como regravar.
3. **Perfil:** `voice-clone prepare --input minha-voz.wav --profile-id minha-voz --consent consentimento.txt --language Portuguese`.
4. **Pronúncia antes de gravar:**
   - `voice-clone pronounce --profile $P --script roteiro.txt` → lista as palavras difíceis (estrangeirismo, sigla, marca) que ainda não estão no dicionário.
   - `voice-clone pronounce --profile $P --script roteiro.txt --learn-script --output-dir aprender/` → fala cada uma na sua voz em algumas grafias, escuta e guarda no dicionário a que foi entendida.
   - `voice-clone pronounce --profile $P --text "..."` → mostra exatamente como o texto será falado.
   - `voice-clone pronounce --profile $P --add "Admin=Adimin"` → correção manual.
5. **Narrar:** `voice-clone narrate --profile $P --script roteiro.txt --output-dir narracao/` → `line-NN.leveled.wav` + `narration-report.json`.
6. **Conferir:** ouça as falas em `to_review` (`CONFERIR_FIDELIDADE` = voz fora do tom; `CONFERIR_PRONUNCIA` = palavra suspeita, listada em `words.suspects`). Corrija o dicionário e regrave só elas: `--only 3 7`. Peça a aprovação humana antes de publicar.

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
| Amostra com ruído ou curta deixava o clone instável | Texto de leitura por idioma e análise da amostra no `prepare` |

## Onde rodar

A geração usa a GPU (Metal). Rode `narrate`, `synthesize` e `pronounce --learn` num **terminal comum do Mac**; em sandbox de agente o MLX pode não enxergar a GPU. Se travar, pare e informe; não troque de engine.

## Idiomas

Português, inglês e espanhol têm texto de leitura, dicionário base, números por extenso e documentação (`README.md`, `README.en.md`, `README.es.md`). O Qwen3-TTS também fala francês, alemão, italiano, japonês, coreano, chinês e russo (sem dicionário base ainda).

Contrato completo de instalação, testes e recuperação: `docs/PLANO.md`.
