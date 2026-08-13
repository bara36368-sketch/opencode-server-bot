"""Multi-repo auto-update for the runner (opencode-server-bot).

Each repo gets its own small registry file under <bot>/repos/<label>.json.
runner.py drives update_all() on every main-loop tick; it walks every
registered repo and:

  * reports live progress as 0/N, 1/N, ... N/N
  * "searching update" -> "update found, git pulling..."
  * on pull failure falls back to fetch + hard reset to the default remote
    branch ("use the other one")

New repos on disk are auto-discovered (discover_repos). A repo is linked
(added to the update set + gets a registry file) when its files reference
the bot's entrypoints: cyberdeck.py / runner.py / opencode.py
(also cyberdeck_bot.py / opencode_bot.py / repo_updater).
"""
import glob
import json
import os
import subprocess

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
              "_archive", "vendor", "dist", "build", "whatsapp", "repos",
              "auth_info", "data", "models", "cache", "logs"}
_SKIP_EXTS = {".pyc", ".exe", ".dll", ".so", ".dylib", ".png", ".jpg",
              ".jpeg", ".gif", ".bmp", ".webp", ".bin", ".scad", ".ogg",
              ".mp3", ".mp4", ".zip", ".7z", ".whl", ".ttf", ".woff2"}
_MAX_SCAN_BYTES = 512_000
_MAX_SCAN_FILES = 300
_LINK_NEEDLES = ("cyberdeck.py", "runner.py", "opencode.py",
                 "cyberdeck_bot.py", "opencode_bot.py", "repo_updater")
_RESET_COOLDOWN = 300
_last_reset = {}
_bot_file_cache = None


def registry_dir():
    """State dir OUTSIDE the bot repo so registry writes never dirty the
    git working tree (which would defeat --ff-only pulls and trigger the
    reset fallback in an endless loop)."""
    d = os.environ.get("REPO_STATE_DIR",
                       os.path.join(os.path.expanduser("~"),
                                    ".opencode-runner", "repos"))
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def _seed_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "repos")


