import httpx, os, sys

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "set-via-env-var")
TG_API = f"https://api.telegram.org/bot{TOKEN}"

async def register():
    if len(sys.argv) < 2:
        print("Usage: python register_webhook.py <your-pythonanywhere-domain>")
        print("Example: python register_webhook.py yourusername.pythonanywhere.com")
        sys.exit(1)

    domain = sys.argv[1]
    if not domain.startswith("https://"):
        domain = f"https://{domain}"
    if domain.endswith("/"):
        domain = domain.rstrip("/")
    webhook_url = f"{domain}/telegram-webhook"

    async with httpx.AsyncClient() as c:
        r = await c.post(f"{TG_API}/deleteWebhook")
        print("Delete webhook:", r.json())

        r = await c.post(f"{TG_API}/setWebhook", json={
            "url": webhook_url,
            "allowed_updates": ["message"],
            "max_connections": 10,
        })
        data = r.json()
        if data.get("ok"):
            print(f"Webhook set to: {webhook_url}")
        else:
            print(f"Failed: {data}")

        r = await c.get(f"{TG_API}/getWebhookInfo")
        print("Webhook info:", r.json())

if __name__ == "__main__":
    import asyncio
    asyncio.run(register())
