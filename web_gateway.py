import asyncio, json, os, time, threading, urllib.parse, copy, uuid
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_FILE = os.path.join(BASE_DIR, "providers.json")
SYNOXCLOUD_AI_MODELS_FILE = os.path.join(BASE_DIR, "synoxcloud_ai_models.json")
WORKFLOWS_FILE = os.path.join(BASE_DIR, "workflows.json")

app = FastAPI(title="OpenCode AI Gateway")

PROVIDERS = {}
SYNOXCLOUD_AI_MODELS = {}
_http = None

PROVIDER_ROLES = {
    "zenmux": {"role": "Strategist", "emoji": "\u265F\uFE0F", "color": "#8b5cf6",
               "desc": "Strategic multi-step reasoning with Grok 4.5 Free",
               "system_prompt": "You are a strategist. Think several steps ahead, consider multiple perspectives, and provide strategic recommendations."},
    "groq": {"role": "Researcher", "emoji": "\U0001F52C", "color": "#10b981",
             "desc": "Fast research and information synthesis",
             "system_prompt": "You are a research assistant. Gather, synthesize, and present information clearly with citations where possible."},
    "gemini": {"role": "Analyst", "emoji": "\U0001F4CA", "color": "#3b82f6",
               "desc": "Multimodal analysis and pattern recognition",
               "system_prompt": "You are an analyst. Examine data critically, identify patterns, and provide insightful analysis with evidence."},
    "deepseek": {"role": "Coder", "emoji": "\U0001F4BB", "color": "#06b6d4",
                 "desc": "Code generation and software architecture",
                 "system_prompt": "You are a senior software engineer. Write clean, efficient, well-documented code following best practices."},
    "mistral": {"role": "Writer", "emoji": "\u270D\uFE0F", "color": "#f59e0b",
                "desc": "Creative and technical writing",
                "system_prompt": "You are a professional writer. Produce clear, engaging, and well-structured content tailored to the audience."},
    "nvidia": {"role": "Scientist", "emoji": "\U0001F52A", "color": "#76b900",
               "desc": "Technical and scientific reasoning",
               "system_prompt": "You are a scientist. Apply rigorous reasoning, cite evidence, and explain technical concepts precisely."},
    "openrouter": {"role": "Generalist", "emoji": "\U0001F9E0", "color": "#a855f7",
                   "desc": "Versatile general-purpose AI",
                   "system_prompt": "You are a helpful general assistant. Answer questions thoroughly, accurately, and adapt to any domain."},
    "cohere": {"role": "Summarizer", "emoji": "\U0001F4DD", "color": "#ec4899",
               "desc": "Document analysis and summarization",
               "system_prompt": "You are a summarization specialist. Condense information while preserving key points, context, and nuance."},
    "xai": {"role": "Explainer", "emoji": "\U0001F50D", "color": "#ef4444",
            "desc": "Clear explanations of complex topics",
            "system_prompt": "You are an explainer. Break down complex topics into clear, understandable explanations with examples."},
    "github": {"role": "Developer", "emoji": "\U0001F6E0\uFE0F", "color": "#2da44e",
               "desc": "Code review and software development",
               "system_prompt": "You are a developer. Build and review code with best practices, testing, and maintainability in mind."},
    "together": {"role": "Creator", "emoji": "\U0001F3A8", "color": "#8b5cf6",
                 "desc": "Creative content generation",
                 "system_prompt": "You are a creative AI. Generate imaginative, original content with flair and originality."},
    "fireworks": {"role": "Optimizer", "emoji": "\u26A1", "color": "#f97316",
                  "desc": "Performance optimization and refinement",
                  "system_prompt": "You are an optimizer. Improve and refine content for clarity, impact, and effectiveness."},
    "cerebras": {"role": "Speedster", "emoji": "\U0001F3CE\uFE0F", "color": "#14b8a6",
                 "desc": "Ultra-fast responses for simple tasks",
                 "system_prompt": "You are a rapid-response AI. Provide quick, accurate answers without unnecessary verbosity."},
    "sambanova": {"role": "Reasoner", "emoji": "\U0001F9EE", "color": "#6366f1",
                  "desc": "Deep logical reasoning",
                  "system_prompt": "You are a reasoning engine. Think step-by-step, show your work, and reach logical conclusions."},
    "lepton": {"role": "Advisor", "emoji": "\U0001F4A1", "color": "#eab308",
               "desc": "Strategic advice and consulting",
               "system_prompt": "You are an advisor. Provide strategic guidance, actionable recommendations, and consider trade-offs."},
    "synoxcloud": {"role": "Assistant", "emoji": "\U0001F916", "color": "#6b7280",
                   "desc": "General-purpose AI assistant via SynoxCloud",
                   "system_prompt": "You are a helpful assistant. Be concise, accurate, and friendly."},
    "hy3": {"role": "Thinker", "emoji": "\U0001F4AD", "color": "#d946ef",
            "desc": "Deep thinking with Hy3 model",
            "system_prompt": "You are a deep thinker. Explore ideas thoroughly and provide nuanced perspectives."},
    "hy3-preview": {"role": "Pioneer", "emoji": "\U0001F680", "color": "#f43f5e",
                    "desc": "Cutting-edge Hy3 preview model",
                    "system_prompt": "You are a pioneer. Explore new ideas and push boundaries in your analysis."},
}

