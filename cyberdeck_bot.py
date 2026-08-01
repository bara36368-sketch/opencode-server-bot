"""
Cyberdeck Bot — Dedicated Telegram bot for Cyberdeck Agent v7.1
Token: 8954725646:AAFHDboglEzsIX864QtVlVyp_zYhaUUrK0M
"""
import os, sys, json, time, asyncio, logging, traceback, hashlib, copy, re, urllib.request, urllib.parse, subprocess
from datetime import datetime

import androidllm_models

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

for _lib in ["httpx", "httpcore", "urllib3", "chardet"]:
    logging.getLogger(_lib).setLevel(logging.WARNING)

logging.basicConfig(filename="cyberdeck_bot.log", level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

BOT_TOKEN = "8954725646:AAFHDboglEzsIX864QtVlVyp_zYhaUUrK0M"
OWNER_ID = "8585609360"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BOT_VERSION = "7.1.0"
BOT_NAME = "CyberdeckBot"

try:
    import httpx
except ImportError:
    httpx = None

_http = None
_shutdown = asyncio.Event()
_last_update = 0
OFFSET_FILE = os.path.join(DIR, ".cyberdeck.offset")
_sessions = {}
_processed = set()
_active_tasks = {}

def log(msg, section="bot"):
    ts = time.strftime("%H:%M:%S")
    print(f"{ts} [{section}] {msg}", flush=True)
    logging.info(f"{ts} [{section}] {msg}")

def _load_offset():
    global _last_update
    try:
        with open(OFFSET_FILE, encoding="utf-8") as f:
            _last_update = int(f.read().strip())
    except:
        pass

def _save_offset():
    try:
        with open(OFFSET_FILE, "w", encoding="utf-8") as f:
            f.write(str(_last_update))
    except:
        pass

async def get_http():
    global _http
    if httpx is None:
        raise RuntimeError("httpx required: pip install httpx")
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10, read=60, write=30, pool=10),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            http2=False,
        )
    return _http

async def tg(method, data=None):
    c = await get_http()
    for attempt in range(2):
        try:
            r = await c.post(f"{TG_API}/{method}", json=data or {}, timeout=15)
            resp = r.json()
            if resp.get("ok"):
                return resp
            if resp.get("error_code") == 429:
                retry = resp.get("parameters", {}).get("retry_after", 5)
                await asyncio.sleep(retry)
                continue
            log(f"TG error: {method} {resp}")
            return resp
        except Exception as e:
            if attempt == 0:
                await asyncio.sleep(1)
                continue
            log(f"TG error: {method} {e}")
            return {"ok": False}
    return {"ok": False}

async def send(chat, text, parse_mode="HTML"):
    raw = str(text) if text else ""
    if not raw:
        return {"ok": True}
    MAX_TG = 4096
    if len(raw) <= MAX_TG:
        return await tg("sendMessage", {"chat_id": chat, "text": raw, "parse_mode": parse_mode})
    chunks = []
    while raw:
        if len(raw) <= MAX_TG:
            chunks.append(raw)
            break
        split_at = raw.rfind("\n", 0, MAX_TG)
        if split_at < MAX_TG // 2:
            split_at = raw.rfind(" ", 0, MAX_TG)
        if split_at < MAX_TG // 2:
            split_at = MAX_TG
        chunks.append(raw[:split_at])
        raw = raw[split_at:].lstrip()
    for chunk in chunks:
        await tg("sendMessage", {"chat_id": chat, "text": chunk, "parse_mode": parse_mode})
        await asyncio.sleep(0.3)
    return {"ok": True}

async def typing(chat):
    await tg("sendChatAction", {"chat_id": chat, "action": "typing"})

def _safe_parse_json(text):
    try:
        return json.loads(text)
    except:
        return None

# ============================================================
# Load Cyberdeck Agent
# ============================================================
cyberdeck = None
cd_classes = {}

