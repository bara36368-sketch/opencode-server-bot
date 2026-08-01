use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyAny, PyDictMethods, PyListMethods, PyAnyMethods};

mod types;
mod compat;
mod model3d;
mod print_service;

use types::{BuildAudit, Model3dConfig, extract_str, extract_f64};
use compat::{check_sbc_display, check_sbc_power, check_sbc_enclosure,
             check_connectivity, check_storage, check_thermal,
             audit_build, auto_fix, suggest_upgrades};
use model3d::{generate_openscad, generate_3d_json};
use print_service::{export_scad, export_stl, generate_print_package};

#[pyfunction]
#[pyo3(name = "check_compatibility")]
fn py_check_compatibility(py: Python, components: &Bound<'_, PyDict>) -> PyResult<Py<PyDict>> {
    let mut all_issues: Vec<String> = Vec::new();
    let mut checks: Vec<String> = Vec::new();

    if let (Some(sbc), Some(display)) = (
        components.get_item("sbc").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
        components.get_item("display").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
    ) {
        let (_, issues) = check_sbc_display(&sbc.bind(py), &display.bind(py));
        all_issues.extend(issues);
        checks.push("sbc_display".into());
    }

    if let (Some(sbc), Some(power)) = (
        components.get_item("sbc").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
        components.get_item("power").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
    ) {
        let (_, issues) = check_sbc_power(&sbc.bind(py), &power.bind(py));
        all_issues.extend(issues);
        checks.push("sbc_power".into());
    }

    if let (Some(sbc), Some(enclosure)) = (
        components.get_item("sbc").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
        components.get_item("enclosure").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
    ) {
        let (_, issues) = check_sbc_enclosure(&sbc.bind(py), &enclosure.bind(py));
        all_issues.extend(issues);
        checks.push("sbc_enclosure".into());
    }

    if let (Some(sbc), Some(storage)) = (
        components.get_item("sbc").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
        components.get_item("storage").ok().flatten().and_then(|x| x.extract::<Py<PyDict>>().ok()),
    ) {
        let (_, issues) = check_storage(&sbc.bind(py), &storage.bind(py));
        all_issues.extend(issues);
        checks.push("storage".into());
    }

    let (_, conn_issues) = check_connectivity(components, py);
    all_issues.extend(conn_issues);
    checks.push("connectivity".into());

    // Thermal check
    if let Some(sbc) = components.get_item("sbc").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let cooling = components.get_item("cooling").ok().flatten()
            .and_then(|x| x.extract::<Py<PyDict>>().ok())
            .map(|d| d.bind(py).clone());
        let t_issues = check_thermal(&sbc, cooling.as_ref());
        all_issues.extend(t_issues);
        checks.push("thermal".into());
    }

    let result = PyDict::new(py);
    result.set_item("compatible", all_issues.is_empty())?;
    result.set_item("issues", all_issues)?;
    result.set_item("checks_performed", checks)?;
    Ok(result.into())
}

#[pyfunction]
#[pyo3(name = "audit_build")]
fn py_audit_build(py: Python, components: &Bound<'_, PyAny>) -> PyResult<Py<PyDict>> {
    let (flaws, fixes) = audit_build(components, py)?;
    let total = flaws.len() as u32;
    let critical_high = flaws.iter().filter(|f| f.severity == "critical" || f.severity == "high").count();
    let score = (100u8).saturating_sub((total as u8).saturating_mul(10)).max(50);
    let audit = BuildAudit::new(total, flaws, fixes, score, critical_high == 0);
    audit.to_dict(py)
}

#[pyfunction]
#[pyo3(name = "auto_fix")]
fn py_auto_fix(py: Python, components: &Bound<'_, PyDict>, issues: Vec<String>) -> PyResult<Vec<Py<PyDict>>> {
    auto_fix(components, issues, py)
}

#[pyfunction]
#[pyo3(name = "suggest_upgrades")]
fn py_suggest_upgrades(py: Python, components: &Bound<'_, PyDict>) -> PyResult<Vec<Py<PyDict>>> {
    suggest_upgrades(components, py)
}

