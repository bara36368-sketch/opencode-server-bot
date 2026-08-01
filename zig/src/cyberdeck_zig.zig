const std = @import("std");
const mem = std.mem;
const math = std.math;
const Stringify = std.json.Stringify;

const allocator = std.heap.page_allocator;

fn stringifyAlloc(value: anytype, opts: Stringify.Options) ![]u8 {
    return try Stringify.valueAlloc(allocator, value, opts);
}

fn toCString(slice: []const u8) [*:0]const u8 {
    const buf = allocator.dupeZ(u8, slice) catch unreachable;
    return buf.ptr;
}

fn formatFloat(v: f64) f64 {
    return @round(v * 1000.0) / 1000.0;
}

fn formatFloat1(v: f64) f64 {
    return @round(v * 10.0) / 10.0;
}

export fn cyberdeck_free_string(s: [*:0]const u8) void {
    const len = mem.len(s);
    allocator.free(s[0..len :0]);
}

export fn zig_nato_rail_layout(rails: i32, deck_width_mm: f64, _deck_depth_mm: f64) ?[*:0]const u8 {
    _ = _deck_depth_mm;
    const r = @max(1, @min(rails, 12));
    const spacing = deck_width_mm / @as(f64, @floatFromInt(r + 1));
    const hole_diameter = 4.5;
    const slot_width = 8.0;
    const slot_depth = 6.0;

    var hole_positions: [12]f64 = undefined;
    for (0..@as(usize, @intCast(r))) |i| {
        hole_positions[i] = formatFloat(spacing * @as(f64, @floatFromInt(@as(i32, @intCast(i + 1)))));
    }

    const result = struct {
        rails: i32,
        spacing_mm: f64,
        hole_diameter_mm: f64,
        slot_width_mm: f64,
        slot_depth_mm: f64,
        holes_mm: []const f64,
        total_width_mm: f64,
    }{
        .rails = r,
        .spacing_mm = formatFloat(spacing),
        .hole_diameter_mm = hole_diameter,
        .slot_width_mm = slot_width,
        .slot_depth_mm = slot_depth,
        .holes_mm = hole_positions[0..@as(usize, @intCast(r))],
        .total_width_mm = deck_width_mm,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_battery_capacity(cells: i32, mah_per_cell: f64, voltage: f64, load_watts: f64) ?[*:0]const u8 {
    const c = @max(1, cells);
    const total_mah = @as(f64, @floatFromInt(c)) * mah_per_cell;
    const total_wh = total_mah * voltage / 1000.0;
    const runtime_h = if (load_watts > 0) formatFloat1(total_wh / load_watts) else 0;
    const weight_g = formatFloat(@as(f64, @floatFromInt(c)) * 48.0);

    const result = struct {
        cells: i32,
        total_mah: f64,
        total_wh: f64,
        voltage: f64,
        load_watts: f64,
        runtime_hours: f64,
        weight_grams: f64,
    }{
        .cells = c,
        .total_mah = formatFloat(total_mah),
        .total_wh = formatFloat(total_wh),
        .voltage = voltage,
        .load_watts = load_watts,
        .runtime_hours = runtime_h,
        .weight_grams = weight_g,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_battery_optimizer(target_wh: f64, cell_mah: f64, cell_voltage: f64) ?[*:0]const u8 {
    const cell_wh = cell_mah * cell_voltage / 1000.0;
    const cells_needed = @ceil(target_wh / cell_wh);

    const Config = struct { label: []const u8, cells: i32, series: i32, parallel: i32, voltage: f64, capacity_wh: f64 };
    var configs: [4]Config = undefined;
    const opts = [_]struct { label: []const u8, s: i32, p: i32 }{
        .{ .label = "1S", .s = 1, .p = @as(i32, @intCast(@max(1, @as(i64, @intFromFloat(@ceil(cells_needed / 1.0)))))) },
        .{ .label = "2S", .s = 2, .p = @as(i32, @intCast(@max(1, @as(i64, @intFromFloat(@ceil(cells_needed / 2.0)))))) },
        .{ .label = "3S", .s = 3, .p = @as(i32, @intCast(@max(1, @as(i64, @intFromFloat(@ceil(cells_needed / 3.0)))))) },
        .{ .label = "4S", .s = 4, .p = @as(i32, @intCast(@max(1, @as(i64, @intFromFloat(@ceil(cells_needed / 4.0)))))) },
    };

    for (&configs, opts) |*cfg, opt| {
        const total_cells = opt.s * opt.p;
        cfg.* = Config{
            .label = opt.label,
            .cells = total_cells,
            .series = opt.s,
            .parallel = opt.p,
            .voltage = formatFloat(@as(f64, @floatFromInt(opt.s)) * cell_voltage),
            .capacity_wh = formatFloat(@as(f64, @floatFromInt(total_cells)) * cell_wh),
        };
    }

    const result = struct {
        target_wh: f64,
        cell_wh: f64,
        cells_needed: f64,
        configs: []const Config,
    }{
        .target_wh = target_wh,
        .cell_wh = formatFloat(cell_wh),
        .cells_needed = cells_needed,
        .configs = &configs,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_antenna_calc(freq_mhz: f64) ?[*:0]const u8 {
    if (freq_mhz <= 0) return null;
    const wavelength_cm = 29979.2458 / freq_mhz;
    const quarter_wave_cm = wavelength_cm / 4.0;
    const half_wave_cm = wavelength_cm / 2.0;

    const CableLoss = struct { cable: []const u8, loss_db_per_m: f64 };
    const cable_losses = [_]CableLoss{
        .{ .cable = "RG58", .loss_db_per_m = formatFloat(0.5 * @sqrt(freq_mhz / 100.0)) },
        .{ .cable = "LMR200", .loss_db_per_m = formatFloat(0.3 * @sqrt(freq_mhz / 100.0)) },
        .{ .cable = "LMR400", .loss_db_per_m = formatFloat(0.15 * @sqrt(freq_mhz / 100.0)) },
    };

    const connector = if (freq_mhz <= 1000) "SMA / BNC" else if (freq_mhz <= 6000) "SMA / N-Type" else "N-Type / 2.4mm";

    const result = struct {
        freq_mhz: f64,
        wavelength_cm: f64,
        quarter_wave_cm: f64,
        half_wave_cm: f64,
        connector: []const u8,
        cable_losses: []const CableLoss,
    }{
        .freq_mhz = freq_mhz,
        .wavelength_cm = formatFloat(wavelength_cm),
        .quarter_wave_cm = formatFloat(quarter_wave_cm),
        .half_wave_cm = formatFloat(half_wave_cm),
        .connector = connector,
        .cable_losses = &cable_losses,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_mesh_range(power_dbm: i32, freq_mhz: f64, gain_dbi: f64, sensitivity_dbm: i32) ?[*:0]const u8 {
    if (freq_mhz <= 0) return null;
    const tx_power = @as(f64, @floatFromInt(power_dbm));
    const rx_sens = @as(f64, @floatFromInt(sensitivity_dbm));
    const total_gain = gain_dbi * 2.0;
    const path_loss_budget = tx_power + total_gain - rx_sens;
    const freq_hz = freq_mhz * 1_000_000.0;
    const lambda = 299_792_458.0 / freq_hz;
    const distance_m = math.pow(f64, 10.0, (path_loss_budget - 20.0 * @log10(lambda) - 20.0 * @log10(4.0 * math.pi)) / 20.0);
    const distance_km = distance_m / 1000.0;

    const range_str = if (distance_km < 1) "<1 km" else if (distance_km < 10) "1-10 km" else if (distance_km < 50) "10-50 km" else "50+ km (ideal)";

    const result = struct {
        power_dbm: i32,
        freq_mhz: f64,
        gain_dbi: f64,
        sensitivity_dbm: i32,
        path_loss_budget_db: f64,
        distance_m: f64,
        distance_km: f64,
        los_range_estimate: []const u8,
    }{
        .power_dbm = power_dbm,
        .freq_mhz = freq_mhz,
        .gain_dbi = gain_dbi,
        .sensitivity_dbm = sensitivity_dbm,
        .path_loss_budget_db = formatFloat(path_loss_budget),
        .distance_m = formatFloat(distance_m),
        .distance_km = formatFloat(distance_km),
        .los_range_estimate = range_str,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_print_cost(volume_cm3: f64, material_price_per_g: f64, density_g_per_cm3: f64, print_hours: f64, labor_per_hour: f64) ?[*:0]const u8 {
    const weight_g = volume_cm3 * density_g_per_cm3;
    const material_cost = weight_g * material_price_per_g;
    const labor_cost = print_hours * labor_per_hour;
    const total_cost = material_cost + labor_cost;

    const result = struct {
        volume_cm3: f64,
        weight_grams: f64,
        material_price_per_g: f64,
        material_cost: f64,
        print_hours: f64,
        labor_per_hour: f64,
        labor_cost: f64,
        total_cost: f64,
    }{
        .volume_cm3 = formatFloat(volume_cm3),
        .weight_grams = formatFloat(weight_g),
        .material_price_per_g = material_price_per_g,
        .material_cost = formatFloat(material_cost),
        .print_hours = print_hours,
        .labor_per_hour = labor_per_hour,
        .labor_cost = formatFloat(labor_cost),
        .total_cost = formatFloat(total_cost),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_filament_calc(spool_grams: f64, density: f64, diameter_mm: f64) ?[*:0]const u8 {
    const radius_mm = diameter_mm / 2.0;
    const cross_section_mm2 = math.pi * radius_mm * radius_mm;
    const cross_section_cm2 = cross_section_mm2 / 100.0;
    const total_length_cm = spool_grams / (density * cross_section_cm2);
    const total_length_m = total_length_cm / 100.0;

    const result = struct { spool_grams: f64, density: f64, diameter_mm: f64, total_length_m: f64 }{
        .spool_grams = spool_grams,
        .density = density,
        .diameter_mm = diameter_mm,
        .total_length_m = formatFloat(total_length_m),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_sliding_screen_rail(screen_width_mm: f64, screen_depth_mm: f64, rail_length_mm: f64, carriage_count: i32) ?[*:0]const u8 {
    const cc = @max(1, carriage_count);
    const overhang = rail_length_mm - screen_depth_mm;
    const carriage_spacing = if (cc > 1) (screen_depth_mm - 20.0) / @as(f64, @floatFromInt(cc - 1)) else screen_depth_mm;

    const result = struct {
        screen_width_mm: f64,
        screen_depth_mm: f64,
        rail_length_mm: f64,
        overhang_mm: f64,
        carriage_count: i32,
        carriage_spacing_mm: f64,
    }{
        .screen_width_mm = screen_width_mm,
        .screen_depth_mm = screen_depth_mm,
        .rail_length_mm = rail_length_mm,
        .overhang_mm = formatFloat(overhang),
        .carriage_count = cc,
        .carriage_spacing_mm = formatFloat(carriage_spacing),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_esp32_power(wifi_active: i32, cpu_mhz: i32, ble_enabled: i32, peripherals_ma: f64) ?[*:0]const u8 {
    const wifi_ma: f64 = if (wifi_active != 0) 80.0 else 0.0;
    const ble_ma: f64 = if (ble_enabled != 0) 10.0 else 0.0;
    const cpu_ma: f64 = @as(f64, @floatFromInt(cpu_mhz)) * 0.015 + 15.0;
    const total_ma = wifi_ma + ble_ma + cpu_ma + peripherals_ma;
    const power_mw = total_ma * 3.3;
    const power_w = power_mw / 1000.0;

    const result = struct {
        wifi_active: i32,
        cpu_mhz: i32,
        ble_enabled: i32,
        cpu_current_ma: f64,
        wifi_current_ma: f64,
        ble_current_ma: f64,
        total_current_ma: f64,
        power_watts: f64,
    }{
        .wifi_active = wifi_active,
        .cpu_mhz = cpu_mhz,
        .ble_enabled = ble_enabled,
        .cpu_current_ma = formatFloat(cpu_ma),
        .wifi_current_ma = wifi_ma,
        .ble_current_ma = ble_ma,
        .total_current_ma = formatFloat(total_ma),
        .power_watts = formatFloat(power_w),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_throughput_est(protocol: [*:0]const u8, nodes: i32, hops: i32) ?[*:0]const u8 {
    const proto = mem.sliceTo(protocol, 0);
    const base_bps: f64 = if (mem.eql(u8, proto, "esp_now")) 1_000_000
        else if (mem.eql(u8, proto, "wifi_mesh")) 10_000_000
        else if (mem.eql(u8, proto, "lora")) 250
        else 0;
    const hop_loss = @as(f64, @floatFromInt(@max(1, hops))) * 0.15;
    const node_overhead = @as(f64, @floatFromInt(@max(1, nodes))) * 0.02;
    const effective = base_bps * (1.0 - hop_loss) * (1.0 - node_overhead);

    const result = struct {
        protocol: []const u8,
        base_bps: f64,
        nodes: i32,
        hops: i32,
        hop_loss_pct: f64,
        node_overhead_pct: f64,
        effective_bps: f64,
        effective_kbps: f64,
    }{
        .protocol = proto,
        .base_bps = base_bps,
        .nodes = nodes,
        .hops = hops,
        .hop_loss_pct = formatFloat(hop_loss * 100.0),
        .node_overhead_pct = formatFloat(node_overhead * 100.0),
        .effective_bps = formatFloat(effective),
        .effective_kbps = formatFloat(effective / 1000.0),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_edge_ai_est(model_type: [*:0]const u8, ram_kb: i32, psram_kb: i32) ?[*:0]const u8 {
    const mtype = mem.sliceTo(model_type, 0);
    const model_ram_kb: f64 = if (mem.eql(u8, mtype, "vision")) 500.0
        else if (mem.eql(u8, mtype, "audio")) 200.0
        else if (mem.eql(u8, mtype, "pose")) 800.0
        else 300.0;
    const total_ram = @as(f64, @floatFromInt(ram_kb)) + @as(f64, @floatFromInt(psram_kb));
    const fits = total_ram >= model_ram_kb;
    const fps: f64 = if (fits) blk: {
        if (mem.eql(u8, mtype, "audio")) break :blk 50.0;
        if (mem.eql(u8, mtype, "vision")) break :blk 12.0;
        if (mem.eql(u8, mtype, "pose")) break :blk 8.0;
        break :blk 20.0;
    } else 0;

    const result = struct {
        model_type: []const u8,
        estimated_ram_kb: f64,
        available_ram_kb: f64,
        fits_in_memory: bool,
        estimated_fps: f64,
    }{
        .model_type = mtype,
        .estimated_ram_kb = model_ram_kb,
        .available_ram_kb = total_ram,
        .fits_in_memory = fits,
        .estimated_fps = fps,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_heat_sink_calc(power_watts: f64, ambient_c: f64, max_temp_c: f64) ?[*:0]const u8 {
    const temp_rise = max_temp_c - ambient_c;
    const required_rth = if (power_watts > 0) temp_rise / power_watts else 999.0;
    const min_surface_area_cm2 = 500.0 / required_rth;
    const fin_count = @ceil(min_surface_area_cm2 / 50.0);

    const result = struct {
        power_watts: f64,
        ambient_c: f64,
        max_temp_c: f64,
        temp_rise_c: f64,
        required_thermal_resistance_c_per_w: f64,
        min_surface_area_cm2: f64,
        recommended_fin_count: i64,
    }{
        .power_watts = power_watts,
        .ambient_c = ambient_c,
        .max_temp_c = max_temp_c,
        .temp_rise_c = temp_rise,
        .required_thermal_resistance_c_per_w = formatFloat(required_rth),
        .min_surface_area_cm2 = formatFloat(min_surface_area_cm2),
        .recommended_fin_count = @as(i64, @intFromFloat(fin_count)),
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

test "nato rail layout" {
    const result = zig_nato_rail_layout(3, 200.0, 150.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "battery capacity" {
    const result = zig_battery_capacity(6, 3500.0, 3.7, 10.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "antenna calc" {
    const result = zig_antenna_calc(433.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "mesh range" {
    const result = zig_mesh_range(20, 915.0, 3.0, -120);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "print cost" {
    const result = zig_print_cost(100.0, 1.5, 1.24, 6.0, 25000.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "sliding screen" {
    const result = zig_sliding_screen_rail(180.0, 120.0, 200.0, 4);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "esp32 power" {
    const result = zig_esp32_power(1, 240, 1, 20.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "throughput" {
    const result = zig_throughput_est("lora", 5, 2);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "edge ai" {
    const result = zig_edge_ai_est("vision", 512, 8192);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "heat sink" {
    const result = zig_heat_sink_calc(15.0, 25.0, 85.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "battery optimizer" {
    const result = zig_battery_optimizer(100.0, 3500.0, 3.7);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

const PanelRec = struct { label: []const u8, watts: f64, amps: f64 };

export fn zig_solar_sizer(power_wh_per_day: f64, sun_hours: f64, panel_efficiency: f64, battery_voltage: f64) ?[*:0]const u8 {
    const panel_wattage = if (sun_hours > 0) power_wh_per_day / sun_hours / panel_efficiency else 0;
    const charge_current_a = if (battery_voltage > 0) panel_wattage / battery_voltage else 0;
    const daily_ah = if (battery_voltage > 0) power_wh_per_day / battery_voltage else 0;
    const panel_recommendations = [3]PanelRec{
        .{ .label = "Minimal", .watts = formatFloat(panel_wattage), .amps = formatFloat(charge_current_a) },
        .{ .label = "Recommended", .watts = formatFloat(panel_wattage * 1.3), .amps = formatFloat(charge_current_a * 1.3) },
        .{ .label = "Overland", .watts = formatFloat(panel_wattage * 1.5), .amps = formatFloat(charge_current_a * 1.5) },
    };

    const result = struct {
        power_wh_per_day: f64,
        sun_hours: f64,
        panel_efficiency: f64,
        battery_voltage: f64,
        panel_wattage: f64,
        charge_current_a: f64,
        daily_ah: f64,
        recommendations: []const PanelRec,
    }{
        .power_wh_per_day = power_wh_per_day,
        .sun_hours = sun_hours,
        .panel_efficiency = panel_efficiency,
        .battery_voltage = battery_voltage,
        .panel_wattage = formatFloat(panel_wattage),
        .charge_current_a = formatFloat(charge_current_a),
        .daily_ah = formatFloat(daily_ah),
        .recommendations = &panel_recommendations,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

export fn zig_cable_sizer(current_a: f64, length_m: f64, max_drop_pct: f64, voltage: f64) ?[*:0]const u8 {
    const max_drop_v = voltage * max_drop_pct / 100.0;

    const WireSpec = struct { gauge: []const u8, mm2: f64, ohms_per_km: f64 };
    const wires = [_]WireSpec{
        .{ .gauge = "30 AWG", .mm2 = 0.05, .ohms_per_km = 340.0 },
        .{ .gauge = "28 AWG", .mm2 = 0.08, .ohms_per_km = 210.0 },
        .{ .gauge = "26 AWG", .mm2 = 0.13, .ohms_per_km = 130.0 },
        .{ .gauge = "24 AWG", .mm2 = 0.21, .ohms_per_km = 84.0 },
        .{ .gauge = "22 AWG", .mm2 = 0.33, .ohms_per_km = 53.0 },
        .{ .gauge = "20 AWG", .mm2 = 0.52, .ohms_per_km = 33.0 },
        .{ .gauge = "18 AWG", .mm2 = 0.82, .ohms_per_km = 21.0 },
        .{ .gauge = "16 AWG", .mm2 = 1.31, .ohms_per_km = 13.0 },
        .{ .gauge = "14 AWG", .mm2 = 2.08, .ohms_per_km = 8.5 },
        .{ .gauge = "12 AWG", .mm2 = 3.31, .ohms_per_km = 5.2 },
    };

    const total_length_m = length_m * 2.0;
    var suitable: [10]WireSpec = undefined;
    var count: usize = 0;
    for (wires) |w| {
        const drop_v = current_a * w.ohms_per_km * total_length_m / 1000.0;
        if (drop_v <= max_drop_v) {
            suitable[count] = w;
            count += 1;
        }
    }

    const best_gauge = if (count > 0) suitable[0].gauge else "None suitable";
    const best_drop_v = if (count > 0) formatFloat(current_a * suitable[0].ohms_per_km * total_length_m / 1000.0) else 0;
    const suitable_slice = suitable[0..count];

    const result = struct {
        current_a: f64,
        length_m: f64,
        max_drop_pct: f64,
        voltage: f64,
        max_drop_v: f64,
        total_loop_length_m: f64,
        best_gauge: []const u8,
        best_voltage_drop_v: f64,
        suitable_gauges: []const WireSpec,
    }{
        .current_a = current_a,
        .length_m = length_m,
        .max_drop_pct = max_drop_pct,
        .voltage = voltage,
        .max_drop_v = formatFloat(max_drop_v),
        .total_loop_length_m = total_length_m,
        .best_gauge = best_gauge,
        .best_voltage_drop_v = best_drop_v,
        .suitable_gauges = suitable_slice,
    };
    const raw = stringifyAlloc(result, .{}) catch return null;
    return toCString(raw);
}

test "filament calc" {
    const result = zig_filament_calc(1000.0, 1.24, 1.75);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "solar sizer" {
    const result = zig_solar_sizer(100.0, 5.0, 0.8, 12.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}

test "cable sizer" {
    const result = zig_cable_sizer(5.0, 2.0, 3.0, 12.0);
    defer if (result) |r| cyberdeck_free_string(r);
    try std.testing.expect(result != null);
}
