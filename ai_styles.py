import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLES_FILE = os.path.join(BASE_DIR, "ai_styles.json")

PRESETS = {
    "teacher": "You are a knowledgeable teacher. Explain concepts clearly, use examples, and encourage learning. Be patient and supportive.",
    "friendly": "You are a friendly and casual companion. Use a warm, conversational tone. Be approachable and use everyday language.",
    "professional": "You are a professional consultant. Be formal, precise, and efficient. Use proper terminology and stay on topic.",
    "concise": "You are a concise assistant. Give short, direct answers. No fluff, no extra explanations unless asked. Bullet points preferred.",
    "poetic": "You are a poetic writer. Respond with elegance and creativity. Use metaphors, imagery, and expressive language.",
    "mentor": "You are an experienced mentor. Guide the user with wisdom, ask probing questions, and help them discover answers themselves.",
    "socratic": "You are a Socratic questioner. Don't give direct answers. Instead, ask questions that lead the user to their own conclusions.",
    "comedian": "You are a witty comedian. Use humor, puns, and light-hearted jokes. Keep responses entertaining while still being helpful.",
}

class AIStyles:
    def __init__(self):
        self.styles = self._load()

    def _load(self):
        if os.path.exists(STYLES_FILE):
            try:
                with open(STYLES_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save(self):
        with open(STYLES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.styles, f, indent=2, ensure_ascii=False)

    def get_active(self, uid):
        uid = str(uid)
        return self.styles.get(uid, {}).get("active")

    def get_style_text(self, uid, name=None):
        uid = str(uid)
        user = self.styles.setdefault(uid, {"active": None, "custom": {}, "presets": {}})
        if name:
            c = user["custom"].get(name)
            p = user["presets"].get(name) or PRESETS.get(name)
            return c or p
        active = user.get("active")
        if active:
            return user["custom"].get(active) or user["presets"].get(active) or PRESETS.get(active)
        return None

    def set_active(self, uid, name):
        uid = str(uid)
        user = self.styles.setdefault(uid, {"active": None, "custom": {}, "presets": {}})
        if name is None:
            user["active"] = None
            self._save()
            return True
        if name in user["custom"] or name in user["presets"] or name in PRESETS:
            user["active"] = name
            self._save()
            return True
        return False

    def create_custom(self, uid, name, text):
        uid = str(uid)
        user = self.styles.setdefault(uid, {"active": None, "custom": {}, "presets": {}})
        user["custom"][name] = text
        self._save()
        return True

    def delete_style(self, uid, name):
        uid = str(uid)
        user = self.styles.get(uid)
        if not user:
            return False
        if name in user.get("custom", {}):
            del user["custom"][name]
            if user.get("active") == name:
                user["active"] = None
            self._save()
            return True
        return False

    def list_styles(self, uid):
        uid = str(uid)
        user = self.styles.get(uid, {"active": None, "custom": {}, "presets": {}})
        all_styles = {}
        for pname in PRESETS:
            all_styles[pname] = ("preset", PRESETS[pname][:60])
        for cname, ctext in user.get("custom", {}).items():
            all_styles[cname] = ("custom", ctext[:60])
        active = user.get("active")
        return all_styles, active

_ai_styles = None
def get_ai_styles():
    global _ai_styles
    if _ai_styles is None:
        _ai_styles = AIStyles()
    return _ai_styles
