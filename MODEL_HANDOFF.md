# MODEL HANDOFF — Read This First When Continuing

> **⚠️ SHORT ON TIME? Read `ONBOARDING_QUICKSTART.md` first (60 seconds) — it has the essential steps, then come back here for full detail.**

> **Purpose:** This is the replacement/handover document for the opencode **big-pickle** model session. When big-pickle's free tokens run out and you switch to another model, the new model should read this file to pick up exactly where the work left off. It documents: the project, the v7.1 update just shipped, the bot architecture, conventions, testing workflow, and the accumulated experience/context.
>
> **Switch command example:** `opencode tui --model opencode/gpt-5-nano` (see also `FREE_MODELS_OPENCODE.md` for the full free-model lineup).

---

## 1. What This Project Is

**opencode-server-bot** (`C:\Users\ARYASATYA\Desktop\opencode-server-bot`) — an AI server that runs **Telegram bots**. All AI calls go to cloud APIs. No local model inference.

Current process stack (from `AGENTS.md`, still valid):

```
runner.py (process manager — auto-restart, health checks)
  ├── opencode_bot.py   — Telegram bot (main one, ~2600+ lines, many commands)
  ├── cyberdeck_bot.py  — Telegram bot (Cyberdeck specialist, THE bot we just upgraded)
  ├── web_gateway.py    — Flask HTTP gateway
  └── whatsapp_bot.py   — WhatsApp bot
```

**Cyberdeck bot = a Telegram bot that is a cyberdeck (DIY portable computer) builder/advisor.** Users type `/commands` and get builds, component recs, tutorials, offline-AI plans, etc.

**IMPORTANT distinction:** There are TWO "opencode" files:
- `opencode_bot.py` — the general-purpose bot
- `cyberdeck_bot.py` — the cyberdeck bot (**this is where all recent v7.1 work lives**)

---

## 2. Key Files

| File | Role | Version |
|---|---|---|
| `cyberdeck_agent.py` | Pure-Python "brain" — databases (dicts) + advisor classes + ObsidianBrain | **v7.1.0** (~10,482 lines) |
| `cyberdeck_bot.py` | Telegram glue — polling loop, `load_cyberdeck()`, providers, brains, ~90 command handlers | **v7.1.0** (~3,710 lines) |
| `providers.json` | ~26 provider configs (groq, nvidia, gemini, openrouter, routers, etc.) | — |
| `setenv.sh` / `.env` | Raw API keys + VANSROUTER_URL/MODEL/KEY env vars | — |
| `NEXT_UPDATE_IDEAS.md` | Feature roadmap + research log | updated for v7.1 |
| `FREE_MODELS_OPENCODE.md` | Free higher-tier models for opencode (created this session) | new |
| `TRENDING_FEATURES_2026.md` | 2026 community trend research | — |
| `AGENTS.md` | Project memory (older, general bot focus) | — |
| `CYBERDECK_BUILD_LIST.md` | Community build catalog (auto-appendable) | — |
| `Obsidian vault` | `C:\Users\ARYASATYA\Documents\obsidian-vaults\CyberdeckBrain\AgentMemory` — ObsidianBrain memory notes | — |

---

## 3. Architecture — How the Cyberdeck Bot Works

**Two-layer design:**

1. **`cyberdeck_agent.py`** = data + logic. Each feature is:
   - One or more **module-level dict "databases"** (e.g. `WRITERDECK_DISPLAYS`, `LOCAL_AI_BOARD_DATABASE`)
   - One **class of static methods** (e.g. `WriterDeckAdvisor`, `LocalAITuner`), each method returns a **string** (HTML-ish text with `<b>` tags, sent to Telegram)

2. **`cyberdeck_bot.py`** = wiring. On startup, `load_cyberdeck()` (line 128) imports the agent and registers classes + databases into a global `cd_classes` dict. Command dispatch lives in `handle_command()` (line 492). Each command has an `async def handle_XXX(chat, uid, args)` that calls the agent class and `await send(chat, result)`.

