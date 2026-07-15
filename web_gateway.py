import asyncio, json, os, time, threading, urllib.parse, uuid, re, traceback, subprocess, sys, inspect

HAS_HTTPX = True
try:
    import httpx
except ImportError:
    HAS_HTTPX = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_FILE = os.path.join(BASE_DIR, "providers.json")
SYNOXCLOUD_AI_MODELS_FILE = os.path.join(BASE_DIR, "synoxcloud_ai_models.json")
WORKFLOWS_FILE = os.path.join(BASE_DIR, "workflows.json")

PROVIDERS = {}
SYNOXCLOUD_AI_MODELS = {}
_http = None

PROVIDER_ROLES = {
    "zenmux": {"role": "Strategist", "emoji": "\u265F\uFE0F", "color": "#8b5cf6",
               "desc": "Strategic multi-step reasoning with Grok 4.5 Free",
               "system_prompt": "You are a strategist. Think several steps ahead, consider multiple perspectives, and provide strategic recommendations."},
    "groq": {"role": "Researcher", "emoji": "\U0001F52C", "color": "#10b981",
             "desc": "Fast research and information synthesis",
             "system_prompt": "You are a research assistant. Gather, synthesize, and present information clearly."},
    "gemini": {"role": "Analyst", "emoji": "\U0001F4CA", "color": "#3b82f6",
               "desc": "Multimodal analysis and pattern recognition",
               "system_prompt": "You are an analyst. Examine data critically and provide insightful analysis."},
    "deepseek": {"role": "Coder", "emoji": "\U0001F4BB", "color": "#06b6d4",
                 "desc": "Code generation and software architecture",
                 "system_prompt": "You are a senior software engineer. Write clean, efficient, well-documented code."},
    "mistral": {"role": "Writer", "emoji": "\u270D\uFE0F", "color": "#f59e0b",
                "desc": "Creative and technical writing",
                "system_prompt": "You are a professional writer. Produce clear, engaging content."},
    "nvidia": {"role": "Scientist", "emoji": "\U0001F52A", "color": "#76b900",
               "desc": "Technical and scientific reasoning",
               "system_prompt": "You are a scientist. Apply rigorous reasoning and explain precisely."},
    "openrouter": {"role": "Generalist", "emoji": "\U0001F9E0", "color": "#a855f7",
                   "desc": "Versatile general-purpose AI",
                   "system_prompt": "You are a helpful general assistant. Answer thoroughly and accurately."},
    "cohere": {"role": "Summarizer", "emoji": "\U0001F4DD", "color": "#ec4899",
               "desc": "Document analysis and summarization",
               "system_prompt": "You are a summarization specialist. Condense while preserving key points."},
    "xai": {"role": "Explainer", "emoji": "\U0001F50D", "color": "#ef4444",
            "desc": "Clear explanations of complex topics",
            "system_prompt": "You are an explainer. Break down complex topics into clear explanations."},
    "github": {"role": "Developer", "emoji": "\U0001F6E0\uFE0F", "color": "#2da44e",
               "desc": "Code review and software development",
               "system_prompt": "You are a developer. Build and review code following best practices."},
    "together": {"role": "Creator", "emoji": "\U0001F3A8", "color": "#8b5cf6",
                 "desc": "Creative content generation",
                 "system_prompt": "You are a creative AI. Generate imaginative, original content."},
    "fireworks": {"role": "Optimizer", "emoji": "\u26A1", "color": "#f97316",
                  "desc": "Performance optimization and refinement",
                  "system_prompt": "You are an optimizer. Improve and refine content for impact."},
    "cerebras": {"role": "Speedster", "emoji": "\U0001F3CE\uFE0F", "color": "#14b8a6",
                 "desc": "Ultra-fast responses for simple tasks",
                 "system_prompt": "You are a rapid-response AI. Provide quick, accurate answers."},
    "sambanova": {"role": "Reasoner", "emoji": "\U0001F9EE", "color": "#6366f1",
                  "desc": "Deep logical reasoning",
                  "system_prompt": "You are a reasoning engine. Think step-by-step and show your work."},
    "lepton": {"role": "Advisor", "emoji": "\U0001F4A1", "color": "#eab308",
               "desc": "Strategic advice and consulting",
               "system_prompt": "You are an advisor. Provide strategic guidance and recommendations."},
    "synoxcloud": {"role": "Assistant", "emoji": "\U0001F916", "color": "#6b7280",
                   "desc": "General-purpose AI assistant via SynoxCloud",
                   "system_prompt": "You are a helpful assistant. Be concise and accurate."},
    "omniroute": {"role": "Router", "emoji": "\U0001F9F0", "color": "#f59e0b",
                  "desc": "Smart router: 250+ providers, 90+ free, auto-fallback, token compression",
                  "system_prompt": "You are a smart routing AI. Route requests intelligently across the best available provider for each task."},
    "hy3": {"role": "Thinker", "emoji": "\U0001F4AD", "color": "#d946ef",
            "desc": "Deep thinking with Hy3 model",
            "system_prompt": "You are a deep thinker. Explore ideas thoroughly."},
    "hy3-preview": {"role": "Pioneer", "emoji": "\U0001F680", "color": "#f43f5e",
                    "desc": "Cutting-edge Hy3 preview model",
                    "system_prompt": "You are a pioneer. Push boundaries in your analysis."},
}

# ---- MCP Server (Model Context Protocol) ----

MCP_TOOLS = [
    {"name": "call_llm", "description": "Call any configured LLM provider with messages",
     "input_schema": {"type": "object", "properties": {
         "provider": {"type": "string", "description": "Provider ID (e.g. groq, gemini, omniroute)"},
         "messages": {"type": "array", "description": "Messages array with role and content"},
         "system_prompt": {"type": "string", "description": "Optional system prompt"}},
         "required": ["provider", "messages"]}},
    {"name": "execute_workflow", "description": "Execute a workflow by its node/edge graph",
     "input_schema": {"type": "object", "properties": {
         "nodes": {"type": "array"}, "edges": {"type": "array"},
         "input": {"type": "string", "description": "Initial input text"}},
         "required": ["nodes", "edges"]}},
    {"name": "list_providers", "description": "List all configured AI providers",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "list_models", "description": "List all available AI models",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "bot_status", "description": "Get Telegram bot status (running/stopped)",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "bot_toggle", "description": "Start or stop the Telegram bot",
     "input_schema": {"type": "object", "properties": {
         "action": {"type": "string", "enum": ["start", "stop"]}},
         "required": ["action"]}},
    {"name": "list_workflows", "description": "List all saved workflows",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_workflow", "description": "Get a specific workflow by ID",
     "input_schema": {"type": "object", "properties": {
         "workflow_id": {"type": "string"}},
         "required": ["workflow_id"]}},
]

