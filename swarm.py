"""Agent Swarm — dynamic, health-aware multi-agent coordination.

Standalone, zero-dependency module. It is bot-agnostic: the host bot injects a
`call_fn(msgs, provider) -> str` and a provider chain, and the swarm does the rest.

Architecture (two levels, no recursion):
  planner  ->  decomposes the task into subtasks (1 LLM call)
  workers  ->  N specialized agents run the subtasks in parallel (health-aware pool)
  synthesis ->  one aggregator combines all worker outputs (1 LLM call)

The worker pool is dynamic: providers that error / 429 go on a short cooldown,
so the swarm degrades gracefully instead of storming a failing provider. The
maximum concurrency is capped by SWARM_MAX_WORKERS (default 8), but a backlog of
any size can be queued through it.

Run standalone for a demo:  python swarm.py "your task here"
"""

import asyncio
import os
import random
import time
from collections import Counter

__all__ = ["Swarm", "default_is_error"]

PLANNER_SYSTEM = (
    "You are a swarm orchestrator. Decompose the given task into 3-6 independent, "
    "non-overlapping subtasks that can be solved in parallel by specialist agents. "
    "Rules:\n"
    "- Each subtask must be self-contained and actionable on its own.\n"
    "- Cover the main facets: research, design, verification, edge cases, final assembly.\n"
    "- Output ONLY the subtasks, one per line, each starting with '- '.\n"
    "- No preamble, no numbering like 1), no markdown headers."
)

SWARM_WORKER_SYSTEM = (
    "You are a specialist agent inside a parallel agent swarm. Your job is to solve "
    "ONLY your assigned subtask, completely and precisely, as if it is your sole "
    "responsibility. Do not try to solve other subtasks. Deliver a self-contained "
    "result that another agent can merge into the final answer."
)

SYNTHESIS_SYSTEM = (
    "You are the swarm aggregator. You are given an original task plus the outputs "
    "of N parallel specialist agents. Merge them into ONE coherent, complete, final "
    "answer. Rules:\n"
    "- Reconcile contradictions; prefer verified specifics over vague claims.\n"
    "- Do not invent results the workers did not produce.\n"
    "- Structure the final answer with clear sections.\n"
    "- If some worker outputs are missing/failed, say so briefly and fill gaps best you can."
)

ROUND_ROLES = [
    "You are a rigorous technical reviewer. Attack the task for correctness, missing edge cases, and weak assumptions.",
    "You are a pragmatic implementer. Produce concrete, actionable, buildable output.",
    "You are a creative designer. Suggest bold, alternative, or elegant approaches.",
    "You are a security/compliance auditor. Flag risks, failure modes, and safeguards.",
    "You are a cost/simplicity optimizer. Prefer the cheapest, simplest, most robust solution.",
]

_COOLDOWN_SECONDS = 30.0
_MAX_WORKER_CHARS = 4000


def default_is_error(reply):
    """Heuristic: is this reply actually a provider/error string, not real content?"""
    if not isinstance(reply, str):
        return True
    low = reply.lower()
    head = low[:80]
    if head.startswith(("gemini error", "ai call failed", "no ai provider", "no user message")):
        return True
    if low.startswith("all coding providers failed"):
        return True
    if "error:" in head:
        return True
    if "insufficient balance" in low:
        return True
    if "payment required" in low:
        return True
    return False