**The pattern for every command (v7.0 + v7.1):**
- Agent class: `@staticmethod def overview() -> str` + one method per subcommand
- Bot handler: parse `args`, branch on first word, call class method, wrap in `try/except` → `await send(chat, f"Xxx error: {e}")`
- Dispatch line in `handle_command()`: `elif cmd == "/xxx": await handle_xxx(chat, uid, args)`
- Registration: add class + database names to `load_cyberdeck()` blocks, add class/db names to agent `__all__`

---

## 4. The v7.1 Update (JUST COMPLETED — session 2026-07-31)

Bumped `cyberdeck_bot.py` `BOT_VERSION = "7.1.0"` (line 20) and `cyberdeck_agent.py` `VERSION = "7.1.0"`. Added **8 features**, each with databases + class in the agent and a handler + dispatch in the bot. All compile + smoke-tested (details in section 7).

### Feature list (commands + what they do)

| # | Command | Class (agent) | Databases | Subcommands |
|---|---|---|---|---|
| 1 | `/localai` | `LocalAITuner` | `LOCAL_AI_BOARD_DATABASE`, `LOCAL_AI_MODEL_DATABASE`, `BUDGET_TIERS_LOCALAI` | `recommend <$>` | `boards` | `models` | `npu` | `estimate <board> <model>` |
| 2 | `/hotswap` | `HotSwapPlanner` | `HOTSWAP_COMPONENT_DATABASE`, `HOTSWAP_REFERENCE_BUILDS` | `design <board> <power_w>` | `parts` | `builds` | `guide` |
| 3 | `/ortho` | `OrthoAdvisor` | `ORTHO_KEYBOARD_DATABASE`, `ORTHO_FIRMWARE_GUIDE` | `recommend <type>` | `firmware <kb>` | `wiring` | `<keyboard>` |
| 4 | `/offgridstack` | `OffgridStackPlanner` | `OFFGRID_STACK_COMPONENTS`, `OFFGRID_REFERENCE_BUILD` | `plan <$>` | `components` | `dtn` | `reference` |
| 5 | `/features` | `CommunityFeatureBoard` | `COMMUNITY_FEATURE_DATABASE` | `top` | `recommend <type>` | (list) |
| 6 | `/character` | `CharacterBuilder` | `CHARACTER_TEMPLATES` | `<minimal\|maximal\|field>` | `compare` | `list` |
| 7 | `/scavenge` | `ScavengePlanner` | `SCAVENGE_SOURCES`, `SCAVENGE_BUILD_PLAN` | `sources` | `tips` | `<bootstrap\|mech_focus\|media_screen>` |
| 8 | `/newhardware` | `NewHardwareRadar` | `NEW_HARDWARE_2026` | `detail <name>` | `compare <a> <b>` | (list) |

### Where things live (line markers as of this session)

- Agent: the entire v7.1 block was inserted **before the `# SINGLETON` section** (after `BuildSharing`). `__all__` updated to export the 8 classes + 15 databases.
- Bot: 8 `async def handle_*` handlers inserted **before `# Main Loop`** (handler `handle_localai` at ~3343, `handle_newhardware` at ~3552). 8 dispatch `elif cmd == "/xxx"` lines added in `handle_command()` right after `/share`. `load_cyberdeck()` gained a "v7.1 classes" + "v7.1 databases" registration block (total now **132 classes** loaded).
- `/start` help: added a `<b>v7.1 New Features:</b>` section listing all 8 commands.
- `NEXT_UPDATE_IDEAS.md`: added a `## v7.1 Features (IMPLEMENTED)` section at top.

