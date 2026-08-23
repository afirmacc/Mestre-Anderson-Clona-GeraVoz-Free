# IA Skill — Clonagem de Voz Local

![status](https://img.shields.io/badge/status-release%20candidate-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Hermes](https://img.shields.io/badge/Hermes-Agent%20Skill-6f42c1)
![local](https://img.shields.io/badge/processamento-local-success)

Clonagem de voz local, auditável e orientada por consentimento para agentes de IA — sem depender do ElevenLabs e sem enviar a voz para serviços externos.

> Criado a partir de colaboração e compartilhado para devolver conhecimento à comunidade.

## Estado do projeto

> **Release candidate para macOS Apple Silicon.**

A implementação do caminho Qwen3-TTS/MLX está disponível para homologação. Ainda não considere esta versão estável até concluir uma instalação limpa, uma segunda execução idempotente e o QA humano da voz no equipamento de destino.

### O que já funciona

- CLI com diagnóstico, instalação, reparo, perfis, síntese, verificação e testes;
- instalador idempotente para macOS Apple Silicon;
- adaptador Qwen3-TTS/MLX sem fallback;
- preparação da amostra por FFmpeg e validação por hashes;
- manifestos, relatórios, transcrição local e comparação textual;
- testes automatizados e proteção contra vozes ou perfis no Git.

### O que ainda precisa de homologação

- instalação limpa em uma segunda máquina Hermes;
- repetição da instalação sem novo download;
- bateria completa com uma voz de teste consentida;
- aprovação humana de semelhança, naturalidade e estabilidade;
- Linux/NVIDIA e Windows/WSL2.

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

Comandos disponíveis:

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
```

## Compatibilidade planejada

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS + MLX | Release candidate |
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

Instale a partir de um clone verificado deste repositório:

```bash
./installers/install-macos.sh
```

O script pede confirmação antes de instalar ferramentas de sistema ou baixar o modelo. Uma segunda execução revalida e reutiliza os componentes corretos.

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

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE). A licença do código não concede direito de usar a voz de terceiros nem substitui consentimento.

## Créditos

Idealizado por Anderson Oliveira como forma de retribuir à comunidade o conhecimento recebido de amigos, colaboradores e pessoas que compartilham tecnologia de maneira generosa.

Desenvolvido com apoio da Bellete Ritter de Oliveira e construído para evoluir por colaboração.
