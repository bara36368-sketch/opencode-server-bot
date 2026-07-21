import json, os, time, asyncio, re, html, base64, io, math, random, textwrap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_CACHE_DIR = os.path.join(BASE_DIR, "video_cache")

HAS_PIL = False
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    pass

os.makedirs(VIDEO_CACHE_DIR, exist_ok=True)

STYLES = {
    "tiktok": {"bg": (18, 18, 18), "text_color": (255, 255, 255), "accent": (255, 0, 80), "font_size": 48, "title_size": 36},
    "youtube": {"bg": (255, 255, 255), "text_color": (0, 0, 0), "accent": (255, 0, 0), "font_size": 42, "title_size": 32},
    "instagram": {"bg": (255, 255, 255), "text_color": (38, 38, 38), "accent": (225, 48, 108), "font_size": 40, "title_size": 30},
    "meme": {"bg": (255, 255, 255), "text_color": (0, 0, 0), "accent": (0, 0, 0), "font_size": 36, "title_size": 28},
    "vintage": {"bg": (250, 240, 210), "text_color": (80, 40, 20), "accent": (180, 100, 40), "font_size": 38, "title_size": 30},
    "neon": {"bg": (0, 0, 30), "text_color": (0, 255, 255), "accent": (255, 0, 255), "font_size": 44, "title_size": 34},
    "minimal": {"bg": (240, 240, 240), "text_color": (30, 30, 30), "accent": (0, 120, 200), "font_size": 42, "title_size": 32},
}

MEME_TEMPLATES = {
    "drake": {
        "name": "Drake Hotline Bling",
        "top_text": "top",
        "bottom_text": "bottom",
        "layout": "split"
    },
    "distracted": {
        "name": "Distracted Boyfriend",
        "left_text": "current thing",
        "center_text": "new thing",
        "right_text": "partner",
        "layout": "three_panel"
    },
    "captain": {
        "name": "Captain America/Iron Man",
        "text": "A",
        "text2": "Also A",
        "layout": "flip"
    },
    "doge": {
        "name": "Doge",
        "top_text": "wow",
        "bottom_text": "much text",
        "layout": "overlay"
    },
}

TRENDING_KEYWORDS = [
    "AI", "2026", "viral", "shocked", "hack", "life hack", "productivity",
    "mind blown", "game changer", "next level", "insane", "tutorial",
    "how to", "review", "vs", "best", "top 10", "stop doing", "you need",
    "million", "billion", "crazy", "genius", "secret", "hidden feature"
]

def score_virality(text):
    text_lower = text.lower()
    score = 0
    matched = []
    for kw in TRENDING_KEYWORDS:
        if kw.lower() in text_lower:
            score += 10
            matched.append(kw)
    if len(text) < 50:
        score += 5
    if len(text) > 200:
        score += 3
    if "?" in text:
        score += 5
    if "!" in text:
        score += 5
    if any(c.isdigit() for c in text):
        score += 3
    words = text.split()
    if len(words) <= 10:
        score += 5
    score = min(score, 100)
    return score, matched

def wrap_text(text, max_width=20):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 <= max_width:
            current = (current + " " + w).strip()
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines if lines else [text]