def seed_registry():
    """First-run: copy the bundled repos/*.json (Windows/this-host entries)
    into the state dir so labels survive. Entries pointing at missing paths
    are ignored by registry_entries()."""
    dst = registry_dir()
    if glob.glob(os.path.join(dst, "*.json")):
        return 0
    copied = 0
    for p in glob.glob(os.path.join(_seed_dir(), "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                e = json.load(f)
            if e.get("label") and e.get("path"):
                write_entry(e)
                copied += 1
        except Exception:
            continue
    return copied


def registry_path(label):
    safe = str(label).replace("/", "_").replace("\\", "_").strip()
    return os.path.join(registry_dir(), safe + ".json")


def read_entry(label):
    try:
        with open(registry_path(label), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_entry(entry):
    try:
        os.makedirs(registry_dir(), exist_ok=True)
        with open(registry_path(entry["label"]), "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
        return True
    except OSError:
        return False


def registry_entries():
    seed_registry()
    out = []
    for p in sorted(glob.glob(os.path.join(registry_dir(), "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                e = json.load(f)
            if e.get("label") and e.get("path") and os.path.isdir(
                    os.path.join(e["path"], ".git")):
                out.append(e)
        except Exception:
            continue
    return out


def discover_repos(parent):
    """(label, path) for every git repo directly under `parent`."""
    if not os.path.isdir(parent):
        return []
    out = []
    try:
        for name in sorted(os.listdir(parent)):
            d = os.path.join(parent, name)
            if os.path.isdir(d) and os.path.isdir(os.path.join(d, ".git")):
                out.append((name, d))
    except OSError:
        pass
    return out


def _repo_files(repo_dir):
    count = 0
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for fname in files:
            if not fname.endswith((".py", ".js", ".json", ".md", ".txt", ".sh")):
                continue
            fp = os.path.join(root, fname)
            try:
                if os.path.getsize(fp) > _MAX_SCAN_BYTES or os.path.islink(fp):
                    continue
            except OSError:
                continue
            yield fp
            count += 1
            if count >= _MAX_SCAN_FILES:
                return


def _bot_files(bot_dir=None):
    global _bot_file_cache
    if _bot_file_cache is None:
        _bot_file_cache = list(_repo_files(
            bot_dir or os.path.dirname(os.path.abspath(__file__))))
    return _bot_file_cache


def is_linked_to_runner(repo_dir):
    """True when any tracked-ish file references the bot entrypoints."""
    for fp in _repo_files(repo_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            if any(n in text for n in _LINK_NEEDLES):
                return True
        except Exception:
            continue
    return False


def is_referenced_by_bot(repo_label, repo_dir, bot_dir=None):
    """True when the runner's own entrypoints mention this repo by name or
    path (covers repos that are consumers, e.g. obsidian-memory/MEMORY_REPO).
    Returns None when the bot dir is unknown (no verdict)."""
    bot_dir = bot_dir or os.path.dirname(os.path.abspath(__file__))
    label = str(repo_label).lower()
    path_hint = os.path.normcase(os.path.normpath(repo_dir)).lower()
    for fp in _bot_files(bot_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as fh:
                text = fh.read().lower()
            if label in text or path_hint in text:
                return True
        except Exception:
            continue
    return False


def sync_registry(parent, extras=None, allow_reset_default=True):
    """Ensure every git repo under `parent` (plus extras) has a registry
    entry. New repos are added only when linked to the bot (repo references
    the bot's entrypoints, or the bot references the repo); unlinked ones
    are returned in `ignored`. Returns (entries, ignored)."""
    entries = registry_entries()
    ignored = []
    by_path = {}
    for e in entries:
        by_path.setdefault(_norm(e["path"]), e)
    for label, d in discover_repos(parent):
        key = _norm(d)
        if key in by_path:
            continue
        if not (is_linked_to_runner(d) or is_referenced_by_bot(label, d)):
            ignored.append(label)
            continue
        e = {"label": label, "path": d,
             "allow_reset": bool(allow_reset_default), "linked": True}
        by_path[key] = e
        write_entry(e)
    for label, d in (extras or {}).items():
        key = _norm(d)
        if key in by_path:
            continue
        e = {"label": label, "path": d,
             "allow_reset": bool(allow_reset_default), "linked": True}
        by_path[key] = e
        write_entry(e)
    return [e for e in by_path.values() if e.get("linked")], ignored


def _norm(path):
    return os.path.normcase(os.path.normpath(path))


def _primary_remote(d):
    try:
        r = subprocess.run(["git", "remote"], cwd=d, capture_output=True,
                           text=True, timeout=10, encoding="utf-8")
        names = [n.strip() for n in r.stdout.split() if n.strip()]
        if "origin" in names:
            return "origin"
        return names[0] if names else None
    except Exception:
        return None


def _default_branch(d):
    try:
        r = subprocess.run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                           cwd=d, capture_output=True, text=True, timeout=10,
                           encoding="utf-8")
        if r.returncode == 0:
            return r.stdout.strip().replace("refs/remotes/origin/", "").strip()
    except Exception:
        pass
    try:
        r = subprocess.run(["git", "symbolic-ref", "refs/remotes/HEAD"],
                           cwd=d, capture_output=True, text=True, timeout=10,
                           encoding="utf-8")
        if r.returncode == 0:
            return r.stdout.strip().replace("refs/remotes/", "").split("/", 1)[1]
    except Exception:
        pass
    return "master"


def _head_short(d):
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=d,
                           capture_output=True, text=True, timeout=10,
                           encoding="utf-8")
        return r.stdout.strip() or None
    except Exception:
        return None


def update_all(entries, notify=None):
    """Pull every entry; on pull failure fall back to fetch + hard reset.
    notify(prefix, msg) is called with prefix like "0/6" (searching) then
    "1/6" (after the repo is done). Returns the set of changed labels."""
    def say(i, total, msg):
        if notify:
            try:
                notify("%d/%d" % (i, total), msg)
            except Exception:
                pass

    total = len(entries)
    changed = set()
    for i, entry in enumerate(entries):
        label = entry.get("label", "?")
        d = entry["path"]
        allow_reset = bool(entry.get("allow_reset", True))
        say(i, total, "%s — searching update" % label)
        if not os.path.isdir(os.path.join(d, ".git")):
            say(i, total, "%s — not a git repo, skipped" % label)
            continue
        try:
            r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d,
                               capture_output=True, text=True, timeout=10,
                               encoding="utf-8")
        except Exception as e:
            say(i, total, "%s — git unavailable: %s" % (label, e))
            continue
        old_head = r.stdout.strip()
        say(i, total, "%s — update found, git pulling..." % label)
        try:
            pr = subprocess.run(["git", "pull", "--ff-only", "--depth=1"],
                                cwd=d, capture_output=True, text=True,
                                timeout=30, encoding="utf-8")
        except Exception as e:
            say(i, total, "%s — pull error: %s" % (label, e))
            continue
        if pr.returncode == 0:
            new_head = _head_short(d)
            if new_head and new_head != old_head[:len(new_head)]:
                changed.add(label)
                say(i + 1, total, "%s — pulled %s" % (label, new_head))
            else:
                say(i + 1, total, "%s — up to date" % label)
            continue
        # pull failed -> stash-then-pull (preserve local changes)
        say(i, total, "%s — pull failed, trying stash-then-pull" % label)
        stashed = False
        try:
            sp = subprocess.run(["git", "stash", "push", "-m", "runner-auto"],
                                cwd=d, capture_output=True, text=True,
                                timeout=30, encoding="utf-8")
            comb = (sp.stdout or "") + (sp.stderr or "")
            if sp.returncode == 0:
                stashed = "No local changes" not in comb
            else:
                say(i, total, "%s — stash error: %s" % (label, sp.stderr.strip()[-200:]))
        except Exception as e:
            say(i, total, "%s — stash error: %s" % (label, e))
        try:
            pr2 = subprocess.run(["git", "pull", "--ff-only", "--depth=1"],
                                 cwd=d, capture_output=True, text=True,
                                 timeout=30, encoding="utf-8")
        except Exception as e:
            pr2 = None
            say(i, total, "%s — pull retry error: %s" % (label, e))
        restored = True
        if stashed:
            try:
                rp = subprocess.run(["git", "stash", "pop"], cwd=d,
                                    capture_output=True, text=True,
                                    timeout=30, encoding="utf-8")
                restored = rp.returncode == 0
                if not restored:
                    say(i, total, "%s — stash pop conflict, run 'git stash list' to recover" % label)
            except Exception as e:
                restored = False
                say(i, total, "%s — stash pop error: %s" % (label, e))
        if pr2 and pr2.returncode == 0:
            new_head = _head_short(d)
            if new_head and new_head != old_head[:len(new_head)]:
                changed.add(label)
                say(i + 1, total, "%s — pulled %s (stash-then-pull)" % (label, new_head))
            else:
                say(i + 1, total, "%s — up to date (stash)" % label)
            continue
        # last resort: fetch + hard reset (local edits already stashed)
        if not allow_reset:
            say(i, total, "%s — pull still failed, reset not allowed, skipped" % label)
            continue
        now = _now()
        if now - _last_reset.get(d, 0) < _RESET_COOLDOWN:
            say(i, total, "%s — pull still failed, fallback on cooldown" % label)
            continue
        say(i, total, "%s — pull still failed, using fallback (fetch + hard reset)" % label)
        remote = _primary_remote(d)
        if not remote:
            say(i, total, "%s — no git remote, cannot fallback" % label)
            continue
        try:
            fr = subprocess.run(["git", "fetch", remote], cwd=d,
                                capture_output=True, text=True, timeout=60,
                                encoding="utf-8")
            if fr.returncode != 0:
                say(i, total, "%s — fetch failed: %s" % (label, fr.stderr.strip()[-200:]))
                continue
            branch = _default_branch(d)
            ref = "%s/%s" % (remote, branch) if branch else "%s/master" % remote
            rr = subprocess.run(["git", "reset", "--hard", ref], cwd=d,
                                capture_output=True, text=True, timeout=30,
                                encoding="utf-8")
            if rr.returncode != 0:
                say(i, total, "%s — reset failed: %s" % (label, rr.stderr.strip()[-200:]))
                continue
            _last_reset[d] = now
            new_head = _head_short(d)
            if new_head and new_head != old_head[:len(new_head)]:
                changed.add(label)
                say(i + 1, total, "%s — fallback reset -> %s" % (label, new_head))
            else:
                say(i + 1, total, "%s — fallback reset: no change" % label)
        except Exception as e:
            say(i, total, "%s — fallback error: %s" % (label, e))
    return changed


def _now():
    import time
    return int(time.time())
