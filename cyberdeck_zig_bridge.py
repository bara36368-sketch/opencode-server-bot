"""
cyberdeck_zig_bridge.py — Zig-Python ctypes bridge for Cyberdeck Agent.
Loads cyberdeck_zig.dll for computation kernels (geometry, battery,
antenna, mesh, power, heat). Falls back to None on failure.
"""
import json
import logging
import os
from ctypes import CDLL, POINTER, c_char_p, c_double, c_int32, c_int64, c_bool

_log = logging.getLogger(__name__)

_dll_path = os.path.join(os.path.dirname(__file__), "zig", "cyberdeck_zig.dll")

_ZIG = None

def _load():
    global _ZIG
    if _ZIG is not None:
        return True
    if not os.path.isfile(_dll_path):
        _log.warning("Zig DLL not found at %s", _dll_path)
        return False
    try:
        lib = CDLL(_dll_path)
        _wire_fn(lib, "zig_nato_rail_layout", [c_int32, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_battery_capacity", [c_int32, c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_battery_optimizer", [c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_antenna_calc", [c_double], c_char_p)
        _wire_fn(lib, "zig_mesh_range", [c_int32, c_double, c_double, c_int32], c_char_p)
        _wire_fn(lib, "zig_print_cost", [c_double, c_double, c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_filament_calc", [c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_sliding_screen_rail", [c_double, c_double, c_double, c_int32], c_char_p)
        _wire_fn(lib, "zig_esp32_power", [c_int32, c_int32, c_int32, c_double], c_char_p)
        _wire_fn(lib, "zig_throughput_est", [c_char_p, c_int32, c_int32], c_char_p)
        _wire_fn(lib, "zig_edge_ai_est", [c_char_p, c_int32, c_int32], c_char_p)
        _wire_fn(lib, "zig_heat_sink_calc", [c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_solar_sizer", [c_double, c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "zig_cable_sizer", [c_double, c_double, c_double, c_double], c_char_p)
        _wire_fn(lib, "cyberdeck_free_string", [c_char_p], None)
        _ZIG = lib
        _log.info("Zig DLL loaded from %s", _dll_path)
        return True
    except Exception as exc:
        _log.warning("Failed to load Zig DLL: %s", exc)
        return False

def _wire_fn(lib, name, argtypes, restype):
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    return fn

def _call(name, *args):
    if not _load():
        return None
    try:
        fn = getattr(_ZIG, name)
        result_ptr = fn(*args)
        if not result_ptr:
            return None
        result = result_ptr.decode("utf-8")
        _ZIG.cyberdeck_free_string(result_ptr)
        return json.loads(result)
    except Exception as exc:
        _log.warning("Zig %s failed: %s", name, exc)
        return None


def nato_rail_layout(rails, deck_width_mm, deck_depth_mm=150.0):
    return _call("zig_nato_rail_layout", rails, deck_width_mm, deck_depth_mm)

def battery_capacity(cells, mah_per_cell=3500.0, voltage=3.7, load_watts=10.0):
    return _call("zig_battery_capacity", cells, mah_per_cell, voltage, load_watts)

def battery_optimizer(target_wh, cell_mah=3500.0, cell_voltage=3.7):
    return _call("zig_battery_optimizer", target_wh, cell_mah, cell_voltage)

def antenna_calc(freq_mhz):
    return _call("zig_antenna_calc", freq_mhz)

def mesh_range(power_dbm=20, freq_mhz=915.0, gain_dbi=3.0, sensitivity_dbm=-120):
    return _call("zig_mesh_range", power_dbm, freq_mhz, gain_dbi, sensitivity_dbm)

def print_cost(volume_cm3, material_price_per_g=1.5, density_g_per_cm3=1.24, print_hours=6.0, labor_per_hour=25000.0):
    return _call("zig_print_cost", volume_cm3, material_price_per_g, density_g_per_cm3, print_hours, labor_per_hour)

def filament_calc(spool_grams=1000.0, density=1.24, diameter_mm=1.75):
    return _call("zig_filament_calc", spool_grams, density, diameter_mm)

def sliding_screen_rail(screen_width_mm, screen_depth_mm, rail_length_mm, carriage_count=4):
    return _call("zig_sliding_screen_rail", screen_width_mm, screen_depth_mm, rail_length_mm, carriage_count)

def esp32_power(wifi_active=1, cpu_mhz=240, ble_enabled=1, peripherals_ma=20.0):
    return _call("zig_esp32_power", wifi_active, cpu_mhz, ble_enabled, peripherals_ma)

def throughput_est(protocol="lora", nodes=5, hops=2):
    return _call("zig_throughput_est", protocol.encode(), nodes, hops)

def edge_ai_est(model_type="vision", ram_kb=512, psram_kb=8192):
    return _call("zig_edge_ai_est", model_type.encode(), ram_kb, psram_kb)

def heat_sink_calc(power_watts, ambient_c=25.0, max_temp_c=85.0):
    return _call("zig_heat_sink_calc", power_watts, ambient_c, max_temp_c)

def solar_sizer(power_wh_per_day, sun_hours=5.0, panel_efficiency=0.8, battery_voltage=12.0):
    return _call("zig_solar_sizer", power_wh_per_day, sun_hours, panel_efficiency, battery_voltage)

def cable_sizer(current_a, length_m=2.0, max_drop_pct=3.0, voltage=12.0):
    return _call("zig_cable_sizer", current_a, length_m, max_drop_pct, voltage)


HAS_ZIG = _load()

__all__ = [
    "HAS_ZIG", "nato_rail_layout", "battery_capacity", "battery_optimizer",
    "antenna_calc", "mesh_range", "print_cost", "filament_calc",
    "sliding_screen_rail", "esp32_power", "throughput_est",
    "edge_ai_est", "heat_sink_calc",
    "solar_sizer", "cable_sizer",
]
