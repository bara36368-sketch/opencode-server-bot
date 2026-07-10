import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "set-via-env-var")

from a2wsgi import ASGIMiddleware
from webhook_app import app as fastapi_app

app = ASGIMiddleware(fastapi_app)