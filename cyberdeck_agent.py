"""
Cyberdeck Agent v3.0 — Full-featured cyberdeck builder, learner, and evolution engine.
Watches videos, analyzes images, builds from prompts, picks best components,
validates compatibility, generates tutorials, and gets smarter over time.
"""
import os, json, time, logging, hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

VERSION = "3.0.0"
LEARNINGS_FILE = "cyberdeck_learnings.json"
BUILD_HISTORY_FILE = "cyberdeck_build_history.json"
VIDEO_QUEUE_FILE = "cyberdeck_video_queue.json"
BUILD_LIST_FILE = "CYBERDECK_BUILD_LIST.md"

# ============================================================
# TIER SYSTEM
# ============================================================
TIERS = {
    "beginner": {
        "name": "Beginner (Easy)",
        "budget": "$100-$300",
        "soldering": "Optional",
        "skills": "Plug together, basic Linux",
        "build_time": "1-3 days",
        "risk": "Minimal",
    },
    "intermediate": {
        "name": "Intermediate (Moderate)",
        "budget": "$300-$700",
        "soldering": "Optional but helpful",
        "skills": "3D printing, cable management",
        "build_time": "1-2 weeks",
        "risk": "Low",
    },
    "advanced": {
        "name": "Advanced (Expert)",
        "budget": "$700-$3000+",
        "soldering": "Recommended",
        "skills": "Soldering, PCB, QMK firmware",
        "build_time": "2-8+ weeks",
        "risk": "Minimal (with validation)",
    },
}

# ============================================================
# CATEGORY SYSTEM
# ============================================================
CATEGORIES = {
    "coding": {
        "name": "Coding & Development",
        "description": "Portable coding, terminal work, remote server admin, software development",
        "budget_range": "$300-$1200",
        "best_sbc": "pi5_16gb",
        "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60",
        "best_power": "ups_h5180",
        "best_enclosure": "3d_printed",
        "best_cooling": "active_fan",
        "best_os": "raspberry_pi_os",
        "best_connectivity": "usb_ethernet",
        "pcb": "waveshare_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_18awg",
        "soldering_tips": "Power switch, GPIO wiring",
        "aesthetic": "Industrial with exposed screws",
    },
    "writerdeck": {
        "name": "Writerdeck",
        "description": "Distraction-free writing, journaling, note-taking",
        "budget_range": "$100-$400",
        "best_sbc": "pi_zero_2w",
        "best_display": "eink_7inch",
        "best_keyboard": "ortho_40",
        "best_power": "pisugar3_plus",
        "best_enclosure": "3d_printed",
        "best_cooling": "passive_heatsink",
        "best_os": "writerdeck_os",
        "best_connectivity": "cat6_flat",
        "pcb": "penkesu_pcb",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_20awg",
        "soldering_tips": "Battery connection, power switch",
        "aesthetic": "Minimal, clean, retro",
    },
    "security": {
        "name": "Security & Pentesting",
        "description": "Network analysis, red team, RF exploration",
        "budget_range": "$400-$1500",
        "best_sbc": "pi5_16gb",
        "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60",
        "best_power": "ups_h5180",
        "best_enclosure": "pelican_1450",
        "best_cooling": "active_fan",
        "best_os": "kali_linux",
        "best_connectivity": "awus036ach",
        "pcb": "waveshare_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_18awg",
        "soldering_tips": "Antenna wiring, GPIO switches",
        "aesthetic": "Military black, tactical",
    },
    "gaming": {
        "name": "Retro Gaming & Media",
        "description": "Emulation, retro gaming, media playback",
        "budget_range": "$150-$500",
        "best_sbc": "pi5_8gb",
        "best_display": "hdmi_7inch_ips",
        "best_keyboard": "controller",
        "best_power": "power_bank_20000",
        "best_enclosure": "3d_printed",
        "best_cooling": "passive_heatsink",
        "best_os": "retropie",
        "best_connectivity": "cat6_flat",
        "pcb": "adafruit_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_20awg",
        "soldering_tips": "Controller wiring, speaker connections",
        "aesthetic": "Retro, neon, arcade",
    },
    "research": {
        "name": "Field Research",
        "description": "Fieldwork, data collection, offline reference",
        "budget_range": "$300-$800",
        "best_sbc": "pi5_8gb",
        "best_display": "sunlight_readable_7",
        "best_keyboard": "mech_60",
        "best_power": "custom_18650_x6",
        "best_enclosure": "pelican_1400",
        "best_cooling": "passive_heatsink",
        "best_os": "raspberry_pi_os",
        "best_connectivity": "usb_ethernet",
        "pcb": "waveshare_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_18awg",
        "soldering_tips": "Battery wiring, weatherproofing",
        "aesthetic": "Rugged, utilitarian",
    },
    "ai": {
        "name": "AI & Machine Learning",
        "description": "Local AI inference, LLM hosting, computer vision",
        "budget_range": "$500-$2000",
        "best_sbc": "jetson_orin_nano",
        "best_display": "hdmi_10inch",
        "best_keyboard": "mech_60",
        "best_power": "ups_h5180",
        "best_enclosure": "3d_printed_vented",
        "best_cooling": "active_fan_heatsink",
        "best_os": "jetpack",
        "best_connectivity": "usb_ethernet",
        "pcb": "jetson_carrier",
        "wire_signal": "silicon_24awg",
        "wire_power": "silicon_16awg",
        "soldering_tips": "Fan wiring, NVMe power",
        "aesthetic": "Futuristic, LED accent",
    },
    "survival": {
        "name": "Survival & Off-Grid",
        "description": "Emergency computing, off-grid comms, disaster preparedness",
        "budget_range": "$300-$1000",
        "best_sbc": "pi5_8gb",
        "best_display": "eink_7inch",
        "best_keyboard": "thumb_keyboard",
        "best_power": "solar_panel_18w",
        "best_enclosure": "pelican_1450",
        "best_cooling": "passive_heatsink",
        "best_os": "raspberry_pi_os",
        "best_connectivity": "lora_module",
        "pcb": "waveshare_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_16awg",
        "soldering_tips": "Solar wiring, LoRa antenna",
        "aesthetic": "Military green, rugged",
    },
    "media": {
        "name": "Media Center",
        "description": "Music, movies, streaming, media playback",
        "budget_range": "$150-$500",
        "best_sbc": "pi5_4gb",
        "best_display": "hdmi_10inch",
        "best_keyboard": "bt_keyboard_trackpad",
        "best_power": "power_bank_20000",
        "best_enclosure": "3d_printed",
        "best_cooling": "passive_heatsink",
        "best_os": "libreelec",
        "best_connectivity": "cat6_flat",
        "pcb": "adafruit_phat",
        "wire_signal": "silicon_26awg",
        "wire_power": "silicon_20awg",
        "soldering_tips": "Speaker wiring, HDMI routing",
        "aesthetic": "Sleek, modern",
    },
    "conversation": {
        "name": "Conversation Piece / Cosplay",
        "description": "Aesthetic statement, cosplay prop, display piece",
        "budget_range": "$150-$800",
        "best_sbc": "pi_zero_2w",
        "best_display": "oled_1_3inch",
        "best_keyboard": "bt_keyboard",
        "best_power": "pisugar3_plus",
        "best_enclosure": "3d_printed_cyberpunk",
        "best_cooling": "passive_heatsink",
        "best_os": "twister_os",
        "best_connectivity": "wifi_antenna_pigtail",
        "pcb": "custom_neon_pcb",
        "wire_signal": "silicon_26awg_neon",
        "wire_power": "silicon_20awg",
        "soldering_tips": "LED wiring, neo pixel strips",
        "aesthetic": "Cyberpunk, neon, exposed",
    },
}

