# AI Skill — Local Voice Cloning

[Português](README.md) · **English** · [Español](README.es.md)

![version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Claude%20%C2%B7%20Codex%20%C2%B7%20Hermes-6f42c1)
![local](https://img.shields.io/badge/processing-100%25%20local-success)

Clone **your own voice** on your computer and narrate whole scripts with it — no ElevenLabs, no per-character billing, and your voice never leaves your machine. It works as a **skill for AI agents** (Claude Code, Codex, Hermes and others) and as a command-line tool.

> Created by **Mestre Anderson Menezes de Oliveira** · [afirma.cc](https://afirma.cc)
> Born from real production work: the videos of the *Combinado em Família* app, narrated with the author's own voice. Every default in this skill comes from a mistake that actually happened.

## Install as a skill

```bash
npx skills add afirmacc/ia-skill-clonagem-voz
```

Works with Claude Code, Codex, Hermes and any agent that reads `SKILL.md`. Then just ask your agent: *"narrate this script with my voice"*.

## Install the tool (macOS Apple Silicon)

```bash
git clone https://github.com/afirmacc/ia-skill-clonagem-voz.git
cd ia-skill-clonagem-voz
./installers/install-macos.sh
```

The installer is idempotent: it asks before installing tools or downloading the model (Qwen3-TTS 1.7B, 8-bit, ~2 GB) and only re-validates on a second run.

## Use in 4 steps

```bash
# 1. Profile: 15–40 s of natural, clean, single-speaker speech, with signed consent
voice-clone prepare --input my-voice.m4a --profile-id my-voice \
  --consent consent.txt --language English

# 2. One line (up to 10 takes; keeps the one closest to your pitch and timbre)
voice-clone synthesize --profile ~/.local/share/voice-clone/profiles/my-voice \
  --text "Hi! This is my voice." --output hi.wav

# 3. A whole script (one line per row), with even loudness across lines
voice-clone narrate --profile ~/.local/share/voice-clone/profiles/my-voice \
  --script script.txt --output-dir narration/

# 4. Listen to the lines listed in "to_review" (narration/narration-report.json) and redo only those
voice-clone narrate ... --only 3 7
```

## What 0.2.0 brings (production lessons)

| Real problem | What the skill does |
|---|---|
| One line came out in **a different voice**, 8 semitones higher | **Fidelity filter:** measures pitch (F0) and timbre of every take against your sample; accepts up to 1.2 semitones and timbre 4.3; tries up to 10 times and keeps the best |
| With the reference transcript, the model **cut** lines or **babbled** for 30 s | Does not send the transcript by default |
| Truncated or repeating takes | Discards durations outside 6–16 characters per second |
| **Loudness jumping** between lines | Trims edge silence and levels every line to −20 dB mean |
| Brand words **mispronounced** | **Pronunciation dictionary** applied only to the spoken text; subtitles keep the correct spelling |
| Long paragraphs made the voice **drift** | Scripts in short lines (up to ~42 characters) |

## Writing a good script

- One idea per line, around 7 words.
- `.txt`: one line per row. `.json`: `{"lines": [{"text": "Visit afirma.cc", "speak": "Visit afirma dot see see."}]}` — `text` goes to subtitles, `speak` is how to say it.
- Acronyms, foreign names and URLs: write them the way they are spoken.
- Examples in [`templates/`](templates/).

## Languages

Portuguese, English, Spanish, French, German, Italian, Japanese, Korean, Chinese and Russian (Qwen3-TTS). Use `--language` on the profile or per line.

## Compatibility

| Platform | Backend | Status |
|---|---|---|
| macOS Apple Silicon | Qwen3-TTS + MLX | Used in production (0.2.0) |
| Linux + NVIDIA | Qwen3/PyTorch + CUDA | Planned |
| Windows + WSL2 + NVIDIA | Linux/CUDA backend | Planned |
| Intel Mac / CPU only | — | Not validated |

Run generation in a regular macOS terminal: it uses the GPU (Metal).

## Principles

- **Local by default:** model and processing stay on your computer.
- **Consent required:** only your voice or a voice authorized in writing ([en](templates/consent.en.txt) · [pt](templates/consentimento.txt) · [es](templates/consentimiento.es.txt)).
- **No silent fallback:** if the profile or engine fails, it stops and says so (`BLOQUEADO_VOZ`, "voice blocked").
- **Human approval:** the machine checks integrity and fidelity; a person approves the voice.
- **Privacy:** samples, profiles and generated audio never go to Git (blocked by `.gitignore`).

## Responsible use

Do not use it to clone someone without permission, for fraud, impersonation, bypassing voice authentication or fabricating statements by others. If consent or identity is uncertain, the correct state is `BLOQUEADO_VOZ`.

The CLI messages and detailed docs are in Brazilian Portuguese; translations are welcome.

## Contributing

Welcome: new local backends (Linux/NVIDIA, Windows), docs in more languages, tests, accessibility, security and abuse prevention. Never submit real voice samples, models, caches or personal data. See [CONTRIBUTING.md](CONTRIBUTING.md). Contact: [app@afirma.cc](mailto:app@afirma.cc).

## License

MIT — see [LICENSE](LICENSE). The code license gives no right to use anyone's voice and does not replace consent. The Qwen3-TTS model is Apache 2.0.

## Credits

Conceived and created by **Mestre Anderson Menezes de Oliveira**, of [Afirma](https://afirma.cc), to give back to the community the knowledge received from friends, collaborators and everyone who shares technology generously. With the support of Bellete Ritter de Oliveira.

If this skill helped you, leave a ⭐ and cite: *Local Voice Cloning — Mestre Anderson Menezes de Oliveira · afirma.cc*.