### Content notes (what the data is grounded in)
These were built from **2026 web research**, not invented:
- `/localai` uses 2026 SBC LLM benchmark tiers (Pi 5 + AI HAT+ Hailo 8L/8H "just works"; RK3588 NPU is the "NPU tax" trap; Radxa Rock 5B 32GB is the only SBC that runs Llama 3 8B usable). Verified against sanj.dev's 2026 SBC LLM battle + community reports.
- `/hotswap` references HALGRID P-1 (Hackster.io, 12h/26,800mAh) and DINODECK-2026 (PiSugar 3 I2C telemetry), the recurring 120s supercap UPS pattern.
- `/ortho` covers the exploding ortho/split trend: Corne, Helix, Lily58, Ferris Sweep, Sofle, Cantor, Planck, Preonic, Air40, Gherkin + QMK/VIA/VIAL/ZMK firmware + hand-wiring + Miryoku.
- `/offgridstack` is the sarogamedev CyberDeck (113★ GitHub) "offline survival platform" pattern: DTN bundle protocol, Kiwix ZIM + RAG, offline maps, P2P model sharing, mDNS/UDP beacon.
- `/features` = live voted requests from `cyberdeck.ing` feature board (multi-layer macros 87, slide-out keyboard 78, more USB 71, rear camera 64, speech-to-text 52...) + r/cyberDeck wishlist.
- `/character` maps the 2026 minimal↔maximal spectrum (Altoids-tin Pi Zero 2W + Gherkin ↔ M.A.S.K. lunchbox with oscilloscope/HackRF/projector).
- `/scavenge` = community-standard thrift/e-waste/dollar-store sourcing.
- `/newhardware` = 2026 arrivals: Pi 500+, Radxa Rock 5B/5 ITX 32GB, AI HAT+, SiSpeed Lichee Console 4A (RISC-V), x86 12W i5-class boards.

---

## 5. Provider + Brain Systems (added in an earlier session — still live, don't break them)

### Provider system (in `cyberdeck_bot.py`)
- `load_providers()` (line 249) merges `setenv.sh`/`.env` + `providers.json` (~15 usable providers loaded). Skips configs marked `set-via-env-var`/`not configured`.
- Router providers: `9router` (`http://localhost:20128/v1/chat/completions`), `bitrouter` (`http://127.0.0.1:4356/...`), `vansrouter`, `omniroute`.
- `ROUTER_CHAIN = ["9router", "vansrouter", "bitrouter", "omniroute"]` (line 322).
- **Per-user provider switching:** `_user_provider = {}` (line 323), `_get_provider_for(uid)` (line 330) — per-user override wins over global. `call_ai()` uses it. Commands: `/provider`, `/provider routers`, `/provider test <name>`, `/providers`.
- `_current_uid` is set at the top of `handle_command` and in the free-chat branch of the main loop.

### Brain system
- `BRAINS` dict (line 448): `default`, `obsidian` (`memory:True`, `learn:True`), `writer`, `coder`, `hacker`, `researcher`. Per-user: `_user_brain = {}` (line 486).
- `_brain_system(uid)` (line 376) injects the persona (and Obsidian memory context) as the session[0] system prompt.
- `_obsidian_memory_context(limit=8)` (line 390): lists recent notes from `OBSIDIAN_NOTES_DIR` (`~/Documents/obsidian-vaults/CyberdeckBrain/AgentMemory`), cached 60s in `_brain_memory_cache`.
- `_obsidian_learn(user_msg, reply)` (line 421): persists Telegram chats via `ObsidianBrain.learn_chat` (agent class at `cyberdeck_agent.py:1582`).
- Commands: `/brain`, `/brains`, `/status` reports active provider + brain.

---

## 6. Conventions & Hard-Won Gotchas (follow these!)

