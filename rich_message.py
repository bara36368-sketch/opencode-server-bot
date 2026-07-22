import re, json

def markdown_to_rich_blocks(text):
    blocks = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_table = False
    table_headers = []
    table_rows = []
    in_list = []
    list_items = []

    def flush_code():
        nonlocal code_lines, code_lang
        if code_lines:
            code_text = "\n".join(code_lines)
            blocks.append({"type": "code", "text": code_text})
            if code_lang:
                blocks[-1]["language"] = code_lang
            code_lines = []
            code_lang = ""

    def flush_table():
        nonlocal table_headers, table_rows, in_table
        if table_headers or table_rows:
            blocks.append({"type": "table", "headers": table_headers, "rows": table_rows})
            table_headers = []
            table_rows = []
            in_table = False

    def flush_list():
        nonlocal list_items, in_list
        if list_items:
            blocks.append({"type": "list", "items": list_items, "ordered": in_list and in_list[-1] == "ordered"})
            list_items = []
            in_list = []

    def parse_inline(t):
        segments = []
        pos = 0
        while pos < len(t):
            m = re.match(r'\*\*(.+?)\*\*', t[pos:])
            if m:
                segments.append({"type": "bold", "text": m.group(1)})
                pos += m.end()
                continue
            m = re.match(r'\*(.+?)\*', t[pos:])
            if m:
                segments.append({"type": "italic", "text": m.group(1)})
                pos += m.end()
                continue
            m = re.match(r'`(.+?)`', t[pos:])
            if m:
                segments.append({"type": "code", "text": m.group(1)})
                pos += m.end()
                continue
            m = re.match(r'~~(.+?)~~', t[pos:])
            if m:
                segments.append({"type": "strikethrough", "text": m.group(1)})
                pos += m.end()
                continue
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', t[pos:])
            if m:
                segments.append({"type": "url", "text": m.group(1), "url": m.group(2)})
                pos += m.end()
                continue
            remaining = t[pos:]
            next_special = re.search(r'\*\*|\*|`|~~|\[', remaining)
            if next_special:
                raw = remaining[:next_special.start()]
                if raw:
                    segments.append({"type": "plain", "text": raw})
                pos += next_special.start()
            else:
                if remaining:
                    segments.append({"type": "plain", "text": remaining})
                pos = len(t)
        return segments if segments else [{"type": "plain", "text": t}]

    for line in text.split("\n"):
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if re.match(r'^\|.*\|$', stripped) and "|" in stripped[1:-1]:
            flush_list()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                in_table = True
                table_headers = cells
            else:
                table_rows.append(cells)
            continue
        else:
            if in_table:
                if table_rows or table_headers:
                    flush_table()
                else:
                    in_table = False

        if stripped.startswith("---") or stripped.startswith("***"):
            flush_list()
            blocks.append({"type": "divider"})
            continue

        h_match = re.match(r'^(#{1,3})\s+(.+)$', stripped)
        if h_match:
            flush_list()
            level = len(h_match.group(1))
            text_content = h_match.group(2)
            blocks.append({"type": "section_heading", "text": text_content, "level": level})
            continue

        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)$', stripped)
        if list_match:
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            item_text = list_match.group(3)
            is_ordered = marker[0].isdigit()
            if not in_list or (in_list and in_list[-1] != ("ordered" if is_ordered else "unordered")):
                flush_list()
                in_list = ["ordered" if is_ordered else "unordered"]
            list_items.append(parse_inline(item_text))
            continue
        else:
            if in_list:
                flush_list()

        if stripped.startswith(">"):
            flush_list()
            quote_text = re.sub(r'^>\s?', '', stripped)
            blocks.append({"type": "block_quotation", "text": quote_text})
            continue

        if stripped == "":
            continue

        flush_list()
        blocks.append({"type": "paragraph", "text": parse_inline(stripped)})

    flush_code()
    flush_table()
    flush_list()

    return blocks

def rich_message_payload(chat_id, blocks, receiver_user_id=None):
    payload = {
        "chat_id": chat_id,
        "rich_message": {"blocks": blocks}
    }
    if receiver_user_id:
        payload["receiver_user_id"] = receiver_user_id
    return payload

def has_rich_content(text):
    return bool(re.search(r'```|^\|.*\|$|^#{1,3}\s|^\d+\.\s|^>\s|^\* |^- ', text, re.MULTILINE))

async def send_rich(http_client, bot_token, chat_id, text, receiver_user_id=None):
    blocks = markdown_to_rich_blocks(text)
    if not blocks:
        return None
    payload = rich_message_payload(chat_id, blocks, receiver_user_id)
    try:
        resp = await http_client.post(
            f"https://api.telegram.org/bot{bot_token}/sendRichMessage",
            json=payload,
            timeout=15
        )
        return resp.json()
    except Exception:
        return None
