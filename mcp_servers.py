"""MCP servers for the cyberdeck/opencode bot ecosystem.

Zero-dependency stdio JSON-RPC MCP servers (works in Termux + Windows, no pip
install needed). Three servers, selected by the first CLI argument:

  python mcp_servers.py free-llm     # ranked free-tier LLM chain  -> call_coding
  python mcp_servers.py telegram     # Telegram sending             -> bot send / TG API
  python mcp_servers.py cyberdeck    # parametric OpenSCAD enclosure -> ParametricEnclosureGenerator

Each speaks MCP over stdio: reads line-delimited JSON-RPC 2.0 from stdin and
writes responses to stdout. Test a server without a client:

  python mcp_servers.py free-llm --test 'explain json in 3 lines'
"""

import asyncio
import json
import os
import sys
import threading

_PROTOCOL_VERSION = "2025-06-18"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_STDOUT = sys.stdout


# ---------------------------------------------------------------------- loop
_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True, name="mcp-loop").start()


def run_async(coro, timeout=300):
    """Run a coroutine on the shared background loop and return its result."""
    fut = asyncio.run_coroutine_threadsafe(coro, _loop)
    return fut.result(timeout=timeout)


# --------------------------------------------------------------- MCP plumbing
def _read_line():
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    return line or None


def _write(obj):
    try:
        _STDOUT.write(json.dumps(obj, ensure_ascii=False) + "\n")
        _STDOUT.flush()
    except Exception:
        pass


class Tool:
    def __init__(self, name, description, schema, handler):
        self.name = name
        self.description = description
        self.schema = schema
        self.handler = handler

    def to_mcp(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.schema,
        }


class MCPServer:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.tools = {}

    def tool(self, name, description, schema):
        def deco(fn):
            self.tools[name] = Tool(name, description, schema, fn)
            return fn
        return deco

    def _handle(self, req):
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}

        if method == "initialize":
            client_proto = params.get("protocolVersion")
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": client_proto or _PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.name, "version": self.version},
                },
            }
        if method in ("notifications/initialized", "notifications/cancelled"):
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        if method == "tools/list":
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"tools": [t.to_mcp() for t in self.tools.values()]},
            }
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            tool = self.tools.get(name)
            if not tool:
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {name}"},
                }
            try:
                text = tool.handler(args)
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": str(text)}],
                               "isError": False},
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text",
                                            "text": f"error: {e}"}],
                               "isError": True},
                }
        if method is None and req.get("jsonrpc"):
            return None
        return {
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    def serve(self):
        while True:
            line = _read_line()
            if line is None:
                break
            try:
                req = json.loads(line)
            except Exception:
                continue
            if not isinstance(req, dict):
                continue
            resp = self._handle(req)
            if resp is not None:
                _write(resp)


def _coerce_messages(messages):
    """Accept a plain string, a single {role,content}, or a list of them."""
    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    if isinstance(messages, dict):
        return [messages]
    out = []
    for m in messages:
        if isinstance(m, str):
            out.append({"role": "user", "content": m})
        else:
            out.append({"role": m.get("role", "user"),
                        "content": str(m.get("content", ""))})
    return out


# ====================================================================== tools
def build_free_llm_server():
    from cyberdeck_bot import call_coding, _coding_chain, PROVIDERS, load_providers
    load_providers()

    srv = MCPServer("free-llm-mcp", "1.0.0")

    @srv.tool(
        "chat",
        "Send a prompt through the bot's ranked free-tier LLM chain. "
        "Returns the best available model's answer, falling back across providers "
        "on failure. Chain order follows the coder priority (e.g. groq, kimi, "
        "nvidia, deepseek, cerebras, openrouter).",
        {
            "type": "object",
            "properties": {
                "messages": {
                    "description": "Prompt string, or [{role,content}...] messages",
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "object"}},
                        {"type": "object"},
                    ],
                },
                "chain": {
                    "description": "Optional provider order override, e.g. ['groq','kimi']",
                    "type": "array", "items": {"type": "string"},
                },
            },
            "required": ["messages"],
        },
    )
    def chat(args):
        msgs = _coerce_messages(args.get("messages"))
        chain = args.get("chain")
        if chain:
            chain = [p for p in chain if p in PROVIDERS]
        reply, provider, used = run_async(call_coding(msgs, chain))
        meta = f"[provider: {provider}]"
        if reply.startswith("No coding") or reply.startswith("All coding"):
            return f"error: {reply}"
        return f"{meta}\n\n{reply}"

    @srv.tool(
        "coding_chain",
        "Return the active ranked free-tier provider chain the LLM router uses.",
        {"type": "object", "properties": {}},
    )
    def coding_chain(args):
        return json.dumps(_coding_chain())

    return srv