async def _mcp_call_tool(name, arguments):
    if name == "call_llm":
        provider = arguments.get("provider", "groq")
        messages = arguments.get("messages", [])
        sys_prompt = arguments.get("system_prompt")
        if sys_prompt:
            messages = [{"role": "system", "content": sys_prompt}] + messages
        result = await call_provider(messages, provider)
        if "error" in result:
            return {"content": [{"type": "text", "text": result["error"]}], "isError": True}
        return {"content": [{"type": "text", "text": result.get("content", "")}]}
    elif name == "execute_workflow":
        result = await execute_workflow({"nodes": arguments.get("nodes", []), "edges": arguments.get("edges", [])}, arguments.get("input", ""))
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    elif name == "list_providers":
        return {"content": [{"type": "text", "text": json.dumps(get_available_providers(), indent=2, ensure_ascii=False)}]}
    elif name == "list_models":
        return {"content": [{"type": "text", "text": json.dumps(get_available_models(), indent=2, ensure_ascii=False)}]}
    elif name == "bot_status":
        return {"content": [{"type": "text", "text": json.dumps(bot_status(), indent=2, ensure_ascii=False)}]}
    elif name == "bot_toggle":
        r = bot_start() if arguments.get("action") == "start" else bot_stop()
        return {"content": [{"type": "text", "text": json.dumps({"result": r, "status": bot_status()}, indent=2, ensure_ascii=False)}]}
    elif name == "list_workflows":
        wl = [{"id": k, "name": v.get("name", "Unnamed"), "node_count": len(v.get("nodes", []))} for k, v in WORKFLOWS.items()]
        return {"content": [{"type": "text", "text": json.dumps(wl, indent=2, ensure_ascii=False)}]}
    elif name == "get_workflow":
        wf = WORKFLOWS.get(arguments.get("workflow_id", ""))
        if not wf:
            return {"content": [{"type": "text", "text": "Workflow not found"}], "isError": True}
        return {"content": [{"type": "text", "text": json.dumps(wf, indent=2, ensure_ascii=False)}]}
    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

async def _mcp_handle(body_str):
    try:
        req = json.loads(body_str) if body_str and body_str.strip() else {}
    except:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
    rid = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": MCP_TOOLS}}
    elif method == "tools/call":
        result = await _mcp_call_tool(params.get("name", ""), params.get("arguments", {}))
        return {"jsonrpc": "2.0", "id": rid, "result": result}
    elif method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}, "resources": {}}}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    else:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}}

# ---- CrewAI Workflow Engine (optional) ----

HAS_CREWAI = False
try:
    from crewai import Agent as CrewAgent, Task as CrewTask, Crew as CrewCrew, Process as CrewProcess
    HAS_CREWAI = True
except ImportError:
    pass

async def execute_workflow_crewai(workflow, initial_input=""):
    if not HAS_CREWAI:
        return {"error": "CrewAI not installed. Install with: pip install crewai", "fallback": True}
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
    agents = {}
    tasks = []
    task_map = {}
    for nid in order:
        node = node_map[nid]
        pid = node.get("provider", "openrouter")
        role_info = _get_role(pid)
        agent_role = node.get("label") or role_info.get("role", "Assistant")
        agent = CrewAgent(
            role=agent_role,
            goal=node.get("system_prompt") or role_info.get("system_prompt", "Complete your task effectively."),
            backstory=f"You are an AI {agent_role} powered by {pid}. Complete your assigned task thoroughly.",
            verbose=True
        )
        agents[nid] = agent
        upstream = in_edges.get(nid, [])
        ctx = []
        for uid in upstream:
            if uid in task_map:
                ctx.append(task_map[uid])
        desc = f"Execute your role as {agent_role}. "
        if initial_input and not upstream:
            desc += f"Initial input: {initial_input}\n"
        if ctx:
            desc += f"Context from upstream tasks: {', '.join(str(c) for c in ctx)}\n"
        task = CrewTask(description=desc, expected_output="Detailed response based on your role and context", agent=agent)
        tasks.append(task)
        task_map[nid] = task
    crew = CrewCrew(agents=list(agents.values()), tasks=tasks, process=CrewProcess.sequential, verbose=True)
    try:
        result = crew.kickoff()
        return {"success": True, "result": str(result), "engine": "crewai", "total_nodes": len(nodes)}
    except Exception as e:
        return {"error": str(e), "engine": "crewai"}

def _is_configured(key):
    return bool(key) and "YOUR_" not in key and key != "not configured"

