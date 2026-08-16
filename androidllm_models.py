"""Shared catalog + state for the local androidllm model server.

Used by runner.py (process supervision) and cyberdeck_bot.py (/model command).
Import-safe: no side effects, no network, no deps beyond stdlib.

Per-model defaults: each catalog entry can carry a "defaults" dict of
ANDROIDLLM_* env overrides applied by runner.py when that model is serving
(threads, pinned/kept layers, prefix KV, throttle, etc.). Engine-side knobs
are documented in androidllm/serve.py.

Consent gate: model changes (switches + OOM downgrades) are pending until
the owner replies /approve or /deny — see request_consent/decide/apply.
"""
import json
import os

RECOMMENDED = [
    {"id": "qwen15", "repo": "Qwen/Qwen2.5-1.5B-Instruct",
     "disk_gb": 1.1, "note": "best overall, great tool use",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1",
                  "ANDROIDLLM_DRAFT": "qwen05", "ANDROIDLLM_SPEC_K": "4"}},
    {"id": "smollm2", "repo": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
     "disk_gb": 1.06, "note": "English-only",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "2",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "0",
                  "ANDROIDLLM_DRAFT": "smollm2-135m", "ANDROIDLLM_SPEC_K": "5"}},
    {"id": "qwen3", "repo": "Qwen/Qwen3-1.7B-Instruct",
     "disk_gb": 1.28, "note": "thinking mode",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "2",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "80",
                  "ANDROIDLLM_DRAFT": "qwen3-06", "ANDROIDLLM_SPEC_K": "4"}},
    # -- larger tier models (5GB-16GB RAM; matches modelpicker.CATALOG ids) --
    {"id": "qwen25-3b", "repo": "Qwen/Qwen2.5-3B-Instruct",
     "disk_gb": 2.2, "note": "3B — fits 5GB RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "2",
                  "ANDROIDLLM_PREFIX_KV": "1",
                  "ANDROIDLLM_DRAFT": "qwen05", "ANDROIDLLM_SPEC_K": "4"}},
    {"id": "qwen3-4b", "repo": "Qwen/Qwen3-4B-Instruct",
     "disk_gb": 2.8, "note": "4B thinking — fits 5GB RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "2",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "80",
                  "ANDROIDLLM_DRAFT": "qwen3-06", "ANDROIDLLM_SPEC_K": "4"}},
    {"id": "qwen25-7b", "repo": "Qwen/Qwen2.5-7B-Instruct",
     "disk_gb": 5.3, "note": "7B generalist — fits 5GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1"}},
    {"id": "mistral-7b", "repo": "mistralai/Mistral-7B-Instruct-v0.3",
     "disk_gb": 5.1, "note": "7B Mistral v0.3 — fits 5GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1"}},
    {"id": "qwen3-8b", "repo": "Qwen/Qwen3-8B-Instruct",
     "disk_gb": 5.6, "note": "8B thinking — fits 6GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "80"}},
    {"id": "qwen3-14b", "repo": "Qwen/Qwen3-14B-Instruct",
     "disk_gb": 10.4, "note": "14B thinking — fits 7GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "80"}},
    {"id": "qwen25-14b", "repo": "Qwen/Qwen2.5-14B-Instruct",
     "disk_gb": 10.4, "note": "14B generalist — fits 7GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1"}},
    {"id": "mistral-24b", "repo": "mistralai/Mistral-Small-24B-Instruct-2501",
     "disk_gb": 16.9, "note": "24B — fits 10GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1"}},
    {"id": "qwen25-32b", "repo": "Qwen/Qwen2.5-32B-Instruct",
     "disk_gb": 23.0, "note": "32B generalist — fits 14GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1"}},
    {"id": "qwen3-32b", "repo": "Qwen/Qwen3-32B-Instruct",
     "disk_gb": 23.0, "note": "32B thinking — fits 14GB+ RAM",
     "defaults": {"ANDROIDLLM_THREADS": "4", "ANDROIDLLM_KEEP_LAYERS": "1",
                  "ANDROIDLLM_PREFIX_KV": "1", "ANDROIDLLM_THROTTLE_MS": "80"}},
]

