# IA Skill — Clonación de Voz Local

[Português](README.md) · [English](README.en.md) · **Español**

![versión](https://img.shields.io/badge/versi%C3%B3n-0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Claude%20%C2%B7%20Codex%20%C2%B7%20Hermes-6f42c1)
![local](https://img.shields.io/badge/procesamiento-100%25%20local-success)

Clona **tu propia voz** en tu computadora y narra guiones completos con ella — sin ElevenLabs, sin pagar por carácter y sin enviar tu voz a ningún servicio. Funciona como **skill para agentes de IA** (Claude Code, Codex, Hermes y otros) y como herramienta de línea de comandos.

> Creada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc)
> Nació de una producción real: los videos de la app *Combinado em Família*, narrados con la voz del autor. Cada configuración de esta skill viene de un error que realmente ocurrió.

## Instalar como skill

```bash
npx skills add afirmacc/ia-skill-clonagem-voz
```

Funciona con Claude Code, Codex, Hermes y cualquier agente que lea `SKILL.md`. Luego pídele a tu agente: *"narra este guion con mi voz"*.

## Instalar la herramienta (macOS Apple Silicon)

```bash
git clone https://github.com/afirmacc/ia-skill-clonagem-voz.git
cd ia-skill-clonagem-voz
./installers/install-macos.sh
```

El instalador es idempotente: pregunta antes de instalar herramientas o descargar el modelo (Qwen3-TTS 1.7B, 8 bits, ~2 GB) y en la segunda ejecución solo vuelve a validar.

## Uso en 4 pasos

```bash
# 1. Perfil: 15 a 40 s de habla natural, limpia, de un solo hablante, con consentimiento firmado
voice-clone prepare --input mi-voz.m4a --profile-id mi-voz \
  --consent consentimiento.txt --language Spanish

# 2. Una frase (hasta 10 tomas; guarda la más fiel a tu tono y timbre)
voice-clone synthesize --profile ~/.local/share/voice-clone/profiles/mi-voz \
  --text "¡Hola! Esta es mi voz." --output hola.wav

# 3. Un guion completo (una frase por línea), con el mismo volumen en todas
voice-clone narrate --profile ~/.local/share/voice-clone/profiles/mi-voz \
  --script guion.txt --output-dir narracion/

# 4. Escucha las frases de "to_review" (narracion/narration-report.json) y regraba solo esas
voice-clone narrate ... --only 3 7
```

## Qué trae la 0.2.0 (lecciones de producción)

| Problema real | Lo que hace la skill |
|---|---|
| Una frase salió con **otra voz**, 8 semitonos más aguda | **Filtro de fidelidad:** mide tono (F0) y timbre de cada toma contra tu muestra; acepta hasta 1,2 semitonos y timbre 4,3; intenta hasta 10 veces y se queda con la mejor |
| Con la transcripción de la muestra, el modelo **cortaba** frases o **balbuceaba** 30 s | No envía la transcripción por defecto |
| Tomas cortadas o repetidas | Descarta duraciones fuera de 6–16 caracteres por segundo |
| **Volumen que salta** entre frases | Recorta silencios de los extremos e iguala todo a −20 dB |
| Palabras de marca **mal pronunciadas** | **Diccionario de pronunciación** solo en el audio; los subtítulos mantienen la ortografía correcta |
| Párrafos largos hacían **derivar** la voz | Guiones en frases cortas (hasta ~42 caracteres) |

## Cómo escribir un buen guion

- Una idea por frase, unas 7 palabras.
- `.txt`: una frase por línea. `.json`: `{"lines": [{"text": "Visita afirma.cc", "speak": "Visita afirma punto ce ce."}]}` — `text` va a los subtítulos, `speak` es cómo decirlo.
- Siglas, nombres extranjeros y direcciones web: escríbelos como se pronuncian.
- Ejemplos en [`templates/`](templates/).

## Idiomas

Portugués, inglés, español, francés, alemán, italiano, japonés, coreano, chino y ruso (Qwen3-TTS). Usa `--language` en el perfil o en cada frase.

## Compatibilidad

| Plataforma | Backend | Estado |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS + MLX | Usado en producción (0.2.0) |
| Linux + NVIDIA | Qwen3/PyTorch + CUDA | Planeado |
| Windows + WSL2 + NVIDIA | Backend Linux/CUDA | Planeado |
| Mac Intel / solo CPU | — | No validado |

Ejecuta la generación en una terminal normal de macOS: usa la GPU (Metal).

## Principios

- **Local por defecto:** el modelo y el procesamiento quedan en tu computadora.
- **Consentimiento obligatorio:** solo tu voz o una voz autorizada por escrito ([es](templates/consentimiento.es.txt) · [pt](templates/consentimento.txt) · [en](templates/consent.en.txt)).
- **Sin fallback silencioso:** si el perfil o el motor fallan, se detiene y avisa (`BLOQUEADO_VOZ`, "voz bloqueada").
- **Aprobación humana:** la máquina mide integridad y fidelidad; una persona aprueba la voz.
- **Privacidad:** muestras, perfiles y audios nunca van a Git (los bloquea el `.gitignore`).

## Uso responsable

No la uses para clonar a alguien sin autorización, fraude, suplantación, burlar autenticación por voz o fabricar declaraciones de terceros. Si hay duda sobre el consentimiento o la identidad, el estado correcto es `BLOQUEADO_VOZ`.

Los mensajes de la CLI y la documentación detallada están en portugués de Brasil; las traducciones son bienvenidas.

## Contribuir

Bienvenidos: nuevos backends locales (Linux/NVIDIA, Windows), documentación en más idiomas, pruebas, accesibilidad, seguridad y prevención de abusos. Nunca envíes muestras reales de voz, modelos, cachés ni datos personales. Lee [CONTRIBUTING.md](CONTRIBUTING.md). Contacto: [app@afirma.cc](mailto:app@afirma.cc).

## Licencia

MIT — ver [LICENSE](LICENSE). La licencia del código no da derecho a usar la voz de nadie ni reemplaza el consentimiento. El modelo Qwen3-TTS es Apache 2.0.

## Créditos

Ideada y creada por **Mestre Anderson Menezes de Oliveira**, de [Afirma](https://afirma.cc), para devolver a la comunidad el conocimiento recibido de amigos, colaboradores y de quienes comparten tecnología con generosidad. Con el apoyo de Bellete Ritter de Oliveira.

Si esta skill te ayudó, deja una ⭐ y cita: *Clonación de Voz Local — Mestre Anderson Menezes de Oliveira · afirma.cc*.
