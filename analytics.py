import json, os, time, re
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "analytics_data.json")

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

class Analytics:
    def __init__(self):
        self.data = _load_json(DATA_FILE, defaultdict(lambda: {
            "messages": [], "members": [], "commands": defaultdict(int),
            "active_hours": defaultdict(int), "top_users": defaultdict(int),
            "daily_counts": defaultdict(int), "hourly_counts": defaultdict(int)
        }))
        if isinstance(self.data, dict) and not hasattr(self.data, "default_factory"):
            self.data = defaultdict(lambda: {
                "messages": [], "members": [], "commands": defaultdict(int),
                "active_hours": defaultdict(int), "top_users": defaultdict(int),
                "daily_counts": defaultdict(int), "hourly_counts": defaultdict(int)
            }, self.data)

    def _save(self):
        _save_json(DATA_FILE, dict(self.data))

    def track_message(self, chat_id, user_id, text, is_command=False):
        cid = str(chat_id)
        uid = str(user_id)
        now = time.time()
        hour = datetime.fromtimestamp(now, tz=timezone.utc).strftime("%Y-%m-%d %H:00")
        day = datetime.fromtimestamp(now, tz=timezone.utc).strftime("%Y-%m-%d")

        cfg = self.data[cid]
        cfg["messages"].append({"user": uid, "time": now, "cmd": is_command, "len": len(text or "")})
        if len(cfg["messages"]) > 10000:
            cfg["messages"] = cfg["messages"][-5000:]

        cfg["active_hours"][hour] = cfg["active_hours"].get(hour, 0) + 1
        cfg["daily_counts"][day] = cfg["daily_counts"].get(day, 0) + 1
        cfg["hourly_counts"][hour] = cfg["hourly_counts"].get(hour, 0) + 1
        cfg["top_users"][uid] = cfg["top_users"].get(uid, 0) + 1
        if is_command:
            cmd_name = text.split()[0].lower() if text else "unknown"
            cfg["commands"][cmd_name] = cfg["commands"].get(cmd_name, 0) + 1

        if len(cfg["daily_counts"]) > 90:
            old_days = sorted(cfg["daily_counts"].keys())[:-60]
            for d in old_days:
                del cfg["daily_counts"][d]
        self._save()

    def track_member_join(self, chat_id, user_id):
        cid = str(chat_id)
        uid = str(user_id)
        cfg = self.data[cid]
        cfg["members"].append({"user": uid, "action": "join", "time": time.time()})
        if len(cfg["members"]) > 2000:
            cfg["members"] = cfg["members"][-1000:]
        self._save()

    def track_member_leave(self, chat_id, user_id):
        cid = str(chat_id)
        uid = str(user_id)
        cfg = self.data[cid]
        cfg["members"].append({"user": uid, "action": "leave", "time": time.time()})
        if len(cfg["members"]) > 2000:
            cfg["members"] = cfg["members"][-1000:]
        self._save()

    def get_stats(self, chat_id, days=7):
        cid = str(chat_id)
        cfg = self.data.get(cid, {})
        if not cfg:
            return None
        now = time.time()
        cutoff = now - days * 86400
        period_msgs = [m for m in cfg.get("messages", []) if m["time"] > cutoff]
        period_members = [m for m in cfg.get("members", []) if m["time"] > cutoff]

        total_msgs = len(period_msgs)
        unique_users = len(set(m["user"] for m in period_msgs))
        cmds = len([m for m in period_msgs if m.get("cmd")])
        avg_len = sum(m.get("len", 0) for m in period_msgs) / max(total_msgs, 1)

        joins = len([m for m in period_members if m["action"] == "join"])
        leaves = len([m for m in period_members if m["action"] == "leave"])
        net_growth = joins - leaves

        daily_data = cfg.get("daily_counts", {})
        daily_totals = sorted(
            [(d, c) for d, c in daily_data.items() if d >= (datetime.fromtimestamp(cutoff, tz=timezone.utc).strftime("%Y-%m-%d"))],
            key=lambda x: x[0]
        )
        daily_avg = sum(c for _, c in daily_totals) / max(len(daily_totals), 1)

        hourly = cfg.get("hourly_counts", {})
        hour_buckets = defaultdict(int)
        for h, c in hourly.items():
            try:
                hh = h.split(" ")[1].split(":")[0]
                hour_buckets[int(hh)] += c
            except Exception:
                pass
        peak_hour = max(hour_buckets, key=hour_buckets.get) if hour_buckets else 12

        top = sorted(cfg.get("top_users", {}).items(), key=lambda x: -x[1])[:5]

        cmd_stats = sorted(cfg.get("commands", {}).items(), key=lambda x: -x[1])[:5]

        monday = datetime.fromtimestamp(cutoff, tz=timezone.utc)
        growth_rate = ((joins - leaves) / max(unique_users, 1)) * 100 if unique_users > 0 else 0

        return {
            "period_days": days,
            "total_messages": total_msgs,
            "unique_users": unique_users,
            "commands_used": cmds,
            "avg_msg_length": round(avg_len, 1),
            "joins": joins,
            "leaves": leaves,
            "net_growth": net_growth,
            "growth_rate": round(growth_rate, 1),
            "daily_avg": round(daily_avg, 1),
            "peak_hour": peak_hour,
            "top_users": [(u, c) for u, c in top],
            "top_commands": [(u, c) for u, c in cmd_stats]
        }

    def format_stats(self, chat_id, days=7):
        s = self.get_stats(chat_id, days)
        if not s:
            return "No analytics data for this chat yet."
        lines = [
            f"📊 Analytics (last {s['period_days']}d):",
            f"  Messages: {s['total_messages']} ({s['daily_avg']}/day avg)",
            f"  Unique users: {s['unique_users']}",
            f"  Commands: {s['commands_used']} ({s['avg_msg_length']} chars/msg avg)",
            f"  Growth: +{s['joins']}/-{s['leaves']} = {s['net_growth']:+,d} ({s['growth_rate']}%)",
            f"  Peak hour: {s['peak_hour']}:00 UTC",
        ]
        if s["top_users"]:
            lines.append(f"  Top users: {', '.join(f'ID {u}({c})' for u, c in s['top_users'][:3])}")
        if s["top_commands"]:
            lines.append(f"  Top commands: {', '.join(f'{c}({n})' for c, n in s['top_commands'][:3])}")
        return "\n".join(lines)

    def format_daily(self, chat_id, days=7):
        cid = str(chat_id)
        cfg = self.data.get(cid, {})
        daily = cfg.get("daily_counts", {})
        cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        relevant = sorted([(d, c) for d, c in daily.items() if d >= cutoff], key=lambda x: x[0])
        if not relevant:
            return "No daily data."
        spark = "▁▂▃▄▅▆▇█"
        counts = [c for _, c in relevant]
        mx = max(counts) if counts else 1
        bars = []
        for d, c in relevant[-14:]:
            idx = min(int(c / mx * (len(spark) - 1)), len(spark) - 1)
            bars.append(f"  {d}: {spark[idx]} {c}")
        return "Daily activity:\n" + "\n".join(bars)

_analytics = None
def get_analytics():
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics
