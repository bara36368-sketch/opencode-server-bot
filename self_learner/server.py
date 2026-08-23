"""Self-learning brain server (:4590).

/v1/chat/completions  OpenAI-compatible. Every request is enriched with
                      retrieved experiences from knowledge memory before
                      hitting the local model (Ollama) - cloud fallback via
                      OMNI Gateway when Ollama is down.
/api/stats            memory statistics
/api/study            trigger a study cycle NOW (asks other AIs, learns)
/api/search?q=        query the knowledge base directly

Local backend: first model from `ollama list` (dolphin3-coder etc.).
Cloud backend: OMNI Gateway :4455 ranked free models.
"""
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import memory

PORT = int(os.environ.get("BRAIN_PORT", "4590"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OMNI_CHAT = os.environ.get("OMNI_BASE", "http://127.0.0.1:4455") + "/api/chat"
STUDY_INTERVAL_H = float(os.environ.get("BRAIN_STUDY_INTERVAL_H", "6"))
MEMORY_LIMIT = int(os.environ.get("BRAIN_MEMORY_LIMIT", "6"))
_ollama_cache = {"name": None, "ts": 0.0}
_study_lock = threading.Lock()


def local_model_name():
    now = time.time()
    if _ollama_cache["name"] and now - _ollama_cache["ts"] < 300:
        return _ollama_cache["name"]
    name = None
    try:
        with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=3) as r:
            models = json.loads(r.read().decode()).get("models", [])
        if models:
            name = models[0]["name"]
    except Exception:
        name = None
    _ollama_cache.update({"name": name, "ts": now})
    return name


def omni_fallback(messages):
    payload = json.dumps({"model": "auto", "messages": messages,
                          "max_tokens": 1500}).encode()
    req = urllib.request.Request(OMNI_CHAT, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode("utf-8", "replace")).get("reply", "")


def build_system_prompt(query_hint):
    exps = memory.search(query_hint or "", limit=MEMORY_LIMIT)
    if not exps:
        return None, []
    lines = ["You have a personal knowledge memory of past multi-AI studied "
             "experiences. Use these learned insights when relevant; they were "
             "cross-checked from multiple AI sources (agreement-scored):", ""]
    used = []
    for e in exps:
        lines.append(f"[LEARNED | topic={e['topic']} | {e['age_days']}d ago | "
                     f"confidence {e['score']:.2f} | sources {len(e['sources'])}]")
        lines.append(f"Q: {e['question']}")
        lines.append(f"A: {e['answer'][:1200]}")
        lines.append("")
        used.append({"topic": e["topic"], "score": e["score"]})
    return "\n".join(lines), used


def answer(user_text):
    sys_prompt, used = build_system_prompt(user_text)
    messages = []
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})
    messages.append({"role": "user", "content": user_text})

    model = local_model_name()
    if model:
        try:
            payload = json.dumps({"model": model, "messages": messages,
                                  "stream": False}).encode()
            req = urllib.request.Request(OLLAMA_URL + "/v1/chat/completions",
                                         data=payload,
                                         headers={"Content-Type": "application/json"},
                                         method="POST")
            with urllib.request.urlopen(req, timeout=600) as r:
                body = json.loads(r.read().decode())
                reply = (body.get("choices") or [{}])[0].get("message", {}).get("content", "")
                return reply, {"backend": f"local:{model}", "memories_used": used}
        except Exception as e:
            print(f"[brain] local backend failed ({e}), falling back to OMNI")
    reply = omni_fallback(messages)
    return reply, {"backend": "omni-gateway", "memories_used": used}


def study_worker():
    import collector
    while True:
        if _study_lock.acquire(blocking=False):
            try:
                print("[brain] autonomous study cycle starting...")
                collector.study_cycle()
            except Exception as e:
                print(f"[brain] study cycle error: {e}")
            finally:
                _study_lock.release()
        time.sleep(max(0.5, STUDY_INTERVAL_H) * 3600)


def start_autonomous_study():
    t = threading.Thread(target=study_worker, daemon=True)
    t.start()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/api/stats":
            s = memory.stats()
            s["local_model"] = local_model_name() or "(ollama down - cloud fallback)"
            s["autonomous_study_every_h"] = STUDY_INTERVAL_H
            return self._send(200, s)
        if p == "/api/search":
            q = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query).get("q", [""])[0]
            return self._send(200, {"results": memory.search(q, limit=10)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8", "replace") or "{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        p = self.path.split("?")[0]
        if p == "/api/study":
            topics = payload.get("topics")
            n = int(payload.get("n", 3))
            if not _study_lock.acquire(blocking=False):
                return self._send(202, {"status": "study already running"})
            try:
                import collector
                res = collector.study_cycle(n_topics=n, topics=topics)
                return self._send(200, res)
            except Exception as e:
                return self._send(500, {"error": str(e)[:200]})
            finally:
                _study_lock.release()
        if p == "/v1/chat/completions":
            msgs = payload.get("messages") or []
            user_text = next((m.get("content", "") for m in reversed(msgs)
                              if m.get("role") == "user"), "")
            try:
                reply, meta = answer(user_text)
            except Exception as e:
                return self._send(502, {"error": str(e)[:300]})
            resp = {
                "id": f"brain-{int(time.time()*1000)}",
                "object": "chat.completion",
                "model": meta.get("backend", "brain"),
                "choices": [{"index": 0,
                             "message": {"role": "assistant", "content": reply},
                             "finish_reason": "stop"}],
                "omni_brain": meta,
            }
            return self._send(200, resp)
        return self._send(404, {"error": "not found"})


def main():
    memory.init_db()
    start_autonomous_study()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[brain] self-learning AI on http://127.0.0.1:{PORT} "
          f"(study every {STUDY_INTERVAL_H}h, memory={memory.DB_PATH})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
