# Compatibilidade

## Significado dos estados

- **Testado:** instalação e síntese aprovadas ponta a ponta.
- **Em implementação:** código em construção, sem garantia operacional.
- **Release candidate:** implementação disponível, aguardando homologação limpa.
- **Planejado:** arquitetura prevista, adaptador ainda ausente.
- **Experimental:** pode funcionar com limitações severas.
- **Não suportado:** o instalador deve bloquear.

## Matriz atual

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS/MLX | Release candidate |
| Linux NVIDIA | Qwen3/PyTorch ou Chatterbox/CUDA | Planejado |
| Windows WSL2 NVIDIA | Linux/CUDA | Planejado |
| CPU | Dependente da engine | Experimental |
| Mac Intel | Sem MLX | Não suportado atualmente |

Nenhuma combinação está marcada como estável. O Mac Apple Silicon será promovido somente após instalação limpa, reinstalação idempotente, bateria de voz e QA humano.
