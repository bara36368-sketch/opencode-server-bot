import sys, os, json, asyncio, logging, time, base64, re

DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=os.path.join(DIR, "whatsapp.log"), level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

SIDECAR = ["node", os.path.join(DIR, "whatsapp", "sidecar.js")]
SEND_DELAY = 1.5
SESSIONS = {}

sys.path.insert(0, DIR)
from opencode_bot import smart_call, PROVIDERS, bf

def log(msg):
    print(f"[wa] {msg}", flush=True)
    logging.info(msg)

async def send_msg(sock, jid, text):
    text = str(text)[:4000]
    cmd = json.dumps({"type": "send", "to": jid, "text": text}) + "\n"
    if sock.stdin:
        sock.stdin.write(cmd.encode())
        await sock.stdin.drain()
    await asyncio.sleep(SEND_DELAY)

async def read_stdout(sock, queue):
    while True:
        line = await sock.stdout.readline()
        if not line:
            await queue.put({"type": "sidecar_exit"})
            break
        try:
            msg = json.loads(line.strip())
            await queue.put(msg)
        except json.JSONDecodeError:
            pass

def pick_provider():
    best, best_score = None, 0
    for name, p in PROVIDERS.items():
        score = 0
        if p.get("key") and p["key"] not in ("set-via-env-var", "", "free"):
            score += 2
        if p.get("url"):
            score += 1
        if score > best_score:
            best, best_score = name, score
    return best or "groq"

async def handle_message(msg, sock):
    jid = msg["from"]
    text = msg["text"]
    push = msg.get("pushName", "")
    log(f"Msg from {jid} ({push}): {text[:60]}")

    SESSIONS.setdefault(jid, [])
    agent_prompt = "You are a helpful AI assistant on WhatsApp."
    if not SESSIONS[jid]:
        SESSIONS[jid].append({"role": "system", "content": agent_prompt})
    SESSIONS[jid].append({"role": "user", "content": text})
    if len(SESSIONS[jid]) > 20:
        SESSIONS[jid] = SESSIONS[jid][:1] + SESSIONS[jid][-10:]

    provider = pick_provider()
    try:
        reply = await smart_call(SESSIONS[jid][-15:], provider)
        SESSIONS[jid].append({"role": "assistant", "content": reply})
        await send_msg(sock, jid, reply)
    except Exception as e:
        log(f"Error handling message: {e}")
        await send_msg(sock, jid, f"Error: {e}")

async def run(pair_phone=None):
    loop = asyncio.get_event_loop()
    sock = await asyncio.create_subprocess_exec(
        *SIDECAR, stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE, stderr=None,
        cwd=DIR,
    )
    queue = asyncio.Queue()
    reader = asyncio.create_task(read_stdout(sock, queue))

    log("Sidecar started.")
    paired = False

    while True:
        msg = await queue.get()
        t = msg.get("type")

        if t == "qr":
            qr_raw = msg.get("qr", "")
            import qrcode
            qr = qrcode.QRCode()
            qr.add_data(qr_raw)
            print("\n" + "=" * 50, flush=True)
            print("SCAN THIS QR CODE WITH WHATSAPP:", flush=True)
            print("(Open WhatsApp > Linked Devices > Link a Device)", flush=True)
            print("=" * 50, flush=True)
            qr.print_ascii()
            print("=" * 50 + "\n", flush=True)
            log("QR displayed above")
        elif t == "ready":
            log("WhatsApp connected!")
        elif t == "connecting":
            log("Connecting...")
            if pair_phone and not paired:
                paired = True
                cmd = json.dumps({"type": "pair", "phone": pair_phone}) + "\n"
                sock.stdin.write(cmd.encode())
                await sock.stdin.drain()
        elif t == "pair_code":
            code = msg.get("code", "")
            print("\n" + "=" * 50, flush=True)
            print("PAIRING CODE:", flush=True)
            print("Open WhatsApp > Linked Devices > Link with Phone Number", flush=True)
            print("Enter this code:", flush=True)
            print("=" * 50, flush=True)
            print(f"    {code}", flush=True)
            print("=" * 50 + "\n", flush=True)
            log(f"Pairing code: {code}")
        elif t == "close":
            reason = msg.get("reason", "unknown")
            log(f"Disconnected (reason: {reason}), reconnecting...")
            if reason == 401:
                log("Logged out, delete auth_info and restart")
                break
            await asyncio.sleep(5)
            return
        elif t == "auth_expired":
            log("Auth expired, restarting to generate new QR...")
            return
        elif t == "sidecar_exit":
            log("Sidecar process exited")
            break
        elif t == "message":
            await handle_message(msg, sock)
        elif t == "error":
            log(f"Sidecar error: {msg.get('msg', 'unknown')}")

    sock.terminate()
    await sock.wait()

async def main():
    pair_phone = None
    if "--pair" in sys.argv:
        idx = sys.argv.index("--pair")
        if idx + 1 < len(sys.argv):
            pair_phone = re.sub(r"\D", "", sys.argv[idx + 1])
    while True:
        try:
            await run(pair_phone)
        except Exception as e:
            log(f"Fatal: {e}")
        log("Restarting in 5s...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
