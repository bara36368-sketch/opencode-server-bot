import json, os, time
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLL_PLUS_FILE = os.path.join(BASE_DIR, "poll_plus_data.json")

class PollPlus:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if os.path.exists(POLL_PLUS_FILE):
            try:
                with open(POLL_PLUS_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"polls": {}, "answers": []}

    def _save(self):
        with open(POLL_PLUS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def track_poll(self, poll_id, question, options, chat_id, creator_id):
        self.data["polls"][poll_id] = {
            "id": poll_id,
            "question": question,
            "options": options,
            "chat_id": chat_id,
            "creator_id": str(creator_id),
            "created": time.time(),
            "votes": {str(i): 0 for i in range(len(options))},
            "voters": {},
            "history": [],
        }
        self._save()

    def record_answer(self, poll_id, user_id, option_ids):
        poll = self.data["polls"].get(poll_id)
        if not poll:
            return
        uid = str(user_id)
        prev = poll["voters"].get(uid)
        if prev is not None:
            poll["votes"][str(prev)] = max(0, poll["votes"].get(str(prev), 0) - 1)
        for oid in option_ids:
            poll["votes"][str(oid)] = poll["votes"].get(str(oid), 0) + 1
        poll["voters"][uid] = option_ids[0] if option_ids else None
        poll.setdefault("history", []).append({
            "user_id": uid, "option_ids": option_ids, "time": time.time()
        })
        if len(poll["history"]) > 500:
            poll["history"] = poll["history"][-250:]
        self.data.setdefault("answers", []).append({
            "poll_id": poll_id, "user_id": uid,
            "option_ids": option_ids, "time": time.time()
        })
        if len(self.data["answers"]) > 2000:
            self.data["answers"] = self.data["answers"][-1000:]
        self._save()

    def get_stats(self, poll_id):
        poll = self.data["polls"].get(poll_id)
        if not poll:
            return None
        total = sum(poll["votes"].values())
        vote_pct = []
        for i, opt in enumerate(poll["options"]):
            count = poll["votes"].get(str(i), 0)
            pct = round((count / total * 100), 1) if total > 0 else 0
            bar_len = max(1, int(pct / 5))
            bar = "█" * bar_len + "░" * (20 - bar_len)
            vote_pct.append((opt, count, pct, bar))
        peak_hour = self._peak_hour(poll_id)
        return {
            "question": poll["question"],
            "total": total,
            "options": vote_pct,
            "unique_voters": len(poll["voters"]),
            "created": poll["created"],
            "peak_hour": peak_hour,
        }

    def _peak_hour(self, poll_id):
        poll = self.data["polls"].get(poll_id)
        if not poll:
            return None
        hour_counts = defaultdict(int)
        for entry in poll.get("history", []):
            dt = time.localtime(entry["time"])
            hour_counts[dt.tm_hour] += 1
        if not hour_counts:
            return None
        return max(hour_counts, key=hour_counts.get)

    def format_stats(self, poll_id):
        stats = self.get_stats(poll_id)
        if not stats:
            return None
        lines = [
            f"Poll Statistics: {stats['question'][:50]}",
            f"   Total votes: {stats['total']}",
            f"   Unique voters: {stats['unique_voters']}",
            "",
        ]
        for opt, count, pct, bar in stats["options"]:
            lines.append(f"  {bar} {opt[:30]}  {count} ({pct}%)")
        if stats["peak_hour"] is not None:
            lines.append(f"\n   Peak voting hour: {stats['peak_hour']}:00")
        return "\n".join(lines)

    def list_tracked(self, chat_id):
        return [p for p in self.data["polls"].values() if p.get("chat_id") == chat_id]

    def get_poll(self, poll_id):
        return self.data["polls"].get(poll_id)

_poll_plus = None
def get_poll_plus():
    global _poll_plus
    if _poll_plus is None:
        _poll_plus = PollPlus()
    return _poll_plus
