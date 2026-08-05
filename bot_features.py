import asyncio, json, os, time, re, hashlib, html, urllib.parse
import httpx
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.json")
RAG_FILE = os.path.join(BASE_DIR, "rag_data.json")
MEMORY_LOG_FILE = os.path.join(BASE_DIR, "memory_log.json")
PAGES_FILE = os.path.join(BASE_DIR, "pages.json")
_http = None

async def get_http():
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(timeout=60, limits=httpx.Limits(max_keepalive_connections=10, max_connections=20))
    return _http

# ── 1. IMAGE VISION ───────────────────────────────────────

async def vision_analyze(photo_url, prompt="Describe this image in detail"):
    import base64
    img_resp = await (await get_http()).get(photo_url)
    img_data = img_resp.content
    ct = img_resp.headers.get("content-type", "image/jpeg").split(";")[0]
    if len(img_data) > 4_000_000:
        img_data = img_data[:4_000_000]
    b64 = base64.b64encode(img_data).decode("utf-8")
    data_uri = f"data:{ct};base64,{b64}"

    gemini_key = os.environ.get("GEMINI_KEY", "")
    openai_key = os.environ.get("OPENAI_KEY", "")

    models = ["gemini-3.5-flash", "gemini-2.0-flash-001", "gemini-2.0-flash", "gemini-1.5-flash-001", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_err = None
    for model in models:
        if gemini_key and gemini_key not in ("", "set-via-env-var"):
            try:
                return await _try_gemini_vision(model, data_uri, prompt)
            except Exception as e:
                last_err = e
                print(f"vision: {model} failed: {e}")
        else:
            last_err = Exception("no gemini key")
    if openai_key and openai_key not in ("", "set-via-env-var"):
        try:
            return await _try_openai_vision(data_uri, prompt, openai_key)
        except Exception as e:
            last_err = e
            print(f"vision: openai failed: {e}")
    reason = str(last_err) if last_err else "unknown error"
    return (f"Could not analyze image. The bot needs a GEMINI_KEY or OPENAI_KEY "
            f"in your .env file for vision features. (debug: {reason})")

async def _try_gemini_vision(model, data_uri, prompt):
    c = await get_http()
    gemini_key = os.environ.get("GEMINI_KEY", "set-via-env-var")
    parts = [
        {"inline_data": {"mime_type": data_uri.split(";")[0].split(":")[1], "data": data_uri.split("base64,")[1]}},
        {"text": prompt},
    ]
    r = await c.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}",
        json={"contents": [{"parts": parts}]},
        timeout=30,
    )
    data = r.json()
    if r.status_code != 200:
        msg = data.get("error", {}).get("message", "") or r.text[:300]
        raise Exception(f"{model}: {msg}")
    candidates = data.get("candidates", [])
    if not candidates:
        raise Exception(f"{model}: no candidates - {json.dumps(data)[:300]}")
    finish = candidates[0].get("finishReason", "")
    if finish == "BLOCKED":
        block = candidates[0].get("blockReason", "unknown")
        raise Exception(f"{model}: blocked ({block})")
    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    if "does not support image" in text.lower():
        raise Exception(f"{model}: {text}")
    return text or "No response"

async def _try_openai_vision(data_uri, prompt, key):
    c = await get_http()
    r = await c.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_uri}}]}],
            "max_tokens": 1024,
        },
        timeout=30,
    )
    data = r.json()
    if r.status_code != 200:
        raise Exception(f"openai: {data.get('error',{}).get('message','')[:300]}")
    return data["choices"][0]["message"]["content"]

async def get_photo_url(file_id):
    try:
        c = await get_http()
        r = await c.get(f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN', 'set-via-env-var')}/getFile?file_id={file_id}")
        data = r.json()
        if data.get("ok"):
            path = data["result"]["file_path"]
            return f"https://api.telegram.org/file/bot{os.environ.get('TELEGRAM_BOT_TOKEN', 'set-via-env-var')}/{path}"
        return None
    except:
        return None

# ── 2. VOICE CHAT (X-Phone v2) ─────────────────────────────

VOICE_SESSIONS = {}
VOICE_EMOTIONS = {"neutral", "happy", "sad", "angry", "excited", "calm", "whisper"}

async def voice_to_text(file_id):
    try:
        c = await get_http()
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
        r = await c.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}")
        data = r.json()
        if not data.get("ok"):
            return None
        path = data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{path}"
        audio_data = (await c.get(file_url)).content
        hf_key = os.environ.get("HUGGINGFACE_KEY", "hf_free")
        r2 = await c.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
            data=audio_data,
            headers={"Authorization": f"Bearer {hf_key}"},
            timeout=60,
        )
        result = r2.json()
        return result.get("text", str(result))
    except Exception as e:
        return f"[Voice error: {e}]"

async def text_to_speech(text, chat_id, voice="nova", emotion=None):
    try:
        c = await get_http()
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
        openai_key = os.environ.get("OPENAI_KEY", "")
        if openai_key:
            voice = voice or "nova"
            resp = await c.post(
                "https://api.openai.com/v1/audio/speech",
                json={"model": "tts-1", "input": text[:500], "voice": voice},
                headers={"Authorization": f"Bearer {openai_key}"},
                timeout=30
            )
            if resp.status_code == 200:
                await c.post(
                    f"https://api.telegram.org/bot{bot_token}/sendVoice",
                    files={"voice": ("speech.ogg", resp.content)},
                    data={"chat_id": chat_id, "caption": emotion or "AI Reply"},
                    timeout=30,
                )
                return True
        r = await c.post(
            "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits",
            json={"inputs": text[:500]},
            timeout=30,
        )
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("audio/"):
            await c.post(
                f"https://api.telegram.org/bot{bot_token}/sendAudio",
                files={"audio": ("reply.wav", r.content)},
                data={"chat_id": chat_id, "title": emotion or "AI Reply"},
                timeout=30,
            )
            return True
        return False
    except:
        return False

def get_voice_session(chat_id):
    chat_id = str(chat_id)
    return VOICE_SESSIONS.get(chat_id, {})

def set_voice_mode(chat_id, mode):
    chat_id = str(chat_id)
    if chat_id not in VOICE_SESSIONS:
        VOICE_SESSIONS[chat_id] = {}
    VOICE_SESSIONS[chat_id]["mode"] = mode
    VOICE_SESSIONS[chat_id]["active"] = time.time()

def get_voice_mode(chat_id):
    return get_voice_session(chat_id).get("mode", "off")

