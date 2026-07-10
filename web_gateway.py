import asyncio, json, os, time, threading, urllib.parse
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_FILE = os.path.join(BASE_DIR, "providers.json")
SYNOXCLOUD_AI_MODELS_FILE = os.path.join(BASE_DIR, "synoxcloud_ai_models.json")

app = FastAPI(title="OpenCode AI Gateway")

PROVIDERS = {}
SYNOXCLOUD_AI_MODELS = {}
_http = None

def _is_configured(key):
    return bool(key) and "YOUR_" not in key and key != "not configured"

def _load_providers():
    global PROVIDERS, SYNOXCLOUD_AI_MODELS
    PROVIDERS = {
        "nvidia": {"url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "meta/llama-3.3-70b-instruct", "key": os.environ.get("NVIDIA_KEY", "not configured")},
        "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile", "key": os.environ.get("GROQ_KEY", "not configured")},
        "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", "model": "gemini-2.0-flash", "key": os.environ.get("GEMINI_KEY", "not configured")},
        "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "gryphe/mythomax-l2-13b", "key": os.environ.get("OPENROUTER_KEY", "not configured")},
        "deepseek": {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat", "key": os.environ.get("DEEPSEEK_KEY", "not configured")},
        "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-small-latest", "key": os.environ.get("MISTRAL_KEY", "not configured")},
        "sambanova": {"url": "https://api.sambanova.ai/v1/chat/completions", "model": "Meta-Llama-3.3-70B-Instruct", "key": os.environ.get("SAMBANOVA_KEY", "not configured")},
        "cerebras": {"url": "https://api.cerebras.ai/v1/chat/completions", "model": "llama3.1-70b", "key": os.environ.get("CEREBRAS_KEY", "not configured")},
        "cohere": {"url": "https://api.cohere.ai/v1/chat/completions", "model": "command-r-plus-08-2024", "key": os.environ.get("COHERE_KEY", "not configured")},
        "xai": {"url": "https://api.x.ai/v1/chat/completions", "model": "grok-2-1212", "key": os.environ.get("XAI_KEY", "not configured")},
        "github": {"url": "https://models.inference.ai.azure.com/chat/completions", "model": "gpt-4o", "key": os.environ.get("GITHUB_KEY", "not configured")},
        "together": {"url": "https://api.together.xyz/v1/chat/completions", "model": "mistralai/Mixtral-8x22B-Instruct-v0.1", "key": os.environ.get("TOGETHER_KEY", "not configured")},
        "fireworks": {"url": "https://api.fireworks.ai/inference/v1/chat/completions", "model": "accounts/fireworks/models/llama-v3p3-70b-instruct", "key": os.environ.get("FIREWORKS_KEY", "not configured")},
        "lepton": {"url": "https://mixtral-8x22b.lepton.run/api/v1/chat/completions", "model": "mixtral-8x22b", "key": os.environ.get("LEPTON_KEY", "not configured")},
        "synoxcloud": {"url": "https://api.synoxcloud.xyz/api/ai-chat", "model": "gpt-5", "key": "free"},
        "hy3": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "tencent/hy3", "key": os.environ.get("OPENROUTER_KEY", "not configured")},
        "hy3-preview": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "tencent/hy3-preview", "key": os.environ.get("OPENROUTER_KEY", "not configured")},
    }
    if os.path.exists(PROVIDERS_FILE):
        try:
            with open(PROVIDERS_FILE) as f:
                PROVIDERS.update(json.load(f))
        except:
            pass
    if os.path.exists(SYNOXCLOUD_AI_MODELS_FILE):
        try:
            with open(SYNOXCLOUD_AI_MODELS_FILE, encoding="utf-8") as f:
                SYNOXCLOUD_AI_MODELS = json.load(f)
            for _mid in SYNOXCLOUD_AI_MODELS:
                _key = "synox-" + _mid
                if _key not in PROVIDERS:
                    PROVIDERS[_key] = {"url": "https://api.synoxcloud.xyz/ai-chat", "model": _mid, "key": "free"}
        except:
            pass

_load_providers()

async def get_http():
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(timeout=120, limits=httpx.Limits(max_keepalive_connections=10, max_connections=20))
    return _http

