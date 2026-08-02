"""Tests for opencode.py — provider shim wiring opencode to the phone's
androidllm endpoint. Pure functions only: no network, no opencode binary."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opencode as oc


def _tmpdir(tmp_path, sub):
    d = tmp_path / sub
    d.mkdir(parents=True, exist_ok=True)
    return str(d)


def test_endpoint_default_and_override():
    assert oc.endpoint({}) == "http://127.0.0.1:8000"
    assert oc.endpoint({"ANDROIDLLM_URL": "http://192.168.1.50:8080/"}) == "http://192.168.1.50:8080"


def test_api_key_from_file(tmp_path, monkeypatch):
    keydir = tmp_path / "androidllm"
    keydir.mkdir()
    (keydir / "api_key").write_text("sk-test-key\n", encoding="utf-8")
    monkeypatch.setattr(oc, "KEY_FILE", str(keydir / "api_key"))
    assert oc.api_key({}) == "sk-test-key"
    assert oc.api_key({"ANDROIDLLM_KEY": "sk-env"}) == "sk-env"
    monkeypatch.setattr(oc, "KEY_FILE", str(tmp_path / "nope" / "api_key"))
    assert oc.api_key({}) == "skip-auth"


def test_pick_model_prefers_active(tmp_path, monkeypatch):
    env = {"ANDROIDLLM_DIR": str(tmp_path)}
    assert oc.pick_model(env) == "qwen15"
    monkeypatch.setattr(oc, "active_model", lambda env=None: "qwen3-8b")
    assert oc.pick_model(env) == "qwen3-8b"


def test_pick_model_respects_ram_tier(monkeypatch):
    monkeypatch.setattr(oc, "active_model", lambda env=None: None)
    # largest model that fits budget = 70% of RAM
    for ram, expect in [(4, "qwen3-4b"), (5, "qwen3-4b"), (8, "qwen3-8b"), (16, "qwen25-14b"), (64, "qwen3-32b")]:
        m = oc.pick_model({}, {"ram_gb": ram})
        assert m == expect, (ram, m)


def test_provider_patch_shape():
    patch = oc.provider_patch("http://127.0.0.1:8000", "sk-x", "qwen15")
    assert patch["npm"] == "@ai-sdk/openai-compatible"
    assert patch["options"]["baseURL"] == "http://127.0.0.1:8000/v1"
    assert patch["options"]["apiKey"] == "sk-x"
    assert "qwen15" in patch["models"]
    assert patch["models"]["qwen15"]["limit"]["context"] > 0


def test_setup_config_merges_not_clobbers(tmp_path, monkeypatch):
    cfg = tmp_path / "opencode.json"
    auth = tmp_path / "auth.json"
    cfg.write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "provider": {"openai": {"name": "keep me"}},
    }), encoding="utf-8")
    auth.write_text(json.dumps({"openai": {"type": "api", "key": "sk-old"}}), encoding="utf-8")
    monkeypatch.setattr(oc, "OPENCODE_CONFIG", str(cfg))
    monkeypatch.setattr(oc, "OPENCODE_AUTH", str(auth))

    c, a = oc.setup_config("http://127.0.0.1:8000", "sk-new", "qwen15")

    merged_cfg = json.load(open(c, encoding="utf-8"))
    assert "openai" in merged_cfg["provider"]
    assert merged_cfg["provider"]["openai"]["name"] == "keep me"
    assert "androidllm" in merged_cfg["provider"]
    merged_auth = json.load(open(a, encoding="utf-8"))
    assert merged_auth["androidllm"] == {"type": "api", "key": "sk-new"}
    assert merged_auth["openai"]["key"] == "sk-old"


def test_setup_config_twice_is_idempotent(tmp_path, monkeypatch):
    cfg = tmp_path / "opencode.json"
    auth = tmp_path / "auth.json"
    monkeypatch.setattr(oc, "OPENCODE_CONFIG", str(cfg))
    monkeypatch.setattr(oc, "OPENCODE_AUTH", str(auth))
    oc.setup_config("http://127.0.0.1:8000", "sk-a", "qwen15")
    oc.setup_config("http://127.0.0.1:9000", "sk-b", "qwen3")
    data = json.load(open(cfg, encoding="utf-8"))
    prov = data["provider"]["androidllm"]
    assert prov["options"]["baseURL"] == "http://127.0.0.1:9000/v1"
    assert prov["models"] == {"qwen3": prov["models"]["qwen3"]}
