# IA Skill — Clonagem de Voz Local

![status](https://img.shields.io/badge/status-pr%C3%A9--alpha-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Hermes](https://img.shields.io/badge/Hermes-Agent%20Skill-6f42c1)
![local](https://img.shields.io/badge/processamento-local-success)

Clonagem de voz local, auditável e orientada por consentimento para agentes de IA — sem depender do ElevenLabs e sem enviar a voz para serviços externos.

> Criado a partir de colaboração e compartilhado para devolver conhecimento à comunidade.

## Estado do projeto

> **Pré-lançamento / em desenvolvimento.**

A arquitetura da skill e o plano de instalação estão definidos. A CLI, os instaladores e os adaptadores ainda estão em implementação e validação. Não considere esta versão pronta para produção até que a matriz de compatibilidade apresente sua plataforma como **testada**.

### O que já funciona

- CLI inicial com `voice-clone doctor` e `voice-clone status`;
- diagnóstico sem alterações no equipamento;
- detecção básica de plataforma, arquitetura, memória, disco e comandos;
- testes automatizados da camada de diagnóstico;
- CI inicial para macOS e Linux;
- proteção contra versionamento acidental de vozes e perfis.

### O que ainda não funciona

- instalação automática das engines;
- criação e preparação do perfil;
- síntese pela CLI pública;
- transcrição e QA automático;
- suporte validado para produção.

## Documentação

- [Instalação e bootstrap](docs/INSTALACAO.md)
- [Arquitetura](docs/ARQUITETURA.md)
- [Compatibilidade](docs/COMPATIBILIDADE.md)
- [Estratégia de testes](docs/TESTES.md)
- [Privacidade e consentimento](docs/PRIVACIDADE.md)
- [Plano operacional](docs/PLANO.md)
- [Política de releases](docs/RELEASES.md)
- [Roadmap](ROADMAP.md)

## Por que este projeto existe?

Este projeto nasceu de uma experiência prática: criar uma voz local para produção de conteúdo sem cobrança por caractere e sem depender de uma plataforma externa.

O objetivo é transformar esse aprendizado em uma skill que outras pessoas e IAs possam instalar, testar, auditar e melhorar juntas.

## Princípios

- **Local por padrão:** modelos e processamento ficam no equipamento do usuário.
- **Consentimento obrigatório:** use somente sua própria voz ou uma voz expressamente autorizada.
- **Sem fallback silencioso:** se o perfil ou a engine falhar, a operação deve parar.
- **Instalação idempotente:** executar o instalador novamente não reinstala componentes válidos.
- **Validação técnica e humana:** integridade pode ser automatizada; identidade e naturalidade exigem avaliação humana.
- **Transparência:** plataformas não testadas são identificadas como experimentais ou não suportadas.

## O que a skill pretende fazer

```text
amostra autorizada
        ↓
diagnóstico do equipamento
        ↓
instalação/revalidação da engine local
        ↓
preparação e validação do perfil de voz
        ↓
síntese local
        ↓
transcrição e testes automáticos
        ↓
avaliação humana
        ↓
relatório auditável
```

Comandos planejados:

```bash
voice-clone doctor
voice-clone install
voice-clone status
voice-clone prepare
voice-clone profile validate
voice-clone synthesize
voice-clone verify
voice-clone test
voice-clone repair
voice-clone update --check
voice-clone uninstall
```

## Compatibilidade planejada

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS + MLX | Em implementação |
| Linux + NVIDIA | Qwen3/PyTorch ou Chatterbox + CUDA | Planejado |
| Windows + WSL2 + NVIDIA | Backend Linux/CUDA | Planejado |
| CPU sem GPU compatível | Dependente da engine, desempenho reduzido | Experimental |
| Mac Intel | Alternativa sem MLX | Não validado |

O instalador deverá diagnosticar o equipamento e bloquear combinações incompatíveis em vez de tentar improvisar outra voz.

## Instalação no Hermes

O Hermes Agent utiliza o padrão `SKILL.md`. A skill deverá ser instalada em um diretório semelhante a:

```text
~/.hermes/skills/local/clonar-voz-local/
```

Após a instalação, abra uma nova sessão ou use `/reset` e confirme:

```bash
hermes skills list
```

> Os comandos automáticos de bootstrap serão documentados quando a primeira versão executável for validada. Por enquanto, não execute instruções de instalação copiadas de forks ou fontes não verificadas.

## Instalação inteligente

O instalador será idempotente. Antes de modificar o equipamento, ele deverá verificar:

- skill e versão existentes;
- Python e ambiente virtual;
- FFmpeg, Git e ferramentas de compilação;
- backend MLX, CUDA ou CPU;
- bibliotecas instaladas e versões fixadas;
- modelo e integridade do cache;
- perfis privados existentes;
- resultados dos testes anteriores.

Componentes válidos serão reutilizados. Atualização, reparo ou reinstalação forçada deverão ser explícitos e preservar os perfis de voz.

## Perfil privado

Vozes reais nunca devem fazer parte da skill ou do repositório.

Estrutura prevista:

```text
voice-profiles/<profile-id>/
├── reference.wav
├── profile.json
├── consent.txt
└── pronunciation.json
```

Esses arquivos devem permanecer privados, fora do Git e com permissões restritas.

## Testes

A validação deverá cobrir:

1. instalação limpa;
2. segunda execução sem reinstalação;
3. atualização e retorno de versão;
4. reparo seletivo;
5. download interrompido;
6. modelo ausente ou corrompido;
7. preservação dos perfis privados;
8. frase curta;
9. nomes, números, datas e siglas;
10. termos do dicionário fonético;
11. texto de 30 a 45 segundos;
12. texto longo para detectar deriva de timbre.

Os relatórios planejados são:

```text
installation-report.json
voice-test-report.json
```

Uma voz só poderá receber o estado `PRONTO` após testes técnicos e aprovação humana autorizada.

## Uso responsável

Não use este projeto para:

- clonar uma pessoa sem autorização;
- praticar fraude ou personificação enganosa;
- contornar autenticação por voz;
- fabricar declarações atribuídas a terceiros;
- ocultar a natureza sintética do áudio quando isso puder induzir alguém ao erro.

Se a autorização, o perfil ou a identidade da voz estiverem incertos, o estado correto é `BLOQUEADO_VOZ`.

## Estrutura planejada

```text
.
├── SKILL.md
├── bin/
├── scripts/
├── installers/
├── adapters/
├── requirements/
├── schemas/
├── templates/
├── tests/
├── docs/
└── .github/workflows/
```

## Como contribuir

Contribuições serão bem-vindas em:

- novos backends locais;
- compatibilidade com outras plataformas;
- testes de instalação limpa e atualização;
- análise e preparação de áudio;
- acessibilidade e documentação;
- segurança, privacidade e prevenção de abuso.

Antes de contribuir, não envie amostras reais de voz, modelos pesados, caches, credenciais ou dados pessoais.

Leia [CONTRIBUTING.md](CONTRIBUTING.md) e o [Código de Conduta](CODE_OF_CONDUCT.md) antes de abrir uma contribuição.

## Licença

A licença aberta ainda será definida antes do primeiro lançamento público. Até essa decisão, o conteúdo permanece em desenvolvimento e não deve ser redistribuído como uma versão estável.

## Créditos

Idealizado por Anderson Oliveira como forma de retribuir à comunidade o conhecimento recebido de amigos, colaboradores e pessoas que compartilham tecnologia de maneira generosa.

Desenvolvido com apoio da Bellete Ritter de Oliveira e construído para evoluir por colaboração.