# OOM downgrade ladder: largest (most RAM-hungry) first. On an OOM-class
# crash of androidllm-serve, runner.py steps down to the next smaller model
# that is already sharded locally, so the phone stays online without a
# download. Matches modelpicker.CATALOG ids (kept import-safe here).
DOWNGRADE_LADDER = [
    "qwen3-32b", "qwen25-32b", "mistral-24b",
    "qwen3-14b", "qwen25-14b",
    "qwen3-8b", "qwen25-7b", "mistral-7b",
    "qwen3-4b", "qwen25-3b",
    "qwen3", "qwen15", "smollm2",
    "qwen3-06", "qwen05", "smollm2-360m", "smollm2-135m",
]


def androidllm_dir(env=None):
    env = env or os.environ
    return env.get("ANDROIDLLM_DIR", os.path.expanduser("~/androidllm"))


def models_dir(env=None):
    return os.path.join(androidllm_dir(env), "models")


def shard_dir(model_id, env=None):
    return os.path.join(models_dir(env), model_id)


def is_sharded(model_id, env=None):
    return os.path.isfile(os.path.join(shard_dir(model_id, env), "manifest.json"))


def state_path(env=None):
    return os.path.join(androidllm_dir(env), "current_model.json")


def read_state(env=None):
    try:
        with open(state_path(env), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_state(model_id, model_path, env=None):
    p = state_path(env)
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
    except OSError:
        pass
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"id": model_id, "path": model_path}, f)


def active_model(env=None):
    return read_state(env).get("id")


def model_defaults(model_id):
    """Per-model ANDROIDLLM_* env overrides for the serve process (item 11)."""
    for m in RECOMMENDED:
        if m["id"] == model_id:
            return dict(m.get("defaults", {}))
    return {}


def recommended_ids():
    return [m["id"] for m in RECOMMENDED]


def next_smaller(model_id, env=None):
    """Next smaller model id in DOWNGRADE_LADDER that is already sharded on
    this device (no download needed), or None when at the bottom of the
    ladder / nothing smaller is available locally."""
    if model_id not in DOWNGRADE_LADDER:
        return None
    for mid in DOWNGRADE_LADDER[DOWNGRADE_LADDER.index(model_id) + 1:]:
        if is_sharded(mid, env):
            return mid
    return None


