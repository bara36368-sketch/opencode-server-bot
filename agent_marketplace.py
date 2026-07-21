import json, os, time, asyncio, re, html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MARKET_FILE = os.path.join(BASE_DIR, "market_registry.json")
AGENTS_FILE = os.path.join(BASE_DIR, "agents.json")

MARKETPLACE_REPO = "https://raw.githubusercontent.com/anomalyco/opencode-agents/main/registry.json"
MARKETPLACE_FALLBACK = "https://raw.githubusercontent.com/aryasatya42/opencode-bot-agents/main/registry.json"

def _load_agents():
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        with open(AGENTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_agents(agents):
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)

class AgentMarketplace:
    def __init__(self):
        self.registry = []
        self.cache_time = 0
        self.installed = self._load_installed()

    def _load_installed(self):
        p = os.path.join(BASE_DIR, "market_installed.json")
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_installed(self):
        p = os.path.join(BASE_DIR, "market_installed.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.installed, f, indent=2)

    async def fetch_registry(self, http_client=None):
        if time.time() - self.cache_time < 300:
            return self.registry
        urls = [MARKETPLACE_REPO, MARKETPLACE_FALLBACK]
        for url in urls:
            try:
                if http_client:
                    r = await http_client.get(url, timeout=15)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list):
                            self.registry = data
                        elif isinstance(data, dict) and "agents" in data:
                            self.registry = data["agents"]
                        elif isinstance(data, dict):
                            self.registry = [{"id": k, **v} for k, v in data.items()]
                        self.cache_time = time.time()
                        return self.registry
            except Exception:
                continue
        return self.registry

    def search(self, query, limit=15):
        q = query.lower()
        results = []
        for agent in self.registry:
            aid = agent.get("id", "").lower()
            desc = agent.get("desc", "").lower()
            prompt = agent.get("prompt", "").lower()
            tags = " ".join(agent.get("tags", [])).lower()
            if q in aid or q in desc or q in prompt or q in tags:
                results.append(agent)
        return results[:limit]

    def get_featured(self, limit=10):
        featured = [a for a in self.registry if a.get("featured") or a.get("stars", 0) > 10]
        return sorted(featured, key=lambda x: x.get("stars", 0), reverse=True)[:limit]

    def list_all(self, page=0, per_page=20):
        start = page * per_page
        return self.registry[start:start + per_page]

    def get(self, agent_id):
        for a in self.registry:
            if a.get("id", "").lower() == agent_id.lower():
                return a
        return None

    async def install(self, agent_id, http_client=None):
        agent = self.get(agent_id)
        if not agent:
            alt_url = f"https://raw.githubusercontent.com/anomalyco/opencode-agents/main/agents/{agent_id}.json"
            try:
                if http_client:
                    r = await http_client.get(alt_url, timeout=10)
                    if r.status_code == 200:
                        agent = r.json()
            except Exception:
                pass
        if not agent:
            return False, "Agent not found in marketplace"

        aid = agent.get("id", agent_id).lower().replace(" ", "-")
        existing = _load_agents()
        already = aid in existing

        existing[aid] = {
            "desc": agent.get("desc", ""),
            "prompt": agent.get("prompt", ""),
            "tags": agent.get("tags", []),
            "marketplace": True,
            "installed": time.time(),
            "source": agent.get("source", agent.get("url", "")),
        }
        _save_agents(existing)

        self.installed[aid] = {"installed": time.time(), "source": agent.get("source", "marketplace")}
        self._save_installed()

        return True, f"Installed {'(updated)' if already else ''}: {aid}"

    def list_installed(self):
        agents = _load_agents()
        market_agents = {k: v for k, v in agents.items() if v.get("marketplace")}
        return sorted(market_agents.items(), key=lambda x: x[1].get("installed", 0), reverse=True)

    def uninstall(self, agent_id):
        agents = _load_agents()
        aid = agent_id.lower().replace(" ", "-")
        if aid not in agents or not agents[aid].get("marketplace"):
            return False, "Not a marketplace agent"
        del agents[aid]
        _save_agents(agents)
        self.installed.pop(aid, None)
        self._save_installed()
        return True, f"Uninstalled: {aid}"

    async def publish(self, agent_id, desc, prompt, http_client=None, github_token=None):
        aid = agent_id.lower().replace(" ", "-")
        payload = {"id": aid, "desc": desc, "prompt": prompt, "source": "community", "stars": 0}
        if github_token:
            url = "https://api.github.com/repos/anomalyco/opencode-agents/contents/agents"
            try:
                if http_client:
                    existing = _load_agents()
                    existing[aid] = {"desc": desc, "prompt": prompt, "source": "community", "marketplace": True, "installed": time.time()}
                    _save_agents(existing)
                    return True, f"Published locally: {aid}\n\nTo publish to global registry, fork github.com/anomalyco/opencode-agents and submit a PR."
            except Exception:
                pass
        existing = _load_agents()
        existing[aid] = {"desc": desc, "prompt": prompt, "source": "community", "marketplace": True, "installed": time.time()}
        _save_agents(existing)
        return True, f"Published locally: {aid}\n\nShare your agent: Submit a PR to github.com/anomalyco/opencode-agents"

_market = None

def get_market():
    global _market
    if _market is None:
        _market = AgentMarketplace()
    return _market
