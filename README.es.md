# Mestre Anderson Clona GeraVoz Free

[Português](README.md) · [English](README.en.md) · **Español**

![version](https://img.shields.io/badge/versi%C3%B3n-0.5.0-blue)
![IA local](https://img.shields.io/badge/IA-100%25%20LOCAL-success)
![grátis](https://img.shields.io/badge/costo-0%20%24-success)
![Agentes](https://img.shields.io/badge/agentes-Claude%20%C2%B7%20Codex%20%C2%B7%20Hermes%20%C2%B7%20Orca%20%C2%B7%20OpenClaw-6f42c1)

**Clona tu voz y genera narraciones con ella usando IA 100% LOCAL, gratis.** El modelo de voz (Qwen3-TTS) y el oído automático (Whisper) corren **en tu propia computadora**: sin nube, sin clave de API, sin pagar por carácter, y tu voz **nunca sale de tu máquina**. Una vez instalada, funciona incluso sin internet.

Funciona como **skill** para **Claude Code, Codex, Hermes, Orca y OpenClaw** (y cualquier agente que lea `SKILL.md`), y como herramienta de línea de comandos.

> Creada por **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc)
> Nació de una producción real: los videos de la app *Combinado em Família*, narrados con la voz del autor. Cada configuración de esta skill viene de un error que realmente ocurrió.

## Qué significa "IA local" aquí

| | Esta skill | Servicios de voz en la nube |
|---|---|---|
| Dónde se procesa tu voz | En tu Mac (GPU Apple Silicon) | En los servidores de la empresa |
| ¿Tu grabación sale de la computadora? | Nunca | Sí, se sube |
| Costo | Gratis (código MIT, modelo Apache 2.0) | Suscripción o por carácter |
| Clave de API / cuenta | No hace falta | Obligatoria |
| Funciona sin internet | Sí, una vez instalada | No |

## Úsala en tu agente

```bash
# Claude Code, Codex, Hermes y OpenClaw a la vez (instalación de usuario)
npx skills add afirmacc/Mestre-Anderson-Clona-GeraVoz-Free -g -a claude-code -a codex -a hermes-agent -a openclaw
```

- **Orca:** Orca ejecuta Claude Code y Codex por dentro y usa las mismas skills; basta con instalarla para ellos.
- **Otro agente:** copia la carpeta del repositorio en su carpeta de skills; lo que cuenta es el `SKILL.md`.
- Luego pide: *"crea mi voz"* o *"narra este guion con mi voz"*.

## Empieza en 3 pasos

```bash
# 1. Descarga la skill (Claude Code, Codex, Hermes, Orca, OpenClaw…)
npx skills add afirmacc/Mestre-Anderson-Clona-GeraVoz-Free

# 2. Instala la herramienta (macOS Apple Silicon). Pregunta antes de descargar el modelo (~3 GB).
git clone https://github.com/afirmacc/Mestre-Anderson-Clona-GeraVoz-Free.git && ./Mestre-Anderson-Clona-GeraVoz-Free/installers/install-macos.sh

# (¿Ya tienes el modelo Qwen3-TTS 1.7B Base 8bit? Agrega --model-dir=<carpeta> y no se descarga de nuevo.)

# 3. Crea tu voz: el asistente guía todo y reproduce el resultado al final
voice-clone crear-voz --language es
```

**Consejo de oro (prueba real):** la mejor muestra vino de un **audio de WhatsApp grabado con el celular cerca de la boca**, en un lugar tranquilo, unos 30 s hablando con naturalidad (voz a −13 dB, fondo −54 dB). ¿Tienes uno así? Usa `voice-clone crear-voz --input audio.opus` (.opus, .m4a, .mp3, .wav). Para narrar, habla más calmado y grave que en una charla: el clon copia el tono de la muestra.

`crear-voz` hace, en orden: consentimiento (escribes AUTORIZO) → prueba de volumen de 5 s ("acércate" o "puedes grabar") → lectura guiada que cubre los sonidos del idioma → análisis de la muestra (regraba hasta que esté bien) → perfil → frase de prueba reproducida al momento → tú apruebas. Luego pídele a tu agente: *"narra este guion con mi voz"*, o:

```bash
voice-clone narrate --profile ~/.local/share/voice-clone/profiles/<tu-perfil> --script guion.txt --output-dir narracion/
```

### Por qué la captación importa tanto (caso real)

El modelo imita la muestra entera: sala, micrófono y forma de hablar. Mismo modelo, mismo guion: una muestra buena (voz a −13 dB, 26 s de voz, tono natural de narración) dio una voz excelente; una muestra con el micrófono lejos (−35 dB, 11 s de voz, lectura tensa) dio una voz mala, incluso igualando el volumen después. Por eso la skill prueba el volumen antes, rechaza muestras bajas o cortas y pide leer en tu tono de narrar.

## Paso a paso (cada etapa por separado)

```bash
# 1. Captación: mira el texto de lectura (cubre los sonidos del idioma) y los consejos, graba y revisa
voice-clone record --guide --language Spanish
voice-clone record --output mi-voz.wav --language Spanish   # o graba con el celular
voice-clone record --analyze mi-voz.wav                      # duración, ruido, saturación: dice qué corregir

# 2. Perfil (con consentimiento firmado)
voice-clone prepare --input mi-voz.wav --profile-id mi-voz --consent consentimiento.txt --language Spanish
P=~/.local/share/voice-clone/profiles/mi-voz

# 3. Pronunciación: encuentra las palabras difíciles del guion y aprende cómo TU voz debe decirlas
voice-clone pronounce --profile $P --script guion.txt
voice-clone pronounce --profile $P --script guion.txt --learn-script --output-dir aprender/

# 4. Narración: escucha cada toma y se queda con la que tiene tu tono y las palabras correctas
voice-clone narrate --profile $P --script guion.txt --output-dir narracion/

# 5. Escucha las frases de "to_review" (narracion/narration-report.json) y regraba solo esas
voice-clone narrate --profile $P --script guion.txt --output-dir narracion/ --only 3 7
```

## Hablar bien: cómo la skill cuida la pronunciación

1. **Diccionario base por idioma** (pt, en, es) con las palabras que el modelo más falla: app, WhatsApp, YouTube, Google, Wi-Fi, email… El diccionario de tu perfil gana.
2. **Reglas automáticas:** dinero, `40%`, números, siglas, sitios web (`afirma.cc` → "afirma punto ce ce") y correos.
3. **Encontrar palabras difíciles** en el guion antes de grabar (`pronounce --script`).
4. **Aprender con tu voz** (`pronounce --learn palabra` o `--learn-script`): la skill dice la palabra en varias grafías, escucha con Whisper y guarda la que fue entendida.
5. **Cada toma se escucha** en la narración: si una palabra sale cambiada o se pierde, prueba otra toma; si ninguna sale limpia, la frase va a `to_review` con las palabras sospechosas.
6. **Vista previa:** `pronounce --text "..."` muestra exactamente qué se dirá. Corrección manual: `pronounce --add "WhatsApp=guasap"`.

Los subtítulos siempre mantienen la ortografía correcta.

## Lecciones de producción (por qué la configuración es así)

| Problema real | Lo que hace la skill |
|---|---|
| Una frase salió con **otra voz**, 8 semitonos más aguda | **Filtro de fidelidad:** mide tono (F0) y timbre de cada toma contra tu muestra; acepta hasta 1,2 semitonos (el timbre solo bloquea cambios groseros); intenta hasta 10 veces y se queda con la mejor |
| Con la transcripción de la muestra, el modelo **cortaba** frases o **balbuceaba** 30 s | No envía la transcripción por defecto |
| Tomas cortadas o repetidas | Descarta duraciones fuera de 6–16 caracteres por segundo |
| **Volumen que salta** entre frases | Recorta silencios de los extremos e iguala todo a −20 dB |
| Palabras de marca **mal pronunciadas** | Diccionario base, escucha automática y aprendizaje de la grafía con tu voz |
| Una muestra baja, corta o tensa dio un **clon malo** | Prueba de volumen, mínimo de 15 s de voz, muestras bajas rechazadas, asistente `crear-voz` |
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

Si esta skill te ayudó, deja una ⭐ y cita: *Mestre Anderson Clona GeraVoz Free — Mestre Anderson Menezes de Oliveira · afirma.cc*.
