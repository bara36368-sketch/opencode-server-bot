import subprocess, time, os, sys, hashlib, glob, urllib.request, json, logging, threading, re as _re, traceback, socket, shutil

import androidllm_models

for _lib in ["httpx", "httpcore", "urllib3", "chardet"]:
    logging.getLogger(_lib).setLevel(logging.WARNING)

DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(DIR, "runner.log")
CRASH_LOG = os.path.join(DIR, "crash.log")
NOTIFY_COOLDOWN = 300
CRASH_HISTORY = os.path.join(DIR, "crash_history.json")

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

OWNER_ID = os.environ.get("OWNER_ID", "8585609360")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

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
            "bot_crash.txt", "bot.log", "security_warnings.txt"}
    for f in glob.glob(os.path.join(DIR, "*.py")) + glob.glob(os.path.join(DIR, "*.json")) + glob.glob(os.path.join(DIR, "whatsapp", "*.js")):
        if os.path.basename(f) in skip:
            continue
        try:
            with open(f, "rb") as fh:
                h[f] = hashlib.sha256(fh.read()).hexdigest()
        except:
            pass
    return h

def git_update():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode != 0:
            log(f"not a git repo: {r.stderr.strip()}", "git")
            return False
        old_head = r.stdout.strip()
        log("trying git pull...", "git")
        r = subprocess.run(["git", "pull", "--ff-only", "--depth=1"], cwd=DIR, capture_output=True, text=True, timeout=30, encoding="utf-8")
        if r.returncode == 0 and "Already up to date" not in r.stdout:
            r2 = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
            new_head = r2.stdout.strip()
            log(f"pull success ({new_head})", "git")
            return True
        log("pull: no updates or failed, trying fetch+reset...", "git")
        subprocess.run(["git", "stash", "--include-untracked"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        r = subprocess.run(["git", "fetch", "--depth=1", "origin"], cwd=DIR, capture_output=True, text=True, timeout=20, encoding="utf-8")
        if r.returncode != 0:
            log(f"fetch failed: {r.stderr.strip()}", "git")
            return False
        r = subprocess.run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode != 0:
            default_branch = "origin/master"
        else:
            ref = r.stdout.strip()
            default_branch = ref.replace("refs/remotes/", "")
        r = subprocess.run(["git", "log", "--oneline", "-3", default_branch], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        new_commits = [l for l in r.stdout.strip().split("\n") if l.strip()]
        if not new_commits:
            return False
        log("update detected", "git")
        for c in new_commits:
            log(f"  {c}", "git")
        log("resetting...", "git")
        r = subprocess.run(["git", "reset", "--hard", default_branch], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r2 = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        new_head = r2.stdout.strip()
        if new_head == old_head[:len(new_head)]:
            return False
        log(f"success ({new_head}) is pulled!", "git")
        return True
    except Exception as e:
        log(f"update failed: {e}", "git")
    return False

def git_push_fix(message="auto-fix: runner patch"):
    try:
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode != 0:
            return False
        subprocess.run(["git", "add", "-A"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=DIR, capture_output=True, text=True, timeout=10, encoding="utf-8")
        if r.returncode == 0:
            log("nothing to push", "git")
            return False
        subprocess.run(["git", "commit", "-m", message, "--no-verify"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "push", "--force-with-lease"], cwd=DIR, capture_output=True, text=True, timeout=60, encoding="utf-8")
        if r.returncode == 0:
            log("auto-push successful", "git")
            return True
        else:
            log(f"push failed: {r.stderr.strip()}", "git")
            return False
    except Exception as e:
        log(f"git push error: {e}", "git")
        return False

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
    if sys.platform == "win32":
        try:
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=10, encoding="utf-8")
            for line in r.stdout.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 5 and f":{port}" in parts[1]:
                    pid = parts[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, timeout=5)
        except Exception:
            pass
    else:
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, timeout=5)
        except Exception:
            pass
        try:
            subprocess.run(["pkill", "-f", "web_gateway.py"], capture_output=True, timeout=5)
        except Exception:
            pass

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
    """On OOM crash: switch current_model.json to the next smaller sharded
    model. Returns (new_model_id | None, message)."""
    global _androidllm_state_ts
    if not _is_oom_crash(exit_code, stderr_text):
        return None, None
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
    androidllm_models.write_state(nxt, androidllm_models.shard_dir(nxt, bot_env))
    _down_last["ts"] = now
    _record_downgrade()
    try:
        _androidllm_state_ts = os.path.getmtime(_androidllm_state)
    except OSError:
        _androidllm_state_ts = None
    return nxt, f"OOM downgrade {cur} -> {nxt}"

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
    msg = f"{name} crashed (exit {exit_code})"
    log(msg, "proc")
    with open(CRASH_LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    analysis = analyze_crash(name, exit_code, stderr_text)
    diagnosis_str = "\n".join(analysis["diagnosis"])
    downgrade_info = None
    if name == "androidllm":
        try:
            nxt, msg = _maybe_downgrade_androidllm(exit_code, stderr_text)
            if nxt:
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
CHECK_INTERVAL = 15
HEALTH_URL = "http://127.0.0.1:4357/api/providers"
MAX_RESTARTS = 5
RESTART_WINDOW = 300

last_hashes = file_hashes()
procs = {}
first = True
restart_times = []
bot_env = load_dotenv()

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

def kill_all():
    global procs
    for name, p in list(procs.items()):
        try: p.terminate()
        except: pass
    time.sleep(1)
    for name, p in list(procs.items()):
        try: p.kill()
        except: pass
    procs.clear()
    time.sleep(1)

def kill_one(name):
    if name in procs:
        try: procs[name].terminate()
        except: pass
        time.sleep(1)
        try: procs[name].kill()
        except: pass
        try: procs[name].wait(timeout=3)
        except: pass
        procs.pop(name, None)

if __name__ == "__main__":
    while True:
        if _androidllm_enabled:
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
                if name == "web":
                    free_port(4357)
                    time.sleep(1)
                cmd = _androidllm_cmd() if name == "androidllm" else base_cmd
                log(f"starting {name}...", "proc")
                stderr_file = os.path.join(DIR, f"{name}.stderr")
                stderr_fh = open(stderr_file, "w", encoding="utf-8")
                proc_env = _androidllm_env() if name == "androidllm" else bot_env
                proc = subprocess.Popen(cmd, cwd=DIR, env=proc_env, stderr=stderr_fh)
                procs[name] = proc
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
            time.sleep(CHECK_INTERVAL // 2 if not health_check() else CHECK_INTERVAL)

        current = file_hashes()
        changed_files = [f for f, h in current.items() if last_hashes.get(f) != h]
        for f in changed_files:
            log(f"changed: {os.path.basename(f)}", "watch")
        last_hashes = current

        git_changed = git_update()

        web_dead = "web" in procs and procs["web"].poll() is not None and not health_check()

        if git_changed:
            now = time.time()
            restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
            if len(restart_times) >= MAX_RESTARTS:
                log(f"max restarts ({MAX_RESTARTS}) exceeded in {RESTART_WINDOW}s, sleeping 60s", "proc")
                time.sleep(60)
                restart_times.clear()
            restart_times.append(now)
            log(f"git update, restarting all processes...", "proc")
            kill_all()
            last_hashes = file_hashes()
        elif changed_files:
            code_changed = any(os.path.basename(f) in ("opencode_bot.py", "web_gateway.py", "bot_features.py", "bot_to_bot_agent.py", "providers.json") for f in changed_files)
            cyberdeck_changed = any(os.path.basename(f) in ("cyberdeck_bot.py", "cyberdeck_agent.py") for f in changed_files)
            if code_changed:
                log(f"code changed, restarting bot+web...", "proc")
                kill_one("bot")
                kill_one("web")
            if cyberdeck_changed:
                log(f"cyberdeck changed, restarting cyberdeck...", "proc")
                kill_one("cyberdeck")
        elif web_dead:
            log(f"web not responding, restarting web only...", "health")
            kill_one("web")
