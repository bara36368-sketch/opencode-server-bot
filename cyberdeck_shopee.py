"""
cyberdeck_shopee.py — Automated 3D printing order system for Shopee Indonesia.
Generates STL/SCAD files, searches Shopee for 3D printing services,
creates order specifications, and generates Shopee chat message templates.
All materials are premium-grade, matching the best available from
Indonesian 3D printing services (3D Extrude ID, 3D To Real Studio, etc.).
"""
import os, json, math, webbrowser, urllib.parse
from datetime import datetime
from pathlib import Path

PRINTS_DIR = "cyberdeck_prints"

MATERIAL_OPTIONS = {
    "PETG": {"price_per_g": 0.04, "print_temp": "230-250°C", "bed_temp": "70-85°C",
             "desc": "Strong, UV resistant, premium-grade. Best for enclosures.",
             "tier": "Standard Premium"},
    "PETG-CF": {"price_per_g": 0.12, "print_temp": "230-260°C", "bed_temp": "70-85°C",
                "desc": "PETG + carbon fiber. Stiff, lightweight, matte premium finish. Hardened nozzle required.",
                "tier": "Advanced Premium"},
    "ABS+": {"price_per_g": 0.05, "print_temp": "240-260°C", "bed_temp": "90-110°C",
             "desc": "Premium ABS+. High strength, acetone vapor smoothable. Needs enclosed printer.",
             "tier": "Standard Premium"},
    "ASA": {"price_per_g": 0.07, "print_temp": "240-260°C", "bed_temp": "90-110°C",
            "desc": "UV stable, weather resistant. Premium outdoor-grade. Needs enclosure.",
            "tier": "Standard Premium"},
    "eASA": {"price_per_g": 0.08, "print_temp": "245-265°C", "bed_temp": "95-110°C",
             "desc": "Extended ASA. Superior UV/heat/crack resistance. Top-tier outdoor material.",
             "tier": "Advanced Premium"},
    "Polycarbonate": {"price_per_g": 0.12, "print_temp": "265-290°C", "bed_temp": "95-110°C",
                      "desc": "PC. High heat resistance (110°C). Stiff, strong. All-metal hotend required.",
                      "tier": "Advanced Premium"},
    "PC-CF": {"price_per_g": 0.18, "print_temp": "270-290°C", "bed_temp": "100-115°C",
              "desc": "Polycarbonate + carbon fiber. Extreme stiffness & heat resistance. Professional grade.",
              "tier": "Ultra Premium"},
    "PA-Nylon": {"price_per_g": 0.10, "print_temp": "250-270°C", "bed_temp": "70-85°C",
                 "desc": "Pure nylon. Tough, impact-resistant, low friction. Must dry before printing.",
                 "tier": "Advanced Premium"},
    "PA-CF": {"price_per_g": 0.18, "print_temp": "260-280°C", "bed_temp": "80-90°C",
              "desc": "Nylon + carbon fiber. Highest tensile strength. Aircraft-grade. Hardened nozzle required.",
              "tier": "Ultra Premium"},
    "PA12-CF": {"price_per_g": 0.25, "print_temp": "260-285°C", "bed_temp": "80-95°C",
                "desc": "PA12 + carbon fiber. The ultimate FDM material. Chemical/heat/impact resistant. Hardened nozzle + enclosure required.",
                "tier": "Ultra Premium"},
    "ABS-GF": {"price_per_g": 0.15, "print_temp": "250-270°C", "bed_temp": "100-115°C",
               "desc": "ABS + glass fiber. Extreme stiffness & thermal stability. Industrial-grade.",
               "tier": "Advanced Premium"},
    "eTPU": {"price_per_g": 0.09, "print_temp": "220-240°C", "bed_temp": "40-60°C",
             "desc": "Premium flexible TPU. Elastic, abrasion-resistant. Good for gaskets & feet.",
             "tier": "Standard Premium"},
    "Resin": {"price_per_g": 0.20, "print_temp": "N/A (UV cure)", "bed_temp": "N/A",
              "desc": "High-detail SLA/DLP resin. Perfect for intricate parts & display pieces.",
              "tier": "Ultra Premium"},
    "PEEK": {"price_per_g": 0.35, "print_temp": "360-400°C", "bed_temp": "120-150°C",
             "desc": "Polyether Ether Ketone. Medical-grade, 250°C continuous, 343°C melt. Extreme chemical/radiation resistance. All-metal hotend 400C+ required, enclosed chamber 100C+.",
             "tier": "Industrial Premium"},
    "PEI_Ultem": {"price_per_g": 0.30, "print_temp": "340-380°C", "bed_temp": "120-150°C",
                  "desc": "PEI/Ultem 1010. Aerospace-grade, 216°C continuous, flame retardant. Highest dielectric strength. Enclosed chamber 120C+, hotend 380C+ required.",
                  "tier": "Industrial Premium"},
    "PPSU": {"price_per_g": 0.28, "print_temp": "330-370°C", "bed_temp": "120-145°C",
             "desc": "Polyphenylsulfone. 220°C continuous, extremely impact resistant — 'unbreakable'. Sterilizable, chemical resistant. Enclosed chamber required.",
             "tier": "Industrial Premium"},
    "Ceramic_Alumina": {"price_per_g": 2.50, "print_temp": "N/A (SLA + sintering)", "bed_temp": "N/A",
                        "desc": "99.8% Alumina (Al2O3) ceramic via SLA + kiln sintering. 1600°C max service. Electrically insulating, 9H hardness, chemically inert. Requires ceramic 3D printing service.",
                        "tier": "Industrial Premium"},
    "StainlessSteel_316L": {"price_per_g": 3.00, "print_temp": "N/A (DMLS)", "bed_temp": "N/A",
                           "desc": "316L stainless steel via DMLS/SLM. 1400°C melting point. Corrosion resistant, magnetic, medical-grade. Requires metal 3D printing service (DMLS).",
                           "tier": "Industrial Premium"},
    "Titanium_Ti64": {"price_per_g": 5.00, "print_temp": "N/A (DMLS)", "bed_temp": "N/A",
                      "desc": "Ti-6Al-4V titanium alloy via DMLS/SLM. 1668°C melting point. Highest strength-to-weight ratio. Aerospace & medical grade. Requires metal 3D printing service.",
                      "tier": "Industrial Premium"},
}

