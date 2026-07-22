import json, os, time, re
from datetime import datetime, timedelta, timezone
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_CONFIG_FILE = os.path.join(BASE_DIR, "ai_intelligence_config.json")
PERSONA_FILE = os.path.join(BASE_DIR, "ai_personas.json")
BRIEFINGS_FILE = os.path.join(BASE_DIR, "ai_briefings.json")

def _load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default if default is not None else {}

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

DOMAIN_PROFILES = {
    "healthcare": {
        "name": "Healthcare",
        "system_prompt": "You are a healthcare AI assistant. Provide accurate, evidence-based health information. Always remind users to consult healthcare professionals. Do not diagnose or prescribe.",
        "temperature": 0.3,
        "features": ["symptom_checker", "medication_info", "health_tips"],
    },
    "finance": {
        "name": "Finance",
        "system_prompt": "You are a financial AI assistant. Provide market analysis, budgeting advice, and investment education. Remind users that all investments carry risk. Never guarantee returns.",
        "temperature": 0.4,
        "features": ["market_analysis", "budget_planner", "investment_basics"],
    },
    "ecommerce": {
        "name": "E-Commerce",
        "system_prompt": "You are an e-commerce AI assistant. Help with product recommendations, order tracking, and customer support. Be helpful and professional.",
        "temperature": 0.5,
        "features": ["product_search", "order_status", "recommendations"],
    },
    "education": {
        "name": "Education",
        "system_prompt": "You are an educational AI tutor. Explain concepts clearly, use examples, and adapt to the student's level. Encourage curiosity and critical thinking.",
        "temperature": 0.6,
        "features": ["tutoring", "quiz_generation", "concept_explanation"],
    },
    "legal": {
        "name": "Legal",
        "system_prompt": "You are a legal information assistant. Provide general legal information, not legal advice. Always recommend consulting a qualified attorney.",
        "temperature": 0.3,
        "features": ["legal_info", "document_review", "rights_explanation"],
    },
}

