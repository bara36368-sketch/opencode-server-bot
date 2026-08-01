"""
Cyberdeck Agent v7.1 — Full-featured cyberdeck builder, learner, and evolution engine.
Watches videos, analyzes images, builds from prompts, picks best components,
validates compatibility, generates tutorials, and gets smarter over time.

New in v7.1:
  - Local AI Tuner: offline LLM board/model/quant recommendations with NPU-tax warning
  - Battery Hot-Swap & Supercap UPS: power-path design for battery-swap-while-running
  - Ortholinear & Split Keyboard DB: Corne, Helix, Lily58, Ferris Sweep, Sofle, firmware
  - Offline Survival Stack: DTN sync, Kiwix RAG, offline maps, P2P model sharing
  - Community Feature Board: voted mods from cyberdeck.ing + r/cyberDeck
  - Maximalist vs Minimalist Character Builder: themed build generator
  - Scavenge Build Sourcing: thrift/e-waste/dollar-store build plans
  - 2026 Hardware Radar: Pi 500+, Rock 5B 32GB, AI HAT+, Lichee Console 4A, x86 12W

New in v7.0:
  - WriterDeck Mode, Thermal Management Designer, Multi-Build Comparator,
    Build Cost Optimizer, Upgrade Path Analyzer, Solar & Off-Grid Power Planner,
    Beginner Build Wizard, Build Sharing & Export

New in v6.2:
  - Hardware Module System: NATO rail layouts, sliding screen mechanisms,
    NP-F battery sleds, and Li'l PCB hot-swappable module ecosystem
  - Li'l PCB: standardized 30x25mm hot-swap modules (SDR, LoRa, GPS, NVMe, sensors)
    4-slot backplane with I2C + power + GPIO + UART per slot
  - 9 new cyberdeck ideas featuring hardware modules

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
from cyberdeck_bridge import (
    HAS_RUST,
    check_compatibility as rust_check_compatibility,
    audit_build as rust_audit_build,
    auto_fix as rust_auto_fix,
    suggest_upgrades as rust_suggest_upgrades,
    generate_3d_model as rust_generate_3d_model,
    calculate_battery_life as rust_calculate_battery_life,
    calculate_antenna as rust_calculate_antenna,
    bom_generate as rust_bom_generate,
    search_components as rust_search_components,
    generate_cable_plan as rust_generate_cable_plan,
    category_requirements as rust_category_requirements,
    compute_stack_path as rust_compute_stack_path,
    compute_score as rust_compute_score,
)

from cyberdeck_zig_bridge import (
    HAS_ZIG,
    antenna_calc as zig_antenna,
    battery_capacity as zig_battery,
    battery_optimizer as zig_batt_opt,
    mesh_range as zig_mesh,
    nato_rail_layout as zig_nato,
    print_cost as zig_print,
    filament_calc as zig_filament,
    sliding_screen_rail as zig_sliding,
    esp32_power as zig_esp32,
    throughput_est as zig_throughput,
    edge_ai_est as zig_edge,
    heat_sink_calc as zig_heat,
)

logger = logging.getLogger(__name__)

VERSION = "7.1.0"
__all__ = [
    "VERSION", "HAS_ZIG", "HAS_RUST",
    "TIERS", "CAREER_TEMPLATES", "SOC_DATABASE", "SBC_DATABASE", "SBC_ALT_DATABASE",
    "DISPLAY_DATABASE", "BATTERY_DATABASE", "INPUT_DATABASE", "CASE_DATABASE", "TOOL_DATABASE",
    "CABLE_DATABASE", "SOFTWARE_DATABASE", "COOLING_DATABASE",
    "ESPRESSIF_ISA_DATABASE", "BRUCE_FIRMWARE_DATABASE", "GR3ML1N_TEMPLATE",
    "HOMEBREW_OS_DATABASE", "EDGE_AI_DATABASE", "ESP_NOW_DATABASE", "WIFI_BLE_SCANNER_DATABASE",
    "WRITERDECK_DISPLAYS", "WRITER_SOFTWARE", "WRITER_OS_TEMPLATES", "WRITER_KEYBOARDS",
    "SBC_THERMAL_DATA", "COOLING_PARTS_DATABASE",
    "COMPARISON_METRICS",
    "PRICE_SOURCE_DATABASE", "REGION_VENDORS", "BUDGET_TEMPLATES",
    "UPGRADE_PATHS_DATABASE",
    "SOLAR_PANEL_DATABASE", "BATTERY_BANK_DATABASE", "SOLAR_CONTROLLER_DATABASE",
    "SUN_HOURS_BY_REGION", "OFFGRID_TEMPLATES",
    "WIZARD_QUESTIONS", "WIZARD_TEMPLATES",
    "SHARE_TEMPLATES", "EXPORT_THEMES",
    "CyberdeckAgent", "RiskAssessor", "get_cyberdeck_agent",
    "AntennaCalculator", "BatterySizingCalculator",
    "WriterDeckAdvisor", "ThermalDesigner", "BuildComparator",
    "CostOptimizer", "UpgradeAdvisor", "SolarPlanner",
    "BeginnerWizard", "BuildSharing",
    "LOCAL_AI_BOARD_DATABASE", "LOCAL_AI_MODEL_DATABASE", "BUDGET_TIERS_LOCALAI", "LocalAITuner",
    "HOTSWAP_COMPONENT_DATABASE", "HOTSWAP_REFERENCE_BUILDS", "HotSwapPlanner",
    "ORTHO_KEYBOARD_DATABASE", "ORTHO_FIRMWARE_GUIDE", "OrthoAdvisor",
    "OFFGRID_STACK_COMPONENTS", "OFFGRID_REFERENCE_BUILD", "OffgridStackPlanner",
    "COMMUNITY_FEATURE_DATABASE", "CommunityFeatureBoard",
    "GITHUB_BUILDS", "SAMPLE_COMMUNITY_BUILDS", "CommunityExplorer",
    "CHARACTER_TEMPLATES", "CharacterBuilder",
    "SCAVENGE_SOURCES", "SCAVENGE_BUILD_PLAN", "ScavengePlanner",
    "NEW_HARDWARE_2026", "NewHardwareRadar",
    "zig_battery", "zig_antenna", "zig_mesh", "zig_print", "zig_filament",
    "zig_sliding", "zig_esp32", "zig_throughput", "zig_edge", "zig_heat",
    "zig_nato", "zig_batt_opt",
]
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
    "hacker_black": {"name": "Hacker Black", "description": "Matte black, green neon, terminal grid", "default_color": "#0a0a0a", "accent_color": "#00ff66", "screw_style": "hidden", "surface": "smooth matte", "vent_style": "thin matrix slits", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "razor thin", "enclosure_notes": "Add matrix-code emboss, green underglow, cable-managed interior"},
    "milspec": {"name": "MIL-SPEC", "description": "Olive drab, MIL-STD stencils, non-reflective", "default_color": "#4a5230", "accent_color": "#d9d2a5", "screw_style": "exposed hex", "surface": "textured non-reflective", "vent_style": "louvered slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "armored thick", "enclosure_notes": "Add MIL-STD stenciling, QR data plates, tie-down loops, matte clearcoat"},
    "server_room": {"name": "Server Room", "description": "Data center gray, rack rails, cable lacing", "default_color": "#4d4f53", "accent_color": "#2e6bff", "screw_style": "exposed Phillips", "surface": "powder coat texture", "vent_style": "rack vent grills", "led_channels": False, "fillet_radius": 1, "wire_visibility": "laced bundles", "bezel_style": "rack-mount bezel", "enclosure_notes": "Add rack ears, status LEDs, lacing bars, silk-screened port labels"},
    "lab_equipment": {"name": "Lab Equipment", "description": "Institutional white/black, chrome knobs, banana jacks", "default_color": "#e8e8e8", "accent_color": "#c0392b", "screw_style": "exposed hex", "surface": "smooth enamel", "vent_style": "fine perforated", "led_channels": False, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "instrument panel", "enclosure_notes": "Add banana-jack cutouts, rotary knob decals, oscilloscope grid bezel, enamel finish"},
    "nasa_white": {"name": "NASA White", "description": "White panels, red/blue accents, mission patch vibe", "default_color": "#f2f2f2", "accent_color": "#b31b1b", "screw_style": "exposed (torx)", "surface": "smooth gloss", "vent_style": "aerospace slits", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "thin rounded", "enclosure_notes": "Add mission-patch decal, velcro strap anchors, stowage labels"},
    "aircraft_cockpit": {"name": "Aircraft Cockpit", "description": "Dark avionics, backlit legends, knurled knobs", "default_color": "#1e2226", "accent_color": "#ffb300", "screw_style": "exposed Phillips", "surface": "textured anti-glare", "vent_style": "avionics slot", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "avionics frame", "enclosure_notes": "Add backlit button decals, sun-shade lip, grommet cable exits"},
    "submarine_sonar": {"name": "Submarine Sonar", "description": "Deep green phosphor, brass, watertight vibe", "default_color": "#14201a", "accent_color": "#7fff00", "screw_style": "exposed brass", "surface": "painted steel", "vent_style": "port ring", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "round porthole", "enclosure_notes": "Add ring gasket bezels, brass valves, depth-gauge decal, damped interior"},
    "telecom_gray": {"name": "Telecom Gray", "description": "Western Electric gray, 66 blocks, punchdown vibe", "default_color": "#b5b7b9", "accent_color": "#666666", "screw_style": "exposed Phillips", "surface": "vinyl laminate", "vent_style": "louvered", "led_channels": False, "fillet_radius": 1, "wire_visibility": "visible", "bezel_style": "square", "enclosure_notes": "Add punchdown block decal, phone-jack cutouts, rotary dial bezel"},
    "dsp_module": {"name": "DSP Module", "description": "Euro-module style, black/gold, knobs and jacks", "default_color": "#151515", "accent_color": "#d4af37", "screw_style": "exposed hex", "surface": "anodized texture", "vent_style": "small slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "module faceplate", "enclosure_notes": "Add gold knob decals, patch-jack cutouts, module mounting holes"},
    "synth_rack": {"name": "Synth Rack", "description": "Modular synth, wood cheeks, rainbow patch points", "default_color": "#1a1a1a", "accent_color": "#ff4d4d", "screw_style": "exposed hex", "surface": "textured anodize", "vent_style": "small slots", "led_channels": True, "fillet_radius": 1, "wire_visibility": "exposed braided", "bezel_style": "rack faceplate", "enclosure_notes": "Add wood side cheeks, patch cable holders, rainbow LED accents"},
    "mixing_desk": {"name": "Mixing Desk", "description": "Studio console, charcoal, LED VU meter", "default_color": "#3b3b3b", "accent_color": "#ffd700", "screw_style": "hidden", "surface": "soft-touch", "vent_style": "slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "console strip", "enclosure_notes": "Add fader-slot decals, VU-meter window, channel label strip"},
    "broadcast": {"name": "Broadcast Studio", "description": "Cobalt blue, chrome, on-air light", "default_color": "#1f3a5f", "accent_color": "#e74c3c", "screw_style": "hidden", "surface": "smooth gloss", "vent_style": "fine slots", "led_channels": True, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "slim chrome", "enclosure_notes": "Add ON-AIR indicator, chrome trim, studio logo plate"},
    "snes_classic": {"name": "SNES Classic", "description": "US SNES gray with purple slider accents", "default_color": "#b8b8c0", "accent_color": "#7b5fa0", "screw_style": "exposed Phillips", "surface": "textured matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "rounded console", "enclosure_notes": "Add indented logo pad, slider lines, purple accent trim"},
    "famicom": {"name": "Famicom", "description": "Red/white/gold, cartridge slot vibe", "default_color": "#e3302a", "accent_color": "#d4af37", "screw_style": "exposed Phillips", "surface": "smooth gloss", "vent_style": "grid", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Add cartridge-slot cutout, gold trim, red eject detail"},
    "gameboy_gray": {"name": "Game Boy Classic", "description": "Off-white/gray with maroon red accents", "default_color": "#d0cfc4", "accent_color": "#8b0000", "screw_style": "exposed Phillips", "surface": "smooth", "vent_style": "none", "led_channels": False, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "thick rounded", "enclosure_notes": "Add recessed screen bezel, D-pad grooves, maroon accent bar"},
    "gameboy_pocket": {"name": "Game Boy Pocket", "description": "Gunmetal gray, red power LED", "default_color": "#6b6b6b", "accent_color": "#ff0000", "screw_style": "exposed Phillips", "surface": "smooth matte", "vent_style": "none", "led_channels": False, "fillet_radius": 7, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Tight handheld proportions, recessed screen, red LED dot"},
    "dreamcast": {"name": "Dreamcast", "description": "Ivory white with orange swirl window", "default_color": "#f0efe9", "accent_color": "#ff7f00", "screw_style": "exposed Phillips", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "rounded console", "enclosure_notes": "Add swirl logo window, controller-port notches, vent fan grill"},
    "ps1_gray": {"name": "PS1 Gray", "description": "Classic PlayStation gray, red/green/blue logo dots", "default_color": "#b5b5ad", "accent_color": "#e03a3e", "screw_style": "exposed Phillips", "surface": "textured matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "rounded slab", "enclosure_notes": "Add tri-color dots, controller port notches, gray vent ribs"},
    "ps2_black": {"name": "PS2 Slim", "description": "Glossy black with blue accent", "default_color": "#171717", "accent_color": "#3b6fe0", "screw_style": "hidden", "surface": "gloss piano", "vent_style": "fine slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "slim rounded", "enclosure_notes": "Gloss black top, matte base, slim clamshell profile"},
    "xbox_og": {"name": "Xbox Original", "description": "Green jewel, black, X motifs", "default_color": "#2b2b2b", "accent_color": "#7fc32b", "screw_style": "hidden", "surface": "textured matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "X top plate", "enclosure_notes": "Add green X jewel emblem, top-slot vents, controller cutouts"},
    "n64": {"name": "N64 Atomic", "description": "Translucent purple, atomic green", "default_color": "#7a3b6e", "accent_color": "#a8e06b", "screw_style": "exposed Phillips", "surface": "clear-coated translucent", "vent_style": "slots", "led_channels": False, "fillet_radius": 7, "wire_visibility": "partially exposed", "bezel_style": "rounded", "enclosure_notes": "Use translucent filament, show interior, atomic swirl decal"},
    "sega_genesis": {"name": "Sega Genesis", "description": "Black with red stripes and gold label", "default_color": "#1a1a1a", "accent_color": "#e01111", "screw_style": "exposed Phillips", "surface": "textured matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "angled slab", "enclosure_notes": "Add angled red stripe, gold cart label plate, cartridge slot"},
    "atari_wood": {"name": "Atari Woodgrain", "description": "Walnut woodgrain with black vents", "default_color": "#5a3d2b", "accent_color": "#e8a33d", "screw_style": "exposed Phillips", "surface": "woodgrain veneer", "vent_style": "horizontal ribs", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "wood frame", "enclosure_notes": "Add woodgrain side panels, rainbow strip decal, chunky switches"},
    "macintosh_84": {"name": "Macintosh 1984", "description": "Beige box with floppy slot, minimal", "default_color": "#d8cfbe", "accent_color": "#8a8a8a", "screw_style": "hidden", "surface": "smooth beige", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "thick rounded", "enclosure_notes": "Add floppy-slot cutout, subtle recess for logo, compact cube proportions"},
    "ibm_beige": {"name": "IBM 5150", "description": "IBM beige, blue PS/2 accents, expansion slots", "default_color": "#d6d3cd", "accent_color": "#1a3c8c", "screw_style": "exposed Phillips", "surface": "textured beige", "vent_style": "horizontal vents", "led_channels": False, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "square tower", "enclosure_notes": "Add floppy/drive bays, red LED, blue label block, expansion slot covers"},
    "commodore_64": {"name": "Commodore 64", "description": "Cream/chocolate with light brown keys", "default_color": "#e8e0cc", "accent_color": "#8a6a45", "screw_style": "exposed Phillips", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "rounded wedge", "enclosure_notes": "Add wedge profile, rainbow bar decal, cart slot on top"},
    "amiga_500": {"name": "Amiga 500", "description": "White wedge with beige keys and power LEDs", "default_color": "#f0ece0", "accent_color": "#d9534f", "screw_style": "exposed Phillips", "surface": "smooth matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "rounded wedge", "enclosure_notes": "Add wedge shape, side cartridge slot, LED bar"},
    "trs80": {"name": "TRS-80", "description": "Silver/black with red keyboard", "default_color": "#c0c0c0", "accent_color": "#a81c1c", "screw_style": "exposed Phillips", "surface": "brushed metal", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "chrome frame", "enclosure_notes": "Add brushed-metal panels, red key block, square display bezel"},
    "apple_iig": {"name": "Apple IIgs", "description": "Warm white with rainbow apple stripe", "default_color": "#eee8d8", "accent_color": "#7a4a9e", "screw_style": "exposed Phillips", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "rounded slab", "enclosure_notes": "Add rainbow stripe decal, flush front, soft rounded top"},
    "typewriter": {"name": "Vintage Typewriter", "description": "Olive green, cream keys, carriage return", "default_color": "#4a5d3a", "accent_color": "#e8dcc0", "screw_style": "exposed (chrome)", "surface": "wrinkle paint", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "partially exposed", "bezel_style": "chrome trim", "enclosure_notes": "Add carriage-return lever, round key decals, platen roller cutout"},
    "underwood": {"name": "Underwood Noir", "description": "Black typewriter with gold decals", "default_color": "#111111", "accent_color": "#d4af37", "screw_style": "exposed (chrome)", "surface": "wrinkle paint", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "chrome rim", "enclosure_notes": "Add gold leaf decals, round keys, recessed carriage"},
    "teletype": {"name": "Teletype Machine", "description": "Dark green/black, paper feed, loud keys", "default_color": "#263128", "accent_color": "#c8b88a", "screw_style": "exposed hex", "surface": "crinkle paint", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "heavy frame", "enclosure_notes": "Add paper-feed slot, brass plate, large round keys"},
    "punch_card": {"name": "Punch Card", "description": "Cream cards, printed grid, IBM vibe", "default_color": "#f4f0dc", "accent_color": "#2b3a67", "screw_style": "hidden", "surface": "cardstock textured", "vent_style": "none", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "square", "enclosure_notes": "Add punch-card grid emboss, tab cuts, printed columns"},
    "vt100": {"name": "VT100 Terminal", "description": "White/beige with amber phosphor screen", "default_color": "#d8d4c8", "accent_color": "#c8721a", "screw_style": "exposed Phillips", "surface": "smooth matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Add sloped terminal profile, recessed screen, function-key strip"},
    "dot_matrix": {"name": "Dot Matrix", "description": "Fabric gray with '80s office vibe", "default_color": "#9a9a9a", "accent_color": "#c0392b", "screw_style": "exposed Phillips", "surface": "textured", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "square", "enclosure_notes": "Add pin-feed wheels, tear bar, paper tray slot"},
    "trek_tng": {"name": "Star Trek TNG", "description": "Graphite gray, bronze panel, blue LCARS light", "default_color": "#3a3d42", "accent_color": "#66b3ff", "screw_style": "hidden", "surface": "smooth brushed", "vent_style": "slot", "led_channels": True, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "smooth curved", "enclosure_notes": "Add LCARS-style curved accent stripe, bronze grill, smooth organic curves"},
    "nostromo": {"name": "Nostromo", "description": "Dark industrial, hazard stripes, green CRT", "default_color": "#20201c", "accent_color": "#9acd32", "screw_style": "exposed hex", "surface": "rough cast", "vent_style": "cargo grills", "led_channels": False, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "industrial frame", "enclosure_notes": "Add hazard stripes, riveted plates, grimy finish"},
    "hal9000": {"name": "HAL 9000", "description": "Black monolith, red lens, white panels", "default_color": "#0d0d0d", "accent_color": "#e74c3c", "screw_style": "hidden", "surface": "gloss black", "vent_style": "none", "led_channels": True, "fillet_radius": 10, "wire_visibility": "hidden", "bezel_style": "seamless", "enclosure_notes": "Add central red lens window, white underpanel, seamless dark shell"},
    "cyberdyne": {"name": "Cyberdyne", "description": "Chrome/red, T-800 combat chrome", "default_color": "#8a8a8a", "accent_color": "#e60000", "screw_style": "exposed hex", "surface": "brushed metal", "vent_style": "angled slots", "led_channels": True, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "armored", "enclosure_notes": "Add red LED eye window, chrome finish, combat grip texture"},
    "tyrell": {"name": "Tyrell Corp", "description": "Art deco gold/black, empire style", "default_color": "#1a1008", "accent_color": "#c9a227", "screw_style": "hidden", "surface": "polished gold trim", "vent_style": "deco fan slits", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "deco frame", "enclosure_notes": "Add deco stepped layers, gold fan grill, pyramid accent"},
    "deus_ex": {"name": "Deus Ex", "description": "Brass/black dystopia, augments", "default_color": "#191512", "accent_color": "#c39b5c", "screw_style": "exposed hex", "surface": "leather and brass", "vent_style": "vault slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "riveted", "enclosure_notes": "Add brass rivets, leather panels, aug-slot cutouts, brass washers"},
    "ghost_shell": {"name": "Ghost in the Shell", "description": "Blue/grey tactical, clean military cyber", "default_color": "#2a3a45", "accent_color": "#7fd4ff", "screw_style": "hidden", "surface": "matte polymer", "vent_style": "tactical slots", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "thin tactical", "enclosure_notes": "Add clean panel lines, blue LED accents, minimal military markings"},
    "tachikoma": {"name": "Tachikoma", "description": "Teal/cream spider-mech, cute-industrial", "default_color": "#7fa8a9", "accent_color": "#f2e6c8", "screw_style": "exposed hex", "surface": "smooth", "vent_style": "round vents", "led_channels": True, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "bulbous", "enclosure_notes": "Add bulbous lens windows, cute segmented panels, cream accents"},
    "gundam": {"name": "Gundam RX-78", "description": "White/red/blue primary blocks, inner frame", "default_color": "#e8e8e8", "accent_color": "#cc0000", "screw_style": "hidden", "surface": "smooth gloss", "vent_style": "vent grills", "led_channels": False, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "armor plate", "enclosure_notes": "Add panel separations, inner-frame look, yellow power vents"},
    "eva_01": {"name": "EVA Unit-01", "description": "Purple/green biomech, sci-fi lab", "default_color": "#3a1f5c", "accent_color": "#7bd34c", "screw_style": "hidden", "surface": "gloss purple", "vent_style": "organic slits", "led_channels": True, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "organic frame", "enclosure_notes": "Add green accent ridges, tube details, shoulder-pod bumps"},
    "aperture": {"name": "Aperture Science", "description": "White panels with orange accents", "default_color": "#eae6da", "accent_color": "#ff7a00", "screw_style": "hidden", "surface": "gloss panel", "vent_style": "slots", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "panel seam", "enclosure_notes": "Add orange accent stripes, panel seams, companion-cube decal"},
    "half_life": {"name": "Half-Life Hazard", "description": "Orange/blue hazard suit colors", "default_color": "#f0a02c", "accent_color": "#1e5aa8", "screw_style": "exposed hex", "surface": "rubberized", "vent_style": "slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "armored", "enclosure_notes": "Add hazard suit piping, orange/blue panels, HEV decals"},
    "apollo": {"name": "Apollo Mission", "description": "Silver/white with American blue", "default_color": "#e5e5e5", "accent_color": "#24386b", "screw_style": "exposed (torx)", "surface": "brushed metal", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "thin rounded", "enclosure_notes": "Add mission patch decal, American flag accent, seam lines"},
    "forest_camo": {"name": "Forest Camouflage", "description": "Multi-tone green camo", "default_color": "#4a5d3a", "accent_color": "#2b3a22", "screw_style": "exposed", "surface": "textured matte", "vent_style": "slot", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "minimal", "enclosure_notes": "Use camo-pattern hydrodip or paint, non-reflective finish"},
    "desert_storm": {"name": "Desert Storm", "description": "Tan/sand with brown accents", "default_color": "#b8a270", "accent_color": "#5c4a2e", "screw_style": "exposed hex", "surface": "sand textured", "vent_style": "louvered", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "rugged", "enclosure_notes": "Add sand texture, heat vents, carry-handle mounts"},
    "alpine_snow": {"name": "Alpine Snow", "description": "White with glacier blue", "default_color": "#f4f6f5", "accent_color": "#5aa9e6", "screw_style": "hidden", "surface": "smooth", "vent_style": "slits", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "slim", "enclosure_notes": "Clean white panels, ice-blue accent ring, frosted texture"},
    "jungle_viper": {"name": "Jungle Viper", "description": "Deep jungle green with yellow stripe", "default_color": "#223322", "accent_color": "#c8a800", "screw_style": "exposed", "surface": "textured", "vent_style": "slot", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "rugged", "enclosure_notes": "Add yellow hazard stripe, rubber grip panels, sealed seams"},
    "deep_ocean": {"name": "Deep Ocean", "description": "Midnight blue with teal glow", "default_color": "#0d1f38", "accent_color": "#00c8a0", "screw_style": "exposed hex", "surface": "smooth gloss", "vent_style": "gills", "led_channels": True, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "sleek", "enclosure_notes": "Add teal underglow, gill vents, glossy finish"},
    "volcanic": {"name": "Volcanic Ash", "description": "Charcoal with ember orange", "default_color": "#26221f", "accent_color": "#ff5a1f", "screw_style": "exposed", "surface": "rough texture", "vent_style": "cracked slots", "led_channels": True, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "rugged", "enclosure_notes": "Add ember glow, cracked vent lines, dark soot finish"},
    "arctic_whiteout": {"name": "Arctic Whiteout", "description": "All-white storm camo", "default_color": "#e8ecef", "accent_color": "#b0c4de", "screw_style": "hidden", "surface": "smooth", "vent_style": "slits", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "slim", "enclosure_notes": "Whiteout finish, faint blue shading, minimal markings"},
    "wasteland": {"name": "Wasteland Rust", "description": "Rust orange, corroded, post-apoc", "default_color": "#6e3a23", "accent_color": "#b5541e", "screw_style": "exposed (rusty)", "surface": "rusted texture", "vent_style": "jagged", "led_channels": False, "fillet_radius": 0, "wire_visibility": "exposed", "bezel_style": "rough", "enclosure_notes": "Add rust streaks, paint chips, corroded metal texture"},
    "redrock": {"name": "Canyon Redrock", "description": "Sedona red with tan", "default_color": "#7a2e1d", "accent_color": "#d2a679", "screw_style": "exposed", "surface": "rock textured", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "natural", "enclosure_notes": "Add layered rock strata texture, natural canyon palette"},
    "boreal": {"name": "Boreal Forest", "description": "Pine green with birch white", "default_color": "#2b4a2f", "accent_color": "#d9d2c0", "screw_style": "hidden", "surface": "wood-grain", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "wood frame", "enclosure_notes": "Add birch veneer panels, pine-green shell, nature blend"},
    "denim": {"name": "Japanese Denim", "description": "Indigo denim with sashiko stitching", "default_color": "#2a3a5e", "accent_color": "#c8a951", "screw_style": "hidden", "surface": "denim fabric", "vent_style": "stitched slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "fabric-wrapped", "enclosure_notes": "Add denim wrap panels, visible stitching, brass rivets"},
    "samurai": {"name": "Samurai", "description": "Lacquer black with gold and red", "default_color": "#101010", "accent_color": "#c9a227", "screw_style": "exposed brass", "surface": "lacquer gloss", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "muneate frame", "enclosure_notes": "Add lacquer finish, gold crest decal, red accent cord wrap"},
    "geisha": {"name": "Geisha Silk", "description": "Cherry blossom pink, silk kimono", "default_color": "#f0d4d4", "accent_color": "#c94f7c", "screw_style": "hidden", "surface": "silk-like sheen", "vent_style": "petal cut-outs", "led_channels": False, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "soft curved", "enclosure_notes": "Add cherry blossom inlay, silk cord, gold Obi belt accent"},
    "celtic": {"name": "Celtic Bronze", "description": "Bronze with knotwork", "default_color": "#8c5a2b", "accent_color": "#3a6b35", "screw_style": "exposed", "surface": "hammered metal", "vent_style": "knot perforations", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "engraved", "enclosure_notes": "Add celtic knot engravings, green enamel accents, hammered texture"},
    "norse": {"name": "Norse Runes", "description": "Ashen gray with iron runes", "default_color": "#3a3f44", "accent_color": "#b0b7bd", "screw_style": "exposed rivets", "surface": "iron texture", "vent_style": "rune slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "wrought iron", "enclosure_notes": "Add rune engravings, iron rivets, weathered metal"},
    "egyptian": {"name": "Egyptian Gold", "description": "Sandstone with gold and lapis", "default_color": "#d8c08a", "accent_color": "#23408c", "screw_style": "exposed brass", "surface": "hieroglyph texture", "vent_style": "scarab vents", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "cartouche frame", "enclosure_notes": "Add gold leaf accents, hieroglyph relief, lapis inlay"},
    "greek": {"name": "Greek Marble", "description": "White marble with gold leaf", "default_color": "#e8e6df", "accent_color": "#c9a227", "screw_style": "exposed bronze", "surface": "marble texture", "vent_style": "column slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "laurel frame", "enclosure_notes": "Add marble veining, gold laurel trim, column fluting"},
    "aztec": {"name": "Aztec Obsidian", "description": "Obsidian black with turquoise and red", "default_color": "#101014", "accent_color": "#2eb6a0", "screw_style": "exposed", "surface": "obsidian gloss", "vent_style": "zigzag slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "stepped frame", "enclosure_notes": "Add stepped pyramid geometry, turquoise inlay, zigzag trim"},
    "art_deco": {"name": "Art Deco", "description": "Black/gold/green deco", "default_color": "#0e0e10", "accent_color": "#d4af37", "screw_style": "hidden", "surface": "lacquered", "vent_style": "fan slits", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "sunburst", "enclosure_notes": "Add sunburst grills, deco stepped layers, gold pinstripes"},
    "bauhaus": {"name": "Bauhaus", "description": "Red/yellow/blue primaries on white", "default_color": "#f2f2f0", "accent_color": "#e03a3e", "screw_style": "hidden", "surface": "smooth", "vent_style": "circle holes", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "clean geometric", "enclosure_notes": "Add geometric color blocks, circle vents, functional simplicity"},
    "pop_art": {"name": "Pop Art", "description": "Halftone dots, bold primaries", "default_color": "#f5d000", "accent_color": "#1d3fd6", "screw_style": "hidden", "surface": "glossy", "vent_style": "halftone holes", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "comic frame", "enclosure_notes": "Add halftone patterns, comic burst shapes, bold color blocks"},
    "manga": {"name": "Manga Neon", "description": "Black with neon pink screen tones", "default_color": "#141414", "accent_color": "#ff2fa0", "screw_style": "hidden", "surface": "smooth", "vent_style": "speed-line slits", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "panel frame", "enclosure_notes": "Add speed-line accents, halftone decals, neon pink LEDs"},
    "kawaii": {"name": "Kawaii Pastel", "description": "Pastel pink with adorable decals", "default_color": "#ffd6e8", "accent_color": "#ff8ab5", "screw_style": "hidden", "surface": "soft matte", "vent_style": "heart cut-outs", "led_channels": False, "fillet_radius": 10, "wire_visibility": "hidden", "bezel_style": "rounded soft", "enclosure_notes": "Add heart vents, cute face decals, pastel palette, plush corners"},
    "y2k_chrome": {"name": "Y2K Chrome", "description": "Liquid chrome with iridescence", "default_color": "#a8b0b8", "accent_color": "#e0c8ff", "screw_style": "hidden", "surface": "chrome gloss", "vent_style": "bubble slots", "led_channels": True, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "blob frame", "enclosure_notes": "Add iridescent sheen, chrome liquid shapes, inflatable blobs"},
    "cyberramen": {"name": "Cyber Ramen", "description": "Bowl tones with neon toppings", "default_color": "#2a2410", "accent_color": "#ff5a1f", "screw_style": "exposed", "surface": "matte", "vent_style": "noodle swirl", "led_channels": True, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "bowl rim", "enclosure_notes": "Add noodle-swirl vents, egg decal, steam-slit grills"},
    "soda_red": {"name": "Soda Pop Red", "description": "Cola red with cream foam", "default_color": "#a32c2c", "accent_color": "#f2e8c8", "screw_style": "hidden", "surface": "gloss", "vent_style": "bubble holes", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "curvy", "enclosure_notes": "Add cream foam wave, bubble holes, retro soda decal"},
    "menthol": {"name": "Menthol Green", "description": "Mint green with white swirl", "default_color": "#9adbc0", "accent_color": "#f4f6f5", "screw_style": "hidden", "surface": "smooth", "vent_style": "swirl slots", "led_channels": False, "fillet_radius": 7, "wire_visibility": "hidden", "bezel_style": "soft", "enclosure_notes": "Add white swirl pattern, mint gloss, clean cooling vibe"},
    "cotton_candy": {"name": "Cotton Candy", "description": "Blue/pink clouds", "default_color": "#a8d8f0", "accent_color": "#f0a8c8", "screw_style": "hidden", "surface": "soft", "vent_style": "cloud cut-outs", "led_channels": False, "fillet_radius": 9, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Add cloud-shaped vents, soft pastel gradient"},
    "chocolate": {"name": "Chocolate Swirl", "description": "Mocha with cream swirl", "default_color": "#5a3a22", "accent_color": "#e8d8c0", "screw_style": "hidden", "surface": "matte", "vent_style": "swirl slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Add swirl marble pattern, warm brown tones"},
    "wasabi": {"name": "Wasabi Green", "description": "Pale green with darker green", "default_color": "#a8c08a", "accent_color": "#3a5a2a", "screw_style": "exposed", "surface": "textured", "vent_style": "leaf slits", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "natural", "enclosure_notes": "Add leaf-vein texture, fresh green palette"},
    "bubblegum": {"name": "Bubblegum", "description": "Bright pink with white dots", "default_color": "#ff88b0", "accent_color": "#f4f4f4", "screw_style": "hidden", "surface": "gloss", "vent_style": "dot holes", "led_channels": False, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "candy", "enclosure_notes": "Add white polka dots, candy-gloss finish"},
    "sunset": {"name": "Sunset Orange", "description": "Gradient orange to purple", "default_color": "#ff7a2a", "accent_color": "#8a2abf", "screw_style": "hidden", "surface": "gradient gloss", "vent_style": "wave slits", "led_channels": True, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "smooth", "enclosure_notes": "Add sunset gradient paint, wave patterns, warm LEDs"},
    "electric_violet": {"name": "Electric Violet", "description": "Deep purple with UV glow", "default_color": "#2a1040", "accent_color": "#a04cff", "screw_style": "hidden", "surface": "smooth", "vent_style": "slits", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "sleek", "enclosure_notes": "Add UV-reactive accents, violet underglow, blacklight colors"},
    "acid_green": {"name": "Acid Green", "description": "Lime on black, radioactive", "default_color": "#0a0a0a", "accent_color": "#ccff00", "screw_style": "exposed", "surface": "matte", "vent_style": "biohazard slots", "led_channels": True, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "angular", "enclosure_notes": "Add biohazard decal, lime accents, hazard grill"},
    "baby_blue": {"name": "Baby Blue", "description": "Soft blue with white", "default_color": "#b8d8f0", "accent_color": "#f4f8fc", "screw_style": "hidden", "surface": "soft", "vent_style": "cloud holes", "led_channels": False, "fillet_radius": 8, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Soft pastel blue, cloud cut-outs, gentle palette"},
    "coral_reef": {"name": "Coral Reef", "description": "Coral pink with teal", "default_color": "#ff7f6e", "accent_color": "#2aa8a0", "screw_style": "hidden", "surface": "gloss", "vent_style": "fish-scale", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "organic", "enclosure_notes": "Add fish-scale texture, coral/teal palette, reef pattern"},
    "gunmetal": {"name": "Gunmetal Gradient", "description": "Dark gunmetal with copper fade", "default_color": "#2e3236", "accent_color": "#b87333", "screw_style": "exposed hex", "surface": "brushed", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "sleek", "enclosure_notes": "Add brushed metal, copper accents, subtle gradient"},
    "rose_gold": {"name": "Rose Gold", "description": "Blush metal with white", "default_color": "#d8a08a", "accent_color": "#f4f0ea", "screw_style": "hidden", "surface": "metallic sheen", "vent_style": "slits", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "slim metallic", "enclosure_notes": "Add rose-gold metallic paint, white trim, premium feel"},
    "titanium": {"name": "Titanium Brushed", "description": "Titanium gray with brushed finish", "default_color": "#8a8f94", "accent_color": "#c0c5ca", "screw_style": "exposed (torx)", "surface": "brushed titanium", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "machined", "enclosure_notes": "Add CNC brushed finish, chamfered edges, machined bezel"},
    "gold_luxe": {"name": "Gold Luxe", "description": "Metallic gold with black", "default_color": "#d4af37", "accent_color": "#1a1a1a", "screw_style": "hidden", "surface": "metallic gloss", "vent_style": "deco slits", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "gold frame", "enclosure_notes": "Add metallic gold paint, black trim, luxe deco lines"},
    "panda": {"name": "Panda Matte", "description": "White shell with black accents", "default_color": "#f0f0f0", "accent_color": "#1a1a1a", "screw_style": "hidden", "surface": "matte", "vent_style": "black slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "two-tone", "enclosure_notes": "Two-tone panda scheme, matte finish, black trim panels"},
    "vaporwave": {"name": "Vaporwave", "description": "Pink/cyan grid, palm trees, 80s", "default_color": "#ff71ce", "accent_color": "#01cdfe", "screw_style": "hidden", "surface": "gloss", "vent_style": "grid slits", "led_channels": True, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "retro sun", "enclosure_notes": "Add sun-grid decal, pastel gradient, palm silhouette accents"},
    "synthwave": {"name": "Synthwave Outrun", "description": "Purple/cyan, sun horizon, chrome grid", "default_color": "#2a0845", "accent_color": "#00f5ff", "screw_style": "hidden", "surface": "smooth", "vent_style": "grid slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "retro", "enclosure_notes": "Add grid floor decal, sun horizon line, neon glow channels"},
    "gruvbox": {"name": "Gruvbox Dev", "description": "Warm retro dev palette", "default_color": "#282828", "accent_color": "#fabd2f", "screw_style": "hidden", "surface": "matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "clean", "enclosure_notes": "Add gruvbox accent bar, warm neutrals, code-themed decals"},
    "nord": {"name": "Nord Dark", "description": "Polar night blue with frost", "default_color": "#2e3440", "accent_color": "#88c0d0", "screw_style": "hidden", "surface": "matte", "vent_style": "slots", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "slim", "enclosure_notes": "Add frost-blue LEDs, arctic palette, clean lines"},
    "material": {"name": "Material Design", "description": "Google material colors, elevation", "default_color": "#fafafa", "accent_color": "#1e88e5", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "elevated", "enclosure_notes": "Add card elevations, primary-color accents, drop shadows"},
    "glass": {"name": "Glassmorphism", "description": "Frosted glass, blur, translucency", "default_color": "#dbe7f0", "accent_color": "#ffffff", "screw_style": "hidden", "surface": "frosted glass", "vent_style": "none", "led_channels": True, "fillet_radius": 8, "wire_visibility": "partially exposed", "bezel_style": "frosted rim", "enclosure_notes": "Use translucent panels, show interior glow, frosted diffuser"},
    "flat": {"name": "Flat Design", "description": "Solid colors, no gradients", "default_color": "#2c3e50", "accent_color": "#e74c3c", "screw_style": "hidden", "surface": "solid", "vent_style": "solid slots", "led_channels": False, "fillet_radius": 0, "wire_visibility": "hidden", "bezel_style": "flat", "enclosure_notes": "Flat color blocks, no gradients or shadows, solid palette"},
    "neo_brutalist": {"name": "Neo-Brutalist", "description": "High-contrast borders, blocky", "default_color": "#f0f0f0", "accent_color": "#e11d48", "screw_style": "exposed", "surface": "solid", "vent_style": "blocky slots", "led_channels": False, "fillet_radius": 0, "wire_visibility": "exposed", "bezel_style": "thick border", "enclosure_notes": "Thick black outlines, hard shadows, blocky type, pop colors"},
    "goblin": {"name": "Goblincore", "description": "Moss, mud, acorns, shrooms", "default_color": "#4a6b3a", "accent_color": "#8a6a4a", "screw_style": "exposed", "surface": "moss textured", "vent_style": "organic holes", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "twig frame", "enclosure_notes": "Add mushroom decals, twig trims, earthy cluttered vibe"},
    "cottagecore": {"name": "Cottagecore", "description": "Floral, cream, wood", "default_color": "#f2ead8", "accent_color": "#7a6a4a", "screw_style": "hidden", "surface": "fabric", "vent_style": "floral holes", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "floral frame", "enclosure_notes": "Add floral fabric panels, wood trim, lace edges"},
    "wabi_sabi": {"name": "Wabi-Sabi", "description": "Imperfect, natural, muted", "default_color": "#b8a892", "accent_color": "#6a5a4a", "screw_style": "exposed", "surface": "unfinished", "vent_style": "rough slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "partially exposed", "bezel_style": "rough", "enclosure_notes": "Embrace imperfections, natural texture, muted earth palette"},
    "maximalist": {"name": "Maximalist", "description": "Everything everywhere, loud", "default_color": "#e03a3e", "accent_color": "#1d3fd6", "screw_style": "exposed", "surface": "busy pattern", "vent_style": "mixed", "led_channels": True, "fillet_radius": 3, "wire_visibility": "exposed", "bezel_style": "busy", "enclosure_notes": "Mix patterns, colors, stickers, lights — more is more"},
    "night_ops": {"name": "Night Ops", "description": "No visible light, red preservation", "default_color": "#0f0f0f", "accent_color": "#8a0303", "screw_style": "exposed hex", "surface": "anti-glare matte", "vent_style": "stealth slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "minimal", "enclosure_notes": "Zero white LEDs, red-only accents, matte anti-glare, velcro battery"},
    "medkit": {"name": "Medkit Cross", "description": "White with red cross", "default_color": "#e8e8e8", "accent_color": "#c0392b", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Add red cross emblem, white shell, medical-label decals"},
    "firewatch": {"name": "Firewatch", "description": "National park orange/red", "default_color": "#b8402a", "accent_color": "#e06a2a", "screw_style": "exposed", "surface": "matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "ranger", "enclosure_notes": "Add park-service decal, pine silhouette, firetower vibe"},
    "rescue_orange": {"name": "Search & Rescue", "description": "High-vis orange with reflective", "default_color": "#ff7a00", "accent_color": "#e8e8e8", "screw_style": "exposed", "surface": "safety texture", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "rugged", "enclosure_notes": "Add reflective strips, high-vis orange, grab handles"},
    "dive": {"name": "Diver Anodized", "description": "Deep anodized blue with accents", "default_color": "#0a3a5a", "accent_color": "#00c8c8", "screw_style": "exposed hex", "surface": "anodized", "vent_style": "gills", "led_channels": True, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "sealed", "enclosure_notes": "Add anodized finish, dive light accents, o-ring channels"},
    "hazmat": {"name": "Hazmat Yellow", "description": "Radiation yellow with black", "default_color": "#d8b800", "accent_color": "#1a1a1a", "screw_style": "exposed", "surface": "smooth", "vent_style": "hazard slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "hazard", "enclosure_notes": "Add biohazard/radiation decals, black hazard stripes, yellow shell"},
    "high_vis": {"name": "High-Vis Worker", "description": "Safety green with reflective", "default_color": "#c8e02a", "accent_color": "#1a1a1a", "screw_style": "exposed", "surface": "safety texture", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "rugged", "enclosure_notes": "Add hi-vis stripes, reflective tape, hard-hat durable finish"},
    "carbon": {"name": "Carbon Fiber", "description": "Real carbon pattern", "default_color": "#1a1a1a", "accent_color": "#e03030", "screw_style": "exposed hex", "surface": "carbon fiber texture", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "carbon", "enclosure_notes": "Add real/printed carbon weave, red pinstripe, weight-save cutouts"},
    "walnut": {"name": "Walnut Veneer", "description": "Real walnut wood", "default_color": "#5a3a22", "accent_color": "#d4af37", "screw_style": "exposed brass", "surface": "walnut veneer", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "wood frame", "enclosure_notes": "Add walnut veneer, brass accents, oiled finish"},
    "piano_black": {"name": "Piano Black", "description": "Gloss lacquer black", "default_color": "#0a0a0a", "accent_color": "#8a8a8a", "screw_style": "hidden", "surface": "piano gloss", "vent_style": "none", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "gloss frame", "enclosure_notes": "High-gloss lacquer, mirror-like finish, keepsake quality"},
    "crystal_ice": {"name": "Crystal Ice", "description": "Frosted white with blue ice", "default_color": "#e8f4f8", "accent_color": "#7fd4ff", "screw_style": "hidden", "surface": "frosted", "vent_style": "ice cracks", "led_channels": True, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "ice rim", "enclosure_notes": "Add ice-crack patterns, frosted panels, glacier blue LEDs"},
    "sapphire": {"name": "Sapphire Blue", "description": "Deep blue with silver", "default_color": "#1a3a8a", "accent_color": "#d8d8e0", "screw_style": "hidden", "surface": "metallic sheen", "vent_style": "slots", "led_channels": True, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "silver rim", "enclosure_notes": "Add sapphire metallic paint, silver trim, jewel accents"},
    "emerald": {"name": "Emerald Velvet", "description": "Rich green velvet", "default_color": "#0a4a2a", "accent_color": "#d4af37", "screw_style": "hidden", "surface": "velvet", "vent_style": "slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "gold rim", "enclosure_notes": "Add velvet panels, gold trim, jewelry-box presentation"},
    "champagne": {"name": "Champagne Creme", "description": "Cream champagne with gold", "default_color": "#f2e4c8", "accent_color": "#c9a227", "screw_style": "hidden", "surface": "satin", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "satin rim", "enclosure_notes": "Satin cream finish, champagne shimmer, gold accents"},
    "wizard": {"name": "Wizard Tower", "description": "Dark purple with runes", "default_color": "#2a1a3a", "accent_color": "#a04cff", "screw_style": "exposed brass", "surface": "arcane texture", "vent_style": "rune slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "arcane frame", "enclosure_notes": "Add glowing runes, arcane circles, purple glow channels"},
    "cybermonk": {"name": "Cyber Monk", "description": "Minimal monk robes, tech altar", "default_color": "#3a3028", "accent_color": "#d4af37", "screw_style": "hidden", "surface": "fabric", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "simple", "enclosure_notes": "Add fabric wraps, brass bell accent, simple zen geometry"},
    "captain": {"name": "Starship Captain", "description": "Brass and navy, command chair", "default_color": "#1a2a4a", "accent_color": "#d4af37", "screw_style": "hidden", "surface": "leather", "vent_style": "slot", "led_channels": True, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "command frame", "enclosure_notes": "Add brass trim, navy leather, captain's insignia decal"},
    "private_eye": {"name": "Private Eye", "description": "Noir tan, film grain, office", "default_color": "#6a5a3a", "accent_color": "#8a8a8a", "screw_style": "exposed", "surface": "venetian blind texture", "vent_style": "blinds", "led_channels": False, "fillet_radius": 2, "wire_visibility": "partially exposed", "bezel_style": "desk frame", "enclosure_notes": "Add venetian blind shadow decal, desk lamp glow accents"},
    "outlaw_biker": {"name": "Outlaw Biker", "description": "Black leather, studs, flame", "default_color": "#141414", "accent_color": "#b8402a", "screw_style": "exposed studs", "surface": "leather", "vent_style": "flame slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "partially exposed", "bezel_style": "studded", "enclosure_notes": "Add leather panels, metal studs, flame decals, chains"},
    "spy": {"name": "Luxury Spy", "description": "Midnight black, gold accents", "default_color": "#0a0a0a", "accent_color": "#c9a227", "screw_style": "hidden", "surface": "soft-touch", "vent_style": "none", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "sleek", "enclosure_notes": "Add gold accents, soft-touch finish, discrete aesthetics"},
    "pirate": {"name": "Pirate Captain", "description": "Worn teak with brass", "default_color": "#5a3a22", "accent_color": "#b8860b", "screw_style": "exposed rivets", "surface": "worn teak", "vent_style": "cannon slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "partially exposed", "bezel_style": "worn frame", "enclosure_notes": "Add brass fittings, worn wood, rope details, skull accent"},
    "explorer": {"name": "Jungle Explorer", "description": "Khaki and brass, expedition", "default_color": "#b8a270", "accent_color": "#6a5a3a", "screw_style": "exposed brass", "surface": "canvas", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "expedition", "enclosure_notes": "Add canvas wrap, brass buckles, compass decal"},
    "vhs": {"name": "VHS Snap", "description": "Black with color-block label", "default_color": "#1a1a1a", "accent_color": "#e03a3e", "screw_style": "exposed", "surface": "matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "label strip", "enclosure_notes": "Add VHS label block, video-gauge decal, plastic snap texture"},
    "floppy": {"name": "Floppy Disk", "description": "Gray floppy with label", "default_color": "#b8b8b8", "accent_color": "#2a3a8a", "screw_style": "exposed", "surface": "textured", "vent_style": "slots", "led_channels": False, "fillet_radius": 1, "wire_visibility": "hidden", "bezel_style": "floppy frame", "enclosure_notes": "Add write-protect tab, label window, sliding shutter detail"},
    "phosphor": {"name": "Green Phosphor", "description": "CRT green screen", "default_color": "#0a1a0a", "accent_color": "#33ff33", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "CRT frame", "enclosure_notes": "Add phosphor green, scanline decals, CRT curve bezel"},
    "amber": {"name": "Amber Terminal", "description": "Vintage amber CRT", "default_color": "#1a120a", "accent_color": "#ff8c00", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "CRT frame", "enclosure_notes": "Amber phosphor accents, CRT curve, warm glow"},
    "oled_black": {"name": "OLED Pure Black", "description": "True black with white", "default_color": "#000000", "accent_color": "#ffffff", "screw_style": "hidden", "surface": "matte black", "vent_style": "none", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "slim", "enclosure_notes": "True black panels, white text accents, minimal bezel"},
    "polaroid": {"name": "Polaroid White", "description": "White with colored strip", "default_color": "#f2f2f2", "accent_color": "#2a6a8a", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "photo frame", "enclosure_notes": "Add polaroid bottom bar, photo-frame bezel, retro white"},
    "film_noir": {"name": "Film Noir", "description": "Monochrome with red", "default_color": "#1a1a1a", "accent_color": "#8a0000", "screw_style": "hidden", "surface": "matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "cinematic", "enclosure_notes": "B&W palette, deep red accents, film-grain texture"},
    "club": {"name": "Techno Club", "description": "UV-reactive with strobes", "default_color": "#0a0a14", "accent_color": "#ff00ff", "screw_style": "hidden", "surface": "UV-reactive", "vent_style": "slots", "led_channels": True, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "sleek", "enclosure_notes": "UV-reactive paint, RGB LED strips, rave-ready"},
    "coffee": {"name": "Coffee Shop", "description": "Espresso and cream", "default_color": "#3a2a1a", "accent_color": "#d8c8a8", "screw_style": "exposed", "surface": "leather", "vent_style": "steam slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "cafe", "enclosure_notes": "Add espresso brown, cream accents, leather strap"},
    "hospital": {"name": "Hospital Sterile", "description": "White and light blue", "default_color": "#f4f6f8", "accent_color": "#5aa9e6", "screw_style": "hidden", "surface": "smooth", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "clean", "enclosure_notes": "Sterile white, medical blue accents, cleanable finish"},
    "pinstripe": {"name": "Mafia Pinstripe", "description": "Charcoal pinstripes, gold", "default_color": "#2a2a2e", "accent_color": "#c9a227", "screw_style": "exposed", "surface": "pinstripe", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "sharp", "enclosure_notes": "Add pinstripe lines, fedora-worthy, brass button accents"},
    "oceanic_dark": {"name": "Oceanic Dark", "description": "Abyssal blue, bioluminescent", "default_color": "#0a1a2a", "accent_color": "#00c8ff", "screw_style": "hidden", "surface": "gloss", "vent_style": "biolum holes", "led_channels": True, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "organic", "enclosure_notes": "Add bioluminescent dots, deep abyss blue, glow accents"},
    "grape_crush": {"name": "Grape Crush", "description": "Deep purple candy gloss", "default_color": "#3a1a5a", "accent_color": "#ff6ad5", "screw_style": "hidden", "surface": "candy gloss", "vent_style": "slots", "led_channels": True, "fillet_radius": 7, "wire_visibility": "hidden", "bezel_style": "rounded", "enclosure_notes": "Candy-purple gloss, hot-pink LED accents, retro candy vibe"},
    "lime_radio": {"name": "Lime Radio", "description": "Walkie-talkie yellow-green", "default_color": "#b8d83a", "accent_color": "#1a1a1a", "screw_style": "exposed", "surface": "tactical rubber", "vent_style": "speaker grill", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "radio frame", "enclosure_notes": "Add speaker grill, rubber overmold, PTT-button decal"},
    "salmon_drift": {"name": "Salmon Drift", "description": "Warm salmon and wood", "default_color": "#e8887a", "accent_color": "#5a3a22", "screw_style": "hidden", "surface": "matte", "vent_style": "wood slits", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "warm", "enclosure_notes": "Warm salmon shell, wood inlay, drift aesthetic"},
    "midnight_smoke": {"name": "Midnight Smoke", "description": "Smoky gray gradient", "default_color": "#1a1c1e", "accent_color": "#6a7a8a", "screw_style": "hidden", "surface": "smoked gloss", "vent_style": "slits", "led_channels": False, "fillet_radius": 4, "wire_visibility": "hidden", "bezel_style": "smoked", "enclosure_notes": "Smoked translucent gloss, fog gradient, moody finish"},
    "candy_apple": {"name": "Candy Apple Red", "description": "Deep translucent red gloss", "default_color": "#8a1010", "accent_color": "#e0a000", "screw_style": "hidden", "surface": "candy gloss", "vent_style": "slots", "led_channels": False, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "gloss", "enclosure_notes": "Candy-apple deep red, gold flake, showroom shine"},
    "glacier_teal": {"name": "Glacier Teal", "description": "Teal with white ice", "default_color": "#1a8a8a", "accent_color": "#e8f8f8", "screw_style": "hidden", "surface": "gloss", "vent_style": "ice slots", "led_channels": True, "fillet_radius": 6, "wire_visibility": "hidden", "bezel_style": "clean", "enclosure_notes": "Teal glacier gloss, white ice accents, crisp finish"},
    "sakura": {"name": "Sakura Bloom", "description": "Petal pink gradient", "default_color": "#ffd8e8", "accent_color": "#ff6a9a", "screw_style": "hidden", "surface": "pearl gloss", "vent_style": "petal holes", "led_channels": False, "fillet_radius": 9, "wire_visibility": "hidden", "bezel_style": "soft", "enclosure_notes": "Pearl pink gloss, petal cut-outs, spring palette"},
    "steel_blue": {"name": "Steel Blue", "description": "Blue steel industrial", "default_color": "#3a5a7a", "accent_color": "#e8e8e8", "screw_style": "exposed hex", "surface": "brushed steel", "vent_style": "slots", "led_channels": False, "fillet_radius": 2, "wire_visibility": "hidden", "bezel_style": "machined", "enclosure_notes": "Brushed steel blue, machined edges, industrial clean"},
    "sandstone": {"name": "Sandstone Desert", "description": "Sandstone with sage", "default_color": "#d8c8a8", "accent_color": "#7a8a6a", "screw_style": "exposed", "surface": "stone textured", "vent_style": "slots", "led_channels": False, "fillet_radius": 3, "wire_visibility": "hidden", "bezel_style": "natural", "enclosure_notes": "Sandstone texture, sage accents, desert minimal"},
    "venom": {"name": "Venom Symbiote", "description": "Black with white web veins", "default_color": "#0d0d0f", "accent_color": "#ffffff", "screw_style": "hidden", "surface": "gloss black", "vent_style": "web slots", "led_channels": False, "fillet_radius": 5, "wire_visibility": "hidden", "bezel_style": "organic", "enclosure_notes": "Add white web-vein accents, gloss black, menacing curves"},
    "mint_fresh": {"name": "Mint Fresh", "description": "Clean mint white", "default_color": "#d8f2e8", "accent_color": "#2aa878", "screw_style": "hidden", "surface": "matte", "vent_style": "slots", "led_channels": False, "fillet_radius": 7, "wire_visibility": "hidden", "bezel_style": "clean", "enclosure_notes": "Mint shell, fresh white accents, spa-clean vibe"},
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
    "esp32_p4": {"name": "ESP32-P4 (Espressif)", "cpu": "Dual-core RISC-V @ 400MHz", "isa": "RISC-V", "ram": "520KB SRAM + 32MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "USB OTG, MIPI CSI/DSI, Ethernet MAC", "gpio": "54-pin GPIO", "video_output": "MIPI DSI + RGB LCD", "price": 5, "power_draw": "3.3V/200mA", "form_factor": "25mm x 20mm (module)", "pros": ["Dual MIPI cameras", "MIPI display", "USB HS", "H.264 encoder", "Ultra cheap"], "cons": ["No WiFi/BT native", "MCU not Linux", "Limited RAM"], "best_for": ["maker", "conversation", "drone"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "MIPI DSI up to 1080p", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "MIPI CSI/DSI, USB OTG", "power_consumption_w": 0.5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "m5stack_cardputer_adv": {"name": "M5Stack Cardputer ADV (ESP32-S3)", "cpu": "ESP32-S3 Dual-core @ 240MHz", "isa": "XTensa LX7", "ram": "512KB SRAM + 8MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi, BLE 5.0, USB-C", "gpio": "Internal GPIO", "video_output": "1.14\" TFT (135x240)", "price": 25, "power_draw": "3.7V/150mA", "form_factor": "Credit-card size (85mm x 54mm)", "pros": ["Ultra portable", "Built-in keyboard", "TFT display", "IR transceiver", "RTC battery"], "cons": ["Tiny screen", "MCU not Linux", "Limited RAM"], "best_for": ["conversation", "maker", "security"], "compatibility": ["ALL"], "display_type": "TFT", "screen_size_inches": 1.14, "resolution": "135x240", "refresh_rate_hz": 60, "brightness_nits": 300, "interface": "SPI TFT", "power_consumption_w": 0.4, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "radxa_rock_5a": {"name": "Radxa ROCK 5A (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 100, "power_draw": "5V/4A USB-C", "form_factor": "100mm x 75mm", "pros": ["RK3588S flagship", "NVMe native", "2.5GbE", "M.2 E-key WiFi"], "cons": ["More expensive than competitors", "Active cooling needed"], "best_for": ["ai", "coding", "security", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "orange_pi_5_max": {"name": "Orange Pi 5 Max (RK3588)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB/32GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + 2x NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP + eDP", "price": 120, "power_draw": "5V/5A USB-C", "form_factor": "110mm x 80mm", "pros": ["Full RK3588", "32GB RAM option", "2x NVMe", "Triple display"], "cons": ["Large form factor", "Expensive", "Active cooling needed"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, eDP", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "orange_pi_5_pro": {"name": "Orange Pi 5 Pro (RK3588S)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, GbE, USB 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 85, "power_draw": "5V/4A USB-C", "form_factor": "90mm x 62mm", "pros": ["Affordable RK3588S", "NVMe native", "Good community support"], "cons": ["GbE only (not 2.5GbE)", "Active cooling needed"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "pi_cm0": {"name": "Raspberry Pi CM0 (Compute Module 0)", "cpu": "BCM2710 Cortex-A53 (quad-core)", "ram": "512MB LPDDR2", "gpu": "VideoCore IV", "storage": "eMMC + MicroSD via carrier", "connectivity": "PCIe, USB 2.0", "gpio": "2x 50-pin connectors", "video_output": "Depends on carrier board", "price": 10, "power_draw": "3.3V/1A", "form_factor": "30mm x 25mm (tiny module)", "pros": ["Ultra cheap compute module", "Tiny form factor", "Pi ecosystem", "Great for embedded"], "cons": ["Needs carrier board", "512MB RAM only", "No built-in WiFi"], "best_for": ["maker", "conversation", "writerdeck"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "Depends on carrier", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "Depends on carrier board", "power_consumption_w": 3, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "makerfabs_cm0iq": {"name": "Makerfabs CM0-IQ Carrier Board", "cpu": "For Pi CM0 module", "ram": "CM0 dependent", "gpu": "CM0 dependent", "storage": "MicroSD + eMMC", "connectivity": "WiFi, BT, USB, HDMI", "gpio": "40-pin GPIO + camera + display", "video_output": "HDMI + MIPI DSI + CSI", "price": 25, "power_draw": "5V/2A USB-C", "form_factor": "Compact carrier", "pros": ["CM0 carrier with full Pi ports", "Camera + display connectors", "Affordable"], "cons": ["Needs CM0 module", "Basic specs"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "N/A (Carrier)", "screen_size_inches": 0, "resolution": "HDMI 1080p", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI, USB, CSI, DSI", "power_consumption_w": 5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "milkv_jupiter2": {"name": "Milk-V Jupiter2 (RISC-V SG2380)", "cpu": "SG2380 RISC-V 8-core @ 2.5GHz", "ram": "8GB/16GB/32GB DDR5", "gpu": "IMG BXT-32-1024", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6E, BT 5.3, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + DP 1.4", "price": 130, "power_draw": "12V/2A DC", "form_factor": "120mm x 120mm", "pros": ["8-core RISC-V desktop-class", "32GB DDR5 option", "NVMe + 2.5GbE", "PCIe 3.0 expansion"], "cons": ["RISC-V Linux ecosystem maturing", "Larger form factor", "Needs 12V power supply"], "best_for": ["ai", "coding", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 4K@120Hz", "refresh_rate_hz": 120, "brightness_nits": 0, "interface": "HDMI 2.1, DP 1.4", "power_consumption_w": 20, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "low"}},
    "radxa_a7a": {"name": "Radxa A7A (RK3588S, AIO)", "cpu": "RK3588S Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 75, "power_draw": "5V/4A USB-C", "form_factor": "100mm x 75mm (AIO laptop board)", "pros": ["RK3588S at budget price", "Laptop AIO design", "NVMe native", "6 TOPS NPU"], "cons": ["AIO form limits enclosure options", "Linux support still maturing"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 10, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "hackberrypi_cm5": {"name": "HackberryPi CM5 (RK3588 Module)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB/32GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP + eDP", "price": 99, "power_draw": "5V/5A USB-C", "form_factor": "100mm x 80mm (CM module)", "pros": ["Full RK3588 in CM form", "32GB option", "Triple display", "NVMe + 2.5GbE", "6 TOPS NPU"], "cons": ["Needs carrier board", "Premium price for module"], "best_for": ["ai", "coding", "security", "research"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP, eDP", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "zhihe_a210": {"name": "Zhihe A210 (RISC-V, 12 TOPS NPU)", "cpu": "SpacemiT K1 8-core RISC-V @ 2.0GHz", "ram": "8GB/16GB LPDDR4X", "gpu": "IMG BXE-4-32", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.4, GbE, USB 3.0 x2", "gpio": "40-pin GPIO", "video_output": "HDMI 2.0 + USB-C DP", "price": 85, "power_draw": "5V/3A USB-C", "form_factor": "100mm x 75mm", "pros": ["12 TOPS NPU for edge AI", "8-core RISC-V", "NVMe", "16GB RAM option"], "cons": ["RISC-V ecosystem", "NPU software immature", "No 2.5GbE"], "best_for": ["ai", "coding", "research", "maker"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@30Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, USB-C DP", "power_consumption_w": 8, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "fair", "community_usage": "low", "failure_rate": "medium"}},
    "bbc_microbit_v2": {"name": "BBC micro:bit v2", "cpu": "ARM Cortex-M4 @ 64MHz (Nordic nRF52833)", "isa": "ARM Cortex-M4", "ram": "128KB SRAM + 512KB Flash", "gpu": "None (microcontroller)", "storage": "512KB Flash (built-in)", "connectivity": "BLE 5.0, USB-C, edge connector (19-pin)", "gpio": "19-pin edge connector (3V, GND, 5x large pads, 20-pin), SPI, I2C, UART", "video_output": "5x5 LED matrix (25 red LEDs)", "price": 20, "power_draw": "3V/30mA (USB or battery)", "form_factor": "51mm x 43mm (credit-card sized PCB)", "pros": ["Ultra beginner-friendly", "Built-in 5x5 LED matrix", "BLE 5.0 built-in", "2 programmable buttons", "MicroPython/CircuitPython/MakeCode", "Edge connector for accessories", "Built-in speaker + MEMS mic", "20-pin GPIO edge", "Temperature/light/magnet sensors", "Huge educational community"], "cons": ["No Linux (MCU only)", "Limited RAM", "No display output", "No WiFi (BLE only)", "5x5 LED matrix very small"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "5x5 LED Matrix", "screen_size_inches": 0.5, "resolution": "5x5 pixels", "refresh_rate_hz": 100, "brightness_nits": 50, "interface": "Edge connector + USB-C", "power_consumption_w": 0.1, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "esp32_devkitc": {"name": "ESP32-DevKitC V4 (ESP32-WROOM-32)", "cpu": "Tensilica Xtensa LX6 dual-core @ 240MHz", "isa": "XTensa LX6", "ram": "520KB SRAM + 4MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi 802.11 b/g/n, BT 4.2 BR/EDR + BLE, USB-UART bridge", "gpio": "30-pin GPIO (19x GPIO, ADC, DAC, touch, SPI, I2C, UART, I2S, PWM)", "video_output": "None (SPI/I2C display via GPIO)", "price": 8, "power_draw": "3.3V/80mA (WiFi idle), 500mA peak (WiFi TX)", "form_factor": "56mm x 28mm (standard dev board)", "pros": ["Most popular ESP32 board", "WiFi + BT classic + BLE", "Huge community", "Arduino/MicroPython/ESP-IDF", "Touch sensors", "Dual-core", "Ultra cheap", "Huge accessory ecosystem"], "cons": ["No video output", "MCU not Linux", "Limited RAM", "No built-in display"], "best_for": ["maker", "conversation", "survival"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via SPI/I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-UART, GPIO", "power_consumption_w": 0.5, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "esp32_s3_devkitc": {"name": "ESP32-S3-DevKitC-1", "cpu": "Tensilica Xtensa LX7 dual-core @ 240MHz", "isa": "XTensa LX7", "ram": "512KB SRAM + 8MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi 802.11 b/g/n, BLE 5.0, USB OTG, USB-UART", "gpio": "45-pin GPIO (SPI, I2C, UART, I2S, PWM, LCD, camera)", "video_output": "RGB LCD interface (8-bit parallel), MIPI DBI, SPI display", "price": 10, "power_draw": "3.3V/80mA (WiFi idle)", "form_factor": "54mm x 28mm (standard dev board)", "pros": ["USB OTG host/device", "Parallel RGB LCD out", "Camera interface", "WiFi + BLE 5.0", "P4 replacement ready", "Vector instructions (SIMD)", "Cheap"], "cons": ["No BT classic", "MCU not Linux", "Limited RAM"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "RGB LCD / SPI TFT", "screen_size_inches": 0, "resolution": "Up to 1024x600 via RGB LCD", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "USB OTG, GPIO", "power_consumption_w": 0.6, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "xiao_esp32c3": {"name": "Seeed Studio XIAO ESP32C3", "cpu": "RISC-V 32-bit single-core @ 160MHz", "isa": "RISC-V", "ram": "400KB SRAM", "gpu": "None (MCU)", "storage": "4MB Flash", "connectivity": "WiFi 802.11 b/g/n, BLE 5.0, USB-C", "gpio": "11x GPIO (ADC, SPI, I2C, UART, PWM)", "video_output": "None (I2C/SPI display)", "price": 6, "power_draw": "3.3V/65mA", "form_factor": "21mm x 17.5mm (thumb-sized)", "pros": ["Tiny thumb-size", "RISC-V ESP32-C3", "USB-C", "Ultra cheap", "Battery charging (JST)", "Low power"], "cons": ["Very few GPIO pins", "Single-core", "No BT classic", "MCU not Linux"], "best_for": ["conversation", "maker", "writerdeck"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via I2C/SPI", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-C, GPIO", "power_consumption_w": 0.2, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "excellent", "community_usage": "very_high", "failure_rate": "very_low"}},
    "tbeam_sx1262": {"name": "TTGO T-Beam (ESP32 + LoRa SX1262 + GPS)", "cpu": "Tensilica Xtensa LX6 dual-core @ 240MHz", "isa": "XTensa LX6", "ram": "520KB SRAM + 4MB PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi, BT 4.2, BLE, LoRa SX1262 (868/915MHz), NEO-6M GPS, USB-UART", "gpio": "Internal (pin headers for I2C/UART/SPI)", "video_output": "None (SPI OLED on board)", "price": 30, "power_draw": "3.7V/120mA (LoRa idle), 450mA peak (TX+GPS)", "form_factor": "65mm x 25mm (board with IPEX+GPS)", "pros": ["Built-in LoRa + GPS", "Meshtastic ready", "WiFi + BT + BLE", "Integrated GPS", "Solar charging option (IPEX)", "Active Meshtastic community"], "cons": ["No display (needs OLED add-on)", "MCU not Linux", "Less GPIO accessible"], "best_for": ["survival", "research", "maker"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External 0.96\" OLED 128x64 via I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-UART, GPIO", "power_consumption_w": 0.4, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "very_high", "failure_rate": "low"}},
    "esp32_c5_devkitc": {"name": "ESP32-C5-DevKitC-1 (Dual-band WiFi 6)", "cpu": "RISC-V 32-bit single-core @ 240MHz + LP-core", "isa": "RISC-V", "ram": "384KB SRAM + external PSRAM", "gpu": "None (MCU)", "storage": "16MB Flash", "connectivity": "WiFi 6 dual-band 2.4/5GHz, BLE 5.0, 802.15.4 (Thread/Zigbee), USB-UART", "gpio": "29-pin GPIO (SPI, I2C, UART, I2S, PWM, USB OTG)", "video_output": "None (SPI/I2C display via GPIO)", "price": 10, "power_draw": "3.3V/100mA", "form_factor": "52mm x 28mm (standard dev board)", "pros": ["First ESP32 with dual-band WiFi 6", "5GHz band avoids 2.4GHz congestion", "802.15.4 for Thread/Zigbee", "USB OTG", "RISC-V open ISA"], "cons": ["Single-core", "No BT classic", "MCU not Linux", "Newer chip, smaller community"], "best_for": ["maker", "conversation", "survival"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via SPI/I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "USB-UART, GPIO", "power_consumption_w": 0.3, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "good", "community_usage": "low", "failure_rate": "low"}},
    "esp32_e22_devkitc": {"name": "ESP32-E22 (WiFi 6E tri-band)", "cpu": "RISC-V dual-core @ 500MHz", "isa": "RISC-V", "ram": "1MB on-chip SRAM", "gpu": "None (MCU)", "storage": "16MB Flash + external PSRAM option", "connectivity": "WiFi 6E tri-band 2.4/5/6GHz, BT 6.0 BR/EDR+LE, 2x2 MIMO, PCIe, USB, SDIO", "gpio": "UP to GPIO (SPI, I2C, UART, I2S, PWM)", "video_output": "None (SPI display via GPIO)", "price": 15, "power_draw": "3.3V/200mA (WiFi TX)", "form_factor": "52mm x 28mm (standard dev board)", "pros": ["WiFi 6E tri-band (2.4/5/6GHz)", "2.1 Gbps throughput (iperf)", "BT 6.0 dual-mode", "PCIe + USB + SDIO host", "RISC-V dual-core 500MHz"], "cons": ["No PSRAM confirmed", "Early silicon, limited docs", "Higher power draw", "Expensive for ESP32"], "best_for": ["maker", "research"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "External display via SPI/I2C", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "PCIe, USB, SDIO, GPIO", "power_consumption_w": 1.0, "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "early", "community_usage": "very_low", "failure_rate": "medium"}},
    "esp32_h21_devkitc": {"name": "ESP32-H21 (Ultra-low-power BLE+Zigbee)", "cpu": "RISC-V single-core @ 96MHz", "isa": "RISC-V", "ram": "320KB SRAM", "gpu": "None (MCU)", "storage": "4MB Flash", "connectivity": "BLE 5.x, 802.15.4 (Zigbee/Thread), integrated RF, DC-DC converter", "gpio": "GPIO (SPI, I2C, UART, PWM)", "video_output": "None", "price": 5, "power_draw": "3.3V/10mA active, uA sleep", "form_factor": "15mm x 15mm (tiny QFN)", "pros": ["Ultra-low power (uA sleep)", "BLE + Zigbee/Thread", "Integrated DC-DC", "Tiny footprint", "Sub-$5"], "cons": ["96MHz only", "No WiFi at all", "Very limited RAM", "MCU not Linux", "New chip"], "best_for": ["maker", "conversation"], "compatibility": ["ALL"], "display_type": "N/A (MCU)", "screen_size_inches": 0, "resolution": "None", "refresh_rate_hz": 0, "brightness_nits": 0, "interface": "GPIO", "power_consumption_w": 0.03, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "very_high", "driver_support": "early", "community_usage": "very_low", "failure_rate": "low"}},
    "banana_pi_m4_super": {"name": "Banana Pi BPI-M4 Super (RK3588)", "cpu": "RK3588 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR4X", "gpu": "Mali-G610 MC4", "storage": "eMMC + NVMe M.2 + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.2, PCIe 3.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 95, "power_draw": "5V/4A USB-C", "form_factor": "100mm x 75mm", "pros": ["RK3588 at Pi 5 price", "2.5GbE", "NVMe native", "6 TOPS NPU", "Good Banana Pi community"], "cons": ["Smaller community than Pi", "Linux support maturing"], "best_for": ["ai", "coding", "security"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 12, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "unihiker": {"name": "UNIHIKER (Pi Alternative + Touch)", "cpu": "Allwinner H618 Cortex-A53 quad-core @ 1.5GHz", "ram": "2GB LPDDR4", "gpu": "Mali-G31 MP2", "storage": "16GB eMMC + MicroSD", "connectivity": "WiFi 5, BT 5.0, GbE, USB 2.0 x2, USB-C", "gpio": "24-pin GPIO + 4-pin STEMMA QT", "video_output": "Built-in 2.8\" 240x320 IPS touch", "price": 79, "power_draw": "5V/2A USB-C", "form_factor": "86mm x 58mm x 15mm (built-in screen)", "pros": ["Built-in 2.8\" touchscreen", "All-in-one design", "Python/Bash/MicroPython", "Jupyter notebook built-in", "STEMMA QT for sensors", "Headphone + mic jacks"], "cons": ["2.8\" screen small", "2GB RAM only", "Limited CPU power", "No NVMe"], "best_for": ["maker", "conversation", "education"], "compatibility": ["ALL"], "display_type": "IPS touch", "screen_size_inches": 2.8, "resolution": "240x320", "refresh_rate_hz": 30, "brightness_nits": 250, "interface": "Built-in + HDMI out", "power_consumption_w": 3, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "waveshare_cm5_mini_pc": {"name": "Waveshare CM5 Mini PC (Fanless)", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "8GB/16GB LPDDR4X", "gpu": "VideoCore VII", "storage": "eMMC + NVMe + MicroSD", "connectivity": "WiFi 6, BT 5.0, 2x GbE, USB 3.0 x2, USB 2.0 x2", "gpio": "40-pin GPIO header (internal)", "video_output": "2x micro-HDMI (4K@60Hz)", "price": 100, "power_draw": "5V/5A USB-C (27W max)", "form_factor": "120mm x 80mm x 25mm (fanless metal case)", "pros": ["Fanless metal enclosure", "Dual Ethernet", "NVMe support", "Industrial ready", "Built-in wall mount"], "cons": ["Larger than board-only", "No battery built-in", "Limited GPIO access in case"], "best_for": ["coding", "security", "research", "server"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "4K@60Hz per output", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "2x micro-HDMI, USB-C power", "power_consumption_w": 12, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "low"}},
    "pironman_5_pro_max": {"name": "Pironman 5 Pro Max (Pi 5 Tower)", "cpu": "BCM2712 Cortex-A76 @ 2.4GHz quad-core", "ram": "8GB/16GB LPDDR4X", "gpu": "VideoCore VII", "storage": "M.2 NVMe + MicroSD", "connectivity": "WiFi 6, BT 5.0, GbE, USB 3.0 x2", "gpio": "40-pin GPIO + AI HAT+ connector", "video_output": "2x micro-HDMI + 4.3\" built-in touch", "price": 160, "power_draw": "5V/5A USB-C", "form_factor": "150mm x 100mm x 60mm (tower)", "pros": ["Built-in 4.3\" touch display", "AI HAT+ ready (26 TOPS)", "RGB LED tower", "NVMe M.2 onboard", "Active fan cooling", "Desktop-like form factor"], "cons": ["Expensive", "Bulky for portable use", "Proprietary case"], "best_for": ["ai", "coding", "research", "media"], "compatibility": ["ALL"], "display_type": "IPS touch + HDMI", "screen_size_inches": 4.3, "resolution": "800x480 (built-in)", "refresh_rate_hz": 60, "brightness_nits": 300, "interface": "micro-HDMI + built-in", "power_consumption_w": 15, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "medium", "failure_rate": "low"}},
    "odroid_m2": {"name": "ODROID-M2 (RK3588S2)", "cpu": "RK3588S2 Cortex-A76+A55 (8-core)", "ram": "8GB/16GB LPDDR5", "gpu": "Mali-G610 MC4", "storage": "NVMe M.2 + eMMC + MicroSD", "connectivity": "WiFi 6, BT 5.2, 2.5GbE, USB 3.0 x2, USB 2.0", "gpio": "40-pin GPIO", "video_output": "HDMI 2.1 + USB-C DP", "price": 85, "power_draw": "9V/3A DC barrel", "form_factor": "90mm x 62mm", "pros": ["RK3588S2 with LPDDR5", "NVMe native", "2.5GbE", "Hardkernel quality", "Good Linux support"], "cons": ["DC barrel (not USB-C)", "Active cooling needed", "Smaller community"], "best_for": ["ai", "coding", "research", "media"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.1 8K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.1, USB-C DP", "power_consumption_w": 12, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "zimablade": {"name": "ZimaBlade (x86 Blade SBC)", "cpu": "Intel N100 or N305 (4C/8C)", "ram": "8GB/16GB DDR5", "gpu": "Intel UHD", "storage": "NVMe M.2 + SATA III", "connectivity": "WiFi 6, BT 5.2, 2x 2.5GbE, USB 3.2, USB-C", "gpio": "16-pin GPIO", "video_output": "HDMI 2.0 + Mini-DP", "price": 140, "power_draw": "12W TDP (fanless)", "form_factor": "120mm x 80mm (blade/mini-ITX mount)", "pros": ["Full x86 desktop CPU", "Dual 2.5GbE", "NVMe + SATA", "Wall-mount rackable", "True Windows/Linux", "Low power for x86"], "cons": ["No 40-pin GPIO", "Fanless chassis needed", "Limited cyberdeck builds", "Not ARM ecosystem"], "best_for": ["coding", "research", "security", "server"], "compatibility": ["ALL"], "display_type": "N/A (SBC)", "screen_size_inches": 0, "resolution": "HDMI 2.0 4K@60Hz", "refresh_rate_hz": 60, "brightness_nits": 0, "interface": "HDMI 2.0, Mini-DP", "power_consumption_w": 12, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "medium", "failure_rate": "low"}},
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
    "dsi_7inch_touch2": {"name": "Raspberry Pi Touch Display 2 (7\" DSI)", "size": "7 inch", "resolution": "1280x800", "interface": "DSI ribbon + GPIO touch", "price": 70, "power_draw": "5V/0.5A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Official Pi 5/CM5 display", "Higher res than v1", "USB-C touch passthrough", "Direct DSI (no HDMI)", "Slim bezel"], "cons": ["Pi/CM only", "Needs DSI cable"], "best_for": ["coding", "writerdeck", "gaming"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 500, "power_consumption_w": 3, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "excellent", "community_usage": "high", "failure_rate": "very_low"}},
    "dsi_10_1_waveshare": {"name": "Waveshare 10.1\" DSI IPS (1280x800)", "size": "10.1 inch", "resolution": "1280x800", "interface": "DSI ribbon + GPIO touch", "price": 95, "power_draw": "5V/0.6A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Large DSI panel", "Capacitive touch", "CM4/CM5 carrier compatible", "Frees HDMI port"], "cons": ["DSI cable routing", "Pi/CM only"], "best_for": ["coding", "research", "ai", "media"], "display_type": "IPS", "screen_size_inches": 10.1, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 4, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "low"}},
    "dsi_8inch_waveshare": {"name": "Waveshare 8\" DSI IPS (1280x800)", "size": "8 inch", "resolution": "1280x800", "interface": "DSI ribbon + GPIO touch", "price": 80, "power_draw": "5V/0.5A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Compact DSI panel", "Touch", "Good for handheld CM5 builds"], "cons": ["Pi/CM only"], "best_for": ["coding", "writerdeck", "conversation"], "display_type": "IPS", "screen_size_inches": 8, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 3.5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "dsi_5inch_waveshare": {"name": "Waveshare 5\" DSI IPS (800x480)", "size": "5 inch", "resolution": "800x480", "interface": "DSI ribbon + GPIO touch", "price": 45, "power_draw": "5V/0.3A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Small DSI panel", "Touch", "Ultra slim", "Cheap"], "cons": ["Low resolution", "Pi/CM only"], "best_for": ["conversation", "writerdeck", "field-repair"], "display_type": "IPS", "screen_size_inches": 5, "refresh_rate_hz": 60, "brightness_nits": 350, "power_consumption_w": 2, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "dsi_11_9_ultrawide": {"name": "Waveshare 11.9\" DSI Ultra-Wide (1920x480)", "size": "11.9 inch", "resolution": "1920x480", "interface": "DSI ribbon + GPIO touch", "price": 120, "power_draw": "5V/0.8A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Cinematic ultrawide", "CM5 carrier staple", "Touch", "Great for dashboards/terminals"], "cons": ["Unusual aspect ratio", "DSI only"], "best_for": ["coding", "security", "media", "ai"], "display_type": "IPS", "screen_size_inches": 11.9, "refresh_rate_hz": 60, "brightness_nits": 450, "power_consumption_w": 5, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "dsi_13_3_waveshare": {"name": "Waveshare 13.3\" DSI IPS (1920x1080)", "size": "13.3 inch", "resolution": "1920x1080", "interface": "DSI ribbon + GPIO touch", "price": 180, "power_draw": "5V/1A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Full HD DSI", "Large workspace", "CM4/CM5 compatible"], "cons": ["Expensive", "Large enclosure needed"], "best_for": ["coding", "ai", "research", "media"], "display_type": "IPS", "screen_size_inches": 13.3, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 7, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "medium", "failure_rate": "low"}},
    "dsi_4inch_capacitive": {"name": "4\" MIPI DSI Capacitive Touch (720x720)", "size": "4 inch", "resolution": "720x720", "interface": "DSI ribbon + GPIO touch", "price": 55, "power_draw": "5V/0.3A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Square DSI panel", "Touch", "HackberryPi CM5 style", "Compact"], "cons": ["Square format", "Pi/CM only"], "best_for": ["conversation", "writerdeck", "gaming"], "display_type": "IPS", "screen_size_inches": 4, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 2, "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "driver_support": "medium", "community_usage": "low", "failure_rate": "medium"}},
    "pimoroni_pidisplay7": {"name": "Pimoroni 7\" DSI Display", "size": "7 inch", "resolution": "800x480", "interface": "DSI ribbon + GPIO touch", "price": 85, "power_draw": "5V/0.5A via GPIO", "touch": True, "viewing_angle": "178 degrees", "pros": ["Pimoroni quality", "Frameless glass", "Touch", "Attaches to GPIO header"], "cons": ["Low resolution", "Pi only"], "best_for": ["conversation", "writerdeck", "media"], "display_type": "IPS", "screen_size_inches": 7, "refresh_rate_hz": 60, "brightness_nits": 400, "power_consumption_w": 3, "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "driver_support": "good", "community_usage": "high", "failure_rate": "very_low"}},
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
    "waveshare_cm5_carrier_pcie": {"name": "Waveshare CM5 PCIe Carrier Board", "type": "CM5 carrier", "pins": "Full 40-pin GPIO + M.2 NVMe + PCIe x1 + eMMC", "compatibility": "CM5 only", "price_range": "$35-$55", "pros": ["NVMe boot support", "PCIe Gen 3 x1", "Compact 90x62mm", "Fan header"], "cons": ["CM5 only", "No HDMI (use DSI/USB-C DP)"], "best_for": ["ai", "coding", "security"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "geekworm_x1001": {"name": "Geekworm X1001 NVMe Carrier for CM5", "type": "CM5 carrier", "pins": "M.2 2280/2242 + 40-pin GPIO + USB 2.0 hub", "compatibility": "CM5 only", "price_range": "$15-$25", "pros": ["Dual M.2 slots", "NVMe boot", "Affordable", "Stackable"], "cons": ["No eMMC slot", "Basic carrier"], "best_for": ["coding", "security", "ai"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "low"}},
    "pineberry_pi_hatdrive": {"name": "Pineberry Pi HatDrive! (CM5 NVMe)", "type": "CM5 carrier", "pins": "M.2 2230/2242 + PCIe flex + 40-pin GPIO", "compatibility": "CM5 only", "price_range": "$15-$20", "pros": ["Boot from NVMe", "PCIe Gen 3 x1 flex cable", "Compact", "Open hardware"], "cons": ["Flex cable delicate", "No M.2 2280"], "best_for": ["coding", "ai"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "waveshare_cm4_carrier_pcie": {"name": "Waveshare CM4 IO Board (PCIe)", "type": "CM4 carrier", "pins": "Full 40-pin GPIO + M.2 NVMe + PCIe x1 + eMMC", "compatibility": "CM4 only", "price_range": "$25-$40", "pros": ["NVMe for CM4", "Full IO breakout", "Industrial grade"], "cons": ["CM4 only"], "best_for": ["gaming", "media", "writerdeck"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "pimoroni_nvme_base": {"name": "Pimoroni NVMe Base for CM4/CM5", "type": "NVMe carrier", "pins": "M.2 2230-2280 + PCIe", "compatibility": "CM4, CM5", "price_range": "$15-$20", "pros": ["Works with CM4 and CM5", "M.2 2280 support", "Low profile"], "cons": ["Needs separate IO board"], "best_for": ["coding", "security"], "risk_level": "minimal", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "high", "failure_rate": "very_low"}},
    "clockworkpi_uconsole_kit": {"name": "ClockworkPi uConsole Kit (CM4/CM5)", "type": "All-in-one carrier", "pins": "CM4/CM5 slot + 5\" display + QWERTY + battery + speaker", "compatibility": "CM4, CM5", "price_range": "$160-$280", "pros": ["Complete handheld kit", "Modular compute", "Expansion bay", "Aluminum shell"], "cons": ["Fixed form factor", "Limited SBC options"], "best_for": ["coding", "writerdeck", "survival"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "hackberrypi_cm5_carrier": {"name": "HackberryPi CM5 Carrier (Aluminum)", "type": "CM5 carrier + chassis", "pins": "40-pin GPIO + NVMe + 4\" display + BB keyboard", "compatibility": "CM5 only", "price_range": "$168", "pros": ["Aluminum chassis", "Integrated keyboard", "Open-source STL", "Kali ready"], "cons": ["CM5 only", "Fixed 4\" screen"], "best_for": ["security", "coding", "writerdeck"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "medium", "failure_rate": "low"}},
    "radxa_rock5c_carrier": {"name": "Radxa ROCK 5C (CM4 form factor RK3588S2)", "type": "RK3588S2 module in CM4 form", "pins": "CM4-compatible + PCIe 3.0 x4 + 2.5GbE", "compatibility": "CM4 carriers", "price_range": "$80-$190", "pros": ["RK3588S2 power in CM4 form", "PCIe 3.0 x4", "2.5GbE", "Fits CM4 carriers"], "cons": ["Needs CM4 carrier", "Heat management"], "best_for": ["ai", "coding", "security"], "risk_level": "low", "risk_factors": {"manufacturer_reliability": "high", "community_usage": "medium", "failure_rate": "low"}},
    "bananapi_cm5_carrier": {"name": "Banana Pi BPI-CM5 (RK3588S2, CM4 form)", "type": "RK3588S2 module in CM4 form", "pins": "CM4-compatible + dual 2.5GbE + NVMe", "compatibility": "CM4 carriers", "price_range": "$70-$120", "pros": ["Dual 2.5GbE", "RK3588S2", "CM4 form factor"], "cons": ["Needs CM4 carrier", "Newer board"], "best_for": ["ai", "coding", "security"], "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "low", "failure_rate": "medium"}},
    "milkv_mars_cm_carrier": {"name": "Milk-V Mars CM (RISC-V SG2002, CM4 form)", "type": "RISC-V module in CM4 form", "pins": "CM4-compatible + dual GbE + NVMe", "compatibility": "CM4 carriers", "price_range": "$55", "pros": ["RISC-V in CM4 form", "Dual GbE", "Affordable"], "cons": ["RISC-V ecosystem", "4GB RAM only"], "best_for": ["coding", "research", "maker"], "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "medium", "community_usage": "low", "failure_rate": "medium"}},
    "cm5_custom_nvme_carrier": {"name": "Custom CM5 NVMe Carrier (4-layer PCB)", "type": "Custom carrier design", "pins": "M.2 2280 PCIe Gen3 x1 + 40-pin GPIO + USB hub", "compatibility": "CM5 only", "price_range": "$50-$80 (fab)", "pros": ["Impedance-controlled PCIe/DSI", "Custom port placement", "4-layer stackup"], "cons": ["PCB fab required", "Design effort"], "best_for": ["ai", "coding", "security"], "risk_level": "medium", "risk_factors": {"manufacturer_reliability": "varies", "community_usage": "low", "failure_rate": "medium"}},
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
    "powder_coating": {"name": "Powder Coating", "finish": ["matte", "gloss", "textured", "metallic", "translucent"], "price": "$40-80/batch", "application": "Electrostatic spray + 400F oven cure", "best_for": ["industrial", "survival", "tactical"], "notes": "Marine-grade durability, scratch-proof, shop service or $150 DIY rig"},
    "cerakote": {"name": "Cerakote Ceramic Coating", "finish": ["matte", "gloss", "camo", "cobalt", "burnt-bronze"], "price": "$30-60/batch", "application": "Spray + 180F cure, or air-cure C series", "best_for": ["tactical", "survival", "industrial"], "notes": "Thin (0.001\") ceramic armor, won't chip like paint, 1500+ colors"},
    "anodizing": {"name": "Aluminum Anodizing", "finish": ["black", "blue", "red", "clear", "two-tone-mask"], "price": "$50-120/batch", "application": "Electrolytic bath, acid etch + dye + seal", "best_for": ["cyberpunk", "industrial"], "notes": "Metal parts only, dye penetrates surface — scratch-proof color"},
    "hydrodipping": {"name": "Hydrographic Dipping (Water Transfer)", "finish": ["camo", "carbon", "wood", "skull", "circuit"], "price": "$20-50/part", "application": "Base coat + film float + dip + clear coat", "best_for": ["cyberpunk", "tactical", "conversation-piece"], "notes": "Wrap impossible 3D shapes with printed film patterns"},
    "bead_blasting": {"name": "Bead / Sand Blasting", "finish": ["satin", "matte", "etched-rough"], "price": "$15-40/part", "application": "Abrasive blast, masks for logos", "best_for": ["industrial", "minimal", "nautical"], "notes": "Uniform matte key for paint or bare-metal anodized look"},
    "laser_engraving": {"name": "Laser Engraving / Etching", "finish": ["burned-black", "white-mask", "depth-relief"], "price": "$5-30/part", "application": "CO2 or diode laser, masks for contrast", "best_for": ["nautical", "steampunk", "conversation-piece"], "notes": "Logos, runes, serial numbers, artwork burned into any surface"},
    "uv_printing": {"name": "UV Printing / Flatbed", "finish": ["photo", "white-ink", "textured-clear"], "price": "$20-60/side", "application": "Flatbed UV printer, full color direct", "best_for": ["conversation-piece", "cyberpunk"], "notes": "Full-color artwork printed directly on enclosure, shop service"},
    "flocking": {"name": "Flocking (Velvet Coating)", "finish": ["black", "red", "teal", "charcoal"], "price": "$10-20/kit", "application": "Adhesive + electrostatic fiber applicator", "best_for": ["retro", "writerdeck", "feminine_craft"], "notes": "Soft-touch velvet interior or full shell, muffles rattles"},
    "thermochromic": {"name": "Thermochromic Paint", "finish": ["color-shift", "black-to-color"], "price": "$15-25/can", "application": "Spray or brush, reactive to heat", "best_for": ["conversation-piece", "cyberpunk"], "notes": "Changes color where the CPU is hot — living heat map"},
    "photoluminescent": {"name": "Photoluminescent (Glow) Pigment", "finish": ["glow-green", "glow-blue", "glow-teal"], "price": "$12-20", "application": "Mix into resin or paint, charge with light", "best_for": ["survival", "tactical", "night_ops"], "notes": "Night-visible bezels, keycaps, and alignment markers"},
    "acid_patina": {"name": "Acid Patina (Forced Aging)", "finish": ["verdigris", "rust", "blue-steel"], "price": "$8-15", "application": "Acid/ammonia fuming over copper, brass, or steel", "best_for": ["steampunk", "nautical", "wasteland"], "notes": "Forced years of aging in an afternoon on metal accents"},
    "automotive_clearcoat": {"name": "Automotive 2K Clear Coat", "finish": ["wet-look-gloss", "matte", "satin"], "price": "$15-30", "application": "Spray over painted/enameled parts, cures hard", "best_for": ["ALL"], "notes": "Gasoline-resistant hard shell over any paint job"},
    "marbling": {"name": "Acrylic Paint Marbling", "finish": ["swirl", "multi-color", "water-marble"], "price": "$5-12", "application": "Float paint on water, dip the part", "best_for": ["conversation-piece", "feminine_craft"], "notes": "One-of-a-kind swirl patterns, cheap and fun"},
    "electroplating": {"name": "Electroplating (Copper/Nickel/Gold)", "finish": ["mirror-gold", "nickel", "copper"], "price": "$25-60/batch", "application": "Electrolytic bath on conductive base", "best_for": ["steampunk", "luxury", "conversation-piece"], "notes": "Real plated metal finish for brass/gold hardware"},
    "ceramic_glaze": {"name": "Ceramic / Porcelain Glaze", "finish": ["glossy-ceramic", "matte", "crackle"], "price": "$20-40", "application": "Glaze ceramic or fired-clay panels, kiln fire", "best_for": ["conversation-piece", "minimal"], "notes": "Kiln-fired glossy panels that never fade"},
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
        "orange_pi_rv2": "USB-C 5V/3A", "banana_pi_bpi_m4": "USB-C 5V/5A",
        "pi_500": "USB-C 5V/5A", "rock5b_itx": "DC 12V barrel or 5V/5A",
        "lichee_console_4a": "USB-C PD 5V/3A", "hackberry_cm5": "USB-C PD (via carrier)",
    },
    "display_interface": {
        "pi5": ["hdmi", "dsi", "spi"], "pi4": ["hdmi", "dsi", "spi"],
        "pi_zero_2w": ["mini-hdmi", "spi", "i2c"],
        "orange_pi_5": ["hdmi", "usb-c-dp"], "orange_pi_5_plus": ["hdmi", "usb-c-dp"],
        "jetson_orin_nano": ["hdmi", "dsi"], "lattepanda_3_delta": ["hdmi", "usb-c-dp"],
        "radxa_rock_5b": ["hdmi", "usb-c-dp"], "khadas_edge2": ["hdmi", "usb-c-dp"],
        "orange_pi_rv2": ["hdmi", "spi"], "banana_pi_bpi_m4": ["hdmi", "dsi"],
        "pi_500": ["hdmi", "spi"], "rock5b_itx": ["hdmi", "dsi", "usb-c-dp"],
        "lichee_console_4a": ["dsi"], "hackberry_cm5": ["dsi"],
    },
    "dsi_panels": {
        "dsi_7inch_touch2": ["pi5", "cm4", "cm5"], "dsi_10_1_waveshare": ["pi4", "pi5", "cm4", "cm5"],
        "dsi_8inch_waveshare": ["pi4", "pi5", "cm4", "cm5"], "dsi_5inch_waveshare": ["pi4", "pi5", "cm4", "cm5"],
        "dsi_11_9_ultrawide": ["pi5", "cm5"], "dsi_13_3_waveshare": ["pi4", "pi5", "cm4", "cm5"],
        "dsi_4inch_capacitive": ["cm4", "cm5"], "pimoroni_pidisplay7": ["pi4", "pi5"],
    },
    "ups_compat": {
        "geekworm_x733": ["pi5", "pi4", "cm5"], "geekworm_x728": ["pi5", "pi4", "cm5"],
        "pichondria_pd_trigger": ["any"], "pichondria_pd_20000": ["any"], "pichondria_pd_30000": ["any"],
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
# HARDWARE MODULE DATABASE — NATO rails, sliding screens, NP-F batteries, Li'l PCB
# ============================================================
HARDWARE_MODULE_DATABASE = {
    "nato_rail_set": {
        "name": "NATO Rail Set (3x Picatinny)",
        "type": "mounting", "price": 3.50, "tier": "essential",
        "description": "3x MIL-STD-1913 Picatinny rails. Mount cameras, flashlights, antennas.",
        "includes": "3x 10-slot rails, 12x M4 bolts, 12x T-nuts, 4x corner brackets", "weight_g": 180,
        "stl_files": ["nato_rail_bracket.stl", "nato_rail_endcap.stl"],
        "best_for": ["security", "survival", "research", "field-repair"],
    },
    "nato_deluxe_bundle": {
        "name": "Deluxe NATO Rail Bundle (5 rails + QD clamps)",
        "type": "mounting", "price": 8.00, "tier": "premium",
        "description": "Full rail system: 5 rails, 8 corner brackets, 2 quick-release sling mounts.",
        "includes": "5x rails, 8x L-brackets, 2x QD mounts, 24x hardware kit", "weight_g": 420,
        "stl_files": ["nato_full_frame.stl", "nato_qd_mount.stl"],
        "best_for": ["security", "survival", "conversation-piece"],
    },
    "sliding_screen_kit": {
        "name": "Sliding Screen Mechanism (linear rails)",
        "type": "mechanical", "price": 10.00, "tier": "premium",
        "description": "2x 250mm steel rods + 4x bearings + carriage + cable chain. Inspired by Jankbu 2026.",
        "includes": "2x 250mm 8mm rods, 4x SC8UU bearings, carriage STL, 0.5m cable chain, hardware",
        "weight_g": 350, "max_screen": "10.1\" / 600g",
        "stl_files": ["screen_carriage.stl", "rod_bracket.stl", "cable_chain_mount.stl"],
        "best_for": ["coding", "ai", "research", "security"],
    },
    "sliding_screen_heavyduty": {
        "name": "HD Sliding Screen (CNC aluminum + IGUS chain)",
        "type": "mechanical", "price": 18.00, "tier": "pro",
        "description": "CNC aluminum carriage, 4x LM8UU, IGUS energy chain, locking pin. For 15\" displays.",
        "includes": "CNC carriage, 2x 300mm rails, 4x LM8UU, 0.8m IGUS chain, locking pin, jig STL",
        "weight_g": 680, "max_screen": "15.6\" / 1200g",
        "stl_files": ["hd_carriage_plate.stl", "locking_pin_assembly.stl"],
        "best_for": ["ai", "research", "media"],
    },
    "npf_battery_sled": {
        "name": "NP-F Battery Sled (hot-swap, OLED voltage)",
        "type": "power", "price": 6.00, "tier": "essential",
        "description": "Sony NP-F camcorder battery sled. Hot-swap, USB-C PD, OLED voltage display.",
        "includes": "Sled STL, NP-F terminals, 0.91\" OLED, USB-C PD board, DC jack, hardware",
        "weight_g": 85, "output": "5V/9V/12V @ 3A",
        "stl_files": ["npf_sled.stl", "npf_contact_plate.stl"],
        "best_for": ["ALL"],
    },
    "npf_battery_sled_dual": {
        "name": "Dual NP-F Sled (parallel + ideal diode)",
        "type": "power", "price": 10.00, "tier": "premium",
        "description": "Dual NP-F sled with ideal diode combiner. Hot-swap without power cycle. 18400mAh max.",
        "includes": "Dual sled STL, 2x NP-F contacts, OR-ing module, OLED, USB-C PD, hardware",
        "weight_g": 155, "output": "5V/9V/12V @ 5A",
        "stl_files": ["npf_dual_sled.stl", "npf_dual_lid.stl"],
        "best_for": ["survival", "research", "conversation-piece"],
    },
    "lilpcb_backplane": {
        "name": "Li'l PCB Backplane (4-slot hot-swap)",
        "type": "pcb_module", "price": 5.00, "tier": "essential",
        "description": "4-slot backplane: I2C + 3.3V/5V + 2x GPIO + UART per slot. No rewiring needed.",
        "includes": "Backplane PCB, 4x 8-pin slot connectors, power terminals, I2C breakout, standoffs",
        "weight_g": 45, "slot_count": 4, "module_format": "30x25mm Li'l PCB",
        "stl_files": ["lilpcb_backplane_mount.stl"],
        "best_for": ["maker", "coding", "research", "ai"],
    },
    "lilpcb_sdr": {
        "name": "Li'l PCB SDR Module (RTL-SDR)",
        "type": "pcb_module", "price": 8.00, "tier": "premium",
        "description": "RTL-SDR (R820T2 + RTL2832U) on Li'l PCB. 24MHz-1766MHz, SMA antenna.",
        "includes": "SDR module, SMA connector, telescopic antenna (15cm)",
        "weight_g": 25, "frequency": "24MHz-1766MHz", "antenna": "SMA telescopic",
        "needs_module": "lilpcb_backplane",
        "best_for": ["security", "ham-radio", "research"],
    },
    "lilpcb_lora": {
        "name": "Li'l PCB LoRa Module (SX1262 Meshtastic)",
        "type": "pcb_module", "price": 5.50, "tier": "essential",
        "description": "SX1262 LoRa on Li'l PCB. Meshtastic firmware. 868/915MHz, 5-15km.",
        "includes": "LoRa module, SMA antenna, 1/4 wave whip, Meshtastic pre-flashed",
        "weight_g": 18, "frequency": "868/915MHz", "range_km": "5-15",
        "needs_module": "lilpcb_backplane",
        "best_for": ["survival", "research", "ham-radio"],
    },
    "lilpcb_gps": {
        "name": "Li'l PCB GPS Module (ublox)",
        "type": "pcb_module", "price": 4.00, "tier": "essential",
        "description": "ublox GPS + GLONASS on Li'l PCB. 72-channel, -167dBm, NMEA @ 9600 baud.",
        "includes": "GPS module, active patch antenna, CR1220 backup battery holder",
        "weight_g": 15, "channels": 72, "sensitivity_dbm": -167,
        "needs_module": "lilpcb_backplane",
        "best_for": ["survival", "research", "drone"],
    },
    "lilpcb_nvme": {
        "name": "Li'l PCB NVMe Adapter (M.2 2242)",
        "type": "pcb_module", "price": 7.00, "tier": "premium",
        "description": "M.2 NVMe on Li'l PCB. PCIe 3.0 x1 via FPC cable. 1TB+ hot-swap storage.",
        "includes": "NVMe adapter PCB, M.2 2242 connector, FPC PCIe cable (10cm)",
        "weight_g": 12, "max_ssd": "2TB M.2 2242 NVMe",
        "needs_module": "lilpcb_backplane",
        "best_for": ["ai", "coding", "security"],
    },
    "lilpcb_env_sensor": {
        "name": "Li'l PCB Environmental Sensor Pack",
        "type": "pcb_module", "price": 3.50, "tier": "essential",
        "description": "BME280 + SGP40 + BH1750 on one Li'l PCB. Temp/humidity/pressure/VOC/light.",
        "includes": "Sensor module, I2C address jumpers",
        "weight_g": 10, "sensors": "BME280 + SGP40 + BH1750",
        "needs_module": "lilpcb_backplane",
        "best_for": ["weather-station", "research", "home-automation"],
    },
}

LILPCB_MODULE_CATALOG = {k: v for k, v in HARDWARE_MODULE_DATABASE.items() if v["type"] == "pcb_module"}

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

    _SPEC_FIELDS = ("cpu", "ram", "gpu", "storage", "connectivity", "gpio", "video_output",
                    "power_draw", "form_factor", "interface", "resolution", "display_type",
                    "isa", "size", "capacity", "soc", "wifi", "ble", "ethernet", "usb",
                    "display", "camera", "pcie", "power", "tier")
    _CATEGORY_ALIASES = {"screen": "display", "kbd": "keyboard", "case": "enclosure",
                         "battery": "power", "fan": "cooling", "cable": "wire",
                         "wifi": "connectivity", "ssd": "storage", "sd": "storage"}

    @staticmethod
    def search(query, budget=None, category=None, sort="relevance", limit=10):
        """Search all component databases. Scores keyword hits across name, specs,
        use-cases and category. Supports budget/category filters and price sort.
        Enriches matches with the cheapest vendor + URL from PRICE_SOURCE_DATABASE."""
        ql = query.lower()
        tokens = [t for t in ql.split() if t]
        all_dbs = [("SBC", SBC_DATABASE), ("Display", DISPLAY_DATABASE),
                   ("Keyboard", KEYBOARD_DATABASE), ("Power", POWER_DATABASE),
                   ("Enclosure", ENCLOSURE_DATABASE), ("Cooling", COOLING_DATABASE),
                   ("PCB", PCB_DATABASE), ("Wire", WIRE_DATABASE),
                   ("Connectivity", CONNECTIVITY_DATABASE), ("Storage", STORAGE_DATABASE),
                   ("OS", OS_DATABASE), ("Sensor", ENVIRONMENTAL_SENSOR_DATABASE),
                   ("Camera", CAMERA_MODULE_DATABASE), ("SDR", SDR_DATABASE),
                   ("LoRa", LORA_MESH_DATABASE), ("NFC", NFC_RFID_DATABASE),
                   ("Fingerprint", FINGERPRINT_DATABASE), ("Haptic", HAPTIC_FEEDBACK_DATABASE),
                   ("IMU", IMU_DATABASE), ("uConsole Expansion", UCONSOLE_EXPANSION_DATABASE)]
        cat = category.strip().lower() if category else None
        results = []
        for db_name, db in all_dbs:
            if cat:
                want = ComponentDatabase._CATEGORY_ALIASES.get(cat, cat)
                if want not in db_name.lower():
                    continue
            for item_id, item in db.items():
                if not isinstance(item, dict):
                    continue
                nl = str(item.get("name", "")).lower()
                score = 0
                for t in tokens:
                    if t in nl:
                        score += 4
                    best_for = item.get("best_for", [])
                    if isinstance(best_for, list) and any(t in str(b).lower() for b in best_for):
                        score += 3
                    if t in db_name.lower():
                        score += 2
                    if any(t in str(item.get(f, "")).lower() for f in ComponentDatabase._SPEC_FIELDS):
                        score += 2
                    if isinstance(item.get("pros"), list) and any(t in str(p).lower() for p in item["pros"]):
                        score += 1
                if tokens and score <= 0:
                    continue
                price = None
                raw_price = item.get("price")
                if not isinstance(raw_price, (int, float, str)):
                    raw_price = item.get("price_range")
                if isinstance(raw_price, (int, float)):
                    price = float(raw_price)
                elif isinstance(raw_price, str):
                    nums = re.findall(r"\d+(?:\.\d+)?", raw_price)
                    if nums:
                        price = float(nums[0])
                vendor_price = None
                vendor_name = vendor_url = None
                for pk, pv in PRICE_SOURCE_DATABASE.items():
                    if pk.lower() in nl or nl in pk.lower():
                        cheapest = min(pv, key=lambda s: s.get("price", 0) + s.get("shipping", 0))
                        vendor_price = cheapest["price"] + cheapest.get("shipping", 0)
                        vendor_name = cheapest["vendor"]
                        vendor_url = cheapest.get("url")
                        break
                eff = None
                if price is not None or vendor_price is not None:
                    eff = min(x for x in (price, vendor_price) if x is not None)
                if budget is not None and eff is not None and eff > budget:
                    continue
                results.append({"type": db_name, "id": item_id, "name": item.get("name", "?"),
                                "price": price, "spec_line": ComponentDatabase._spec_line(item, db_name),
                                "score": score, "vendor": vendor_name, "vendor_price": vendor_price,
                                "vendor_url": vendor_url, "effective_price": eff})
        if sort == "price":
            results.sort(key=lambda r: (r["effective_price"] is None, r["effective_price"] or float("inf")))
        else:
            results.sort(key=lambda r: (-r["score"],
                                        r["effective_price"] if r["effective_price"] is not None else float("inf")))
        return results[:limit]

    @staticmethod
    def _spec_line(item, db_name):
        prefs = {"SBC": ("ram", "cpu"), "Display": ("size", "resolution", "interface"),
                 "Keyboard": ("layout", "switch", "size"), "Power": ("capacity", "voltage"),
                 "Storage": ("capacity", "interface"), "Camera": ("resolution", "interface"),
                 "Sensor": ("measure", "interface"), "Connectivity": ("standard", "interface")}
        for field in prefs.get(db_name, ("size", "resolution", "interface", "connectivity", "ram", "cpu")):
            v = item.get(field)
            if v and str(v).strip() and str(v) not in ("N/A", "None", "Depends on carrier"):
                return str(v)
        return ""

    @staticmethod
    def price_lookup(name):
        """Cheapest vendor + URL for a part, by fuzzy name match."""
        nl = name.lower()
        best = None
        for pk, pv in PRICE_SOURCE_DATABASE.items():
            if nl in pk.lower() or pk.lower() in nl:
                for s in pv:
                    total = s["price"] + s.get("shipping", 0)
                    if best is None or total < best["price"]:
                        best = {"vendor": s["vendor"], "price": total, "url": s.get("url")}
        return best

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
OBSIDIAN_VAULT_NAME = "CyberdeckBrain"
OBSIDIAN_NOTES_DIR = os.path.join(os.path.expanduser("~"), "Documents", "obsidian-vaults", "CyberdeckBrain", "AgentMemory")


def _obsidian_available():
    """Check if Obsidian CLI is available."""
    try:
        r = os.system("obsidian --help 2>nul >nul")
        return r == 0
    except Exception:
        return False


class ObsidianBrain:
    """Second agent brain — persists learnings as Obsidian notes.
    Every learning is auto-saved as a markdown note in the Obsidian vault,
    creating a persistent, searchable memory that survives agent restarts."""

    def __init__(self, vault_name=OBSIDIAN_VAULT_NAME):
        self.vault_name = vault_name
        self.available = _obsidian_available()
        self.notes_dir = OBSIDIAN_NOTES_DIR
        os.makedirs(self.notes_dir, exist_ok=True)

    def _write_note(self, title, content, tags=None):
        """Write a markdown note. Uses Obsidian CLI if available, else direct file write."""
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title).strip()[:100]
        safe_title = safe_title or "note"
        tags_line = ""
        if tags:
            tags_str = " ".join(f"#{t.replace(' ', '_')}" for t in tags)
            tags_line = f"\n{tags_str}\n"
        note = f"---\ncreated: {datetime.now().isoformat()}\n---\n\n# {title}{tags_line}\n\n{content}\n"
        path = os.path.join(self.notes_dir, f"{safe_title}.md")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(note)
            if self.available:
                os.system(f'start obsidian://open?vault={self.vault_name}&file=AgentMemory%2F{safe_title}')
            return path
        except Exception as e:
            logger.warning(f"ObsidianBrain write failed: {e}")
            return None

    def _search_notes(self, query):
        """Search notes content. Uses Obsidian CLI search if available."""
        if self.available:
            result = os.popen(f'obsidian search "{query}" 2>nul').read()
            return result.strip() if result else ""
        results = []
        try:
            for fname in os.listdir(self.notes_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(self.notes_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    if query.lower() in content.lower():
                        results.append(fname.replace(".md", ""))
        except Exception:
            pass
        return "\n".join(results) if results else ""

    def learn_video(self, title, url, key_points, components):
        """Save video learning as Obsidian note."""
        tags = ["video", "learning"] + [f"comp_{c.replace(' ', '_')}" for c in components[:5]]
        content = (
            f"## Video\n\n**Title:** {title}\n"
            f"**URL:** {url}\n"
            f"**Learned:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"### Key Points\n" + "\n".join(f"- {kp}" for kp in key_points) + "\n\n"
            f"### Components Found\n" + "\n".join(f"- {c}" for c in components) + "\n"
        )
        return self._write_note(f"Video: {title[:80]}", content, tags)

    def learn_chat(self, user_message, agent_response, context="general"):
        """Save chat learning as Obsidian note."""
        tags = ["chat", "learning", context]
        content = (
            f"## Chat Interaction\n\n"
            f"**Context:** {context}\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"### User Said\n> {user_message[:500]}\n\n"
            f"### Agent Responded\n> {agent_response[:500]}\n"
        )
        return self._write_note(f"Chat: {context} {datetime.now().strftime('%Y%m%d_%H%M')}", content, tags)

    def learn_build(self, build_data):
        """Save build as Obsidian note."""
        name = build_data.get("name", "build") if isinstance(build_data, dict) else "build"
        tags = ["build", "cyberdeck", build_data.get("tier", "general") if isinstance(build_data, dict) else "general"]
        content = (
            f"## Build Record\n\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"```json\n{json.dumps(build_data, indent=2, default=str)[:2000]}\n```\n"
        )
        return self._write_note(f"Build: {name[:80]}", content, tags)

    def learn_insight(self, insight_text, insight_type="tip"):
        """Save a general insight/tip as Obsidian note."""
        tags = [insight_type, "insight"]
        content = (
            f"## {insight_type.title()}\n\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"{insight_text}\n"
        )
        safe_title = insight_text[:80].rstrip(". ")
        return self._write_note(f"{insight_type.title()}: {safe_title}", content, tags)

    def daily_summary(self):
        """Generate a daily summary note of all learnings."""
        today = datetime.now().strftime('%Y-%m-%d')
        tags = ["daily", "summary"]
        content = (
            f"# Agent Daily Summary — {today}\n\n"
            f"_Automatically generated by CyberdeckAgent ObsidianBrain_\n\n"
            f"## Today's Learnings\n\n"
            f"Check individual notes in this folder for details.\n\n"
            f"---\n*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        )
        return self._write_note(f"Daily Summary {today}", content, tags)

    def search_memory(self, query):
        """Search across all memory notes."""
        return self._search_notes(query)

    def get_stats(self):
        """Get stats about stored memories."""
        try:
            notes = [f for f in os.listdir(self.notes_dir) if f.endswith(".md")]
            return {"notes_count": len(notes), "notes_dir": self.notes_dir, "available": self.available}
        except Exception:
            return {"notes_count": 0, "notes_dir": self.notes_dir, "available": self.available}


class CyberdeckLearner:
    def __init__(self):
        self.file = LEARNINGS_FILE
        self.learnings = self._load()
        self.obsidian = ObsidianBrain()

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
        self.obsidian.learn_video(title, url, key_points, components)

    def learn_from_chat(self, user_message, bot_response, context="general"):
        entry = {"user_message": user_message[:500], "bot_response": bot_response[:500],
                 "context": context, "learned_at": datetime.now().isoformat()}
        self.learnings["chat_learnings"].append(entry)
        if len(self.learnings["chat_learnings"]) > 500:
            self.learnings["chat_learnings"] = self.learnings["chat_learnings"][-500:]
        self._save()
        self.obsidian.learn_chat(user_message[:500], bot_response[:500], context)

    def learn_from_build(self, build):
        entry = {"build": build, "learned_at": datetime.now().isoformat()}
        self.learnings["build_insights"].append(entry)
        self._save()
        self.obsidian.learn_build(build)

    def log_flaw_fix(self, flaw, fix):
        self.learnings["flaws_fixed"].append(
            {"flaw": flaw, "fix": fix, "fixed_at": datetime.now().isoformat()})
        self._save()
        self.obsidian.learn_insight(f"Flaw: {flaw}\nFix: {fix}", "flaw_fix")

    def log_evolution(self, what_changed):
        self.learnings["evolution_log"].append(
            {"change": what_changed, "at": datetime.now().isoformat()})
        self._save()
        self.obsidian.learn_insight(f"Evolution: {what_changed}", "evolution")

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
                           "4. Connect BMS output to SBC power input via correct gauge wire.",
                           "",
                           "   **Soldering 18650 cells (if not using spot welder):**",
                           "   - Clean terminals with isopropyl alcohol",
                           "   - Apply flux, tin terminals quickly (max 3s at 350°C)",
                           "   - Let cool completely between welds",
                           "   - Insulate with kapton tape + heat shrink",
                           "   ⚠ NEVER short terminals. Spot welding is safer.",
                           "   🎥 Tutorial: https://youtube.com/watch?v=DS6qReI1LbI"])
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
        {"title": "The Minimalist Writer", "category": "writerdeck", "description": "Pi Zero 2W + 4.2\" e-ink + Planck ortho. 3D-printed clamshell.", "difficulty": "beginner", "estimated_cost": "$150", "material": "PETG", "post_processing": "vapor_smoothing"},
        {"title": "The Field Hacker", "category": "security", "description": "Pi 5 16GB + 7\" touch + Kali + AWUS036ACH + HackRF SDR. Ruggedized 3D enclosure.", "difficulty": "intermediate", "estimated_cost": "$800", "material": "PA-CF", "post_processing": "superhydrophobic_nano"},
        {"title": "The Retro Arcade", "category": "gaming", "description": "Pi 5 8GB + 7\" HDMI + RetroPie + USB controllers + Pelican-style case.", "difficulty": "beginner", "estimated_cost": "$250", "material": "PETG", "post_processing": ""},
        {"title": "The AI Terminal", "category": "ai", "description": "Jetson Orin Nano + 10\" HDMI + NVMe + active cooling + 40 TOPS local AI.", "difficulty": "advanced", "estimated_cost": "$1200", "material": "PC-CF", "post_processing": ""},
        {"title": "The Off-Grid Comms", "category": "survival", "description": "Pi 5 + e-ink + LoRa + ham radio + solar + 6x 18650. Waterproof IP65.", "difficulty": "advanced", "estimated_cost": "$700", "material": "PA12-CF", "post_processing": "waterproof_bundle"},
        {"title": "The Dual-Screen Dev", "category": "coding", "description": "Pi 5 16GB + 7\" main + 5\" OLED status + Planck + NVMe + custom 3D case.", "difficulty": "advanced", "estimated_cost": "$900", "material": "eASA", "post_processing": ""},
        {"title": "The Cinema Deck", "category": "media", "description": "Pi 5 + 10.5\" HDMI + speakers + IR remote + LibreELEC. Wall-mountable dock.", "difficulty": "beginner", "estimated_cost": "$300", "material": "ABS+", "post_processing": "vapor_smoothing"},
        {"title": "The Cyberpunk Prop", "category": "conversation-piece", "description": "Zero 2W + OLED + neon LEDs + transparent case + mechanical keyboard.", "difficulty": "intermediate", "estimated_cost": "$400", "material": "Resin", "post_processing": ""},
        {"title": "The Research Station", "category": "research", "description": "Pi 5 8GB + sunlight-readable 10\" + NVMe + 6x 18650 + offline Wikipedia.", "difficulty": "intermediate", "estimated_cost": "$600", "material": "ASA", "post_processing": ""},
        {"title": "The Recovery Kit", "category": "coding", "description": "Pi 5 + 7\" touch + Planck + Ethernet switch + UPS HAT + Pelican 1450.", "difficulty": "advanced", "estimated_cost": "$850", "material": "ABS-GF", "post_processing": "gasket_kit"},
        {"title": "The Penkesu Computer", "category": "writerdeck", "description": "Pi Zero 2W + 7.5\" e-ink + split mechanical + GBA SP hinges. 3D-printed lid.", "difficulty": "intermediate", "estimated_cost": "$350", "material": "PETG", "post_processing": ""},
        {"title": "The Chonky Palmtop", "category": "coding", "description": "Pi 5 + 7\" touch + Corne split on pivot + NVMe + dual fans + 3D chassis.", "difficulty": "advanced", "estimated_cost": "$1000", "material": "Polycarbonate", "post_processing": ""},
        {"title": "The Cyberdore 2064", "category": "conversation-piece", "description": "Zero 2W + OLED 128x64 + rotary encoder + mechanical switches + ammo box.", "difficulty": "beginner", "estimated_cost": "$200", "material": "PETG", "post_processing": ""},
        {"title": "The Tactical Wedge", "category": "security", "description": "Pi 5 + wedge-angled 3D case + Kali + external antenna array + GPIO switches.", "difficulty": "advanced", "estimated_cost": "$750", "material": "PA-CF", "post_processing": "superhydrophobic_nano"},
        {"title": "The Bumble Budget", "category": "gaming", "description": "Orange Pi Zero 3 + 5\" HDMI + RetroPie + $30 3D-printed enclosure.", "difficulty": "beginner", "estimated_cost": "$120", "material": "PLA", "post_processing": ""},
        {"title": "The Ham Shack", "category": "ham-radio", "description": "Pi 5 + HackRF + RTL-SDR + 7\" + 3D case + 18650 pack + antenna mounts.", "difficulty": "advanced", "estimated_cost": "$900", "material": "eASA", "post_processing": ""},
        {"title": "The Maker's Bench", "category": "maker", "description": "Pi 5 + 7\" touch + Qwiic HAT + Logic Analyzer + UPS + 3D tool holder.", "difficulty": "intermediate", "estimated_cost": "$500", "material": "PETG", "post_processing": ""},
        {"title": "The Field Surgeon", "category": "field-repair", "description": "Pi 5 + 5\" HDMI + Rii combo + Pelican 1200 + USB multimeter + Ethernet.", "difficulty": "intermediate", "estimated_cost": "$450", "material": "ABS+", "post_processing": "gasket_kit"},
        {"title": "The Retro Terminal", "category": "retro", "description": "Pi Zero 2W + 4.2\" amber e-ink + Model M + wood/brass enclosure.", "difficulty": "intermediate", "estimated_cost": "$250", "material": "PLA", "post_processing": "vapor_smoothing"},
        {"title": "The MeshNode", "category": "survival", "description": "Pi 5 + e-ink + 3x LoRa + LTE modem + solar + Pelican 1450. Full waterproof.", "difficulty": "advanced", "estimated_cost": "$800", "material": "PA12-CF", "post_processing": "waterproof_bundle"},
        {"title": "The Obsidian Brain", "category": "ai", "description": "Pi 5 8GB + 7\" touch + NVMe + local LLM (Llama 3B) + Obsidian vault for persistent agent memory. Learns daily.", "difficulty": "advanced", "estimated_cost": "$650", "material": "PC-CF", "post_processing": "conformal_coating"},
        {"title": "The Weatherproof Watchdog", "category": "survival", "description": "Pi 5 + 5\" sunlight-readable + LoRa + temp/humidity sensors + solar MPPT. IP67.", "difficulty": "intermediate", "estimated_cost": "$550", "material": "PA-CF", "post_processing": "waterproof_bundle"},
        {"title": "The Digital Nomad", "category": "writerdeck", "description": "Pi 5 + 10\" e-ink panel + Planck + 8x 18650 + 3D-printed slim clamshell. 20h battery.", "difficulty": "intermediate", "estimated_cost": "$500", "material": "PETG-CF", "post_processing": ""},
        {"title": "The SDR Station", "category": "ham-radio", "description": "Pi 5 + 10\" HDMI + HackRF + Airspy + upconverter + 3D antenna mount rack.", "difficulty": "expert", "estimated_cost": "$1500", "material": "eASA", "post_processing": ""},
        {"title": "The Server Blade", "category": "coding", "description": "Pi 5 16GB + NVMe + 2.5G Ethernet + OLED stats + rackmount 3D tray. Headless server.", "difficulty": "intermediate", "estimated_cost": "$400", "material": "ABS-GF", "post_processing": ""},
        {"title": "The Ghost Deck", "category": "security", "description": "Pi Zero 2W + 3.5\" touch + LoRa + GPS + encrypted mesh + stealth 3D case. No WiFi/BT.", "difficulty": "expert", "estimated_cost": "$500", "material": "PA-CF", "post_processing": "superhydrophobic_nano"},
        {"title": "The Ultra-Temp Probe", "category": "research", "description": "Pi 5 + PEEK 3D-printed enclosure (250°C rated) + thermal cameras + sensors for industrial logging.", "difficulty": "expert", "estimated_cost": "$2000", "material": "PEEK", "post_processing": ""},
        {"title": "The Titanium Rugged", "category": "security", "description": "Pi 5 + DMLS titanium enclosure (1668°C melt) + sapphire display window. MIL-spec.", "difficulty": "expert", "estimated_cost": "$5000", "material": "Titanium_Ti64", "post_processing": "ceramic_coating"},
        {"title": "The Ceramic Server", "category": "ai", "description": "Pi 5 + ceramic SLA enclosure (1600°C rated) + passive cooling. Server-room grade.", "difficulty": "expert", "estimated_cost": "$1500", "material": "Ceramic_Alumina", "post_processing": ""},
        {"title": "The Nylon Beast", "category": "gaming", "description": "Pi 5 16GB + 10\" 120Hz + Hall-effect analog sticks + PA12-CF enclosure. Drop-proof.", "difficulty": "advanced", "estimated_cost": "$1100", "material": "PA12-CF", "post_processing": ""},
        {"title": "The Modular Tactical Deck", "category": "security", "description": "Pi 5 + NATO rail frame + sliding screen + NP-F battery sled + Lil PCB SDR/LoRa modules. Full hot-swappable modular system.", "difficulty": "advanced", "estimated_cost": "$1200", "material": "PA-CF", "post_processing": "waterproof_bundle", "hardware": ["nato_deluxe_bundle", "sliding_screen_kit", "npf_battery_sled_dual", "lilpcb_backplane", "lilpcb_sdr", "lilpcb_lora"]},
        {"title": "The Hot-Swap Writerdeck", "category": "writerdeck", "description": "Pi Zero 2W + e-ink 7\" + Planck + NP-F battery sled (hot-swap 9200mAh) + 3D-printed clamshell with sliding screen.", "difficulty": "intermediate", "estimated_cost": "$450", "material": "PETG-CF", "post_processing": "", "hardware": ["npf_battery_sled", "sliding_screen_kit"]},
        {"title": "The Field Lab", "category": "research", "description": "Pi 5 + Lil PCB backplane + SDR + GPS + LoRa + env sensor + NP-F dual sled + sliding 10\" display. Full field research station that fits in a backpack.", "difficulty": "expert", "estimated_cost": "$1500", "material": "PC-CF", "post_processing": "waterproof_bundle", "hardware": ["lilpcb_backplane", "lilpcb_sdr", "lilpcb_gps", "lilpcb_lora", "lilpcb_env_sensor", "npf_battery_sled_dual", "sliding_screen_kit"]},
        {"title": "The Rail Gunner", "category": "coding", "description": "Pi 5 16GB + 7\" + mechanical keyboard + NATO rail frame + QD sling mount + NP-F sled. Carry it like a briefcase, deploy anywhere.", "difficulty": "intermediate", "estimated_cost": "$800", "material": "eASA", "post_processing": "superhydrophobic_nano", "hardware": ["nato_rail_set", "nato_deluxe_bundle", "npf_battery_sled"]},
        {"title": "The SDR Scanner", "category": "ham-radio", "description": "Pi 5 + Lil PCB SDR module + LoRa module + GPS module + NP-F dual sled + 10\" display. Multi-band RF scanner in a hot-swap modular frame.", "difficulty": "advanced", "estimated_cost": "$1000", "material": "ABS-GF", "post_processing": "", "hardware": ["lilpcb_backplane", "lilpcb_sdr", "lilpcb_lora", "lilpcb_gps", "npf_battery_sled_dual"]},
        {"title": "The AI Slider", "category": "ai", "description": "Jetson Orin Nano + HD sliding screen (15\" 120Hz) + Lil PCB NVMe module + NP-F dual + CNC aluminum carriage. AI workstation that slides closed for transport.", "difficulty": "expert", "estimated_cost": "$2500", "material": "PC-CF", "post_processing": "", "hardware": ["sliding_screen_heavyduty", "lilpcb_backplane", "lilpcb_nvme", "npf_battery_sled_dual"]},
        {"title": "The Tactical Grey Man", "category": "survival", "description": "Pi 5 + NATO rail frame (disguised as briefcase) + Lil PCB LoRa/GPS/env + NP-F hot-swap + solar input. Low-profile off-grid mesh node.", "difficulty": "advanced", "estimated_cost": "$900", "material": "PA12-CF", "post_processing": "waterproof_bundle", "hardware": ["nato_rail_set", "lilpcb_backplane", "lilpcb_lora", "lilpcb_gps", "npf_battery_sled"]},
        {"title": "The RISC-V Pioneer", "category": "coding", "description": "Orange Pi RV2 16GB + 7\" HDMI + open-source ISA + NVMe + RISC-V native toolchain. First open-ISA portable dev station.", "difficulty": "advanced", "estimated_cost": "$400", "material": "eASA", "post_processing": ""},
        {"title": "The x86 Pelican Brick", "category": "coding", "description": "LattePanda μ + 7\" 1080p touch + Pelican 1200 + NVMe + 6x 18650. Full Windows/Linux x86 deck that fits in a hard case.", "difficulty": "advanced", "estimated_cost": "$900", "material": "ABS-GF", "post_processing": "gasket_kit"},
        {"title": "The Solar E-Ink Writer", "category": "writerdeck", "description": "Pi Zero 2W + 7.5\" e-ink + solar MPPT charger + 5000mAh LiPo + slim 3D-printed clamshell. Write all day off sunlight.", "difficulty": "intermediate", "estimated_cost": "$350", "material": "PETG-CF", "post_processing": ""},
        {"title": "The HexaScreen Station", "category": "coding", "description": "3x Pi 5 8GB + 6x 5.5\" displays folded into one unit + modular 3D frame + 3x 26500mAh power banks. Split into three dual-display laptops.", "difficulty": "expert", "estimated_cost": "$1800", "material": "PC-CF", "post_processing": ""},
        {"title": "The Lunchbox Ghost", "category": "conversation-piece", "description": "Pi 5 + 7\" HDMI + 75% mech keyboard + 4x 18650 + hidden in 80s M.A.S.K. lunchbox. Opens to reveal a full deck.", "difficulty": "intermediate", "estimated_cost": "$400", "material": "PETG", "post_processing": ""},
        {"title": "The Pocket Mesh", "category": "survival", "description": "Pi Zero 2W + 3.5\" DPI touch + LTE modem + Meshtastic LoRa + 5000mAh. Fits in a jacket pocket. Off-grid handheld.", "difficulty": "intermediate", "estimated_cost": "$300", "material": "PA-CF", "post_processing": "waterproof_bundle"},
        {"title": "The Instant Writer", "category": "writerdeck", "description": "ESP32-S3 + 2.8\" ILI9341 LCD + hand-wired 30% ortho + boots in 1s. Micro Journal style distraction-free writer.", "difficulty": "advanced", "estimated_cost": "$120", "material": "PLA", "post_processing": ""},
        {"title": "The NPU Vision Deck", "category": "edge-ai", "description": "Pi 5 + AI HAT+ (26 TOPS) + camera module + 7\" display + OpenCV. Real-time object detection at the edge.", "difficulty": "advanced", "estimated_cost": "$500", "material": "eASA", "post_processing": "conformal_coating"},
        {"title": "The AMOLED Writer", "category": "writerdeck", "description": "Pi Zero 2W + 5.5\" AMOLED + Air40 low-profile mech + slim clamshell purse case. Inspired by Bee Write Back.", "difficulty": "intermediate", "estimated_cost": "$300", "material": "Resin", "post_processing": ""},
        {"title": "The Cyber Grrrl", "category": "conversation-piece", "description": "Pi 5 + 7\" touch + lavender/quilted fabric enclosure + pink LED underglow + embroidered bezel. Soft aesthetic cyberdeck.", "difficulty": "beginner", "estimated_cost": "$350", "material": "PETG", "post_processing": ""},
        {"title": "The Macro Pad Companion", "category": "maker", "description": "Pi Zero 2W + 1.3\" OLED + 4x rotary encoders + 20x mechanical switches. USB macro pad meets standalone cyberdeck.", "difficulty": "beginner", "estimated_cost": "$100", "material": "PLA", "post_processing": ""},
        {"title": "The Don't Panic Deck", "category": "coding", "description": "Pi 5 8GB + 7\" HDMI + Planck + 3D-printed handle case + 6x 18650. Approachable starter build inspired by Paul Rickards.", "difficulty": "beginner", "estimated_cost": "$450", "material": "PETG", "post_processing": ""},
        {"title": "The RISC-V Terminal", "category": "coding", "description": "Orange Pi RV2 + 5\" HDMI + compact mech + 2x LoRa + NVMe. Pocket RISC-V developer terminal for on-the-go coding.", "difficulty": "intermediate", "estimated_cost": "$350", "material": "eASA", "post_processing": ""},
        {"title": "The Foldable Duo", "category": "research", "description": "2x Pi 5 4GB + 2x 5.5\" displays + hinge frame that splits into two independent decks. Share one, keep one.", "difficulty": "expert", "estimated_cost": "$1400", "material": "PC-CF", "post_processing": ""},
        {"title": "The HackberryPi Handheld", "category": "coding", "description": "CM5 + 4\" 720p display + BlackBerry QWERTY keyboard + aluminum chassis + 5000mAh. All-metal pocket Linux handheld.", "difficulty": "advanced", "estimated_cost": "$600", "material": "eASA", "post_processing": ""},
        {"title": "The uConsole Rig", "category": "coding", "description": "CM5 core + 5\" 1280x720 IPS + integrated speakers + 6000mAh battery. Off-shelf cyberdeck kit turned to daily driver.", "difficulty": "beginner", "estimated_cost": "$280", "material": "PETG", "post_processing": ""},
        {"title": "The x86 LattePanda Palmtop", "category": "coding", "description": "LattePanda μ + 7\" 1080p touch + aluminum faceplate + resin shell + 36mm thin enclosure. True x86 handheld.", "difficulty": "expert", "estimated_cost": "$700", "material": "PC-CF", "post_processing": ""},
        {"title": "The Don't Panic 3A", "category": "writing", "description": "Pi 3A+ + HyperPixel 4.0 Square + 3D-printed handle case + hand-wired ortho. Towel not included.", "difficulty": "beginner", "estimated_cost": "$250", "material": "PETG", "post_processing": ""},
        {"title": "The Dinodeck Rover", "category": "survival", "description": "Pi Zero 2W + LTE + Meshtastic LoRa + 5\" DPI touch + thrifted toy enclosure. Open-source field comms deck.", "difficulty": "intermediate", "estimated_cost": "$250", "material": "PLA", "post_processing": ""},
        {"title": "The Reviiser Luggable", "category": "research", "description": "Pi 4 + 7\" e-ink main + 7\" OLED status + 30Ah battery bank + Pelican 1450. Week-long field research station.", "difficulty": "advanced", "estimated_cost": "$600", "material": "ABS-GF", "post_processing": "gasket_kit"},
        {"title": "The Sprawl Hosaka", "category": "coding", "description": "Pi 5 + 7\" HDMI + Planck + 3D-printed clamshell + 18650 pack. Fully printable cyberdeck inspired by Neuromancer.", "difficulty": "intermediate", "estimated_cost": "$400", "material": "eASA", "post_processing": ""},
        {"title": "The Termyte Pocket Deck", "category": "security", "description": "Orange Pi Zero 3 + 3.5\" touch + Rii mini keyboard + 18650 + slim 3D case. Fits in a cargo pocket.", "difficulty": "beginner", "estimated_cost": "$150", "material": "PETG-CF", "post_processing": ""},
        {"title": "The Banana Pi Build Station", "category": "coding", "description": "Banana Pi BPI-M4 Super + 10\" 1920x1200 + NVMe + 2.5GbE + 8x 18650. RK3588 NAS-capable coding deck.", "difficulty": "advanced", "estimated_cost": "$600", "material": "eASA", "post_processing": ""},
        {"title": "The DSI Ultra-Slim Writer", "category": "writerdeck", "description": "CM5 carrier + 8\" DSI IPS touch + Chocofi split (wireless ZMK) + 21700 UPS HAT. Frees the HDMI port for a dock.", "difficulty": "advanced", "estimated_cost": "$650", "material": "PETG-CF", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_8inch_waveshare", "chocofi", "geekworm_x733"]},
        {"title": "The Ultrawide Terminal", "category": "coding", "description": "CM5 + 11.9\" DSI ultrawide (1920x480) + Planck + NVMe. One window for code, one for terminal — no bezels.", "difficulty": "intermediate", "estimated_cost": "$700", "material": "ABS-GF", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_11_9_ultrawide", "planck"]},
        {"title": "The Voyager Road Case", "category": "writerdeck", "description": "Pi 5 + 13.3\" DSI full HD + ZSA Voyager + Geekworm X733. A briefcase writerdeck with a proper split board.", "difficulty": "advanced", "estimated_cost": "$1200", "material": "PC-CF", "post_processing": "", "hardware": ["dsi_13_3_waveshare", "voyager", "geekworm_x733"]},
        {"title": "The Field Surgeon II", "category": "field-repair", "description": "Pi 5 + 5\" DSI touch + Pichondria PD 20000 pack + USB multimeter + Lil PCB SDR. Fits a Pelican 1200 with room for tools.", "difficulty": "intermediate", "estimated_cost": "$550", "material": "ABS+", "post_processing": "gasket_kit", "hardware": ["dsi_5inch_waveshare", "pichondria_pd_20000", "lilpcb_sdr"]},
        {"title": "The Hackberry CM5 Clone", "category": "coding", "description": "CM5 + 4\" DSI square touch + BlackBerry keyboard + 21700 cell + aluminum. All-metal palm-top inspired by HackberryPi.", "difficulty": "expert", "estimated_cost": "$500", "material": "Resin", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_4inch_capacitive"]},
        {"title": "The 30Ah Field Deck", "category": "survival", "description": "Pi 5 + 7\" DSI Touch 2 + Pichondria PD 30000 brick + Meshtastic LoRa + GPS. Multi-day off-grid comms on one charge.", "difficulty": "advanced", "estimated_cost": "$800", "material": "PA12-CF", "post_processing": "waterproof_bundle", "hardware": ["dsi_7inch_touch2", "pichondria_pd_30000"]},
        {"title": "The Iris Mesh Node", "category": "survival", "description": "Pi Zero 2W + 5\" DSI + Iris split + solar MPPT + 21700. A hot-swap powered mesh endpoint you can type on.", "difficulty": "advanced", "estimated_cost": "$500", "material": "PA-CF", "post_processing": "waterproof_bundle", "hardware": ["dsi_5inch_waveshare", "iris"]},
        {"title": "The Media Slab", "category": "media", "description": "CM5 + 13.3\" DSI + 2x speakers + IR remote + Pichondria PD trigger. A flat, wall-mountable, battery-backed media slab.", "difficulty": "beginner", "estimated_cost": "$450", "material": "PETG", "post_processing": "vapor_smoothing", "hardware": ["cm5_carrier_dsi", "dsi_13_3_waveshare", "pichondria_pd_trigger"]},
        {"title": "The Kyria Writer", "category": "writerdeck", "description": "Pi 5 + 7\" DSI + Kyria split (encoders for volume) + Geekworm X728. A writing deck built around the best thumb clusters.", "difficulty": "intermediate", "estimated_cost": "$650", "material": "eASA", "post_processing": "", "hardware": ["dsi_7inch_touch2", "kyria", "geekworm_x728"]},
        {"title": "The Redox Comms Rig", "category": "ham-radio", "description": "Pi 5 + 10.1\" DSI + Redox 76-key + HackRF + 21700 UPS. Full-size keys for full-size QSO logging in the field.", "difficulty": "advanced", "estimated_cost": "$950", "material": "ABS-GF", "post_processing": "", "hardware": ["dsi_10_1_waveshare", "redox", "geekworm_x733"]},
        {"title": "The Ghost Splitter", "category": "security", "description": "Pi Zero 2W + 5\" DSI + Ferris Sweep + LTE + GPS + stealth matte case. No WiFi/BT, typed on the lightest split board alive.", "difficulty": "expert", "estimated_cost": "$450", "material": "PA-CF", "post_processing": "superhydrophobic_nano", "hardware": ["dsi_5inch_waveshare", "ferris_sweep"]},
        {"title": "The Desk Dock Writer", "category": "writerdeck", "description": "CM5 carrier + 7\" DSI Touch 2 + Pteron36 + X733 UPS, plus a HDMI dock pass-through. Undock to a big monitor, dock to write.", "difficulty": "intermediate", "estimated_cost": "$700", "material": "PETG-CF", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_7inch_touch2", "pteron36", "geekworm_x733"]},
        {"title": "The Livestream Deck", "category": "media", "description": "CM5 + 10.1\" DSI + camera + Pichondria PD 20000 + vlog handle. A battery-backed streaming rig on a CM5 carrier.", "difficulty": "advanced", "estimated_cost": "$800", "material": "eASA", "post_processing": "conformal_coating", "hardware": ["dsi_10_1_waveshare", "pichondria_pd_20000"]},
        {"title": "The Logistics Tablet", "category": "maker", "description": "CM5 + 8\" DSI touch + Qwiic HAT + 21700 UPS + barcode scanner. A warehouse/deck tablet for makerspaces.", "difficulty": "intermediate", "estimated_cost": "$600", "material": "ABS-GF", "post_processing": "", "hardware": ["dsi_8inch_waveshare", "geekworm_x733"]},
        {"title": "The PicoWriter 42", "category": "writerdeck", "description": "CM5 + 4\" DSI + Corne on Choc + 21700 cell. A 42-key ultraportable that boots straight to a text editor.", "difficulty": "advanced", "estimated_cost": "$500", "material": "PLA", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_4inch_capacitive", "corne"]},
        {"title": "The Ambulatory AI", "category": "ai", "description": "Pi 5 + AI HAT+ + 10.1\" DSI + Pichondria PD 30000 + camera. A walking local-LLM/vision companion that lasts a day.", "difficulty": "expert", "estimated_cost": "$1100", "material": "PC-CF", "post_processing": "conformal_coating", "hardware": ["dsi_10_1_waveshare", "pichondria_pd_30000"]},
        {"title": "The Sofle Server Control", "category": "coding", "description": "Pi 5 + 7\" DSI + Sofle (encoders + OLED for CPU/mem) + X728 UPS. A control deck for a home server rack.", "difficulty": "intermediate", "estimated_cost": "$700", "material": "ABS-GF", "post_processing": "", "hardware": ["dsi_7inch_touch2", "sofle", "geekworm_x728"]},
        {"title": "The Travel Terminal", "category": "coding", "description": "CM5 + 5\" DSI + Voyager + Pichondria PD trigger on a 10Ah pack. Airline-tray friendly SSH terminal.", "difficulty": "intermediate", "estimated_cost": "$600", "material": "PETG", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_5inch_waveshare", "voyager", "pichondria_pd_trigger"]},
        {"title": "The Kitchen Command", "category": "conversation-piece", "description": "CM5 + 7\" DSI Touch 2 + recessed mount + 21700 UPS + touch UI. A battery-backed wall panel with a hidden SD slot.", "difficulty": "beginner", "estimated_cost": "$400", "material": "PETG", "post_processing": "", "hardware": ["cm5_carrier_dsi", "dsi_7inch_touch2", "geekworm_x733"]},
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
    def search(query, budget=None, skill=None, limit=5):
        """Free-text search over BASE_IDEAS (title/description/category/material),
        with optional budget ($) and skill (beginner..expert) filters. Pure local,
        offline-safe; relevance = title/category hits count 3x, body/material 1x."""
        terms = [t for t in re.findall(r"[a-z0-9]+", (query or "").lower()) if t]
        if not terms:
            return IdeaGenerator.generate(category=None, budget=budget,
                                          skill=skill)[:limit]
        skill_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
        max_level = skill_order.get(skill, 2) if skill else None
        scored = []
        for idea in IdeaGenerator.BASE_IDEAS:
            if budget is not None and IdeaGenerator._parse_cost(
                    idea.get("estimated_cost", "$500")) > budget * 1.2:
                continue
            if max_level is not None and skill_order.get(
                    idea.get("difficulty", ""), 0) > max_level:
                continue
            title = (idea.get("title", "") or "").lower()
            desc = (idea.get("description", "") or "").lower()
            cat = (idea.get("category", "") or "").lower()
            mat = (idea.get("material", "") or "").lower()
            score = 0
            for t in terms:
                if t in title or t in cat:
                    score += 3
                elif t in desc:
                    score += 1
                elif t in mat:
                    score += 1
            if score > 0:
                scored.append((score, idea))
        scored.sort(key=lambda x: (-x[0], IdeaGenerator._parse_cost(
            x[1].get("estimated_cost", "$500"))))
        return [idea for _, idea in scored[:limit]]

    @staticmethod
    def generate_from_trends(learner, category=None):
        ideas = IdeaGenerator.generate(category)
        trends = learner.get_trends()
        if trends:
            recent = [t["trend"] for t in trends[-10:]]
            for idea in ideas:
                idea["trending_context"] = recent[:3]
        return ideas

    @staticmethod
    def generate_ideas(user_preferences: Dict = None) -> List[Dict]:
        """Legacy compat: filter by user preferences."""
        ideas = IdeaGenerator.generate()
        if user_preferences:
            pref_style = user_preferences.get("style")
            pref_category = user_preferences.get("category")
            if pref_style:
                ideas = [i for i in ideas if i.get("style", "").lower() == pref_style.lower()]
            if pref_category:
                ideas = [i for i in ideas if i.get("category", "").lower() == pref_category.lower()]
        return ideas


# ============================================================
# HARDWARE MODULE GENERATORS — NATO rails, sliding screens, NP-F batteries, Li'l PCB
# ============================================================
class HardwareModuleGenerator:
    """Generates hardware module specs for cyberdeck builds.
    Covers NATO rail systems, sliding screen mechanisms, NP-F battery sleds,
    and the Li'l PCB hot-swappable module ecosystem."""

    @staticmethod
    def get_module(module_id):
        return HARDWARE_MODULE_DATABASE.get(module_id)

    @staticmethod
    def list_modules(module_type=None):
        if module_type:
            return {k: v for k, v in HARDWARE_MODULE_DATABASE.items() if v.get("type") == module_type}
        return dict(HARDWARE_MODULE_DATABASE)

    @staticmethod
    def list_module_types():
        types = set(v["type"] for v in HARDWARE_MODULE_DATABASE.values())
        return sorted(types)

    @staticmethod
    def generate_nato_layout(rail_count=3, style="standard"):
        """Generate a NATO rail layout plan for an enclosure."""
        rails = HardwareModuleGenerator.get_module("nato_rail_set")
        bundle = HardwareModuleGenerator.get_module("nato_deluxe_bundle")
        plan = [
            f"NATO Rail Layout ({rail_count} rails, {style} style)",
            "",
            f"Rail positions:",
            f"  1. Top: 10-slot center (for accessories/camera)",
            f"  2. Left side: 10-slot (for flashlight/tool mount)",
            f"  3. Right side: 10-slot (for antenna/expansion)",
        ]
        if rail_count >= 4:
            plan.append("  4. Bottom: 6-slot (for tripod/arm mount)")
        if rail_count >= 5:
            plan.append("  5. Front: 6-slot (for camera/sensor)")
        plan += [
            "",
            f"Hardware needed:",
            f"  M4 bolts: {rail_count * 4} (stainless steel, included in {bundle['name']})",
            f"  T-nuts: {rail_count * 4} (roll-in or drop-in type)",
            f"  Corner brackets: {min(rail_count * 2, 8)}",
            f"  Quick-release mounts: 2 (for sling/shoulder strap)",
            "",
            "Print NATO-compatible brackets from STL files:",
            "  - nato_rail_bracket.stl — M4 bolt-on rail section",
            "  - nato_rail_endcap.stl — rail end cap for clean finish",
            "",
            "Pro tips:",
            "  - Use thread-locker (Loctite blue) on all M4 bolts",
            "  - Leave 2mm gap between rails for accessory QD levers",
            "  - Aluminum rails can be anodized any color",
            "  - 3D-printed PETG-CF rails work but aluminum is stronger",
        ]
        return "\n".join(plan)

    @staticmethod
    def generate_sliding_screen_plan(screen_size_inches=7, heavy=False):
        """Generate sliding screen assembly plan."""
        kit = "sliding_screen_heavyduty" if heavy else "sliding_screen_kit"
        module = HARDWARE_MODULE_DATABASE.get(kit, {})
        max_scr = module.get("max_screen", "10\"")
        plan = [
            f"Sliding Screen Assembly Plan ({screen_size_inches}\" display)",
            "",
            f"Mechanism: {module.get('name', 'Standard')}",
            f"Max supported screen: {max_scr}",
            f"Weight capacity: {module.get('weight_g', 350)}g assembly",
            "",
            "Assembly order:",
            "  1. Mount linear rod brackets to enclosure frame (M3 bolts)",
            "  2. Slide linear bearings onto rods, then mount rods into brackets",
            "  3. Attach screen carriage plate to bearings",
            "  4. Mount display to carriage plate (VESA 75mm or custom)",
            "  5. Run display cables through cable chain",
            "  6. Mount cable chain between carriage and enclosure base",
            "  7. Test slide motion — should be smooth with no binding",
            "  8. Install locking mechanism (magnet or spring pin)",
            "",
            "Cable management:",
            "  - HDMI flat ribbon cable in cable chain",
            "  - USB-C touch cable alongside HDMI",
            "  - Leave 15% slack in chain for flex",
            "  - Use velcro ties inside chain, not zip ties",
            "",
            "Troubleshooting:",
            "  - Binding: Loosen rod brackets, retighten evenly",
            "  - Wobble: Add 3rd rod or use thicker bearings",
            "  - Cable pinch: Check chain routing at full extension",
        ]
        return "\n".join(plan)

    @staticmethod
    def generate_npf_battery_plan(dual=False):
        """Generate NP-F battery integration plan."""
        sled = "npf_battery_sled_dual" if dual else "npf_battery_sled"
        module = HARDWARE_MODULE_DATABASE.get(sled, {})
        cap = "18400mAh (2x NP-F970)" if dual else "9200mAh (1x NP-F970)"
        runtime = "12-18h" if dual else "6-9h"
        plan = [
            f"NP-F Battery Integration Plan ({cap} capacity)",
            "",
            f"Sled: {module.get('name', 'Standard')}",
            f"Output: {module.get('output', '5V/9V/12V')}",
            f"Estimated runtime: {runtime}",
            "",
            "Wiring:",
            "  1. Mount sled inside enclosure or on exterior via NATO rail",
            "  2. Connect USB-C PD board output to SBC power input",
            "  3. Wire OLED display to I2C (SDA/SCL) for voltage readout",
            "  4. If using dual sled, wire ideal diode OR-ing module",
            "",
            "Battery options (Shopee Indonesia):",
            "  - NP-F550 (2100mAh, 7.4V) — Rp 150k — compact",
            "  - NP-F750 (5200mAh, 7.4V) — Rp 250k — standard",
            "  - NP-F970 (9200mAh, 7.4V) — Rp 400k — max capacity",
            "",
            "Hot-swap procedure:",
            "  1. Deck stays on while swapping (super-cap buffer)",
            "  2. Remove depleted battery, insert fresh one",
            "  3. OLED updates voltage instantly",
            "  4. Hot-swap safe: ideal diode prevents backfeed",
        ]
        return "\n".join(plan)

    @staticmethod
    def generate_lilpcb_plan(modules=None):
        """Generate Li'l PCB module configuration plan."""
        if modules is None:
            modules = []
        plan = [
            "Li'l PCB Hot-Swappable Module Configuration",
            "",
            "Backplane: 4-slot carrier (I2C + 3.3V/5V + 2x GPIO + UART per slot)",
            f"Modules installed: {len(modules)}/4 slots",
            "",
        ]
        for i, mod_id in enumerate(modules[:4], 1):
            mod = HARDWARE_MODULE_DATABASE.get(mod_id, {})
            plan.append(f"  Slot {i}: {mod.get('name', mod_id)}")
            plan.append(f"    {mod.get('description', '')}")
            plan.append(f"    Weight: {mod.get('weight_g', '?')}g")
            if mod.get("frequency"):
                plan.append(f"    Frequency: {mod['frequency']}")
            if mod.get("range_km"):
                plan.append(f"    Range: {mod['range_km']}km")
            plan.append("")
        plan += [
            "I2C address map:",
            "  Slot 1: 0x76 (default)",
            "  Slot 2: 0x77 (address shift)",
            "  Slot 3: 0x59",
            "  Slot 4: 0x23",
            "",
            "GPIO allocation:",
            "  Slot 1-2 GPIO: GPIO17, GPIO27",
            "  Slot 3-4 GPIO: GPIO22, GPIO23",
            "  UART shared: GPIO14 (TX), GPIO15 (RX)",
            "",
            "3D-print backplane mount: lilpcb_backplane_mount.stl",
            "Fasten with M2.5 standoffs (included in backplane kit)",
        ]
        return "\n".join(plan)

    @staticmethod
    def total_module_cost(module_ids):
        total = 0.0
        details = []
        for mid in module_ids:
            mod = HARDWARE_MODULE_DATABASE.get(mid)
            if mod:
                total += mod.get("price", 0)
                details.append(f"  {mod['name']}: ${mod.get('price', 0):.2f}")
        return total, details


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

    def get_obsidian_brain(self):
        """Get the ObsidianBrain — second agent's persistent memory/knowledge engine."""
        return self.learner.obsidian

    def obsidian_daily_summary(self):
        """Generate daily summary of all learnings into Obsidian vault."""
        return self.learner.obsidian.daily_summary()

    def obsidian_search(self, query):
        """Search across all Obsidian memory notes."""
        return self.learner.obsidian.search_memory(query)

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
        if HAS_RUST:
            try:
                components = build.get("components", {})
                result = rust_generate_cable_plan(components)
                if result:
                    return {"cables": result, "source": "rust"}
            except Exception:
                pass
        return CableRouter.generate_routing_plan(build)

    async def generate_tutorial(self, build):
        return TutorialGenerator.generate(build)

    async def generate_pack(self, build):
        return PackGenerator.generate_pack(build)

    async def generate_3d_model(self, build, color=None, style=None):
        if HAS_RUST:
            try:
                sbc = build["components"].get("sbc", {})
                sbc_name = sbc.get("name", "Cyberdeck")
                w = build.get("width", 120)
                h = build.get("height", 40)
                d = build.get("depth", 90)
                result = rust_generate_3d_model(sbc_name, color or "black", style or "cyberpunk", w, h, d)
                if result:
                    return result
            except Exception:
                pass
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
    """Calculates antenna dimensions and cable losses for cyberdeck builds.
    Delegates to Zig (cyberdeck_zig.dll) when available, falls back to pure Python."""

    @staticmethod
    def _zig_result(frequency_mhz: float):
        if HAS_ZIG:
            try: return zig_antenna(frequency_mhz)
            except Exception: pass
        return None

    @staticmethod
    def calculate_wavelength(frequency_mhz: float) -> float:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z: return z["wavelength_cm"]
        return 29979.2458 / frequency_mhz

    @staticmethod
    def quarter_wave(frequency_mhz: float) -> float:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z: return z["quarter_wave_cm"]
        return AntennaCalculator.calculate_wavelength(frequency_mhz) / 4

    @staticmethod
    def half_wave(frequency_mhz: float) -> float:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z: return z["half_wave_cm"]
        return AntennaCalculator.calculate_wavelength(frequency_mhz) / 2

    @staticmethod
    def cable_loss_db(cable_type: str, frequency_mhz: float, length_m: float) -> float:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z:
            for c in z.get("cable_losses", []):
                if c["cable"].lower() == cable_type.lower():
                    return round(c["loss_db_per_m"] * length_m, 2)
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
    def cable_losses(frequency_mhz: float) -> list:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z: return z["cable_losses"]
        return [
            {"cable": "RG58", "loss_db_per_m": round(0.5 * math.sqrt(frequency_mhz / 100.0), 3)},
            {"cable": "LMR200", "loss_db_per_m": round(0.3 * math.sqrt(frequency_mhz / 100.0), 3)},
            {"cable": "LMR400", "loss_db_per_m": round(0.15 * math.sqrt(frequency_mhz / 100.0), 3)},
        ]

    @staticmethod
    def link_budget(power_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float,
                    cable_loss_db: float, frequency_mhz: float) -> Dict:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z:
            mz = zig_mesh(power_dbm, frequency_mhz, tx_gain_dbi, -100)
            if mz:
                return {
                    "free_space_loss_db": round(mz["path_loss_budget_db"] - power_dbm - tx_gain_dbi * 2 + 100, 2),
                    "total_link_budget_db": mz["path_loss_budget_db"],
                    "max_range_km": round(mz["distance_km"], 1),
                    "recommended": mz["path_loss_budget_db"] > 10,
                }
        free_space_loss = 32.45 + 20 * (frequency_mhz / 1000) + 20 * 10
        budget = power_dbm + tx_gain_dbi + rx_gain_dbi - cable_loss_db - free_space_loss
        return {
            "free_space_loss_db": round(free_space_loss, 2),
            "total_link_budget_db": round(budget, 2),
            "max_range_km": round(10 ** (budget / (10 * 2)), 1),
            "recommended": budget > 10,
        }

    @staticmethod
    def recommend_connector(frequency_mhz: float) -> str:
        z = AntennaCalculator._zig_result(frequency_mhz)
        if z: return z["connector"]
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
    """Calculates battery requirements for cyberdeck builds.
    Delegates to Zig (cyberdeck_zig.dll) when available, falls back to pure Python."""

    @staticmethod
    def calculate_18650_capacity(cells: int, voltage: float = 3.7, capacity_mah: float = 3500,
                                   efficiency: float = 0.9, load_watts: float = 10) -> Dict:
        if HAS_ZIG:
            try:
                z = zig_battery(cells, capacity_mah, voltage, load_watts)
                if z:
                    return {
                        "cells": z["cells"],
                        "voltage_nominal": z["voltage"],
                        "total_mah": z["total_mah"],
                        "total_wh": z["total_wh"],
                        "runtime_hours_5w": round(z["total_wh"] / 5, 1),
                        "runtime_hours_10w": round(z["total_wh"] / 10, 1),
                        "runtime_hours_15w": round(z["total_wh"] / 15, 1),
                        "weight_grams": z["weight_grams"],
                    }
            except Exception: pass
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
    def recommend_capacity(power_draw_w: float, runtime_hours: float, cells_available: int = 6,
                            cell_mah: float = 3500, cell_voltage: float = 3.7) -> Dict:
        needed_wh = power_draw_w * runtime_hours / 0.9
        cells_needed = max(1, -(-int(needed_wh // (cell_voltage * cell_mah / 1000))))
        return {
            "power_draw_w": power_draw_w,
            "runtime_hours": runtime_hours,
            "needed_wh": round(needed_wh, 2),
            "cells_recommended": cells_needed,
            "cells_available": cells_available,
            "sufficient": cells_needed <= cells_available,
            "total_wh_available": round(cells_available * cell_voltage * cell_mah / 1000 * 0.9, 2),
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
    "bbc_microbit_v2": {
        "name": "BBC micro:bit v2",
        "soc": "Nordic nRF52833", "cpu": "ARM Cortex-M4 @ 64MHz", "isa": "ARM Cortex-M4", "gpu": "None (MCU)",
        "ram": "128KB SRAM + 512KB Flash", "storage": "512KB Flash (built-in)",
        "wifi": "None", "ble": "Bluetooth 5.0", "ethernet": "None",
        "usb": "USB-C", "gpio": "19-pin edge connector (SPI, I2C, UART)",
        "display": "5x5 LED matrix", "camera": "None",
        "power": "USB-C or 3V battery",
        "price": "$20", "tier": "budget",
        "best_for": ["maker", "field_research", "home_automation"],
        "compatibility_note": "Microcontroller not Linux. 5x5 LED matrix + BLE + sensors. Great for education/Maker projects. MicroPython/CircuitPython/MakeCode.",
    },
    "esp32_devkitc": {
        "name": "ESP32-DevKitC V4 (ESP32-WROOM-32)",
        "soc": "ESP32-WROOM-32", "cpu": "Tensilica LX6 dual-core @ 240MHz", "isa": "XTensa LX6", "gpu": "None (MCU)",
        "ram": "520KB SRAM + 4MB PSRAM", "storage": "16MB Flash",
        "wifi": "WiFi 4 (b/g/n)", "ble": "Bluetooth 4.2 + BLE", "ethernet": "Optional MAC",
        "usb": "USB-UART bridge", "gpio": "30-pin (ADC, DAC, touch, SPI, I2C, UART, I2S, PWM)",
        "display": "External via SPI/I2C", "camera": "Optional via I2S",
        "power": "3.3V/500mA via USB or regulator",
        "price": "$8", "tier": "budget",
        "best_for": ["iot", "maker", "home_automation", "ham_radio"],
        "compatibility_note": "Most popular ESP32. WiFi + BT classic + BLE. Ultra cheap. Arduino/MicroPython/ESP-IDF. Huge community.",
    },
    "esp32_s3_devkitc": {
        "name": "ESP32-S3-DevKitC-1",
        "soc": "ESP32-S3", "cpu": "Tensilica LX7 dual-core @ 240MHz", "isa": "XTensa LX7", "gpu": "None (MCU)",
        "ram": "512KB SRAM + 8MB PSRAM", "storage": "16MB Flash",
        "wifi": "WiFi 4 (b/g/n)", "ble": "Bluetooth 5.0", "ethernet": "None",
        "usb": "USB OTG + USB-UART", "gpio": "45-pin (SPI, I2C, UART, I2S, PWM, LCD, camera)",
        "display": "RGB LCD parallel + SPI TFT", "camera": "MIPI CSI",
        "power": "3.3V via USB OTG",
        "price": "$10", "tier": "budget",
        "best_for": ["maker", "iot", "portable_hacking"],
        "compatibility_note": "USB OTG host/device. Parallel RGB LCD out. Camera interface. Vector instructions (SIMD). Cheap.",
    },
    "xiao_esp32c3": {
        "name": "Seeed Studio XIAO ESP32C3",
        "soc": "ESP32-C3", "cpu": "RISC-V single-core @ 160MHz", "isa": "RISC-V", "gpu": "None (MCU)",
        "ram": "400KB SRAM", "storage": "4MB Flash",
        "wifi": "WiFi 4 (b/g/n)", "ble": "Bluetooth 5.0", "ethernet": "None",
        "usb": "USB-C", "gpio": "11x (ADC, SPI, I2C, UART, PWM)",
        "display": "External via I2C/SPI", "camera": "None",
        "power": "3.3V/65mA via USB-C or JST battery",
        "price": "$6", "tier": "budget",
        "best_for": ["iot", "maker", "writer", "portable_hacking"],
        "compatibility_note": "Tiny thumb-size RISC-V ESP32-C3. USB-C. Ultra cheap. Battery charging built-in. Low power.",
    },
    "tbeam_sx1262": {
        "name": "TTGO T-Beam (ESP32 + LoRa SX1262 + GPS)",
        "soc": "ESP32 + SX1262 + NEO-6M", "cpu": "Tensilica LX6 dual-core @ 240MHz", "isa": "XTensa LX6", "gpu": "None (MCU)",
        "ram": "520KB SRAM + 4MB PSRAM", "storage": "16MB Flash",
        "wifi": "WiFi 4 (b/g/n)", "ble": "Bluetooth 4.2 + BLE", "ethernet": "None",
        "usb": "USB-UART", "gpio": "Internal pin headers (I2C/UART/SPI)",
        "display": "External 0.96\" OLED via I2C", "camera": "None",
        "power": "3.7V LiPo via IPEX",
        "price": "$30", "tier": "standard",
        "best_for": ["field_research", "ham_radio", "home_automation"],
        "compatibility_note": "Built-in LoRa + GPS + WiFi + BLE. Meshtastic ready. Solar charging option. Active Meshtastic community.",
    },
    "esp32_c5_devkitc": {
        "name": "ESP32-C5-DevKitC-1 (Dual-band WiFi 6)",
        "soc": "ESP32-C5", "cpu": "RISC-V 32-bit single-core @ 240MHz + LP-core", "isa": "RISC-V", "gpu": "None (MCU)",
        "ram": "384KB SRAM + external PSRAM", "storage": "16MB Flash",
        "wifi": "WiFi 6 dual-band 2.4/5GHz", "ble": "Bluetooth 5.0", "ethernet": "None",
        "usb": "USB-OTG", "gpio": "29-pin GPIO (SPI, I2C, UART, I2S, PWM, USB OTG)",
        "display": "External via SPI/I2C", "camera": "None",
        "power": "3.3V/100mA",
        "price": "$10", "tier": "budget",
        "best_for": ["maker", "conversation", "survival"],
        "compatibility_note": "First ESP32 with dual-band WiFi 6. 5GHz band avoids 2.4GHz congestion. 802.15.4 for Thread/Zigbee. USB OTG. RISC-V open ISA.",
    },
    "esp32_e22_devkitc": {
        "name": "ESP32-E22 (WiFi 6E tri-band)",
        "soc": "ESP32-E22", "cpu": "RISC-V dual-core @ 500MHz", "isa": "RISC-V", "gpu": "None (MCU)",
        "ram": "1MB on-chip SRAM", "storage": "16MB Flash + external PSRAM option",
        "wifi": "WiFi 6E tri-band 2.4/5/6GHz", "ble": "Bluetooth 6.0 BR/EDR+LE", "ethernet": "None",
        "usb": "USB + SDIO", "gpio": "UP to GPIO (SPI, I2C, UART, I2S, PWM)",
        "display": "External via SPI/I2C", "camera": "None",
        "power": "3.3V/200mA (WiFi TX)",
        "price": "$15", "tier": "standard",
        "best_for": ["maker", "research"],
        "compatibility_note": "WiFi 6E tri-band (2.4/5/6GHz). 2.1 Gbps throughput. BT 6.0 dual-mode. PCIe + USB + SDIO host. RISC-V dual-core 500MHz. Early silicon, limited docs.",
    },
    "esp32_h21_devkitc": {
        "name": "ESP32-H21 (Ultra-low-power BLE+Zigbee)",
        "soc": "ESP32-H21", "cpu": "RISC-V single-core @ 96MHz", "isa": "RISC-V", "gpu": "None (MCU)",
        "ram": "320KB SRAM", "storage": "4MB Flash",
        "wifi": "None", "ble": "Bluetooth 5.x", "ethernet": "None",
        "usb": "None", "gpio": "GPIO (SPI, I2C, UART, PWM)",
        "display": "None", "camera": "None",
        "power": "3.3V/10mA active, uA sleep",
        "price": "$5", "tier": "budget",
        "best_for": ["maker", "conversation"],
        "compatibility_note": "Ultra-low power (uA sleep). BLE + Zigbee/Thread. Integrated DC-DC. Tiny footprint. Sub-$5.",
    },
    "banana_pi_m4_super": {
        "name": "Banana Pi BPI-M4 Super (RK3588)",
        "soc": "RK3588", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "8/16GB LPDDR4X", "storage": "eMMC + NVMe M.2 + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.2", "ethernet": "2.5Gbps",
        "usb": "USB 3.2 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + USB-C DP", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "USB-C PD (5V/4A)",
        "price": "$95", "tier": "standard",
        "best_for": ["ai_ml", "coding", "security"],
        "compatibility_note": "RK3588 at Pi 5 price. 2.5GbE. NVMe native. 6 TOPS NPU. Smaller community than Pi.",
    },
    "unihiker": {
        "name": "UNIHIKER (Pi Alternative + Touch)",
        "soc": "Allwinner H618", "cpu": "Cortex-A53 1.5GHz x4", "gpu": "Mali-G31 MP2",
        "ram": "2GB LPDDR4", "storage": "16GB eMMC + MicroSD",
        "wifi": "WiFi 5", "ble": "Bluetooth 5.0", "ethernet": "1Gbps",
        "usb": "2x USB 2.0 + USB-C", "gpio": "24-pin GPIO + STEMMA QT",
        "display": "Built-in 2.8\" 240x320 IPS touch + HDMI out", "camera": "None",
        "power": "USB-C (5V/2A)",
        "price": "$79", "tier": "standard",
        "best_for": ["maker", "education", "portable_hacking"],
        "compatibility_note": "Built-in 2.8\" touchscreen. All-in-one Python/Bash. Jupyter notebook. STEMMA QT. Headphone + mic jacks.",
    },
    "waveshare_cm5_mini_pc": {
        "name": "Waveshare CM5 Mini PC (Fanless)",
        "soc": "BCM2712", "cpu": "Cortex-A76 2.4GHz x4", "gpu": "VideoCore VII",
        "ram": "8/16GB LPDDR4X", "storage": "eMMC + NVMe + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.0", "ethernet": "2x 1Gbps",
        "usb": "2x USB 3.0 + 2x USB 2.0", "gpio": "40-pin GPIO (internal)",
        "display": "2x micro-HDMI", "camera": "CSI-2",
        "pcie": "PCIe Gen 3 x1", "power": "USB-C PD (5V/5A)",
        "price": "$100", "tier": "standard-premium",
        "best_for": ["coding", "security", "research", "home_automation"],
        "compatibility_note": "Fanless metal enclosure. Dual Ethernet. NVMe. Industrial ready. Wall-mountable.",
    },
    "pironman_5_pro_max": {
        "name": "Pironman 5 Pro Max (Pi 5 Tower)",
        "soc": "BCM2712", "cpu": "Cortex-A76 2.4GHz x4", "gpu": "VideoCore VII",
        "ram": "8/16GB LPDDR4X", "storage": "M.2 NVMe + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.0", "ethernet": "1Gbps",
        "usb": "2x USB 3.0", "gpio": "40-pin GPIO + AI HAT+",
        "display": "2x micro-HDMI + 4.3\" built-in touch", "camera": "CSI-2",
        "pcie": "PCIe Gen 3 x1", "power": "USB-C PD (5V/5A)",
        "price": "$160", "tier": "premium",
        "best_for": ["ai_ml", "coding", "research", "media_production"],
        "compatibility_note": "Built-in 4.3\" touch. AI HAT+ ready (26 TOPS). RGB LED tower. NVMe. Desktop-like form factor.",
    },
    "odroid_m2": {
        "name": "ODROID-M2 (RK3588S2)",
        "soc": "RK3588S2", "cpu": "A76 2.4GHz x4 + A55 1.8GHz x4", "gpu": "Mali-G610 MP4",
        "ram": "8/16GB LPDDR5", "storage": "NVMe M.2 + eMMC + MicroSD",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.2", "ethernet": "2.5Gbps",
        "usb": "2x USB 3.0 + USB 2.0", "gpio": "40-pin GPIO",
        "display": "HDMI 2.1 + USB-C DP", "camera": "MIPI CSI",
        "pcie": "PCIe 3.0", "power": "9V/3A DC barrel",
        "price": "$85", "tier": "standard",
        "best_for": ["ai_ml", "coding", "research", "media_production"],
        "compatibility_note": "RK3588S2 with LPDDR5. NVMe. 2.5GbE. Hardkernel quality. DC barrel power (not USB-C).",
    },
    "zimablade": {
        "name": "ZimaBlade (x86 Blade SBC)",
        "soc": "Intel N100/N305", "cpu": "Alder Lake-N x4/x8", "gpu": "Intel UHD",
        "ram": "8/16GB DDR5", "storage": "NVMe M.2 + SATA III",
        "wifi": "WiFi 6", "ble": "Bluetooth 5.2", "ethernet": "2x 2.5Gbps",
        "usb": "USB 3.2 + USB-C", "gpio": "16-pin GPIO",
        "display": "HDMI 2.0 + Mini-DP", "camera": "None",
        "pcie": "PCIe 3.0", "power": "12V DC",
        "price": "$140", "tier": "premium",
        "best_for": ["coding", "research", "security", "home_automation"],
        "compatibility_note": "Full x86 desktop CPU in blade form. Dual 2.5GbE. NVMe + SATA. Low power for x86. No 40-pin GPIO.",
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
        """Audit a build for flaws and return fixes. Uses Rust core when available."""
        if HAS_RUST:
            try:
                result = rust_audit_build(build)
                if result:
                    return result
            except Exception:
                pass
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
        """Suggest upgrades for an existing build. Uses Rust core when available."""
        if HAS_RUST:
            try:
                result = rust_suggest_upgrades(build)
                if result:
                    return result
            except Exception:
                pass
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
# ESPRESSIF ISA DATABASE
# ============================================================
ESPRESSIF_ISA_DATABASE = {
    "XTensa LX6": {"chips": ["ESP32", "ESP32-WROOM-32", "ESP32-WROVER"], "features": ["Dual-core", "WiFi 4 + BT 4.2 classic + BLE", "Mature ecosystem"], "firmware_compat": ["Arduino", "ESP-IDF v4/v5", "MicroPython", "ESPHome", "Tasmota", "Bruce"]},
    "XTensa LX7": {"chips": ["ESP32-S2", "ESP32-S3"], "features": ["Dual-core S3 only", "WiFi 4 + BLE 5.0", "USB OTG", "Vector instructions (SIMD)", "Parallel RGB LCD"], "firmware_compat": ["Arduino", "ESP-IDF v5", "MicroPython", "ESPHome", "Tasmota", "Bruce", "TensorFlow Micro"]},
    "RISC-V": {"chips": ["ESP32-C2", "ESP32-C3", "ESP32-C5", "ESP32-C6", "ESP32-C61", "ESP32-E22", "ESP32-H2", "ESP32-H21", "ESP32-H4", "ESP32-P4"], "features": ["Open ISA", "Future-proof", "Varying performance C2→E22", "C5 adds 5GHz WiFi 6", "E22 adds 6GHz WiFi 6E"], "firmware_compat": ["Arduino", "ESP-IDF v5+", "MicroPython", "ESPHome (C3/C6)", "Bruce (C3/C6)", "Zigbee2MQTT (C6/H2)"]},
}

# ============================================================
# BRUCE FIRMWARE DATABASE
# ============================================================
BRUCE_FIRMWARE_DATABASE = {
    "bruce_esp32s3": {"name": "Bruce Firmware (ESP32-S3)", "chip": "ESP32-S3", "firmware": "Bruce", "features": ["Sub-GHz RF", "IR blaster", "NFC/RFID", "WiFi deauth", "BLE spam", "Bad USB", "GPS", "1-Wire"], "display": "TFT/OLED via SPI", "storage": "PSRAM + SD card", "best_for": ["security", "field-repair", "research"], "price": 15, "build_time_hours": 3},
    "bruce_esp32c6": {"name": "Bruce Firmware (ESP32-C6)", "chip": "ESP32-C6", "firmware": "Bruce", "features": ["Sub-GHz RF", "IR blaster", "NFC/RFID", "WiFi deauth", "BLE spam", "Thread/Zigbee", "Bad USB", "GPS"], "display": "TFT/OLED via SPI", "storage": "PSRAM + SD card", "best_for": ["security", "research"], "price": 12, "build_time_hours": 3},
    "bruce_esp32": {"name": "Bruce Firmware (ESP32 classic)", "chip": "ESP32", "firmware": "Bruce", "features": ["Sub-GHz RF", "IR blaster", "WiFi deauth", "BLE spam", "Bad USB"], "display": "TFT/OLED via SPI", "storage": "PSRAM + SD card", "best_for": ["security", "maker"], "price": 10, "build_time_hours": 2},
}

# ============================================================
# GR3ML1N TEMPLATE
# ============================================================
GR3ML1N_TEMPLATE = {
    "name": "GR3ML1N — Handheld ESP32 Cyberdeck",
    "author": "Andy Warburton (2026)",
    "inspiration_url": "https://www.hackster.io/news/andy-warburton-s-gr3ml1n",
    "sbc": "Waveshare ESP32-S3 2.8\" Touch LCD",
    "controller": "Waveshare RP2040 Zero",
    "keyboard": "Hand-wired compact (tactile switches, non-keyboard)",
    "display": "2.8\" 240x320 TFT LCD",
    "enclosure": "3D printed (small bed friendly)",
    "firmware": "Custom (CircuitPython/MicroPython)",
    "battery": "LiPo 2000mAh",
    "total_price": 45,
    "build_time_hours": 8,
    "pros": ["Pocket-sized", "Rapid boot (no Linux)", "Low power", "Small-bed 3D print", "Chaos aesthetic"],
    "cons": ["No WiFi hacking out of box", "Limited to 2.8\" screen", "Hand-wiring needed"],
    "best_for": ["conversation", "security", "maker"],
}

# ============================================================
# HOMEBREW OS DATABASE
# ============================================================
HOMEBREW_OS_DATABASE = {
    "solar_os": {"name": "Solar OS (ESP32-S3 RLCD)", "platform": "ESP32-S3-RLCD-4.2", "os": "FreeRTOS custom OS", "features": ["Orthodox file manager", "Web browser", "Chat client", "MP3 player", "Image viewer", "Text editor", "Games", "Serial terminal"], "display": "4.2\" Reflective LCD (sunlight readable)", "input": "Mini keyboard via USB", "battery": "LiPo", "author": "nilseuropa (2026)", "repo": "https://github.com/nilseuropa/solar_os", "price": 60, "best_for": ["writerdeck", "conversation", "survival"]},
    "micro_journal": {"name": "Micro Journal Rev4 (ESP32 Writerdeck)", "platform": "ESP32 + ILI9341 LCD", "os": "ESP32 firmware", "features": ["Instant-on writerdeck", "30% ortholinear keyboard", "Distraction-free writing", "MicroSD save", "USB-C"], "display": "2.8\" ILI9341 LCD", "input": "Hand-wired 30% ortho keyboard", "author": "Un Kyu Lee", "price": 40, "best_for": ["writerdeck"]},
}

# ============================================================
# EDGE AI DATABASE
# ============================================================
EDGE_AI_DATABASE = {
    "tensorflow_micro_vision": {"name": "TensorFlow Micro Vision (ESP32-S3)", "platform": "ESP32-S3", "framework": "TensorFlow Lite Micro", "capabilities": ["Object detection", "Image classification", "Face detection", "Gesture recognition"], "ram_needed": "8MB PSRAM min", "model_format": ".tflite quantized", "fps": "5-15 FPS (QVGA)", "price": 12, "best_for": ["maker", "security", "research"]},
    "tensorflow_micro_audio": {"name": "TensorFlow Micro Audio (ESP32-S3)", "platform": "ESP32-S3", "framework": "TensorFlow Lite Micro", "capabilities": ["Keyword spotting", "Wake word detection", "Audio classification", "Speaker recognition"], "ram_needed": "4MB PSRAM", "model_format": ".tflite quantized", "fps": "Real-time", "price": 10, "best_for": ["maker", "conversation"]},
    "esp_dl": {"name": "ESP-DL (Espressif Deep Learning)", "platform": "ESP32-S3", "framework": "ESP-DL (ESP-IDF)", "capabilities": ["Face recognition", "Object detection", "Human pose estimation", "Hand gesture"], "ram_needed": "8MB PSRAM", "model_format": "ESP-DL native", "fps": "10-25 FPS", "price": 12, "best_for": ["security", "research", "ai"]},
    "edge_impulse": {"name": "Edge Impulse (ESP32-S3/C3)", "platform": "ESP32-S3 / C3", "framework": "Edge Impulse", "capabilities": ["Motion classification", "Audio events", "Anomaly detection", "Custom vision"], "ram_needed": "4MB PSRAM", "model_format": "Edge Impulse SDK", "fps": "Varies by model", "price": 10, "best_for": ["maker", "research", "ai"]},
}

# ============================================================
# ESP-NOW DATABASE
# ============================================================
ESP_NOW_DATABASE = {
    "esp_now_mesh": {"protocol": "ESP-NOW", "type": "Peer-to-peer mesh", "range": "200m (line of sight)", "band": "2.4GHz", "throughput": "1 Mbps", "power": "Very low", "esp_compat": ["ESP32", "ESP32-S3", "ESP32-C3", "ESP32-C5", "ESP32-C6", "ESP32-E22"], "use_cases": ["Mesh networking", "Sensor networks", "Remote display", "Keyboard link", "Multi-deck sync"], "pros": ["No WiFi router needed", "Ultra low latency", "Built-in encryption", "Easy to set up"], "cons": ["Limited range without mesh", "No IP routing", "Proprietary protocol"], "price": 0, "best_for": ["survival", "field-repair", "maker"]},
    "esp_mesh_lite": {"protocol": "ESP-MESH (WiFi mesh)", "type": "WiFi mesh network", "range": "1km+ (multi-hop)", "band": "2.4GHz", "throughput": "10 Mbps", "power": "Moderate", "esp_compat": ["ESP32", "ESP32-S3", "ESP32-C3", "ESP32-C5", "ESP32-C6"], "use_cases": ["Large area coverage", "IoT sensor grid", "Off-grid communication", "Disaster recovery"], "pros": ["Self-healing mesh", "TCP/IP compatible", "HTTP/MQTT over mesh"], "cons": ["Higher power than ESP-NOW", "Setup complexity"], "price": 0, "best_for": ["survival", "research"]},
    "lora_mesh": {"protocol": "LoRa Mesh (Meshtastic)", "type": "Long-range mesh", "range": "10-15km per node", "band": "868/915MHz", "throughput": "250 bps", "power": "Very low", "esp_compat": ["ESP32 + SX1262/SX1276"], "use_cases": ["Off-grid texting", "GPS tracking", "Emergency comms", "Multi-day field ops"], "pros": ["10km+ range", "Meshtastic ecosystem", "Open source", "Encrypted"], "cons": ["Low bandwidth", "Needs LoRa radio module"], "price": 25, "best_for": ["survival", "research", "field-repair"]},
}

# ============================================================
# WIFI BLE SCANNER DATABASE
# ============================================================
WIFI_BLE_SCANNER_DATABASE = {
    "wardriving_esp32": {"name": "WiFi Wardriving (ESP32)", "firmware": "ESP32 Marauder / Bruce", "features": ["SSID scan", "Channel hop", "GPS logging", "Wigle export", "Deauth detection"], "hardware": "ESP32 + GPS module (NEO-6M)", "output": "CSV / Wigle CSV", "price": 15, "best_for": ["security", "research", "field-repair"]},
    "ble_scanner": {"name": "BLE Device Scanner", "firmware": "ESP32 BLE", "features": ["BLE device discovery", "iBeacon detection", "RSSI logging", "Address tracking"], "hardware": "ESP32 (any)", "output": "JSON / CSV", "price": 8, "best_for": ["security", "research"]},
    "spectrum_analyzer": {"name": "WiFi Spectrum Analyzer", "firmware": "ESP32 WiFi", "features": ["Channel utilization", "Signal strength heatmap", "AP detection", "Channel interference"], "hardware": "ESP32", "output": "Real-time display", "price": 8, "best_for": ["security", "maker", "research"]},
    "packet_sniffer": {"name": "WiFi Packet Sniffer (Monitor mode)", "firmware": "ESP32 Marauder", "features": ["Promiscuous mode", "Packet capture", "SSID probe", "Channel hopping"], "hardware": "ESP32", "output": "PCAP / console", "price": 8, "best_for": ["security", "research"]},
}


class BuildComparison:
    """Side-by-side comparison of two cyberdeck builds."""

    @staticmethod
    def compare(build_a: Dict, build_b: Dict) -> Dict:
        keys = ["sbc", "display", "keyboard", "enclosure", "power", "cooling", "storage", "connectivity", "total_price", "power_draw_w", "weight_kg", "battery_life_h"]
        result = {"build_a_name": build_a.get("name", "Build A"), "build_b_name": build_b.get("name", "Build B"), "differences": {}}
        for k in keys:
            va = build_a.get(k, "N/A")
            vb = build_b.get(k, "N/A")
            diff = va != vb
            result["differences"][k] = {"a": va, "b": vb, "differs": diff}
        for k in ["total_price", "power_draw_w", "weight_kg", "battery_life_h"]:
            try:
                va = float(build_a.get(k, 0) or 0)
                vb = float(build_b.get(k, 0) or 0)
                delta = round(vb - va, 2)
                result["differences"][k + "_delta"] = delta
            except (ValueError, TypeError):
                result["differences"][k + "_delta"] = 0
        return result

    @staticmethod
    def format_comparison(result: Dict) -> str:
        lines = [f"<b>Build Comparison</b>", f"", f"<b>A:</b> {result['build_a_name']}", f"<b>B:</b> {result['build_b_name']}", f""]
        diffs = result["differences"]
        for k, v in diffs.items():
            if k.endswith("_delta"):
                continue
            va = v.get("a", "N/A")
            vb = v.get("b", "N/A")
            differs = v.get("differs", False)
            marker = " <b>\u2260</b>" if differs else ""
            lines.append(f"<b>{k.replace('_', ' ').title()}:</b>{marker}")
            lines.append(f"  A: {va}")
            lines.append(f"  B: {vb}")
        lines.append(f"")
        lines.append("<b>Deltas:</b>")
        for k in ["total_price_delta", "power_draw_w_delta", "weight_kg_delta", "battery_life_h_delta"]:
            if k in diffs:
                d = diffs[k]
                sign = "+" if d > 0 else ""
                lines.append(f"  {k.replace('_delta', '').replace('_', ' ').title()}: {sign}{d}")
        return "\n".join(lines)


class BOMExporter:
    """Export build bill of materials to CSV or text."""

    @staticmethod
    def to_csv(build: Dict, filepath: str = None) -> str:
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Component", "Type", "Model", "Price", "Quantity", "Notes"])
        for cat, items in build.get("components", {}).items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        writer.writerow([item.get("name", ""), cat, item.get("model", ""), item.get("price", ""), item.get("qty", 1), item.get("notes", "")])
                    else:
                        writer.writerow([str(item), cat, "", "", 1, ""])
            elif isinstance(items, dict):
                writer.writerow([items.get("name", ""), cat, items.get("model", ""), items.get("price", ""), items.get("qty", 1), items.get("notes", "")])
        csv_data = output.getvalue()
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(csv_data)
        return csv_data

    @staticmethod
    def to_text(build: Dict) -> str:
        lines = [f"<b>Bill of Materials</b>", f"Build: {build.get('name', 'Unnamed')}", f""]
        for cat, items in build.get("components", {}).items():
            lines.append(f"<b>{cat.replace('_', ' ').title()}:</b>")
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        price = item.get("price", "?")
                        qty = item.get("qty", 1)
                        lines.append(f"  {item.get('name', str(item))} x{qty}  ${price}")
                    else:
                        lines.append(f"  {item}")
            elif isinstance(items, dict):
                price = items.get("price", "?")
                lines.append(f"  {items.get('name', str(items))}  ${price}")
            lines.append("")
        total = build.get("total_price", 0)
        lines.append(f"<b>Total: ${total}</b>")
        return "\n".join(lines)


class BuildTimeline:
    """Track revisions of a cyberdeck build over time."""

    def __init__(self):
        self.revisions = []

    def save_revision(self, build: Dict, notes: str = ""):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "build": build,
            "notes": notes,
            "version": len(self.revisions) + 1
        }
        self.revisions.append(entry)
        return entry["version"]

    def get_revision(self, version: int) -> Optional[Dict]:
        for r in self.revisions:
            if r["version"] == version:
                return r
        return None

    def list_revisions(self) -> List[Dict]:
        return [{"version": r["version"], "timestamp": r["timestamp"], "notes": r["notes"]} for r in self.revisions]

    def diff_revisions(self, v1: int, v2: int) -> str:
        r1 = self.get_revision(v1)
        r2 = self.get_revision(v2)
        if not r1 or not r2:
            return "Revision not found"
        b1 = r1["build"]
        b2 = r2["build"]
        comp = BuildComparison.compare(b1, b2)
        return BuildComparison.format_comparison(comp)


class Changelog:
    """Track version history for the cyberdeck system."""

    entries = []

    @classmethod
    def add_entry(cls, version: str, date: str, changes: List[str]):
        cls.entries.append({"version": version, "date": date, "changes": changes})

    @classmethod
    def format(cls) -> str:
        lines = ["<b>Cyberdeck Agent Changelog</b>", ""]
        for e in reversed(cls.entries):
            lines.append(f"<b>v{e['version']}</b> ({e['date']})")
            for c in e["changes"]:
                lines.append(f"  \u2022 {c}")
            lines.append("")
        return "\n".join(lines)


Changelog.add_entry("6.2.0", "2026-07-30", [
    "Hardware Module System: NATO rails, sliding screens, NP-F batteries, Li'l PCB ecosystem",
    "BBC micro:bit v2 + ESP32-DevKitC/S3/XIAO C3/TTGO T-Beam SBC entries",
    "/hardware, /modules, /lilpcb bot commands",
    "7 new cyberdeck ideas with hardware module specs",
])
Changelog.add_entry("6.3.0", "2026-07-30", [
    "ESP32-C5 (dual-band WiFi 6), ESP32-E22 (WiFi 6E tri-band), ESP32-H21 (ultra-low-power) chips",
    "ISA categorization: XTensa LX6/LX7 vs RISC-V vs ARM for all MCU/SBC entries",
    "BuildComparison: side-by-side diff of 2 cyberdeck builds",
    "BOMExporter: CSV bill of materials export",
    "BuildTimeline: version tracking for builds",
    "Dashboard re-render command",
    "Multi-language: Indonesian build instructions",
    "AMOLED, RLCD, Camera, Audio, Cellular/LTE, Sensor Pack component databases",
    "Bruce firmware builds, GR3ML1N template, Homebrew OS cards",
    "ESP-NOW/Mesh connectivity option + WiFi/BLE scanner presets",
    "Edge AI configs (ESP32-S3 + TensorFlow Micro)",
])


class DashboardReRender:
    """Re-generate HTML dashboard for an existing build from history."""

    @staticmethod
    def render(build: Dict) -> str:
        import html as h
        name = h.escape(build.get("name", "Cyberdeck Build"))
        comps = build.get("components", {})
        total = build.get("total_price", 0)
        lines = [f"<html><head><title>{name}</title><meta charset='utf-8'>",
                 "<style>body{background:#0a0a0f;color:#e0e0e0;font-family:monospace;padding:20px}",
                 "h1{color:#00ff88;border-bottom:2px solid #00ff88;padding-bottom:10px}",
                 "table{width:100%;border-collapse:collapse;margin:10px 0}",
                 "th,td{text-align:left;padding:8px;border-bottom:1px solid #333}",
                 "th{color:#00ff88}.card{background:#151520;border:1px solid #2a2a35;border-radius:8px;padding:15px;margin:10px 0}",
                 ".total{font-size:1.5em;color:#00ff88;text-align:right}",
                 "pre{background:#1a1a25;padding:10px;border-radius:4px;overflow-x:auto}",
                 "</style></head><body>",
                 f"<h1>\U0001f4df {name}</h1>",
                 f"<div class='card'><h3>\U0001f4ca Build Overview</h3>",
                 f"<pre>{h.escape(str(build.get('description', '')))}</pre></div>",
                 f"<div class='card'><h3>\U0001f9f0 Components</h3><table><tr><th>Category</th><th>Component</th><th>Price</th></tr>"]
        for cat, items in comps.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        lines.append(f"<tr><td>{cat}</td><td>{h.escape(str(item.get('name', '')))}</td><td>${item.get('price', 0)}</td></tr>")
                    else:
                        lines.append(f"<tr><td>{cat}</td><td>{h.escape(str(item))}</td><td>-</td></tr>")
            elif isinstance(items, dict):
                lines.append(f"<tr><td>{cat}</td><td>{h.escape(str(items.get('name', '')))}</td><td>${items.get('price', 0)}</td></tr>")
        lines.append(f"</table></div>")
        lines.append(f"<div class='total'>Total: ${total}</div>")
        lines.append(f"<div class='card'><h3>\U0001f50b Power Specs</h3><pre>Power draw: {build.get('power_draw_w', '?')}W\nBattery: {build.get('battery_capacity', '?')}mAh\nEst. runtime: {build.get('battery_life_h', '?')}h</pre></div>")
        lines.append(f"<div class='card'><h3>\U0001f4d0 Physical</h3><pre>Weight: {build.get('weight_kg', '?')}kg\nDimensions: {build.get('dimensions', '?')}</pre></div>")
        lines.append(f"<p style='color:#666;font-size:0.8em'>Generated by Cyberdeck Agent v6.3</p>")
        lines.append("</body></html>")
        return "\n".join(lines)

    @staticmethod
    def render_to_file(build: Dict, filepath: str) -> bool:
        html = DashboardReRender.render(build)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True


class IndonesianTranslator:
    """Multi-language support: Indonesian build instructions."""

    translations = {
        "Build": "Rakit",
        "Components": "Komponen",
        "Tools needed": "Alat yang dibutuhkan",
        "Step": "Langkah",
        "Assembly": "Perakitan",
        "Wiring": "Kabel",
        "Testing": "Pengujian",
        "Warning": "Peringatan",
        "Tip": "Tips",
        "Mount the SBC": "Pasang SBC",
        "Connect the display": "Hubungkan layar",
        "Wire the keyboard": "Kabel keyboard",
        "Install the battery": "Pasang baterai",
        "Close the enclosure": "Tutup casing",
        "Power on and test": "Nyalakan dan uji",
        "Soldering required": "Perlu solder",
        "No soldering needed": "Tidak perlu solder",
        "Estimated time": "Perkiraan waktu",
        "Difficulty": "Tingkat kesulitan",
    }

    @staticmethod
    def id(text: str) -> str:
        return IndonesianTranslator.translations.get(text, text)

    @staticmethod
    def translate_instructions(instructions: List[str]) -> List[str]:
        return [IndonesianTranslator.id(s) for s in instructions]

    @staticmethod
    def format_build(build: Dict) -> str:
        name = build.get("name", "Tanpa Nama")
        lines = [f"<b>\U0001f4df Rakit Cyberdeck: {name}</b>", ""]
        lines.append(f"<b>Komponen:</b>")
        for cat, items in build.get("components", {}).items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        lines.append(f"  \u2022 {item.get('name', str(item))}  Rp{item.get('price_idr', '?')}")
            elif isinstance(items, dict):
                lines.append(f"  \u2022 {items.get('name', str(items))}")
        lines.append("")
        lines.append(f"<b>Alat yang dibutuhkan:</b>")
        lines.append(f"  \u2022 Obeng (+ dan -)")
        lines.append(f"  \u2022 Tang potong")
        lines.append(f"  \u2022 Solder (jika perlu)")
        lines.append(f"  \u2022 Multimeter")
        lines.append("")
        lines.append(f"<b>Langkah-langkah:</b>")
        steps = build.get("steps", ["Pasang SBC", "Hubungkan layar", "Kabel keyboard", "Pasang baterai", "Tutup casing", "Nyalakan dan uji"])
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. {IndonesianTranslator.id(step)}")
        lines.append("")
        lines.append(f"<b>\U0001f4b0 Total: Rp{build.get('total_price_idr', 0):,}</b>")
        return "\n".join(lines)


# ============================================================
# v6.5 — MESH FREQUENCY PLAN DATABASE
# ============================================================
MESH_FREQUENCY_PLAN = {
    "us": {"region": "US (ISM 915)", "bands": [{"freq": 915, "label": "915MHz ISM", "channels": "1-13 (903-927MHz)", "tx_power_max": 27, "duty_cycle": "100%", "notes": "LoRa 915MHz band, 13 channels, 125kHz/250kHz/500kHz"}], "default_channel": 6, "lorawan": "US915"},
    "eu": {"region": "EU (868)", "bands": [{"freq": 868, "label": "868MHz SRD", "channels": "1-10 (863-870MHz)", "tx_power_max": 14, "duty_cycle": "1%", "notes": "ETSI 868MHz, 10 channels, duty cycle limited to 1%"}], "default_channel": 3, "lorawan": "EU868"},
    "au": {"region": "Australia (915)", "bands": [{"freq": 915, "label": "915MHz ISM", "channels": "1-8 (915-928MHz)", "tx_power_max": 30, "duty_cycle": "100%", "notes": "Similar to US 915, 8 channels, higher TX power allowed"}], "default_channel": 5, "lorawan": "AU915"},
    "jp": {"region": "Japan (920)", "bands": [{"freq": 920, "label": "920MHz ARIB", "channels": "1-28 (920-928MHz)", "tx_power_max": 20, "duty_cycle": "10%", "notes": "ARIB STD-T108, 28 channels, listen-before-talk required"}], "default_channel": 10, "lorawan": "AS923"},
    "kr": {"region": "Korea (920)", "bands": [{"freq": 920, "label": "920MHz KCC", "channels": "1-8 (917-923.5MHz)", "tx_power_max": 14, "duty_cycle": "10%", "notes": "KCC 920MHz, 8 channels, LBT required"}], "default_channel": 4, "lorawan": "KR920"},
    "in": {"region": "India (866)", "bands": [{"freq": 866, "label": "866MHz WPC", "channels": "1-10 (865-867MHz)", "tx_power_max": 14, "duty_cycle": "10%", "notes": "WPC 866MHz, 10 channels"}], "default_channel": 2, "lorawan": "IN865"},
    "cn": {"region": "China (780)", "bands": [{"freq": 780, "label": "780MHz MIIT", "channels": "1-8 (779-787MHz)", "tx_power_max": 17, "duty_cycle": "100%", "notes": "MIIT 780MHz, 8 channels"}], "default_channel": 3, "lorawan": "CN779"},
}

LORA_HARDWARE_DATABASE = {
    "heltec_v3": {"name": "Heltec WiFi LoRa 32 V3", "chipset": "ESP32-S3FN8", "frequency_mhz": 868, "max_range_km": 10.0, "protocol": "LoRa", "interface": "WiFi+LoRa", "price": 18, "features": ["0.96in OLED", "WiFi", "Bluetooth LE", "USB-C", "SX1262"], "best_for": ["meshtastic", "iot", "weather", "aprs"]},
    "heltec_wireless_stick": {"name": "Heltec Wireless Stick V3", "chipset": "ESP32-S3", "frequency_mhz": 868, "max_range_km": 8.0, "protocol": "LoRa", "interface": "WiFi+LoRa", "price": 15, "features": ["USB-C", "SX1262", "WiFi", "BLE", "compact"], "best_for": ["meshtastic", "portable", "iot"]},
    "ttgo_t_beams3": {"name": "TTGO T-Beam S3", "chipset": "ESP32-S3", "frequency_mhz": 915, "max_range_km": 12.0, "protocol": "LoRa", "interface": "WiFi+LoRa+GPS", "price": 32, "features": ["NEO-6M GPS", "SX1262", "WiFi", "BLE", "IPEX antenna", "18650 holder"], "best_for": ["meshtastic", "gps", "tracking", "offgrid"]},
    "ttgo_lora32_v21": {"name": "TTGO LoRa32 V2.1", "chipset": "ESP32", "frequency_mhz": 868, "max_range_km": 8.0, "protocol": "LoRa", "interface": "WiFi+LoRa", "price": 14, "features": ["0.96in OLED", "SX1276", "WiFi", "BLE"], "best_for": ["meshtastic", "iot", "education"]},
    "rak4631": {"name": "RAK4631 WisBlock Core", "chipset": "nRF52840", "frequency_mhz": 868, "max_range_km": 15.0, "protocol": "LoRaWAN", "interface": "BLE+LoRa", "price": 25, "features": ["SX1262", "BLE 5.0", "nRF52840 MCU", "ultra-low-power", "IoT connectors"], "best_for": ["lorawan", "sensor", "low-power"]},
    "lilygo_t3s3": {"name": "LilyGO T3S3", "chipset": "ESP32-S3", "frequency_mhz": 868, "max_range_km": 10.0, "protocol": "LoRa", "interface": "WiFi+LoRa", "price": 20, "features": ["1.9in TFT", "SX1262", "WiFi", "BLE", "SD card"], "best_for": ["meshtastic", "display", "portable"]},
    "esp32_s3_sx1262": {"name": "ESP32-S3 + SX1262 Dev", "chipset": "ESP32-S3", "frequency_mhz": 868, "max_range_km": 10.0, "protocol": "LoRa", "interface": "WiFi+LoRa", "price": 12, "features": ["SX1262", "WiFi", "BLE", "USB-C", "breadboard-friendly"], "best_for": ["custom", "experiment", "prototype"]},
    "rp2040_lora": {"name": "RP2040 LoRa", "chipset": "RP2040", "frequency_mhz": 868, "max_range_km": 5.0, "protocol": "LoRa", "interface": "USB+LoRa", "price": 10, "features": ["SX1262", "dual-core Cortex-M0+", "no WiFi", "low-cost"], "best_for": ["sensor", "low-cost", "education"]},
    "sx1262_mm": {"name": "SX1262 Mini Module", "chipset": "SX1262", "frequency_mhz": 868, "max_range_km": 3.0, "protocol": "LoRa", "interface": "SPI", "price": 5, "features": ["compact", "low-power", "+22dBm", "SPI interface"], "best_for": ["custom-pcb", "tiny", "embedded"]},
    "sx1276": {"name": "SX1276 Module", "chipset": "SX1276", "frequency_mhz": 868, "max_range_km": 3.0, "protocol": "LoRa", "interface": "SPI", "price": 4, "features": ["+20dBm", "SPI", "FSK/OOK", "legacy"], "best_for": ["custom-pcb", "legacy", "experiment"]},
    "lr1110": {"name": "LR1110 Module", "chipset": "LR1110", "frequency_mhz": 915, "max_range_km": 10.0, "protocol": "LoRaWAN/LR-FHSS", "interface": "SPI+GNSS", "price": 8, "features": ["GNSS", "WiFi scan", "+22dBm", "LR-FHSS"], "best_for": ["lorawan", "gnss", "tracking"]},
    "wio_e5": {"name": "Wio E5 Mini", "chipset": "STM32WLE5JC", "frequency_mhz": 868, "max_range_km": 10.0, "protocol": "LoRaWAN", "interface": "UART+LoRa", "price": 9, "features": ["AT command set", "ultra-low-power", "STM32", "LoRaWAN stack"], "best_for": ["lorawan", "sensor", "low-power"]},
}

MESH_CONFIG_TEMPLATES = {
    "meshtastic": {
        "name": "Meshtastic LoRa Mesh",
        "yaml": """# Meshtastic config for cyberdeck node
lora:
  modem_config: Bw125Cr48Sf4096
  region: US
  hop_limit: 3
  tx_power: 20
  frequency_offset: 0
  override_frequency: 0
  ignore_incoming: false
  ok_to_mqtt: false

position:
  fixed_position: true
  latitude: 0.0
  longitude: 0.0
  altitude: 0
  gps_enabled: true
  gps_update_interval: 300

bluetooth:
  enabled: true
  mode: RANDOM_PIN

display:
  screen_on_seconds: 300
  wake_on_tap: true
  carousel_enabled: true

network:
  wifi_enabled: false
  wifi_ssid: ""
  wifi_password: ""

device:
  role: CLIENT
  serial_enabled: false
  rebroadcast_mode: ALL
  node_info_broadcast_secs: 10800
"""
    },
    "esp_now": {
        "name": "ESP-NOW Peer-to-Peer",
        "yaml": """# ESP-NOW config for cyberdeck mesh
esp_now:
  wifi_mode: WIFI_STA
  channel: 1
  encryption: true
  pmk: "cyberdeck_mesh_key_2026"
  long_range: false
  tx_power: 20
  data_rate: 1  # 0=1M, 1=2M, 2=5.5M, 3=11M

peers:
  max_peers: 20
  auto_discover: true
  discovery_interval_s: 30
  heartbeat_interval_s: 10
  timeout_s: 120

mesh:
  max_hops: 5
  route_discovery: proactive
  congestion_control: enabled
  fragment_size_bytes: 250
  max_payload_bytes: 1000

channels:
  primary: 1
  backup: 6
  broadcast: 11

sleep:
  enable_dsm: false
  sleep_interval_s: 0
  wake_interval_s: 0
"""
    },
    "lora_mesh": {
        "name": "LoRa Mesh (RNode/RAK)",
        "yaml": """# LoRa Mesh config for offgrid cyberdeck
interface:
  type: tty
  port: /dev/ttyACM0
  baud: 115200

lora:
  frequency_hz: 868000000
  bandwidth_khz: 125
  spreading_factor: 12
  coding_rate: 5
  tx_power_dbm: 20
  preamble_length: 8
  sync_word: 0xAB

mesh:
  routing: source_routing
  max_hops: 8
  ack_timeout_ms: 3000
  retransmissions: 3
  neighbor_timeout_s: 300
  broadcast_interval_s: 60

encryption:
  enabled: true
  cipher: AES-256-GCM
  key_rotation: session

mqtt:
  enabled: false
  broker: ""
  port: 1883
  topic: "mesh/cyberdeck"
"""
    },
    "rag_bulletin": {
        "name": "RAG Bulletin Board",
        "yaml": """# RAG Bulletin Board — AI-powered mesh messaging
mesh:
  protocol: lora_rag
  beacon_interval_s: 120
  max_message_size: 512
  retention_hours: 72
  replication_factor: 3

rag:
  enabled: true
  embedding_model: all-MiniLM-L6-v2
  vector_dim: 384
  similarity_threshold: 0.75
  max_context_messages: 10
  summary_interval_m: 30
  llm_model: phi3:mini
  context_window_size: 10

bulletin:
  categories:
    - alerts
    - weather
    - resources
    - coordination
    - general
  auto_summarize: true
  max_pinned: 5
  expire_after_h: 48

power:
  deep_sleep: true
  wake_interval_s: 60
  tx_window_ms: 500
  rx_window_ms: 5000
"""
    },
}


class MeshNetworkPlanner:
    """LoRA mesh network planning, hardware recommendation, and config generation."""

    @staticmethod
    def calculate_range(freq_mhz: int, tx_power_dbm: int, antenna_gain_dbi: float, environment: str = "urban") -> dict:
        if environment == "rural":
            base_range = 10.0
            env_factor = 1.0
            n = 2.5
        elif environment == "suburban":
            base_range = 5.0
            env_factor = 0.6
            n = 3.0
        else:
            base_range = 2.0
            env_factor = 0.3
            n = 3.5

        freq_ghz = freq_mhz / 1000.0
        path_loss_20m = 20 * (freq_ghz * 20) + 20 * 0.2
        path_loss_db = 20 * (freq_ghz * base_range) + 20 * 0.2
        fresnel_zone = 8.656 * (base_range / freq_ghz) ** 0.5
        power_factor = (tx_power_dbm - 14) * 0.05
        antenna_factor = antenna_gain_dbi * 0.1
        range_km = round(base_range * (1 + power_factor + antenna_factor) * env_factor, 2)

        if range_km < 0.5:
            rec = "Very short range — ensure line-of-sight, consider higher gain antenna"
        elif range_km < 2:
            rec = "Short range — suitable for urban mesh, increase node density"
        elif range_km < 5:
            rec = "Moderate range — good for suburban mesh with acceptable density"
        elif range_km < 10:
            rec = "Good range — suitable for rural mesh with sparse nodes"
        else:
            rec = "Excellent range — long-distance links feasible, consider directional antennas"

        return {
            "range_km": range_km,
            "fresnel_zone_m": round(fresnel_zone, 2),
            "path_loss_db": round(path_loss_db, 1),
            "recommendation": rec,
        }

    @staticmethod
    def recommend_hardware(use_case: str, budget: str = "mid") -> str:
        use_case = use_case.lower()
        budget_map = {"low": 10, "budget": 10, "mid": 20, "high": 35, "premium": 100}
        max_price = budget_map.get(budget, 20)

        candidates = []
        for hid, hw in LORA_HARDWARE_DATABASE.items():
            score = 0
            if use_case in hw["best_for"]:
                score += 3
            if hw["price"] <= max_price:
                score += 2
            if "meshtastic" in use_case and hid in ("heltec_v3", "ttgo_t_beams3", "lilygo_t3s3"):
                score += 2
            if "gps" in use_case or "tracking" in use_case:
                if "GPS" in " ".join(hw["features"]):
                    score += 2
            if "lora" in use_case or "mesh" in use_case:
                score += 1
            if "low-power" in use_case:
                if "ultra-low-power" in hw["features"] or "low-power" in hw["best_for"]:
                    score += 2
            if score > 0:
                candidates.append((score, hid, hw))

        if not candidates:
            return f"No hardware found for '{use_case}' (budget: {budget}). Try a different use case."

        candidates.sort(reverse=True)
        lines = [f"<b>Hardware recommendations for: {use_case} (budget: ${max_price})</b>", ""]
        for score, hid, hw in candidates[:5]:
            lines.append(f"<b>{hw['name']}</b> — ${hw['price']}  [score: {score}]")
            lines.append(f"  Chipset: {hw['chipset']} | Freq: {hw['frequency_mhz']}MHz")
            lines.append(f"  Range: {hw['max_range_km']}km | Protocol: {hw['protocol']}")
            lines.append(f"  Features: {', '.join(hw['features'][:5])}")
            lines.append(f"  Tags: {', '.join(hw['best_for'])}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def generate_node_config(protocol: str, node_name: str, role: str, region: str = "us") -> str:
        protocol = protocol.lower()
        template = MESH_CONFIG_TEMPLATES.get(protocol)
        if not template:
            avail = ", ".join(MESH_CONFIG_TEMPLATES.keys())
            return f"Unknown protocol: {protocol}. Available: {avail}"

        region_plan = MESH_FREQUENCY_PLAN.get(region, MESH_FREQUENCY_PLAN["us"])
        lines = [
            f"# Mesh Node Config: {node_name}",
            f"# Role: {role} | Protocol: {template['name']}",
            f"# Region: {region_plan['region']} | Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# ============================================",
            "",
            f"node:",
            f"  name: \"{node_name}\"",
            f"  role: {role}",
            f"  region: {region}",
            f"  frequency_plan: {region_plan['default_channel']}",
            f"  tx_power_max: {region_plan['bands'][0]['tx_power_max']}dBm",
            "",
        ]
        lines.append(template["yaml"])
        return "\n".join(lines)

    @staticmethod
    def plan_mesh_network(node_count: int, area_km2: float, environment: str) -> str:
        density = node_count / max(area_km2, 0.1)
        side_km = area_km2 ** 0.5

        if environment == "rural":
            node_range = 8.0
            ideal_spacing = node_range * 0.8
        elif environment == "suburban":
            node_range = 4.0
            ideal_spacing = node_range * 0.7
        else:
            node_range = 1.5
            ideal_spacing = node_range * 0.6

        nodes_needed_line = max(1, int(side_km / ideal_spacing) + 1)
        nodes_needed = nodes_needed_line ** 2

        hop_count = max(1, int(side_km / node_range) + 1)
        total_range_km = hop_count * node_range

        lines = [
            f"<b>Mesh Network Plan</b>\n",
            f"<b>Parameters:</b>",
            f"  Nodes: {node_count} | Area: {area_km2}km² | Environment: {environment}",
            f"  Est. density: {density:.2f} nodes/km²",
            f"  Est. node range: {node_range}km",
            f"",
            f"<b>Topology:</b>",
            f"  Ideal grid spacing: {ideal_spacing}km",
            f"  Nodes needed for full coverage: {nodes_needed} ({nodes_needed_line}x{nodes_needed_line} grid)",
            f"  Max hop count: {hop_count}",
            f"  Total mesh range: ~{total_range_km}km",
            f"",
        ]

        if node_count < nodes_needed * 0.5:
            lines.append("<b>⚠ Coverage gap:</b> Too few nodes for full area coverage.")
            lines.append(f"  Need ~{nodes_needed} nodes for complete {area_km2}km² coverage.")
            lines.append(f"  Current {node_count} nodes cover ~{round(node_count / max(nodes_needed, 1) * 100)}%")
            lines.append("")
            lines.append("<b>Recommendations:</b>")
            lines.append(f"  Add {nodes_needed - node_count} more nodes to close gaps")
            lines.append(f"  Use higher gain antennas to extend range")
            lines.append(f"  Place nodes at high points for line-of-sight")
        elif node_count >= nodes_needed * 1.5:
            lines.append("<b>✅ Coverage sufficient:</b> Dense mesh with redundancy.")
            lines.append(f"  Redundancy factor: {node_count / max(nodes_needed, 1):.1f}x")
            lines.append("  Consider adding routing nodes for backbone")
        else:
            lines.append("<b>✅ Basic coverage achieved.</b>")
            lines.append("  Consider strategic node placement for optimal coverage")
            lines.append("  Add 1-2 extra nodes for redundancy")

        lines.append("")
        lines.append("<b>Hardware Strategy:</b>")
        if environment == "urban":
            lines.append("  Use ESP32-S3 + SX1262 nodes (dense, low-power)")
            lines.append("  Heltec V3 or LilyGO T3S3 recommended")
        elif environment == "rural":
            lines.append("  Use TTGO T-Beam S3 for long-range + GPS")
            lines.append("  Directional antennas for backbone links")
        else:
            lines.append("  Mix of Heltec V3 + T-Beam S3 recommended")
            lines.append("  Omni antennas for coverage, directional for links")

        return "\n".join(lines)

    @staticmethod
    def frequency_plan(region: str = "us") -> dict:
        plan = MESH_FREQUENCY_PLAN.get(region)
        if not plan:
            return {"error": f"Unknown region: {region}", "available": list(MESH_FREQUENCY_PLAN.keys())}
        return plan


# ============================================================
# v6.5 — BOM TRACKER (PRICE TIERS + PERSISTENCE)
# ============================================================
BOM_PROJECTS_FILE = "bom_projects.json"

PRICE_TIERS = {
    "budget": {"multiplier": 0.7, "description": "Cost-optimized with basic components, no frills"},
    "standard": {"multiplier": 1.0, "description": "Balanced quality and cost, recommended for most builds"},
    "premium": {"multiplier": 1.5, "description": "High-end components with best performance and aesthetics"},
}

_BOM_COMPONENT_LIBRARY = {
    "writerdeck": [
        {"name": "Raspberry Pi 5 8GB", "qty": 1, "unit_price": 80},
        {"name": "7-inch HDMI IPS Display", "qty": 1, "unit_price": 45},
        {"name": "Mechanical Keyboard PCB", "qty": 1, "unit_price": 25},
        {"name": "Cherry MX Brown Switches", "qty": 60, "unit_price": 0.35},
        {"name": "NP-F970 Battery (7.2V 6600mAh)", "qty": 1, "unit_price": 35},
        {"name": "Battery Charging Module", "qty": 1, "unit_price": 8},
        {"name": "Custom Enclosure (3D Print)", "qty": 1, "unit_price": 15},
        {"name": "Step-down Converter", "qty": 1, "unit_price": 5},
    ],
    "pentest_kali": [
        {"name": "Orange Pi 5 Max 16GB", "qty": 1, "unit_price": 150},
        {"name": "5-inch HDMI Touch Display", "qty": 1, "unit_price": 55},
        {"name": "Mini Keyboard with Trackpad", "qty": 1, "unit_price": 30},
        {"name": "Alfa AWUS036ACH WiFi Adapter", "qty": 1, "unit_price": 35},
        {"name": "NEO-6M GPS Module", "qty": 1, "unit_price": 10},
        {"name": "18650 4-cell Battery Pack", "qty": 1, "unit_price": 25},
        {"name": "USB Hub (7-port)", "qty": 1, "unit_price": 12},
        {"name": "Pelican-style Case", "qty": 1, "unit_price": 40},
    ],
    "offgrid_survival": [
        {"name": "Radxa Zero 3 4GB", "qty": 1, "unit_price": 45},
        {"name": "3.5-inch TFT Display", "qty": 1, "unit_price": 25},
        {"name": "Heltec LoRa V3 Module", "qty": 1, "unit_price": 18},
        {"name": "Solar Panel 20W (foldable)", "qty": 1, "unit_price": 50},
        {"name": "BMS 4S 18650 Board", "qty": 1, "unit_price": 8},
        {"name": "18650 Cells x8", "qty": 8, "unit_price": 5},
        {"name": "USB-C PD Trigger Board", "qty": 1, "unit_price": 4},
        {"name": "IP67 Waterproof Box", "qty": 1, "unit_price": 15},
    ],
    "cosplay_prop": [
        {"name": "ESP32-S3 Dev Board", "qty": 1, "unit_price": 12},
        {"name": "0.96in OLED Display", "qty": 1, "unit_price": 6},
        {"name": "WS2812B LED Strip (1m)", "qty": 1, "unit_price": 8},
        {"name": "Speaker Module (MAX98357)", "qty": 1, "unit_price": 5},
        {"name": "Lipo Battery 1000mAh", "qty": 1, "unit_price": 8},
        {"name": "NeoPixel Ring (16 LEDs)", "qty": 2, "unit_price": 6},
        {"name": "Momentary Push Buttons", "qty": 5, "unit_price": 1},
        {"name": "3D Printed Prop Shell", "qty": 1, "unit_price": 20},
    ],
    "retro_gaming": [
        {"name": "Raspberry Pi 5 4GB", "qty": 1, "unit_price": 60},
        {"name": "5-inch IPS Display (640x480)", "qty": 1, "unit_price": 35},
        {"name": "Joy-Con Style Joysticks", "qty": 2, "unit_price": 8},
        {"name": "Tactile Button Set (12pb)", "qty": 1, "unit_price": 5},
        {"name": "PowerBoost 1000C", "qty": 1, "unit_price": 10},
        {"name": "Lipo Battery 5000mAh", "qty": 1, "unit_price": 20},
        {"name": "Cooling Fan 30x30mm", "qty": 1, "unit_price": 5},
        {"name": "Custom Case (3D Print)", "qty": 1, "unit_price": 18},
    ],
    "ai_lab": [
        {"name": "Jetson Orin Nano 8GB", "qty": 1, "unit_price": 299},
        {"name": "15.6-inch Portable Monitor", "qty": 1, "unit_price": 150},
        {"name": "Mechanical Keyboard (Keychron)", "qty": 1, "unit_price": 65},
        {"name": "NP-F970 Dual Battery Kit", "qty": 1, "unit_price": 70},
        {"name": "Noctua 40mm Fan", "qty": 2, "unit_price": 15},
        {"name": "M.2 NVMe 1TB Drive", "qty": 1, "unit_price": 80},
        {"name": "TP-Link Archer T4U AC1300", "qty": 1, "unit_price": 25},
        {"name": "Aluminum Enclosure (Custom)", "qty": 1, "unit_price": 60},
    ],
    "media_server": [
        {"name": "Orange Pi 5 Plus 16GB", "qty": 1, "unit_price": 120},
        {"name": "7-inch HDMI Monitor", "qty": 1, "unit_price": 55},
        {"name": "USB 3.0 2TB External SSD", "qty": 1, "unit_price": 100},
        {"name": "Mini Keyboard w/ Touchpad", "qty": 1, "unit_price": 25},
        {"name": "18650 6-cell Power Bank", "qty": 1, "unit_price": 35},
        {"name": "USB-C PD 65W Charger", "qty": 1, "unit_price": 20},
        {"name": "Cooling Fan 50x50mm", "qty": 1, "unit_price": 6},
        {"name": "Acrylic Enclosure Kit", "qty": 1, "unit_price": 12},
    ],
    "research_station": [
        {"name": "Rock 5B 16GB", "qty": 1, "unit_price": 120},
        {"name": "10-inch HDMI Display", "qty": 1, "unit_price": 95},
        {"name": "SDR (RTL-SDR V4)", "qty": 1, "unit_price": 30},
        {"name": "Mechanical Keyboard 60%", "qty": 1, "unit_price": 40},
        {"name": "NP-F970 Battery System", "qty": 1, "unit_price": 55},
        {"name": "USB 3.0 Hub (10-port)", "qty": 1, "unit_price": 18},
        {"name": "SSD 512GB M.2 NVMe", "qty": 1, "unit_price": 50},
        {"name": "Aluminum Carrying Case", "qty": 1, "unit_price": 45},
    ],
    "security_audit": [
        {"name": "Orange Pi 5 Max 16GB", "qty": 1, "unit_price": 150},
        {"name": "5-inch HDMI Touch Display", "qty": 1, "unit_price": 55},
        {"name": "Hak5 Packet Squirrel", "qty": 1, "unit_price": 80},
        {"name": "WiFi Pineapple Nano", "qty": 1, "unit_price": 100},
        {"name": "RTL-SDR V4 with Antenna", "qty": 1, "unit_price": 35},
        {"name": "USB Ethernet Adapter", "qty": 1, "unit_price": 12},
        {"name": "PortaPack H2 (HackRF)", "qty": 1, "unit_price": 45},
        {"name": "Custom Security Case", "qty": 1, "unit_price": 50},
    ],
}


class BOMTracker:
    """Live BOM generation, project persistence, cost comparison, and alternative finding."""

    @staticmethod
    def _apply_tier(components: list, tier: str) -> list:
        tier_info = PRICE_TIERS.get(tier, PRICE_TIERS["standard"])
        mult = tier_info["multiplier"]
        result = []
        for c in components:
            entry = dict(c)
            entry["unit_price"] = round(entry["unit_price"] * mult, 2)
            result.append(entry)
        return result

    @staticmethod
    def generate_bom(component_keys: dict, tier: str = "standard") -> dict:
        if isinstance(component_keys, str):
            category = component_keys
            comps = _BOM_COMPONENT_LIBRARY.get(category, [])
            if not comps:
                return {"error": f"Unknown category: {category}", "available": list(_BOM_COMPONENT_LIBRARY.keys())}
            component_keys = {"items": [{"key": c["name"], "qty": c["qty"]} for c in comps]}

        category = component_keys if isinstance(component_keys, str) else None
        if isinstance(component_keys, dict) and "items" in component_keys:
            items_data = component_keys["items"]
        else:
            return {"error": "Invalid component data format"}

        items = []
        for item in items_data:
            if isinstance(item, dict) and "name" in item:
                items.append(item)

        if not items and category:
            source = _BOM_COMPONENT_LIBRARY.get(category, [])
            for c in source:
                items.append({"name": c["name"], "qty": c["qty"], "unit_price": c["unit_price"]})

        if not items:
            return {"error": "No components found"}

        tiered = BOMTracker._apply_tier(items, tier) if tier else items

        line_items = []
        subtotal = 0.0
        for c in tiered:
            total = round(c["qty"] * c.get("unit_price", c.get("price", 0)), 2)
            line_items.append({
                "name": c["name"],
                "qty": c["qty"],
                "unit_price": c.get("unit_price", c.get("price", 0)),
                "total": total,
            })
            subtotal += total

        tax_rate = 0.08
        tax = round(subtotal * tax_rate, 2)
        shipping = 12.50 if subtotal < 200 else 0.0
        grand_total = round(subtotal + tax + shipping, 2)
        tier_info = PRICE_TIERS.get(tier, PRICE_TIERS["standard"])

        savings_tips = []
        if subtotal > 300:
            savings_tips.append("Consider buying in bulk for component discounts")
        if shipping > 0:
            savings_tips.append("Add more items to qualify for free shipping (over $200)")
        if tier == "premium":
            savings_tips.append("Downshift to 'standard' tier to save ~33%")
        elif tier == "budget" and subtotal < 50:
            savings_tips.append("Consider AliExpress for better pricing on budget builds")
        savings_tips.append("Check local electronics recyclers for used components")

        return {
            "items": line_items,
            "subtotal": round(subtotal, 2),
            "tax": tax,
            "shipping": shipping,
            "grand_total": grand_total,
            "tier": tier,
            "tier_description": tier_info["description"],
            "savings_tips": savings_tips,
        }

    @staticmethod
    def _bom_path():
        import os as _os
        return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), BOM_PROJECTS_FILE)

    @staticmethod
    def save_project(name: str, bom_data: dict) -> str:
        import json as _j
        path = BOMTracker._bom_path()
        try:
            with open(path, "r", encoding="utf-8") as f:
                projects = _j.load(f)
        except:
            projects = {}
        projects[name] = {"saved_at": time.strftime("%Y-%m-%d %H:%M:%S"), "bom": bom_data}
        with open(path, "w", encoding="utf-8") as f:
            _j.dump(projects, f, indent=2, ensure_ascii=False)
        total = bom_data.get("grand_total", 0)
        return f"<b>Project saved:</b> {name}\nTotal: ${total}\nItems: {len(bom_data.get('items', []))}\nTier: {bom_data.get('tier', 'standard')}"

    @staticmethod
    def load_project(name: str) -> dict:
        import json as _j
        path = BOMTracker._bom_path()
        try:
            with open(path, "r", encoding="utf-8") as f:
                projects = _j.load(f)
        except:
            return {"error": "No saved projects found"}
        p = projects.get(name)
        if not p:
            return {"error": f"Project '{name}' not found", "saved": list(projects.keys())}
        return p

    @staticmethod
    def list_projects() -> str:
        import json as _j
        path = BOMTracker._bom_path()
        try:
            with open(path, "r", encoding="utf-8") as f:
                projects = _j.load(f)
        except:
            return "No saved BOM projects."
        if not projects:
            return "No saved BOM projects."
        lines = ["<b>Saved BOM Projects</b>\n"]
        for name, p in sorted(projects.items()):
            bom = p.get("bom", {})
            total = bom.get("grand_total", "?")
            items = len(bom.get("items", []))
            saved = p.get("saved_at", "?")
            lines.append(f"<b>{name}</b> — ${total} ({items} items)")
            lines.append(f"  Saved: {saved}")
        return "\n".join(lines)

    @staticmethod
    def compare_boms(project_a: str, project_b: str) -> str:
        a = BOMTracker.load_project(project_a)
        b = BOMTracker.load_project(project_b)
        if "error" in a:
            return f"Project A error: {a.get('error')}"
        if "error" in b:
            return f"Project B error: {b.get('error')}"

        bom_a = a.get("bom", {})
        bom_b = b.get("bom", {})

        items_a = {i["name"]: i for i in bom_a.get("items", [])}
        items_b = {i["name"]: i for i in bom_b.get("items", [])}
        all_names = sorted(set(list(items_a.keys()) + list(items_b.keys())))

        lines = [
            f"<b>BOM Comparison: {project_a} vs {project_b}</b>\n",
            f"{'Component':<30} {'Qty A':<8} {'Price A':<10} {'Qty B':<8} {'Price B':<10}",
            "-" * 66,
        ]
        for name in all_names:
            ia = items_a.get(name, {})
            ib = items_b.get(name, {})
            qa = str(ia.get("qty", "-")) if ia else "-"
            pa = f"${ia.get('total', 0):.2f}" if ia else "-"
            qb = str(ib.get("qty", "-")) if ib else "-"
            pb = f"${ib.get('total', 0):.2f}" if ib else "-"
            lines.append(f"{name:<30} {qa:<8} {pa:<10} {qb:<8} {pb:<10}")

        lines.append("")
        lines.append(f"{'TOTAL':<30} {'':<8} ${bom_a.get('grand_total', 0):<7.2f} {'':<8} ${bom_b.get('grand_total', 0):.2f}")
        diff = abs(bom_a.get('grand_total', 0) - bom_b.get('grand_total', 0))
        if bom_a.get('grand_total', 0) < bom_b.get('grand_total', 0):
            lines.append(f"  {project_a} is ${diff:.2f} cheaper ✓")
        else:
            lines.append(f"  {project_b} is ${diff:.2f} cheaper ✓")
        return "\n".join(lines)

    @staticmethod
    def find_alternatives(component_key: str, max_price: int) -> str:
        results = []
        for cat, comps in _BOM_COMPONENT_LIBRARY.items():
            for c in comps:
                if component_key.lower() in c["name"].lower() and c["unit_price"] <= max_price:
                    results.append((c["name"], c["unit_price"], c["qty"], cat))
                name_lower = c["name"].lower()
                key_lower = component_key.lower()
                if key_lower in name_lower and c["unit_price"] <= max_price:
                    results.append((c["name"], c["unit_price"], c["qty"], cat))

        if not results:
            for cat, comps in _BOM_COMPONENT_LIBRARY.items():
                for c in comps:
                    if c["unit_price"] <= max_price:
                        results.append((c["name"], c["unit_price"], c["qty"], cat))
            if not results:
                return f"No components found under ${max_price} for '{component_key}'."

        seen = set()
        uniq = []
        for r in results:
            if r[0] not in seen:
                seen.add(r[0])
                uniq.append(r)
        uniq.sort(key=lambda x: x[1])
        lines = [f"<b>Alternatives for '{component_key}' (max ${max_price})</b>\n"]
        for name, price, qty, cat in uniq[:12]:
            lines.append(f"  {name} — ${price:.2f}ea (from {cat})")
        lines.append("")
        lines.append(f"<i>Found {len(uniq)} alternatives within budget</i>")
        return "\n".join(lines)

    @staticmethod
    def price_tier_info() -> str:
        lines = ["<b>BOM Price Tiers</b>\n"]
        for tid, t in PRICE_TIERS.items():
            mult_pct = int((t["multiplier"] - 1.0) * 100)
            if mult_pct > 0:
                line = f"  <b>{tid.title()}</b>: +{mult_pct}% | {t['description']}"
            elif mult_pct < 0:
                line = f"  <b>{tid.title()}</b>: {mult_pct}% | {t['description']}"
            else:
                line = f"  <b>{tid.title()}</b>: Baseline | {t['description']}"
            lines.append(line)
        lines.append("")
        lines.append("Usage: /bomtrack generate &lt;category&gt; [tier]")
        lines.append("Categories: " + ", ".join(_BOM_COMPONENT_LIBRARY.keys()))
        return "\n".join(lines)


# ============================================================
# v6.5 — BUILD PROFILE MANAGER
# ============================================================
BUILD_PROFILES_DATABASE = {
    "writerdeck": {
        "name": "WriterDeck", "description": "Distraction-free writing machine for authors, journalists, and note-takers",
        "sbc_recommendation": "Radxa Zero 3 / Raspberry Pi 5", "display_size_inches": 7.0,
        "battery_min_wh": 50, "os_recommendation": "DietPi / Kali Linux headless", "case_style": "Clamshell laptop",
        "keyboard_type": "Mechanical (Cherry MX Brown)", "cooling_required": False, "wifi_required": True,
        "lora_required": False, "sdr_required": False, "ram_min_gb": 4, "storage_min_gb": 128,
        "weight_target_kg": 1.2, "color_palette": "Monochrome + Warm White", "led_accent_color": "#FFD700",
        "switches": "Tactile silent", "aesthetic_vibe": "Journal, Understated, Retro-future",
        "notes": "Focus on battery life and keyboard feel. E-ink display optional for extended battery.",
        "example_commands": ["writerdeck distraction-free setup", "focus word processing on Radxa"],
    },
    "pentest_kali": {
        "name": "Pentest Kali Deck", "description": "Portable penetration testing workstation with Kali Linux",
        "sbc_recommendation": "Orange Pi 5 Max 16GB", "display_size_inches": 5.0,
        "battery_min_wh": 80, "os_recommendation": "Kali Linux ARM", "case_style": "Tactical hard case (Pelican)",
        "keyboard_type": "Mini keyboard with trackpad", "cooling_required": True, "wifi_required": True,
        "lora_required": False, "sdr_required": True, "ram_min_gb": 16, "storage_min_gb": 256,
        "weight_target_kg": 2.0, "color_palette": "Black + Red accents", "led_accent_color": "#FF0000",
        "switches": "Clickly tactile switches", "aesthetic_vibe": "Tactical, Aggressive, Dark Ops",
        "notes": "Prioritize SDR and WiFi adapters. Include Faraday bag option.",
        "example_commands": ["deauth attack on Orange Pi", "RTL-SDR frequency scanning"],
    },
    "offgrid_survival": {
        "name": "Off-Grid Survival Deck", "description": "Solar-powered field computer for emergencies and remote operations",
        "sbc_recommendation": "Radxa Zero 3 4GB", "display_size_inches": 3.5,
        "battery_min_wh": 150, "os_recommendation": "Custom Linux (minimal)", "case_style": "Rugged IP67 box",
        "keyboard_type": "Membrane sealed keypad", "cooling_required": False, "wifi_required": False,
        "lora_required": True, "sdr_required": True, "ram_min_gb": 4, "storage_min_gb": 64,
        "weight_target_kg": 1.5, "color_palette": "Olive Drab + Amber", "led_accent_color": "#FFBF00",
        "switches": "Sealed tactile buttons", "aesthetic_vibe": "Military, Rugged, Functional",
        "notes": "Solar charging with MPPT, LoRa mesh for off-grid comms, weather station sensors",
        "example_commands": ["solar powered cyberdeck build", "offgrid LoRa mesh node"],
    },
    "cosplay_prop": {
        "name": "Cosplay Prop Deck", "description": "Lightweight cyberdeck prop with LEDs and sound for conventions",
        "sbc_recommendation": "ESP32-S3", "display_size_inches": 3.5,
        "battery_min_wh": 10, "os_recommendation": "Arduino/ESP-IDF", "case_style": "Custom 3D printed prop",
        "keyboard_type": "Custom capacitive touch", "cooling_required": False, "wifi_required": True,
        "lora_required": False, "sdr_required": False, "ram_min_gb": 1, "storage_min_gb": 16,
        "weight_target_kg": 0.5, "color_palette": "Neon Cyan + Pink", "led_accent_color": "#FF00FF",
        "switches": "RGB LED buttons", "aesthetic_vibe": "Cyberpunk, Neon, Dystopian",
        "notes": "Focus on visual impact. Programmable LED matrix + audio effects.",
        "example_commands": ["cyberpunk cosplay build", "cosplay prop cyberdeck with LEDs"],
    },
    "retro_gaming": {
        "name": "Retro Gaming Deck", "description": "Retro gaming handheld or portable emulation station",
        "sbc_recommendation": "Raspberry Pi 5 4GB", "display_size_inches": 5.0,
        "battery_min_wh": 40, "os_recommendation": "RetroPie / Batocera", "case_style": "Handheld console",
        "keyboard_type": "Gamepad buttons + D-pad", "cooling_required": True, "wifi_required": True,
        "lora_required": False, "sdr_required": False, "ram_min_gb": 4, "storage_min_gb": 128,
        "weight_target_kg": 0.6, "color_palette": "Retro Grey + Neon Green", "led_accent_color": "#00FF00",
        "switches": "Tactile silent", "aesthetic_vibe": "Retro, Playful, Nostalgic",
        "notes": "IPS display for better viewing angles. Consider analog sticks for N64/PSX.",
        "example_commands": ["pi 5 retro gaming handheld", "full retro emulation deck"],
    },
    "ai_lab": {
        "name": "AI Lab Deck", "description": "Portable AI workstation for running local LLMs and edge inference",
        "sbc_recommendation": "Jetson Orin Nano 8GB", "display_size_inches": 15.6,
        "battery_min_wh": 200, "os_recommendation": "Ubuntu 24.04 LTS", "case_style": "Aluminum briefcase",
        "keyboard_type": "Full size mechanical (Keychron)", "cooling_required": True, "wifi_required": True,
        "lora_required": False, "sdr_required": False, "ram_min_gb": 16, "storage_min_gb": 1000,
        "weight_target_kg": 3.5, "color_palette": "Dark Grey + Cyan", "led_accent_color": "#00FFFF",
        "switches": "Tactile (Cherry MX Brown)", "aesthetic_vibe": "Professional, Laboratory, Modern",
        "notes": "Focus on CUDA cores and VRAM for LLM inference. Active cooling essential.",
        "example_commands": ["jetson orin nano portable ai", "local LLM cyberdeck build"],
    },
    "media_server": {
        "name": "Media Server Deck", "description": "Portable media server for travel, events, and content creation",
        "sbc_recommendation": "Orange Pi 5 Plus 16GB", "display_size_inches": 7.0,
        "battery_min_wh": 100, "os_recommendation": "Ubuntu Server / OMV", "case_style": "Transport briefcase",
        "keyboard_type": "Mini keyboard with trackpad", "cooling_required": True, "wifi_required": True,
        "lora_required": False, "sdr_required": False, "ram_min_gb": 16, "storage_min_gb": 2000,
        "weight_target_kg": 2.5, "color_palette": "Silver + Blue", "led_accent_color": "#4488FF",
        "switches": "Silent membrane", "aesthetic_vibe": "Professional, Clean, AV-gear",
        "notes": "Large NVMe storage, USB-C PD for fast charging. Plex/Jellyfin ready.",
        "example_commands": ["portable plex server build", "travel media cyberdeck"],
    },
    "research_station": {
        "name": "Research Station Deck", "description": "Portable research workstation with offline knowledge base and analysis tools",
        "sbc_recommendation": "Rock 5B 16GB", "display_size_inches": 10.0,
        "battery_min_wh": 120, "os_recommendation": "Ubuntu 24.04 / Kali", "case_style": "Clamshell with document storage",
        "keyboard_type": "Full size mechanical 60%", "cooling_required": True, "wifi_required": True,
        "lora_required": True, "sdr_required": True, "ram_min_gb": 16, "storage_min_gb": 512,
        "weight_target_kg": 2.8, "color_palette": "Navy + Gold", "led_accent_color": "#D4AF37",
        "switches": "Tactile (Cherry MX Clear)", "aesthetic_vibe": "Academic, Explorer, Archivist",
        "notes": "Kiwix ZIM offline knowledge base, SDR for spectrum analysis, LoRa for field comms",
        "example_commands": ["offline research cyberdeck", "field researcher workstation"],
    },
    "security_audit": {
        "name": "Security Audit Deck", "description": "Professional security auditing toolkit with dedicated hardware modules",
        "sbc_recommendation": "Orange Pi 5 Max 16GB", "display_size_inches": 5.0,
        "battery_min_wh": 100, "os_recommendation": "Kali Linux + Parrot OS", "case_style": "Hard case with foam cutouts",
        "keyboard_type": "Mini keyboard with trackpad", "cooling_required": True, "wifi_required": True,
        "lora_required": False, "sdr_required": True, "ram_min_gb": 16, "storage_min_gb": 512,
        "weight_target_kg": 2.2, "color_palette": "Black + Red + Yellow", "led_accent_color": "#FF6600",
        "switches": "Tactile silent", "aesthetic_vibe": "Professional, Stealth, Tactical",
        "notes": "Include WiFi Pineapple, HackRF, USB Ethernet, Faraday enclosure option",
        "example_commands": ["pentest cyberdeck build", "network audit portable workstation"],
    },
}

PROFILE_OVERRIDE_RULES = {
    "writerdeck": {"sbc_score_filter": {"min_cores": 4, "min_ram_gb": 4, "prefer_low_power": True}, "display_picker": {"min_size": 5, "prefer_eink": True}, "battery_calculator": {"min_wh": 50, "target_runtime_h": 12}},
    "pentest_kali": {"sbc_score_filter": {"min_cores": 8, "min_ram_gb": 8, "prefer_gpu": True}, "display_picker": {"min_size": 4, "prefer_touch": True}, "battery_calculator": {"min_wh": 80, "target_runtime_h": 6}},
    "offgrid_survival": {"sbc_score_filter": {"min_cores": 2, "min_ram_gb": 2, "prefer_low_power": True}, "display_picker": {"min_size": 2.5, "prefer_sunlight_readable": True}, "battery_calculator": {"min_wh": 150, "target_runtime_h": 24}},
    "cosplay_prop": {"sbc_score_filter": {"min_cores": 2, "min_ram_gb": 1, "prefer_low_power": True}, "display_picker": {"min_size": 2, "prefer_oled": True}, "battery_calculator": {"min_wh": 10, "target_runtime_h": 4}},
    "retro_gaming": {"sbc_score_filter": {"min_cores": 4, "min_ram_gb": 4, "prefer_gpu": True}, "display_picker": {"min_size": 3.5, "prefer_ips": True}, "battery_calculator": {"min_wh": 40, "target_runtime_h": 5}},
    "ai_lab": {"sbc_score_filter": {"min_cores": 8, "min_ram_gb": 16, "require_cuda": True}, "display_picker": {"min_size": 13, "prefer_higher_res": True}, "battery_calculator": {"min_wh": 200, "target_runtime_h": 4}},
    "media_server": {"sbc_score_filter": {"min_cores": 6, "min_ram_gb": 8, "prefer_usb3": True}, "display_picker": {"min_size": 7, "prefer_higher_res": True}, "battery_calculator": {"min_wh": 100, "target_runtime_h": 6}},
    "research_station": {"sbc_score_filter": {"min_cores": 6, "min_ram_gb": 8, "prefer_gpio": True}, "display_picker": {"min_size": 10, "prefer_higher_res": True}, "battery_calculator": {"min_wh": 120, "target_runtime_h": 8}},
    "security_audit": {"sbc_score_filter": {"min_cores": 8, "min_ram_gb": 16, "prefer_usb_ports": True}, "display_picker": {"min_size": 5, "prefer_touch": True}, "battery_calculator": {"min_wh": 100, "target_runtime_h": 6}},
}


class BuildProfileManager:
    """Cyberdeck build profile management — categorized deck templates with config overrides."""

    @staticmethod
    def get_profile(name: str) -> dict:
        name = name.lower().replace(" ", "_")
        p = BUILD_PROFILES_DATABASE.get(name)
        if not p:
            avail = ", ".join(BUILD_PROFILES_DATABASE.keys())
            return {"error": f"Unknown profile: {name}", "available": list(BUILD_PROFILES_DATABASE.keys())}
        return p

    @staticmethod
    def list_profiles() -> str:
        lines = ["<b>Build Profiles</b>\n"]
        for pid, p in BUILD_PROFILES_DATABASE.items():
            lines.append(f"<b>{p['name']}</b> — /profile {pid}")
            lines.append(f"  {p['description']}")
            lines.append(f"  SBC: {p['sbc_recommendation']} | Display: {p['display_size_inches']}\" | RAM: {p['ram_min_gb']}GB")
            lines.append(f"  OS: {p['os_recommendation']} | Vibe: {p['aesthetic_vibe']}")
            lines.append("")
        lines.append("Usage: /profile &lt;name&gt; — view profile details")
        lines.append("Usage: /profile &lt;name&gt; apply — get config overrides")
        return "\n".join(lines)

    @staticmethod
    def apply_profile_config(name: str) -> dict:
        name = name.lower().replace(" ", "_")
        profile = BUILD_PROFILES_DATABASE.get(name)
        if not profile:
            return {"error": f"Unknown profile: {name}"}
        overrides = PROFILE_OVERRIDE_RULES.get(name, {})
        return {
            "profile": profile["name"],
            "sbc_filter": overrides.get("sbc_score_filter", {}),
            "display_filter": overrides.get("display_picker", {}),
            "battery_filter": overrides.get("battery_calculator", {}),
            "os_config": {"os": profile["os_recommendation"], "cooling": profile["cooling_required"]},
            "aesthetic_config": {
                "color_palette": profile["color_palette"],
                "led_color": profile["led_accent_color"],
                "switches": profile["switches"],
                "vibe": profile["aesthetic_vibe"],
                "case": profile["case_style"],
            },
        }

    @staticmethod
    def compare_profiles(a: str, b: str) -> str:
        pa = BuildProfileManager.get_profile(a)
        pb = BuildProfileManager.get_profile(b)
        if "error" in pa:
            return f"Profile A error: {pa.get('error')}"
        if "error" in pb:
            return f"Profile B error: {pb.get('error')}"

        keys = ["name", "sbc_recommendation", "display_size_inches", "battery_min_wh",
                "os_recommendation", "case_style", "keyboard_type", "ram_min_gb",
                "storage_min_gb", "weight_target_kg", "aesthetic_vibe"]
        lines = [f"<b>Profile Comparison: {pa['name']} vs {pb['name']}</b>\n"]
        lines.append(f"{'Attribute':<25} {pa['name']:<35} {pb['name']:<35}")
        lines.append("-" * 95)
        for k in keys:
            va = str(pa.get(k, "-"))
            vb = str(pb.get(k, "-"))
            lines.append(f"{k:<25} {va:<35} {vb:<35}")
        lines.append("")
        lines.append("<b>Key differences:</b>")
        diff_count = 0
        for k in keys:
            va = pa.get(k)
            vb = pb.get(k)
            if va != vb:
                diff_count += 1
                if diff_count <= 5:
                    lines.append(f"  • {k}: <b>{va}</b> → <b>{vb}</b>")
        if diff_count == 0:
            lines.append("  Profiles are identical")
        return "\n".join(lines)

    @staticmethod
    def suggest_profile_for_description(desc: str) -> str:
        desc_lower = desc.lower()
        keywords = {
            "writerdeck": ["write", "author", "journalist", "note", "distraction-free", "word", "typing", "prose", "manuscript"],
            "pentest_kali": ["pentest", "hack", "security", "kali", "audit", "exploit", "deauth", "wifi", "network", "scan"],
            "offgrid_survival": ["survival", "offgrid", "solar", "remote", "emergency", "camping", "field", "disaster"],
            "cosplay_prop": ["cosplay", "prop", "costume", "led", "neon", "convention", "decoration", "display"],
            "retro_gaming": ["game", "retro", "emulat", "nintendo", "play", "console", "handheld"],
            "ai_lab": ["ai", "llm", "machine learning", "inference", "neural", "cuda", "tensor", "ml"],
            "media_server": ["media", "server", "plex", "movie", "music", "video", "stream", "storage"],
            "research_station": ["research", "study", "analysis", "field work", "scientist", "academic", "offline", "knowledge"],
            "security_audit": ["audit", "professional", "enterprise", "soc", "incident", "forensic", "compliance"],
        }
        scores = {}
        for pid, kws in keywords.items():
            score = sum(2 for kw in kws if kw in desc_lower)
            if score > 0:
                scores[pid] = score

        if not scores:
            lines = ["<b>No strong match found.</b>", "", "Available profiles:"]
            for pid, p in BUILD_PROFILES_DATABASE.items():
                lines.append(f"  • /profile {pid} — {p['name']}: {p['description']}")
            return "\n".join(lines)

        best = max(scores, key=scores.get)
        p = BUILD_PROFILES_DATABASE[best]
        return f"<b>Best matching profile:</b> {p['name']}\nDescription: {p['description']}\nSBC: {p['sbc_recommendation']}\nOS: {p['os_recommendation']}\n\nUse: /profile {best}\nUse: /profile {best} apply"


# ============================================================
# OLLAMA MODEL DATABASE
# ============================================================
OLLAMA_MODEL_DATABASE = {
    "phi3:mini": {"name": "Phi-3 Mini", "size_b": 3.8, "ram_min_gb": 4, "quantization": "Q4_K_M", "tokens_sec_est": "20-40", "best_for": ["coding", "reasoning", "general"], "description": "Microsoft's efficient 3.8B model, great for code and logic on low-RAM SBCs", "command": "ollama pull phi3:mini"},
    "llama3.2:1b": {"name": "Llama 3.2 1B", "size_b": 1.0, "ram_min_gb": 2, "quantization": "Q4_K_M", "tokens_sec_est": "40-60", "best_for": ["chat", "general", "classification"], "description": "Ultra-light 1B model for the tightest RAM budgets", "command": "ollama pull llama3.2:1b"},
    "llama3.2:3b": {"name": "Llama 3.2 3B", "size_b": 3.0, "ram_min_gb": 4, "quantization": "Q4_K_M", "tokens_sec_est": "25-45", "best_for": ["chat", "writing", "reasoning"], "description": "Balanced 3B model, good quality-to-size ratio for SBCs", "command": "ollama pull llama3.2:3b"},
    "llama3.1:8b": {"name": "Llama 3.1 8B", "size_b": 8.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "10-20", "best_for": ["chat", "coding", "reasoning", "analysis"], "description": "Meta's capable 8B model, strong general-purpose on 8GB+ SBCs", "command": "ollama pull llama3.1:8b"},
    "mistral:7b": {"name": "Mistral 7B", "size_b": 7.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "12-22", "best_for": ["chat", "coding", "reasoning"], "description": "Mistral's efficient 7B, excellent quality for its size", "command": "ollama pull mistral:7b"},
    "codellama:7b": {"name": "CodeLlama 7B", "size_b": 7.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "10-18", "best_for": ["coding", "code-review", "debugging"], "description": "Meta's code-specialized 7B, great for on-device code assistance", "command": "ollama pull codellama:7b"},
    "deepseek-coder:6.7b": {"name": "DeepSeek Coder 6.7B", "size_b": 6.7, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "10-18", "best_for": ["coding", "code-completion", "reasoning"], "description": "DeepSeek's code model, strong at multi-file coding tasks", "command": "ollama pull deepseek-coder:6.7b"},
    "qwen2.5:7b": {"name": "Qwen 2.5 7B", "size_b": 7.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "12-20", "best_for": ["chat", "reasoning", "coding", "writing"], "description": "Alibaba's strong 7B, multilingual and good at reasoning", "command": "ollama pull qwen2.5:7b"},
    "gemma2:9b": {"name": "Gemma 2 9B", "size_b": 9.0, "ram_min_gb": 12, "quantization": "Q4_K_M", "tokens_sec_est": "8-15", "best_for": ["chat", "reasoning", "analysis", "research"], "description": "Google's 9B, strong instruction following and safety", "command": "ollama pull gemma2:9b"},
    "phi3.5:3.8b": {"name": "Phi-3.5 3.8B", "size_b": 3.8, "ram_min_gb": 4, "quantization": "Q4_K_M", "tokens_sec_est": "22-40", "best_for": ["coding", "reasoning", "math"], "description": "Microsoft's updated 3.8B, punches above its weight class", "command": "ollama pull phi3.5:3.8b"},
    "llama3.2-vision:11b": {"name": "Llama 3.2 Vision 11B", "size_b": 11.0, "ram_min_gb": 16, "quantization": "Q4_K_M", "tokens_sec_est": "5-10", "best_for": ["vision", "image-analysis", "captioning"], "description": "Meta's vision model, needs 16GB+ for image analysis", "command": "ollama pull llama3.2-vision:11b"},
    "starcoder2:7b": {"name": "StarCoder2 7B", "size_b": 7.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "10-18", "best_for": ["coding", "code-completion", "debugging"], "description": "HuggingFace's code model, trained on 600+ languages", "command": "ollama pull starcoder2:7b"},
    "dolphin-mixtral:8x7b": {"name": "Dolphin Mixtral 8x7B", "size_b": 56.0, "ram_min_gb": 48, "quantization": "Q4_K_M", "tokens_sec_est": "2-5", "best_for": ["reasoning", "coding", "analysis", "research"], "description": "Mixtral MOE, needs 48GB RAM — high-end SBCs only", "command": "ollama pull dolphin-mixtral:8x7b"},
    "neural-chat:7b": {"name": "Neural Chat 7B", "size_b": 7.0, "ram_min_gb": 8, "quantization": "Q4_K_M", "tokens_sec_est": "12-22", "best_for": ["chat", "roleplay", "conversation"], "description": "Intel's fine-tuned Mistral 7B for chat, very conversational", "command": "ollama pull neural-chat:7b"},
    "tinyllama:1.1b": {"name": "TinyLlama 1.1B", "size_b": 1.1, "ram_min_gb": 2, "quantization": "Q4_K_M", "tokens_sec_est": "45-70", "best_for": ["chat", "general", "classification"], "description": "Ultra-compact 1.1B, fits on any SBC with 2GB RAM", "command": "ollama pull tinyllama:1.1b"},
}

SBC_TO_RECOMMENDED_MODEL = {
    "rpi5_8gb": "llama3.2:3b",
    "rpi5_16gb": "llama3.1:8b",
    "jetson_orin_nano": "llama3.1:8b",
    "orangepi5_max": "qwen2.5:7b",
    "rock5b": "mistral:7b",
    "radxa_zero3": "phi3:mini",
}


class OllamaAssistant:
    """Ollama AI model recommendations and setup for SBC cyberdecks."""

    @staticmethod
    def get_ollama_models():
        return list(OLLAMA_MODEL_DATABASE.keys())

    @staticmethod
    def recommend_model(sbc_key: str) -> str:
        if sbc_key in SBC_TO_RECOMMENDED_MODEL:
            mk = SBC_TO_RECOMMENDED_MODEL[sbc_key]
            m = OLLAMA_MODEL_DATABASE.get(mk)
            if m:
                return f"<b>Recommended model for {sbc_key}:</b>\nModel: {m['name']} ({mk})\nRAM needed: {m['ram_min_gb']}GB\nEst. tokens/sec: {m['tokens_sec_est']}\nBest for: {', '.join(m['best_for'])}"
        sbcs_list = "\n".join(f"  • {k}" for k in SBC_TO_RECOMMENDED_MODEL)
        return f"<b>Available SBCs:</b>\n{sbcs_list}\n\nUsage: /ollama recommend &lt;sbc_key&gt;"

    @staticmethod
    def generate_setup_cmds(model_key: str, sbc_key: str) -> str:
        model = OLLAMA_MODEL_DATABASE.get(model_key)
        if not model:
            return f"Unknown model: {model_key}. See /ollama for list."
        lines = [f"<b>Ollama Setup for {model['name']} on {sbc_key}</b>", ""]
        lines.append("<b>1. Install Ollama:</b>")
        lines.append(f"  <code>curl -fsSL https://ollama.com/install.sh | sh</code>")
        lines.append("")
        lines.append("<b>2. Pull model:</b>")
        lines.append(f"  <code>{model['command']}</code>")
        lines.append(f"  Estimated size: {model['size_b']}GB download")
        lines.append("")
        lines.append("<b>3. Run model:</b>")
        lines.append(f"  <code>ollama run {model_key}</code>")
        lines.append("")
        lines.append("<b>4. Systemd service (auto-start):</b>")
        lines.append("  <code>sudo systemctl edit ollama.service</code>")
        lines.append("  Add: <code>Environment=OLLAMA_HOST=0.0.0.0:11434</code>")
        lines.append("  <code>sudo systemctl restart ollama</code>")
        lines.append("")
        lines.append("<b>5. API test:</b>")
        lines.append("  <code>curl http://localhost:11434/api/generate -d '{\"model\":\"%s\",\"prompt\":\"Hello\"}'</code>" % model_key)
        lines.append("")
        lines.append(f"<b>RAM requirement:</b> {model['ram_min_gb']}GB free")
        lines.append(f"<b>Quantization:</b> {model['quantization']}")
        lines.append(f"<b>Est. tokens/sec:</b> {model['tokens_sec_est']} on capable SBC")
        return "\n".join(lines)

    @staticmethod
    def estimate_tokens_per_sec(sbc_key: str, model_key: str) -> str:
        sbc_tiers = {
            "rpi5_8gb": {"base_tps": 25, "desc": "RPi 5 8GB"},
            "rpi5_16gb": {"base_tps": 30, "desc": "RPi 5 16GB"},
            "jetson_orin_nano": {"base_tps": 45, "desc": "Jetson Orin Nano"},
            "orangepi5_max": {"base_tps": 35, "desc": "Orange Pi 5 Max"},
            "rock5b": {"base_tps": 32, "desc": "Rock 5B"},
            "radxa_zero3": {"base_tps": 18, "desc": "Radxa Zero 3"},
        }
        model = OLLAMA_MODEL_DATABASE.get(model_key)
        sbc = sbc_tiers.get(sbc_key)
        if not model:
            return f"Unknown model: {model_key}"
        if not sbc:
            return f"Unknown SBC: {sbc_key}. Known: {', '.join(sbc_tiers.keys())}"
        size_factor = max(1.0, 8.0 / max(model["size_b"], 1.0))
        tps = int(sbc["base_tps"] * size_factor * 0.5)
        return f"<b>Est. tokens/sec:</b> {tps} tok/s\nSBC: {sbc['desc']}\nModel: {model['name']} ({model['size_b']}B)\nQuantization: {model['quantization']}"

    @staticmethod
    def suggest_quantization(model_key: str, ram_gb: int) -> str:
        model = OLLAMA_MODEL_DATABASE.get(model_key)
        if not model:
            return f"Unknown model: {model_key}"
        model_size = model["size_b"]
        if ram_gb >= model_size * 2:
            q = "Q8_0 (highest quality)"
        elif ram_gb >= model_size * 1.2:
            q = "Q4_K_M (balanced)"
        elif ram_gb >= model_size * 0.7:
            q = "Q3_K_S (compact)"
        else:
            q = "Q2_K (ultra compact, quality loss)"
        lines = [
            f"<b>Quantization advice for {model['name']} on {ram_gb}GB RAM</b>",
            f"Model size: {model_size}B",
            f"Available RAM: {ram_gb}GB",
            f"Recommended: <b>{q}</b>",
            "",
            "Pull with quant: <code>ollama pull %s --quantize %s</code>" % (model_key, q.split(" ")[0]),
        ]
        if ram_gb < model_size * 0.7:
            lines.append("")
            lines.append("<b>⚠ Warning:</b> This model may not run well on this much RAM.")
            lines.append("Consider a smaller model like phi3:mini or llama3.2:1b.")
        return "\n".join(lines)


# ============================================================
# KIWIX/ZIM KNOWLEDGE BASE
# ============================================================
ZIM_DATABASE = {
    "wikipedia_en": {"name": "Wikipedia English", "description": "Full English Wikipedia — 6M+ articles", "size_mb": 45000, "language": "en", "content_type": "encyclopedia", "best_for": ["research", "education", "survival", "writerdeck"], "zim_url": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi.zim", "kiwix_serve_url": "http://localhost:8080/wikipedia_en"},
    "wiktionary_en": {"name": "Wiktionary English", "description": "English dictionary and thesaurus", "size_mb": 2500, "language": "en", "content_type": "dictionary", "best_for": ["writerdeck", "education", "research"], "zim_url": "https://download.kiwix.org/zim/wiktionary/wiktionary_en_all_maxi.zim", "kiwix_serve_url": "http://localhost:8080/wiktionary_en"},
    "wikibooks_en": {"name": "Wikibooks English", "description": "Open textbooks and manuals", "size_mb": 800, "language": "en", "content_type": "textbooks", "best_for": ["education", "coding", "research"], "zim_url": "https://download.kiwix.org/zim/wikibooks/wikibooks_en_all_maxi.zim", "kiwix_serve_url": "http://localhost:8080/wikibooks_en"},
    "wikiversity_en": {"name": "Wikiversity English", "description": "Open learning resources and courses", "size_mb": 400, "language": "en", "content_type": "education", "best_for": ["education", "research"], "zim_url": "https://download.kiwix.org/zim/wikiversity/wikiversity_en_all.zim", "kiwix_serve_url": "http://localhost:8080/wikiversity_en"},
    "wikivoyage_en": {"name": "Wikivoyage English", "description": "Travel guides for worldwide destinations", "size_mb": 600, "language": "en", "content_type": "travel", "best_for": ["survival", "research"], "zim_url": "https://download.kiwix.org/zim/wikivoyage/wikivoyage_en_all.zim", "kiwix_serve_url": "http://localhost:8080/wikivoyage_en"},
    "wikisource_en": {"name": "Wikisource English", "description": "Free content textual sources", "size_mb": 1200, "language": "en", "content_type": "library", "best_for": ["research", "writerdeck", "education"], "zim_url": "https://download.kiwix.org/zim/wikisource/wikisource_en_all.zim", "kiwix_serve_url": "http://localhost:8080/wikisource_en"},
    "wikiquote_en": {"name": "Wikiquote English", "description": "Collection of quotations", "size_mb": 300, "language": "en", "content_type": "reference", "best_for": ["writerdeck", "education"], "zim_url": "https://download.kiwix.org/zim/wikiquote/wikiquote_en_all.zim", "kiwix_serve_url": "http://localhost:8080/wikiquote_en"},
    "wikinews_en": {"name": "Wikinews English", "description": "Free news content archive", "size_mb": 500, "language": "en", "content_type": "news", "best_for": ["research", "survival"], "zim_url": "https://download.kiwix.org/zim/wikinews/wikinews_en_all.zim", "kiwix_serve_url": "http://localhost:8080/wikinews_en"},
    "stackoverflow": {"name": "Stack Overflow", "description": "Stack Overflow Q&A archive — coding answers", "size_mb": 42000, "language": "en", "content_type": "q&a", "best_for": ["coding", "research", "education"], "zim_url": "https://download.kiwix.org/zim/stackoverflow/stackoverflow.com.zip", "kiwix_serve_url": "http://localhost:8080/stackoverflow"},
    "khan_academy": {"name": "Khan Academy", "description": "Khan Academy educational videos and articles", "size_mb": 15000, "language": "en", "content_type": "education", "best_for": ["education", "research"], "zim_url": "https://download.kiwix.org/zim/khan_academy/khan_academy_all.zim", "kiwix_serve_url": "http://localhost:8080/khan_academy"},
    "project_gutenberg": {"name": "Project Gutenberg", "description": "70,000+ free eBooks — classic literature", "size_mb": 8000, "language": "en", "content_type": "library", "best_for": ["writerdeck", "education", "survival"], "zim_url": "https://download.kiwix.org/zim/gutenberg/gutenberg.zim", "kiwix_serve_url": "http://localhost:8080/gutenberg"},
    "vikidia": {"name": "Vikidia", "description": "Encyclopedia for 8-13 year olds, simpler language", "size_mb": 400, "language": "en", "content_type": "encyclopedia", "best_for": ["education"], "zim_url": "https://download.kiwix.org/zim/vikidia/vikidia_en.zim", "kiwix_serve_url": "http://localhost:8080/vikidia"},
    "ted_talks": {"name": "TED Talks", "description": "TED Talk transcripts and descriptions", "size_mb": 600, "language": "en", "content_type": "talks", "best_for": ["education", "research"], "zim_url": "https://download.kiwix.org/zim/ted_talks/ted_talks.zim", "kiwix_serve_url": "http://localhost:8080/ted_talks"},
    "wikimedia": {"name": "Wikimedia Commons", "description": "Free media file repository", "size_mb": 10000, "language": "multi", "content_type": "media", "best_for": ["research", "education"], "zim_url": "https://download.kiwix.org/zim/wikimedia/wikimedia_en.zim", "kiwix_serve_url": "http://localhost:8080/wikimedia"},
    "debian_docs": {"name": "Debian Documentation", "description": "Debian official documentation and manuals", "size_mb": 200, "language": "en", "content_type": "docs", "best_for": ["coding", "research"], "zim_url": "https://download.kiwix.org/zim/debian/debian_docs.zim", "kiwix_serve_url": "http://localhost:8080/debian_docs"},
    "arch_wiki": {"name": "Arch Linux Wiki", "description": "Arch Linux wiki — excellent technical reference", "size_mb": 300, "language": "en", "content_type": "docs", "best_for": ["coding", "research", "pentest"], "zim_url": "https://download.kiwix.org/zim/archlinux/archlinux.zim", "kiwix_serve_url": "http://localhost:8080/arch_wiki"},
    "kali_docs": {"name": "Kali Linux Documentation", "description": "Kali Linux docs — penetration testing guides", "size_mb": 150, "language": "en", "content_type": "docs", "best_for": ["pentest", "research"], "zim_url": "https://download.kiwix.org/zim/kali/kali_docs.zim", "kiwix_serve_url": "http://localhost:8080/kali_docs"},
    "python_docs": {"name": "Python Documentation", "description": "Python 3 official docs", "size_mb": 80, "language": "en", "content_type": "docs", "best_for": ["coding", "education"], "zim_url": "https://download.kiwix.org/zim/python/python_docs.zim", "kiwix_serve_url": "http://localhost:8080/python_docs"},
    "nodejs_docs": {"name": "Node.js Documentation", "description": "Node.js API reference and guides", "size_mb": 60, "language": "en", "content_type": "docs", "best_for": ["coding"], "zim_url": "https://download.kiwix.org/zim/nodejs/nodejs_docs.zim", "kiwix_serve_url": "http://localhost:8080/nodejs_docs"},
    "raspberry_pi_docs": {"name": "Raspberry Pi Documentation", "description": "Official Raspberry Pi docs", "size_mb": 120, "language": "en", "content_type": "docs", "best_for": ["coding", "education", "research"], "zim_url": "https://download.kiwix.org/zim/raspberrypi/raspberrypi_docs.zim", "kiwix_serve_url": "http://localhost:8080/rpi_docs"},
    "arduino_docs": {"name": "Arduino Documentation", "description": "Arduino language reference and guides", "size_mb": 90, "language": "en", "content_type": "docs", "best_for": ["coding", "education"], "zim_url": "https://download.kiwix.org/zim/arduino/arduino_docs.zim", "kiwix_serve_url": "http://localhost:8080/arduino_docs"},
    "esp32_docs": {"name": "ESP32 Documentation", "description": "ESP-IDF and ESP32 technical reference", "size_mb": 200, "language": "en", "content_type": "docs", "best_for": ["coding", "research", "education"], "zim_url": "https://download.kiwix.org/zim/esp32/esp32_docs.zim", "kiwix_serve_url": "http://localhost:8080/esp32_docs"},
}

BUILD_PURPOSE_ZIM_MAP = {
    "pentest": ["kali_docs", "arch_wiki", "stackoverflow", "debian_docs"],
    "writerdeck": ["wikipedia_en", "project_gutenberg", "wikiquote_en", "wiktionary_en", "wikisource_en"],
    "coding": ["stackoverflow", "python_docs", "nodejs_docs", "arduino_docs", "esp32_docs", "debian_docs", "arch_wiki", "wikipedia_en"],
    "research": ["wikipedia_en", "wikibooks_en", "wikiversity_en", "stackoverflow", "arch_wiki", "wikimedia", "ted_talks", "project_gutenberg"],
    "education": ["khan_academy", "wikipedia_en", "wikibooks_en", "wikiversity_en", "vikidia", "python_docs", "arduino_docs", "raspberry_pi_docs"],
    "survival": ["wikipedia_en", "wikivoyage_en", "wikinews_en", "project_gutenberg", "kali_docs"],
}


class KiwixKnowledgeBase:
    """Kiwix offline knowledge base manager for cyberdeck ZIM content."""

    @staticmethod
    def list_zims(category: str = "") -> str:
        if category:
            zids = BUILD_PURPOSE_ZIM_MAP.get(category, [])
            if not zids:
                return f"Unknown purpose: {category}. Available: {', '.join(BUILD_PURPOSE_ZIM_MAP.keys())}"
            lines = [f"<b>ZIM files for: {category}</b>\n"]
            for zid in zids:
                z = ZIM_DATABASE.get(zid)
                if z:
                    lines.append(f"<b>{z['name']}</b> ({zid})")
                    lines.append(f"  Size: {z['size_mb']}MB | Lang: {z['language']}")
                    lines.append(f"  {z['description']}")
                    lines.append(f"  Best for: {', '.join(z['best_for'])}\n")
            return "\n".join(lines)
        lines = ["<b>All ZIM Knowledge Bases</b>\n"]
        for zid, z in ZIM_DATABASE.items():
            lines.append(f"<b>{z['name']}</b> ({zid}) — {z['size_mb']}MB")
            lines.append(f"  {z['description']}")
            lines.append(f"  Best for: {', '.join(z['best_for'])}\n")
        return "\n".join(lines)

    @staticmethod
    def recommend_for_purpose(purpose: str) -> str:
        zids = BUILD_PURPOSE_ZIM_MAP.get(purpose)
        if not zids:
            return f"Unknown purpose: {purpose}. Choose: {', '.join(BUILD_PURPOSE_ZIM_MAP.keys())}"
        lines = [f"<b>Recommended ZIM files for: {purpose}</b>\n"]
        total_mb = 0
        for zid in zids:
            z = ZIM_DATABASE.get(zid)
            if z:
                total_mb += z["size_mb"]
                lines.append(f"<b>{z['name']}</b> — {z['size_mb']}MB")
                lines.append(f"  {z['description']}")
        lines.append("")
        lines.append(f"<b>Total storage needed:</b> {total_mb}MB ({total_mb/1024:.1f}GB)")
        lines.append("")
        lines.append(f"Install: /kiwix install {' '.join(zids)}")
        return "\n".join(lines)

    @staticmethod
    def generate_install_cmds(zim_ids: list[str]) -> str:
        valid = [z for z in zim_ids if z in ZIM_DATABASE]
        if not valid:
            return "No valid ZIM IDs provided."
        lines = ["<b>Kiwix Install Commands</b>", ""]
        lines.append("<b>1. Install Kiwix-serve:</b>")
        lines.append("  <code>wget -O kiwix-serve https://download.kiwix.org/release/kiwix-serve/kiwix-serve-linux-aarch64</code>")
        lines.append("  <code>chmod +x kiwix-serve</code>")
        lines.append("  <code>sudo mv kiwix-serve /usr/local/bin/</code>")
        lines.append("")
        lines.append("<b>2. Download ZIM files:</b>")
        for zid in valid:
            z = ZIM_DATABASE[zid]
            lines.append(f"  <code>wget -O /data/{zid}.zim {z['zim_url']}</code>  # {z['size_mb']}MB")
        lines.append("")
        lines.append("<b>3. Run Kiwix-serve:</b>")
        zims_str = " ".join(f"/data/{z}.zim" for z in valid)
        lines.append(f"  <code>kiwix-serve --port=8080 {zims_str}</code>")
        lines.append("")
        lines.append("<b>4. Systemd service (auto-start):</b>")
        lines.append(f"  <code>sudo tee /etc/systemd/system/kiwix.service &lt;&lt;EOF</code>")
        lines.append("[Unit]")
        lines.append("Description=Kiwix ZIM Server")
        lines.append("After=network.target")
        lines.append("")
        lines.append("[Service]")
        lines.append(f"ExecStart=/usr/local/bin/kiwix-serve --port=8080 {zims_str}")
        lines.append("Restart=always")
        lines.append("User=root")
        lines.append("")
        lines.append("[Install]")
        lines.append("WantedBy=multi-user.target")
        lines.append("EOF")
        lines.append("  <code>sudo systemctl daemon-reload</code>")
        lines.append("  <code>sudo systemctl enable --now kiwix</code>")
        lines.append("")
        lines.append("<b>5. Access:</b>")
        for zid in valid:
            z = ZIM_DATABASE[zid]
            lines.append(f"  {z['kiwix_serve_url']}")
        return "\n".join(lines)

    @staticmethod
    def setup_rag_cmds(model_key: str, zim_ids: list[str]) -> str:
        valid = [z for z in zim_ids if z in ZIM_DATABASE]
        if not valid:
            return "No valid ZIM IDs provided."
        lines = [f"<b>RAG Pipeline Setup: Ollama + ChromaDB + ZIM</b>", ""]
        lines.append("<b>1. Install dependencies:</b>")
        lines.append("  <code>pip install chromadb sentence-transformers pypdf2 beautifulsoup4</code>")
        lines.append("")
        lines.append("<b>2. Pull embedding model:</b>")
        lines.append("  <code>ollama pull nomic-embed-text</code>")
        lines.append("")
        lines.append(f"<b>3. Pull LLM model:</b>")
        lines.append(f"  <code>ollama pull {model_key}</code>")
        lines.append("")
        lines.append("<b>4. Create ingest script (ingest_zim.py):</b>")
        lines.append("  <code>")
        lines.append("import chromadb")
        lines.append("from sentence_transformers import SentenceTransformer")
        lines.append("import os, glob")
        lines.append("")
        lines.append("client = chromadb.PersistentClient(path='/data/chroma')")
        lines.append("collection = client.create_collection('knowledge', get_or_create=True)")
        lines.append("model = SentenceTransformer('all-MiniLM-L6-v2')")
        lines.append("")
        lines.append("zim_dirs = glob.glob('/data/*.zim')")
        lines.append("for zd in zim_dirs:")
        lines.append("    # Extract text from ZIM (requires zimdump or pyzim)")
        lines.append("    pass  # Implement ZIM text extraction here")
        lines.append("")
        lines.append("print('Knowledge base indexed')")
        lines.append("  </code>")
        lines.append("")
        lines.append("<b>5. Run ingest:</b>")
        lines.append("  <code>python ingest_zim.py</code>")
        lines.append("")
        lines.append("<b>6. Query script (query_kb.py):</b>")
        lines.append("  <code>")
        lines.append("import chromadb")
        lines.append("client = chromadb.PersistentClient(path='/data/chroma')")
        lines.append("collection = client.get_collection('knowledge')")
        lines.append("results = collection.query(query_texts=[user_query], n_results=5)")
        lines.append("context = '\\n'.join(results['documents'][0])")
        lines.append("prompt = f'Context: {context}\\n\\nQuestion: {user_query}'")
        lines.append("print(prompt)")
        lines.append("  </code>")
        lines.append("")
        lines.append("<b>7. Run with Ollama:</b>")
        lines.append(f"  <code>python query_kb.py | ollama run {model_key}</code>")
        return "\n".join(lines)


# ============================================================
# ENCLOSURE MATERIAL DATABASE
# ============================================================
ENCLOSURE_MATERIAL_DATABASE = {
    "pla": {"name": "PLA", "print_temp_c": "190-220", "bed_temp_c": "50-70", "strength": "Medium", "flexible": False, "best_for": ["prototypes", "casual-decks", "education"], "notes": "Easy to print, bio-degradable, low warping"},
    "petg": {"name": "PETG", "print_temp_c": "230-260", "bed_temp_c": "70-90", "strength": "High", "flexible": False, "best_for": ["field-decks", "durable-enclosures", "outdoor"], "notes": "Stronger than PLA, UV resistant, good layer adhesion"},
    "abs": {"name": "ABS", "print_temp_c": "230-260", "bed_temp_c": "90-110", "strength": "Very High", "flexible": False, "best_for": ["tactical-decks", "high-temp", "structural"], "notes": "Needs enclosure, fumes, acetone smoothing possible"},
    "asa": {"name": "ASA", "print_temp_c": "240-270", "bed_temp_c": "90-110", "strength": "Very High", "flexible": False, "best_for": ["outdoor-decks", "tactical", "marine"], "notes": "ABS with UV stability, excellent for outdoor cyberdecks"},
    "polycarbonate": {"name": "Polycarbonate", "print_temp_c": "260-310", "bed_temp_c": "100-130", "strength": "Extreme", "flexible": False, "best_for": ["rugged-decks", "military", "impact-resistant"], "notes": "Highest strength, needs all-metal hotend, very tough"},
    "wood_pla": {"name": "Wood PLA", "print_temp_c": "190-220", "bed_temp_c": "50-70", "strength": "Medium", "flexible": False, "best_for": ["aesthetic-decks", "conversation-piece", "retro"], "notes": "Wood fiber filled, smells like wood, post-process with sanding"},
    "carbon_fiber": {"name": "Carbon Fiber PETG/PA", "print_temp_c": "250-280", "bed_temp_c": "80-100", "strength": "Extreme", "flexible": False, "best_for": ["high-end-decks", "lightweight", "professional"], "notes": "Stiff, lightweight, abrasive (use hardened nozzle)"},
    "resin": {"name": "Resin (SLA)", "print_temp_c": "N/A (SLA)", "bed_temp_c": "N/A", "strength": "Medium", "flexible": True, "best_for": ["detailed-parts", "aesthetic", "display"], "notes": "High detail, brittle standard resins, toxic liquid handling"},
    "nylon": {"name": "Nylon (PA)", "print_temp_c": "250-280", "bed_temp_c": "80-100", "strength": "Very High", "flexible": True, "best_for": ["functional-decks", "durable", "moving-parts"], "notes": "Excellent layer adhesion, hygroscopic, needs drying"},
    "tpu": {"name": "TPU", "print_temp_c": "210-250", "bed_temp_c": "40-70", "strength": "Low-Medium", "flexible": True, "best_for": ["gaskets", "bumpers", "buttons", "phone-holders"], "notes": "Flexible filament, excellent for gaskets and vibration dampening"},
}


class ParametricEnclosureGenerator:
    """Parametric OpenSCAD enclosure generator for cyberdeck builds."""

    @staticmethod
    def style_presets():
        return {
            "minimal": {"name": "Minimal", "description": "Clean, flat panels with rounded corners. Best for modern desk decks.", "wall_thickness": 2.0, "corner_radius": 4, "color_hex": "#2a2a2a", "material": "pla", "features": ["vent_holes"]},
            "tactical": {"name": "Tactical", "description": "Angled facets, aggressive styling with NATO rail mounts. Field-ready.", "wall_thickness": 3.0, "corner_radius": 2, "color_hex": "#1a3a1a", "material": "petg", "features": ["nato_rails", "vent_holes", "antenna_mount"]},
            "cyberpunk": {"name": "Cyberpunk", "description": "Hexagonal vents, geometric cutouts, transparent panels. Neon-ready.", "wall_thickness": 2.5, "corner_radius": 1, "color_hex": "#1a1a2e", "material": "abs", "features": ["vent_holes", "antenna_mount"]},
            "retro": {"name": "Retro", "description": "Beveled edges, chunky corners, vintage computer aesthetic.", "wall_thickness": 2.5, "corner_radius": 8, "color_hex": "#d4c9a8", "material": "wood_pla", "features": []},
            "solarpunk": {"name": "Solarpunk", "description": "Organic curves, bamboo/wood accents, solar panel mounts. Eco-aesthetic.", "wall_thickness": 2.0, "corner_radius": 6, "color_hex": "#4a6741", "material": "wood_pla", "features": ["vent_holes"]},
        }

    @staticmethod
    def compute_enclosure_dimensions(sbc_key: str, display_key: str, battery_key: str) -> dict:
        sbc_sizes = {
            "rpi5": {"w": 85, "d": 56, "h": 17},
            "rpi4": {"w": 85, "d": 56, "h": 15},
            "rpi3": {"w": 85, "d": 56, "h": 17},
            "orangepi5": {"w": 90, "d": 62, "h": 20},
            "rock5b": {"w": 92, "d": 62, "h": 20},
            "jetson_nano": {"w": 100, "d": 80, "h": 25},
            "radxa_zero3": {"w": 65, "d": 30, "h": 10},
            "esp32s3": {"w": 55, "d": 28, "h": 8},
        }
        display_sizes = {
            "hdmi5": {"w": 130, "d": 5, "h": 90},
            "hdmi7": {"w": 165, "d": 5, "h": 100},
            "hdmi10": {"w": 230, "d": 5, "h": 150},
            "dsi5": {"w": 120, "d": 5, "h": 80},
            "dsi7": {"w": 155, "d": 5, "h": 95},
            "oled128x64": {"w": 40, "d": 5, "h": 30},
            "tft3.5": {"w": 80, "d": 5, "h": 55},
            "tft2.8": {"w": 65, "d": 5, "h": 45},
        }
        battery_sizes = {
            "npf550": {"w": 70, "d": 25, "h": 55},
            "npf970": {"w": 70, "d": 40, "h": 55},
            "18650_2": {"w": 40, "d": 20, "h": 75},
            "18650_4": {"w": 80, "d": 20, "h": 75},
            "18650_6": {"w": 120, "d": 20, "h": 75},
            "lipo_5000": {"w": 80, "d": 15, "h": 60},
            "lipo_10000": {"w": 100, "d": 20, "h": 80},
        }
        sbc = sbc_sizes.get(sbc_key, {"w": 85, "d": 56, "h": 17})
        disp = display_sizes.get(display_key, {"w": 0, "d": 0, "h": 0})
        batt = battery_sizes.get(battery_key, {"w": 0, "d": 0, "h": 0})
        wall = 2.5
        w = max(sbc["w"], disp["w"]) + wall * 2 + 10
        d = sbc["d"] + disp["d"] + batt["d"] + wall * 2 + 20
        h = max(sbc["h"], disp["h"], batt["h"]) + wall * 2 + 10
        vol = round(w * d * h / 1000, 1)
        return {
            "width_mm": round(w, 1),
            "depth_mm": round(d, 1),
            "height_mm": round(h, 1),
            "wall_thickness_mm": wall,
            "volume_cm3": vol,
        }

    @staticmethod
    def generate_openscad(sbc_key: str, display_key: str, battery_key: str, material: str = "pla", style: str = "minimal", nato_rails: bool = False, vent_holes: bool = True, has_antenna_mount: bool = False) -> str:
        dims = ParametricEnclosureGenerator.compute_enclosure_dimensions(sbc_key, display_key, battery_key)
        styles = ParametricEnclosureGenerator.style_presets()
        st = styles.get(style, styles["minimal"])
        mat = ENCLOSURE_MATERIAL_DATABASE.get(material, ENCLOSURE_MATERIAL_DATABASE["pla"])
        W = dims["width_mm"]
        D = dims["depth_mm"]
        H = dims["height_mm"]
        T = dims["wall_thickness_mm"]
        CR = st["corner_radius"]
        code = f"""// Parametric Cyberdeck Enclosure
// Style: {st['name']} | Material: {mat['name']}
// Generated by CyberdeckBot v6.5
// SBC: {sbc_key} | Display: {display_key} | Battery: {battery_key}
// Dimensions: {W}x{D}x{H}mm | Wall: {T}mm | Volume: {dims['volume_cm3']}cm3

/* [Dimensions] */
case_width = {W};        // Total width of enclosure (mm)
case_depth = {D};        // Total depth of enclosure (mm)
case_height = {H};       // Total height of enclosure (mm)
wall_thickness = {T};    // Wall thickness (mm)
corner_radius = {CR};    // Corner fillet radius (mm)

/* [Components] */
// SBC mounting (standoffs)
sbc_width = {W - T*2 - 10};
sbc_depth = {D - T*2 - 20};
standoff_height = 5;     // Standoff height for SBC (mm)
standoff_radius = 2;     // Screw hole radius (mm)
standoff_count = 4;      // Number of standoffs

// Display cutout
display_width = {W - T*2 - 10};
display_height = sbc_depth;
display_bezel = 2;       // Display bezel thickness (mm)

// Battery compartment
battery_width = sbc_width - 10;
battery_depth = 25;
battery_height = 15;

/* [Ventilation] */
vent_slot_width = 3;     // Width of each vent slot (mm)
vent_slot_count = {"8" if vent_holes else "0"};

/* [Accessories] */
nato_rails = {"true" if nato_rails else "false"};
antenna_mount = {"true" if has_antenna_mount else "false"};

// =============================================
// MODULES
// =============================================

module rounded_box(w, d, h, r) {{
    hull() {{
        translate([r, r, 0]) cylinder(h, r, r, center=false);
        translate([w-r, r, 0]) cylinder(h, r, r, center=false);
        translate([r, d-r, 0]) cylinder(h, r, r, center=false);
        translate([w-r, d-r, 0]) cylinder(h, r, r, center=false);
    }}
}}

module main_case() {{
    difference() {{
        rounded_box(case_width, case_depth, case_height, corner_radius);
        translate([wall_thickness, wall_thickness, wall_thickness])
            rounded_box(case_width-wall_thickness*2, case_depth-wall_thickness*2, case_height-wall_thickness, corner_radius);
    }}
}}

module standoffs() {{
    positions = [
        [20, 15, wall_thickness],
        [20, case_depth - 15, wall_thickness],
        [case_width - 20, 15, wall_thickness],
        [case_width - 20, case_depth - 15, wall_thickness]
    ];
    for (pos = positions) {{
        translate(pos) difference() {{
            cylinder(standoff_height + wall_thickness, 4, 4);
            cylinder(standoff_height + wall_thickness, standoff_radius, standoff_radius);
        }}
    }}
}}

module display_cutout() {{
    dx = (case_width - display_width) / 2;
    dy = (case_depth - display_height) / 2;
    translate([dx - display_bezel, dy - display_bezel, case_height - wall_thickness])
        cube([display_width + display_bezel*2, display_height + display_bezel*2, wall_thickness + 1]);
}}

module battery_compartment() {{
    bx = (case_width - battery_width) / 2;
    by = case_depth - battery_depth - wall_thickness - 5;
    translate([bx, by, wall_thickness])
        cube([battery_width, battery_depth, battery_height]);
}}

module vent_slots() {{
    for (i = [0:vent_slot_count-1]) {{
        x = 10 + i * ((case_width - 20) / vent_slot_count);
        translate([x, 0, case_height / 2])
            cube([vent_slot_width, wall_thickness + 1, case_height * 0.4]);
    }}
}}

module power_button_hole() {{
    translate([case_width - 10, case_depth / 2, case_height / 2])
        rotate([0, 90, 0])
            cylinder(20, 6, 6);
}}

module nato_rail_mount() {{
    // NATO rail standard — 21mm spacing
    rail_width = 40;
    rail_height = 3;
    translate([case_width - wall_thickness - 5, (case_depth - rail_width) / 2, 0])
        cube([10, rail_width, rail_height]);
}}

module antenna_pass_through() {{
    translate([case_width / 2, 0, case_height / 2])
        cylinder(wall_thickness + 2, 3, 3);
}}

// =============================================
// ASSEMBLY
// =============================================

difference() {{
    union() {{
        main_case();
        standoffs();
        if (nato_rails) nato_rail_mount();
    }}
    display_cutout();
    battery_compartment();
    if ({1 if vent_holes else 0}) vent_slots();
    power_button_hole();
    if ({1 if has_antenna_mount else 0}) antenna_pass_through();
}}
"""
        return code


# ============================================================
# v6.5 — POWER MANAGEMENT
# ============================================================
UPS_HAT_DATABASE = {
    "pisugar_3": {"name": "PiSugar 3", "capacity_wh": 10.0, "voltage_v": 5.1, "max_current_a": 3.0, "interface": "I2C", "sbc_compat": ["rpi5", "rpi4", "rpi3", "rpi0"], "features": ["RTC", "low_battery_alarm", "software_shutdown"], "price": 35, "form_factor": "HAT", "monitoring": True, "safe_shutdown": True, "notes": "Magnetic switch, i2c battery gauge, fits under RPi"},
    "pisugar_2": {"name": "PiSugar 2", "capacity_wh": 8.0, "voltage_v": 5.1, "max_current_a": 2.5, "interface": "I2C", "sbc_compat": ["rpi4", "rpi3", "rpi0"], "features": ["RTC", "low_battery_alarm"], "price": 28, "form_factor": "HAT", "monitoring": True, "safe_shutdown": False, "notes": "Older PiSugar, still good for RPi zero builds"},
    "waveshare_bp_5a": {"name": "Waveshare BP 5A", "capacity_wh": 18.5, "voltage_v": 5.1, "max_current_a": 5.0, "interface": "GPIO", "sbc_compat": ["rpi5", "rpi4", "rpi3", "orangepi5", "rock5b"], "features": ["high_current", "dual_usb", "fan_header"], "price": 45, "form_factor": "HAT", "monitoring": False, "safe_shutdown": False, "notes": "5A max output — can power RPi5 + display + peripherals"},
    "waveshare_bp_4a": {"name": "Waveshare BP 4A", "capacity_wh": 14.8, "voltage_v": 5.1, "max_current_a": 4.0, "interface": "GPIO", "sbc_compat": ["rpi4", "rpi3", "rpi0"], "features": ["dual_usb"], "price": 35, "form_factor": "HAT", "monitoring": False, "safe_shutdown": False, "notes": "Good for medium-load RPi4/3 builds"},
    "waveshare_ups_hat": {"name": "Waveshare UPS HAT", "capacity_wh": 12.0, "voltage_v": 5.1, "max_current_a": 3.0, "interface": "I2C/GPIO", "sbc_compat": ["rpi4", "rpi3", "rpi0"], "features": ["hot_swap", "i2c_monitoring"], "price": 32, "form_factor": "HAT", "monitoring": True, "safe_shutdown": False, "notes": "Hot-swappable 18650 cells, I2C fuel gauge"},
    "juicebox_hdmi": {"name": "JuiceBox HDMI", "capacity_wh": 20.0, "voltage_v": 12.0, "max_current_a": 3.0, "interface": "HDMI/CEC", "sbc_compat": ["rpi4", "rpi3", "jetson_nano"], "features": ["hdmi_passthrough", "various_voltage", "usb_c"], "price": 55, "form_factor": "Inline", "monitoring": False, "safe_shutdown": False, "notes": "Inline UPS between power supply and SBC — clean power"},
    "juicebox_40pin": {"name": "JuiceBox 40-Pin", "capacity_wh": 15.0, "voltage_v": 5.1, "max_current_a": 3.0, "interface": "GPIO", "sbc_compat": ["rpi4", "rpi3", "rpi5"], "features": ["gpio_passthrough", "i2c", "safe_shutdown"], "price": 48, "form_factor": "HAT", "monitoring": True, "safe_shutdown": True, "notes": "40-pin passthrough UPS with monitoring and graceful shutdown"},
    "pijuice": {"name": "PiJuice", "capacity_wh": 11.0, "voltage_v": 5.1, "max_current_a": 2.5, "interface": "I2C", "sbc_compat": ["rpi4", "rpi3", "rpi0"], "features": ["RTC", "fuel_gauge", "programmable_shutdown", "multi_chemistry"], "price": 55, "form_factor": "HAT", "monitoring": True, "safe_shutdown": True, "notes": "Full-featured UPS HAT with programmable power management"},
    "powerblade": {"name": "PowerBlade", "capacity_wh": 5.0, "voltage_v": 5.0, "max_current_a": 2.0, "interface": "I2C", "sbc_compat": ["rpi0", "rpi3", "esp32s3"], "features": ["ultra_compact", "i2c_gauge", "low_profile"], "price": 20, "form_factor": "Mini", "monitoring": True, "safe_shutdown": False, "notes": "Ultra-compact UPS for RPi Zero builds"},
    "rocky_battery": {"name": "Rocky Battery", "capacity_wh": 22.0, "voltage_v": 5.0, "max_current_a": 4.0, "interface": "I2C", "sbc_compat": ["rock5b", "orangepi5", "rpi5"], "features": ["high_capacity", "i2c_gauge", "fast_charge"], "price": 50, "form_factor": "HAT", "monitoring": True, "safe_shutdown": False, "notes": "High-capacity UPS for Rockchip SBCs"},
    "oem_battery_shim": {"name": "OEM Battery Shim", "capacity_wh": 6.0, "voltage_v": 5.0, "max_current_a": 2.0, "interface": "GPIO", "sbc_compat": ["rpi0", "rpi3"], "features": ["ultra_compact", "shim_design"], "price": 15, "form_factor": "Shim", "monitoring": False, "safe_shutdown": False, "notes": "Minimal UPS shim, no monitoring — just backup power"},
    "adafruit_powerboost": {"name": "Adafruit PowerBoost", "capacity_wh": 0.0, "voltage_v": 5.0, "max_current_a": 2.0, "interface": "Analog", "sbc_compat": ["any"], "features": ["boost_converter", "lipo_charger", "low_battery"], "price": 20, "form_factor": "Breakout", "monitoring": True, "safe_shutdown": False, "notes": "PowerBoost 1000C — lipo charger + boost converter, LBO pin"},
    "sparkfun_powercell": {"name": "SparkFun PowerCell", "capacity_wh": 0.0, "voltage_v": 5.0, "max_current_a": 2.5, "interface": "I2C", "sbc_compat": ["any"], "features": ["lipo_charger", "fuel_gauge", "usb_output"], "price": 25, "form_factor": "Breakout", "monitoring": True, "safe_shutdown": False, "notes": "PowerCell with MAX17048 fuel gauge, for custom battery solutions"},
    "geekworm_x733": {"name": "Geekworm X733 UPS HAT (4x21700)", "capacity_wh": 69.6, "voltage_v": 5.1, "max_current_a": 8.0, "interface": "I2C", "sbc_compat": ["rpi5", "rpi4", "cm5"], "features": ["high_capacity", "i2c_monitoring", "smart_shutdown", "hot_swap", "eeprom"], "price": 79, "form_factor": "HAT", "monitoring": True, "safe_shutdown": True, "notes": "4x 21700 cells = ~70Wh, 8A output, full shutdown script for Pi 5/CM5 decks"},
    "geekworm_x728": {"name": "Geekworm X728 UPS HAT (2x18650)", "capacity_wh": 24.7, "voltage_v": 5.1, "max_current_a": 8.0, "interface": "I2C", "sbc_compat": ["rpi5", "rpi4", "cm5"], "features": ["high_current", "i2c_monitoring", "smart_shutdown", "hot_swap"], "price": 55, "form_factor": "HAT", "monitoring": True, "safe_shutdown": True, "notes": "2x 18650, 8A buck with fan header — solid mid-capacity UPS"},
    "pichondria_pd_trigger": {"name": "Pichondria PD Trigger Board", "capacity_wh": 0.0, "voltage_v": 5.0, "max_current_a": 5.0, "interface": "USB-C PD", "sbc_compat": ["any"], "features": ["pd_negotiation", "passthrough", "12v_or_20v_mode"], "price": 18, "form_factor": "Breakout", "monitoring": False, "safe_shutdown": False, "notes": "Taps PD packs for 5/9/12/20V; Pichondria's favorite cyberdeck PSU breakout"},
    "pichondria_pd_20000": {"name": "Pichondria PD 20000mAh Battery", "capacity_wh": 74.0, "voltage_v": 5.0, "max_current_a": 5.0, "interface": "USB-C PD", "sbc_compat": ["any"], "features": ["pd_5v_passthrough", "high_capacity", "usb_c_in_out"], "price": 65, "form_factor": "Brick", "monitoring": False, "safe_shutdown": False, "notes": "Flat 20Ah PD pack with 5V line focus — perfect under a CM5 deck, not a HAT"},
    "pichondria_pd_30000": {"name": "Pichondria PD 30000mAh Battery", "capacity_wh": 111.0, "voltage_v": 5.0, "max_current_a": 6.0, "interface": "USB-C PD", "sbc_compat": ["any"], "features": ["pd_5v_passthrough", "ultra_capacity", "dual_usb_c"], "price": 95, "form_factor": "Brick", "monitoring": False, "safe_shutdown": False, "notes": "30Ah PD brick — multi-day field decks, feeds a trigger board instead of GPIO"},
}
BATTERY_CHEMISTRY = {
    "li_ion": {"energy_density_wh_kg": 250, "cycles": 500, "voltage_per_cell": 3.6, "safety_notes": "Stable with protection circuit, risk of thermal runaway if damaged"},
    "lipoly": {"energy_density_wh_kg": 220, "cycles": 400, "voltage_per_cell": 3.7, "safety_notes": "Flexible form factor, must not over-discharge below 3.0V/cell"},
    "lifepo4": {"energy_density_wh_kg": 140, "cycles": 2000, "voltage_per_cell": 3.2, "safety_notes": "Very safe, long cycle life, tolerant to overcharge/over-discharge"},
    "nimh": {"energy_density_wh_kg": 80, "cycles": 500, "voltage_per_cell": 1.2, "safety_notes": "Safe chemistry, memory effect, low energy density"},
    "lead_acid": {"energy_density_wh_kg": 40, "cycles": 300, "voltage_per_cell": 2.0, "safety_notes": "Heavy, durable, needs ventilation (hydrogen venting)"},
}
POWER_PROFILES = {
    "idle": {"sbc_power_w": 3, "display_power_w": 1, "peripheral_power_w": 0.5, "description": "SBC idle, screen dim, no peripherals active"},
    "light": {"sbc_power_w": 5, "display_power_w": 2, "peripheral_power_w": 1, "description": "Light browsing, terminal work, low brightness"},
    "normal": {"sbc_power_w": 8, "display_power_w": 3, "peripheral_power_w": 2, "description": "Normal desktop use, medium brightness, keyboard + mouse"},
    "heavy": {"sbc_power_w": 15, "display_power_w": 5, "peripheral_power_w": 5, "description": "Compiling, video playback, high brightness, multiple peripherals"},
    "turbo": {"sbc_power_w": 25, "display_power_w": 7, "peripheral_power_w": 8, "description": "Overclocked SBC, max brightness, SDR/mesh active, USB devices"},
}

class PowerMonitor:
    @staticmethod
    def estimate_runtime(battery_wh: float, load_profile: str = "normal") -> dict:
        profile = POWER_PROFILES.get(load_profile, POWER_PROFILES["normal"])
        total_w = profile["sbc_power_w"] + profile["display_power_w"] + profile["peripheral_power_w"]
        if total_w <= 0:
            total_w = 13
        hours = battery_wh / total_w
        return {"hours": round(hours, 1), "minutes": int(hours * 60), "profile": load_profile, "battery_name": f"{battery_wh}Wh", "notes": f"At {load_profile} load ({total_w}W total)"}

    @staticmethod
    def recommend_ups(sbc_key: str, target_hours: float) -> str:
        matches = []
        for hid, hat in UPS_HAT_DATABASE.items():
            if sbc_key in hat["sbc_compat"] and hat["capacity_wh"] > 0:
                runtime = hat["capacity_wh"] / 13 * 60
                if runtime >= target_hours * 60 * 0.7:
                    matches.append((hat["capacity_wh"], hid, hat))
        matches.sort(reverse=True)
        if not matches:
            all_sbcs = set()
            for hid, hat in UPS_HAT_DATABASE.items():
                all_sbcs.update(hat["sbc_compat"])
            compat = [f"<code>{h}</code>" for h in sorted(all_sbcs)]
            return f"No UPS HAT compatible with <b>{sbc_key}</b>.\nKnown SBCs: {', '.join(compat)}"
        lines = [f"<b>Recommended UPS HATs for {sbc_key} ({target_hours}h+ runtime)</b>\n"]
        for cap, hid, hat in matches:
            est_h = hat["capacity_wh"] / 13
            lines.append(f"<b>{hat['name']}</b> (<code>{hid}</code>)")
            lines.append(f"  Capacity: {hat['capacity_wh']}Wh | Est runtime: {est_h:.1f}h")
            lines.append(f"  Interface: {hat['interface']} | Price: ${hat['price']}")
            lines.append(f"  Monitoring: {'✅' if hat['monitoring'] else '❌'} | Safe shutdown: {'✅' if hat['safe_shutdown'] else '❌'}")
            if hat['notes']:
                lines.append(f"  <i>{hat['notes']}</i>")
            lines.append("")
        lines.append("<b>Usage:</b> /power runtime <wh> [profile] to estimate runtime")
        return "\n".join(lines)

    @staticmethod
    def generate_safe_shutdown_script(sbc_os: str = "raspberry_pi_os") -> str:
        script = '#!/bin/bash\n# Cyberdeck Safe Shutdown Monitor — Generated by CyberdeckBot\nBATTERY_MIN_V=3.2\nBATTERY_WARN_V=3.4\nCHECK_INTERVAL=10\nLOG_FILE=/var/log/battery_monitor.log\nSHUTDOWN_FILE=/tmp/battery_critical\n\nbattery_voltage() {\n'
        if sbc_os in ("raspberry_pi_os", "ubuntu_server", "dietpi"):
            script += '    if [ -f /sys/class/i2c-adapter/i2c-1/1-0036/voltage ]; then cat /sys/class/i2c-adapter/i2c-1/1-0036/voltage; else echo "3.7"; fi\n'
        elif sbc_os == "kali_linux":
            script += '    for dev in /sys/class/power_supply/*/voltage_now; do [ -f "$dev" ] && echo "scale=2; $(cat $dev)/1000000" | bc && return; done; echo "3.7"\n'
        elif sbc_os in ("arch_arm", "manjaro_arm"):
            script += '    if command -v upower &>/dev/null; then upower -i $(upower -e | grep BAT) | grep voltage | awk \'{print $2}\'; else echo "3.7"; fi\n'
        else:
            script += '    for dev in /sys/class/power_supply/*/voltage_now; do [ -f "$dev" ] && echo "scale=2; $(cat $dev)/1000000" | bc && return; done; echo "3.7"\n'
        script += '}\nwrite_log() { echo "$(date \'+%Y-%m-%d %H:%M:%S\') $1" >> "$LOG_FILE"; }\nwrite_log "Battery monitor started"\nwhile true; do\n  VOLT=$(battery_voltage)\n  if [ "$(echo "$VOLT < $BATTERY_MIN_V" | bc 2>/dev/null)" = "1" ]; then\n    write_log "CRITICAL: Battery at ${VOLT}V — shutting down!"\n    touch "$SHUTDOWN_FILE"\n    sync && shutdown -h now\n    exit 0\n  elif [ "$(echo "$VOLT < $BATTERY_WARN_V" | bc 2>/dev/null)" = "1" ]; then\n    write_log "WARNING: Battery at ${VOLT}V — low voltage"\n    wall "Battery low (${VOLT}V) — connect power or save work!"\n  fi\n  sleep "$CHECK_INTERVAL"\ndone\n'
        return f"<b>Safe Shutdown Script — {sbc_os}</b>\n\n<code># Save as /usr/local/bin/battery_monitor.sh\n# chmod +x /usr/local/bin/battery_monitor.sh\n# Add to crontab: @reboot /usr/local/bin/battery_monitor.sh &\n</code>\n<code>{script}</code>"

    @staticmethod
    def power_profile_info() -> str:
        lines = ["<b>Power Profiles</b>\n"]
        for pid, p in POWER_PROFILES.items():
            total = p["sbc_power_w"] + p["display_power_w"] + p["peripheral_power_w"]
            lines.append(f"<b>{pid}:</b> {total}W total\n  SBC: {p['sbc_power_w']}W | Display: {p['display_power_w']}W | Peripherals: {p['peripheral_power_w']}W\n  {p['description']}\n")
        return "\n".join(lines)

    @staticmethod
    def battery_chemistry_info() -> str:
        lines = ["<b>Battery Chemistry Comparison</b>\n"]
        for cid, c in BATTERY_CHEMISTRY.items():
            lines.append(f"<b>{cid}:</b> {c['energy_density_wh_kg']}Wh/kg | {c['cycles']} cycles | {c['voltage_per_cell']}V/cell\n  Safety: {c['safety_notes']}\n")
        return "\n".join(lines)

    @staticmethod
    def list_hats() -> str:
        lines = ["<b>Available UPS HATs</b>\n"]
        for hid, hat in UPS_HAT_DATABASE.items():
            lines.append(f"<b>{hat['name']}</b> (<code>{hid}</code>)\n  {hat['capacity_wh']}Wh @ {hat['voltage_v']}V | ${hat['price']} | {hat['form_factor']}\n  Interface: {hat['interface']} | SBCs: {', '.join(hat['sbc_compat'][:4])}\n  Monitoring: {'✅' if hat['monitoring'] else '❌'} | Safe shutdown: {'✅' if hat['safe_shutdown'] else '❌'}\n")
        lines.append("<b>Usage:</b> /power ups <sbc> <hours>")
        return "\n".join(lines)


# ============================================================
# v6.5 — OS CONFIGURATION
# ============================================================
OS_DATABASE = {
    "raspberry_pi_os": {"name": "Raspberry Pi OS", "base": "Debian", "arch": ["armhf", "arm64"], "sbc_compat": ["rpi5", "rpi4", "rpi3", "rpi0"], "min_ram_mb": 1024, "min_storage_mb": 4096, "best_for": ["general", "education", "iot", "media"], "package_manager": "apt", "default_desktop": "LXDE", "boot_time_s": 30, "difficulty": "Beginner", "notes": "Official RPi OS, well-supported, large community"},
    "ubuntu_server": {"name": "Ubuntu Server", "base": "Debian", "arch": ["arm64", "amd64"], "sbc_compat": ["rpi5", "rpi4", "orangepi5", "rock5b", "jetson_nano", "radxa_zero3"], "min_ram_mb": 2048, "min_storage_mb": 8192, "best_for": ["server", "coding", "docker", "edge_ai"], "package_manager": "apt", "default_desktop": "none", "boot_time_s": 25, "difficulty": "Intermediate", "notes": "Great for servers and Docker hosts, LTS releases"},
    "kali_linux": {"name": "Kali Linux", "base": "Debian", "arch": ["arm64", "armhf", "amd64"], "sbc_compat": ["rpi5", "rpi4", "rpi3", "orangepi5"], "min_ram_mb": 2048, "min_storage_mb": 16384, "best_for": ["pentest", "forensics", "security", "wardriving"], "package_manager": "apt", "default_desktop": "XFCE", "boot_time_s": 35, "difficulty": "Advanced", "notes": "Pre-installed with 600+ security tools"},
    "dietpi": {"name": "DietPi", "base": "Debian", "arch": ["arm64", "armhf"], "sbc_compat": ["rpi5", "rpi4", "rpi3", "rpi0", "orangepi5", "rock5b"], "min_ram_mb": 256, "min_storage_mb": 1024, "best_for": ["iot", "server", "minimal", "low_ram"], "package_manager": "apt", "default_desktop": "none", "boot_time_s": 15, "difficulty": "Intermediate", "notes": "Ultra-lightweight, optimized for SBCs, great for low-RAM builds"},
    "arch_arm": {"name": "Arch Linux ARM", "base": "Arch", "arch": ["arm64", "armhf"], "sbc_compat": ["rpi5", "rpi4", "rpi3", "rock5b", "orangepi5"], "min_ram_mb": 512, "min_storage_mb": 4096, "best_for": ["coding", "desktop", "rolling_release", "custom"], "package_manager": "pacman", "default_desktop": "none", "boot_time_s": 20, "difficulty": "Advanced", "notes": "Rolling release, AUR, full control, needs more maintenance"},
    "manjaro_arm": {"name": "Manjaro ARM", "base": "Arch", "arch": ["arm64", "armhf"], "sbc_compat": ["rpi4", "rpi3", "orangepi5"], "min_ram_mb": 1024, "min_storage_mb": 8192, "best_for": ["desktop", "media", "gaming"], "package_manager": "pacman", "default_desktop": "XFCE", "boot_time_s": 25, "difficulty": "Intermediate", "notes": "User-friendly Arch with GUI installer"},
    "alpine_linux": {"name": "Alpine Linux", "base": "Musl/Busybox", "arch": ["arm64", "armhf", "x86_64"], "sbc_compat": ["rpi4", "rpi3", "rpi0", "radxa_zero3"], "min_ram_mb": 128, "min_storage_mb": 256, "best_for": ["container", "server", "embedded", "minimal"], "package_manager": "apk", "default_desktop": "none", "boot_time_s": 10, "difficulty": "Advanced", "notes": "Extremely lightweight, musl-based, great for containers"},
    "freebsd": {"name": "FreeBSD", "base": "BSD", "arch": ["arm64", "amd64"], "sbc_compat": ["rpi4", "rpi3"], "min_ram_mb": 512, "min_storage_mb": 4096, "best_for": ["server", "networking", "storage", "jails"], "package_manager": "pkg", "default_desktop": "none", "boot_time_s": 20, "difficulty": "Expert", "notes": "ZFS, jails, pf firewall — excellent networking OS"},
    "retropie": {"name": "RetroPie", "base": "Debian/Raspbian", "arch": ["armhf"], "sbc_compat": ["rpi4", "rpi3", "rpi0"], "min_ram_mb": 1024, "min_storage_mb": 16384, "best_for": ["gaming", "retro", "emulation"], "package_manager": "apt", "default_desktop": "EmulationStation", "boot_time_s": 20, "difficulty": "Beginner", "notes": "Pre-configured emulation station for retro gaming"},
    "batocera": {"name": "Batocera", "base": "Buildroot", "arch": ["arm64", "x86_64"], "sbc_compat": ["rpi5", "rpi4", "orangepi5"], "min_ram_mb": 2048, "min_storage_mb": 8192, "best_for": ["gaming", "retro", "emulation"], "package_manager": "none", "default_desktop": "EmulationStation", "boot_time_s": 15, "difficulty": "Beginner", "notes": "Turnkey retro gaming, no install needed, boots from SD"},
    "lakka": {"name": "Lakka", "base": "Buildroot/LibreELEC", "arch": ["arm64", "armhf"], "sbc_compat": ["rpi4", "rpi3", "orangepi5"], "min_ram_mb": 1024, "min_storage_mb": 4096, "best_for": ["gaming", "retro"], "package_manager": "none", "default_desktop": "RetroArch", "boot_time_s": 12, "difficulty": "Beginner", "notes": "Minimal RetroArch distro, boots fast, all controller config"},
    "moode_audio": {"name": "moOde Audio", "base": "Debian/Raspbian", "arch": ["armhf"], "sbc_compat": ["rpi4", "rpi3", "rpi0"], "min_ram_mb": 512, "min_storage_mb": 2048, "best_for": ["audio", "music", "streaming"], "package_manager": "apt", "default_desktop": "none (web UI)", "boot_time_s": 20, "difficulty": "Beginner", "notes": "HiFi audio player, web interface, supports USB DACs"},
    "octoprint": {"name": "OctoPrint", "base": "Debian/Raspbian", "arch": ["armhf"], "sbc_compat": ["rpi4", "rpi3", "rpi0"], "min_ram_mb": 1024, "min_storage_mb": 4096, "best_for": ["3d_printing", "maker"], "package_manager": "apt", "default_desktop": "none (web UI)", "boot_time_s": 25, "difficulty": "Beginner", "notes": "3D printer management via web interface, camera streaming"},
    "homebridge": {"name": "Homebridge", "base": "Debian/Raspbian", "arch": ["arm64", "armhf"], "sbc_compat": ["rpi4", "rpi3", "rpi0"], "min_ram_mb": 512, "min_storage_mb": 2048, "best_for": ["home_automation", "smart_home", "iot"], "package_manager": "apt", "default_desktop": "none (web UI)", "boot_time_s": 20, "difficulty": "Intermediate", "notes": "HomeKit bridge for non-Apple smart home devices"},
    "openwrt": {"name": "OpenWrt", "base": "Linux (custom)", "arch": ["arm64", "armhf", "mips", "x86_64"], "sbc_compat": ["rpi4", "rpi3", "rpi0"], "min_ram_mb": 128, "min_storage_mb": 128, "best_for": ["router", "networking", "vpn", "firewall"], "package_manager": "opkg", "default_desktop": "none (web UI)", "boot_time_s": 10, "difficulty": "Advanced", "notes": "Full router OS, mesh networking, ad-blocking, VPN server"},
    "pfsense": {"name": "pfSense", "base": "FreeBSD", "arch": ["amd64"], "sbc_compat": ["x86_64_pc"], "min_ram_mb": 2048, "min_storage_mb": 8192, "best_for": ["firewall", "router", "vpn", "enterprise_networking"], "package_manager": "pkg", "default_desktop": "none (web UI)", "boot_time_s": 40, "difficulty": "Expert", "notes": "Enterprise firewall, not SBC-native but runs on x86_64"},
    "vyos": {"name": "VyOS", "base": "Debian", "arch": ["amd64"], "sbc_compat": ["x86_64_pc"], "min_ram_mb": 1024, "min_storage_mb": 2048, "best_for": ["router", "firewall", "vpn", "wan_aggregation"], "package_manager": "apt", "default_desktop": "none (CLI)", "boot_time_s": 30, "difficulty": "Expert", "notes": "Linux-based router OS, CLI-driven, wireguard, BGP"},
    "tails": {"name": "Tails", "base": "Debian", "arch": ["amd64"], "sbc_compat": ["x86_64_pc"], "min_ram_mb": 2048, "min_storage_mb": 8192, "best_for": ["privacy", "anonymity", "journalism", "whistleblowing"], "package_manager": "apt", "default_desktop": "GNOME", "boot_time_s": 45, "difficulty": "Intermediate", "notes": "Amnesic OS, routes all traffic through Tor, leaves no trace"},
    "whonix": {"name": "Whonix", "base": "Debian/Kicksecure", "arch": ["amd64"], "sbc_compat": ["x86_64_pc", "vm"], "min_ram_mb": 2048, "min_storage_mb": 16384, "best_for": ["privacy", "anonymity", "research", "journalism"], "package_manager": "apt", "default_desktop": "XFCE", "boot_time_s": 50, "difficulty": "Advanced", "notes": "Tor-routed VMs, Gateway + Workstation isolation"},
    "parrot_os": {"name": "Parrot OS", "base": "Debian Testing", "arch": ["arm64", "amd64"], "sbc_compat": ["rpi5", "rpi4", "orangepi5"], "min_ram_mb": 2048, "min_storage_mb": 16384, "best_for": ["pentest", "forensics", "privacy", "development"], "package_manager": "apt", "default_desktop": "MATE", "boot_time_s": 30, "difficulty": "Intermediate", "notes": "Kali alternative with better desktop experience, AnonSurf"},
    "fedora_iot": {"name": "Fedora IoT", "base": "Fedora", "arch": ["arm64", "aarch64"], "sbc_compat": ["rpi4", "rpi3", "orangepi5"], "min_ram_mb": 1024, "min_storage_mb": 4096, "best_for": ["iot", "edge", "container", "server"], "package_manager": "dnf", "default_desktop": "none", "boot_time_s": 25, "difficulty": "Advanced", "notes": "RPM-ostree based IoT OS, atomic updates, container-native"},
    "yocto": {"name": "Yocto/OpenEmbedded", "base": "Custom (bitbake)", "arch": ["arm64", "armhf", "riscv"], "sbc_compat": ["rpi4", "rpi3", "orangepi5", "rock5b"], "min_ram_mb": 256, "min_storage_mb": 512, "best_for": ["embedded", "custom", "production", "minimal"], "package_manager": "none", "default_desktop": "none", "boot_time_s": 8, "difficulty": "Expert", "notes": "Build your own custom Linux distro from source"},
    "buildroot": {"name": "Buildroot", "base": "Custom (make)", "arch": ["arm64", "armhf", "riscv"], "sbc_compat": ["rpi4", "rpi3", "orangepi5"], "min_ram_mb": 64, "min_storage_mb": 64, "best_for": ["embedded", "minimal", "production", "appliance"], "package_manager": "none", "default_desktop": "none", "boot_time_s": 5, "difficulty": "Expert", "notes": "Ultra-minimal embedded Linux, boots in seconds"},
}
BUILD_OS_MAP = {
    "pentest": "kali_linux", "security": "kali_linux", "wardriving": "kali_linux", "forensics": "kali_linux",
    "writerdeck": "raspberry_pi_os", "writing": "raspberry_pi_os", "coding": "ubuntu_server", "developer": "ubuntu_server",
    "desktop": "manjaro_arm", "general": "raspberry_pi_os", "gaming": "retropie", "retro": "batocera",
    "media": "raspberry_pi_os", "audio": "moode_audio", "music": "moode_audio", "iot": "dietpi",
    "home_automation": "homebridge", "smart_home": "homebridge", "router": "openwrt", "networking": "openwrt",
    "firewall": "pfsense", "vpn": "vyos", "privacy": "tails", "anonymity": "whonix",
    "research": "ubuntu_server", "edge_ai": "ubuntu_server", "container": "alpine_linux", "docker": "ubuntu_server",
    "server": "ubuntu_server", "embedded": "yocto", "production_embedded": "buildroot", "3d_printing": "octoprint",
}

class OSConfigurator:
    @staticmethod
    def generate_post_install_script(os_key: str, purpose: str) -> str:
        os_info = OS_DATABASE.get(os_key)
        if not os_info:
            return f"Unknown OS: {os_key}"
        pm = os_info["package_manager"]
        update_cmd = {"apt": "apt update && apt upgrade -y", "pacman": "pacman -Syu --noconfirm", "apk": "apk update && apk upgrade", "pkg": "pkg update && pkg upgrade", "dnf": "dnf update -y", "opkg": "opkg update", "none": "echo 'No package manager'"}.get(pm, "apt update && apt upgrade -y")
        install_cmd = {"apt": "apt install -y", "pacman": "pacman -S --noconfirm", "apk": "apk add", "pkg": "pkg install -y", "dnf": "dnf install -y", "opkg": "opkg install", "none": "echo 'No package manager'"}.get(pm, "apt install -y")
        purpose_tools = {
            "pentest": f"{install_cmd} kali-linux-headless nmap wireshark aircrack-ng hydra john metasploit-framework burpsuite",
            "writerdeck": f"{install_cmd} libreoffice-writer cool-retro-term focuswriter pandoc aspell calibre",
            "coding": f"{install_cmd} git vim neovim emacs build-essential python3 python3-pip nodejs npm docker.io docker-compose code-server",
            "desktop": f"{install_cmd} firefox-esr thunderbird libreoffice gimp vlc htop neofetch",
            "gaming": f"{install_cmd} retroarch libretro-* mame ppsspp",
            "iot": f"{install_cmd} python3 python3-pip mosquitto nodered influxdb grafana",
            "server": f"{install_cmd} nginx postgresql redis-server ufw fail2ban docker.io",
            "privacy": f"{install_cmd} tor torsocks torbrowser-launcher signal-desktop",
            "router": f"{install_cmd} bird2 wireguard-tools keepalived isc-dhcp-server bind9",
        }.get(purpose, f"{install_cmd} htop neofetch tmux git curl wget")
        de_choice = "i3-wm i3status i3lock dmenu"
        if purpose in ("writerdeck", "desktop", "coding"):
            de_choice = "sway swaybg waybar"
        script = f"""#!/bin/bash
set -euo pipefail
echo "=== Cyberdeck Post-Install: {os_info['name']} ==="
echo "Purpose: {purpose} | Date: $(date)"
{update_cmd}
{install_cmd} {de_choice} cool-retro-term alacritty
{purpose_tools}
{install_cmd} powertop tlp
if command -v systemctl &>/dev/null; then systemctl enable tlp; systemctl start tlp; fi
cat > /etc/udev/rules.d/99-battery-monitor.rules << 'RULES'
SUBSYSTEM=="power_supply", ATTR{{status}}=="Discharging", RUN+="/usr/local/bin/battery_warn.sh"
RULES
if [ -f /etc/ssh/sshd_config ]; then
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
fi
if command -v ufw &>/dev/null; then
    ufw default deny incoming; ufw default allow outgoing
    ufw allow 2222/tcp; ufw allow 80/tcp; ufw allow 443/tcp
    ufw --force enable
fi
echo "=== Post-install complete! Reboot recommended. ==="
"""
        return f"<b>Post-Install Script: {os_info['name']} for {purpose}</b>\n\n<code>{script}</code>"

    @staticmethod
    def recommend_os(purpose: str, sbc_key: str = "") -> str:
        os_key = BUILD_OS_MAP.get(purpose)
        if not os_key:
            purposes = [f"<code>{p}</code>" for p in sorted(BUILD_OS_MAP.keys())]
            return f"<b>Unknown purpose:</b> {purpose}\nKnown purposes: {', '.join(purposes)}"
        os_info = OS_DATABASE.get(os_key)
        if not os_info:
            return f"OS mapping issue: {os_key}"
        lines = [f"<b>Recommended OS for <code>{purpose}</code>:</b>\n"]
        lines.append(f"<b>{os_info['name']}</b> (<code>{os_key}</code>)")
        lines.append(f"  Base: {os_info['base']} | Arch: {', '.join(os_info['arch'])}")
        lines.append(f"  Package manager: {os_info['package_manager']} | Difficulty: {os_info['difficulty']}")
        lines.append(f"  Min RAM: {os_info['min_ram_mb']}MB | Min Storage: {os_info['min_storage_mb']}MB")
        lines.append(f"  Best for: {', '.join(os_info['best_for'])}")
        lines.append(f"  Default desktop: {os_info['default_desktop']}")
        lines.append(f"  <i>{os_info['notes']}</i>")
        if sbc_key:
            if sbc_key in os_info["sbc_compat"]:
                lines.append(f"\n  Compatible with <b>{sbc_key}</b>")
            else:
                lines.append(f"\n  {sbc_key} not compatible")
        lines.append(f"\n  <b>Generate setup script:</b> /osconf script {os_key} {purpose}")
        return "\n".join(lines)

    @staticmethod
    def list_oses(filter_by: str = "") -> str:
        lines = ["<b>Operating Systems Database</b>\n"]
        for oid, os_info in OS_DATABASE.items():
            if filter_by and filter_by not in oid and filter_by not in os_info["name"].lower() and filter_by not in os_info["best_for"]:
                continue
            lines.append(f"<b>{os_info['name']}</b> (<code>{oid}</code>)\n  Base: {os_info['base']} | Difficulty: {os_info['difficulty']}\n  RAM: {os_info['min_ram_mb']}MB | Storage: {os_info['min_storage_mb']}MB\n  Best for: {', '.join(os_info['best_for'])}\n")
        lines.append("<b>Usage:</b> /osconf recommend <purpose> [sbc]")
        return "\n".join(lines)

    @staticmethod
    def compare_oses(a: str, b: str) -> str:
        oa, ob = OS_DATABASE.get(a), OS_DATABASE.get(b)
        if not oa or not ob:
            return f"Unknown OS: {a}" if not oa else f"Unknown OS: {b}"
        lines = [f"<b>Comparison: {oa['name']} vs {ob['name']}</b>\n"]
        for label, key in [("Base", "base"), ("Min RAM", lambda x: f"{x['min_ram_mb']}MB"), ("Min Storage", lambda x: f"{x['min_storage_mb']}MB"), ("Difficulty", "difficulty"), ("Boot Time", lambda x: f"{x['boot_time_s']}s")]:
            va = oa[key] if isinstance(key, str) else key(oa)
            vb = ob[key] if isinstance(key, str) else key(ob)
            lines.append(f"<b>{label}:</b> {oa['name']}: {va} | {ob['name']}: {vb}\n")
        return "\n".join(lines)

    @staticmethod
    def generate_docker_compose(os_key: str, services: list[str]) -> str:
        os_info = OS_DATABASE.get(os_key)
        if not os_info:
            return f"Unknown OS: {os_key}"
        service_defs = {
            "nginx": {"image": "nginx:alpine", "ports": ["80:80", "443:443"], "restart": "unless-stopped"},
            "postgres": {"image": "postgres:16-alpine", "ports": ["5432:5432"], "volumes": ["pgdata:/var/lib/postgresql/data"], "env": {"POSTGRES_PASSWORD": "changeme", "POSTGRES_DB": "cyberdeck"}, "restart": "unless-stopped"},
            "redis": {"image": "redis:7-alpine", "ports": ["6379:6379"], "volumes": ["redisdata:/data"], "restart": "unless-stopped"},
            "mosquitto": {"image": "eclipse-mosquitto:2", "ports": ["1883:1883", "9001:9001"], "restart": "unless-stopped"},
            "portainer": {"image": "portainer/portainer-ce:latest", "ports": ["9000:9000", "8000:8000"], "volumes": ["/var/run/docker.sock:/var/run/docker.sock"], "restart": "unless-stopped"},
            "ollama": {"image": "ollama/ollama:latest", "ports": ["11434:11434"], "volumes": ["ollama_data:/root/.ollama"], "restart": "unless-stopped"},
            "grafana": {"image": "grafana/grafana:latest", "ports": ["3000:3000"], "volumes": ["grafana_data:/var/lib/grafana"], "restart": "unless-stopped"},
            "nodered": {"image": "nodered/node-red:latest", "ports": ["1880:1880"], "volumes": ["nodered_data:/data"], "restart": "unless-stopped"},
            "code-server": {"image": "codercom/code-server:latest", "ports": ["8443:8443"], "volumes": ["./code-server:/home/coder/.local/share/code-server"], "env": {"PASSWORD": "changeme"}, "restart": "unless-stopped"},
            "pihole": {"image": "pihole/pihole:latest", "ports": ["53:53/tcp", "53:53/udp", "80:80/tcp"], "volumes": ["pihole_etc:/etc/pihole", "pihole_dnsmasq:/etc/dnsmasq.d"], "env": {"TZ": "UTC", "WEBPASSWORD": "changeme"}, "restart": "unless-stopped"},
        }
        valid = [s for s in services if s in service_defs]
        if not valid:
            return f"Unknown services. Known: {', '.join(service_defs.keys())}"
        lines = ["version: '3.8'", "", "services:"]
        for svc in valid:
            sd = service_defs[svc]
            lines.append(f"  {svc}:")
            lines.append(f"    image: {sd['image']}")
            if sd.get("ports"):
                lines.append("    ports:")
                for p in sd["ports"]:
                    lines.append(f"      - '{p}'")
            if sd.get("volumes"):
                lines.append("    volumes:")
                for v in sd["volumes"]:
                    lines.append(f"      - {v}")
            if sd.get("env"):
                lines.append("    environment:")
                for ek, ev in sd["env"].items():
                    lines.append(f"      {ek}: '{ev}'")
            if sd.get("restart"):
                lines.append(f"    restart: {sd['restart']}")
        lines.append("")
        lines.append("volumes:")
        vols_seen = set()
        for svc in valid:
            sd = service_defs[svc]
            if sd.get("volumes"):
                for v in sd["volumes"]:
                    vname = v.split(":")[0]
                    if vname and vname not in vols_seen and "_" in vname:
                        vols_seen.add(vname)
                        lines.append(f"  {vname}:")
        return f"<b>docker-compose.yml for {os_info['name']} — Services: {', '.join(valid)}</b>\n\n<code>{chr(10).join(lines)}\n</code>"


# ============================================================
# v6.5 — BUILD DOCUMENTATION GENERATOR
# ============================================================
WIRING_TEMPLATES = {
    "sbc_display": {"name": "SBC to Display", "connections": [
        {"from_pin": "SBC HDMI", "to_pin": "Display HDMI", "wire_color": "HDMI cable", "notes": "Use HDMI-CEC adapter for power control if available"},
        {"from_pin": "SBC 5V", "to_pin": "Display 5V", "wire_color": "Red", "notes": "If display needs separate power, use buck converter"},
        {"from_pin": "SBC GND", "to_pin": "Display GND", "wire_color": "Black", "notes": "Common ground"},
    ]},
    "sbc_keyboard": {"name": "SBC to Keyboard", "connections": [
        {"from_pin": "SBC USB", "to_pin": "Keyboard USB", "wire_color": "USB cable", "notes": "USB-A to micro/USB-C for mechanical keyboards"},
    ]},
    "sbc_battery": {"name": "SBC to Battery/UPS", "connections": [
        {"from_pin": "Battery +", "to_pin": "UPS HAT B+", "wire_color": "Red (14-18 AWG)", "notes": "Use XT30/XT60 connectors for high-current"},
        {"from_pin": "Battery -", "to_pin": "UPS HAT B-", "wire_color": "Black (14-18 AWG)", "notes": "Keep wire length under 10cm for voltage drop"},
        {"from_pin": "UPS HAT 5V", "to_pin": "SBC 5V (GPIO 2,4)", "wire_color": "Red", "notes": "GPIO pin 2 (5V) or 4 (5V) on 40-pin header"},
        {"from_pin": "UPS HAT GND", "to_pin": "SBC GND (GPIO 6)", "wire_color": "Black", "notes": "GPIO pin 6 (GND) on 40-pin header"},
        {"from_pin": "UPS HAT I2C SDA", "to_pin": "SBC SDA (GPIO 3)", "wire_color": "Green", "notes": "Battery monitoring via I2C"},
        {"from_pin": "UPS HAT I2C SCL", "to_pin": "SBC SCL (GPIO 5)", "wire_color": "Blue", "notes": "I2C clock line with 4.7k pull-up"},
    ]},
    "sbc_audio": {"name": "SBC to Audio", "connections": [
        {"from_pin": "SBC I2S BCK", "to_pin": "DAC BCK", "wire_color": "White", "notes": "Bit clock"},
        {"from_pin": "SBC I2S DATA", "to_pin": "DAC DIN", "wire_color": "Yellow", "notes": "Data line"},
        {"from_pin": "SBC I2S LRCLK", "to_pin": "DAC LRCLK", "wire_color": "Orange", "notes": "Left/right clock"},
        {"from_pin": "SBC 3.3V", "to_pin": "DAC VCC", "wire_color": "Red", "notes": "3.3V power"},
        {"from_pin": "SBC GND", "to_pin": "DAC GND", "wire_color": "Black", "notes": "Common ground"},
    ]},
    "sdcard_boot": {"name": "SD Card Boot Setup", "connections": [
        {"from_pin": "SD Card", "to_pin": "SBC SD Slot", "wire_color": "N/A", "notes": "Use class A2 V30 U3 for best performance"},
    ]},
    "button_reset": {"name": "Push Button Reset/Shutdown", "connections": [
        {"from_pin": "Button NO", "to_pin": "SBC GPIO 3 (pin 5)", "wire_color": "Green", "notes": "NO = normally open, momentary switch"},
        {"from_pin": "Button COM", "to_pin": "SBC GND (pin 6)", "wire_color": "Black", "notes": "Short GPIO3 to GND to wake from halt"},
    ]},
}

class BuildDocGenerator:
    @staticmethod
    def generate_build_doc(components: dict, author: str = "") -> str:
        lines = [f"# Cyberdeck Build Documentation"]
        if author:
            lines.append(f"**Author:** {author}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n---\n\n## Components\n")
        lines.append("| Component | Name | Specs | Price |\n|-----------|------|-------|-------|")
        for cat, comp in components.items():
            if isinstance(comp, dict):
                name = comp.get("name", str(comp))
                specs = comp.get("specs", comp.get("description", ""))
                price = comp.get("price", "?")
                if isinstance(price, (int, float)):
                    price = f"${price}"
                lines.append(f"| {cat.capitalize()} | {name} | {specs} | {price} |")
        lines.append("\n---\n\n## Wiring Diagram\n\n```")
        lines.append(BuildDocGenerator.generate_wiring_diagram(components))
        lines.append("```\n\n---\n\n## Assembly Steps\n")
        steps = [
            ("Mount the SBC", "Secure SBC to enclosure standoffs with M2.5 screws."),
            ("Connect Display", "Attach display cable to SBC. Secure display bezel."),
            ("Wire Keyboard", "Route keyboard cable through cable channel."),
            ("Install Battery/UPS", "Mount battery sled or UPS HAT. Connect power wires to SBC GPIO."),
            ("Configure I2C", "Enable I2C on SBC. Connect UPS HAT SDA/SCL wires."),
            ("Close Enclosure", "Fit top panel. Secure with screws. Test ports."),
            ("First Boot", "Flash SD card with OS. Insert and power on."),
        ]
        for i, (title, tip) in enumerate(steps, 1):
            lines.append(f"### Step {i}: {title}\n> {tip}\n")
        lines.append("---\n\n## Photo Checklist\n")
        lines.append(BuildDocGenerator.generate_photo_checklist(components))
        lines.append("\n---\n\n## Testing Procedure\n")
        for t in ["Power on", "Display shows desktop", "Keyboard works", "Battery charging", "WiFi connects", "I2C devices detected", "Safe shutdown works"]:
            lines.append(f"- [ ] {t}")
        lines.append("\n---\n\n## Share Your Build\n\n### Reddit\n```markdown")
        lines.append(BuildDocGenerator.generate_reddit_post({"sbc": components.get("sbc", {}).get("name", "?"), "display": components.get("display", {}).get("name", "?"), "components": components}))
        lines.append("```\n\n### Hackaday.io\n```markdown")
        lines.append(BuildDocGenerator.generate_hackaday_template({"sbc": components.get("sbc", {}).get("name", "?"), "display": components.get("display", {}).get("name", "?"), "components": components}))
        lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def generate_wiring_diagram(components: dict) -> str:
        sbc_name = components.get("sbc", {}).get("name", "SBC")
        lines = [f"  CYBERDECK WIRING DIAGRAM\n  ========================\n\n  {sbc_name}\n   +--------------------+\n   |   GPIO 40-pin     |\n   |  5V GND SDA SCL   |\n   +--------------------+\n          |    |\n    +-----+    +-----+\n    |                |\n  DISPLAY         BATTERY\n   HDMI             UPS\n\n  POWER: Battery -> SBC 5V (GPIO 2/4)\n  I2C:   SDA (GPIO 3) -> UPS SDA\n         SCL (GPIO 5) -> UPS SCL"]
        return "\n".join(lines)

    @staticmethod
    def generate_photo_checklist(components: dict) -> str:
        lines = ["- [ ] Overview — all components before assembly", "- [ ] SBC close-up", "- [ ] Display front/back", "- [ ] Battery/UPS label", "- [ ] Keyboard layout", "- [ ] Case inside/outside", "- [ ] Wiring before closing", "- [ ] Completed build (front/back/side)", "- [ ] Power-on screen", "- [ ] Portability shot"]
        return "\n".join(lines)

    @staticmethod
    def generate_reddit_post(build_data: dict) -> str:
        sbc = build_data.get("sbc", "?")
        display = build_data.get("display", "?")
        comps = build_data.get("components", {})
        lines = [f"**My {sbc} + {display} cyberdeck build**\n", "Just finished building my portable cyberdeck!", "", "**Components:**"]
        for cat, comp in comps.items():
            if isinstance(comp, dict):
                lines.append(f"- {cat}: {comp.get('name', '?')}")
        lines.extend(["", "**Assembly time:** ~4 hours", "**Difficulty:** Moderate", "", "Let me know if you have questions!"])
        return "\n".join(lines)

    @staticmethod
    def generate_hackaday_template(build_data: dict) -> str:
        sbc = build_data.get("sbc", "?")
        display = build_data.get("display", "?")
        return f"Title: [Build Log] Cyberdeck with {sbc} and {display}\n\n## Summary\nA portable cyberdeck build.\n\n## Components\n[List components]\n\n## Photos\n[Attach photos]"

    @staticmethod
    def gather_build_data(sbc_key: str, display_key: str, battery_key: str = "", case_key: str = "", keyboard_key: str = "") -> dict:
        data = {"sbc": SBC_DATABASE.get(sbc_key, SBC_ALT_DATABASE.get(sbc_key, {"name": sbc_key})), "display": DISPLAY_DATABASE.get(display_key, {"name": display_key})}
        if battery_key and battery_key in BATTERY_DATABASE:
            data["battery"] = BATTERY_DATABASE[battery_key]
        if case_key and case_key in CASE_DATABASE:
            data["case"] = CASE_DATABASE[case_key]
        if keyboard_key and keyboard_key in INPUT_DATABASE:
            data["keyboard"] = INPUT_DATABASE[keyboard_key]
        return data


# ============================================================
# v6.5 — SDR & RADIO INTEGRATION
# ============================================================
SDR_HARDWARE_DATABASE = {
    "hackrf_one": {"name": "HackRF One", "frequency_range": "1 MHz – 6 GHz", "bandwidth_mhz": 20.0, "adc_bits": 8, "interface": "USB 2.0 (High Speed)", "tx_capable": True, "price": 300, "best_for": ["portable", "pentest", "research", "gsm", "gps_spoofing"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["TX capability", "1-6 GHz", "8-bit ADC", "20 MSPS"], "antenna_connector": "SMA (female)", "notes": "Industry standard for portable SDR work"},
    "rtlsdr_v5": {"name": "RTL-SDR Blog V5", "frequency_range": "500 kHz – 1.766 GHz", "bandwidth_mhz": 3.2, "adc_bits": 8, "interface": "USB 2.0", "tx_capable": False, "price": 35, "best_for": ["hobbyist", "beginner", "fm_radio", "airband", "weather_sat"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["Low cost", "Wide community", "HF mod", "TCXO stability"], "antenna_connector": "MCX (SMA adapter incl.)", "notes": "Best value entry-level SDR"},
    "rtlsdr_v4": {"name": "RTL-SDR Blog V4", "frequency_range": "500 kHz – 1.766 GHz", "bandwidth_mhz": 3.2, "adc_bits": 8, "interface": "USB 2.0", "tx_capable": False, "price": 30, "best_for": ["hobbyist", "beginner", "fm_radio", "airband"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["Low cost", "Improved HF", "Bias tee", "Aluminum case"], "antenna_connector": "MCX", "notes": "Legacy V4 model, V5 recommended"},
    "limesdr_mini": {"name": "LimeSDR Mini", "frequency_range": "10 MHz – 3.5 GHz", "bandwidth_mhz": 30.72, "adc_bits": 12, "interface": "USB 3.0", "tx_capable": True, "price": 160, "best_for": ["portable", "experimental", "gsm", "lora", "research"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["TX/RX", "12-bit ADC", "30.72 MSPS", "FPGA core", "Open source"], "antenna_connector": "U.FL (IPEX)", "notes": "Excellent cost/TX balance"},
    "limesdr_usb": {"name": "LimeSDR USB", "frequency_range": "100 kHz – 3.8 GHz", "bandwidth_mhz": 61.44, "adc_bits": 12, "interface": "USB 3.0", "tx_capable": True, "price": 300, "best_for": ["research", "mimo", "full_duplex", "experimental"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["Full duplex", "61.44 MSPS", "12-bit ADC", "FPGA", "2x2 MIMO"], "antenna_connector": "U.FL (IPEX) x4", "notes": "Full duplex MIMO SDR"},
    "adalm_pluto": {"name": "ADALM-Pluto", "frequency_range": "325 MHz – 3.8 GHz", "bandwidth_mhz": 20.0, "adc_bits": 12, "interface": "USB 2.0", "tx_capable": True, "price": 150, "best_for": ["education", "research", "experimental", "sdr_learning"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["TX/RX", "12-bit ADC", "20 MSPS", "MATLAB/Simulink", "IIO framework"], "antenna_connector": "SMA (female)", "notes": "Academic-focused SDR"},
    "airspy_mini": {"name": "Airspy Mini", "frequency_range": "24 MHz – 1.7 GHz", "bandwidth_mhz": 6.0, "adc_bits": 12, "interface": "USB 2.0 (High Speed)", "tx_capable": False, "price": 100, "best_for": ["spectrum_monitoring", "airband", "weather_sat", "dmr"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["12-bit ADC", "6 MSPS", "Low noise", "Compact"], "antenna_connector": "SMA (female)", "notes": "Best-in-class RX sensitivity"},
    "airspy_hf": {"name": "Airspy HF+", "frequency_range": "DC – 31 MHz (HF)", "bandwidth_mhz": 0.768, "adc_bits": 16, "interface": "USB 2.0", "tx_capable": False, "price": 200, "best_for": ["hf_listening", "ham_radio", "shortwave", "dxing"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["16-bit ADC", "768 kSPS", "HF optimized", "Extreme dynamic range"], "antenna_connector": "SMA (female)", "notes": "Premium HF SDR"},
    "bladerf_2": {"name": "BladeRF 2.0 micro", "frequency_range": "47 MHz – 6 GHz", "bandwidth_mhz": 56.0, "adc_bits": 12, "interface": "USB 3.0", "tx_capable": True, "price": 480, "best_for": ["research", "cellular", "gsm", "lte", "wideband"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["TX/RX", "56 MSPS", "12-bit ADC", "FPGA"], "antenna_connector": "SMA (female) x2", "notes": "Professional grade, full duplex"},
    "usrp_b205mini": {"name": "USRP B205mini", "frequency_range": "70 MHz – 6 GHz", "bandwidth_mhz": 56.0, "adc_bits": 12, "interface": "USB 3.0", "tx_capable": True, "price": 675, "best_for": ["research", "education", "mimo", "prototyping"], "sdrpp_compat": False, "gnuradio_compat": True, "features": ["TX/RX", "56 MSPS", "12-bit ADC", "FPGA"], "antenna_connector": "SMA (female)", "notes": "Ettus Research, UHD framework"},
    "rx888": {"name": "RX-888", "frequency_range": "1 MHz – 2 GHz", "bandwidth_mhz": 32.0, "adc_bits": 16, "interface": "USB 3.0", "tx_capable": False, "price": 130, "best_for": ["wideband_rx", "spectrum_analysis", "multi_channel", "research"], "sdrpp_compat": True, "gnuradio_compat": True, "features": ["16-bit ADC", "32 MSPS", "8 channel", "USB 3.0"], "antenna_connector": "FPC", "notes": "High bit-depth wideband RX"},
    "kiwi_sdr": {"name": "KiwiSDR", "frequency_range": "10 kHz – 30 MHz", "bandwidth_mhz": 0.032, "adc_bits": 14, "interface": "Ethernet/WiFi", "tx_capable": False, "price": 300, "best_for": ["hf_listening", "remote_rx", "networked_sdr", "dx_cluster"], "sdrpp_compat": False, "gnuradio_compat": False, "features": ["Networked SDR", "Web UI", "14-bit ADC", "GPS disciplined"], "antenna_connector": "SMA (female)", "notes": "Network-connected HF SDR"},
    "websdr": {"name": "WebSDR (Network)", "frequency_range": "Varies by node", "bandwidth_mhz": 0.0, "adc_bits": 0, "interface": "Web Browser", "tx_capable": False, "price": 0, "best_for": ["remote_listening", "no_hardware", "hf", "education"], "sdrpp_compat": False, "gnuradio_compat": False, "features": ["Free", "No hardware needed", "Worldwide nodes"], "antenna_connector": "N/A", "notes": "Free networked SDR receivers via web browser"},
}
FREQUENCY_BANDS = {
    "ham_160m": {"name": "160m Ham Band", "freq_mhz": "1.8–2.0", "mode": "CW, SSB, Digital", "usage": "Nighttime DX and regional ham communication", "requires_license": True, "antenna_suggestion": "Dipole 80m full wave, inverted-L"},
    "ham_80m": {"name": "80m Ham Band", "freq_mhz": "3.5–4.0", "mode": "CW, SSB, Digital, AM", "usage": "Regional and NVIS communication", "requires_license": True, "antenna_suggestion": "Dipole 40m full wave, NVIS horizontal"},
    "ham_40m": {"name": "40m Ham Band", "freq_mhz": "7.0–7.3", "mode": "CW, SSB, Digital, FT8", "usage": "Most popular HF band, day/night, worldwide DX", "requires_license": True, "antenna_suggestion": "Dipole 20m, EFHW, vertical"},
    "ham_20m": {"name": "20m Ham Band", "freq_mhz": "14.0–14.35", "mode": "CW, SSB, Digital, FT8, RTTY", "usage": "Primary DX band, worldwide daytime propagation", "requires_license": True, "antenna_suggestion": "Yagi, dipole, vertical 1/4 wave"},
    "ham_10m": {"name": "10m Ham Band", "freq_mhz": "28.0–29.7", "mode": "CW, SSB, FM, Digital", "usage": "Solar cycle dependent, great DX when open", "requires_license": True, "antenna_suggestion": "1/4 wave vertical, ground plane"},
    "ham_2m": {"name": "2m Ham Band (VHF)", "freq_mhz": "144–148", "mode": "FM, SSB, CW, Digital", "usage": "Local repeaters, simplex, satellite (ISS), APRS", "requires_license": True, "antenna_suggestion": "J-pole, Yagi, 1/4 wave whip"},
    "ham_70cm": {"name": "70cm Ham Band (UHF)", "freq_mhz": "420–450", "mode": "FM, Digital, CW, SSB", "usage": "Local repeaters, DMR, Fusion, satellite", "requires_license": True, "antenna_suggestion": "Collinear, Yagi, 1/4 wave whip"},
    "fm_radio": {"name": "FM Radio Broadcast", "freq_mhz": "88–108", "mode": "WBFM (Stereo)", "usage": "Commercial FM broadcast", "requires_license": False, "antenna_suggestion": "Dipole 75cm"},
    "airband": {"name": "Civil Airband (VHF)", "freq_mhz": "118–137", "mode": "AM", "usage": "Civil aviation communications", "requires_license": False, "antenna_suggestion": "1/4 wave ground plane"},
    "weather_sat": {"name": "Weather Satellite (NOAA)", "freq_mhz": "137–138", "mode": "WBFM, APT", "usage": "NOAA APT weather satellite reception", "requires_license": False, "antenna_suggestion": "QFH, Turnstile"},
    "gps": {"name": "GPS L1", "freq_mhz": "1575.42", "mode": "DSSS", "usage": "Global Positioning System", "requires_license": False, "antenna_suggestion": "Active GPS patch antenna with LNA"},
    "wifi_24": {"name": "WiFi 2.4 GHz", "freq_mhz": "2400–2500", "mode": "OFDM, DSSS", "usage": "WiFi, Bluetooth, Zigbee", "requires_license": False, "antenna_suggestion": "2.4 GHz omnidirectional"},
    "wifi_5": {"name": "WiFi 5 GHz", "freq_mhz": "5150–5850", "mode": "OFDM", "usage": "WiFi 802.11a/n/ac/ax", "requires_license": False, "antenna_suggestion": "5 GHz panel"},
    "ism_433": {"name": "ISM 433 MHz", "freq_mhz": "433.05–434.79", "mode": "FSK, LoRa, ASK", "usage": "Short-range devices, IoT", "requires_license": False, "antenna_suggestion": "1/4 wave whip ~17cm"},
    "ism_868": {"name": "ISM 868 MHz (EU)", "freq_mhz": "863–870", "mode": "FSK, LoRa, GFSK", "usage": "EU ISM, LoRaWAN, IoT", "requires_license": False, "antenna_suggestion": "1/4 wave whip ~8.6cm"},
    "ism_915": {"name": "ISM 915 MHz (US)", "freq_mhz": "902–928", "mode": "FSK, LoRa, GFSK", "usage": "US ISM, LoRaWAN, IoT", "requires_license": False, "antenna_suggestion": "1/4 wave whip ~8.2cm"},
    "lte": {"name": "LTE 700–2600", "freq_mhz": "700–2690", "mode": "OFDMA, SC-FDMA", "usage": "4G LTE/5G NR cellular", "requires_license": False, "antenna_suggestion": "Wideband LTE antenna, MIMO"},
}
SDR_INTERFACES = {
    "sdrpp": {"name": "SDR++", "install_cmd": "sudo apt install sdrpp", "use_case": "General purpose SDR, multi-platform", "difficulty": "Beginner"},
    "gnuradio": {"name": "GNU Radio", "install_cmd": "sudo apt install gnuradio", "use_case": "Advanced DSP, custom flowgraphs", "difficulty": "Advanced"},
    "gqrx": {"name": "Gqrx", "install_cmd": "sudo apt install gqrx-sdr", "use_case": "Beginner-friendly SDR receiver with GUI", "difficulty": "Beginner"},
    "cubic_sdr": {"name": "CubicSDR", "install_cmd": "sudo apt install cubicsdr", "use_case": "Cross-platform SDR with waterfall", "difficulty": "Beginner"},
    "rtl_433": {"name": "rtl_433", "install_cmd": "sudo apt install rtl-433", "use_case": "433/868/915 MHz sensor decoding", "difficulty": "Intermediate"},
    "dump1090": {"name": "dump1090", "install_cmd": "git clone https://github.com/antirez/dump1090.git", "use_case": "ADS-B aircraft tracking at 1090 MHz", "difficulty": "Intermediate"},
    "wxtoimg": {"name": "wxtoimg", "install_cmd": "wget https://wxtoimgrestored.xyz/download/wxtoimg-armhf", "use_case": "NOAA APT weather satellite image decoding", "difficulty": "Intermediate"},
    "satdump": {"name": "SatDump", "install_cmd": "wget -O - https://satdump.org/install.sh | bash", "use_case": "Multi-satellite data decoding", "difficulty": "Intermediate"},
}

class SDRIntegration:
    @staticmethod
    def recommend_sdr(use_case: str, budget: int = 200) -> str:
        matches = []
        for sid, sdr in SDR_HARDWARE_DATABASE.items():
            if sdr["price"] > budget:
                continue
            score = sum(1 for b in sdr["best_for"] if b in use_case.lower() or use_case.lower() in b)
            if score > 0:
                matches.append((score, sid, sdr))
        matches.sort(key=lambda x: (-x[0], x[2]["price"]))
        if not matches:
            lines = [f"<b>No SDR found for '{use_case}' under ${budget}</b>\n"]
            for sid, sdr in SDR_HARDWARE_DATABASE.items():
                lines.append(f"  <b>{sdr['name']}</b> — ${sdr['price']} — {', '.join(sdr['best_for'][:3])}")
            return "\n".join(lines)
        lines = [f"<b>SDR Recommendations for: {use_case}</b> (budget ${budget})\n"]
        for score, sid, sdr in matches[:5]:
            tx = "TX ✓" if sdr["tx_capable"] else "RX-only"
            lines.append(f"<b>{sdr['name']}</b> (<code>{sid}</code>) — ${sdr['price']}")
            lines.append(f"  Freq: {sdr['frequency_range']} | BW: {sdr['bandwidth_mhz']}MSPS | {tx}")
            lines.append(f"  Best for: {', '.join(sdr['best_for'][:4])}\n")
        return "\n".join(lines)

    @staticmethod
    def list_bands(filter_licensed: bool = False) -> str:
        lines = ["<b>Frequency Bands</b>\n"]
        for bid, band in FREQUENCY_BANDS.items():
            if filter_licensed and not band["requires_license"]:
                continue
            lic = "Licensed" if band["requires_license"] else "Unlicensed"
            lines.append(f"<b>{band['name']}</b>\n  Freq: {band['freq_mhz']} MHz | Mode: {band['mode']}\n  {lic} | Antenna: {band['antenna_suggestion']}\n")
        return "\n".join(lines)

    @staticmethod
    def generate_install_script(sdr_key: str, os_key: str = "raspberry_pi_os") -> str:
        sdr = SDR_HARDWARE_DATABASE.get(sdr_key)
        if not sdr:
            return f"Unknown SDR: {sdr_key}. Available: {', '.join(SDR_HARDWARE_DATABASE.keys())}"
        lines = [f"<b>Installation Script for {sdr['name']} on {os_key}</b>", ""]
        lines.append("<b># System update</b>")
        lines.append("  <code>sudo apt update && sudo apt upgrade -y</code>\n")
        lines.append("<b># Install build dependencies</b>")
        lines.append("  <code>sudo apt install -y git cmake build-essential libusb-1.0-0-dev libboost-all-dev swig</code>\n")
        if sdr_key == "hackrf_one":
            lines.append("<b># HackRF One</b>")
            lines.append("  <code>sudo apt install -y hackrf libhackrf-dev</code>")
            lines.append("  <code>sudo hackrf_info  # Verify</code>")
        elif sdr_key in ("rtlsdr_v5", "rtlsdr_v4"):
            lines.append("<b># RTL-SDR</b>")
            lines.append("  <code>sudo apt install -y rtl-sdr librtlsdr-dev</code>")
            lines.append("  <code>echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/rtlsdr-blacklist.conf</code>")
        elif sdr_key in ("limesdr_mini", "limesdr_usb"):
            lines.append("<b># LimeSDR</b>")
            lines.append("  <code>sudo add-apt-repository -y ppa:myriadrf/drivers && sudo apt install -y limesuite liblimesuite-dev</code>")
        elif sdr_key == "adalm_pluto":
            lines.append("<b># ADALM-Pluto</b>")
            lines.append("  <code># Set IP: 192.168.2.1 (default Pluto IP)</code>")
            lines.append("  <code>export IIOD_REMOTE=192.168.2.1</code>")
        elif sdr_key in ("airspy_mini", "airspy_hf"):
            lines.append("<b># Airspy</b>")
            lines.append("  <code>sudo apt install -y airspy libairspy-dev && sudo airspy_info</code>")
        elif sdr_key == "bladerf_2":
            lines.append("<b># BladeRF</b>")
            lines.append("  <code>sudo apt install -y bladerf libbladerf-dev</code>")
        elif sdr_key == "usrp_b205mini":
            lines.append("<b># USRP B205mini</b>")
            lines.append("  <code>sudo apt install -f -y libuhd-dev uhd-host && sudo uhd_images_downloader</code>")
        elif sdr_key == "rx888":
            lines.append("<b># RX-888</b>")
            lines.append("  <code>git clone https://github.com/ik1xpv/ExtIO_sddc.git && cd ExtIO_sddc && mkdir build && cd build && cmake .. && make -j4</code>")
        elif sdr_key == "kiwi_sdr":
            lines.append("<b># KiwiSDR</b>")
            lines.append("  <code># KiwiSDR runs its own embedded Linux, access via http://kiwisdr.local:8073</code>")
        elif sdr_key == "websdr":
            lines.append("<b># WebSDR (No install needed)</b>")
            lines.append("  <code># Simply open http://websdr.org in browser</code>")
        return "\n".join(lines)

    @staticmethod
    def generate_gnuradio_flowgraph(flow_type: str, freq_mhz: float) -> str:
        lines = [f"<b>GNU Radio Flowgraph: {flow_type} @ {freq_mhz} MHz</b>", ""]
        if flow_type == "fm_receiver":
            lines.append("Blocks: osmosdr Source -> WBFM Receive -> Rational Resampler -> Audio Sink")
            lines.append(f"  Freq: {freq_mhz}e6 Hz, Rate: 2.4e6, Gain: 40")
        elif flow_type == "am_receiver":
            lines.append("Blocks: osmosdr Source -> AM Demod -> Rational Resampler -> Audio Sink")
            lines.append(f"  Freq: {freq_mhz}e6 Hz, Rate: 2.4e6")
        elif flow_type == "waterfall":
            lines.append("Blocks: osmosdr Source -> QT GUI Frequency Sink")
            lines.append(f"  Freq: {freq_mhz}e6 Hz, FFT Size: 1024")
        elif flow_type == "adsb":
            lines.append("Blocks: osmosdr Source -> ADS-B Demodulator -> ADS-B Sink")
            lines.append("  Freq: 1090e6 Hz (fixed for ADS-B)")
        elif flow_type == "apt":
            lines.append("Blocks: osmosdr Source -> Resampler -> AM Demod -> File Sink (WAV)")
            lines.append(f"  Freq: {freq_mhz}e6 Hz, Post-process with wxtoimg or SatDump")
        else:
            return f"Unknown flow type: {flow_type}. Available: fm_receiver, am_receiver, waterfall, adsb, apt"
        return "\n".join(lines)

    @staticmethod
    def frequency_plan_for_use(use_case: str) -> str:
        plans = {"aviation": ["airband"], "fm": ["fm_radio"], "weather_sat": ["weather_sat"], "ham": ["ham_160m", "ham_80m", "ham_40m", "ham_20m", "ham_10m", "ham_2m", "ham_70cm"], "ham_hf": ["ham_160m", "ham_80m", "ham_40m", "ham_20m", "ham_10m"], "ham_vhf": ["ham_2m"], "ham_uhf": ["ham_70cm"], "cellular": ["lte"], "lora": ["ism_433", "ism_868", "ism_915"], "wifi": ["wifi_24", "wifi_5"], "gps": ["gps"], "all": list(FREQUENCY_BANDS.keys())}
        band_keys = plans.get(use_case.lower().strip())
        if band_keys is None:
            return f"Unknown use case. Available: {', '.join(plans.keys())}"
        lines = [f"<b>Frequency Plan: {use_case.title()}</b>\n"]
        for bk in band_keys:
            b = FREQUENCY_BANDS.get(bk)
            if b:
                lines.append(f"<b>{b['name']}</b>\n  Freq: {b['freq_mhz']} MHz | Antenna: {b['antenna_suggestion']}\n")
        return "\n".join(lines)

    @staticmethod
    def list_interfaces() -> str:
        lines = ["<b>SDR Software Interfaces</b>\n"]
        for iid, iface in SDR_INTERFACES.items():
            lines.append(f"<b>{iface['name']}</b> (<code>{iid}</code>)\n  {iface['use_case']} | Difficulty: {iface['difficulty']}\n  Install: <code>{iface['install_cmd']}</code>\n")
        return "\n".join(lines)


# ============================================================
# v6.5 — COMMUNITY BUILD EXPLORER
# ============================================================
SAMPLE_COMMUNITY_BUILDS = {
    "deck_ops_cyberdeck": {"title": "Deck Ops Cyberdeck", "author": "u/DeckOps", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/deckops", "sbc": "Raspberry Pi 5 8GB", "display": "7.9\" Waveshare HDMI", "battery": "NP-F970 (2x)", "case_style": "3D printed tactical (OD green)", "features": ["NATO rail mount", "SDR HackRF integrated", "Mechanical keyboard 60%", "USB hub 4-port", "OLED status display"], "difficulty": "Advanced", "cost_tier": "Premium ($500+)", "year": 2025, "upvotes": 2340, "description": "Full tactical cyberdeck with integrated HackRF SDR, NATO rail mounting, and dual NP-F batteries.", "why_interesting": "Perfect example of a complete field-ready SDR cyberdeck.", "tags": ["tactical", "sdr", "hacking", "portable", "cyberpunk"]},
    "pi_pwn_box": {"title": "Pi Pwn Box", "author": "u/raspberry_pwn", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/pipwn", "sbc": "Raspberry Pi Zero 2W", "display": "3.5\" TFT touch", "battery": "18650 (2x 3000mAh)", "case_style": "Custom acrylic stack", "features": ["WiFi hacking suite", "BLE scanning", "Battery monitor IC", "Physical kill switch", "USB Ethernet gadget"], "difficulty": "Intermediate", "cost_tier": "Budget ($100-200)", "year": 2024, "upvotes": 1890, "description": "Compact penetration testing cyberdeck on Pi Zero 2W.", "why_interesting": "Shows how much power fits in a tiny form factor.", "tags": ["hacking", "portable", "minimal", "tactical"]},
    "writerdeck_v2": {"title": "WriterDeck V2", "author": "u/WriterDeck", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/writerdeckv2", "sbc": "Orange Pi 5 Max", "display": "5.0\" HDMI 800x480", "battery": "LiPo 10000mAh", "case_style": "3D printed minimal (retro beige)", "features": ["Mechanical keyboard (Cherry MX)", "E-ink secondary display", "Markdown editor focus", "Pomodoro timer", "Minimal OS (DietPi)"], "difficulty": "Intermediate", "cost_tier": "Mid-Range ($200-500)", "year": 2025, "upvotes": 3120, "description": "Distraction-free writing cyberdeck with e-ink display.", "why_interesting": "The most polished writerdeck design.", "tags": ["writer", "minimal", "desktop", "retro"]},
    "mesh_deck": {"title": "MeshNet Cyberdeck", "author": "u/MeshComm", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/meshdeck", "sbc": "Radxa Zero 3", "display": "5.5\" AMOLED HDMI", "battery": "18650 (4x 3500mAh)", "case_style": "3D printed rugged (SLA)", "features": ["LoRa (RAK2287 module)", "Meshtastic node", "GPS (BN-880)", "Solar charging MPPT", "IP54 sealed"], "difficulty": "Advanced", "cost_tier": "Mid-Range ($200-500)", "year": 2025, "upvotes": 1560, "description": "Off-grid mesh communication cyberdeck with LoRa and solar.", "why_interesting": "Fully self-contained mesh comms node.", "tags": ["mesh", "offgrid", "solar", "portable", "tactical"]},
    "sdr_hunter": {"title": "SDR Hunter Portable", "author": "u/SignalHound", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/sdrhunter", "sbc": "Raspberry Pi 5 8GB", "display": "10\" HDMI 1024x600", "battery": "NP-F970", "case_style": "Pelican 1450 case", "features": ["HackRF + RTL-SDR (dual)", "20dB LNA frontend", "Discone antenna", "SDR++ + GQRX", "GPS-locked recording"], "difficulty": "Advanced", "cost_tier": "Premium ($500+)", "year": 2025, "upvotes": 2100, "description": "Professional spectrum monitoring in a Pelican case.", "why_interesting": "Dual SDR setup enables TDOA direction finding.", "tags": ["sdr", "hacking", "portable", "tactical", "cyberpunk"]},
    "ai_lab_deck": {"title": "AI Lab Deck", "author": "u/AI_Tinkerer", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/ailabdeck", "sbc": "Jetson Orin Nano 8GB", "display": "13.3\" HDMI 1920x1080", "battery": "LiPo 20000mAh 4S", "case_style": "CNC aluminum (black anodized)", "features": ["Local LLM (Llama 3.2 8B)", "AI accelerator (TPU)", "NVMe SSD 1TB", "Active cooling (Noctua)", "microSD + USB3 hub"], "difficulty": "Expert", "cost_tier": "Premium ($500+)", "year": 2025, "upvotes": 2780, "description": "AI development cyberdeck running local LLMs on Jetson Orin Nano.", "why_interesting": "Runs 8B parameter LLM locally — edge AI in portable form.", "tags": ["ai", "desktop", "hacking", "portable"]},
    "solar_survival": {"title": "Solar Survival Deck", "author": "u/PrepperTech", "source": "Hackaday", "url": "https://hackaday.com/projects/solar-survival-deck", "sbc": "Raspberry Pi 5 4GB", "display": "7\" HDMI 1024x600", "battery": "Solar 50W + LiFePO4 10Ah", "case_style": "3D printed (OD green)", "features": ["Solar MPPT charger", "Offline Wikipedia (Kiwix)", "Cellular modem", "GPS", "IP54 water resistant"], "difficulty": "Advanced", "cost_tier": "Mid-Range ($200-500)", "year": 2024, "upvotes": 1340, "description": "Solar-powered survival cyberdeck with offline Wikipedia.", "why_interesting": "Practical survival tool combining solar, offline KB, and cellular.", "tags": ["solar", "offgrid", "portable", "minimal", "tactical"]},
    "cosplay_prop": {"title": "Cyberpunk Arcade Deck (Cosplay)", "author": "u/CosplayDeck", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/cosplaydeck", "sbc": "ESP32-S3", "display": "2.8\" TFT 320x240", "battery": "LiPo 2000mAh", "case_style": "Custom resin cast (neon green/black)", "features": ["Working faux terminal", "Neon glow strips (WS2812)", "Animated matrix effect", "Battery level indicator", "Mini keyboard prop"], "difficulty": "Intermediate", "cost_tier": "Budget ($100-200)", "year": 2025, "upvotes": 3450, "description": "Cyberpunk cosplay prop cyberdeck with animated terminal effects.", "why_interesting": "Highest upvoted cyberdeck cosplay.", "tags": ["cosplay", "cyberpunk", "portable", "minimal"]},
    "pentest_briefcase": {"title": "Pentest Briefcase", "author": "u/SecPro", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/pentestcase", "sbc": "Orange Pi 5 Max 16GB", "display": "10\" HDMI touch", "battery": "LiPo 20000mAh", "case_style": "Aluminum briefcase with foam cutout", "features": ["WiFi Pineapple + Pi", "SDR + antenna panel", "USB hub + Ethernet", "Kali Linux", "Hardware kill switch"], "difficulty": "Expert", "cost_tier": "Premium ($500+)", "year": 2025, "upvotes": 2670, "description": "Professional pentest workstation in a briefcase.", "why_interesting": "All-in-one pentest rig with organized layout.", "tags": ["hacking", "sdr", "tactical", "portable", "cyberpunk"]},
    "ham_radio_deck": {"title": "HamRadio DigiDeck", "author": "u/HamShack", "source": "r/cyberDeck", "url": "https://reddit.com/r/cyberDeck/comments/hamdeck", "sbc": "Raspberry Pi 5 4GB", "display": "7\" HDMI 1024x600", "battery": "LiFePO4 12Ah (external)", "case_style": "3D printed (olive drab)", "features": ["ICOM IC-705 interface", "FT8/FT4 digital modes", "APRS iGate", "WSJT-X + JTDX", "Antenna tuner control"], "difficulty": "Expert", "cost_tier": "Premium ($500+)", "year": 2024, "upvotes": 890, "description": "Ham radio digital modes cyberdeck with ICOM IC-705.", "why_interesting": "Bridges SDR cyberdeck with traditional ham radio.", "tags": ["sdr", "offgrid", "tactical", "portable"]},
}
GITHUB_BUILDS = {
    "penkesu_computer": {"title": "Penkesu Computer", "author": "penkia", "source": "GitHub", "url": "https://github.com/penkia/penkesu", "sbc": "Raspberry Pi Zero 2W", "display": "7.5\" e-ink 800x480", "battery": "LiPo 4000mAh", "case_style": "3D printed hinged clamshell (PETG)", "features": ["Hinged e-ink lid", "Mechanical keyboard (38 key)", "2x 3000mAh removable", "GBA SP style hinge", "Fully open-source STLs"], "difficulty": "Intermediate", "cost_tier": "Mid-Range ($200-500)", "year": 2022, "upvotes": 3200, "description": "Penkesu is a compact cyberdeck inspired by the Penkesu aesthetic, driven by a Pi Zero 2W with a hinged e-ink display.", "why_interesting": "One of the most famous fully open-source writerdeck STL projects.", "tags": ["writer", "minimal", "retro", "portable", "desktop"]},
    "ginko": {"title": "Ginko — Full Metal Cyberdeck", "author": "NickVimos", "source": "GitHub", "url": "https://github.com/NickVimos/ginko", "sbc": "Raspberry Pi 4/5", "display": "5.5\" AMOLED HDMI", "battery": "LiPo 3S 10000mAh", "case_style": "CNC aluminum panels + 3D printed frame", "features": ["Aluminum faceplates", "Mechanical keyboard", "Hot-swap battery", "Open hardware license", "Ventilated top panel"], "difficulty": "Expert", "cost_tier": "Premium ($500+)", "year": 2023, "upvotes": 2800, "description": "Ginko is a self-hosted, full-metal cyberdeck designed around the Raspberry Pi 4/5 with an aluminum chassis.", "why_interesting": "The reference build for machined-metal cyberdeck enclosures.", "tags": ["desktop", "writer", "portable", "minimal"]},
    "cybird": {"title": "CyBird Handheld", "author": "ericseibold", "source": "GitHub", "url": "https://github.com/ericseibold/cybird", "sbc": "Raspberry Pi 4 Compute Module", "display": "5\" HDMI 800x480", "battery": "LiPo 2x 4000mAh", "case_style": "Handheld clamshell with shoulder buttons", "features": ["CM4 based", "Mechanical keyboard", "Shoulder buttons", "Pocket handheld size", "Magnetic lid"], "difficulty": "Advanced", "cost_tier": "Mid-Range ($200-500)", "year": 2023, "upvotes": 1500, "description": "CyBird is a compact cyberdeck handheld built around a Compute Module 4 with a built-in keyboard.", "why_interesting": "Proof that CM4 can power a genuinely pocketable Linux handheld.", "tags": ["portable", "minimal", "gaming", "writer"]},
    "cyberdeck_ic_v": {"title": "Cyberdeck IC V", "author": "badgergt", "source": "GitHub", "url": "https://github.com/badgergt/cyberdeck_ic_v", "sbc": "Orange Pi Zero 2", "display": "7\" HDMI 1024x600", "battery": "18650 (4x)", "case_style": "3D printed rugged frame", "features": ["Full print files", "Removable battery tray", "Folding display", "Carry handle", "Kali-compatible"], "difficulty": "Intermediate", "cost_tier": "Budget ($100-200)", "year": 2022, "upvotes": 1100, "description": "A rugged, fully printable cyberdeck with a folding display and swappable 18650 sled.", "why_interesting": "Great first-build print project with a huge parts list.", "tags": ["portable", "minimal", "tactical", "hacking"]},
    "cyberdork": {"title": "Cyberdork", "author": "Nt44", "source": "GitHub", "url": "https://github.com/Nt44/cyberdork", "sbc": "Raspberry Pi 4B", "display": "7\" HDMI touch", "battery": "2x 18650 (hot-swap)", "case_style": "3D printed retro laptop", "features": ["Laptop-style clamshell", "Hot-swap batteries", "Mechanical keyboard", "I2C battery monitor", "Open STL source"], "difficulty": "Advanced", "cost_tier": "Mid-Range ($200-500)", "year": 2022, "upvotes": 1900, "description": "Cyberdork is a fully printable laptop-style cyberdeck with hot-swappable 18650 packs.", "why_interesting": "The laptop-form-factor cyberdeck that set the STL-sharing bar.", "tags": ["desktop", "writer", "portable", "retro"]},
    "reterminal_handheld": {"title": "ReTerminal Handheld", "author": "cyberdeck-builder", "source": "GitHub", "url": "https://github.com/cyberdeck-builder/reterminal", "sbc": "Seeed ReTerminal CM4", "display": "5\" IPS touch (built-in)", "battery": "LiPo 5000mAh", "case_style": "CNC/3D hybrid body", "features": ["ReTerminal CM4 base", "E-ink under-keyboard", "RFID module", "PM2.5 sensor", "Weather station add-on"], "difficulty": "Intermediate", "cost_tier": "Mid-Range ($200-500)", "year": 2024, "upvotes": 900, "description": "A field-rugged handheld built on the Seeed ReTerminal CM4 with environmental sensors.", "why_interesting": "Shows a commercial CM4 panel being turned into a full deck.", "tags": ["portable", "tactical", "maker", "offgrid"]},
    "esp32_writerdeck": {"title": "ESP32-S3 WriterDeck", "author": "writerdeck-github", "source": "GitHub", "url": "https://github.com/writerdeck-github/esp32-writerdeck", "sbc": "ESP32-S3", "display": "4.2\" e-ink 400x300", "battery": "LiPo 2000mAh", "case_style": "3D printed two-piece shell", "features": ["Instant-on firmware", "4.2\" e-ink", "Hand-wired 30% keyboard", "USB-C charging", "Week-long battery"], "difficulty": "Advanced", "cost_tier": "Budget ($100-200)", "year": 2025, "upvotes": 760, "description": "An ESP32-S3 powered distraction-free writer that cold-boots to a text editor in under two seconds.", "why_interesting": "The extreme-ultralight end of the writerdeck spectrum.", "tags": ["writer", "minimal", "portable", "retro"]},
    "hackberry_pi_clone": {"title": "HackberryPi-Style CM5", "author": "cm5-handheld", "source": "GitHub", "url": "https://github.com/cm5-handheld/hackberry-cm5", "sbc": "Raspberry Pi CM5 + carrier", "display": "4\" DSI 720x720 touch", "battery": "21700 (1x)", "case_style": "CNC aluminum faceplate", "features": ["BlackBerry-style keyboard", "MIPI DSI display", "USB-C PD charging", "NVMe on CM5", "True pocket Linux"], "difficulty": "Expert", "cost_tier": "Mid-Range ($200-500)", "year": 2025, "upvotes": 1400, "description": "An open-source CM5 palm-top with a MIPI DSI display and BlackBerry-style thumb keyboard.", "why_interesting": "Latest-gen CM5 + DSI + NVMe packed into a palm-top frame.", "tags": ["portable", "minimal", "desktop", "hacking"]},
    "cyberdeck_elite": {"title": "Cyberdeck Elite", "author": "penguin_knight", "source": "GitHub", "url": "https://github.com/penguin_knight/cyberdeck-elite", "sbc": "Raspberry Pi 5 8GB", "display": "5.5\" OLED (Vivitek)", "battery": "NP-F970 (2x)", "case_style": "Aluminum frame + 3D printed back", "features": ["15\" slide-out OLED", "Hall-effect analog stick", "Trackball + buttons", "Cyberdeck OS skin", "Hot-swap NP-F"], "difficulty": "Expert", "cost_tier": "Premium ($500+)", "year": 2024, "upvotes": 2100, "description": "Cyberdeck Elite features a 15-inch slide-out OLED display in a premium aluminum and 3D printed hybrid frame.", "why_interesting": "The slide-out big-screen concept done properly.", "tags": ["desktop", "portable", "gaming", "ai"]},
    "pi_top_like": {"title": "PiTop-Like Modular Deck", "author": "modular-deck", "source": "GitHub", "url": "https://github.com/modular-deck/modular-deck", "sbc": "Raspberry Pi 4B", "display": "11.6\" HDMI 1920x1080", "battery": "5x 18650 (18650 pack)", "case_style": "Modular stackable 3D printed", "features": ["Stackable module rails", "Hot-swap battery module", "External GPU module", "Docking station", "SCREW-standard mounting"], "difficulty": "Advanced", "cost_tier": "Mid-Range ($200-500)", "year": 2023, "upvotes": 1300, "description": "A modular, stackable cyberdeck with rail-mounted battery and peripheral modules.", "why_interesting": "Pushes the modular cyberdeck ecosystem idea.", "tags": ["desktop", "portable", "maker", "gaming"]},
    "tritium_deck": {"title": "Tritium Deck", "author": "tritium", "source": "GitHub", "url": "https://github.com/tritium/cyberdeck", "sbc": "Raspberry Pi Zero 2W", "display": "3.5\" DPI 480x320", "battery": "LiPo 3000mAh", "case_style": "3D printed retro handheld", "features": ["Retro handheld form", "Gamepad-style buttons", "PiKVM remote", "Tactical port cover", "Wearable strap"], "difficulty": "Intermediate", "cost_tier": "Budget ($100-200)", "year": 2024, "upvotes": 950, "description": "A wearable retro-handheld cyberdeck with PiKVM remote server access.", "why_interesting": "Brings PiKVM remote control into a wearable deck form.", "tags": ["portable", "hacking", "retro", "minimal"]},
    "lilipad_deck": {"title": "LilPad Deck", "author": "lilipad", "source": "GitHub", "url": "https://github.com/lilipad/lilipad-deck", "sbc": "Raspberry Pi 4B", "display": "7\" HDMI 1024x600", "battery": "LiPo 10000mAh", "case_style": "3D printed fold-over tablet", "features": ["Fold-over tablet design", "Magnetic lid", "Full-size keyboard", "Tripod mount", "Fully printable"], "difficulty": "Intermediate", "cost_tier": "Mid-Range ($200-500)", "year": 2023, "upvotes": 870, "description": "A fold-over tablet cyberdeck that closes like a book for transport.", "why_interesting": "Elegant fold-over mechanism that protects screen and keys.", "tags": ["portable", "writer", "minimal", "desktop"]},
}
SAMPLE_COMMUNITY_BUILDS.update(GITHUB_BUILDS)
BUILD_TAGS = {"portable", "desktop", "hacking", "writer", "gaming", "ai", "sdr", "mesh", "offgrid", "solar", "cosplay", "media", "retro", "minimal", "tactical", "cyberpunk"}

class CommunityExplorer:
    @staticmethod
    def get_featured_builds() -> str:
        sorted_builds = sorted(SAMPLE_COMMUNITY_BUILDS.values(), key=lambda b: (-b["upvotes"], b["year"]))
        lines = ["<b>Featured / Trending Community Builds</b>\n"]
        for b in sorted_builds[:8]:
            lines.append(f"<b>{b['title']}</b> by {b['author']}\n  Source: {b['source']} | {b['upvotes']} upvotes | {b['year']}\n  SBC: {b['sbc']} | Cost: {b['cost_tier']}\n  {b['description'][:100]}\n")
        lines.append("Use: /explore view <build_id> | /explore tag <tag> | /explore random")
        return "\n".join(lines)

    @staticmethod
    def explore_by_tag(tag: str, limit: int = 5) -> str:
        tag = tag.lower().strip()
        matches = [b for b in SAMPLE_COMMUNITY_BUILDS.values() if tag in b["tags"]]
        if not matches:
            return f"<b>No builds found for tag '{tag}'</b>\n\nAvailable tags: {', '.join(sorted(BUILD_TAGS))}"
        matches.sort(key=lambda b: -b["upvotes"])
        lines = [f"<b>Community Builds tagged: {tag}</b> ({len(matches)} found)\n"]
        for b in matches[:limit]:
            lines.append(f"<b>{b['title']}</b> by {b['author']} | {b['upvotes']} upvotes | {b['cost_tier']}\n  {b['description'][:120]}\n")
        return "\n".join(lines)

    @staticmethod
    def explore_by_source(source: str, limit: int = 5) -> str:
        source = source.lower().strip()
        source_map = {"r": "r/cyberDeck", "reddit": "r/cyberDeck", "hackaday": "Hackaday", "printables": "Printables", "github": "GitHub"}
        mapped = source_map.get(source, source)
        matches = [b for b in SAMPLE_COMMUNITY_BUILDS.values() if b["source"].lower() == mapped.lower()]
        if not matches:
            return f"<b>No builds found from source '{source}'</b>"
        matches.sort(key=lambda b: -b["upvotes"])
        lines = [f"<b>Community Builds from: {mapped}</b> ({len(matches)} found)\n"]
        for b in matches[:limit]:
            lines.append(f"<b>{b['title']}</b> by {b['author']} | {b['upvotes']} upvotes\n  SBC: {b['sbc']} | Display: {b['display']}\n  {b['description'][:120]}\n")
        return "\n".join(lines)

    @staticmethod
    def search_builds(query: str) -> str:
        q = query.lower().strip()
        matches = []
        for bid, b in SAMPLE_COMMUNITY_BUILDS.items():
            search_text = f"{b['title']} {b['description']} {b['author']} {' '.join(b['tags'])} {b['sbc']}".lower()
            if q in search_text:
                matches.append((bid, b))
        if not matches:
            return f"<b>No builds matching '{query}'</b>"
        lines = [f"<b>Search results for: {query}</b> ({len(matches)} found)\n"]
        for bid, b in matches[:10]:
            lines.append(f"<code>{bid}</code> — <b>{b['title']}</b> by {b['author']} | {b['upvotes']} upvotes\n  {b['description'][:120]}\n")
        return "\n".join(lines)

    @staticmethod
    def get_build_details(build_id: str) -> str:
        b = SAMPLE_COMMUNITY_BUILDS.get(build_id)
        if not b:
            avail = "\n".join(f"  <code>{bid}</code> — {b['title']}" for bid, b in SAMPLE_COMMUNITY_BUILDS.items())
            return f"<b>Unknown build: {build_id}</b>\n\nAvailable builds:\n{avail}"
        lines = [f"<b>{b['title']}</b>", f"by {b['author']} on {b['source']} | {b['upvotes']} upvotes | {b['year']}", ""]
        lines.append(f"<b>Description:</b> {b['description']}")
        lines.append(f"<b>Why it's interesting:</b> {b['why_interesting']}\n")
        lines.append(f"<b>Hardware:</b>\n  SBC: {b['sbc']}\n  Display: {b['display']}\n  Battery: {b['battery']}\n  Case: {b['case_style']}\n")
        lines.append(f"<b>Features:</b>")
        for f in b["features"]:
            lines.append(f"  - {f}")
        lines.append(f"\n<b>Difficulty:</b> {b['difficulty']} | Cost: {b['cost_tier']}")
        lines.append(f"<b>Tags:</b> {', '.join(b['tags'])}")
        return "\n".join(lines)

    @staticmethod
    def import_bom_as_starting_point(build_id: str) -> dict:
        b = SAMPLE_COMMUNITY_BUILDS.get(build_id)
        if not b:
            return {"error": f"Unknown build: {build_id}"}
        return {"build_id": build_id, "title": b["title"], "sbc": b["sbc"], "display": b["display"], "battery": b["battery"], "features": b["features"], "estimated_cost_tier": b["cost_tier"], "notes": b["description"]}

    @staticmethod
    def random_build() -> str:
        import random
        return CommunityExplorer.get_build_details(random.choice(list(SAMPLE_COMMUNITY_BUILDS.keys())))


# ============================================================
# v6.5 — AESTHETIC STYLE ENGINE
# ============================================================
AESTHETIC_STYLES = {
    "retro_terminal": {"name": "Retro Terminal", "description": "Amber/green CRT monitor aesthetic with beige cases.", "case_color_hex": "#d4c9a8", "case_color_name": "Retro Beige", "led_accent_hex": "#ffb000", "switch_color": "Cherry MX Amber (clicky)", "display_bezel_color": "#2a2a2a", "keycap_style": "SA profile, beige/amber", "font_suggestion": "IBM Plex Mono / VT323", "material_suggestion": "Wood PLA or beige ABS", "cable_sleeve_color": "Beige spiral wrap", "button_type": "Round arcade (amber LED)", "vibe": "Nostalgic, warm, tactile", "inspiration": "IBM 5150, VT100 terminal", "best_for_profiles": ["writer", "retro_gamer", "programmer"], "compatible_materials": ["wood_pla", "abs", "resin"]},
    "tactical_military": {"name": "Tactical Military", "description": "Olive drab and matte black. MIL-SPEC connectors, ruggedized.", "case_color_hex": "#4a5d23", "case_color_name": "Olive Drab", "led_accent_hex": "#00ff41", "switch_color": "Military toggle (guarded)", "display_bezel_color": "#1a1a1a", "keycap_style": "DSA profile, OD green/black", "font_suggestion": "JetBrains Mono / Fira Code", "material_suggestion": "PETG or polycarbonate", "cable_sleeve_color": "Coyote 550 paracord", "button_type": "Metal toggle with guard", "vibe": "Rugged, field-ready, utilitarian", "inspiration": "PRC-152 radio, Pelican cases", "best_for_profiles": ["pentester", "field_engineer", "survivalist"], "compatible_materials": ["petg", "polycarbonate", "carbon_fiber"]},
    "cyberpunk_neon": {"name": "Cyberpunk Neon", "description": "Black with neon cyan/magenta, hex cutouts, glowing elements.", "case_color_hex": "#0a0a0a", "case_color_name": "Matrix Black", "led_accent_hex": "#00ffff", "switch_color": "Chiky (translucent cyan)", "display_bezel_color": "#1a1a2e", "keycap_style": "XDA profile, cyan/magenta/black", "font_suggestion": "Orbitron / Rajdhani", "material_suggestion": "ABS or resin (translucent)", "cable_sleeve_color": "UV reactive cyan paracord", "button_type": "Illuminated push button (RGB)", "vibe": "Futuristic, hacking, bold", "inspiration": "Blade Runner, Ghost in the Shell", "best_for_profiles": ["cosplayer", "cyberdeck_enthusiast", "gamer"], "compatible_materials": ["abs", "resin", "carbon_fiber"]},
    "industrial_minimalist": {"name": "Industrial Minimalist", "description": "Raw aluminum, visible screw heads, brushed metal.", "case_color_hex": "#8c8c8c", "case_color_name": "Brushed Aluminum", "led_accent_hex": "#ffffff", "switch_color": "Silver toggle", "display_bezel_color": "#3a3a3a", "keycap_style": "G20 profile, grey/white", "font_suggestion": "Inter / Roboto", "material_suggestion": "Aluminum or carbon fiber PETG", "cable_sleeve_color": "Black techflex", "button_type": "Panel mount momentary (metal)", "vibe": "Clean, functional, professional", "inspiration": "Test equipment, server racks", "best_for_profiles": ["engineer", "maker", "programmer"], "compatible_materials": ["carbon_fiber", "petg", "pla"]},
    "solarpunk": {"name": "Solarpunk", "description": "Warm wood tones, sage green, bamboo panels, visible solar cells.", "case_color_hex": "#4a6741", "case_color_name": "Sage Green", "led_accent_hex": "#ffd700", "switch_color": "Wooden toggle", "display_bezel_color": "#2d1810", "keycap_style": "SA profile, green/cream/brown", "font_suggestion": "Cabin / Karla", "material_suggestion": "Wood PLA or bamboo filament", "cable_sleeve_color": "Brown cotton braid", "button_type": "Wooden button or brass toggle", "vibe": "Warm, sustainable, organic", "inspiration": "Solarpunk art, bio-mimicry", "best_for_profiles": ["environmentalist", "offgrid_builder", "writer"], "compatible_materials": ["wood_pla", "pla", "tpu"]},
    "vaporwave": {"name": "Vaporwave", "description": "Pastel pink, teal, purple gradients. Geometric patterns.", "case_color_hex": "#ff69b4", "case_color_name": "Neon Pink", "led_accent_hex": "#00ffff", "switch_color": "Translucent pink/teal", "display_bezel_color": "#1a0033", "keycap_style": "Cherry profile, pink/teal/white", "font_suggestion": "VCR OSD Mono / Press Start 2P", "material_suggestion": "Resin (translucent)", "cable_sleeve_color": "Pink UV reactive", "button_type": "Arcade button (pink/teal)", "vibe": "Retro-futuristic, dreamy", "inspiration": "OutRun, MacOS 9, synthwave", "best_for_profiles": ["cosplayer", "creative", "gamer"], "compatible_materials": ["resin", "abs", "pla"]},
    "steampunk": {"name": "Steampunk", "description": "Brass, copper, dark wood, leather. Pressure gauges, rivets.", "case_color_hex": "#6b3a2a", "case_color_name": "Antique Brass", "led_accent_hex": "#ff8c00", "switch_color": "Brass toggle or knife switch", "display_bezel_color": "#1a0f0a", "keycap_style": "Round typewriter keys (brass)", "font_suggestion": "Special Elite / IM Fell", "material_suggestion": "Wood PLA or ABS with metallic paint", "cable_sleeve_color": "Brown leather wrap", "button_type": "Brass toggle (vintage)", "vibe": "Victorian, mechanical, ornate", "inspiration": "Jules Verne, Victorian engineering", "best_for_profiles": ["cosplayer", "maker", "writer"], "compatible_materials": ["wood_pla", "tpu", "resin"]},
    "cassette_futurism": {"name": "Cassette Futurism", "description": "Off-white, dark grey, red/orange. Chunky buttons, angular.", "case_color_hex": "#e8e0d0", "case_color_name": "Off-White Cream", "led_accent_hex": "#ff4500", "switch_color": "Chunky piano key", "display_bezel_color": "#1a1a1a", "keycap_style": "OEM profile, cream/red/black", "font_suggestion": "Chicago / SF UI", "material_suggestion": "ABS or SLA resin", "cable_sleeve_color": "Red braided nylon", "button_type": "Piano key or chunky pushbutton", "vibe": "Retro-tech, chunky, 70s-80s", "inspiration": "TRS-80, VCR decks, Walkman", "best_for_profiles": ["retro_gamer", "cosplayer", "maker"], "compatible_materials": ["abs", "resin", "pla"]},
    "ghost_spec": {"name": "Ghost Spec", "description": "White/light grey with subtle blue. Clean, minimal, sterile.", "case_color_hex": "#f0f0f0", "case_color_name": "Phantom White", "led_accent_hex": "#4a90d9", "switch_color": "Silver flat top", "display_bezel_color": "#d0d0d0", "keycap_style": "XDA profile, white/grey/blue", "font_suggestion": "SF Pro / Inter", "material_suggestion": "Sanded PLA or aluminum", "cable_sleeve_color": "White techflex (blue stripe)", "button_type": "Flat panel touch", "vibe": "Clean, professional, stealth", "inspiration": "GitS: SAC Section 9", "best_for_profiles": ["professional", "programmer", "engineer"], "compatible_materials": ["pla", "carbon_fiber", "petg"]},
    "woodland_camo": {"name": "Woodland Camo", "description": "Green, brown, khaki, black camo. Matte finish.", "case_color_hex": "#3b4d2e", "case_color_name": "Woodland Green", "led_accent_hex": "#ff6600", "switch_color": "Black rubberized toggle", "display_bezel_color": "#1a1a1a", "keycap_style": "DSA profile, camo pattern", "font_suggestion": "JetBrains Mono / Fira Code", "material_suggestion": "PETG or nylon (water resistant)", "cable_sleeve_color": "Khaki paracord", "button_type": "Rubberized momentary", "vibe": "Stealth, outdoors, tactical", "inspiration": "M81 Woodland pattern", "best_for_profiles": ["survivalist", "field_engineer", "pentester"], "compatible_materials": ["petg", "nylon", "tpu"]},
    "white_ice": {"name": "White Ice", "description": "Crystal white with ice blue LEDs. Frosted translucent.", "case_color_hex": "#e8f0f8", "case_color_name": "Ice White", "led_accent_hex": "#88ddff", "switch_color": "Translucent ice blue", "display_bezel_color": "#c0c8d0", "keycap_style": "SA profile, white/ice-blue", "font_suggestion": "Product Sans / San Francisco", "material_suggestion": "Resin (frosted) or white PETG", "cable_sleeve_color": "White UV reactive", "button_type": "Low profile illuminated (white LED)", "vibe": "Clean, cold, premium", "inspiration": "Frost, snow, cybernetic implants", "best_for_profiles": ["professional", "creative", "cosplayer"], "compatible_materials": ["resin", "pla", "petg"]},
    "blood_red": {"name": "Blood Red", "description": "Deep crimson, matte black, dark chrome. Aggressive.", "case_color_hex": "#8b0000", "case_color_name": "Crimson Red", "led_accent_hex": "#ff0000", "switch_color": "Black w/ red backlight", "display_bezel_color": "#0a0000", "keycap_style": "OEM profile, red/black", "font_suggestion": "Orbitron / Exo 2", "material_suggestion": "ABS or aluminum (painted)", "cable_sleeve_color": "Red paracord (black tracer)", "button_type": "Metal pushbutton (red LED)", "vibe": "Aggressive, dark, intense", "inspiration": "Cyberpunk 2077, DOOM", "best_for_profiles": ["gamer", "pentester", "cosplayer"], "compatible_materials": ["abs", "petg", "carbon_fiber"]},
    "midnight": {"name": "Midnight", "description": "Dark navy/black with warm white LEDs. Understated.", "case_color_hex": "#0a0a1a", "case_color_name": "Midnight Navy", "led_accent_hex": "#ffeecc", "switch_color": "Black silent tactile", "display_bezel_color": "#050510", "keycap_style": "DSA profile, dark navy/grey", "font_suggestion": "Inter / IBM Plex Sans", "material_suggestion": "PETG or carbon fiber PETG", "cable_sleeve_color": "Black matte techflex", "button_type": "Tactile dome (silent)", "vibe": "Stealth, elegant, serious", "inspiration": "Stealth aircraft, night missions", "best_for_profiles": ["programmer", "field_engineer", "writer"], "compatible_materials": ["carbon_fiber", "petg", "nylon"]},
    "desert_storm": {"name": "Desert Storm", "description": "Tan, sand, brown. Desert digital camo.", "case_color_hex": "#c2b280", "case_color_name": "Desert Tan", "led_accent_hex": "#ffa500", "switch_color": "Sand-colored rubberized", "display_bezel_color": "#4a3520", "keycap_style": "DSA profile, tan/brown/khaki", "font_suggestion": "JetBrains Mono / Fira Code", "material_suggestion": "PETG or nylon (UV resistant)", "cable_sleeve_color": "Tan paracord", "button_type": "Rubberized toggle (dust cover)", "vibe": "Arid, tactical, field-tested", "inspiration": "Desert Storm operations", "best_for_profiles": ["survivalist", "field_engineer", "pentester"], "compatible_materials": ["petg", "nylon", "tpu"]},
}
COLOR_PALETTES = {_sid: {"primary": _s["case_color_hex"], "secondary": _s["display_bezel_color"], "accent": _s["led_accent_hex"], "background": "#000000", "text": "#ffffff", "success": "#00cc66", "warning": "#ffcc00", "error": "#ff3333"} for _sid, _s in AESTHETIC_STYLES.items()}

class AestheticEngine:
    @staticmethod
    def get_style(name: str):
        return AESTHETIC_STYLES.get(name.lower().replace(" ", "_").replace("-", "_"))

    @staticmethod
    def list_styles() -> str:
        lines = ["<b>Aesthetic Style Engine — Available Styles</b>\n"]
        for sid, s in AESTHETIC_STYLES.items():
            lines.append(f"<b>{s['name']}</b> (<code>{sid}</code>)\n  {s['description']}\n  Case: {s['case_color_name']} ({s['case_color_hex']}) | LED: {s['led_accent_hex']}\n  Material: {s['material_suggestion']} | Vibe: {s['vibe']}\n")
        lines.append("Usage: /aesthetic <style_name> | /aesthetic colors <style> | /aesthetic suggest <profile> | /aesthetic mix <a> <b>")
        return "\n".join(lines)

    @staticmethod
    def apply_style_to_build(style_name: str, build_data: dict) -> dict:
        style = AestheticEngine.get_style(style_name)
        if not style:
            return {"error": f"Unknown style: {style_name}"}
        return {"style": style["name"], "case_color": style["case_color_hex"], "accent_color": style["led_accent_hex"], "font": style["font_suggestion"], "material": style["material_suggestion"], "cable": style["cable_sleeve_color"], "button_type": style["button_type"], "keycaps": style["keycap_style"], "build_components": {"case": f"{style['material_suggestion']} in {style['case_color_name']} ({style['case_color_hex']})", "display_bezel": f"Bezel: {style['display_bezel_color']}", "keyboard": style["keycap_style"], "lighting": f"LED accent: {style['led_accent_hex']}", "cables": style["cable_sleeve_color"], "switches": style["switch_color"]}, "description": f"A {style['name']} build with {style['case_color_name']} case and {style['vibe']} accents."}

    @staticmethod
    def generate_css_theme(style_name: str) -> str:
        style = AestheticEngine.get_style(style_name)
        if not style:
            return f"Unknown style: {style_name}"
        palette = COLOR_PALETTES.get(style_name, {})
        return f"/* {style['name']} CSS Theme */\n:root {{\n  --color-primary: {palette.get('primary', style['case_color_hex'])};\n  --color-accent: {palette.get('accent', style['led_accent_hex'])};\n  --color-background: {palette.get('background', '#000000')};\n  --color-text: {palette.get('text', '#ffffff')};\n  --font-primary: '{style['font_suggestion'].split('/')[0].strip()}', sans-serif;\n}}"

    @staticmethod
    def generate_case_colors(style_name: str) -> str:
        style = AestheticEngine.get_style(style_name)
        if not style:
            return f"Unknown style: {style_name}"
        return f"<b>Case Colors for {style['name']}</b>\n\nHEX: <code>{style['case_color_hex']}</code>\nName: {style['case_color_name']}\nAccent LED: <code>{style['led_accent_hex']}</code>\nMaterial: {style['material_suggestion']}\n\nLook for {style['case_color_name']} spray paint in matte/satin finish."

    @staticmethod
    def suggest_style_for_profile(profile_name: str) -> str:
        profile = profile_name.lower().replace(" ", "_").replace("-", "_")
        for sid, s in AESTHETIC_STYLES.items():
            if profile in s["best_for_profiles"]:
                return f"<b>Recommended style for '{profile_name}'</b>\n\n<b>{s['name']}</b>\n{s['description']}\n\nCase: {s['case_color_name']} ({s['case_color_hex']})\nLED: {s['led_accent_hex']}\nFont: {s['font_suggestion']}\nMaterial: {s['material_suggestion']}"
        all_profiles = set()
        for s in AESTHETIC_STYLES.values():
            all_profiles.update(s["best_for_profiles"])
        return f"<b>No exact match for '{profile_name}'</b>\n\nAvailable profiles: {', '.join(sorted(all_profiles))}"

    @staticmethod
    def mix_styles(primary_style: str, accent_style: str) -> str:
        p = AestheticEngine.get_style(primary_style)
        a = AestheticEngine.get_style(accent_style)
        if not p or not a:
            return f"Unknown style: {primary_style if not p else accent_style}"
        return f"<b>Mixed Style: {p['name']} + {a['name']}</b>\n\nBase: {p['name']} — {p['description']}\nAccent: {a['name']}\n\nCase: {p['case_color_hex']} ({p['case_color_name']})\nLED Accent: {a['led_accent_hex']}\nFont: {p['font_suggestion']}\nMaterial: {p['material_suggestion']}\nCables: {a['cable_sleeve_color']}\nVibe: {p['vibe']} with {a['vibe']} accents"

    @staticmethod
    def compare_styles(a: str, b: str) -> str:
        s1 = AestheticEngine.get_style(a)
        s2 = AestheticEngine.get_style(b)
        if not s1 or not s2:
            return f"Unknown style: {a if not s1 else b}"
        lines = [f"<b>Style Comparison: {s1['name']} vs {s2['name']}</b>\n"]
        for attr, v1, v2 in [("Case", s1["case_color_name"], s2["case_color_name"]), ("HEX", s1["case_color_hex"], s2["case_color_hex"]), ("LED", s1["led_accent_hex"], s2["led_accent_hex"]), ("Material", s1["material_suggestion"], s2["material_suggestion"]), ("Vibe", s1["vibe"], s2["vibe"])]:
            lines.append(f"<b>{attr}:</b> {v1} | {v2}\n")
        return "\n".join(lines)


# ============================================================
# v7.0 — WRITERDECK MODE
# ============================================================
WRITERDECK_DISPLAYS = {
    "waveshare_7.5_eink": {"name": "Waveshare 7.5\" E-Ink", "res": "800x480", "type": "e-ink", "ppi": 125, "refresh_s": 1.5, "power_w": 0.05, "price": 65, "pros": ["Ultra low power", "readable in sunlight", "no eye strain"], "cons": ["Slow refresh", "no color", "grayscale only"]},
    "waveshare_4.2_eink": {"name": "Waveshare 4.2\" E-Ink", "res": "400x300", "type": "e-ink", "ppi": 120, "refresh_s": 1.0, "power_w": 0.03, "price": 35, "pros": ["Tiny power draw", "cheap", "good for text"], "cons": ["Very small", "low resolution", "grayscale"]},
    "waveshare_10.3_eink": {"name": "Waveshare 10.3\" E-Ink", "res": "1872x1404", "type": "e-ink", "ppi": 227, "refresh_s": 2.0, "power_w": 0.08, "price": 150, "pros": ["Near paper quality", "high DPI", "great for reading"], "cons": ["Expensive", "slow refresh", "large"]},
    "raspberry_pi_7_touch": {"name": "Raspberry Pi 7\" Touch", "res": "1024x600", "type": "LCD", "ppi": 170, "refresh_s": 0.016, "power_w": 1.5, "price": 80, "pros": ["Fast refresh", "color", "touch input"], "cons": ["Higher power", "glare", "backlight always on"]},
    "amoled_5.5": {"name": "5.5\" AMOLED HDMI", "res": "1920x1080", "type": "AMOLED", "ppi": 401, "refresh_s": 0.008, "power_w": 1.2, "price": 120, "pros": ["Vibrant colors", "deep blacks", "high res"], "cons": ["Power hungry", "expensive", "burn-in risk"]},
}
WRITER_SOFTWARE = {
    "warewoolf": {"name": "WareWoolf", "type": "GUI (Electron)", "platform": ["Linux", "Windows"], "features": ["Auto-save", "file manager", "word count", "self-email drafts", "dark mode"], "desc": "Purpose-built for writerdecks. No mouse needed, full keyboard control.", "url": "https://github.com/brsloan/warewoolf", "resource_use": "Medium"},
    "zerowriter": {"name": "ZeroWriter", "type": "Terminal (Python)", "platform": ["Linux"], "features": ["File browser", "WiFi control", "minimal UI", "extremely lightweight"], "desc": "Terminal-based writerdeck software. Runs on anything including Pi Zero.", "url": "https://github.com/zerowriter/zerowriter1", "resource_use": "Very Low"},
    "focuswriter": {"name": "FocusWriter", "type": "GUI", "platform": ["Linux", "Windows", "macOS"], "features": ["Distraction-free", "daily goals", "themes", "timer", "typewriter sounds"], "desc": "Mature distraction-free writing app with rich features.", "url": "https://gottcode.org/focuswriter/", "resource_use": "Low"},
    "wordgrinder": {"name": "WordGrinder", "type": "Terminal (C)", "platform": ["Linux", "macOS"], "features": ["Keyboard driven", "Markdown export", "minimal dependencies", "fast startup"], "desc": "Word processor for the terminal. Instant boot, full keyboard control.", "url": "http://cowlark.com/wordgrinder/", "resource_use": "Very Low"},
    "microjournal": {"name": "Micro Journal Rev4", "type": "ESP32 native", "platform": ["ESP32"], "features": ["Instant-on", "30% ortho keyboard", "2.8\" ILI9341", "low power", "boots in <1s"], "desc": "ESP32-powered writerdeck that boots instantly. Full hardware design open source.", "url": "https://github.com/unkyulee/micro-journal", "resource_use": "Minimal"},
    "vim_editor": {"name": "Vim + Goyo/Limelight", "type": "Terminal (CLI)", "platform": ["Linux", "macOS", "Windows"], "features": ["Extreme flexibility", "Goyo distration-free mode", "Limelight focus", "Markdown preview"], "desc": "Vim with distraction-free plugins. Maximum productivity for writers who code.", "url": "https://www.vim.org/", "resource_use": "Very Low"},
}
WRITER_OS_TEMPLATES = {
    "dietpi_minimal": {"name": "DietPi CLI-Only", "base": "DietPi", "size_mb": 800, "boot_to_editor": True, "auto_login": True, "power_idle_w": 2.5, "setup_steps": ["Install DietPi to SD", "Enable auto-login", "Install writing software", "Create .bashrc to launch editor on login", "Disable WiFi/BT for distraction-free"], "packages": ["vim", "git", "tmux", "wordgrinder", "screen"], "notes": "Ultimate low-power writerdeck OS. ~2.5W idle on Pi 5."},
    "rpi_lite_writer": {"name": "Raspberry Pi OS Lite Writer", "base": "Raspberry Pi OS Lite", "size_mb": 1200, "boot_to_editor": True, "auto_login": True, "power_idle_w": 3.0, "setup_steps": ["Flash Raspberry Pi OS Lite", "Enable SSH", "Install writing software", "Configure boot to editor", "Disable desktop services"], "packages": ["vim", "git", "focuswriter", "tmux", "cowsay"], "notes": "Good balance of compatibility and minimalism."},
    "full_desktop_writer": {"name": "Full Desktop + Writer", "base": "Raspberry Pi OS Desktop", "size_mb": 4000, "boot_to_editor": False, "auto_login": True, "power_idle_w": 4.5, "setup_steps": ["Flash Raspberry Pi OS Desktop", "Install writing software", "Set up auto-start editor", "Configure WiFi/BT management"], "packages": ["focuswriter", "libreoffice", "vim", "firefox-esr", "warewoolf"], "notes": "Full desktop experience. Higher power draw but most flexible."},
}
WRITER_KEYBOARDS = {
    "air40": {"name": "Air40 (40% Ortho)", "keys": 40, "layout": "Ortholinear", "switch": "Cherry MX Low Profile", "connectivity": "USB-C", "price": 80, "pros": ["Ultra compact", "low profile", "great for writerdecks"], "cons": ["Small learning curve", "no number row"]},
    "planck": {"name": "Planck (40% Ortho)", "keys": 48, "layout": "Ortholinear", "switch": "Cherry MX", "connectivity": "USB-C", "price": 100, "pros": ["Compact", "fully programmable", "huge community"], "cons": ["No number row", "takes practice"]},
    "preonic": {"name": "Preonic (50% Ortho)", "keys": 60, "layout": "Ortholinear", "switch": "Cherry MX", "connectivity": "USB-C", "price": 120, "pros": ["Number row included", "programmable", "great layout"], "cons": ["Slightly larger than Planck"]},
    "cardkb": {"name": "M5Stack CardKB (I2C)", "keys": 56, "layout": "QWERTY thumb", "switch": "Membrane", "connectivity": "I2C", "price": 15, "pros": ["Tiny footprint", "I2C saves USB port", "cheap"], "cons": ["Membrane keys", "small keys", "not mechanical"]},
    "keychron_k2": {"name": "Keychron K2 (75%)", "keys": 84, "layout": "75% staggered", "switch": "Gateron", "connectivity": "USB-C / BT", "price": 70, "pros": ["Full function row", "BT + wired", "great feel"], "cons": ["Large", "BT battery life ~40h"]},
}

class WriterDeckAdvisor:
    @staticmethod
    def overview() -> str:
        return ("<b>WriterDeck Advisor</b>\n\n"
                "A writerdeck is a distraction-free writing computer. "
                "Minimal OS, e-ink or low-glare display, mechanical keyboard, "
                "and instant-on writing software.\n\n"
                "Commands:\n"
                "  /writerdeck profile     — full writer build rec\n"
                "  /writerdeck display     — e-ink display recommendations\n"
                "  /writerdeck software    — distraction-free writing tools\n"
                "  /writerdeck os          — minimal OS config\n"
                "  /writerdeck keyboard    — writer-friendly keyboards\n"
                "  /writerdeck tune        — power-save config")

    @staticmethod
    def profile(budget: str = "mid") -> str:
        tiers = {"low": {"display": "waveshare_4.2_eink", "sbc": "Raspberry Pi Zero 2W", "os": "dietpi_minimal", "software": "zerowriter", "keyboard": "cardkb", "battery": "18650 5000mAh", "cost": "~$80-120"},
                 "mid": {"display": "waveshare_7.5_eink", "sbc": "Raspberry Pi 5 4GB", "os": "rpi_lite_writer", "software": "wordgrinder", "keyboard": "air40", "battery": "LiPo 10000mAh", "cost": "~$200-350"},
                 "high": {"display": "waveshare_10.3_eink", "sbc": "Orange Pi 5 Max 8GB", "os": "full_desktop_writer", "software": "focuswriter", "keyboard": "preonic", "battery": "LiPo 20000mAh", "cost": "~$400-650"}}
        t = tiers.get(budget, tiers["mid"])
        lines = [f"<b>WriterDeck Profile: {budget.title()} Budget ({t['cost']})</b>\n"]
        lines.append(f"  <b>SBC:</b> {t['sbc']}")
        disp = WRITERDECK_DISPLAYS.get(t["display"], {})
        lines.append(f"  <b>Display:</b> {disp.get('name', t['display'])} ({disp.get('res', '')})")
        lines.append(f"  <b>OS:</b> {WRITER_OS_TEMPLATES.get(t['os'], {}).get('name', t['os'])}")
        sw = WRITER_SOFTWARE.get(t["software"], {})
        lines.append(f"  <b>Software:</b> {sw.get('name', t['software'])} — {sw.get('desc', '')[:80]}")
        kb = WRITER_KEYBOARDS.get(t["keyboard"], {})
        lines.append(f"  <b>Keyboard:</b> {kb.get('name', t['keyboard'])}")
        lines.append(f"  <b>Battery:</b> {t['battery']}")
        lines.append(f"\n  <b>Estimated Total:</b> {t['cost']}")
        return "\n".join(lines)

    @staticmethod
    def display_recs(purpose: str = "writing") -> str:
        if purpose == "eink":
            filtered = {k: v for k, v in WRITERDECK_DISPLAYS.items() if v["type"] == "e-ink"}
        elif purpose == "fast":
            filtered = {k: v for k, v in WRITERDECK_DISPLAYS.items() if v["type"] != "e-ink"}
        else:
            filtered = WRITERDECK_DISPLAYS
        lines = [f"<b>Display Recommendations ({purpose})</b>\n"]
        for k, v in filtered.items():
            lines.append(f"<b>{v['name']}</b>\n  Res: {v['res']} | Power: {v['power_w']}W | Price: ${v['price']}\n  Pros: {', '.join(v['pros'][:2])}\n")
        return "\n".join(lines[:4000])

    @staticmethod
    def software_recs() -> str:
        lines = ["<b>Writer Software Recommendations</b>\n"]
        for k, v in WRITER_SOFTWARE.items():
            lines.append(f"<b>{v['name']}</b> ({v['type']})\n  {v['desc'][:120]}\n  Features: {', '.join(v['features'][:3])}\n  Resource: {v['resource_use']}\n")
        return "\n".join(lines)

    @staticmethod
    def os_recs() -> str:
        lines = ["<b>Writer OS Templates</b>\n"]
        for k, v in WRITER_OS_TEMPLATES.items():
            lines.append(f"<b>{v['name']}</b>\n  Idle power: {v['power_idle_w']}W | Boot to editor: {v['boot_to_editor']}\n  Packages: {', '.join(v['packages'][:4])}\n")
        return "\n".join(lines)

    @staticmethod
    def keyboard_recs() -> str:
        lines = ["<b>Writer-Friendly Keyboards</b>\n"]
        for k, v in WRITER_KEYBOARDS.items():
            lines.append(f"<b>{v['name']}</b> ({v['layout']})\n  Keys: {v['keys']} | Switch: {v['switch']} | ${v['price']}\n  Pros: {', '.join(v['pros'][:2])}\n")
        return "\n".join(lines)

    @staticmethod
    def tune() -> str:
        return ("<b>WriterDeck Power-Save Tuning</b>\n\n"
                "1. <b>Disable WiFi/BT</b> — rfkill block all (save ~0.5W)\n"
                "2. <b>Use CLI-only OS</b> — DietPi minimal (save ~2W vs desktop)\n"
                "3. <b>Reduce display brightness</b> — 30% cuts power by 40%\n"
                "4. <b>E-ink display</b> — 0.05W vs 1.5W for LCD\n"
                "5. <b>Disable HDMI output</b> — tvservice -o when using DPI\n"
                "6. <b>CPU governor: powersave</b> — echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor\n"
                "7. <b>Disable USB ports</b> — hubutil or uhubctl\n"
                "8. <b>Auto-suspend display</b> — setterm -blank 1\n\n"
                "Expected: 2.5-4h on 5000mAh, 6-10h on 10000mAh")

# ============================================================
# v7.0 — THERMAL MANAGEMENT DESIGNER
# ============================================================
SBC_THERMAL_DATA = {
    "Raspberry Pi 5 4GB": {"idle_w": 3.2, "load_w": 12.0, "max_temp_c": 85, "throttle_temp_c": 80, "die_size_mm": 10.2, "recommended_heatsink": "Aluminum 14x14x10mm + thermal pad", "fan_needed": True, "fan_recommended": "30x30x10mm 5V @ 0.2W", "notes": "Pi 5 runs hot — active cooling strongly recommended above 50% load"},
    "Raspberry Pi 5 8GB": {"idle_w": 3.5, "load_w": 15.0, "max_temp_c": 85, "throttle_temp_c": 80, "die_size_mm": 10.2, "recommended_heatsink": "Aluminum 14x14x14mm + thermal pad", "fan_needed": True, "fan_recommended": "30x30x10mm 5V @ 0.2W", "notes": "Same as Pi 5 4GB, slightly higher max draw"},
    "Raspberry Pi 4 4GB": {"idle_w": 2.7, "load_w": 7.6, "max_temp_c": 85, "throttle_temp_c": 80, "die_size_mm": 8.0, "recommended_heatsink": "Aluminum 14x14x6mm + thermal pad", "fan_needed": False, "fan_recommended": "Optional 30x30mm", "notes": "Pi 4 can run passive with good ventilation"},
    "Orange Pi 5 Max 8GB": {"idle_w": 4.0, "load_w": 18.0, "max_temp_c": 90, "throttle_temp_c": 85, "die_size_mm": 12.0, "recommended_heatsink": "Copper 20x20x15mm + thermal paste", "fan_needed": True, "fan_recommended": "40x40x10mm 5V @ 0.3W", "notes": "RK3588 runs very hot under load — active cooling essential"},
    "Jetson Orin Nano 8GB": {"idle_w": 5.0, "load_w": 25.0, "max_temp_c": 90, "throttle_temp_c": 85, "die_size_mm": 14.0, "recommended_heatsink": "Copper 30x30x20mm + Noctua fan", "fan_needed": True, "fan_recommended": "40x40x20mm 5V @ 0.5W", "notes": "AI workloads push thermal limits — overkill cooling recommended"},
    "Raspberry Pi Zero 2W": {"idle_w": 0.8, "load_w": 2.5, "max_temp_c": 85, "throttle_temp_c": 80, "die_size_mm": 5.0, "recommended_heatsink": "Small copper heatsink + thermal pad", "fan_needed": False, "fan_recommended": "None", "notes": "Runs cool enough for passive cooling in most cases"},
    "Radxa Rock 5B": {"idle_w": 3.5, "load_w": 16.0, "max_temp_c": 85, "throttle_temp_c": 80, "die_size_mm": 11.0, "recommended_heatsink": "Aluminum 20x20x12mm + thermal pad", "fan_needed": True, "fan_recommended": "30x30x10mm 5V @ 0.2W", "notes": "Similar thermal profile to Pi 5 under load"},
}
COOLING_PARTS_DATABASE = {
    "heatsink_small_al": {"name": "Small Aluminum Heatsink 14x14x6mm", "type": "heatsink", "material": "Aluminum", "size_mm": "14x14x6", "price": 2, "suitable_for": ["Raspberry Pi Zero 2W", "Raspberry Pi 4 4GB"], "r_theta_cw": 28.0},
    "heatsink_med_al": {"name": "Medium Aluminum Heatsink 14x14x10mm", "type": "heatsink", "material": "Aluminum", "size_mm": "14x14x10", "price": 3, "suitable_for": ["Raspberry Pi 5 4GB", "Raspberry Pi 5 8GB"], "r_theta_cw": 18.0},
    "heatsink_large_cu": {"name": "Large Copper Heatsink 20x20x15mm", "type": "heatsink", "material": "Copper", "size_mm": "20x20x15", "price": 8, "suitable_for": ["Orange Pi 5 Max 8GB", "Radxa Rock 5B"], "r_theta_cw": 10.0},
    "heatsink_xl_cu": {"name": "XL Copper Heatsink 30x30x20mm", "type": "heatsink", "material": "Copper", "size_mm": "30x30x20", "price": 15, "suitable_for": ["Jetson Orin Nano 8GB"], "r_theta_cw": 6.0},
    "fan_30mm": {"name": "30x30x10mm 5V Fan", "type": "fan", "size_mm": "30x30x10", "price": 5, "airflow_cfm": 2.5, "noise_dba": 18, "power_w": 0.2, "suitable_for": ["Raspberry Pi 5 4GB", "Raspberry Pi 5 8GB", "Radxa Rock 5B"]},
    "fan_40mm": {"name": "40x40x10mm 5V Fan", "type": "fan", "size_mm": "40x40x10", "price": 8, "airflow_cfm": 5.0, "noise_dba": 22, "power_w": 0.3, "suitable_for": ["Orange Pi 5 Max 8GB"]},
    "fan_40mm_noctua": {"name": "Noctua NF-A4x20 5V", "type": "fan", "size_mm": "40x40x20", "price": 18, "airflow_cfm": 5.5, "noise_dba": 14, "power_w": 0.5, "suitable_for": ["Jetson Orin Nano 8GB", "Orange Pi 5 Max 8GB"]},
    "vent_grill_set": {"name": "Ventilation Grill Set (2x40mm)", "type": "vent", "size_mm": "40x40", "price": 4, "airflow_improvement_pct": 35},
    "thermal_pad_standard": {"name": "Thermal Pad 1mm (Arctic)", "type": "thermal_pad", "thickness_mm": 1.0, "conductivity_wmk": 6.0, "price": 5},
    "thermal_paste_arctic": {"name": "Arctic MX-6 Thermal Paste", "type": "thermal_paste", "conductivity_wmk": 10.5, "price": 8},
    "thermal_paste_kryonaut": {"name": "Thermal Grizzly Kryonaut", "type": "thermal_paste", "conductivity_wmk": 12.5, "price": 12},
}

class ThermalDesigner:
    @staticmethod
    def overview() -> str:
        return ("<b>Thermal Management Designer</b>\n\n"
                "Design your cyberdeck's cooling system. Calculate heat output, "
                "select heatsinks and fans, optimize ventilation.\n\n"
                "Commands:\n"
                "  /thermal calc <sbc> <load%>   — heat/CFM calculation\n"
                "  /thermal parts <sbc>           — compatible cooling parts\n"
                "  /thermal undervolt <sbc>       — undervolt config\n"
                "  /thermal vent <sbc>            — vent sizing\n"
                "  /thermal compare               — compare cooling solutions")

    @staticmethod
    def calc(sbc_name: str, load_pct: int = 100) -> str:
        sbc = None
        for k, v in SBC_THERMAL_DATA.items():
            if k.lower().startswith(sbc_name.lower()):
                sbc = v
                sbc_key = k
                break
        if not sbc:
            avail = ", ".join(SBC_THERMAL_DATA.keys())
            return f"Unknown SBC. Available: {avail}"
        load_frac = max(10, min(100, load_pct)) / 100.0
        power_w = sbc["idle_w"] + (sbc["load_w"] - sbc["idle_w"]) * load_frac
        # Realistic thermal model: 15C/W passive (heatsink), 4C/W active (fan + heatsink)
        passive_temp = 25 + power_w * 15
        active_temp = 25 + power_w * 4
        fan_needed = sbc["fan_needed"]
        est_temp = active_temp if fan_needed else passive_temp
        cooling_mode = "active (fan + heatsink)" if fan_needed else "passive (heatsink only)"
        throttling = est_temp > sbc["throttle_temp_c"]
        needed_cfm = max(0.5, power_w * 0.4)
        lines = [f"<b>Thermal Report: {sbc_name}</b>", ""]
        lines.append(f"  Load: {load_pct}%")
        lines.append(f"  Estimated Power: {power_w:.1f}W")
        lines.append(f"  Ambient: 25C | Est Die Temp ({cooling_mode}): {est_temp:.0f}C")
        lines.append(f"  Passive only: {passive_temp:.0f}C | With fan: {active_temp:.0f}C")
        lines.append(f"  Max Safe: {sbc['max_temp_c']}C | Throttle: {sbc['throttle_temp_c']}C")
        lines.append(f"  {'[WARNING] THROTTLING RISK' if throttling else '[OK] Within limits'}")
        lines.append(f"")
        lines.append(f"  <b>Cooling Required:</b>")
        lines.append(f"  Minimum airflow: {needed_cfm:.1f} CFM")
        lines.append(f"  Heatsink: {sbc['recommended_heatsink']}")
        if sbc["fan_needed"]:
            lines.append(f"  Fan: {sbc['fan_recommended']}")
        else:
            lines.append(f"  Fan: Not required (passive OK)")
        lines.append(f"")
        lines.append(f"  Tip: {sbc['notes']}")
        return "\n".join(lines)

    @staticmethod
    def parts(sbc_name: str) -> str:
        sbc_key = None
        for k in SBC_THERMAL_DATA:
            if k.lower().startswith(sbc_name.lower()):
                sbc_key = k
                break
        if not sbc_key:
            return f"Unknown SBC."
        compatible = []
        for pid, part in COOLING_PARTS_DATABASE.items():
            if sbc_key in part.get("suitable_for", []):
                compatible.append(part)
        if not compatible:
            return f"No specific cooling parts found for {sbc_key}. General rec: {SBC_THERMAL_DATA[sbc_key]['recommended_heatsink']}"
        lines = [f"<b>Cooling Parts for {sbc_key}</b>\n"]
        for p in compatible:
            lines.append(f"<b>{p['name']}</b> — ${p['price']}")
            if 'airflow_cfm' in p:
                lines.append(f"  Airflow: {p['airflow_cfm']} CFM | Noise: {p['noise_dba']} dBA | Power: {p['power_w']}W")
            if 'r_theta_cw' in p:
                lines.append(f"  Thermal Resistance: {p['r_theta_cw']} C/W")
            if 'conductivity_wmk' in p:
                lines.append(f"  Conductivity: {p['conductivity_wmk']} W/mK")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def undervolt(sbc_name: str) -> str:
        configs = {
            "raspberry pi 5": ("# /boot/firmware/config.txt additions for Pi 5 undervolt\n"
                               "over_voltage=-2\n"
                               "core_freq=500\n"
                               "gpu_freq=300\n"
                               "v3d_freq=300\n"
                               "# Expected: -10C to -15C under load, ~0.5W power savings"),
            "raspberry pi 4": ("# /boot/config.txt additions for Pi 4 undervolt\n"
                               "over_voltage=-2\n"
                               "core_freq=350\n"
                               "gpu_freq=200\n"
                               "# Expected: -5C to -10C under load"),
            "orange pi 5": ("# /boot/config.txt or armbian-config\n"
                            "Use armbian-config -> CPU -> Voltage\n"
                            "Set voltage offset: -50mV to -100mV\n"
                            "Monitor stability with stress test\n"
                            "# Expected: -8C to -12C under load"),
        }
        for key, val in configs.items():
            if sbc_name.lower().startswith(key) or key.startswith(sbc_name.lower()):
                return f"<b>Undervolt Config for {sbc_name}</b>\n\n<pre>{val}</pre>"
        return ("<b>Undervolt Guide (General)</b>\n\n"
                "1. Edit config file: /boot/firmware/config.txt (Pi 5) or /boot/config.txt (Pi 4)\n"
                "2. Add over_voltage=-2 to reduce core voltage\n"
                "3. Lower core_freq to reduce heat generation\n"
                "4. Test stability: vcgencmd measure_temp + stress test\n"
                "5. Expected: 5-15C reduction, 0.3-0.8W power savings\n\n"
                "For Pi-specific config, use: /thermal undervolt \"Raspberry Pi 5\"")

    @staticmethod
    def vent(sbc_name: str) -> str:
        sbc = None
        for k in SBC_THERMAL_DATA:
            if k.lower().startswith(sbc_name.lower()):
                sbc = SBC_THERMAL_DATA[k]
                break
        if not sbc:
            return f"Unknown SBC."
        load_w = sbc["load_w"]
        vent_area_cm2 = load_w * 1.5
        fan_needed = sbc["fan_needed"]
        lines = [f"<b>Ventilation Design for {sbc_name}</b>\n"]
        lines.append(f"  Heat output (max): {load_w}W")
        lines.append(f"  Recommended vent area: {vent_area_cm2:.0f} cm²")
        lines.append(f"  Equivalent to: {vent_area_cm2 / 16:.1f}x 40x40mm grills")
        lines.append(f"  Passive cooling{' NOT' if not fan_needed else ''} sufficient" if not fan_needed else f"  Active fan recommended: {sbc['fan_recommended']}")
        lines.append(f"\n  <b>Tips:</b>")
        lines.append(f"  - Place intake vents low, exhaust vents high")
        lines.append(f"  - Avoid vent placement above SBC (dust falls in)")
        lines.append(f"  - Use mesh filters on intake vents")
        lines.append(f"  - Leave 5-10mm air gap around heatsink fins")
        return "\n".join(lines)

    @staticmethod
    def compare() -> str:
        lines = ["<b>Cooling Solution Comparison</b>\n"]
        for pid, part in COOLING_PARTS_DATABASE.items():
            lines.append(f"<b>{part['name']}</b> — ${part['price']}")
            if 'airflow_cfm' in part:
                lines.append(f"  {part['airflow_cfm']} CFM | {part['noise_dba']} dBA | {part['power_w']}W")
            if 'r_theta_cw' in part:
                lines.append(f"  {part['r_theta_cw']} C/W")
            if 'conductivity_wmk' in part:
                lines.append(f"  {part['conductivity_wmk']} W/mK")
            lines.append("")
        return "\n".join(lines)

# ============================================================
# v7.0 — MULTI-BUILD COMPARATOR
# ============================================================
COMPARISON_METRICS = {
    "cost": {"label": "Total Cost", "unit": "$", "higher_better": False},
    "weight": {"label": "Weight", "unit": "g", "higher_better": False},
    "battery_hours": {"label": "Battery Life", "unit": "h", "higher_better": True},
    "perf_score": {"label": "Performance", "unit": "/100", "higher_better": True},
    "difficulty": {"label": "Build Difficulty", "unit": "/5", "higher_better": False},
    "display_size": {"label": "Display Size", "unit": '"', "higher_better": False},
    "upgradeability": {"label": "Upgradeability", "unit": "/10", "higher_better": True},
}

class BuildComparator:
    def __init__(self):
        self._selection = []

    @staticmethod
    def metric_defs() -> str:
        lines = ["<b>Available Comparison Metrics</b>\n"]
        for k, v in COMPARISON_METRICS.items():
            lines.append(f"<b>{v['label']}</b> ({v['unit']}) — {'Higher' if v['higher_better'] else 'Lower'} is better")
        return "\n".join(lines)

    def add(self, build_id: str) -> str:
        if build_id in self._selection:
            return f"Build '{build_id}' already in comparison"
        self._selection.append(build_id)
        return f"Added '{build_id}' ({len(self._selection)}/3 selected)"

    def remove(self, build_id: str) -> str:
        if build_id in self._selection:
            self._selection.remove(build_id)
            return f"Removed '{build_id}'"
        return f"'{build_id}' not in selection"

    def clear(self) -> str:
        self._selection = []
        return "Comparison selection cleared"

    def selection(self) -> str:
        if not self._selection:
            return "No builds selected. Use /compare add <build_id>"
        lines = [f"<b>Selected Builds ({len(self._selection)}/3)</b>\n"]
        for b in self._selection:
            from_db = SAMPLE_COMMUNITY_BUILDS.get(b) or BOM_PROJECTS_FILE.get(b, {"title": b})
            lines.append(f"  <code>{b}</code> — {from_db.get('title', b)}")
        return "\n".join(lines)

    def score(self, build_id: str = None) -> str:
        check = [build_id] if build_id else self._selection
        if not check:
            return "No build selected. Use /compare add <build_id> or /compare score <build_id>"
        lines = []
        for bid in check[:3]:
            b = SAMPLE_COMMUNITY_BUILDS.get(bid)
            if not b:
                continue
            # Compute a rough score
            cost_score = 100 if b.get("cost_tier") == "Budget ($100-200)" else 60 if "Mid" in b.get("cost_tier", "") else 30
            diff_score = 100 if b.get("difficulty") == "Beginner" else 75 if b.get("difficulty") == "Intermediate" else 40
            feat_score = min(100, len(b.get("features", [])) * 15)
            upvote_score = min(100, b.get("upvotes", 0) / 35)
            total = cost_score * 0.2 + diff_score * 0.2 + feat_score * 0.3 + upvote_score * 0.3
            lines.append(f"<b>{b['title']}</b> Score: {total:.0f}/100")
            lines.append(f"  Cost: {cost_score}/100 | Difficulty: {diff_score}/100")
            lines.append(f"  Features: {feat_score}/100 | Popularity: {upvote_score:.0f}/100\n")
        return "\n".join(lines) if lines else "No valid builds found"

    def compare_builds(self) -> str:
        if len(self._selection) < 2:
            return "Select at least 2 builds (/compare add <id1> <id2>)"
        builds = []
        for bid in self._selection[:3]:
            b = SAMPLE_COMMUNITY_BUILDS.get(bid)
            if b:
                builds.append((bid, b))
        if len(builds) < 2:
            return "Could not find valid builds to compare"
        lines = [f"<b>Build Comparison: {' vs '.join(b[1]['title'] for b in builds)}</b>\n"]
        headers = ["Metric"] + [b[1]['title'][:15] for b in builds]
        rows = []
        for mk, mv in COMPARISON_METRICS.items():
            row = [mv['label']]
            for bid, b in builds:
                val = b.get(mk, 0)
                if mk == "cost":
                    val = {"Budget ($100-200)": 150, "Mid-Range ($200-500)": 350, "Premium ($500+)": 700}.get(b.get("cost_tier", ""), 0)
                elif mk == "difficulty":
                    val = {"Beginner": 2, "Intermediate": 3, "Advanced": 4, "Expert": 5}.get(b.get("difficulty", ""), 3)
                elif mk == "perf_score":
                    val = {"Raspberry Pi 5": 70, "Raspberry Pi 4": 50, "Orange Pi 5": 85, "Jetson Orin Nano": 95, "Raspberry Pi Zero 2W": 25}.get(b.get("sbc", "").split(" ")[0] + " " + b.get("sbc", "").split(" ")[1] if len(b.get("sbc", "").split()) > 1 else b.get("sbc", ""), 50)
                elif mk == "battery_hours":
                    val = {"18650 (2x 3000mAh)": 4, "LiPo 10000mAh": 8, "LiPo 20000mAh": 14, "NP-F970": 10, "18650 (4x 3500mAh)": 12, "Solar + LiFePO4": 24}.get(b.get("battery", ""), 6)
                row.append(f"{val}{mv['unit']}" if val else "—")
            rows.append(row)
        lines.append("<b>" + " | ".join(f"{h:20}" for h in headers) + "</b>")
        for row in rows:
            lines.append(" | ".join(f"{c:20}" for c in row))
        lines.append("\n<i>Higher is better ↑ for: Performance, Battery, Upgradeability</i>")
        lines.append("<i>Lower is better ↓ for: Cost, Weight, Difficulty, Display Size</i>")
        return "\n".join(lines)

# ============================================================
# v7.0 — BUILD COST OPTIMIZER
# ============================================================
PRICE_SOURCE_DATABASE = {
    "Raspberry Pi 5 4GB": [{"vendor": "PiShop.us", "price": 60, "shipping": 5, "url": "https://pishop.us"}, {"vendor": "Adafruit", "price": 60, "shipping": 8, "url": "https://adafruit.com"}, {"vendor": "Amazon", "price": 75, "shipping": 0, "url": "https://amazon.com"}, {"vendor": "AliExpress", "price": 55, "shipping": 3, "url": "https://aliexpress.com", "note": "slower shipping (2-4 weeks)"}],
    "Raspberry Pi 5 8GB": [{"vendor": "PiShop.us", "price": 80, "shipping": 5, "url": "https://pishop.us"}, {"vendor": "Adafruit", "price": 80, "shipping": 8, "url": "https://adafruit.com"}, {"vendor": "Amazon", "price": 95, "shipping": 0, "url": "https://amazon.com"}, {"vendor": "AliExpress", "price": 72, "shipping": 3, "url": "https://aliexpress.com", "note": "slower shipping"}],
    "Waveshare 7.5 E-Ink": [{"vendor": "Waveshare (direct)", "price": 60, "shipping": 5, "url": "https://waveshare.com"}, {"vendor": "Amazon", "price": 75, "shipping": 0, "url": "https://amazon.com"}, {"vendor": "AliExpress", "price": 50, "shipping": 2, "url": "https://aliexpress.com", "note": "authenticity risk"}],
    "Raspberry Pi 7 Touch": [{"vendor": "PiShop.us", "price": 70, "shipping": 5, "url": "https://pishop.us"}, {"vendor": "Adafruit", "price": 80, "shipping": 8, "url": "https://adafruit.com"}, {"vendor": "Amazon", "price": 85, "shipping": 0, "url": "https://amazon.com"}],
    "Air40 Keyboard": [{"vendor": "Drop", "price": 80, "shipping": 5, "url": "https://drop.com"}, {"vendor": "AliExpress", "price": 55, "shipping": 3, "url": "https://aliexpress.com"}],
    "LiPo 10000mAh": [{"vendor": "Adafruit", "price": 30, "shipping": 8, "url": "https://adafruit.com"}, {"vendor": "Amazon", "price": 25, "shipping": 0, "url": "https://amazon.com"}, {"vendor": "AliExpress", "price": 18, "shipping": 2, "url": "https://aliexpress.com"}],
    "SD Card 128GB": [{"vendor": "Amazon", "price": 15, "shipping": 0, "url": "https://amazon.com"}, {"vendor": "Best Buy", "price": 18, "shipping": 0, "url": "https://bestbuy.com"}, {"vendor": "AliExpress", "price": 10, "shipping": 1, "url": "https://aliexpress.com"}],
}
REGION_VENDORS = {
    "us": ["PiShop.us", "Adafruit", "Amazon", "SparkFun"],
    "uk": ["The Pi Hut", "Pimoroni", "Amazon UK"],
    "eu": ["PiShop.eu", "Amazon DE", "BuyZero", "Reichelt"],
    "asia": ["AliExpress", "Amazon JP", "Seeed Studio"],
    "au": ["Core Electronics", "Amazon AU", "Little Bird"],
}
BUDGET_TEMPLATES = {
    "ultra_budget": {"name": "Ultra Budget", "max_cost": 100, "sbc": "Raspberry Pi Zero 2W", "display": "waveshare_4.2_eink", "battery": "18650 5000mAh", "keyboard": "cardkb", "case": "3D printed PLA", "os": "DietPi", "notes": "Bare essentials. Great for learning."},
    "budget": {"name": "Budget Build", "max_cost": 200, "sbc": "Raspberry Pi 4 4GB", "display": "Waveshare 7.5 E-Ink", "battery": "LiPo 10000mAh", "keyboard": "air40", "case": "3D printed PETG", "os": "Raspberry Pi OS Lite", "notes": "Solid writerdeck or terminal deck."},
    "mid_range": {"name": "Mid-Range", "max_cost": 400, "sbc": "Raspberry Pi 5 8GB", "display": "Raspberry Pi 7 Touch", "battery": "LiPo 20000mAh", "keyboard": "preonic", "case": "Pelican 1150", "os": "Raspberry Pi OS Full", "notes": "Versatile daily driver."},
    "premium": {"name": "Premium Build", "max_cost": 800, "sbc": "Orange Pi 5 Max 16GB", "display": "10\" HDMI 1920x1200", "battery": "LiFePO4 12Ah", "keyboard": "keychron_k2", "case": "CNC aluminum", "os": "Ubuntu MATE", "notes": "High performance, no compromises."},
}

class CostOptimizer:
    @staticmethod
    def overview() -> str:
        return ("<b>Build Cost Optimizer</b>\n\n"
                "Find the cheapest sources for your cyberdeck parts, optimize "
                "your BOM for any budget, and discover cost-saving alternatives.\n\n"
                "Commands:\n"
                "  /cost <budget>         — optimize BOM for budget (ultra_budget|budget|mid_range|premium)\n"
                "  /cost parts <part>     — cheapest sources for a part\n"
                "  /cost alternate <part> — cheaper substitutes\n"
                "  /cost regions <region> — vendors by region (us|uk|eu|asia|au)")

    @staticmethod
    def budget_template(tier: str) -> str:
        t = BUDGET_TEMPLATES.get(tier)
        if not t:
            avail = ", ".join(BUDGET_TEMPLATES.keys())
            return f"Unknown tier. Available: {avail}"
        lines = [f"<b>Budget Template: {t['name']}</b> (max ${t['max_cost']})\n"]
        lines.append(f"  SBC: {t['sbc']}")
        lines.append(f"  Display: {t['display']}")
        lines.append(f"  Battery: {t['battery']}")
        lines.append(f"  Keyboard: {t['keyboard']}")
        lines.append(f"  Case: {t['case']}")
        lines.append(f"  OS: {t['os']}")
        lines.append(f"\n  Note: {t['notes']}")
        return "\n".join(lines)

    @staticmethod
    def part_prices(part_name: str) -> str:
        sources = None
        for k, v in PRICE_SOURCE_DATABASE.items():
            if part_name.lower() in k.lower():
                sources = v
                part_key = k
                break
        if not sources:
            avail = ", ".join(PRICE_SOURCE_DATABASE.keys())
            return f"Part not found. Available: {avail}"
        sorted_src = sorted(sources, key=lambda x: x["price"])
        lines = [f"<b>Price Comparison: {part_key}</b>\n"]
        for s in sorted_src:
            total = s["price"] + s["shipping"]
            note = f" — {s.get('note', '')}" if s.get("note") else ""
            lines.append(f"<b>{s['vendor']}</b>: ${s['price']} + ${s['shipping']} shipping = ${total}{note}")
        lines.append(f"\nCheapest: <b>{sorted_src[0]['vendor']}</b> at ${sorted_src[0]['price'] + sorted_src[0]['shipping']} total")
        lines.append(f"Fastest: <b>{sorted_src[-1]['vendor']}</b> at ${sorted_src[-1]['price'] + sorted_src[-1]['shipping']} (free shipping)")
        return "\n".join(lines)

    @staticmethod
    def alternate(part_name: str) -> str:
        alternates = {
            "Raspberry Pi 5 8GB": [("Orange Pi 5 8GB", "$55", "Similar perf, uses RK3588"), ("Radxa Rock 5B", "$80", "More GPIO, similar power")],
            "Raspberry Pi 5 4GB": [("Orange Pi 5 4GB", "$45", "More CPU power for less"), ("Khadas Edge2 4GB", "$70", "Smaller footprint")],
            "Waveshare 7.5 E-Ink": [("Waveshare 6.0 E-Ink", "$40", "Smaller, cheaper"), ("GoodDisplay 7.5", "$55", "Alternative e-ink vendor")],
            "LiPo 10000mAh": [("18650 4x 3500mAh", "$24", "Replaceable cells, no soldering"), ("LiFePO4 10Ah", "$40", "Safer chemistry, longer life")],
            "Air40 Keyboard": [("CardKB I2C", "$15", "Tiny I2C keyboard, saves USB port"), ("Planck", "$100", "Full mechanical ortho")],
        }
        for k, alts in alternates.items():
            if part_name.lower() in k.lower():
                lines = [f"<b>Alternatives for: {k}</b>\n"]
                for name, price, reason in alts:
                    lines.append(f"<b>{name}</b> - ~{price}\n  {reason}\n")
                return "\n".join(lines)
        return f"No alternatives found for '{part_name}'. Try a more specific part name."

    @staticmethod
    def regions(region: str) -> str:
        vendors = REGION_VENDORS.get(region)
        if not vendors:
            avail = ", ".join(REGION_VENDORS.keys())
            return f"Unknown region. Available: {avail}"
        lines = [f"<b>Vendors for {region.upper()} Region</b>\n"]
        for v in vendors:
            lines.append(f"  • {v}")
        lines.append("\nTip: AliExpress ships globally with low prices but longer delivery (2-6 weeks).")
        return "\n".join(lines)

# ============================================================
# v7.0 — UPGRADE PATH ANALYZER
# ============================================================
UPGRADE_PATHS_DATABASE = {
    "sbc": [
        {"from": "Raspberry Pi 4 4GB", "to": "Raspberry Pi 5 8GB", "cost": 80, "perf_gain_pct": 180, "effort": "Medium", "notes": "New Pi 5 board, same form factor. Requires new SD card or reinstall."},
        {"from": "Raspberry Pi 5 4GB", "to": "Raspberry Pi 5 8GB", "cost": 20, "perf_gain_pct": 15, "effort": "Low", "notes": "Only RAM difference. Drop-in replacement."},
        {"from": "Raspberry Pi Zero 2W", "to": "Raspberry Pi 5 4GB", "cost": 60, "perf_gain_pct": 500, "effort": "High", "notes": "Complete rebuild — different form factor, power, and cooling needs."},
        {"from": "Raspberry Pi 5 8GB", "to": "Orange Pi 5 Max 16GB", "cost": 120, "perf_gain_pct": 60, "effort": "Medium", "notes": "More RAM + CPU cores. May need different GPIO layout."},
    ],
    "display": [
        {"from": "7\" 1024x600 LCD", "to": "10\" 1920x1200 LCD", "cost": 80, "perf_gain_pct": 40, "effort": "Low", "notes": "Larger display needs bigger case or mounting plate."},
        {"from": "5\" HDMI", "to": "7.5\" E-Ink", "cost": 40, "perf_gain_pct": 30, "effort": "Low", "notes": "Works great for writerdecks. Different driver needed."},
        {"from": "LCD 7\"", "to": "AMOLED 5.5\"", "cost": 40, "perf_gain_pct": 20, "effort": "Low", "notes": "Better colors, higher res, but smaller."},
    ],
    "battery": [
        {"from": "5000mAh LiPo", "to": "10000mAh LiPo", "cost": 20, "perf_gain_pct": 80, "effort": "Low", "notes": "Double capacity, same voltage. Check physical fit."},
        {"from": "10000mAh LiPo", "to": "20000mAh LiPo", "cost": 30, "perf_gain_pct": 90, "effort": "Low", "notes": "Significant weight and space increase."},
        {"from": "18650 2x3000mAh", "to": "18650 4x3500mAh", "cost": 15, "perf_gain_pct": 130, "effort": "Medium", "notes": "Needs larger battery holder and possibly new BMS."},
    ],
    "memory": [
        {"from": "4GB", "to": "8GB", "cost": 20, "perf_gain_pct": 25, "effort": "Low", "notes": "Only if board supports upgrade (Pi 5)."},
        {"from": "8GB", "to": "16GB", "cost": 40, "perf_gain_pct": 15, "effort": "Low", "notes": "Beneficial for AI/LLM workloads."},
    ],
}

class UpgradeAdvisor:
    @staticmethod
    def overview() -> str:
        return ("<b>Upgrade Path Analyzer</b>\n\n"
                "Plan your cyberdeck upgrade path. See which component upgrades "
                "give the best performance per dollar.\n\n"
                "Commands:\n"
                "  /upgrade <build_id>       — full upgrade report\n"
                "  /upgrade sbc              — SBC upgrade options\n"
                "  /upgrade display          — display upgrade options\n"
                "  /upgrade battery          — battery upgrade options\n"
                "  /upgrade list             — all upgrade categories")

    @staticmethod
    def list_upgrades(category: str = None) -> str:
        if category and category in UPGRADE_PATHS_DATABASE:
            paths = UPGRADE_PATHS_DATABASE[category]
            lines = [f"<b>Upgrade Paths: {category.upper()}</b>\n"]
            for p in paths:
                lines.append(f"<b>{p['from']}</b> → <b>{p['to']}</b>")
                lines.append(f"  Cost: ${p['cost']} | Gain: +{p['perf_gain_pct']}% | Effort: {p['effort']}")
                lines.append(f"  {p['notes']}\n")
            return "\n".join(lines)
        elif category:
            return f"Unknown category: {category}. Available: sbc, display, battery, memory"
        lines = ["<b>All Upgrade Paths</b>\n"]
        for cat, paths in UPGRADE_PATHS_DATABASE.items():
            lines.append(f"<b>{cat.upper()}</b> ({len(paths)} upgrades available)")
            for p in paths:
                lines.append(f"  {p['from']} → {p['to']} | ${p['cost']} | +{p['perf_gain_pct']}%")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def upgrade_report(build_id: str) -> str:
        b = SAMPLE_COMMUNITY_BUILDS.get(build_id)
        if not b:
            return f"Unknown build '{build_id}'. Use /explore to see available builds."
        lines = [f"<b>Upgrade Report: {b['title']}</b>\n"]
        sbc = b.get("sbc", "")
        display = b.get("display", "")
        battery = b.get("battery", "")
        suggestions = []
        for cat, paths in UPGRADE_PATHS_DATABASE.items():
            for p in paths:
                if p["from"].lower() in sbc.lower() or p["from"].lower() in display.lower() or p["from"].lower() in battery.lower():
                    suggestions.append(p)
        if not suggestions:
            return f"No upgrade paths found for '{b['title']}'. Try /upgrade list"
        lines.append(f"<b>Recommended Upgrades:</b>\n")
        for s in sorted(suggestions, key=lambda x: -x["perf_gain_pct"] / max(1, x["cost"])):
            perf_per_dollar = s["perf_gain_pct"] / max(1, s["cost"])
            lines.append(f"<b>{s['from']} → {s['to']}</b>")
            lines.append(f"  ${s['cost']} | +{s['perf_gain_pct']}% perf | {perf_per_dollar:.1f}%/$\n")
        return "\n".join(lines)

# ============================================================
# v7.0 — SOLAR & OFF-GRID POWER PLANNER
# ============================================================
SOLAR_PANEL_DATABASE = {
    "foldable_20w": {"name": "Foldable 20W Monocrystalline", "watts": 20, "type": "Monocrystalline", "vmp_v": 18.0, "imp_a": 1.11, "folded_mm": "240x170x30", "weight_g": 450, "price": 45, "waterproof": True, "usb_output": True, "note": "Good for small decks (Pi Zero + e-ink). Fits in bag."},
    "foldable_50w": {"name": "Foldable 50W Monocrystalline", "watts": 50, "type": "Monocrystalline", "vmp_v": 18.5, "imp_a": 2.70, "folded_mm": "420x280x35", "weight_g": 950, "price": 85, "waterproof": True, "usb_output": True, "note": "Popular size for mid-range builds."},
    "rigid_100w": {"name": "Rigid 100W Polycrystalline", "watts": 100, "type": "Polycrystalline", "vmp_v": 19.2, "imp_a": 5.21, "folded_mm": "670x540x30", "weight_g": 2200, "price": 100, "waterproof": True, "usb_output": False, "note": "Large, stationary panel. Needs external charge controller."},
    "flexible_30w": {"name": "Flexible 30W ETFE", "watts": 30, "type": "Monocrystalline", "vmp_v": 18.0, "imp_a": 1.67, "folded_mm": "350x250x2", "weight_g": 300, "price": 40, "waterproof": True, "usb_output": True, "note": "Ultra thin and light. Can mount on case surface."},
}
BATTERY_BANK_DATABASE = {
    "lipo_5000": {"name": "LiPo 5000mAh 3S", "capacity_wh": 55.5, "voltage_v": 11.1, "chemistry": "LiPo", "weight_g": 180, "price": 25, "cycles": 300, "safety": "Requires balance charger, fire risk if punctured"},
    "lipo_10000": {"name": "LiPo 10000mAh 3S", "capacity_wh": 111, "voltage_v": 11.1, "chemistry": "LiPo", "weight_g": 350, "price": 40, "cycles": 300, "safety": "Most common cyberdeck battery"},
    "lifepo4_12ah": {"name": "LiFePO4 12Ah 4S", "capacity_wh": 153.6, "voltage_v": 12.8, "chemistry": "LiFePO4", "weight_g": 1200, "price": 65, "cycles": 2000, "safety": "Safest chemistry, long cycle life, heavy"},
    "18650_4x3500": {"name": "18650 4x 3500mAh (3S4P)", "capacity_wh": 51.8, "voltage_v": 11.1, "chemistry": "18650 Li-Ion", "weight_g": 200, "price": 24, "cycles": 500, "safety": "Replaceable cells, requires BMS"},
}
SOLAR_CONTROLLER_DATABASE = {
    "usb_direct": {"name": "USB Direct (panel to deck)", "type": "Direct USB", "price": 0, "efficiency_pct": 80, "max_w": 30, "note": "Panel with built-in USB. Simplest, but less efficient."},
    "pwm_5a": {"name": "PWM 5A Solar Controller", "type": "PWM", "price": 12, "efficiency_pct": 75, "max_w": 60, "note": "Cheap but inefficient. OK for small panels <50W."},
    "mppt_10a": {"name": "MPPT 10A Solar Controller", "type": "MPPT", "price": 35, "efficiency_pct": 95, "max_w": 120, "note": "Best efficiency. Recommended for all solar builds."},
}
SUN_HOURS_BY_REGION = {
    "north_america_north": {"label": "North America (Northern)", "winter": 2.0, "spring": 4.5, "summer": 6.0, "fall": 3.5},
    "north_america_south": {"label": "North America (Southern)", "winter": 4.0, "spring": 5.5, "summer": 7.0, "fall": 5.0},
    "europe_north": {"label": "Europe (Northern)", "winter": 1.0, "spring": 3.5, "summer": 5.5, "fall": 2.5},
    "europe_south": {"label": "Europe (Southern)", "winter": 3.0, "spring": 5.0, "summer": 7.5, "fall": 4.5},
    "asia_tropical": {"label": "Asia (Tropical)", "winter": 5.0, "spring": 6.0, "summer": 5.5, "fall": 5.0},
    "asia_temperate": {"label": "Asia (Temperate)", "winter": 2.5, "spring": 4.5, "summer": 6.0, "fall": 3.5},
    "australia": {"label": "Australia / Oceania", "winter": 4.0, "spring": 5.5, "summer": 7.0, "fall": 5.5},
    "south_america": {"label": "South America", "winter": 3.5, "spring": 5.0, "summer": 6.5, "fall": 4.5},
    "africa": {"label": "Africa", "winter": 5.0, "spring": 6.0, "summer": 7.0, "fall": 5.5},
}
OFFGRID_TEMPLATES = {
    "light_solar": {"name": "Light Solar Kit", "panel": "foldable_20w", "battery": "lipo_5000", "controller": "usb_direct", "total_cost": 70, "runtime_h": 4, "notes": "Keep your deck charged during day hikes. Enough for Pi Zero + e-ink."},
    "mid_solar": {"name": "Mid-Range Solar Kit", "panel": "foldable_50w", "battery": "lipo_10000", "controller": "mppt_10a", "total_cost": 160, "runtime_h": 10, "notes": "Full day off-grid power for most builds. Sweet spot for value."},
    "heavy_solar": {"name": "Heavy Solar Rig", "panel": "rigid_100w", "battery": "lifepo4_12ah", "controller": "mppt_10a", "total_cost": 265, "runtime_h": 24, "notes": "Multi-day off-grid. Can power a full desktop setup indefinitely."},
}

class SolarPlanner:
    @staticmethod
    def overview() -> str:
        return ("<b>Solar & Off-Grid Power Planner</b>\n\n"
                "Design a solar charging system for your cyberdeck. Calculate "
                "panel size, battery bank, and controller needs based on your "
                "location and power requirements.\n\n"
                "Commands:\n"
                "  /solar             — overview\n"
                "  /solar calc <Wh> <region>  — panel + battery sizing\n"
                "  /solar parts       — available solar components\n"
                "  /solar setup       — complete off-grid configs\n"
                "  /solar regions     — sun-hours by region")

    @staticmethod
    def calc(watt_hours: int, region: str = "north_america_south") -> str:
        try:
            wh = int(watt_hours)
        except:
            return "watt_hours must be a number (e.g., /solar calc 50 north_america_south)"
        region_data = SUN_HOURS_BY_REGION.get(region, SUN_HOURS_BY_REGION["north_america_south"])
        avg_sun = (region_data["winter"] + region_data["summer"]) / 2
        worst_sun = region_data["winter"]
        panel_w_worst = wh / worst_sun * 1.3  # 30% overhead for efficiency losses
        panel_w_avg = wh / avg_sun * 1.3
        battery_wh = wh * 2  # 2x for safety margin
        lines = [f"<b>Solar Calculation</b>\n"]
        lines.append(f"  Daily load: {wh}Wh")
        lines.append(f"  Region: {region_data['label']}")
        lines.append(f"  Winter sun: {worst_sun}h/day | Summer sun: {SUN_HOURS_BY_REGION[region]['summer']}h/day")
        lines.append(f"")
        lines.append(f"  <b>Panel needed:</b>")
        lines.append(f"    Worst-case (winter): {panel_w_worst:.0f}W")
        lines.append(f"    Average: {panel_w_avg:.0f}W")
        lines.append(f"  <b>Battery needed:</b> {battery_wh:.0f}Wh")
        lines.append(f"")
        lines.append(f"  <b>Recommendation:</b>")
        if panel_w_worst <= 20:
            lines.append(f"    Panel: 20W foldable ({ipanel_search(20)})")
        elif panel_w_worst <= 50:
            lines.append(f"    Panel: 50W foldable ({ipanel_search(50)})")
        else:
            lines.append(f"    Panel: 100W rigid ({ipanel_search(100)})")
        if battery_wh <= 60:
            lines.append(f"    Battery: LiPo 5000mAh (55.5Wh)")
        elif battery_wh <= 120:
            lines.append(f"    Battery: LiPo 10000mAh (111Wh)")
        else:
            lines.append(f"    Battery: LiFePO4 12Ah (153.6Wh)")
        lines.append(f"    Controller: MPPT 10A recommended")
        return "\n".join(lines)

    @staticmethod
    def parts() -> str:
        lines = ["<b>Solar Components</b>\n"]
        lines.append("<b>Panels:</b>")
        for k, v in SOLAR_PANEL_DATABASE.items():
            lines.append(f"  {v['name']} — ${v['price']} | {v['watts']}W | {v['weight_g']}g")
        lines.append("\n<b>Batteries:</b>")
        for k, v in BATTERY_BANK_DATABASE.items():
            lines.append(f"  {v['name']} — ${v['price']} | {v['capacity_wh']}Wh | {v['chemistry']}")
        lines.append("\n<b>Controllers:</b>")
        for k, v in SOLAR_CONTROLLER_DATABASE.items():
            lines.append(f"  {v['name']} — ${v['price']} | {v['efficiency_pct']}% eff")
        lines.append("\n<b>Cable guide:</b> For <5A runs up to 5m, use 14AWG. For >5A, use 10AWG.")
        return "\n".join(lines)

    @staticmethod
    def setup() -> str:
        lines = ["<b>Off-Grid Solar Setups</b>\n"]
        for k, v in OFFGRID_TEMPLATES.items():
            panel = SOLAR_PANEL_DATABASE.get(v["panel"], {})
            battery = BATTERY_BANK_DATABASE.get(v["battery"], {})
            controller = SOLAR_CONTROLLER_DATABASE.get(v["controller"], {})
            lines.append(f"<b>{v['name']}</b> — ${v['total_cost']}")
            lines.append(f"  Panel: {panel.get('name', v['panel'])}")
            lines.append(f"  Battery: {battery.get('name', v['battery'])} ({battery.get('capacity_wh', '')}Wh)")
            lines.append(f"  Controller: {controller.get('name', v['controller'])}")
            lines.append(f"  Est. runtime: {v['runtime_h']}h | {v['notes']}\n")
        return "\n".join(lines)

    @staticmethod
    def regions() -> str:
        lines = ["<b>Sun Hours by Region</b>\n"]
        lines.append("(Hours of peak sunlight per day)\n")
        for k, v in SUN_HOURS_BY_REGION.items():
            lines.append(f"<b>{v['label']}</b>: Winter {v['winter']}h | Summer {v['summer']}h | Avg {((v['winter'] + v['summer']) / 2):.1f}h")
        return "\n".join(lines)

def ipanel_search(w):
    for k, v in SOLAR_PANEL_DATABASE.items():
        if v["watts"] == w:
            return f"${v['price']}"
    return ""

# ============================================================
# v7.0 — BEGINNER BUILD WIZARD
# ============================================================
WIZARD_QUESTIONS = [
    {"step": 1, "question": "What's your build purpose?", "field": "purpose",
     "options": {"writer": "Distraction-free writing machine", "coding": "Portable coding terminal",
                 "hacking": "Security pentesting / Kali", "media": "Media consumption / general",
                 "ai": "AI / LLM experiments", "ham": "Ham radio / SDR", "gaming": "Retro gaming",
                 "offgrid": "Off-grid survival / solar"}},
    {"step": 2, "question": "What's your budget?", "field": "budget",
     "options": {"ultra_budget": "Under $100 (absolute basics)", "budget": "$100-200 (good starter)",
                 "mid": "$200-400 (quality build)", "premium": "$400+ (no compromises)"}},
    {"step": 3, "question": "What's your skill level?", "field": "skill",
     "options": {"beginner": "Never built a computer before", "intermediate": "Some electronics experience",
                 "advanced": "Comfortable with soldering and Linux"}},
    {"step": 4, "question": "How portable should it be?", "field": "portability",
     "options": {"pocket": "Fits in a jacket pocket", "bag": "Fits in a small bag",
                 "briefcase": "Briefcase / Pelican case size", "desktop": "Stays on a desk"}},
    {"step": 5, "question": "Display preference?", "field": "display",
     "options": {"eink": "E-ink (low power, readable in sun)", "small_lcd": "Small LCD 5-7\"",
                 "large_lcd": "Large LCD 7-10\"", "touch": "Touch screen (7\"+)"}},
    {"step": 6, "question": "Battery life needed?", "field": "battery",
     "options": {"minimal": "2-4 hours (plugged in most of the time)",
                 "moderate": "4-8 hours (all-day use)",
                 "extended": "8-12 hours (full day off-grid)"}},
]
WIZARD_TEMPLATES = {
    "writer_budget_beginner": {
        "sbc": "Raspberry Pi Zero 2W", "display": "Waveshare 4.2\" E-Ink",
        "keyboard": "M5Stack CardKB (I2C)", "battery": "18650 5000mAh",
        "os": "DietPi CLI", "case": "3D printed PLA (or cardboard prototype!)",
        "tools_needed": ["Screwdriver set", "Wire strippers", "Soldering iron (optional)"],
        "build_time": "3-5 hours", "cost": "~$80-120", "tutorial": "https://www.writerdeck.org/",
        "tips": ["Start with cardboard mockup before buying case", "Use DietPi for minimal power draw", "FocusWriter or WordGrinder for distraction-free writing"]},
    "coding_mid_intermediate": {
        "sbc": "Raspberry Pi 5 4GB", "display": "Raspberry Pi 7\" Touch",
        "keyboard": "Air40 40% Ortho", "battery": "LiPo 10000mAh",
        "os": "Raspberry Pi OS Lite + i3wm", "case": "3D printed PETG or acrylic stack",
        "tools_needed": ["Screwdriver set", "Wire strippers", "Multimeter", "3D printer access"],
        "build_time": "8-15 hours", "cost": "~$250-350",
        "tips": ["i3wm + terminal = perfect coding environment", "Use tmux for split panes", "Add a UPS HAT for safe shutdown"]},
    "hacking_mid_advanced": {
        "sbc": "Raspberry Pi 5 8GB", "display": "Raspberry Pi 7\" Touch",
        "keyboard": "Preonic 50% Ortho", "battery": "LiPo 20000mAh",
        "os": "Kali Linux", "case": "Pelican 1170 with foam cutout",
        "tools_needed": ["Soldering station", "Multimeter", "USB hub", "WiFi adapter (if not built-in)"],
        "build_time": "15-25 hours", "cost": "~$400-550",
        "tips": ["Use Kali on separate SD card", "Add hardware kill switches for WiFi/Radio", "Include SDR for signal analysis"]},
}

class BeginnerWizard:
    def __init__(self):
        self._sessions = {}

    def get_session(self, uid: str):
        return self._sessions.get(str(uid), {"step": 0, "answers": {}})

    def start(self, uid: str) -> str:
        self._sessions[str(uid)] = {"step": 1, "answers": {}}
        return self._ask(1)

    def _ask(self, step: int) -> str:
        for q in WIZARD_QUESTIONS:
            if q["step"] == step:
                opts = "\n".join(f"  <code>{k}</code> — {v}" for k, v in q["options"].items())
                return f"<b>Step {step}/{len(WIZARD_QUESTIONS)}: {q['question']}</b>\n\n{opts}\n\nReply: /wizard step {step} <option>"
        return "Wizard complete! Use /wizard result to see your build."

    def answer(self, uid: str, step: int, answer: str) -> str:
        session = self._sessions.get(str(uid))
        if not session:
            return "No active wizard. Start with /wizard"
        q = None
        for qq in WIZARD_QUESTIONS:
            if qq["step"] == step:
                q = qq
                break
        if not q:
            return f"Invalid step {step}"
        if answer not in q["options"]:
            return f"Invalid option. Choose: {', '.join(q['options'].keys())}"
        session["answers"][q["field"]] = answer
        next_step = step + 1
        if next_step > len(WIZARD_QUESTIONS):
            return self.result(uid)
        session["step"] = next_step
        return self._ask(next_step)

    def result(self, uid: str) -> str:
        session = self._sessions.get(str(uid))
        if not session or len(session["answers"]) < len(WIZARD_QUESTIONS):
            return "Wizard not complete. Use /wizard to start or /wizard step <n> to continue."
        a = session["answers"]
        purpose = a.get("purpose", "coding")
        budget = a.get("budget", "mid")
        skill = a.get("skill", "beginner")
        key = f"{purpose}_{budget}_{skill}"
        template = WIZARD_TEMPLATES.get(key) or WIZARD_TEMPLATES.get(f"{purpose}_mid_intermediate") or list(WIZARD_TEMPLATES.values())[0]
        lines = [f"<b>Your Build Plan</b>\n"]
        lines.append(f"<b>SBC:</b> {template['sbc']}")
        lines.append(f"<b>Display:</b> {template['display']}")
        lines.append(f"<b>Keyboard:</b> {template['keyboard']}")
        lines.append(f"<b>Battery:</b> {template['battery']}")
        lines.append(f"<b>OS:</b> {template['os']}")
        lines.append(f"<b>Case:</b> {template['case']}")
        lines.append(f"\n<b>Estimated cost:</b> {template['cost']}")
        lines.append(f"<b>Build time:</b> {template['build_time']}")
        lines.append(f"\n<b>Tools needed:</b> {', '.join(template['tools_needed'])}")
        lines.append(f"\n<b>Pro tips:</b>")
        for tip in template['tips']:
            lines.append(f"  • {tip}")
        self._sessions[str(uid)]["step"] = 0
        return "\n".join(lines)

    def reset(self, uid: str) -> str:
        self._sessions.pop(str(uid), None)
        return "Wizard reset. Use /wizard to start fresh."

    def faq(self) -> str:
        return ("<b>Beginner FAQ</b>\n\n"
                "Q: What's the easiest first build?\n"
                "A: A Raspberry Pi 4/5 + 7\" touch screen + mechanical keyboard "
                "in a 3D printed case. Raspberry Pi OS works out of the box.\n\n"
                "Q: Do I need to know programming?\n"
                "A: No! Assembly is mechanical. You'll learn Linux as you go.\n\n"
                "Q: What tools do I need?\n"
                "A: Basic: screwdriver set. Intermediate: + wire strippers, multimeter. "
                "Advanced: + soldering iron, 3D printer.\n\n"
                "Q: How much does a basic build cost?\n"
                "A: $80-120 for a minimalist writerdeck. $200-350 for a solid general build.\n\n"
                "Q: Can I use a laptop instead of a Pi?\n"
                "A: Yes! Many cyberdecks repurpose laptop motherboards (cheap ThinkPads are popular).\n\n"
                "Q: What OS should I use?\n"
                "A: Start with Raspberry Pi OS. DietPi for minimal builds. Kali for security.")

# ============================================================
# v7.0 — BUILD SHARING & EXPORT
# ============================================================
SHARE_TEMPLATES = {
    "reddit": {
        "template": "**{title}** — My Cyberdeck Build\n\n"
                     "Here's my {category} build!\n\n"
                     "## Hardware\n"
                     "- SBC: {sbc}\n"
                     "- Display: {display}\n"
                     "- Battery: {battery}\n"
                     "- Keyboard: {keyboard}\n"
                     "- Case: {case}\n\n"
                     "## Features\n"
                     "{features}\n\n"
                     "## Build Notes\n"
                     "{notes}\n\n"
                     "## Cost\n"
                     "{cost}\n\n"
                     "Built with love and patience. Questions welcome!",
        "tags": "[cyberdeck] [build] [showcase]"},
    "hackaday": {
        "template": "= {title} =\n\n"
                     "A {category} cyberdeck built by {author}\n\n"
                     "== Hardware ==\n"
                     "* SBC: {sbc}\n"
                     "* Display: {display}\n"
                     "* Battery: {battery}\n"
                     "* Keyboard: {keyboard}\n"
                     "* Case: {case}\n\n"
                     "== Features ==\n"
                     "{features}\n\n"
                     "== Build Process ==\n"
                     "{notes}\n\n"
                     "== BOM ==\n"
                     "{bom}\n\n"
                     "[[Category: Cyberdeck]] [[Category: DIY]]",
        "tags": ""},
    "github_readme": {
        "template": "# {title}\n\n"
                     "A {category} cyberdeck build.\n\n"
                     "## Hardware\n\n"
                     "| Component | Part |\n"
                     "|-----------|------|\n"
                     "| SBC | {sbc} |\n"
                     "| Display | {display} |\n"
                     "| Battery | {battery} |\n"
                     "| Keyboard | {keyboard} |\n"
                     "| Case | {case} |\n\n"
                     "## Features\n\n{features}\n\n"
                     "## Setup\n\n{notes}\n\n"
                     "## BOM\n\n{bom}\n\n"
                     "## License\n\nMIT",
        "tags": ""},
}
EXPORT_THEMES = {
    "default": {"name": "Default", "accent": "#00ff00", "bg": "#0a0a0a", "font": "monospace"},
    "cyberpunk": {"name": "Cyberpunk Neon", "accent": "#ff00ff", "bg": "#000000", "font": "monospace"},
    "retro_terminal": {"name": "Retro Terminal", "accent": "#33ff33", "bg": "#001800", "font": "Courier New"},
    "solarized": {"name": "Solarized Light", "accent": "#268bd2", "bg": "#fdf6e3", "font": "sans-serif"},
}

class BuildSharing:
    @staticmethod
    def overview() -> str:
        return ("<b>Build Sharing & Export</b>\n\n"
                "Export your build as a Reddit post, Hackaday.io project, "
                "GitHub repo template, or CSV BOM.\n\n"
                "Commands:\n"
                "  /share <build_id>          — sharing menu\n"
                "  /share reddit <build_id>   — Reddit post template\n"
                "  /share hackaday <build_id> — Hackaday.io template\n"
                "  /share github <build_id>   — GitHub README scaffold\n"
                "  /share bom <build_id>      — CSV BOM export\n"
                "  /share lists               — available build IDs")

    @staticmethod
    def generate(platform: str, build_id: str) -> str:
        b = SAMPLE_COMMUNITY_BUILDS.get(build_id)
        if not b:
            return f"Unknown build '{build_id}'. Available: {', '.join(SAMPLE_COMMUNITY_BUILDS.keys())}"
        t = SHARE_TEMPLATES.get(platform)
        if not t:
            return f"Unknown platform '{platform}'. Available: reddit, hackaday, github_readme"
        features_text = "\n".join(f"- {f}" for f in b.get("features", []))
        bom_text = "\n".join(f"- {b.get('sbc', '?')}, {b.get('display', '?')}, {b.get('battery', '?')}, {b.get('case', '?')}")
        notes = b.get("description", "") + "\n" + b.get("why_interesting", "")
        result = t["template"].format(
            title=b["title"], category=b.get("tags", ["cyberdeck"])[0],
            author=b.get("author", "Anonymous"), sbc=b.get("sbc", "?"),
            display=b.get("display", "?"), battery=b.get("battery", "?"),
            keyboard="Mechanical" if "keyboard" in str(b.get("features", [])).lower() else "Custom",
            case=b.get("case_style", "Custom"), features=features_text,
            notes=notes, cost=b.get("cost_tier", "?"), bom=bom_text
        )
        if t["tags"]:
            result += f"\n\n{t['tags']}"
        return f"<b>{platform.upper()} Post Template</b>\n\n<pre>{result[:3800]}</pre>"

    @staticmethod
    def bom_csv(build_id: str) -> str:
        b = SAMPLE_COMMUNITY_BUILDS.get(build_id)
        if not b:
            return f"Unknown build '{build_id}'"
        lines = ["Component,Part,Estimated Cost,Source"]
        lines.append(f"SBC,{b.get('sbc','?')},{b.get('cost_tier','?')},Community build")
        lines.append(f"Display,{b.get('display','?')},,Community build")
        lines.append(f"Battery,{b.get('battery','?')},,Community build")
        lines.append(f"Case,{b.get('case_style','?')},,Community build")
        for f in b.get("features", []):
            lines.append(f"Feature,{f},,Community build")
        return f"<b>BOM CSV: {b['title']}</b>\n\n<pre>{chr(10).join(lines)}</pre>"

    @staticmethod
    def list_builds() -> str:
        lines = ["<b>Available Builds for Sharing</b>\n"]
        for bid, b in SAMPLE_COMMUNITY_BUILDS.items():
            lines.append(f"<code>{bid}</code> — {b['title']} by {b['author']}")
        return "\n".join(lines)


# ============================================================
# v7.1 — LOCAL AI TUNER
# ============================================================
LOCAL_AI_BOARD_DATABASE = {
    "pi5_hailo8l": {"name": "Raspberry Pi 5 8GB + AI HAT+ (Hailo-8L)", "ram_gb": 8, "npu": "Hailo-8L (13 TOPS)", "npu_effort": "Low", "price": 155, "tokens_s": {"deepseek_r1_1.5b": 11, "gemma3_1b": 11, "qwen2.5_3b": 6, "llama3_8b": 2}, "notes": "Best plug-and-play NPU path. 'It just works' with hailo-all runtime. Max ~4B models comfortable."},
    "pi5_hailo8h": {"name": "Raspberry Pi 5 8GB + AI HAT+ (Hailo-8H)", "ram_gb": 8, "npu": "Hailo-8H (26 TOPS)", "npu_effort": "Low", "price": 195, "tokens_s": {"deepseek_r1_1.5b": 22, "gemma3_1b": 22, "qwen2.5_3b": 12, "llama3_8b": 4}, "notes": "Double the TOPS of the 8L. Best price/perf NPU deck, but Pi 5 USB/NVMe becomes the bottleneck at 8B."},
    "orange_pi5": {"name": "Orange Pi 5 (RK3588 8-16GB)", "ram_gb": 16, "npu": "RK3588 6 TOPs", "npu_effort": "Very High", "price": 100, "tokens_s": {"deepseek_r1_1.5b": 8, "gemma3_1b": 15, "qwen2.5_3b": 5, "llama3_8b": 1}, "notes": "Faster CPU than Pi 5, but the NPU is a trap: RKLLM model conversion is a multi-day nightmare for hobbyists. Stick to CPU+Ollama."},
    "rock5b": {"name": "Radxa Rock 5B 32GB", "ram_gb": 32, "npu": "RK3588 6 TOPs", "npu_effort": "Very High", "price": 190, "tokens_s": {"deepseek_r1_1.5b": 14, "gemma3_1b": 20, "qwen2.5_3b": 8, "llama3_8b": 2.5}, "notes": "Only SBC that runs Llama 3 8B usable (2-3 t/s) thanks to 32GB RAM via NVMe. The 8B king, slow but works."},
    "jetson_orin_nano": {"name": "NVIDIA Jetson Orin Nano 8GB", "ram_gb": 8, "npu": "Tegra (67 TOPS)", "npu_effort": "Medium", "price": 249, "tokens_s": {"deepseek_r1_1.5b": 25, "gemma3_1b": 30, "qwen2.5_3b": 14, "llama3_8b": 6}, "notes": "Best NPU ecosystem (TensorRT-LLM). Highest cost + power draw. Overkill for 1B-4B models."},
    "pi_zero2w": {"name": "Raspberry Pi Zero 2W", "ram_gb": 0.5, "npu": "None (CPU only)", "npu_effort": "None", "price": 15, "tokens_s": {"deepseek_r1_1.5b": 0.4, "gemma3_1b": 0.6, "qwen2.5_3b": 0.1, "llama3_8b": 0.05}, "notes": "TinyLLaMA 1.1B at ~1 t/s is the realistic ceiling. Good for offline dictation/handwriting, not chat."},
}
LOCAL_AI_MODEL_DATABASE = {
    "deepseek_r1_1.5b": {"name": "DeepSeek-R1 1.5B (distilled)", "params": "1.5B", "quant": "Q4_K_M", "min_ram_gb": 2, "best_for": ["pi_zero2w", "pi5_hailo8l", "orange_pi5"], "desc": "Reasoning model that fits on everything. The 2026 community default for offline decks."},
    "gemma3_1b": {"name": "Gemma3 1B", "params": "1B", "quant": "Q4_K_M", "min_ram_gb": 1, "best_for": ["pi_zero2w", "pi5_hailo8l", "orange_pi5"], "desc": "Fastest usable small model. Great for autocomplete, dictation, summarization."},
    "qwen2.5_3b": {"name": "Qwen2.5 3B", "params": "3B", "quant": "Q4_K_M", "min_ram_gb": 3, "best_for": ["pi5_hailo8l", "pi5_hailo8h", "orange_pi5", "rock5b"], "desc": "The quality/speed sweet spot for 4GB+ decks. Best all-rounder offline chat."},
    "llama3_8b": {"name": "Llama 3 8B", "params": "8B", "quant": "Q4_K_M", "min_ram_gb": 8, "best_for": ["rock5b", "jetson_orin_nano"], "desc": "Requires 32GB RAM board (Rock 5B) or NPU. Usable but slow on SBCs."},
}
BUDGET_TIERS_LOCALAI = {
    "50": {"label": "Under $50", "board": "pi_zero2w", "model": "gemma3_1b", "reason": "Smallest budget. Zero 2W + TinyLLaMA/Gemma3 1B gets offline completion working."},
    "150": {"label": "$100-150", "board": "pi5_hailo8l", "model": "deepseek_r1_1.5b", "reason": "The community sweet spot. Pi 5 + AI HAT+ runs 1.5-4B models at usable speed with zero firmware pain."},
    "200": {"label": "$150-200", "board": "pi5_hailo8h", "model": "qwen2.5_3b", "reason": "Double TOPS. Comfortably runs 3-4B models and small 8B quantized."},
    "250": {"label": "$200-250", "board": "rock5b", "model": "llama3_8b", "reason": "The only SBC route to 8B models. 32GB RAM runs Llama 3 8B at 2-3 t/s."},
}

class LocalAITuner:
    @staticmethod
    def overview() -> str:
        return ("<b>Local AI Tuner</b>\n\n"
                "Build a fully offline LLM deck. Picks the right SBC, NPU, "
                "model, and quantization for your budget.\n\n"
                "Commands:\n"
                "  /localai recommend <$budget>  — best board + model combo\n"
                "  /localai boards               — SBC/AI HAT database\n"
                "  /localai models               — offline model database\n"
                "  /localai npu                  — 'NPU tax' warning\n"
                "  /localai estimate <board> <model> — tokens/sec estimate")

    @staticmethod
    def recommend(budget: str = "150") -> str:
        tier_key = None
        for k, v in BUDGET_TIERS_LOCALAI.items():
            try:
                if int(budget) <= int(k):
                    tier_key = k
                    break
            except ValueError:
                continue
        if not tier_key:
            tier_key = "250"
        t = BUDGET_TIERS_LOCALAI[tier_key]
        board = LOCAL_AI_BOARD_DATABASE.get(t["board"], {})
        model = LOCAL_AI_MODEL_DATABASE.get(t["model"], {})
        tps = board.get("tokens_s", {}).get(t["model"], "?")
        lines = [f"<b>Local AI Recommendation: {t['label']}</b>\n"]
        lines.append(f"<b>Board:</b> {board.get('name', t['board'])} — ${board.get('price', '?')}")
        lines.append(f"  NPU: {board.get('npu', '?')} | Effort: {board.get('npu_effort', '?')}")
        lines.append(f"<b>Model:</b> {model.get('name', t['model'])} ({model.get('params', '?')}, {model.get('quant', '?')})")
        lines.append(f"  Est. speed: {tps} t/s")
        lines.append(f"  {model.get('desc', '')}")
        lines.append(f"\n<b>Why:</b> {t['reason']}")
        lines.append(f"\n  Setup: ollama pull {t['model']}  (or hailo-all for AI HAT+)")
        return "\n".join(lines)

    @staticmethod
    def boards() -> str:
        lines = ["<b>Local AI Board Database</b>\n"]
        for k, v in LOCAL_AI_BOARD_DATABASE.items():
            lines.append(f"<b>{v['name']}</b> — ${v['price']}")
            lines.append(f"  RAM: {v['ram_gb']}GB | NPU: {v['npu']} | Setup effort: {v['npu_effort']}")
            lines.append(f"  {v['notes']}\n")
        return "\n".join(lines)

    @staticmethod
    def models() -> str:
        lines = ["<b>Offline Model Database</b>\n"]
        for k, v in LOCAL_AI_MODEL_DATABASE.items():
            lines.append(f"<b>{v['name']}</b> ({v['params']}, {v['quant']})")
            lines.append(f"  Min RAM: {v['min_ram_gb']}GB | {v['desc']}\n")
        return "\n".join(lines)

    @staticmethod
    def npu() -> str:
        return ("<b>[WARNING] The NPU Tax</b>\n\n"
                "NPUs promise speed but hobbyists repeatedly hit the same wall:\n\n"
                "  1. RK3588/RKLLM conversion takes days (5-day horror stories)\n"
                "  2. Tooling is closed-source and poorly documented\n"
                "  3. Every model update = re-conversion\n\n"
                "The 2026 community verdict:\n"
                "  - Hailo (Pi 5 AI HAT+): the exception, it 'just works'\n"
                "  - Jetson: great but expensive and power hungry\n"
                "  - RK3588: SKIP the NPU, run CPU + Ollama instead\n\n"
                "Rule of thumb: if the board is under $200, CPU + quantized "
                "small model beats NPU pain.")

    @staticmethod
    def estimate(board_key: str, model_key: str) -> str:
        board = LOCAL_AI_BOARD_DATABASE.get(board_key)
        if not board:
            return f"Unknown board '{board_key}'. Available: {', '.join(LOCAL_AI_BOARD_DATABASE.keys())}"
        if model_key not in board.get("tokens_s", {}):
            return f"Unknown/unsupported model '{model_key}' on {board_key}."
        tps = board["tokens_s"][model_key]
        model = LOCAL_AI_MODEL_DATABASE.get(model_key, {})
        lines = [f"<b>Estimate: {board['name']} + {model.get('name', model_key)}</b>\n"]
        lines.append(f"  Speed: ~{tps} t/s")
        lines.append(f"  Words/min: ~{int(tps * 60 / 4)}")
        lines.append(f"  Practical uses: {('chat yes' if tps >= 8 else 'chat slow' if tps >= 4 else 'autocomplete/offline tools only')}")
        return "\n".join(lines)

# ============================================================
# v7.1 — BATTERY HOT-SWAP & SUPERCAP UPS
# ============================================================
HOTSWAP_COMPONENT_DATABASE = {
    "supercap_ups": {"name": "Supercap UPS module (e.g. 2x 2.7V 5F in series -> 5V ~1-2s hold)", "type": "UPS", "price": 15, "hold_time_s": 2, "note": "Short hold for clean shutdown, NOT for continued use."},
    "supercap_120s": {"name": "120-second supercap UPS (12V/5V, ~100F)", "type": "UPS", "price": 60, "hold_time_s": 120, "note": "The community gold standard: enough time to hot-swap a battery without shutdown."},
    "hotswap_sled": {"name": "Hot-swap battery sled (18650 or NP-F)", "type": "Battery sled", "price": 12, "note": "Spring-loaded slot so cells can be pulled while running."},
    "passthrough_charger": {"name": "Power-path / passthrough charger (e.g. LiPo SHIM or TPS2115A)", "type": "Charger", "price": 20, "note": "Runs deck off wall power while charging battery simultaneously."},
    "bms_3s": {"name": "3S BMS with balance + low-voltage cutoff", "type": "BMS", "price": 10, "note": "Required for multi-cell Li-Ion. Cuts output before cell damage."},
    "switch_over": {"name": "Auto-switching load sharing board (diode-OR)", "type": "Power path", "price": 8, "note": "Seamlessly switches between battery and external supply with no dip."},
    "pfm_boost": {"name": "Boost converter 3.3-5V (PFM for light-load efficiency)", "type": "Converter", "price": 7, "note": "Low quiescent current matters for long idle battery life."},
}
HOTSWAP_REFERENCE_BUILDS = {
    "halgrid": {"name": "HALGRID P-1", "source": "Hackster.io", "year": 2025, "battery": "26,800mAh power bank", "runtime_h": "12+", "keyboard": "Keychron K2", "features": ["Hot-swap via bank + passthrough", "12+ hour runtime", "Mechanical keyboard focus"], "lesson": "Big capacity bank + power-path charging = all-day deck."},
    "dinodeck": {"name": "DINODECK-2026", "source": "r/cyberDeck", "year": 2026, "battery": "PiSugar 3 (I2C monitored)", "runtime_h": "8+", "keyboard": "Hammond case + ortho", "features": ["I2C battery monitoring", "Charge state in software", "Supercap shutdown cushion"], "lesson": "Software battery telemetry (I2C) catches low-cell issues before a hard cut."},
}

class HotSwapPlanner:
    @staticmethod
    def overview() -> str:
        return ("<b>Battery Hot-Swap & Supercap UPS</b>\n\n"
                "Design a battery system you can swap while running, with a "
                "supercap UPS to cover the gap.\n\n"
                "Commands:\n"
                "  /hotswap design <board> <power_w> — full power-path plan\n"
                "  /hotswap parts          — component database\n"
                "  /hotswap builds         — reference builds (HALGRID, DINODECK)\n"
                "  /hotswap guide          — step-by-step wiring")

    @staticmethod
    def design(board_name: str, power_w: int = 8) -> str:
        try:
            power_w = int(power_w)
        except ValueError:
            power_w = 8
        cap_hold = "supercap_120s" if power_w >= 10 else "supercap_ups"
        cap = HOTSWAP_COMPONENT_DATABASE[cap_hold]
        lines = [f"<b>Hot-Swap Power Design: {board_name} ({power_w}W)</b>\n"]
        lines.append(f"  <b>UPS stage:</b> {cap['name']} (${cap['price']})")
        lines.append(f"    Hold: {cap['hold_time_s']}s — {cap['note']}")
        lines.append(f"  <b>Battery stage:</b> {HOTSWAP_COMPONENT_DATABASE['hotswap_sled']['name']} (${HOTSWAP_COMPONENT_DATABASE['hotswap_sled']['price']})")
        lines.append(f"  <b>Charging:</b> {HOTSWAP_COMPONENT_DATABASE['passthrough_charger']['name']} (${HOTSWAP_COMPONENT_DATABASE['passthrough_charger']['price']})")
        lines.append(f"  <b>Switching:</b> {HOTSWAP_COMPONENT_DATABASE['switch_over']['name']} (${HOTSWAP_COMPONENT_DATABASE['switch_over']['price']})")
        if power_w > 5:
            lines.append(f"  <b>BMS:</b> {HOTSWAP_COMPONENT_DATABASE['bms_3s']['name']} (${HOTSWAP_COMPONENT_DATABASE['bms_3s']['price']})")
        if power_w <= 5:
            lines.append(f"  <b>Converter:</b> {HOTSWAP_COMPONENT_DATABASE['pfm_boost']['name']} (${HOTSWAP_COMPONENT_DATABASE['pfm_boost']['price']})")
        total = cap["price"] + HOTSWAP_COMPONENT_DATABASE["hotswap_sled"]["price"] + HOTSWAP_COMPONENT_DATABASE["passthrough_charger"]["price"] + HOTSWAP_COMPONENT_DATABASE["switch_over"]["price"]
        if power_w > 5:
            total += HOTSWAP_COMPONENT_DATABASE["bms_3s"]["price"]
        if power_w <= 5:
            total += HOTSWAP_COMPONENT_DATABASE["pfm_boost"]["price"]
        lines.append(f"\n  <b>Estimated extra cost:</b> ~${total}")
        lines.append(f"\n  Order of power flow: Battery -> Sled -> Diode-OR -> UPS caps -> Deck")
        lines.append(f"  Wall charger -> Passthrough -> Battery + Deck simultaneously")
        return "\n".join(lines)

    @staticmethod
    def parts() -> str:
        lines = ["<b>Hot-Swap / UPS Component Database</b>\n"]
        for k, v in HOTSWAP_COMPONENT_DATABASE.items():
            lines.append(f"<b>{v['name']}</b> — ${v['price']}")
            if v.get("hold_time_s"):
                lines.append(f"  Hold time: {v['hold_time_s']}s")
            lines.append(f"  {v['note']}\n")
        return "\n".join(lines)

    @staticmethod
    def builds() -> str:
        lines = ["<b>Reference Hot-Swap Builds</b>\n"]
        for k, v in HOTSWAP_REFERENCE_BUILDS.items():
            lines.append(f"<b>{v['name']}</b> ({v['source']}, {v['year']})")
            lines.append(f"  Battery: {v['battery']} | Runtime: {v['runtime_h']}h | Keyboard: {v['keyboard']}")
            lines.append(f"  {v['lesson']}\n")
        return "\n".join(lines)

    @staticmethod
    def guide() -> str:
        return ("<b>Hot-Swap Wiring Guide</b>\n\n"
                "1. <b>Power path:</b> Wire deck positive rail through a diode-OR "
                "switch-over board. Battery and wall charger both feed in.\n"
                "2. <b>Passthrough charger:</b> Connect charger input to wall/USB-C, "
                "its output to battery AND to the switch-over board. Deck runs off "
                "wall power while the battery charges.\n"
                "3. <b>Supercap UPS:</b> Put caps on the deck-side rail. When the "
                "battery is pulled, caps hold 2-120s for a clean shutdown.\n"
                "4. <b>Software:</b> run a daemon that reads battery state (I2C/GPIO) "
                "and triggers safe shutdown when the UPS signals power loss.\n"
                "5. <b>Test:</b> pull the battery while running `stress` and confirm "
                "no brownout. Never hot-pull without the UPS stage.")

# ============================================================
# v7.1 — ORTHOLINEAR & SPLIT KEYBOARD DB
# ============================================================
ORTHO_KEYBOARD_DATABASE = {
    "corne": {"name": "Corne (CRKBD)", "layout": "3x6+3 ortholinear split", "keys": 42, "switch": "MX/Choc hotswap", "price": 90, "firmware": ["QMK", "ZMK", "VIAL"], "best_for": ["writerdeck", "pentest"], "pros": ["Legendary community", "ZMK wireless via nice!nano", "Tons of build logs"]},
    "helix": {"name": "Helix", "layout": "5x6 ortholinear split", "keys": 60, "switch": "MX hotswap", "price": 110, "firmware": ["QMK", "ZMK", "VIAL"], "best_for": ["general", "writerdeck"], "pros": ["6x5 includes number row", "OLED per half", "Soldered or hotswap options"]},
    "lily58": {"name": "Lily58", "layout": "4x6+2 ortholinear split", "keys": 58, "switch": "MX/Choc hotswap", "price": 100, "firmware": ["QMK", "ZMK", "VIAL"], "best_for": ["general", "coding"], "pros": ["The default first split build", "Great ergonomics", "Pinkys rest on thumb clusters"]},
    "ferris_sweep": {"name": "Ferris Sweep", "layout": "3x5+2 low-profile split", "keys": 34, "switch": "Choc (solder)", "price": 70, "firmware": ["ZMK", "QMK"], "best_for": ["writerdeck", "pentest", "survival"], "pros": ["Feather-light, fits in Altoids tin", "Choc switches = ultra slim", "Wireless via nice!nano"]},
    "sofle": {"name": "Sofle", "layout": "4x6+4 ortholinear split", "keys": 56, "switch": "MX hotswap", "price": 105, "firmware": ["QMK", "VIAL"], "best_for": ["coding", "general"], "pros": ["Encoders + OLED", "More thumb keys than Lily58", "Great for macro-heavy use"]},
    "cantor": {"name": "Cantor", "layout": "3x5+3 low-profile split", "keys": 36, "switch": "Choc (solder)", "price": 75, "firmware": ["ZMK", "QMK"], "best_for": ["writerdeck", "pentest"], "pros": ["Cheap, few parts", "good for hand-wiring practice"]},
    "planck": {"name": "Planck", "layout": "12x4 ortholinear (non-split)", "keys": 48, "switch": "MX/Choc hotswap", "price": 130, "firmware": ["QMK", "VIAL"], "best_for": ["writerdeck", "general"], "pros": ["The original ortho", "Drop.com kits", "Compact single-board"]},
    "preonic": {"name": "Preonic", "layout": "12x5 ortholinear (non-split)", "keys": 60, "switch": "MX/Choc hotswap", "price": 140, "firmware": ["QMK", "VIAL"], "best_for": ["coding", "general"], "pros": ["Number row included", "Great first ortho"]},
    "air40": {"name": "Air40", "layout": "40% ortholinear (non-split)", "keys": 40, "switch": "Choc hotswap", "price": 80, "firmware": ["QMK", "VIAL"], "best_for": ["writerdeck"], "pros": ["Ultra-low profile", "Writerdeck standard"]},
    "gherkin": {"name": "Gherkin 30%", "layout": "5x4 ortholinear (non-split)", "keys": 30, "switch": "MX (solder)", "price": 40, "firmware": ["QMK"], "best_for": ["survival", "minimalist"], "pros": ["Tiny, fits Altoids tin builds", "Great for ultraminimal cyberdecks"]},
    "iris": {"name": "Iris", "layout": "4x6+2 staggered split (columnar)", "keys": 54, "switch": "MX/Choc hotswap", "price": 115, "firmware": ["QMK", "VIAL"], "best_for": ["coding", "general"], "pros": ["Pre-soldered hotswap kits", "Optional per-key RGB", "2x5 thumb clusters"]},
    "kyria": {"name": "Kyria", "layout": "3x6+3 ortholinear split", "keys": 46, "switch": "MX/Choc hotswap", "price": 120, "firmware": ["QMK", "ZMK"], "best_for": ["writerdeck", "pentest"], "pros": ["4 thumb keys per side", "Encoder support", "Aggressive stagger"]},
    "chocofi": {"name": "Chocofi", "layout": "3x5+2 low-profile split", "keys": 34, "switch": "Choc hotswap", "price": 95, "firmware": ["ZMK", "QMK"], "best_for": ["writerdeck", "pentest"], "pros": ["Hotswap Chocs", "nice!nano friendly", "Slim enough for a clam case"]},
    "redox": {"name": "Redox", "layout": "5x7+2 ortholinear split", "keys": 76, "switch": "MX hotswap", "price": 125, "firmware": ["QMK", "VIAL"], "best_for": ["general", "coding"], "pros": ["Bigger board with num row", "OLED + rotary option", "For anyone missing keys"]},
    "voyager": {"name": "ZSA Voyager", "layout": "3x5+2 low-profile split", "keys": 34, "switch": "Choc hotswap", "price": 350, "firmware": ["ZSA (QMK)", "VIA"], "best_for": ["coding", "general"], "pros": ["Built like a tank", "Pre-assembled & warrantied", "Travel case included"], "cons": ["Pricey", "Proprietary-ish tooling"]},
    "pteron36": {"name": "Pteron36", "layout": "3x6+3 ortholinear split", "keys": 36, "switch": "MX/Choc hotswap", "price": 85, "firmware": ["QMK", "ZMK", "VIAL"], "best_for": ["writerdeck", "pentest"], "pros": ["Open-source & free to fab", "Wide community forks", "Can hand-wire in a weekend"]},
}
ORTHO_FIRMWARE_GUIDE = {
    "qmk": {"name": "QMK", "language": "C", "best_for": "Anything, wired", "url": "https://docs.qmk.fm", "note": "Most mature. Every board has a firmware folder."},
    "via": {"name": "VIA (QMK add-on)", "language": "GUI", "best_for": "Live remapping without flashing", "url": "https://usevia.app", "note": "Plug in, remap keys in browser. Killer for newbies."},
    "vial": {"name": "VIAL (QMK fork)", "language": "GUI + macros", "best_for": "Macros + tap dance without reflashing", "url": "https://get.vial.today", "note": "Macro recording at runtime. Community favorite."},
    "zmk": {"name": "ZMK", "language": "YAML + DTS", "best_for": "Wireless (nice!nano, BLE)", "url": "https://zmk.dev", "note": "Wireless-first. Battery-friendly. No C needed."},
}

class OrthoAdvisor:
    @staticmethod
    def overview() -> str:
        return ("<b>Ortholinear & Split Keyboard DB</b>\n\n"
                "Match the perfect ortho/split keyboard to your build: Corne, "
                "Helix, Lily58, Ferris Sweep, Sofle, Planck and more.\n\n"
                "Commands:\n"
                "  /ortho                 — full keyboard list\n"
                "  /ortho recommend <build_type> — writerdeck|coding|pentest|survival|general\n"
                "  /ortho firmware <kb>   — firmware guide for a keyboard\n"
                "  /ortho wiring          — hand-wiring guide\n"
                "  /ortho <keyboard>      — detail on one keyboard")

    @staticmethod
    def list_all() -> str:
        lines = ["<b>Ortho / Split Keyboard Database</b>\n"]
        for k, v in ORTHO_KEYBOARD_DATABASE.items():
            lines.append(f"<b>{v['name']}</b> ({v['layout']}) — ${v['price']}")
            lines.append(f"  Keys: {v['keys']} | Switch: {v['switch']}")
            lines.append(f"  Firmware: {', '.join(v['firmware'])}")
            lines.append(f"  Pros: {', '.join(v['pros'][:2])}\n")
        return "\n".join(lines)

    @staticmethod
    def recommend(build_type: str = "general") -> str:
        matches = [v for v in ORTHO_KEYBOARD_DATABASE.values() if build_type in v.get("best_for", [])]
        if not matches:
            return f"Unknown build type '{build_type}'. Try: writerdeck, coding, pentest, survival, general"
        matches.sort(key=lambda x: x["price"])
        lines = [f"<b>Keyboard Recommendations: {build_type}</b>\n"]
        for v in matches[:3]:
            lines.append(f"<b>{v['name']}</b> — ${v['price']}")
            lines.append(f"  {v['layout']} | {v['keys']} keys | {v['switch']}")
            lines.append(f"  Pros: {', '.join(v['pros'][:2])}\n")
        return "\n".join(lines)

    @staticmethod
    def detail(keyboard: str) -> str:
        for k, v in ORTHO_KEYBOARD_DATABASE.items():
            if keyboard.lower() in k or keyboard.lower() in v["name"].lower():
                lines = [f"<b>{v['name']}</b>\n"]
                lines.append(f"  Layout: {v['layout']}")
                lines.append(f"  Keys: {v['keys']} | Switch: {v['switch']} | Price: ${v['price']}")
                lines.append(f"  Firmware: {', '.join(v['firmware'])}")
                lines.append(f"  Best for: {', '.join(v['best_for'])}")
                for p in v['pros']:
                    lines.append(f"  + {p}")
                return "\n".join(lines)
        return f"Unknown keyboard. Available: {', '.join(ORTHO_KEYBOARD_DATABASE.keys())}"

    @staticmethod
    def firmware(keyboard: str = "") -> str:
        kb = None
        if keyboard:
            for k, v in ORTHO_KEYBOARD_DATABASE.items():
                if keyboard.lower() in k or keyboard.lower() in v["name"].lower():
                    kb = v
                    break
        if kb:
            fw_names = kb["firmware"]
            lines = [f"<b>Firmware for {kb['name']}</b>\n"]
            for name in fw_names:
                f = ORTHO_FIRMWARE_GUIDE.get(name.lower())
                if f:
                    lines.append(f"<b>{f['name']}</b> — {f['best_for']}")
                    lines.append(f"  {f['note']}\n")
            return "\n".join(lines)
        lines = ["<b>Firmware Guide</b>\n"]
        for k, v in ORTHO_FIRMWARE_GUIDE.items():
            lines.append(f"<b>{v['name']}</b> — {v['best_for']}")
            lines.append(f"  {v['note']}\n")
        return "\n".join(lines)

    @staticmethod
    def wiring() -> str:
        return ("<b>Hand-Wiring an Ortho Keyboard</b>\n\n"
                "1. <b>Matrix wiring:</b> Every switch gets a column and row wire. "
                "Columns = diode -> pin, rows = plain wire -> pin.\n"
                "2. <b>Diodes:</b> One 1N4148 per switch, cathode (striped side) "
                "toward the column wire.\n"
                "3. <b>Controller:</b> Use a Pro Micro (ATmega32U4) or RP2040. "
                "Flash QMK/VIAL with your layout.\n"
                "4. <b>Miryoku layout:</b> The community-standard 36-key home-row "
                "layout. Supports layers for numbers, symbols, media.\n"
                "5. <b>Wireless:</b> Swap to nice!nano + ZMK for BLE and weeks of "
                "battery on a 110mAh LiPo.\n\n"
                "Beginner tip: start with a Cantor or Ferris Sweep PCB — fewer parts "
                "and it doubles as the hand-wiring practice board.")

# ============================================================
# v7.1 — OFFLINE SURVIVAL STACK
# ============================================================
OFFGRID_STACK_COMPONENTS = {
    "dtn": {"name": "Delay-Tolerant Networking (DTN)", "type": "Comms", "price": 0, "stack": "bundle protocol / TCPCL", "note": "Store-and-forward messaging between peers with no always-on network. Sync messages when two decks meet."},
    "kiwix_rag": {"name": "Kiwix ZIM + RAG index", "type": "Knowledge", "price": 0, "stack": "Kiwix + local embeddings", "note": "Offline Wikipedia/books with semantic search. Pair with a 1B embedding model for offline RAG."},
    "offline_maps": {"name": "Offline maps (OSM + MBTiles)", "type": "Navigation", "price": 0, "stack": "Organic Maps / osmand", "note": "Pre-download region tiles. Vector maps for the whole country are ~1-2GB."},
    "p2p_models": {"name": "P2P model sharing", "type": "AI", "price": 0, "stack": "LAN mesh + model registry", "note": "Share GGUF models peer-to-peer so one download populates the whole group."},
    "mesh_beacon": {"name": "Mesh beacon (mDNS/UDP discovery)", "type": "Comms", "price": 5, "stack": "mDNS + UDP broadcast", "note": "Decks advertise themselves on the local mesh. Discovery handshake then hand off to DTN or TCP."},
    "gps_module": {"name": "GPS/GNSS module", "type": "Navigation", "price": 15, "stack": "u-blox NEO-8M", "note": "Time + position anchors for messages, adds rescue-grade location to every sync."},
    "offgrid_nas": {"name": "Off-grid NAS", "type": "Storage", "price": 0, "stack": "Syncthing (LAN-only)", "note": "Sync notes, maps, and models between decks and a hub. Works fully offline."},
}
OFFGRID_REFERENCE_BUILD = {
    "name": "CyberDeck DTN / Offline Platform",
    "repo": "github.com/sarogamedev/CyberDeck",
    "stars": "113+",
    "stack": ["DTN (delay-tolerant sync)", "Kiwix ZIM + RAG", "Offline maps", "P2P model sharing", "mDNS/UDP beacon"],
    "lesson": "The reference pattern: combine mesh discovery, store-and-forward, and offline knowledge into one 'survival platform' rather than separate toys.",
}

class OffgridStackPlanner:
    @staticmethod
    def overview() -> str:
        return ("<b>Offline Survival Stack</b>\n\n"
                "Plan a full offline platform: DTN sync, Kiwix RAG, offline maps, "
                "and P2P model sharing. The sarogamedev pattern.\n\n"
                "Commands:\n"
                "  /offgridstack plan <budget> — full stack plan\n"
                "  /offgridstack components     — component database\n"
                "  /offgridstack dtn            — DTN architecture\n"
                "  /offgridstack reference      — reference build")

    @staticmethod
    def plan(budget: str = "200") -> str:
        try:
            budget_n = int(budget)
        except ValueError:
            budget_n = 200
        board = "Raspberry Pi 5 8GB" if budget_n >= 150 else "Raspberry Pi 4 4GB"
        stack = "full (DTN + Kiwix RAG + maps + P2P)" if budget_n >= 250 else "core (Kiwix + maps + DTN)"
        lines = [f"<b>Offline Survival Stack Plan (budget ${budget_n})</b>\n"]
        lines.append(f"  <b>Core deck:</b> {board} + NVMe/SD for knowledge")
        lines.append(f"  <b>Scope:</b> {stack}")
        lines.append("")
        for k, v in OFFGRID_STACK_COMPONENTS.items():
            lines.append(f"<b>{v['name']}</b> — {v['type']}")
            lines.append(f"  {v['note']}")
            lines.append(f"  Stack: {v['stack']}\n")
        lines.append(f"  <b>Total software cost:</b> ~$0 (all free/open source)")
        lines.append(f"  Hardware add-ons: GPS ${OFFGRID_STACK_COMPONENTS['gps_module']['price']}, beacon ~$5")
        return "\n".join(lines)

    @staticmethod
    def components() -> str:
        lines = ["<b>Offgrid Stack Components</b>\n"]
        for k, v in OFFGRID_STACK_COMPONENTS.items():
            lines.append(f"<b>{v['name']}</b> — {v['type']} (${v['price']})")
            lines.append(f"  {v['note']}\n")
        return "\n".join(lines)

    @staticmethod
    def dtn() -> str:
        return ("<b>Delay-Tolerant Networking (DTN)</b>\n\n"
                "How offline sync works when nobody is online:\n\n"
                "  1. <b>Bundle protocol</b>: messages are wrapped in bundles, not "
                "streams. Each bundle survives disconnects.\n"
                "  2. <b>Store-and-forward</b>: every deck is a router. When two decks "
                "meet on mesh, bundles exchange automatically.\n"
                "  3. <b>Discovery</b>: mDNS/UDP beacon advertises presence. No "
                "central server needed.\n"
                "  4. <b>DTN transport</b>: TCPCL (TCP Convergence Layer) carries "
                "bundles over the mesh once linked.\n\n"
                "Pattern: Beacon -> handshake -> DTN bundle sync -> done. Repeat at "
                "every meeting. Over days a mesh community converges on full sync.\n\n"
                "Implementation: pyDTN or IBR-DTN on the deck, Syncthing (LAN-only "
                "mode) for file/map/model sync.")

    @staticmethod
    def reference() -> str:
        r = OFFGRID_REFERENCE_BUILD
        lines = [f"<b>Reference Build: {r['name']}</b>\n"]
        lines.append(f"  Repo: {r['repo']} ({r['stars']} stars)")
        lines.append(f"  Stack:")
        for s in r["stack"]:
            lines.append(f"    - {s}")
        lines.append(f"\n  {r['lesson']}")
        return "\n".join(lines)

# ============================================================
# v7.1 — COMMUNITY FEATURE BOARD
# ============================================================
COMMUNITY_FEATURE_DATABASE = {
    "multilayer_macros": {"title": "Multi-layer macro support", "votes": 87, "source": "cyberdeck.ing feature board", "mod": "Software + key remap", "fit": ["coding", "pentest", "general"], "effort": "Low", "desc": "Per-app macro layers so one physical button does different things per app/context."},
    "rear_camera": {"title": "Rear / rotating camera", "votes": 64, "source": "cyberdeck.ing feature board", "mod": "USB camera + swivel mount", "fit": ["hacking", "general"], "effort": "Medium", "desc": "Documentation camera, QR capture, or telepresence without a laptop."},
    "speech_to_text": {"title": "Offline speech-to-text", "votes": 52, "source": "cyberdeck.ing feature board", "mod": "Whisper.cpp (1B/3B)", "fit": ["writerdeck", "general"], "effort": "Medium", "desc": "Dictation on deck using local Whisper models. Works offline on Pi 5+."},
    "volume_knob": {"title": "Physical volume / encoder knob", "votes": 40, "source": "cyberdeck.ing feature board", "mod": "Rotary encoder + OLED", "fit": ["media", "gaming", "general"], "effort": "Low", "desc": "Tactile volume and brightness control via EC11 encoder."},
    "slide_out_keyboard": {"title": "Slide-out keyboard", "votes": 78, "source": "r/cyberDeck wishlist", "mod": "NATO rail + slider tray", "fit": ["general", "writerdeck"], "effort": "High", "desc": "Keyboard stows under deck and slides out on rails. The top Reddit ask."},
    "glasses_display": {"title": "Glasses / AR display", "votes": 45, "source": "r/cyberDeck wishlist", "mod": "HDMI micro-OLED glasses", "fit": ["survival", "pentest", "writerdeck"], "effort": "Low", "desc": "Head-mounted display frees hands. HDMI-in glasses like Xreal/Rokid."},
    "projector_attach": {"title": "Articulated projector mount", "votes": 33, "source": "r/cyberDeck wishlist", "mod": "Mini projector + arm", "fit": ["media", "general"], "effort": "Medium", "desc": "Share screen on any wall. Seen on maximalist builds like M.A.S.K."},
    "extra_usb": {"title": "More USB ports / hub", "votes": 71, "source": "r/cyberDeck wishlist", "mod": "USB hub + power switch", "fit": ["hacking", "coding", "general"], "effort": "Low", "desc": "Persistent complaint: decks never have enough USB for SDR + keyboard + storage."},
}

class CommunityFeatureBoard:
    @staticmethod
    def overview() -> str:
        return ("<b>Community Feature Board</b>\n\n"
                "Live mod ideas voted by the cyberdeck community "
                "(cyberdeck.ing + r/cyberDeck).\n\n"
                "Commands:\n"
                "  /features                — all requested mods, top votes first\n"
                "  /features recommend <type> — best mods for your build type\n"
                "  /features top            — top 3 by votes")

    @staticmethod
    def list_all() -> str:
        ordered = sorted(COMMUNITY_FEATURE_DATABASE.values(), key=lambda x: -x["votes"])
        lines = ["<b>Community Feature Board</b>\n"]
        for v in ordered:
            lines.append(f"<b>{v['title']}</b> — {v['votes']} votes ({v['source']})")
            lines.append(f"  Mod: {v['mod']} | Effort: {v['effort']}")
            lines.append(f"  {v['desc']}\n")
        return "\n".join(lines)

    @staticmethod
    def top() -> str:
        ordered = sorted(COMMUNITY_FEATURE_DATABASE.values(), key=lambda x: -x["votes"])[:3]
        lines = ["<b>Top Community Requests</b>\n"]
        for i, v in enumerate(ordered, 1):
            lines.append(f"{i}. <b>{v['title']}</b> — {v['votes']} votes")
            lines.append(f"   {v['desc']}\n")
        return "\n".join(lines)

    @staticmethod
    def recommend(build_type: str = "general") -> str:
        matches = [v for v in COMMUNITY_FEATURE_DATABASE.values() if build_type in v.get("fit", [])]
        if not matches:
            return f"Unknown build type '{build_type}'. Try: writerdeck, coding, pentest, general, hacking, media, gaming, survival"
        matches.sort(key=lambda x: (-x["votes"], x["effort"]))
        lines = [f"<b>Recommended Mods: {build_type}</b>\n"]
        for v in matches:
            lines.append(f"<b>{v['title']}</b> — {v['votes']} votes | Effort: {v['effort']}")
            lines.append(f"  {v['mod']}")
            lines.append(f"  {v['desc']}\n")
        return "\n".join(lines)

# ============================================================
# v7.1 — MAXIMALIST vs MINIMALIST CHARACTER BUILDER
# ============================================================
CHARACTER_TEMPLATES = {
    "minimal": {
        "name": "Ultra-Minimal", "persona": "The Ghost Deck",
        "sbc": "Raspberry Pi Zero 2W", "display": "Sharp Memory Display 2.7\" (400x240, 0.05W)",
        "keyboard": "Gherkin 30% or Ferris Sweep", "battery": "4000mAh LiPo", "case": "Altoids tin",
        "software": "DietPi CLI + tmux", "weight_g": 120, "cost": "~$80-110", "runtime_h": "10-14",
        "features": ["Fits in a pocket", "All-day battery", "Boots to terminal in 8s", "No fan, no noise", "Solar micro-panel optional"],
        "philosophy": "Less hardware = less to fail. The deck you actually carry is the deck you use."},
    "maximal": {
        "name": "Maximalist Battle Deck", "persona": "The M.A.S.K. Rig",
        "sbc": "Orange Pi 5 / Pi 5 8GB", "display": "7\" touch + secondary oscilloscope panel",
        "keyboard": "Keychron K2 + macro pad", "battery": "NP-F970 dual sled", "case": "Lunchbox / Pelican 1150",
        "software": "Kali or Ubuntu MATE + SDR + HackRF", "weight_g": 2500, "cost": "~$700-1100", "runtime_h": "6-10",
        "features": ["SDR + HackRF antenna farm", "Articulated projector", "Built-in oscilloscope display", "Hardware kill switches", "Folding solar panel"],
        "philosophy": "A complete field station. Every panel does something. Inspired by the M.A.S.K. builds of 2026."},
    "field": {
        "name": "Field Survival Deck", "persona": "The Nomad Rig",
        "sbc": "Raspberry Pi 5 4GB", "display": "5\" reflective LCD (sunlight readable)",
        "keyboard": "Corne split (wireless)", "battery": "PiSugar 3 + solar 20W", "case": "OD green 3D printed",
        "software": "Offgrid stack (Kiwix + DTN + maps)", "weight_g": 900, "cost": "~$300-450", "runtime_h": "8-12",
        "features": ["Kiwix offline knowledge", "DTN mesh sync", "Offline maps + GPS", "IP54 water resistant", "Rugged connectors"],
        "philosophy": "Built for days away from power and internet. Knowledge + comms in one unit."},
}

class CharacterBuilder:
    @staticmethod
    def overview() -> str:
        return ("<b>Maximalist vs Minimalist Character Builder</b>\n\n"
                "Generate a themed build along the 2026 community spectrum.\n\n"
                "Commands:\n"
                "  /character               — list available characters\n"
                "  /character <minimal|maximal|field> — full build plan\n"
                "  /character compare       — minimal vs maximal side-by-side")

    @staticmethod
    def list_styles() -> str:
        lines = ["<b>Available Character Builds</b>\n"]
        for k, v in CHARACTER_TEMPLATES.items():
            lines.append(f"<b>{v['name']}</b> (<code>{k}</code>) — {v['persona']}")
            lines.append(f"  Cost: {v['cost']} | Weight: {v['weight_g']}g | Runtime: {v['runtime_h']}h\n")
        return "\n".join(lines)

    @staticmethod
    def build(style: str) -> str:
        t = CHARACTER_TEMPLATES.get(style)
        if not t:
            return f"Unknown character '{style}'. Available: {', '.join(CHARACTER_TEMPLATES.keys())}"
        lines = [f"<b>{t['name']}: {t['persona']}</b>\n"]
        lines.append(f"  <b>SBC:</b> {t['sbc']}")
        lines.append(f"  <b>Display:</b> {t['display']}")
        lines.append(f"  <b>Keyboard:</b> {t['keyboard']}")
        lines.append(f"  <b>Battery:</b> {t['battery']}")
        lines.append(f"  <b>Case:</b> {t['case']}")
        lines.append(f"  <b>Software:</b> {t['software']}")
        lines.append(f"")
        lines.append(f"  <b>Specs:</b> {t['weight_g']}g | {t['cost']} | {t['runtime_h']}h runtime")
        lines.append(f"\n  <b>Features:</b>")
        for f in t['features']:
            lines.append(f"    + {f}")
        lines.append(f"\n  <b>Philosophy:</b> {t['philosophy']}")
        return "\n".join(lines)

    @staticmethod
    def compare() -> str:
        a = CHARACTER_TEMPLATES["minimal"]
        b = CHARACTER_TEMPLATES["maximal"]
        lines = [f"<b>Minimal vs Maximal</b>\n"]
        lines.append(f"{'Metric':24} | {'Minimal':20} | {'Maximal':20}")
        rows = [
            ("Cost", a["cost"], b["cost"]),
            ("Weight", f"{a['weight_g']}g", f"{b['weight_g']}g"),
            ("Runtime", f"{a['runtime_h']}h", f"{b['runtime_h']}h"),
            ("SBC", a["sbc"][:18], b["sbc"][:18]),
            ("Display", a["display"][:18], b["display"][:18]),
            ("Case", a["case"][:18], b["case"][:18]),
        ]
        for name, av, bv in rows:
            lines.append(f"{name:24} | {av:20} | {bv:20}")
        lines.append(f"\n  Minimal: {a['philosophy']}")
        lines.append(f"\n  Maximal: {b['philosophy']}")
        lines.append(f"\n  Community verdict: carry a minimal deck daily, build a maximal "
                     f"deck for events. Both are valid 2026 paths.")
        return "\n".join(lines)

# ============================================================
# v7.1 — SCAVENGE BUILD SOURCING
# ============================================================
SCAVENGE_SOURCES = {
    "thrift": {"name": "Thrift stores (Goodwill, Value Village)", "gold": "Mechanical keyboards $3-10", "bargains": ["Keychron/K8, Corsair mechs", "Old USB hubs", "Laptop batteries", "Bluetooth dongles", "Cheap monitors"], "tip": "Check the keyboard bin weekly — mechs show up constantly. Test with a phone before buying."},
    "ewaste": {"name": "E-waste recycling centers", "gold": "Industrial laptops, docking stations", "bargains": ["ThinkPads (motherboard donor)", "Dell docks with 90W PSU", "SSD/NVMe pulls", "CCTV/panel PCs"], "tip": "Ask politely for 'damaged goods' — most centers sell by the pound. Sand and retest SSDs."},
    "dollar": {"name": "Dollar / 99c stores", "gold": "Enclosures, cables, adapters", "bargains": ["Tin boxes and organizers", "USB cables and adapters", "Small speakers", "LED strip lights"], "tip": "Cheap USB cables are often junk for data — test each one for charging AND data."},
    "ebay": {"name": "eBay 'for parts' listings", "gold": "Broken flagship gear, cheap SBCs", "bargains": ["Dead E-readers (screens!)", "Board pulls (Pi 4/5)", "Old phones (screens)", "Mechanical keyboard lots"], "tip": "Search '[device] for parts not working'. 50-80% off retail for fixable gear."},
    "refurb": {"name": "Refurbished IT resellers", "gold": "Enterprise laptops, docks", "bargains": ["Latitude/ThinkPad docks", "Old tablet panels", "Fiber NICs and SBC-adjacent", "UPS batteries"], "tip": "Enterprise lease-returns are the cheapest source of quality batteries + screens."},
}
SCAVENGE_BUILD_PLAN = {
    "bootstrap": {"name": "Scavenge Bootstrap ($0-50)", "parts": ["Thrift mech keyboard ($5)", "E-waste ThinkPad board ($20)", "Tin case from dollar store ($2)", "Scrap cables + PSU", "Old phone screen"], "notes": "Builds a basic deck almost entirely from salvaged parts. 18650 cells pulled from old laptop batteries (test each!)."},
    "mech_focus": {"name": "Mech Keyboard Focus ($30-80)", "parts": ["2-3 thrift mechs to harvest switches ($10-20)", "Ortho PCB or hand-wire plate ($20)", "Diodes + wire ($5)", "Pro Micro controller ($5)"], "notes": "Harvest Cherry/Gateron switches from junk boards, hand-wire into an ortho layout. Zero custom parts needed."},
    "media_screen": {"name": "Screen Donor ($20-40)", "parts": ["Old phone or tablet ($15-25)", "HDMI driver board (~$15)", "USB touch controller", "Tin/case frame"], "notes": "The classic hack: a dead phone screen + driver board becomes a $25 1080p display."},
}

class ScavengePlanner:
    @staticmethod
    def overview() -> str:
        return ("<b>Scavenge Build Sourcing</b>\n\n"
                "Build a cyberdeck from thrift stores, e-waste, and dollar stores. "
                "The budget-builders' bible.\n\n"
                "Commands:\n"
                "  /scavenge                — scavenger hunt plans\n"
                "  /scavenge sources        — sourcing locations\n"
                "  /scavenge tips           — scavenging rules\n"
                "  /scavenge <plan>         — bootstrap|mech_focus|media_screen")

    @staticmethod
    def plans() -> str:
        lines = ["<b>Scavenge Build Plans</b>\n"]
        for k, v in SCAVENGE_BUILD_PLAN.items():
            lines.append(f"<b>{v['name']}</b> ({k})")
            lines.append(f"  Parts:")
            for p in v["parts"]:
                lines.append(f"    - {p}")
            lines.append(f"  Notes: {v['notes']}\n")
        return "\n".join(lines)

    @staticmethod
    def sources() -> str:
        lines = ["<b>Scavenging Sources</b>\n"]
        for k, v in SCAVENGE_SOURCES.items():
            lines.append(f"<b>{v['name']}</b>")
            lines.append(f"  Gold: {v['gold']}")
            lines.append(f"  Bargains: {', '.join(v['bargains'][:3])}")
            lines.append(f"  Tip: {v['tip']}\n")
        return "\n".join(lines)

    @staticmethod
    def tips() -> str:
        return ("<b>Scavenging Rules</b>\n\n"
                "1. <b>Test before buying</b> — bring a USB-C tester and charger.\n"
                "2. <b>18650 safety</b> — only pull cells that hold voltage after "
                "charging; recycle the rest. Never puncture.\n"
                "3. <b>Screens are gold</b> — dead phones/tablets/e-readers donate "
                "the most valuable part of a deck.\n"
                "4. <b>Data cables need testing</b> — dollar-store cables often "
                "charge but don't carry data.\n"
                "5. <b>Donors over parts</b> — one broken ThinkPad gives you board, "
                "keyboard, screen, battery, and charger.\n"
                "6. <b>Ask the staff</b> — e-waste centers usually have a 'non-sale' "
                "pile. Politely ask and you'll get boards for free.\n"
                "7. <b>Total cost target</b> — a good scavenge build should stay "
                "under $100. Beyond that, buy new.")

    @staticmethod
    def plan(plan_key: str) -> str:
        v = SCAVENGE_BUILD_PLAN.get(plan_key)
        if not v:
            return f"Unknown plan '{plan_key}'. Available: {', '.join(SCAVENGE_BUILD_PLAN.keys())}"
        lines = [f"<b>{v['name']}</b>\n"]
        lines.append("  Parts:")
        for p in v["parts"]:
            lines.append(f"    - {p}")
        lines.append(f"\n  Notes: {v['notes']}")
        return "\n".join(lines)

# ============================================================
# v7.1 — 2026 HARDWARE RADAR
# ============================================================
NEW_HARDWARE_2026 = {
    "pi500_plus": {"name": "Raspberry Pi 500+", "year": 2026, "type": "Keyboard computer", "price": 100, "ram_gb": 8, "arch": "ARM (BCM2712)", "highlight": "The Pi-in-a-keyboard returns with Pi 5 silicon. Instant cyberdeck keyboard chassis.", "best_for": ["writerdeck", "general"], "gpu_ai": "CPU-only (use small models)"},
    "rock5b_32": {"name": "Radxa Rock 5B / 5 ITX 32GB", "year": 2026, "type": "SBC", "price": 190, "ram_gb": 32, "arch": "ARM (RK3588)", "highlight": "32GB RAM = the only SBC that runs 8B LLMs usefully. ITX version fits in a full deck.", "best_for": ["local_ai", "coding"], "gpu_ai": "8B via CPU, NPU is a trap"},
    "ai_hat_plus": {"name": "AI HAT+ (Hailo-8L / 8H)", "year": 2026, "type": "NPU add-on", "price": 70, "ram_gb": 0, "arch": "NPU add-on for Pi 5", "highlight": "13/26 TOPS. The 'it just works' NPU path for offline LLMs on a Pi 5.", "best_for": ["local_ai", "edge_ai"], "gpu_ai": "1-4B models at 10-22 t/s"},
    "lichee_console": {"name": "SiSpeed Lichee Console 4A", "year": 2026, "type": "RISC-V laptop", "price": 395, "ram_gb": 16, "arch": "RISC-V (TH1520)", "highlight": "The 2026 RISC-V laptop/console. Open-hardware, 7-inch screen. A statement cyberdeck base.", "best_for": ["writerdeck", "general"], "gpu_ai": "Small models only, new architecture"},
    "x86_12w": {"name": "x86 12W i5-class boards", "year": 2026, "type": "Mini ITX / thin mini", "price": 150, "ram_gb": 16, "arch": "x86", "highlight": "Full x86 compatibility (Windows/Kali/drivers) at 12W idle-ish draw. Bigger than SBCs.", "best_for": ["hacking", "coding", "general"], "gpu_ai": "8B via CPU possible with 16GB"},
    "pi_zero2w_2026": {"name": "Raspberry Pi Zero 2W (2026 firmware era)", "year": 2026, "type": "SBC", "price": 15, "ram_gb": 0.5, "arch": "ARM", "highlight": "Still the ultraminimal deck king in 2026. Tiny, cheap, community-proven.", "best_for": ["minimalist", "survival"], "gpu_ai": "1B models ~1 t/s ceiling"},
}

class NewHardwareRadar:
    @staticmethod
    def overview() -> str:
        return ("<b>2026 Hardware Radar</b>\n\n"
                "Fresh boards circulating in the 2026 community. Keep your SBC "
                "database current.\n\n"
                "Commands:\n"
                "  /newhardware              — all 2026 arrivals\n"
                "  /newhardware detail <name> — deep dive on one board\n"
                "  /newhardware compare <a> <b> — side-by-side")

    @staticmethod
    def list_all() -> str:
        lines = ["<b>2026 Hardware Radar</b>\n"]
        for k, v in NEW_HARDWARE_2026.items():
            lines.append(f"<b>{v['name']}</b> — ${v['price']} ({v['type']}, {v['year']})")
            lines.append(f"  {v['highlight']}\n")
        return "\n".join(lines)

    @staticmethod
    def detail(name: str) -> str:
        for k, v in NEW_HARDWARE_2026.items():
            if name.lower() in k or name.lower() in v["name"].lower():
                lines = [f"<b>{v['name']}</b>\n"]
                lines.append(f"  Type: {v['type']} | Arch: {v['arch']} | ${v['price']}")
                lines.append(f"  RAM: {v['ram_gb']}GB")
                lines.append(f"  AI: {v['gpu_ai']}")
                lines.append(f"  Highlight: {v['highlight']}")
                lines.append(f"  Best for: {', '.join(v['best_for'])}")
                return "\n".join(lines)
        return f"Unknown board '{name}'. Available: {', '.join(NEW_HARDWARE_2026.keys())}"

    @staticmethod
    def compare(a: str, b: str) -> str:
        va = vb = None
        for k, v in NEW_HARDWARE_2026.items():
            if a.lower() in k or a.lower() in v["name"].lower():
                va = v
            if b.lower() in k or b.lower() in v["name"].lower():
                vb = v
        if not va or not vb:
            return f"Could not match boards. Available: {', '.join(NEW_HARDWARE_2026.keys())}"
        lines = [f"<b>Compare: {va['name']} vs {vb['name']}</b>\n"]
        lines.append(f"{'Metric':16} | {va['name'][:22]:22} | {vb['name'][:22]:22}")
        rows = [
            ("Price", f"${va['price']}", f"${vb['price']}"),
            ("RAM", f"{va['ram_gb']}GB", f"{vb['ram_gb']}GB"),
            ("Arch", va["arch"], vb["arch"]),
            ("Type", va["type"], vb["type"]),
        ]
        for name, av, bv in rows:
            lines.append(f"{name:16} | {av:22} | {bv:22}")
        lines.append(f"\n  {va['name']}: {va['highlight']}")
        lines.append(f"\n  {vb['name']}: {vb['highlight']}")
        return "\n".join(lines)

# ============================================================
# SINGLETON
# ============================================================
_agent_instance = None

def get_cyberdeck_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CyberdeckAgent()
    return _agent_instance
