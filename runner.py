import subprocess, time, os, sys, hashlib, glob, urllib.request, json, logging, threading, re as _re, traceback, socket, shutil, importlib as _importlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import androidllm_models
import free_model_watcher

for _lib in ["httpx", "httpcore", "urllib3", "chardet"]:
    logging.getLogger(_lib).setLevel(logging.WARNING)

DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(DIR, "runner.log")
CRASH_LOG = os.path.join(DIR, "crash.log")
NOTIFY_COOLDOWN = 300
CRASH_HISTORY = os.path.join(DIR, "crash_history.json")
PROC_LEDGER = os.path.join(DIR, "proc-ledger.jsonl")
STATUS_FILE = os.path.join(DIR, "runner_status.json")
RULES_FILE = os.path.join(DIR, "runner-rules.json")
SCHEDULE_FILE = os.path.join(DIR, "runner-schedule.json")
SELFHEAL_URL = "http://127.0.0.1:4357/v1/chat/completions"
# Runner control API: the runner exposes an HTTP control endpoint (inbound)
# so external .py programs / second servers can query and manage the fleet
# via runner_connector.py. The runner ALSO polls runner-managed.json servers
# (outbound) for health and restarts them on failure.
CTRL_PORT = int(os.environ.get("RUNNER_CTRL_PORT", "8431"))
CTRL_TOKEN = os.environ.get("RUNNER_CTRL_TOKEN", "sk-runner-local")
MANAGED_FILE = os.path.join(DIR, "runner-managed.json")
_ctrl_server = None

# obsidian-memory companion repo (sibling of this bot repo). Supervised as
# the "memory" process and kept in sync via git_update/git_push_fix.
MEMORY_REPO = os.environ.get("MEMORY_REPO", os.path.join(os.path.dirname(DIR), "obsidian-memory"))

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

OWNER_ID = os.environ.get("OWNER_ID", "8585609360")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Multi-repo auto-update: every repo linked to the runner is git-synced on
# the main loop. Registry: one small file per repo under <bot>/repos/,
# managed by repo_updater.py (auto-discovers new repos linked to
# cyberdeck.py / runner.py / opencode.py). Each entry is
#   (label, path, allow_reset); allow_reset=False means pull-only
#   (never force-sync). Add more with
#   GIT_EXTRA_REPOS="label=path;label2=path2"  (or drop a repos/*.json file).
_PARENT = os.path.dirname(DIR)
import repo_updater as _repo_updater
_repo_updater_mtime = None
_GIT_EXTRA = {}
for _extra in (os.environ.get("GIT_EXTRA_REPOS", "") or "").split(";"):
    _entry = _extra.strip()
    if "=" in _entry:
        _label, _path = _entry.split("=", 1)
        _GIT_EXTRA[_label.strip()] = _path.strip()

def log(msg, section="runner"):
    ts = time.strftime("%H:%M:%S")
    print(f"{ts} [{section}] {msg}")
    logging.info(f"{ts} [{section}] {msg}")

def _security_check():
    issues = []
    setenv = os.path.join(DIR, "setenv.sh")
    if os.path.exists(setenv):
        with open(setenv, encoding="utf-8") as f:
            content = f.read()
        keys_found = _re.findall(r'export\s+(\w+)="([^"]+)"', content)
        credential_suffixes = ("_KEY", "_TOKEN", "_PASSWORD", "_SECRET", "_CREDENTIALS")
        for name, val in keys_found:
            if any(sfx in name for sfx in credential_suffixes) and val and val != "set-via-env-var" and not val.startswith("$"):
                issues.append(f"Hardcoded API key in setenv.sh (masked in log)")
    if issues:
        print("--- Security Scan ---")
        for issue in issues:
            msg = f"! {issue}"
            print(f"  {msg}")
            logging.warning(f"SECURITY {msg}")
        if len(issues) > 2:
            msg = f"! {len(issues)} hardcoded API keys found. Use env vars or encrypted storage."
            print(f"  {msg}")
            logging.warning(f"SECURITY {msg}")
        print("----------------------")

_security_check()

try:
    import key_backup
    missing = key_backup.check_missing_keys()
    if missing:
        log(f"Missing critical keys: {missing}, attempting restore...", "keys")
        restore_result = key_backup.restore_keys()
        if restore_result.get("success"):
            log(f"Keys restored: {restore_result.get('count', 0)} keys", "keys")
        else:
            log(f"Key restore failed: {restore_result.get('error', 'unknown')}", "keys")
    backup_result = key_backup.auto_backup_on_startup()
    if backup_result.get("action") == "backed_up":
        log(f"Auto-backup: {backup_result.get('count', 0)} keys saved", "keys")
except Exception as e:
    log(f"Key backup system error (non-fatal): {e}", "keys")

_last_notify_time = {}

def send_telegram(text, parse_mode="HTML"):
    global BOT_TOKEN, OWNER_ID
    if not BOT_TOKEN or not OWNER_ID:
        return False
    try:
        data = json.dumps({
            "chat_id": OWNER_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        log(f"Telegram notify failed: {e}", "notify")
        return False

def _can_notify(key):
    now = time.time()
    last = _last_notify_time.get(key, 0)
    if now - last < NOTIFY_COOLDOWN:
        return False
    _last_notify_time[key] = now
    return True

# Free-model watcher: polls public catalogs for newly-free / limited-time
# models (e.g. stealth previews free for ~1 week) and broadcasts them to all
# known Telegram chats. State persisted in freemodels_state.json so restarts
# never re-announce. Interval via FREE_MODEL_CHECK_INTERVAL (default 4h).
_free_model_next_check = [0.0]

def _maybe_check_free_models():
    now = time.time()
    if now < _free_model_next_check[0]:
        return
    _free_model_next_check[0] = now + max(600, free_model_watcher.CHECK_INTERVAL)
    try:
        tok = BOT_TOKEN or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        oid = OWNER_ID or os.environ.get("OWNER_ID", "")
        events = free_model_watcher.check_now(bot_token=tok, owner_id=oid)
        if events.get("new"):
            log(f"free models announced: {events['new']} -> {events['sent_to']} chats", "freemodels")
        if events.get("expired"):
            log(f"free models expired: {events['expired']}", "freemodels")
        if events.get("errors"):
            log(f"source errors: {events['errors']}", "freemodels")
    except Exception as e:
        log(f"free model watcher error: {e}", "freemodels")

# Daily owner digest: one Telegram message per day summarizing fleet health,
# restarts, and the free-model tracker. Hour via DIGEST_HOUR (default 8am).
_digest_last_day = [None]

def _snapshot_diff_section():
    """Idea #13: what changed since the most recent fleet snapshot."""
    try:
        snaps = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "snap_*.json")))
        if not snaps:
            return None
        with open(snaps[-1], encoding="utf-8") as f:
            snap = json.load(f)
        lines = []
        old_procs = snap.get("processes") or {}
        changes = []
        for name in PROCESSES:
            new_state = _proc_status(name)
            old = old_procs.get(name)
            old_state = old.get("state") if isinstance(old, dict) else None
            if old_state and old_state != new_state:
                changes.append(f"{name}: {old_state} → {new_state}")
        if changes:
            lines.append("\U0001F4C8 Since last snapshot:")
            lines.extend(f"• {c}" for c in changes[:6])
        try:
            fm = free_model_watcher.load_state()
            day_ago = time.time() - 86400
            gained = [a.get("model_id") for a in (fm.get("adopted") or {}).values()
                      if a.get("adopted_at", 0) > day_ago]
            lost = [k.split(":", 1)[-1] for k, r in (fm.get("expired") or {}).items()
                    if r.get("last_seen", 0) > day_ago]
            if gained or lost:
                lines.append("\U0001F381 Free models 24h: "
                             + (f"gained {', '.join(map(str, gained))} " if gained else "")
                             + (f"| lost {', '.join(lost)}" if lost else ""))
        except Exception:
            pass
        return "\n".join(lines) if lines else None
    except Exception:
        return None

def _build_daily_digest():
    up_s = int(time.time() - _runner_started)
    uptime = f"{up_s // 86400}d {up_s % 86400 // 3600}h {up_s % 3600 // 60}m"
    lines = [f"\U0001F4DF <b>Fleet digest</b> — {time.strftime('%Y-%m-%d %H:%M')}",
             f"Uptime: {uptime}", ""]
    total_restarts = 0
    for name in PROCESSES:
        alive = name in procs and procs[name].poll() is None
        rc = _restart_count.get(name, 0)
        total_restarts += rc
        state = "\U0001F7E2 up" if alive else ("\u26D4 disabled" if name in _disabled else "\U0001F534 down")
        ram = ""
        if alive:
            try:
                usage = _proc_usage(procs[name].pid)
                if usage and usage.get("rss_mb"):
                    ram = f" | {usage['rss_mb']:.0f}MB"
            except Exception:
                pass
        lines.append(f"• {name}: {state}{ram} | restarts {rc}")
    lines.append("")
    lines.append(f"\U0001F501 Total restarts: {total_restarts}")
    am_line = _androidllm_status_line()
    if am_line:
        lines.insert(1, am_line)
    slo_line = _slo_digest_line()
    if slo_line:
        lines.insert(1, slo_line)
    if _degrade_state["active"]:
        lines.insert(1, "\u26D4 DEGRADED mode active (RAM pressure) — heavy procs paused")
    diff = _snapshot_diff_section()
    if diff:
        lines.append(diff)
        lines.append("")
    try:
        fm_state = free_model_watcher.load_state()
        n_seen = len(fm_state.get("seen", {}))
        adopted = list((fm_state.get("adopted") or {}).keys())
        lines.append(f"\U0001F381 Free models tracked: {n_seen}")
        if adopted:
            lines.append(f"✅ Adopted providers: {', '.join(adopted[:6])}")
    except Exception as e:
        lines.append(f"\U0001F381 freemodels: error ({e})")
    try:
        with open(CRASH_HISTORY, encoding="utf-8") as f:
            hist = json.load(f)
        recent = [c for c in (hist if isinstance(hist, list) else [])][-3:]
        if recent:
            lines.append("")
            lines.append("\U0001FAE1 Recent crashes:")
            for c in recent:
                if isinstance(c, dict):
                    lines.append(f"• {c.get('proc', '?')} {c.get('ts', '')}: {str(c.get('error', ''))[:60]}")
    except Exception:
        pass
    return "\n".join(lines)

def _daily_digest(force=False):
    today = time.strftime("%Y-%m-%d")
    if not force and _digest_last_day[0] == today:
        return
    hour = int(os.environ.get("DIGEST_HOUR", "8"))
    if not force and time.localtime().tm_hour < hour:
        return
    _digest_last_day[0] = today
    try:
        tok = BOT_TOKEN or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        oid = OWNER_ID or os.environ.get("OWNER_ID", "")
        msg = _build_daily_digest()
        if tok and oid and send_telegram(msg):
            log("daily digest sent", "digest")
        else:
            log("daily digest skipped (no token/chat or send failed)", "digest")
    except Exception as e:
        log(f"daily digest error: {e}", "digest")

# ---- upgrade pack v4 -------------------------------------------------------
# adaptive cadence (#1), deploy-guard auto-rollback (#2), stderr sentry (#3/#4),
# disk guard + nightly maintenance (#5/#11), heartbeat/doctor (#6),
# hung-watchdog lite (#7). See RUNNER_IDEAS.md for rationale.

HEARTBEAT_FILE = os.path.join(DIR, "runner_heartbeat.json")
DEPLOY_GUARD_WINDOW = int(os.environ.get("RUNNER_DEPLOY_GUARD_S", "600"))
DEPLOY_GUARD_MAX_CRASHES = int(os.environ.get("RUNNER_DEPLOY_GUARD_MAX_CRASHES", "3"))
STDERR_BURST_LINES = int(os.environ.get("RUNNER_STDERR_BURST", "12"))
STDERR_TAIL_BYTES = 8192
DISK_MIN_FREE_GB = float(os.environ.get("RUNNER_DISK_MIN_FREE_GB", "2.0"))
CADENCE_FAST_S = max(2, int(os.environ.get("RUNNER_CADENCE_FAST_S", "5")))
HUNG_STREAK_NOTIFY = int(os.environ.get("RUNNER_HUNG_STREAK", "20"))

_deploy_guard = {"armed_at": None, "prev_sha": None, "crashes_at_arm": 0}
_stderr_offsets = {}
_web_unhealthy_streak = [0]
_last_maint_day = [None]

def _git_head_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=DIR,
                           capture_output=True, text=True, timeout=10, encoding="utf-8")
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def write_heartbeat():
    """Dead-man-switch file: external watchers check age to detect a stalled runner."""
    try:
        snap = {
            "ts": time.time(),
            "iso": time.strftime("%Y-%m-%d %H:%M:%S"),
            "procs": {n: (p.poll() is None) for n, p in procs.items()},
            "uptime_s": int(time.time() - _runner_started),
            "total_restarts": sum(_restart_count.values()),
        }
        tmp = HEARTBEAT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(snap, f)
        os.replace(tmp, HEARTBEAT_FILE)
    except Exception:
        pass

def _deploy_guard_arm():
    if os.path.isdir(os.path.join(DIR, ".git")):
        _deploy_guard["prev_sha"] = _git_head_sha()
        _deploy_guard["armed_at"] = time.time()
        _deploy_guard["crashes_at_arm"] = _restart_count.get("bot", 0)

