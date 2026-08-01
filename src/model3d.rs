use pyo3::prelude::*;
use pyo3::types::{PyDict, PyDictMethods};
use crate::types::Model3dConfig;

const STYLES: [(&str, &[&str], &[&str]); 6] = [
    ("futuristic", &["white", "cyan", "silver", "neon_blue"], &["#FFFFFF", "#00FFFF", "#C0C0C0", "#00D4FF"]),
    ("retro", &["beige", "brown", "cream", "warm_white"], &["#F5F5DC", "#8B4513", "#FFFDD0", "#FAF0E6"]),
    ("industrial", &["black", "yellow", "silver", "red"], &["#1A1A1A", "#FFD700", "#C0C0C0", "#DC143C"]),
    ("minimal", &["white", "gray", "black", "natural"], &["#F8F8F8", "#A9A9A9", "#2F2F2F", "#D2B48C"]),
    ("steampunk", &["bronze", "brass", "copper", "leather_brown"], &["#CD7F32", "#B5A642", "#B87333", "#8B4513"]),
    ("cyberpunk", &["black", "neon_pink", "neon_green", "dark_gray"], &["#0D0D0D", "#FF00FF", "#00FF41", "#1A1A2E"]),
];

fn style_primary(style: &str) -> String {
    STYLES.iter().find(|(s, _, _)| *s == style)
        .and_then(|(_, _, h)| h.first())
        .map(|s| s.to_string())
        .unwrap_or("#808080".into())
}

fn style_accent(style: &str) -> String {
    STYLES.iter().find(|(s, _, _)| *s == style)
        .and_then(|(_, _, h)| h.get(1))
        .map(|s| s.to_string())
        .unwrap_or("#808080".into())
}

fn style_names(style: &str) -> Vec<&str> {
    STYLES.iter().find(|(s, _, _)| *s == style)
        .map(|(_, n, _)| n.as_ref())
        .unwrap_or(&["white", "gray", "black", "dark_gray"])
        .to_vec()
}

fn round_cube(name: &str, w: f64, h: f64, d: f64, r: f64) -> String {
    let r2 = r.max(0.5);
    let cw = (w - r2 * 2.0).max(0.1);
    let ch = (h - r2 * 2.0).max(0.1);
    let cd = (d - r2 * 2.0).max(0.1);
    format!(r#"module {n}() {{
    minkowski() {{
        cube([{w:.2}, {h:.2}, {d:.2}], center=true);
        sphere(r={r:.2}, $fn=24);
    }}
}}

"#, n=name, w=cw, h=ch, d=cd, r=r2)
}

fn vent_slots(w: f64, _d: f64, count: u32) -> String {
    let mut out = String::from("module vent_slots() {\n");
    let spacing = w / (count + 1) as f64;
    for i in 0..count {
        let x = -w / 2.0 + spacing * (i + 1) as f64;
        out.push_str(&format!(
            "    translate([{x:.2}, 0, d/2 - 3])\n        cube([1.5, 25, 1], center=true);\n", x=x));
    }
    out.push_str("}\n\n");
    out
}

fn cable_channel(w: f64, d: f64) -> String {
    format!("module cable_channel() {{
    color(\"#505050\") {{
        difference() {{
            translate([-{w:.2}/2 + 3, 0, -h/2 + 2])
                cube([4, {d:.2} - 10, 4], center=true);
            translate([-{w:.2}/2 + 3, 0, -h/2 + 2])
                cube([2.4, {d:.2} - 8, 5], center=true);
        }}
    }}
}}

")
}

fn hinge() -> String {
    format!("module hinge() {{
    color(\"#808080\") {{
        translate([0, 0, -h/2]) {{
            cube([w - 20, 3, 0.8], center=true);
        }}
    }}
}}

")
}

fn standoffs() -> String {
    String::from(r##"module standoffs() {
    color("#C0C0C0") {
        for (pos = [[-30, -25], [30, -25], [-30, 25], [30, 25], [-15, 35], [15, 35]]) {
            translate([pos[0], pos[1], -h/2 + 1])
                difference() {
                    cylinder(r=3.2, h=6, center=true, $fn=20);
                    translate([0, 0, -1])
                        cylinder(r=1.3, h=8, center=true, $fn=12);
                }
        }
    }
}

"##)
}

fn io_cutouts() -> String {
    String::from(r##"module io_cutouts() {
    // HDMI
    translate([w/2 - 2, -8, 2])
        cube([5, 14, 7], center=true);
    // USB ports × 2
    translate([w/2 - 2, 7, 2])
        cube([5, 13, 6], center=true);
    translate([w/2 - 2, 22, 2])
        cube([5, 13, 6], center=true);
    // Power barrel / USB-C
    translate([w/2 - 2, -22, 2])
        cube([6, 10, 8], center=true);
    // 3.5mm audio
    translate([w/2 - 2, -35, 2])
        cube([5, 8, 6], center=true);
    // GPIO access
    translate([-w/2 + 2, 0, 2])
        cube([8, 40, 4], center=true);
}

"##)
}

fn display_bezel(w: f64, d: f64) -> String {
    let bw = w * 0.75;
    let bd = d * 0.65;
    format!(r#"module display_bezel() {{
    difference() {{
        translate([0, 0, h/2])
            cube([{bw:.2}, {bd:.2}, 2], center=true);
        translate([0, 0, h/2 + 1])
            cube([{bw:.2} - 8, {bd:.2} - 8, 4], center=true);
    }}
}}

"#, bw=bw, bd=bd)
}

fn lid_latch() -> String {
    String::from(r#"module lid_latch() {
    translate([0, d/2 - 5, 0])
        cube([12, 3, 3], center=true);
}

"#)
}

