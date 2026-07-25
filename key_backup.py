"""
Key Backup System — saves and restores .env + setenv.sh keys.
Auto-restores on startup if files are missing or keys are deleted.
"""
import os, json, base64, hashlib, time

BACKUP_FILE = "keys_backup.json"
DIR = os.path.dirname(os.path.abspath(__file__))


def _obfuscate(text):
    """Simple base64 obfuscation (not encryption, but hides plaintext)."""
    return base64.b64encode(text.encode()).decode()


def _deobfuscate(text):
    """Reverse obfuscation."""
    try:
        return base64.b64decode(text.encode()).decode()
    except Exception:
        return text


def backup_keys():
    """Backup all keys from .env and setenv.sh to keys_backup.json."""
    keys = {}
    for fname in [".env", "setenv.sh"]:
        fpath = os.path.join(DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        line = line.replace("export ", "")
                        key, _, val = line.partition("=")
                        val = val.strip().strip('"').strip("'")
                        key = key.strip()
                        if val and val != "set-via-env-var" and not val.startswith("$"):
                            keys[key] = val
    if not keys:
        return {"success": False, "error": "No keys found"}
    backup = {
        "keys": {k: _obfuscate(v) for k, v in keys.items()},
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(keys),
        "checksum": hashlib.sha256(json.dumps(keys, sort_keys=True).encode()).hexdigest()[:16],
    }
    bpath = os.path.join(DIR, BACKUP_FILE)
    with open(bpath, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2)
    return {"success": True, "count": len(keys), "timestamp": backup["timestamp"]}


def restore_keys():
    """Restore keys from backup to .env and setenv.sh if they're missing."""
    bpath = os.path.join(DIR, BACKUP_FILE)
    if not os.path.exists(bpath):
        return {"success": False, "error": "No backup file found"}
    with open(bpath, encoding="utf-8") as f:
        backup = json.load(f)
    keys = {k: _deobfuscate(v) for k, v in backup.get("keys", {}).items()}
    if not keys:
        return {"success": False, "error": "Backup is empty"}
    restored = []
    env_path = os.path.join(DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            existing = f.read()
        for k, v in keys.items():
            if k not in existing:
                restored.append(k)
    else:
        restored = list(keys.keys())
    env_lines = []
    for k, v in sorted(keys.items()):
        env_lines.append(f"{k}={v}")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines) + "\n")
    sh_path = os.path.join(DIR, "setenv.sh")
    sh_lines = ["#!/data/data/com.termux/files/usr/bin/bash", "# Restored from keys_backup.json"]
    for k, v in sorted(keys.items()):
        sh_lines.append(f'export {k}="{v}"')
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sh_lines) + "\n")
    return {"success": True, "restored": restored, "count": len(restored)}


def check_missing_keys():
    """Check if critical keys are missing from .env and return list."""
    critical = ["TELEGRAM_BOT_TOKEN", "OWNER_ID"]
    missing = []
    env_path = os.path.join(DIR, ".env")
    if not os.path.exists(env_path):
        return critical
    with open(env_path, encoding="utf-8") as f:
        content = f.read()
    for k in critical:
        if k not in content:
            missing.append(k)
    return missing


def list_backed_up():
    """List all backed up keys (masked)."""
    bpath = os.path.join(DIR, BACKUP_FILE)
    if not os.path.exists(bpath):
        return {"success": False, "error": "No backup file found"}
    with open(bpath, encoding="utf-8") as f:
        backup = json.load(f)
    keys = {k: _deobfuscate(v) for k, v in backup.get("keys", {}).items()}
    masked = {}
    for k, v in keys.items():
        if len(v) > 8:
            masked[k] = v[:4] + "*" * (len(v) - 8) + v[-4:]
        else:
            masked[k] = "****"
    return {
        "success": True,
        "keys": masked,
        "count": len(keys),
        "timestamp": backup.get("timestamp", "unknown"),
        "checksum": backup.get("checksum", "unknown"),
    }


def auto_backup_on_startup():
    """Auto-backup keys on startup if backup doesn't exist or is stale."""
    bpath = os.path.join(DIR, BACKUP_FILE)
    if os.path.exists(bpath):
        try:
            with open(bpath, encoding="utf-8") as f:
                backup = json.load(f)
            ts = backup.get("timestamp", "")
            if ts:
                backup_time = time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                age_hours = (time.time() - backup_time) / 3600
                if age_hours < 24:
                    return {"action": "skip", "reason": "backup is fresh (< 24h)"}
        except Exception:
            pass
    result = backup_keys()
    if result.get("success"):
        return {"action": "backed_up", "count": result["count"]}
    return {"action": "failed", "error": result.get("error", "unknown")}


if __name__ == "__main__":
    print("=== Key Backup System ===")
    missing = check_missing_keys()
    if missing:
        print(f"Missing critical keys: {missing}")
        print("Attempting restore...")
        r = restore_keys()
        print(f"Restore: {r}")
    else:
        print("All critical keys present.")
    result = backup_keys()
    print(f"Backup: {result}")
    info = list_backed_up()
    print(f"Backed up keys: {info.get('count', 0)}")
    for k, v in info.get("keys", {}).items():
        print(f"  {k}: {v}")