# ============================================================
# SBC DATABASE — Best of the best per category
# ============================================================
SBC_DATABASE = {
    "pi5_16gb": {
        "name": "Raspberry Pi 5 16GB",
        "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core",
        "ram": "16GB LPDDR4X",
        "gpu": "VideoCore VII",
        "storage": "MicroSD + NVMe via HAT",
        "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2",
        "gpio": "40-pin GPIO header",
        "video_output": "2x micro-HDMI (4K@60Hz)",
        "price": 120,
        "power_draw": "5V/5A USB-C (27W max)",
        "form_factor": "85mm x 56mm",
        "pros": ["Most powerful Pi", "16GB RAM for heavy workloads", "NVMe support", "Dual 4K HDMI"],
        "cons": ["Needs active cooling", "Requires official 27W PSU"],
        "best_for": ["coding", "security", "research", "ai"],
        "compatibility": ["ALL"],
    },
    "pi5_8gb": {
        "name": "Raspberry Pi 5 8GB",
        "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core",
        "ram": "8GB LPDDR4X",
        "gpu": "VideoCore VII",
        "storage": "MicroSD + NVMe via HAT",
        "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2",
        "gpio": "40-pin GPIO header",
        "video_output": "2x micro-HDMI (4K@60Hz)",
        "price": 80,
        "power_draw": "5V/5A USB-C (27W max)",
        "form_factor": "85mm x 56mm",
        "pros": ["Great price/performance", "NVMe support", "Dual HDMI"],
        "cons": ["Needs active cooling"],
        "best_for": ["coding", "security", "research", "gaming", "media"],
        "compatibility": ["ALL"],
    },
    "pi5_4gb": {
        "name": "Raspberry Pi 5 4GB",
        "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core",
        "ram": "4GB LPDDR4X",
        "gpu": "VideoCore VII",
        "storage": "MicroSD + NVMe via HAT",
        "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2",
        "gpio": "40-pin GPIO header",
        "video_output": "2x micro-HDMI (4K@60Hz)",
        "price": 60,
        "power_draw": "5V/5A USB-C (27W max)",
        "form_factor": "85mm x 56mm",
        "pros": ["Affordable Pi 5", "Good for media/light tasks"],
        "cons": ["4GB limits heavy workloads"],
        "best_for": ["media", "gaming"],
        "compatibility": ["ALL"],
    },
    "pi4_8gb": {
        "name": "Raspberry Pi 4 8GB",
        "cpu": "BCM2711 Cortex-A72 @ 1.5GHz quad-core",
        "ram": "8GB LPDDR4",
        "gpu": "VideoCore VI",
        "storage": "MicroSD + USB SSD",
        "connectivity": "WiFi 5, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2",
        "gpio": "40-pin GPIO header",
        "video_output": "2x micro-HDMI (4K@30Hz)",
        "price": 55,
        "power_draw": "5V/3A USB-C (15W)",
        "form_factor": "85mm x 56mm",
        "pros": ["Mature ecosystem", "Huge community", "Cheap"],
        "cons": ["Older CPU", "No NVMe native"],
        "best_for": ["gaming", "media", "research"],
        "compatibility": ["ALL"],
    },
    "pi_zero_2w": {
        "name": "Raspberry Pi Zero 2 W",
        "cpu": "BCM2710A1 Cortex-A53 @ 1GHz quad-core",
        "ram": "512MB LPDDR2",
        "gpu": "VideoCore IV",
        "storage": "MicroSD",
        "connectivity": "WiFi (2.4GHz), BT 4.2, 1x USB OTG, mini-HDMI",
        "gpio": "40-pin GPIO header (unpopulated)",
        "video_output": "mini-HDMI (1080p)",
        "price": 15,
        "power_draw": "5V/2.5A micro-USB",
        "form_factor": "65mm x 30mm",
        "pros": ["Tiny", "Ultra cheap", "Low power", "Perfect for writerdeck"],
        "cons": ["512MB RAM limits multitasking", "mini-HDMI needs adapter"],
        "best_for": ["writerdeck", "conversation", "survival"],
        "compatibility": ["ALL"],
    },
    "orange_pi_5": {
        "name": "Orange Pi 5 16GB",
        "cpu": "RK3588S Cortex-A76+A55 octa-core",
        "ram": "16GB LPDDR4x",
        "gpu": "Mali-G610 MC4",
        "storage": "eMMC + NVMe + MicroSD",
        "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.0, USB 2.0",
        "gpio": "40-pin GPIO",
        "video_output": "HDMI 2.1 + USB-C DP",
        "price": 90,
        "power_draw": "5V/4A USB-C",
        "form_factor": "89mm x 56mm",
        "pros": ["More powerful than Pi 5", "NPU for AI", "eMMC support", "NVMe"],
        "cons": ["Smaller community", "Driver quirks"],
        "best_for": ["ai", "coding", "security"],
        "compatibility": ["ALL"],
    },
    "jetson_orin_nano": {
        "name": "NVIDIA Jetson Orin Nano 8GB",
        "cpu": "6-core Arm Cortex-A78AE",
        "ram": "8GB LPDDR5",
        "gpu": "1024-core NVIDIA Ampere + 32 Tensor Cores",
        "storage": "MicroSD + NVMe",
        "connectivity": "WiFi 5, BT 5.0, GbE, USB 3.2 x2, USB 2.0 x2",
        "gpio": "40-pin GPIO header",
        "video_output": "HDMI 2.1 (4K@60Hz)",
        "price": 249,
        "power_draw": "7W-15W (configurable)",
        "form_factor": "100mm x 87mm",
        "pros": ["40 TOPS AI performance", "GPU + Tensor Cores", "Camera support", "Industrial"],
        "cons": ["Expensive", "Needs good cooling", "JetPack required"],
        "best_for": ["ai"],
        "compatibility": ["hdmi_7inch_ips", "hdmi_10inch", "active_fan_heatsink", "ups_h5180"],
    },
    "lattepanda_3_delta": {
        "name": "LattePanda 3 Delta 864",
        "cpu": "Intel N100 (4C/4T, 3.4GHz)",
        "ram": "8GB LPDDR5",
        "gpu": "Intel UHD Graphics",
        "storage": "eMMC 64GB + M.2 NVMe",
        "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.2, USB-C",
        "gpio": "Arduino Leonardo co-processor",
        "video_output": "USB-C DP + HDMI 2.0",
        "price": 269,
        "power_draw": "5V/3A USB-C",
        "form_factor": "125mm x 78mm",
        "pros": ["Full x86 Windows/Linux", "Arduino co-processor", "NVMe"],
        "cons": ["Expensive", "More power draw", "Larger"],
        "best_for": ["coding", "research"],
        "compatibility": ["hdmi_7inch_ips", "hdmi_10inch", "active_fan_heatsink", "ups_h5180"],
    },
    "orange_pi_zero3": {
        "name": "Orange Pi Zero 3",
        "cpu": "Allwinner H618 Cortex-A53 quad-core",
        "ram": "4GB LPDDR4",
        "gpu": "Mali-G57 MC1",
        "storage": "MicroSD + eMMC",
        "connectivity": "WiFi 5, BT 5.1, GbE, USB 2.0 x2",
        "gpio": "26-pin GPIO header",
        "video_output": "Micro-HDMI (4K@60Hz)",
        "price": 20,
        "power_draw": "5V/2A USB-C",
        "form_factor": "65mm x 50mm",
        "pros": ["Ultra cheap", "4K HDMI", "Good Pi Zero alternative"],
        "cons": ["Smaller community", "No USB 3.0"],
        "best_for": ["writerdeck", "conversation", "gaming"],
        "compatibility": ["ALL"],
    },
    "cm5": {
        "name": "Raspberry Pi CM5 16GB",
        "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core",
        "ram": "16GB LPDDR4X",
        "gpu": "VideoCore VII",
        "storage": "eMMC + MicroSD + NVMe",
        "connectivity": "PCIe Gen 3 x1, USB 3.0, GbE",
        "gpio": "2x 100-pin connectors",
        "video_output": "Depends on carrier board",
        "price": 110,
        "power_draw": "5V/4A",
        "form_factor": "55mm x 40mm (module only)",
        "pros": ["Most powerful compute module", "Industrial grade", "NVMe", "eMMC"],
        "cons": ["Needs carrier board", "More complex"],
        "best_for": ["ai", "coding", "security"],
        "compatibility": ["waveshare_cm5_carrier", "all_displays"],
    },
    "cm4": {
        "name": "Raspberry Pi CM4 8GB",
        "cpu": "BCM2711 Cortex-A72 @ 1.5GHz quad-core",
        "ram": "8GB LPDDR4",
        "gpu": "VideoCore VI",
        "storage": "eMMC + MicroSD",
        "connectivity": "PCIe Gen 2 x1, USB 3.0, GbE",
        "gpio": "2x 100-pin connectors",
        "video_output": "Depends on carrier board",
        "price": 55,
        "power_draw": "5V/3A",
        "form_factor": "55mm x 40mm (module only)",
        "pros": ["Mature ecosystem", "Cheap", "Lots of carrier boards"],
        "cons": ["Needs carrier board"],
        "best_for": ["gaming", "media", "writerdeck"],
        "compatibility": ["waveshare_cm4_carrier", "all_displays"],
    },
}

# ============================================================
# DISPLAY DATABASE
# ============================================================
DISPLAY_DATABASE = {
    "hdmi_7inch_ips": {
        "name": "Waveshare 7\" HDMI IPS (1024x600)",
        "size": "7 inch",
        "resolution": "1024x600",
        "interface": "HDMI + USB-C touch",
        "price": 40,
        "power_draw": "5V/1A via USB",
        "touch": True,
        "viewing_angle": "178 degrees",
        "pros": ["IPS wide angle", "Capacitive touch", "Cheap", "Bright"],
        "cons": ["Needs HDMI adapter for Pi Zero"],
        "best_for": ["ALL"],
    },
    "hdmi_7inch_1024": {
        "name": "Waveshare 7\" HDMI IPS (1280x800)",
        "size": "7 inch",
        "resolution": "1280x800",
        "interface": "HDMI + USB-C touch",
        "price": 50,
        "power_draw": "5V/1A via USB",
        "touch": True,
        "viewing_angle": "178 degrees",
        "pros": ["Higher resolution", "Sharp text for coding"],
        "cons": ["Slightly more expensive"],
        "best_for": ["coding", "security", "research"],
    },
    "hdmi_10inch": {
        "name": "Waveshare 10.1\" HDMI IPS (1280x800)",
        "size": "10.1 inch",
        "resolution": "1280x800",
        "interface": "HDMI + USB-C touch",
        "price": 65,
        "power_draw": "5V/1.5A via USB",
        "touch": True,
        "viewing_angle": "178 degrees",
        "pros": ["Large screen", "Good for media/AI", "IPS"],
        "cons": ["Larger enclosure needed"],
        "best_for": ["ai", "media", "research"],
    },
    "dsi_7inch": {
        "name": "Raspberry Pi Official 7\" DSI Touchscreen",
        "size": "7 inch",
        "resolution": "800x480",
        "interface": "DSI ribbon cable",
        "price": 60,
        "power_draw": "5V/0.5A via GPIO",
        "touch": True,
        "viewing_angle": "170 degrees",
        "pros": ["Official Pi accessory", "Direct DSI (no HDMI)", "GPIO pass-through"],
        "cons": ["Lower resolution", "Bulky bezel"],
        "best_for": ["coding", "gaming"],
    },
    "eink_7inch": {
        "name": "Waveshare 7.5\" E-Ink (800x480)",
        "size": "7.5 inch",
        "resolution": "800x480",
        "interface": "SPI",
        "price": 70,
        "power_draw": "Near zero (static), ~15mA refresh",
        "touch": False,
        "viewing_angle": "180 degrees (full)",
        "pros": ["Sunlight readable", "Ultra low power", "Paper-like", "No eye strain"],
        "cons": ["Slow refresh", "No color", "No touch"],
        "best_for": ["writerdeck", "survival"],
    },
    "eink_4_2inch": {
        "name": "Waveshare 4.2\" E-Ink (400x300)",
        "size": "4.2 inch",
        "resolution": "400x300",
        "interface": "SPI",
        "price": 30,
        "power_draw": "Near zero",
        "touch": False,
        "viewing_angle": "180 degrees",
        "pros": ["Tiny", "Ultra cheap", "Paper-like"],
        "cons": ["Small text", "Slow refresh", "No touch"],
        "best_for": ["writerdeck", "survival"],
    },
    "oled_1_3inch": {
        "name": "SSD1306 1.3\" OLED (128x64)",
        "size": "1.3 inch",
        "resolution": "128x64",
        "interface": "I2C",
        "price": 8,
        "power_draw": "~10mA",
        "touch": False,
        "viewing_angle": "160 degrees",
        "pros": ["Tiny", "Ultra cheap", "Low power", "Great for status display"],
        "cons": ["Tiny", "Monochrome"],
        "best_for": ["conversation", "writerdeck"],
    },
    "sunlight_readable_7": {
        "name": "Sunread 7\" Sunlight Readable (1024x600)",
        "size": "7 inch",
        "resolution": "1024x600",
        "interface": "HDMI + USB touch",
        "price": 120,
        "power_draw": "5V/2A via USB",
        "touch": True,
        "viewing_angle": "178 degrees",
        "pros": ["1000 nits brightness", "Direct sunlight readable", "IPS"],
        "cons": ["Expensive", "Higher power draw"],
        "best_for": ["research", "survival"],
    },
    "hdmi_5inch": {
        "name": "Waveshare 5\" HDMI IPS (800x480)",
        "size": "5 inch",
        "resolution": "800x480",
        "interface": "HDMI + USB touch",
        "price": 25,
        "power_draw": "5V/0.5A via USB",
        "touch": True,
        "viewing_angle": "178 degrees",
        "pros": ["Small", "Cheap", "Touch"],
        "cons": ["Low resolution"],
        "best_for": ["conversation", "writerdeck"],
    },
}

# ============================================================
# KEYBOARD DATABASE
# ============================================================
KEYBOARD_DATABASE = {
    "mech_60": {
        "name": "60% Mechanical Keyboard (Keychron K12 / HyperX Alloy 60)",
        "type": "Mechanical 60%",
        "layout": "60% ANSI",
        "switches": "Gateron Brown/Red/Blue",
        "connection": "USB-C / BT",
        "price_range": "$40-$80",
        "size_mm": "285 x 100",
        "pros": ["Compact", "Great typing", "RGB backlight", "QMK/VIA support"],
        "cons": ["No function row"],
        "best_for": ["coding", "security", "research", "ai"],
    },
    "ortho_40": {
        "name": "Planck / OLKB 40% Ortholinear",
        "type": "Ortholinear 40%",
        "layout": "40% grid",
        "switches": "Cherry MX compatible",
        "connection": "USB-C",
        "price_range": "$80-$150",
        "size_mm": "270 x 115",
        "pros": ["Ultra compact", "Programmable QMK", "Cyberdeck classic", "Split option"],
        "cons": ["Learning curve", "No number row"],
        "best_for": ["writerdeck", "coding", "conversation"],
    },
    "corne_split": {
        "name": "Corne / CRKBD Split Keyboard",
        "type": "Split 3x6",
        "layout": "36 keys split",
        "switches": "Cherry MX compatible",
        "connection": "USB-C / wireless",
        "price_range": "$100-$200",
        "size_mm": "120 x 120 (each half)",
        "pros": ["Ergonomic", "Split design", "Minimal", "QMK firmware"],
        "cons": ["Assembly required", "Learning curve"],
        "best_for": ["writerdeck", "coding"],
    },
    "thumb_keyboard": {
        "name": "Pinky3 / Thumb Keyboard",
        "type": "Thumb-based",
        "layout": "Compact thumb",
        "switches": "Cherry MX / Kailh",
        "connection": "USB-C / wireless",
        "price_range": "$60-$120",
        "size_mm": "150 x 100",
        "pros": ["Held in one hand", "Field use", "Compact"],
        "cons": ["Limited keys", "Learning curve"],
        "best_for": ["survival", "research"],
    },
    "bt_keyboard": {
        "name": "Logitech K380 / Bluetooth Compact",
        "type": "Membrane BT",
        "layout": "Full compact",
        "switches": "Membrane",
        "connection": "Bluetooth",
        "price_range": "$30-$50",
        "size_mm": "279 x 124",
        "pros": ["Multi-device", "No wires", "Cheap", "Proven"],
        "cons": ["Membrane feel", "Not QMK"],
        "best_for": ["media", "conversation", "gaming"],
    },
    "bt_keyboard_trackpad": {
        "name": "Keyboards + Trackpad Combo (Rii i8+)",
        "type": "Wireless combo",
        "layout": "Mini keyboard + touchpad",
        "switches": "Membrane",
        "connection": "2.4GHz USB dongle",
        "price_range": "$20-$35",
        "size_mm": "145 x 95",
        "pros": ["Keyboard + mouse in one", "Tiny", "Media center ideal"],
        "cons": ["Small keys", "Dongle required"],
        "best_for": ["media", "gaming"],
    },
    "vintage_keyboard": {
        "name": "Vintage Mechanical (Model M / Cherry G80)",
        "type": "Full-size vintage",
        "layout": "Full ANSI",
        "switches": "Buckling spring / Cherry MX",
        "connection": "USB adapter",
        "price_range": "$30-$100",
        "size_mm": "450 x 160",
        "pros": ["Epic typing feel", "Cyberpunk aesthetic", "Built like a tank"],
        "cons": ["Huge", "Heavy", "Needs adapter"],
        "best_for": ["conversation", "coding"],
    },
}