#[pyfunction]
#[pyo3(name = "generate_3d_model")]
fn py_generate_3d(py: Python, desc: String, color: String, style: String,
                   width: f64, height: f64, depth: f64) -> PyResult<Py<PyDict>> {
    let config = Model3dConfig::new(desc, color, style, width.max(60.0), height.max(35.0), depth.max(60.0));
    let scad = generate_openscad(&config);
    let result = PyDict::new(py);
    result.set_item("openscad", scad)?;
    result.set_item("style", &config.style)?;
    result.set_item("color", &config.color)?;

    let metadata = PyDict::new(py);
    metadata.set_item("width_mm", config.width)?;
    metadata.set_item("height_mm", config.height)?;
    metadata.set_item("depth_mm", config.depth)?;
    let vol = config.width * config.height * config.depth / 1000.0;
    metadata.set_item("volume_cc", vol)?;
    metadata.set_item("estimated_print_time_minutes", (vol * 3.0) as u32)?;
    result.set_item("metadata", metadata)?;
    Ok(result.into())
}

#[pyfunction]
#[pyo3(name = "generate_3d_from_config")]
fn py_generate_3d_from(py: Python, config: &Bound<'_, Model3dConfig>) -> PyResult<Py<PyDict>> {
    let c = config.borrow();
    generate_3d_json(&c, py)
}

#[pyfunction]
#[pyo3(name = "bom_generate")]
fn py_bom_generate(py: Python, components: &Bound<'_, PyList>) -> PyResult<Py<PyDict>> {
    let mut subtotal: f64 = 0.0;
    let mut items: Vec<Py<PyDict>> = Vec::new();

    for comp in components.iter() {
        if let Ok(d) = comp.cast::<PyDict>() {
            let name = extract_str(d, "name").unwrap_or_default();
            let price = extract_f64(d, "price")
                .or_else(|| extract_f64(d, "price_num"))
                .unwrap_or(0.0);
            let qty = d.get_item("qty").ok().flatten()
                .or_else(|| d.get_item("quantity").ok().flatten())
                .and_then(|x| x.extract::<u32>().ok()).unwrap_or(1);
            let url = extract_str(d, "url").or_else(|| extract_str(d, "source")).unwrap_or_default();

            subtotal += price * qty as f64;
            let item = PyDict::new(py);
            item.set_item("name", &name)?;
            item.set_item("qty", qty)?;
            item.set_item("unit_price", price)?;
            item.set_item("total_price", price * qty as f64)?;
            item.set_item("url", &url)?;
            items.push(item.into());
        }
    }

    let shipping = if subtotal > 100.0 { 0.0 } else { subtotal * 0.08 }.max(5.99);
    let tax = subtotal * 0.08;
    let total = subtotal + shipping + tax;

    let result = PyDict::new(py);
    let count = items.len();
    result.set_item("items", items)?;
    result.set_item("subtotal", (subtotal * 100.0).round() / 100.0)?;
    result.set_item("shipping", (shipping * 100.0).round() / 100.0)?;
    result.set_item("tax", (tax * 100.0).round() / 100.0)?;
    result.set_item("total", (total * 100.0).round() / 100.0)?;
    result.set_item("currency", "USD")?;

    let summary = PyDict::new(py);
    summary.set_item("component_count", count)?;
    summary.set_item("subtotal", (subtotal * 100.0).round() / 100.0)?;
    summary.set_item("shipping_estimate", (shipping * 100.0).round() / 100.0)?;
    summary.set_item("tax_estimate", (tax * 100.0).round() / 100.0)?;
    summary.set_item("grand_total", (total * 100.0).round() / 100.0)?;
    result.set_item("summary", summary)?;

    Ok(result.into())
}

