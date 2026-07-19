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
        for issue in issues:
            print(f"[security] {issue}")
            logging.warning(f"[security] {issue}")
    if len(issues) > 2:
        print(f"[security] WARNING: {len(issues)} hardcoded API keys found. Use environment variables or encrypted storage.")
        logging.warning(f"[security] {len(issues)} hardcoded API keys found. Use environment variables or encrypted storage.")

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

def log(msg):
    print(msg)
    logging.info(msg)

def file_hashes():
    h = {}
    for f in glob.glob(os.path.join(DIR, "*.py")) + glob.glob(os.path.join(DIR, "*.json")) + glob.glob(os.path.join(DIR, "whatsapp", "*.js")):
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
            log(f"[runner] not a git repo: {r.stderr.strip()}")
            return False
        old_head = r.stdout.strip()
        subprocess.run(["git", "stash", "--include-untracked"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        r = subprocess.run(["git", "fetch", "--all"], cwd=DIR, capture_output=True, text=True, timeout=30, encoding="utf-8")
        if r.returncode != 0:
            log(f"[runner] git fetch failed: {r.stderr.strip()}")
            return False
        r = subprocess.run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        if r.returncode != 0:
            default_branch = "origin/master"
        else:
            ref = r.stdout.strip()
            default_branch = ref.replace("refs/remotes/", "")
        r = subprocess.run(["git", "log", "--oneline", "-3", default_branch], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        log(f"[runner] remote commits: {r.stdout.strip()}")
        r = subprocess.run(["git", "reset", "--hard", default_branch], cwd=DIR, capture_output=True, text=True, timeout=30, encoding="utf-8")
        r2 = subprocess.run(["git", "rev-parse", "HEAD"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        new_head = r2.stdout.strip()
        if new_head == old_head:
            return False
        log(f"[runner] updated: {old_head[:8]}..{new_head[:8]}")
        r3 = subprocess.run(["git", "log", "--oneline", "-3"], cwd=DIR, capture_output=True, text=True, timeout=15, encoding="utf-8")
        for line in r3.stdout.strip().split("\n"):
            line = line.strip()
            if line:
                log(f"[runner]   {line}")
        return True
    except Exception as e:
        log(f"[runner] git update failed: {e}")
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
    msg = f"[runner] {name} crashed with exit code {exit_code}, restarting..."
    log(msg)
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
            log(f"[runner] starting {name}...")
            proc = subprocess.Popen(cmd, cwd=DIR)
            procs[name] = proc
            threading.Thread(target=monitor_process, args=(name, proc), daemon=True).start()
            if name == "web":
                for _ in range(6):
                    time.sleep(5)
                    if health_check():
                        log(f"[runner] OK web gateway healthy on {HEALTH_URL}")
                        break
                else:
                    log(f"[runner] WARNING web gateway health check failed after start")
    if first:
        time.sleep(CHECK_INTERVAL)
        first = False
    else:
        time.sleep(CHECK_INTERVAL // 2 if not health_check() else CHECK_INTERVAL)

    changed = False
    current = file_hashes()
    for f, h in current.items():
        if last_hashes.get(f) != h:
            log(f"[runner] change detected in {os.path.basename(f)}")
            changed = True
    last_hashes = current

    if git_update():
        changed = True

    if not health_check() and "web" in procs and procs["web"].poll() is not None:
        log(f"[runner] web gateway not responding, marking for restart")
        changed = True

    if changed:
        now = time.time()
        restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
        if len(restart_times) >= MAX_RESTARTS:
            log(f"[runner] max restarts ({MAX_RESTARTS}) exceeded in {RESTART_WINDOW}s, sleeping 60s")
            time.sleep(60)
            restart_times.clear()
        restart_times.append(now)
        log("[runner] update found, restarting processes...")
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
