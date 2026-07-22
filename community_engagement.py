import json, os, time, re, hashlib
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMUNITY_FILE = os.path.join(BASE_DIR, "community_engagement.json")

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

class CommunityEngagement:
    def __init__(self):
        self.config = _load_json(COMMUNITY_FILE, {})

    def _save(self):
        _save_json(COMMUNITY_FILE, self.config)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "reaction_roles": {},
                "welcome_enabled": False,
                "welcome_template": "Welcome {name} to {group}!",
                "welcome_image_url": None,
                "server_builder_enabled": False,
            }
        return self.config[cid]

    def toggle(self, chat_id):
        cfg = self.get_chat(chat_id)
        cfg["enabled"] = not cfg.get("enabled", False)
        self._save()
        return cfg["enabled"]

    def add_reaction_role(self, chat_id, message_id, emoji, role_name):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        mr = cfg.setdefault("reaction_roles", {})
        msg_key = str(message_id)
        if msg_key not in mr:
            mr[msg_key] = {}
        mr[msg_key][emoji] = {"role": role_name, "created": time.time()}
        self._save()
        return f"Reaction role added: {emoji} → {role_name}"

    def remove_reaction_role(self, chat_id, message_id, emoji):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        mr = cfg.get("reaction_roles", {})
        msg_key = str(message_id)
        if msg_key in mr and emoji in mr[msg_key]:
            del mr[msg_key][emoji]
            if not mr[msg_key]:
                del mr[msg_key]
            self._save()
            return f"Reaction role removed: {emoji}"
        return "Reaction role not found"

    def get_reaction_roles(self, chat_id, message_id=None):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        mr = cfg.get("reaction_roles", {})
        if message_id:
            return mr.get(str(message_id), {})
        return mr

    def handle_reaction(self, chat_id, message_id, emoji, user_id):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        if not cfg.get("enabled"):
            return None
        mr = cfg.get("reaction_roles", {})
        msg_key = str(message_id)
        if msg_key in mr and emoji in mr[msg_key]:
            role_info = mr[msg_key][emoji]
            return {
                "action": "assign_role",
                "role": role_info["role"],
                "user_id": user_id,
                "emoji": emoji,
            }
        return None

    def handle_remove_reaction(self, chat_id, message_id, emoji, user_id):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        if not cfg.get("enabled"):
            return None
        mr = cfg.get("reaction_roles", {})
        msg_key = str(message_id)
        if msg_key in mr and emoji in mr[msg_key]:
            role_info = mr[msg_key][emoji]
            return {
                "action": "remove_role",
                "role": role_info["role"],
                "user_id": user_id,
                "emoji": emoji,
            }
        return None

    def set_welcome(self, chat_id, template=None, image_url=None, enabled=None):
        cid = str(chat_id)
        cfg = self.get_chat(cid)
        if template is not None:
            cfg["welcome_template"] = template
        if image_url is not None:
            cfg["welcome_image_url"] = image_url
        if enabled is not None:
            cfg["welcome_enabled"] = enabled
        self._save()
        return "Welcome configured"

    def get_welcome(self, chat_id):
        cfg = self.get_chat(chat_id)
        return {
            "enabled": cfg.get("welcome_enabled", False),
            "template": cfg.get("welcome_template", "Welcome {name}!"),
            "image_url": cfg.get("welcome_image_url"),
        }

    def format_welcome(self, chat_id, user_name, group_name=None):
        cfg = self.get_chat(chat_id)
        template = cfg.get("welcome_template", "Welcome {name}!")
        text = template.replace("{name}", user_name)
        if group_name:
            text = text.replace("{group}", group_name)
        text = text.replace("{time}", datetime.now(timezone.utc).strftime("%H:%M UTC"))
        text = text.replace("{date}", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        return text

    def generate_welcome_image_url(self, chat_id, user_name, style="default"):
        canvas_bg = {
            "default": "#1a1a2e",
            "ocean": "#0a3d62",
            "sunset": "#e55039",
            "forest": "#1e8449",
            "purple": "#6c3483",
        }
        bg = canvas_bg.get(style, canvas_bg["default"])
        encoded_name = user_name.replace(" ", "+")
        url = f"https://placehold.co/800x400/{bg[1:]}/ffffff?text=Welcome+{encoded_name}"
        return url

    def generate_server_plan(self, prompt):
        prompt_lower = prompt.lower()
        channels = []
        roles = []
        if any(w in prompt_lower for w in ["dev", "code", "programming", "hack"]):
            channels.extend([
                {"name": "general", "type": "text"},
                {"name": "help", "type": "text"},
                {"name": "showcase", "type": "text"},
                {"name": "resources", "type": "text"},
                {"name": "voice-hangout", "type": "voice"},
            ])
            roles.extend(["Admin", "Moderator", "Developer", "Member"])
        elif any(w in prompt_lower for w in ["gaming", "game", "esport", "clan"]):
            channels.extend([
                {"name": "lobby", "type": "text"},
                {"name": "lfg", "type": "text"},
                {"name": "clips", "type": "text"},
                {"name": "voice-general", "type": "voice"},
                {"name": "voice-gaming", "type": "voice"},
            ])
            roles.extend(["Admin", "Moderator", "Leader", "Member"])
        elif any(w in prompt_lower for w in ["business", "startup", "company", "team"]):
            channels.extend([
                {"name": "announcements", "type": "text"},
                {"name": "general", "type": "text"},
                {"name": "projects", "type": "text"},
                {"name": "resources", "type": "text"},
                {"name": "standup", "type": "text"},
                {"name": "voice-meetings", "type": "voice"},
            ])
            roles.extend(["Owner", "Admin", "Manager", "Team Member", "Member"])
        elif any(w in prompt_lower for w in ["study", "school", "university", "learn"]):
            channels.extend([
                {"name": "general", "type": "text"},
                {"name": "homework-help", "type": "text"},
                {"name": "resources", "type": "text"},
                {"name": "study-group", "type": "text"},
                {"name": "voice-study", "type": "voice"},
            ])
            roles.extend(["Admin", "Moderator", "Tutor", "Student"])
        else:
            channels.extend([
                {"name": "general", "type": "text"},
                {"name": "off-topic", "type": "text"},
                {"name": "media", "type": "text"},
                {"name": "voice-chat", "type": "voice"},
            ])
            roles.extend(["Admin", "Moderator", "Member"])
        permissions = {
            "Admin": ["all"],
            "Moderator": ["ban", "kick", "delete", "mute"],
            "Member": ["send_messages", "send_media", "add_members"],
        }
        rules = [
            "Be respectful to all members",
            "No spam or self-promotion",
            "No NSFW content",
            "Use English or provide translations",
            "Follow Telegram ToS",
        ]
        return {
            "channels": channels,
            "roles": roles,
            "permissions": permissions,
            "rules": rules,
            "welcome_message": f"Welcome to {prompt[:50]}! Please read the rules and enjoy your stay.",
        }

    def format_server_plan(self, plan):
        lines = ["📋 Server Plan:", ""]
        lines.append(f"Channels ({len(plan['channels'])}):")
        for ch in plan["channels"]:
            icon = "🔊" if ch["type"] == "voice" else "💬"
            lines.append(f"  {icon} #{ch['name']}")
        lines.append("")
        lines.append(f"Roles ({len(plan['roles'])}):")
        for role in plan["roles"]:
            perms = plan.get("permissions", {}).get(role, [])
            lines.append(f"  👤 {role}: {', '.join(perms) if perms else 'basic'}")
        lines.append("")
        lines.append("Rules:")
        for i, rule in enumerate(plan.get("rules", []), 1):
            lines.append(f"  {i}. {rule}")
        return "\n".join(lines)

    def format_config(self, chat_id):
        cfg = self.get_chat(chat_id)
        rr = cfg.get("reaction_roles", {})
        total_reactions = sum(len(msg) for msg in rr.values())
        lines = [
            f"Community: {'ON' if cfg.get('enabled') else 'OFF'}",
            f"  Reaction Roles: {total_reactions} configured ({len(rr)} messages)",
            f"  Welcome: {'ON' if cfg.get('welcome_enabled') else 'OFF'}",
            f"  Server Builder: {'ON' if cfg.get('server_builder_enabled') else 'OFF'}",
        ]
        return "\n".join(lines)

_community = None
def get_community():
    global _community
    if _community is None:
        _community = CommunityEngagement()
    return _community