POST_PROCESSING_OPTIONS = {
    "superhydrophobic_nano": {
        "name": "Superhydrophobic Nano Coating",
        "type": "spray",
        "price_idr": 75000,
        "price_usd": 5.00,
        "description": "NeverWet-style superhydrophobic nano coating. Creates 150-171° water contact angle — water beads up and rolls off surfaces. Viral on TikTok/YouTube 2023.",
        "application": "Clean surface, spray 6-8 inches away, 3 thin coats, 30min between coats, 24h full cure",
        "temp_range": "-40°C to 150°C",
        "durability": "6-12 months (reapply as needed)",
    },
    "vapor_smoothing": {
        "name": "Acetone Vapor Smoothing",
        "type": "chemical",
        "price_idr": 35000,
        "price_usd": 2.00,
        "description": "Acetone vapor bath for ABS/ASA. Melts surface layer for glossy, injection-mold-like finish. Seals layer lines.",
        "application": "Vapor chamber treatment, 15-30min exposure. For ABS/ASA materials only.",
        "temp_range": "N/A",
        "durability": "Permanent",
    },
    "ceramic_coating": {
        "name": "Nano-Ceramic Coating (Automotive Grade)",
        "type": "liquid",
        "price_idr": 120000,
        "price_usd": 8.00,
        "description": "9H hardness nano-ceramic coating. UV resistant, chemical resistant, 175°C tolerant. Professional automotive-grade protection.",
        "application": "Surface prep with isopropyl alcohol, apply with applicator, buff after 5min, 24h cure",
        "temp_range": "-40°C to 175°C",
        "durability": "2-3 years",
    },
    "conformal_coating": {
        "name": "PCB Conformal Coating (Silicone)",
        "type": "spray",
        "price_idr": 100000,
        "price_usd": 7.00,
        "description": "Silicone conformal coating spray for PCBs. MIL-spec protection against moisture, dust, corrosion & short circuits. Apply directly to populated PCB before assembly.",
        "application": "Mask connectors & switches. Spray 6in away, 2-3 thin coats. 30min dry between coats. 24h full cure. Apply BEFORE inserting into enclosure.",
        "temp_range": "-65°C to 200°C",
        "durability": "Permanent (removable with isopropyl alcohol)",
    },
    "silicone_conformal_pen": {
        "name": "Silicone Conformal Coating Pen",
        "type": "pen",
        "price_idr": 65000,
        "price_usd": 4.50,
        "description": "Precision applicator pen for spot-coating solder joints, pin headers & exposed traces. Good for repairs or targeted protection without masking.",
        "application": "Draw over solder joints & exposed traces. 30min dry. 24h full cure.",
        "temp_range": "-65°C to 200°C",
        "durability": "Permanent",
    },
    "gasket_kit": {
        "name": "Silicone Gasket + O-Ring Seal Kit",
        "type": "hardware",
        "price_idr": 85000,
        "price_usd": 5.50,
        "description": "Custom-cut silicone gasket sheet (1.5mm) for enclosure seam + assorted nitrile O-rings for screw holes & connector boots. Full waterproof seal.",
        "application": "Cut gasket to enclosure profile. Lay between body & lid. Apply O-rings under screw heads and around panel-mount connectors.",
        "temp_range": "-40°C to 230°C",
        "durability": "Permanent (replaceable)",
    },
    "dielectric_grease": {
        "name": "Dielectric Grease Kit",
        "type": "grease",
        "price_idr": 35000,
        "price_usd": 2.00,
        "description": "Silicone-based dielectric grease for connector pins & battery terminals. Prevents corrosion, arcing & moisture ingress at contact points.",
        "application": "Apply thin layer to connector pins, battery terminals & switch contacts before assembly.",
        "temp_range": "-50°C to 200°C",
        "durability": "Permanent (reapply on disconnect)",
    },
    "waterproof_bundle": {
        "name": "Full Waterproof Bundle",
        "type": "bundle",
        "price_idr": 250000,
        "price_usd": 17.00,
        "description": "Complete waterproofing package: exterior superhydrophobic nano coating + PCB conformal coating + gasket kit + dielectric grease. Makes the entire cyberdeck splash-proof and weather-resistant.",
        "application": "1) Conformal coat PCB. 2) Assemble with gasket. 3) Apply dielectric grease to connectors. 4) Spray superhydrophobic coating on exterior shell.",
        "temp_range": "-65°C to 200°C",
        "durability": "1-2 years (nano coating reapply), permanent rest",
    },
}

