import json, os, time, hashlib, hmac
from datetime import datetime, timedelta, timezone
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEC_API_FILE = os.path.join(BASE_DIR, "security_api_config.json")
WEBHOOK_FILE = os.path.join(BASE_DIR, "webhook_config.json")
BOT_BOT_FILE = os.path.join(BASE_DIR, "bot_bot_config.json")

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

class SecurityAPI:
    def __init__(self):
        self.config = _load_json(SEC_API_FILE, {})
        self.webhooks = _load_json(WEBHOOK_FILE, {})
        self.bot_bot = _load_json(BOT_BOT_FILE, {})
        self.ephemeral_store = defaultdict(list)

    def _save(self):
        _save_json(SEC_API_FILE, self.config)
        _save_json(WEBHOOK_FILE, self.webhooks)
        _save_json(BOT_BOT_FILE, self.bot_bot)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "ephemeral_enabled": True,
                "guest_bot_enabled": False,
                "bot_bot_enabled": False,
                "default_ephemeral_ttl": 3600,
                "allowed_guest_bots": [],
                "allowed_bot_bot_partners": [],
            }
        return self.config[cid]

    def toggle(self, chat_id, feature=None):
        cfg = self.get_chat(chat_id)
        if feature and feature in cfg:
            cfg[feature] = not cfg[feature]
        else:
            cfg["enabled"] = not cfg["enabled"]
        self._save()
        return cfg["enabled"]

    def create_ephemeral(self, chat_id, user_id, text, ttl=None):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        if not cfg.get("ephemeral_enabled"):
            return None
        eid = hashlib.md5(f"{cid}:{user_id}:{time.time()}".encode()).hexdigest()[:12]
        ttl = ttl or cfg.get("default_ephemeral_ttl", 3600)
        self.ephemeral_store[cid].append({
            "id": eid, "user_id": str(user_id), "text": text,
            "created": time.time(), "expires": time.time() + ttl,
            "ttl": ttl,
        })
        return {"ephemeral_id": eid, "ttl": ttl}

    def get_ephemeral(self, chat_id, ephemeral_id):
        cid = str(chat_id)
        now = time.time()
        for msg in self.ephemeral_store.get(cid, []):
            if msg["id"] == ephemeral_id and msg["expires"] > now:
                return msg
        return None

    def edit_ephemeral(self, chat_id, ephemeral_id, new_text):
        cid = str(chat_id)
        now = time.time()
        for msg in self.ephemeral_store.get(cid, []):
            if msg["id"] == ephemeral_id and msg["expires"] > now:
                msg["text"] = new_text
                return True
        return False

    def delete_ephemeral(self, chat_id, ephemeral_id):
        cid = str(chat_id)
        store = self.ephemeral_store.get(cid, [])
        self.ephemeral_store[cid] = [m for m in store if m["id"] != ephemeral_id]
        return True

    def cleanup_expired(self):
        now = time.time()
        cleaned = 0
        for cid in list(self.ephemeral_store.keys()):
            before = len(self.ephemeral_store[cid])
            self.ephemeral_store[cid] = [m for m in self.ephemeral_store[cid] if m["expires"] > now]
            cleaned += before - len(self.ephemeral_store[cid])
        return cleaned

    def add_webhook(self, name, url, secret=None, events=None, enabled=True):
        wid = hashlib.md5(f"{name}:{time.time()}".encode()).hexdigest()[:10]
        self.webhooks[wid] = {
            "id": wid, "name": name, "url": url,
            "secret": secret, "events": events or ["*"],
            "enabled": enabled, "created": time.time(),
            "last_triggered": 0, "fail_count": 0,
            "success_count": 0,
        }
        self._save()
        return wid

    def remove_webhook(self, webhook_id):
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self._save()
            return True
        return False

    def list_webhooks(self):
        return self.webhooks

    def trigger_webhook(self, webhook_id, event_type, payload):
        wh = self.webhooks.get(webhook_id)
        if not wh or not wh.get("enabled"):
            return False
        if "*" not in wh.get("events", []) and event_type not in wh.get("events", []):
            return False
        wh["last_triggered"] = time.time()
        wh["success_count"] = wh.get("success_count", 0) + 1
        self._save()
        return True

    def add_bot_bot_partner(self, chat_id, bot_username, allowed_commands=None):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        partners = cfg.setdefault("allowed_bot_bot_partners", [])
        if bot_username not in [p.get("bot") for p in partners]:
            partners.append({
                "bot": bot_username,
                "allowed_commands": allowed_commands or ["*"],
                "added": time.time(),
                "enabled": True,
            })
            self._save()
        return f"Bot-bot partner added: @{bot_username}"

    def remove_bot_bot_partner(self, chat_id, bot_username):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        partners = cfg.get("allowed_bot_bot_partners", [])
        cfg["allowed_bot_bot_partners"] = [p for p in partners if p.get("bot") != bot_username]
        self._save()
        return f"Bot-bot partner removed: @{bot_username}"

    def is_bot_bot_allowed(self, chat_id, bot_username):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        for p in cfg.get("allowed_bot_bot_partners", []):
            if p.get("bot") == bot_username and p.get("enabled"):
                return True
        return False

    def add_guest_bot(self, chat_id, bot_username):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        allowed = cfg.setdefault("allowed_guest_bots", [])
        if bot_username not in allowed:
            allowed.append(bot_username)
            self._save()
        return f"Guest bot allowed: @{bot_username}"

    def remove_guest_bot(self, chat_id, bot_username):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        cfg["allowed_guest_bots"] = [b for b in cfg.get("allowed_guest_bots", []) if b != bot_username]
        self._save()
        return f"Guest bot removed: @{bot_username}"

    def is_guest_bot_allowed(self, chat_id, bot_username):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        return bot_username in cfg.get("allowed_guest_bots", [])

    def format_config(self, chat_id):
        cfg = self.get_chat(chat_id)
        lines = [
            f"Security & API: {'ON' if cfg.get('enabled') else 'OFF'}",
            f"  Ephemeral: {'ON' if cfg.get('ephemeral_enabled') else 'OFF'} (TTL: {cfg.get('default_ephemeral_ttl', 3600)}s)",
            f"  Guest Bots: {'ON' if cfg.get('guest_bot_enabled') else 'OFF'} ({len(cfg.get('allowed_guest_bots', []))} allowed)",
            f"  Bot-to-Bot: {'ON' if cfg.get('bot_bot_enabled') else 'OFF'} ({len(cfg.get('allowed_bot_bot_partners', []))} partners)",
        ]
        wh_count = len(self.webhooks)
        lines.append(f"  Webhooks: {wh_count} configured")
        return "\n".join(lines)

_sec = None
def get_security_api():
    global _sec
    if _sec is None:
        _sec = SecurityAPI()
    return _sec
