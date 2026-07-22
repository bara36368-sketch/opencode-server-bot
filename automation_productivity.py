import json, os, time, hashlib
from datetime import datetime, timedelta, timezone
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_CONFIG_FILE = os.path.join(BASE_DIR, "automation_config.json")
DRIP_FILE = os.path.join(BASE_DIR, "drip_sequences.json")
CRM_FILE = os.path.join(BASE_DIR, "crm_data.json")
WIZARDS_FILE = os.path.join(BASE_DIR, "wizards.json")

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

class AutomationProductivity:
    def __init__(self):
        self.config = _load_json(AUTO_CONFIG_FILE, {})
        self.drips = _load_json(DRIP_FILE, {})
        self.crm = _load_json(CRM_FILE, {})
        self.wizards = _load_json(WIZARDS_FILE, {})

    def _save(self):
        _save_json(AUTO_CONFIG_FILE, self.config)
        _save_json(DRIP_FILE, self.drips)
        _save_json(CRM_FILE, self.crm)
        _save_json(WIZARDS_FILE, self.wizards)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "drip_enabled": True,
                "crm_enabled": True,
                "wizard_enabled": True,
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

    def create_drip(self, chat_id, name, messages, interval_hours=24, target_chat=None):
        cid = str(chat_id)
        did = hashlib.md5(f"{cid}:{name}:{time.time()}".encode()).hexdigest()[:10]
        self.drips[did] = {
            "id": did, "chat_id": cid, "name": name,
            "messages": messages, "interval_hours": interval_hours,
            "target_chat": target_chat or cid,
            "active": True, "subscribers": [],
            "created": time.time(), "last_sent": 0,
        }
        self._save()
        return did

    def subscribe_drip(self, drip_id, user_id):
        if drip_id not in self.drips:
            return False, "Drip not found"
        uid = str(user_id)
        drip = self.drips[drip_id]
        if uid not in drip.get("subscribers", []):
            drip.setdefault("subscribers", []).append(uid)
            drip["started"] = drip.get("started", {})
            drip["started"][uid] = time.time()
            drip["progress"] = drip.get("progress", {})
            drip["progress"][uid] = 0
            self._save()
        return True, f"Subscribed to '{drip['name']}'"

    def unsubscribe_drip(self, drip_id, user_id):
        if drip_id not in self.drips:
            return False
        uid = str(user_id)
        drip = self.drips[drip_id]
        drip["subscribers"] = [s for s in drip.get("subscribers", []) if s != uid]
        self._save()
        return True

    def get_pending_drip_messages(self):
        now = time.time()
        pending = []
        for did, drip in self.drips.items():
            if not drip.get("active"):
                continue
            interval = drip.get("interval_hours", 24) * 3600
            for uid in drip.get("subscribers", []):
                progress = drip.get("progress", {}).get(uid, 0)
                if progress >= len(drip.get("messages", [])):
                    continue
                started = drip.get("started", {}).get(uid, drip.get("created", 0))
                next_time = started + (progress * interval)
                if now >= next_time:
                    pending.append({
                        "drip_id": did,
                        "user_id": uid,
                        "message_index": progress,
                        "message": drip["messages"][progress],
                        "target_chat": drip.get("target_chat"),
                    })
                    drip.setdefault("progress", {})[uid] = progress + 1
        if pending:
            self._save()
        return pending

    def list_drips(self, chat_id=None):
        if chat_id:
            cid = str(chat_id)
            return {k: v for k, v in self.drips.items() if v.get("chat_id") == cid}
        return self.drips

    def delete_drip(self, drip_id):
        if drip_id in self.drips:
            del self.drips[drip_id]
            self._save()
            return True
        return False

    def add_crm_contact(self, chat_id, user_id, name, phone=None, email=None, tags=None, notes=None):
        cid = str(chat_id)
        uid = str(user_id)
        self.crm.setdefault(cid, {})
        self.crm[cid][uid] = {
            "name": name, "phone": phone, "email": email,
            "tags": tags or [], "notes": notes or "",
            "created": time.time(), "last_updated": time.time(),
            "interactions": 0,
        }
        self._save()
        return True

    def update_crm_contact(self, chat_id, user_id, **kwargs):
        cid = str(chat_id)
        uid = str(user_id)
        if cid in self.crm and uid in self.crm[cid]:
            for k, v in kwargs.items():
                if k in ("name", "phone", "email", "tags", "notes"):
                    self.crm[cid][uid][k] = v
            self.crm[cid][uid]["last_updated"] = time.time()
            self._save()
            return True
        return False

    def get_crm_contact(self, chat_id, user_id):
        cid = str(chat_id)
        uid = str(user_id)
        return self.crm.get(cid, {}).get(uid)

    def list_crm_contacts(self, chat_id, tag=None):
        cid = str(chat_id)
        contacts = self.crm.get(cid, {})
        if tag:
            return {k: v for k, v in contacts.items() if tag in v.get("tags", [])}
        return contacts

    def search_crm(self, chat_id, query):
        cid = str(chat_id)
        contacts = self.crm.get(cid, {})
        query_lower = query.lower()
        results = {}
        for uid, contact in contacts.items():
            if (query_lower in (contact.get("name") or "").lower() or
                query_lower in (contact.get("phone") or "").lower() or
                query_lower in (contact.get("email") or "").lower() or
                any(query_lower in t.lower() for t in contact.get("tags", []))):
                results[uid] = contact
        return results

    def create_wizard(self, chat_id, name, steps):
        cid = str(chat_id)
        wid = hashlib.md5(f"{cid}:{name}:{time.time()}".encode()).hexdigest()[:10]
        self.wizards[wid] = {
            "id": wid, "chat_id": cid, "name": name,
            "steps": steps, "active": True,
            "created": time.time(),
        }
        self._save()
        return wid

    def get_wizard(self, wizard_id):
        return self.wizards.get(wizard_id)

    def start_wizard(self, wizard_id, user_id):
        wizard = self.wizards.get(wizard_id)
        if not wizard:
            return None
        uid = str(user_id)
        return {
            "wizard_id": wizard_id,
            "user_id": uid,
            "current_step": 0,
            "data": {},
            "started": time.time(),
        }

    def process_wizard_step(self, wizard_id, user_id, step_index, answer):
        wizard = self.wizards.get(wizard_id)
        if not wizard:
            return None
        steps = wizard.get("steps", [])
        if step_index >= len(steps):
            return None
        step = steps[step_index]
        return {
            "step": step,
            "answer": answer,
            "next_step": step_index + 1 if step_index + 1 < len(steps) else None,
            "complete": step_index + 1 >= len(steps),
        }

    def list_wizards(self, chat_id=None):
        if chat_id:
            cid = str(chat_id)
            return {k: v for k, v in self.wizards.items() if v.get("chat_id") == cid}
        return self.wizards

    def delete_wizard(self, wizard_id):
        if wizard_id in self.wizards:
            del self.wizards[wizard_id]
            self._save()
            return True
        return False

    def format_config(self, chat_id):
        cfg = self.get_chat(chat_id)
        drips = self.list_drips(chat_id)
        crm_count = len(self.crm.get(str(chat_id), {}))
        wizards = self.list_wizards(chat_id)
        lines = [
            f"Automation: {'ON' if cfg.get('enabled') else 'OFF'}",
            f"  Drip: {'ON' if cfg.get('drip_enabled') else 'OFF'} ({len(drips)} sequences)",
            f"  CRM: {'ON' if cfg.get('crm_enabled') else 'OFF'} ({crm_count} contacts)",
            f"  Wizards: {'ON' if cfg.get('wizard_enabled') else 'OFF'} ({len(wizards)} active)",
        ]
        return "\n".join(lines)

_auto = None
def get_automation():
    global _auto
    if _auto is None:
        _auto = AutomationProductivity()
    return _auto