async def voice_conversation_pipeline(file_id, chat_id, call_provider=None, provider_name=None):
    transcribed = await voice_to_text(file_id)
    if not transcribed or transcribed.startswith("[Voice error"):
        return None, None
    if call_provider and provider_name:
        reply = await call_provider([{"role": "user", "content": transcribed}], provider_name)
    else:
        reply = transcribed
    tts_ok = await text_to_speech(reply, chat_id, emotion="neutral")
    if not tts_ok:
        await text_to_speech(reply[:200], chat_id, emotion="neutral")
    return transcribed, reply

# ── 3. DOCUMENT RAG ────────────────────────────────────────

class DocumentDB:
    def __init__(self):
        self.docs = []
        self.chunks = []
        self._load()

    def _load(self):
        if os.path.exists(RAG_FILE):
            try:
                with open(RAG_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                    self.docs = data.get("docs", [])
                    self.chunks = data.get("chunks", [])
            except:
                pass

    def _save(self):
        with open(RAG_FILE, "w", encoding="utf-8") as f:
            json.dump({"docs": self.docs, "chunks": self.chunks}, f)

    def add_document(self, name, text):
        self.docs.append({"name": name, "text": text, "added": time.time()})
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 50]
        for p in paragraphs:
            self.chunks.append({"text": p, "doc": name, "tokens": self._simple_hash(p)})
        self._save()
        return len(paragraphs)

    def query(self, question, top_k=3):
        q_words = set(question.lower().split())
        scored = []
        for chunk in self.chunks:
            c_words = set(chunk["text"].lower().split())
            overlap = len(q_words & c_words)
            if overlap > 0:
                scored.append((overlap, chunk["text"]))
        scored.sort(reverse=True)
        return [s[1][:1000] for s in scored[:top_k]]

    def list_docs(self):
        return [d["name"] for d in self.docs]

    def clear(self):
        self.docs = []
        self.chunks = []
        self._save()

    def _simple_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()[:8]

doc_db = DocumentDB()

# ── 3b. PERSISTENT LONG-TERM MEMORY ─────────────────────

class MemoryLog:
    def __init__(self):
        self.logs = {}  # uid -> [{"role": str, "content": str, "ts": float, "summary": str}]
        self._load()

    def _load(self):
        if os.path.exists(MEMORY_LOG_FILE):
            try:
                with open(MEMORY_LOG_FILE, encoding="utf-8") as f:
                    self.logs = json.load(f)
                self.logs = {int(k) if k.isdigit() else k: v for k, v in self.logs.items()}
            except:
                self.logs = {}

    def _save(self):
        clean = {}
        for uid, entries in self.logs.items():
            clean[str(uid)] = [{"role": e["role"], "content": e["content"], "ts": e.get("ts", 0), "summary": e.get("summary", "")} for e in entries[-200:]]
        with open(MEMORY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(clean, f, indent=2, ensure_ascii=False)

    def append(self, uid, role, content):
        uid = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        self.logs.setdefault(uid, [])
        self.logs[uid].append({"role": role, "content": content, "ts": time.time(), "summary": ""})
        if len(self.logs[uid]) > 200:
            self.logs[uid] = self.logs[uid][-200:]
        self._save()

    def get_recent(self, uid, limit=20):
        uid = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        return self.logs.get(uid, [])[-limit:]

    def get_all(self, uid):
        uid = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        return self.logs.get(uid, [])

    def search(self, uid, keyword, limit=5):
        uid = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        entries = self.logs.get(uid, [])
        kw = keyword.lower()
        hits = [e for e in entries if kw in e.get("content", "").lower()]
        return hits[-limit:]

    def summarize_old(self, uid, smart_call_fn, max_age=3600):
        uid_int = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        entries = self.logs.get(uid_int, [])
        old = [e for e in entries if time.time() - e.get("ts", 0) > max_age and not e.get("summary")]
        if len(old) < 5:
            return
        text = "\n".join(f"{e['role']}: {e['content'][:200]}" for e in old)
        try:
            summary = smart_call_fn([
                {"role": "system", "content": "Summarize key facts, preferences, and decisions from this conversation history concisely."},
                {"role": "user", "content": text},
            ])
        except:
            summary = ""
        if summary:
            for e in old:
                e["summary"] = str(summary)[:500]
            self._save()

    def get_context_blob(self, uid, recent_count=8, max_age=86400):
        uid_int = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        entries = self.logs.get(uid_int, [])
        recent = [e for e in entries if time.time() - e.get("ts", 0) < max_age][-recent_count:]
        summaries = [e.get("summary", "") for e in entries if e.get("summary")]
        recent_text = "\n".join(f"{e['role']}: {e['content'][:300]}" for e in recent)
        summary_text = " | ".join(set(s for s in summaries if s))
        parts = []
        if summary_text:
            parts.append(f"[Past context: {summary_text[:800]}]")
        if recent_text:
            parts.append(f"[Recent: {recent_text[:1500]}]")
        return "\n".join(parts)

    def clear_user(self, uid):
        uid_int = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        self.logs.pop(uid_int, None)
        self._save()

    def get_stats(self, uid):
        uid_int = int(uid) if isinstance(uid, str) and uid.isdigit() else uid
        entries = self.logs.get(uid_int, [])
        user_msgs = sum(1 for e in entries if e["role"] == "user")
        ai_msgs = sum(1 for e in entries if e["role"] == "assistant")
        first = entries[0]["ts"] if entries else 0
        return {"total": len(entries), "user": user_msgs, "ai": ai_msgs, "first_seen": first, "days": max(1, int((time.time() - first) / 86400)) if first else 1}

memory_log = MemoryLog()

async def append_to_memory_log(uid, role, content):
    memory_log.append(uid, role, content)

async def get_memory_context(uid):
    return memory_log.get_context_blob(uid)

async def search_user_memories(uid, keyword):
    return memory_log.search(uid, keyword)

async def get_memory_stats(uid):
    return memory_log.get_stats(uid)

async def clear_user_memory(uid):
    memory_log.clear_user(uid)

async def extract_text_from_file(file_id, file_name):
    try:
        c = await get_http()
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
        r = await c.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}")
        data = r.json()
        if not data.get("ok"):
            return None
        path = data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{path}"
        content = (await c.get(file_url)).content
        ext = (file_name or "").lower()
        if ext.endswith(".txt") or ext.endswith(".md"):
            return content.decode("utf-8", errors="replace")
        elif ext.endswith(".json"):
            try:
                return json.dumps(json.loads(content), indent=2)
            except:
                return content.decode("utf-8", errors="replace")
        elif ext.endswith(".pdf"):
            try:
                import io, PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                return "\n".join(p.extract_text() or "" for p in reader.pages)
            except:
                return "[PDF parsing failed - PyPDF2 not installed]"
        else:
            return content.decode("utf-8", errors="replace")[:50000]
    except Exception as e:
        return f"[Extract error: {e}]"