1. **Windows console is cp1252** — unicode chars (`→`, `—`, `⚠️`, `✓`, `·`, `→`) print as garbage (`�`) in the terminal AND can crash code. **Use ASCII-safe replacements** in all bot output: `->`, `-`, `[WARNING]`, `[OK]`, `+`. (The source files are UTF-8 and contain em-dashes in comments/docstrings — that's fine — but command output strings should avoid fancy unicode.)
2. **Databases are module-level dicts; classes are static-method string-returners.** Keep this pattern. Every class must have `overview()`.
3. **HTML-ish formatting** for Telegram: `<b>`, `<code>`, `<pre>` tags work; keep each output under ~4000 chars; join lines with `"\n".join(lines)`.
4. **Always wrap handlers in `try/except`** → `await send(chat, f"Xxx error: {e}")`.
5. **`load_cyberdeck()` registration is required** — adding a class to the agent is NOT enough; you must add it to `cd_classes` (and to `__all__` in the agent).
6. **`BRAINS`/memory block placement matters** — `CYBERDECK_SYSTEM` is defined mid-file, BEFORE command handlers. The module-level `BRAINS` dict must live AFTER it (a `NameError` was fixed earlier by relocating the block).
7. **Bot main loop:** free-chat messages create sessions `[system(_brain_system)]`, call `call_ai()`, and call `_obsidian_learn(text, reply)` when the active brain has `"learn": True`.
8. **Version discipline:** bump BOTH `BOT_VERSION` (bot) and `VERSION` (agent) on every feature release. Update `/start` help + `NEXT_UPDATE_IDEAS.md`.
9. **Never commit/push unless explicitly asked.** (Different from the general bot in AGENTS.md, which auto-commits on the user's instruction.)
10. **User workflow:** user asks → research the web for real 2026 data → implement → py_compile → smoke test (see section 7) → tell user to restart the bot.

---

## 7. Testing Workflow (used for v7.1, reuse it)

```powershell
# 1. Compile both files
python -m py_compile cyberdeck_agent.py; python -m py_compile cyberdeck_bot.py

# 2. Smoke-test the agent classes (all 8 + error paths) — drive with a Python heredoc
#    (import ca from cyberdeck_agent.py, call each class method, check no exceptions)

# 3. Verify registration:
#    import cyberdeck_bot; load_providers(); load_cyberdeck()
#    -> expect "Loaded 132 cyberdeck classes (...+v7.1)" and every new class in cd_classes

# 4. Handler test: monkeypatch cb.typing/cb.send to no-ops, call each handle_* with
#    valid + bogus args, confirm a string is produced for both.
```

**v7.1 results:** 19 agent smoke tests PASS, 10 handler tests PASS (incl. fallbacks), both files compile, registration confirms all 8 classes. Bot was NOT restarted — a restart is required for the changes to go live.

---

## 8. Current State & Next Steps

**DONE:**
- v7.1 fully implemented + tested (all 8 features above)
- `FREE_MODELS_OPENCODE.md` created (free higher-tier models: `opencode/gpt-5-nano` 5/5 permanently free, Google Gemini free tier, Groq Llama 3.3 70B, OpenRouter `:free`, GitHub Copilot `github/claude-sonnet-3-5`, NVIDIA NIM 550B already wired in config)
- `NEXT_UPDATE_IDEAS.md` updated with v7.1 spec
- Agent + bot docstrings/headers bumped to v7.1

**PENDING / TODO:**
1. **Restart `cyberdeck_bot.py`** (or `runner.py`) so v7.1 goes live. ← user-facing step
2. (Optional) Add `GOOGLE_API_KEY` to `~/.config/opencode/.env` to unlock Gemini free tier for opencode switching (see FREE_MODELS_OPENCODE.md)
3. Backlog ideas already gathered from research (not yet built): deeper `/localai` (benchmark tables per board), `/hotswap` CAD/3D mounts, `/ortho` wiring diagram SVG, `/offgridstack` software install scripts, e-paper/micro-display selector, P2P model-sharing implementation guide
4. Consider adding v7.1 features to the bot's `/status` (it already shows provider+brain; could add "v7.1 features loaded: 8")

---

## 9. Restart Commands (for the user)

```powershell
cd C:\Users\ARYASATYA\Desktop\opencode-server-bot
# single bot:
python cyberdeck_bot.py
# or all processes via the manager:
python runner.py
# health check for the general gateway:
curl http://127.0.0.1:4357/api/providers
```

---

## 10. Session Experience Log (for continuity)

- **Provider/Brains work** (earlier session): per-user provider switching + BRAINS system + Obsidian memory brain. Fixed a `NameError` by moving the `BRAINS` block after `CYBERDECK_SYSTEM`. Verified `/provider test groq` returned `OK / PONG` live; `_obsidian_learn` wrote a real note `Chat_ telegram_chat` into the Obsidian AgentMemory vault.
- **v7.1 work** (this session): implemented the 8 features above, all grounded in 2026 web research; all tests green.
- **Key lesson repeated across sessions:** console encoding (cp1252) breaks unicode output → always ASCII-safe in bot output strings.
- **Files touched in the v7.1 session:** `cyberdeck_agent.py` (v7.1 block + `__all__` + VERSION + docstring), `cyberdeck_bot.py` (version, load_cyberdeck, dispatch, 8 handlers, /start help, header), `NEXT_UPDATE_IDEAS.md`, `FREE_MODELS_OPENCODE.md` (new).