def _deploy_guard_tick():
    """If bot crash-spikes right after a git deploy, revert to pre-pull commit."""
    armed = _deploy_guard.get("armed_at")
    if not armed:
        return
    now = time.time()
    if now - armed > DEPLOY_GUARD_WINDOW:
        _deploy_guard["armed_at"] = None
        log(f"deploy guard passed ({DEPLOY_GUARD_WINDOW}s stable)", "guard")
        return
    crashes = _restart_count.get("bot", 0) - _deploy_guard.get("crashes_at_arm", 0)
    if crashes < DEPLOY_GUARD_MAX_CRASHES:
        return
    sha = _deploy_guard.get("prev_sha")
    current_sha = _git_head_sha()
    log(f"deploy guard TRIPPED: {crashes} bot crashes within {int(now-armed)}s of deploy", "guard")
    _ledger("deploy_rollback_start", sha=(sha or "?")[:12], crashes=crashes)
    rolled_back = False
    if sha and sha != current_sha:
        try:
            r = subprocess.run(["git", "reset", "--hard", sha], cwd=DIR,
                               capture_output=True, text=True, timeout=30, encoding="utf-8")
            rolled_back = r.returncode == 0
        except Exception as e:
            log(f"rollback git error: {e}", "guard")
    kill_all(reason="deploy_rollback")
    globals()["last_hashes"] = file_hashes()
    _deploy_guard["armed_at"] = None
    tail = ("Reverted to previous commit. Fleet restarting." if rolled_back
            else "No revert needed (HEAD unchanged or unknown) — fleet restarting.")
    msg = ("<b>Runner</b>: deploy auto-ROLLBACK\n"
           f"{crashes} bot crashes within {int(now-armed)}s of git update.\n"
           + tail)
    send_telegram(msg)
    _ledger("deploy_rollback_done", reverted=bool(rolled_back))

def _stderr_sentry_tick():
    """Detect error bursts in per-proc stderr; alert once per cooldown with excerpt."""
    pat = _re.compile(r"Traceback|CRITICAL|FATAL|Unhandled|uncaught|MemoryError|Segmentation", _re.I)
    for name in PROCESSES:
        path = os.path.join(DIR, f"{name}.stderr")
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        off = _stderr_offsets.get(name)
        if off is None or size < off:
            off = max(0, size - STDERR_TAIL_BYTES)
        if size <= off:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                f.seek(off)
                chunk = f.read()
            _stderr_offsets[name] = min(size, off + len(chunk.encode("utf-8")))
        except OSError:
            continue
        hits = [ln.strip()[:160] for ln in chunk.splitlines() if pat.search(ln)]
        if not hits:
            continue
        for ln in hits[-5:]:
            sig = _re.sub(r"[0-9a-f]{6,}", "H", _re.sub(r"\d+", "N", ln))[:120]
            _ledger("error_signature", proc=name, sig=sig)
        if len(hits) >= STDERR_BURST_LINES and _can_notify(f"errburst_{name}"):
            excerpt = "\n".join(hits[-3:])
            log(f"stderr burst: {len(hits)} errors from {name}", "sentry")
            send_telegram(f"<b>Runner</b>: {len(hits)} error lines just appeared in "
                          f"{name}.stderr\n<pre>{excerpt}</pre>")

def _disk_and_maintenance_tick():
    """Hourly disk check w/ pruning; nightly deep maintenance."""
    global _last_maint_day
    today = time.strftime("%Y-%m-%d")
    hourly_due = not getattr(_disk_and_maintenance_tick, "_last", 0) \
        or time.time() - _disk_and_maintenance_tick._last > 3600
    nightly_due = _last_maint_day[0] != today and time.localtime().tm_hour >= int(os.environ.get("MAINT_HOUR", "4"))
    if not hourly_due and not nightly_due:
        return
    _disk_and_maintenance_tick._last = time.time()
    freed_files = 0
    cutoff_snap = time.time() - 14 * 86400
    cutoff_cache = time.time() - 7 * 86400
    for pattern, cutoff in ((os.path.join(SNAPSHOT_DIR, "snap_*.json"), cutoff_snap),
                            (os.path.join(DIR, "video_cache", "*"), cutoff_cache),
                            (os.path.join(DIR, "*.stderr.*"), cutoff_cache)):
        for f in glob.glob(pattern):
            try:
                if os.path.getmtime(f) < cutoff:
                    os.remove(f)
                    freed_files += 1
            except OSError:
                pass
    free_gb = 0.0
    try:
        du = shutil.disk_usage(DIR)
        free_gb = du.free / 1e9
    except Exception:
        pass
    if nightly_due:
        _last_maint_day[0] = today
        try:
            _rotate_fleet_logs()
        except Exception:
            pass
        log(f"nightly maintenance done (pruned {freed_files} files)", "maint")
        _ledger("nightly_maintenance", pruned=freed_files)
    if free_gb and free_gb < DISK_MIN_FREE_GB:
        if _can_notify("disk_low"):
            send_telegram(f"<b>Runner</b>: LOW DISK {free_gb:.1f}GB free "
                          f"(pruned {freed_files} old files already)")
            log(f"low disk warning: {free_gb:.2f}GB free", "maint")

def _hung_watchdog_tick():
    """web alive but health failing continuously -> restart it (zombie detection)."""
    if "web" not in procs or procs["web"].poll() is not None:
        _web_unhealthy_streak[0] = 0
        return
    if health_check():
        _web_unhealthy_streak[0] = 0
        return
    _web_unhealthy_streak[0] += 1
    if _web_unhealthy_streak[0] == HUNG_STREAK_NOTIFY:
        log(f"web hung: {HUNG_STREAK_NOTIFY} consecutive failed health checks while alive", "watchdog")
        send_telegram("<b>Runner</b>: web process ALIVE but unhealthy for many checks — restarting (possible hang)")
        kill_one("web", reason="hung_watchdog")

def _adaptive_sleep(base_s):
    """Fast cadence when unstable (recent restart / unhealthy), slow when calm."""
    all_ts = [t for wins in _recent_restarts.values() for t in (wins or [])]
    recent_restart = bool(all_ts) and (time.time() - max(all_ts)) < 90
    web_ok = health_check()
    if recent_restart or not web_ok:
        return CADENCE_FAST_S
    return base_s

METRICS_FILE = os.path.join(DIR, "metrics.jsonl")
METRICS_ROTATE_ROWS = 20000
_metrics_last_write = [0.0]

