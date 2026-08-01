"""
cyberdeck_bridge.py — Three-tier Rust/Zig/Python bridge for Cyberdeck Agent.
Tier 1: cyberdeck_core (Rust via PyO3)
Tier 2: cyberdeck_zig (Zig via ctypes)
Tier 3: pure Python fallback (caller level)
"""
import logging

try:
    import cyberdeck_core as _cc
    HAS_RUST = True
except ImportError:
    HAS_RUST = False

try:
    from cyberdeck_zig_bridge import (
        HAS_ZIG,
        nato_rail_layout as _zig_nato,
        battery_capacity as _zig_battery,
        battery_optimizer as _zig_batt_opt,
        antenna_calc as _zig_antenna,
        mesh_range as _zig_mesh,
        print_cost as _zig_print,
        filament_calc as _zig_filament,
        sliding_screen_rail as _zig_sliding,
        esp32_power as _zig_esp32,
        throughput_est as _zig_throughput,
        edge_ai_est as _zig_edge_ai,
        heat_sink_calc as _zig_heat,
        solar_sizer as _zig_solar,
        cable_sizer as _zig_cable,
    )
except ImportError:
    HAS_ZIG = False
    _zig_nato = _zig_battery = _zig_batt_opt = None
    _zig_antenna = _zig_mesh = _zig_print = None
    _zig_filament = _zig_sliding = _zig_esp32 = None
    _zig_throughput = _zig_edge_ai = _zig_heat = None
    _zig_solar = _zig_cable = None


def check_compatibility(components):
    if HAS_RUST:
        try: return _cc.check_compatibility(components)
        except Exception: pass
    return None

def audit_build(components_data):
    if HAS_RUST:
        try: return _cc.audit_build(components_data)
        except Exception: pass
    return None

def auto_fix(components, issues):
    if HAS_RUST:
        try: return _cc.auto_fix(components, issues)
        except Exception: pass
    return None

def suggest_upgrades(build_data):
    if HAS_RUST:
        try: return _cc.suggest_upgrades(build_data)
        except Exception: pass
    return None

def generate_3d_model(description, color="black", style="cyberpunk", width=120, height=40, depth=90):
    if HAS_RUST:
        try: return _cc.generate_3d_model(description, color, style, width, height, depth)
        except Exception: pass
    return None

def calculate_battery_life(capacity_mah, voltage=3.7, load_watts=5.0):
    if HAS_ZIG and _zig_battery:
        try: return _zig_battery(1, capacity_mah, voltage, load_watts)
        except Exception: pass
    if HAS_RUST:
        try: return _cc.calculate_battery_life(capacity_mah, voltage, load_watts)
        except Exception: pass
    return None

def calculate_antenna(freq_mhz):
    if HAS_ZIG and _zig_antenna:
        try: return _zig_antenna(freq_mhz)
        except Exception: pass
    if HAS_RUST:
        try: return _cc.calculate_antenna(freq_mhz)
        except Exception: pass
    return None

def bom_generate(component_list):
    if HAS_RUST:
        try: return _cc.bom_generate(component_list)
        except Exception: pass
    return None

def search_components(database, query):
    if HAS_RUST:
        try: return _cc.search_components(database, query)
        except Exception: pass
    return None

def generate_cable_plan(components_dict):
    if HAS_RUST:
        try: return _cc.generate_cable_plan(components_dict)
        except Exception: pass
    return None

def category_requirements():
    if HAS_RUST:
        try: return _cc.category_requirements()
        except Exception: pass
    return None

def compute_stack_path(category, current_sbc=None, budget=None):
    if HAS_RUST:
        try: return _cc.compute_stack_path(category, current_sbc, budget)
        except Exception: pass
    return None

def compute_score(components):
    if HAS_RUST:
        try: return _cc.compute_score(components)
        except Exception: pass
    return None

def export_scad(description, color="black", style="cyberpunk", width=120, height=40, depth=90):
    if HAS_RUST:
        try:
            cfg = _cc.Model3dConfig(description, color, style, width, height, depth)
            return _cc.export_scad(cfg)
        except Exception: pass
    return None

def export_stl(description, color="black", style="cyberpunk", width=120, height=40, depth=90):
    if HAS_RUST:
        try:
            cfg = _cc.Model3dConfig(description, color, style, width, height, depth)
            return _cc.export_stl(cfg)
        except Exception: pass
    return None

def generate_print_package(description, material="PETG", quantity=1, color="black", style="cyberpunk", width=120, height=40, depth=90):
    if HAS_RUST:
        try:
            cfg = _cc.Model3dConfig(description, color, style, width, height, depth)
            return _cc.generate_print_package(cfg, material, quantity)
        except Exception: pass
    return None

def solar_sizer(power_wh_per_day, sun_hours=5.0, panel_efficiency=0.8, battery_voltage=12.0):
    if HAS_ZIG and _zig_solar:
        try: return _zig_solar(power_wh_per_day, sun_hours, panel_efficiency, battery_voltage)
        except Exception: pass
    return None

def cable_sizer(current_a, length_m=2.0, max_drop_pct=3.0, voltage=12.0):
    if HAS_ZIG and _zig_cable:
        try: return _zig_cable(current_a, length_m, max_drop_pct, voltage)
        except Exception: pass
    return None

def nato_rail_layout(rails, deck_width_mm, deck_depth_mm=150.0):
    if HAS_ZIG and _zig_nato:
        try: return _zig_nato(rails, deck_width_mm, deck_depth_mm)
        except Exception: pass
    return None

def mesh_range(power_dbm=20, freq_mhz=915.0, gain_dbi=3.0, sensitivity_dbm=-120):
    if HAS_ZIG and _zig_mesh:
        try: return _zig_mesh(power_dbm, freq_mhz, gain_dbi, sensitivity_dbm)
        except Exception: pass
    return None

def print_cost(volume_cm3, material_price_per_g=1.5, density_g_per_cm3=1.24, print_hours=6.0, labor_per_hour=25000.0):
    if HAS_ZIG and _zig_print:
        try: return _zig_print(volume_cm3, material_price_per_g, density_g_per_cm3, print_hours, labor_per_hour)
        except Exception: pass
    return None

def heat_sink_calc(power_watts, ambient_c=25.0, max_temp_c=85.0):
    if HAS_ZIG and _zig_heat:
        try: return _zig_heat(power_watts, ambient_c, max_temp_c)
        except Exception: pass
    return None

__all__ = [
    "HAS_RUST", "HAS_ZIG",
    "check_compatibility", "audit_build", "auto_fix",
    "suggest_upgrades", "generate_3d_model", "calculate_battery_life",
    "calculate_antenna", "bom_generate", "search_components",
    "generate_cable_plan", "category_requirements",
    "compute_stack_path", "compute_score",
    "export_scad", "export_stl", "generate_print_package",
    "solar_sizer", "cable_sizer", "nato_rail_layout",
    "mesh_range", "print_cost", "heat_sink_calc",
]
