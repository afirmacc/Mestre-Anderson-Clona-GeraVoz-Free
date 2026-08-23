# Compatibilidade

## Significado dos estados

- **Testado:** instalação e síntese aprovadas ponta a ponta.
- **Em implementação:** código em construção, sem garantia operacional.
- **Planejado:** arquitetura prevista, adaptador ainda ausente.
- **Experimental:** pode funcionar com limitações severas.
- **Não suportado:** o instalador deve bloquear.

## Matriz atual

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS/MLX | Em implementação |
| Linux NVIDIA | Qwen3/PyTorch ou Chatterbox/CUDA | Planejado |
| Windows WSL2 NVIDIA | Linux/CUDA | Planejado |
| CPU | Dependente da engine | Experimental |
| Mac Intel | Sem MLX | Não suportado atualmente |

Nenhuma combinação está marcada como testada para release público.