def get_available_providers():
    return [{"id": k, "model": v.get("model", ""), "configured": _is_configured(v.get("key", ""))} for k, v in PROVIDERS.items()]

def get_available_models():
    models = []
    for pid, p in PROVIDERS.items():
        configured = _is_configured(p.get("key", ""))
        models.append({"id": pid, "model": p["model"], "provider": pid, "configured": configured})
    return models

async def call_provider(messages, provider_id):
    p = PROVIDERS.get(provider_id)
    if not p:
        return {"error": "Unknown provider: " + provider_id}
    c = await get_http()
    if provider_id == "gemini":
        parts = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            parts.append({"role": role, "parts": [{"text": m["content"]}]})
        r = await c.post(p["url"] + "?key=" + p["key"], json={"contents": parts})
        if r.status_code == 200:
            data = r.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))
                return {"content": text}
            return {"error": str(data)}
        return {"error": "Gemini error: " + str(r.status_code)}
    elif provider_id == "synoxcloud" or provider_id.startswith("synox-"):
        last = [m for m in messages if m["role"] == "user"]
        if not last:
            return {"error": "No user message"}
        prompt = last[-1]["content"]
        model_id = p.get("model", "gpt-5")
        model_info = SYNOXCLOUD_AI_MODELS.get(model_id, {})
        if model_info and isinstance(model_info, dict) and model_info.get("path"):
            ep_path = model_info["path"].split("?")[0]
            raw_params = model_info.get("params", [])
            param_names = [pp.split("=")[0] for pp in raw_params if isinstance(pp, str) and "=" in pp]
            recommended = param_names[0] if param_names else "q"
            url = "https://api.synoxcloud.xyz" + ep_path + "?" + recommended + "=" + urllib.parse.quote(prompt)
        else:
            url = p["url"] + "/" + model_id + "?q=" + urllib.parse.quote(prompt)
        key = p.get("key", "")
        if _is_configured(key) and key != "free":
            url += "&apikey=" + key
        try:
            r = await c.get(url)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    for k in ("result", "response", "message", "text", "data", "content"):
                        if k in data:
                            return {"content": str(data[k])}
                    return {"content": str(data)[:2000]}
                return {"content": str(data)[:2000]}
            return {"error": "SynoxCloud error: " + str(r.status_code)}
        except Exception as e:
            return {"error": str(e)}
    else:
        headers = {"Content-Type": "application/json"}
        if p.get("key") and p["key"] != "skip-auth":
            headers["Authorization"] = "Bearer " + p["key"]
        body = {"model": p["model"], "messages": messages, "max_tokens": 4096}
        try:
            r = await c.post(p["url"], json=body, headers=headers)
            if r.status_code == 200:
                content = r.json().get("choices", [{}])[0].get("message", {}).get("content", str(r.json()))
                return {"content": content}
            return {"error": str(r.status_code) + ": " + r.text[:300]}
        except Exception as e:
            return {"error": str(e)}

