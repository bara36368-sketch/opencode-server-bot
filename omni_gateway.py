"""OMNI Gateway — one keyring, one endpoint, every free model ranked.

OmniRoute-inspired local gateway:
  1. Paste ANY provider API key into the dashboard (auto-detects provider
     from key prefix, validates live, stores locally).
  2. Scanner walks each validated provider's model catalog and detects FREE
     models ($0 in/$0 out).
  3. Free models are RANKED (context size + modalities + provider speed tier).
  4. One OpenAI-compatible endpoint (/v1/chat/completions) proxies to whichever
     ranked model you pick — any app just points at this base URL.

Endpoints:
  GET  /                     dashboard UI
  GET  /api/status           keys + last scan summary
  POST /api/keys             {key: "..."} -> auto-detect + validate + save
  DEL  /api/keys/<name>      remove stored key
  POST /api/scan             re-validate all keys + refresh catalogs
  GET  /api/free             ranked free models JSON
  POST /v1/chat/completions  unified endpoint {"model": "<provider>/<id>", ...}

Port: OMNI_PORT (default 4455). Storage: omni_keys.json + omni_catalog.json
(both gitignored — never commit real keys).
"""
import json
import os
import re
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(DIR, "omni_keys.json")
CATALOG_FILE = os.path.join(DIR, "omni_catalog.json")
USAGE_FILE = os.path.join(DIR, "omni_usage.json")
FREE_STATE_FILE = os.path.join(DIR, "freemodels_state.json")
PORT = int(os.environ.get("OMNI_PORT", "4455"))
HEALTH_INTERVAL_H = float(os.environ.get("OMNI_HEALTH_INTERVAL_H", "6"))
STEALTH_WINDOW_DAYS = float(os.environ.get("OMNI_STEALTH_WINDOW_DAYS", "7"))
BLENDED_RETAIL_PER_M = float(os.environ.get("OMNI_RETAIL_PER_M", "2.50"))  # est. $/M tokens

# provider registry: key-prefix detect -> endpoints. auth: bearer | query | header
PROVIDERS = {
    "openrouter": {
        "prefixes": ["sk-or-"],
        "models_url": "https://openrouter.ai/api/v1/models",
        "chat_url": "https://openrouter.ai/api/v1/chat/completions",
        "auth": "bearer",
        "speed": 3,
    },
    "groq": {
        "prefixes": ["gsk_"],
        "models_url": "https://api.groq.com/openai/v1/models",
        "chat_url": "https://api.groq.com/openai/v1/chat/completions",
        "auth": "bearer",
        "speed": 5,
    },
    "gemini": {
        "prefixes": ["AIza"],
        "models_url": "https://generativelanguage.googleapis.com/v1beta/openai/models",
        "chat_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "auth": "bearer",
        "speed": 4,
    },
    "nvidia": {
        "prefixes": ["nvapi-"],
        "models_url": "https://integrate.api.nvidia.com/v1/models",
        "chat_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "auth": "bearer",
        "speed": 4,
    },
    "cerebras": {
        "prefixes": ["csk-"],
        "models_url": "https://api.cerebras.ai/v1/models",
        "chat_url": "https://api.cerebras.ai/v1/chat/completions",
        "auth": "bearer",
        "speed": 5,
    },
    "mistral": {
        "prefixes": [],
        "models_url": "https://api.mistral.ai/v1/models",
        "chat_url": "https://api.mistral.ai/v1/chat/completions",
        "auth": "bearer",
        "speed": 4,
    },
    "deepseek": {
        "prefixes": ["sk-"],
        "models_url": "https://api.deepseek.com/v1/models",
        "chat_url": "https://api.deepseek.com/v1/chat/completions",
        "auth": "bearer",
        "speed": 4,
    },
    "together": {
        "prefixes": ["tgp_v1_"],
        "models_url": "https://api.together.xyz/v1/models",
        "chat_url": "https://api.together.xyz/v1/chat/completions",
        "auth": "bearer",
        "speed": 3,
    },
    "huggingface": {
        "prefixes": ["hf_"],
        "models_url": "https://router.huggingface.co/v1/models",
        "chat_url": "https://router.huggingface.co/v1/chat/completions",
        "auth": "bearer",
        "speed": 2,
    },
    "siliconflow": {
        "prefixes": ["sk-siliconflow"],
        "models_url": "https://api.siliconflow.cn/v1/models",
        "chat_url": "https://api.siliconflow.cn/v1/chat/completions",
        "auth": "bearer",
        "speed": 3,
    },
    "sambanova": {
        "prefixes": [],
        "models_url": "https://api.sambanova.ai/v1/models",
        "chat_url": "https://api.sambanova.ai/v1/chat/completions",
        "auth": "bearer",
        "speed": 5,
    },
    "llm7": {
        "prefixes": [],          # works keyless too
        "models_url": "https://api.llm7.io/v1/models",
        "chat_url": "https://api.llm7.io/v1/chat/completions",
        "auth": "none-ok",
        "speed": 3,
    },
    "pollinations": {
        "prefixes": [],
        "models_url": "https://text.pollinations.ai/models",
        "chat_url": "https://text.pollinations.ai/openai/chat/completions",  # POST via /openai
        "auth": "none-ok",
        "speed": 2,
    },
}
_PREFIX_TO_PROVIDER = {}
for _pname, _pcfg in PROVIDERS.items():
    for _pre in _pcfg["prefixes"]:
        _PREFIX_TO_PROVIDER[_pre] = _pname
