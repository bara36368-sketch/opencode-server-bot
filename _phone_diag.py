import sys, os, json

results = []
results.append(f"Python: {sys.version}")
results.append(f"Platform: {sys.platform}")
results.append(f"CWD: {os.getcwd()}")

# Check .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                if "TOKEN" in k:
                    results.append(f"ENV {k}: {v[:10]}...{v[-5:]} (len={len(v)})")
                elif "KEY" in k:
                    results.append(f"ENV {k}: present ({len(v)} chars)")
                else:
                    results.append(f"ENV {k}: {v[:20]}")
else:
    results.append(f"NO .env file at {env_path}")

# Check token specifically
token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if token and ":" in token:
    results.append(f"TOKEN valid format: yes (len={len(token)})")
elif token:
    results.append(f"TOKEN valid format: NO (no colon found)")
else:
    results.append(f"TOKEN: EMPTY")

# Check dependencies
deps = ["httpx", "asyncio", "json", "logging"]
for dep in deps:
    try:
        __import__(dep)
        results.append(f"  {dep}: OK")
    except ImportError as e:
        results.append(f"  {dep}: MISSING - {e}")

# Check optional heavy deps
opt_deps = ["networkx", "PIL", "numpy", "pandas"]
for dep in opt_deps:
    try:
        m = __import__(dep)
        results.append(f"  {dep}: installed")
    except ImportError:
        results.append(f"  {dep}: not installed (OK - lazy loaded)")

# Check httpx version
try:
    import httpx
    results.append(f"  httpx version: {httpx.__version__}")
except Exception as e:
    results.append(f"  httpx error: {e}")

# Quick API test
import asyncio
async def test_api():
    try:
        import httpx
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return "NO TOKEN - cannot test API"
        async with httpx.AsyncClient() as c:
            r = await c.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
            data = r.json()
            if data.get("ok"):
                bot = data.get("result", {})
                return f"API OK: @{bot.get('username', '?')} ({bot.get('first_name', '?')})"
            else:
                return f"API FAILED: {data}"
    except Exception as e:
        return f"API ERROR: {type(e).__name__}: {e}"

try:
    api_result = asyncio.run(test_api())
    results.append(f"  Telegram API: {api_result}")
except Exception as e:
    results.append(f"  API test failed: {e}")

# Check RAM
try:
    import resource
    usage = resource.getrusage(resource.RUSAGE_SELF)
    results.append(f"  RSS memory: {usage.ru_maxrss} KB")
except Exception:
    pass

# Write results
out = "\n".join(results)
print(out)
with open("phone_diag.txt", "w") as f:
    f.write(out)