def load_cyberdeck():
    global cyberdeck, cd_classes
    try:
        import cyberdeck_agent as ca
        cd_classes = {
            "ComponentDatabase": ca.ComponentDatabase,
            "CyberdeckLearner": ca.CyberdeckLearner,
            "CompatibilityEngine": ca.CompatibilityEngine,
            "CableRouter": ca.CableRouter,
            "TutorialGenerator": ca.TutorialGenerator,
            "IdeaGenerator": ca.IdeaGenerator,
            "VideoLearningQueue": ca.VideoLearningQueue,
            "ImageAnalyzer": ca.ImageAnalyzer,
            "BuildOptimizer": ca.BuildOptimizer,
            "PackGenerator": ca.PackGenerator,
            "BuildGenerator": ca.BuildGenerator,
            "HardwareModuleGenerator": ca.HardwareModuleGenerator,
            "BuildComparison": ca.BuildComparison,
            "BOMExporter": ca.BOMExporter,
            "BuildTimeline": ca.BuildTimeline,
            "Changelog": ca.Changelog,
            "DashboardReRender": ca.DashboardReRender,
            "IndonesianTranslator": ca.IndonesianTranslator,
        }
        # v5.0 classes
        for cname in ["PeripheralRecommendationEngine", "AntennaCalculator", "BatterySizingCalculator",
                       "ForensicsModule", "TestEquipmentModule", "HamRadioModule"]:
            if hasattr(ca, cname):
                cd_classes[cname] = getattr(ca, cname)
        # v5.2 classes
        if hasattr(ca, 'CustomBuildEngine'):
            cd_classes["CustomBuildEngine"] = ca.CustomBuildEngine
        # v5.0 databases
        for db_name in ["COLOR_PALETTE_DATABASE", "ANTENNA_GUIDE", "AESTHETIC_MATERIAL_DATABASE",
                         "THERMAL_INTERFACE_DATABASE", "ENVIRONMENTAL_SENSOR_DATABASE",
                         "CAMERA_MODULE_DATABASE", "SDR_DATABASE", "LORA_MESH_DATABASE",
                         "NFC_RFID_DATABASE", "FINGERPRINT_DATABASE", "HAPTIC_FEEDBACK_DATABASE",
                         "IMU_DATABASE"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # v6.3 databases
        for db_name in ["ESPRESSIF_ISA_DATABASE", "BRUCE_FIRMWARE_DATABASE", "GR3ML1N_TEMPLATE",
                         "HOMEBREW_OS_DATABASE", "EDGE_AI_DATABASE", "ESP_NOW_DATABASE",
                         "WIFI_BLE_SCANNER_DATABASE"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # v6.5 classes
        for cname in ["OllamaAssistant", "KiwixKnowledgeBase", "ParametricEnclosureGenerator",
                       "MeshNetworkPlanner", "BOMTracker", "BuildProfileManager"]:
            if hasattr(ca, cname):
                cd_classes[cname] = getattr(ca, cname)
        # v6.5 databases
        for db_name in ["OLLAMA_MODEL_DATABASE", "SBC_TO_RECOMMENDED_MODEL", "ZIM_DATABASE",
                         "BUILD_PURPOSE_ZIM_MAP", "ENCLOSURE_MATERIAL_DATABASE",
                         "MESH_FREQUENCY_PLAN", "LORA_HARDWARE_DATABASE", "MESH_CONFIG_TEMPLATES",
                         "PRICE_TIERS", "BOM_PROJECTS_FILE", "BUILD_PROFILES_DATABASE",
                         "PROFILE_OVERRIDE_RULES"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # v6.5 feature 7-12 classes
        for cname in ["PowerMonitor", "OSConfigurator", "BuildDocGenerator",
                       "SDRIntegration", "CommunityExplorer", "AestheticEngine"]:
            if hasattr(ca, cname):
                cd_classes[cname] = getattr(ca, cname)
        # v6.5 feature 7-12 databases
        for db_name in ["UPS_HAT_DATABASE", "BATTERY_CHEMISTRY", "POWER_PROFILES",
                         "OS_DATABASE", "BUILD_OS_MAP", "WIRING_TEMPLATES",
                         "SDR_HARDWARE_DATABASE", "FREQUENCY_BANDS", "SDR_INTERFACES",
                         "SAMPLE_COMMUNITY_BUILDS", "BUILD_TAGS",
                         "AESTHETIC_STYLES", "COLOR_PALETTES"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # v7.0 classes
        for cname in ["WriterDeckAdvisor", "ThermalDesigner", "BuildComparator",
                       "CostOptimizer", "UpgradeAdvisor", "SolarPlanner",
                       "BeginnerWizard", "BuildSharing"]:
            if hasattr(ca, cname):
                cd_classes[cname] = getattr(ca, cname)
        # v7.0 databases
        for db_name in ["WRITERDECK_DISPLAYS", "WRITER_SOFTWARE", "WRITER_OS_TEMPLATES", "WRITER_KEYBOARDS",
                         "SBC_THERMAL_DATA", "COOLING_PARTS_DATABASE",
                         "COMPARISON_METRICS",
                         "PRICE_SOURCE_DATABASE", "REGION_VENDORS", "BUDGET_TEMPLATES",
                         "UPGRADE_PATHS_DATABASE",
                         "SOLAR_PANEL_DATABASE", "BATTERY_BANK_DATABASE", "SOLAR_CONTROLLER_DATABASE",
                         "SUN_HOURS_BY_REGION", "OFFGRID_TEMPLATES",
                         "WIZARD_QUESTIONS", "WIZARD_TEMPLATES",
                         "SHARE_TEMPLATES", "EXPORT_THEMES"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # v7.1 classes
        for cname in ["LocalAITuner", "HotSwapPlanner", "OrthoAdvisor",
                       "OffgridStackPlanner", "CommunityFeatureBoard", "CharacterBuilder",
                       "ScavengePlanner", "NewHardwareRadar"]:
            if hasattr(ca, cname):
                cd_classes[cname] = getattr(ca, cname)
        # v7.1 databases
        for db_name in ["LOCAL_AI_BOARD_DATABASE", "LOCAL_AI_MODEL_DATABASE", "BUDGET_TIERS_LOCALAI",
                         "HOTSWAP_COMPONENT_DATABASE", "HOTSWAP_REFERENCE_BUILDS",
                         "ORTHO_KEYBOARD_DATABASE", "ORTHO_FIRMWARE_GUIDE",
                         "OFFGRID_STACK_COMPONENTS", "OFFGRID_REFERENCE_BUILD",
                         "COMMUNITY_FEATURE_DATABASE",
                         "CHARACTER_TEMPLATES",
                         "SCAVENGE_SOURCES", "SCAVENGE_BUILD_PLAN",
                         "NEW_HARDWARE_2026"]:
            if hasattr(ca, db_name):
                cd_classes[db_name] = getattr(ca, db_name)
        # Dashboard (v6.0 interactive HTML)
        if hasattr(ca, 'InteractiveDashboard'):
            cd_classes["InteractiveDashboard"] = ca.InteractiveDashboard
        log(f"Loaded {len(cd_classes)} cyberdeck classes (v5.0+v5.2+v6.0+v6.3+v6.5+v7.0+v7.1)", "init")
        return True
    except Exception as e:
        log(f"Failed to load cyberdeck_agent: {e}", "init")
        return False

# ============================================================
# Provider System (minimal — reuse from setenv.sh)
# ============================================================
PROVIDERS = {}

def load_providers():
    global PROVIDERS
    env = os.environ.copy()
    for fname in [".env", "setenv.sh"]:
        fpath = os.path.join(DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        line = line.replace("export ", "")
                        k, _, v = line.partition("=")
                        env[k.strip()] = v.strip().strip('"').strip("'")

    groq_key = env.get("GROQ_KEY", "")
    if groq_key and groq_key != "set-via-env-var":
        PROVIDERS["groq"] = {"url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile", "key": groq_key}
    gemini_key = env.get("GEMINI_KEY", "")
    if gemini_key and gemini_key != "set-via-env-var":
        PROVIDERS["gemini"] = {"url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}", "model": "gemini-2.0-flash", "key": gemini_key}
    deepseek_key = env.get("DEEPSEEK_KEY", "")
    if deepseek_key and deepseek_key != "set-via-env-var":
        PROVIDERS["deepseek"] = {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat", "key": deepseek_key}
    openrouter_key = env.get("OPENROUTER_KEY", "")
    if openrouter_key and openrouter_key != "set-via-env-var":
        PROVIDERS["openrouter"] = {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "meta-llama/llama-3.3-70b-instruct:free", "key": openrouter_key}
    cerebras_key = env.get("CEREBRAS_KEY", "")
    if cerebras_key and cerebras_key != "set-via-env-var":
        PROVIDERS["cerebras"] = {"url": "https://api.cerebras.ai/v1/chat/completions", "model": "llama-3.3-70b", "key": cerebras_key}
    nvidia_key = env.get("NVIDIA_KEY", "")
    if nvidia_key and nvidia_key != "set-via-env-var":
        PROVIDERS["nvidia"] = {"url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "nvidia/llama-3.3-nemotron-super-49b-v1", "key": nvidia_key}
    mistral_key = env.get("MISTRAL_KEY", "")
    if mistral_key and mistral_key != "set-via-env-var":
        PROVIDERS["mistral"] = {"url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-small-latest", "key": mistral_key}

    omniroute_url = env.get("OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions")
    omniroute_model = env.get("OMNIROUTE_MODEL", "auto")
    omniroute_key = env.get("OMNIROUTE_KEY", "skip-auth")
    PROVIDERS["omniroute"] = {"url": omniroute_url, "model": omniroute_model, "key": omniroute_key}

    blackbox_key = env.get("BLACKBOX_KEY", "")
    if blackbox_key and blackbox_key != "set-via-env-var":
        PROVIDERS["blackbox"] = {"url": "https://api.blackbox.ai/v1/chat/completions", "model": "deepseek-v4-flash", "key": blackbox_key}

    vansrouter_url = env.get("VANSROUTER_URL", "http://localhost:3003/api/v1/chat/completions")
    vansrouter_model = env.get("VANSROUTER_MODEL", "auto")
    vansrouter_key = env.get("VANSROUTER_KEY", "skip-auth")
    PROVIDERS["vansrouter"] = {"url": vansrouter_url, "model": vansrouter_model, "key": vansrouter_key}

    androidllm_url = env.get("ANDROIDLLM_URL", "http://127.0.0.1:8080/v1/chat/completions")
    androidllm_model = env.get("ANDROIDLLM_MODEL", "auto")
    androidllm_key = env.get("ANDROIDLLM_KEY", "skip-auth")
    PROVIDERS["androidllm"] = {"url": androidllm_url, "model": androidllm_model, "key": androidllm_key}

    PROVIDERS.setdefault("9router", {"url": "http://localhost:20128/v1/chat/completions", "model": "auto", "key": "skip-auth"})
    PROVIDERS.setdefault("bitrouter", {"url": "http://127.0.0.1:4356/v1/chat/completions", "model": "qwen/qwen3.6-flash", "key": "skip-auth"})

    pj = os.path.join(DIR, "providers.json")
    if os.path.exists(pj):
        try:
            with open(pj, encoding="utf-8") as f:
                pj_data = json.load(f)
            for name, cfg in pj_data.items():
                if name in PROVIDERS:
                    continue
                if str(cfg.get("key", "")).startswith("set-via-env-var") or str(cfg.get("key", "")).startswith("not configured"):
                    continue
                if str(cfg.get("url", "")).startswith("set-via-env-var"):
                    continue
                PROVIDERS[name] = {"url": cfg.get("url", ""), "model": cfg.get("model", "auto"), "key": cfg.get("key", "skip-auth")}
            log(f"Merged {len(pj_data)} providers from providers.json", "init")
        except Exception as e:
            log(f"providers.json merge failed: {e}", "init")

    log(f"Loaded {len(PROVIDERS)} providers: {', '.join(PROVIDERS.keys())}", "init")

ACTIVE_PROVIDER = "groq"
ROUTER_CHAIN = ["9router", "vansrouter", "bitrouter", "omniroute", "androidllm"]
_user_provider = {}
_current_uid = None

def _set_provider(name):
    global ACTIVE_PROVIDER
    ACTIVE_PROVIDER = name

def _get_provider_for(uid=None):
    """Resolve the provider for a user. Per-user override wins, else global default."""
    if uid is None:
        uid = _current_uid
    if uid is not None and str(uid) in _user_provider and _user_provider[str(uid)] in PROVIDERS:
        return _user_provider[str(uid)]
    return ACTIVE_PROVIDER


def _switch_local_model(model_id):
    """Point androidllm at <model_id> and nudge androidllm-serve to restart.
    runner.py (which supervises androidllm-serve) sees the new state file and
    restarts the serve on the new model within a poll cycle."""
    try:
        androidllm_models.write_state(model_id, androidllm_models.shard_dir(model_id))
    except Exception as e:
        log(f"model state write failed: {e}", "model")
        return False
    try:
        subprocess.run(["pkill", "-f", "androidllm-serve"], capture_output=True, timeout=5)
    except Exception:
        pass
    return True


async def _shard_and_switch(chat, model):
    """Download + shard a recommended model in the background, then switch to it."""
    adir = androidllm_models.androidllm_dir()
    script = os.path.join(adir, "scripts", "shard_model.sh")
    if not os.path.exists(script):
        await send(chat, f"androidllm not found on this host ({adir}). "
                         f"Run setup in Termux first:\n<code>bash ~/androidllm/scripts/setup_termux.sh</code>")
        return
    try:
        await send(chat, f"Sharding <b>{model['id']}</b> ({model['repo']})... "
                         f"~{model['disk_gb']} GB download, this can take a while. "
                         f"I'll notify you when it's done.")
        proc = await asyncio.create_subprocess_exec(
            "bash", script, model["repo"], model["id"],
            cwd=adir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        out, _ = await proc.communicate()
        if proc.returncode == 0:
            _switch_local_model(model["id"])
            await send(chat, f"<b>{model['id']}</b> sharded and switched. "
                             f"androidllm-serve is restarting on the new model...")
        else:
            tail = (out or b"").decode("utf-8", "replace")[-800:]
            await send(chat, f"Shard failed for <b>{model['id']}</b> (exit {proc.returncode}).\n"
                             f"<pre>{tail}</pre>")
    except Exception as e:
        await send(chat, f"Shard error for <b>{model['id']}</b>: {e}")

async def call_ai(messages, provider_name=None, local_fallback=False):
    pname = provider_name or _get_provider_for()
    p = PROVIDERS.get(pname)
    if not p:
        for k, v in PROVIDERS.items():
            p = v
            pname = k
            break
    if not p:
        return "No AI provider configured. Set GROQ_KEY in setenv.sh"
    c = await get_http()
    try:
        if "gemini" in pname:
            parts = []
            for m in messages:
                role = "model" if m["role"] == "assistant" else "user"
                parts.append({"role": role, "parts": [{"text": m["content"]}]})
            r = await c.post(p["url"], json={"contents": parts}, timeout=30)
            if r.status_code == 200:
                data = r.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))
                return str(data)[:2000]
            return await _maybe_local(messages, pname, f"Gemini error: {r.status_code}", local_fallback)
        else:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {p['key']}"}
            body = {"model": p["model"], "messages": messages, "max_tokens": 4096}
            r = await c.post(p["url"], json=body, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
            return await _maybe_local(messages, pname,
                                      f"{pname} error: {r.status_code} - {r.text[:300]}",
                                      local_fallback)
    except Exception as e:
        return await _maybe_local(messages, pname, f"AI call failed: {e}", local_fallback)

# ============================================================
# Local androidllm serving — hybrid router, airgap, idle wake
# ============================================================
_offline_mode = False

_MATH_PAT = re.compile(
    r"(?:\d\s*[\+\-*/×÷]\s*\d)"
    r"|(?:what\s+is\s+\d)"
    r"|\b(?:calculate|compute|solve|arithmetic|square\s*root|"
    r"percentage|convert|conversion|terjemahkan|terjemah)\b",
    re.IGNORECASE,
)
_TRANSLATE_PAT = re.compile(
    r"^\s*(?:translate|terjemahkan|terjemah)\b"
    r"|\b(?:translate|terjemahkan|terjemah)\b(?=.*\b(?:to|into|ke|dalam)\b)",
    re.IGNORECASE,
)


def _offline_file():
    return os.path.join(androidllm_models.androidllm_dir(), "offline.json")


def _load_offline_mode():
    global _offline_mode
    try:
        with open(_offline_file(), encoding="utf-8") as f:
            _offline_mode = bool(json.load(f).get("offline"))
    except Exception:
        _offline_mode = False


def _save_offline_mode():
    try:
        os.makedirs(os.path.dirname(_offline_file()), exist_ok=True)
        with open(_offline_file(), "w", encoding="utf-8") as f:
            json.dump({"offline": bool(_offline_mode)}, f)
    except Exception:
        pass


def _androidllm_base():
    p = PROVIDERS.get("androidllm", {})
    url = p.get("url", "http://127.0.0.1:8080/v1/chat/completions")
    if url.endswith("/chat/completions"):
        return url[: -len("/chat/completions")]
    return url.rstrip("/")


def _local_available():
    """True where androidllm is actually installed + has a model on this host."""
    try:
        if os.path.exists(androidllm_models.state_path()):
            return True
        return any(androidllm_models.is_sharded(m["id"])
                   for m in androidllm_models.RECOMMENDED)
    except Exception:
        return False


def _nudge_restart():
    """Bump the state file mtime so runner.py restarts androidllm-serve now."""
    try:
        p = androidllm_models.state_path()
        if os.path.exists(p):
            os.utime(p)
    except Exception:
        pass


async def _androidllm_health():
    try:
        c = await get_http()
        r = await c.get(_androidllm_base() + "/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


async def _ensure_androidllm_up(max_wait=25):
    """Poll serve health; if down, nudge runner to restart (idle wake) and wait."""
    if await _androidllm_health():
        return True
    _nudge_restart()
    deadline = time.time() + max_wait
    while time.time() < deadline:
        await asyncio.sleep(2)
        if await _androidllm_health():
            return True
    return False


async def _local_try(messages, tag=True, max_wait=25):
    """Ask the local androidllm model. Returns (reply, ok); tags $0.00 cost."""
    up = await _ensure_androidllm_up(max_wait)
    if not up:
        return ("Local model offline (androidllm-serve not reachable). "
                "Try /status or /model.", False)
    reply = await call_ai(_rag_augment(messages), provider_name="androidllm")
    if _is_ai_error(reply, "androidllm"):
        return reply, False
    if tag:
        reply = reply + "\n\n<i>$0.00 served locally by androidllm</i>"
    return reply, True


async def _maybe_local(messages, pname, err, local_fallback):
    """Cloud-failure failover: fall back to the local model once."""
    if not local_fallback or pname == "androidllm":
        return err
    if "androidllm" not in PROVIDERS or not _local_available():
        return err
    reply, ok = await _local_try(messages, max_wait=12)
    if ok:
        log(f"local failover for {pname}", "provider")
    return reply if ok else err


def _route_local(text):
    """Heuristic: math/unit-conversion/translation -> local model (free, private)."""
    t = (text or "").strip()
    if not t:
        return False
    if _TRANSLATE_PAT.search(t):
        return True
    if _MATH_PAT.search(t):
        return True
    return False


# -- offline RAG v1: keyword-matched local knowledge injected into local calls
_rag_kb = []


def _load_rag_kb():
    global _rag_kb
    try:
        with open(os.path.join(DIR, "androidllm_rag.json"), encoding="utf-8") as f:
            _rag_kb = json.load(f)
        log(f"RAG KB loaded: {len(_rag_kb)} entries", "init")
    except Exception:
        _rag_kb = []
        log("RAG KB missing, offline augmentation disabled", "init")


def _rag_snippets(text, limit=2):
    t = (text or "").lower()
    hits = []
    for entry in _rag_kb:
        if any(k in t for k in entry.get("keywords", [])):
            hits.append(entry["text"])
            if len(hits) >= limit:
                break
    return hits


def _rag_augment(messages):
    """Prepend matching KB snippets as a system note (RAG v1, local calls only)."""
    for m in reversed(messages):
        if m.get("role") == "user":
            snips = _rag_snippets(m.get("content", ""))
            if snips:
                block = ("Local knowledge notes (use when relevant):\n"
                         + "\n---\n".join(snips))
                return [{"role": "system", "content": block}] + list(messages)
            break
    return messages


# ============================================================
# Offline Q&A mode — every chat message answered from the local
# knowledge base (RAG + component DB) with cited sources
# ============================================================
_qa_users = {}


def _qa_file():
    return os.path.join(DIR, "qa_mode.json")


def _load_qa_mode():
    global _qa_users
    try:
        with open(_qa_file(), encoding="utf-8") as f:
            _qa_users = {str(k): bool(v) for k, v in json.load(f).items()}
    except Exception:
        _qa_users = {}


def _save_qa_mode():
    try:
        with open(_qa_file(), "w", encoding="utf-8") as f:
            json.dump(_qa_users, f)
    except Exception:
        pass


def _rag_hits(text, limit=2):
    """Return matching KB entries as [{'topic','text'}], best matches first."""
    t = (text or "").lower()
    hits = []
    for entry in _rag_kb:
        if any(k in t for k in entry.get("keywords", [])):
            hits.append({"topic": entry.get("topic", entry.get("keywords", ["kb"])[0]),
                         "text": entry["text"]})
            if len(hits) >= limit:
                break
    return hits


async def _qa_answer(chat, uid, text):
    """Offline Q&A: local model + KB/component sources, cited. Cloud only if local down."""
    sources = _rag_hits(text, limit=2)
    comps = []
    if not sources and "ComponentDatabase" in cd_classes:
        try:
            from cyberdeck_agent import ComponentDatabase
            comps = ComponentDatabase.search(text, limit=2)
        except Exception:
            comps = []
    qa_sys = (CYBERDECK_SYSTEM + "\nQ&A mode: answer concisely from the attached knowledge. "
              "If the knowledge is insufficient, say what is missing and never invent specs.")
    messages = [{"role": "system", "content": qa_sys}]
    if sources:
        block = "\n---\n".join(f"[{s['topic']}] {s['text']}" for s in sources)
        messages.append({"role": "system", "content": "Knowledge base:\n" + block})
    elif comps:
        cl = "\n".join(f"- {r['name']} [{r['type']}] ${r.get('price')}" for r in comps)
        messages.append({"role": "system", "content": "Matching local parts:\n" + cl})
    messages.append({"role": "user", "content": text})
    reply, ok = await _local_try(messages, tag=False)
    if not ok:
        if _is_ai_error(reply, "androidllm"):
            fallback = await call_ai(messages, local_fallback=True)
            if not _is_ai_error(fallback, "androidllm"):
                reply = fallback
                ok = True
        if not ok:
            return reply
    cite = ""
    if sources:
        cite = "\n\n<b>Sources:</b>\n" + "\n".join(f"• {s['topic']} (local KB)" for s in sources)
    elif comps:
        cite = "\n\n<b>Sources:</b>\n" + "\n".join(
            f"• {r['name']} [{r['type']}]" for r in comps)
    tag = "\n\n<i>$0.00 served locally by androidllm</i>"
    return reply + cite + tag

# ============================================================
# Unified Coding AI — one brain routed across EVERY provider
# (your paid keys + free tiers), smartest-first with auto-fallback
# ============================================================
CODER_SYSTEM = """You are an elite software engineering AI. You write clean, correct,
production-ready code. Rules:
- Solve the exact problem asked; if ambiguous, state your assumption in one line.
- Output complete, runnable code with all imports and function signatures.
- Use modern, idiomatic patterns; explain briefly only when it helps.
- Include a short usage example and note any dependencies.
- For bugs, give root cause first, then the fix.
- No fluff, no fake APIs, no hallucinated library names."""

# Ranked smartest-first across all providers in the bot. Local androidllm is
# always last (offline/private fallback). Override with CODER_CHAIN env var.
_CODER_PRIORITY = [
    "nvidia",      # llama-3.3-nemotron-super-49b — strong free coder
    "blackbox",    # deepseek-v4-flash — strong + free
    "deepseek",    # deepseek-chat — strong
    "cerebras",    # fast Llama/Qwen
    "openrouter",  # free llama/qwen/deepseek variants
    "mistral",     # codestral-flash if configured
    "gemini",      # gemini-2.0-flash free tier
    "groq",        # llama-3.3-70b, qwen-2.5-32b (fast, free)
    "omniroute",   # 290+ providers
    "9router",     # universal gateway
    "vansrouter",  # local 9Router fork
    "bitrouter",   # local router
    "androidllm",  # local model on the phone (last resort, offline/private)
]

def _coding_chain():
    if _offline_mode:
        return [p for p in ("androidllm",) if p in PROVIDERS]
    env_chain = os.environ.get("CODER_CHAIN", "").strip()
    if env_chain:
        return [p.strip() for p in env_chain.split(",") if p.strip() in PROVIDERS]
    return [p for p in _CODER_PRIORITY if p in PROVIDERS]

def _is_ai_error(reply, pname):
    """call_ai returns content on success, or a short error string on failure."""
    if not isinstance(reply, str):
        return True
    if reply.startswith(f"{pname} error:"):
        return True
    if reply.startswith("Gemini error:"):
        return True
    if reply.startswith("AI call failed") or reply.startswith("No AI provider configured"):
        return True
    return False

async def call_coding(messages, chain=None):
    """Route a coding prompt across the chain; auto-fall back on failure."""
    chain = chain if chain is not None else _coding_chain()
    if not chain:
        return "No coding providers available.", None, []
    used = []
    for pname in chain:
        try:
            reply = await call_ai(messages, provider_name=pname)
        except Exception as e:
            used.append((pname, f"failed: {e}"))
            continue
        if _is_ai_error(reply, pname):
            used.append((pname, reply))
            continue
        used.append((pname, "ok"))
        return reply, pname, used
    return "All coding providers failed.", None, used

async def handle_code(chat, task):
    if not task:
        return await send(chat, "Usage: /code &lt;your coding task&gt;")
    await send(chat, "Coding brain: querying best available model...")
    msgs = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user", "content": task},
    ]
    reply, pname, used = await call_coding(msgs)
    if not pname:
        return await send(chat, reply)
    tag = f"\n\n<i>⚡ {pname}</i>"
    if pname == "androidllm":
        tag += " <i>$0.00 served locally</i>"
    tried = [p for p, s in used if s != "ok"]
    if tried:
        tag += f" <i>(fallback: {', '.join(tried)})</i>"
    await send(chat, reply + tag)

async def handle_codeall(chat, task):
    if not task:
        return await send(chat, "Usage: /codeall &lt;task&gt; — asks the top coding models in parallel")
    chain = _coding_chain()[:3]
    if not chain:
        return await send(chat, "No coding providers available.")
    await send(chat, f"Ask-all: querying <b>{len(chain)}</b> models in parallel ({', '.join(chain)})...")
    msgs = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user", "content": task},
    ]
    results = await asyncio.gather(*[call_ai(msgs, provider_name=p) for p in chain], return_exceptions=True)
    blocks = []
    for p, r in zip(chain, results):
        if isinstance(r, BaseException) or _is_ai_error(r, p):
            blocks.append(f"<b>{p}</b>: ❌ {str(r)[:200]}")
        else:
            blocks.append(f"<b>{p}</b>:\n{r}")
    await send(chat, "\n\n".join(blocks))

_coder_mode = {}

def _brain_system(uid=None):
    """System prompt for the user's active brain (default or Obsidian memory brain)."""
    if uid is None:
        uid = _current_uid
    bname = _user_brain.get(str(uid), "default")
    brain = BRAINS.get(bname, BRAINS["default"])
    sys_text = brain["system"]
    if brain.get("memory"):
        ctx = _obsidian_memory_context()
        if ctx:
            sys_text = sys_text + "\n\n--- MEMORY ---\n" + ctx
    return sys_text


def _obsidian_memory_context(limit=8):
    """List the most recent Obsidian memory notes (cached 60s) for brain injection."""
    now = time.time()
    if now - _brain_memory_cache["ts"] < 60:
        return _brain_memory_cache["text"]
    try:
        import cyberdeck_agent as _ca
        ndir = getattr(_ca, "OBSIDIAN_NOTES_DIR", None)
        if not ndir or not os.path.isdir(ndir):
            return ""
        notes = []
        for fn in os.listdir(ndir):
            if fn.endswith(".md"):
                fp = os.path.join(ndir, fn)
                try:
                    notes.append((os.path.getmtime(fp), fn[:-3]))
                except Exception:
                    pass
        notes.sort(reverse=True)
        if not notes:
            return ""
        lines = ["Recent memory notes:"]
        for _, title in notes[:limit]:
            lines.append(f"  - {title}")
        _brain_memory_cache["ts"] = now
        _brain_memory_cache["text"] = "\n".join(lines)
        return _brain_memory_cache["text"]
    except Exception:
        return ""


def _obsidian_learn(user_msg, reply):
    """Persist a Telegram conversation as an Obsidian memory note."""
    try:
        import cyberdeck_agent as _ca
        brain = _ca.ObsidianBrain()
        brain.learn_chat(str(user_msg)[:3000], str(reply)[:3000], "telegram_chat")
    except Exception:
        pass

def is_owner(uid):
    return str(uid) == OWNER_ID

# ============================================================
# Cyberdeck System Prompt
# ============================================================
CYBERDECK_SYSTEM = """You are CyberdeckBot, an expert cyberdeck builder and electronics specialist.
You help users design, build, and optimize cyberdecks — portable custom computers.
You know about SBCs (Raspberry Pi, Orange Pi, Radxa, etc.), displays, keyboards, power systems,
enclosures, cooling, PCBs, wiring, connectivity, and accessories.
You can generate builds, BOMs, tutorials, 3D models, PCB designs, cable routing plans,
and compatibility checks. Be concise, technical, and helpful.
When given a build request, provide: components list with prices, compatibility notes,
assembly steps, and tips. Use markdown formatting."""

# ============================================================
# Brain System — switchable AI personas (Obsidian memory brain)
# ============================================================
BRAINS = {
    "default": {
        "desc": "Standard cyberdeck builder",
        "system": CYBERDECK_SYSTEM,
    },
    "obsidian": {
        "desc": "Obsidian memory brain — persistent learning vault",
        "system": CYBERDECK_SYSTEM + ("\n\nYou have a persistent Obsidian memory vault at "
            "~/Documents/obsidian-vaults/CyberdeckBrain/AgentMemory. Notes from past "
            "builds, chats, videos, and insights are injected into your context. Use "
            "that memory to personalize answers and recall prior discussions."),
        "memory": True,
        "learn": True,
    },
    "writer": {
        "desc": "WriterDeck-focused brain (e-ink writing machines)",
        "system": CYBERDECK_SYSTEM + ("\n\nFocus on WriterDeck-style builds: e-ink displays, "
            "distraction-free writing software (FocusWriter, WordGrinder), low-power SBCs, "
            "mechanical keyboards, and writing-first ergonomics."),
    },
    "coder": {
        "desc": "Coding terminal brain",
        "system": CYBERDECK_SYSTEM + ("\n\nFocus on coding terminal builds: portable dev setups, "
            "terminal UIs (tmux, vim), OS configs for programming, hotkey layout, and "
            "keyboard-centric workflows."),
    },
    "coding": {
        "desc": "Unified coding AI — routed across every provider (paid + free), auto-fallback",
        "system": CODER_SYSTEM,
    },
    "hacker": {
        "desc": "Security / pentest brain",
        "system": CYBERDECK_SYSTEM + ("\n\nFocus on security and pentest builds: Kali/Parrot, "
            "WiFi/SDR gear, forensics, and hardened enclosures. Keep all advice legal "
            "and ethical."),
    },
    "researcher": {
        "desc": "Research / AI experiments brain",
        "system": CYBERDECK_SYSTEM + ("\n\nFocus on research and AI builds: LLM inference on SBCs, "
            "edge AI (TensorFlow Micro), homelab experiments, and sensor/data logging rigs."),
    },
}
_user_brain = {}
_brain_memory_cache = {"ts": 0, "text": ""}

# ============================================================
# Command Handlers
# ============================================================
async def handle_command(chat, uid, text, msg):
    global _current_uid
    _current_uid = uid
    parts = text.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        await send(chat, f"""<b>CyberdeckBot v{BOT_VERSION}</b>

Dedicated cyberdeck builder with v6.0 AI engine.

<b>v6.3 2026 Trends:</b>
/compare &lt;BuildA&gt; | &lt;BuildB&gt; — Side-by-side build comparison
/bomcsv &lt;build&gt; — Export BOM as CSV
/timeline &lt;save|list|diff&gt; — Build revision timeline
/changelog — System version history
/dashboard_render &lt;build&gt; — Re-generate HTML dashboard
/idbuild &lt;build&gt; — Indonesian language build instructions
/isa — ESP32 ISA architecture guide (XTensa vs RISC-V)
/bruce — Bruce firmware builds for ESP32
/gr3ml1n — GR3ML1N handheld cyberdeck template
/homebrew_os — Homebrew OS cards (Solar OS, Micro Journal)
/edgeai — Edge AI configs (TensorFlow Micro on ESP32-S3)
/espnow — ESP-NOW / Mesh networking guide
/wifi_scan — WiFi/BLE wardriving &amp; scanner presets

<b>v6.5 New Features:</b>
/ollama — Ollama AI model recommendations &amp; setup for SBCs
/kiwix — Kiwix/ZIM offline knowledge base for cyberdecks
/enclosure — Parametric enclosure generator (OpenSCAD)
/power — UPS HAT database, runtime estimation &amp; safe shutdown scripts
/osconf — OS recommendations, post-install scripts &amp; docker-compose
/builddoc — Build documentation with wiring diagrams &amp; Reddit/Hackaday templates
/sdr — SDR hardware database, frequency bands &amp; GNU Radio flowgraphs
/explore — Community build explorer with 15+ featured builds
/aesthetic — Aesthetic style engine with 14 themes &amp; CSS output

<b>v6.2 Hardware Modules:</b>
/hardware — Hardware module catalog (NATO rails, sliding screens, NP-F batteries)
/hardware &lt;module_id&gt; — Details for a specific module
/hardware nato &lt;rails&gt; — NATO rail layout plan
/hardware slide &lt;inches&gt; [heavy] — Sliding screen assembly plan
/hardware npf [dual] — NP-F battery integration plan
/modules — Li'l PCB hot-swappable module ecosystem
/modules &lt;mod1&gt; &lt;mod2&gt;... — Configure a module stack
/lilpcb &lt;modules&gt; — Li'l PCB configuration plan

<b>v6.0 Commands:</b>
/cyberdeck &lt;request&gt; — Build a cyberdeck from description
/build &lt;category&gt; [tier] — Auto-build for category
/bom &lt;request&gt; — Bill of materials
/compat &lt;sbc&gt; &lt;display&gt; — Compatibility check
/tutorial &lt;request&gt; — Step-by-step assembly guide
/upgrade &lt;build&gt; — Suggest upgrades
/ideas [category] — Build ideas
/ideasearch &lt;keywords&gt; [budget $X] [skill level] — Search the idea database locally
/search &lt;query&gt; [budget $X] [category] [sort price] — Search components with filters
/3d &lt;desc&gt; [style] — Generate 3D model (OpenSCAD)
/pcb &lt;desc&gt; — PCB design
/cables &lt;build&gt; — Cable routing plan
/flaws &lt;build&gt; — Detect flaws
/pack &lt;build&gt; — Generate build pack
/career &lt;career&gt; — Career-specific build
/dashboard &lt;build&gt; — Interactive HTML dashboard
/specs &lt;component&gt; — Detailed specs
/styles — List 3D styles
/categories — List build categories
/tiers — List tier system
/list — List all components
/status — Bot status
/provider — Switch AI provider (9router, vansrouter, bitrouter, androidllm, groq...)
/provider routers — List local router providers
/provider test &lt;name&gt; — Ping a provider
/providers — List providers
/model — Switch local androidllm model (qwen15, smollm2, qwen3)
/offline on|off — Airgap mode: all AI runs on the local androidllm model ($0.00, no internet)
/qa on|off — Offline Q&A mode: answers from local KB + parts DB with cited sources
/sysinfo — Deck system info (CPU, RAM, temp, disk, battery)
/top — Top processes by CPU
/wifi — Current WiFi network info
/stop — Interrupt the current AI reply
/survival &lt;topic&gt; — Offline survival guides (water, fire, shelter, first-aid, navigation, signal, weather)
/morse [decode] &lt;text&gt; — Morse code encode/decode (offline)
/convert &lt;value&gt; &lt;from&gt; to &lt;to&gt; — Unit converter (length, weight, data, speed, power, energy, temp, time)
/solarcalc &lt;panelW&gt; [batteryWh] [deckW] [sunH] — Offline solar sizing calculator
/brain — Switch AI brain (obsidian memory brain, writer, coder...)
/brains — List brains
/coder on|off — Unified coding AI mode (all providers, auto-fallback)
/code &lt;task&gt; — One-shot coding with smartest model + fallback
/codeall &lt;task&gt; — Compare top 3 coding models in parallel
/v1 — Switch to General AI mode (opencode-bot)
/v2 — Switch to Cyberdeck mode

<b>AI Gateway Tools:</b>
/9router — Universal AI Gateway (upstream)
/omniroute — Fork of 9Router with 290+ providers
/vansrouter — Local 9Router fork
/openclaw — AI multi-tool orchestration CLI
/blackbox — Multi-model AI provider
/odysseus — Self-hosted AI workspace
/hermes — Hermes Agent (Nous Research self-improving AI)
/obsidian — Obsidian AI CLI + MCP integration

<b>v5.2 Experimental:</b>
/cb — Interactive custom build (mix-and-match)

<b>v5.0 Experimental:</b>
/peripherals &lt;category&gt; — Recommend peripherals
/antenna &lt;freq_mhz&gt; — Antenna calculator
/battery &lt;cells&gt; [watts] — Battery sizing
/forensics — Digital forensics tools
/testeq — Test equipment catalog
/hamradio — Ham radio bands &amp; modes
/palette — Color palettes
/material — Aesthetic materials
/thermal — Thermal interface materials

<b>v6.5 New Features (cont):</b>
/mesh — Mesh network planner (LoRa, ESP-NOW, Meshtastic)
/bomtrack — Live BOM &amp; cost tracker with project saving
/profile — Build category profiles (writerdeck, pentest, etc.)
/power — UPS HAT power management &amp; runtime estimation
/osconf — OS configurator with post-install scripts
/builddoc — Build documentation generator
/sdr — SDR integration &amp; radio frequency bands
/explore — Community build explorer
/aesthetic — Aesthetic style engine with 14 themes

<b>v7.1 New Features:</b>
/localai — Offline LLM deck tuner (boards, models, NPU warning)
/hotswap — Battery hot-swap &amp; supercap UPS design
/ortho — Ortholinear &amp; split keyboard DB (Corne, Lily58, Ferris...)
/offgridstack — Offline survival stack (DTN, Kiwix RAG, maps, P2P)
/features — Community feature board (voted mods from cyberdeck.ing)
/character — Maximalist vs minimalist build character generator
/scavenge — Thrift/e-waste scavenger hunt build planner
/newhardware — 2026 hardware radar (Pi 500+, Rock 5B 32GB, AI HAT+)""")

    elif cmd == "/status":
        n_comp = len(cd_classes.get("ComponentDatabase", {}).get_all_sbcs()) if "ComponentDatabase" in cd_classes else 0
        bname = _user_brain.get(str(uid), "default")
        await send(chat, f"""<b>CyberdeckBot {BOT_VERSION}</b>
Provider: {_get_provider_for(uid)}
Airgap: {"ON (local only)" if _offline_mode else "OFF"}
Local model: {androidllm_models.active_model() or "none"}
Brain: {bname}{"  (coding mode ON)" if _coder_mode.get(str(uid)) else ""}
Providers: {len(PROVIDERS)}
Components loaded: {n_comp}
Uptime: {time.strftime('%H:%M:%S')}""")

    elif cmd == "/provider":
        a = args.strip()
        if not a:
            lines = ["<b>Providers:</b>", ""]
            routers = [n for n in PROVIDERS if "localhost" in PROVIDERS[n]["url"] or "127.0.0.1" in PROVIDERS[n]["url"]]
            for name, p in PROVIDERS.items():
                marker = " << active" if _get_provider_for(uid) == name else ""
                tag = " [router]" if name in routers else ""
                lines.append(f"  <b>{name}</b>{tag}{marker}: {p['model']}")
            lines.append("")
            lines.append("Usage: /provider &lt;name&gt; | /provider routers | /provider test &lt;name&gt;")
            await send(chat, "\n".join(lines))
        elif a == "routers":
            lines = ["<b>Local Router Providers:</b>", ""]
            for name in ROUTER_CHAIN:
                if name in PROVIDERS:
                    marker = " << active" if _get_provider_for(uid) == name else ""
                    lines.append(f"  <b>{name}</b>{marker}: {PROVIDERS[name]['url']}")
            lines.append("")
            lines.append("Switch: /provider 9router | /provider vansrouter | /provider bitrouter | /provider androidllm")
            await send(chat, "\n".join(lines))
        elif a.startswith("test "):
            tname = a.split(maxsplit=1)[1]
            if tname not in PROVIDERS:
                await send(chat, f"Unknown provider: <b>{tname}</b>")
            else:
                await send(chat, f"Testing <b>{tname}</b> ({PROVIDERS[tname]['url']})...")
                r = await call_ai([{"role": "user", "content": "Reply with exactly: PONG"}], provider_name=tname)
                ok = "PONG" in r or ("OK" in r and "error" not in r.lower())
                await send(chat, f"<b>{tname}</b>: {'<code>OK</code>' if ok else '<code>FAIL</code>'}\n{r[:300]}")
        elif a in PROVIDERS:
            _user_provider[str(uid)] = a
            log(f"User {uid} switched provider to {a}", "provider")
            await send(chat, f"Switched to <b>{a}</b> ({PROVIDERS[a]['model']})")
        else:
            await send(chat, f"Unknown provider: <b>{a}</b>\nAvailable: {', '.join(PROVIDERS.keys())}")

    elif cmd == "/providers":
        lines = []
        for name, p in PROVIDERS.items():
            marker = " << active" if _get_provider_for(uid) == name else ""
            lines.append(f"  <b>{name}</b>{marker}: {p['model']}")
        await send(chat, "<b>Providers:</b>\n" + "\n".join(lines))

    elif cmd == "/model":
        a = args.strip()
        if not a:
            lines = ["<b>Local androidllm models (one at a time):</b>", ""]
            active = androidllm_models.active_model()
            for m in androidllm_models.RECOMMENDED:
                sharded = androidllm_models.is_sharded(m["id"])
                marker = " << serving" if m["id"] == active else ""
                st = "sharded" if sharded else "not sharded"
                lines.append(f"  <b>{m['id']}</b>{marker}: {m['disk_gb']} GB ({st}) — {m['note']}")
            lines.append("")
            lines.append("Usage: /model &lt;id&gt;  (un-sharded picks auto-download + shard)")
            await send(chat, "\n".join(lines))
        elif a in androidllm_models.recommended_ids():
            m = next(x for x in androidllm_models.RECOMMENDED if x["id"] == a)
            if androidllm_models.is_sharded(a):
                _switch_local_model(a)
                await send(chat, f"Switched local model to <b>{a}</b>. androidllm-serve restarting...")
            else:
                await send(chat, f"<b>{a}</b> is not sharded yet — auto-sharding in the background.\n"
                                 f"Manual alternative:\n<code>bash ~/androidllm/scripts/setup_termux.sh {m['repo']} {a}</code>")
                asyncio.create_task(_shard_and_switch(chat, m))
        else:
            await send(chat, f"Unknown model: <b>{a}</b>. "
                             f"Available: {', '.join(androidllm_models.recommended_ids())}")

    elif cmd == "/offline":
        a = args.strip().lower()
        if a in ("on", "1", "yes", "true"):
            _offline_mode = True
            _save_offline_mode()
            await send(chat, "<b>Airgap mode ON.</b> All AI replies now route through the "
                             "local androidllm model on this phone ($0.00). Cloud providers blocked.")
        elif a in ("off", "0", "no", "false"):
            _offline_mode = False
            _save_offline_mode()
            await send(chat, "Airgap mode OFF. Normal routing restored (cloud allowed).")
        else:
            st = "ON (all AI is local)" if _offline_mode else "OFF (cloud allowed)"
            local = androidllm_models.active_model() or "none"
            await send(chat, f"<b>Airgap mode: {st}</b>\nLocal model: {local}\n\n"
                             f"Usage: /offline on | /offline off\n\n"
                             f"When ON, every message and /code request runs on the local "
                             f"androidllm model — $0.00, works with no internet.")

    elif cmd == "/qa":
        a = args.strip().lower()
        if a in ("on", "1", "yes", "true"):
            _qa_users[str(uid)] = True
            _save_qa_mode()
            await send(chat, "<b>Q&A mode ON.</b> Every message is answered from the local "
                             "knowledge base (SBC, battery, display, keyboard, LoRa, wiring...) "
                             "with cited sources — $0.00 via androidllm. /qa off to exit.")
        elif a in ("off", "0", "no", "false"):
            _qa_users[str(uid)] = False
            _save_qa_mode()
            await send(chat, "Q&A mode OFF. Normal chat restored.")
        else:
            st = "ON" if _qa_users.get(str(uid)) else "OFF"
            kb_n = len(_rag_kb)
            await send(chat, f"<b>Q&A mode: {st}</b> (KB: {kb_n} topics)\n\n"
                             f"Usage: /qa on | /qa off\n\n"
                             f"When ON, questions are answered from the local knowledge base "
                             f"with sources cited, served by the on-phone androidllm model "
                             f"($0.00). No knowledge match → answers from local parts database.")

    elif cmd in ("/brain", "/brains"):
        bname = args.strip().lower()
        if cmd == "/brains" or not bname:
            lines = ["<b>Available Brains:</b>", ""]
            for k, v in BRAINS.items():
                marker = " << active" if _user_brain.get(str(uid), "default") == k else ""
                mem = " (memory)" if v.get("memory") else ""
                lines.append(f"  <b>{k}</b>{mem}{marker}: {v['desc']}")
            lines.append("")
            lines.append("Usage: /brain &lt;name&gt;")
            await send(chat, "\n".join(lines))
        elif bname in BRAINS:
            _user_brain[str(uid)] = bname
            _brain_memory_cache["ts"] = 0
            if str(uid) in _sessions and _sessions[str(uid)] and _sessions[str(uid)][0].get("role") == "system":
                _sessions[str(uid)][0]["content"] = _brain_system(uid)
            log(f"User {uid} switched brain to {bname}", "brain")
            await send(chat, f"Brain switched to <b>{bname}</b>: {BRAINS[bname]['desc']}")
        else:
            await send(chat, f"Unknown brain: <b>{bname}</b>\nAvailable: {', '.join(BRAINS.keys())}")

    elif cmd == "/coder":
        mode = args.strip().lower()
        if mode in ("on", "1", "yes", "true"):
            _coder_mode[str(uid)] = True
            _user_brain[str(uid)] = "coding"
            if str(chat) in _sessions and _sessions[str(chat)]:
                _sessions[str(chat)][0] = {"role": "system", "content": CODER_SYSTEM}
            await send(chat, "🧠 <b>Coding mode ON.</b> All messages route through the unified coding brain — "
                             "smartest free/paid model first, auto-fallback down the chain. /coder off to exit.")
        elif mode in ("off", "0", "no", "false"):
            _coder_mode[str(uid)] = False
            _user_brain[str(uid)] = "default"
            if str(chat) in _sessions and _sessions[str(chat)]:
                _sessions[str(chat)][0] = {"role": "system", "content": _brain_system(uid)}
            await send(chat, "Coding mode OFF. Back to the cyberdeck brain.")
        else:
            state = "ON" if _coder_mode.get(str(uid)) else "OFF"
            chain = ", ".join(_coding_chain()) or "none"
            await send(chat, f"🧠 <b>Coding mode: {state}</b>\n\nChain: {chain}\n\n"
                             f"Commands:\n/coder on|off — toggle\n/code &lt;task&gt; — one-shot (auto-fallback)\n"
                             f"/codeall &lt;task&gt; — compare top 3 models in parallel")

    elif cmd == "/code":
        await handle_code(chat, args)

    elif cmd == "/codeall":
        await handle_codeall(chat, args)

    elif cmd == "/v1":
        await send(chat, "Switched to General AI mode (opencode-bot).\n\nAll general AI commands available.\nSwitch back: /v2")

    elif cmd == "/categories":
        cats = ["coding", "writerdeck", "security", "gaming", "research", "ai",
                "survival", "media", "conversation-piece", "drone", "forensics",
                "test-equipment", "weather", "home-automation", "edge-ai"]
        await send(chat, "<b>Build Categories:</b>\n" + "\n".join(f"  • {c}" for c in cats))

    elif cmd == "/tiers":
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import TIERS
            lines = []
            for tid, t in TIERS.items():
                lines.append(f"<b>{t['name']}</b>\n  Budget: {t['budget']} | Soldering: {t['soldering']}\n  Skills: {t['skills']}")
            await send(chat, "\n\n".join(lines))
        else:
            await send(chat, "Cyberdeck agent not loaded")

    elif cmd == "/styles":
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import STYLE_PRESETS
            lines = []
            for sid, s in STYLE_PRESETS.items():
                lines.append(f"<b>{s['name']}</b>: {s['description']}")
            await send(chat, "<b>3D Model Styles:</b>\n\n" + "\n\n".join(lines))
        else:
            await send(chat, "Cyberdeck agent not loaded")

    elif cmd == "/list":
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import ComponentDatabase
            sbcs = ComponentDatabase.get_all_sbcs()
            displays = ComponentDatabase.get_all_displays()
            kbs = ComponentDatabase.get_all_keyboards()
            power = ComponentDatabase.get_all_power()
            cool = ComponentDatabase.get_all_cooling()
            await send(chat, f"""<b>Component Database:</b>
SBCs: {len(sbcs)}
Displays: {len(displays)}
Keyboards: {len(kbs)}
Power: {len(power)}
Cooling: {len(cool)}
Total: {len(sbcs)+len(displays)+len(kbs)+len(power)+len(cool)}""")

    elif cmd in ("/build", "/cyberdeck"):
        await handle_build(chat, uid, args)

    elif cmd == "/bom":
        await handle_bom(chat, uid, args)

    elif cmd == "/compat":
        await handle_compat(chat, uid, args)

    elif cmd == "/tutorial":
        await handle_tutorial(chat, uid, args)

    elif cmd == "/ideas":
        await handle_ideas(chat, uid, args)

    elif cmd in ("/ideasearch", "/isearch"):
        await handle_ideasearch(chat, uid, args)

    elif cmd == "/search":
        await handle_search(chat, uid, args)

    elif cmd == "/3d":
        await handle_3d(chat, uid, args)

    elif cmd == "/pcb":
        await handle_pcb(chat, uid, args)

    elif cmd == "/cables":
        await handle_cables(chat, uid, args)

    elif cmd == "/flaws":
        await handle_flaws(chat, uid, args)

    elif cmd == "/pack":
        await handle_pack(chat, uid, args)

    elif cmd == "/career":
        await handle_career(chat, uid, args)

    elif cmd == "/dashboard":
        await handle_dashboard(chat, uid, args)

    elif cmd == "/specs":
        await handle_specs(chat, uid, args)

    elif cmd == "/cb":
        await handle_custom_build(chat, uid, args)

    elif cmd == "/peripherals":
        await handle_peripherals(chat, uid, args)

    elif cmd == "/antenna":
        await handle_antenna(chat, uid, args)

    elif cmd == "/battery":
        await handle_battery(chat, uid, args)

    elif cmd == "/forensics":
        await handle_forensics(chat, uid, args)

    elif cmd == "/testeq":
        await handle_testeq(chat, uid, args)

    elif cmd == "/hamradio":
        await handle_hamradio(chat, uid, args)

    elif cmd == "/palette":
        await handle_palette(chat, uid, args)

    elif cmd == "/material":
        await handle_material(chat, uid, args)

    elif cmd == "/v2":
        await send(chat, "Switched to Cyberdeck Builder mode (cyberdeck-bot).\n\nAll cyberdeck commands available.\nType /start for command list.\nSwitch back: /v1")

    elif cmd == "/9router":
        await send(chat, "<b>9Router</b> — Universal AI Gateway\nInstall: npm install -g 9router\nEndpoint: http://localhost:20128/v1\nGitHub: https://github.com/decolua/9router\nSmart 3-tier fallback: subscription → cheap → free\nRTK+Caveman token compression (20-65%)\n60+ AI providers, 10+ CLI tools")

    elif cmd == "/vansrouter":
        await send(chat, "<b>VansRouter</b> — Local 9Router fork (port 3003)\nDashboard: http://localhost:3003\nDev: http://localhost:20127/v1\nProd: http://localhost:3003/api/v1\nProvider: vansrouter (port 3003, auto model)\nCustom server with IP spoofing protection\nCLI: vansrouter/cli/cli.js")

    elif cmd == "/omniroute":
        op = PROVIDERS.get("omniroute", {})
        await send(chat, f"<b>OmniRoute</b> — 290+ provider AI gateway\nFork of 9Router\n{op.get('url', 'http://localhost:20128/v1/chat/completions')}\nModel: {op.get('model', 'auto')}\n17 routing strategies, RTK+Caveman (15-95% savings)\nMCP server (95+ tools), A2A agent protocol\nDesktop (Electron), PWA, Termux\nSet OMNIROUTE_URL/MODEL/KEY in setenv.sh")

    elif cmd == "/openclaw":
        await send(chat, "<b>OpenClaw</b> — AI Multi-Tool Orchestration CLI\nInstall: npm install -g clawhub\nConfig: ~/.openclaw/openclaw.json\nDocs: https://docs.openclaw.ai\nSkills: clawhub install <skill>\nMCP: x64dbg, Ghidra, dnSpy, radare2, Frida\nReverse engineering, coding, forensics\nRoute via VansRouter: baseUrl=http://localhost:20128/v1")

    elif cmd == "/blackbox":
        bp = PROVIDERS.get("blackbox", {})
        await send(chat, f"<b>Blackbox AI</b> — Multi-model provider\nProvider: {'configured' if 'BLACKBOX_KEY' in os.environ and os.environ.get('BLACKBOX_KEY') != 'set-via-env-var' else 'NOT configured'}\nURL: https://api.blackbox.ai/v1/chat/completions\nModels: claude-fable-5, claude-opus-4.8, claude-sonnet-4.6\ngpt-5.5, gpt-5.4-pro, gpt-5.4, gpt-5.3-codex, gpt-5.4-nano\ndeepseek-v4-flash, grok-4.3\nAPI keys: https://www.blackbox.ai/api-management\nSet BLACKBOX_KEY in setenv.sh")

    elif cmd == "/odysseus":
        await send(chat, "<b>Odysseus</b> — Self-Hosted AI Workspace\nRun local LLMs + autonomous agents locally\n270+ model catalog, hardware-aware recommendations\nBuilt-in tools: bash, files, web, memory\nMCP-compatible multi-machine serving\nPersistent memory, skill authoring, IMAP/SMTP\nResearch workflows with cited report generation\nPrivate by default — bring your own endpoints")

    elif cmd == "/hermes":
        await send(chat, "<b>Hermes Agent</b> — Self-Improving AI by Nous Research\nGitHub: https://github.com/NousResearch/hermes-agent (200K+ stars)\nInstall: curl -fsSL raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash\nConfig: ~/.hermes/.env\nSelf-improving learning loop — creates skills from experience\nPersistent cross-session memory (SQLite + FTS5)\nMulti-platform: Telegram, Discord, Slack, WhatsApp, Signal, CLI\n40+ tools, cron automations, subagent delegation\n200+ models via OpenRouter, runs on $5 VPS\nRoute via VansRouter: OPENAI_BASE_URL=http://localhost:20128/v1")

    elif cmd == "/obsidian":
        await send(chat, "<b>Obsidian AI</b> — Knowledge Base + AI Agent Integration\nOfficial CLI (v1.12+): obsidian search/daily/open/vault/note\nEnable: Settings > General > Command line interface\nMCP: obsidian-mcp-server (STDIO), mcp-obsidian (REST API)\nPlugins: Obsidian AI CLI, Agentic Copilot, Smart Connections v4\n100+ commands for vault automation, scripting, cron\nDocs: https://obsidian.md/cli")

    elif cmd == "/solder":
        await handle_solder(chat, uid, args)

    elif cmd == "/hardware":
        await handle_hardware(chat, uid, args)

    elif cmd == "/modules":
        await handle_modules(chat, uid, args)

    elif cmd == "/lilpcb":
        await handle_lilpcb(chat, uid, args)

    elif cmd == "/bomcsv":
        await handle_bomcsv(chat, uid, args)

    elif cmd == "/timeline":
        await handle_timeline(chat, uid, args)

    elif cmd == "/changelog":
        await handle_changelog(chat, uid, args)

    elif cmd == "/dashboard_render":
        await handle_dashboard_render(chat, uid, args)

    elif cmd == "/idbuild":
        await handle_idbuild(chat, uid, args)

    elif cmd == "/isa":
        await handle_isa(chat, uid, args)

    elif cmd == "/bruce":
        await handle_bruce(chat, uid, args)

    elif cmd == "/gr3ml1n":
        await handle_gr3ml1n(chat, uid, args)

    elif cmd == "/homebrew_os":
        await handle_homebrew_os(chat, uid, args)

    elif cmd == "/edgeai":
        await handle_edgeai(chat, uid, args)

    elif cmd == "/espnow":
        await handle_espnow(chat, uid, args)

    elif cmd == "/wifi_scan":
        await handle_wifi_scan(chat, uid, args)

    elif cmd == "/ollama":
        await handle_ollama(chat, uid, args)

    elif cmd == "/kiwix":
        await handle_kiwix(chat, uid, args)

    elif cmd == "/enclosure":
        await handle_enclosure(chat, uid, args)

    elif cmd == "/mesh":
        await handle_mesh(chat, uid, args)

    elif cmd == "/bomtrack":
        await handle_bomtrack(chat, uid, args)

    elif cmd == "/profile":
        await handle_profile(chat, uid, args)

    elif cmd == "/power":
        await handle_power(chat, uid, args)

    elif cmd == "/osconf":
        await handle_osconf(chat, uid, args)

    elif cmd == "/builddoc":
        await handle_builddoc(chat, uid, args)

    elif cmd == "/sdr":
        await handle_sdr(chat, uid, args)

    elif cmd == "/explore":
        await handle_explore(chat, uid, args)

    elif cmd == "/aesthetic":
        await handle_aesthetic(chat, uid, args)

    elif cmd == "/writerdeck":
        await handle_writerdeck(chat, uid, args)

    elif cmd == "/thermal":
        await handle_thermal(chat, uid, args)

    elif cmd == "/compare":
        await handle_compare(chat, uid, args)

    elif cmd == "/cost":
        await handle_cost(chat, uid, args)

    elif cmd == "/upgrade":
        await handle_upgrade(chat, uid, args)

    elif cmd == "/solar":
        await handle_solar(chat, uid, args)

    elif cmd == "/wizard":
        await handle_wizard(chat, uid, args)

    elif cmd == "/share":
        await handle_share(chat, uid, args)

    elif cmd == "/localai":
        await handle_localai(chat, uid, args)

    elif cmd == "/hotswap":
        await handle_hotswap(chat, uid, args)

    elif cmd == "/ortho":
        await handle_ortho(chat, uid, args)

    elif cmd == "/offgridstack":
        await handle_offgridstack(chat, uid, args)

    elif cmd == "/features":
        await handle_features(chat, uid, args)

    elif cmd == "/character":
        await handle_character(chat, uid, args)

    elif cmd == "/scavenge":
        await handle_scavenge(chat, uid, args)

    elif cmd == "/newhardware":
        await handle_newhardware(chat, uid, args)

    elif cmd == "/sysinfo":
        await handle_sysinfo(chat, uid, args)

    elif cmd == "/top":
        await handle_top(chat, uid, args)

    elif cmd == "/wifi":
        await handle_wifi(chat, uid, args)

    elif cmd == "/stop":
        t = _active_tasks.get(str(chat))
        if t and not t.done():
            t.cancel()
            await send(chat, "Stopped.")
        else:
            await send(chat, "Nothing running to stop.")

    elif cmd == "/survival":
        await handle_survival(chat, uid, args)

    elif cmd == "/morse":
        await handle_morse(chat, uid, args)

    elif cmd == "/convert":
        await handle_convert(chat, uid, args)

    elif cmd == "/solarcalc":
        await handle_solarcalc(chat, uid, args)

    elif cmd == "/help":
        await handle_command(chat, uid, "/start", msg)

    else:
        await send(chat, f"Unknown command: {cmd}\nType /help for commands")

# ============================================================
# Cyberdeck Feature Handlers
# ============================================================
async def handle_build(chat, uid, args):
    if not args:
        await send(chat, "Usage: /cyberdeck &lt;description&gt;\nExample: /cyberdeck portable hacking rig with 7\" screen and mechanical keyboard")
        return
    await typing(chat)
    try:
        if "BuildGenerator" in cd_classes:
            gen = cd_classes["BuildGenerator"]
            build = gen.build_from_prompt(args)
            if build:
                lines = [f"<b>Build: {build.get('name', args[:40])}</b>\n"]
                lines.append(f"Category: {build.get('category', 'custom')} | Tier: {build.get('tier', 'intermediate')}")
                lines.append(f"Est. Budget: {build.get('budget', 'unknown')}\n")
                components = build.get("components", {})
                for cat, comp in components.items():
                    if isinstance(comp, dict):
                        lines.append(f"<b>{cat.upper()}: {comp.get('name', '?')}</b> — ${comp.get('price', '?')}")
                    elif isinstance(comp, str):
                        lines.append(f"<b>{cat.upper()}:</b> {comp}")
                compat = build.get("compatibility_notes", "")
                if compat:
                    lines.append(f"\n<b>Compatibility:</b> {compat}")
                await send(chat, "\n".join(lines))
                return
        # Fallback: use AI
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Build a cyberdeck: {args}. Provide components list with prices, compatibility notes, and assembly tips."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        _sessions[str(uid)].append({"role": "assistant", "content": reply})
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Build error: {e}")
        log(f"Build error: {e}")

async def handle_bom(chat, uid, args):
    if not args:
        await send(chat, "Usage: /bom &lt;build description&gt;")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a Bill of Materials (BOM) for: {args}. List every component with: name, model, price, quantity, source (Amazon/Adafruit/etc), and notes."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        _sessions[str(uid)].append({"role": "assistant", "content": reply})
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"BOM error: {e}")

async def handle_compat(chat, uid, args):
    if not args:
        await send(chat, "Usage: /compat &lt;sbc_id&gt; &lt;display_id&gt;\nExample: /compat rpi5 hdmi7")
        return
    await typing(chat)
    try:
        parts = args.split()
        if len(parts) >= 2 and "CompatibilityEngine" in cd_classes:
            engine = cd_classes["CompatibilityEngine"]
            result = engine.check_sbc_display(parts[0], parts[1])
            if result:
                issues = result.get("issues", [])
                fixed = result.get("fixed", [])
                lines = [f"<b>Compatibility: {parts[0]} ↔ {parts[1]}</b>"]
                if not issues:
                    lines.append("✅ Fully compatible!")
                else:
                    for issue in issues:
                        lines.append(f"⚠️ {issue}")
                if fixed:
                    lines.append(f"\n🔧 Auto-fixed: {', '.join(fixed)}")
                await send(chat, "\n".join(lines))
                return
        # Fallback
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Check compatibility between: {args}. Report issues and fixes."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Compat error: {e}")

async def handle_tutorial(chat, uid, args):
    if not args:
        await send(chat, "Usage: /tutorial &lt;build description&gt;")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a word-by-word assembly tutorial for: {args}. Include: tools needed, step-by-step instructions, risks per step, tips, estimated time per step."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        _sessions[str(uid)].append({"role": "assistant", "content": reply})
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Tutorial error: {e}")

async def handle_upgrade(chat, uid, args):
    if not args:
        await send(chat, "Usage: /upgrade &lt;current build description&gt;")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Suggest upgrades for this cyberdeck build: {args}. List upgrade paths with cost, performance gain, and difficulty."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Upgrade error: {e}")

async def handle_ideas(chat, uid, args):
    await typing(chat)
    try:
        cat_filter = args.lower().strip() if args else None
        if "IdeaGenerator" in cd_classes:
            ideas = cd_classes["IdeaGenerator"].generate(category=cat_filter)
            if ideas:
                lines = [f"<b>Cyberdeck Ideas{f' ({cat_filter})' if cat_filter else ''}:</b>\n"]
                for i, idea in enumerate(ideas[:8], 1):
                    if isinstance(idea, dict):
                        t = idea.get('title', idea.get('name', 'Idea'))
                        d = idea.get('description', '')
                        c = idea.get('estimated_cost', idea.get('budget', '?'))
                        cat = idea.get('category', '?')
                        diff = idea.get('difficulty', '?')
                        pp = idea.get('post_processing', '')
                        mat = idea.get('material', '')
                        pp_str = f" [{pp}]" if pp else ""
                        mat_str = f" [{mat}]" if mat else ""
                        lines.append(f"<b>{i}. {t}</b> {mat_str}{pp_str}")
                        lines.append(f"  {d}")
                        lines.append(f"  💰 {c} | 🏷 {cat} | 🔧 {diff}\n")
                    else:
                        lines.append(f"{i}. {idea}\n")
                total = len(ideas)
                lines.append(f"<i>Showing {min(8, total)} of {total} ideas. Filter: /ideas &lt;category&gt;</i>")
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate 5 creative cyberdeck build ideas{' in category: ' + args if args else ''}. For each: name, description, key components, estimated budget, difficulty."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Ideas error: {e}")

async def handle_ideasearch(chat, uid, args):
    """Free-text idea search over IdeaGenerator.BASE_IDEAS — local, instant,
    offline-safe. Supports 'budget $X' and 'skill <level>' filters."""
    await typing(chat)
    try:
        if "IdeaGenerator" not in cd_classes:
            await send(chat, "IdeaGenerator not loaded")
            return
        parts = args.strip().split()
        if not parts:
            await send(chat, "Usage: /ideasearch &lt;keywords&gt; [budget $X] [skill level]\n"
                             "Example: /ideasearch e-ink writer under $400\n"
                             "Example: /ideasearch lora mesh skill advanced")
            return
        budget = None
        skill = None
        query = []
        i = 0
        while i < len(parts):
            p = parts[i].lower()
            if p in ("budget", "under", "max") and i + 1 < len(parts):
                b = re.sub(r"[^\d.]", "", parts[i + 1])
                if b:
                    budget = float(b)
                i += 2
                continue
            if p in ("skill", "level", "difficulty") and i + 1 < len(parts):
                s = parts[i + 1].lower()
                if s in ("beginner", "intermediate", "advanced", "expert"):
                    skill = s
                i += 2
                continue
            query.append(parts[i])
            i += 1
        q = " ".join(query).strip()
        if not q:
            await send(chat, "Usage: /ideasearch &lt;keywords&gt; [budget $X] [skill level]")
            return
        ideas = cd_classes["IdeaGenerator"].search(q, budget=budget, skill=skill)
        if not ideas:
            await send(chat, f"No ideas match <b>{q}</b>"
                             f"{' under $%.0f' % budget if budget else ''}"
                             f"{' (skill %s)' % skill if skill else ''}. "
                             f"Try broader keywords.")
            return
        head = f"<b>Idea search: {q}</b>"
        if budget:
            head += f" <i>(max $%.0f)</i>" % budget
        if skill:
            head += f" <i>({skill})</i>"
        lines = [head, ""]
        for i, idea in enumerate(ideas, 1):
            t = idea.get("title", "Idea")
            d = idea.get("description", "")
            c = idea.get("estimated_cost", "?")
            cat = idea.get("category", "?")
            diff = idea.get("difficulty", "?")
            lines.append(f"<b>{i}. {t}</b>")
            lines.append(f"  {d}")
            lines.append(f"  {c} | {cat} | {diff}\n")
        lines.append("<i>Filters: budget $X | skill beginner|intermediate|advanced|expert</i>")
        await send(chat, "\n".join(lines))
    except Exception as e:
        await send(chat, f"Idea search error: {e}")

async def handle_search(chat, uid, args):
    if not args:
        await send(chat, "Usage: /search &lt;query&gt; [budget $X] [category &lt;type&gt;] [sort price]\nCategories: sbc, display, keyboard, power, enclosure, cooling, pcb, wire, connectivity, storage, sensor, camera, sdr, lora, nfc, fingerprint, haptic, imu\nExample: /search pi 5 budget $100 sort price")
        return
    await typing(chat)
    try:
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import ComponentDatabase
            budget = None
            category = None
            sort = "relevance"
            keywords = []
            pending = None
            for a in args.split():
                if pending:
                    if pending == "budget":
                        m = re.match(r"^\$?(\d+)$", a)
                        if m:
                            budget = int(m.group(1))
                    elif pending == "sort":
                        if a.lower() in ("relevance", "price"):
                            sort = a.lower()
                    else:
                        category = a
                    pending = None
                    continue
                if a.lower() in ("budget", "under", "max"):
                    pending = "budget"
                    continue
                if a.lower() == "sort":
                    pending = "sort"
                    continue
                if a.lower() == "category":
                    pending = "category"
                    continue
                m = re.match(r"^\$?(\d+)$", a)
                if m and budget is None:
                    budget = int(m.group(1))
                    continue
                keywords.append(a)
            q = " ".join(keywords) or args
            results = ComponentDatabase.search(q, budget=budget, category=category, sort=sort, limit=10)
            if results:
                head = f"<b>Search: {q}</b>"
                if budget:
                    head += f" <i>(max ${budget})</i>"
                if category:
                    head += f" <i>({category})</i>"
                if sort == "price":
                    head += " <i>(cheapest first)</i>"
                head += f" — {len(results)} results"
                lines = [head, ""]
                for i, r in enumerate(results, 1):
                    p = f"${r.get('price')}" if r.get("price") is not None else "price ?"
                    lines.append(f"<b>{i}. {r.get('name', '?')}</b> [{r.get('type', '?')}] {p}")
                    if r.get("spec_line"):
                        lines.append(f"   {r['spec_line']}")
                    if r.get("vendor"):
                        lines.append(f"   Buy: <i>{r['vendor']}</i> ${r['vendor_price']} → {r['vendor_url']}")
                    lines.append("")
                lines.append("<i>Filters: budget $X | category &lt;type&gt; | sort price</i>")
                await send(chat, "\n".join(lines))
                return
            await send(chat, f"No local matches for '<b>{q}</b>'. Try fewer keywords or drop the budget/category filter — falling back to AI...")
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Search for cyberdeck components: {args}. List matching components with prices and where to buy."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Search error: {e}")

# ============================================================
# Deck system commands — /sysinfo /top /wifi (deck phone)
# ============================================================
def _read_proc(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except Exception:
        return None


async def handle_sysinfo(chat, uid, args):
    await typing(chat)
    try:
        lines = ["<b>Deck System Info</b>"]
        try:
            import platform
            lines.append(f"Platform: {platform.system()} {platform.release()}")
            lines.append(f"Machine: {platform.machine()}")
        except Exception:
            pass
        mem = _read_proc("/proc/meminfo") or ""
        mem_total = mem_avail = 0
        for ln in mem.splitlines():
            if ln.startswith("MemTotal:"):
                mem_total = int(ln.split()[1]) // 1024
            elif ln.startswith("MemAvailable:"):
                mem_avail = int(ln.split()[1]) // 1024
        if mem_total:
            lines.append(f"RAM: {mem_total - mem_avail}MB / {mem_total}MB used ({mem_avail}MB free)")
        load = _read_proc("/proc/loadavg")
        if load:
            lines.append("Load: " + " ".join(load.split()[:3]))
        cpu = _read_proc("/proc/cpuinfo") or ""
        if cpu:
            cores = cpu.count("processor")
            model = ""
            for ln in cpu.splitlines():
                if ln.startswith(("Hardware", "model name")):
                    model = ln.split(":", 1)[1].strip()
                    break
            lines.append(f"CPU: {cores} core{'' if cores == 1 else 's'} {model}".rstrip())
        try:
            import glob
            temp = None
            for zone in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
                t = _read_proc(zone)
                if t:
                    temp = int(t) // 1000
                    break
            if temp is not None:
                lines.append(f"Temp: {temp}C")
        except Exception:
            pass
        try:
            import os
            v = os.statvfs("/")
            lines.append(f"Disk: {v.f_bavail * v.f_frsize / 1e9:.1f}GB / {v.f_blocks * v.f_frsize / 1e9:.1f}GB free")
        except Exception:
            pass
        try:
            out = subprocess.check_output(["termux-battery-status"], timeout=5,
                                          stderr=subprocess.DEVNULL)
            bat = json.loads(out.decode())
            lines.append(f"Battery: {bat.get('percentage')}% ({bat.get('status')}, {bat.get('temperature', 0) / 10}C)")
        except Exception:
            pass
        await send(chat, "\n".join(lines))
    except Exception as e:
        await send(chat, f"System info error: {e}")


async def handle_top(chat, uid, args):
    await typing(chat)
    try:
        out = subprocess.check_output(
            ["ps", "-Ao", "pid,comm,%cpu,%mem", "--sort=-%cpu"],
            timeout=5, stderr=subprocess.DEVNULL).decode(errors="replace")
        rows = out.strip().splitlines()
        if not rows:
            await send(chat, "No process list available on this platform.")
            return
        head = rows[:1]
        body = rows[1:13]
        await send(chat, f"<b>Top processes ({len(rows) - 1} total)</b>\n"
                         f"<code>{chr(10).join(head + body)}</code>\n"
                         f"<i>PID | COMM | CPU% | MEM%</i>")
    except Exception as e:
        await send(chat, f"Process list error: {e}")


async def handle_wifi(chat, uid, args):
    await typing(chat)
    try:
        try:
            out = subprocess.check_output(["termux-wifi-connectioninfo"], timeout=5,
                                          stderr=subprocess.DEVNULL)
            d = json.loads(out.decode())
            ssid = d.get("ssid") or "unknown"
            lines = [f"<b>WiFi: {ssid}</b>"]
            if d.get("rssi") is not None:
                lines.append(f"Signal: {d['rssi']} dBm")
            if d.get("frequency"):
                lines.append(f"Freq: {d['frequency']} MHz")
            if d.get("ip"):
                lines.append(f"IP: {d['ip']}")
            await send(chat, "\n".join(lines))
            return
        except Exception:
            pass
        w = _read_proc("/proc/net/wireless")
        if w and len(w.splitlines()) > 2:
            await send(chat, "<b>WiFi interfaces</b>\n<code>" + w + "</code>")
            return
        await send(chat, "WiFi info unavailable.\nInstall Termux:API:\n<code>pkg install termux-api</code>")
    except Exception as e:
        await send(chat, f"WiFi error: {e}")


# ============================================================
# Offline survival, morse, unit conversion, solar sizing
# ============================================================
SURVIVAL_GUIDES = {
    "water": [
        "Find water: look for vegetation, animal tracks, valleys and drainage lines.",
        "Purify: boil 1 min (3 min above 2000m), or chemical tabs, or filter (0.2um).",
        "Collect: solar still, dew traps, tarp rain catch, or wrap a tree branch with cloth overnight.",
        "NEVER drink seawater, urine, or stagnant water untreated.",
        "Target: 2-3L per day; ration by activity, not by thirst.",
    ],
    "fire": [
        "Prep three stages: tinder (dry grass, bark shavings), kindling (pencil-thick), fuel (thumb-thick).",
        "Shelter the fire from wind; build on dry ground or a rock plate.",
        "Methods: ferro rod (best), bow drill, battery + steel wool, magnifying glass in sun.",
        "Signal use: add green leaves for white smoke, keep fire 24h if lost.",
        "Extinguish fully before moving: water + dirt, until ashes are cold.",
    ],
    "shelter": [
        "Priority: protect from wind, rain, and ground cold (insulation under you first).",
        "Debris hut: ridgepole + A-frame of branches, 30cm of leaf/dry-debris wall.",
        "Tarp setup: ridgeline between two trees, stake corners, dig a drainage channel.",
        "In cold: build small shelters — body heat keeps a small space warm.",
        "Never camp under dead branches, rock faces, or dry river beds (flash floods).",
    ],
    "first-aid": [
        "Bleeding: direct pressure 10 min, then bandage; elevate; no tourniquet unless arterial.",
        "Burns: cool with running water 10-20 min; cover with clean dry cloth; no ice directly.",
        "Fracture: splint the joint above and below the break with rigid material + padding.",
        "Heat stroke: move to shade, remove clothing, cool with wet cloths, hydrate slowly.",
        "Hypothermia: get dry, add layers, warm core first (chest/neck/groin), warm sweet drinks.",
        "Deck kit: bandage, gauze, tape, antiseptic, ibuprofen, antihistamine, blister pads, scissors.",
    ],
    "navigation": [
        "Day: shadow-stick method — mark shadow tip, wait 15 min, second mark = east-west line.",
        "Night: Southern Cross / Big Dipper pointers for direction; moon crescent trick.",
        "Landmarks: pick 2-3 ahead, walk to them, never dead-reckon in featureless terrain.",
        "Altimeter apps or GPS only if charged — carry a paper map + compass backup.",
        "Route planning: follow ridges down, not valleys (easier walking, better views, safer).",
    ],
    "signal": [
        "Whistle: 3 blasts = distress; mirror flashes sweep the horizon; signal fire 3 fires in triangle.",
        "Ground signals: giant letters with branches/rocks — V = need assistance, X = need medical.",
        "By radio: repeat your callsign/position on 3-5 min cycles; use emergency bands 121.5/243.0 MHz.",
        "At night: flashlight SOS (3 short, 3 long, 3 short) or strobe if available.",
        "Your deck: SDR can find signals; Meshtastic/LoRa nodes can relay a text SOS.",
    ],
    "weather": [
        "Cirrus 'mare's tails' + falling barometer = rain within 24h.",
        "Red sky at night, sailor's delight; red sky in morning = weather moving in.",
        "Froze hard in the morning = cold clear day; fog before noon burns off = fine day.",
        "Cumulonimbus tower = storms; listen for distant thunder and smell for rain.",
        "In lightning: avoid high ground, trees, and open water; crouch low, feet together.",
    ],
}


async def handle_survival(chat, uid, args):
    topic = args.strip().lower()
    if not topic:
        await send(chat, "<b>Survival guides (offline)</b>\nTopics: "
                         + ", ".join(SURVIVAL_GUIDES.keys())
                         + "\n\nUsage: /survival &lt;topic&gt;")
        return
    guide = SURVIVAL_GUIDES.get(topic)
    if not guide:
        await send(chat, f"No guide for '{topic}'. Topics: {', '.join(SURVIVAL_GUIDES.keys())}")
        return
    lines = [f"<b>Survival: {topic}</b>"]
    lines += [f"  {i}. {p}" for i, p in enumerate(guide, 1)]
    await send(chat, "\n".join(lines))


MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.", "!": "-.-.--",
    "/": "-..-.", "(": "-.--.", ")": "-.--.-", "&": ".-...", ":": "---...",
    ";": "-.-.-.", "=": "-...-", "+": ".-.-.", "-": "-....-", "_": "..--.-",
    '"': ".-..-.", "$": "...-..-", "@": ".--.-.",
}
MORSE_REV = {v: k for k, v in MORSE.items()}


async def handle_morse(chat, uid, args):
    parts = args.strip().split(maxsplit=1)
    if not parts:
        await send(chat, "Usage: /morse &lt;text&gt;  |  /morse decode &lt;dashes-dots&gt;")
        return
    mode = "encode"
    payload = args.strip()
    if parts[0].lower() in ("decode", "d"):
        mode = "decode"
        payload = parts[1] if len(parts) > 1 else ""
    if not payload:
        await send(chat, "Empty input.")
        return
    if mode == "encode":
        out = []
        for ch in payload.upper():
            if ch == " ":
                out.append("/")
            elif ch in MORSE:
                out.append(MORSE[ch])
            else:
                out.append("?")
        await send(chat, "<code>" + " ".join(out)[:3500] + "</code>")
    else:
        words = payload.split("/")
        out = []
        for w in words:
            out.append("".join(MORSE_REV.get(t.strip(), "?") for t in w.split()))
        await send(chat, "<code>" + " ".join(out)[:3500] + "</code>")


_UNIT_FACTORS = {
    "length": {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254,
               "ft": 0.3048, "mi": 1609.344, "inch": 0.0254, "feet": 0.3048},
    "weight": {"g": 0.001, "kg": 1.0, "lb": 0.453592, "oz": 0.0283495},
    "data": {"kb": 1e3, "mb": 1e6, "gb": 1e9, "tb": 1e12, "kib": 1024.0, "mib": 1048576.0,
             "gib": 1073741824.0},
    "speed": {"kmh": 1.0, "mph": 1.609344, "mps": 3.6, "knot": 1.852, "kn": 1.852},
    "power": {"w": 1.0, "kw": 1000.0, "hp": 745.7},
    "energy": {"wh": 1.0, "kwh": 1000.0, "j": 1 / 3600.0, "kj": 1000 / 3600.0},
    "time": {"sec": 1.0, "secs": 1.0, "s": 1.0, "min": 60.0, "minute": 60.0, "hr": 3600.0,
             "hour": 3600.0, "day": 86400.0},
}


def _find_unit(u):
    u = u.lower().strip()
    for cat, factors in _UNIT_FACTORS.items():
        if u in factors:
            return cat, factors[u]
    return None, None


async def handle_convert(chat, uid, args):
    if not args:
        await send(chat, ("Usage: /convert &lt;value&gt; &lt;from&gt; to &lt;to&gt;\n"
                          "Examples:\n"
                          "  /convert 100 kmh to mph\n"
                          "  /convert 12 in to cm\n"
                          "  /convert 98.6 f to c\n"
                          "  /convert 64 gb to mb\n"
                          "  /convert 5 kg to lb\n"
                          "  /convert 2 hr to min\n"
                          "  /convert 800 mah to ah\n"))
        return
    parts = [p for p in re.split(r"\s+", args.strip()) if p]
    toks = [p for p in parts if p.lower() not in ("to", "in", "into", "->")]
    if len(toks) < 3:
        await send(chat, "Format: /convert &lt;value&gt; &lt;from&gt; [to] &lt;to&gt;")
        return
    try:
        value = float(toks[0])
    except ValueError:
        await send(chat, f"'{toks[0]}' is not a number.")
        return
    frm, to = toks[1].lower(), toks[2].lower()
    if frm in ("c", "f", "k") and to in ("c", "f", "k"):
        if frm == "c" and to == "f":
            await send(chat, f"{value} C = <b>{value * 9 / 5 + 32:.2f} F</b>")
        elif frm == "c" and to == "k":
            await send(chat, f"{value} C = <b>{value + 273.15:.2f} K</b>")
        elif frm == "f" and to == "c":
            await send(chat, f"{value} F = <b>{(value - 32) * 5 / 9:.2f} C</b>")
        elif frm == "f" and to == "k":
            await send(chat, f"{value} F = <b>{(value - 32) * 5 / 9 + 273.15:.2f} K</b>")
        elif frm == "k" and to == "c":
            await send(chat, f"{value} K = <b>{value - 273.15:.2f} C</b>")
        elif frm == "k" and to == "f":
            await send(chat, f"{value} K = <b>{(value - 273.15) * 5 / 9 + 32:.2f} F</b>")
        else:
            await send(chat, f"{value} {frm} = {value} {to}")
        return
    if frm == "mah" and to == "ah":
        await send(chat, f"{value} mAh = <b>{value / 1000:.3f} Ah</b>")
        return
    if frm == "ah" and to == "mah":
        await send(chat, f"{value} Ah = <b>{value * 1000:.0f} mAh</b>")
        return
    cat_f, f_factor = _find_unit(frm)
    cat_t, t_factor = _find_unit(to)
    if not f_factor or not t_factor:
        await send(chat, f"Unknown unit pair '{frm}' -> '{to}'.")
        return
    if cat_f != cat_t:
        await send(chat, f"Cannot convert {cat_f} to {cat_t}.")
        return
    await send(chat, f"{value} {frm} = <b>{value * f_factor / t_factor:g} {to}</b>")


async def handle_solarcalc(chat, uid, args):
    nums = re.findall(r"\d+(?:\.\d+)?", args or "")
    if args.strip().lower().startswith("plan"):
        wh_needed = float(nums[0]) if nums else 60.0
        sun = float(nums[1]) if len(nums) > 1 else 4.0
        panel = wh_needed / (sun * 0.75)
        await send(chat, f"<b>Solar plan</b> ({wh_needed:.0f}Wh/day, {sun}h sun)\n"
                         f"Panel needed: <b>{panel:.0f}W</b> (75% system efficiency)\n"
                         f"Cheap options: {max(20, panel / 2):.0f}W (2 panels) or {max(20, panel):.0f}W single panel\n"
                         f"Battery for 3 days autonomy: <b>{wh_needed * 3:.0f}Wh</b>")
        return
    panel = float(nums[0]) if len(nums) > 0 else 25.0
    battery = float(nums[1]) if len(nums) > 1 else 100.0
    deck = float(nums[2]) if len(nums) > 2 else 8.0
    sun = float(nums[3]) if len(nums) > 3 else 4.0
    runtime = battery * 0.85 / deck
    daily_out = panel * sun * 0.75
    charge_h = battery / (panel * 0.8)
    solar_run = daily_out / deck
    lines = [f"<b>Solar sizing</b>  panel {panel:.0f}W | battery {battery:.0f}Wh | deck {deck:.0f}W",
             f"Runtime on battery alone: <b>{runtime:.1f}h</b> ({battery * 0.85:.0f}Wh usable @85%)",
             f"Charge time from panel: <b>{charge_h:.1f}h</b> sun ({panel * 0.8:.0f}W effective)",
             f"Daily harvest: <b>{daily_out:.0f}Wh</b> at {sun}h sun -> <b>{solar_run:.1f}h</b> deck time",
             "",
             f"Battery for 24h of deck: <b>{deck * 24 / 0.85:.0f}Wh</b>",
             f"Panel for 24h/day at {sun}h sun: <b>{deck * 24 / (sun * 0.75):.0f}W</b>",
             "",
             "Defaults: 25W panel, 100Wh battery, 8W deck (7\" + SBC), 4h sun. "
             "Usage: /solarcalc &lt;panelW&gt; [batteryWh] [deckW] [sunH] | /solarcalc plan &lt;Wh/day&gt;"]
    await send(chat, "\n".join(lines))

async def handle_3d(chat, uid, args):
    if not args:
        await send(chat, "Usage: /3d &lt;description&gt; [style]\nStyles: futuristic, retro, industrial, minimal, steampunk, cyberpunk, nautical, solarpunk, cassette_futurism, feminine_craft, fallout, brutalist")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM + "\nGenerate OpenSCAD code for 3D models."})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate an OpenSCAD 3D model for: {args}. Include the full .scad code with dimensions, colors, and style notes. Suggest STL export settings."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"3D error: {e}")

