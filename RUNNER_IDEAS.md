# RUNNER_IDEAS.md — 20 baked upgrade ideas (researched 2026-08-23)

Sources: PM2 restart strategies, systemd/supervisord patterns, KubeGuardian auto-remediation,
SLO burn-rate alerting, deploy auto-rollback playbooks, AIOps multi-signal correlation.

1. **Adaptive check cadence.** The main loop sleeps at a fixed 15s regardless of fleet state.
   Real supervisors breathe: poll fast (3-5s) when any process is unstable or restarting, slow
   (30-60s) when everything has been healthy for a while. This catches crash-loops earlier while
   cutting idle CPU/battery burn — important because this runner runs on phones and laptops alike.
   Implementation: dynamic sleep computed from recent restart events and health-check failures,
   with hysteresis so it doesn't flap between speeds.

2. **Deploy guard with auto-rollback (auto-bisect).** The runner auto-pulls git updates. If a pull
   introduces a startup-crashing change, the current backoff/storm guards prevent infinite loops
   but leave the fleet DOWN until a human notices. KubeGuardian-style remediation says: correlate
   failure with the last change event and revert it. After any git_update that changed hashes, arm
   a 10-minute observation window; if the affected process accumulates more than N crashes inside
   it, `git reset --hard` back to the pre-pull commit, restart, and notify the owner. This converts
   "bad push takes down the bot for hours" into "bad push costs 10 minutes".

3. **Stderr error-burst detection.** Restarts are not the only signal — a process can be up yet
   spewing tracebacks (provider 429 storms, JSON decode errors). Each loop, tail the per-process
   .stderr files and count error-pattern lines (Traceback, CRITICAL, unhandled) in a sliding
   window. Cross a threshold → notify owner once per cooldown with a short excerpt. This is the
   cheap version of Graylog-style anomaly alerting and needs no new infrastructure.

4. **New-error-signature alerts.** Beyond bursts, keep a rolling hash set of normalized error
   lines (strip numbers/hex/paths). When an unseen signature appears, log it to a
   new_errors.jsonl and include it in the daily digest. Recurring-but-known errors stay quiet;
   genuinely novel failures get surfaced. Sentry's stickiest feature, reimplemented in ~40 lines.

5. **Disk guard.** Log rotation exists per-file, but fleet_snapshots/, video_cache/, and JSON
   state files grow forever. Add a periodic du-based check: if repo dir exceeds a cap or the
   volume's free space drops under a floor, prune oldest snapshots/caches, force log rotation,
   and notify before things hit ENOSPC. OOM guards exist; disk guards are the missing twin.