def build_telegram_server():
    from cyberdeck_bot import send

    srv = MCPServer("telegram-mcp", "1.0.0")

    @srv.tool(
        "send_message",
        "Send a text message to a Telegram chat/channel/group via the bot. "
        "chat is the numeric chat_id.",
        {
            "type": "object",
            "properties": {
                "chat": {"type": "integer", "description": "Telegram chat_id"},
                "text": {"type": "string"},
                "parse_mode": {"type": "string", "enum": ["HTML", "Markdown", ""]},
            },
            "required": ["chat", "text"],
        },
    )
    def send_message(args):
        chat = args["chat"]
        text = str(args.get("text", ""))
        if not text:
            return "error: text is empty"
        parse_mode = args.get("parse_mode") or "HTML"
        res = run_async(send(chat, text, parse_mode=parse_mode), timeout=60)
        return json.dumps(res)

    @srv.tool(
        "get_me",
        "Return the bot identity (username, id) from the Telegram API.",
        {"type": "object", "properties": {}},
    )
    def get_me(args):
        import urllib.request
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return "error: TELEGRAM_BOT_TOKEN not set"
        try:
            with urllib.request.urlopen(
                f"https://api.telegram.org/bot{token}/getMe", timeout=15
            ) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return f"error: {e}"

    @srv.tool(
        "send_chat_action",
        "Set a typing/recording action on a chat while processing.",
        {
            "type": "object",
            "properties": {
                "chat": {"type": "integer"},
                "action": {"type": "string", "enum": ["typing", "upload_photo", "record_video", "find_location"]},
            },
            "required": ["chat"],
        },
    )
    def send_chat_action(args):
        import urllib.request
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return "error: TELEGRAM_BOT_TOKEN not set"
        body = json.dumps({"chat_id": args["chat"], "action": args.get("action", "typing")}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendChatAction",
            data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return f"error: {e}"

    return srv


def build_cyberdeck_server():
    from cyberdeck_agent import ParametricEnclosureGenerator

    srv = MCPServer("cyberdeck-mcp", "1.0.0")
    gen = ParametricEnclosureGenerator

    @srv.tool(
        "generate_openscad",
        "Generate a parametric OpenSCAD enclosure for a cyberdeck build. "
        "sbc_key/display_key/battery_key from part_keys; returns full SCAD source.",
        {
            "type": "object",
            "properties": {
                "sbc_key": {"type": "string", "description": "e.g. rpi5, rpi4, orangepi5, rock5b, jetson_nano"},
                "display_key": {"type": "string", "description": "e.g. hdmi7, dsi5, oled128x64, tft3.5"},
                "battery_key": {"type": "string", "description": "e.g. npf550, npf970, 18650_4, lipo_10000"},
                "material": {"type": "string", "enum": ["pla", "petg", "abs", "wood_pla"]},
                "style": {"type": "string", "enum": ["minimal", "tactical", "cyberpunk", "retro", "solarpunk"]},
                "nato_rails": {"type": "boolean"},
                "vent_holes": {"type": "boolean"},
                "has_antenna_mount": {"type": "boolean"},
            },
            "required": ["sbc_key", "display_key", "battery_key"],
        },
    )
    def generate_openscad(args):
        code = gen.generate_openscad(
            sbc_key=args["sbc_key"],
            display_key=args["display_key"],
            battery_key=args["battery_key"],
            material=args.get("material", "pla"),
            style=args.get("style", "minimal"),
            nato_rails=bool(args.get("nato_rails", False)),
            vent_holes=bool(args.get("vent_holes", True)),
            has_antenna_mount=bool(args.get("has_antenna_mount", False)),
        )
        return code

    @srv.tool(
        "enclosure_dimensions",
        "Compute enclosure width/depth/height/volume in mm for a part combo.",
        {
            "type": "object",
            "properties": {
                "sbc_key": {"type": "string"},
                "display_key": {"type": "string"},
                "battery_key": {"type": "string"},
            },
            "required": ["sbc_key", "display_key", "battery_key"],
        },
    )
    def enclosure_dimensions(args):
        dims = gen.compute_enclosure_dimensions(
            args["sbc_key"], args["display_key"], args["battery_key"])
        return json.dumps(dims)

    @srv.tool(
        "style_presets",
        "List available enclosure design styles and their properties.",
        {"type": "object", "properties": {}},
    )
    def style_presets(args):
        return json.dumps(gen.style_presets())

    @srv.tool(
        "part_keys",
        "List valid sbc_key / display_key / battery_key options for the enclosure tools.",
        {"type": "object", "properties": {}},
    )
    def part_keys(args):
        return json.dumps({
            "sbc": ["rpi5", "rpi4", "rpi3", "orangepi5", "rock5b", "jetson_nano", "radxa_zero3", "esp32s3"],
            "display": ["hdmi5", "hdmi7", "hdmi10", "dsi5", "dsi7", "oled128x64", "tft3.5", "tft2.8"],
            "battery": ["npf550", "npf970", "18650_2", "18650_4", "18650_6", "lipo_5000", "lipo_10000"],
        })

    return srv


BUILDERS = {
    "free-llm": build_free_llm_server,
    "telegram": build_telegram_server,
    "cyberdeck": build_cyberdeck_server,
}


# ------------------------------------------------------------------- selftest
def _self_test(srv, prompt):
    print(f"== {srv.name} tools ==")
    for t in srv.tools.values():
        print(f"  - {t.name}: {t.description.splitlines()[0]}")

    def call(name, args):
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": name, "arguments": args}})
        srv._handle(json.loads(line))

    print(f"\n== chat ==\n{srv.tools['chat'].handler({'messages': prompt})[:1200]}\n")
    print("== generate_openscad ==\n"
          + srv.tools['generate_openscad'].handler(
              {"sbc_key": "rpi5", "display_key": "hdmi7", "battery_key": "npf970"})[:400])


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        print("Available servers: " + ", ".join(BUILDERS) +
              "\nTest: python mcp_servers.py <server> --test '<prompt>'")
        return 0

    key = args[0]
    if key not in BUILDERS:
        print(f"Unknown server '{key}'. Choose from: {', '.join(BUILDERS)}")
        return 1

    # Keep the stdio protocol pure: any stray prints from imported bot modules
    # go to stderr; responses go to the real stdout via _STDOUT.
    sys.stdout = sys.stderr

    server = BUILDERS[key]()

    if "--test" in args:
        i = args.index("--test")
        prompt = args[i + 1] if len(args) > i + 1 else "explain MCP in 3 lines"
        _self_test(server, prompt)
        return 0

    server.serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
