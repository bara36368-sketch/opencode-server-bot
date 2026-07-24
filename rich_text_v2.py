"""Rich Text v2 — Telegram Bot API 10.1 Rich Messages (tables, collapsible, math, slideshows)."""
import os, json, re, time, html as html_mod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RICH_V2_FILE = os.path.join(BASE_DIR, "rich_text_v2_data.json")

class RichTextV2:
    def __init__(self):
        self.data = self._load()
        self.enabled = True

    def _load(self):
        if os.path.exists(RICH_V2_FILE):
            try:
                with open(RICH_V2_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"stats": {"messages_richified": 0, "blocks_used": 0}}

    def _save(self):
        tmp = RICH_V2_FILE + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, RICH_V2_FILE)
        except Exception:
            pass

    def richify(self, text):
        """Convert plain/markdown text to Telegram Rich Message HTML."""
        if not text:
            return text
        if not self.enabled:
            return text
        try:
            html = self._markdown_to_rich_html(text)
            self.data["stats"]["messages_richified"] = self.data["stats"].get("messages_richified", 0) + 1
            self._save()
            return html
        except Exception:
            return text

    def _markdown_to_rich_html(self, text):
        lines = text.split("\n")
        result = []
        in_code = False
        code_lang = ""
        code_lines = []
        in_table = False
        table_rows = []
        in_details = False
        details_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code:
                    result.append(self._code_block("\n".join(code_lines), code_lang))
                    code_lines = []
                    in_code = False
                    code_lang = ""
                else:
                    if in_table:
                        result.append(self._table_block(table_rows))
                        table_rows = []
                        in_table = False
                    in_code = True
                    code_lang = stripped[3:].strip()
                continue

            if in_code:
                code_lines.append(line)
                continue

            if stripped.startswith("<details>") or stripped.startswith("<details "):
                in_details = True
                details_lines = [stripped]
                continue

            if in_details:
                details_lines.append(stripped)
                if stripped == "</details>":
                    result.append(self._details_block(details_lines))
                    details_lines = []
                    in_details = False
                continue

            if self._is_table_row(stripped):
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(stripped)
                continue
            elif in_table:
                result.append(self._table_block(table_rows))
                table_rows = []
                in_table = False

            if stripped.startswith("# "):
                result.append(f"<b>{self._inline_format(stripped[2:])}</b>")
            elif stripped.startswith("## "):
                result.append(f"<b>{self._inline_format(stripped[3:])}</b>")
            elif stripped.startswith("### "):
                result.append(f"<b>{self._inline_format(stripped[4:])}</b>")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                result.append(f"  • {self._inline_format(stripped[2:])}")
            elif stripped.startswith("$$") and stripped.endswith("$$"):
                formula = stripped[2:-2].strip()
                result.append(self._math_block(formula))
            elif stripped.startswith("$") and stripped.endswith("$") and len(stripped) > 2:
                formula = stripped[1:-1].strip()
                result.append(self._math_inline(formula))
            elif stripped.startswith("> "):
                result.append(f"❝ {self._inline_format(stripped[2:])}")
            elif stripped.startswith("---"):
                result.append("─" * 30)
            elif stripped == "":
                result.append("")
            else:
                result.append(self._inline_format(stripped))

        if in_code and code_lines:
            result.append(self._code_block("\n".join(code_lines), code_lang))
        if in_table and table_rows:
            result.append(self._table_block(table_rows))
        if in_details and details_lines:
            result.append(self._details_block(details_lines))

        return "\n".join(result)

    def _is_table_row(self, line):
        if not line.startswith("|") or not line.endswith("|"):
            return False
        inner = line[1:-1]
        cells = [c.strip() for c in inner.split("|")]
        if all(re.match(r'^[-:]+$', c) for c in cells if c):
            return True
        return len(cells) >= 2

    def _table_block(self, rows):
        if len(rows) < 2:
            return "\n".join(rows)
        header = rows[0]
        data_rows = rows[2:] if len(rows) > 2 else rows[1:]
        hcells = [self._inline_format(c.strip()) for c in header[1:-1].split("|")]
        lines = ["<b>" + " | ".join(hcells) + "</b>"]
        lines.append("─" * 40)
        for row in data_rows:
            cells = [self._inline_format(c.strip()) for c in row[1:-1].split("|")]
            lines.append(" | ".join(cells))
        return "\n".join(lines)

    def _code_block(self, code, lang=""):
        escaped = html_mod.escape(code)
        if lang:
            return f"<pre><code class=\"language-{lang}\">{escaped}</code></pre>"
        return f"<pre><code>{escaped}</code></pre>"

    def _details_block(self, lines):
        summary = ""
        content = []
        for line in lines:
            if line.startswith("<summary>"):
                summary = line.replace("<summary>", "").replace("</summary>", "").strip()
            elif line == "<details>" or line == "</details>" or line == "<summary>" or line == "</summary>":
                continue
            else:
                content.append(line)
        if not summary:
            summary = "Click to expand"
        content_text = "\n".join(content)
        return f"<details><summary><b>{html_mod.escape(summary)}</b></summary>\n{content_text}\n</details>"

    def _math_block(self, formula):
        return f"<pre><code class=\"math\">{html_mod.escape(formula)}</code></pre>"

    def _math_inline(self, formula):
        return f"<code class=\"math\">{html_mod.escape(formula)}</code>"

    def _inline_format(self, text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
        text = re.sub(r'\|\|(.+?)\|\|', r'<span class="tg-spoiler">\1</span>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        return text

    def format_with_rich(self, text, method="html"):
        """Return dict for sendMessage with rich content."""
        html_content = self.richify(text)
        return {
            "text": html_content,
            "parse_mode": "HTML",
            "entities": [],
        }

    def get_stats(self):
        return {
            "enabled": self.enabled,
            "messages_richified": self.data["stats"].get("messages_richified", 0),
            "blocks_used": self.data["stats"].get("blocks_used", 0),
        }

_rich_v2 = None
def get_rich_v2():
    global _rich_v2
    if _rich_v2 is None:
        _rich_v2 = RichTextV2()
    return _rich_v2

def format_rich_response(text, method="html"):
    rt = get_rich_v2()
    return rt.format_with_rich(text, method)