#[pyfunction]
#[pyo3(name = "search_components")]
fn py_search(py: Python, database: &Bound<'_, PyDict>, query: String) -> PyResult<Vec<Py<PyDict>>> {
    let q = query.to_lowercase();
    let mut results: Vec<Py<PyDict>> = Vec::new();

    let keys: Vec<String> = database.keys().into_iter().filter_map(|k| k.extract::<String>().ok()).collect();
    for id_str in keys {
        if let Some(val) = database.get_item(&id_str).ok().flatten() {
            if let Ok(d) = val.cast::<PyDict>() {
                let name = extract_str(&d, "name").unwrap_or_default();
                let tags = extract_str(&d, "tags").or_else(|| extract_str(&d, "keywords")).unwrap_or_default();
                let desc = extract_str(&d, "description").or_else(|| extract_str(&d, "desc")).unwrap_or_default();
                if name.to_lowercase().contains(&q) || id_str.to_lowercase().contains(&q)
                    || tags.to_lowercase().contains(&q) || desc.to_lowercase().contains(&q)
                {
                    let r = PyDict::new(py);
                    r.set_item("id", &id_str)?;
                    let sub_keys: Vec<String> = d.keys().into_iter().filter_map(|k| k.extract::<String>().ok()).collect();
                    for sk in sub_keys {
                        if let Ok(Some(sv)) = d.get_item(&sk) {
                            let _ = r.set_item(&sk, sv);
                        }
                    }
                    results.push(r.into());
                }
            }
        }
    }
    // Sort by relevance — exact name match first
    results.sort_by(|a, b| {
        let a_id = a.bind(py).get_item("id").ok().flatten()
            .and_then(|x| x.extract::<String>().ok()).unwrap_or_default();
        let b_id = b.bind(py).get_item("id").ok().flatten()
            .and_then(|x| x.extract::<String>().ok()).unwrap_or_default();
        let a_exact = a_id.to_lowercase() == q;
        let b_exact = b_id.to_lowercase() == q;
        b_exact.cmp(&a_exact)
    });
    Ok(results)
}

