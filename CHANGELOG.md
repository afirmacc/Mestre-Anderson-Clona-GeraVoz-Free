# Histórico de mudanças

Este projeto segue a ideia de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e pretende adotar versionamento semântico após o primeiro release funcional.

## 0.2.0 — 2026-11-13

Lições da produção real de vídeos narrados com voz clonada (Mestre Anderson Menezes de Oliveira · afirma.cc).

### Adicionado

- filtro de fidelidade vocal (`voice_clone/fidelity.py`): mede tom (F0) e timbre de cada tomada contra a referência; aceita até 1,2 semitom e timbre 4,3;
- `synthesize --takes N` (padrão 10): gera até N tomadas e grava a mais fiel; status `CONFERIR_FIDELIDADE` quando nenhuma passa;
- descarte de tomadas com duração implausível (fora de 6–16 caracteres por segundo);
- dicionário de pronúncia por perfil (`pronunciation.json`) e extra (`--pronunciation`), aplicado só ao texto falado;
- comando `narrate`: roteiro `.txt` (uma fala por linha) ou `.json` (`text` + `speak`), volume igualado a −20 dB, relatório `narration-report.json` com `to_review` e regravação seletiva `--only`;
- idioma no perfil (`prepare --language`) e por fala (`--language`);
- documentação em português, inglês e espanhol; modelos de consentimento em en/es; exemplos de pronúncia e roteiro.

### Mudado

- a transcrição da referência não é mais enviada ao modelo por padrão (`use_reference_transcript: false`): na produção ela causava falas cortadas ou balbucio;
- amostra com menos de 8 s de voz é recusada;
- `numpy` passa a ser dependência base;
- créditos: Mestre Anderson Menezes de Oliveira · Afirma.

## 0.1.0rc2

### Corrigido em 0.1.0rc2

- detecção do cache Hugging Face sob `model-cache/hub`;
- comparação canônica de vínculos Hermes entre `/tmp` e `/private/tmp`;
- reutilização do pacote Python quando a versão instalada já é válida;
- reparo seletivo por inventário dos componentes;
- smoke test obrigatório de backend/modelo e teste vocal opcional por perfil;
- `status` agora exige modelo, Whisper, FFmpeg, estado e integração Hermes;
- wheel inclui instalador, `SKILL.md`, schemas e templates.

### Adicionado

- estrutura inicial de Agent Skill;
- CLI com `doctor`, `install`, `status`, `repair`, `prepare`, `profile`, `synthesize`, `verify` e `test`;
- diagnóstico seguro e somente leitura;
- testes unitários e CI inicial;
- documentação de arquitetura, instalação, compatibilidade, testes e privacidade;
- regras de instalação idempotente;
- proteção contra dados biométricos no Git.
- instalador macOS Apple Silicon idempotente e integração Hermes preservadora;
- adaptador Qwen3-TTS/MLX sem fallback;
- perfis privados com hashes de referência e consentimento;
- manifestos, schemas, transcrição local e bateria de testes de voz;
- licença MIT.

### Pendente

- validação ponta a ponta no Hermes.
- segunda instalação real sem novo download;
- QA humano de uma voz consentida.
