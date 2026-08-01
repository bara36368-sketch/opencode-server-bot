# Next Update Ideas (v7.1+)

> **NOTE:** When users mention "ideas" in conversation, they mean *feature ideas for the next update*, NOT the bot's `/ideas` command (which lists themed build concepts). If unsure, ask: "Do you mean `/ideas` build concepts or feature ideas for a new update?"

---

## v7.1 Features (IMPLEMENTED)

### 1. Local AI Tuner (`/localai`)
Fully offline LLM deck advisor. Picks board + model + quantization by budget from 2026 community benchmarks. Warns about the "NPU tax" (RKLLM conversion pain on RK3588 vs Hailo's plug-and-play).

**Commands:** `/localai` — overview | `/localai recommend <$budget>` — board+model combo | `/localai boards` — SBC/AI HAT database | `/localai models` — offline model database | `/localai npu` — NPU tax warning | `/localai estimate <board> <model>` — tokens/sec

**Databases:** `LOCAL_AI_BOARD_DATABASE`, `LOCAL_AI_MODEL_DATABASE`, `BUDGET_TIERS_LOCALAI`

### 2. Battery Hot-Swap & Supercap UPS (`/hotswap`)
Designs a battery system that can be swapped while running. Power-path / passthrough charging, diode-OR switching, supercap UPS hold window. Reference builds: HALGRID P-1, DINODECK-2026.

**Commands:** `/hotswap` — overview | `/hotswap design <board> <power_w>` — full power-path plan | `/hotswap parts` — component database | `/hotswap builds` — reference builds | `/hotswap guide` — wiring guide

**Databases:** `HOTSWAP_COMPONENT_DATABASE`, `HOTSWAP_REFERENCE_BUILDS`

### 3. Ortholinear & Split Keyboard DB (`/ortho`)
The exploding ortho/split keyboard trend: Corne, Helix, Lily58, Ferris Sweep, Sofle, Cantor, Planck, Preonic, Air40, Gherkin. Firmware guides (QMK/VIA/VIAL/ZMK), hand-wiring guide, and layout matching per build type.

**Commands:** `/ortho` — overview | `/ortho recommend <build_type>` — match to build | `/ortho firmware <kb>` — firmware guide | `/ortho wiring` — hand-wiring guide | `/ortho <keyboard>` — detail

**Databases:** `ORTHO_KEYBOARD_DATABASE`, `ORTHO_FIRMWARE_GUIDE`

### 4. Offline Survival Stack (`/offgridstack`)
The sarogamedev "survival platform" pattern: DTN (delay-tolerant sync), Kiwix ZIM + RAG, offline maps, P2P model sharing, mDNS/UDP beacon discovery. Combines the bot's mesh + kiwix into one offline planner.

**Commands:** `/offgridstack` — overview | `/offgridstack plan <budget>` — full stack plan | `/offgridstack components` — component database | `/offgridstack dtn` — DTN architecture | `/offgridstack reference` — reference build

**Databases:** `OFFGRID_STACK_COMPONENTS`, `OFFGRID_REFERENCE_BUILD`

### 5. Community Feature Board (`/features`)
Live mod requests voted by the community (cyberdeck.ing + r/cyberDeck): multi-layer macros, rear camera, speech-to-text, volume knob, slide-out keyboard, glasses display, projector mount, more USB.

**Commands:** `/features` — all mods, top votes first | `/features recommend <build_type>` — best mods per build type | `/features top` — top 3

**Databases:** `COMMUNITY_FEATURE_DATABASE`

### 6. Maximalist vs Minimalist Character Builder (`/character`)
Themed build generator across the 2026 spectrum: ultra-minimal (Pi Zero 2W + Gherkin 30% + Altoids tin + Sharp Memory Display) to maximalist (M.A.S.K. lunchbox with oscilloscope + HackRF + projector).

**Commands:** `/character` — list characters | `/character <minimal|maximal|field>` — full build plan | `/character compare` — side-by-side

**Databases:** `CHARACTER_TEMPLATES`

### 7. Scavenge Build Sourcing (`/scavenge`)
Budget-builder sourcing from thrift stores, e-waste centers, dollar stores, and eBay "for parts". Salvaged-parts build plans (bootstrap, mech keyboard focus, screen donor).

**Commands:** `/scavenge` — plans | `/scavenge sources` — sourcing locations | `/scavenge tips` — scavenging rules | `/scavenge <plan>` — specific plan

**Databases:** `SCAVENGE_SOURCES`, `SCAVENGE_BUILD_PLAN`

### 8. 2026 Hardware Radar (`/newhardware`)
Fresh 2026 boards: Pi 500+, Radxa Rock 5B/5 ITX 32GB, AI HAT+ (Hailo), SiSpeed Lichee Console 4A (RISC-V), x86 12W i5-class boards, Pi Zero 2W era.

**Commands:** `/newhardware` — all arrivals | `/newhardware detail <name>` — deep dive | `/newhardware compare <a> <b>` — side-by-side

**Databases:** `NEW_HARDWARE_2026`

---

## v7.0 Features

### 1. WriterDeck Mode (`/writerdeck`)
Dedicated distraction-free writing advisor. Recommends e-ink displays, minimalist OS configs (DietPi + CLI-only), writing software (WareWoolf, ZeroWriter, FocusWriter, WordGrinder), keyboard-focused input. Generates a complete "writerdeck profile" with battery-max power tuning, font packages, and Pomodoro timer setup.

**Commands:** `/writerdeck` — overview | `/writerdeck profile` — full writer build | `/writerdeck display` — e-ink recs | `/writerdeck software` — distraction-free writing tools | `/writerdeck os` — minimal OS with auto-boot-into-editor | `/writerdeck tune` — power-save config

**Databases:** `WRITERDECK_DISPLAYS`, `WRITER_SOFTWARE`, `WRITER_OS_TEMPLATES`, `WRITER_KEYBOARDS`

### 2. Thermal Management Designer (`/thermal`)
SBC cooling advisor. Calculates heat output per SBC+load, recommends heatsink + fan + vent sizes, estimates passive cooling viability, generates undervolt config (for Pi 5, Jetson). Thermal simulation estimates for enclosed vs ventilated cases.

**Commands:** `/thermal` — overview | `/thermal calc <sbc> <load>` — heat/CFM calc | `/thermal parts <sbc>` — compatible cooling hardware | `/thermal undervolt <sbc>` — undervolt config | `/thermal vent <sbc>` — vent sizing | `/thermal compare` — compare cooling solutions

**Databases:** `SBC_THERMAL_DATA`, `COOLING_PARTS_DATABASE`, `THERMAL_PASTE_DATABASE`

### 3. Multi-Build Comparator (`/compare`)
Side-by-side comparison of 2-3 saved build configs. Compares: total cost, weight, battery life, performance score, difficulty, size, display quality, upgradeability. Visual diff table.

**Commands:** `/compare` — list saved builds to compare | `/compare add <id1> <id2>` — compare 2 builds | `/compare add3 <id1> <id2> <id3>` — compare 3 | `/compare score <id>` — detailed scoring | `/compare clear` — reset selection

**Databases:** `COMPARISON_METRICS`

### 4. Build Cost Optimizer (`/cost`)
Finds cheapest component sources. Price-aware BOM with budget targets, alternate part suggestions, AliExpress/Amazon/Adafruit/PiShop comparisons, total-with-shipping estimates.

**Commands:** `/cost <budget>` — optimize BOM for budget | `/cost parts` — cheapest sources per part | `/cost alternate <part>` — cheaper substitutes | `/cost breakdown <build_id>` — line-item pricing | `/cost regions <region>` — region-aware pricing

**Databases:** `PRICE_SOURCE_DATABASE`, `REGION_VENDORS`, `BUDGET_TEMPLATES`

### 5. Upgrade Path Analyzer (`/upgrade`)
Given an existing build, suggests component upgrades ranked by perf/$ gain. Pi 4 → Pi 5, 4GB → 8GB, 7" → 10" display, 5000mAh → 10000mAh battery, add SDR module, etc.

**Commands:** `/upgrade <build_id>` — full upgrade report | `/upgrade list` — available upgrade paths | `/upgrade sbc` — SBC upgrade options | `/upgrade battery` — battery upgrade options | `/upgrade display` — display upgrade options

**Databases:** `UPGRADE_PATHS_DATABASE`, `PERF_BOOST_ESTIMATES`

### 6. Solar & Off-Grid Power Planner (`/solar`)
Solar charging system designer. Panel wattage calculator based on location sun-hours, battery bank sizing (LiPo/LiFePO4/18650), MPPT charge controller selection, runtime estimates per load profile, cable gauge for solar runs.

**Commands:** `/solar` — overview | `/solar calc <watt_hours> <location>` — panel + battery sizing | `/solar parts` — solar components | `/solar setup` — complete off-grid config | `/solar regions` — sun-hours by region | `/solar cable` — wire gauge calc

**Databases:** `SOLAR_PANEL_DATABASE`, `BATTERY_BANK_DATABASE`, `SOLAR_CONTROLLER_DATABASE`, `SUN_HOURS_BY_REGION`, `OFFGRID_TEMPLATES`

### 7. Beginner Build Wizard (`/wizard`)
Guided Q&A to build a first cyberdeck. Step by step: budget → purpose → skill level → portability → display size → battery needs. Generates a complete shopping list with links, assembly order, and estimated build time.

**Commands:** `/wizard` — start wizard | `/wizard step <n>` — jump to step | `/wizard reset` — restart | `/wizard quick <purpose> <budget>` — skip to result | `/wizard faq` — beginner FAQ

**Databases:** `WIZARD_QUESTIONS`, `WIZARD_TEMPLATES`, `BEGINNER_MISTAKES_DB`, `TOOL_REQUIREMENTS`

### 8. Build Sharing & Export (`/share`)
Export a complete build as: Reddit/Hackaday build markdown post, GitHub repo template, Printables/Thingiverse documentation page, CSV BOM, wiring diagram SVG, parts shopping list. One-command publish workflow.

**Commands:** `/share <build_id>` — share menu | `/share reddit <build_id>` — generate Reddit post | `/share hackaday <build_id>` — Hackaday.io template | `/share github <build_id>` — GitHub repo scaffold | `/share bom <build_id>` — CSV BOM | `/share wiring <build_id>` — wiring diagram | `/share publish <build_id>` — full export

**Databases:** `SHARE_TEMPLATES`, `EXPORT_THEMES`

---

## How to Decide

- **Most community buzz**: #1 (WriterDeck) — writerdecks are trending hard in 2026, dedicated subreddit
- **Practical value**: #2 (Thermal) — every build needs cooling, few tools help
- **Decision support**: #3 (Comparator) + #7 (Wizard) — help beginners and intermediates decide
- **Cost savings**: #4 (Cost Optimizer) — builders love saving money
- **Growth path**: #5 (Upgrade) — keeps users engaged with their existing builds
- **Off-grid trend**: #6 (Solar) — solarpunk is fastest-growing aesthetic
- **Community sharing**: #8 (Share) — documentation is the #1 thing the community asks for
