# AI Skill — Local Voice Cloning

[Português](README.md) · **English** · [Español](README.es.md)

![version](https://img.shields.io/badge/version-0.3.0-blue)
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

## Use in 5 steps

```bash
# 1. Capture: see the reading text (covers the sounds of the language) and tips, record and check
voice-clone record --guide --language English
voice-clone record --output my-voice.wav --language English   # or record on your phone
voice-clone record --analyze my-voice.wav                      # length, noise, clipping: says what to fix

# 2. Profile (with signed consent)
voice-clone prepare --input my-voice.wav --profile-id my-voice --consent consent.txt --language English
P=~/.local/share/voice-clone/profiles/my-voice

# 3. Pronunciation: find the hard words in the script and learn how YOUR voice should say them
voice-clone pronounce --profile $P --script script.txt
voice-clone pronounce --profile $P --script script.txt --learn-script --output-dir learn/

# 4. Narration: listens to every take and keeps the one with your pitch and the right words
voice-clone narrate --profile $P --script script.txt --output-dir narration/

# 5. Listen to the "to_review" lines (narration/narration-report.json) and redo only those
voice-clone narrate --profile $P --script script.txt --output-dir narration/ --only 3 7
```

## Saying it right: how the skill handles pronunciation

1. **Base dictionary per language** (pt, en, es) with the words the model gets wrong most. Your profile dictionary wins.
2. **Automatic rules:** money (`$19.99` → "nineteen dollars and ninety-nine cents"), `25%`, numbers, acronyms, websites (`afirma.cc` → "afirma dot see see") and e-mails.
3. **Find hard words** in the script before recording (`pronounce --script`).
4. **Learn in your voice** (`pronounce --learn word` or `--learn-script`): the skill says the word in a few spellings, listens with Whisper and saves the one that was understood.
5. **Every take is listened to** during narration: a swapped or swallowed word makes the skill try another take; if none comes out clean, the line goes to `to_review` with the suspect words.
6. **Preview:** `pronounce --text "..."` shows exactly what will be spoken. Manual fix: `pronounce --add "GUI=gooey"`.

Subtitles always keep the correct spelling.

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
