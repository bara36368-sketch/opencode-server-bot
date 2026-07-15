import subprocess, time, os, sys

DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
}

def git_pull():
    try:
        r = subprocess.run(["git", "pull"], cwd=DIR, capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout and "Already up to date" not in r.stdout:
            print(f"[runner] git pulled: {r.stdout.strip()}")
            return True
    except Exception as e:
        print(f"[runner] git check failed: {e}")
    return False

procs = {}
while True:
    for name, cmd in PROCESSES.items():
        if name not in procs or procs[name].poll() is not None:
            print(f"[runner] starting {name}...")
            procs[name] = subprocess.Popen(cmd, cwd=DIR)
    time.sleep(5)
    if git_pull():
        print("[runner] update found, restarting...")
        for p in procs.values():
            p.terminate()
        time.sleep(2)
        for p in procs.values():
            try: p.kill()
            except: pass
        procs.clear()
        time.sleep(1)
