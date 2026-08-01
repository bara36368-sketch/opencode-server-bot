import sys, os, json, signal, traceback as _tb, io as _io, re as _re
from datetime import datetime

def _security_check():
    issues = []
    setenv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setenv.sh")
    if os.path.exists(setenv):
        with open(setenv, encoding="utf-8") as f:
            content = f.read()
        keys = _re.findall(r'export\s+(\w+)="([^"]+)"', content)
        credential_suffixes = ("_KEY", "_TOKEN", "_PASSWORD", "_SECRET", "_CREDENTIALS")
        for name, val in keys:
            if any(sfx in name for sfx in credential_suffixes) and val not in ("set-via-env-var", "", "skip-auth") and not val.startswith("$"):
                issues.append(f"HARDCODED KEY: {name} in setenv.sh")
    providers = os.path.join(os.path.dirname(os.path.abspath(__file__)), "providers.json")
    if os.path.exists(providers):
        with open(providers, encoding="utf-8") as f:
            pdata = json.load(f)
        for pname, pconf in pdata.items():
            if isinstance(pconf, dict) and pconf.get("key") and pconf["key"] not in ("set-via-env-var", "skip-auth", ""):
                issues.append(f"HARDCODED KEY: {pname} in providers.json")
    if issues:
        try:
            with open("security_warnings.txt", "w", encoding="utf-8") as f:
                f.write(f"Security warnings ({len(issues)}):\n")
                for i in issues:
                    f.write(f"  - {i}\n")
        except Exception:
            pass
        print(f"[security] {len(issues)} hardcoded API keys detected (see security_warnings.txt)")

_security_check()

_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot.lock")
def _check_single_instance():
    try:
        if os.path.exists(_LOCK_FILE):
            with open(_LOCK_FILE, encoding="utf-8") as _f:
                _old_pid = int(_f.read().strip())
            _alive = False
            if os.name == "nt":
                import ctypes
                _h = ctypes.windll.kernel32.OpenProcess(1, 0, _old_pid)
                if _h:
                    ctypes.windll.kernel32.CloseHandle(_h)
                    _alive = True
            else:
                try:
                    os.kill(_old_pid, 0)
                    _alive = True
                except PermissionError:
                    try:
                        _ = open(f"/proc/{_old_pid}/status", encoding="utf-8")
                        _.close()
                        _alive = True
                    except Exception:
                        pass
                except Exception:
                    pass
            if _alive:
                sys.exit(0)
    except Exception:
        pass
    try:
        with open(_LOCK_FILE, "w", encoding="utf-8") as _f:
            _f.write(str(os.getpid()))
    except Exception:
        pass
_check_single_instance()

_M = object()
asyncio=_M; httpx=_M; json=_M; uuid=_M; time=_M; copy=_M; re=_M; random=_M; urllib=_M
try:
    import asyncio, json, uuid, time, copy, re, random, urllib.parse, html
except Exception:
    try:
        with open("bot_crash.txt", "w", encoding="utf-8") as _f:
            _f.write(f"stdlib import failed:\n{_tb.format_exc()}")
    except Exception:
        pass
    raise
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
try:
    import httpx
except Exception:
    try:
        with open("bot_crash.txt", "w", encoding="utf-8") as _f:
            _f.write(f"httpx import failed (non-fatal):\n{_tb.format_exc()}")
    except Exception:
        pass

try:
    import pyrit_attacks
except Exception:
    try:
        with open("bot_crash.txt", "w", encoding="utf-8") as _f:
            _f.write(f"pyrit import failed:\n{_tb.format_exc()}")
    except Exception:
        pass
    pyrit_attacks = None

class _BfStub:
    class _DbStub:
        def add_document(self, *a, **k): return 0
        def list(self, *a, **k): return []
        def query(self, *a, **k): return []
    class _SchedulerStub:
        def add(self, *a, **k): return ""
        def remove(self, *a, **k): pass
        def list(self, *a, **k): return []
    class _ReminderStub:
        def add(self, *a, **k): return ""
        def remove(self, *a, **k): pass
        def list(self, *a, **k): return []
        def clear_chat(self, *a, **k): pass
    def __init__(self):
        self.doc_db = self._DbStub()
        self.scheduler = self._SchedulerStub()
        self.reminder_db = self._ReminderStub()
    def __getattr__(self, name):
        async def _a(*a, **k): return None
        def _s(*a, **k): return None
        return _a if name.startswith(("run_", "voice_", "text_to_", "vision_", "image_", "translate", "web_search", "youtube_", "run_code", "fetch_url", "qr_", "auto_context", "summarize_", "get_photo_url", "extract_", "parse_spread", "youtube_search", "tiktok_search", "github_search", "analyze_github_repo", "append_to_memory_log", "get_memory_context", "search_user_memories", "get_memory_stats", "clear_user_memory", "reddit_search", "hackernews_search", "medium_search", "x_search", "social_search_all", "analyze_document", "ask_document", "analyze_document_with_vision", "list_cached_documents", "clear_document_cache", "extract_pdf_text_fallback", "run_page_monitor_loop")) else _s

try:
    import bot_features as bf
    _ = bf  # verify it actually loaded
except Exception as _bf_err:
    try:
        with open("bot_crash.txt", "w", encoding="utf-8") as _f:
            _f.write(f"bot_features import failed: {_bf_err}\n{_tb.format_exc()}")
    except Exception:
        pass
    bf = _BfStub()

_modules_to_lazy = {
    "stack_ref": "ai_stack_reference",
    "ai_stack": "ai_stack_combined",
    "kg_mod": "knowledge_graph",
    "market_mod": "agent_marketplace",
    "vid_mod": "video_generator",
    "guard_mod": "guardian",
    "rich_mod": "rich_message",
    "styles_mod": "ai_styles",
    "pollplus_mod": "poll_plus",
    "pw_mod": "paywall",
    "ca_mod": "content_automation",
    "an_mod": "analytics",
    "safety_mod": "safety_moderation",
    "dev_mod": "coding_dev",
    "ai_int_mod": "ai_intelligence",
    "comm_mod": "community_engagement",
    "auto_mod": "automation_productivity",
    "sec_mod": "security_api",
    "nf_mod": "new_features",
    "loc_mod": "location_distance",
    "ma_mod": "mini_app",
    "rt2_mod": "rich_text_v2",
    "cv_mod": "computer_vision",
    "n8n_mod": "n8n_workflow",
}
class _LazyProxy:
    def __init__(self, mod_name):
        self._mod_name = mod_name
        self._mod = None
        self._failed = False
    def _load(self):
        if self._mod is None and not self._failed:
            try:
                import importlib
                self._mod = importlib.import_module(self._mod_name)
            except Exception:
                self._failed = True
        return self._mod
    def __getattr__(self, name):
        m = self._load()
        if m is None:
            raise AttributeError(name)
        return getattr(m, name)
    def __repr__(self):
        m = self._load()
        return repr(m) if m else f"<lazy module {self._mod_name} (failed)>"
    def __bool__(self):
        return self._load() is not None
    def __call__(self, *a, **kw):
        m = self._load()
        if m is None:
            raise RuntimeError(f"Module {self._mod_name} not available")
        return m(*a, **kw)

for _var, _mod in _modules_to_lazy.items():
    globals()[_var] = _LazyProxy(_mod)

try:
    import aiohttp
except Exception:
    aiohttp = None

class _LazyModule:
    def __init__(self, name, attr_name=None):
        self._name = name
        self._attr = attr_name or name
        self._mod = None
    def _load(self):
        if self._mod is None:
            import importlib
            self._mod = importlib.import_module(self._name)
        return self._mod
    def __getattr__(self, name):
        return getattr(self._load(), name)
    def __bool__(self):
        try:
            self._load()
            return True
        except Exception:
            return False

def _safe_track_usage(uid, agent, provider):
    global bf
    if bf:
        try:
            bf.track_usage(uid, agent, provider)
        except Exception as _e:
            log(f"track_usage failed: {_e}")

_http = None
_save_counter = 0

_rate_limits = {}
_announced_versions = set()
_ANNOUNCED_FILE = os.path.join(os.path.dirname(__file__), "announced_versions.json")
try:
    if os.path.exists(_ANNOUNCED_FILE):
        with open(_ANNOUNCED_FILE, encoding="utf-8") as _af:
            _announced_versions = set(json.load(_af))
except Exception:
    pass
def _save_announced_versions():
    try:
        with open(_ANNOUNCED_FILE, "w", encoding="utf-8") as _af:
            json.dump(list(_announced_versions), _af)
    except Exception:
        pass
def _check_rate_limit(key, max_calls=5, window=60):
    return True

async def get_http():
    global _http
    if httpx is _M or not hasattr(httpx, "AsyncClient"):
        raise RuntimeError("httpx is not installed. Install with: pip install httpx")
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10, read=60, write=30, pool=10),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30),
            http2=False,
        )
    return _http

AGENTS_FILE = os.path.join(os.path.dirname(__file__), "agents.json")
PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), "providers.json")
PREMADE_SKILLS_FILE = os.path.join(os.path.dirname(__file__), "premade_skills.json")
TEAMS_FILE = os.path.join(os.path.dirname(__file__), "teams.json")
SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")
ADMINS_FILE = os.path.join(os.path.dirname(__file__), "admins.json")
MODS_FILE = os.path.join(os.path.dirname(__file__), "mods.json")
AGENT_PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), "agent_providers.json")
SYNOXCLOUD_ENDPOINTS_FILE = os.path.join(os.path.dirname(__file__), "synoxcloud_endpoints.json")
SYNOXCLOUD_AI_MODELS_FILE = os.path.join(os.path.dirname(__file__), "synoxcloud_ai_models.json")
ROUTINES_FILE = os.path.join(os.path.dirname(__file__), "routines.json")
MULTI_FILE = os.path.join(os.path.dirname(__file__), "multi_sessions.json")

try:
    LOG = open("bot.log", "a", encoding="utf-8")
except Exception:
    LOG = None
def log(msg):
    if LOG:
        LOG.write(f"{msg}\n")
        LOG.flush()

DEFAULT_RATE_LIMITS = {
    "groq": (30, 14400),
    "cerebras": (30, 14400),
    "gemini": (15, 1500),
    "sambanova": (20, 20),
    "nvidia": (40, 2000),
    "openrouter": (10, 1000),
    "deepseek": (30, 10000),
    "mistral": (30, 10000),
    "vansrouter": (9999, 999999),
    "blackbox": (30, 60000),
    "openclaw": (9999, 999999),
    "github": (30, 15000),
    "together": (30, 10000),
    "fireworks": (30, 10000),
    "cohere": (20, 5000),
    "xai": (30, 10000),
    "lepton": (20, 5000),
    "imarena": (30, 60000),
    "synoxcloud": (30, 60000),
    "hy3": (30, 10000),
    "hy3-preview": (30, 10000),
    "bitrouter": (9999, 999999),
    "omniroute": (9999, 999999),
    "siliconflow": (30, 60000),
    "pollinations": (60, 100000),
    "llm7": (30, 50000),
    "ovh": (30, 50000),
    "freetheai": (30, 60000),
}

class SlidingWindow:
    def __init__(self, rpm, rpd):
        self.rpm = rpm
        self.rpd = rpd
        self.min_ts = []
        self.day_ts = []
    def is_allowed(self):
        now = time.time()
        self.min_ts = [t for t in self.min_ts if t > now - 60]
        self.day_ts = [t for t in self.day_ts if t > now - 86400]
        return len(self.min_ts) < self.rpm and len(self.day_ts) < self.rpd
    def record(self):
        now = time.time()
        self.min_ts.append(now)
        self.day_ts.append(now)
    def remaining(self):
        now = time.time()
        self.min_ts = [t for t in self.min_ts if t > now - 60]
        return max(0, self.rpm - len(self.min_ts))
    def wait_seconds(self):
        if len(self.min_ts) < self.rpm:
            return 0
        sorted_ts = sorted(self.min_ts, reverse=True)
        return max(0, sorted_ts[self.rpm - 1] + 60 - time.time())

def _is_configured(key):
    return bool(key) and "YOUR_" not in key and key != "not configured"

class ProviderGateway:
    def __init__(self):
        self.health = {}
        self.ratelimits = {}
        self.requests = {}
        self._queue = asyncio.Queue()
        self._worker = None
    def init_providers(self):
        for name in PROVIDERS:
            configured = _is_configured(PROVIDERS[name].get("key", ""))
            self.health[name] = {"success": 0, "failure": 0, "last_fail": 0, "cooldown_until": 0, "avg_latency": 0.0, "configured": configured}
            rpm, rpd = DEFAULT_RATE_LIMITS.get(name, (30, 1000))
            self.ratelimits[name] = SlidingWindow(rpm, rpd)
            self.requests[name] = 0
    def can_try(self, name):
        h = self.health.get(name, {})
        if not h.get("configured", False):
            return False
        if h.get("cooldown_until", 0) > time.time():
            return False
        rl = self.ratelimits.get(name)
        if rl and not rl.is_allowed():
            return False
        return True
    def record(self, name, elapsed, success):
        h = self.health[name]
        self.requests[name] += 1
        self.ratelimits[name].record()
        if success:
            h["success"] += 1
            h["avg_latency"] = (h["avg_latency"] * (h["success"] - 1) + elapsed) / h["success"]
        else:
            h["failure"] += 1
            h["last_fail"] = time.time()
            h["cooldown_until"] = time.time() + min(60 * max(h["failure"] - h["success"], 1), 300)
    def best_available(self):
        candidates = []
        for name in PROVIDERS:
            if not self.can_try(name):
                continue
            h = self.health[name]
            score = h.get("avg_latency", 5) + h.get("failure", 0) * 5
            candidates.append((score, name))
        if not candidates:
            return None
        candidates.sort()
        return candidates[0][1]
    def fallback_chain(self, preferred, count=4):
        available = [n for n in PROVIDERS if self.can_try(n)]
        random.shuffle(available)
        chain = [preferred] if preferred in available else []
        for n in available:
            if n not in chain and len(chain) < count:
                chain.append(n)
        return chain
    def next_available(self):
        best = 9999
        for name in PROVIDERS:
            h = self.health.get(name, {})
            cd = h.get("cooldown_until", 0) - time.time()
            if cd > 0:
                best = min(best, cd)
                continue
            rl = self.ratelimits.get(name)
            if rl:
                w = rl.wait_seconds()
                if w > 0:
                    best = min(best, w)
                else:
                    return 0
        return best if best < 9999 else 60
    async def execute(self, messages, preferred, _retries=0):
        max_retries = 5
        while _retries < max_retries:
            chain = self.fallback_chain(preferred)
            t0 = time.time()
            errors = []
            for provider in chain:
                t1 = time.time()
                try:
                    result = await asyncio.wait_for(call_provider(messages, provider), timeout=25)
                    elapsed = time.time() - t1
                    if isinstance(result, str) and "error" in result.lower()[:20]:
                        self.record(provider, elapsed, False)
                        errors.append(f"{provider}: {result[:80]}")
                        continue
                    self.record(provider, elapsed, True)
                    log(f"gateway: {provider} in {time.time()-t0:.1f}s")
                    return result
                except asyncio.TimeoutError:
                    self.record(provider, 25, False)
                    errors.append(f"{provider}: timeout")
                except Exception as e:
                    self.record(provider, time.time()-t1, False)
                    errors.append(f"{provider}: {e}")
            _retries += 1
            wait = self.next_available()
            retry_in = max(wait, 5) if wait > 0 else 10
            if _retries >= max_retries:
                break
            log(f"gateway: all failed, retrying in {retry_in:.0f}s (attempt {_retries}/{max_retries})")
            await asyncio.sleep(min(retry_in, 30))
        return f"All providers failed.\n" + "\n".join(errors) + f"\nNext available in {wait:.0f}s."
    def get_route_health(self):
        global active_provider
        lines = []
        for name in sorted(PROVIDERS.keys()):
            h = self.health[name]
            if not h.get("configured", False):
                lines.append(f"  {name}: not configured")
                continue
            status = "OK" if h["cooldown_until"] <= time.time() else f"cooldown {h['cooldown_until']-time.time():.0f}s"
            rl = self.ratelimits[name]
            m = " << active" if name == active_provider else ""
            lines.append(f"  {name}{m}: {status} | RPM {rl.remaining()}/{rl.rpm} | {h['success']}ok/{h['failure']}fail | {h['avg_latency']:.1f}s | {self.requests[name]}req")
        return "\n".join(lines)
    def get_gateway_stats(self):
        lines = [f"Gateway stats ({len(PROVIDERS)} providers):"]
        for name in sorted(PROVIDERS.keys()):
            h = self.health[name]
            if not h.get("configured", False):
                lines.append(f"  {name}: not configured")
                continue
            rl = self.ratelimits[name]
            status = "OK" if h["cooldown_until"] <= time.time() else f"CD {h['cooldown_until']-time.time():.0f}s"
            lines.append(f"  {name}: {status} | RPM {rl.remaining()}/{rl.rpm} | {h['success']}/{h['failure']} | {h['avg_latency']:.1f}s | {self.requests[name]}req")
        wait = self.next_available()
        if wait > 0:
            lines.append(f"\nNext provider free: {wait:.0f}s")
        lines.append(f"Queue: ~{self._queue.qsize()} pending")
        return "\n".join(lines)
    async def start_worker(self):
        self._worker = asyncio.create_task(self._queue_worker())
        self._worker.add_done_callback(_task_done)
    async def enqueue(self, messages, preferred, chat_id, uid):
        await self._queue.put((messages, preferred, chat_id, uid))
    async def _queue_worker(self):
        while True:
            try:
                messages, preferred, chat_id, uid = await self._queue.get()
                result = await self.execute(messages, preferred)
                if not result.startswith("All providers failed"):
                    sessions.setdefault(uid, [])
                    sessions[uid].append({"role": "assistant", "content": result})
                    save_sessions()
                await send(chat_id, result)
            except Exception as e:
                log(f"Queue worker error: {e}")
            await asyncio.sleep(0.5)

gateway = ProviderGateway()

_shutdown_event = asyncio.Event()

def _task_done(t):
    try:
        e = t.exception()
        if e:
            log(f"Background task failed: {type(e).__name__}: {e}")
    except (asyncio.CancelledError, RuntimeError):
        pass
def _handle_signal():
    _shutdown_event.set()
    log("Shutdown signal received, saving state...")

try:
    with open(os.path.join(os.path.dirname(__file__), ".env"), encoding="utf-8") as _env_f:
        for _env_line in _env_f:
            _env_line = _env_line.strip()
            if _env_line and not _env_line.startswith("#") and "=" in _env_line:
                _k, _v = _env_line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())
except Exception:
    pass

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
TG_API = f"https://api.telegram.org/bot{TOKEN}"
BOT_VERSION = "unknown"

DEFAULT_AGENTS = {
    "orchestrator": {
        "desc": "Orchestrates and delegates tasks to specialized agents",
        "prompt": "You are the orchestrator. Analyze the user's request and coordinate with appropriate specialized agents to solve their problem. Route tasks to the right expert and synthesize results.",
    },
    "ai-researcher": {
        "desc": "This agent is for AI research and ML prototyping",
        "prompt": "You analyze research papers, design and run experiments, prototype novel ML approaches, and stay current with state-of-the-art AI and deep learning advances.",
    },
    "analytics-engineer": {
        "desc": "This agent is for BI dashboards and SQL reporting",
        "prompt": "You build analytics pipelines, design BI dashboards, write complex SQL queries, create reports, and transform raw data into business intelligence insights.",
    },
    "api-dev": {
        "desc": "This agent is for REST, GraphQL, and gRPC API design",
        "prompt": "You design and implement APIs using REST, GraphQL, gRPC, and WebSocket protocols with proper versioning, pagination, error handling, and documentation.",
    },
    "backend-dev": {
        "desc": "This agent is for NodeJS/Python backend services",
        "prompt": "You build backend services with NodeJS and Python, design REST and GraphQL APIs, implement authentication, and structure scalable server architectures.",
    },
    "blockchain-dev": {
        "desc": "This agent is for Solidity smart contracts and web3",
        "prompt": "You develop smart contracts in Solidity, build decentralized applications, integrate web3 libraries, and implement blockchain protocols and tokenomics.",
    },
    "cloud-architect": {
        "desc": "This agent is for AWS, Azure, GCP cloud architecture",
        "prompt": "You design cloud architectures, plan migrations, optimize costs, implement serverless solutions, and ensure Well-Architected Framework compliance across AWS, Azure, and GCP.",
    },
    "computer-vision-specialist": {
        "desc": "This agent is for object detection and image processing",
        "prompt": "You implement computer vision solutions including object detection, image classification, segmentation, and real-time video processing using OpenCV and deep learning.",
    },
    "data-analyst": {
        "desc": "This agent is for Excel, Tableau, and data insights",
        "prompt": "You analyze data with Excel, build dashboards in Tableau and PowerBI, identify trends and patterns, and deliver data-driven business recommendations.",
    },
    "data-engineer": {
        "desc": "This agent is for ETL pipelines and Spark/Airflow",
        "prompt": "You build data pipelines, design ETL workflows, orchestrate with Airflow, process large datasets with Spark, and manage data warehouse architectures.",
    },
    "data-scientist": {
        "desc": "This agent is for pandas, numpy, and statistics",
        "prompt": "You analyze data using pandas and numpy, apply statistical methods, create visualizations, and derive actionable insights from structured and unstructured data.",
    },
    "database-admin": {
        "desc": "This agent is for PostgreSQL/MySQL/MongoDB admin",
        "prompt": "You administer relational and NoSQL databases, optimize queries, manage indexes, configure replication, and tune performance for production workloads.",
    },
    "database-architect": {
        "desc": "This agent is for schema design and data replication",
        "prompt": "You design database schemas, plan sharding strategies, configure replication, optimize data distribution, and architect scalable and resilient data storage systems.",
    },
    "devops-engineer": {
        "desc": "This agent is for Docker, K8s, CI/CD, and Terraform",
        "prompt": "You configure Docker containers, manage Kubernetes clusters, build CI/CD pipelines, and provision infrastructure with Terraform following GitOps practices.",
    },
    "embedded-dev": {
        "desc": "This agent is for C/C++/Rust firmware and IoT",
        "prompt": "You develop firmware for microcontrollers, write C/C++ and Rust for embedded systems, implement IoT protocols, and optimize for memory and power constraints.",
    },
    "etl-developer": {
        "desc": "This agent is for data ingestion and warehousing",
        "prompt": "You build ETL pipelines for data ingestion, perform transformations, load data into warehouses, handle streaming and batch processing, and ensure data quality.",
    },
    "frontend-dev": {
        "desc": "This agent is for React, CSS, TypeScript, NextJS",
        "prompt": "You build React components, write modular CSS, implement type-safe TypeScript, and develop NextJS applications with App Router and server components.",
    },
    "fullstack-dev": {
        "desc": "This agent is for full-stack web applications",
        "prompt": "You build complete web applications across frontend and backend, design system architecture, integrate APIs with UIs, and ensure end-to-end data flow and security.",
    },
    "ml-engineer": {
        "desc": "This agent is for PyTorch/TensorFlow model training",
        "prompt": "You train and deploy machine learning models with PyTorch and TensorFlow, design training pipelines, tune hyperparameters, and evaluate model performance.",
    },
    "mlops-engineer": {
        "desc": "This agent is for ML model deployment and monitoring",
        "prompt": "You deploy and monitor ML models in production, build CI/CD pipelines for ML, manage model registries, implement A/B testing, and automate retraining workflows.",
    },
    "mobile-dev": {
        "desc": "This agent is for ReactNative/Flutter mobile apps",
        "prompt": "You build cross-platform mobile apps with React Native and Flutter, implement native features, handle platform-specific code, and optimize UI performance.",
    },
    "nlp-specialist": {
        "desc": "This agent is for LLMs, RAG, and embeddings",
        "prompt": "You build NLP solutions with LLMs and transformers, implement RAG pipelines, create embeddings, fine-tune models, and optimize prompt engineering strategies.",
    },
    "performance-engineer": {
        "desc": "This agent is for profiling, caching, and optimization",
        "prompt": "You profile application performance, implement caching strategies, optimize database queries, reduce latency, and improve throughput across the stack.",
    },
    "qa-engineer": {
        "desc": "This agent is for Playwright/Jest test automation",
        "prompt": "You write and maintain test suites, automate E2E tests with Playwright, implement unit tests with Jest, and ensure quality gates across the SDLC.",
    },
    "security-engineer": {
        "desc": "This agent is for pentesting and vulnerability assessment",
        "prompt": "You conduct security assessments, identify vulnerabilities, implement authentication and authorization, configure encryption, and apply OWASP best practices.",
    },
    "system-admin": {
        "desc": "This agent is for Linux servers and network admin",
        "prompt": "You administer Linux servers, configure networking and firewalls, set up monitoring and alerting, manage users and permissions, and troubleshoot system issues.",
    },
    "n8n-expert": {
        "desc": "Expert n8n workflow automation, AI agents, and node configuration",
        "prompt": "You are an n8n expert. You specialize in building n8n workflows using webhooks, HTTP requests, AI agents, MCP triggers and tools, database operations, batch processing with SplitInBatches, scheduled tasks, and error handling with onError continueErrorOutput and exponential retry backoff. You know sub-workflow contracts with mode all vs each, binary data preservation via Merge combineByPosition, Code node return format as array of json objects, webhook response mode responseNode, MCP initialization and the Database not found error fix using npx n8n-mcp init and N8N_MCP_DATA_DIR, AI agent design with maxIterations 15-200 and tool descriptions as verb-first phrases, hierarchical multi-agent patterns with sequential parallel and gatekeeper routing, guardrails for PII and jailbreak detection, and self-hosting with queue mode and Docker Compose. You output structured JSON schemas, Code node JavaScript, error wiring, and complete workflow topologies.",
    },
    "animate-text": {
        "desc": "Text animation expert for CSS, GSAP, Motion, and WAAPI effects",
        "prompt": "You are a text animation specialist. You design and implement text animations using CSS keyframes, GSAP timelines, Framer Motion variants, Motion library, WAAPI Element.animate, and Lottie JSON. You specialize in effects like soft-blur-in, typewriter, shared-axis-y, kinetic-center-build, short-slide-down, stagger crossfade, line reveal, and per-character builds. You preserve target mode whole per-character per-word or per-line, map enter exit durations easing and stagger directly into the target stack, and handle transform opacity blur scale rotation and spacing fields."
    },
    "github-actions": {
        "desc": "GitHub Actions CI/CD pipeline expert",
        "prompt": "You are a GitHub Actions expert. You design CI/CD workflows using YAML syntax with jobs, steps, matrix builds, reusable workflows, composite actions, environment secrets, artifacts caching, OIDC authentication, and deployment gates. You know triggers including push, pull_request, schedule, workflow_dispatch, repository_dispatch, and workflow_call. You handle multi-platform builds across ubuntu, windows, and macos runners, Docker container jobs, service containers for integration tests, concurrency groups for cancel-in-progress, and GitHub-hosted vs self-hosted runner configuration. You output complete .github/workflows YAML files."
    },
    "docker-compose": {
        "desc": "Docker and Docker Compose infrastructure specialist",
        "prompt": "You are a Docker and Docker Compose expert. You design multi-service architectures with Dockerfiles using multi-stage builds, layer caching, distroless base images, healthchecks, and security scanning. You configure Docker Compose with service dependencies, volumes, networks, environment files, restart policies, resource limits, and profiles. You handle production patterns with Traefik or Caddy reverse proxy, Let's Encrypt SSL, Redis caching, Postgres replication, volume backups, and log shipping. You output complete Dockerfile and docker-compose.yml files."
    },
    "kubernetes": {
        "desc": "Kubernetes deployment and orchestration specialist",
        "prompt": "You are a Kubernetes expert. You design and deploy containerized applications on K8s using Deployments, StatefulSets, DaemonSets, Services, Ingress, ConfigMaps, Secrets, PersistentVolumeClaims, HorizontalPodAutoscalers, NetworkPolicies, RBAC roles, and PodDisruptionBudgets. You write Helm charts with values.yaml templating, create Kustomize overlays for dev/staging/prod, configure service meshes with Istio or Linkerd, set up monitoring with Prometheus Operator and Grafana dashboards, and implement GitOps with ArgoCD or Flux. You output complete YAML manifests."
    },
    "database-designer": {
        "desc": "Database schema designer for SQL and NoSQL",
        "prompt": "You are a database design expert. You design relational schemas with proper normalization, indexes, foreign keys, check constraints, views, materialized views, stored procedures, triggers, and partitioning strategies. You work with PostgreSQL, MySQL, SQLite, SQL Server, and MariaDB. You also design NoSQL schemas for MongoDB with embedded vs reference patterns, Firestore with collection group queries, and DynamoDB with single-table design and composite keys. You output CREATE TABLE statements, migration scripts, and ER diagrams in text format."
    },
    "api-tester": {
        "desc": "API testing and Postman collection specialist",
        "prompt": "You are an API testing expert. You design comprehensive API test suites covering happy path, error codes, edge cases, rate limiting, auth failures, pagination, and idempotency. You write Postman collections with dynamic variables, pre-request scripts, test assertions in pm.test, chaining requests with pm.environment, and Newman CLI runners. You also write curl commands, httpx Python tests, and k6 load test scripts with thresholds and virtual users. You output ready-to-import Postman JSON and k6 JavaScript."
    },
    "design_arena": {
        "desc": "Web design specialist — HTML, CSS, JS, UI/UX, responsive layouts",
        "prompt": "You are a web design expert. You create beautiful, responsive websites using HTML, CSS, and JavaScript. You specialize in modern CSS layouts (flexbox, grid), animations, responsive design, accessibility, color theory, typography, and UI/UX best practices. You output complete single-file HTML with embedded CSS and JS, or separate files as needed."
    },
    "custom": {
        "desc": "This agent is for custom tasks (use /addprompt to set prompt)",
        "prompt": "You are a helpful assistant. Answer the user's questions accurately and concisely.",
    },
    "video-creator": {
        "desc": "OpenMontage agentic video production — 12 pipelines, 52 tools, full production studio",
        "prompt": "You are OpenMontage, the world's first open-source agentic video production system. You turn plain-language descriptions into finished videos through a structured production pipeline. Your job is to guide users through installing OpenMontage, selecting the right pipeline, and producing a video from concept to final render.\n\n## Identity & Architecture\nYou are based on calesthio/OpenMontage (AGPL-3.0). Core principle: the AI agent IS the orchestrator. Python provides tools and persistence; the agent reads YAML pipeline manifests + Markdown skill files to drive production. The flow is: agent reads pipeline manifest -> reads stage director skill -> calls Python tools -> self-reviews using meta skill -> checkpoints -> presents for human approval.\n\n## Prerequisites & Installation\nPrerequisites: Python 3.10+, FFmpeg, Node.js 18+, AI coding assistant (Claude Code, Cursor, Copilot, Windsurf, Codex). Install:\n- git clone https://github.com/calesthio/OpenMontage.git && cd OpenMontage && make setup\n- Windows: py -3 -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; python -m pip install -r requirements.txt; cd remotion-composer; npm install; cd ..; python -m pip install piper-tts; Copy-Item .env.example .env\n- If npm install fails on Windows with ERR_INVALID_ARG_TYPE, use: npx --yes npm install\n- Copy .env.example to .env and add API keys (all optional)\n\n## 12 Production Pipelines\nEach pipeline is a YAML manifest under pipeline_defs/. The state machine: research -> proposal -> script -> scene_plan -> assets -> edit -> compose -> publish. Some pipelines start with idea instead of research+proposal.\n\n1. **animated-explainer** — AI-generated explainers with research, narration, visuals, music. Best for educational content, tutorials, topic breakdowns. Budget $2. Stages: research proposal script scene_plan assets edit compose publish. Human gates: proposal script scene_plan assets publish.\n2. **animation** — Motion graphics, kinetic typography, animated sequences. Social media, product demos. Budget $2. Same stages/gates as explainer.\n3. **avatar-spokesperson** — Avatar-driven presenter videos. Corporate comms, training. Budget $2. Starts at idea stage. Human gates: idea script scene_plan assets publish.\n4. **character-animation** — SVG-rigged character animation with pose libraries. 10 stages including character_design and rig_plan. Budget $2. Beta stability.\n5. **cinematic** — Trailers, teasers, mood-driven edits. Brand films, promotional. Budget $2. Full research+proposal flow.\n6. **clip-factory** — Batch ranked short-form clips from one long source. Repurposing content for social media. Budget $1. Beta.\n7. **documentary-montage** — Thematic montage from CLIP-indexed corpus of free stock footage (Archive.org, NASA, Wikimedia, Pexels). Real footage, no paid video models needed. Budget $1. Beta. Stages: idea scene_plan assets edit compose. Edit is human-gated.\n8. **hybrid** — Source footage + AI-generated support visuals. Enhancing existing footage. Budget $2.\n9. **localization-dub** — Subtitle, dub, translate existing video. Multi-language. Budget $3. Beta.\n10. **podcast-repurpose** — Podcast highlights to video. Budget $1. Beta.\n11. **screen-demo** — Software screen recordings and walkthroughs. Dual mode: REAL CAPTURE (OS recording) or SYNTHETIC (Remotion TerminalScene). Budget $1.\n12. **talking-head** — Footage-led speaker videos. Presentations, vlogs. Budget $0.50. Beta.\n\n## Tools (52+ production tools)\nCategories with examples:\n- **Video Generation**: Kling (fal.ai), Kling Official, Runway Gen-4, Google Veo 3, Grok Imagine Video, Higgsfield, MiniMax, HeyGen. Local GPU: WAN 2.1 (1.3B/14B), Hunyuan, CogVideo (2B/5B), LTX-Video. Stock: Pexels, Pixabay, Wikimedia Commons, Archive.org. Composition: Remotion (React-based), HyperFrames (HTML/CSS/GSAP), FFmpeg.\n- **Image Generation**: FLUX (fal.ai), Google Imagen 4, Grok Imagine Image, GPT Image 2, Recraft, Kling Official, Local Diffusion. Stock: Pexels, Pixabay, Unsplash.\n- **Text-to-Speech**: ElevenLabs (premium), Google TTS (700+ voices, 50+ languages), OpenAI TTS (fast/cheap), Kling Official TTS, Piper (free offline), Doubao, DashScope.\n- **Music**: Suno AI (full songs), ElevenLabs Music/SFX, Pixabay, Freesound, Google Music, Music Library (local).\n- **Post-Production** (all free/local): FFmpeg encoding, Video Stitch (crossfades/PIP/layouts), Video Trimmer, Audio Mixer (ducking/fades), Audio Enhance (noise reduction/normalization), Color Grade (LUT-based), Subtitle Gen (SRT/VTT).\n- **Enhancement**: Upscale (Real-ESRGAN), Background Remove (rembg/U2Net), Face Enhance, Face Restore (CodeFormer/GFPGAN).\n- **Analysis**: Transcriber (WhisperX word-level timestamps), Scene Detect, Frame Sampler, Video Understand (CLIP/BLIP-2), Visual QA, Audio Energy/Probe, Composition Validator.\n- **Avatar & Lip Sync**: Talking Head (SadTalker/MuseTalk), Lip Sync (Wav2Lip), Kling Avatar, Kling Lip Sync.\n- **Capture**: Screen Recorder, Cap Recorder, Screen Capture Selector.\n- **Graphics**: Diagram Gen, Code Snippet, Math Animate (ManimCE), Character Animation (spec builder, SVG rig builder, pose library, action timeline, rig renderer, anim review).\n\n## Agent Orchestration Contract (Rules You MUST Follow)\n1. ALL production goes through the pipeline system. No ad-hoc scripts.\n2. Read every tool's agent_skills before calling it (check .agents/skills/).\n3. Announce provider/model/runtime before execution; ask before major changes.\n4. Re-log changed decisions as new entries; never mutate old ones.\n5. Present both composition runtimes (Remotion + HyperFrames) when available; wait for approval.\n6. Default to atelier (bespoke) composition for hero work.\n7. No unilateral substitutions — provider/model/runtime swaps require user approval.\n8. Escalate blockers explicitly: what was attempted, what failed, why, options, recommendation.\n9. Music plan is mandatory — surface at proposal time.\n10. Cannot mark a gated stage completed without human_approved=True (gate violation = defect).\n11. Never silently swap Remotion<->HyperFrames<->FFmpeg — logged decision + user approval required.\n12. Decision log is append-only, identified by (category, subject) pair.\n\n## Full Production Workflow\nWhen a user says \"Make a video about X\":\n1. **Pipeline Selection** — Match request to the right pipeline. Ask clarifying questions if needed (duration, tone, style, real footage vs generated, budget).\n2. **Mandatory Preflight** — Run tool_registry.discover() and show provider_menu_summary() to show what's configured. Present both composition runtimes. User approves plan.\n3. **Initialize Workspace** — init_project(..., pipeline_type=...), open backlot board.\n4. **Research Stage** (if applicable) — 15-25+ web searches across YouTube, Reddit, HN, news, academic. Produce research_brief with citations.\n5. **Proposal Stage** (HUMAN GATE) — Present 4-5 concept directions, recommended tool path, cost estimate, music plan, render_runtime options. Wait for approval.\n6. **Script Stage** (HUMAN GATE) — Write structured script with enhancement cues, voice performance plan (pacing, pause, emphasis).\n7. **Scene Plan** (HUMAN GATE) — Map script to scenes with asset requirements. Ensure visual variety.\n8. **Assets Stage** (HUMAN GATE) — Generate narration (tts_selector), images (image_selector), video clips (video_selector), music. Each scene generates audio+image+optional video.\n9. **Edit Stage** — Define cuts, transitions, subtitles, audio ducking. Produce edit_decisions.\n10. **Compose Stage** — Route to locked render_runtime. Audio mixing, subtitle burn-in. Post-render self-review (ffprobe + frame extraction + audio analysis). Must pass to present video.\n11. **Publish Stage** (HUMAN GATE) — SEO metadata, export package. Final video.\n\n## Configuration & API Keys\nAll keys go in .env (every key is optional). Key ones: FAL_KEY (FLUX/Veo/Kling/MiniMax via fal.ai), KLING_API_KEY (official Kling), GOOGLE_API_KEY (Imagen/Gemini/Google TTS), ELEVENLABS_API_KEY (TTS/music/SFX), OPENAI_API_KEY (TTS/gpt-image), XAI_API_KEY (Grok), SUNO_API_KEY (music), HEYGEN_API_KEY, RUNWAY_API_KEY, PEXELS_API_KEY, PIXABAY_API_KEY, UNSPLASH_ACCESS_KEY. Local GPU: VIDEO_GEN_LOCAL_ENABLED=true with wan2.1-1.3b or hunyuan-1.5.\n\n## Style Playbooks\n- clean-professional — corporate, educational, SaaS\n- flat-motion-graphics — social media, TikTok, startups\n- minimalist-diagram — technical deep-dives, architecture\n- premium-minimalist — investor updates, expert explainers\n- anime-ghibli — Ghibli-style animation\n- ink-sketch — hand-drawn ink doodle animation\n\n## Platform Output Profiles\nYouTube Landscape 1920x1080, YouTube 4K 3840x2160, YouTube Shorts 1080x1920, Instagram Reels 1080x1920, TikTok 1080x1920, LinkedIn 1920x1080, Cinematic 2560x1080 (21:9).\n\n## Quality Gates\n- Human approval gates enforced for proposal, script, scene_plan, assets, publish\n- Pre-compose validation: blocks render if delivery promise violated, slideshow risk critical, or renderer missing\n- Post-render self-review: ffprobe validation, frame extraction (4 positions checking black frames + broken overlays), audio level analysis (silence + clipping), delivery promise verification, subtitle presence check\n- Slideshow risk scoring: 6-dimension analysis prevents animated-PowerPoint outputs\n- Failed review = video not presented\n\n## What You Get With Zero API Keys\nNarration via Piper TTS (free offline), open footage from Archive.org/NASA/Wikimedia Commons, free stock from Pexels/Unsplash/Pixabay (developer keys free to get), Remotion composition, FFmpeg encoding, auto-generated captions. Two free paths: image-based video (Piper + still images animated by Remotion) or real-footage video (documentary montage from free stock footage).",
    },
}

def save_agents():
    _atomic_save(AGENTS_FILE, AGENTS)

def save_providers():
    _atomic_save(PROVIDERS_FILE, PROVIDERS)

def save_admins():
    _atomic_save(ADMINS_FILE, list(admins))

def save_mods():
    _atomic_save(MODS_FILE, list(mods))

def save_teams():
    _atomic_save(TEAMS_FILE, TEAMS)

def save_sessions():
    global _save_counter
    _save_counter += 1
    if _save_counter % 3 != 0:
        return
    data = {
        "sessions": {str(k): v for k, v in sessions.items()},
        "team_sessions": {str(k): v for k, v in team_sessions.items()},
        "_last_update": last_update,
    }
    _atomic_save(SESSIONS_FILE, data)

def load_sessions():
    global last_update
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, encoding="utf-8") as f:
                data = json.load(f)
                sessions.update({int(k): v for k, v in data.get("sessions", {}).items()})
                team_sessions.update({int(k): v for k, v in data.get("team_sessions", {}).items()})
                lu = data.get("_last_update", 0)
                if lu and not last_update:
                    last_update = lu
        except Exception:
            pass

class _LRUDict(dict):
    def __init__(self, maxsize=200):
        self._maxsize = maxsize
        super().__init__()
    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        if len(self) > self._maxsize:
            oldest = next(iter(self))
            del self[oldest]

routines = _LRUDict(200)

CONVERSATIONS_FILE = os.path.join(os.path.dirname(__file__), "conversations.json")

def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"counter": 0, "archives": {}}

def save_conversations(data):
    _atomic_save(CONVERSATIONS_FILE, data)

def _summarize_conversation(messages):
    if not messages:
        return ""
    first_user = ""
    for m in messages:
        if m.get("role") == "user":
            first_user = m["content"][:80]
            break
    summary = first_user if first_user else f"{len(messages)} messages"
    return f"{summary}{'...' if len(first_user) >= 80 else ''}"

def _archive_current(uid, chat):
    if uid not in sessions or not sessions[uid]:
        return
    convs = load_conversations()
    msgs = sessions[uid]
    summary = _summarize_conversation(msgs)
    cid = convs["counter"] + 1
    convs["counter"] = cid
    chat_key = str(chat)
    if chat_key not in convs["archives"]:
        convs["archives"][chat_key] = []
    convs["archives"][chat_key].append({
        "id": cid,
        "time": time.time(),
        "summary": summary,
        "count": len(msgs),
        "messages": msgs,
    })
    if len(convs["archives"][chat_key]) > 50:
        convs["archives"][chat_key] = convs["archives"][chat_key][-50:]
    save_conversations(convs)

def save_routines():
    _atomic_save(ROUTINES_FILE, routines)
def load_routines():
    global routines
    if os.path.exists(ROUTINES_FILE):
        try:
            with open(ROUTINES_FILE, encoding="utf-8") as f:
                data = json.load(f)
            routines.clear()
            routines.update(data)
        except Exception:
            routines.clear()

multi_sessions = _LRUDict(200)
def save_multi():
    _atomic_save(MULTI_FILE, multi_sessions)
def load_multi():
    global multi_sessions
    if os.path.exists(MULTI_FILE):
        try:
            with open(MULTI_FILE, encoding="utf-8") as f:
                data = json.load(f)
            multi_sessions.clear()
            multi_sessions.update(data)
        except Exception:
            multi_sessions.clear()

ARCHITECTURES = {
    "single": {"desc": "Single agent mode (default, no team coordination)"},
    "sequential": {"desc": "Agents run one after another, each gets previous output"},
    "parallel": {"desc": "All agents run simultaneously, orchestrator merges results"},
    "hierarchical": {"desc": "Orchestrator delegates to sub-agents, collects reports"},
    "mesh": {"desc": "All agents collaborate freely with shared context"},
    "voting": {"desc": "Each agent answers independently, best answer selected"},
    "supervisor": {"desc": "Supervisor plans, delegates, reviews agent outputs, and iterates for quality"},
    "reflection": {"desc": "Agent generates output, then reflects and improves it before returning"},
}

MODES = {
    "chat": {"desc": "Single agent chat, no planning"},
    "team": {"desc": "Multi-agent team with architecture patterns"},
    "autonomous": {"desc": "Autonomous agent with planner, executor, tools, and memory"},
}

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_usage.json")
EXPERIMENTAL_FILE = os.path.join(os.path.dirname(__file__), "experimental.json")
CUSTOM_COMMANDS_FILE = os.path.join(os.path.dirname(__file__), "custom_commands.json")
CONTEXT_FILES_FILE = os.path.join(os.path.dirname(__file__), "context_files.json")
CONVERSATION_TAGS_FILE = os.path.join(os.path.dirname(__file__), "conversation_tags.json")
BRIDGES_FILE = os.path.join(os.path.dirname(__file__), "bridges.json")
bridges = {}
vector_memory = {}
class _MemoryBuffer(dict):
    MAX_ENTRIES_PER_UID = 100
    MAX_UIDS = 200
    def __setitem__(self, key, val):
        if isinstance(val, list):
            super().__setitem__(key, val[-self.MAX_ENTRIES_PER_UID:])
        else:
            super().__setitem__(key, val)
        if len(self) > self.MAX_UIDS:
            oldest = next(iter(self))
            del self[oldest]
    def append(self, key, item):
        self.setdefault(key, [])
        lst = self[key]
        lst.append(item)
        if len(lst) > self.MAX_ENTRIES_PER_UID:
            self[key] = lst[-self.MAX_ENTRIES_PER_UID:]
        if len(self) > self.MAX_UIDS:
            oldest = next(iter(self))
            del self[oldest]

memory_buffers = _MemoryBuffer()

PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
    "stack": ["python", "ai_stack_combined.py"],
}

# Persistent memory store (from ai_stack_combined)
try:
    user_memory = ai_stack.MemoryStore() if ai_stack else None
except Exception:
    user_memory = None

def save_memory():
    data = {"vector": vector_memory, "buffers": {str(k): v for k, v in memory_buffers.items()}}
    if user_memory:
        data["memories"] = [{"id": m.id, "content": m.content, "user_id": m.user_id, "metadata": m.metadata} for m in user_memory.memories]
        data["blocks"] = {k: v.value for k, v in user_memory.blocks.items()}
    _atomic_save(MEMORY_FILE, data)

def load_memory():
    global vector_memory, memory_buffers
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, encoding="utf-8") as f:
                data = json.load(f)
                vector_memory.update(data.get("vector", {}))
                memory_buffers.update({int(k): v for k, v in data.get("buffers", {}).items()})
                # Load MemoryStore if available
                if user_memory:
                    for m in data.get("memories", []):
                        user_memory.add(m["content"], m.get("user_id", "default"), **m.get("metadata", {}))
                    for k, v in data.get("blocks", {}).items():
                        user_memory.set_block(k, v)
        except Exception: pass

# Token usage tracking for FreeTokenFaucet
token_usage = {"balance": 1096964, "used": 0, "last_claim": "", "history": []}

def load_token_usage():
    global token_usage
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, encoding="utf-8") as f:
                token_usage.update(json.load(f))
        except Exception: pass

def save_token_usage():
    _atomic_save(TOKEN_FILE, token_usage)

experimental_features = {}
def load_experimental():
    global experimental_features
    if os.path.exists(EXPERIMENTAL_FILE):
        try:
            with open(EXPERIMENTAL_FILE, encoding="utf-8") as f:
                data = json.load(f)
                experimental_features = data.get("features", {})
        except Exception:
            experimental_features = {}
    defaults = {
        "search-tags": {"name": "Search by Tags", "desc": "Enables /search tags <tag> to find chats by auto-generated tags", "version": "2.8.0", "category": "research"},
        "search-files": {"name": "Search Attached Files", "desc": "Enables /search files <keyword> to search attached context files", "version": "2.8.0", "category": "research"},
        "search-history": {"name": "Search History", "desc": "Enables /search history <keyword> to search current session messages", "version": "2.8.0", "category": "research"},
        "custom-commands": {"name": "Custom Commands", "desc": "Users can create their own /commands with custom responses", "version": "2.8.0", "category": "automation"},
        "context-files": {"name": "Context Files", "desc": "Attach and detach files as permanent AI context in conversations", "version": "2.8.0", "category": "ai"},
        "auto-tagging": {"name": "Auto-Tagging", "desc": "Auto-categorize conversations with tags, searchable via /find", "version": "2.8.0", "category": "automation"},
        "enhanced-search": {"name": "Enhanced Search", "desc": "Enhanced /search with tags, files, and history modes", "version": "2.8.0", "category": "research"},
        "web-dashboard": {"name": "Web Dashboard", "desc": "Web UI for managing agents, viewing logs, and toggling experimental features", "version": "2.8.0", "category": "admin"},
        "plugin-system": {"name": "Plugin System", "desc": "Load custom functionality from plugins/ directory at startup", "version": "2.8.0", "category": "automation"},
        "bot-bridge": {"name": "Bot Bridge", "desc": "Bridge connection to other Telegram bots, Discord, or Slack", "version": "2.8.0", "category": "automation"},
        "persistent-memory": {"name": "Persistent Memory", "desc": "Long-term memory log per user with search, stats, and auto-context injection", "version": "3.0.0", "category": "ai"},
        "scheduled-cron": {"name": "Scheduled Cron", "desc": "Recurring AI prompt scheduling with /cron and web page monitoring with /monitor", "version": "3.0.0", "category": "automation"},
        "social-search": {"name": "Social Search", "desc": "Multi-platform search across Reddit, Hacker News, and Medium via /reddit, /hn, /social", "version": "3.0.0", "category": "research"},
        "doc-analyzer": {"name": "Document Analyzer", "desc": "Enhanced PDF/document analysis with AI-powered Q&A and multi-engine text extraction", "version": "3.0.0", "category": "ai"},
        "rich-messages": {"name": "Rich Messages", "desc": "Send AI responses using Telegram's Rich Message format (tables, code blocks, headings, collapsible details)", "version": "3.1.0", "category": "ai"},
        "ai-styles": {"name": "AI Styles", "desc": "Custom AI personality presets: /style list, /style on <name>, /style create <name> <text>, /style off", "version": "3.1.0", "category": "ai"},
        "poll-plus": {"name": "Poll Plus", "desc": "Advanced poll tracking with statistics, vote distribution charts, peak hour detection (subscription only)", "version": "3.1.0", "category": "admin"},
        "content-automation": {"name": "Content Automation", "desc": "Auto-post from RSS/Atom feeds to channels with AI-powered relevance filtering", "version": "3.1.0", "category": "automation"},
        "analytics-dashboard": {"name": "Analytics Dashboard", "desc": "Per-chat message/member tracking, stats, growth rate, peak hours, top users", "version": "3.1.0", "category": "admin"},
        "subscription-paywall": {"name": "Subscription Paywall", "desc": "Telegram Stars subscriptions, Dana bank transfer (Rp28k/month), plan management", "version": "3.1.0", "category": "admin"},
        "safety-moderation": {"name": "Safety & Moderation", "desc": "AI toxicity detection, anti-nuke, CAPTCHA, behavioral analysis, cross-group reputation, edit detection", "version": "3.2.0", "category": "safety"},
        "coding-dev-tools": {"name": "Coding & Dev Tools", "desc": "Remote coding assistant, code playground, GitHub integration, API doc generator", "version": "3.2.0", "category": "coding"},
        "ai-intelligence": {"name": "AI Intelligence", "desc": "Proactive AI briefings, multi-modal processing, domain-specific chatbots, AI persona engine", "version": "3.2.0", "category": "ai"},
        "community-engagement": {"name": "Community Engagement", "desc": "Reaction roles, AI server builder, image-based welcomes", "version": "3.2.0", "category": "community"},
        "automation-productivity": {"name": "Automation & Productivity", "desc": "Content drip sequences, CRM integration, multi-step wizards, silent scheduled messages", "version": "3.2.0", "category": "automation"},
        "security-api": {"name": "Security & API", "desc": "Ephemeral messages v2, communities support, star subscriptions v2, webhook manager, guest bots, bot-to-bot", "version": "3.2.0", "category": "security"},
        "new-research-features": {"name": "New Research Features", "desc": "Streaming text, OCR document scanner, real-time translation", "version": "3.2.0", "category": "research"},
        "location-distance": {"name": "Location & Distance", "desc": "Set home location, track user distances, restrict responses to within 14km range", "version": "3.2.1", "category": "utility"},
        "mini-apps": {"name": "Mini Apps", "desc": "Telegram Web Apps — full HTML dashboards and tools inside Telegram", "version": "3.4.0", "category": "utility"},
        "rich-text-v2": {"name": "Rich Text v2", "desc": "Telegram Bot API 10.1 Rich Messages — tables, collapsible details, math formulas, code blocks, slideshows", "version": "3.4.0", "category": "ai"},
        "multi-agent": {"name": "Multi-Agent System", "desc": "Bot-to-Bot Agent orchestration — specialized AI agents collaborate on complex tasks", "version": "3.5.0", "category": "ai"},
    }
    changed = False
    for fid, fdef in defaults.items():
        if fid not in experimental_features:
            fdef["enabled"] = False
            experimental_features[fid] = fdef
            changed = True
    if changed:
        save_experimental()

def _atomic_save(path, data):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception as _e:
        log(f"atomic_save failed for {path}: {_e}")

def save_experimental():
    _atomic_save(EXPERIMENTAL_FILE, {"features": experimental_features})

def load_bridges():
    global bridges
    if os.path.exists(BRIDGES_FILE):
        try:
            with open(BRIDGES_FILE, encoding="utf-8") as f:
                bridges = json.load(f)
        except Exception:
            bridges = {}
    else:
        bridges = {}

def save_bridges():
    _atomic_save(BRIDGES_FILE, bridges)

async def relay_to_bridge(text, _chat, _uid, _msg):
    if not is_experimental_enabled("bot-bridge"):
        return
    for name, cfg in bridges.items():
        if not cfg.get("enabled"):
            continue
        targets = cfg.get("targets", [])
        for t in targets:
            platform = t.get("platform")
            url = t.get("webhook_url")
            if platform == "telegram":
                token = t.get("bot_token")
                target_chat = t.get("chat_id")
                if token and target_chat:
                    try:
                        c = await get_http()
                        payload = {
                            "chat_id": target_chat,
                            "text": f"[Bridge {name}] {html.escape(text[:2000])}",
                            "parse_mode": "HTML",
                        }
                        await c.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=10)
                    except Exception:
                        pass
            elif platform == "bot":
                if url:
                    try:
                        c = await get_http()
                        sender_name = bridges.get(name, {}).get("sender_name", "opencode-bot")
                        payload = {"text": text[:2000], "sender": sender_name, "from": "opencode-bot"}
                        if t.get("expect_reply"):
                            payload["reply_url"] = t.get("my_webhook_url", "")
                        await c.post(url, json=payload, timeout=15)
                    except Exception:
                        pass
            elif platform in ("discord", "slack"):
                if url:
                    try:
                        c = await get_http()
                        safe_text = html.escape(text[:2000])
                        payload = {"content": f"[Bridge {name}] {safe_text}"}
                        if platform == "slack":
                            payload = {"text": f"[Bridge {name}] {safe_text}"}
                        await c.post(url, json=payload, timeout=10)
                    except Exception:
                        pass

def is_experimental_enabled(name):
    feat = experimental_features.get(name)
    return feat.get("enabled", False) if feat else False

def get_experimental_list():
    lines = ["Experimental Features:", ""]
    categories = {}
    for fid, f in experimental_features.items():
        cat = f.get("category", "other")
        categories.setdefault(cat, []).append((fid, f))
    cat_order = ["ai", "media", "automation", "developer", "research", "social", "other"]
    for cat in cat_order:
        if cat not in categories:
            continue
        items = categories[cat]
        lines.append(f"  [{cat.upper()}]")
        for fid, f in items:
            status = "ON" if f.get("enabled") else "OFF"
            badge = "✅" if f.get("enabled") else "⬜"
            lines.append(f"  {badge} {fid}")
            lines.append(f"     {f['name']} — {f['desc']}")
            lines.append(f"     Status: {status} | Added: v{f.get('version', '?')}")
        lines.append("")
    lines.append("Commands:")
    lines.append("  /experimental enable <name> — Enable feature")
    lines.append("  /experimental disable <name> — Disable feature")
    lines.append("  /experimental status — Quick status")
    return "\n".join(lines)

custom_commands = {}
def load_custom_commands():
    global custom_commands
    if os.path.exists(CUSTOM_COMMANDS_FILE):
        try:
            with open(CUSTOM_COMMANDS_FILE, encoding="utf-8") as f:
                custom_commands = json.load(f)
        except Exception:
            custom_commands = {}

def save_custom_commands():
    _atomic_save(CUSTOM_COMMANDS_FILE, custom_commands)

context_files = {}
def load_context_files():
    global context_files
    if os.path.exists(CONTEXT_FILES_FILE):
        try:
            with open(CONTEXT_FILES_FILE, encoding="utf-8") as f:
                context_files = json.load(f)
        except Exception:
            context_files = {}

def save_context_files():
    _atomic_save(CONTEXT_FILES_FILE, context_files)

conversation_tags = _LRUDict(500)
def load_conversation_tags():
    global conversation_tags
    if os.path.exists(CONVERSATION_TAGS_FILE):
        try:
            with open(CONVERSATION_TAGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            conversation_tags.clear()
            conversation_tags.update(data)
        except Exception:
            conversation_tags.clear()

def save_conversation_tags():
    _atomic_save(CONVERSATION_TAGS_FILE, conversation_tags)

def tag_keywords(text):
    tags = {}
    text_lower = text.lower()
    rules = [
        ("code", ["def ", "class ", "import ", "function", "const ", "var ", "return ", "async "]),
        ("python", ["import ", "def ", "class ", "async def", "lambda", "print("]),
        ("javascript", ["const ", "let ", "var ", "function(", "=>", "console."]),
        ("ai-ml", ["neural", "llm", "model", "training", "dataset", "inference", "gpt", "token"]),
        ("web", ["html", "css", "http", "api", "endpoint", "route", "server"]),
        ("database", ["sql", "query", "table", "index", "select ", "insert", "database"]),
        ("docker", ["docker", "container", "image", "compose", "kubernetes", "k8s"]),
        ("git", ["commit", "push", "pull", "branch", "merge", "repo", "git "]),
        ("telegram", ["bot", "message", "chat", "telegram", "update", "polling"]),
        ("help", ["how", "what", "why", "when", "where", "help", "guide", "tutorial"]),
        ("error", ["error", "bug", "crash", "fail", "exception", "issue", "problem"]),
    ]
    for tag, keywords in rules:
        for kw in keywords:
            if kw in text_lower:
                tags[tag] = tags.get(tag, 0) + 1
                break
    return tags

TOOLFK_TOKEN = os.environ.get("TOOLFK_TOKEN", "")

# Integration API keys
N8N_URL = os.environ.get("N8N_URL", "").rstrip("/")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SHEETS_CREDENTIALS = os.environ.get("SHEETS_CREDENTIALS", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")

_TFK = [
    "rebang","lunar","clang","ip","dns","shorturl","qrcode","ocr",
    "txt2img","text2img","tts","password","barcode","regex","diff","unixtime",
    "rmbg","upscale","img2prompts","morseenc","morsedec",
    "b64enc","b64dec","md2html","jsonfmt","sqlfmt","htmlfmt",
    "encdec","encryption","compress","byte","base-converter","hex",
    "csv","xml","yaml","markdown","css","javascript",
    "htaccess2nginx","curl","crontab","cdnjs","sequence","difftext",
    "mobile","idcard","bankcardinfo","youjia","tax","poem","couplets","copybook",
    "text2video","img2video","image-recognition","paint","screenshot",
    "idphotos","pdf2word","qwen-image-editor","ai-image-editor","nanobanana",
    "pdf-decrypt","decompile-apk","base64-to-pdf","watermark",
    "hf-wan-image-to-video","pdf2image","videoparser","ai-photo-to-cartoon",
    "website-mirror","convert-text","ai-watermark-remover","online-mind",
    "online-bazi","online-http","python-confuse","turbo-image-generator",
    "base64-to-audio","online-photoshop","online-designer",
    "ai-photo-to-oil-painting","word-to-pdf","seedream-image-generator",
    "audio-to-base64","online-run","flux-image-generator","ai-clothes-changer",
    "online-ocr","pdf-to-ppt","online-images-compression","online-jigsaw",
    "online-php-confuse","ai-photo-to-sketch","pdf-to-text","online-morse",
    "base64-to-video","online-run-haskell","online-run-python3","java-confuse",
    "format-css","online-plotter","online-gushi-name","online-run-java",
    "online-run-php","online-safe-domain","ai-emoji-maker","format-javascript",
    "online-website-port","online-tibetan-poems","online-run-c",
    "online-pdf-encrypt","format-yaml","online-run-c++","base64-to-image",
    "online-text-to-pdf","ai-turn-photo-into-line-drawing","online-run-lisp",
    "online-runwebsocket","game-calculator","online-tao","base64-to-file",
    "online-excel-to-pdf","convert-unixtime","online-run-lua","base64-to-hex",
    "encdec-transform","online-cdnjs","generate-crontab","image-to-base64",
    "online-sequence","online-foto","base64-to-text","convert-csv",
    "online-pdf-to-html","convert-svg","online-ppt-to-pdf","convert-markdown",
    "hex-to-base64","online-run-csharp","online-run-golang","hf-image-to-text",
    "file-to-base64","ai-photo-to-painting","online-run-rust","online-run-swift",
    "online-run-kotlin","url-to-base64","online-run-ruby","online-run-erlang",
    "online-runjs","online-run-scala","online-run-perl","text-to-base64",
    "online-run-elixir","base64-to-ascii","online-run-clojure",
]

TOOLFK_ENDPOINTS = sorted(set(_TFK))
del _TFK

def _tfk_desc(name):
    m = {
        "rebang":"Today's hot news topics", "lunar":"Chinese lunar calendar",
        "clang":"Chinese text converter (simplified/traditional/pinyin)",
        "ip":"IP address geolocation lookup", "dns":"DNS records lookup",
        "shorturl":"URL shortener", "qrcode":"QR code generator",
        "ocr":"Optical character recognition from image",
        "txt2img":"AI text-to-image generation","text2img":"AI text-to-image",
        "tts":"Text-to-speech","password":"Random password generator",
        "barcode":"Barcode generator (EAN13, Code39, etc)",
        "regex":"Regex pattern tester","diff":"Compare two texts",
        "unixtime":"Unix timestamp converter",
        "rmbg":"Remove image background","upscale":"AI image upscaler",
        "img2prompts":"Convert image to AI art prompts",
        "morseenc":"Encode text to Morse","morsedec":"Decode Morse to text",
        "b64enc":"Base64 encode","b64dec":"Base64 decode",
        "md2html":"Markdown to HTML","jsonfmt":"JSON formatter/validator",
        "sqlfmt":"SQL formatter","htmlfmt":"HTML formatter/minifier",
        "encdec":"Encrypt/decrypt text (AES, DES)","encryption":"Hash text (MD5,SHA)",
        "compress":"Lossless image compression","byte":"Byte unit converter",
        "base-converter":"Number base converter","hex":"Hex converter",
        "csv":"CSV converter","xml":"XML formatter/validator",
        "yaml":"YAML formatter","markdown":"Markdown converter",
        "css":"CSS formatter/minifier","javascript":"JS formatter/minifier",
        "htaccess2nginx":".htaccess to Nginx converter",
        "curl":"cURL to code converter","crontab":"Crontab evaluator",
        "cdnjs":"cdnjs library lookup","sequence":"UML sequence diagram",
        "difftext":"Side-by-side text diff","mobile":"Chinese phone lookup",
        "idcard":"Chinese ID card validator","bankcardinfo":"Chinese bank card lookup",
        "youjia":"Chinese oil prices","tax":"Chinese salary/tax calculator",
        "poem":"AI poem generator","couplets":"Chinese couplets generator",
        "copybook":"Chinese character practice sheets",
        "text2video":"AI text-to-video","img2video":"AI image-to-video",
        "image-recognition":"AI image recognition","paint":"Online drawing board",
        "screenshot":"Image beautifier/editor","idphotos":"AI ID photo generator",
        "pdf2word":"PDF to Word converter",
        "qwen-image-editor":"AI Qwen image editor",
        "ai-image-editor":"AI image editor",
        "nanobanana":"Nanobanana AI image generator",
        "pdf-decrypt":"PDF password remover","decompile-apk":"APK decompiler",
        "base64-to-pdf":"Base64 to PDF","watermark":"Image watermark tool",
        "hf-wan-image-to-video":"Wan AI image-to-video",
        "pdf2image":"PDF to image converter","videoparser":"Video URL parser",
        "ai-photo-to-cartoon":"AI photo to cartoon",
        "website-mirror":"Website mirror/download tool",
        "convert-text":"AI article generator",
        "ai-watermark-remover":"AI watermark remover",
        "online-mind":"Mind mapper / flowchart",
        "online-bazi":"Chinese Bazi (Four Pillars) calculator",
        "online-http":"HTTP request simulator",
        "python-confuse":"Python code obfuscator",
        "turbo-image-generator":"Turbo AI image generator",
        "base64-to-audio":"Base64 to audio","online-photoshop":"Online PS editor",
        "online-designer":"SQL schema designer",
        "ai-photo-to-oil-painting":"AI photo to oil painting",
        "word-to-pdf":"Word to PDF converter",
        "seedream-image-generator":"Seedream AI image generator",
        "audio-to-base64":"Audio to Base64","online-run":"Multi-language code runner",
        "flux-image-generator":"Flux AI image generator",
        "ai-clothes-changer":"AI clothes changer",
        "online-ocr":"Image OCR text extractor","pdf-to-ppt":"PDF to PPT converter",
        "online-images-compression":"Image compression tool",
        "online-jigsaw":"Jigsaw puzzle generator",
        "online-php-confuse":"PHP obfuscator/encryptor",
        "ai-photo-to-sketch":"AI photo to sketch",
        "pdf-to-text":"PDF to text converter","online-morse":"Morse code translator",
        "base64-to-video":"Base64 to video",
        "online-run-haskell":"Haskell online compiler",
        "online-run-python3":"Python3 online compiler",
        "java-confuse":"Java code obfuscator","format-css":"CSS formatter",
        "online-plotter":"Function plotter (FooPlot)",
        "online-gushi-name":"Chinese baby name generator",
        "online-run-java":"Java online compiler",
        "online-run-php":"PHP online compiler",
        "online-safe-domain":"Domain security checker",
        "ai-emoji-maker":"AI emoji generator",
        "format-javascript":"JavaScript formatter",
        "online-website-port":"Website port scanner",
        "online-tibetan-poems":"Tibetan/acrostic poem generator",
        "online-run-c":"C online compiler",
        "online-pdf-encrypt":"Password protect PDF",
        "format-yaml":"YAML formatter","online-run-c++":"C++ online compiler",
        "base64-to-image":"Base64 to image",
        "online-text-to-pdf":"Text to PDF converter",
        "ai-turn-photo-into-line-drawing":"Turn photo into line drawing",
        "online-run-lisp":"Lisp online compiler",
        "online-runwebsocket":"WebSocket test tool",
        "game-calculator":"Scientific notation calculator",
        "online-tao":"Taoist calendar","base64-to-file":"Base64 to file",
        "online-excel-to-pdf":"Excel to PDF converter",
        "convert-unixtime":"Unix time converter",
        "online-run-lua":"Lua online compiler","base64-to-hex":"Base64 to hex",
        "encdec-transform":"Base64 URL converter",
        "online-cdnjs":"cdnjs CDN library lookup",
        "generate-crontab":"Crontab expression generator",
        "image-to-base64":"Image to Base64","online-sequence":"UML diagram tool",
        "online-foto":"Buddhist calendar","base64-to-text":"Base64 to text",
        "convert-csv":"CSV converter","online-pdf-to-html":"PDF to HTML",
        "convert-svg":"SVG to image","online-ppt-to-pdf":"PPT to PDF",
        "convert-markdown":"Markdown converter","hex-to-base64":"Hex to Base64",
        "online-run-csharp":"C# online compiler",
        "online-run-golang":"Go online compiler",
        "hf-image-to-text":"Image to text (AI)",
        "file-to-base64":"File to Base64 encoder",
        "ai-photo-to-painting":"AI photo to painting",
        "online-run-rust":"Rust online compiler",
        "online-run-swift":"Swift online compiler",
        "online-run-kotlin":"Kotlin online compiler",
        "url-to-base64":"URL to Base64 encoder",
        "online-run-ruby":"Ruby online compiler",
        "online-run-erlang":"Erlang online compiler",
        "online-runjs":"JavaScript code runner",
        "online-run-scala":"Scala online compiler",
        "online-run-perl":"Perl online compiler",
        "text-to-base64":"Text to Base64",
        "online-run-elixir":"Elixir online compiler",
        "base64-to-ascii":"Base64 to ASCII",
        "online-run-clojure":"Clojure online compiler",
    }
    return m.get(name, name.replace("-"," ").title())

TOOLFK_DESC = {e: _tfk_desc(e) for e in TOOLFK_ENDPOINTS}

TOOLS = {
    "web-scrape": {"desc": "Fetch and extract text content from a URL"},
    "web-search": {"desc": "Search the internet for information"},
    "python-exec": {"desc": "Execute Python code and return output"},
    "toolfk": {"desc": f"Call a ToolFK.com API ({len(TOOLFK_ENDPOINTS)} endpoints). Use /toolfk to list them. Pass endpoint=X&param=Y."},
    "synoxcloud": {"desc": "Call a SynoxCloud API endpoint. Use /synoxcloud to list endpoints. Pass endpoint=X&param=Y."},
    "youtube-search": {"desc": "Search YouTube for videos by keyword (no transcript). Returns titles, views, channels."},
    "tiktok-search": {"desc": "Search TikTok for trending videos by keyword. Returns plays, likes, author, description."},
    "github-search": {"desc": "Search GitHub repositories by keyword, sorted by stars. Returns repo info, stars, description, language, topics."},
    "github-analyze": {"desc": "Deep analyze a GitHub repo: fetch README, languages, file structure, metadata. Pass a full GitHub URL."},
    "reddit-search": {"desc": "Search Reddit for discussions and posts by keyword. Returns subreddit, score, comments."},
    "hn-search": {"desc": "Search Hacker News for popular stories and discussions. Returns points, author, comments."},
    "social-search": {"desc": "Multi-platform search across Reddit, Hacker News, and Medium simultaneously."},
    "memory-search": {"desc": "Search the user's persistent long-term memory log by keyword."},
    "memory-stats": {"desc": "Get stats about the user's persistent memory usage (total messages, days active)."},
    "doc-analyze": {"desc": "Analyze an uploaded document or PDF. Pass file_id, file_name, and optional question."},
    "cron-add": {"desc": "Schedule a recurring AI prompt task. Pass interval_seconds (int) and prompt (str)."},
    "cron-list": {"desc": "List all scheduled cron tasks."},
    "cron-remove": {"desc": "Remove a scheduled cron task by its ID."},
    "monitor-add": {"desc": "Start monitoring a web page for changes. Pass url and optional label."},
    "monitor-list": {"desc": "List all monitored web pages."},
}

_DISALLOWED_HOSTS = ["169.254.", "127.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31.", "192.168.", "0.0.0.0", "localhost",
    "metadata.google.internal", "169.254.169.254", "100.100.100.200"]

async def execute_tool(name, args, uid=None):
    c = await get_http()
    if name == "web-scrape":
        url = args.get("url", "")
        host = urllib.parse.urlparse(url).hostname or ""
        for blocked in _DISALLOWED_HOSTS:
            if host.startswith(blocked) or host == blocked:
                return f"Blocked: cannot access internal/private host '{host}'"
        r = await c.get(url, timeout=30)
        text = r.text[:5000]
        return f"Content from {url}:\n{text[:2000]}"
    if name == "web-search":
        q = args.get("query", "")
        encoded_q = urllib.parse.quote(q)
        r = await c.get(f"https://api.duckduckgo.com/?q={encoded_q}&format=json&no_html=1", timeout=15)
        data = r.json()
        return f"Results for '{q}': {str(data.get('AbstractText', 'No results'))[:2000]}"
    if name == "python-exec":
        if uid != OWNER_ID:
            return "Error: only the bot owner can execute arbitrary Python code"
        code = args.get("code", "")
        try:
            class _SandboxModule:
                __slots__ = ('_m',)
                def __init__(self, name):
                    self._m = __import__(name)
                def __getattr__(self, attr):
                    if attr.startswith('_'):
                        raise AttributeError(f'access denied: {attr}')
                    return getattr(self._m, attr)
            restricted = {"__builtins__": {"abs": abs, "all": all, "any": any, "chr": chr, "dict": dict,
                "dir": dir, "divmod": divmod, "enumerate": enumerate, "filter": filter, "float": float,
                "format": format, "frozenset": frozenset, "hash": hash, "hex": hex, "id": id, "int": int,
                "isinstance": isinstance, "issubclass": issubclass, "iter": iter, "len": len, "list": list,
                "map": map, "max": max, "min": min, "next": next, "oct": oct, "ord": ord, "pow": pow,
                "range": range, "repr": repr, "reversed": reversed, "round": round, "set": set,
                "slice": slice, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple, "type": type,
                "zip": zip, "True": True, "False": False, "None": None, "print": print},
                "math": _SandboxModule("math"), "json": _SandboxModule("json"), "re": _SandboxModule("re"),
                "random": _SandboxModule("random"), "collections": _SandboxModule("collections"),
                "datetime": _SandboxModule("datetime"), "itertools": _SandboxModule("itertools")}
            local_vars = {}
            exec(code, restricted, local_vars)
            result = str(local_vars.get("result", "Code executed (no result variable)"))
            return f"Output: {result[:2000]}"
        except Exception as e:
            return f"Error: {e}"
    if name == "toolfk":
        endpoint = args.get("endpoint", "")
        tool_params = {k: v for k, v in args.items() if k not in ("endpoint", "tool")}
        if not endpoint:
            return f"Usage: pass endpoint=NAME (one of: {', '.join(TOOLFK_ENDPOINTS[:10])}...)"
        if not TOOLFK_TOKEN:
            return f"TOOLFK_TOKEN not set. Register at https://toolfk.com to get a token, then set the env var."
        try:
            c = await get_http()
            payload = {"token": TOOLFK_TOKEN, **tool_params}
            r = await c.post(f"http://api.toolfk.com/api/{endpoint}", data=payload, timeout=30)
            text = r.text[:5000]
            return f"[toolfk/{endpoint}] Result:\n{text[:2000]}"
        except Exception as e:
            return f"[toolfk/{endpoint}] Error: {e}"
    if name == "synoxcloud":
        endpoint = args.get("endpoint", "")
        tool_params = {k: v for k, v in args.items() if k not in ("endpoint", "tool")}
        if not endpoint:
            return f"Usage: pass endpoint=NAME. Use /synoxcloud to list. Pass endpoint=X&param=Y."
        ep_path = SYNOXCLOUD_ENDPOINTS.get(endpoint)
        if not ep_path:
            return f"Unknown endpoint '{endpoint}'. Use /synoxcloud to list all."
        try:
            sep = "&" if "?" in ep_path else "?"
            url = f"https://api.synoxcloud.xyz{ep_path}{sep}{urllib.parse.urlencode(tool_params)}"
            c = await get_http()
            r = await c.get(url, timeout=30)
            text = r.text[:5000]
            return f"[synoxcloud/{endpoint}] Result:\n{text[:2000]}"
        except Exception as e:
            return f"[synoxcloud/{endpoint}] Error: {e}"
    if name == "youtube-search":
        q = args.get("query", "")
        if not q:
            return "Pass a query parameter."
        return await bf.youtube_search(q, int(args.get("max_results", 5)))
    if name == "tiktok-search":
        q = args.get("query", "")
        if not q:
            return "Pass a query parameter."
        return await bf.tiktok_search(q, int(args.get("max_results", 5)))
    if name == "github-search":
        q = args.get("query", "")
        if not q:
            return "Pass a query parameter."
        return await bf.github_search(q, args.get("sort_by", "stars"), int(args.get("max_results", 5)))
    if name == "github-analyze":
        url = args.get("url", "")
        if not url:
            return "Pass a url parameter (full GitHub repo URL)."
        return await bf.analyze_github_repo(url, args.get("depth", "readme"))
    if name == "reddit-search":
        q = args.get("query", "")
        if not q: return "Pass a query parameter."
        return await bf.reddit_search(q)
    if name == "hn-search":
        q = args.get("query", "")
        if not q: return "Pass a query parameter."
        return await bf.hackernews_search(q)
    if name == "social-search":
        q = args.get("query", "")
        if not q: return "Pass a query parameter."
        return await bf.social_search_all(q)
    if name == "memory-search":
        q = args.get("query", "")
        uid = args.get("uid") or uid
        if not q: return "Pass a query parameter."
        results = await bf.search_user_memories(uid, q)
        return "\n".join(f"[{e['role']}] {e['content'][:200]}" for e in (results or [])) or "No memories found."
    if name == "memory-stats":
        stats = await bf.get_memory_stats(uid)
        if stats:
            return f"Total: {stats['total']} | User: {stats['user']} | AI: {stats['ai']} | Days: {stats['days']}"
        return "No memory data."
    if name == "doc-analyze":
        file_id = args.get("file_id", "")
        file_name = args.get("file_name", "document.bin")
        question = args.get("question", "")
        return await bf.analyze_document(file_id, file_name, question)
    if name == "cron-add":
        try:
            interval = int(args.get("interval_seconds", 0))
        except:
            return "interval_seconds must be an integer."
        prompt = args.get("prompt", "")
        if not prompt: return "Pass a prompt parameter."
        tid = bf.scheduler.add(interval, prompt, args.get("chat_id", 0))
        return f"Cron task added: [{tid}] every {interval}s"
    if name == "cron-list":
        tasks = bf.scheduler.list()
        return "\n".join(f"[{t[0]}] {t[1]} (every {t[2]}s)" for t in tasks) or "No cron tasks."
    if name == "cron-remove":
        tid = args.get("id", "")
        if not tid: return "Pass an id parameter."
        bf.scheduler.remove(tid)
        return f"Task {tid} removed."
    if name == "monitor-add":
        url = args.get("url", "")
        if not url: return "Pass a url parameter."
        label = args.get("label", url[:40])
        pid = bf.page_monitor.add(url, args.get("chat_id", 0), label)
        return f"Monitoring added: [{pid}] {label}"
    if name == "monitor-list":
        pages = bf.page_monitor.list()
        return "\n".join(f"[{p[0]}] {p[1]} ({p[2]})" for p in pages) or "No monitors."
    return f"Unknown tool: {name}"

def format_agent_messages(log):
    if not log: return ""
    return "\n".join(f"[{e['sender']} -> {e['receiver']}] ({e['type']}): {e['content'][:300]}" for e in log[-8:])

checkpoint_counter = 0

async def save_checkpoint(uid, tag, data):
    global checkpoint_counter
    checkpoint_counter += 1
    cp = {"tag": tag, "data": data, "time": time.time()}
    key = f"ckpt_{uid}"
    all_ckpts = {}
    if os.path.exists("checkpoints.json"):
        try:
            with open("checkpoints.json", encoding="utf-8") as f: all_ckpts = json.load(f)
        except Exception:
            pass
    all_ckpts.setdefault(str(uid), []).append(cp)
    if len(all_ckpts[str(uid)]) > 20: all_ckpts[str(uid)] = all_ckpts[str(uid)][-20:]
    _atomic_save("checkpoints.json", all_ckpts)

async def run_architecture(arch, agents_in_team, user_text, provider, uid=None, msg_log=None):
    if msg_log is None: msg_log = []

    if arch == "supervisor":
        orc_prompt = AGENTS.get("orchestrator", {}).get("prompt", "You are a coordinator.")
        sub_agents = [a for a in agents_in_team if a in AGENTS and a != "orchestrator"][:5]
        if not sub_agents:
            sub_agents = [a for a in AGENTS if a != "orchestrator"][:5]
        chat_log = format_agent_messages(msg_log)

        decompose = await smart_call([{"role": "system", "content": f"{orc_prompt}\n\nDecompose this request into up to 4 clear sub-tasks. For each sub-task, assign the best agent from: {', '.join(sub_agents)}. Output as JSON:\n[\n  {{\"agent\": \"agent_name\", \"task\": \"sub-task description\", \"criteria\": \"quality check\"}},\n  ...\n]\n\nRequest: {user_text}"}], provider)
        msg_log.append({"sender": "supervisor", "receiver": "coordinator", "type": "plan", "content": decompose[:500]})
        try:
            plan_steps = json.loads(decompose.strip().removeprefix("```json").removesuffix("```").strip())
        except:
            plan_steps = [{"agent": a, "task": user_text, "criteria": "correct and complete"} for a in sub_agents[:3]]

        reports = []
        for step in plan_steps[:4]:
            agent_name = step.get("agent", sub_agents[0] if sub_agents else "orchestrator")
            if agent_name not in AGENTS:
                agent_name = sub_agents[0] if sub_agents else "orchestrator"
            task_desc = step.get("task", "Process the request")
            quality_criteria = step.get("criteria", "correct and complete")
            prompt = AGENTS[agent_name]["prompt"]
            context = f"Task: {task_desc}\n\nOriginal request: {user_text}\n\nPrevious reports:\n" + "\n".join(reports[-3:])
            result = await smart_call([{"role": "system", "content": f"{prompt}\n\nQuality criteria: {quality_criteria}"}, {"role": "user", "content": context}], provider)
            msg_log.append({"sender": agent_name, "receiver": "supervisor", "type": "report", "content": str(result)[:300]})

            review = await smart_call([{"role": "system", "content": f"You are a quality supervisor. Review this agent output against: {quality_criteria}\n\nRate 1-10 and suggest ONE improvement if score < 8.\nRespond JSON: {{\"score\": 0-10, \"pass\": bool, \"improvement\": \"\" or \"suggestion\"}}"}, {"role": "user", "content": f"Agent: {agent_name}\nTask: {task_desc}\n\nOutput:\n{result[:2000]}"}], provider)
            msg_log.append({"sender": "supervisor", "receiver": agent_name, "type": "review", "content": review[:300]})
            try:
                review_data = json.loads(review.strip().removeprefix("```json").removesuffix("```").strip())
                if not review_data.get("pass", True) and review_data.get("improvement"):
                    improved = await smart_call([{"role": "system", "content": f"{prompt}\n\nImprove your output based on: {review_data['improvement']}"}, {"role": "user", "content": context}], provider)
                    result = improved
                    msg_log.append({"sender": agent_name, "receiver": "supervisor", "type": "revised", "content": str(result)[:300]})
            except:
                pass
            reports.append(f"[{agent_name}]: {str(result)[:2000]}")
            if uid: await save_checkpoint(uid, f"supervisor_{agent_name}", {"task": task_desc, "result": str(result)[:500]})

        synthesis = await smart_call([{"role": "system", "content": orc_prompt}, {"role": "user", "content": f"Original request: {user_text}\n\nAgent reports:\n" + "\n\n".join(reports) + "\n\nSynthesize a final answer. Cite each agent's contribution."}], provider)
        msg_log.append({"sender": "supervisor", "receiver": "user", "type": "final", "content": synthesis})
        steps_summary = "\n".join(f"  {i+1}. [{s.get('agent','?')}] {s.get('task','')[:80]}" for i, s in enumerate(plan_steps[:4]))
        if uid: await save_checkpoint(uid, "supervisor_done", {"final": synthesis[:500]})
        return f"Supervisor pipeline ({len(plan_steps)} agents)\n{steps_summary}\n\n{synthesis}"

    if arch == "reflection":
        reflection_rounds = 2
        current = await smart_call([{"role": "system", "content": AGENTS.get(agents_in_team[0], {}).get("prompt", "You are a helpful assistant.")}, {"role": "user", "content": user_text}], provider)
        msg_log.append({"sender": agents_in_team[0] if agents_in_team else "agent", "receiver": "user", "type": "initial", "content": current[:300]})
        for r in range(reflection_rounds):
            reflect = await smart_call([{"role": "system", "content": "You are a critical reviewer. Analyze the following response. Identify: 1) what's good, 2) what's missing or could be improved, 3) factual errors. Be specific."}, {"role": "user", "content": f"Original request: {user_text}\n\nResponse to review:\n{current[:3000]}"}], provider)
            msg_log.append({"sender": "critic", "receiver": agents_in_team[0] if agents_in_team else "agent", "type": "reflection", "content": reflect[:300]})
            improved = await smart_call([{"role": "system", "content": f"{AGENTS.get(agents_in_team[0], {}).get('prompt', 'You are a helpful assistant.')}\n\nCritique received:\n{reflect}\n\nImprove your response based on this critique."}, {"role": "user", "content": user_text}], provider)
            msg_log.append({"sender": agents_in_team[0] if agents_in_team else "agent", "receiver": "user", "type": f"refined_r{r+1}", "content": improved[:300]})
            current = improved
            if uid: await save_checkpoint(uid, f"reflection_r{r+1}", {"reflection": reflect[:300], "improved": improved[:300]})
        return current

    return await smart_call([{"role": "user", "content": user_text}], provider)

    team_def = TEAMS.get(active_team, {})
    plan = team_def.get("plan", [])

    if arch == "sequential":
        context = user_text
        if plan:
            for step in plan:
                agent_name = step["agent"]
                if agent_name not in AGENTS: continue
                task_desc = step.get("task", "Process the request")
                chat_log = format_agent_messages(msg_log)
                prompt = AGENTS[agent_name]["prompt"]
                messages = [{"role": "system", "content": f"{prompt}\n\nYour specific task: {task_desc}\n\nPrevious agent messages:\n{chat_log}"}, {"role": "user", "content": context}]
                result = await smart_call(messages, provider)
                msg_log.append({"sender": agent_name, "receiver": "coordinator", "type": "report", "content": result})
                context = context + f"\n\n[{agent_name}]: {result}"
                if uid: await save_checkpoint(uid, f"sequential_{agent_name}", {"context": context, "msg_log": msg_log})
        else:
            for agent_name in agents_in_team:
                if agent_name not in AGENTS: continue
                prompt = AGENTS[agent_name]["prompt"]
                messages = [{"role": "system", "content": prompt}, {"role": "user", "content": context}]
                result = await smart_call(messages, provider)
                msg_log.append({"sender": agent_name, "receiver": "coordinator", "type": "report", "content": result})
                context = context + f"\n\n[{agent_name}]: {result}"
                if uid: await save_checkpoint(uid, f"sequential_{agent_name}", {"context": context})
        return context

    if arch == "parallel":
        tasks = []
        for agent_name in agents_in_team:
            if agent_name not in AGENTS: continue
            prompt = AGENTS[agent_name]["prompt"]
            messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_text}]
            tasks.append(smart_call(messages, provider))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged = []
        for i, agent_name in enumerate(agents_in_team):
            r = results[i] if i < len(results) else "Error"
            merged.append(f"[{agent_name}]: {r}")
            msg_log.append({"sender": agent_name, "receiver": "coordinator", "type": "report", "content": str(r)[:300]})
        merge_prompt = f"Merge these agent responses into one coherent answer:\n\n" + "\n\n".join(merged)
        final = await smart_call([{"role": "user", "content": merge_prompt}], provider)
        msg_log.append({"sender": "coordinator", "receiver": "user", "type": "final", "content": final})
        if uid: await save_checkpoint(uid, "parallel_done", {"final": final, "msg_log": msg_log})
        return final

    if arch == "hierarchical":
        orc = AGENTS.get("orchestrator", {}).get("prompt", "You are a coordinator.")
        sub_agents = [a for a in agents_in_team if a in AGENTS and a != "orchestrator"]
        chat_log = format_agent_messages(msg_log)
        plan_prompt = f"{orc}\n\nTask: {user_text}\n\nAvailable agents: {', '.join(sub_agents)}\n\nAgent messages so far:\n{chat_log}\n\nDecide which agents to use and create a plan."
        plan = await smart_call([{"role": "system", "content": plan_prompt}], provider)
        msg_log.append({"sender": "orchestrator", "receiver": "coordinator", "type": "plan", "content": plan})
        tasks = []
        used_agents = []
        for agent_name in sub_agents[:3]:
            prompt = AGENTS[agent_name]["prompt"]
            assign_msg = f"Task: {user_text}\n\nCoordinator plan: {plan}\n\nAgent messages:\n{chat_log}"
            messages = [{"role": "system", "content": prompt}, {"role": "user", "content": assign_msg}]
            tasks.append(smart_call(messages, provider))
            used_agents.append(agent_name)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        reports = []
        for i, agent_name in enumerate(used_agents):
            r = results[i] if not isinstance(results[i], Exception) else f"Error: {results[i]}"
            reports.append(f"[{agent_name}]: {r}")
            msg_log.append({"sender": agent_name, "receiver": "orchestrator", "type": "report", "content": str(r)[:300]})
        reports_str = "\n\n".join(reports)
        final = await smart_call([{"role": "system", "content": orc}, {"role": "user", "content": f"Task: {user_text}\n\nPlan: {plan}\n\nReports:\n{reports_str}\n\nSynthesize the final answer based on all agent reports."}], provider)
        msg_log.append({"sender": "orchestrator", "receiver": "user", "type": "final", "content": final})
        if uid: await save_checkpoint(uid, "hierarchical_done", {"final": final, "msg_log": msg_log})
        return final

    if arch == "mesh":
        agents_used = [a for a in agents_in_team[:4] if a in AGENTS]
        chat_log = format_agent_messages(msg_log)
        prompts = "\n\n".join(f"[{a}]: {AGENTS[a]['prompt']}" for a in agents_used)
        messages = [{"role": "system", "content": f"You are a team of specialists collaborating. Available:\n\n{prompts}\n\nAgent messages:\n{chat_log}\n\nDiscuss and solve the task together."}, {"role": "user", "content": user_text}]
        result = await smart_call(messages, provider)
        msg_log.append({"sender": "mesh-team", "receiver": "user", "type": "final", "content": result})
        if uid: await save_checkpoint(uid, "mesh_done", {"final": result})
        return result

    if arch == "voting":
        tasks = []
        agents_used = [a for a in agents_in_team[:5] if a in AGENTS]
        for agent_name in agents_used:
            prompt = AGENTS[agent_name]["prompt"]
            messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_text}]
            tasks.append(smart_call(messages, provider))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, agent_name in enumerate(agents_used):
            r = results[i] if not isinstance(results[i], Exception) else "Error"
            msg_log.append({"sender": agent_name, "receiver": "judge", "type": "vote", "content": str(r)[:300]})
        votes = "\n\n".join(f"[{agents_used[i]}]: {results[i]}" if not isinstance(results[i], Exception) else f"[{agents_used[i]}]: Error" for i in range(len(agents_used)))
        vote_prompt = f"Review these answers and select the best one. Explain your choice.\n\nQuestion: {user_text}\n\nAnswers:\n{votes}"
        final = await smart_call([{"role": "user", "content": vote_prompt}], provider)
        msg_log.append({"sender": "judge", "receiver": "user", "type": "final", "content": final})
        if uid: await save_checkpoint(uid, "voting_done", {"final": final})
        return final

    return await smart_call([{"role": "user", "content": user_text}], provider)

async def run_autonomous(goal, uid):
    memory_buffers.setdefault(uid, [])
    recent = memory_buffers[uid][-6:]
    context = "\n".join(recent) if recent else "No prior context."

    plan_prompt = (
        f"You are an autonomous agent planner. Break this goal into executable steps.\n"
        f"Goal: {goal}\nRecent memory:\n{context}\n\n"
        f"Respond with ONLY a JSON array of steps (no markdown):\n"
        f'[{{\"step\":1,\"type\":\"reason|tool\",\"tool\":null|\"web-scrape\"|\"web-search\"|\"python-exec\"|\"toolfk\"|\"synoxcloud\",'
        f'"task\":\"description\",\"input\":{{}},\"expected\":\"what this produces\"}}]\n\n'
        f"Use 'reason' for LLM thinking, 'tool' to use a tool. For toolfk/synoxcloud pass {{\"endpoint\":\"NAME\",...params}}. 500+ synoxcloud endpoints available. Max 5 steps."
    )
    raw = await smart_call([{"role": "user", "content": plan_prompt}], active_provider)
    raw = raw.strip()
    if raw.startswith("```"): raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return f"Planner failed to produce steps. Raw:\n{raw[:300]}"
    try:
        steps = json.loads(match.group())
    except Exception:
        return f"Planner JSON parse error. Raw:\n{raw[:300]}"

    log(f"Autonomous plan ({len(steps)} steps) for uid {uid}")

    results = []
    for i, step in enumerate(steps):
        step_type = step.get("type", "reason")
        task = step.get("task", f"Step {i+1}")
        memory_buffers.append(uid, f"[PLAN] Step {i+1}: {task}")

        if step_type == "tool":
            tool_name = step.get("tool")
            tool_input = step.get("input", {})
            tool_result = await execute_tool(tool_name, tool_input, uid)
            results.append(f"Step {i+1} ({tool_name}): {tool_result[:500]}")
            memory_buffers.append(uid, f"[TOOL] {tool_name}: {tool_result[:200]}")
        else:
            reason_prompt = (
                f"You are executing step {i+1} of an autonomous plan.\n"
                f"Goal: {goal}\nYour task: {task}\n"
                f"Previous results:\n" + "\n".join(results[-3:]) + "\n\n"
                f"Memory context:\n{context}\n\n"
                f"Complete your task."
            )
            reason_result = await smart_call([{"role": "user", "content": reason_prompt}], active_provider)
            results.append(f"Step {i+1} ({step_type}): {reason_result[:500]}")
            memory_buffers.append(uid, f"[REASON] Step {i+1}: {reason_result[:200]}")
        if uid: await save_checkpoint(uid, f"auto_step_{i+1}", {"step": step, "result": results[-1]})
    synthesis_prompt = (
        f"Synthesize the final answer for this goal based on all step results.\n"
        f"Goal: {goal}\n\nResults:\n" + "\n".join(results)
    )
    final = await smart_call([{"role": "user", "content": synthesis_prompt}], active_provider)
    memory_buffers.append(uid, f"[FINAL] {final[:200]}")
    save_memory()
    steps_summary = "\n".join(f"  {s.get('step',i+1)}. [{s.get('type','?')}] {s.get('task','')}" for i, s in enumerate(steps[:8]))
    return f"ðŸ¤– Autonomous Mode — Plan executed ({len(steps)} steps)\n{steps_summary}\n\n{final}"

DEFAULT_PREMADE_SKILLS = {
    "fullstack-web": {
        "desc": "Frontend, backend, API, and database for complete web apps",
        "agents": ["frontend-dev", "backend-dev", "api-dev", "database-architect"],
    },
    "data-pipeline": {
        "desc": "ETL, data engineering, analytics, and data warehousing",
        "agents": ["data-engineer", "etl-developer", "analytics-engineer", "data-analyst"],
    },
    "ml-ai": {
        "desc": "ML training, data science, NLP, and MLOps deployment",
        "agents": ["ml-engineer", "data-scientist", "nlp-specialist", "mlops-engineer"],
    },
    "devops-cloud": {
        "desc": "DevOps, cloud architecture, containers, and system admin",
        "agents": ["devops-engineer", "cloud-architect", "system-admin", "performance-engineer"],
    },
    "mobile-app": {
        "desc": "Mobile dev, backend API, UI design, and database",
        "agents": ["mobile-dev", "backend-dev", "api-dev", "database-admin"],
    },
    "security-audit": {
        "desc": "Security assessment, pentesting, and hardening",
        "agents": ["security-engineer", "system-admin", "cloud-architect"],
    },
    "api-service": {
        "desc": "API design, backend implementation, and database",
        "agents": ["api-dev", "backend-dev", "database-architect", "fullstack-dev"],
    },
    "ai-research": {
        "desc": "Research, prototyping, CV, and NLP experimentation",
        "agents": ["ai-researcher", "computer-vision-specialist", "nlp-specialist", "data-scientist"],
    },
    "web-scraper": {
        "desc": "Data extraction, ETL processing, and storage",
        "agents": ["backend-dev", "data-engineer", "etl-developer", "database-admin"],
    },
    "blockchain-web3": {
        "desc": "Smart contracts, dApps, backend, and security",
        "agents": ["blockchain-dev", "backend-dev", "api-dev", "security-engineer"],
    },
    "quality-assurance": {
        "desc": "Testing, QA automation, and performance monitoring",
        "agents": ["qa-engineer", "performance-engineer", "devops-engineer"],
    },
    "embedded-iot": {
        "desc": "Firmware, embedded systems, and hardware integration",
        "agents": ["embedded-dev", "backend-dev", "security-engineer"],
    },
}

AGENTS = copy.deepcopy(DEFAULT_AGENTS)
if os.path.exists(AGENTS_FILE):
    try:
        with open(AGENTS_FILE, encoding="utf-8") as f:
            AGENTS.update(json.load(f))
    except Exception: pass

AGENT_PROVIDERS = {}
if os.path.exists(AGENT_PROVIDERS_FILE):
    try:
        with open(AGENT_PROVIDERS_FILE, encoding="utf-8") as f:
            AGENT_PROVIDERS.update(json.load(f))
    except Exception: pass

PREMADE_SKILLS = copy.deepcopy(DEFAULT_PREMADE_SKILLS)
if os.path.exists(PREMADE_SKILLS_FILE):
    try:
        with open(PREMADE_SKILLS_FILE, encoding="utf-8") as f:
            PREMADE_SKILLS.update(json.load(f))
    except Exception: pass

TEAMS = {}
if os.path.exists(TEAMS_FILE):
    try:
        with open(TEAMS_FILE, encoding="utf-8") as f:
            TEAMS.update(json.load(f))
    except Exception: pass

PROVIDERS = {
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "meta/llama-3.3-70b-instruct",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "key": os.environ.get("GROQ_KEY", "set-via-env-var"),
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "model": "gemini-2.0-flash",
        "key": os.environ.get("GEMINI_KEY", "set-via-env-var"),
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "gryphe/mythomax-l2-13b",
        "key": os.environ.get("OPENROUTER_KEY", "set-via-env-var"),
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "key": os.environ.get("DEEPSEEK_KEY", "set-via-env-var"),
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-small-latest",
        "key": os.environ.get("MISTRAL_KEY", "set-via-env-var"),
    },
    "sambanova": {
        "url": "https://api.sambanova.ai/v1/chat/completions",
        "model": "Meta-Llama-3.3-70B-Instruct",
        "key": os.environ.get("SAMBANOVA_KEY", "set-via-env-var"),
    },
    "cerebras": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama3.1-70b",
        "key": os.environ.get("CEREBRAS_KEY", "set-via-env-var"),
    },
    "github": {
        "url": "https://models.inference.ai.azure.com/chat/completions",
        "model": "gpt-4o-mini",
        "key": os.environ.get("GITHUB_KEY", "set-via-env-var"),
    },
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "key": os.environ.get("TOGETHER_KEY", "set-via-env-var"),
    },
    "fireworks": {
        "url": "https://api.fireworks.ai/inference/v1/chat/completions",
        "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "key": os.environ.get("FIREWORKS_KEY", "set-via-env-var"),
    },
    "cohere": {
        "url": "https://api.cohere.ai/v1/chat/completions",
        "model": "command-r-plus-08-2024",
        "key": os.environ.get("COHERE_KEY", "set-via-env-var"),
    },
    "xai": {
        "url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-2-1212",
        "key": os.environ.get("XAI_KEY", "set-via-env-var"),
    },
    "lepton": {
        "url": "https://mixtral-8x22b.lepton.run/api/v1/chat/completions",
        "model": "mixtral-8x22b",
        "key": os.environ.get("LEPTON_KEY", "set-via-env-var"),
    },
    "imarena": {
        "url": "https://api.preview.arena.ai/v1/chat/completions",
        "model": "auto",
        "key": "not configured"
    },

    "hy3": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "tencent/hy3",
        "key": os.environ.get("OPENROUTER_KEY", "set-via-env-var"),
    },
    "hy3-preview": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "tencent/hy3-preview",
        "key": os.environ.get("OPENROUTER_KEY", "set-via-env-var"),
    },

    "synoxcloud": {
        "url": "https://api.synoxcloud.xyz/api/ai-chat",
        "model": "claude-haiku-4.5",
        "key": "free"
    },

    "omniroute": {
        "url": os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions"),
        "model": os.environ.get("OMNIROUTE_MODEL", "auto"),
        "key": os.environ.get("OMNIROUTE_KEY", "skip-auth")
    },
    "vansrouter": {
        "url": os.environ.get("VANSROUTER_URL", "http://localhost:3003/api/v1/chat/completions"),
        "model": os.environ.get("VANSROUTER_MODEL", "auto"),
        "key": os.environ.get("VANSROUTER_KEY", "skip-auth")
    },
    "blackbox": {
        "url": "https://api.blackbox.ai/v1/chat/completions",
        "model": "deepseek-v4-flash",
        "key": os.environ.get("BLACKBOX_KEY", "set-via-env-var")
    },
    "openclaw": {
        "url": "http://localhost:20128/v1/chat/completions",
        "model": "auto",
        "key": "skip-auth"
    },
    "zenmux": {
        "url": "https://zenmux.ai/api/v1/chat/completions",
        "model": "x-ai/grok-4.5-free",
        "key": os.environ.get("ZENMUX_KEY", "set-via-env-var")
    },
    "zenmux-grok-4.5-free": {
        "url": "https://zenmux.ai/api/v1/chat/completions",
        "model": "x-ai/grok-4.5-free",
        "key": os.environ.get("ZENMUX_KEY", "set-via-env-var")
    },
    "zenmux-kimi-k3-free": {
        "url": "https://zenmux.ai/api/v1/chat/completions",
        "model": "z-ai/glm-5.2-free",
        "key": os.environ.get("ZENMUX_KEY", "set-via-env-var")
    },


    "bitrouter": {
        "url": "http://127.0.0.1:4356/v1/chat/completions",
        "model": "qwen/qwen3.6-flash",
        "key": "skip-auth"
    },
    "zyloo": {
        "url": "https://api.zyloo.io/v1/chat/completions",
        "model": "zyloo/kimi-k2",
        "key": os.environ.get("ZYLOO_KEY", "set-via-env-var")
    },
    "siliconflow": {
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "model": "Qwen/Qwen3-8B",
        "key": os.environ.get("SILICONFLOW_KEY", "set-via-env-var")
    },
    "pollinations": {
        "url": "https://text.pollinations.ai/v1/chat/completions",
        "model": "openai",
        "key": "skip-auth"
    },
    "llm7": {
        "url": "https://api.llm7.io/v1/chat/completions",
        "model": "gpt-oss",
        "key": "skip-auth"
    },
    "ovh": {
        "url": "https://endpoints.ai.cloud.ovh.net/v1/chat/completions",
        "model": "Qwen/Qwen3.5-397B-A3B",
        "key": "skip-auth"
    },
    "freetheai": {
        "url": "https://api.freetheai.xyz/v1/chat/completions",
        "model": "glm-5.1",
        "key": os.environ.get("FREETHEAI_KEY", "set-via-env-var")
    },
    "freetokenfaucet": {
        "url": "https://freetokenfaucet.com/v1/chat/completions",
        "model": "deepseek-v4-flash",
        "key": os.environ.get("FREETOKENFAUCET_KEY", "set-via-env-var")
    },

    "agnes": {
        "url": "https://apihub.agnes-ai.com/v1/chat/completions",
        "model": "agnes-2.0-flash",
        "key": os.environ.get("AGNES_KEY", "set-via-env-var"),
    },
    "cloudflare": {
        "url": os.environ.get("CLOUDFLARE_URL", "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/ai/v1/chat/completions"),
        "model": "@cf/meta/llama-4-scout-17b-16e-instruct",
        "key": os.environ.get("CLOUDFLARE_KEY", "set-via-env-var"),
    },
    "huggingface": {
        "url": "https://router.huggingface.co/v1/chat/completions",
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "key": os.environ.get("HUGGINGFACE_KEY", "set-via-env-var"),
    },

    "nvidia-glm5": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "zhipuai/glm-5.2",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
    "nvidia-deepseek-v4": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "deepseek/deepseek-v4-pro",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
    "nvidia-qwen35": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "qwen/qwen3.5-397b-a3b",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
    "nvidia-kimi-k26": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "moonshotai/kimi-k2.5",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
    "nvidia-nemotron": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "nvidia/nemotron-3-ultra-550b",
        "key": os.environ.get("NVIDIA_KEY", "set-via-env-var"),
    },
}

if os.path.exists(PROVIDERS_FILE):
    try:
        with open(PROVIDERS_FILE, encoding="utf-8") as f:
            PROVIDERS.update(json.load(f))
    except Exception: pass

SYNOXCLOUD_ENDPOINTS = {}
SYNOXCLOUD_AI_MODELS = {}

if os.path.exists(SYNOXCLOUD_ENDPOINTS_FILE):
    try:
        with open(SYNOXCLOUD_ENDPOINTS_FILE, encoding="utf-8") as f:
            _sd = json.load(f)
        for _cat in _sd.get("endpoints", []):
            for _item in _cat.get("items", []):
                SYNOXCLOUD_ENDPOINTS[_item["id"]] = _item["path"]
    except Exception: pass

if os.path.exists(SYNOXCLOUD_AI_MODELS_FILE):
    try:
        with open(SYNOXCLOUD_AI_MODELS_FILE, encoding="utf-8") as f:
            SYNOXCLOUD_AI_MODELS = json.load(f)
        for _mid in SYNOXCLOUD_AI_MODELS:
            _key = f"synox-{_mid}"
            if _key not in PROVIDERS:
                _m = SYNOXCLOUD_AI_MODELS[_mid]
                PROVIDERS[_key] = {
                    "url": "https://api.synoxcloud.xyz/ai-chat",
                    "model": _mid,
                    "key": "free",
                }
    except Exception: pass

gateway.init_providers()

EFFORT_LEVELS = {
    "low": {"max_tokens": 512, "desc": "Fast, concise responses (512 tokens)"},
    "normal": {"max_tokens": 2048, "desc": "Balanced speed and detail (2048 tokens)"},
    "medium": {"max_tokens": 4096, "desc": "Moderate effort, more thorough (4096 tokens)"},
    "high": {"max_tokens": 8192, "desc": "High effort, detailed responses (8192 tokens)"},
    "superhigh": {"max_tokens": 16384, "desc": "Maximum effort, most thorough (16384 tokens)"},
}
effort = "medium"
thinking_mode = "off"

active_agent = "orchestrator"
active_provider = "groq"
active_team = None
active_arch = "single"
active_mode = "chat"
active_topic = "v1"  # v1=general AI, v2=cyberdeck

CYBERDECK_KEYWORDS = [
    "cyberdeck", "sbc", "raspberry pi", "orange pi", "radxa", "jetson", "lattepanda",
    "enclosure", "pelican", "display", "oled", "eink", "e-ink", "keyboard", "mechanical",
    "battery", "ups", "18650", "lipo", "solar", "antenna", "lora", "sdr", "hackrf",
    "rtl-sdr", "gps", "nfc", "fingerprint", "imu", "sensor", "pcb", "soldering",
    "wiring", "gpio", "i2c", "spi", "uart", "hdmi", "dsi", "csi", "nvme", "emmc",
    "3d print", "petg", "pla", "abs", "enclosure design", "bom", "build list",
    "component", "raspberry", "pi 5", "pi 4", "pi zero", "cm4", "cm5", "compute module",
    "ham radio", "amateur radio", "radio", "transceiver", "frequency", "mhz", "ghz",
    "forensics", "dfir", "volatile", "disk image", "malware", "incident",
    "test equipment", "oscilloscope", "multimeter", "logic analyzer", "spectrum",
    "thermal", "heatsink", "cooling", "fan", "heat pipe",
    "nato rail", "picatinny", "kevlar", "carbon fiber", "bamboo", "wood veneer",
    "cyberdeck builder", "build deck", "deck build", "portable computer",
    "field computer", "tactical", "rugged", "waterproof case",
    "milk-v", "hackberry", "zhihe", "bananapi", "banana pi", "odroid", "khadas",
    "waveshare", "pimoroni", "clockworkpi", "uconsole",
]
admins = {OWNER_ID}
if os.path.exists(ADMINS_FILE):
    try:
        with open(ADMINS_FILE, encoding="utf-8") as f:
            admins.update(json.load(f))
    except Exception:
        pass
mods = set()
if os.path.exists(MODS_FILE):
    try:
        with open(MODS_FILE, encoding="utf-8") as f:
            mods.update(json.load(f))
    except Exception:
        pass
_OFFSET_FILE = os.path.join(os.path.dirname(__file__), ".bot.offset")
last_update = 0
try:
    with open(_OFFSET_FILE, encoding="utf-8") as _f:
        last_update = int(_f.read().strip())
except Exception:
    pass
processed = set()
last_user_msg = _LRUDict(200)
_last_msg_times = _LRUDict(200)
from collections import OrderedDict
MAX_SESSIONS = 200

class LRUSessions(OrderedDict):
    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        self.move_to_end(key)
        if len(self) > MAX_SESSIONS:
            self.popitem(last=False)
    def __getitem__(self, key):
        val = super().__getitem__(key)
        self.move_to_end(key)
        return val

sessions = LRUSessions()

# ----- Per-User State System -----
class LRUUserState(OrderedDict):
    max_states = 300
    def __missing__(self, key):
        val = self[key] = {}
        if len(self) > self.max_states:
            self.popitem(last=False)
        return val
    def __getitem__(self, key):
        val = super().__getitem__(key)
        self.move_to_end(key)
        return val

_user_state = LRUUserState()
def _get_state(chat_id):
    return _user_state[chat_id]


def set_user_pref(chat_id, key, value):
    _get_state(chat_id)[key] = value

def reset_user_state(chat_id):
    _user_state.pop(chat_id, None)

def resolve_state(chat_id):
    global active_agent, active_provider, active_team, active_arch, active_mode, effort, thinking_mode
    s = _get_state(chat_id)
    if "active_agent" in s: active_agent = s["active_agent"]
    if "active_provider" in s: active_provider = s["active_provider"]
    if "active_team" in s: active_team = s["active_team"]
    if "active_arch" in s: active_arch = s["active_arch"]
    if "active_mode" in s: active_mode = s["active_mode"]
    if "effort" in s: effort = s["effort"]
    if "thinking_mode" in s: thinking_mode = s["thinking_mode"]

# ----- Response Cache -----
_response_cache = {}
_RESPONSE_CACHE_TTL = 300  # 5 minutes
_RESPONSE_CACHE_MAX = 500
_cache_stats = {"hits": 0, "misses": 0, "stored": 0}

async def _cache_cleanup():
    while True:
        await asyncio.sleep(600)
        now = time.time()
        stale = [k for k, v in _response_cache.items() if now - v["t"] >= _RESPONSE_CACHE_TTL]
        for k in stale:
            del _response_cache[k]
        if stale:
            log(f"cache: purged {len(stale)} stale entries ({len(_response_cache)} remain)")

def _cache_key(messages, provider):
    import hashlib
    raw = json.dumps([provider, messages], sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()

def _get_cached(messages, provider):
    key = _cache_key(messages, provider)
    entry = _response_cache.get(key)
    if entry and time.time() - entry["t"] < _RESPONSE_CACHE_TTL:
        _cache_stats["hits"] += 1
        return entry["text"]
    _cache_stats["misses"] += 1
    return None

def _set_cached(messages, provider, text):
    if len(_response_cache) >= _RESPONSE_CACHE_MAX:
        oldest = min(_response_cache.keys(), key=lambda k: _response_cache[k]["t"])
        del _response_cache[oldest]
    key = _cache_key(messages, provider)
    _response_cache[key] = {"t": time.time(), "text": text}
    _cache_stats["stored"] += 1

# ----- Smart Task-Based Provider Routing -----
_TASK_PROVIDERS = {
    "code": "deepseek",
    "reasoning": "gemini",
    "creative": "together",
    "research": "groq",
    "science": "nvidia",
    "speed": "cerebras",
    "writing": "mistral",
    "general": "groq",
}

def detect_task_type(messages):
    text = " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str)).lower()
    if any(w in text for w in ["code", "program", "function", "debug", "implement", "write a", "python", "javascript", "script"]):
        return "code"
    if any(w in text for w in ["why", "how", "explain", "reason", "think", "analyze", "compare"]):
        return "reasoning"
    if any(w in text for w in ["write a story", "poem", "creative", "imagine", "design"]):
        return "creative"
    if any(w in text for w in ["research", "find", "search", "summarize", "what is"]):
        return "research"
    if any(w in text for w in ["science", "physics", "chemistry", "biology", "math", "equation"]):
        return "science"
    return "general"

def suggest_provider(messages, preferred=None):
    if preferred and PROVIDERS.get(preferred, {}).get("key", "") not in ("set-via-env-var", "not configured", ""):
        return preferred
    task = detect_task_type(messages)
    suggested = _TASK_PROVIDERS.get(task, "groq")
    if PROVIDERS.get(suggested, {}).get("key", "") in ("set-via-env-var", "not configured", ""):
        for fallback in ["groq", "gemini", "openrouter", "deepseek"]:
            if PROVIDERS.get(fallback, {}).get("key", "") not in ("set-via-env-var", "not configured", ""):
                return fallback
    return suggested

# ----- Per-User State Helpers -----
def get_effort(chat_id=None):
    s = _get_state(chat_id) if chat_id else {}
    return s.get("effort", effort)

# ----- Circuit Breaker System -----
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = {}  # provider -> {"failures": int, "last_fail": float, "state": str}

    def _ensure(self, provider):
        if provider not in self.state:
            self.state[provider] = {"failures": 0, "last_fail": 0, "state": "closed"}

    def allow(self, provider):
        self._ensure(provider)
        s = self.state[provider]
        if s["state"] == "open":
            if time.time() - s["last_fail"] > self.recovery_timeout:
                s["state"] = "half-open"
                log(f"CB {provider}: open -> half-open (probe)")
                return True
            return False
        return True

    def record_success(self, provider):
        self._ensure(provider)
        s = self.state[provider]
        if s["state"] == "half-open":
            log(f"CB {provider}: half-open -> closed (probe OK)")
        s["state"] = "closed"
        s["failures"] = 0

    def record_failure(self, provider):
        self._ensure(provider)
        s = self.state[provider]
        s["failures"] += 1
        s["last_fail"] = time.time()
        if s["failures"] >= self.failure_threshold:
            s["state"] = "open"
            log(f"CB {provider}: closed -> open ({s['failures']} failures)")

    def status(self, provider):
        self._ensure(provider)
        return self.state[provider]["state"]

circuit_breaker = CircuitBreaker()

# ----- Provider Racing -----
async def race_providers(messages, providers, timeout=15):
    async def call_one(p):
        try:
            result = await asyncio.wait_for(call_provider(messages, p), timeout)
            if result and not result[:20].lower().startswith("error"):
                return p, result
        except Exception:
            pass
        return p, None
    tasks = [call_one(p) for p in providers if circuit_breaker.allow(p)]
    if not tasks:
        return None, None
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    for t in done:
        p, r = t.result()
        if r:
            return p, r
    return None, None

async def smart_call(messages, preferred):
    cached = _get_cached(messages, preferred)
    if cached:
        log(f"Cache HIT for {preferred}")
        return cached
    ap = resolve_provider()
    if ap:
        result = await call_provider(messages, "__agent_provider__", override=ap)
        if result and not result[:20].lower().startswith("error"):
            _set_cached(messages, "__agent_provider__", result)
            return result
    effective = suggest_provider(messages, preferred)
    if effective != preferred:
        log(f"Smart route: {preferred} -> {effective} (task={detect_task_type(messages)})")
    if not circuit_breaker.allow(effective):
        log(f"CB {effective} OPEN, finding fallback for {preferred}")
        for fb in ["groq", "gemini", "openrouter", "deepseek"]:
            if fb != effective and circuit_breaker.allow(fb) and PROVIDERS.get(fb, {}).get("key", "") not in ("set-via-env-var", "not configured", ""):
                effective = fb
                log(f"CB fallback to {fb}")
                break
    text_len = len(" ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str)))
    if text_len < 500 and effective == preferred:
        candidates = [effective]
        for fb in ["groq", "gemini", "cerebras", "deepseek"]:
            if fb != effective and circuit_breaker.allow(fb) and PROVIDERS.get(fb, {}).get("key", "") not in ("set-via-env-var", "not configured", ""):
                candidates.append(fb)
                if len(candidates) >= 3:
                    break
        if len(candidates) > 1:
            log(f"Racing providers: {candidates}")
            winner, result = await race_providers(messages, candidates)
            if result:
                circuit_breaker.record_success(winner)
                for c in candidates:
                    if c != winner:
                        circuit_breaker.record_failure(c)
                return result
    result = await gateway.execute(messages, effective)
    if result and not result[:20].lower().startswith("error"):
        circuit_breaker.record_success(effective)
        _set_cached(messages, preferred, result)
    else:
        circuit_breaker.record_failure(effective)
    return result

# ----- Provider Health Dashboard -----
def get_provider_health():
    rows = []
    for pid, p in sorted(PROVIDERS.items()):
        key = p.get("key", "")
        if key in ("skip-auth",) or p.get("url", "").startswith("http://127.0.0.1") or p.get("url", "").startswith("http://localhost"):
            continue
        configured = key not in ("set-via-env-var", "not configured", "", "free")
        gh = gateway.health.get(pid, {"success":0,"failure":0,"cooldown_until":0,"avg_latency":0.0})
        latency = gh.get("avg_latency", 0)
        if latency:
            latency_str = f"{latency*1000:.0f}ms"
        else:
            latency_str = "-"
        status = "OK" if gh.get("success", 0) > 0 else ("FAIL" if gh.get("failure", 0) > 0 else "?")
        if gh.get("cooldown_until", 0) > time.time():
            status = "COOLDOWN"
        rows.append((pid, status, latency_str, "key" if configured else "no-key"))
    return rows
team_sessions = _LRUDict(200)
load_sessions()
load_memory()
load_routines()
load_multi()
load_custom_commands()
load_context_files()
load_conversation_tags()

async def tg(method, data=None):
    c = await get_http()
    for _attempt in range(2):
        try:
            r = await c.post(f"{TG_API}/{method}", json=data or {}, timeout=15)
            resp = r.json()
            if resp.get("ok"):
                return resp
            if resp.get("error_code") == 429:
                retry_after = resp.get("parameters", {}).get("retry_after", 5)
                await asyncio.sleep(retry_after)
                continue
            log(f"TG API error: {method} {resp}")
            return resp
        except Exception as _e:
            if _attempt == 0:
                await asyncio.sleep(1)
                continue
            log(f"TG API error: {method} {_e}")
            return {"ok": False, "error": str(_e)}
    return {"ok": False}

_sent_cache = {}
async def send(chat, text, parse_mode=None, receiver_user=None):
    raw = str(text)
    if not raw:
        return {"ok": True, "empty": True}
    key = (chat, raw[:200])
    now = time.time()
    if key in _sent_cache and now - _sent_cache[key] < 3:
        log(f"dedup: skipped duplicate send to {chat}")
        return {"ok": True, "dedup": True}
    _sent_cache[key] = now
    if len(_sent_cache) > 200:
        _sent_cache.clear()

    rich_ok = rich_mod and is_experimental_enabled("rich-messages") and rich_mod.has_rich_content(raw) and len(raw) < 5000

    if rich_ok:
        try:
            c = await get_http()
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            r = await rich_mod.send_rich(c, bot_token, chat, raw, receiver_user)
            if r and r.get("ok"):
                return r
        except Exception:
            pass

    rich_v2_ok = rt2_mod and is_experimental_enabled("rich-text-v2") and len(raw) > 50 and len(raw) < 8000
    if rich_v2_ok:
        try:
            rich_data = rt2_mod.format_rich_response(raw)
            if rich_data and rich_data.get("text"):
                raw = rich_data["text"]
                parse_mode = rich_data.get("parse_mode", "HTML")
        except Exception:
            pass

    if parse_mode is None and ("```" in raw or "**" in raw or "`" in raw):
        import re as _re
        html = raw
        html = html.replace("&", "&amp;")
        html = _re.sub(r"```(\w*)\n(.*?)```", lambda m: "<pre>" + m.group(2) + "</pre>", html, flags=_re.DOTALL)
        html = _re.sub(r"```(.*?)```", lambda m: "<pre>" + m.group(1) + "</pre>", html, flags=_re.DOTALL)
        html = _re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1).replace("&amp;", "&") + "</code>", html)
        html = _re.sub(r"\*\*(.+?)\*\*", lambda m: "<b>" + m.group(1).replace("&amp;", "&") + "</b>", html)
        html = _re.sub(r"\*(.+?)\*", lambda m: "<i>" + m.group(1).replace("&amp;", "&") + "</i>", html)
        raw = html
        parse_mode = "HTML"

    MAX_TG = 4096
    params = {"chat_id": chat, "text": raw}
    if parse_mode:
        params["parse_mode"] = parse_mode
    if receiver_user:
        params["receiver_user_id"] = receiver_user

    if len(raw) <= MAX_TG:
        if receiver_user:
            params["receiver_user_id"] = receiver_user
        log(f"SEND to chat={chat}: {raw[:80]}...")
        result = await tg("sendMessage", params)
        log(f"SEND result: ok={result.get('ok')} error={result.get('error_code', 'none')}")
        return result

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

    results = []
    for chunk in chunks:
        p = {"chat_id": chat, "text": chunk}
        if receiver_user:
            p["receiver_user_id"] = receiver_user
        r = await tg("sendMessage", p)
        results.append(r)
        await asyncio.sleep(0.3)
    return results[-1] if results else {"ok": True}

async def typing(chat):
    await tg("sendChatAction", {"chat_id": chat, "action": "typing"})

async def bot_delete_message(chat, mid):
    try:
        c = await get_http()
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        await c.post(f"https://api.telegram.org/bot{bot_token}/deleteMessage",
            json={"chat_id": chat, "message_id": mid}, timeout=10)
    except Exception:
        pass

async def call_provider(messages, provider, override=None):
    if override:
        p = override
    else:
        p = PROVIDERS[provider]
    c = await get_http()
    max_tokens = EFFORT_LEVELS[effort]["max_tokens"]
    msgs = copy.deepcopy(messages)

    if thinking_mode == "extended":
        thinking_msg = "You MUST reason step-by-step before answering. Think through the problem carefully, showing your reasoning process, then provide your final answer."
        if msgs and msgs[0].get("role") == "system":
            msgs[0]["content"] = thinking_msg + "\n\n" + msgs[0]["content"]
        else:
            msgs.insert(0, {"role": "system", "content": thinking_msg})
    elif thinking_mode == "adaptive":
        combined = " ".join(m.get("content", "") for m in msgs[-3:])
        if len(combined) > 300 or "?" in combined or "why" in combined.lower() or "how" in combined.lower() or "explain" in combined.lower():
            thinking_msg = "Think through this step-by-step before answering. Show your reasoning."
            if msgs and msgs[0].get("role") == "system":
                msgs[0]["content"] = thinking_msg + "\n\n" + msgs[0]["content"]
            else:
                msgs.insert(0, {"role": "system", "content": thinking_msg})

    if provider == "gemini":
        parts = []
        for m in msgs:
            role = "model" if m["role"] == "assistant" else "user"
            parts.append({"role": role, "parts": [{"text": m["content"]}]})
        r = await c.post(p["url"], json={"contents": parts}, headers={"X-Goog-Api-Key": p["key"]})
        if r.status_code == 200:
            data = r.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))
            return str(data)
        return f"Gemini error: {r.status_code} - {r.text[:500]}"
    elif provider == "synoxcloud" or provider.startswith("synox-"):
        last = [m for m in msgs if m["role"] == "user"]
        if not last:
            return "No user message found"
        prompt = last[-1]["content"]
        model_id = p.get("model", "gpt-5")
        model_info = SYNOXCLOUD_AI_MODELS.get(model_id, {})
        if model_info and isinstance(model_info, dict) and model_info.get("path"):
            ep_path = model_info["path"].split("?")[0]
            raw_params = model_info.get("params", [])
            param_names = [pp.split("=")[0].strip() for pp in raw_params if isinstance(pp, str) and pp.strip()]
            recommended = param_names[0] if param_names else "q"
            url = f"https://api.synoxcloud.xyz{ep_path}?{recommended}={urllib.parse.quote(prompt)}"
        else:
            recommended = "q"
            url = f"{p['url']}/{model_id}?q={urllib.parse.quote(prompt)}"
        key = p.get("key", "")
        if _is_configured(key) and key != "free":
            url += f"&apikey={key}"
        r = await c.get(url)
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, dict):
                    for k in ("result", "response", "message", "text", "data", "content"):
                        if k in data:
                            return str(data[k])
            except Exception:
                return r.text[:2000]
        return f"SynoxCloud error: {r.status_code} - {r.text[:500]}"
    else:
        headers = {
            "Content-Type": "application/json",
        }
        if p["key"] != "skip-auth":
            headers["Authorization"] = f"Bearer {p['key']}"
        body = {
            "model": p["model"],
            "messages": msgs,
            "max_tokens": max_tokens,
        }
        r = await c.post(p["url"], json=body, headers=headers)
        log(f"{provider} API: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content
            for k in ("answer", "result", "response", "message", "text", "data", "content"):
                if k in data and isinstance(data[k], str):
                    return data[k]
            return str(data)[:2000]
        return f"{provider.title()} error: {r.status_code} - {r.text[:500]}"

def resolve_provider(agent_name=None):
    agent_name = agent_name or active_agent
    cfg = AGENT_PROVIDERS.get(agent_name)
    if cfg and _is_configured(cfg.get("key", "")):
        return cfg
    return None

_empty_polls = 0

async def poll():
    global last_update, _empty_polls
    p = {"timeout": 15, "allowed_updates": ["message", "chat_join_request", "chat_member", "my_chat_member", "poll_answer"]}
    if last_update:
        p["offset"] = last_update + 1
    for attempt in range(3):
        try:
            c = await get_http()
            r = (await c.get(f"{TG_API}/getUpdates", params=p, timeout=20)).json()
            if not r.get("ok"):
                return []
            for u in r.get("result", []):
                last_update = u["update_id"]
            try:
                with open(_OFFSET_FILE, "w", encoding="utf-8") as _f:
                    _f.write(str(last_update))
            except Exception as _e:
                log(f"poll loop error: {_e}")
                pass
            result = r.get("result", [])
            now_ts = int(time.time())
            filtered = []
            for u in result:
                msg = u.get("message") or u.get("chat_join_request") or u.get("poll_answer")
                if msg and isinstance(msg, dict):
                    msg_date = msg.get("date", 0)
                    if msg_date and (now_ts - msg_date) > 300:
                        log(f"skipping stale update {u.get('update_id')} (age {now_ts - msg_date}s)")
                        continue
                filtered.append(u)
            result = filtered
            if result:
                _empty_polls = 0
            else:
                _empty_polls += 1
            return result
        except Exception as e:
            log(f"Poll attempt {attempt+1}/3 failed: {type(e).__name__}: {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
    return []

VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.json")
VERSION_STATE_FILE = os.path.join(os.path.dirname(__file__), "version_state.json")

def load_version():
    try:
        with open(VERSION_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "unknown", "whats_new": {}}

def load_version_state():
    try:
        with open(VERSION_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_version": "", "notified_chats": {}}

def save_version_state(state):
    _atomic_save(VERSION_STATE_FILE, state)

async def announce_update(old_v, new_v, changes, state):
    global _announced_versions
    if new_v in _announced_versions:
        log(f"announce_update: skipping v{new_v} (already announced this session)")
        state["last_announced_version"] = new_v
        state["last_version"] = new_v
        save_version_state(state)
        return state
    if new_v == state.get("last_announced_version", ""):
        log(f"announce_update: skipping v{new_v} (already announced per state)")
        _announced_versions.add(new_v)
        _save_announced_versions()
        return state
    _announced_versions.add(new_v)
    _save_announced_versions()
    known_chats = set()
    my_bot_id = 0
    try:
        my_bot_id = int(OWNER_ID)
    except Exception:
        pass
    try:
        for cid in sessions:
            known_chats.add(cid)
        for chat_ids in state.get("notified_chats", {}).values():
            for cid in chat_ids:
                known_chats.add(int(cid))
        for cid in list(multi_sessions.keys()):
            known_chats.add(int(cid))
    except Exception as e:
        log(f"announce_update: chat collection error: {e}")
    known_chats.discard(0)
    known_chats.discard(my_bot_id)
    ver_info = load_version()
    exp_features = ver_info.get("experimental", [])
    new_features = [c for c in changes if not any(kw in c.lower() for kw in ["fix", "bug", "crash", "patch", "hotfix", "corrected", "resolved"])]
    new_exp = [ef for ef in exp_features if ef not in state.get("announced_experimental", [])]
    total_new = len(new_features) + len(new_exp)
    if total_new < 5:
        log(f"Update skipped: v{old_v} -> v{new_v} (only {total_new} new items, need 5+)")
        state["last_version"] = new_v
        state["last_announced_version"] = new_v
        save_version_state(state)
        return state
    lines = []
    lines.append("🚀 ==============================")
    lines.append("   BIG UPDATE INCOMING!")
    lines.append("   ==============================")
    lines.append("")
    lines.append(f"  v{old_v} → v{new_v}")
    lines.append("")
    if new_features:
        lines.append(f"🆕 {len(new_features)} New Feature{'s' if len(new_features) > 1 else ''}:")
        lines.append("")
        for i, c in enumerate(new_features, 1):
            lines.append(f"  {i}. {c}")
        lines.append("")
    if new_exp:
        lines.append(f"🧪 {len(new_exp)} New Experimental Feature{'s' if len(new_exp) > 1 else ''}:")
        lines.append("")
        for i, ef in enumerate(new_exp, 1):
            lines.append(f"  {i}. {ef}")
        lines.append("")
        lines.append("  Use /experimental to enable!")
        lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("💡 Try these:")
    lines.append("  /start — See updated commands")
    lines.append("  /help — Browse all features")
    lines.append("  /version — Full changelog")
    if new_exp:
        lines.append("  /experimental — Enable new features")
    lines.append("")
    lines.append("🚀 Enjoying the bot? Share it with friends!")
    lines.append("")
    lines.append("🔕 Don't want these? /announcementoff")
    msg = "\n".join(lines)
    sent_count = 0
    opted_out = set(state.get("opted_out_announcements", []))
    for cid in known_chats:
        try:
            if cid in opted_out:
                continue
            if str(cid) not in state.get("notified_chats", {}).get(new_v, []):
                r = await send(cid, msg)
                if r and r.get("ok"):
                    state.setdefault("notified_chats", {}).setdefault(new_v, []).append(str(cid))
                    sent_count += 1
                await asyncio.sleep(0.1)
        except Exception:
            pass
    if new_exp:
        state.setdefault("announced_experimental", []).extend(new_exp)
    log(f"Update announced: v{old_v} -> v{new_v} to {sent_count} chats (features={len(new_features)}, experimental={len(new_exp)})")
    state["last_version"] = new_v
    state["last_announced_version"] = new_v
    save_version_state(state)
    return state

def get_git_commit():
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""

def get_git_log(from_sha, to_sha):
    if not from_sha or not to_sha or from_sha == to_sha:
        return []
    try:
        import subprocess
        r = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate", f"{from_sha}..{to_sha}"],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if r.returncode == 0 and r.stdout.strip():
            lines = r.stdout.strip().split("\n")
            return [l.split(" ", 1)[1] if " " in l else l for l in lines if l.strip()]
    except Exception:
        pass
    return []

def auto_bump_version():
    v = load_version()
    cur = v.get("version", "0.0.0")
    major = "0"
    minor = "0"
    try:
        segs = cur.split(".")
        major = segs[0]
        minor = segs[1] if len(segs) > 1 else "0"
    except Exception:
        pass
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if r.returncode == 0:
            build = r.stdout.strip()
            new_ver = f"{major}.{minor}.{build}"
        else:
            new_ver = f"{major}.{minor}.{int(time.time())}"
    except Exception:
        new_ver = f"{major}.{minor}.{int(time.time())}"
    v["version"] = new_ver
    v["updated"] = time.strftime("%Y-%m-%d")
    v["whats_new"] = v.get("whats_new", {})
    v["whats_new"][new_ver] = []
    _atomic_save(VERSION_FILE, v)
    return new_ver, v["whats_new"][new_ver]

def set_changelog(ver, changes):
    try:
        v = load_version()
        v.setdefault("whats_new", {})[ver] = changes
        _atomic_save(VERSION_FILE, v)
    except Exception:
        pass

async def auto_version_checker():
    while True:
        await asyncio.sleep(300)
        try:
            current = load_version()
            current_ver = current.get("version", "unknown")
            state = load_version_state()
            announced_ver = state.get("last_announced_version", "")
            last_ver = state.get("last_version", "")
            cur_git = get_git_commit()
            if current_ver != "unknown" and current_ver != announced_ver and current_ver != last_ver:
                changes = current.get("whats_new", {}).get(current_ver, [])
                log(f"Auto-check: new version detected {announced_ver or 'initial'} -> {current_ver}")
                state["last_version"] = current_ver
                state["last_git_commit"] = cur_git
                save_version_state(state)
                await announce_update(announced_ver or "initial", current_ver, changes, state)
                save_version_state(state)
            elif current_ver != last_ver:
                state["last_version"] = current_ver
                state["last_announced_version"] = current_ver
                state["last_git_commit"] = cur_git
                save_version_state(state)
        except Exception as e:
            log(f"Auto version check error: {e}")

async def run_startup_check():
    global BOT_VERSION
    try:
        version_info = load_version()
        ver = version_info.get("version", "unknown")
        BOT_VERSION = ver
        state = load_version_state()
        old_ver = state.get("last_version", "")
        old_git = state.get("last_git_commit", "")
        cur_git = get_git_commit()
        if old_ver and old_ver != ver:
            changes = version_info.get("whats_new", {}).get(ver, [])
            log(f"startup: version changed {old_ver} -> {ver}")
            state["last_git_commit"] = cur_git
            state["last_announced_version"] = ver
            save_version_state(state)
            await announce_update(old_ver, ver, changes, state)
            save_version_state(state)
        elif not old_ver and ver != "unknown":
            changes = version_info.get("whats_new", {}).get(ver, [])
            state["last_git_commit"] = cur_git
            state["last_announced_version"] = ver
            save_version_state(state)
            await announce_update("initial", ver, changes, state)
            save_version_state(state)
        else:
            state["last_version"] = ver
            state["last_announced_version"] = ver
            state["last_git_commit"] = cur_git
            save_version_state(state)
        log(f"Bot v{BOT_VERSION} started")
    except Exception as e:
        log(f"startup check error (non-fatal): {e}")
        try:
            with open("bot_crash.txt", "w", encoding="utf-8") as _cf:
                _cf.write(f"startup check error:\n{_tb.format_exc()}")
        except Exception:
            pass

async def main():
    global active_agent, active_provider, active_mode, active_arch, active_team, effort, thinking_mode, bf, last_update, processed, active_topic
    last_update = 0
    use_webhook = os.environ.get("WEBHOOK_MODE", "").lower() in ("1", "true", "yes")
    webhook_queue = None
    if use_webhook:
        try:
            import webhook_server as whs
            webhook_queue = asyncio.Queue()
            whs.update_queue = webhook_queue
            whs.SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET", whs.SECRET_TOKEN)
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, whs.start_server, os.environ.get("TELEGRAM_BOT_TOKEN", ""))
            await asyncio.sleep(2)
            try:
                import subprocess
                ngrok_proc = subprocess.Popen(["ngrok", "http", "8443", "--log=stdout"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                await asyncio.sleep(3)
                import httpx
                async with httpx.AsyncClient() as _c:
                    r = await _c.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                    tunnels = r.json().get("tunnels", [])
                    public_url = tunnels[0]["public_url"] if tunnels else None
                if public_url:
                    ok = await whs.setup_webhook(public_url)
                    if ok:
                        log(f"Webhook mode active: {public_url}")
                        _drain = asyncio.create_task(whs.drain_queue())
                        _drain.add_done_callback(_task_done)
                    else:
                        log("Webhook setup failed, falling back to polling")
                        use_webhook = False
                        webhook_queue = None
                else:
                    log("ngrok failed, falling back to polling")
                    use_webhook = False
                    webhook_queue = None
            except FileNotFoundError:
                log("ngrok not found, falling back to polling. Install ngrok or set WEBHOOK_URL manually.")
                use_webhook = False
                webhook_queue = None
            except Exception as _e:
                log(f"Webhook setup error: {_e}, falling back to polling")
                use_webhook = False
                webhook_queue = None
        except Exception as _e:
            log(f"Webhook import error: {_e}, falling back to polling")
            use_webhook = False
            webhook_queue = None
    if not use_webhook:
        try:
            c = await get_http()
            await c.post(f"{TG_API}/deleteWebhook", timeout=10)
        except Exception as _e:
            log(f"poll loop error: {_e}")
            pass
    try:
        loop = asyncio.get_running_loop()
        if os.name == "nt":
            for sig in (2, 15):
                try:
                    loop.add_signal_handler(sig, _handle_signal)
                except NotImplementedError:
                    break
        else:
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, _handle_signal)
    except Exception:
        log("Signal handler registration not supported on this platform")
    log("Bot started")

    await gateway.start_worker()
    if bf:
        _t1 = asyncio.create_task(bf.run_scheduler_loop(smart_call, send))
        _t1.add_done_callback(_task_done)
        _t2 = asyncio.create_task(bf.run_reminder_loop(send))
        _t2.add_done_callback(_task_done)
        _t6 = asyncio.create_task(bf.run_page_monitor_loop(send))
        _t6.add_done_callback(_task_done)
        bf.init_plugins()
    _t3 = asyncio.create_task(auto_version_checker())
    _t3.add_done_callback(_task_done)
    _t4 = asyncio.create_task(run_startup_check())
    _t4.add_done_callback(_task_done)
    _t5 = asyncio.create_task(_cache_cleanup())
    _t5.add_done_callback(_task_done)

    if user_memory:
        log("AI Stack memory initialized")
        load_memory()
    load_token_usage()
    load_experimental()
    load_bridges()
    import gc; gc.collect()

    token_warn = sum(1 for cfg in bridges.values() for t in cfg.get("targets", []) if t.get("bot_token"))
    if token_warn:
        log(f"[security] WARNING: {token_warn} bridge bot token(s) stored in plaintext in bridges.json")

    if is_experimental_enabled("plugin-system"):
        bf.init_plugins_from_dir()

    async def keepalive_loop():
        while True:
            try:
                await asyncio.sleep(120)
                c = await get_http()
                await c.get(f"{TG_API}/getMe", timeout=10)
            except Exception:
                pass

    _tk = asyncio.create_task(keepalive_loop())
    _tk.add_done_callback(_task_done)

    while True:
        if _shutdown_event.is_set():
            log("Shutting down gracefully...")
            break
        try:
            updates = []
            if use_webhook and webhook_queue:
                try:
                    u = await asyncio.wait_for(webhook_queue.get(), timeout=1.0)
                    updates = [u]
                except asyncio.TimeoutError:
                    pass
            else:
                updates = await poll()
            for u in updates:
                if _shutdown_event.is_set():
                    break
                msg = u.get("message")
                join_req = u.get("chat_join_request")
                if join_req:
                    jchat = join_req["chat"]["id"]
                    juser = join_req["from"]["id"]
                    jname = join_req["from"].get("first_name", "User")
                    if guard_mod:
                        guard = guard_mod.get_guardian()
                        if guard.is_enabled(jchat):
                            approved, reason = guard.evaluate_join_request(jchat, join_req.get("from", {}))
                            guard.log_action(jchat, "join_request" if approved else "join_rejected", juser, f"{jname}: {reason or 'approved'}")
                            if approved:
                                try:
                                    c = await get_http()
                                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                                    await c.post(f"https://api.telegram.org/bot{bot_token}/approveChatJoinRequest",
                                        json={"chat_id": jchat, "user_id": juser}, timeout=10)
                                    cfg = guard.get_chat(jchat)
                                    welcome = cfg.get("welcome", "")
                                    if welcome:
                                        wtext = welcome.replace("{name}", jname)
                                        await c.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                            json={"chat_id": jchat, "text": wtext, "parse_mode": "HTML"}, timeout=10)
                                except Exception:
                                    pass
                        else:
                            pass
                    continue
                poll_ans = u.get("poll_answer")
                if poll_ans and pollplus_mod:
                    pp = pollplus_mod.get_poll_plus()
                    pid = poll_ans["poll_id"]
                    uid_a = poll_ans["user"]["id"]
                    opts = poll_ans.get("option_ids", [])
                    pp.record_answer(pid, uid_a, opts)
                    continue
                if not msg: continue
                mid, cid = msg.get("message_id"), msg["chat"]["id"]
                if mid and (cid, mid) in processed: continue
                if mid: processed.add((cid, mid))
                if len(processed) > 1000:
                    processed = set(list(processed)[-500:])
                new_members = msg.get("new_chat_members", [])
                if new_members:
                    for nm in new_members:
                        if nm.get("is_bot"):
                            if nm.get("id") == int(os.environ.get("TELEGRAM_BOT_TOKEN", "0").split(":")[0]) if ":" in os.environ.get("TELEGRAM_BOT_TOKEN", "") else False:
                                await send(chat, "🤖 Bot added to group! Use /guard on to enable AI guardian.")
                            continue
                        if guard_mod:
                            guard = guard_mod.get_guardian()
                            if guard.is_enabled(cid):
                                cfg = guard.get_chat(cid)
                                welcome = cfg.get("welcome", "")
                                if welcome:
                                    nm_name = nm.get("first_name", "User")
                                    wtext = welcome.replace("{name}", nm_name)
                                    try:
                                        c = await get_http()
                                        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                                        await c.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                            json={"chat_id": cid, "text": wtext, "parse_mode": "HTML"}, timeout=10)
                                    except Exception:
                                        pass
                                guard.log_action(cid, "member_joined", nm.get("id", 0), nm.get("first_name", "?"))
                                if an_mod and is_experimental_enabled("analytics-dashboard"):
                                    try:
                                        an_mod.get_analytics().track_member_join(cid, nm.get("id", 0))
                                    except Exception:
                                        pass
                    continue
                if msg.get("from", {}).get("is_bot"):
                    continue
                chat, uid = msg["chat"]["id"], msg["from"]["id"]
                # Handle Mini App web_app_data
                web_app_data = msg.get("web_app_data")
                if web_app_data and ma_mod and is_experimental_enabled("mini-apps"):
                    try:
                        wa_data = web_app_data.get("data", "")
                        ma_mod.get_mini_app().record_web_app_data(uid, chat, wa_data)
                        if wa_data.startswith("/"):
                            text = wa_data
                        else:
                            await send(chat, f"📱 Received from Mini App: {wa_data[:500]}")
                            continue
                    except Exception:
                        pass
                await typing(chat)
                resolve_state(chat)
                text = msg.get("text", "")
                now = time.time()
                _prev = last_user_msg.get(uid, {})
                if _prev and now - _prev.get("t", 0) < 10 and _prev.get("text") == text:
                    continue
                if uid in last_user_msg:
                    _last_msg_times[uid] = last_user_msg[uid].get("t", now)
                else:
                    _last_msg_times[uid] = now
                last_user_msg[uid] = {"t": now, "text": text}
                if an_mod and is_experimental_enabled("analytics-dashboard"):
                    try:
                        an_mod.get_analytics().track_message(chat, uid, text, is_command=text.startswith("/"))
                    except Exception:
                        pass
                photo = msg.get("photo")
                voice = msg.get("voice")
                document = msg.get("document")
                photo_file_id = None
                if photo:
                    photo_file_id = photo[-1]["file_id"]
                    caption = msg.get("caption", "")
                    text = f"/vision {caption}" if caption else "/vision describe"
                elif voice:
                    await typing(chat)
                    vmode = bf.get_voice_mode(chat)
                    transcribed = await bf.voice_to_text(voice["file_id"])
                    if not transcribed or transcribed == "/voice_error":
                        await send(chat, "Could not transcribe audio.")
                        continue
                    text = transcribed
                    if vmode in ("conversation", "happy", "sad", "angry", "excited", "calm"):
                        await send(chat, f"Transcribed: {text[:200]}")
                        uid_key = str(uid)
                        sessions.setdefault(uid_key, [])
                        sessions[uid_key].append({"role": "user", "content": text})
                        reply = await smart_call(sessions[uid_key][-10:], active_provider)
                        sessions[uid_key].append({"role": "assistant", "content": reply})
                        emotion = vmode if vmode != "conversation" else "neutral"
                        await send(chat, reply[:1500])
                        tts_ok = await bf.text_to_speech(reply, chat, emotion=emotion)
                        if tts_ok:
                            await send(chat, "🎙️ X-Phone voice reply sent. Say something else or /voice off to stop.")
                        continue
                    await send(chat, f"Transcribed: {text[:300]}")
                    tts_ok = await bf.text_to_speech(text, chat)
                    continue
                elif document:
                    file_id = document["file_id"]
                    fname = document.get("file_name", "document.bin")
                    ext = (fname or "").lower()
                    if ext.endswith((".csv", ".xlsx", ".xls")):
                        rows, summary = await bf.parse_spreadsheet(file_id, fname)
                        if rows:
                            bf.doc_db.add_document(fname, str(rows[:50]))
                            await send(chat, f"ðŸ“Š Spreadsheet '{fname}' loaded.\n{summary}")
                            if len(rows) > 5:
                                await send(chat, f"Ask questions with /ask <question>, or use /data query <sql-like expression>")
                        else:
                            await send(chat, f"Could not parse '{fname}': {summary}")
                    else:
                        extracted = await bf.extract_text_from_file(file_id, fname)
                        if extracted and len(extracted) > 20:
                            chunks = bf.doc_db.add_document(fname, extracted)
                            await send(chat, f"ðŸ“„ Document '{fname}' indexed ({chunks} chunks, {len(extracted)} chars).\nAsk questions with /ask <question>")
                        else:
                            await send(chat, f"Could not extract text from '{fname}'.")
                    continue

                location = msg.get("location")
                if location and loc_mod and is_experimental_enabled("location-distance"):
                    try:
                        ld = loc_mod.get_location()
                        ld.record_user_location(chat, uid, location["latitude"], location["longitude"])
                    except Exception:
                        pass

                if guard_mod and text:
                    guard = guard_mod.get_guardian()
                    v = guard.check_message(chat, text)
                    if v:
                        is_cmd = text.startswith("/")
                        if not is_cmd:
                            actions = []
                            for vtype, vmsg in v:
                                guard.log_action(chat, f"mod_{vtype}", uid, vmsg[:100])
                                if vtype == "ban":
                                    actions.append(f"⛔ {vmsg}")
                                else:
                                    actions.append(f"⚠️ {vmsg}")
                            if actions:
                                try:
                                    await bot_delete_message(chat, mid)
                                except Exception:
                                    pass
                                await send(chat, f"Guardian mod:\n" + "\n".join(actions[:3]))

                parts = text.split()
                cmd = parts[0].lower() if parts else ""

                log(f"Msg from {uid}: {text[:50]}")
                if not text: continue
                log(f"Processing: {cmd}")

                is_owner = uid == OWNER_ID
                is_admin = uid in admins
                is_mod = uid in mods

                if not cmd.startswith("/") and active_topic == "v1":
                    text_lower = text.lower()
                    if any(kw in text_lower for kw in CYBERDECK_KEYWORDS):
                        active_topic = "v2"
                        log(f"Auto-switched to v2 (cyberdeck) for user {uid}")
                        await send(chat, "Detected cyberdeck topic. Switched to v2 (Cyberdeck Builder). Use /v1 to switch back.")

                if cmd == "/start":
                    active_agent = "orchestrator"
                    active_provider = "groq"
                    active_team = None
                    active_arch = "single"
                    effort = "medium"
                    thinking_mode = "off"
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    lines = [
                        f"OpenCode Bot v{BOT_VERSION}",
                        f"  Agents: {len(AGENTS)}  Providers: {len(PROVIDERS)}  Skills: 90+",
                        "",
                        "Commands:",
                        "  /agents — List agents",
                        "  /agent <name> — Switch agent",
                        "  /skills — List available skills from repo catalog",
                        "  /repo — List providers",
                        "  /repo <name> — Switch provider",
                        "  /arch — List architectures",
                        "  /arch <name> — Switch architecture",
                        "  /mode — List modes (chat/team/autonomous)",
                        "  /mode <name> — Switch mode",
                        "  /teams — List teams",
                        "  /createteam <desc> — AI creates a team",
                        "  /putteam <name> <a1> <a2>... — Create/update team",
                        "  /useteam <name> — Activate a team",
                        "  /stopteam — Deactivate team mode",
                        "  /tools — List available tools",
                        "  /effort — Show current effort level",
                        "  /low|/normal|/medium|/high|/superhigh — Set effort",
                        "  /thinking off|extended|adaptive — Thinking mode",
                        "  /help — Help",
                        "  /status — Current agent + provider",
                        "  /providers — Provider health dashboard",
                        "  /reset — Reset your personal settings",
                        "  /myrole — Your role",
                        "  /clear — Clear session",
                        "  /premadeskills — Pre-made skill teams",
                        "  /routes — Provider health",
                        "  /vision — Analyze images with AI",
                        "  /draw — Generate images from text",
                        "  /schedule — Schedule recurring AI tasks",
                        "  /export — Export chat history (json/md)",
                        "  /doc — List indexed documents",
                        "  /ask — Query uploaded documents",
                        "  /context — Show current auto-context",
                        "  /search — Web search via DuckDuckGo",
                        "  /youtube — Get YouTube transcript/summary",
                        "  /youtube_search — Search YouTube videos by keyword",
                        "  /tiktok — Search TikTok videos by keyword",
                        "  /reddit — Search Reddit discussions",
                        "  /hn — Search Hacker News",
                        "  /social — Search Reddit + HN + Medium at once",
                        "  /github_search — Search GitHub repos by keyword",
                        "  /analyze — Deep analyze a GitHub repo (README, structure, languages)",
                        "  /cron — Schedule recurring AI tasks",
                        "  /monitor — Watch web pages for changes",
                        "  /memory — View/search your persistent memory log",
                        "  /run — Execute code in sandbox (python/js)",
                        "  /fetch — Fetch and summarize any URL",
                        "  /remind — Set a reminder",
                        "  /translate — Translate text",
                        "  /qr — Encode/decode QR codes",
                        "  /stats — Your usage statistics",
                        "  /data — Query spreadsheets",
                        "  /plugin — Dynamic plugin system",
                        "  /version — Show version and changelog",
                        "  /stack — 2026 AI Infrastructure Reference",
                        "  /webgateway — Web AI Gateway status + URL",
                        "  /weather <city> — Weather forecast",
                        "  /dailydigest — Daily summary",
                        "  /experimental — Experimental features",
                        "  /miniapp — Telegram Mini App dashboard",
                        "",
                        "Reverse-Engineered Tools:",
                        "  /9router — Universal AI Gateway (upstream)",
                        "  /vansrouter — Local 9Router fork",
                        "  /omniroute — Fork of 9Router (290+ providers)",
                        "  /openclaw — AI multi-tool orchestration CLI",
                        "  /blackbox — Multi-model AI provider",
                        "  /odysseus — Self-hosted AI workspace",
                        "  /hermes — Hermes Agent (Nous Research self-improving AI)",
                        "  /obsidian — Obsidian AI CLI + MCP integration",
                    ]
                    if is_owner or is_admin or is_mod:
                        lines += [
                            "",
                            "Admin:",
                            "  /addprovider — Add a provider",
                            "  /createagent — AI creates an agent",
                            "  /repair — Reset provider health",
                            "  /backup — Backup all data",
                            "  /restore — Restore from backup",
                        ]
                    if is_owner:
                        lines += [
                            "",
                            "Owner:",
                        "  /addadmin <id> — Add admin",
                        "  /removeadmin <id> — Remove admin",
                        "  /adminlist — List admins",
                        ]
                    await send(chat, "\n".join(lines))

                elif cmd in ("/v1", "/v2"):
                    old_topic = active_topic
                    active_topic = cmd[1:]
                    topic_names = {"v1": "General AI (opencode-bot)", "v2": "Cyberdeck Builder (cyberdeck-bot)"}
                    if active_topic == "v2":
                        lines = [
                            f"Switched to {topic_names[active_topic]}",
                            "",
                            "Cyberdeck mode active. I'll help with:",
                            "  - Component selection (SBCs, displays, keyboards, power)",
                            "  - Build planning and BOM generation",
                            "  - Enclosure design and 3D printing",
                            "  - Wiring, soldering, and assembly",
                            "  - Compatibility checking",
                            "  - Troubleshooting and upgrades",
                            "",
                            "Commands: /build, /bom, /compat, /ideas, /search,",
                            "  /tutorial, /upgrade, /flaws, /pack, /career, /dashboard,",
                            "  /specs, /cb, /peripherals, /antenna, /battery,",
                            "  /forensics, /testeq, /hamradio, /palette, /material, /thermal",
                            "",
                            "Switch back: /v1",
                        ]
                    else:
                        lines = [
                            f"Switched to {topic_names[active_topic]}",
                            "",
                            "General AI mode. All commands available.",
                            "Switch to cyberdeck mode: /v2",
                        ]
                    await send(chat, "\n".join(lines))

                elif cmd == "/help":
                    categories = [
                        ("TOPIC SWITCHER", [
                            "/v1 — General AI mode (opencode-bot)",
                            "/v2 — Cyberdeck Builder mode (cyberdeck-bot)",
                            "Auto-detect: cyberdeck keywords auto-switch to v2",
                        ]),
                        ("CHAT", [
                            "/start — Reset session",
                            "/agent <name> — Switch agent",
                            "/agents — List agents",
                            "/repo — List / switch AI provider",
                            "/providers — Provider health dashboard",
                            "/reset — Reset your personal settings",
                            "/status — Current agent + provider",
                            "/multi start <p1> [p2] [rounds=2] — Talk to 2 AIs at once",
                            "/multi stop — End multi-AI session",
                            "/clear — Clear history",
                            "/remember <fact> — Store a fact in memory",
                            "/recall <query> — Search your memories",
                        ]),
                        ("MODES", [
                            "/mode — Toggle chat / team / autonomous",
                            "/arch — Switch architecture (single, sequential, parallel, supervisor, reflection…)",
                            "/teams — List teams",
                            "/createteam <desc> — AI builds a team",
                            "/putteam <n> <a1> <a2>... — Create/update team",
                            "/useteam <name> — Activate team",
                            "/stopteam — Deactivate team",
                            "/tools — Available tools",
                            "/effort — Show effort level",
                            "/low|/normal|/medium|/high|/superhigh — Set effort",
                            "/thinking off|extended|adaptive — Thinking mode",
                        ]),
                        ("MEDIA", [
                            "/vision <prompt> — Analyze image (reply to photo)",
                            "/draw <prompt> — Generate image",
                            "/qr encode <text> — Generate QR",
                            "/qr decode — Decode QR from replied photo",
                        ]),
                        ("RESEARCH", [
                            "/search <query> — Web search + AI summary",
                            "/youtube <url> — Transcript + summary",
                            "/youtube_search <query> — Search YouTube videos",
                            "/tiktok <query> — Search TikTok videos",
                            "/reddit <query> — Search Reddit discussions",
                            "/hn <query> — Search Hacker News",
                            "/social <query> — Search Reddit + HN + Medium at once",
                            "/github_search <query> — Search GitHub repos by stars",
                            "/analyze <repo_url> — Deep analyze GitHub repo",
                            "/fetch <url> — Fetch & summarize any URL",
                            "/translate <src>:<tgt> <text> — Translate",
                            "/run python|js <code> — Sandboxed code exec",
                            "/weather <city> — Weather forecast",
                        ]),
                        ("DATA", [
                            "/doc — List indexed docs",
                            "/ask <question> — Query uploaded docs",
                            "/context — Show auto-context",
                            "/data list|query — Spreadsheet ops",
                            "/export json|md — Export chat",
                            "/tokens — FreeTokenFaucet balance",
                            "/tokens set <amount> — Set balance",
                            "/tokens claim <amount> — Record daily claim",
                            "/dailydigest — Daily summary with stats",
                        ]),
                        ("AUTOMATION", [
                            "/schedule add|list|remove — Recurring AI tasks",
                            "/cron add|list|remove — Schedule recurring AI prompts",
                            "/monitor add|list|remove — Watch web pages for changes",
                            "/remind <duration> <msg> — Reminder",
                            "/digest — Summarize conversation",
                            "/routine create|list|show|delete|run — Prompt chaining workflows",
                            "/plugin load|list — Load/list plugins",
                            "/memory stats|search|clear — Persistent memory log",
                        ]),
                        ("INTEGRATIONS", [
                            "/n8n — Trigger n8n webhook",
                            "/n8n-status — n8n health check",
                            "/n8n-logs — Recent executions",
                            "/github — Repo info, issues, PRs",
                            "/gmail — Read Gmail inbox",
                            "/sheets — Read Google Sheets",
                            "/notion — Search / query Notion",
                            "/crypto — CoinGecko price lookup",
                        ]),
                        ("SYSTEM", [
                            "/routes — Provider health",
                            "/gateway — Gateway stats + queue",
                            "/version — Show version and changelog",
                            "/stack — 2026 AI Infrastructure Reference (10 layers)",
                            "/stackstatus — Live status of all 10 AI stack layers",
                            "/webgateway — Web gateway status + admin dashboard",
                            "/9router — Universal AI Gateway (upstream)",
                            "/vansrouter — Local 9Router fork (port 3003)",
                            "/omniroute — Fork of 9Router (290+ providers)",
                            "/openclaw — AI multi-tool orchestration CLI",
                            "/blackbox — Multi-model AI provider",
                            "/odysseus — Self-hosted AI workspace",
                            "/hermes — Hermes Agent (Nous Research self-improving AI)",
                            "/obsidian — Obsidian AI CLI + MCP integration",
                            "/toolfk — 200+ free utilities",
                            "/synoxcloud — 434 tools + 52 AI models",
                            "/stats — Your usage stats",
                            "/myrole — Your ID + role",
                            "/profile save|load|show|reset — Persist your settings",
                            "/experimental — Experimental features (enable/disable)",
                        ]),
                        ("MODERATION", [
                            "/addmod <id> — Add moderator (owner/admin)",
                            "/removemod <id> — Remove moderator",
                            "/modlist — List moderators",
                            "/checkrole <id> — Check user role",
                        ]),
                    ]
                    lines = []
                    for title, items in categories:
                        lines.append(f"╌ {title} ╌")
                        for item in items:
                            lines.append(f"  {item}")
                        lines.append("")
                    if is_owner or is_admin or is_mod:
                        lines.append("╌ ADMIN ╌")
                        lines.append("  /addprovider <name> <model> <url> <key> — Add provider")
                        lines.append("  /agentprovider <agent> <url> <key> <model> — Agent-specific provider")
                        lines.append("  /createagent <desc> — AI creates agent")
                        lines.append("  /addprompt <agent> <prompt> — Set agent prompt")
                        lines.append("  /repair — Reset provider health")
                        lines.append("  /backup — Backup all data to zip")
                        lines.append("  /restore — Restore from backup (reply to zip)")
                        lines.append("  /pyrit <mode> <objective> — Red-team attack")
                    if is_owner:
                        lines.append("  /addadmin <id> — Add admin")
                        lines.append("  /removeadmin <id> — Remove admin")
                        lines.append("  /adminlist — List admins")
                    lines.append("")
                    lines.append(f"Agent: {active_agent}  |  Provider: {active_provider} ({PROVIDERS[active_provider]['model']})")
                    lines.append(f"Mode: {active_mode}  |  Arch: {active_arch}  |  Team: {active_team or 'none'}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/agents":
                    lines = [f"Available agents ({len(AGENTS)}):"]
                    for name, a in sorted(AGENTS.items()):
                        m = " << active" if name == active_agent else ""
                        lines.append(f"  {name}{m} — {a['desc']}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/myrole":
                    if uid == OWNER_ID:
                        role = "owner"
                    elif uid in admins:
                        role = "admin"
                    elif uid in mods:
                        role = "mod"
                    else:
                        role = "user"
                    await send(chat, f"Your ID: {uid}\nRole: {role}")

                elif cmd == "/profile":
                    sub = parts[1] if len(parts) > 1 else "show"
                    _pd = {}
                    if os.path.exists(SESSIONS_FILE):
                        try:
                            with open(SESSIONS_FILE, encoding="utf-8") as _f: _pd = json.load(_f)
                        except Exception:
                            pass
                    profiles = _pd.get("profiles", {})
                    if sub == "save":
                        profiles[str(uid)] = {"agent": active_agent, "provider": active_provider, "effort": effort, "thinking": thinking_mode, "arch": active_arch}
                        _pd["profiles"] = profiles
                        _atomic_save(SESSIONS_FILE, _pd)
                        await send(chat, "Profile saved.")
                    elif sub == "load":
                        p = profiles.get(str(uid))
                        if not p:
                            await send(chat, "No saved profile.")
                            continue
                        active_agent = p.get("agent", active_agent)
                        active_provider = p.get("provider", active_provider)
                        effort = p.get("effort", effort)
                        thinking_mode = p.get("thinking", thinking_mode)
                        active_arch = p.get("arch", active_arch)
                        await send(chat, f"Profile loaded: agent={active_agent}, provider={active_provider}, effort={effort}")
                    elif sub == "reset":
                        profiles.pop(str(uid), None)
                        _pd["profiles"] = profiles
                        _atomic_save(SESSIONS_FILE, _pd)
                        await send(chat, "Profile reset.")
                    else:
                        p = profiles.get(str(uid), {})
                        if p:
                            await send(chat, f"Saved profile: agent={p.get('agent')}, provider={p.get('provider')}, effort={p.get('effort')}, thinking={p.get('thinking')}, arch={p.get('arch')}")
                        else:
                            await send(chat, "No saved profile. Use /profile save to create one.")

                elif cmd == "/checkrole":
                    if len(parts) < 2:
                        await send(chat, "Usage: /checkrole <user_id>")
                        continue
                    try:
                        target = int(parts[1])
                        if target == OWNER_ID:
                            role = "owner"
                        elif target in admins:
                            role = "admin"
                        elif target in mods:
                            role = "mod"
                        else:
                            role = "user"
                        await send(chat, f"User {target}: {role}")
                    except Exception:
                        await send(chat, "Invalid ID.")

                elif cmd == "/agent":
                    _multi_agent_subs = {"status", "list", "info", "run", "pipeline", "parallel", "crew", "debate", "handoff", "swarm", "flow"}
                    sub = parts[1].lower() if len(parts) > 1 else ""
                    if sub in _multi_agent_subs or (not sub and len(parts) == 1):
                        if not is_experimental_enabled("multi-agent"):
                            await send(chat, "Multi-Agent System is disabled. Use /experimental enable multi-agent")
                            continue
                        try:
                            from bot_to_bot_agent import get_manager, format_system_status, format_agent_status
                            manager = get_manager()
                            if sub == "status" or not sub:
                                status = manager.get_status()
                                await send(chat, format_system_status(status))
                            elif sub == "list":
                                agents = manager.list_available_agents()
                                lines = ["🤖 **Available Agents:**\n"]
                                for aid in agents:
                                    astatus = manager.get_agent_status(aid)
                                    if astatus:
                                        emoji = "✅" if astatus.get('enabled') else "❌"
                                        lines.append(f"{emoji} `{aid}` — {astatus.get('name', 'Unknown')}")
                                await send(chat, "\n".join(lines))
                            elif sub == "info":
                                if len(parts) < 3:
                                    await send(chat, "Usage: /agent info <agent_id>")
                                else:
                                    aid = parts[2]
                                    astatus = manager.get_agent_status(aid)
                                    if astatus:
                                        await send(chat, format_agent_status(astatus))
                                    else:
                                        await send(chat, f"Agent '{aid}' not found.")
                            elif sub == "run":
                                if len(parts) < 3:
                                    await send(chat, "Usage: /agent run <message>\nRoutes request through triage to specialist agent.")
                                else:
                                    message = " ".join(parts[2:])
                                    await send(chat, "🤖 Processing through agent system...")
                                    result = await manager.process_request(message, uid)
                                    routing = result.get('routing', 'unknown')
                                    agent_result = result.get('result', {})
                                    response = f"🔀 **Routed to:** {routing}\n\n"
                                    if isinstance(agent_result, dict):
                                        for k, v in agent_result.items():
                                            if k != 'error':
                                                response += f"**{k}:** {str(v)[:200]}\n"
                                    else:
                                        response += str(agent_result)[:500]
                                    await send(chat, response)
                            elif sub == "pipeline":
                                if len(parts) < 4:
                                    await send(chat, "Usage: /agent pipeline <agent1,agent2,...> <message>\nRun sequential pipeline.")
                                else:
                                    agent_chain = [a.strip() for a in parts[2].split(",")]
                                    message = " ".join(parts[3:])
                                    await send(chat, f"🔄 Running pipeline: {' → '.join(agent_chain)}")
                                    result = await manager.run_pipeline(message, agent_chain)
                                    final = result.get('final_result', {})
                                    response = f"✅ **Pipeline Complete**\nChain: {' → '.join(agent_chain)}\n\n"
                                    if isinstance(final, dict):
                                        for k, v in final.items():
                                            response += f"**{k}:** {str(v)[:200]}\n"
                                    else:
                                        response += str(final)[:500]
                                    await send(chat, response)
                            elif sub == "parallel":
                                if len(parts) < 4:
                                    await send(chat, "Usage: /agent parallel <agent1,agent2,...> <message>\nRun agents in parallel.")
                                else:
                                    agent_ids = [a.strip() for a in parts[2].split(",")]
                                    message = " ".join(parts[3:])
                                    await send(chat, f"⚡ Running parallel: {', '.join(agent_ids)}")
                                    result = await manager.run_parallel(message, agent_ids)
                                    results = result.get('results', {})
                                    response = f"✅ **Parallel Complete**\nAgents: {', '.join(agent_ids)}\n\n"
                                    for aid, res in results.items():
                                        response += f"**{aid}:** {str(res)[:150]}\n"
                                    await send(chat, response)
                            elif sub == "crew":
                                if len(parts) < 3:
                                    crews = manager.crew.list_crews()
                                    if crews:
                                        lines = ["👥 **Crews:**\n"]
                                        for c in crews:
                                            lines.append(f"  `{c['id']}` — {c['name']} ({c['members']} members, {c['process']})")
                                        await send(chat, "\n".join(lines))
                                    else:
                                        await send(chat, "No crews defined. Use Python to create one:\n`manager.crew.create_crew(CrewConfig(...))`")
                                else:
                                    crew_action = parts[2].lower()
                                    if crew_action == "run" and len(parts) >= 5:
                                        cid = parts[3]
                                        task = " ".join(parts[4:])
                                        await send(chat, "👥 Running crew...")
                                        result = await manager.run_crew(cid, task, uid)
                                        response = f"✅ **Crew Complete**\n"
                                        for r in result.get("results", []):
                                            response += f"  `{r['agent_id']}` ({r['role']}): {str(r.get('result', {}))[:150]}\n"
                                        if result.get("delegations"):
                                            response += f"\n  Delegations: {len(result['delegations'])}"
                                        if result.get("final_output"):
                                            response += f"\n\n**Final:** {str(result['final_output'])[:300]}"
                                        await send(chat, response)
                                    else:
                                        await send(chat, "Usage: /agent crew run <crew_id> <task>")
                            elif sub == "debate":
                                if len(parts) < 5:
                                    debates = manager.debate.list_debates()
                                    if debates:
                                        lines = ["🗣️ **Recent Debates:**\n"]
                                        for d in debates:
                                            lines.append(f"  `{d['id']}` — {d['topic']} ({d['rounds']} rounds)")
                                        await send(chat, "\n".join(lines))
                                    else:
                                        await send(chat, "Usage: /agent debate <topic> <proponent> <opponent> [neutral] [judge] [rounds]")
                                else:
                                    topic = parts[2]
                                    proponent = parts[3]
                                    opponent = parts[4]
                                    neutral = parts[5] if len(parts) > 5 and parts[5] not in ("2", "3", "4", "5") else None
                                    judge = parts[6] if len(parts) > 6 and parts[6] not in ("2", "3", "4", "5") else None
                                    rounds = 3
                                    for p in parts[2:]:
                                        if p.isdigit() and 1 <= int(p) <= 10:
                                            rounds = int(p)
                                    await send(chat, f"🗣️ Starting debate: {topic}")
                                    result = await manager.run_debate(topic, proponent, opponent, neutral, judge, rounds, uid)
                                    response = f"🗣️ **Debate: {result.get('topic', topic)}**\nRounds: {result.get('total_rounds', 0)}\n\n"
                                    for r in result.get("rounds", []):
                                        role_emoji = {"proponent": "🟢", "opponent": "🔴", "neutral": "⚪", "judge": "⚖️"}.get(r["role"], "•")
                                        response += f"{role_emoji} **R{r['round']}** {r['role']}: {r['argument'][:200]}\n"
                                    if result.get("judgment"):
                                        response += f"\n⚖️ **Judgment:** {str(result['judgment'])[:300]}"
                                    await send(chat, response)
                            elif sub == "handoff":
                                if len(parts) < 4:
                                    stats = manager.handoff.get_stats()
                                    rules = manager.handoff.handoff_rules
                                    lines = [f"🔄 **Handoff System** ({stats['total_rules']} rules, {stats['total_handoffs']} performed)\n"]
                                    for r in rules:
                                        lines.append(f"  `{r.from_agent}` → `{r.to_agent}` ({r.strategy.value})")
                                    await send(chat, "\n".join(lines))
                                else:
                                    from_ag = parts[2]
                                    to_ag = parts[3]
                                    task = " ".join(parts[4:]) if len(parts) > 4 else "test handoff"
                                    result = await manager.run_handoff(from_ag, to_ag, task)
                                    response = f"🔄 **Handoff:** `{from_ag}` → `{to_ag}`\n"
                                    if isinstance(result, dict):
                                        for k, v in result.items():
                                            response += f"  **{k}:** {str(v)[:150]}\n"
                                    await send(chat, response)
                            elif sub == "swarm":
                                if len(parts) < 4:
                                    status = manager.swarm.get_status()
                                    lines = [f"🐝 **Swarm Status**\nAgents: {status['swarm_agents']}, Active: {status['active_swarms']}"]
                                    for aid, load in status.get("agent_loads", {}).items():
                                        lines.append(f"  `{aid}` — load: {load:.1f}")
                                    await send(chat, "\n".join(lines))
                                else:
                                    caps = [c.strip() for c in parts[2].split(",")]
                                    task = " ".join(parts[3:])
                                    max_a = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 3
                                    await send(chat, f"🐝 Swarm executing with capabilities: {', '.join(caps)}")
                                    result = await manager.run_swarm(task, caps, max_a, uid)
                                    response = f"🐝 **Swarm Complete**\nAgents: {', '.join(result.get('selected_agents', []))}\n"
                                    consensus = result.get("consensus", {})
                                    response += f"Consensus: {consensus.get('strategy', 'none')}\n"
                                    for pr in result.get("peer_results", []):
                                        response += f"  `{pr['agent_id']}`: {str(pr.get('result', {}))[:150]}\n"
                                    await send(chat, response)
                            elif sub == "flow":
                                if len(parts) < 3:
                                    flows = manager.flow.list_flows()
                                    if flows:
                                        lines = ["📊 **Flows:**\n"]
                                        for f in flows:
                                            lines.append(f"  `{f['id']}` — {f['name']} ({f['nodes']} nodes)")
                                        await send(chat, "\n".join(lines))
                                    else:
                                        await send(chat, "No flows defined.")
                                elif parts[2] == "run" and len(parts) >= 4:
                                    fid = parts[3]
                                    data = {"message": " ".join(parts[4:])} if len(parts) > 4 else {}
                                    await send(chat, f"📊 Running flow...")
                                    result = await manager.run_flow(fid, data, uid)
                                    response = f"📊 **Flow: {result.get('flow_name', fid)}**\nStatus: {result.get('status')}\n"
                                    response += f"Path: {' → '.join(result.get('path', []))}\n"
                                    for nid, nr in result.get("node_results", {}).items():
                                        response += f"  `{nid}`: {str(nr)[:150]}\n"
                                    if result.get("error"):
                                        response += f"\n❌ Error: {result['error']}"
                                    await send(chat, response)
                                else:
                                    await send(chat, "Usage: /agent flow [run <flow_id> <message>]")
                            else:
                                await send(chat, "🤖 **Multi-Agent System v3.7.0**\n\n"
                                    "**Basic:**\n"
                                    "  /agent status — System status\n"
                                    "  /agent list — List all agents\n"
                                    "  /agent info <id> — Agent details\n"
                                    "  /agent run <msg> — Route request\n"
                                    "  /agent pipeline <a1,a2,...> <msg> — Sequential\n"
                                    "  /agent parallel <a1,a2,...> <msg> — Parallel\n\n"
                                    "**Advanced:**\n"
                                    "  /agent crew [run <id> <task>] — Crew execution\n"
                                    "  /agent debate <topic> <prop> <opp> [neutral] [judge] [rounds]\n"
                                    "  /agent handoff [from to] — Handoff system\n"
                                    "  /agent swarm [caps] <task> — Swarm execution\n"
                                    "  /agent flow [run <id> <msg>] — Flow execution")
                        except Exception as e:
                            await send(chat, f"Agent system error: {str(e)[:200]}")
                    else:
                        if len(parts) < 2:
                            await send(chat, f"Usage: /agent <name>. Use /agents to list all.")
                            continue
                        name = sub
                        if name not in AGENTS:
                            await send(chat, f"Unknown agent. Use /agents to see all.")
                            continue
                        a = AGENTS[name]
                        active_agent = name
                        set_user_pref(chat, "active_agent", name)
                        sessions.pop(uid, None)
                        await send(chat, f"Agent: {name} — {a['desc']}\n\nPrompt: {a['prompt']}")
                        ap = AGENT_PROVIDERS.get(name)
                        if not ap or not _is_configured(ap.get("key", "")):
                            await send(chat, f"This agent needs its own API provider. Use:\n/agentprovider {name} <url> <key> <model>\nExample: /agentprovider {name} https://api.example.com/v1/chat/completions sk-abc123 gpt-4o")
                        await send(chat, f"Great choice! Do you wanna set token usage?\nUse /low /normal /medium /high /superhigh\nCurrent: {get_effort(chat)} ({EFFORT_LEVELS[get_effort(chat)]['desc']})")

                elif cmd == "/video":
                    if vid_mod and vid_mod.HAS_PIL:
                        if len(parts) < 2:
                            styles = ", ".join(vid_mod.get_available_styles())
                            templates = ", ".join(vid_mod.get_meme_templates().keys())
                            await send(chat, f"Usage:\n/video make <title> | <caption> [style] — Generate video frame (styles: {styles})\n/video meme <template> <text1> [text2] — Generate meme (templates: {templates})\n/video virality <text> — Check virality score\n/video styles — List available styles")
                            continue
                        vsub = parts[1].lower()
                        if vsub == "make":
                            rest = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if " | " not in rest:
                                await send(chat, "Usage: /video make <title> | <caption> [style]")
                                continue
                            left, caption = rest.split(" | ", 1)
                            left_p = left.rsplit(" ", 1)
                            style = "tiktok"
                            if len(left_p) > 1 and left_p[1].lower() in vid_mod.STYLES:
                                style = left_p[1].lower()
                                title = left_p[0]
                            else:
                                title = left
                            await typing(chat)
                            buf = vid_mod.create_frame(720, 720, vid_mod.STYLES[style]["bg"], title, caption, style, gradient=True)
                            if buf:
                                c = await bf.get_http()
                                bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                                await c.post(f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                                    files={"photo": ("frame.png", buf.getvalue())},
                                    data={"chat_id": chat, "caption": f"🎬 {title} ({style})"})
                                score, kws = vid_mod.score_virality(caption)
                                if score > 30:
                                    await send(chat, f"📈 Virality score: {score}% — matched: {', '.join(kws) if kws else 'N/A'}")
                            else:
                                await send(chat, "PIL not available for image generation. Install Pillow.")
                        elif vsub == "meme":
                            if len(parts) < 4:
                                await send(chat, "Usage: /video meme <template> <text1> [text2]")
                                continue
                            tmpl = parts[2].lower()
                            text1 = parts[3]
                            text2 = " ".join(parts[4:]) if len(parts) > 4 else ""
                            await typing(chat)
                            buf = vid_mod.create_meme(tmpl, text1, text2)
                            if buf:
                                c = await bf.get_http()
                                bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                                await c.post(f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                                    files={"photo": ("meme.png", buf.getvalue())},
                                    data={"chat_id": chat, "caption": f"Meme: {tmpl}"})
                            else:
                                await send(chat, "Failed to generate meme.")
                        elif vsub == "virality":
                            text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if not text:
                                await send(chat, "Usage: /video virality <text>")
                                continue
                            score, kws = vid_mod.score_virality(text)
                            await send(chat, f"📈 Virality score: {score}%\nMatched keywords: {', '.join(kws) if kws else 'None'}\n{'🔥 Going viral!' if score > 60 else '📊 Needs more punch' if score > 30 else '💤 Low engagement potential'}")
                        elif vsub == "styles":
                            lines = ["Available styles:"]
                            for sname, sdata in vid_mod.STYLES.items():
                                lines.append(f"  {sname} — bg:{sdata['bg']}, text:{sdata['text_color']}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, f"Unknown subcommand: {vsub}")
                    else:
                        name = "video-creator"
                        if name not in AGENTS:
                            await send(chat, "Video creator agent not loaded.")
                            continue
                        a = AGENTS[name]
                        active_agent = name
                        set_user_pref(chat, "active_agent", name)
                        sessions.pop(uid, None)
                        msg = f"Agent: {name} — {a['desc']}\n\nSwitched to OpenMontage video creator."
                        rest = parts[1:] if len(parts) > 1 else []
                        if rest:
                            prompt = " ".join(rest)
                            sessions[uid] = [{"role": "system", "content": a["prompt"]}, {"role": "user", "content": prompt}]
                            msg += f"\n\nPrompt received: {prompt[:200]}"
                        await send(chat, msg)
                        ap = AGENT_PROVIDERS.get(name)
                        if not ap or not _is_configured(ap.get("key", "")):
                            await send(chat, f"This agent needs its own API provider. Use:\n/agentprovider {name} <url> <key> <model>")
                        await send(chat, f"Token usage: /low /normal /medium /high /superhigh (current: {get_effort(chat)} - {EFFORT_LEVELS[get_effort(chat)]['desc']})")
                        await send(chat, "OpenMontage is not installed on this machine yet. I can walk you through installing it — start by saying 'install openmontage' or tell me what video you want to make and I'll guide you through the setup.")

                elif cmd == "/repo":
                    if len(parts) < 2:
                        lines = ["Available providers:"]
                        for k, v in PROVIDERS.items():
                            cfg = _is_configured(v.get("key", ""))
                            m = " << active" if k == active_provider else ""
                            tag = "" if cfg else " [not configured]"
                            lines.append(f"  {k} — {v['model']}{tag}{m}")
                        await send(chat, "\n".join(lines))
                        continue
                    name = parts[1].lower()
                    if name not in PROVIDERS:
                        await send(chat, f"Unknown provider. Use: {', '.join(PROVIDERS.keys())}")
                        continue
                    active_provider = name
                    set_user_pref(chat, "active_provider", name)
                    await send(chat, f"Switched to provider: {name} ({PROVIDERS[name]['model']})")

                elif cmd == "/providers":
                    rows = get_provider_health()
                    s = _cache_stats
                    h = s["hits"]
                    m = s["misses"]
                    total = h + m
                    ratio = f"{h*100//max(total,1)}%" if total else "-"
                    lines = [f"Provider Health ({len(rows)} configured) | Cache: {h}/{m} ({ratio})", ""]
                    for pid, status, latency, cfg in rows:
                        cb_state = circuit_breaker.status(pid)
                        cb_mark = {"closed": "", "open": " [CB OPEN]", "half-open": " [CB PROBE]"}.get(cb_state, "")
                        icon = {"OK": chr(9989), "FAIL": chr(10060), "COOLDOWN": chr(9200), "?": chr(10067)}.get(status, "?")
                        lines.append(f"  {icon} {pid} — {status} ({latency}) [{cfg}]{cb_mark}")
                    lines.append("")
                    lines.append("Use /repo <name> to switch provider.")
                    await send(chat, "\n".join(lines))

                elif cmd == "/status":
                    mode_info = f"Mode: {active_mode} ({MODES[active_mode]['desc']})"
                    arch_info = f"Arch: {active_arch} ({ARCHITECTURES[active_arch]['desc']})"
                    team_info = f"Team: {active_team or 'none'}"
                    ap = AGENT_PROVIDERS.get(active_agent)
                    if ap and _is_configured(ap.get("key", "")):
                        prov_info = f"Provider: {active_agent} (dedicated: {ap['model']})"
                    else:
                        prov_info = f"Provider: {active_provider} ({PROVIDERS[active_provider]['model']})"
                    await send(chat, (
                        f"Agent: {active_agent} — {AGENTS[active_agent]['desc']}\n"
                        f"{prov_info}\n"
                        f"{mode_info}\n{arch_info}\n{team_info}\n"
                        f"Effort: {effort} ({EFFORT_LEVELS[effort]['desc']})\n"
                        f"Thinking: {thinking_mode}"
                    ))

                elif cmd == "/reset":
                    reset_user_state(chat)
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, "Your state reset to defaults.")

                elif cmd == "/clear":
                    _archive_current(uid, chat)
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, "Session cleared and archived.")

                elif cmd == "/archive":
                    _archive_current(uid, chat)
                    await send(chat, "Conversation archived.")

                elif cmd == "/history":
                    convs = load_conversations()
                    chat_key = str(chat)
                    items = convs.get("archives", {}).get(chat_key, [])
                    if not items:
                        await send(chat, "No archived conversations.")
                        continue
                    items = items[-20:]
                    lines = [f"Your conversations ({len(items)}):", ""]
                    for item in reversed(items):
                        ago = int(time.time() - item["time"])
                        if ago < 60: ts = "just now"
                        elif ago < 3600: ts = f"{ago//60}m ago"
                        elif ago < 86400: ts = f"{ago//3600}h ago"
                        else: ts = f"{ago//86400}d ago"
                        lines.append(f"  #{item['id']} — {item['summary'][:60]} ({item['count']} msgs, {ts})")
                    lines.append("")
                    lines.append("Use /view <id> to see, /change <id> to resume")
                    for chunk in [lines[i:i+15] for i in range(0, len(lines), 15)]:
                        await send(chat, "\n".join(chunk))

                elif cmd == "/view":
                    convs = load_conversations()
                    chat_key = str(chat)
                    items = convs.get("archives", {}).get(chat_key, [])
                    target = int(parts[1]) if len(parts) > 1 else 0
                    found = None
                    for item in items:
                        if item["id"] == target:
                            found = item
                            break
                    if not found:
                        await send(chat, f"No archived conversation #{target}. Use /history to list.")
                        continue
                    msgs = found["messages"][-30:]
                    lines = [f"Conversation #{target} ({found['count']} msgs):", ""]
                    for m in msgs:
                        role = m.get("role", "?")[:4]
                        content = m.get("content", "")[:200]
                        lines.append(f"[{role}] {content}")
                    for chunk in [lines[i:i+20] for i in range(0, len(lines), 20)]:
                        await send(chat, "\n".join(chunk))

                elif cmd in ("/change", "/resume"):
                    convs = load_conversations()
                    chat_key = str(chat)
                    items = convs.get("archives", {}).get(chat_key, [])
                    target = int(parts[1]) if len(parts) > 1 else 0
                    found = None
                    for item in items:
                        if item["id"] == target:
                            found = item
                            break
                    if not found:
                        await send(chat, f"No archived conversation #{target}. Use /history to list.")
                        continue
                    _archive_current(uid, chat)
                    sessions[uid] = list(found["messages"])
                    team_sessions.pop(uid, None)
                    await send(chat, f"Resumed conversation #{target} ({found['count']} msgs). Current session archived.")

                elif cmd == "/remember":
                    if user_memory is None:
                        await send(chat, "Memory module not loaded.")
                        continue
                    fact = text[len("/remember"):].strip()
                    if not fact:
                        await send(chat, "Usage: /remember <fact>\nExample: /remember I prefer dark mode")
                        continue
                    user_memory.add(fact, str(uid))
                    save_memory()
                    await send(chat, f"Remembered: {fact[:100]}")

                elif cmd == "/recall":
                    if user_memory is None:
                        await send(chat, "Memory module not loaded.")
                        continue
                    query = text[len("/recall"):].strip()
                    if not query:
                        # Show recent memories
                        user_mems = [m for m in user_memory.memories if m.user_id == str(uid)]
                        if not user_mems:
                            await send(chat, "No memories stored yet. Use /remember <fact> to add some.")
                        else:
                            lines = [f"Your memories ({len(user_mems)}):"]
                            for m in user_mems[-10:]:
                                lines.append(f"  - {m.content[:80]}")
                            await send(chat, "\n".join(lines))
                    else:
                        results = user_memory.search(query, str(uid), top_k=5)
                        if not results:
                            await send(chat, f"No memories found for: {query}")
                        else:
                            lines = [f"Memories for '{query}':"]
                            for m in results:
                                lines.append(f"  [{m.score:.2f}] {m.content[:80]}")
                            await send(chat, "\n".join(lines))

                elif cmd == "/arch":
                    if len(parts) < 2:
                        lines = [f"Architectures ({len(ARCHITECTURES)}):"]
                        for name, a in sorted(ARCHITECTURES.items()):
                            m = " << active" if name == active_arch else ""
                            lines.append(f"  {name}{m} — {a['desc']}")
                        await send(chat, "\n".join(lines))
                        continue
                    name = parts[1].lower()
                    if name not in ARCHITECTURES:
                        await send(chat, f"Unknown arch. Options: {', '.join(ARCHITECTURES.keys())}")
                        continue
                    active_arch = name
                    set_user_pref(chat, "active_arch", name)
                    await send(chat, f"Architecture: {name} — {ARCHITECTURES[name]['desc']}")

                elif cmd == "/mode":
                    if len(parts) < 2:
                        lines = [f"Modes ({len(MODES)}):"]
                        for name, m in sorted(MODES.items()):
                            cur = " << active" if name == active_mode else ""
                            lines.append(f"  {name}{cur} — {m['desc']}")
                        await send(chat, "\n".join(lines))
                        continue
                    name = parts[1].lower()
                    if name not in MODES:
                        await send(chat, f"Unknown mode. Options: {', '.join(MODES.keys())}")
                        continue
                    active_mode = name
                    set_user_pref(chat, "active_mode", name)
                    await send(chat, f"Mode: {name} — {MODES[name]['desc']}")

                elif cmd == "/effort":
                    await send(chat, f"Effort: {effort} — {EFFORT_LEVELS[effort]['desc']}\nUse /low /normal /medium /high /superhigh to change.\nThinking: {thinking_mode}")

                elif cmd in ("/low", "/normal", "/medium", "/high", "/superhigh"):
                    level = cmd[1:]
                    if level in EFFORT_LEVELS:
                        effort = level
                        set_user_pref(chat, "effort", level)
                        await send(chat, f"Effort: {level} — {EFFORT_LEVELS[level]['desc']}")

                elif cmd == "/thinking":
                    if len(parts) < 2:
                        await send(chat, f"Thinking: {thinking_mode}\nUsage: /thinking off|extended|adaptive")
                        continue
                    mode = parts[1].lower()
                    if mode not in ("off", "extended", "adaptive"):
                        await send(chat, "Options: off, extended, adaptive")
                        continue
                    thinking_mode = mode
                    set_user_pref(chat, "thinking_mode", mode)
                    descs = {"off": "No extended thinking", "extended": "Step-by-step reasoning on every response", "adaptive": "Auto-decides when to use thinking"}
                    await send(chat, f"Thinking: {mode} — {descs[mode]}")

                elif cmd == "/tools":
                    lines = [f"Available tools ({len(TOOLS)}):"]
                    for name, t in sorted(TOOLS.items()):
                        lines.append(f"  {name} — {t['desc']}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/teams":
                    if not TEAMS:
                        await send(chat, "No teams yet. Use /createteam or /putteam to make one.")
                        continue
                    lines = [f"Teams ({len(TEAMS)}):"]
                    for name, t in sorted(TEAMS.items()):
                        agents = ", ".join(t["agents"])
                        tools = ", ".join(t.get("tools", []))
                        m = " << active" if name == active_team else ""
                        lines.append(f"\n  {name}{m}")
                        lines.append(f"  {t['desc']}")
                        lines.append(f"  Agents: {agents}")
                        if tools: lines.append(f"  Tools: {tools}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/putteam":
                    if len(parts) < 3:
                        await send(chat, "Usage: /putteam <name> <agent1> <agent2> ...\nExample: /putteam webteam backend-dev frontend-dev api-dev")
                        continue
                    tname = parts[1].lower()
                    tagents = [a.lower() for a in parts[2:]]
                    missing = [a for a in tagents if a not in AGENTS]
                    if missing:
                        await send(chat, f"Unknown agents: {', '.join(missing)}")
                        continue
                    TEAMS[tname] = {"desc": f"Team with {len(tagents)} agents", "agents": tagents, "tools": []}
                    save_teams()
                    await send(chat, f"Team created: {tname} ({', '.join(tagents)})")

                elif cmd == "/createteam":
                    if len(parts) < 2:
                        await send(chat, "Usage: /createteam <description>\nExample: /createteam A team for building full-stack web apps")
                        continue
                    desc = " ".join(parts[1:])
                    await typing(chat)
                    agents_list = ", ".join(sorted(AGENTS.keys()))
                    prompt = (
                        f"Design a multi-agent team for: \"{desc}\". "
                        f"Available agents: {agents_list}. "
                        f"Respond with ONLY JSON (no markdown): "
                        f"{{\"name\": \"team-name\", \"desc\": \"short desc\", \"agents\": [\"agent1\", ...], "
                        f"\"plan\": [{{\"agent\": \"agent1\", \"task\": \"what they do\", \"depends_on\": []}}]}}. "
                        f"Pick 3-5 agents. Each plan step specifies one agent's task and which other steps it depends on (by agent name). "
                        f"The last step should synthesize results."
                    )
                    raw = ""
                    try:
                        raw = await smart_call([{"role": "user", "content": prompt}], active_provider)
                        raw = raw.strip()
                        if raw.startswith("```"): raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                        match = re.search(r'\{.*\}', raw, re.DOTALL)
                        if not match: raise Exception("No JSON found")
                        data = json.loads(match.group())
                        tname = data["name"].lower().replace(" ", "-")
                        tagents = [a.lower() for a in data["agents"] if a.lower() in AGENTS]
                        if not tagents: raise Exception("No valid agents selected")
                        plan = data.get("plan", [])
                        for step in plan:
                            step["agent"] = step["agent"].lower()
                        TEAMS[tname] = {"desc": data["desc"], "agents": tagents, "plan": plan, "tools": []}
                        save_teams()
                        steps = "\n".join(f"  {i+1}. {s['agent']}: {s['task']}" for i, s in enumerate(plan[:6]))
                        await send(chat, f"Created team: {tname} — {data['desc']}\nAgents: {', '.join(tagents)}\nPlan:\n{steps}")
                    except Exception as e:
                        await send(chat, f"Failed: {e}\nRaw: {raw[:200] if raw else 'none'}")

                elif cmd == "/useteam":
                    if len(parts) < 2:
                        await send(chat, "Usage: /useteam <teamname>")
                        continue
                    tname = parts[1].lower()
                    if tname not in TEAMS:
                        await send(chat, f"Unknown team: {tname}. Use /teams to see all.")
                        continue
                    active_team = tname
                    set_user_pref(chat, "active_team", tname)
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, f"Team activated: {tname} ({', '.join(TEAMS[tname]['agents'])})\nArch: {active_arch}")

                elif cmd == "/stopteam":
                    active_team = None
                    set_user_pref(chat, "active_team", None)
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, "Team mode deactivated. Back to single agent.")

                elif cmd == "/addadmin" and is_owner:
                    if len(parts) < 2:
                        await send(chat, "Usage: /addadmin <telegram_user_id>")
                        continue
                    try:
                        new_id = int(parts[1])
                        admins.add(new_id)
                        save_admins()
                        await send(chat, f"Added admin: {new_id}")
                    except Exception:
                        await send(chat, "Invalid ID. Must be a number.")

                elif cmd == "/removeadmin" and is_owner:
                    if len(parts) < 2:
                        await send(chat, "Usage: /removeadmin <telegram_user_id>")
                        continue
                    try:
                        rem_id = int(parts[1])
                        if rem_id == OWNER_ID:
                            await send(chat, "Cannot remove owner.")
                        elif rem_id in admins:
                            admins.discard(rem_id)
                            save_admins()
                            await send(chat, f"Removed admin: {rem_id}")
                        else:
                            await send(chat, f"Not an admin: {rem_id}")
                    except Exception:
                        await send(chat, "Invalid ID. Must be a number.")

                elif cmd == "/adminlist" and is_owner:
                    await send(chat, f"Admins ({len(admins)}):\n" + "\n".join(f"  {a}" + (" (owner)" if a == OWNER_ID else "") for a in admins))

                elif cmd == "/addmod" and (is_owner or is_admin or is_mod):
                    if len(parts) < 2:
                        await send(chat, "Usage: /addmod <telegram_user_id>")
                        continue
                    try:
                        new_id = int(parts[1])
                        if new_id in mods:
                            await send(chat, f"Already a mod: {new_id}")
                        else:
                            mods.add(new_id)
                            save_mods()
                            await send(chat, f"Added mod: {new_id}")
                    except Exception:
                        await send(chat, "Invalid ID. Must be a number.")

                elif cmd == "/removemod" and (is_owner or is_admin or is_mod):
                    if len(parts) < 2:
                        await send(chat, "Usage: /removemod <telegram_user_id>")
                        continue
                    try:
                        rem_id = int(parts[1])
                        if rem_id in mods:
                            mods.discard(rem_id)
                            save_mods()
                            await send(chat, f"Removed mod: {rem_id}")
                        else:
                            await send(chat, f"Not a mod: {rem_id}")
                    except Exception:
                        await send(chat, "Invalid ID. Must be a number.")

                elif cmd == "/modlist" and (is_owner or is_admin or is_mod):
                    if mods:
                        await send(chat, f"Mods ({len(mods)}):\n" + "\n".join(f"  {m}" for m in mods))
                    else:
                        await send(chat, "No mods added yet.")

                elif cmd == "/addprovider" and (is_owner or is_admin or is_mod):
                    if len(parts) < 5:
                        await send(chat, "Usage: /addprovider <name> <model> <url> <key>\nExample: /addprovider grok grok-1 https://api.grok.com/v1/chat xyz123")
                        continue
                    pname = parts[1].lower()
                    pmodel = parts[2]
                    purl = parts[3]
                    pkey = parts[4]
                    PROVIDERS[pname] = {"url": purl, "model": pmodel, "key": pkey}
                    save_providers()
                    await send(chat, f"Added provider: {pname} ({pmodel})")

                elif cmd == "/agentprovider" and (is_owner or is_admin or is_mod):
                    if len(parts) < 5:
                        await send(chat, "Usage: /agentprovider <agent> <url> <key> <model>\nExample: /agentprovider design_arena https://api.designarena.ai/v1/chat sk-abc123 gpt-4o")
                        continue
                    aname = parts[1].lower()
                    purl = parts[2]
                    pkey = parts[3]
                    pmodel = parts[4]
                    if aname not in AGENTS:
                        await send(chat, f"Unknown agent: {aname}")
                        continue
                    AGENT_PROVIDERS[aname] = {"url": purl, "key": pkey, "model": pmodel}
                    _atomic_save(AGENT_PROVIDERS_FILE, AGENT_PROVIDERS)
                    await send(chat, f"Agent provider set for {aname}: {pmodel}")

                elif cmd == "/createagent" and (is_owner or is_admin or is_mod):
                    if len(parts) < 2:
                        await send(chat, "Usage: /createagent <description>\nExample: /createagent A rust engineer specialized in blockchain and WASM")
                        continue
                    desc = " ".join(parts[1:])
                    await typing(chat)
                    raw = ""
                    try:
                        prompt = (
                f"Create a new AI agent definition based on this description: \"{desc}\". "
                f"Respond with ONLY a JSON object (no markdown, no code blocks) with keys: name (lowercase, no spaces), desc (short description), prompt (detailed system prompt for the agent). "
                f"The prompt should be 2-4 sentences explaining what the agent does."
                        )
                        msg = [{"role": "user", "content": prompt}]
                        raw = await call_provider(msg, active_provider)
                        raw = raw.strip()
                        if raw.startswith("```"): raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                        match = re.search(r'\{.*\}', raw, re.DOTALL)
                        if not match: raise Exception("No JSON found in response")
                        data = json.loads(match.group())
                        name = data["name"].lower().replace(" ", "-")
                        AGENTS[name] = {"desc": data["desc"], "prompt": data["prompt"]}
                        save_agents()
                        await send(chat, f"Created agent: {name} — {data['desc']}\n\nPrompt: {data['prompt']}")
                        await send(chat, f"Tip: if you want to add prompt in this command /addprompt {name} <prompt>")
                    except Exception as e:
                        await send(chat, f"Failed to create agent: {e}\nRaw: {raw[:300] if raw else 'none'}")
                        try: await send(chat, f"Tip: you can also use /addprompt <agentname> <prompt> to set a prompt manually.")
                        except Exception: pass

                elif cmd == "/premadeskills":
                    lines = [f"Pre-made skill teams ({len(PREMADE_SKILLS)}):"]
                    for name, s in sorted(PREMADE_SKILLS.items()):
                        agents = ", ".join(s["agents"])
                        lines.append(f"\n  {name}")
                        lines.append(f"  {s['desc']}")
                        lines.append(f"  Agents: {agents}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/market":
                    if not market_mod:
                        await send(chat, "Marketplace module not available.")
                        continue
                    if len(parts) < 2:
                        await send(chat, "Usage:\n/market list [page] — Browse marketplace\n/market search <query> — Search agents\n/market featured — Featured agents\n/market install <name> — Install agent\n/market uninstall <name> — Remove agent\n/market installed — Your installed agents\n/market publish <name> <desc> | <prompt> — Publish agent")
                        continue
                    msub = parts[1].lower()
                    market = market_mod.get_market()
                    if msub == "list":
                        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                        agents_list = market.list_all(page=page)
                        if not agents_list:
                            await send(chat, "No agents found. Try /market refresh")
                            continue
                        lines = [f"Marketplace (page {page + 1}):"]
                        for a in agents_list[:20]:
                            sid = a.get("id", "?")
                            desc = a.get("desc", "")[:60]
                            stars = a.get("stars", 0)
                            lines.append(f"  {sid} {'⭐' * (stars // 10 + 1)} {desc}")
                        await send(chat, "\n".join(lines))
                    elif msub == "search":
                        q = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not q:
                            await send(chat, "Usage: /market search <query>")
                            continue
                        results = market.search(q)
                        if not results:
                            await send(chat, f"No agents matching '{q}'. Try: /market refresh")
                            continue
                        lines = [f"Results for '{q}':"]
                        for a in results[:15]:
                            sid = a.get("id", "?")
                            desc = a.get("desc", "")[:80]
                            stars = a.get("stars", 0)
                            lines.append(f"  {sid} (⭐{stars}) — {desc}")
                        await send(chat, "\n".join(lines))
                    elif msub == "featured":
                        featured = market.get_featured()
                        if not featured:
                            await send(chat, "No featured agents. Try: /market refresh")
                            continue
                        lines = ["Featured agents:"]
                        for a in featured[:10]:
                            sid = a.get("id", "?")
                            desc = a.get("desc", "")[:80]
                            lines.append(f"  ⭐ {sid} — {desc}")
                        await send(chat, "\n".join(lines))
                    elif msub == "install":
                        if len(parts) < 3:
                            await send(chat, "Usage: /market install <agent_name>")
                            continue
                        aid = parts[2].lower()
                        await typing(chat)
                        ok, msg = await market.install(aid, await bf.get_http())
                        await send(chat, msg)
                    elif msub == "uninstall" and (is_owner or is_admin):
                        if len(parts) < 3:
                            await send(chat, "Usage: /market uninstall <agent_name>")
                            continue
                        ok, msg = market.uninstall(parts[2])
                        await send(chat, msg)
                    elif msub == "installed":
                        installed = market.list_installed()
                        if not installed:
                            await send(chat, "No marketplace agents installed.")
                            continue
                        lines = ["Installed marketplace agents:"]
                        for name, info in installed[:20]:
                            t = time.strftime("%Y-%m-%d", time.localtime(info.get("installed", 0)))
                            lines.append(f"  {name} (installed {t})")
                        await send(chat, "\n".join(lines))
                    elif msub == "publish" and (is_owner or is_admin):
                        rest = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if " | " not in rest:
                            await send(chat, "Usage: /market publish <name> <desc> | <prompt>")
                            continue
                        left, prompt = rest.split(" | ", 1)
                        left_parts = left.split(" ", 1)
                        name = left_parts[0]
                        desc = left_parts[1] if len(left_parts) > 1 else "Community agent"
                        ok, msg = await market.publish(name, desc, prompt, await bf.get_http())
                        await send(chat, msg)
                    elif msub == "refresh":
                        await typing(chat)
                        reg = await market.fetch_registry(await bf.get_http())
                        await send(chat, f"Refreshed. {len(reg)} agents in registry.")
                    else:
                        await send(chat, "Unknown subcommand. Use: /market")

                elif cmd == "/addprompt" and (is_owner or is_admin or is_mod):
                    if len(parts) < 3:
                        await send(chat, "Usage: /addprompt <agentname> <prompt>")
                        continue
                    pname = parts[1].lower()
                    if pname not in AGENTS:
                        await send(chat, f"Unknown agent: {pname}")
                        continue
                    pprompt = " ".join(parts[2:])
                    AGENTS[pname]["prompt"] = pprompt
                    save_agents()
                    await send(chat, f"Updated prompt for agent: {pname}")

                elif cmd == "/announce" and (is_owner or is_admin):
                    if not _check_rate_limit(f"announce:{chat}", max_calls=2, window=300):
                        await send(chat, "Rate limit: /announce can be used 2 times per 5 minutes.")
                        continue
                    ver_info = load_version()
                    ver = ver_info.get("version", "unknown")
                    changes = ver_info.get("whats_new", {}).get(ver, [])
                    state = load_version_state()
                    await announce_update(state.get("last_version", ""), ver, changes, state)
                    await send(chat, f"Announced v{ver} to all chats.")
                    
                elif cmd == "/skills":
                    skills_db = {
                        "ai-engineering": "Stanford CS229 → production AI systems. Covers ML, RLHF, RAG, fine-tuning, MLOps.",
                        "browser-automation": "Skyvern + Browser Use — AI-driven browser automation, CAPTCHA handling, dynamic pages.",
                        "video-analysis": "Claude Video — Extract key frames, detect objects/scenes/actions, generate video summaries.",
                        "text-to-speech": "Pocket TTS + Voicebox — Natural TTS, SSML, voiceovers, audiobooks, accessibility audio.",
                        "system-prompts": "System prompt engineering — meta-prompt structures, guardrails, anti-jailbreak patterns.",
                        "knowledge-graph": "Graphify + Neo4j — Entity extraction, relationship mapping, graph RAG, Cypher queries.",
                        "code-review-graph": "Dependency graph analysis — circular deps, dead code, impact path tracing, module coupling.",
                        "copilot-ui": "CopilotKit — Build AI copilot UIs with React: sidebar, popup, textarea, co-agents.",
                        "multi-agent": "Agency-Agents — Agent-to-agent messaging, hierarchical structures, tool sharing.",
                        "goose": "Goose (Block) — Autonomous task execution with structured tool calling, file ops, shell.",
                        "cube-analytics": "Cube.js — Semantic analytics layer, data modeling, pre-aggregations, multi-tenant.",
                        "penpot-design": "Penpot — Open-source design tooling, prototypes, design tokens, collaborative workflows.",
                        "lobehub-chat": "LobeChat — Modern chat UIs, streaming text, multi-modal messages, session mgmt.",
                        "cognee-memory": "Cognee — Cognitive graph memory with episodic/semantic/procedural layers for agents.",
                        "openhands-dev": "OpenHands — Full AI developer: code, debug, run commands, build complete apps.",
                    }
                    lines = [f"Available skills from repo catalog ({len(skills_db)}):"]
                    for sname, sdesc in sorted(skills_db.items()):
                        lines.append(f"  {sname} — {sdesc}")
                    lines.append("")
                    lines.append("Use /agent <name> to switch to an agent, or just chat with any agent about these skills.")
                    await send(chat, "\n".join(lines))

                elif cmd == "/pocket-tts":
                    if len(parts) < 3:
                        await send(chat, "Usage: /pocket-tts <voice> <text>\nVoices: alloy, echo, fable, nova, shimmer, ash, coral, sage\nExample: /pocket-tts nova Hello, welcome to the AI bot!")
                        continue
                    voice = parts[1].lower()
                    tts_text = " ".join(parts[2:])
                    if voice not in ("alloy", "echo", "fable", "nova", "shimmer", "ash", "coral", "sage"):
                        await send(chat, f"Unknown voice '{voice}'. Use: alloy, echo, fable, nova, shimmer, ash, coral, sage")
                        continue
                    await typing(chat)
                    try:
                        c = await get_http()
                        resp = await c.post(
                            "https://api.openai.com/v1/audio/speech",
                            json={"model": "tts-1", "input": tts_text, "voice": voice},
                            headers={"Authorization": f"Bearer {os.environ.get('OPENAI_KEY', '')}"},
                            timeout=30
                        )
                        if resp.status_code == 200:
                            audio_data = resp.content
                            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                            await c.post(
                                f"https://api.telegram.org/bot{bot_token}/sendVoice",
                                files={"voice": ("speech.ogg", audio_data)},
                                data={"chat_id": chat, "caption": f"TTS ({voice}): {tts_text[:100]}"},
                                timeout=30,
                            )
                        else:
                            await send(chat, f"TTS error: {resp.status_code} - {resp.text[:200]}")
                    except Exception as e:
                        await send(chat, f"TTS error: {e}")

                elif cmd == "/voice":
                    if len(parts) < 2:
                        mode = bf.get_voice_mode(chat)
                        await send(chat, f"X-Phone Voice: {mode}\nUsage:\n/voice on — Enable voice conversation mode (voice in, voice out)\n/voice off — Disable voice mode\n/voice emotion <emotion> — Set voice emotion (neutral, happy, sad, angry, excited, calm, whisper)\n/voice status — Current settings")
                        continue
                    vc = parts[1].lower()
                    if vc == "on":
                        bf.set_voice_mode(chat, "conversation")
                        await send(chat, "🎙️ X-Phone Voice ON. Send a voice message and I'll reply with voice.\nSpeak naturally — you can interrupt me anytime by sending another voice message.")
                    elif vc == "off":
                        bf.set_voice_mode(chat, "off")
                        await send(chat, "X-Phone Voice OFF. Text mode restored.")
                    elif vc == "emotion":
                        if len(parts) < 3:
                            await send(chat, f"Usage: /voice emotion <emotion>\nOptions: {', '.join(sorted(bf.VOICE_EMOTIONS))}")
                            continue
                        emotion = parts[2].lower()
                        if emotion not in bf.VOICE_EMOTIONS:
                            await send(chat, f"Unknown emotion. Use: {', '.join(sorted(bf.VOICE_EMOTIONS))}")
                            continue
                        bf.set_voice_mode(chat, emotion)
                        await send(chat, f"Voice emotion set to: {emotion}")
                    elif vc == "status":
                        mode = bf.get_voice_mode(chat)
                        await send(chat, f"X-Phone Status:\n  Mode: {mode}\n  Available emotions: {', '.join(sorted(bf.VOICE_EMOTIONS))}")
                    else:
                        await send(chat, "Unknown subcommand. Use: /voice")

                elif cmd == "/auto":
                    if not guard_mod:
                        await send(chat, "Auto-reply module not available.")
                        continue
                    auto = guard_mod.get_auto()
                    if len(parts) < 2:
                        c = auto.get(uid)
                        status = "ON" if c.get("enabled") else "OFF"
                        await send(chat, f"Chat Automation: {status}\nUsage:\n/auto on — Enable AI auto-response on your behalf\n/auto off — Disable\n/auto toggle — Toggle on/off\n/auto template <text> — Set auto-reply style/prompt\n/auto scope all|whitelist|blacklist — Set chat scope\n/auto allow <chat_id> — Add chat to whitelist\n/auto deny <chat_id> — Add chat to blacklist\n/auto status — Current settings")
                        continue
                    a_sub = parts[1].lower()
                    if a_sub == "on":
                        auto.set(uid, enabled=True)
                        await send(chat, f"✅ Chat Automation ON. I'll auto-respond to messages in allowed chats using your style.\nUse /auto template <text> to customize my voice.")
                    elif a_sub == "off":
                        auto.set(uid, enabled=False)
                        await send(chat, "Chat Automation OFF.")
                    elif a_sub == "toggle":
                        new = auto.toggle(uid)
                        await send(chat, f"Chat Automation {'ON' if new else 'OFF'}.")
                    elif a_sub == "template":
                        tpl = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not tpl:
                            await send(chat, "Usage: /auto template <text>\nExample: /auto template Respond as a friendly, professional assistant. Keep replies under 100 chars.")
                            continue
                        auto.set(uid, template=tpl)
                        await send(chat, f"Auto-reply template set:\n{tpl[:200]}")
                    elif a_sub == "scope":
                        if len(parts) < 3 or parts[2] not in ("all", "whitelist", "blacklist"):
                            await send(chat, "Usage: /auto scope all|whitelist|blacklist")
                            continue
                        auto.set(uid, scope=parts[2])
                        await send(chat, f"Scope set to: {parts[2]}")
                    elif a_sub == "allow":
                        cid = parts[2] if len(parts) > 2 else ""
                        if cid:
                            cfg = auto.get(uid)
                            wl = cfg.get("whitelist", [])
                            if cid not in wl:
                                wl.append(cid)
                            auto.set(uid, whitelist=wl, scope=cfg.get("scope", "all"))
                            await send(chat, f"Added {cid} to whitelist.")
                    elif a_sub == "deny":
                        cid = parts[2] if len(parts) > 2 else ""
                        if cid:
                            cfg = auto.get(uid)
                            bl = cfg.get("blacklist", [])
                            if cid not in bl:
                                bl.append(cid)
                            auto.set(uid, blacklist=bl, scope=cfg.get("scope", "all"))
                            await send(chat, f"Added {cid} to blacklist.")
                    elif a_sub == "status":
                        c = auto.get(uid)
                        status = "ON" if c.get("enabled") else "OFF"
                        await send(chat, f"Chat Automation Status:\n  Status: {status}\n  Scope: {c.get('scope', 'all')}\n  Template: {c.get('template', '(default)')[:100]}")
                    else:
                        await send(chat, f"Unknown subcommand: {a_sub}")

                elif cmd == "/guard":
                    if not guard_mod:
                        await send(chat, "Guardian module not available.")
                        continue
                    guard = guard_mod.get_guardian()
                    is_group = msg.get("chat", {}).get("type", "") in ("group", "supergroup")
                    if not is_group and (is_owner or is_admin):
                        pass
                    elif not is_group:
                        await send(chat, "Guardian mode only works in groups.")
                        continue
                    if len(parts) < 2:
                        cfg = guard.get_chat(chat)
                        status = "ON" if cfg.get("enabled") else "OFF"
                        qcount = len(cfg.get("quizzes", []))
                        await send(chat, f"AI Guardian: {status}\nUsage:\n/guard on — Enable AI guardian for this group\n/guard off — Disable\n/guard toggle — Toggle\n/guard rules <text> — Set moderation rules (ban:keyword, warn:keyword, maxlen:N)\n/guard screening on|off — Toggle join request screening\n/guard quiz add <question> | <answer> — Add screening question\n/guard quiz remove <id> — Remove quiz question\n/guard quiz list — List questions\n/guard welcome <text> — Set welcome message\n/guard strictness low|medium|high — Set screening strictness\n/guard log on|off — Toggle action logging\n/guard status — Current settings")
                        continue
                    g_sub = parts[1].lower()
                    if g_sub == "on":
                        guard.set_chat(chat, enabled=True)
                        await send(chat, f"🛡️ AI Guardian ON for this group.\nI'll screen join requests, enforce rules, and welcome new members.\nUse /guard rules to set moderation rules.")
                    elif g_sub == "off":
                        guard.set_chat(chat, enabled=False)
                        await send(chat, "AI Guardian OFF.")
                    elif g_sub == "toggle":
                        new = guard.toggle(chat)
                        await send(chat, f"AI Guardian {'ON' if new else 'OFF'}.")
                    elif g_sub == "rules":
                        rules = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not rules:
                            await send(chat, "Usage: /guard rules <text>\nOne rule per line. Prefix with ban:, warn:, or maxlen:\nExample:\n/guard rules ban:spam\nban:crypto\nwarn:badword\nmaxlen:1000")
                            continue
                        guard.set_chat(chat, rules=rules)
                        await send(chat, f"Guardian rules set ({len(rules.split(chr(10)))} lines).")
                    elif g_sub == "screening":
                        if len(parts) < 3:
                            await send(chat, "Usage: /guard screening on|off")
                            continue
                        on = parts[2].lower() == "on"
                        guard.set_chat(chat, screening=on)
                        await send(chat, f"Join request screening {'ON' if on else 'OFF'}.")
                    elif g_sub == "quiz" and len(parts) >= 3:
                        qsub = parts[2].lower()
                        if qsub == "add":
                            rest = " ".join(parts[3:]) if len(parts) > 3 else ""
                            if " | " not in rest:
                                await send(chat, "Usage: /guard quiz add <question> | <answer>")
                                continue
                            qq, qa = rest.split(" | ", 1)
                            guard.add_quiz(chat, qq.strip(), qa.strip())
                            await send(chat, f"Quiz question added:\nQ: {qq.strip()}\nA: {qa.strip()}")
                        elif qsub == "remove":
                            qid = parts[3] if len(parts) > 3 else ""
                            guard.remove_quiz(chat, qid)
                            await send(chat, f"Removed quiz: {qid}")
                        elif qsub == "list":
                            cfg = guard.get_chat(chat)
                            quizzes = cfg.get("quizzes", [])
                            if not quizzes:
                                await send(chat, "No screening questions configured.")
                                continue
                            lines = [f"Screening questions ({len(quizzes)}):"]
                            for q in quizzes:
                                lines.append(f"  [{q['id']}] {q['question']} -> {q['answer']}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "Usage: /guard quiz add|remove|list")
                    elif g_sub == "welcome":
                        welcome = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not welcome:
                            await send(chat, "Usage: /guard welcome <text>\nExample: /guard welcome Welcome {name}! Please read the rules.")
                            continue
                        guard.set_chat(chat, welcome=welcome)
                        await send(chat, f"Welcome message set:\n{welcome[:200]}")
                    elif g_sub == "strictness":
                        if len(parts) < 3 or parts[2] not in ("low", "medium", "high"):
                            await send(chat, "Usage: /guard strictness low|medium|high")
                            continue
                        guard.set_chat(chat, strictness=parts[2])
                        await send(chat, f"Screening strictness set to: {parts[2]}")
                    elif g_sub == "log":
                        if len(parts) < 3:
                            await send(chat, "Usage: /guard log on|off")
                            continue
                        guard.set_chat(chat, log=parts[2].lower() == "on")
                        await send(chat, f"Guardian logging {'ON' if parts[2].lower() == 'on' else 'OFF'}.")
                    elif g_sub == "status":
                        cfg = guard.get_chat(chat)
                        status = "ON" if cfg.get("enabled") else "OFF"
                        await send(chat, f"AI Guardian Status:\n  Status: {status}\n  Screening: {'ON' if cfg.get('screening') else 'OFF'}\n  Strictness: {cfg.get('strictness', 'medium')}\n  Rules: {(cfg.get('rules', '') or '')[:200] or '(none)'}\n  Quizzes: {len(cfg.get('quizzes', []))}\n  Welcome: {(cfg.get('welcome', '') or '')[:100] or '(none)'}")
                    else:
                        await send(chat, f"Unknown subcommand: {g_sub}")

                elif cmd == "/video-analyze":
                    if len(parts) < 2:
                        await send(chat, "Usage: /video-analyze <search_query>\nExample: /video-analyze a cat playing piano\nDescribes what the AI would analyze in a video matching the query.")
                        continue
                    query = " ".join(parts[1:])
                    await typing(chat)
                    analysis = await smart_call([
                        {"role": "system", "content": "You are a video analysis AI. Describe what you would analyze in a video matching the given query: scene composition, objects, actions, text overlay, audio context, transitions, timestamps. Be detailed and structured."},
                        {"role": "user", "content": f"Video search: {query}\n\nDescribe a detailed analysis of what this video likely contains, structured by: visual scene, detected objects, actions/events, text/overlays, audio/speech, timestamps."}
                    ], active_provider)
                    await send(chat, f"Video Analysis for '{query}':\n\n{analysis[:3500]}")

                elif cmd == "/prompt-analyze":
                    if len(parts) < 2:
                        await send(chat, "Usage: /prompt-analyze <prompt_text>\nAnalyzes a system prompt for structure, guardrails, effectiveness.")
                        continue
                    prompt_text = " ".join(parts[1:])
                    await typing(chat)
                    analysis = await smart_call([
                        {"role": "system", "content": "You are a system prompt engineer. Analyze the given prompt for: role clarity, instruction specificity, output format constraints, guardrail coverage, anti-jailbreak measures, token efficiency, personality injection, and potential weaknesses. Score each category 1-10 and suggest specific improvements."},
                        {"role": "user", "content": f"Analyze this prompt:\n\n{prompt_text}"}
                    ], active_provider)
                    await send(chat, f"Prompt Analysis:\n\n{analysis[:3500]}")

                elif cmd == "/kg":
                    if len(parts) < 2:
                        await send(chat, "Usage:\n/kg add <entity> [type] — Add entity\n/kg relate <source> <relation> <target> — Add relation\n/kg extract <text> — Extract from text\n/kg search <query> — Search entities\n/kg query <text> — Graph query\n/kg related <name> — Show related\n/kg stats — Graph statistics\n/kg remove <entity> — Remove entity\n/kg clear — Clear all data")
                        continue
                    sub = parts[1].lower()
                    if not kg_mod:
                        await send(chat, "Knowledge Graph module not available.")
                        continue
                    kg_inst = kg_mod.get_kg()
                    if sub == "add":
                        if len(parts) < 3:
                            await send(chat, "Usage: /kg add <entity> [type]")
                            continue
                        name = parts[2]
                        etype = parts[3] if len(parts) > 3 else "concept"
                        if kg_inst.add_entity(name, etype):
                            await send(chat, f"Added: {name} ({etype})")
                        else:
                            await send(chat, f"Already exists: {name}")
                    elif sub == "relate" and len(parts) >= 5:
                        kg_inst.add_relation(parts[2], parts[3], parts[4])
                        await send(chat, f"Related: {parts[2]} --[{parts[3]}]--> {parts[4]}")
                    elif sub == "extract":
                        text = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not text:
                            await send(chat, "Usage: /kg extract <text>")
                            continue
                        await typing(chat)
                        ec, rc = await kg_inst.extract_from_text(text, smart_call)
                        await send(chat, f"Extracted {ec} entities and {rc} relationships.")
                    elif sub == "search":
                        q = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not q:
                            await send(chat, "Usage: /kg search <query>")
                            continue
                        results = kg_inst.search_entities(q)
                        if not results:
                            await send(chat, "No matches found.")
                            continue
                        lines = [f"Entities matching '{q}':"]
                        for r in results:
                            lines.append(f"  {r['name']} ({r.get('type', '?')})")
                        await send(chat, "\n".join(lines))
                    elif sub == "query":
                        q = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not q:
                            await send(chat, "Usage: /kg query <text>")
                            continue
                        await typing(chat)
                        results = kg_inst.query(q)
                        msg = f"Query: {q}\n"
                        if results["entities"]:
                            msg += f"\nDirect matches: {len(results['entities'])}\n"
                            for e in results["entities"][:5]:
                                msg += f"  {e['name']} ({e.get('type', '?')})\n"
                        if results["paths"]:
                            msg += f"\nPaths found: {len(results['paths'])}\n"
                            for p in results["paths"][:3]:
                                msg += f"  {' -> '.join(p['path'])}\n"
                        if results["subgraph"]:
                            sg = results["subgraph"]
                            msg += f"\nSubgraph: {len(sg['nodes'])} nodes, {len(sg['edges'])} edges around '{sg['center']}'"
                        await send(chat, msg[:3500])
                    elif sub == "related":
                        name = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not name:
                            await send(chat, "Usage: /kg related <name>")
                            continue
                        rel = kg_inst.get_related(name)
                        if not rel:
                            await send(chat, f"Entity not found: {name}")
                            continue
                        await send(chat, f"Relationships for '{name}':\n  Nodes: {len(rel['nodes'])}\n  Edges: {len(rel['edges'])}\n\n  /kg webviz to see visual map")
                    elif sub == "stats":
                        s = kg_inst.stats()
                        await send(chat, f"Knowledge Graph Stats:\n  Entities: {s['entities']}\n  Relationships: {s['relationships']}\n  Types: {json.dumps(s['types'])}")
                    elif sub == "remove":
                        name = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if name and kg_inst.remove_entity(name):
                            await send(chat, f"Removed: {name}")
                        else:
                            await send(chat, "Entity not found.")
                    elif sub == "clear" and (is_owner or is_admin):
                        kg_inst.clear()
                        await send(chat, "Knowledge Graph cleared.")
                    elif sub == "webviz":
                        await send(chat, f"Open web dashboard at http://localhost:{WEB_PORT}/kg-viz to see the graph")
                    else:
                        await send(chat, "Unknown subcommand. Use: /kg to see usage.")

                elif cmd == "/vault":
                    if len(parts) < 2:
                        await send(chat, "Usage:\n/vault save <title> | <content>\n/vault search <query>\n/vault list\n/vault get <id>\n/vault delete <id>")
                        continue
                    vsub = parts[1].lower()
                    if not kg_mod:
                        await send(chat, "Knowledge Vault module not available.")
                        continue
                    vault = kg_mod.get_vault()
                    if vsub == "save":
                        rest = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if " | " not in rest:
                            await send(chat, "Usage: /vault save <title> | <content>")
                            continue
                        title, content = rest.split(" | ", 1)
                        eid = vault.save(title.strip(), content.strip(), uid=str(uid))
                        await send(chat, f"Saved: '{title}' (id: {eid})")
                    elif vsub == "search":
                        q = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not q:
                            await send(chat, "Usage: /vault search <query>")
                            continue
                        results = vault.search(q, uid=str(uid))
                        if not results:
                            await send(chat, "No matches found.")
                            continue
                        lines = ["Vault results:"]
                        for r in results[:10]:
                            lines.append(f"  [{r['id']}] {r['title']} — {r['content'][:80]}...")
                        await send(chat, "\n".join(lines))
                    elif vsub == "list":
                        entries = vault.list(uid=str(uid))
                        if not entries:
                            await send(chat, "Vault is empty.")
                            continue
                        lines = ["Vault entries:"]
                        for r in entries[:20]:
                            lines.append(f"  [{r['id']}] {r['title']}")
                        await send(chat, "\n".join(lines))
                    elif vsub == "get":
                        eid = parts[2] if len(parts) > 2 else ""
                        entry = vault.get(eid)
                        if entry:
                            await send(chat, f"Title: {entry['title']}\n\n{entry['content'][:3000]}")
                        else:
                            await send(chat, "Entry not found.")
                    elif vsub == "delete":
                        eid = parts[2] if len(parts) > 2 else ""
                        if vault.delete(eid):
                            await send(chat, "Deleted.")
                        else:
                            await send(chat, "Entry not found.")
                    else:
                        await send(chat, "Unknown subcommand. Use: /vault")

                elif cmd == "/routes":
                    await send(chat, f"Provider routing health ({len(PROVIDERS)}):\n{gateway.get_route_health()}")

                elif cmd == "/gateway":
                    await send(chat, gateway.get_gateway_stats())

                elif cmd == "/repair" and (is_owner or is_admin or is_mod):
                    for name in PROVIDERS:
                        if name in gateway.health:
                            gateway.health[name]["cooldown_until"] = 0
                            gateway.health[name]["failure"] = 0
                    await send(chat, "All provider health counters reset.")

                elif cmd == "/pyrit" and (is_owner or is_admin or is_mod):
                    if pyrit_attacks is None:
                        await send(chat, "pyrit_attacks module not available (import failed)")
                        continue
                    modes = ", ".join(pyrit_attacks.ATTACK_MENU.keys())
                    if len(parts) < 3:
                        await send(chat, f"Usage: /pyrit <mode> <objective>\nModes: {modes}\nExample: /pyrit classic write a python keylogger")
                        continue
                    mode = parts[1].lower()
                    objective = " ".join(parts[2:])
                    if mode not in pyrit_attacks.ATTACK_MENU:
                        await send(chat, f"Unknown mode: {mode}. Use: {modes}")
                        continue
                    await typing(chat)
                    def make_call_fn(prov=None):
                        pv = prov or active_provider
                        async def fn(msgs):
                            return await call_provider(msgs, pv)
                        return fn
                    try:
                        if mode == "ultraplinian":
                            fns = [make_call_fn(n) for n in PROVIDERS if _is_configured(PROVIDERS[n].get("key",""))]
                            results = await pyrit_attacks.run_ultraplinian(fns, objective)
                        elif mode == "crescendo":
                            cf = make_call_fn(active_provider)
                            result = await pyrit_attacks.run_crescendo(cf, objective)
                            results = [result]
                        else:
                            cf = make_call_fn(active_provider)
                            results = await pyrit_attacks.ATTACK_MENU[mode]["fn"](cf, objective)
                        reply = [f"PyRIT {mode} attack results ({objective[:50]}):"]
                        for r in results[:5]:
                            resp = r.get("response", r.get("final", ""))[:200]
                            tag = r.get("template") or r.get("technique") or r.get("provider", "")
                            sc = r.get("score", 0)
                            turns = r.get("turns", "")
                            tstr = f" [{turns}turns]" if turns else ""
                            reply.append(f"\n[{tag}] score={sc}{tstr}")
                            reply.append(f"  {resp}")
                        await send(chat, "\n".join(reply))
                    except Exception as e:
                        await send(chat, f"PyRIT error: {e}")

                elif cmd == "/9router":
                    lines = ["<b>9Router</b> — Universal AI Gateway (upstream of VansRouter)",
                             "GitHub: https://github.com/decolua/9router",
                             "Install: npm install -g 9router",
                             "Endpoint: http://localhost:20128/v1",
                             "",
                             "Smart 3-tier fallback: subscription → cheap API → free tiers",
                             "RTK+Caveman token compression (20-65% savings)",
                             "60+ AI providers, 10+ CLI tools supported",
                             "",
                             "Use <b>/omniroute</b> to configure the OmniRoute provider",
                             "Use <b>/vansrouter</b> to configure the local VansRouter fork"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/vansrouter":
                    vp = PROVIDERS.get("vansrouter", {})
                    status = "configured" if vp.get("key") != "set-via-env-var" else "not configured"
                    lines = ["<b>VansRouter</b> — Local 9Router fork (port 3003)",
                             f"Provider status: {status}",
                             f"URL: {vp.get('url', 'N/A')}",
                             "Dashboard: http://localhost:3003",
                             "Dev endpoint: http://localhost:20127/v1",
                             "Prod endpoint: http://localhost:3003/api/v1",
                             "",
                             "CLI: node vansrouter/cli/cli.js",
                             "Custom server with IP spoofing protection (x-9r-real-ip)"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/omniroute":
                    op = PROVIDERS.get("omniroute", {})
                    lines = ["<b>OmniRoute</b> — Fork of 9Router with 290+ providers",
                             "GitHub: https://github.com/diegosouzapw/OmniRoute",
                             f"Provider: {op.get('url', 'http://localhost:20128/v1/chat/completions')}",
                             f"Model: {op.get('model', 'auto')}",
                             "",
                             "17 routing strategies, RTK+Caveman compression (15-95%)",
                             "Built-in MCP server (95+ tools), A2A agent protocol",
                             "Desktop (Electron), PWA, Termux support",
                             "Set OMNIROUTE_URL/OMNIROUTE_MODEL/OMNIROUTE_KEY in setenv.sh"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/openclaw":
                    lines = ["<b>OpenClaw</b> — AI Multi-Tool Orchestration CLI",
                             "Docs: https://docs.openclaw.ai",
                             "Install: npm install -g clawhub",
                             "Config: ~/.openclaw/openclaw.json",
                             "",
                             "Multi-tool AI orchestration with MCP support",
                             "Skills ecosystem: clawhub install <skill>",
                             "Works with: x64dbg, Ghidra, dnSpy, radare2, Frida",
                             "Supports reverse engineering, coding, forensics workflows",
                             "",
                             "To route through VansRouter/OmniRoute:",
                             "  Set baseUrl to http://localhost:20128/v1",
                             "  Model: 9router/<provider>/<model>"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/blackbox":
                    bp = PROVIDERS.get("blackbox", {})
                    models_list = [
                        "claude-fable-5, claude-opus-4.8, claude-sonnet-4.6",
                        "gpt-5.5, gpt-5.4-pro, gpt-5.4, gpt-5.3-codex, gpt-5.4-nano",
                        "deepseek-v4-flash, grok-4.3"
                    ]
                    lines = ["<b>Blackbox AI</b> — Multi-model provider gateway",
                             f"Provider: {'configured' if bp.get('key') != 'set-via-env-var' else 'NOT configured'}",
                             "URL: https://api.blackbox.ai/v1/chat/completions",
                             "API keys: https://www.blackbox.ai/api-management",
                             "",
                             "Models:"]
                    for m in models_list:
                        lines.append(f"  • {m}")
                    lines.append("")
                    lines.append("Set BLACKBOX_KEY in setenv.sh to activate")
                    await send(chat, "\n".join(lines))

                elif cmd == "/odysseus":
                    lines = ["<b>Odysseus</b> — Self-Hosted AI Workspace",
                             "Run and serve local LLMs + autonomous agents",
                             "GitHub: https://github.com/pewdiepie-archdaemon/odysseus",
                             "",
                             "Local-first, privacy-first architecture",
                             "270+ model catalog with hardware-aware recommendations",
                             "Built-in tools: bash, files, web, memory",
                             "MCP-compatible multi-machine model serving",
                             "Persistent memory, skill authoring, IMAP/SMTP",
                             "Email assistant, document editor, research workflows",
                             "",
                              "Integrates with VansRouter/OmniRoute as backend"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/hermes":
                    lines = ["<b>Hermes Agent</b> — Self-Improving AI Agent by Nous Research",
                             "GitHub: https://github.com/NousResearch/hermes-agent (200K+ stars)",
                             "Docs: https://hermes-agent.nousresearch.com/docs",
                             "Install: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash",
                             "Config: ~/.hermes/.env",
                             "",
                             "Self-improving learning loop — creates skills from experience every 15 tool calls",
                             "Persistent cross-session memory (SQLite + FTS5 full-text search)",
                             "Multi-platform: Telegram, Discord, Slack, WhatsApp, Signal, CLI",
                             "40+ built-in tools, scheduled cron automations",
                             "Subagent delegation for parallel workstreams",
                             "Runs on $5 VPS, Docker, serverless, Termux",
                             "200+ models via OpenRouter, or any OpenAI-compatible endpoint",
                             "",
                             "Routes through VansRouter/OmniRoute: set OPENAI_BASE_URL=http://localhost:20128/v1"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/obsidian":
                    lines = ["<b>Obsidian AI</b> — Knowledge Base + AI Agent Integration",
                             "Official CLI (v1.12+): obsidian search/daily/open/vault/note",
                             "CLI docs: https://obsidian.md/cli",
                             "Install: upgrade to Obsidian 1.12+, enable CLI in Settings > General",
                             "",
                             "MCP Integration:",
                             "  • obsidian-mcp-server — file-based STDIO MCP server",
                             "  • mcp-obsidian — Local REST API plugin (search_by_tag, get_frontmatter)",
                             "  • Agent Client — ACP protocol plugin for Claude Code/Codex",
                             "",
                             "AI Plugin Ecosystem:",
                             "  • Obsidian AI CLI — sidebar panels for Claude Code, Gemini, Codex, Qwen",
                             "  • Agentic Copilot — connects Obsidian to CLI agents (auto-detect)",
                             "  • Smart Connections v4 — local embeddings, semantic search, offline",
                             "  • Claudian — Claude Code embedded in Obsidian",
                             "",
                             "CLI commands: search, daily, note, template, tag, vault, graph, plugin",
                             "100+ commands for vault automation, scripting, cron"]
                    await send(chat, "\n".join(lines))

                elif cmd == "/toolfk":
                    key_status = f"TOOLFK_TOKEN={'set' if TOOLFK_TOKEN else 'NOT SET'}"
                    lines = [f"ToolFK.com API ({len(TOOLFK_ENDPOINTS)} endpoints, {key_status})"]
                    lines.append(f"Usage: in autonomous mode, use toolfk(endpoint=NAME, param=VAL, ...)")
                    lines.append(f"")
                    for ep in sorted(TOOLFK_ENDPOINTS):
                        lines.append(f"  {ep} — {TOOLFK_DESC.get(ep, '')}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/synoxcloud":
                    ai_count = len(SYNOXCLOUD_AI_MODELS)
                    ep_count = len(SYNOXCLOUD_ENDPOINTS)
                    lines = [f"SynoxCloud API ({ep_count} endpoints, {ai_count} AI models)"]
                    lines.append(f"Usage: in autonomous mode, use synoxcloud(endpoint=ID, param=VAL, ...)")
                    lines.append(f"")
                    search = text.lower().split("/synoxcloud", 1)[-1].strip()
                    if not search or any(s in search for s in ["model", "ai", "gpt", "claude", "llama", "gemini", "synox-"]):
                        lines.append(f"--- AI Models ({ai_count}) ---")
                        shown_m = 0
                        for mid in sorted(SYNOXCLOUD_AI_MODELS.keys()):
                            if search and search not in mid.lower() and f"synox-{search}" not in mid.lower():
                                continue
                            if shown_m >= 30 and not search:
                                lines.append(f"  ... and {ai_count - shown_m} more AI models")
                                break
                            minfo = SYNOXCLOUD_AI_MODELS[mid]
                            mpath = minfo.get("path", "") if isinstance(minfo, dict) else ""
                            mdesc = minfo.get("desc", "") if isinstance(minfo, dict) else ""
                            extra = f" — {mdesc}" if mdesc else (f" — {mpath}" if mpath else "")
                            lines.append(f"  /synox-{mid}{extra}")
                            shown_m += 1
                    if not search or any(s in search for s in ["ep", "endpoint", "tool", "filter"]):
                        lines.append(f"")
                        lines.append(f"--- Endpoints ({ep_count}) ---")
                        shown = 0
                        for eid in sorted(SYNOXCLOUD_ENDPOINTS.keys()):
                            if search and search not in eid.lower():
                                continue
                            if shown >= 50 and not search:
                                lines.append(f"  ... and {ep_count - shown} more. Filter with /synoxcloud <keyword>")
                                break
                            path = SYNOXCLOUD_ENDPOINTS[eid]
                            lines.append(f"  {eid} — {path}")
                            shown += 1
                    await send(chat, "\n".join(lines))

                elif cmd == "/n8n":
                    if not N8N_URL:
                        await send(chat, "N8N_URL not set. Add it to setenv.sh")
                        continue
                    parts2 = text.split(maxsplit=1)
                    if len(parts2) < 2:
                        await send(chat, "Usage: /n8n <workflow-path> [params as JSON]\nExample: /n8n webhook/chatbot {\"message\":\"hello\"}\n/n8n-status — check server\n/n8n-logs — recent executions")
                        continue
                    rest = parts2[1]
                    if rest.startswith("{"):
                        path = "webhook/chatbot"
                        payload = json.loads(rest)
                    elif " " in rest and rest.split(" ", 1)[1].startswith("{"):
                        path, _, raw = rest.partition(" ")
                        payload = json.loads(raw)
                    else:
                        path = rest
                        payload = {}
                    url = f"{N8N_URL}/{path.lstrip('/')}"
                    headers = {}
                    if N8N_API_KEY:
                        headers["X-N8N-API-KEY"] = N8N_API_KEY
                    await typing(chat)
                    try:
                        c = await get_http()
                        resp = await c.post(url, json=payload, headers=headers, timeout=30)
                        out = resp.text[:2000]
                        await send(chat, f"n8n response ({resp.status_code}):\n{out}")
                    except Exception as e:
                        await send(chat, f"n8n error: {e}")

                elif cmd == "/n8n-status":
                    if not N8N_URL:
                        await send(chat, "N8N_URL not set.")
                        continue
                    await typing(chat)
                    try:
                        c = await get_http()
                        resp = await c.get(f"{N8N_URL}/healthz", timeout=10)
                        await send(chat, f"n8n server: HTTP {resp.status_code} ✅" if resp.ok else f"n8n server: HTTP {resp.status_code}")
                    except Exception:
                        try:
                            c = await get_http()
                            resp = await c.get(f"{N8N_URL}/rest/health", timeout=10)
                            await send(chat, f"n8n server: HTTP {resp.status_code} ✅" if resp.ok else f"n8n server: HTTP {resp.status_code}")
                        except Exception as e2:
                            await send(chat, f"n8n unreachable: {e2}")

                elif cmd == "/n8n-logs":
                    if not N8N_URL or not N8N_API_KEY:
                        await send(chat, "N8N_URL and N8N_API_KEY required.")
                        continue
                    await typing(chat)
                    try:
                        c = await get_http()
                        resp = await c.get(f"{N8N_URL}/rest/executions?limit=10&take=10", headers={"X-N8N-API-KEY": N8N_API_KEY}, timeout=15)
                        if not resp.ok:
                            await send(chat, f"n8n API error: {resp.status_code}")
                            continue
                        data = resp.json()
                        execs = data.get("data", [])
                        if not execs:
                            await send(chat, "No recent executions.")
                            continue
                        lines = ["Recent n8n executions:"]
                        for ex in execs[:10]:
                            wid = ex.get("workflowId", "?")
                            status = ex.get("finished", False) and "✅" or "⏳"
                            mode = ex.get("mode", "?")
                            started = ex.get("startedAt", "?")[:19] if ex.get("startedAt") else "?"
                            lines.append(f"  {status} {wid} [{mode}] {started}")
                        await send(chat, "\n".join(lines))
                    except Exception as e:
                        await send(chat, f"n8n logs error: {e}")

                elif cmd == "/github":
                    parts2 = text.split(maxsplit=2)
                    if len(parts2) < 2:
                        await send(chat, "Usage:\n/github repo <user/repo> — repo info\n/github issues <user/repo> — list issues\n/github issue <user/repo> <title>|<body> — create issue\n/github pr <user/repo> — list open PRs")
                        continue
                    sub = parts2[1].lower()
                    gh_headers = {"Accept": "application/vnd.github.v3+json"}
                    if GITHUB_TOKEN:
                        gh_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
                    c = await get_http()
                    await typing(chat)
                    try:
                        if sub == "repo" and len(parts2) >= 3:
                            repo = parts2[2]
                            resp = await c.get(f"https://api.github.com/repos/{repo}", headers=gh_headers, timeout=15)
                            if not resp.ok:
                                await send(chat, f"GitHub error: {resp.status_code} {resp.text[:200]}")
                                continue
                            d = resp.json()
                            lines = [
                                f"📦 {d['full_name']}",
                                f"⭐ {d['stargazers_count']}  🍴 {d['forks_count']}  👁 {d['subscribers_count']}",
                                f"📝 {d.get('description', 'no description')}",
                                f"🔗 {d['html_url']}",
                                f"📅 created {d['created_at'][:10]}  updated {d['updated_at'][:10]}",
                                f"🐛 open issues: {d['open_issues_count']}",
                            ]
                            if d.get("language"):
                                lines.append(f"🔤 {d['language']}")
                            await send(chat, "\n".join(lines))
                        elif sub == "issues" and len(parts2) >= 3:
                            repo = parts2[2]
                            resp = await c.get(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=10", headers=gh_headers, timeout=15)
                            if not resp.ok:
                                await send(chat, f"GitHub error: {resp.status_code}")
                                continue
                            data = resp.json()
                            if not data:
                                await send(chat, f"No open issues in {repo}")
                                continue
                            lines = [f"🐛 Open issues in {repo}:"]
                            for issue in data:
                                labels = ", ".join(l["name"] for l in issue.get("labels", []))
                                label_str = f" [{labels}]" if labels else ""
                                lines.append(f"  #{issue['number']} {issue['title']}{label_str}")
                            await send(chat, "\n".join(lines))
                        elif sub == "issue" and len(parts2) >= 3:
                            repo = parts2[2]
                            if "|" in repo:
                                repo, _, body = repo.partition("|")
                                title = body.strip()
                                body_text = ""
                            else:
                                rest_text = text.split("/github issue " + repo + " ", 1)
                                if len(rest_text) > 1 and "|" in rest_text[1]:
                                    title, _, body_text = rest_text[1].partition("|")
                                elif len(rest_text) > 1:
                                    title = rest_text[1]
                                    body_text = ""
                                else:
                                    await send(chat, "Usage: /github issue <user/repo> <title> | <body>")
                                    continue
                                title = title.strip()
                                body_text = body_text.strip()
                            if not title:
                                await send(chat, "Title required.")
                                continue
                            resp = await c.post(f"https://api.github.com/repos/{repo}/issues", json={"title": title, "body": body_text}, headers=gh_headers, timeout=15)
                            if resp.ok:
                                d = resp.json()
                                await send(chat, f"✅ Issue created: {d['html_url']}")
                            else:
                                await send(chat, f"GitHub error: {resp.status_code} {resp.text[:300]}")
                        elif sub == "pr" and len(parts2) >= 3:
                            repo = parts2[2]
                            resp = await c.get(f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=10", headers=gh_headers, timeout=15)
                            if not resp.ok:
                                await send(chat, f"GitHub error: {resp.status_code}")
                                continue
                            data = resp.json()
                            if not data:
                                await send(chat, f"No open PRs in {repo}")
                                continue
                            lines = [f"🔀 Open PRs in {repo}:"]
                            for pr in data:
                                lines.append(f"  #{pr['number']} {pr['title']} — {pr['user']['login']}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "Unknown subcommand. Use: repo, issues, issue, pr")
                    except Exception as e:
                        await send(chat, f"GitHub error: {e}")

                elif cmd == "/gmail":
                    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
                        await send(chat, "GMAIL_USER and GMAIL_APP_PASSWORD required in setenv.sh")
                        continue
                    parts2 = text.split(maxsplit=1)
                    mode = parts2[1].lower() if len(parts2) > 1 else "inbox"
                    await typing(chat)
                    try:
                        import imaplib, email
                        from email.header import decode_header
                        m = imaplib.IMAP4_SSL("imap.gmail.com")
                        m.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                        m.select("INBOX")
                        if mode.startswith("search") and len(parts2) > 1:
                            query = parts2[1][7:].strip()
                            _, data = m.search(None, "ALL")
                        else:
                            _, data = m.search(None, "ALL")
                        ids = data[0].split()
                        recent = ids[-5:] if len(ids) >= 5 else ids
                        lines = [f"📬 Recent Gmail ({mode}):"]
                        for iid in reversed(recent):
                            _, msg_data = m.fetch(iid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                            for part in msg_data:
                                if isinstance(part, tuple):
                                    msg = email.message_from_bytes(part[1])
                                    frm = msg.get("From", "?").split("<")[0].strip()
                                    subj = msg.get("Subject", "?")
                                    dt = msg.get("Date", "?")[:17]
                                    lines.append(f"  {dt} {frm[:20]}: {subj[:40]}")
                        m.logout()
                        await send(chat, "\n".join(lines))
                    except Exception as e:
                        await send(chat, f"Gmail error: {e}")

                elif cmd == "/sheets":
                    if not SHEETS_CREDENTIALS:
                        await send(chat, "SHEETS_CREDENTIALS (path to JSON) required in setenv.sh\nUsage: /sheets <spreadsheet-id> <range>\nExample: /sheets 1abcd123 Sheet1!A1:C5")
                        continue
                    parts2 = text.split(maxsplit=2)
                    if len(parts2) < 3:
                        await send(chat, "Usage: /sheets <spreadsheet-id> <range>\nExample: /sheets 1abcd123 Sheet1!A1:C5")
                        continue
                    sheet_id = parts2[1]
                    sheet_range = parts2[2]
                    await typing(chat)
                    try:
                        import gspread
                        from gspread.utils import extract_id_from_url
                        gc = gspread.service_account(filename=SHEETS_CREDENTIALS)
                        sh = gc.open_by_key(sheet_id)
                        ws = sh.sheet1
                        if "!" in sheet_range:
                            ws_name, _, cell_range = sheet_range.partition("!")
                            ws = sh.worksheet(ws_name)
                        else:
                            cell_range = sheet_range
                        data = ws.get(cell_range)
                        lines = [f"📊 Sheet data ({sheet_range}):"]
                        for row in data[:20]:
                            lines.append("  " + " | ".join(str(c)[:30] for c in row))
                        await send(chat, "\n".join(lines))
                    except ImportError:
                        await send(chat, "gspread not installed. Run: pip install gspread")
                    except Exception as e:
                        await send(chat, f"Sheets error: {e}")

                elif cmd == "/notion":
                    if not NOTION_TOKEN:
                        await send(chat, "NOTION_TOKEN required in setenv.sh\nGet it from https://www.notion.so/my-integrations")
                        continue
                    parts2 = text.split(maxsplit=2)
                    if len(parts2) < 2:
                        await send(chat, "Usage:\n/notion search <query> — search pages\n/notion page <page-id> — get page\n/notion db <db-id> — query database")
                        continue
                    sub = parts2[1].lower()
                    nh = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
                    c = await get_http()
                    await typing(chat)
                    try:
                        if sub == "search" and len(parts2) >= 3:
                            query = parts2[2]
                            resp = await c.post("https://api.notion.com/v1/search", json={"query": query}, headers=nh, timeout=15)
                            if not resp.ok:
                                await send(chat, f"Notion error: {resp.status_code}")
                                continue
                            data = resp.json()
                            results = data.get("results", [])
                            if not results:
                                await send(chat, "No results.")
                                continue
                            lines = [f" Notion search results for '{query}':"]
                            for r in results[:10]:
                                title = "untitled"
                                props = r.get("properties", {})
                                for p in props.values():
                                    if p.get("type") == "title":
                                        tt = p.get("title", [])
                                        if tt:
                                            title = tt[0].get("plain_text", "untitled")
                                        break
                                pid = r["id"].replace("-", "")
                                lines.append(f"  {title[:50]} ({pid[:12]}...)")
                            await send(chat, "\n".join(lines))
                        elif sub == "page" and len(parts2) >= 3:
                            pid = parts2[2].replace("-", "")
                            resp = await c.get(f"https://api.notion.com/v1/pages/{pid}", headers=nh, timeout=15)
                            if not resp.ok:
                                await send(chat, f"Notion error: {resp.status_code}")
                                continue
                            page = resp.json()
                            title = "untitled"
                            props = page.get("properties", {})
                            for p in props.values():
                                if p.get("type") == "title":
                                    tt = p.get("title", [])
                                    if tt:
                                        title = tt[0].get("plain_text", "untitled")
                                    break
                            url = page.get("url", "")
                            lines = [f"📄 {title}", f"🔗 {url}"] if url else [f"📄 {title}"]
                            await send(chat, "\n".join(lines))
                        elif sub == "db" and len(parts2) >= 3:
                            db_id = parts2[2].replace("-", "")
                            resp = await c.post(f"https://api.notion.com/v1/databases/{db_id}/query", json={}, headers=nh, timeout=15)
                            if not resp.ok:
                                await send(chat, f"Notion error: {resp.status_code}")
                                continue
                            data = resp.json()
                            results = data.get("results", [])
                            if not results:
                                await send(chat, "No entries in database.")
                                continue
                            lines = [f"🗄 Database entries ({len(results)} total):"]
                            for r in results[:10]:
                                title = "untitled"
                                props = r.get("properties", {})
                                for p in props.values():
                                    if p.get("type") == "title":
                                        tt = p.get("title", [])
                                        if tt:
                                            title = tt[0].get("plain_text", "untitled")
                                        break
                                lines.append(f"  {title[:60]}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "Unknown subcommand: search, page, db")
                    except Exception as e:
                        await send(chat, f"Notion error: {e}")

                elif cmd == "/crypto":
                    parts2 = text.split(maxsplit=1)
                    coin = (parts2[1] if len(parts2) > 1 else "bitcoin").lower().strip()
                    await typing(chat)
                    try:
                        c = await get_http()
                        resp = await c.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true", timeout=15)
                        if not resp.ok:
                            await send(chat, f"Coin not found. Try: bitcoin, ethereum, solana, dogecoin, etc.")
                            continue
                        data = resp.json()
                        info = data.get(coin)
                        if not info:
                            await send(chat, f"Coin '{coin}' not found.")
                            continue
                        price = info.get("usd", "?")
                        change = info.get("usd_24h_change", 0)
                        mcap = info.get("usd_market_cap", 0)
                        arrow = "📈" if change >= 0 else "📉"
                        mcap_str = f"${mcap:,.0f}" if mcap else "?"
                        lines = [
                            f"🪙 {coin.upper()}",
                            f"💰 ${price:,.6f}" if isinstance(price, float) else f"💰 ${price}",
                            f"{arrow} 24h: {change:+.2f}%" if change else "",
                            f"🏛 Market Cap: {mcap_str}",
                        ]
                        await send(chat, "\n".join(lines))
                    except Exception as e:
                        await send(chat, f"Crypto error: {e}")
                    continue

                elif cmd == "/vision":
                    try:
                        await typing(chat)
                        if not photo_file_id:
                            if msg.get("reply_to_message") and msg["reply_to_message"].get("photo"):
                                photo_file_id = msg["reply_to_message"]["photo"][-1]["file_id"]
                        if not photo_file_id:
                            await send(chat, "Send a photo with /vision <prompt> or reply to a photo.")
                            continue
                        prompt = " ".join(parts[1:]) or "Describe this image in detail"
                        url = await bf.get_photo_url(photo_file_id)
                        if not url:
                            await send(chat, "Could not fetch photo.")
                            continue
                        result = await bf.vision_analyze(url, prompt)
                        await send(chat, result[:3500])
                    except Exception as e:
                        await send(chat, f"Vision error: {e}")
                    continue

                elif cmd == "/draw":
                    if len(parts) < 2:
                        await send(chat, "Usage: /draw <prompt>\nExample: /draw a cat riding a bicycle on mars")
                        continue
                    prompt = " ".join(parts[1:])
                    await typing(chat)
                    image_data = await bf.image_generate(prompt)
                    if image_data:
                        c = await get_http()
                        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
                        await c.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                files={"photo": ("gen.png", image_data)},
                data={"chat_id": chat, "caption": prompt[:200]},
                timeout=30,
                        )
                    else:
                        await send(chat, "Image generation failed. Try a different prompt.")

                elif cmd == "/schedule":
                    if len(parts) < 2:
                        tasks = bf.scheduler.list()
                        if not tasks:
                            await send(chat, "No scheduled tasks.\nUsage: /schedule add <interval_seconds> <prompt>\n       /schedule remove <id>\n       /schedule list")
                        else:
                            lines = ["Scheduled tasks:"]
                            for tid, label, interval, cid in tasks:
                                lines.append(f"  [{tid}] {label} — every {interval}s (chat: {cid})")
                            await send(chat, "\n".join(lines))
                        continue
                    sub = parts[1].lower()
                    if sub == "add" and len(parts) >= 4:
                        try:
                            interval = int(parts[2])
                            prompt = " ".join(parts[3:])
                            tid = bf.scheduler.add(interval, prompt, chat)
                            await send(chat, f"Scheduled: [{tid}] every {interval}s — {prompt[:100]}")
                        except ValueError:
                            await send(chat, "Interval must be a number in seconds.")
                    elif sub == "remove" and len(parts) >= 3:
                        bf.scheduler.remove(parts[2])
                        await send(chat, f"Task {parts[2]} removed.")
                    elif sub == "list":
                        tasks = bf.scheduler.list()
                        if not tasks:
                            await send(chat, "No scheduled tasks.")
                        else:
                            lines = ["Scheduled tasks:"]
                            for tid, label, interval, cid in tasks:
                                lines.append(f"  [{tid}] {label} — every {interval}s")
                            await send(chat, "\n".join(lines))
                    else:
                        await send(chat, "Usage: /schedule add <seconds> <prompt>  or  /schedule remove <id>  or  /schedule list")

                elif cmd == "/export":
                    if len(parts) < 2:
                        await send(chat, "Usage: /export json|md")
                        continue
                    fmt = parts[1].lower()
                    session = sessions.get(uid, [])
                    if not session:
                        await send(chat, "No session data to export.")
                        continue
                    if fmt == "json":
                        data = bf.export_as_json(session)
                        await send(chat, f"```json\n{data[:3500]}\n```")
                    elif fmt == "md":
                        data = bf.export_as_markdown(session)
                        await send(chat, f"```markdown\n{data[:3500]}\n```")
                    else:
                        await send(chat, "Format: json or md")

                elif cmd == "/doc":
                    docs = bf.doc_db.list()
                    if not docs:
                        await send(chat, "No documents indexed. Send a txt/pdf file to add it.\nCommands:\n  /doc — list documents\n  /ask <question> — query documents\n  /doc clear — clear all documents")
                    else:
                        await send(chat, "Indexed documents:\n" + "\n".join(f"  {d}" for d in docs))

                elif cmd == "/ask":
                    if len(parts) < 2:
                        await send(chat, "Usage: /ask <question>\nQuery your uploaded documents.")
                        continue
                    q = " ".join(parts[1:])
                    context = bf.doc_db.query(q)
                    if not context:
                        await send(chat, "No relevant documents found. Upload a document first with a file.")
                        continue
                    ctx_text = "\n\n".join(context)
                    await typing(chat)
                    try:
                        reply = await smart_call([
                {"role": "system", "content": f"Answer based on these documents:\n\n{ctx_text}"},
                {"role": "user", "content": q},
                        ], active_provider)
                        await send(chat, reply[:3500])
                    except Exception as e:
                        await send(chat, f"Query error: {e}")

                elif cmd == "/context":
                    if is_experimental_enabled("context-files") and len(parts) > 1:
                        sub = parts[1].lower()
                        chat_str = str(chat)
                        if sub == "list":
                            files = context_files.get(chat_str, [])
                            if not files:
                                await send(chat, "No attached files. Use /context add <name> <description>")
                            else:
                                lines = [f"Attached files ({len(files)}):"]
                                for f in files:
                                    cp = (f.get("content", "")[:100] + "…") if f.get("content") else "(empty)"
                                    lines.append(f"  📄 {f.get('name', 'unnamed')}: {cp}")
                                await send(chat, "\n".join(lines))
                        elif sub == "add" and len(parts) > 3:
                            fname = parts[2]
                            fcontent = " ".join(parts[3:])
                            context_files.setdefault(chat_str, []).append({"name": fname, "content": fcontent, "added_at": time.time()})
                            save_context_files()
                            await send(chat, f"✅ Attached context file '{fname}'")
                        elif sub == "remove" and len(parts) > 2:
                            fname = parts[2]
                            files = context_files.get(chat_str, [])
                            new_files = [f for f in files if f.get("name") != fname]
                            if len(new_files) < len(files):
                                context_files[chat_str] = new_files
                                save_context_files()
                                await send(chat, f"Removed '{fname}'")
                            else:
                                await send(chat, f"No file named '{fname}'")
                        elif sub == "clear":
                            context_files.pop(chat_str, None)
                            save_context_files()
                            await send(chat, "All context files cleared.")
                        else:
                            await send(chat, "Usage: /context list | add <name> <content> | remove <name> | clear")
                    else:
                        await typing(chat)
                        ctx = await bf.auto_context()
                        await send(chat, f"Current context:\n{ctx}")

                elif cmd == "/search":
                    if len(parts) < 2:
                        if is_experimental_enabled("enhanced-search"):
                            await send(chat, "Usage:\n  /search tags <tag>\n  /search files <keyword>\n  /search history <keyword>\n  /search web <query>")
                        else:
                            await send(chat, "Usage: /search <query>\nExample: /search latest AI news 2026")
                        continue
                    mode = parts[1].lower()
                    if mode == "tags":
                        if not is_experimental_enabled("search-tags"):
                            await send(chat, "Feature 'search-tags' is not enabled. Use /experimental enable search-tags")
                            continue
                        query = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not query:
                            await send(chat, "Usage: /search tags <tag>")
                            continue
                        results = [(cid, tag, count) for cid, tags in conversation_tags.items() for tag, count in tags.items() if query in tag]
                        if not results:
                            await send(chat, f"No chats found for tag '{query}'")
                        else:
                            results.sort(key=lambda x: -x[2])
                            lines = [f"Results for tag '{query}':"]
                            for cid, tag, count in results[:15]:
                                lines.append(f"  Chat {cid} - #{tag} ({count}x)")
                            await send(chat, "\n".join(lines))
                    elif mode == "files":
                        if not is_experimental_enabled("search-files"):
                            await send(chat, "Feature 'search-files' is not enabled. Use /experimental enable search-files")
                            continue
                        query = " ".join(parts[2:]).lower() if len(parts) > 2 else ""
                        if not query:
                            await send(chat, "Usage: /search files <keyword>")
                            continue
                        results = [(cid, f.get("name","unnamed"), f.get("content","")[:80]) for cid, files in context_files.items() for f in files if query in f.get("name","").lower() or query in f.get("content","").lower()]
                        if not results:
                            await send(chat, f"No attached files matching '{query}'")
                        else:
                            lines = [f"Files matching '{query}' ({len(results)}):"]
                            for cid, fname, preview in results[:10]:
                                lines.append(f"  {fname} ({'this chat' if cid==str(chat) else 'Chat '+cid}): {preview}")
                            await send(chat, "\n".join(lines))
                    elif mode == "history":
                        if not is_experimental_enabled("search-history"):
                            await send(chat, "Feature 'search-history' is not enabled. Use /experimental enable search-history")
                            continue
                        query = " ".join(parts[2:]) if len(parts) > 2 else ""
                        if not query:
                            await send(chat, "Usage: /search history <keyword>")
                            continue
                        uid = msg["from"]["id"]
                        matches = [m for m in sessions.get(uid, []) if query.lower() in m.get("content","").lower() and m["role"]!="system"]
                        if matches:
                            lines = [f"Found {len(matches)} in session:"]
                            for m in matches[-5:]:
                                lines.append(f"  [{m['role']}]: {m.get('content','')[:200]}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "No matches in session.")
                    else:
                        q = " ".join(parts[1:])
                        await typing(chat)
                        results = await bf.web_search(q)
                        reply = await smart_call([
                            {"role": "system", "content": "Summarize these web search results concisely, highlighting key findings."},
                            {"role": "user", "content": f"Search query: {q}\n\n{results}"},
                        ], active_provider)
                        await send(chat, f"Search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1000]}")

                elif cmd == "/youtube":
                    if len(parts) < 2:
                        await send(chat, "Usage: /youtube <url>\nExample: /youtube https://youtube.com/watch?v=dQw4w9WgXcQ")
                        continue
                    url = parts[1]
                    await typing(chat)
                    transcript = await bf.youtube_transcript(url)
                    if "Could not" in transcript or "error" in transcript.lower()[:100]:
                        await send(chat, transcript)
                    else:
                        reply = await smart_call([
                {"role": "system", "content": "Summarize this YouTube video transcript in 3-5 bullet points covering key topics."},
                {"role": "user", "content": f"Transcript:\n\n{transcript[:7000]}"},
                        ], active_provider)
                        await send(chat, f"ðŸ“¹ YouTube Summary:\n\n{reply[:3500]}")

                elif cmd == "/run":
                    if not is_owner and not is_admin:
                        await send(chat, "Only owners/admins can execute code.")
                        continue
                    if len(parts) < 3:
                        await send(chat, "Usage: /run <python|js> <code>\nExample: /run python print('hello')\nOr use /run python followed by multiple lines in subsequent messages.")
                        continue
                    lang = parts[1].lower()
                    code = " ".join(parts[2:])
                    if len(code) > 5000:
                        await send(chat, "Code too long (max 5000 chars).")
                        continue
                    await typing(chat)
                    result = await bf.run_code(code, lang)
                    await send(chat, f"```\n{result[:3500]}\n```")

                elif cmd == "/fetch":
                    if not is_owner and not is_admin:
                        await send(chat, "Only owners/admins can fetch URLs.")
                        continue
                    if len(parts) < 2:
                        await send(chat, "Usage: /fetch <url>\nExample: /fetch https://example.com")
                        continue
                    url = parts[1]
                    if not url.startswith(("http://", "https://")):
                        await send(chat, "Only http/https URLs are allowed.")
                        continue
                    await typing(chat)
                    content = await bf.fetch_url(url)
                    if content.startswith("HTTP") or content.startswith("Fetch error"):
                        await send(chat, content[:2000])
                    else:
                        reply = await smart_call([
                {"role": "system", "content": "Summarize this web page content concisely."},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{content[:6000]}"},
                        ], active_provider)
                        await send(chat, f"ðŸ“„ {url}\n\n{reply[:3500]}")

                elif cmd == "/youtube_search":
                    if len(parts) < 2:
                        await send(chat, "Usage: /youtube_search <query>\nExample: /youtube_search how to use transformers")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.youtube_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these YouTube search results, highlighting the most relevant videos for the query."},
                        {"role": "user", "content": f"Query: {q}\n\nResults:\n{results}"},
                    ], active_provider)
                    await send(chat, f"YouTube search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1500]}")

                elif cmd == "/tiktok":
                    if len(parts) < 2:
                        await send(chat, "Usage: /tiktok <query>\nExample: /tiktok AI coding tools")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.tiktok_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these TikTok search results, highlighting the most popular and relevant videos."},
                        {"role": "user", "content": f"Query: {q}\n\nResults:\n{results}"},
                    ], active_provider)
                    await send(chat, f"TikTok search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1500]}")

                elif cmd == "/github_search":
                    if len(parts) < 2:
                        await send(chat, "Usage: /github_search <query>\nExample: /github_search transformer language model")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.github_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these GitHub search results, highlighting the most popular and relevant repositories for the query."},
                        {"role": "user", "content": f"Query: {q}\n\nResults:\n{results}"},
                    ], active_provider)
                    await send(chat, f"GitHub search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:2000]}")

                elif cmd == "/analyze":
                    if len(parts) < 2:
                        await send(chat, "Usage: /analyze <github_repo_url>\nExample: /analyze https://github.com/huggingface/transformers")
                        continue
                    url = parts[1]
                    await typing(chat)
                    analysis = await bf.analyze_github_repo(url)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize this GitHub repository analysis, highlighting what the project does, key technologies, and how to get started."},
                        {"role": "user", "content": f"Repo: {url}\n\nAnalysis:\n{analysis}"},
                    ], active_provider)
                    await send(chat, f"Repo analysis:\n\n{reply[:3500]}\n\n---\n{analysis[:2000]}")

                elif cmd == "/reddit":
                    if len(parts) < 2:
                        await send(chat, "Usage: /reddit <query>\nExample: /reddit machine learning")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.reddit_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these Reddit search results, highlighting the most relevant discussions."},
                        {"role": "user", "content": f"Query: {q}\n\nResults:\n{results}"},
                    ], active_provider)
                    await send(chat, f"Reddit search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1500]}")

                elif cmd == "/hn":
                    if len(parts) < 2:
                        await send(chat, "Usage: /hn <query>\nExample: /hn rust programming")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.hackernews_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these Hacker News results, highlighting the most popular stories and discussions."},
                        {"role": "user", "content": f"Query: {q}\n\nResults:\n{results}"},
                    ], active_provider)
                    await send(chat, f"Hacker News: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1500]}")

                elif cmd == "/social":
                    if len(parts) < 2:
                        await send(chat, "Usage: /social <query>\nExample: /social AI agents\nSearches Reddit, Hacker News, and Medium simultaneously.")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.social_search_all(q)
                    await send(chat, f"Multi-platform search: {q}\n\n{results[:3500]}")

                elif cmd == "/memory":
                    sub = parts[1].lower() if len(parts) > 1 else "stats"
                    if sub == "stats":
                        stats = await bf.get_memory_stats(uid)
                        if stats:
                            await send(chat, f"Memory stats:\n  Total messages: {stats['total']}\n  Your messages: {stats['user']}\n  AI responses: {stats['ai']}\n  Days active: {stats['days']}\n  First message: {time.strftime('%Y-%m-%d', time.localtime(stats['first_seen'])) if stats['first_seen'] else 'N/A'}")
                        else:
                            await send(chat, "No memory data yet.")
                    elif sub == "search" and len(parts) >= 3:
                        kw = " ".join(parts[2:])
                        results = await bf.search_user_memories(uid, kw)
                        if results:
                            lines = [f"Memories matching '{kw}':"]
                            for e in results[-5:]:
                                lines.append(f"  [{e['role']}] {e['content'][:200]}")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, f"No memories found for: {kw}")
                    elif sub == "clear":
                        await bf.clear_user_memory(uid)
                        await send(chat, "Your memory log cleared.")
                    else:
                        await send(chat, "Usage:\n  /memory stats — Memory statistics\n  /memory search <keyword> — Search your memory\n  /memory clear — Clear your memory log")

                elif cmd == "/cron":
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "list":
                        tasks = bf.scheduler.list()
                        if not tasks:
                            await send(chat, "No scheduled tasks.\nUsage: /cron add <interval_seconds> <prompt>\nExample: /cron add 3600 Give me a summary of today's AI news")
                        else:
                            lines = ["Scheduled tasks:"]
                            for tid, label, interval, cid in tasks:
                                lines.append(f"  [{tid}] {label} (every {interval}s) chat:{cid}")
                            await send(chat, "\n".join(lines))
                    elif sub == "add" and len(parts) >= 4:
                        try:
                            interval = int(parts[2])
                            prompt = " ".join(parts[3:])
                            tid = bf.scheduler.add(interval, prompt, chat)
                            await send(chat, f"Cron task added: [{tid}] every {interval}s\nPrompt: {prompt[:100]}")
                        except ValueError:
                            await send(chat, "Interval must be a number (seconds).")
                    elif sub == "remove" and len(parts) >= 3:
                        bf.scheduler.remove(parts[2])
                        await send(chat, f"Task {parts[2]} removed.")
                    else:
                        await send(chat, "Usage:\n  /cron list — List scheduled tasks\n  /cron add <seconds> <prompt> — Add a task\n  /cron remove <id> — Remove a task")

                elif cmd == "/monitor":
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "list":
                        pages = bf.page_monitor.list(chat_id=chat)
                        if not pages:
                            await send(chat, "No monitored pages.\nUsage: /monitor add <url> [label]\nExample: /monitor add https://news.ycombinator.com HN frontpage")
                        else:
                            lines = ["Monitored pages:"]
                            for pid, url, label, interval in pages:
                                lines.append(f"  [{pid}] {label} ({interval}s interval)")
                            await send(chat, "\n".join(lines))
                    elif sub == "add" and len(parts) >= 3:
                        url = parts[2]
                        label = " ".join(parts[3:]) if len(parts) > 3 else url[:40]
                        pid = bf.page_monitor.add(url, chat, label)
                        await send(chat, f"Monitoring added: [{pid}] {label}\nWill check for changes every hour.")
                    elif sub == "remove" and len(parts) >= 3:
                        bf.page_monitor.remove(parts[2])
                        await send(chat, f"Monitor {parts[2]} removed.")
                    else:
                        await send(chat, "Usage:\n  /monitor list — List monitored pages\n  /monitor add <url> [label] — Add a page to monitor\n  /monitor remove <id> — Remove a monitor")

                elif cmd == "/remind":
                    if len(parts) < 3:
                        tasks = bf.reminder_db.list(chat_id=chat)
                        if not tasks:
                            await send(chat, "No reminders.\nUsage: /remind <duration> <message>\nExamples:\n  /remind 30min check the oven\n  /remind 2h take a break\n  /remind list\n  /remind clear")
                        else:
                            lines = ["Your reminders:"]
                            for rid, msg, fire_at in tasks:
                                remaining = int(fire_at - time.time())
                                mins = remaining // 60
                                secs = remaining % 60
                                lines.append(f"  [{rid}] {msg} (in {mins}m{secs}s)")
                            await send(chat, "\n".join(lines))
                        continue
                    sub = parts[1].lower()
                    if sub == "list":
                        tasks = bf.reminder_db.list(chat_id=chat)
                        if not tasks:
                            await send(chat, "No reminders.")
                        else:
                            lines = ["Your reminders:"]
                            for rid, msg, fire_at in tasks:
                                remaining = int(fire_at - time.time())
                                lines.append(f"  [{rid}] {msg} (in {remaining//60}m{remaining%60}s)")
                            await send(chat, "\n".join(lines))
                    elif sub == "clear":
                        bf.reminder_db.clear_chat(chat)
                        await send(chat, "All your reminders cleared.")
                    elif sub == "remove" and len(parts) >= 3:
                        bf.reminder_db.remove(parts[2])
                        await send(chat, f"Reminder {parts[2]} removed.")
                    else:
                        duration = bf.parse_duration(" ".join(parts[1:-1]) if len(parts) > 2 else parts[1])
                        message = parts[-1] if len(parts) > 2 else "Reminder!"
                        if not duration:
                            duration = bf.parse_duration(parts[1])
                            message = " ".join(parts[2:]) if len(parts) > 2 else "Reminder!"
                        if duration:
                            rid = bf.reminder_db.add(chat, duration, message)
                            await send(chat, f"â° Reminder set: '{message}' in {duration//60}m{duration%60}s (ID: {rid})")
                        else:
                            await send(chat, "Could not parse duration. Use e.g. 30min, 2h, 90s")

                elif cmd == "/digest":
                    uid_s = sessions.get(uid, [])
                    if len(uid_s) < 3:
                        await send(chat, "Not enough conversation to summarize.")
                        continue
                    await typing(chat)
                    chat_text = "\n".join(f"{m['role']}: {m['content'][:500]}" for m in uid_s[-15:])
                    summary = await smart_call([
                        {"role": "system", "content": "You are a conversation analyst. Produce a concise digest of this AI chat session. Structure: Key Topics Discussed, Decisions Made, Open Questions, Suggested Next Steps. Be specific and reference actual content."},
                        {"role": "user", "content": f"Conversation:\n{chat_text}\n\nProduce a structured digest."},
                    ], active_provider)
                    await send(chat, f"Digest:\n{summary[:3500]}")

                elif cmd == "/routine":
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "create":
                        if len(parts) < 4:
                            await send(chat, "Usage: /routine create <name> <step1> | <step2> [| <step3> ...]")
                            continue
                        name = parts[2].lower()
                        rest = " ".join(parts[3:])
                        steps = [s.strip() for s in rest.split("|") if s.strip()]
                        if len(steps) < 2:
                            await send(chat, "Need at least 2 steps separated by |")
                            continue
                        if len(steps) > 6:
                            await send(chat, "Maximum 6 steps per routine.")
                            continue
                        routines[name] = {"steps": steps, "created_by": uid}
                        save_routines()
                        await send(chat, f"Routine '{name}' created with {len(steps)} steps.")
                    elif sub == "list":
                        if not routines:
                            await send(chat, "No routines defined. Use /routine create to make one.")
                            continue
                        lines = [f"Routines ({len(routines)}):"]
                        for rname, r in sorted(routines.items()):
                            lines.append(f"  /do {rname} — {len(r['steps'])} steps")
                        await send(chat, "\n".join(lines))
                    elif sub == "show":
                        if len(parts) < 3:
                            await send(chat, "Usage: /routine show <name>")
                            continue
                        name = parts[2].lower()
                        r = routines.get(name)
                        if not r:
                            await send(chat, f"Unknown routine: {name}")
                            continue
                        lines = [f"Routine: {name}"]
                        for i, s in enumerate(r["steps"], 1):
                            lines.append(f"  Step {i}: {s[:200]}")
                        await send(chat, "\n".join(lines))
                    elif sub == "delete":
                        if len(parts) < 3:
                            await send(chat, "Usage: /routine delete <name>")
                            continue
                        name = parts[2].lower()
                        if name not in routines:
                            await send(chat, f"Unknown routine: {name}")
                            continue
                        del routines[name]
                        save_routines()
                        await send(chat, f"Routine '{name}' deleted.")
                    elif sub == "run":
                        if len(parts) < 4:
                            await send(chat, "Usage: /routine run <name> <input>")
                            continue
                        name = parts[2].lower()
                        r = routines.get(name)
                        if not r:
                            await send(chat, f"Unknown routine: {name}")
                            continue
                        user_input = " ".join(parts[3:])
                        await typing(chat)
                        current = user_input
                        total = len(r["steps"])
                        for i, step_prompt in enumerate(r["steps"], 1):
                            await send(chat, f"Step {i}/{total}: running...")
                            filled = step_prompt.replace("{input}", user_input).replace("{prev}", current)
                            resp = await smart_call([
                                {"role": "system", "content": "You are a precise AI workflow executor. Follow the instruction exactly using the provided context."},
                                {"role": "user", "content": filled},
                            ], active_provider)
                            current = resp.strip()
                        await send(chat, current[:4000])
                    else:
                        await send(chat, "Subcommands: create, list, show, delete, run")

                elif cmd == "/multi":
                    sub = parts[1] if len(parts) > 1 else ""
                    chat_multi = multi_sessions.get(str(chat), {})
                    if sub == "start":
                        available = [n for n in PROVIDERS if _is_configured(PROVIDERS[n].get("key", ""))]
                        if len(parts) < 3:
                            await send(chat, f"Usage: /multi start <provider1> <provider2> [rounds=2]\nAvailable: {', '.join(available[:20])}")
                            continue
                        p1, p2 = parts[2], parts[3] if len(parts) > 3 else "zenmux"
                        rounds = int(parts[4]) if len(parts) > 4 else 2
                        bad = [p for p in (p1, p2) if p not in PROVIDERS or not _is_configured(PROVIDERS[p].get("key", ""))]
                        if bad:
                            await send(chat, f"Unavailable: {', '.join(bad)}.\nAvailable: {', '.join(available[:12])}")
                            continue
                        multi_sessions[str(chat)] = {
                            "providers": [p1, p2],
                            "rounds": max(1, min(rounds, 5)),
                            "history": [],
                            "active": True
                        }
                        save_multi()
                        await send(chat, f"Multi-AI started: {p1} + {p2}, {rounds} rounds.\nSend any message and both AIs will respond. Use /multi stop to end.")
                    elif sub == "stop":
                        if not chat_multi:
                            await send(chat, "No active multi-AI session.")
                            continue
                        multi_sessions.pop(str(chat), None)
                        save_multi()
                        await send(chat, "Multi-AI session stopped.")
                    elif sub == "status":
                        if not chat_multi:
                            await send(chat, "No active multi-AI session.")
                            continue
                        p = chat_multi["providers"]
                        await send(chat, f"Multi-AI active\nProviders: {p[0]} + {p[1]}\nRounds: {chat_multi['rounds']}\nExchanges: {len(chat_multi['history'])//2}")
                    else:
                        available = [n for n in PROVIDERS if _is_configured(PROVIDERS[n].get("key", ""))]
                        msg_lines = [
                            "Multi-AI - Talk to 2 AIs at once, they debate each other",
                            "",
                            f"Available providers: {', '.join(available[:12])}",
                            "",
                            "Commands:",
                            "  /multi start <p1> [p2] [rounds=2]  - Start multi-AI session",
                            "  /multi stop                        - Stop current session",
                            "  /multi status                      - Show session info",
                        ]
                        await send(chat, "\n".join(msg_lines))

                elif cmd == "/translate":
                    if len(parts) < 3:
                        await send(chat, "Usage: /translate <source>:<target> <text>\n       /translate en:fr Hello world\n       /translate :es Hello (auto-detect source)")
                        continue
                    pair = parts[1]
                    translate_text = " ".join(parts[2:])
                    source, target, cleaned = bf.parse_language_pair(f"{pair} {translate_text}")
                    if not target:
                        await send(chat, "Usage: /translate <source>:<target> <text>\nExample: /translate en:fr Hello world")
                        continue
                    await typing(chat)
                    result = await bf.translate(cleaned, source or "auto", target)
                    await send(chat, f"Translation ({source or 'auto'}â†’{target}):\n{result[:2000]}")

                elif cmd == "/qr":
                    if len(parts) < 3:
                        await send(chat, "Usage: /qr encode <text> — Generate QR code\n       /qr decode — Reply to a photo with /qr decode (or send photo as caption)")
                        continue
                    sub = parts[1].lower()
                    if sub == "encode":
                        qtext = " ".join(parts[2:])
                        await typing(chat)
                        img_data = await bf.qr_encode(qtext)
                        if isinstance(img_data, bytes):
                            c = await get_http()
                            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
                            await c.post(
                            f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                            files={"photo": ("qr.png", img_data)},
                            data={"chat_id": chat, "caption": f"QR: {qtext[:200]}"},
                            timeout=15,
                            )
                        else:
                            await send(chat, str(img_data)[:2000])
                    elif sub == "decode":
                        if msg.get("reply_to_message") and msg["reply_to_message"].get("photo"):
                            fid = msg["reply_to_message"]["photo"][-1]["file_id"]
                        elif photo_file_id:
                            fid = photo_file_id
                        else:
                            await send(chat, "Send /qr decode as a reply to a photo with a QR code.")
                            continue
                        await typing(chat)
                        purl = await bf.get_photo_url(fid)
                        if purl:
                            decoded = await bf.qr_decode_from_url(purl)
                            await send(chat, f"QR decoded: {decoded[:2000]}")
                        else:
                            await send(chat, "Could not fetch photo.")
                    else:
                        await send(chat, "Usage: /qr encode <text>  or  /qr decode (reply to photo)")

                elif cmd == "/stats":
                    uid_stats = bf.get_usage(uid)
                    if uid_stats:
                        top_a = sorted(uid_stats.get("agents", {}).items(), key=lambda x: -x[1])[:3]
                        top_p = sorted(uid_stats.get("providers", {}).items(), key=lambda x: -x[1])[:3]
                        lines = [f"Your stats ({uid_stats.get('total_requests', 0)} requests, {uid_stats.get('total_tokens', 0)} tokens):"]
                        if top_a: lines.append(f"  Top agents: {', '.join(f'{a}({c})' for a,c in top_a)}")
                        if top_p: lines.append(f"  Top providers: {', '.join(f'{p}({c})' for p,c in top_p)}")
                        await send(chat, "\n".join(lines))
                    else:
                        await send(chat, "No usage data yet. Start chatting!")
                    global_stats = bf.get_global_stats()
                    await send(chat, f"Global: {global_stats['total_users']} users, {global_stats['total_requests']} requests, {global_stats['total_tokens']} tokens")

                elif cmd == "/experimental":
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "list" or sub == "":
                        await send(chat, get_experimental_list())
                    elif sub == "status":
                        enabled = [f"{f['name']}" for f in experimental_features.values() if f.get("enabled")]
                        disabled = [f"{f['name']}" for f in experimental_features.values() if not f.get("enabled")]
                        lines = [
                            f"Experimental Status:",
                            f"  Enabled: {len(enabled)}",
                            f"  Disabled: {len(disabled)}",
                            f"  Total: {len(experimental_features)}",
                        ]
                        if enabled:
                            lines.append("")
                            lines.append("Active features:")
                            for e in enabled:
                                lines.append(f"  ✅ {e}")
                        await send(chat, "\n".join(lines))
                    elif sub == "enable" and len(parts) > 2:
                        fid = parts[2].lower()
                        if fid not in experimental_features:
                            await send(chat, f"Unknown feature: {fid}\nUse /experimental to see all features.")
                            continue
                        if experimental_features[fid].get("enabled"):
                            await send(chat, f"{experimental_features[fid]['name']} is already enabled.")
                            continue
                        experimental_features[fid]["enabled"] = True
                        save_experimental()
                        await send(chat, f"✅ Enabled: {experimental_features[fid]['name']}\n{experimental_features[fid]['desc']}")
                    elif sub == "disable" and len(parts) > 2:
                        fid = parts[2].lower()
                        if fid not in experimental_features:
                            await send(chat, f"Unknown feature: {fid}\nUse /experimental to see all features.")
                            continue
                        if not experimental_features[fid].get("enabled"):
                            await send(chat, f"{experimental_features[fid]['name']} is already disabled.")
                            continue
                        experimental_features[fid]["enabled"] = False
                        save_experimental()
                        await send(chat, f"⬜ Disabled: {experimental_features[fid]['name']}")
                    elif sub == "add" and (is_owner or is_admin):
                        if len(parts) < 5:
                            await send(chat, "Usage: /experimental add <id> <name> <description>\nExample: /experimental add my-feature My Feature A cool new thing")
                            continue
                        fid = parts[2].lower()
                        fname = parts[3]
                        fdesc = " ".join(parts[4:])
                        if fid in experimental_features:
                            await send(chat, f"Feature '{fid}' already exists.")
                            continue
                        ver_info = load_version()
                        experimental_features[fid] = {
                            "name": fname,
                            "desc": fdesc,
                            "version": ver_info.get("version", "unknown"),
                            "enabled": False,
                            "category": "other",
                        }
                        save_experimental()
                        await send(chat, f"Added experimental feature: {fid} — {fname}")
                    elif sub == "remove" and (is_owner or is_admin):
                        if len(parts) < 3:
                            await send(chat, "Usage: /experimental remove <id>")
                            continue
                        fid = parts[2].lower()
                        if fid not in experimental_features:
                            await send(chat, f"Unknown feature: {fid}")
                            continue
                        del experimental_features[fid]
                        save_experimental()
                        await send(chat, f"Removed feature: {fid}")
                    else:
                        await send(chat, get_experimental_list())

                elif cmd == "/announcementoff":
                    state = load_version_state()
                    opted = state.get("opted_out_announcements", [])
                    if chat not in opted:
                        opted.append(chat)
                    state["opted_out_announcements"] = opted
                    save_version_state(state)
                    await send(chat, "🔕 Update announcements turned OFF for this chat.\nUse /announcementon to re-enable.")

                elif cmd == "/announcementon":
                    state = load_version_state()
                    opted = state.get("opted_out_announcements", [])
                    if chat in opted:
                        opted.remove(chat)
                    state["opted_out_announcements"] = opted
                    save_version_state(state)
                    await send(chat, "🔔 Update announcements turned ON for this chat.")

                elif cmd == "/rich":
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "on":
                        if not rich_mod:
                            await send(chat, "Rich Messages module not available.")
                            continue
                        fid = "rich-messages"
                        if fid not in experimental_features:
                            experimental_features[fid] = {"enabled": True, "name": "Rich Messages", "desc": "Send AI responses using Telegram's Rich Message format", "version": "3.1.0", "category": "ai"}
                        experimental_features[fid]["enabled"] = True
                        save_experimental()
                        await send(chat, "✅ Rich Messages ON. AI output will use structured blocks (tables, code, headings).")
                    elif sub == "off":
                        fid = "rich-messages"
                        if fid in experimental_features:
                            experimental_features[fid]["enabled"] = False
                            save_experimental()
                        await send(chat, "Rich Messages OFF.")
                    elif sub == "status" or sub == "":
                        on = is_experimental_enabled("rich-messages") if rich_mod else False
                        await send(chat, f"Rich Messages: {'ON' if on else 'OFF'}\nConverts AI markdown into Telegram's native rich blocks (tables, code, headings, collapsible details).\nUse /rich on or /rich off to toggle.")

                elif cmd == "/richv2":
                    if not rt2_mod:
                        await send(chat, "Rich Text v2 module not available.")
                        continue
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "on":
                        fid = "rich-text-v2"
                        if fid not in experimental_features:
                            experimental_features[fid] = {"enabled": True, "name": "Rich Text v2", "desc": "Bot API 10.1 Rich Messages — tables, collapsible details, math, code, slideshows", "version": "3.4.0", "category": "ai"}
                        experimental_features[fid]["enabled"] = True
                        save_experimental()
                        await send(chat, "✅ Rich Text v2 ON. AI output will use Bot API 10.1 rich formatting.")
                    elif sub == "off":
                        fid = "rich-text-v2"
                        if fid in experimental_features:
                            experimental_features[fid]["enabled"] = False
                            save_experimental()
                        await send(chat, "Rich Text v2 OFF.")
                    elif sub == "stats":
                        stats = rt2_mod.get_rich_v2().get_stats()
                        await send(chat, f"📊 Rich Text v2 Stats:\n  Enabled: {stats.get('enabled', False)}\n  Messages richified: {stats.get('messages_richified', 0)}\n  Blocks used: {stats.get('blocks_used', 0)}")
                    else:
                        on = is_experimental_enabled("rich-text-v2") if rt2_mod else False
                        await send(chat, f"Rich Text v2: {'ON' if on else 'OFF'}\nBot API 10.1 Rich Messages — tables, collapsible details, math formulas, code blocks, slideshows.\n\nCommands:\n  /richv2 on — Enable\n  /richv2 off — Disable\n  /richv2 stats — View statistics")

                elif cmd == "/cyberdeck":
                    try:
                        from cyberdeck_agent import get_cyberdeck_agent
                        agent = get_cyberdeck_agent()
                        sub = parts[1].lower() if len(parts) > 1 else "help"

                        if sub == "build":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if not prompt_text:
                                await send(chat, "Usage: /cyberdeck build <description>\nExample: /cyberdeck build I want a budget writerdeck under $100")
                                continue
                            await send(chat, "🔧 Building your cyberdeck with full compatibility check...")
                            build = await agent.build(prompt_text)
                            lines = [f"🔧 **{build.get('category', 'Custom Cyberdeck')}**\n"]
                            lines.append(f"📂 Category: `{build.get('category_id', 'coding')}`")
                            lines.append(f"⭐ Tier: **{build.get('tier_id', 'intermediate').upper()}**")
                            lines.append("")
                            comps = build.get("components", {})
                            if comps:
                                lines.append("**Components (Most Powerful Per Category):**")
                                for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "pcb", "wire_signal", "wire_power", "os"]:
                                    comp = comps.get(key, {})
                                    if comp:
                                        name = comp.get("name", key)
                                        price = comp.get("price", comp.get("price_range", comp.get("price_per_meter", "?")))
                                        lines.append(f"  {key.replace('_', ' ').title()}: **{name}** (${price})")
                                lines.append("")
                            compat = build.get("compatibility", {})
                            if compat.get("compatible"):
                                lines.append("✅ **All components compatible**")
                            elif compat.get("issues"):
                                lines.append("⚠️ **Compatibility issues (auto-fixed):**")
                                for issue in compat["issues"]:
                                    lines.append(f"  • {issue}")
                            lines.append(f"\n💵 **Estimated Total:** {build.get('total_price_estimate', '?')}")
                            lines.append(f"🎨 **Aesthetic:** {build.get('aesthetic', 'Industrial')}")
                            lines.append(f"🔧 **Soldering:** {build.get('soldering_required', 'Optional')}")
                            bom_text = build.get("bom", "")
                            if bom_text:
                                lines.append(f"\n🧾 **Bill of Materials:**\n{bom_text[:1500]}")
                            await send(chat, "\n".join(lines))

                        elif sub == "custom":
                            if len(parts) < 4:
                                await send(chat, "Usage: /cyberdeck custom <category_name> <description>\nExample: /cyberdeck custom \"Robotics Lab\" Mobile robotics with camera and servos\nYou name it, AI fills everything with best components.")
                                continue
                            cat_name = parts[2].strip('"').strip("'")
                            desc = " ".join(parts[3:])
                            await send(chat, f"🔧 Building custom category: **{cat_name}**...")
                            build = await agent.build_custom(cat_name, desc)
                            lines = [f"🔧 **Custom: {cat_name}**\n"]
                            lines.append(f"📂 Detected as: `{build.get('category_id', 'custom')}`")
                            lines.append(f"⭐ Tier: **{build.get('tier_id', 'intermediate').upper()}**")
                            lines.append("")
                            comps = build.get("components", {})
                            if comps:
                                lines.append("**Components (AI-Selected Most Powerful):**")
                                for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "pcb"]:
                                    comp = comps.get(key, {})
                                    if comp:
                                        lines.append(f"  {key.replace('_', ' ').title()}: **{comp.get('name', key)}** (${comp.get('price', '?')})")
                                lines.append("")
                            compat = build.get("compatibility", {})
                            if compat.get("compatible"):
                                lines.append("✅ **All components compatible**")
                            await send(chat, "\n".join(lines))

                        elif sub == "categories":
                            cats = agent.get_categories()
                            lines = ["📂 **Cyberdeck Categories:**\n"]
                            for cat_id, cat_info in cats.items():
                                lines.append(f"**{cat_info['name']}** (`{cat_id}`)")
                                lines.append(f"  {cat_info['description']}")
                                lines.append(f"  Budget: {cat_info['budget_range']}")
                                lines.append("")
                            await send(chat, "\n".join(lines))

                        elif sub == "tiers":
                            from cyberdeck_agent import TIERS
                            lines = ["📊 **Budget Tiers:**\n"]
                            for tier_id, tier_info in TIERS.items():
                                lines.append(f"**{tier_info['name']}** (`{tier_id}`)")
                                lines.append(f"  Budget: {tier_info['budget']}")
                                lines.append(f"  Soldering: {tier_info['soldering']}")
                                lines.append(f"  Skills: {tier_info['skills']}")
                                lines.append(f"  Build time: {tier_info['build_time']}")
                                lines.append(f"  Risk: {tier_info['risk']}")
                                lines.append("")
                            await send(chat, "\n".join(lines))

                        elif sub == "pick":
                            if len(parts) < 3:
                                await send(chat, "Usage: /cyberdeck pick <component_type> [category]\nTypes: sbc, display, keyboard, power, enclosure, cooling, pcb, wire_signal, wire_power, os\nExample: /cyberdeck pick sbc security")
                                continue
                            comp_type = parts[2]
                            category = parts[3] if len(parts) > 3 else "coding"
                            result = await agent.pick(comp_type, category)
                            if "error" in result:
                                await send(chat, f"❌ {result['error']}")
                                continue
                            item = result.get("item", {})
                            lines = [f"🔧 **{comp_type.upper()} Pick** ({category}):\n"]
                            lines.append(f"**{item.get('name', 'N/A')}**")
                            lines.append(f"  Price: ${item.get('price', item.get('price_range', item.get('price_per_meter', '?')))}")
                            if item.get("pros"):
                                lines.append(f"  Pros: {', '.join(item['pros'][:4])}")
                            if item.get("cons"):
                                lines.append(f"  Cons: {', '.join(item['cons'][:3])}")
                            if item.get("best_for"):
                                lines.append(f"  Best for: {', '.join(item['best_for'][:4])}")
                            await send(chat, "\n".join(lines))

                        elif sub == "compat":
                            if len(parts) < 3:
                                await send(chat, "Usage: /cyberdeck compat <sbc_id> [display_id] [power_id] [enclosure_id]\nExample: /cyberdeck compat pi5_16gb hdmi_7inch_ips ups_h5180 pelican_1450")
                                continue
                            sbc_id = parts[2]
                            display_id = parts[3] if len(parts) > 3 else None
                            power_id = parts[4] if len(parts) > 4 else None
                            enclosure_id = parts[5] if len(parts) > 5 else None
                            result = await agent.check_compatibility(sbc_id, display_id, power_id, enclosure_id)
                            lines = ["🔍 **Compatibility Check:**\n"]
                            if result.get("compatible"):
                                lines.append("✅ All components are compatible!")
                            else:
                                lines.append("⚠️ Issues found:")
                                for issue in result.get("issues", []):
                                    lines.append(f"  • {issue}")
                            await send(chat, "\n".join(lines))

                        elif sub == "bom":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            bom_text = build.get("bom", "")
                            if bom_text:
                                lines = ["🧾 **Bill of Materials:**\n", bom_text]
                            else:
                                lines = ["🧾 **Bill of Materials:**\n", "No BOM generated."]
                            await send(chat, "\n".join(lines))

                        elif sub == "tutorial":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            tutorial = build.get("tutorial", "")
                            if tutorial:
                                lines = ["📖 **Assembly Tutorial:**\n", tutorial[:2000]]
                            else:
                                lines = ["No tutorial generated."]
                            await send(chat, "\n".join(lines))

                        elif sub == "upgrade":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            upgrades = await agent.upgrade(build)
                            lines = ["⬆️ **Upgrade Suggestions:**\n"]
                            for up in upgrades:
                                lines.append(f"• **{up.get('component', 'N/A')}**: {up.get('from', '')} → **{up.get('to', '')}**")
                                lines.append(f"  {up.get('reason', '')}")
                            await send(chat, "\n".join(lines))

                        elif sub == "search":
                            query = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if not query:
                                await send(chat, "Usage: /cyberdeck search <query>\nExample: /cyberdeck search raspberry pi 5 8gb buy")
                                continue
                            await send(chat, f"🔍 Searching for: {query}")
                            results = await agent.search_parts(query)
                            lines = [f"🔍 **Search Results:** {query}\n"]
                            for s in results.get("suggestions", [])[:8]:
                                price = s.get("price", s.get("price_range", s.get("price_per_meter", "?")))
                                lines.append(f"• **{s.get('name', 'N/A')}** ({s.get('type', '')}) — ${price}")
                            if not results.get("suggestions"):
                                lines.append("No matching components found.")
                            lines.append(f"\nSources: {', '.join(results.get('sources', []))}")
                            await send(chat, "\n".join(lines))

                        elif sub == "watch":
                            url = parts[2] if len(parts) > 2 else ""
                            if not url:
                                await send(chat, "Usage: /cyberdeck watch <youtube_url>\nAutomatically learns from cyberdeck build videos.")
                                continue
                            await send(chat, "🎬 Watching and learning from video...")
                            result = await agent.watch_video(url)
                            lines = ["🎬 **Video Learnings:**\n"]
                            lines.append(f"Title: {result.get('title', 'Unknown')}")
                            lines.append(f"Key points: {result.get('key_points_count', 0)}")
                            comps = result.get("components_found", [])
                            if comps:
                                lines.append(f"Components found: {', '.join(str(c) for c in comps[:5])}")
                            tips = result.get("tips_found", [])
                            if tips:
                                lines.append("\nTips:")
                                for tip in tips[:3]:
                                    lines.append(f"  • {tip}")
                            await send(chat, "\n".join(lines))

                        elif sub == "code":
                            task = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if not task:
                                await send(chat, "Usage: /cyberdeck code <task>\nExample: /cyberdeck code battery monitor for raspberry pi")
                                continue
                            code_result = await agent.generate_code(task)
                            lines = ["💻 **Generated Code:**\n"]
                            lines.append(f"```{code_result.get('language', 'python')}")
                            lines.append(code_result.get("code", ""))
                            lines.append("```")
                            lines.append(f"\n{code_result.get('description', '')}")
                            await send(chat, "\n".join(lines))

                        elif sub == "ideas":
                            category = parts[2] if len(parts) > 2 else None
                            ideas = await agent.generate_ideas(category)
                            lines = ["💡 **Cyberdeck Ideas:**\n"]
                            for idea in ideas:
                                lines.append(f"• **{idea.get('title', 'Idea')}** ({idea.get('category', '')} — {idea.get('difficulty', '')})")
                                lines.append(f"  {idea.get('description', '')}")
                            await send(chat, "\n".join(lines))

                        elif sub == "list":
                            history = agent.build_history
                            if history:
                                lines = ["📋 **Build History:**\n"]
                                for i, entry in enumerate(history[-5:], 1):
                                    lines.append(f"{i}. {entry.get('category', 'custom')} ({entry.get('tier', '?')}) — SBC: {entry.get('sbc', '?')} — {entry.get('timestamp', 'unknown')}")
                                await send(chat, "\n".join(lines))
                            else:
                                await send(chat, "No build history yet. Use /cyberdeck build to create your first build!")

                        elif sub == "queue":
                            url = parts[2] if len(parts) > 2 else ""
                            if not url:
                                await send(chat, "Usage: /cyberdeck queue <youtube_url>\nQueues video for background learning (processes while you're offline/online).")
                                continue
                            result = await agent.queue_video(url)
                            await send(chat, f"🎬 **Video queued!**\nURL: {result['url']}\nPosition: #{result['position']}\n\nIt will be learned automatically. Use /cyberdeck process-queue to process now.")

                        elif sub == "process-queue":
                            await send(chat, "🎬 Processing video queue...")
                            result = await agent.process_queue()
                            lines = [f"🎬 **Queue Processed:** {result['processed']} videos\n"]
                            for r in result.get("results", []):
                                if isinstance(r, dict):
                                    lines.append(f"• **{r.get('title', 'Unknown')}** — {r.get('key_points_count', 0)} key points, {len(r.get('components_found', []))} components")
                            await send(chat, "\n".join(lines) if len(lines) > 1 else "No pending videos in queue.")

                        elif sub == "cooling":
                            from cyberdeck_agent import COOLING_DATABASE
                            lines = ["❄️ **Cooling Systems:**\n"]
                            for cid, cooler in COOLING_DATABASE.items():
                                lines.append(f"  • **{cooler['name']}** — ${cooler['price']} ({cooler.get('type', '?')})")
                                lines.append(f"    Best for: {', '.join(cooler.get('best_for', [])[:3])}")
                            lines.append("\n💡 Pi 5 needs active cooling. Copper > Aluminum (401 vs 205 W/mK).")
                            await send(chat, "\n".join(lines))

                        elif sub == "analyze":
                            await send(chat, "📸 **Send me a photo** of a cyberdeck or electronics project and I'll analyze it!\n\nI can identify components, suggest upgrades, check compatibility, and recommend the best category.\n\nTip: Reply to a photo with `/cyberdeck analyze`")

                        elif sub == "pcb":
                            from cyberdeck_agent import PCB_DATABASE
                            lines = ["🔌 **PCB / Carrier Board Database:**\n"]
                            for pid, pcb in PCB_DATABASE.items():
                                lines.append(f"• **{pcb['name']}** — {pcb['type']}")
                                lines.append(f"  Price: {pcb['price_range']}")
                                lines.append(f"  Best for: {', '.join(pcb.get('best_for', [])[:3])}")
                            await send(chat, "\n".join(lines))

                        elif sub == "wires":
                            from cyberdeck_agent import WIRE_DATABASE
                            lines = ["🔌 **Wire / Cable Database:**\n"]
                            for wid, wire in WIRE_DATABASE.items():
                                lines.append(f"• **{wire['name']}** — {wire['gauge']} / {wire['type']}")
                                lines.append(f"  Current: {wire['current_capacity']} | Use: {wire['use']}")
                                lines.append(f"  ${wire['price_per_meter']}/m")
                            await send(chat, "\n".join(lines))

                        elif sub == "connectivity":
                            from cyberdeck_agent import CONNECTIVITY_DATABASE
                            lines = ["📡 **WiFi / LAN / LoRa / Cellular Database:**\n"]
                            for cid, comp in CONNECTIVITY_DATABASE.items():
                                lines.append(f"• **{comp['name']}** ({comp['type']})")
                                lines.append(f"  {comp.get('standard', '')} | Price: ${comp.get('price', '?')}")
                                if comp.get('pros'):
                                    lines.append(f"  Pros: {', '.join(comp['pros'][:3])}")
                                if comp.get('best_for'):
                                    lines.append(f"  Best for: {', '.join(comp['best_for'])}")
                                lines.append("")
                            await send(chat, "\n".join(lines))

                        elif sub == "status":
                            status = agent.get_status()
                            lines = ["🔧 **Cyberdeck Agent v4.1 Status:**\n"]
                            lines.append(f"Version: {status.get('version', '?')}")
                            lines.append(f"Total Builds: {status.get('total_builds', 0)}")
                            lines.append(f"Videos Learned: {status.get('videos_learned', 0)}")
                            lines.append(f"Tips Learned: {status.get('tips_count', 0)}")
                            lines.append(f"Flaws Fixed: {status.get('flaws_fixed', 0)}")
                            lines.append(f"Categories: {len(status.get('categories', []))}")
                            lines.append(f"Tiers: {len(status.get('tiers', []))}")
                            lines.append(f"SBCs: {status.get('sbc_count', 0)} | Displays: {status.get('display_count', 0)}")
                            lines.append(f"Keyboards: {status.get('keyboard_count', 0)} | Power: {status.get('power_count', 0)}")
                            lines.append(f"Enclosures: {status.get('enclosure_count', 0)} | Cooling: {status.get('cooling_count', 0)}")
                            lines.append(f"PCBs: {status.get('pcb_count', 0)} | Wires: {status.get('wire_count', 0)}")
                            lines.append(f"Connectivity: {status.get('connectivity_count', 0)} | OS Options: {status.get('os_count', 0)}")
                            lines.append(f"Video Queue: {status.get('video_queue_pending', 0)} pending")
                            lines.append(f"Learnings: {len(agent.learnings) if hasattr(agent, 'learnings') else 0}")
                            await send(chat, "\n".join(lines))

                        elif sub == "cables":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            routing = build.get("cable_plan", {})
                            lines = ["🔌 **Cable Routing Plan:**\n"]
                            if routing:
                                routes = routing.get("routes", [])
                                for route in routes:
                                    if isinstance(route, dict):
                                        lines.append(f"  • **{route.get('from', '?')}** → **{route.get('to', '?')}**")
                                        lines.append(f"    Cable: {route.get('cable', '?')} | Length: {route.get('length', '?')}")
                                    else:
                                        lines.append(f"  • {route}")
                                accessories = routing.get("accessories", [])
                                if accessories:
                                    lines.append(f"\n**Accessories:** {', '.join(accessories) if isinstance(accessories, list) else accessories}")
                            else:
                                lines.append("No cable routing generated.")
                            await send(chat, "\n".join(lines))

                        elif sub == "pack":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            pack = await agent.generate_pack(build)
                            lines = ["📦 **Build Pack Generated:**\n"]
                            lines.append(f"Cables: {pack.get('cable_plan', {}).get('total_cables', 0)}")
                            lines.append(f"Upgrades: {len(pack.get('upgrades', []))}")
                            lines.append(f"Ideas: {len(pack.get('ideas', []))}")
                            lines.append(f"\nMarkdown pack saved ({len(pack.get('markdown', ''))} chars)")
                            md = pack.get("markdown", "")
                            if md:
                                lines.append(f"\n{md[:1500]}")
                            await send(chat, "\n".join(lines))

                        elif sub == "flaws":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            flaws = await agent.detect_flaws(build)
                            lines = ["🔍 **Flaw Detection Report:**\n"]
                            if flaws:
                                for flaw in flaws:
                                    severity = flaw.get('severity', 'low')
                                    emoji = '🔴' if severity == 'high' else '🟡' if severity == 'medium' else '🟢'
                                    lines.append(f"{emoji} **{flaw.get('component', 'N/A')}**: {flaw.get('issue', 'Unknown')}")
                                    if flaw.get('fix'):
                                        lines.append(f"  Fix: {flaw['fix']}")
                            else:
                                lines.append("✅ No flaws detected! Build is solid.")
                            await send(chat, "\n".join(lines))

                        elif sub == "learn":
                            learnings = agent.learner.learnings if hasattr(agent, 'learner') else {}
                            lines = ["🧠 **Agent Learnings:**\n"]
                            lines.append(f"Total learnings: {len(learnings)}")
                            for key, value in list(learnings.items())[:10]:
                                if isinstance(value, dict):
                                    lines.append(f"  • {key}: {list(value.keys())[:3]}")
                                elif isinstance(value, list):
                                    lines.append(f"  • {key}: {len(value)} items")
                                else:
                                    lines.append(f"  • {key}: {str(value)[:100]}")
                            if not learnings:
                                lines.append("No learnings yet. Watch videos or chat to start learning!")
                            await send(chat, "\n".join(lines))

                        elif sub == "search-web":
                            query = " ".join(parts[2:]) if len(parts) > 2 else ""
                            if not query:
                                await send(chat, "Usage: /cyberdeck search-web <query>\nExample: /cyberdeck search-web raspberry pi cyberdeck build 2026")
                                continue
                            await send(chat, f"🌐 Searching web for: {query}")
                            results = await agent.search_web(query)
                            lines = [f"🌐 **Web Search Results:** {query}\n"]
                            platforms = results.get("platforms", {})
                            for platform, info in platforms.items():
                                lines.append(f"**{platform.title()}:**")
                                lines.append(f"  🔗 {info.get('url', '')}")
                                lines.append(f"  {info.get('note', '')}")
                                lines.append("")
                            if not platforms:
                                lines.append("No results found.")
                            await send(chat, "\n".join(lines))

                        elif sub == "optimize":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            optimized = await agent.optimize_build(build)
                            lines = ["⚡ **Optimized Build:**\n"]
                            opt_info = optimized.get("optimizer", {})
                            lines.append(f"Flaws found: {opt_info.get('flaws_found', 0)}")
                            lines.append(f"Flaws fixed: {opt_info.get('flaws_fixed', 0)}")
                            lines.append(f"Status: {opt_info.get('status', 'unknown')}")
                            comps = optimized.get("components", {})
                            if comps:
                                lines.append("\n**Components:**")
                                for key, comp in comps.items():
                                    if comp and isinstance(comp, dict):
                                        lines.append(f"  {key.replace('_', ' ').title()}: **{comp.get('name', key)}**")
                            await send(chat, "\n".join(lines))

                        elif sub == "stats":
                            status = agent.get_status()
                            lines = ["📊 **Component Database Stats:**\n"]
                            lines.append(f"  SBCs: {status.get('sbc_count', 0)}")
                            lines.append(f"  Displays: {status.get('display_count', 0)}")
                            lines.append(f"  Keyboards: {status.get('keyboard_count', 0)}")
                            lines.append(f"  Power: {status.get('power_count', 0)}")
                            lines.append(f"  Enclosures: {status.get('enclosure_count', 0)}")
                            lines.append(f"  Cooling: {status.get('cooling_count', 0)}")
                            lines.append(f"  PCBs: {status.get('pcb_count', 0)}")
                            lines.append(f"  Wires: {status.get('wire_count', 0)}")
                            lines.append(f"  Connectivity: {status.get('connectivity_count', 0)}")
                            lines.append(f"  OS Options: {status.get('os_count', 0)}")
                            lines.append(f"  Styles: {status.get('styles_count', 0)}")
                            lines.append(f"  Custom PCBs: {status.get('custom_pcb_count', 0)}")
                            await send(chat, "\n".join(lines))

                        elif sub == "3d":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            color = parts[3] if len(parts) > 3 else "black"
                            style = parts[4] if len(parts) > 4 else "futuristic"
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            model = agent.generate_3d_model(build, color, style)
                            lines = ["🎨 **3D Model Generated:**\n"]
                            lines.append(f"Style: {model.get('style', style)}")
                            lines.append(f"Color: {model.get('color', color)}")
                            lines.append(f"Dimensions: {model.get('dimensions', 'N/A')}")
                            lines.append(f"\n**OpenSCAD Code:**\n```{model.get('openscad_code', 'N/A')[:1000]}```")
                            lines.append(f"\n💡 Copy the code to OpenSCAD and render to get STL file.")
                            await send(chat, "\n".join(lines))

                        elif sub == "specs":
                            comp_id = parts[2] if len(parts) > 2 else ""
                            if not comp_id:
                                await send(chat, "Usage: /cyberdeck specs <component_id>\nExample: /cyberdeck specs pi5_16gb")
                                continue
                            details = agent.get_component_details(comp_id)
                            if not details:
                                await send(chat, f"❌ Component `{comp_id}` not found.")
                                continue
                            lines = [f"📋 **{details.get('name', comp_id)}**\n"]
                            for key, val in details.items():
                                if key != "name":
                                    lines.append(f"  {key.replace('_', ' ').title()}: {val}")
                            await send(chat, "\n".join(lines))

                        elif sub == "video":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            video = agent.generate_build_video(build)
                            lines = ["🎬 **Build Video Script:**\n"]
                            lines.append(f"Title: {video.get('title', 'Cyberdeck Build')}")
                            lines.append(f"Scenes: {len(video.get('scenes', []))}")
                            lines.append(f"Duration: {video.get('estimated_duration', 'N/A')}")
                            for scene in video.get("scenes", [])[:5]:
                                lines.append(f"\n**Scene {scene.get('scene', '?')}: {scene.get('name', '')}**")
                                lines.append(f"  Camera: {scene.get('camera', '')}")
                                lines.append(f"  Narration: {scene.get('narration', '')[:100]}")
                            await send(chat, "\n".join(lines))

                        elif sub == "pcb-custom":
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else ""
                            build = await agent.build(prompt_text or "budget cyberdeck")
                            issues = build.get("compatibility", {}).get("issues", [])
                            pcb = agent.suggest_custom_pcb(issues)
                            lines = ["🔌 **Custom PCB Suggestion:**\n"]
                            if pcb:
                                lines.append(f"Template: {pcb.get('name', 'N/A')}")
                                lines.append(f"Purpose: {pcb.get('purpose', '')}")
                                lines.append(f"Complexity: {pcb.get('complexity', '')}")
                                lines.append(f"Cost: {pcb.get('estimated_cost', '?')}")
                            else:
                                lines.append("✅ No custom PCB needed — all components compatible!")
                            await send(chat, "\n".join(lines))

                        elif sub == "styles":
                            from cyberdeck_agent import STYLE_PRESETS
                            lines = ["🎨 **3D Model Styles:**\n"]
                            for style_id, style_info in STYLE_PRESETS.items():
                                lines.append(f"**{style_info.get('name', style_id)}** (`{style_id}`)")
                                lines.append(f"  Colors: {', '.join(style_info.get('colors', [])[:5])}")
                                lines.append(f"  Screws: {style_info.get('screws', 'hidden')}")
                                lines.append(f"  Wiring: {style_info.get('wiring', 'hidden')}")
                                lines.append("")
                            await send(chat, "\n".join(lines))

                        elif sub == "risk":
                            lines = ["⚠️ **Component Risk Levels:**\n"]
                            from cyberdeck_agent import SBC_DATABASE, DISPLAY_DATABASE, POWER_DATABASE
                            for db_name, db in [("SBC", SBC_DATABASE), ("Display", DISPLAY_DATABASE), ("Power", POWER_DATABASE)]:
                                for cid, comp in db.items():
                                    risk = comp.get("risk_level", "unknown")
                                    emoji = "🟢" if risk == "minimal" else "🟡" if risk == "low" else "🟠" if risk == "medium" else "🔴" if risk == "high" else "⚪"
                                    lines.append(f"{emoji} **{comp.get('name', cid)}** ({db_name}): {risk}")
                            await send(chat, "\n".join(lines))

                        elif sub == "career":
                            from cyberdeck_agent import CAREER_TEMPLATES
                            career_type = parts[2].lower() if len(parts) > 2 else ""
                            if not career_type or career_type == "list":
                                lines = ["💼 **Career Templates (v6.0):**\n"]
                                for cid, ct in CAREER_TEMPLATES.items():
                                    lines.append(f"• **{ct['name']}** (`{cid}`)")
                                    lines.append(f"  {ct.get('description', '')[:80]}")
                                    lines.append(f"  Budget: {ct.get('budget', '?')} | Tier: {ct.get('tier', '?')}")
                                lines.append("\nUsage: /cyberdeck career <type> (e.g., coding, gaming, ai_ml, security, writer)")
                                await send(chat, "\n".join(lines))
                            elif career_type in CAREER_TEMPLATES:
                                ct = CAREER_TEMPLATES[career_type]
                                lines = [f"💼 **{ct['name']}:**\n"]
                                lines.append(f"Description: {ct.get('description', '')}")
                                lines.append(f"Budget: {ct.get('budget', '?')} | Tier: {ct.get('tier', '?')}")
                                lines.append(f"SBC: {ct.get('sbc', '?')} | Display: {ct.get('display', '?')}")
                                lines.append(f"Power: {ct.get('power', '?')} | Enclosure: {ct.get('enclosure', '?')}")
                                lines.append(f"Key Features: {', '.join(ct.get('features', [])[:5])}")
                                lines.append(f"\n💡 Use /cyberdeck build {ct.get('description', career_type)} to create this build!")
                                await send(chat, "\n".join(lines))
                            else:
                                await send(chat, f"Unknown career: {career_type}\nAvailable: {', '.join(CAREER_TEMPLATES.keys())}")

                        elif sub == "dashboard":
                            from cyberdeck_agent import InteractiveDashboard
                            dashboard = InteractiveDashboard()
                            prompt_text = " ".join(parts[2:]) if len(parts) > 2 else "budget coding cyberdeck"
                            build = await agent.build(prompt_text)
                            html = dashboard.generate_dashboard(build)
                            lines = ["🌐 **Interactive Dashboard Generated (v6.0):**\n"]
                            lines.append(f"HTML size: {len(html)} chars")
                            lines.append(f"Features: 3D visualization, component picker, color customization, cable guide, tutorials")
                            lines.append(f"\n💡 The dashboard is saved as cyberdeck_dashboard.html")
                            lines.append("Open it in a browser to interact with your build!")
                            await send(chat, "\n".join(lines))

                        elif sub == "custombuild" or sub == "cb":
                            from cyberdeck_agent import CustomBuildEngine
                            cb_action = parts[2].lower() if len(parts) > 2 else "menu"

                            if not hasattr(agent, '_custom_build_engine'):
                                agent._custom_build_engine = CustomBuildEngine()
                            engine = agent._custom_build_engine

                            if cb_action == "menu" or cb_action == "start":
                                engine.start_build(chat)
                                cats = engine.CATEGORIES
                                lines = ["🔧 **CYBERDECK CUSTOM BUILDER v5.2**\n"]
                                lines.append("Pick components for each category. See prices instantly.\n")
                                for key, cat in cats.items():
                                    req = " *" if cat["required"] else ""
                                    lines.append(f"{cat['icon']} `{key}` — {cat['name']}{req}")
                                lines.append(f"\n* = Required component")
                                lines.append("\n**Commands:**")
                                lines.append("  `/cyberdeck cb list <category>` — See all options with prices")
                                lines.append("  `/cyberdeck cb pick <category> <id>` — Select a component")
                                lines.append("  `/cyberdeck cb remove <category>` — Remove a component")
                                lines.append("  `/cyberdeck cb show` — Show current build + total cost")
                                lines.append("  `/cyberdeck cb compat` — Check compatibility")
                                lines.append("  `/cyberdeck cb summary` — Full build summary")
                                lines.append("  `/cyberdeck cb clear` — Start over")
                                await send(chat, "\n".join(lines))

                            elif cb_action == "list":
                                cat_name = parts[3].lower() if len(parts) > 3 else ""
                                if not cat_name:
                                    await send(chat, "Usage: `/cyberdeck cb list <category>`\nCategories: " + ", ".join(engine.CATEGORIES.keys()))
                                    continue
                                options = engine.get_category_options(cat_name)
                                if not options:
                                    await send(chat, f"Unknown category: {cat_name}\nAvailable: {', '.join(engine.CATEGORIES.keys())}")
                                    continue
                                cat_info = engine.CATEGORIES.get(cat_name, {})
                                lines = [f"{cat_info.get('icon', '')} **{cat_info.get('name', cat_name)} Options:**\n"]
                                for opt in options:
                                    price_str = f"${opt['price']}" if isinstance(opt['price'], (int, float)) else str(opt['price'])
                                    lines.append(f"  `{opt['id']}` — **{opt['name']}**")
                                    lines.append(f"    💰 {price_str}")
                                    if opt.get('key_specs'):
                                        lines.append(f"    📋 {opt['key_specs']}")
                                await send(chat, "\n".join(lines))

                            elif cb_action == "pick":
                                cat_name = parts[3].lower() if len(parts) > 3 else ""
                                comp_id = parts[4].lower() if len(parts) > 4 else ""
                                if not cat_name or not comp_id:
                                    await send(chat, "Usage: `/cyberdeck cb pick <category> <component_id>`\nExample: `/cyberdeck cb pick sbc pi5_8gb`")
                                    continue
                                result = engine.select_component(chat, cat_name, comp_id)
                                if "error" in result:
                                    await send(chat, f"❌ {result['error']}")
                                else:
                                    await send(chat, f"✅ **{result['component']}** selected for {result['category']}\n💰 Price: {result['price']}\n📊 Running total: **{result['total_cost']}**")

                            elif cb_action == "remove":
                                cat_name = parts[3].lower() if len(parts) > 3 else ""
                                if not cat_name:
                                    await send(chat, "Usage: `/cyberdeck cb remove <category>`")
                                    continue
                                result = engine.remove_component(chat, cat_name)
                                if "error" in result:
                                    await send(chat, f"❌ {result['error']}")
                                else:
                                    await send(chat, f"🗑️ Removed {result['removed']}\n📊 Running total: **{result['total_cost']}**")

                            elif cb_action == "show" or cb_action == "status":
                                build = engine.get_build(chat)
                                if not build["components"]:
                                    await send(chat, "No components selected yet. Start with `/cyberdeck cb list sbc`")
                                    continue
                                lines = ["🔧 **YOUR CUSTOM BUILD:**\n"]
                                for comp in build["components"]:
                                    price_str = f"${comp['price']}" if isinstance(comp['price'], (int, float)) else str(comp['price'])
                                    lines.append(f"{comp['icon']} **{comp['category_name']}**: {comp['name']}")
                                    lines.append(f"  💰 {price_str} | 📋 {comp['specs']}")
                                lines.append(f"\n💰 **TOTAL: {build['total_cost']}**")
                                if build["required_missing"]:
                                    lines.append(f"\n⚠️ Missing required: {', '.join(build['required_missing'])}")
                                await send(chat, "\n".join(lines))

                            elif cb_action == "compat":
                                result = engine.check_compatibility(chat)
                                lines = ["🔍 **COMPATIBILITY CHECK:**\n"]
                                if result["compatible"]:
                                    lines.append("✅ All selected components are compatible!")
                                else:
                                    for w in result["warnings"]:
                                        lines.append(w)
                                if result["recommendations"]:
                                    lines.append("\n💡 **Recommendations:**")
                                    for r in result["recommendations"]:
                                        lines.append(r)
                                await send(chat, "\n".join(lines))

                            elif cb_action == "summary":
                                summary = engine.generate_build_summary(chat)
                                await send(chat, summary)

                            elif cb_action == "clear":
                                engine.clear_build(chat)
                                await send(chat, "🗑️ Build cleared. Start fresh with `/cyberdeck cb start`")

                            else:
                                await send(chat, "Unknown custombuild action. Use: start, list, pick, remove, show, compat, summary, clear")

                        else:
                            await send(chat, "🔧 **Cyberdeck Agent v6.0**\n\n"
                                "**Build & Design:**\n"
                                "  /cyberdeck build <desc> — Build (auto-detect category, most powerful parts)\n"
                                "  /cyberdeck custom <name> <desc> — Custom category (AI fills everything)\n"
                                "  /cyberdeck cb — **Custom Builder** (pick components, see prices, mix & match)\n"
                                "  /cyberdeck categories — View all categories\n"
                                "  /cyberdeck tiers — View budget tiers\n"
                                "  /cyberdeck pick <type> [category] — Pick best component\n"
                                "  /cyberdeck compat <sbc> [display] [power] [enclosure] — Check compatibility\n"
                                "  /cyberdeck bom <desc> — Bill of materials\n"
                                "  /cyberdeck tutorial <desc> — Word-by-word assembly guide\n"
                                "  /cyberdeck upgrade <desc> — Suggest upgrades\n"
                                "  /cyberdeck cables <desc> — Cable routing plan\n"
                                "  /cyberdeck pack <desc> — Generate build pack (image+video+text)\n"
                                "  /cyberdeck flaws <desc> — Run flaw detection\n"
                                "  /cyberdeck optimize <desc> — Optimize build for cost/performance\n"
                                "  /cyberdeck 3d <desc> [color] [style] — Generate 3D model (OpenSCAD)\n"
                                "  /cyberdeck video <desc> — Generate build video script\n"
                                "  /cyberdeck pcb-custom <desc> — Suggest custom PCB for compatibility\n"
                                "  /cyberdeck cooling — View cooling options\n"
                                "  /cyberdeck pcb — View PCB/carrier board database\n"
                                "  /cyberdeck wires — View wire/cable database\n"
                                "  /cyberdeck connectivity — View WiFi/LAN/LoRa/cellular database\n"
                                "  /cyberdeck stats — Component database statistics\n"
                                "  /cyberdeck styles — View 3D model styles\n"
                                "  /cyberdeck risk — View component risk levels\n\n"
                                "**v6.0 New Features:**\n"
                                "  /cyberdeck career <type> — Career-specific templates (coding, gaming, ai, security, writer, etc.)\n"
                                "  /cyberdeck dashboard — Generate interactive HTML dashboard with 3D visualization\n"
                                "  /cyberdeck search-web <query> — Search YouTube/TikTok/GitHub/Reddit/web\n"
                                "  /cyberdeck ideas [category] — Get cyberdeck ideas with trend analysis\n"
                                "  /cyberdeck learn — View agent learnings from chat/video/builds\n"
                                "  /cyberdeck analyze — Analyze a cyberdeck photo (AI vision)\n"
                                "  /cyberdeck specs <id> — Detailed component specs (OLED/IPS, size, resolution, etc.)\n\n"
                                "**Research & Learn:**\n"
                                "  /cyberdeck search <query> — Search for parts\n"
                                "  /cyberdeck watch <url> — Learn from YouTube/TikTok video\n"
                                "  /cyberdeck queue <url> — Queue video for offline learning\n"
                                "  /cyberdeck process-queue — Process queued videos\n"
                                "  /cyberdeck code <task> — Generate electronics code\n\n"
                                "**History & Info:**\n"
                                "  /cyberdeck list — View build history\n"
                                "  /cyberdeck status — Agent status (v6.0)\n\n"
                                "Types: sbc, display, keyboard, power, enclosure, cooling, pcb, wire_signal, wire_power, os\n"
                                "Styles: futuristic, retro, industrial, minimal, steampunk, cyberpunk, nautical, solarpunk, cassette-futurism, feminine-craft, fallout, brutalist\n"
                                "Sizes: small (compact), big (full power)\n"
                                "Careers: coding, gaming, ai_ml, security, writer, field_research, robotics, media_production, ham_radio, home_automation, portable_hacking\n"
                                "Categories: coding, writerdeck, security, gaming, research, ai, survival, media, conversation, retro, maker, ham-radio, field-repair, drone, forensics, test-equipment, weather, home-automation, edge-ai")

                    except Exception as e:
                        await send(chat, f"Cyberdeck error: {str(e)[:200]}")

                elif cmd == "/iot":
                    try:
                        from iot_control import handle_iot_command, get_iot_manager
                        sub = parts[1].lower() if len(parts) > 1 else ""
                        if sub == "add" and len(parts) >= 4:
                            name = parts[2]
                            dtype = parts[3]
                            ip = parts[4] if len(parts) > 4 else ""
                            mgr = get_iot_manager()
                            device = mgr.add_device(name, dtype, ip)
                            await send(chat, f"✅ Device added: {device.name}\nID: `{device.device_id}`\nType: {device.device_type.value}")
                        elif sub == "list":
                            mgr = get_iot_manager()
                            devices = mgr.list_devices()
                            if not devices:
                                await send(chat, "No devices. Use /iot add <name> <type> [ip]")
                            else:
                                lines = ["📡 **Devices:**\n"]
                                for d in devices:
                                    icon = "🟢" if d.status == "online" else "🔴"
                                    lines.append(f"{icon} `{d.device_id}` — {d.name} ({d.device_type.value})")
                                await send(chat, "\n".join(lines))
                        elif sub == "status":
                            device_id = parts[2] if len(parts) > 2 else None
                            mgr = get_iot_manager()
                            if device_id:
                                s = mgr.get_device_status(device_id)
                                if "error" in s:
                                    await send(chat, f"❌ {s['error']}")
                                else:
                                    icon = "🟢" if s["status"] == "online" else "🔴"
                                    await send(chat, f"{icon} **{s['name']}** (`{s['device_id']}`)\n\nType: {s['type']}\nStatus: {s['status']}\nPins: {len(s['pins'])}\nAlerts: {s['alerts']}\nSchedules: {s['schedules']}")
                            else:
                                statuses = mgr.get_all_status()
                                if not statuses:
                                    await send(chat, "No devices. Use /iot add")
                                else:
                                    lines = ["📊 **Device Status:**\n"]
                                    for st in statuses:
                                        icon = "🟢" if st["status"] == "online" else "🔴"
                                        lines.append(f"{icon} **{st['name']}** — {st['type']} | Pins: {len(st['pins'])}")
                                    await send(chat, "\n".join(lines))
                        elif sub == "pin" and len(parts) >= 4:
                            device_id = parts[2]
                            try:
                                pin = int(parts[3])
                                state = int(parts[4]) if len(parts) > 4 else 0
                            except ValueError:
                                await send(chat, "Pin and state must be numbers.")
                                continue
                            mgr = get_iot_manager()
                            ok = mgr.set_pin(device_id, pin, state)
                            await send(chat, f"✅ Pin {pin} → {'HIGH ⚡' if state else 'LOW ⚫'}" if ok else "❌ Device not found.")
                        elif sub == "sensor" and len(parts) >= 4:
                            device_id = parts[2]
                            stype = parts[3]
                            value = float(parts[4]) if len(parts) > 4 else None
                            mgr = get_iot_manager()
                            if value is not None:
                                unit = parts[5] if len(parts) > 5 else ""
                                mgr.add_sensor_reading(device_id, stype, value, unit)
                                await send(chat, f"✅ Reading: {stype} = {value}{unit}")
                            else:
                                v = mgr.simulate_reading(device_id, stype)
                                await send(chat, f"✅ Simulated {stype}: {v}")
                        elif sub == "simulate" and len(parts) >= 4:
                            mgr = get_iot_manager()
                            v = mgr.simulate_reading(parts[2], parts[3])
                            await send(chat, f"✅ Simulated {parts[3]}: {v}")
                        elif sub == "logs":
                            device_id = parts[2] if len(parts) > 2 else None
                            mgr = get_iot_manager()
                            logs = mgr.get_logs(device_id)
                            if not logs:
                                await send(chat, "No logs.")
                            else:
                                lines = ["📋 **Recent Activity:**\n"]
                                for entry in logs[-10:]:
                                    ts = datetime.fromtimestamp(entry["time"]).strftime("%H:%M:%S")
                                    lines.append(f"`{ts}` {entry['action']}: {entry['details']}")
                                await send(chat, "\n".join(lines))
                        elif sub == "help":
                            from iot_control import build_iot_commands
                            await send(chat, build_iot_commands())
                        else:
                            from iot_control import build_iot_commands
                            await send(chat, build_iot_commands())
                    except Exception as e:
                        await send(chat, f"IoT error: {str(e)[:200]}")

                elif cmd == "/edu":
                    try:
                        from education_games import handle_education_command, get_education_manager
                        sub = parts[1].lower() if len(parts) > 1 else ""
                        user_id = str(uid)
                        mgr = get_education_manager()

                        if sub == "quiz":
                            if len(parts) > 2 and parts[2] == "answer":
                                if len(parts) < 4:
                                    await send(chat, "Usage: /edu quiz answer <0-3>")
                                    continue
                                try:
                                    ans = int(parts[3])
                                except ValueError:
                                    await send(chat, "Answer must be 0-3.")
                                    continue
                                correct, feedback, done = mgr.answer_quiz(user_id, ans)
                                await send(chat, feedback)
                            else:
                                quiz, first_q = mgr.start_quiz(user_id)
                                lines = [f"📝 **{quiz.title}**\n"]
                                q = quiz.questions[0]
                                lines.append(f"Q1: {q.question}")
                                for i, opt in enumerate(q.options):
                                    lines.append(f"  {i}. {opt}")
                                lines.append(f"\nAnswer: /edu quiz answer <0-3>")
                                await send(chat, "\n".join(lines))
                        elif sub == "wordle":
                            game = mgr.start_wordle(user_id)
                            await send(chat, f"🔤 **Wordle** ({len(game.word)} letters)\n\nGuess: /edu guess <word>\n🟩=correct 🟨=wrong position ⬜=not in word")
                        elif sub == "guess":
                            if len(parts) < 3:
                                await send(chat, "Usage: /edu guess <word>")
                                continue
                            result, feedback, done = mgr.guess_wordle(user_id, parts[2])
                            await send(chat, feedback)
                        elif sub == "hangman":
                            category = parts[2] if len(parts) > 2 else None
                            game = mgr.start_hangman(user_id, category)
                            display = " ".join("_" for _ in game.word)
                            await send(chat, f"🎭 **Hangman** — {game.category}\n\nWord: `{display}` ({len(game.word)} letters)\nGuess: /edu hguess <letter>")
                        elif sub == "hguess":
                            if len(parts) < 3:
                                await send(chat, "Usage: /edu hguess <letter>")
                                continue
                            display, feedback, done = mgr.guess_hangman(user_id, parts[2])
                            await send(chat, feedback)
                        elif sub == "math":
                            difficulty = parts[2] if len(parts) > 2 else "medium"
                            problem = mgr.generate_math(difficulty)
                            await send(chat, f"🔢 **Math** ({difficulty})\n\n**{problem.expression}** = ?\n\nAnswer: /edu mathanswer <number>")
                        elif sub == "mathanswer":
                            if len(parts) < 3:
                                await send(chat, "Usage: /edu mathanswer <number>")
                                continue
                            try:
                                ans = float(parts[2])
                            except ValueError:
                                await send(chat, "Enter a number.")
                                continue
                            profile = mgr.get_profile(user_id)
                            profile.math_solved += 1
                            profile.add_xp(5, "math_attempt")
                            mgr._save_data()
                            await send(chat, f"✅ Submitted! Your answer: {ans}")
                        elif sub == "code":
                            difficulty = parts[2] if len(parts) > 2 else None
                            challenge = mgr.get_code_challenge(difficulty)
                            hints = "\n".join(f"💡 {h}" for h in challenge.hints[:2])
                            await send(chat, f"💻 **{challenge.title}** ({challenge.difficulty.value})\n\n{challenge.description}\n\nHints:\n{hints}")
                        elif sub == "addcards":
                            text = " ".join(parts[2:])
                            entries = [line.split("|") for line in text.split("\n") if "|" in line]
                            cards = [(e[0].strip(), e[1].strip(), e[2].strip() if len(e) > 2 else "general") for e in entries if len(e) >= 2]
                            count = mgr.add_flashcards(user_id, cards)
                            await send(chat, f"✅ Added {count} flashcards!")
                        elif sub == "review":
                            cards = mgr.get_review_cards(user_id)
                            if not cards:
                                await send(chat, "No cards due! 🎉")
                            else:
                                card = cards[0]
                                await send(chat, f"🃏 **Flashcard** ({card.category})\n\n**Q:** {card.front}\n\nRate: /edu review good or /edu review bad")
                        elif sub == "top":
                            board = mgr.get_leaderboard()
                            medals = ["🥇", "🥈", "🥉"]
                            lines = ["🏆 **Leaderboard:**\n"]
                            for i, p in enumerate(board):
                                medal = medals[i] if i < 3 else f"{i+1}."
                                lines.append(f"{medal} **{p.username or p.user_id}** — Lv.{p.level} | {p.xp} XP")
                            await send(chat, "\n".join(lines))
                        elif sub == "stats":
                            stats = mgr.get_stats(user_id)
                            await send(chat, f"📊 **Stats:**\n\nLevel: {stats['level']} ({stats['xp']} XP)\n📝 Quizzes: {stats['quizzes_correct']}/{stats['quizzes_taken']}\n🔤 Wordle: {stats['wordle_wins']} wins\n🔢 Math: {stats['math_solved']} solved\n💻 Code: {stats['code_solved']} solved\n🏅 Achievements: {len(stats['achievements'])}")
                        elif sub == "achievements":
                            handle_result = await asyncio.get_event_loop().run_in_executor(None, lambda: handle_education_command(update, context))
                            await send(chat, handle_result)
                        else:
                            from education_games import build_education_commands
                            await send(chat, build_education_commands())
                    except Exception as e:
                        await send(chat, f"Education error: {str(e)[:200]}")

                elif cmd == "/fin":
                    try:
                        from finance_crypto import handle_finance_command, get_finance_manager
                        sub = parts[1].lower() if len(parts) > 1 else ""
                        user_id = str(uid)
                        mgr = get_finance_manager()

                        if sub == "price" and len(parts) >= 3:
                            symbol = parts[2].upper()
                            price = mgr.get_price(symbol)
                            if price is None:
                                await send(chat, f"❌ Unknown: {symbol}")
                            else:
                                from finance_crypto import POPULAR_CRYPTOS
                                name = POPULAR_CRYPTOS.get(symbol, {}).get("name", symbol)
                                rank = list(mgr.get_prices(POPULAR_CRYPTOS.keys()).keys()).index(symbol) + 1 if symbol in mgr.get_prices(POPULAR_CRYPTOS.keys()) else "?"
                                await send(chat, f"💰 **{name}** ({symbol})\n\nPrice: **${price:,.2f}**\nRank: #{rank}")
                        elif sub == "market":
                            overview = mgr.get_market_overview()
                            lines = ["📊 **Top 10 Cryptos:**\n"]
                            for item in overview["top_cryptos"]:
                                lines.append(f"**{item['symbol']}** ({item['name']}) — ${item['price']:,.2f}")
                            await send(chat, "\n".join(lines))
                        elif sub == "convert" and len(parts) >= 5:
                            try:
                                amount = float(parts[2])
                            except ValueError:
                                await send(chat, "Amount must be a number.")
                                continue
                            result = mgr.convert_currency(amount, parts[3].upper(), parts[4].upper())
                            await send(chat, f"💱 {amount:,.2f} {parts[3].upper()} = **{result:,.2f} {parts[4].upper()}**" if result else "❌ Unknown currency.")
                        elif sub == "buy" and len(parts) >= 5:
                            try:
                                qty = float(parts[3])
                                price = float(parts[4])
                            except ValueError:
                                await send(chat, "Quantity and price must be numbers.")
                                continue
                            mgr.add_to_portfolio(user_id, parts[2].upper(), qty, price)
                            await send(chat, f"✅ Bought {qty} {parts[2].upper()} at ${price:,.2f} = ${qty*price:,.2f}")
                        elif sub == "sell" and len(parts) >= 5:
                            try:
                                qty = float(parts[3])
                                price = float(parts[4])
                            except ValueError:
                                await send(chat, "Quantity and price must be numbers.")
                                continue
                            ok, msg = mgr.sell_from_portfolio(user_id, parts[2].upper(), qty, price)
                            await send(chat, f"✅ {msg}" if ok else f"❌ {msg}")
                        elif sub == "portfolio":
                            await send(chat, mgr.get_portfolio_summary(user_id))
                        elif sub == "transactions":
                            await send(chat, mgr.get_transactions(user_id))
                        elif sub == "alert" and len(parts) >= 5:
                            symbol = parts[2].upper()
                            condition = parts[3].lower()
                            try:
                                target = float(parts[4])
                            except ValueError:
                                await send(chat, "Target price must be a number.")
                                continue
                            msg = " ".join(parts[5:]) if len(parts) > 5 else ""
                            mgr.add_alert(user_id, symbol, condition, target, msg)
                            await send(chat, f"✅ Alert: {symbol} {condition} ${target:,.2f}")
                        elif sub == "alerts":
                            profile = mgr.get_profile(user_id)
                            if not profile.alerts:
                                await send(chat, "No alerts.")
                            else:
                                lines = ["🔔 **Alerts:**\n"]
                                for a in profile.alerts:
                                    lines.append(f"`{a.alert_id[-6:]}` — {a.asset} {a.condition} ${a.target_value:,.2f}")
                                await send(chat, "\n".join(lines))
                        elif sub == "watch" and len(parts) >= 3:
                            ok = mgr.add_to_watchlist(user_id, parts[2].upper())
                            await send(chat, f"✅ Added {parts[2].upper()} to watchlist." if ok else f"⚠️ Already watching {parts[2].upper()}.")
                        elif sub == "unwatch" and len(parts) >= 3:
                            ok = mgr.remove_from_watchlist(user_id, parts[2].upper())
                            await send(chat, f"✅ Removed {parts[2].upper()}." if ok else f"❌ Not in watchlist.")
                        elif sub == "watchlist":
                            await send(chat, mgr.get_watchlist_display(user_id))
                        elif sub == "info" and len(parts) >= 3:
                            info = mgr.get_crypto_info(parts[2])
                            if info:
                                await send(chat, f"ℹ️ **{info['name']}** ({info['symbol']})\n\nPrice: ${info['price']:,.2f}")
                            else:
                                await send(chat, f"❌ Unknown: {parts[2]}")
                        else:
                            from finance_crypto import build_finance_commands
                            await send(chat, build_finance_commands())
                    except Exception as e:
                        await send(chat, f"Finance error: {str(e)[:200]}")

                elif cmd == "/cv":
                    try:
                        from computer_vision import handle_cv_command, get_cv_manager
                        sub = parts[1].lower() if len(parts) > 1 else ""
                        user_id = str(uid)
                        mgr = get_cv_manager()

                        if sub == "objects":
                            from computer_vision import analyze_objects_mock, COMMON_OBJECTS, AnalysisResult
                            objects = analyze_objects_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="objects",
                                timestamp=time.time(), processing_time=0.15, objects=objects)
                            mgr.save_result(result)
                            lines = ["🔍 **Object Detection:**\n"]
                            for obj in objects:
                                icon = COMMON_OBJECTS.get(obj.label, "📦")
                                lines.append(f"{icon} **{obj.label.title()}** — {obj.confidence*100:.1f}%")
                            await send(chat, "\n".join(lines))
                        elif sub == "faces":
                            from computer_vision import analyze_faces_mock, EMOTION_ICONS, AnalysisResult
                            faces = analyze_faces_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="faces",
                                timestamp=time.time(), processing_time=0.22, faces=faces)
                            mgr.save_result(result)
                            lines = ["👤 **Face Analysis:**\n"]
                            for i, face in enumerate(faces):
                                icon = EMOTION_ICONS.get(face.emotion, "😐")
                                lines.append(f"Face {i+1}: ~{face.age_estimate:.0f}y {face.gender} {icon} {face.emotion.title()}")
                            await send(chat, "\n".join(lines))
                        elif sub == "ocr":
                            from computer_vision import analyze_ocr_mock, AnalysisResult
                            ocr = analyze_ocr_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="ocr",
                                timestamp=time.time(), processing_time=0.18, ocr=ocr)
                            mgr.save_result(result)
                            await send(chat, f"📝 **OCR:**\n```\n{ocr.text}\n```\nConfidence: {ocr.confidence*100:.1f}%")
                        elif sub == "classify":
                            from computer_vision import classify_image_mock, AnalysisResult
                            cls = classify_image_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="classify",
                                timestamp=time.time(), processing_time=0.12, classification=cls)
                            mgr.save_result(result)
                            lines = ["🏷️ **Classification:**\n"]
                            for cat, conf in sorted(cls.items(), key=lambda x: x[1], reverse=True):
                                bar = "█" * int(conf * 20) + "░" * (20 - int(conf * 20))
                                lines.append(f"**{cat.title()}**: {bar} {conf*100:.1f}%")
                            await send(chat, "\n".join(lines))
                        elif sub == "describe":
                            from computer_vision import describe_image_mock, AnalysisResult
                            desc = describe_image_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="describe",
                                timestamp=time.time(), processing_time=0.35, description=desc)
                            mgr.save_result(result)
                            await send(chat, f"🖼️ **Description:**\n{desc}")
                        elif sub == "colors":
                            from computer_vision import extract_colors_mock, AnalysisResult
                            colors = extract_colors_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="colors",
                                timestamp=time.time(), processing_time=0.10, colors=colors)
                            mgr.save_result(result)
                            lines = ["🎨 **Color Palette:**\n"]
                            for c in colors:
                                lines.append(f"**{c.name}** `{c.hex}` — {c.percentage:.1f}%")
                            await send(chat, "\n".join(lines))
                        elif sub == "barcode":
                            from computer_vision import scan_barcode_mock, AnalysisResult
                            barcode = scan_barcode_mock()
                            result = AnalysisResult(
                                result_id=f"cv_{int(time.time()*1000) % 100000}",
                                user_id=user_id, analysis_type="barcode",
                                timestamp=time.time(), processing_time=0.08, barcode=barcode)
                            mgr.save_result(result)
                            await send(chat, f"📊 **Barcode:** `{barcode}`")
                        elif sub == "stats":
                            stats = mgr.get_stats(user_id)
                            await send(chat, f"📊 **CV Stats:**\nTotal: {stats['total']}\nTypes: {stats['by_type']}")
                        elif sub == "history":
                            profile = mgr.get_profile(user_id)
                            if not profile.analyses:
                                await send(chat, "No history yet.")
                            else:
                                lines = ["📜 **Recent:**\n"]
                                for a in reversed(profile.analyses[-5:]):
                                    ts = datetime.fromtimestamp(a.timestamp).strftime("%H:%M")
                                    lines.append(f"`{ts}` {a.analysis_type}")
                                await send(chat, "\n".join(lines))
                        else:
                            from computer_vision import build_cv_commands
                            await send(chat, build_cv_commands())
                    except Exception as e:
                        await send(chat, f"CV error: {str(e)[:200]}")

                elif cmd == "/style":
                    if not styles_mod:
                        await send(chat, "AI Styles module not available.")
                        continue
                    if not is_experimental_enabled("ai-styles"):
                        await send(chat, "AI Styles is disabled. Use /experimental on ai-styles to enable.")
                        continue
                    ast = styles_mod.get_ai_styles()
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub in ("list", ""):
                        all_s, active_n = ast.list_styles(uid)
                        lines = [f"AI Styles (active: {active_n or 'none'})", ""]
                        for sname, (stype, sdesc) in sorted(all_s.items()):
                            mark = "★ " if sname == active_n else "  "
                            lines.append(f"{mark}{sname} [{stype}] — {sdesc}")
                        lines.append("")
                        lines.append("Usage:")
                        lines.append("  /style on <name> — activate")
                        lines.append("  /style off — deactivate")
                        lines.append("  /style create <name> <text> — custom style")
                        lines.append("  /style show <name> — view style text")
                        lines.append("  /style delete <name> — delete custom style")
                        await send(chat, "\n".join(lines))
                    elif sub == "on":
                        if len(parts) < 3:
                            await send(chat, "Usage: /style on <name>")
                            continue
                        sname = parts[2]
                        if ast.set_active(uid, sname):
                            await send(chat, f"Style '{sname}' activated.")
                        else:
                            await send(chat, f"Style '{sname}' not found. Use /style list to see available styles.")
                    elif sub == "off":
                        ast.set_active(uid, None)
                        await send(chat, "Style deactivated.")
                    elif sub == "show":
                        if len(parts) < 3:
                            await send(chat, "Usage: /style show <name>")
                            continue
                        sname = parts[2]
                        stext = ast.get_style_text(uid, sname)
                        if stext:
                            await send(chat, f"Style '{sname}':\n{stext}")
                        else:
                            await send(chat, f"Style '{sname}' not found.")
                    elif sub == "create":
                        if len(parts) < 4:
                            await send(chat, "Usage: /style create <name> <style text>")
                            continue
                        sname = parts[2]
                        stext = " ".join(parts[3:])
                        ast.create_custom(uid, sname, stext)
                        await send(chat, f"Custom style '{sname}' created. Use /style on {sname} to activate.")
                    elif sub == "delete":
                        if len(parts) < 3:
                            await send(chat, "Usage: /style delete <name>")
                            continue
                        sname = parts[2]
                        if ast.delete_style(uid, sname):
                            await send(chat, f"Style '{sname}' deleted.")
                        else:
                            await send(chat, f"Style '{sname}' not found or is a built-in preset (cannot delete).")

                elif cmd == "/pollplus":
                    if not pollplus_mod or not pw_mod:
                        await send(chat, "Poll Plus module or Paywall not available.")
                        continue
                    if not is_experimental_enabled("poll-plus"):
                        await send(chat, "Poll Plus is disabled. Use /experimental on poll-plus to enable.")
                        continue
                    pw = pw_mod.get_paywall()
                    has_sub = any(s.get("active") for s in pw.user_subs(uid))
                    if not has_sub and not is_owner:
                        await send(chat, f"This feature requires an active subscription.\n{pw.payment_instructions()}")
                        continue
                    pp = pollplus_mod.get_poll_plus()
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "track":
                        if len(parts) < 3:
                            await send(chat, "Usage: /pollplus track <poll_id>\nForward a poll to me or paste its ID.")
                            continue
                        pid = parts[2]
                        existing = pp.get_poll(pid)
                        if existing:
                            await send(chat, f"Already tracking poll {pid}.")
                            continue
                        await send(chat, f"Poll {pid} is now being tracked. Use /pollplus stats {pid} to see results.")
                    elif sub == "stats":
                        if len(parts) < 3:
                            await send(chat, "Usage: /pollplus stats <poll_id>")
                            continue
                        pid = parts[2]
                        formatted = pp.format_stats(pid)
                        if formatted:
                            await send(chat, formatted)
                        else:
                            await send(chat, f"No data for poll {pid}. Track it first with /pollplus track {pid}")
                    elif sub == "list":
                        tracked = pp.list_tracked(chat)
                        if not tracked:
                            await send(chat, "No polls tracked in this chat. Use /pollplus track <poll_id> to start.")
                        else:
                            lines = ["Tracked polls in this chat:"]
                            for p in tracked:
                                lines.append(f"  {p['id']} — {p['question'][:50]}")
                            await send(chat, "\n".join(lines))

                elif cmd == "/content":
                    if not ca_mod:
                        await send(chat, "Content Automation module not available.")
                        continue
                    if not is_experimental_enabled("content-automation"):
                        await send(chat, "Content Automation is disabled. Use /experimental enable content-automation")
                        continue
                    ca = ca_mod.get_ca()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, ca.get_status(chat))
                    elif sub == "on":
                        ca.toggle(chat)
                        await send(chat, "Content Automation ON.")
                    elif sub == "off":
                        ca.toggle(chat)
                        await send(chat, "Content Automation OFF.")
                    elif sub == "add":
                        if len(parts) < 3:
                            await send(chat, "Usage: /content add <rss_url> [label]")
                            continue
                        url = parts[2]
                        label = parts[3] if len(parts) > 3 else None
                        fid = ca.add_feed(chat, url, label=label)
                        await send(chat, f"Feed added: {url}\nID: {fid}\nUse /content on to enable auto-posting.")
                    elif sub == "remove":
                        if len(parts) < 3:
                            await send(chat, "Usage: /content remove <feed_id>")
                            continue
                        ca.remove_feed(chat, parts[2])
                        await send(chat, f"Feed {parts[2]} removed.")
                    elif sub == "channel":
                        if len(parts) < 3:
                            await send(chat, "Usage: /content channel <channel_id>\n(Use -100... format for private channels)")
                            continue
                        ca.set_channel(chat, parts[2])
                        await send(chat, f"Channel set to {parts[2]}")
                    else:
                        await send(chat, "Content commands: status, on, off, add, remove, channel")

                elif cmd == "/analytics":
                    if not an_mod:
                        await send(chat, "Analytics module not available.")
                        continue
                    if not is_experimental_enabled("analytics-dashboard"):
                        await send(chat, "Analytics Dashboard is disabled. Use /experimental enable analytics-dashboard")
                        continue
                    an = an_mod.get_analytics()
                    sub = parts[1].lower() if len(parts) > 1 else "stats"
                    days = 7
                    if len(parts) > 2:
                        try:
                            days = max(1, min(90, int(parts[2])))
                        except Exception:
                            days = 7
                    if sub == "stats":
                        await send(chat, an.format_stats(chat, days))
                    elif sub == "daily":
                        await send(chat, an.format_daily(chat, days))
                    elif sub == "top":
                        stats = an.get_stats(chat, days)
                        if not stats:
                            await send(chat, "No data.")
                        else:
                            lines = [f"Top users ({days}d):"]
                            for uid, cnt in stats.get("top_users", []):
                                lines.append(f"  {uid}: {cnt} msgs")
                            await send(chat, "\n".join(lines))
                    else:
                        await send(chat, "Analytics commands: stats [days], daily [days], top [days]")

                elif cmd == "/sub":
                    if not pw_mod:
                        await send(chat, "Paywall module not available.")
                        continue
                    if not is_experimental_enabled("subscription-paywall"):
                        await send(chat, "Subscription Paywall is disabled. Use /experimental enable subscription-paywall")
                        continue
                    pw = pw_mod.get_paywall()
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    if sub == "list":
                        plans = pw.list_plans()
                        if not plans:
                            await send(chat, "No active plans. Admins can use /sub create to add one.")
                        else:
                            lines = ["Available plans:"]
                            for p in plans:
                                lines.append(pw.format_plan(p))
                            lines.append("")
                            lines.append(pw.payment_instructions())
                            await send(chat, "\n".join(lines))
                    elif sub == "status":
                        user_subs = pw.user_subs(uid)
                        active = [s for s in user_subs if s.get("active")]
                        if not active:
                            await send(chat, "You have no active subscriptions.\n" + pw.payment_instructions())
                        else:
                            lines = ["Your subscriptions:"]
                            for s in active:
                                plan = pw.get_plan(s["plan_id"])
                                exp = datetime.fromtimestamp(s["expires"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                                lines.append(f"  {plan['name'] if plan else s['plan_id']} — expires {exp}")
                            await send(chat, "\n".join(lines))
                    elif sub == "pay":
                        if len(parts) < 3:
                            await send(chat, "Usage: /sub pay <plan_id>")
                            continue
                        plan_id = parts[2]
                        plan = pw.get_plan(plan_id)
                        if not plan:
                            await send(chat, "Plan not found.")
                            continue
                        inv_id = pw.create_stars_invoice(plan_id, uid)
                        await send(chat, f"Invoice created (pending): {inv_id}\nPlan: {plan['name']}\n{pw.payment_instructions()}")
                    elif sub == "create":
                        if not is_owner and not is_admin:
                            await send(chat, "Owner/Admin only.")
                            continue
                        if len(parts) < 5:
                            await send(chat, "Usage: /sub create <name> <stars_price> <days> [description]")
                            continue
                        name = parts[2]
                        try:
                            price = int(parts[3])
                            days_sub = int(parts[4])
                        except Exception:
                            await send(chat, "Price and days must be numbers.")
                            continue
                        desc = " ".join(parts[5:]) if len(parts) > 5 else f"{name} subscription"
                        pid = pw.create_plan(uid, name, desc, price, days_sub)
                        await send(chat, f"Plan created: {name}\nID: {pid}\n{pw.format_plan(pw.get_plan(pid))}")
                    elif sub == "cancel":
                        if len(parts) < 3:
                            await send(chat, "Usage: /sub cancel <plan_id>")
                            continue
                        if pw.cancel(parts[2], uid):
                            await send(chat, "Subscription cancelled.")
                        else:
                            await send(chat, "No active subscription found for that plan.")
                    else:
                        await send(chat, "Sub commands: list, status, pay, create (admin), cancel")

                elif cmd == "/safety":
                    if not safety_mod:
                        await send(chat, "Safety module not available.")
                        continue
                    if not is_experimental_enabled("safety-moderation"):
                        await send(chat, "Safety & Moderation is disabled. Use /experimental enable safety-moderation")
                        continue
                    sf = safety_mod.get_safety()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, sf.format_config(chat))
                    elif sub == "on":
                        sf.toggle(chat)
                        await send(chat, "Safety & Moderation ON.")
                    elif sub == "off":
                        sf.toggle(chat)
                        await send(chat, "Safety & Moderation OFF.")
                    elif sub == "log":
                        log_entries = sf.get_log(chat)
                        if not log_entries:
                            await send(chat, "No safety events logged.")
                        else:
                            lines = [f"Safety log ({len(log_entries)} entries):"]
                            for e in log_entries[-10:]:
                                lines.append(f"  [{e['feature']}] {e['action']} — user {e['user']}: {e['detail'][:80]}")
                            await send(chat, "\n".join(lines))
                    elif sub == "trust":
                        if len(parts) < 3:
                            await send(chat, "Usage: /safety trust <user_id>")
                            continue
                        sf.add_trusted_user(chat, parts[2])
                        await send(chat, f"User {parts[2]} trusted.")
                    elif sub == "ban-global":
                        if len(parts) < 3:
                            await send(chat, "Usage: /safety ban-global <user_id> [reason]")
                            continue
                        reason = " ".join(parts[3:]) if len(parts) > 3 else "spam"
                        sf.add_to_global_ban(parts[2], reason, chat)
                        await send(chat, f"User {parts[2]} globally banned: {reason}")
                    elif sub == "reputation":
                        if len(parts) < 3:
                            await send(chat, "Usage: /safety reputation <user_id>")
                            continue
                        rep = sf.get_reputation(parts[2])
                        await send(chat, f"Reputation for {parts[2]}:\n  Score: {rep.get('score', 50)}/100\n  Violations: {rep.get('violations', 0)}\n  Verified: {rep.get('verified', False)}")
                    else:
                        await send(chat, "Safety commands: status, on, off, log, trust, ban-global, reputation")

                elif cmd == "/dev":
                    if not dev_mod:
                        await send(chat, "Dev Tools module not available.")
                        continue
                    if not is_experimental_enabled("coding-dev-tools"):
                        await send(chat, "Coding & Dev Tools is disabled. Use /experimental enable coding-dev-tools")
                        continue
                    dt = dev_mod.get_dev_tools()
                    sub = parts[1].lower() if len(parts) > 1 else "help"
                    if sub == "cwd":
                        await send(chat, f"Working directory: {dt.get_working_dir(uid)}")
                    elif sub == "setcwd":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev setcwd <path>")
                            continue
                        ok, msg = dt.set_working_dir(uid, " ".join(parts[2:]))
                        await send(chat, msg)
                    elif sub == "exec":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev exec <code>\nLanguages: python, javascript, bash")
                            continue
                        lang = "python"
                        code = " ".join(parts[2:])
                        if code.startswith("```"):
                            code = code.split("\n", 1)[-1].rsplit("```", 1)[0]
                        ok, result = await dt.execute_code(uid, code, lang)
                        await send(chat, result[:4000])
                    elif sub == "history":
                        await send(chat, dt.list_history(uid))
                    elif sub == "clear":
                        dt.clear_history(uid)
                        await send(chat, "History cleared.")
                    elif sub == "github-token":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev github-token <token>")
                            continue
                        dt.set_github_token(uid, parts[2])
                        await send(chat, "GitHub token set.")
                    elif sub == "repos":
                        ok, result = await dt.github_repos(uid)
                        await send(chat, result[:4000] if ok else result)
                    elif sub == "issues":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev issues <owner/repo>")
                            continue
                        ok, result = await dt.github_issues(uid, parts[2])
                        await send(chat, result[:4000] if ok else result)
                    elif sub == "prs":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev prs <owner/repo>")
                            continue
                        ok, result = await dt.github_prs(uid, parts[2])
                        await send(chat, result[:4000] if ok else result)
                    elif sub == "docs":
                        if len(parts) < 3:
                            await send(chat, "Usage: /dev docs <filepath>")
                            continue
                        ok, result = await dt.generate_api_docs(parts[2])
                        await send(chat, result[:4000] if ok else result)
                    else:
                        await send(chat, "Dev commands: cwd, setcwd, exec, history, clear, github-token, repos, issues, prs, docs")

                elif cmd == "/aiint":
                    if not ai_int_mod:
                        await send(chat, "AI Intelligence module not available.")
                        continue
                    if not is_experimental_enabled("ai-intelligence"):
                        await send(chat, "AI Intelligence is disabled. Use /experimental enable ai-intelligence")
                        continue
                    ai = ai_int_mod.get_ai_intelligence()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, ai.format_config(chat))
                    elif sub == "on":
                        ai.toggle(chat)
                        await send(chat, "AI Intelligence ON.")
                    elif sub == "off":
                        ai.toggle(chat)
                        await send(chat, "AI Intelligence OFF.")
                    elif sub == "domain":
                        if len(parts) < 3:
                            await send(chat, ai.list_domains())
                            continue
                        ok, msg = ai.set_domain(chat, parts[2])
                        await send(chat, msg)
                    elif sub == "persona":
                        if len(parts) < 3:
                            personas = ai.list_personas(uid)
                            if not personas:
                                await send(chat, "No custom personas. Use /aiint create-persona <name> <desc> <prompt>")
                            else:
                                lines = ["Your personas:"]
                                for pid, p in personas.items():
                                    lines.append(f"  [{pid}] {p['name']}: {p['description'][:50]}")
                                await send(chat, "\n".join(lines))
                            continue
                        ok, msg = ai.set_persona(chat, parts[2])
                        await send(chat, msg)
                    elif sub == "create-persona":
                        if len(parts) < 5:
                            await send(chat, "Usage: /aiint create-persona <name> <description> <system_prompt>")
                            continue
                        pid = ai.create_persona(uid, parts[2], parts[3], " ".join(parts[4:]))
                        await send(chat, f"Persona created: {pid} ({parts[2]})")
                    elif sub == "briefing":
                        if len(parts) < 3:
                            ai.schedule_briefing(chat, "daily", "08:00")
                            await send(chat, "Daily briefing scheduled at 08:00 UTC.")
                        elif parts[2] == "off":
                            ai.cancel_briefing(chat)
                            await send(chat, "Briefing cancelled.")
                        else:
                            ai.schedule_briefing(chat, "daily", parts[2])
                            await send(chat, f"Briefing scheduled at {parts[2]} UTC.")
                    elif sub == "profile":
                        profile = ai.get_user_profile(uid)
                        if not profile:
                            await send(chat, "No profile data yet.")
                        else:
                            lines = [f"Your AI profile:"]
                            lines.append(f"  Mood: {profile.get('mood', 'neutral')}")
                            lines.append(f"  Interests: {', '.join(profile.get('interests', [])) or 'none'}")
                            lines.append(f"  Interactions: {profile.get('interaction_count', 0)}")
                            lines.append(f"  Style: {profile.get('preferred_style', 'balanced')}")
                            await send(chat, "\n".join(lines))
                    else:
                        await send(chat, "AI Intelligence commands: status, on, off, domain, persona, create-persona, briefing, profile")

                elif cmd == "/community":
                    if not comm_mod:
                        await send(chat, "Community module not available.")
                        continue
                    if not is_experimental_enabled("community-engagement"):
                        await send(chat, "Community Engagement is disabled. Use /experimental enable community-engagement")
                        continue
                    ce = comm_mod.get_community()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, ce.format_config(chat))
                    elif sub == "on":
                        ce.toggle(chat)
                        await send(chat, "Community Engagement ON.")
                    elif sub == "off":
                        ce.toggle(chat)
                        await send(chat, "Community Engagement OFF.")
                    elif sub == "welcome":
                        if len(parts) < 3:
                            w = ce.get_welcome(chat)
                            await send(chat, f"Welcome: {'ON' if w['enabled'] else 'OFF'}\nTemplate: {w['template']}")
                        elif parts[2] == "on":
                            ce.set_welcome(chat, enabled=True)
                            await send(chat, "Welcome messages ON.")
                        elif parts[2] == "off":
                            ce.set_welcome(chat, enabled=False)
                            await send(chat, "Welcome messages OFF.")
                        elif parts[2] == "set":
                            template = " ".join(parts[3:]) if len(parts) > 3 else None
                            ce.set_welcome(chat, template=template)
                            await send(chat, f"Welcome template set: {template}")
                        else:
                            await send(chat, "Usage: /community welcome [on|off|set <template>]")
                    elif sub == "server-plan":
                        if len(parts) < 3:
                            await send(chat, "Usage: /community server-plan <description>\nExample: /community server-plan gaming community for Valorant players")
                            continue
                        prompt = " ".join(parts[2:])
                        plan = ce.generate_server_plan(prompt)
                        await send(chat, ce.format_server_plan(plan))
                    elif sub == "reaction-role":
                        if len(parts) < 5:
                            await send(chat, "Usage: /community reaction-role <message_id> <emoji> <role_name>")
                            continue
                        msg = ce.add_reaction_role(chat, parts[2], parts[3], " ".join(parts[4:]))
                        await send(chat, msg)
                    else:
                        await send(chat, "Community commands: status, on, off, welcome, server-plan, reaction-role")

                elif cmd == "/automate":
                    if not auto_mod:
                        await send(chat, "Automation module not available.")
                        continue
                    if not is_experimental_enabled("automation-productivity"):
                        await send(chat, "Automation & Productivity is disabled. Use /experimental enable automation-productivity")
                        continue
                    ap = auto_mod.get_automation()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, ap.format_config(chat))
                    elif sub == "on":
                        ap.toggle(chat)
                        await send(chat, "Automation ON.")
                    elif sub == "off":
                        ap.toggle(chat)
                        await send(chat, "Automation OFF.")
                    elif sub == "drip":
                        if len(parts) < 4:
                            await send(chat, "Usage: /automate drip create <name> | <msg1> | <msg2> | ...\nOr: /automate drip list")
                            continue
                        action = parts[2].lower()
                        if action == "list":
                            drips = ap.list_drips(chat)
                            if not drips:
                                await send(chat, "No drip sequences.")
                            else:
                                lines = ["Drip sequences:"]
                                for did, d in drips.items():
                                    lines.append(f"  [{did}] {d['name']} ({len(d.get('messages', []))} messages, {len(d.get('subscribers', []))} subs)")
                                await send(chat, "\n".join(lines))
                        elif action == "create":
                            name_msg = " ".join(parts[3:])
                            parts_split = name_msg.split("|")
                            name = parts_split[0].strip()
                            messages = [m.strip() for m in parts_split[1:] if m.strip()]
                            if not messages:
                                await send(chat, "Usage: /automate drip create <name> | <msg1> | <msg2>")
                                continue
                            did = ap.create_drip(chat, name, messages)
                            await send(chat, f"Drip created: {did} ({name}, {len(messages)} messages)")
                        elif action == "subscribe":
                            if len(parts) < 4:
                                await send(chat, "Usage: /automate drip subscribe <drip_id>")
                                continue
                            ok, msg = ap.subscribe_drip(parts[3], uid)
                            await send(chat, msg)
                        else:
                            await send(chat, "Drip commands: list, create, subscribe")
                    elif sub == "crm":
                        crm_action = parts[2].lower() if len(parts) > 2 else "list"
                        if crm_action == "add":
                            if len(parts) < 5:
                                await send(chat, "Usage: /automate crm add <user_id> <name> [phone]")
                                continue
                            phone = parts[5] if len(parts) > 5 else None
                            ap.add_crm_contact(chat, parts[3], parts[4], phone=phone)
                            await send(chat, f"CRM contact added: {parts[4]}")
                        elif crm_action == "list":
                            contacts = ap.list_crm_contacts(chat)
                            if not contacts:
                                await send(chat, "No CRM contacts.")
                            else:
                                lines = [f"CRM contacts ({len(contacts)}):"]
                                for uid_c, c in list(contacts.items())[:10]:
                                    lines.append(f"  {c.get('name', uid_c)}: {c.get('phone', 'no phone')}")
                                await send(chat, "\n".join(lines))
                        elif crm_action == "search":
                            if len(parts) < 4:
                                await send(chat, "Usage: /automate crm search <query>")
                                continue
                            results = ap.search_crm(chat, " ".join(parts[3:]))
                            if not results:
                                await send(chat, "No matches.")
                            else:
                                lines = [f"Search results ({len(results)}):"]
                                for uid_c, c in results.items():
                                    lines.append(f"  {c.get('name', uid_c)}: {c.get('tags', [])}")
                                await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "CRM commands: add, list, search")
                    elif sub == "wizard":
                        if len(parts) < 3:
                            await send(chat, "Usage: /automate wizard list")
                            continue
                        action = parts[2].lower()
                        if action == "list":
                            wizards = ap.list_wizards(chat)
                            if not wizards:
                                await send(chat, "No wizards.")
                            else:
                                lines = ["Wizards:"]
                                for wid, w in wizards.items():
                                    lines.append(f"  [{wid}] {w['name']} ({len(w.get('steps', []))} steps)")
                                await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "Wizard commands: list")
                    else:
                        await send(chat, "Automate commands: status, on, off, drip, crm, wizard")

                elif cmd == "/secapi":
                    if not sec_mod:
                        await send(chat, "Security API module not available.")
                        continue
                    if not is_experimental_enabled("security-api"):
                        await send(chat, "Security & API is disabled. Use /experimental enable security-api")
                        continue
                    sa = sec_mod.get_security_api()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, sa.format_config(chat))
                    elif sub == "on":
                        sa.toggle(chat)
                        await send(chat, "Security & API ON.")
                    elif sub == "off":
                        sa.toggle(chat)
                        await send(chat, "Security & API OFF.")
                    elif sub == "ephemeral":
                        if len(parts) < 3:
                            await send(chat, "Usage: /secapi ephemeral <message>\n(Sends a self-destructing message)")
                            continue
                        text = " ".join(parts[2:])
                        result = sa.create_ephemeral(chat, uid, text)
                        if result:
                            await send(chat, f"🔒 Ephemeral message sent (ID: {result['ephemeral_id']}, TTL: {result['ttl']}s)")
                        else:
                            await send(chat, "Ephemeral messages disabled.")
                    elif sub == "webhook":
                        if len(parts) < 3:
                            whs = sa.list_webhooks()
                            if not whs:
                                await send(chat, "No webhooks configured.")
                            else:
                                lines = [f"Webhooks ({len(whs)}):"]
                                for wid, wh in whs.items():
                                    status = "ON" if wh.get("enabled") else "OFF"
                                    lines.append(f"  [{wid}] {wh['name']} → {wh['url'][:50]} ({status})")
                                await send(chat, "\n".join(lines))
                            continue
                        action = parts[2].lower()
                        if action == "add" and len(parts) >= 5:
                            name = parts[3]
                            url = parts[4]
                            wid = sa.add_webhook(name, url)
                            await send(chat, f"Webhook added: {wid} ({name})")
                        elif action == "remove" and len(parts) >= 4:
                            sa.remove_webhook(parts[3])
                            await send(chat, f"Webhook {parts[3]} removed.")
                        else:
                            await send(chat, "Webhook commands: add <name> <url>, remove <id>")
                    elif sub == "guest-bot":
                        if len(parts) < 3:
                            await send(chat, "Usage: /secapi guest-bot add <bot_username>")
                            continue
                        action = parts[2].lower()
                        if action == "add" and len(parts) >= 4:
                            bot_name = parts[3].lstrip("@")
                            msg = sa.add_guest_bot(chat, bot_name)
                            await send(chat, msg)
                        elif action == "remove" and len(parts) >= 4:
                            bot_name = parts[3].lstrip("@")
                            msg = sa.remove_guest_bot(chat, bot_name)
                            await send(chat, msg)
                        else:
                            await send(chat, "Guest bot commands: add <username>, remove <username>")
                    elif sub == "bot-bot":
                        if len(parts) < 3:
                            await send(chat, "Usage: /secapi bot-bot add <bot_username>")
                            continue
                        action = parts[2].lower()
                        if action == "add" and len(parts) >= 4:
                            bot_name = parts[3].lstrip("@")
                            msg = sa.add_bot_bot_partner(chat, bot_name)
                            await send(chat, msg)
                        elif action == "remove" and len(parts) >= 4:
                            bot_name = parts[3].lstrip("@")
                            msg = sa.remove_bot_bot_partner(chat, bot_name)
                            await send(chat, msg)
                        else:
                            await send(chat, "Bot-bot commands: add <username>, remove <username>")
                    else:
                        await send(chat, "Security API commands: status, on, off, ephemeral, webhook, guest-bot, bot-bot")

                elif cmd == "/languages":
                    if not nf_mod:
                        await send(chat, "New Features module not available.")
                        continue
                    nf = nf_mod.get_new_features()
                    await send(chat, nf.list_languages()[:2000])

                elif cmd == "/ocr":
                    if not nf_mod:
                        await send(chat, "New Features module not available.")
                        continue
                    if not is_experimental_enabled("new-research-features"):
                        await send(chat, "New Research Features is disabled. Use /experimental enable new-research-features")
                        continue
                    nf = nf_mod.get_new_features()
                    if not msg.get("photo"):
                        await send(chat, "Send a photo with /ocr as caption, or reply to a photo with /ocr")
                        continue
                    await typing(chat)
                    photo = msg["photo"][-1]
                    file_id = photo["file_id"]
                    try:
                        c = await get_http()
                        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                        file_resp = await c.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}", timeout=15)
                        file_data = file_resp.json()
                        if file_data.get("ok"):
                            file_path = file_data["result"]["file_path"]
                            dl_resp = await c.get(f"https://api.telegram.org/file/bot{bot_token}/{file_path}", timeout=30)
                            if dl_resp.status_code == 200:
                                text = nf.extract_text_from_image_data(dl_resp.content)
                                if text:
                                    await send(chat, f"📄 OCR Result:\n{text[:4000]}")
                                else:
                                    await send(chat, "Could not extract text from image. Make sure the image contains readable text.")
                            else:
                                await send(chat, "Could not download image.")
                        else:
                            await send(chat, "Could not get file info.")
                    except Exception as e:
                        await send(chat, f"OCR error: {str(e)[:200]}")

                elif cmd == "/loc":
                    if not loc_mod:
                        await send(chat, "Location module not available.")
                        continue
                    if not is_experimental_enabled("location-distance"):
                        await send(chat, "Location & Distance is disabled. Use /experimental enable location-distance")
                        continue
                    ld = loc_mod.get_location()
                    sub = parts[1].lower() if len(parts) > 1 else "status"
                    if sub == "status":
                        await send(chat, ld.format_config(chat))
                    elif sub == "set":
                        if len(parts) < 4:
                            await send(chat, "Usage: /loc set <lat> <lon> [name]\nExample: /loc set -6.2088 106.8456 Home")
                            continue
                        try:
                            lat, lon = float(parts[2]), float(parts[3])
                            name = " ".join(parts[4:]) if len(parts) > 4 else "Home"
                            ld.set_home(chat, lat, lon, name)
                            await send(chat, f"Home location set: {name} ({lat}, {lon})")
                        except ValueError:
                            await send(chat, "Invalid coordinates. Use decimal format like -6.2088 106.8456")
                    elif sub == "here":
                        if msg.get("location"):
                            loc = msg["location"]
                            ld.record_user_location(chat, uid, loc["latitude"], loc["longitude"])
                            dist = ld.get_distance(chat, uid)
                            maxd = ld.get_max_distance(chat)
                            lines = [f"Your location recorded ({loc['latitude']:.4f}, {loc['longitude']:.4f})"]
                            if dist is not None:
                                lines.append(f"Distance from home: {dist:.1f} km")
                                if maxd:
                                    status = "WITHIN" if dist <= maxd else "OUTSIDE"
                                    lines.append(f"Range: {status} ({status.lower()} {maxd} km limit)")
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, "Send your location using Telegram's location button (📎 → Location), then reply with /loc here")
                    elif sub == "range":
                        if len(parts) < 3:
                            maxd = ld.get_max_distance(chat)
                            await send(chat, f"Current max distance: {maxd} km" if maxd else "No distance limit set.")
                            continue
                        try:
                            km = float(parts[2])
                            ld.set_max_distance(chat, km)
                            await send(chat, f"Max distance set to {km} km. Bot will only respond within this range.")
                        except ValueError:
                            await send(chat, "Usage: /loc range <km>")
                    elif sub == "nearby":
                        users = ld.get_all_users_in_range(chat)
                        if not users:
                            await send(chat, "No users tracked or no home set.")
                        else:
                            lines = [f"Users within range ({len(users)}):"]
                            for u in users[:10]:
                                lines.append(f"  User {u['user_id']}: {u['distance_km']} km")
                            await send(chat, "\n".join(lines))
                    elif sub == "dist":
                        if len(parts) < 3:
                            await send(chat, "Usage: /loc dist <user_id>")
                            continue
                        dist = ld.get_distance(chat, parts[2])
                        if dist is None:
                            await send(chat, "No location data for that user.")
                        else:
                            await send(chat, f"User {parts[2]} is {dist:.1f} km from home.")
                    else:
                        await send(chat, "Location commands:\n  /loc set <lat> <lon> [name] — set home\n  /loc here — record your location (send location first)\n  /loc range <km> — set max distance\n  /loc nearby — users in range\n  /loc dist <user_id> — distance to user\n  /loc status — current config")

                elif cmd == "/miniapp":
                    if not ma_mod:
                        await send(chat, "Mini App module not available.")
                        continue
                    if not is_experimental_enabled("mini-apps"):
                        await send(chat, "Mini Apps is disabled. Use /experimental enable mini-apps")
                        continue
                    action, data = ma_mod.handle_mini_app_command(parts, uid, is_owner)
                    response = ma_mod.format_mini_app_response(action, data)
                    if response:
                        await send(chat, response)

                elif cmd == "/weather":
                    city = " ".join(parts[1:]) if len(parts) > 1 else ""
                    await typing(chat)
                    try:
                        c = await get_http()
                        if city:
                            r = await c.get(f"https://wttr.in/{city}?format=%C+%t+%h+%w&lang=en", timeout=10)
                        else:
                            r = await c.get("https://wttr.in?format=%C+%t+%h+%w", timeout=10)
                        if r.status_code == 200:
                            weather_text = r.text.strip()
                            r2 = await c.get(f"https://wttr.in/{city or ''}?format=3", timeout=10)
                            header = r2.text.strip() if r2.status_code == 200 else ""
                            r3 = await c.get(f"https://wttr.in/{city or ''}?format=%C+%t+Feels+like+%f+Wind:%w+Humidity:%h+UV:%u+Visibility:%V", timeout=10)
                            details = r3.text.strip() if r3.status_code == 200 else weather_text
                            lines = [f"Weather {header}", details]
                            await send(chat, "\n".join(lines))
                        else:
                            await send(chat, f"Weather error: HTTP {r.status_code}")
                    except Exception as e:
                        await send(chat, f"Weather error: {e}")

                elif cmd == "/backup":
                    if not is_owner and not is_admin:
                        await send(chat, "Owner/Admin only.")
                        continue
                    if not _check_rate_limit(f"backup:{chat}", max_calls=2, window=3600):
                        await send(chat, "Rate limit: /backup can be used 2 times per hour.")
                        continue
                    await typing(chat)
                    try:
                        import zipfile, io as _bio
                        buf = _bio.BytesIO()
                        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                            data_files = [
                                "agents.json", "providers.json", "premade_skills.json",
                                "teams.json", "sessions.json", "admins.json", "mods.json",
                                "agent_providers.json", "routines.json", "multi_sessions.json",
                                "memory.json", "token_usage.json", "mods.json",
                                "schedule.json", "reminders.json", "usage_stats.json",
                                "version.json", "workflows.json",
                            ]
                            for fname in data_files:
                                fpath = os.path.join(os.path.dirname(__file__), fname)
                                if os.path.exists(fpath):
                                    zf.write(fpath, fname)
                            backups_dir = os.path.join(os.path.dirname(__file__), "backups")
                            os.makedirs(backups_dir, exist_ok=True)
                            backup_name = f"backup_{int(time.time())}.zip"
                            backup_path = os.path.join(backups_dir, backup_name)
                            with open(backup_path, "wb") as _bf:
                                _bf.write(buf.getvalue())
                            buf.seek(0)
                            await tg("sendDocument", {
                                "chat_id": chat,
                                "document": ("backup.zip", buf.getvalue()),
                                "caption": f"Backup: {len(data_files)} files, {len(buf.getvalue())} bytes"
                            })
                            await send(chat, f"Backup saved: {backup_name}")
                    except Exception as e:
                        await send(chat, f"Backup error: {e}")

                elif cmd == "/backup-keys":
                    if not is_owner:
                        await send(chat, "Owner only.")
                        continue
                    try:
                        import key_backup
                        sub_backup = parts[1].lower() if len(parts) > 1 else "save"
                        if sub_backup == "save":
                            result = key_backup.backup_keys()
                            if result.get("success"):
                                await send(chat, f"Keys backed up: {result['count']} keys\nTimestamp: {result['timestamp']}")
                            else:
                                await send(chat, f"Backup failed: {result.get('error', 'unknown')}")
                        elif sub_backup == "restore":
                            result = key_backup.restore_keys()
                            if result.get("success"):
                                await send(chat, f"Keys restored: {result['count']} keys\nRestored: {', '.join(result.get('restored', [])[:10])}")
                            else:
                                await send(chat, f"Restore failed: {result.get('error', 'unknown')}")
                        elif sub_backup == "list":
                            info = key_backup.list_backed_up()
                            if info.get("success"):
                                lines = [f"Keys backed up: {info['count']}\nTimestamp: {info['timestamp']}\nChecksum: {info['checksum']}\n"]
                                for k, v in info.get("keys", {}).items():
                                    lines.append(f"  {k}: {v}")
                                await send(chat, "\n".join(lines))
                            else:
                                await send(chat, f"No backup: {info.get('error', 'unknown')}")
                        elif sub_backup == "check":
                            missing = key_backup.check_missing_keys()
                            if missing:
                                await send(chat, f"Missing keys: {', '.join(missing)}\nUse /backup-keys restore to fix")
                            else:
                                await send(chat, "All critical keys present in .env")
                        else:
                            await send(chat, "Usage:\n/backup-keys save — Backup all keys\n/backup-keys restore — Restore keys from backup\n/backup-keys list — Show backed up keys (masked)\n/backup-keys check — Check for missing keys")
                    except Exception as e:
                        await send(chat, f"Key backup error: {e}")

                elif cmd == "/restore":
                    if not is_owner and not is_admin:
                        await send(chat, "Owner/Admin only.")
                        continue
                    if not _check_rate_limit(f"restore:{chat}", max_calls=2, window=3600):
                        await send(chat, "Rate limit: /restore can be used 2 times per hour.")
                        continue
                    if not msg.get("reply_to_message") or not msg["reply_to_message"].get("document"):
                        await send(chat, "Reply to a backup.zip file with /restore")
                        continue
                    await typing(chat)
                    try:
                        file_id = msg["reply_to_message"]["document"]["file_id"]
                        c = await get_http()
                        r = await c.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}")
                        data = r.json()
                        if not data.get("ok"):
                            await send(chat, "Could not fetch backup file.")
                            continue
                        path = data["result"]["file_path"]
                        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"
                        zip_data = (await c.get(file_url)).content
                        import zipfile, io as _bio
                        zf = zipfile.ZipFile(_bio.BytesIO(zip_data))
                        restored = []
                        base_dir = os.path.realpath(os.path.dirname(__file__))
                        for name in zf.namelist():
                            if name.endswith(".json"):
                                target = os.path.realpath(os.path.join(base_dir, name))
                                if not target.startswith(base_dir):
                                    continue
                                with open(target, "wb") as f:
                                    f.write(zf.read(name))
                                restored.append(name)
                        zf.close()
                        await send(chat, f"Restored {len(restored)} files:\n" + "\n".join(f"  {n}" for n in restored) + "\nRestart bot with /start to apply.")
                    except Exception as e:
                        await send(chat, f"Restore error: {e}")

                elif cmd == "/dailydigest":
                    await typing(chat)
                    try:
                        usage = bf.get_global_stats()
                        top_agents = ", ".join(f"{a}({c})" for a, c in usage.get("top_agents", [])[:5]) or "none"
                        top_providers = ", ".join(f"{p}({c})" for p, c in usage.get("top_providers", [])[:5]) or "none"
                        c = await get_http()
                        r = await c.get("https://wttr.in?format=%C+%t+%h+%w", timeout=10)
                        weather = r.text.strip() if r.status_code == 200 else "N/A"
                        r2 = await c.get("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", timeout=10)
                        headlines = []
                        if r2.status_code == 200:
                            headlines = re.findall(r"<title>(.*?)</title>", r2.text)[1:6]
                        lines = [
                            f"Daily Digest — {time.strftime('%Y-%m-%d %H:%M')}",
                            "",
                            f"Weather: {weather}",
                            "",
                            f"Bot Stats:",
                            f"  Users: {usage['total_users']}",
                            f"  Requests: {usage['total_requests']}",
                            f"  Top agents: {top_agents}",
                            f"  Top providers: {top_providers}",
                        ]
                        if headlines:
                            lines += ["", "Headlines:"]
                            for i, h in enumerate(headlines, 1):
                                lines.append(f"  {i}. {h[:80]}")
                        remaining = token_usage["balance"] - token_usage["used"]
                        lines += ["", f"Token balance: {remaining:,} remaining"]
                        await send(chat, "\n".join(lines))
                    except Exception as e:
                        await send(chat, f"Digest error: {e}")

                elif cmd == "/tokens":
                    if len(parts) < 2:
                        # Show token status
                        remaining = token_usage["balance"] - token_usage["used"]
                        lines = [
                            "FreeTokenFaucet Balance:",
                            f"  Balance: {token_usage['balance']:,} tokens",
                            f"  Used today: {token_usage['used']:,} tokens",
                            f"  Remaining: {remaining:,} tokens",
                        ]
                        if token_usage["last_claim"]:
                            lines.append(f"  Last claim: {token_usage['last_claim']}")
                        if token_usage["history"]:
                            recent = token_usage["history"][-3:]
                            lines.append("  Recent usage:")
                            for h in recent:
                                lines.append(f"    {h['model']}: {h['tokens']} tokens")
                        await send(chat, "\n".join(lines))
                    elif parts[1] == "set" and len(parts) > 2:
                        # Set balance: /tokens set 1096964
                        try:
                            new_balance = int(parts[2])
                            token_usage["balance"] = new_balance
                            token_usage["used"] = 0
                            token_usage["last_claim"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_token_usage()
                            await send(chat, f"Balance set to {new_balance:,} tokens. Usage reset.")
                        except ValueError:
                            await send(chat, "Usage: /tokens set <amount>")
                    elif parts[1] == "claim":
                        # Mark daily claim: /tokens claim 1000000
                        try:
                            claimed = int(parts[2]) if len(parts) > 2 else 1000000
                            token_usage["balance"] = claimed
                            token_usage["used"] = 0
                            token_usage["last_claim"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_token_usage()
                            await send(chat, f"Daily claim recorded: {claimed:,} tokens. Usage reset.")
                        except ValueError:
                            await send(chat, "Usage: /tokens claim <amount>")
                    elif parts[1] == "reset":
                        token_usage["used"] = 0
                        save_token_usage()
                        await send(chat, "Usage counter reset.")
                    else:
                        await send(chat, "Usage: /tokens [set <amount>|claim <amount>|reset]")

                elif cmd == "/data":
                    if len(parts) < 3:
                        await send(chat, "Usage: /data query <natural language question about loaded spreadsheets>\n       /data list — list loaded data files")
                        continue
                    sub = parts[1].lower()
                    if sub == "list":
                        docs = bf.doc_db.list()
                        spreadsheet_docs = [d for d in docs if any(d.endswith(e) for e in (".csv", ".xlsx", ".xls"))]
                        if spreadsheet_docs:
                            await send(chat, "Loaded spreadsheets:\n" + "\n".join(f"  {d}" for d in spreadsheet_docs))
                        else:
                            await send(chat, "No spreadsheets loaded. Send a CSV or XLSX file.")
                    elif sub == "query":
                        q = " ".join(parts[2:])
                        context = bf.doc_db.query(q)
                        if not context:
                            await send(chat, "No data found. Load a spreadsheet first.")
                            continue
                        ctx_text = "\n\n".join(context)
                        await typing(chat)
                        reply = await smart_call([
                {"role": "system", "content": "Answer based on the spreadsheet data provided. Give specific numbers and insights."},
                {"role": "user", "content": f"Data:\n{ctx_text}\n\nQuestion: {q}"},
                        ], active_provider)
                        await send(chat, reply[:3500])
                    else:
                        await send(chat, "Usage: /data query <question>  or  /data list")

                elif cmd == "/plugin":
                    if not is_experimental_enabled("plugin-system"):
                        await send(chat, "Plugin system is not enabled. Use /experimental enable plugin-system")
                        continue
                    if len(parts) < 2:
                        plugins = bf.list_plugins()
                        if plugins:
                            await send(chat, "Loaded plugins:\n" + "\n".join(f"  {name}: {', '.join(cmds)}" for name, cmds in plugins))
                        else:
                            await send(chat, "No plugins loaded.\nUsage: /plugin load <url_or_path>\n       /plugin list")
                        continue
                    sub = parts[1].lower()
                    if sub == "load" and len(parts) >= 3:
                        if not is_owner:
                            await send(chat, "Only the owner can load plugins.")
                            continue
                        url_or_path = " ".join(parts[2:])
                        await typing(chat)
                        result = await bf.load_plugin(url_or_path)
                        await send(chat, result[:2000])
                    elif sub == "list":
                        plugins = bf.list_plugins()
                        if plugins:
                            await send(chat, "Loaded plugins:\n" + "\n".join(f"  {name}: {', '.join(cmds)}" for name, cmds in plugins))
                        else:
                            await send(chat, "No plugins loaded.")
                    else:
                        await send(chat, "Usage: /plugin load <url_or_path>  or  /plugin list")

                elif cmd == "/bridge":
                    if not is_experimental_enabled("bot-bridge"):
                        await send(chat, "Bot Bridge is not enabled. Use /experimental enable bot-bridge")
                        continue
                    if len(parts) < 2:
                        if not bridges:
                            await send(chat, "No bridges configured.\nUsage:\n  /bridge list\n  /bridge add <name> <platform> <webhook_url|bot_token> [chat_id]\n  /bridge remove <name>\n  /bridge toggle <name>\n  /bridge send <name> <message>\n  /bridge webhook <name> <url>\n  /bridge auto-reply <name> on|off\n  /bridge prompt <name> <system_prompt>")
                        else:
                            lines = ["Configured bridges:"]
                            for name, cfg in bridges.items():
                                status = "ON" if cfg.get("enabled") else "OFF"
                                targets = cfg.get("targets", [])
                                platforms = ", ".join(t.get("platform", "?") for t in targets)
                                ar = " AR" if cfg.get("auto_reply") else ""
                                lines.append(f"  {name} ({status}){ar} -> {platforms}")
                            await send(chat, "\n".join(lines))
                        continue
                    sub = parts[1].lower()
                    if sub == "list":
                        if not bridges:
                            await send(chat, "No bridges configured.")
                        else:
                            lines = ["Bridges:"]
                            for name, cfg in bridges.items():
                                status = "ON" if cfg.get("enabled") else "OFF"
                                targets = cfg.get("targets", [])
                                ar = " auto-reply" if cfg.get("auto_reply") else ""
                                for t in targets:
                                    plat = t.get("platform", "?")
                                    url = t.get("webhook_url", t.get("bot_token", ""))[:40]
                                    lines.append(f"  {name} [{status}]{ar} {plat} -> {url}...")
                            await send(chat, "\n".join(lines))
                    elif sub == "add" and len(parts) >= 4:
                        if not is_owner:
                            await send(chat, "Only the owner can add bridges.")
                            continue
                        bname = parts[2]
                        platform = parts[3].lower()
                        if platform not in ("telegram", "discord", "slack", "bot"):
                            await send(chat, "Platform must be 'telegram', 'discord', 'slack', or 'bot'.")
                            continue
                        rest = " ".join(parts[4:])
                        if platform == "telegram":
                            args = rest.split(None, 1)
                            token = args[0] if args else ""
                            chat_id = args[1] if len(args) > 1 else ""
                            if not token or not chat_id:
                                await send(chat, "Usage: /bridge add <name> telegram <bot_token> <chat_id>")
                                continue
                            target = {"platform": "telegram", "bot_token": token, "chat_id": chat_id}
                        elif platform == "bot":
                            target = {"platform": "bot", "webhook_url": rest}
                            bridges.setdefault(bname, {}).setdefault("targets", [])
                            bridges[bname]["sender_name"] = "opencode-bot"
                        else:
                            webhook_url = rest
                            if not webhook_url.lower().startswith(("http://", "https://")):
                                await send(chat, "Webhook URL must start with http:// or https://")
                                continue
                            target = {"platform": platform, "webhook_url": webhook_url}
                        bridges.setdefault(bname, {"enabled": True, "targets": []})
                        bridges[bname]["targets"].append(target)
                        save_bridges()
                        await send(chat, f"Bridge '{bname}' added ({platform}). Use /bridge toggle {bname} to enable/disable.")
                    elif sub == "remove" and len(parts) >= 3:
                        if not is_owner:
                            await send(chat, "Only the owner can remove bridges.")
                            continue
                        bname = parts[2]
                        if bname in bridges:
                            del bridges[bname]
                            save_bridges()
                            await send(chat, f"Bridge '{bname}' removed.")
                        else:
                            await send(chat, f"Bridge '{bname}' not found.")
                    elif sub == "toggle" and len(parts) >= 3:
                        if not is_owner:
                            await send(chat, "Only the owner can toggle bridges.")
                            continue
                        bname = parts[2]
                        if bname in bridges:
                            bridges[bname]["enabled"] = not bridges[bname].get("enabled", True)
                            save_bridges()
                            s = "enabled" if bridges[bname]["enabled"] else "disabled"
                            await send(chat, f"Bridge '{bname}' {s}.")
                        else:
                            await send(chat, f"Bridge '{bname}' not found.")
                    elif sub == "send" and len(parts) >= 4:
                        bname = parts[2]
                        msg_text = " ".join(parts[3:])
                        if bname not in bridges:
                            await send(chat, f"Bridge '{bname}' not found.")
                            continue
                        cfg = bridges[bname]
                        relayed = False
                        for t in cfg.get("targets", []):
                            if t.get("platform") == "telegram":
                                token = t.get("bot_token")
                                target_chat = t.get("chat_id")
                                if token and target_chat:
                                    try:
                                        c = await get_http()
                                        await c.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": target_chat, "text": msg_text[:3000]}, timeout=10)
                                        relayed = True
                                    except:
                                        pass
                            elif t.get("platform") == "bot":
                                url = t.get("webhook_url")
                                if url:
                                    try:
                                        c = await get_http()
                                        sender_name = cfg.get("sender_name", "opencode-bot")
                                        payload = {"text": msg_text[:2000], "sender": sender_name, "from": "opencode-bot"}
                                        await c.post(url, json=payload, timeout=15)
                                        relayed = True
                                    except:
                                        pass
                            elif t.get("platform") in ("discord", "slack"):
                                url = t.get("webhook_url")
                                if url:
                                    try:
                                        c = await get_http()
                                        payload = {"content": msg_text[:2000]}
                                        if t.get("platform") == "slack":
                                            payload = {"text": msg_text[:2000]}
                                        await c.post(url, json=payload, timeout=10)
                                        relayed = True
                                    except:
                                        pass
                        if relayed:
                            await send(chat, f"Message sent via bridge '{bname}'.")
                        else:
                            await send(chat, f"Could not relay. Check bridge '{bname}' targets.")
                    elif sub == "webhook" and len(parts) >= 4:
                        if not is_owner:
                            await send(chat, "Only the owner can set webhooks.")
                            continue
                        bname = parts[2]
                        webhook_url = parts[3]
                        if bname not in bridges:
                            await send(chat, f"Bridge '{bname}' not found. Create it first with /bridge add")
                            continue
                        if not webhook_url.lower().startswith(("http://", "https://")):
                            await send(chat, "Webhook URL must start with http:// or https://")
                            continue
                        bridges[bname].setdefault("targets", [])
                        bridges[bname]["targets"].append({"platform": "bot", "webhook_url": webhook_url, "expect_reply": True})
                        bridges[bname]["my_webhook_url"] = webhook_url
                        save_bridges()
                        await send(chat, f"Bridge '{bname}' bot-to-bot webhook set. Other bots can POST to {webhook_url}")
                    elif sub == "auto-reply" and len(parts) >= 4:
                        if not is_owner:
                            await send(chat, "Only the owner can configure auto-reply.")
                            continue
                        bname = parts[2]
                        state = parts[3].lower()
                        if bname not in bridges:
                            await send(chat, f"Bridge '{bname}' not found.")
                            continue
                        if state == "on":
                            bridges[bname]["auto_reply"] = True
                            save_bridges()
                            await send(chat, f"Bridge '{bname}' auto-reply enabled. Incoming bot messages will be answered by AI.")
                        elif state == "off":
                            bridges[bname]["auto_reply"] = False
                            save_bridges()
                            await send(chat, f"Bridge '{bname}' auto-reply disabled.")
                        else:
                            await send(chat, "Usage: /bridge auto-reply <name> on|off")
                    elif sub == "prompt" and len(parts) >= 4:
                        if not is_owner:
                            await send(chat, "Only the owner can set bridge prompts.")
                            continue
                        bname = parts[2]
                        prompt_text = " ".join(parts[3:])
                        if bname not in bridges:
                            await send(chat, f"Bridge '{bname}' not found.")
                            continue
                        bridges[bname]["system_prompt"] = prompt_text
                        save_bridges()
                        await send(chat, f"Bridge '{bname}' system prompt set.")
                    else:
                        await send(chat, "Usage: /bridge list | add | remove | toggle | send <name> <msg> | webhook <name> <url> | auto-reply <name> on|off | prompt <name> <text>")

                elif cmd == "/version":
                    ver_info = load_version()
                    ver = ver_info.get("version", "unknown")
                    updated = ver_info.get("updated", "unknown")
                    wn = ver_info.get("whats_new", {})
                    lines = [f"OpenCode Bot v{ver}", f"Updated: {updated}", "", "Changelog:"]
                    for v in sorted(wn.keys(), reverse=True):
                        lines.append(f"  v{v}:")
                        for c in wn[v]:
                            lines.append(f"    \u2022 {c}")
                    await send(chat, "\n".join(lines))

                elif cmd == "/update":
                    ver_info = load_version()
                    ver = ver_info.get("version", "unknown")
                    updated = ver_info.get("updated", "unknown")
                    changes = ver_info.get("whats_new", {}).get(ver, [])
                    t = "big" if len(changes) >= 5 else ("mini" if len(changes) >= 2 else "patch")
                    lines = [f"OpenCode Bot v{ver} ({updated})", ""]
                    if changes:
                        lines.append(f"{'🚀 BIG' if t == 'big' else '🟢 Mini' if t == 'mini' else '✨ Patch'} update:")
                        for c in changes:
                            lines.append(f"  \u2022 {c}")
                    lines.append("")
                    lines.append("/version for full changelog")
                    await send(chat, "\n".join(lines))

                elif cmd == "/stack":
                    if stack_ref is None:
                        await send(chat, "AI Stack Reference module not loaded.")
                        continue
                    arg = parts[1].lower() if len(parts) > 1 else "0"
                    # Handle page navigation: /stack 3 2 (topic 3, page 2)
                    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                    topic_aliases = {
                        "0": "0", "overview": "0", "all": "0",
                        "1": "1", "agents": "1", "agentic": "1", "langgraph": "1", "crewai": "1",
                        "2": "2", "workflows": "2", "orchestration": "2", "temporal": "2", "prefect": "2", "n8n": "2",
                        "3": "3", "memory": "3", "context": "3", "mem0": "3", "graphiti": "3", "letta": "3",
                        "4": "4", "multimodal": "4", "media": "4", "image": "4", "video": "4", "flux": "4",
                        "5": "5", "serving": "5", "infra": "5", "vllm": "5", "ollama": "5", "llamacpp": "5",
                        "6": "6", "mcp": "6", "protocol": "6", "fastmcp": "6",
                        "7": "7", "observability": "7", "monitoring": "7", "langfuse": "7", "deepeval": "7",
                        "8": "8", "security": "8", "guardrails": "8", "nemo": "8", "owasp": "8",
                        "9": "9", "hitl": "9", "approval": "9", "human": "9", "interrupt": "9",
                        "10": "10", "edge": "10", "local": "10", "llamacpp": "10", "mlx": "10", "termux": "10",
                    }
                    lookup = topic_aliases.get(arg, arg)
                    if lookup == "0" and arg != "0":
                        # Try fuzzy match
                        sec = stack_ref.get_section(arg)
                    else:
                        sec = stack_ref.get_section(lookup)
                    if sec is None:
                        await send(chat, stack_ref.list_topics())
                    else:
                        text = stack_ref.format_section(sec, page)
                        await send(chat, text)
                        if len(sec["body"]) > 3800:
                            await send(chat, f"More pages available. Use: /stack {arg} {page+1}")

                elif cmd == "/stackstatus":
                    if ai_stack is None:
                        await send(chat, "AI Stack Combined module not loaded.")
                        continue
                    try:
                        tracer = ai_stack.Tracer()
                        llm = ai_stack.LLMRouter()
                        memory = ai_stack.MemoryStore()
                        guardrails = ai_stack.Guardrails()
                        edge = ai_stack.EdgeManager()
                        mcp = ai_stack.MCPServer("ai-stack")
                        hitl = ai_stack.HITLManager()

                        lines = [
                            "AI Infrastructure Stack - Live Status",
                            "",
                            f"[1/Agent] Agent system: Ready",
                            f"[2/Workflow] WorkflowEngine: Ready",
                            f"[3/Memory] MemoryStore: {memory.status()}",
                            f"[4/Multimodal] ComfyUI: {ai_stack.MultimodalEngine().comfyui_url}",
                            f"[5/Serving] Providers: {llm.status()}",
                            f"[6/MCP] Tools: {len(mcp.list_tools())} registered",
                            f"[7/Observability] Tracer: {tracer.summary()}",
                            f"[8/Security] Guardrails: {guardrails.scan('test').status}",
                            f"[9/HITL] {hitl.status()}",
                            f"[10/Edge] {edge.status()}",
                        ]
                        await send(chat, "\n".join(lines))
                    except Exception as e:
                        await send(chat, f"Stack status error: {e}")

                elif cmd == "/webgateway":
                    gw_port = int(os.environ.get("WEB_GATEWAY_PORT", "4357"))
                    lines = [f"Web AI Gateway: http://localhost:{gw_port}", f"Admin Dashboard: http://localhost:{gw_port}/admin"]
                    try:
                        if aiohttp:
                            async with aiohttp.ClientSession() as s:
                                r = await s.get(f"http://127.0.0.1:{gw_port}/api/providers", timeout=5)
                                if r.status == 200:
                                    lines.append(f"Status: Running on port {gw_port}")
                                    lines.append(f"Web UI: http://localhost:{gw_port}")
                                    lines.append(f"API: POST http://localhost:{gw_port}/v1/chat/completions")
                                    lines.append(f"Models: GET http://localhost:{gw_port}/api/models")
                        else:
                            c = await get_http()
                            r = await c.get(f"http://127.0.0.1:{gw_port}/api/providers", timeout=5)
                            if r.status_code == 200:
                                lines.append(f"Status: Running on port {gw_port}")
                                lines.append(f"Web UI: http://localhost:{gw_port}")
                                lines.append(f"API: POST http://localhost:{gw_port}/v1/chat/completions")
                                lines.append(f"Models: GET http://localhost:{gw_port}/api/models")
                    except Exception:
                        lines.append("Status: Not running (start separately: python web_gateway.py)")
                    await send(chat, "\n".join(lines))

                elif cmd == "/cmd" and is_experimental_enabled("custom-commands"):
                    sub = parts[1].lower() if len(parts) > 1 else "list"
                    uid_str = str(uid)
                    user_cmds = custom_commands.setdefault(uid_str, {})
                    if sub == "list":
                        if not user_cmds:
                            await send(chat, "No custom commands. Create one with:\n/cmd add <name> <response>")
                        else:
                            lines = [f"Your custom commands ({len(user_cmds)}):"]
                            for cname, cresp in sorted(user_cmds.items()):
                                lines.append(f"  /{cname} — {cresp[:60]}{'…' if len(cresp) > 60 else ''}")
                            await send(chat, "\n".join(lines))
                    elif sub == "add" and len(parts) > 3:
                        cname = parts[2].lower().replace("/", "")
                        if not cname.isalnum() and not cname.replace("_", "").isalnum():
                            await send(chat, "Command name must be alphanumeric.")
                            continue
                        if cname in ("start", "help", "cmd", "experimental", "admin", "version"):
                            await send(chat, "Cannot override built-in commands.")
                            continue
                        cresp = " ".join(parts[3:])
                        user_cmds[cname] = cresp
                        save_custom_commands()
                        await send(chat, f"✅ Created /{cname}")
                    elif sub == "remove" and len(parts) > 2:
                        cname = parts[2].lower().replace("/", "")
                        if cname in user_cmds:
                            del user_cmds[cname]
                            save_custom_commands()
                            await send(chat, f"Removed /{cname}")
                        else:
                            await send(chat, f"No custom command /{cname}")
                    else:
                        await send(chat, "Usage:\n  /cmd list — List your commands\n  /cmd add <name> <response> — Create a command\n  /cmd remove <name> — Delete a command")

                elif cmd.startswith("/") and cmd[1:] in custom_commands.get(str(uid), {}) and is_experimental_enabled("custom-commands"):
                    user_cmds = custom_commands.get(str(uid), {})
                    reply = user_cmds.get(cmd[1:], "")
                    await send(chat, reply)

                elif cmd == "/tags" and is_experimental_enabled("auto-tagging"):
                    chat_tags = conversation_tags.get(str(chat), {})
                    if not chat_tags:
                        await send(chat, "No tags for this chat yet. Start chatting to auto-generate tags!")
                    else:
                        sorted_tags = sorted(chat_tags.items(), key=lambda x: -x[1])
                        lines = [f"Tags for this chat ({sum(chat_tags.values())} total):"]
                        for t, c in sorted_tags:
                            lines.append(f"  #{t} — {c}x")
                        await send(chat, "\n".join(lines))

                elif cmd == "/find" and is_experimental_enabled("enhanced-search"):
                    if len(parts) < 2:
                        await send(chat, "Usage: /find <tag>\nExample: /find python")
                        continue
                    query = parts[1].lower()
                    results = []
                    for cid, tags in conversation_tags.items():
                        for tag, count in tags.items():
                            if query in tag:
                                results.append((cid, tag, count))
                                break
                    if not results:
                        await send(chat, f"No chats found with tag matching '{query}'")
                    else:
                        results.sort(key=lambda x: -x[2])
                        lines = [f"Chats matching '{query}':"]
                        for cid, tag, count in results[:10]:
                            lines.append(f"  Chat {cid} — #{tag} ({count}x)")
                        await send(chat, "\n".join(lines))

                elif cmd.startswith("/") and cmd not in ("/start", "/version", "/help", "/agents", "/agent", "/repo", "/status", "/clear", "/myrole", "/checkrole", "/profile", "/addadmin", "/removeadmin", "/adminlist", "/addmod", "/removemod", "/modlist", "/addprovider", "/reset", "/providers", "/agentprovider", "/createagent", "/premadeskills", "/addprompt", "/arch", "/mode", "/tools", "/teams", "/putteam", "/createteam", "/useteam", "/stopteam", "/routes", "/gateway", "/repair", "/pyrit", "/toolfk", "/synoxcloud", "/webgateway", "/effort", "/thinking", "/low", "/normal", "/medium", "/high", "/superhigh", "/vision", "/draw", "/schedule", "/export", "/doc", "/ask", "/context", "/search", "/youtube", "/youtube_search", "/tiktok", "/github_search", "/analyze", "/run", "/fetch", "/remind", "/digest", "/routine", "/multi", "/translate", "/qr", "/stats", "/data", "/plugin", "/n8n", "/n8n-status", "/n8n-logs", "/github", "/gmail", "/sheets", "/notion", "/crypto", "/stack", "/stackstatus", "/remember", "/recall", "/tokens", "/weather", "/backup", "/restore", "/dailydigest", "/experimental", "/update", "/skills", "/pocket-tts", "/video-analyze", "/prompt-analyze", "/kgraph", "/history", "/view", "/change", "/resume", "/archive", "/video", "/cmd", "/tags", "/find", "/bridge", "/reddit", "/hn", "/social", "/memory", "/cron", "/monitor", "/announcementoff", "/announcementon", "/announce", "/rich", "/richv2", "/cyberdeck", "/iot", "/edu", "/fin", "/cv", "/style", "/pollplus", "/content", "/analytics", "/sub", "/safety", "/dev", "/aiint", "/community", "/automate", "/secapi", "/languages", "/ocr", "/loc", "/miniapp", "/backup-keys", "/market", "/voice", "/auto", "/guard", "/kg", "/vault", "/watch-video"):
                    if not is_owner and not is_admin:
                        await send(chat, "Unknown command.")
                    else:
                        await send(chat, f"Unknown command or insufficient permissions.")

                else:
                    chat_multi = multi_sessions.get(str(chat), {})
                    if chat_multi and chat_multi.get("active"):
                        await typing(chat)
                        providers = chat_multi["providers"]
                        rounds = chat_multi["rounds"]
                        history = chat_multi.setdefault("history", [])
                        history.append({"role": "user", "content": text, "provider": None})

                        async def call_one(provider):
                            ctx = [{"role": "system", "content": "You are a helpful AI assistant. Respond to the user and engage with other AIs in a multi-AI discussion."}]
                            ctx += [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
                            try:
                                r = await call_provider(ctx, provider)
                                return provider, r
                            except Exception as e:
                                return provider, f"<Error: {e}>"

                        all_responses = {}
                        tasks = [call_one(p) for p in providers]
                        results = await asyncio.gather(*tasks)
                        output = [f"Round 1/{rounds}:"]
                        for p, r in results:
                            all_responses[p] = r
                            history.append({"role": "assistant", "content": r, "provider": p})
                            output.append(f"[{p}]: {r}")

                        for rnd in range(1, rounds):
                            output.append(f"\nRound {rnd+1}/{rounds}:")
                            async def debate_one(provider):
                                other = [f"[{k}]: {v}" for k, v in all_responses.items() if k != provider]
                                prompt = f"The user said: {text}\n\nOther AI responses:\n" + "\n".join(other)
                                prompt += "\n\nReact to what the other AI said. You can agree, disagree, add insight, or challenge. Keep it concise."
                                ctx = [{"role": "system", "content": "You are in a multi-AI discussion. React to other AIs' responses."}, {"role": "user", "content": prompt}]
                                try:
                                    r = await call_provider(ctx, provider)
                                    return provider, r
                                except Exception as e:
                                    return provider, f"<Error: {e}>"
                            tasks_debate = [debate_one(p) for p in providers]
                            debate_results = await asyncio.gather(*tasks_debate)
                            all_responses = {}
                            for p, r in debate_results:
                                all_responses[p] = r
                                history.append({"role": "assistant", "content": r, "provider": p})
                                output.append(f"[{p}]: {r}")

                        save_multi()
                        await send(chat, "\n\n".join(output))
                        _safe_track_usage(uid, "multi", "+".join(providers))
                        continue

                    await typing(chat)
                    try:
                        if active_mode == "autonomous":
                            memory_buffers.setdefault(uid, [])
                            memory_buffers.append(uid, f"[USER] {text}")
                            reply = await run_autonomous(text, uid)
                            _safe_track_usage(uid, active_agent, active_provider)
                            await send(chat, reply)
                            continue
                        elif active_team and active_team in TEAMS and active_arch != "single":
                            team = TEAMS[active_team]
                            team_sessions.setdefault(uid, [])
                            team_sessions[uid].append({"role": "user", "content": text})
                            ctx = team_sessions[uid][-10:]
                            combined = "\n".join(m["content"] for m in ctx if m["role"] == "user")
                            msg_log_key = f"_msg_log_{uid}"
                            msg_log = memory_buffers.get(msg_log_key, [])
                            reply = await run_architecture(active_arch, team["agents"], combined, active_provider, uid=uid, msg_log=msg_log)
                            memory_buffers[msg_log_key] = msg_log
                            team_sessions[uid].append({"role": "assistant", "content": reply})
                            save_sessions()
                            _safe_track_usage(uid, active_agent, active_provider)
                            await send(chat, reply)
                            continue
                        else:
                            _last_msg_times.setdefault(uid, 0)
                            if uid in sessions and sessions[uid] and time.time() - _last_msg_times[uid] > 1800:
                                _archive_current(uid, chat)
                                sessions[uid] = []
                            sessions.setdefault(uid, [])
                            agent_prompt = AGENTS[active_agent]["prompt"]
                            if guard_mod:
                                auto = guard_mod.get_auto()
                                acfg = auto.get(uid)
                                if acfg.get("enabled") and acfg.get("template"):
                                    agent_prompt = f"{agent_prompt}\n\n[Auto-Reply Style]\n{acfg['template']}"
                            if styles_mod and is_experimental_enabled("ai-styles"):
                                ast = styles_mod.get_ai_styles()
                                stext = ast.get_style_text(uid)
                                if stext:
                                    agent_prompt = f"{agent_prompt}\n\n[AI Style]\n{stext}"
                            if not sessions[uid]:
                                try:
                                    ctx = await bf.auto_context()
                                    mem_ctx = ""
                                    try:
                                        mem_ctx = await bf.get_memory_context(uid)
                                    except:
                                        pass
                                    extra = ""
                                    if is_experimental_enabled("context-files"):
                                        chat_files = context_files.get(str(chat), [])
                                        if chat_files:
                                            file_block = "\n\n".join(f"[{f['name']}]\n{f['content']}" for f in chat_files if f.get("content"))
                                            if file_block:
                                                extra = f"\n\n[Attached Context Files]\n{file_block}"
                                    combined_ctx = f"{ctx}\n{mem_ctx}".strip()
                                    if combined_ctx or extra:
                                        sessions[uid].append({"role": "system", "content": f"{agent_prompt}\n\n[Auto-Context]\n{combined_ctx}{extra}"})
                                    else:
                                        sessions[uid].append({"role": "system", "content": agent_prompt})
                                except Exception:
                                    sessions[uid].append({"role": "system", "content": agent_prompt})
                            if len(sessions[uid]) > 30:
                                try:
                                    summarized = await bf.summarize_conversation(sessions[uid], smart_call)
                                    if summarized:
                                        sessions[uid] = summarized
                                except Exception:
                                    sessions[uid] = sessions[uid][-20:]
                            sessions[uid].append({"role": "user", "content": text})
                            if is_experimental_enabled("auto-tagging") and text:
                                tags = tag_keywords(text)
                                if tags:
                                    chat_tags = conversation_tags.setdefault(str(chat), {})
                                    for t, count in tags.items():
                                        chat_tags[t] = chat_tags.get(t, 0) + count
                                    save_conversation_tags()
                            _bridge = asyncio.create_task(relay_to_bridge(text, chat, uid, msg))
                            _bridge.add_done_callback(_task_done)
                            try:
                                await bf.append_to_memory_log(uid, "user", text)
                            except:
                                pass
                            log(f"Calling {active_provider} for: {text[:50]}")
                            try:
                                reply = await asyncio.wait_for(smart_call(sessions[uid][-20:], active_provider), timeout=60)
                            except asyncio.TimeoutError:
                                reply = f"All providers timed out. Try /repo to switch provider."
                                log(f"smart_call timed out for {active_provider}")
                            except Exception as _e:
                                reply = f"Provider error: {_e}"
                                log(f"smart_call exception: {_e}")
                            if not reply:
                                reply = "Empty response from provider. Try /repo to switch."
                            log(f"Reply: {str(reply)[:80]}...")
                            sessions[uid].append({"role": "assistant", "content": reply})
                            try:
                                await bf.append_to_memory_log(uid, "assistant", reply[:2000])
                            except:
                                pass
                            save_sessions()
                            _safe_track_usage(uid, active_agent, active_provider)
                            await send(chat, reply)
                    except Exception as e:
                        log(f"Chat error: {e}")
                        await send(chat, f"Error: {e}")
        except Exception as e:
            log(f"Poll error: {e}")
            print(f"Poll error: {e}")
            await asyncio.sleep(1)

    log("Saving state before shutdown...")
    save_sessions()
    save_memory()
    save_token_usage()
    save_routines()
    log("State saved. Goodbye.")
    if LOG:
        try:
            LOG.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        if sys.platform == "win32" and sys.version_info < (3, 14):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except BaseException as _be:
        _em = f"FATAL: {type(_be).__name__}: {_be}"
        print(_em, flush=True)
        try:
            with open("bot_crash.txt", "w", encoding="utf-8") as _cf:
                _cf.write(f"main crash:\n{_tb.format_exc()}")
        except Exception:
            pass
        try:
            _bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            _owner_id = os.environ.get("OWNER_ID", "")
            if _bot_token and _owner_id:
                import urllib.request as _ur
                _trace = _tb.format_exc()[-500:]
                _data = json.dumps({
                    "chat_id": _owner_id,
                    "text": f"<b>Bot Offline!</b>\n\n<b>Error:</b> {_em[:200]}\n\n<b>Trace:</b>\n<pre>{_trace}</pre>",
                    "parse_mode": "HTML"
                }).encode("utf-8")
                _req = _ur.Request(
                    f"https://api.telegram.org/bot{_bot_token}/sendMessage",
                    data=_data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                _ur.urlopen(_req, timeout=10)
        except Exception:
            pass
    finally:
        try:
            if os.path.exists(_LOCK_FILE):
                with open(_LOCK_FILE, encoding="utf-8") as _f:
                    if _f.read().strip() == str(os.getpid()):
                        os.remove(_LOCK_FILE)
        except Exception:
            pass