# ── 4. SCHEDULED AI TASKS ────────────────────────────────

class Scheduler:
    def __init__(self):
        self.tasks = []
        self._load()

    def _load(self):
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except:
                pass

    def _save(self):
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    def add(self, interval_seconds, prompt, chat_id, label=""):
        task = {
            "id": hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:8],
            "interval": interval_seconds,
            "prompt": prompt,
            "chat_id": chat_id,
            "label": label or prompt[:40],
            "last_run": 0,
            "created": time.time(),
        }
        self.tasks.append(task)
        self._save()
        return task["id"]

    def remove(self, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save()

    def list(self):
        return [(t["id"], t["label"], t["interval"], t["chat_id"]) for t in self.tasks]

    def due(self):
        now = time.time()
        return [t for t in self.tasks if now - t["last_run"] >= t["interval"]]

    def mark_run(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                t["last_run"] = time.time()
                break
        self._save()

scheduler = Scheduler()

async def run_scheduler_loop(smart_call_fn, send_fn):
    while True:
        try:
            for task in scheduler.due():
                try:
                    result = await smart_call_fn([{"role": "user", "content": task["prompt"]}], None)
                    await send_fn(task["chat_id"], f"[Scheduled: {task['label']}]\n{result[:3000]}")
                    scheduler.mark_run(task["id"])
                except Exception as e:
                    await send_fn(task["chat_id"], f"[Scheduler error for {task['label']}]: {e}")
        except:
            pass
        await asyncio.sleep(30)

# ── 5. IMAGE GENERATION ─────────────────────────────────

async def image_generate(prompt):
    try:
        c = await get_http()
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        r = await c.get(url, timeout=60)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
            return r.content
        text = await c.get(url + "?width=512&height=512&nologo=true", timeout=60)
        if text.status_code == 200:
            return text.content
        return None
    except:
        return None

# ── 6. CHAT EXPORT ──────────────────────────────────────

def export_as_json(session):
    return json.dumps(session, indent=2, ensure_ascii=False)

def export_as_markdown(session):
    lines = ["# Chat Export\n"]
    for msg in session:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        lines.append(f"## {role}\n\n{content}\n")
    return "\n".join(lines)

# ── 7. AUTO-CONTEXT ─────────────────────────────────────

_weather_cache = {"data": "", "time": 0}
_news_cache = {"data": "", "time": 0}

async def auto_context():
    now = time.time()
    parts = [f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}"]
    if now - _weather_cache["time"] > 3600:
        try:
            c = await get_http()
            r = await c.get("https://wttr.in?format=%C+%t+%h+%w", timeout=10)
            if r.status_code == 200:
                _weather_cache["data"] = r.text.strip()
                _weather_cache["time"] = now
        except:
            pass
    if _weather_cache["data"]:
        parts.append(f"Weather: {_weather_cache['data']}")
    if now - _news_cache["time"] > 7200:
        try:
            c = await get_http()
            r = await c.get("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", timeout=10)
            if r.status_code == 200:
                headlines = re.findall(r"<title>(.*?)</title>", r.text)[:5]
                if headlines:
                    _news_cache["data"] = " | ".join(headlines)
                    _news_cache["time"] = now
        except:
            pass
    if _news_cache["data"]:
        parts.append(f"Latest headlines: {_news_cache['data']}")
    return "\n".join(parts)

# ── 8. CONVERSATION SUMMARIZER ──────────────────────────

async def summarize_conversation(messages, smart_call_fn, max_before_summary=20):
    if len(messages) <= max_before_summary:
        return messages
    system_msgs = [m for m in messages if m.get("role") == "system"]
    to_summarize = messages[:max_before_summary - 5]
    keep = messages[-(max_before_summary - 5):]
    try:
        text = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in to_summarize)
        summary = await smart_call_fn([
            {"role": "system", "content": "Summarize this conversation concisely, keeping key facts and decisions."},
            {"role": "user", "content": text},
        ], None)
        summary_text = summary[:2000] if isinstance(summary, str) else str(summary)[:2000]
        return system_msgs + [{"role": "system", "content": f"Previous conversation summary: {summary_text}"}] + keep
    except:
        return messages

# ── 9. WEB SEARCH ───────────────────────────────────────────

async def web_search(query):
    try:
        c = await get_http()
        url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
        r = await c.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return f"Search error: {r.status_code}"
        results = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', r.text, re.DOTALL)
        lines = [f"Web search results for: {query}\n"]
        for i, ((link, title), snippet) in enumerate(zip(results[:5], snippets[:5])):
            title_clean = re.sub(r'<[^>]+>', '', title).strip()[:80]
            snippet_clean = re.sub(r'<[^>]+>', '', snippet).strip()[:300]
            lines.append(f"{i+1}. {title_clean}")
            lines.append(f"   {snippet_clean}")
            lines.append(f"   {link}")
        return "\n".join(lines) if lines[1:] else f"No results for: {query}"
    except Exception as e:
        return f"Search error: {e}"

# ── 10. YOUTUBE SUMMARIZER ─────────────────────────────────

async def youtube_transcript(url):
    try:
        video_id = None
        patterns = [r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"]
        for p in patterns:
            m = re.search(p, url)
            if m:
                video_id = m.group(1)
                break
        if not video_id:
            return "Could not extract YouTube video ID from URL."
        c = await get_http()
        r = await c.get(
            f"https://youtubetranscript.com/?v={video_id}&format=json",
            timeout=15,
        )
        if r.status_code != 200:
            return f"Transcript not available (status {r.status_code})."
        data = r.json()
        if isinstance(data, dict) and "text" in data:
            return data.get("text", "")[:10000]
        if isinstance(data, list):
            text = " ".join(seg.get("text", "") for seg in data)
            text = re.sub(r'<[^>]+>', '', text)
            return text[:10000]
        return str(data)[:10000]
    except Exception as e:
        return f"YouTube error: {e}"

async def summarize_youtube(url):
    transcript = await youtube_transcript(url)
    if not transcript or transcript.startswith("Could not") or transcript.startswith("YouTube error") or transcript.startswith("Transcript not"):
        return transcript
    return f"📹 YouTube Transcript ({url[:60]}...)\n\nTranscript length: {len(transcript)} chars\n\n{transcript[:3500]}"

# ── 11. CODE SANDBOX ────────────────────────────────────────

import subprocess, tempfile, textwrap

async def run_code(code, language="python"):
    try:
        code = textwrap.dedent(code)
        if language == "python":
            import ast
            try:
                ast.parse(code)
            except SyntaxError as e:
                return f"Syntax error: {e}"
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: _exec_python(code))
            return result
        elif language in ("js", "javascript"):
            return _exec_node(code)
        else:
            return f"Unsupported language: {language}. Use 'python' or 'js'."
    except Exception as e:
        return f"Sandbox error: {e}"

def _exec_python(code):
    try:
        import io, sys
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_stdout = io.StringIO()
        sys.stderr = captured_stderr = io.StringIO()
        restricted = {"__builtins__": {
            "print": print, "len": len, "str": str, "int": int, "float": float,
            "list": list, "dict": dict, "tuple": tuple, "set": set, "bool": bool,
            "range": range, "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
            "sorted": sorted, "reversed": reversed, "abs": abs, "max": max, "min": min,
            "sum": sum, "any": any, "all": all, "isinstance": isinstance,
            "True": True, "False": False, "None": None,
            "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError,
            "IndexError": IndexError, "ZeroDivisionError": ZeroDivisionError,
        }}
        try:
            exec(code, restricted)
            output = captured_stdout.getvalue()
            err = captured_stderr.getvalue()
        except Exception as e:
            output = captured_stdout.getvalue()
            err = str(e)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        result = ""
        if output: result += f"Output:\n{output[:3000]}"
        if err: result += f"Error:\n{err[:1000]}"
        return result or "(no output)"
    except Exception as e:
        return f"Execution error: {e}"

def _exec_node(code):
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                ["node", f.name],
                capture_output=True, text=True, timeout=10,
            )
        os.unlink(f.name)
        out = result.stdout[:3000]
        err = result.stderr[:1000]
        r = ""
        if out: r += f"Output:\n{out}"
        if err: r += f"Error:\n{err}"
        return r or "(no output)"
    except subprocess.TimeoutExpired:
        return "Execution timed out (10s limit)."
    except FileNotFoundError:
        return "Node.js not found on this server."
    except Exception as e:
        return f"Execution error: {e}"

