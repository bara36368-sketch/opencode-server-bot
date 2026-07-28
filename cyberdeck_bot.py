"""
Cyberdeck Bot — Dedicated Telegram bot for Cyberdeck Agent v6.0
Token: 8954725646:AAFHDboglEzsIX864QtVlVyp_zYhaUUrK0M
"""
import os, sys, json, time, asyncio, logging, traceback, hashlib, copy, re, urllib.request, urllib.parse
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

for _lib in ["httpx", "httpcore", "urllib3", "chardet"]:
    logging.getLogger(_lib).setLevel(logging.WARNING)

logging.basicConfig(filename="cyberdeck_bot.log", level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

BOT_TOKEN = "8954725646:AAFHDboglEzsIX864QtVlVyp_zYhaUUrK0M"
OWNER_ID = "8585609360"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BOT_VERSION = "6.0.0"
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
        # Dashboard (v6.0 interactive HTML)
        if hasattr(ca, 'InteractiveDashboard'):
            cd_classes["InteractiveDashboard"] = ca.InteractiveDashboard
        log(f"Loaded {len(cd_classes)} cyberdeck classes (v5.0+v5.2+v6.0)", "init")
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
        PROVIDERS["nvidia"] = {"url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "moonshotai/kimi-k2.5", "key": nvidia_key}
    mistral_key = env.get("MISTRAL_KEY", "")
    if mistral_key and mistral_key != "set-via-env-var":
        PROVIDERS["mistral"] = {"url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-small-latest", "key": mistral_key}

    log(f"Loaded {len(PROVIDERS)} providers: {', '.join(PROVIDERS.keys())}", "init")

ACTIVE_PROVIDER = "groq"

def _set_provider(name):
    global ACTIVE_PROVIDER
    ACTIVE_PROVIDER = name

async def call_ai(messages, provider_name=None):
    pname = provider_name or ACTIVE_PROVIDER
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
            return f"Gemini error: {r.status_code}"
        else:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {p['key']}"}
            body = {"model": p["model"], "messages": messages, "max_tokens": 4096}
            r = await c.post(p["url"], json=body, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
            return f"{pname} error: {r.status_code} - {r.text[:300]}"
    except Exception as e:
        return f"AI call failed: {e}"

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
# Command Handlers
# ============================================================
async def handle_command(chat, uid, text, msg):
    parts = text.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        await send(chat, f"""<b>CyberdeckBot v{BOT_VERSION}</b>

Dedicated cyberdeck builder with v6.0 AI engine.

<b>v6.0 Commands:</b>
/cyberdeck &lt;request&gt; — Build a cyberdeck from description
/build &lt;category&gt; [tier] — Auto-build for category
/bom &lt;request&gt; — Bill of materials
/compat &lt;sbc&gt; &lt;display&gt; — Compatibility check
/tutorial &lt;request&gt; — Step-by-step assembly guide
/upgrade &lt;build&gt; — Suggest upgrades
/ideas [category] — Build ideas
/search &lt;query&gt; — Search components
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
/provider — Switch AI provider
/providers — List providers
/v1 — Switch to General AI mode (opencode-bot)

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
/thermal — Thermal interface materials""")

    elif cmd == "/status":
        n_comp = len(cd_classes.get("ComponentDatabase", {}).get_all_sbcs()) if "ComponentDatabase" in cd_classes else 0
        await send(chat, f"""<b>CyberdeckBot {BOT_VERSION}</b>
Provider: {ACTIVE_PROVIDER}
Providers: {len(PROVIDERS)}
Components loaded: {n_comp}
Uptime: {time.strftime('%H:%M:%S')}""")

    elif cmd == "/provider":
        if args and args in PROVIDERS:
            _set_provider(args)
            await send(chat, f"Switched to <b>{args}</b>")
        else:
            await send(chat, f"Available: {', '.join(PROVIDERS.keys())}\nUsage: /provider &lt;name&gt;")

    elif cmd == "/providers":
        lines = []
        for name, p in PROVIDERS.items():
            marker = " << active" if name == ACTIVE_PROVIDER else ""
            lines.append(f"  <b>{name}</b>{marker}: {p['model']}")
        await send(chat, "<b>Providers:</b>\n" + "\n".join(lines))

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

    elif cmd == "/upgrade":
        await handle_upgrade(chat, uid, args)

    elif cmd == "/ideas":
        await handle_ideas(chat, uid, args)

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

    elif cmd == "/thermal":
        await handle_thermal(chat, uid, args)

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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Upgrade error: {e}")

async def handle_ideas(chat, uid, args):
    await typing(chat)
    try:
        if "IdeaGenerator" in cd_classes:
            ideas = cd_classes["IdeaGenerator"].generate(category=args or None)
            if ideas:
                lines = ["<b>Cyberdeck Ideas:</b>\n"]
                for i, idea in enumerate(ideas[:5], 1):
                    if isinstance(idea, dict):
                        lines.append(f"<b>{i}. {idea.get('name', 'Idea')}</b>")
                        lines.append(f"  {idea.get('description', '')}")
                        lines.append(f"  Budget: {idea.get('budget', '?')} | Category: {idea.get('category', '?')}\n")
                    else:
                        lines.append(f"{i}. {idea}\n")
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate 5 creative cyberdeck build ideas{' in category: ' + args if args else ''}. For each: name, description, key components, estimated budget, difficulty."})
        reply = await call_ai(_sessions[str(uid)[-10:]])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Ideas error: {e}")

async def handle_search(chat, uid, args):
    if not args:
        await send(chat, "Usage: /search &lt;query&gt;\nExample: /search raspberry pi 5")
        return
    await typing(chat)
    try:
        if "ComponentDatabase" in cd_classes:
            from cyberdeck_agent import ComponentDatabase
            results = ComponentDatabase.search(args)
            if results:
                lines = [f"<b>Search: {args}</b>\n"]
                for r in results[:10]:
                    if isinstance(r, dict):
                        lines.append(f"• <b>{r.get('name', '?')}</b> — ${r.get('price', '?')}")
                    else:
                        lines.append(f"• {r}")
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Search for cyberdeck components: {args}. List matching components with prices and where to buy."})
        reply = await call_ai(_sessions[str(uid)[-10:]])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Search error: {e}")

async def handle_3d(chat, uid, args):
    if not args:
        await send(chat, "Usage: /3d &lt;description&gt; [style]\nStyles: futuristic, retro, industrial, minimal, steampunk, cyberpunk, nautical, solarpunk, cassette_futurism, feminine_craft, fallout, brutalist")
        return
    await typing(chat)
    try:
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM + "\nGenerate OpenSCAD code for 3D models."})
        _sessions[str(uid)].append({"role": "user", "content": f"Generate an OpenSCAD 3D model for: {args}. Include the full .scad code with dimensions, colors, and style notes. Suggest STL export settings."})
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
        await send(chat, reply)
    except Exception as e:
        await send(chat, f"Cables error: {e}")

async def handle_flaws(chat, uid, args):
    if not args:
        await send(chat, "Usage: /flaws &lt;build description&gt;")
        return
    await typing(chat)
    try:
        if "BuildOptimizer" in cd_classes:
            optimizer = cd_classes["BuildOptimizer"]
            build = {"description": args, "components": {}}
            flaws = optimizer.scan_flaws(build)
            if flaws:
                lines = ["<b>Detected Flaws:</b>\n"]
                if isinstance(flaws, list):
                    for f in flaws:
                        if isinstance(f, dict):
                            lines.append(f"⚠️ <b>{f.get('type', 'Issue')}</b>: {f.get('description', str(f))}")
                            if f.get("fix"):
                                lines.append(f"  🔧 Fix: {f['fix']}")
                        else:
                            lines.append(f"⚠️ {f}")
                await send(chat, "\n".join(lines))
                return
        _sessions.setdefault(str(uid), [])
        _sessions[str(uid)].append({"role": "system", "content": CYBERDECK_SYSTEM})
        _sessions[str(uid)].append({"role": "user", "content": f"Analyze this cyberdeck build for flaws: {args}. Check power, cooling, connectivity, safety, compatibility. List each flaw with severity and fix."})
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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
        reply = await call_ai(_sessions[str(uid)[-10:]])
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

async def main():
    log(f"Starting {BOT_NAME} v{BOT_VERSION}...")
    _load_offset()
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

                if text.startswith("/"):
                    await typing(chat)
                    await handle_command(chat, uid, text, msg)
                elif str(chat) not in _sessions:
                    _sessions[str(chat)] = []
                    _sessions[str(chat)].append({"role": "system", "content": CYBERDECK_SYSTEM})

                    _sessions[str(chat)].append({"role": "user", "content": text})
                    await typing(chat)
                    reply = await call_ai(_sessions[str(chat)[-10:]])
                    _sessions[str(chat)].append({"role": "assistant", "content": reply})
                    await send(chat, reply)

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
