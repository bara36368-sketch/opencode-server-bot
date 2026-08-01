use pyo3::prelude::*;
use pyo3::types::{PyDict, PyAny, PyDictMethods, PyAnyMethods};
use crate::types::{Flaw, extract_str, extract_f64};

pub fn check_sbc_display(sbc: &Bound<'_, PyDict>, display: &Bound<'_, PyDict>) -> (bool, Vec<String>) {
    let mut issues = Vec::new();
    let sbc_name = extract_str(sbc, "name").unwrap_or_default().to_lowercase();
    let display_if = extract_str(display, "interface").unwrap_or_default().to_lowercase();
    let display_id = extract_str(display, "id").or_else(|| extract_str(display, "name"))
        .unwrap_or_default().to_lowercase();
    let sbc_id = extract_str(sbc, "id").unwrap_or_default().to_lowercase();

    if sbc_name.contains("zero 2w") || sbc_name.contains("zero 2") {
        if display_if.contains("hdmi") && !display_if.contains("mini") {
            issues.push("Pi Zero 2W needs mini-HDMI adapter for HDMI displays".into());
        }
        if display_if.contains("dsi") {
            issues.push("Pi Zero 2W has no DSI connector".into());
        }
        if display_id.contains("eink") && display_id.contains("7") {
            issues.push("Pi Zero 2W may struggle to drive large e-ink displays (>6\")".into());
        }
    }
    if sbc_name.contains("jetson") && (display_id.contains("eink") || display_id.contains("oled")) {
        issues.push("Jetson works best with HDMI/DSI displays".into());
    }
    if sbc_name.contains("orange pi zero3") && display_if.contains("dsi") {
        issues.push("Orange Pi Zero 3 has no DSI connector".into());
    }
    if sbc_id.contains("rk3588") && !display_if.contains("hdmi") && !display_if.contains("dsi") {
        issues.push("RK3588 boards (Orange Pi 5) need HDMI or DSI display".into());
    }
    if display_id.contains("10inch") && sbc_name.contains("zero") {
        issues.push("10\" display requires more GPU than Pi Zero can provide".into());
    }
    (issues.is_empty(), issues)
}

pub fn check_sbc_power(sbc: &Bound<'_, PyDict>, power: &Bound<'_, PyDict>) -> (bool, Vec<String>) {
    let mut issues = Vec::new();
    let sbc_name = extract_str(sbc, "name").unwrap_or_default();
    let sbc_id = extract_str(sbc, "id").or_else(|| extract_str(sbc, "name")).unwrap_or_default().to_lowercase();
    let sbc_power = extract_str(sbc, "power").or_else(|| extract_str(sbc, "power_draw")).unwrap_or_default();
    let power_output = extract_str(power, "output").unwrap_or_default();
    let power_id = extract_str(power, "id").unwrap_or_default().to_lowercase();
    let power_name = extract_str(power, "name").unwrap_or_default();
    let power_wh = extract_f64(power, "watt_hours").or_else(|| extract_f64(power, "capacity_wh"));
    let power_ma = extract_f64(power, "capacity_mah");

    if sbc_power.contains("5V/5A") && !power_output.contains("5A") {
        issues.push(format!("{} needs 5V/5A (27W) but {} outputs {}",
            sbc_name, power_name, power_output));
    }
    if sbc_power.contains("5V/3A") && power_output.contains("5V/5A") {
        issues.push(format!("Over-spec PSU — {} outputs 25W, draw is ~15W. Efficient but heavy.",
            power_name));
    }
    if sbc_id.contains("jetson") && power_id.contains("pisugar") {
        issues.push("Jetson requires more power than PiSugar can provide".into());
    }
    if sbc_id.contains("orange_pi_5") && power_id.contains("pimoroni_lipo") {
        issues.push("Orange Pi 5 Plus needs more power than LiPo SHIM provides".into());
    }
    if sbc_id.contains("lattepanda") && power_id.contains("pimoroni_lipo") {
        issues.push("LattePanda Sigma requires 12V/2A — LiPo SHIM insufficient".into());
    }
    // Estimate runtime if both capacity and SBC power draw known
    if let Some(wh) = power_wh {
        let draw = if sbc_id.contains("jetson") { 15.0 }
            else if sbc_id.contains("lattepanda") { 25.0 }
            else if sbc_id.contains("pi_5") || sbc_id.contains("rpi5") { 12.0 }
            else if sbc_id.contains("pi_4") { 7.0 }
            else { 3.0 };
        if draw > 0.0 && wh / draw < 1.0 {
            issues.push(format!("Battery runtime <1h ({:.1}Wh / {:.1}W draw). Increase capacity.", wh, draw));
        }
    } else if let Some(ma) = power_ma {
        let wh = ma * 3.7 / 1000.0;
        let draw = if sbc_id.contains("jetson") { 15.0 }
            else if sbc_id.contains("lattepanda") { 25.0 }
            else if sbc_id.contains("rpi5") { 12.0 }
            else if sbc_id.contains("pi_4") { 7.0 }
            else { 3.0 };
        if draw > 0.0 && wh / draw < 1.0 {
            issues.push(format!("Battery runtime <1h ({:.0}mAh ~ {:.1}Wh / {:.1}W draw). Increase capacity.",
                ma, wh, draw));
        }
    }

    (issues.is_empty(), issues)
}