async def handle_pcb(chat, uid, args):
    if not args:
        await send(chat, "Usage: /pcb &lt;description&gt;\nExample: /pcb HDMI to DSI adapter board")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM + "\nGenerate PCB designs with component placement and trace routing."})
        _sessions[str(uid)].append({"role": "user", "content": f"Design a custom PCB for: {args}. Include: schematic description, component list, board dimensions, trace routing notes, and gerber file suggestions."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"PCB error: {e}")

async def handle_cables(chat, uid, args):
    if not args:
        await send(chat, "Usage: /cables &lt;build description&gt;")
        return
    await typing(chat)
    try:
        if "CableRouter" in cd_classes:
            router = cd_classes["CableRouter"]
            build = {"description": args, "components": {}}
            plan = router.generate_routing_plan(build)
            if plan:
                lines = ["<b>Cable Routing Plan:</b>\n"]
                if isinstance(plan, dict):
                    for k, v in plan.items():
                        lines.append(f"<b>{k}:</b> {v}")
                else:
                    lines.append(str(plan))
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a cable routing plan for: {args}. Include: cable types, lengths, routing paths, connectors, and cable management tips."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Cables error: {e}")

def _extract_build_components(text):
    t = text.lower()
    c = {}
    sbc = {}
    if any(k in t for k in ("pi 5", "raspberry pi 5", "pi5")):
        sbc = {"id": "pi5", "connectivity": "WiFi", "form_factor": "hat"}
    elif any(k in t for k in ("pi zero 2w", "zero 2w", "pi zero")):
        sbc = {"id": "pi zero 2w", "connectivity": "WiFi", "form_factor": "mini"}
    elif any(k in t for k in ("rock 5", "rock5")):
        sbc = {"id": "rock5b", "connectivity": "WiFi", "form_factor": "itx"}
    power = {}
    if "ups hat" in t:
        power = {"type": "ups_hat", "output": "5V/5A"}
    elif "power bank" in t:
        power = {"type": "power_bank", "output": "5V/3A"}
    elif "battery" in t:
        power = {"type": "battery", "output": "5V/3A"}
    if "18650" in t and "bms" not in t:
        power["name"] = "18650 cells"
    if sbc:
        if power:
            sbc["power_draw"] = "5V/5A"
        c["sbc"] = sbc
    if power:
        c["power"] = power
    if any(k in t for k in ("wifi", "wlan", "bluetooth", "ethernet")):
        c["connectivity"] = {"id": "ethernet" if "ethernet" in t else "wifi"}
    if "fan" in t:
        c["cooling"] = {"type": "active_fan_heatsink"}
    elif any(k in t for k in ("heatsink", "heat sink")):
        c["cooling"] = {"type": "Passive"}
    if "hdmi" in t:
        c["display"] = {"interface": "mini HDMI" if "mini hdmi" in t else "HDMI"}
    return c

