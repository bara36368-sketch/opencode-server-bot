# opencode-server-bot

A Telegram AI bot stack that runs on Android (Termux) with two engines:

- **CyberdeckBot** (`cyberdeck_bot.py`) — cyberdeck/electronics builder + unified coding AI
- **General AI bot** (`opencode_bot.py`) — general-purpose AI chat with 20+ providers

Managed by `runner.py` (auto-pull, crash supervision, local model switching).

## 🌐 OMNI Gateway — dashboard/manager (`omni_gateway.py`)

**One keyring. One endpoint. Every free model, ranked.**

```bash
python runner.py          # omni auto-starts on http://localhost:4455
```

| URL | What |
|---|---|
| `http://localhost:4455` | Dashboard — paste keys, ranked FREE model table |
| `http://localhost:4455/chat` | Chat test UI — talk to any ranked model |

- Paste ANY provider key → prefix auto-detects provider (`gsk_`=Groq, `sk-or-`=OpenRouter, `nvapi-`=NVIDIA, `AIza`=Gemini, `csk-`=Cerebras, `hf_`=HF...) → live validation
- Scanner extracts every FREE model ($0/$0, `:free`, free-by-design services) and ranks by context + modalities + speed
- **Unified OpenAI-compatible endpoint**: point any app at `http://localhost:4455/v1`
- Ranked auto-fallback: requested model down → walks the ranking until one answers

Wired into the whole stack:
- Telegram bots: `/provider omni` (model `auto` = gateway picks best ranked)
- opencode CLI: `python opencode.py omni` → then `opencode run --model omni/auto "<prompt>"`

## Features

### Cyberdeck Builder
Design, build, and optimize portable custom computers (Raspberry Pi, Orange Pi, displays, power systems, enclosures, PCBs). Commands include `/cyberdeck`, `/build`, `/bom`, `/compat`, `/tutorial`, `/3d`, `/pcb`, `/cables`, plus hardware catalogs (`/hardware`, `/modules`, `/lilpcb`).

### Unified Coding AI (free)
One coding brain routed across **every** provider — paid keys + free tiers — smartest-first with automatic fallback:

| Command | What it does |
|---|---|
| `/coder on|off` | Persistent coding mode (all chat routes through the coding chain) |
| `/code <task>` | One-shot coding via the smartest available model, auto-fallback |
| `/codeall <task>` | Asks the top 3 coding models in parallel for comparison |

The chain is configurable via the `CODER_CHAIN` env var. Default (free):

```
kimi,groq,gemini,openrouter,cerebras,nvidia,blackbox,androidllm
```

- `kimi` = `moonshotai/kimi-k3` (free on OpenRouter) — top coder
- `nvidia` = `nvidia/llama-3.3-nemotron-super-49b-v1`
- `androidllm` = local model on the phone (offline/private, last resort)

### Switchable AI Brains
`/brain <name>` — cyberdeck personas: `default`, `obsidian` (persistent Obsidian memory vault), `writer`, `coder`, `coding`, `hacker`, `researcher`.

### Local AI (androidllm)
Runs a local LLM on the phone via `androidllm-serve`. One model at a time; switching writes state and restarts the server.

- `/model` — list local models (sharded/serving status)
- `/model <id>` — switch (auto-shards in the background if needed)
- Recommended: `qwen15`, `smollm2`, `qwen3`

### Providers
Groq, Gemini, Kimi K3, DeepSeek, Mistral, Cerebras, NVIDIA (Nemotron 49B), Blackbox, OpenRouter, Together, Fireworks, plus local routers (9router, omniRoute, vansRouter, bitRouter). Switch anytime with `/provider <name>`.

## Setup (Termux)

```bash
pkg install git python nodejs -y
git clone https://github.com/bara36368-sketch/opencode-server-bot
cd opencode-server-bot
# copy setenv.sh.example to setenv.sh (or create from template)
#   - set TELEGRAM_BOT_TOKEN and OWNER_ID (required)
#   - add API keys for providers you want
source setenv.sh
python runner.py
```

Auto-start at boot (optional): add `cd ~/opencode-server-bot && source setenv.sh && python runner.py` to `~/.bashrc`.

## Configuration

Environment variables live in `setenv.sh` (gitignored — keys never leave the device):

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `OWNER_ID` | Your Telegram user ID |
| `GROQ_KEY`, `GEMINI_KEY`, `OPENROUTER_KEY` ... | Provider API keys |
| `CODER_CHAIN` | Ordered coding-AI provider chain |
| `ANDROIDLLM_DIR`, `ANDROIDLLM_MODEL`, `ANDROIDLLM_PORT` | Local model settings |

## Notes

- `setenv.sh` is intentionally gitignored so API keys are never committed.
- Free models are subject to provider rate limits; the coding chain falls back automatically.