def _metrics_tick():
    """Persist compact fleet metrics (idea #9): one row/minute, self-rotating.
    Gives digests/admin real baselines instead of in-memory-only history."""
    now = time.time()
    if now - _metrics_last_write[0] < 60:
        return
    _metrics_last_write[0] = now
    row = {"ts": now, "iso": time.strftime("%H:%M"), "web_ok": bool(health_check()), "procs": {}}
    for name, p in procs.items():
        alive = p.poll() is None
        info = {"alive": alive}
        if alive:
            try:
                u = _proc_usage(p.pid)
                if u:
                    info["rss_mb"] = round(u.get("rss_mb") or 0, 1)
                    info["cpu_pct"] = round(u.get("cpu_pct") or 0, 1)
            except Exception:
                pass
        row["procs"][name] = info
    try:
        with open(METRICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        if random_line_count(METRICS_FILE, cap=METRICS_ROTATE_ROWS * 2) > METRICS_ROTATE_ROWS * 2:
            _rotate_log_file(METRICS_FILE, max_mb=5, keep=1)
    except Exception as e:
        log(f"metrics write error: {e}", "metrics")

def random_line_count(path, cap=40000):
    """Cheap line estimate for rotation decisions (stops at cap)."""
    n = 0
    try:
        with open(path, "rb") as f:
            for _ in f:
                n += 1
                if n > cap:
                    break
    except OSError:
        return 0
    return n

def _incident_timeline(date_str=None):
    """Idea #17: group proc-ledger events into readable incident episodes."""
    target = date_str or "*"
    rows = []
    try:
        with open(PROC_LEDGER, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                ts = r.get("ts", "")
                if target != "*" and not ts.startswith(target):
                    continue
                if r.get("event") in ("crash", "start", "stop", "git_restart",
                                      "deploy_rollback_start", "deploy_rollback_done",
                                      "storm_hold", "restart_blocked", "nightly_maintenance"):
                    rows.append(r)
    except FileNotFoundError:
        return ["no ledger yet"]
    if not rows:
        return [f"no incidents on {target}"]
    out = [f"=== incident timeline {target} ({len(rows)} events) ==="]
    for r in rows[-60:]:
        extra = ", ".join(f"{k}={v}" for k, v in r.items()
                          if k not in ("ts", "event") and v is not None)
        out.append(f"{r.get('ts', '')}  {r.get('event', '?'):<22} {extra[:100]}")
    return out

PROVIDER_HEALTH_FILE = os.path.join(DIR, "provider_health.json")
SLO_FILE = os.path.join(DIR, "slo_daily.json")
SLO_TARGET_PCT = float(os.environ.get("RUNNER_SLO_TARGET", "99.0"))
DEGRADE_RAM_PCT = float(os.environ.get("RUNNER_DEGRADE_RAM_PCT", "92"))
DEGRADE_RESUME_PCT = float(os.environ.get("RUNNER_DEGRADE_RESUME_PCT", "85"))
DEGRADABLE_PROCS = [s.strip() for s in os.environ.get("RUNNER_DEGRADABLE", "cyberdeck,dma").split(",") if s.strip()]
_degrade_state = {"active": False}
_slo_day = {"day": None}

def _degrade_tick():
    """Idea #16: host RAM pressure -> stop heavy optional procs; resume when clear."""
    try:
        import psutil as _ps
        pct = _ps.virtual_memory().percent
    except Exception:
        return
    if not _degrade_state["active"] and pct >= DEGRADE_RAM_PCT:
        stopped = []
        for name in DEGRADABLE_PROCS:
            if name in procs and procs[name].poll() is None:
                kill_one(name, reason="ram_degrade")
                _disabled.add(name)
                stopped.append(name)
        if stopped:
            _degrade_state["active"] = True
            log(f"DEGRADED mode: RAM {pct:.0f}% >= {DEGRADE_RAM_PCT}% — stopped {', '.join(stopped)}", "degrade")
            _ledger("degrade_on", ram_pct=pct, stopped=stopped)
            send_telegram(f"<b>Runner</b>: DEGRADED mode — RAM {pct:.0f}%, "
                          f"paused: {', '.join(stopped)}. Auto-resumes under {DEGRADE_RESUME_PCT}%.")
    elif _degrade_state["active"] and pct <= DEGRADE_RESUME_PCT:
        resumed = []
        for name in DEGRADABLE_PROCS:
            if name in _disabled:
                _disabled.discard(name)
                resumed.append(name)
        _degrade_state["active"] = False
        if resumed:
            log(f"RAM recovered to {pct:.0f}% — resuming {', '.join(resumed)}", "degrade")
            _ledger("degrade_off", ram_pct=pct, resumed=resumed)
            send_telegram(f"<b>Runner</b>: RAM recovered ({pct:.0f}%) — resuming: {', '.join(resumed)}")

def _load_slo():
    try:
        with open(SLO_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _slo_tick():
    """Idea #10: daily web availability ratio; digest escalates when budget burns."""
    today = time.strftime("%Y-%m-%d")
    if _slo_day["day"] != today:
        prev = _load_slo()
        if prev.get("day") and prev.get("total"):
            prev["closed"] = True
            with open(SLO_FILE + ".prev.json", "w", encoding="utf-8") as f:
                json.dump(prev, f)
        _slo_day.update({"day": today, "total": 0, "ok": 0})
    _slo_day["total"] = _slo_day.get("total", 0) + 1
    if health_check():
        _slo_day["ok"] = _slo_day.get("ok", 0) + 1
    if _slo_day["total"] % 20 == 0:
        try:
            with open(SLO_FILE, "w", encoding="utf-8") as f:
                json.dump({"day": today, "total": _slo_day["total"], "ok": _slo_day["ok"]}, f)
        except Exception:
            pass

def _slo_digest_line():
    d = dict(_slo_day)
    if not d.get("total"):
        try:
            with open(SLO_FILE, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            return None
    total, ok = d.get("total") or 0, d.get("ok") or 0
    if not total:
        return None
    pct = 100.0 * ok / total
    mark = "\u26A0\uFE0F" if pct < SLO_TARGET_PCT else "\U0001F7E2"
    return f"{mark} Web availability today: {pct:.2f}% ({ok}/{total} checks, target {SLO_TARGET_PCT:.0f}%)"

def _record_provider_failure(provider, error=""):
    """Shared circuit file (#12): any process reports failures here; the ctrl
    API exposes it so ALL processes can skip recently-broken providers."""
    try:
        data = {}
        try:
            with open(PROVIDER_HEALTH_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
        now = time.time()
        entry = data.get(provider) or {"fails": [], }
        fails = [t for t in entry.get("fails", []) if now - t < 3600]
        fails.append(now)
        data[provider] = {"fails": fails[-20:], "last_error": str(error)[:120],
                          "updated": time.strftime("%H:%M:%S")}
        tmp = PROVIDER_HEALTH_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, PROVIDER_HEALTH_FILE)
    except Exception:
        pass

def _ledger(event, **fields):
    """Append a structured event to proc-ledger.jsonl (one JSON object per
    line). Continuous-Claude-v3-inspired: full machine-readable lifecycle."""
    try:
        row = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event}
        row.update(fields)
        with open(PROC_LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception as e:
        log(f"ledger write error: {e}", "ledger")

# runner-rules.json ops policy (raptor-inspired): per-process overrides for
# crash auto-disable threshold, self-heal LLM, and androidllm OOM downgrade.
_DEFAULT_RULES = {
    "defaults": {
        "max_strikes": 6,
        "selfheal": True,
        "downgrade_on_oom": False,
        # Tier-1 guardrails (all 0/off unless overridden):
        "max_ram_mb": 0,            # pm2 max_memory_restart-style ceiling
        "max_cpu_pct": 0,           # 0 = CPU guard off (RAM is the reliable one)
        "guard_cooldown_s": 300,    # min gap between guard restarts of one proc
        "grace_timeout_s": 3,       # wait after terminate() before SIGKILL
        "storm_threshold": 5,       # restarts within storm_window_s -> hold
        "storm_window_s": 60,
        "storm_hold_s": 300,        # how long a storm-held proc is paused
        "default_exit_action": "restart",  # restart|no_restart|disable
        "exit_policy": {},          # {"<code>": "restart|no_restart|disable"}
        "log_max_mb": 5,            # per-proc .stderr rotation size
        "pre_stop": None,           # shell cmd run before terminate (graceful)
    },
    "bot": {"max_strikes": 4, "selfheal": True, "max_ram_mb": 1024, "max_cpu_pct": 0},
    "web": {"max_strikes": 4, "selfheal": False, "max_ram_mb": 768, "max_cpu_pct": 0},
    "omni": {"max_strikes": 4, "selfheal": True, "max_ram_mb": 512, "max_cpu_pct": 0},
    "brain": {"max_strikes": 4, "selfheal": True, "max_ram_mb": 256, "max_cpu_pct": 0},
    "mcp": {"max_strikes": 4, "selfheal": True, "max_ram_mb": 512, "max_cpu_pct": 0},
    "cyberdeck": {"selfheal": True, "max_ram_mb": 768, "max_cpu_pct": 0},
    "memory": {"selfheal": True, "max_ram_mb": 512, "max_cpu_pct": 0},
    "dma": {"selfheal": True, "max_ram_mb": 512, "max_cpu_pct": 0},
    "androidllm": {
        "downgrade_on_oom": True,
        "selfheal": False,
        "max_ram_mb": 2048,         # serve.py child included via psutil sum
        "max_cpu_pct": 0,
        "max_strikes": 8,
    },
}
_rules_cache = None
_rules_mtime = None


def _load_rules(force=False):
    """Merge runner-rules.json over defaults. Cache by file mtime."""
    global _rules_cache, _rules_mtime
    rules = json.loads(json.dumps(_DEFAULT_RULES))
    try:
        m = os.path.getmtime(RULES_FILE)
        if force or m != _rules_mtime:
            with open(RULES_FILE, encoding="utf-8") as f:
                user = json.load(f)
            for section, vals in user.items():
                if isinstance(vals, dict):
                    rules.setdefault(section, {}).update(vals)
                else:
                    rules[section] = vals
            _rules_cache = rules
            _rules_mtime = m
    except FileNotFoundError:
        _rules_cache = rules
        _rules_mtime = 0
    except Exception:
        pass
    return _rules_cache or rules


def _rule(proc, key, default=None):
    """Look up a rule: per-proc override, then defaults."""
    rules = _load_rules()
    proc_rules = rules.get(proc, {}) if isinstance(rules.get(proc, {}), dict) else {}
    if key in proc_rules:
        return proc_rules[key]
    return rules.get("defaults", {}).get(key, default)

SELFHEAL_TIMEOUT = 25
SELFHEAL_MODEL = "groq"


def _llm_self_heal(proc, exit_code, stderr_text, diagnosis):
    """superlog-inspired: ask the :4357 gateway to explain an unexplained
    crash and propose a fix. Only pip-install fixes are auto-applied; the
    diagnosis line is always appended (falling back to regex on any error)."""
    if not _rule(proc, "selfheal", False):
        return diagnosis, False
    try:
        body = json.dumps({
            "model": SELFHEAL_MODEL,
            "messages": [
                {"role": "system", "content": (
                    "You diagnose a crashed python process from its stderr. "
                    "Return ONLY JSON: {\"diagnosis\": \"<1-2 line cause>\", "
                    "\"fix\": \"pip install <module>\" or \"\"}.")},
                {"role": "user", "content": (
                    f"Process: {proc}\nExit code: {exit_code}\n"
                    f"Stderr tail:\n{stderr_text[-1500:] or '(none)'}")},
            ],
            "max_tokens": 200,
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            SELFHEAL_URL, data=body,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=SELFHEAL_TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        m = _re.search(r"\{.*\}", content, _re.S)
        if not m:
            return diagnosis, False
        fix = ""
        try:
            parsed = json.loads(m.group(0))
            diag = str(parsed.get("diagnosis", "")).strip()
            fix = str(parsed.get("fix", "")).strip()
        except Exception:
            diag = content[:200]
        if diag:
            diagnosis.append(f"[LLM] {diag}")
            _ledger("selfheal_analyzed", proc=proc, diagnosis=diag[:300])
        fix_applied = False
        if fix.startswith("pip install"):
            mod = fix.split()[2].strip()
            if mod and mod != "install":
                try:
                    r = subprocess.run(
                        [sys.executable, "-m", "pip", "install", mod],
                        capture_output=True, text=True, timeout=120)
                    if r.returncode == 0:
                        fix_applied = True
                        diagnosis.append(f"[LLM] auto-installed: {mod}")
                        _ledger("selfheal_fix", proc=proc, fix=f"pip install {mod}", applied=True)
                except Exception:
                    pass
        return diagnosis, fix_applied
    except Exception as e:
        log(f"self-heal failed ({proc}): {e}", "selfheal")
        return diagnosis, False


def _validate_py_compile(repo_dir):
    """bernstein-inspired: py_compile every *.py under `repo_dir` before a
    git-triggered fleet restart. Returns list of (path, line, msg)."""
    errors = []
    if not repo_dir or not os.path.isdir(repo_dir):
        return errors
    py_files = glob.glob(os.path.join(repo_dir, "**", "*.py"), recursive=True)
    for f in py_files:
        if any(seg in f.replace("\\", "/") for seg in ("/venv/", "/.venv/", "/node_modules/", "/.git/", "/site-packages/")):
            continue
        try:
            compile(open(f, encoding="utf-8", errors="replace").read(), f, "exec")
        except SyntaxError as e:
            errors.append((os.path.relpath(f, repo_dir), e.lineno or 0, e.msg))
    return errors


def _validate_repo_change(label, repo_dir):
    """Validate a changed repo; log+ledger + return False to block restart."""
    errors = _validate_py_compile(repo_dir)
    if errors:
        first = errors[0]
        msg = f"repo '{label}' has syntax errors, BLOCKING restart: {first[0]}:{first[1]} {first[2]}"
        log(msg, "git")
        _ledger("restart_blocked", proc=label, reason="syntax_error",
                file=first[0], line=first[1], msg=first[2])
        if _can_notify(f"blocked_{label}"):
            send_telegram(f"<b>Runner</b>: {label} update BLOCKED "
                          f"(py_compile failed)\n{first[0]}:{first[1]} {first[2]}")
        return False
    return True

def load_dotenv():
    env_vars = os.environ.copy()
    for fname in [".env", "setenv.sh"]:
        fpath = os.path.join(DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        line = line.replace("export ", "")
                        key, _, val = line.partition("=")
                        val = val.strip().strip('"').strip("'")
                        env_vars[key.strip()] = val
    return env_vars

def file_hashes():
    h = {}
    skip = {"version.json", "version_state.json", "runner.log", "crash.log",
            "announced_versions.json", "crash_history.json",
            "agents.json", "providers.json", "teams.json", "sessions.json",
            "admins.json", "mods.json", "agent_providers.json", "routines.json",
            "multi_sessions.json", "conversations.json", "memory.json",
            "token_usage.json", "experimental.json", "custom_commands.json",
            "context_files.json", "conversation_tags.json", "bridges.json",
            "checkpoints.json", "premade_skills.json", "schedule.json",
            "reminders.json", "usage_stats.json", "workflows.json",
            "bot_crash.txt", "bot.log", "security_warnings.txt",
            "runner-notes.md", "runner_status.json", "proc-ledger.jsonl",
            "runner-rules.json", "runner-schedule.json", "runner-managed.json"}
    _repo_dir_prefix = os.path.join(DIR, "repos")
    for f in glob.glob(os.path.join(DIR, "*.py")) + glob.glob(os.path.join(DIR, "*.json")) + glob.glob(os.path.join(DIR, "whatsapp", "*.js")):
        if os.path.basename(f) in skip:
            continue
        if os.path.dirname(f) == _repo_dir_prefix or f.startswith(_repo_dir_prefix + os.sep):
            continue
        try:
            with open(f, "rb") as fh:
                h[f] = hashlib.sha256(fh.read()).hexdigest()
        except:
            pass
    return h

def git_update():
    """Multi-repo sync with live progress (0/N -> N/N). New repos that are
    linked to the bot (reference cyberdeck.py/runner.py/opencode.py, or are
    referenced by them) are auto-added to the update set. Returns the set
    of labels that actually changed."""
    global _repo_updater_mtime
    try:
        _path = os.path.abspath(_repo_updater.__file__)
        _mtime = os.path.getmtime(_path)
        if _repo_updater_mtime != _mtime:
            _importlib.reload(_repo_updater)
            _repo_updater_mtime = _mtime
    except Exception as e:
        log(f"multi-repo module reload error: {e}", "git")
    try:
        entries, ignored = _repo_updater.sync_registry(_PARENT, _GIT_EXTRA)
    except Exception as e:
        log(f"multi-repo registry error: {e}", "git")
        return set()
    if ignored:
        log(f"multi-repo: new repos not linked to bot, skipped: "
            f"{', '.join(ignored)}", "git")
        if _can_notify("git_unlinked"):
            send_telegram(f"<b>Runner</b>: found new repos not linked to the "
                          f"bot (no cyberdeck.py/runner.py/opencode.py "
                          f"reference) — skipped: {', '.join(ignored)}")
    def _notify(prefix, msg):
        log(f"multi-repo {prefix}: {msg}", "git")
        if not msg.startswith("searching") or _can_notify(f"git_prog_{prefix}"):
            if _can_notify("git_prog"):
                send_telegram(f"<b>Runner</b> ({prefix}): {msg}")
    try:
        return _repo_updater.update_all(entries, notify=_notify)
    except Exception as e:
        log(f"multi-repo update error: {e}", "git")
        return set()

def _git_push_fix_dir(d, label, message="auto-fix: runner patch"):
    try:
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=d, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode != 0:
            return False
        subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=d, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode == 0:
            log(f"[{label}] nothing to push", "git")
            return False
        subprocess.run(["git", "commit", "-m", message, "--no-verify"], cwd=d, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "push", "--force-with-lease"], cwd=d, capture_output=True, text=True, timeout=60, encoding="utf-8")
        if r.returncode == 0:
            log(f"[{label}] auto-push successful", "git")
            return True
        else:
            log(f"[{label}] push failed: {r.stderr.strip()}", "git")
            return False
    except Exception as e:
        log(f"[{label}] git push error: {e}", "git")
        return False

def git_push_fix(message="auto-fix: runner patch"):
    ok = _git_push_fix_dir(DIR, "bot", message)
    mem_ok = False
    if os.path.isdir(os.path.join(MEMORY_REPO, ".git")):
        mem_ok = _git_push_fix_dir(MEMORY_REPO, "memory", message)
    return ok or mem_ok

def load_crash_history():
    try:
        if os.path.exists(CRASH_HISTORY):
            with open(CRASH_HISTORY, encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"crashes": [], "total": 0}

def save_crash_history(history):
    try:
        history["crashes"] = history["crashes"][-50:]
        with open(CRASH_HISTORY, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except:
        pass

def analyze_crash(name, exit_code, stderr_text=""):
    history = load_crash_history()
    crash_entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "process": name,
        "exit_code": exit_code,
        "stderr": stderr_text[:2000] if stderr_text else ""
    }
    history["crashes"].append(crash_entry)
    history["total"] = history.get("total", 0) + 1
    save_crash_history(history)
    recent = [c for c in history["crashes"][-10:] if c["process"] == name]
    crash_count = len(recent)
    diagnosis = []
    fix_applied = False
    if exit_code == -11 or exit_code == 139:
        diagnosis.append("SIGSEGV - memory corruption")
    elif exit_code == -6 or exit_code == 134:
        diagnosis.append("SIGABRT - assertion failure or OOM")
    elif exit_code == -4 or exit_code == -8:
        diagnosis.append("SIGILL/SIGFPE - illegal instruction or float error")
    elif exit_code == 1:
        diagnosis.append("Generic error (exit 1)")
    elif exit_code == 2:
        diagnosis.append("Misuse of shell command / file not found")
    elif exit_code == 3:
        diagnosis.append("Cannot open input file")
    elif exit_code == 137 or exit_code == -9:
        diagnosis.append("SIGKILL - OOM killer or force-killed")
    elif exit_code == 143 or exit_code == -15:
        diagnosis.append("SIGTERM - clean shutdown")
    else:
        diagnosis.append(f"Exit code {exit_code}")
    if "SyntaxError" in stderr_text:
        diagnosis.append("Python syntax error detected")
        match = _re.search(r'File "(.+?)", line (\d+)', stderr_text)
        if match:
            filepath, lineno = match.group(1), match.group(2)
            diagnosis.append(f"  -> {filepath}:{lineno}")
    elif "IndentationError" in stderr_text:
        diagnosis.append("Indentation error")
    elif "ModuleNotFoundError" in stderr_text:
        match = _re.search(r"No module named '(.+?)'", stderr_text)
        mod = match.group(1) if match else "unknown"
        diagnosis.append(f"Missing module: {mod}")
        try:
            pip_cmd = [sys.executable, "-m", "pip", "install", mod]
            r = subprocess.run(pip_cmd, capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                diagnosis.append(f"  -> Auto-installed: {mod}")
                fix_applied = True
        except:
            pass
    elif "ImportError" in stderr_text:
        match = _re.search(r"cannot import name '(.+?)'", stderr_text)
        if match:
            diagnosis.append(f"Import error: {match.group(1)}")
    elif "PermissionError" in stderr_text:
        diagnosis.append("Permission denied - check file permissions")
    elif "ConnectionRefused" in stderr_text or "Errno 111" in stderr_text:
        diagnosis.append("Port already in use or service down")
    elif "Address already in use" in stderr_text:
        diagnosis.append("Port conflict detected")
        match = _re.search(r'port (\d+)', stderr_text)
        if match:
            port = match.group(1)
            free_port(int(port))
            diagnosis.append(f"  -> Freed port {port}")
            fix_applied = True
    elif "MemoryError" in stderr_text or "out of memory" in stderr_text.lower():
        diagnosis.append("Out of memory")
    elif "UnicodeDecodeError" in stderr_text:
        diagnosis.append("Encoding error - adding utf-8 fallback")
    elif "Traceback" in stderr_text:
        lines = [l for l in stderr_text.split("\n") if l.strip()]
        if lines:
            diagnosis.append(f"Traceback: {lines[-1][:200]}")
    if crash_count >= 3:
        diagnosis.append(f"WARNING: {name} crashed {crash_count} times recently!")
    return {
        "diagnosis": diagnosis,
        "crash_count": crash_count,
        "fix_applied": fix_applied,
        "history": history
    }

def free_port(port):
    """Kill whatever holds `port`. Returns (freed, detail). On Windows this
    also refuses to kill the runner's own supervised processes (those are
    handled by kill_one instead, so their crash/backoff logic stays intact)."""
    if sys.platform == "win32":
        try:
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=10, encoding="utf-8")
            for line in r.stdout.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 5 and f":{port}" in parts[1]:
                    pid = parts[-1]
                    name = _proc_name_by_pid(pid)
                    if name and name in PROCESSES and name in procs:
                        log(f"port {port} held by supervised '{name}' (pid {pid}) — restarting instead", "ports")
                        _intentional_kills.add(name)
                        kill_one(name)
                        return True, f"restarted supervised '{name}'"
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, timeout=5)
                    return True, f"killed pid {pid} ({name or 'unknown'})"
        except Exception as e:
            log(f"free_port error: {e}", "ports")
            return False, str(e)
    else:
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, timeout=5)
        except Exception:
            pass
        try:
            subprocess.run(["pkill", "-f", "web_gateway.py"], capture_output=True, timeout=5)
        except Exception:
            pass
    return False, "no holder found"


def _proc_name_by_pid(pid):
    """Map a PID to a short process name (best-effort, cached per scan)."""
    if pid in _pid_name_cache:
        return _pid_name_cache[pid]
    name = None
    if sys.platform == "win32":
        try:
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                               capture_output=True, text=True, timeout=8, encoding="utf-8")
            if r.returncode == 0 and r.stdout.strip():
                name = r.stdout.strip().split(",")[0].strip('"').lower()
        except Exception:
            pass
    else:
        try:
            r = subprocess.run(["ps", "-o", "comm=", "-p", str(pid)],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                name = os.path.basename(r.stdout.strip()).lower()
        except Exception:
            pass
    _pid_name_cache[pid] = name
    return name


def _proc_script_by_pid(pid):
    """Find the .py/.js script in a process's command line (for supervised
    tagging, since every python child shows as python.exe). Uses a cache
    warmed by _warm_script_cache() so a full port scan only fires ONE CIM
    query instead of one per PID."""
    if pid in _script_cache:
        return _script_cache.get(pid)
    if _script_cache is not None:
        return None
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],
                capture_output=True, text=True, timeout=10, encoding="utf-8")
            cl = (r.stdout or "").strip()
        except Exception:
            cl = ""
    else:
        try:
            r = subprocess.run(["ps", "-p", str(pid), "-o", "args="],
                               capture_output=True, text=True, timeout=5)
            cl = r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            cl = ""
    script = None
    if cl:
        for tok in cl.replace('"', "").split():
            if tok.lower().endswith((".py", ".js", ".mjs")):
                script = os.path.basename(tok).lower()
                break
    _script_cache[pid] = script
    return script


def _warm_script_cache():
    """Batch-load command lines for every python/node process in one CIM
    query, so supervised tagging in a port scan doesn't shell out per PID."""
    global _script_cache
    _script_cache = {}
    if sys.platform != "win32":
        return
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '\\.py|node\\.exe' } | "
             "ForEach-Object { \"$($_.ProcessId)|$($_.CommandLine)\" }"],
            capture_output=True, text=True, timeout=15, encoding="utf-8")
        for line in (r.stdout or "").split("\n"):
            line = line.strip()
            if "|" not in line:
                continue
            pid, cl = line.split("|", 1)
            script = None
            for tok in cl.replace('"', "").split():
                if tok.lower().endswith((".py", ".js", ".mjs")):
                    script = os.path.basename(tok).lower()
                    break
            _script_cache[pid] = script
    except Exception:
        pass


