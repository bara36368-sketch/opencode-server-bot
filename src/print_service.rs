use pyo3::prelude::*;
use pyo3::types::{PyDict, PyDictMethods};
use std::path::PathBuf;
use std::process::Command;
use std::fs;

use crate::model3d::generate_openscad;
use crate::types::Model3dConfig;

static PRINTS_DIR: &str = "cyberdeck_prints";

fn approx_print_volume_cc(w: f64, h: f64, d: f64) -> f64 {
    let wall = 2.0;
    let outer_vol = w * h * d;
    let inner_w = (w - wall * 2.0).max(0.1);
    let inner_h = (h - wall * 2.0).max(0.1);
    let inner_d = (d - wall * 2.0).max(0.1);
    let shell_vol = outer_vol - inner_w * inner_h * inner_d;
    let void_vol = inner_w * inner_h * inner_d;
    let infill = 0.15;
    (shell_vol + void_vol * infill) / 1000.0
}

fn get_print_hours(vol_cc: f64) -> f64 {
    // ~15cc/hr at 0.2mm, 60mm/s, with acceleration overhead
    (vol_cc / 15.0 * 1.3).max(1.0)
}
fn ensure_dir() -> std::io::Result<()> {
    fs::create_dir_all(PRINTS_DIR)
}

fn safe_name(s: &str) -> String {
    s.chars().map(|c| if c.is_alphanumeric() || c == '-' || c == '_' { c } else { '_' }).collect()
}

pub fn export_scad(py: Python, config: &Model3dConfig) -> PyResult<Py<PyDict>> {
    ensure_dir().map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Cannot create prints dir: {}", e)))?;

    let name = safe_name(&config.description);
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs();
    let filename = format!("{}_{}_{}", name, config.style, timestamp);
    let scad_path = PathBuf::from(PRINTS_DIR).join(format!("{}.scad", filename));

    let openscad = generate_openscad(config);
    fs::write(&scad_path, &openscad)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Cannot write SCAD: {}", e)))?;

    let d = PyDict::new(py);
    d.set_item("scad_path", scad_path.to_string_lossy().to_string())?;
    d.set_item("filename", format!("{}.scad", filename))?;
    d.set_item("style", &config.style)?;
    d.set_item("color", &config.color)?;
    d.set_item("width_mm", config.width)?;
    d.set_item("height_mm", config.height)?;
    d.set_item("depth_mm", config.depth)?;
    let vol = approx_print_volume_cc(config.width, config.height, config.depth);
    let bounded_vol = config.width * config.height * config.depth / 1000.0;
    d.set_item("volume_cc", vol)?;
    d.set_item("bounding_volume_cc", bounded_vol)?;
    d.set_item("stl_path", "")?;
    d.set_item("openscad_source", &openscad)?;
    Ok(d.into())
}

pub fn export_stl(py: Python, config: &Model3dConfig) -> PyResult<Py<PyDict>> {
    let result = export_scad(py, config)?;

    let scad_path_str: String = result.bind(py).get_item("scad_path")
        .ok().flatten().and_then(|x| x.extract::<String>().ok())
        .unwrap_or_default();

    if scad_path_str.is_empty() {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("No SCAD file generated"));
    }

    let scad_path = PathBuf::from(&scad_path_str);
    let stl_path = scad_path.with_extension("stl");

    let openscad_cmd = if cfg!(target_os = "windows") { "openscad.com" } else { "openscad" };

    match Command::new(openscad_cmd)
        .arg("-o").arg(&stl_path).arg(&scad_path)
        .output()
    {
        Ok(output) if output.status.success() => {
            result.bind(py).set_item("stl_path", stl_path.to_string_lossy().to_string())?;
            let size_kb = fs::metadata(&stl_path).map(|m| m.len() as f64 / 1024.0).unwrap_or(0.0);
            result.bind(py).set_item("stl_size_kb", format!("{:.1}", size_kb))?;
        }
        Ok(output) => {
            let stderr = String::from_utf8_lossy(&output.stderr);
            result.bind(py).set_item("stl_warning", format!("OpenSCAD export failed: {}", stderr))?;
        }
        Err(e) => {
            result.bind(py).set_item("stl_warning",
                format!("OpenSCAD CLI not available. STL file not generated. Install OpenSCAD or use .scad directly. Error: {}", e))?;
        }
    }

    Ok(result)
}

