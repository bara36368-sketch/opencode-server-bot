const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lib = b.addExecutable(.{
        .name = "cyberdeck_zig",
        .root_source_file = b.path("src/cyberdeck_zig.zig"),
        .target = target,
        .optimize = optimize,
    });
    lib.rdynamic = true;

    const lib_step = b.step("lib", "Build shared library");
    const install = b.addInstallArtifact(lib, .{ .dest_sub_path = "bin/cyberdeck_zig.dll" });
    lib_step.dependOn(&install.step);

    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/cyberdeck_zig.zig"),
        .target = target,
        .optimize = optimize,
    });
    const run_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}
