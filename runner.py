import subprocess, time, os, sys, hashlib, glob, urllib.request, json, logging, threading, re as _re, traceback, socket, shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import androidllm_models

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
    },
    "bot": {"max_strikes": 4, "selfheal": True},
    "web": {"max_strikes": 4, "selfheal": False},
    "mcp": {"max_strikes": 4, "selfheal": True},
    "androidllm": {
        "downgrade_on_oom": True,
        "selfheal": False,
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
    _next_start[name] = now + min(BACKOFF_BASE * (2 ** (strikes - 1)), BACKOFF_CAP)


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
            if path == "/api/restart":
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
                  "managed_restart", "scheduled_start"):
            out.append({"time": row.get("ts"), "proc": row.get("proc"),
                        "kind": ev, "exit": row.get("exit")})
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

def kill_all():
    global procs
    for name, p in list(procs.items()):
        _intentional_kills.add(name)
        _ledger("stop", proc=name, reason="kill_all")
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
        _intentional_kills.add(name)
        _ledger("stop", proc=name, reason="kill_one")
        try: procs[name].terminate()
        except: pass
        time.sleep(1)
        try: procs[name].kill()
        except: pass
        try: procs[name].wait(timeout=3)
        except: pass
        procs.pop(name, None)

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
    _load_rules(force=True)
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
                stderr_file = os.path.join(DIR, f"{name}.stderr")
                stderr_fh = open(stderr_file, "w", encoding="utf-8")
                proc_env = _androidllm_env() if name == "androidllm" else bot_env
                proc_cwd = MEMORY_REPO if name == "memory" else (_DMA_DIR if name == "dma" else DIR)
                proc = subprocess.Popen(cmd, cwd=proc_cwd, env=proc_env, stderr=stderr_fh)
                procs[name] = proc
                _started_at[name] = time.time()
                _restart_count[name] = _restart_count.get(name, 0) + 1
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
            time.sleep(CHECK_INTERVAL // 2 if not health_check() else CHECK_INTERVAL)

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
                kill_all()
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
                kill_one("bot")
                kill_one("web")
            if cyberdeck_changed:
                log(f"cyberdeck changed, restarting cyberdeck...", "proc")
                kill_one("cyberdeck")
            if mcp_changed:
                log(f"mcp pack changed, restarting mcp...", "proc")
                kill_one("mcp")
        elif web_dead:
            log(f"web not responding, restarting web only...", "health")
            kill_one("web")
