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
| `free_model_watcher.py` | Free-model watcher — polls OpenRouter/OpenCode Zen/models.dev catalogs every 4h, announces NEW limited-time free models to all Telegram chats, expiry alerts when free window ends. **Adoption engine: probes then auto-registers openrouter free models into providers.json as `free_<name>`; auto-retires when expired.** CLI: `python runner.py freemodels [dry]`, digest: `python runner.py digest [dry]` |
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
3. NEVER integration-test destructive paths (deploy guard rollback, kill_all, git reset) against the live repo with uncommitted changes — mock subprocess git calls too, or commit first. (Incident 2026-08-23: guard test's real `git reset --hard` wiped its own uncommitted implementation; restored in 189a386.)

## Free Model System (added 2026-08-23)
- Watcher polls OpenRouter + OpenCode Zen + models.dev public catalogs every 4h (FREE_MODEL_CHECK_INTERVAL).
- NEW free model → probe via OPENROUTER_KEY → adopt into providers.json as `free_<slug>` → broadcast alert with "/provider <name>" hint to all chats.
- Expired free model (gone >2 check cycles) → retire adopted provider → broadcast "FREE MODEL ENDED" with window length.
- State in freemodels_state.json: seen/expired/adopted — restarts never re-announce.
- `/freemodels` Telegram command: top tracked models by context, ✅ marks adopted ones with /provider names.
- Daily owner digest at DIGEST_HOUR (default 8am): uptime, per-proc health+RAM, restart counts, free-model tracker status, recent crashes.
- Live-verified: stealth/ox-alpha probed OK (1.7s), adopted as `free_ox_alpha`, visible in providers.json.

## Runner Upgrade Pack v4 (added 2026-08-23) — see RUNNER_IDEAS.md for the full 20-idea doc
1. Adaptive cadence — loop sleeps 5s when unstable (recent restart / web unhealthy), normal 15s when calm (`_adaptive_sleep`).
2. Deploy guard auto-rollback — after any bot git update, 600s observation window; ≥3 bot crashes in it → `git reset --hard` to pre-pull SHA + kill_all + Telegram alert (`_deploy_guard_*`). Env: RUNNER_DEPLOY_GUARD_S, RUNNER_DEPLOY_GUARD_MAX_CRASHES.
3. Stderr sentry — tails per-proc .stderr incrementally; error-line bursts (≥12, Traceback/CRITICAL/FATAL/MemoryError) notify once per cooldown; every error line hashed into a normalized signature and written to proc-ledger as error_signature events (`_stderr_sentry_tick`).
4. Disk guard + nightly maintenance — hourly disk check prunes fleet_snapshots >14d, video_cache/* + stderr rotations >7d; nightly deep pass at MAINT_HOUR (default 4am); LOW DISK alert under RUNNER_DISK_MIN_FREE_GB (default 2GB) (`_disk_and_maintenance_tick`).
5. Heartbeat + doctor — runner writes runner_heartbeat.json every loop (dead-man-switch for external watchers); `python runner.py doctor` = one-shot triage (heartbeat age, procs, disk, crash history, freemodels, ctrl API liveness).
6. Hung-watchdog lite — web ALIVE but failing health checks 20 consecutive ticks → auto-restart + alert (`_hung_watchdog_tick`, RUNNER_HUNG_STREAK).
7. Telegram remote control (bot side) — owner/admin only: /rstatus, /rrestart <proc>, /rlogs [filter], /rdisable <proc>, /renable <proc> via ctrl API :8431 (RUNNER_CTRL_TOKEN).
8. Jittered backoff (#15) — crash restart delays get ±20% jitter, no thundering-herd on shared hosts.
9. Metrics persistence (#9) — one compact fleet row/minute → metrics.jsonl (self-rotating), baselines for digest/admin.
10. Snapshot diff in digest (#13) — daily digest reports proc state changes + free models gained/lost vs last snapshot.
11. Incidents CLI (#17) — `python runner.py incidents [YYYY-MM-DD]` renders readable episode timeline from proc-ledger.jsonl.
12. Graceful degradation (#16) — host RAM >= RUNNER_DEGRADE_RAM_PCT (92%) pauses heavy optional procs (RUNNER_DEGRADABLE = cyberdeck,dma), auto-resumes <= 85%; digest shows DEGRADED banner (`_degrade_tick`).
13. SLO burn tracking (#10) — daily web availability ratio persisted to slo_daily.json; digest line amber under RUNNER_SLO_TARGET (default 99%) (`_slo_tick`, `_slo_digest_line`).
14. Shared provider circuits (#12) — bots append failures to provider_health.json (throttled); ctrl GET /api/provider_health exposes fails_1h fleet-wide; hook: ProviderGateway.record fail path (`_report_provider_failure_shared`, `_record_provider_failure`).
- All tested with mocked-destructive paths (rule 3): guard trips+notifies+expires cleanly, sentry detects bursts, doctor runs standalone, jitter bounds 0.8x–1.2x verified across strikes 1–8, degrade on/off cycle works, SLO line renders, shared circuit file round-trips.
- Runner ideas scorecard: 17/20 implemented. Remaining: #8 dependency-aware startup ordering, #14 explicit runner.py self-validation pre-restart, #19 config hot-reload for env constants, #20 committed pytest suite (mock tests exist only in session history).

## Next Steps
1. Restart runner.py so all fixes take effect
2. Test new features: /history, /archive, /video
3. Move API keys from setenv.sh/providers.json to env vars

## Key Commands
Start bot: `python opencode_bot.py`
Start web: `python web_gateway.py`
Start all: `python runner.py`
Health check: `curl http://127.0.0.1:4357/api/providers`