def create_frame(width, height, bg_color, title, caption_text, style_name="tiktok", gradient=True):
    if not HAS_PIL:
        return None
    style = STYLES.get(style_name, STYLES["tiktok"])
    img = Image.new("RGB", (width, height), style["bg"])
    draw = ImageDraw.Draw(img)

    if gradient:
        for y in range(height):
            ratio = y / height
            r = int(style["bg"][0] * (1 - ratio * 0.3))
            g = int(style["bg"][1] * (1 - ratio * 0.3))
            b = int(style["bg"][2] * (1 - ratio * 0.3))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    try:
        title_font = ImageFont.truetype("arial.ttf", style["title_size"])
        body_font = ImageFont.truetype("arial.ttf", style["font_size"])
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    tw = draw.textlength(title, font=title_font)
    tx = (width - tw) // 2
    draw.text((tx, 60), title, fill=style["accent"], font=title_font)

    lines = wrap_text(caption_text, max_width=25)
    total_h = len(lines) * (style["font_size"] + 8)
    start_y = (height - total_h) // 2

    if style_name == "meme":
        top_lines = lines[:len(lines)//2] if len(lines) > 2 else [lines[0]]
        bottom_lines = lines[len(lines)//2:] if len(lines) > 2 else lines[1:]
        y = 40
        for line in top_lines:
            lw = draw.textlength(line, font=body_font)
            draw.text(((width - lw) // 2, y), line, fill=style["text_color"], font=body_font)
            y += style["font_size"] + 4
        y = height - len(bottom_lines) * (style["font_size"] + 8) - 40
        for line in bottom_lines:
            lw = draw.textlength(line, font=body_font)
            draw.text(((width - lw) // 2, y), line, fill=style["text_color"], font=body_font)
            y += style["font_size"] + 4
    else:
        y = start_y
        for line in lines:
            lw = draw.textlength(line, font=body_font)
            draw.text(((width - lw) // 2, y), line, fill=style["text_color"], font=body_font)
            y += style["font_size"] + 8

    if style_name == "tiktok":
        draw.rectangle([(0, height - 80), (width, height)], fill=(255, 0, 80, 200))
        footer_text = f"  {style_name.upper()}  |  OpenCode Bot"
        fw = draw.textlength(footer_text, font=body_font)
        draw.text(((width - fw) // 2, height - 65), footer_text, fill=(255, 255, 255), font=body_font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def create_meme(template_name, text1, text2=None, width=720, height=720):
    if not HAS_PIL:
        return None
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font = ImageFont.load_default()
        small_font = font
    template = MEME_TEMPLATES.get(template_name, MEME_TEMPLATES["drake"])

    if template["layout"] == "split":
        draw.rectangle([(0, 0), (width, height // 2)], fill=(255, 255, 255))
        draw.rectangle([(0, height // 2), (width, height)], fill=(100, 180, 100))
        lines1 = wrap_text(text1, 20)
        y = height // 4 - len(lines1) * 22
        for line in lines1:
            lw = draw.textlength(line, font=font)
            draw.text(((width - lw) // 2, y), line, fill=(0, 0, 0), font=font)
            y += 44
        lines2 = wrap_text(text2 or "", 20)
        y = 3 * height // 4 - len(lines2) * 22
        for line in lines2:
            lw = draw.textlength(line, font=font)
            draw.text(((width - lw) // 2, y), line, fill=(255, 255, 255), font=font)
            y += 44
    elif template["layout"] == "overlay":
        draw.rectangle([(0, 0), (width, height)], fill=(200, 180, 100))
        lines = wrap_text(text1, 15)
        y = 30
        for line in lines:
            lw = draw.textlength(line, font=font)
            draw.text(((width - lw) // 2, y), line, fill=(0, 0, 0), font=font, stroke_width=2, stroke_fill=(255, 255, 255))
            y += 44
        if text2:
            lines2 = wrap_text(text2, 15)
            y = height - len(lines2) * 44 - 30
            for line in lines2:
                lw = draw.textlength(line, font=font)
                draw.text(((width - lw) // 2, y), line, fill=(0, 0, 0), font=font, stroke_width=2, stroke_fill=(255, 255, 255))
                y += 44
    else:
        lines = wrap_text(text1, 20)
        y = (height - len(lines) * 44) // 2
        for line in lines:
            lw = draw.textlength(line, font=font)
            draw.text(((width - lw) // 2, y), line, fill=(0, 0, 0), font=font)
            y += 44

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def add_captions(frame_buf, captions):
    if not HAS_PIL:
        return frame_buf
    img = Image.open(frame_buf)
    w, h = img.size
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    y = h - 50
    for cap in captions[:3]:
        lw = draw.textlength(cap, font=font)
        draw.rectangle([(5, y - 5), (lw + 15, y + 35)], fill=(0, 0, 0, 180))
        draw.text((10, y), cap, fill=(255, 255, 255), font=font)
        y -= 45
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_trending_overlay(frame_buf, trend_score, matched_keywords):
    if not HAS_PIL:
        return frame_buf
    img = Image.open(frame_buf)
    w, h = img.size
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    badge = f"TRENDING {trend_score}%"
    bw = draw.textlength(badge, font=font)
    draw.rectangle([(w - bw - 20, 10), (w - 10, 40)], fill=(255, 0, 80))
    draw.text((w - bw - 15, 14), badge, fill=(255, 255, 255), font=font)
    if matched_keywords:
        kw_text = " ".join(f"#{k.replace(' ', '')}" for k in matched_keywords[:3])
        draw.text((10, h - 30), kw_text, fill=(255, 255, 255, 180), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def get_available_styles():
    return list(STYLES.keys())

def get_meme_templates():
    return {k: v["name"] for k, v in MEME_TEMPLATES.items()}

async def generate_video_frames(title, caption, style="tiktok", num_frames=5):
    frames = []
    for i in range(num_frames):
        buf = create_frame(720, 720, STYLES.get(style, STYLES["tiktok"])["bg"], title, caption, style, gradient=True)
        if buf:
            frames.append(buf)
    return frames
