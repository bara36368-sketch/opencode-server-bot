import json, os, time, re, hashlib
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAFETY_FILE = os.path.join(BASE_DIR, "safety_config.json")
REPUTATION_FILE = os.path.join(BASE_DIR, "safety_reputation.json")
THREATS_FILE = os.path.join(BASE_DIR, "safety_threats.json")

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

SPAM_PATTERNS = [
    r'(?i)(buy|sell|crypto|forex|invest|profit|guaranteed|earn|money|wealth|rich|millionaire)',
    r'(?i)(click here|join now|limited time|act fast|free money|no risk)',
    r'(?i)(t\.me/|telegram\.me/)',
    r'https?://[^\s]+',
    r'(?i)(@\w+bot|forward|share with|send to)',
    r'(?i)(adult|xxx|nsfw|18\+|porn)',
]

NUKE_ACTIONS = {"ban", "kick", "delete", "restrict", "promote", "set_title", "set_photo", "set_description"}

class SafetyModeration:
    def __init__(self):
        self.config = _load_json(SAFETY_FILE, {})
        self.reputation = _load_json(REPUTATION_FILE, {})
        self.threats = _load_json(THREATS_FILE, {"banned_patterns": [], "cross_group_bans": []})
        self.action_log = defaultdict(lambda: deque(maxlen=500))
        self.join_tracker = defaultdict(lambda: deque(maxlen=200))
        self.edit_tracker = defaultdict(lambda: deque(maxlen=500))

    def _save(self):
        _save_json(SAFETY_FILE, self.config)
        _save_json(REPUTATION_FILE, self.reputation)
        _save_json(THREATS_FILE, self.threats)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "toxicity_enabled": True,
                "captcha_enabled": True,
                "anti_nuke_enabled": True,
                "behavioral_enabled": True,
                "edit_detection_enabled": True,
                "toxicity_threshold": 0.7,
                "captcha_timeout": 120,
                "max_joins_per_minute": 10,
                "max_actions_per_minute": 5,
                "trusted_users": [],
                "whitelisted_domains": [],
                "custom_blocked_phrases": [],
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

    def _check_spam_score(self, text):
        if not text:
            return 0.0
        score = 0.0
        text_lower = text.lower()
        matches = 0
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        score = min(1.0, matches / 3.0)
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                score = min(1.0, score + 0.2)
        if text.count("!") > 3 or text.count("?") > 3:
            score = min(1.0, score + 0.1)
        return score

    def check_toxicity(self, chat_id, user_id, text):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled") or not cfg.get("toxicity_enabled"):
            return None
        uid = str(user_id)
        if uid in cfg.get("trusted_users", []):
            return None
        score = self._check_spam_score(text)
        blocked = cfg.get("custom_blocked_phrases", [])
        for phrase in blocked:
            if phrase.lower() in text.lower():
                score = 1.0
                break
        for entry in self.threats.get("banned_patterns", []):
            if re.search(entry.get("pattern", ""), text, re.IGNORECASE):
                score = 1.0
                break
        threshold = cfg.get("toxicity_threshold", 0.7)
        if score >= threshold:
            action = "ban" if score >= 0.9 else "warn"
            self._log_action(chat_id, "toxicity", user_id, text[:200], score, action)
            return {"action": action, "score": round(score, 2), "reason": "spam/toxicity detected"}
        return None

    def check_captcha(self, chat_id, user_id, username=None):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled") or not cfg.get("captcha_enabled"):
            return None
        uid = str(user_id)
        if uid in cfg.get("trusted_users", []):
            return None
        rep = self._get_reputation(uid)
        if rep.get("verified", False):
            return None
        challenge_type = "math"
        import random
        a, b = random.randint(1, 20), random.randint(1, 20)
        op = random.choice(["+", "-", "*"])
        if op == "+": answer = a + b
        elif op == "-": answer = a - b
        else: answer = a * b
        challenge = f"What is {a} {op} {b}?"
        return {
            "type": challenge_type,
            "challenge": challenge,
            "answer": str(answer),
            "timeout": cfg.get("captcha_timeout", 120),
            "user_id": uid,
        }

    def verify_captcha(self, chat_id, user_id, answer, expected):
        uid = str(user_id)
        if str(answer).strip() == str(expected).strip():
            rep = self._get_reputation(uid)
            rep["verified"] = True
            rep["verified_at"] = time.time()
            self._save()
            return True
        return False

    def check_anti_nuke(self, chat_id, admin_id, action_type, targets=None):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled") or not cfg.get("anti_nuke_enabled"):
            return None
        aid = str(admin_id)
        cid = str(chat_id)
        now = time.time()
        log_key = f"{cid}:{aid}"
        self.action_log[log_key].append({"action": action_type, "time": now, "targets": targets or []})
        recent = [a for a in self.action_log[log_key] if now - a["time"] < 60]
        if len(recent) >= cfg.get("max_actions_per_minute", 5):
            action_types = set(a["action"] for a in recent)
            if len(action_types) >= 2 or action_type in ("ban", "kick", "delete"):
                self._log_action(chat_id, "anti_nuke", admin_id, f"mass {action_type}", len(recent), "alert")
                return {
                    "alert": True,
                    "message": f"⚠️ Anti-Nuke: Admin {admin_id} performed {len(recent)} actions in 1 minute ({', '.join(action_types)})",
                    "severity": "high" if len(recent) >= 10 else "medium",
                    "recent_actions": len(recent),
                }
        return None

    def check_behavioral(self, chat_id, user_id, username=None, first_name=None):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled") or not cfg.get("behavioral_enabled"):
            return None
        uid = str(user_id)
        cid = str(chat_id)
        now = time.time()
        self.join_tracker[cid].append({"user": uid, "time": now})
        recent_joins = [j for j in self.join_tracker[cid] if now - j["time"] < 60]
        if len(recent_joins) >= cfg.get("max_joins_per_minute", 10):
            self._log_action(chat_id, "behavioral", user_id, "mass join detected", len(recent_joins), "alert")
            return {"alert": True, "reason": "mass join raid detected", "count": len(recent_joins)}
        flags = []
        if username and re.match(r'^[a-zA-Z]+\d{4,}$', username):
            flags.append("suspicious_username")
        if first_name and len(first_name) > 20:
            flags.append("long_first_name")
        if not username:
            flags.append("no_username")
        rep = self._get_reputation(uid)
        if rep.get("flags", 0) >= 3:
            flags.append("repeat_offender")
        if len(flags) >= 2:
            return {"alert": True, "reason": "suspicious profile", "flags": flags}
        return None

    def check_edit(self, chat_id, message_id, user_id, old_text, new_text):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled") or not cfg.get("edit_detection_enabled"):
            return None
        cid = str(chat_id)
        mid = str(message_id)
        now = time.time()
        self.edit_tracker[cid].append({
            "message_id": mid, "user_id": str(user_id),
            "old": old_text[:500], "new": new_text[:500], "time": now
        })
        old_score = self._check_spam_score(old_text)
        new_score = self._check_spam_score(new_text)
        if old_score < 0.3 and new_score >= 0.7:
            self._log_action(chat_id, "edit_detection", user_id,
                f"edited clean→spam: {new_text[:200]}", new_score, "alert")
            return {
                "alert": True,
                "reason": "message edited from clean to spam",
                "old_score": round(old_score, 2),
                "new_score": round(new_score, 2),
            }
        return None

    def add_to_global_ban(self, user_id, reason="spam", source_chat=None):
        uid = str(user_id)
        entry = {
            "user_id": uid, "reason": reason,
            "time": time.time(), "source": source_chat,
        }
        if entry not in self.threats.get("cross_group_bans", []):
            self.threats.setdefault("cross_group_bans", []).append(entry)
            if len(self.threats["cross_group_bans"]) > 5000:
                self.threats["cross_group_bans"] = self.threats["cross_group_bans"][-2500:]
            self._save()
        rep = self._get_reputation(uid)
        rep["banned"] = True
        rep["ban_reason"] = reason
        rep["ban_time"] = time.time()
        self._save()

    def is_global_banned(self, user_id):
        uid = str(user_id)
        for entry in self.threats.get("cross_group_bans", []):
            if entry.get("user_id") == uid:
                return entry
        rep = self._get_reputation(uid)
        if rep.get("banned"):
            return {"reason": rep.get("ban_reason", "unknown"), "time": rep.get("ban_time", 0)}
        return None

    def add_blocked_pattern(self, pattern, reason="custom"):
        self.threats.setdefault("banned_patterns", []).append({
            "pattern": pattern, "reason": reason, "time": time.time()
        })
        self._save()

    def add_trusted_user(self, chat_id, user_id):
        cfg = self.get_chat(chat_id)
        uid = str(user_id)
        if uid not in cfg.get("trusted_users", []):
            cfg.setdefault("trusted_users", []).append(uid)
            self._save()

    def _get_reputation(self, user_id):
        uid = str(user_id)
        if uid not in self.reputation:
            self.reputation[uid] = {
                "score": 50, "violations": 0, "verified": False,
                "flags": 0, "first_seen": time.time(), "last_action": time.time()
            }
        return self.reputation[uid]

    def update_reputation(self, user_id, delta):
        uid = str(user_id)
        rep = self._get_reputation(uid)
        rep["score"] = max(0, min(100, rep["score"] + delta))
        rep["last_action"] = time.time()
        if delta < 0:
            rep["violations"] = rep.get("violations", 0) + 1
            rep["flags"] = rep.get("flags", 0) + 1
        self._save()

    def get_reputation(self, user_id):
        return self._get_reputation(user_id)

    def _log_action(self, chat_id, feature, user_id, detail, score, action):
        cid = str(chat_id)
        log_key = f"{cid}:log"
        self.action_log[log_key].append({
            "feature": feature, "user": str(user_id),
            "detail": detail[:300], "score": score,
            "action": action, "time": time.time()
        })

    def get_log(self, chat_id, limit=20):
        cid = str(chat_id)
        log_key = f"{cid}:log"
        entries = list(self.action_log.get(log_key, []))
        return entries[-limit:]

    def format_config(self, chat_id):
        cfg = self.get_chat(chat_id)
        features = [
            ("AI Toxicity", cfg.get("toxicity_enabled")),
            ("CAPTCHA", cfg.get("captcha_enabled")),
            ("Anti-Nuke", cfg.get("anti_nuke_enabled")),
            ("Behavioral", cfg.get("behavioral_enabled")),
            ("Edit Detection", cfg.get("edit_detection_enabled")),
        ]
        lines = [f"Safety: {'ON' if cfg.get('enabled') else 'OFF'}"]
        for name, enabled in features:
            lines.append(f"  {name}: {'ON' if enabled else 'OFF'}")
        lines.append(f"  Threshold: {cfg.get('toxicity_threshold', 0.7)}")
        lines.append(f"  Trusted: {len(cfg.get('trusted_users', []))} users")
        return "\n".join(lines)

_safety = None
def get_safety():
    global _safety
    if _safety is None:
        _safety = SafetyModeration()
    return _safety
