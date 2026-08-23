"""Knowledge memory for the self-learning brain.
SQLite + FTS5: every collected experience is searchable forever.
Schema: experiences(topic, question, answer, sources_json, score, ts)."""
import json
import os
import sqlite3
import time

DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, "brain_memory.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources_json TEXT NOT NULL DEFAULT '[]',
    score REAL NOT NULL DEFAULT 0.5,
    created_ts REAL NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts USING fts5(
    question, answer, topic, content='experiences', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS exp_ai AFTER INSERT ON experiences BEGIN
    INSERT INTO experiences_fts(rowid, question, answer, topic)
    VALUES (new.id, new.question, new.answer, new.topic);
END;
CREATE TRIGGER IF NOT EXISTS exp_ad AFTER DELETE ON experiences BEGIN
    INSERT INTO experiences_fts(experiences_fts, rowid, question, answer, topic)
    VALUES ('delete', old.id, old.question, old.answer, old.topic);
END;
CREATE INDEX IF NOT EXISTS exp_topic_idx ON experiences(topic);
"""


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.executescript(_SCHEMA)


def store_experience(topic, question, answer, sources, score=0.6):
    with _conn() as c:
        c.execute(
            "INSERT INTO experiences (topic, question, answer, sources_json, score, created_ts)"
            " VALUES (?,?,?,?,?,?)",
            (topic[:200], question[:1000], answer, json.dumps(sources or []),
             float(score), time.time()))


def search(query, limit=6, min_len=40):
    """FTS match, fallback to recent when query has no hits. Returns list of
    dicts: {topic, question, answer, sources, score, age_days}."""
    if not query:
        return []
    terms = " OR ".join(w for w in
                        "".join(ch if ch.isalnum() else " " for ch in query).split()
                        if len(w) > 2)[:240]
    out = []
    with _conn() as c:
        if terms:
            try:
                rows = c.execute(
                    "SELECT e.* FROM experiences_fts f JOIN experiences e ON e.id = f.rowid "
                    "WHERE experiences_fts MATCH ? ORDER BY rank LIMIT ?",
                    (terms, limit)).fetchall()
                out = [dict(r) for r in rows]
            except sqlite3.OperationalError:
                out = []
        if not out:
            rows = c.execute(
                "SELECT * FROM experiences ORDER BY created_ts DESC, score DESC LIMIT ?",
                (limit,)).fetchall()
            out = [dict(r) for r in rows]
    result = []
    for r in out:
        if len(r["answer"]) < min_len:
            continue
        result.append({
            "topic": r["topic"],
            "question": r["question"],
            "answer": r["answer"],
            "sources": json.loads(r.get("sources_json") or "[]"),
            "score": r["score"],
            "age_days": round((time.time() - r["created_ts"]) / 86400, 1),
        })
    return result


def stats():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
        topics = c.execute("SELECT COUNT(DISTINCT topic) FROM experiences").fetchone()[0]
        last = c.execute("SELECT MAX(created_ts) FROM experiences").fetchone()[0]
        per_topic = c.execute(
            "SELECT topic, COUNT(*) n FROM experiences GROUP BY topic "
            "ORDER BY n DESC LIMIT 8").fetchall()
    return {"total_experiences": total, "distinct_topics": topics,
            "last_learned_ago_h": round((time.time() - (last or 0)) / 3600, 1) if last else None,
            "top_topics": [{"topic": t["topic"], "count": t["n"]} for t in per_topic]}


if __name__ == "__main__":
    init_db()
    print(json.dumps(stats(), indent=1))