_CHATHOST_TO_PROVIDER = {cfg["chat_url"].split("//")[1].split("/")[0]: pname
                         for pname, cfg in PROVIDERS.items()}


def _provider_by_chat_url(chat_url):
    try:
        return _CHATHOST_TO_PROVIDER.get(chat_url.split("//")[1].split("/")[0], "unknown")
    except Exception:
        return "unknown"


def detect_provider(key):
    k = (key or "").strip()
    for pre, pname in _PREFIX_TO_PROVIDER.items():
        if k.startswith(pre):
            return pname
    return None


def _http_json(url, key=None, auth="bearer", timeout=20):
    headers = {"User-Agent": "omni-gateway/1.0"}
    if key and auth == "bearer":
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def mask_key(key):
    if not key or len(key) < 10:
        return "***"
    return key[:6] + "..." + key[-4:]


# ---- storage ---------------------------------------------------------------
def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


# ---- validation + catalog scanning -----------------------------------------
def validate_key(provider, key):
    """Live-check a key against its provider. Returns (ok, detail, models|[])."""
    cfg = PROVIDERS.get(provider)
    if not cfg:
        return False, "unknown provider", []
    try:
        if provider == "gemini":
            data = _http_json(cfg["models_url"] + "?key=" + key)
        else:
            data = _http_json(cfg["models_url"], key=key, auth=cfg["auth"])
        if isinstance(data, list):          # pollinations returns a bare array
            raw = data
        else:
            raw = data.get("data", data.get("models", []))
        ids = []
        for m in raw:
            if isinstance(m, dict):
                mid = m.get("id") or m.get("name") or ""
                ids.append((mid, m))
            elif isinstance(m, str):
                ids.append((m, {}))
        return True, f"{len(ids)} models", ids
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}", []
    except Exception as e:
        return False, str(e)[:80], []


def extract_free_models(provider, entries):
    """From a provider's catalog entries return [(model_id, info)] that are free."""
    cfg = PROVIDERS[provider]
    out = []
    for mid, m in entries:
        pricing = m.get("pricing") or {}
        cost = m.get("cost") or {}
        free = False
        ctx = int(m.get("context_length") or (m.get("limit") or {}).get("context", 0) or 0)
        mods = (m.get("architecture") or {}).get("input_modalities") \
            or m.get("modalities") or ["text"]
        if isinstance(mods, dict):
            mods = mods.get("input") or ["text"]
        try:
            pp = float(pricing.get("prompt") or cost.get("input") or -1)
            pc = float(pricing.get("completion") or cost.get("output") or -1)
            free = pp == 0 and pc == 0
        except (TypeError, ValueError):
            free = False
        if provider in ("llm7", "pollinations"):
            free = True              # these services are free-tier by design
        if ":free" in mid or m.get("free") or m.get("is_free"):
            free = True
        if free:
            out.append({
                "id": f"{provider}/{mid}",
                "model_id": mid,
                "provider": provider,
                "context": ctx,
                "modalities": [x for x in mods if x] or ["text"],
                "desc": (m.get("description") or "")[:140],
            })
    return out