async def handle_flaws(chat, uid, args):
    if not args:
        await send(chat, "Usage: /flaws &lt;build description&gt;")
        return
    await typing(chat)
    try:
        if "BuildOptimizer" in cd_classes:
            optimizer = cd_classes["BuildOptimizer"]
            build = {"description": args, "components": _extract_build_components(args)}
            flaws = optimizer.scan_flaws(build)
            if flaws:
                lines = ["<b>Detected Flaws:</b>\n"]
                if isinstance(flaws, list):
                    for f in flaws:
                        if isinstance(f, dict):
                            sev = str(f.get('severity', 'WARNING')).upper()
                            lines.append(f"[{sev}] <b>{f.get('type', 'Issue')}</b>: {f.get('issue', f.get('description', str(f)))}")
                            if f.get("fix"):
                                lines.append(f"  -> Fix: {f['fix']}")
                        else:
                            lines.append(f"[WARNING] {f}")
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Analyze this cyberdeck build for flaws: {args}. Check power, cooling, connectivity, safety, compatibility. List each flaw with severity and fix."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Flaws error: {e}")

async def handle_pack(chat, uid, args):
    if not args:
        await send(chat, "Usage: /pack &lt;build description&gt;")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a complete build pack for: {args}. Include: README, BOM, assembly tutorial, cable guide, OpenSCAD enclosure code, and purchase links."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Pack error: {e}")

async def handle_career(chat, uid, args):
    if not args:
        careers = ["coding", "gaming", "ai_ml", "security", "writer", "field_research",
                   "robotics", "media_production", "ham_radio", "home_automation", "portable_hacking"]
        await send(chat, "<b>Career Templates:</b>\n" + "\n".join(f"  • {c}" for c in careers) + "\n\nUsage: /career &lt;name&gt;")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a cyberdeck build optimized for the career: {args}. Include best components, software setup, and use-case specific features."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Career error: {e}")

async def handle_dashboard(chat, uid, args):
    await typing(chat)
    try:
        if "InteractiveDashboard" in cd_classes and args:
            dash = cd_classes["InteractiveDashboard"]
            build = {"name": args, "components": {}, "description": args}
            output_file = os.path.join(DIR, f"cyberdeck_dashboard_{uid}.html")
            result = dash.generate_dashboard([build], output_file)
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                await send(chat, f"<b>Dashboard generated!</b>\nFile: <code>{os.path.basename(output_file)}</code>\nSize: {size} bytes\n\nOpen in browser to view the interactive dashboard with 3D preview, component picker, and cable guide.")
                return
        # Fallback: AI-generated
        if not args:
            await send(chat, "Usage: /dashboard &lt;build description&gt;\nGenerates an interactive HTML dashboard.")
            return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM + "\nGenerate HTML dashboards with interactive components."})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a complete interactive HTML dashboard for this cyberdeck build: {args}. Include: 3D preview, component table with prices, BOM total, assembly progress tracker, cable diagram, and customization options. Use inline CSS, make it responsive and dark-themed."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Dashboard error: {e}")

async def handle_specs(chat, uid, args):
    if not args:
        await send(chat, "Usage: /specs &lt;component_id&gt;\nExample: /specs rpi5")
        return
    await typing(chat)
    try:
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import ComponentDatabase
            details = ComponentDatabase.get_component_details(args)
            if details:
                lines = [f"<b>Component: {args}</b>\n"]
                if isinstance(details, dict):
                    for k, v in details.items():
                        if isinstance(v, dict):
                            lines.append(f"<b>{k}:</b>")
                            for sk, sv in v.items():
                                lines.append(f"  {sk}: {sv}")
                        else:
                            lines.append(f"<b>{k}:</b> {v}")
                else:
                    lines.append(str(details))
                await send(chat, "\n".join(lines))
                return
        await send(chat, f"Component '{args}' not found in database.\nUse /list to see available components.")
    except Exception as e:
        await send(chat, f"Specs error: {e}")

# ============================================================
# v5.2 — Custom Builder
# ============================================================
async def handle_custom_build(chat, uid, args):
    await typing(chat)
    try:
        if "CustomBuildEngine" in cd_classes:
            engine = cd_classes["CustomBuildEngine"]
            if args.startswith("list "):
                cat = args.split(maxsplit=1)[1]
                options = engine.get_category_options(cat)
                if options:
                    lines = [f"<b>{cat.upper()} options:</b>\n"]
                    for o in options[:15]:
                        lines.append(f"• <b>{o['name']}</b> (${o['price']})\n  Specs: {o.get('key_specs', 'N/A')}")
                    await send(chat, "\n".join(lines))
                else:
                    await send(chat, f"No options for '{cat}'. Categories: {', '.join(engine.CATEGORIES.keys())}")
                return
            if args.startswith("select "):
                parts = args.split(maxsplit=2)
                if len(parts) >= 3:
                    result = engine.select_component(uid, parts[1], parts[2])
                    if "error" in result:
                        await send(chat, f"Error: {result['error']}")
                    else:
                        lines = [f"<b>Selected: {parts[1]} → {parts[2]}</b>"]
                        if result.get("compatibility"):
                            for c in result["compatibility"]:
                                icon = "✅" if c.get("ok") else "⚠️"
                                lines.append(f"{icon} {c.get('check', '')}: {c.get('note', '')}")
                        price = result.get("price", "?")
                        lines.append(f"\nPrice: ${price}")
                        await send(chat, "\n".join(lines))
                    return
            # Default: show categories
            cats = engine.CATEGORIES
            lines = ["<b>Custom Build — Pick Components</b>\n"]
            for cid, cat in cats.items():
                icon = cat.get("icon", "")
                req = " (required)" if cat.get("required") else ""
                lines.append(f"{icon} <b>{cid}</b>{req}: {cat['desc']}")
            lines.append("\nUsage:")
            lines.append("  /cb list &lt;category&gt; — see options")
            lines.append("  /cb select &lt;category&gt; &lt;id&gt; — pick component")
            await send(chat, "\n".join(lines))
        else:
            await send(chat, "CustomBuildEngine not loaded")
    except Exception as e:
        await send(chat, f"Custom build error: {e}")

