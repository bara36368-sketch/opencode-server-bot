import sys, os, traceback as _tb, io as _io
from datetime import datetime

_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot.lock")
def _check_single_instance():
    try:
        if os.path.exists(_LOCK_FILE):
            with open(_LOCK_FILE) as _f:
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
                        _ = open(f"/proc/{_old_pid}/status")
                        _.close()
                        _alive = True
                    except:
                        pass
                except:
                    pass
            if _alive:
                sys.exit(0)
    except: pass
    try:
        with open(_LOCK_FILE, "w") as _f:
            _f.write(str(os.getpid()))
    except: pass
_check_single_instance()

try:
    _dbg = open("bot_startup.txt", "w")
    _dbg.write("1\n")
    _dbg.close()
except:
    pass

_M = object()
asyncio=_M; httpx=_M; json=_M; uuid=_M; time=_M; copy=_M; re=_M; random=_M; urllib=_M
try:
    import asyncio, json, uuid, time, copy, re, random, urllib.parse
except Exception:
    try:
        with open("bot_crash.txt", "w") as _f:
            _f.write(f"stdlib import failed:\n{_tb.format_exc()}")
    except:
        pass
    raise
try:
    import httpx
except Exception:
    try:
        with open("bot_crash.txt", "w") as _f:
            _f.write(f"httpx import failed (non-fatal):\n{_tb.format_exc()}")
    except:
        pass

try:
    import pyrit_attacks
except Exception:
    try:
        with open("bot_crash.txt", "w") as _f:
            _f.write(f"pyrit import failed:\n{_tb.format_exc()}")
    except:
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
        return _a if name.startswith(("run_", "voice_", "text_to_", "vision_", "image_", "translate", "web_search", "youtube_", "run_code", "fetch_url", "qr_", "auto_context", "summarize_", "get_photo_url", "extract_", "parse_spread")) else _s

try:
    import bot_features as bf
    _ = bf  # verify it actually loaded
except Exception as _bf_err:
    try:
        with open("bot_crash.txt", "w") as _f:
            _f.write(f"bot_features import failed: {_bf_err}\n{_tb.format_exc()}")
    except:
        pass
    bf = _BfStub()

try:
    import ai_stack_reference as stack_ref
except Exception:
    stack_ref = None

try:
    import ai_stack_combined as ai_stack
except Exception:
    ai_stack = None

try:
    import aiohttp
except Exception:
    aiohttp = None

def _safe_track_usage(uid, agent, provider):
    global bf
    if bf:
        try:
            bf.track_usage(uid, agent, provider)
        except:
            pass

try:
    _dbg2 = open("bot_startup.txt", "a")
    _dbg2.write("2\n")
    _dbg2.close()
except:
    pass

_http = None
_save_counter = 0

async def get_http():
    global _http
    if httpx is _M or not hasattr(httpx, "AsyncClient"):
        raise RuntimeError("httpx is not installed. Install with: pip install httpx")
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(timeout=120, limits=httpx.Limits(max_keepalive_connections=10, max_connections=20))
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
except:
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
    async def execute(self, messages, preferred):
        chain = self.fallback_chain(preferred)
        t0 = time.time()
        errors = []
        for provider in chain:
            t1 = time.time()
            try:
                result = await asyncio.wait_for(call_provider(messages, provider), timeout=25)
                elapsed = time.time() - t1
                if "error" in result.lower()[:20]:
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
        wait = self.next_available()
        retry_in = max(wait, 5) if wait > 0 else 10
        if retry_in < 60:
            log(f"gateway: all failed, retrying in {retry_in:.0f}s")
            await asyncio.sleep(retry_in)
            return await self.execute(messages, preferred)
        return f"All providers failed.\n" + "\n".join(errors) + f"\nNext available in {wait:.0f}s."
    def get_route_health(self):
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

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
TG_API = f"https://api.telegram.org/bot{TOKEN}"

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
}

def save_agents():
    with open(AGENTS_FILE, "w") as f:
        json.dump(AGENTS, f, indent=2)

