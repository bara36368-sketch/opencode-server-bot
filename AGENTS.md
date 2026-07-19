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

## Next Steps
1. Finish `/skills` marketplace integration (if any backend wiring is needed)
2. Test-run: `python runner.py` or `python opencode_bot.py` (single instance)
3. Move API keys to environment variables
4. Repo catalog has 90 repos total — 9 reviewed & integrated, 35 pending review, 45 to ADD

## Key Commands
Start bot: `python opencode_bot.py`
Start web: `python web_gateway.py`
Start all: `python runner.py`
Health check: `curl http://127.0.0.1:4357/api/providers`