class Swarm:
    def __init__(self, call_fn, chain, is_error=default_is_error, max_workers=None):
        self.call_fn = call_fn
        self.chain = list(chain)
        self.is_error = is_error
        self.max_workers = max_workers or int(os.environ.get("SWARM_MAX_WORKERS", "8"))
        self.max_workers = max(1, min(self.max_workers, 64))
        self._health = {p: {"ok": 0, "fail": 0, "cooldown_until": 0.0, "latency": []} for p in self.chain}
        self._rr = 0
        self.total_spawned = 0
        self.total_succeeded = 0
        self.total_failed = 0
        self.runs = []

    # ------------------------------------------------------------------ health
    def _record(self, provider, ok, latency=None):
        h = self._health.setdefault(
            provider, {"ok": 0, "fail": 0, "cooldown_until": 0.0, "latency": []})
        if ok:
            h["ok"] += 1
            h["cooldown_until"] = 0.0
        else:
            h["fail"] += 1
            h["cooldown_until"] = time.time() + _COOLDOWN_SECONDS
        if latency is not None:
            h["latency"].append(latency)
            h["latency"] = h["latency"][-50:]

    def _next_provider(self):
        """Next healthy provider, scanning the chain cyclically from the cursor."""
        n = len(self.chain)
        if n == 0:
            return None
        now = time.time()
        for _ in range(n):
            self._rr = (self._rr + 1) % n
            p = self.chain[self._rr]
            if self._health[p]["cooldown_until"] <= now:
                return p
        return self.chain[(self._rr + 1) % n]

    # ------------------------------------------------------------------ core
    async def _call(self, msgs, provider):
        started = time.time()
        try:
            reply = await self.call_fn(msgs, provider)
        except Exception as e:
            self._record(provider, False)
            return f"worker exception: {e}", provider, None
        latency = time.time() - started
        if self.is_error(reply):
            self._record(provider, False, latency)
        else:
            self._record(provider, True, latency)
        return reply, provider, latency

    async def _call_any(self, msgs, attempts=6):
        """Try providers until one returns real content; record each failure."""
        last = None
        used = None
        for _ in range(max(1, attempts)):
            provider = self._next_provider()
            if provider is None:
                return "No providers.", None
            reply, used, _ = await self._call(msgs, provider)
            if not self.is_error(reply):
                return reply, used
            last = reply
        return last, used

    async def _planner(self, task):
        msgs = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": task},
        ]
        reply, provider = await self._call_any(msgs)
        if self.is_error(reply):
            return [task], provider
        subs = []
        for line in reply.splitlines():
            line = line.strip()
            if line.startswith("- "):
                subs.append(line[2:].strip())
            elif line.startswith("• ") or line.startswith("* "):
                subs.append(line[2:].strip())
        subs = [s for s in subs if s]
        if not subs:
            return [task], provider
        return subs[:8], provider

    async def _worker(self, sem, idx, subtask):
        async with sem:
            msgs = [
                {"role": "system", "content": SWARM_WORKER_SYSTEM},
                {"role": "user", "content": subtask},
            ]
            self.total_spawned += 1
            reply, used_provider, latency = None, None, None
            for _attempt in range(2):
                provider = self._next_provider()
                if provider is None:
                    break
                reply, used_provider, latency = await self._call(msgs, provider)
                if not self.is_error(reply):
                    break
            ok = not self.is_error(reply)
            if ok:
                self.total_succeeded += 1
            else:
                self.total_failed += 1
            return {
                "index": idx,
                "subtask": subtask,
                "provider": used_provider,
                "ok": ok,
                "latency": latency,
                "chars": len(reply),
                "text": reply,
                "preview": reply[:200].replace("\n", " "),
            }

    async def _synthesize(self, task, subtasks, results):
        blocks = []
        for r in results:
            head = r["text"][:_MAX_WORKER_CHARS]
            blocks.append(f"--- Worker {r['index']} [{r['provider']}]\n{head}")
        body = (
            f"Original task:\n{task}\n\n"
            f"Subtask plan:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(subtasks)) + "\n\n"
            f"Worker outputs:\n" + "\n\n".join(blocks)
        )
        msgs = [
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": body},
        ]
        reply, used_provider = await self._call_any(msgs)
        return reply, used_provider

    # ------------------------------------------------------------------ API
    async def run(self, task, role=None):
        """Divide & conquer: plan -> parallel workers -> synthesis."""
        started = time.time()
        subtasks, plan_provider = await self._planner(task)
        sem = asyncio.Semaphore(self.max_workers)
        results = await asyncio.gather(
            *[self._worker(sem, i + 1, s) for i, s in enumerate(subtasks)],
            return_exceptions=True)
        clean = []
        for r in results:
            if isinstance(r, BaseException):
                clean.append({
                    "index": len(clean) + 1, "subtask": "?",
                    "provider": None, "ok": False, "latency": None,
                    "chars": 0, "text": f"exception: {r}", "preview": str(r)[:200]})
            else:
                clean.append(r)
        synthesis, syn_provider = await self._synthesize(task, subtasks, clean)
        stats = {
            "planned": len(subtasks),
            "spawned": len(clean),
            "succeeded": sum(1 for r in clean if r["ok"]),
            "failed": sum(1 for r in clean if not r["ok"]),
            "elapsed": round(time.time() - started, 2),
            "max_workers": self.max_workers,
            "plan_provider": plan_provider,
            "synthesis_provider": syn_provider,
            "providers_used": dict(Counter(r["provider"] for r in clean if r["provider"])),
        }
        run = {
            "mode": "divide",
            "task": task,
            "role": role,
            "subtasks": subtasks,
            "results": clean,
            "synthesis": synthesis,
            "stats": stats,
        }
        self.runs.append(run)
        self.runs = self.runs[-20:]
        return run

    async def run_round(self, task, roles=None):
        """Round table: several role-perspective agents attack the SAME task, then merge."""
        started = time.time()
        roles = roles or ROUND_ROLES
        sem = asyncio.Semaphore(self.max_workers)

        async def _one(i, role):
            async with sem:
                msgs = [
                    {"role": "system", "content": role},
                    {"role": "user", "content": task},
                ]
                self.total_spawned += 1
                reply, used_provider, latency = None, None, None
                for _attempt in range(2):
                    provider = self._next_provider()
                    if provider is None:
                        break
                    reply, used_provider, latency = await self._call(msgs, provider)
                    if not self.is_error(reply):
                        break
                ok = not self.is_error(reply)
                if ok:
                    self.total_succeeded += 1
                else:
                    self.total_failed += 1
                return {"index": i + 1, "role": role, "provider": used_provider,
                        "ok": ok, "latency": latency, "chars": len(reply),
                        "text": reply, "preview": reply[:200].replace("\n", " ")}

        results = await asyncio.gather(*[_one(i, r) for i, r in enumerate(roles[:8])],
                                       return_exceptions=True)
        clean = [r if not isinstance(r, BaseException) else
                 {"index": i + 1, "role": roles[i], "provider": None, "ok": False,
                  "latency": None, "chars": 0, "text": f"exception: {r}", "preview": str(r)[:200]}
                 for i, r in enumerate(results)]
        subtasks = [f"{r['role']}" for r in clean]
        synthesis, syn_provider = await self._synthesize(task, subtasks, clean)
        stats = {
            "planned": len(clean),
            "spawned": len(clean),
            "succeeded": sum(1 for r in clean if r["ok"]),
            "failed": sum(1 for r in clean if not r["ok"]),
            "elapsed": round(time.time() - started, 2),
            "max_workers": self.max_workers,
            "synthesis_provider": syn_provider,
            "providers_used": dict(Counter(r["provider"] for r in clean if r["provider"])),
        }
        run = {"mode": "round", "task": task, "role": None, "subtasks": subtasks,
               "results": clean, "synthesis": synthesis, "stats": stats}
        self.runs.append(run)
        self.runs = self.runs[-20:]
        return run

    def status(self):
        now = time.time()
        lines = []
        for p, h in self._health.items():
            cool = "COOLDOWN" if h["cooldown_until"] > now else "ok"
            lat = f"{sum(h['latency'])/len(h['latency']):.1f}s" if h["latency"] else "-"
            lines.append(f"  {p}: ok={h['ok']} fail={h['fail']} {cool} avg={lat}")
        return {
            "providers": len(self.chain),
            "max_workers": self.max_workers,
            "total_spawned": self.total_spawned,
            "total_succeeded": self.total_succeeded,
            "total_failed": self.total_failed,
            "health": lines,
            "last_run": self.runs[-1]["stats"] if self.runs else None,
        }