def save_providers():
    with open(PROVIDERS_FILE, "w") as f:
        json.dump(PROVIDERS, f, indent=2)

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(list(admins), f)

def save_mods():
    with open(MODS_FILE, "w") as f:
        json.dump(list(mods), f)

def save_premade():
    with open(PREMADE_SKILLS_FILE, "w") as f:
        json.dump(PREMADE_SKILLS, f, indent=2)

def save_teams():
    with open(TEAMS_FILE, "w") as f:
        json.dump(TEAMS, f, indent=2)

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
    with open(SESSIONS_FILE, "w") as f:
        json.dump(data, f)

def load_sessions():
    global last_update
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE) as f:
                data = json.load(f)
                sessions.update({int(k): v for k, v in data.get("sessions", {}).items()})
                team_sessions.update({int(k): v for k, v in data.get("team_sessions", {}).items()})
                lu = data.get("_last_update", 0)
                if lu and not last_update:
                    last_update = lu
        except: pass

routines = {}
def save_routines():
    with open(ROUTINES_FILE, "w") as f:
        json.dump(routines, f)
def load_routines():
    global routines
    if os.path.exists(ROUTINES_FILE):
        try:
            with open(ROUTINES_FILE) as f:
                routines = json.load(f)
        except:
            routines = {}

multi_sessions = {}
def save_multi():
    with open(MULTI_FILE, "w") as f:
        json.dump(multi_sessions, f)
def load_multi():
    global multi_sessions
    if os.path.exists(MULTI_FILE):
        try:
            with open(MULTI_FILE) as f:
                multi_sessions = json.load(f)
        except:
            multi_sessions = {}

ARCHITECTURES = {
    "single": {"desc": "Single agent mode (default, no team coordination)"},
    "sequential": {"desc": "Agents run one after another, each gets previous output"},
    "parallel": {"desc": "All agents run simultaneously, orchestrator merges results"},
    "hierarchical": {"desc": "Orchestrator delegates to sub-agents, collects reports"},
    "mesh": {"desc": "All agents collaborate freely with shared context"},
    "voting": {"desc": "Each agent answers independently, best answer selected"},
}

MODES = {
    "chat": {"desc": "Single agent chat, no planning"},
    "team": {"desc": "Multi-agent team with architecture patterns"},
    "autonomous": {"desc": "Autonomous agent with planner, executor, tools, and memory"},
}

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_usage.json")
EXPERIMENTAL_FILE = os.path.join(os.path.dirname(__file__), "experimental.json")
vector_memory = {}
memory_buffers = {}

PROCESSES = {
    "bot": ["python", "opencode_bot.py"],
    "web": ["python", "web_gateway.py"],
    "stack": ["python", "ai_stack_combined.py"],
}

# Persistent memory store (from ai_stack_combined)
try:
    user_memory = ai_stack.MemoryStore() if ai_stack else None
except:
    user_memory = None

def save_memory():
    data = {"vector": vector_memory, "buffers": {str(k): v for k, v in memory_buffers.items()}}
    # Save MemoryStore if available
    if user_memory:
        data["memories"] = [{"id": m.id, "content": m.content, "user_id": m.user_id, "metadata": m.metadata} for m in user_memory.memories]
        data["blocks"] = {k: v.value for k, v in user_memory.blocks.items()}
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def load_memory():
    global vector_memory, memory_buffers
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE) as f:
                data = json.load(f)
                vector_memory.update(data.get("vector", {}))
                memory_buffers.update({int(k): v for k, v in data.get("buffers", {}).items()})
                # Load MemoryStore if available
                if user_memory:
                    for m in data.get("memories", []):
                        user_memory.add(m["content"], m.get("user_id", "default"), **m.get("metadata", {}))
                    for k, v in data.get("blocks", {}).items():
                        user_memory.set_block(k, v)
        except: pass

# Token usage tracking for FreeTokenFaucet
token_usage = {"balance": 1096964, "used": 0, "last_claim": "", "history": []}

def load_token_usage():
    global token_usage
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                token_usage.update(json.load(f))
        except: pass

