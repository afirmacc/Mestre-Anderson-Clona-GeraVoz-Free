---
name: clonar-voz-local
description: Diagnostica, instala e valida clonagem local autorizada de voz sem fallback silencioso.
version: 0.1.0-dev
---

# Clonar voz local

## Estado

Pré-lançamento. Use `voice-clone doctor` antes de qualquer instalação. Não declare a skill pronta enquanto o backend e os testes de voz não forem aprovados.

## Regras obrigatórias

- Usar somente voz própria ou autorizada por escrito.
- Manter amostras e perfis fora do repositório.
- Nunca usar fallback ou trocar silenciosamente a engine.
- Reinstalações devem ser idempotentes: validar e reutilizar componentes corretos.
- Automação valida integridade; identidade vocal exige aprovação humana.
- Na incerteza, retornar `BLOQUEADO_VOZ`.

## Fluxo

1. Execute `voice-clone doctor --json`.
2. Confira plataforma, arquitetura, memória, disco e dependências.
3. Se já estiver instalado, execute `voice-clone status` e reteste; não reinstale tudo.
4. Prepare um perfil autorizado fora do repositório.
5. Sintetize somente com o backend declarado no perfil.
6. Gere relatórios técnicos e faça QA humano.

Leia `docs/PLANO.md` para o contrato completo de instalação, atualização, testes e recuperação.