def rank_score(m):
    ctx = m.get("context") or 0
    speed = PROVIDERS.get(m["provider"], {}).get("speed", 2) * 50_000
    mods = m.get("modalities") or []
    mod_bonus = 200_000 * len([x for x in mods if x != "text"])
    return ctx + speed + mod_bonus


def scan_all():
    """Validate every stored key, refresh catalogs, persist ranked free list."""
    keys = load_json(KEYS_FILE, {})
    all_free = []
    results = {}
    # keyless providers always scanned
    for pname, cfg in PROVIDERS.items():
        if cfg["auth"] == "none-ok" and pname not in keys:
            ok, detail, entries = validate_key(pname, None)
            if ok:
                results[pname] = {"ok": True, "detail": detail, "masked": "(keyless)"}
                all_free.extend(extract_free_models(pname, entries))
            continue
    for pname, rec in keys.items():
        key = rec.get("key", "")
        ok, detail, entries = validate_key(pname, key)
        results[pname] = {"ok": ok, "detail": detail,
                          "masked": mask_key(key)}
        record_key_health(pname, ok, detail)
        if ok:
            all_free.extend(extract_free_models(pname, entries))
    all_free.sort(key=rank_score, reverse=True)
    catalog = {"ts": time.time(), "free": all_free, "results": results}
    save_json(CATALOG_FILE, catalog)
    return catalog


# ---- #1 key health monitor -------------------------------------------------
def record_key_health(provider, ok, detail=""):
    """Merge a validation result into the stored key's health record."""
    keys = load_json(KEYS_FILE, {})
    rec = keys.get(provider)
    if not rec:
        return
    h = rec.setdefault("health", {"status": "unknown", "fails": 0,
                                  "last_ok": 0, "last_fail": 0})
    now = time.time()
    prev = h.get("status")
    h["last_checked"] = now
    h["detail"] = detail[:80]
    if ok:
        h["status"] = "healthy"
        h["fails"] = 0
        h["last_ok"] = now
    else:
        h["status"] = "failing"
        h["fails"] = int(h.get("fails", 0)) + 1
        h["last_fail"] = now
        if h["fails"] >= 3 and prev in ("healthy", "unknown", None):
            h["status"] = "dead"       # 3 consecutive failures = likely dead
    rec["health"] = h
    save_json(KEYS_FILE, keys)


def _health_monitor_loop():
    """Daemon: re-validate every stored key on an interval so dead/expiring
    keys are flagged BEFORE they fail mid-chat."""
    while True:
        try:
            keys = load_json(KEYS_FILE, {})
            for provider, rec in keys.items():
                key = rec.get("key", "")
                ok, detail, _e = validate_key(provider, key)
                record_key_health(provider, ok, detail)
                time.sleep(1)          # gentle pacing between providers
        except Exception:
            pass
        time.sleep(max(0.5, HEALTH_INTERVAL_H) * 3600)


def start_health_monitor():
    import threading
    t = threading.Thread(target=_health_monitor_loop, daemon=True)
    t.start()


def key_health_snapshot():
    keys = load_json(KEYS_FILE, {})
    out = []
    for provider, rec in keys.items():
        h = rec.get("health") or {}
        out.append({
            "provider": provider,
            "masked": rec.get("masked") or mask_key(rec.get("key", "")),
            "status": h.get("status", "unchecked"),
            "detail": h.get("detail", ""),
            "fails": h.get("fails", 0),
            "last_ok_ago_h": round((time.time() - h["last_ok"]) / 3600, 1) if h.get("last_ok") else None,
        })
    return out