def _scan_ports():
    """List all listening TCP ports with owning pid + process name, plus a
    flag for ports owned by supervised processes. port-whisperer-inspired."""
    out = []
    _warm_script_cache()
    _pid_name_cache.clear()
    if sys.platform == "win32":
        try:
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=10, encoding="utf-8")
            for line in r.stdout.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0] == "TCP" and "LISTENING" in line:
                    proto = parts[0].lower()
                    local = parts[1]
                    pid = parts[-1]
                    if ":" in local:
                        host, port = local.rsplit(":", 1)
                        if host in ("127.0.0.1", "0.0.0.0", "[::]", "::", "[::1]"):
                            out.append(_port_row(proto, port, pid))
        except Exception as e:
            log(f"port scan error: {e}", "ports")
            return []
    else:
        try:
            r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.split("\n"):
                parts = line.split()
                if len(parts) >= 4:
                    port = parts[3].rsplit(":", 1)[-1]
                    pid = "?"
                    for p in parts:
                        if "pid=" in p:
                            pid = p.split("pid=")[1].split(",")[0]
                            break
                    out.append(_port_row("tcp", port, pid))
        except Exception:
            pass
    # Dedupe IPv4/IPv6 double listings of the same (port, pid).
    seen = set()
    uniq = []
    for row in out:
        key = (row.get("port"), row.get("pid"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(row)
    out = uniq
    out.sort(key=lambda x: (x["port"] is None, x.get("port") or 0))
    return out


def _port_row(proto, port, pid):
    try:
        port_i = int(port)
    except Exception:
        port_i = None
    name = _proc_name_by_pid(pid)
    supervised_key = None
    for key, pobj in procs.items():
        try:
            if str(getattr(pobj, "pid", "")) == str(pid):
                supervised_key = key
                break
        except Exception:
            continue
    if supervised_key is None and name in ("python.exe", "python3", "node.exe", "node"):
        script = _proc_script_by_pid(pid)
        if script:
            for key in PROCESSES:
                if script in " ".join(map(str, PROCESSES[key])):
                    supervised_key = key
                    break
    supervised = supervised_key is not None
    managed = False
    for s in _load_managed():
        try:
            if str(s.get("pid")) == str(pid):
                managed = True
                break
        except Exception:
            continue
    if supervised_key:
        name = supervised_key
    return {"proto": proto, "port": port_i, "pid": pid, "proc": name,
            "supervised": supervised, "managed": managed}

# -- androidllm OOM downgrade cascade --------------------------------------
# When androidllm-serve dies from an OOM-class crash (Android lowmemorykiller
# sends SIGKILL; Python aborts on alloc failure), step down to the next
# smaller sharded model instead of crash-looping on the same one. The state
# file write is picked up by the main loop's mtime watcher, which restarts
# serve on the smaller model. Cooldown + persisted timestamp avoid storms.
DOWNGRADE_COOLDOWN = 600
_down_last = {"ts": 0}


def _is_oom_crash(exit_code, stderr_text):
    if exit_code in (137, -9, 134, -6):
        return True
    low = (stderr_text or "").lower()
    return ("memoryerror" in low or "out of memory" in low
            or "killed" in low)


def _downgrade_state():
    """Last downgrade timestamp from crash_history.json (survives restarts)."""
    try:
        if os.path.exists(CRASH_HISTORY):
            with open(CRASH_HISTORY, encoding="utf-8") as f:
                return json.load(f).get("downgrade_ts", 0)
    except Exception:
        pass
    return 0


def _record_downgrade():
    try:
        history = load_crash_history()
        history["downgrade_ts"] = time.time()
        save_crash_history(history)
    except Exception:
        pass


def _maybe_downgrade_androidllm(exit_code, stderr_text):
    """On OOM crash: ASK the owner before switching to the next smaller
    sharded model. Returns (pending | apply | None, message)."""
    global _androidllm_state_ts
    if not _is_oom_crash(exit_code, stderr_text):
        return None, None
    if not _rule("androidllm", "downgrade_on_oom", False):
        return None, "OOM crash but downgrade disabled by runner-rules.json"
    now = time.time()
    last = max(_down_last["ts"], _downgrade_state())
    if now - last < DOWNGRADE_COOLDOWN:
        return None, f"OOM crash but downgrade on cooldown ({int(now - last)}s ago)"
    st = androidllm_models.read_state(bot_env)
    cur = st.get("id")
    nxt = androidllm_models.next_smaller(cur, bot_env) if cur else None
    if not cur:
        return None, "OOM crash but no active model id in state"
    if not nxt:
        return None, (f"OOM crash with {cur} but no smaller sharded model "
                      f"available (ladder bottom or not installed)")
    # consent gate: an already-pending request means we already asked —
    # don't re-ask, don't apply; the owner will answer or it expires.
    pending = androidllm_models.peek_consent(bot_env)
    if pending:
        return None, f"OOM crash but consent for {pending.get('target')} already pending"
    req = androidllm_models.request_consent(
        "downgrade", nxt, f"OOM crash of {cur}", requester="runner", env=bot_env)
    _down_last["ts"] = now
    _record_downgrade()
    _ledger("downgrade_proposed", proc="androidllm", cur=cur, nxt=nxt)
    if _can_notify("model_consent"):
        send_telegram(
            f"<b>Androidllm model server</b> crashed with <b>out of memory</b> "
            f"while serving <b>{cur}</b>.\n\n"
            f"Proposed: downgrade the server to <b>{nxt}</b> "
            f"({androidllm_models.shard_dir(nxt, bot_env)}).\n\n"
            f"Reply <b>/approve</b> to switch, or <b>/deny</b> to stay on {cur}.")
    return "pending", f"OOM downgrade {cur} -> {nxt} ASKED OWNER (pending consent)"

# -- AndroidLLM Autopilot ----------------------------------------------------
# Proactive local-model management (upgrades the reactive OOM cascade):
#   1. serve health probe -> hung restarts (alive but not answering)
#   2. host RAM pressure -> PROPOSE downgrade BEFORE the OOM killer strikes
#   3. sustained headroom -> PROPOSE upgrade to the largest fitting model
# All switches go through the same consent gate as OOM downgrades (/approve).
ANDROIDLLM_HUNG_TICKS = int(os.environ.get("ANDROIDLLM_HUNG_TICKS", "12"))
ANDROIDLLM_PROBE_TIMEOUT = float(os.environ.get("ANDROIDLLM_PROBE_TIMEOUT", "3"))
ANDROIDLLM_RAM_PRESSURE_PCT = float(os.environ.get("ANDROIDLLM_RAM_PRESSURE_PCT", "88"))
ANDROIDLLM_UPGRADE_HEADROOM_PCT = float(os.environ.get("ANDROIDLLM_UPGRADE_HEADROOM_PCT", "55"))
ANDROIDLLM_AUTOPILOT_COOLDOWN = int(os.environ.get("ANDROIDLLM_AUTOPILOT_COOLDOWN_S", str(6 * 3600)))
_ap = {"probe_fails": 0, "last_action": 0.0}

def _am_model_entry(mid):
    for m in getattr(androidllm_models, "RECOMMENDED", []):
        if m.get("id") == mid:
            return m
    return None

def _next_bigger_fitting(cur):
    """Largest sharded model above `cur` in the ladder that fits free RAM
    (keeping ~1.5GB OS margin), or None."""
    ladder = getattr(androidllm_models, "DOWNGRADE_LADDER", [])
    if cur not in ladder:
        return None
    try:
        avail = androidllm_models.available_ram_gb(bot_env)
    except Exception:
        return None
    headroom = max(0.0, avail - 1.5)
    for mid in reversed(ladder[:ladder.index(cur)]):
        e = _am_model_entry(mid)
        if e and androidllm_models.is_sharded(mid, bot_env) \
                and float(e.get("disk_gb") or 99) <= headroom:
            return mid
    return None

def _androidllm_probe_ok():
    url = f"http://127.0.0.1:{_androidllm_port}/health"
    try:
        with urllib.request.urlopen(url, timeout=ANDROIDLLM_PROBE_TIMEOUT) as r:
            return r.status < 500
    except urllib.error.HTTPError:
        return True          # answered with an error code -> server IS alive
    except Exception:
        pass
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{_androidllm_port}/", timeout=ANDROIDLLM_PROBE_TIMEOUT) as r:
            return r.status < 500
    except Exception:
        return False

def _androidllm_autopilot_tick():
    if not _androidllm_enabled:
        return
    p = procs.get("androidllm")
    alive = bool(p and p.poll() is None)

    # 1) hung-serve watchdog: alive but never answers, well after start
    if alive:
        up_s = time.time() - _started_at.get("androidllm", 0)
        if up_s > 300:
            if _androidllm_probe_ok():
                _ap["probe_fails"] = 0
            else:
                _ap["probe_fails"] += 1
                if _ap["probe_fails"] >= ANDROIDLLM_HUNG_TICKS:
                    log(f"androidllm hung: {_ap['probe_fails']} failed probes while alive", "autopilot")
                    send_telegram("<b>Androidllm</b>: serving process alive but not answering — restarting it.")
                    _ledger("serve_hung_restart", proc="androidllm")
                    kill_one("androidllm", reason="serve_hung")
                    _ap["probe_fails"] = 0

    # 2)+3) RAM-pressure downgrade / headroom upgrade proposals
    if not alive:
        return
    now = time.time()
    if now - _ap["last_action"] < ANDROIDLLM_AUTOPILOT_COOLDOWN:
        return
    if androidllm_models.peek_consent(bot_env):
        return                      # already asking something
    try:
        import psutil as _ps
        pct = _ps.virtual_memory().percent
    except Exception:
        return
    st = androidllm_models.read_state(bot_env)
    cur = st.get("id")

    if pct >= ANDROIDLLM_RAM_PRESSURE_PCT and cur:
        nxt = androidllm_models.next_smaller(cur, bot_env)
        if nxt:
            req = androidllm_models.request_consent(
                "downgrade", nxt,
                f"host RAM at {pct:.0f}% with {cur} served (prevent OOM)",
                requester="autopilot", env=bot_env)
            if req:
                _ap["last_action"] = now
                _ledger("autopilot_downgrade_proposed", proc="androidllm", cur=cur, nxt=nxt, ram_pct=pct)
                if _can_notify("autopilot"):
                    send_telegram(
                        f"<b>Androidllm Autopilot</b>: RAM at <b>{pct:.0f}%</b> while "
                        f"serving <b>{cur}</b>.\n\nProposed PREVENTIVE downgrade to "
                        f"<b>{nxt}</b>. Reply <b>/approve</b> to switch now, or "
                        f"<b>/deny</b> to ride it out (OOM cascade will re-ask later).")
                log(f"autopilot proposed downgrade {cur} -> {nxt} (RAM {pct:.0f}%)", "autopilot")

    elif pct <= ANDROIDLLM_UPGRADE_HEADROOM_PCT and cur:
        bigger = _next_bigger_fitting(cur)
        if bigger:
            req = androidllm_models.request_consent(
                "upgrade", bigger,
                f"stable headroom ({pct:.0f}% RAM used) with {cur} served",
                requester="autopilot", env=bot_env)
            if req:
                _ap["last_action"] = now
                _ledger("autopilot_upgrade_proposed", proc="androidllm", cur=cur, nxt=bigger, ram_pct=pct)
                if _can_notify("autopilot"):
                    send_telegram(
                        f"<b>Androidllm Autopilot</b>: you have spare RAM "
                        f"({100-pct:.0f}% free) and <b>{bigger}</b> is sharded locally.\n\n"
                        f"Proposed UPGRADE from <b>{cur}</b>. Reply <b>/approve</b> for the "
                        f"bigger brain, or <b>/deny</b> to keep {cur}.")
                log(f"autopilot proposed upgrade {cur} -> {bigger} (RAM {pct:.0f}%)", "autopilot")

def _androidllm_status_line():
    if not _androidllm_enabled:
        return None
    st = androidllm_models.read_state(bot_env)
    cur = st.get("id") or "?"
    parts = [f"\U0001F9EE Local model: {cur}"]
    p = procs.get("androidllm")
    parts.append("\U0001F7E2 serving" if p and p.poll() is None else "\U0001F534 stopped")
    try:
        import psutil as _ps
        pct = _ps.virtual_memory().percent
        parts.append(f"RAM {pct:.0f}%")
        if pct >= ANDROIDLLM_RAM_PRESSURE_PCT:
            parts.append("\u26A0\uFE0F pressure")
    except Exception:
        pass
    pend = androidllm_models.peek_consent(bot_env)
    if pend:
        parts.append(f"\u23F3 awaiting /approve for {pend.get('target')}")
    return " | ".join(parts)

def health_check():
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except:
        return False

def monitor_process(name, proc):
    proc.wait()
    exit_code = proc.returncode
    stderr_text = ""
    try:
        crash_file = os.path.join(DIR, f"{name}.stderr")
        if os.path.exists(crash_file):
            with open(crash_file, encoding="utf-8", errors="replace") as f:
                stderr_text = f.read()[:2000]
    except:
        pass
    if name not in _intentional_kills:
        _register_crash(name)
    _intentional_kills.discard(name)
    msg = f"{name} crashed (exit {exit_code})"
    log(msg, "proc")
    _ledger("crash", proc=name, exit=exit_code,
            strikes=_crash_strikes.get(name, 0),
            stderr=stderr_text[-300:])
    with open(CRASH_LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    analysis = analyze_crash(name, exit_code, stderr_text)
    diagnosis_str = "\n".join(analysis["diagnosis"])
    analysis["diagnosis"], analysis["fix_applied"] = _llm_self_heal(
        name, exit_code, stderr_text, analysis["diagnosis"])
    diagnosis_str = "\n".join(analysis["diagnosis"])
    if name not in _intentional_kills:
        _maybe_disable(name)
    _apply_exit_policy(name, exit_code)
    downgrade_info = None
    if name == "androidllm":
        try:
            nxt, msg = _maybe_downgrade_androidllm(exit_code, stderr_text)
            if nxt:
                if nxt == "pending":
                    downgrade_info = (f"<b>{msg}</b>\n"
                                      f"Waiting for <b>/approve</b> or <b>/deny</b> (30 min TTL).")
                else:
                    downgrade_info = f"Downgraded to <b>{nxt}</b> - restarting on smaller model"
                log(f"androidllm {msg}", "proc")
            elif msg:
                log(f"androidllm {msg}", "proc")
        except Exception as e:
            log(f"androidllm downgrade error: {e}", "proc")
    if _can_notify(f"crash_{name}"):
        hostname = socket.gethostname()[:20]
        notify_msg = (
            f"<b>Bot Offline!</b>\n\n"
            f"<b>Process:</b> {name}\n"
            f"<b>Exit:</b> {exit_code}\n"
            f"<b>Host:</b> {hostname}\n"
            f"<b>Crashes:</b> {analysis['crash_count']}/10 recent\n"
            f"<b>Time:</b> {time.strftime('%H:%M:%S')}\n\n"
            f"<b>Diagnosis:</b>\n<pre>{diagnosis_str}</pre>"
        )
        if downgrade_info:
            notify_msg += f"\n\n<i>{downgrade_info}</i>"
        if stderr_text:
            tail = stderr_text[-500:].strip()
            if tail:
                notify_msg += f"\n\n<b>Error tail:</b>\n<pre>{tail}</pre>"
        if analysis["fix_applied"]:
            notify_msg += "\n\n<i>Auto-fix was applied, restarting...</i>"
        send_telegram(notify_msg)

PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
    "cyberdeck": ["python", "cyberdeck_bot.py"],
}
# OMNI Gateway (OmniRoute-inspired): one keyring -> validated providers ->
# ranked free models -> single OpenAI-compatible endpoint on :4455.
if os.path.isfile(os.path.join(DIR, "omni_gateway.py")):
    PROCESSES["omni"] = [sys.executable, os.path.join(DIR, "omni_gateway.py")]
    log("omni gateway supervision enabled (:"
        f"{os.environ.get('OMNI_PORT', '4455')})", "proc")
# Self-learning brain (:4590): local Ollama model + multi-AI study loop that
# asks other models via the OMNI gateway and distills answers into memory.
_brain_py = os.path.join(DIR, "self_learner", "server.py")
if os.path.isfile(_brain_py):
    PROCESSES["brain"] = [sys.executable, _brain_py]
    log("self-learning brain supervision enabled (:"
        f"{os.environ.get('BRAIN_PORT', '4590')})", "proc")
# MCP reference pack (modelcontextprotocol/servers): HTTP bridge on :8430.
# Both bots (bot + web gateway) reach the same tools over HTTP. The gateway
# is supervised directly (NOT via `mcp_servers.py bridge`, whose os.execv is
# broken on Windows when the python path contains spaces); the gateway itself
# spawns the TS (node) / Python (uv) servers as children. servers.json is
# refreshed once at startup via `mcp_servers.py config`.
_mcp_pack = os.path.join(DIR, "mcp_servers.py")
_mcp_config = os.path.join(os.path.expanduser("~"), ".mcp", "servers.json")
_mcp_gateway = os.path.join(os.path.expanduser("~"), "Desktop", "agents-places",
                            "agents", "mcp-gateway", "gateway.py")
if os.path.isfile(_mcp_pack) and os.path.isfile(_mcp_config) and os.path.isfile(_mcp_gateway):
    PROCESSES["mcp"] = [
        sys.executable, _mcp_gateway,
        "--port", os.environ.get("MCP_HTTP_PORT", "8430"),
        "--token", os.environ.get("MCP_GATEWAY_TOKEN", "sk-local"),
        "--servers", _mcp_config,
    ]
    log(f"mcp gateway supervision enabled (:"
        f"{os.environ.get('MCP_HTTP_PORT', '8430')}, {_mcp_config})", "proc")
else:
    log(f"mcp gateway supervision disabled (mcp_servers.py, servers.json "
        f"or gateway.py missing: {_mcp_config})", "proc")
if os.path.isfile(os.path.join(MEMORY_REPO, "om.py")):
    PROCESSES["memory"] = [sys.executable, os.path.join(MEMORY_REPO, "om.py"), "watch"]
    log(f"memory daemon supervision enabled ({MEMORY_REPO})", "proc")
else:
    log(f"memory daemon supervision disabled (om.py not found at {MEMORY_REPO})", "proc")
CHECK_INTERVAL = 15
HEALTH_URL = "http://127.0.0.1:4357/api/providers"
MAX_RESTARTS = 5
RESTART_WINDOW = 300

# Per-process crash backoff: when a process crashes repeatedly, wait
# progressively longer before restarting it (BACKOFF_BASE x 2^strikes,
# capped at BACKOFF_CAP). Strikes decay once a process stays alive longer
# than BACKOFF_RESET seconds, so a single hiccup restarts fast but a real
# crash-loop gets backoff instead of hammering restarts every CHECK_INTERVAL.
BACKOFF_BASE = 5
BACKOFF_CAP = 300
BACKOFF_RESET = 120
_crash_strikes = {}
_next_start = {}
_started_at = {}
# Total restarts per process (incl. intentional), reset on runner restart.
_restart_count = {}
# Processes killed on purpose (git restart, model switch, file change) are
# not counted as crashes, so planned restarts never trigger backoff.
_intentional_kills = set()


def _register_crash(name):
    """Record a real crash for `name` and arm its next restart time."""
    now = time.time()
    strikes = _crash_strikes.get(name, 0) + 1
    _crash_strikes[name] = strikes
    # jittered exponential backoff (idea #15): +-20% avoids synchronized
    # thundering-herd retries when multiple procs crash on a shared host
    base_delay = min(BACKOFF_BASE * (2 ** (strikes - 1)), BACKOFF_CAP)
    import random as _random
    delay = base_delay * (0.8 + 0.4 * _random.random())
    _next_start[name] = now + delay


def _clear_backoff(name):
    _crash_strikes.pop(name, None)
    _next_start.pop(name, None)


def _backoff_remaining(name):
    """Seconds left before `name` may be (re)started. Decays strikes when
    the process survived long enough between restarts."""
    now = time.time()
    up_since = _started_at.get(name, 0)
    if up_since and now - up_since > BACKOFF_RESET:
        _clear_backoff(name)
    return max(0, _next_start.get(name, 0) - now)


# Auto-disable: when a process exceeds its rules-configured max_strikes, stop
# restarting it entirely until the runner restarts (herdr/raptor-inspired).
_disabled = set()

# pid -> process-name cache for the port inspector (refreshed per scan call).
_pid_name_cache = {}

# pid -> script (.py/.js) cache for the port inspector; None = not warmed yet.
_script_cache = None


def _maybe_disable(name):
    """Disable `name` once its crash strikes exceed max_strikes from rules."""
    if name in _disabled:
        return
    max_strikes = int(_rule(name, "max_strikes", 6))
    if _crash_strikes.get(name, 0) >= max_strikes:
        _disabled.add(name)
        _ledger("disabled", proc=name, strikes=_crash_strikes[name], max_strikes=max_strikes)
        log(f"{name} disabled after {_crash_strikes[name]} crashes "
            f"(max_strikes={max_strikes})", "proc")
        if _can_notify(f"disabled_{name}"):
            send_telegram(f"<b>Runner</b>: <code>{name}</code> disabled after "
                          f"{_crash_strikes[name]} crashes "
                          f"(max_strikes={max_strikes}). Restart runner to re-enable.")


# ---------------------------------------------------------------------------
# Tier-1 resilience: resource guardrails (pm2-style), restart-storm guard
# (systemd StartLimitBurst-style), exit-code policies, graceful kill with
# pre_stop hooks, and per-process log rotation.
# ---------------------------------------------------------------------------
_guard_last = {}
_guard_restarts = {}
_recent_restarts = {}
_storm_held = {}


def _proc_usage(pid):
    """(ram_mb, cpu_pct) for pid INCLUDING its children, so wrapper procs
    (uvx/uvicorn) report the real load. (None, None) on any error."""
    try:
        import psutil as _ps
    except Exception:
        return None, None
    try:
        pp = _ps.Process(pid)
    except Exception:
        return None, None
    ram = 0.0
    try:
        ram += (pp.memory_info().rss or 0)
    except Exception:
        pass
    try:
        for ch in pp.children(recursive=True):
            try:
                ram += ch.memory_info().rss or 0
            except Exception:
                pass
    except Exception:
        pass
    cpu = 0.0
    try:
        cpu = pp.cpu_percent(interval=0.05) or 0
    except Exception:
        pass
    return round(ram / 1048576, 1), round(cpu, 1)


def _check_resource_guards():
    """pm2 max_memory_restart-inspired: gracefully restart any supervised
    proc breaching its max_ram_mb / max_cpu_pct ceiling, at most once per
    guard_cooldown_s."""
    now = time.time()
    for name in list(procs.keys()):
        p = procs.get(name)
        if p is None or p.poll() is not None:
            continue
        max_ram = int(_rule(name, "max_ram_mb", 0) or 0)
        max_cpu = int(_rule(name, "max_cpu_pct", 0) or 0)
        if max_ram <= 0 and max_cpu <= 0:
            continue
        if now - _guard_last.get(name, 0) < int(_rule(name, "guard_cooldown_s", 300) or 300):
            continue
        ram_mb, cpu_pct = _proc_usage(p.pid)
        breach = None
        if max_ram > 0 and ram_mb and ram_mb > max_ram:
            breach = f"RAM {ram_mb}MB > {max_ram}MB"
        elif max_cpu > 0 and cpu_pct and cpu_pct > max_cpu:
            breach = f"CPU {cpu_pct}% > {max_cpu}%"
        if not breach:
            continue
        _guard_last[name] = now
        _guard_restarts[name] = _guard_restarts.get(name, 0) + 1
        log(f"guard: {name} breach ({breach}), restarting", "guard")
        _ledger("guard_restart", proc=name, breach=breach,
                ram_mb=ram_mb, cpu_pct=cpu_pct)
        if _can_notify(f"guard_{name}"):
            send_telegram(f"<b>Runner guard</b>: <code>{name}</code> breached "
                          f"<b>{breach}</b> - restarting.")
        kill_one(name, reason="resource_guard")


def _note_restart(name):
    """Record a restart for the storm guard; if restarts in the window cross
    storm_threshold, hold the proc and alert (systemd StartLimitBurst)."""
    now = time.time()
    window = int(_rule(name, "storm_window_s", 60) or 60)
    wins = [t for t in _recent_restarts.get(name, []) if now - t < window]
    wins.append(now)
    _recent_restarts[name] = wins
    thresh = int(_rule(name, "storm_threshold", 5) or 5)
    if len(wins) >= thresh:
        hold = int(_rule(name, "storm_hold_s", 300) or 300)
        _storm_held[name] = now + hold
        _ledger("storm_hold", proc=name, restarts=len(wins),
                window_s=window, hold_s=hold)
        log(f"{name} restart storm ({len(wins)} restarts in {window}s), "
            f"holding {hold}s", "proc")
        if _can_notify(f"storm_{name}"):
            send_telegram(f"<b>Runner</b>: <code>{name}</code> restart storm "
                          f"({len(wins)} restarts in {window}s) - "
                          f"holding for {hold}s.")


def _storm_remaining(name):
    """Seconds the storm guard still holds `name` (0 = clear to start)."""
    now = time.time()
    until = _storm_held.get(name, 0)
    if until <= 0:
        return 0
    if now >= until:
        _storm_held.pop(name, None)
        _recent_restarts.pop(name, None)
        return 0
    return int(until - now)


def _exit_action_for(name, exit_code):
    """Exit-code policy -> action. Explicit per-code rule wins, then
    'default', then default_exit_action. Exit 0 with no explicit rule is a
    clean exit -> 'restart' with backoff reset (handled by caller)."""
    policy = _rule(name, "exit_policy", {})
    if isinstance(policy, dict):
        action = policy.get(str(exit_code)) or policy.get("default")
        if action in ("restart", "no_restart", "disable"):
            return action
    return _rule(name, "default_exit_action", "restart")


def _apply_exit_policy(name, exit_code):
    """Enforce the exit-code policy after a crash. 'no_restart' parks the
    proc until a manual /api/enable; 'disable' behaves like max_strikes;
    exit 0 with the default 'restart' policy is a clean exit -> backoff
    reset (no escalation) so a well-behaved daemon restarting itself on
    exit(0) doesn't climb the backoff ladder."""
    action = _exit_action_for(name, exit_code)
    if action == "no_restart":
        _next_start[name] = time.time() + 31536000
        _ledger("no_restart", proc=name, exit=exit_code)
        log(f"{name} exit {exit_code}: exit policy -> no_restart (manual /api/enable to revive)", "proc")
    elif action == "disable":
        if name not in _disabled:
            _disabled.add(name)
            _ledger("disabled_exit_policy", proc=name, exit=exit_code)
            log(f"{name} exit {exit_code}: exit policy -> disable", "proc")
            if _can_notify(f"exitpolicy_{name}"):
                send_telegram(f"<b>Runner</b>: <code>{name}</code> exit "
                              f"{exit_code} policy says <b>disable</b> - "
                              f"not restarting.")
    else:
        policy = _rule(name, "exit_policy", {})
        explicit = isinstance(policy, dict) and (
            str(exit_code) in policy or "default" in policy)
        if exit_code == 0 and not explicit:
            _clear_backoff(name)


def _rotate_log_file(path, max_mb, keep=2):
    """foreverjs-style rotation: path -> path.1 -> path.2 once size breaches."""
    try:
        if not os.path.exists(path):
            return
        if (os.path.getsize(path) / 1048576) <= max_mb:
            return
        for i in range(keep, 0, -1):
            src = f"{path}.{i - 1}" if i > 1 else path
            dst = f"{path}.{i}"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
    except Exception as e:
        log(f"rotate error for {os.path.basename(path)}: {e}", "proc")


def _rotate_stderr(name):
    max_mb = float(_rule(name, "log_max_mb", 5) or 5)
    _rotate_log_file(os.path.join(DIR, f"{name}.stderr"), max_mb)


def _rotate_fleet_logs():
    for _path, _mb in ((LOG_FILE, 10), (CRASH_LOG, 10), (PROC_LEDGER, 50)):
        _rotate_log_file(_path, _mb)


def _pre_stop(name):
    """Run the proc's pre_stop hook (runner-rules.json): a shell string or
    {"cmd": ..., "timeout": ...} executed before termination (supervisord
    drain-style)."""
    hook = _rule(name, "pre_stop", None)
    if not hook:
        return
    cmd = hook if isinstance(hook, str) else (
        hook.get("cmd", "") if isinstance(hook, dict) else "")
    if not cmd:
        return
    timeout = float(hook.get("timeout", 10)) if isinstance(hook, dict) else 10.0
    log(f"{name} pre_stop: {str(cmd)[:120]}", "proc")
    try:
        subprocess.run(cmd, shell=isinstance(cmd, str), timeout=timeout,
                       cwd=DIR, capture_output=True)
    except Exception as e:
        log(f"{name} pre_stop failed: {e}", "proc")


def _proc_status(name):
    """Current supervision state for `name` (status-file view)."""
    p = procs.get(name)
    if p is None:
        return "absent"
    if p.poll() is None:
        return "running"
    if name in _intentional_kills:
        return "stopped"
    return "crashed"


def _write_status():
    """herdr-inspired: snapshot fleet state to runner_status.json every loop."""
    try:
        status = {
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "runner_pid": os.getpid(),
            "uptime_s": int(time.time() - _runner_started),
            "health_web": health_check(),
            "ctrl": {"port": CTRL_PORT, "listening": bool(_ctrl_server)},
            "managed": {s.get("name", "?") for s in _load_managed()},
            "processes": {},
        }
        for name in PROCESSES:
            p = procs.get(name)
            status["processes"][name] = {
                "state": _proc_status(name),
                "pid": p.pid if p and p.poll() is None else None,
                "uptime_s": int(time.time() - _started_at[name]) if name in _started_at and p and p.poll() is None else 0,
                "strikes": _crash_strikes.get(name, 0),
                "backoff_s": int(_backoff_remaining(name)) if name in _next_start else 0,
                "disabled": name in _disabled,
                "guard_restarts": _guard_restarts.get(name, 0),
                "storm_held_s": _storm_remaining(name),
            }
        status["managed"] = {
            s.get("name", "?"): "ok" if not _managed_down_notified.get(s.get("name", "?"), False) else "down"
            for s in _load_managed()
        }
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        log(f"status write error: {e}", "status")


# row-bot-inspired: runner-schedule.json cron-like tasks + per-loop health rows.
_sched_last = {}
SCHEDULE_DEFAULTS = []


def _load_schedule():
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log(f"schedule load error: {e}", "sched")
    return {}


def _run_scheduled():
    """Run tasks whose minute (and hour) matches now. Each task runs at most
    once per matching minute. Cmd is a list; cwd/timeout optional."""
    cfg = _load_schedule()
    tasks = cfg.get("tasks", [])
    now = time.localtime()
    hhmm = f"{now.tm_hour:02d}:{now.tm_min:02d}"
    for task in tasks:
        name = task.get("name")
        if not name:
            continue
        hour, minute = str(task.get("hour", "*")), str(task.get("minute", "*"))
        if hour != "*" and int(hour) != now.tm_hour:
            continue
        if minute != "*" and int(minute) != now.tm_min:
            continue
        if _sched_last.get(name) == hhmm:
            continue
        _sched_last[name] = hhmm
        cmd = task.get("cmd")
        if not isinstance(cmd, list):
            cmd = str(cmd or "").split()
        cwd = task.get("cwd", DIR)
        if not cwd or not os.path.isdir(cwd):
            cwd = DIR
        timeout = int(task.get("timeout", 120))
        log(f"scheduled task: {name} -> {' '.join(cmd)}", "sched")
        _ledger("scheduled_start", proc=name, cmd=" ".join(cmd)[:200])
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                               timeout=timeout, encoding="utf-8", errors="replace")
            _ledger("scheduled_done", proc=name, rc=r.returncode,
                    out=(r.stdout or "")[-300:], err=(r.stderr or "")[-200:])
            if r.returncode != 0:
                log(f"scheduled task {name} failed rc={r.returncode}: "
                    f"{(r.stderr or '')[-200:]}", "sched")
        except Exception as e:
            log(f"scheduled task {name} error: {e}", "sched")
            _ledger("scheduled_error", proc=name, error=str(e)[:200])

# ---------------------------------------------------------------------------
# Runner control API (inbound): external .py programs / second servers manage
# the fleet over HTTP. Token auth via Bearer header; bind only on loopback.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Drain mode (gunicorn-inspired): when drain is active the runner stops
# accepting new work, waits for in-flight tasks to finish, then kills procs.
# ---------------------------------------------------------------------------
_drain_active = False
_drain_started_at = 0
_DRAIN_TIMEOUT = 60  # max seconds to wait before force-kill


def _enter_drain():
    """Enter drain mode: no new work, in-flight tasks get DRAIN_TIMEOUT s."""
    global _drain_active, _drain_started_at
    if _drain_active:
        return {"ok": False, "error": "already draining"}
    _drain_active = True
    _drain_started_at = time.time()
    _ledger("drain_enter")
    log("drain mode ACTIVATED", "drain")
    send_telegram("<b>Runner</b>: drain mode ACTIVATED — in-flight tasks finishing.")
    return {"ok": True, "timeout_s": _DRAIN_TIMEOUT}


def _exit_drain():
    global _drain_active, _drain_started_at
    _drain_active = False
    _drain_started_at = 0
    _ledger("drain_exit")
    log("drain mode DEACTIVATED", "drain")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Startup validation (kubernetes-readiness-inspired): check ports, files,
# env vars before accepting traffic. Returns list of issues.
# ---------------------------------------------------------------------------
REQUIRED_FILES = ["opencode_bot.py", "web_gateway.py", "providers.json", "runner-rules.json"]
REQUIRED_ENV = []


def _startup_validation():
    issues = []
    for fname in REQUIRED_FILES:
        fpath = os.path.join(DIR, fname)
        if not os.path.isfile(fpath):
            issues.append(f"missing file: {fname}")
    for ev in REQUIRED_ENV:
        if not os.environ.get(ev):
            issues.append(f"missing env: {ev}")
    for port_name, port_val in [("web gateway", 4357), ("mcp gateway", 8430)]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            if s.connect_ex(("127.0.0.1", int(port_val))) == 0:
                # only flag if the port holder is NOT a supervised process
                issues.append(f"port {port_val} ({port_name}) already in use")
            s.close()
        except Exception:
            pass
    return issues


# ---------------------------------------------------------------------------
# Daily fleet snapshot (openclaw-guardian-inspired): save fleet state to
# disk every 24h for debugging and trend analysis.
# ---------------------------------------------------------------------------
SNAPSHOT_DIR = os.path.join(DIR, "fleet_snapshots")
_snapshot_last_hour = -1


def _fleet_snapshot_daily():
    """Save a timestamped fleet state snapshot once per hour."""
    global _snapshot_last_hour
    now = time.localtime()
    if now.tm_hour == _snapshot_last_hour:
        return
    _snapshot_last_hour = now.tm_hour
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        snap = {
            "ts": ts,
            "uptime_s": int(time.time() - _runner_started),
            "runner_pid": os.getpid(),
            "processes": {},
        }
        try:
            import psutil as _ps
            snap["system"] = {
                "cpu_pct": _ps.cpu_percent(interval=0.1),
                "ram_used_gb": round(_ps.virtual_memory().used / (1024**3), 2),
                "ram_total_gb": round(_ps.virtual_memory().total / (1024**3), 2),
                "disk_free_gb": round(_ps.disk_usage("C:\\").free / (1024**3), 2),
            }
        except Exception:
            pass
        for name in PROCESSES:
            p = procs.get(name)
            alive = p and p.poll() is None
            row = {"state": _proc_status(name), "pid": p.pid if alive else None,
                   "uptime_s": int(time.time() - _started_at[name]) if alive and name in _started_at else 0,
                   "strikes": _crash_strikes.get(name, 0),
                   "restarts": _restart_count.get(name, 0)}
            if alive:
                try:
                    import psutil as _ps
                    pp = _ps.Process(p.pid)
                    row["ram_mb"] = round((pp.memory_info().rss or 0) / 1048576, 1)
                except Exception:
                    pass
            snap["processes"][name] = row
        fpath = os.path.join(SNAPSHOT_DIR, f"snap_{ts}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        _ledger("fleet_snapshot", ts=ts)
        # prune old snapshots (keep 72 = 3 days)
        snaps = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "snap_*.json")))
        for old in snaps[:-72]:
            os.remove(old)
    except Exception as e:
        log(f"fleet snapshot error: {e}", "snapshot")


