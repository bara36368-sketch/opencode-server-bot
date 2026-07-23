import subprocess, time, os, sys, hashlib, glob, urllib.request, json, logging, threading, re as _re

for _lib in ["httpx", "httpcore", "urllib3", "chardet"]:
    logging.getLogger(_lib).setLevel(logging.WARNING)

def _security_check():
    import ast
    issues = []
    setenv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setenv.sh")
    if os.path.exists(setenv):
        with open(setenv, encoding="utf-8") as f:
            content = f.read()
        keys_found = _re.findall(r'export\s+\w+_KEY=["\']([^"\']+)["\']', content)
        for k in keys_found:
            if k and k != "set-via-env-var" and not k.startswith("$"):
                issues.append(f"Hardcoded API key in setenv.sh (masked in log)")
        providers = os.path.join(os.path.dirname(os.path.abspath(__file__)), "providers.json")
        if os.path.exists(providers):
            with open(providers, encoding="utf-8") as f:
                pdata = json.load(f)
            for pname, pconf in pdata.items():
                if isinstance(pconf, dict) and "key" in pconf and pconf["key"] and pconf["key"] not in ("set-via-env-var", "skip-auth", ""):
                    issues.append(f"Hardcoded API key in providers.json for '{pname}'")
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

DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(DIR, "runner.log")
CRASH_LOG = os.path.join(DIR, "crash.log")
logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
}
CHECK_INTERVAL = 30
HEALTH_URL = "http://127.0.0.1:4357/api/providers"
MAX_RESTARTS = 5
RESTART_WINDOW = 300

def log(msg, section="runner"):
    ts = time.strftime("%H:%M:%S")
    print(f"{ts} [{section}] {msg}")
    logging.info(f"{ts} [{section}] {msg}")

def file_hashes():
    h = {}
    skip = {"version.json", "version_state.json", "runner.log", "crash.log"}
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
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        if r.returncode != 0:
            log(f"not a git repo: {r.stderr.strip()}", "git")
            return False
        old_head = r.stdout.strip()
        subprocess.run(["git", "stash", "--include-untracked"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "fetch", "--all"], cwd=DIR, capture_output=True, text=True, timeout=30, encoding="utf-8")
        if r.returncode != 0:
            log(f"fetch failed: {r.stderr.strip()}", "git")
            return False
        r = subprocess.run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        if r.returncode != 0:
            default_branch = "origin/master"
        else:
            ref = r.stdout.strip()
            default_branch = ref.replace("refs/remotes/", "")
        r = subprocess.run(["git", "log", "--oneline", "-3", default_branch], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        new_commits = [l for l in r.stdout.strip().split("\n") if l.strip()]
        if not new_commits:
            return False
        log("update detected", "git")
        for c in new_commits:
            log(f"  {c}", "git")
        log("pulling...", "git")
        r = subprocess.run(["git", "reset", "--hard", default_branch], cwd=DIR, capture_output=True, text=True, timeout=30, encoding="utf-8")
        r2 = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        new_head = r2.stdout.strip()
        if new_head == old_head[:len(new_head)]:
            return False
        log(f"success ({new_head}) is pulled!", "git")
        return True
    except Exception as e:
        log(f"update failed: {e}", "git")
    return False

def health_check():
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except:
        return False

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

def monitor_process(name, proc):
    proc.wait()
    exit_code = proc.returncode
    msg = f"{name} crashed (exit {exit_code}), restarting..."
    log(msg, "proc")
    with open(CRASH_LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

last_hashes = file_hashes()
procs = {}
first = True
restart_times = []

while True:
    for name, cmd in PROCESSES.items():
        if name not in procs or procs[name].poll() is not None:
            was_running = name in procs and procs[name].poll() is not None
            if name == "web":
                free_port(4357)
                time.sleep(1)
            log(f"starting {name}...", "proc")
            proc = subprocess.Popen(cmd, cwd=DIR)
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

    changed = False
    current = file_hashes()
    for f, h in current.items():
        if last_hashes.get(f) != h:
            log(f"changed: {os.path.basename(f)}", "watch")
            changed = True
    last_hashes = current

    if git_update():
        changed = True

    if not health_check() and "web" in procs and procs["web"].poll() is not None:
        log(f"web not responding, marking for restart", "health")
        changed = True

    if changed:
        now = time.time()
        restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
        if len(restart_times) >= MAX_RESTARTS:
            log(f"max restarts ({MAX_RESTARTS}) exceeded in {RESTART_WINDOW}s, sleeping 60s", "proc")
            time.sleep(60)
            restart_times.clear()
        restart_times.append(now)
        log(f"update found, restarting all processes...", "proc")
        proc_list = list(procs.values())
        for p in proc_list:
            try: p.terminate()
            except: pass
        time.sleep(2)
        for p in proc_list:
            try: p.kill()
            except: pass
        procs.clear()
        time.sleep(1)
        last_hashes = file_hashes()