# ============================================================
# v5.0 — Peripheral Recommendation
# ============================================================
async def handle_peripherals(chat, uid, args):
    await typing(chat)
    try:
        if "PeripheralRecommendationEngine" in cd_classes:
            engine = cd_classes["PeripheralRecommendationEngine"]
            if args:
                recs = engine.recommend_for_category(args.lower())
                if recs:
                    lines = [f"<b>Peripherals for {args}:</b>\n"]
                    for db_name, items in recs.items():
                        if db_name.startswith("_"):
                            continue
                        lines.append(f"<b>{db_name}:</b>")
                        for item in items[:3]:
                            lines.append(f"  • {item.get('name', item.get('id', '?'))} — ${item.get('price', '?')}")
                    if "_total_estimated_cost" in recs:
                        lines.append(f"\n<b>Total est:</b> ${recs['_total_estimated_cost']}")
                        lines.append(f"<b>Budget left:</b> ${recs['_budget_remaining']}")
                    await send(chat, "\n".join(lines))
                else:
                    await send(chat, f"No peripherals found for '{args}'")
            else:
                cats = list(cd_classes.get("ComponentDatabase", {}).get_all_sbcs().keys())[:5] if "ComponentDatabase" in cd_classes else []
                await send(chat, "Usage: /peripherals &lt;category&gt;\nExample: /peripherals security\n\nCategories: security, coding, gaming, research, ai, survival, media, drone")
        else:
            await send(chat, "PeripheralRecommendationEngine not loaded")
    except Exception as e:
        await send(chat, f"Peripherals error: {e}")

# ============================================================
# v5.0 — Antenna Calculator
# ============================================================
async def handle_antenna(chat, uid, args):
    await typing(chat)
    try:
        if "AntennaCalculator" in cd_classes:
            calc = cd_classes["AntennaCalculator"]
            if args:
                try:
                    freq = float(args.replace("mhz", "").replace("MHz", "").strip())
                    wavelength = calc.calculate_wavelength(freq)
                    quarter = calc.quarter_wave(freq)
                    connector = calc.recommend_connector(freq)
                    lines = [
                        f"<b>Antenna Calculator — {freq} MHz</b>\n",
                        f"Wavelength: {wavelength:.1f} cm",
                        f"Quarter-wave: {quarter:.1f} cm",
                        f"Recommended connector: {connector}",
                    ]
                    # Cable losses
                    for cable in ["RG58", "LMR200", "LMR400"]:
                        loss = calc.cable_loss_db(cable, freq, 1.0)
                        lines.append(f"{cable} loss (1m): {loss} dB")
                    await send(chat, "\n".join(lines))
                except ValueError:
                    await send(chat, "Usage: /antenna &lt;freq_mhz&gt;\nExample: /antenna 433\nExample: /antenna 915")
            else:
                await send(chat, "Usage: /antenna &lt;freq_mhz&gt;\nCommon: 433 (LoRa), 868 (EU LoRa), 915 (US LoRa), 2400 (WiFi)")
        else:
            await send(chat, "AntennaCalculator not loaded")
    except Exception as e:
        await send(chat, f"Antenna error: {e}")

# ============================================================
# v5.0 — Battery Sizing
# ============================================================
async def handle_battery(chat, uid, args):
    await typing(chat)
    try:
        if "BatterySizingCalculator" in cd_classes:
            calc = cd_classes["BatterySizingCalculator"]
            parts = args.split()
            if parts:
                try:
                    cells = int(parts[0])
                    watts = float(parts[1]) if len(parts) > 1 else 10.0
                    cap = calc.calculate_18650_capacity(cells)
                    rec = calc.recommend_capacity(watts, 4.0, cells)
                    lines = [
                        f"<b>Battery Sizing — {cells}x 18650</b>\n",
                        f"Total: {cap['total_wh']} Wh",
                        f"Runtime @5W: {cap['runtime_hours_5w']}h",
                        f"Runtime @10W: {cap['runtime_hours_10w']}h",
                        f"Runtime @15W: {cap['runtime_hours_15w']}h",
                        f"Weight: {cap['weight_grams']}g",
                        f"\nFor {watts}W draw (4h):",
                        f"  Needed: {rec['needed_wh']} Wh",
                        f"  Cells needed: {rec['cells_recommended']}",
                        f"  Sufficient: {'Yes' if rec['sufficient'] else 'No — need more cells'}",
                    ]
                    await send(chat, "\n".join(lines))
                except ValueError:
                    await send(chat, "Usage: /battery &lt;cells&gt; [watts]\nExample: /battery 6 10")
            else:
                await send(chat, "Usage: /battery &lt;cells&gt; [watts]\nExample: /battery 6 (default 10W)\nExample: /battery 4 5")
        else:
            await send(chat, "BatterySizingCalculator not loaded")
    except Exception as e:
        await send(chat, f"Battery error: {e}")

# ============================================================
# v5.0 — Forensics Module
# ============================================================
async def handle_forensics(chat, uid, args):
    await typing(chat)
    try:
        if "ForensicsModule" in cd_classes:
            mod = cd_classes["ForensicsModule"]
            if args:
                proc = mod.get_procedure(args.lower())
                if "error" in proc:
                    await send(chat, f"Unknown procedure. Available: {', '.join(mod.list_procedures())}")
                else:
                    lines = [
                        f"<b>{proc['name']}</b>\n",
                        f"<b>Tool:</b> <code>{proc.get('tool', 'N/A')}</code>",
                    ]
                    if proc.get("dc3dd"):
                        lines.append(f"<b>dc3dd:</b> <code>{proc['dc3dd']}</code>")
                    lines.append(f"<b>Notes:</b> {proc.get('notes', 'N/A')}")
                    await send(chat, "\n".join(lines))
            else:
                procs = mod.list_procedures()
                await send(chat, f"<b>Digital Forensics Tools:</b>\n\n" + "\n".join(f"  /forensics {p}" for p in procs))
        else:
            await send(chat, "ForensicsModule not loaded")
    except Exception as e:
        await send(chat, f"Forensics error: {e}")

# ============================================================
# v5.0 — Test Equipment
# ============================================================
async def handle_testeq(chat, uid, args):
    await typing(chat)
    try:
        if "TestEquipmentModule" in cd_classes:
            mod = cd_classes["TestEquipmentModule"]
            if args:
                eq = mod.get_equipment(args.lower())
                if "error" in eq:
                    await send(chat, f"Unknown. Available: {', '.join(mod.list_equipment())}")
                else:
                    lines = [f"<b>{eq['name']}</b>\nType: {eq.get('type', '?')}\nPrice: ${eq.get('price', '?')}"]
                    for k, v in eq.items():
                        if k not in ("name", "type", "price"):
                            lines.append(f"{k}: {v}")
                    await send(chat, "\n".join(lines))
            else:
                items = mod.list_equipment()
                lines = ["<b>Portable Test Equipment:</b>\n"]
                for name in items:
                    eq = mod.get_equipment(name)
                    lines.append(f"  /testeq {name} — {eq.get('name', name)} (${eq.get('price', '?')})")
                await send(chat, "\n".join(lines))
        else:
            await send(chat, "TestEquipmentModule not loaded")
    except Exception as e:
        await send(chat, f"Test equipment error: {e}")

# ============================================================
# v5.0 — Ham Radio
# ============================================================
async def handle_hamradio(chat, uid, args):
    await typing(chat)
    try:
        if "HamRadioModule" in cd_classes:
            mod = cd_classes["HamRadioModule"]
            if args:
                band = mod.BANDS.get(args.lower())
                if not band:
                    await send(chat, f"Unknown band. Available: {', '.join(mod.BANDS.keys())}")
                else:
                    lines = [
                        f"<b>Ham Radio Band: {args}</b>\n",
                        f"Frequency: {band['freq_mhz']} MHz",
                        f"Mode: {band['mode']}",
                        f"Wavelength: {band['wavelength']}",
                    ]
                    if "AntennaCalculator" in cd_classes:
                        calc = cd_classes["AntennaCalculator"]
                        quarter = calc.quarter_wave(band["freq_mhz"])
                        lines.append(f"Quarter-wave antenna: {quarter:.1f} cm")
                    await send(chat, "\n".join(lines))
            else:
                bands = mod.BANDS
                lines = ["<b>Ham Radio Bands:</b>\n"]
                for name, band in bands.items():
                    lines.append(f"  /hamradio {name} — {band['freq_mhz']} MHz ({band['mode']})")
                await send(chat, "\n".join(lines))
        else:
            await send(chat, "HamRadioModule not loaded")
    except Exception as e:
        await send(chat, f"Ham radio error: {e}")

# ============================================================
# v5.0 — Color Palettes
# ============================================================
async def handle_palette(chat, uid, args):
    await typing(chat)
    try:
        if "COLOR_PALETTE_DATABASE" in cd_classes:
            db = cd_classes["COLOR_PALETTE_DATABASE"]
            if args and args in db:
                p = db[args]
                lines = [f"<b>Palette: {p.get('name', args)}</b>\n"]
                colors = p.get("colors", [])
                for c in colors:
                    if isinstance(c, dict):
                        lines.append(f"  {c.get('name', '')}: {c.get('hex', '')}")
                    else:
                        lines.append(f"  {c}")
                if p.get("description"):
                    lines.append(f"\n{p['description']}")
                await send(chat, "\n".join(lines))
            else:
                names = list(db.keys())
                await send(chat, "<b>Color Palettes:</b>\n" + "\n".join(f"  /palette {n}" for n in names))
        else:
            await send(chat, "Color palette database not loaded")
    except Exception as e:
        await send(chat, f"Palette error: {e}")

# ============================================================
# v5.0 — Aesthetic Materials
# ============================================================
async def handle_material(chat, uid, args):
    await typing(chat)
    try:
        if "AESTHETIC_MATERIAL_DATABASE" in cd_classes:
            db = cd_classes["AESTHETIC_MATERIAL_DATABASE"]
            if args and args in db:
                m = db[args]
                lines = [f"<b>Material: {m.get('name', args)}</b>\n"]
                for k, v in m.items():
                    if k != "name":
                        lines.append(f"{k}: {v}")
                await send(chat, "\n".join(lines))
            else:
                names = list(db.keys())
                await send(chat, "<b>Aesthetic Materials:</b>\n" + "\n".join(f"  /material {n}" for n in names))
        else:
            await send(chat, "Aesthetic material database not loaded")
    except Exception as e:
        await send(chat, f"Material error: {e}")

# ============================================================
# v5.0 — Thermal Interface
# ============================================================
async def handle_thermal(chat, uid, args):
    await typing(chat)
    try:
        if "THERMAL_INTERFACE_DATABASE" in cd_classes:
            db = cd_classes["THERMAL_INTERFACE_DATABASE"]
            if args and args in db:
                t = db[args]
                lines = [f"<b>Thermal: {t.get('name', args)}</b>\n"]
                for k, v in t.items():
                    if k != "name":
                        lines.append(f"{k}: {v}")
                await send(chat, "\n".join(lines))
            else:
                names = list(db.keys())
                await send(chat, "<b>Thermal Interface Materials:</b>\n" + "\n".join(f"  /thermal {n}" for n in names))
        else:
            await send(chat, "Thermal interface database not loaded")
    except Exception as e:
        await send(chat, f"Thermal error: {e}")