pub fn check_sbc_enclosure(sbc: &Bound<'_, PyDict>, enclosure: &Bound<'_, PyDict>) -> (bool, Vec<String>) {
    let mut issues = Vec::new();
    let sbc_id = extract_str(sbc, "id").or_else(|| extract_str(sbc, "name")).unwrap_or_default().to_lowercase();
    let enc_id = extract_str(enclosure, "id").unwrap_or_default().to_lowercase();
    let sbc_name = extract_str(sbc, "name").unwrap_or_default().to_lowercase();
    let enc_form = extract_str(enclosure, "form_factor").or_else(|| extract_str(enclosure, "size")).unwrap_or_default();

    if sbc_id.contains("lattepanda") && enc_id.contains("pelican_1150") {
        issues.push("LattePanda 3 Delta (125x78mm) is too large for Pelican 1150".into());
    }
    if sbc_id.contains("jetson") && (enc_id.contains("pelican_1150") || enc_id.contains("pelican_1200")) {
        issues.push("Jetson Orin Nano (100x87mm) needs larger enclosure".into());
    }
    if sbc_name.contains("zero 2w") && enc_id.contains("3d_printed_vented") {
        issues.push("Pi Zero 2W doesn't need vented enclosure — too small for active cooling".into());
    }
    if sbc_id.contains("rk3588") && enc_form.contains("1150") {
        issues.push("RK3588 SBC (100x70mm) may be tight in Pelican 1150 — check fit".into());
    }
    if sbc_id.contains("pi_5") && enc_id.contains("3d_printed_vented") {
        if extract_str(enclosure, "width").and_then(|w| w.parse::<f64>().ok()).map(|w| w < 120.0).unwrap_or(false) {
            issues.push("Pi 5 with active cooler needs minimum 120mm enclosure width".into());
        }
    }

    (issues.is_empty(), issues)
}

pub fn check_connectivity(components: &Bound<'_, PyDict>, py: Python) -> (bool, Vec<String>) {
    let mut issues = Vec::new();
    let sbc = components.get_item("sbc").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone());
    let conn_id = extract_str(components, "connectivity").unwrap_or_default();
    let cat = extract_str(components, "category").unwrap_or_default();

    let has_wifi = sbc.as_ref()
        .and_then(|s| s.get_item("connectivity").ok().flatten())
        .and_then(|x| x.extract::<String>().ok())
        .map(|c| c.contains("WiFi")).unwrap_or(false);
    let has_bt = sbc.as_ref()
        .and_then(|s| s.get_item("connectivity").ok().flatten())
        .and_then(|x| x.extract::<String>().ok())
        .map(|c| c.contains("BT")).unwrap_or(false);

    if conn_id.is_empty() && !has_wifi {
        issues.push("No connectivity: SBC has no built-in WiFi and no adapter selected".into());
    }
    if !has_bt && conn_id.is_empty() {
        issues.push("No Bluetooth — wireless peripherals won't connect".into());
    }
    if cat == "security" && !conn_id.is_empty() &&
       conn_id != "awus036ach" && conn_id != "awus036acs" && conn_id != "hackrf_one" {
        issues.push("Security builds should include an Alfa WiFi adapter or HackRF".into());
    }
    if cat == "survival" && !conn_id.is_empty() &&
       conn_id != "lora_module" && conn_id != "lte_modem" {
        issues.push("Survival builds should include LoRa or LTE modem for off-grid comms".into());
    }
    if cat == "ai_ml" && !has_wifi {
        issues.push("AI/ML builds benefit from WiFi 6 for model downloads and cloud inference".into());
    }

    (issues.is_empty(), issues)
}