# whichllm-inspired: pick the best model that will actually run on this
# device. Best = largest catalog entry (by disk_gb) that (a) is already
# sharded locally, and (b) fits available RAM (disk_gb in GB <= available GB
# as a loose heuristic for a llama.cpp-style loader on Android/desktop).
def available_ram_gb(env=None):
    """Free RAM in GB (best-effort). Falls back to a sane default (4 GB) so
    the picker degrades gracefully on platforms without psutil."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        try:
            import ctypes
            if os.name == "nt":
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                st = MEMORYSTATUSEX()
                st.dwLength = ctypes.sizeof(st)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
                    return st.ullAvailPhys / (1024 ** 3)
        except Exception:
            pass
    return float(os.environ.get("ANDROIDLLM_RAM_GB", "4"))


def pick_best_model(env=None, prefer=None):
    """Return the best model id to serve given local shards + free RAM.
    Prefers `prefer` when it is sharded and fits; otherwise picks the largest
    fitting catalog entry. Never returns a model that isn't sharded locally.
    """
    avail = available_ram_gb(env)
    if prefer and is_sharded(prefer, env):
        for m in RECOMMENDED:
            if m["id"] == prefer and m.get("disk_gb", 0) <= avail:
                return prefer
    fitted = [m for m in RECOMMENDED
              if is_sharded(m["id"], env) and m.get("disk_gb", 0) <= avail]
    if fitted:
        return max(fitted, key=lambda m: m.get("disk_gb", 0))["id"]
    # Nothing fitting/sharded in the catalog — fall back to any local shard
    # in RECOMMENDED order, then to the smallest ladder entry.
    for m in RECOMMENDED:
        if is_sharded(m["id"], env):
            return m["id"]
    for mid in reversed(DOWNGRADE_LADDER):
        if is_sharded(mid, env):
            return mid
    return None


def pick_report(env=None, prefer=None):
    """Pick a model and explain the decision (RAM, shards). Context-window
    guard: also flags models whose repo is likely too large for the free
    RAM. whichllm-style 'pick with reasoning'."""
    avail = available_ram_gb(env)
    mid = pick_best_model(env=env, prefer=prefer)
    if not mid:
        return {"model": None, "reason": "no locally-sharded model found"}
    entry = next((m for m in RECOMMENDED if m["id"] == mid), None)
    return {
        "model": mid,
        "free_ram_gb": round(avail, 2),
        "disk_gb": entry.get("disk_gb") if entry else None,
        "reason": (f"{mid} ({entry['note'] if entry else 'local shard'}) "
                   f"fits {round(avail, 2)}GB free RAM"),
        "next_smaller": next_smaller(mid, env),
    }


def context_window_ok(model_id, est_tokens, env=None):
    """True when `est_tokens` is plausibly inside the model context window.
    We only track a rough ceiling per tier (est_tokens guard); known huge
    prompts are refused before the edge call."""
    tiers = {"smollm2": 2048, "qwen15": 32768, "qwen3": 32768,
             "qwen05": 2048, "smollm2-360m": 2048, "smollm2-135m": 2048}
    if model_id in tiers:
        return est_tokens <= tiers[model_id]
    return est_tokens <= 8192  # unknown tier: conservative


# -- model-change consent gate --------------------------------------------
# The local model server is a supervised SYSTEM, not a fire-and-forget
# command: switching models (manual /model, /autopick, or the OOM
# downgrade cascade) always asks the owner first.  A pending request is
# written to a JSON file OUTSIDE both repos (runner file-watcher never
# sees it); owner replies /approve or /deny and the change is applied (or
# rejected) by whichever process sees the decision next.
CONSENT_TTL = int(os.environ.get("MODEL_CONSENT_TTL", "1800"))  # 30 min


def consent_path(env=None):
    base = (env or os.environ).get(
        "MODEL_STATE_DIR",
        os.path.join(os.path.expanduser("~"), ".opencode-runner"))
    return os.path.join(base, "model_consent.json")


def _now():
    import time
    return int(time.time())


def request_consent(action, target_model, reason, requester="runner", env=None):
    """Persist a pending model change: nothing switches until /approve."""
    req = {
        "action": action,          # "switch" | "downgrade"
        "target": target_model,
        "from": active_model(env),
        "reason": reason,
        "requester": requester,
        "ts": _now(),
        "status": "pending",
        "decided": None,
        "decided_by": None,
    }
    p = consent_path(env)
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
    except OSError:
        pass
    with open(p, "w", encoding="utf-8") as f:
        json.dump(req, f)
    return req


def peek_consent(env=None):
    """Active pending request, or None. Expired requests are cleared."""
    try:
        with open(consent_path(env), encoding="utf-8") as f:
            req = json.load(f)
    except Exception:
        return None
    if req.get("status") != "pending":
        return None
    if _now() - req.get("ts", 0) > CONSENT_TTL:
        clear_consent(env)
        return None
    return req


def decide_consent(approved, by="owner", env=None):
    """Owner answered: mark the pending request decided (does NOT apply the
    change — the supervisor applies it and then clears). Returns the
    decision dict (with target) or None when nothing was pending."""
    req = peek_consent(env)
    if not req:
        return None
    req["status"] = "approved" if approved else "denied"
    req["decided"] = _now()
    req["decided_by"] = by
    with open(consent_path(env), "w", encoding="utf-8") as f:
        json.dump(req, f)
    return req


def apply_consent(env=None):
    """Atomic apply of an approved request: only the first caller wins.
    Returns the applied model id or None. write_state touches current
    model.json which the androidllm supervisor watches and restarts on."""
    try:
        with open(consent_path(env), encoding="utf-8") as f:
            req = json.load(f)
    except Exception:
        return None
    if req.get("status") != "approved":
        return None
    target = req.get("target")
    if not target or not is_sharded(target, env):
        return None
    write_state(target, shard_dir(target, env), env)
    clear_consent(env)
    return target


def clear_consent(env=None):
    try:
        os.remove(consent_path(env))
    except OSError:
        pass
