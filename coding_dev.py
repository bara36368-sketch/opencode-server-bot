import json, os, time, subprocess, tempfile, hashlib
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_CONFIG_FILE = os.path.join(BASE_DIR, "dev_tools_config.json")

def _load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default if default is not None else {}

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

SUPPORTED_LANGUAGES = {
    "python": {"ext": ".py", "cmd": "python", "timeout": 30},
    "javascript": {"ext": ".js", "cmd": "node", "timeout": 30},
    "bash": {"ext": ".sh", "cmd": "bash", "timeout": 15},
    "powershell": {"ext": ".ps1", "cmd": "powershell", "timeout": 15},
}

class CodingDevTools:
    def __init__(self):
        self.config = _load_json(DEV_CONFIG_FILE, {})
        self.sessions = {}
        self.github_tokens = {}

    def _save(self):
        _save_json(DEV_CONFIG_FILE, self.config)

    def get_user_session(self, user_id):
        uid = str(user_id)
        if uid not in self.sessions:
            self.sessions[uid] = {
                "cwd": os.path.expanduser("~"),
                "history": [],
                "active_project": None,
            }
        return self.sessions[uid]

    def set_working_dir(self, user_id, path):
        session = self.get_user_session(user_id)
        expanded = os.path.expanduser(path)
        if os.path.isdir(expanded):
            session["cwd"] = expanded
            return True, f"Working directory: {expanded}"
        return False, f"Directory not found: {path}"

    def get_working_dir(self, user_id):
        session = self.get_user_session(user_id)
        return session.get("cwd", os.path.expanduser("~"))

    async def execute_code(self, user_id, code, language="python"):
        lang = SUPPORTED_LANGUAGES.get(language)
        if not lang:
            return False, f"Unsupported language: {language}. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        session = self.get_user_session(user_id)
        cwd = session.get("cwd", os.path.expanduser("~"))
        if not os.path.isdir(cwd):
            cwd = os.path.expanduser("~")
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=lang["ext"], delete=False, encoding="utf-8") as f:
                f.write(code)
                tmp_path = f.name
            cmd = [lang["cmd"], tmp_path]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=lang["timeout"])
            output = stdout.decode("utf-8", errors="replace")[:5000]
            errors = stderr.decode("utf-8", errors="replace")[:3000]
            exit_code = proc.returncode
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            result = {
                "language": language,
                "exit_code": exit_code,
                "stdout": output,
                "stderr": errors,
                "cwd": cwd,
                "time": time.time(),
            }
            session["history"].append(result)
            if len(session["history"]) > 50:
                session["history"] = session["history"][-25:]
            if exit_code == 0:
                return True, f"✅ Exit 0\n{output}" if output else "✅ Exit 0 (no output)"
            else:
                msg = f"❌ Exit {exit_code}\n"
                if output: msg += f"Output:\n{output}\n"
                if errors: msg += f"Error:\n{errors}"
                return False, msg[:5000]
        except asyncio.TimeoutError:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return False, f"⏰ Timeout ({lang['timeout']}s limit)"
        except Exception as e:
            return False, f"Error: {str(e)[:500]}"

    def list_history(self, user_id, limit=10):
        session = self.get_user_session(user_id)
        history = session.get("history", [])[-limit:]
        if not history:
            return "No execution history."
        lines = ["Execution history:"]
        for i, h in enumerate(history, 1):
            status = "✅" if h.get("exit_code") == 0 else "❌"
            lines.append(f"  {i}. {status} {h.get('language', '?')} (exit {h.get('exit_code', '?')})")
        return "\n".join(lines)

    def clear_history(self, user_id):
        session = self.get_user_session(user_id)
        session["history"] = []
        return "History cleared."

    def set_github_token(self, user_id, token):
        uid = str(user_id)
        self.github_tokens[uid] = token
        return "GitHub token set."

    async def github_api(self, user_id, endpoint, method="GET", data=None):
        uid = str(user_id)
        token = self.github_tokens.get(uid)
        if not token:
            return False, "GitHub token not set. Use /dev github-token <token>"
        try:
            import httpx
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            async with httpx.AsyncClient(timeout=30) as c:
                if method == "GET":
                    r = await c.get(f"https://api.github.com{endpoint}", headers=headers)
                elif method == "POST":
                    r = await c.post(f"https://api.github.com{endpoint}", headers=headers, json=data)
                else:
                    return False, f"Unsupported method: {method}"
                if r.status_code == 200:
                    return True, json.dumps(r.json(), indent=2)[:5000]
                else:
                    return False, f"GitHub API error {r.status_code}: {r.text[:1000]}"
        except Exception as e:
            return False, f"GitHub API error: {str(e)[:500]}"

    async def github_repos(self, user_id):
        return await self.github_api(user_id, "/user/repos?sort=updated&per_page=10")

    async def github_issues(self, user_id, repo):
        return await self.github_api(user_id, f"/repos/{repo}/issues?state=open&per_page=10")

    async def github_prs(self, user_id, repo):
        return await self.github_api(user_id, f"/repos/{repo}/pulls?state=open&per_page=10")

    async def generate_api_docs(self, file_path, doc_type="openapi"):
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            if doc_type == "openapi":
                doc = self._generate_openapi(content, file_path)
            elif doc_type == "readme":
                doc = self._generate_readme(content, file_path)
            else:
                return False, f"Unknown doc type: {doc_type}"
            return True, doc
        except Exception as e:
            return False, f"Error: {str(e)[:500]}"

    def _generate_openapi(self, content, filename):
        lines = ["---", "openapi: 3.0.0", f"info:", f"  title: {os.path.basename(filename)} API", "  version: 1.0.0", "paths:"]
        import re
        endpoints = re.findall(r'(?:"/[\w/]+"|\'/[\w/]+\')', content)
        for ep in set(endpoints):
            ep_clean = ep.strip("'\"")
            lines.append(f"  {ep_clean}:")
            lines.append(f"    get:")
            lines.append(f"      responses:")
            lines.append(f"        '200':")
            lines.append(f"          description: Success")
        if len(endpoints) == 0:
            lines.append("  /:")
            lines.append("    get:")
            lines.append("      responses:")
            lines.append("        '200':")
            lines.append("          description: Success")
        return "\n".join(lines)

    def _generate_readme(self, content, filename):
        import re
        basename = os.path.basename(filename)
        funcs = re.findall(r'(?:async\s+)?(?:def|function)\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        lines = [f"# {basename}", "", "## Overview", f"Source: `{basename}`", ""]
        if classes:
            lines.append("## Classes")
            for c in classes[:20]:
                lines.append(f"- `{c}`")
            lines.append("")
        if funcs:
            lines.append("## Functions")
            for f in funcs[:30]:
                lines.append(f"- `{f}()`")
            lines.append("")
        lines.append(f"## Stats")
        lines.append(f"- Lines: {len(content.splitlines())}")
        lines.append(f"- Functions: {len(funcs)}")
        lines.append(f"- Classes: {len(classes)}")
        return "\n".join(lines)

_dev = None
def get_dev_tools():
    global _dev
    if _dev is None:
        _dev = CodingDevTools()
    return _dev