pub fn check_storage(sbc: &Bound<'_, PyDict>, storage: &Bound<'_, PyDict>) -> (bool, Vec<String>) {
    let mut issues = Vec::new();
    let sbc_name = extract_str(sbc, "name").unwrap_or_default().to_lowercase();
    let storage_type = extract_str(storage, "type").unwrap_or_default().to_lowercase();
    let storage_name = extract_str(storage, "name").unwrap_or_default();

    if storage_type.contains("nvme") && sbc_name.contains("zero") {
        issues.push("Pi Zero cannot use NVMe — no PCIe lane".into());
    }
    if storage_type.contains("nvme") && sbc_name.contains("pi 4") {
        issues.push("Pi 4 needs PCIe HAT for NVMe — not native".into());
    }
    if storage_type.contains("nvme") && sbc_name.contains("pi 5") {
        // Native NVMe on Pi 5 — OK
    }
    if storage_type.contains("m.2 sata") && sbc_name.contains("pi") && !sbc_name.contains("orange") {
        issues.push("Raspberry Pi doesn't support SATA. Use NVMe or USB adapter".into());
    }
    if storage_type.contains("sata") && sbc_name.contains("lattepanda") {
        // LattePanda supports SATA — OK
    }
    if storage_type.contains("microsd") && storage_name.contains("64") {
        issues.push("64GB or larger microSD should be A2 class for adequate IOPS".into());
    }
    if storage_type.contains("emmc") && sbc_name.contains("zero") {
        // Pi Zero has no eMMC — needs module/HAT
        issues.push("Pi Zero needs eMMC module on GPIO. Ensure module compatibility".into());
    }

    (issues.is_empty(), issues)
}

pub fn check_thermal(sbc: &Bound<'_, PyDict>, cooling: Option<&Bound<'_, PyDict>>) -> Vec<String> {
    let mut issues = Vec::new();
    let sbc_name = extract_str(sbc, "name").unwrap_or_default().to_lowercase();
    let sbc_id = extract_str(sbc, "id").unwrap_or_default().to_lowercase();

    let needs_active = sbc_id.contains("jetson") || sbc_id.contains("lattepanda")
        || sbc_id.contains("rk3588") || sbc_name.contains("pi 5");

    if needs_active && cooling.is_none() {
        issues.push("This SBC needs active cooling (fan + heatsink)".into());
    } else if let Some(c) = cooling {
        let c_type = extract_str(c, "type").or_else(|| extract_str(c, "name")).unwrap_or_default().to_lowercase();
        if needs_active && !c_type.contains("fan") && !c_type.contains("active") {
            issues.push("Passive cooling insufficient for this SBC under load".into());
        }
    }

    if sbc_name.contains("pi 5") && cooling.is_none() {
        issues.push("Pi 5 throttles without cooling — benchmark loses 40% perf".into());
    }

    issues
}

