"""Telegram Mini Apps module — serves a web dashboard inside Telegram."""
import os, json, time, hashlib, hmac, urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MINI_APP_FILE = os.path.join(BASE_DIR, "mini_app_data.json")

class MiniAppManager:
    def __init__(self):
        self.data = self._load()
        self.enabled = False
        self.menu_url = ""
        self.app_pages = {}

    def _load(self):
        if os.path.exists(MINI_APP_FILE):
            try:
                with open(MINI_APP_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"pages": {}, "stats": {}, "web_app_data": []}

    def _save(self):
        tmp = MINI_APP_FILE + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, MINI_APP_FILE)
        except Exception:
            pass

    def record_web_app_data(self, user_id, chat_id, data):
        self.data["web_app_data"].append({
            "user_id": user_id,
            "chat_id": chat_id,
            "data": data[:2000],
            "ts": time.time()
        })
        if len(self.data["web_app_data"]) > 500:
            self.data["web_app_data"] = self.data["web_app_data"][-250:]
        self._save()

    def get_stats(self):
        return {
            "total_submissions": len(self.data.get("web_app_data", [])),
            "pages": list(self.data.get("pages", {}).keys()),
            "enabled": self.enabled,
            "menu_url": self.menu_url,
        }

    def register_page(self, page_id, title, url):
        self.data.setdefault("pages", {})[page_id] = {
            "title": title, "url": url, "created": time.time()
        }
        self._save()

    def list_pages(self):
        return self.data.get("pages", {})

    def track_open(self, user_id):
        key = str(user_id)
        self.data.setdefault("stats", {}).setdefault("opens", {})
        self.data["stats"]["opens"][key] = self.data["stats"]["opens"].get(key, 0) + 1
        self._save()

_mini_app = None
def get_mini_app():
    global _mini_app
    if _mini_app is None:
        _mini_app = MiniAppManager()
    return _mini_app

