# Estratégia de testes

## Testes unitários

```bash
python -m unittest discover -s tests -v
```

## Cenários de instalação

- máquina limpa;
- segunda execução sem mudanças;
- dependência ausente;
- atualização;
- reparo seletivo;
- download interrompido;
- modelo corrompido;
- retorno à versão anterior;
- preservação de perfis.

## Casos de voz

- frase curta;
- nomes próprios;
- números, datas e valores;
- siglas;
- pergunta e exclamação;
- termos fonéticos;
- texto de 30 a 45 segundos;
- texto longo segmentado.

## Gate

Testes automáticos verificam integridade e correspondência textual. Sem avaliação humana autorizada, o estado máximo é `AGUARDA_QA_HUMANO`.

### Gate de release estável

1. `python -m unittest discover -s tests -v` aprovado;
2. instalação limpa aprovada em Mac Apple Silicon;
3. segunda execução sem reinstalar dependências nem modelo;
4. criação e validação de perfil consentido;
5. todos os casos de `templates/voice-test-cases.json` gerados;
6. `fallback_used=false` em todos os manifestos;
7. correspondência textual mínima de 0,85 quando houver transcrição;
8. aprovação humana de timbre, naturalidade, ritmo e pronúncia;
9. varredura do Git sem vozes, perfis, credenciais ou modelos;
10. instalação pelo artefato da release candidate em Hermes limpo.
