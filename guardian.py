import json, os, time, asyncio, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_FILE = os.path.join(BASE_DIR, "auto_reply.json")
GUARDIAN_FILE = os.path.join(BASE_DIR, "guardian_config.json")
GUARDIAN_LOG_FILE = os.path.join(BASE_DIR, "guardian_log.json")

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


class AutoReplyConfig:
    def __init__(self):
        self.configs = _load_json(AUTO_FILE, {})

    def _save(self):
        _save_json(AUTO_FILE, self.configs)

    def set(self, uid, enabled=True, template=None, scope="all", whitelist=None, blacklist=None):
        uid = str(uid)
        if uid not in self.configs:
            self.configs[uid] = {"enabled": False, "template": "", "scope": "all", "whitelist": [], "blacklist": []}
        self.configs[uid]["enabled"] = enabled
        if template is not None:
            self.configs[uid]["template"] = template
        if scope:
            self.configs[uid]["scope"] = scope
        if whitelist is not None:
            self.configs[uid]["whitelist"] = whitelist
        if blacklist is not None:
            self.configs[uid]["blacklist"] = blacklist
        self._save()

    def get(self, uid):
        uid = str(uid)
        return self.configs.get(uid, {"enabled": False, "template": "", "scope": "all", "whitelist": [], "blacklist": []})

    def is_enabled(self, uid):
        return self.get(uid).get("enabled", False)

    def can_respond_in(self, uid, chat_id):
        cfg = self.get(uid)
        if not cfg.get("enabled"):
            return False
        scope = cfg.get("scope", "all")
        chat_id = str(chat_id)
        if scope == "all":
            return True
        if scope == "whitelist":
            return chat_id in cfg.get("whitelist", [])
        if scope == "blacklist":
            return chat_id not in cfg.get("blacklist", [])
        return True

    def allowed_chats(self, uid):
        cfg = self.get(uid)
        return {"scope": cfg.get("scope", "all"), "whitelist": cfg.get("whitelist", []), "blacklist": cfg.get("blacklist", [])}

    def toggle(self, uid):
        cfg = self.get(uid)
        new = not cfg.get("enabled", False)
        self.set(uid, enabled=new)
        return new

    def all_enabled(self):
        return [uid for uid, cfg in self.configs.items() if cfg.get("enabled")]


class GuardianConfig:
    def __init__(self):
        self.configs = _load_json(GUARDIAN_FILE, {})

    def _save(self):
        _save_json(GUARDIAN_FILE, self.configs)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        return self.configs.get(cid, {"enabled": False, "rules": "", "screening": False, "quizzes": [], "welcome": "", "auto_approve": True, "log": True, "strictness": "medium"})

    def set_chat(self, chat_id, **kwargs):
        cid = str(chat_id)
        if cid not in self.configs:
            self.configs[cid] = {"enabled": False, "rules": "", "screening": False, "quizzes": [], "welcome": "", "auto_approve": True, "log": True, "strictness": "medium"}
        for k, v in kwargs.items():
            self.configs[cid][k] = v
        self._save()

    def toggle(self, chat_id):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        new = not cfg.get("enabled", False)
        self.set_chat(chat_id, enabled=new)
        return new

    def is_enabled(self, chat_id):
        return self.get_chat(chat_id).get("enabled", False)

    def add_quiz(self, chat_id, question, answer):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        quizzes = cfg.get("quizzes", [])
        quizzes.append({"question": question, "answer": answer, "id": str(int(time.time()))})
        self.set_chat(chat_id, quizzes=quizzes)

    def remove_quiz(self, chat_id, quiz_id):
        cfg = self.get_chat(chat_id)
        quizzes = [q for q in cfg.get("quizzes", []) if q.get("id") != quiz_id]
        self.set_chat(chat_id, quizzes=quizzes)

    def check_message(self, chat_id, text):
        cfg = self.get_chat(chat_id)
        if not cfg.get("enabled"):
            return None
        rules = cfg.get("rules", "")
        if not rules:
            return None
        text_lower = text.lower()
        violations = []
        for line in rules.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("ban:") or line.startswith("block:"):
                keyword = line.split(":", 1)[1].strip().lower()
                if keyword in text_lower:
                    violations.append(("ban", f"Contains banned keyword: {keyword}"))
            elif line.startswith("warn:"):
                keyword = line.split(":", 1)[1].strip().lower()
                if keyword in text_lower:
                    violations.append(("warn", f"Flagged keyword: {keyword}"))
            elif line.startswith("maxlen:"):
                try:
                    maxl = int(line.split(":", 1)[1].strip())
                    if len(text) > maxl:
                        violations.append(("warn", f"Message exceeds {maxl} chars"))
                except ValueError:
                    pass
        return violations if violations else None

    def evaluate_join_request(self, chat_id, user_info, answers=None):
        cfg = self.get_chat(chat_id)
        if not cfg.get("screening"):
            return True, None
        quizzes = cfg.get("quizzes", [])
        if not quizzes:
            return True, None
        if not answers:
            strictness = cfg.get("strictness", "medium")
            if strictness == "low":
                return True, None
            return False, "Please answer the screening questions first."
        correct = 0
        total = len(quizzes)
        for q in quizzes:
            uid = q.get("id")
            user_ans = (answers or {}).get(uid, "").strip().lower()
            correct_ans = q.get("answer", "").strip().lower()
            if user_ans == correct_ans:
                correct += 1
        strictness = cfg.get("strictness", "medium")
        if strictness == "low" and correct >= max(1, total // 2):
            return True, None
        if strictness == "medium" and correct >= max(1, total * 2 // 3):
            return True, None
        if strictness == "high" and correct == total:
            return True, None
        return False, f"Passed {correct}/{total} questions. Need {'all' if strictness == 'high' else 'most'} correct."

    def log_action(self, chat_id, action, user_id, details=""):
        if not self.get_chat(chat_id).get("log", True):
            return
        log = _load_json(GUARDIAN_LOG_FILE, [])
        log.append({"chat": str(chat_id), "action": action, "user": str(user_id), "details": details, "time": time.time()})
        if len(log) > 1000:
            log = log[-500:]
        _save_json(GUARDIAN_LOG_FILE, log)


_auto_reply = None
_guardian = None

def get_auto():
    global _auto_reply
    if _auto_reply is None:
        _auto_reply = AutoReplyConfig()
    return _auto_reply

def get_guardian():
    global _guardian
    if _guardian is None:
        _guardian = GuardianConfig()
    return _guardian