# ---------------------------------------------------------------------------
# HTML for the Mini App dashboard
# ---------------------------------------------------------------------------
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>OpenCode Bot</title>
<script src="https://telegram.org/js/telegram-web-app.js?63"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:var(--tg-theme-bg-color,#fff);color:var(--tg-theme-text-color,#000);
padding:16px;min-height:100vh}
h1{font-size:22px;margin-bottom:12px;color:var(--tg-theme-text-color,#000)}
.card{background:var(--tg-theme-secondary-bg-color,#f0f2f5);border-radius:12px;
padding:16px;margin-bottom:12px}
.card h2{font-size:16px;margin-bottom:8px}
.card p{font-size:14px;opacity:0.8;line-height:1.4}
.stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.stat-box{background:var(--tg-theme-button-color,#3390ec);color:var(--tg-theme-button-text-color,#fff);
border-radius:12px;padding:16px;text-align:center}
.stat-box .num{font-size:28px;font-weight:700}
.stat-box .label{font-size:12px;opacity:0.8}
.btn{display:block;width:100%;padding:14px;border:none;border-radius:12px;
font-size:16px;font-weight:600;cursor:pointer;margin-bottom:8px;
background:var(--tg-theme-button-color,#3390ec);color:var(--tg-theme-button-text-color,#fff)}
.btn:active{opacity:0.8}
.btn-secondary{background:var(--tg-theme-secondary-bg-color,#f0f2f5);
color:var(--tg-theme-text-color,#000)}
input,textarea{width:100%;padding:12px;border:1px solid var(--tg-theme-hint-color,#999);
border-radius:8px;font-size:14px;background:var(--tg-theme-bg-color,#fff);
color:var(--tg-theme-text-color,#000);margin-bottom:8px}
textarea{min-height:80px;resize:vertical}
.label{font-size:13px;opacity:0.7;margin-bottom:4px;display:block}
.section-title{font-size:14px;font-weight:600;margin:16px 0 8px;opacity:0.6;text-transform:uppercase}
.user-info{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.user-info img{width:48px;height:48px;border-radius:50%}
.user-info .name{font-weight:600;font-size:16px}
.user-info .id{font-size:12px;opacity:0.5}
.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
.quick-btn{padding:12px;border-radius:10px;border:none;cursor:pointer;font-size:13px;font-weight:500;
background:var(--tg-theme-secondary-bg-color,#f0f2f5);color:var(--tg-theme-text-color,#000);text-align:center}
</style>
</head>
<body>
<div id="app">
<div class="user-info" id="userInfo"></div>
<div class="stats-grid" id="statsGrid"></div>
<div class="section-title">Quick Actions</div>
<div class="quick-actions" id="quickActions"></div>
<div class="section-title">Send Data to Bot</div>
<div class="card">
<label class="label">Message</label>
<textarea id="msgInput" placeholder="Type a message to send to the bot..."></textarea>
<button class="btn" onclick="sendData()">Send to Bot</button>
</div>
<div class="section-title">About</div>
<div class="card">
<h2>OpenCode Bot Mini App</h2>
<p>Full web interface running inside Telegram. Control your bot, view stats, and interact — all without leaving the chat.</p>
</div>
</div>
<script>
const tg=window.Telegram?.WebApp;
if(tg){tg.ready();tg.expand();document.body.style.background=tg.themeParams?.bg_color||'#fff'}
const user=tg?.initDataUnsafe?.user;
const el=document.getElementById('userInfo');
if(user){el.innerHTML=`<img src="${user.photo_url||'https://ui-avatars.com/api/?name='+encodeURIComponent(user.first_name)}" alt=""><div><div class="name">${user.first_name}${user.last_name?' '+user.last_name:''}</div><div class="id">ID: ${user.id}${user.username?' @'+user.username:''}</div></div>`}
document.getElementById('statsGrid').innerHTML=`
<div class="stat-box"><div class="num">v3.3</div><div class="label">Bot Version</div></div>
<div class="stat-box"><div class="num">${user?'Online':'Guest'}</div><div class="label">Status</div></div>`;
document.getElementById('quickActions').innerHTML=`
<button class="quick-btn" onclick="sendCmd('/status')">/status</button>
<button class="quick-btn" onclick="sendCmd('/agents')">/agents</button>
<button class="quick-btn" onclick="sendCmd('/providers')">/providers</button>
<button class="quick-btn" onclick="sendCmd('/version')">/version</button>`;
function sendCmd(c){if(tg){tg.sendData(c);tg.close()}else{alert('Open in Telegram to use')}}
function sendData(){const m=document.getElementById('msgInput').value.trim();if(!m)return;if(tg){tg.sendData(m);document.getElementById('msgInput').value='';tg.close()}else{alert('Open in Telegram to send')}}
</script>
</body>
</html>"""

def get_dashboard_html():
    return DASHBOARD_HTML

def get_menu_button_text():
    return "🚀 OpenCode Bot"

def get_menu_button_url(webapp_url):
    return webapp_url

def validate_init_data(init_data, bot_token):
    """Validate Telegram Mini App initData (HMAC-SHA256)."""
    try:
        parsed = urllib.parse.parse_qs(init_data)
        hash_val = parsed.get("hash", [""])[0]
        if not hash_val:
            return False, {}
        data_check = sorted([f"{k}={v[0]}" for k, v in parsed.items() if k != "hash"])
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret_key, "\n".join(data_check).encode(), hashlib.sha256).hexdigest()
        if calculated != hash_val:
            return False, {}
        user_data = {}
        if "user" in parsed:
            user_data = json.loads(parsed["user"][0])
        return True, user_data
    except Exception:
        return False, {}

def handle_mini_app_command(parts, uid, is_owner):
    """Handle /miniapp commands. Returns (action, data) or (None, None)."""
    if len(parts) < 2:
        return "help", {}
    sub = parts[1].lower()
    if sub == "status":
        ma = get_mini_app()
        return "status", ma.get_stats()
    elif sub == "pages":
        ma = get_mini_app()
        return "pages", ma.list_pages()
    elif sub == "data":
        ma = get_mini_app()
        return "data", {"count": len(ma.data.get("web_app_data", []))}
    elif sub == "url" and is_owner:
        if len(parts) >= 3:
            ma = get_mini_app()
            ma.menu_url = parts[2]
            ma._save()
            return "url_set", {"url": parts[2]}
    return "help", {}

def format_mini_app_response(action, data):
    if action == "help":
        return (
            "📱 Mini Apps (Telegram Web Apps)\\n\\n"
            "Commands:\\n"
            "  /miniapp status — View mini app stats\\n"
            "  /miniapp pages — List registered pages\\n"
            "  /miniapp data — View received web_app_data count\\n"
            "  /miniapp url <url> — Set menu button URL (owner only)\\n\\n"
            "How to use:\\n"
            "1. Add a web_app inline button to any message\\n"
            "2. The mini app opens inside Telegram\\n"
            "3. User can send data back to bot via sendData()\\n"
            "4. Bot receives it as a message with web_app_data"
        )
    elif action == "status":
        return (
            f"📱 Mini App Status\\n\\n"
            f"Enabled: {'Yes' if data.get('enabled') else 'No'}\\n"
            f"Menu URL: {data.get('menu_url') or 'Not set'}\\n"
            f"Pages: {len(data.get('pages', []))}\\n"
            f"Submissions: {data.get('total_submissions', 0)}"
        )
    elif action == "pages":
        pages = data
        if not pages:
            return "📱 No pages registered. Use /miniapp url <url> to set one."
        lines = ["📱 Registered Pages:\\n"]
        for pid, pinfo in pages.items():
            lines.append(f"  • {pinfo['title']} — {pinfo['url']}")
        return "\\n".join(lines)
    elif action == "data":
        return f"📱 {data.get('count', 0)} web_app_data submissions received"
    elif action == "url_set":
        return f"📱 Menu button URL set to: {data.get('url')}"
    return ""