6. **Dead-man-switch heartbeat.** The runner itself has no supervisor above it. Write a
   heartbeat file (timestamp) every main-loop iteration. Any external cron/watcher (or the
   phone's Termux:Boot script) can check heartbeat age and hard-restart the runner if it stalls.
   Also expose `runner.py doctor`: one-shot diagnostics (heartbeat age, proc states, port
   listeners, disk, recent crashes) for manual triage without reading five log files.

7. **Hung-process watchdog.** Alive-but-wedged processes pass `poll() is None` forever. Track
   CPU-time deltas per supervised pid (psutil already used); a process whose CPU delta is zero
   across multiple windows WHILE its service health check fails is probably hung → notify, then
   optionally kill_one + restart after a second confirmation window. Distinguishes "crashed"
   from "zombie", which today are invisible.

8. **Dependency-aware startup ordering.** PROCESSES start in dict order with fixed waits. Give
   each rule an optional `after` list and `ready_probe` (URL or file). Start web only after bot's
   lockfile exists, mcp after web answers :8430, etc. Removes race-y startup flakiness documented
   in past crash logs, and makes adding future services safe.

9. **Metrics history persistence.** _health_rows keeps 120 in-memory rows that die on restart.
   Persist compact per-minute rows (ts, proc, rss_mb, cpu, alive) to metrics.jsonl with its own
   rotation. Enables sparklines in /admin, trend graphs in digests, and gives idea #3/#7 real
   baselines instead of single-window guesses.

10. **Per-process SLO burn tracking.** Define availability as "% of health checks OK per day".
    Track daily success ratio per process; when the projected burn exceeds budget (e.g. >1%
    downtime), escalate notification severity in digest. Turns vague "it crashed a lot" into a
    number you can defend, borrowed from SRE error-budget practice.

11. **Maintenance window.** Nightly low-traffic hour: rotate all logs, vacuum oversized JSON
    state (rewrite pretty→compact), prune fleet_snapshots >14 days, run key_backup.verify,
    optionally py_compile every module as a smoke test. One coordinated janitor instead of
    scattered housekeeping.

12. **Shared provider-circuit file.** Both bots maintain separate provider failure memories.
    Have runner aggregate 429/failure reports written by bots to provider_health.json and expose
    them via the ctrl API, so /codeall routing can skip providers another process just saw fail.
    Fleet-wide circuit breaker instead of per-process amnesia.

13. **Fleet-snapshot diffing.** _fleet_snapshot_daily writes files nobody reads. Make the next
    day's snapshot diff against yesterday's (new crash types, RAM drift, restart counts, free
    models gained/lost) and prepend a CHANGELOG section to the digest. Snapshots become a story,
    not an archive.

14. **Runner self-validation before self-restart.** When the runner updates its own repo, it
    should py_compile itself + free_model_watcher + critical imports BEFORE killing children;
    on failure, refuse the update and alert. Today a broken runner.py push would brick the whole
    supervision layer silently.

15. **Jittered backoff.** All restart delays are deterministic. On a shared host, synchronized
    retries cause thundering-herd spikes. Add ±20% jitter to BACKOFF_BASE growth and storm holds.
    Trivial change, standard practice (already used by retry libraries everywhere).

16. **Graceful degradation mode.** Under sustained memory pressure (host-level), automatically
    enter degraded mode: stop heaviest optional processes (cyberdeck, dma) per rules priority,
    notify owner, resume when pressure clears for M minutes. Extends the existing androidllm
    OOM-downgrade concept fleet-wide instead of just one process.

17. **Incident timeline generator.** proc-ledger.jsonl already records lifecycle events but
    nothing consumes them. Add `runner.py incidents [date]`: group ledger rows into episodes
    (crash→restarts→recovery), print/digest a readable timeline with durations and exit codes.
    Postmortems become `python runner.py incidents yesterday`.

18. **Telegram remote-control bridge.** The ctrl API (:8431) is powerful but needs curl. Wire
    owner-only bot commands (/rstatus, /rrestart <name>, /rlogs <name> [n], /rdigest) through
    runner_connector to the local ctrl API. Owner manages the entire fleet from the phone chat
    where they already live — no SSH, no laptop.

19. **Config hot-reload everywhere.** Rules reload by mtime, but CHECK_INTERVAL, NOTIFY_COOLDOWN,
    DIGEST_HOUR, watcher intervals are import-time constants. Move reads to a tiny config()
    helper re-reading env/file each use (cached by mtime). Owners tune behavior live without
    restarting the supervisor — which matters precisely when things are on fire.

20. **Self-test suite for the runner.** No tests exist for the most critical file in the repo.
    Add test_runner.py: fake Popen objects exercising backoff math, storm guard, exit policies,
    digest builder, rollback decision logic, watcher state machine. Even 15 unit tests would have
    caught several past regressions listed in AGENTS.md and makes every idea above safe to ship.

## Implementation picks for this session (highest value ÷ risk)
Adaptive cadence (#1), deploy-guard auto-rollback (#2), stderr burst + signature detection
(#3/#4), disk guard (#5), heartbeat + doctor (#6), hung-watchdog lite (#7), nightly maintenance
(#11), Telegram remote control (#18). Deferred: #8-#17 need larger refactors or new data flows;
documented here for next sessions.