# ── 12. URL READER ─────────────────────────────────────────

def _is_private_ip(host):
    import ipaddress
    try:
        addr = ipaddress.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except ValueError:
        return False

async def fetch_url(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if _is_private_ip(host):
            return "Fetch error: URL points to a private/internal network address."
        c = await get_http()
        r = await c.get(url, timeout=20, follow_redirects=False, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code in (301, 302, 303, 307, 308):
            location = r.headers.get("location", "")
            if location and _is_private_ip(urlparse(location).hostname or ""):
                return "Fetch error: Redirect blocked (internal network)."
        if r.status_code != 200:
            return f"HTTP {r.status_code}: Could not fetch {url}"
        text = r.text
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = html.unescape(text)
        return text[:8000]
    except Exception as e:
        return f"Fetch error: {e}"

# ── 13. YOUTUBE SEARCH ─────────────────────────────────────

async def youtube_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://www.youtube.com/results?search_query={q}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        )
        import json
        initial_data = None
        for match in re.finditer(r'ytInitialData\s*=\s*({.*?});\s*</script>', r.text, re.DOTALL):
            try:
                initial_data = json.loads(match.group(1))
                break
            except Exception:
                continue
        if not initial_data:
            return "Could not parse YouTube search results."
        results = []
        sections = initial_data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])
        for section in sections:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                vr = item.get("videoRenderer", {})
                if not vr:
                    continue
                vid = vr.get("videoId", "")
                title = "".join(seg.get("text", "") for seg in vr.get("title", {}).get("runs", []))
                views = vr.get("viewCountText", {}).get("simpleText", "") or "".join(seg.get("text", "") for seg in vr.get("viewCountText", {}).get("runs", []))
                length = vr.get("lengthText", {}).get("simpleText", "")
                channel = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                published = vr.get("publishedTimeText", {}).get("simpleText", "")
                results.append({
                    "id": vid,
                    "title": title,
                    "views": views,
                    "duration": length,
                    "channel": channel,
                    "published": published,
                    "url": f"https://youtube.com/watch?v={vid}"
                })
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
        if not results:
            return f"No YouTube results for: {query}"
        lines = [f"YouTube search results for: {query}\n"]
        for i, r2 in enumerate(results):
            lines.append(f"{i+1}. {r2['title']}")
            lines.append(f"   Channel: {r2['channel']} | Views: {r2['views']} | Duration: {r2['duration']} | {r2['published']}")
            lines.append(f"   {r2['url']}")
        return "\n".join(lines)
    except Exception as e:
        return f"YouTube search error: {e}"

# ── 14. TIKTOK SEARCH ─────────────────────────────────────

