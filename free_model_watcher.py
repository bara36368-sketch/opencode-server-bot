"""Free Model Watcher — detects limited-time FREE AI models across providers
and broadcasts them to Telegram users.

Motivation: stealth models like Ox Alpha appear free for ~5-7 days on
aggregator catalogs (OpenRouter / OpenCode Zen). This watcher polls those
public catalogs, diffs against persisted state, and announces:

  - NEW free model appeared        -> "FREE MODEL ALERT"
  - previously-free model expired  -> "FREE MODEL ENDED" (with window length)

Sources are public JSON catalogs, no API keys required:
  openrouter   https://openrouter.ai/api/v1/models   (pricing.prompt/completion == "0")
  opencode_zen https://opencode.ai/zen/v1/models     (pricing == 0 or "free")
  models_dev   https://models.dev/api.json           (cost.input/output == 0)

State lives in freemodels_state.json so restarts never re-announce.
"""
import json
import os
import re
import time
import urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(DIR, "freemodels_state.json")
PROVIDERS_FILE = os.path.join(DIR, "providers.json")

ADOPT_ENABLED = os.environ.get("FREE_MODEL_ADOPT", "1") != "0"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
PROBE_MAX_TOKENS = int(os.environ.get("FREE_MODEL_PROBE_MAX_TOKENS", "8"))
PROBE_TIMEOUT = float(os.environ.get("FREE_MODEL_PROBE_TIMEOUT", "25"))

CHECK_INTERVAL = int(os.environ.get("FREE_MODEL_CHECK_INTERVAL", str(4 * 3600)))
BROADCAST_ENABLED = os.environ.get("FREE_MODEL_BROADCAST", "1") != "0"
MAX_ANNOUNCE_PER_CHECK = int(os.environ.get("FREE_MODEL_MAX_ANNOUNCE", "6"))
HTTP_TIMEOUT = float(os.environ.get("FREE_MODEL_HTTP_TIMEOUT", "20"))

SOURCES = [
    ("openrouter", "https://openrouter.ai/api/v1/models"),
    ("opencode_zen", "https://opencode.ai/zen/v1/models"),
    ("models_dev", "https://models.dev/api.json"),
]
PARSERS = {}


def _http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-server-bot/3.8 freemodel-watcher"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _parse_openrouter(data):
    """OpenRouter catalog -> list of normalized free-model dicts."""
    out = []
    for m in (data or {}).get("data", []):
        pricing = m.get("pricing") or {}
        try:
            prompt = float(pricing.get("prompt") or 1)
            completion = float(pricing.get("completion") or 1)
        except (TypeError, ValueError):
            continue
        if prompt != 0.0 or completion != 0.0:
            continue
        arch = m.get("architecture") or {}
        mods = arch.get("input_modalities") or ["text"]
        out.append({
            "id": m.get("id"),
            "name": m.get("name") or m.get("id"),
            "provider": "openrouter",
            "context": int(m.get("context_length") or 0),
            "modalities": [x for x in mods if x],
            "desc": (m.get("description") or "").strip().split("\n")[0][:180],
            "url": f"https://openrouter.ai/{m.get('id', '')}",
        })
    return out


def _parse_opencode_zen(data):
    """OpenCode Zen catalog -> free models (Zen lists preview models free)."""
    out = []
    for m in (data or {}).get("data", []):
        pricing = m.get("pricing") or {}
        free = False
        if isinstance(pricing, dict):
            vals = [pricing.get(k) for k in ("input", "output", "prompt", "completion") if k in pricing]
            nums = []
            for v in vals:
                try:
                    nums.append(float(v))
                except (TypeError, ValueError):
                    pass
            free = bool(nums) and all(v == 0.0 for v in nums)
        elif isinstance(pricing, str):
            free = pricing.lower() in ("free", "0", "$0")
        if not free:
            continue
        mid = m.get("id") or ""
        out.append({
            "id": f"zen:{mid}",
            "name": m.get("name") or mid,
            "provider": "opencode_zen",
            "context": int(m.get("context_length") or m.get("limit", {}).get("context", 0) or 0),
            "modalities": _norm_modalities((m.get("architecture") or {}).get("input_modalities")),
            "desc": (m.get("description") or "").strip().split("\n")[0][:180],
            "url": "https://opencode.ai/docs/zen",
        })
    return out


