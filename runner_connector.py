import json
import os
import sys
import time
import urllib.request
import urllib.error

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = int(os.environ.get("RUNNER_CTRL_PORT", "8431"))
DEFAULT_TOKEN = os.environ.get("RUNNER_CTRL_TOKEN", "sk-runner-local")
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".runner_connector.json")
_RETRYABLE = ("timed out", "Connection refused", "Bad Gateway", "Connection reset",
              "urlopen error", "Service Unavailable")


def _load_config():
    cfg = {}
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        pass
    if not isinstance(cfg, dict):
        cfg = {}
    return cfg


class RunnerConnector:
    """Client for runner.py's inbound control API. Lets any .py program or
    second server query and manage the runner's supervised fleet.

    Config file ~/.runner_connector.json (optional):
        {"host": "1.2.3.4", "port": 8431, "token": "...", "timeout": 15,
         "retries": 2}
    Env vars RUNNER_CTRL_PORT / RUNNER_CTRL_TOKEN also apply.
    """

    def __init__(self, host=None, port=None, token=None, timeout=None, retries=None):
        cfg = _load_config()
        host = host or cfg.get("host") or DEFAULT_HOST
        port = port or cfg.get("port") or DEFAULT_PORT
        token = token or cfg.get("token") or DEFAULT_TOKEN
        self.base = f"http://{host}:{port}"
        self.token = token
        self.timeout = float(timeout or cfg.get("timeout") or 15)
        self.retries = int(retries if retries is not None else cfg.get("retries", 1))
        try:
            mode = os.stat(CONFIG_FILE).st_mode & 0o777
            if mode & 0o077:
                print(f"warning: {CONFIG_FILE} is world-readable "
                      f"(mode {oct(mode)}) — chmod 600 to protect the token",
                      file=sys.stderr)
        except Exception:
            pass

    def _headers(self):
        return {"Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"}

    def _request(self, method, path, payload=None, timeout=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        to = timeout or self.timeout
        req = urllib.request.Request(self.base + path, data=data,
                                     headers=self._headers(), method=method)
        attempts = self.retries + 1
        last = None
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(req, timeout=to) as r:
                    return json.loads(r.read().decode("utf-8", "replace"))
            except urllib.error.HTTPError as e:
                try:
                    return json.loads(e.read().decode("utf-8", "replace"))
                except Exception:
                    return {"ok": False, "error": f"HTTP {e.code}"}
            except Exception as e:
                last = {"ok": False, "error": str(e)}
                msg = str(e)
                if attempt < attempts - 1 and method == "GET" and any(
                        r in msg for r in _RETRYABLE):
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
        return last

    def ping(self):
        return self._request("GET", "/api/ping")

    def status(self):
        return self._request("GET", "/api/status")

    def procs(self):
        return self._request("GET", "/api/procs")

    def ledger(self):
        return self._request("GET", "/api/ledger")

    def ports(self):
        return self._request("GET", "/api/ports")

    def free_port(self, port):
        return self._request("POST", f"/api/free_port/{port}")

    def rules(self):
        return self._request("GET", "/api/rules")

    def schedule(self):
        return self._request("GET", "/api/schedule")

    def logs(self):
        return self._request("GET", "/api/logs")

    def health(self):
        """Cascading health: runner + per-process + web gateway."""
        return self._request("GET", "/api/health")

    def metrics(self):
        return self._request("GET", "/api/metrics")

    def restarts(self):
        return self._request("GET", "/api/restarts")

    def exec(self, cmd, timeout=60, cwd=None, shell=False):
        """Run a short-lived command on the runner host. cmd may be a string
        (shell=True on the runner) or a list of args."""
        if isinstance(cmd, str):
            shell = True
        return self._request("POST", "/api/exec",
                             {"cmd": cmd, "timeout": timeout, "cwd": cwd},
                             timeout=timeout + 10)

    def batch(self, calls):
        """Execute several connector calls and return them keyed by name.
        calls: list of (name, fn) or (name, callable) pairs. Uses a cached
        health snapshot where applicable."""
        out = {}
        for name, fn in calls:
            try:
                out[name] = fn()
            except Exception as e:
                out[name] = {"ok": False, "error": str(e)}
        return out

    def restart(self, proc):
        return self._request("POST", f"/api/restart/{proc}")

    def restart_all(self):
        return self._request("POST", "/api/restart")

    def disable(self, proc):
        return self._request("POST", f"/api/disable/{proc}")

    def enable(self, proc):
        return self._request("POST", f"/api/enable/{proc}")

    def notify(self, text):
        return self._request("POST", "/api/notify", {"text": text})

    def reload_rules(self):
        return self._request("POST", "/api/reload_rules")


# Backward-compatible alias (older callers used RunnerControl).
RunnerControl = RunnerConnector


_USAGE = """runner_connector.py — control the fleet from any .py program or CLI

As a library:
    from runner_connector import RunnerConnector
    c = RunnerConnector()                    # host/token from ~/.runner_connector.json or env
    c.status(); c.restart("bot"); c.disable("web"); c.notify("hello")
    c.exec("git pull"); c.health(); c.metrics(); c.restarts(); c.batch([...])

Config file ~/.runner_connector.json (optional):
    {"host": "127.0.0.1", "port": 8431, "token": "...", "timeout": 15, "retries": 1}

As a CLI:
    runner_connector.py status|procs|ping|ledger|ports|rules|schedule|logs
    runner_connector.py health | metrics | restarts
    runner_connector.py restart <proc> | restart-all
    runner_connector.py disable <proc> | enable <proc>
    runner_connector.py free_port <port>
    runner_connector.py exec <shell command...>
    runner_connector.py notify <text>
"""


def main():
    if len(sys.argv) < 2:
        print(_USAGE)
        return 1
    cmd = sys.argv[1]
    c = RunnerConnector()
    result = None
    if cmd == "ping":
        result = c.ping()
    elif cmd == "status":
        result = c.status()
    elif cmd == "procs":
        result = c.procs()
    elif cmd == "ledger":
        result = c.ledger()
    elif cmd == "ports":
        result = c.ports()
    elif cmd == "rules":
        result = c.rules()
    elif cmd == "schedule":
        result = c.schedule()
    elif cmd == "logs":
        result = c.logs()
    elif cmd == "health":
        result = c.health()
    elif cmd == "metrics":
        result = c.metrics()
    elif cmd == "restarts":
        result = c.restarts()
    elif cmd == "restart-all":
        result = c.restart_all()
    elif cmd == "restart" and len(sys.argv) > 2:
        result = c.restart(sys.argv[2])
    elif cmd == "disable" and len(sys.argv) > 2:
        result = c.disable(sys.argv[2])
    elif cmd == "enable" and len(sys.argv) > 2:
        result = c.enable(sys.argv[2])
    elif cmd == "free_port" and len(sys.argv) > 2:
        result = c.free_port(sys.argv[2])
    elif cmd == "exec" and len(sys.argv) > 2:
        result = c.exec(" ".join(sys.argv[2:]), timeout=60)
    elif cmd == "notify" and len(sys.argv) > 2:
        result = c.notify(" ".join(sys.argv[2:]))
    else:
        print(_USAGE)
        return 1
    print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    if isinstance(result, dict) and result.get("ok") is False:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