def _load_providers():
    global PROVIDERS, SYNOXCLOUD_AI_MODELS
    PROVIDERS = {
        "omniroute": {"url": os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions"), "model": os.environ.get("OMNIROUTE_MODEL", "auto"), "key": os.environ.get("OMNIROUTE_KEY", "not configured")},
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
        "synoxcloud": {"url": "https://api.synoxcloud.xyz/api/ai-chat", "model": "claude-haiku-4.5", "key": "free"},
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
        models.append({"id": pid, "model": p["model"], "provider": pid, "configured": _is_configured(p.get("key", ""))})
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
    return PROVIDER_ROLES.get(provider_id, PROVIDER_ROLES.get("openrouter", {}))

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
            param_names = [pp.split("=")[0].strip() for pp in raw_params if isinstance(pp, str) and pp.strip()]
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
                try:
                    if isinstance(data, dict):
                        # try inner data wrapper first
                        inner = data.get("data")
                        if isinstance(inner, dict):
                            data = inner
                        # find first non-empty string value from known keys
                        for k in ("answer", "result", "response", "message", "text", "content", "reply", "output"):
                            v = data.get(k)
                            if isinstance(v, str) and v:
                                return {"content": v}
                        # check for error
                        err = data.get("error")
                        if isinstance(err, str) and err:
                            return {"content": "Error: " + err[:500]}
                        # fallback: return the full dict
                        return {"content": str(data)[:2000]}
                except Exception as e:
                    return {"content": "Parse error: " + str(e)[:200]}
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
            try: err_detail = r.json().get("error", {}).get("message", r.text[:300])
            except: err_detail = r.text[:300]
            return {"error": str(r.status_code) + ": " + err_detail}
        except Exception as e:
            return {"error": str(e)}

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
            result = await call_provider(messages, pid)
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
        "steps": steps, "results": results, "errors": errors,
        "final_output": final_output, "total_nodes": len(nodes),
        "success_count": sum(1 for s in steps if s["status"] == "ok"),
        "error_count": sum(1 for s in steps if s["status"] == "error"),
        "total_time": round(sum(s.get("elapsed", 0) for s in steps), 2),
    }

# ---- Bot Subprocess Manager ----

_bot_proc = None
_bot_start_time = 0
_bot_logs = []
_bot_log_lock = threading.Lock()

def _bot_reader(pipe, name):
    global _bot_logs
    for line in iter(pipe.readline, ""):
        if not line:
            break
        with _bot_log_lock:
            _bot_logs.append(f"[{name}] {line.strip()}")
            if len(_bot_logs) > 500:
                _bot_logs = _bot_logs[-300:]

def bot_start():
    global _bot_proc, _bot_start_time
    if _bot_proc and _bot_proc.poll() is None:
        return "already running"
    bot_script = os.path.join(BASE_DIR, "opencode_bot.py")
    if not os.path.exists(bot_script):
        return "opencode_bot.py not found"
    _bot_proc = subprocess.Popen(
        [sys.executable, bot_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=BASE_DIR, env={**os.environ, "WEB_GATEWAY_PORT": os.environ.get("WEB_GATEWAY_PORT", "4357")}
    )
    _bot_start_time = time.time()
    threading.Thread(target=_bot_reader, args=(_bot_proc.stdout, "BOT"), daemon=True).start()
    threading.Thread(target=_bot_reader, args=(_bot_proc.stderr, "ERR"), daemon=True).start()
    return "started"

def bot_stop():
    global _bot_proc
    if not _bot_proc or _bot_proc.poll() is not None:
        return "not running"
    _bot_proc.terminate()
    try:
        _bot_proc.wait(timeout=5)
    except:
        _bot_proc.kill()
        _bot_proc.wait()
    _bot_proc = None
    return "stopped"

def bot_status():
    global _bot_proc, _bot_start_time
    running = _bot_proc is not None and _bot_proc.poll() is None
    return {"running": running, "pid": _bot_proc.pid if running else 0, "uptime": round(time.time() - _bot_start_time, 1) if running else 0}

def bot_logs(count=50):
    with _bot_log_lock:
        return _bot_logs[-count:]

# ---- Minimal HTTP Server (zero C extensions needed) ----

def _parse_path(path):
    path = path.split("?")[0].rstrip("/")
    return path if path else "/"

def _match_route(route_path, request_path):
    stripped = route_path.strip("/")
    route_parts = stripped.split("/") if stripped else []
    stripped2 = request_path.strip("/")
    req_parts = stripped2.split("/") if stripped2 else []
    params = {}
    if len(route_parts) != len(req_parts):
        return None
    for rp, rqp in zip(route_parts, req_parts):
        if rp.startswith("{") and rp.endswith("}"):
            params[rp[1:-1]] = rqp
        elif rp != rqp:
            return None
    return params

_ROUTES = []

def route(method, path):
    def wrapper(f):
        _ROUTES.append((method, path, f))
        return f
    return wrapper

def use_route(method, path):
    for m, p, f in _ROUTES:
        if m == method:
            params = _match_route(p, path)
            if params is not None:
                return f, params
    return None, None

async def _handle(reader, writer):
    try:
        data = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=30)
    except asyncio.IncompleteReadError as e:
        data = e.partial
    except:
        writer.close()
        return
    if not data:
        writer.close()
        return
    try:
        raw = data.decode("utf-8", errors="replace")
    except:
        writer.close()
        return
    lines = raw.split("\r\n")
    if not lines:
        writer.close()
        return
    fl = lines[0].split(" ")
    if len(fl) < 2:
        writer.close()
        return
    method, path = fl[0].upper(), _parse_path(fl[1])
    headers = {}
    i = 1
    while i < len(lines) and lines[i].strip():
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            headers[k.strip().lower()] = v.strip()
        i += 1

    cl = int(headers.get("content-length", 0))
    body_raw = data[data.find(b"\r\n\r\n") + 4:]
    body_str = ""
    if cl > 0:
        have = len(body_raw)
        if have < cl:
            try:
                more = await asyncio.wait_for(reader.readexactly(cl - have), timeout=30)
                body_raw += more
            except:
                pass
        try:
            body_str = body_raw[:cl].decode("utf-8", errors="replace")
        except:
            body_str = ""

    f, params = use_route(method, path)
    if f is None:
        await _send(writer, 404, "text/plain", b"Not Found")
        writer.close()
        return

    if path in ("/mcp/sse",):
        params["_writer"] = writer

    try:
        if inspect.iscoroutinefunction(f):
            result = await f(method, path, headers, body_str, params)
        else:
            result = f(method, path, headers, body_str, params)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error handling {method} {path}: {e}\n{tb}")
        await _send(writer, 500, "application/json", json.dumps({"error": str(e)}).encode())
        writer.close()
        return

    if isinstance(result, tuple) and len(result) == 2 and result[0] == "__sse__":
        return
    if isinstance(result, tuple):
        status, ct, body_bytes, extra_headers = result
        await _send(writer, status, ct, body_bytes, extra_headers)
    else:
        status, ct, body_bytes, extra_headers = 200, "text/plain", b"", {}
        await _send(writer, status, ct, body_bytes, extra_headers)
    writer.close()

async def _send(writer, status, content_type, body, extra_headers=None):
    reason = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found", 500: "Internal Server Error"}.get(status, "OK")
    resp = f"HTTP/1.1 {status} {reason}\r\nContent-Type: {content_type}\r\nContent-Length: {len(body)}\r\n"
    if extra_headers:
        for k, v in extra_headers.items():
            resp += f"{k}: {v}\r\n"
    resp += "\r\n"
    writer.write(resp.encode() + body)
    await writer.drain()

def json_response(data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return (status, "application/json", body, {})

def html_response(html, status=200):
    body = html.encode("utf-8")
    return (status, "text/html; charset=utf-8", body, {})

async def sse_response(writer, generator):
    reason = "OK"
    resp = f"HTTP/1.1 200 {reason}\r\nContent-Type: text/event-stream\r\nCache-Control: no-cache\r\nConnection: keep-alive\r\n\r\n"
    writer.write(resp.encode())
    await writer.drain()
    async for chunk in generator:
        writer.write(chunk.encode())
        await writer.drain()

# ---- HTML Templates ----

_CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OpenCode AI Gateway</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;height:100vh;display:flex;flex-direction:column}
header{background:#161b22;padding:12px 24px;border-bottom:1px solid #30363d;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
h1{font-size:16px;font-weight:600}
nav{display:flex;gap:12px;margin-left:auto}
nav a{color:#58a6ff;text-decoration:none;font-size:13px;padding:4px 10px;border-radius:4px;border:1px solid #30363d}
nav a:hover{background:#1f6feb22}
select{background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:6px 12px;border-radius:6px;font-size:13px}
#chat{flex:1;overflow-y:auto;padding:20px 24px;display:flex;flex-direction:column;gap:16px}
.msg{max-width:720px;padding:12px 16px;border-radius:8px;line-height:1.6;font-size:14px;white-space:pre-wrap}
.user{background:#1f6feb22;border:1px solid #1f6feb44;align-self:flex-end}
.assistant{background:#161b22;border:1px solid #30363d;align-self:flex-start}
.error{background:#da363322;border:1px solid #da363344;color:#f85149;align-self:flex-start}
.loading{background:#161b22;border:1px solid #30363d;color:#8b949e;font-style:italic;align-self:flex-start}
#input-area{background:#161b22;border-top:1px solid #30363d;padding:12px 24px;display:flex;gap:10px}
#input{flex:1;background:#0d1117;color:#e6edf3;border:1px solid #30363d;padding:10px 14px;border-radius:6px;font-size:14px;resize:none;outline:none}
#input:focus{border-color:#1f6feb}
button{background:#238636;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer}
button:hover{background:#2ea043}
button:disabled{background:#23863644;cursor:not-allowed}
.toggle{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:12px;font-size:11px;cursor:pointer;border:1px solid #30363d;background:#161b22;color:#8b949e;user-select:none;transition:all .2s}
.toggle.on{background:#3fb95022;border-color:#3fb950;color:#3fb950}
.toggle.off{background:#f8514922;border-color:#f85149;color:#f85149}
.toggle .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.toggle.on .dot{background:#3fb950}
.toggle.off .dot{background:#f85149}
</style></head><body>
<header><h1>OpenCode AI Gateway</h1><span style="font-size:12px;color:#8b949e" id="status">__STATUS__</span>
<nav><a href="/">Chat</a><a href="/workflow">Workflow Builder</a>
<span class="toggle off" id="bot-toggle" onclick="toggleBot()"><span class="dot"></span> Bot</span>
<select id="model-select">__OPTIONS__</select></nav></header>
<div id="chat"><div class="msg assistant" style="color:#8b949e">Welcome. Select a model and start chatting.</div></div>
<div id="input-area"><textarea id="input" rows="2" placeholder="Type a message..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea><button id="send-btn" onclick="send()">Send</button></div>
<script>
const chat=document.getElementById('chat'),input=document.getElementById('input'),btn=document.getElementById('send-btn'),sel=document.getElementById('model-select');
let h=[];
function add(r,c){const d=document.createElement('div');d.className='msg '+(r==='u'?'user':'a');d.textContent=c;chat.appendChild(d);chat.scrollTop=chat.scrollHeight}
async function send(){const t=input.value.trim();if(!t)return;const m=sel.value;add('u',t);input.value='';btn.disabled=true;
const ld=document.createElement('div');ld.className='msg loading';ld.textContent='Thinking...';chat.appendChild(ld);h.push({role:'user',content:t});
try{const r=await fetch('/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:m,messages:h.slice(-20)})});const j=await r.json();ld.remove();
if(j.choices&&j.choices[0]){const rep=j.choices[0].message.content;add('a',rep);h.push({role:'assistant',content:rep})}else add('error',j.error?.message||'No response')
}catch(e){ld.remove();add('error','Error: '+e.message)}btn.disabled=false}
async function updateBot(){try{const r=await fetch('/api/bot/status');const j=await r.json();const el=document.getElementById('bot-toggle');if(j.running){el.className='toggle on';el.innerHTML='<span class=\"dot\"></span> Bot ON'}else{el.className='toggle off';el.innerHTML='<span class=\"dot\"></span> Bot OFF'}}catch(e){}}
async function toggleBot(){const el=document.getElementById('bot-toggle');const isOn=el.classList.contains('on');el.style.opacity='0.5';try{const r=await fetch(isOn?'/api/bot/stop':'/api/bot/start',{method:'POST'});await r.json();await updateBot()}catch(e){}el.style.opacity='1'}
updateBot();setInterval(updateBot,5000);
</script></body></html>"""

WORKFLOW_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OpenCode Workflow Builder</title>
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
#palette{width:220px;background:#161b22;border-right:1px solid #30363d;overflow-y:auto;flex-shrink:0}
#palette h3{font-size:11px;font-weight:600;text-transform:uppercase;color:#8b949e;padding:10px 12px 6px;letter-spacing:.5px}
.palette-item{padding:6px 12px;cursor:grab;display:flex;align-items:center;gap:8px;border-bottom:1px solid #21262d;transition:background .15s;user-select:none}
.palette-item:hover{background:#1f6feb11}
.palette-item .emoji{font-size:16px;width:24px;text-align:center}
.palette-item .info{flex:1;min-width:0}
.palette-item .name{font-size:12px;font-weight:500}
.palette-item .role{font-size:10px;color:#8b949e}
.palette-item .status{width:6px;height:6px;border-radius:50%;flex-shrink:0}
#canvas-wrap{flex:1;position:relative;overflow:hidden;background:#0d1117;background-image:radial-gradient(circle,#1c2333 1px,transparent 1px);background-size:20px 20px}
#canvas{position:absolute;top:0;left:0;width:100%;height:100%}
#svg-layer{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1}
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
.wf-node.executing .status-icon{display:block;background:#58a6ff;color:#fff}
.wf-node.done .status-icon{display:block;background:#3fb950;color:#fff}
.wf-node.error .status-icon{display:block;background:#f85149;color:#fff}
#exec-overlay{display:none;position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:50;justify-content:center;align-items:flex-start;padding-top:60px}
#exec-panel{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;width:600px;max-height:70vh;overflow-y:auto}
#exec-panel h3{margin-bottom:12px;font-size:14px}
#exec-panel .step{padding:8px 12px;margin:4px 0;border-radius:4px;font-size:12px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
#exec-panel .step.ok{background:#3fb95011;border-left:3px solid #3fb950}
#exec-panel .step.error{background:#f8514911;border-left:3px solid #f85149}
#exec-panel .step.pending{background:#21262d;border-left:3px solid #30363d}
#exec-panel .step .time{color:#8b949e;font-size:11px;margin-left:auto}
#exec-panel .step .preview{color:#8b949e;font-size:11px;margin-top:4px;max-height:60px;overflow:hidden;width:100%}
#exec-panel .final-output{background:#0d1117;border:1px solid #30363d;border-radius:4px;padding:12px;margin-top:12px;font-size:12px;white-space:pre-wrap;max-height:200px;overflow-y:auto}
#exec-panel .close-exec{float:right;background:transparent;color:#8b949e;border:none;cursor:pointer;font-size:16px}
#exec-panel .close-exec:hover{color:#e6edf3}
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
.toggle{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:12px;font-size:11px;cursor:pointer;border:1px solid #30363d;background:#161b22;color:#8b949e;user-select:none;transition:all .2s;vertical-align:middle}
.toggle.on{background:#3fb95022;border-color:#3fb950;color:#3fb950}
.toggle.off{background:#f8514922;border-color:#f85149;color:#f85149}
.toggle .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.toggle.on .dot{background:#3fb950}
.toggle.off .dot{background:#f85149}
</style></head><body>
<header><h1>\u2699\uFE0F Workflow Builder</h1><a href="/">Chat</a>
<span class="toggle off" id="bot-toggle" onclick="toggleBot()"><span class="dot"></span> Bot</span>
<input class="wf-name" id="wf-name" placeholder="Workflow name..." value="Untitled Workflow"/>
<div class="toolbar"><button onclick="loadDialog()">Load</button><button onclick="saveWf()">Save</button><button onclick="exportWf()">Export</button><button class="primary" onclick="runWf()">Run</button><button class="danger" onclick="clearWf()">Clear</button></div></header>
<div id="main"><div id="palette"><h3>AI Providers</h3><div id="palette-list"></div></div>
<div id="canvas-wrap" oncontextmenu="return false"><div id="canvas"></div><svg id="svg-layer"></svg><div class="hint">Drag providers to canvas &bull; Connect output to input &bull; Click node to configure</div></div></div>
<div id="config-overlay"><div id="config-modal"></div></div>
<div id="exec-overlay"><div id="exec-panel"></div></div>
<script>
let nodes=[],edges=[],selectedId=null,nodeCounter=0,connecting=null,dragNode=null,dragOx=0,dragOy=0,providers=[],roles={},cfgNid=null,wfId=null;
async function loadP(){const r=await fetch('/api/provider-roles');const d=await r.json();providers=d.providers||[];roles=d.roles||{};renderP()}
function renderP(){const el=document.getElementById('palette-list');
el.innerHTML=providers.map(p=>{const r=roles[p.id]||{role:'Assistant',emoji:'\U0001F916'};return '<div class="palette-item" data-p="'+p.id+'" draggable="true"><span class="emoji">'+r.emoji+'</span><div class="info"><div class="name">'+r.role+'</div><div class="role">'+p.id+'</div></div><span class="status" style="background:'+(p.configured?'#3fb950':'#f85149')+'"></span></div>'}).join('');
document.querySelectorAll('.palette-item').forEach(e=>e.addEventListener('dragstart',ev=>ev.dataTransfer.setData('text/plain',e.dataset.p)))}
loadP();const cvs=document.getElementById('canvas'),svg=document.getElementById('svg-layer'),wrap=document.getElementById('canvas-wrap');
wrap.addEventListener('dragover',e=>e.preventDefault());
wrap.addEventListener('drop',e=>{e.preventDefault();const p=e.dataTransfer.getData('text/plain');if(!p)return;const r=wrap.getBoundingClientRect();addNode(p,e.clientX-r.left-90,e.clientY-r.top-30)});
wrap.addEventListener('mousedown',e=>{if(e.target===wrap||e.target===cvs||e.target.id==='svg-layer'){selectedId=null;document.querySelectorAll('.wf-node').forEach(el=>el.classList.remove('selected'))}});
wrap.addEventListener('mousemove',e=>{if(connecting){connecting.mx=e.clientX;connecting.my=e.clientY;renderE()}
if(!dragNode)return;const n=nodes.find(x=>x.id===dragNode);if(!n)return;const r=wrap.getBoundingClientRect();n.x=e.clientX-r.left-dragOx;n.y=e.clientY-r.top-dragOy;renderN();renderE()});
wrap.addEventListener('mouseup',e=>{if(connecting){const tgt=document.elementFromPoint(e.clientX,e.clientY);if(tgt&&tgt.classList.contains('port-in')){const ne=tgt.closest('.wf-node');if(ne&&ne.dataset.id!==connecting.source)addEdge(connecting.source,ne.dataset.id)}
connecting=null;renderE()}dragNode=null});
document.addEventListener('keydown',e=>{if(e.key==='Delete'||e.key==='Backspace'){if(document.querySelector('#config-overlay[style*="flex"]'))return;if(selectedId){delNode(selectedId);e.preventDefault()}}
if(e.key==='Escape'){closeCfg();closeExec();connecting=null;renderE()}});
window.addEventListener('resize',()=>renderE());
function addNode(p,x,y){const r=roles[p]||{emoji:'\U0001F916',color:'#6b7280',system_prompt:'You are a helpful assistant.'};const id='n'+(++nodeCounter);nodes.push({id,provider:p,label:(r.role||'Assistant')+' '+nodeCounter,x,y,system_prompt:r.system_prompt,temperature:.7});renderN();renderE();return id}
function renderN(){document.querySelectorAll('.wf-node').forEach(el=>{if(!nodes.find(n=>n.id===el.dataset.id))el.remove()});
nodes.forEach(n=>{let el=document.querySelector('.wf-node[data-id="'+n.id+'"]');const r=roles[n.provider]||{emoji:'\U0001F916',color:'#6b7280'};
if(!el){el=document.createElement('div');el.className='wf-node';el.dataset.id=n.id;
el.innerHTML='<div class="header" style="background:'+r.color+'22;color:'+r.color+'"><span>'+r.emoji+'</span><span>'+n.label+'</span></div><div class="body"><div class="provider-name">'+n.provider+'</div><div style="margin-top:2px">'+(r.role||'')+'</div></div><div class="port port-in"></div><div class="port port-out"></div><button class="delete-node" onclick="delNode(\''+n.id+'\')">\u2715</button><div class="status-icon"></div>';
el.addEventListener('mousedown',e=>{if(e.button!==0||e.target.classList.contains('port')||e.target.classList.contains('delete-node'))return;selectedId=n.id;document.querySelectorAll('.wf-node').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');dragNode=n.id;const r2=el.getBoundingClientRect();dragOx=e.clientX-r2.left;dragOy=e.clientY-r2.top;e.preventDefault()});
el.addEventListener('dblclick',()=>openCfg(n.id));
cvs.appendChild(el)}
el.style.left=n.x+'px';el.style.top=n.y+'px';if(selectedId===n.id)el.classList.add('selected');else el.classList.remove('selected');
el.querySelector('.port-out').onmousedown=e=>{e.stopPropagation();connecting={source:n.id,mx:e.clientX,my:e.clientY};e.preventDefault()};
el.querySelector('.port-in').onmouseup=e=>{e.stopPropagation();if(connecting&&connecting.source!==n.id)addEdge(connecting.source,n.id);connecting=null;renderE()}})}
function renderE(){while(svg.firstChild)svg.removeChild(svg.firstChild);const wr=wrap.getBoundingClientRect();
edges.forEach(e=>{const src=document.querySelector('.wf-node[data-id="'+e.source+'"]'),tgt=document.querySelector('.wf-node[data-id="'+e.target+'"]');if(!src||!tgt)return;
const so=src.querySelector('.port-out'),ti=tgt.querySelector('.port-in');if(!so||!ti)return;
const sr=so.getBoundingClientRect(),tr=ti.getBoundingClientRect();const x1=sr.left+sr.width/2-wr.left,y1=sr.top+sr.height/2-wr.top,x2=tr.left+tr.width/2-wr.left,y2=tr.top+tr.height/2-wr.top,my=(y1+y2)/2;
const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d','M '+x1+' '+y1+' C '+x1+' '+my+', '+x2+' '+my+', '+x2+' '+y2);p.setAttribute('stroke','#58a6ff');p.setAttribute('stroke-width','2');p.setAttribute('fill','none');p.style.pointerEvents='stroke';p.style.cursor='pointer';p.onclick=()=>{edges=edges.filter(x=>x.id!==e.id);renderE()};svg.appendChild(p)});
if(connecting){const src=document.querySelector('.wf-node[data-id="'+connecting.source+'"]');if(src){const so=src.querySelector('.port-out');if(so){const sr=so.getBoundingClientRect(),wr2=wrap.getBoundingClientRect();const x1=sr.left+sr.width/2-wr2.left,y1=sr.top+sr.height/2-wr2.top,x2=connecting.mx-wr2.left,y2=connecting.my-wr2.top,my2=(y1+y2)/2;
const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d','M '+x1+' '+y1+' C '+x1+' '+my2+', '+x2+' '+my2+', '+x2+' '+y2);p.setAttribute('stroke','#58a6ff66');p.setAttribute('stroke-width','2');p.setAttribute('stroke-dasharray','5,5');p.setAttribute('fill','none');p.id='tmp-c';svg.appendChild(p)}}}}
function addEdge(s,t){if(s===t||edges.find(e=>e.source===s&&e.target===t))return;edges.push({id:'e'+Date.now(),source:s,target:t});renderE()}
function delNode(id){nodes=nodes.filter(n=>n.id!==id);edges=edges.filter(e=>e.source!==id&&e.target!==id);if(selectedId===id)selectedId=null;renderN();renderE()}
function openCfg(id){const n=nodes.find(x=>x.id===id);if(!n)return;cfgNid=id;const r=roles[n.provider]||{};
document.getElementById('config-modal').innerHTML='<h3>Configure <span style="color:'+(r.color||'#58a6ff')+'">'+n.label+'</span></h3><label>Provider</label><input value="'+n.provider+'" disabled style="opacity:.6"/><label>Label</label><input id="c-l" value="'+n.label+'"/><label>System Prompt</label><textarea id="c-p" rows="4">'+(n.system_prompt||r.system_prompt||'')+'</textarea><label>Temperature (0-2)</label><input id="c-t" type="number" min="0" max="2" step=".1" value="'+(n.temperature||.7)+'"/><div class="btn-row"><button class="save" onclick="saveCfg()">Save</button><button class="cancel" onclick="closeCfg()">Cancel</button></div>';
document.getElementById('config-overlay').style.display='flex'}
function saveCfg(){const n=nodes.find(x=>x.id===cfgNid);if(!n)return;n.label=document.getElementById('c-l').value||n.label;n.system_prompt=document.getElementById('c-p').value||'';const t=parseFloat(document.getElementById('c-t').value);n.temperature=isNaN(t)?.7:Math.max(0,Math.min(2,t));closeCfg();renderN()}
function closeCfg(){document.getElementById('config-overlay').style.display='none';cfgNid=null}
async function saveWf(){const nm=document.getElementById('wf-name').value||'Untitled';const w={name:nm,nodes,edges};if(wfId)w.id=wfId;
const r=await fetch('/api/workflows'+(wfId?'/'+wfId:''),{method:wfId?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(w)});const d=await r.json();if(d.id){wfId=d.id;document.getElementById('wf-name').value=d.name||nm;toast('Saved: '+(d.name||nm))}else toast('Save failed')}
async function loadDialog(){const r=await fetch('/api/workflows');const list=await r.json();if(!list.length){toast('No saved workflows');return}
document.getElementById('config-modal').innerHTML='<h3>Load Workflow</h3><div style="max-height:300px;overflow-y:auto">'+list.map(w=>'<div class="palette-item" style="cursor:pointer" onclick="loadWf(\''+w.id+'\')"><span style="color:#58a6ff">\U0001F4C4</span><div class="info"><div class="name">'+(w.name||'Unnamed')+'</div><div class="role">'+w.node_count+' nodes</div></div></div>').join('')+'</div><div class="btn-row"><button class="cancel" onclick="closeCfg()">Cancel</button></div>';
document.getElementById('config-overlay').style.display='flex'}
async function loadWf(id){closeCfg();const r=await fetch('/api/workflows/'+id);const w=await r.json();if(w.error){toast('Load failed');return}
nodes=(w.nodes||[]).map(n=>({...n}));edges=(w.edges||[]).map(e=>({...e}));wfId=w.id;document.getElementById('wf-name').value=w.name||'Untitled';nodeCounter=nodes.length;selectedId=null;renderN();renderE();toast('Loaded: '+(w.name||'Untitled'))}
function exportWf(){const w={name:document.getElementById('wf-name').value,nodes,edges};const b=new Blob([JSON.stringify(w,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=(w.name||'workflow').replace(/\s+/g,'_')+'.json';a.click();URL.revokeObjectURL(a.href);toast('Exported')}
async function runWf(){if(!nodes.length){toast('Add at least one node');return}
const ov=document.getElementById('exec-overlay'),pn=document.getElementById('exec-panel');pn.innerHTML='<h3>Executing <span class="close-exec" onclick="closeExec()">\u2715</span></h3><div id="exec-steps"></div>';ov.style.display='flex';
try{const r=await fetch('/api/workflows/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('wf-name').value,nodes,edges})});const res=await r.json();
if(res.error){document.getElementById('exec-steps').innerHTML='<div class="step error">Error: '+res.error+'</div>';return}
let h='<div style="margin-bottom:8px;font-size:12px;color:#8b949e">'+(res.success_count||0)+'/'+res.total_nodes+' ok &bull; '+(res.total_time||'0')+'s</div>';
(res.steps||[]).forEach(s=>{h+='<div class="step '+s.status+'"><span>'+(s.status==='ok'?'\u2713':'\u2717')+'</span><span>'+(s.node_name||s.node_id)+'</span>'+(s.elapsed?'<span class="time">'+s.elapsed+'s</span>':'')+(s.preview?'<div class="preview">'+s.preview+'...</div>':'')+(s.error?'<div class="preview" style="color:#f85149">'+s.error+'</div>':'')+'</div>'});
if(res.final_output)h+='<h4 style="font-size:12px;margin:12px 0 4px;color:#8b949e">Final Output</h4><div class="final-output">'+res.final_output+'</div>';
document.getElementById('exec-steps').innerHTML=h;
(res.steps||[]).forEach(s=>{const el=document.querySelector('.wf-node[data-id="'+s.node_id+'"]');if(el){el.classList.remove('executing');el.classList.add(s.status==='ok'?'done':'error')}})
}catch(e){document.getElementById('exec-steps').innerHTML='<div class="step error">Error: '+e.message+'</div>'}}
function closeExec(){document.getElementById('exec-overlay').style.display='none';document.querySelectorAll('.wf-node').forEach(el=>el.classList.remove('executing','done','error'))}
function clearWf(){if(nodes.length&&!confirm('Clear all nodes?'))return;nodes=[];edges=[];selectedId=null;wfId=null;nodeCounter=0;document.getElementById('wf-name').value='Untitled Workflow';renderN();renderE()}
function toast(m){let t=document.getElementById('toast');if(!t){t=document.createElement('div');t.id='toast';t.style.cssText='position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#161b22;border:1px solid #30363d;padding:8px 20px;border-radius:6px;font-size:12px;z-index:200;transition:opacity .3s;opacity:0';document.body.appendChild(t)}
t.textContent=m;t.style.opacity='1';clearTimeout(t._hide);t._hide=setTimeout(()=>t.style.opacity='0',2500)}
renderN();renderE();
async function updateBot(){try{const r=await fetch('/api/bot/status');const j=await r.json();const el=document.getElementById('bot-toggle');if(j.running){el.className='toggle on';el.innerHTML='<span class=\"dot\"></span> Bot ON'}else{el.className='toggle off';el.innerHTML='<span class=\"dot\"></span> Bot OFF'}}catch(e){}}
async function toggleBot(){const el=document.getElementById('bot-toggle');const isOn=el.classList.contains('on');el.style.opacity='0.5';try{const r=await fetch(isOn?'/api/bot/stop':'/api/bot/start',{method:'POST'});await r.json();await updateBot()}catch(e){}el.style.opacity='1'}
updateBot();setInterval(updateBot,5000);
</script></body></html>"""

# ---- Route Handlers ----

@route("GET", "/")
async def handle_root(method, path, headers, body, params):
    models = get_available_models()
    configured = [m for m in models if m["configured"]]
    unconfigured = [m for m in models if not m["configured"]]
    opts = "".join('<option value="'+m["id"]+'">'+m["provider"]+" \u2014 "+m["model"]+"</option>" for m in configured)
    uopts = "".join('<option value="'+m["id"]+'" disabled>'+m["provider"]+" \u2014 "+m["model"]+" (no key)</option>" for m in unconfigured)
    html = _CHAT_HTML.replace("__STATUS__", f"{len(configured)}/{len(models)} ready")
    html = html.replace("__OPTIONS__", opts + uopts)
    return html_response(html)

@route("GET", "/workflow")
async def handle_workflow(method, path, headers, body, params):
    return html_response(WORKFLOW_HTML)

@route("GET", "/api/provider-roles")
async def handle_provider_roles(method, path, headers, body, params):
    return json_response({"providers": get_available_providers(), "roles": PROVIDER_ROLES})

@route("GET", "/api/workflows")
async def handle_list_workflows(method, path, headers, body, params):
    return json_response([{"id": k, "name": v.get("name", "Unnamed"), "node_count": len(v.get("nodes", [])), "edge_count": len(v.get("edges", []))} for k, v in WORKFLOWS.items()])

def _parse_body(body):
    try:
        return json.loads(body) if body and body.strip() else {}
    except json.JSONDecodeError as e:
        return {"_parse_error": str(e)}

@route("POST", "/api/workflows")
async def handle_create_workflow(method, path, headers, body, params):
    global _next_wf_id
    data = _parse_body(body)
    if "_parse_error" in data:
        return json_response({"error": "Invalid JSON: " + data["_parse_error"]}, 400)
    wf_id = str(_next_wf_id)
    _next_wf_id += 1
    WORKFLOWS[wf_id] = {"id": wf_id, "name": data.get("name", "Untitled"), "nodes": data.get("nodes", []), "edges": data.get("edges", []), "created": time.time()}
    _save_workflows()
    return json_response({"id": wf_id, "name": WORKFLOWS[wf_id]["name"]}, 201)

@route("GET", "/api/workflows/{wf_id}")
async def handle_get_workflow(method, path, headers, body, params):
    wf = WORKFLOWS.get(params["wf_id"])
    if not wf:
        return json_response({"error": "Not found"}, 404)
    return json_response(wf)

@route("PUT", "/api/workflows/{wf_id}")
async def handle_update_workflow(method, path, headers, body, params):
    wf = WORKFLOWS.get(params["wf_id"])
    if not wf:
        return json_response({"error": "Not found"}, 404)
    data = _parse_body(body)
    if "_parse_error" in data:
        return json_response({"error": "Invalid JSON: " + data["_parse_error"]}, 400)
    wf["name"] = data.get("name", wf["name"])
    wf["nodes"] = data.get("nodes", wf["nodes"])
    wf["edges"] = data.get("edges", wf["edges"])
    wf["updated"] = time.time()
    _save_workflows()
    return json_response({"id": params["wf_id"], "name": wf["name"]})

@route("DELETE", "/api/workflows/{wf_id}")
async def handle_delete_workflow(method, path, headers, body, params):
    if params["wf_id"] in WORKFLOWS:
        del WORKFLOWS[params["wf_id"]]
        _save_workflows()
        return json_response({"ok": True})
    return json_response({"error": "Not found"}, 404)

@route("POST", "/api/workflows/execute")
async def handle_execute_workflow(method, path, headers, body, params):
    data = _parse_body(body)
    if "_parse_error" in data:
        return json_response({"error": "Invalid JSON: " + data["_parse_error"]}, 400)
    engine = data.get("engine", "builtin")
    if engine == "crewai":
        result = await execute_workflow_crewai(data)
        if result.get("fallback"):
            result = await execute_workflow(data)
    else:
        result = await execute_workflow(data)
    return json_response(result)

@route("GET", "/api/models")
async def handle_models(method, path, headers, body, params):
    return json_response(get_available_models())

@route("GET", "/api/providers")
async def handle_providers(method, path, headers, body, params):
    return json_response(get_available_providers())

@route("GET", "/api/bot/status")
async def handle_bot_status(method, path, headers, body, params):
    return json_response(bot_status())

@route("POST", "/api/bot/start")
async def handle_bot_start(method, path, headers, body, params):
    result = bot_start()
    return json_response({"result": result, "status": bot_status()})

@route("POST", "/api/bot/stop")
async def handle_bot_stop(method, path, headers, body, params):
    result = bot_stop()
    return json_response({"result": result, "status": bot_status()})

@route("GET", "/api/bot/logs")
async def handle_bot_logs(method, path, headers, body, params):
    n = int(headers.get("x-log-count", 50))
    return json_response({"logs": bot_logs(n)})

@route("POST", "/v1/chat/completions")
async def handle_chat(method, path, headers, body, params):
    data = _parse_body(body)
    if "_parse_error" in data:
        return json_response({"error": {"message": "Invalid JSON: " + data["_parse_error"]}}, 400)
    model_id = data.get("model", "groq")
    messages = data.get("messages", [])
    stream = data.get("stream", False)
    if not messages:
        return json_response({"error": {"message": "No messages"}}, 400)
    if model_id not in PROVIDERS:
        return json_response({"error": {"message": "Unknown model: " + model_id}}, 400)
    result = await call_provider(messages, model_id)
    content = result.get("content", "")
    error = result.get("error")
    if error:
        return json_response({"error": {"message": error}}, 500)
    return json_response({
        "id": "chatcmpl-" + str(int(time.time())),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_id,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })

# ---- MCP Routes ----

@route("POST", "/mcp")
async def handle_mcp(method, path, headers, body, params):
    result = await _mcp_handle(body)
    return json_response(result)

@route("GET", "/mcp/sse")
async def handle_mcp_sse(method, path, headers, body, params):
    w = params.get("_writer")
    if w is None:
        return json_response({"error": "no writer"})
    try:
        reason = "OK"
        resp = f"HTTP/1.1 200 {reason}\r\nContent-Type: text/event-stream\r\nCache-Control: no-cache\r\nConnection: keep-alive\r\nAccess-Control-Allow-Origin: *\r\n\r\n"
        w.write(resp.encode())
        await w.drain()
        await asyncio.sleep(0.5)
        endpoint_event = f"event: endpoint\ndata: /mcp\n\n"
        w.write(endpoint_event.encode())
        await w.drain()
        while True:
            await asyncio.sleep(15)
            w.write(f": keepalive\n\n".encode())
            await w.drain()
    except:
        pass
    finally:
        try: w.close()
        except: pass
    return ("__sse__", None)

@route("GET", "/api/mcp-tools")
async def handle_mcp_tools(method, path, headers, body, params):
    return json_response({"tools": MCP_TOOLS})

# ---- Server ----

async def _serve(host, port):
    server = await asyncio.start_server(_handle, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Gateway running on http://{addr[0]}:{addr[1]}")
    print(f"Chat: http://{addr[0]}:{addr[1]}/")
    print(f"Workflow Builder: http://{addr[0]}:{addr[1]}/workflow")
    print(f"MCP Endpoint: POST http://{addr[0]}:{addr[1]}/mcp (JSON-RPC 2.0)")
    print(f"MCP SSE: http://{addr[0]}:{addr[1]}/mcp/sse")
    if PROVIDERS.get("omniroute", {}).get("key") != "not configured" or PROVIDERS.get("omniroute", {}).get("key", "") == "skip-auth":
        print(f"OmniRoute: http://{addr[0]}:{addr[1]}/v1 → local OmniRoute gateway")
    if HAS_CREWAI:
        print(f"CrewAI engine: available (use engine=crewai in workflow)")
    async with server:
        await server.serve_forever()

def run(port=4357, host="0.0.0.0"):
    print(f"OpenCode AI Gateway starting on {host}:{port}")
    configured = sum(1 for p in PROVIDERS.values() if _is_configured(p.get("key", "")))
    print(f"Providers: {len(PROVIDERS)} total, {configured} configured")
    try:
        asyncio.run(_serve(host, port))
    except KeyboardInterrupt:
        print("Shutting down...")

def start(port=4357, host="0.0.0.0"):
    t = threading.Thread(target=run, args=(port, host), daemon=True)
    t.start()
    return f"Gateway running on http://{host}:{port}"

if __name__ == "__main__":
    run()