pub fn audit_build(components: &Bound<'_, PyAny>, py: Python) -> PyResult<(Vec<Flaw>, Vec<String>)> {
    let mut flaws: Vec<Flaw> = Vec::new();
    let mut fixes: Vec<String> = Vec::new();

    let comp_list: Vec<Bound<'_, PyDict>> = if let Ok(d) = components.cast::<PyDict>() {
        d.get_item("components").ok().flatten()
            .and_then(|x| x.extract::<Vec<Py<PyDict>>>().ok().map(|v| {
                v.into_iter().filter_map(|c| c.bind(py).clone().into()).collect()
            })).unwrap_or_default()
    } else if let Ok(list) = components.extract::<Vec<Py<PyDict>>>() {
        list.into_iter().filter_map(|c| c.bind(py).clone().into()).collect()
    } else { return Ok((flaws, fixes)) };

    let comp_types: Vec<String> = comp_list.iter().filter_map(|c| {
        extract_str(c, "type").or_else(|| extract_str(c, "component_type"))
            .map(|s| s.to_lowercase())
    }).collect();

    let has_type = |t: &str| comp_types.iter().any(|ct| ct.contains(t));
    let get_comp = |t: &str| comp_list.iter().find(|c| {
        extract_str(c, "type").or_else(|| extract_str(c, "component_type"))
            .map(|s| s.to_lowercase().contains(t)).unwrap_or(false)
    });

    if !has_type("sbc") {
        flaws.push(Flaw::new("critical".into(), "No SBC selected".into(),
            "Add a Raspberry Pi 5 or equivalent SBC".into()));
        fixes.push("Added SBC to component list".into());
    }
    if !has_type("cool") && !has_type("fan") && !has_type("heatsink") {
        flaws.push(Flaw::new("high".into(), "No cooling solution".into(),
            "Add heatsink and/or fan".into()));
        fixes.push("Added cooling solution".into());
    }
    if !has_type("wifi") && !has_type("connectivity") && !has_type("ethernet") {
        flaws.push(Flaw::new("high".into(), "No connectivity (WiFi/LAN)".into(),
            "Add WiFi adapter or Ethernet".into()));
        fixes.push("Added connectivity module".into());
    }
    if !has_type("power") && !has_type("battery") {
        flaws.push(Flaw::new("critical".into(), "No power system".into(),
            "Add battery and charging circuit".into()));
        fixes.push("Added power system".into());
    }
    if !has_type("display") {
        flaws.push(Flaw::new("high".into(), "No display".into(),
            "Add display module".into()));
        fixes.push("Added display".into());
    }
    if !has_type("enclosure") {
        flaws.push(Flaw::new("medium".into(), "No enclosure".into(),
            "Add enclosure — 3D printed or Pelican case".into()));
        fixes.push("Added enclosure".into());
    }
    if !has_type("keyboard") {
        flaws.push(Flaw::new("low".into(), "No keyboard input".into(),
            "Consider adding a keyboard for text input".into()));
        fixes.push("Added keyboard suggestion".into());
    }

    // Per-component checks
    for c in &comp_list {
        let c_name = extract_str(c, "name").unwrap_or_default();
        let c_price = extract_f64(c, "price").or_else(|| extract_f64(c, "price_num")).unwrap_or(0.0);
        if c_price == 0.0 {
            flaws.push(Flaw::new("low".into(),
                format!("No price for {}", c_name),
                "Add pricing information".into()));
        }
        let c_cable = extract_str(c, "cable_length").or_else(|| extract_str(c, "cable"));
        if c_cable.is_none() || c_cable.as_deref() == Some("") {
            flaws.push(Flaw::new("medium".into(),
                format!("No cable length for {}", c_name),
                "Calculate cable length based on position".into()));
        }
    }

    // Thermal check if SBC exists
    if let Some(sbc) = get_comp("sbc") {
        let cooling = get_comp("cooling");
        let thermal_issues = check_thermal(sbc, cooling);
        for issue in thermal_issues {
            flaws.push(Flaw::new("high".into(), issue.clone(),
                "Add active cooling (fan + heatsink)".into()));
            if !fixes.contains(&"Added active cooling".to_string()) {
                fixes.push("Added active cooling".into());
            }
        }
    }

    let total_price: f64 = comp_list.iter().filter_map(|c| {
        extract_f64(c, "price").or_else(|| extract_f64(c, "price_num"))
    }).sum();

    if total_price > 2000.0 {
        flaws.push(Flaw::new("info".into(),
            format!("High cost: ${:.2}", total_price),
            "Consider budget alternatives".into()));
    }
    if total_price > 0.0 && total_price < 50.0 {
        flaws.push(Flaw::new("info".into(),
            format!("Suspiciously low total: ${:.2}", total_price),
            "Verify all components have prices".into()));
    }

    Ok((flaws, fixes))
}