# ============================================================
# POWER DATABASE
# ============================================================
POWER_DATABASE = {
    "ups_h5180": {
        "name": "Waveshare UPS HAT (5V/5A, 18650 x4)",
        "type": "UPS HAT",
        "capacity": "12000mAh (4x 18650)",
        "output": "5V/5A",
        "charge_time": "~4 hours",
        "runtime": "4-8 hours (depending on load)",
        "price": 45,
        "pros": ["Auto power switch", "Charges while running", "Battery level I2C"],
        "cons": ["Batteries not included", "Adds height"],
        "best_for": ["coding", "security", "research", "ai"],
    },
    "pisugar3_plus": {
        "name": "PiSugar 3 Plus (5000mAh)",
        "type": "SBC-mount battery",
        "capacity": "5000mAh",
        "output": "5V/3A",
        "charge_time": "~3 hours",
        "runtime": "3-6 hours",
        "price": 35,
        "pros": ["Sits under Pi Zero/3A+", "RTC clock", "Button control", "Compact"],
        "cons": ["Pi Zero only", "Limited capacity"],
        "best_for": ["writerdeck", "conversation", "survival"],
    },
    "power_bank_20000": {
        "name": "Anker 20000mAh Power Bank",
        "type": "USB power bank",
        "capacity": "20000mAh",
        "output": "5V/3A, 9V/2A, 12V/1.5A",
        "charge_time": "~6 hours",
        "runtime": "8-15 hours",
        "price": 35,
        "pros": ["High capacity", "USB-C PD", "No soldering", "Portable"],
        "cons": ["Bulky", "Not integrated"],
        "best_for": ["gaming", "media", "research", "coding"],
    },
    "custom_18650_x6": {
        "name": "Custom 18650 x6 (BMS + Buck Converter)",
        "type": "Custom 6-cell",
        "capacity": "18000mAh",
        "output": "5V/5A (buck)",
        "charge_time": "~5 hours",
        "runtime": "10-20 hours",
        "price": 30,
        "pros": ["Massive capacity", "Field repairable", "Custom voltage"],
        "cons": ["Soldering required", "Needs BMS", "Larger"],
        "best_for": ["survival", "research", "security"],
    },
    "solar_panel_18w": {
        "name": "TP-Link SolarGo 18W Panel + Battery Pack",
        "type": "Solar charging",
        "capacity": "20000mAh battery + 18W panel",
        "output": "5V/2.4A USB",
        "charge_time": "4-6 hours (sunlight)",
        "runtime": "Continuous (sunlight dependent)",
        "price": 50,
        "pros": ["Off-grid", "Sustainable", "Emergency power"],
        "cons": ["Weather dependent", "Slow charge"],
        "best_for": ["survival", "research"],
    },
}

# ============================================================
# ENCLOSURE DATABASE
# ============================================================
ENCLOSURE_DATABASE = {
    "pelican_1450": {
        "name": "Pelican 1450 Case",
        "material": "Polypropylene",
        "dimensions": "350 x 250 x 160mm",
        "protection": "IP67 waterproof, crushproof, dustproof",
        "foam": "Pick-and-pluck foam interior",
        "price": 80,
        "pros": ["Ultimate protection", "Professional look", "Weatherproof", "Jay Doscher inspired"],
        "cons": ["Heavy", "Expensive", "Needs cutting"],
        "best_for": ["security", "survival", "research"],
    },
    "pelican_1400": {
        "name": "Pelican 1400 Case",
        "material": "Polypropylene",
        "dimensions": "325 x 235 x 140mm",
        "protection": "IP67 waterproof",
        "foam": "Pick-and-pluck foam",
        "price": 60,
        "pros": ["Smaller Pelican", "Waterproof", "Professional"],
        "cons": ["Needs foam cutting"],
        "best_for": ["research", "survival"],
    },
    "3d_printed": {
        "name": "Custom 3D Printed Enclosure",
        "material": "PLA / PETG / ABS",
        "dimensions": "Variable (custom fit)",
        "protection": "Basic splash-resistant",
        "price": 5,
        "pros": ["Fully customizable", "Cheap", "Fast iteration", "Open source designs"],
        "cons": ["Not waterproof", "Needs printer", "Weaker material"],
        "best_for": ["coding", "gaming", "media", "conversation", "writerdeck"],
    },
    "3d_printed_cyberpunk": {
        "name": "3D Printed Cyberpunk Shell",
        "material": "PLA + Neon filament",
        "dimensions": "Variable",
        "protection": "Basic",
        "price": 10,
        "pros": ["Aesthetic", "LED cutouts", "Exposed screws", "Industrial look"],
        "cons": ["Fragile", "Needs finishing"],
        "best_for": ["conversation"],
    },
    "3d_printed_vented": {
        "name": "3D Printed Vented Enclosure",
        "material": "PETG / ABS",
        "dimensions": "Variable (with fan cutouts)",
        "protection": "Splash-resistant with vents",
        "price": 8,
        "pros": ["Airflow design", "Fan mounting", "Custom fit"],
        "cons": ["Less dust protection"],
        "best_for": ["ai", "coding"],
    },
    "apache_3800": {
        "name": "Apache 3800 (Harbor Freight)",
        "material": "Polypropylene",
        "dimensions": "360 x 260 x 140mm",
        "protection": "IP67",
        "foam": "Pick-and-pluck foam",
        "price": 30,
        "pros": ["Cheaper Pelican alternative", "Waterproof", "Solid"],
        "cons": ["Less premium feel"],
        "best_for": ["security", "research"],
    },
    "found_object": {
        "name": "Found Object / Upcycled Enclosure",
        "material": "Vintage briefcase, ammo box, etc.",
        "dimensions": "Variable",
        "protection": "Varies",
        "price": 0,
        "pros": ["Free", "Unique character", "Sustainable", "Story"],
        "cons": ["Not purpose-built", "Needs modification"],
        "best_for": ["conversation", "gaming", "media"],
    },
}

# ============================================================
# COOLING DATABASE
# ============================================================
COOLING_DATABASE = {
    "active_fan": {
        "name": "Active Fan (Official Pi 5 Active Cooler)",
        "type": "Active",
        "cooling_power": "High",
        "noise": "Moderate",
        "price": 5,
        "pros": ["Official", "Easy install", "Effective", "Cheap"],
        "cons": ["Fan noise"],
        "best_for": ["coding", "security", "research"],
    },
    "active_fan_heatsink": {
        "name": "Active Fan + Heatsink Combo (ICE Tower)",
        "type": "Active + Passive",
        "cooling_power": "Very High",
        "noise": "Moderate",
        "price": 20,
        "pros": ["Best cooling", "Tower design", "Handles sustained loads"],
        "cons": ["Tall", "More expensive"],
        "best_for": ["ai", "coding"],
    },
    "passive_heatsink": {
        "name": "Passive Heatsink (Aluminum/Copper)",
        "type": "Passive",
        "cooling_power": "Moderate",
        "noise": "Silent",
        "price": 8,
        "pros": ["Silent", "No moving parts", "Reliable"],
        "cons": ["Lower cooling capacity"],
        "best_for": ["writerdeck", "gaming", "media", "conversation", "survival"],
    },
    "thermal_paste": {
        "name": "Thermal Paste (Arctic MX-6)",
        "type": "Compound",
        "cooling_power": "Improves any cooler by 5-10C",
        "noise": "N/A",
        "price": 8,
        "pros": ["Easy apply", "Reduces temps", "Lasts years"],
        "cons": ["Needs reapply every few years"],
        "best_for": ["ALL"],
    },
    "copper_spreader": {
        "name": "Copper Heat Spreader / Shim",
        "type": "Passive",
        "cooling_power": "Moderate-High",
        "noise": "Silent",
        "price": 12,
        "pros": ["Excellent thermal conductivity", "Thin profile", "Silent"],
        "cons": ["Needs thermal paste", "Precise fit"],
        "best_for": ["ai", "coding", "security"],
    },
    "fan_controller": {
        "name": "PWM Fan Controller HAT",
        "type": "Active (controlled)",
        "cooling_power": "Variable (auto-adjust)",
        "noise": "Variable (temp-based)",
        "price": 15,
        "pros": ["Auto temperature control", "Silent at low temps", "GPIO controlled"],
        "cons": ["Extra HAT", "Needs wiring"],
        "best_for": ["ai", "coding", "security", "research"],
    },
}

