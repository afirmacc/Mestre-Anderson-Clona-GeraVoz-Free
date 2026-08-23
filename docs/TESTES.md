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