def _norm_modalities(raw):
    """models.dev may give {'input': [...], 'output': [...]} or a flat list."""
    if isinstance(raw, dict):
        mods = [x for x in (raw.get("input") or []) if x]
    elif isinstance(raw, list):
        mods = [x for x in raw if x]
    else:
        mods = []
    return [m for m in mods if m != "input" and m != "output"] or ["text"]


def _parse_models_dev(data):
    """models.dev catalog: {provider: {models: {id: {...cost...}}}}"""
    out = []
    for prov, pdata in (data or {}).items():
        if not isinstance(pdata, dict):
            continue
        for mid, m in (pdata.get("models") or {}).items():
            cost = m.get("cost") or {}
            try:
                cin = float(cost.get("input") or 0)
                cout = float(cost.get("output") or 0)
            except (TypeError, ValueError):
                continue
            if not m.get("free", False) and (cin != 0.0 or cout != 0.0):
                continue
            mods = _norm_modalities(m.get("modalities"))
            if "text" not in mods:
                continue
            out.append({
                "id": f"{prov}/{mid}",
                "name": m.get("name") or mid,
                "provider": prov,
                "context": int(m.get("limit", {}).get("context", 0) or 0),
                "modalities": mods,
                "desc": "",
                "url": "",
            })
    return out


PARSERS["openrouter"] = _parse_openrouter
PARSERS["opencode_zen"] = _parse_opencode_zen
PARSERS["models_dev"] = _parse_models_dev


def fetch_free_models():
    """Poll every source; returns {source: [model dicts]} skipping failures."""
    result = {}
    for name, url in SOURCES:
        try:
            result[name] = PARSERS[name](_http_json(url))
        except Exception as e:
            result[name] = None
            log_err(f"{name} fetch failed: {e}")
    return result


def log_err(msg):
    try:
        from runner import log as _rlog
        _rlog(msg, "freemodels")
    except Exception:
        pass


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"seen": {}, "expired": {}, "last_check": 0}
    except Exception:
        return {"seen": {}, "expired": {}, "last_check": 0}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=1)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        log_err(f"state save failed: {e}")


def _fmt_ctx(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.0f}M tokens"
    if n >= 1000:
        return f"{n // 1000}K tokens"
    return f"{n or '?'} tokens"


def _rank_key(m):
    ctx = m.get("context") or 0
    bonus = 500_000 if "image" in m.get("modalities", []) else 0
    return -(ctx + bonus)


def build_new_model_message(models, adopted=None):
    """adopted: {model_id: provider_name} for models registered into providers.json."""
    adopted = adopted or {}
    lines = [
        "\U0001F381 ==============================",
        "   FREE MODEL ALERT!",
        "   ==============================",
        "",
        f"\U0001F9E0 {len(models)} new FREE model{'s' if len(models) > 1 else ''} just appeared:",
        "",
    ]
    for i, m in enumerate(sorted(models, key=_rank_key)[:MAX_ANNOUNCE_PER_CHECK], 1):
        mods = ", ".join(m.get("modalities") or ["text"])
        lines.append(f"{i}. \U0001F9E9 {m['name']} ({m['id']})")
        lines.append(f"   • Context: {_fmt_ctx(m.get('context'))}")
        lines.append(f"   • Input: {mods}")
        if m.get("desc"):
            lines.append(f"   • {m['desc']}")
        pname = adopted.get(m.get("id"))
        if pname:
            lines.append(f"   ✅ Ready to use: /provider {pname}")
        lines.append("")
    lines.append("⏳ These are usually limited-time (often 5-7 days).")
    if adopted:
        lines.append("💡 Adopted models are live in the bot — try /freemodels!")
    else:
        lines.append("💡 Try it now via /codeall <task> before it's gone!")
    return "\n".join(lines)


