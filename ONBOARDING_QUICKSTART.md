# QUICKSTART — For the Replacement Model (READ THIS FIRST, 60 seconds)

> You are taking over for a previous AI that ran out of tokens. Do these steps IN ORDER. Full details: `MODEL_HANDOFF.md`.

## Step 0 — Ground yourself
- Project: **opencode-server-bot** — a Telegram bot for building cyberdecks (DIY portable computers). All AI calls go to cloud APIs.
- The bot we care about is `cyberdeck_bot.py` + its brain `cyberdeck_agent.py`. Both are version **7.1.0**.
- Ignore `opencode_bot.py` (different, general-purpose bot).

## Step 1 — Read these two files fully before changing anything
```
cyberdeck_agent.py   (databases + advisor classes, ~10,482 lines)
cyberdeck_bot.py     (Telegram glue, commands, ~3,710 lines)
```
Start near the bottom of each (the newest work) and skim the `/start` help text.

## Step 2 — Know the state (already done, do NOT redo)
- 8 v7.1 features shipped: `/localai`, `/hotswap`, `/ortho`, `/offgridstack`, `/features`, `/character`, `/scavenge`, `/newhardware`.
- Each = databases (dicts in agent) + class of static methods + bot handler + dispatch line + registration in `load_cyberdeck()`.
- All tested: files compile, 132 classes load, 19 agent + 10 handler smoke tests passed.
- `FREE_MODELS_OPENCODE.md` (free opencode models) and `MODEL_HANDOFF.md` (full details) exist.

## Step 3 — Pending work (only if asked)
1. Bot needs a **restart** for v7.1 to go live (user runs `python cyberdeck_bot.py` or `python runner.py`).
2. Optional: add `GOOGLE_API_KEY` for Gemini free tier; add v7.1 features to `/status` output.

## Step 4 — Conventions (violating these breaks the bot)
1. **ASCII-safe output strings only** (`->` not `→`, `[OK]` not `✓`). Windows console is cp1252; unicode crashes or shows `�`.
2. New feature recipe:
   - agent: add DB dicts + class of `@staticmethod`s (must have `overview()`), update `__all__`
   - bot: `handle_XXX()` wrapped in try/except, dispatch `elif cmd == "/xxx"` in `handle_command()`, register in `load_cyberdeck()`
   - bump BOTH `VERSION` (agent) and `BOT_VERSION` (bot), update `/start` help + `NEXT_UPDATE_IDEAS.md`
3. Bump the version on every feature release.
4. Do NOT commit/push unless the user explicitly asks.

## Step 5 — Verify your changes
```powershell
python -m py_compile cyberdeck_agent.py; python -m py_compile cyberdeck_bot.py
```
Then import both modules and confirm `load_cyberdeck()` registers the classes (expect "132 classes").

## Golden rule
When unsure, ask the user. Never guess at databases, commands, or APIs. Full history + line numbers: `MODEL_HANDOFF.md`.
