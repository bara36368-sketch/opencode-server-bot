"""
Cyberdeck Agent v1.0
Specialized agent for building, upgrading, and managing cyberdeck builds.
Features: component selection, compatibility checking, BOM generation,
tutorial generation, image analysis, video learning, code generation,
idea creation, flaw detection, and continuous learning.
"""

import os
import json
import asyncio
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ============================================================
# CONSTANTS
# ============================================================
CYBERDECK_BUILD_LIST = "CYBERDECK_BUILD_LIST.md"
CYBERDECK_LEARNINGS_FILE = "cyberdeck_learnings.json"
CYBERDECK_BUILD_HISTORY = "cyberdeck_build_history.json"

# ============================================================
# KNOWLEDGE BASE — MOST POWERFUL COMPONENTS PER CATEGORY
# ============================================================
SBC_DATABASE = {
    "pi5_16gb": {
        "name": "Raspberry Pi 5 16GB",
        "cpu": "Quad-core ARM Cortex-A76 @ 2.4GHz",
        "ram": "16GB LPDDR4X",
        "storage": "microSD + PCIe 2.0 x1 (NVMe via HAT)",
        "video": "Dual micro HDMI (4Kp60)",
        "gpio": "40-pin header",
        "power": "USB-C (5V/5A recommended)",
        "tdp": "12W",
        "price": 90,
        "tier": "advanced",
        "categories": ["coding", "security", "research", "ai", "survival", "media"],
        "pros": ["Best ARM performance", "NVMe support", "PCIe lane", "16GB RAM"],
        "cons": ["Higher power draw", "Needs active cooling"],
        "compatibility": {"displays": ["hdmi", "dsi", "eink"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc_pd", "ups_hat"]},
    },
    "pi5_8gb": {
        "name": "Raspberry Pi 5 8GB",
        "cpu": "Quad-core ARM Cortex-A76 @ 2.4GHz",
        "ram": "8GB LPDDR4X",
        "storage": "microSD + PCIe 2.0 x1 (NVMe via HAT)",
        "video": "Dual micro HDMI (4Kp60)",
        "gpio": "40-pin header",
        "power": "USB-C (5V/5A recommended)",
        "tdp": "12W",
        "price": 75,
        "tier": "intermediate",
        "categories": ["coding", "security", "research", "survival", "media", "gaming"],
        "pros": ["Excellent performance", "NVMe support", "Great community"],
        "cons": ["Needs active cooling in enclosed builds"],
        "compatibility": {"displays": ["hdmi", "dsi", "eink"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc_pd", "ups_hat"]},
    },
    "pi5_4gb": {
        "name": "Raspberry Pi 5 4GB",
        "cpu": "Quad-core ARM Cortex-A76 @ 2.4GHz",
        "ram": "4GB LPDDR4X",
        "storage": "microSD + PCIe 2.0 x1 (NVMe via HAT)",
        "video": "Dual micro HDMI (4Kp60)",
        "gpio": "40-pin header",
        "power": "USB-C (5V/5A recommended)",
        "tdp": "12W",
        "price": 60,
        "tier": "intermediate",
        "categories": ["coding", "gaming", "media", "security"],
        "pros": ["Good performance", "NVMe support", "Affordable"],
        "cons": ["4GB may limit heavy workloads"],
        "compatibility": {"displays": ["hdmi", "dsi", "eink"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc_pd", "ups_hat"]},
    },
    "pi4_8gb": {
        "name": "Raspberry Pi 4 Model B 8GB",
        "cpu": "Quad-core ARM Cortex-A72 @ 1.8GHz",
        "ram": "8GB LPDDR4",
        "storage": "microSD + USB 3.0",
        "video": "2x micro HDMI (4Kp60)",
        "gpio": "40-pin header",
        "power": "USB-C (5V/3A)",
        "tdp": "7W",
        "price": 75,
        "tier": "intermediate",
        "categories": ["coding", "security", "gaming", "media", "research"],
        "pros": ["Mature ecosystem", "Lower power", "Runs cooler", "8GB RAM"],
        "cons": ["Older CPU", "No PCIe NVMe"],
        "compatibility": {"displays": ["hdmi", "dsi", "eink"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc", "ups_hat"]},
    },
    "pi4_4gb": {
        "name": "Raspberry Pi 4 Model B 4GB",
        "cpu": "Quad-core ARM Cortex-A72 @ 1.8GHz",
        "ram": "4GB LPDDR4",
        "storage": "microSD + USB 3.0",
        "video": "2x micro HDMI (4Kp60)",
        "gpio": "40-pin header",
        "power": "USB-C (5V/3A)",
        "tdp": "7W",
        "price": 55,
        "tier": "beginner",
        "categories": ["gaming", "media", "writerdeck", "coding"],
        "pros": ["Mature ecosystem", "Low power", "Affordable", "Community standard"],
        "cons": ["Older CPU", "No NVMe"],
        "compatibility": {"displays": ["hdmi", "dsi", "eink"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc", "ups_hat"]},
    },
    "zero2w": {
        "name": "Raspberry Pi Zero 2 W",
        "cpu": "Quad-core ARM Cortex-A53 @ 1GHz",
        "ram": "512MB LPDDR2",
        "storage": "microSD",
        "video": "mini HDMI (1080p)",
        "gpio": "40-pin header (unpopulated)",
        "power": "micro USB (5V/2.5A)",
        "tdp": "2W",
        "price": 15,
        "tier": "beginner",
        "categories": ["writerdeck", "conversation"],
        "pros": ["Tiny", "Ultra-low power", "Wi-Fi built-in"],
        "cons": ["Limited performance", "512MB RAM"],
        "compatibility": {"displays": ["hdmi_mini", "eink"], "keyboards": ["usb_otg", "bluetooth"], "power": ["micro_usb", "lipo"]},
    },
    "cm5": {
        "name": "Raspberry Pi Compute Module 5",
        "cpu": "Quad-core ARM Cortex-A76 @ 2.4GHz",
        "ram": "4–16GB LPDDR4X",
        "storage": "eMMC + microSD (carrier dependent)",
        "video": "Via carrier board",
        "gpio": "Board-to-board connector",
        "power": "Via carrier board",
        "tdp": "12W",
        "price": 90,
        "tier": "advanced",
        "categories": ["coding", "security", "research", "ai"],
        "pros": ["Compact", "Flexible carrier design", "Pi 5 performance"],
        "cons": ["Requires custom carrier board"],
        "compatibility": {"displays": ["via_carrier"], "keyboards": ["via_carrier"], "power": ["via_carrier"]},
    },
    "orange_pi_5": {
        "name": "Orange Pi 5",
        "cpu": "Octa-core RK3588S (4x A76 + 4x A55) @ 2.4GHz",
        "ram": "4–32GB LPDDR5",
        "storage": "eMMC + NVMe + microSD",
        "video": "HDMI 2.1 (8K) + USB-C DP",
        "gpio": "40-pin header",
        "power": "USB-C (5V/4A)",
        "tdp": "15W",
        "price": 100,
        "tier": "advanced",
        "categories": ["coding", "gaming", "ai", "media"],
        "pros": ["Much faster than Pi", "NVMe built-in", "32GB RAM possible"],
        "cons": ["Smaller community", "Higher power"],
        "compatibility": {"displays": ["hdmi", "usbc_dp"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["usbc_pd"]},
    },
    "jetson_orin_nano": {
        "name": "NVIDIA Jetson Orin Nano",
        "cpu": "6-core ARM Cortex-A78AE",
        "gpu": "1024-core NVIDIA Ampere",
        "ram": "4/8GB LPDDR5",
        "storage": "NVMe + microSD",
        "video": "HDMI 2.1 + MIPI CSI/DSI",
        "gpio": "40-pin header",
        "power": "DC barrel jack (5–20V)",
        "tdp": "15W",
        "price": 200,
        "tier": "advanced",
        "categories": ["ai"],
        "pros": ["GPU acceleration", "CUDA support", "Best AI performance"],
        "cons": ["Expensive", "High power", "Niche"],
        "compatibility": {"displays": ["hdmi", "mipi_dsi"], "keyboards": ["usb", "bluetooth", "gpio"], "power": ["dc_barrel"]},
    },
    "lattepanda_mu": {
        "name": "LattePanda Mu (x86)",
        "cpu": "AMD Ryzen 7 7840HS (8-core/16-thread)",
        "ram": "Up to 64GB DDR5",
        "storage": "NVMe PCIe 4.0",
        "video": "USB4 + HDMI + DP",
        "gpio": "None (standard PC)",
        "power": "USB-C PD (65–100W)",
        "tdp": "54W",
        "price": 400,
        "tier": "advanced",
        "categories": ["coding", "security", "ai"],
        "pros": ["Full desktop performance", "Windows 11", "x86 apps"],
        "cons": ["Expensive", "High power", "Needs active cooling"],
        "compatibility": {"displays": ["hdmi", "dp", "usb4"], "keyboards": ["usb", "bluetooth"], "power": ["usbc_pd"]},
    },
}

DISPLAY_DATABASE = {
    "7ips_hdmi_touch": {
        "name": "7\" IPS HDMI Touchscreen",
        "size": 7,
        "resolution": "1024x600",
        "interface": "hdmi",
        "touch": True,
        "price": 70,
        "brands": ["iPistBit", "JUN-ELECTRON", "HAMTYSAN"],
        "pros": ["Universal compatibility", "Touch input", "Built-in speakers"],
        "cons": ["Needs separate USB power"],
    },
    "7ips_hdmi_1280": {
        "name": "7\" IPS HDMI 1280x800",
        "size": 7,
        "resolution": "1280x800",
        "interface": "hdmi",
        "touch": True,
        "price": 90,
        "brands": ["Waveshare", "Elecrow"],
        "pros": ["Higher resolution", "Sharp text"],
        "cons": ["Slightly more expensive"],
    },
    "5ips_hdmi": {
        "name": "5\" HDMI IPS LCD",
        "size": 5,
        "resolution": "800x480",
        "interface": "hdmi",
        "touch": True,
        "price": 45,
        "brands": ["Waveshare", "Generic"],
        "pros": ["Compact", "Affordable"],
        "cons": ["Small for desktop use"],
    },
    "10ips_hdmi": {
        "name": "10.1\" IPS HDMI LCD",
        "size": 10.1,
        "resolution": "1280x800",
        "interface": "hdmi",
        "touch": False,
        "price": 110,
        "brands": ["Waveshare", "Elecrow"],
        "pros": ["Large screen real estate"],
        "cons": ["No touch", "Bigger build"],
    },
    "eink_7": {
        "name": "7\" E-Ink Display",
        "size": 7,
        "resolution": "800x480",
        "interface": "spi",
        "touch": False,
        "price": 80,
        "brands": ["Waveshare", "GoodDisplay"],
        "pros": ["Near-zero power", "Sunlight readable"],
        "cons": ["Slow refresh", "No video"],
    },
    "eink_4": {
        "name": "4.2\" E-Ink Display",
        "size": 4.2,
        "resolution": "400x300",
        "interface": "spi",
        "touch": False,
        "price": 40,
        "brands": ["Waveshare", "GoodDisplay"],
        "pros": ["Ultra-compact", "Minimal power"],
        "cons": ["Very small", "Slow refresh"],
    },
    "oled_13": {
        "name": "1.3\" OLED Status Display",
        "size": 1.3,
        "resolution": "128x64",
        "interface": "i2c",
        "touch": False,
        "price": 10,
        "brands": ["Adafruit", "Generic"],
        "pros": ["Tiny", "System stats", "Low power"],
        "cons": ["Not for main display"],
    },
    "79_ultrawide": {
        "name": "7.9\" Ultrawide Touchscreen",
        "size": 7.9,
        "resolution": "1280x400",
        "interface": "hdmi",
        "touch": True,
        "price": 120,
        "brands": ["Waveshare"],
        "pros": ["Unique form factor", "Wide view"],
        "cons": ["Unusual aspect ratio"],
    },
}

KEYBOARD_DATABASE = {
    "60_mechanical": {
        "name": "60% Mechanical Keyboard",
        "layout": "60%",
        "switches": "Mechanical (Cherry MX compatible)",
        "connectivity": "usb",
        "price_range": [30, 130],
        "best_for": ["coding", "security", "research", "gaming"],
        "models": ["HyperX Alloy Origins 60", "Keychron K12", "MageGee"],
        "pros": ["Full alpha layout", "Compact", "Great typing feel"],
        "cons": ["No function row", "No numpad"],
    },
    "40_ortholinear": {
        "name": "40% Ortholinear Keyboard",
        "layout": "40%",
        "switches": "Mechanical",
        "connectivity": "usb",
        "price_range": [80, 130],
        "best_for": ["writerdeck", "coding", "conversation"],
        "models": ["Drop/OLKB Planck v7", "Preonic"],
        "pros": ["Ultra-compact", "Grid layout packs well", "Layer combinations"],
        "cons": ["Learning curve", "No number row"],
    },
    "split_corne": {
        "name": "Corne Split Ergonomic",
        "layout": "Split 42-key",
        "switches": "Mechanical",
        "connectivity": "usb/trrs",
        "price_range": [100, 200],
        "best_for": ["coding", "writerdeck"],
        "models": ["Corne Classic", "Corne choc"],
        "pros": ["Ergonomic", "Reduces strain"],
        "cons": ["Two pieces", "Assembly required"],
    },
    "thumb_bbq20kbd": {
        "name": "Blackberry-style Thumb Keyboard",
        "layout": "Thumb",
        "switches": "Membrane",
        "connectivity": "i2c",
        "price_range": [20, 40],
        "best_for": ["writerdeck", "conversation", "field"],
        "models": ["BBQ20KBD"],
        "pros": ["Ultra-compact", "Thumb-typing"],
        "cons": ["Small keys", "Not for long typing"],
    },
    "bluetooth_k380": {
        "name": "Logitech K380 Bluetooth",
        "layout": "Compact",
        "switches": "Membrane",
        "connectivity": "bluetooth",
        "price_range": [25, 40],
        "best_for": ["media", "conversation", "field"],
        "models": ["Logitech K380"],
        "pros": ["Multi-device", "Compact", "Wireless"],
        "cons": ["Membrane feel", "No backlight"],
    },
}

POWER_DATABASE = {
    "ups_hat_waveshare": {
        "name": "Waveshare UPS HAT (B)",
        "capacity": "2x 18650 cells",
        "voltage": "7.4V nominal",
        "features": ["I2C battery status", "Charging circuit"],
        "price": 25,
        "runtime_estimate": "1.5–2.5 hours (Pi 5 + 7\" display)",
        "best_for": ["intermediate", "advanced"],
        "safety": "Known brand, recommended",
    },
    "pisugar_3": {
        "name": "PiSugar 3",
        "capacity": "500mAh LiPo",
        "voltage": "5V",
        "features": ["Slim integrated", "UPS function", "RTC"],
        "price": 35,
        "runtime_estimate": "30–60 minutes",
        "best_for": ["beginner", "small builds"],
        "safety": "Known brand, recommended",
    },
    "usb_bank_20000": {
        "name": "USB Power Bank 20,000mAh",
        "capacity": "20,000mAh",
        "voltage": "5V USB-C PD",
        "features": ["Passthrough charging", "No integration needed"],
        "price": 30,
        "runtime_estimate": "4–6 hours",
        "best_for": ["beginner"],
        "safety": "Safest option for beginners",
    },
    "custom_18650_4cell": {
        "name": "Custom 4x 18650 Pack",
        "capacity": "12,000mAh",
        "voltage": "7.4V via BMS + boost",
        "features": ["High capacity", "Full control"],
        "price": 40,
        "runtime_estimate": "4–6 hours",
        "best_for": ["advanced"],
        "safety": "Requires BMS knowledge, use quality cells",
    },
}

ENCLOSURE_DATABASE = {
    "pelican_1150": {
        "name": "Pelican 1150",
        "type": "hard_case",
        "size": "Small (Pi + 5–7\" display)",
        "features": ["Watertight", "Impact resistant"],
        "price": 40,
        "best_for": ["beginner", "intermediate"],
        "aesthetic": "Military-industrial",
    },
    "pelican_1450": {
        "name": "Pelican 1450",
        "type": "hard_case",
        "size": "Full (10\" display + keyboard)",
        "features": ["Watertight", "Impact resistant"],
        "price": 70,
        "best_for": ["intermediate", "advanced"],
        "aesthetic": "Military-industrial",
    },
    "3d_printed_custom": {
        "name": "3D Printed Custom Case",
        "type": "3d_printed",
        "size": "Custom (designed for components)",
        "features": ["Unlimited design freedom", "Iterative", "Affordable"],
        "price": 10,
        "best_for": ["intermediate", "advanced"],
        "aesthetic": "Any — cyberpunk, minimalist, industrial",
        "filament": "PETG recommended (impact + heat resistant)",
    },
    "apache_1800": {
        "name": "Apache 1800 (Harbor Freight)",
        "type": "hard_case",
        "size": "Medium",
        "features": ["Budget Pelican alternative"],
        "price": 20,
        "best_for": ["beginner", "intermediate"],
        "aesthetic": "Military-industrial",
    },
    "found_object": {
        "name": "Found/Repurposed Enclosure",
        "type": "repurposed",
        "size": "Varies",
        "features": ["Unique character", "Thrift store find"],
        "price": 5,
        "best_for": ["beginner", "conversation"],
        "examples": ["Briefcase", "Toolbox", "Military ammo box", "Vintage electronics"],
    },
}

OS_DATABASE = {
    "pi_os": {"name": "Raspberry Pi OS", "base": "Debian", "best_for": ["general", "coding", "research"], "difficulty": "beginner"},
    "kali": {"name": "Kali Linux", "base": "Debian", "best_for": ["security", "pentesting"], "difficulty": "intermediate"},
    "dietpi": {"name": "DietPi", "base": "Debian", "best_for": ["low-resource", "writerdeck", "battery"], "difficulty": "intermediate"},
    "ubuntu_mate": {"name": "Ubuntu MATE", "base": "Ubuntu", "best_for": ["desktop", "coding"], "difficulty": "beginner"},
    "retropie": {"name": "RetroPie", "base": "Debian", "best_for": ["gaming", "retro"], "difficulty": "beginner"},
    "batocera": {"name": "Batocera", "base": "Linux", "best_for": ["gaming", "retro"], "difficulty": "beginner"},
    "writerdeck_os": {"name": "writerdeckOS", "base": "Debian", "best_for": ["writerdeck"], "difficulty": "beginner"},
    "twister_os": {"name": "Twister OS", "base": "Raspberry Pi OS", "best_for": ["conversation", "retro"], "difficulty": "beginner"},
    "libreelec": {"name": "LibreELEC", "base": "Linux", "best_for": ["media"], "difficulty": "beginner"},
}

CATEGORY_DEFAULTS = {
    "coding": {
        "name": "Coding & Development",
        "description": "Portable coding, terminal work, remote server admin",
        "sbcs": ["pi5_16gb", "pi5_8gb", "lattepanda_mu"],
        "displays": ["7ips_hdmi_1280", "10ips_hdmi"],
        "keyboards": ["60_mechanical", "40_ortholinear"],
        "power": ["ups_hat_waveshare", "custom_18650_4cell"],
        "enclosures": ["3d_printed_custom", "pelican_1450"],
        "os": ["pi_os", "kali", "ubuntu_mate"],
        "accessories": ["nvme_ssd", "usb_hub", "ethernet_switch"],
        "budget_range": [300, 1200],
    },
    "writerdeck": {
        "name": "Writerdeck",
        "description": "Distraction-free writing, journaling",
        "sbcs": ["zero2w", "pi4_4gb"],
        "displays": ["eink_7", "eink_4"],
        "keyboards": ["40_ortholinear", "thumb_bbq20kbd"],
        "power": ["pisugar_3", "usb_bank_20000"],
        "enclosures": ["3d_printed_custom", "found_object"],
        "os": ["writerdeck_os", "dietpi"],
        "accessories": [],
        "budget_range": [100, 400],
    },
    "security": {
        "name": "Security & Pentesting",
        "description": "Network analysis, red team, RF exploration",
        "sbcs": ["pi5_8gb", "pi5_16gb"],
        "displays": ["7ips_hdmi_touch"],
        "keyboards": ["60_mechanical"],
        "power": ["ups_hat_waveshare", "custom_18650_4cell"],
        "enclosures": ["3d_printed_custom", "pelican_1150"],
        "os": ["kali"],
        "accessories": ["wifi_antenna", "sdr", "ethernet_switch", "gpio_switches"],
        "budget_range": [400, 1500],
    },
    "gaming": {
        "name": "Retro Gaming & Media",
        "description": "Emulation, retro gaming, media playback",
        "sbcs": ["pi5_8gb", "pi4_4gb", "orange_pi_5"],
        "displays": ["7ips_hdmi_touch", "10ips_hdmi"],
        "keyboards": ["60_mechanical"],
        "power": ["ups_hat_waveshare", "usb_bank_20000"],
        "enclosures": ["3d_printed_custom", "pelican_1150"],
        "os": ["retropie", "batocera"],
        "accessories": ["game_controllers", "hdmi_output", "speakers"],
        "budget_range": [150, 500],
    },
    "research": {
        "name": "Field Research & Note-Taking",
        "description": "Fieldwork, data collection, travel computing",
        "sbcs": ["pi5_8gb", "pi5_16gb"],
        "displays": ["7ips_hdmi_1280", "10ips_hdmi"],
        "keyboards": ["60_mechanical"],
        "power": ["custom_18650_4cell", "ups_hat_waveshare"],
        "enclosures": ["3d_printed_custom", "pelican_1150"],
        "os": ["pi_os", "dietpi"],
        "accessories": ["nvme_ssd", "offline_wikipedia", "sunlight_readable"],
        "budget_range": [300, 800],
    },
    "ai": {
        "name": "AI & Machine Learning",
        "description": "Local AI inference, LLM hosting, computer vision",
        "sbcs": ["jetson_orin_nano", "pi5_16gb", "lattepanda_mu"],
        "displays": ["7ips_hdmi_1280", "10ips_hdmi"],
        "keyboards": ["60_mechanical"],
        "power": ["custom_18650_4cell"],
        "enclosures": ["3d_printed_custom"],
        "os": ["pi_os", "ubuntu_mate"],
        "accessories": ["nvme_ssd", "active_cooling", "gpu_compute"],
        "budget_range": [500, 2000],
    },
    "survival": {
        "name": "Survival & Off-Grid",
        "description": "Emergency computing, off-grid communication",
        "sbcs": ["pi5_8gb", "pi5_16gb"],
        "displays": ["7ips_hdmi_touch", "eink_7"],
        "keyboards": ["60_mechanical"],
        "power": ["custom_18650_4cell"],
        "enclosures": ["pelican_1150", "3d_printed_custom"],
        "os": ["pi_os", "dietpi"],
        "accessories": ["lora", "ham_radio", "solar_panel", "offline_wikipedia", "usb_storage"],
        "budget_range": [300, 1000],
    },
    "media": {
        "name": "Media Center",
        "description": "Music, movies, streaming, media playback",
        "sbcs": ["pi5_8gb", "pi4_4gb"],
        "displays": ["10ips_hdmi", "7ips_hdmi_touch"],
        "keyboards": ["bluetooth_k380"],
        "power": ["ups_hat_waveshare", "usb_bank_20000"],
        "enclosures": ["3d_printed_custom", "pelican_1150"],
        "os": ["libreelec"],
        "accessories": ["hdmi_output", "speakers", "wireless_keyboard"],
        "budget_range": [150, 500],
    },
    "conversation": {
        "name": "Conversation Piece / Cosplay",
        "description": "Aesthetic statement, cosplay prop, display piece",
        "sbcs": ["zero2w", "pi4_4gb"],
        "displays": ["5ips_hdmi", "7ips_hdmi_touch", "oled_13"],
        "keyboards": ["thumb_bbq20kbd", "bluetooth_k380"],
        "power": ["pisugar_3", "usb_bank_20000"],
        "enclosures": ["found_object", "3d_printed_custom"],
        "os": ["twister_os", "pi_os"],
        "accessories": ["leds", "themed_aesthetics"],
        "budget_range": [150, 800],
    },
}

COMPATIBILITY_RULES = {
    "hdmi": ["pi5_16gb", "pi5_8gb", "pi5_4gb", "pi4_8gb", "pi4_4gb", "orange_pi_5", "lattepanda_mu"],
    "hdmi_mini": ["zero2w"],
    "dsi": ["pi5_16gb", "pi5_8gb", "pi5_4gb", "pi4_8gb", "pi4_4gb"],
    "spi": ["pi5_16gb", "pi5_8gb", "pi5_4gb", "pi4_8gb", "pi4_4gb", "zero2w", "orange_pi_5"],
    "i2c": ["pi5_16gb", "pi5_8gb", "pi5_4gb", "pi4_8gb", "pi4_4gb", "zero2w", "orange_pi_5"],
    "usbc_dp": ["orange_pi_5", "lattepanda_mu"],
    "dp": ["lattepanda_mu"],
    "usb4": ["lattepanda_mu"],
}

# ============================================================
# LEARNING SYSTEM
# ============================================================
class CyberdeckLearner:
    """Tracks learned knowledge from videos, user interactions, and builds."""

    def __init__(self):
        self.learnings = self._load_learnings()

    def _load_learnings(self) -> Dict[str, Any]:
        if os.path.exists(CYBERDECK_LEARNINGS_FILE):
            try:
                with open(CYBERDECK_LEARNINGS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "video_knowledge": [],
            "user_patterns": {},
            "build_history": [],
            "component_preferences": {},
            "tips_learned": [],
            "flaws_fixed": [],
            "updated_at": datetime.now().isoformat(),
        }

    def _save_learnings(self):
        self.learnings["updated_at"] = datetime.now().isoformat()
        with open(CYBERDECK_LEARNINGS_FILE, 'w') as f:
            json.dump(self.learnings, f, indent=2)

    def learn_from_video(self, title: str, url: str, key_points: List[str], components_found: List[str], tips: List[str]):
        entry = {
            "title": title,
            "url": url,
            "key_points": key_points,
            "components": components_found,
            "tips": tips,
            "learned_at": datetime.now().isoformat(),
        }
        self.learnings["video_knowledge"].append(entry)
        for tip in tips:
            if tip not in self.learnings["tips_learned"]:
                self.learnings["tips_learned"].append(tip)
        self._save_learnings()

    def learn_from_user(self, user_id: int, prompt: str, category: str, preferences: Dict):
        uid = str(user_id)
        if uid not in self.learnings["user_patterns"]:
            self.learnings["user_patterns"][uid] = {"builds": [], "preferences": {}}
        self.learnings["user_patterns"][uid]["builds"].append({
            "prompt": prompt[:200],
            "category": category,
            "preferences": preferences,
            "timestamp": datetime.now().isoformat(),
        })
        for k, v in preferences.items():
            self.learnings["user_patterns"][uid]["preferences"][k] = v
        self._save_learnings()

    def learn_flaw_fix(self, flaw: str, fix: str, category: str):
        self.learnings["flaws_fixed"].append({
            "flaw": flaw,
            "fix": fix,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_learnings()

    def get_tips_for_category(self, category: str) -> List[str]:
        return [t for t in self.learnings.get("tips_learned", [])][:10]

    def get_learned_components(self) -> List[str]:
        components = set()
        for vk in self.learnings.get("video_knowledge", []):
            components.update(vk.get("components", []))
        return list(components)

    def get_user_preferences(self, user_id: int) -> Dict:
        return self.learnings.get("user_patterns", {}).get(str(user_id), {}).get("preferences", {})

# ============================================================
# COMPATIBILITY ENGINE
# ============================================================
class CompatibilityEngine:
    """Validates all components work together without errors."""

    @staticmethod
    def check_sbc_display(sbc_id: str, display_id: str) -> Tuple[bool, str]:
        sbc = SBC_DATABASE.get(sbc_id)
        display = DISPLAY_DATABASE.get(display_id)
        if not sbc or not display:
            return False, "Unknown component"
        interface = display.get("interface", "")
        compatible_sbcs = COMPATIBILITY_RULES.get(interface, [])
        if sbc_id in compatible_sbcs:
            return True, f"{display['name']} ({interface}) is compatible with {sbc['name']}"
        return False, f"{display['name']} ({interface}) is NOT compatible with {sbc['name']}. Use: {', '.join(SBC_DATABASE[s]['name'] for s in compatible_sbcs if s in SBC_DATABASE)}"

    @staticmethod
    def check_sbc_keyboard(sbc_id: str, keyboard_id: str) -> Tuple[bool, str]:
        sbc = SBC_DATABASE.get(sbc_id)
        keyboard = KEYBOARD_DATABASE.get(keyboard_id)
        if not sbc or not keyboard:
            return False, "Unknown component"
        conn = keyboard.get("connectivity", "")
        if conn == "usb" and sbc_id != "zero2w":
            return True, f"{keyboard['name']} (USB) works with {sbc['name']}"
        if conn == "usb" and sbc_id == "zero2w":
            return True, f"{keyboard['name']} (USB) works with Zero 2W via OTG cable"
        if conn == "bluetooth":
            return True, f"{keyboard['name']} (Bluetooth) works with any SBC with Bluetooth"
        if conn in ("i2c", "gpio"):
            return True, f"{keyboard['name']} ({conn}) connects via GPIO header on {sbc['name']}"
        if conn == "usb_trrs":
            return True, f"{keyboard['name']} (TRRS split) connects via USB"
        return True, f"Likely compatible — verify specific model"

    @staticmethod
    def check_sbc_power(sbc_id: str, power_id: str) -> Tuple[bool, str]:
        sbc = SBC_DATABASE.get(sbc_id)
        power = POWER_DATABASE.get(power_id)
        if not sbc or not power:
            return False, "Unknown component"
        if sbc_id == "lattepanda_mu" and power_id in ("pisugar_3", "usb_bank_20000"):
            return False, f"LattePanda Mu needs 65–100W PD. {power['name']} is insufficient."
        if sbc_id == "jetson_orin_nano" and power_id in ("pisugar_3", "usb_bank_20000"):
            return False, f"Jetson Orin Nano needs DC barrel jack. {power['name']} won't work."
        return True, f"{power['name']} can power {sbc['name']}"

    @staticmethod
    def check_full_build(components: Dict[str, str]) -> Dict[str, Any]:
        issues = []
        warnings = []
        passed = []
        sbc = components.get("sbc")
        display = components.get("display")
        keyboard = components.get("keyboard")
        power = components.get("power")

        if sbc and display:
            ok, msg = CompatibilityEngine.check_sbc_display(sbc, display)
            (passed if ok else issues).append(f"Display: {msg}")

        if sbc and keyboard:
            ok, msg = CompatibilityEngine.check_sbc_keyboard(sbc, keyboard)
            (passed if ok else warnings).append(f"Keyboard: {msg}")

        if sbc and power:
            ok, msg = CompatibilityEngine.check_sbc_power(sbc, power)
            (passed if ok else issues).append(f"Power: {msg}")

        if power and power in ("pisugar_3",) and sbc and sbc in ("pi5_16gb", "pi5_8gb"):
            warnings.append("PiSugar 3 has limited capacity for Pi 5. Consider UPS HAT or power bank for longer runtime.")

        if display and display in ("eink_7", "eink_4") and sbc and sbc in ("pi5_16gb", "pi5_8gb"):
            warnings.append("E-ink display cannot show video or dynamic content. Pi 5 power may be wasted.")

        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "passed": passed,
            "score": len(passed) / max(len(passed) + len(issues) + len(warnings), 1),
        }

# ============================================================
# BUILD GENERATOR
# ============================================================
class BuildGenerator:
    """Generates complete cyberdeck builds from prompts and categories."""

    def __init__(self, learner: CyberdeckLearner):
        self.learner = learner

    def generate_build(self, prompt: str, category: str = None, tier: str = "intermediate",
                       custom_parts: Dict[str, str] = None, user_id: int = None) -> Dict[str, Any]:
        if not category:
            category = self._detect_category(prompt)

        cat_config = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS["coding"])
        tier_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
        tier_idx = tier_map.get(tier, 1)

        components = self._select_components(cat_config, tier_idx, custom_parts or {})

        compat = CompatibilityEngine.check_full_build(components)

        if not compat["compatible"]:
            components = self._fix_flaws(components, compat["issues"], cat_config, tier_idx)
            compat = CompatibilityEngine.check_full_build(components)

        build = {
            "prompt": prompt,
            "category": category,
            "category_name": cat_config["name"],
            "tier": tier,
            "components": components,
            "compatibility": compat,
            "bom": self._generate_bom(components, cat_config),
            "tutorial": self._generate_tutorial(components, cat_config, tier),
            "tips": self._get_tips(category, tier),
            "optional_enhancements": self._get_enhancements(category, components),
            "soldering_notes": self._get_soldering_notes(tier, components),
            "aesthetic_suggestions": self._get_aesthetic_suggestions(category, tier),
            "upgrade_paths": self._get_upgrade_paths(components, category),
            "generated_at": datetime.now().isoformat(),
        }

        if user_id:
            self.learner.learn_from_user(user_id, prompt, category, {"tier": tier, "sbc": components.get("sbc"), "display": components.get("display")})

        return build

    def _detect_category(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        keywords = {
            "coding": ["code", "program", "develop", "terminal", "vim", "ssh", "server", "python", "javascript", "rust", "golang"],
            "writerdeck": ["write", "writing", "journal", "note", "distraction", "focus", "typing", "author", "book"],
            "security": ["hack", "security", "pentest", "kali", "network", "scan", "vulnerability", "red team", "rf", "sdr"],
            "gaming": ["game", "retro", "emulator", "retropie", "console", "play", "nes", "snes", "genesis"],
            "research": ["research", "field", "travel", "note", "data", "collect", "survey", "expedition"],
            "ai": ["ai", "machine learning", "llm", "inference", "neural", "gpu", "cuda", "model", "vision"],
            "survival": ["survival", "emergency", "off-grid", "disaster", "prepper", "radio", "lora", "ham"],
            "media": ["media", "movie", "music", "kodi", "stream", "video", "player", "home theater"],
            "conversation": ["show", "cool", "cyberpunk", "cosplay", "display", "aesthetic", "prop", "art"],
        }
        scores = {}
        for cat, kws in keywords.items():
            score = sum(1 for kw in kws if kw in prompt_lower)
            if score > 0:
                scores[cat] = score
        if scores:
            return max(scores, key=scores.get)
        return "coding"

    def _select_components(self, cat_config: Dict, tier_idx: int, custom_parts: Dict) -> Dict[str, str]:
        components = {}
        sbcs = cat_config.get("sbcs", ["pi5_8gb"])
        tier_names = ["beginner", "intermediate", "advanced"]
        tier_name = tier_names[tier_idx]
        best_sbc = sbcs[0]
        for s in sbcs:
            sbc_data = SBC_DATABASE.get(s, {})
            if sbc_data.get("tier") == tier_name:
                best_sbc = s
                break
        if custom_parts.get("sbc"):
            best_sbc = custom_parts["sbc"]
        components["sbc"] = best_sbc

        displays = cat_config.get("displays", ["7ips_hdmi_touch"])
        best_display = displays[0]
        if custom_parts.get("display"):
            best_display = custom_parts["display"]
        components["display"] = best_display

        keyboards = cat_config.get("keyboards", ["60_mechanical"])
        best_keyboard = keyboards[0]
        if custom_parts.get("keyboard"):
            best_keyboard = custom_parts["keyboard"]
        components["keyboard"] = best_keyboard

        powers = cat_config.get("power", ["ups_hat_waveshare"])
        best_power = powers[0]
        if custom_parts.get("power"):
            best_power = custom_parts["power"]
        components["power"] = best_power

        enclosures = cat_config.get("enclosures", ["3d_printed_custom"])
        best_enclosure = enclosures[0]
        if custom_parts.get("enclosure"):
            best_enclosure = custom_parts["enclosure"]
        components["enclosure"] = best_enclosure

        os_list = cat_config.get("os", ["pi_os"])
        components["os"] = os_list[0]

        extras = custom_parts.get("extras", [])
        if extras:
            components["extras"] = extras

        return components

    def _fix_flaws(self, components: Dict, issues: List[str], cat_config: Dict, tier_idx: int) -> Dict[str, str]:
        fixed = dict(components)
        for issue in issues:
            if "NOT compatible" in issue and "display" in issue.lower():
                displays = cat_config.get("displays", ["7ips_hdmi_touch"])
                for d in displays:
                    ok, _ = CompatibilityEngine.check_sbc_display(fixed.get("sbc", ""), d)
                    if ok:
                        fixed["display"] = d
                        break
            if "insufficient" in issue and "power" in issue.lower():
                powers = cat_config.get("power", ["ups_hat_waveshare"])
                for p in powers:
                    ok, _ = CompatibilityEngine.check_sbc_power(fixed.get("sbc", ""), p)
                    if ok:
                        fixed["power"] = p
                        break
            self.learner.learn_flaw_fix(issue, f"Auto-fixed by selecting compatible component", cat_config.get("name", "unknown"))
        return fixed

    def _generate_bom(self, components: Dict, cat_config: Dict) -> List[Dict[str, Any]]:
        bom = []
        sbc = SBC_DATABASE.get(components.get("sbc", ""), {})
        if sbc:
            bom.append({"item": sbc["name"], "type": "SBC", "price": sbc.get("price", 0), "essential": True})
        display = DISPLAY_DATABASE.get(components.get("display", ""), {})
        if display:
            bom.append({"item": display["name"], "type": "Display", "price": display.get("price", 0), "essential": True})
        keyboard = KEYBOARD_DATABASE.get(components.get("keyboard", ""), {})
        if keyboard:
            bom.append({"item": keyboard["name"], "type": "Keyboard", "price": keyboard.get("price_range", [0])[0], "essential": True})
        power = POWER_DATABASE.get(components.get("power", ""), {})
        if power:
            bom.append({"item": power["name"], "type": "Power", "price": power.get("price", 0), "essential": True})
        enclosure = ENCLOSURE_DATABASE.get(components.get("enclosure", ""), {})
        if enclosure:
            bom.append({"item": enclosure["name"], "type": "Enclosure", "price": enclosure.get("price", 0), "essential": True})
        bom.append({"item": "MicroSD Card (64GB+)", "type": "Storage", "price": 15, "essential": True})
        bom.append({"item": "USB-C Power Cable", "type": "Cable", "price": 8, "essential": True})
        bom.append({"item": "Micro HDMI to HDMI Cable", "type": "Cable", "price": 10, "essential": True})
        bom.append({"item": "M2/M3/M4 Bolt Pack", "type": "Hardware", "price": 8, "essential": True})
        bom.append({"item": "Standoffs Pack", "type": "Hardware", "price": 5, "essential": False})
        bom.append({"item": "Heat Shrink Tubing", "type": "Wiring", "price": 5, "essential": False})
        bom.append({"item": "Wire (22AWG, assorted)", "type": "Wiring", "price": 6, "essential": False})
        extras = components.get("extras", [])
        for extra in extras:
            bom.append({"item": extra, "type": "Extra", "price": 0, "essential": False})
        total = sum(item["price"] for item in bom)
        bom.append({"item": "TOTAL ESTIMATED", "type": "", "price": total, "essential": True})
        return bom

    def _generate_tutorial(self, components: Dict, cat_config: Dict, tier: str) -> str:
        sbc = SBC_DATABASE.get(components.get("sbc", ""), {})
        display = DISPLAY_DATABASE.get(components.get("display", ""), {})
        keyboard = KEYBOARD_DATABASE.get(components.get("keyboard", ""), {})
        power = POWER_DATABASE.get(components.get("power", ""), {})
        enclosure = ENCLOSURE_DATABASE.get(components.get("enclosure", ""), {})
        os_data = OS_DATABASE.get(components.get("os", ""), {})
        lines = [
            f"# Cyberdeck Build Tutorial — {cat_config['name']}",
            f"**Tier:** {tier.upper()}",
            f"**SBC:** {sbc.get('name', 'Unknown')}",
            f"**Display:** {display.get('name', 'Unknown')}",
            f"**Keyboard:** {keyboard.get('name', 'Unknown')}",
            f"**Power:** {power.get('name', 'Unknown')}",
            f"**Enclosure:** {enclosure.get('name', 'Unknown')}",
            f"**OS:** {os_data.get('name', 'Unknown')}",
            "",
            "## Phase 1: Unbox and Verify",
            f"1. Open all component packages and verify nothing is damaged.",
            f"2. Check that your {sbc.get('name', 'SBC')} board is the correct model.",
            f"3. Verify the {display.get('name', 'display')} screen is intact.",
            f"4. Confirm your {keyboard.get('name', 'keyboard')} connects via {keyboard.get('connectivity', 'USB')}.",
            f"5. Test the {power.get('name', 'power supply')} outputs the correct voltage.",
            "",
            "## Phase 2: Prototype on Bench",
            f"6. Place the {sbc.get('name', 'SBC')} on a non-conductive surface.",
            f"7. Connect the {display.get('name', 'display')} to the SBC via {display.get('interface', 'HDMI')}.",
            f"8. Plug the {keyboard.get('name', 'keyboard')} into the SBC.",
            f"9. Connect the {power.get('name', 'power supply')} to the SBC.",
            f"10. Insert a microSD card with {os_data.get('name', 'the OS')} flashed (use Raspberry Pi Imager).",
            f"11. Power on and verify the display shows the boot screen.",
            f"12. Test keyboard input — type some text in the terminal.",
            f"13. Test Wi-Fi connectivity if applicable.",
            f"14. If anything fails, diagnose now before building the enclosure.",
            "",
            "## Phase 3: Enclosure Preparation",
            f"15. If 3D printing: print the case in sections (PETG recommended, 40–60% infill).",
            f"16. If using Pelican case: cut foam to fit components.",
            f"17. If found object: plan component mounting points.",
            f"18. Test-fit all components in the enclosure before permanent mounting.",
            f"19. Mark and drill/cut any access holes for ports and cables.",
            "",
            "## Phase 4: Assembly",
            f"20. Mount the {sbc.get('name', 'SBC')} using standoffs.",
            f"21. Install the {display.get('name', 'display')} in the lid or front panel.",
            f"22. Mount the {keyboard.get('name', 'keyboard')} in the base.",
            f"23. Install the {power.get('name', 'power supply')} — ensure battery is secured.",
            f"24. Route all cables cleanly — use cable ties or clips.",
            f"25. Connect all cables: display, keyboard, power.",
            f"26. Install any status LEDs or switches if desired.",
            f"27. Add cooling if needed — fan or heatsink.",
            "",
            "## Phase 5: Software Setup",
            f"28. Flash {os_data.get('name', 'Raspberry Pi OS')} to microSD.",
            f"29. Boot and complete initial OS setup.",
            f"30. Configure display resolution and rotation if needed.",
            f"31. Install essential applications for your use case.",
            f"32. Configure power management and low-battery shutdown.",
            "",
            "## Phase 6: Testing",
            f"33. Run the deck for 30+ minutes under load to test thermals.",
            f"34. Verify battery runtime meets expectations.",
            f"35. Test all ports and connections.",
            f"36. Verify keyboard and any pointing device work correctly.",
            f"37. Run any specific software needed for your category.",
            "",
            "## Phase 7: Finishing",
            f"38. Close up the enclosure.",
            f"39. Add any labels, stickers, or aesthetic touches.",
            f"40. Document your build — take photos and notes.",
            f"41. Share with the community on Discord or Reddit!",
            "",
            "**Total estimated build time:** " + ("1–3 days (beginner)" if tier == "beginner" else "1–2 weeks (intermediate)" if tier == "intermediate" else "2–8 weeks (advanced)"),
        ]
        return "\n".join(lines)

    def _get_tips(self, category: str, tier: str) -> List[str]:
        tips = [
            "Always prototype on the bench before building the enclosure.",
            "Design for future upgrades — modular design is a core cyberdeck strength.",
            "Use PETG for 3D printed cases — more impact-resistant and heat-tolerant than PLA.",
            "Plan your cable routing before assembly — clean wiring is a mark of a quality build.",
            "Keep screws and small parts in labeled bags during assembly.",
            "Test at each stage — discovering problems after full assembly means disassembly.",
        ]
        if category == "security":
            tips.extend([
                "Mount external antennas on the case face for easy access.",
                "Keep Kali on a separate SD card you can swap in when needed.",
                "Add a hardware kill switch for Wi-Fi — visible toggle switch on the case.",
            ])
        elif category == "writerdeck":
            tips.extend([
                "Consider removing the browser entirely for a distraction-free experience.",
                "E-ink displays use almost no power — your battery will last much longer.",
                "A 40% keyboard forces you to use layers, which can actually speed up typing.",
            ])
        elif category == "gaming":
            tips.extend([
                "USB game controllers (8BitDo, Xbox) work great with RetroPie.",
                "HDMI output to a TV is often better than a small built-in display for gaming.",
                "Consider adding speakers or a headphone jack for audio.",
            ])
        elif category == "ai":
            tips.extend([
                "NVMe SSD is essential for loading large models quickly.",
                "Active cooling is mandatory for sustained AI inference workloads.",
                "The Jetson Orin Nano is the best choice if you need GPU acceleration.",
            ])
        if tier == "beginner":
            tips.extend([
                "You don't need to solder for a beginner build — everything can connect via USB.",
                "Thrift stores are goldmines for cheap keyboards and enclosures.",
                "Start simple, then upgrade — your first build teaches you what you actually need.",
            ])
        elif tier == "advanced":
            tips.extend([
                "Soldering gives you the cleanest internal wiring — invest in a good iron.",
                "GPIO switches and LEDs add a lot of character to a build.",
                "Consider a custom PCB for clean internal connections.",
            ])
        learned_tips = self.learner.get_tips_for_category(category)
        tips.extend(learned_tips)
        return tips[:15]

    def _get_enhancements(self, category: str, components: Dict) -> List[Dict[str, str]]:
        enhancements = [
            {"name": "NVMe SSD via HAT", "description": "Boot from NVMe instead of microSD — 5x faster I/O", "price": 40, "difficulty": "intermediate"},
            {"name": "Status OLED Display", "description": "1.3\" OLED showing CPU temp, battery, IP address", "price": 10, "difficulty": "beginner"},
            {"name": "USB Hub (4-port)", "description": "Internal hub for extra USB ports", "price": 15, "difficulty": "beginner"},
            {"name": "Active Cooling Fan", "description": "Temperature-controlled 30mm fan", "price": 10, "difficulty": "beginner"},
            {"name": "Power LED + Switch", "description": "Visible power indicator and hard power switch", "price": 5, "difficulty": "beginner"},
            {"name": "External Wi-Fi Antenna", "description": "High-power antenna for range (AWUS036ACH)", "price": 30, "difficulty": "intermediate"},
            {"name": "SDR Dongle", "description": "RTL-SDR for radio exploration", "price": 30, "difficulty": "beginner"},
        ]
        if category == "security":
            enhancements.append({"name": "GPIO Hardware Kill Switch", "description": "Physical switch to disable Wi-Fi/Bluetooth", "price": 5, "difficulty": "intermediate"})
        if category == "gaming":
            enhancements.append({"name": "Bluetooth Game Controller", "description": "8BitDo or Xbox controller for gaming", "price": 40, "difficulty": "beginner"})
        if category == "writerdeck":
            enhancements.append({"name": "E-ink Display Upgrade", "description": "Switch to e-ink for ultra-low power writing", "price": 80, "difficulty": "intermediate"})
        return enhancements

    def _get_soldering_notes(self, tier: str, components: Dict) -> Dict[str, Any]:
        notes = {
            "required": False,
            "skill_level": "basic" if tier == "beginner" else "intermediate",
            "common_tasks": ["Power switch wiring", "LED connections", "GPIO wiring"],
            "guide": "Basic soldering skills are often required for power switches and custom connections. Start with tinning wires, then practice through-hole soldering.",
            "optional": True,
            "note": "Soldering is optional for all tiers. You can build a fully functional cyberdeck without soldering using USB connections and pre-made cables.",
        }
        if tier == "beginner":
            notes["recommendation"] = "No soldering required. Use USB power banks and plug-and-play components."
        elif tier == "intermediate":
            notes["recommendation"] = "Soldering optional but helpful for power switches and cleaner internal wiring."
        else:
            notes["recommendation"] = "Soldering recommended for custom connections, GPIO switches, and LED indicators."
        return notes

    def _get_aesthetic_suggestions(self, category: str, tier: str) -> List[str]:
        suggestions = [
            "Exposed screws and bolts enhance the industrial cyberpunk look",
            "Visible wiring can be a feature — use colored wire and route it cleanly",
            "Metal toggle switches and arcade buttons add tactile character",
            "LED indicators (power, network, activity) add visual feedback",
        ]
        if category == "conversation":
            suggestions.extend([
                "Neon accents and UV-reactive paint for cyberpunk aesthetic",
                "Retro terminal fonts (cool-retro-term) for software theme",
                "Exposed circuit boards visible through transparent panels",
                "Vintage or military surplus enclosures for authentic character",
            ])
        elif category == "security":
            suggestions.extend([
                "Military-grade Pelican case for field-ready appearance",
                "External antenna mounts with SMA connectors",
                "Tactical labeling and hazard stripes",
                "Locking clasps and rubber gaskets",
            ])
        elif category == "writerdeck":
            suggestions.extend([
                "Clean, minimal aesthetic — less is more",
                "Wood or leather accents for warmth",
                "Low-profile design for portability",
            ])
        return suggestions

    def _get_upgrade_paths(self, components: Dict, category: str) -> List[Dict[str, str]]:
        paths = []
        sbc = components.get("sbc", "")
        if sbc in ("pi4_4gb", "pi4_8gb"):
            paths.append({"from": "Pi 4", "to": "Pi 5 8GB", "benefit": "2–3x faster CPU, NVMe support", "cost": "$75"})
        if sbc in ("zero2w",):
            paths.append({"from": "Zero 2W", "to": "Pi 4 4GB", "benefit": "More RAM, better performance", "cost": "$55"})
        if "microsd" in str(components).lower():
            paths.append({"from": "microSD boot", "to": "NVMe SSD via HAT", "benefit": "5x faster I/O, more reliable", "cost": "$40"})
        if "7ips_hdmi_touch" == components.get("display"):
            paths.append({"from": "7\" 1024x600", "to": "7\" 1280x800 or 10\"", "benefit": "Sharper text, more screen space", "cost": "$20–$50"})
        paths.append({"from": "Basic enclosure", "to": "Custom 3D printed", "benefit": "Perfect fit, custom aesthetics", "cost": "$10 filament"})
        return paths


# ============================================================
# CYBERDECK AGENT
# ============================================================
class CyberdeckAgent:
    """Main cyberdeck agent — builds, upgrades, teaches, learns."""

    def __init__(self):
        self.learner = CyberdeckLearner()
        self.generator = BuildGenerator(self.learner)
        self.build_history = self._load_history()
        self.version = "1.0.0"

    def _load_history(self) -> List[Dict]:
        if os.path.exists(CYBERDECK_BUILD_HISTORY):
            try:
                with open(CYBERDECK_BUILD_HISTORY, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        with open(CYBERDECK_BUILD_HISTORY, 'w') as f:
            json.dump(self.build_history[-100:], f, indent=2)

    async def build_from_prompt(self, prompt: str, tier: str = "intermediate",
                                 custom_parts: Dict[str, str] = None, user_id: int = None) -> Dict[str, Any]:
        build = self.generator.generate_build(prompt, tier=tier, custom_parts=custom_parts or {}, user_id=user_id)
        self.build_history.append({
            "prompt": prompt[:200],
            "category": build["category"],
            "tier": tier,
            "sbc": build["components"].get("sbc"),
            "compatible": build["compatibility"]["compatible"],
            "timestamp": datetime.now().isoformat(),
        })
        self._save_history()
        return build

    async def pick_components(self, category: str, tier: str = "intermediate",
                               custom_parts: Dict[str, str] = None) -> Dict[str, Any]:
        cat_config = CATEGORY_DEFAULTS.get(category)
        if not cat_config:
            return {"error": f"Unknown category: {category}. Use: {', '.join(CATEGORY_DEFAULTS.keys())}"}
        components = self.generator._select_components(cat_config, {"beginner": 0, "intermediate": 1, "advanced": 2}.get(tier, 1), custom_parts or {})
        compat = CompatibilityEngine.check_full_build(components)
        result = {
            "category": cat_config["name"],
            "tier": tier,
            "components": {},
            "compatibility": compat,
        }
        for key, val in components.items():
            if key == "extras":
                result["components"]["extras"] = val
                continue
            db = {"sbc": SBC_DATABASE, "display": DISPLAY_DATABASE, "keyboard": KEYBOARD_DATABASE, "power": POWER_DATABASE, "enclosure": ENCLOSURE_DATABASE, "os": OS_DATABASE}.get(key, {})
            data = db.get(val, {})
            result["components"][key] = {"id": val, "name": data.get("name", val), "price": data.get("price", 0), "details": data}
        return result

    async def check_compatibility(self, components: Dict[str, str]) -> Dict[str, Any]:
        return CompatibilityEngine.check_full_build(components)

    async def generate_bom(self, prompt: str, tier: str = "intermediate") -> List[Dict]:
        build = await self.build_from_prompt(prompt, tier)
        return build["bom"]

    async def generate_tutorial(self, prompt: str, tier: str = "intermediate") -> str:
        build = await self.build_from_prompt(prompt, tier)
        return build["tutorial"]

    async def suggest_upgrades(self, components: Dict[str, str], category: str = "coding") -> List[Dict]:
        return self.generator._get_upgrade_paths(components, category)

    async def fix_flaws(self, components: Dict[str, str], category: str = "coding", tier: str = "intermediate") -> Dict[str, Any]:
        compat = CompatibilityEngine.check_full_build(components)
        if compat["compatible"]:
            return {"status": "already_compatible", "components": components, "compatibility": compat}
        tier_idx = {"beginner": 0, "intermediate": 1, "advanced": 2}.get(tier, 1)
        cat_config = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS["coding"])
        fixed = self.generator._fix_flaws(components, compat["issues"], cat_config, tier_idx)
        new_compat = CompatibilityEngine.check_full_build(fixed)
        return {"status": "fixed", "original_issues": compat["issues"], "components": fixed, "compatibility": new_compat}

    async def search_parts(self, query: str) -> Dict[str, Any]:
        results = {"query": query, "suggestions": [], "sources": [
            "Amazon (amazon.com)", "Adafruit (adafruit.com)", "Pimoroni (shop.pimoroni.com)",
            "PiShop.us (pishop.us)", "CanaKit (canakit.com)", "AliExpress",
        ]}
        query_lower = query.lower()
        for sid, sbc in SBC_DATABASE.items():
            if any(kw in sbc["name"].lower() or kw in query_lower for kw in query_lower.split()):
                results["suggestions"].append({"type": "SBC", "name": sbc["name"], "price": sbc["price"], "id": sid})
        for did, display in DISPLAY_DATABASE.items():
            if any(kw in display["name"].lower() or kw in query_lower for kw in query_lower.split()):
                results["suggestions"].append({"type": "Display", "name": display["name"], "price": display["price"], "id": did})
        for kid, kb in KEYBOARD_DATABASE.items():
            if any(kw in kb["name"].lower() or kw in query_lower for kw in query_lower.split()):
                results["suggestions"].append({"type": "Keyboard", "name": kb["name"], "price_range": kb["price_range"], "id": kid})
        return results

    async def learn_from_video(self, title: str, url: str, key_points: List[str], components: List[str], tips: List[str]):
        self.learner.learn_from_video(title, url, key_points, components, tips)
        return {"status": "learned", "title": title, "knowledge_count": len(self.learner.learnings.get("video_knowledge", []))}

    async def analyze_image(self, image_description: str) -> Dict[str, Any]:
        result = {
            "description": image_description,
            "identified_components": [],
            "suggested_category": "coding",
            "suggested_build": None,
        }
        desc_lower = image_description.lower()
        found = []
        for sid, sbc in SBC_DATABASE.items():
            if any(kw in desc_lower for kw in sbc["name"].lower().split()):
                found.append({"type": "SBC", "id": sid, "name": sbc["name"]})
        for did, display in DISPLAY_DATABASE.items():
            if any(kw in desc_lower for kw in display["name"].lower().split()):
                found.append({"type": "Display", "id": did, "name": display["name"]})
        result["identified_components"] = found
        return result

    async def generate_ideas(self, category: str = None) -> List[Dict[str, str]]:
        ideas = [
            {"title": "The Minimalist Writer", "category": "writerdeck", "description": "Pi Zero 2W + 4.2\" e-ink + 40% ortho keyboard. Ultra-portable distraction-free writing machine.", "difficulty": "beginner"},
            {"title": "The Field Hacker", "category": "security", "description": "Pi 5 8GB + 7\" touch + Kali + external Wi-Fi antenna + SDR. Portable red-team lab.", "difficulty": "intermediate"},
            {"title": "The Retro Gamer", "category": "gaming", "description": "Pi 4 4GB + 7\" HDMI + RetroPie + USB controller + Pelican case. Portable arcade.", "difficulty": "beginner"},
            {"title": "The AI Terminal", "category": "ai", "description": "Jetson Orin Nano + 10\" HDMI + NVMe + active cooling. Local LLM inference in the field.", "difficulty": "advanced"},
            {"title": "The Off-Grid Comms", "category": "survival", "description": "Pi 5 + e-ink + LoRa + ham radio + solar panel + 4x 18650 cells. Emergency communication deck.", "difficulty": "advanced"},
            {"title": "The Dual-Screen Dev", "category": "coding", "description": "Pi 5 16GB + 7\" main + 5\" secondary OLED status display + Planck keyboard. Maximum productivity.", "difficulty": "advanced"},
            {"title": "The Cinema Deck", "category": "media", "description": "Pi 4 + 10\" HDMI + speakers + wireless keyboard + LibreELEC. Portable home theater.", "difficulty": "beginner"},
            {"title": "The Cyberpunk Prop", "category": "conversation", "description": "Zero 2W + OLED + neon LEDs + vintage briefcase enclosure + mechanical keyboard. Pure aesthetic.", "difficulty": "intermediate"},
            {"title": "The Research Station", "category": "research", "description": "Pi 5 8GB + 10\" sunlight-readable + NVMe + 6x 18650 + offline Wikipedia. Field research powerhouse.", "difficulty": "intermediate"},
            {"title": "The Recovery Kit", "category": "coding", "description": "Pi 5 + Pelican 1450 + 7\" touch + Planck keyboard + Ethernet switch + UPS HAT. Jay Doscher inspired.", "difficulty": "advanced"},
        ]
        if category:
            ideas = [i for i in ideas if i["category"] == category]
        return ideas

    async def generate_code(self, request: str, language: str = "python") -> Dict[str, str]:
        code_templates = {
            "battery_monitor": {
                "python": """#!/usr/bin/env python3
import smbus2 import smbus
import time

BUS = smbus.SMBus(1)
ADDRESS = 0x36

def read_voltage():
    data = BUS.read_word_data(ADDRESS, 0x02)
    voltage = (data & 0xFFFF) * 1.25 / 1000 / 16
    return round(voltage, 2)

def read_capacity():
    data = BUS.read_word_data(ADDRESS, 0x04)
    capacity = (data & 0xFFFF) * 256 / 10000
    return round(capacity, 1)

if __name__ == "__main__":
    while True:
        print(f"Battery: {read_voltage()}V | Capacity: {read_capacity()}%")
        time.sleep(5)
""",
                "description": "Read battery voltage and capacity via I2C (for UPS HATs)",
            },
            "temp_monitor": {
                "python": """#!/usr/bin/env python3
import subprocess
import time

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = float(f.read().strip()) / 1000
    return round(temp, 1)

def get_fan_speed(temp):
    if temp > 70:
        return "FULL"
    elif temp > 55:
        return "HIGH"
    elif temp > 40:
        return "MEDIUM"
    else:
        return "LOW"

if __name__ == "__main__":
    while True:
        temp = get_cpu_temp()
        fan = get_fan_speed(temp)
        print(f"CPU: {temp}°C | Fan: {fan}")
        time.sleep(10)
""",
                "description": "Monitor CPU temperature and control fan speed",
            },
            "led_status": {
                "python": """#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

POWER_LED = 17
ACTIVITY_LED = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_LED, GPIO.OUT)
GPIO.setup(ACTIVITY_LED, GPIO.OUT)

GPIO.output(POWER_LED, GPIO.HIGH)

try:
    while True:
        GPIO.output(ACTIVITY_LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(ACTIVITY_LED, GPIO.LOW)
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
""",
                "description": "Blink status LEDs via GPIO",
            },
            "low_battery_shutdown": {
                "python": """#!/usr/bin/env python3
import smbus2 as smbus
import subprocess
import time

BUS = smbus.SMBus(1)
ADDRESS = 0x36
SHUTDOWN_THRESHOLD = 3.0

def read_voltage():
    data = BUS.read_word_data(ADDRESS, 0x02)
    voltage = (data & 0xFFFF) * 1.25 / 1000 / 16
    return round(voltage, 2)

if __name__ == "__main__":
    while True:
        v = read_voltage()
        print(f"Battery: {v}V")
        if v < SHUTDOWN_THRESHOLD:
            print("Low battery! Shutting down...")
            subprocess.run(["sudo", "shutdown", "-h", "now"])
        time.sleep(60)
""",
                "description": "Auto-shutdown on low battery to protect SD card",
            },
            "qmk_keymap": {
                "c": """// QMK Keymap for Cyberdeck
#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT_ortho_4x12(
        KC_GRV,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_BSPC,
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_BSLS,
        KC_ESC,  KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, KC_QUOT,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, KC_RSFT
    ),
};
""",
                "description": "Basic QMK keymap for 40% ortholinear keyboard",
            },
        }
        req_lower = request.lower()
        for key, template in code_templates.items():
            if key.replace("_", " ") in req_lower or key in req_lower:
                return {"code": template.get(language, template.get("python", "")), "description": template["description"], "language": language}
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                prompt = f"Write {language} code for a cyberdeck project: {request}\nProvide clean, commented code."
                response = provider.generate(prompt)
                return {"code": response, "description": f"AI-generated {language} code", "language": language}
        except Exception:
            pass
        return {"code": f"# TODO: Implement {request} in {language}", "description": "Template — customize for your needs", "language": language}

    def get_status(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "total_builds": len(self.build_history),
            "learned_videos": len(self.learner.learnings.get("video_knowledge", [])),
            "learned_tips": len(self.learner.learnings.get("tips_learned", [])),
            "flaws_fixed": len(self.learner.learnings.get("flaws_fixed", [])),
            "categories": list(CATEGORY_DEFAULTS.keys()),
            "tiers": ["beginner", "intermediate", "advanced"],
            "sbc_count": len(SBC_DATABASE),
            "display_count": len(DISPLAY_DATABASE),
            "keyboard_count": len(KEYBOARD_DATABASE),
        }

    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"name": v["name"], "description": v["description"], "budget_range": v["budget_range"]} for k, v in CATEGORY_DEFAULTS.items()}

    def get_sbc_for_category(self, category: str) -> List[Dict[str, Any]]:
        cat_config = CATEGORY_DEFAULTS.get(category, {})
        sbc_ids = cat_config.get("sbcs", [])
        return [{"id": sid, **SBC_DATABASE.get(sid, {})} for sid in sbc_ids if sid in SBC_DATABASE]


# ============================================================
# SINGLETON
# ============================================================
_agent_instance = None

def get_cyberdeck_agent() -> CyberdeckAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CyberdeckAgent()
    return _agent_instance
