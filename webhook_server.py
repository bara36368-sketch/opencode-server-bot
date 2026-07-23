import asyncio
import json
import os
import time
import logging
import hashlib
import hmac

logging.basicConfig(level=logging.INFO, format="%(asctime)s [webhook] %(message)s")
logger = logging.getLogger("webhook")

WEBHOOK_HOST = "127.0.0.1"
WEBHOOK_PORT = 8443
SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET", "opencode_webhook_secret_" + hashlib.md5(os.environ.get("TELEGRAM_BOT_TOKEN", "").encode()).hexdigest()[:8])

update_queue = None
bot_token = None
TG_API = None

async def handle_webhook(request):
    try:
        x_telegram = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if SECRET_TOKEN and x_telegram != SECRET_TOKEN:
            logger.info(f"Invalid secret token from {request.remote}")
            return {"ok": False, "error": "unauthorized"}, 403
        data = await request.json()
        if update_queue:
            await update_queue.put(data)
        return {"ok": True}
    except Exception as e:
        logger.info(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}, 400

async def handle_health(request):
    return {"status": "ok", "queue_size": update_queue.qsize() if update_queue else 0, "timestamp": time.time()}

async def setup_webhook(public_url):
    import httpx
    global bot_token, TG_API
    if not bot_token:
        return False
    TG_API = f"https://api.telegram.org/bot{bot_token}"
    webhook_url = f"{public_url}/webhook"
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{TG_API}/setWebhook", json={
            "url": webhook_url,
            "secret_token": SECRET_TOKEN,
            "allowed_updates": ["message", "chat_join_request", "chat_member", "my_chat_member", "poll_answer"],
            "max_connections": 40,
            "drop_pending_updates": True
        }, timeout=15)
        resp = r.json()
        if resp.get("ok"):
            logger.info(f"Webhook set: {webhook_url}")
            return True
        else:
            logger.info(f"Webhook setup failed: {resp}")
            return False

async def remove_webhook():
    import httpx
    if not bot_token:
        return
    TG_API_url = f"https://api.telegram.org/bot{bot_token}"
    async with httpx.AsyncClient() as c:
        await c.post(f"{TG_API_url}/deleteWebhook", timeout=10)
        logger.info("Webhook removed")

def start_server(queue, token):
    global update_queue, bot_token
    update_queue = queue
    bot_token = token
    from aiohttp import web
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.router.add_get("/health", handle_health)
    logger.info(f"Starting webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT, print=None)
