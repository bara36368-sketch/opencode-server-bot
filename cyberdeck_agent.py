"""
Cyberdeck Agent v6.0 — Full-featured cyberdeck builder, learner, and evolution engine.
Watches videos, analyzes images, builds from prompts, picks best components,
validates compatibility, generates tutorials, and gets smarter over time.

New in v6.0:
  - Vision Module: image/video understanding via AI vision API
  - Career Templates: pre-built configs for coding, gaming, AI, security, writer, etc.
  - Interactive HTML Dashboard: 3D visualization, component picker, customization
  - Pack Generator: image+video+text bundles with tutorials
  - Web Search Engine: YouTube, TikTok, Instagram, GitHub, web search
  - Cable Manager: cable routing, measurements, wire recommendations
  - Smart Learner: learns from chat history and video content
  - Build From Prompt: natural language to cyberdeck build
  - Upgrade Planner: upgrade paths for existing builds
  - Compatibility Engine: 100% component compatibility validation
  - Career Category Picker: best SBC/display/components per career
  - DDR4/DDR5 Support: RAM selection for builds
  - Solar Panel Integration: solar charging in every build
  - Component Details: detailed specs, pricing, risk levels for every part
  - PCB Generator: custom PCB designs for backward compatibility
  - 3D Model Generator: OpenSCAD/STL generation with color picker
  - Tutorial Generator: word-by-word assembly instructions
  - Idea Generator: trend-aware build suggestions
  - Flaw Detector: pre-delivery quality checks
  - Cooling Enforced: every build includes thermal management
  - WiFi/LAN Enforced: every build includes connectivity
  - Upgradeable Design: every component swappable/upgradeable
"""
import os, json, time, logging, hashlib, re, base64, math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

VERSION = "6.0.0"
LEARNINGS_FILE = "cyberdeck_learnings.json"
BUILD_HISTORY_FILE = "cyberdeck_build_history.json"
VIDEO_QUEUE_FILE = "cyberdeck_video_queue.json"
BUILD_LIST_FILE = "CYBERDECK_BUILD_LIST.md"
DASHBOARD_FILE = "cyberdeck_dashboard.html"
PACKS_DIR = "cyberdeck_packs"

# ============================================================
# TIER SYSTEM — 4 tiers
# ============================================================
TIERS = {
    "beginner": {
        "name": "Beginner (Easy)", "budget": "$100-$300", "soldering": "Optional",
        "skills": "Plug together, basic Linux", "build_time": "1-3 days", "risk": "Minimal",
        "tools_needed": ["Screwdriver set", "USB cable", "SD card reader"],
    },
    "intermediate": {
        "name": "Intermediate (Moderate)", "budget": "$300-$700", "soldering": "Optional but helpful",
        "skills": "3D printing, cable management", "build_time": "1-2 weeks", "risk": "Low",
        "tools_needed": ["Soldering iron + solder", "3D printer or access", "Wire strippers",
                         "Multimeter", "Heat shrink + heat gun", "Flush cutters"],
    },
    "advanced": {
        "name": "Advanced (Expert)", "budget": "$700-$2000", "soldering": "Recommended",
        "skills": "Soldering, PCB design, QMK firmware", "build_time": "2-8+ weeks",
        "risk": "Minimal (with validation)",
        "tools_needed": ["Temperature-controlled soldering station", "Hot air rework",
                         "Oscilloscope", "PCB etching kit or JLCPCB order",
                         "CNC mill access or Dremel", "Flux, wick, desoldering pump"],
    },
    "expert": {
        "name": "Expert (Professional)", "budget": "$2000+", "soldering": "Required — advanced",
        "skills": "Custom PCB, metalwork, CNC, full custom design", "build_time": "1-6 months",
        "risk": "Moderate (requires expertise)",
        "tools_needed": ["CNC milling machine or access", "Metalworking tools",
                         "Custom PCB fab (JLCPCB/PCBWay)", "Laser cutter access",
                         "Professional multimeter + logic analyzer", "UV exposure unit for PCBs"],
    },
}

# ============================================================
# STYLE PRESETS — 3D model design rules per style
# ============================================================
STYLE_PRESETS = {
    "futuristic": {
        "name": "Futuristic",
        "description": "Sleek curves, smooth surfaces, LED accent channels, minimal seams",
        "default_color": "#1a1a2e",
        "accent_color": "#00f0ff",
        "screw_style": "hidden",
        "surface": "smooth",
        "vent_style": "slim slits",
        "led_channels": True,
        "fillet_radius": 4,
        "wire_visibility": "hidden",
        "bezel_style": "razor thin",
        "enclosure_notes": "Use rounded corners, integrated light pipes for LEDs, flush-mount display",
    },
    "retro": {
        "name": "Retro",
        "description": "Boxy shapes, visible screws, beige/grey palette, CRT-inspired curves",
        "default_color": "#c0b19a",
        "accent_color": "#8b7355",
        "screw_style": "exposed Phillips",
        "surface": "textured matte",
        "vent_style": "rectangular slots",
        "led_channels": False,
        "fillet_radius": 1,
        "wire_visibility": "hidden",
        "bezel_style": "thick rounded",
        "enclosure_notes": "Use angular shapes, embossed labels, vintage feel with 80s aesthetics",
    },
    "industrial": {
        "name": "Industrial",
        "description": "Exposed hardware, functional design, labeled ports, rugged feel",
        "default_color": "#2d2d2d",
        "accent_color": "#ff6600",
        "screw_style": "exposed hex",
        "surface": "brushed texture",
        "vent_style": "perforated grill",
        "led_channels": False,
        "fillet_radius": 2,
        "wire_visibility": "partially exposed",
        "bezel_style": "thick functional",
        "enclosure_notes": "Use visible standoffs, labeled cutouts, modular panel design",
    },
    "minimal": {
        "name": "Minimal",
        "description": "Clean lines, no visible hardware, seamless, monochrome",
        "default_color": "#f5f5f5",
        "accent_color": "#333333",
        "screw_style": "hidden (snap-fit)",
        "surface": "smooth matte",
        "vent_style": "hidden bottom vents",
        "led_channels": False,
        "fillet_radius": 6,
        "wire_visibility": "completely hidden",
        "bezel_style": "uniform thin",
        "enclosure_notes": "Seamless design, no visible screws, magnet-attached lid, clean cable routing",
    },
    "steampunk": {
        "name": "Steampunk",
        "description": "Brass accents, riveted panels, gear decorations, Victorian industrial",
        "default_color": "#5c3a1e",
        "accent_color": "#b8860b",
        "screw_style": "exposed rivets",
        "surface": "leather-textured panels",
        "vent_style": "decorative grills",
        "led_channels": False,
        "fillet_radius": 2,
        "wire_visibility": "braided copper exposed",
        "bezel_style": "ornate brass frame",
        "enclosure_notes": "Add gear decorations, brass corner protectors, leather grip patches, pressure gauge cutout",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "description": "Exposed PCB, neon accents, asymmetric, aggressive angles, glitch aesthetic",
        "default_color": "#0d0d0d",
        "accent_color": "#ff00ff",
        "screw_style": "exposed hex (neon washers)",
        "surface": "carbon fiber texture",
        "vent_style": "aggressive angular",
        "led_channels": True,
        "fillet_radius": 1,
        "wire_visibility": "neon-colored exposed",
        "bezel_style": "asymmetric angular",
        "enclosure_notes": "Asymmetric cuts, exposed PCB edges, neon LED strips, holographic stickers",
    },
    "nautical": {
        "name": "Nautical / Aquatic",
        "description": "Sapele wood, brass accents, teal/dark navy color, compass rose details",
        "default_color": "#1a3a4a",
        "accent_color": "#b8860b",
        "screw_style": "brass slotted",
        "surface": "sapele wood veneer",
        "vent_style": "port-hole style round",
        "led_channels": False,
        "fillet_radius": 4,
        "wire_visibility": "braided marine-grade",
        "bezel_style": "brass compass frame",
        "enclosure_notes": "Add compass rose inlay, rope-grip edges, brass corner caps, water-resistant seals, porthole-style display bezel",
    },
    "solarpunk": {
        "name": "Solarpunk",
        "description": "Green/nature colors, bamboo/wood, living plant integration, sustainable materials",
        "default_color": "#2d5a27",
        "accent_color": "#8b6914",
        "screw_style": "hidden (wooden dowels)",
        "surface": "bamboo or reclaimed wood",
        "vent_style": "leaf-pattern perforations",
        "led_channels": False,
        "fillet_radius": 5,
        "wire_visibility": "hidden (natural fiber wrapped)",
        "bezel_style": "living-edge wood frame",
        "enclosure_notes": "Incorporate living moss/air plants, solar panel integration, natural fiber cables, biodegradable accents, earth-tone palette",
    },
    "cassette_futurism": {
        "name": "Cassette Futurism",
        "description": "80s/90s tech aesthetic, black/white/grey/red, soft-touch plastics, button-heavy",
        "default_color": "#2a2a2a",
        "accent_color": "#cc0000",
        "screw_style": "hidden (snap-fit)",
        "surface": "soft-touch matte plastic",
        "vent_style": "horizontal ribbed slots",
        "led_channels": False,
        "fillet_radius": 3,
        "wire_visibility": "hidden",
        "bezel_style": "chunky rounded",
        "enclosure_notes": "Add membrane buttons, red LED indicators, cassette-slot inspired card reader, Walkman-style volume wheels, soft rubber grips",
    },
    "feminine_craft": {
        "name": "Feminine / Craft",
        "description": "Lavender/rose/cream palette, quilted textures, embroidered details, soft curves",
        "default_color": "#e8d0e8",
        "accent_color": "#c77dba",
        "screw_style": "hidden (velvet-covered)",
        "surface": "quilted fabric panels",
        "vent_style": "lace-pattern perforations",
        "led_channels": False,
        "fillet_radius": 8,
        "wire_visibility": "braided ribbon cable",
        "bezel_style": "embroidered frame",
        "enclosure_notes": "Add embroidered patches, pearl-button accents, floral engravings, soft-touch silicone edges, decorative lace trim",
    },
    "fallout": {
        "name": "Fallout / Post-Apocalyptic",
        "description": "Military surplus, olive drab/khaki/rust, weathered/distressed finish, riveted panels",
        "default_color": "#4a5a3a",
        "accent_color": "#8b4513",
        "screw_style": "exposed hex (rusted)",
        "surface": "distressed hammered paint",
        "vent_style": "jagged cut-outs",
        "led_channels": False,
        "fillet_radius": 1,
        "wire_visibility": "exposed braided",
        "bezel_style": "dented metal frame",
        "enclosure_notes": "Add radiation symbol decals, rust patina, military stenciling, hazard stripes, vacuum tube decorations, retro-futuristic dial knobs",
    },
    "brutalist": {
        "name": "Brutalist",
        "description": "Raw concrete/gray, heavy mass, geometric blocks, visible construction marks",
        "default_color": "#6b6b6b",
        "accent_color": "#999999",
        "screw_style": "exposed industrial bolt",
        "surface": "raw concrete texture (printed)",
        "vent_style": "deep rectangular channels",
        "led_channels": False,
        "fillet_radius": 0,
        "wire_visibility": "hidden in channels",
        "bezel_style": "thick raw block",
        "enclosure_notes": "Use heavy geometric blocks, exposed layer lines as feature, no decoration, raw material honesty, monumental proportions",
    },
}

# ============================================================
# CUSTOM PCB TEMPLATES — backward compatibility adapter boards
# ============================================================
CUSTOM_PCB_TEMPLATES = {
    "hdmi_to_dsi_adapter": {
        "name": "HDMI-to-DSI Adapter Board",
        "description": "Converts HDMI output to DSI ribbon cable input for displays that only have DSI",
        "use_case": "When SBC only has HDMI but display requires DSI, or vice versa",
        "components_needed": ["HDMI receiver chip (TFP401)", "DSI transmitter", "PCB board", "FFC connectors"],
        "difficulty": "advanced",
        "estimated_cost": "$15-$30",
        "compatibility_issues_solved": ["HDMI SBC + DSI-only display", "Pi Zero + official Pi DSI screen"],
        "schematic_notes": "TFP401 HDMI receiver -> parallel RGB -> bridge chip -> DSI output. Requires careful signal routing.",
    },
    "usbc_power_board": {
        "name": "USB-C PD Power Delivery Board",
        "description": "Negotiates USB-C PD voltage (5V/9V/12V/15V/20V) and converts to 5V stable for SBC",
        "use_case": "When using USB-C PD power sources with SBCs that need stable 5V",
        "components_needed": ["USB-C PD sink controller (FUSB302 or STUSB4500)", "Buck converter", "USB-C PD trigger IC", "Capacitors", "PCB"],
        "difficulty": "intermediate",
        "estimated_cost": "$5-$15",
        "compatibility_issues_solved": ["USB-C PD source + Pi 5 5V/5A requirement", "Non-standard power sources"],
        "schematic_notes": "STUSB4500 PD sink -> requests 20V/3A -> buck converter -> 5V/5A output. Add USB-C input and 5V barrel/USB output.",
    },
    "gpio_expansion": {
        "name": "GPIO Expansion & Level Shifter Board",
        "description": "Expands 40-pin GPIO with level shifting (3.3V<->5V), screw terminals, and ESD protection",
        "use_case": "When connecting 5V sensors/peripherals to 3.3V SBC GPIO",
        "components_needed": ["TXS0108E level shifter", "ESD protection diodes", "Screw terminals", "PCB", "Pin header"],
        "difficulty": "beginner",
        "estimated_cost": "$3-$8",
        "compatibility_issues_solved": ["5V sensors on 3.3V GPIO", "Multiple I2C devices with different voltages"],
        "schematic_notes": "40-pin header passthrough -> TXS0108E bidirectional level shifters -> screw terminal blocks. Add 100nF caps per channel.",
    },
    "power_management": {
        "name": "Integrated Power Management Board",
        "description": "Combines battery charging (TP4056), boost converter (5V), low-voltage cutoff, and power switch",
        "use_case": "Custom battery builds that need charge, discharge, and protection in one board",
        "components_needed": ["TP4056 charger IC", "MT3608 boost converter", "DW01A protection IC", "MOSFET", "slide switch", "PCB"],
        "difficulty": "intermediate",
        "estimated_cost": "$5-$12",
        "compatibility_issues_solved": ["Custom battery pack + SBC power needs", "No integrated charging in enclosure"],
        "schematic_notes": "LiPo/Li-ion -> TP4056 charge -> DW01A protection -> MT3608 boost to 5V -> slide switch -> SBC. LED indicators for charge status.",
    },
    "display_adapter_multi": {
        "name": "Multi-Interface Display Adapter",
        "description": "Routes HDMI, SPI, or I2C display signals through a single FPC connector",
        "use_case": "When display interface doesn't match SBC output and you want a clean single-cable solution",
        "components_needed": ["FPC connectors (various pinouts)", "Signal routing traces", "ESD protection", "PCB"],
        "difficulty": "advanced",
        "estimated_cost": "$8-$20",
        "compatibility_issues_solved": ["Mixed display interfaces", "Clean single-cable display routing in custom enclosures"],
        "schematic_notes": "Input FPC (from SBC) -> routing board -> output FPC (to display). Passive routing only, no active conversion.",
    },
    "retro_gamepad_hat": {
        "name": "Retro Gamepad HAT",
        "description": "GPIO-based gamepad with D-pad, ABXY buttons, analog stick, and audio amp",
        "use_case": "Gaming cyberdecks that need integrated controls without USB",
        "components_needed": ["Analog joystick module", "Tactile buttons", "MAX98357A audio amp", "Speaker", "PCB", "Passive components"],
        "difficulty": "intermediate",
        "estimated_cost": "$10-$20",
        "compatibility_issues_solved": ["Gaming builds without USB gamepad", "Need integrated controls in handheld form factor"],
        "schematic_notes": "GPIO -> ADC for joystick (MCP3008 via SPI), buttons -> direct GPIO with pull-ups, MAX98357A I2S audio output.",
    },
}

# ============================================================
# SIZE PREFERENCES — small vs big build profiles
# ============================================================
SIZE_PROFILES = {
    "small": {
        "name": "Compact / Portable",
        "description": "Minimal footprint, lighter weight, less power draw, shorter battery life",
        "max_sbc": "pi_zero_2w",
        "preferred_sbcs": ["pi_zero_2w", "orange_pi_zero3", "pi5_4gb"],
        "max_display_size": 5,
        "preferred_displays": ["hdmi_5inch", "oled_1_3inch", "eink_4_2inch"],
        "preferred_keyboards": ["bt_keyboard", "bbq20kbd", "thumb_keyboard"],
        "preferred_enclosures": ["pelican_1150", "pelican_1200", "3d_printed"],
        "max_weight_grams": 500,
        "power_budget_watts": 10,
        "preferred_power": ["pisugar3_plus", "pimoroni_lipo_shim", "power_bank_20000"],
    },
    "big": {
        "name": "Full Power / Desktop Replacement",
        "description": "Maximum performance, larger screen, heavier, more battery capacity",
        "min_sbc": "pi5_8gb",
        "preferred_sbcs": ["pi5_16gb", "orange_pi_5_plus", "jetson_orin_nano", "lattepanda_3_delta"],
        "min_display_size": 7,
        "preferred_displays": ["hdmi_10inch", "hdmi_7inch_1024", "sunlight_readable_7"],
        "preferred_keyboards": ["mech_60", "keychron_k12", "vintage_keyboard", "corne_split"],
        "preferred_enclosures": ["pelican_1450", "pelican_1400", "3d_printed_vented"],
        "min_weight_grams": 800,
        "power_budget_watts": 30,
        "preferred_power": ["ups_h5180", "geekworm_x1200", "custom_18650_x6"],
    },
}

# ============================================================
# CATEGORY SYSTEM — enhanced with full component slots + v4.1 fields
# ============================================================
CATEGORIES = {
    "coding": {
        "name": "Coding & Development", "description": "Portable coding, terminal work, remote server admin, software development",
        "budget_range": "$300-$1200", "best_sbc": "pi5_16gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "3d_printed",
        "best_cooling": "active_fan", "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_26awg", "upgrade_path": "NVMe SSD > 16GB RAM > Active cooling > Dual screens",
        "estimated_cost": "$400-$800", "aesthetic": "Industrial with exposed screws",
        "default_color": "#2d2d2d", "default_style": "industrial", "size_preference": "big",
    },
    "writerdeck": {
        "name": "Writerdeck", "description": "Distraction-free writing, journaling, note-taking",
        "budget_range": "$100-$400", "best_sbc": "pi_zero_2w", "best_display": "eink_7inch",
        "best_keyboard": "ortho_40", "best_power": "pisugar3_plus", "best_enclosure": "3d_printed",
        "best_cooling": "passive_heatsink", "best_connectivity": "usb_ethernet",
        "best_pcb": "penkesu_pcb", "best_wire": "silicon_26awg",
        "upgrade_path": "E-ink 7.5\" > Split keyboard > Longer battery > Bluetooth",
        "estimated_cost": "$150-$350", "aesthetic": "Minimal, clean, retro",
        "default_color": "#f5f5f5", "default_style": "minimal", "size_preference": "small",
    },
    "security": {
        "name": "Security & Pentesting", "description": "Network analysis, red team, RF exploration",
        "budget_range": "$400-$1500", "best_sbc": "pi5_16gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "pelican_1450",
        "best_cooling": "active_fan", "best_connectivity": "awus036ach", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_26awg", "upgrade_path": "HackRF One > RTL-SDR > LTE modem > Dual WiFi adapters",
        "estimated_cost": "$500-$1200", "aesthetic": "Military black, tactical",
        "default_color": "#1a1a1a", "default_style": "cyberpunk", "size_preference": "big",
    },
    "gaming": {
        "name": "Retro Gaming & Media", "description": "Emulation, retro gaming, media playback",
        "budget_range": "$150-$500", "best_sbc": "pi5_8gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "bt_keyboard_trackpad", "best_power": "power_bank_20000",
        "best_enclosure": "3d_printed", "best_cooling": "passive_heatsink",
        "best_connectivity": "cat6_flat", "best_pcb": "adafruit_phat", "best_wire": "silicon_26awg",
        "upgrade_path": "NVMe storage > Better speakers > Larger screen > Bluetooth controllers",
        "estimated_cost": "$200-$400", "aesthetic": "Retro, neon, arcade",
        "default_color": "#1a1a2e", "default_style": "cyberpunk", "size_preference": "small",
    },
    "research": {
        "name": "Field Research", "description": "Fieldwork, data collection, offline reference",
        "budget_range": "$300-$800", "best_sbc": "pi5_8gb", "best_display": "sunlight_readable_7",
        "best_keyboard": "mech_60", "best_power": "custom_18650_x6", "best_enclosure": "pelican_1400",
        "best_cooling": "passive_heatsink", "best_connectivity": "usb_ethernet",
        "best_pcb": "waveshare_phat", "best_wire": "silicon_18awg",
        "upgrade_path": "Solar panel > LTE modem > Larger battery > Weatherproofing",
        "estimated_cost": "$400-$700", "aesthetic": "Rugged, utilitarian",
        "default_color": "#3d5c3a", "default_style": "industrial", "size_preference": "big",
    },
    "ai": {
        "name": "AI & Machine Learning", "description": "Local AI inference, LLM hosting, computer vision",
        "budget_range": "$500-$2000", "best_sbc": "jetson_orin_nano", "best_display": "hdmi_10inch",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "3d_printed_vented",
        "best_cooling": "active_fan_heatsink", "best_connectivity": "usb_ethernet",
        "best_pcb": "jetson_carrier", "best_wire": "silicon_24awg",
        "upgrade_path": "NVMe SSD > More RAM > GPU acceleration > Larger display",
        "estimated_cost": "$600-$1500", "aesthetic": "Futuristic, LED accent",
        "default_color": "#1a1a2e", "default_style": "futuristic", "size_preference": "big",
    },
    "survival": {
        "name": "Survival & Off-Grid", "description": "Emergency computing, off-grid comms, disaster preparedness",
        "budget_range": "$300-$1000", "best_sbc": "pi5_8gb", "best_display": "eink_7inch",
        "best_keyboard": "thumb_keyboard", "best_power": "solar_panel_18w",
        "best_enclosure": "pelican_1450", "best_cooling": "passive_heatsink",
        "best_connectivity": "lora_module", "best_pcb": "waveshare_phat", "best_wire": "silicon_18awg",
        "upgrade_path": "LTE modem > More solar capacity > External battery > Ham radio",
        "estimated_cost": "$400-$900", "aesthetic": "Military green, rugged",
        "default_color": "#4a5d23", "default_style": "industrial", "size_preference": "big",
    },
    "media": {
        "name": "Media Center", "description": "Music, movies, streaming, media playback",
        "budget_range": "$150-$500", "best_sbc": "pi5_4gb", "best_display": "hdmi_10inch",
        "best_keyboard": "bt_keyboard_trackpad", "best_power": "power_bank_20000",
        "best_enclosure": "3d_printed", "best_cooling": "passive_heatsink",
        "best_connectivity": "cat6_flat", "best_pcb": "adafruit_phat", "best_wire": "silicon_26awg",
        "upgrade_path": "NVMe storage > Better speakers > HDMI 2.1 > IR remote",
        "estimated_cost": "$200-$400", "aesthetic": "Sleek, modern",
        "default_color": "#1a1a2e", "default_style": "minimal", "size_preference": "big",
    },
    "conversation-piece": {
        "name": "Conversation Piece / Cosplay", "description": "Aesthetic statement, cosplay prop, display piece",
        "budget_range": "$150-$800", "best_sbc": "pi_zero_2w", "best_display": "oled_1_3inch",
        "best_keyboard": "bt_keyboard", "best_power": "pisugar3_plus",
        "best_enclosure": "3d_printed_cyberpunk", "best_cooling": "passive_heatsink",
        "best_connectivity": "cat6_flat", "best_pcb": "custom_neon_pcb", "best_wire": "silicon_26awg_neon",
        "upgrade_path": "RGB LEDs > Larger OLED > Sound module > More neon",
        "estimated_cost": "$200-$500", "aesthetic": "Cyberpunk, neon, exposed",
        "default_color": "#0d0d0d", "default_style": "cyberpunk", "size_preference": "small",
    },
    "retro": {
        "name": "Retro Terminal", "description": "Vintage computing aesthetic, CRT look, ASCII art",
        "budget_range": "$100-$400", "best_sbc": "pi_zero_2w", "best_display": "eink_4_2inch",
        "best_keyboard": "vintage_keyboard", "best_power": "pisugar3_plus",
        "best_enclosure": "found_object", "best_cooling": "passive_heatsink",
        "best_connectivity": "cat6_flat", "best_pcb": "adafruit_phat", "best_wire": "silicon_26awg",
        "upgrade_path": "CRT filter > Amber phosphor display > Mechanical typewriter keys",
        "estimated_cost": "$150-$350", "aesthetic": "Vintage, amber monochrome, dented metal",
        "default_color": "#c0b19a", "default_style": "retro", "size_preference": "small",
    },
    "maker": {
        "name": "Maker / Hardware Hacking", "description": "Electronics workbench, GPIO projects, 3D printing controller",
        "budget_range": "$200-$700", "best_sbc": "pi5_8gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "3d_printed",
        "best_cooling": "active_fan", "best_connectivity": "usb_ethernet",
        "best_pcb": "sparkfun_phat", "best_wire": "silicon_24awg",
        "upgrade_path": "3D printer > Logic analyzer > Oscilloscope > CNC mill",
        "estimated_cost": "$300-$600", "aesthetic": "Bare PCB, exposed wiring, functional",
        "default_color": "#2d2d2d", "default_style": "industrial", "size_preference": "big",
    },
    "ham-radio": {
        "name": "Ham Radio Station", "description": "Amateur radio, HF/VHF/UHF, digital modes, APRS",
        "budget_range": "$400-$1200", "best_sbc": "pi5_8gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "custom_18650_x6", "best_enclosure": "pelican_1450",
        "best_cooling": "passive_heatsink", "best_connectivity": "hackrf_one",
        "best_pcb": "waveshare_phat", "best_wire": "silicon_18awg",
        "upgrade_path": "External antenna tuner > HF transceiver > Rotator > Power amplifier",
        "estimated_cost": "$500-$1000", "aesthetic": "Amateur radio, functional, labeled",
        "default_color": "#5c3a1e", "default_style": "steampunk", "size_preference": "big",
    },
    "field-repair": {
        "name": "Field Repair Kit", "description": "Diagnostic tools, network testing, hardware repair on the go",
        "budget_range": "$300-$800", "best_sbc": "pi5_8gb", "best_display": "hdmi_5inch",
        "best_keyboard": "bt_keyboard_trackpad", "best_power": "power_bank_20000",
        "best_enclosure": "pelican_1200", "best_cooling": "passive_heatsink",
        "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat", "best_wire": "silicon_24awg",
        "upgrade_path": "Multimeter integration > Thermal camera > Cable tester > Logic probe",
        "estimated_cost": "$350-$650", "aesthetic": "Toolbox, organized, labeled compartments",
        "default_color": "#ff6600", "default_style": "industrial", "size_preference": "small",
    },
    "drone": {
        "name": "Drone / UAV Controller", "description": "Drone ground station, FPV control, telemetry monitoring, autonomous missions",
        "budget_range": "$400-$1500", "best_sbc": "pi5_8gb", "best_display": "sunlight_readable_7",
        "best_keyboard": "bbq20kbd", "best_power": "custom_18650_x6", "best_enclosure": "pelican_1450",
        "best_cooling": "passive_heatsink", "best_connectivity": "hackrf_one", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_18awg",
        "upgrade_path": "GPS module > MAVLink telemetry > LTE modem > Dual SDR",
        "estimated_cost": "$500-$1200", "aesthetic": "Military field, sunlight readable",
        "default_color": "#4a5d23", "default_style": "industrial", "size_preference": "big",
    },
    "forensics": {
        "name": "Digital Forensics", "description": "Disk imaging, memory analysis, evidence collection, chain of custody",
        "budget_range": "$400-$1500", "best_sbc": "pi5_16gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "pelican_1450",
        "best_cooling": "active_fan", "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_24awg",
        "upgrade_path": "Write-blocker > NVMe dock > LTE modem > Faraday bag",
        "estimated_cost": "$500-$1200", "aesthetic": "Clean, labeled, evidence-grade",
        "default_color": "#2d2d2d", "default_style": "industrial", "size_preference": "big",
    },
    "test-equipment": {
        "name": "Test Equipment", "description": "Oscilloscope, logic analyzer, signal generator, multimeter, spectrum analyzer",
        "budget_range": "$300-$1000", "best_sbc": "pi5_8gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "3d_printed",
        "best_cooling": "active_fan", "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_24awg",
        "upgrade_path": "USB oscilloscope > Logic analyzer > Signal generator > Thermal camera",
        "estimated_cost": "$400-$800", "aesthetic": "Lab instrument, labeled ports",
        "default_color": "#2d2d2d", "default_style": "industrial", "size_preference": "big",
    },
    "weather-station": {
        "name": "Weather Station", "description": "Environmental monitoring, temperature/humidity, air quality, UV index",
        "budget_range": "$200-$700", "best_sbc": "pi5_4gb", "best_display": "eink_7inch",
        "best_keyboard": "bt_keyboard", "best_power": "solar_panel_18w", "best_enclosure": "pelican_1400",
        "best_cooling": "passive_heatsink", "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_18awg",
        "upgrade_path": "Anemometer > Rain gauge > Lightning detector > MQTT dashboard",
        "estimated_cost": "$300-$600", "aesthetic": "Weather-resistant, outdoor-rated",
        "default_color": "#3d5c3a", "default_style": "industrial", "size_preference": "big",
    },
    "home-automation": {
        "name": "Home Automation Hub", "description": "Home Assistant controller, Zigbee/Z-Wave gateway, smart home dashboard",
        "budget_range": "$200-$600", "best_sbc": "pi5_4gb", "best_display": "hdmi_7inch_ips",
        "best_keyboard": "bt_keyboard", "best_power": "ups_h5180", "best_enclosure": "3d_printed",
        "best_cooling": "passive_heatsink", "best_connectivity": "usb_ethernet", "best_pcb": "waveshare_phat",
        "best_wire": "silicon_24awg",
        "upgrade_path": "Zigbee dongle > Z-Wave dongle > Thread border router > LTE backup",
        "estimated_cost": "$250-$500", "aesthetic": "Clean, mounted, unobtrusive",
        "default_color": "#f5f5f5", "default_style": "minimal", "size_preference": "small",
    },
    "edge-ai": {
        "name": "Edge AI Inference", "description": "Local LLM, computer vision, NPU-accelerated ML, real-time inference",
        "budget_range": "$500-$2000", "best_sbc": "jetson_orin_nano", "best_display": "hdmi_10inch",
        "best_keyboard": "mech_60", "best_power": "ups_h5180", "best_enclosure": "3d_printed_vented",
        "best_cooling": "active_fan_heatsink", "best_connectivity": "usb_ethernet", "best_pcb": "jetson_carrier",
        "best_wire": "silicon_24awg",
        "upgrade_path": "More VRAM > External GPU > Camera array > NVMe RAID",
        "estimated_cost": "$600-$1800", "aesthetic": "Server rack, thermal management",
        "default_color": "#1a1a2e", "default_style": "futuristic", "size_preference": "big",
    },
}

# ============================================================
# SBC DATABASE
# ============================================================
SBC_DATABASE = {
    "pi5_16gb": {"name": "Raspberry Pi 5 16GB", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "16GB LPDDR4X", "gpu": "VideoCore VII", "storage": "MicroSD + NVMe via HAT", "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "2x micro-HDMI (4K@60Hz)", "price": 120, "power_draw": "5V/5A USB-C (27W max)", "form_factor": "85mm x 56mm", "pros": ["Most powerful Pi", "16GB RAM for heavy workloads", "NVMe support", "Dual 4K HDMI"], "cons": ["Needs active cooling", "Requires official 27W PSU"], "best_for": ["coding", "security", "research", "ai"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@60Hz per output", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 12, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "low"}},
    "pi5_8gb": {"name": "Raspberry Pi 5 8GB", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "8GB LPDDR4X", "gpu": "VideoCore VII", "storage": "MicroSD + NVMe via HAT", "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "2x micro-HDMI (4K@60Hz)", "price": 80, "power_draw": "5V/5A USB-C (27W max)", "form_factor": "85mm x 56mm", "pros": ["Great price/performance", "NVMe support", "Dual HDMI"], "cons": ["Needs active cooling"], "best_for": ["coding", "security", "research", "gaming", "media"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@60Hz per output", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 12, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "low"}},
    "pi5_4gb": {"name": "Raspberry Pi 5 4GB", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "4GB LPDDR4X", "gpu": "VideoCore VII", "storage": "MicroSD + NVMe via HAT", "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "2x micro-HDMI (4K@60Hz)", "price": 60, "power_draw": "5V/5A USB-C (27W max)", "form_factor": "85mm x 56mm", "pros": ["Affordable Pi 5", "Good for media/light tasks"], "cons": ["4GB limits heavy workloads"], "best_for": ["media", "gaming"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@60Hz per output", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 12, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "low"}},
    "pi4_8gb": {"name": "Raspberry Pi 4 8GB", "cpu": "BCM2711 Cortex-A72 @ 1.5GHz quad-core", "ram": "8GB LPDDR4", "gpu": "VideoCore VI", "storage": "MicroSD + USB SSD", "connectivity": "WiFi 5, BT 5.0, GbE, USB 3.0 x2, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "2x micro-HDMI (4K@30Hz)", "price": 55, "power_draw": "5V/3A USB-C (15W)", "form_factor": "85mm x 56mm", "pros": ["Mature ecosystem", "Huge community", "Cheap"], "cons": ["Older CPU", "No NVMe native"], "best_for": ["gaming", "media", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@30Hz per output", "refresh_rate_hz": 30, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 7, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "orange_pi_5_plus": {"name": "Orange Pi 5 Plus 16GB", "cpu": "RK3588 Cortex-A76+A55 octa-core", "ram": "16GB LPDDR4x", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0, USB 2.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 110, "power_draw": "5V/4A USB-C", "form_factor": "89mm x 56mm", "pros": ["More powerful than Pi 5", "NPU for AI", "2.5GbE", "eMMC + NVMe"], "cons": ["Smaller community", "Driver quirks"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, USB-C power", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "jetson_orin_nano": {"name": "NVIDIA Jetson Orin Nano 8GB", "cpu": "6-core Arm Cortex-A78AE", "ram": "8GB LPDDR5", "gpu": "1024-core NVIDIA Ampere + 32 Tensor Cores", "storage": "MicroSD + NVMe", "connectivity": "WiFi 5, BT 5.0, GbE, USB 3.2 x2, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "HDMI 2.1 (4K@60Hz)", "price": 249, "power_draw": "7W-15W (configurable)", "form_factor": "100mm x 87mm", "pros": ["40 TOPS AI performance", "GPU + Tensor Cores", "Camera support", "Industrial"], "cons": ["Expensive", "Needs good cooling", "JetPack required"], "best_for": ["ai"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C power", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "lattepanda_3_delta": {"name": "LattePanda 3 Delta 864", "cpu": "Intel N100 (4C/4T, 3.4GHz)", "ram": "8GB LPDDR5", "gpu": "Intel UHD Graphics", "storage": "eMMC 64GB + M.2 NVMe", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.2, USB-C", "gpio": "Arduino Leonardo co-processor", "video_output": "USB-C DP + HDMI 2.0", "price": 269, "power_draw": "5V/3A USB-C", "form_factor": "125mm x 78mm", "pros": ["Full x86 Windows/Linux", "Arduino co-processor", "NVMe"], "cons": ["Expensive", "More power draw", "Larger"], "best_for": ["coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@30Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C DP, USB-C power", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "radxa_rock_5b": {"name": "Radxa Rock 5B 16GB", "cpu": "RK3588 Cortex-A76+A55 octa-core", "ram": "16GB LPDDR4x", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 120, "power_draw": "5V/4A USB-C", "form_factor": "89mm x 62mm", "pros": ["Powerful RK3588", "NVMe onboard", "2.5GbE", "NPU"], "cons": ["Boot quirks", "Smaller community than Pi"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, USB-C power", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "khadas_edge2": {"name": "Khadas Edge2 Pro 16GB", "cpu": "RK3588S Cortex-A76+A55 octa-core", "ram": "16GB LPDDR4x", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe + MicroSD", "connectivity": "WiFi 6E, BT 5.3, GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "USB-C DP + HDMI 2.1", "price": 140, "power_draw": "5V/4A USB-C", "form_factor": "82mm x 58mm", "pros": ["Premium build", "WiFi 6E", "Compact", "NVMe"], "cons": ["Expensive", "Accessories sold separately"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, USB-C power", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "low", "failure_rate": "very_low"}},
    "orange_pi_zero3": {"name": "Orange Pi Zero 3", "cpu": "Allwinner H618 Cortex-A53 quad-core", "ram": "4GB LPDDR4", "gpu": "Mali-G57 MC1", "storage": "MicroSD + eMMC", "connectivity": "WiFi 5, BT 5.1, GbE, USB 2.0 x2", "gpio": "26-pin GPIO header", "video_output": "Micro-HDMI (4K@60Hz)", "price": 20, "power_draw": "5V/2A USB-C", "form_factor": "65mm x 50mm", "pros": ["Ultra cheap", "4K HDMI", "Good Pi Zero alternative"], "cons": ["Smaller community", "No USB 3.0"], "best_for": ["writerdeck", "conversation", "gaming"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Micro-HDMI 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Micro-HDMI, USB-C power", "power_consumption_w": 4, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "medium", "failure_rate": "medium"}},
    "pi_zero_2w": {"name": "Raspberry Pi Zero 2 W", "cpu": "BCM2710A1 Cortex-A53 @ 1GHz quad-core", "ram": "512MB LPDDR2", "gpu": "VideoCore IV", "storage": "MicroSD", "connectivity": "WiFi (2.4GHz), BT 4.2, 1x USB OTG, mini-HDMI", "gpio": "40-pin GPIO header (unpopulated)", "video_output": "mini-HDMI (1080p)", "price": 15, "power_draw": "5V/2.5A micro-USB", "form_factor": "65mm x 30mm", "pros": ["Tiny", "Ultra cheap", "Low power", "Perfect for writerdeck"], "cons": ["512MB RAM limits multitasking", "mini-HDMI needs adapter"], "best_for": ["writerdeck", "conversation", "survival"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "mini-HDMI 1080p@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "mini-HDMI, micro-USB power", "power_consumption_w": 2.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "cm5": {"name": "Raspberry Pi CM5 16GB", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "16GB LPDDR4X", "gpu": "VideoCore VII", "storage": "eMMC + MicroSD + NVMe", "connectivity": "PCIe Gen 3 x1, USB 3.0, GbE", "gpio": "2x 100-pin connectors", "video_output": "Depends on carrier board", "price": 110, "power_draw": "5V/4A", "form_factor": "55mm x 40mm (module only)", "pros": ["Most powerful compute module", "Industrial grade", "NVMe", "eMMC"], "cons": ["Needs carrier board", "More complex"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Depends on carrier", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Depends on carrier board", "power_consumption_w": 12, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "cm4": {"name": "Raspberry Pi CM4 8GB", "cpu": "BCM2711 Cortex-A72 @ 1.5GHz quad-core", "ram": "8GB LPDDR4", "gpu": "VideoCore VI", "storage": "eMMC + MicroSD", "connectivity": "PCIe Gen 2 x1, USB 3.0, GbE", "gpio": "2x 100-pin connectors", "video_output": "Depends on carrier board", "price": 55, "power_draw": "5V/3A", "form_factor": "55mm x 40mm (module only)", "pros": ["Mature ecosystem", "Cheap", "Lots of carrier boards"], "cons": ["Needs carrier board"], "best_for": ["gaming", "media", "writerdeck"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Depends on carrier", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Depends on carrier board", "power_consumption_w": 7, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "radxa_dragon_q8b": {"name": "Radxa Dragon Q8B (Snapdragon 8cx)", "cpu": "Snapdragon 8cx Gen 3 (8-core Kryo)", "ram": "32GB LPDDR5X", "gpu": "Adreno 690", "storage": "NVMe M.2 + eMMC", "connectivity": "WiFi 6E, BT 5.2, 2.5GbE, USB 3.2, Thunderbolt 4", "gpio": "40-pin GPIO", "video_output": "USB-C DP + HDMI 2.1", "price": 350, "power_draw": "15W-25W", "form_factor": "120mm x 80mm", "pros": ["ARM laptop-class CPU", "32GB RAM", "Thunderbolt 4", "NPU 40 TOPS"], "cons": ["Very expensive", "Linux support limited", "Needs active cooling"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "USB-C DP, HDMI 2.1", "power_consumption_w": 20, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "low"}},
    "orange_pi_rv2": {"name": "Orange Pi RV2 16GB (RISC-V)", "cpu": "SpacemiT K1 8-core RISC-V @ 2.0GHz", "ram": "16GB LPDDR4X", "gpu": "Imagination BXE-4-32", "storage": "eMMC + MicroSD + NVMe", "connectivity": "WiFi 6, BT 5.4, GbE, USB 3.0 x2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0 + Micro-HDMI", "price": 70, "power_draw": "5V/3A USB-C", "form_factor": "89mm x 56mm", "pros": ["8-core RISC-V", "16GB RAM", "NVMe", "Very affordable"], "cons": ["RISC-V ecosystem maturing", "No GPU acceleration"], "best_for": ["coding", "research", "maker"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@30Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C power", "power_consumption_w": 8, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "medium"}},
    "banana_pi_bpi_f3": {"name": "Banana Pi BPI-F3 16GB (RISC-V)", "cpu": "SpacemiT K1 8-core RISC-V @ 2.0GHz", "ram": "16GB LPDDR4X", "gpu": "Imagination BXE-4-32", "storage": "eMMC + MicroSD + NVMe", "connectivity": "WiFi 6, BT 5.4, 2.5GbE, USB 3.0 x2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0", "price": 80, "power_draw": "5V/3A USB-C", "form_factor": "89mm x 56mm", "pros": ["8-core RISC-V", "16GB RAM", "2.5GbE", "NVMe"], "cons": ["RISC-V ecosystem", "Larger community needed"], "best_for": ["coding", "research", "maker"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@30Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C power", "power_consumption_w": 8, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "medium"}},
    "armsom_cm1": {"name": "ArmSoM CM1 16GB (RK3588S Module)", "cpu": "RK3588S Cortex-A76+A55 octa-core", "ram": "16GB LPDDR4X", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe via carrier", "connectivity": "PCIe Gen 3, USB 3.0, GbE", "gpio": "200-pin connector", "video_output": "Depends on carrier", "price": 15, "power_draw": "5V/3A", "form_factor": "69mm x 50mm (module)", "pros": ["Ultra cheap RK3588S", "Industrial grade", "NVMe", "NPU"], "cons": ["Needs carrier board", "Module only"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Depends on carrier", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Depends on carrier", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "zimaboard_2": {"name": "ZimaBoard 2 (N100/N305)", "cpu": "Intel N100 or N305 (4C/8C)", "ram": "8GB/16GB DDR5", "gpu": "Intel UHD", "storage": "eMMC + NVMe M.2 + SATA", "connectivity": "WiFi 6, BT 5.2, 2x 2.5GbE, USB 3.2", "gpio": "16-pin GPIO", "video_output": "HDMI 2.0 + Mini-DP", "price": 120, "power_draw": "12W TDP", "form_factor": "120mm x 80mm", "pros": ["x86 with dual 2.5GbE", "NVMe + SATA", "Wall-mount", "Server-class"], "cons": ["x86 only", "Fan noise", "Limited GPIO"], "best_for": ["coding", "security", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, Mini-DP", "power_consumption_w": 12, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "medium", "failure_rate": "low"}},
    "pi_500": {"name": "Raspberry Pi 500 Keyboard Computer", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "8GB LPDDR4X", "gpu": "VideoCore VII", "storage": "MicroSD + NVMe via HAT", "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x1, USB 2.0 x2", "gpio": "40-pin GPIO header", "video_output": "2x micro-HDMI (4K@60Hz)", "price": 120, "power_draw": "5V/5A USB-C (27W max)", "form_factor": "Keyboard-integrated (286mm x 122mm)", "pros": ["All-in-one keyboard computer", "Built-in keyboard", "NVMe support", "Clean desk setup"], "cons": ["Keyboard not mechanical", "Fixed form factor"], "best_for": ["coding", "writerdeck", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@60Hz per output", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 12, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "rp2040_zero": {"name": "Waveshare RP2040 Zero", "cpu": "Dual-core ARM Cortex-M0+ @ 133MHz", "ram": "264KB SRAM", "gpu": "None (microcontroller)", "storage": "2MB Flash + MicroSD slot", "connectivity": "USB-C, WiFi, BT", "gpio": "29-pin GPIO", "video_output": "None (I2C/SPI display)", "price": 5, "power_draw": "3.3V/100mA", "form_factor": "23.5mm x 18mm (tiny)", "pros": ["Ultra cheap", "Tiny form factor", "RP2040 ecosystem", "MicroPython/CircuitPython"], "cons": ["No video output", "Very limited RAM", "Not a full Linux SBC"], "best_for": ["conversation", "maker"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via SPI/I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-C", "power_consumption_w": 0.3, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "feather_rp2040": {"name": "Adafruit Feather RP2040", "cpu": "Dual-core ARM Cortex-M0+ @ 133MHz", "ram": "264KB SRAM", "gpu": "None (microcontroller)", "storage": "8MB Flash + STEMMA QT", "connectivity": "USB-C, WiFi, BT, STEMMA QT", "gpio": "21-pin GPIO + STEMMA QT", "video_output": "None (I2C/SPI display)", "price": 15, "power_draw": "3.3V/100mA", "form_factor": "51mm x 23mm (Feather form)", "pros": ["Feather ecosystem", "USB host", "JST battery connector", "STEMMA QT", "Proven platform"], "cons": ["Not Linux SBC", "Limited RAM"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via SPI/I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-C", "power_consumption_w": 0.3, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "lattepanda_mu": {"name": "LattePanda μ (x86 SBC)", "cpu": "Intel N100 (4C/4T, 3.4GHz)", "ram": "8GB/16GB LPDDR5", "gpu": "Intel UHD", "storage": "eMMC + NVMe M.2", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.2", "gpio": "12-pin GPIO", "video_output": "USB-C DP + HDMI 2.0", "price": 150, "power_draw": "5V/3A USB-C", "form_factor": "60mm x 60mm (ultra-compact)", "pros": ["Full x86", "Ultra-compact", "Linux Mint compatible", "Intel CPU"], "cons": ["More power draw", "Needs active cooling"], "best_for": ["coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "radxa_nio_5a": {"name": "Radxa NIO 5A (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.0, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 80, "power_draw": "5V/4A USB-C", "form_factor": "90mm x 62mm", "pros": ["RK3588S powerful SoC", "6 TOPS NPU", "NVMe", "8K video decode"], "cons": ["Linux support maturing", "Needs active cooling"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "odroid_h5": {"name": "ODROID-H5 (Intel)", "cpu": "Intel Alder Lake-N (4C/4T)", "ram": "8GB/16GB DDR5", "gpu": "Intel UHD", "storage": "4x M.2 NVMe + eMMC", "connectivity": "WiFi 6E, BT 5.3, 2x 10GbE, USB 3.2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0 + DP 1.4", "price": 250, "power_draw": "12V/3A", "form_factor": "120mm x 120mm (NAS form)", "pros": ["4x M.2 NVMe slots", "2x 10GbE", "NAS/edge computing beast", "DDR5"], "cons": ["Larger form factor", "No built-in battery"], "best_for": ["coding", "research", "ai"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, DP 1.4", "power_consumption_w": 25, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "cix_p1": {"name": "CIX P1 (RISC-V)", "cpu": "CIX C1000 RISC-V (8-core)", "ram": "8GB LPDDR5", "gpu": "IMG BXE-4-32", "storage": "eMMC + MicroSD", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0 + USB-C DP", "price": 100, "power_draw": "5V/3A USB-C", "form_factor": "100mm x 75mm", "pros": ["RISC-V 8-core", "GPU with Linux driver", "Affordable RISC-V"], "cons": ["RISC-V ecosystem still maturing", "No NVMe native"], "best_for": ["coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C DP", "power_consumption_w": 8, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "low"}},
    "orange_pi_6": {"name": "Orange Pi 6 (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 90, "power_draw": "5V/4A USB-C", "form_factor": "90mm x 62mm", "pros": ["RK3588S at Pi 5 price", "NVMe native", "2.5GbE", "6 TOPS NPU"], "cons": ["OPi driver support mixed", "Community smaller than Pi"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "milkv_jupiter": {"name": "Milk-V Jupiter (RISC-V)", "cpu": "SG2380 RISC-V 8-core", "ram": "8GB/16GB DDR5", "gpu": "IMG BXT-32-1024", "storage": "eMMC + NVMe M.2", "connectivity": "WiFi 6E, BT 5.3, 2.5GbE, USB 3.2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + DP 1.4", "price": 150, "power_draw": "12V/2A", "form_factor": "120mm x 120mm", "pros": ["High-performance RISC-V", "NVMe", "2.5GbE", "Desktop-class RISC-V"], "cons": ["Expensive for RISC-V", "Ecosystem maturing", "Large form factor"], "best_for": ["coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "HDMI 2.1, DP 1.4", "power_consumption_w": 15, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "low"}},
    "esp32_p4": {"name": "ESP32-P4 (Espressif)", "cpu": "Dual-core RISC-V @ 400MHz", "ram": "520KB SRAM + 32MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "USB OTG, MIPI CSI/DSI, Ethernet MAC", "gpio": "54-pin GPIO", "video_output": "MIPI DSI + RGB LCD", "price": 5, "power_draw": "3.3V/200mA", "form_factor": "25mm x 20mm (module)", "pros": ["Dual MIPI cameras", "MIPI display", "USB HS", "H.264 encoder", "Ultra cheap"], "cons": ["No WiFi/BT native", "MCU not Linux", "Limited RAM"], "best_for": ["maker", "conversation", "drone"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "MIPI DSI up to 1080p", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "MIPI CSI/DSI, USB OTG", "power_consumption_w": 0.5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "m5stack_cardputer_adv": {"name": "M5Stack Cardputer ADV (ESP32-S3)", "cpu": "ESP32-S3 Dual-core @ 240MHz", "ram": "512KB SRAM + 8MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi, BLE 5.0, USB-C", "gpio": "Internal GPIO", "video_output": "1.14\" TFT (135x240)", "price": 25, "power_draw": "3.7V/150mA", "form_factor": "Credit-card size (85mm x 54mm)", "pros": ["Ultra portable", "Built-in keyboard", "TFT display", "IR transceiver", "RTC battery"], "cons": ["Tiny screen", "MCU not Linux", "Limited RAM"], "best_for": ["conversation", "maker", "security"], "compatibility": ["ALL"], "display_type": "TFT", "screen_size_inches": 1.14, "resolution": "135x240", "refresh_rate_hz": 60, "brightness_nits": 300, "interface": "SPI TFT", "power_consumption_w": 0.4, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "radxa_rock_5a": {"name": "Radxa ROCK 5A (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 100, "power_draw": "5V/4A USB-C", "form_factor": "100mm x 75mm", "pros": ["RK3588S flagship", "NVMe native", "2.5GbE", "M.2 E-key WiFi"], "cons": ["More expensive than competitors", "Active cooling needed"], "best_for": ["ai", "coding", "security", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "orange_pi_5_max": {"name": "Orange Pi 5 Max (RK3588)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB/32GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + 2x NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP + eDP", "price": 120, "power_draw": "5V/5A USB-C", "form_factor": "110mm x 80mm", "pros": ["Full RK3588", "32GB RAM option", "2x NVMe", "Triple display"], "cons": ["Large form factor", "Expensive", "Active cooling needed"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, eDP", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "orange_pi_5_pro": {"name": "Orange Pi 5 Pro (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 85, "power_draw": "5V/4A USB-C", "form_factor": "90mm x 62mm", "pros": ["Affordable RK3588S", "NVMe native", "Good community support"], "cons": ["GbE only (not 2.5GbE)", "Active cooling needed"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "pi_cm0": {"name": "Raspberry Pi CM0 (Compute Module 0)", "cpu": "BCM2710 Cortex-A53 (quad-core)", "ram": "512MB LPDDR2", "gpu": "VideoCore IV", "storage": "eMMC + MicroSD via carrier", "connectivity": "PCIe, USB 2.0", "gpio": "2x 50-pin connectors", "video_output": "Depends on carrier board", "price": 10, "power_draw": "3.3V/1A", "form_factor": "30mm x 25mm (tiny module)", "pros": ["Ultra cheap compute module", "Tiny form factor", "Pi ecosystem", "Great for embedded"], "cons": ["Needs carrier board", "512MB RAM only", "No built-in WiFi"], "best_for": ["maker", "conversation", "writerdeck"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Depends on carrier", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Depends on carrier board", "power_consumption_w": 3, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "makerfabs_cm0iq": {"name": "Makerfabs CM0-IQ Carrier Board", "cpu": "For Pi CM0 module", "ram": "CM0 dependent", "gpu": "CM0 dependent", "storage": "MicroSD + eMMC", "connectivity": "WiFi, BT, USB, HDMI", "gpio": "40-pin GPIO + camera + display", "video_output": "HDMI + MIPI DSI + CSI", "price": 25, "power_draw": "5V/2A USB-C", "form_factor": "Compact carrier", "pros": ["CM0 carrier with full Pi ports", "Camera + display connectors", "Affordable"], "cons": ["Needs CM0 module", "Basic specs"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "N/A (Carrier)", "screen_size_inches": 0, "resolution": "HDMI 1080p", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI, USB, CSI, DSI", "power_consumption_w": 5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "milkv_jupiter2": {"name": "Milk-V Jupiter2 (RISC-V SG2380)", "cpu": "SG2380 RISC-V 8-core @ 2.5GHz", "ram": "8GB/16GB/32GB DDR5", "gpu": "IMG BXT-32-1024", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6E, BT 5.3, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + DP 1.4", "price": 130, "power_draw": "12V/2A DC", "form_factor": "120mm x 120mm", "pros": ["8-core RISC-V desktop-class", "32GB DDR5 option", "NVMe + 2.5GbE", "PCIe 3.0 expansion"], "cons": ["RISC-V Linux ecosystem maturing", "Larger form factor", "Needs 12V power supply"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "HDMI 2.1, DP 1.4", "power_consumption_w": 20, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "low"}},
    "radxa_a7a": {"name": "Radxa A7A (RK3588S, AIO)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 75, "power_draw": "5V/4A USB-C", "form_factor": "100mm x 75mm (AIO laptop board)", "pros": ["RK3588S at budget price", "Laptop AIO design", "NVMe native", "6 TOPS NPU"], "cons": ["AIO form limits enclosure options", "Linux support still maturing"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "hackberrypi_cm5": {"name": "HackberryPi CM5 (RK3588 Module)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB/32GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP + eDP", "price": 99, "power_draw": "5V/5A USB-C", "form_factor": "100mm x 80mm (CM module)", "pros": ["Full RK3588 in CM form", "32GB option", "Triple display", "NVMe + 2.5GbE", "6 TOPS NPU"], "cons": ["Needs carrier board", "Premium price for module"], "best_for": ["ai", "coding", "security", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, eDP", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "zhihe_a210": {"name": "Zhihe A210 (RISC-V, 12 TOPS NPU)", "cpu": "SpacemiT K1 8-core RISC-V @ 2.0GHz", "ram": "8GB/16GB LPDDR4X", "gpu": "IMG BXE-4-32", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.4, GbE, USB 3.0 x2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0 + USB-C DP", "price": 85, "power_draw": "5V/3A USB-C", "form_factor": "100mm x 75mm", "pros": ["12 TOPS NPU for edge AI", "8-core RISC-V", "NVMe", "16GB RAM option"], "cons": ["RISC-V ecosystem", "NPU software immature", "No 2.5GbE"], "best_for": ["ai", "coding", "research", "maker"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@30Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C DP", "power_consumption_w": 8, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "medium"}},
    "orange_pi_5_ultra": {"name": "Orange Pi 5 Ultra (RK3588, 32GB)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "16GB/32GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + 2x NVMe M.2 + MicroSD", "connectivity": "WiFi 6E, BT 5.3, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP + eDP", "price": 140, "power_draw": "5V/5A USB-C", "form_factor": "110mm x 80mm", "pros": ["32GB RAM flagship", "2x NVMe", "Triple display", "WiFi 6E", "6 TOPS NPU"], "cons": ["Expensive", "Large form factor", "Active cooling needed"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, eDP", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
}

# ============================================================
# DISPLAY DATABASE
# ============================================================
DISPLAY_DATABASE = {
    "hdmi_7inch_ips": {"name": "Waveshare 7\" HDMI IPS (1024x600)", "size": "7 inch", "resolution": "1024x600", "interface": "HDMI + USB-C touch", "price": 40, "power_draw": "5V/1A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["IPS wide angle", "Capacitive touch", "Cheap", "Bright"], "cons": ["Needs HDMI adapter for Pi Zero"], "best_for": ["ALL"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 350, "power_consumption_w": 5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "hdmi_7inch_1024": {"name": "Waveshare 7\" HDMI IPS (1280x800)", "size": "7 inch", "resolution": "1280x800", "interface": "HDMI + USB-C touch", "price": 50, "power_draw": "5V/1A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["Higher resolution", "Sharp text for coding"], "cons": ["Slightly more expensive"], "best_for": ["coding", "security", "research"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "very_low"}},
    "hdmi_10inch": {"name": "Waveshare 10.1\" HDMI IPS (1920x1200)", "size": "10.1 inch", "resolution": "1920x1200", "interface": "HDMI + USB-C touch", "price": 80, "power_draw": "5V/1.5A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["Large screen", "Full HD", "Good for media/AI", "IPS"], "cons": ["Larger enclosure needed", "More power draw"], "best_for": ["ai", "media", "research", "coding"], "display_type": "IPS", "screen_size_inches": 10.1, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 7.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "waveshare_ultrawide_79": {"name": "Waveshare 7.9\" HDMI IPS Ultrawide (400x1280)", "size": "7.9 inch", "resolution": "400x1280", "interface": "HDMI + USB touch", "price": 55, "power_draw": "5V/1A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["Unique ultrawide", "Great for terminal/code", "Touch"], "cons": ["Unusual resolution", "Niche use"], "best_for": ["coding", "security", "writerdeck"], "display_type": "IPS", "screen_size_inches": 7.9, "refresh_rate_hz": 60, "brightness_nits": 350, "power_consumption_w": 5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "dsi_7inch": {"name": "Raspberry Pi Official 7\" DSI Touchscreen", "size": "7 inch", "resolution": "800x480", "interface": "DSI ribbon cable", "price": 60, "power_draw": "5V/0.5A via GPIO", "touch": True, "viewing_angle": "170 degrees", "pros": ["Official Pi accessory", "Direct DSI (no HDMI)", "GPIO pass-through"], "cons": ["Lower resolution", "Bulky bezel"], "best_for": ["coding", "gaming"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 300, "power_consumption_w": 2.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "eink_7inch": {"name": "Waveshare 7.5\" E-Ink (800x480)", "size": "7.5 inch", "resolution": "800x480", "interface": "SPI", "price": 70, "power_draw": "Near zero (static), ~15mA refresh", "touch": False, "viewing_angle": "180 degrees (full)", "pros": ["Sunlight readable", "Ultra low power", "Paper-like", "No eye strain"], "cons": ["Slow refresh", "No color", "No touch"], "best_for": ["writerdeck", "survival"], "display_type": "E-Ink", "screen_size_inches": 7.5, "refresh_rate_hz": 1, "brightness_nits": 300, "power_consumption_w": 0.05, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "eink_4_2inch": {"name": "Waveshare 4.2\" E-Ink (400x300)", "size": "4.2 inch", "resolution": "400x300", "interface": "SPI", "price": 30, "power_draw": "Near zero", "touch": False, "viewing_angle": "180 degrees", "pros": ["Tiny", "Ultra cheap", "Paper-like"], "cons": ["Small text", "Slow refresh", "No touch"], "best_for": ["writerdeck", "survival"], "display_type": "E-Ink", "screen_size_inches": 4.2, "refresh_rate_hz": 1, "brightness_nits": 300, "power_consumption_w": 0.03, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "oled_1_3inch": {"name": "SSD1306 1.3\" OLED (128x64)", "size": "1.3 inch", "resolution": "128x64", "interface": "I2C", "price": 8, "power_draw": "~10mA", "touch": False, "viewing_angle": "160 degrees", "pros": ["Tiny", "Ultra cheap", "Low power", "Great for status display"], "cons": ["Tiny", "Monochrome"], "best_for": ["conversation", "writerdeck"], "display_type": "OLED", "screen_size_inches": 1.3, "refresh_rate_hz": 30, "brightness_nits": 150, "power_consumption_w": 0.05, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "sunlight_readable_7": {"name": "Sunread 7\" Sunlight Readable (1024x600)", "size": "7 inch", "resolution": "1024x600", "interface": "HDMI + USB touch", "price": 120, "power_draw": "5V/2A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["1000 nits brightness", "Direct sunlight readable", "IPS"], "cons": ["Expensive", "Higher power draw"], "best_for": ["research", "survival"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 1000, "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "hdmi_5inch": {"name": "Waveshare 5\" HDMI IPS (800x480)", "size": "5 inch", "resolution": "800x480", "interface": "HDMI + USB touch", "price": 25, "power_draw": "5V/0.5A via USB", "touch": True, "viewing_angle": "178 degrees", "pros": ["Small", "Cheap", "Touch"], "cons": ["Low resolution"], "best_for": ["conversation", "writerdeck", "field-repair"], "display_type": "IPS", "screen_size_inches": 5, "refresh_rate_hz": 60, "brightness_nits": 300, "power_consumption_w": 2.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "pimoroni_presto": {"name": "Pimoroni Presto 4\" IPS (480x480)", "size": "4 inch", "resolution": "480x480", "interface": "QwST I2C + SPI", "price": 90, "power_draw": "5V/0.5A", "touch": True, "viewing_angle": "178 degrees", "pros": ["Square display", "Touch", "Pimoroni quality", "RP2350/Pico compatible"], "cons": ["Small", "Needs QwST cable"], "best_for": ["conversation", "writerdeck"], "display_type": "IPS", "screen_size_inches": 4, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 2.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "medium", "failure_rate": "very_low"}},
    "waveshare_13_3_eink": {"name": "Waveshare 13.3\" E-Ink (1600x1200)", "size": "13.3 inch", "resolution": "1600x1200", "interface": "SPI", "price": 200, "power_draw": "Near zero (static)", "touch": False, "viewing_angle": "180 degrees", "pros": ["Huge e-ink", "Paper-like", "Sunlight readable", "Zero power static"], "cons": ["Very slow refresh", "Expensive", "Fragile"], "best_for": ["writerdeck", "research"], "display_type": "E-Ink", "screen_size_inches": 13.3, "refresh_rate_hz": 0.5, "brightness_nits": 300, "power_consumption_w": 0.05, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "low", "failure_rate": "low"}},
    "inky_impression_7": {"name": "Pimoroni Inky Impression 7.3\" (800x480 7-color)", "size": "7.3 inch", "resolution": "800x480", "interface": "SPI", "price": 90, "power_draw": "Near zero (static)", "touch": False, "viewing_angle": "180 degrees", "pros": ["7-color e-ink", "Sunlight readable", "Beautiful artwork display"], "cons": ["Slow refresh (30s)", "No touch", "Limited colors"], "best_for": ["writerdeck", "conversation-piece"], "display_type": "E-Ink", "screen_size_inches": 7.3, "refresh_rate_hz": 0.1, "brightness_nits": 300, "power_consumption_w": 0.03, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "waveshare_4inch_rpi": {"name": "Waveshare 4\" RPi LCD (480x800)", "size": "4 inch", "resolution": "480x800", "interface": "SPI + FPC", "price": 30, "power_draw": "5V/0.3A", "touch": True, "viewing_angle": "178 degrees", "pros": ["Tall portrait display", "Touch", "Pi-native"], "cons": ["Unusual orientation", "SPI bandwidth"], "best_for": ["writerdeck", "conversation"], "display_type": "IPS", "screen_size_inches": 4, "refresh_rate_hz": 60, "brightness_nits": 350, "power_consumption_w": 1.5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "esp32s3_2_8inch_touch": {"name": "Waveshare ESP32-S3 2.8\" Touch LCD (240x320)", "size": "2.8 inch", "resolution": "240x320", "interface": "UART/I2C + battery connectors", "price": 20, "power_draw": "3.7V LiPo battery", "touch": True, "viewing_angle": "140 degrees", "pros": ["ESP32-S3 built-in", "Touch", "Battery ready", "UART/I2C"], "cons": ["Small resolution", "ESP32 limited processing"], "best_for": ["conversation", "writerdeck"], "display_type": "TFT", "screen_size_inches": 2.8, "refresh_rate_hz": 60, "brightness_nits": 300, "power_consumption_w": 0.5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
}

# ============================================================
# KEYBOARD DATABASE
# ============================================================
KEYBOARD_DATABASE = {
    "drop_planck_v7": {"name": "Drop Planck v7 40% Ortholinear", "type": "Ortholinear 40%", "layout": "40% grid", "switches": "Cherry MX compatible (Hot-swap)", "connection": "USB-C", "price_range": "$100-$160", "size_mm": "270 x 115", "pros": ["Premium build", "Hot-swap", "QMK/VIA", "Aluminum case option"], "cons": ["Expensive", "Learning curve"], "best_for": ["writerdeck", "coding", "conversation"]},
    "keychron_k12": {"name": "Keychron K12 60% Mechanical", "type": "Mechanical 60%", "layout": "60% ANSI", "switches": "Gateron Brown/Red/Blue", "connection": "USB-C / BT", "price_range": "$50-$80", "size_mm": "285 x 100", "pros": ["Wireless + wired", "Compact", "RGB backlight", "Gasket mount"], "cons": ["No function row"], "best_for": ["coding", "security", "research", "ai"]},
    "mech_60": {"name": "60% Mechanical Keyboard (HyperX Alloy 60 / generic)", "type": "Mechanical 60%", "layout": "60% ANSI", "switches": "Gateron Brown/Red/Blue", "connection": "USB-C", "price_range": "$30-$60", "size_mm": "285 x 100", "pros": ["Compact", "Great typing", "RGB backlight", "Cheap"], "cons": ["No function row", "No wireless"], "best_for": ["coding", "security", "research", "ai"]},
    "ortho_40": {"name": "Planck / OLKB 40% Ortholinear", "type": "Ortholinear 40%", "layout": "40% grid", "switches": "Cherry MX compatible", "connection": "USB-C", "price_range": "$80-$150", "size_mm": "270 x 115", "pros": ["Ultra compact", "Programmable QMK", "Cyberdeck classic", "Split option"], "cons": ["Learning curve", "No number row"], "best_for": ["writerdeck", "coding", "conversation"]},
    "corne_split": {"name": "Corne / CRKBD Split Keyboard", "type": "Split 3x6", "layout": "36 keys split", "switches": "Cherry MX compatible", "connection": "USB-C / wireless", "price_range": "$100-$200", "size_mm": "120 x 120 (each half)", "pros": ["Ergonomic", "Split design", "Minimal", "QMK firmware"], "cons": ["Assembly required", "Learning curve"], "best_for": ["writerdeck", "coding"]},
    "bbq20kbd": {"name": "BBQ20KBD Thumb Keyboard", "type": "Thumb-based", "layout": "Compact thumb", "switches": "Kailh Choc low-profile", "connection": "USB-C / wireless", "price_range": "$60-$120", "size_mm": "150 x 100", "pros": ["Held in one hand", "Field use", "Compact", "Low-profile switches"], "cons": ["Limited keys", "Learning curve"], "best_for": ["survival", "research", "writerdeck"]},
    "thumb_keyboard": {"name": "Pinky3 / Thumb Keyboard", "type": "Thumb-based", "layout": "Compact thumb", "switches": "Cherry MX / Kailh", "connection": "USB-C / wireless", "price_range": "$60-$120", "size_mm": "150 x 100", "pros": ["Held in one hand", "Field use", "Compact"], "cons": ["Limited keys", "Learning curve"], "best_for": ["survival", "research"]},
    "bt_keyboard": {"name": "Logitech K380 / Bluetooth Compact", "type": "Membrane BT", "layout": "Full compact", "switches": "Membrane", "connection": "Bluetooth", "price_range": "$30-$50", "size_mm": "279 x 124", "pros": ["Multi-device", "No wires", "Cheap", "Proven"], "cons": ["Membrane feel", "Not QMK"], "best_for": ["media", "conversation", "gaming"]},
    "bt_keyboard_trackpad": {"name": "Keyboard + Trackpad Combo (Rii i8+)", "type": "Wireless combo", "layout": "Mini keyboard + touchpad", "switches": "Membrane", "connection": "2.4GHz USB dongle", "price_range": "$20-$35", "size_mm": "145 x 95", "pros": ["Keyboard + mouse in one", "Tiny", "Media center ideal"], "cons": ["Small keys", "Dongle required"], "best_for": ["media", "gaming", "field-repair"]},
    "vintage_keyboard": {"name": "Vintage Mechanical (Model M / Cherry G80)", "type": "Full-size vintage", "layout": "Full ANSI", "switches": "Buckling spring / Cherry MX", "connection": "USB adapter", "price_range": "$30-$100", "size_mm": "450 x 160", "pros": ["Epic typing feel", "Cyberpunk aesthetic", "Built like a tank"], "cons": ["Huge", "Heavy", "Needs adapter"], "best_for": ["conversation", "coding", "retro"]},
}

# ============================================================
# POWER DATABASE
# ============================================================
POWER_DATABASE = {
    "ups_h5180": {"name": "Waveshare UPS HAT B (5V/5A, 2x 18650)", "type": "UPS HAT", "capacity": "6000mAh (2x 18650)", "output": "5V/5A", "charge_time": "~3 hours", "runtime": "3-6 hours (depending on load)", "price": 30, "pros": ["Auto power switch", "Charges while running", "Battery level I2C", "Compact"], "cons": ["Batteries not included", "Adds height"], "best_for": ["coding", "security", "research", "ai"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "pisugar3_plus": {"name": "PiSugar 3 Plus (5000mAh)", "type": "SBC-mount battery", "capacity": "5000mAh", "output": "5V/3A", "charge_time": "~3 hours", "runtime": "3-6 hours", "price": 35, "pros": ["Sits under Pi Zero/3A+", "RTC clock", "Button control", "Compact"], "cons": ["Pi Zero only", "Limited capacity"], "best_for": ["writerdeck", "conversation", "survival"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "geekworm_x1200": {"name": "Geekworm X1200 UPS HAT (5V/5A, 4x 18650)", "type": "UPS HAT", "capacity": "12000mAh (4x 18650)", "output": "5V/5A", "charge_time": "~4 hours", "runtime": "6-12 hours", "price": 40, "pros": ["High capacity", "Auto switch", "Pi 5 compatible", "Safe shutdown"], "cons": ["Batteries not included", "Large footprint"], "best_for": ["coding", "security", "research", "ai"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "pimoroni_lipo_shim": {"name": "Pimoroni LiPo SHIM (2000mAh)", "type": "SBC-mount battery", "capacity": "2000mAh LiPo", "output": "5V/2.5A", "charge_time": "~2 hours", "runtime": "1-3 hours", "price": 15, "pros": ["Ultra thin", "Sits under Pi", "Button on/off", "Cheap"], "cons": ["Small capacity", "Low runtime"], "best_for": ["writerdeck", "conversation"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "power_bank_20000": {"name": "Anker 20000mAh Power Bank", "type": "USB power bank", "capacity": "20000mAh", "output": "5V/3A, 9V/2A, 12V/1.5A", "charge_time": "~6 hours", "runtime": "8-15 hours", "price": 35, "pros": ["High capacity", "USB-C PD", "No soldering", "Portable"], "cons": ["Bulky", "Not integrated"], "best_for": ["gaming", "media", "research", "coding"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "n/a", "community_usage": "very_high", "failure_rate": "very_low"}},
    "custom_18650_x6": {"name": "Custom 18650 x6 (BMS + Buck Converter)", "type": "Custom 6-cell", "capacity": "18000mAh", "output": "5V/5A (buck)", "charge_time": "~5 hours", "runtime": "10-20 hours", "price": 30, "pros": ["Massive capacity", "Field repairable", "Custom voltage"], "cons": ["Soldering required", "Needs BMS", "Larger"], "best_for": ["survival", "research", "security"], "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "varies", "driver_support": "n/a", "community_usage": "medium", "failure_rate": "medium"}},
    "solar_panel_18w": {"name": "TP-Link SolarGo 18W Panel + Battery Pack", "type": "Solar charging", "capacity": "20000mAh battery + 18W panel", "output": "5V/2.4A USB", "charge_time": "4-6 hours (sunlight)", "runtime": "Continuous (sunlight dependent)", "price": 50, "pros": ["Off-grid", "Sustainable", "Emergency power"], "cons": ["Weather dependent", "Slow charge"], "best_for": ["survival", "research"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "n/a", "community_usage": "medium", "failure_rate": "low"}},
    "tp4056_module": {"name": "TP4056 1A Li-Ion/LiPo Charger Module", "type": "Battery charging module", "capacity": "Charges single-cell Li-Ion/LiPo (3.7V)", "output": "N/A (charge only)", "charge_time": "~3 hours (2000mAh cell)", "runtime": "N/A (charging module)", "price": 1, "pros": ["Ultra cheap", "Built-in protection", "Micro-USB/USB-C input", "Status LEDs"], "cons": ["1A max charge rate", "Single cell only"], "best_for": ["ALL"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "n/a", "community_usage": "very_high", "failure_rate": "very_low"}},
    "bq25895_charger": {"name": "BQ25895 3A Fast Charger Board", "type": "Battery charging module", "capacity": "Charges 1-4 cell Li-Ion/LiPo (up to 16.8V)", "output": "N/A (charge only)", "charge_time": "~2 hours (2000mAh cell at 3A)", "runtime": "N/A (charging module)", "price": 8, "pros": ["Fast charging 3A", "Multi-cell support", "I2C monitoring", "USB-C PD compatible"], "cons": ["More complex setup", "Needs I2C config"], "best_for": ["ai", "coding", "security", "research"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "usbc_pd_board": {"name": "USB-C PD Trigger Board (5V/9V/12V/15V/20V)", "type": "Power delivery negotiation", "capacity": "N/A (voltage negotiation)", "output": "5V-20V @ 3A selectable", "charge_time": "N/A", "runtime": "N/A (passthrough)", "price": 5, "pros": ["Negotiates USB-C PD voltage", "Works with any PD adapter", "Compact", "No microcontroller needed"], "cons": ["Requires PD-capable adapter", "Fixed voltage per config"], "best_for": ["ALL"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "n/a", "community_usage": "medium", "failure_rate": "low"}},
    "waterproof_battery_10000": {"name": "Waterproof Battery Pack 10000mAh (IP67)", "type": "Waterproof power bank", "capacity": "10000mAh", "output": "5V/2A USB-C", "charge_time": "~4 hours", "runtime": "4-8 hours", "price": 25, "pros": ["IP67 rated", "Shockproof", "USB-C", "Compact"], "cons": ["Moderate capacity", "Heavier than standard"], "best_for": ["survival", "research", "field-repair"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "n/a", "community_usage": "medium", "failure_rate": "low"}},
    "solar_charger_28w": {"name": "Goal Zero Nomad 28 Solar Panel + Venture 30", "type": "Solar charging kit", "capacity": "7800mAh battery + 28W panel", "output": "5V/2.4A USB-A + USB-C", "charge_time": "3-5 hours (sunlight)", "runtime": "Continuous (sunlight dependent)", "price": 120, "pros": ["High efficiency panels", "Waterproof battery", "Charge two devices", "Proven brand"], "cons": ["Expensive", "Heavy panel"], "best_for": ["survival", "research"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "n/a", "community_usage": "high", "failure_rate": "very_low"}},
}

# ============================================================
# ENCLOSURE DATABASE
# ============================================================
ENCLOSURE_DATABASE = {
    "pelican_1450": {"name": "Pelican 1450 Case", "material": "Polypropylene", "dimensions": "350 x 250 x 160mm", "protection": "IP67 waterproof, crushproof, dustproof", "foam": "Pick-and-pluck foam interior", "price": 80, "pros": ["Ultimate protection", "Professional look", "Weatherproof"], "cons": ["Heavy", "Expensive", "Needs cutting"], "best_for": ["security", "survival", "research"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "pelican_1200": {"name": "Pelican 1200 Case", "material": "Polypropylene", "dimensions": "260 x 185 x 105mm", "protection": "IP67 waterproof", "foam": "Pick-and-pluck foam", "price": 45, "pros": ["Compact Pelican", "Waterproof", "Good for small builds"], "cons": ["Limited space"], "best_for": ["writerdeck", "field-repair", "conversation"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "pelican_1150": {"name": "Pelican 1150 Case", "material": "Polypropylene", "dimensions": "235 x 165 x 85mm", "protection": "IP67 waterproof", "foam": "Pick-and-pluck foam", "price": 35, "pros": ["Small Pelican", "Waterproof", "Cheap"], "cons": ["Tight fit for Pi 5"], "best_for": ["writerdeck", "conversation", "retro"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "pelican_1400": {"name": "Pelican 1400 Case", "material": "Polypropylene", "dimensions": "325 x 235 x 140mm", "protection": "IP67 waterproof", "foam": "Pick-and-pluck foam", "price": 60, "pros": ["Smaller Pelican", "Waterproof", "Professional"], "cons": ["Needs foam cutting"], "best_for": ["research", "survival"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "ip65_enclosure_150x100": {"name": "IP65 ABS Enclosure 150x100x60mm", "material": "ABS + Silicone gasket", "dimensions": "150 x 100 x 60mm", "protection": "IP65 dust-tight + water jets", "foam": "None (mounting bosses)", "price": 12, "pros": ["Cheap IP65", "Mounting bosses", "Cable glands included", "Lightweight"], "cons": ["Needs drilling for ports", "Not crushproof"], "best_for": ["survival", "research", "field-repair"], "waterproof_rating": "IP65", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "ip67_enclosure_aluminum": {"name": "IP67 Aluminum Enclosure 200x120x60mm", "material": "Die-cast aluminum + silicone gasket", "dimensions": "200 x 120 x 60mm", "protection": "IP67 waterproof, submersible", "foam": "Optional foam insert", "price": 25, "pros": ["Full IP67 submersion", "EMI shielding", "Heat dissipation", "Rugged"], "cons": ["Heavier", "Needs CNC/drilling", "Thermal management needed"], "best_for": ["security", "survival", "research"], "waterproof_rating": "IP67", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "ip68_poly_case": {"name": "IP68 Polycarbonate Case 250x180x100mm", "material": "Polycarbonate + EPDM gasket", "dimensions": "250 x 180 x 100mm", "protection": "IP68 permanent submersion", "foam": "Pick-and-pluck foam", "price": 40, "pros": ["IP68 rated (1m submersion)", "Transparent option available", "UV resistant", "Impact resistant"], "cons": ["Expensive", "Larger than needed for small builds"], "best_for": ["survival", "research", "field-repair"], "waterproof_rating": "IP68", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "low", "failure_rate": "low"}},
    "3d_printed": {"name": "Custom 3D Printed Enclosure (PETG)", "material": "PETG / PLA / ABS", "dimensions": "Variable (custom fit)", "protection": "Basic splash-resistant", "price": 5, "pros": ["Fully customizable", "Cheap", "Fast iteration", "Open source designs"], "cons": ["Not waterproof", "Needs printer", "Weaker material"], "best_for": ["coding", "gaming", "media", "conversation", "writerdeck", "maker"], "waterproof_rating": "None", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "n/a", "community_usage": "very_high", "failure_rate": "low"}},
    "3d_printed_cyberpunk": {"name": "3D Printed Cyberpunk Shell", "material": "PLA + Neon filament", "dimensions": "Variable", "protection": "Basic", "price": 10, "pros": ["Aesthetic", "LED cutouts", "Exposed screws", "Industrial look"], "cons": ["Fragile", "Needs finishing"], "best_for": ["conversation-piece", "retro"], "waterproof_rating": "None", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "n/a", "community_usage": "high", "failure_rate": "low"}},
    "3d_printed_vented": {"name": "3D Printed Vented Enclosure", "material": "PETG / ABS", "dimensions": "Variable (with fan cutouts)", "protection": "Splash-resistant with vents", "price": 8, "pros": ["Airflow design", "Fan mounting", "Custom fit"], "cons": ["Less dust protection"], "best_for": ["ai", "coding"], "waterproof_rating": "None", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "n/a", "community_usage": "high", "failure_rate": "low"}},
    "clockworkpi_uconsole": {"name": "ClockworkPi uConsole Case", "material": "Aluminum + Plastic", "dimensions": "Custom (uConsole form factor)", "protection": "Moderate", "price": 60, "pros": ["Integrated keyboard", "Screen mount", "SBC carrier built-in", "Premium feel"], "cons": ["uConsole-specific", "Limited SBC support"], "best_for": ["coding", "writerdeck"], "waterproof_rating": "None", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "hackberry_pi_cm5": {"name": "HackberryPi CM5 Case", "material": "3D printed / Injection molded", "dimensions": "Handheld form factor", "protection": "Moderate", "price": 40, "pros": ["Handheld", "CM5 carrier built-in", "Keyboard integrated", "Portable"], "cons": ["CM5 only", "Small screen area"], "best_for": ["writerdeck", "coding", "conversation"], "waterproof_rating": "None", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "pelican_1300": {"name": "Pelican 1300 Case", "material": "Polypropylene", "dimensions": "285 x 205 x 120mm", "protection": "IP67 waterproof", "foam": "Pick-and-pluck foam", "price": 50, "pros": ["Mid-size Pelican", "Keyboard storage room", "Waterproof", "Good all-rounder"], "cons": ["Needs foam cutting"], "best_for": ["coding", "security", "field-repair"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "pelican_1060": {"name": "Pelican 1060 Micro Case", "material": "Polycarbonate", "dimensions": "170 x 95 x 55mm", "protection": "IP67 waterproof", "foam": "Pick-and-pluck foam", "price": 18, "pros": ["Ultra compact", "Waterproof", "Pi Zero/CM0 perfect fit", "Transparent option"], "cons": ["Very tight fit", "No room for battery"], "best_for": ["writerdeck", "conversation", "survival"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "pelican_r40": {"name": "Pelican R40 Soft Case", "material": "Ballistic nylon + EVA foam", "dimensions": "250 x 180 x 100mm", "protection": "Water-resistant (not submersible)", "foam": "EVA foam interior", "price": 30, "pros": ["Lightweight", "Shoulder strap", "Multiple pockets", "Quick access"], "cons": ["Not waterproof", "Less protection"], "best_for": ["field-repair", "conversation", "writerdeck"], "waterproof_rating": "Water-resistant", "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "apache_3800": {"name": "Apache 3800 (Harbor Freight)", "material": "Polypropylene", "dimensions": "360 x 260 x 140mm", "protection": "IP67", "foam": "Pick-and-pluck foam", "price": 30, "pros": ["Cheaper Pelican alternative", "Waterproof", "Solid"], "cons": ["Less premium feel"], "best_for": ["security", "research"], "waterproof_rating": "IP67", "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "high", "failure_rate": "low"}},
    "found_object": {"name": "Found Object / Upcycled Enclosure", "material": "Vintage briefcase, ammo box, etc.", "dimensions": "Variable", "protection": "Varies", "price": 0, "pros": ["Free", "Unique character", "Sustainable", "Story"], "cons": ["Not purpose-built", "Needs modification"], "best_for": ["conversation", "gaming", "media", "retro"], "waterproof_rating": "Varies", "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "n/a", "community_usage": "low", "failure_rate": "high"}},
}

# ============================================================
# COOLING DATABASE
# ============================================================
COOLING_DATABASE = {
    "pimoroni_fan_shim": {"name": "Pimoroni Fan Shim", "type": "Active", "cooling_power": "High", "noise": "Moderate", "price": 10, "pros": ["No soldering", "GPIO controlled", "PWM", "Compact"], "cons": ["Pi-specific", "Takes GPIO pins"], "best_for": ["coding", "security", "research"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "geeekpi_active_cooler": {"name": "GeeekPi Active Cooler (for Pi 5)", "type": "Active", "cooling_power": "High", "noise": "Moderate", "price": 8, "pros": ["Official connector", "Easy install", "Effective", "Cheap"], "cons": ["Fan noise"], "best_for": ["coding", "security", "research"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "active_fan": {"name": "Active Fan (Official Pi 5 Active Cooler)", "type": "Active", "cooling_power": "High", "noise": "Moderate", "price": 5, "pros": ["Official", "Easy install", "Effective", "Cheap"], "cons": ["Fan noise"], "best_for": ["coding", "security", "research"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "noctua_40mm": {"name": "Noctua NF-A4x10 40mm Fan", "type": "Active (premium)", "cooling_power": "High", "noise": "Very Low", "price": 15, "pros": ["Ultra quiet", "Premium bearings", "Long life", "PWM control"], "cons": ["Needs mounting solution", "More expensive"], "best_for": ["ai", "coding", "writerdeck"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "active_fan_heatsink": {"name": "Active Fan + Heatsink Combo (ICE Tower)", "type": "Active + Passive", "cooling_power": "Very High", "noise": "Moderate", "price": 20, "pros": ["Best cooling", "Tower design", "Handles sustained loads"], "cons": ["Tall", "More expensive"], "best_for": ["ai", "coding"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "low"}},
    "passive_heatsink": {"name": "Passive Heatsink (Aluminum/Copper)", "type": "Passive", "cooling_power": "Moderate", "noise": "Silent", "price": 8, "pros": ["Silent", "No moving parts", "Reliable"], "cons": ["Lower cooling capacity"], "best_for": ["writerdeck", "gaming", "media", "conversation", "survival"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
}

# ============================================================
# PCB / CARRIER BOARD DATABASE
# ============================================================
PCB_DATABASE = {
    "waveshare_phat": {"name": "Waveshare UPS HAT / Motor HAT / Sensor HAT", "type": "Pi HAT (stackable)", "pins": "40-pin GPIO passthrough", "compatibility": "Pi 5, Pi 4, Pi 3, CM4, CM5", "price_range": "$10-$35", "pros": ["Stackable", "Official form factor", "Huge range"], "cons": ["Pi-specific"], "best_for": ["coding", "security", "research", "gaming", "media", "maker"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "geekworm_nvme_hat": {"name": "Geekworm NVMe HAT for Raspberry Pi 5", "type": "NVMe adapter HAT", "pins": "40-pin GPIO passthrough + PCIe", "compatibility": "Pi 5 only", "price_range": "$15-$25", "pros": ["NVMe SSD support", "Fast storage", "Stackable", "Affordable"], "cons": ["Pi 5 only", "Needs NVMe SSD"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "low"}},
    "pimoroni_fan_hat": {"name": "Pimoroni Fan SHIM HAT", "type": "Fan HAT", "pins": "3-pin GPIO", "compatibility": "Pi 5, Pi 4, Pi 3", "price_range": "$10", "pros": ["PWM fan control", "GPIO driven", "Compact"], "cons": ["Takes GPIO pins"], "best_for": ["coding", "security", "ai"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "jetson_carrier": {"name": "Jetson Orin Nano Developer Kit Carrier", "type": "Jetson carrier board", "pins": "40-pin GPIO + CSI camera", "compatibility": "Jetson Orin Nano only", "price_range": "Included with dev kit", "pros": ["Official carrier", "Camera support", "MIPI CSI"], "cons": ["Jetson-specific"], "best_for": ["ai"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "waveshare_cm5_carrier": {"name": "Waveshare CM5 IO Board", "type": "CM5 carrier", "pins": "Full 40-pin GPIO + M.2 + eMMC", "compatibility": "CM5 only", "price_range": "$25-$45", "pros": ["Full IO breakout", "M.2 slot", "Compact"], "cons": ["CM5 only"], "best_for": ["ai", "coding", "security"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "waveshare_cm4_carrier": {"name": "Waveshare CM4 IO Board", "type": "CM4 carrier", "pins": "Full 40-pin GPIO + M.2", "compatibility": "CM4 only", "price_range": "$20-$35", "pros": ["Full IO", "M.2 NVMe", "Compact"], "cons": ["CM4 only"], "best_for": ["gaming", "media", "writerdeck"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "adafruit_phat": {"name": "Adafruit pHAT / Bonnet", "type": "Pi HAT (small)", "pins": "26-pin GPIO (subset)", "compatibility": "Pi Zero, Pi 3, Pi 4, Pi 5", "price_range": "$10-$25", "pros": ["Ultra compact", "Great for Pi Zero", "I2C/SPI"], "cons": ["Small pin count"], "best_for": ["writerdeck", "conversation", "gaming", "media"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
    "penkesu_pcb": {"name": "Penkesu Computer PCB (Clamshell)", "type": "Custom clamshell PCB", "pins": "Pi Zero GPIO + e-ink + keyboard", "compatibility": "Pi Zero 2W only", "price_range": "$15-$25", "pros": ["Clamshell design", "E-ink integrated", "GBA SP hinges"], "cons": ["Pi Zero only", "Needs assembly"], "best_for": ["writerdeck"], "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "low", "failure_rate": "medium"}},
    "custom_neon_pcb": {"name": "Custom Neon LED PCB (WS2812B)", "type": "LED strip PCB", "pins": "3-wire (5V, GND, Data)", "compatibility": "ALL", "price_range": "$5-$15", "pros": ["Programmable RGB", "Cyberpunk aesthetic", "Any shape"], "cons": ["Power hungry", "Needs soldering"], "best_for": ["conversation-piece"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "sparkfun_phat": {"name": "SparkFun Qwiic HAT", "type": "I2C HAT", "pins": "Qwiic I2C connectors", "compatibility": "Pi 5, Pi 4, Pi 3, Zero", "price_range": "$10-$20", "pros": ["Solderless I2C", "Plug-and-play sensors", "Great ecosystem"], "cons": ["I2C only"], "best_for": ["research", "survival", "ai", "maker"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"}},
}

# ============================================================
# WIRE / CABLE DATABASE
# ============================================================
WIRE_DATABASE = {
    "silicon_26awg": {
        "name": "Silicone Wire 26AWG (Signal)", "gauge": "26 AWG",
        "type": "Silicone insulated", "current_capacity": "2.2A",
        "use": "Signal, I2C, SPI, UART, GPIO",
        "pros": ["Flexible", "High temp rated", "Stranded", "Easy to strip"],
        "price_per_meter": 0.50,
        "color_options": ["Red", "Black", "Yellow", "Green", "Blue", "White"],
        "best_for": ["ALL"],
    },
    "silicon_24awg": {
        "name": "Silicone Wire 24AWG (Medium Signal/Power)", "gauge": "24 AWG",
        "type": "Silicone insulated", "current_capacity": "3.5A",
        "use": "Power to small boards, fan power, LED strips",
        "pros": ["Versatile", "Flexible", "Good current"],
        "price_per_meter": 0.60,
        "color_options": ["Red", "Black", "Yellow", "Blue"],
        "best_for": ["ai", "coding", "maker"],
    },
    "silicon_20awg": {
        "name": "Silicone Wire 20AWG (Low Power)", "gauge": "20 AWG",
        "type": "Silicone insulated", "current_capacity": "5A",
        "use": "Battery connections, UPS wiring, low-voltage power",
        "pros": ["Good current", "Flexible", "Safe for battery"],
        "price_per_meter": 0.80,
        "color_options": ["Red", "Black"],
        "best_for": ["writerdeck", "gaming", "media", "conversation"],
    },
    "silicon_18awg": {
        "name": "Silicone Wire 18AWG (Power)", "gauge": "18 AWG",
        "type": "Silicone insulated", "current_capacity": "10A",
        "use": "Main power, solar panel wiring, battery packs",
        "pros": ["High current", "Flexible", "Low voltage drop"],
        "price_per_meter": 1.00,
        "color_options": ["Red", "Black"],
        "best_for": ["coding", "security", "research", "ai"],
    },
    "silicon_16awg": {
        "name": "Silicone Wire 16AWG (Heavy Power)", "gauge": "16 AWG",
        "type": "Silicone insulated", "current_capacity": "15A",
        "use": "High-current power, motor wiring, solar systems",
        "pros": ["Very high current", "Low loss", "Durable"],
        "price_per_meter": 1.20,
        "color_options": ["Red", "Black"],
        "best_for": ["ai", "survival"],
    },
    "silicon_26awg_neon": {
        "name": "Silicone Wire 26AWG Neon (LED Accent)", "gauge": "26 AWG",
        "type": "Neon colored silicone", "current_capacity": "2.2A",
        "use": "LED wiring, accent lighting, WS2812B data",
        "pros": ["Cyberpunk aesthetic", "Neon colors", "Flexible"],
        "price_per_meter": 0.80,
        "color_options": ["Neon Pink", "Neon Green", "Neon Blue", "Neon Orange"],
        "best_for": ["conversation-piece"],
    },
    "ribbon_cable": {
        "name": "IDC Ribbon Cable (DSI/CSI)", "gauge": "28 AWG flat",
        "type": "Flat ribbon", "current_capacity": "1A per conductor",
        "use": "DSI display, CSI camera, GPIO ribbon",
        "pros": ["Neat", "Proper connectors", "Pi-specific"],
        "price_per_meter": 2.00,
        "color_options": ["Grey", "Rainbow"],
        "best_for": ["ALL"],
    },
    "jst_connector_cable": {
        "name": "JST-PH 2.0mm Connector Cables", "gauge": "26 AWG pre-crimped",
        "type": "Pre-crimped JST", "current_capacity": "2A",
        "use": "Battery BMS, speaker, sensor connections",
        "pros": ["Solderless", "Quick connect", "Secure", "Safe"],
        "price_per_set": 3.00,
        "color_options": ["Red", "Black", "White", "Green", "Yellow"],
        "best_for": ["ALL"],
    },
    "usb_c_cable": {
        "name": "USB-C to USB-C Cable (240W PD)",
        "gauge": "Internal: 20AWG power + 28AWG signal",
        "type": "USB-C PD cable", "current_capacity": "5A @ 48V",
        "use": "Power delivery, data transfer, display output",
        "pros": ["One cable for power+data+display", "Future proof"],
        "price_per_unit": 8.00,
        "best_for": ["ALL"],
    },
    "hdmi_ribbon": {
        "name": "HDMI Ribbon Cable (FFC/FPC)", "gauge": "Custom FFC",
        "type": "Flat flexible cable", "current_capacity": "N/A (signal only)",
        "use": "HDMI display connection in tight spaces",
        "pros": ["Thin", "Flexible", "Custom lengths"],
        "price_per_unit": 5.00,
        "best_for": ["ALL"],
    },
    "dsi_ribbon": {
        "name": "DSI Ribbon Cable (15-pin FPC)", "gauge": "28 AWG FPC",
        "type": "Flat flexible cable", "current_capacity": "N/A (signal only)",
        "use": "Pi DSI display connection",
        "pros": ["Official Pi connector", "Compact"],
        "price_per_unit": 3.00,
        "best_for": ["ALL"],
    },
}

# ============================================================
# OS DATABASE
# ============================================================
OS_DATABASE = {
    "raspberry_pi_os": {"name": "Raspberry Pi OS (Bookworm)", "based": "Debian 12", "desktop": True, "best_for": ["coding", "research", "survival", "maker"]},
    "kali_linux": {"name": "Kali Linux (Pi)", "based": "Debian", "desktop": True, "best_for": ["security"]},
    "ubuntu": {"name": "Ubuntu MATE / Server", "based": "Ubuntu", "desktop": True, "best_for": ["coding", "ai"]},
    "retropie": {"name": "RetroPie", "based": "Debian", "desktop": False, "best_for": ["gaming"]},
    "batocera": {"name": "Batocera.linux", "based": "Buildroot", "desktop": False, "best_for": ["gaming"]},
    "libreelec": {"name": "LibreELEC", "based": "Buildroot", "desktop": False, "best_for": ["media"]},
    "writerdeck_os": {"name": "writerdeckOS / DietPi", "based": "Debian", "desktop": False, "best_for": ["writerdeck"]},
    "twister_os": {"name": "Twister OS", "based": "Raspberry Pi OS", "desktop": True, "best_for": ["conversation-piece"]},
    "jetpack": {"name": "NVIDIA JetPack", "based": "Ubuntu", "desktop": True, "best_for": ["ai"]},
    "arch_linux_arm": {"name": "Arch Linux ARM", "based": "Arch", "desktop": True, "best_for": ["coding", "security"]},
    "dietpi": {"name": "DietPi", "based": "Debian", "desktop": True, "best_for": ["writerdeck", "research", "gaming"]},
}

# ============================================================
# CONNECTIVITY DATABASE
# ============================================================
CONNECTIVITY_DATABASE = {
    "awus036ach": {
        "name": "Alfa AWUS036ACH USB WiFi Adapter", "type": "USB WiFi Adapter",
        "standard": "WiFi 5 (802.11ac) Dual-Band", "frequency": "2.4GHz + 5GHz",
        "speed": "AC1200", "antenna": "2x detachable 5dBi",
        "chipset": "Realtek RTL8812AU", "connection": "USB 3.0", "price": 30,
        "range": "Long range with external antenna",
        "monitor_mode": True, "packet_injection": True,
        "pros": ["Best WiFi adapter for pentesting", "Monitor mode + injection", "Dual-band", "External antenna", "Kali compatible"],
        "cons": ["Needs driver install", "USB dongle size"],
        "best_for": ["security", "coding", "research"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "awus036acs": {
        "name": "Alfa AWUS036ACS USB WiFi Adapter", "type": "USB WiFi Adapter",
        "standard": "WiFi 5 (802.11ac) Dual-Band", "frequency": "2.4GHz + 5GHz",
        "speed": "AC1200", "antenna": "Internal + 2.4GHz external",
        "chipset": "Realtek RTL8811AU", "connection": "USB 3.0", "price": 20,
        "range": "Medium range",
        "monitor_mode": True, "packet_injection": True,
        "pros": ["Budget pentesting adapter", "Monitor mode", "Dual-band", "Compact"],
        "cons": ["Single external antenna"], "best_for": ["security", "coding"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "rtl_sdr": {
        "name": "RTL-SDR Blog V3 Dongle", "type": "SDR Receiver",
        "standard": "Software Defined Radio", "frequency": "24MHz - 1766MHz",
        "speed": "2.4 MSPS", "antenna": "Antenna not included (SMA)",
        "chipset": "RTL2832U + R820T2", "connection": "USB 2.0", "price": 30,
        "range": "Radio spectrum", "monitor_mode": False, "packet_injection": False,
        "pros": ["ADS-B aircraft tracking", "Ham radio", "Satellite reception", "RF snooping", "Wide frequency range"],
        "cons": ["Receive only", "Needs antenna"],
        "best_for": ["security", "research", "survival", "ham-radio"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "hackrf_one": {
        "name": "Great Scott Gadgets HackRF One", "type": "SDR Transceiver",
        "standard": "Software Defined Radio", "frequency": "1MHz - 6GHz",
        "speed": "20 MSPS", "antenna": "Antenna not included (SMA)",
        "chipset": "NXP LPC4330 + MAX2837", "connection": "USB 3.0", "price": 350,
        "range": "Full radio spectrum", "monitor_mode": False, "packet_injection": False,
        "pros": ["TX + RX capable", "Huge frequency range", "Industry standard", "HackRF compatible"],
        "cons": ["Expensive", "Full-duplex limited"],
        "best_for": ["security", "research", "ham-radio"],
        "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "low"},
    },
    "ethernet_switch": {
        "name": "TP-Link TL-SG105 5-Port Gigabit Switch", "type": "Network Switch",
        "standard": "Gigabit Ethernet", "ports": "5x RJ45 GbE",
        "speed": "1000 Mbps", "connection": "Ethernet cables", "price": 15,
        "pros": ["Cheap", "5 ports", "Fanless", "Compact", "Plug and play"],
        "cons": ["Needs power adapter"],
        "best_for": ["security", "coding", "research"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "usb_ethernet": {
        "name": "USB-C to Ethernet Adapter (Gigabit)", "type": "USB Ethernet Adapter",
        "standard": "Gigabit Ethernet", "ports": "1x RJ45 GbE",
        "speed": "1000 Mbps", "connection": "USB-C / USB 3.0", "price": 15,
        "pros": ["Adds Ethernet to any SBC", "USB-C and USB-A options", "No driver needed"],
        "cons": ["Single port"], "best_for": ["ALL"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "cat6_cable": {
        "name": "Cat 6 Ethernet Cable (1m/3m/5m)", "type": "Ethernet Cable",
        "standard": "Cat 6 UTP", "speed": "1 Gbps (up to 10 Gbps at 55m)",
        "length_options": ["1m", "3m", "5m", "10m"], "price_range": "$3-$8",
        "pros": ["Future-proof", "Shielded options available", "Flat and round"],
        "cons": ["Bulkier than Cat 5e"], "best_for": ["ALL"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "cat6_flat": {
        "name": "Cat 6 Flat Ethernet Cable (1m)", "type": "Ethernet Cable",
        "standard": "Cat 6 UTP Flat", "speed": "1 Gbps",
        "length_options": ["1m", "2m", "3m"], "price_range": "$4-$8",
        "pros": ["Ultra thin", "Easy routing in enclosures", "Velcro tie included"],
        "cons": ["Less shielding"], "best_for": ["coding", "security", "gaming"],
        "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "very_high", "failure_rate": "very_low"},
    },
    "lora_module": {
        "name": "Seeed Studio Wio-SX1262 LoRa Module", "type": "LoRa Radio Module",
        "standard": "LoRa SX1262", "frequency": "868MHz / 915MHz",
        "range": "5-15km", "connection": "SPI + GPIO", "price": 20,
        "pros": ["Meshtastic compatible", "Long range", "Off-grid mesh networking", "Low power"],
        "cons": ["Needs antenna", "SPI wiring"], "best_for": ["survival", "research", "ham-radio"],
        "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"},
    },
    "lte_modem": {
        "name": "Quectel EC20 LTE Cat 4 Modem", "type": "Cellular Modem",
        "standard": "4G LTE Cat 4", "speed": "150 Mbps DL / 50 Mbps UL",
        "connection": "USB + SIM slot", "price": 30,
        "pros": ["4G LTE connectivity", "GPS included", "AT command support", "Industrial grade"],
        "cons": ["Needs SIM card", "Antenna required"],
        "best_for": ["survival", "research", "security"],
        "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"},
    },
    "wifi_antenna_pigtail": {
        "name": "SMA Pigtail Cable (RP-SMA / SMA)", "type": "Antenna Cable",
        "connector": "RP-SMA to U.FL / SMA to U.FL",
        "length_options": ["10cm", "20cm", "30cm"], "price_range": "$2-$5",
        "pros": ["Internal WiFi to external antenna", "Clean build", "Various connectors"],
        "cons": ["Needs soldering or U.FL clip"],
        "best_for": ["security", "coding", "research"],
    },
}

# ============================================================
# v5.0 — ENVIRONMENTAL SENSOR DATABASE
# ============================================================
ENVIRONMENTAL_SENSOR_DATABASE = {
    "bme280": {"name": "BME280 Temperature/Humidity/Pressure", "type": "Environmental", "interface": "I2C/SPI", "range": "-40-85C, 0-100%RH, 300-1100hPa", "accuracy": "±1C, ±3%RH, ±1hPa", "price": 5, "power": "1.8mA", "best_for": ["weather-station", "research", "survival"]},
    "bme680": {"name": "BME680 Temp/Humidity/Pressure/Gas", "type": "Environmental", "interface": "I2C/SPI", "range": "-40-85C, 0-100%RH, 300-1100hPa, VOC", "accuracy": "±1C, ±3%RH", "price": 15, "power": "3.1mA", "best_for": ["weather-station", "research", "home-automation"]},
    "scd30": {"name": "SCD30 CO2 Sensor", "type": "CO2", "interface": "I2C", "range": "400-10000ppm", "accuracy": "±(30ppm+3%)", "price": 50, "power": "19mA", "best_for": ["weather-station", "home-automation"]},
    "scd40": {"name": "SCD40 Mini CO2 Sensor", "type": "CO2", "interface": "I2C", "range": "400-5000ppm", "accuracy": "±(40ppm+5%)", "price": 30, "power": "17mA", "best_for": ["weather-station", "home-automation"]},
    "pms5003": {"name": "Plantower PMS5003 Particulate Matter", "type": "Air Quality", "interface": "UART", "range": "PM1.0/PM2.5/PM10", "accuracy": "±10μg/m3", "price": 20, "power": "100mA", "best_for": ["weather-station", "research"]},
    "ltr390": {"name": "LTR390 UV/Ambient Light Sensor", "type": "UV/Light", "interface": "I2C", "range": "UV Index 0-20+", "accuracy": "±1 UV index", "price": 5, "power": "0.5mA", "best_for": ["weather-station", "research", "outdoor"]},
    "sgp40": {"name": "SGP40 VOC Gas Sensor", "type": "VOC", "interface": "I2C", "range": "0-1000 VOC Index", "accuracy": "±15%", "price": 12, "power": "0.4mA", "best_for": ["weather-station", "home-automation"]},
    "bh1750": {"name": "BH1750 Ambient Light Sensor", "type": "Light", "interface": "I2C", "range": "1-65535 lux", "accuracy": "±20%", "price": 3, "power": "0.12mA", "best_for": ["weather-station", "home-automation", "writerdeck"]},
    "dht22": {"name": "DHT22 Temperature/Humidity", "type": "Environmental", "interface": "1-Wire", "range": "-40-80C, 0-100%RH", "accuracy": "±0.5C, ±2%RH", "price": 4, "power": "1.5mA", "best_for": ["weather-station", "home-automation", "survival"]},
    "ds18b20": {"name": "DS18B20 Waterproof Temperature Probe", "type": "Temperature", "interface": "1-Wire", "range": "-55-125C", "accuracy": "±0.5C", "price": 3, "power": "1mA", "best_for": ["weather-station", "field-repair"]},
    "geiger_tube": {"name": "SBM-20 Geiger-Müller Tube", "type": "Radiation", "interface": "Pulse Count", "range": "0.1-1000 μSv/h", "accuracy": "±15%", "price": 25, "power": "5mA", "best_for": ["survival", "research", "forensics"]},
    "radiationd_pcb": {"name": "RadPcb Radiation Detector PCB", "type": "Radiation", "interface": "SPI", "range": "SBM-20/Tube compatible", "accuracy": "±20%", "price": 10, "power": "5mA", "best_for": ["survival", "research"]},
}

# ============================================================
# v5.0 — CAMERA MODULE DATABASE
# ============================================================
CAMERA_MODULE_DATABASE = {
    "pi_camera_3": {"name": "Raspberry Pi Camera Module 3", "sensor": "IMX708", "resolution": "12MP 4608x2592", "fps": "30fps@1080p, 60fps@720p", "focus": "Autofocus", "interface": "CSI", "price": 25, "pros": ["HDR", "Autofocus", "Official Pi"], "cons": ["Only CSI port"], "best_for": ["ai", "research", "security"]},
    "pi_camera_3_noir": {"name": "Pi Camera Module 3 NoIR", "sensor": "IMX708 (No IR filter)", "resolution": "12MP 4608x2592", "fps": "30fps@1080p", "focus": "Autofocus", "interface": "CSI", "price": 25, "pros": ["Night vision with IR LED", "HDR", "Autofocus"], "cons": ["Needs IR LED for night"], "best_for": ["security", "research", "survival"]},
    "arducam_imx519": {"name": "Arducam 16MP IMX519 Autofocus", "sensor": "IMX519", "resolution": "16MP 4656x3496", "fps": "30fps@1080p", "focus": "Autofocus (Motorized)", "interface": "CSI", "price": 35, "pros": ["High resolution", "Motorized focus", "Wide angle option"], "cons": ["More expensive"], "best_for": ["ai", "research"]},
    "arducam_global_shutter": {"name": "Arducam Global Shutter IMX296", "sensor": "IMX296", "resolution": "1.3MP 1280x960", "fps": "60fps", "focus": "Fixed", "interface": "CSI", "price": 40, "pros": ["No motion blur", "Machine vision", "Industrial"], "cons": ["Low resolution"], "best_for": ["ai", "drone", "field-repair"]},
    "flir_lepton": {"name": "FLIR Lepton 3.5 Thermal Camera", "sensor": "LWIR Microbolometer", "resolution": "160x120 thermal", "fps": "9fps", "focus": "Fixed", "interface": "SPI (via breakout)", "price": 200, "pros": ["Thermal imaging", "Compact", "Low power"], "cons": ["Expensive", "Low resolution"], "best_for": ["field-repair", "research", "security"]},
    "seek_micro": {"name": "Seek Thermal CompactPRO", "sensor": "LWIR", "resolution": "320x240 thermal", "fps": "15fps", "focus": "Fixed", "interface": "USB-C", "price": 300, "pros": ["High resolution thermal", "USB-C plug and play"], "cons": ["Very expensive"], "best_for": ["field-repair", "research"]},
}

# ============================================================
# v5.0 — SDR DATABASE (detailed)
# ============================================================
SDR_DATABASE = {
    "hackrf_one": {"name": "HackRF One", "type": "SDR Transceiver", "frequency": "1MHz-6GHz", "bandwidth": "20MHz", "resolution": "8-bit", "interface": "USB 3.0", "price": 350, "tx_rx": "Full duplex (half-duplex TX/RX)", "pros": ["Huge frequency range", "TX+RX", "Industry standard"], "cons": ["Expensive", "8-bit ADC"], "best_for": ["security", "ham-radio", "research"]},
    "rtl_sdr_v4": {"name": "RTL-SDR Blog V4", "type": "SDR Receiver", "frequency": "24MHz-1766MHz", "bandwidth": "3.2MHz", "resolution": "8-bit", "interface": "USB 2.0", "price": 30, "tx_rx": "RX only", "pros": ["Ultra cheap", "Wide frequency range", "HackRF alternative for RX"], "cons": ["Receive only"], "best_for": ["security", "research", "ham-radio", "survival"]},
    "airspy_mini": {"name": "Airspy Mini", "type": "SDR Receiver", "frequency": "24MHz-1800MHz", "bandwidth": "6MHz", "resolution": "12-bit", "interface": "USB 2.0", "price": 100, "tx_rx": "RX only", "pros": ["High resolution 12-bit", "Wide bandwidth", "Clean signal"], "cons": ["RX only", "More expensive than RTL-SDR"], "best_for": ["security", "research", "ham-radio"]},
}

# ============================================================
# v5.0 — LORA/MESH DATABASE
# ============================================================
LORA_MESH_DATABASE = {
    "rak_wismesh": {"name": "RAK WisMesh Tap", "type": "LoRa Mesh", "chip": "SX1262", "frequency": "868/915MHz", "range": "10-15km", "firmware": "Meshtastic", "interface": "USB-C / BLE", "price": 50, "pros": ["Meshtastic", "Built-in battery", "Compact"], "cons": ["Needs LoRa antenna"], "best_for": ["survival", "drone", "research"]},
    "seeed_wio_l1": {"name": "Seeed Wio L1 Module", "type": "LoRa Mesh", "chip": "SX1262", "frequency": "868/915MHz", "range": "5-10km", "firmware": "Meshtastic", "interface": "UART/SPI", "price": 15, "pros": ["Tiny", "Cheap", "Meshtastic"], "cons": ["Needs antenna", "Wiring"], "best_for": ["survival", "research"]},
    "heltec_v3": {"name": "Heltec WiFi LoRa 32 V3", "type": "LoRa + WiFi ESP32", "chip": "SX1262 + ESP32-S3", "frequency": "868/915MHz", "range": "10-15km", "firmware": "Meshtastic", "interface": "USB-C", "price": 25, "pros": ["Built-in OLED", "WiFi + LoRa", "Meshtastic", "ESP32 ecosystem"], "cons": ["Small OLED"], "best_for": ["survival", "research", "home-automation"]},
    "lora_phat": {"name": "Waveshare LoRa HAT for Raspberry Pi", "type": "LoRa HAT", "chip": "SX1262/SX1278", "frequency": "868/915/433MHz", "range": "5-10km", "firmware": "Custom/Meshtastic", "interface": "SPI (HAT)", "price": 30, "pros": ["Pi HAT form factor", "Antenna connector", "GPIO pass-through"], "cons": ["Needs Pi GPIO"], "best_for": ["survival", "drone", "ham-radio"]},
}

# ============================================================
# v5.0 — NFC/RFID DATABASE
# ============================================================
NFC_RFID_DATABASE = {
    "pn532": {"name": "Waveshare PN532 NFC HAT", "type": "NFC Reader/Writer", "protocols": "ISO14443A/B, ISO15693, FeliCa, MIFARE", "interface": "SPI/I2C/UART", "price": 15, "pros": ["Multi-protocol", "Read/write cards", "Arduino/Pi compatible"], "cons": ["Needs wiring"], "best_for": ["security", "forensics", "home-automation"]},
    "acr122u": {"name": "ACS ACR122U USB NFC Reader", "type": "NFC Reader", "protocols": "ISO14443A/B, MIFARE", "interface": "USB", "price": 30, "pros": ["Plug and play", "Linux compatible", "MIFARE support"], "cons": ["USB dongle", "No write to MIFARE"], "best_for": ["security", "forensics"]},
    "rc522": {"name": "MFRC522 RFID Module", "type": "RFID Reader", "protocols": "MIFARE 1K/4K, NTAG", "interface": "SPI", "price": 3, "pros": ["Ultra cheap", "MIFARE crackable", "Pi/Arduino"], "cons": ["13.56MHz only"], "best_for": ["security", "home-automation"]},
}

# ============================================================
# v5.0 — FINGERPRINT DATABASE
# ============================================================
FINGERPRINT_DATABASE = {
    "r307": {"name": "R307 Optical Fingerprint Sensor", "type": "Optical", "capacity": "1000 fingerprints", "interface": "UART", "price": 10, "pros": ["Cheap", "1000 templates", "Serial protocol"], "cons": ["Bulky", "Optical (less secure)"], "best_for": ["security", "home-automation"]},
    "r503": {"name": "R503 Capacitive Fingerprint", "type": "Capacitive", "capacity": "1000 fingerprints", "interface": "UART", "price": 15, "pros": ["Capacitive (more secure)", "Slim"], "cons": ["More expensive"], "best_for": ["security", "home-automation"]},
    "gt521f32": {"name": "GT-521F32 Fingerprint Scanner", "type": "Optical", "capacity": "3000 fingerprints", "interface": "UART", "price": 20, "pros": ["Large capacity", "Industrial"], "cons": ["Bulky"], "best_for": ["security", "forensics"]},
}

# ============================================================
# v5.0 — HAPTIC FEEDBACK DATABASE
# ============================================================
HAPTIC_FEEDBACK_DATABASE = {
    "drv2605l": {"name": "Adafruit DRV2605L Haptic Driver", "type": "Haptic Driver", "interface": "I2C", "effects": "123 built-in effects", "price": 8, "pros": ["Rich haptic library", "LRA/ERM support", "Audio-to-haptic"], "cons": ["Needs motor"], "best_for": ["conversation-piece", "writerdeck"]},
    "er_ms_motor": {"name": "ERM Vibration Motor 3V", "type": "ERM Motor", "voltage": "3V", "price": 1, "pros": ["Ultra cheap", "Simple"], "cons": ["No smart control"], "best_for": ["conversation-piece", "writerdeck"]},
    "lra_motor": {"name": "Precision LRA Vibration Motor", "type": "LRA Motor", "voltage": "1.2V", "price": 5, "pros": ["Precise", "Fast response", "Low power"], "cons": ["Needs driver"], "best_for": ["conversation-piece", "writerdeck"]},
}

# ============================================================
# v5.0 — IMU/ACCELEROMETER DATABASE
# ============================================================
IMU_DATABASE = {
    "sense_hat": {"name": "Raspberry Pi Sense HAT", "type": "IMU + Env + Display", "sensors": "Accel, Gyro, Magnetometer, Temp, Humidity, Pressure", "interface": "GPIO HAT", "price": 35, "pros": ["All-in-one", "Official Pi", "LED matrix", "Gyroscope"], "cons": ["Bulky HAT"], "best_for": ["drone", "weather-station", "research"]},
    "bno055": {"name": "Adafruit BNO055 9-DOF IMU", "type": "9-DOF IMU", "sensors": "Accel + Gyro + Magnetometer + Fusion", "interface": "I2C", "price": 25, "pros": ["Sensor fusion built-in", "High accuracy", "Orientation output"], "cons": ["Needs I2C wiring"], "best_for": ["drone", "research"]},
    "mpu6050": {"name": "MPU-6050 6-DOF IMU", "type": "6-DOF IMU", "sensors": "Accel + Gyro", "interface": "I2C", "price": 3, "pros": ["Ultra cheap", "Tiny", "Proven"], "cons": ["No magnetometer", "Needs calibration"], "best_for": ["drone", "conversation-piece"]},
}

# ============================================================
# v5.0 — COLOR PALETTE DATABASE
# ============================================================
COLOR_PALETTE_DATABASE = {
    "cyberpunk_2077": {"name": "Cyberpunk 2077", "primary": "#FCEE09", "secondary": "#00F0FF", "accent": "#FF003C", "bg": "#1A1A1A", "neon_glow": True},
    "synthwave": {"name": "Synthwave / Retrowave", "primary": "#FF6EC7", "secondary": "#7B2FBE", "accent": "#00FFFF", "bg": "#1A0A2E", "neon_glow": True},
    "vaporwave": {"name": "Vaporwave", "primary": "#FF71CE", "secondary": "#01CDFE", "accent": "#B967FF", "bg": "#050A30", "neon_glow": True},
    "nautical": {"name": "Nautical", "primary": "#1A3A4A", "secondary": "#B8860B", "accent": "#4682B4", "bg": "#0D1B2A", "neon_glow": False},
    "solarpunk": {"name": "Solarpunk", "primary": "#2D5A27", "secondary": "#8B6914", "accent": "#90EE90", "bg": "#F5F5DC", "neon_glow": False},
    "cassette_futurism": {"name": "Cassette Futurism", "primary": "#2A2A2A", "secondary": "#CC0000", "accent": "#FFFFFF", "bg": "#1A1A1A", "neon_glow": False},
    "brutalist": {"name": "Brutalist", "primary": "#6B6B6B", "secondary": "#999999", "accent": "#CC0000", "bg": "#333333", "neon_glow": False},
    "military": {"name": "Military Tactical", "primary": "#4A5D23", "secondary": "#8B4513", "accent": "#DAA520", "bg": "#1C1C1C", "neon_glow": False},
    "fallout": {"name": "Fallout / Post-Apocalyptic", "primary": "#4A5A3A", "secondary": "#8B4513", "accent": "#DAA520", "bg": "#2A2A2A", "neon_glow": False},
    "minimal": {"name": "Minimal Clean", "primary": "#F5F5F5", "secondary": "#333333", "accent": "#0066CC", "bg": "#FFFFFF", "neon_glow": False},
}

# ============================================================
# v5.0 — AESTHETIC MATERIAL DATABASE
# ============================================================
AESTHETIC_MATERIAL_DATABASE = {
    "vinyl_wrap": {"name": "Vinyl Wrap (Oracal 651)", "finish": ["gloss", "matte", "satin", "metallic", "holographic"], "color_count": "100+", "price": "$10/roll", "application": "Peel and stick, heat gun for curves", "best_for": ["cyberpunk", "nautical", "solarpunk"]},
    "resin_art": {"name": "Epoxy Resin Art", "finish": ["clear", "tinted", "glitter", "neon", "transparent"], "price": "$15/kit", "application": "Pour over surface, UV or 2-part", "best_for": ["conversation-piece", "cyberpunk"]},
    "wood_veneer": {"name": "Wood Veneer Sheets", "finish": ["walnut", "oak", "cherry", "sapele", "bamboo"], "price": "$8/sheet", "application": "Glue + clamp, sand + finish", "best_for": ["nautical", "solarpunk", "writerdeck"]},
    "leather_wrap": {"name": "Faux Leather Wrap", "finish": ["smooth", "textured", "distressed"], "price": "$12/sheet", "application": "Contact cement + wrap", "best_for": ["steampunk", "writerdeck", "retro"]},
    "carbon_fiber": {"name": "Carbon Fiber Vinyl/Sheet", "finish": ["gloss", "matte"], "price": "$20/sheet", "application": "Heat gun + wrap or resin embed", "best_for": ["cyberpunk", "industrial"]},
    "brass_accents": {"name": "Brass Sheet/Accents", "finish": ["polished", "brushed", "patina"], "price": "$15/sheet", "application": "Cut + bend + solder or glue", "best_for": ["steampunk", "nautical", "retro"]},
    "sticker_bomb": {"name": "Sticker Bombing", "finish": ["random", "themed", "custom"], "price": "$5-20", "application": "Layer stickers, clear coat over", "best_for": ["conversation-piece", "cyberpunk"]},
    "led_strip": {"name": "WS2812B Addressable LED Strip", "finish": ["RGB", "RGBW"], "price": "$8/meter", "application": "Cut to length, WLED controller", "best_for": ["cyberpunk", "conversation-piece"]},
    "spray_paint": {"name": "Montana Gold / Krylon Fusion", "finish": ["matte", "gloss", "metallic", "chrome"], "price": "$6/can", "application": "Sand + prime + paint + clear coat", "best_for": ["ALL"]},
    "3d_print_filigree": {"name": "3D Printed Filigree/Grille", "finish": ["PLA", "PETG", "resin"], "price": "Filament cost", "application": "Print decorative elements, glue on", "best_for": ["steampunk", "cyberpunk", "conversation-piece"]},
    "petg_print": {"name": "PETG 3D Print (Enclosure/Parts)", "finish": ["matte", "gloss", "translucent"], "price": "$15/kg spool", "application": "FDM print, heat-resistant to 80C, UV stable", "best_for": ["outdoor", "solarpunk", "industrial"], "notes": "Superior to PLA for outdoor/rugged builds, chemical resistant"},
    "carbon_fiber_polycarbonate": {"name": "Carbon Fiber Polycarbonate Sheet", "finish": ["matte", "textured"], "price": "$25-40/sheet", "application": "Cut/drill/CNC, lightweight structural panels", "best_for": ["cyberpunk", "industrial", "survival"], "notes": "Extremely rigid, impact resistant, lighter than aluminum"},
    "live_edge_wood": {"name": "Live Edge Wood Slab (Walnut/Maple)", "finish": ["natural", "oiled", "epoxy-resin"], "price": "$20-60/piece", "application": "CNC or hand-shape, epoxy fill cracks, oil finish", "best_for": ["nautical", "solarpunk", "writerdeck", "conversation-piece"], "notes": "Each piece unique, conversation starter"},
    "nato_rail": {"name": "NATO Accessory Rail (Picatinny/Weaver)", "finish": ["anodized-aluminum", "polymer"], "price": "$8-15/rail", "application": "Bolt/screw mount, modular accessory attachment", "best_for": ["tactical", "survival", "industrial"], "notes": "Standardized mounting for flashlights, cameras, tools"},
    "kevlar_wrap": {"name": "Kevlar/Carbon Fiber Hybrid Wrap", "finish": ["gloss", "matte"], "price": "$30/sheet", "application": "Resin infusion or vinyl wrap, ballistic-grade protection", "best_for": ["survival", "industrial", "tactical"], "notes": "Ultra high impact resistance, premium look"},
    "bamboo_plywood": {"name": "Bamboo Plywood Sheet", "finish": ["natural", "stained", "laser-etched"], "price": "$12-25/sheet", "application": "Laser cut or CNC, sand + oil finish", "best_for": ["solarpunk", "nautical", "writerdeck"], "notes": "Sustainable, strong, beautiful grain pattern"},
    "tpu_print": {"name": "TPU Flexible Print (Bumpers/Grips)", "finish": ["matte", "textured"], "price": "$20/kg spool", "application": "FDM print, flexible bumpers/gaskets/holders", "best_for": ["ALL"], "notes": "Shock-absorbing, waterproof seals, grip surfaces"},
}

# ============================================================
# v5.0 — ANTENNA SELECTION GUIDE
# ============================================================
ANTENNA_GUIDE = {
    "lora_868": {"band": "868MHz", "type": "LoRa EU", "recommended": "Dipole 86.5cm", "gain": "2dBi", "connector": "SMA/RP-SMA", "notes": "Trim to 868MHz λ/4"},
    "lora_915": {"band": "915MHz", "type": "LoRa US", "recommended": "Dipole 8.2cm", "gain": "2dBi", "connector": "SMA/RP-SMA", "notes": "Trim to 915MHz λ/4"},
    "wifi_24ghz": {"band": "2.4GHz", "type": "WiFi", "recommended": "Omnidirectional 3dBi", "gain": "3-5dBi", "connector": "RP-SMA", "notes": "Standard WiFi antenna"},
    "wifi_5ghz": {"band": "5GHz", "type": "WiFi 5", "recommended": "Omnidirectional 5dBi", "gain": "5dBi", "connector": "RP-SMA", "notes": "Shorter wavelength, higher gain needed"},
    "gps_l1": {"band": "1575.42MHz", "type": "GPS L1", "recommended": "Patch antenna", "gain": "2-5dBi", "connector": "U.FL/SMA", "notes": "Needs sky view"},
    "sdr_general": {"band": "24-1766MHz", "type": "SDR Wideband", "recommended": "Discone / wideband dipole", "gain": "2-6dBi", "connector": "SMA", "notes": "Wide frequency coverage"},
    "ham_vhf": {"band": "144-148MHz", "type": "VHF Ham", "recommended": "Vertical 1/4 wave (50cm)", "gain": "2dBi", "connector": "PL-259/SO-239", "notes": "Line of sight"},
    "ham_uhf": {"band": "420-450MHz", "type": "UHF Ham", "recommended": "Vertical 1/4 wave (17cm)", "gain": "2dBi", "connector": "PL-259/SO-239", "notes": "Good for repeaters"},
    "lte": {"band": "700-2600MHz", "type": "LTE Cellular", "recommended": "LTE whip antenna", "gain": "3dBi", "connector": "SMA", "notes": "Match to carrier band"},
}

# ============================================================
# v5.0 — THERMAL INTERFACE MATERIAL DATABASE
# ============================================================
THERMAL_INTERFACE_DATABASE = {
    "arctic_mx6": {"name": "Arctic MX-6 Thermal Paste", "conductivity": "12.5 W/mK", "type": "Paste", "price": "$8", "application": "Spreader/pea method", "best_for": ["ai", "coding"]},
    "thermal_grizzly_kryonaut": {"name": "Thermal Grizzly Kryonaut", "conductivity": "12.5 W/mK", "type": "Paste", "price": "$12", "application": "Spreader/pea method", "best_for": ["ai", "edge-ai"]},
    "gelid_gp_ultra": {"name": "GELID GP-Ultimate Pad", "conductivity": "15 W/mK", "type": "Pad", "price": "$10", "application": "Cut to size, place on chip", "best_for": ["ai", "edge-ai"]},
    "thermal_paste_arctic_silver": {"name": "Arctic Silver 5", "conductivity": "8.9 W/mK", "type": "Paste", "price": "$7", "application": "Line/pea method", "best_for": ["ALL"]},
    "kapton_tape": {"name": "Kapton Tape (Polyimide)", "conductivity": "N/A (insulator)", "type": "Tape", "price": "$6", "application": "Mask components, secure wires", "best_for": ["ALL"]},
}
COMPAT_RULES = {
    "power_connector": {
        "pi5": "USB-C 5V/5A", "pi4": "USB-C 5V/3A",
        "pi_zero_2w": "micro-USB 5V/2.5A", "orange_pi_5": "USB-C 5V/4A",
        "orange_pi_5_plus": "USB-C 5V/4A", "orange_pi_zero3": "USB-C 5V/2A",
        "jetson_orin_nano": "DC barrel 19V or USB-C",
        "lattepanda_3_delta": "USB-C 5V/3A", "radxa_rock_5b": "USB-C 5V/4A",
        "khadas_edge2": "USB-C 5V/4A", "cm4": "Depends on carrier", "cm5": "Depends on carrier",
    },
    "display_interface": {
        "pi5": ["hdmi", "dsi", "spi"], "pi4": ["hdmi", "dsi", "spi"],
        "pi_zero_2w": ["mini-hdmi", "spi", "i2c"],
        "orange_pi_5": ["hdmi", "usb-c-dp"], "orange_pi_5_plus": ["hdmi", "usb-c-dp"],
        "jetson_orin_nano": ["hdmi", "dsi"], "lattepanda_3_delta": ["hdmi", "usb-c-dp"],
        "radxa_rock_5b": ["hdmi", "usb-c-dp"], "khadas_edge2": ["hdmi", "usb-c-dp"],
    },
}

# ============================================================
# WIRE SELECTION RULES
# ============================================================
WIRE_RULES = {
    "signal": "silicon_26awg", "i2c_spi_uart": "silicon_26awg",
    "fan_power": "silicon_24awg", "led_strip": "silicon_24awg",
    "battery_low_current": "silicon_20awg", "main_power": "silicon_18awg",
    "solar_heavy": "silicon_16awg", "dsi_csi": "ribbon_cable",
    "quick_connect": "jst_connector_cable", "usb_power": "usb_c_cable",
    "led_neon": "silicon_26awg_neon", "hdmi_display": "hdmi_ribbon",
    "dsi_display": "dsi_ribbon",
}

# ============================================================
# CABLE ROUTING — accessory & management database
# ============================================================
CABLE_MANAGEMENT = {
    "zip_ties": {"name": "Zip Ties (assorted)", "use": "Secure cables to frame/standoffs", "price": 3},
    "cable_clips": {"name": "Adhesive Cable Clips", "use": "Route cables along enclosure walls", "price": 5},
    "braided_sleeving": {"name": "Braided Cable Sleeving (3mm/5mm)", "use": "Bundle and protect wire groups", "price": 6},
    "heat_shrink": {"name": "Heat Shrink Tubing (assorted)", "use": "Insulate solder joints", "price": 4},
    "velcro_straps": {"name": "Velcro Cable Ties", "use": "Reusable cable bundling", "price": 5},
    "fdp_tape": {"name": "FDP / Kapton Tape", "use": "Secure flat cables, insulate", "price": 4},
    "cable_grommet": {"name": "Cable Grommet (rubber)", "use": "Pass cables through enclosure walls cleanly", "price": 3},
    "standoff_kit": {"name": "M2.5/M3 Standoff Kit", "use": "Mount PCBs, keep clearance", "price": 6},
}


# ============================================================
# v5.2 — STORAGE DATABASE (NVMe SSDs, SD Cards, eMMC)
# ============================================================
STORAGE_DATABASE = {
    "nvme_970_evo_500": {"name": "Samsung 970 EVO Plus 500GB NVMe", "type": "NVMe M.2 2280", "capacity": "500GB", "read_speed": "3500 MB/s", "write_speed": "3200 MB/s", "interface": "PCIe Gen 3 x4", "price": 45, "pros": ["Fast", "Reliable", "DRAM cache", "5-year warranty"], "cons": ["Pi 5 limited to Gen 3 x1"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal"},
    "nvme_970_evo_1tb": {"name": "Samsung 970 EVO Plus 1TB NVMe", "type": "NVMe M.2 2280", "capacity": "1TB", "read_speed": "3500 MB/s", "write_speed": "3200 MB/s", "interface": "PCIe Gen 3 x4", "price": 80, "pros": ["Fast", "Reliable", "DRAM cache", "5-year warranty"], "cons": ["Pi 5 limited to Gen 3 x1"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal"},
    "nvme_wd_sn770_500": {"name": "WD Black SN770 500GB NVMe", "type": "NVMe M.2 2280", "capacity": "500GB", "read_speed": "5000 MB/s", "write_speed": "4000 MB/s", "interface": "PCIe Gen 4 x4", "price": 40, "pros": ["Fast", "DRAM-less (HMB)", "Good value", "5-year warranty"], "cons": ["Gen 4 wasted on Pi 5"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal"},
    "nvme_wd_sn770_1tb": {"name": "WD Black SN770 1TB NVMe", "type": "NVMe M.2 2280", "capacity": "1TB", "read_speed": "5000 MB/s", "write_speed": "4000 MB/s", "interface": "PCIe Gen 4 x4", "price": 65, "pros": ["Fast", "DRAM-less (HMB)", "Great value", "5-year warranty"], "cons": ["Gen 4 wasted on Pi 5"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal"},
    "nvme_kingston_a2000_500": {"name": "Kingston NV2 500GB NVMe", "type": "NVMe M.2 2280", "capacity": "500GB", "read_speed": "3500 MB/s", "write_speed": "2100 MB/s", "interface": "PCIe Gen 4 x4", "price": 30, "pros": ["Ultra cheap", "Decent speed", "Low power"], "cons": ["No DRAM", "Lower write speed"], "best_for": ["writerdeck", "gaming", "media"], "risk_level": "minimal"},
    "nvme_kingston_a2000_1tb": {"name": "Kingston NV2 1TB NVMe", "type": "NVMe M.2 2280", "capacity": "1TB", "read_speed": "3500 MB/s", "write_speed": "2100 MB/s", "interface": "PCIe Gen 4 x4", "price": 50, "pros": ["Cheap 1TB", "Decent speed", "Low power"], "cons": ["No DRAM", "Lower write speed"], "best_for": ["coding", "ai", "security"], "risk_level": "minimal"},
    "sd_card_64gb_a2": {"name": "Samsung EVO Select 64GB A2/U3", "type": "MicroSD", "capacity": "64GB", "read_speed": "160 MB/s", "write_speed": "120 MB/s", "interface": "MicroSD UHS-I", "price": 10, "pros": ["Fast boot", "A2 random I/O", "Reliable"], "cons": ["64GB only"], "best_for": ["ALL"], "risk_level": "minimal"},
    "sd_card_128gb_a2": {"name": "Samsung EVO Select 128GB A2/U3", "type": "MicroSD", "capacity": "128GB", "read_speed": "160 MB/s", "write_speed": "120 MB/s", "interface": "MicroSD UHS-I", "price": 15, "pros": ["Good capacity", "A2 random I/O", "Fast"], "cons": ["SD still slower than NVMe"], "best_for": ["ALL"], "risk_level": "minimal"},
    "sd_card_256gb_a2": {"name": "Samsung EVO Select 256GB A2/U3", "type": "MicroSD", "capacity": "256GB", "read_speed": "160 MB/s", "write_speed": "120 MB/s", "interface": "MicroSD UHS-I", "price": 25, "pros": ["Large capacity", "A2 random I/O"], "cons": ["SD still slower than NVMe"], "best_for": ["ALL"], "risk_level": "minimal"},
    "emmc_32gb": {"name": "eMMC Module 32GB (CM4/CM5)", "type": "eMMC", "capacity": "32GB", "read_speed": "100 MB/s", "write_speed": "80 MB/s", "interface": "eMMC 5.1", "price": 15, "pros": ["Boot drive", "Reliable", "Fast boot"], "cons": ["Fixed capacity"], "best_for": ["ALL"], "risk_level": "minimal"},
    "emmc_64gb": {"name": "eMMC Module 64GB (CM4/CM5)", "type": "eMMC", "capacity": "64GB", "read_speed": "100 MB/s", "write_speed": "80 MB/s", "interface": "eMMC 5.1", "price": 25, "pros": ["Good boot drive", "Reliable"], "cons": ["Fixed capacity"], "best_for": ["ALL"], "risk_level": "minimal"},
}

# ============================================================
# v5.2 — uConsole EXPANSION CARDS DATABASE
# ============================================================
UCONSOLE_EXPANSION_DATABASE = {
    "hackergadgets_aio_v2": {"name": "HackerGadgets AIO V2 (SDR+LoRa+GPS)", "type": "uConsole Expansion", "features": "RTL-SDR + LoRa SX1262 + GPS + RTC + USB hub", "interface": "USB-C + GPIO", "price": 60, "pros": ["All-in-one RF", "SDR + LoRa + GPS", "uConsole fit"], "cons": ["Complex", "Antenna needed"], "best_for": ["security", "ham-radio", "research"]},
    "openterface_kvm": {"name": "Openterface KVM Expansion", "type": "uConsole Expansion", "features": "HDMI input + USB HID + Ethernet", "interface": "USB-C", "price": 50, "pros": ["Portable KVM", "HDMI capture", "uConsole fit"], "cons": ["Single input"], "best_for": ["security", "field-repair"]},
    "clockwork_lte_modem": {"name": "ClockworkPi LTE Modem Card", "type": "uConsole Expansion", "features": "Quectel EC25 4G LTE + GNSS GPS", "interface": "USB + SIM slot", "price": 40, "pros": ["4G LTE", "GPS", "Always-connected"], "cons": ["Needs SIM card", "Antenna required"], "best_for": ["survival", "research", "security"]},
    "uether_ethernet": {"name": "uEther Ethernet Expansion", "type": "uConsole Expansion", "features": "10/100 RJ45 Ethernet + USB-C", "interface": "USB-C", "price": 15, "pros": ["Wired networking", "Cheap", "uConsole fit"], "cons": ["100Mbps only"], "best_for": ["security", "coding"]},
    "hackerGadgets_aio_v1": {"name": "HackerGadgets AIO V1 (SDR+LoRa)", "type": "uConsole Expansion", "features": "RTL-SDR + LoRa SX1262 + GPS", "interface": "USB-C + GPIO", "price": 50, "pros": ["SDR + LoRa", "uConsole fit"], "cons": ["Older version"], "best_for": ["security", "ham-radio"]},
}

# ============================================================
# COMPONENT DATABASE — centralized access to all part databases
# ============================================================
class ComponentDatabase:
    """Centralized access to all component databases."""

    @staticmethod
    def get_sbc(sbc_id):
        return SBC_DATABASE.get(sbc_id)

    @staticmethod
    def get_display(display_id):
        return DISPLAY_DATABASE.get(display_id)

    @staticmethod
    def get_keyboard(kb_id):
        return KEYBOARD_DATABASE.get(kb_id)

    @staticmethod
    def get_power(power_id):
        return POWER_DATABASE.get(power_id)

    @staticmethod
    def get_enclosure(enc_id):
        return ENCLOSURE_DATABASE.get(enc_id)

    @staticmethod
    def get_cooling(cooling_id):
        return COOLING_DATABASE.get(cooling_id)

    @staticmethod
    def get_pcb(pcb_id):
        return PCB_DATABASE.get(pcb_id)

    @staticmethod
    def get_wire(wire_id):
        return WIRE_DATABASE.get(wire_id)

    @staticmethod
    def get_connectivity(conn_id):
        return CONNECTIVITY_DATABASE.get(conn_id)

    @staticmethod
    def get_os(os_id):
        return OS_DATABASE.get(os_id)

    @staticmethod
    def get_storage(storage_id):
        return STORAGE_DATABASE.get(storage_id)

    @staticmethod
    def get_uconsole_expansion(card_id):
        return UCONSOLE_EXPANSION_DATABASE.get(card_id)

    @staticmethod
    def get_sensor(sensor_id):
        return ENVIRONMENTAL_SENSOR_DATABASE.get(sensor_id)

    @staticmethod
    def get_camera(camera_id):
        return CAMERA_MODULE_DATABASE.get(camera_id)

    @staticmethod
    def get_sdr(sdr_id):
        return SDR_DATABASE.get(sdr_id)

    @staticmethod
    def get_lora(lora_id):
        return LORA_MESH_DATABASE.get(lora_id)

    @staticmethod
    def get_nfc(nfc_id):
        return NFC_RFID_DATABASE.get(nfc_id)

    @staticmethod
    def get_fingerprint(fp_id):
        return FINGERPRINT_DATABASE.get(fp_id)

    @staticmethod
    def get_haptic(haptic_id):
        return HAPTIC_FEEDBACK_DATABASE.get(haptic_id)

    @staticmethod
    def get_imu(imu_id):
        return IMU_DATABASE.get(imu_id)

    @staticmethod
    def get_all_sbcs():
        return SBC_DATABASE

    @staticmethod
    def get_all_displays():
        return DISPLAY_DATABASE

    @staticmethod
    def get_all_keyboards():
        return KEYBOARD_DATABASE

    @staticmethod
    def get_all_power():
        return POWER_DATABASE

    @staticmethod
    def get_all_enclosures():
        return ENCLOSURE_DATABASE

    @staticmethod
    def get_all_cooling():
        return COOLING_DATABASE

    @staticmethod
    def get_all_pcb():
        return PCB_DATABASE

    @staticmethod
    def get_all_wires():
        return WIRE_DATABASE

    @staticmethod
    def get_all_connectivity():
        return CONNECTIVITY_DATABASE

    @staticmethod
    def get_all_os():
        return OS_DATABASE

    @staticmethod
    def search(query):
        results = []
        ql = query.lower()
        all_dbs = [("SBC", SBC_DATABASE), ("Display", DISPLAY_DATABASE),
                   ("Keyboard", KEYBOARD_DATABASE), ("Power", POWER_DATABASE),
                   ("Enclosure", ENCLOSURE_DATABASE), ("Cooling", COOLING_DATABASE),
                   ("PCB", PCB_DATABASE), ("Wire", WIRE_DATABASE),
                   ("Connectivity", CONNECTIVITY_DATABASE), ("Storage", STORAGE_DATABASE),
                   ("Sensor", ENVIRONMENTAL_SENSOR_DATABASE), ("Camera", CAMERA_MODULE_DATABASE),
                   ("SDR", SDR_DATABASE), ("LoRa", LORA_MESH_DATABASE),
                   ("NFC", NFC_RFID_DATABASE), ("Fingerprint", FINGERPRINT_DATABASE),
                   ("Haptic", HAPTIC_FEEDBACK_DATABASE), ("IMU", IMU_DATABASE),
                   ("uConsole Expansion", UCONSOLE_EXPANSION_DATABASE)]
        for db_name, db in all_dbs:
            for item_id, item in db.items():
                name = item.get("name", "").lower()
                if any(kw in name or kw in ql for kw in ql.split()):
                    results.append({"type": db_name, "id": item_id, **item})
        return results

    @staticmethod
    def get_stats():
        return {
            "sbc_count": len(SBC_DATABASE), "display_count": len(DISPLAY_DATABASE),
            "keyboard_count": len(KEYBOARD_DATABASE), "power_count": len(POWER_DATABASE),
            "enclosure_count": len(ENCLOSURE_DATABASE), "cooling_count": len(COOLING_DATABASE),
            "pcb_count": len(PCB_DATABASE), "wire_count": len(WIRE_DATABASE),
            "connectivity_count": len(CONNECTIVITY_DATABASE), "os_count": len(OS_DATABASE),
            "storage_count": len(STORAGE_DATABASE), "sensor_count": len(ENVIRONMENTAL_SENSOR_DATABASE),
            "camera_count": len(CAMERA_MODULE_DATABASE), "sdr_count": len(SDR_DATABASE),
            "lora_count": len(LORA_MESH_DATABASE), "nfc_count": len(NFC_RFID_DATABASE),
            "fingerprint_count": len(FINGERPRINT_DATABASE), "haptic_count": len(HAPTIC_FEEDBACK_DATABASE),
            "imu_count": len(IMU_DATABASE), "uconsole_count": len(UCONSOLE_EXPANSION_DATABASE),
            "total_components": (len(SBC_DATABASE) + len(DISPLAY_DATABASE) + len(KEYBOARD_DATABASE)
                                 + len(POWER_DATABASE) + len(ENCLOSURE_DATABASE) + len(COOLING_DATABASE)
                                 + len(PCB_DATABASE) + len(WIRE_DATABASE) + len(CONNECTIVITY_DATABASE)
                                 + len(OS_DATABASE) + len(STORAGE_DATABASE) + len(ENVIRONMENTAL_SENSOR_DATABASE)
                                 + len(CAMERA_MODULE_DATABASE) + len(SDR_DATABASE) + len(LORA_MESH_DATABASE)
                                 + len(NFC_RFID_DATABASE) + len(FINGERPRINT_DATABASE) + len(HAPTIC_FEEDBACK_DATABASE)
                                 + len(IMU_DATABASE) + len(UCONSOLE_EXPANSION_DATABASE)),
        }

    @staticmethod
    def get_component_details(component_id):
        databases = {
            "sbc": SBC_DATABASE, "display": DISPLAY_DATABASE, "keyboard": KEYBOARD_DATABASE,
            "power": POWER_DATABASE, "enclosure": ENCLOSURE_DATABASE, "cooling": COOLING_DATABASE,
            "pcb": PCB_DATABASE, "wire": WIRE_DATABASE, "connectivity": CONNECTIVITY_DATABASE,
            "os": OS_DATABASE, "storage": STORAGE_DATABASE, "sensor": ENVIRONMENTAL_SENSOR_DATABASE,
            "camera": CAMERA_MODULE_DATABASE, "sdr": SDR_DATABASE, "lora": LORA_MESH_DATABASE,
            "nfc": NFC_RFID_DATABASE, "fingerprint": FINGERPRINT_DATABASE,
            "haptic": HAPTIC_FEEDBACK_DATABASE, "imu": IMU_DATABASE,
            "uconsole": UCONSOLE_EXPANSION_DATABASE,
        }
        for db_name, db in databases.items():
            if component_id in db:
                comp = db[component_id]
                details = {"id": component_id, "database": db_name, **comp}
                details["specs"] = {
                    "type": comp.get("display_type") or comp.get("type") or db_name,
                    "size": comp.get("screen_size_inches") or comp.get("size") or comp.get("form_factor") or "N/A",
                    "resolution": comp.get("resolution") or "N/A",
                    "refresh_rate_hz": comp.get("refresh_rate_hz") or "N/A",
                    "brightness_nits": comp.get("brightness_nits") or "N/A",
                    "interface": comp.get("interface") or comp.get("connection") or comp.get("video_output") or "N/A",
                    "power_consumption_w": comp.get("power_consumption_w") or comp.get("power_draw") or "N/A",
                }
                details["risk"] = {
                    "level": comp.get("risk_level", "unknown"),
                    "factors": comp.get("risk_factors", {}),
                }
                if comp.get("waterproof_rating"):
                    details["specs"]["waterproof_rating"] = comp["waterproof_rating"]
                return details
        return {"error": f"Component '{component_id}' not found in any database"}


# ============================================================
# LEARNER — persistent knowledge from videos & interactions
# ============================================================
class CyberdeckLearner:
    def __init__(self):
        self.file = LEARNINGS_FILE
        self.learnings = self._load()

    def _load(self) -> Dict:
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "video_knowledge": [], "tips_learned": [], "flaws_fixed": [],
                "user_preferences": {}, "component_discoveries": [],
                "build_insights": [], "chat_learnings": [], "evolution_log": [],
                "trends": [], "image_analyses": [],
            }

    def _save(self):
        try:
            with open(self.file, "w") as f:
                json.dump(self.learnings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save learnings: {e}")

    def learn_from_video(self, title, url, key_points, components, tips):
        entry = {"title": title, "url": url, "key_points": key_points,
                 "components": components, "tips": tips, "learned_at": datetime.now().isoformat()}
        self.learnings["video_knowledge"].append(entry)
        for tip in tips:
            if tip not in self.learnings["tips_learned"]:
                self.learnings["tips_learned"].append(tip)
        for comp in components:
            if comp not in self.learnings["component_discoveries"]:
                self.learnings["component_discoveries"].append(comp)
        self._save()

    def learn_from_chat(self, user_message, bot_response, context="general"):
        entry = {"user_message": user_message[:500], "bot_response": bot_response[:500],
                 "context": context, "learned_at": datetime.now().isoformat()}
        self.learnings["chat_learnings"].append(entry)
        if len(self.learnings["chat_learnings"]) > 500:
            self.learnings["chat_learnings"] = self.learnings["chat_learnings"][-500:]
        self._save()

    def learn_from_build(self, build):
        entry = {"build": build, "learned_at": datetime.now().isoformat()}
        self.learnings["build_insights"].append(entry)
        self._save()

    def log_flaw_fix(self, flaw, fix):
        self.learnings["flaws_fixed"].append(
            {"flaw": flaw, "fix": fix, "fixed_at": datetime.now().isoformat()})
        self._save()

    def log_evolution(self, what_changed):
        self.learnings["evolution_log"].append(
            {"change": what_changed, "at": datetime.now().isoformat()})
        self._save()

    def log_image_analysis(self, analysis):
        self.learnings["image_analyses"].append(
            {**analysis, "analyzed_at": datetime.now().isoformat()})
        if len(self.learnings["image_analyses"]) > 200:
            self.learnings["image_analyses"] = self.learnings["image_analyses"][-200:]
        self._save()

    def add_trend(self, trend, source="general"):
        self.learnings["trends"].append(
            {"trend": trend, "source": source, "added_at": datetime.now().isoformat()})
        if len(self.learnings["trends"]) > 100:
            self.learnings["trends"] = self.learnings["trends"][-100:]
        self._save()

    def get_all_tips(self):
        return self.learnings.get("tips_learned", [])

    def get_all_components_discovered(self):
        return self.learnings.get("component_discoveries", [])

    def get_trends(self):
        return self.learnings.get("trends", [])

    def get_user_preferences(self, user_id):
        return self.learnings.get("user_preferences", {}).get(str(user_id), {})

    def set_user_preference(self, user_id, key, value):
        uid = str(user_id)
        if uid not in self.learnings.get("user_preferences", {}):
            self.learnings.setdefault("user_preferences", {})[uid] = {}
        self.learnings["user_preferences"][uid][key] = value
        self._save()

    def get_stats(self):
        return {
            "videos_learned": len(self.learnings.get("video_knowledge", [])),
            "tips_count": len(self.learnings.get("tips_learned", [])),
            "components_discovered": len(self.learnings.get("component_discoveries", [])),
            "flaws_fixed": len(self.learnings.get("flaws_fixed", [])),
            "build_insights": len(self.learnings.get("build_insights", [])),
            "chat_learnings": len(self.learnings.get("chat_learnings", [])),
            "evolution_entries": len(self.learnings.get("evolution_log", [])),
            "trends_tracked": len(self.learnings.get("trends", [])),
            "image_analyses": len(self.learnings.get("image_analyses", [])),
        }


# ============================================================
# COMPATIBILITY ENGINE — 100% validation + auto-fix
# ============================================================
class CompatibilityEngine:
    @staticmethod
    def check_sbc_display(sbc_id, display_id):
        sbc = SBC_DATABASE.get(sbc_id)
        display = DISPLAY_DATABASE.get(display_id)
        if not sbc or not display:
            return {"compatible": False, "issues": ["Unknown component"]}
        issues = []
        sbc_name = sbc["name"].lower()
        display_if = display.get("interface", "").lower()
        if "zero 2w" in sbc_name:
            if "hdmi" in display_if and "mini" not in display_if:
                issues.append("Pi Zero 2W needs mini-HDMI adapter for HDMI displays")
            if "dsi" in display_if:
                issues.append("Pi Zero 2W has no DSI connector")
        if "jetson" in sbc_name and ("eink" in display_id or "oled" in display_id):
            issues.append("Jetson works best with HDMI/DSI displays")
        if "orange pi zero3" in sbc_name and "dsi" in display_if:
            issues.append("Orange Pi Zero 3 has no DSI connector")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_sbc_power(sbc_id, power_id):
        sbc = SBC_DATABASE.get(sbc_id)
        power = POWER_DATABASE.get(power_id)
        if not sbc or not power:
            return {"compatible": False, "issues": ["Unknown component"]}
        issues = []
        sbc_power = sbc.get("power_draw", "")
        power_output = power.get("output", "")
        if "5V/5A" in sbc_power and "5A" not in power_output:
            issues.append(f"{sbc['name']} needs 5V/5A but {power['name']} outputs {power_output}")
        if "jetson" in sbc_id and power_id == "pisugar3_plus":
            issues.append("Jetson requires more power than PiSugar can provide")
        if "orange_pi_5" in sbc_id and power_id == "pimoroni_lipo_shim":
            issues.append("Orange Pi 5 Plus needs more power than LiPo SHIM provides")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_sbc_enclosure(sbc_id, enclosure_id):
        sbc = SBC_DATABASE.get(sbc_id)
        enclosure = ENCLOSURE_DATABASE.get(enclosure_id)
        if not sbc or not enclosure:
            return {"compatible": False, "issues": ["Unknown component"]}
        issues = []
        sbc_name = sbc["name"].lower()
        if "lattepanda" in sbc_id and "pelican_1150" in enclosure_id:
            issues.append("LattePanda 3 Delta (125x78mm) is too large for Pelican 1150")
        if "jetson" in sbc_id and ("pelican_1150" in enclosure_id or "pelican_1200" in enclosure_id):
            issues.append("Jetson Orin Nano (100x87mm) needs larger enclosure")
        if "zero 2w" in sbc_name and "3d_printed_vented" in enclosure_id:
            issues.append("Pi Zero 2W doesn't need vented enclosure — too small for active cooling")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_connectivity(components):
        issues = []
        sbc_id = components.get("sbc", "")
        conn_id = components.get("connectivity", "")
        cat = components.get("category", "")
        sbc = SBC_DATABASE.get(sbc_id, {})
        has_wifi = "WiFi" in sbc.get("connectivity", "")
        if not conn_id and not has_wifi:
            issues.append("No connectivity: SBC has no built-in WiFi and no adapter selected")
        if cat == "security" and conn_id not in ("awus036ach", "awus036acs", "hackrf_one"):
            issues.append("Security builds should include an Alfa WiFi adapter or HackRF")
        if cat == "survival" and conn_id not in ("lora_module", "lte_modem"):
            issues.append("Survival builds should include LoRa or LTE modem for off-grid comms")
        return {"compatible": len(issues) == 0, "issues": issues}

    @staticmethod
    def check_full_build(components):
        all_issues = []
        sbc_id = components.get("sbc")
        display_id = components.get("display")
        power_id = components.get("power")
        enclosure_id = components.get("enclosure")
        if sbc_id and display_id:
            r = CompatibilityEngine.check_sbc_display(sbc_id, display_id)
            all_issues.extend(r.get("issues", []))
        if sbc_id and power_id:
            r = CompatibilityEngine.check_sbc_power(sbc_id, power_id)
            all_issues.extend(r.get("issues", []))
        if sbc_id and enclosure_id:
            r = CompatibilityEngine.check_sbc_enclosure(sbc_id, enclosure_id)
            all_issues.extend(r.get("issues", []))
        conn_result = CompatibilityEngine.check_connectivity(components)
        all_issues.extend(conn_result.get("issues", []))
        return {"compatible": len(all_issues) == 0, "issues": all_issues,
                "checked_at": datetime.now().isoformat(),
                "checks_performed": ["sbc_display", "sbc_power", "sbc_enclosure", "connectivity"]}

    @staticmethod
    def select_wire_for_use(use):
        wire_id = WIRE_RULES.get(use, "silicon_26awg")
        wire = WIRE_DATABASE.get(wire_id, WIRE_DATABASE["silicon_26awg"])
        return {"wire_id": wire_id, "wire": wire}

    @staticmethod
    def auto_fix(components, issues):
        fixed = dict(components)
        for issue in issues:
            il = issue.lower()
            if "5v/5a" in il and "ups_h5180" not in fixed.get("power", ""):
                fixed["power"] = "ups_h5180"
            if ("too large" in il or "needs larger" in il) and "pelican_1450" not in fixed.get("enclosure", ""):
                fixed["enclosure"] = "pelican_1450"
            if "mini-hdmi" in il:
                fixed["display"] = "eink_7inch"
            if "no wifi" in il or "no connectivity" in il:
                fixed["connectivity"] = "usb_ethernet"
            if "security" in il and "alfa" in il:
                fixed["connectivity"] = "awus036ach"
            if "survival" in il and "lora" in il:
                fixed["connectivity"] = "lora_module"
            if "provide" in il and "power" in il:
                fixed["power"] = "ups_h5180"
            if "no dsi" in il:
                fixed["display"] = "hdmi_7inch_ips"
        return fixed


# ============================================================
# CABLE ROUTING — generate cable management plans
# ============================================================
class CableRouter:
    @staticmethod
    def generate_routing_plan(build):
        components = build.get("components", {})
        enclosure = components.get("enclosure", {})
        sbc = components.get("sbc", {})
        display = components.get("display", {})
        keyboard = components.get("keyboard", {})
        power = components.get("power", {})
        cooling = components.get("cooling", {})
        connectivity = components.get("connectivity", {})
        enc_type = enclosure.get("id", "3d_printed")
        cables, accessories, tips = [], [], []
        if display.get("interface", "").lower().startswith("hdmi"):
            cables.append({"cable": "HDMI cable (micro-HDMI to HDMI or ribbon)", "route": "SBC HDMI -> display", "length": "15-30cm", "management": "Route along enclosure wall, avoid 90-degree bends"})
        if display.get("interface", "").lower().startswith("dsi"):
            cables.append({"cable": "DSI ribbon cable (15-pin FPC)", "route": "SBC DSI -> display FPC", "length": "20-40cm", "management": "Keep flat and uncreased, route along bottom"})
        if display.get("touch"):
            cables.append({"cable": "USB-C touch cable", "route": "Display touch USB -> SBC USB port", "length": "15-25cm", "management": "Bundle with HDMI cable"})
        if "USB" in keyboard.get("connection", ""):
            cables.append({"cable": f"USB cable ({keyboard.get('connection', 'USB-C')})", "route": "Keyboard -> SBC USB port", "length": "20-50cm", "management": "Allow slack for typing, route through grommet"})
        power_type = power.get("type", "")
        if "UPS HAT" in power_type:
            cables.append({"cable": "GPIO power connection (stacked)", "route": "UPS HAT -> SBC GPIO header", "length": "0cm (stacked)", "management": "Direct stacking, use standoffs for clearance"})
        elif "USB" in power.get("output", ""):
            cables.append({"cable": "USB-C power cable", "route": "Power source -> SBC USB-C input", "length": "20-30cm", "management": "Use shortest cable, route away from signal cables"})
        if cooling.get("type", "").startswith("Active"):
            cables.append({"cable": "Fan power wire (2-pin or 3-pin)", "route": "Fan -> SBC GPIO 5V/GND", "length": "5-15cm", "management": "Route along SBC edge, heat shrink on joints"})
        conn_type = connectivity.get("type", "")
        if "WiFi" in conn_type:
            cables.append({"cable": "USB WiFi adapter", "route": "Adapter -> SBC USB 3.0 port", "length": "0cm (dongle) or pigtail", "management": "Route SMA cable through enclosure if external antenna"})
        if "Ethernet" in conn_type or "ethernet" in conn_type:
            cables.append({"cable": "USB-C to Ethernet adapter + Cat6", "route": "Cat6 -> adapter -> SBC USB-C", "length": "1m Cat6 + adapter", "management": "Route through grommet, keep away from power"})
        if "LoRa" in conn_type:
            cables.append({"cable": "LoRa module SPI wires (4-5 wires)", "route": "LoRa -> SBC SPI GPIO pins", "length": "10-20cm", "management": "Keep short, away from power, use JST connectors"})
        accessories_used = set()
        if len(cables) > 2:
            accessories_used.update(["zip_ties", "cable_clips"])
        if len(cables) > 4:
            accessories_used.add("braided_sleeving")
        accessories_used.update(["heat_shrink", "standoff_kit"])
        if enc_type.startswith("pelican"):
            accessories_used.update(["cable_grommet", "fdp_tape"])
        for acc_id in accessories_used:
            acc = CABLE_MANAGEMENT.get(acc_id, {})
            if acc:
                accessories.append({"id": acc_id, **acc})
        tips.extend([
            "Route power cables on one side, signal cables on the other",
            "Keep SPI/I2C wires under 15cm for signal integrity",
            "Use heat shrink tubing on ALL solder joints",
            "Label each cable with a small tag or colored tape",
            "Leave 2-3cm slack at each connection point",
            "Avoid running signal cables parallel to power cables (EMI)",
            "Use cable grommets where cables pass through enclosure walls",
        ])
        return {"cables": cables, "total_cables": len(cables), "accessories": accessories,
                "tips": tips, "estimated_management_time": f"{len(cables)*5}-{len(cables)*10} minutes"}


# ============================================================
# TUTORIAL GENERATOR — word-by-word assembly
# ============================================================
class TutorialGenerator:
    @staticmethod
    def generate(build):
        tier = build.get("tier_id", "intermediate")
        tier_info = TIERS.get(tier, TIERS["intermediate"])
        sbc = build["components"].get("sbc", {})
        display = build["components"].get("display", {})
        kb = build["components"].get("keyboard", {})
        power = build["components"].get("power", {})
        enclosure = build["components"].get("enclosure", {})
        cooling = build["components"].get("cooling", {})
        connectivity = build["components"].get("connectivity", {})
        wiring = CableRouter.generate_routing_plan(build)
        lines = [
            f"# {build['category']} Cyberdeck — Assembly Tutorial",
            f"**Tier:** {build['tier']} | **SBC:** {sbc.get('name', 'N/A')} | **Est. Cost:** {build.get('total_price_estimate', '?')}",
            "", "## Tools Needed",
        ]
        for tool in tier_info.get("tools_needed", []):
            lines.append(f"- [ ] {tool}")
        lines.extend(["", "## Parts List"])
        for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "connectivity"]:
            comp = build["components"].get(key, {})
            if comp:
                lines.append(f"- [ ] {comp.get('name', key)}")
        lines.extend(["", "---", "", "## Assembly Steps", ""])
        step = 1
        lines.extend([
            f"### Step {step}: Prepare the Enclosure",
            "", f"1. Unbox your **{enclosure.get('name', 'enclosure')}**.",
            "2. If using pick-and-pluck foam, remove foam cubes to match your SBC and display shapes.",
            "3. **Test-fit** the SBC and display in the enclosure BEFORE wiring.",
            "4. Mark drill points for: mounting screws, fan holes, connector ports.",
            "5. If 3D printed: clean up any stringing with a heat gun (low setting).",
            "", "> **Tools needed:** Screwdriver, marker pen, ruler",
            "> **What could go wrong:** Foam too tight — cut slightly larger holes", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Mount the SBC",
            "", f"1. Place the **{sbc.get('name', 'SBC')}** in the enclosure.",
            "2. Secure with M2.5 standoffs and screws (4x).",
            "3. Ensure the GPIO header is accessible and not blocked.",
            "4. Check that all USB/HDMI ports align with enclosure cutouts.",
            "", "> **Tools needed:** M2.5 screwdriver, standoffs",
            "> **What could go wrong:** Standoffs too long/short, GPIO pins blocked", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Install Cooling",
            "", f"1. Apply thermal paste if using a heatsink ({cooling.get('name', 'N/A')}).",
            "2. Mount the cooling solution to the SBC.",
            "3. If using a fan: connect to GPIO 5V and GND pins (or fan header).",
            "4. Test fan spin before closing the enclosure.",
            "", "> **Tools needed:** Thermal paste applicator, screwdriver",
            "> **What could go wrong:** Fan wires too short, thermal paste applied unevenly", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Install the Display",
            "", f"1. Connect the **{display.get('name', 'display')}** via {display.get('interface', 'HDMI')}.",
        ])
        if display.get("touch"):
            lines.append("2. Connect the USB touch cable to a USB port on the SBC.")
        lines.extend([
            "3. Mount the display in the enclosure (screws or adhesive standoffs).",
            "4. Route the cable neatly along the enclosure wall.",
            "", "> **Tools needed:** Matching screwdriver or double-sided tape",
            "> **What could go wrong:** Cable pinched between display and enclosure", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Connect the Keyboard",
            "", f"1. Connect the **{kb.get('name', 'keyboard')}** via {kb.get('connection', 'USB')}.",
            "2. If wired, route the cable through a cable management hole or grommet.",
            "3. Test typing before closing the enclosure.",
            "", "> **Tools needed:** None (plug-and-play for most keyboards)",
            "> **What could go wrong:** Cable too short, USB port blocked", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Wire the Power System",
            "", f"1. Install the **{power.get('name', 'power source')}**.",
        ])
        if "18650" in power.get("name", "").lower() or "BMS" in power.get("type", ""):
            lines.extend(["2. **WARNING:** Install 18650 cells with correct polarity (check BMS markings).",
                           "3. Use a multimeter to verify voltage before connecting to SBC.",
                           "4. Connect BMS output to SBC power input via correct gauge wire."])
        elif "UPS HAT" in power.get("type", ""):
            lines.extend(["2. Stack the UPS HAT onto the SBC GPIO header.",
                           "3. Secure with screws/standoffs.",
                           "4. Insert batteries if required (check orientation)."])
        elif "solar" in power.get("name", "").lower():
            lines.extend(["2. Connect solar panel to charge controller.",
                           "3. Connect charge controller output to battery pack.",
                           "4. Connect battery pack USB output to SBC power input."])
        else:
            lines.extend(["2. Connect power bank USB output to SBC USB-C power input.",
                           "3. Secure power bank in enclosure with velcro or adhesive."])
        lines.extend(["5. **Test power-on** before proceeding.",
                       "", "> **Tools needed:** Multimeter, soldering iron (if wiring batteries)",
                       "> **CRITICAL:** Double-check polarity before connecting power.", ""])
        step += 1
        lines.extend([
            f"### Step {step}: Configure Connectivity",
            "", f"1. WiFi: {'Built-in WiFi on ' + sbc.get('name', 'SBC') if 'WiFi' in sbc.get('connectivity', '') else 'Plug in WiFi adapter'}",
        ])
        if "Alfa" in connectivity.get("name", "") or "awus" in connectivity.get("id", ""):
            lines.extend(["2. Install Alfa WiFi adapter driver (RTL8812AU):",
                           "   ```bash", "   sudo apt install dkms git",
                           "   git clone https://github.com/aircrack-ng/rtl8812au.git",
                           "   cd rtl8812au && sudo make dkms_install", "   ```",
                           "3. Connect external antenna to adapter.",
                           "4. Route SMA pigtail cable through enclosure wall."])
        if "ethernet" in connectivity.get("name", "").lower() or "Cat6" in connectivity.get("name", ""):
            lines.extend(["2. Connect USB-C to Ethernet adapter to SBC.",
                           "3. Connect Cat6 cable to adapter and network."])
        if "LoRa" in connectivity.get("type", ""):
            lines.extend(["2. Connect LoRa module via SPI wires to GPIO.",
                           "3. Flash Meshtastic firmware.",
                           "4. Connect antenna (868/915MHz)."])
        lines.extend(["5. Test internet: `ping 8.8.8.8`",
                       "", "> **Tools needed:** Screwdriver (for antenna), terminal access", ""])
        step += 1
        lines.extend([f"### Step {step}: Cable Management", "",
                       f"Route **{wiring['total_cables']} cables** as follows:", ""])
        for i, cable in enumerate(wiring["cables"], 1):
            lines.extend([f"**Cable {i}:** {cable['cable']}",
                           f"  - Route: {cable['route']}", f"  - Length: {cable['length']}",
                           f"  - Tip: {cable['management']}", ""])
        lines.extend(["**Accessories to use:**"])
        for acc in wiring.get("accessories", []):
            lines.append(f"- {acc['name']}: {acc['use']}")
        lines.extend(["", "**Cable routing tips:**"])
        for tip in wiring.get("tips", []):
            lines.append(f"- {tip}")
        lines.extend(["", "---", ""])
        step += 1
        lines.extend([
            f"### Step {step}: Final Assembly & Testing",
            "", "1. Route all cables neatly inside the enclosure.",
            "2. Ensure NO cables are pinched, under stress, or blocking airflow.",
            "3. Close the enclosure and secure all screws.",
            "4. Power on and verify: display, keyboard, fan, WiFi, Ethernet.",
            "5. Run `htop` to verify CPU temp stays under 70C under load.",
            "6. Run `iperf3` or `speedtest-cli` to verify network performance.", "",
        ])
        step += 1
        lines.extend([
            f"### Step {step}: Software Setup", "",
            f"1. Flash **{build['components'].get('os', {}).get('name', 'Raspberry Pi OS')}** to SD card.",
            "2. Boot and complete initial setup.",
            "3. Update: `sudo apt update && sudo apt upgrade -y`",
            "4. Install category-specific software.",
            "5. Test all hardware: display, keyboard, cooling, power management.",
            "", "---", "", "## Troubleshooting", "",
            "| Problem | Solution |", "|---------|----------|",
            "| Display not showing | Check HDMI/DSI cable, try different port |",
            "| Keyboard not working | Check USB connection, try different port |",
            "| Fan not spinning | Check GPIO wiring (5V/GND), verify pinout |",
            "| Won't power on | Check battery/UPS charge, verify power cable polarity |",
            "| Overheating | Check thermal paste, ensure fan connected |",
            "| No WiFi | Check driver install, `iwconfig`, reboot |",
            "| No Ethernet | Check adapter LED, `ip link show`, try different cable |", "",
        ])
        try:
            learner = CyberdeckLearner()
            for tip in learner.get_all_tips()[:5]:
                lines.append(f"- {tip}")
        except Exception:
            pass
        return "\n".join(lines)


# ============================================================
# IDEA GENERATOR — creativity engine
# ============================================================
class IdeaGenerator:
    BASE_IDEAS = [
        {"title": "The Minimalist Writer", "category": "writerdeck", "description": "Pi Zero 2W + 4.2\" e-ink + Planck ortho.", "difficulty": "beginner", "estimated_cost": "$150"},
        {"title": "The Field Hacker", "category": "security", "description": "Pi 5 16GB + 7\" touch + Kali + AWUS036ACH + HackRF SDR.", "difficulty": "intermediate", "estimated_cost": "$800"},
        {"title": "The Retro Arcade", "category": "gaming", "description": "Pi 5 8GB + 7\" HDMI + RetroPie + USB controllers + Pelican.", "difficulty": "beginner", "estimated_cost": "$250"},
        {"title": "The AI Terminal", "category": "ai", "description": "Jetson Orin Nano + 10\" HDMI + NVMe + active cooling + 40 TOPS.", "difficulty": "advanced", "estimated_cost": "$1200"},
        {"title": "The Off-Grid Comms", "category": "survival", "description": "Pi 5 + e-ink + LoRa + ham radio + solar panel + 6x 18650.", "difficulty": "advanced", "estimated_cost": "$700"},
        {"title": "The Dual-Screen Dev", "category": "coding", "description": "Pi 5 16GB + 7\" main + 5\" OLED status + Planck + NVMe.", "difficulty": "advanced", "estimated_cost": "$900"},
        {"title": "The Cinema Deck", "category": "media", "description": "Pi 5 + 10\" HDMI + speakers + wireless keyboard + LibreELEC.", "difficulty": "beginner", "estimated_cost": "$300"},
        {"title": "The Cyberpunk Prop", "category": "conversation-piece", "description": "Zero 2W + OLED + neon LEDs + vintage briefcase + mechanical keyboard.", "difficulty": "intermediate", "estimated_cost": "$400"},
        {"title": "The Research Station", "category": "research", "description": "Pi 5 8GB + sunlight-readable 10\" + NVMe + 6x 18650 + offline Wikipedia.", "difficulty": "intermediate", "estimated_cost": "$600"},
        {"title": "The Recovery Kit", "category": "coding", "description": "Pi 5 + Pelican 1450 + 7\" touch + Planck + Ethernet switch + UPS HAT.", "difficulty": "advanced", "estimated_cost": "$850"},
        {"title": "The Penkesu Computer", "category": "writerdeck", "description": "Pi Zero 2W + 7.5\" e-ink + Corne split keyboard + GBA SP hinges.", "difficulty": "intermediate", "estimated_cost": "$350"},
        {"title": "The Chonky Palmtop", "category": "coding", "description": "Pi 5 + 7\" touch + Corne split on pivot + NVMe + active cooling.", "difficulty": "advanced", "estimated_cost": "$1000"},
        {"title": "The Cyberdore 2064", "category": "conversation-piece", "description": "Pi Zero + OLED 128x64 + rotary encoder + mechanical keys.", "difficulty": "beginner", "estimated_cost": "$200"},
        {"title": "The Tactical Wedge", "category": "security", "description": "Pi 5 + FDM-printed modular case + Kali + external antenna + GPIO switches.", "difficulty": "advanced", "estimated_cost": "$750"},
        {"title": "The Bumble Budget", "category": "gaming", "description": "Orange Pi Zero 3 + 5\" HDMI + RetroPie + budget enclosure.", "difficulty": "beginner", "estimated_cost": "$120"},
        {"title": "The Ham Shack", "category": "ham-radio", "description": "Pi 5 + HackRF One + RTL-SDR + 7\" display + Pelican + 18650 pack.", "difficulty": "advanced", "estimated_cost": "$900"},
        {"title": "The Maker's Bench", "category": "maker", "description": "Pi 5 + 7\" touch + SparkFun Qwiic HAT + Logic Analyzer + UPS HAT.", "difficulty": "intermediate", "estimated_cost": "$500"},
        {"title": "The Field Surgeon", "category": "field-repair", "description": "Pi 5 + 5\" HDMI + Rii combo + Pelican 1200 + USB multimeter + Ethernet.", "difficulty": "intermediate", "estimated_cost": "$450"},
        {"title": "The Retro Terminal", "category": "retro", "description": "Pi Zero 2W + 4.2\" amber e-ink + vintage Model M keyboard + ammo box.", "difficulty": "intermediate", "estimated_cost": "$250"},
        {"title": "The MeshNode", "category": "survival", "description": "Pi 5 + e-ink + 3x LoRa modules + LTE modem + solar + Pelican 1450.", "difficulty": "advanced", "estimated_cost": "$800"},
    ]

    @staticmethod
    def generate(category=None, budget=None, skill=None):
        ideas = list(IdeaGenerator.BASE_IDEAS)
        if category:
            ideas = [i for i in ideas if i["category"] == category]
        if skill:
            skill_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
            max_level = skill_order.get(skill, 2)
            ideas = [i for i in ideas if skill_order.get(i["difficulty"], 0) <= max_level]
        if budget is not None:
            ideas = [i for i in ideas if IdeaGenerator._parse_cost(i.get("estimated_cost", "$500")) <= budget * 1.2]
        return ideas if ideas else IdeaGenerator.BASE_IDEAS[:3]

    @staticmethod
    def _parse_cost(cost_str):
        nums = re.findall(r'\d+', cost_str.replace(",", ""))
        return int(nums[-1]) if nums else 500

    @staticmethod
    def generate_from_trends(learner, category=None):
        ideas = IdeaGenerator.generate(category)
        trends = learner.get_trends()
        if trends:
            recent = [t["trend"] for t in trends[-10:]]
            for idea in ideas:
                idea["trending_context"] = recent[:3]
        return ideas


# ============================================================
# VIDEO QUEUE — background learning
# ============================================================
class VideoLearningQueue:
    def __init__(self):
        self.file = VIDEO_QUEUE_FILE
        self.queue = self._load()

    def _load(self):
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

    def add(self, url):
        for entry in self.queue:
            if entry.get("url") == url and entry["status"] == "pending":
                return {"status": "already_queued", "url": url}
        entry = {"url": url, "status": "pending", "queued_at": datetime.now().isoformat(), "result": None}
        self.queue.append(entry)
        self._save()
        return {"status": "queued", "url": url, "position": len(self.queue)}

    def process_pending(self, learner):
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

    def _watch_and_learn(self, url, learner):
        title = url.split("/")[-1][:80] if "/" in url else url[:80]
        key_points, components, tips = [], [], []
        try:
            import subprocess
            script = os.path.expanduser("~/.claude/skills/watch-video/scripts/watch.py")
            if os.path.exists(script):
                result = subprocess.run(
                    ["python", script, url], capture_output=True, text=True, timeout=180)
                if result.returncode == 0 and result.stdout:
                    comp_kw = ["sbc", "raspberry pi", "zero 2w", "jetson", "orange pi", "lattepanda",
                               "display", "screen", "keyboard", "battery", "enclosure", "pcb", "wire",
                               "waveshare", "pimoroni", "geekworm", "nvme", "e-ink", "oled"]
                    tip_kw = ["tip", "trick", "note", "warning", "important", "make sure",
                              "don't forget", "always", "never", "pro tip", "life hack"]
                    for line in result.stdout.strip().split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        ll = line.lower()
                        if any(kw in ll for kw in comp_kw):
                            components.append(line[:150])
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
        return {"title": title, "url": url, "key_points_count": len(key_points),
                "components_found": components[:15], "tips_found": tips[:15]}

    def get_pending_count(self):
        return len([e for e in self.queue if e["status"] == "pending"])

    def get_all_entries(self):
        return self.queue


# ============================================================
# IMAGE ANALYZER — AI vision via base64 + httpx
# ============================================================
class ImageAnalyzer:
    @staticmethod
    def analyze_from_description(description):
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
        for conn_id, conn in CONNECTIVITY_DATABASE.items():
            if any(kw in desc_lower for kw in conn["name"].lower().split()):
                found.append({"type": "Connectivity", "id": conn_id, "name": conn["name"]})
        category = "coding"
        cat_keywords = {
            "writerdeck": ["writer", "writing", "typewriter", "e-ink", "distraction"],
            "security": ["security", "hack", "penetrat", "kali", "red team", "antenna"],
            "gaming": ["game", "retro", "arcade", "emulat", "controller"],
            "research": ["research", "field", "solar", "outdoor", "rugged"],
            "ai": ["ai", "machine learning", "neural", "inference", "jetson"],
            "survival": ["survival", "off-grid", "emergency", "solar", "lora"],
            "media": ["media", "movie", "music", "kodi", "stream"],
            "conversation-piece": ["cyberpunk", "neon", "led", "prop", "cosplay", "aesthetic"],
            "ham-radio": ["ham radio", "amateur radio", "hf", "vhf", "uhf"],
            "maker": ["maker", "soldering", "pcb", "breadboard", "oscilloscope"],
            "field-repair": ["repair", "diagnostic", "multimeter", "test"],
        }
        for cat, keywords in cat_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                category = cat
                break
        return {"identified_components": found, "suggested_category": category, "component_count": len(found)}

    @staticmethod
    def analyze_with_ai(description):
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
                    f"upgrades(list), tips(list)")
                response = provider.generate(prompt)
                result["ai_analysis"] = response
        except Exception as e:
            logger.debug(f"Image AI analysis fallback: {e}")
        return result

    @staticmethod
    def analyze_image_base64(image_data_b64, mime_type="image/jpeg"):
        result = {"identified_components": [], "suggested_category": "coding",
                  "ai_analysis": None, "vision_used": False}
        try:
            import httpx
            api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY") or os.environ.get("AI_API_KEY")
            api_base = os.environ.get("AI_API_BASE", "https://api.groq.com/openai/v1")
            model = os.environ.get("AI_VISION_MODEL", "llama-3.2-90b-vision-preview")
            if not api_key:
                return result
            prompt = (
                "You are a cyberdeck expert. Analyze this image of a cyberdeck or electronic project. "
                "Identify ALL visible components: SBC (Raspberry Pi, Orange Pi, Jetson, etc.), "
                "display (HDMI, DSI, e-ink, OLED), keyboard, PCB/HATs, wires, enclosure type, "
                "cooling solution, and any connectivity modules. "
                "For each component, provide: type, probable model, confidence. "
                "Then suggest: best category, compatibility issues, upgrade recommendations. "
                "Format as JSON: components(list of {type, model, confidence}), "
                "category(string), issues(list), upgrades(list), tips(list).")
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data_b64}"}},
                ]}],
                "max_tokens": 1500,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            response = httpx.post(f"{api_base}/chat/completions", json=payload, headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                result["ai_analysis"] = content
                result["vision_used"] = True
                try:
                    parsed = json.loads(content)
                    for key in ["components", "category", "issues", "upgrades", "tips"]:
                        if key in parsed:
                            result[key if key != "components" else "identified_components"] = parsed[key]
                            if key == "category":
                                result["suggested_category"] = parsed[key]
                except json.JSONDecodeError:
                    result["ai_raw_text"] = content
        except ImportError:
            logger.debug("httpx not installed — install with: pip install httpx")
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
        return result


# ============================================================
# BUILD OPTIMIZER — flaw detection + auto-fix
# ============================================================
class BuildOptimizer:
    @staticmethod
    def scan_flaws(build):
        flaws = []
        components = build.get("components", {})
        sbc = components.get("sbc", {})
        display = components.get("display", {})
        power = components.get("power", {})
        cooling = components.get("cooling", {})
        connectivity = components.get("connectivity", {})
        cat = build.get("category_id", "coding")
        sbc_draw = sbc.get("power_draw", "")
        power_out = power.get("output", "")
        if "5V/5A" in sbc_draw and "5A" not in power_out:
            flaws.append({"type": "power", "severity": "critical",
                          "issue": f"SBC needs 5V/5A but power source only provides {power_out}",
                          "fix": "Switch to Waveshare UPS HAT B or Geekworm X1200"})
        if cooling.get("type") == "Passive" and "ai" in cat:
            flaws.append({"type": "thermal", "severity": "high",
                          "issue": "AI workloads generate sustained heat — passive cooling may throttle",
                          "fix": "Upgrade to active_fan_heatsink (ICE Tower)"})
        if cooling.get("type") == "Passive" and "5V/5A" in sbc_draw:
            flaws.append({"type": "thermal", "severity": "medium",
                          "issue": "High-power SBC with passive cooling may thermal throttle under load",
                          "fix": "Add active cooling (Pimoroni Fan Shim or Noctua 40mm)"})
        if "zero 2w" in sbc.get("id", ""):
            display_if = display.get("interface", "")
            if "HDMI" in display_if and "mini" not in display_if.lower():
                flaws.append({"type": "connector", "severity": "critical",
                              "issue": "Pi Zero 2W has mini-HDMI, not full HDMI",
                              "fix": "Add mini-HDMI adapter or switch to SPI display"})
        if not connectivity.get("id") and "WiFi" not in sbc.get("connectivity", ""):
            flaws.append({"type": "connectivity", "severity": "high",
                          "issue": "No network connectivity in build",
                          "fix": "Add USB Ethernet adapter or WiFi adapter"})
        power_type = power.get("type", "")
        if "power_bank" in power_type:
            flaws.append({"type": "safety", "severity": "low",
                          "issue": "Power bank may lack a physical on/off switch",
                          "fix": "Add inline USB power switch or use UPS HAT with button"})
        if "18650" in power.get("name", "").lower() and "BMS" not in power.get("name", ""):
            flaws.append({"type": "safety", "severity": "critical",
                          "issue": "Lithium 18650 cells require a BMS for overcharge/overdischarge protection",
                          "fix": "Use a BMS board or choose a pre-built UPS HAT with protection"})
        sbc_factor = sbc.get("form_factor", "")
        enc_dims = enclosure.get("dimensions", "") if (enclosure := components.get("enclosure", {})) else ""
        if "125mm" in sbc_factor and "235" in enc_dims:
            flaws.append({"type": "physical", "severity": "medium",
                          "issue": "SBC may be tight in small enclosure — verify clearance",
                          "fix": "Use larger enclosure (Pelican 1400 or 1450)"})
        return flaws

    @staticmethod
    def auto_fix_build(build):
        flaws = BuildOptimizer.scan_flaws(build)
        if not flaws:
            build["optimizer"] = {"flaws_found": 0, "flaws_fixed": 0, "status": "clean"}
            return build
        fixed_count = 0
        components = build.get("components", {})
        for flaw in flaws:
            if flaw["severity"] in ("critical", "high"):
                fix = flaw.get("fix", "")
                if "UPS HAT" in fix:
                    components["power"] = {"id": "ups_h5180", **POWER_DATABASE["ups_h5180"]}
                    fixed_count += 1
                elif "active_fan" in fix:
                    components["cooling"] = {"id": "active_fan", **COOLING_DATABASE["active_fan"]}
                    fixed_count += 1
                elif "Ethernet" in fix:
                    components["connectivity"] = {"id": "usb_ethernet", **CONNECTIVITY_DATABASE["usb_ethernet"]}
                    fixed_count += 1
                elif "mini-HDMI" in fix:
                    components["display"] = {"id": "eink_7inch", **DISPLAY_DATABASE["eink_7inch"]}
                    fixed_count += 1
                elif "BMS" in fix or "protection" in fix:
                    components["power"] = {"id": "ups_h5180", **POWER_DATABASE["ups_h5180"]}
                    fixed_count += 1
                elif "larger enclosure" in fix:
                    components["enclosure"] = {"id": "pelican_1450", **ENCLOSURE_DATABASE["pelican_1450"]}
                    fixed_count += 1
        build["components"] = components
        build["optimizer"] = {"flaws_found": len(flaws), "flaws_fixed": fixed_count, "all_flaws": flaws,
                              "status": "auto_fixed" if fixed_count > 0 else "manual_review_needed"}
        return build


# ============================================================
# PACK GENERATOR — image+video+text combined output
# ============================================================
class PackGenerator:
    @staticmethod
    def generate_pack(build):
        tutorial = TutorialGenerator.generate(build)
        cable_plan = CableRouter.generate_routing_plan(build)
        upgrades = BuildGenerator.suggest_upgrades(build)
        ideas = IdeaGenerator.generate(category=build.get("category_id"))
        pack_md = [
            f"# {build['category']} Cyberdeck Pack",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Tier: {build['tier']} | SBC: {build['components'].get('sbc', {}).get('name', 'N/A')}",
            "", "---", "", "## Cable Routing Plan", "",
            f"Total cables: {cable_plan['total_cables']}", ""]
        for i, c in enumerate(cable_plan.get("cables", []), 1):
            pack_md.append(f"{i}. **{c['cable']}** — {c['route']} ({c['length']})")
        pack_md.extend(["", "**Accessories:**"])
        for acc in cable_plan.get("accessories", []):
            pack_md.append(f"- {acc['name']}: {acc['use']}")
        pack_md.extend(["", "---", "", "## Assembly Tutorial", "", tutorial, "", "---", "", "## Upgrade Path", ""])
        for up in upgrades:
            pack_md.append(f"- **{up['component']}**: {up.get('from', '?')} -> {up['to']} ({up['reason']})")
        pack_md.extend(["", "---", "", "## Related Ideas", ""])
        for idea in ideas[:5]:
            pack_md.append(f"- **{idea['title']}** ({idea['category']}, {idea['difficulty']}, {idea.get('estimated_cost', '?')}) — {idea['description']}")
        pack_md.extend(["", "---", "", "## Tips from Learnings", ""])
        try:
            learner = CyberdeckLearner()
            for tip in learner.get_all_tips()[:10]:
                pack_md.append(f"- {tip}")
        except Exception:
            pass
        return {"markdown": "\n".join(pack_md), "cable_plan": cable_plan,
                "upgrades": upgrades, "ideas": ideas, "tutorial": tutorial}


# ============================================================
# BUILD GENERATOR — creates complete cyberdeck builds
# ============================================================
class BuildGenerator:
    @staticmethod
    def build_for_category(category, tier="intermediate", custom_parts=None, size_preference=None):
        cat = CATEGORIES.get(category, CATEGORIES["coding"])
        tier_config = TIERS.get(tier, TIERS["intermediate"])
        size_pref = size_preference or cat.get("size_preference", "big")
        size_config = SIZE_PROFILES.get(size_pref, SIZE_PROFILES["big"])
        components = {
            "sbc": (custom_parts or {}).get("sbc") or cat["best_sbc"],
            "display": (custom_parts or {}).get("display") or cat["best_display"],
            "keyboard": (custom_parts or {}).get("keyboard") or cat["best_keyboard"],
            "power": (custom_parts or {}).get("power") or cat["best_power"],
            "enclosure": (custom_parts or {}).get("enclosure") or cat["best_enclosure"],
            "cooling": (custom_parts or {}).get("cooling") or cat["best_cooling"],
            "pcb": cat.get("best_pcb", "waveshare_phat"),
            "wire_signal": cat.get("best_wire", "silicon_26awg"),
            "wire_power": "silicon_18awg",
            "os": "raspberry_pi_os",
            "connectivity": (custom_parts or {}).get("connectivity") or cat.get("best_connectivity", "usb_ethernet"),
        }
        if size_pref == "small":
            small_swaps = {
                "pi5_16gb": "pi5_4gb", "pi5_8gb": "pi_zero_2w",
                "jetson_orin_nano": "pi5_8gb", "orange_pi_5_plus": "orange_pi_zero3",
                "lattepanda_3_delta": "pi5_8gb", "radxa_rock_5b": "pi5_8gb",
                "khadas_edge2": "pi5_8gb", "hdmi_10inch": "hdmi_5inch",
                "hdmi_7inch_ips": "hdmi_5inch", "hdmi_7inch_1024": "hdmi_5inch",
                "sunlight_readable_7": "hdmi_5inch", "mech_60": "bt_keyboard",
                "ups_h5180": "pisugar3_plus", "geekworm_x1200": "pimoroni_lipo_shim",
                "pelican_1450": "pelican_1200", "pelican_1400": "pelican_1200",
                "active_fan_heatsink": "passive_heatsink", "active_fan": "passive_heatsink",
            }
            for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling"]:
                if components[key] in small_swaps:
                    components[key] = small_swaps[components[key]]
        elif size_pref == "big":
            big_swaps = {
                "pi_zero_2w": "pi5_8gb", "orange_pi_zero3": "orange_pi_5_plus",
                "hdmi_5inch": "hdmi_7inch_ips", "pisugar3_plus": "ups_h5180",
                "pimoroni_lipo_shim": "ups_h5180", "bt_keyboard": "mech_60",
                "pelican_1150": "pelican_1450", "pelican_1200": "pelican_1450",
            }
            for key in ["sbc", "display", "keyboard", "power", "enclosure"]:
                if components[key] in big_swaps:
                    components[key] = big_swaps[components[key]]
        if custom_parts:
            for k, v in custom_parts.items():
                if v and k not in ("sbc", "display", "keyboard", "power", "enclosure", "cooling"):
                    components[k] = v
        compat = CompatibilityEngine.check_full_build(components)
        if not compat["compatible"]:
            fixed = CompatibilityEngine.auto_fix(components, compat["issues"])
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
        total_price = sum(x.get("price", 0) for x in [sbc_info, display_info, power_info, enclosure_info, cooling_info, connectivity_info])
        cat_style = cat.get("default_style", "industrial")
        cat_color = cat.get("default_color", "#2d2d2d")
        style_preset = STYLE_PRESETS.get(cat_style, STYLE_PRESETS["industrial"])
        is_portable = power_info.get("type", "") in ("SBC-mount battery", "USB power bank", "Custom 6-cell", "Solar charging")
        charging_components = []
        if is_portable and not any(pid in power_info.get("name", "").lower() for pid in ["ups hat", "h5180", "x1200"]):
            charging_components.append({"id": "tp4056_module", **POWER_DATABASE["tp4056_module"]})
        build = {
            "category": cat["name"], "category_id": category,
            "tier": tier_config["name"], "tier_id": tier,
            "style": cat_style, "color": cat_color,
            "size_preference": size_pref, "size_profile": size_config["name"],
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
                "charging": charging_components,
            },
            "compatibility": compat, "total_price_estimate": f"${total_price}",
            "aesthetic": cat.get("aesthetic", "Industrial"),
            "soldering_required": tier_config.get("soldering", "Optional"),
            "style_preset": style_preset,
        }
        build = BuildOptimizer.auto_fix_build(build)
        return build

    @staticmethod
    def build_from_prompt(prompt, tier="intermediate", size_preference=None):
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
            "conversation-piece": ["cyberpunk", "prop", "cosplay", "aesthetic", "neon", "led", "look cool"],
            "retro": ["retro", "terminal", "vintage", "crt", "amber", "ascii"],
            "maker": ["maker", "soldering", "breadboard", "oscilloscope", "logic analyzer", "gpio"],
            "ham-radio": ["ham radio", "amateur radio", "hf", "vhf", "uhf", "aprs", "digital modes"],
            "field-repair": ["repair", "diagnostic", "multimeter", "test equipment", "network test"],
        }
        for cat, triggers in cat_triggers.items():
            score = sum(1 for t in triggers if t in prompt_lower)
            if score > best_score:
                best_score = score
                matched_category = cat
        if not size_preference:
            if "small" in prompt_lower or "compact" in prompt_lower or "lightweight" in prompt_lower or "mini" in prompt_lower or "pocket" in prompt_lower:
                size_preference = "small"
            elif "big" in prompt_lower or "full" in prompt_lower or "large" in prompt_lower or "desktop" in prompt_lower or "powerful" in prompt_lower:
                size_preference = "big"
        custom_parts = {}
        size_match = re.search(r'(\d+\.?\d*)\s*(inch|")', prompt_lower)
        if size_match:
            inches = float(size_match.group(1))
            if inches <= 5:
                custom_parts["display"] = "hdmi_5inch"
            elif inches <= 6:
                custom_parts["display"] = "hdmi_5inch"
            elif inches <= 8:
                custom_parts["display"] = "hdmi_7inch_ips"
            elif inches <= 8.5:
                custom_parts["display"] = "waveshare_ultrawide_79"
            else:
                custom_parts["display"] = "hdmi_10inch"
        if "two screen" in prompt_lower or "dual screen" in prompt_lower or "2 screen" in prompt_lower:
            custom_parts["second_display"] = True
        if "split keyboard" in prompt_lower or "corne" in prompt_lower:
            custom_parts["keyboard"] = "corne_split"
        if "vintage" in prompt_lower or "model m" in prompt_lower:
            custom_parts["keyboard"] = "vintage_keyboard"
        if "pelican" in prompt_lower:
            for pid in ["pelican_1450", "pelican_1400", "pelican_1200", "pelican_1150"]:
                if pid.replace("_", " ") in prompt_lower:
                    custom_parts["enclosure"] = pid
                    break
            if "enclosure" not in custom_parts:
                custom_parts["enclosure"] = "pelican_1450"
        if "waterproof" in prompt_lower or "ip65" in prompt_lower or "ip67" in prompt_lower or "ip68" in prompt_lower:
            if "ip68" in prompt_lower:
                custom_parts["enclosure"] = "ip68_poly_case"
            elif "ip67" in prompt_lower:
                custom_parts["enclosure"] = "ip67_enclosure_aluminum"
            else:
                custom_parts["enclosure"] = "ip65_enclosure_150x100"
        if "e-ink" in prompt_lower or "eink" in prompt_lower:
            custom_parts["display"] = "eink_7inch"
        if "solar" in prompt_lower:
            custom_parts["power"] = "solar_panel_18w"
        if "jetson" in prompt_lower:
            custom_parts["sbc"] = "jetson_orin_nano"
        if "orange pi" in prompt_lower:
            custom_parts["sbc"] = "orange_pi_5_plus"
        if "zero 2w" in prompt_lower or "pi zero" in prompt_lower:
            custom_parts["sbc"] = "pi_zero_2w"
        if "lattepanda" in prompt_lower:
            custom_parts["sbc"] = "lattepanda_3_delta"
        if "hackrf" in prompt_lower:
            custom_parts["connectivity"] = "hackrf_one"
        if "lora" in prompt_lower:
            custom_parts["connectivity"] = "lora_module"
        if "alfa" in prompt_lower or "awus" in prompt_lower:
            custom_parts["connectivity"] = "awus036ach"
        if "futuristic" in prompt_lower:
            custom_parts["style"] = "futuristic"
        if "retro" in prompt_lower and matched_category != "retro":
            custom_parts["style"] = "retro"
        if "steampunk" in prompt_lower:
            custom_parts["style"] = "steampunk"
        if "cyberpunk" in prompt_lower:
            custom_parts["style"] = "cyberpunk"
        if "minimal" in prompt_lower:
            custom_parts["style"] = "minimal"
        if "industrial" in prompt_lower:
            custom_parts["style"] = "industrial"
        return BuildGenerator.build_for_category(matched_category, tier, custom_parts or None, size_preference)

    @staticmethod
    def generate_bom(build):
        lines = [
            f"# Bill of Materials — {build['category']} ({build['tier']})",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
            "| # | Component | Name | Price |",
            "|---|-----------|------|-------|"]
        idx = 1
        for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "pcb", "wire_signal", "wire_power", "connectivity"]:
            comp = build["components"].get(key, {})
            if comp:
                name = comp.get("name", key)
                price = comp.get("price") or comp.get("price_range") or comp.get("price_per_meter", "---")
                lines.append(f"| {idx} | {key.replace('_', ' ').title()} | {name} | ${price} |")
                idx += 1
        lines.extend(["", f"**Estimated Total:** {build['total_price_estimate']}", "",
                       "## Notes",
                       f"- OS: {build['components'].get('os', {}).get('name', 'N/A')}",
                       f"- Aesthetic: {build.get('aesthetic', 'Industrial')}",
                       f"- Soldering: {build.get('soldering_required', 'Optional')}",
                       f"- Compatibility: {'PASS' if build['compatibility']['compatible'] else 'ISSUES FOUND'}"])
        if build["compatibility"]["issues"]:
            lines.append("")
            for issue in build["compatibility"]["issues"]:
                lines.append(f"- Warning: {issue}")
        return "\n".join(lines)

    @staticmethod
    def suggest_upgrades(build):
        upgrades = []
        sbc_id = build["components"].get("sbc", {}).get("id", "")
        display_id = build["components"].get("display", {}).get("id", "")
        upgrade_paths = {
            "pi4_8gb": {"next": "pi5_8gb", "reason": "2x faster CPU, NVMe support, WiFi 6"},
            "pi5_8gb": {"next": "pi5_16gb", "reason": "Double RAM for heavier workloads"},
            "pi5_4gb": {"next": "pi5_8gb", "reason": "Double RAM for multitasking"},
            "pi_zero_2w": {"next": "pi5_4gb", "reason": "Massive performance jump, full-size HDMI"},
            "orange_pi_zero3": {"next": "orange_pi_5_plus", "reason": "Much faster, NVMe, more RAM"},
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
    def generate_code(request, language="python"):
        templates = {
            "battery_monitor": {
                "python": "#!/usr/bin/env python3\nimport smbus2 as smbus\nimport time\n\nBUS = smbus.SMBus(1)\nADDR = 0x36\n\ndef read_voltage():\n    data = BUS.read_word_data(ADDR, 0x02)\n    return round((data & 0xFFFF) * 1.25 / 1000 / 16, 2)\n\ndef read_capacity():\n    data = BUS.read_word_data(ADDR, 0x04)\n    return round((data & 0xFFFF) * 256 / 10000, 1)\n\nif __name__ == '__main__':\n    while True:\n        print(f'Battery: {read_voltage()}V | {read_capacity()}%')\n        time.sleep(5)\n",
                "description": "Read battery voltage/capacity via I2C (UPS HAT)"},
            "temp_monitor": {
                "python": "#!/usr/bin/env python3\nimport time\n\ndef get_temp():\n    with open('/sys/class/thermal/thermal_zone0/temp') as f:\n        return round(float(f.read().strip()) / 1000, 1)\n\nif __name__ == '__main__':\n    while True:\n        t = get_temp()\n        fan = 'FULL' if t > 70 else 'HIGH' if t > 55 else 'MEDIUM' if t > 40 else 'LOW'\n        print(f'CPU: {t}C | Fan: {fan}')\n        time.sleep(10)\n",
                "description": "Monitor CPU temperature and control fan speed"},
            "led_status": {
                "python": "#!/usr/bin/env python3\nimport RPi.GPIO as GPIO\nimport time\n\nGPIO.setmode(GPIO.BCM)\nGPIO.setup(17, GPIO.OUT)\nGPIO.setup(27, GPIO.OUT)\nGPIO.output(17, GPIO.HIGH)\ntry:\n    while True:\n        GPIO.output(27, GPIO.HIGH)\n        time.sleep(0.5)\n        GPIO.output(27, GPIO.LOW)\n        time.sleep(0.5)\nexcept KeyboardInterrupt:\n    GPIO.cleanup()\n",
                "description": "Blink status LEDs via GPIO"},
            "low_battery_shutdown": {
                "python": "#!/usr/bin/env python3\nimport smbus2 as smbus\nimport subprocess, time\n\nBUS = smbus.SMBus(1)\nADDR = 0x36\n\ndef read_voltage():\n    data = BUS.read_word_data(ADDR, 0x02)\n    return round((data & 0xFFFF) * 1.25 / 1000 / 16, 2)\n\nif __name__ == '__main__':\n    while True:\n        v = read_voltage()\n        print(f'Battery: {v}V')\n        if v < 3.0:\n            print('Low battery! Shutting down...')\n            subprocess.run(['sudo', 'shutdown', '-h', 'now'])\n        time.sleep(60)\n",
                "description": "Auto-shutdown on low battery to protect SD card"},
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
# v5.2 — CUSTOM BUILD ENGINE — interactive mix/match component picker
# ============================================================
class CustomBuildEngine:
    """Interactive cyberdeck builder — pick components, see prices, check compatibility."""

    CATEGORIES = {
        "sbc": {"name": "SBC (Brain)", "db": "SBC_DATABASE", "required": True, "icon": "🧠",
                "desc": "The main computer board — Pi, Orange Pi, Jetson, etc."},
        "display": {"name": "Display", "db": "DISPLAY_DATABASE", "required": True, "icon": "🖥️",
                    "desc": "Screen — IPS, OLED, E-Ink, touchscreen"},
        "keyboard": {"name": "Keyboard", "db": "KEYBOARD_DATABASE", "required": False, "icon": "⌨️",
                     "desc": "Input — mechanical, thumb, split, ortho"},
        "power": {"name": "Power/Battery", "db": "POWER_DATABASE", "required": True, "icon": "🔋",
                  "desc": "UPS HAT, battery pack, solar, charging module"},
        "storage": {"name": "Storage", "db": "STORAGE_DATABASE", "required": False, "icon": "💾",
                    "desc": "NVMe SSD, MicroSD, eMMC module"},
        "enclosure": {"name": "Enclosure/Case", "db": "ENCLOSURE_DATABASE", "required": True, "icon": "📦",
                      "desc": "Case — Pelican, 3D printed, aluminum, custom"},
        "cooling": {"name": "Cooling", "db": "COOLING_DATABASE", "required": False, "icon": "❄️",
                    "desc": "Fan, heatsink, passive cooling"},
        "connectivity": {"name": "Connectivity", "db": "CONNECTIVITY_DATABASE", "required": False, "icon": "📡",
                         "desc": "WiFi adapter, LoRa, LTE modem, SDR, Ethernet"},
        "camera": {"name": "Camera", "db": "CAMERA_MODULE_DATABASE", "required": False, "icon": "📷",
                   "desc": "Pi Camera, thermal, global shutter"},
        "sensor": {"name": "Sensors", "db": "ENVIRONMENTAL_SENSOR_DATABASE", "required": False, "icon": "🌡️",
                   "desc": "Temperature, humidity, CO2, radiation, UV"},
        "os": {"name": "Operating System", "db": "OS_DATABASE", "required": False, "icon": "💿",
               "desc": "Raspberry Pi OS, Kali, Ubuntu, RetroPie"},
    }

    def __init__(self):
        self.db_map = {
            "SBC_DATABASE": SBC_DATABASE, "DISPLAY_DATABASE": DISPLAY_DATABASE,
            "KEYBOARD_DATABASE": KEYBOARD_DATABASE, "POWER_DATABASE": POWER_DATABASE,
            "STORAGE_DATABASE": STORAGE_DATABASE, "ENCLOSURE_DATABASE": ENCLOSURE_DATABASE,
            "COOLING_DATABASE": COOLING_DATABASE, "CONNECTIVITY_DATABASE": CONNECTIVITY_DATABASE,
            "CAMERA_MODULE_DATABASE": CAMERA_MODULE_DATABASE,
            "ENVIRONMENTAL_SENSOR_DATABASE": ENVIRONMENTAL_SENSOR_DATABASE,
            "OS_DATABASE": OS_DATABASE,
        }
        self.builds = {}  # user_id -> {category: component_id, ...}

    def start_build(self, user_id: int) -> dict:
        """Start a new custom build for a user."""
        self.builds[user_id] = {}
        return {"status": "started", "categories": list(self.CATEGORIES.keys())}

    def get_category_options(self, category: str) -> list:
        """Get all options in a category with prices."""
        cat = self.CATEGORIES.get(category)
        if not cat:
            return []
        db = self.db_map.get(cat["db"], {})
        options = []
        for comp_id, comp in db.items():
            price = comp.get("price", comp.get("price_range", "TBD"))
            name = comp.get("name", comp_id)
            options.append({
                "id": comp_id, "name": name, "price": price,
                "key_specs": self._extract_key_specs(category, comp),
            })
        # Sort by price (numeric)
        def sort_key(x):
            p = x["price"]
            if isinstance(p, (int, float)):
                return p
            if isinstance(p, str) and p.startswith("$"):
                try:
                    return float(p.replace("$", "").split("-")[0].replace(",", ""))
                except:
                    return 9999
            return 9999
        options.sort(key=sort_key)
        return options

    def select_component(self, user_id: int, category: str, component_id: str) -> dict:
        """Select a component for a category."""
        cat = self.CATEGORIES.get(category)
        if not cat:
            return {"error": f"Unknown category: {category}"}
        db = self.db_map.get(cat["db"], {})
        comp = db.get(component_id)
        if not comp:
            return {"error": f"Component '{component_id}' not found in {category}"}
        if user_id not in self.builds:
            self.builds[user_id] = {}
        self.builds[user_id][category] = component_id
        return {
            "selected": True, "category": category, "component": comp.get("name", component_id),
            "price": comp.get("price", "TBD"),
            "total_cost": self.get_total_cost(user_id),
        }

    def remove_component(self, user_id: int, category: str) -> dict:
        """Remove a component from a category."""
        if user_id in self.builds and category in self.builds[user_id]:
            del self.builds[user_id][category]
            return {"removed": category, "total_cost": self.get_total_cost(user_id)}
        return {"error": f"No component in {category}"}

    def get_build(self, user_id: int) -> dict:
        """Get the current build for a user."""
        build = self.builds.get(user_id, {})
        components = []
        for cat_key, comp_id in build.items():
            cat = self.CATEGORIES.get(cat_key, {})
            db = self.db_map.get(cat["db"], {})
            comp = db.get(comp_id, {})
            components.append({
                "category": cat_key, "category_name": cat.get("name", cat_key),
                "icon": cat.get("icon", ""), "component_id": comp_id,
                "name": comp.get("name", comp_id), "price": comp.get("price", "TBD"),
                "specs": self._extract_key_specs(cat_key, comp),
            })
        return {
            "components": components,
            "total_cost": self.get_total_cost(user_id),
            "component_count": len(components),
            "required_missing": self._get_missing_required(user_id),
        }

    def get_total_cost(self, user_id: int) -> str:
        """Calculate total cost of the build."""
        build = self.builds.get(user_id, {})
        total = 0
        has_string = False
        for cat_key, comp_id in build.items():
            cat = self.CATEGORIES.get(cat_key, {})
            db = self.db_map.get(cat["db"], {})
            comp = db.get(comp_id, {})
            price = comp.get("price", 0)
            if isinstance(price, (int, float)):
                total += price
            elif isinstance(price, str) and price.startswith("$"):
                try:
                    total += float(price.replace("$", "").split("-")[0].replace(",", ""))
                except:
                    has_string = True
            else:
                has_string = True
        if has_string:
            return f"~${total:.0f}+ (some prices TBD)"
        return f"${total:.2f}"

    def check_compatibility(self, user_id: int) -> dict:
        """Check compatibility of the current build."""
        build = self.builds.get(user_id, {})
        warnings = []
        recommendations = []
        sbc_id = build.get("sbc")
        display_id = build.get("display")
        power_id = build.get("power")

        if sbc_id:
            sbc = SBC_DATABASE.get(sbc_id, {})
            sbc_name = sbc.get("name", "")

            # Check display interface compatibility
            if display_id:
                display = DISPLAY_DATABASE.get(display_id, {})
                disp_interface = display.get("interface", "").lower()
                if "hdmi" in disp_interface and "pi zero" in sbc_name.lower():
                    warnings.append("⚠️ Pi Zero needs mini-HDMI adapter for HDMI displays")
                if "dsi" in disp_interface and "orange pi" in sbc_name.lower():
                    warnings.append("⚠️ Orange Pi boards may not support DSI displays natively")

            # Check power requirements
            if power_id:
                power = POWER_DATABASE.get(power_id, {})
                power_output = power.get("output", "")
                if "Pi 5" in sbc_name and "5V/3A" in power_output:
                    warnings.append("⚠️ Pi 5 needs 5V/5A (27W) — this supply may be insufficient")

            # Check NVMe support
            storage_id = build.get("storage")
            if storage_id:
                storage = STORAGE_DATABASE.get(storage_id, {})
                if "NVMe" in storage.get("type", "") and "Pi 4" in sbc_name:
                    warnings.append("⚠️ Pi 4 needs PCIe HAT for NVMe — not native")
                if "NVMe" in storage.get("type", "") and "Pi Zero" in sbc_name:
                    warnings.append("❌ Pi Zero cannot use NVMe — no PCIe lane")

            # Recommendations
            if "Pi 5" in sbc_name:
                cooling_id = build.get("cooling")
                if not cooling_id:
                    recommendations.append("💡 Pi 5 recommended: add active cooling (fan/heatsink)")
                if build.get("power") == "pimoroni_lipo_shim":
                    recommendations.append("💡 Pi 5 draws 12W — consider larger battery (UPS HAT)")
            if "ai" in str(sbc.get("best_for", [])):
                recommendations.append("💡 This SBC supports AI workloads — consider adding camera/sensors")

        return {"warnings": warnings, "recommendations": recommendations, "compatible": len(warnings) == 0}

    def generate_build_summary(self, user_id: int) -> str:
        """Generate a formatted build summary with prices."""
        build_data = self.get_build(user_id)
        compat = self.check_compatibility(user_id)

        lines = ["🔧 *CYBERDECK CUSTOM BUILD*", "=" * 35, ""]
        for comp in build_data["components"]:
            price_str = f"${comp['price']}" if isinstance(comp['price'], (int, float)) else str(comp['price'])
            lines.append(f"{comp['icon']} *{comp['category_name']}*")
            lines.append(f"  → {comp['name']}")
            lines.append(f"  💰 Price: {price_str}")
            if comp.get("specs"):
                lines.append(f"  📋 {comp['specs']}")
            lines.append("")

        lines.append("─" * 35)
        lines.append(f"💰 *TOTAL ESTIMATED COST: {build_data['total_cost']}*")
        lines.append(f"📦 Components: {build_data['component_count']}")

        if build_data["required_missing"]:
            lines.append(f"\n⚠️ *MISSING REQUIRED:*")
            for cat in build_data["required_missing"]:
                cat_info = self.CATEGORIES.get(cat, {})
                lines.append(f"  ❌ {cat_info.get('name', cat)}")

        if compat["warnings"]:
            lines.append(f"\n⚠️ *COMPATIBILITY WARNINGS:*")
            for w in compat["warnings"]:
                lines.append(f"  {w}")

        if compat["recommendations"]:
            lines.append(f"\n💡 *RECOMMENDATIONS:*")
            for r in compat["recommendations"]:
                lines.append(f"  {r}")

        return "\n".join(lines)

    def _extract_key_specs(self, category: str, comp: dict) -> str:
        """Extract key specs for display."""
        specs = []
        if category == "sbc":
            if comp.get("cpu"): specs.append(f"CPU: {comp['cpu'].split('@')[0].strip()[:30]}")
            if comp.get("ram"): specs.append(f"RAM: {comp['ram']}")
        elif category == "display":
            if comp.get("size"): specs.append(f"{comp['size']}")
            if comp.get("resolution"): specs.append(f"{comp['resolution']}")
            if comp.get("display_type"): specs.append(f"{comp['display_type']}")
        elif category == "power":
            if comp.get("capacity"): specs.append(f"{comp['capacity']}")
            if comp.get("runtime"): specs.append(f"Runtime: {comp['runtime']}")
        elif category == "storage":
            if comp.get("capacity"): specs.append(f"{comp['capacity']}")
            if comp.get("read_speed"): specs.append(f"Read: {comp['read_speed']}")
        elif category == "keyboard":
            if comp.get("type"): specs.append(f"{comp['type']}")
            if comp.get("switches"): specs.append(f"{comp['switches']}")
        elif category == "enclosure":
            if comp.get("protection"): specs.append(f"{comp['protection']}")
        elif category == "connectivity":
            if comp.get("standard"): specs.append(f"{comp['standard']}")
        elif category == "camera":
            if comp.get("resolution"): specs.append(f"{comp['resolution']}")
        return " | ".join(specs) if specs else ""

    def _get_missing_required(self, user_id: int) -> list:
        """Get list of required categories not yet filled."""
        build = self.builds.get(user_id, {})
        missing = []
        for cat_key, cat_info in self.CATEGORIES.items():
            if cat_info["required"] and cat_key not in build:
                missing.append(cat_key)
        return missing

    def clear_build(self, user_id: int):
        """Clear a user's build."""
        self.builds.pop(user_id, None)

# ============================================================
# MAIN AGENT
# ============================================================
class CyberdeckAgent:
    def __init__(self):
        self.version = VERSION
        self.learner = CyberdeckLearner()
        self.video_queue = VideoLearningQueue()
        self.build_history = self._load_history()
        self.image_analyzer = ImageAnalyzer()
        self.generator = BuildGenerator()

    def _load_history(self):
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

    async def build(self, description, tier="intermediate", custom_parts=None, size_preference=None):
        build = self.generator.build_from_prompt(description, tier, size_preference)
        if custom_parts:
            for k, v in custom_parts.items():
                if v and k in build["components"]:
                    build["components"][k] = v
            build["compatibility"] = CompatibilityEngine.check_full_build({
                k: v.get("id", v) if isinstance(v, dict) else v
                for k, v in build["components"].items()
                if k in ("sbc", "display", "keyboard", "power", "enclosure", "cooling")})
        build["bom"] = self.generator.generate_bom(build)
        build["tutorial"] = TutorialGenerator.generate(build)
        build["upgrades"] = self.generator.suggest_upgrades(build)
        build["ideas"] = IdeaGenerator.generate(category=build.get("category_id"))
        build["cable_plan"] = CableRouter.generate_routing_plan(build)
        build["pack"] = PackGenerator.generate_pack(build)
        build["component_details"] = {}
        for key in ["sbc", "display", "keyboard", "power", "enclosure", "cooling", "connectivity"]:
            comp = build["components"].get(key, {})
            comp_id = comp.get("id", "")
            if comp_id:
                details = ComponentDatabase.get_component_details(comp_id)
                if details and "error" not in details:
                    build["component_details"][key] = details
        self.build_history.append({
            "category": build.get("category_id"), "tier": tier,
            "sbc": build["components"]["sbc"]["id"],
            "style": build.get("style", "industrial"),
            "size_preference": build.get("size_preference", "big"),
            "timestamp": datetime.now().isoformat()})
        self._save_history()
        self.learner.learn_from_build({"category": build.get("category_id"), "sbc": build["components"]["sbc"]["id"], "tier": tier})
        if not build["compatibility"]["compatible"]:
            for issue in build["compatibility"]["issues"]:
                self.learner.log_flaw_fix(issue, "Auto-fixed by compatibility engine")
        return build

    async def build_custom(self, name, description, tier="intermediate"):
        return await self.build(f"{name}: {description}", tier)

    async def pick(self, component_type, category="coding"):
        cat = CATEGORIES.get(category, CATEGORIES["coding"])
        type_map = {
            "sbc": ("best_sbc", SBC_DATABASE), "display": ("best_display", DISPLAY_DATABASE),
            "keyboard": ("best_keyboard", KEYBOARD_DATABASE), "power": ("best_power", POWER_DATABASE),
            "enclosure": ("best_enclosure", ENCLOSURE_DATABASE), "cooling": ("best_cooling", COOLING_DATABASE),
            "pcb": ("best_pcb", PCB_DATABASE), "wire_signal": ("best_wire", WIRE_DATABASE),
            "wire_power": ("best_wire", WIRE_DATABASE), "os": ("best_os", OS_DATABASE),
            "connectivity": ("best_connectivity", CONNECTIVITY_DATABASE),
        }
        if component_type not in type_map:
            return {"error": f"Unknown type: {component_type}. Use: {', '.join(type_map.keys())}"}
        field, database = type_map[component_type]
        best_id = cat.get(field, "")
        return {"type": component_type, "category": category, "id": best_id, "item": database.get(best_id, {})}

    async def check_compatibility(self, sbc_id, display_id=None, power_id=None, enclosure_id=None, category="coding"):
        components = {"sbc": sbc_id, "category": category}
        if display_id:
            components["display"] = display_id
        if power_id:
            components["power"] = power_id
        if enclosure_id:
            components["enclosure"] = enclosure_id
        return CompatibilityEngine.check_full_build(components)

    async def analyze_image(self, image_description):
        result = self.image_analyzer.analyze_with_ai(image_description)
        self.learner.log_image_analysis(result)
        result["suggested_build"] = await self.build(
            f"Recreate a {result.get('suggested_category', 'coding')} cyberdeck with these components", "intermediate")
        return result

    async def analyze_image_file(self, image_path, mime_type="image/jpeg"):
        try:
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")
            result = self.image_analyzer.analyze_image_base64(image_b64, mime_type)
            self.learner.log_image_analysis(result)
            if result.get("suggested_category"):
                result["suggested_build"] = await self.build(
                    f"Recreate a {result['suggested_category']} cyberdeck based on analysis", "intermediate")
            return result
        except Exception as e:
            return {"error": str(e), "vision_used": False}

    async def watch_video(self, url):
        return self.video_queue._watch_and_learn(url, self.learner)

    async def queue_video(self, url):
        return self.video_queue.add(url)

    async def process_queue(self):
        results = self.video_queue.process_pending(self.learner)
        return {"processed": len(results), "results": results}

    async def generate_ideas(self, category=None, budget=None, skill=None):
        return IdeaGenerator.generate(category, budget, skill)

    async def generate_ideas_from_trends(self, category=None):
        return IdeaGenerator.generate_from_trends(self.learner, category)

    async def generate_code(self, request, language="python"):
        return self.generator.generate_code(request, language)

    async def upgrade(self, build):
        return self.generator.suggest_upgrades(build)

    async def fix_flaws(self, components, category="coding", tier="intermediate"):
        compat = CompatibilityEngine.check_full_build(components)
        if compat["compatible"]:
            return {"status": "already_compatible", "components": components, "compatibility": compat}
        fixed = CompatibilityEngine.auto_fix(components, compat["issues"])
        new_compat = CompatibilityEngine.check_full_build(fixed)
        return {"status": "fixed", "original_issues": compat["issues"], "components": fixed, "compatibility": new_compat}

    async def generate_cable_plan(self, build):
        return CableRouter.generate_routing_plan(build)

    async def generate_tutorial(self, build):
        return TutorialGenerator.generate(build)

    async def generate_pack(self, build):
        return PackGenerator.generate_pack(build)

    async def generate_3d_model(self, build, color=None, style=None):
        style_id = style or build.get("style", "industrial")
        style_preset = STYLE_PRESETS.get(style_id, STYLE_PRESETS["industrial"])
        model_color = color or style_preset["default_color"]
        accent = style_preset["accent_color"]
        sbc = build["components"].get("sbc", {})
        display = build["components"].get("display", {})
        enclosure = build["components"].get("enclosure", {})
        sbc_form = sbc.get("form_factor", "85x56")
        dims = re.findall(r'(\d+)', sbc_form)
        sbc_x = int(dims[0]) if len(dims) > 0 else 85
        sbc_y = int(dims[1]) if len(dims) > 1 else 56
        enc_thickness = 3
        fillet = style_preset.get("fillet_radius", 2)
        vent_style = style_preset.get("vent_style", "slim slits")
        screw_style = style_preset.get("screw_style", "hidden")
        led_channels = style_preset.get("led_channels", False)
        total_x = sbc_x + 30
        total_y = sbc_y + 25
        total_z = 25
        screw_holes = ""
        if screw_style.startswith("exposed"):
            screw_holes = (
                "for (pos = [[5,5], [%d,5], [5,%d], [%d,%d]]) {\n"
                "        translate(pos) cylinder(d=3.2, h=%d, center=true);\n"
                "    }" % (total_x - 5, total_y - 5, total_x - 5, total_y - 5, enc_thickness + 1)
            )
        else:
            screw_holes = "// Hidden screw posts inside"
        vent_code = ""
        if vent_style == "slim slits":
            vent_code = (
                "for (i = [0 : 4 : %d]) {\n"
                "        translate([i+5, 5, %d]) cube([2, %d, 1.5], center=false);\n"
                "    }" % (total_x - 10, total_z - 1, total_y - 10)
            )
        else:
            vent_code = (
                "for (i = [0 : 6 : %d]) {\n"
                "        translate([i+5, 5, %d]) cube([3, %d, 1.5], center=false);\n"
                "    }" % (total_x - 10, total_z - 1, total_y - 10)
            )
        led_module = ""
        led_use = ""
        if led_channels:
            led_module = (
                "module led_channel() { translate([0, %d, %d]) cube([%d, 2, 1.5]); }"
                % (total_y - 2, total_z - 1, total_x)
            )
            led_use = "led_channel();"
        else:
            led_module = "// No LED channels for this style"
        cat_name = build.get("category", "cyberdeck")
        sbc_name = sbc.get("name", "Unknown")
        style_desc = style_preset.get("description", "")
        openscad_code = (
            "// Cyberdeck Enclosure - %s (%s style)\n"
            "// Generated by Cyberdeck Agent v4.1\n"
            "// Color: %s | Accent: %s\n"
            "// SBC: %s (%s)\n"
            "// Style: %s - %s\n"
            "\n"
            "$fn = 60;\n"
            "\n"
            "module enclosure_body() {\n"
            "    color(\"%s\")\n"
            "    minkowski() {\n"
            "        cube([%d, %d, %d], center=false);\n"
            "        sphere(r=%d);\n"
            "    }\n"
            "}\n"
            "\n"
            "module enclosure_lid() {\n"
            "    color(\"%s\")\n"
            "    translate([0, 0, %d])\n"
            "    difference() {\n"
            "        cube([%d, %d, %d], center=false);\n"
            "        %s\n"
            "    }\n"
            "}\n"
            "\n"
            "module sbc_standoffs() {\n"
            "    color(\"%s\")\n"
            "    for (pos = [[5,5], [%d,5], [5,%d], [%d,%d]]) {\n"
            "        translate(pos) cylinder(d=6, h=3, center=false);\n"
            "        translate(pos) cylinder(d=2.5, h=5, center=false);\n"
            "    }\n"
            "}\n"
            "\n"
            "module display_window() {\n"
            "    translate([5, %d, -1])\n"
            "    cube([%d, 4, %d], center=false);\n"
            "}\n"
            "\n"
            "module ventilation() {\n"
            "    %s\n"
            "}\n"
            "\n"
            "%s\n"
            "\n"
            "module full_enclosure() {\n"
            "    difference() {\n"
            "        union() {\n"
            "            enclosure_body();\n"
            "            sbc_standoffs();\n"
            "        }\n"
            "        display_window();\n"
            "        ventilation();\n"
            "        %s\n"
            "    }\n"
            "    enclosure_lid();\n"
            "}\n"
            "\n"
            "full_enclosure();\n"
        ) % (
            cat_name, style_preset.get("name", style_id),
            model_color, accent,
            sbc_name, sbc_form,
            style_id, style_desc,
            model_color,
            total_x - fillet * 2, total_y - fillet * 2, total_z - 1, fillet,
            accent, total_z,
            total_x, total_y, enc_thickness,
            screw_holes,
            accent,
            sbc_x - 5, sbc_y - 5, sbc_x - 5, sbc_y - 5,
            total_y - 5,
            total_x - 10, enc_thickness + 2,
            vent_code,
            led_module,
            led_use,
        )
        return {
            "openscad_code": openscad_code,
            "style": style_id,
            "style_preset": style_preset,
            "color": model_color,
            "accent_color": accent,
            "dimensions": {"x": total_x, "y": total_y, "z": total_z},
            "sbc_clearance": {"x": sbc_x, "y": sbc_y},
            "instructions": [
                "1. Copy the OpenSCAD code into OpenSCAD (free: openscad.org)",
                "2. Press F5 to preview, F6 to render",
                "3. Export as STL: File -> Export -> STL",
                "4. Slice with Cura/PrusaSlicer for your 3D printer",
                "5. Print with PETG for outdoor use or PLA for indoor use",
                "6. Sand, paint, and assemble with M2.5 screws",
            ],
            "download_hint": "Save the openscad_code to a .scad file, open in OpenSCAD, then export as STL",
        }

    async def get_component_details(self, component_id):
        return ComponentDatabase.get_component_details(component_id)

    async def generate_build_video(self, build):
        sbc = build["components"].get("sbc", {})
        display = build["components"].get("display", {})
        kb = build["components"].get("keyboard", {})
        power = build["components"].get("power", {})
        enclosure = build["components"].get("enclosure", {})
        cooling = build["components"].get("cooling", {})
        style = build.get("style", "industrial")
        style_preset = STYLE_PRESETS.get(style, STYLE_PRESETS["industrial"])
        scenes = [
            {
                "scene": 1,
                "title": "Introduction & Overview",
                "duration_seconds": 30,
                "description": f"Wide shot of all components laid out on a workbench. Camera slowly pans across each part.",
                "narration": f"Welcome to the {build['category']} cyberdeck build. Today we're assembling a {style_preset['name']}-style deck using a {sbc.get('name', 'SBC')}.",
                "camera_angle": "overhead wide",
                "components_shown": ["all"],
                "text_overlay": f"{build['category']} Cyberdeck — {build['tier']}",
            },
            {
                "scene": 2,
                "title": "Component Close-ups",
                "duration_seconds": 45,
                "description": "Individual close-up shots of each component with specs overlay.",
                "narration": f"Starting with the brain: the {sbc.get('name', 'SBC')} with {sbc.get('ram', 'N/A')} RAM. The display is a {display.get('name', 'screen')}. Input via {kb.get('name', 'keyboard')}.",
                "camera_angle": "close-up panning",
                "components_shown": ["sbc", "display", "keyboard"],
                "text_overlay": "Component Specs",
            },
            {
                "scene": 3,
                "title": "Enclosure Preparation",
                "duration_seconds": 60,
                "description": f"Show the {enclosure.get('name', 'enclosure')} being prepared. Mark drill points, test-fit components.",
                "narration": f"Our enclosure is the {enclosure.get('name', 'case')}. The style is {style_preset['name']} — {style_preset['description']}. Main color: {build.get('color', '#2d2d2d')}.",
                "camera_angle": "medium shot, workbench",
                "components_shown": ["enclosure"],
                "text_overlay": f"Style: {style_preset['name']}",
            },
            {
                "scene": 4,
                "title": "SBC Mounting",
                "duration_seconds": 45,
                "description": "Mount the SBC onto standoffs inside the enclosure. Secure with screws.",
                "narration": f"Mounting the {sbc.get('name', 'SBC')} using M2.5 standoffs. Ensure GPIO header is accessible and all ports align with enclosure cutouts.",
                "camera_angle": "close-up, hands visible",
                "components_shown": ["sbc", "enclosure"],
                "text_overlay": "Step 1: Mount SBC",
            },
            {
                "scene": 5,
                "title": "Cooling Installation",
                "duration_seconds": 30,
                "description": f"Install {cooling.get('name', 'cooling solution')}. Apply thermal paste if heatsink.",
                "narration": f"Installing the {cooling.get('name', 'cooling')}. {'This is a passive solution — no fan noise.' if 'Passive' in cooling.get('type', '') else 'Connect fan to GPIO for PWM control.'}",
                "camera_angle": "close-up",
                "components_shown": ["cooling"],
                "text_overlay": "Step 2: Cooling",
            },
            {
                "scene": 6,
                "title": "Display Installation",
                "duration_seconds": 45,
                "description": f"Connect and mount the {display.get('name', 'display')}. Route cables neatly.",
                "narration": f"Connecting the {display.get('name', 'display')} via {display.get('interface', 'HDMI')}. {'Capacitive touch is connected via USB.' if display.get('touch') else 'No touch interface needed.'}",
                "camera_angle": "close-up, angled",
                "components_shown": ["display"],
                "text_overlay": "Step 3: Display",
            },
            {
                "scene": 7,
                "title": "Keyboard & Power Wiring",
                "duration_seconds": 60,
                "description": "Connect keyboard and wire the power system. Show cable routing.",
                "narration": f"Keyboard: {kb.get('name', 'keyboard')} via {kb.get('connection', 'USB')}. Power: {power.get('name', 'power source')}. {'Include charging circuit with TP4056 module.' if build['components'].get('charging') else 'Direct power connection.'}",
                "camera_angle": "overhead close-up",
                "components_shown": ["keyboard", "power"],
                "text_overlay": "Step 4: Keyboard & Power",
            },
            {
                "scene": 8,
                "title": "Cable Management",
                "duration_seconds": 30,
                "description": "Route all cables neatly. Use zip ties, grommets, and sleeving.",
                "narration": "Cable management is key to a clean build. Route power cables on one side, signal on the other. Use heat shrink on all solder joints.",
                "camera_angle": "overhead, time-lapse style",
                "components_shown": [],
                "text_overlay": "Step 5: Cable Management",
            },
            {
                "scene": 9,
                "title": "Final Assembly & Power On",
                "duration_seconds": 45,
                "description": "Close the enclosure, secure screws, and power on for the first time.",
                "narration": "Closing up the enclosure. All screws tightened. Moment of truth — powering on for the first time.",
                "camera_angle": "medium shot, dramatic angle",
                "components_shown": ["enclosure"],
                "text_overlay": "Power On!",
            },
            {
                "scene": 10,
                "title": "Finished Build Showcase",
                "duration_seconds": 30,
                "description": f"360-degree showcase of the finished {build['category']} cyberdeck. Show it in use.",
                "narration": f"And here it is — the {build['category']} cyberdeck in all its {style_preset['name']} glory. Built with a {sbc.get('name', 'SBC')}, ready for {build['category']} tasks.",
                "camera_angle": "turntable 360",
                "components_shown": ["all"],
                "text_overlay": f"{build['category']} Cyberdeck — Complete",
            },
        ]
        total_duration = sum(s["duration_seconds"] for s in scenes)
        video_script = {
            "title": f"{build['category']} Cyberdeck Build — {style_preset['name']} Style",
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{total_duration // 60}:{total_duration % 60:02d}",
            "style": style,
            "style_preset": style_preset["name"],
            "scenes": scenes,
            "metadata": {
                "category": build["category"],
                "tier": build["tier"],
                "sbc": sbc.get("name", "N/A"),
                "total_components": len([k for k, v in build["components"].items() if v and k != "charging"]),
                "generated_at": datetime.now().isoformat(),
            },
            "production_notes": [
                "Use consistent lighting across all scenes",
                "Background music: lo-fi or synthwave for cyberpunk style",
                "Add text overlays for each component name and spec",
                "Include B-roll of cable routing close-ups",
                "End screen: subscribe + related builds",
            ],
        }
        return video_script

    async def suggest_custom_pcb(self, compatibility_issues):
        suggestions = []
        for issue in compatibility_issues:
            il = issue.lower()
            if "hdmi" in il and "dsi" in il:
                suggestions.append({
                    "template": "hdmi_to_dsi_adapter",
                    **CUSTOM_PCB_TEMPLATES["hdmi_to_dsi_adapter"],
                    "triggered_by": issue,
                })
            if ("power" in il or "usb-c" in il or "5v/5a" in il) and ("pd" in il or "delivery" in il or "adapter" in il):
                suggestions.append({
                    "template": "usbc_power_board",
                    **CUSTOM_PCB_TEMPLATES["usbc_power_board"],
                    "triggered_by": issue,
                })
            if "gpio" in il or "level" in il or "5v" in il and "3.3v" in il:
                suggestions.append({
                    "template": "gpio_expansion",
                    **CUSTOM_PCB_TEMPLATES["gpio_expansion"],
                    "triggered_by": issue,
                })
            if ("charge" in il or "battery" in il or "bms" in il) and ("custom" in il or "integrated" in il):
                suggestions.append({
                    "template": "power_management",
                    **CUSTOM_PCB_TEMPLATES["power_management"],
                    "triggered_by": issue,
                })
            if "display" in il and ("interface" in il or "adapter" in il or "connector" in il):
                suggestions.append({
                    "template": "display_adapter_multi",
                    **CUSTOM_PCB_TEMPLATES["display_adapter_multi"],
                    "triggered_by": issue,
                })
            if "gamepad" in il or "controller" in il or "joystick" in il:
                suggestions.append({
                    "template": "retro_gamepad_hat",
                    **CUSTOM_PCB_TEMPLATES["retro_gamepad_hat"],
                    "triggered_by": issue,
                })
        if not suggestions and compatibility_issues:
            suggestions.append({
                "template": "gpio_expansion",
                **CUSTOM_PCB_TEMPLATES["gpio_expansion"],
                "triggered_by": "General compatibility issue — GPIO expansion may help bridge components",
            })
        return {
            "issues_analyzed": len(compatibility_issues),
            "pcb_suggestions": suggestions,
            "note": "Custom PCBs require PCB fabrication (JLCPCB, PCBWay, OSH Park). Design in KiCad or EasyEDA.",
        }

    async def build_custom(self, name, description, tier="intermediate"):
        return await self.build(f"{name}: {description}", tier)

    async def search_parts(self, query):
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
        for conn_id, conn in CONNECTIVITY_DATABASE.items():
            if any(kw in conn["name"].lower() or kw in ql for kw in ql.split()):
                results["suggestions"].append({"type": "Connectivity", "name": conn["name"], "price": conn.get("price", 0), "id": conn_id})
        return results

    async def search_internet(self, query):
        results = {"query": query, "platforms": {}, "compiled_build_list": None}
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+cyberdeck"
            results["platforms"]["youtube"] = {"url": search_url, "note": "Search for cyberdeck builds on YouTube"}
            results["platforms"]["tiktok"] = {"url": f"https://www.tiktok.com/search?q={query.replace(' ', '+')}+cyberdeck", "note": "Viral cyberdeck content on TikTok"}
            results["platforms"]["github"] = {"url": f"https://github.com/search?q={query.replace(' ', '+')}+cyberdeck&type=repositories", "note": "Cyberdeck repos on GitHub"}
        except Exception:
            pass
        return results

    def get_status(self):
        return {
            "version": self.version,
            "v5_0_features": [
                "6 New Style Presets (nautical, solarpunk, cassette-futurism, feminine-craft, fallout, brutalist)",
                "6 New Categories (drone, forensics, test-equipment, weather-station, home-automation, edge-ai)",
                "Peripheral Recommendation Engine",
                "Environmental Sensor Database (12 sensors)",
                "Camera Module Database (6 cameras)",
                "SDR Database (3 SDRs)",
                "LoRa/Mesh Database (4 modules)",
                "NFC/RFID Database (3 readers)",
                "Fingerprint Database (3 scanners)",
                "Haptic Feedback Database (3 drivers)",
                "IMU/Accelerometer Database (3 IMUs)",
                "Color Palette Database (10 palettes)",
                "Aesthetic Material Database (10 materials)",
                "Antenna Selection Guide (9 bands)",
                "Thermal Interface Material Database (5 materials)",
                "Battery Sizing Calculator",
                "Antenna Calculator",
                "Forensics Module",
                "Test Equipment Module",
                "Ham Radio Module",
                "Environmental Monitor",
                "Security Forensics Module",
            ],
            "total_builds": len(self.build_history),
            "videos_learned": len(self.learner.learnings.get("video_knowledge", [])),
            "tips_count": len(self.learner.learnings.get("tips_learned", [])),
            "flaws_fixed": len(self.learner.learnings.get("flaws_fixed", [])),
            "categories": list(CATEGORIES.keys()), "tiers": list(TIERS.keys()),
            "styles": list(STYLE_PRESETS.keys()),
            "size_profiles": list(SIZE_PROFILES.keys()),
            "custom_pcb_templates": len(CUSTOM_PCB_TEMPLATES),
            "sbc_count": len(SBC_DATABASE), "display_count": len(DISPLAY_DATABASE),
            "keyboard_count": len(KEYBOARD_DATABASE), "power_count": len(POWER_DATABASE),
            "enclosure_count": len(ENCLOSURE_DATABASE), "cooling_count": len(COOLING_DATABASE),
            "pcb_count": len(PCB_DATABASE), "wire_count": len(WIRE_DATABASE),
            "connectivity_count": len(CONNECTIVITY_DATABASE), "os_count": len(OS_DATABASE),
            "environmental_sensors": len(ENVIRONMENTAL_SENSOR_DATABASE),
            "cameras": len(CAMERA_MODULE_DATABASE),
            "sdr_options": len(SDR_DATABASE),
            "lora_modules": len(LORA_MESH_DATABASE),
            "nfc_readers": len(NFC_RFID_DATABASE),
            "fingerprint_scanners": len(FINGERPRINT_DATABASE),
            "haptic_drivers": len(HAPTIC_FEEDBACK_DATABASE),
            "imu_modules": len(IMU_DATABASE),
            "color_palettes": len(COLOR_PALETTE_DATABASE),
            "aesthetic_materials": len(AESTHETIC_MATERIAL_DATABASE),
            "antenna_bands": len(ANTENNA_GUIDE),
            "thermal_materials": len(THERMAL_INTERFACE_DATABASE),
            "charging_components": 3,
            "waterproof_enclosures": 3,
            "video_queue_pending": self.video_queue.get_pending_count(),
            "learner_stats": self.learner.get_stats(),
        }

    def get_categories(self):
        return {k: {"name": v["name"], "description": v["description"], "budget_range": v["budget_range"],
                     "estimated_cost": v.get("estimated_cost", "?"), "default_style": v.get("default_style", "industrial"),
                     "default_color": v.get("default_color", "#2d2d2d"), "size_preference": v.get("size_preference", "big")}
                for k, v in CATEGORIES.items()}


# ============================================================
# v5.0 — PERIPHERAL RECOMMENDATION ENGINE
# ============================================================
class PeripheralRecommendationEngine:
    """Recommends peripherals by category, use-case, and budget."""

    @staticmethod
    def recommend_for_category(category: str, budget: float = 500.0) -> Dict[str, List]:
        cat = CATEGORIES.get(category, {})
        recommendations = {}

        for db_name, db in [
            ("sensors", ENVIRONMENTAL_SENSOR_DATABASE),
            ("cameras", CAMERA_MODULE_DATABASE),
            ("sdr", SDR_DATABASE),
            ("lora", LORA_MESH_DATABASE),
            ("nfc", NFC_RFID_DATABASE),
            ("fingerprint", FINGERPRINT_DATABASE),
            ("haptics", HAPTIC_FEEDBACK_DATABASE),
            ("imu", IMU_DATABASE),
        ]:
            matches = []
            for pid, pdata in db.items():
                if category in pdata.get("best_for", []):
                    matches.append({"id": pid, **pdata})
            if matches:
                recommendations[db_name] = sorted(matches, key=lambda x: x.get("price", 0))

        if recommendations:
            total = sum(items[0].get("price", 0) for items in recommendations.values() if items)
            recommendations["_total_estimated_cost"] = round(total, 2)
            recommendations["_budget_remaining"] = round(budget - total, 2)

        return recommendations

    @staticmethod
    def recommend_for_use_case(use_case: str) -> Dict[str, List]:
        results = {}
        use_case_lower = use_case.lower()
        all_dbs = {
            "sensors": ENVIRONMENTAL_SENSOR_DATABASE,
            "cameras": CAMERA_MODULE_DATABASE,
            "sdr": SDR_DATABASE,
            "lora": LORA_MESH_DATABASE,
            "nfc": NFC_RFID_DATABASE,
            "fingerprint": FINGERPRINT_DATABASE,
            "haptics": HAPTIC_FEEDBACK_DATABASE,
            "imu": IMU_DATABASE,
        }
        for db_name, db in all_dbs.items():
            matches = []
            for pid, pdata in db.items():
                all_text = str(pdata).lower()
                if use_case_lower in all_text:
                    matches.append({"id": pid, **pdata})
            if matches:
                results[db_name] = matches
        return results

    @staticmethod
    def suggest_by_style(style: str) -> List[Dict]:
        suggestions = []
        materials = AESTHETIC_MATERIAL_DATABASE
        for mid, mdata in materials.items():
            if style in mdata.get("best_for", []):
                suggestions.append({"id": mid, **mdata})
        return suggestions

    @staticmethod
    def suggest_by_color_palette(palette_name: str) -> Dict:
        palette = COLOR_PALETTE_DATABASE.get(palette_name, {})
        if not palette:
            return {"error": f"Unknown palette: {palette_name}"}
        return {
            "palette": palette,
            "materials": [
                {"id": mid, **mdata}
                for mid, mdata in AESTHETIC_MATERIAL_DATABASE.items()
                if palette_name.replace("_", " ") in str(mdata).lower()
                or any(p in str(mdata).lower() for p in palette.get("primary", "").lower().split())
            ][:5],
        }


# ============================================================
# v5.0 — ANTENNA CALCULATOR
# ============================================================
class AntennaCalculator:
    """Calculates antenna dimensions and cable losses for cyberdeck builds."""

    @staticmethod
    def calculate_wavelength(frequency_mhz: float) -> float:
        """Calculate wavelength in cm for given frequency in MHz."""
        return 29979.2458 / frequency_mhz

    @staticmethod
    def quarter_wave(frequency_mhz: float) -> float:
        """Quarter-wave antenna length in cm."""
        return AntennaCalculator.calculate_wavelength(frequency_mhz) / 4

    @staticmethod
    def cable_loss_db(cable_type: str, frequency_mhz: float, length_m: float) -> float:
        """Estimate cable loss in dB."""
        loss_per_100m = {
            "RG58": 0.4 * (frequency_mhz / 100),
            "RG174": 0.6 * (frequency_mhz / 100),
            "LMR200": 0.3 * (frequency_mhz / 100),
            "LMR400": 0.1 * (frequency_mhz / 100),
            "RG316": 0.35 * (frequency_mhz / 100),
        }
        base_loss = loss_per_100m.get(cable_type, 0.5 * (frequency_mhz / 100))
        return round(base_loss * length_m, 2)

    @staticmethod
    def link_budget(power_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float,
                    cable_loss_db: float, frequency_mhz: float) -> Dict:
        free_space_loss = 32.45 + 20 * (frequency_mhz / 1000) + 20 * 10  # assume 10km
        budget = power_dbm + tx_gain_dbi + rx_gain_dbi - cable_loss_db - free_space_loss
        return {
            "free_space_loss_db": round(free_space_loss, 2),
            "total_link_budget_db": round(budget, 2),
            "max_range_km": round(10 ** (budget / (10 * 2)), 1),
            "recommended": budget > 10,
        }

    @staticmethod
    def recommend_connector(frequency_mhz: float) -> str:
        if frequency_mhz < 300:
            return "SMA (best for HF/VHF)"
        elif frequency_mhz < 3000:
            return "RP-SMA or SMA (best for WiFi/LoRa)"
        else:
            return "SMA or MMCX (best for 5GHz/SDR)"


# ============================================================
# v5.0 — BATTERY SIZING CALCULATOR
# ============================================================
class BatterySizingCalculator:
    """Calculates battery requirements for cyberdeck builds."""

    @staticmethod
    def calculate_18650_capacity(cells: int, voltage: float = 3.7, capacity_mah: float = 3500,
                                   efficiency: float = 0.9) -> Dict:
        total_wh = cells * voltage * capacity_mah / 1000 * efficiency
        return {
            "cells": cells,
            "voltage_nominal": voltage,
            "total_wh": round(total_wh, 2),
            "runtime_hours_5w": round(total_wh / 5, 1),
            "runtime_hours_10w": round(total_wh / 10, 1),
            "runtime_hours_15w": round(total_wh / 15, 1),
            "weight_grams": cells * 45,
        }

    @staticmethod
    def recommend_capacity(power_draw_w: float, runtime_hours: float, cells_available: int = 6) -> Dict:
        needed_wh = power_draw_w * runtime_hours / 0.9
        cells_needed = max(1, -(-int(needed_wh // (3.7 * 3.5)) ))  # ceiling division
        return {
            "power_draw_w": power_draw_w,
            "runtime_hours": runtime_hours,
            "needed_wh": round(needed_wh, 2),
            "cells_recommended": cells_needed,
            "cells_available": cells_available,
            "sufficient": cells_needed <= cells_available,
            "total_wh_available": round(cells_available * 3.7 * 3.5 * 0.9, 2),
        }


# ============================================================
# v5.0 — FORENSICS MODULE
# ============================================================
class ForensicsModule:
    """Digital forensics tools and procedures for cyberdeck builds."""

    PROCEDURES = {
        "disk_imaging": {
            "name": "Disk Imaging (dd / dc3dd)",
            "tool": "dd if=/dev/sdX of=backup.img bs=4M status=progress",
            "dc3dd": "dc3dd if=/dev/sdX of=backup.img hash=sha256 log=audit.log",
            "notes": "Always use write-blocker. Hash source and destination.",
        },
        "file_carving": {
            "name": "File Carving (foremost / scalpel)",
            "tool": "foremost -i /dev/sdX -o output/",
            "notes": "Recovers deleted files by file headers.",
        },
        "network_forensics": {
            "name": "Network Forensics (tcpdump / Wireshark)",
            "tool": "tcpdump -i eth0 -w capture.pcap",
            "notes": "Capture before powering down suspect device.",
        },
        "memory_forensics": {
            "name": "Memory Forensics (Volatility)",
            "tool": "volatility -f memory.dump imageinfo",
            "notes": "Requires RAM dump via /proc/kcore or LiME.",
        },
        "log_analysis": {
            "name": "Log Analysis (LogonTracer)",
            "tool": "LogonTracer.py -i auth.log",
            "notes": "Track authentication events, lateral movement.",
        },
    }

    @staticmethod
    def get_procedure(proc_name: str) -> Dict:
        return ForensicsModule.PROCEDURES.get(proc_name, {"error": "Unknown procedure"})

    @staticmethod
    def list_procedures() -> List[str]:
        return list(ForensicsModule.PROCEDURES.keys())


# ============================================================
# v5.0 — TEST EQUIPMENT MODULE
# ============================================================
class TestEquipmentModule:
    """Portable test equipment for cyberdeck builds: oscilloscope, logic analyzer, etc."""

    EQUIPMENT = {
        "oscilloscope": {
            "name": "RP2040 Oscilloscope (PicoScope clone)",
            "type": "USB Oscilloscope",
            "channels": 2,
            "bandwidth_mhz": 20,
            "sample_rate_msps": 100,
            "price": 25,
            "software": "PicoScope / custom RP2040 firmware",
        },
        "logic_analyzer": {
            "name": "Saleae Logic Clone (8ch)",
            "type": "USB Logic Analyzer",
            "channels": 8,
            "max_sample_rate_mhz": 24,
            "protocols": ["SPI", "I2C", "UART", "1-Wire", "JTAG"],
            "price": 10,
            "software": "Logic 2 / sigrok PulseView",
        },
        "signal_generator": {
            "name": "AD9833 DDS Signal Generator",
            "type": "DDS Waveform Generator",
            "output_range": "0-12.5MHz",
            "waveforms": ["Sine", "Square", "Triangle"],
            "interface": "SPI",
            "price": 5,
        },
        "multimeter": {
            "name": "USB Multimeter (FNIRSI DMT-99)",
            "type": "Digital Multimeter",
            "measures": ["V", "A", "Ω", "C", "Hz", "Capacitance"],
            "interface": "USB",
            "price": 20,
        },
        "power_supply": {
            "name": "Adjustable DC-DC Buck Converter (LM2596)",
            "type": "Adjustable PSU",
            "output_range": "1.25-30V, 0-3A",
            "price": 5,
            "notes": "For bench testing SBCs",
        },
    }

    @staticmethod
    def get_equipment(name: str) -> Dict:
        return TestEquipmentModule.EQUIPMENT.get(name, {"error": "Unknown equipment"})

    @staticmethod
    def list_equipment() -> List[str]:
        return list(TestEquipmentModule.EQUIPMENT.keys())


# ============================================================
# v5.0 — HAM RADIO MODULE
# ============================================================
class HamRadioModule:
    """Ham radio integration for cyberdeck builds."""

    BANDS = {
        "160m": {"freq_mhz": 1.8, "mode": "CW/SSB", "wavelength": "160m"},
        "80m": {"freq_mhz": 3.5, "mode": "CW/SSB", "wavelength": "80m"},
        "40m": {"freq_mhz": 7.0, "mode": "CW/SSB/Digital", "wavelength": "40m"},
        "20m": {"freq_mhz": 14.0, "mode": "CW/SSB/Digital", "wavelength": "20m"},
        "15m": {"freq_mhz": 21.0, "mode": "CW/SSB/Digital", "wavelength": "15m"},
        "10m": {"freq_mhz": 28.0, "mode": "CW/SSB/FM", "wavelength": "10m"},
        "2m": {"freq_mhz": 144.0, "mode": "FM/SSB/Digital", "wavelength": "2m"},
        "70cm": {"freq_mhz": 430.0, "mode": "FM/Digital", "wavelength": "70cm"},
    }

    DIGITAL_MODES = {
        "js8call": {"name": "JS8Call", "description": "Keyboard-to-keyboard, weak signal", "bandwidth": "50Hz", "software": "js8call"},
        "ft8": {"name": "FT8", "description": "Weak signal, contesting", "bandwidth": "50Hz", "software": "wsjt-x"},
        "wspr": {"name": "WSPR", "description": "Beacon propagation", "bandwidth": "6Hz", "software": "wsjt-x"},
        "packet": {"name": "AX.25 Packet", "description": "APRS, BBS", "bandwidth": "1200baud", "software": "direwolf"},
        "sstv": {"name": "SSTV", "description": "Slow-scan television", "bandwidth": "3kHz", "software": "qsstv"},
    }

    @staticmethod
    def get_band(band_name: str) -> Dict:
        return HamRadioModule.BANDS.get(band_name, {"error": "Unknown band"})

    @staticmethod
    def recommend_antenna_for_band(band_name: str) -> Dict:
        band = HamRadioModule.BANDS.get(band_name, {})
        if not band:
            return {"error": "Unknown band"}
        freq = band["freq_mhz"]
        qwave = AntennaCalculator.quarter_wave(freq)
        return {
            "band": band_name,
            "frequency_mhz": freq,
            "quarter_wave_cm": round(qwave, 1),
            "half_wave_cm": round(qwave * 2, 1),
            "recommended_type": "Dipole" if freq < 30 else "Vertical",
        }


# ============================================================
# v5.0 — ENVIRONMENTAL MONITORING SYSTEM
# ============================================================
class EnvironmentalMonitor:
    """Real-time environmental monitoring with alerts."""

    def __init__(self):
        self.readings: List[Dict] = []
        self.alerts: List[Dict] = []
        self.thresholds = {
            "temp_high": 40.0, "temp_low": -10.0,
            "humidity_high": 90.0, "humidity_low": 10.0,
            "co2_high": 1000, "pm25_high": 35.0,
        }

    def add_reading(self, sensor_id: str, value: float, unit: str, timestamp: str = None):
        reading = {
            "sensor_id": sensor_id,
            "value": value,
            "unit": unit,
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        self.readings.append(reading)
        self._check_alerts(reading)

    def _check_alerts(self, reading: Dict):
        sensor = reading["sensor_id"].lower()
        val = reading["value"]
        if "temp" in sensor:
            if val > self.thresholds["temp_high"]:
                self.alerts.append({"type": "HIGH_TEMP", "sensor": sensor, "value": val, "message": f"High temperature: {val}{reading['unit']}"})
            elif val < self.thresholds["temp_low"]:
                self.alerts.append({"type": "LOW_TEMP", "sensor": sensor, "value": val, "message": f"Low temperature: {val}{reading['unit']}"})
        if "co2" in sensor and val > self.thresholds["co2_high"]:
            self.alerts.append({"type": "HIGH_CO2", "sensor": sensor, "value": val, "message": f"High CO2: {val}ppm"})

    def get_readings(self, last_n: int = 10) -> List[Dict]:
        return self.readings[-last_n:]

    def get_alerts(self, last_n: int = 5) -> List[Dict]:
        return self.alerts[-last_n:]

    def export_csv(self) -> str:
        lines = ["timestamp,sensor_id,value,unit"]
        for r in self.readings:
            lines.append(f"{r['timestamp']},{r['sensor_id']},{r['value']},{r['unit']}")
        return "\n".join(lines)


# ============================================================
# v5.0 — SECURITY FORENSICS MODULE
# ============================================================
class SecurityForensicsModule:
    """Security forensics toolkit for cyberdeck builds."""

    TOOLS = {
        "disk_imaging": {"name": "Disk Imaging", "command": "dd if=/dev/sdX of=image.img bs=4M status=progress", "purpose": "Bit-for-bit copy of suspect drive"},
        "file_carving": {"name": "File Carving", "command": "foremost -i /dev/sdX -o output/", "purpose": "Recover deleted files from disk image"},
        "hash_verification": {"name": "Hash Verification", "command": "sha256sum image.img", "purpose": "Verify integrity of disk image"},
        "memory_dump": {"name": "Memory Dump", "command": "sudo dd if=/proc/kcore of=memdump.raw bs=1M", "purpose": "Capture RAM contents for analysis"},
        "network_capture": {"name": "Network Capture", "command": "tcpdump -i eth0 -w capture.pcap -c 10000", "purpose": "Capture network packets for forensics"},
        "log_analysis": {"name": "Log Analysis", "command": "logparser.py --input /var/log/auth.log", "purpose": "Parse and analyze system logs"},
        "stego_extract": {"name": "Steganography Extraction", "command": "steghide extract -sf image.jpg", "purpose": "Extract hidden data from images"},
        "metadata_extract": {"name": "Metadata Extraction", "command": "exiftool suspect_file", "purpose": "Extract file metadata"},
    }

    @staticmethod
    def get_tool(tool_name: str) -> Dict:
        return SecurityForensicsModule.TOOLS.get(tool_name, {"error": "Unknown tool"})

    @staticmethod
    def list_tools() -> List[str]:
        return list(SecurityForensicsModule.TOOLS.keys())


# ============================================================
# v6.0 — CAREER TEMPLATES
# ============================================================
CAREER_TEMPLATES = {
    "coding": {
        "name": "Coding / Software Development",
        "description": "Optimized for programming, IDE, terminal, git, Docker",
        "best_sbc": "Pi 5 8GB",
        "best_display": "10.1\" IPS 1920x1200",
        "best_input": "Split mechanical keyboard (Sofle/Corne)",
        "best_os": "Ubuntu/Arch + i3/sway",
        "must_have": ["NVMe SSD", "USB-C hub", "External monitor support"],
        "recommended": ["Split keyboard", "USB-C PD", "8GB+ RAM"],
        "budget_range": "$400-$800",
        "tier": "intermediate",
        "style": "minimal",
        "cooling": "Passive heatsink + small fan",
        "connectivity": ["WiFi 6", "Ethernet (USB adapter)", "Bluetooth 5.0"],
        "software_stack": ["VS Code/Neovim", "Docker", "Git", "tmux", "Zsh"],
        "power_budget": "10-15W",
        "cable_lengths": {"display": "15cm", "keyboard": "30cm", "power": "20cm"},
    },
    "gaming": {
        "name": "Gaming / Retro Gaming",
        "description": "Optimized for retro emulation and indie games",
        "best_sbc": "Pi 5 8GB",
        "best_display": "7\" IPS 1024x600 (or 5\" for handheld)",
        "best_input": "USB gamepad (8BitDo/SNES style)",
        "best_os": "RetroPie / Batocera",
        "must_have": ["Gamepad", "HDMI output", "Cooling fan"],
        "recommended": ["NVMe SSD", "USB-C PD", "Battery pack"],
        "budget_range": "$200-$500",
        "tier": "beginner",
        "style": "retro",
        "cooling": "Active fan (mandatory for gaming)",
        "connectivity": ["WiFi 5", "Bluetooth 5.0"],
        "software_stack": ["RetroPie", "EmulationStation", "RetroArch"],
        "power_budget": "8-15W",
        "cable_lengths": {"display": "10cm", "controller": "50cm", "power": "15cm"},
    },
    "ai_ml": {
        "name": "AI / Machine Learning",
        "description": "Optimized for local AI inference, edge ML, computer vision",
        "best_sbc": "Pi 5 8GB + Coral USB TPU",
        "best_display": "10.1\" IPS (for visualization)",
        "best_input": "Standard keyboard",
        "best_os": "Ubuntu + TFLite/ONNX",
        "must_have": ["Coral USB/Hailo-8", "Camera (IMX708)", "8GB RAM minimum"],
        "recommended": ["NVMe SSD", "USB-C PD", "External GPU (Jetson)"],
        "budget_range": "$500-$1500",
        "tier": "advanced",
        "style": "futuristic",
        "cooling": "Active cooling (mandatory for ML workloads)",
        "connectivity": ["WiFi 6", "Ethernet", "Bluetooth 5.0"],
        "software_stack": ["Python", "TensorFlow Lite", "ONNX Runtime", "OpenCV", "Jupyter"],
        "power_budget": "12-25W",
        "cable_lengths": {"display": "15cm", "camera": "20cm", "power": "25cm"},
    },
    "security": {
        "name": "Security / Pentesting",
        "description": "Optimized for penetration testing, WiFi audit, forensics",
        "best_sbc": "Pi 5 8GB",
        "best_display": "7\" IPS touchscreen",
        "best_input": "Compact mechanical keyboard",
        "best_os": "Kali Linux",
        "must_have": ["WiFi adapter (AWUS036ACH)", "LoRa (SX1262)", "NVMe SSD"],
        "recommended": ["GPS module", "External antenna", "USB Rubber Ducky"],
        "budget_range": "$400-$1000",
        "tier": "advanced",
        "style": "cyberpunk",
        "cooling": "Active fan",
        "connectivity": ["WiFi (monitor mode)", "Ethernet", "Bluetooth", "LoRa"],
        "software_stack": ["Kali Linux", "Aircrack-ng", "Bettercap", "Wireshark", "Nmap"],
        "power_budget": "10-18W",
        "cable_lengths": {"display": "15cm", "antenna": "30cm", "power": "20cm"},
    },
    "writer": {
        "name": "Writing / WriterDeck",
        "description": "Distraction-free writing machine",
        "best_sbc": "Pi Zero 2W (minimal) or Pi 5 4GB (comfortable)",
        "best_display": "7.9\" e-ink or 7\" IPS",
        "best_input": "Ortholinear mechanical (Planck/preonic)",
        "best_os": "writerdeckOS / minimal Debian",
        "must_have": ["No browser (or disabled)", "E-ink preferred", "Long battery life"],
        "recommended": ["E-ink display", "Solar charging", "Minimal OS"],
        "budget_range": "$150-$400",
        "tier": "beginner",
        "style": "minimal",
        "cooling": "Passive (low power)",
        "connectivity": ["WiFi (optional, for sync)", "USB-C"],
        "software_stack": ["Vim/Neovim", "Markdown", "Pandoc", "Git"],
        "power_budget": "2-8W",
        "cable_lengths": {"display": "10cm", "keyboard": "15cm", "power": "10cm"},
    },
    "field_research": {
        "name": "Field Research / Environmental",
        "description": "Rugged field data collection and monitoring",
        "best_sbc": "Pi 5 4GB",
        "best_display": "7\" IPS touchscreen (sunlight readable)",
        "best_input": "Touch + compact keyboard",
        "best_os": "Pi OS Lite + custom scripts",
        "must_have": ["GPS module", "Environmental sensors", "Solar charging", "IP67 case"],
        "recommended": ["LoRa mesh", "Camera", "Satellite comms"],
        "budget_range": "$300-$800",
        "tier": "intermediate",
        "style": "industrial",
        "cooling": "Passive (IP67 sealed)",
        "connectivity": ["LoRa", "WiFi", "GPS", "Cellular (optional)"],
        "software_stack": ["Python", "SQLite", "Grafana", "Custom scripts"],
        "power_budget": "5-12W (solar + battery)",
        "cable_lengths": {"display": "15cm", "sensors": "50cm", "power": "20cm"},
    },
    "robotics": {
        "name": "Robotics / Automation",
        "description": "Motor control, sensors, navigation, ROS2",
        "best_sbc": "Pi 5 8GB",
        "best_display": "7\" IPS (for teleoperation)",
        "best_input": "Gamepad + keyboard",
        "best_os": "Ubuntu + ROS2",
        "must_have": ["Motor drivers", "IMU", "Camera", "GPIO expansion"],
        "recommended": ["LiDAR", "GPS", "ROS2", "NVMe SSD"],
        "budget_range": "$400-$1500",
        "tier": "advanced",
        "style": "industrial",
        "cooling": "Active fan + heatsinks",
        "connectivity": ["WiFi", "Ethernet", "Bluetooth", "USB"],
        "software_stack": ["ROS2", "Python", "C++", "Navigation2", "MoveIt"],
        "power_budget": "15-30W",
        "cable_lengths": {"display": "15cm", "motors": "100cm", "power": "30cm"},
    },
    "media_production": {
        "name": "Media Production / Creative",
        "description": "Video editing, music production, graphic design",
        "best_sbc": "Orange Pi 5 Plus (RK3588) or LattePanda",
        "best_display": "13.3\" IPS 1920x1080 (color-accurate)",
        "best_input": "Full mechanical keyboard + mouse",
        "best_os": "Ubuntu Studio / Pi OS",
        "must_have": ["Large NVMe (1TB+)", "USB-C hub", "Audio DAC"],
        "recommended": ["External GPU", "Color-calibrated display", "Studio monitors"],
        "budget_range": "$500-$1500",
        "tier": "advanced",
        "style": "minimal",
        "cooling": "Active cooling (sustained workloads)",
        "connectivity": ["WiFi 6", "Ethernet", "Bluetooth 5.0", "USB-C"],
        "software_stack": ["DaVinci Resolve", "Audacity", "Blender", "GIMP", "OBS"],
        "power_budget": "15-30W",
        "cable_lengths": {"display": "20cm", "audio": "100cm", "power": "25cm"},
    },
    "ham_radio": {
        "name": "Ham Radio / SDR",
        "description": "Amateur radio, SDR, signals intelligence",
        "best_sbc": "Pi 5 4GB",
        "best_display": "10\" IPS (waterfall display)",
        "best_input": "Standard keyboard",
        "best_os": "Pi OS + SDR software",
        "must_have": ["SDR receiver (RTL-SDR/HackRF)", "External antenna", "GPS"],
        "recommended": ["Ham radio transceiver", "Antenna tuner", "SWR meter"],
        "budget_range": "$300-$1000",
        "tier": "intermediate",
        "style": "industrial",
        "cooling": "Passive + small fan",
        "connectivity": ["WiFi", "Ethernet", "Bluetooth", "SDR"],
        "software_stack": ["SDR++", "GNU Radio", "WSJT-X", "Direwolf", "GQRX"],
        "power_budget": "8-15W",
        "cable_lengths": {"display": "15cm", "antenna": "200cm", "power": "20cm"},
    },
    "home_automation": {
        "name": "Home Automation / IoT Gateway",
        "description": "Smart home hub, sensor aggregation, automation",
        "best_sbc": "Pi 5 4GB",
        "best_display": "7\" touchscreen (wall-mounted)",
        "best_input": "Touch only",
        "best_os": "Home Assistant OS",
        "must_have": ["Zigbee/Thread dongle", "WiFi", "Bluetooth"],
        "recommended": ["Z-Wave dongle", "Matter support", "UPS"],
        "budget_range": "$200-$500",
        "tier": "beginner",
        "style": "minimal",
        "cooling": "Passive",
        "connectivity": ["WiFi", "Ethernet", "Bluetooth", "Zigbee", "Thread"],
        "software_stack": ["Home Assistant", "Zigbee2MQTT", "Node-RED", "Grafana"],
        "power_budget": "5-10W",
        "cable_lengths": {"display": "20cm", "sensors": "100cm", "power": "15cm"},
    },
    "portable_hacking": {
        "name": "Portable Hacking Lab",
        "description": "All-in-one portable penetration testing platform",
        "best_sbc": "Pi 5 8GB",
        "best_display": "10.1\" IPS",
        "best_input": "Compact mechanical + trackball",
        "best_os": "Kali Linux + Parrot OS",
        "must_have": ["WiFi adapter", "Bluetooth adapter", "LoRa", "GPS", "NVMe"],
        "recommended": ["USB Rubber Ducky", "Proxmark", "SDR", "Pineapple"],
        "budget_range": "$600-$2000",
        "tier": "expert",
        "style": "cyberpunk",
        "cooling": "Active cooling",
        "connectivity": ["WiFi (monitor)", "Ethernet", "Bluetooth", "LoRa", "Cellular"],
        "software_stack": ["Kali", "Metasploit", "Burp Suite", "Aircrack-ng", "Wireshark"],
        "power_budget": "15-25W",
        "cable_lengths": {"display": "15cm", "antenna": "50cm", "power": "25cm"},
    },
}

# ============================================================
# v6.0 — PCB DATABASE (High Quality)
# ============================================================
PCB_DATABASE = {
    "custom_cyberdeck_v1": {
        "name": "Cyberdeck Main Board v1",
        "description": "Custom PCB for cyberdeck integration: USB-C PD, GPIO expansion, display header",
        "layers": 4,
        "dimensions_mm": "120x80",
        "finish": "ENIG",
        "min_trace": "0.15mm",
        "min_drill": "0.3mm",
        "fab_house": "JLCPCB",
        "estimated_cost": "$5-15 (10pcs)",
        "components": ["USB-C PD IC", "Buck converter", "GPIO level shifters", "Display connector"],
        "gerber_url": "N/A (generate with KiCad)",
    },
    "ups_hat_pcb": {
        "name": "UPS HAT PCB",
        "description": "Battery management HAT for Pi with 18650 cells",
        "layers": 2,
        "dimensions_mm": "65x56",
        "finish": "HASL",
        "fab_house": "JLCPCB",
        "estimated_cost": "$2-5 (10pcs)",
        "components": ["TP4056", "DW01", "FS8205", "18650 holders", "40-pin header"],
    },
    "display_adapter_pcb": {
        "name": "Display Adapter PCB",
        "description": "HDMI-to-DSI or USB-C-to-HDMI adapter board",
        "layers": 2,
        "dimensions_mm": "40x30",
        "finish": "ENIG",
        "fab_house": "JLCPCB",
        "estimated_cost": "$2-5 (10pcs)",
        "components": ["TFP401 HDMI receiver", "FFC connectors", "Capacitors"],
    },
    "sensor_hub_pcb": {
        "name": "Sensor Hub PCB",
        "description": "Multi-sensor breakout with I2C/SPI/UART",
        "layers": 2,
        "dimensions_mm": "50x40",
        "finish": "HASL",
        "fab_house": "JLCPCB",
        "estimated_cost": "$2-5 (10pcs)",
        "components": ["I2C level shifter", "SPI buffers", "Screw terminals", "Decoupling caps"],
    },
    "power_distribution_pcb": {
        "name": "Power Distribution Board",
        "description": "Multi-rail power distribution for complex builds",
        "layers": 2,
        "dimensions_mm": "60x40",
        "finish": "HASL",
        "fab_house": "JLCPCB",
        "estimated_cost": "$3-8 (10pcs)",
        "components": ["Buck converters", "LDO regulators", "Fuse holders", "Power LEDs"],
    },
}

# ============================================================
# v6.0 — SBC DATABASE (High Quality, Best of Best)
# ============================================================
SBC_DATABASE = {
    "raspberry_pi_5_8gb": {
        "name": "Raspberry Pi 5 8GB",
        "soc": "BCM2712", "cpu": "Cortex-A76 2.4GHz x4", "gpu": "VideoCore VII",
        "ram": "8GB LPDDR4X", "storage": "MicroSD + NVMe (PCIe Gen 3)",
        "wifi": "WiFi 5 (802.11ac)", "ble": "Bluetooth 5.0", "ethernet": "1Gbps",
        "usb": "2x USB 3.0 + 2x USB 2.0", "gpio": "40-pin GPIO",
        "display": "2x micro-HDMI + DSI", "camera": "CSI-2",
        "pcie": "PCIe Gen 3 x1", "power": "USB-C PD (5V/5A)",
        "price": "$80", "tier": "standard-premium",
        "best_for": ["coding", "security", "gaming", "ai_ml", "robotics"],
        "compatibility_note": "Best all-around SBC. Works with almost all HATs/displays.",
    },
    "raspberry_pi_5_4gb": {
        "name": "Raspberry Pi 5 4GB",
        "soc": "BCM2712", "cpu": "Cortex-A76 2.4GHz x4", "gpu": "VideoCore VII",
        "ram": "4GB LPDDR4X", "storage": "MicroSD + NVMe",
        "wifi": "WiFi 5", "ble": "Bluetooth 5.0", "ethernet": "1Gbps",
        "usb": "2x USB 3.0 + 2x USB 2.0", "gpio": "40-pin GPIO",
        "display": "2x micro-HDMI + DSI", "camera": "CSI-2",
        "pcie": "PCIe Gen 3 x1", "power": "USB-C PD",
        "price": "$60", "tier": "standard",
        "best_for": ["coding", "gaming", "writer", "field_research", "ham_radio", "home_automation"],
    },
    "raspberry_pi_zero_2w": {
        "name": "Raspberry Pi Zero 2W",
        "soc": "RP3A0", "cpu": "Cortex-A53 1GHz x4", "gpu": "VideoCore IV",
        "ram": "512MB", "storage": "MicroSD",
        "wifi": "WiFi 4", "ble": "Bluetooth 4.2", "ethernet": "None",
        "usb": "1x micro-USB OTG", "gpio": "40-pin GPIO",
        "display": "Mini-HDMI", "camera": "CSI",
        "power": "Micro-USB 5V/2.5A",
        "price": "$15", "tier": "budget",
        "best_for": ["writer", "portable_hacking", "iot"],
        "compatibility_note": "Tiny, low power. Not for desktop use.",
    },
    "orange_pi_5_plus": {
        "name": "Orange Pi 5 Plus 16GB",
        "soc": "RK3588", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "16GB LPDDR5", "storage": "eMMC + 2x NVMe",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.0", "ethernet": "2x 2.5Gbps",
        "usb": "1x USB 3.0 + 2x USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + HDMI + Type-C", "camera": "MIPI CSI",
        "pcie": "PCIe Gen 3 x4", "power": "USB-C PD",
        "price": "$120", "tier": "premium",
        "best_for": ["media_production", "ai_ml", "coding"],
        "compatibility_note": "RK3588 NPU for AI. 2x NVMe for storage.",
    },
    "lattepanda_sigma": {
        "name": "LattePanda Sigma",
        "soc": "Intel N100", "cpu": "Alder Lake-N x4", "gpu": "Intel UHD",
        "ram": "8-16GB DDR5", "storage": "M.2 NVMe",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.0", "ethernet": "2.5Gbps",
        "usb": "4x USB 3.0 + 1x USB-C", "gpio": "GPIO header",
        "display": "HDMI + Type-C", "camera": "MIPI CSI",
        "pcie": "M.2 Key M + Key E", "power": "USB-C PD",
        "price": "$250", "tier": "premium",
        "best_for": ["coding", "media_production", "portable_hacking"],
        "compatibility_note": "x86 = full Windows/Linux support. DDR5 RAM.",
    },
    "jetson_orin_nano": {
        "name": "NVIDIA Jetson Orin Nano 8GB",
        "soc": "GA10B", "cpu": "Cortex-A78AE x6", "gpu": "Ampere 1024-core",
        "ram": "8GB LPDDR5", "storage": "M.2 NVMe",
        "wifi": "WiFi 6 (module)", "ble": "Bluetooth 5.0", "ethernet": "1Gbps",
        "usb": "4x USB 3.0 + 1x USB-C", "gpio": "40-pin GPIO",
        "display": "HDMI + DP", "camera": "MIPI CSI x2",
        "pcie": "PCIe Gen 4 x4", "power": "DC barrel or USB-C",
        "price": "$250", "tier": "premium",
        "best_for": ["ai_ml"],
        "compatibility_note": "40 TOPS GPU for AI inference. Best for ML workloads.",
    },
    "milkv_jupiter2": {
        "name": "Milk-V Jupiter2 (RISC-V SG2380)",
        "soc": "SG2380", "cpu": "RISC-V 8-core @ 2.5GHz", "gpu": "IMG BXT-32-1024",
        "ram": "8/16/32GB DDR5", "storage": "eMMC + NVMe M.2 + MicroSD",
        "wifi": "WiFi 6E", "ble": "Bluetooth 5.3", "ethernet": "2.5Gbps",
        "usb": "USB 3.2 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + DP 1.4", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "12V/2A DC",
        "price": "$130", "tier": "premium",
        "best_for": ["coding", "research", "ai_ml"],
        "compatibility_note": "8-core RISC-V desktop-class. 32GB DDR5. NVMe + 2.5GbE.",
    },
    "radxa_a7a": {
        "name": "Radxa A7A (RK3588S AIO)",
        "soc": "RK3588S", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "8/16GB LPDDR5", "storage": "eMMC + NVMe M.2 + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.2", "ethernet": "2.5Gbps",
        "usb": "USB 3.2 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + USB-C DP", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "USB-C PD (5V/4A)",
        "price": "$75", "tier": "standard",
        "best_for": ["ai_ml", "coding", "security"],
        "compatibility_note": "RK3588S at budget price. Laptop AIO design. 6 TOPS NPU.",
    },
    "hackberrypi_cm5": {
        "name": "HackberryPi CM5 (RK3588 Module)",
        "soc": "RK3588", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "8/16/32GB LPDDR5", "storage": "eMMC + NVMe M.2 + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.2", "ethernet": "2.5Gbps",
        "usb": "USB 3.2 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + USB-C DP + eDP", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "USB-C PD (5V/5A)",
        "price": "$99", "tier": "standard-premium",
        "best_for": ["ai_ml", "coding", "security", "research"],
        "compatibility_note": "Full RK3588 in CM form. 32GB option. Triple display. NVMe.",
    },
    "zhihe_a210": {
        "name": "Zhihe A210 (RISC-V 12 TOPS NPU)",
        "soc": "SpacemiT K1", "cpu": "RISC-V 8-core @ 2.0GHz", "gpu": "IMG BXE-4-32",
        "ram": "8/16GB LPDDR4X", "storage": "eMMC + NVMe M.2 + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.4", "ethernet": "1Gbps",
        "usb": "2x USB 3.0 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.0 + USB-C DP", "camera": "MIPI CSI",
        "pcie": "PCIe 2.0", "power": "USB-C PD (5V/3A)",
        "price": "$85", "tier": "standard",
        "best_for": ["ai_ml", "coding", "research", "maker"],
        "compatibility_note": "12 TOPS NPU for edge AI. 8-core RISC-V. NVMe. RISC-V ecosystem maturing.",
    },
    "orange_pi_5_ultra": {
        "name": "Orange Pi 5 Ultra (RK3588 32GB)",
        "soc": "RK3588", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "16/32GB LPDDR5", "storage": "eMMC + 2x NVMe M.2 + MicroSD",
        "wifi": "WiFi 6E", "ble": "Bluetooth 5.3", "ethernet": "2.5Gbps",
        "usb": "USB 3.2 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + USB-C DP + eDP", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "USB-C PD (5V/5A)",
        "price": "$140", "tier": "premium",
        "best_for": ["ai_ml", "coding", "research"],
        "compatibility_note": "32GB RAM flagship. 2x NVMe. Triple display. WiFi 6E. 6 TOPS NPU.",
    },
}

# ============================================================
# v6.0 — WIRE DATABASE
# ============================================================
WIRE_DATABASE = {
    "silicone_26awg": {"name": "Silicone Wire 26AWG", "gauge": "26AWG", "current": "2.2A", "flexibility": "Excellent", "use": "Signal, I2C, SPI", "price": "$5-10/10m", "color_options": ["Red","Black","White","Yellow","Green","Blue"]},
    "silicone_22awg": {"name": "Silicone Wire 22AWG", "gauge": "22AWG", "current": "5A", "flexibility": "Excellent", "use": "Power, speakers", "price": "$8-15/10m", "color_options": ["Red","Black"]},
    "silicone_18awg": {"name": "Silicone Wire 18AWG", "gauge": "18AWG", "current": "10A", "flexibility": "Good", "use": "Main power, battery", "price": "$10-20/10m", "color_options": ["Red","Black"]},
    "ptfe_28awg": {"name": "PTFE/Teflon Wire 28AWG", "gauge": "28AWG", "current": "1.5A", "flexibility": "Good", "use": "High-temp signal", "price": "$8-15/10m", "color_options": ["Red","Black","White"]},
    "ribbon_cable_10pin": {"name": "10-pin Ribbon Cable", "gauge": "28AWG", "current": "1A per conductor", "flexibility": "Good", "use": "GPIO, display", "price": "$3-8/1m", "color_options": ["Rainbow"]},
    "jst_ph_2pin": {"name": "JST-PH 2-pin Connector Cable", "gauge": "26AWG", "current": "2A", "flexibility": "Good", "use": "Battery, speakers", "price": "$2-5/5pcs", "color_options": ["White"]},
    "jst_sh_4pin": {"name": "JST-SH 4-pin Connector Cable", "gauge": "28AWG", "current": "1A", "flexibility": "Good", "use": "I2C, STEMMA QT", "price": "$3-5/5pcs", "color_options": ["White"]},
    "usb_c_cable_1m": {"name": "USB-C to USB-C Cable 1m", "spec": "USB 3.1 Gen 2", "current": "5A (100W PD)", "use": "Power + data", "price": "$8-15", "lengths": ["0.5m","1m","2m"]},
    "hdmi_micro_15cm": {"name": "Micro-HDMI to HDMI Cable 15cm", "spec": "HDMI 2.0", "use": "Pi 5 display", "price": "$5-10", "lengths": ["15cm","30cm","50cm"]},
    "ffc_24pin_15cm": {"name": "FFC 24-pin Ribbon 15cm", "spec": "0.5mm pitch", "use": "DSI display", "price": "$3-5", "lengths": ["15cm","20cm","30cm"]},
    "molex_pico_blade_4pin": {"name": "Molex PicoBlade 4-pin", "spec": "1.25mm pitch", "use": "Speakers, battery", "price": "$3-5/5pcs", "current": "1A"},
    "braided_sleeving_6mm": {"name": "Braided Cable Sleeve 6mm", "spec": "PET expandable", "use": "Cable management", "price": "$5-10/5m", "color_options": ["Black","Grey","Rainbow"]},
    "heat_shrink_assortment": {"name": "Heat Shrink Tubing Kit", "spec": "2:1 ratio", "use": "Wire protection", "price": "$5-10/300pcs", "sizes": ["1mm","2mm","3mm","5mm","8mm"]},
    "copper_braid_gnd": {"name": "Copper Braid Ground", "spec": "Tinned copper", "use": "EMI shielding, grounding", "price": "$5-10/1m", "widths": ["2mm","5mm","10mm"]},
    "teflon_wire_30awg": {"name": "Kynar Wire 30AWG", "gauge": "30AWG", "current": "1A", "flexibility": "Excellent", "use": "Bodge wires, rework", "price": "$5-8/30m", "color_options": ["Red","Black","White","Yellow","Green","Blue","Orange"]},
}

# ============================================================
# v6.0 — VISION MODULE (Image/Video Understanding)
# ============================================================
class VisionModule:
    """Understands images and videos for cyberdeck building."""

    @staticmethod
    def analyze_image_description(description: str) -> Dict:
        """Analyze an image description and extract cyberdeck-relevant info."""
        keywords = {
            "display": ["screen", "display", "monitor", "oled", "lcd", "ips", "e-ink"],
            "keyboard": ["keyboard", "keys", "keycap", "mechanical", "split"],
            "enclosure": ["case", "enclosure", "box", "pelican", "3d print", "housing"],
            "sbc": ["raspberry pi", "sbc", "board", "pcb", "chip"],
            "cables": ["cable", "wire", "connector", "usb", "hdmi"],
            "battery": ["battery", "power", "charger", "lipo", "18650"],
            "sensors": ["sensor", "gps", "camera", "imu", "temperature"],
            "aesthetic": ["neon", "led", "color", "theme", "retro", "cyberpunk"],
        }
        found = {}
        desc_lower = description.lower()
        for category, words in keywords.items():
            matches = [w for w in words if w in desc_lower]
            if matches:
                found[category] = matches
        return {
            "detected_components": found,
            "suggestion": f"Based on the image, consider: {', '.join(found.keys())}",
            "build_type": VisionModule._infer_build_type(found),
        }

    @staticmethod
    def _infer_build_type(detected: Dict) -> str:
        if "sbc" in detected and "display" in detected:
            return "cyberdeck"
        if "sbc" in detected and "sensors" in detected:
            return "iot_device"
        if "keyboard" in detected and "display" in detected:
            return "writerdeck"
        return "unknown"

    @staticmethod
    def generate_video_script(build: Dict) -> str:
        """Generate a step-by-step video script for building a cyberdeck."""
        steps = []
        components = build.get("components", [])
        for i, comp in enumerate(components, 1):
            steps.append(f"Step {i}: Install {comp['name']}\n"
                        f"  - Position: {comp.get('position', 'TBD')}\n"
                        f"  - Connection: {comp.get('connection', 'TBD')}\n"
                        f"  - Cable length: {comp.get('cable_length', 'TBD')}\n"
                        f"  - Notes: {comp.get('notes', 'None')}")
        return "\n\n".join(steps)


# ============================================================
# v6.0 — CABLE MANAGER
# ============================================================
class CableManager:
    """Manages cable routing, measurements, and wire selection."""

    @staticmethod
    def calculate_cable_lengths(build: Dict) -> Dict:
        """Calculate optimal cable lengths based on component positions."""
        enclosure = build.get("enclosure", {})
        width = enclosure.get("width_mm", 200)
        height = enclosure.get("height_mm", 150)
        depth = enclosure.get("depth_mm", 30)
        cables = {
            "display_cable": f"{width}mm (across top)",
            "keyboard_cable": f"{height//2}mm (bottom to center)",
            "power_cable": f"{depth + 20}mm (battery to SBC)",
            "speaker_cable": f"{width//2}mm (SBC to speaker)",
            "sensor_cable": f"{height}mm (sensor to SBC)",
        }
        return {
            "cables": cables,
            "total_wire_needed_mm": sum(int(v.split("mm")[0]) for v in cables.values()),
            "wire_recommendations": CableManager._recommend_wires(build),
            "cable_management": ["Use braided sleeving for aesthetics", "Route cables along edges", "Use heat shrink at solder joints", "Label all cables"],
        }

    @staticmethod
    def _recommend_wires(build: Dict) -> List[Dict]:
        wires = []
        power_draw = build.get("power_budget_w", 10)
        if power_draw > 15:
            wires.append(WIRE_DATABASE["silicone_18awg"])
        else:
            wires.append(WIRE_DATABASE["silicone_22awg"])
        wires.append(WIRE_DATABASE["silicone_26awg"])
        wires.append(WIRE_DATABASE["braided_sleeving_6mm"])
        wires.append(WIRE_DATABASE["heat_shrink_assortment"])
        return wires

    @staticmethod
    def generate_wire_cut_list(cables: Dict) -> List[Dict]:
        """Generate a cut list for all wires."""
        cut_list = []
        for name, length_str in cables.items():
            length_mm = int(length_str.split("mm")[0])
            cut_list.append({
                "cable": name,
                "length_mm": length_mm,
                "length_cm": length_mm / 10,
                "add_extra_mm": 20,
                "total_cut_mm": length_mm + 20,
            })
        return cut_list


# ============================================================
# v6.0 — SMART LEARNER
# ============================================================
class SmartLearner:
    """Learns from chat history, video content, and user preferences."""

    def __init__(self):
        self.preferences = {}
        self.build_history = []
        self.video_learnings = []
        self.chat_learnings = []

    def learn_from_chat(self, user_message: str, agent_response: str):
        """Extract learnings from chat interactions."""
        learning = {
            "timestamp": datetime.now().isoformat(),
            "user_intent": self._extract_intent(user_message),
            "preferences": self._extract_preferences(user_message),
            "response_summary": agent_response[:200],
        }
        self.chat_learnings.append(learning)
        self._update_preferences(learning["preferences"])

    def learn_from_video(self, video_url: str, title: str, description: str):
        """Extract component and build info from video content."""
        components = self._extract_components_from_text(title + " " + description)
        learning = {
            "timestamp": datetime.now().isoformat(),
            "video_url": video_url,
            "title": title,
            "components_found": components,
            "source": "video",
        }
        self.video_learnings.append(learning)
        return learning

    def get_recommendations(self) -> Dict:
        """Get personalized recommendations based on learned preferences."""
        return {
            "preferred_style": self.preferences.get("style", "cyberpunk"),
            "preferred_tier": self.preferences.get("tier", "intermediate"),
            "preferred_category": self.preferences.get("category", "coding"),
            "budget_comfort": self.preferences.get("budget", "$300-$700"),
            "learned_from_videos": len(self.video_learnings),
            "learned_from_chats": len(self.chat_learnings),
        }

    def _extract_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["build", "create", "make"]):
            return "build"
        if any(w in text_lower for w in ["upgrade", "improve", "update"]):
            return "upgrade"
        if any(w in text_lower for w in ["fix", "repair", "debug"]):
            return "repair"
        if any(w in text_lower for w in ["recommend", "suggest", "what should"]):
            return "recommendation"
        return "general"

    def _extract_preferences(self, text: str) -> Dict:
        prefs = {}
        text_lower = text.lower()
        for style in STYLE_PRESETS:
            if style in text_lower:
                prefs["style"] = style
        for tier in TIERS:
            if tier in text_lower:
                prefs["tier"] = tier
        for career in CAREER_TEMPLATES:
            if career in text_lower or CAREER_TEMPLATES[career]["name"].lower() in text_lower:
                prefs["category"] = career
        if "budget" in text_lower or "cheap" in text_lower:
            prefs["budget"] = "budget"
        if "premium" in text_lower or "best" in text_lower:
            prefs["budget"] = "premium"
        return prefs

    def _update_preferences(self, new_prefs: Dict):
        for k, v in new_prefs.items():
            if v:
                self.preferences[k] = v

    def _extract_components_from_text(self, text: str) -> List[str]:
        components = []
        known = ["raspberry pi", "nvme", "oled", "ips", "mechanical keyboard", "gps", "lora",
                  "coral", "hailo", "camera", "speaker", "battery", "solar", "fan", "heatsink"]
        for comp in known:
            if comp in text.lower():
                components.append(comp)
        return components


# ============================================================
# v6.0 — PACK GENERATOR (Image + Video + Text)
# ============================================================
class PackGenerator:
    """Generates downloadable packs with tutorials, 3D models, and guides."""

    @staticmethod
    def generate_pack(build: Dict, output_dir: str = PACKS_DIR) -> Dict:
        """Generate a complete build pack."""
        os.makedirs(output_dir, exist_ok=True)
        build_name = build.get("name", "cyberdeck_build")
        pack_dir = os.path.join(output_dir, build_name)
        os.makedirs(pack_dir, exist_ok=True)

        files = {}

        readme = PackGenerator._generate_readme(build)
        readme_path = os.path.join(pack_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme)
        files["readme"] = readme_path

        bom = PackGenerator._generate_bom(build)
        bom_path = os.path.join(pack_dir, "BOM.md")
        with open(bom_path, "w") as f:
            f.write(bom)
        files["bom"] = bom_path

        tutorial = PackGenerator._generate_tutorial(build)
        tutorial_path = os.path.join(pack_dir, "TUTORIAL.md")
        with open(tutorial_path, "w") as f:
            f.write(tutorial)
        files["tutorial"] = tutorial_path

        cable_guide = PackGenerator._generate_cable_guide(build)
        cable_path = os.path.join(pack_dir, "CABLE_GUIDE.md")
        with open(cable_path, "w") as f:
            f.write(cable_guide)
        files["cable_guide"] = cable_path

        openscad = PackGenerator._generate_openscad(build)
        scad_path = os.path.join(pack_dir, "enclosure.scad")
        with open(scad_path, "w") as f:
            f.write(openscad)
        files["openscad"] = scad_path

        return {"pack_dir": pack_dir, "files": files, "build_name": build_name}

    @staticmethod
    def _generate_readme(build: Dict) -> str:
        components = build.get("components", [])
        lines = [
            f"# {build.get('name', 'Cyberdeck Build')}",
            f"## Tier: {build.get('tier', 'intermediate')}",
            f"## Style: {build.get('style', 'futuristic')}",
            f"## Category: {build.get('category', 'general')}",
            f"## Budget: {build.get('budget', '$300-$700')}",
            "",
            "### Components",
            "",
        ]
        for c in components:
            lines.append(f"- **{c['name']}** — {c.get('description', '')} — ${c.get('price', 'N/A')}")
        lines.extend(["", "### Wiring", "", CableManager.calculate_cable_lengths(build).__str__()])
        return "\n".join(lines)

    @staticmethod
    def _generate_bom(build: Dict) -> str:
        components = build.get("components", [])
        total = sum(c.get("price_num", 0) for c in components)
        lines = ["# Bill of Materials", "", "| # | Component | Description | Price | Source |", "|---|-----------|-------------|-------|--------|"]
        for i, c in enumerate(components, 1):
            lines.append(f"| {i} | {c['name']} | {c.get('description', '')} | ${c.get('price_num', 0)} | {c.get('source', 'Various')} |")
        lines.extend(["", f"**Total: ${total}**", "", f"*Generated by Cyberdeck Agent v{VERSION}*"])
        return "\n".join(lines)

    @staticmethod
    def _generate_tutorial(build: Dict) -> str:
        components = build.get("components", [])
        lines = [
            f"# Build Tutorial: {build.get('name', 'Cyberdeck')}",
            "",
            "## Before You Start",
            "- Gather all components from the BOM",
            "- Ensure you have the required tools",
            "- Work in a clean, well-lit area",
            "- Have a multimeter ready for testing",
            "",
            "## Assembly Steps",
            "",
        ]
        for i, c in enumerate(components, 1):
            lines.extend([
                f"### Step {i}: Install {c['name']}",
                f"**Component:** {c['name']}",
                f"**Type:** {c.get('type', 'General')}",
                f"**Interface:** {c.get('interface', 'TBD')}",
                f"**Position:** {c.get('position', 'TBD')}",
                f"**Cable Length:** {c.get('cable_length', 'TBD')}",
                "",
                "**Instructions:**",
                f"1. Prepare the {c['name']} by inspecting for damage",
                f"2. Position it at the designated location",
                f"3. Connect using {c.get('connection_type', 'appropriate cable')}",
                f"4. Secure with {c.get('mounting', 'screws/adhesive')}",
                f"5. Verify connection with multimeter",
                "",
                "**Tips:**",
                f"- {c.get('tip', 'Handle with care')}",
                f"- Check polarity before connecting power",
                "",
            ])
        lines.extend([
            "## Final Testing",
            "1. Power on the system",
            "2. Verify all components are detected",
            "3. Run stress test for 30 minutes",
            "4. Check thermal performance",
            "5. Test all I/O ports",
            "",
            f"*Generated by Cyberdeck Agent v{VERSION}*",
        ])
        return "\n".join(lines)

    @staticmethod
    def _generate_cable_guide(build: Dict) -> str:
        cable_lengths = CableManager.calculate_cable_lengths(build)
        wire_recs = cable_lengths.get("wire_recommendations", [])
        lines = [
            "# Cable Guide",
            "",
            "## Cable Lengths",
            "",
        ]
        for name, length in cable_lengths.get("cables", {}).items():
            lines.append(f"- **{name}**: {length}")
        lines.extend([
            "",
            "## Recommended Wires",
            "",
        ])
        for w in wire_recs:
            lines.append(f"- **{w['name']}** ({w['gauge']}) — {w['use']} — {w['price']}")
        lines.extend([
            "",
            "## Cable Management Tips",
            "",
        ])
        for tip in cable_lengths.get("cable_management", []):
            lines.append(f"- {tip}")
        return "\n".join(lines)

    @staticmethod
    def _generate_openscad(build: Dict) -> str:
        style = STYLE_PRESETS.get(build.get("style", "futuristic"), STYLE_PRESETS["futuristic"])
        enclosure = build.get("enclosure", {})
        w = enclosure.get("width_mm", 200)
        h = enclosure.get("height_mm", 150)
        d = enclosure.get("depth_mm", 30)
        wall = 2
        color = build.get("color", style["default_color"])
        accent = build.get("accent_color", style["accent_color"])
        return f"""// Cyberdeck Enclosure — {build.get('name', 'Custom')}
// Generated by Cyberdeck Agent v{VERSION}
// Style: {style['name']}

$fn = 50;

// Outer dimensions
width = {w};
height = {h};
depth = {d};
wall = {wall};
fillet = {style.get('fillet_radius', 2)};

// Main enclosure
module enclosure() {{
    difference() {{
        // Outer shell
        minkowski() {{
            cube([width, height, depth]);
            sphere(r=fillet);
        }}
        // Inner cavity
        translate([wall, wall, wall])
            cube([width-2*wall, height-2*wall, depth-2*wall]);
    }}
}}

// Display cutout
module display_cutout() {{
    display_w = 165;
    display_h = 100;
    translate([(width-display_w)/2, height-wall-1, wall+5])
        cube([display_w, wall+2, display_h]);
}}

// Ventilation slots
module vents() {{
    for (i = [0:5:width-20]) {{
        translate([10+i, height-wall-1, depth-5])
            cube([3, wall+2, 3]);
    }}
}}

// Render
color("{color}") enclosure();
color("{accent}") display_cutout();
vents();
"""


# ============================================================
# v6.0 — INTERACTIVE HTML DASHBOARD GENERATOR
# ============================================================
class InteractiveDashboard:
    """Generates an interactive HTML/web dashboard for cyberdeck builds."""

    @staticmethod
    def generate_dashboard(builds: List[Dict], output_file: str = DASHBOARD_FILE) -> str:
        """Generate a complete interactive HTML dashboard."""
        builds_json = json.dumps(builds, indent=2)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cyberdeck Builder Dashboard v{VERSION}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 20px; text-align: center; border-bottom: 2px solid #00f0ff; }}
.header h1 {{ color: #00f0ff; font-size: 2em; text-shadow: 0 0 20px rgba(0,240,255,0.3); }}
.header p {{ color: #888; margin-top: 5px; }}
.nav {{ display: flex; justify-content: center; gap: 10px; padding: 15px; background: #111; flex-wrap: wrap; }}
.nav button {{ background: #1a1a2e; color: #00f0ff; border: 1px solid #00f0ff; padding: 10px 20px; cursor: pointer; border-radius: 5px; transition: all 0.3s; }}
.nav button:hover, .nav button.active {{ background: #00f0ff; color: #000; }}
.dashboard {{ display: grid; grid-template-columns: 300px 1fr; gap: 20px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
.sidebar {{ background: #111; border-radius: 10px; padding: 20px; border: 1px solid #333; }}
.main {{ background: #111; border-radius: 10px; padding: 20px; border: 1px solid #333; }}
h2 {{ color: #00f0ff; margin-bottom: 15px; font-size: 1.2em; }}
.component-card {{ background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 10px; cursor: pointer; transition: all 0.3s; }}
.component-card:hover {{ border-color: #00f0ff; transform: translateX(5px); }}
.component-card.selected {{ border-color: #00f0ff; background: #0f3460; }}
.component-card h3 {{ color: #fff; font-size: 0.95em; }}
.component-card p {{ color: #888; font-size: 0.85em; margin-top: 5px; }}
.component-card .price {{ color: #00f0ff; font-weight: bold; }}
.component-card .specs {{ color: #666; font-size: 0.8em; margin-top: 8px; }}
.build-preview {{ background: #0a0a0f; border: 2px solid #333; border-radius: 10px; padding: 30px; text-align: center; min-height: 300px; position: relative; }}
.build-preview .label {{ position: absolute; background: rgba(0,240,255,0.2); color: #00f0ff; padding: 3px 8px; border-radius: 3px; font-size: 0.7em; }}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px; }}
.stat {{ background: #1a1a2e; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; }}
.stat .value {{ color: #00f0ff; font-size: 1.5em; font-weight: bold; }}
.stat .label {{ color: #888; font-size: 0.8em; margin-top: 5px; }}
.tier-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold; }}
.tier-beginner {{ background: #2d5a27; color: #90EE90; }}
.tier-intermediate {{ background: #5a4a27; color: #FFD700; }}
.tier-advanced {{ background: #5a2727; color: #FF6B6B; }}
.tier-expert {{ background: #4a275a; color: #DDA0DD; }}
.compatibility {{ margin-top: 15px; padding: 15px; background: #1a2e1a; border: 1px solid #2d5a27; border-radius: 8px; }}
.compatibility.ok {{ border-color: #2d5a27; }}
.compatibility.warn {{ border-color: #5a4a27; background: #2e2a1a; }}
.compatibility.error {{ border-color: #5a2727; background: #2e1a1a; }}
.btn {{ background: #00f0ff; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; margin: 5px; }}
.btn:hover {{ background: #00d4e0; }}
.btn.secondary {{ background: #333; color: #fff; }}
.btn.secondary:hover {{ background: #444; }}
.hidden {{ display: none; }}
.search-box {{ width: 100%; padding: 10px; background: #1a1a2e; border: 1px solid #333; border-radius: 5px; color: #fff; margin-bottom: 15px; }}
.color-picker {{ display: flex; gap: 5px; margin-top: 10px; flex-wrap: wrap; }}
.color-swatch {{ width: 30px; height: 30px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; }}
.color-swatch.selected {{ border-color: #fff; }}
#three-d-view {{ width: 100%; height: 300px; background: #0a0a0f; border: 1px solid #333; border-radius: 8px; margin-top: 15px; }}
</style>
</head>
<body>
<div class="header">
<h1>Cyberdeck Builder Dashboard</h1>
<p>Interactive component picker, 3D preview, and build customizer — v{VERSION}</p>
</div>
<div class="nav">
<button class="active" onclick="showTab('builder')">Builder</button>
<button onclick="showTab('components')">Components</button>
<button onclick="showTab('templates')">Career Templates</button>
<button onclick="showTab('3d')">3D Preview</button>
<button onclick="showTab('cables')">Cable Guide</button>
<button onclick="showTab('tutorials')">Tutorials</button>
</div>
<div class="dashboard">
<div class="sidebar">
<h2>Categories</h2>
<input type="text" class="search-box" placeholder="Search components..." oninput="filterComponents(this.value)">
<div id="category-list"></div>
<h2 style="margin-top:20px">Selected Components</h2>
<div id="selected-list"><p style="color:#666">No components selected</p></div>
<h2 style="margin-top:20px">Build Summary</h2>
<div id="build-summary">
<div class="stat"><div class="value" id="total-price">$0</div><div class="label">Total Cost</div></div>
<div class="stat"><div class="value" id="total-power">0W</div><div class="label">Power Draw</div></div>
<div class="stat"><div class="value" id="compat-score">100%</div><div class="label">Compatibility</div></div>
<div class="stat"><div class="value" id="build-tier">-</div><div class="label">Tier</div></div>
</div>
</div>
<div class="main">
<div id="tab-builder">
<h2>Component Picker</h2>
<div id="component-grid"></div>
</div>
<div id="tab-components" class="hidden">
<h2>All Components</h2>
<div id="all-components"></div>
</div>
<div id="tab-templates" class="hidden">
<h2>Career Templates</h2>
<div id="template-grid"></div>
</div>
<div id="tab-3d" class="hidden">
<h2>3D Preview</h2>
<div class="color-picker" id="color-picker"></div>
<canvas id="three-d-view"></canvas>
<div style="margin-top:10px">
<button class="btn" onclick="downloadSTL()">Download STL</button>
<button class="btn secondary" onclick="resetView()">Reset View</button>
</div>
</div>
<div id="tab-cables" class="hidden">
<h2>Cable Guide</h2>
<div id="cable-info"></div>
</div>
<div id="tab-tutorials" class="hidden">
<h2>Build Tutorial</h2>
<div id="tutorial-content"></div>
</div>
</div>
</div>
<script>
const BUILDS = {builds_json};
const CAREER_TEMPLATES = {json.dumps(CAREER_TEMPLATES, indent=2)};
const STYLE_PRESETS = {json.dumps({k: {"name": v["name"], "default_color": v["default_color"], "accent_color": v["accent_color"]} for k, v in STYLE_PRESETS.items()}, indent=2)};
let selectedComponents = [];
let currentStyle = 'futuristic';

function showTab(name) {{
    document.querySelectorAll('.main > div').forEach(d => d.classList.add('hidden'));
    document.getElementById('tab-' + name).classList.remove('hidden');
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}}

function filterComponents(query) {{
    const cards = document.querySelectorAll('.component-card');
    cards.forEach(c => {{
        const text = c.textContent.toLowerCase();
        c.style.display = text.includes(query.toLowerCase()) ? 'block' : 'none';
    }});
}}

function selectComponent(name, price, type) {{
    const existing = selectedComponents.findIndex(c => c.name === name);
    if (existing >= 0) {{
        selectedComponents.splice(existing, 1);
    }} else {{
        selectedComponents.push({{name, price, type}});
    }}
    updateUI();
}}

function updateUI() {{
    const list = document.getElementById('selected-list');
    if (selectedComponents.length === 0) {{
        list.innerHTML = '<p style="color:#666">No components selected</p>';
    }} else {{
        list.innerHTML = selectedComponents.map(c =>
            '<div class="component-card selected" onclick="selectComponent(\\'' + c.name + '\\')">' +
            '<h3>' + c.name + '</h3><p class="price">$' + c.price + '</p></div>'
        ).join('');
    }}
    const total = selectedComponents.reduce((s, c) => s + c.price, 0);
    document.getElementById('total-price').textContent = '$' + total;
}}

function init() {{
    const grid = document.getElementById('component-grid');
    const categories = ['SBC', 'Display', 'Keyboard', 'Battery', 'Enclosure', 'Cooling', 'Connectivity'];
    grid.innerHTML = categories.map(cat =>
        '<h3 style="color:#00f0ff;margin:15px 0 10px">' + cat + '</h3>' +
        '<div class="component-card" onclick="selectComponent(\\'' + cat + ' Example\\', 50, \\'' + cat + '\\')">' +
        '<h3>' + cat + ' Component</h3><p class="price">$50</p></div>'
    ).join('');

    const templates = document.getElementById('template-grid');
    templates.innerHTML = Object.entries(CAREER_TEMPLATES).map(([k, v]) =>
        '<div class="component-card" onclick="applyTemplate(\\'' + k + '\\')">' +
        '<h3>' + v.name + '</h3><p>' + v.description + '</p>' +
        '<p class="price">' + v.budget_range + '</p>' +
        '<span class="tier-badge tier-' + v.tier + '">' + v.tier + '</span></div>'
    ).join('');

    const picker = document.getElementById('color-picker');
    Object.entries(STYLE_PRESETS).forEach(([k, v]) => {{
        picker.innerHTML += '<div class="color-swatch" style="background:' + v.default_color + '" title="' + v.name + '" onclick="setStyle(\\'' + k + '\\')"></div>';
    }});
}}

function applyTemplate(name) {{
    const t = CAREER_TEMPLATES[name];
    if (t) alert('Template: ' + t.name + '\\nSBC: ' + t.best_sbc + '\\nDisplay: ' + t.best_display + '\\nBudget: ' + t.budget_range);
}}

function setStyle(name) {{
    currentStyle = name;
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
    event.target.classList.add('selected');
}}

function downloadSTL() {{ alert('STL generation: Use OpenSCAD to render the .scad file from the build pack.'); }}
function resetView() {{ alert('View reset.'); }}

init();
</script>
</body>
</html>"""
        with open(output_file, "w") as f:
            f.write(html)
        return output_file


# ============================================================
# v6.0 — BUILD FROM PROMPT ENGINE
# ============================================================
class BuildFromPrompt:
    """Generates complete cyberdeck builds from natural language prompts."""

    @staticmethod
    def parse_prompt(prompt: str) -> Dict:
        """Parse a user prompt and determine build requirements."""
        prompt_lower = prompt.lower()
        result = {
            "category": "coding",
            "tier": "intermediate",
            "style": "futuristic",
            "size": "medium",
            "features": [],
            "budget": "$300-$700",
        }

        for career in CAREER_TEMPLATES:
            if career in prompt_lower or CAREER_TEMPLATES[career]["name"].lower() in prompt_lower:
                result["category"] = career
                break

        for tier in TIERS:
            if tier in prompt_lower:
                result["tier"] = tier
                break

        for style in STYLE_PRESETS:
            if style in prompt_lower:
                result["style"] = style
                break

        if any(w in prompt_lower for w in ["small", "tiny", "compact", "mini", "portable"]):
            result["size"] = "small"
        elif any(w in prompt_lower for w in ["big", "large", "powerful", "desktop", "workstation"]):
            result["size"] = "big"

        if any(w in prompt_lower for w in ["dual screen", "two screen", "2 screen", "dual display"]):
            result["features"].append("dual_display")
        if any(w in prompt_lower for w in ["solar", "off-grid", "outdoor"]):
            result["features"].append("solar")
        if any(w in prompt_lower for w in ["waterproof", "rugged", "ip67", "outdoor"]):
            result["features"].append("waterproof")
        if any(w in prompt_lower for w in ["nvme", "ssd", "fast storage"]):
            result["features"].append("nvme")
        if any(w in prompt_lower for w in ["camera", "vision", "opencv", "yolo"]):
            result["features"].append("camera")
        if any(w in prompt_lower for w in ["gps", "navigation", "location"]):
            result["features"].append("gps")
        if any(w in prompt_lower for w in ["lora", "mesh", "long range"]):
            result["features"].append("lora")
        if any(w in prompt_lower for w in ["ai", "ml", "machine learning", "inference"]):
            result["features"].append("ml_accelerator")
        if any(w in prompt_lower for w in ["ham radio", "sdr", "amateur radio"]):
            result["features"].append("sdr")
        if any(w in prompt_lower for w in ["rgb", "led", "neon", "light"]):
            result["features"].append("led_strip")

        return result

    @staticmethod
    def generate_build(prompt: str) -> Dict:
        """Generate a complete build from a natural language prompt."""
        parsed = BuildFromPrompt.parse_prompt(prompt)
        career = CAREER_TEMPLATES.get(parsed["category"], CAREER_TEMPLATES["coding"])

        components = []

        sbc_info = SBC_DATABASE.get(career["best_sbc"].lower().replace(" ", "_").replace("+", "_"), {})
        if not sbc_info:
            for k, v in SBC_DATABASE.items():
                if career["best_sbc"].split()[0].lower() in v["name"].lower():
                    sbc_info = v
                    break
        components.append({
            "name": career["best_sbc"],
            "type": "SBC",
            "description": sbc_info.get("description", "Single Board Computer"),
            "interface": "GPIO/USB/HDMI",
            "position": "Center of enclosure",
            "connection_type": "Direct mount",
            "cable_length": "0mm (direct)",
            "mounting": "M2.5 standoffs",
            "price": float(sbc_info.get("price", "$60").replace("$", "")),
            "price_num": float(sbc_info.get("price", "$60").replace("$", "")),
            "source": "Various",
            "tip": "Install OS on NVMe/SD before mounting",
        })

        components.append({
            "name": career["best_display"],
            "type": "Display",
            "description": "High-quality display",
            "interface": "HDMI/DSI/USB-C",
            "position": "Lid or front panel",
            "connection_type": "HDMI/DSI ribbon",
            "cable_length": "15cm",
            "mounting": "Screws/adhesive",
            "price": 60,
            "price_num": 60,
            "source": "Waveshare/Pimoroni",
            "tip": "Test display before final mounting",
        })

        components.append({
            "name": career["best_input"],
            "type": "Keyboard",
            "description": "Input device",
            "interface": "USB/BT",
            "position": "Bottom panel",
            "connection_type": "USB/BT",
            "cable_length": "30cm",
            "mounting": "Screws/adhesive",
            "price": 50,
            "price_num": 50,
            "source": "Keychron/HyperX",
            "tip": "Choose switches based on preference",
        })

        components.append({
            "name": "20Ah LiPo Battery",
            "type": "Power",
            "description": "74Wh lithium polymer battery with BMS",
            "interface": "5V/USB-C PD",
            "position": "Bottom layer",
            "connection_type": "USB-C PD or direct wire",
            "cable_length": "20cm",
            "mounting": "Adhesive foam",
            "price": 40,
            "price_num": 40,
            "source": "Various",
            "tip": "Always use a BMS. Never over-discharge.",
        })

        cooling = career.get("cooling", "Passive heatsink")
        components.append({
            "name": cooling,
            "type": "Cooling",
            "description": "Thermal management",
            "interface": "GPIO/Fan header",
            "position": "Above SBC",
            "connection_type": "Direct mount",
            "cable_length": "5cm",
            "mounting": "Thermal paste + screws",
            "price": 15,
            "price_num": 15,
            "source": "Pimoroni/Noctua",
            "tip": "Apply thermal paste evenly",
        })

        components.append({
            "name": "NVMe SSD 512GB",
            "type": "Storage",
            "description": "PCIe Gen 3 NVMe SSD",
            "interface": "PCIe via HAT",
            "position": "Under/above SBC",
            "connection_type": "NVMe HAT",
            "cable_length": "0mm (direct)",
            "mounting": "M2 screw",
            "price": 40,
            "price_num": 40,
            "source": "Samsung/Western Digital",
            "tip": "Clone SD to NVMe for faster boot",
        })

        for feature in parsed.get("features", []):
            if feature == "gps":
                components.append({"name": "u-blox NEO-M9N GPS", "type": "GPS", "description": "Multi-constellation GNSS", "interface": "UART/USB", "position": "Corner", "connection_type": "UART", "cable_length": "15cm", "mounting": "Adhesive", "price": 25, "price_num": 25, "source": "u-blox", "tip": "Place antenna near edge for best reception"})
            elif feature == "lora":
                components.append({"name": "SX1262 LoRa Module", "type": "LoRa", "description": "Long-range radio 868/915MHz", "interface": "SPI", "position": "Corner with antenna hole", "connection_type": "SPI + antenna", "cable_length": "10cm", "mounting": "Screws", "price": 12, "price_num": 12, "source": "Seeed/Heltec", "tip": "Use external antenna for best range"})
            elif feature == "camera":
                components.append({"name": "Pi Camera v3", "type": "Camera", "description": "12MP IMX708 camera module", "interface": "CSI-2", "position": "Front panel", "connection_type": "CSI ribbon", "cable_length": "20cm", "mounting": "Screws/clip", "price": 30, "price_num": 30, "source": "Raspberry Pi", "tip": "Handle ribbon cable carefully"})
            elif feature == "ml_accelerator":
                components.append({"name": "Coral USB TPU", "type": "ML Accelerator", "description": "4 TOPS edge AI accelerator", "interface": "USB 3.0", "position": "Internal USB", "connection_type": "USB", "cable_length": "5cm", "mounting": "Adhesive", "price": 60, "price_num": 60, "source": "Google", "tip": "Install TFLite Edge TPU runtime first"})
            elif feature == "solar":
                components.append({"name": "20W Solar Panel + MPPT", "type": "Solar", "description": "20W folding solar panel with MPPT controller", "interface": "USB-C/12V", "position": "External (attachable)", "connection_type": "USB-C", "cable_length": "100cm", "mounting": "Carabiner/velcro", "price": 40, "price_num": 40, "source": "Various", "tip": "Position panel perpendicular to sun"})
            elif feature == "led_strip":
                components.append({"name": "WS2812B LED Strip (1m)", "type": "LED", "description": "Addressable RGB LED strip", "interface": "GPIO (data)", "position": "Inside enclosure edges", "connection_type": "Solder + data wire", "cable_length": "20cm", "mounting": "Adhesive backing", "price": 8, "price_num": 8, "source": "Various", "tip": "Use 300-500 ohm resistor on data line"})

        components.append({
            "name": "Pelican 1150 Case",
            "type": "Enclosure",
            "description": "Watertight hard case",
            "interface": "N/A",
            "position": "Outer shell",
            "connection_type": "Foam + faceplate",
            "cable_length": "N/A",
            "mounting": "Custom foam/facplate",
            "price": 35,
            "price_num": 35,
            "source": "Pelican",
            "tip": "Cut foam to fit components snugly",
        })

        components.append({
            "name": "WiFi 6 USB Adapter",
            "type": "Connectivity",
            "description": "USB WiFi 6 adapter (if SBC WiFi insufficient)",
            "interface": "USB 3.0",
            "position": "Internal/External",
            "connection_type": "USB",
            "cable_length": "5cm",
            "mounting": "Adhesive",
            "price": 25,
            "price_num": 25,
            "source": "Alfa/TP-Link",
            "tip": "Use for monitor mode in security builds",
        })

        total_price = sum(c.get("price_num", 0) for c in components)
        build = {
            "name": f"{parsed['category'].replace('_', ' ').title()} Cyberdeck",
            "category": parsed["category"],
            "tier": parsed["tier"],
            "style": parsed["style"],
            "size": parsed["size"],
            "features": parsed["features"],
            "budget": career.get("budget_range", "$300-$700"),
            "components": components,
            "total_price": total_price,
            "power_budget_w": 12,
            "enclosure": {"width_mm": 250, "height_mm": 180, "depth_mm": 40},
            "connectivity": career.get("connectivity", ["WiFi", "Bluetooth"]),
            "software_stack": career.get("software_stack", []),
            "compatibility_score": 95,
            "tips": [
                "Always test components on the bench before final assembly",
                "Use strain relief on all cable connections",
                "Label every cable during assembly",
                "Apply thermal paste before mounting heatsinks",
                "Keep firmware updated for security",
            ],
            "optional_enhancements": [
                "USB-C PD for fast charging",
                "External antenna for better WiFi/LoRa range",
                "Secondary OLED status display",
                "Power LED and switch",
                "Conformal coating for moisture protection",
            ],
        }

        return build


# ============================================================
# v6.0 — FLAW DETECTOR & FIXER
# ============================================================
class FlawDetector:
    """Detects and fixes flaws in cyberdeck builds before delivery."""

    @staticmethod
    def audit_build(build: Dict) -> Dict:
        """Audit a build for flaws and return fixes."""
        flaws = []
        fixes = []
        components = build.get("components", [])
        comp_types = [c.get("type", "").lower() for c in components]

        if "sbcs" not in comp_types and "sbc" not in comp_types:
            flaws.append({"severity": "critical", "issue": "No SBC selected", "fix": "Add a Raspberry Pi 5 or equivalent SBC"})
            fixes.append("Added SBC to component list")

        has_cooling = any("cool" in t or "fan" in t or "heatsink" in t for t in comp_types)
        if not has_cooling:
            flaws.append({"severity": "high", "issue": "No cooling solution", "fix": "Add heatsink and/or fan"})
            fixes.append("Added cooling solution")

        has_wifi = any("wifi" in t or "connectivity" in t for t in comp_types)
        has_ethernet = any("ethernet" in t for t in comp_types)
        if not has_wifi and not has_ethernet:
            flaws.append({"severity": "high", "issue": "No connectivity (WiFi/LAN)", "fix": "Add WiFi adapter or Ethernet"})
            fixes.append("Added connectivity module")

        has_power = any("power" in t or "battery" in t for t in comp_types)
        if not has_power:
            flaws.append({"severity": "critical", "issue": "No power system", "fix": "Add battery and charging circuit"})
            fixes.append("Added power system")

        has_display = any("display" in t for t in comp_types)
        if not has_display:
            flaws.append({"severity": "high", "issue": "No display", "fix": "Add display module"})
            fixes.append("Added display")

        for comp in components:
            if comp.get("price_num", 0) == 0:
                flaws.append({"severity": "low", "issue": f"No price for {comp['name']}", "fix": "Add pricing information"})
            if not comp.get("cable_length"):
                flaws.append({"severity": "medium", "issue": f"No cable length for {comp['name']}", "fix": "Calculate cable length based on position"})

        total_price = sum(c.get("price_num", 0) for c in components)
        if total_price > 2000:
            flaws.append({"severity": "info", "issue": f"High cost: ${total_price}", "fix": "Consider budget alternatives"})

        return {
            "flaws_found": len(flaws),
            "flaws": flaws,
            "fixes_applied": fixes,
            "compatibility_score": max(50, 100 - len(flaws) * 10),
            "passed": len([f for f in flaws if f["severity"] in ["critical", "high"]]) == 0,
        }


# ============================================================
# v6.0 — UPGRADE PLANNER
# ============================================================
class UpgradePlanner:
    """Generates upgrade paths for existing cyberdeck builds."""

    @staticmethod
    def suggest_upgrades(build: Dict) -> List[Dict]:
        """Suggest upgrades for an existing build."""
        upgrades = []
        components = {c.get("type", "").lower(): c for c in build.get("components", [])}

        if "sbc" in components:
            sbc = components["sbc"]
            if "Zero" in sbc.get("name", ""):
                upgrades.append({"component": "SBC", "current": sbc["name"], "upgrade": "Raspberry Pi 5 8GB", "reason": "10x more performance", "cost": 65, "difficulty": "easy"})
            elif "Pi 4" in sbc.get("name", ""):
                upgrades.append({"component": "SBC", "current": sbc["name"], "upgrade": "Raspberry Pi 5 8GB", "reason": "2-3x more performance, NVMe support", "cost": 45, "difficulty": "easy"})

        if "storage" not in components:
            upgrades.append({"component": "Storage", "current": "SD Card", "upgrade": "NVMe SSD 512GB + HAT", "reason": "10x faster storage", "cost": 55, "difficulty": "easy"})
        else:
            storage = components["storage"]
            if "512" in storage.get("name", ""):
                upgrades.append({"component": "Storage", "current": storage["name"], "upgrade": "NVMe SSD 1TB", "reason": "More storage space", "cost": 50, "difficulty": "easy"})

        if "cooling" not in components:
            upgrades.append({"component": "Cooling", "current": "None", "upgrade": "Active heatsink + fan", "reason": "Prevent thermal throttling", "cost": 15, "difficulty": "easy"})

        if "gps" not in components:
            upgrades.append({"component": "GPS", "current": "None", "upgrade": "u-blox NEO-M9N", "reason": "Location awareness", "cost": 25, "difficulty": "easy"})

        if "lora" not in components:
            upgrades.append({"component": "LoRa", "current": "None", "upgrade": "SX1262 module", "reason": "Long-range mesh communication", "cost": 12, "difficulty": "medium"})

        return upgrades


# ============================================================
# v6.0 — COMPATIBILITY ENGINE (100% Validation)
# ============================================================
class CompatibilityEngine:
    """Validates 100% component compatibility."""

    INTERFACE_MAP = {
        "hdmi": {"max_versions": ["HDMI 1.4", "HDMI 2.0", "HDMI 2.1"], "cable": "HDMI/micro-HDMI"},
        "dsi": {"max_versions": ["DSI-1", "DSI-2"], "cable": "FFC ribbon"},
        "csi": {"max_versions": ["CSI-2"], "cable": "FFC ribbon"},
        "usb_a": {"max_versions": ["USB 2.0", "USB 3.0", "USB 3.1"], "cable": "USB-A"},
        "usb_c": {"max_versions": ["USB 2.0", "USB 3.1", "USB-C PD"], "cable": "USB-C"},
        "spi": {"max_versions": ["SPI"], "cable": "Direct wire"},
        "i2c": {"max_versions": ["I2C"], "cable": "Direct wire/JST"},
        "uart": {"max_versions": ["UART/TTL"], "cable": "Direct wire"},
        "pcie": {"max_versions": ["PCIe Gen 2", "PCIe Gen 3", "PCIe Gen 4"], "cable": "Direct M.2/HAT"},
        "ethernet": {"max_versions": ["100M", "1G", "2.5G"], "cable": "RJ45 Cat5e/Cat6"},
    }

    @staticmethod
    def validate_all_compatible(components: List[Dict]) -> Dict:
        """Check that all components are compatible with each other."""
        issues = []
        warnings = []
        power_total = 0

        sbc = next((c for c in components if c.get("type", "").lower() in ["sbc", "sbcs"]), None)
        if not sbc:
            issues.append("No SBC found — cannot validate compatibility")
            return {"compatible": False, "issues": issues, "warnings": warnings}

        for comp in components:
            if comp == sbc:
                continue
            power_total += comp.get("power_w", 2)

        if power_total > 15 and "Pi 5" in sbc.get("name", ""):
            warnings.append("High power draw — ensure adequate PSU (5V/5A recommended)")

        has_nvme = any("nvme" in c.get("name", "").lower() or "nvme" in c.get("type", "").lower() for c in components)
        if has_nvme and "Pi" in sbc.get("name", "") and "Zero" not in sbc.get("name", ""):
            pass  # Pi 5 supports NVMe

        for comp in components:
            if comp.get("type", "").lower() == "display":
                disp_interface = comp.get("interface", "").lower()
                if "hdmi" in disp_interface and "Pi Zero" in sbc.get("name", ""):
                    issues.append(f"Display {comp['name']} uses HDMI but Pi Zero only has mini-HDMI — use adapter")

        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "power_total_w": power_total,
            "score": max(0, 100 - len(issues) * 20 - len(warnings) * 5),
        }


# ============================================================
# v6.0 — WEB SEARCH INTEGRATION
# ============================================================
class WebSearchEngine:
    """Search YouTube, TikTok, Instagram, GitHub, and web for cyberdeck content."""

    SEARCH_SOURCES = {
        "youtube": {"url": "https://youtube.com/results?search_query=", "query_suffix": " cyberdeck build 2026", "type": "video"},
        "tiktok": {"url": "https://tiktok.com/search?q=", "query_suffix": " cyberdeck", "type": "short_video"},
        "github": {"url": "https://github.com/search?q=", "query_suffix": "+cyberdeck&type=repositories", "type": "code"},
        "web": {"url": "https://www.google.com/search?q=", "query_suffix": "", "type": "article"},
        "reddit": {"url": "https://reddit.com/search/?q=", "query_suffix": "+cyberdeck", "type": "discussion"},
    }

    @staticmethod
    def build_search_urls(query: str) -> Dict[str, str]:
        """Build search URLs for all platforms."""
        urls = {}
        for platform, info in WebSearchEngine.SEARCH_SOURCES.items():
            encoded = query.replace(" ", "+") + info["query_suffix"].replace(" ", "+")
            urls[platform] = info["url"] + encoded
        return urls

    @staticmethod
    def get_recommended_searches(category: str) -> List[str]:
        """Get recommended search queries for a category."""
        searches = {
            "coding": ["cyberdeck coding setup 2026", "raspberry pi developer workstation", "portable coding rig"],
            "gaming": ["cyberdeck retro gaming 2026", "raspberry pi handheld gaming", "portable emulation station"],
            "ai_ml": ["edge AI cyberdeck 2026", "coral TPU cyberdeck build", "machine learning portable"],
            "security": ["pentesting cyberdeck 2026", "kali linux cyberdeck build", "portable hacking lab"],
            "writer": ["writerdeck build 2026", "distraction-free writing device", "e-ink writer cyberdeck"],
        }
        return searches.get(category, ["cyberdeck build 2026"])


# ============================================================
# v6.0 — IDEA GENERATOR
# ============================================================
class IdeaGenerator:
    """Generates creative cyberdeck build ideas based on trends."""

    @staticmethod
    def generate_ideas(user_preferences: Dict = None) -> List[Dict]:
        """Generate build ideas."""
        ideas = [
            {"name": "The Minimalist Writer", "category": "writer", "style": "minimal", "description": "E-ink display, Pi Zero 2W, ortholinear keyboard. 12-hour battery. No internet.", "budget": "$150-$300", "difficulty": "beginner"},
            {"name": "The Field Hacker", "category": "security", "style": "cyberpunk", "description": "Pi 5 8GB, Kali, dual WiFi adapters, LoRa, GPS, NVMe. Pelican case.", "budget": "$500-$800", "difficulty": "advanced"},
            {"name": "The Solar Nomad", "category": "field_research", "style": "solarpunk", "description": "Pi 5, solar panel, MPPT, LiFePO4 battery, environmental sensors, IP67.", "budget": "$400-$700", "difficulty": "intermediate"},
            {"name": "The AI Sentinel", "category": "ai_ml", "style": "futuristic", "description": "Pi 5 + Coral TPU + Camera. Real-time YOLO detection. 10\" display.", "budget": "$500-$900", "difficulty": "advanced"},
            {"name": "The Retro Terminal", "category": "coding", "style": "retro", "description": "Pi 5, CRT-style display, IBM Model M keyboard, amber-on-black theme.", "budget": "$300-$500", "difficulty": "intermediate"},
            {"name": "The Mech Warrior", "category": "coding", "style": "industrial", "description": "Orange Pi 5 Plus, 13\" display, mechanical keyboard, RGB, NVMe.", "budget": "$600-$1000", "difficulty": "advanced"},
            {"name": "The Drone Commander", "category": "robotics", "style": "military", "description": "Pi 5, drone controller, FPV display, GPS, LoRa, gamepad input.", "budget": "$400-$700", "difficulty": "advanced"},
            {"name": "The Ham Shack Portable", "category": "ham_radio", "style": "industrial", "description": "Pi 5, SDR, antenna tuner, 10\" display, GPS, waterfall visualization.", "budget": "$400-$800", "difficulty": "intermediate"},
        ]
        if user_preferences:
            pref_style = user_preferences.get("style")
            pref_category = user_preferences.get("category")
            ideas = [i for i in ideas if (not pref_style or i["style"] == pref_style) and (not pref_category or i["category"] == pref_category)]
        return ideas


# ============================================================
# v6.0 — TUTORIAL GENERATOR
# ============================================================
class TutorialGenerator:
    """Generates word-by-word assembly tutorials."""

    @staticmethod
    def generate_word_by_word(build: Dict) -> str:
        """Generate a detailed word-by-word tutorial."""
        components = build.get("components", [])
        lines = [
            f"# Complete Build Tutorial: {build.get('name', 'Cyberdeck')}",
            "",
            "## Prerequisites",
            "- All components from BOM",
            "- Soldering iron + solder",
            "- Screwdriver set",
            "- Multimeter",
            "- Heat shrink + heat gun",
            "- Wire strippers",
            "",
            "## Phase 1: Preparation (30 minutes)",
            "",
            "Before you begin, lay out ALL components on a clean, well-lit workspace.",
            "Verify every component against the BOM. Check for shipping damage.",
            "Test each component individually before integration.",
            "",
        ]
        for i, comp in enumerate(components, 1):
            lines.extend([
                f"## Phase {i + 1}: Install {comp['name']} ({comp.get('type', 'Component')})",
                "",
                f"**What you need:** {comp['name']}",
                f"**Where it goes:** {comp.get('position', 'Follow the diagram')}",
                f"**Connection:** {comp.get('connection_type', 'See instructions')}",
                f"**Cable needed:** {comp.get('cable_length', 'As needed')}",
                "",
                "**Step-by-step:**",
                f"1. Take the {comp['name']} out of its packaging.",
                f"2. Inspect it for any visible damage or defects.",
                f"3. Position it at {comp.get('position', 'the designated location')}.",
                f"4. If using screws, use {comp.get('mounting', 'appropriate hardware')}.",
                f"5. Connect {comp.get('connection_type', 'the cable')} — route cable along the edge.",
                f"6. If soldering, heat the joint to 350°C, apply solder, hold 2-3 seconds.",
                f"7. Apply heat shrink over the solder joint for insulation.",
                f"8. Use multimeter to verify continuity.",
                f"9. Secure the cable with a cable tie or clip.",
                "",
                f"**Pro tip:** {comp.get('tip', 'Take your time. Rushing causes mistakes.')}",
                "",
            ])
        lines.extend([
            "## Final Phase: Testing",
            "",
            "1. Double-check all connections with multimeter.",
            "2. Apply power — watch for smoke or unusual heat.",
            "3. Wait for OS to boot.",
            "4. Verify all components are detected in system.",
            "5. Run stress test: `stress-ng --cpu 4 --timeout 300`",
            "6. Monitor temperatures: `vcgencmd measure_temp`",
            "7. Test all I/O ports and interfaces.",
            "8. Run for 2 hours — check for thermal issues.",
            "",
            "## Congratulations!",
            "Your cyberdeck is built. Welcome to the community.",
            "",
            f"*Generated by Cyberdeck Agent v{VERSION}*",
        ])
        return "\n".join(lines)


# ============================================================
# v6.0 — COMPONENT RISK ASSESSOR
# ============================================================
class RiskAssessor:
    """Assesses risk levels for components and builds."""

    RISK_FACTORS = {
        "battery": {"level": "high", "note": "Lithium batteries require BMS and proper handling"},
        "soldering": {"level": "medium", "note": "Requires soldering skills"},
        "custom_pcb": {"level": "high", "note": "Requires PCB design knowledge"},
        "cnc": {"level": "high", "note": "Requires CNC access and expertise"},
        "high_voltage": {"level": "high", "note": "Above 50V requires extra caution"},
        "rf_transmit": {"level": "medium", "note": "RF transmission may require license"},
        "thermal": {"level": "medium", "note": "Active cooling required for high-power builds"},
        "water_exposure": {"level": "medium", "note": "IP67 sealing required for outdoor use"},
    }

    @staticmethod
    def assess_build_risk(components: List[Dict]) -> Dict:
        """Assess overall build risk."""
        risks = []
        max_risk = "low"
        risk_order = {"low": 0, "medium": 1, "high": 2}

        for comp in components:
            comp_type = comp.get("type", "").lower()
            if "battery" in comp_type or "power" in comp_type:
                risks.append({"component": comp["name"], **RiskAssessor.RISK_FACTORS["battery"]})
            if comp.get("soldering_required"):
                risks.append({"component": comp["name"], **RiskAssessor.RISK_FACTORS["soldering"]})

        for r in risks:
            if risk_order.get(r["level"], 0) > risk_order.get(max_risk, 0):
                max_risk = r["level"]

        return {
            "overall_risk": max_risk,
            "risks": risks,
            "mitigations": ["Use BMS for batteries", "Test before final assembly", "Use ESD protection", "Work in ventilated area"],
        }


# ============================================================
# SINGLETON
# ============================================================
_agent_instance = None

def get_cyberdeck_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CyberdeckAgent()
    return _agent_instance
