# IA Skill — Clonación de Voz Local

[Português](README.md) · [English](README.en.md) · **Español**

![versión](https://img.shields.io/badge/versi%C3%B3n-0.3.0-blue)
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

## Uso en 5 pasos

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