def save_token_usage():
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_usage, f, indent=2)

experimental_features = {}
def load_experimental():
    global experimental_features
    if os.path.exists(EXPERIMENTAL_FILE):
        try:
            with open(EXPERIMENTAL_FILE) as f:
                data = json.load(f)
                experimental_features = data.get("features", {})
        except:
            experimental_features = {}

def save_experimental():
    with open(EXPERIMENTAL_FILE, "w") as f:
        json.dump({"features": experimental_features}, f, indent=2)

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

def track_tokens(model, tokens_used):
    token_usage["used"] += tokens_used
    token_usage["history"].append({
        "time": datetime.now().isoformat(),
        "model": model,
        "tokens": tokens_used
    })
    if len(token_usage["history"]) > 100:
        token_usage["history"] = token_usage["history"][-100:]
    save_token_usage()

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
}

async def execute_tool(name, args):
    c = await get_http()
    if name == "web-scrape":
        url = args.get("url", "")
        r = await c.get(url, timeout=30)
        text = r.text[:5000]
        return f"Content from {url}:\n{text[:2000]}"
    if name == "web-search":
        q = args.get("query", "")
        r = await c.get(f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1", timeout=15)
        data = r.json()
        return f"Results for '{q}': {str(data.get('AbstractText', 'No results'))[:2000]}"
    if name == "python-exec":
        code = args.get("code", "")
        try:
            local_vars = {}
            exec(code, {}, local_vars)
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
            url = f"https://api.synoxcloud.xyz{ep_path}"
            for k, v in tool_params.items():
                url += f"&{k}={v}" if "?" in url else f"?{k}={v}"
            c = await get_http()
            r = await c.get(url, timeout=30)
            text = r.text[:5000]
            return f"[synoxcloud/{endpoint}] Result:\n{text[:2000]}"
        except Exception as e:
            return f"[synoxcloud/{endpoint}] Error: {e}"
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
            with open("checkpoints.json") as f: all_ckpts = json.load(f)
        except: pass
    all_ckpts.setdefault(str(uid), []).append(cp)
    if len(all_ckpts[str(uid)]) > 20: all_ckpts[str(uid)] = all_ckpts[str(uid)][-20:]
    with open("checkpoints.json", "w") as f: json.dump(all_ckpts, f)

async def run_architecture(arch, agents_in_team, user_text, provider, uid=None, msg_log=None):
    if msg_log is None: msg_log = []

    if arch == "single":
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
    except:
        return f"Planner JSON parse error. Raw:\n{raw[:300]}"

    log(f"Autonomous plan ({len(steps)} steps) for uid {uid}")

    results = []
    for i, step in enumerate(steps):
        step_type = step.get("type", "reason")
        task = step.get("task", f"Step {i+1}")
        memory_buffers[uid].append(f"[PLAN] Step {i+1}: {task}")

        if step_type == "tool":
            tool_name = step.get("tool")
            tool_input = step.get("input", {})
            tool_result = await execute_tool(tool_name, tool_input)
            results.append(f"Step {i+1} ({tool_name}): {tool_result[:500]}")
            memory_buffers[uid].append(f"[TOOL] {tool_name}: {tool_result[:200]}")
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
            memory_buffers[uid].append(f"[REASON] Step {i+1}: {reason_result[:200]}")

        if uid: await save_checkpoint(uid, f"auto_step_{i+1}", {"step": step, "result": results[-1]})

    synthesis_prompt = (
        f"Synthesize the final answer for this goal based on all step results.\n"
        f"Goal: {goal}\n\nResults:\n" + "\n".join(results)
    )
    final = await smart_call([{"role": "user", "content": synthesis_prompt}], active_provider)
    memory_buffers[uid].append(f"[FINAL] {final[:200]}")
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
        with open(AGENTS_FILE) as f:
            AGENTS.update(json.load(f))
    except: pass

AGENT_PROVIDERS = {}
if os.path.exists(AGENT_PROVIDERS_FILE):
    try:
        with open(AGENT_PROVIDERS_FILE) as f:
            AGENT_PROVIDERS.update(json.load(f))
    except: pass

PREMADE_SKILLS = copy.deepcopy(DEFAULT_PREMADE_SKILLS)
if os.path.exists(PREMADE_SKILLS_FILE):
    try:
        with open(PREMADE_SKILLS_FILE) as f:
            PREMADE_SKILLS.update(json.load(f))
    except: pass

TEAMS = {}
if os.path.exists(TEAMS_FILE):
    try:
        with open(TEAMS_FILE) as f:
            TEAMS.update(json.load(f))
    except: pass

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
        "model": "moonshotai/kimi-k3-free",
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
        "model": "gpt-4o-mini",
        "key": "tf_ae094ac3d7fd4a73b8d1f40bf5f2d5f4"
    },
}