_WEB_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OpenCode AI Gateway</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;height:100vh;display:flex;flex-direction:column}
  header{background:#161b22;padding:12px 24px;border-bottom:1px solid #30363d;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
  h1{font-size:16px;font-weight:600}
  .model-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  select{background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:6px 12px;border-radius:6px;font-size:13px}
  #chat{flex:1;overflow-y:auto;padding:20px 24px;display:flex;flex-direction:column;gap:16px}
  .msg{max-width:720px;padding:12px 16px;border-radius:8px;line-height:1.6;font-size:14px;white-space:pre-wrap}
  .user{background:#1f6feb22;border:1px solid #1f6feb44;align-self:flex-end}
  .assistant{background:#161b22;border:1px solid #30363d;align-self:flex-start}
  .error{background:#da363322;border:1px solid #da363344;align-self:flex-start;color:#f85149}
  .loading{background:#161b22;border:1px solid #30363d;align-self:flex-start;color:#8b949e;font-style:italic}
  #input-area{background:#161b22;border-top:1px solid #30363d;padding:12px 24px;display:flex;gap:10px}
  #input{flex:1;background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:10px 14px;border-radius:6px;font-size:14px;resize:none;outline:none}
  #input:focus{border-color:#1f6feb}
  button{background:#238636;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer}
  button:hover{background:#2ea043}
  button:disabled{background:#23863644;cursor:not-allowed}
  .status-dot{width:8px;height:8px;border-radius:50%;display:inline-block}
  .ok{background:#3fb950}
  .bad{background:#f85149}
</style>
</head>
<body>
<header>
  <div style="display:flex;align-items:center;gap:12px">
    <h1>OpenCode AI Gateway</h1>
    <span style="font-size:12px;color:#8b949e">__READY_COUNT__/__MODEL_COUNT__ providers ready</span>
  </div>
  <div class="model-row">
    <label style="font-size:13px;color:#8b949e">Model:</label>
    <select id="model-select">__MODEL_OPTIONS____UNCONFIGURED_OPTIONS__</select>
  </div>
</header>
<div id="chat"></div>
<div id="input-area">
  <textarea id="input" rows="2" placeholder="Type a message..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
  <button id="send-btn" onclick="send()">Send</button>
</div>
<script>
const chat=document.getElementById('chat');
const input=document.getElementById('input');
const btn=document.getElementById('send-btn');
const sel=document.getElementById('model-select');
let history=[];
function addMsg(role,content){
  const d=document.createElement('div');
  d.className='msg '+(role==='user'?'user':role==='error'?'error':'assistant');
  d.textContent=content;
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}
async function send(){
  const text=input.value.trim();
  if(!text)return;
  const model=sel.value;
  addMsg('user',text);
  input.value='';
  btn.disabled=true;
  const ld=document.createElement('div');
  ld.className='msg loading';
  ld.textContent='Thinking...';
  chat.appendChild(ld);
  history.push({role:'user',content:text});
  try{
    const r=await fetch('/v1/chat/completions',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({model:model,messages:history.slice(-20)})
    });
    const j=await r.json();
    ld.remove();
    if(j.choices&&j.choices[0]){
      const reply=j.choices[0].message.content;
      addMsg('assistant',reply);
      history.push({role:'assistant',content:reply});
    }else{
      addMsg('error',j.error?.message||'No response');
    }
  }catch(e){
    ld.remove();
    addMsg('error','Error: '+e.message);
  }
  btn.disabled=false;
}
</script>
</body>
</html>"""

@app.get("/")
async def web_ui():
    models = get_available_models()
    configured = [m for m in models if m["configured"]]
    unconfigured = [m for m in models if not m["configured"]]
    opts = "".join("".join(('<option value="', m["id"], '">', m["provider"], " — ", m["model"], "</option>")) for m in configured)
    uopts = "".join("".join(('<option value="', m["id"], '" disabled>', m["provider"], " — ", m["model"], " (not configured)</option>")) for m in unconfigured)
    html = _WEB_HTML_TEMPLATE.replace("__READY_COUNT__", str(len(configured)))
    html = html.replace("__MODEL_COUNT__", str(len(models)))
    html = html.replace("__MODEL_OPTIONS__", opts)
    html = html.replace("__UNCONFIGURED_OPTIONS__", uopts)
    return HTMLResponse(html)

@app.get("/api/models")
async def list_models():
    return JSONResponse(get_available_models())

@app.get("/api/providers")
async def list_providers():
    return JSONResponse(get_available_providers())

@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    body = await req.json()
    model_id = body.get("model", "groq")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    if not messages:
        return JSONResponse({"error": {"message": "No messages"}}, status_code=400)
    if model_id not in PROVIDERS:
        return JSONResponse({"error": {"message": "Unknown model: " + model_id}}, status_code=400)
    if stream:
        async def gen():
            result = await call_provider(messages, model_id)
            content = result.get("content", result.get("error", ""))
            chunk = json.dumps({"choices": [{"delta": {"content": content}, "index": 0}]})
            yield "data: " + chunk + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(gen(), media_type="text/event-stream")
    result = await call_provider(messages, model_id)
    content = result.get("content", "")
    error = result.get("error")
    if error:
        return JSONResponse({"error": {"message": error}}, status_code=500)
    return JSONResponse({
        "id": "chatcmpl-" + str(int(time.time())),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_id,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })

def run(port=4357, host="0.0.0.0"):
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")

def start(port=4357, host="0.0.0.0"):
    t = threading.Thread(target=run, args=(port, host), daemon=True)
    t.start()
    return "Gateway running on http://" + host + ":" + str(port)

if __name__ == "__main__":
    run()