def build_expired_message(entries):
    lines = [
        "\u23F0 ==============================",
        "   FREE MODEL ENDED",
        "   ==============================",
        "",
    ]
    for m in entries[:MAX_ANNOUNCE_PER_CHECK]:
        first = m.get("first_seen")
        last = m.get("last_seen")
        if first and last:
            days = max(1, round((last - first) / 86400))
            window = f"Free window: ~{days} day(s)"
        else:
            window = ""
        lines.append(f"\u2022 {m.get('info', {}).get('name') or m['key']} is no longer free.")
        if window:
            lines.append(f"  {window}")
    lines.append("")
    lines.append("It may still be available paid, or gone entirely.")
    return "\n".join(lines)


def get_openrouter_key():
    key = os.environ.get("OPENROUTER_KEY", "")
    if key:
        return key
    try:
        with open(PROVIDERS_FILE, encoding="utf-8") as f:
            provs = json.load(f)
        return (provs.get("openrouter") or {}).get("key", "")
    except Exception:
        return ""


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:28] or "model"


def probe_openrouter(model_id, key):
    """Live-test a model with a tiny completion. Returns (ok, latency_ms, err)."""
    data = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": PROBE_MAX_TOKENS,
    }).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://localhost",
            "X-Title": "opencode-server-bot freemodel-watcher",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
        ms = int((time.time() - t0) * 1000)
        ok = bool(body.get("choices"))
        return ok, ms, None if ok else "empty choices"
    except Exception as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            msg = str(e)[:200]
        return False, int((time.time() - t0) * 1000), msg