# ============================================================
# PCB / CARRIER BOARD DATABASE
# ============================================================
PCB_DATABASE = {
    "waveshare_phat": {
        "name": "Waveshare UPS HAT / Motor HAT / Sensor HAT",
        "type": "Pi HAT (stackable)",
        "pins": "40-pin GPIO passthrough",
        "compatibility": "Pi 5, Pi 4, Pi 3, CM4",
        "price_range": "$10-$35",
        "pros": ["Stackable", "Official form factor", "Huge range"],
        "cons": ["Pi-specific"],
        "best_for": ["coding", "security", "research", "gaming", "media"],
    },
    "jetson_carrier": {
        "name": "Jetson Orin Nano Developer Kit Carrier",
        "type": "Jetson carrier board",
        "pins": "40-pin GPIO + CSI camera",
        "compatibility": "Jetson Orin Nano only",
        "price_range": "Included with dev kit",
        "pros": ["Official carrier", "Camera support", "MIPI CSI"],
        "cons": ["Jetson-specific"],
        "best_for": ["ai"],
    },
    "waveshare_cm5_carrier": {
        "name": "Waveshare CM5 IO Board",
        "type": "CM5 carrier",
        "pins": "Full 40-pin GPIO + M.2 + eMMC",
        "compatibility": "CM5 only",
        "price_range": "$25-$45",
        "pros": ["Full IO breakout", "M.2 slot", "Compact"],
        "cons": ["CM5 only"],
        "best_for": ["ai", "coding", "security"],
    },
    "waveshare_cm4_carrier": {
        "name": "Waveshare CM4 IO Board",
        "type": "CM4 carrier",
        "pins": "Full 40-pin GPIO + M.2",
        "compatibility": "CM4 only",
        "price_range": "$20-$35",
        "pros": ["Full IO", "M.2 NVMe", "Compact"],
        "cons": ["CM4 only"],
        "best_for": ["gaming", "media", "writerdeck"],
    },
    "adafruit_phat": {
        "name": "Adafruit pHAT / Bonnet",
        "type": "Pi HAT (small)",
        "pins": "26-pin GPIO (subset)",
        "compatibility": "Pi Zero, Pi 3, Pi 4, Pi 5",
        "price_range": "$10-$25",
        "pros": ["Ultra compact", "Great for Pi Zero", "I2C/SPI"],
        "cons": ["Small pin count"],
        "best_for": ["writerdeck", "conversation", "gaming", "media"],
    },
    "penkesu_pcb": {
        "name": "Penkesu Computer PCB (Clamshell)",
        "type": "Custom clamshell PCB",
        "pins": "Pi Zero GPIO + e-ink + keyboard",
        "compatibility": "Pi Zero 2W only",
        "price_range": "$15-$25",
        "pros": ["Clamshell design", "E-ink integrated", "GBA SP hinges"],
        "cons": ["Pi Zero only", "Needs assembly"],
        "best_for": ["writerdeck"],
    },
    "custom_neon_pcb": {
        "name": "Custom Neon LED PCB (WS2812B)",
        "type": "LED strip PCB",
        "pins": "3-wire (5V, GND, Data)",
        "compatibility": "ALL",
        "price_range": "$5-$15",
        "pros": ["Programmable RGB", "Cyberpunk aesthetic", "Any shape"],
        "cons": ["Power hungry", "Needs soldering"],
        "best_for": ["conversation"],
    },
    "sparkfun_phat": {
        "name": "SparkFun Qwiic HAT",
        "type": "I2C HAT",
        "pins": "Qwiic I2C connectors",
        "compatibility": "Pi 5, Pi 4, Pi 3, Zero",
        "price_range": "$10-$20",
        "pros": ["Solderless I2C", "Plug-and-play sensors", "Great ecosystem"],
        "cons": ["I2C only"],
        "best_for": ["research", "survival", "ai"],
    },
}

# ============================================================
# WIRE / CABLE DATABASE
# ============================================================
WIRE_DATABASE = {
    "silicon_26awg": {
        "name": "Silicon Wire 26AWG (Signal)",
        "gauge": "26 AWG",
        "type": "Silicone insulated",
        "current_capacity": "2.2A",
        "use": "Signal, I2C, SPI, UART, GPIO",
        "pros": ["Flexible", "High temp rated", "Stranded", "Easy to strip"],
        "price_per_meter": 0.50,
        "color_options": ["Red", "Black", "Yellow", "Green", "Blue", "White"],
        "best_for": ["ALL"],
    },
    "silicon_24awg": {
        "name": "Silicon Wire 24AWG (Medium Signal/Power)",
        "gauge": "24 AWG",
        "type": "Silicone insulated",
        "current_capacity": "3.5A",
        "use": "Power to small boards, fan power, LED strips",
        "pros": ["Versatile", "Flexible", "Good current"],
        "price_per_meter": 0.60,
        "color_options": ["Red", "Black", "Yellow", "Blue"],
        "best_for": ["ai", "coding"],
    },
    "silicon_20awg": {
        "name": "Silicon Wire 20AWG (Low Power)",
        "gauge": "20 AWG",
        "type": "Silicone insulated",
        "current_capacity": "5A",
        "use": "Battery connections, UPS wiring, low-voltage power",
        "pros": ["Good current", "Flexible", "Safe for battery"],
        "price_per_meter": 0.80,
        "color_options": ["Red", "Black"],
        "best_for": ["writerdeck", "gaming", "media", "conversation"],
    },
    "silicon_18awg": {
        "name": "Silicon Wire 18AWG (Power)",
        "gauge": "18 AWG",
        "type": "Silicone insulated",
        "current_capacity": "10A",
        "use": "Main power, solar panel wiring, battery packs",
        "pros": ["High current", "Flexible", "Low voltage drop"],
        "price_per_meter": 1.00,
        "color_options": ["Red", "Black"],
        "best_for": ["coding", "security", "research", "ai"],
    },
    "silicon_16awg": {
        "name": "Silicon Wire 16AWG (Heavy Power)",
        "gauge": "16 AWG",
        "type": "Silicone insulated",
        "current_capacity": "15A",
        "use": "High-current power, motor wiring, solar systems",
        "pros": ["Very high current", "Low loss", "Durable"],
        "price_per_meter": 1.20,
        "color_options": ["Red", "Black"],
        "best_for": ["ai", "survival"],
    },
    "silicon_26awg_neon": {
        "name": "Silicon Wire 26AWG Neon (LED Accent)",
        "gauge": "26 AWG",
        "type": "Neon colored silicone",
        "current_capacity": "2.2A",
        "use": "LED wiring, accent lighting, WS2812B data",
        "pros": ["Cyberpunk aesthetic", "Neon colors", "Flexible"],
        "price_per_meter": 0.80,
        "color_options": ["Neon Pink", "Neon Green", "Neon Blue", "Neon Orange"],
        "best_for": ["conversation"],
    },
    "ribbon_cable": {
        "name": "IDC Ribbon Cable (DSI/CSI)",
        "gauge": "28 AWG flat",
        "type": "Flat ribbon",
        "current_capacity": "1A per conductor",
        "use": "DSI display, CSI camera, GPIO ribbon",
        "pros": ["Neat", "Proper connectors", "Pi-specific"],
        "price_per_meter": 2.00,
        "color_options": ["Grey", "Rainbow"],
        "best_for": ["ALL"],
    },
    "jst_connector_cable": {
        "name": "JST-PH 2.0mm Connector Cables",
        "gauge": "26 AWG pre-crimped",
        "type": "Pre-crimped JST",
        "current_capacity": "2A",
        "use": "Battery BMS, speaker, sensor connections",
        "pros": ["Solderless", "Quick connect", "Secure", "Safe"],
        "price_per_set": 3.00,
        "color_options": ["Red", "Black", "White", "Green", "Yellow"],
        "best_for": ["ALL"],
    },
    "usb_c_cable": {
        "name": "USB-C to USB-C Cable (240W PD)",
        "gauge": "Internal: 20AWG power + 28AWG signal",
        "type": "USB-C PD cable",
        "current_capacity": "5A @ 48V",
        "use": "Power delivery, data transfer, display output",
        "pros": ["One cable for power+data+display", "Future proof"],
        "price_per_unit": 8.00,
        "best_for": ["ALL"],
    },
}

# ============================================================
# OS DATABASE
# ============================================================
OS_DATABASE = {
    "raspberry_pi_os": {"name": "Raspberry Pi OS (Bookworm)", "based": "Debian 12", "desktop": True, "best_for": ["coding", "research", "survival"]},
    "kali_linux": {"name": "Kali Linux (Pi)", "based": "Debian", "desktop": True, "best_for": ["security"]},
    "ubuntu": {"name": "Ubuntu MATE / Server", "based": "Ubuntu", "desktop": True, "best_for": ["coding", "ai"]},
    "retropie": {"name": "RetroPie", "based": "Debian", "desktop": False, "best_for": ["gaming"]},
    "batocera": {"name": "Batocera.linux", "based": "Buildroot", "desktop": False, "best_for": ["gaming"]},
    "libreelec": {"name": "LibreELEC", "based": "Buildroot", "desktop": False, "best_for": ["media"]},
    "writerdeck_os": {"name": "writerdeckOS / DietPi", "based": "Debian", "desktop": False, "best_for": ["writerdeck"]},
    "twister_os": {"name": "Twister OS", "based": "Raspberry Pi OS", "desktop": True, "best_for": ["conversation"]},
    "jetpack": {"name": "NVIDIA JetPack", "based": "Ubuntu", "desktop": True, "best_for": ["ai"]},
    "arch_linux_arm": {"name": "Arch Linux ARM", "based": "Arch", "desktop": True, "best_for": ["coding", "security"]},
    "dietpi": {"name": "DietPi", "based": "Debian", "desktop": True, "best_for": ["writerdeck", "research", "gaming"]},
}

# ============================================================
# CONNECTIVITY DATABASE — WiFi adapters, LAN cables, switches
# ============================================================
CONNECTIVITY_DATABASE = {
    "awus036ach": {
        "name": "Alfa AWUS036ACH USB WiFi Adapter",
        "type": "USB WiFi Adapter",
        "standard": "WiFi 5 (802.11ac) Dual-Band",
        "frequency": "2.4GHz + 5GHz",
        "speed": "AC1200",
        "antenna": "2x detachable 5dBi",
        " chipset": "Realtek RTL8812AU",
        "connection": "USB 3.0",
        "price": 30,
        "range": "Long range with external antenna",
        "monitor_mode": True,
        "packet_injection": True,
        "pros": ["Best WiFi adapter for pentesting", "Monitor mode + injection", "Dual-band", "External antenna", "Kali compatible"],
        "cons": ["Needs driver install", "USB dongle size"],
        "best_for": ["security", "coding", "research"],
    },
    "awus036acs": {
        "name": "Alfa AWUS036ACS USB WiFi Adapter",
        "type": "USB WiFi Adapter",
        "standard": "WiFi 5 (802.11ac) Dual-Band",
        "frequency": "2.4GHz + 5GHz",
        "speed": "AC1200",
        "antenna": "Internal + 2.4GHz external",
        "chipset": "Realtek RTL8811AU",
        "connection": "USB 3.0",
        "price": 20,
        "range": "Medium range",
        "monitor_mode": True,
        "packet_injection": True,
        "pros": ["Budget pentesting adapter", "Monitor mode", "Dual-band", "Compact"],
        "cons": ["Single external antenna"],
        "best_for": ["security", "coding"],
    },
    "rtl_sdr": {
        "name": "RTL-SDR Blog V3 Dongle",
        "type": "SDR Receiver",
        "standard": "Software Defined Radio",
        "frequency": "24MHz - 1766MHz",
        "speed": "2.4 MSPS",
        "antenna": "Antenna not included (SMA)",
        "chipset": "RTL2832U + R820T2",
        "connection": "USB 2.0",
        "price": 30,
        "range": "Radio spectrum",
        "monitor_mode": False,
        "packet_injection": False,
        "pros": ["ADS-B aircraft tracking", "Ham radio", "Satellite reception", "RF snooping", "Wide frequency range"],
        "cons": ["Receive only", "Needs antenna"],
        "best_for": ["security", "research", "survival"],
    },
    "hackrf_one": {
        "name": "Great Scott Gadgets HackRF One",
        "type": "SDR Transceiver",
        "standard": "Software Defined Radio",
        "frequency": "1MHz - 6GHz",
        "speed": "20 MSPS",
        "antenna": "Antenna not included (SMA)",
        "chipset": "NXP LPC4330 + MAX2837",
        "connection": "USB 3.0",
        "price": 350,
        "range": "Full radio spectrum",
        "monitor_mode": False,
        "packet_injection": False,
        "pros": ["TX + RX capable", "Huge frequency range", "Industry standard", "HackRF compatible"],
        "cons": ["Expensive", "Full-duplex limited"],
        "best_for": ["security", "research"],
    },
    "ethernet_switch": {
        "name": "UGREEN 5-Port Gigabit Ethernet Switch",
        "type": "Network Switch",
        "standard": "Gigabit Ethernet",
        "ports": "5x RJ45 GbE",
        "speed": "1000 Mbps",
        "connection": "Ethernet cables",
        "price": 15,
        "pros": ["Cheap", "5 ports", "Fanless", "Compact", "Plug and play"],
        "cons": ["Needs power adapter"],
        "best_for": ["security", "coding", "research"],
    },
    "usb_ethernet": {
        "name": "UGREEN USB 3.0 to Ethernet Adapter",
        "type": "USB Ethernet Adapter",
        "standard": "Gigabit Ethernet",
        "ports": "1x RJ45 GbE",
        "speed": "1000 Mbps",
        "connection": "USB 3.0",
        "price": 15,
        "pros": ["Adds Ethernet to Pi Zero", "USB-C and USB-A options", "No driver needed"],
        "cons": ["Single port"],
        "best_for": ["writerdeck", "conversation", "survival"],
    },
    "cat6_cable": {
        "name": "Cat 6 Ethernet Cable (1m/3m/5m)",
        "type": "Ethernet Cable",
        "standard": "Cat 6 UTP",
        "speed": "1 Gbps (up to 10 Gbps at 55m)",
        "length_options": ["1m", "3m", "5m", "10m"],
        "price_range": "$3-$8",
        "pros": ["Future-proof", "Shielded options available", "Flat and round"],
        "cons": ["Bulkier than Cat 5e"],
        "best_for": ["ALL"],
    },
    "cat6_flat": {
        "name": "Cat 6 Flat Ethernet Cable (1m)",
        "type": "Ethernet Cable",
        "standard": "Cat 6 UTP Flat",
        "speed": "1 Gbps",
        "length_options": ["1m", "2m", "3m"],
        "price_range": "$4-$8",
        "pros": ["Ultra thin", "Easy routing in enclosures", "Velcro tie included"],
        "cons": ["Less shielding"],
        "best_for": ["coding", "security", "gaming"],
    },
    "lora_module": {
        "name": "Seeed Studio Wio-SX1262 LoRa Module",
        "type": "LoRa Radio Module",
        "standard": "LoRa SX1262",
        "frequency": "868MHz / 915MHz",
        "range": "5-15km",
        "connection": "SPI + GPIO",
        "price": 20,
        "pros": ["Meshtastic compatible", "Long range", "Off-grid mesh networking", "Low power"],
        "cons": ["Needs antenna", "SPI wiring"],
        "best_for": ["survival", "research"],
    },
    "lte_modem": {
        "name": "Quectel EC20 LTE Cat 4 Modem",
        "type": "Cellular Modem",
        "standard": "4G LTE Cat 4",
        "speed": "150 Mbps DL / 50 Mbps UL",
        "connection": "USB + SIM slot",
        "price": 30,
        "pros": ["4G LTE connectivity", "GPS included", "AT command support", "Industrial grade"],
        "cons": ["Needs SIM card", "Antenna required"],
        "best_for": ["survival", "research", "security"],
    },
    "wifi_antenna_pigtail": {
        "name": "SMA Pigtail Cable (RP-SMA / SMA)",
        "type": "Antenna Cable",
        "connector": "RP-SMA to U.FL / SMA to U.FL",
        "length_options": ["10cm", "20cm", "30cm"],
        "price_range": "$2-$5",
        "pros": ["Internal WiFi to external antenna", "Clean build", "Various connectors"],
        "cons": ["Needs soldering or U.FL clip"],
        "best_for": ["security", "coding", "research"],
    },
}

