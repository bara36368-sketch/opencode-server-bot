"""Google Drive helper for the File Editor — public-link downloads with zero
setup (stdlib only); optional service-account uploads when credentials exist.

Input flow:  user pastes a drive.google.com link -> parse id -> streaming
download (handles the big-file confirm-token dance) -> local path.
Output flow: edited file <=50MB goes back via Telegram; larger files upload
to Drive IF a service account is configured, else stay local with a notice.
"""
import json
import os
import re
import urllib.request
import urllib.parse

DIR = os.path.dirname(os.path.abspath(__file__))
SA_PATH = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON", "")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")

_DRIVE_ID_PATTERNS = [
    r"/file/d/([A-Za-z0-9_-]{10,})",
    r"[?&]id=([A-Za-z0-9_-]{10,})",
    r"/d/([A-Za-z0-9_-]{10,})",
]


def parse_drive_link(text):
    """Extract a Drive file id from any pasted link/text. Returns id or None."""
    if not text:
        return None
    for pat in _DRIVE_ID_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def _confirm_token_for(file_id):
    """Big files hit an interstitial; fetch its confirm token + uuid."""
    url = ("https://drive.google.com/uc?export=download&"
           + urllib.parse.urlencode({"id": file_id}))
    req = urllib.request.Request(url)
    token = uuid = ""
    html = ""
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
            cookie = r.headers.get("Set-Cookie", "")
            m = re.search(r'download_warning[^=]*=([^;]+)', cookie or "")
            if m:
                token = m.group(1)
    except Exception:
        return "", ""
    if not token and html:
        m = re.search(r'name="confirm"\s+value="([^"]+)"', html)
        if m:
            token = m.group(1)
        m2 = re.search(r'name="uuid"\s+value="([^"]+)"', html)
        if m2:
            uuid = m2.group(1)
    return token, uuid


def download_public_drive_file(file_id, dest_dir, max_mb=1024.0, name_hint=""):
    """Stream a publicly-shared Drive file to dest_dir. Returns local path."""
    os.makedirs(dest_dir, exist_ok=True)
    params = {"export": "download", "id": file_id, "confirm": "t"}
    token, uuid = _confirm_token_for(file_id)
    if token:
        params["confirm"] = token
    if uuid:
        params["uuid"] = uuid
    url = "https://drive.google.com/uc?" + urllib.parse.urlencode(params)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name_hint or f"gdrive_{file_id[:12]}")[-80:]
    out_path = os.path.join(dest_dir, safe)
    limit = int(max_mb * 1024 * 1024)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    downloaded = 0
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(out_path, "wb") as f:
            ctype = r.headers.get("Content-Type", "")
            while True:
                block = r.read(1024 * 256)
                if not block:
                    break
                downloaded += len(block)
                if downloaded > limit:
                    raise ValueError(f"exceeds {max_mb:.0f}MB limit")
                f.write(block)
        head = open(out_path, "rb").read(4096)
        if b"<html" in head.lower() and b"drive" in head.lower():
            os.remove(out_path)
            raise PermissionError("file is not publicly shared (got HTML page)")
        if downloaded == 0:
            os.remove(out_path)
            raise IOError("empty response from Drive")
        return out_path
    except Exception:
        if os.path.exists(out_path) and os.path.getsize(out_path) == 0:
            os.remove(out_path)
        raise


def _service_account_available():
    if not SA_PATH or not os.path.exists(SA_PATH):
        return False
    try:
        import google.auth          # noqa: F401
        import googleapiclient      # noqa: F401
        return True
    except ImportError:
        return False


def upload_to_drive(local_path, folder_id=None):
    """Upload the edited file via service account. Returns share link or None.
    Requires: GDRIVE_SERVICE_ACCOUNT_JSON env + google-api-python_client installed
    + the SA email added as editor on the target folder."""
    if not _service_account_available():
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        creds = service_account.Credentials.from_service_account_file(
            SA_PATH, scopes=["https://www.googleapis.com/auth/drive"])
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        meta = {"name": os.path.basename(local_path)}
        if folder_id or GDRIVE_FOLDER_ID:
            meta["parents"] = [folder_id or GDRIVE_FOLDER_ID]
        media = MediaFileUpload(local_path, resumable=True)
        f = svc.files().create(body=meta, media_body=media,
                               fields="id, webViewLink").execute()
        try:
            svc.permissions().create(fileId=f["id"],
                                     body={"role": "reader", "type": "anyone"}).execute()
        except Exception:
            pass
        return f.get("webViewLink") or f"https://drive.google.com/file/d/{f['id']}/view"
    except Exception:
        return None
