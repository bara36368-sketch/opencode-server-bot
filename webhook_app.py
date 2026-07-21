import asyncio, json, os, time, sys, copy, httpx
import bot_features as bf
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
TG_API = f"https://api.telegram.org/bot{TOKEN}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")

PROVIDERS = {
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile", "key": os.environ.get("GROQ_KEY", "set-via-env-var")},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", "model": "gemini-2.0-flash", "key": os.environ.get("GEMINI_KEY", "set-via-env-var")},
    "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "gryphe/mythomax-l2-13b", "key": os.environ.get("OPENROUTER_KEY", "")},
    "deepseek": {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat", "key": os.environ.get("DEEPSEEK_KEY", "")},
    "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-small-latest", "key": os.environ.get("MISTRAL_KEY", "")},
    "sambanova": {"url": "https://api.sambanova.ai/v1/chat/completions", "model": "Meta-Llama-3.3-70B-Instruct", "key": os.environ.get("SAMBANOVA_KEY", "")},
    "cerebras": {"url": "https://api.cerebras.ai/v1/chat/completions", "model": "llama3.1-70b", "key": os.environ.get("CEREBRAS_KEY", "")},
    "github": {"url": "https://models.inference.ai.azure.com/chat/completions", "model": "gpt-4o-mini", "key": os.environ.get("GITHUB_KEY", "")},
    "nvidia": {"url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "meta/llama-3.3-70b-instruct", "key": os.environ.get("NVIDIA_KEY", "")},
    "hy3": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "tencent/hy3", "key": os.environ.get("OPENROUTER_KEY", "")},
    "hy3-preview": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "tencent/hy3-preview", "key": os.environ.get("OPENROUTER_KEY", "")},
}
PROVIDERS_FILE = os.path.join(BASE_DIR, "providers.json")
if os.path.exists(PROVIDERS_FILE):
    try:
        with open(PROVIDERS_FILE) as f:
            PROVIDERS.update(json.load(f))
    except: pass

_http = None
async def get_http():
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(timeout=60, limits=httpx.Limits(max_keepalive_connections=10, max_connections=20))
    return _http

async def tg(method, data=None):
    c = await get_http()
    r = await c.post(f"{TG_API}/{method}", json=data or {}, timeout=15)
    return r.json()

async def send(chat, text):
    await tg("sendMessage", {"chat_id": chat, "text": str(text)[:4000]})

async def typing(chat):
    await tg("sendChatAction", {"chat_id": chat, "action": "typing"})

def load_sessions():
    global sessions
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, encoding="utf-8") as f:
                sessions = json.load(f)
        except: pass

def save_sessions():
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    except: pass

sessions = {}
load_sessions()

async def call_provider(messages, provider):
    p = PROVIDERS[provider]
    c = await get_http()
    msgs = copy.deepcopy(messages)

    if provider == "gemini":
        parts = []
        for m in msgs:
            role = "model" if m["role"] == "assistant" else "user"
            parts.append({"role": role, "parts": [{"text": m["content"]}]})
        r = await c.post(f"{p['url']}?key={p['key']}", json={"contents": parts})
        if r.status_code == 200:
            data = r.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))
            return str(data)
        return f"Gemini error: {r.status_code}"
    else:
        headers = {"Content-Type": "application/json"}
        if p["key"]:
            headers["Authorization"] = f"Bearer {p['key']}"
        body = {"model": p["model"], "messages": msgs, "max_tokens": 2048}
        r = await c.post(p["url"], json=body, headers=headers)
        if r.status_code == 200:
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", str(r.json()))
        return f"{provider.title()} error: {r.status_code}"

app = FastAPI(title="OpenCode Bot Webhook")