# ---- #2 usage leaderboard --------------------------------------------------
def record_usage(provider, model_id, chars_in, chars_out):
    data = load_json(USAGE_FILE, {"totals": {}, "daily": {}})
    today = time.strftime("%Y-%m-%d")
    for bucket in (data["totals"], data["daily"].setdefault(today, {})):
        k = f"{provider}/{model_id}"
        u = bucket.setdefault(k, {"calls": 0, "chars_in": 0, "chars_out": 0})
        u["calls"] += 1
        u["chars_in"] += chars_in
        u["chars_out"] += chars_out
    # prune daily beyond 30 days + totals beyond 500 models
    cutoff = time.strftime("%Y-%m-%d", time.localtime(time.time() - 30 * 86400))
    data["daily"] = {d: v for d, v in sorted(data["daily"].items())[-40:] if d >= cutoff}
    if len(data["totals"]) > 500:
        top = sorted(data["totals"].items(),
                     key=lambda kv: kv[1]["calls"], reverse=True)[:500]
        data["totals"] = dict(top)
    save_json(USAGE_FILE, data)


def usage_leaderboard():
    data = load_json(USAGE_FILE, {})
    rows = []
    for mid, u in (data.get("totals") or {}).items():
        tok_est = (u["chars_in"] + u["chars_out"]) / 4.0
        saved = tok_est / 1e6 * BLENDED_RETAIL_PER_M
        prov = mid.split("/", 1)[0]
        rows.append({"model": mid, "provider": prov,
                     "calls": u["calls"],
                     "tokens_est": int(tok_est),
                     "saved_usd_est": round(saved, 2),
                     "is_free": prov in ("llm7", "pollinations") or ":free" in mid})
    rows.sort(key=lambda r: r["calls"], reverse=True)
    total_saved = sum(r["saved_usd_est"] for r in rows if r["is_free"])
    total_calls = sum(r["calls"] for r in rows)
    return {"rows": rows[:50], "total_calls": total_calls,
            "total_saved_usd_est": round(total_saved, 2)}


# ---- #8 free-model alerts panel --------------------------------------------
def free_model_alerts():
    st = load_json(FREE_STATE_FILE, {})
    now = time.time()
    window = STEALTH_WINDOW_DAYS * 86400
    new, ending, expired_recent = [], [], []
    for key, rec in (st.get("seen") or {}).items():
        info = rec.get("info") or {}
        announced = rec.get("announced")
        first = rec.get("first_seen") or now
        age_d = (now - first) / 86400
        days_left = max(0.0, (first + window - now) / 86400)
        row = {"id": info.get("id") or key.split(":", 1)[-1],
               "name": info.get("name") or key,
               "age_days": round(age_d, 1),
               "context": info.get("context") or 0}
        if announced is None:
            continue                  # seeded silently, never promoted
        if age_d <= 2:
            row["level"] = "new"
            new.append(row)
        elif days_left <= 2.5:
            row["level"] = "ending"
            row["days_left"] = round(days_left, 1)
            ending.append(row)
    for key, rec in list((st.get("expired") or {}).items()):
        if (rec.get("last_seen") or 0) > now - 7 * 86400:
            expired_recent.append({
                "id": (rec.get("info") or {}).get("id") or key,
                "days_free": round(((rec.get("last_seen") or 0) -
                                    (rec.get("first_seen") or 0)) / 86400, 1)})
    ending.sort(key=lambda r: r.get("days_left", 99))
    return {"new": new[:6], "ending_soon": ending[:8], "expired": expired_recent[:5]}


