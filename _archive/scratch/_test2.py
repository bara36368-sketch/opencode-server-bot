import httpx, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
t = os.environ.get('TELEGRAM_BOT_TOKEN', '')
c = httpx.Client()
r = c.get(f'https://api.telegram.org/bot{t}/getMe')
print('Bot:', r.json()['result']['username'])
r2 = c.get(f'https://api.telegram.org/bot{t}/getUpdates', params={'limit': 5, 'timeout': 2})
d = r2.json()
results = d.get('result', [])
print(f'Pending: {len(results)} updates')
for u in results:
    msg = u.get('message', {})
    print(f'  update_id={u["update_id"]} from={msg.get("from",{}).get("first_name","?")}: {msg.get("text","")}')
