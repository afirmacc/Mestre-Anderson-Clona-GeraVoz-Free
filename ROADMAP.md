# Roadmap

## Fase 0 — Fundação

- [x] estrutura do repositório;
- [x] README e política de segurança;
- [x] diagnóstico inicial;
- [x] testes unitários e CI;
- [x] definir licença aberta.

## Fase 1 — macOS Apple Silicon

- [x] diagnóstico de plataforma, memória, disco, Python e FFmpeg;
- [x] instalador idempotente;
- [x] ambiente virtual e dependências fixadas;
- [x] adaptador Qwen3-TTS/MLX;
- [x] cache reutilizável do modelo;
- [x] preparação de perfil autorizado;
- [x] síntese e manifesto;
- [x] testes unitários de reutilização lógica, integridade e bloqueio de fallback;
- [ ] validação em Hermes limpo.

## Fase 2 — Qualidade

- [x] transcrição e comparação textual;
- [x] bateria inicial de pronúncia e expressividade;
- [x] relatórios JSON com schemas;
- [ ] QA humano estruturado;
- [ ] release candidate para testes do grupo.

## Fase 3 — Outras plataformas

- [ ] Linux + NVIDIA/CUDA;
- [ ] Windows via WSL2;
- [ ] backend Chatterbox separado;
- [ ] matriz pública de compatibilidade.
