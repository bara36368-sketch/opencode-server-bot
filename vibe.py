"""VIBE — your free vibe-coding agent.

Rides the local free stack only:
    - OMNI Gateway :4455 ranked free models (coder-first selection)
    - OmniRoute :20128 as secondary
    - Ollama :20200/:11434 local dolphin3-coder as last resort
Zero paid APIs. Zero keys beyond what this machine already has.

Usage:
    python vibe.py "build a snake game in ./snake"
    python vibe.py --dir ./myproject "add unit tests for utils.py"
    python vibe.py --model auto "..."     force a specific provider/model id

Agent loop: the model proposes JSON tool calls; vibe executes them
(list_dir/read_file/write_file/edit_file/run_command/finish) and feeds
results back until finish or iteration cap.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.request

OMNI = os.environ.get("VIBE_OMNI", "http://127.0.0.1:4455")
OMNIROUTE = os.environ.get("VIBE_OMNIROUTE", "http://127.0.0.1:20128")
OLLAMA = os.environ.get("VIBE_OLLAMA", "http://127.0.0.1:20200")
MAX_ITERS = int(os.environ.get("VIBE_MAX_ITERS", "12"))
MAX_CMD_SECONDS = int(os.environ.get("VIBE_CMD_TIMEOUT", "60"))
CODER_HINTS = ("coder", "code", "devstral", "codestral", "deepseek", "qwen3",
               "starcoder", "glm", "kimi")

SYSTEM_PROMPT = """You are VIBE, an autonomous coding agent working inside the user's project directory.
You accomplish the request step by step by emitting EXACTLY ONE JSON object per turn — no prose, no markdown fences:

{"tool": "list_dir", "path": "."}
{"tool": "read_file", "path": "src/app.py"}
{"tool": "write_file", "path": "src/app.py", "content": "...full file content..."}
{"tool": "edit_file", "path": "src/app.py", "find": "exact old text", "replace": "new text"}
{"tool": "run_command", "command": "python -m pytest -q"}
{"tool": "finish", "summary": "what you built and how to run it"}

