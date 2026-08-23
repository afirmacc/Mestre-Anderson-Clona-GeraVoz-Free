# Plano operacional da versão 2

## Instalação idempotente

Toda execução começa com inventário. Cada componente é classificado como ausente, válido, desatualizado, incompatível ou corrompido. Itens válidos são reutilizados; reparos e atualizações afetam apenas alvos identificados.

Sem `--force`, o instalador nunca reinstala componentes válidos. Perfis privados são preservados em instalação, atualização, reparo, retorno e desinstalação.

## Gates

`NAO_DIAGNOSTICADO` → `COMPATIVEL` → `DEPENDENCIAS_OK` → `MODELO_OK` → `PERFIL_OK` → `TESTE_TECNICO_OK` → `AGUARDA_QA_HUMANO` → `PRONTO`.

## Bootstrap macOS Apple Silicon

1. Detectar macOS e `arm64`.
2. Validar Command Line Tools e Homebrew.
3. Instalar ou reutilizar Python 3.12, FFmpeg e Git.
4. Criar ou reutilizar ambiente virtual compatível com o lockfile.
5. Instalar ou validar MLX e MLX-Audio.
6. Reutilizar modelo íntegro; retomar download incompleto; baixar somente se necessário.
7. Instalar ou atualizar a skill do Hermes.
8. Executar testes e produzir relatório.

## Casos obrigatórios

- instalação limpa;
- segunda execução sem mudanças;
- atualização e retorno;
- reparo seletivo;
- download interrompido;
- modelo corrompido;
- preservação de perfis;
- síntese curta e longa;
- transcrição compatível;
- `fallback_used=false`;
- aprovação humana.