def _fmt_run(run):
    s = run["stats"]
    lines = [
        f"<b>Swarm · {run['mode']}</b> — {s['elapsed']}s",
        f"Planned {s['planned']} subtasks · spawned {s['spawned']} · "
        f"succeeded {s['succeeded']} · failed {s['failed']}",
        f"Providers: {', '.join(f'{k}={v}' for k, v in (s.get('providers_used') or {}).items())}",
        "",
    ]
    for r in run["results"]:
        mark = "✅" if r["ok"] else "❌"
        lines.append(f"{mark} #{r['index']} [{r['provider']}] {r['subtask'][:80]}")
    syn = run.get("synthesis") or ""
    lines.append("")
    lines.append("<b>Merged answer:</b>")
    lines.append(syn[:4000])
    return "\n".join(lines)


# ------------------------------------------------------------------ demo CLI
async def _demo(task):
    import json

    providers = {}
    for name in ("groq", "gemini", "openrouter", "kimi", "cerebras", "deepseek"):
        env_key = name.upper().replace("-", "_") + "_KEY"
        if os.environ.get(env_key):
            providers[name] = env_key

    if not providers:
        print("No provider keys in env (GROQ_KEY/GEMINI_KEY/...) for the demo.")
        return

    async def call_fn(msgs, provider):
        import urllib.request
        key = os.environ[providers[provider]]
        url = {
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "kimi": "https://openrouter.ai/api/v1/chat/completions",
            "cerebras": "https://api.cerebras.ai/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
        }[provider]
        model = {
            "groq": "llama-3.3-70b-versatile",
            "gemini": "gemini-3.5-flash",
            "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
            "kimi": "moonshotai/kimi-k3",
            "cerebras": "llama-3.3-70b",
            "deepseek": "deepseek-chat",
        }[provider]
        if provider == "gemini":
            parts = [{"role": "model" if m["role"] == "assistant" else "user",
                      "parts": [{"text": m["content"]}]} for m in msgs]
            req = urllib.request.Request(
                url + f"?key={key}", data=json.dumps({"contents": parts}).encode(),
                headers={"Content-Type": "application/json"})
        else:
            body = {"model": model, "messages": msgs, "max_tokens": 4096}
            req = urllib.request.Request(
                url, data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            if provider == "gemini":
                cands = data.get("candidates", [])
                return cands[0]["content"]["parts"][0]["text"] if cands else str(data)[:500]
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            return f"{provider} error: {e}"

    swarm = Swarm(call_fn, list(providers), max_workers=4)
    run = await swarm.run(task)
    print(_fmt_run(run).replace("<b>", "").replace("</b>", ""))
    print("\n--- STATUS ---")
    print(json.dumps(swarm.status(), indent=2))


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) or "Explain how to build a small cyberdeck on a Raspberry Pi 5"
    asyncio.run(_demo(task))