SHOPEE_JASA_URL = "https://shopee.co.id/search?keyword={keyword}&filters={\"category\":\"118080\"}"


MATERIAL_TIER_PREMIUM_IDR = {
    "Standard Premium": {"price_per_g_idr": 1500, "service_per_hour_idr": 25000},
    "Advanced Premium": {"price_per_g_idr": 3000, "service_per_hour_idr": 40000},
    "Ultra Premium":    {"price_per_g_idr": 5000, "service_per_hour_idr": 60000},
    "Industrial Premium": {"price_per_g_idr": 10000, "service_per_hour_idr": 100000},
}


def shopee_search_url(keyword="jasa 3D printing", location=None):
    kw = urllib.parse.quote(keyword)
    url = f"https://shopee.co.id/search?keyword={kw}"
    if location:
        loc = urllib.parse.quote(location)
        url += f"&location={loc}"
    return url


def material_tier(material):
    mat = MATERIAL_OPTIONS.get(material, MATERIAL_OPTIONS["PETG"])
    return mat.get("tier", "Standard Premium")


def estimate_print_cost(volume_cc, material="PETG", quantity=1, location="id"):
    vol = volume_cc * quantity
    mat = MATERIAL_OPTIONS.get(material, MATERIAL_OPTIONS["PETG"])
    filament_g = vol * 1.24
    tier = mat.get("tier", "Standard Premium")
    tier_pricing = MATERIAL_TIER_PREMIUM_IDR.get(tier, MATERIAL_TIER_PREMIUM_IDR["Standard Premium"])

    # IDR pricing — premium Indonesian service rates (Shopee / Tokopedia)
    if location == "id":
        price_per_g = tier_pricing["price_per_g_idr"]
        service_per_hour = tier_pricing["service_per_hour_idr"]
        print_hours = get_print_hours(vol)
        base_cost = filament_g * price_per_g
        service_fee = int(print_hours * service_per_hour)
        shipping = 25000  # premium insured shipping
        total_idr = int(base_cost + service_fee + shipping)

        is_dmls = material in ("Ceramic_Alumina", "StainlessSteel_316L", "Titanium_Ti64")
        note = "Premium Indonesian jasa 3D printing rates. Actual cost depends on seller."
        if is_dmls:
            note += " DMLS/metal/ceramic — contact seller for exact pricing, this is an estimate."
        elif tier == "Industrial Premium":
            note += " Industrial-grade high-temp material — confirm availability with seller."

        return {
            "filament_g": round(filament_g, 1),
            "material": material,
            "material_tier": tier,
            "price_per_g_idr": price_per_g,
            "material_cost_idr": int(base_cost),
            "service_fee_idr": service_fee,
            "estimated_print_hours": round(print_hours, 1),
            "shipping_idr": shipping,
            "total_idr": total_idr,
            "total_usd": round(total_idr / 16000, 2),
            "currency": "IDR",
            "note": note,
            "recommended_search": shopee_search_url(f"jasa 3D printing {material}"),
        }
    else:
        price_per_g = mat["price_per_g"]
        material_cost = filament_g * price_per_g
        print_hours = get_print_hours(vol)
        service_hourly = 10.0 if tier == "Industrial Premium" else 5.0
        service_cost = print_hours * service_hourly
        shipping = 25.0 if tier == "Industrial Premium" else 15.0  # international premium shipping
        total = material_cost + service_cost + shipping

        is_dmls = material in ("Ceramic_Alumina", "StainlessSteel_316L", "Titanium_Ti64")
        note = "Premium material pricing. International shipping included."
        if is_dmls:
            note += " DMLS/metal/ceramic — contact seller for exact pricing, this is an estimate."
        elif tier == "Industrial Premium":
            note += " Industrial-grade high-temp material — confirm availability with seller."

        return {
            "filament_g": round(filament_g, 1),
            "material": material,
            "material_tier": tier,
            "material_cost_usd": round(material_cost, 2),
            "service_cost_usd": round(service_cost, 2),
            "shipping_usd": shipping,
            "total_usd": round(total, 2),
            "print_hours": round(print_hours, 1),
            "currency": "USD",
            "note": note,
        }