if os.path.exists(PROVIDERS_FILE):
    try:
        with open(PROVIDERS_FILE) as f:
            PROVIDERS.update(json.load(f))
    except: pass

SYNOXCLOUD_ENDPOINTS = {}
SYNOXCLOUD_AI_MODELS = {}

if os.path.exists(SYNOXCLOUD_ENDPOINTS_FILE):
    try:
        with open(SYNOXCLOUD_ENDPOINTS_FILE, encoding="utf-8") as f:
            _sd = json.load(f)
        for _cat in _sd.get("endpoints", []):
            for _item in _cat.get("items", []):
                SYNOXCLOUD_ENDPOINTS[_item["id"]] = _item["path"]
    except: pass

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
    except: pass

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
admins = {OWNER_ID}
if os.path.exists(ADMINS_FILE):
    try:
        with open(ADMINS_FILE) as f:
            admins.update(json.load(f))
    except: pass
mods = set()
if os.path.exists(MODS_FILE):
    try:
        with open(MODS_FILE) as f:
            mods.update(json.load(f))
    except: pass
_OFFSET_FILE = os.path.join(os.path.dirname(__file__), ".bot.offset")
last_update = 0
try:
    with open(_OFFSET_FILE) as _f:
        last_update = int(_f.read().strip())
except:
    pass
processed = set()
last_user_msg = {}
sessions = {}
team_sessions = {}
load_sessions()
load_memory()
load_routines()
load_multi()

async def tg(method, data=None):
    c = await get_http()
    r = await c.post(f"{TG_API}/{method}", json=data or {}, timeout=15)
    if not r.json().get("ok"):
        log(f"TG API error: {method} {r.json()}")
    return r.json()

_sent_cache = {}
async def send(chat, text):
    key = (chat, str(text)[:200])
    now = time.time()
    if key in _sent_cache and now - _sent_cache[key] < 3:
        log(f"dedup: skipped duplicate send to {chat}")
        return
    _sent_cache[key] = now
    if len(_sent_cache) > 500:
        for k in list(_sent_cache.keys()):
            if now - _sent_cache[k] > 10:
                del _sent_cache[k]
    return await tg("sendMessage", {"chat_id": chat, "text": str(text)[:4000]})

async def typing(chat):
    await tg("sendChatAction", {"chat_id": chat, "action": "typing"})

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
        r = await c.post(f"{p['url']}?key={p['key']}", json={"contents": parts})
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
            except:
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
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", str(r.json()))
        return f"{provider.title()} error: {r.status_code} - {r.text[:500]}"

def resolve_provider(agent_name=None):
    agent_name = agent_name or active_agent
    cfg = AGENT_PROVIDERS.get(agent_name)
    if cfg and _is_configured(cfg.get("key", "")):
        return cfg
    return None

def get_fallback_chain(preferred):
    return gateway.fallback_chain(preferred)

async def smart_call(messages, preferred):
    ap = resolve_provider()
    if ap:
        return await call_provider(messages, "__agent_provider__", override=ap)
    return await gateway.execute(messages, preferred)