# ---- chat proxy ------------------------------------------------------------
def _try_chat(cfg, mid, payload):
    """One attempt. Returns (status, raw_bytes) or raises HTTPError."""
    body = dict(payload)
    body["model"] = mid
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    keys = load_json(KEYS_FILE, {})
    key = (keys.get(mid.split("/", 1)[0]) or {}).get("key") \
        if "/" in mid else None
    if key and cfg["auth"] == "bearer":
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(cfg["chat_url"], data=data,
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()


def proxy_chat(payload, max_fallbacks=4):
    """Try the requested model; on auth/model errors walk down the ranked
    free list (skipping image-only models) until one answers."""
    tried = []
    candidates = []
    model_field = payload.get("model", "")
    if model_field and "/" in model_field:
        prov, mid = model_field.split("/", 1)
        if prov in PROVIDERS:
            candidates.append((PROVIDERS[prov], mid))
    cat = load_json(CATALOG_FILE, {})
    for m in (cat.get("free") or []):
        mods = [x.lower() for x in (m.get("modalities") or ["text"])]
        mid_l = m["model_id"].lower()
        image_only = ("text" not in mods) or any(
            k in mid_l for k in ("image", "flux", "dall", "imagen", "sdxl",
                                 "stable-diff", "-tts", "whisper", "embed"))
        if image_only:
            continue
        cand = (PROVIDERS[m["provider"]], m["model_id"])
        if all(c[1] != cand[1] or c[0] is not cand[0] for c in candidates):
            candidates.append(cand)
        if len(candidates) >= max_fallbacks + 1:
            break
    last_err = None
    for cfg, mid in candidates[:max_fallbacks + 1]:
        try:
            status, raw = _try_chat(cfg, mid, payload)
            try:
                chars_out = len(json.loads(raw.decode("utf-8", "replace"))
                                .get("choices", [{}])[0]
                                .get("message", {}).get("content") or "")
            except Exception:
                chars_out = len(raw)
            chars_in = sum(len(str(m.get("content", "")))
                           for m in payload.get("messages", []))
            record_usage(_provider_by_chat_url(cfg["chat_url"]), mid,
                         chars_in, chars_out)
            return status, raw, {"served_by": f"{cfg['chat_url']}", "model": mid,
                                 "fallbacks_used": len(tried)}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200]
            tried.append(f"{mid}: HTTP {e.code}")
            if e.code not in (401, 403, 404, 429, 502, 503):
                return e.code, json.dumps({"error": detail}).encode(), {}
            last_err = detail
        except Exception as e:
            tried.append(f"{mid}: {str(e)[:60]}")
            last_err = str(e)[:200]
    return 502, json.dumps({"error": f"all fallbacks failed: {'; '.join(tried)}",
                            "last": last_err}).encode(), {}


