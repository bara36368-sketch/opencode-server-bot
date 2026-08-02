"""Shared catalog + state for the local androidllm model server.

Used by runner.py (process supervision) and cyberdeck_bot.py (/model command).
Import-safe: no side effects, no network, no deps beyond stdlib.

Per-model defaults: each catalog entry can carry a "defaults" dict of
ANDROIDLLM_* env overrides applied by runner.py when that model is serving
(threads, pinned/kept layers, prefix KV, throttle, etc.). Engine-side knobs
are documented in androidllm/serve.py.
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