def _is_configured(key):
    return bool(key) and "YOUR_" not in key and key != "not configured"

def _load_providers():
    global PROVIDERS, SYNOXCLOUD_AI_MODELS
    PROVIDERS = {
        "zenmux": {"url": "https://zenmux.ai/api/v1/chat/completions", "model": "x-ai/grok-4.5-free", "key": os.environ.get("ZENMUX_KEY", "not configured")},
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

WORKFLOWS = {}
_next_wf_id = 1

def _load_workflows():
    global WORKFLOWS, _next_wf_id
    if os.path.exists(WORKFLOWS_FILE):
        try:
            with open(WORKFLOWS_FILE) as f:
                data = json.load(f)
                WORKFLOWS = data.get("workflows", {})
                _next_wf_id = data.get("next_id", 1)
        except:
            pass

def _save_workflows():
    try:
        with open(WORKFLOWS_FILE, "w") as f:
            json.dump({"workflows": WORKFLOWS, "next_id": _next_wf_id}, f, indent=2)
    except:
        pass

_load_workflows()

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

# ---- Workflow Engine ----

def _toposort(nodes, edges):
    in_deg = {n["id"]: 0 for n in nodes}
    adj = {n["id"]: [] for n in nodes}
    for e in edges:
        if e["source"] in adj and e["target"] in in_deg:
            adj[e["source"]].append(e["target"])
            in_deg[e["target"]] = in_deg.get(e["target"], 0) + 1
    queue = [nid for nid, d in in_deg.items() if d == 0]
    order = []
    while queue:
        nid = queue.pop(0)
        order.append(nid)
        for nb in adj.get(nid, []):
            in_deg[nb] -= 1
            if in_deg[nb] == 0:
                queue.append(nb)
    return order

def _get_role(provider_id):
    return PROVIDER_ROLES.get(provider_id, PROVIDER_ROLES.get("openrouter"))

async def execute_workflow(workflow, initial_input=""):
    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])
    if not nodes:
        return {"error": "Workflow has no nodes"}
    
    node_map = {n["id"]: n for n in nodes}
    order = _toposort(nodes, edges)
    
    in_edges = {n["id"]: [] for n in nodes}
    for e in edges:
        if e["target"] in in_edges:
            in_edges[e["target"]].append(e["source"])
    
    results = {}
    errors = {}
    steps = []
    
    for nid in order:
        node = node_map.get(nid)
        if not node:
            continue
        pid = node.get("provider", "openrouter")
        p = PROVIDERS.get(pid)
        if not p:
            errors[nid] = f"Unknown provider: {pid}"
            steps.append({"node_id": nid, "node_name": node.get("label", nid), "status": "error", "error": errors[nid]})
            continue
        if not _is_configured(p.get("key", "")):
            errors[nid] = f"Provider {pid} not configured"
            steps.append({"node_id": nid, "node_name": node.get("label", nid), "status": "error", "error": errors[nid]})
            continue
        
        role = _get_role(pid)
        sys_prompt = node.get("system_prompt") or role.get("system_prompt", "You are a helpful assistant.")
        temperature = node.get("temperature", 0.7)
        
        upstream = in_edges.get(nid, [])
        context_parts = []
        for uid in upstream:
            if uid in results:
                context_parts.append(f"From {node_map.get(uid, {}).get('label', uid)}:\n{results[uid]}")
        
        if initial_input and not upstream:
            context_parts.append(f"User input:\n{initial_input}")
        
        messages = [{"role": "system", "content": sys_prompt}]
        if context_parts:
            messages.append({"role": "user", "content": "\n\n".join(context_parts)})
        
        start = time.time()
        try:
            result = await call_provider_internal(messages, pid)
            elapsed = time.time() - start
            content = result.get("content", "")
            error = result.get("error")
            if error:
                errors[nid] = error
                steps.append({"node_id": nid, "node_name": node.get("label", nid), "status": "error", "error": error, "elapsed": round(elapsed, 2)})
            else:
                results[nid] = content
                steps.append({"node_id": nid, "node_name": node.get("label", nid), "status": "ok", "elapsed": round(elapsed, 2), "preview": content[:200]})
        except Exception as e:
            errors[nid] = str(e)
            steps.append({"node_id": nid, "node_name": node.get("label", nid), "status": "error", "error": str(e)})
    
    final_nodes = [nid for nid in node_map if nid not in [e["source"] for e in edges]]
    final_output = "\n\n".join(results.get(nid, "") for nid in final_nodes if nid in results)
    
    return {
        "workflow_id": workflow.get("id"),
        "workflow_name": workflow.get("name", "Untitled"),
        "steps": steps,
        "results": results,
        "errors": errors,
        "final_output": final_output,
        "total_nodes": len(nodes),
        "success_count": sum(1 for s in steps if s["status"] == "ok"),
        "error_count": sum(1 for s in steps if s["status"] == "error"),
        "total_time": round(sum(s.get("elapsed", 0) for s in steps), 2),
    }

async def call_provider_internal(messages, provider_id):
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