pub fn auto_fix(components: &Bound<'_, PyDict>, issues: Vec<String>, py: Python) -> PyResult<Vec<Py<PyDict>>> {
    let mut fixed: Vec<Py<PyDict>> = Vec::new();
    let mut fixed_ids: Vec<String> = Vec::new();

    // Collect existing component IDs
    for key in components.keys().into_iter().filter_map(|k| k.extract::<String>().ok()) {
        if let Some(val) = components.get_item(&key).ok().flatten() {
            if let Ok(d) = val.cast::<PyDict>() {
                let item = PyDict::new(py);
                for k2 in d.keys().into_iter().filter_map(|k| k.extract::<String>().ok()) {
                    if let Ok(Some(v)) = d.get_item(&k2) {
                        let _ = item.set_item(&k2, v);
                    }
                }
                fixed_ids.push(key);
                fixed.push(item.into());
            }
        }
    }

    for issue in &issues {
        let il = issue.to_lowercase();
        if il.contains("no sbc") && !fixed_ids.iter().any(|id| id.contains("sbc") || id.contains("pi")) {
            let d = PyDict::new(py);
            d.set_item("id", "rpi5_8gb")?; d.set_item("name", "Raspberry Pi 5 8GB")?;
            d.set_item("type", "SBC")?; d.set_item("price", 80.0)?;
            d.set_item("power", "5V/5A")?;
            fixed_ids.push("rpi5_8gb".into());
            fixed.push(d.into());
        }
        if il.contains("no display") && !fixed_ids.iter().any(|id| id.contains("display")) {
            let d = PyDict::new(py);
            d.set_item("id", "hdmi_7inch_ips")?; d.set_item("name", "HDMI 7\" IPS")?;
            d.set_item("type", "Display")?; d.set_item("interface", "HDMI")?;
            d.set_item("price", 55.0)?;
            fixed_ids.push("hdmi_7inch_ips".into());
            fixed.push(d.into());
        }
        if il.contains("no cooling") && !fixed_ids.iter().any(|id| id.contains("cool")) {
            let d = PyDict::new(py);
            d.set_item("id", "active_fan_heatsink")?; d.set_item("name", "Active Fan + Heatsink")?;
            d.set_item("type", "Cooling")?; d.set_item("price", 12.0)?;
            fixed_ids.push("active_fan_heatsink".into());
            fixed.push(d.into());
        }
        if il.contains("no power") && !fixed_ids.iter().any(|id| id.contains("power")) {
            let d = PyDict::new(py);
            d.set_item("id", "ups_h5180")?; d.set_item("name", "UPS HAT 5000mAh")?;
            d.set_item("type", "Power")?; d.set_item("output", "5V/5A")?;
            d.set_item("price", 45.0)?;
            fixed_ids.push("ups_h5180".into());
            fixed.push(d.into());
        }
        if il.contains("no connectivity") && !fixed_ids.iter().any(|id| id.contains("wifi")) {
            let d = PyDict::new(py);
            d.set_item("id", "wifi_usb_adapter")?; d.set_item("name", "WiFi 5 USB Adapter")?;
            d.set_item("type", "Connectivity")?; d.set_item("price", 15.0)?;
            fixed_ids.push("wifi_usb_adapter".into());
            fixed.push(d.into());
        }
        if il.contains("no enclosure") && !fixed_ids.iter().any(|id| id.contains("enclosure")) {
            let d = PyDict::new(py);
            d.set_item("id", "3d_printed_vented")?; d.set_item("name", "3D Printed Vented Enclosure")?;
            d.set_item("type", "Enclosure")?; d.set_item("price", 35.0)?;
            fixed_ids.push("3d_printed_vented".into());
            fixed.push(d.into());
        }
    }

    Ok(fixed)
}

