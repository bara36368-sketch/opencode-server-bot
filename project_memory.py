"""Local-first agent memory layer (projectmem/OptMem-inspired).

Typed, append-only event log (issues / attempts / fixes / decisions / notes)
stored as plain JSONL under .projectmem/ inside the bot repo. Distilled into
compact AI-readable summaries so long-running bots stop re-explaining the
same failures. Provides:

  * log_event(kind, summary, **meta)     - append a typed event
  * search_events(query)                 - grep over the raw log
  * get_brief()                          - session-start briefing
  * get_compact_context(tokens=800)      - OptMem-style compact memory block
  * precheck_file(path)                  - warn before repeating a failure

Import-safe: no side effects, no network, stdlib only.
"""
import json
import os
import re
import time

PMEM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".projectmem")
EVENTS_FILE = os.path.join(PMEM_DIR, "events.jsonl")
SUMMARY_FILE = os.path.join(PMEM_DIR, "summary.json")

_KINDS = ("issue", "attempt", "fix", "decision", "note")

_MAX_RAW = 2000


def _now():
    return time.time()


def _fmt(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def _ensure_dir():
    try:
        os.makedirs(PMEM_DIR, exist_ok=True)
    except OSError:
        pass


def log_event(kind, summary, **meta):
    """Append a typed event. kind in {issue, attempt, fix, decision, note}.
    `outcome` (failed/partial/worked) and `file` are common meta fields.
    Identical repeats within DEDUP_SECONDS are collapsed into a count."""
    kind = kind.lower()
    if kind not in _KINDS:
        kind = "note"
    key = str(summary)[:200].lower()
    now = _now()
    rows = _load_events()
    if rows and _DEDUP_SECONDS > 0:
        last = rows[-1]
        if (last.get("kind") == kind
                and str(last.get("summary", ""))[:200].lower() == key
                and now - float(last.get("ts", 0)) < _DEDUP_SECONDS):
            last["count"] = int(last.get("count", 1)) + 1
            last["ts"] = now
            last["time"] = _fmt(now)
            _rewrite_events(rows)
            _rebuild_summary()
            return last
    row = {"ts": now, "time": _fmt(now), "kind": kind,
           "summary": str(summary)[:1000]}
    row.update({k: (v[:1000] if isinstance(v, str) else v) for k, v in meta.items()})
    _ensure_dir()
    try:
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass
    _rebuild_summary()
    return row


_DEDUP_SECONDS = 120


def _rewrite_events(rows):
    _ensure_dir()
    try:
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def pinned():
    """Events flagged pin:true (priority decisions immune to trimming)."""
    return [r for r in reversed(_load_events()) if r.get("pin")]


def export_memory():
    """Return the full event log as a list of dicts (for backup/migration)."""
    return _load_events()


def import_memory(rows):
    """Append exported events (export_memory output) back into the log.
    Returns number of events appended."""
    added = 0
    _ensure_dir()
    try:
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            for row in rows:
                if isinstance(row, dict) and row.get("summary"):
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    added += 1
    except Exception:
        pass
    if added:
        _rebuild_summary()
    return added


def _load_events(limit=None):
    rows = []
    try:
        with open(EVENTS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return rows[-limit:] if limit else rows


def search_events(query, limit=20):
    """Plain-text search over the raw event log (projectmem `search`)."""
    q = query.lower()
    hits = []
    for row in reversed(_load_events()):
        blob = json.dumps(row, ensure_ascii=False).lower()
        if q in blob:
            hits.append(row)
            if len(hits) >= limit:
                break
    return hits


def failed_approaches(file=None):
    """All failed/partial attempts + issues, newest first — the "Do NOT retry"
    list. `precheck_file` warns when a target file appears in here."""
    out = []
    for row in reversed(_load_events()):
        if row.get("kind") == "issue":
            out.append(row)
        elif row.get("kind") == "attempt" and row.get("outcome") in ("failed", "partial"):
            out.append(row)
        elif row.get("kind") == "fix" and row.get("outcome") == "failed":
            out.append(row)
    if file:
        out = [r for r in out
               if file in str(r.get("file", "")) or file in str(r.get("path", ""))]
    return out[:50]


def precheck_file(path):
    """projectmem `precheck_file`: surface failure history for a file before
    a bot edits it. Returns list of warning strings (empty = all clear)."""
    fname = os.path.basename(path) if isinstance(path, str) else ""
    warns = []
    for row in failed_approaches(file=fname):
        kind = row.get("kind")
        label = {"issue": "OPEN ISSUE", "attempt": "FAILED ATTEMPT",
                 "fix": "FAILED FIX"}.get(kind, kind.upper())
        when = row.get("time", "")
        warns.append(f"  {label}: {row.get('summary', '')[:180]} ({when})")
    if warns:
        warns.insert(0, f"WARN — {fname}: repeated failures on record:")
    return warns


def get_stats():
    rows = _load_events()
    counts = {}
    for r in rows:
        counts[r.get("kind", "?")] = counts.get(r.get("kind", "?"), 0) + 1
    return {"total": len(rows), "by_kind": counts,
            "failed": sum(1 for r in rows if r.get("outcome") in ("failed", "partial"))}


def get_brief():
    """One-screen session-start briefing: open issues, dead ends, decisions,
    recent notes. projectmem `brief`."""
    rows = _load_events()
    if not rows:
        return "No project memory yet. Use /pmem to log issues, fixes and decisions."
    lines = [f"Project memory ({len(rows)} events, {_fmt(rows[-1]['ts'])} latest)", ""]
    open_issues = [r for r in reversed(rows) if r.get("kind") == "issue"]
    if open_issues:
        lines.append(f"Open issues ({len(open_issues)}):")
        for r in open_issues[:6]:
            lines.append(f"  • {r.get('summary','')[:160]}")
        lines.append("")
    dead = failed_approaches()
    if dead:
        lines.append(f"Do NOT retry ({len(dead)} failures):")
        for r in dead[:6]:
            lines.append(f"  ✗ [{r.get('kind')}] {r.get('summary','')[:160]}")
        lines.append("")
    decisions = [r for r in reversed(rows) if r.get("kind") == "decision"]
    if decisions:
        lines.append(f"Decisions ({len(decisions)}):")
        for r in decisions[:6]:
            lines.append(f"  ✓ {r.get('summary','')[:160]}")
    return "\n".join(lines)


def get_compact_context(tokens=800):
    """OptMem-style compact permanent-memory block, token-budgeted. Meant to
    be injected into a system prompt so a fresh session starts 'experienced'."""
    brief = get_brief()
    if not brief or brief.startswith("No project memory"):
        return ""
    budget_chars = max(400, tokens * 4)
    if len(brief) > budget_chars:
        brief = brief[:budget_chars] + "…"
    return ("[Permanent project memory — from the .projectmem event log. "
            "These are typed, append-only records of what was tried, what "
            "failed, and what was decided. Respect the 'Do NOT retry' list.]\n"
            + brief)


def _rebuild_summary():
    try:
        stats = get_stats()
        data = {"updated": _fmt(time.time()), "stats": stats}
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _cmd_brief():
    print(get_brief())


def _cmd_log(kind, text):
    row = log_event(kind, text)
    print(f"logged {kind}: {row.get('summary','')[:120]}")


def _cmd_search(query):
    for row in search_events(query):
        print(f"[{row.get('time','')}] {row.get('kind','?'):<8} {row.get('summary','')[:180]}")


def _cmd_precheck(path):
    warns = precheck_file(path)
    if not warns:
        print(f"{path}: all clear")
    else:
        print("\n".join(warns))


_USAGE = """project_memory.py — local-first agent memory (.projectmem/)

Commands:
  brief                 Session-start briefing
  log <kind> <text>     kind: issue|attempt|fix|decision|note
  search <query>        Search the raw event log
  precheck <file>       Failure history warnings for a file
  stats                 Event counts by kind
  export                Dump full event log as JSON
  pinned                Pinned (priority) events
"""


def main():
    import sys
    if len(sys.argv) < 2:
        print(_USAGE)
        return 0
    cmd = sys.argv[1]
    if cmd == "brief":
        _cmd_brief()
    elif cmd == "log" and len(sys.argv) >= 4:
        _cmd_log(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "search" and len(sys.argv) >= 3:
        _cmd_search(" ".join(sys.argv[2:]))
    elif cmd == "precheck" and len(sys.argv) >= 3:
        _cmd_precheck(sys.argv[2])
    elif cmd == "stats":
        print(json.dumps(get_stats(), indent=2))
    elif cmd == "export":
        print(json.dumps(export_memory(), ensure_ascii=False, indent=1))
    elif cmd == "pinned":
        for row in pinned():
            print(f"[{row.get('time','')}] {row.get('kind','?')} {row.get('summary','')[:180]}")
    else:
        print(_USAGE)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