# ============================================================
# COMPATIBILITY RULES
# ============================================================
COMPAT_RULES = {
    "power_connector": {
        "pi5": "USB-C 5V/5A",
        "pi4": "USB-C 5V/3A",
        "pi_zero_2w": "micro-USB 5V/2.5A",
        "orange_pi_5": "USB-C 5V/4A",
        "orange_pi_zero3": "USB-C 5V/2A",
        "jetson_orin_nano": "DC barrel 19V or USB-C",
        "lattepanda_3_delta": "USB-C 5V/3A",
        "cm4": "Depends on carrier",
        "cm5": "Depends on carrier",
    },
    "display_interface": {
        "pi5": ["hdmi", "dsi", "spi"],
        "pi4": ["hdmi", "dsi", "spi"],
        "pi_zero_2w": ["mini-hdmi", "spi", "i2c"],
        "orange_pi_5": ["hdmi", "usb-c-dp"],
        "jetson_orin_nano": ["hdmi", "dsi"],
        "lattepanda_3_delta": ["hdmi", "usb-c-dp"],
    },
}

# ============================================================
# WIRE SELECTION RULES (per gauge, per use)
# ============================================================
WIRE_RULES = {
    "signal": "silicon_26awg",
    "i2c_spi_uart": "silicon_26awg",
    "fan_power": "silicon_24awg",
    "led_strip": "silicon_24awg",
    "battery_low_current": "silicon_20awg",
    "main_power": "silicon_18awg",
    "solar_heavy": "silicon_16awg",
    "dsi_csi": "ribbon_cable",
    "quick_connect": "jst_connector_cable",
    "usb_power": "usb_c_cable",
    "led_neon": "silicon_26awg_neon",
}


