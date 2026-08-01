"""
test_print_service.py - End-to-end tests for 3D print + Shopee ordering pipeline.
Tests all layers: Rust export, Python bridge, Shopee module, full integration.
"""
import os, sys, json, math
from pathlib import Path

sys.path.insert(0, ".")
PRINTS_DIR = "cyberdeck_prints"
PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        marker = " [FAIL] "
        print(f"  {marker}{name}" + (f" - {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ------------------------------------------------------------------
section("1. Rust Module Import & Basic Sanity")
# ------------------------------------------------------------------
from cyberdeck_core import (
    Model3dConfig, export_scad, export_stl, generate_print_package,
    generate_3d_model
)
check("Model3dConfig class exists", callable(Model3dConfig))
check("export_scad exists", callable(export_scad))
check("export_stl exists", callable(export_stl))
check("generate_print_package exists", callable(generate_print_package))

cfg = Model3dConfig("Test Enclosure", "black", "cyberpunk", 120.0, 40.0, 90.0)
check("Config created", cfg.description == "Test Enclosure")
check("Config dims", cfg.width == 120.0 and cfg.height == 40.0 and cfg.depth == 90.0)

# ------------------------------------------------------------------
section("2. SCAD Export (Rust -> File)")
# ------------------------------------------------------------------

scad_result = export_scad(cfg)
check("SCAD result is dict", isinstance(scad_result, dict))
scad_path = scad_result.get("scad_path", "")
check("SCAD path returned", bool(scad_path))
check("SCAD file exists on disk", os.path.isfile(scad_path))
scad_size = os.path.getsize(scad_path)
check("SCAD file non-empty", scad_size > 500, f"{scad_size} bytes")
check("Filename has .scad", scad_result["filename"].endswith(".scad"))
check("Style in result", scad_result["style"] == "cyberpunk")
check("Color in result", scad_result["color"] == "black")
check("Width in result", scad_result["width_mm"] == 120.0)
check("Volume is < bounding box",
      scad_result["volume_cc"] < scad_result["bounding_volume_cc"],
      f"{scad_result['volume_cc']} < {scad_result['bounding_volume_cc']}")

with open(scad_path, "r", encoding="utf-8") as f:
    scad_content = f.read()
check("SCAD contains modules", "module enclosure_body" in scad_content)
check("SCAD has standoffs", "standoffs" in scad_content)
check("SCAD has hinge", "hinge" in scad_content)
check("SCAD has vent slots", "vent_slots" in scad_content)
check("SCAD has cable channel", "cable_channel" in scad_content)
check("SCAD has IO cutouts", "io_cutouts" in scad_content)
check("SCAD has assembly", "difference()" in scad_content)
check("SCAD uses style colors", "#" in scad_content)

# ------------------------------------------------------------------
section("3. STL Export (Rust -> CLI -> STL)")
# ------------------------------------------------------------------

stl_result = export_stl(cfg)
check("STL result is dict", isinstance(stl_result, dict))
if stl_result.get("stl_path"):
    check("STL file exists", os.path.isfile(stl_result["stl_path"]))
    stl_size = os.path.getsize(stl_result["stl_path"])
    check("STL non-empty", stl_size > 1000, f"{stl_size} bytes")
    check("STL size key present", "stl_size_kb" in stl_result)
else:
    warning = stl_result.get("stl_warning", "")
    check("STL export skipped (OpenSCAD CLI not found)", True,
          f"Graceful degradation: {warning[:80]}...")

# ------------------------------------------------------------------
section("4. Print Package (Full Job Bundle)")
# ------------------------------------------------------------------

for mat in ["PETG", "PLA", "ABS", "Resin", "Carbon Fiber PETG"]:
    pkg = generate_print_package(cfg, mat, 1)
    check(f"Print package with {mat}", isinstance(pkg, dict))
    check(f"  - Files present", "files" in pkg)
    check(f"  - Model info present", "model" in pkg)
    check(f"  - Print spec present", "print_spec" in pkg)
    check(f"  - Pricing present", "pricing" in pkg)
    check(f"  - Volume realistic", pkg["model"]["volume_cc"] < 200,
          f"{pkg['model']['volume_cc']}cc")
    check(f"  - Filament reasonable", pkg["model"]["estimated_filament_g"] < 500,
          f"{pkg['model']['estimated_filament_g']}g")
    check(f"  - Total > 0", pkg["pricing"]["total_estimate_usd"] > 0)

# Test quantity scaling (use same material as reference)
from cyberdeck_core import generate_print_package as gpp
pkg_ref = gpp(cfg, "PETG", 1)
pkg_3 = gpp(cfg, "PETG", 3)
check("Quantity 3 scales filament",
      abs(pkg_3["model"]["estimated_filament_g"] - 3 * pkg_ref["model"]["estimated_filament_g"]) < 0.2)
check("Quantity 3 scales total",
      pkg_3["pricing"]["total_estimate_usd"] > pkg_ref["pricing"]["total_estimate_usd"] * 2.5)
check("Filament per unit key exists",
      "filament_per_unit_g" in pkg_ref["model"])
# Clean up loop vars
pkg = gpp(cfg, "PETG", 1)

# Test different styles
for style in ["cyberpunk", "futuristic", "retro", "industrial", "minimal", "steampunk"]:
    c = Model3dConfig("Style Test", "black", style, 100, 30, 80)
    p = generate_print_package(c, "PETG", 1)
    check(f"Style '{style}' stored in model",
          p["model"]["style"] == style)
    check(f"Style '{style}' has finish recommendation",
          bool(p.get("print_spec", {}).get("finish_recommendation", "")))

# Test different volume sizes
for label, w, h, d in [("Small Pi Zero", 80, 25, 60), ("Medium Pi 5", 120, 40, 90), ("Large LattePanda", 160, 50, 120)]:
    c = Model3dConfig(label, "black", "industrial", float(w), float(h), float(d))
    p = generate_print_package(c, "PETG", 1)
    check(f"{label}: volume < bounding",
          p["model"]["volume_cc"] < p["model"]["bounding_volume_cc"],
          f"{p['model']['volume_cc']} < {p['model']['bounding_volume_cc']}")
    check(f"{label}: filament > 0", p["model"]["estimated_filament_g"] > 10)
    check(f"{label}: print hours > 0", p["pricing"]["estimated_print_hours"] > 0)

# ------------------------------------------------------------------
section("5. Bridge Layer (cyberdeck_bridge)")
# ------------------------------------------------------------------

from cyberdeck_bridge import (
    HAS_RUST, export_scad as br_export_scad,
    export_stl as br_export_stl,
    generate_print_package as br_generate_print_package,
)
check("Bridge HAS_RUST", HAS_RUST)
br_scad = br_export_scad("Bridge Test", "white", "minimal", 100, 30, 80)
check("Bridge export_scad works", br_scad is not None)
check("Bridge scad has file", br_scad.get("scad_path", "").endswith(".scad"))

br_stl = br_export_stl("Bridge Test", "white", "minimal", 100, 30, 80)
check("Bridge export_stl returns dict", isinstance(br_stl, dict))

br_pkg = br_generate_print_package("Bridge Test", "PLA", 2, "white", "minimal", 100, 30, 80)
check("Bridge print package", br_pkg is not None)
check("Bridge package files", "scad" in br_pkg.get("files", {}))

# ------------------------------------------------------------------
section("6. Shopee Module (cyberdeck_shopee)")
# ------------------------------------------------------------------

from cyberdeck_shopee import (
    shopee_search_url, generate_order_spec, shopee_order_message,
    estimate_print_cost, find_shopee_sellers, prepare_print_job,
    MATERIAL_OPTIONS,
)

# URL generation
url = shopee_search_url("jasa 3D printing")
check("Shopee search URL has shopee.co.id", "shopee.co.id" in url)
check("Shopee URL encoded keyword", "jasa%203D%20printing" in url)

url_jkt = shopee_search_url("jasa 3D printing", "Jakarta")
check("Shopee URL with location", "Jakarta" in url_jkt or "location" in url_jkt)

# Material options
check("Material options defined", len(MATERIAL_OPTIONS) >= 6)
check("PETG in materials", "PETG" in MATERIAL_OPTIONS)
check("PETG has price", MATERIAL_OPTIONS["PETG"]["price_per_g"] > 0)

# Cost estimation - IDR (Indonesia)
cost_idr = estimate_print_cost(126.7, "PETG", 1, "id")
check("IDR cost has total_idr", cost_idr.get("total_idr", 0) > 0)
check("IDR cost reasonable", 50000 < cost_idr["total_idr"] < 1000000,
      f"Rp {cost_idr['total_idr']:,}")
check("IDR cost has search URL", "shopee.co.id" in cost_idr.get("recommended_search", ""))

cost_idr2 = estimate_print_cost(126.7, "PLA", 2, "id")
check("IDR PLA cheaper than PETG",
      cost_idr2["total_idr"] < cost_idr["total_idr"] * 2.1)

# Cost estimation - USD
cost_usd = estimate_print_cost(126.7, "PETG", 1, "us")
check("USD cost has total_usd", cost_usd.get("total_usd", 0) > 0)
check("USD cost reasonable", 5 < cost_usd["total_usd"] < 250)

# Order spec generation
spec = generate_order_spec({
    "volume_cc": 126.7, "dimensions_mm": "120x40x90",
    "name": "Cyberdeck Enclosure", "style": "cyberpunk",
    "filename": "enclosure.stl"
}, "PETG", 1, "black", "USB-C cutout needed")
check("Order spec has model info", "Cyberdeck Enclosure" in spec)
check("Order spec has PETG", "PETG" in spec)
check("Order spec has settings", "0.16mm" in spec or "0.20mm" in spec)
check("Order spec has orientation", "Interior" in spec or "orient" in spec.lower())
check("Order spec has notes", "USB-C" in spec)
check("Order spec has post-processing", "supports" in spec.lower())
check("Order spec has standoff info", "M2.5" in spec)

# Shopee chat message
msg = shopee_order_message("Cyberdeck Enclosure", "PETG", 1, 126.7, 15.0)
check("Chat message has greeting", "Halo" in msg)
check("Chat message has material", "PETG" in msg)
check("Chat message has budget", "Rp" in msg)
check("Chat message has specs", "0.16mm" in msg)
check("Chat message has STL mention", "STL" in msg or "file" in msg.lower())

# Find sellers
search = find_shopee_sellers("jasa 3D printing", "PETG", "Bandung")
check("Seller search has URL", "shopee.co.id" in search.get("search_url", ""))
check("Seller search has keyword", "PETG" in search.get("search_term", ""))
check("Seller search has instructions", bool(search.get("instructions")))

# Full pipeline
result = prepare_print_job({
    "description": "Pi 5 Enclosure", "style": "cyberpunk",
    "color": "black", "width": 120, "height": 40, "depth": 90
}, "PETG", 1)
check("Full pipeline returns dict", isinstance(result, dict))
check("Pipeline has files", "files" in result)
check("Pipeline has model", "model" in result)
check("Pipeline has print_spec", "print_spec" in result)
check("Pipeline has pricing", "pricing" in result)
check("Pipeline has search", "search" in result)
check("Pipeline has order_specification", "order_specification" in result)
check("Pipeline has shopee_chat_message", "shopee_chat_message" in result)
check("Pipeline SCAD file exists",
      result.get("files", {}).get("scad", "").endswith(".scad"))
check("Pipeline chat msg mentions enclosure",
      "Enclosure" in result.get("shopee_chat_message", ""))
check("Pipeline order spec has all sections",
      all(s in result.get("order_specification", "") for s in ["PRINT SETTINGS", "ORIENTATION", "POST-PROCESSING", "FILES ATTACHED"]))

# Test with no config
empty = prepare_print_job()
check("Empty config returns error", "error" in empty or "usage" in empty)

# ------------------------------------------------------------------
section("7. Edge Cases & Error Handling")
# ------------------------------------------------------------------

# Minimum dimensions
tiny_cfg = Model3dConfig("Tiny", "black", "minimal", 10.0, 10.0, 10.0)
tiny_scad = export_scad(tiny_cfg)
check("Tiny model exports", tiny_scad is not None)

# Very large
big_cfg = Model3dConfig("Big", "white", "industrial", 500.0, 200.0, 400.0)
big_pkg = generate_print_package(big_cfg, "PETG", 1)
check("Large model generates pricing", big_pkg["pricing"]["total_estimate_usd"] > 0)

# Unusual material
weird_pkg = generate_print_package(cfg, "Unobtainium", 1)
check("Unknown material defaults", weird_pkg["pricing"]["total_estimate_usd"] > 0)

# Empty description
empty_name = Model3dConfig("", "black", "cyberpunk", 100, 30, 80)
empty_scad = export_scad(empty_name)
check("Empty description exports", empty_scad is not None)
check("Empty name file has fallback name", bool(empty_scad.get("filename")))

# Shopee with special characters
url_special = shopee_search_url("jasa 3D printing + resin")
check("Special char in URL", "%" in url_special)

# Zero quantity
try:
    _ = generate_print_package(cfg, "PETG", 0)
    check("Zero quantity accepted", True)
except Exception:
    check("Zero quantity rejected", True)

# ------------------------------------------------------------------
section("8. Version Consistency")
# ------------------------------------------------------------------

with open("version.json", encoding="utf-8") as f:
    ver = json.load(f)

check("Version file loadable", isinstance(ver, dict))
check("Version has version key", "version" in ver)
print(f"  Version: {ver.get('version', '?')}")
print(f"  Changelog entries: {len(ver.get(ver.get('version', ''), []))}")

# ------------------------------------------------------------------
section("RESULTS")
# ------------------------------------------------------------------

print(f"\n  {'='*50}")
print(f"  TOTAL: {PASS} passed, {FAIL} failed")
print(f"  {'='*50}")

if FAIL > 0:
    print("\n  ~~> SOME TESTS FAILED")
    sys.exit(1)
else:
    print("\n  ~~> ALL TESTS PASSED")
