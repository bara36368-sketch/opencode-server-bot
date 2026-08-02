import httpx, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
t = os.environ.get('TELEGRAM_BOT_TOKEN', '')
chat_id = 8585609360
r = httpx.get(f'https://api.telegram.org/bot{t}/getUpdates', params={'limit': 3}, timeout=10)
d = r.json()
print("Updates:", d)
results = d.get('result', [])
if results:
    last = results[-1]
    cid = last.get('message', {}).get('chat', {}).get('id')
    print(f"Last chat_id from updates: {cid}")
    print(f"Trying to send test to chat_id={cid}...")
    r2 = httpx.post(f'https://api.telegram.org/bot{t}/sendMessage', json={'chat_id': cid, 'text': 'Test from script'}, timeout=10)
    print("Send result:", r2.json())
else:
    print("No pending updates. Sending test to 8585609360...")
    r2 = httpx.post(f'https://api.telegram.org/bot{t}/sendMessage', json={'chat_id': 8585609360, 'text': 'Test from script'}, timeout=10)
    print("Send result:", r2.json())