async def poll():
    global last_update
    p = {"timeout": 15, "allowed_updates": ["message"]}
    if last_update:
        p["offset"] = last_update + 1
    for attempt in range(3):
        try:
            c = await get_http()
            r = (await c.get(f"{TG_API}/getUpdates", params=p, timeout=20)).json()
            for u in r.get("result", []):
                last_update = u["update_id"]
            try:
                with open(_OFFSET_FILE, "w") as _f:
                    _f.write(str(last_update))
            except:
                pass
            return r.get("result", [])
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
        with open(VERSION_FILE) as f:
            return json.load(f)
    except:
        return {"version": "unknown", "whats_new": {}}

def load_version_state():
    try:
        with open(VERSION_STATE_FILE) as f:
            return json.load(f)
    except:
        return {"last_version": "", "notified_chats": {}}

def save_version_state(state):
    try:
        with open(VERSION_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass

async def announce_update(old_v, new_v, changes, state):
    state["last_version"] = new_v
    known_chats = set()
    for cid in sessions:
        known_chats.add(cid)
    for cid in list(state.get("notified_chats", {}).keys()):
        known_chats.add(int(cid))
    for cid in list(multi_sessions.keys()):
        known_chats.add(int(cid))
    try:
        usage_file = os.path.join(os.path.dirname(__file__), "usage_stats.json")
        if os.path.exists(usage_file):
            with open(usage_file) as f:
                usage = json.load(f)
            for uid in usage:
                known_chats.add(int(uid))
    except:
        pass
    known_chats.discard(0)
    ver_info = load_version()
    exp_features = ver_info.get("experimental", [])
    total = len(changes) + len(exp_features)
    if total < 2:
        update_type = "patch"
    elif total <= 4:
        update_type = "mini"
    else:
        update_type = "big"
    lines = []
    if update_type == "big":
        lines.append("🚀 ==============================")
        lines.append("   BIG UPDATE INCOMING!")
        lines.append("   ==============================")
        lines.append("")
        lines.append(f"  v{old_v} → v{new_v}")
        lines.append("")
    elif update_type == "mini":
        lines.append("🟢 Mini Update!")
        lines.append(f"  v{old_v} → v{new_v}")
        lines.append("")
    else:
        lines.append(f"✨ Patch v{new_v}")
        lines.append("")
    if changes:
        if update_type == "big":
            lines.append("🆕 What's New:")
        else:
            lines.append(f"🆕 {len(changes)} New Feature{'s' if len(changes) > 1 else ''}:")
        lines.append("")
        for i, c in enumerate(changes, 1):
            lines.append(f"  {i}. {c}")
        lines.append("")
    if exp_features:
        lines.append(f"🧪 Experimental ({len(exp_features)}):")
        lines.append("")
        for i, ef in enumerate(exp_features, 1):
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
    if exp_features:
        lines.append("  /experimental — Enable new features")
    lines.append("")
    lines.append("🚀 Enjoying the bot? Share it with friends!")
    msg = "\n".join(lines)
    sent_count = 0
    for cid in known_chats:
        try:
            if str(cid) not in state.get("notified_chats", {}).get(new_v, []):
                r = await send(cid, msg)
                if r and r.get("ok"):
                    state.setdefault("notified_chats", {}).setdefault(new_v, []).append(str(cid))
                    sent_count += 1
                await asyncio.sleep(0.1)
        except:
            pass
    log(f"Update announced: v{old_v} -> v{new_v} to {sent_count} chats (type={update_type}, features={total})")
    save_version_state(state)
    return state

async def auto_version_checker():
    while True:
        await asyncio.sleep(30)
        try:
            current = load_version()
            current_ver = current.get("version", "unknown")
            state = load_version_state()
            last_ver = state.get("last_version", "")
            if last_ver and current_ver != last_ver:
                changes = current.get("whats_new", {}).get(current_ver, [])
                log(f"Auto-check: version changed {last_ver} -> {current_ver}")
                await announce_update(last_ver, current_ver, changes, state)
        except Exception as e:
            log(f"Auto version check error: {e}")

async def main():
    global active_agent, active_provider, active_mode, active_arch, active_team, effort, thinking_mode, bf
    log("Bot started")

    version_info = load_version()
    ver = version_info.get("version", "unknown")
    state = load_version_state()
    old_ver = state.get("last_version", "")
    if old_ver and old_ver != ver:
        changes = version_info.get("whats_new", {}).get(ver, [])
        log(f"Version changed: {old_ver} -> {ver}")
        state = await announce_update(old_ver, ver, changes, state)
    else:
        state["last_version"] = ver
        save_version_state(state)
    log(f"OpenCode Bot v{ver} started")

    await gateway.start_worker()
    if bf:
        asyncio.create_task(bf.run_scheduler_loop(smart_call, send))
        asyncio.create_task(bf.run_reminder_loop(send))
        bf.init_plugins()
    asyncio.create_task(auto_version_checker())

    # Initialize AI Stack memory on startup
    if user_memory:
        log("AI Stack memory initialized")
        load_memory()
    load_token_usage()
    load_experimental()

    while True:
        try:
            for u in (await poll()):
                msg = u.get("message")
                if not msg: continue
                mid, cid = msg.get("message_id"), msg["chat"]["id"]
                if mid and (cid, mid) in processed: continue
                if mid: processed.add((cid, mid))
                if len(processed) > 1000: processed.clear()
                if msg.get("from", {}).get("is_bot"):
                    continue
                chat, uid = msg["chat"]["id"], msg["from"]["id"]
                text = msg.get("text", "")
                now = time.time()
                _prev = last_user_msg.get(uid, {})
                if _prev and now - _prev.get("t", 0) < 10 and _prev.get("text") == text:
                    continue
                last_user_msg[uid] = {"t": now, "text": text}
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
                    transcribed = await bf.voice_to_text(voice["file_id"])
                    if not transcribed or transcribed == "/voice_error":
                        await send(chat, "Could not transcribe audio.")
                        continue
                    text = transcribed
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

                parts = text.split()
                cmd = parts[0].lower() if parts else ""

                log(f"Msg from {uid}: {text[:50]}")
                if not text: continue
                log(f"Processing: {cmd}")

                is_owner = uid == OWNER_ID
                is_admin = uid in admins
                is_mod = uid in mods

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
                        f"OpenCode Bot v{ver}",
                        f"  Agents: {len(AGENTS)}  Providers: {len(PROVIDERS)}",
                        "",
                        "Commands:",
                        "  /agents — List agents",
                        "  /agent <name> — Switch agent",
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

                elif cmd == "/help":
                    categories = [
                        ("CHAT", [
                            "/start — Reset session",
                            "/agent <name> — Switch agent",
                            "/agents — List agents",
                            "/repo — List / switch AI provider",
                            "/status — Current agent + provider",
                            "/multi start <p1> [p2] [rounds=2] — Talk to 2 AIs at once",
                            "/multi stop — End multi-AI session",
                            "/clear — Clear history",
                            "/remember <fact> — Store a fact in memory",
                            "/recall <query> — Search your memories",
                        ]),
                        ("MODES", [
                            "/mode — Toggle chat / team / autonomous",
                            "/arch — Switch architecture (single, sequential, parallel…)",
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
                            "/remind <duration> <msg> — Reminder",
                            "/digest — Summarize conversation",
                            "/routine create|list|show|delete|run — Prompt chaining workflows",
                            "/plugin load|list — Load/list plugins",
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
                            with open(SESSIONS_FILE) as _f: _pd = json.load(_f)
                        except: pass
                    profiles = _pd.get("profiles", {})
                    if sub == "save":
                        profiles[str(uid)] = {"agent": active_agent, "provider": active_provider, "effort": effort, "thinking": thinking_mode, "arch": active_arch}
                        _pd["profiles"] = profiles
                        with open(SESSIONS_FILE, "w") as _f: json.dump(_pd, _f)
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
                        with open(SESSIONS_FILE, "w") as _f: json.dump(_pd, _f)
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
                    except:
                        await send(chat, "Invalid ID.")

                elif cmd == "/agent":
                    if len(parts) < 2:
                        await send(chat, f"Usage: /agent <name>. Use /agents to list all.")
                        continue
                    name = parts[1].lower()
                    if name not in AGENTS:
                        await send(chat, f"Unknown agent. Use /agents to see all.")
                        continue
                    a = AGENTS[name]
                    active_agent = name
                    sessions.pop(uid, None)
                    await send(chat, f"Agent: {name} — {a['desc']}\n\nPrompt: {a['prompt']}")
                    ap = AGENT_PROVIDERS.get(name)
                    if not ap or not _is_configured(ap.get("key", "")):
                        await send(chat, f"This agent needs its own API provider. Use:\n/agentprovider {name} <url> <key> <model>\nExample: /agentprovider {name} https://api.example.com/v1/chat/completions sk-abc123 gpt-4o")
                    await send(chat, f"Great choice! Do you wanna set token usage?\nUse /low /normal /medium /high /superhigh\nCurrent: {effort} ({EFFORT_LEVELS[effort]['desc']})")

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
                    await send(chat, f"Switched to provider: {name} ({PROVIDERS[name]['model']})")

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

                elif cmd == "/clear":
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, "Session cleared.")

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
                    await send(chat, f"Mode: {name} — {MODES[name]['desc']}")

                elif cmd == "/effort":
                    await send(chat, f"Effort: {effort} — {EFFORT_LEVELS[effort]['desc']}\nUse /low /normal /medium /high /superhigh to change.\nThinking: {thinking_mode}")

                elif cmd in ("/low", "/normal", "/medium", "/high", "/superhigh"):
                    level = cmd[1:]
                    if level in EFFORT_LEVELS:
                        effort = level
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
                    sessions.pop(uid, None)
                    team_sessions.pop(uid, None)
                    await send(chat, f"Team activated: {tname} ({', '.join(TEAMS[tname]['agents'])})\nArch: {active_arch}")

                elif cmd == "/stopteam":
                    active_team = None
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
                    except:
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
                    except:
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
                    except:
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
                    except:
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
                    with open(AGENT_PROVIDERS_FILE, "w") as f:
                        json.dump(AGENT_PROVIDERS, f, indent=2)
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
                        except: pass

                elif cmd == "/premadeskills":
                    lines = [f"Pre-made skill teams ({len(PREMADE_SKILLS)}):"]
                    for name, s in sorted(PREMADE_SKILLS.items()):
                        agents = ", ".join(s["agents"])
                        lines.append(f"\n  {name}")
                        lines.append(f"  {s['desc']}")
                        lines.append(f"  Agents: {agents}")
                    await send(chat, "\n".join(lines))

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
                    ver_info = load_version()
                    ver = ver_info.get("version", "unknown")
                    changes = ver_info.get("whats_new", {}).get(ver, [])
                    state = load_version_state()
                    await announce_update(state.get("last_version", ""), ver, changes, state)
                    await send(chat, f"Announced v{ver} to all chats.")
                    
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
                            lines = [f"🔍 Notion search results for '{query}':"]
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
                    await typing(chat)
                    ctx = await bf.auto_context()
                    await send(chat, f"Current context:\n{ctx}")

                elif cmd == "/search":
                    if len(parts) < 2:
                        await send(chat, "Usage: /search <query>\nExample: /search latest AI news 2026")
                        continue
                    q = " ".join(parts[1:])
                    await typing(chat)
                    results = await bf.web_search(q)
                    reply = await smart_call([
                        {"role": "system", "content": "Summarize these web search results concisely, highlighting key findings."},
                        {"role": "user", "content": f"Search query: {q}\n\n{results}"},
                    ], active_provider)
                    await send(chat, f"ðŸ” Search: {q}\n\n{reply[:3500]}\n\nRaw results:\n{results[:1000]}")

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
                    if len(parts) < 3:
                        await send(chat, "Usage: /run <python|js> <code>\nExample: /run python print('hello')\nOr use /run python followed by multiple lines in subsequent messages.")
                        continue
                    lang = parts[1].lower()
                    code = " ".join(parts[2:])
                    await typing(chat)
                    result = await bf.run_code(code, lang)
                    await send(chat, f"```\n{result[:3500]}\n```")

                elif cmd == "/fetch":
                    if len(parts) < 2:
                        await send(chat, "Usage: /fetch <url>\nExample: /fetch https://example.com")
                        continue
                    url = parts[1]
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

                elif cmd == "/restore":
                    if not is_owner and not is_admin:
                        await send(chat, "Owner/Admin only.")
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
                        for name in zf.namelist():
                            if name.endswith(".json"):
                                target = os.path.join(os.path.dirname(__file__), name)
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
                    if len(parts) < 2:
                        plugins = bf.list_plugins()
                        if plugins:
                            await send(chat, "Loaded plugins:\n" + "\n".join(f"  {name}: {', '.join(cmds)}" for name, cmds in plugins))
                        else:
                            await send(chat, "No plugins loaded.\nUsage: /plugin load <url_or_path>\n       /plugin list")
                        continue
                    sub = parts[1].lower()
                    if sub == "load" and len(parts) >= 3:
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
                    except:
                        lines.append("Status: Not running (start separately: python web_gateway.py)")
                    await send(chat, "\n".join(lines))

                elif cmd.startswith("/") and cmd not in ("/start", "/version", "/help", "/agents", "/agent", "/repo", "/status", "/clear", "/myrole", "/checkrole", "/profile", "/addadmin", "/removeadmin", "/adminlist", "/addmod", "/removemod", "/modlist", "/addprovider", "/agentprovider", "/createagent", "/premadeskills", "/addprompt", "/arch", "/mode", "/tools", "/teams", "/putteam", "/createteam", "/useteam", "/stopteam", "/routes", "/gateway", "/repair", "/pyrit", "/toolfk", "/synoxcloud", "/webgateway", "/effort", "/thinking", "/low", "/normal", "/medium", "/high", "/superhigh", "/vision", "/draw", "/schedule", "/export", "/doc", "/ask", "/context", "/search", "/youtube", "/run", "/fetch", "/remind", "/digest", "/routine", "/multi", "/translate", "/qr", "/stats", "/data", "/plugin", "/n8n", "/n8n-status", "/n8n-logs", "/github", "/gmail", "/sheets", "/notion", "/crypto", "/stack", "/stackstatus", "/remember", "/recall", "/tokens", "/weather", "/backup", "/restore", "/dailydigest", "/experimental"):
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
                            memory_buffers[uid].append(f"[USER] {text}")
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
                            sessions.setdefault(uid, [])
                            agent_prompt = AGENTS[active_agent]["prompt"]
                            if not sessions[uid]:
                                try:
                                    ctx = await bf.auto_context()
                                    if ctx:
                                        sessions[uid].append({"role": "system", "content": f"{agent_prompt}\n\n[Auto-Context]\n{ctx}"})
                                    else:
                                        sessions[uid].append({"role": "system", "content": agent_prompt})
                                except:
                                    sessions[uid].append({"role": "system", "content": agent_prompt})
                            if len(sessions[uid]) > 30:
                                try:
                                    summarized = await bf.summarize_conversation(sessions[uid], smart_call)
                                    if summarized:
                                        sessions[uid] = summarized
                                except:
                                    sessions[uid] = sessions[uid][-20:]
                            sessions[uid].append({"role": "user", "content": text})
                            log(f"Calling {active_provider} for: {text[:50]}")
                            reply = await smart_call(sessions[uid][-20:], active_provider)
                            log(f"Reply: {reply[:80]}...")
                            sessions[uid].append({"role": "assistant", "content": reply})
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


if __name__ == "__main__":
    try:
        if sys.platform == "win32" and sys.version_info < (3, 14):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except BaseException as _be:
        _em = f"FATAL: {type(_be).__name__}: {_be}"
        print(_em, flush=True)
        try:
            with open("bot_crash.txt", "w") as _cf:
                _cf.write(f"main crash:\n{_tb.format_exc()}")
        except:
            pass
    finally:
        try:
            if os.path.exists(_LOCK_FILE):
                with open(_LOCK_FILE) as _f:
                    if _f.read().strip() == str(os.getpid()):
                        os.remove(_LOCK_FILE)
        except:
            pass