# ============================================================
# Hardware Module Handlers (NATO rails, sliding screens, NP-F, Li'l PCB)
# ============================================================
async def handle_hardware(chat, uid, args):
    await typing(chat)
    try:
        hw = cd_classes.get("HardwareModuleGenerator")
        if not hw:
            await send(chat, "HardwareModuleGenerator not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            types = hw.list_module_types()
            lines = ["<b>Hardware Module Catalog</b>\n"]
            for t in types:
                mods = hw.list_modules(t)
                lines.append(f"\n<b>{t.upper()}:</b>")
                for mid, m in mods.items():
                    lines.append(f"  /hardware {mid} — {m['name']} (${m.get('price', '?')})")
            lines.append("\n<b>Plans:</b>")
            lines.append("  /hardware nato [rails] — NATO rail layout")
            lines.append("  /hardware slide [inches] [heavy] — Sliding screen plan")
            lines.append("  /hardware npf [dual] — NP-F battery plan")
            await send(chat, "\n".join(lines))
            return
        cmd = parts[0]
        if cmd == "nato":
            rails = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 3
            plan = hw.generate_nato_layout(rails)
            await send(chat, f"<b>NATO Rail Layout ({rails} rails)</b>\n\n<pre>{plan}</pre>")
        elif cmd == "slide":
            inches = parts[1] if len(parts) > 1 else "7"
            heavy = "heavy" in parts
            plan = hw.generate_sliding_screen_plan(inches, heavy)
            await send(chat, f"<b>Sliding Screen Plan ({inches}\")</b>\n\n<pre>{plan}</pre>")
        elif cmd == "npf":
            dual = "dual" in parts
            plan = hw.generate_npf_battery_plan(dual)
            await send(chat, f"<b>NP-F Battery Plan{' (Dual)' if dual else ''}</b>\n\n<pre>{plan}</pre>")
        else:
            mod = hw.get_module(cmd)
            if mod:
                lines = [f"<b>{mod['name']}</b>", f"Type: {mod.get('type', '?')} | Tier: {mod.get('tier', '?')} | ${mod.get('price', 0):.2f}", f"Description: {mod.get('description', '')}", f"Includes: {mod.get('includes', 'N/A')}", f"Weight: {mod.get('weight_g', '?')}g"]
                if mod.get("max_screen"):
                    lines.append(f"Max screen: {mod['max_screen']}")
                if mod.get("output"):
                    lines.append(f"Output: {mod['output']}")
                if mod.get("stl_files"):
                    lines.append(f"STL files: {', '.join(mod['stl_files'])}")
                if mod.get("needs_module"):
                    parent = hw.get_module(mod["needs_module"])
                    lines.append(f"Requires: {parent['name'] if parent else mod['needs_module']}")
                lines.append(f"\nBest for: {', '.join(mod.get('best_for', []))}")
                await send(chat, "\n".join(lines))
            else:
                await send(chat, f"Unknown module: {cmd}. Type /hardware for catalog.")
    except Exception as e:
        await send(chat, f"Hardware error: {e}")
        log(f"Hardware error: {e}")

async def handle_modules(chat, uid, args):
    await typing(chat)
    try:
        hw = cd_classes.get("HardwareModuleGenerator")
        if not hw:
            await send(chat, "HardwareModuleGenerator not loaded")
            return
        parts = args.lower().strip().split()
        lilpcb = hw.list_modules("pcb_module")
        if not parts:
            lines = ["<b>Li'l PCB Hot-Swappable Module Ecosystem</b>\n", "Backplane (required):"]
            bp = hw.get_module("lilpcb_backplane")
            lines.append(f"  /modules backplane — {bp['name']} (${bp.get('price', 0):.2f})")
            lines.append("")
            lines.append("<b>Modules available:</b>")
            for mid, m in lilpcb.items():
                if mid == "lilpcb_backplane":
                    continue
                lines.append(f"  /modules {mid} — {m['name']} (${m.get('price', 0):.2f})")
            lines.append("")
            lines.append("<b>Build a stack:</b>")
            lines.append("  /modules backplane sdr lora gps")
            lines.append("  /modules backplane nvme env_sensor")
            lines.append("  /lilpcb sdr lora gps env_sensor")
            await send(chat, "\n".join(lines))
            return
        if parts[0] == "backplane" or parts[0] in lilpcb:
            mod = hw.get_module(parts[0])
            if mod:
                lines = [f"<b>{mod['name']}</b>", f"Type: {mod.get('type', '?')} | ${mod.get('price', 0):.2f}", f"Description: {mod.get('description', '')}", f"Includes: {mod.get('includes', 'N/A')}", f"Weight: {mod.get('weight_g', '?')}g"]
                if mod.get("slot_count"):
                    lines.append(f"Slots: {mod['slot_count']}")
                if mod.get("frequency"):
                    lines.append(f"Freq: {mod['frequency']}")
                if mod.get("range_km"):
                    lines.append(f"Range: {mod['range_km']}km")
                await send(chat, "\n".join(lines))
            return
        # Try building config from module list
        mod_ids = []
        for p in parts:
            if p in lilpcb or p == "lilpcb_backplane":
                mod_ids.append(p)
        if mod_ids:
            total, details = hw.total_module_cost(mod_ids)
            plan = hw.generate_lilpcb_plan(mod_ids)
            await send(chat, f"<b>Li'l PCB Config ({len(mod_ids)} modules)</b>\n\n<pre>{plan}</pre>\nCost:\n" + "\n".join(details) + f"\n  <b>Total: ${total:.2f}</b>")
        else:
            await send(chat, f"No valid modules in: {args}. See /modules for catalog.")
    except Exception as e:
        await send(chat, f"Modules error: {e}")

async def handle_lilpcb(chat, uid, args):
    await handle_modules(chat, uid, f"lilpcb_backplane {args}")

# ============================================================
# Soldering Tutorial
# ============================================================
async def handle_solder(chat, uid, args):
    await typing(chat)
    topic = args.lower().strip() if args else ""
    guides = {
        "": {
            "title": "Battery Soldering — Complete Guide",
            "steps": [
                "1. PREP: Clean 18650 terminals with isopropyl alcohol",
                "2. TIN: Apply flux to battery terminals, tin both battery and wire with solder",
                "3. QUICK: Touch iron (350°C) to terminal for max 2-3 seconds — lithium cells hate heat",
                "4. COOL: Let terminal cool completely between welds",
                "5. INSULATE: Cover solder joints with kapton tape + heat shrink",
                "",
                "⚠ CRITICAL: Never short positive/negative. Always use a BMS. Never pierce 18650 casing.",
                "🎥 Video: https://youtube.com/watch?v=DS6qReI1LbI (GreatScott! 18650 soldering guide)",
                "",
                "Better option: Buy a spot welder (Rp150-300k on Shopee) + pure nickel strips.",
                "Spot welding is MUCH safer than soldering directly to 18650 terminals.",
            ],
            "tools": ["Soldering iron (adjustable, 350°C)", "60/40 tin-lead or lead-free solder",
                      "Rosin flux pen", "Helping hands / third hand", "Wire stripper",
                      "Kapton tape", "Heat shrink assortment", "Multimeter"],
            "warnings": ["NEVER short 18650 terminals — fire/explosion risk",
                         "Do NOT heat 18650 for more than 3 seconds — thermal runaway",
                         "Always use a BMS (Battery Management System)",
                         "Check polarity with multimeter before connecting to device",
                         "Use appropriate gauge wire (18-22 AWG for power)",
                         "Double-check: no stray wire strands touching opposite terminals"],
        },
        "wire": {
            "title": "Soldering Basics — Wire",
            "steps": [
                "1. Strip 5mm of insulation using wire stripper",
                "2. Twist strands together",
                "3. Tin wire: apply solder to iron tip, touch to wire, feed solder into strands",
                "4. Tin pad: apply solder to PCB pad",
                "5. JOIN: hold tinned wire to tinned pad, reheat briefly",
            ],
            "tools": ["Soldering iron", "Solder", "Wire stripper", "Helping hands"],
            "warnings": ["Don't breathe the fumes (use fan or fume extractor)"],
        },
        "throughhole": {
            "title": "Through-Hole Soldering (Pin Headers, GPIO)",
            "steps": [
                "1. Insert component leg through PCB hole",
                "2. Bend leg slightly outward at 45° to hold in place",
                "3. Touch iron tip to both pad and leg simultaneously",
                "4. Feed solder into the joint (not onto the iron)",
                "5. Remove iron, let cool — should look like a shiny 'volcano'",
                "6. Clip excess leg with flush cutters",
            ],
            "tools": ["Soldering iron", "Solder", "Flush cutters", "Flux pen"],
            "warnings": ["Cold joint = dull grey = bad. Reheat if needed.",
                         "Don't use too much solder — can bridge adjacent pins"],
        },
        "desolder": {
            "title": "Desoldering — Fixing Mistakes",
            "steps": [
                "1. Apply flux to the joint",
                "2. Use solder wick: place wick on joint, press iron on top, wick absorbs molten solder",
                "3. OR use solder sucker: heat joint, quickly position sucker, press trigger",
                "4. Repeat until clean",
                "5. Use isopropyl alcohol + brush to clean flux residue",
            ],
            "tools": ["Solder wick", "Solder sucker", "Flux", "Isopropyl alcohol", "Small brush"],
            "warnings": ["Don't lift PCB pads by excessive heat or force",
                         "Add fresh solder to old joints before desoldering — helps heat transfer"],
        },
    }
    guide = guides.get(topic, guides[""])
    lines = [
        f"<b>🛠 {guide['title']}</b>\n",
        "<b>Tools:</b>",
    ]
    for t in guide["tools"]:
        lines.append(f"  • {t}")
    lines.append("")
    lines.append("<b>Steps:</b>")
    for s in guide["steps"]:
        lines.append(f"  {s}")
    lines.append("")
    lines.append("<b>⚠ Warnings:</b>")
    for w in guide["warnings"]:
        lines.append(f"  ⚠ {w}")
    lines.append("")
    lines.append("<b>Sub-topics:</b> /solder (general battery)  /solder wire  /solder throughhole  /solder desolder")
    await send(chat, "\n".join(lines))

# ============================================================
# v6.3 — Compare two builds
# ============================================================
async def handle_compare(chat, uid, args):
    if not args or "|" not in args:
        await send(chat, "Usage: /compare &lt;BuildA&gt; | &lt;BuildB&gt;\nCompare two builds side-by-side.\nExample: /compare portable hacking rig | solar writerdeck")
        return
    await typing(chat)
    try:
        bc = cd_classes.get("BuildComparison")
        if not bc:
            await send(chat, "BuildComparison not loaded")
            return
        parts = [p.strip() for p in args.split("|", 1)]
        build_a = {"name": parts[0], "components": {}, "description": parts[0]}
        build_b = {"name": parts[1], "components": {}, "description": parts[1]}
        # Try to get AI-generated component data
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate build data as JSON for: {parts[0]}. Return JSON with keys: sbc, display, keyboard, enclosure, power, cooling, storage, connectivity, total_price, power_draw_w, weight_kg, battery_life_h. Use numeric values where possible."})
        reply_a = await call_ai(_sessions[str(uid)][-10:])
        _sessions[str(uid)].append({"role": "assistant", "content": reply_a})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate build data as JSON for: {parts[1]}. Same format."})
        reply_b = await call_ai(_sessions[str(uid)][-10:])
        result = bc.compare(build_a, build_b)
        formatted = bc.format_comparison(result)
        await send(chat, formatted)
    except Exception as e:
        await send(chat, f"Compare error: {e}")
        log(f"Compare error: {e}")

# ============================================================
# v6.3 — Export BOM as CSV
# ============================================================
async def handle_bomcsv(chat, uid, args):
    if not args:
        await send(chat, "Usage: /bomcsv &lt;build&gt;\nExport bill of materials as CSV.")
        return
    await typing(chat)
    try:
        be = cd_classes.get("BOMExporter")
        if not be:
            await send(chat, "BOMExporter not loaded")
            return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a build JSON for: {args}. Include components dict with category keys each containing list of dicts with name, model, price, qty, notes. Set total_price."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        build = {"name": args, "components": {}, "total_price": 0}
        csv_data = be.to_csv(build)
        filepath = os.path.join(DIR, f"bom_{uid}.csv")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(csv_data)
        size = os.path.getsize(filepath)
        await send(chat, f"<b>BOM CSV exported!</b>\nFile: <code>bom_{uid}.csv</code>\nSize: {size} bytes\n\n<pre>{csv_data[:1500]}</pre>")
    except Exception as e:
        await send(chat, f"BOM CSV error: {e}")

# ============================================================
# v6.3 — Build Revision Timeline
# ============================================================
async def handle_timeline(chat, uid, args):
    await typing(chat)
    try:
        key = f"timeline_{uid}"
        if key not in cd_classes:
            from cyberdeck_agent import BuildTimeline as BuildTimelineCls
            cd_classes[key] = BuildTimelineCls()
        tl = cd_classes[key]
        parts = args.strip().split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        if not cmd:
            revs = tl.list_revisions()
            if revs:
                lines = ["<b>Build Timeline</b>", ""]
                for r in revs[-10:]:
                    lines.append(f"  v{r['version']} [{r['timestamp'][:19]}] {r['notes']}")
                lines.append("\nUsage: /timeline save &lt;notes&gt;  /timeline diff v1 v2  /timeline list")
                await send(chat, "\n".join(lines))
            else:
                await send(chat, "No revisions yet. Usage: /timeline save &lt;notes&gt;")
            return
        if cmd == "save":
            notes = parts[1] if len(parts) > 1 else ""
            build = {"name": notes[:50], "components": {}, "total_price": 0}
            v = tl.save_revision(build, notes)
            await send(chat, f"Saved revision <b>v{v}</b>: {notes}")
        elif cmd == "list":
            revs = tl.list_revisions()
            if revs:
                lines = [f"<b>Timeline ({len(revs)} revisions)</b>", ""]
                for r in revs:
                    lines.append(f"  v{r['version']} [{r['timestamp'][:19]}] {r['notes']}")
                await send(chat, "\n".join(lines))
            else:
                await send(chat, "No revisions saved.")
        elif cmd == "diff":
            vp = parts[1].split() if len(parts) > 1 else []
            if len(vp) < 2:
                await send(chat, "Usage: /timeline diff &lt;v1&gt; &lt;v2&gt;")
                return
            try:
                diff = tl.diff_revisions(int(vp[0]), int(vp[1]))
                await send(chat, diff)
            except ValueError:
                await send(chat, "Invalid version numbers. Use integers.")
        else:
            await send(chat, "Usage: /timeline save &lt;notes&gt;  /timeline diff v1 v2  /timeline list")
    except Exception as e:
        await send(chat, f"Timeline error: {e}")

# ============================================================
# v6.3 — Changelog
# ============================================================
async def handle_changelog(chat, uid, args):
    await typing(chat)
    try:
        cl = cd_classes.get("Changelog")
        if cl:
            await send(chat, cl.format())
        else:
            await send(chat, "Changelog not loaded")
    except Exception as e:
        await send(chat, f"Changelog error: {e}")

# ============================================================
# v6.3 — Dashboard Re-Render
# ============================================================
async def handle_dashboard_render(chat, uid, args):
    if not args:
        await send(chat, "Usage: /dashboard_render &lt;build&gt;\nRe-generates HTML dashboard for a build.")
        return
    await typing(chat)
    try:
        dr = cd_classes.get("DashboardReRender")
        if not dr:
            await send(chat, "DashboardReRender not loaded")
            return
        build = {"name": args, "components": {}, "description": args, "total_price": 0}
        filepath = os.path.join(DIR, f"dashboard_{uid}.html")
        ok = dr.render_to_file(build, filepath)
        if ok and os.path.exists(filepath):
            size = os.path.getsize(filepath)
            await send(chat, f"<b>Dashboard re-rendered!</b>\nFile: <code>dashboard_{uid}.html</code>\nSize: {size} bytes")
        else:
            await send(chat, "Dashboard render failed")
    except Exception as e:
        await send(chat, f"Dashboard render error: {e}")

# ============================================================
# v6.3 — Indonesian Build Instructions
# ============================================================
async def handle_idbuild(chat, uid, args):
    if not args:
        await send(chat, "Usage: /idbuild &lt;build&gt;\nGenerate Indonesian language build instructions.\nContoh: /idbuild rakitan hacking portabel")
        return
    await typing(chat)
    try:
        it = cd_classes.get("IndonesianTranslator")
        if not it:
            await send(chat, "IndonesianTranslator not loaded")
            return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate a build with Indonesian components for: {args}. Use IDR prices (Rp). Return JSON with name, components dict, total_price_idr, and steps list. Components should have price_idr field."})
        reply = await call_ai(_sessions[str(uid)][-10:])
        build = {"name": args, "components": {}, "total_price_idr": 0}
        result = it.format_build(build)
        await send(chat, result)
    except Exception as e:
        await send(chat, f"ID build error: {e}")

# ============================================================
# v6.3 — ISA Architecture Guide
# ============================================================
async def handle_isa(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("ESPRESSIF_ISA_DATABASE")
        if not db:
            await send(chat, "ISA database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>ESP32 ISA Architecture Guide</b>\n"]
            for isa_name, info in db.items():
                chips = ", ".join(info.get("chips", [])[:5])
                lines.append(f"<b>{isa_name}:</b> {chips}...")
                lines.append(f"  Features: {', '.join(info.get('features', [])[:3])}")
                lines.append(f"  Firmware: {', '.join(info.get('firmware_compat', [])[:4])}\n")
            lines.append("Usage: /isa &lt;xtensa|lx6|lx7|riscv&gt; — view details")
            await send(chat, "\n".join(lines))
            return
        query = parts[0]
        if query in ("xtensa", "lx6"):
            info = db.get("XTensa LX6")
            if info:
                await send(chat, f"<b>XTensa LX6</b>\nChips: {', '.join(info['chips'])}\nFeatures: {', '.join(info['features'])}\nFirmware: {', '.join(info['firmware_compat'])}")
        elif query in ("lx7", "xtensa_lx7"):
            info = db.get("XTensa LX7")
            if info:
                await send(chat, f"<b>XTensa LX7</b>\nChips: {', '.join(info['chips'])}\nFeatures: {', '.join(info['features'])}\nFirmware: {', '.join(info['firmware_compat'])}")
        elif query in ("riscv", "risc-v"):
            info = db.get("RISC-V")
            if info:
                await send(chat, f"<b>RISC-V</b>\nChips: {', '.join(info['chips'])}\nFeatures: {', '.join(info['features'])}\nFirmware: {', '.join(info['firmware_compat'])}")
        else:
            await send(chat, f"Unknown ISA: {query}. Options: xtensa, lx6, lx7, riscv")
    except Exception as e:
        await send(chat, f"ISA error: {e}")

# ============================================================
# v6.3 — Bruce Firmware
# ============================================================
async def handle_bruce(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("BRUCE_FIRMWARE_DATABASE")
        if not db:
            await send(chat, "Bruce firmware database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>Bruce Firmware Builds</b>\n"]
            for bid, info in db.items():
                lines.append(f"<b>{info['name']}</b> — ${info['price']}")
                lines.append(f"  Chip: {info['chip']} | Build: {info['build_time_hours']}h")
                lines.append(f"  Features: {', '.join(info['features'][:5])}")
                lines.append(f"  Best for: {', '.join(info['best_for'])}\n")
            lines.append("Usage: /bruce &lt;s3|c6|classic&gt; — view details")
            await send(chat, "\n".join(lines))
        else:
            key = f"bruce_esp32{parts[0]}" if parts[0] in ("s3", "c6") else f"bruce_{parts[0]}"
            if key not in db:
                key = parts[0]
            info = db.get(key)
            if info:
                await send(chat, f"<b>{info['name']}</b>\nChip: {info['chip']}\nFirmware: {info['firmware']}\nDisplay: {info['display']}\nStorage: {info['storage']}\nPrice: ${info['price']}\nBuild time: {info['build_time_hours']}h\n\nFeatures: {', '.join(info['features'])}\nBest for: {', '.join(info['best_for'])}")
            else:
                await send(chat, f"Unknown: {args}. See /bruce for builds.")
    except Exception as e:
        await send(chat, f"Bruce error: {e}")

# ============================================================
# v6.3 — GR3ML1N Template
# ============================================================
async def handle_gr3ml1n(chat, uid, args):
    await typing(chat)
    try:
        tmpl = cd_classes.get("GR3ML1N_TEMPLATE")
        if not tmpl:
            await send(chat, "GR3ML1N template not loaded")
            return
        lines = [f"<b>{tmpl['name']}</b>", f"Author: {tmpl['author']}", f"Inspiration: {tmpl['inspiration_url']}", "",
                 f"<b>SBC:</b> {tmpl['sbc']}", f"<b>Controller:</b> {tmpl['controller']}", f"<b>Keyboard:</b> {tmpl['keyboard']}", f"<b>Display:</b> {tmpl['display']}", f"<b>Enclosure:</b> {tmpl['enclosure']}", f"<b>Firmware:</b> {tmpl['firmware']}", f"<b>Battery:</b> {tmpl['battery']}", "",
                 f"<b>Total price:</b> ${tmpl['total_price']}", f"<b>Build time:</b> {tmpl['build_time_hours']}h", "",
                 "<b>Pros:</b>"] + [f"  + {p}" for p in tmpl['pros']] + ["", "<b>Cons:</b>"] + [f"  - {c}" for c in tmpl['cons']] + ["", f"<b>Best for:</b> {', '.join(tmpl['best_for'])}"]
        await send(chat, "\n".join(lines))
    except Exception as e:
        await send(chat, f"GR3ML1N error: {e}")

# ============================================================
# v6.3 — Homebrew OS
# ============================================================
async def handle_homebrew_os(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("HOMEBREW_OS_DATABASE")
        if not db:
            await send(chat, "Homebrew OS database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>Homebrew OS Cards</b>\n"]
            for oid, info in db.items():
                lines.append(f"<b>{info['name']}</b> — ${info['price']}")
                lines.append(f"  Platform: {info['platform']}")
                lines.append(f"  Features: {', '.join(info['features'][:4])}")
                lines.append(f"  Best for: {', '.join(info['best_for'])}\n")
            lines.append("Usage: /homebrew_os &lt;solar|micro_journal&gt;")
            await send(chat, "\n".join(lines))
        else:
            info = db.get(parts[0])
            if info:
                await send(chat, f"<b>{info['name']}</b>\nPlatform: {info['platform']}\nOS: {info['os']}\nDisplay: {info['display']}\nInput: {info['input']}\nBattery: {info['battery']}\nAuthor: {info['author']}\nRepo: {info['repo']}\nPrice: ${info['price']}\n\nFeatures: {', '.join(info['features'])}\nBest for: {', '.join(info['best_for'])}")
            else:
                await send(chat, f"Unknown: {args}. See /homebrew_os for list.")
    except Exception as e:
        await send(chat, f"Homebrew OS error: {e}")

# ============================================================
# v6.3 — Edge AI
# ============================================================
async def handle_edgeai(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("EDGE_AI_DATABASE")
        if not db:
            await send(chat, "Edge AI database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>Edge AI Configs (ESP32-S3)</b>\n"]
            for eid, info in db.items():
                lines.append(f"<b>{info['name']}</b> — ${info['price']}")
                lines.append(f"  Framework: {info['framework']}")
                lines.append(f"  RAM: {info['ram_needed']} | FPS: {info['fps']}")
                lines.append(f"  Capabilities: {', '.join(info['capabilities'][:4])}\n")
            lines.append("Usage: /edgeai &lt;vision|audio|espdl|impulse&gt;")
            await send(chat, "\n".join(lines))
        else:
            lookup = {"vision": "tensorflow_micro_vision", "audio": "tensorflow_micro_audio", "espdl": "esp_dl", "impulse": "edge_impulse"}
            key = lookup.get(parts[0], parts[0])
            info = db.get(key)
            if info:
                await send(chat, f"<b>{info['name']}</b>\nPlatform: {info['platform']}\nFramework: {info['framework']}\nRAM: {info['ram_needed']}\nFPS: {info['fps']}\nPrice: ${info['price']}\n\nCapabilities: {', '.join(info['capabilities'])}\nBest for: {', '.join(info['best_for'])}")
            else:
                await send(chat, f"Unknown: {args}. See /edgeai for list.")
    except Exception as e:
        await send(chat, f"Edge AI error: {e}")

# ============================================================
# v6.3 — ESP-NOW / Mesh
# ============================================================
async def handle_espnow(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("ESP_NOW_DATABASE")
        if not db:
            await send(chat, "ESP-NOW database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>ESP-NOW & Mesh Networking</b>\n"]
            for nid, info in db.items():
                lines.append(f"<b>{info['protocol']}</b> ({info['type']})")
                lines.append(f"  Range: {info['range']} | Band: {info['band']} | Throughput: {info['throughput']}")
                lines.append(f"  Power: {info['power']} | Price: ${info['price']}")
                lines.append(f"  Pros: {', '.join(info['pros'][:3])}")
                lines.append(f"  Best for: {', '.join(info['best_for'])}\n")
            lines.append("Usage: /espnow &lt;now|mesh|lora&gt;")
            await send(chat, "\n".join(lines))
        else:
            lookup = {"now": "esp_now_mesh", "mesh": "esp_mesh_lite", "lora": "lora_mesh"}
            key = lookup.get(parts[0], parts[0])
            info = db.get(key)
            if info:
                await send(chat, f"<b>{info['protocol']}</b> ({info['type']})\nRange: {info['range']}\nBand: {info['band']}\nThroughput: {info['throughput']}\nPower: {info['power']}\nPrice: ${info['price']}\n\nESP Compat: {', '.join(info['esp_compat'])}\nUse cases: {', '.join(info['use_cases'])}\nPros: {', '.join(info['pros'])}\nCons: {', '.join(info['cons'])}\nBest for: {', '.join(info['best_for'])}")
            else:
                await send(chat, f"Unknown: {args}. See /espnow for list.")
    except Exception as e:
        await send(chat, f"ESP-NOW error: {e}")

# ============================================================
# v6.3 — WiFi/BLE Scanner
# ============================================================
async def handle_wifi_scan(chat, uid, args):
    await typing(chat)
    try:
        db = cd_classes.get("WIFI_BLE_SCANNER_DATABASE")
        if not db:
            await send(chat, "WiFi/BLE scanner database not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = ["<b>WiFi/BLE Scanner Presets</b>\n"]
            for sid, info in db.items():
                lines.append(f"<b>{info['name']}</b> — ${info['price']}")
                lines.append(f"  Firmware: {info['firmware']}")
                lines.append(f"  Features: {', '.join(info['features'][:4])}")
                lines.append(f"  Best for: {', '.join(info['best_for'])}\n")
            lines.append("Usage: /wifi_scan &lt;wardrive|ble|spectrum|sniffer&gt;")
            await send(chat, "\n".join(lines))
        else:
            lookup = {"wardrive": "wardriving_esp32", "ble": "ble_scanner", "spectrum": "spectrum_analyzer", "sniffer": "packet_sniffer"}
            key = lookup.get(parts[0], parts[0])
            info = db.get(key)
            if info:
                await send(chat, f"<b>{info['name']}</b>\nFirmware: {info['firmware']}\nHardware: {info['hardware']}\nOutput: {info['output']}\nPrice: ${info['price']}\n\nFeatures: {', '.join(info['features'])}\nBest for: {', '.join(info['best_for'])}")
            else:
                await send(chat, f"Unknown: {args}. See /wifi_scan for list.")
    except Exception as e:
        await send(chat, f"WiFi scan error: {e}")

# ============================================================
# v6.5 — Mesh Network Planner
# ============================================================
async def handle_mesh(chat, uid, args):
    await typing(chat)
    try:
        planner = cd_classes.get("MeshNetworkPlanner")
        if not planner:
            await send(chat, "MeshNetworkPlanner not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            lines = [
                "<b>Mesh Network Planner</b>\n",
                "Subcommands:",
                "  <code>/mesh hardware &lt;use_case&gt; [budget]</code> — Recommend LoRa hardware",
                "  <code>/mesh range &lt;freq&gt; &lt;power&gt; &lt;gain&gt; [env]</code> — Range calculation",
                "  <code>/mesh config &lt;protocol&gt; &lt;name&gt; &lt;role&gt; [region]</code> — Generate config",
                "  <code>/mesh plan &lt;nodes&gt; &lt;area_km2&gt; [env]</code> — Mesh topology plan",
                "  <code>/mesh freq [region]</code> — Frequency plan by region",
                "",
                "<b>Example:</b> /mesh range 915 20 2.5 urban",
                "<b>Example:</b> /mesh plan 10 25 rural",
                "<b>Example:</b> /mesh config meshtastic node1 router us",
            ]
            await send(chat, "\n".join(lines))
            return
        sub = parts[0]
        if sub == "hardware":
            use_case = parts[1] if len(parts) > 1 else "meshtastic"
            budget = parts[2] if len(parts) > 2 else "mid"
            await send(chat, planner.recommend_hardware(use_case, budget))
        elif sub == "range":
            if len(parts) < 4:
                await send(chat, "Usage: /mesh range &lt;freq_mhz&gt; &lt;tx_power_dbm&gt; &lt;antenna_gain_dbi&gt; [urban|rural|suburban]")
                return
            try:
                freq = int(parts[1])
                power = int(parts[2])
                gain = float(parts[3])
                env = parts[4] if len(parts) > 4 else "urban"
                if env not in ("urban", "rural", "suburban"):
                    env = "urban"
                r = planner.calculate_range(freq, power, gain, env)
                lines = [
                    f"<b>Range Calculation — {freq}MHz @ {power}dBm</b>\n",
                    f"Environment: {env.title()}",
                    f"Antenna gain: {gain}dBi",
                    f"Estimated range: <b>{r['range_km']} km</b>",
                    f"Fresnel zone: {r['fresnel_zone_m']}m",
                    f"Path loss: {r['path_loss_db']}dB",
                    f"",
                    f"<b>Recommendation:</b> {r['recommendation']}",
                ]
                await send(chat, "\n".join(lines))
            except ValueError as ve:
                await send(chat, f"Invalid number: {ve}. Usage: /mesh range &lt;freq&gt; &lt;power&gt; &lt;gain&gt; [env]")
        elif sub == "config":
            if len(parts) < 4:
                await send(chat, "Usage: /mesh config &lt;protocol&gt; &lt;node_name&gt; &lt;role&gt; [region]")
                return
            protocol = parts[1]
            node_name = parts[2]
            role = parts[3]
            region = parts[4] if len(parts) > 4 else "us"
            result = planner.generate_node_config(protocol, node_name, role, region)
            if len(result) > 4000:
                chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
                for chunk in chunks:
                    await send(chat, f"<code>{chunk}</code>")
            else:
                await send(chat, f"<code>{result}</code>")
        elif sub == "plan":
            if len(parts) < 3:
                await send(chat, "Usage: /mesh plan &lt;node_count&gt; &lt;area_km2&gt; [urban|rural|suburban]")
                return
            try:
                node_count = int(parts[1])
                area_km2 = float(parts[2])
                env = parts[3] if len(parts) > 3 else "urban"
                if env not in ("urban", "rural", "suburban"):
                    env = "urban"
                await send(chat, planner.plan_mesh_network(node_count, area_km2, env))
            except ValueError as ve:
                await send(chat, f"Invalid number: {ve}. Usage: /mesh plan &lt;nodes&gt; &lt;area&gt; [env]")
        elif sub == "freq":
            region = parts[1] if len(parts) > 1 else "us"
            plan = planner.frequency_plan(region)
            if "error" in plan:
                avail = ", ".join(plan.get("available", []))
                await send(chat, f"Unknown region: {region}. Available: {avail}")
                return
            lines = [f"<b>Frequency Plan: {plan['region']}</b>\n"]
            for b in plan["bands"]:
                lines.append(f"Frequency: {b['freq']}MHz — {b['label']}")
                lines.append(f"Channels: {b['channels']}")
                lines.append(f"Max TX power: {b['tx_power_max']}dBm")
                lines.append(f"Duty cycle: {b['duty_cycle']}")
                lines.append(f"Notes: {b['notes']}")
            lines.append(f"\nDefault channel: {plan['default_channel']}")
            lines.append(f"LoRaWAN plan: {plan['lorawan']}")
            await send(chat, "\n".join(lines))
        else:
            await send(chat, f"Unknown subcommand: {sub}. See /mesh for list.")
    except Exception as e:
        await send(chat, f"Mesh error: {e}")

# ============================================================
# v6.5 — BOM Tracker (Live BOM & Cost)
# ============================================================
async def handle_bomtrack(chat, uid, args):
    await typing(chat)
    try:
        tracker = cd_classes.get("BOMTracker")
        if not tracker:
            await send(chat, "BOMTracker not loaded")
            return
        parts = args.strip().split()
        if not parts:
            lines = [
                "<b>BOM Tracker</b>\n",
                "Subcommands:",
                "  <code>/bomtrack generate &lt;category&gt; [tier]</code> — Generate BOM",
                "  <code>/bomtrack save &lt;name&gt; &lt;category&gt; [tier]</code> — Save BOM project",
                "  <code>/bomtrack load &lt;name&gt;</code> — Load saved BOM",
                "  <code>/bomtrack list</code> — List saved projects",
                "  <code>/bomtrack compare &lt;a&gt; &lt;b&gt;</code> — Compare two BOMs",
                "  <code>/bomtrack alternatives &lt;component&gt; &lt;max_price&gt;</code> — Find alternatives",
                "  <code>/bomtrack tiers</code> — Show price tier info",
                "",
                "Categories: writerdeck, pentest_kali, offgrid_survival, cosplay_prop, retro_gaming, ai_lab, media_server, research_station, security_audit",
                "Tiers: budget, standard (default), premium",
            ]
            await send(chat, "\n".join(lines))
            return
        sub = parts[0].lower()
        if sub == "generate":
            if len(parts) < 2:
                await send(chat, "Usage: /bomtrack generate &lt;category&gt; [tier]\nExample: /bomtrack generate writerdeck premium")
                return
            category = parts[1]
            tier = parts[2].lower() if len(parts) > 2 else "standard"
            if tier not in ("budget", "standard", "premium"):
                tier = "standard"
            bom = tracker.generate_bom(category, tier)
            if "error" in bom:
                avail = ", ".join(bom.get("available", []))
                await send(chat, f"Error: {bom['error']}\nAvailable: {avail}")
                return
            lines = [f"<b>BOM: {category.title()} ({tier})</b>\n"]
            lines.append(f"{'Item':<35} {'Qty':<6} {'Unit Price':<12} {'Total':<10}")
            lines.append("-" * 63)
            for item in bom["items"]:
                lines.append(f"{item['name']:<35} {item['qty']:<6} ${item['unit_price']:<8.2f} ${item['total']:<6.2f}")
            lines.append("")
            lines.append(f"{'SUBTOTAL':>53} ${bom['subtotal']:.2f}")
            lines.append(f"{'Tax (8%)':>53} ${bom['tax']:.2f}")
            lines.append(f"{'Shipping':>53} ${bom['shipping']:.2f}")
            lines.append(f"{'GRAND TOTAL':>53} ${bom['grand_total']:.2f}")
            lines.append("")
            lines.append(f"<i>Tier: {tier} — {bom['tier_description']}</i>")
            lines.append("")
            lines.append("<b>Savings Tips:</b>")
            for tip in bom["savings_tips"]:
                lines.append(f"  \u2022 {tip}")
            await send(chat, "\n".join(lines))
        elif sub == "save":
            if len(parts) < 3:
                await send(chat, "Usage: /bomtrack save &lt;name&gt; &lt;category&gt; [tier]\nExample: /bomtrack save mybuild writerdeck premium")
                return
            name = parts[1]
            category = parts[2]
            tier = parts[3].lower() if len(parts) > 3 else "standard"
            if tier not in ("budget", "standard", "premium"):
                tier = "standard"
            bom = tracker.generate_bom(category, tier)
            if "error" in bom:
                await send(chat, f"Error: {bom['error']}")
                return
            result = tracker.save_project(name, bom)
            await send(chat, result)
        elif sub == "load":
            if len(parts) < 2:
                await send(chat, "Usage: /bomtrack load &lt;name&gt;\nExample: /bomtrack load mybuild")
                return
            name = parts[1]
            data = tracker.load_project(name)
            if "error" in data:
                msg = f"Error: {data['error']}"
                if "saved" in data:
                    msg += f"\nSaved projects: {', '.join(data['saved'])}"
                await send(chat, msg)
                return
            bom = data.get("bom", {})
            lines = [f"<b>Project: {name}</b>\n"]
            lines.append(f"Saved: {data.get('saved_at', '?')}")
            lines.append(f"Tier: {bom.get('tier', '?')}")
            lines.append(f"Grand total: ${bom.get('grand_total', 0):.2f}")
            lines.append(f"Items: {len(bom.get('items', []))}")
            lines.append("")
            for item in bom.get("items", []):
                lines.append(f"  \u2022 {item['name']} x{item['qty']} — ${item['total']:.2f}")
            await send(chat, "\n".join(lines))
        elif sub == "list":
            await send(chat, tracker.list_projects())
        elif sub == "compare":
            if len(parts) < 3:
                await send(chat, "Usage: /bomtrack compare &lt;project_a&gt; &lt;project_b&gt;\nExample: /bomtrack compare build1 build2")
                return
            result = tracker.compare_boms(parts[1], parts[2])
            await send(chat, result)
        elif sub == "alternatives":
            if len(parts) < 3:
                await send(chat, "Usage: /bomtrack alternatives &lt;component&gt; &lt;max_price&gt;\nExample: /bomtrack alternatives display 50")
                return
            try:
                max_price = int(parts[2])
                await send(chat, tracker.find_alternatives(parts[1], max_price))
            except ValueError:
                await send(chat, "Max price must be a number. Usage: /bomtrack alternatives &lt;component&gt; &lt;max_price&gt;")
        elif sub == "tiers":
            await send(chat, tracker.price_tier_info())
        else:
            await send(chat, f"Unknown subcommand: {sub}. See /bomtrack for list.")
    except Exception as e:
        await send(chat, f"BOM track error: {e}")

# ============================================================
# v6.5 — Build Profile Manager
# ============================================================
async def handle_profile(chat, uid, args):
    await typing(chat)
    try:
        mgr = cd_classes.get("BuildProfileManager")
        if not mgr:
            await send(chat, "BuildProfileManager not loaded")
            return
        parts = args.strip().split()
        if not parts:
            await send(chat, mgr.list_profiles())
            return
        if parts[0].lower() == "apply":
            if len(parts) < 2:
                await send(chat, "Usage: /profile apply &lt;profile_name&gt;\nExample: /profile apply writerdeck")
                return
            result = mgr.apply_profile_config(parts[1])
            if "error" in result:
                await send(chat, f"Error: {result['error']}")
                return
            lines = [f"<b>Profile Config Overrides: {result['profile']}</b>\n"]
            lines.append("<b>SBC Filter:</b>")
            for k, v in result["sbc_filter"].items():
                lines.append(f"  {k}: {v}")
            lines.append("")
            lines.append("<b>Display Filter:</b>")
            for k, v in result["display_filter"].items():
                lines.append(f"  {k}: {v}")
            lines.append("")
            lines.append("<b>Battery Filter:</b>")
            for k, v in result["battery_filter"].items():
                lines.append(f"  {k}: {v}")
            lines.append("")
            lines.append(f"<b>OS:</b> {result['os_config']['os']} (Cooling: {result['os_config']['cooling']})")
            lines.append("")
            lines.append("<b>Aesthetic Config:</b>")
            for k, v in result["aesthetic_config"].items():
                lines.append(f"  {k}: {v}")
            await send(chat, "\n".join(lines))
        elif parts[0].lower() == "compare":
            if len(parts) < 3:
                await send(chat, "Usage: /profile compare &lt;profile_a&gt; &lt;profile_b&gt;\nExample: /profile compare writerdeck pentest_kali")
                return
            await send(chat, mgr.compare_profiles(parts[1], parts[2]))
        elif parts[0].lower() == "suggest":
            if len(parts) < 2:
                await send(chat, "Usage: /profile suggest &lt;description&gt;\nExample: /profile suggest I want a portable AI machine")
                return
            desc = " ".join(parts[1:])
            await send(chat, mgr.suggest_profile_for_description(desc))
        else:
            name = parts[0]
            profile = mgr.get_profile(name)
            if "error" in profile:
                avail = ", ".join(profile.get("available", []))
                await send(chat, f"Unknown profile: {name}\nAvailable: {avail}")
                return
            lines = [
                f"<b>{profile['name']}</b>",
                f"{profile['description']}\n",
                f"<b>SBC:</b> {profile['sbc_recommendation']}",
                f"<b>Display:</b> {profile['display_size_inches']}\"",
                f"<b>Battery:</b> {profile['battery_min_wh']}Wh min",
                f"<b>OS:</b> {profile['os_recommendation']}",
                f"<b>Case:</b> {profile['case_style']}",
                f"<b>Keyboard:</b> {profile['keyboard_type']}",
                f"<b>Cooling:</b> {'Required' if profile['cooling_required'] else 'Passive'}",
                f"<b>RAM:</b> {profile['ram_min_gb']}GB min",
                f"<b>Storage:</b> {profile['storage_min_gb']}GB min",
                f"<b>Weight target:</b> {profile['weight_target_kg']}kg",
                f"\n<b>Vibe:</b> {profile['aesthetic_vibe']}",
                f"<b>Colors:</b> {profile['color_palette']}",
                f"<b>LED:</b> <code>{profile['led_accent_color']}</code>",
                f"<b>Switches:</b> {profile['switches']}",
                f"\n<i>{profile['notes']}</i>",
            ]
            await send(chat, "\n".join(lines))
    except Exception as e:
        await send(chat, f"Profile error: {e}")

# ============================================================
# Main Loop
# ============================================================
# v6.5 — Ollama AI Integration
# ============================================================
async def handle_ollama(chat, uid, args):
    await typing(chat)
    try:
        oa = cd_classes.get("OllamaAssistant")
        if not oa:
            await send(chat, "OllamaAssistant not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            models = oa.get_ollama_models()
            ram_groups = {}
            for mk in models:
                m = cd_classes.get("OLLAMA_MODEL_DATABASE", {}).get(mk)
                if m:
                    rg = m["ram_min_gb"]
                    ram_groups.setdefault(rg, []).append((mk, m))
            lines = ["<b>Available Ollama Models</b>\n"]
            for rg in sorted(ram_groups.keys()):
                lines.append(f"<b>≤{rg}GB RAM:</b>")
                for mk, m in ram_groups[rg]:
                    lines.append(f"  <code>{mk}</code> — {m['tokens_sec_est']} tok/s — {', '.join(m['best_for'][:3])}")
                lines.append("")
            lines.append("Usage: /ollama recommend &lt;sbc&gt; | /ollama setup &lt;model&gt; | /ollama quantize &lt;model&gt; &lt;ram&gt; | /ollama models &lt;sbc&gt;")
            await send(chat, "\n".join(lines))
            return
        cmd = parts[0]
        if cmd == "recommend" and len(parts) > 1:
            result = oa.recommend_model(parts[1])
            await send(chat, result)
        elif cmd == "setup" and len(parts) > 1:
            sbc = parts[2] if len(parts) > 2 else "generic_sbc"
            result = oa.generate_setup_cmds(parts[1], sbc)
            await send(chat, result)
        elif cmd == "quantize" and len(parts) > 2:
            try:
                ram = int(parts[2])
                result = oa.suggest_quantization(parts[1], ram)
                await send(chat, result)
            except ValueError:
                await send(chat, "RAM must be a number (GB). Usage: /ollama quantize &lt;model&gt; &lt;ram_gb&gt;")
        elif cmd == "models" and len(parts) > 1:
            db = cd_classes.get("OLLAMA_MODEL_DATABASE", {})
            sbc_tiers = {"rpi5_8gb": 8, "rpi5_16gb": 16, "jetson_orin_nano": 8, "orangepi5_max": 16, "rock5b": 16, "radxa_zero3": 4}
            avail_ram = sbc_tiers.get(parts[1], 8)
            compat = [(mk, m) for mk, m in db.items() if m["ram_min_gb"] <= avail_ram]
            if compat:
                lines = [f"<b>Models workable on {parts[1]} ({avail_ram}GB):</b>\n"]
                for mk, m in sorted(compat, key=lambda x: -x[1]["size_b"]):
                    lines.append(f"  <code>{mk}</code> — {m['name']} ({m['size_b']}B) ~{m['tokens_sec_est']} tok/s")
                await send(chat, "\n".join(lines))
            else:
                await send(chat, f"No models fit in {avail_ram}GB for {parts[1]}")
        else:
            await send(chat, "Usage: /ollama recommend &lt;sbc&gt; | /ollama setup &lt;model&gt; [sbc] | /ollama quantize &lt;model&gt; &lt;ram&gt; | /ollama models &lt;sbc&gt;")
    except Exception as e:
        await send(chat, f"Ollama error: {e}")

# ============================================================
# v6.5 — Kiwix/ZIM Knowledge Base
# ============================================================
async def handle_kiwix(chat, uid, args):
    await typing(chat)
    try:
        kb = cd_classes.get("KiwixKnowledgeBase")
        if not kb:
            await send(chat, "KiwixKnowledgeBase not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            purposes = list(cd_classes.get("BUILD_PURPOSE_ZIM_MAP", {}).keys())
            lines = ["<b>Kiwix ZIM Knowledge Base</b>\n", "<b>Available purposes:</b>"]
            for p in purposes:
                lines.append(f"  • <code>{p}</code>: {', '.join(cd_classes['BUILD_PURPOSE_ZIM_MAP'][p][:3])}...")
            lines.append("")
            lines.append("Usage: /kiwix &lt;purpose&gt; | /kiwix install &lt;zims...&gt; | /kiwix rag &lt;model&gt; &lt;zims...&gt; | /kiwix list")
            await send(chat, "\n".join(lines))
            return
        cmd = parts[0]
        if cmd == "install":
            zids = parts[1:]
            if not zids:
                await send(chat, "Usage: /kiwix install &lt;zim_id1&gt; [zim_id2 ...]")
                return
            result = kb.generate_install_cmds(zids)
            await send(chat, result)
        elif cmd == "rag" and len(parts) > 2:
            model_key = parts[1]
            zids = parts[2:]
            result = kb.setup_rag_cmds(model_key, zids)
            await send(chat, result)
        elif cmd == "list":
            result = kb.list_zims()
            await send(chat, result[:4000])
        else:
            purpose = parts[0]
            result = kb.recommend_for_purpose(purpose)
            await send(chat, result[:4000])
    except Exception as e:
        await send(chat, f"Kiwix error: {e}")

# ============================================================
# v6.5 — Parametric Enclosure Generator
# ============================================================
async def handle_enclosure(chat, uid, args):
    await typing(chat)
    try:
        peg = cd_classes.get("ParametricEnclosureGenerator")
        if not peg:
            await send(chat, "ParametricEnclosureGenerator not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            styles = peg.style_presets()
            mats = cd_classes.get("ENCLOSURE_MATERIAL_DATABASE", {})
            lines = ["<b>Parametric Enclosure Generator</b>\n", "<b>Styles:</b>"]
            for sid, s in styles.items():
                lines.append(f"  • <code>{sid}</code>: {s['name']} — {s['description'][:50]}")
            lines.append("", "<b>Materials:</b>")
            for mid, m in mats.items():
                lines.append(f"  • <code>{mid}</code>: {m['name']} — {m['strength']}")
            lines.append("", "Usage: /enclosure dimensions &lt;sbc&gt; [display] [battery]")
            lines.append("       /enclosure generate &lt;sbc&gt; [display] [battery] [material] [style] [nato] [vents]")
            lines.append("       /enclosure materials | /enclosure styles")
            await send(chat, "\n".join(lines))
            return
        cmd = parts[0]
        if cmd == "dimensions":
            sbc = parts[1] if len(parts) > 1 else "rpi5"
            disp = parts[2] if len(parts) > 2 else "hdmi7"
            batt = parts[3] if len(parts) > 3 else "npf550"
            dims = peg.compute_enclosure_dimensions(sbc, disp, batt)
            await send(chat, f"<b>Enclosure Dimensions</b>\nSBC: {sbc} | Display: {disp} | Battery: {batt}\n\nWidth: {dims['width_mm']}mm\nDepth: {dims['depth_mm']}mm\nHeight: {dims['height_mm']}mm\nWall: {dims['wall_thickness_mm']}mm\nVolume: {dims['volume_cm3']}cm³")
        elif cmd == "generate":
            sbc = parts[1] if len(parts) > 1 else "rpi5"
            disp = parts[2] if len(parts) > 2 else "hdmi7"
            batt = parts[3] if len(parts) > 3 else "npf550"
            mat = parts[4] if len(parts) > 4 else "pla"
            sty = parts[5] if len(parts) > 5 else "minimal"
            nato = "nato" in parts or "rails" in args
            vents = not ("novents" in args or "novent" in args)
            ant = "antenna" in args
            scad = peg.generate_openscad(sbc, disp, batt, mat, sty, nato, vents, ant)
            scad_esc = scad.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            await send(chat, f"<b>OpenSCAD Enclosure</b>\nSBC: {sbc} | Display: {disp} | Battery: {batt}\nMaterial: {mat} | Style: {sty}\nNATO rails: {nato} | Vents: {vents} | Antenna mount: {ant}\n\n<pre>{scad_esc[:3800]}</pre>")
        elif cmd == "materials":
            mats = cd_classes.get("ENCLOSURE_MATERIAL_DATABASE", {})
            lines = ["<b>Enclosure Materials</b>\n"]
            for mid, m in mats.items():
                lines.append(f"<b>{m['name']}</b> (<code>{mid}</code>)")
                lines.append(f"  Print: {m['print_temp_c']}°C | Bed: {m['bed_temp_c']}°C")
                lines.append(f"  Strength: {m['strength']} | Flexible: {'Yes' if m['flexible'] else 'No'}")
                lines.append(f"  Best for: {', '.join(m['best_for'][:4])}")
                lines.append(f"  Notes: {m['notes']}\n")
            await send(chat, "\n".join(lines))
        elif cmd == "styles":
            styles = peg.style_presets()
            lines = ["<b>Enclosure Style Presets</b>\n"]
            for sid, s in styles.items():
                color_name = s["color_hex"]
                lines.append(f"<b>{s['name']}</b> (<code>{sid}</code>)")
                lines.append(f"  {s['description']}")
                lines.append(f"  Wall: {s['wall_thickness']}mm | Radius: {s['corner_radius']}mm")
                lines.append(f"  Color: {color_name} | Material: {s['material']}")
                lines.append(f"  Features: {', '.join(s['features']) if s['features'] else 'None'}\n")
            await send(chat, "\n".join(lines))
        else:
            await send(chat, "Usage: /enclosure dimensions|generate|materials|styles")
    except Exception as e:
        await send(chat, f"Enclosure error: {e}")


# ============================================================
# v6.5 — Power Monitor
# ============================================================
async def handle_power(chat, uid, args):
    await typing(chat)
    try:
        pm = cd_classes.get("PowerMonitor")
        if not pm:
            await send(chat, "PowerMonitor not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, """<b>Power Management Subcommands:</b>

<code>/power runtime &lt;wh&gt; [profile]</code> — Estimate runtime
<code>/power ups &lt;sbc&gt; &lt;hours&gt;</code> — Recommend UPS HAT
<code>/power shutdown [os]</code> — Safe shutdown script
<code>/power profiles</code> — Power profiles
<code>/power chemistry</code> — Battery chemistry
<code>/power hats</code> — List UPS HATs""")
            return
        sub = parts[0]
        if sub == "runtime":
            if len(parts) < 2:
                await send(chat, "Usage: /power runtime <wh> [profile]")
                return
            try:
                wh = float(parts[1])
            except ValueError:
                await send(chat, "battery_wh must be a number")
                return
            profile = parts[2] if len(parts) > 2 else "normal"
            result = pm.estimate_runtime(wh, profile)
            await send(chat, f"<b>Runtime Estimate</b>\n\nBattery: {result['battery_name']}\nProfile: {result['profile']}\nRuntime: <b>{result['hours']}h</b> ({result['minutes']} min)\n{result['notes']}")
        elif sub == "ups":
            if len(parts) < 3:
                await send(chat, "Usage: /power ups <sbc_key> <hours>")
                return
            try:
                hours = float(parts[2])
            except ValueError:
                await send(chat, "hours must be a number")
                return
            await send(chat, pm.recommend_ups(parts[1], hours))
        elif sub == "shutdown":
            os_key = parts[1] if len(parts) > 1 else "raspberry_pi_os"
            await send(chat, pm.generate_safe_shutdown_script(os_key))
        elif sub == "profiles":
            await send(chat, pm.power_profile_info())
        elif sub == "chemistry":
            await send(chat, pm.battery_chemistry_info())
        elif sub == "hats":
            await send(chat, pm.list_hats())
        else:
            await send(chat, f"Unknown subcommand: {sub}")
    except Exception as e:
        await send(chat, f"Power error: {e}")


# ============================================================
# v6.5 — OS Configurator
# ============================================================
async def handle_osconf(chat, uid, args):
    await typing(chat)
    try:
        oc = cd_classes.get("OSConfigurator")
        if not oc:
            await send(chat, "OSConfigurator not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            purposes = [f"<code>{p}</code>" for p in sorted(cd_classes.get("BUILD_OS_MAP", {}).keys())]
            await send(chat, f"""<b>OS Configuration Subcommands:</b>

<code>/osconf recommend &lt;purpose&gt; [sbc]</code> — Recommend OS
<code>/osconf script &lt;os&gt; &lt;purpose&gt;</code> — Post-install script
<code>/osconf list [filter]</code> — List OSes
<code>/osconf compare &lt;a&gt; &lt;b&gt;</code> — Compare two OSes
<code>/osconf docker &lt;os&gt; &lt;services&gt;</code> — Docker compose

<b>Known purposes:</b>
{', '.join(purposes)}""")
            return
        sub = parts[0]
        if sub == "recommend":
            if len(parts) < 2:
                await send(chat, "Usage: /osconf recommend <purpose> [sbc]")
                return
            sbc = parts[2] if len(parts) > 2 else ""
            await send(chat, oc.recommend_os(parts[1], sbc))
        elif sub == "script":
            if len(parts) < 3:
                await send(chat, "Usage: /osconf script <os_key> <purpose>")
                return
            await send(chat, oc.generate_post_install_script(parts[1], parts[2]))
        elif sub == "list":
            filt = " ".join(parts[1:]) if len(parts) > 1 else ""
            await send(chat, oc.list_oses(filt))
        elif sub == "compare":
            if len(parts) < 3:
                await send(chat, "Usage: /osconf compare <os_a> <os_b>")
                return
            await send(chat, oc.compare_oses(parts[1], parts[2]))
        elif sub == "docker":
            if len(parts) < 3:
                await send(chat, "Usage: /osconf docker <os_key> <service1> [service2] ...")
                return
            await send(chat, oc.generate_docker_compose(parts[1], parts[2:]))
        else:
            await send(chat, f"Unknown subcommand: {sub}")
    except Exception as e:
        await send(chat, f"OSConfig error: {e}")


# ============================================================
# v6.5 — Build Documentation Generator
# ============================================================
async def handle_builddoc(chat, uid, args):
    await typing(chat)
    try:
        bd = cd_classes.get("BuildDocGenerator")
        if not bd:
            await send(chat, "BuildDocGenerator not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, """<b>Build Documentation Subcommands:</b>

<code>/builddoc generate &lt;sbc&gt; &lt;display&gt; [battery] [case] [keyboard]</code> — Full build doc
<code>/builddoc wiring &lt;sbc&gt; &lt;display&gt;</code> — Wiring diagram only
<code>/builddoc reddit &lt;sbc&gt; &lt;display&gt;</code> — Reddit post template
<code>/builddoc hackaday &lt;sbc&gt; &lt;display&gt;</code> — Hackaday template""")
            return
        sub = parts[0]
        if sub in ("generate", "wiring", "reddit", "hackaday"):
            if len(parts) < 3:
                await send(chat, f"Usage: /builddoc {sub} <sbc_key> <display_key> [battery] [case] [keyboard]")
                return
            sbc_key = parts[1]
            display_key = parts[2]
            battery_key = parts[3] if len(parts) > 3 else ""
            case_key = parts[4] if len(parts) > 4 else ""
            keyboard_key = parts[5] if len(parts) > 5 else ""
            data = bd.gather_build_data(sbc_key, display_key, battery_key, case_key, keyboard_key)
            if sub == "generate":
                result = bd.generate_build_doc(data)
            elif sub == "wiring":
                result = "```\n" + bd.generate_wiring_diagram(data) + "\n```"
            elif sub == "reddit":
                result = bd.generate_reddit_post(data)
            elif sub == "hackaday":
                result = bd.generate_hackaday_template(data)
            await send(chat, result)
        else:
            await send(chat, f"Unknown subcommand: {sub}")
    except Exception as e:
        await send(chat, f"BuildDoc error: {e}")


# ============================================================
# v6.5 — SDR & Radio Integration
# ============================================================
async def handle_sdr(chat, uid, args):
    await typing(chat)
    try:
        sdr = cd_classes.get("SDRIntegration")
        if not sdr:
            await send(chat, "SDRIntegration not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, """<b>SDR & Radio Integration</b>

<code>/sdr hardware [use_case] [budget]</code> — Recommend SDR
<code>/sdr bands [filter]</code> — Frequency bands
<code>/sdr install &lt;sdr&gt; [os]</code> — Install script
<code>/sdr flow &lt;type&gt; &lt;freq_mhz&gt;</code> — GNU Radio flowgraph
<code>/sdr plan &lt;use_case&gt;</code> — Frequency plan
<code>/sdr interfaces</code> — SDR software list""")
            return
        cmd = parts[0]
        if cmd == "hardware":
            use_case = parts[1] if len(parts) > 1 else "general"
            budget = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 200
            await send(chat, sdr.recommend_sdr(use_case, budget))
        elif cmd == "bands":
            filt = parts[1] if len(parts) > 1 else ""
            filter_licensed = filt in ("licensed", "ham", "lic")
            await send(chat, sdr.list_bands(filter_licensed)[:4000])
        elif cmd == "install" and len(parts) > 1:
            os_key = parts[2] if len(parts) > 2 else "raspberry_pi_os"
            await send(chat, sdr.generate_install_script(parts[1], os_key)[:4000])
        elif cmd == "flow" and len(parts) > 2:
            try:
                freq = float(parts[2])
                await send(chat, sdr.generate_gnuradio_flowgraph(parts[1], freq)[:4000])
            except ValueError:
                await send(chat, "Frequency must be a number (MHz)")
        elif cmd == "plan" and len(parts) > 1:
            await send(chat, sdr.frequency_plan_for_use(parts[1])[:4000])
        elif cmd == "interfaces":
            await send(chat, sdr.list_interfaces()[:4000])
        else:
            await send(chat, "Usage: /sdr hardware|bands|install|flow|plan|interfaces")
    except Exception as e:
        await send(chat, f"SDR error: {e}")


# ============================================================
# v6.5 — Community Build Explorer
# ============================================================
async def handle_explore(chat, uid, args):
    await typing(chat)
    try:
        ce = cd_classes.get("CommunityExplorer")
        if not ce:
            await send(chat, "CommunityExplorer not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, ce.get_featured_builds()[:4000])
            return
        cmd = parts[0]
        if cmd == "tag" and len(parts) > 1:
            await send(chat, ce.explore_by_tag(" ".join(parts[1:]))[:4000])
        elif cmd == "source" and len(parts) > 1:
            await send(chat, ce.explore_by_source(parts[1])[:4000])
        elif cmd == "search" and len(parts) > 1:
            await send(chat, ce.search_builds(" ".join(parts[1:]))[:4000])
        elif cmd == "view" and len(parts) > 1:
            await send(chat, ce.get_build_details(parts[1])[:4000])
        elif cmd == "import" and len(parts) > 1:
            bom = ce.import_bom_as_starting_point(parts[1])
            if "error" in bom:
                await send(chat, bom["error"])
            else:
                lines = [f"<b>Import BOM: {bom['title']}</b>", ""]
                lines.append(f"<b>SBC:</b> {bom['sbc']}")
                lines.append(f"<b>Display:</b> {bom['display']}")
                lines.append(f"<b>Battery:</b> {bom['battery']}")
                lines.append(f"<b>Features:</b>")
                for f in bom["features"]:
                    lines.append(f"  - {f}")
                lines.append(f"\n<b>Estimated cost:</b> {bom['estimated_cost_tier']}")
                await send(chat, "\n".join(lines))
        elif cmd == "random":
            await send(chat, ce.random_build()[:4000])
        elif cmd == "tags":
            db = cd_classes.get("SAMPLE_COMMUNITY_BUILDS", {})
            tag_counts = {}
            for b in db.values():
                for t in b.get("tags", []):
                    tag_counts[t] = tag_counts.get(t, 0) + 1
            lines = ["<b>Build Tags</b>\n"]
            for tag in sorted(tag_counts.keys()):
                lines.append(f"  <code>{tag}</code> ({tag_counts[tag]} builds)")
            await send(chat, "\n".join(lines))
        else:
            await send(chat, "Usage: /explore tag|source|search|view|import|random|tags")
    except Exception as e:
        await send(chat, f"Explore error: {e}")


# ============================================================
# v6.5 — Aesthetic Style Engine
# ============================================================
async def handle_aesthetic(chat, uid, args):
    await typing(chat)
    try:
        ae = cd_classes.get("AestheticEngine")
        if not ae:
            await send(chat, "AestheticEngine not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, ae.list_styles()[:4000])
            return
        cmd = parts[0]
        if cmd == "apply" and len(parts) > 1:
            style_name = parts[1]
            category = "_".join(parts[2:]) if len(parts) > 2 else "custom_build"
            result = ae.apply_style_to_build(style_name, {"category": category, "name": category.replace("_", " ").title()})
            if "error" in result:
                await send(chat, result["error"])
            else:
                lines = [f"<b>Apply: {result['style']} to {category}</b>", ""]
                lines.append(f"<b>Case:</b> {result['build_components']['case']}")
                lines.append(f"<b>Keyboard:</b> {result['build_components']['keyboard']}")
                lines.append(f"<b>Lighting:</b> {result['build_components']['lighting']}")
                lines.append(f"<b>Cables:</b> {result['build_components']['cables']}")
                lines.append(f"<b>Switches:</b> {result['build_components']['switches']}")
                lines.append(f"<b>Display Bezel:</b> {result['build_components']['display_bezel']}")
                lines.append(f"<b>Font:</b> {result['font']}")
                lines.append(f"<b>Material:</b> {result['material']}")
                await send(chat, "\n".join(lines))
        elif cmd == "css" and len(parts) > 1:
            result = ae.generate_css_theme(parts[1])
            await send(chat, f"<pre>{result[:3900]}</pre>")
        elif cmd == "colors" and len(parts) > 1:
            await send(chat, ae.generate_case_colors(parts[1]))
        elif cmd == "suggest" and len(parts) > 1:
            await send(chat, ae.suggest_style_for_profile("_".join(parts[1:])))
        elif cmd == "mix" and len(parts) > 2:
            await send(chat, ae.mix_styles(parts[1], parts[2]))
        elif cmd == "compare" and len(parts) > 2:
            await send(chat, ae.compare_styles(parts[1], parts[2]))
        elif len(parts) == 1:
            style = ae.get_style(parts[0])
            if style:
                await send(chat, f"<b>{style['name']}</b>\n{style['description']}\n\nCase: <code>{style['case_color_hex']}</code> ({style['case_color_name']})\nLED: <code>{style['led_accent_hex']}</code>\nMaterial: {style['material_suggestion']}\nKeycaps: {style['keycap_style']}\nVibe: {style['vibe']}")
            else:
                await send(chat, f"Unknown style: {parts[0]}")
        else:
            await send(chat, "Usage: /aesthetic <style> | apply|css|colors|suggest|mix|compare")
    except Exception as e:
        await send(chat, f"Aesthetic error: {e}")


# ============================================================
# v7.0 — WriterDeck Mode
# ============================================================
async def handle_writerdeck(chat, uid, args):
    await typing(chat)
    try:
        wa = cd_classes.get("WriterDeckAdvisor")
        if not wa:
            await send(chat, "WriterDeckAdvisor not loaded")
            return
        parts = args.lower().strip().split()
        if not parts:
            await send(chat, wa.overview())
        elif parts[0] == "profile":
            budget = parts[1] if len(parts) > 1 else "mid"
            await send(chat, wa.profile(budget))
        elif parts[0] == "display":
            purpose = parts[1] if len(parts) > 1 else "all"
            await send(chat, wa.display_recs(purpose))
        elif parts[0] == "software":
            await send(chat, wa.software_recs())
        elif parts[0] == "os":
            await send(chat, wa.os_recs())
        elif parts[0] == "keyboard":
            await send(chat, wa.keyboard_recs())
        elif parts[0] == "tune":
            await send(chat, wa.tune())
        else:
            await send(chat, wa.overview())
    except Exception as e:
        await send(chat, f"WriterDeck error: {e}")


# ============================================================
# v7.0 — Thermal Management Designer
# ============================================================
async def handle_thermal(chat, uid, args):
    await typing(chat)
    try:
        td = cd_classes.get("ThermalDesigner")
        if not td:
            await send(chat, "ThermalDesigner not loaded")
            return
        parts = args.strip().split(maxsplit=2)
        if not parts:
            await send(chat, td.overview())
            return
        cmd = parts[0].lower()
        if cmd == "calc" and len(parts) >= 2:
            sbc = parts[1]
            load = int(parts[2]) if len(parts) > 2 else 100
            await send(chat, td.calc(sbc, load))
        elif cmd == "parts" and len(parts) >= 2:
            await send(chat, td.parts(parts[1]))
        elif cmd == "undervolt" and len(parts) >= 2:
            await send(chat, td.undervolt(parts[1]))
        elif cmd == "vent" and len(parts) >= 2:
            await send(chat, td.vent(parts[1]))
        elif cmd == "compare":
            await send(chat, td.compare())
        else:
            await send(chat, td.overview())
    except Exception as e:
        await send(chat, f"Thermal error: {e}")


# ============================================================
# v7.0 — Multi-Build Comparator
# ============================================================
_build_comparator = None

def _get_comparator():
    global _build_comparator
    if _build_comparator is None:
        BC = cd_classes.get("BuildComparator")
        if BC:
            _build_comparator = BC()
    return _build_comparator

async def handle_compare(chat, uid, args):
    await typing(chat)
    try:
        bc = _get_comparator()
        if not bc:
            await send(chat, "BuildComparator not loaded")
            return
        parts = args.strip().split()
        if not parts:
            s = bc.selection()
            if "No builds selected" in s:
                s += "\n\nUsage: /compare add <build_id> | /compare add3 <id1> <id2> <id3> | /compare score | /compare clear"
            await send(chat, s)
            return
        cmd = parts[0].lower()
        if cmd == "add" and len(parts) > 1:
            await send(chat, bc.add(parts[1]))
        elif cmd == "add3" and len(parts) > 3:
            r = []
            for i in range(1, 4):
                r.append(bc.add(parts[i]))
            await send(chat, "\n".join(r))
        elif cmd == "remove" and len(parts) > 1:
            await send(chat, bc.remove(parts[1]))
        elif cmd == "score":
            bid = parts[1] if len(parts) > 1 else None
            await send(chat, bc.score(bid))
        elif cmd == "clear":
            await send(chat, bc.clear())
        elif cmd == "compare":
            await send(chat, bc.compare_builds())
        elif cmd == "metrics":
            await send(chat, bc.metric_defs())
        else:
            result = bc.compare_builds()
            if "Select at least 2 builds" in result:
                result += "\n\nUsage: /compare add <id1> <id2>"
            await send(chat, result)
    except Exception as e:
        await send(chat, f"Compare error: {e}")


# ============================================================
# v7.0 — Build Cost Optimizer
# ============================================================
async def handle_cost(chat, uid, args):
    await typing(chat)
    try:
        co = cd_classes.get("CostOptimizer")
        if not co:
            await send(chat, "CostOptimizer not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, co.overview())
            return
        cmd = parts[0].lower()
        budgets = cd_classes.get("BUDGET_TEMPLATES", {})
        if cmd in budgets:
            await send(chat, co.budget_template(cmd))
        elif cmd == "parts" and len(parts) > 1:
            await send(chat, co.part_prices(parts[1]))
        elif cmd == "alternate" and len(parts) > 1:
            await send(chat, co.alternate(parts[1]))
        elif cmd == "regions" and len(parts) > 1:
            await send(chat, co.regions(parts[1]))
        else:
            t = co.budget_template(cmd)
            if "Unknown tier" in t:
                await send(chat, co.overview())
            else:
                await send(chat, t)
    except Exception as e:
        await send(chat, f"Cost error: {e}")


# ============================================================
# v7.0 — Upgrade Path Analyzer
# ============================================================
async def handle_upgrade(chat, uid, args):
    await typing(chat)
    try:
        ua = cd_classes.get("UpgradeAdvisor")
        if not ua:
            await send(chat, "UpgradeAdvisor not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, ua.overview())
            return
        cmd = parts[0].lower()
        if cmd in ("sbc", "display", "battery", "memory"):
            await send(chat, ua.list_upgrades(cmd))
        elif cmd == "list":
            await send(chat, ua.list_upgrades())
        elif cmd in cd_classes.get("SAMPLE_COMMUNITY_BUILDS", {}) or any(cmd in k for k in cd_classes.get("SAMPLE_COMMUNITY_BUILDS", {})):
            bid = cmd
            builds_db = cd_classes.get("SAMPLE_COMMUNITY_BUILDS", {})
            if bid not in builds_db:
                for k in builds_db:
                    if cmd in k:
                        bid = k
                        break
            await send(chat, ua.upgrade_report(bid))
        else:
            report = ua.upgrade_report(cmd)
            if "Unknown build" in report:
                await send(chat, f"Unknown: '{cmd}'. Try: /upgrade list or /upgrade sbc")
            else:
                await send(chat, report)
    except Exception as e:
        await send(chat, f"Upgrade error: {e}")


# ============================================================
# v7.0 — Solar & Off-Grid Power Planner
# ============================================================
async def handle_solar(chat, uid, args):
    await typing(chat)
    try:
        sp = cd_classes.get("SolarPlanner")
        if not sp:
            await send(chat, "SolarPlanner not loaded")
            return
        parts = args.strip().split(maxsplit=2)
        if not parts:
            await send(chat, sp.overview())
            return
        cmd = parts[0].lower()
        if cmd == "calc" and len(parts) >= 2:
            wh = parts[1]
            region = parts[2] if len(parts) > 2 else "north_america_south"
            await send(chat, sp.calc(wh, region))
        elif cmd == "parts":
            await send(chat, sp.parts())
        elif cmd == "setup":
            await send(chat, sp.setup())
        elif cmd == "regions":
            await send(chat, sp.regions())
        else:
            await send(chat, sp.overview())
    except Exception as e:
        await send(chat, f"Solar error: {e}")


# ============================================================
# v7.0 — Beginner Build Wizard
# ============================================================
_wizard_instances = {}

def _get_wizard(uid):
    global _wizard_instances
    if uid not in _wizard_instances:
        BW = cd_classes.get("BeginnerWizard")
        if BW:
            _wizard_instances[uid] = BW()
    return _wizard_instances.get(uid)

async def handle_wizard(chat, uid, args):
    await typing(chat)
    try:
        parts = args.strip().split(maxsplit=2)
        cmd = parts[0].lower() if parts else ""
        wiz = _get_wizard(str(uid))
        if not wiz:
            await send(chat, "BeginnerWizard not loaded")
            return
        if cmd == "" or cmd == "start":
            await send(chat, wiz.start(str(uid)))
        elif cmd == "step" and len(parts) >= 2:
            step = int(parts[1])
            answer = parts[2] if len(parts) > 2 else ""
            if not answer:
                wq = cd_classes.get("WIZARD_QUESTIONS", [])
                for q in wq:
                    if q["step"] == step:
                        opts = "\n".join(f"  <code>{k}</code> — {v}" for k, v in q["options"].items())
                        await send(chat, f"<b>Step {step}: {q['question']}</b>\n\n{opts}")
                        return
            await send(chat, wiz.answer(str(uid), step, answer))
        elif cmd == "reset":
            await send(chat, wiz.reset(str(uid)))
        elif cmd == "quick" and len(parts) >= 2:
            wiz.start(str(uid))
            purpose, budget = parts[1], parts[2] if len(parts) > 2 else "budget"
            wq = cd_classes.get("WIZARD_QUESTIONS", [])
            for q in wq:
                val = {"purpose": purpose, "budget": budget, "skill": "beginner",
                       "portability": "bag", "display": "small_lcd", "battery": "moderate"}.get(q["field"], "")
                if val:
                    wiz.answer(str(uid), q["step"], val)
            await send(chat, wiz.result(str(uid)))
        elif cmd == "faq":
            await send(chat, wiz.faq())
        else:
            await send(chat, wiz.start(str(uid)))
    except Exception as e:
        await send(chat, f"Wizard error: {e}")


# ============================================================
# v7.0 — Build Sharing & Export
# ============================================================
async def handle_share(chat, uid, args):
    await typing(chat)
    try:
        bs = cd_classes.get("BuildSharing")
        if not bs:
            await send(chat, "BuildSharing not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, bs.overview())
            return
        cmd = parts[0].lower()
        if cmd == "lists" or cmd == "list":
            await send(chat, bs.list_builds())
        elif cmd in ("reddit", "hackaday", "github_readme", "github") and len(parts) > 1:
            platform = "github_readme" if cmd == "github" else cmd
            await send(chat, bs.generate(platform, parts[1]))
        elif cmd == "bom" and len(parts) > 1:
            await send(chat, bs.bom_csv(parts[1]))
        else:
            builds_db = cd_classes.get("SAMPLE_COMMUNITY_BUILDS", {})
            if cmd in builds_db:
                await send(chat, bs.generate("reddit", cmd))
            else:
                await send(chat, bs.overview())
    except Exception as e:
        await send(chat, f"Share error: {e}")


# ============================================================
# v7.1 — Local AI Tuner
# ============================================================
async def handle_localai(chat, uid, args):
    await typing(chat)
    try:
        la = cd_classes.get("LocalAITuner")
        if not la:
            await send(chat, "LocalAITuner not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, la.overview())
            return
        cmd = parts[0].lower()
        if cmd == "recommend" or cmd == "rec":
            budget = parts[1] if len(parts) > 1 else "150"
            await send(chat, la.recommend(budget))
        elif cmd == "boards":
            await send(chat, la.boards())
        elif cmd == "models":
            await send(chat, la.models())
        elif cmd == "npu":
            await send(chat, la.npu())
        elif cmd == "estimate" and len(parts) > 1:
            sub = parts[1].split()
            board = sub[0] if sub else "pi5_hailo8l"
            model = sub[1] if len(sub) > 1 else "deepseek_r1_1.5b"
            await send(chat, la.estimate(board, model))
        else:
            await send(chat, la.overview())
    except Exception as e:
        await send(chat, f"LocalAI error: {e}")


# ============================================================
# v7.1 — Battery Hot-Swap & Supercap UPS
# ============================================================
async def handle_hotswap(chat, uid, args):
    await typing(chat)
    try:
        hs = cd_classes.get("HotSwapPlanner")
        if not hs:
            await send(chat, "HotSwapPlanner not loaded")
            return
        parts = args.strip().split(maxsplit=2)
        if not parts:
            await send(chat, hs.overview())
            return
        cmd = parts[0].lower()
        if cmd == "design" and len(parts) >= 2:
            board = parts[1]
            power = parts[2] if len(parts) > 2 else "8"
            await send(chat, hs.design(board, power))
        elif cmd == "parts":
            await send(chat, hs.parts())
        elif cmd == "builds":
            await send(chat, hs.builds())
        elif cmd == "guide":
            await send(chat, hs.guide())
        else:
            await send(chat, hs.overview())
    except Exception as e:
        await send(chat, f"HotSwap error: {e}")


# ============================================================
# v7.1 — Ortholinear & Split Keyboard DB
# ============================================================
async def handle_ortho(chat, uid, args):
    await typing(chat)
    try:
        oa = cd_classes.get("OrthoAdvisor")
        if not oa:
            await send(chat, "OrthoAdvisor not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, oa.overview())
            return
        cmd = parts[0].lower()
        if cmd in ("list", "all"):
            await send(chat, oa.list_all())
        elif cmd == "recommend":
            bt = parts[1] if len(parts) > 1 else "general"
            await send(chat, oa.recommend(bt))
        elif cmd == "firmware":
            kb = parts[1] if len(parts) > 1 else ""
            await send(chat, oa.firmware(kb))
        elif cmd == "wiring":
            await send(chat, oa.wiring())
        else:
            await send(chat, oa.detail(cmd))
    except Exception as e:
        await send(chat, f"Ortho error: {e}")


# ============================================================
# v7.1 — Offline Survival Stack
# ============================================================
async def handle_offgridstack(chat, uid, args):
    await typing(chat)
    try:
        osg = cd_classes.get("OffgridStackPlanner")
        if not osg:
            await send(chat, "OffgridStackPlanner not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, osg.overview())
            return
        cmd = parts[0].lower()
        if cmd == "plan":
            budget = parts[1] if len(parts) > 1 else "200"
            await send(chat, osg.plan(budget))
        elif cmd in ("components", "comp"):
            await send(chat, osg.components())
        elif cmd == "dtn":
            await send(chat, osg.dtn())
        elif cmd == "reference":
            await send(chat, osg.reference())
        else:
            await send(chat, osg.overview())
    except Exception as e:
        await send(chat, f"OffgridStack error: {e}")


# ============================================================
# v7.1 — Community Feature Board
# ============================================================
async def handle_features(chat, uid, args):
    await typing(chat)
    try:
        fb = cd_classes.get("CommunityFeatureBoard")
        if not fb:
            await send(chat, "CommunityFeatureBoard not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, fb.overview())
            return
        cmd = parts[0].lower()
        if cmd == "top":
            await send(chat, fb.top())
        elif cmd == "recommend":
            bt = parts[1] if len(parts) > 1 else "general"
            await send(chat, fb.recommend(bt))
        elif cmd in ("all", "list"):
            await send(chat, fb.list_all())
        else:
            await send(chat, fb.list_all())
    except Exception as e:
        await send(chat, f"Features error: {e}")


# ============================================================
# v7.1 — Maximalist vs Minimalist Character Builder
# ============================================================
async def handle_character(chat, uid, args):
    await typing(chat)
    try:
        cb = cd_classes.get("CharacterBuilder")
        if not cb:
            await send(chat, "CharacterBuilder not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, cb.overview())
            return
        cmd = parts[0].lower()
        if cmd == "compare":
            await send(chat, cb.compare())
        elif cmd in ("list", "styles"):
            await send(chat, cb.list_styles())
        elif cmd in cd_classes.get("CHARACTER_TEMPLATES", {}):
            await send(chat, cb.build(cmd))
        else:
            await send(chat, cb.list_styles())
    except Exception as e:
        await send(chat, f"Character error: {e}")


# ============================================================
# v7.1 — Scavenge Build Sourcing
# ============================================================
async def handle_scavenge(chat, uid, args):
    await typing(chat)
    try:
        sp = cd_classes.get("ScavengePlanner")
        if not sp:
            await send(chat, "ScavengePlanner not loaded")
            return
        parts = args.strip().split(maxsplit=1)
        if not parts:
            await send(chat, sp.overview())
            return
        cmd = parts[0].lower()
        if cmd == "sources":
            await send(chat, sp.sources())
        elif cmd == "tips":
            await send(chat, sp.tips())
        elif cmd in cd_classes.get("SCAVENGE_BUILD_PLAN", {}):
            await send(chat, sp.plan(cmd))
        else:
            await send(chat, sp.plans())
    except Exception as e:
        await send(chat, f"Scavenge error: {e}")


# ============================================================
# v7.1 — 2026 Hardware Radar
# ============================================================
async def handle_newhardware(chat, uid, args):
    await typing(chat)
    try:
        nh = cd_classes.get("NewHardwareRadar")
        if not nh:
            await send(chat, "NewHardwareRadar not loaded")
            return
        parts = args.strip().split(maxsplit=2)
        if not parts:
            await send(chat, nh.overview())
            return
        cmd = parts[0].lower()
        if cmd == "detail" and len(parts) >= 2:
            await send(chat, nh.detail(parts[1]))
        elif cmd == "compare" and len(parts) >= 3:
            await send(chat, nh.compare(parts[1], parts[2]))
        elif cmd in cd_classes.get("NEW_HARDWARE_2026", {}):
            await send(chat, nh.detail(cmd))
        else:
            await send(chat, nh.list_all())
    except Exception as e:
        await send(chat, f"NewHardware error: {e}")


# ============================================================
# Main Loop
# ============================================================
async def poll():
    global _last_update
    p = {"timeout": 15, "allowed_updates": ["message"]}
    if _last_update:
        p["offset"] = _last_update + 1
    for attempt in range(3):
        try:
            c = await get_http()
            r = (await c.get(f"{TG_API}/getUpdates", params=p, timeout=20)).json()
            if not r.get("ok"):
                return []
            for u in r.get("result", []):
                _last_update = u["update_id"]
            _save_offset()
            result = r.get("result", [])
            now_ts = int(time.time())
            filtered = []
            for u in result:
                msg = u.get("message")
                if msg and isinstance(msg, dict):
                    msg_date = msg.get("date", 0)
                    if msg_date and (now_ts - msg_date) > 300:
                        continue
                filtered.append(u)
            return filtered
        except Exception as e:
            log(f"Poll error: {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
    return []

async def _handle_chat(chat, uid, text, msg):
    """AI reply path for plain messages, wrapped so /stop can cancel it.
    Quoted-reply context is injected into the user message."""
    try:
        quoted = ""
        rtm = msg.get("reply_to_message") if msg else None
        if rtm and rtm.get("text"):
            quoted = f'\n[Context: replying to "{rtm["text"][:500]}"]'
            content = text + quoted
            if _sessions.get(str(chat)):
                _sessions[str(chat)][-1] = {"role": "user", "content": content}

        coder = _coder_mode.get(str(uid))
        want_local = _offline_mode or (
            not coder and "androidllm" in PROVIDERS
            and _local_available() and _route_local(text))
        if want_local:
            reply, ok = await _local_try(_sessions[str(chat)][-10:])
            if ok:
                _sessions[str(chat)].append({"role": "assistant", "content": reply})
                bname = _user_brain.get(str(uid), "default")
                if BRAINS.get(bname, {}).get("learn"):
                    _obsidian_learn(text, reply)
                await send(chat, reply)
                return
            if _offline_mode:
                _sessions[str(chat)].append({"role": "assistant", "content": reply})
                await send(chat, reply)
                return

        if coder:
            reply, _cp, _cu = await call_coding(_sessions[str(chat)][-10:])
        else:
            reply = await call_ai(_sessions[str(chat)][-10:], local_fallback=True)
        _sessions[str(chat)].append({"role": "assistant", "content": reply})
        bname = _user_brain.get(str(uid), "default")
        if BRAINS.get(bname, {}).get("learn"):
            _obsidian_learn(text, reply)
        await send(chat, reply)
    except asyncio.CancelledError:
        try:
            await send(chat, "Stopped.")
        except Exception:
            pass
        raise
    except Exception as e:
        try:
            await send(chat, f"Error: {e}")
        except Exception:
            pass


async def main():
    global _current_uid
    log(f"Starting {BOT_NAME} v{BOT_VERSION}...")
    _load_offset()
    _load_offline_mode()
    _load_qa_mode()
    _load_rag_kb()
    load_providers()
    load_cyberdeck()
    log(f"Ready. Providers: {len(PROVIDERS)}")

    while not _shutdown.is_set():
        try:
            updates = await poll()
            for u in updates:
                msg = u.get("message")
                if not msg:
                    continue
                uid = msg.get("from", {}).get("id", 0)
                chat = msg.get("chat", {}).get("id", 0)
                text = msg.get("text", "")
                mid = msg.get("message_id")

                if uid == 0 or chat == 0:
                    continue

                photo = msg.get("photo")
                voice = msg.get("voice")
                document = msg.get("document")
                location = msg.get("location")

                if photo:
                    caption = msg.get("caption", "describe this cyberdeck")
                    text = f"/cyberdeck analyze this image: {caption}"
                    await typing(chat)
                    await handle_command(chat, uid, text, msg)
                    continue

                if voice:
                    await send(chat, "Voice support not available in cyberdeck bot. Use /v1 for voice.")
                    continue

                if document:
                    fname = document.get("file_name", "document")
                    await send(chat, f"Document '{fname}' received. Cyberdeck bot doesn't process files. Use /v1 for document analysis.")
                    continue

                if location:
                    lat = location.get("latitude", 0)
                    lon = location.get("longitude", 0)
                    text = f"/cyberdeck suggest builds for this location: {lat}, {lon}"
                    await typing(chat)
                    await handle_command(chat, uid, text, msg)
                    continue

                if text.startswith("/"):
                    await typing(chat)
                    await handle_command(chat, uid, text, msg)
                    continue

                if not text.strip():
                    continue

                if _qa_users.get(str(uid)):
                    await typing(chat)
                    reply = await _qa_answer(chat, uid, text)
                    _sessions.setdefault(str(chat), [])
                    _sessions[str(chat)].append({"role": "user", "content": text})
                    _sessions[str(chat)].append({"role": "assistant", "content": reply})
                    await send(chat, reply)
                    continue

                if str(chat) not in _sessions:
                    _sessions[str(chat)] = []
                    _sessions[str(chat)].append({"role": "system", "content": _brain_system(uid)})

                _current_uid = uid
                _sessions[str(chat)].append({"role": "user", "content": text})
                await typing(chat)

                t = asyncio.create_task(_handle_chat(chat, uid, text, msg))
                _active_tasks[str(chat)] = t
                t.add_done_callback(
                    lambda _t, c=chat: _active_tasks.pop(str(c), None))

            if not updates:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            print(f"Main loop error: {e}", flush=True)
            await asyncio.sleep(2)

    log("Shutting down...")

if __name__ == "__main__":
    try:
        if sys.platform == "win32" and sys.version_info < (3, 14):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Interrupted")
    except BaseException as e:
        log(f"FATAL: {e}")
        print(f"FATAL: {e}", flush=True)
        try:
            with open("cyberdeck_crash.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except:
            pass
