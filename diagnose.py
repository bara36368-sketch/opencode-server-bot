"""
OpenCode Bot — Auto Diagnostic System
Tests every component, catches errors, writes to crash.log
Run: python diagnose.py
"""
import py_compile, sys, os, json, time, traceback, importlib.util, inspect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRASH_LOG = os.path.join(BASE_DIR, "crash.log")
RESULTS = []

def log_result(category, name, status, detail=""):
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "category": category, "name": name, "status": status, "detail": detail}
    RESULTS.append(entry)
    icon = "PASS" if status == "pass" else "FAIL" if status == "fail" else "WARN"
    print(f"  [{icon}] {name}: {detail[:120] if detail else 'OK'}")

def test_syntax():
    print("\n=== SYNTAX CHECK ===")
    py_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".py")]
    for fname in sorted(py_files):
        fpath = os.path.join(BASE_DIR, fname)
        try:
            py_compile.compile(fpath, doraise=True)
            log_result("syntax", fname, "pass")
        except py_compile.PyCompileError as e:
            log_result("syntax", fname, "fail", str(e))

def test_import(module_name, filepath=None):
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath or os.path.join(BASE_DIR, f"{module_name}.py"))
        if not spec or not spec.loader:
            log_result("import", module_name, "fail", "Cannot create module spec")
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        log_result("import", module_name, "pass")
        return mod
    except SystemExit:
        log_result("import", module_name, "warn", "SystemExit (lock file or normal exit)")
        return None
    except Exception as e:
        log_result("import", module_name, "fail", f"{type(e).__name__}: {e}")
        return None

def test_imports():
    print("\n=== IMPORT CHECK ===")
    stdlib = ["asyncio", "json", "os", "time", "re", "hashlib", "html", "copy", "random", "urllib", "uuid", "io", "traceback", "sys", "threading", "subprocess", "inspect", "glob", "signal", "shutil", "base64"]
    for mod in stdlib:
        try:
            __import__(mod)
            log_result("stdlib", mod, "pass")
        except ImportError as e:
            log_result("stdlib", mod, "fail", str(e))

    third_party = ["httpx", "aiohttp"]
    for mod in third_party:
        try:
            __import__(mod)
            log_result("third_party", mod, "pass")
        except ImportError:
            log_result("third_party", mod, "warn", "Not installed (optional)")

