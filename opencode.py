#!/usr/bin/env python3
"""opencode.py — wire opencode (desktop coding agent) to the phone's
androidllm OpenAI-compatible server.

Usage:
    python opencode.py setup              # register provider + auth, print next step
    python opencode.py status             # phone health, active model, config state
    python opencode.py models             # list catalog ids the phone can serve
    python opencode.py run "<prompt>"     # non-interactive opencode run on the phone model
    python opencode.py routes             # phone-vs-cloud decision table

What it writes (both files are merged, never clobbered):
    ~/.config/opencode/opencode.json          -> provider["androidllm"]
    ~/.local/share/opencode/auth.json         -> { "androidllm": { "type": "api", "key": ... } }

Imports: stdlib only. Python 3.8+ (runs on the phone's Termux too).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    from androidllm_models import RECOMMENDED, active_model, recommended_ids
except ImportError:  # allow running from another cwd
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from androidllm_models import RECOMMENDED, active_model, recommended_ids  # noqa: F811

PROVIDER_ID = "androidllm"
OPENCODE_CONFIG = os.path.join(os.path.expanduser("~"), ".config", "opencode", "opencode.json")
OPENCODE_AUTH = os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "auth.json")
KEY_FILE = os.path.join(os.path.expanduser("~"), "androidllm", "api_key")


# ---------------------------------------------------------------- discovery

def endpoint(env=None):
    env = env or os.environ
    return (env.get("ANDROIDLLM_URL") or "http://127.0.0.1:8000").rstrip("/")


def api_key(env=None):
    env = env or os.environ
    if env.get("ANDROIDLLM_KEY"):
        return env["ANDROIDLLM_KEY"]
    try:
        with open(KEY_FILE, encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    except OSError:
        pass
    return "skip-auth"


def http_json(url, key=None, timeout=3.0):
    req = urllib.request.Request(url)
    if key:
        req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if not body:
            return {}
        try:
            return json.loads(body.decode("utf-8"))
        except ValueError:
            return {"raw": body.decode("utf-8", "replace")[:500]}


def health(env=None, timeout=3.0):
    """GET /health on the phone server. Returns a dict, or raises."""
    url = endpoint(env) + "/health"
    t0 = time.monotonic()
    data = http_json(url, key=api_key(env), timeout=timeout)
    data["latency_ms"] = int((time.monotonic() - t0) * 1000)
    return data


def phone_up(env=None):
    try:
        health(env, timeout=2.0)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- model pick

def pick_model(env=None, health_data=None):
    """Best model to point opencode at: the phone's active serving model if
    it is known, otherwise the LARGEST catalog model whose disk footprint
    fits the phone's reported RAM tier (headroom for the OS), else the
    smallest recommended model."""
    active = active_model(env)
    if active and active in recommended_ids():
        return active
    ram_gb = None
    if health_data:
        for k in ("ram_gb", "total_ram_gb", "mem_gb", "ram"):
            v = health_data.get(k)
            if isinstance(v, (int, float)) and v > 0:
                ram_gb = float(v)
                break
    if ram_gb:
        budget = ram_gb * 0.7  # keep headroom for the OS
        for m in reversed(RECOMMENDED):  # largest first
            if m["disk_gb"] <= budget:
                return m["id"]
    return RECOMMENDED[0]["id"]


# ---------------------------------------------------------------- config merge

def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def provider_patch(base_url, key, model_id):
    """The provider block opencode needs for an OpenAI-compatible endpoint."""
    m = next((x for x in RECOMMENDED if x["id"] == model_id), {})
    ctx = int(m.get("ctx", 32768) if m.get("ctx") else 32768)
    return {
        "npm": "@ai-sdk/openai-compatible",
        "name": "androidllm (phone)",
        "options": {
            "baseURL": base_url.rstrip("/") + "/v1",
            "apiKey": key,
        },
        "models": {
            model_id: {
                "name": m.get("repo", model_id),
                "limit": {"context": ctx, "output": 4096},
            }
        },
    }


def setup_config(base_url, key, model_id):
    """Merge provider into opencode.json + auth.json. Returns both paths."""
    cfg = read_json(OPENCODE_CONFIG)
    cfg.setdefault("provider", {})[PROVIDER_ID] = provider_patch(base_url, key, model_id)
    if "$schema" not in cfg:
        cfg["$schema"] = "https://opencode.ai/config.json"
    write_json(OPENCODE_CONFIG, cfg)

    auth = read_json(OPENCODE_AUTH)
    auth[PROVIDER_ID] = {"type": "api", "key": key}
    write_json(OPENCODE_AUTH, auth)
    return OPENCODE_CONFIG, OPENCODE_AUTH


# ---------------------------------------------------------------- commands

def cmd_setup(args, env=None):
    base = endpoint(env)
    key = api_key(env)
    try:
        h = health(env)
        print("phone:  UP  %s  (%d ms)" % (base, h.get("latency_ms", 0)))
        model = pick_model(env, h)
    except Exception as exc:
        print("phone:  DOWN  %s  (%s)" % (base, exc))
        model = pick_model(env)
    cfg, auth = setup_config(base, key, model)
    print("config: %s" % cfg)
    print("auth:   %s" % auth)
    print("model:  androidllm/%s" % model)
    print()
    print("next:   opencode run --model androidllm/%s \"<prompt>\"" % model)


def cmd_status(args, env=None):
    base = endpoint(env)
    try:
        h = health(env)
        print("phone   UP     %s  (%d ms)" % (base, h.get("latency_ms", 0)))
        for k in sorted(h.keys()):
            if k != "latency_ms":
                print("        %-12s %s" % (k, h[k]))
    except Exception as exc:
        print("phone   DOWN   %s  (%s)" % (base, exc))
    print("model   %s" % pick_model(env))
    cfg = read_json(OPENCODE_CONFIG)
    prov = cfg.get("provider", {}).get(PROVIDER_ID)
    print("provider configured: %s" % ("yes" if prov else "no"))
    auth = read_json(OPENCODE_AUTH)
    print("auth configured:     %s" % ("yes" if PROVIDER_ID in auth else "no"))


def cmd_models(args):
    for m in RECOMMENDED:
        print("%-14s %-8sGB  %s" % (m["id"], m["disk_gb"], m.get("note", "")))


def cmd_run(args, env=None):
    if not phone_up(env):
        print("phone is DOWN (%s) — start androidllm serve first, or use a cloud model." % endpoint(env))
        return 1
    model = args.model or pick_model(env)
    if not args.prompt:
        print("prompt required:  python opencode.py run \"<prompt>\"")
        return 2
    cmd = ["opencode", "run", "--model", "%s/%s" % (PROVIDER_ID, model)]
    if args.dir:
        cmd += ["--dir", args.dir]
    cmd.append(args.prompt)
    print("running:  %s" % " ".join(cmd))
    return subprocess.call(cmd)


def cmd_routes(args, env=None):
    up = phone_up(env)
    print("phone    %s   %s" % ("UP  " if up else "DOWN", endpoint(env)))
    print("route    %s" % ("androidllm/phone" if up else "cloud only"))
    if up:
        m = pick_model(env)
        print("model    androidllm/%s" % m)
        print("tip      coding-heavy tasks: keep phone on; chat-heavy: cloud is fine")


def cmd_omni(args):
    """Register the OMNI Gateway (:4455) as an opencode CLI provider.
    Uses the gateway's ranked fallback — model 'auto' always works."""
    base = "http://127.0.0.1:4455/v1"
    try:
        with urllib.request.urlopen("http://127.0.0.1:4455/api/free", timeout=5) as r:
            free = json.loads(r.read().decode()).get("free", [])
        top = free[0]["id"].split("/", 1)[1] if free else "auto"
    except Exception:
        top = "auto"
    cfg = read_json(OPENCODE_CONFIG)
    cfg.setdefault("provider", {})["omni"] = {
        "npm": "@ai-sdk/openai-compatible",
        "name": "OMNI Gateway (ranked free models)",
        "options": {"baseURL": base, "apiKey": "omni-local"},
        "models": {(top if top != "auto" else "auto"): {
            "name": "omni-ranked-auto",
            "limit": {"context": 131072, "output": 8192}}},
    }
    if "$schema" not in cfg:
        cfg["$schema"] = "https://opencode.ai/config.json"
    write_json(OPENCODE_CONFIG, cfg)
    auth = read_json(OPENCODE_AUTH)
    auth["omni"] = {"type": "api", "key": "omni-local"}
    write_json(OPENCODE_AUTH, auth)
    print("omni:   registered in %s" % OPENCODE_CONFIG)
    print("model:  omni/auto  (gateway picks best ranked free model)")
    print("next:   opencode run --model omni/auto \"<prompt>\"")
    print("chat UI: http://localhost:4455/chat")


def main(argv=None):
    p = argparse.ArgumentParser(prog="opencode.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="register phone provider in opencode config + auth")
    sub.add_parser("status", help="phone health + config state")
    sub.add_parser("models", help="list catalog models")
    sub.add_parser("routes", help="phone-vs-cloud decision table")
    sub.add_parser("omni", help="register OMNI Gateway (:4455) as opencode provider")
    run = sub.add_parser("run", help="non-interactive opencode run on the phone model")
    run.add_argument("prompt", nargs="?", default=None)
    run.add_argument("--model", default=None, help="catalog id, default = active/best")
    run.add_argument("--dir", default=None, help="working directory")
    args = p.parse_args(argv)

    if args.cmd == "setup":
        cmd_setup(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "models":
        cmd_models(args)
    elif args.cmd == "run":
        return cmd_run(args)
    elif args.cmd == "routes":
        cmd_routes(args)
    elif args.cmd == "omni":
        cmd_omni(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
