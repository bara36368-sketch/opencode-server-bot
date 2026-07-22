import json, os, time, re, hashlib
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_FEATURES_FILE = os.path.join(BASE_DIR, "new_features_config.json")

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

LANGUAGES = {
    "en": "English", "id": "Indonesian", "ms": "Malay", "ar": "Arabic",
    "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese",
    "ko": "Korean", "zh": "Chinese", "ru": "Russian", "pt": "Portuguese",
    "hi": "Hindi", "th": "Thai", "vi": "Vietnamese", "tr": "Turkish",
    "it": "Italian", "nl": "Dutch", "pl": "Polish", "sv": "Swedish",
}

class NewFeatures:
    def __init__(self):
        self.config = _load_json(NEW_FEATURES_FILE, {})
        self.translation_cache = {}

    def _save(self):
        _save_json(NEW_FEATURES_FILE, self.config)

    def get_chat(self, chat_id):
        cid = str(chat_id)
        if cid not in self.config:
            self.config[cid] = {
                "enabled": False,
                "streaming_enabled": True,
                "ocr_enabled": True,
                "translation_enabled": True,
                "default_target_lang": "en",
                "auto_translate": False,
            }
        return self.config[cid]

    def toggle(self, chat_id, feature=None):
        cfg = self.get_chat(chat_id)
        if feature and feature in cfg:
            cfg[feature] = not cfg[feature]
        else:
            cfg["enabled"] = not cfg["enabled"]
        self._save()
        return cfg["enabled"]

    def set_target_lang(self, chat_id, lang_code):
        if lang_code not in LANGUAGES:
            return False, f"Unknown language: {lang_code}. Available: {', '.join(list(LANGUAGES.keys())[:10])}..."
        cfg = self.get_chat(chat_id)
        cfg["default_target_lang"] = lang_code
        self._save()
        return True, f"Default language set to {LANGUAGES[lang_code]}"

    def list_languages(self):
        lines = ["Supported languages:"]
        for code, name in sorted(LANGUAGES.items()):
            lines.append(f"  {code} — {name}")
        return "\n".join(lines)

    async def translate_text(self, text, target_lang, source_lang="auto"):
        if not text or not text.strip():
            return ""
        cache_key = hashlib.md5(f"{text}:{target_lang}:{source_lang}".encode()).hexdigest()
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as c:
                params = {"q": text[:5000], "sl": source_lang, "tl": target_lang, "dt": "t"}
                r = await c.get("https://translate.googleapis.com/translate_a/single", params=params)
                if r.status_code == 200:
                    data = r.json()
                    translated = "".join(part[0] for part in data[0] if part[0])
                    self.translation_cache[cache_key] = translated
                    if len(self.translation_cache) > 1000:
                        keys = list(self.translation_cache.keys())[:500]
                        for k in keys:
                            del self.translation_cache[k]
                    return translated
        except Exception:
            pass
        return f"[Translation to {target_lang} unavailable]"

    def extract_text_from_image_data(self, image_data):
        try:
            import pytesseract
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(img)
            return text.strip()
        except ImportError:
            return None
        except Exception:
            return None

    async def ocr_from_url(self, image_url):
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(image_url)
                if r.status_code == 200:
                    return self.extract_text_from_image_data(r.content)
        except Exception:
            pass
        return None

    async def ocr_from_file(self, file_path):
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return self.extract_text_from_image_data(data)
        except Exception:
            return None

    def format_streaming_chunk(self, text, chunk_size=3):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def calculate_streaming_delay(self, text):
        word_count = len(text.split())
        if word_count < 20:
            return 0.05
        elif word_count < 50:
            return 0.03
        else:
            return 0.02

    def format_config(self, chat_id):
        cfg = self.get_chat(chat_id)
        lines = [
            f"New Features: {'ON' if cfg.get('enabled') else 'OFF'}",
            f"  Streaming: {'ON' if cfg.get('streaming_enabled') else 'OFF'}",
            f"  OCR: {'ON' if cfg.get('ocr_enabled') else 'OFF'}",
            f"  Translation: {'ON' if cfg.get('translation_enabled') else 'OFF'}",
            f"  Default Lang: {LANGUAGES.get(cfg.get('default_target_lang', 'en'), 'en')}",
            f"  Auto-Translate: {'ON' if cfg.get('auto_translate') else 'OFF'}",
        ]
        return "\n".join(lines)

_new = None
def get_new_features():
    global _new
    if _new is None:
        _new = NewFeatures()
    return _new