#[pyfunction]
#[pyo3(name = "generate_cable_plan")]
fn py_cable_plan(py: Python, components: &Bound<'_, PyDict>) -> PyResult<Vec<Py<PyDict>>> {
    let mut cables: Vec<Py<PyDict>> = Vec::new();

    if let Some(display) = components.get_item("display").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let iface = extract_str(&display, "interface").unwrap_or_default().to_lowercase();
        let touch: bool = display.get_item("touch").ok().flatten()
            .and_then(|x| x.extract::<bool>().ok()).unwrap_or(false);

        if iface.starts_with("hdmi") {
            let c = PyDict::new(py);
            c.set_item("cable", "HDMI cable (micro-HDMI to HDMI or ribbon)")?;
            c.set_item("route", "SBC HDMI -> display")?;
            c.set_item("length", "15-30cm")?;
            c.set_item("gauge", "30AWG ribbon recommended for flexibility")?;
            c.set_item("management", "Route along enclosure wall, avoid 90-degree bends, use clip")?;
            cables.push(c.into());
        }
        if iface.starts_with("dsi") {
            let c = PyDict::new(py);
            c.set_item("cable", "DSI ribbon cable (15-pin FPC, 0.5mm pitch)")?;
            c.set_item("route", "SBC DSI -> display FPC connector")?;
            c.set_item("length", "20-40cm")?;
            c.set_item("gauge", "0.5mm pitch FPC")?;
            c.set_item("management", "Keep flat and uncreased, route along enclosure bottom")?;
            cables.push(c.into());
        }
        if touch {
            let c = PyDict::new(py);
            c.set_item("cable", "USB-C touch cable (or USB-A if no C port)")?;
            c.set_item("route", "Display touch USB -> SBC USB port")?;
            c.set_item("length", "15-25cm")?;
            c.set_item("management", "Bundle with display cable using spiral wrap")?;
            cables.push(c.into());
        }
    }

    if let Some(keyboard) = components.get_item("keyboard").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let conn = extract_str(&keyboard, "connection").unwrap_or_default();
        let kb_name = extract_str(&keyboard, "name").unwrap_or_default();
        if conn.contains("USB") {
            let c = PyDict::new(py);
            c.set_item("cable", format!("USB cable ({conn})"))?;
            c.set_item("route", format!("{} -> SBC USB port", kb_name))?;
            c.set_item("length", "20-50cm")?;
            c.set_item("gauge", "24/28AWG USB cable")?;
            c.set_item("management", "Allow slack for typing, route through grommet, coil excess")?;
            cables.push(c.into());
        } else if conn.contains("BT") || conn.contains("Bluetooth") {
            // Wireless — no cable needed
        } else {
            let c = PyDict::new(py);
            c.set_item("cable", format!("{} data cable", conn))?;
            c.set_item("route", format!("{} -> SBC", kb_name))?;
            c.set_item("length", "20-40cm")?;
            c.set_item("management", "Route along enclosure edge")?;
            cables.push(c.into());
        }
    }

    if let Some(power) = components.get_item("power").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let ptype = extract_str(&power, "type").unwrap_or_default();
        let pout = extract_str(&power, "output").unwrap_or_default();
        let pname = extract_str(&power, "name").unwrap_or_default();
        if ptype.contains("UPS HAT") {
            let c = PyDict::new(py);
            c.set_item("cable", "GPIO power connection (stacked via 40-pin header)")?;
            c.set_item("route", format!("{} -> SBC GPIO header (stacked)", pname))?;
            c.set_item("length", "0cm (direct stack, use female header + standoffs)")?;
            c.set_item("gauge", "GPIO pin direct")?;
            c.set_item("management", "Use 11mm standoffs for clearance, insulate back of UPS PCB")?;
            cables.push(c.into());
        } else if pout.contains("USB") {
            let c = PyDict::new(py);
            c.set_item("cable", "USB power cable (USB-A to USB-C or barrel)")?;
            c.set_item("route", format!("{} -> SBC USB-C/power port", pname))?;
            c.set_item("length", "10-30cm")?;
            c.set_item("gauge", "20AWG for power, 28AWG for data if applicable")?;
            c.set_item("management", "Route along enclosure base, secure with clip near battery")?;
            cables.push(c.into());
        }
    }

    // Storage cable
    if let Some(storage) = components.get_item("storage").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let stype = extract_str(&storage, "type").unwrap_or_default().to_lowercase();
        let sname = extract_str(&storage, "name").unwrap_or_default();
        if stype.contains("nvme") {
            let c = PyDict::new(py);
            c.set_item("cable", "M.2 NVMe direct (PCIe Gen 2/3 x1 or x4)")?;
            c.set_item("route", format!("{} -> SBC M.2 or PCIe HAT connector", sname))?;
            c.set_item("length", "0-5cm (direct mount or short ribbon)")?;
            c.set_item("management", "Secure with M2 screw, thermal pad recommended")?;
            cables.push(c.into());
        } else if stype.contains("sata") {
            let c = PyDict::new(py);
            c.set_item("cable", "SATA data + power cable")?;
            c.set_item("route", format!("{} -> SBC SATA port", sname))?;
            c.set_item("length", "10-20cm")?;
            c.set_item("management", "Use right-angle connectors for tight spaces")?;
            cables.push(c.into());
        }
    }

    Ok(cables)
}