class AIIntelligence:
    def __init__(self):
        self.config = _load_json(AI_CONFIG_FILE, {})
        self.personas = _load_json(PERSONA_FILE, {})
        self.briefings = _load_json(BRIEFINGS_FILE, {})
        self.user_profiles = defaultdict(lambda: {
            "mood": "neutral", "interests": [], "interaction_count": 0,
            "last_interaction": 0, "preferred_style": "balanced",
            "learning_history": [], "context_memory": [],
        })

    def _save(self):
        _save_json(AI_CONFIG_FILE, self.config)
        _save_json(PERSONA_FILE, self.personas)
        _save_json(BRIEFINGS_FILE, self.briefings)

    def get_chat_config(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "proactive_enabled": True,
                "multimodal_enabled": True,
                "domain": None,
                "persona_id": None,
                "briefing_schedule": None,
                "briefing_time": "08:00",
                "timezone": "UTC",
            }
        return self.config[cid]

    def toggle(self, chat_id, feature=None):
        cfg = self.get_chat_config(chat_id)
        if feature and feature in cfg:
            cfg[feature] = not cfg[feature]
        else:
            cfg["enabled"] = not cfg["enabled"]
        self._save()
        return cfg["enabled"]

    def set_domain(self, chat_id, domain):
        if domain and domain not in DOMAIN_PROFILES:
            return False, f"Unknown domain: {domain}. Available: {', '.join(DOMAIN_PROFILES.keys())}"
        cfg = self.get_chat_config(chat_id)
        cfg["domain"] = domain
        self._save()
        if domain:
            return True, f"Domain set to {DOMAIN_PROFILES[domain]['name']}"
        return True, "Domain cleared (general assistant)"

    def get_domain_prompt(self, chat_id):
        cfg = self.get_chat_config(chat_id)
        domain = cfg.get("domain")
        if domain and domain in DOMAIN_PROFILES:
            return DOMAIN_PROFILES[domain]["system_prompt"]
        return None

    def list_domains(self):
        lines = ["Available domains:"]
        for key, profile in DOMAIN_PROFILES.items():
            lines.append(f"  {key} — {profile['name']}: {', '.join(profile['features'])}")
        return "\n".join(lines)

    def create_persona(self, user_id, name, description, system_prompt, style="custom"):
        uid = str(user_id)
        pid = hashlib.md5(f"{uid}:{name}:{time.time()}".encode()).hexdigest()[:10]
        self.personas[pid] = {
            "id": pid, "creator": uid, "name": name,
            "description": description, "system_prompt": system_prompt,
            "style": style, "created": time.time(), "usage_count": 0,
        }
        self._save()
        return pid

    def get_persona(self, persona_id):
        return self.personas.get(persona_id)

    def list_personas(self, user_id=None):
        if user_id:
            uid = str(user_id)
            return {k: v for k, v in self.personas.items() if v.get("creator") == uid}
        return self.personas

    def delete_persona(self, persona_id, user_id):
        uid = str(user_id)
        if persona_id in self.personas:
            if self.personas[persona_id].get("creator") == uid:
                del self.personas[persona_id]
                self._save()
                return True
        return False

    def get_persona_prompt(self, chat_id):
        cfg = self.get_chat_config(chat_id)
        pid = cfg.get("persona_id")
        if pid and pid in self.personas:
            return self.personas[pid].get("system_prompt")
        return None

    def set_persona(self, chat_id, persona_id):
        cfg = self.get_chat_config(chat_id)
        if persona_id and persona_id not in self.personas:
            return False, "Persona not found"
        cfg["persona_id"] = persona_id
        self._save()
        if persona_id:
            p = self.personas[persona_id]
            return True, f"Persona set: {p['name']}"
        return True, "Persona cleared"

    def update_user_profile(self, user_id, **kwargs):
        uid = str(user_id)
        profile = self.user_profiles[uid]
        for k, v in kwargs.items():
            if k in ("mood", "interests", "preferred_style"):
                profile[k] = v
        profile["interaction_count"] = profile.get("interaction_count", 0) + 1
        profile["last_interaction"] = time.time()

    def get_user_profile(self, user_id):
        uid = str(user_id)
        return dict(self.user_profiles.get(uid, {}))

    def add_context_memory(self, user_id, text, role="user"):
        uid = str(user_id)
        profile = self.user_profiles[uid]
        profile.setdefault("context_memory", []).append({
            "text": text[:500], "role": role, "time": time.time()
        })
        if len(profile["context_memory"]) > 20:
            profile["context_memory"] = profile["context_memory"][-15:]

    def get_context_memory(self, user_id):
        uid = str(user_id)
        return self.user_profiles.get(uid, {}).get("context_memory", [])

    def schedule_briefing(self, chat_id, schedule="daily", time_str="08:00", timezone_str="UTC"):
        cid = str(chat_id)
        cfg = self.get_chat_config(cid)
        cfg["briefing_schedule"] = schedule
        cfg["briefing_time"] = time_str
        cfg["timezone"] = timezone_str
        self._save()
        return f"Briefing scheduled: {schedule} at {time_str} {timezone_str}"

    def cancel_briefing(self, chat_id):
        cfg = self.get_chat_config(chat_id)
        cfg["briefing_schedule"] = None
        self._save()
        return "Briefing cancelled"

    def should_send_briefing(self, chat_id):
        cfg = self.get_chat_config(chat_id)
        if not cfg.get("briefing_schedule"):
            return False
        now = datetime.now(timezone.utc)
        target_time = cfg.get("briefing_time", "08:00")
        try:
            h, m = map(int, target_time.split(":"))
        except Exception:
            return False
        if now.hour == h and now.minute == m:
            cid = str(chat_id)
            last = self.briefings.get(cid, {}).get("last_sent", 0)
            if time.time() - last > 3600:
                self.briefings.setdefault(cid, {})["last_sent"] = time.time()
                self._save()
                return True
        return False

    def format_briefing(self, chat_id, smart_call=None):
        cfg = self.get_chat_config(chat_id)
        domain = cfg.get("domain")
        lines = [f"🌅 Daily Briefing — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]
        if domain:
            lines.append(f"Domain: {DOMAIN_PROFILES.get(domain, {}).get('name', domain)}")
        lines.append("")
        lines.append("Good morning! Here's your daily summary:")
        lines.append("")
        lines.append("📊 Activity: Bot is operational and ready.")
        lines.append("🔧 Features: All systems nominal.")
        lines.append("")
        lines.append("Send any message to start chatting!")
        return "\n".join(lines)

    def format_config(self, chat_id):
        cfg = self.get_chat_config(chat_id)
        domain = cfg.get("domain")
        persona = cfg.get("persona_id")
        brief = cfg.get("briefing_schedule")
        lines = [
            f"AI Intelligence: {'ON' if cfg.get('enabled') else 'OFF'}",
            f"  Proactive: {'ON' if cfg.get('proactive_enabled') else 'OFF'}",
            f"  Multi-Modal: {'ON' if cfg.get('multimodal_enabled') else 'OFF'}",
            f"  Domain: {domain or 'general'}",
            f"  Persona: {persona or 'default'}",
            f"  Briefing: {brief or 'none'}",
        ]
        return "\n".join(lines)

_ai_int = None
def get_ai_intelligence():
    global _ai_int
    if _ai_int is None:
        _ai_int = AIIntelligence()
    return _ai_int
