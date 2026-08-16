"""mcp_servers.py — pack manager for the modelcontextprotocol/servers reference
collection, supervised by runner.py so both bots (opencode_bot + web/cyberdeck)
can use the same MCP tools over HTTP.

Design:
  - MCP_SERVERS_DIR  reference clone root (default sibling Desktop/mcp-servers)
  - MCP_GATEWAY_DIR  mcp-gateway HTTP bridge dir (default agents-places)
  - MCP_HTTP_PORT    bridge port (default 8430)
  - MCP_FS_ROOT      allowed directory for the filesystem server

Subcommands:
  python mcp_servers.py build   # install/compile the enabled servers
  python mcp_servers.py status  # show which servers are usable
  python mcp_servers.py config  # write the merged servers.json for the bridge
  python mcp_servers.py bridge  # run the HTTP MCP bridge (supervised by runner)

Zero-dependency (stdlib). Node + uv optional; servers that can't run are
simply skipped instead of ruining the bridge.
"""
import json
import os
import shutil
import subprocess
import sys
import time

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.expanduser("~"), ".mcp")
SERVER_ROOT = os.environ.get("MCP_SERVERS_DIR") or os.path.join(os.path.dirname(DIR), "mcp-servers")
GATEWAY_DIR = os.environ.get("MCP_GATEWAY_DIR") or os.path.join(
    os.path.expanduser("~"), "Desktop", "agents-places", "agents", "mcp-gateway")
CONFIG = os.path.join(DATA, "servers.json")
FS_ROOT = os.environ.get("MCP_FS_ROOT") or os.path.join(DATA, "mcp-fs")

# TypeScript reference servers (src/<name>/dist/index.js after npm build).
TS_SERVERS = ("everything", "filesystem", "memory", "sequentialthinking")

# Python reference servers (src/<name>/src/<module>/server.py, run with uv).
PY_SERVERS = {
    "git": {"module": "mcp_server_git", "dir": "src/git"},
    "time": {"module": "mcp_server_time", "dir": "src/time"},
    "fetch": {"module": "mcp_server_fetch", "dir": "src/fetch"},
}


def log(msg, section="mcp"):
    print("%s [%s] %s" % (time.strftime("%H:%M:%S"), section, msg))


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def run_cmd(cmd, cwd=None, timeout=900):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)[-2000:]
    except Exception as exc:
        return 1, str(exc)


def ts_dist(name):
    return os.path.join(SERVER_ROOT, "src", name, "dist", "index.js")


def py_project(name):
    return os.path.join(SERVER_ROOT, PY_SERVERS[name]["dir"], "pyproject.toml")


def py_venv(name):
    return os.path.join(SERVER_ROOT, PY_SERVERS[name]["dir"], ".venv")


def server_ready(name):
    if name in TS_SERVERS:
        return os.path.isfile(ts_dist(name))
    return os.path.isdir(py_venv(name))


def build():
    if not os.path.isdir(SERVER_ROOT):
        log("no reference clone at %s (git clone https://github.com/modelcontextprotocol/servers.git)"
            % SERVER_ROOT)
        return 1
    node = which("node")
    npm = which("npm", "npm.cmd")
    for name in TS_SERVERS:
        d = os.path.join(SERVER_ROOT, "src", name)
        if not os.path.isdir(d):
            log("skip %s: not in reference clone" % name)
            continue
        if server_ready(name) and os.path.isdir(os.path.join(d, "node_modules")):
            log("%s: already built" % name)
            continue
        if not node:
            log("skip %s: node not found" % name)
            continue
        if not npm:
            log("skip %s: npm not found" % name)
            continue
        for step in ([npm, "install", "--no-audit", "--no-fund"],
                     [npm, "run", "build"]):
            log("%s: %s..." % (name, step[1]))
            rc, out = run_cmd(step, cwd=d)
            if rc != 0:
                log("%s npm %s failed: %s" % (name, step[1], out.strip()[-400:]))
                break
        else:
            log("%s: built" % name)
    uv = which("uv")
    for name in PY_SERVERS:
        d = os.path.join(SERVER_ROOT, PY_SERVERS[name]["dir"])
        if not os.path.isdir(d):
            log("skip %s: not in reference clone" % name)
            continue
        if os.path.isdir(py_venv(name)):
            log("%s: already synced" % name)
            continue
        if not uv:
            log("skip %s: uv not found" % name)
            continue
        log("%s: uv sync..." % name)
        rc, out = run_cmd(["uv", "sync"], cwd=d)
        log("%s: %s" % (name, "synced" if rc == 0 else "sync failed: " + out.strip()[-300:]))
    return 0


def _cmd_ts(name):
    return {"cmd": [which("node") or "node", ts_dist(name)]}


def _cmd_filesystem():
    os.makedirs(FS_ROOT, exist_ok=True)
    return {"cmd": [which("node") or "node", ts_dist("filesystem"), FS_ROOT]}


def _cmd_py(name):
    d = os.path.join(SERVER_ROOT, PY_SERVERS[name]["dir"])
    return {"cmd": [which("uv") or "uv", "run", "python", "-m", PY_SERVERS[name]["module"]],
            "dir": d}


def merged_servers():
    """Reference servers that can actually run (node dist or uv venv)."""
    cfg = {}
    tg = os.path.join(os.path.expanduser("~"), "Desktop", "agents-places",
                      "agents", "telegram-mcp-ts", "telegram_mcp.py")
    if os.path.isfile(tg):
        for name in ("free-llm", "telegram", "cyberdeck"):
            cfg[name] = {"cmd": [sys.executable, tg, name]}
    mem = os.path.join(os.path.expanduser("~"), "Desktop", "agents-places",
                       "agents", "agent-memory-mcp", "memory_mcp.py")
    if os.path.isfile(mem):
        cfg["memory-agent"] = {"cmd": [sys.executable, mem]}
    for name in TS_SERVERS:
        if not server_ready(name):
            continue
        cfg[name] = _cmd_filesystem() if name == "filesystem" else _cmd_ts(name)
    for name in PY_SERVERS:
        if server_ready(name):
            cfg[name] = _cmd_py(name)
    return cfg