# ---- HTTP server -----------------------------------------------------------
DASH = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>OMNI Gateway</title><style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0;padding:24px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin-bottom:16px}
h1{margin:0 0 4px}.sub{color:#8b949e;margin-bottom:20px}
input,button,select{font-size:14px;padding:10px;border-radius:8px;border:1px solid #30363d;background:#0d1117;color:#e6edf3}
button{background:#238636;cursor:pointer;border:none;font-weight:600}
button.gray{background:#30363d}
table{width:100%;border-collapse:collapse;margin-top:12px}
td,th{padding:8px 10px;border-bottom:1px solid #21262d;text-align:left;font-size:13px}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;background:#1f6feb}
.free{background:#238636}.ctx{color:#8b949e}
.row{display:flex;gap:10px;flex-wrap:wrap}
#msg{margin-top:10px;color:#58a6ff;min-height:20px}
</style></head><body>
<h1>🌐 OMNI Gateway</h1><div class=sub>one keyring · every provider · free models ranked</div>
<div class=card><b>🔑 Add an API key</b>
<div class=row style=margin-top:10px>
<input id=key style="flex:1;min-width:260px" placeholder="paste key (gsk_… sk-or-… nvapi-… AIza… csk-… hf_…)">
<button onclick=addKey()>Validate &amp; Save</button>
<button class=gray onclick=scan()>Re-scan all</button></div><div id=msg></div></div>
<div class=card id=alertsCard><b>🔔 Free-model alerts</b> <span class=ctx>(from runner watcher)</span><div id=alerts style=margin-top:8px></div></div>
<div class=card><b>❤️ Key health</b> <span class=ctx>(re-checked every __HEALTH_H__h)</span>
<table id=healthTbl><tr><th>Provider</th><th>Key</th><th>Status</th></tr></table></div>
<div class=card><b>🏆 Ranked FREE models</b> <span id=cataloginfo class=ctx></span>
<table id=tbl><tr><th>#</th><th>Model</th><th>Provider</th><th>Context</th><th>Input</th></tr></table></div>
<div class=card><b>📊 Usage leaderboard</b> <span id=savedInfo class=ctx></span>
<table id=usageTbl><tr><th>#</th><th>Model</th><th>Calls</th><th>Tokens~</th><th>Saved est.</th></tr></table></div>
<div class=card><b>⚡ Use anywhere (OpenAI-compatible)</b>
<pre style=color:#8b949e;baseURL = "http://localhost:__PORT__/v1"
model   = "&lt;pick from table&gt;"   e.g. openrouter/stealth/ox-alpha
key     = anything</pre>
<p style=margin:6px 0 0><a href=/chat style=color:#58a6ff>💬 Open chat test UI →</a></p></div>
<script>
async function refresh(){const s=await(await fetch('/api/status')).json();
let h='';for(const[p,r]of Object.entries(s.keys||{})){h+=`<tr><td>${p}</td><td>${r.masked}</td><td>${r.ok?'✅':'❌ '+r.detail}</td><td><button class=gray onclick=delKey('${p}')>x</button></td></tr>`}
document.getElementById('keys').innerHTML=h||'<i>no keys yet</i>';
const c=await(await fetch('/api/free')).json();
document.getElementById('cataloginfo').textContent=`(${(c.free||[]).length} free · scan ${new Date((c.ts||0)*1000).toLocaleTimeString()})`;
let t='<tr><th>#</th><th>Model</th><th>Provider</th><th>Context</th><th>Input</th></tr>';
(c.free||[]).slice(0,60).forEach((m,i)=>{t+=`<tr><td>${i+1}</td><td>${m.model_id}</td><td><span class=badge>${m.provider}</span></td><td class=ctx>${(m.context/1000||'?')+'K'}</td><td>${[...new Set([...m.modalities,'text'])].join('+')}</td></tr>`});
document.getElementById('tbl').innerHTML=t;
try{const hk=await(await fetch('/api/health')).json();let ht='<tr><th>Provider</th><th>Key</th><th>Status</th></tr>';
(hk.keys||[]).forEach(k=>{const ic=k.status==='healthy'?'✅':(k.status==='dead'?'💀':'⚠️');
ht+=`<tr><td>${k.provider}</td><td class=ctx>${k.masked}</td><td>${ic} ${k.status}${k.fails?' ('+k.fails+' fails)':''}</td></tr>`});
document.getElementById('healthTbl').innerHTML=ht;}catch(e){}
try{const u=await(await fetch('/api/usage')).json();
document.getElementById('savedInfo').textContent=`${u.total_calls||0} calls · saved ~$${u.total_saved_usd_est||0}`;
let ut='<tr><th>#</th><th>Model</th><th>Calls</th><th>Tokens~</th><th>Saved est.</th></tr>';
(u.rows||[]).slice(0,15).forEach((r,i)=>{ut+=`<tr><td>${i+1}</td><td>${r.model}</td><td>${r.calls}</td><td class=ctx>${r.tokens_est>=1000?(r.tokens_est/1000).toFixed(1)+'K':r.tokens_est}</td><td>$${r.saved_usd_est}</td></tr>`});
document.getElementById('usageTbl').innerHTML=ut;}catch(e){}
try{const al=await(await fetch('/api/alerts')).json();let ah='';
(al.new||[]).forEach(m=>{ah+=`<div>🟢 NEW: ${m.id} <span class=ctx>(${m.age_days}d old)</span></div>`});
(al.ending_soon||[]).forEach(m=>{ah+=`<div>🟡 ENDING: ${m.id} <span class=ctx>~${m.days_left}d left</span></div>`});
(al.expired||[]).forEach(m=>{ah+=`<div>🔴 ENDED: ${m.id} <span class=ctx>(lived ~${m.days_free}d)</span></div>`});
document.getElementById('alerts').innerHTML=ah||'<span class=ctx>all quiet — no new/expiring free models</span>';}catch(e){}}
async function addKey(){const k=document.getElementById('key').value.trim();if(!k)return;
document.getElementById('msg').textContent='validating…';
const r=await(await fetch('/api/keys',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:k})})).json();
document.getElementById('msg').textContent=r.ok?('✅ '+r.provider+' validated ('+r.detail+') — scanning catalog…'):('❌ '+(r.detail||'invalid'));
document.getElementById('key').value='';await scan();refresh();}
async function delKey(p){await fetch('/api/keys/'+p,{method:'DELETE'});scan();refresh();}
async function scan(){document.getElementById('msg').textContent='scanning providers…';await fetch('/api/scan',{method:'POST'});document.getElementById('msg').textContent='';refresh();}
refresh();setInterval(refresh,30000);
</script>
<table class=card id=keys></table>
</body></html>"""


CHAT_PAGE = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>OMNI Chat Test</title><style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0;padding:16px;display:flex;flex-direction:column;height:100vh;box-sizing:border-box}
header{display:flex;gap:10px;align-items:center;margin-bottom:10px}
select,input{padding:9px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#e6edf3}
#log{flex:1;overflow-y:auto;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px}
.msg{margin-bottom:10px;padding:8px 12px;border-radius:10px;max-width:85%;white-space:pre-wrap;word-wrap:break-word;font-size:14px}
.you{background:#1f6feb;margin-left:auto}.bot{background:#21262d;border:1px solid #30363d}
.meta{font-size:11px;color:#8b949e;margin-top:4px}
.bar{display:flex;gap:8px;margin-top:10px}
input[type=text]{flex:1}
button{background:#238636;color:#fff;border:none;border-radius:8px;padding:9px 18px;font-weight:600;cursor:pointer}
</style></head><body>
<header><b>💬 OMNI Chat</b>
<select id=model></select>
<button class=gray onclick="location='/'" style=background:#30363d>← dashboard</button></header>
<div id=log></div>
<div class=bar><input type=text id=q placeholder="message… (Enter to send)" autofocus>
<button onclick=send()>Send</button></div>
<script>
async function loadModels(){const c=await(await fetch('/api/free')).json();
const s=document.getElementById('model');s.innerHTML='';
(c.free||[]).filter(m=>(m.modalities||[]).includes('text')).slice(0,80).forEach(m=>{
const o=document.createElement('option');o.value=m.id;o.textContent=`${m.provider} · ${m.model_id}`;s.appendChild(o)});}
function add(t,cls,meta){const d=document.createElement('div');d.className='msg '+cls;d.textContent=t;
if(meta){const m=document.createElement('div');m.className='meta';m.textContent=meta;d.appendChild(m)}
document.getElementById('log').appendChild(d);document.getElementById('log').scrollTop=99999;}
async function send(){const q=document.getElementById('q');const v=q.value.trim();if(!v)return;
q.value='';add(v,'you');
const model=document.getElementById('model').value;
try{const r=await(await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({model:model,message:v})})).json();
add(r.reply||('❌ '+(r.error||'no reply')),'bot',r.served_by?('via '+r.served_by+(r.fallbacks_used?' ('+r.fallbacks_used+' fallbacks)':'')):'');}
catch(e){add('❌ '+e.message,'bot');}}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
loadModels();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, bytes):
            raw = body
        elif "html" in ctype:
            raw = body.encode("utf-8")
        else:
            raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/":
            return self._send(200, DASH.replace("__PORT__", str(PORT))
                              .replace("__HEALTH_H__", str(int(HEALTH_INTERVAL_H))),
                              "text/html; charset=utf-8")
        if p == "/chat":
            return self._send(200, CHAT_PAGE, "text/html; charset=utf-8")
        if p == "/api/status":
            keys = {k: {"masked": v.get("masked", mask_key(v.get("key", ""))),
                        "ok": v.get("ok", False)}
                    for k, v in load_json(KEYS_FILE, {}).items()}
            return self._send(200, {"port": PORT, "providers": len(PROVIDERS),
                                    "keys": keys})
        if p == "/api/free":
            cat = load_json(CATALOG_FILE, {"free": [], "ts": 0})
            return self._send(200, {"ts": cat.get("ts", 0), "free": cat.get("free", [])[:200]})
        if p.startswith("/v1/models"):
            cat = load_json(CATALOG_FILE, {})
            data = [{"id": m["id"], "object": "model"} for m in cat.get("free", [])]
            return self._send(200, {"object": "list", "data": data})
        if p == "/api/health":
            return self._send(200, {"keys": key_health_snapshot()})
        if p == "/api/usage":
            return self._send(200, usage_leaderboard())
        if p == "/api/alerts":
            return self._send(200, free_model_alerts())
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        p = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8", "replace") or "{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        if p == "/api/keys":
            key = str(payload.get("key", "")).strip()
            if not key:
                return self._send(400, {"error": "empty key"})
            provider = detect_provider(key)
            if not provider:
                return self._send(200, {"ok": False, "detail":
                                        "could not detect provider from key prefix"})
            ok, detail, entries = validate_key(provider, key)
            keys = load_json(KEYS_FILE, {})
            if ok:
                keys[provider] = {"key": key, "masked": mask_key(key),
                                  "added": time.time()}
                save_json(KEYS_FILE, keys)
            return self._send(200, {"ok": ok, "provider": provider, "detail": detail})
        if p == "/api/scan":
            cat = scan_all()
            return self._send(200, {"scanned": len(cat.get("results", {})),
                                    "free_found": len(cat.get("free", []))})
        if p == "/api/chat":
            msg = str(payload.get("message", ""))[:4000]
            model = payload.get("model", "")
            if not msg:
                return self._send(400, {"error": "empty message"})
            status, raw, meta = proxy_chat({"model": model,
                                            "messages": [{"role": "user", "content": msg}],
                                            "max_tokens": 800})
            try:
                body = json.loads(raw.decode("utf-8", "replace"))
                reply = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            except Exception:
                reply = ""
            if not reply:
                return self._send(status if status else 502,
                                  {"error": raw.decode("utf-8", "replace")[:300]})
            served = meta.get("model") or meta.get("served_by", "")
            return self._send(200, {"reply": reply[:6000], "served_by": served,
                                    "fallbacks_used": meta.get("fallbacks_used", 0)})
        if p == "/v1/chat/completions":
            try:
                status, raw, meta = proxy_chat(payload)
                if meta.get("fallbacks_used"):
                    try:
                        body = json.loads(raw.decode("utf-8", "replace"))
                        if isinstance(body, dict):
                            body.setdefault("omni", {k: v for k, v in meta.items()
                                                     if k != "served_by"})
                            raw = json.dumps(body).encode()
                    except Exception:
                        pass
                return self._send(status, raw)
            except urllib.error.HTTPError as e:
                return self._send(e.code, {"error": e.read().decode("utf-8", "replace")[:300]})
            except Exception as e:
                return self._send(502, {"error": str(e)[:200]})
        return self._send(404, {"error": "not found"})

    def do_DELETE(self):
        p = self.path.split("?")[0].rstrip("/")
        m = re.match(r"^/api/keys/(.+)$", p)
        if m:
            name = m.group(1)
            keys = load_json(KEYS_FILE, {})
            keys.pop(name, None)
            save_json(KEYS_FILE, keys)
            return self._send(200, {"deleted": name})
        return self._send(404, {"error": "not found"})


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    start_health_monitor()
    print(f"[omni] gateway on http://127.0.0.1:{PORT} "
          f"({len(PROVIDERS)} providers registered, "
          f"health monitor every {HEALTH_INTERVAL_H}h)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