#[pyfunction]
#[pyo3(name = "category_requirements")]
fn py_category_reqs(py: Python) -> PyResult<Vec<Py<PyDict>>> {
    let categories = vec![
        ("coding", "Development cyberdeck for programmers", "Raspberry Pi 5 8GB",
         "HDMI 7-10\"", "Mechanical 60%", "USB-C PD power bank", "WiFi 6",
         "Active heatsink", "NVMe 512GB+", "coding, productivity"),
        ("security", "Penetration testing cyberdeck", "Raspberry Pi 5 8GB",
         "HDMI 7\"", "Mechanical 60%", "Alfa AWUS036ACH", "WiFi 5/6",
         "Active heatsink", "NVMe 512GB", "kali, nmap, wireshark, metasploit"),
        ("ai_ml", "AI/ML inference cyberdeck", "Jetson Orin Nano",
         "HDMI 7-10\"", "Any compact", "10000mAh+ 5V/5A", "WiFi 6",
         "Active + fan", "NVMe 512GB+", "pytorch, tensorflow, onnx, coral"),
        ("writer", "Distraction-free writing deck", "Pi Zero 2W",
         "e-ink 7.5\"", "Corne/custom split", "PiSugar standalone", "None needed",
         "Passive", "SD card 64GB+", "vim, emacs, obsidian, pandoc"),
        ("survival", "Off-grid communication deck", "Orange Pi 5 Plus",
         "Low-power e-ink/OLED", "Low power mech", "Large 18650 pack", "LoRa + LTE",
         "Minimal", "SD card 128GB", "meshtastic, lora-aprs, ax25"),
        ("gaming", "Retro/light gaming deck", "Raspberry Pi 5 8GB",
         "HDMI 7-10\" 60Hz+", "60% mechanical", "10000mAh+", "WiFi 5/6",
         "Active heatsink", "NVMe 256GB+", "retroarch, steam-link, dosbox"),
        ("media_production", "Content creation deck", "LattePanda Sigma",
         "HDMI 10\"+ touch", "Full-size mech", "USB-C PD 65W+", "WiFi 6",
         "Active heatsink", "NVMe 1TB+", "kdenlive, obs, gimp, audacity"),
        ("field_research", "Field data collection deck", "Raspberry Pi 5 4GB",
         "Sunlight-readable", "Split keyboard", "Solar + 18650", "WiFi 5/6 + GPS",
         "Active heatsink", "SD card 256GB", "python, rtl-sdr, gpsd, influxdb"),
        ("ham_radio", "Amateur radio cyberdeck", "RPi 5 4GB",
         "HDMI 7\"", "Any compact", "Large battery 10000mAh", "WiFi 5/6",
         "Active heatsink", "SD card 128GB", "gnuradio, wsjt-x, fldigi, sdr++"),
        ("home_automation", "Smart home controller deck", "RPi 5 4GB",
         "Touch display 7\"", "Any", "UPS + backup battery", "Zigbee/Z-Wave",
         "Passive", "SD card 64GB", "home-assistant, zigbee2mqtt, esp32"),
        ("portable_hacking", "Ultra-portable hacking deck", "Pi Zero 2W",
         "OLED 1.3\"", "Thumb/40%", "Small battery 1200mAh", "WiFi 4",
         "Passive", "SD card 32GB", "nmap, bettercap, aircrack, bluetooth-hci"),
        ("robotics", "Robot control cyberdeck", "Orange Pi 5 Plus",
         "HDMI 7\" touch", "Compact gamepad", "High-capacity 18650", "WiFi 6",
         "Active + fan", "NVMe 256GB", "ros2, opencv, i2c, canbus, pwm"),
    ];

    let mut result = Vec::new();
    for (id, desc, sbc, display, keyboard, power, connectivity, cooling, storage, software) in categories {
        let d = PyDict::new(py);
        d.set_item("id", id)?; d.set_item("description", desc)?;
        d.set_item("recommended_sbc", sbc)?; d.set_item("recommended_display", display)?;
        d.set_item("recommended_keyboard", keyboard)?; d.set_item("recommended_power", power)?;
        d.set_item("recommended_connectivity", connectivity)?; d.set_item("recommended_cooling", cooling)?;
        d.set_item("recommended_storage", storage)?;
        d.set_item("recommended_software", software)?;
        result.push(d.into());
    }
    Ok(result)
}