async def call_provider(messages, provider_id):
    return await call_provider_internal(messages, provider_id)

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
  nav{display:flex;gap:12px;align-items:center}
  nav a{color:#58a6ff;text-decoration:none;font-size:13px;padding:4px 10px;border-radius:4px;border:1px solid #30363d}
  nav a:hover{background:#1f6feb22;border-color:#1f6feb}
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
  <nav>
    <a href="/">Chat</a>
    <a href="/workflow">Workflow Builder</a>
    <div class="model-row">
      <label style="font-size:13px;color:#8b949e">Model:</label>
      <select id="model-select">__MODEL_OPTIONS____UNCONFIGURED_OPTIONS__</select>
    </div>
  </nav>
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

_WORKFLOW_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OpenCode AI Workflow Builder</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
  
  header{background:#161b22;padding:8px 16px;border-bottom:1px solid #30363d;display:flex;align-items:center;gap:12px;flex-shrink:0;z-index:10}
  header h1{font-size:14px;font-weight:600}
  header a{color:#58a6ff;text-decoration:none;font-size:12px;padding:3px 8px;border-radius:4px;border:1px solid #30363d}
  header a:hover{background:#1f6feb22}
  .wf-name{background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:4px 10px;border-radius:4px;font-size:13px;width:200px;outline:none}
  .wf-name:focus{border-color:#1f6feb}
  .toolbar{display:flex;gap:6px;align-items:center;margin-left:auto}
  .toolbar button{background:#21262d;color:#e6edf3;border:1px solid #30363d;padding:5px 12px;border-radius:4px;font-size:12px;cursor:pointer}
  .toolbar button:hover{background:#30363d}
  .toolbar .primary{background:#238636;border-color:#238636;color:#fff}
  .toolbar .primary:hover{background:#2ea043}
  .toolbar .danger{color:#f85149;border-color:#f8514944}
  .toolbar .danger:hover{background:#f8514922}
  .toolbar select{background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:4px 8px;border-radius:4px;font-size:12px}
  
  #main{display:flex;flex:1;overflow:hidden}
  
  /* Palette */
  #palette{width:220px;background:#161b22;border-right:1px solid #30363d;overflow-y:auto;flex-shrink:0}
  #palette h3{font-size:11px;font-weight:600;text-transform:uppercase;color:#8b949e;padding:10px 12px 6px;letter-spacing:0.5px}
  .palette-item{padding:6px 12px;cursor:grab;display:flex;align-items:center;gap:8px;border-bottom:1px solid #21262d;transition:background .15s;user-select:none}
  .palette-item:hover{background:#1f6feb11}
  .palette-item .emoji{font-size:16px;width:24px;text-align:center}
  .palette-item .info{flex:1;min-width:0}
  .palette-item .name{font-size:12px;font-weight:500}
  .palette-item .role{font-size:10px;color:#8b949e}
  .palette-item .status{width:6px;height:6px;border-radius:50%;flex-shrink:0}
  .palette-item.dragging{opacity:0.4}
  
  /* Canvas */
  #canvas-wrap{flex:1;position:relative;overflow:hidden;background:#0d1117;background-image:radial-gradient(circle,#1c2333 1px,transparent 1px);background-size:20px 20px}
  #canvas{position:absolute;top:0;left:0;width:100%;height:100%}
  #svg-layer{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1}
  #svg-layer line,#svg-layer path{pointer-events:stroke;cursor:pointer}
  
  /* Nodes */
  .wf-node{position:absolute;width:180px;background:#161b22;border:1px solid #30363d;border-radius:8px;cursor:move;z-index:2;box-shadow:0 4px 12px rgba(0,0,0,.3);user-select:none;transition:box-shadow .15s}
  .wf-node:hover{box-shadow:0 6px 20px rgba(0,0,0,.4)}
  .wf-node.selected{border-color:#58a6ff;box-shadow:0 0 0 1px #58a6ff44,0 6px 20px rgba(0,0,0,.4)}
  .wf-node.executing{animation:pulse-border 1s ease-in-out infinite}
  .wf-node.done{border-color:#3fb950}
  .wf-node.error{border-color:#f85149}
  @keyframes pulse-border{0%,100%{border-color:#58a6ff}50%{border-color:#58a6ff88}}
  .wf-node .header{display:flex;align-items:center;gap:6px;padding:8px 10px;border-radius:7px 7px 0 0;font-size:12px;font-weight:500}
  .wf-node .body{padding:6px 10px;font-size:11px;color:#8b949e;border-top:1px solid #21262d}
  .wf-node .body .provider-name{color:#e6edf3;font-size:11px}
  .wf-node .port{width:10px;height:10px;border-radius:50%;background:#30363d;border:2px solid #58a6ff;position:absolute;left:50%;margin-left:-5px;cursor:crosshair;z-index:3;transition:all .15s}
  .wf-node .port:hover{background:#58a6ff;transform:scale(1.3)}
  .wf-node .port-in{top:-6px}
  .wf-node .port-out{bottom:-6px}
  .wf-node .delete-node{position:absolute;top:-8px;right:-8px;width:18px;height:18px;border-radius:50%;background:#f85149;color:#fff;border:none;font-size:10px;cursor:pointer;display:none;z-index:5;line-height:18px;text-align:center}
  .wf-node.selected .delete-node{display:block}
  .wf-node .status-icon{position:absolute;top:-8px;left:-8px;width:18px;height:18px;border-radius:50%;font-size:10px;line-height:18px;text-align:center;display:none;z-index:5}
  .wf-node.executing .status-icon{display:block;background:#58a6ff;color:#fff;animation:pulse 1s infinite}
  .wf-node.done .status-icon{display:block;background:#3fb950;color:#fff}
  .wf-node.error .status-icon{display:block;background:#f85149;color:#fff}
  
  /* Execution overlay */
  #exec-overlay{display:none;position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:50;justify-content:center;align-items:flex-start;padding-top:60px}
  #exec-panel{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;width:600px;max-height:70vh;overflow-y:auto}
  #exec-panel h3{margin-bottom:12px;font-size:14px}
  #exec-panel .step{padding:8px 12px;margin:4px 0;border-radius:4px;font-size:12px;display:flex;align-items:center;gap:8px}
  #exec-panel .step.ok{background:#3fb95011;border-left:3px solid #3fb950}
  #exec-panel .step.error{background:#f8514911;border-left:3px solid #f85149}
  #exec-panel .step.pending{background:#21262d;border-left:3px solid #30363d}
  #exec-panel .step .time{color:#8b949e;font-size:11px;margin-left:auto}
  #exec-panel .step .preview{color:#8b949e;font-size:11px;margin-top:4px;max-height:60px;overflow:hidden}
  #exec-panel .final-output{background:#0d1117;border:1px solid #30363d;border-radius:4px;padding:12px;margin-top:12px;font-size:12px;white-space:pre-wrap;max-height:200px;overflow-y:auto}
  #exec-panel .close-exec{float:right;background:transparent;color:#8b949e;border:none;cursor:pointer;font-size:16px}
  #exec-panel .close-exec:hover{color:#e6edf3}
  
  /* Config modal */
  #config-overlay{display:none;position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:100;justify-content:center;align-items:center}
  #config-modal{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;width:440px;max-height:80vh;overflow-y:auto}
  #config-modal h3{margin-bottom:12px;font-size:14px}
  #config-modal label{display:block;font-size:12px;color:#8b949e;margin:8px 0 4px}
  #config-modal input,#config-modal textarea,#config-modal select{width:100%;background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:6px 10px;border-radius:4px;font-size:12px;outline:none}
  #config-modal textarea{min-height:60px;resize:vertical;font-family:inherit}
  #config-modal input:focus,#config-modal textarea:focus{border-color:#1f6feb}
  #config-modal .btn-row{display:flex;gap:8px;margin-top:12px;justify-content:flex-end}
  #config-modal .btn-row button{padding:6px 16px;border-radius:4px;font-size:12px;cursor:pointer;border:none}
  #config-modal .btn-row .save{background:#238636;color:#fff}
  #config-modal .btn-row .save:hover{background:#2ea043}
  #config-modal .btn-row .cancel{background:#21262d;color:#e6edf3;border:1px solid #30363d}
  #config-modal .btn-row .cancel:hover{background:#30363d}
  
  .hint{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);background:#161b22;border:1px solid #30363d;padding:6px 14px;border-radius:6px;font-size:11px;color:#8b949e;z-index:5;pointer-events:none;white-space:nowrap}
  
  ::-webkit-scrollbar{width:6px;height:6px}
  ::-webkit-scrollbar-track{background:transparent}
  ::-webkit-scrollbar-thumb{background:#30363d;border-radius:3px}
  ::-webkit-scrollbar-thumb:hover{background:#484f58}
</style>
</head>
<body>
<header>
  <h1>\u2699\uFE0F Workflow Builder</h1>
  <a href="/">Chat</a>
  <input class="wf-name" id="wf-name" placeholder="Workflow name..." value="Untitled Workflow"/>
  <div class="toolbar">
    <button onclick="loadWorkflowDialog()">Load</button>
    <button onclick="saveWorkflow()">Save</button>
    <button onclick="exportWorkflow()">Export</button>
    <button class="primary" onclick="executeWorkflow()">Run</button>
    <button class="danger" onclick="clearCanvas()">Clear</button>
  </div>
</header>
<div id="main">
  <div id="palette">
    <h3>AI Providers</h3>
    <div id="palette-list"></div>
  </div>
  <div id="canvas-wrap" oncontextmenu="return false">
    <div id="canvas"></div>
    <svg id="svg-layer"></svg>
    <div class="hint">Drag providers to canvas &bull; Connect output \u25BC to input \u25B2 &bull; Click node to configure</div>
  </div>
</div>

<div id="config-overlay"><div id="config-modal"></div></div>
<div id="exec-overlay"><div id="exec-panel"></div></div>

<script>
// State
let nodes = [];
let edges = [];
let selectedId = null;
let nextNodeId = 1;
let nodeCounter = 0;
let connecting = null;
let dragNode = null;
let dragOffX = 0, dragOffY = 0;
let providers = [];
let providerRoles = {};
let configNodeId = null;
let currentWorkflowId = null;

// Load providers
async function loadProviders() {
  const r = await fetch('/api/provider-roles');
  const data = await r.json();
  providers = data.providers || [];
  providerRoles = data.roles || {};
  renderPalette();
}
loadProviders();

function renderPalette() {
  const list = document.getElementById('palette-list');
  list.innerHTML = providers.map(p => {
    const role = providerRoles[p.id] || {role:'Assistant', emoji:'\U0001F916'};
    const configured = p.configured;
    return '<div class="palette-item" data-provider="'+p.id+'" draggable="true">' +
      '<span class="emoji">'+role.emoji+'</span>' +
      '<div class="info"><div class="name">'+role.role+'</div><div class="role">'+p.id+'</div></div>' +
      '<span class="status" style="background:'+(configured?'#3fb950':'#f85149')+'"></span>' +
    '</div>';
  }).join('');
  
  document.querySelectorAll('.palette-item').forEach(el => {
    el.addEventListener('dragstart', onPaletteDragStart);
  });
}

function onPaletteDragStart(e) {
  e.dataTransfer.setData('text/plain', e.target.closest('.palette-item').dataset.provider);
  e.dataTransfer.effectAllowed = 'copy';
}

// Canvas
const canvas = document.getElementById('canvas');
const svgLayer = document.getElementById('svg-layer');
const canvasWrap = document.getElementById('canvas-wrap');

canvasWrap.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
canvasWrap.addEventListener('drop', onCanvasDrop);
canvasWrap.addEventListener('mousedown', onCanvasMouseDown);
canvasWrap.addEventListener('mousemove', onCanvasMouseMove);
canvasWrap.addEventListener('mouseup', onCanvasMouseUp);
canvasWrap.addEventListener('click', onCanvasClick);

function onCanvasDrop(e) {
  e.preventDefault();
  const pid = e.dataTransfer.getData('text/plain');
  if (!pid) return;
  const rect = canvasWrap.getBoundingClientRect();
  const x = e.clientX - rect.left - 90;
  const y = e.clientY - rect.top - 30;
  addNode(pid, Math.max(0, x), Math.max(0, y));
}

function addNode(providerId, x, y) {
  const role = providerRoles[providerId] || {role:'Assistant', emoji:'\U0001F916', color:'#6b7280', desc:'', system_prompt:'You are a helpful assistant.'};
  const id = 'n' + (++nodeCounter);
  const label = role.role + ' ' + nodeCounter;
  nodes.push({
    id, provider: providerId, label,
    x, y, system_prompt: role.system_prompt, temperature: 0.7
  });
  renderNodes();
  renderEdges();
  return id;
}

function renderNodes() {
  // Remove DOM nodes not in state
  document.querySelectorAll('.wf-node').forEach(el => {
    if (!nodes.find(n => n.id === el.dataset.id)) el.remove();
  });
  
  nodes.forEach(n => {
    let el = document.querySelector('.wf-node[data-id="'+n.id+'"]');
    const role = providerRoles[n.provider] || {emoji:'\U0001F916', color:'#6b7280'};
    if (!el) {
      el = document.createElement('div');
      el.className = 'wf-node';
      el.dataset.id = n.id;
      el.innerHTML =
        '<div class="header" style="background:'+role.color+'22;color:'+role.color+'">' +
          '<span>'+role.emoji+'</span><span>'+n.label+'</span>' +
        '</div>' +
        '<div class="body">' +
          '<div class="provider-name">'+n.provider+'</div>' +
          '<div style="margin-top:2px">'+ (role.role) +'</div>' +
        '</div>' +
        '<div class="port port-in"></div>' +
        '<div class="port port-out"></div>' +
        '<button class="delete-node" onclick="deleteNode(\''+n.id+'\')">\u2715</button>' +
        '<div class="status-icon"></div>';
      el.addEventListener('mousedown', onNodeMouseDown);
      el.addEventListener('dblclick', () => openConfig(n.id));
      canvas.appendChild(el);
    }
    el.style.left = n.x + 'px';
    el.style.top = n.y + 'px';
    if (selectedId === n.id) el.classList.add('selected');
    else el.classList.remove('selected');
    
    // Port event handlers
    el.querySelector('.port-out').onmousedown = (e) => { e.stopPropagation(); startConnection(n.id, e); };
    el.querySelector('.port-in').onmouseup = (e) => { e.stopPropagation(); endConnection(n.id); };
  });
}

function renderEdges() {
  while (svgLayer.firstChild) svgLayer.removeChild(svgLayer.firstChild);
  
  const wrapRect = canvasWrap.getBoundingClientRect();
  
  edges.forEach(e => {
    const src = document.querySelector('.wf-node[data-id="'+e.source+'"]');
    const tgt = document.querySelector('.wf-node[data-id="'+e.target+'"]');
    if (!src || !tgt) return;
    
    const srcOut = src.querySelector('.port-out');
    const tgtIn = tgt.querySelector('.port-in');
    if (!srcOut || !tgtIn) return;
    
    const srcRect = srcOut.getBoundingClientRect();
    const tgtRect = tgtIn.getBoundingClientRect();
    
    const x1 = srcRect.left + srcRect.width/2 - wrapRect.left;
    const y1 = srcRect.top + srcRect.height/2 - wrapRect.top;
    const x2 = tgtRect.left + tgtRect.width/2 - wrapRect.left;
    const y2 = tgtRect.top + tgtRect.height/2 - wrapRect.top;
    
    const midY = (y1 + y2) / 2;
    const d = 'M '+x1+' '+y1+' C '+x1+' '+midY+', '+x2+' '+midY+', '+x2+' '+y2;
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d);
    path.setAttribute('stroke', '#58a6ff');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    path.setAttribute('data-edge', e.id);
    path.style.pointerEvents = 'stroke';
    path.style.cursor = 'pointer';
    path.title = e.id;
    path.onclick = () => deleteEdge(e.id);
    svgLayer.appendChild(path);
  });
  
  if (connecting) {
    const src = document.querySelector('.wf-node[data-id="'+connecting.source+'"]');
    if (src) {
      const port = src.querySelector('.port-out');
      if (port) {
        const pr = port.getBoundingClientRect();
        const wr = canvasWrap.getBoundingClientRect();
        const x1 = pr.left + pr.width/2 - wr.left;
        const y1 = pr.top + pr.height/2 - wr.top;
        const x2 = connecting.mx - wr.left;
        const y2 = connecting.my - wr.top;
        const midY = (y1 + y2) / 2;
        const d = 'M '+x1+' '+y1+' C '+x1+' '+midY+', '+x2+' '+midY+', '+x2+' '+y2;
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('stroke', '#58a6ff66');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('stroke-dasharray', '5,5');
        path.setAttribute('fill', 'none');
        path.id = 'temp-conn';
        svgLayer.appendChild(path);
      }
    }
  }
}

// Node dragging
function onNodeMouseDown(e) {
  if (e.button !== 0) return;
  if (e.target.classList.contains('port') || e.target.classList.contains('delete-node')) return;
  const nodeEl = e.target.closest('.wf-node');
  if (!nodeEl) return;
  const id = nodeEl.dataset.id;
  selectNode(id);
  dragNode = id;
  const rect = nodeEl.getBoundingClientRect();
  dragOffX = e.clientX - rect.left;
  dragOffY = e.clientY - rect.top;
  e.preventDefault();
}

function onCanvasMouseMove(e) {
  if (connecting) {
    connecting.mx = e.clientX;
    connecting.my = e.clientY;
    renderEdges();
    return;
  }
  if (!dragNode) return;
  const node = nodes.find(n => n.id === dragNode);
  if (!node) return;
  const wrapRect = canvasWrap.getBoundingClientRect();
  node.x = e.clientX - wrapRect.left - dragOffX;
  node.y = e.clientY - wrapRect.top - dragOffY;
  renderNodes();
  renderEdges();
}

function onCanvasMouseUp(e) {
  if (connecting) {
    const target = document.elementFromPoint(e.clientX, e.clientY);
    if (target && target.classList.contains('port-in')) {
      const nodeEl = target.closest('.wf-node');
      if (nodeEl && nodeEl.dataset.id !== connecting.source) {
        addEdge(connecting.source, nodeEl.dataset.id);
      }
    }
    connecting = null;
    renderEdges();
  }
  dragNode = null;
}

function onCanvasClick(e) {
  if (e.target === canvasWrap || e.target === canvas || e.target.id === 'svg-layer') {
    selectedId = null;
    document.querySelectorAll('.wf-node').forEach(el => el.classList.remove('selected'));
  }
}

// Connections
function startConnection(sourceId, e) {
  connecting = { source: sourceId, mx: e.clientX, my: e.clientY };
  e.preventDefault();
}

function endConnection(targetId) {
  if (connecting && connecting.source !== targetId) {
    addEdge(connecting.source, targetId);
  }
  connecting = null;
  renderEdges();
}

function addEdge(source, target) {
  if (source === target) return;
  if (edges.find(e => e.source === source && e.target === target)) return;
  if (edges.find(e => e.target === source)) return; // single input
  const id = 'e' + (edges.length + 1);
  edges.push({ id, source, target });
  renderEdges();
}

function deleteEdge(id) {
  edges = edges.filter(e => e.id !== id);
  renderEdges();
}

function deleteNode(id) {
  nodes = nodes.filter(n => n.id !== id);
  edges = edges.filter(e => e.source !== id && e.target !== id);
  if (selectedId === id) selectedId = null;
  renderNodes();
  renderEdges();
}

function selectNode(id) {
  selectedId = id;
  document.querySelectorAll('.wf-node').forEach(el => el.classList.remove('selected'));
  const el = document.querySelector('.wf-node[data-id="'+id+'"]');
  if (el) el.classList.add('selected');
}

// Config
function openConfig(id) {
  const node = nodes.find(n => n.id === id);
  if (!node) return;
  configNodeId = id;
  const role = providerRoles[node.provider] || {};
  const providerInfo = providers.find(p => p.id === node.provider) || {};
  
  const modal = document.getElementById('config-modal');
  modal.innerHTML =
    '<h3>Configure <span style="color:'+(role.color||'#58a6ff')+'">'+node.label+'</span></h3>' +
    '<label>Provider</label><input value="'+node.provider+'" disabled style="opacity:0.6"/>' +
    '<label>Label</label><input id="cfg-label" value="'+node.label+'"/>' +
    '<label>System Prompt</label><textarea id="cfg-prompt" rows="4">'+(node.system_prompt || role.system_prompt || '')+'</textarea>' +
    '<label>Temperature (0-2)</label><input id="cfg-temp" type="number" min="0" max="2" step="0.1" value="'+(node.temperature||0.7)+'"/>' +
    '<div class="btn-row">' +
      '<button class="save" onclick="saveConfig()">Save</button>' +
      '<button class="cancel" onclick="closeConfig()">Cancel</button>' +
    '</div>';
  document.getElementById('config-overlay').style.display = 'flex';
}

function saveConfig() {
  const node = nodes.find(n => n.id === configNodeId);
  if (!node) return;
  node.label = document.getElementById('cfg-label').value || node.label;
  node.system_prompt = document.getElementById('cfg-prompt').value || '';
  const t = parseFloat(document.getElementById('cfg-temp').value);
  node.temperature = isNaN(t) ? 0.7 : Math.max(0, Math.min(2, t));
  closeConfig();
  renderNodes();
}

function closeConfig() {
  document.getElementById('config-overlay').style.display = 'none';
  configNodeId = null;
}

// Workflow CRUD
async function saveWorkflow() {
  const name = document.getElementById('wf-name').value || 'Untitled Workflow';
  const wf = { name, nodes, edges };
  if (currentWorkflowId) wf.id = currentWorkflowId;
  
  const r = await fetch('/api/workflows' + (currentWorkflowId ? '/' + currentWorkflowId : ''), {
    method: currentWorkflowId ? 'PUT' : 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(wf)
  });
  const data = await r.json();
  if (data.id) {
    currentWorkflowId = data.id;
    document.getElementById('wf-name').value = data.name || name;
    showToast('Saved: ' + (data.name || name));
  } else {
    showToast('Save failed: ' + (data.error || 'unknown error'));
  }
}

async function loadWorkflowDialog() {
  const r = await fetch('/api/workflows');
  const list = await r.json();
  if (!list.length) { showToast('No saved workflows'); return; }
  
  const modal = document.getElementById('config-modal');
  modal.innerHTML =
    '<h3>Load Workflow</h3>' +
    '<div style="max-height:300px;overflow-y:auto">' +
    list.map(w => '<div class="palette-item" style="cursor:pointer" onclick="loadWorkflow(\''+w.id+'\')">' +
      '<span style="color:#58a6ff">\U0001F4C4</span>' +
      '<div class="info"><div class="name">'+(w.name||'Unnamed')+'</div><div class="role">'+w.node_count+' nodes</div></div>' +
    '</div>').join('') +
    '</div>' +
    '<div class="btn-row"><button class="cancel" onclick="closeConfig()">Cancel</button></div>';
  document.getElementById('config-overlay').style.display = 'flex';
}

async function loadWorkflow(id) {
  closeConfig();
  const r = await fetch('/api/workflows/' + id);
  const wf = await r.json();
  if (wf.error) { showToast('Load failed: ' + wf.error); return; }
  
  nodes = (wf.nodes || []).map(n => ({...n}));
  edges = (wf.edges || []).map(e => ({...e}));
  currentWorkflowId = wf.id;
  document.getElementById('wf-name').value = wf.name || 'Untitled';
  nodeCounter = nodes.length;
  selectedId = null;
  renderNodes();
  renderEdges();
  showToast('Loaded: ' + (wf.name || 'Untitled'));
}

function exportWorkflow() {
  const wf = { name: document.getElementById('wf-name').value, nodes, edges };
  const text = JSON.stringify(wf, null, 2);
  const blob = new Blob([text], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (wf.name || 'workflow').replace(/\\s+/g,'_') + '.json';
  a.click();
  URL.revokeObjectURL(a.href);
  showToast('Exported');
}

async function executeWorkflow() {
  if (!nodes.length) { showToast('Add at least one node'); return; }
  
  // Show exec overlay
  const overlay = document.getElementById('exec-overlay');
  const panel = document.getElementById('exec-panel');
  panel.innerHTML = '<h3>Executing Workflow <span class="close-exec" onclick="closeExec()">\u2715</span></h3><div id="exec-steps"></div>';
  overlay.style.display = 'flex';
  
  // Run
  const name = document.getElementById('wf-name').value;
  const wf = { name, nodes, edges };
  
  try {
    const r = await fetch('/api/workflows/execute', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(wf)
    });
    const result = await r.json();
    
    if (result.error) {
      document.getElementById('exec-steps').innerHTML = '<div class="step error">Error: '+result.error+'</div>';
      return;
    }
    
    let html = '<div style="margin-bottom:8px;font-size:12px;color:#8b949e">' +
      'Nodes: '+(result.success_count||0)+'/'+result.total_nodes+' ok &bull; Time: '+(result.total_time||'0')+'s' +
    '</div>';
    
    (result.steps || []).forEach(s => {
      const icon = s.status === 'ok' ? '\u2713' : s.status === 'error' ? '\u2717' : '\u23F3';
      html += '<div class="step '+s.status+'">' +
        '<span>'+icon+'</span>' +
        '<span>'+(s.node_name||s.node_id)+'</span>' +
        (s.elapsed ? '<span class="time">'+s.elapsed+'s</span>' : '') +
        (s.preview ? '<div class="preview">'+s.preview+'...</div>' : '') +
        (s.error ? '<div class="preview" style="color:#f85149">'+s.error+'</div>' : '') +
      '</div>';
    });
    
    if (result.final_output) {
      html += '<h4 style="font-size:12px;margin:12px 0 4px;color:#8b949e">Final Output</h4>' +
        '<div class="final-output">'+result.final_output+'</div>';
    }
    
    document.getElementById('exec-steps').innerHTML = html;
    
    // Highlight nodes
    (result.steps || []).forEach(s => {
      const el = document.querySelector('.wf-node[data-id="'+s.node_id+'"]');
      if (el) {
        el.classList.remove('executing');
        el.classList.add(s.status === 'ok' ? 'done' : 'error');
      }
    });
    
  } catch(e) {
    document.getElementById('exec-steps').innerHTML = '<div class="step error">Error: '+e.message+'</div>';
  }
}

function closeExec() {
  document.getElementById('exec-overlay').style.display = 'none';
  document.querySelectorAll('.wf-node').forEach(el => {
    el.classList.remove('executing', 'done', 'error');
  });
}

function clearCanvas() {
  if (nodes.length && !confirm('Clear all nodes?')) return;
  nodes = [];
  edges = [];
  selectedId = null;
  currentWorkflowId = null;
  nodeCounter = 0;
  document.getElementById('wf-name').value = 'Untitled Workflow';
  renderNodes();
  renderEdges();
}

// Toast
function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#161b22;border:1px solid #30363d;padding:8px 20px;border-radius:6px;font-size:12px;z-index:200;transition:opacity .3s;opacity:0';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._hide);
  t._hide = setTimeout(() => t.style.opacity = '0', 2500);
}

// Keyboard
document.addEventListener('keydown', e => {
  if (e.key === 'Delete' || e.key === 'Backspace') {
    if (document.querySelector('#config-overlay[style*="flex"]')) return;
    if (selectedId) {
      deleteNode(selectedId);
      e.preventDefault();
    }
  }
  if (e.key === 'Escape') {
    closeConfig();
    closeExec();
    connecting = null;
    renderEdges();
  }
});

// Re-render edges on scroll/resize
window.addEventListener('resize', () => renderEdges());

// Initial render
renderNodes();
renderEdges();

</script>
</body>
</html>"""

@app.get("/")
async def web_ui():
    models = get_available_models()
    configured = [m for m in models if m["configured"]]
    unconfigured = [m for m in models if not m["configured"]]
    opts = "".join("".join(('<option value="', m["id"], '">', m["provider"], " \u2014 ", m["model"], "</option>")) for m in configured)
    uopts = "".join("".join(('<option value="', m["id"], '" disabled>', m["provider"], " \u2014 ", m["model"], " (not configured)</option>")) for m in unconfigured)
    html = _WEB_HTML_TEMPLATE.replace("__READY_COUNT__", str(len(configured)))
    html = html.replace("__MODEL_COUNT__", str(len(models)))
    html = html.replace("__MODEL_OPTIONS__", opts)
    html = html.replace("__UNCONFIGURED_OPTIONS__", uopts)
    return HTMLResponse(html)

@app.get("/workflow")
async def workflow_builder():
    return HTMLResponse(_WORKFLOW_HTML_TEMPLATE)

@app.get("/api/provider-roles")
async def list_provider_roles():
    available = get_available_providers()
    return JSONResponse({"providers": available, "roles": PROVIDER_ROLES})

@app.get("/api/workflows")
async def list_workflows():
    return JSONResponse([{"id": k, "name": v.get("name", "Unnamed"), "node_count": len(v.get("nodes", [])), "edge_count": len(v.get("edges", []))} for k, v in WORKFLOWS.items()])

@app.post("/api/workflows")
async def create_workflow(req: Request):
    global _next_wf_id
    body = await req.json()
    wf_id = str(_next_wf_id)
    _next_wf_id += 1
    WORKFLOWS[wf_id] = {
        "id": wf_id,
        "name": body.get("name", "Untitled Workflow"),
        "nodes": body.get("nodes", []),
        "edges": body.get("edges", []),
        "created": time.time(),
    }
    _save_workflows()
    return JSONResponse({"id": wf_id, "name": WORKFLOWS[wf_id]["name"]})

@app.get("/api/workflows/{wf_id}")
async def get_workflow(wf_id: str):
    wf = WORKFLOWS.get(wf_id)
    if not wf:
        return JSONResponse({"error": "Workflow not found"}, status_code=404)
    return JSONResponse(wf)

@app.put("/api/workflows/{wf_id}")
async def update_workflow(wf_id: str, req: Request):
    wf = WORKFLOWS.get(wf_id)
    if not wf:
        return JSONResponse({"error": "Workflow not found"}, status_code=404)
    body = await req.json()
    wf["name"] = body.get("name", wf["name"])
    wf["nodes"] = body.get("nodes", wf["nodes"])
    wf["edges"] = body.get("edges", wf["edges"])
    wf["updated"] = time.time()
    _save_workflows()
    return JSONResponse({"id": wf_id, "name": wf["name"]})

@app.delete("/api/workflows/{wf_id}")
async def delete_workflow(wf_id: str):
    if wf_id in WORKFLOWS:
        del WORKFLOWS[wf_id]
        _save_workflows()
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Workflow not found"}, status_code=404)

@app.post("/api/workflows/execute")
async def run_workflow(req: Request):
    body = await req.json()
    result = await execute_workflow(body)
    return JSONResponse(result)

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
