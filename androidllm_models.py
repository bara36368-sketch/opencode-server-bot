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
]

# OOM downgrade ladder: largest (most RAM-hungry) first. On an OOM-class
# crash of androidllm-serve, runner.py steps down to the next smaller model
# that is already sharded locally, so the phone stays online without a
# download. Matches modelpicker.CATALOG ids (kept import-safe here).
DOWNGRADE_LADDER = [
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