def write_config(verbose=False):
    cfg = merged_servers()
    if not cfg:
        log("no servers usable yet — run `python mcp_servers.py build` first")
        return 1
    os.makedirs(DATA, exist_ok=True)
    with open(CONFIG, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
    if verbose:
        log("wrote %s with %d servers: %s" % (CONFIG, len(cfg), ", ".join(sorted(cfg))))
    return 0


def status():
    print("server root: %s" % SERVER_ROOT)
    print("gateway:     %s" % GATEWAY_DIR)
    for name in TS_SERVERS:
        print("  %-18s %s" % (name, "ok" if server_ready(name) else "missing"))
    for name in PY_SERVERS:
        print("  %-18s %s" % (name, "ok" if server_ready(name) else "missing"))
    print("bridge config: %s" % CONFIG)
    return 0


# Registry of popular third-party MCP servers (punkpeye/awesome-mcp-servers
# inspired). name, command template, tags, description.
MCP_REGISTRY = [
    {"name": "playwright", "cmd": "npx -y @playwright/mcp@latest",
     "tags": ["browser", "web"], "desc": "Browser automation (click, fill, screenshot)."},
    {"name": "fetch", "cmd": "uvx mcp-server-fetch",
     "tags": ["web", "http"], "desc": "Fetch URLs and convert to markdown."},
    {"name": "git", "cmd": "uvx mcp-server-git",
     "tags": ["git", "vcs"], "desc": "Git repo read tools (log, status, diff)."},
    {"name": "time", "cmd": "uvx mcp-server-time",
     "tags": ["time", "tz"], "desc": "Timezone-aware current time."},
    {"name": "memory", "cmd": "npx -y @modelcontextprotocol/server-memory",
     "tags": ["memory", "kg"], "desc": "Knowledge-graph memory for agents."},
    {"name": "filesystem", "cmd": "npx -y @modelcontextprotocol/server-filesystem <ROOT>",
     "tags": ["fs", "files"], "desc": "Scoped file read/write."},
    {"name": "sequentialthinking", "cmd": "npx -y @modelcontextprotocol/server-sequential-thinking",
     "tags": ["reasoning"], "desc": "Structured multi-step reasoning."},
    {"name": "github", "cmd": "npx -y @modelcontextprotocol/server-github",
     "tags": ["github", "vcs"], "desc": "GitHub issues/PRs/repos tools."},
    {"name": "postgres", "cmd": "uvx mcp-server-postgres --connection <DSN>",
     "tags": ["db", "sql"], "desc": "PostgreSQL read-only queries."},
    {"name": "sqlite", "cmd": "uvx mcp-server-sqlite --db-path <PATH>",
     "tags": ["db", "sql"], "desc": "SQLite local database tools."},
    {"name": "brave-search", "cmd": "npx -y @modelcontextprotocol/server-brave-search",
     "tags": ["search"], "desc": "Brave web search (needs BRAVE_API_KEY)."},
    {"name": "slack", "cmd": "npx -y @modelcontextprotocol/server-slack",
     "tags": ["slack", "chat"], "desc": "Slack channel read/post tools."},
    {"name": "e2b", "cmd": "npx -y @e2b/mcp-server",
     "tags": ["sandbox", "code"], "desc": "Run code in sandboxed cloud VM."},
    {"name": "redis", "cmd": "npx -y @modelcontextprotocol/server-redis",
     "tags": ["cache", "db"], "desc": "Redis key/value tools."},
    {"name": "puppeteer", "cmd": "npx -y @modelcontextprotocol/server-puppeteer",
     "tags": ["browser", "web"], "desc": "Headless Chrome automation."},
    {"name": "gitlab", "cmd": "uvx mcp-server-gitlab",
     "tags": ["gitlab", "vcs"], "desc": "GitLab project tools."},
]


def search_registry(query):
    """Search the third-party MCP registry by keyword (registry-search idea)."""
    q = query.lower()
    out = []
    for s in MCP_REGISTRY:
        blob = (s["name"] + " " + s["desc"] + " " + " ".join(s["tags"])).lower()
        if q in blob:
            out.append(s)
    return out


def bridge():
    gate = os.path.join(GATEWAY_DIR, "gateway.py")
    if not os.path.isfile(gate):
        log("gateway.py not found at %s (set MCP_GATEWAY_DIR)" % gate)
        return 1
    if write_config() != 0:
        return 1
    port = os.environ.get("MCP_HTTP_PORT", "8430")
    token = os.environ.get("MCP_GATEWAY_TOKEN", "sk-local")
    cmd = [sys.executable, gate, "--port", port, "--token", token, "--servers", CONFIG]
    log("starting HTTP MCP bridge: %s" % " ".join(cmd))
    os.execv(sys.executable, cmd)
    return 0  # unreachable


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1
    sub = sys.argv[1]
    if sub == "build":
        return build()
    if sub == "status":
        return status()
    if sub == "config":
        return write_config(verbose=True)
    if sub == "bridge":
        return bridge()
    if sub == "search" and len(sys.argv) > 2:
        hits = search_registry(" ".join(sys.argv[2:]))
        if not hits:
            print("no MCP registry matches for '%s'" % " ".join(sys.argv[2:]))
            return 0
        for s in hits:
            print("  %-18s %s" % (s["name"], s["desc"]))
            print("    cmd: %s" % s["cmd"])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())