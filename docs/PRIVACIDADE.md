# Privacidade e consentimento

Uma voz é dado pessoal e pode funcionar como identificador biométrico. O projeto adota minimização e processamento local.

## Regras

- consentimento específico e verificável;
- finalidade registrada;
- amostra fora do Git;
- acesso local restrito;
- nenhum log com conteúdo privado desnecessário;
- exclusão ou revogação respeitada;
- proibição de clonagem a partir de áudio sintético.

## Perfil privado

```text
voice-profiles/<id>/
├── reference.wav
├── profile.json
├── consent.txt
└── pronunciation.json
```

O `.gitignore` bloqueia esses caminhos, mas isso não substitui revisão humana antes de cada commit.