#[pyfunction]
#[pyo3(name = "calculate_battery_life")]
fn py_battery_life(py: Python, capacity_mah: f64, voltage: f64, load_watts: f64) -> PyResult<Py<PyDict>> {
    let wh = if capacity_mah > 0.0 && voltage > 0.0 {
        capacity_mah * voltage / 1000.0
    } else { 0.0 };
    let hours = if load_watts > 0.0 && wh > 0.0 {
        wh / load_watts
    } else { 0.0 };

    // Chemistry labels
    let chemistry = if voltage >= 3.6 && voltage <= 3.7 { "Li-ion / LiPo (3.7V nominal)" }
        else if voltage >= 3.2 && voltage <= 3.3 { "LiFePO4 (3.2V nominal)" }
        else if voltage >= 1.2 && voltage <= 1.5 { "NiMH / Alkaline (1.2-1.5V)" }
        else if voltage >= 11.1 && voltage <= 14.8 { "Li-ion 3S-4S pack" }
        else { "Unknown / custom chemistry" };

    let result = PyDict::new(py);
    result.set_item("capacity_mah", capacity_mah)?;
    result.set_item("voltage", voltage)?;
    result.set_item("watt_hours", (wh * 100.0).round() / 100.0)?;
    result.set_item("load_watts", load_watts)?;
    result.set_item("estimated_hours", (hours * 100.0).round() / 100.0)?;
    result.set_item("estimated_minutes", (hours * 60.0).round() as u32)?;
    result.set_item("chemistry", chemistry)?;
    result.set_item("usable_factor", "80% (recommended DoD max)")?;
    result.set_item("usable_wh", (wh * 0.8 * 100.0).round() / 100.0)?;

    if hours < 1.0 && hours > 0.0 {
        result.set_item("warning", format!("Runtime <1 hour ({:.0} min). Consider larger battery or lower-power SBC.", hours * 60.0))?;
    }
    Ok(result.into())
}

#[pyfunction]
#[pyo3(name = "calculate_antenna")]
fn py_antenna(py: Python, freq_mhz: f64) -> PyResult<Py<PyDict>> {
    let c = 299792458.0;
    let wavelength = if freq_mhz > 0.0 { c / (freq_mhz * 1_000_000.0) } else { 0.0 };
    let quarter = wavelength / 4.0;
    let half = wavelength / 2.0;
    let five_eighths = wavelength * 5.0 / 8.0;

    let band = if freq_mhz < 30.0 { "HF" } else if freq_mhz < 300.0 { "VHF" }
               else if freq_mhz < 3000.0 { "UHF" } else if freq_mhz < 6000.0 { "SHF" } else { "EHF" };

    let antenna_type = if freq_mhz >= 144.0 && freq_mhz <= 148.0 { "2m Amateur band — ground plane or J-pole" }
        else if freq_mhz >= 430.0 && freq_mhz <= 440.0 { "70cm Amateur band — collinear or yagi" }
        else if freq_mhz >= 902.0 && freq_mhz <= 928.0 { "33cm ISM band — quarter wave or patch" }
        else if freq_mhz >= 2400.0 && freq_mhz <= 2500.0 { "2.4GHz ISM — dipole, patch, or helical" }
        else if freq_mhz >= 5150.0 && freq_mhz <= 5850.0 { "5GHz ISM — patch or grid" }
        else { "Quarter-wave or half-wave dipole" };

    let ground_plane_radials = if freq_mhz >= 30.0 && freq_mhz <= 1000.0 {
        Some(format!("{:.2} cm × 4 radials at 45° down", quarter * 100.0 * 1.05))
    } else { None };

    let result = PyDict::new(py);
    result.set_item("frequency_mhz", freq_mhz)?;
    result.set_item("band", band)?;
    result.set_item("wavelength_m", format!("{:.4}", wavelength))?;
    result.set_item("quarter_wave_cm", format!("{:.2}", quarter * 100.0))?;
    result.set_item("half_wave_cm", format!("{:.2}", half * 100.0))?;
    result.set_item("five_eighth_wave_cm", format!("{:.2}", five_eighths * 100.0))?;
    result.set_item("recommended_antenna", antenna_type)?;
    if let Some(rp) = ground_plane_radials {
        result.set_item("ground_plane_radial_length", rp)?;
    }

    // Coax recommendations
    let coax = if freq_mhz < 30.0 { "RG-213 or RG-8X (low loss at HF)" }
        else if freq_mhz < 300.0 { "RG-58 or RG-8X (OK at VHF)" }
        else if freq_mhz < 3000.0 { "RG-316 or LMR-100 (low loss at UHF)" }
        else { "SMA semi-rigid or U.FL (short runs only)" };
    result.set_item("recommended_coax", coax)?;

    Ok(result.into())
}