def get_print_hours(volume_cc):
    return max(1.0, volume_cc / 7.0)


def generate_order_spec(model_info, material="PETG", quantity=1, color=None, notes="", post_processing=None):
    vol_cc = model_info.get("volume_cc", 100)
    dims = model_info.get("dimensions_mm", "120x40x90")
    name = model_info.get("name", "Cyberdeck Enclosure")
    style = model_info.get("style", "cyberpunk")

    mat = MATERIAL_OPTIONS.get(material, MATERIAL_OPTIONS["PETG"])
    tier = mat.get("tier", "Standard Premium")
    filament_g = vol_cc * 1.24 * quantity
    print_hours = get_print_hours(vol_cc * quantity)

    is_industrial = material in ("PEEK", "PEI_Ultem", "PPSU")
    is_dmls = material in ("Ceramic_Alumina", "StainlessSteel_316L", "Titanium_Ti64")

    if tier == "Industrial Premium":
        if is_dmls:
            printer_req = "Specialized DMLS/SLM metal printer or ceramic SLA + kiln sintering. Industrial facility required. Contact for lead time."
            handling = "Industrial-grade. Post-processing: support removal, surface finishing, heat treatment (if applicable)."
        elif is_industrial:
            printer_req = "High-temp printer (400C+ hotend, 120C+ chamber). E.g. Intamsys FUNMAT HT, Vision Miner, or custom Voron with high-temp mods."
            handling = "Extremely moisture sensitive. Dry 8-12h at 80-100°C. Print from filament dryer. Store in sealed bag with desiccant."
        else:
            printer_req = "Specialized industrial printer."
            handling = "Handle with care. Industrial-grade material."
    elif tier == "Ultra Premium":
        printer_req = "Enclosed printer (e.g. Bambu Lab X1C, Voron), hardened nozzle, filament dryer required."
        handling = "Extremely hygroscopic. Print directly from filament dryer. Store in sealed bag with desiccant."
    elif tier == "Advanced Premium":
        printer_req = "Enclosed or semi-enclosed printer, all-metal hotend recommended."
        handling = "Hygroscopic. Dry before printing (4-6h at 70-80°C)."
    else:
        printer_req = "Standard enclosed or open printer."
        handling = "Store in cool dry place."

    density = {"Standard Premium": 1.24, "Advanced Premium": 1.20, "Ultra Premium": 1.15, "Industrial Premium": 1.10}.get(tier, 1.24)
    weight_g = vol_cc * density * quantity

    coating_lines = ""
    seal_lines = ""
    if post_processing and post_processing in POST_PROCESSING_OPTIONS:
        pp = POST_PROCESSING_OPTIONS[post_processing]
        coating_lines = f"""
ADDITIONAL SERVICE: {pp['name']}
  Description: {pp['description']}
  Application: {pp['application']}
  Temp Range: {pp['temp_range']}
  Durability: {pp['durability']}
  Cost: Rp{pp['price_idr']:,} (IDR) / ${pp['price_usd']:.2f} (USD)"""
        is_conformal = "conformal" in post_processing
        is_bundle = post_processing == "waterproof_bundle"
        if is_conformal or is_bundle:
            seal_lines = """
WATERPROOFING NOTES — CRITICAL
  Water is the #1 enemy of electronics. Conformal coating + gasket + nano coating
  work together to protect your cyberdeck from shorts & corrosion.
  Assembly order: 1) Conformal coat PCB first (before inserting into enclosure)
                   2) Install gasket on enclosure seam
                   3) Apply dielectric grease to connector pins
                   4) Assemble enclosure, then spray nano coating on exterior
  !!! Do NOT superhydrophobic spray the PCB — it is NOT designed for electronics.
  !!! Do NOT conformal coat over connectors/switches — mask them first."""

    spec = f"""================================================================
3D PRINTING ORDER SPECIFICATION — PREMIUM
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Material Tier: {tier}
================================================================

MODEL: {name}
STYLE: {style}
DIMENSIONS: {dims}
VOLUME: {vol_cc:.1f} cc
EST. WEIGHT: ~{weight_g:.0f}g ({quantity} unit(s))
TIER: {tier}

PRINT SETTINGS
  Material: {material} — {mat['desc']}
  Color: {color or style.replace('_', ' ').title() + ' scheme'}
  Layer Height: 0.16mm (fine) / 0.20mm (standard)
  Infill: 15% gyroid (structural) or 25% (heavy duty)
  Perimeters: 4 (premium)
  Supports: Auto (45 degree threshold) — remove carefully
  Quantity: {quantity} unit(s)
  Estimated print time: {print_hours:.1f} hours total
  Printer requirements: {printer_req}

ORIENTATION
  - Body: Interior facing up for best overhangs
  - Lid: Facing up
  - M2.5 standoff holes: 6x (3.2mm outer, 1.3mm inner)
  - Cable channel: 2.4x4mm along left edge
  - IO cutouts: HDMI, USBx2, USB-C power, audio, GPIO

POST-PROCESSING
  - Remove supports carefully (flush cutters recommended)
  - Sand mating surfaces flat (400 grit for final)
  - Tap M2.5 holes (or use 1.3mm drill + brass heat-set inserts)
  - {handling}
  - {mat['desc']}{coating_lines}{seal_lines}

FILES ATTACHED
  - {model_info.get('filename', 'model.stl')}
  - (OpenSCAD source available if edits needed)

NOTES
  {notes or 'Premium cyberdeck enclosure. Print orientation as specified.'}
  {chr(9888) + ' Hotend 265C+ required for this material.' if mat['print_temp'].startswith('26') else ''}
  {chr(9888) + ' Hardened nozzle MANDATORY for carbon/glass fiber materials.' if 'CF' in material or 'GF' in material else ''}
  {chr(9888) + ' HIGH TEMP — 360C+ hotend, 100C+ chamber required.' if is_industrial else ''}
  {chr(9888) + ' DMLS/SLM INDUSTRIAL SERVICE — contact for lead time & pricing.' if is_dmls else ''}

================================================================
"""
    return spec


