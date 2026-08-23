# Como contribuir

Obrigada por contribuir. O projeto está em pré-lançamento e prioriza segurança, reprodutibilidade e documentação honesta.

## Antes de começar

1. confira issues e pull requests existentes;
2. para mudanças grandes, abra uma proposta antes de implementar;
3. não inclua voz real, dado pessoal, modelo, cache ou credencial;
4. descreva plataforma e hardware usados nos testes;
5. leia `SECURITY.md` e `docs/PRIVACIDADE.md`.

## Canais de contribuição

- Para código, correções e documentação, prefira Issues e Pull Requests no GitHub.
- Para dúvidas, ideias ou contato direto sobre contribuições, escreva para [bellete.afirma.cc@gmail.com](mailto:bellete.afirma.cc@gmail.com).
- Não envie amostras de voz, dados biométricos, credenciais ou outros dados sensíveis por e-mail.

## Ambiente de desenvolvimento

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Requisitos de uma mudança

- testes para comportamento novo ou corrigido;
- instalação idempotente;
- nenhuma troca silenciosa de engine ou voz;
- mensagens de erro acionáveis;
- documentação de limitações;
- preservação de perfis privados;
- relatório do teste executado.

## Commits

Prefira commits pequenos e mensagens no padrão:

```text
feat: adiciona diagnóstico de MLX
fix: preserva perfil durante reparo
docs: detalha instalação no Hermes
test: cobre segunda execução idempotente
```

## Pull request

Preencha o template, informe risco, testes e plataformas. Uma contribuição não será mesclada se depender de voz privada para ser validada.
