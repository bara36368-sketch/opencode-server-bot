"""Shared catalog + state for the local androidllm model server.

Used by runner.py (process supervision) and cyberdeck_bot.py (/model command).
Import-safe: no side effects, no network, no deps beyond stdlib.
"""
import json
import os

RECOMMENDED = [
    {"id": "qwen15", "repo": "Qwen/Qwen2.5-1.5B-Instruct",
     "disk_gb": 1.1, "note": "best overall, great tool use"},
    {"id": "smollm2", "repo": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
     "disk_gb": 1.06, "note": "English-only"},
    {"id": "qwen3", "repo": "Qwen/Qwen3-1.7B-Instruct",
     "disk_gb": 1.28, "note": "thinking mode"},
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


def recommended_ids():
    return [m["id"] for m in RECOMMENDED]