def shopee_order_message(model_name, material, quantity, volume_cc, budget_usd=None, post_processing=None):
    mat = MATERIAL_OPTIONS.get(material, MATERIAL_OPTIONS["PETG"])
    tier = mat.get("tier", "Standard Premium")
    is_dmls = material in ("Ceramic_Alumina", "StainlessSteel_316L", "Titanium_Ti64")
    lines = [
        f"Halo kak, saya mau order jasa 3D printing premium untuk {quantity} unit.",
        f"Material: {material} ({tier})",
        "",
        f"Model: {model_name}",
        f"Estimasi volume: {volume_cc:.1f}cc per unit",
        f"Jumlah: {quantity} unit",
        "",
        "Spesifikasi cetak premium:",
        "- Layer height: 0.16mm",
        "- Infill: 15% gyroid",
        "- Perimeters: 4",
        "- Supports: auto (45 deg threshold)",
        "",
        f"{mat['desc']}",
        "",
    ]
    if is_dmls:
        lines += [
            "Ini material industrial — DMLS/metal/ceramic.",
            "Mohon info lead time, minimum order, dan harga.",
        ]
    if post_processing and post_processing in POST_PROCESSING_OPTIONS:
        pp = POST_PROCESSING_OPTIONS[post_processing]
        lines += [
            "",
            f"Butuh tambahan: {pp['name']}",
            f"Estimasi biaya: Rp{pp['price_idr']:,}",
        ]
    lines += [
        "",
        "File STL sudah siap. Mohon estimasi harga + ongkir untuk material ini?",
        "Terima kasih.",
    ]
    if budget_usd:
        idr_estimate = budget_usd * 16000
        lines.insert(1, f"Budget sekitar Rp{idr_estimate:,.0f}.")
    return "\n".join(lines)