class _CtrlHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _auth_ok(self):
        return self.headers.get("Authorization") == f"Bearer {CTRL_TOKEN}"

    def _send(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bad(self):
        self._send(401, {"error": "unauthorized"})

    def do_GET(self):
        if not self._auth_ok():
            return self._bad()
        path = self.path.split("?")[0].rstrip("/")
        try:
            if path == "/api/ping":
                self._send(200, {"ok": True, "pid": os.getpid(),
                                 "runner_up": time.time() - _runner_started < 120})
            elif path == "/api/health/live":
                self._send(200, {"ok": True, "uptime_s": int(time.time() - _runner_started)})
            elif path == "/api/health/ready":
                issues = _startup_validation()
                self._send(200 if not issues else 503,
                           {"ok": not bool(issues), "issues": issues})
            elif path == "/api/fleet":
                snap = _fleet_snapshot()
                snap["drain"] = _drain_active
                snap["health_web"] = health_check()
                snap["uptime_s"] = int(time.time() - _runner_started)
                snap["total_restarts"] = sum(_restart_count.values())
                self._send(200, snap)
            elif path == "/api/status":
                _write_status()
                with open(STATUS_FILE, encoding="utf-8") as f:
                    self._send(200, json.load(f))
            elif path == "/api/procs":
                self._send(200, _fleet_snapshot())
            elif path == "/api/ledger":
                self._send(200, {"ledger": _ledger_tail()})
            elif path == "/api/ports":
                self._send(200, {"ports": _scan_ports()})
            elif path == "/api/rules":
                self._send(200, _load_rules(force=True))
            elif path == "/api/schedule":
                self._send(200, _load_schedule())
            elif path == "/api/logs":
                self._send(200, _all_stderr_tails())
            elif path == "/api/health":
                self._send(200, _api_metrics())
            elif path == "/api/metrics":
                self._send(200, _api_metrics())
            elif path == "/api/restarts":
                self._send(200, _api_restarts())
            elif path == "/api/provider_health":
                try:
                    with open(PROVIDER_HEALTH_FILE, encoding="utf-8") as f:
                        data = json.load(f)
                    now = time.time()
                    for name, e in list(data.items()):
                        e["fails_1h"] = len([t for t in e.get("fails", []) if now - t < 3600])
                        e.pop("fails", None)
                    self._send(200, {"providers": data})
                except FileNotFoundError:
                    self._send(200, {"providers": {}})
            else:
                self._send(404, {"error": f"no route {path}"})
        except Exception as e:
            log(f"ctrl api GET error: {e}", "ctrl")
            self._send(500, {"error": str(e)[:300]})

    def do_POST(self):
        if not self._auth_ok():
            return self._bad()
        path = self.path.split("?")[0].rstrip("/")
        try:
            if path == "/api/drain":
                self._send(200, _enter_drain())
            elif path == "/api/drain/cancel":
                self._send(200, _exit_drain())
            elif path == "/api/restart":
                self._send(200, _api_restart_all())
            elif path.startswith("/api/restart/"):
                name = path[len("/api/restart/"):]
                self._send(200, _api_restart_one(name))
            elif path.startswith("/api/disable/"):
                name = path[len("/api/disable/"):]
                _disabled.add(name)
                _ledger("disabled_via_ctrl", proc=name)
                self._send(200, {"ok": True, "proc": name, "disabled": True})
            elif path.startswith("/api/enable/"):
                name = path[len("/api/enable/"):]
                _disabled.discard(name)
                _clear_backoff(name)
                _ledger("enabled_via_ctrl", proc=name)
                self._send(200, {"ok": True, "proc": name, "disabled": False})
            elif path == "/api/notify":
                length = int(self.headers.get("Content-Length", "0") or 0)
                body = json.loads(self.rfile.read(length).decode("utf-8", "replace") or "{}")
                text = str(body.get("text", ""))[:2000]
                ok = bool(text) and send_telegram(text)
                self._send(200, {"ok": ok, "sent": text[:120]})
            elif path == "/api/reload_rules":
                _load_rules(force=True)
                self._send(200, {"ok": True, "rules": _load_rules()})
            elif path == "/api/exec":
                if _drain_active:
                    self._send(503, {"ok": False, "error": "runner is draining"})
                    return
                length = int(self.headers.get("Content-Length", "0") or 0)
                try:
                    payload = json.loads(self.rfile.read(length).decode("utf-8", "replace") or "{}")
                except Exception:
                    self._send(400, {"ok": False, "error": "invalid JSON body"})
                    return
                self._send(200, _api_exec(payload))
            elif path.startswith("/api/free_port/"):
                try:
                    port = int(path[len("/api/free_port/"):])
                except Exception:
                    self._send(400, {"ok": False, "error": "port must be int"})
                    return
                freed, detail = free_port(port)
                _ledger("free_port_via_ctrl", port=port, freed=freed, detail=detail[:200])
                self._send(200, {"ok": freed, "port": port, "detail": detail})
            else:
                self._send(404, {"error": f"no route {path}"})
        except Exception as e:
            log(f"ctrl api POST error: {e}", "ctrl")
            self._send(500, {"error": str(e)[:300]})


def _start_ctrl_server():
    """Start the inbound control API on loopback :CTRL_PORT (daemon thread)."""
    global _ctrl_server
    try:
        _ctrl_server = ThreadingHTTPServer(("127.0.0.1", CTRL_PORT), _CtrlHandler)
        threading.Thread(target=_ctrl_server.serve_forever, daemon=True).start()
        log(f"control API listening on :{CTRL_PORT}", "ctrl")
        _ledger("ctrl_start", port=CTRL_PORT)
    except Exception as e:
        log(f"control API start failed: {e}", "ctrl")


def _fleet_snapshot():
    out = {}
    for name in PROCESSES:
        p = procs.get(name)
        out[name] = {
            "state": _proc_status(name),
            "pid": p.pid if p and p.poll() is None else None,
            "uptime_s": int(time.time() - _started_at[name]) if name in _started_at and p and p.poll() is None else 0,
            "strikes": _crash_strikes.get(name, 0),
            "backoff_s": int(_backoff_remaining(name)) if name in _next_start else 0,
            "disabled": name in _disabled,
            "guard_restarts": _guard_restarts.get(name, 0),
            "storm_held_s": _storm_remaining(name),
        }
    return {"processes": out, "runner_pid": os.getpid()}


def _ledger_tail(n=100):
    rows = []
    try:
        with open(PROC_LEDGER, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
    except Exception:
        pass
    return rows[-n:]


def _all_stderr_tails():
    tails = {}
    for name in PROCESSES:
        sf = os.path.join(DIR, f"{name}.stderr")
        if os.path.exists(sf):
            try:
                with open(sf, encoding="utf-8", errors="replace") as f:
                    tails[name] = f.read()[-1500:]
            except Exception:
                tails[name] = "(unreadable)"
    return {"stderr": tails}


def _api_restart_one(name):
    if name not in PROCESSES:
        return {"ok": False, "error": f"unknown process '{name}'"}
    if name in procs:
        _ledger("restart_via_ctrl", proc=name)
        kill_one(name)
    _clear_backoff(name)
    log(f"restart via ctrl: {name}", "ctrl")
    return {"ok": True, "proc": name}


def _api_exec(payload):
    """exec endpoint: run a short-lived shell command and return output.
    payload: {"cmd": <str or list>, "timeout": <sec>}"""
    cmd = payload.get("cmd")
    if not cmd:
        return {"ok": False, "error": "cmd required"}
    if isinstance(cmd, str):
        cmd = cmd.split()
    if not isinstance(cmd, list) or not cmd:
        return {"ok": False, "error": "cmd must be a non-empty string or list"}
    timeout = min(float(payload.get("timeout", 60) or 60), 600)
    cwd = payload.get("cwd") or DIR
    _ledger("exec_via_ctrl", cmd=" ".join(cmd)[:200])
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace",
                           shell=isinstance(payload.get("cmd"), str))
        return {
            "ok": r.returncode == 0,
            "rc": r.returncode,
            "stdout": (r.stdout or "")[-4000:],
            "stderr": (r.stderr or "")[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "stdout": "", "stderr": f"timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "rc": None, "stdout": "", "stderr": str(e)[:500]}


def _api_metrics():
    """Metrics endpoint: per-process CPU/RAM/uptime/restarts (psutil where
    available), plus runner + web gateway health."""
    try:
        import psutil as _ps
        have_ps = True
    except Exception:
        have_ps = False
    now = time.time()
    metrics = {"runner_pid": os.getpid(), "uptime_s": int(now - _runner_started),
               "health_web": health_check(), "psutil": have_ps, "processes": {}}
    for name in PROCESSES:
        p = procs.get(name)
        alive = p is not None and p.poll() is None
        row = {
            "state": _proc_status(name),
            "pid": p.pid if alive else None,
            "uptime_s": int(now - _started_at[name]) if alive and name in _started_at else 0,
            "strikes": _crash_strikes.get(name, 0),
            "restarts": _restart_count.get(name, 0),
            "backoff_s": int(_backoff_remaining(name)) if name in _next_start else 0,
            "guard_restarts": _guard_restarts.get(name, 0),
            "storm_held_s": _storm_remaining(name),
        }
        if alive and have_ps:
            try:
                pp = _ps.Process(p.pid)
                row["cpu_pct"] = round(pp.cpu_percent(interval=0.05) or 0, 1)
                row["ram_mb"] = round((pp.memory_info().rss or 0) / 1048576, 1)
            except Exception:
                pass
        metrics["processes"][name] = row
    metrics["managed"] = _managed_down_notified
    return metrics


def _api_restarts():
    """Restart history: recent crashes from crash_history.json + ctrl-triggered
    restarts from the ledger, newest first."""
    out = []
    try:
        history = load_crash_history()
        for c in history.get("crashes", [])[-30:]:
            out.append({"time": c.get("time"), "proc": c.get("process"),
                        "kind": "crash", "exit": c.get("exit_code"),
                        "detail": (c.get("stderr") or "")[:120]})
    except Exception:
        pass
    for row in _ledger_tail(500):
        ev = row.get("event", "")
        if ev in ("restart_via_ctrl", "restart_all_via_ctrl", "crash",
                  "managed_restart", "scheduled_start", "guard_restart",
                  "storm_hold", "no_restart", "git_restart"):
            out.append({"time": row.get("ts"), "proc": row.get("proc"),
                        "kind": ev, "exit": row.get("exit"),
                        "reason": row.get("reason")})
    out.sort(key=lambda r: r.get("time") or "", reverse=True)
    return {"restarts": out[:50], "total_crashes": load_crash_history().get("total", 0)}


def _api_restart_all():
    _ledger("restart_all_via_ctrl")
    log("restart-all via ctrl", "ctrl")
    kill_all()
    return {"ok": True}


def _clean_stale_lock():
    """Before spawning 'bot', remove .bot.lock if its PID is dead so the bot
    never sees a stale lock. If the PID is alive, leave it (real double-run
    guard that makes the new bot exit cleanly)."""
    lock = os.path.join(DIR, ".bot.lock")
    try:
        if not os.path.exists(lock):
            return
        with open(lock, encoding="utf-8") as f:
            pid = int(f.read().strip() or 0)
        if pid <= 0:
            os.remove(lock)
            return
        if os.name == "nt":
            import ctypes
            _h = ctypes.windll.kernel32.OpenProcess(1, 0, pid)
            if _h:
                ctypes.windll.kernel32.CloseHandle(_h)
                return  # alive
        else:
            os.kill(pid, 0)
            return  # alive
        os.remove(lock)
        log(f"removed stale .bot.lock (pid {pid} dead)", "proc")
    except Exception:
        try:
            os.remove(lock)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Managed external servers (outbound): poll runner-managed.json endpoints and
# restart them when they go unhealthy.
# ---------------------------------------------------------------------------
_managed_down_notified = {}


def _load_managed():
    try:
        if os.path.exists(MANAGED_FILE):
            with open(MANAGED_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("servers", [])
    except Exception as e:
        log(f"managed config error: {e}", "managed")
    return []


def _managed_check(srv):
    url = srv.get("url", "")
    if not url:
        return None
    ok = False
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=float(srv.get("timeout", 10))) as r:
            body = r.read().decode("utf-8", "replace")
            expect = srv.get("expect")
            ok = r.status == 200 and (not expect or expect in body)
    except Exception:
        ok = False
    return ok


def _managed_recover(srv):
    name = srv.get("name", "managed")
    if srv.get("cmd"):
        cmd = srv["cmd"]
        if isinstance(cmd, str):
            cmd = cmd.split()
        cwd = srv.get("cwd") or DIR
        log(f"managed {name}: unhealthy, restarting {' '.join(cmd)}", "managed")
        _ledger("managed_restart", proc=name)
        try:
            subprocess.Popen(cmd, cwd=cwd, creationflags=0x00000008 | 0x00000200 if os.name == "nt" else 0,
                             stderr=subprocess.STDOUT)
            return True
        except Exception as e:
            log(f"managed {name} restart failed: {e}", "managed")
            return False
    return False


def _check_managed_servers():
    """Poll every managed server; on unhealthy transition, restart it and
    notify once (notify repeats only after it recovers then fails again)."""
    for srv in _load_managed():
        name = srv.get("name", "managed")
        ok = _managed_check(srv)
        if ok is None:
            continue
        prev = _managed_down_notified.get(name, False)
        if ok:
            if prev:
                log(f"managed {name}: healthy again", "managed")
                _ledger("managed_ok", proc=name)
            _managed_down_notified[name] = False
            continue
        if prev:
            continue
        _managed_down_notified[name] = True
        log(f"managed {name}: UNHEALTHY", "managed")
        _ledger("managed_down", proc=name, url=srv.get("url", ""))
        if _can_notify(f"managed_{name}"):
            send_telegram(f"<b>Runner</b>: managed server <code>{name}</code> "
                          f"is unhealthy (<i>{srv.get('url', '')}</i>)")
        if _rule(name, "selfheal", False) or srv.get("restart", False):
            _managed_recover(srv)

last_hashes = file_hashes()
procs = {}
first = True
restart_times = []
_runner_started = time.time()
_health_rows = []
bot_env = load_dotenv()

# Refresh the merged servers.json once at startup so the supervised mcp
# gateway picks up any newly built reference servers.
if "mcp" in PROCESSES and os.path.isfile(_mcp_pack):
    try:
        _rc = subprocess.run([sys.executable, _mcp_pack, "config"],
                             cwd=DIR, capture_output=True, text=True, timeout=60)
        if _rc.returncode != 0:
            log(f"mcp config refresh failed: {_rc.stdout[-300:]} {_rc.stderr[-300:]}", "proc")
    except Exception as _e:
        log(f"mcp config refresh error: {_e}", "proc")

# androidllm local model server (Termux/phone). Only supervised where the
# androidllm-serve binary exists AND a model is available (default shard dir
# or a current_model.json state from a previous switch); auto-disabled
# on machines where androidllm isn't installed.
_androidllm_dir = bot_env.get("ANDROIDLLM_DIR", os.path.expanduser("~/androidllm"))
_androidllm_model = bot_env.get("ANDROIDLLM_MODEL", os.path.join(_androidllm_dir, "models", "qwen15"))
_androidllm_port = bot_env.get("ANDROIDLLM_PORT", "8080")
_androidllm_bin = shutil.which("androidllm-serve")
_androidllm_state = androidllm_models.state_path(bot_env)
_androidllm_state_ts = None
_androidllm_enabled = bool(_androidllm_bin) and (os.path.isdir(_androidllm_model) or os.path.exists(_androidllm_state))
if _androidllm_enabled:
    PROCESSES["androidllm"] = None  # real cmd computed per start via _androidllm_cmd()
    log(f"androidllm supervision enabled (default {_androidllm_model}, :{_androidllm_port})", "proc")
    try:
        _androidllm_state_ts = os.path.getmtime(_androidllm_state)
    except OSError:
        _androidllm_state_ts = None
else:
    log(f"androidllm supervision disabled (binary={bool(_androidllm_bin)}, model={os.path.isdir(_androidllm_model)})", "proc")

# deep-memory-ai ("dma") — secondary androidllm: an OpenAI-compatible
# memory server on :8101 running from the sibling deep-memory-ai repo.
# Supervised only on hosts that have the repo + its venv (Windows desktop).
_DMA_DIR = os.environ.get("DMA_DIR", os.path.join(_PARENT, "deep-memory-ai"))
_DMA_PORT = os.environ.get("DMA_PORT", "8101")
_DMA_PY = os.path.join(_DMA_DIR, "venv", "Scripts", "python.exe")
if not os.path.isfile(_DMA_PY):
    _DMA_PY = os.path.join(_DMA_DIR, ".venv", "Scripts", "python.exe")
_dma_serve = os.path.join(_DMA_DIR, "serve.py")
if os.path.isfile(_dma_serve) and os.path.isfile(_DMA_PY):
    PROCESSES["dma"] = [_DMA_PY, _dma_serve, "--port", _DMA_PORT]
    log(f"dma supervision enabled (deep-memory on :{_DMA_PORT})", "proc")
else:
    log(f"dma supervision disabled (serve.py/venv missing at {_DMA_DIR})", "proc")

def _androidllm_cmd():
    st = androidllm_models.read_state(bot_env)
    model_path = st.get("path") or _androidllm_model
    return [_androidllm_bin, "--model", model_path, "--port", _androidllm_port]

def _androidllm_env():
    """Per-model ANDROIDLLM_* defaults (threads, keep layers, prefix KV...)
    merged over the base env; explicit env vars win."""
    env = dict(bot_env)
    st = androidllm_models.read_state(bot_env)
    model_id = st.get("id") or ""
    for k, v in androidllm_models.model_defaults(model_id).items():
        env.setdefault(k, v)
    return env

def kill_all(reason="kill_all"):
    """Graceful cascade: run pre_stop hooks, terminate children newest-first,
    then force-kill leftovers (Supervisor/forever pattern)."""
    global procs
    names = list(procs.keys())
    for name in reversed(names):
        _intentional_kills.add(name)
        _pre_stop(name)
        _ledger("stop", proc=name, reason=reason)
        try: procs[name].terminate()
        except: pass
    time.sleep(1)
    for name in names:
        try: procs[name].kill()
        except: pass
    procs.clear()
    time.sleep(1)

def kill_one(name, reason="kill_one", graceful=True):
    """Terminate one supervised process gracefully: optional pre_stop hook,
    SIGTERM, wait grace_timeout_s, then SIGKILL. Returns True if it existed."""
    if name not in procs:
        return False
    p = procs[name]
    _intentional_kills.add(name)
    _ledger("stop", proc=name, reason=reason)
    if graceful:
        _pre_stop(name)
    try: p.terminate()
    except: pass
    grace = max(1, int(_rule(name, "grace_timeout_s", 3) or 3))
    try:
        p.wait(timeout=grace)
    except Exception:
        try:
            p.kill()
            _ledger("stop_forced", proc=name, reason=reason)
        except Exception:
            pass
    try:
        p.wait(timeout=3)
    except Exception:
        pass
    procs.pop(name, None)
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        try:
            with open(STATUS_FILE, encoding="utf-8") as f:
                print(f.read())
        except FileNotFoundError:
            print(f"no status file yet at {STATUS_FILE}")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "ports":
        # port-whisperer-inspired: list listening ports w/ owning process,
        # flag supervised ones. `runner.py ports <port>` filters to one port.
        _load_rules(force=True)
        want = sys.argv[2] if len(sys.argv) > 2 else None
        rows = _scan_ports()
        for row in rows:
            if want is not None and str(row.get("port")) != str(want):
                continue
            mark = ""
            if row.get("supervised"):
                mark = "  <-- supervised"
            elif row.get("managed"):
                mark = "  <-- managed"
            print(f"  {row['proto']:<4} :{row['port']:<6} pid {row['pid']:<8} {row['proc'] or '?'}{mark}")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "freemodels":
        # force a free-model check right now (announces + prints events).
        # `runner.py freemodels dry` scans without sending Telegram messages.
        _load_rules(force=True)
        load_dotenv()
        dry = len(sys.argv) > 2 and sys.argv[2] == "dry"
        ev = free_model_watcher.check_now(
            bot_token=None if dry else BOT_TOKEN, owner_id=OWNER_ID, dry=dry)
        print(json.dumps(ev, indent=1))
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "digest":
        # build + send the daily fleet digest right now
        _load_rules(force=True)
        load_dotenv()
        print(_build_daily_digest())
        if not (len(sys.argv) > 2 and sys.argv[2] == "dry"):
            tok = BOT_TOKEN or os.environ.get("TELEGRAM_BOT_TOKEN", "")
            oid = OWNER_ID or os.environ.get("OWNER_ID", "")
            if tok and oid:
                send_telegram(_build_daily_digest())
                print("(sent to Telegram)")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        # one-shot fleet triage: heartbeat, procs, disk, crashes, freemodels
        print("=== runner doctor ===")
        try:
            with open(HEARTBEAT_FILE, encoding="utf-8") as f:
                hb = json.load(f)
            age = time.time() - hb.get("ts", 0)
            state = "OK" if age < 120 else "STALLED"
            print(f"heartbeat : {age:.0f}s old [{state}] (uptime {hb.get('uptime_s', '?')}s, "
                  f"restarts {hb.get('total_restarts', '?')})")
        except FileNotFoundError:
            print("heartbeat : MISSING (runner never ran here)")
        except Exception as e:
            print(f"heartbeat : error ({e})")
        try:
            with open(STATUS_FILE, encoding="utf-8") as f:
                st = json.load(f)
            for pname, pinfo in (st.get("processes") or {}).items():
                print(f"proc      : {pname:<10} {pinfo.get('state', '?')}")
        except Exception:
            print("status    : no status file yet")
        try:
            du = shutil.disk_usage(DIR)
            print(f"disk      : {du.free / 1e9:.1f}GB free / {du.total / 1e9:.0f}GB")
        except Exception:
            pass
        try:
            with open(CRASH_HISTORY, encoding="utf-8") as f:
                hist = json.load(f)
            rows = hist[-5:] if isinstance(hist, list) else []
            print(f"crashes   : {len(hist) if isinstance(hist, list) else '?'} total, last {len(rows)}:")
            for c in rows:
                if isinstance(c, dict):
                    print(f"  - {c.get('ts', '?')} {c.get('proc', '?')}: {str(c.get('error', ''))[:70]}")
        except Exception:
            print("crashes   : none recorded")
        try:
            fm = free_model_watcher.load_state()
            adopted = list((fm.get("adopted") or {}).keys())
            print(f"freemodels: {len(fm.get('seen', {}))} tracked, adopted: {', '.join(adopted) or 'none'}")
        except Exception as e:
            print(f"freemodels: error ({e})")
        am_line = _androidllm_status_line()
        if am_line:
            print(f"androidllm : {am_line}")
        import urllib.request as _ur
        try:
            req = _ur.Request(f"http://127.0.0.1:{CTRL_PORT}/api/health/live",
                              headers={"Authorization": f"Bearer {CTRL_TOKEN}"})
            with _ur.urlopen(req, timeout=3) as r:
                print(f"ctrl api  : UP on :{CTRL_PORT}")
        except Exception:
            print(f"ctrl api  : DOWN on :{CTRL_PORT} (runner not running?)")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "incidents":
        # idea #17: readable incident timeline from proc-ledger.jsonl
        # usage: runner.py incidents [YYYY-MM-DD]   (default: today)
        target = sys.argv[2] if len(sys.argv) > 2 else time.strftime("%Y-%m-%d")
        for line in _incident_timeline(target):
            print(line)
        sys.exit(0)
    _load_rules(force=True)
    _rotate_fleet_logs()
    _start_ctrl_server()
    while True:
        _health_rows.append({
            "ts": time.strftime("%H:%M:%S"),
            "web_ok": health_check(),
            "procs": {n: (p.poll() is None) for n, p in procs.items()},
        })
        _health_rows = _health_rows[-120:]
        _write_status()
        _run_scheduled()
        _check_managed_servers()
        _check_resource_guards()
        _fleet_snapshot_daily()
        _maybe_check_free_models()
        _daily_digest()
        write_heartbeat()
        _stderr_sentry_tick()
        _disk_and_maintenance_tick()
        _hung_watchdog_tick()
        _deploy_guard_tick()
        _metrics_tick()
        _degrade_tick()
        _slo_tick()
        _androidllm_autopilot_tick()

        # drain mode: after timeout, force-kill all supervised processes
        if _drain_active and _drain_started_at:
            elapsed = time.time() - _drain_started_at
            if elapsed >= _DRAIN_TIMEOUT:
                log(f"drain timeout ({_DRAIN_TIMEOUT}s), force-killing fleet", "drain")
                _ledger("drain_force_kill", elapsed=elapsed)
                kill_all(reason="drain_timeout")
                _exit_drain()
            else:
                # don't start new work during drain
                time.sleep(2)
                continue
        if _androidllm_enabled:
            try:
                # consent gate: owner replied /approve -> apply the switch
                # (write_state bumps current_model.json mtime, restart below)
                applied = androidllm_models.apply_consent(bot_env)
                if applied:
                    log(f"consent approved: switching androidllm to {applied}", "proc")
            except Exception as e:
                log(f"consent apply error: {e}", "proc")
            try:
                _ts = os.path.getmtime(_androidllm_state)
            except OSError:
                _ts = None
            if _ts != _androidllm_state_ts:
                _androidllm_state_ts = _ts
                if "androidllm" in procs:
                    log("androidllm model switch detected, restarting serve...", "proc")
                    kill_one("androidllm")

        for name, base_cmd in PROCESSES.items():
            if name not in procs or procs[name].poll() is not None:
                was_running = name in procs and procs[name].poll() is not None
                remaining = _backoff_remaining(name)
                if remaining > 0:
                    log(f"{name} crash backoff, retry in {remaining:.0f}s", "proc")
                    continue
                storm = _storm_remaining(name)
                if storm > 0:
                    log(f"{name} held by restart-storm guard ({storm}s)", "proc")
                    continue
                if name in _disabled:
                    log(f"{name} disabled by rules, skipping start", "proc")
                    continue
                if name == "bot":
                    _clean_stale_lock()
                if name == "web":
                    free_port(4357)
                    time.sleep(1)
                cmd = _androidllm_cmd() if name == "androidllm" else base_cmd
                log(f"starting {name}...", "proc")
                _rotate_stderr(name)
                stderr_file = os.path.join(DIR, f"{name}.stderr")
                stderr_fh = open(stderr_file, "w", encoding="utf-8")
                proc_env = _androidllm_env() if name == "androidllm" else bot_env
                proc_cwd = MEMORY_REPO if name == "memory" else (_DMA_DIR if name == "dma" else DIR)
                proc = subprocess.Popen(cmd, cwd=proc_cwd, env=proc_env, stderr=stderr_fh)
                procs[name] = proc
                _started_at[name] = time.time()
                _restart_count[name] = _restart_count.get(name, 0) + 1
                _note_restart(name)
                _ledger("start", proc=name, pid=proc.pid, cmd=" ".join(cmd)[:200])
                threading.Thread(target=monitor_process, args=(name, proc), daemon=True).start()
                if name == "web":
                    for _ in range(6):
                        time.sleep(5)
                        if health_check():
                            log(f"healthy on {HEALTH_URL}", "proc")
                            break
                    else:
                        log(f"health check FAILED after start", "proc")
        if first:
            time.sleep(CHECK_INTERVAL)
            first = False
        else:
            time.sleep(_adaptive_sleep(CHECK_INTERVAL))

        current = file_hashes()
        changed_files = [f for f, h in current.items() if last_hashes.get(f) != h]
        for f in changed_files:
            log(f"changed: {os.path.basename(f)}", "watch")
        last_hashes = current

        changed_repos = git_update()
        git_changed = "bot" in changed_repos
        memory_git_changed = "memory" in changed_repos
        repo_to_proc = {"cyberdeck": "cyberdeck", "agent-01": "cyberdeck"}
        proc_restart = set()
        for _label in changed_repos - {"bot", "memory"}:
            _proc = repo_to_proc.get(_label)
            if _proc and _proc in PROCESSES:
                proc_restart.add(_proc)
        if changed_repos - {"bot", "memory"}:
            log(f"extra repo(s) synced: {', '.join(sorted(changed_repos - {'bot', 'memory'}))}", "git")

        web_dead = "web" in procs and procs["web"].poll() is not None and not health_check()

        if git_changed:
            if not _validate_repo_change("bot", DIR):
                last_hashes = file_hashes()
            else:
                now = time.time()
                restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
                if len(restart_times) >= MAX_RESTARTS:
                    log(f"max restarts ({MAX_RESTARTS}) exceeded in {RESTART_WINDOW}s, sleeping 60s", "proc")
                    time.sleep(60)
                    restart_times.clear()
                restart_times.append(now)
                log(f"git update, restarting all processes...", "proc")
                _ledger("git_restart", proc="all")
                _deploy_guard_arm()
                kill_all(reason="git_restart")
                last_hashes = file_hashes()
        elif memory_git_changed:
            log(f"memory repo updated, restarting memory daemon...", "proc")
            if not _validate_repo_change("memory", MEMORY_REPO):
                pass
            else:
                kill_one("memory")
        elif proc_restart:
            for _proc in sorted(proc_restart):
                log(f"repo update, restarting {_proc}...", "proc")
                _entry = _repo_updater.read_entry(_proc) or {}
                _path = _entry.get("path") if isinstance(_entry, dict) else None
                if _path and os.path.isdir(_path):
                    if not _validate_repo_change(_proc, _path):
                        continue
                kill_one(_proc)
        elif changed_files:
            code_changed = any(os.path.basename(f) in ("opencode_bot.py", "web_gateway.py", "bot_features.py", "bot_to_bot_agent.py", "providers.json") for f in changed_files)
            cyberdeck_changed = any(os.path.basename(f) in ("cyberdeck_bot.py", "cyberdeck_agent.py") for f in changed_files)
            mcp_changed = any(os.path.basename(f) in ("mcp_servers.py",) for f in changed_files)
            if code_changed:
                log(f"code changed, restarting bot+web...", "proc")
                kill_one("bot", reason="code_changed")
                kill_one("web", reason="code_changed")
            if cyberdeck_changed:
                log(f"cyberdeck changed, restarting cyberdeck...", "proc")
                kill_one("cyberdeck", reason="code_changed")
            if mcp_changed:
                log(f"mcp pack changed, restarting mcp...", "proc")
                kill_one("mcp", reason="code_changed")
        elif web_dead:
            log(f"web not responding, restarting web only...", "health")
            kill_one("web", reason="web_health")
