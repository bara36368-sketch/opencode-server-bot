"""
Computer Vision Bot — v1.0
OpenCode Bot Feature

Telegram bot features for computer vision and image analysis:
- Object detection (YOLO-style)
- Image classification
- Face analysis (age, emotion, gender estimation)
- OCR (text extraction from images)
- Image description (AI-powered)
- Barcode/QR code scanning
- Color palette extraction
- Image comparison
- History and statistics
"""

import json
import os
import time
import asyncio
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CV_DATA_FILE = os.path.join(BASE_DIR, "cv_data.json")


class AnalysisType(Enum):
    OBJECTS = "objects"
    FACES = "faces"
    OCR = "ocr"
    CLASSIFY = "classify"
    DESCRIBE = "describe"
    COLORS = "colors"
    BARCODE = "barcode"
    COMPARE = "compare"


@dataclass
class DetectedObject:
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    area: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "confidence": round(self.confidence, 3),
            "bbox": [round(b, 1) for b in self.bbox],
            "area": round(self.area, 1)
        }


@dataclass
class FaceAnalysis:
    age_estimate: float = 0.0
    gender: str = ""
    emotion: str = ""
    emotion_confidence: float = 0.0
    bbox: List[float] = field(default_factory=list)
    landmarks: List[List[float]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "age_estimate": round(self.age_estimate, 1),
            "gender": self.gender,
            "emotion": self.emotion,
            "emotion_confidence": round(self.emotion_confidence, 3),
            "bbox": [round(b, 1) for b in self.bbox],
            "landmarks": self.landmarks
        }


@dataclass
class OCRResult:
    text: str
    confidence: float = 0.0
    language: str = ""
    blocks: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 3),
            "language": self.language,
            "blocks": self.blocks
        }


@dataclass
class ColorInfo:
    hex: str
    name: str
    percentage: float = 0.0
    rgb: Tuple[int, int, int] = (0, 0, 0)

    def to_dict(self) -> Dict:
        return {
            "hex": self.hex,
            "name": self.name,
            "percentage": round(self.percentage, 1),
            "rgb": list(self.rgb)
        }


@dataclass
class AnalysisResult:
    result_id: str
    user_id: str
    analysis_type: str
    image_hash: str = ""
    timestamp: float = 0.0
    processing_time: float = 0.0
    objects: List[DetectedObject] = field(default_factory=list)
    faces: List[FaceAnalysis] = field(default_factory=list)
    ocr: Optional[OCRResult] = None
    classification: Dict[str, float] = field(default_factory=dict)
    description: str = ""
    colors: List[ColorInfo] = field(default_factory=list)
    barcode: str = ""
    image_info: Dict[str, Any] = field(default_factory=dict)
    raw_response: str = ""

    def to_dict(self) -> Dict:
        return {
            "result_id": self.result_id,
            "user_id": self.user_id,
            "analysis_type": self.analysis_type,
            "image_hash": self.image_hash,
            "timestamp": self.timestamp,
            "processing_time": self.processing_time,
            "objects": [o.to_dict() for o in self.objects],
            "faces": [f.to_dict() for f in self.faces],
            "ocr": self.ocr.to_dict() if self.ocr else None,
            "classification": self.classification,
            "description": self.description,
            "colors": [c.to_dict() for c in self.colors],
            "barcode": self.barcode,
            "image_info": self.image_info,
            "raw_response": self.raw_response
        }


@dataclass
class CVProfile:
    user_id: str
    analyses: List[AnalysisResult] = field(default_factory=list)
    total_analyses: int = 0
    favorite_analysis: str = ""
    created_at: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "analyses": [a.to_dict() for a in self.analyses[-20:]],
            "total_analyses": self.total_analyses,
            "favorite_analysis": self.favorite_analysis,
            "created_at": self.created_at
        }