def load_providers():
    try:
        with open(PROVIDERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_providers(provs):
    tmp = PROVIDERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(provs, f, indent=1)
    os.replace(tmp, PROVIDERS_FILE)


def adopt_model(info, state):
    """Register a free model into providers.json as free_<slug>.

    Returns provider name or None. Only adopts openrouter-sourced models
    (probe needs a key and the id must route on openrouter).
    """
    if not ADOPT_ENABLED or info.get("provider") != "openrouter":
        return None
    mid = info.get("id") or ""
    if not mid or "/" not in mid:
        return None
    name = "free_" + slugify(mid.split("/", 1)[1])
    key = get_openrouter_key()
    if not key:
        log_err(f"adopt skipped ({mid}): no OPENROUTER_KEY")
        return None
    ok, ms, err = probe_openrouter(mid, key)
    if not ok:
        log_err(f"probe failed for {mid} ({ms}ms): {err}")
        return None
    provs = load_providers()
    existed = name in provs
    provs[name] = {
        "url": OPENROUTER_CHAT_URL,
        "model": mid,
        "key": key,
    }
    save_providers(provs)
    state.setdefault("adopted", {})[name] = {
        "model_id": mid,
        "adopted_at": time.time(),
        "probe_ms": ms,
    }
    log_err(f"{'updated' if existed else 'adopted'} provider {name} -> {mid} (probe {ms}ms)")
    return name


def retire_provider(name, state):
    """Remove an adopted provider from providers.json when its free window ends."""
    if not name:
        return False
    provs = load_providers()
    if name not in provs:
        state.get("adopted", {}).pop(name, None)
        return False
    del provs[name]
    save_providers(provs)
    state.get("adopted", {}).pop(name, None)
    log_err(f"retired provider {name} (no longer free)")
    return True


def collect_broadcast_chats(owner_id=None):
    """All chats worth notifying: owner + bot sessions, minus opt-outs."""
    chats = set()
    if owner_id:
        try:
            chats.add(int(owner_id))
        except (TypeError, ValueError):
            pass
    try:
        with open(os.path.join(DIR, "sessions.json"), encoding="utf-8") as f:
            s = json.load(f)
        for cid in (s.get("sessions") or {}):
            try:
                chats.add(int(cid))
            except (TypeError, ValueError):
                pass
    except Exception:
        pass
    opted_out = set()
    try:
        with open(os.path.join(DIR, "version_state.json"), encoding="utf-8") as f:
            vs = json.load(f)
        for cid in vs.get("opted_out_announcements", []):
            try:
                opted_out.add(int(cid))
            except (TypeError, ValueError):
                pass
    except Exception:
        pass
    return sorted(chats - opted_out)


def send_to_chat(bot_token, chat_id, text):
    data = json.dumps({"chat_id": chat_id, "text": text, "disable_web_page_preview": True}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            ok = r.status == 200
    except Exception as e:
        log_err(f"send to {chat_id} failed: {e}")
        return False
    time.sleep(0.15)
    return ok


def broadcast(bot_token, owner_id, text):
    if not BROADCAST_ENABLED or not bot_token:
        return 0
    sent = 0
    for cid in collect_broadcast_chats(owner_id):
        if send_to_chat(bot_token, cid, text):
            sent += 1
    return sent


def check_now(bot_token=None, owner_id=None, dry=False):
    """One poll cycle. Returns dict of events for logging/testing."""
    state = load_state()
    sources = fetch_free_models()
    events = {"new": [], "expired": [], "errors": [], "sent_to": 0}

    now = time.time()
    current_keys = {}

    for src, models in sources.items():
        if models is None:
            events["errors"].append(src)
            continue
        for m in models:
            if not m.get("id"):
                continue
            key = f"{src}:{m['id']}"
            current_keys[key] = (src, m)

    # newly free
    fresh = []
    for key, (src, m) in current_keys.items():
        seen = state["seen"].get(key)
        if seen is None:
            rec = {"first_seen": now, "last_seen": now, "info": m, "announced": None}
            state["seen"][key] = rec
            fresh.append(rec)
        else:
            seen["last_seen"] = now
            seen.setdefault("info", {}).update({k: m[k] for k in m})

    # expired: announced models that vanished from every source this check
    vanished = []
    for key, rec in list(state["seen"].items()):
        if key not in current_keys and rec.get("announced"):
            grace_ok = now - rec["last_seen"] > CHECK_INTERVAL * 2
            if grace_ok:
                vanished.append((key, rec))

    for key, rec in vanished:
        state["expired"][key] = rec
        del state["seen"][key]

    state["last_check"] = now

    announce_new = [r for r in fresh if r.get("announced") is None]
    if dry:
        save_state(state)
        return events

    adopted_map = {}
    if announce_new:
        for r in announce_new:
            pname = adopt_model(r.get("info") or {}, state)
            if pname:
                adopted_map[r["info"].get("id")] = pname
        msg = build_new_model_message([r["info"] for r in announce_new], adopted_map)
        events["sent_to"] = broadcast(bot_token, owner_id, msg)
        for r in announce_new:
            r["announced"] = now
            events["new"].append(r["info"].get("id"))
        events["adopted"] = list(adopted_map.values())
        log_err(f"announced {len(announce_new)} new free model(s) to {events['sent_to']} chat(s)"
                f" (adopted: {len(adopted_map)})")

    if vanished:
        retired = []
        for k, rec in vanished:
            mid = (rec.get("info") or {}).get("id")
            src = k.split(":", 1)[0]
            pname = None
            if src == "openrouter" and mid:
                pname = "free_" + slugify(mid.split("/", 1)[1])
                if pname not in state.get("adopted", {}):
                    pname = None
            if retire_provider(pname, state):
                retired.append(pname)
        events["retired"] = retired
        exp_rows = [
            {"key": k.split(':', 1)[-1], "first_seen": r.get("first_seen"),
             "last_seen": r.get("last_seen"), "info": r.get("info", {})}
            for k, r in vanished
        ]
        msg = build_expired_message(exp_rows)
        broadcast(bot_token, owner_id, msg)
        for k, _r in vanished:
            events["expired"].append(k)

    save_state(state)
    return events


if __name__ == "__main__":
    ev = check_now(dry=True)
    print(json.dumps(ev, indent=1))