Rules:
- write_file ALWAYS writes the complete final file (never partial).
- Prefer edit_file for small targeted changes.
- run_command is for builds/tests; never destructive commands (rm -rf, format...).
- After verifying things work (run tests/build when applicable), call finish.
- If a tool result shows an error, fix it and retry."""


def http_json(url, payload=None, timeout=180):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0 VIBE/1.0"},
                                 method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def extract_reply(raw_bytes):
    raw = raw_bytes.decode("utf-8", "replace")
    try:
        body = json.loads(raw)
        txt = (body.get("choices") or [{}])[0].get("message", {}).get("content")
        if txt:
            return txt
    except Exception:
        pass
    text = ""
    if "data:" in raw:
        for line in raw.splitlines():
            if line.startswith("data:") and "[DONE]" not in line:
                try:
                    c = json.loads(line[5:])
                    ch = (c.get("choices") or [{}])[0]
                    text += ((ch.get("delta") or {}).get("content")
                             or (ch.get("message") or {}).get("content") or "")
                except Exception:
                    pass
            if text:
                break
    return text or raw[:200]


def pick_model():
    """Coder-first model from OMNI ranking; then OmniRoute; then Ollama."""
    try:
        with urllib.request.urlopen(OMNI + "/api/free", timeout=15) as r:
            free = json.loads(r.read()).get("free", [])
        text_ok = [m for m in free
                   if "text" in [x.lower() for x in (m.get("modalities") or ["text"])]]
        coders = [m for m in text_ok
                  if any(h in m["model_id"].lower() for h in CODER_HINTS)]
        pool = coders + text_ok
        seen = set()
        ordered = []
        # round-robin across providers so one dead provider doesn't eat tries
        by_prov = {}
        for m in pool:
            by_prov.setdefault(m["provider"], []).append(m)
        provs = list(by_prov)
        i = 0
        while len(ordered) < 24 and any(by_prov.values()):
            p = provs[i % len(provs)]
            lst = by_prov.get(p) or []
            if lst:
                ordered.append(lst.pop(0)["id"])
            i += 1
        return [("omni", mid) for mid in ordered]
    except Exception:
        pass
    try:
        with urllib.request.urlopen(OMNIROUTE + "/v1/models", timeout=10) as r:
            ids = [m["id"] for m in json.loads(r.read()).get("data", [])]
        coders = [i for i in ids if any(h in i.lower() for h in CODER_HINTS)]
        return [("omniroute", i) for i in (coders[:8] + ids[:8])]
    except Exception:
        pass
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            tags = json.loads(r.read()).get("models", [])
        return [("ollama", t["name"]) for t in tags]
    except Exception:
        return []


def ask_model(backends, messages):
    """Try backends in order; return reply text or raise after exhausting."""
    errs = []
    for kind, model in backends:
        url, payload = None, None
        if kind == "omni":
            payload = {"model": model.split("/", 1)[1] if model.count("/") >= 1 and model.split("/")[0] == "omniroute" else model,
                       "messages": messages, "max_tokens": 3000}
            url = OMNI + "/v1/chat/completions"
            payload["model"] = model
        elif kind == "omniroute":
            url = OMNIROUTE + "/v1/chat/completions"
            payload = {"model": model, "messages": messages, "max_tokens": 3000}
        elif kind == "ollama":
            url = OLLAMA + "/v1/chat/completions"
            payload = {"model": model, "messages": messages, "max_tokens": 4000}
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json",
                                                  "User-Agent": "Mozilla/5.0 VIBE/1.0"},
                                         method="POST")
            with urllib.request.urlopen(req, timeout=240) as r:
                reply = extract_reply(r.read())
            if reply and len(reply.strip()) > 2:
                print(f"  [{kind}:{model[:40]}]")
                return reply
            errs.append(f"{model}: empty")
        except Exception as e:
            errs.append(f"{model}: {str(e)[:60]}")
    raise RuntimeError("all model backends failed:\n  " + "\n  ".join(errs[:6]))


def parse_tool_call(reply):
    """Extract the single JSON tool object from a possibly chatty reply."""
    reply = reply.strip()
    if reply.startswith("```"):
        reply = re.sub(r"^```[a-zA-Z0-9_+-]*\n?", "", reply)
        reply = re.sub(r"\n?```\s*$", "", reply)
    try:
        obj = json.loads(reply)
        if isinstance(obj, dict) and obj.get("tool"):
            return obj
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", reply)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict) and obj.get("tool"):
                return obj
        except Exception:
            pass
    return None


# ---- tools -----------------------------------------------------------------
def tool_list_dir(root, args):
    path = os.path.normpath(os.path.join(root, args.get("path", ".")))
    if not path.startswith(root):
        return {"error": "path escapes project"}
    entries = []
    for dirpath, dirnames, filenames in os.walk(path):
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > 2:
            dirnames[:] = []
            continue
        for f in filenames[:50]:
            fp = os.path.join(dirpath, f)
            entries.append(f"{os.path.relpath(fp, root)} ({os.path.getsize(fp)}B)")
        if len(entries) > 150:
            break
    return {"entries": entries[:150], "count": len(entries)}


def _safe_path(root, p):
    path = os.path.normpath(os.path.join(root, p or ""))
    if not path.startswith(root):
        raise ValueError("path escapes project")
    return path


def tool_read_file(root, args):
    path = _safe_path(root, args.get("path"))
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    truncated = len(content) > 16000
    return {"path": args.get("path"),
            "content": content[:16000],
            "note": "TRUNCATED" if truncated else "full",
            "size": len(content)}


def tool_write_file(root, args):
    path = _safe_path(root, args.get("path"))
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(args.get("content", ""))
    return {"ok": True, "path": args.get("path"), "bytes": len(args.get("content", ""))}


def tool_edit_file(root, args):
    path = _safe_path(root, args.get("path"))
    src = open(path, encoding="utf-8", errors="replace").read()
    find, rep = args.get("find", ""), args.get("replace", "")
    if find not in src:
        return {"error": "find-text not present in file"}
    if src.count(find) > 1:
        return {"error": f"find-text matches {src.count(find)} times; add more context"}
    open(path, "w", encoding="utf-8", newline="").write(src.replace(find, rep, 1))
    return {"ok": True, "path": args.get("path")}


DANGEROUS = ("rm -rf", "rmdir /s", "del /f", "format ", "shutdown", "mkfs",
             "> /dev/", "reg delete", ":(){ fork")


def tool_run_command(root, args):
    cmd = args.get("command", "").strip()
    low = cmd.lower()
    if any(d in low for d in DANGEROUS):
        return {"error": "blocked potentially destructive command"}
    try:
        r = subprocess.run(cmd, cwd=root, shell=True, capture_output=True,
                           text=True, timeout=MAX_CMD_SECONDS,
                           encoding="utf-8", errors="replace")
        out = ((r.stdout or "") + (("\n[STDERR] " + r.stderr) if r.stderr else ""))[-4000:]
        return {"exit_code": r.returncode, "output": out or "(no output)"}
    except subprocess.TimeoutExpired:
        return {"error": f"timeout after {MAX_CMD_SECONDS}s"}
    except Exception as e:
        return {"error": str(e)[:200]}


TOOLS = {"list_dir": tool_list_dir, "read_file": tool_read_file,
         "write_file": tool_write_file, "edit_file": tool_edit_file,
         "run_command": tool_run_command}


def run_vibe(task, project_dir, forced_model=None):
    root = os.path.abspath(project_dir)
    os.makedirs(root, exist_ok=True)
    backends = ([(k, forced_model)] if forced_model else []) + pick_model()
    if not backends:
        print("no available model backends"); return 1
    print(f"backends ready: {len(backends)} | project: {root}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content":
                 f"PROJECT DIR CONTENTS WILL BE SHOWN VIA TOOLS.\n\nTASK: {task}"}]

    for it in range(1, MAX_ITERS + 1):
        print(f"── iter {it}/{MAX_ITERS}")
        reply = ask_model(backends, messages)
        call = parse_tool_call(reply)
        if call is None:
            messages.append({"role": "assistant", "content": reply[:800]})
            messages.append({"role": "user", "content":
                             "That was not a valid JSON tool call. Reply with EXACTLY "
                             "one JSON object using the documented schema."})
            continue
        tool = call["tool"]
        if tool == "finish":
            print(f"\n✅ DONE: {call.get('summary', '')[:500]}")
            return 0
        fn = TOOLS.get(tool)
        if fn is None:
            result = {"error": f"unknown tool '{tool}'"}
        else:
            try:
                result = fn(root, call)
            except Exception as e:
                result = {"error": str(e)[:250]}
        brief = json.dumps(result)[:300].replace("\n", " ")
        print(f"   {tool}: {brief}")
        messages.append({"role": "assistant", "content": json.dumps(call)})
        messages.append({"role": "user", "content": "TOOL RESULT:\n" + json.dumps(result)[:6000]})
    print("\n⏹ iteration cap reached without finish")
    return 2


def main():
    args = sys.argv[1:]
    forced = None
    if "--model" in args:
        i = args.index("--model")
        forced = args[i + 1]; del args[i:i + 2]
    dflag = "--dir" in args
    project = "."
    if dflag:
        i = args.index("--dir")
        project = args[i + 1]; del args[i:i + 2]
    task = " ".join(args).strip()
    if not task:
        print('usage: python vibe.py [--dir ./proj] [--model provider/model] "task"')
        return 2
    return run_vibe(task, project, forced)


if __name__ == "__main__":
    sys.exit(main())