@app.post("/telegram-webhook")
async def webhook(request: Request):
    try:
        update = await request.json()
    except:
        return JSONResponse({"ok": False}, status_code=400)

    msg = update.get("message")
    if not msg:
        return JSONResponse({"ok": True})

    chat = msg["chat"]["id"]
    uid = msg["from"]["id"]
    text = msg.get("text", "")
    photo = msg.get("photo")
    voice = msg.get("voice")
    document = msg.get("document")

    if photo:
        file_id = photo[-1]["file_id"]
        caption = msg.get("caption", "Describe this image")
        await typing(chat)
        photo_url = await bf.get_photo_url(file_id)
        if photo_url:
            reply = await bf.vision_analyze(photo_url, caption)
        else:
            reply = "Could not get photo URL"
        await send(chat, reply)
        return JSONResponse({"ok": True})

    if voice:
        await typing(chat)
        transcribed = await bf.voice_to_text(voice["file_id"])
        if transcribed:
            await send(chat, f"Transcribed: {transcribed[:300]}")
            sessions.setdefault(str(uid), [])
            sessions[str(uid)].append({"role": "user", "content": transcribed})
            reply = await call_provider(sessions[str(uid)][-10:], "groq")
            sessions[str(uid)].append({"role": "assistant", "content": reply})
            save_sessions()
            await send(chat, reply)
        else:
            await send(chat, "Could not transcribe audio")
        return JSONResponse({"ok": True})

    if document:
        file_id = document["file_id"]
        fname = document.get("file_name", "document.bin")
        await typing(chat)
        extracted = await bf.extract_text_from_file(file_id, fname)
        if extracted and len(extracted) > 20:
            await send(chat, f"Document indexed ({len(extracted)} chars). Ask with /ask")
        else:
            await send(chat, "Could not extract text from document")
        return JSONResponse({"ok": True})

    if not text:
        return JSONResponse({"ok": True})

    parts = text.split()
    cmd = parts[0].lower()

    if cmd == "/start":
        lines = [
            "OpenCode Bot (Webhook)",
            f"Providers: {', '.join(PROVIDERS.keys())}",
            "",
            "/help — Commands",
            "/clear — Reset session",
            "/repo — List providers",
            "/repo <name> — Switch provider",
        ]
        await send(chat, "\n".join(lines))
        return JSONResponse({"ok": True})

    if cmd == "/help":
        await send(chat, (
            "/start — Reset\n/clear — Reset session\n"
            "/repo — List providers\n/repo <name> — Switch provider\n"
            "/status — Current status\n"
            "Send any message to chat with AI"
        ))
        return JSONResponse({"ok": True})

    if cmd == "/clear":
        sessions.pop(str(uid), None)
        save_sessions()
        await send(chat, "Session cleared")
        return JSONResponse({"ok": True})

    if cmd == "/repo":
        if len(parts) >= 2:
            active_provider_local = parts[1]
            await send(chat, f"Switched to {active_provider_local}")
        else:
            await send(chat, "Providers:\n" + "\n".join(f"  {k}" for k in PROVIDERS))
        return JSONResponse({"ok": True})

    if cmd == "/status":
        await send(chat, f"OpenCode Bot webhook mode\nSessions: {len(sessions)}")
        return JSONResponse({"ok": True})

    await typing(chat)
    sessions.setdefault(str(uid), [])
    agent_prompt = "You are OpenCode Bot, a helpful AI assistant. Be concise and accurate."
    if not sessions[str(uid)]:
        ctx = await bf.auto_context()
        sessions[str(uid)].append({"role": "system", "content": f"{agent_prompt}\n\n[Context]\n{ctx}"})
    sessions[str(uid)].append({"role": "user", "content": text})
    reply = await call_provider(sessions[str(uid)][-15:], "groq")
    sessions[str(uid)].append({"role": "assistant", "content": reply})
    save_sessions()
    await send(chat, reply)
    return JSONResponse({"ok": True})

@app.get("/")
async def root():
    return {"status": "ok", "name": "OpenCode Bot Webhook"}

# ── Bot-to-Bot Bridge ──────────────────────────────────────
BRIDGES_FILE = os.path.join(BASE_DIR, "bridges.json")
_bot_bridges = {}

def _load_bridges():
    global _bot_bridges
    if os.path.exists(BRIDGES_FILE):
        try:
            with open(BRIDGES_FILE, encoding="utf-8") as f:
                _bot_bridges = json.load(f)
        except:
            _bot_bridges = {}

def _save_bridges():
    try:
        with open(BRIDGES_FILE, "w", encoding="utf-8") as f:
            json.dump(_bot_bridges, f, indent=2)
    except:
        pass

_load_bridges()

@app.post("/bot-bridge/{bridge_name}")
async def bot_bridge_webhook(bridge_name: str, request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"ok": False}, status_code=400)

    bridge = _bot_bridges.get(bridge_name)
    if not bridge or not bridge.get("enabled", False):
        return JSONResponse({"ok": False, "error": "bridge not found or disabled"}, status_code=404)

    text = body.get("text", "") or body.get("message", "") or body.get("content", "")
    sender = body.get("sender", "") or body.get("from", "") or "unknown-bot"
    reply_url = body.get("reply_url", "")

    if not text:
        return JSONResponse({"ok": False, "error": "no text"})

    auto_reply = bridge.get("auto_reply", False)
    response_text = ""

    if auto_reply:
        try:
            msgs = [{"role": "system", "content": bridge.get("system_prompt", "You are a helpful bot assistant. Respond concisely.")}]
            msgs.append({"role": "user", "content": f"[Message from bot {sender} via bridge {bridge_name}]: {text}"})
            resp = await call_provider(msgs, "groq")
            response_text = str(resp)[:3000]

            if reply_url:
                c2 = await get_http()
                await c2.post(reply_url, json={"text": response_text, "from": "opencode-bot", "bridge": bridge_name}, timeout=10)
        except Exception as e:
            response_text = f"Auto-reply error: {e}"

    if bridge.get("relay_to_owner", False) and OWNER_ID:
        header = f"Bot-to-Bot [{sender} -> {bridge_name}]: {text[:500]}"
        if response_text:
            header += f"\n\n[Auto-reply]: {response_text[:500]}"
        await tg("sendMessage", {"chat_id": OWNER_ID, "text": header[:4000]})

    return JSONResponse({"ok": True, "reply": response_text if auto_reply else "", "auto_replied": auto_reply})

@app.get("/setup-webhook")
async def setup_webhook(request: Request):
    host = request.headers.get("host", "unknown")
    webhook_url = f"https://{host}/telegram-webhook"
    c = await get_http()
    r = await c.post(f"{TG_API}/deleteWebhook")
    r = await c.post(f"{TG_API}/setWebhook", json={"url": webhook_url, "allowed_updates": ["message"]})
    data = r.json()
    return {"ok": data.get("ok"), "description": data.get("description"), "webhook_url": webhook_url}