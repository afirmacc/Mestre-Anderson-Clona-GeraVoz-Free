# Arquitetura

## Componentes

- **Skill:** procedimento carregado pelo agente.
- **CLI:** interface determinística para diagnóstico e operação.
- **Adaptador:** integração isolada com uma engine.
- **Perfil privado:** referência, consentimento, parâmetros e pronúncia.
- **Relatórios:** evidências de instalação, síntese e QA.

## Fluxo de dados

```text
texto + perfil privado
        ↓
validação de consentimento e hash
        ↓
adaptador da engine declarada
        ↓
áudio local
        ↓
verificação técnica e transcrição
        ↓
QA humano
```

## Separação de responsabilidades

A skill não contém vozes. A CLI não escolhe outra engine silenciosamente. O adaptador não aprova identidade. O QA humano não substitui testes técnicos.

## Estados

`NAO_DIAGNOSTICADO` → `COMPATIVEL` → `DEPENDENCIAS_OK` → `MODELO_OK` → `PERFIL_OK` → `TESTE_TECNICO_OK` → `AGUARDA_QA_HUMANO` → `PRONTO`.

Qualquer falha preserva o último estado seguro.