# ============================================================
# LEARNER — persistent knowledge from videos & interactions
# ============================================================
class CyberdeckLearner:
    """Learns from videos, user chats, and build history. Evolves over time."""

    def __init__(self):
        self.file = LEARNINGS_FILE
        self.learnings = self._load()

    def _load(self) -> Dict:
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "video_knowledge": [],
                "tips_learned": [],
                "flaws_fixed": [],
                "user_preferences": {},
                "component_discoveries": [],
                "build_insights": [],
                "chat_learnings": [],
                "evolution_log": [],
            }

    def _save(self):
        try:
            with open(self.file, "w") as f:
                json.dump(self.learnings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save learnings: {e}")

    def learn_from_video(self, title: str, url: str, key_points: List[str], components: List[str], tips: List[str]):
        entry = {
            "title": title, "url": url,
            "key_points": key_points, "components": components, "tips": tips,
            "learned_at": datetime.now().isoformat(),
        }
        self.learnings["video_knowledge"].append(entry)
        for tip in tips:
            if tip not in self.learnings["tips_learned"]:
                self.learnings["tips_learned"].append(tip)
        for comp in components:
            if comp not in self.learnings["component_discoveries"]:
                self.learnings["component_discoveries"].append(comp)
        self._save()

    def learn_from_chat(self, user_message: str, bot_response: str, context: str = "general"):
        entry = {
            "user_message": user_message[:500],
            "bot_response": bot_response[:500],
            "context": context,
            "learned_at": datetime.now().isoformat(),
        }
        self.learnings["chat_learnings"].append(entry)
        if len(self.learnings["chat_learnings"]) > 500:
            self.learnings["chat_learnings"] = self.learnings["chat_learnings"][-500:]
        self._save()

    def learn_from_build(self, build: Dict):
        entry = {
            "build": build,
            "learned_at": datetime.now().isoformat(),
        }
        self.learnings["build_insights"].append(entry)
        self._save()

    def log_flaw_fix(self, flaw: str, fix: str):
        self.learnings["flaws_fixed"].append({
            "flaw": flaw, "fix": fix, "fixed_at": datetime.now().isoformat()
        })
        self._save()

    def log_evolution(self, what_changed: str):
        self.learnings["evolution_log"].append({
            "change": what_changed, "at": datetime.now().isoformat()
        })
        self._save()

    def get_all_tips(self) -> List[str]:
        return self.learnings.get("tips_learned", [])

    def get_all_components_discovered(self) -> List[str]:
        return self.learnings.get("component_discoveries", [])

    def get_user_preferences(self, user_id: str) -> Dict:
        return self.learnings.get("user_preferences", {}).get(str(user_id), {})

    def set_user_preference(self, user_id: str, key: str, value: Any):
        uid = str(user_id)
        if uid not in self.learnings.get("user_preferences", {}):
            self.learnings.setdefault("user_preferences", {})[uid] = {}
        self.learnings["user_preferences"][uid][key] = value
        self._save()

    def get_stats(self) -> Dict:
        return {
            "videos_learned": len(self.learnings.get("video_knowledge", [])),
            "tips_count": len(self.learnings.get("tips_learned", [])),
            "components_discovered": len(self.learnings.get("component_discoveries", [])),
            "flaws_fixed": len(self.learnings.get("flaws_fixed", [])),
            "build_insights": len(self.learnings.get("build_insights", [])),
            "chat_learnings": len(self.learnings.get("chat_learnings", [])),
            "evolution_entries": len(self.learnings.get("evolution_log", [])),
        }


# ============================================================
# COMPATIBILITY ENGINE
# ============================================================
class CompatibilityEngine:
    """Validates every component pair for compatibility."""

    @staticmethod
    def check_sbc_display(sbc_id: str, display_id: str) -> Dict:
        sbc = SBC_DATABASE.get(sbc_id)
        display = DISPLAY_DATABASE.get(display_id)
        if not sbc or not display:
            return {"compatible": False, "reason": "Unknown component"}
        sbc_name_lower = sbc["name"].lower()
        display_if = display.get("interface", "").lower()
        issues = []
        if "zero 2w" in sbc_name_lower or "orange pi zero3" in sbc_name_lower:
            if display_if in ["hdmi", "dsi"] and "mini" not in display_if and "spi" not in display_if and "i2c" not in display_if:
                issues.append(f"{sbc['name']} needs mini-HDMI or SPI/I2C display")
        if "jetson" in sbc_name_lower:
            if "eink" in display_id or "oled" in display_id:
                issues.append("Jetson works best with HDMI/DSI displays")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_sbc_power(sbc_id: str, power_id: str) -> Dict:
        sbc = SBC_DATABASE.get(sbc_id)
        power = POWER_DATABASE.get(power_id)
        if not sbc or not power:
            return {"compatible": False, "reason": "Unknown component"}
        issues = []
        sbc_power = sbc.get("power_draw", "")
        if "5V/5A" in sbc_power and "5A" not in power.get("output", ""):
            issues.append(f"{sbc['name']} needs 5V/5A but {power['name']} only outputs {power.get('output', '?')}")
        if "jetson" in sbc_id.lower() and power_id == "pisugar3_plus":
            issues.append("Jetson requires more power than PiSugar can provide")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_sbc_enclosure(sbc_id: str, enclosure_id: str) -> Dict:
        sbc = SBC_DATABASE.get(sbc_id)
        enclosure = ENCLOSURE_DATABASE.get(enclosure_id)
        if not sbc or not enclosure:
            return {"compatible": False, "reason": "Unknown component"}
        issues = []
        if "lattepanda" in sbc_id and "pelican" in enclosure_id:
            issues.append("LattePanda is larger; verify Pelican dimensions")
        if "jetson" in sbc_id and "pi_zero" in enclosure_id:
            issues.append("Jetson is too large for Pi Zero cases")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_full_build(components: Dict) -> Dict:
        all_issues = []
        sbc_id = components.get("sbc")
        display_id = components.get("display")
        power_id = components.get("power")
        enclosure_id = components.get("enclosure")
        if sbc_id and display_id:
            r = CompatibilityEngine.check_sbc_display(sbc_id, display_id)
            if not r["compatible"]:
                all_issues.extend(r.get("issues", []))
        if sbc_id and power_id:
            r = CompatibilityEngine.check_sbc_power(sbc_id, power_id)
            if not r["compatible"]:
                all_issues.extend(r.get("issues", []))
        if sbc_id and enclosure_id:
            r = CompatibilityEngine.check_sbc_enclosure(sbc_id, enclosure_id)
            if not r["compatible"]:
                all_issues.extend(r.get("issues", []))
        return {"compatible": len(all_issues) == 0, "issues": all_issues, "checked_at": datetime.now().isoformat()}

    @staticmethod
    def select_wire_for_use(use: str) -> Dict:
        wire_id = WIRE_RULES.get(use, "silicon_26awg")
        wire = WIRE_DATABASE.get(wire_id, WIRE_DATABASE["silicon_26awg"])
        return {"wire_id": wire_id, "wire": wire}


# ============================================================
# VIDEO QUEUE — background learning while user offline/online
# ============================================================
class VideoQueue:
    """Queues YouTube/TikTok URLs for background processing."""

    def __init__(self):
        self.file = VIDEO_QUEUE_FILE
        self.queue = self._load()

    def _load(self) -> List[Dict]:
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        try:
            with open(self.file, "w") as f:
                json.dump(self.queue, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save video queue: {e}")

    def add(self, url: str) -> Dict:
        entry = {
            "url": url,
            "status": "pending",
            "queued_at": datetime.now().isoformat(),
            "result": None,
        }
        self.queue.append(entry)
        self._save()
        return {"status": "queued", "url": url, "position": len(self.queue)}

    def process_pending(self, learner: CyberdeckLearner) -> List[Dict]:
        processed = []
        for entry in self.queue:
            if entry["status"] == "pending":
                try:
                    result = self._watch_and_learn(entry["url"], learner)
                    entry["status"] = "done"
                    entry["result"] = result
                    processed.append(result)
                except Exception as e:
                    entry["status"] = "failed"
                    entry["error"] = str(e)
        self._save()
        return processed

    def _watch_and_learn(self, url: str, learner: CyberdeckLearner) -> Dict:
        title = url.split("/")[-1][:80] if "/" in url else url[:80]
        key_points, components, tips = [], [], []
        try:
            import subprocess
            script = os.path.expanduser("~/.claude/skills/watch-video/scripts/watch.py")
            if os.path.exists(script):
                result = subprocess.run(
                    ["python", script, url],
                    capture_output=True, text=True, timeout=180,
                )
                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        ll = line.lower()
                        comp_kw = ["sbc", "raspberry pi", "zero 2w", "jetson", "orange pi", "lattepanda", "display", "screen", "keyboard", "battery", "enclosure", "pcb", "wire"]
                        if any(kw in ll for kw in comp_kw):
                            components.append(line[:150])
                        tip_kw = ["tip", "trick", "note", "warning", "important", "make sure", "don't forget", "always", "never"]
                        if any(kw in ll for kw in tip_kw):
                            tips.append(line[:250])
                        if len(key_points) < 15:
                            key_points.append(line[:250])
                    if title == url.split("/")[-1][:80]:
                        for line in result.stdout.strip().split("\n")[:5]:
                            if 5 < len(line) < 100:
                                title = line.strip()
                                break
        except Exception as e:
            logger.debug(f"Video queue watch fallback: {e}")
        learner.learn_from_video(title, url, key_points, components, tips)
        return {
            "title": title, "url": url,
            "key_points_count": len(key_points),
            "components_found": components[:15],
            "tips_found": tips[:15],
        }

    def get_pending_count(self) -> int:
        return len([e for e in self.queue if e["status"] == "pending"])


# ============================================================
# IMAGE ANALYZER — understand user-sent cyberdeck photos
# ============================================================
class ImageAnalyzer:
    """Analyzes cyberdeck images to identify components and suggest builds."""

    @staticmethod
    def analyze_from_description(description: str) -> Dict:
        desc_lower = description.lower()
        found = []
        for sid, sbc in SBC_DATABASE.items():
            if any(kw in desc_lower for kw in sbc["name"].lower().split()):
                found.append({"type": "SBC", "id": sid, "name": sbc["name"]})
        for did, display in DISPLAY_DATABASE.items():
            if any(kw in desc_lower for kw in display["name"].lower().split()):
                found.append({"type": "Display", "id": did, "name": display["name"]})
        for kid, kb in KEYBOARD_DATABASE.items():
            if any(kw in desc_lower for kw in kb["name"].lower().split()):
                found.append({"type": "Keyboard", "id": kid, "name": kb["name"]})
        for cid, cooler in COOLING_DATABASE.items():
            if any(kw in desc_lower for kw in cooler["name"].lower().split()):
                found.append({"type": "Cooling", "id": cid, "name": cooler["name"]})
        for pid, pcb in PCB_DATABASE.items():
            if any(kw in desc_lower for kw in pcb["name"].lower().split()):
                found.append({"type": "PCB", "id": pid, "name": pcb["name"]})
        for wid, wire in WIRE_DATABASE.items():
            if any(kw in desc_lower for kw in wire["name"].lower().split()):
                found.append({"type": "Wire", "id": wid, "name": wire["name"]})
        category = "coding"
        cat_keywords = {
            "writerdeck": ["writer", "writing", "typewriter", "e-ink", "distraction"],
            "security": ["security", "hack", "penetrat", "kali", "red team", "antenna"],
            "gaming": ["game", "retro", "arcade", "emulat", "controller"],
            "research": ["research", "field", "solar", "outdoor", "rugged"],
            "ai": ["ai", "machine learning", "neural", "inference", "jetson"],
            "survival": ["survival", "off-grid", "emergency", "solar", "lora"],
            "media": ["media", "movie", "music", "kodi", "stream"],
            "conversation": ["cyberpunk", "neon", "led", "prop", "cosplay", "aesthetic"],
        }
        for cat, keywords in cat_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                category = cat
                break
        return {
            "identified_components": found,
            "suggested_category": category,
            "component_count": len(found),
        }

    @staticmethod
    def analyze_with_ai(description: str) -> Dict:
        result = ImageAnalyzer.analyze_from_description(description)
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                prompt = (
                    f"Analyze this cyberdeck photo/description. Identify all visible components "
                    f"(SBC, display, keyboard, PCB, wires, enclosure, cooling). Suggest the best "
                    f"category, flag compatibility issues, and recommend upgrades.\n\n"
                    f"Description: {description}\n\n"
                    f"Respond in JSON: components(list), category(string), issues(list), "
                    f"upgrades(list), tips(list)"
                )
                response = provider.generate(prompt)
                result["ai_analysis"] = response
        except Exception as e:
            logger.debug(f"Image AI analysis fallback: {e}")
        return result


# ============================================================
# BUILD GENERATOR — creates complete cyberdeck builds
# ============================================================
class BuildGenerator:
    """Generates complete builds from prompts and categories."""

    @staticmethod
    def build_for_category(category: str, tier: str = "intermediate", custom_parts: Dict = None) -> Dict:
        cat = CATEGORIES.get(category, CATEGORIES["coding"])
        tier_config = TIERS.get(tier, TIERS["intermediate"])
        components = {
            "sbc": custom_parts.get("sbc") if custom_parts and custom_parts.get("sbc") else cat["best_sbc"],
            "display": custom_parts.get("display") if custom_parts and custom_parts.get("display") else cat["best_display"],
            "keyboard": custom_parts.get("keyboard") if custom_parts and custom_parts.get("keyboard") else cat["best_keyboard"],
            "power": custom_parts.get("power") if custom_parts and custom_parts.get("power") else cat["best_power"],
            "enclosure": custom_parts.get("enclosure") if custom_parts and custom_parts.get("enclosure") else cat["best_enclosure"],
            "cooling": custom_parts.get("cooling") if custom_parts and custom_parts.get("cooling") else cat["best_cooling"],
            "pcb": cat.get("pcb", "waveshare_phat"),
            "wire_signal": cat.get("wire_signal", "silicon_26awg"),
            "wire_power": cat.get("wire_power", "silicon_18awg"),
            "os": cat.get("best_os", "raspberry_pi_os"),
            "connectivity": custom_parts.get("connectivity") if custom_parts and custom_parts.get("connectivity") else cat.get("best_connectivity", "cat6_flat"),
        }
        if custom_parts:
            for k, v in custom_parts.items():
                if k not in ("sbc", "display", "keyboard", "power", "enclosure", "cooling") and v:
                    components[k] = v
        compat = CompatibilityEngine.check_full_build(components)
        if not compat["compatible"]:
            fixed = BuildGenerator._fix_flaws(components, compat["issues"], cat, tier)
            components = fixed
            compat = CompatibilityEngine.check_full_build(components)
        sbc_info = SBC_DATABASE.get(components["sbc"], {})
        display_info = DISPLAY_DATABASE.get(components["display"], {})
        kb_info = KEYBOARD_DATABASE.get(components["keyboard"], {})
        power_info = POWER_DATABASE.get(components["power"], {})
        enclosure_info = ENCLOSURE_DATABASE.get(components["enclosure"], {})
        cooling_info = COOLING_DATABASE.get(components["cooling"], {})
        pcb_info = PCB_DATABASE.get(components.get("pcb", ""), {})
        wire_signal = WIRE_DATABASE.get(components.get("wire_signal", "silicon_26awg"), WIRE_DATABASE["silicon_26awg"])
        wire_power = WIRE_DATABASE.get(components.get("wire_power", "silicon_18awg"), WIRE_DATABASE["silicon_18awg"])
        os_info = OS_DATABASE.get(components.get("os", "raspberry_pi_os"), {})
        connectivity_info = CONNECTIVITY_DATABASE.get(components.get("connectivity", "cat6_flat"), {})
        total_price = (
            sbc_info.get("price", 0) + display_info.get("price", 0) +
            power_info.get("price", 0) + enclosure_info.get("price", 0) +
            cooling_info.get("price", 0) + connectivity_info.get("price", 0)
        )
        return {
            "category": cat["name"],
            "category_id": category,
            "tier": tier_config["name"],
            "tier_id": tier,
            "components": {
                "sbc": {"id": components["sbc"], **sbc_info},
                "display": {"id": components["display"], **display_info},
                "keyboard": {"id": components["keyboard"], **kb_info},
                "power": {"id": components["power"], **power_info},
                "enclosure": {"id": components["enclosure"], **enclosure_info},
                "cooling": {"id": components["cooling"], **cooling_info},
                "pcb": {"id": components.get("pcb", ""), **pcb_info},
                "wire_signal": {"id": components.get("wire_signal", ""), **wire_signal},
                "wire_power": {"id": components.get("wire_power", ""), **wire_power},
                "os": {"id": components.get("os", ""), **os_info},
                "connectivity": {"id": components.get("connectivity", ""), **connectivity_info},
            },
            "compatibility": compat,
            "total_price_estimate": f"${total_price}",
            "aesthetic": cat.get("aesthetic", "Industrial"),
            "soldering_required": tier_config.get("soldering", "Optional"),
        }

    @staticmethod
    def build_from_prompt(prompt: str, tier: str = "intermediate") -> Dict:
        prompt_lower = prompt.lower()
        matched_category = "coding"
        best_score = 0
        cat_triggers = {
            "coding": ["code", "coding", "program", "develop", "terminal", "linux", "server", "git"],
            "writerdeck": ["write", "writing", "writer", "journal", "typewriter", "distraction", "e-ink"],
            "security": ["security", "hack", "pentest", "kali", "red team", "network", "antenna", "sdr"],
            "gaming": ["game", "gaming", "retro", "arcade", "emulator", "controller", "console"],
            "research": ["research", "field", "outdoor", "data collect", "offline", "rugged"],
            "ai": ["ai", "artificial intelligence", "machine learning", "neural", "llm", "inference", "jetson"],
            "survival": ["survival", "off-grid", "emergency", "disaster", "solar", "lora", "ham radio"],
            "media": ["media", "movie", "music", "kodi", "stream", "video player", "home theater"],
            "conversation": ["cyberpunk", "prop", "cosplay", "aesthetic", "neon", "led", "look cool"],
        }
        for cat, triggers in cat_triggers.items():
            score = sum(1 for t in triggers if t in prompt_lower)
            if score > best_score:
                best_score = score
                matched_category = cat
        custom_parts = {}
        if "two screen" in prompt_lower or "dual screen" in prompt_lower or "2 screen" in prompt_lower:
            custom_parts["second_display"] = True
        if "split keyboard" in prompt_lower or "corne" in prompt_lower:
            custom_parts["keyboard"] = "corne_split"
        if "vintage" in prompt_lower or "model m" in prompt_lower:
            custom_parts["keyboard"] = "vintage_keyboard"
        if "pelican" in prompt_lower:
            custom_parts["enclosure"] = "pelican_1450"
        if "e-ink" in prompt_lower or "eink" in prompt_lower:
            custom_parts["display"] = "eink_7inch"
        if "solar" in prompt_lower:
            custom_parts["power"] = "solar_panel_18w"
        if "jetson" in prompt_lower:
            custom_parts["sbc"] = "jetson_orin_nano"
        if "orange pi" in prompt_lower:
            custom_parts["sbc"] = "orange_pi_5"
        if "zero 2w" in prompt_lower or "pi zero" in prompt_lower:
            custom_parts["sbc"] = "pi_zero_2w"
        return BuildGenerator.build_for_category(matched_category, tier, custom_parts or None)

    @staticmethod
    def _fix_flaws(components: Dict, issues: List[str], cat: Dict, tier: str) -> Dict:
        fixed = dict(components)
        for issue in issues:
            issue_lower = issue.lower()
            if "5V/5A" in issue or "5v/5a" in issue_lower:
                if "ups_h5180" not in fixed.get("power", ""):
                    fixed["power"] = "ups_h5180"
            if "too large" in issue_lower or "larger" in issue_lower:
                fixed["enclosure"] = "pelican_1450"
            if "mini-hdmi" in issue_lower:
                if "spi" not in str(fixed.get("display", "")):
                    fixed["display"] = "eink_7inch"
            if "power" in issue_lower and "provide" in issue_lower:
                fixed["power"] = "ups_h5180"
        return fixed

    @staticmethod
    def generate_bom(build: Dict) -> str:
        lines = [
            f"# Bill of Materials — {build['category']} ({build['tier']})",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "| # | Component | Name | Price |",
            "|---|-----------|------|-------|",
        ]
        idx = 1
        for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "pcb", "wire_signal", "wire_power", "connectivity"]:
            comp = build["components"].get(key, {})
            if comp:
                name = comp.get("name", key)
                price = comp.get("price") or comp.get("price_range") or comp.get("price_per_meter", "—")
                lines.append(f"| {idx} | {key.replace('_', ' ').title()} | {name} | ${price} |")
                idx += 1
        lines.extend([
            "",
            f"**Estimated Total:** {build['total_price_estimate']}",
            "",
            "## Notes",
            f"- OS: {build['components'].get('os', {}).get('name', 'N/A')}",
            f"- Aesthetic: {build.get('aesthetic', 'Industrial')}",
            f"- Soldering: {build.get('soldering_required', 'Optional')}",
            f"- Compatibility: {'PASS' if build['compatibility']['compatible'] else 'ISSUES FOUND'}",
        ])
        if build["compatibility"]["issues"]:
            lines.append("")
            for issue in build["compatibility"]["issues"]:
                lines.append(f"- ⚠ {issue}")
        learned_tips = []
        try:
            learner = CyberdeckLearner()
            all_tips = learner.get_all_tips()
            for tip in all_tips[:5]:
                lines.append(f"- 💡 {tip}")
        except Exception:
            pass
        return "\n".join(lines)

    @staticmethod
    def generate_tutorial(build: Dict) -> str:
        cat = build.get("category_id", "coding")
        sbc = build["components"].get("sbc", {})
        display = build["components"].get("display", {})
        kb = build["components"].get("keyboard", {})
        enclosure = build["components"].get("enclosure", {})
        lines = [
            f"# Assembly Tutorial — {build['category']} Cyberdeck",
            f"Tier: {build['tier']} | SBC: {sbc.get('name', 'N/A')}",
            "",
            "## What You Need",
            "",
        ]
        for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "pcb", "connectivity"]:
            comp = build["components"].get(key, {})
            if comp:
                lines.append(f"- {comp.get('name', key)}")
        wire_s = build["components"].get("wire_signal", {})
        wire_p = build["components"].get("wire_power", {})
        if wire_s:
            lines.append(f"- Signal wire: {wire_s.get('name', '26AWG silicon')}")
        if wire_p:
            lines.append(f"- Power wire: {wire_p.get('name', '18AWG silicon')}")
        lines.extend([
            "",
            "## Step-by-Step Assembly",
            "",
            "### Step 1: Prepare the Enclosure",
            f"1. Unbox your {enclosure.get('name', 'enclosure')}.",
            "2. If using pick-and-pluck foam, remove foam cubes to match your SBC and display shapes.",
            "3. Test-fit the SBC and display in the enclosure before wiring.",
            "4. Mark drill points for mounting screws, fan holes, and connector ports.",
            "",
            "### Step 2: Mount the SBC",
            f"1. Place the {sbc.get('name', 'SBC')} in the enclosure.",
            "2. Secure with M2.5 standoffs and screws (4x).",
            "3. Ensure the GPIO header is accessible.",
            "4. Connect the cooling solution (fan/heatsink) to the SBC.",
            "",
            "### Step 3: Install the Display",
            f"1. Connect the {display.get('name', 'display')} to the SBC via HDMI/DSI/SPI.",
            "2. If touch-enabled, connect the USB touch cable to a USB port.",
            "3. Mount the display in the enclosure (screws or adhesive).",
            "4. Route the ribbon cable neatly along the enclosure wall.",
            "",
            "### Step 4: Connect the Keyboard",
            f"1. Connect the {kb.get('name', 'keyboard')} via USB-C or Bluetooth.",
            "2. If wired, route the cable through a cable management hole.",
            "3. Test typing before closing the enclosure.",
            "",
            "### Step 5: Wire the Power System",
            "1. Connect the power source (UPS HAT / power bank / battery) to the SBC.",
            "2. Use the correct wire gauge for power connections.",
            "3. If using a UPS HAT, install 18650 cells before connecting.",
            "4. Test power-on before proceeding.",
            "",
            "### Step 6: Connect Cooling",
            "1. Connect the fan to the 5V/GND pins on the GPIO header.",
            "2. If using PWM, connect the signal wire to a GPIO pin.",
            "3. Test fan spin at power-on.",
            "",
            "### Step 7: Final Assembly",
            "1. Route all cables neatly inside the enclosure.",
            "2. Ensure no cables are pinched or under stress.",
            "3. Close the enclosure and secure all screws.",
            "4. Power on and verify all components work.",
            "",
            "### Step 8: Software Setup",
            f"1. Flash {build['components'].get('os', {}).get('name', 'Raspberry Pi OS')} to the SD card.",
            "2. Boot and complete initial setup.",
            "3. Install any category-specific software (IDE, Kali tools, RetroPie, etc.).",
            "4. Test all hardware: display, keyboard, cooling, power management.",
            "",
            "### Step 9: Configure Connectivity",
            "1. If using WiFi adapter: plug into USB 3.0 port, install drivers.",
            "2. If using Ethernet: connect Cat6 cable to SBC Ethernet port.",
            "3. If using LoRa: connect module via SPI, install Meshtastic firmware.",
            "4. If using cellular modem: insert SIM, connect via USB.",
            "5. Test internet access: `ping 8.8.8.8`",
            "6. If external antenna: mount and route SMA cable through enclosure.",
            "",
            "## Tips",
        ])
        try:
            learner = CyberdeckLearner()
            for tip in learner.get_all_tips()[:5]:
                lines.append(f"- {tip}")
        except Exception:
            pass
        lines.extend([
            "",
            "## Troubleshooting",
            "- Display not showing: Check HDMI/DSI cable, try different port",
            "- Keyboard not working: Check USB connection, try different port",
            "- Fan not spinning: Check GPIO wiring, verify 5V/GND",
            "- Won't power on: Check battery/UPS charge, verify power cable",
            "- Overheating: Check thermal paste, ensure fan is connected",
        ])
        return "\n".join(lines)

    @staticmethod
    def suggest_upgrades(build: Dict) -> List[Dict]:
        upgrades = []
        sbc_id = build["components"].get("sbc", {}).get("id", "")
        display_id = build["components"].get("display", {}).get("id", "")
        upgrade_paths = {
            "pi4_8gb": {"next": "pi5_8gb", "reason": "2x faster CPU, NVMe support, WiFi 6"},
            "pi5_8gb": {"next": "pi5_16gb", "reason": "Double RAM for heavier workloads"},
            "pi5_4gb": {"next": "pi5_8gb", "reason": "Double RAM for multitasking"},
            "pi_zero_2w": {"next": "pi5_4gb", "reason": "Massive performance jump, full-size HDMI"},
            "orange_pi_zero3": {"next": "orange_pi_5", "reason": "Much faster, NVMe, more RAM"},
            "hdmi_5inch": {"next": "hdmi_7inch_ips", "reason": "Larger, better resolution"},
            "hdmi_7inch_ips": {"next": "hdmi_10inch", "reason": "Larger for better productivity"},
            "eink_4_2inch": {"next": "eink_7inch", "reason": "Larger, more readable"},
            "passive_heatsink": {"next": "active_fan", "reason": "Better cooling under load"},
        }
        if sbc_id in upgrade_paths:
            up = upgrade_paths[sbc_id]
            upgrades.append({"component": "SBC", "from": sbc_id, "to": up["next"], "reason": up["reason"]})
        if display_id in upgrade_paths:
            up = upgrade_paths[display_id]
            upgrades.append({"component": "Display", "from": display_id, "to": up["next"], "reason": up["reason"]})
        upgrades.append({"component": "Cooling", "from": "passive_heatsink", "to": "active_fan_heatsink", "reason": "Best cooling for sustained performance"})
        upgrades.append({"component": "Storage", "from": "SD card", "to": "NVMe SSD", "reason": "10x faster boot and I/O"})
        return upgrades

    @staticmethod
    def generate_ideas(category: str = None) -> List[Dict]:
        ideas = [
            {"title": "The Minimalist Writer", "category": "writerdeck", "description": "Pi Zero 2W + 4.2\" e-ink + Planck ortho. Ultra-portable distraction-free writing.", "difficulty": "beginner"},
            {"title": "The Field Hacker", "category": "security", "description": "Pi 5 16GB + 7\" touch + Kali + AWUS036ACH antenna + HackRF SDR.", "difficulty": "intermediate"},
            {"title": "The Retro Arcade", "category": "gaming", "description": "Pi 5 8GB + 7\" HDMI + RetroPie + USB controllers + Pelican case.", "difficulty": "beginner"},
            {"title": "The AI Terminal", "category": "ai", "description": "Jetson Orin Nano + 10\" HDMI + NVMe + active cooling + 40 TOPS.", "difficulty": "advanced"},
            {"title": "The Off-Grid Comms", "category": "survival", "description": "Pi 5 + e-ink + LoRa + ham radio + solar panel + 6x 18650 cells.", "difficulty": "advanced"},
            {"title": "The Dual-Screen Dev", "category": "coding", "description": "Pi 5 16GB + 7\" main + 5\" OLED status + Planck keyboard + NVMe.", "difficulty": "advanced"},
            {"title": "The Cinema Deck", "category": "media", "description": "Pi 5 + 10\" HDMI + speakers + wireless keyboard + LibreELEC.", "difficulty": "beginner"},
            {"title": "The Cyberpunk Prop", "category": "conversation", "description": "Zero 2W + OLED + neon LEDs + vintage briefcase + mechanical keyboard.", "difficulty": "intermediate"},
            {"title": "The Research Station", "category": "research", "description": "Pi 5 8GB + sunlight-readable 10\" + NVMe + 6x 18650 + offline Wikipedia.", "difficulty": "intermediate"},
            {"title": "The Recovery Kit", "category": "coding", "description": "Pi 5 + Pelican 1450 + 7\" touch + Planck + Ethernet switch + UPS HAT.", "difficulty": "advanced"},
            {"title": "The Penkesu Computer", "category": "writerdeck", "description": "Pi Zero 2W + 7.5\" e-ink + Corne split keyboard + GBA SP hinges.", "difficulty": "intermediate"},
            {"title": "The Chonky Palmtop", "category": "coding", "description": "Pi 5 + 7\" touch + Corne split on pivot + NVMe + active cooling.", "difficulty": "advanced"},
            {"title": "The Cyberdore 2064", "category": "conversation", "description": "Pi Zero + OLED 128x64 + rotary encoder + mechanical keys.", "difficulty": "beginner"},
            {"title": "The Tactical Wedge", "category": "security", "description": "Pi 5 + FDM-printed modular case + Kali + external antenna + GPIO switches.", "difficulty": "advanced"},
            {"title": "The Bumble Budget", "category": "gaming", "description": "Orange Pi Zero 3 + 5\" HDMI + RetroPie + budget enclosure.", "difficulty": "beginner"},
        ]
        if category:
            ideas = [i for i in ideas if i["category"] == category]
        return ideas

    @staticmethod
    def generate_code(request: str, language: str = "python") -> Dict[str, str]:
        templates = {
            "battery_monitor": {
                "python": "#!/usr/bin/env python3\nimport smbus2 as smbus\nimport time\n\nBUS = smbus.SMBus(1)\nADDR = 0x36\n\ndef read_voltage():\n    data = BUS.read_word_data(ADDR, 0x02)\n    return round((data & 0xFFFF) * 1.25 / 1000 / 16, 2)\n\ndef read_capacity():\n    data = BUS.read_word_data(ADDR, 0x04)\n    return round((data & 0xFFFF) * 256 / 10000, 1)\n\nif __name__ == '__main__':\n    while True:\n        print(f'Battery: {read_voltage()}V | {read_capacity()}%')\n        time.sleep(5)\n",
                "description": "Read battery voltage/capacity via I2C (UPS HAT)",
            },
            "temp_monitor": {
                "python": "#!/usr/bin/env python3\nimport time\n\ndef get_temp():\n    with open('/sys/class/thermal/thermal_zone0/temp') as f:\n        return round(float(f.read().strip()) / 1000, 1)\n\nif __name__ == '__main__':\n    while True:\n        t = get_temp()\n        fan = 'FULL' if t > 70 else 'HIGH' if t > 55 else 'MEDIUM' if t > 40 else 'LOW'\n        print(f'CPU: {t}C | Fan: {fan}')\n        time.sleep(10)\n",
                "description": "Monitor CPU temperature and control fan speed",
            },
            "led_status": {
                "python": "#!/usr/bin/env python3\nimport RPi.GPIO as GPIO\nimport time\n\nGPIO.setmode(GPIO.BCM)\nGPIO.setup(17, GPIO.OUT)\nGPIO.setup(27, GPIO.OUT)\nGPIO.output(17, GPIO.HIGH)\ntry:\n    while True:\n        GPIO.output(27, GPIO.HIGH)\n        time.sleep(0.5)\n        GPIO.output(27, GPIO.LOW)\n        time.sleep(0.5)\nexcept KeyboardInterrupt:\n    GPIO.cleanup()\n",
                "description": "Blink status LEDs via GPIO",
            },
            "low_battery_shutdown": {
                "python": "#!/usr/bin/env python3\nimport smbus2 as smbus\nimport subprocess, time\n\nBUS = smbus.SMBus(1)\nADDR = 0x36\n\ndef read_voltage():\n    data = BUS.read_word_data(ADDR, 0x02)\n    return round((data & 0xFFFF) * 1.25 / 1000 / 16, 2)\n\nif __name__ == '__main__':\n    while True:\n        v = read_voltage()\n        print(f'Battery: {v}V')\n        if v < 3.0:\n            print('Low battery! Shutting down...')\n            subprocess.run(['sudo', 'shutdown', '-h', 'now'])\n        time.sleep(60)\n",
                "description": "Auto-shutdown on low battery to protect SD card",
            },
        }
        req_lower = request.lower()
        for key, tmpl in templates.items():
            if key.replace("_", " ") in req_lower or key in req_lower:
                return {"code": tmpl[language], "description": tmpl["description"], "language": language}
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                resp = provider.generate(f"Write {language} code for: {request}\nProvide clean, commented code.")
                return {"code": resp, "description": f"AI-generated {language} code", "language": language}
        except Exception:
            pass
        return {"code": f"# TODO: Implement {request} in {language}", "description": "Template", "language": language}


