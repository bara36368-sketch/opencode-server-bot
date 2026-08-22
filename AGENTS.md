# opencode-server-bot — Project Memory

## Overview
AI server running on a phone (4GB RAM / Helio G85). All AI calls go to cloud APIs — no local models.
Three processes managed by `runner.py` with auto-restart, health checks, and file-change detection.

## Architecture
```
runner.py (process manager)
├── opencode_bot.py  — Telegram bot (4031 lines, 83 commands, session/memory/scheduler/provider gateway)
├── web_gateway.py   — Flask HTTP gateway (1738 lines, 23 routes, MCP tools, workflow builder)
└── whatsapp_bot.py  — WhatsApp bot
```

## Key Files
| File | Purpose |
|---|---|
| `runner.py` | Process manager — monitors 3 processes, health checks every 30s, file hash change detection, git auto-update |
| `free_model_watcher.py` | Free-model watcher — polls OpenRouter/OpenCode Zen/models.dev catalogs every 4h, announces NEW limited-time free models to all Telegram chats, expiry alerts when free window ends. CLI: `python runner.py freemodels [dry]` |
| `opencode_bot.py` | Telegram bot — 4031 lines, polling loop, 18 API providers via smart_call(), agent teams, memory, scheduler, 83 commands |
| `web_gateway.py` | Flask gateway — 1738 lines, chat UI, workflow builder, MCP server, 23 routes, /skills marketplace, 15 provider "roles" (Strategist, Researcher, etc.) |
| `agents.json` | 189 agent definitions with prompts |
| `providers.json` | 18 API provider configs (keys in plaintext — security risk) |
| `mods.json` | Telegram mod/admin chat IDs |
| `whatsapp/` | WhatsApp bot JS/scripts |

## Hardware Constraint
- 4GB RAM, Helio G85 (phone)
- **No local AI models** — everything goes through cloud APIs
- lightweight = uses local Python (no AI inference), not "free API"

## What Was Done (Session 2026-07-19)

### Added 16 agents to agents.json
skyvern, browser-use, openhands-agent, copilot-kit, goose-agent, agency-agents, pocket-tts, claude-video, system-prompts-expert, graphify, code-review-graph, ai-engineering-mentor, cube-analytics, penpot-designer, lobehub-chat, cognee

### Added 5 commands to opencode_bot.py
- `/skills` — list skills from repo catalog
- `/pocket-tts` — text-to-speech (voices: alloy/echo/fable/nova/shimmer/ash/coral/sage)
- `/video-analyze` — vision-based video content analysis
- `/prompt-analyze` — inspect system prompts for structure/guardrails
- `/kgraph` — extract entities/relationships as knowledge graph

### Added 8 MCP tools + /skills page to web_gateway.py
- analyze_video, text_to_speech, analyze_prompt, extract_knowledge_graph
- code_review_graph, list_skills, cognee_memory
- Full HTML marketplace UI at `/skills`, JSON API at `/api/skills`
- Added to nav bar (Chat, Workflows, Admin, Skills)

### Added 2 providers to providers.json
- zenmux (Grok 4.5 free)
- zyloo (Kimi K2)

### Security Concern
`providers.json` has ~15 hardcoded API keys. Move to env vars / `.env`.

## What Was Done (Session 2026-07-19 — Part 2: Bugfix, Security, Features)

### Runtime Bugfixes
- ALL open() calls missing encoding=utf-8 fixed across opencode_bot.py (48), web_gateway.py (4), runner.py (1), bot_features.py (12)
- web_gateway.py analyze_prompt NameError: 'and k' variable-as-iterable
- tg() triple json.parse: cached in variable
- send() dedup returning None instead of {ok: true}
- announce_update first-install skip: handles empty old_ver
- auto_version_checker: handles unknown current_ver
- /restore zip slip path traversal: os.path.realpath prefix check
- ProviderGateway.execute() .lower() crash: isinstance guard
- runner.py subprocess encoding: utf-8 for git + netstat
- json import missing at module level (_security_check crashed on import)

### Security Hardening
- /run restricted to owner/admin (5000 char limit)
- /fetch restricted to owner/admin (http/https only)
- /plugin load restricted to owner only
- SSRF via fetch_url: _is_private_ip() blocks private ranges + redirect check
- Python sandbox escape: type removed from builtins
- Startup security scanner: warns on hardcoded API keys in setenv.sh/providers.json
- Rate limiting: /announce (2/5min), /backup (2/hour), /restore (2/hour)

### Conversation History System
- conversations.json archive with auto-increment IDs per chat
- /archive — manually archive current session
- /history — list last 20 archived conversations
- /view <id> — show last 30 messages of archived conversation
- /change <id> /resume <id> — switch to archived conversation
- Auto-archive on /clear, 30-min inactivity gap, /change

### Video Creator Agent (OpenMontage)
- video-creator agent with full OpenMontage reverse-engineered knowledge: 12 pipelines, 52+ tools, installation guide, agent orchestration contract, pipeline state machine, style playbooks, quality gates
- /video [prompt] — shortcut to enter video-creator agent

## Workflow Rules
1. After every update, auto git commit + git push. (Set by user 2026-07-19)
2. Version auto-bumps on every git push — no need to edit version.json manually. Changelog is generated from git log messages. (Set by user 2026-07-19)

## Next Steps
1. Restart runner.py so all fixes take effect
2. Test new features: /history, /archive, /video
3. Move API keys from setenv.sh/providers.json to env vars

## Key Commands
Start bot: `python opencode_bot.py`
Start web: `python web_gateway.py`
Start all: `python runner.py`
Health check: `curl http://127.0.0.1:4357/api/providers`