fn assembly() -> String {
    String::from(r##"// ===== ASSEMBLY =====
difference() {
    enclosure_body();

    // Cut out SBC area
    translate([0, 0, -h/4])
        cube([65, 56, h/2], center=true);

    // Cut out display area
    translate([0, 0, h/4])
        cube([w * 0.7, d * 0.6, h/2], center=true);

    // Ventilation
    translate([0, 0, h/4]) vent_slots();

    // I/O cutouts
    io_cutouts();

    // Cable channel slot
    translate([0, 0, -h/4])
        cable_channel();

    // Screw holes
    for (corner = [[-w/2 + 6, -d/2 + 6], [w/2 - 6, -d/2 + 6],
                   [-w/2 + 6, d/2 - 6], [w/2 - 6, d/2 - 6]]) {
        translate([corner[0], corner[1], 0])
            cylinder(r=1.6, h=h+1, center=true, $fn=16);
    }
}

// Standoffs
standoffs();

// Lid
translate([0, 0, h/2 + 1.5]) {
    enclosure_lid();
    display_bezel();
    lid_latch();
}

// Hinge
hinge();

// Accent lines
translate([0, 0, h/2 + 2])
    accent_lines();
"##)
}

pub fn generate_openscad(config: &Model3dConfig) -> String {
    let w = config.width.max(60.0);
    let h = config.height.max(35.0);
    let d = config.depth.max(90.0);

    let primary = style_primary(&config.style);
    let accent = style_accent(&config.style);
    let s_names = style_names(&config.style);

    let mut scad = String::new();
    scad.push_str("// Cyberdeck Enclosure v2 — generated by cyberdeck_core (Rust)\n");
    scad.push_str(&format!("// Style: {}, Colors: {:?}\n\n", config.style, s_names));
    scad.push_str("$fn = 32;\n\n");

    scad.push_str(&format!("w = {w:.2};\nh = {h:.2};\nd = {d:.2};\n\n"));

    scad.push_str(&format!(
        "module enclosure_body() {{ color(\"{p}\") {{
            {rc}
        }} }}

",
        p=primary,
        rc=round_cube("body_core", w, h * 0.6, d, 4.0).lines().skip(1).collect::<Vec<&str>>().join("\n")
    ));

    scad.push_str(&format!(
        "module enclosure_lid() {{ color(\"{p}\") {{
            {rc}
        }} }}

",
        p=primary,
        rc=round_cube("lid_core", w, 3.0, d, 3.0).lines().skip(1).collect::<Vec<&str>>().join("\n")
    ));

    scad.push_str(&vent_slots(w, d, 8));
    scad.push_str(&cable_channel(w, d));
    scad.push_str(&hinge());
    scad.push_str(&standoffs());
    scad.push_str(&io_cutouts());
    scad.push_str(&display_bezel(w, d));
    scad.push_str(&lid_latch());

    // Accent lines
    scad.push_str(&format!(
        "module accent_lines() {{\n    color(\"{a}\") {{\n", a=accent));
    for i in 0..4 {
        let y = -d / 2.0 + 12.0 + (i as f64) * (d - 24.0) / 3.0;
        scad.push_str(&format!(
            "        translate([0, {y:.2}, h/2 + 2])\n            cube([w - 24, 1.2, 0.5], center=true);\n", y=y));
    }
    scad.push_str("    }\n}\n\n");

    scad.push_str(&assembly());

    scad
}

pub fn generate_3d_json(config: &Model3dConfig, py: Python) -> PyResult<Py<PyDict>> {
    let scad = generate_openscad(config);
    let result = PyDict::new(py);
    result.set_item("openscad", &scad)?;
    result.set_item("style", &config.style)?;
    result.set_item("color", &config.color)?;

    let metadata = PyDict::new(py);
    metadata.set_item("width_mm", config.width)?;
    metadata.set_item("height_mm", config.height)?;
    metadata.set_item("depth_mm", config.depth)?;
    metadata.set_item("wall_thickness_mm", 2.0)?;
    metadata.set_item("standoff_type", "M2.5" )?;
    metadata.set_item("standoff_count", 6)?;

    let vol = (config.width * config.height * config.depth) / 1000.0;
    metadata.set_item("volume_cc", vol)?;
    metadata.set_item("estimated_print_time_minutes", (vol * 3.0) as u32)?;
    metadata.set_item("filament_grams", (vol * 1.24) as u32)?;
    result.set_item("metadata", metadata)?;

    let recs: Vec<String> = vec![
        "Print with 0.2mm layer height, 15-20% infill, 3 perimeters".into(),
        "Supports required for display bezel overhang (45° threshold)".into(),
        "Recommended filament: PETG for strength, PLA for ease (200-230°C)".into(),
        "Use M2.5 × 6mm brass inserts for standoffs — iron at 200°C".into(),
        "Apply 0.2mm horizontal expansion compensation for tight fits".into(),
        "Consider ASA/ABS if enclosure lives in hot car or direct sunlight".into(),
    ];
    result.set_item("print_recommendations", recs)?;

    let hardware: Vec<String> = vec![
        "6× M2.5 × 6mm brass heat-set inserts".into(),
        "4× M2.5 × 8mm socket head screws (lid)".into(),
        "4× M2.5 × 6mm flat head screws (SBC mount)".into(),
        "2× M2 × 4mm self-tapping screws (display bezel)".into(),
        "Optional: rubber feet 8mm × 3mm (4 pcs)".into(),
    ];
    result.set_item("hardware_bom", hardware)?;

    Ok(result.into())
}