def find_shopee_sellers(search_term="jasa 3D printing", material=None, city=None):
    kw = search_term
    if material:
        kw += f" {material}"
    url = shopee_search_url(kw, city)
    return {
        "search_url": url,
        "search_term": kw,
        "instructions": "Klik URL search untuk lihat daftar penyedia jasa 3D printing premium di Shopee.\n"
                        "Cari seller dengan rating tinggi (>4.8) dan badge 'Premium' atau 'Star Seller'.\n"
                        "Tanyakan apakah mereka support material premium (nylon CF, polycarbonate, dll).\n"
                        "Kirimkan file STL + order spec via chat Shopee.",
        "pro_tip": "Filter lokasi 'Jakarta' atau 'Bandung' untuk pengiriman lebih cepat. "
                   "Tanya dulu apakah punya pengalaman dengan material yang dipilih.",
    }


def prepare_print_job(config=None, material="PETG", quantity=1, color=None, notes="", post_processing=None):
    """
    Full print job preparation. If config dict provided, generates files
    and returns complete order package. Otherwise returns template.
    """
    if config is None:
        return {
            "error": "No config provided",
            "usage": "Pass a config dict with: description, style, color, width, height, depth",
        }

    try:
        from cyberdeck_core import Model3dConfig, generate_print_package, export_stl
        cfg = Model3dConfig(
            config.get("description", "Cyberdeck Enclosure"),
            config.get("color", "black"),
            config.get("style", "cyberpunk"),
            float(config.get("width", 120)),
            float(config.get("height", 40)),
            float(config.get("depth", 90)),
        )
        pkg = generate_print_package(cfg, material, quantity)
        if not pkg.get("files", {}).get("stl"):
            _ = export_stl(cfg)

        model_info = pkg.get("model", {})
        model_info["filename"] = Path(pkg.get("files", {}).get("stl", "")).name or "model.stl"

        spec = generate_order_spec(model_info, material, quantity, color, notes, post_processing)
        cost = estimate_print_cost(model_info.get("volume_cc", 100), material, quantity)
        search = find_shopee_sellers(material=material)
        msg = shopee_order_message(
            model_info.get("name", "Enclosure"),
            material, quantity,
            model_info.get("volume_cc", 100),
            cost.get("total_usd"),
            post_processing,
        )

        pp_cost_idr = 0
        pp_cost_usd = 0
        if post_processing and post_processing in POST_PROCESSING_OPTIONS:
            pp = POST_PROCESSING_OPTIONS[post_processing]
            pp_cost_idr = pp["price_idr"]
            pp_cost_usd = pp["price_usd"]

        result = {
            "files": pkg.get("files", {}),
            "model": model_info,
            "print_spec": pkg.get("print_spec", {}),
            "pricing": cost,
            "post_processing": {
                "enabled": bool(post_processing and post_processing in POST_PROCESSING_OPTIONS),
                "option": post_processing,
                "details": POST_PROCESSING_OPTIONS.get(post_processing, {}) if post_processing else {},
                "cost_idr": pp_cost_idr,
                "cost_usd": pp_cost_usd,
            },
            "search": search,
            "order_specification": spec,
            "shopee_chat_message": msg,
            "print_ready": bool(pkg.get("files", {}).get("stl")),
        }
        return result
    except ImportError:
        return {"error": "cyberdeck_core not installed", "files": {}}
    except Exception as e:
        return {"error": str(e)}


