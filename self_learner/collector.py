"""Self-study collector: generates curiosity questions, asks many AIs at once
through the OMNI Gateway (:4455 ranked free models), cross-checks their
answers, and distills consensus into the knowledge memory.

This is how the brain 'trains' without GPUs: every cycle injects fresh,
multi-source, cross-validated knowledge that retrieval surfaces forever."""
import json
import os
import time
import urllib.request

import memory

DIR = os.path.dirname(os.path.abspath(__file__))
OMNI_BASE = os.environ.get("OMNI_BASE", "http://127.0.0.1:4455")
ANSWER_MODELS = int(os.environ.get("BRAIN_ANSWER_MODELS", "3"))
QUESTIONS_PER_CYCLE = int(os.environ.get("BRAIN_QUESTIONS", "3"))
HTTP_TIMEOUT = float(os.environ.get("BRAIN_TIMEOUT", "240"))

TOPIC_SEEDS = [
    "programming languages and their tradeoffs",
    "electronics and microcontrollers (SBCs, PCBs, sensors)",
    "mathematics for machine learning",
    "physics concepts explained simply",
    "history of technology",
    "practical cybersecurity defense",
    "health and human performance",
    "economics and markets basics",
    "space exploration",
    "productivity systems and learning science",
    "databases and system design",
    "networking protocols",
    "AI architectures and training methods",
    "chemistry in everyday life",
    "philosophy of mind",
]


def _omni_chat(model, system, user_text, max_tokens=1200):
    """Gateway /api/chat contract: single 'message' + optional system prefix."""
    content = (f"[SYSTEM] {system}\n\n[USER] {user_text}") if system else user_text
    payload = json.dumps({"model": model, "message": content,
                          "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(OMNI_BASE + "/api/chat", data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pick_teacher_models(k=ANSWER_MODELS):
    """Distinct providers, text-capable, top-ranked first. Skips omniroute
    (meta-router: every call walks its own fallback chain = slow/flaky for
    multi-perspective collection)."""
    with urllib.request.urlopen(OMNI_BASE + "/api/free", timeout=20) as r:
        free = json.loads(r.read().decode()).get("free", [])
    picks, seen = [], set()
    for m in free:
        prov = m["provider"]
        if prov == "omniroute":
            continue
        mods = [x.lower() for x in (m.get("modalities") or ["text"])]
        mid_l = m["model_id"].lower()
        if "text" not in mods or any(x in mid_l for x in
                ("image", "flux", "tts", "whisper", "embed", "coder")):
            continue
        if prov in seen:
            continue
        seen.add(prov)
        picks.append(m["id"])
        if len(picks) >= k:
            break
    return picks


def generate_question(topic):
    try:
        d = _omni_chat("auto",
            "You generate ONE specific, high-value study question about the given "
            "topic. Output ONLY the question text, nothing else.",
            f"Topic: {topic}", max_tokens=200)
        q = (d.get("reply") or "").strip().strip('"')
        return q[:400] if len(q) > 15 else None
    except Exception as e:
        print(f"  question gen failed: {e}")
        return None


def collect_answers(question, teacher_models):
    answers = []
    for model in teacher_models:
        try:
            d = _omni_chat(model, None,
                f"{question}\n\nAnswer precisely and completely in under 250 words. "
                f"If uncertain, say what is known vs unknown.", max_tokens=700)
            reply = (d.get("reply") or "").strip()
            if len(reply) > 80:
                answers.append({"model": model, "text": reply})
                print(f"    <- {model[:44]} ({len(reply)} chars)")
        except Exception as e:
            print(f"    <- {model[:44]} FAILED {str(e)[:40]}")
        time.sleep(0.5)
    return answers


def distill(question, topic, answers):
    """Cross-check: one strong model merges answers into consensus + insights.
    Score rises with source agreement."""
    src_lines = "\n\n".join(
        f"--- ANSWER from {a['model']} ---\n{a['text']}" for a in answers)
    models_agree = len({a["model"].split("/")[0] for a in answers})
    score = min(0.95, 0.45 + 0.18 * models_agree)
    try:
        d = _omni_chat("auto",
            "You are a rigorous synthesizer. Multiple AI models answered the same "
            "question. Merge them into one authoritative answer: keep points where "
            "answers agree, flag disagreements explicitly as DISPUTED, drop anything "
            "contradicted by majority. Output only the final distilled answer.",
            f"QUESTION: {question}\n\n{src_lines}", max_tokens=900)
        final = (d.get("reply") or "").strip()
    except Exception as e:
        print(f"    distill failed: {e}")
        final = max(answers, key=lambda a: len(a["text"]))["text"] if answers else ""
    return final, round(score, 2), [a["model"] for a in answers]


def study_cycle(n_topics=QUESTIONS_PER_CYCLE, topics=None):
    memory.init_db()
    import random
    seeds = topics or random.sample(TOPIC_SEEDS, min(n_topics, len(TOPIC_SEEDS)))
    teachers = pick_teacher_models()
    if not teachers:
        print("no teacher models available (gateway down?)")
        return {"learned": 0}
    print(f"teachers: {teachers}")
    learned = []
    for topic in seeds:
        print(f"[topic] {topic}")
        q = generate_question(topic)
        if not q:
            continue
        print(f"  Q: {q[:100]}")
        answers = collect_answers(q, teachers)
        if len(answers) < 2:
            print("  skipped (need >=2 sources)")
            continue
        final, score, sources = distill(q, topic, answers)
        if len(final) < 60:
            continue
        memory.store_experience(topic, q, final, sources, score)
        learned.append({"topic": topic, "q": q[:80], "score": score,
                        "sources": len(sources)})
        print(f"  stored (score {score}, {len(sources)} sources)")
    return {"learned": len(learned), "details": learned}


if __name__ == "__main__":
    result = study_cycle()
    print(json.dumps(result, indent=1))