#[pyfunction]
#[pyo3(name = "compute_stack_path")]
fn py_stack_path(py: Python, category: String, _current_sbc: Option<&Bound<'_, PyDict>>,
                 budget: Option<f64>) -> PyResult<Vec<Py<PyDict>>> {
    let mut steps = Vec::new();
    let cat = category.to_lowercase();
    let budget_val = budget.unwrap_or(500.0);

    let path = match cat.as_str() {
        "coding" => vec![
            ("Beginner", "Pi Zero 2W", "5\" HDMI, low-cost mech", "$150-250", 1),
            ("Intermediate", "Pi 5 4GB", "7\" HDMI IPS, 60% mech", "$300-500", 2),
            ("Advanced", "Pi 5 8GB", "10\" HDMI touch, custom split", "$600-900", 3),
        ],
        "security" => vec![
            ("Beginner", "Pi 4 8GB", "5\" HDMI, Kali pre-installed", "$200-350", 1),
            ("Intermediate", "Pi 5 8GB", "7\" HDMI, dual WiFi, HackRF", "$500-800", 2),
            ("Advanced", "Pi 5 8GB", "10\" touch, SDR, mesh, GPS", "$800-1200", 3),
        ],
        "ai_ml" => vec![
            ("Intermediate", "Pi 5 8GB", "7\" HDMI, USB AI stick", "$400-600", 1),
            ("Advanced", "Jetson Orin Nano", "10\" touch, Coral TPU, camera", "$800-1500", 2),
            ("Expert", "Jetson Orin NX", "10\" touch, dual camera, NVMe", "$1500-2500", 3),
        ],
        _ => vec![
            ("Beginner", "Pi Zero 2W", "Basic display, starter components", "$100-200", 1),
            ("Intermediate", "Pi 5 4GB", "Mid-range display, full set", "$300-500", 2),
            ("Advanced", "Pi 5 8GB/Orange Pi 5", "All components, premium build", "$600-1200", 3),
        ],
    };

    for (tier_name, sbc, parts, cost, level) in path {
        if budget_val >= level as f64 * 200.0 {
            let d = PyDict::new(py);
            d.set_item("tier", tier_name)?; d.set_item("sbc", sbc)?;
            d.set_item("detail", parts)?; d.set_item("cost_range", cost)?;
            d.set_item("level", level)?;
            steps.push(d.into());
        }
    }

    if steps.is_empty() {
        let d = PyDict::new(py);
        d.set_item("tier", "None")?;
        d.set_item("sbc", "No build within budget")?;
        d.set_item("detail", "Consider DIY with repurposed parts")?;
        d.set_item("cost_range", format!("${:.0}", budget_val))?;
        d.set_item("level", 0)?;
        steps.push(d.into());
    }

    Ok(steps)
}