pub fn suggest_upgrades(comp_dict: &Bound<'_, PyDict>, py: Python) -> PyResult<Vec<Py<PyDict>>> {
    let mut upgrades = Vec::new();

    if let Some(sbc) = comp_dict.get_item("sbc").ok().flatten()
        .and_then(|x| x.extract::<Py<PyDict>>().ok())
        .map(|d| d.bind(py).clone())
    {
        let name = extract_str(&sbc, "name").unwrap_or_default();
        if name.contains("Zero") {
            let d = PyDict::new(py);
            d.set_item("component", "SBC")?; d.set_item("current", &name)?;
            d.set_item("upgrade", "Raspberry Pi 5 8GB")?;
            d.set_item("reason", "10x more performance, full-size HDMI, NVMe")?;
            d.set_item("cost", 65.0)?; d.set_item("difficulty", "easy")?;
            upgrades.push(d.into());
        } else if name.contains("Pi 4") {
            let d = PyDict::new(py);
            d.set_item("component", "SBC")?; d.set_item("current", &name)?;
            d.set_item("upgrade", "Raspberry Pi 5 8GB")?;
            d.set_item("reason", "2-3x more performance, NVMe support, WiFi 6")?;
            d.set_item("cost", 45.0)?; d.set_item("difficulty", "easy")?;
            upgrades.push(d.into());
        } else if name.contains("Pi 5 4GB") {
            let d = PyDict::new(py);
            d.set_item("component", "SBC")?; d.set_item("current", &name)?;
            d.set_item("upgrade", "Raspberry Pi 5 8GB")?;
            d.set_item("reason", "Double RAM for heavy multitasking")?;
            d.set_item("cost", 20.0)?; d.set_item("difficulty", "easy")?;
            upgrades.push(d.into());
        } else if name.contains("Orange Pi Zero") {
            let d = PyDict::new(py);
            d.set_item("component", "SBC")?; d.set_item("current", &name)?;
            d.set_item("upgrade", "Orange Pi 5 Plus")?;
            d.set_item("reason", "Much faster RK3588, NVMe, 32GB RAM support")?;
            d.set_item("cost", 80.0)?; d.set_item("difficulty", "medium")?;
            upgrades.push(d.into());
        }
    }

    let has_key = |k: &str| -> bool {
        comp_dict.get_item(k).ok().flatten().is_some()
    };

    if !has_key("storage") {
        let d = PyDict::new(py);
        d.set_item("component", "Storage")?; d.set_item("current", "SD Card")?;
        d.set_item("upgrade", "NVMe SSD 512GB + HAT")?;
        d.set_item("reason", "10x faster storage, more reliable")?;
        d.set_item("cost", 55.0)?; d.set_item("difficulty", "easy")?;
        upgrades.push(d.into());
    } else if has_key("storage") {
        if let Some(storage) = comp_dict.get_item("storage").ok().flatten()
            .and_then(|x| x.extract::<Py<PyDict>>().ok())
            .map(|d| d.bind(py).clone())
        {
            let s_name = extract_str(&storage, "name").unwrap_or_default();
            if s_name.contains("256") || s_name.contains("128") || s_name.contains("64") {
                let d = PyDict::new(py);
                d.set_item("component", "Storage")?; d.set_item("current", &s_name)?;
                d.set_item("upgrade", "NVMe SSD 1TB")?;
                d.set_item("reason", "More storage space for OS + projects")?;
                d.set_item("cost", 60.0)?; d.set_item("difficulty", "easy")?;
                upgrades.push(d.into());
            }
        }
    }

    if !has_key("cooling") {
        let d = PyDict::new(py);
        d.set_item("component", "Cooling")?; d.set_item("current", "None")?;
        d.set_item("upgrade", "Active heatsink + fan")?;
        d.set_item("reason", "Prevent thermal throttling, extend lifespan")?;
        d.set_item("cost", 15.0)?; d.set_item("difficulty", "easy")?;
        upgrades.push(d.into());
    }
    if !has_key("gps") && !has_key("connectivity") {
        let d = PyDict::new(py);
        d.set_item("component", "GPS")?; d.set_item("current", "None")?;
        d.set_item("upgrade", "u-blox NEO-M9N GPS module")?;
        d.set_item("reason", "Location awareness, time sync, geotagging")?;
        d.set_item("cost", 25.0)?; d.set_item("difficulty", "easy")?;
        upgrades.push(d.into());
    }
    if !has_key("lora") {
        let d = PyDict::new(py);
        d.set_item("component", "LoRa")?; d.set_item("current", "None")?;
        d.set_item("upgrade", "SX1262 LoRa module")?;
        d.set_item("reason", "Long-range mesh communication off-grid")?;
        d.set_item("cost", 12.0)?; d.set_item("difficulty", "medium")?;
        upgrades.push(d.into());
    }
    if !has_key("display") {
        let d = PyDict::new(py);
        d.set_item("component", "Display")?; d.set_item("current", "None")?;
        d.set_item("upgrade", "7\" HDMI IPS display")?;
        d.set_item("reason", "Essential for any cyberdeck")?;
        d.set_item("cost", 55.0)?; d.set_item("difficulty", "easy")?;
        upgrades.push(d.into());
    }

    Ok(upgrades)
}