async def tiktok_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://www.tiktok.com/search/video?q={q}",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        )
        sigi_data = None
        for match in re.finditer(r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION"[^>]*>({.*?})</script>', r.text, re.DOTALL):
            try:
                sigi_data = json.loads(match.group(1))
                break
            except Exception:
                continue
        if not sigi_data:
            try:
                for match in re.finditer(r'<script[^>]*id="SIGI_STATE"[^>]*>({.*?})</script>', r.text, re.DOTALL):
                    sigi_data = json.loads(match.group(1))
                    break
            except Exception:
                pass
        results = []
        if sigi_data:
            items = sigi_data.get("ItemModule", {})
            for vid, item in items.items():
                results.append({
                    "id": vid,
                    "desc": (item.get("desc", "") or "")[:200],
                    "author": item.get("author", "") or (item.get("authorInfo", {}) or {}).get("uniqueId", ""),
                    "likes": item.get("diggCount", 0),
                    "plays": item.get("playCount", 0),
                    "shares": item.get("shareCount", 0),
                    "duration": item.get("video", {}).get("duration", 0),
                    "url": f"https://www.tiktok.com/@{item.get('author', '')}/video/{vid}"
                })
                if len(results) >= max_results:
                    break
        if not results:
            try:
                alt_r = await c.get(
                    f"https://tikwm.com/api/feed/search?keywords={q}",
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                alt_data = alt_r.json()
                for item in (alt_data.get("data", {}).get("videos", []) or []):
                    results.append({
                        "id": item.get("video_id", ""),
                        "desc": (item.get("title", "") or "")[:200],
                        "author": item.get("author", {}).get("unique_id", "") if isinstance(item.get("author"), dict) else str(item.get("author", "")),
                        "likes": item.get("digg_count", 0),
                        "plays": item.get("play_count", 0),
                        "shares": item.get("share_count", 0),
                        "duration": item.get("duration", 0),
                        "url": f"https://www.tiktok.com/@{item.get('author', {}).get('unique_id', '')}/video/{item.get('video_id', '')}" if isinstance(item.get("author"), dict) else f"https://www.tiktok.com/video/{item.get('video_id', '')}"
                    })
                    if len(results) >= max_results:
                        break
            except Exception:
                pass
        if not results:
            return f"No TikTok results for: {query}"
        lines = [f"TikTok search results for: {query}\n"]
        for i, r2 in enumerate(results):
            likes_str = f"{r2['likes']:,}" if isinstance(r2['likes'], int) else str(r2['likes'])
            plays_str = f"{r2['plays']:,}" if isinstance(r2['plays'], int) else str(r2['plays'])
            dur = f"{r2['duration']}s" if r2['duration'] else "?"
            lines.append(f"{i+1}. {r2['desc'][:100] or '(no description)'}")
            lines.append(f"   Author: @{r2['author']} | Plays: {plays_str} | Likes: {likes_str} | Duration: {dur}")
            lines.append(f"   {r2['url']}")
        return "\n".join(lines)
    except Exception as e:
        return f"TikTok search error: {e}"

# ── 15. MULTI-PLATFORM SOCIAL SEARCH ─────────────────────

async def reddit_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://www.reddit.com/search.json?q={q}&limit={max_results}&sort=relevance&t=year",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; OpenCodeBot/1.0)"}
        )
        if r.status_code != 200:
            return f"Reddit search error: {r.status_code}"
        data = r.json()
        children = data.get("data", {}).get("children", [])
        if not children:
            return f"No Reddit results for: {query}"
        lines = [f"Reddit results for: {query}\n"]
        for i, child in enumerate(children[:max_results]):
            d = child.get("data", {})
            title = d.get("title", "")
            sub = d.get("subreddit", "")
            score = d.get("score", 0)
            comments = d.get("num_comments", 0)
            permalink = d.get("permalink", "")
            url = f"https://reddit.com{permalink}"
            lines.append(f"{i+1}. [{sub}] {title[:120]}")
            lines.append(f"   Score: {score} | Comments: {comments}")
            lines.append(f"   {url}")
        return "\n".join(lines)
    except Exception as e:
        return f"Reddit search error: {e}"

async def hackernews_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://hn.algolia.com/api/v1/search?query={q}&hitsPerPage={max_results}&tags=story",
            timeout=15
        )
        if r.status_code != 200:
            return f"HN search error: {r.status_code}"
        data = r.json()
        hits = data.get("hits", [])
        if not hits:
            return f"No Hacker News results for: {query}"
        lines = [f"Hacker News results for: {query}\n"]
        for i, hit in enumerate(hits[:max_results]):
            title = hit.get("title", "")
            points = hit.get("points", 0)
            author = hit.get("author", "")
            comments = hit.get("num_comments", 0)
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            hn_url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            lines.append(f"{i+1}. {title[:120]}")
            lines.append(f"   {points} points | {author} | {comments} comments")
            lines.append(f"   {url}")
            lines.append(f"   Discuss: {hn_url}")
        return "\n".join(lines)
    except Exception as e:
        return f"HN search error: {e}"

async def medium_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://medium.com/search?q={q}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        urls = re.findall(r'href="(https://medium\.com/[^"/]+/[^"]+)"', r.text)
        titles = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', r.text, re.DOTALL)
        seen = set()
        results = []
        for url in urls:
            if url not in seen and "/search?" not in url:
                seen.add(url)
                results.append(url)
                if len(results) >= max_results:
                    break
        if not results:
            return f"No Medium results for: {query}"
        lines = [f"Medium results for: {query}\n"]
        for i, url in enumerate(results):
            lines.append(f"{i+1}. {url}")
        return "\n".join(lines)
    except Exception as e:
        return f"Medium search error: {e}"