#[pyfunction]
#[pyo3(name = "compute_score")]
fn py_compute_score(py: Python, components: &Bound<'_, PyDict>) -> PyResult<Py<PyDict>> {
    let mut score: f64 = 0.0;
    let mut breakdown: Vec<String> = Vec::new();

    let has = |k: &str| components.get_item(k).ok().flatten().is_some();

    score += if has("sbc") { 20.0 } else { 0.0 };
    score += if has("display") { 15.0 } else { 0.0 };
    score += if has("keyboard") { 10.0 } else { 0.0 };
    score += if has("power") { 15.0 } else { 0.0 };
    score += if has("enclosure") { 10.0 } else { 0.0 };
    score += if has("cooling") { 10.0 } else { 0.0 };
    score += if has("storage") { 10.0 } else { 0.0 };
    score += if has("connectivity") { 5.0 } else { 0.0 };
    score += if has("lora") { 5.0 } else { 0.0 };

    breakdown.push(format!("SBC: {}/20", if has("sbc") { 20 } else { 0 }));
    breakdown.push(format!("Display: {}/15", if has("display") { 15 } else { 0 }));
    breakdown.push(format!("Keyboard: {}/10", if has("keyboard") { 10 } else { 0 }));
    breakdown.push(format!("Power: {}/15", if has("power") { 15 } else { 0 }));
    breakdown.push(format!("Enclosure: {}/10", if has("enclosure") { 10 } else { 0 }));
    breakdown.push(format!("Cooling: {}/10", if has("cooling") { 10 } else { 0 }));
    breakdown.push(format!("Storage: {}/10", if has("storage") { 10 } else { 0 }));
    breakdown.push(format!("Connectivity: {}/5", if has("connectivity") { 5 } else { 0 }));
    breakdown.push(format!("Extras (LoRa): {}/5", if has("lora") { 5 } else { 0 }));

    let grade = if score >= 90.0 { "S" } else if score >= 75.0 { "A" }
        else if score >= 60.0 { "B" } else if score >= 40.0 { "C" }
        else if score >= 20.0 { "D" } else { "F" };

    let result = PyDict::new(py);
    result.set_item("score", score as u32)?;
    result.set_item("max_score", 100)?;
    result.set_item("grade", grade)?;
    result.set_item("breakdown", breakdown)?;
    Ok(result.into())
}

#[pymodule]
fn cyberdeck_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<crate::types::Component>()?;
    m.add_class::<crate::types::Flaw>()?;
    m.add_class::<crate::types::BuildAudit>()?;
    m.add_class::<crate::types::Upgrade>()?;
    m.add_class::<crate::types::Model3dConfig>()?;
    m.add_function(wrap_pyfunction!(py_check_compatibility, m)?)?;
    m.add_function(wrap_pyfunction!(py_audit_build, m)?)?;
    m.add_function(wrap_pyfunction!(py_auto_fix, m)?)?;
    m.add_function(wrap_pyfunction!(py_suggest_upgrades, m)?)?;
    m.add_function(wrap_pyfunction!(py_generate_3d, m)?)?;
    m.add_function(wrap_pyfunction!(py_generate_3d_from, m)?)?;
    m.add_function(wrap_pyfunction!(py_bom_generate, m)?)?;
    m.add_function(wrap_pyfunction!(py_search, m)?)?;
    m.add_function(wrap_pyfunction!(py_cable_plan, m)?)?;
    m.add_function(wrap_pyfunction!(py_category_reqs, m)?)?;
    m.add_function(wrap_pyfunction!(py_battery_life, m)?)?;
    m.add_function(wrap_pyfunction!(py_antenna, m)?)?;
    m.add_function(wrap_pyfunction!(py_stack_path, m)?)?;
    m.add_function(wrap_pyfunction!(py_compute_score, m)?)?;
    m.add_function(wrap_pyfunction!(py_export_scad, m)?)?;
    m.add_function(wrap_pyfunction!(py_export_stl, m)?)?;
    m.add_function(wrap_pyfunction!(py_generate_print_package, m)?)?;
    Ok(())
}

#[pyfunction]
#[pyo3(name = "export_scad")]
fn py_export_scad(py: Python, config: &Bound<'_, Model3dConfig>) -> PyResult<Py<PyDict>> {
    let c = config.borrow();
    export_scad(py, &c)
}

#[pyfunction]
#[pyo3(name = "export_stl")]
fn py_export_stl(py: Python, config: &Bound<'_, Model3dConfig>) -> PyResult<Py<PyDict>> {
    let c = config.borrow();
    export_stl(py, &c)
}

#[pyfunction]
#[pyo3(name = "generate_print_package")]
fn py_generate_print_package(py: Python, config: &Bound<'_, Model3dConfig>, material: String, quantity: u32) -> PyResult<Py<PyDict>> {
    let c = config.borrow();
    generate_print_package(py, &c, &material, quantity)
}