HARDWARE_MODULE_OPTIONS = {
    "nato_rail_set": {
        "name": "NATO Rail Set (3x Picatinny rails + brackets)",
        "type": "mounting",
        "price_idr": 55000,
        "price_usd": 3.50,
        "description": "3x MIL-STD-1913 Picatinny rails with M4 bolts + T-nuts. Mount cameras, flashlights, antennas, or expansion modules.",
        "material": "Anodized aluminum",
        "includes": "3x 10-slot rails, 12x M4 bolts, 12x T-nuts, 4x corner brackets, hex key",
        "weight_g": 180,
        "compatible_with": ["pelican_1450", "pelican_1400", "3d_printed", "3d_printed_vented", "custom"],
    },
    "nato_accessory_bundle": {
        "name": "Deluxe NATO Rail Bundle (5 rails + corner brackets + quick-release)",
        "type": "mounting",
        "price_idr": 125000,
        "price_usd": 8.00,
        "description": "Full rail system: 5x Picatinny rails, 8x corner brackets, 2x quick-release clamps, 24x hardware kit. Wrap the entire deck in modular rails.",
        "material": "Anodized aluminum + stainless steel",
        "includes": "5x 10-slot rails, 8x corner L-brackets, 2x QD sling mounts, 24x M4 bolts + nuts, hex key set",
        "weight_g": 420,
        "compatible_with": ["3d_printed", "3d_printed_vented", "pelican_1450", "custom"],
    },
    "sliding_screen_kit": {
        "name": "Sliding Screen Mechanism (Linear rails + carriage + cable chain)",
        "type": "mechanical",
        "price_idr": 150000,
        "price_usd": 10.00,
        "description": "Complete sliding screen assembly: 2x 250mm steel linear rods + 4x linear bearings + 3D-printed screen carriage + cable management chain. Inspired by Jankbu's 2026 cyberdeck build.",
        "material": "Hardened steel rods + aluminum carriage + PETG cable chain",
        "includes": "2x 250mm Ø8mm linear rods, 4x SC8UU linear bearings, 3D-printed screen carriage (STL), 0.5m cable chain (10x10mm), M3/M4 hardware kit, rod end brackets",
        "weight_g": 350,
        "max_screen_size": "10.1 inch",
        "max_screen_weight_g": 600,
        "compatible_with": ["3d_printed", "custom"],
    },
    "sliding_screen_heavy": {
        "name": "Heavy-Duty Sliding Screen Kit (CNC aluminum carriage + linear guides)",
        "type": "mechanical",
        "price_idr": 280000,
        "price_usd": 18.00,
        "description": "Industrial-grade sliding screen: CNC-machined aluminum carriage, 4x LM8UU bearings on Ø8mm rails, IGUS energy chain for cables, locking mechanism. For heavy/large displays up to 15\".",
        "material": "CNC 6061 aluminum + hardened steel rails + IGUS polymer chain",
        "includes": "CNC aluminum carriage plate, 2x 300mm Ø8mm hardened rails, 4x LM8UU bearings, 0.8m IGUS energy chain, spring-loaded locking pin, full hardware kit, assembly jig STL",
        "weight_g": 680,
        "max_screen_size": "15.6 inch",
        "max_screen_weight_g": 1200,
        "compatible_with": ["custom", "3d_printed_vented"],
    },
    "npf_battery_sled": {
        "name": "NP-F Battery Sled (Hot-swappable, Sony camcorder batteries)",
        "type": "power",
        "price_idr": 95000,
        "price_usd": 6.00,
        "description": "NP-F series battery sled with hot-swap capability. Uses standard Sony NP-F550/F750/F970 camcorder batteries. Includes voltage display + USB-C PD output.",
        "material": "3D-printed PETG + brass terminals + PCB",
        "includes": "Battery sled housing (STL), NP-F contact terminals, 0.91\" OLED voltage display (I2C), USB-C PD trigger board (5V/9V/12V), DC barrel jack output, M3 hardware",
        "weight_g": 85,
        "output_voltage": "5V/9V/12V (selectable via USB-C PD)",
        "max_current_a": 3,
        "battery_types": ["NP-F550 (7.4V 2100mAh)", "NP-F750 (7.4V 5200mAh)", "NP-F970 (7.4V 9200mAh)"],
        "compatible_with": ["ALL"],
    },
    "npf_battery_sled_dual": {
        "name": "Dual NP-F Battery Sled (Parallel + hot-swap)",
        "type": "power",
        "price_idr": 160000,
        "price_usd": 10.00,
        "description": "Dual NP-F sled with parallel connection + ideal diode combiner. Hot-swap batteries without power cycling. Run 2x NP-F970 for 18400mAh total.",
        "material": "3D-printed PETG-CF + nickel-plated terminals + PCB",
        "includes": "Dual sled housing (STL), 2x NP-F contact sets, ideal diode OR-ing module, OLED voltage display (I2C), USB-C PD board, DC barrel jack, status LEDs, hardware",
        "weight_g": 155,
        "output_voltage": "5V/9V/12V",
        "max_current_a": 5,
        "battery_types": ["2x NP-F550", "2x NP-F750", "2x NP-F970", "Mixed (auto-switch)"],
        "compatible_with": ["ALL"],
    },
    "lilpcb_backplane": {
        "name": "Li'l PCB Backplane Board (4-slot hot-swap module carrier)",
        "type": "pcb_module",
        "price_idr": 75000,
        "price_usd": 5.00,
        "description": "Backplane PCB with 4x standardized hot-swap module slots. Each slot: I2C + 3.3V/5V power + 2x GPIO + UART. Plug in any Li'l PCB module without rewiring.",
        "material": "FR4 PCB (1.6mm, ENIG gold plating)",
        "includes": "Backplane PCB, 4x slot connectors (8-pin), power input screw terminals, I2C breakout, mounting holes, standoff kit",
        "weight_g": 45,
        "slot_count": 4,
        "slot_interface": "I2C + 3.3V + 5V + 2x GPIO + UART",
        "pcb_dimensions_mm": "80x60x1.6",
        "module_size_mm": "30x25 (standard Li'l PCB format)",
        "compatible_with": ["ALL"],
    },
    "lilpcb_sdr_module": {
        "name": "Li'l PCB SDR Module (RTL-SDR on a stick)",
        "type": "pcb_module",
        "price_idr": 120000,
        "price_usd": 8.00,
        "description": "RTL-SDR (R820T2 + RTL2832U) on the Li'l PCB form factor. 24MHz-1766MHz receiver with SMA connector. Plugs directly into backplane.",
        "material": "FR4 PCB + aluminum shield",
        "includes": "Li'l PCB SDR module, SMA antenna connector, telescopic antenna (15cm), I2C control interface",
        "weight_g": 25,
        "frequency_range": "24MHz - 1766MHz",
        "bandwidth_msps": 2.4,
        "antenna": "SMA + included telescopic",
        "compatible_with": ["lilpcb_backplane"],
    },
    "lilpcb_lora_module": {
        "name": "Li'l PCB LoRa Module (SX1262 + Meshtastic)",
        "type": "pcb_module",
        "price_idr": 85000,
        "price_usd": 5.50,
        "description": "SX1262 LoRa transceiver on Li'l PCB format. Runs Meshtastic firmware. 868/915MHz, 5-15km range. SMA antenna + U.FL connector.",
        "material": "FR4 PCB + RF shielding",
        "includes": "Li'l PCB LoRa module, SMA antenna connector, 1/4 wave whip antenna, Meshtastic pre-flashed",
        "weight_g": 18,
        "frequency": "868/915MHz",
        "range_km": "5-15",
        "protocol": "LoRa + Meshtastic",
        "compatible_with": ["lilpcb_backplane"],
    },
    "lilpcb_gps_module": {
        "name": "Li'l PCB GPS/GNSS Module (NEO-6M / ublox)",
        "type": "pcb_module",
        "price_idr": 65000,
        "price_usd": 4.00,
        "description": "ublox GPS + GLONASS receiver on Li'l PCB. 72-channel, -167dBm tracking. UART output at 9600 baud. Backup battery for fast lock.",
        "material": "FR4 PCB",
        "includes": "Li'l PCB GPS module, active GPS antenna (patch), CR1220 backup battery holder",
        "weight_g": 15,
        "channels": 72,
        "sensitivity_dbm": -167,
        "protocol": "NMEA 0183 @ 9600 baud",
        "compatible_with": ["lilpcb_backplane"],
    },
    "lilpcb_nvme_module": {
        "name": "Li'l PCB NVMe Adapter Module (M.2 2242)",
        "type": "pcb_module",
        "price_idr": 110000,
        "price_usd": 7.00,
        "description": "M.2 NVMe SSD adapter on Li'l PCB format. PCIe 3.0 x1 via FPC cable to SBC. Adds 1TB+ storage in a hot-swappable module.",
        "material": "FR4 PCB + M.2 connector",
        "includes": "Li'l PCB NVMe adapter, M.2 2242 connector, FPC PCIe cable (10cm), mounting screws",
        "weight_g": 12,
        "interface": "PCIe 3.0 x1 via FPC",
        "max_ssd_size": "2TB M.2 2242 NVMe",
        "compatible_with": ["lilpcb_backplane"],
    },
    "lilpcb_env_sensor": {
        "name": "Li'l PCB Environmental Sensor Pack (BME280 + SGP40 + BH1750)",
        "type": "pcb_module",
        "price_idr": 55000,
        "price_usd": 3.50,
        "description": "Triple environmental sensors on one Li'l PCB: BME280 (temp/humidity/pressure), SGP40 (VOC air quality), BH1750 (ambient light). All via I2C.",
        "material": "FR4 PCB",
        "includes": "Li'l PCB sensor module, I2C address jumpers",
        "weight_g": 10,
        "sensors": ["BME280 (-40-85C, 0-100%RH)", "SGP40 (VOC index 0-1000)", "BH1750 (1-65535 lux)"],
        "interface": "I2C (0x76, 0x59, 0x23)",
        "compatible_with": ["lilpcb_backplane"],
    },
}


__all__ = [
    "shopee_search_url", "generate_order_spec", "shopee_order_message",
    "estimate_print_cost", "find_shopee_sellers", "prepare_print_job",
    "MATERIAL_OPTIONS", "POST_PROCESSING_OPTIONS", "HARDWARE_MODULE_OPTIONS", "PRINTS_DIR",
]