pub fn generate_print_package(py: Python, config: &Model3dConfig, material: &str, quantity: u32) -> PyResult<Py<PyDict>> {
    ensure_dir().map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e))?;

    let name = safe_name(&config.description);
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs();
    let base = format!("{}_{}_{}", name, config.style, timestamp);
    let scad_path = PathBuf::from(PRINTS_DIR).join(format!("{}.scad", base));
    let stl_path = PathBuf::from(PRINTS_DIR).join(format!("{}.stl", base));

    let openscad = generate_openscad(config);
    fs::write(&scad_path, &openscad)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e))?;

    let vol_cc = approx_print_volume_cc(config.width, config.height, config.depth);
    let per_unit_filament_g = vol_cc * 1.24;
    let total_filament_g = per_unit_filament_g * quantity as f64;

    let openscad_cmd = if cfg!(target_os = "windows") { "openscad.com" } else { "openscad" };
    let stl_ok = Command::new(openscad_cmd)
        .arg("-o").arg(&stl_path).arg(&scad_path)
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false);

    let result = PyDict::new(py);

    let files = PyDict::new(py);
    files.set_item("scad", scad_path.to_string_lossy().to_string())?;
    files.set_item("stl", if stl_ok { stl_path.to_string_lossy().to_string() } else { "".into() })?;
    files.set_item("stl_exported", stl_ok)?;
    result.set_item("files", files)?;

    let model_info = PyDict::new(py);
    model_info.set_item("name", &config.description)?;
    model_info.set_item("style", &config.style)?;
    model_info.set_item("color_scheme", &config.color)?;
    model_info.set_item("dimensions_mm", format!("{:.0}×{:.0}×{:.0}", config.width, config.height, config.depth))?;
    model_info.set_item("volume_cc", (vol_cc * 10.0).round() / 10.0)?;
    model_info.set_item("bounding_volume_cc", (config.width * config.height * config.depth / 1000.0 * 10.0).round() / 10.0)?;
    model_info.set_item("estimated_filament_g", (total_filament_g * 10.0).round() / 10.0)?;
    model_info.set_item("filament_per_unit_g", (per_unit_filament_g * 10.0).round() / 10.0)?;
    model_info.set_item("quantity", quantity)?;
    model_info.set_item("build_plate_area_mm", format!("{:.0}×{:.0}", config.width, config.depth))?;
    result.set_item("model", model_info)?;

    let spec = PyDict::new(py);
    spec.set_item("material", material)?;
    spec.set_item("layer_height_mm", 0.2)?;
    spec.set_item("infill_percent", 15)?;
    spec.set_item("perimeters", 3)?;
    spec.set_item("supports", "Auto — only for display bezel overhang (>45°)")?;
    spec.set_item("quantity", quantity)?;
    spec.set_item("orientation", "Lid facing up. Body with interior facing up.")?;
    let finish = match config.style.as_str() {
        "steampunk" => "Bronze/copper filament. Optional: rub with graphite powder.",
        "cyberpunk" => "Black PETG + neon accents. UV reactive clear coat optional.",
        "futuristic" => "White/translucent PETG. Optional: sand to 400 grit + matte clear coat.",
        "industrial" => "Orange/black PETG. Vibration-dampening feet recommended.",
        "minimal" => "White PLA or PETG. Sand smooth + matte clear coat.",
        "retro" => "Beige PLA. Acetone vapor smooth (ABS only).",
        _ => "Standard finish. Sand mating surfaces.",
    };
    spec.set_item("finish_recommendation", finish)?;
    result.set_item("print_spec", spec)?;

    let material_cost_per_g = match material {
        "PLA" => 0.03, "PETG" => 0.04, "ABS" => 0.04,
        "ASA" => 0.06, "TPU" => 0.07, "Nylon" => 0.08,
        "Polycarbonate" => 0.10, "Carbon Fiber PETG" => 0.12,
        "Resin" => 0.15, _ => 0.05,
    };
    let material_cost = total_filament_g * material_cost_per_g;
    let print_time_h = get_print_hours(vol_cc) * quantity as f64;
    let service_cost = print_time_h * 1.50;
    let shipping = 3.50;
    let total = material_cost + service_cost + shipping;

    let pricing = PyDict::new(py);
    pricing.set_item("material_estimate_usd", (material_cost * 100.0).round() / 100.0)?;
    pricing.set_item("service_estimate_usd", (service_cost * 100.0).round() / 100.0)?;
    pricing.set_item("shipping_estimate_usd", shipping)?;
    pricing.set_item("total_estimate_usd", (total * 100.0).round() / 100.0)?;
    pricing.set_item("estimated_print_hours", (print_time_h * 10.0).round() / 10.0)?;
    pricing.set_item("note", "Estimates only. Actual cost depends on seller and location.")?;
    result.set_item("pricing", pricing)?;

    Ok(result.into())
}
