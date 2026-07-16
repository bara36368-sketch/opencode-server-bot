import subprocess, time, os, sys, hashlib, glob, urllib.request, json

DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
}
CHECK_INTERVAL = 30
HEALTH_URL = "http://127.0.0.1:4357/api/providers"

def file_hashes():
    h = {}
    for f in glob.glob(os.path.join(DIR, "*.py")) + glob.glob(os.path.join(DIR, "*.json")):
        try:
            with open(f, "rb") as fh:
                h[f] = hashlib.sha256(fh.read()).hexdigest()
        except:
            pass
    return h

def git_pull():
    try:
        r = subprocess.run(["git", "pull"], cwd=DIR, capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout and "Already up to date" not in r.stdout:
            print(f"[runner] git pulled: {r.stdout.strip()}")
            return True
    except Exception as e:
        print(f"[runner] git check failed: {e}")
    return False

def health_check():
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status == 200
    except:
        return False

def free_port(port):
    try:
        r = subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, timeout=5)
        if r.returncode == 0:
            print(f"[runner] freed port {port}")
    except:
        pass
    try:
        r = subprocess.run(["pkill", "-f", "web_gateway.py"], capture_output=True, timeout=5)
        if r.returncode == 0:
            print(f"[runner] killed stale web_gateway process")
    except:
        pass

last_hashes = file_hashes()
procs = {}
first = True

while True:
    for name, cmd in PROCESSES.items():
        if name not in procs or procs[name].poll() is not None:
            if name == "web":
                free_port(4357)
                time.sleep(1)
            print(f"[runner] starting {name}...")
            procs[name] = subprocess.Popen(cmd, cwd=DIR)
            if name == "web":
                time.sleep(3)
                if not health_check():
                    print(f"[runner] ⚠ web gateway health check failed after start")
                else:
                    print(f"[runner] ✓ web gateway healthy on {HEALTH_URL}")
    if first:
        time.sleep(CHECK_INTERVAL)
        first = False
    else:
        time.sleep(CHECK_INTERVAL // 2 if not health_check() else CHECK_INTERVAL)

    changed = False
    current = file_hashes()
    for f, h in current.items():
        if last_hashes.get(f) != h:
            print(f"[runner] change detected in {os.path.basename(f)}")
            changed = True
    last_hashes = current

    if git_pull():
        changed = True

    if not health_check() and "web" in procs and procs["web"].poll() is not None:
        print(f"[runner] web gateway not responding, marking for restart")
        changed = True

    if changed:
        print("[runner] update found, restarting...")
        for p in procs.values():
            p.terminate()
        time.sleep(2)
        for p in procs.values():
            try: p.kill()
            except: pass
        procs.clear()
        time.sleep(1)
        last_hashes = file_hashes()