# ============================================================
# MAIN AGENT
# ============================================================
class CyberdeckAgent:
    """Full-featured cyberdeck builder, learner, and evolution engine."""

    def __init__(self):
        self.version = VERSION
        self.learner = CyberdeckLearner()
        self.video_queue = VideoQueue()
        self.build_history = self._load_history()
        self.image_analyzer = ImageAnalyzer()
        self.generator = BuildGenerator()

    def _load_history(self) -> List[Dict]:
        try:
            with open(BUILD_HISTORY_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self):
        try:
            with open(BUILD_HISTORY_FILE, "w") as f:
                json.dump(self.build_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save build history: {e}")

    async def build(self, description: str, tier: str = "intermediate", custom_parts: Dict = None) -> Dict:
        build = self.generator.build_from_prompt(description, tier)
        if custom_parts:
            for k, v in custom_parts.items():
                if v and k in build["components"]:
                    build["components"][k] = v
            build["compatibility"] = CompatibilityEngine.check_full_build({
                k: v.get("id", v) if isinstance(v, dict) else v
                for k, v in build["components"].items()
                if k in ("sbc", "display", "keyboard", "power", "enclosure", "cooling")
            })
        build["bom"] = self.generator.generate_bom(build)
        build["tutorial"] = self.generator.generate_tutorial(build)
        build["upgrades"] = self.generator.suggest_upgrades(build)
        build["ideas"] = self.generator.generate_ideas(build.get("category_id"))
        self.build_history.append({
            "category": build.get("category_id"),
            "tier": tier,
            "sbc": build["components"]["sbc"]["id"],
            "timestamp": datetime.now().isoformat(),
        })
        self._save_history()
        self.learner.learn_from_build({"category": build.get("category_id"), "sbc": build["components"]["sbc"]["id"], "tier": tier})
        if not build["compatibility"]["compatible"]:
            for issue in build["compatibility"]["issues"]:
                self.learner.log_flaw_fix(issue, "Auto-fixed by compatibility engine")
        return build

    async def build_custom(self, name: str, description: str, tier: str = "intermediate") -> Dict:
        prompt = f"{name}: {description}"
        return await self.build(prompt, tier)

    async def pick(self, component_type: str, category: str = "coding") -> Dict:
        cat = CATEGORIES.get(category, CATEGORIES["coding"])
        type_map = {
            "sbc": ("best_sbc", SBC_DATABASE),
            "display": ("best_display", DISPLAY_DATABASE),
            "keyboard": ("best_keyboard", KEYBOARD_DATABASE),
            "power": ("best_power", POWER_DATABASE),
            "enclosure": ("best_enclosure", ENCLOSURE_DATABASE),
            "cooling": ("best_cooling", COOLING_DATABASE),
            "pcb": ("pcb", PCB_DATABASE),
            "wire_signal": ("wire_signal", WIRE_DATABASE),
            "wire_power": ("wire_power", WIRE_DATABASE),
            "os": ("best_os", OS_DATABASE),
            "connectivity": ("best_connectivity", CONNECTIVITY_DATABASE),
        }
        if component_type not in type_map:
            return {"error": f"Unknown type: {component_type}. Use: {', '.join(type_map.keys())}"}
        field, database = type_map[component_type]
        best_id = cat.get(field, "")
        item = database.get(best_id, {})
        return {"type": component_type, "category": category, "id": best_id, "item": item}

    async def check_compatibility(self, sbc_id: str, display_id: str = None, power_id: str = None, enclosure_id: str = None) -> Dict:
        components = {"sbc": sbc_id}
        if display_id:
            components["display"] = display_id
        if power_id:
            components["power"] = power_id
        if enclosure_id:
            components["enclosure"] = enclosure_id
        return CompatibilityEngine.check_full_build(components)

    async def analyze_image(self, image_description: str) -> Dict:
        result = self.image_analyzer.analyze_with_ai(image_description)
        result["suggested_build"] = await self.build(
            f"Recreate a {result.get('suggested_category', 'coding')} cyberdeck with these components",
            "intermediate",
        )
        return result

    async def watch_video(self, url: str) -> Dict:
        return self.video_queue._watch_and_learn(url, self.learner)

    async def queue_video(self, url: str) -> Dict:
        return self.video_queue.add(url)

    async def process_queue(self) -> Dict:
        results = self.video_queue.process_pending(self.learner)
        return {"processed": len(results), "results": results}

    async def generate_ideas(self, category: str = None) -> List[Dict]:
        return self.generator.generate_ideas(category)

    async def generate_code(self, request: str, language: str = "python") -> Dict:
        return self.generator.generate_code(request, language)

    async def upgrade(self, build: Dict) -> List[Dict]:
        return self.generator.suggest_upgrades(build)

    async def fix_flaws(self, components: Dict, category: str = "coding", tier: str = "intermediate") -> Dict:
        compat = CompatibilityEngine.check_full_build(components)
        if compat["compatible"]:
            return {"status": "already_compatible", "components": components, "compatibility": compat}
        cat = CATEGORIES.get(category, CATEGORIES["coding"])
        fixed = self.generator._fix_flaws(components, compat["issues"], cat, tier)
        new_compat = CompatibilityEngine.check_full_build(fixed)
        return {"status": "fixed", "original_issues": compat["issues"], "components": fixed, "compatibility": new_compat}

    async def search_parts(self, query: str) -> Dict:
        results = {"query": query, "suggestions": [], "sources": ["Amazon", "Adafruit", "Pimoroni", "PiShop.us", "CanaKit", "AliExpress"]}
        ql = query.lower()
        for sid, sbc in SBC_DATABASE.items():
            if any(kw in sbc["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "SBC", "name": sbc["name"], "price": sbc["price"], "id": sid})
        for did, display in DISPLAY_DATABASE.items():
            if any(kw in display["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "Display", "name": display["name"], "price": display["price"], "id": did})
        for kid, kb in KEYBOARD_DATABASE.items():
            if any(kw in kb["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "Keyboard", "name": kb["name"], "price_range": kb["price_range"], "id": kid})
        for pid, pcb in PCB_DATABASE.items():
            if any(kw in pcb["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "PCB", "name": pcb["name"], "price_range": pcb["price_range"], "id": pid})
        for wid, wire in WIRE_DATABASE.items():
            if any(kw in wire["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "Wire", "name": wire["name"], "price_per_meter": wire["price_per_meter"], "id": wid})
        return results

    def get_status(self) -> Dict:
        return {
            "version": self.version,
            "total_builds": len(self.build_history),
            "videos_learned": len(self.learner.learnings.get("video_knowledge", [])),
            "tips_count": len(self.learner.learnings.get("tips_learned", [])),
            "flaws_fixed": len(self.learner.learnings.get("flaws_fixed", [])),
            "categories": list(CATEGORIES.keys()),
            "tiers": list(TIERS.keys()),
            "sbc_count": len(SBC_DATABASE),
            "display_count": len(DISPLAY_DATABASE),
            "keyboard_count": len(KEYBOARD_DATABASE),
            "power_count": len(POWER_DATABASE),
            "enclosure_count": len(ENCLOSURE_DATABASE),
            "cooling_count": len(COOLING_DATABASE),
            "pcb_count": len(PCB_DATABASE),
            "wire_count": len(WIRE_DATABASE),
            "connectivity_count": len(CONNECTIVITY_DATABASE),
            "os_count": len(OS_DATABASE),
            "video_queue_pending": self.video_queue.get_pending_count(),
        }

    def get_categories(self) -> Dict:
        return {k: {"name": v["name"], "description": v["description"], "budget_range": v["budget_range"]} for k, v in CATEGORIES.items()}


# ============================================================
# SINGLETON
# ============================================================
_agent_instance = None

def get_cyberdeck_agent() -> CyberdeckAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CyberdeckAgent()
    return _agent_instance
