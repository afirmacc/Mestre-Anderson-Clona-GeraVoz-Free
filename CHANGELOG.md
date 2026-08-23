# Histórico de mudanças

Este projeto segue a ideia de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e pretende adotar versionamento semântico após o primeiro release funcional.

## Não lançado

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