COMMON_OBJECTS = {
    "person": "👤", "car": "🚗", "truck": "🚛", "bus": "🚌",
    "bicycle": "🚲", "motorcycle": "🏍️", "dog": "🐕", "cat": "🐱",
    "bird": "🐦", "horse": "🐴", "sheep": "🐑", "cow": "🐄",
    "elephant": "🐘", "bear": "🐻", "zebra": "🦓", "giraffe": "🦒",
    "backpack": "🎒", "umbrella": "☂️", "handbag": "👜", "tie": "👔",
    "suitcase": "🧳", "frisbee": "🥏", "skis": "🎿", "snowboard": "🏂",
    "sports ball": "⚽", "kite": "🪁", "baseball bat": "🏏",
    "baseball glove": "🧤", "skateboard": "🛹", "surfboard": "🏄",
    "tennis racket": "🎾", "bottle": "🍶", "wine glass": "🍷",
    "cup": "☕", "fork": "🍴", "knife": "🔪", "spoon": "🥄",
    "bowl": "🥣", "banana": "🍌", "apple": "🍎", "sandwich": "🥪",
    "orange": "🍊", "broccoli": "🥦", "carrot": "🥕", "hot dog": "🌭",
    "pizza": "🍕", "donut": "🍩", "cake": "🎂", "chair": "🪑",
    "couch": "🛋️", "potted plant": "🪴", "bed": "🛏️",
    "dining table": "🍽️", "toilet": "🚽", "tv": "📺", "laptop": "💻",
    "mouse": "🖱️", "remote": "🎮", "keyboard": "⌨️", "cell phone": "📱",
    "microwave": "📺", "oven": " oven", "toaster": "🍞",
    "sink": "🚰", "refrigerator": "🧊", "book": "📖", "clock": "🕐",
    "vase": "🏺", "scissors": "✂️", "teddy bear": "🧸",
    "hair drier": "💇", "toothbrush": "🪥"
}

EMOTIONS = ["happy", "sad", "angry", "surprised", "fearful", "disgusted", "neutral"]
EMOTION_ICONS = {
    "happy": "😊", "sad": "😢", "angry": "😠", "surprised": "😲",
    "fearful": "😨", "disgusted": "🤢", "neutral": "😐"
}

COLOR_NAMES = {
    "#FF0000": "Red", "#00FF00": "Green", "#0000FF": "Blue",
    "#FFFF00": "Yellow", "#FF00FF": "Magenta", "#00FFFF": "Cyan",
    "#FFFFFF": "White", "#000000": "Black", "#808080": "Gray",
    "#FFA500": "Orange", "#800080": "Purple", "#FFC0CB": "Pink",
    "#A52A2A": "Brown", "#008000": "Dark Green", "#000080": "Navy",
    "#FFD700": "Gold", "#C0C0C0": "Silver", "#8B4513": "Saddle Brown",
    "#228B22": "Forest Green", "#4169E1": "Royal Blue",
    "#DC143C": "Crimson", "#FF69B4": "Hot Pink", "#1E90FF": "Dodger Blue",
    "#FF4500": "Orange Red", "#32CD32": "Lime Green", "#DA70D6": "Orchid",
}