async def x_search(query, max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        r = await c.get(
            f"https://nitter.net/search?q={q}&f=tweets",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        tweets = re.findall(r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>', r.text, re.DOTALL)
        users = re.findall(r'<a class="username"[^>]*>([^<]+)</a>', r.text)
        if not tweets:
            return f"No results from X/Twitter for: {query}"
        lines = [f"X/Twitter results for: {query}\n"]
        for i, (tweet, user) in enumerate(zip(tweets[:max_results], users[:max_results])):
            clean = re.sub(r'<[^>]+>', '', tweet).strip()[:200]
            lines.append(f"{i+1}. @{user.strip()}: {clean}")
        return "\n".join(lines)
    except Exception as e:
        return f"X/Twitter search error: {e}"

async def social_search_all(query, max_per_source=3):
    results = {}
    tasks = [
        ("reddit", reddit_search(query, max_per_source)),
        ("hackernews", hackernews_search(query, max_per_source)),
        ("medium", medium_search(query, max_per_source)),
    ]
    for name, coro in tasks:
        try:
            results[name] = await coro
        except Exception as e:
            results[name] = f"[{name} error: {e}]"
    lines = [f"Social search results for: {query}\n"]
    for name in ("reddit", "hackernews", "medium"):
        res = results.get(name, "")
        if res and not res.startswith("No ") and not res.startswith("[") and not res.startswith(f"Reddit search error") and not res.startswith(f"HN search error") and not res.startswith(f"Medium search error"):
            head = res.split("\n")[0] if res else ""
            body = "\n".join(res.split("\n")[1:]) if res else ""
            lines.append(f"\n--- {head} ---")
            lines.append(body)
        elif not res.startswith("No"):
            lines.append(f"\n  [{name} unavailable]")
    if len(lines) < 3:
        lines.append("  No results from any platform.")
    return "\n".join(lines)

# ── 17. GITHUB SEARCH ─────────────────────────────────────

async def github_search(query, sort_by="stars", max_results=5):
    try:
        c = await get_http()
        q = urllib.parse.quote(query)
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_KEY", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        sort = "stars" if sort_by == "stars" else "updated"
        r = await c.get(
            f"https://api.github.com/search/repositories?q={q}&sort={sort}&order=desc&per_page={max_results}",
            headers=headers, timeout=15
        )
        if r.status_code != 200:
            return f"GitHub search error: {r.status_code} {r.text[:200]}"
        data = r.json()
        items = data.get("items", [])
        if not items:
            return f"No GitHub repos found for: {query}"
        lines = [f"GitHub repos for: {query} (sorted by {sort_by})\n"]
        for i, repo in enumerate(items):
            name = repo.get("full_name", "")
            desc = (repo.get("description", "") or "")[:120]
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            lang = repo.get("language", "N/A")
            topics = ", ".join(repo.get("topics", [])[:5]) or ""
            updated = (repo.get("updated_at", "") or "")[:10]
            topic_str = f" [{topics}]" if topics else ""
            lines.append(f"{i+1}. {name}{topic_str}")
            lines.append(f"   ⭐ {stars} | 🍴 {forks} | {lang} | Updated: {updated}")
            lines.append(f"   {desc[:120]}")
            lines.append(f"   https://github.com/{name}")
            if repo.get("homepage"):
                lines.append(f"   🌐 {repo['homepage']}")
        return "\n".join(lines)
    except Exception as e:
        return f"GitHub search error: {e}"

# ── 18. REPO ANALYZER ──────────────────────────────────

_ANALYZED_CACHE = {}
_ANALYZED_CACHE_MAX = 50

async def analyze_github_repo(url, depth="readme"):
    try:
        match = re.match(r"(?:https?://)?(?:www\.)?github\.com/([^/]+/[^/]+?)(?:/.*)?$", url)
        if not match:
            return "Invalid GitHub URL. Use format: https://github.com/user/repo"
        repo_full = match.group(1).rstrip("/")
        if repo_full in _ANALYZED_CACHE:
            return _ANALYZED_CACHE[repo_full]

        c = await get_http()
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_KEY", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = await c.get(f"https://api.github.com/repos/{repo_full}", headers=headers, timeout=15)
        if r.status_code != 200:
            return f"GitHub API error: {r.status_code} {r.text[:200]}"
        repo = r.json()

        readme_r = await c.get(f"https://api.github.com/repos/{repo_full}/readme", headers=headers, timeout=15)
        readme_text = ""
        if readme_r.status_code == 200:
            readme_data = readme_r.json()
            import base64
            try:
                readme_text = base64.b64decode(readme_data.get("content", "")).decode("utf-8", errors="replace")
            except Exception:
                readme_text = readme_data.get("content", "")

        contents_r = await c.get(f"https://api.github.com/repos/{repo_full}/contents", headers=headers, timeout=15)
        top_files = []
        if contents_r.status_code == 200:
            for item in contents_r.json()[:20]:
                top_files.append(f"{'📁' if item['type'] == 'dir' else '📄'} {item['name']}")

        languages_r = await c.get(f"https://api.github.com/repos/{repo_full}/languages", headers=headers, timeout=15)
        languages = {}
        if languages_r.status_code == 200:
            languages = languages_r.json()

        lang_summary = ", ".join(sorted(languages.keys(), key=lambda k: languages.get(k, 0), reverse=True)[:8]) if languages else "N/A"

        readme_summary = ""
        if readme_text:
            readme_lines = readme_text.strip().split("\n")
            text_lines = [l for l in readme_lines if not l.startswith("#") and not l.startswith("```") and not l.startswith("![")]
            clean = " ".join(l.strip() for l in text_lines if l.strip())[:3000]
            readme_summary = clean

        result_lines = [
            f"📦 {repo.get('full_name', repo_full)}",
            f"   {repo.get('description', 'No description') or 'No description'}",
            f"   ⭐ {repo.get('stargazers_count', 0)} | 🍴 {repo.get('forks_count', 0)} | {repo.get('open_issues_count', 0)} issues",
            f"   Language: {lang_summary}",
            f"   License: {(repo.get('license', {}) or {}).get('spdx_id', 'N/A') or 'N/A'}",
            f"   Topics: {', '.join(repo.get('topics', [])[:8]) or 'none'}",
            f"   Created: {(repo.get('created_at', '') or '')[:10]} | Updated: {(repo.get('updated_at', '') or '')[:10]}",
            f"   Homepage: {repo.get('homepage', 'N/A') or 'N/A'}",
            f"   URL: https://github.com/{repo_full}",
            "",
        ]
        if top_files:
            result_lines.append("📂 Top-level files:")
            result_lines.extend("   " + f for f in top_files)
            result_lines.append("")
        if repo.get("readme_url_download") or readme_text:
            result_lines.append("📖 README Summary:")
            result_lines.append(f"   {readme_summary[:1500] if readme_summary else '(README fetched but empty)'}")
            result_lines.append("")

        result = "\n".join(result_lines)
        if len(_ANALYZED_CACHE) >= _ANALYZED_CACHE_MAX:
            _ANALYZED_CACHE.clear()
        _ANALYZED_CACHE[repo_full] = result
        return result
    except Exception as e:
        return f"Repo analysis error: {e}"

# ── 19. REMINDERS ──────────────────────────────────────────

REMINDERS_FILE = os.path.join(BASE_DIR, "reminders.json")

class Reminders:
    def __init__(self):
        self.reminders = []
        self._load()

    def _load(self):
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, encoding="utf-8") as f:
                    self.reminders = json.load(f)
            except:
                pass

    def _save(self):
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.reminders, f, indent=2)

    def add(self, chat_id, delay_seconds, message):
        rid = hashlib.md5(f"{chat_id}{message}{time.time()}".encode()).hexdigest()[:8]
        self.reminders.append({
            "id": rid,
            "chat_id": chat_id,
            "fire_at": time.time() + delay_seconds,
            "message": message,
        })
        self._save()
        return rid

    def remove(self, rid):
        self.reminders = [r for r in self.reminders if r["id"] != rid]
        self._save()

    def list(self, chat_id=None):
        if chat_id:
            return [(r["id"], r["message"], r["fire_at"]) for r in self.reminders if r["chat_id"] == chat_id]
        return [(r["id"], r["message"], r["fire_at"]) for r in self.reminders]

    def due(self):
        now = time.time()
        return [r for r in self.reminders if r["fire_at"] <= now]

    def clear_chat(self, chat_id):
        self.reminders = [r for r in self.reminders if r["chat_id"] != chat_id]
        self._save()

reminder_db = Reminders()

async def run_reminder_loop(send_fn):
    while True:
        try:
            for r in reminder_db.due():
                try:
                    remaining = len(reminder_db.reminders)
                    await send_fn(r["chat_id"], f"⏰ Reminder: {r['message']}")
                    reminder_db.remove(r["id"])
                except:
                    pass
        except:
            pass
        await asyncio.sleep(10)

def parse_duration(text):
    text = text.strip().lower()
    total = 0
    patterns = [
        (r'(\d+)\s*(?:h|hour|hours)', 3600),
        (r'(\d+)\s*(?:m|min|minute|minutes)', 60),
        (r'(\d+)\s*(?:s|sec|second|seconds)', 1),
        (r'(\d+)\s*(?:d|day|days)', 86400),
    ]
    for pat, mul in patterns:
        m = re.search(pat, text)
        if m:
            total += int(m.group(1)) * mul
    return total if total > 0 else None

# ── 20. TRANSLATION ───────────────────────────────────────

async def translate(text, source="auto", target="en"):
    try:
        c = await get_http()
        r = await c.post(
            "https://libretranslate.com/translate",
            json={"q": text[:2000], "source": source, "target": target},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("translatedText", str(data))
        return f"Translation error: {r.status_code} — {r.text[:200]}"
    except Exception as e:
        return f"Translation error: {e}"

def parse_language_pair(text):
    pattern = r'^(\w{2,3}(?:-\w{2,3})?):(\w{2,3}(?:-\w{2,3})?)\s+(.*)'
    m = re.match(pattern, text, re.DOTALL)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, text

# ── 21. QR TOOLS ──────────────────────────────────────────

async def qr_encode(text):
    try:
        import qrcode, io
        from PIL import Image
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(text[:2000])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        return f"QR encode error: {e}"

async def qr_decode_from_url(photo_url):
    try:
        c = await get_http()
        img_data = (await c.get(photo_url)).content
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(img_data)
            fpath = f.name
        try:
            from PIL import Image
            try:
                from pyzbar.pyzbar import decode
                img = Image.open(fpath, encoding="utf-8")
                codes = decode(img)
                if codes:
                    return codes[0].data.decode("utf-8")
            except ImportError:
                pass
            result = subprocess.run(
                ["python", "-c", f"""
import sys
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    img = Image.open({repr(fpath, encoding="utf-8")})
    codes = decode(img)
    if codes: print(codes[0].data.decode('utf-8'))
    else: print('No QR code found')
except Exception as e:
    print(f'Error: {{e}}')
"""],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                out = result.stdout.strip()
                if out and "Error:" not in out and "No QR" not in out:
                    return out
        finally:
            os.unlink(fpath)
        c2 = await get_http()
        r = await c2.post(
            "https://api.qrserver.com/v1/read-qr-code/",
            files={"file": ("qr.png", img_data)},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                symbology = data[0].get("symbol", [{}])
                if symbology and len(symbology) > 0:
                    decoded = symbology[0].get("data")
                    if decoded:
                        return decoded
        return "Could not decode QR code."
    except Exception as e:
        return f"QR decode error: {e}"

# ── 22. ENHANCED DOCUMENT/PDF ANALYSIS ───────────────────

_PDF_CACHE = {}
_PDF_CACHE_MAX = 30

async def analyze_document(file_id, file_name, question=None):
    try:
        text = await extract_text_from_file(file_id, file_name)
        if not text or len(text) < 20:
            return "Could not extract meaningful text from this document."
        doc_id = hashlib.md5(f"{file_id}{file_name}".encode()).hexdigest()[:8]
        _PDF_CACHE[doc_id] = text[:50000]
        if len(_PDF_CACHE) > _PDF_CACHE_MAX:
            _PDF_CACHE.clear()
        ext = (file_name or "").lower()
        ftype = "PDF" if ext.endswith(".pdf") else "document"
        lines = [f"Document: {file_name} ({ftype})", f"Text length: {len(text)} chars", ""]
        if question:
            lines.append(f"Question: {question}")
            lines.append("")
        lines.append("--- Content Preview ---")
        preview = text[:3000]
        if len(text) > 3000:
            preview += "\n... (truncated)"
        lines.append(preview)
        return "\n".join(lines)
    except Exception as e:
        return f"Document analysis error: {e}"

async def ask_document(doc_id, question, smart_call_fn):
    text = _PDF_CACHE.get(doc_id, "")
    if not text:
        return "Document not found in cache. Please upload it again."
    prompt = f"Based on the following document text, answer: {question}\n\nDocument text:\n{text[:8000]}"
    try:
        result = await smart_call_fn([{"role": "user", "content": prompt}], None)
        return result[:4000] if result else "Could not analyze document."
    except Exception as e:
        return f"Analysis error: {e}"

async def analyze_document_with_vision(file_id, file_name, question, photo_url=None):
    if photo_url:
        desc = await vision_analyze(photo_url, question or "Describe this document/image in detail")
        return f"Document analysis ({file_name}):\n\n{desc}"
    return await analyze_document(file_id, file_name, question)

async def list_cached_documents():
    return list(_PDF_CACHE.keys())

async def clear_document_cache():
    _PDF_CACHE.clear()

async def extract_pdf_text_fallback(file_url):
    try:
        c = await get_http()
        content = (await c.get(file_url)).content
        try:
            import io, PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except ImportError:
            pass
        try:
            import io, pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            pass
        try:
            import io, pdfminer
            from pdfminer.high_level import extract_text as pdfminer_extract
            return pdfminer_extract(io.BytesIO(content))
        except ImportError:
            pass
        return "[PDF text extraction: no PDF library available. Install PyPDF2, pdfplumber, or pdfminer]"
    except Exception as e:
        return f"[PDF extraction error: {e}]"

class PageMonitor:
    def __init__(self):
        self.pages = {}
        self._load()

    def _load(self):
        if os.path.exists(PAGES_FILE):
            try:
                with open(PAGES_FILE, encoding="utf-8") as f:
                    self.pages = json.load(f)
            except:
                self.pages = {}

    def _save(self):
        with open(PAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.pages, f, indent=2)

    def add(self, url, chat_id, label=""):
        pid = hashlib.md5(f"{url}{chat_id}{time.time()}".encode()).hexdigest()[:8]
        self.pages[pid] = {"url": url, "chat_id": chat_id, "label": label or url[:40], "hash": "", "last_check": 0, "interval": 3600, "created": time.time()}
        self._save()
        return pid

    def remove(self, pid):
        self.pages.pop(pid, None)
        self._save()

    def list(self, chat_id=None):
        if chat_id:
            return [(pid, p["url"], p["label"], p["interval"]) for pid, p in self.pages.items() if p.get("chat_id") == chat_id]
        return [(pid, p["url"], p["label"], p["interval"]) for pid, p in self.pages.items()]

    def due(self):
        now = time.time()
        return [(pid, p) for pid, p in self.pages.items() if now - p.get("last_check", 0) >= p.get("interval", 3600)]

    async def check(self, pid, page, send_fn):
        try:
            c = await get_http()
            r = await c.get(page["url"], timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                return
            new_hash = hashlib.md5(r.text.encode()).hexdigest()
            old_hash = page.get("hash", "")
            if old_hash and new_hash != old_hash:
                import difflib
                old_text = ""
                try:
                    c2 = await get_http()
                    old_r = await c2.get(page["url"], timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    old_text = old_r.text[:500]
                except:
                    pass
                await send_fn(page["chat_id"], f"Page changed: {page['label']}\n{page['url']}")
            self.pages[pid]["hash"] = new_hash
            self.pages[pid]["last_check"] = time.time()
            self._save()
        except Exception as e:
            self.pages[pid]["last_check"] = time.time()
            self._save()

page_monitor = PageMonitor()

async def run_page_monitor_loop(send_fn):
    while True:
        try:
            for pid, page in page_monitor.due():
                await page_monitor.check(pid, page, send_fn)
        except:
            pass
        await asyncio.sleep(120)

# ── 23. USAGE STATS ───────────────────────────────────────

USAGE_FILE = os.path.join(BASE_DIR, "usage_stats.json")

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_usage(data):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def track_usage(user_id, agent, provider, tokens=0):
    data = load_usage()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"total_requests": 0, "total_tokens": 0, "agents": {}, "providers": {}, "first_seen": time.time()}
    data[uid]["total_requests"] += 1
    data[uid]["total_tokens"] += tokens
    data[uid]["last_seen"] = time.time()
    data[uid]["agents"][agent] = data[uid]["agents"].get(agent, 0) + 1
    data[uid]["providers"][provider] = data[uid]["providers"].get(provider, 0) + 1
    save_usage(data)

def get_usage(user_id):
    data = load_usage()
    uid = str(user_id)
    return data.get(uid, {})

def get_global_stats():
    data = load_usage()
    total_req = sum(u.get("total_requests", 0) for u in data.values())
    total_tok = sum(u.get("total_tokens", 0) for u in data.values())
    top_agents = {}
    top_providers = {}
    for uid, u in data.items():
        for a, c in u.get("agents", {}).items():
            top_agents[a] = top_agents.get(a, 0) + c
        for p, c in u.get("providers", {}).items():
            top_providers[p] = top_providers.get(p, 0) + c
    return {
        "total_users": len(data),
        "total_requests": total_req,
        "total_tokens": total_tok,
        "top_agents": sorted(top_agents.items(), key=lambda x: -x[1])[:5],
        "top_providers": sorted(top_providers.items(), key=lambda x: -x[1])[:5],
    }

# ── 24. CHAT WITH FILES (CSV/XLSX) ────────────────────────

async def parse_spreadsheet(file_id, file_name):
    try:
        c = await get_http()
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
        r = await c.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}")
        data = r.json()
        if not data.get("ok"):
            return None, "Could not fetch file."
        path = data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{path}"
        content = (await c.get(file_url)).content
        ext = (file_name or "").lower()
        if ext.endswith(".csv"):
            import io, csv as csv_mod
            decoded = content.decode("utf-8", errors="replace")
            reader = csv_mod.DictReader(io.StringIO(decoded))
            rows = list(reader)
            if not rows:
                return None, "Empty CSV."
            summary = f"CSV: {len(rows)} rows, {len(rows[0])} columns\nColumns: {', '.join(rows[0].keys())}\n\nFirst 5 rows:\n"
            for i, row in enumerate(rows[:5]):
                summary += f"Row {i+1}: {dict(row)}\n"
            return rows, summary
        elif ext.endswith((".xlsx", ".xls")):
            import openpyxl, io as io_mod
            wb = openpyxl.load_workbook(io_mod.BytesIO(content), read_only=True, data_only=True)
            ws = wb.active
            all_rows = []
            for row in ws.iter_rows(values_only=True):
                all_rows.append(list(row))
            if not all_rows:
                return None, "Empty spreadsheet."
            headers = [str(h) if h is not None else "" for h in all_rows[0]]
            summary = f"XLSX: {len(all_rows)-1} data rows, {len(headers)} columns\nColumns: {', '.join(headers)}\n\nFirst 5 rows:\n"
            for row in all_rows[1:6]:
                summary += f"  {dict(zip(headers, row))}\n"
            wb.close()
            return all_rows, summary
        else:
            return None, f"Unsupported format: {ext}. Use CSV or XLSX."
    except Exception as e:
        return None, f"Parse error: {e}"

# ── 25. PLUGIN SYSTEM ─────────────────────────────────────

PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")
_loaded_plugins = {}
_plugin_commands = {}

def init_plugins():
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    _loaded_plugins.clear()
    _plugin_commands.clear()
    init_file = os.path.join(PLUGINS_DIR, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("# plugins package\n")

async def load_plugin(url_or_path):
    await init_plugins()
    try:
        import importlib, sys, urllib.parse, tempfile, pathlib
        if url_or_path.startswith(("http://", "https://")):
            c = await get_http()
            r = await c.get(url_or_path, timeout=30)
            if r.status_code != 200:
                return f"Failed to fetch plugin: HTTP {r.status_code}"
            code = r.text
            parsed = urllib.parse.urlparse(url_or_path)
            name = os.path.splitext(os.path.basename(parsed.path))[0]
            if not name:
                name = f"plugin_{hashlib.md5(url_or_path.encode()).hexdigest()[:8]}"
        else:
            abs_path = os.path.abspath(url_or_path)
            if not abs_path.startswith(os.path.abspath(PLUGINS_DIR)):
                return f"Security: can only load plugins from '{PLUGINS_DIR}' directory"
            with open(abs_path, encoding="utf-8") as f:
                code = f.read()
            name = os.path.splitext(os.path.basename(abs_path))[0]
        spec = importlib.util.spec_from_loader(name, None)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        exec(compile(code, f"{name}.py", "exec"), module.__dict__)
        commands = getattr(module, "COMMANDS", {})
        if commands:
            _loaded_plugins[name] = module
            _plugin_commands.update(commands)
            cmds = ", ".join(commands.keys())
            return f"Plugin '{name}' loaded. Commands: {cmds}"
        return f"Plugin '{name}' loaded (no COMMANDS dict found)."
    except Exception as e:
        return f"Plugin load error: {e}"

def list_plugins():
    return [(k, list(getattr(v, "COMMANDS", {}).keys())) for k, v in _loaded_plugins.items()]

def get_plugin_command(cmd):
    return _plugin_commands.get(cmd)

async def init_plugins_from_dir():
    await init_plugins()
    if not os.path.exists(PLUGINS_DIR):
        return
    for fname in os.listdir(PLUGINS_DIR):
        if fname.endswith(".py") and fname != "__init__.py":
            await load_plugin(os.path.join(PLUGINS_DIR, fname))