def test_json_files():
    print("\n=== JSON FILES CHECK ===")
    json_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".json")]
    for fname in sorted(json_files):
        fpath = os.path.join(BASE_DIR, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            log_result("json", fname, "pass", f"Valid ({len(json.dumps(data))} bytes)")
        except json.JSONDecodeError as e:
            log_result("json", fname, "fail", f"Invalid JSON: {e}")
        except Exception as e:
            log_result("json", fname, "fail", str(e))

def test_bot_features_stub():
    print("\n=== BOT_FEATURES STUB CHECK ===")
    bf_path = os.path.join(BASE_DIR, "bot_features.py")
    if not os.path.exists(bf_path):
        log_result("bf_stub", "bot_features.py", "fail", "File not found")
        return
    try:
        with open(bf_path, encoding="utf-8") as f:
            content = f.read()
        async_methods = ["vision_analyze", "get_photo_url", "voice_to_text", "text_to_speech",
                         "translate", "web_search", "youtube_transcript", "run_code", "fetch_url",
                         "auto_context", "summarize_conversation", "image_generate", "qr_encode",
                         "qr_decode_from_url", "extract_text_from_file", "parse_spreadsheet"]
        for method in async_methods:
            if f"async def {method}" in content or f"def {method}" in content:
                log_result("bf_stub", method, "pass", "Found")
            else:
                log_result("bf_stub", method, "warn", "Not found in bot_features.py")
    except Exception as e:
        log_result("bf_stub", "scan", "fail", str(e))

def test_version_files():
    print("\n=== VERSION SYSTEM CHECK ===")
    try:
        with open(os.path.join(BASE_DIR, "version.json"), encoding="utf-8") as f:
            v = json.load(f)
        ver = v.get("version", "unknown")
        whats_new = v.get("whats_new", {})
        log_result("version", "version.json", "pass", f"v{ver}, {len(whats_new)} versions tracked")
    except Exception as e:
        log_result("version", "version.json", "fail", str(e))

    try:
        with open(os.path.join(BASE_DIR, "version_state.json"), encoding="utf-8") as f:
            vs = json.load(f)
        last = vs.get("last_version", "")
        log_result("version", "version_state.json", "pass", f"last_version={last}")
    except Exception as e:
        log_result("version", "version_state.json", "fail", str(e))

    try:
        with open(os.path.join(BASE_DIR, "experimental.json"), encoding="utf-8") as f:
            exp = json.load(f)
        count = sum(1 for v in exp.values() if v.get("enabled"))
        log_result("version", "experimental.json", "pass", f"{count} features enabled")
    except Exception as e:
        log_result("version", "experimental.json", "fail", str(e))

def test_runner():
    print("\n=== RUNNER CHECK ===")
    try:
        with open(os.path.join(BASE_DIR, "runner.py"), encoding="utf-8") as f:
            content = f.read()
        issues = []
        if "fuser" in content and os.name == "nt":
            issues.append("fuser is Linux-only (guarded OK)")
        if "pkill" in content and os.name == "nt":
            issues.append("pkill is Linux-only (guarded OK)")
        if "signal" not in content:
            issues.append("No signal handling for graceful shutdown")
        log_result("runner", "runner.py", "pass" if not issues else "warn", "; ".join(issues) if issues else "OK")
    except Exception as e:
        log_result("runner", "runner.py", "fail", str(e))

def test_web_gateway():
    print("\n=== WEB GATEWAY CHECK ===")
    wg_path = os.path.join(BASE_DIR, "web_gateway.py")
    try:
        with open(wg_path, encoding="utf-8") as f:
            content = f.read()
        issues = []
        if "httpx.AsyncClient" in content and "HAS_HTTPX" in content:
            if "if not HAS_HTTPX" in content:
                log_result("web_gateway", "httpx guard", "pass", "Protected")
            else:
                issues.append("httpx used without HAS_HTTPX guard in get_http()")
                log_result("web_gateway", "httpx guard", "fail", issues[-1])
        else:
            log_result("web_gateway", "httpx guard", "warn", "Could not verify")

        if "_mcp_call_tool" in content:
            log_result("web_gateway", "MCP tools", "pass", "MCP server present")
        if "PROVIDER_ROLES" in content:
            roles = content.count('"role"')
            log_result("web_gateway", "provider_roles", "pass", f"{roles} roles defined")

        if not issues:
            log_result("web_gateway", "overall", "pass", "No issues found")
    except Exception as e:
        log_result("web_gateway", "overall", "fail", str(e))

def test_providers():
    print("\n=== PROVIDERS CHECK ===")
    pf = os.path.join(BASE_DIR, "providers.json")
    try:
        with open(pf, encoding="utf-8") as f:
            provs = json.load(f)
        configured = sum(1 for p in provs.values() if p.get("key", "not configured") not in ("not configured", "YOUR_"))
        log_result("providers", "providers.json", "pass", f"{len(provs)} providers, {configured} with keys")
    except FileNotFoundError:
        log_result("providers", "providers.json", "warn", "File not found")
    except Exception as e:
        log_result("providers", "providers.json", "fail", str(e))

def test_sessions():
    print("\n=== SESSIONS CHECK ===")
    sf = os.path.join(BASE_DIR, "sessions.json")
    try:
        with open(sf, encoding="utf-8") as f:
            data = json.load(f)
        s_count = len(data.get("sessions", {}))
        t_count = len(data.get("team_sessions", {}))
        log_result("sessions", "sessions.json", "pass", f"{s_count} user sessions, {t_count} team sessions")
    except FileNotFoundError:
        log_result("sessions", "sessions.json", "warn", "File not found (will be created)")
    except Exception as e:
        log_result("sessions", "sessions.json", "fail", str(e))

def test_memory():
    print("\n=== MEMORY & DATA CHECK ===")
    files = {
        "memory.json": "Memory store",
        "token_usage.json": "Token usage",
        "mods.json": "Moderators",
        "bot.log": "Bot log",
    }
    for fname, desc in files.items():
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            log_result("data", f"{fname} ({desc})", "pass", f"{size} bytes")
        else:
            log_result("data", f"{fname} ({desc})", "warn", "Not found")

def test_opencode_bot_main():
    print("\n=== MAIN BOT MODULE CHECK ===")
    bot_path = os.path.join(BASE_DIR, "opencode_bot.py")
    try:
        with open(bot_path, encoding="utf-8") as f:
            content = f.read()

        critical_funcs = ["send", "call_provider", "smart_call", "main", "tg",
                          "announce_update", "auto_version_checker", "_safe_track_usage"]
        for func in critical_funcs:
            if f"def {func}(" in content or f"async def {func}(" in content:
                log_result("bot_main", func, "pass")
            else:
                log_result("bot_main", func, "fail", "Function not found")

        if "_BfStub" in content:
            log_result("bot_main", "_BfStub class", "pass", "Present (prevents None crash)")
        else:
            log_result("bot_main", "_BfStub class", "fail", "MISSING — bot will crash if bot_features fails to import")

        if "datetime" in content:
            log_result("bot_main", "datetime import", "pass")
        else:
            log_result("bot_main", "datetime import", "fail", "datetime not imported")

        if "aiohttp" in content:
            log_result("bot_main", "aiohttp import", "pass")

    except Exception as e:
        log_result("bot_main", "scan", "fail", str(e))

def test_file_permissions():
    print("\n=== FILE PERMISSIONS CHECK ===")
    critical = ["opencode_bot.py", "web_gateway.py", "runner.py", "bot_features.py",
                "version.json", "version_state.json", "experimental.json", "mods.json"]
    for fname in critical:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            readable = os.access(fpath, os.R_OK)
            writable = os.access(fpath, os.W_OK)
            if readable and writable:
                log_result("perms", fname, "pass")
            else:
                log_result("perms", fname, "fail", f"read={readable}, write={writable}")
        else:
            log_result("perms", fname, "warn", "File missing")

def write_crash_log():
    fails = [r for r in RESULTS if r["status"] == "fail"]
    warns = [r for r in RESULTS if r["status"] == "warn"]
    passes = [r for r in RESULTS if r["status"] == "pass"]

    with open(CRASH_LOG, "w", encoding="utf-8") as f:
        f.write(f"{'='*60}\n")
        f.write(f"OpenCode Bot Diagnostic Report\n")
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"SUMMARY: {len(passes)} passed, {len(fails)} FAILED, {len(warns)} warnings\n\n")

        if fails:
            f.write(f"{'='*60}\n")
            f.write(f"FAILURES ({len(fails)})\n")
            f.write(f"{'='*60}\n")
            for r in fails:
                f.write(f"[{r['time']}] [{r['category']}] {r['name']}: {r['detail']}\n")
            f.write("\n")

        if warns:
            f.write(f"{'='*60}\n")
            f.write(f"WARNINGS ({len(warns)})\n")
            f.write(f"{'='*60}\n")
            for r in warns:
                f.write(f"[{r['time']}] [{r['category']}] {r['name']}: {r['detail']}\n")
            f.write("\n")

        f.write(f"{'='*60}\n")
        f.write(f"ALL PASSED ({len(passes)})\n")
        f.write(f"{'='*60}\n")
        for r in passes:
            f.write(f"[{r['category']}] {r['name']}: OK\n")

    print(f"\n{'='*60}")
    print(f"REPORT: {len(passes)} passed, {len(fails)} FAILED, {len(warns)} warnings")
    print(f"Full report written to: {CRASH_LOG}")
    if fails:
        print(f"\nCRITICAL FAILURES:")
        for r in fails:
            print(f"  - [{r['category']}] {r['name']}: {r['detail']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    print(f"OpenCode Bot Auto-Diagnostic System")
    print(f"{'='*60}")
    test_syntax()
    test_imports()
    test_json_files()
    test_bot_features_stub()
    test_version_files()
    test_runner()
    test_web_gateway()
    test_providers()
    test_sessions()
    test_memory()
    test_opencode_bot_main()
    test_file_permissions()
    write_crash_log()