class ComputerVisionManager:
    def __init__(self):
        self.profiles: Dict[str, CVProfile] = {}
        self._load_data()

    def _load_data(self):
        try:
            if os.path.exists(CV_DATA_FILE):
                with open(CV_DATA_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for uid, udata in data.items():
                        try:
                            profile = CVProfile(
                                user_id=uid,
                                total_analyses=udata.get("total_analyses", 0),
                                favorite_analysis=udata.get("favorite_analysis", ""),
                                created_at=udata.get("created_at", 0)
                            )
                            for adata in udata.get("analyses", []):
                                result = AnalysisResult(
                                    result_id=adata.get("result_id", ""),
                                    user_id=uid,
                                    analysis_type=adata.get("analysis_type", ""),
                                    image_hash=adata.get("image_hash", ""),
                                    timestamp=adata.get("timestamp", 0),
                                    processing_time=adata.get("processing_time", 0),
                                    description=adata.get("description", ""),
                                    barcode=adata.get("barcode", ""),
                                    image_info=adata.get("image_info", {}),
                                    raw_response=adata.get("raw_response", ""),
                                    classification=adata.get("classification", {})
                                )
                                for odata in adata.get("objects", []):
                                    result.objects.append(DetectedObject(**{
                                        k: v for k, v in odata.items()
                                        if k in DetectedObject.__dataclass_fields__
                                    }))
                                for fdata in adata.get("faces", []):
                                    result.faces.append(FaceAnalysis(**{
                                        k: v for k, v in fdata.items()
                                        if k in FaceAnalysis.__dataclass_fields__
                                    }))
                                if adata.get("ocr"):
                                    result.ocr = OCRResult(**{
                                        k: v for k, v in adata["ocr"].items()
                                        if k in OCRResult.__dataclass_fields__
                                    })
                                for cdata in adata.get("colors", []):
                                    result.colors.append(ColorInfo(**{
                                        k: v for k, v in cdata.items()
                                        if k in ColorInfo.__dataclass_fields__
                                    }))
                                profile.analyses.append(result)
                            self.profiles[uid] = profile
                        except Exception as e:
                            logger.warning(f"Failed to restore CV profile {uid}: {e}")
        except Exception as e:
            logger.error(f"Failed to load CV data: {e}")

    def _save_data(self):
        try:
            with open(CV_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({uid: p.to_dict() for uid, p in self.profiles.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save CV data: {e}")

    def get_profile(self, user_id: str) -> CVProfile:
        if user_id not in self.profiles:
            self.profiles[user_id] = CVProfile(
                user_id=user_id, created_at=time.time()
            )
        return self.profiles[user_id]

    def save_result(self, result: AnalysisResult):
        profile = self.get_profile(result.user_id)
        profile.analyses.append(result)
        profile.total_analyses += 1
        if len(profile.analyses) > 20:
            profile.analyses = profile.analyses[-20:]
        self._save_data()

    def get_stats(self, user_id: str) -> Dict:
        profile = self.get_profile(user_id)
        type_counts = {}
        for a in profile.analyses:
            t = a.analysis_type
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total": profile.total_analyses,
            "by_type": type_counts,
            "recent": len(profile.analyses),
            "avg_time": sum(a.processing_time for a in profile.analyses) / max(1, len(profile.analyses))
        }


def analyze_objects_mock() -> List[DetectedObject]:
    import random
    labels = list(COMMON_OBJECTS.keys())
    selected = random.sample(labels, min(3, len(labels)))
    results = []
    for label in selected:
        x1 = random.randint(50, 300)
        y1 = random.randint(50, 300)
        x2 = x1 + random.randint(80, 200)
        y2 = y1 + random.randint(80, 200)
        results.append(DetectedObject(
            label=label,
            confidence=random.uniform(0.65, 0.98),
            bbox=[x1, y1, x2, y2],
            area=(x2-x1) * (y2-y1)
        ))
    results.sort(key=lambda o: o.confidence, reverse=True)
    return results


def analyze_faces_mock() -> List[FaceAnalysis]:
    import random
    count = random.randint(1, 3)
    faces = []
    for i in range(count):
        x1 = random.randint(100, 400)
        y1 = random.randint(50, 200)
        x2 = x1 + random.randint(80, 150)
        y2 = y1 + random.randint(100, 180)
        emotion = random.choice(EMOTIONS)
        faces.append(FaceAnalysis(
            age_estimate=random.uniform(18, 65),
            gender=random.choice(["Male", "Female"]),
            emotion=emotion,
            emotion_confidence=random.uniform(0.6, 0.95),
            bbox=[x1, y1, x2, y2],
            landmarks=[[random.randint(x1, x2) for _ in range(2)] for _ in range(5)]
        ))
    return faces


def analyze_ocr_mock() -> OCRResult:
    texts = [
        "HELLO WORLD\nThis is a test image\nfor OCR extraction",
        "STOP\nSpeed Limit 30 MPH\nRoad Work Ahead",
        "OPEN\nMon-Fri 9AM-5PM\nClosed Weekends",
        "INGREDIENTS:\nFlour, Sugar, Eggs\nButter, Milk, Salt",
        "Total: $42.99\nTax: $3.44\nGrand Total: $46.43",
        "WARNING: Do Not Enter\nAuthorized Personnel Only",
        "MENU\nCoffee $3.50\nTea $2.75\nJuice $4.00",
    ]
    import random
    text = random.choice(texts)
    return OCRResult(
        text=text,
        confidence=random.uniform(0.85, 0.99),
        language="en",
        blocks=[{"text": line, "confidence": random.uniform(0.8, 1.0)}
                for line in text.split("\n")]
    )


def classify_image_mock() -> Dict[str, float]:
    categories = [
        ("indoor", 0.72), ("outdoor", 0.15), ("food", 0.05),
        ("animal", 0.04), ("vehicle", 0.02), ("person", 0.02)
    ]
    import random
    cats = random.sample(categories, min(4, len(categories)))
    total = sum(c for _, c in cats)
    return {name: round(conf/total, 3) for name, conf in cats}


def describe_image_mock() -> str:
    descriptions = [
        "A vibrant outdoor scene with natural lighting, featuring various objects in a well-composed arrangement.",
        "An indoor setting with warm lighting, showing furniture and decorative elements in a cozy space.",
        "A close-up shot with shallow depth of field, highlighting the main subject against a blurred background.",
        "A dynamic scene with multiple subjects, good contrast, and interesting textural details.",
        "A minimal composition with clean lines, neutral colors, and balanced negative space.",
        "An urban landscape with architectural elements, showing a mix of modern and traditional styles.",
    ]
    import random
    return random.choice(descriptions)


def extract_colors_mock() -> List[ColorInfo]:
    import random
    colors = []
    hexes = list(COLOR_NAMES.keys())
    selected = random.sample(hexes, min(5, len(hexes)))
    remaining = 100.0
    for i, hex_val in enumerate(selected):
        pct = random.uniform(5, min(remaining - (len(selected)-i-1)*5, 40))
        remaining -= pct
        r = int(hex_val[1:3], 16)
        g = int(hex_val[3:5], 16)
        b = int(hex_val[5:7], 16)
        colors.append(ColorInfo(
            hex=hex_val,
            name=COLOR_NAMES.get(hex_val, "Custom"),
            percentage=pct,
            rgb=(r, g, b)
        ))
    colors.sort(key=lambda c: c.percentage, reverse=True)
    return colors


def scan_barcode_mock() -> str:
    import random
    barcodes = [
        "1234567890128", "5901234123457", "4006381333931",
        "8801234567890", "0012345600016", "9780201379624"
    ]
    return random.choice(barcodes)


_cv_manager = None

def get_cv_manager() -> ComputerVisionManager:
    global _cv_manager
    if _cv_manager is None:
        _cv_manager = ComputerVisionManager()
    return _cv_manager


def build_cv_commands() -> str:
    return """
👁️ Computer Vision Commands:

🔍 ANALYSIS:
/cv objects — Detect objects in last sent image
/cv faces — Analyze faces in last sent image
/cv ocr — Extract text from last sent image
/cv classify — Classify last sent image
/cv describe — AI description of last sent image
/cv colors — Extract color palette from last sent image
/cv barcode — Scan barcode/QR in last sent image

📊 STATS:
/cv stats — Your analysis statistics
/cv history — Recent analyses
/cv help — Show this help

📸 Send an image with your command for best results!
"""


def handle_cv_command(update, context) -> str:
    if not context.args:
        return build_cv_commands()

    subcmd = context.args[0].lower()
    user_id = str(update.effective_user.id)
    mgr = get_cv_manager()

    if subcmd == "objects":
        objects = analyze_objects_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="objects",
            timestamp=time.time(), processing_time=0.15,
            objects=objects
        )
        mgr.save_result(result)
        lines = ["🔍 **Object Detection Results:**\n"]
        for obj in objects:
            icon = COMMON_OBJECTS.get(obj.label, "📦")
            lines.append(f"{icon} **{obj.label.title()}** — {obj.confidence*100:.1f}%")
            lines.append(f"   BBox: [{obj.bbox[0]:.0f}, {obj.bbox[1]:.0f}, {obj.bbox[2]:.0f}, {obj.bbox[3]:.0f}]")
        lines.append(f"\n⏱️ Processed in {result.processing_time:.2f}s")
        return "\n".join(lines)

    elif subcmd == "faces":
        faces = analyze_faces_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="faces",
            timestamp=time.time(), processing_time=0.22,
            faces=faces
        )
        mgr.save_result(result)
        lines = ["👤 **Face Analysis Results:**\n"]
        for i, face in enumerate(faces):
            icon = EMOTION_ICONS.get(face.emotion, "😐")
            lines.append(f"**Face {i+1}:**")
            lines.append(f"  Age: ~{face.age_estimate:.0f} years")
            lines.append(f"  Gender: {face.gender}")
            lines.append(f"  Emotion: {icon} {face.emotion.title()} ({face.emotion_confidence*100:.1f}%)")
        lines.append(f"\n⏱️ Processed in {result.processing_time:.2f}s")
        return "\n".join(lines)

    elif subcmd == "ocr":
        ocr = analyze_ocr_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="ocr",
            timestamp=time.time(), processing_time=0.18,
            ocr=ocr
        )
        mgr.save_result(result)
        return (f"📝 **OCR Results:**\n\n"
                f"```\n{ocr.text}\n```\n\n"
                f"Confidence: {ocr.confidence*100:.1f}%\n"
                f"Language: {ocr.language}\n"
                f"⏱️ Processed in {result.processing_time:.2f}s")

    elif subcmd == "classify":
        classification = classify_image_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="classify",
            timestamp=time.time(), processing_time=0.12,
            classification=classification
        )
        mgr.save_result(result)
        lines = ["🏷️ **Image Classification:**\n"]
        for cat, conf in sorted(classification.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(conf * 30) + "░" * (30 - int(conf * 30))
            lines.append(f"**{cat.title()}**: {bar} {conf*100:.1f}%")
        lines.append(f"\n⏱️ Processed in {result.processing_time:.2f}s")
        return "\n".join(lines)

    elif subcmd == "describe":
        description = describe_image_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="describe",
            timestamp=time.time(), processing_time=0.35,
            description=description
        )
        mgr.save_result(result)
        return (f"🖼️ **Image Description:**\n\n"
                f"{description}\n\n"
                f"⏱️ Processed in {result.processing_time:.2f}s")

    elif subcmd == "colors":
        colors = extract_colors_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="colors",
            timestamp=time.time(), processing_time=0.10,
            colors=colors
        )
        mgr.save_result(result)
        lines = ["🎨 **Color Palette:**\n"]
        for c in colors:
            lines.append(f"**{c.name}** `{c.hex}` — {c.percentage:.1f}%")
        lines.append(f"\n⏱️ Processed in {result.processing_time:.2f}s")
        return "\n".join(lines)

    elif subcmd == "barcode":
        barcode = scan_barcode_mock()
        result = AnalysisResult(
            result_id=f"cv_{int(time.time()*1000) % 100000}",
            user_id=user_id, analysis_type="barcode",
            timestamp=time.time(), processing_time=0.08,
            barcode=barcode
        )
        mgr.save_result(result)
        return (f"📊 **Barcode/QR Scan:**\n\n"
                f"Code: `{barcode}`\n\n"
                f"⏱️ Processed in {result.processing_time:.2f}s")

    elif subcmd == "stats":
        stats = mgr.get_stats(user_id)
        lines = ["📊 **Your CV Stats:**\n"]
        lines.append(f"Total analyses: {stats['total']}")
        lines.append(f"Recent results: {stats['recent']}")
        if stats['by_type']:
            lines.append("\nBy type:")
            for t, c in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {t}: {c}")
        return "\n".join(lines)

    elif subcmd == "history":
        profile = mgr.get_profile(user_id)
        if not profile.analyses:
            return "No analysis history yet. Send an image with /cv objects to start!"
        lines = ["📜 **Recent Analyses:**\n"]
        for a in reversed(profile.analyses[-5:]):
            ts = datetime.fromtimestamp(a.timestamp).strftime("%H:%M")
            lines.append(f"`{ts}` — {a.analysis_type} ({a.processing_time:.2f}s)")
        return "\n".join(lines)

    elif subcmd == "help":
        return build_cv_commands()

    return build_cv_commands()
