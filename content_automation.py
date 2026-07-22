import json, os, time, asyncio, re, hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "content_automation.json")
CACHE_FILE = os.path.join(BASE_DIR, "content_cache.json")

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

class ContentAutomation:
    def __init__(self):
        self.configs = _load_json(CONFIG_FILE, {})
        self.cache = _load_json(CACHE_FILE, {})

    def _save(self):
        _save_json(CONFIG_FILE, self.configs)

    def _save_cache(self):
        _save_json(CACHE_FILE, self.cache)

    def add_feed(self, chat_id, url, label=None, filter_keywords=None, max_per_day=5, schedule_minutes=60):
        cid = str(chat_id)
        if cid not in self.configs:
            self.configs[cid] = {"enabled": False, "feeds": [], "channel_id": None, "schedule": {}}
        fid = hashlib.md5(url.encode()).hexdigest()[:8]
        self.configs[cid]["feeds"].append({
            "id": fid, "url": url, "label": label or url,
            "filter_keywords": filter_keywords or [],
            "max_per_day": max_per_day, "schedule_minutes": schedule_minutes,
            "last_checked": 0, "last_posted": []
        })
        self._save()
        return fid

    def remove_feed(self, chat_id, feed_id):
        cid = str(chat_id)
        if cid in self.configs:
            self.configs[cid]["feeds"] = [f for f in self.configs[cid].get("feeds", []) if f.get("id") != feed_id]
            self._save()

    def set_channel(self, chat_id, channel_id):
        cid = str(chat_id)
        if cid not in self.configs:
            self.configs[cid] = {"enabled": False, "feeds": [], "channel_id": None, "schedule": {}}
        self.configs[cid]["channel_id"] = channel_id
        self._save()

    def toggle(self, chat_id):
        cid = str(chat_id)
        if cid not in self.configs:
            self.configs[cid] = {"enabled": False, "feeds": [], "channel_id": None, "schedule": {}}
        self.configs[cid]["enabled"] = not self.configs[cid].get("enabled", False)
        self._save()
        return self.configs[cid]["enabled"]

    def get_config(self, chat_id):
        cid = str(chat_id)
        return self.configs.get(cid, {"enabled": False, "feeds": [], "channel_id": None, "schedule": {}})

    async def fetch_feed(self, url, timeout=15):
        try:
            import httpx
            c = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
            resp = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
            await c.aclose()
            if resp.status_code != 200:
                return None
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            entries = []
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                e = {}
                title_el = entry.find("{http://www.w3.org/2005/Atom}title")
                if title_el is not None: e["title"] = title_el.text
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                if link_el is not None: e["link"] = link_el.get("href", "")
                summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
                if summary_el is not None: e["summary"] = summary_el.text
                content_el = entry.find("{http://www.w3.org/2005/Atom}content")
                if content_el is not None: e["content"] = content_el.text
                id_el = entry.find("{http://www.w3.org/2005/Atom}id")
                if id_el is not None: e["id"] = id_el.text
                updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
                if updated_el is not None: e["updated"] = updated_el.text
                entries.append(e)
            if not entries:
                for item in root.iter("item"):
                    e = {}
                    t = item.find("title")
                    if t is not None: e["title"] = t.text
                    l = item.find("link")
                    if l is not None: e["link"] = l.text if not l.get("href") else l.get("href")
                    d = item.find("description")
                    if d is not None: e["summary"] = d.text
                    g = item.find("guid")
                    if g is not None: e["id"] = g.text
                    pub = item.find("pubDate")
                    if pub is not None: e["updated"] = pub.text
                    entries.append(e)
            return entries
        except Exception:
            return None

    async def check_feeds(self, chat_id, smart_call=None):
        cid = str(chat_id)
        cfg = self.get_config(cid)
        if not cfg.get("enabled") or not cfg.get("feeds"):
            return []
        now = time.time()
        new_items = []
        for feed in cfg["feeds"]:
            if now - feed.get("last_checked", 0) < feed.get("schedule_minutes", 60) * 60:
                continue
            feed["last_checked"] = now
            entries = await self.fetch_feed(feed["url"])
            if not entries:
                continue
            cached_ids = self.cache.get(cid, {}).get(feed["id"], set())
            posted_ids = set(feed.get("last_posted", []))
            for entry in entries:
                eid = entry.get("id") or entry.get("link") or hashlib.md5((entry.get("title", "") + entry.get("link", "")).encode()).hexdigest()
                if eid in cached_ids or eid in posted_ids:
                    continue
                keywords = feed.get("filter_keywords", [])
                if keywords:
                    text = (entry.get("title", "") + " " + (entry.get("summary", "") or "")).lower()
                    if not any(k.lower() in text for k in keywords):
                        continue
                new_items.append({"feed_id": feed["id"], "feed_url": feed["url"], "entry": entry, "id": eid})
                if cid not in self.cache:
                    self.cache[cid] = {}
                if feed["id"] not in self.cache[cid]:
                    self.cache[cid][feed["id"]] = []
                self.cache[cid][feed["id"]].append(eid)
                posted = feed.get("last_posted", [])
                posted.append(eid)
                if len(posted) > feed.get("max_per_day", 5) * 3:
                    posted = posted[-feed.get("max_per_day", 5) * 3:]
                feed["last_posted"] = posted
            self._save_cache()
        self._save()
        if new_items and smart_call:
            scored = []
            for item in new_items:
                entry = item["entry"]
                text = f"Title: {entry.get('title', '')}\nSummary: {(entry.get('summary', '') or '')[:500]}"
                score_text = await smart_call([
                    {"role": "system", "content": "Rate relevance 0-10 for a Telegram channel audience. Only respond with a number."},
                    {"role": "user", "content": text[:1500]}
                ], "groq")
                try:
                    score = max(0, min(10, int(re.search(r'\d+', score_text or "5").group())))
                except Exception:
                    score = 5
                item["score"] = score
                scored.append(item)
            scored.sort(key=lambda x: -x["score"])
            return scored[:5]
        return new_items[:5]

    async def generate_post(self, item, smart_call=None):
        entry = item["entry"]
        title = entry.get("title", "Untitled")
        summary = (entry.get("summary", "") or "")[:800]
        link = entry.get("link", "")
        if smart_call:
            post = await smart_call([
                {"role": "system", "content": "Write a short Telegram post (2-3 sentences) announcing this content. Be engaging, add emojis, include the link. Keep under 400 chars."},
                {"role": "user", "content": f"Title: {title}\nSummary: {summary[:600]}\nLink: {link}"}
            ], "groq")
            return post[:1500] if post else f"**{title}**\n\n{link}"
        return f"**{title}**\n\n{summary[:300]}\n\n{link}"

    def get_status(self, chat_id):
        cfg = self.get_config(chat_id)
        if not cfg.get("feeds"):
            return "Content Automation: No feeds configured.\nUse /content add <url> to add an RSS/Atom feed."
        lines = [f"Content Automation: {'ON' if cfg.get('enabled') else 'OFF'}"]
        lines.append(f"Channel: {cfg.get('channel_id', 'not set')}")
        lines.append(f"Feeds ({len(cfg['feeds'])}):")
        for f in cfg["feeds"]:
            status = "active" if time.time() - f.get("last_checked", 0) < f.get("schedule_minutes", 60) * 60 * 2 else "pending"
            lines.append(f"  [{f['id']}] {f['label']} ({status}, every {f.get('schedule_minutes', 60)}m)")
        return "\n".join(lines)

_ca = None
def get_ca():
    global _ca
    if _ca is None:
        _ca = ContentAutomation()
    return _ca
