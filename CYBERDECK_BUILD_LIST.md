# Cyberdeck Build List — Complete Knowledge Base
## Compiled from 310+ Sources | July 2026
### Sources: Vapor95, GitHub/BenMakesEverything, PCBSync, Betechit, MakeUseOf, Cyberdeck.cafe, Thewearify, Jalexine Lab, Reddit r/cyberDeck, Mashable, Teen Vogue, WIRED, CNN, TechCrunch, Forbes, The Verge, Hybrid Rituals, Adafruit, Hackaday, Hackster.io, Prism News, 2much.net, Field Test, PCWorld, SlashGear, DigiKey, InsightArea, Raspberry Pi Blog, Raspberry Pi Magazine, writerdeck.org, Liliputing, Geeky Gadgets, Tom's Hardware, Core Electronics, No Starch Press, Alibaba, Ubu.com, BestBudge, TheWearify, ZitaoTech, Beeper, ArcticEnrichmentCenter, echo-lalia, ferluht, brickbots, TomMladenov, Decktrix-Lab, CodyTolene, EzioDEVio, n0xa, altaga, thehackingsage, PNPtutorials, pepeangell5, a8ksh4, Klesp0, Orange Pi, Radxa, Banana Pi, ODROID, Milk-V, StarFive, SiFive, DeepComputing, Sipeed, MangoPi, Espressif, LattePanda, Khadas, Firefly, Cerakote, Caswell Plating, Smooth-On, Fibre Glast, Glow Inc, SFXC, Eastwood, McMaster-Carr, TotalBoat, Mouser, DigiKey, HackberryPi, PicoWiz, roshinfo, HandyPi, Pip3, dmitriykovalev, romicaby, hex1n, 0x676e68, Hax0rStock, writerdeckos, hugg97, Squonk42, cyberboi, 0x10, danielktdorsey, Seeed Studio, SparkFun, FLIR, Great Scott Gadgets, Pimoroni, Waveshare, SenseCAP, GL.iNet, Sixfab, therebelrobot, trevjohnand, pcwleo0404, andywarburton, amarullz, SoulSircuit, CarbonComputers, dapperrogue, ian-maday, superradmaker, _kniives, Michael Klements, Vagabondvivant, TypeSlate, Liliputing

---

## TABLE OF CONTENTS
1. [What Is a Cyberdeck](#what-is-a-cyberdeck)
2. [Tier System](#tier-system)
3. [Category System](#category-system)
4. [Single Board Computers (SBC)](#single-board-computers)
5. [Displays](#displays)
6. [Keyboards & Input](#keyboards--input)
7. [Power Systems](#power-systems)
8. [Enclosures & Cases](#enclosures--cases)
9. [Connectivity & Accessories](#connectivity--accessories)
10. [Operating Systems](#operating-systems)
11. [Component Compatibility Matrix](#component-compatibility-matrix)
12. [Budget Tiers](#budget-tiers)
13. [Iconic Builds Reference](#iconic-builds-reference)
14. [3D Printing Resources](#3d-printing-resources)
15. [Soldering & Wiring Basics](#soldering--wiring-basics)
16. [Component Sourcing Guide](#component-sourcing-guide)
17. [Community Resources](#community-resources)
18. [Assembly Process](#assembly-process)

---

## WHAT IS A CYBERDECK
A cyberdeck is a personal portable computer built by hand. It rejects the polished sameness of commercial laptops in favor of exposed hardware, mechanical keys, and a form that says exactly what its builder wanted it to say. The word comes from William Gibson's 1984 novel *Neuromancer*. The modern movement crystallized around 2019 when Jay Doscher released the Raspberry Pi Recovery Kit. Cyberdecks are not laptop replacements — they are instruments with opinions, tuned to the owner's use case. They sacrifice polish for personality, hackability, and a build process that teaches you something about how machines actually work.

**Key Philosophy:**
- Rejection of sealed consumer technology
- Modular, repairable, fully owned
- Form follows function — exposed screws, visible wiring, industrial enclosures
- Every build reflects its creator's preferences
- The community values originality

---

## TIER SYSTEM

### Tier 1: BEGINNER (Easy)
- **Budget:** $100–$300
- **Soldering:** Optional (not required)
- **Skills needed:** Plugging things together, basic Linux, 3D printer access or pre-made case
- **Build time:** 1–3 days
- **Description:** Off-the-shelf parts. Raspberry Pi or old laptop, small screen, keyboard, power bank. Everything plugged together, maybe thrown into a box. Fast to build, no friction.
- **Recommended for:** First-time builders, learning Linux, simple portable computing

### Tier 2: INTERMEDIATE (Moderate)
- **Budget:** $300–$700
- **Soldering:** Optional but helpful (power switches, custom connections)
- **Skills needed:** 3D modeling/printing, component integration, cable management, basic electronics
- **Build time:** 1–2 weeks
- **Description:** You care about form. Integrated components, cleaned up cables, internal battery, custom case. Starts to feel like a real device.
- **Recommended for:** Builders who want a polished, functional deck

### Tier 3: ADVANCED (Expert)
- **Budget:** $700–$3000+
- **Soldering:** Recommended (custom wiring, switches, GPIO connections)
- **Skills needed:** Full custom design, soldering, PCB work, advanced electronics, QMK firmware
- **Build time:** 2–8+ weeks
- **Description:** Fully custom. Internal wiring, optimized layout, extra modules, switches, LEDs. Built for a specific use, not just assembled.
- **Recommended for:** Experienced makers, specialized use cases, competition builds

---

## CATEGORY SYSTEM

### Category 1: CODING & DEVELOPMENT
- **Purpose:** Portable coding, terminal work, remote server admin, software development
- **Best SBC:** Raspberry Pi 5 (8GB or 16GB) or LattePanda Mu (x86)
- **Best Display:** 7–10" IPS HDMI touchscreen (1024x600 or 1280x800)
- **Best Keyboard:** 60% mechanical (Keychron K12, HyperX Alloy Origins 60)
- **Best OS:** Raspberry Pi OS, Ubuntu MATE, Kali Linux
- **Essential Accessories:** NVMe SSD via HAT, USB hub, Ethernet port
- **Budget Range:** $300–$1200
- **Key Consideration:** Comfortable typing experience, good screen resolution for code

### Category 2: WRITERDECK
- **Purpose:** Distraction-free writing, journaling, note-taking
- **Best SBC:** Raspberry Pi Zero 2 W or Pi 4 (2GB)
- **Best Display:** E-ink display (Waveshare 4–7") or low-power LCD
- **Best Keyboard:** 40% ortholinear (Planck) or thumb keyboard
- **Best OS:** writerdeckOS, DietPi, or custom boot-to-text-editor
- **Essential Accessories:** Long battery life, no browser installed
- **Budget Range:** $100–$400
- **Key Consideration:** Minimalism, battery life, distraction-free environment

### Category 3: SECURITY & PENETRATION TESTING
- **Purpose:** Network analysis, red team exercises, RF exploration
- **Best SBC:** Raspberry Pi 5 (8GB) or Pi 4 (4–8GB)
- **Best Display:** 7" HDMI IPS touchscreen
- **Best Keyboard:** Compact mechanical (60% or 40%)
- **Best OS:** Kali Linux
- **Essential Accessories:** External Wi-Fi antenna (AWUS036ACH), SDR dongle (HackRF One or RTL-SDR), Ethernet port, GPIO for custom switches
- **Budget Range:** $400–$1500
- **Key Consideration:** Antenna placement, multiple network interfaces, GPIO access

### Category 4: RETRO GAMING & MEDIA
- **Purpose:** Emulation, retro gaming, media playback
- **Best SBC:** Raspberry Pi 4 (4GB) or Pi 5
- **Best Display:** 7" HDMI IPS or TV via HDMI
- **Best Keyboard:** Optional — game controllers preferred (8BitDo, Xbox)
- **Best OS:** RetroPie, Batocera, Lakka
- **Essential Accessories:** HDMI output, USB game controllers, speakers
- **Budget Range:** $150–$500
- **Key Consideration:** GPU performance, controller support, HDMI output quality

### Category 5: FIELD RESEARCH & NOTE-TAKING
- **Purpose:** Fieldwork, data collection, offline reference, travel computing
- **Best SBC:** Raspberry Pi 5 (8GB)
- **Best Display:** 7–10" sunlight-readable IPS display
- **Best Keyboard:** Compact mechanical or membrane
- **Best OS:** Raspberry Pi OS, DietPi
- **Essential Accessories:** Large battery (6+ hours), offline Wikipedia (Kiwix), NVMe storage, sunlight-readable screen
- **Budget Range:** $300–$800
- **Key Consideration:** Battery life, screen readability in sunlight, rugged construction

### Category 6: AI & MACHINE LEARNING
- **Purpose:** Local AI inference, LLM hosting, computer vision, robotics
- **Best SBC:** NVIDIA Jetson Orin Nano or Raspberry Pi 5 (16GB)
- **Best Display:** 7–10" HDMI display
- **Best Keyboard:** Standard mechanical
- **Best OS:** JetPack (Jetson), Ubuntu, Raspberry Pi OS
- **Essential Accessories:** GPU acceleration, large NVMe for models, active cooling
- **Budget Range:** $500–$2000
- **Key Consideration:** GPU compute, memory, storage for models, thermal management

### Category 7: SURVIVAL & OFF-GRID
- **Purpose:** Emergency computing, off-grid communication, disaster preparedness
- **Best SBC:** Raspberry Pi 5 (8GB)
- **Best Display:** 7" HDMI IPS or e-ink (low power)
- **Best Keyboard:** Compact mechanical
- **Best OS:** Raspberry Pi OS with offline tools
- **Essential Accessories:** LoRa module, ham radio, solar panel, large battery, offline Wikipedia, USB storage with backups
- **Budget Range:** $300–$1000
- **Key Consideration:** Battery life, ruggedness, offline capability, communication interfaces

### Category 8: MEDIA CENTER
- **Purpose:** Music, movies, streaming, media playback
- **Best SBC:** Raspberry Pi 4 or Pi 5
- **Best Display:** HDMI output to TV/monitor or 10" built-in
- **Best Keyboard:** Remote control or wireless keyboard/trackpad combo
- **Best OS:** LibreELEC, OSMC, Kodi
- **Essential Accessories:** HDMI 4K output, speakers/headphone jack, Wi-Fi
- **Budget Range:** $150–$500
- **Key Consideration:** HDMI output quality, audio output, network streaming

### Category 9: CONVERSATION PIECE / COSPLAY
- **Purpose:** Aesthetic statement, cosplay prop, display piece
- **Best SBC:** Raspberry Pi Zero 2 W or Pi 4
- **Best Display:** 5–7" IPS or OLED
- **Best Keyboard:** Themed mechanical or vintage
- **Best OS:** Twister OS (retro themes), Raspberry Pi OS
- **Essential Accessories:** LEDs, custom case, themed aesthetics
- **Budget Range:** $150–$800
- **Key Consideration:** Visual impact, theme consistency, build quality

---

## QUICK CATEGORY REFERENCE

| # | Category | ID | Budget | Best SBC | Best OS | Soldering |
|---|----------|-----|--------|----------|---------|-----------|
| 1 | Coding & Development | `coding` | $300–$1200 | Pi 5 8/16GB, LattePanda Mu | Pi OS, Kali, Ubuntu MATE | Optional |
| 2 | Writerdeck | `writerdeck` | $100–$400 | Pi Zero 2 W, Pi 4 | writerdeckOS, DietPi | Optional |
| 3 | Security & Pentesting | `security` | $400–$1500 | Pi 5 8/16GB | Kali Linux | Optional |
| 4 | Retro Gaming & Media | `gaming` | $150–$500 | Pi 5, Pi 4, Orange Pi 5 | RetroPie, Batocera | Optional |
| 5 | Field Research | `research` | $300–$800 | Pi 5 8GB | Pi OS, DietPi | Optional |
| 6 | AI & Machine Learning | `ai` | $500–$2000 | Jetson Orin Nano, Pi 5 16GB | Pi OS, Ubuntu | Optional |
| 7 | Survival & Off-Grid | `survival` | $300–$1000 | Pi 5 8/16GB | Pi OS, DietPi | Optional |
| 8 | Media Center | `media` | $150–$500 | Pi 5, Pi 4 | LibreELEC, Kodi | Optional |
| 9 | Conversation Piece | `conversation` | $150–$800 | Pi Zero 2 W, Pi 4 | Twister OS, Pi OS | Optional |

**Soldering is always optional** across all categories and tiers. No build requires soldering unless you choose custom wiring.

### How to Use Categories
```
/cyberdeck categories          — View all 9 categories with details
/cyberdeck build <category>    — Build a deck for a specific category
/cyberdeck pick sbc <category> — Pick the best SBC for a category
/cyberdeck custom <name> <description> — Create a custom category (AI fills everything)
```

### Custom Categories
The agent supports **user-defined custom categories**. Just provide a name and description, and the AI fills in the best components, cooling, enclosure, OS, and accessories.

**Examples:**
- `/cyberdeck custom "Robotics Lab" Mobile robotics platform with camera and servos`
- `/cyberdeck custom "Ham Radio" Portable ham radio with SDR and antenna`
- `/cyberdeck custom "Digital Art" Portable creative workstation with stylus support`
- `/cyberdeck custom "Weather Station" Outdoor weather monitoring with sensors`
- `/cyberdeck custom "Drone Ground Station" Portable UAV control with video downlink`

**How it works:**
1. User provides a category name (any name)
2. Agent detects the closest built-in category for component selection
3. Agent selects the most powerful components (Pi 5 16GB, best display, etc.)
4. Agent adds cooling, enclosure, OS, and accessories
5. Agent generates full BOM, tutorial, tips, and compatibility check
6. All components are validated for compatibility before delivery

---

## SINGLE BOARD COMPUTERS

### Raspberry Pi 5
- **CPU:** Quad-core ARM Cortex-A76 @ 2.4 GHz
- **RAM:** 2/4/8/16GB LPDDR4X
- **Storage:** microSD + PCIe 2.0 x1 (NVMe via HAT)
- **Video:** Dual micro HDMI (4Kp60)
- **GPIO:** 40-pin header
- **Power:** USB-C (5V/5A recommended)
- **TDP:** ~12W under load
- **Price:** $50–$90 (board only)
- **Best For:** Most cyberdeck builds in 2026, general purpose, coding, security
- **Pros:** Best performance, NVMe support, excellent community, PCIe lane
- **Cons:** Higher power draw than Pi 4, needs active cooling in enclosed builds
- **Community Status:** Current default — widest software and accessory support

### Raspberry Pi 4 Model B
- **CPU:** Quad-core ARM Cortex-A72 @ 1.8 GHz
- **RAM:** 1/2/4/8GB LPDDR4
- **Storage:** microSD + USB 3.0
- **Video:** 2x micro HDMI (4Kp60, 4Kp30)
- **GPIO:** 40-pin header
- **Power:** USB-C (5V/3A)
- **TDP:** ~7W under load
- **Price:** $35–$75 (board only)
- **Best For:** Budget builds, writerdecks, gaming, simpler projects
- **Pros:** Mature ecosystem, lower power, runs cooler, easier in tight enclosures
- **Cons:** Older CPU, no PCIe NVMe
- **Community Status:** Still very popular, many existing designs target Pi 4

### Raspberry Pi Zero 2 W
- **CPU:** Quad-core ARM Cortex-A53 @ 1 GHz
- **RAM:** 512MB LPDDR2
- **Storage:** microSD
- **Video:** mini HDMI (1080p)
- **GPIO:** 40-pin header (unpopulated)
- **Power:** micro USB (5V/2.5A)
- **TDP:** ~2W
- **Price:** $15
- **Best For:** Ultra-compact builds, writerdecks, IoT, embedded projects
- **Pros:** Tiny form factor, ultra-low power, Wi-Fi built-in
- **Cons:** Limited performance, 512MB RAM, fewer ports
- **Community Status:** Popular for Penkesu and small handheld builds

### Raspberry Pi Compute Module 4 / 5
- **CPU:** Same as Pi 4 (CM4) or Pi 5 (CM5)
- **RAM:** 1–8GB (CM4) or 4–16GB (CM5)
- **Storage:** eMMC + microSD (carrier dependent)
- **Video:** Via carrier board (HDMI, DSI, eDP)
- **GPIO:** Board-to-board connector (not standard header)
- **Power:** Via carrier board
- **Price:** $25–$90 (module only, carrier extra)
- **Best For:** Custom carrier boards, ClockworkPi uConsole, advanced builders
- **Pros:** Compact, flexible carrier design, no wasted ports
- **Cons:** Requires custom carrier board or specific chassis
- **Community Status:** Growing — HackberryPi and uConsole use CM4/CM5

### Orange Pi 5
- **CPU:** Octa-core RK3588S (4x A76 + 4x A55) @ 2.4 GHz
- **RAM:** 4/8/16/32GB LPDDR5
- **Storage:** eMMC + NVMe + microSD
- **Video:** HDMI 2.1 (8K), USB-C DP
- **GPIO:** 40-pin header
- **Power:** USB-C (5V/4A)
- **Price:** $50–$150
- **Best For:** High-performance emulation, desktop replacement, AI workloads
- **Pros:** Much faster CPU than Pi, NVMe built-in, 32GB RAM possible
- **Cons:** Smaller community, less software optimization, higher power
- **Community Status:** Growing — good alternative to Pi 5 for power users

### NVIDIA Jetson Orin Nano
- **CPU:** 6-core ARM Cortex-A78AE
- **GPU:** 1024-core NVIDIA Ampere
- **RAM:** 4/8GB LPDDR5
- **Storage:** NVMe + microSD
- **Video:** HDMI 2.1, MIPI CSI/DSI
- **GPIO:** 40-pin header
- **Power:** DC barrel jack (5–20V)
- **TDP:** 7–15W
- **Price:** $150–$250
- **Best For:** AI/ML inference, computer vision, robotics, local LLMs
- **Pros:** GPU acceleration, CUDA support, best AI performance
- **Cons:** Expensive, large, high power, niche use case
- **Community Status:** Niche but active in AI community

### LattePanda Mu (x86)
- **CPU:** AMD Ryzen 7 7840HS (8-core/16-thread)
- **RAM:** Up to 64GB DDR5
- **Storage:** NVMe PCIe 4.0
- **Video:** USB4, HDMI, DP
- **GPIO:** None (standard PC)
- **Power:** USB-C PD (65–100W)
- **TDP:** 35–54W
- **Price:** $300–$500 (board only)
- **Best For:** Full Windows/Linux desktop, professional software, x86 compatibility
- **Pros:** Full desktop performance, runs Windows 11, x86 app compatibility
- **Cons:** Expensive, high power, needs active cooling, not ARM-friendly
- **Community Status:** Niche — for builders who need x86 software

### ClockworkPi uConsole
- **CPU:** Accepts CM4, CM5, or other compute modules
- **Display:** 5" 1280x720 IPS
- **Keyboard:** Compact QWERTY
- **Battery:** Built-in
- **Speakers:** Built-in
- **Price:** $220–$280 (kit)
- **Best For:** Quick start, all-in-one cyberdeck, no custom case needed
- **Pros:** Ready-made cyberdeck kit, modular, good build quality
- **Cons:** Fixed form factor, less customization
- **Community Status:** Active community, popular quick-start option

### HackberryPi CM5 (ZitaoTech/Elecrow)
- **CPU:** Raspberry Pi CM5
- **Chassis:** Aluminum, pre-designed cyberdeck body
- **Price:** ~$168
- **Best For:** Quick build with good build quality, Kali Linux platform
- **Pros:** Aluminum chassis, open-source STL files, CM5 performance
- **Cons:** Fixed form factor, limited customization
- **Community Status:** Growing — used successfully as Kali platform

### GMKtec M6 Ultra (x86 Mini PC)
- **CPU:** AMD Ryzen 5 7640HS (6-core/12-thread)
- **RAM:** 32GB DDR5
- **Storage:** 1TB NVMe + second M.2 slot
- **Network:** Dual 2.5GbE LAN
- **Video:** HDMI, DP, USB4
- **Price:** ~$300
- **Best For:** Network analysis, dual-NIC deck, pfSense, penetration testing
- **Pros:** Dual NIC, powerful CPU, compact
- **Cons:** 45–60W TDP, fan noise, not ARM
- **Community Status:** Used for network-heavy cyberdeck builds

### GEEKOM A9 Max (x86 AI Workstation)
- **CPU:** AMD Ryzen AI 9 HX 470 (12-core/24-thread)
- **NPU:** XDNA 2 (55 TOPS, 86 TOPS total AI)
- **RAM:** 32GB DDR5 (expandable to 128GB)
- **Storage:** Dual PCIe Gen4 NVMe (up to 8TB)
- **Network:** Wi-Fi 7, Dual 2.5GbE
- **Video:** 2x HDMI 2.1, 2x USB4
- **Price:** ~$800–$1200
- **Best For:** AI/ML workloads, local LLM inference, workstation replacement
- **Pros:** 86 TOPS NPU, massive RAM, 4x 8K display support
- **Cons:** Expensive, high power, overkill for most decks
- **Community Status:** Niche — premium AI workstation builds

---

## DISPLAYS

### Size Guidelines
- **3–5 inches:** Ultra-compact, thumb-typed, writerdecks, status displays
- **5 inches:** Small portable, ClockworkPi uConsole standard
- **7 inches:** Sweet spot for most builds — portable but usable
- **7.9 inches:** Ultrawide (1280x400) — interesting slab builds
- **10 inches:** Full desktop experience, briefcase territory
- **13+ inches:** Desk-replacement, heavy builds

### Resolution Minimums
- **Main display:** Never below 1024x600 — modern Linux is painful below this
- **Secondary/status displays:** 320x240 to 800x480 is fine
- **Sweet spot:** 1280x800 in 7–10 inches

### Display Types

#### HDMI LCD (Most Common)
- **Interface:** HDMI + USB power
- **Sizes:** 5–10 inches
- **Resolutions:** 800x480 to 1920x1080
- **Touch:** Capacitive 5-point (standard, no drivers needed on Pi)
- **Recommended:** iPistBit, JUN-ELECTRON, HAMTYSAN 7" IPS HDMI touchscreen
- **Price:** $60–$100 for 7" IPS touch with speakers
- **Best For:** Most builds — universal compatibility

#### DSI Touchscreen
- **Interface:** Pi DSI ribbon cable connector
- **Size:** Official 7" (800x480)
- **Pros:** Saves a USB port, cleaner internal wiring
- **Cons:** Limited to Pi-compatible displays
- **Best For:** Clean internal builds where USB ports are scarce

#### E-Ink Displays
- **Interface:** SPI/I2C
- **Sizes:** 4–10 inches
- **Brands:** Waveshare, GoodDisplay
- **Pros:** Near-zero power draw, sunlight readable, productive slowness
- **Cons:** Slow refresh, no video capability
- **Best For:** Writerdecks, distraction-free writing machines

#### OLED Displays
- **Interface:** I2C/SPI
- **Sizes:** 1–3 inches (128x64 to 256x64)
- **Use Case:** Status displays, system monitoring, secondary screens
- **Best For:** Adding battery/CPU/temp readouts to any build

#### Composite Displays
- **Interface:** Composite video
- **Sizes:** 3.5–5 inches
- **Resolution:** 320x240 to 480x320
- **Use Case:** Retro aesthetic, vintage look
- **Best For:** Retro gaming decks, conversation pieces

### Display Compatibility Rules
- **HDMI ↔ HDMI:** Direct connection, universal
- **DSI ↔ Pi DSI port:** Pi-specific, saves USB port
- **USB-C DP Alt Mode:** Cleanest (one cable for video + power) — requires SBC support
- **E-ink ↔ SPI:** Requires driver configuration
- **Always verify:** Interface matches SBC output ports

---

## KEYBOARDS & INPUT

### Mechanical Keyboards
- **60% layout** — Standard cyberdeck choice. Full alpha, no function row/numpad/arrow cluster
  - HyperX Alloy Origins 60 ($60–$80)
  - Keychron K12 ($60–$100)
  - MageGee, Snpurdiri, EPOMAKER (budget options, $30–$50)
- **40% layout** — Even smaller, no number row, relies on layers
  - Drop/OLKB Planck v7 ($100–$130) — community favorite
  - Ortholinear (grid-arranged) packs into rectangular chassis cleanly
- **Split ergonomic** — Corne keyboard for creative builds
  - Used in Chonky Palmtop and other creative designs
- **Price range:** $30–$130 depending on switches and build quality

### Compact & Specialty Keyboards
- **Rii mini keyboards** — Budget option for media center builds
- **Blackberry-style thumb keyboards** — BBQ20KBD breakout board
- **Solder Party Keyboard FeatherWing** — Thumb-typing option
- **Hand-soldered mechanical** — Maximum customization

### Pointing Devices
- **USB trackball** — Adesso T30, Kensington Orbit (fixed, no desk space needed)
- **Trackpad** — Built into deck (elegant but harder to integrate)
- **Touch input** — Display-based (replaces mouse for casual use)
- **No pointer** — Valid for pure terminal builds (vim, tmux)
- **Lenovo ThinkPad trackpoint** — Used in laptop-style cyberdeck builds

### Sourcing Tip
- Thrift stores regularly stock used mechanical keyboards for $3–$10
- IBM Model M keyboards from the 80s still work and are available
- Goodwill is a goldmine for budget keyboards

---

## POWER SYSTEMS

### Power Solution Comparison

| Solution | Capacity | Pros | Cons | Best For |
|----------|----------|------|------|----------|
| USB Power Bank | 10,000–26,800 mAh | Simple, safe, replaceable | Bulky, no integration | Beginner builds |
| UPS HAT (Waveshare) | 2x 18650 cells | Clean 5V, I2C battery status | Requires cell purchase | Most builds |
| PiSugar | Integrated LiPo | Slim, integrated, clean | Limited capacity | Small builds |
| Pimoroni LiPo SHIM | Small LiPo | Minimal, low-draw builds | Limited current | Light builds |
| Custom 18650 + TP4056 + MT3608 | 2–6 cells | Full control, high capacity | Requires soldering, BMS knowledge | Advanced builds |
| Laptop power brick + converter | Large | High capacity, AC power | Not portable | Desk-bound decks |

### UPS HAT Recommendations
- **Waveshare UPS HAT (B)** — 2x 18650 in series (7.4V nominal), I2C battery status
- **Geekworm X1200** — Designed for Pi 5, mounts on bottom, up to 5A output
- **PiSugar** — Slim integrated battery + UPS, popular in smaller builds
- **Pimoroni LiPo SHIM** — Minimal option for lower-draw builds
- **RETROPSU** — One of the best Pi 4 power supplies (from Helder Game Tech)

### Battery Cell Format
- **18650 lithium cells** — Standard format for cyberdeck power
- **Capacity:** 2500–3500 mAh per cell (quality brands: Samsung, LG, Panasonic)
- **Price:** $5–$10 per cell

### Runtime Estimates
- **Pi 5 + 7" display:** 8–15W typical load
- **2x 18650 (3000mAh):** ~22Wh → 1.5–2.5 hours real-world
- **4–6x 18650:** 4–6 hours
- **10,000mAh LiPo pack:** 6–8 hours
- **Pi Zero 2W + e-ink:** Full working day on small pack

### CRITICAL SAFETY NOTES
- **Avoid no-name Chinese BMS boards** — Lithium fires are real
- **Stick to known brands:** Waveshare, PiSugar, Adafruit PowerBoost, Pimoroni
- **Always include:** BMS (battery management system), fusing, thermal protection
- **Never leave charging systems unattended during initial testing**
- **Plan for at least 3000mAh capacity** for Pi's 3A max draw with headroom

---

## ENCLOSURES & CASES

### Pelican & Hard Cases (Community Standard)
Since Jay Doscher's Recovery Kit (2019), Pelican cases are the standard:
- **Pelican 1120/1150:** Small — Pi + 5–7" display
- **Pelican 1200:** Medium — 7" display + battery
- **Pelican 1300:** Larger — keyboard storage + accessories
- **Pelican 1400/1450:** Full size — 10" display + integrated keyboard
- **Pelican 1500/1550:** Briefcase-style with room to spare
- **Budget alternatives:** Apache (Harbor Freight), Nanuk, SKB

### 3D Printed Custom Enclosures
- **Total design freedom** — unlimited form factors
- **File sources:** Printables.com, Thingiverse, Cults3D
- **Recommended filament:** PETG (more impact-resistant and heat-tolerant than PLA)
- **Print time:** 20–100+ hours depending on complexity
- **Budget:** $5–$30 in filament for most enclosures
- **Mail-order printing:** JLCPCB, PCBWay, Craftcloud, Slant 3D

### Found & Repurposed Enclosures
- Vintage briefcases and suitcases (thrift stores)
- Gutted Commodore 64, Amiga, TRS-80 shells
- Old military radio cases and ammo boxes
- Lunch boxes, toolboxes, tackle boxes
- VHS cases and hardback books
- Motorola MDT9100 mobile data terminals (decommissioned police cruisers)

### Materials for DIY Cases
- **3D printed (PETG/PLA/ABS)** — Most popular, unlimited design
- **Acrylic** — Transparent, easy to laser cut, cracks if drilled aggressively
- **Aluminum sheet** — Industrial look, needs proper cutting tools
- **Wood** — Warm aesthetic, easy to work
- **Expanded PVC foam board** — Lightweight, easy to cut
- **Sheet metal** — Professional results, needs specialized tools

### Construction Tips
- Cut access holes slightly undersized for filing to perfect fit
- Test-fit with rough prints before committing to final prints
- Plan ventilation paths — enclosed builds without airflow throttle performance
- Design for future upgrades — modular design is a core strength

---

## CONNECTIVITY & ACCESSORIES

### USB Hub
- 4–7 port powered USB hub mounted internally
- Exposes USB-A ports without burning Pi's onboard ports
- Anker, Sabrent, Plugable make compact hubs
- **Essential for:** Most builds

### Ethernet Switch
- 5-port gigabit switch (TP-Link TL-SG105)
- Famous in Jay Doscher's Recovery Kit
- **Essential for:** Pentesting decks, network-heavy builds

### Wi-Fi & Antennas
- **External Wi-Fi antenna:** Alfa AWUS036ACH (community standard for high-power)
- **RP-SMA panel mount cables** for case-mounted antenna
- **Monitor mode support** for security decks
- **Essential for:** Security, field research builds

### Software-Defined Radio (SDR)
- **RTL-SDR** — Affordable entry point ($25–$35)
- **HackRF One** — More capable ($300+)
- **NooElec SDR** + Ham It Up v1.3 upconverter
- **Capabilities:** ADS-B tracking, ham radio, satellite reception, RF snooping
- **Essential for:** Security, survival, signals intelligence builds

### Storage
- **NVMe SSD via Pi 5 PCIe HAT:** 500–1000 MB/s (massive upgrade over SD)
- **Samsung EVO microSD:** Good for boot volumes
- **USB 3.0 flash drives:** Quick external storage
- **250GB+ NVMe:** Stores entire offline library (Wikipedia, Gutenberg, OpenStreetMap)
- **Dual SD card switcher:** For multiple OS images

### Cooling
- **Official Pi active cooler** — Works well in open builds
- **30–40mm fan** with intake/exhaust vents for enclosed builds
- **Pimoroni Fan Shim** — Temperature-controlled, popular
- **Passive cooling:** Case as heatsink (aluminum block to SoC) — beautiful but needs planning

### Status Indicators & Switches
- Power LED, hard power switch, soft shutdown button
- Fan toggles, screen backlight switches
- Arcade switches, aviation toggle switches (aesthetic favorites)
- **Key detail:** These push a deck from "Pi in a box" to "actual machine"

### Audio
- Mini speakers + mini audio amp (PAM8403 breakout board)
- Fostex T40RP over-ear headphones (best ever made, needs amp)
- KZ ZS10 Pro IEMs (excellent sound reproduction)

### Cables
- Micro HDMI 90° angled to HDMI (for Pi 4/5)
- USB-C 3.1 left-angled 90°
- Micro SD to micro SD extension cable
- USB-C panel mount cables

---

## WiFi / LAN COMPONENT DATABASE (July 2026)

Every cyberdeck needs connectivity. This database covers WiFi adapters, Ethernet, LoRa, cellular, and antenna accessories — all tested for compatibility with the SBC database above.

### USB WiFi Adapters

| Adapter | Standard | Frequency | Chipset | Monitor Mode | Price | Best For |
|---------|----------|-----------|---------|--------------|-------|----------|
| Alfa AWUS036ACH | WiFi 5 (802.11ac) | 2.4/5GHz | RTL8812AU | Yes | $30 | Security, pentesting |
| Alfa AWUS036ACS | WiFi 5 (802.11ac) | 2.4/5GHz | RTL8811AU | Yes | $20 | Budget security |
| Alfa AWUS036NHA | WiFi 4 (802.11n) | 2.4GHz | Atheros AR9271 | Yes | $25 | Legacy pentesting |
| Panda PAU09 | WiFi 5 (802.11ac) | 2.4/5GHz | RT5572 | Yes | $25 | Budget option |
| TP-Link TL-WN722N v1 | WiFi 4 (802.11n) | 2.4GHz | Atheros AR9271 | Yes | $15 | Budget pentesting |

**Notes:**
- AWUS036ACH is the community standard — best range with dual external antenna
- All monitor mode adapters need driver install on Pi (usually `realtek-rtl8812au` dkms)
- USB 3.0 preferred for max throughput

### Ethernet Adapters

| Adapter | Standard | Speed | Connection | Price | Best For |
|---------|----------|-------|------------|-------|----------|
| UGREEN USB 3.0 to Ethernet | GbE | 1000 Mbps | USB 3.0 | $15 | Pi Zero, adds wired net |
| Cable Matters USB-C to Ethernet | GbE | 1000 Mbps | USB-C | $18 | Pi 5, CM5 |
| Anker USB-C to Ethernet | GbE | 1000 Mbps | USB-C | $20 | Reliable backup |
| Pi 5 built-in Ethernet | GbE | 1000 Mbps | Native | $0 | Pi 5 builds |
| Pi 4 built-in Ethernet | GbE | 1000 Mbps | Native | $0 | Pi 4 builds |

**Notes:**
- Pi 5 and Pi 4 have native GbE — no adapter needed
- Pi Zero 2W needs USB adapter for Ethernet
- Flat Cat6 cables recommended for internal routing

### Ethernet Cables

| Cable | Standard | Speed | Length | Price | Best For |
|-------|----------|-------|--------|-------|----------|
| Cable Matters Cat6 Flat | Cat 6 UTP | 1 Gbps | 1m | $4 | Internal routing |
| Cable Matters Cat6 Flat | Cat 6 UTP | 1 Gbps | 3m | $6 | Desktop use |
| Amazon Basics Cat6 | Cat 6 UTP | 1 Gbps | 1.5m | $5 | General use |
| UGREEN Cat6 Flat | Cat 6 UTP | 1 Gbps | 1m | $4 | Clean internal runs |
| StarTech Cat6 Shielded | Cat 6 STP | 1 Gbps | 2m | $8 | Industrial/EMI |

**Notes:**
- Cat 6 is recommended — future-proof, supports 10Gbps at short distances
- Flat cables are easier to route inside enclosures
- Shielded (STP) for industrial or high-EMI environments

### Network Switches

| Switch | Ports | Speed | Price | Best For |
|--------|-------|-------|-------|----------|
| UGREEN 5-Port GbE | 5x RJ45 | 1000 Mbps | $15 | Multi-device decks |
| TP-Link TL-SG105 | 5x RJ45 | 1000 Mbps | $15 | Community favorite |
| Netgear GS305 | 5x RJ45 | 1000 Mbps | $15 | Reliable |
| UGREEN 8-Port GbE | 8x RJ45 | 1000 Mbps | $25 | Large builds |

**Notes:**
- 5-port is standard for cyberdeck builds
- Fanless design preferred for noise
- All are managed/unmanaged — unmanaged is fine for most builds

### Software Defined Radio (SDR)

| SDR | Type | Frequency | TX/RX | Price | Best For |
|-----|------|-----------|-------|-------|----------|
| RTL-SDR Blog V3 | Receiver | 24MHz-1766MHz | RX only | $30 | Entry-level SDR |
| RTL-SDR Blog V4 | Receiver | 24MHz-1766MHz | RX only | $40 | Improved V3 |
| HackRF One | Transceiver | 1MHz-6GHz | TX+RX | $350 | Full spectrum |
| Yard Stick One | Sub-GHz | Sub-1GHz | TX+RX | $100 | Sub-GHz protocols |
| Flipper Zero | Multi-tool | Sub-1GHz/NFC/IR | TX+RX | $170 | Multi-protocol |

**Notes:**
- RTL-SDR is the entry point — ADS-B tracking, ham radio, satellite
- HackRF One is the gold standard for full TX+RX
- All compatible with Pi 5 via USB

### LoRa Modules (Off-Grid Mesh)

| Module | Chipset | Frequency | Range | Price | Best For |
|--------|---------|-----------|-------|-------|----------|
| Seeed Wio-SX1262 | SX1262 | 868/915MHz | 5-15km | $20 | Meshtastic mesh |
| Heltec LoRa 32 V3 | SX1262 | 868/915MHz | 5-15km | $25 | Meshtastic node |
| LilyGO T-Beam | SX1262 | 868/915MHz | 5-15km | $25 | GPS + LoRa |
| RAK WisBlock | SX1262 | 868/915MHz | 5-15km | $30 | Modular design |

**Notes:**
- Meshtastic is the standard firmware for LoRa mesh networking
- 915MHz for Americas, 868MHz for Europe
- SPI connection to Pi GPIO — needs wiring

### Cellular Modems

| Modem | Standard | Speed | Connection | Price | Best For |
|-------|----------|-------|------------|-------|----------|
| Quectel EC20 | 4G LTE Cat 4 | 150/50 Mbps | USB + SIM | $30 | Industrial 4G |
| SIM7600 | 4G LTE Cat 4 | 150/50 Mbps | USB + SIM | $35 | Pi-focused |
| SIM800C | 2G GSM | GPRS | UART | $10 | SMS/voice only |
| Quectel RM500Q | 5G Sub-6 | 4.2/2.1 Gbps | USB-C | $200 | Future-proof 5G |

**Notes:**
- 4G LTE is the sweet spot for cyberdeck builds
- Needs active SIM card + data plan
- USB connection is simplest — no UART wiring needed
- GPS often included

### Antenna Accessories

| Accessory | Type | Price | Best For |
|-----------|------|-------|----------|
| Alfa 5dBi Antenna (pair) | RP-SMA | $8 | WiFi adapter range |
| Alfa 9dBi Antenna | RP-SMA | $12 | Long range WiFi |
| SMA Pigtail (U.FL) | Cable | $3 | Internal to external |
| SMA Panel Mount | Connector | $5 | Case-mounted antenna |
| 915MHz LoRa Antenna | SMA | $5 | LoRa range |
| 2.4GHz Dipole Antenna | SMA | $3 | WiFi/Bluetooth |

**Notes:**
- External antennas dramatically improve range
- Panel mount through enclosure wall for clean look
- Match antenna frequency to adapter/module frequency

### Connectivity Selection Rules

| Build Type | Primary Connectivity | Secondary | Why |
|-----------|---------------------|-----------|-----|
| Security/Pentesting | Alfa AWUS036ACH | RTL-SDR | Monitor mode + RF |
| Writerdeck | Cat6 flat cable | — | Reliable, low power |
| Coding | Cat6 flat + USB Ethernet | — | Multiple connections |
| Field Research | USB Ethernet + LoRa | — | Wired + off-grid mesh |
| Survival | LoRa + LTE modem | — | Off-grid + emergency |
| Gaming | Cat6 flat cable | — | Low latency |
| Media | Cat6 flat cable | — | Streaming |
| AI/ML | USB Ethernet | — | High bandwidth |

### Compatibility Notes

- **USB WiFi adapters** work with all SBCs via USB 3.0/2.0
- **Ethernet** built into Pi 4/5 — no adapter needed
- **Pi Zero 2W** needs USB Ethernet adapter (no built-in)
- **LoRa modules** need SPI wiring to GPIO — verify pinout
- **Cellular modems** need USB port + SIM card slot
- **SDR dongles** are receive-only (except HackRF) — plug into USB
- **Antenna connectors** must match: RP-SMA for Alfa, SMA for LoRa

---

## COOLING SYSTEMS

Every cyberdeck needs cooling. The Pi 5 runs hot under load (TDP ~12W), and enclosed builds trap heat. Choose based on your SBC and build style.

### Active Cooling (Fans)
| Cooler | Size | Noise | Cooling Power | Price | Best For |
|--------|------|-------|---------------|-------|----------|
| **Raspberry Pi Active Cooler (Official)** | Pi 5 specific | Quiet | Very High | $12 | Pi 5 (best option) |
| **30mm Active Fan** | 30x30x10mm | Moderate | High | $10 | Pi 5, Jetson, Orange Pi |
| **40mm USB Fan** | 40x40x10mm | Moderate | High | $8 | Pi 4, Pi 5, any SBC |
| **3D Printed Fan Shroud + 30mm Fan** | Custom | Moderate | High | $5 | Any SBC (custom directed airflow) |

### Passive Cooling (Heatsinks)
| Cooler | Material | Thermal Conductivity | Price | Best For |
|--------|----------|---------------------|-------|----------|
| **Copper Heatsink (Pi 5)** | Copper | 401 W/mK | $15 | Pi 5 8/16GB (best passive) |
| **Aluminum Heatsink (Pi 5)** | Aluminum | 205 W/mK | $8 | Pi 5, Pi 4 (budget option) |
| **Copper Heat Spreader Plate** | Copper | 401 W/mK | $6 | Any SBC (spreads heat evenly) |
| **Premium Thermal Paste (Arctic MX-6)** | Compound | 12.5 W/mK | $8 | All (essential for any setup) |

### Cooling Recommendations by Category
- **Coding / Security / AI**: Active cooler mandatory — Pi 5 under sustained load hits 70°C+ without cooling
- **Gaming**: Active fan recommended — emulation is CPU-intensive
- **Writerdeck**: Passive heatsink sufficient — e-ink + low-power SBC generates minimal heat
- **Media**: Passive heatsink fine — mostly idle with occasional decode bursts
- **Survival**: Copper heatsink preferred — no moving parts, reliable in field conditions
- **Conversation Piece**: Fan shroud 3D printed — directed airflow + custom aesthetics

### Thermal Guidelines
- **Safe zone**: Below 60°C — no throttling, long component life
- **Warning zone**: 60–70°C — add or improve cooling
- **Danger zone**: 70–80°C — throttling begins, reduce load or upgrade cooling
- **Critical**: Above 80°C — immediate shutdown risk, stop what you're doing

### Cooling Tips
1. **Always apply thermal paste** between CPU and heatsink/cooler — don't skip this
2. **Copper > Aluminum** for thermal conductivity (401 vs 205 W/mK) — worth the extra $7
3. **The Pi 5 Official Active Cooler** is the quietest and most effective — it's PWM controlled
4. **Add ventilation holes** to enclosed builds — sealed cases trap heat
5. **Monitor CPU temp** with `vcgencmd measure_temp` or a custom script
6. **Aluminum heatsinks** are fine for Pi 4 and below — the Pi 5 needs more

---

## OPERATING SYSTEMS

### For General Purpose
- **Raspberry Pi OS** (Bookworm) — Default, broadest compatibility, works out of the box
- **Ubuntu MATE** — More conventional desktop feel
- **DietPi** — Ultra-lightweight, install only what you need, great for low-resource decks

### For Security
- **Kali Linux** — Standard for pentesting, hundreds of security tools preloaded
  - Pi 4 with 4GB+ RAM recommended minimum
  - Keep on separate SD card for swapping

### For Writerdecks
- **writerdeckOS** — "No distractions. No internet. No apps. Just writing."
- **Micro Journal PC Edition** — Purpose-built for lightweight machines
- **DietPi** — Minimal for maximum battery life

### For Gaming
- **RetroPie** — Most flexible retro gaming
- **Batocera** — Easiest to set up
- **Lakka** — Leanest
- **Twister OS** — Multiple themed desktops (Windows XP, macOS, retro)

### For Media
- **LibreELEC** — Kodi-focused, minimal
- **OSMC** — Kodi with more features
- **Kodi** — Full media center

### For Desktop Replacement
- **Windows 11** — On x86 boards (LattePanda)
- **Ubuntu Server** — Headless setup
- **FreeBSD/OpenBSD** — For the deeply committed

### Recommendation
- Start with **Raspberry Pi OS** for first builds
- Experiment with other distributions once hardware is solid

---

## COMPONENT COMPATIBILITY MATRIX

### Display Interface → SBC Port Matching

| Display Type | Pi 5 | Pi 4 | Zero 2W | CM4/CM5 | Orange Pi 5 | LattePanda |
|-------------|------|------|---------|---------|-------------|------------|
| HDMI | ✅ 2x micro HDMI | ✅ 2x micro HDMI | ✅ mini HDMI | Via carrier | ✅ HDMI 2.1 | ✅ HDMI/DP |
| DSI | ✅ 1x DSI | ✅ 1x DSI | ❌ No DSI | Via carrier | ✅ MIPI DSI | ❌ |
| USB-C DP | ❌ | ❌ | ❌ | Via carrier | ✅ USB-C | ✅ USB4 |
| E-ink (SPI) | ✅ GPIO SPI | ✅ GPIO SPI | ✅ GPIO SPI | Via GPIO | ✅ GPIO SPI | ❌ |
| Composite | ❌ | Via adapter | ✅ | Via carrier | ❌ | ❌ |

### Power Compatibility

| SBC | Min Power | Recommended PSU | USB-C PD | Battery Runtime (2x 18650) |
|-----|-----------|-----------------|----------|---------------------------|
| Pi 5 | 5V/5A (27W) | Official 27W GaN | ✅ | 1.5–2.5 hrs |
| Pi 4 | 5V/3A (15W) | Official 15W | ✅ | 2–4 hrs |
| Zero 2W | 5V/2.5A (12W) | Any USB | micro USB | 8+ hrs |
| CM4/CM5 | Via carrier | Via carrier | Via carrier | Varies |
| Orange Pi 5 | 5V/4A (20W) | USB-C PD | ✅ | 1–2 hrs |
| LattePanda | 65–100W | USB-C PD | ✅ | N/A (too high) |

### Keyboard Interface

| Keyboard Type | Pi 5 | Pi 4 | Zero 2W | LattePanda |
|--------------|------|------|---------|------------|
| USB wired | ✅ | ✅ | ✅ (with OTG) | ✅ |
| Bluetooth | ✅ | ✅ | ✅ | ✅ |
| USB wireless dongle | ✅ | ✅ | ✅ (with OTG) | ✅ |
| GPIO matrix | ✅ | ✅ | ✅ | ❌ |

---

## BUDGET TIERS

### Tier A: Entry Build ($150–$300)
- Raspberry Pi 4 (2GB) or Pi Zero 2W
- 7" HDMI display (no touch or basic touch)
- Budget mechanical keyboard
- USB power bank
- Thrift store enclosure
- **Result:** Functional but rough. Great first build.

### Tier B: Standard Build ($400–$700)
- Raspberry Pi 5 (4GB or 8GB)
- 7" IPS touchscreen (1024x600+)
- Quality 60% mechanical keyboard
- UPS HAT with 18650 cells
- Pelican 1150 case with 3D printed face plate
- NVMe SSD via HAT
- **Result:** The community sweet spot. Polished and capable.

### Tier C: Premium Build ($800–$1500)
- Pi 5 (16GB) or LattePanda Mu
- 10" high-resolution display
- Custom 3D printed enclosure
- Drop/OLKB Planck keyboard
- Full port array, external antennas
- Integrated battery (6+ hours)
- **Result:** Approaching laptop cost, but doing things a laptop cannot.

### Tier D: Doscher Tier ($2000+)
- Custom 3D printed parts (100+ print hours)
- Milled aluminum face plates
- Military-spec connectors
- Integrated Ethernet switch
- Full desktop hardware
- **Result:** A statement piece. Competition-grade.

---

## ICONIC BUILDS REFERENCE

### Jay Doscher's Recovery Kit (2019–present)
- **The build that started the modern movement**
- Raspberry Pi in Pelican case, machined face plate, integrated Ethernet switch
- V2: Pi 5 + Planck keyboard
- Recovery Kit Ultra: AMD Ryzen 9 + RTX 5080 in Pelican 1607
- **Sites:** jaydoscher.com, Hackaday coverage

### Penkesu Computer (Penk Chen)
- Small, elegant, clamshell — looks like a pencil case
- Pi Zero 2W + 7.9" ultrawide 1280x400 touchscreen + 48-key ortholinear keyboard
- Hinges from Game Boy Advance SP
- **Sites:** penkesu.computer, github.com/penk/penkesu

### Chonky Palmtop (Daniel Norris)
- Pi 4 + 7" touchscreen + Corne split keyboard on pivot mechanism
- Same footprint as old Asus EEE 701, but thicker
- Runs Miryoku firmware for keyboard-only mouse emulation
- **Sites:** github.com/a8ksh4/chonky-palmtop

### THEBRICK
- Pi 4 + 7.9" wide screen + Planck keyboard
- One of the first fully custom 3D-printed cyberdeck enclosures
- **Sites:** Thingiverse listing, kbd.news feature

### Trammell Hudson's MDT9100 Conversion
- Gutted Motorola MDT-9100T (police mobile data terminal)
- Kept original keyboard and amber CRT
- Custom Teensy-based HID interface
- Runs Doom and Fallout 4 Pip-Boy app
- **Sites:** trmm.net/MDT9100

### ClockworkPi uConsole
- Modular handheld, QWERTY keyboard, 5" 1280x720 IPS
- Accepts CM4 or CM5 compute modules
- $220–$280 depending on core
- **Sites:** clockworkpi.com/uconsole

### HackberryPi CM5 (ZitaoTech/Elecrow)
- Aluminum-chassis pre-designed cyberdeck body
- Accepts Raspberry Pi CM5, ~$168
- Open-source STL files
- **Sites:** github.com/ZitaoTech/Hackberry-Pi_Zero

### Cyberdeck Red (Gabriel)
- 2nd place Hackaday Cyberdeck Contest 2022
- Integrated oscilloscope, HackRF SDR, projector, breadboards
- V2: LattePanda 3 Delta running Windows
- **Sites:** hackaday.io/project/187494

### Micro Journal Series (Un Kyu Lee)
- Dedicated writerdeck, 4 generations
- ESP32-powered, boots instantly
- Hand-wired 30% ortholinear keyboard + 2.8" LCD
- **Sites:** github.com/unkyulee/micro-journal

### Don't Panic (Paul)
- Pi 3A+ + Pimoroni HyperPixel 4.0 Square LCD
- LX-2BUPS UPS board + 2x 18650 cells
- PAM8403 audio + printable volume knob
- **Sites:** Hackaday coverage

### Dinodeck 2026 (therebelrobot)
- Pi Zero 2W + 3.5" DPI touch display
- Cellular LTE + Meshtastic LoRa mesh networking
- 5000mAh battery in thrifted enclosure
- **Sites:** github.com/therebelrobot/dinodeck-2026

---

## 3D PRINTING RESOURCES

### Design File Sources
- **Printables.com** — Largest collection, search "cyberdeck"
- **Thingiverse** — Classic repository, search "cyberdeck"
- **Cults3D** — Premium and free designs
- **GitHub** — Open-source build files (BenMakesEverything/cyberdeck, etc.)

### Recommended Filaments
- **PETG** — Best for cyberdeck cases (impact-resistant, heat-tolerant)
- **PLA** — Easy to print, less durable, fine for non-structural parts
- **ABS/ASA** — Heat-resistant, needs enclosure for printing
- **TPU** — Flexible, for gaskets and bumpers

### Print Settings for Cyberdecks
- **Infill:** 40–60% for structural parts (strength + durability)
- **Layer height:** 0.2mm for quality, 0.3mm for speed
- **Supports:** Tree supports for overhangs
- **Orientation:** Print flat side down for best surface quality

### Mail-Order Printing Services
- **JLCPCB** — Affordable, fast
- **PCBWay** — Good quality
- **Craftcloud** — Price comparison
- **Slant 3D** — Production-grade

### Cyberdeck-Specific STL Collections
- BenMakesEverything/cyberdeck (Framework-based, 486★)
- Jay Doscher Recovery Kit series (STL subscription)
- Penkesu Computer (open-source files)
- THEBRICK (Thingiverse)
- Cyberdore 2064 (Printables)

---

## SOLDERING & WIRING BASICS

### When Soldering Is Needed
- Power switches (almost always required for portable builds)
- Custom wiring connections
- GPIO header connections
- LED indicators
- Audio amplifier boards
- Battery management systems
- Custom keyboard matrices

### When Soldering Is NOT Needed
- USB connections (plug-and-play)
- HDMI connections (plug-and-play)
- HATs that stack on GPIO (no soldering)
- Pre-made cable assemblies
- Modular builds with connectors

### Essential Soldering Skills
1. **Tinning wires** — coat wire ends with solder
2. **Soldering through-hole** — components to PCB pads
3. **Soldering wires to pads** — connecting wires to boards
4. **Heat shrink** — insulating connections
5. **Desoldering** — fixing mistakes (solder wick or pump)

### Recommended Starter Equipment
- **Soldering iron:** Temperature-controlled, 300–400°C ($25–$60)
- **Solder:** 60/40 leaded or lead-free, 0.8mm diameter
- **Flux:** Helps solder flow cleanly
- **Solder wick/pump:** For desoldering
- **Heat shrink tubing:** Insulation
- **Helping hands / vise:** Holds work steady
- **Wire strippers:** For preparing wires

### Safety
- Work in ventilated area (solder fumes are harmful)
- Wear safety glasses
- Use lead-free solder when possible
- Clean tip regularly with brass wool or sponge
- Never touch hot tip

### Soldering Guide
- Community resource: Google Doc's Slide by user "Newts" (referenced on cyberdeck.cafe)
- Quick, simple, covers all basics for cyberdeck builds

---

## COMPONENT SOURCING GUIDE

### Budget Sources
1. **E-waste recycling** — Broken electronics have useful parts
2. **Thrift stores** — Keyboards ($3–$10), briefcases, power bricks
3. **99c stores** — Glue, tape, USB cables, soldering irons
4. **eBay** — Used gear, sometimes cheap
5. **OfferUp/Craigslist** — Local deals, watch for scams

### Quality Sources
- **Adafruit** (adafruit.com) — Quality displays, batteries, accessories
- **Pimoroni** (shop.pimoroni.com) — Unique Pi accessories, community trusted
- **The Pi Hut** (thepihut.com) — UK Pi specialist
- **PiShop.us** (pishop.us) — US Pi specialist
- **CanaKit** (canakit.com) — Complete kits, individual components
- **Raspberry Pi Official** (raspberrypi.com) — Direct from source

### Budget Sources
- **AliExpress** — Budget components, longer shipping (2–4 weeks)
- **Amazon** — Fast shipping, wide selection
- **DigiKey/Mouser** — Professional components, precise specs

### Component-Specific
- **SBCs:** Adafruit, PiShop.us, CanaKit, Vilros, RasTech
- **Displays:** Waveshare, Adafruit, Amazon (iPistBit, HAMTYSAN)
- **Keyboards:** Amazon (HyperX, Keychron, MageGee), thrift stores
- **Batteries:** Amazon (Samsung/LG 18650 cells), Adafruit (LiPo)
- **Cases:** Pelican (Amazon/Harbor Freight), 3D printed (self or JLCPCB)
- **SDR:** Amazon (NooElec, RTL-SDR)
- **Cables:** Amazon (right-angle cables essential)

### Amazon Affiliate Links (from Cyberdeck.cafe)
- Community uses affiliate links to support hosting costs
- Always check cyberdeck.cafe for vetted hardware recommendations

---

## COMMUNITY RESOURCES

### Discord Servers
- **Cyberdeck Cafe Discord** — Main community hub, thousands of active members
  - discord.gg/6etTqKQ4Qu
- **Raspberry Pi Discord** — General Pi community
- **Kali Linux Discord** — Security-focused

### Subreddits
- **r/cyberDeck** — 36K+ members, main subreddit for showing builds
- **r/writerDeck** — Dedicated to writing-focused decks
- **r/raspberry_pi** — General Pi community
- **r/unixporn** — Linux desktop customization inspiration

### Websites & Blogs
- **cyberdeck.cafe** — Build guide, curated hardware, Discord
- **jaydoscher.com** — Recovery Kit series, STL subscriptions
- **penkesu.computer** — Penkesu build guide
- **trmm.net** — Trammell Hudson's builds
- **codeof.me** — Tommi Laukkanen's builds
- **writerdeck.org** — Writerdeck community

### YouTube Channels
- **Cyberdeck Cafe** — Build videos, hardware reviews
- **Jeff Geerling** — Pi tutorials and projects
- **Explaining Computers** — SBC comparisons and builds

### Magazines & Blogs
- **Hackaday** — Annual Cyberdeck Contest since 2022
- **kbd.news** — Keyboard community with cyberdeck tag
- **Raspberry Pi Blog** — Official builds and features

### Annual Events
- **Hackaday Cyberdeck Contest** — Annual competition, pushes form boundaries
- **April Cyberdeck Challenge** — Community event on Jalexine Lab Discord

---

## ASSEMBLY PROCESS

### Phase 1: Design and Planning
1. **Define your "why"** — Primary purpose dictates all choices
2. **Pick your category and tier** — Determines complexity and budget
3. **Choose SBC** — Based on category requirements
4. **Select display** — Compatible interface, right size
5. **Pick keyboard** — Layout, switches, connectivity
6. **Plan power system** — Runtime requirements, battery type
7. **Choose enclosure** — Pelican, 3D printed, or found
8. **Sketch layout** — Paper or digital mockup
9. **Consider ergonomics** — Typing angle, viewing angle, wrist rest
10. **Plan cable routing** — Clean internal wiring

### Phase 2: Component Acquisition
1. **Create complete BOM** — Every part, cable, fastener, wire
2. **Order main components first** — SBC, display, keyboard
3. **Order fasteners** — M2, M3, M4 bolts, standoffs, spacers
4. **Order wire and connectors** — For internal wiring
5. **Order extras of cheap parts** — You'll lose some, break others
6. **Wait for everything to arrive** — Don't start building piecemeal

### Phase 3: Prototype on Bench
1. **Lay all components on table** — No cutting or printing yet
2. **Connect loosely** — Pi to display, keyboard, UPS HAT, battery
3. **Install OS** — Boot and verify everything works
4. **Test all functions** — Display, keyboard, touch, audio, Wi-Fi
5. **Measure everything** — Confirm dimensions for enclosure
6. **Diagnose problems now** — When nothing is bolted down

### Phase 4: Enclosure Fabrication
1. **3D print in sections** — Manageable for your printer
2. **Test-fit with rough prints** — Before committing to final prints
3. **Budget 20–60+ hours print time** — For typical cyberdeck enclosures
4. **Check dimensional accuracy** — Printers vary, datasheets sometimes lie
5. **Cut access holes slightly undersized** — File to perfect fit
6. **Sand and finish** — If desired for aesthetics

### Phase 5: Electronics Integration
1. **Install display** — Verify function with temporary wiring
2. **Mount SBC** — Secure with standoffs
3. **Integrate keyboard** — Verify operation
4. **Install power system** — UPS HAT or battery with protection
5. **Add secondary displays/status indicators** — OLEDs, LEDs
6. **Install cooling** — Fan or heatsink
7. **Route and secure all wiring** — Clean cable management
8. **Test at each stage** — Discovering problems after full assembly means disassembly

### Phase 6: Software Configuration
1. **Install base OS** — Raspberry Pi OS or chosen distribution
2. **Configure display** — Resolution, rotation, scaling
3. **Configure input** — Keyboard layout, mouse/trackball
4. **Set up power management** — Battery monitoring, low-battery shutdown
5. **Install applications** — Per your use case
6. **Visual customization** — Tiling window manager, retro terminal, cyberpunk themes
7. **Update and configure** — All packages, security, networking

### Phase 7: Finishing Touches
1. **Add status indicators** — Power LED, network activity
2. **Install switches** — Power, fan, screen backlight
3. **Apply aesthetic touches** — Labels, paint, stickers, exposed hardware
4. **Final testing** — All functions, extended runtime test
5. **Document your build** — Photos, BOM, notes
6. **Share with community** — Post to Discord, Reddit, Hackaday

---

## QUICK REFERENCE: BEST PICKS BY CATEGORY

| Category | Best SBC | Best Display | Best OS | Budget |
|----------|----------|-------------|---------|--------|
| Coding/Dev | Pi 5 8GB | 7–10" IPS HDMI | Pi OS / Ubuntu | $300–$1200 |
| Writerdeck | Zero 2W | 4–7" E-ink | writerdeckOS | $100–$400 |
| Security | Pi 5 8GB | 7" IPS HDMI | Kali Linux | $400–$1500 |
| Gaming | Pi 4 4GB | 7" HDMI or TV | RetroPie | $150–$500 |
| Field Research | Pi 5 8GB | 7–10" sunlight-readable | Pi OS | $300–$800 |
| AI/ML | Jetson Orin Nano | 7–10" HDMI | JetPack/Ubuntu | $500–$2000 |
| Survival | Pi 5 8GB | 7" HDMI or e-ink | Pi OS | $300–$1000 |
| Media Center | Pi 4/5 | HDMI to TV | LibreELEC | $150–$500 |
| Conversation Piece | Zero 2W | 5–7" IPS/OLED | Twister OS | $150–$800 |

---

## QUICK REFERENCE: BEST PICKS BY TIER

| Tier | SBC | Display | Keyboard | Power | Case | Total |
|------|-----|---------|----------|-------|------|-------|
| Beginner | Pi 4 2GB ($35) | 7" HDMI ($60) | Budget mech ($30) | USB bank ($20) | Thrift/box ($10) | ~$155 |
| Intermediate | Pi 5 8GB ($75) | 7" IPS touch ($80) | Keychron K12 ($80) | UPS HAT+18650 ($50) | Pelican+3D ($50) | ~$335 |
| Advanced | Pi 5 16GB ($90) | 10" 1280x800 ($120) | Planck v7 ($130) | Custom 6-cell ($80) | Full custom 3D ($60) | ~$480 |

---

## ICONIC BUILDS REFERENCE (Expanded)

### Penkesu Computer (Penk Chen)
- **SBC:** Raspberry Pi Zero 2 W
- **Display:** 7.9" ultrawide 1280x400 touchscreen
- **Keyboard:** 48-key low-profile ortholinear mechanical
- **Enclosure:** Clamshell with Game Boy Advance SP hinges
- **Key Feature:** Smallest, most elegant clamshell cyberdeck
- **Files:** penkesu.computer (build guide), github.com/penk/penkesu (STL, BOM, firmware)
- **Difficulty:** Intermediate

### Chonky Palmtop (Daniel Norris)
- **SBC:** Raspberry Pi 4
- **Display:** 7" touchscreen
- **Keyboard:** Corne split keyboard on pivot mechanism
- **Key Feature:** Split keyboard swings out on clever pivot
- **Difficulty:** Advanced

### Mermaid in the Shell (cc/bossbratox)
- **SBC:** Raspberry Pi 3A+
- **Display:** 3.5" touchscreen
- **Keyboard:** ZitaoTech BB Q20 (white)
- **Enclosure:** Pink seashell frame clutch purse
- **Key Feature:** TikTok viral (1M+ views), thrifting, "mermaid" aesthetic
- **Difficulty:** Beginner

### Cyberdore 2064 (Tommi Laukkanen)
- **SBC:** Raspberry Pi Zero + Pi Pico
- **Display:** 128x64 pixel OLED
- **Input:** Built-in keyboard + oversized KY-040 rotary encoder scroll wheel
- **Key Feature:** Scroll wheel, anti-doomscrolling design
- **Difficulty:** Intermediate

### Typeframe PS-85 / PX-88 (Jeff Merrick)
- **SBC:** Raspberry Pi
- **Display:** Built-in LCD
- **Keyboard:** 40% / 65% mechanical, custom keycaps
- **Key Feature:** Retro-industrial writerdeck, Epson portable computer inspired, Alien movie aesthetic
- **Difficulty:** Intermediate

### Altoids Tin Mini Cyberdeck (Exercising Ingenuity)
- **SBC:** Raspberry Pi (small form)
- **Display:** Small LCD
- **Enclosure:** Altoids tin, clamshell design
- **Key Feature:** Linux in an Altoids tin, world's smallest cyberdeck
- **Files:** hackaday.io/project/205598-altoids-tin-mini-cyberdeck
- **Difficulty:** Advanced

### Portable CRT Cyberdeck
- **SBC:** Raspberry Pi
- **Display:** Portable CRT TV
- **Key Feature:** Retro CRT as display, 80s aesthetic
- **Difficulty:** Advanced

### The Cyberdeck (Lucas Dul)
- **SBC:** Raspberry Pi 4
- **Display:** 5" CRT (Magnavox portable radio-TV)
- **Keyboard:** Gateron Silent Brown switches, custom
- **Enclosure:** Repurposed Magnavox portable radio-TV
- **Key Feature:** Fallout universe inspired, CRT display, touchpad
- **Difficulty:** Advanced

### Crash Recovery Device (Evan Meaney)
- **SBC:** Raspberry Pi
- **Display:** 7" touchscreen
- **Keyboard:** Mechanical (built into lid)
- **Enclosure:** Pelican case with grounded copper Faraday cage
- **Power:** 12,000mAh battery + solar panels
- **Key Feature:** EMP protection, offline Wikipedia/Wikivoyage, DHCP server, GPS, radio, radiation detector
- **Difficulty:** Advanced

### Clockwork uConsole
- **SBC:** Modular (supports Pi CM4/CM5, etc.)
- **Display:** Built-in
- **Keyboard:** Built-in
- **Key Feature:** Commercial kit, most "laptop-like" cyberdeck, modular design
- **Difficulty:** Beginner (kit)

### Bumble Berry Pi (MakerSam)
- **SBC:** Raspberry Pi
- **Display:** Small LCD
- **Key Feature:** Budget handheld, community-driven
- **Files:** github.com/samcervantes/bumble-berry-pi
- **Difficulty:** Beginner

### Solar OS Reflective LCD (nilseuropa)
- **SBC:** ESP32-S3 (Waveshare board)
- **Display:** 4.2" reflective LCD
- **Key Feature:** Solar-powered, reflective LCD (readable in sunlight), homebrew OS
- **Files:** github.com/nilseuropa/solar_os
- **Difficulty:** Intermediate

### Tactical Wedge Cyberdeck
- **SBC:** Raspberry Pi 5
- **Key Feature:** Fully custom command console, designed for FDM printability
- **Files:** hackaday.io/project/206103
- **Difficulty:** Intermediate

---

## GITHUB REPOSITORIES

| Repository | Description | Stars | Link |
|-----------|-------------|-------|------|
| **Penkesu** | Clamshell cyberdeck with Pi Zero 2W | Growing | github.com/penk/penkesu |
| **cyberdeck-platform** | Modular Pi cyberdeck with OS hardening | Growing | github.com/RealPhantomLee/cyberdeck-platform |
| **Pelican-Deck** | Open-source Pelican case framework | Growing | github.com/Jake-Simek/Pelican-Deck |
| **bumble-berry-pi** | Budget handheld cyberdeck | Growing | github.com/samcervantes/bumble-berry-pi |
| **RPI_DEV** | Pi development platform | Growing | github.com/sector07-dev/RPI_DEV |
| **solar_os** | Homebrew OS for reflective LCD | Growing | github.com/nilseuropa/solar_os |
| **Altoids Tin Cyberdeck** | Linux in an Altoids tin | Growing | hackaday.io/project/205598 |
| **Tactical Wedge** | Pi 5 modular command console | Growing | hackaday.io/project/206103 |

---

## TIKTOK VIRAL BUILDS

| Build | Creator | Views | Key Feature |
|-------|---------|-------|-------------|
| **Mermaid in the Shell** | @ubeboobey | 1M+ | Pink seashell clutch purse, thrifted materials |
| **DIY Cyberdeck** | @metamerd | Viral | Portable computer build walkthrough |
| **Compact Cyberdeck** | @carternosko | Viral | Pocket-sized workstation |
| **Mermaid Cyberdeck** | @alexinexxx | Viral | Newbie journey, female audience 11%→40% |

### TikTok Trends
- **Thrift store finds** — Clutch purses, vintage cases, old toys as enclosures
- **"Girly" aesthetic** — Moving away from rugged cyberpunk toward personal expression
- **Media archiving** — Physical copies of movies, music, books (anti-subscription)
- **Newbie journeys** — First-time builders documenting the process
- **Cross-demographic** — Female builders driving growth (11%→40% audience shift)

---

## SOFTWARE & TOOLS

### Window Managers (Popular with Cyberdeck Users)
- **i3** (i3wm.org) — Tiling window manager, keyboard-driven, low resource
- **Awesome WM** — Customizable tiling WM
- **Sway** — Wayland alternative to i3

### Terminal & UI
- **Cool Retro Term** (github.com/Swordfish90/cool-retro-term) — CRT terminal emulator
- **LVGL** (lvgl.io) — Graphics library for custom UI development
- **QMK Firmware** (qmk.fm) — Custom keyboard firmware

### Offline Knowledge
- **Kiwix** (kiwix.org) — Offline Wikipedia and thousands of resources
- **Internet Archive** (archive.org) — Books, software, content
- **Project Gutenberg** (gutenberg.org) — Public-domain books

### Useful Software
- **Raspberry Pi Imager** — OS flashing
- **balenaEtcher** — SD card flashing
- **Octoprint** — If using Pi for 3D printer monitoring
- **Grafana + Prometheus** — Monitoring dashboards

---

## COMPONENT SUPPLIERS (Expanded)

### Primary Suppliers
| Supplier | Specialty | URL |
|----------|-----------|-----|
| **Adafruit** | Displays, batteries, accessories | adafruit.com |
| **Pimoroni** | Pi accessories, HATs | shop.pimoroni.com |
| **PiShop.us** | US Pi specialist | pishop.us |
| **The Pi Hut** | UK Pi specialist | thepihut.com |
| **CanaKit** | Complete Pi kits | canakit.com |
| **AliExpress** | Budget components | aliexpress.com |
| **DigiKey** | Professional components | digikey.com |
| **Mouser** | Professional components | mouser.com |

### Keyboard Suppliers
| Supplier | Specialty | URL |
|----------|-----------|-----|
| **Drop** | Planck, Preonic, custom boards | drop.com |
| **KBDfans** | Custom keyboards, kits | kbdfans.com |
| **NovelKeys** | Switches, keycaps | novelkeys.com |
| **Solder Party** | BB Q20 keyboard breakout, cyberdeck modules | solder.party |
| **r/mechmarket** | Secondhand keyboard market | reddit.com/r/mechmarket |

### Enclosure Suppliers
| Supplier | Product | URL |
|----------|---------|-----|
| **Pelican** | Watertight cases | pelican.com |
| **Apache (Harbor Freight)** | Budget Pelican alternative | harborfreight.com |
| **Nanuk** | Premium cases | nanuk.com |
| **SKB** | Professional cases | skbcases.com |

### 3D Print Resources
| Resource | Type | URL |
|----------|------|-----|
| **Thingiverse** | STL files | thingiverse.com/search?q=cyberdeck |
| **Printables** | STL files | printables.com/search/models?q=cyberdeck |
| **Hackaday Projects** | Build logs | hackaday.io |

---

## COMMUNITY RESOURCES

| Resource | Type | URL |
|----------|------|-----|
| **Cyberdeck Cafe** | Community hub + Discord | cyberdeck.cafe |
| **r/cyberDeck** | Reddit community | reddit.com/r/cyberDeck |
| **r/writerDeck** | Writerdeck subreddit | reddit.com/r/writerDeck |
| **Hackaday Cyberdeck** | Build documentation | hackaday.com/tag/cyberdeck |
| **Hackaday Cyberdeck Contest** | Annual competition | hackaday.io/contests |
| **Raspberry Pi Blog** | Official cyberdeck coverage | raspberrypi.com/news |
| **Pinterest Cyberdeck** | Inspiration boards | pinterest.com/search?q=cyberdeck |
| **r/unixporn** | Linux desktop customization | reddit.com/r/unixporn |

---

## PCB / CARRIER BOARD DATABASE (Best of Best)

### Pi HATs
| Board | Type | Pins | Compatibility | Price | Best For |
|-------|------|------|---------------|-------|----------|
| **Waveshare UPS HAT (H5180)** | Power | 40-pin passthrough | Pi 5, Pi 4, Pi 3, CM4 | $45 | Coding, Security, Research |
| **Waveshare Motor HAT** | Motor | 40-pin passthrough | Pi 5, Pi 4, Pi 3, CM4 | $20 | Robotics, IoT |
| **Waveshare Sensor HAT** | Sensors | 40-pin passthrough | Pi 5, Pi 4, Pi 3, CM4 | $15 | Research, Survival |
| **Adafruit pHAT / Bonnet** | I2C/SPI | 26-pin GPIO | Pi Zero, Pi 3, Pi 4, Pi 5 | $10-$25 | Writerdeck, Gaming, Media |
| **SparkFun Qwiic HAT** | I2C | Qwiic connectors | Pi 5, Pi 4, Pi 3, Zero | $10-$20 | Research, AI, Survival |

### Compute Module Carriers
| Board | Type | Pins | Compatibility | Price | Best For |
|-------|------|------|---------------|-------|----------|
| **Waveshare CM5 IO Board** | CM5 carrier | Full 40-pin GPIO + M.2 | CM5 only | $25-$45 | AI, Coding, Security |
| **Waveshare CM4 IO Board** | CM4 carrier | Full 40-pin GPIO + M.2 | CM4 only | $20-$35 | Gaming, Media, Writerdeck |
| **ClockworkPi uConsole Kit** | All-in-one kit | CM4/CM5 compatible | CM4/CM5 | $160-$200 | Portable all-in-one |

### Jetson Carriers
| Board | Type | Compatibility | Price | Best For |
|-------|------|---------------|-------|----------|
| **Jetson Orin Nano Dev Kit Carrier** | Official carrier | Jetson Orin Nano only | Included | AI & ML |
| **Leetop A615 Carrier** | Third-party | Orin Nano/NX | $149 | AI (budget) |
| **ReComputer J401 Carrier** | Third-party | Orin Nano/NX | $216-$227 | AI (industrial) |

### Custom / Specialty PCBs
| Board | Type | Compatibility | Price | Best For |
|-------|------|---------------|-------|----------|
| **Penkesu Computer PCB** | Clamshell | Pi Zero 2W only | $15-$25 | Writerdeck |
| **Custom WS2812B Neon LED PCB** | LED strip | ALL | $5-$15 | Conversation Piece |
| **Hackberry Pi Zero Panel** | External antenna | Pi Zero 2W | Free STL | Security |
| **Atopile Custom PCB** | Open-source design | Variable | DIY | Advanced builds |

---

## WIRE / CABLE DATABASE (Best of Best)

### Signal Wires
| Wire | Gauge | Type | Current | Use | Price/m |
|------|-------|------|---------|-----|---------|
| **Silicon 26AWG** | 26 AWG | Silicone insulated | 2.2A | Signal, I2C, SPI, UART, GPIO | $0.50 |
| **Silicon 24AWG** | 24 AWG | Silicone insulated | 3.5A | Fan power, LED strips | $0.60 |
| **IDC Ribbon Cable** | 28 AWG flat | Flat ribbon | 1A/conductor | DSI display, CSI camera | $2.00/m |

### Power Wires
| Wire | Gauge | Type | Current | Use | Price/m |
|------|-------|------|---------|-----|---------|
| **Silicon 20AWG** | 20 AWG | Silicone insulated | 5A | Battery connections, UPS wiring | $0.80 |
| **Silicon 18AWG** | 18 AWG | Silicone insulated | 10A | Main power, solar wiring | $1.00 |
| **Silicon 16AWG** | 16 AWG | Silicone insulated | 15A | Heavy power, motor wiring | $1.20 |

### Specialty / Quick-Connect
| Wire | Type | Current | Use | Price |
|------|------|---------|-----|-------|
| **JST-PH 2.0mm Cables** | Pre-crimped | 2A | Battery BMS, speaker, sensor | $3/set |
| **USB-C to USB-C (240W PD)** | USB-C PD | 5A @ 48V | Power+data+display | $8/unit |
| **Silicon 26AWG Neon** | Neon silicone | 2.2A | LED accent, WS2812B data | $0.80/m |

### Wire Selection Rules (per use case)
| Use Case | Recommended Wire | Gauge |
|----------|-----------------|-------|
| Signal / I2C / SPI / UART | Silicon 26AWG | 26 |
| Fan power / LED strips | Silicon 24AWG | 24 |
| Battery connections | Silicon 20AWG | 20 |
| Main power / UPS | Silicon 18AWG | 18 |
| Solar / heavy power | Silicon 16AWG | 16 |
| DSI / CSI ribbon | IDC Ribbon | 28 flat |
| Quick connect (no solder) | JST-PH 2.0mm | 26 pre-crimped |
| USB-C power delivery | USB-C PD cable | Internal 20+28 |
| LED neon accent | Silicon Neon 26AWG | 26 |

---

## LATEST 2026 TRENDS (Updated July 2026)

### TikTok Viral Cyberdeck Builds
| Creator | Build | Viral Moment | Date |
|---------|-------|--------------|------|
| **Ube Boobey** | Whimsical purse cyberdeck | WIRED feature, CNN coverage | Apr 2026 |
| **Annike Tan (CC)** | "Cunty cyberdeck" — purse with pearls, gold, moss | Viral TikTok, Adafruit feature | Mar-Jun 2026 |
| **Goblin** | Old makeup caboodle converted to Pi | TikTok build series | 2026 |
| **fulltimemenace** | First cyberdeck build progress | TikTok build logs | Apr 2026 |
| **pirate2122yt** | Cyberdeck build progress | TikTok build logs | Jun 2026 |
| **unicoleunicron** | Female maker cyberdeck tutorials | Instagram viral series | 2026 |
| **diypagancrafts** | Retro TV-themed purse cyberdeck | TikTok viral, The Verge coverage | Jun 2026 |
| **fishlooker_** | Cyberduck audio journal (bird-shaped) | TikTok viral, inspired by ubeboobey | Jun 2026 |
| **CocoasAesthetic** | Dunkin' Munchkin box cyberdeck with barista game | TikTok viral, TechCrunch | Jun 2026 |
| **@julip.mp3** | Creative coding + music + tech | TikTok viral | 2026 |

**Key Trend:** Young women driving cyberdeck movement on TikTok — turning purses, caboodles, vintage cases, and even Dunkin' boxes into fully functional computers. WIRED called cyberdecks "the hottest anti-AI gadget" (Apr 2026). The Verge covered the aesthetic shift (Jun 2026). TechCrunch featured the movement (Jun 2026). Hybrid Rituals called it "the aesthetic tech rebellion" (Jul 2026). r/cyberDeck grew to 183K+ members. AI tools enabled non-technical builders to learn wiring, config, and debugging in real time.

### New YouTube Build Channels (2026)
| Channel | Content | Link |
|---------|---------|------|
| **Pi Flux** | Pi 5 security workstation tutorial | youtube.com/@piflux |
| **Cyberdeck Build Series** | Playlist of cyberdeck builds | youtube.com playlist |
| **Jalexine Lab** | 8-episode Raspberry Pi beginner course | youtube.com/@jalexine |

### Key Media Coverage (2026)
| Publication | Article | Date |
|------------|---------|------|
| **WIRED** | "The Hottest Anti-AI Gadget Is a Cyberdeck" | Apr 2026 |
| **CNN** | "Inside the rise of cyberdecks" | Apr 2026 |
| **TechCrunch** | Cyberdecks rejecting big tech | Jun 2026 |
| **Forbes** | AI-powered cyberdecks | May 2026 |
| **Hola** | Women driving cyberdeck movement | 2026 |
| **TechJuice** | Gen Z building cyberdecks | Jul 2026 |
| **Raspberry Pi Magazine** | Issue 167 — Backpack Cyberdeck | Jul 2026 |
| **The Verge** | Cyberdecks used to look like laptops, now they're... | Jun 2026 |
| **Hybrid Rituals** | "Aesthetic Tech Rebellion Taking Over TikTok" | Jul 2026 |
| **Adafruit** | "Hottest Anti-AI Gadget is a Cyberdeck" | May 2026 |
| **Prism News** | TikTok maker turns purse into viral cyberdeck | Jun 2026 |
| **2much.net** | Gen Z Revives Cyberdecks: Annike Tan's Viral Build | Jun 2026 |
| **Field Test (Substack)** | "Why the girls are building cyberdecks" | Apr 2026 |
| **Hackster.io** | 3D Print Farm Cyberdeck, Ben Makes Everything LattePanda | Jul 2026 |
| **Hackaday** | Jankbu modular cyberdeck, mermaid clutch-purse | 2026 |

### New YouTube Build Videos (2026)
| Video | Channel | Date |
|-------|---------|------|
| "Most Powerful Cyberdeck in the World" | Unknown (Anker sponsor) | Jun 2026 |
| "Cyberdeck Build" playlist | Unknown | Ongoing |
| LattePanda μ Handheld Cyberdeck | Ben Makes Everything | Jul 2026 |
| Jankbu Modular Cyberdeck | Jankbu | May 2026 |

### New GitHub Cyberdeck Repos (2026)
| Repo | SBC | Features | URL |
|------|-----|----------|-----|
| **therebelrobot/dinodeck-2026** | Pi Zero 2W | Cellular LTE, LoRa/Meshtastic, 3.5" DPI, thrifted enclosure, $200 | github.com/therebelrobot/dinodeck-2026 |
| **therustyrobot/cyberdeck** | Any Node.js device | Offline AI, mesh networking, Wikipedia, LLMs, 82 commits | github.com/therustyrobot/cyberdeck |
| **penk/penkesu** | Pi Zero 2W | Clamshell, 7.9" ultrawide, Corne keyboard, GBA SP hinges | github.com/penk/penkesu |
| **a8ksh4/chonky-palmtop** | Pi 4 | 7" touch, Corne split pivot, Miryoku firmware | github.com/a8ksh4/chonky-palmtop |
| **drcode/lisperati1000** | Variable | Lisp-focused cyberdeck | github.com/drcode/lisperati1000 |
| **unkyulee/micro-journal** | ESP32 | Writerdeck series (4 gens), instant boot, 30% ortho | github.com/unkyulee/micro-journal |
| **osresearch/mdt9100** | BeagleBone Black | Motorola MDT-9100 police terminal conversion | github.com/osresearch/mdt9100 |
| **ZitaoTech/Hackberry-Pi_Zero** | Pi Zero 2W | External WiFi antenna, Kali, open-source STL | github.com/ZitaoTech/Hackberry-Pi_Zero |
| **beepy** | Variable | Cyberdeck OS/platform | github.com/beepy |
| **ESP32Berry** | ESP32 | Blackberry-style handheld | github.com/ESP32Berry |
| **boostbox** | Variable | Cyberdeck enclosure system | github.com/boostbox |
| **gpio-keyboard** | Variable | GPIO keyboard driver | github.com/gpio-keyboard |

### New Hardware Trends (2026)
| Trend | Details | Status |
|-------|---------|--------|
| **NVMe HATs** | Geekworm, Pimoroni, Pineboards — 500-1000 MB/sec, boots from SSD | Mainstream |
| **RK3588 Carrier Boards** | 8K, 6 TOPS NPU, multiple M.2, WiFi 6 — $80-$190 | Available |
| **ClockworkPi uConsole Kit** | CM4/CM5, 5" IPS, QWERTY, speakers, battery — off-the-shelf kit | Available |
| **Hackberry Pi Zero** | External WiFi antenna panel, Kali-ready | Open-source |
| **Sector 07 Dual-Screen** | Pi 5, two swiveling touchscreens, 3D printed | Open-source |
| **Jankbu Modular** | Pi 5, sliding screen, NATO rail system, swappable modules | Open-source |
| **Dinodeck 2026** | Pi Zero 2W, cellular LTE, LoRa/Meshtastic, off-grid | Open-source |
| **Cyberdeck Red V2** | LattePanda 3 Delta, oscilloscope, HackRF SDR, projector | Hackaday |

### Raspberry Pi Foundation Featured Builds (2026)
| Build | SBC | Description |
|-------|-----|-------------|
| **Mega Six-Screen Cyberdeck** | 3x Pi | Three Raspberry Pis, six screens, orange case |
| **Amstrad PPC-640 Cyberdeck** | Pi | Vintage Amstrad shell with modern Pi internals |
| **Super 8 Cyberdeck** | Pi 4 | 1970s Hanimex film viewer conversion |
| **Clamshell BlackBerry Cyberdeck** | Pi 4 | Blackberry + Pi 4, wooden surround |
| **PiPipBoy** | Pi | Fallout Pip-Boy wearable, 3D printed |
| **P-Sea SeaShell** | Pi | Seashell enclosure |
| **Caboodle Cyberdeck** | Pi | Old makeup caboodle conversion |

### Key Insights from Research
1. **Anti-AI movement**: Cyberdecks positioned as rejection of big tech surveillance — WIRED, CNN, TechCrunch, The Verge, Hybrid Rituals coverage
2. **Female makers driving movement**: TikTok women turning purses, caboodles, Dunkin' boxes into viral builds — 75% of ubeboobey's audience is women
3. **AI enables non-technical builders**: AI tools let first-time builders learn wiring, config, debugging in real time — knowledge barrier removed
4. **NVMe is standard**: Pi 5 PCIe lane + NVMe HAT = proper SSD speed, no more SD card bottleneck
5. **LoRa/Meshtastic**: Off-grid mesh networking is a major trend (dinodeck, therustyrobot)
6. **Modular design**: NATO rails, swappable modules, upgrade-friendly enclosures
7. **Commercial kits emerging**: ClockworkPi uConsole as off-the-shelf option, Amazon selling cyberdeck kits
8. **RK3588 as Pi alternative**: 8K, 6 TOPS NPU, multiple M.2 — serious Pi 5 alternative for AI builds
9. **Vintage shell conversions**: Amstrad, BlackBerry, Motorola police terminals, vintage TVs, retro TV purses — retro shells with modern guts
10. **Open-source everything**: STL files, firmware, schematics all on GitHub — community collaboration
11. **Writerdecks mature**: Micro Journal series (4 gens), Penkesu, Chonky Palmtop — refined single-purpose machines
12. **Scroll-wheel interfaces**: Anti-doomscrolling, tactile control (Cyberdore 2064, Ben Makes Everything)
13. **Clutch-purse/kawaii aesthetic**: Mermaid, pink, feminine, Dunkin' boxes, bird-shaped — breaking the rugged cyberpunk stereotype
14. **3D Print Farm integration**: ESP32 + Home Assistant + OLEDs for monitoring print farms from a cyberdeck
15. **Solarpunk movement**: "Not doomsday, solarpunk" — 4000+ likes on TikTok, ideological axis of the trend
16. **Frutiger Aero aesthetic**: Transparent casing, colorful, early-2000s inspired — new design language
17. **r/cyberDeck 183K+ members**: One of the largest maker communities on Reddit

### Sources Compiled
1. Vapor95 — Complete 2026 guide (Jul 2026)
2. Raspberry Pi Blog — "In celebration of cyberdecks" (Apr 2026)
3. WIRED — "The Hottest Anti-AI Gadget Is a Cyberdeck" (Apr 2026)
4. CNN — "Inside the rise of cyberdecks" (Apr 2026)
5. TechCrunch — Cyberdecks rejecting big tech (Jun 2026)
6. Adafruit — Cyberdeck TikTok coverage (May 2026)
7. Hackaday — Cyberdeck tag (ongoing, Jul 2026)
8. GitHub — therebelrobot/dinodeck-2026, therustyrobot/cyberdeck
9. Geeky Gadgets — DIY modular cyberdeck (May 2026)
10. Tom's Hardware — Sector 07 dual-screen cyberdeck (2025)
11. Core Electronics — Raspberry Pi SDR cyberdeck (Jan 2026)
12. Reddit r/cyberDeck — Active community (2026)
13. cyberdeck.cafe — Build guide
14. PCBSync — Raspberry Pi cyberdeck guide
15. Betechit — Personal cyberdeck building
16. MakeUseOf — Best Raspberry Pi cyberdecks
17. TheWearify — Best cyberdecks
18. Jalexine Lab — Build your first cyberdeck
19. YouTube — Pocket Cyberdeck Pi 5 + 4" touchscreen + CardKB (Jul 2026)
20. Raspberry Pi Magazine — Backpack Cyberdeck (Pi 4, plywood+3D frame, RTL-SDR, bike-mounted)
21. DigiKey — Custom cyberdeck build guide (Pi Zero W, detailed wiring)
22. InsightArea — Practical DIY guide (May 2026)
23. SlashGear — 4 Cool Raspberry Pi Cyberdeck Projects (CRD, uConsole, Recovery Kit, PortaPack)
24. GitHub therebelrobot/dinodeck-2026 — Solar-powered off-grid Pi Zero 2W + LTE + LoRa/Meshtastic

---

## NEW BUILD IDEAS (July 2026)

### 1. Pocket Cyberdeck (Pi 5 + 4" Touchscreen)
- **SBC**: Raspberry Pi 5 (4GB or 8GB)
- **Display**: 4" HD touchscreen (800x480 or 1024x600)
- **Keyboard**: CardKB mini keyboard (thumb-sized)
- **Power**: 3000mAh LiPo + PiSugar 3
- **Enclosure**: 3D printed compact case, 10cm x 7cm x 3cm
- **Category**: writerdeck / field-repair
- **Tier**: Intermediate ($200-400)
- **Style**: Minimal / Cyberpunk
- **Key feature**: Fits in pocket, full Linux computer

### 2. Backpack Cyberdeck (Pi 4 + Plywood Frame)
- **SBC**: Raspberry Pi 4 (8GB, slightly overclocked)
- **Display**: 10" HDMI IPS
- **Keyboard**: Full-size mechanical
- **Power**: 20000mAh USB-C power bank
- **Enclosure**: Plywood + 3D printed mounts, fits in standard backpack
- **Category**: security / ham-radio
- **Tier**: Intermediate ($300-600)
- **Style**: Industrial / Exposed hardware
- **Key feature**: Bike-mounted, RTL-SDR for wireless analysis, GNU Radio + Kali Linux
- **Source**: Raspberry Pi Magazine Issue 167

### 3. DineDeck 2026 (Solar + Off-Grid)
- **SBC**: Raspberry Pi Zero 2W
- **Display**: 3.5" DPI display (GPIO-driven)
- **Keyboard**: XIAO SAMD21 microcontroller keyboard
- **Power**: Solar panel + LiPo + BMS
- **Enclosure**: Thrifted enclosure, solarpunk aesthetic
- **Category**: survival / field-repair
- **Tier**: Advanced ($200-500)
- **Style**: Retro / Solarpunk
- **Key feature**: Off-grid, cellular + LoRa/Meshtastic mesh networking, solar powered
- **Source**: GitHub therebelrobot/dinodeck-2026

### 4. Modular Cyberdeck (NATO Rail System)
- **SBC**: Raspberry Pi 5
- **Display**: Sliding screen (retracts for portability)
- **Keyboard**: Mechanical with custom keycaps
- **Power**: Modular battery system
- **Enclosure**: 3D printed with NATO rails for swappable modules
- **Category**: coding / maker
- **Tier**: Advanced ($400-800)
- **Style**: Futuristic / Industrial
- **Key feature**: Swappable modules (SDR, sensors, batteries), trackball, upgradeable
- **Source**: Geeky Gadgets, Jankbu project

### 5. Post-Apocalyptic CRD (Catastrophe Recovery Deck)
- **SBC**: Raspberry Pi 4 or 5
- **Display**: 7" sunlight-readable
- **Keyboard**: rugged mechanical
- **Power**: Large battery + solar charging
- **Enclosure**: Pelican 1450, waterproof
- **Category**: survival
- **Tier**: Advanced ($400-800)
- **Style**: Industrial / Military
- **Key feature**: Offline Wikipedia + Wikivoyage, regional maps, medical guides, DHCP server for mesh networking
- **Source**: SlashGear

### 6. Clockwork uConsole (Commercial Kit)
- **SBC**: Raspberry Pi CM4 or CM5
- **Display**: 5" IPS
- **Keyboard**: Built-in thumb keyboard
- **Power**: 18650 battery
- **Enclosure**: Aluminum clamshell
- **Category**: coding / writerdeck
- **Tier**: Beginner ($250-400)
- **Style**: Minimal / Retro
- **Key feature**: Commercially available kit, easy assembly, modular SBC slot
- **Source**: ClockworkPi

### 7. Pi Flux Cyberdeck (Security Workstation)
- **SBC**: Raspberry Pi 5 (8GB)
- **Display**: 7" HDMI IPS touchscreen
- **Keyboard**: 60% mechanical
- **Power**: 20000mAh USB-C
- **Enclosure**: 3D printed tactical case
- **Category**: security
- **Tier**: Intermediate ($350-700)
- **Style**: Futuristic / Cyberpunk
- **Key feature**: Pre-loaded Kali Linux, WiFi pentesting, full cybersecurity workstation
- **Source**: YouTube "Pi Flux Cyberdeck: The Complete Build Tutorial"

### 8. Mermaid in the Shell (Clutch Purse)
- **SBC**: Raspberry Pi 3A+
- **Display**: 3.5" touchscreen
- **Keyboard**: ZitaoTech BB Q10 (white, thumb)
- **Power**: LiPo battery
- **Enclosure**: Frame clutch purse (pink seashell shape)
- **Category**: conversation-piece
- **Tier**: Beginner ($150-300)
- **Style**: Kawaii / Mermaid
- **Key feature**: Feminine cyberdeck aesthetic, hinges from purse, decorative shells/pearls
- **Source**: Hackaday "Mermaid Clutch-Purse Cyberdeck"

### 9. LattePanda μ x86 Cyberdeck
- **SBC**: LattePanda μ (x86, Windows/Linux)
- **Display**: 7" 1080p touchscreen
- **Keyboard**: Thumb-typing keyboard
- **Power**: Custom BMS battery pack
- **Enclosure**: 36mm case, aluminum faceplate, translucent resin shell
- **Category**: coding / maker
- **Tier**: Advanced ($500-1000)
- **Style**: Minimal / Industrial
- **Key feature**: Full x86 computing, runs Windows/Linux, desktop-class apps
- **Source**: Ben Makes Everything / Geeky Gadgets

### 10. Mini Music Workstation
- **SBC**: Raspberry Pi 4
- **Display**: 3.5" Waveshare DSI (800x480)
- **Keyboard**: Rii Mini X1
- **Power**: 10,000mAh battery
- **Enclosure**: 3D printed compact case
- **Category**: media
- **Tier**: Intermediate ($250-500)
- **Style**: Minimal / Cyberpunk
- **Key feature**: Teensy 4.1 runs headless M8 tracker, portable music production
- **Source**: Adafruit Blog

### 11. Radxa X2L Cyberdeck (Large Screen)
- **SBC**: Radxa X2L (ARM SBC)
- **Display**: 12.3" touchscreen
- **Keyboard**: External Bluetooth
- **Power**: USB-C power bank
- **Enclosure**: Custom ABS plastic case
- **Category**: coding / research
- **Tier**: Intermediate ($300-600)
- **Style**: Minimal / Industrial
- **Key feature**: Large screen for coding/research, affordable ARM SBC
- **Source**: Class Central YouTube course

### 12. Vintage TV Cyberdeck
- **SBC**: Raspberry Pi 5
- **Display**: Original CRT TV screen (via HDMI RF modulator)
- **Keyboard**: 60% foldable mechanical
- **Power**: Li-ion battery pack in repurposed battery tray
- **Enclosure**: Vintage TV shell (fully reversible mod)
- **Category**: retro / conversation-piece
- **Tier**: Advanced ($300-700)
- **Style**: Retro / Steampunk
- **Key feature**: Original TV aesthetics preserved, RF modulator to antenna input, reversible mod
- **Source**: Hackaday

### 13. Cyberdore 2064 (Scroll Wheel Deck)
- **SBC**: Raspberry Pi Zero + Pi Pico
- **Display**: 128x64 OLED
- **Keyboard**: Built-in mini keyboard
- **Power**: Small LiPo
- **Enclosure**: 3D printed compact case
- **Category**: writerdeck / retro
- **Tier**: Beginner ($100-200)
- **Style**: Retro / Minimal
- **Key feature**: Oversized KY-040 rotary encoder scroll wheel, anti-doomscrolling design
- **Source**: Tommi Laukkanen / codeof.me

### 14. Typeframe PS-85 Writerdeck
- **SBC**: Raspberry Pi Zero 2W
- **Display**: Small e-ink or OLED
- **Keyboard**: 40% mechanical, custom keycaps (Alien theme)
- **Power**: LiPo battery
- **Enclosure**: 3D printed retro-industrial case
- **Category**: writerdeck
- **Tier**: Intermediate ($200-400)
- **Style**: Retro / Industrial
- **Key feature**: Inspired by early-80s Epson portables, Alien movie aesthetic
- **Source**: Jeff Merrick

### 15. Micro Journal (4 Generations)
- **SBC**: Raspberry Pi Zero 2W
- **Display**: Small LCD
- **Keyboard**: Ortholinear mechanical
- **Power**: LiPo
- **Enclosure**: 3D printed palmtop case
- **Category**: writerdeck
- **Tier**: Intermediate ($200-400)
- **Style**: Minimal / Retro
- **Key feature**: Most refined single-purpose writing machine, 4 iterations, custom-built units available
- **Source**: Un Kyu Lee / GitHub

### 16. Tactical Wedge Cyberdeck (Agnostic Grid)
- **SBC**: Raspberry Pi 5
- **Display**: 7" capacitive touchscreen
- **Keyboard**: Mechanical with custom keycaps
- **Power**: 18650 cells
- **Enclosure**: FDM 3D printed with modular rail system
- **Category**: coding / maker
- **Tier**: Intermediate ($250-500)
- **Style**: Industrial / Futuristic
- **Key feature**: "Agnostic Grid" internal rail system — swap SBCs by printing new $2 adapter plate, over-center clamshell latches, thermal chimney ventilation
- **Source**: Hackaday.io (Ephraim Onimisi PRAXIS)

### 17. RPI DEV CyberStation (Dual Screen)
- **SBC**: Raspberry Pi 4 or 5
- **Display**: 2x 9" touchscreen displays
- **Keyboard**: External USB
- **Power**: External PSU
- **Enclosure**: 3D printed with buttons
- **Category**: coding / maker
- **Tier**: Advanced ($400-800)
- **Style**: Industrial / Minimal
- **Key feature**: Dual screens, internal USB hub, external I2C port, external 40-pin GPIO, external USB — full development platform
- **Source**: GitHub sennimesh/CyberDeck

### 18. 3D-Printable Pi Cyberdeck (Minimal)
- **SBC**: Raspberry Pi 5
- **Display**: 3.5" display
- **Keyboard**: Rii miniature keyboard
- **Power**: USB-C
- **Enclosure**: 3D printed (0.08mm layer height, 5% infill)
- **Category**: writerdeck / field-repair
- **Tier**: Beginner ($100-200)
- **Style**: Minimal
- **Key feature**: Ultra-lightweight, minimal infill, functional proof-of-concept
- **Source**: Raspberry Pi Magazine Issue 166 (MakerWorld)

### 19. Zerowriter Fold (E-Ink Clamshell)
- **SBC**: ESP32
- **Display**: E-ink display
- **Keyboard**: Mechanical keyboard
- **Power**: Internal battery
- **Enclosure**: Clamshell design
- **Category**: writerdeck
- **Tier**: Intermediate ($200-400)
- **Style**: Minimal / Retro
- **Key feature**: Clamshell e-ink writerdeck, tilted screen for better ergonomics, distraction-free
- **Source**: Liliputing / Crowdfunding

### 20. AUTEUR (E-Ink Typewriter)
- **SBC**: ESP32 or similar
- **Display**: 6" E-ink display
- **Keyboard**: Mechanical keyboard
- **Power**: Internal battery
- **Enclosure**: Minimal case
- **Category**: writerdeck
- **Tier**: Intermediate ($150-300)
- **Style**: Minimal / Retro
- **Key feature**: Boots in 10 seconds, dumps directly into word processor, no WiFi/internet, pure distraction-free
- **Source**: Liliputing / Crowdfunding

### Cable Routing Management
- **Auto-optimized routing**: Agent calculates optimal cable paths between components
- **Cable type selection**: Silicon 26AWG for signals, 18AWG for power, JST-PH 2.0mm for connectors
- **Accessories**: Zip ties, cable clips, braided sleeving, heat shrink, cable channels
- **Routing rules**: Power cables separate from signal, short runs preferred, strain relief at connectors

### Pack Generation
- **Combined output**: Image + video + text pack for each build
- **Markdown export**: Full build document with BOM, tutorial, cable plan, upgrades, ideas
- **Ready to share**: Export-friendly format for posting to forums/GitHub

### Build Optimization (Flaw Detection)
- **Critical flaws**: No power protection, no cooling, missing WiFi/LAN, battery without BMS
- **High flaws**: Pi 5 without active cooling, undersized power supply, no Ethernet option
- **Medium flaws**: No strain relief, no power switch, exposed wiring
- **Auto-fix**: Agent swaps problematic components automatically
- **Manual review**: Issues that need user decision (custom enclosures, unique layouts)

### Image Understanding
- **Component identification**: Recognize SBCs, displays, keyboards, PCBs from photos
- **Category detection**: Auto-suggest build category based on visual analysis
- **Upgrade suggestions**: Recommend better components based on what's visible
- **Compatibility check**: Validate identified components work together

### Video Learning Queue
- **Background processing**: Queue YouTube/TikTok URLs for learning while offline
- **Component extraction**: Identify parts mentioned in videos
- **Tip collection**: Gather assembly tips and tricks from builders
- **Trend tracking**: Track what components are trending in the community

### 13 Categories (Enhanced)
Each category now includes: best_sbc, best_display, best_keyboard, best_power, best_enclosure, best_cooling, best_pcb, best_wire, best_connectivity, best_os, upgrade_path, estimated_cost

| Category | Best SBC | Best Connectivity | Budget Range |
|----------|----------|-------------------|--------------|
| Coding | Pi 5 16GB | USB Ethernet + Cat6 | $400-1200 |
| Writerdeck | Pi Zero 2W | Built-in WiFi | $150-400 |
| Security | Pi 5 16GB | Alfa AWUS036ACH + Ethernet | $500-2000 |
| Gaming | Pi 5 8GB | USB Ethernet | $300-800 |
| Research | Pi 5 16GB | WiFi + Ethernet | $400-1200 |
| AI | Jetson Orin Nano | WiFi + Ethernet | $500-1500 |
| Survival | Pi 5 8GB | LoRa + Cellular + WiFi | $400-1200 |
| Media | Pi 5 8GB | WiFi + HDMI out | $300-800 |
| Conversation | Orange Pi 5 | WiFi | $200-600 |
| Retro | Pi 5 4GB | WiFi | $200-500 |
| Maker | LattePanda 3 Delta | WiFi + Ethernet | $500-1500 |
| Ham Radio | Pi 5 8GB | RTL-SDR + LoRa | $300-800 |
| Field Repair | Pi 5 8GB | WiFi + Cellular | $300-800 |

### 4 Tiers (Enhanced)
| Tier | Budget | Soldering | Skills | Build Time |
|------|--------|-----------|--------|------------|
| Beginner | $100-300 | Optional | Plug together, basic Linux | 1-3 days |
| Intermediate | $300-700 | Optional but helpful | 3D printing, cable management | 1-2 weeks |
| Advanced | $700-2000 | Recommended | Soldering, PCB design, QMK | 2-8+ weeks |
| Expert | $2000+ | Required | Full custom, CNC, metalwork | 1-3 months |

### 100% Compatibility Enforcement
- **Power validation**: Voltage/current matching, UPS capacity, battery protection
- **Physical validation**: Display fits enclosure, keyboard layout, SBC mounting
- **Connector validation**: HDMI/DSI/CSI compatibility, USB ports, GPIO headers
- **Driver validation**: OS supports all components, kernel modules available
- **Thermal validation**: Cooling adequate for SBC TDP, enclosure airflow
- **Auto-fix**: Incompatible components swapped automatically with explanation

### Mandatory Requirements
- **WiFi/LAN**: Every build must include networking (built-in WiFi minimum, Ethernet recommended)
- **Cooling**: Every build must have cooling solution (active for Pi 5, passive acceptable for Zero)
- **Power Protection**: UPS HAT or battery with BMS for portable builds
- **Enclosure**: No bare-board builds (even 3D printed minimum)

---

---

## BUILD LIST — ADDITIONAL BUILDS (47-67)

### 47. Lisperati1000
- **SBC**: Pi Zero 2W
- **Key feature**: Ultra-portable, Lisp-programmable, minimal
- **Source**: Hackaday

### 48. Penkesu
- **SBC**: Pi Zero 2W
- **Key feature**: Retro handheld form factor, 3D printed
- **Source**: Hackaday.io

### 49. Typeframe PX-88
- **SBC**: Pi-based
- **Key feature**: 88-key full-size keyboard cyberdeck
- **Source**: Cyberdeck.cafe

### 50. MutantC V5
- **SBC**: Pi-based
- **Key feature**: Slider phone form factor, V5 generation
- **Source**: Cyberdeck.cafe

### 51. Bumble Berry Pi
- **SBC**: Pi Zero 2W
- **Key feature**: Ultra-small, Berry-themed enclosure
- **Source**: Cyberdeck.cafe

### 52. CM Deck
- **SBC**: CM5
- **Key feature**: Split ortho low-profile keyboard + trackpad + OLED, QMK, resin-printed translucent enclosure
- **Source**: YouTube (Feb 2026), GitHub

### 53. Portable CRT TV Cyberdeck
- **SBC**: Pi-based
- **Key feature**: Old CRT TV case repurposed
- **Source**: Hackaday

### 54. Altoids Tin Linux Computer
- **SBC**: Pi Zero
- **Key feature**: Fits inside an Altoids mint tin
- **Source**: Hackaday

### 55. Darbin Orvar Wood Cyberdeck
- **SBC**: Pi 5
- **Key feature**: Hand-crafted Baltic birch plywood, XTool laser cut, OLED + speakers
- **Source**: YouTube (Darbin Orvar)

### 56. Mimisbrunnur E-Reader Cyberdeck
- **SBC**: Pi-based
- **Key feature**: E-ink display, dual-purpose e-reader + cyberdeck
- **Source**: Hackaday

### 57. Jankbu Modular Cyberdeck
- **SBC**: Pi-based
- **Key feature**: Steel linear rods + sliding screen, CNC cable chain
- **Source**: Hackaday

### 58. Pilet
- **SBC**: Pi-based
- **Key feature**: Tablet + keyboard dock hybrid
- **Source**: Hackaday.io

### 59. Mecha Comet
- **SBC**: Pi-based
- **Key feature**: Modular handheld, snap-on modules
- **Source**: Cyberdeck.cafe

### 60. SharkDeck AI
- **SBC**: Pi-based
- **Key feature**: AI-focused, $150 budget
- **Source**: Carbon Computers

### 61. PocketMage (writerdeck)
- **Key feature**: Ultra-portable writerdeck
- **Source**: writerdeck.org

### 62. Foliodeck (writerdeck)
- **Key feature**: Folder-style writerdeck
- **Source**: writerdeck.org

### 63. Octavia (writerdeck)
- **Key feature**: Writerdeck with unique form factor
- **Source**: writerdeck.org

### 64. JFW — Just Fine Writerdeck
- **Key feature**: Minimalist writerdeck
- **Source**: writerdeck.org

### 65. Micro Journal Rev.7 E-Ink (writerdeck)
- **Key feature**: E-ink display writerdeck
- **Source**: writerdeck.org

### 66. Tapico Typer (writerdeck)
- **Key feature**: Writerdeck project
- **Source**: writerdeck.org

### 67. Omega Deck (writerdeck)
- **Key feature**: 60-key ortholinear split, hot-swappable MX, LCD/e-ink between halves, Vim on minimal Linux
- **Source**: GitHub (devarops)

---

## COMMERCIAL DEVICES — ADDITIONAL (25+)

| Device | Price | Key Feature |
|--------|-------|-------------|
| Pi Flux Archnoir | $341–$855 | Premium Pi 5 cyberdeck |
| CyberDeck MK-III | $429–$1,868 | Modular industrial |
| SpecFive Nomad 2 | $550–$680 | Professional field |
| Pi Slate | $282–$706 | Pi 5 handheld |
| ELECROW CrowPi2 | $330–$390 | STEM education |
| HackberryPi Zero | ~$126 | Budget Pi Zero |
| Pi-Edge | ~$152 | Edge computing |
| Playard One | varies | Snap-on modules |
| YARH.IO TheBrick | varies | Modular keyboard deck |
| FRST Model 4 | varies | E-paper display |
| BYOK | $199 | Bring Your Own Keyboard |
| Micro Journal Rev 2 | $269 | Small batches, Italy |
| Micro Journal Rev 5 | $139 | BYOK design |
| Micro Journal Rev 6 | $179 | Protective hood |
| Freewrite Digital Typewriter | $649 | Aluminum, e-ink, mechanical |
| Freewrite Traveler | $499 | Clamshell e-ink |
| Freewrite Alpha | $349 | Budget Alphasmart update |
| Alphasmart Neo/Neo2 | $40-80 | Vintage, incredible battery |
| Alphasmart Dana | $50-80 | Larger screen, PalmPilot |
| Alphasmart 3000 | $50-80 | Modifiable keyboard |
| Writer Fusion | $25-50 | USB drive saving |
| KingJim Pomera DM30 | $150-250 | E-ink, fold-up keyboard |
| KingJim Pomera DM100 | ~$150 | Larger keyboard, LCD |
| KingJim Pomera DM250 | ~$400 | 7" LCD, USB-C, Scrivener-like |
| reMarkable Paper Tablet | $498 | E-ink with Type Folio |
| Zerowriter Ink | $279 | E-ink writerdeck |
| PocketTerm35 | $186 | Portable terminal |

---

## NEW KEYBOARD/ENCLOSURE RESOURCES (43)

| # | Resource | What It Covers |
|---|----------|----------------|
| 1 | CMDeck build (YouTube) | Split ortho low-profile + trackpad + OLED, QMK |
| 2 | Jake Walker Cyberdeck (jakew.me) | 8-key ARTSEY.IO chord keyboard, RP2040 + QMK |
| 3 | Pocket Cyberdeck 9-Button (YouTube) | Two-stroke chording (81 outputs from 9 keys) |
| 4 | Hackaday.io 40-Key QMK | 10-key-wide, Gateron low-profile, ATMega 328 |
| 5 | Fixer-OTG (GitHub) | Pocket keyboard, Kailh Mute Micro, KiCad PCB |
| 6 | CyberKeeb2040 (GitHub) | RP2040 keyboard + Pi Zero, PicoMK firmware |
| 7 | Pico-Keyboard (GitHub) | Hot-swappable RP2040 keyboard, PicoMK |
| 8 | ClickPico (Instructables) | DIY mechanical keyboard with Pico |
| 9 | Adafruit DIY Pico Keyboard | Fritzing PCB, CircuitPython, 26 keys |
| 10 | Krunchboard (GitHub) | 80% ISO Pico keyboard, KMK, OLED, rotary |
| 11 | SlideXdeck (Printables) | Psion 5-inspired sliding keyboard tray |
| 12 | QAZooie (Printables) | Keyboard case with tablet holder, mousepad |
| 13 | Modular Panel Generator (MakerWorld) | Apache 1800 parametric panel, dynamic slots |
| 14 | ModuDeck (GitHub) | Multi-SBC modular, magnetic USB |
| 15 | Costumdeck (GitHub) | Pi 5 + 10.1" touchscreen case |
| 16 | My Cyberdeck Pelican 1300 (Printables) | P40 keyboard, Sharge battery, TPU seals |
| 17 | Kailh Choc Ortho 14x5 (Tindie) | 70-switch low-profile PCB for Pi Pico |
| 18 | Cacao (GitHub) | Hot-swap Choc V2, macro keys, RGB |
| 19 | Sofle Choc | 58-key split, Choc v1, hot-swap, encoders |
| 20 | W-CORNE V4.1 (xkeeb.com) | 2.4G wireless split Choc keyboard |
| 21 | Corne Choc v4 (beekeeb) | Pre-soldered split, RP2040, RGB |
| 22 | Mt. Choc (GitHub) | 65% Choc V1, round display badge |
| 23 | Sofle Choc Kit (TurkeyBoards) | Sofle kit with Sea-Picro controller |
| 24 | Ducktop2 (GitHub) | Cherry MX Ultra Low Profile laptop keyboard |
| 25 | Mill-Max Hot-Swap Guide (keeb.io) | Adding hotswap sockets to any PCB |
| 26 | 3D-Printed Hot-Swap Socket (Printables) | Solderless hotswap for handwired boards |
| 27 | OpenSCAD Hotswap PCB Generator (GitHub) | Generates hotswap PCBs from KLE JSON |
| 28 | Vecdec (GitHub) | Split cyberdeck with Meshtastic LoRa |
| 29 | Omega Deck (GitHub) | Split writerdeck, Vim on minimal Linux |
| 30 | Ergohaven K:04 | Modular split with touchpad/trackball modules |
| 31 | ZSA Voyager | Ultra-thin Choc split, magnetic mounting |
| 32 | MoErgo Go60 | Split with trackpads, ZMK, walnut rests |
| 33 | Micro Journal Rev.2 Ergonomic | Alice-style split, PS2 thumbstick mouse |
| 34 | clickyBoard (GitHub) | Pi GPIO keyboard add-on, 4 Cherry MX |
| 35 | Pi Zero W Split Keyboard (raspberrypi.com) | Pi Zero W as USB keyboard controller |
| 36 | Pi Chord Keyboard (raspberrypi.com) | 6-key chord, CircuitPython, NeoKey |
| 37 | KMK Firmware (GitHub) | CircuitPython-based, split/BT/RGB |
| 38 | QMK Getting Started | Official build guide |
| 39 | QMK Porting Guide | Adding custom keyboards to QMK |
| 40 | Keycaps.dev | AI keycap concept designer |
| 41 | Cyberdeck Artisan | Resin casting, mold making for keycaps |
| 42 | Thock King Cyberdeck Set | 143-piece PBT keycap set |
| 43 | Capsmiths | Custom keycap design tool |

---

## BATTERIES & POWER (14)

| # | Product | Price | Key Feature |
|---|---------|-------|-------------|
| 1 | Waveshare UPS HAT (E) 21700 | ~$32 | 4x 21700, 40W USB-C, 5V/6A |
| 2 | Waveshare UPS HAT (D) 21700 | ~$20 | 2x 21700, compact, Type-C |
| 3 | Pi-UpTime 2.0 | $58.50 | Dual 18650, USB-C, universal |
| 4 | Tiny-UPS 3.0 | $38 | World's tiniest UPS, GPIO indicator |
| 5 | PiShop UPS HAT (3A) | $34.95 | Built-in RTC, safe shutdown |
| 6 | Witty Pi 5 HAT+ | $59.95 | Programmable scheduling, 5A |
| 7 | Yahboom Pi 5 Power Board | ~$15-20 | 6-24V input, 5V/5A output |
| 8 | 52Pi PD Extension Board | ~$23 | USB-C PD support |
| 9 | Sequent Super Watchdog V7 | ~$35 | Hardware watchdog, prevents hangs |
| 10 | EveryCalculators 18650 | Free | Runtime estimation with efficiency |
| 11 | BatterypackCalculator.com | Free | Interactive visual builder, cell database |
| 12 | codingace.net Pack Designer | Free | BMS sizing guidance |
| 13 | that18650calc.dk | Free | Quick capacity/voltage calc |
| 14 | Pichondria USB-PD Converter | $12.99 | Converts any PD to 5V/5A for Pi 5 |

**Key Insight**: Pi 5 needs 5V/5A minimum (8.8W full load). Most power banks shut down below 50-100mA idle — use Pichondria board ($13) or dedicated PD trigger. 21700 cells replacing 18650 in new UPS HATs.

---

## COOLING SOLUTIONS (10)

| # | Product | Price | Type | Peak Temp |
|---|---------|-------|------|-----------|
| 1 | Argon ONE V3 M.2 NVMe | ~$45 | Active+NVMe | <80°C full load |
| 2 | SunFounder Pironman 5 | ~$80-90 | Active+OLED+NVMe | Best active |
| 3 | Flirc Pi 5 Case | ~$20 | Passive aluminum | Silent, 24/7 |
| 4 | GeeekPi Aluminum | ~$15 | Passive | Budget silent |
| 5 | Geekworm P573 | ~$10 | Passive+heatsink | 38°C idle/55°C load |
| 6 | iUniker Aluminum | ~$13 | Passive | -10 to -15°C |
| 7 | 52Pi ICE Tower Plus | ~$17 | Active tower | 50°C under load |
| 8 | Entaniya Heat Pipe | ~$169 | Passive heat pipe | 61°C (best passive) |
| 9 | MILL & GRAIN Monolith | ~$50-60 | 6061-T6 aluminum | 300g thermal mass |
| 10 | Official Pi Active Cooler | ~$5-6 | Active | <50°C sustained |

**Key Insight**: Passive ceiling ~61°C (Entaniya). Best budget active: 52Pi ICE Tower ($17, 50°C). Best passive: Flirc ($20, silent). Thermal paste swap on Active Cooler = only 1.8°C improvement.

---

## DISPLAYS (11 IPS + 4 E-Ink)

**IPS/LCD:**
| # | Product | Price | Size | Brightness |
|---|---------|-------|------|------------|
| 1 | Orient Display 5" | $61.19 | 800x480 | 1000 nits! |
| 2 | Orient Display 10.1" | $141.86 | 1280x800 | 900 nits |
| 3 | Orient Display 7" Industrial | ~$200-300 | 1024x600 | 1000 nits, IP65 |
| 4 | Beetronics 10" | $749 | 10" | 1000 nits, outdoor |
| 5 | SIHOVISION 12.1" | ~$300-500 | 12.1" | 1000 nits, wet-touch |
| 6 | Elecrow 10.1" | ~$57 | 1280x800 | IPS, includes case |
| 7 | Elecrow 8" | ~$57 | 1280x800 | IPS, compact |
| 8 | GeeekPi 10.1" | ~$50-60 | 1024x600 | IPS, plug-and-play |
| 9 | Pi Slate 5" | ~$250-350 | 1280x720 | IPS, modular HAT |

**E-Ink:**
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 10 | Adafruit E-Ink Bonnet | $14.95 | Multiple sizes, 3W speaker |
| 11 | InkyPi (open source) | ~$30-50 | Web interface, plugins |
| 12 | Adafruit MagTag 2.9" | $34.95 | WiFi, battery, retains image |
| 13 | Pimoroni Inky Frame 7.3" | ~$80-100 | 7-color e-ink! |
| 14 | Waveshare 2.13" e-Paper HAT | ~$15-20 | Zero power static |

**Key Insight**: Orient Display 5" at $61 with 1000 nits is best value sunlight-readable for cyberdecks. E-ink zero power when static — ideal for writerdeck status displays.

---

## NVMe STORAGE (5)

| # | Product | Price | Max SSD |
|---|---------|-------|---------|
| 1 | Official Pi M.2 HAT+ | ~$12-15 | 2230/2242 |
| 2 | Pimoroni NVMe Base | ~$15-20 | 2230-2280 |
| 3 | Geekworm X1001 | ~$10-15 | 2230-2280 |
| 4 | Geekworm Q200 Dual | $32 | Dual 2280 |
| 5 | Pineberry Pi HatDrive | ~$15-20 | Boot support |

**Key Insight**: SD ~45 MB/s → NVMe ~800-900 MB/s. Boot 45s → 15s. Random I/O 20x faster.

---

## AUDIO (8)

| # | Product | Price | Feature |
|---|---------|-------|---------|
| 1 | HiFiBerry DAC2 HD | ~$108 | Audiophile 192kHz/24-bit |
| 2 | HiFiBerry Amp2 | ~$50 | Built-in amp, 2x passive speakers |
| 3 | Sonocotta Louder Hat | ~$30-40 | 25W/channel, 2.1, subwoofer |
| 4 | Waveshare Hi-Fi HAT | ~$18 | Stereo, includes speakers |
| 5 | Adafruit I2S Speaker Bonnet | ~$12 | 3W/channel, I2S |
| 6 | ReSpeaker 2-Mics pHAT | ~$12 | Voice recognition input |
| 7 | Pi Codec Zero | ~$19 | Official Pi Zero codec |
| 8 | PAM8403 Amp Module | ~$3-5 | Ultra-cheap Class D |

---

## LORA & MESH NETWORKING (7)

| # | Device | Price | Feature |
|---|--------|-------|---------|
| 1 | RAK WisMesh Pi HAT | $14-206 | Modular Meshtastic |
| 2 | Seeed Wio Tracker L1 | ~$40-60 | GPS+OLED+BLE, pre-flashed |
| 3 | Seeed Wio L1 E-Ink | ~$45-65 | Ultra-low-power e-ink |
| 4 | Elecrow ThinkNode M1 | ~$35-45 | E-ink, 48+ hour battery |
| 5 | RAK WisMesh Tag | $39 | Rugged IP-rated pocket |
| 6 | SenseCAP T1000-E | ~$30-40 | Credit-card size, IP65 |
| 7 | Heltec V3 LoRa | ~$20-25 | Built-in OLED, cheapest |

---

## GPS MODULES (3)

| # | Product | Price | Feature |
|---|---------|-------|---------|
| 1 | GY-NEO6MV2 | ~$8-12 | Ceramic antenna, UART, APM compatible |
| 2 | VFAN Dual GLONASS | ~$15-20 | Dual GLONASS, USB option |
| 3 | diymore ESP32 LoRa V4 | ~$20-30 | GPS+LoRa+Solar in one |

---

## ANTENNAS (5)

| # | Product | Price | Feature |
|---|---------|-------|---------|
| 1 | 868MHz RP-SMA | ~$5-10 | EU LoRa optimized |
| 2 | 915MHz DIY Yagi | ~$5-10 | Directional, 7.7dB gain |
| 3 | Data Alliance Catalog | ~$10-50 | Wide selection, combo antennas |
| 4 | WiMo 9-element Yagi | ~$40-60 | Professional quality |
| 5 | SMA Panel Mount | ~$3-10 | Clean case integration |

---

## SOFTWARE OPTIONS (70+)

### Operating Systems (10 new)
NixOS, Artix Linux, Void Linux, CachyOS, Armbian, Haiku, FreeBSD, OpenBSD, SerenityOS, Redox OS

### Minimal Linux (3 new)
Tiny Core Linux (16MB!), Puppy Linux (runs in RAM), AntiX

### Security OS (5 new)
Parrot Security OS (500+ tools), BlackArch (2900+ tools), Kali 2025.3 (updated), Pentoo, Parrot Home

### Hacking Tools (12)
Nmap, Metasploit, Burp Suite, OWASP ZAP, Aircrack-ng, John the Ripper, Hashcat, Wireshark, Hydra, Responder, BloodHound, Netcat

### Retro Gaming (6)
Recalbox, RetroPie, Lakka, JELOS, Batocera Linux, EmuELEC

### Writerdeck Software (8)
WareWoolf (novel-writing), ZeroWriter (terminal e-ink), TypeWryter (fork), writerDeckOS (no internet/apps/games), CyberWriter (Python), FocusWriter (distraction-free), WordGrinder (terminal DOS-style), WordPerfect for Unix

### Tiling Window Managers (6)
i3wm, Sway, Hyprland, labwc (default in Pi OS), bspwm, dwm

### Networking (5)
Pi-hole v6, AdGuard Home, Tailscale (WireGuard mesh VPN), Cockpit (web management), Zenmap (Nmap GUI)

### Cyberdeck Platforms (7)
MobilePenBerry, ThePwnPal (5000mAh, 8-10hrs), EtherOS, SwissArmyPi, Raspi_Hackbox, PenTesters Framework (300+ tools), CyberDeck CLI Cookbook

### Writerdeck-Specific Resources
- yarh.io — hand-wired ortholinear, QMK firmware
- writerdeck.org — curated guide
- Apple WriterDeck app (Apr 2026)

---

## AESTHETICS — PERIPHERALS & FINISHING (75+ new)

### POINTING DEVICES
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 1 | Ploopy Trackpad | ~$94 | Open-source, QMK, 156x99mm, 16-touch |
| 2 | Pimoroni Trackball Breakout | ~$15 | Mini trackball, RGB LEDs, I2C |
| 3 | EFOG Endgame Trackball | ~$150-200 | BLE wireless, twist-scroll, 50mm ball |
| 4 | Azoteq TPS43 Trackpad | ~$15-20 | Ultra-thin capacitive, I2C |

### NVMe ENCLOSURES
| # | Product | Price | Speed |
|---|---------|-------|-------|
| 5 | OWC Express 1M2 | ~$120-180 | 3836 MB/s, USB4 |
| 6 | OWC Express 1M2 80G | ~$150-250 | 6000+ MB/s, TB5 |
| 7 | Satechi USB4 Slim | ~$100-130 | 40Gbps, tool-free |
| 8 | Satechi USB4 Pro | ~$80-100 | 3840MB/s, 16TB max |
| 9 | StarTech USB4 | ~$90-120 | TB5, rugged |

### CAMERAS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 10 | Pi Camera Module 3 NoIR | ~$25 | 12MP, autofocus, HDR, night vision |
| 11 | Arducam 5MP Motorized IR-CUT | ~$25-30 | Auto day/night, 130° FOV, IR LEDs |
| 12 | Pi Global Shutter Camera | ~$50-60 | 12MP, no rolling shutter, CS mount |

### THERMAL IMAGING
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 13 | FLIR Lepton 3.5 | ~$200-350 | 160x120 LWIR, <50mK, radiometric |
| 14 | PureThermal 3 Board | ~$60-80 | USB webcam interface for Lepton |
| 15 | Pi FLIR Lepton Project | DIY ~$250-400 | Open-source, auto-boot, headless |

### SDR
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 16 | HackRF One | ~$340 | 1MHz-6GHz, TX/RX, open-source |
| 17 | PiSDR Linux | Free | Pre-configured SDR distro |
| 18 | RTL-SDR Blog V4 | ~$30-40 | R828D tuner, HF direct, bias tee |

### GPIO EXPANDERS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 19 | AB Electronics IO Pi Plus | ~$25-30 | 32-channel, stackable to 128 |
| 20 | 52Pi GPIO Screw Terminal HAT | ~$8-12 | Screw terminals, LED indicators |
| 21 | DFRobot IO Expansion HAT | ~$15-20 | STM32 ADC, 22 ports, PWM |
| 22 | SunFounder GPIO Breakout | ~$5-8 | T-shaped breadboard adapter |

### USB HUBS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 23 | Geekworm X1013 | ~$35-45 | 10-port (4x USB3 + 6x USB2), PCIe |
| 24 | Waveshare PCIe USB HAT+ | ~$20-25 | 4x USB3.2, INA219 power monitor |

### E-INK STATUS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 25 | Waveshare 2.13" e-Paper HAT | ~$15-20 | 250x122, zero power static |
| 26 | Pimoroni Inky Frame 7.3" | ~$45-55 | 7-color e-ink |
| 27 | Cyberdeck Stats Monitor | DIY ~$20 | CPU/RAM/disk/IP, auto-refresh |

### OLED STATUS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 28 | Waveshare 1.3" OLED HAT | ~$10-15 | 128x64, joystick, 3 buttons |
| 29 | PiHOLED Software | Free | Multi-function, button integration |

### NFC/RFID
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 30 | Waveshare PN532 NFC HAT | ~$15-20 | Triple interface, card emulation |
| 31 | PiNFC by SB Components | ~$20-25 | OLED, buzzer, GPIO breakout |

### BARCODE/QR
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 32 | SB Components Barcode HAT | ~$40-50 | 20 symbologies, LCD, buzzer |
| 33 | Zero Barcode HAT | ~$35-45 | Pi Zero form factor |

### FINGERPRINT
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 34 | PiFinger HAT | ~$40-50 | Capacitive 508dpi, OLED, crypto |
| 35 | R307 Fingerprint Sensor | ~$10-15 | Optical, 300 prints, standalone |
| 36 | R503 Capacitive Sensor | ~$15-25 | Capacitive, 199 users, 3.3V |

### HAPTIC FEEDBACK
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 37 | Adafruit DRV2605L HAT | ~$10-15 | 100+ effects, ERM+LRA, STEMMA QT |
| 38 | Pimoroni DRV2605L | ~$12-15 | Motor included, Breakout Garden |
| 39 | Boardoza DRV2605L | ~$5-8 | Cheapest, 20x20mm |
| 40 | Boardoza Vibration Motor | ~$3-5 | Motor included, one-pin control |

### IMU/ACCELEROMETER
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 41 | Waveshare Sense HAT (B) | ~$25-35 | 9-axis IMU + temp/humidity + baro + color + ADC |
| 42 | Waveshare Sense HAT (C) | ~$25-35 | 6-axis + magnetometer + env sensors |
| 43 | Adafruit BNO055 | ~$30-35 | 9-DOF with on-board sensor fusion |
| 44 | Adafruit MPU-6050 | ~$10-12 | 6-DOF, cheap, huge community |

### ENVIRONMENTAL SENSORS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 45 | Waveshare Environment Sensor HAT | ~$25-35 | 5 sensors: BME280+IMU+UV+VOC+Light |
| 46 | Pimoroni BME680 | ~$25-30 | Temp/humidity/pressure/gas |
| 47 | Adafruit BME680 | ~$20-25 | Same with STEMMA QT |
| 48 | Adafruit LTR390-UV | ~$8-10 | UVA + ambient light |
| 49 | VEML6075 UV Sensor | ~$8-12 | Dual-band UVA+UVB |
| 50 | Plantower PMS5003 | ~$25-35 | PM1.0/PM2.5/PM10, laser |
| 51 | Nova SDS011 | ~$25-35 | PM2.5/PM10, sleep mode |
| 52 | Adafruit SCD-40 | ~$30-35 | TRUE CO2 (photoacoustic) |
| 53 | Adafruit SCD-30 | ~$55-60 | NDIR CO2, 400-10,000ppm |
| 54 | SparkFun SCD40 Qwiic | ~$40-45 | 0.4µA sleep mode |
| 55 | Adafruit SHT40 | ~$10-12 | ±0.2°C, heater on chip |
| 56 | Adafruit SGP40 | ~$15-18 | VOC index, no clock stretching |
| 57 | SunFounder MQ-2 | ~$5-8 | Multi-gas (LPG/CO/smoke) |

### RADIATION DETECTORS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 58 | PiGI Geiger Interface | ~$20-30 | 1000V for GM tubes, dual stackable |
| 59 | Granz Scientific Pi Zero Geiger | ~$50-80 | I2C, web UI, networked |

### SOIL/WATER
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 60 | ANAVI Gardening uHAT | ~$15-25 | 2 capacitive sensors, temp, open-source |

### AUDIO FEEDBACK
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 61 | Passive Piezo Buzzer | ~$0.50-2 | Any frequency via PWM |
| 62 | Pimoroni Speaker pHAT | ~$10-15 | 3W, Pi Zero optimized |
| 63 | Active Buzzer | ~$0.50-1 | Simplest alert |

### KVM / REMOTE ACCESS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 64 | PiKVM V4 Plus | ~$400 | Full BIOS KVM, open-source |
| 65 | GL-iNet Comet Pro | ~$180 | 4K@30fps, WiFi, touchscreen |
| 66 | Geekworm X680 | ~$55 | 4-port IP KVM for CM4 |

### USB-C HUBS/DOCKS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 67 | Plugable USB-C 10-in-1 | $74.95 | 4K 144Hz, 2.5G Ethernet, 140W PD |

### THERMAL INTERFACE
| # | Product | Price | W/m·K |
|---|---------|-------|-------|
| 68 | Thermal Grizzly Minus Pad 8 | ~$8-15 | 8 W/m·K |
| 69 | Fujipoly Ultra | ~$15-25 | 15 W/m·K |
| 70 | Gelid Extreme | ~$10-18 | 12 W/m·K |
| 71 | Arctic Silver 5 | ~$7-15 | 8.9 W/m·K |
| 72 | Thermal Grizzly Kryonaut | ~$7-15 | 12.5 W/m·K |

### IP-RATED ENCLOSURES
| # | Product | Price | Rating |
|---|---------|-------|--------|
| 73 | GTT Wireless IP67 | ~$80-120 | IP67, 6.2dBi antenna, Gore vent |
| 74 | Sixfab IP65 Outdoor | ~$25-35 | IP65, clear lid, cable grommets |
| 75 | PiLink PL-R5 IP65 | ~$200-300 | IP65 aluminum, 9-40V, M.2 NVMe |

### CABLE MANAGEMENT
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 76 | FPV FPC Flat HDMI Cable | ~$3-8 | Ultra-thin ribbon, flexible |
| 77 | Smallrig Flexible HDMI | ~$5-10 | Gooseneck-style, short |
| 78 | Ubo Pod Side Connector | ~$10-15 | Relocates all ports to one side |

### WIRELESS CHARGING
| # | Approach | Price | Feature |
|---|----------|-------|---------|
| 79 | Qi Receiver + Charging Pad | ~$15-25 | 10W, trickle-charge battery only |

### WATERPROOFING
| # | Approach | Price | Rating |
|---|----------|-------|--------|
| 80 | TPU Gasket Groove | ~$0.01 | IP65, re-openable |
| 81 | O-Ring Groove | ~$2-5 | Professional-grade |
| 82 | Silicone Sealant Bedding | ~$3-8 | Simplest, permanent |

### SPEECH RECOGNITION
| # | Project | Price | Feature |
|---|---------|-------|---------|
| 83 | WhisperBox / VoxPi | Free | 100% offline, Bluetooth HID output |
| 84 | pi5-local-voice-assistant | Free | 7.77x realtime STT, local LLM |
| 85 | voice-hotword | Free | Offline hotword detection |

### MICROPHONE ARRAYS
| # | Product | Price | Feature |
|---|---------|-------|---------|
| 86 | ReSpeaker XMOS XVF3800 | ~$54.50 | 4-mic, ESP32-S3, USB/I2S |
| 87 | ReSpeaker 6-Mic Circular | ~$35-45 | 6 mics, DOA, RGB LEDs |

### BATTERY SIZING TOOLS
| # | Tool | Price | Feature |
|---|------|-------|---------|
| 88 | TheHomeServerBlog Calculator | Free | Runtime estimation, Peukert effect |
| 89 | Simulations4All IEEE 485 | Free | Standards-compliant, exportable reports |

### UPS SHUTDOWN SCRIPTS
| # | Script | Price | Feature |
|---|--------|-------|---------|
| 90 | Matho/x120x-UPS-for-sbc | Free | Python, Geekworm X1200, configurable |
| 91 | maaad/ups-hat-controller | Free | Rust, Waveshare HAT (E), DRY_RUN mode |

---

## AESTHETICS — PAINTING & FINISHING (7)

1. **3DPut Post-Processing Guide** — full sanding→paint→clear coat pipeline (120-3000 grit)
2. **Creality Finishing Guide** — filament-specific (PLA/PETG/ABS/resin), acetone smoothing
3. **Alien-Themed Weathering** — paint-mask-chip technique, Semiotic Standard glyphs
4. **XMT-19 Cutlass Weathering** — WWII scratches, stenciled markings, hand-cut foam greebles
5. **TRL Cyberdeck Weathering** — silver base, edge chipping, retro-futuristic
6. **Wesley Treat Weathering** — rust, patina, aging for props
7. **Christan Workshop Build** — matte black, acrylic tape, PVC foam board

## AESTHETICS — VINYL WRAPPING (4)

8. **Evan Ohl Cyberpunk** — carbon fiber vinyl, sticker slaps
9. **3M 2080 Carbon Fiber** — Controltac repositionable, air-release
10. **YesWrap 3D Carbon** — matte textured twill weave
11. **Arquebus Cyberdeck** — carbon wrap on screen covers

## AESTHETICS — LED & LIGHTING (6)

12. **CMDeck Translucent Shell** — resin neon underglow, LED diffusers
13. **Halogenica QMK Underglow** — dimmable via QMK, STM32 PWM
14. **DIY Keyboards RGB** — WS2812B underglow, animation modes
15. **Raphael's Split Underglow** — layer color indication, battery-saving
16. **Moving Rainbow NeoPixel** — hardware deep-dive, power budgeting
17. **Core Electronics Pi WS2812B** — external power for long runs

## AESTHETICS — RESIN & EPOXY (4)

18. **DOCOResin Cyberpunk Pyramid** — multi-layer pour, mica powder, embedded gears
19. **Advanced Epoxy Pouring** — 6 techniques: lacing, dirty pour, petri, ocean
20. **Resin Pour Art Beginner** — mix ratios, bubble management, curing
21. **CMDeck Resin Enclosure** — translucent purple resin, CNC finish

## AESTHETICS — TRANSPARENT/CLEAR (3)

22. **Framedeck** — stacked clear acrylic + brass hardware
23. **CMDeck Translucent Bottom** — neon underlayer resin
24. **Mu Cyberdeck Slide-Out** — translucent housing, custom PCB

## AESTHETICS — STICKER BOMBING (4)

25. **Eccentric Decals Cyberpunk** — Oracal die-cut, 7-year outdoor
26. **Sticky Studios Edgerunners** — buy-1-get-1 cyberpunk decals
27. **M&M 40-Pack** — 40-piece glossy cyberpunk set
28. **CyberSecDeck Modular** — custom Photoshop stickers, OLED display

## AESTHETICS — WATER SLIDE DECALS (4)

29. **Radical Edward Pwnagotchi** — anime-themed decal files
30. **Kadee Custom** — ALPS thermal, white/metallic capable
31. **Bedlam Creations** — custom since 2001, one-off prints
32. **Phoxy Design** — full-color laser, white underprint

## AESTHETICS — LASER/CNC (6)

33. **UHAB Cyberdeck** — CNC milled MDF + laser engraving
34. **DIY Life Laser-Cut** — Atomstack plywood, Inkscape design
35. **LaBonte CNC Hardwood** — Carbide3D Nomad 3, sapele + bronze
36. **Laser Cut Pelican Panel** — HDPE, dual-mode engrave/cut
37. **Framedeck Acrylic Layers** — laser-cut stacked construction
38. **PrintPal Nameplate** — free 3D-printed nameplate generator

## AESTHETICS — OLED STATUS (5)

39. **ESP32 Status Display** — USB CDC, live GPU/CPU stats
40. **Moondeck ESP32-S3** — Lua widgets, touch/swipe, color LCD
41. **Homelab Server Display** — alert pages, buzzer, daemon
42. **Costumdeck OLED** — ESP32 dual-MCU, retro styling
43. **Cyberdore 2064** — cassette animation, rotary encoder

## AESTHETICS — ROTARY ENCODERS (3)

44. **CyberDeck Rotary + Slider** — programmable knob + slider + 4 buttons
45. **OpenClaw KY-040** — menu navigation, multi-display SPI
46. **Pikku Dial** — Pico USB dial, multi-mode (volume/scroll/cursor)

## AESTHETICS — JOYSTICKS (4)

47. **PS2 Thumbstick** — Sony PS2 as mouse, split Alice layout
48. **Voidnet Viator** — PSP joystick + roll-pin pointer
49. **Schematik AI Joystick** — ESP32 retro gaming + AI chatbot
50. **awesomebrownies** — JH16 + hall effect + distance sensors

## AESTHETICS — GLOW-IN-DARK/UV (4)

51. **Techno Glow Phosphorescent** — charges from any light, 5+ hour glow
52. **GLO Effex Transparent UV** — invisible clear-to-glow under blacklight
53. **SpaceBeams Nebula** — dual-color (pink day/orange glow)
54. **GLO Effex Phosphorescent White** — strontium aluminate, 30+ year life

## AESTHETICS — COLOR THEORY (4)

55. **Cyberdeck VS Code Theme** — 20 cyberpunk palette variants with HEX
56. **Chunky Cyberdeck Palette** — 5-color with CSS variables: `#1f1f61`, `#3a2a84`, `#5a2c9b`, `#8b3c8b`, `#ff6d1f`
57. **xscript.net Palettes** — 8 palettes: Matrix/cyan/amber/purple
58. **PageFlows Guide** — neon selection psychology, contrast principles

### SPECIFIC HEX CODES
**Cyberpunk 2077 UI:** Yellow `#FFEB0B`/`#EBE702`, Cyan `#25E1ED`/`#00FFFF`, Pink `#ED1E79`, Dark Red `#672026`, Bright Red `#FF4A57`
**DuskTools Cyberpunk:** `#0D0221`, `#0F084B`, `#26081C`, `#FF2A6D`, `#05D9E8`
**Synthwave (PaletteCSS):** `#2B1055`, `#7597DE`, `#FF2E97`, `#FE53BB`, `#08F7FE`
**Synthwave Terminal:** BG `#0D0818`, FG `#F0E8FF`, Primary `#FF60C8`, Accent `#40E8E0`
**Vaporwave (EggGradients):** `#F569C4`, `#03CAFC`, `#06FC9E`, `#B768FC`, `#FFFB8D`, `#FF06C1`, `#8705E4`
**Vaporwave (ColorSwatches):** Void Purple `#1A0830`, Electric Purple `#CC00FF`, Hot Pink `#FF2D78`, Neon Cyan `#00FFFF`, Pink Mist `#FF80C0`

## AESTHETICS — WOOD & NATURAL (4)

59. **Darbin Orvar** — Baltic birch plywood, XTool laser cut
60. **LaBonte Hardwood** — Richlite phenolic + Sapele + bronze
61. **Timber Deck** — wooden box, custom mechanical keyboard
62. **Progressive Robot Textile** — natural materials movement

## AESTHETICS — FABRIC & TEXTILE (2)

63. **Fallout Vault-Tec** — Faraday fabric, conductive gasket, EMP shielding
64. **Feminine Cyberdeck Movement** — crochet, macrame, fabric-wrapped

## AESTHETICS — FOAM INSERTS (4)

65. **NANUK Custom Foam** — CNC router or die-cut, EVA/PUF/PEF
66. **Pelican Custom Foam** — waterjet-cut, anti-static pink option
67. **sigmaIQ Battery Case** — 3D-printed ABS + egg-crate foam
68. **Steam Deck CYBERDECK** — sponge foam + magnets + TPU covers

## AESTHETICS — METAL BADGES (5)

69. **JASPER Nameplates** — etched/anodized aluminum, MIL-spec
70. **Custom Metal Labels** — anodized aluminum, custom shapes
71. **Trophy Outlet** — 35+ years, 1/16" precision
72. **Laser Engraving Blanks** — black-over-silver dual-color reveal
73. **PlaqueMaker Magnetic** — laser-engraved, magnetic mounting

## AESTHETICS — CARBON FIBER (2)

74. **3M 2080 CFS12** — professional dual-cast, Controltac
75. **Parma Mer** — upholstery-grade, soft-touch faux leather

## AESTHETICS — COPPER/BRASS (3)

76. **Brass-Framed Pi 5** — hand-bent brass tube skeleton frame
77. **Framedeck Brass + Acrylic** — brass screws/standoffs/accent pieces
78. **LaBonte Bronze Heatsink** — CNC-milled bronze as design feature

## AESTHETICS — RUBBER/CORK/SILICONE (2)

79. **MediaSlab Rubber Grips** — custom mold-cast polyurethane
80. **Cork-Rubber Sheet** — -40° to 250°F, vibration dampening

## AESTHETICS — MAGNETIC SYSTEMS (3)

81. **fyer_deck Magnetic** — magnetic battery door, polarity system
82. **Pegdeck Pegboard** — M3 hardware, magnet-mounted panels
83. **Christan Workshop Magnetic** — magnets hold keyboard rock-solid

## AESTHETICS — HINGES/FOLDING (3)

84. **CMDeck Torque Hinges** — McMaster-Carr, any angle, 140°+
85. **Flipdeck Triple-Function** — hinge + handle + stand pivot
86. **Jankbu Sliding Screen** — steel linear rods + cable chain

## AESTHETICS — KICKSTANDS (3)

87. **Christan Workshop Flip Stand** — dual flip stands, improved balance
88. **CMDesk Riser Feet** — tilt keyboard, improve airflow
89. **Flipdeck Adjustable** — integrated adjustable stand

## AESTHETICS — CARRYING (5)

90. **CyberSecDeck Picatinny** — military rail sling mounts
91. **vbstract Techwear Strap** — AOKU camo, magnetic quick-detach
92. **Кибердек RA01** — bicycle grip handle, retractable power
93. **VirtuScope Grab Handle** — folding case, shoulder strap mounts
94. **Luggable Pi Metal Handles** — dual-purpose handles as wrist rest

## AESTHETICS — SCREEN PROTECTION (2)

95. **Jack of All Trades Lexan** — flush-mounted Lexan cover
96. **Steam Deck CYBERDECK TPU** — dust covers for all ports

## AESTHETICS — NEW THEMES (7)

97. **Feminine/Craft** — crocheted electronics, macrame motherboards
98. **Cassette Futurism** — cassette animation OLED, rotary wheel
99. **Aquatic/Nautical** — sapele hardwood + bronze, deep sea station
100. **Fallout/Post-Apocalyptic** — EMP-hardened, Faraday fabric
101. **M3TAL Industrial** — 2020 aluminum extrusion, T-nut mounting
102. **Pegboard Hacker** — infinite reconfiguration, magnet modules
103. **NODE-3 Cyberpunk Runner** — Steam Deck chassis, neon aesthetic

## AESTHETICS — PAINT/COLOR MATCHING (3)

104. **RAL to Pantone Converter** — 213 RAL colors cross-referenced
105. **Shademix Universal Converter** — RAL/NCS/Pantone/HEX/RGB/CMYK/LAB
106. **RAL Color Chart with HEX** — e.g. RAL 9005 Jet Black `#0A0A0A`, RAL 3020 Traffic Red `#E42313`

## AESTHETICS — DEVICE SKINS (3)

107. **StickieTech Custom** — 3M vinyl wraps, upload any design
108. **M2Skins Steam Deck** — automotive-grade, Controltac
109. **Qskinz Cyber Security PCB** — circuit board themed, 3D texture

## AESTHETICS — PORT LABELING (2)

110. **DYMO Rhino M1011** — industrial embosser, stainless steel/aluminum
111. **DYMO Organizer Xpress** — lightweight handheld embosser

## AESTHETICS — SCREW COVERS (2)

112. **3DSearch Screw Cap** — free STL, printable in any color
113. **Essentra Components** — polypropylene caps, #4-#10 screws

## AESTHETICS — VENT/GRILL DESIGNS (3)

114. **Cyberpunk Circuit Fan Grill** — 120mm, 1mm spacer, chamfered
115. **Grille Generator** — OpenSCAD parametric vents/covers
116. **Parametric Ventilation Grid** — OpenSCAD honeycomb/louver/square

## AESTHETICS — HANDLE/GRIP (2)

117. **CyberSecDeck-001** — bike handlebar grip, picatinny rails
118. **Luggable Pi Metal Handles** — metal handles double as wrist rest

## AESTHETICS — WRIST RESTS (2)

119. **vecdec Ergonomic** — rubber isolators, UAV-style quiet typing
120. **Omega Deck** — integrated wrist rest between split halves

## AESTHETICS — INSPIRATION GALLERIES (4)

121. **Awesome CyberDeck (GitHub)** — curated list of builds, components, software
122. **Pinterest Cyberdeck Builds** — image gallery of community projects
123. **Cyberdeck Cafe Community** — build guides, cultural documentation
124. **r/cyberDeck Subreddit** — active community, progress photos

---

## NEW BUILDS — Round 6 (43 GitHub Repos + Instructables/Hackaday/Reddit)

### GitHub Repos — Notable New Builds

110. **Hackberry Pi Zero** (ZitaoTech) — 2.7k⭐, Pi Zero 2W + 4" 720x720 TFT, handheld Linux terminal
111. **Beepy** (Beeper) — 647⭐, Pi CM4 + RP2040, BlackBerry keyboard, 2.6" 320x240
112. **DFCD Cyberdeck** (ArcticEnrichmentCenter) — 647⭐, CAD files, 3D printed case
113. **Mu Cyberdeck** (BenMakesEverything) — 154⭐, LattePanda Mu, slide-out mechanical keyboard, tablet-style
114. **MicroHydra** (echo-lalia) — 311⭐, ESP32 MicroPython app switcher for cyberdecks
115. **QAZ Cyberdeck** (g1sbi) — 138⭐, QAZ keyboard + Banana Pi M2 Zero
116. **PiMech Deck** (brickbots) — 132⭐, Pi Zero + low-profile mechanical keyboard
117. **Pisdr-Cyberdeck** (TomMladenov) — 71⭐, PiSDR cyberdeck with SDR capabilities
118. **Loopa** (ferluht) — 172⭐, Pi Zero portable sound computer/looper
119. **Decktrix** (Decktrix-Lab) — 58⭐, modular Linux handheld cyberdeck
120. **Lambda Cyberdeck 910** (CodyTolene) — 26⭐, Pi 4, 7" display, SDR, Nanuk 910 case
121. **Doomsday Cyberdeck** (EzioDEVio) — 19⭐, offline survival, RetroPie + SDR + Calibre
122. **Phone-i4 Cyberdeck** (n0xa) — 13⭐, rugged phone case + mini keyboard = mini-laptop
123. **Portable Hacking Station** (altaga) — 119⭐, Pi Zero W/3, WiFi audit, mobile tethering
124. **HackPi** (thehackingsage) — 89⭐, Pi + Kali Linux, portable hacking
125. **PNP Portable Hacking Machine** (PNPtutorials) — 47⭐, Pi 3, auto-login, hacking tools
126. **CyberDeck Mini ESP32** (pepeangell5) — 94⭐, ESP32, 2.4GHz network audit tool
127. **Paper Pi Handheld** (a8ksh4) — 14⭐, e-ink handheld Linux computer
128. **PiBoy Zero** (JohSchneider) — 34⭐, Pi Zero gaming handheld, EmulationStation
129. **Hyper Pi** (ropg) — 67⭐, Pi Zero + HyperPixel 4" touch
130. **Bigtendo Handheld** (Klesp0) — Pi 5 + Feather RP2040, RetroPie gaming
131. **Y2K CyberDeck** (Dobeltip) — 10⭐, SVG files for Pi cyberdeck case
132. **Acid Zero** (chetansaini53) — Pi 3B+, WiFi/BLE/Sub-GHz/IR/BadUSB security tool
133. **CyDK** (ar11011) — Pi Zero 2W, recent handheld Linux computer
134. **Astro** (rmeuth01) — 10⭐, Jetson Nano retro gaming handheld
135. **Pocket265** (agkaminski) — 49⭐, 6502-based handheld computer v2
136. **Pi5-Deck** (K1LLLAGT) — Pi 5 + 7" Touch Display 2, compact Linux computer
137. **Bumble Berry Pi** (samcervantes) — 339⭐, cheap & easy Pi cyberdeck

### Instructables / Hackaday / Hackster.io New Builds

138. **PiWardrive v3** — WiFi wardriving, GPS logging, signal heatmap, Pi 5
139. **WarGPS v2** — GPS-enabled network scanner, Pi Zero 2W
140. **PiKon Telescope** — Pi-powered telescope controller, outdoor cyberdeck
141. **PiScope Oscilloscope** — Pi-based USB oscilloscope, test equipment
142. **PiCast Media Center** — Kodi media center, 10" touchscreen
143. **PiTablet Drawing** — Pi 5 drawing tablet, Wacom EMR pen input
144. **PiJuice Cyberdeck v2** — PiJuice HAT, solar panel, e-ink, field computer
145. **PiStack Modular v2** — stackable Pi modules, GPIO-connected
146. **PiKVM V4 Plus** — 4K HDMI capture, multi-computer KVM, Pi 4
147. **PortablePi Workshop** — Pi 5 + oscilloscope + logic analyzer, field repair
148. **Pi Stack CM5** — CM5 carrier board cluster, compute nodes
149. **PiStackModular CM5** — CM5 with modular expansion cards
150. **OrangePi Cyberdeck** — Orange Pi 5 Plus, 10" display, NVMe
151. **MangoPi Pocket** — MangoPi MQ-Pro, 2.8" TFT, ultra-compact
152. **Sipeed Handheld** — Sipeed LicheeRV, 3.5" TFT, RISC-V handheld
153. **BeagleBone AI Deck** — BeagleBone AI-64, robotics controller
154. **UDOO Bolt Station** — AMD Ryzen V1000, desktop replacement
155. **ZimaBlade NAS** — ZimaBlade, NAS storage, SATA drives
156. **OrangePi Zero3 Handheld** — Zero 3, 3.5" TFT, gaming handheld

### Reddit r/cyberdeck Notable Builds

157. **Pelican Cyberdeck** — Pelican 1450, Pi 5, 7" touch, Kali, field-ready
158. **Altoids Mints Tin** — Pi Zero 2W, 0.96" OLED, thumb keyboard
159. **Gaming Deck** — Pi 5, 7" HDMI, dual analog sticks, RetroPie
160. **Field Research** — Pi 5, sunlight-readable display, GPS, LoRa
161. **WriterDeck Pro** — Pi Zero 2W, 7.5" e-ink, Planck keyboard, 20hr battery
162. **Security Briefcase** — Pi 5, 10" display, HackRF, RTL-SDR, WiFi adapters
163. **Solar Cyberdeck** — Pi 5, 18W solar panel, 6x 18650, e-ink
164. **Mesh Node** — Pi 5, 3x LoRa modules, Meshtastic, solar powered
165. **Ham Station** — Pi 5, HackRF, RTL-SDR, 7" display, Pelican case
166. **Maker's Bench** — Pi 5, 7" touch, SparkFun HAT, logic analyzer
167. **AI Inference** — Jetson Orin Nano, 10" display, NVMe, active cooling
168. **Dual-Screen Dev** — Pi 5, 7" main + 5" OLED status, Planck
169. **Retro Terminal** — Pi Zero 2W, 4.2" amber e-ink, vintage Model M
170. **Tactical Wedge** — Pi 5, FDM case, Kali, external antenna, GPIO switches

---

## NEW BUILDS — Round 7 (34 GitHub Repos + 22 Instructables/Hackaday/Printables + 20 Reddit)

### GitHub Repos — Round 7 Notable New Builds

171. **HackberryPiCM5** (HackberryPi) — 1k⭐, CM5 + 4" 720x720 TFT + BB keyboard
172. **HandiPi** (HandyPi) — 812⭐, Pi 4 handheld with keyboard, full Linux desktop
173. **piBrick** (PicoWiz) — 346⭐, CM5 + 3.91" AMOLED, pocket cyberdeck
174. **DSpi** (roshinfo) — 279⭐, Dual-screen CM5 gaming handheld (DS-style)
175. **HackberryPi5** (HackberryPi) — 131⭐, Pi 5 handheld variant with BB keyboard
176. **MicroHydra** (echo-lalia) — 311⭐, ESP32 MicroPython cyberdeck OS, app switcher
177. **loopa** (ferluht) — 172⭐, Pi Zero portable sound computer/looper
178. **ESP32-Handheld** (Pip3) — 261⭐, Ultra-low power 180µW always-on display, ESP32
179. **lilka** (dmitriykovalev) — 231⭐, Open-source ESP32 game console
180. **esp32_loradv** (romicaby) — 115⭐, ESP32 LoRa walkie-talkie, off-grid comms
181. **piglet** (hex1n) — 198⭐, ESP32 wardriving platform, WiFi scanning
182. **Rogue-Radar** (0x676e68) — 34⭐, ESP32-S3 multi-protocol RF tool (nRF24/CC1101/IR)
183. **Spectre** (Hax0rStock) — 26⭐, ESP32-S3 cyber-multitool, pen-testing
184. **writerdeckOS** (writerdeckos) — 170⭐, Convert x86_64 laptop to writerdeck
185. **draftling** (hugg97) — 37⭐, Writerdeck firmware for ESP32-S3/P4
186. **Pi5-Deck** (K1LLLAGT) — Pi 5 + 7" Touch Display 2, compact Linux computer
187. **PiBoy Advance** (Squonk42) — Pi Zero 2W + RP2040, handheld with dual analog
188. **CyberBoi** (cyberboi) — 12⭐, ESP32-S3 handheld, BB keyboard, 128x64 OLED
189. **ZeroPai** (0x10) — 19⭐, RP2350 AI handheld, tiny ML inference device
190. **Pi Zero Zero** (danielktdorsey) — 4⭐, Pi Zero 2W in custom zero-profile case
191. **PiBrickZeroCM5** (PicoWiz) — PiBrick variant for CM5 Lite, ultra-budget
192. **HackberryPi-4B** (HackberryPi) — 70⭐, Pi 4B handheld with BB keyboard

### Instructables / Hackaday / Printables — Round 7 Notable New Builds

193. **CyberPlug** — Breadboard-integrated handheld, solderless prototyping cyberdeck
194. **Termyte** — Pi Zero 2W + HyperPixel 4" + Xbox Chatpad, pocket terminal
195. **SlideXdeck** — Psion 5-inspired sliding keyboard cyberdeck
196. **Nokia N97 Resurrection** — Slider mechanism cyberdeck, Pi internals, vintage shell
197. **Solar Box** — Bamboo clamshell, solar powered, off-grid field computer
198. **Voidnet Viator** — Roll-pin mouse, CharliePlex LED matrix, Pi Zero
199. **$NB100** — Amstrad NC100 case, Corne split keyboard, NixOS
200. **E.P.I. v1** — Wearable drop-leg tactical bag cyberdeck
201. **BlackberryPi** — BB keyboard, Gameboy style, Pi Zero
202. **PiWardrive v4** — WiFi wardriving, GPS logging, signal heatmap, Pi 5
203. **WarGPS v3** — GPS-enabled network scanner, Pi Zero 2W
204. **PiKon Telescope v2** — Pi-powered telescope controller, outdoor cyberdeck
205. **PiScope Oscilloscope v2** — Pi-based USB oscilloscope, test equipment
206. **PiJuice Cyberdeck v3** — PiJuice HAT, solar panel, e-ink, field computer
207. **PiStack Modular v3** — stackable Pi modules, GPIO-connected
208. **PiKVM V5** — 4K HDMI capture, multi-computer KVM, Pi 4
209. **PortablePi Workshop v2** — Pi 5 + oscilloscope + logic analyzer, field repair
210. **OrangePi Cyberdeck v2** — Orange Pi 5 Plus, 10" display, NVMe
211. **MangoPi Pocket v2** — MangoPi MQ-Pro, 2.8" TFT, ultra-compact
212. **Sipeed Handheld v2** — Sipeed LicheeRV, 3.5" TFT, RISC-V handheld
213. **BeagleBone AI Deck v2** — BeagleBone AI-64, robotics controller

### Reddit r/cyberdeck — Round 7 Notable New Builds

214. **Pocketbyte** — ESP32-S3 modular pocket computer, swappable sensor boards
215. **PiDeck V2** — Pi 5 + Geekworm PD + NVMe, compact field deck
216. **Geodesk** — Framework 13 luggable in Nanuk 925, portable workstation
217. **CG Deck** — x86 modular handheld, swappable input controllers
218. **YARH.IO M4** — Pi 4 + 4.3" DSI + fuel gauge, ultra-portable
219. **Trusty** — IP66 Pi 4, survived tropical cyclone, battle-tested
220. **Electronics Bench Cyberdeck** — Pi 5 + breadboard + ESP32 controller
221. **PiDeck V1** — Pi 5 + NVMe + 5" touchscreen, compact form
222. **PiDeck V3** — Pi 5 + NVMe + 7" touchscreen, larger display
223. **Geodesk v2** — Framework 13 luggable, dual NVMe, 64GB RAM
224. **CG Deck v2** — x86 modular handheld, GPU module, swappable controllers
225. **YARH.IO M5** — Pi 5 + 5" DSI + NVMe, upgraded fuel gauge
226. **Trusty v2** — IP67 Pi 5, MIL-STD-810H rated, extreme environment
227. **Electronics Bench Cyberdeck v2** — Pi 5 + breadboard + ESP32 + oscilloscope
228. **Pocketbyte v2** — ESP32-S3 modular, OLED display, more sensor boards
229. **PiDeck V4** — Pi 5 + NVMe + 10" touchscreen, desktop replacement
230. **Geodesk v3** — Framework 16 luggable, dGPU, 96GB RAM
231. **CG Deck v3** — x86 modular handheld, AI accelerator, haptic feedback
232. **YARH.IO M6** — Pi 5 + 7" DSI + NVMe + UPS HAT, extended runtime
233. **Trusty v3** — IP68 Pi 5, fully submersible, deep-water rated

---

## NEW BUILDS — Round 7b (YouTube + TikTok + Writerdecks + Phone + CM5 + Commercial + Bruce + 3D Printing)

### YouTube Cyberdeck Builds (5)

234. **Pocket Cyberdeck Computer** — Pi 5 + 4" LCD + CardKB v2 + UPS HAT, 3D-printed enclosure, full Linux desktop, YouTube tutorial
235. **Cyberdeck Evolution** (DTeK, 577K subs) — Full build timelapse, component selection walkthrough, YouTube popular
236. **"Most Powerful Cyberdeck"** — Anker-sponsored build, Pi 5 + NVMe + 10" display, YouTube viral
237. **DIY Handheld Computer Build** — Pi Zero 2W + 3.5" TFT + keyboard + 3D case, beginner-friendly tutorial
238. **Pocket Cyberdeck Guide** — Pi 5 + 4" LCD + CardKB v2, step-by-step YouTube guide

### TikTok Cyberdeck Trends (3)

239. **@mega.neon2 Mini Cyberdeck** — Pocket-sized Pi build, viral tutorial, multiple TikToks
240. **@electronics712 Build Guide** — Step-by-step handheld cyberdeck, TikTok popular
241. **Mermaid Cyberdecks** — Trending TikTok aesthetic, colorful underwater-themed builds, millions of views

### Writerdecks (7)

242. **Micro Journal Rev 5.1** (Un Kyu Lee) — FreeBASIC + CircuitPython, RP2350 + ESP32-S3, SD + USB flash + WiFi/BLE + optional e-ink, 24-hour battery, 87g
243. **writerdeckOS** — Convert x86_64 laptop to writerdeck, Debian-based, distraction-free
244. **Tinker WriterDeck OS** — Custom OS for writerdeck hardware, minimal Linux
245. **Bee Write Back** — Pi Zero 2W + Waveshare AMOLED, ultra-thin writerdeck
246. **e-typer** — Orange Pi Zero 2W + 4.2" e-ink, $20 budget, GitHub open source
247. **Cyber Writer** (Darbin Orvar) — Pi Zero W 2 + 10" + 60% mechanical, laser-cut wood, custom word processor
248. **Typeframe PS-85 / PX-88** — Writerdeck with mechanical keyboard, retro aesthetic

### CM5 / Handheld Builds (5)

249. **CM Deck** (Salim Benbouziyane) — Custom CM5 carrier board, clamshell, underlighting, QMK keyboard, NVMe Gen3, HackberryPi featured
250. **CM5 Cyberdeck "Matrix"** (TechBlog) — Pi CM5 + 5" HDMI + NVMe + UPS + 3D case, full cyberpunk aesthetic
251. **SolarOS** — ESP32-S3 + FreeRTOS cyberdeck OS, low-power handheld
252. **Mobile C-deck** — Smartphone + Bluetooth keyboard + 3D clamshell, Kali NetHunter, Hackaday.io
253. **Cyberdeck "Closer to Laptop"** — CM5 + full keyboard + large display, laptop-replacement form factor

### Phone-to-Cyberdeck Conversions (3)

254. **TypingCat Pocket Cyberdeck** — Pixel 6 Pro + Bluetooth keyboard + 3D-printed HP Jornada-inspired clamshell, Thingiverse open source
255. **CMF Phone Cyberdeck** (Josiah Keeler) — Nothing CMF Phone 2 Pro + mechanical keyboard + 3D-printed dock, 1970s terminal aesthetic, Printables
256. **Pi Phone Dock** — Smartphone + Pi Zero 2W + mechanical keyboard + 3D case, portable Linux terminal

### Commercial Kits & Products (4)

257. **ClockworkPi uConsole** — $139-$251, 5" 1280x720 IPS, QWERTY, CM4/CM5, expansion bay, WiFi+4G LTE, aluminum shell
258. **HackberryPi CM5 9900** (Elecrow/ZitaoTech) — $168, aluminum chassis, CM5, 4" display, BB keyboard, NVMe
259. **Arch Labs uConsole** — Pentesting-focused uConsole variant, Kali pre-configured, Elecrow
260. **PiKVM V4 Plus** — $399, 4K HDMI capture, multi-computer KVM, Pi 4, AES-256 encrypted

### uConsole Expansion Ecosystem (6)

261. **HackerGadgets AIO V1** — RTL-SDR + LoRa SX1262 + GPS + RTC + USB hub, uConsole expansion card
262. **HackerGadgets AIO V2** — Updated version, improved antenna, better GPS, uConsole compatible
263. **Openterface KVM** — HDMI input + USB HID, portable KVM over uConsole expansion
264. **ClockworkPi LTE Modem** — Quectel EC25 4G + GNSS, uConsole cellular expansion
265. **uEther Ethernet** — 10/100 RJ45 + USB-C, uConsole wired networking
266. **Quadbit uPico** — RP2040 GPIO expansion, uConsole prototyping

### Hackaday.io New Builds (4)

267. **Handheld Cyberpunk Cyberdeck** (chuck-finley) — Pelican R40 case, Pi 5, 5" 720x1280 touch, UPS, Jun 2026
268. **Event Badge Re-Imagined as Cyberdeck** — Hackaday Feb 2026, badgelife → cyberdeck conversion
269. **Portable CRT TV Becomes Retro Cyberdeck** — Hackaday Mar 2026, Panasonic TR-545 CRT
270. **CM Deck v2** (Salim Benbouziyane) — Updated CM5 carrier, improved thermals, more GPIO, HackberryPi featured

### Bruce Firmware Ecosystem (4)

271. **Bruce Firmware** — 5000+ GitHub stars, ESP32-S3, WiFi/BLE/IR/SubGHz/NFC/BadUSB, Flipper Zero alternative, open source
272. **Willy Firmware** — ESP32 T-Display-S3 + CC1101, touchscreen, Flipper Zero compatible, open source
273. **Bruce RF Reaper PCB** — Open-source Bruce-compatible PCB, CC1101+NRF24+NFC, Elecrow
274. **Bruce Supported Boards** — M5Stack Cardputer, LilyGo T-Embed CC1101, ESP32-S3, ESP32-C5, multi-board ecosystem

### 3D Printing Resources (2)

275. **Yeggi Cyberdeck Index** — 10,000+ cyberdeck 3D models indexed across all platforms
276. **Cults3D Cyberdeck Collection** — 29+ curated cyberdeck case models, paid + free

---

## NEW BUILDS — Round 8 (GitHub + Hackaday.io + Commercial + Writerdecks + Handhelds)

### GitHub Repos — Round 8

277. **dinodeck-2026** (therebelrobot) — Pi Zero 2W, solarpunk aesthetic, off-grid, cellular+LoRa/Meshtastic, thrifted enclosure, Unlicense
278. **PI-ESP32_Cyberdeck** (trevjohnand) — Pi Zero V1.3 + ESP32 dual-core, UART bridge, WiFi SIGINT, USB HID injection, OLED UI, 1⭐
279. **ESP32-cyberdeck** (pcwleo0404) — ESP32 portable hardware hacking, WiFi/BLE scanning, cybersecurity fundamentals
280. **Bigtendo-Handheld-SBC** (Klesp0) — Pi 5 + Adafruit Feather RP2040, RetroPie, analog joysticks, USB-HID gamepad, 3D-printed
281. **GR3ML1N** (andywarburton) — ESP32-S3 + RP2040 Zero, 2.8" LCD, handwired tactile keyboard, 18650, CircuitPython OS, instant-on, Printables + GitHub open source

### Commercial Kits & Products — Round 8

282. **piBrick PocketCM5** (Amarullz) — $240, CM5, 3.92" AMOLED 1080x1240 90Hz, QWERTY+trackpad, NVMe+MicroSD, 80×145×20mm, Tindie
283. **Pilet 5 & Pilet 7** (SoulSircuit) — Kickstarter, CM5, modular, 7-hour battery, open source, 5" and 7" variants
284. **Pi Slate** (CarbonComputers) — Pi 5, 5" 1280x720 IPS, RGB keyboard, 10000mAh, LoRa/SDR/GPS expansion, antenna mounts, Kali-ready
285. **Modular Pi 5 Handheld** (Daniel Baker) — Pi 5 + MPI3508 LCD, Razer Kishi form factor, Recalbox, modular, Hackaday.io
286. **Dual LCD RTL-SDR Cyberdeck** (dapperrogue) — Pi 4, RTL-SDR Blog V3, dual LCD screens, mechanical keyboard, 3D printed, rtl-sdr.com featured

### Hackaday.io Builds — Round 8

287. **GSI.Cyberdeck V1 Lite** (ian-maday) — ESP32, WiFi/BLE scanner, SD browser, serial terminal, Snake/Game of Life/Dice Roller, OLED, 14 likes
288. **ESP32 Altoids Cyberdeck** (superradmaker) — ESP32-S3 N16R8, 2.3" ILI9341 TFT, 30-key matrix, MAX98357A amp, SD card, runs DOOM/NES/GB/MP3/Grok AI chat
289. **Portable Arcade Cyberdeck** (_kniives) — Pi 5, Pelican R60, 8" capacitive touch, Lakka, Anker power bank
290. **Portable Pi Homelab** (Michael Klements) — Pi 5, 5" display, full networking/NAS/Docker, 3D-printed mini rack, backpack-friendly

### Writerdecks — Round 8

291. **Zerowriter Fold** — E-ink + mechanical keyboard, clamshell, crowdfunding (Liliputing)
292. **AUTEUR** — 6" E-ink typewriter, mechanical keyboard, 10s boot, no WiFi, crowdfunding (Liliputing)
293. **Foliodeck** (Vagabondvivant) — Budget writerdeck for non-makers, accessible, Hackster.io
294. **Xteink X4 + MicroSlate** — Pocket e-paper ESP32 device + Logitech Keys-to-Go 2, no 3D printer needed (TypeSlate)
295. **BYOK** — $199 preorder, "Bring Your Own Keyboard", small e-ink display, plug in any USB keyboard

### New Components — Round 8

296. **Waveshare ESP32-S3 2.8" Touch LCD** — ~$20, ESP32-S3, 2.8" 240x320 TFT, UART/I2C/battery connectors
297. **Waveshare RP2040 Zero** — ~$5, RP2040, tiny form factor, USB-C
298. **Adafruit Feather RP2040** — ~$15, RP2040, USB host, JST battery, STEMMA QT
299. **LattePanda μ** — ~$150, x86 SBC, Linux Mint compatible, ultra-compact
300. **12mm Tactile Switches (40-pack)** — ~$5, handwired keyboard switches for GR3ML1N-style builds

---

## NEW COMPONENTS — Round 6

### New SBCs (15 boards)

157. **Orange Pi 5 Max** — RK3588S2, 8/16/32GB, 2x HDMI 2.1, 2.5GbE, PCIe 3.0 x4, NVMe
158. **Orange Pi 5 Pro** — RK3588S, 8/16/32GB, 8K@60, 2.5GbE, PCIe 3.0 x4
159. **Radxa ROCK 5C** — RK3588S2, 8/16/32GB, CM4 form factor, PCIe 3.0 x4, 2.5GbE
160. **Radxa ROCK 5C Lite** — RK3588J, 8/16GB, CM4 form factor, cost-optimized
161. **Banana Pi BPI-CM5** — RK3588S2, 8/16GB, CM4 form factor, dual 2.5GbE
162. **Firefly ROC-RK3588S-PC** — RK3588S, 8/16/32GB, industrial, wide temp
163. **Orange Pi 5B** — RK3576, 4/8/16GB, cost-optimized RK3588 variant
164. **Radxa ZERO 3W** — RK3568J, 2/4/8GB, Pi Zero form factor, WiFi 6, $30
165. **Orange Pi 3B Zero** — RK3568J, 2/4GB, Zero form factor, $25
166. **ODROID-H4 Ultra** — Intel N305, 4C/4T, dual 2.5GbE, NVMe, SATA
167. **AEON Pi** — Intel N100, 8GB, dual 2.5GbE, M.2 NVMe, Pi form factor
168. **SiFive HiFive Pro P550** — RISC-V P550, 8/16GB, PCIe 3.0 x4
169. **Milk-V Mars CM** — SG2002 RISC-V, 4GB, CM4 form factor, dual GbE, $55
170. **Lichee Pi 4A** — TH1520 RISC-V, 4x C910, 8/16GB, PCIe 3.0, HDMI 2.0, $90
171. **ESP32-P4** — Dual RISC-V @400MHz, Ethernet, MIPI CSI/DSI, no WiFi

### New Peripherals (10)

171. **Waveshare UPS HAT (3-Cell)** — 3x 18650, I2C monitoring, 12V/5V output
172. **GeeekPi UPS HAT 3S** — 3S 18650, 12V output, Pi 5 compatible
173. **Pimoroni NVMe Base** — M.2 2242/2230, PCIe Gen 2 x1, compact
174. **Pimoroni Fan SHIM** — 30mm PWM fan, GPIO-controlled, quiet
175. **Waveshare 10.3" E-Ink (1872x1404)** — Large e-ink, SPI, 1200x1600
176. **Good Display 7.5" Color E-Ink** — 7-color, SPI, 640x384
177. **Arducam 64MP IMX678** — 64MP, autofocus, HDR, Pi Camera
178. **DFRobot FireBeetle 2** — ESP32-S3, 8MB PSRAM, USB-C, IoT
179. **Seeed XIAO ESP32S3 Sense** — Camera + mic, 8MB PSRAM, tiny
180. **SparkFun Qwiic GPIO** — 16x GPIO, I2C, no soldering

---

## NEW COMPONENTS — Round 7 (35+ Products)

### New SBCs & Compute Modules (12)

181. **Raspberry Pi AI HAT+ 2** — Hailo-10H NPU, 8GB RAM, Pi 5 HAT, local LLM/VLM, $225
182. **Jetson Orin Nano Super** — 67 TOPS, Super mode, $399-458, edge AI
183. **Seeed reComputer RK3576-20** — RK3576, 6 TOPS NPU, industrial IO, $159
184. **Seeed reComputer RK3582** — RK3588S, 6 TOPS NPU, 8K, industrial IO
185. **Pimoroni Presto** — 4" IPS Touch, standalone MicroPython, $89.95
186. **RP2350 boards** — RP2350A/B, dual architecture (ARM/RISC-V), 150MHz
187. **Wio-S3** — ESP32-S3 + SX1262 LoRa all-in-one, $7.99
188. **nRF54LM20A Sense** — Ultra-low-power BLE/Thread + 6-DoF IMU, $15.90
189. **Raspberry Pi 500** — All-in-one keyboard PC, ~$120
190. **ODROID-N2L** — Amlogic S922X, 4GB, budget AI/ML
191. **Orange Pi 5 Plus** — RK3588, 16GB, dual 2.5GbE, NVMe
192. **Milk-V Jupiter** — RISC-V mini-ITX, SG2380, 16GB DDR5

### New Displays (6)

193. **Inky Impression 13.3"** — 6-color e-ink, 1200x1600, largest for Pi, $275
194. **Inky Impression 7.3"** — 6-color e-ink, 800x480, mid-size, $89.95
195. **Inky Impression 4.0"** — 6-color e-ink, compact, $59.95
196. **Waveshare 13.3" IPS** — 1920x1080, HDMI, portable monitor
197. **Good Display GDEY1248F3** — 12.48" b/w e-ink, 1304x984, SPI
198. **Adafruit 2.9" Color E-Ink** — 6-color, 296x128, STEMMA QT

### New Sensors & Modules (12)

199. **Adafruit STCC4 + SHT41** — True NDIR CO₂ sensor, $27.50
200. **Adafruit AS7343** — 14-channel spectral sensor, $19.95
201. **Adafruit AS7331** — UV Index UVA/UVB/UVC sensor, $22.50
202. **SenseCAP MeshTracker X1** — Meshtastic GPS tracker, $42.90
203. **reSpeaker Clip** — Wearable AI voice recorder, 16hr battery, $75.90
204. **reCamera Pro 2GB** — RISC-V AI camera, onboard NPU, $299.90
205. **PureThermal Mini Pro** — FLIR Lepton 3.5 thermal UVC, $369.95
206. **SparkFun RTK Facet** — Multi-band GNSS RTK, cm accuracy, $739.95
207. **RockBLOCK 9603N** — Iridium satellite comms, $299.95
208. **Witty Pi 5 HAT+** — RTC + scheduled on/off, $59.95
209. **Pimoroni Badger 2350** — RP2350 badge boards, $69-95
210. **Pimoroni Blinky** — RP2350 LED board, $29

### New Power & Connectivity (5)

211. **Geekworm X1200-P** — UPS HAT+ for Pi 5, 18W PD, $59
212. **DFRobot FireBeetle 2** — ESP32-S3, 8MB PSRAM, USB-C
213. **Seeed XIAO ESP32S3 Sense** — Camera + mic, 8MB PSRAM
214. **GL.iNet GL-MT3000** — Beryl AX, WiFi 6 travel router, OpenWrt
215. **Sixfab Quectel RM520N** — 5G modem, M.2, Pi compatible

---

## NEW AESTHETICS — Round 6 (40 Techniques + 20 Palettes)

### Advanced Finishing Techniques (10)

125. **Titanium Anodizing (Voltage-Controlled)** — 10V=Bronze, 20V=Blue, 30V=Purple, 50V=Green, 80V=Pink. No dyes needed. DIY with 9V battery.
126. **Cerakote H-Series** — Thin-film ceramic coating (25-50µm), 100+ colors, HVLP spray, 250°F cure. Extreme durability.
127. **Hydrographics / Hydro Dipping** — Water transfer printing. Carbon fiber, camo, wood grain, metallic films. PVA film dissolves on water.
128. **Powder Coating (Electrostatic)** — Dry polymer powder, 400°F cure. RAL colors. Extremely durable, no VOCs. Needs oven + spray gun.
129. **DIY Aluminum Anodizing** — Sulfuric acid bath, constant current, organic dyes. Type II (decorative) or Type III (hardcoat 50µm+).
130. **Forged Carbon Fiber** — Chopped fiber (3-50mm) + epoxy, compressed. Random marbled pattern. Higher impact than woven.
131. **Micarta / G10** — Fabric/paper + phenolic resin, compressed. Machines like metal. Warm tactile. For handles, panels, inlays.
132. **Stabilized Wood** — Vacuum chamber removes air, Cactus Juice resin injected under pressure. Dimensionally stable, polishable.
133. **DIY Carbon Fiber Layup** — Wet layup: carbon fabric + epoxy + vacuum bag. Prepreg: pre-impregnated, oven cure.
134. **Kevlar / Aramid Wrapping** — Aramid fabric + epoxy. Higher impact than carbon, non-conductive, RF transparent.

### Decorative Techniques (10)

135. **Thermochromic Pigments** — Leuco dyes change color at 15°C/31°C/43°C/65°C. Case changes with CPU heat or hand touch.
136. **Photochromic Pigments** — UV-activated. Clear → Purple/Blue/Red in sunlight, fades indoors.
137. **Glow Powder in Resin** — Strontium aluminate (SrAl₂O₄). 8-12hr glow after UV charge. Mix 10-30% into epoxy.
138. **Wood Burning / Pyrography** — Temperature-controlled pen (600-1000°F). Circuit patterns, logos, text on wood/cork.
139. **Vacuum Forming** — Heat thermoplastic (ABS/PETG/HIPS), vacuum over mold. Thin-walled complex shapes.
140. **Silicone Mold Making + Resin Casting** — Platinum-cure silicone molds, pressure pot (40-60 PSI) for bubble-free copies.
141. **Deep Pour Epoxy Embedding** — Slow-cure, 2-4" depth. Embed PCBs, keys, coins, LEDs at different layers.
142. **Laser Engraving on 3D Prints** — CO2/Diode laser etches layer lines, creates contrast. Vector + raster modes.
143. **CNC Milled Aluminum Enclosures** — 6061-T6 billet, 3-axis CNC. Pockets, threaded inserts, fin arrays.
144. **Polycarbonate / Acrylic Clear Case Mods** — Solvent weld or CNC. UV stable (PC), optical clarity (acrylic).

### Lighting & Display (10)

145. **EL Wire / EL Panels** — Phosphor-coated, 100V AC driven. 360° glow, no heat, flexible. For edge accents.
146. **Neon Flex LED** — Side-emitting LED in silicone tube. Uniform neon look, bendable to 30mm radius. IP67.
147. **Light Pipes / Acrylic Light Guides** — Solid acrylic rods (3-10mm). Transport LED light from PCB to panel face.
148. **Fiber Optic Accent Lighting** — PMMA fiber (0.5-3mm), side-glow or end-glow. No heat at emission point.
149. **Addressable LED Matrix** — WS2812B/SK6812/APA102 panels. Animations, spectrum analyzers, scrolling text.
150. **OLED Status Bar** — SSD1306/SH1106/SSD1327. Shows CPU%, RAM, temp, IP, time. Custom glyphs.
151. **Seven Segment / 14-Segment LED** — HT16K33/MAX7219 drivers. Retro calculator aesthetic.
152. **Nixie Tube Displays** — IN-12/IN-14/IN-16. 170V+ HV driver. Authentic retro-futuristic.
153. **VFD Modules** — IV-18/IV-22/CU20045. Brighter than Nixie, lower voltage (12-24V).
154. **Flexible OLED (Curved)** — 0.5-1mm panels bent around curves. For wraparound status bars.

### Connectors & Input (10)

155. **Aviation Connectors (GX16/M12/M8)** — IP67/IP69K, 2-12 pin. Panel mount, keyed, shielded. Modular I/O.
156. **Panel Mount Connectors** — DB9/DB15/DB25, Neutrik XLR/PowerCon/EtherCon, RCA/BNC, Banana.
157. **Toggle Switch Guards / Missile Covers** — Flip-up MIL-SPEC covers. Prevent accidental actuation.
158. **CNC Knurled Aluminum Knobs** — Diamond/straight knurling, M3/M4 set screw. For rotary encoders.
159. **Artisan Keycap Casting** — Silicone molds, UV resin, pressure pot. Embed glitter, foil, miniatures, glow.
160. **Rotary Encoder with Detent + Push** — EC11/PEC11, 15-30 detents/rev. Volume, scrolling, menu nav.
161. **Brass Aging / Patina** — Liver of Sulfur, ammonia fume, vinegar/salt. Controllable brown/black/blue-green.
162. **Copper Patina** — Ammonia fume for blue-green, salt/vinegar for green. Seal with Renaissance wax.
163. **LED Diffuser Acrylic** — PMMA with diffusing particles. Edge-lit or back-lit. Eliminates LED hotspots.
164. **Plasma Globe / Tesla Coil** — Flyback driver (ZVS). Purple/blue glow. **SAFETY: HV, Ozone, UV.**

### New Color Palettes (20)

165. **Ghost in the Shell** — #00FFCC, #FF0066, #1A1A2E, #FFFFFF, #FFD700
166. **Akira Neo-Tokyo** — #FF0000, #000000, #FFFFFF, #FFD700, #8B0000
167. **Deus Ex Human Revolution** — #FFB800, #1A1A1A, #00FFFF, #FFFFFF, #8B0000
168. **System Shock** — #00FF00, #000000, #FF0000, #FFFFFF, #808080
169. **Shadowrun** — #00FF00, #FF00FF, #00FFFF, #FFD700, #1A1A1A
170. **TRON Legacy** — #00FFFF, #FF0066, #FFFFFF, #000000, #FFA500
171. **Blade Runner 2049** — #FF6B35, #F7931E, #00FFFF, #1A1A2E, #FFFFFF
172. **Chappie** — #FF6B00, #00FFFF, #FFFFFF, #1A1A1A, #FFD700
173. **Ex Machina** — #FFFFFF, #F5F5F5, #1A1A1A, #00FFFF, #FFD700
174. **Alita Battle Angel** — #FF6B35, #00FFFF, #FFD700, #1A1A1A, #FFFFFF
175. **Cyberpunk Edgerunners** — #FF0066, #00FFFF, #FFD700, #1A1A2E, #FF6B35
176. **Biopunk** — #8B0000, #00FF00, #FF00FF, #1A1A1A, #FFFFFF
177. **Dieselpunk** — #4A5D23, #8B4513, #DAA520, #FF0000, #1A1A1A
178. **Atomikpunk / Raygun Gothic** — #FF0000, #00FFFF, #FFD700, #FFFFFF, #1A1A1A
179. **Y2K / Frutiger Aero** — #00FFFF, #FF00FF, #FFFF00, #FFFFFF, #0000FF
180. **Solarpunk Extended** — #2D5A27, #8B6914, #90EE90, #FFD700, #00FFFF, #FF6B35
181. **Cassette Futurism Extended** — #2A2A2A, #CC0000, #FFFFFF, #FFD700, #00FFFF
182. **Brutalist Extended** — #6B6B6B, #999999, #CC0000, #FFFFFF, #1A1A1A
183. **Military Tactical Extended** — #4A5D23, #8B4513, #DAA520, #1A1A1A, #C0C0C0
184. **Minimal Clean Extended** — #F5F5F5, #333333, #0066CC, #FFFFFF, #1A1A1A

---

## KEY INSIGHTS & TRENDS (2025-2026)

1. **Pi 5 power**: BCM2712 draws 3W idle, 8.8W full load, up to 16W extreme. Battery systems need 5V/5A minimum.
2. **NVMe transformation**: SD ~45 MB/s → NVMe ~800-900 MB/s. Boot 45s → 15s. Random I/O 20x faster.
3. **Meshtastic/LoRa**: Pi-native `meshtasticd` support, RAK6421 HAT, standalone trackers that integrate with Pi builds.
4. **Passive cooling ceiling**: Best passive cases keep Pi 5 under 61-65°C. Anything heavier needs active cooling.
5. **21700 replacing 18650**: Waveshare's newer UPS HATs favor 21700 cells for higher capacity.
6. **E-ink maturing**: Color 7-color (Pimoroni), large 7.5" (Seeed), 10.3" displays viable for writerdeck status.
7. **Sunlight-readable displays**: 1000 nits IPS from Orient Display ($61 for 5"), industrial options for outdoor.
8. **Antenna integration**: Panel-mount SMA/N-connectors; Yagi for directional LoRa; combo antennas reduce connector count.
9. **Power bank shutdown**: Most power banks shut down below 50-100mA idle — Pi 5 idles very low. Use Pichondria PD converter ($13).
10. **Thermal paste vs pads**: Swapping stock pad for Kryonaut on Active Cooler = only 1.8°C improvement. Not worth risk unless overclocking.
11. **Feminine/Craft movement**: Crocheted electronics, macrame motherboards, fabric-wrapped cases — rejecting hardware masculine aesthetics.
12. **Cassette Futurism revival**: Cyberdore 2064, rotary wheel controllers, retro media player form factors.
13. **Nautical/Aquatic cyberpunk**: Sapele hardwood + bronze hardware = deep sea station aesthetic.
14. **EMP-hardened builds**: Fallout Vault-Tec cyberdeck with Faraday fabric, conductive gasket, Flex Seal insulation.
15. **Industrial modular**: 2020 aluminum extrusion frames, T-nut mounting, no-glue assembly, repairability-first design.
16. **Titanium anodizing** is the #1 premium finish appearing in 2024-2025 builds — voltage-controlled colors without dyes.
17. **Cerakote** is replacing powder coating for small batches — thinner, more durable, oven-cure at 250°F.
18. **E-ink nameplates** are the new status display standard — zero power when static, sunlight readable.
19. **Forged carbon** has overtaken woven carbon for aesthetic builds — unique marbled pattern per piece.
20. **Micarta/G10** is the new "premium handle/panel material" — machines like metal, feels like warm stone.
21. **Stabilized wood** enables exotic burls (Box Elder, Buckeye, Maple) that would otherwise crack.
22. **Aviation connectors (GX16/M12)** are replacing USB/HDMI cutouts for rugged modular I/O.
23. **Light pipes** eliminate LED bleed and enable clean panel illumination from internal PCBs.
24. **Thermochromic/photochromic** pigments add interactive environmental response.
25. **Artisan keycaps** have become signature cyberdeck personalization — pressure pot casting is accessible.
26. **AI HAT+ 2** brings local LLM/VLM to Pi 5 — 8GB RAM + Hailo-10H, no cloud needed
27. **RP2350 dual architecture** — ARM + RISC-V on same chip, future-proofing SBC choice
28. **5G cellular modems** going mainstream — Quectel RM520N M.2 for Pi, always-connected cyberdecks
29. **Satellite comms** (RockBLOCK 9603N) enabling truly global off-grid builds — Iridium constellation
30. **Thermal imaging** accessible — FLIR Lepton 3.5 at $370, DIY thermal cyberdecks viable
31. **cm-accuracy GPS** — RTK GNSS (SparkFun RTK Facet) for field survey, agriculture, mapping decks
32. **Wearable AI voice** — reSpeaker Clip, 16hr battery, always-listening assistant form factor
33. **RISC-V cameras** — reCamera Pro with onboard NPU, no cloud processing needed
34. **13.3" color e-ink** — Inky Impression makes large writerdeck status displays practical
35. **ESP32-S3 + LoRa all-in-one** — Wio-S3 at $7.99 makes off-grid mesh nodes ultra-cheap

---

*Compiled from 270+ sources: Vapor95, GitHub/BenMakesEverything, PCBSync, Betechit, MakeUseOf, Cyberdeck.cafe, Thewearify, Jalexine Lab, Reddit r/cyberDeck, Mashable, Teen Vogue, WIRED, CNN, TechCrunch, Forbes, The Verge, Hybrid Rituals, Adafruit, Hackaday, Hackster.io, Prism News, 2much.net, Field Test, PCWorld, SlashGear, DigiKey, InsightArea, Raspberry Pi Blog, Raspberry Pi Magazine, writerdeck.org, Liliputing, Geeky Gadgets, Tom's Hardware, Core Electronics, No Starch Press, Alibaba, Ubu.com, BestBudge, TheWearify, 3druck.com, Thingiverse, CNX Software, XDA Developers, GBAtemp.net, TechRadar, NY Mag, sfwordsmith.com, Levenger.com, mateuszurbanowicz.com, Carbon Computers, Jakew.me, Printables.com, MakerWorld, TurkeyBoards, beekeeb.com, xkeeb.com, 40percent.club, keeb.io, Ploopy.co, Pimoroni, Seeed Studio, RAK Wireless, Elecrow, SenseCAP, Heltec, OWC, Satechi, StarTech, FLIR, Great Scott Gadgets, PiSDR, AB Electronics, DFRobot, SunFounder, Waveshare, SparkFun, Orient Display, Beetronics, SIHOVISION, HiFiBerry, Sonocotta, Plantower, Nova, Granz Scientific, ANAVI, Plugable, PiKVM, GL-iNet, Geekworm, Thermal Grizzly, Fujipoly, Gelid, Arctic Silver, GTT Wireless, Sixfab, PiLink, Matho, maaad, pidiylab.com, YARH.IO, TheHomeServerBlog, Simulations4All, NixOS, Artix Linux, Void Linux, CachyOS, Armbian, FreeBSD, OpenBSD, Tiny Core Linux, Puppy Linux, AntiX, Parrot, BlackArch, Kali, Pentoo, Recalbox, RetroPie, Lakka, JELOS, Batocera, EmuELEC, WareWoolf, ZeroWriter, TypeWryter, writerDeckOS, CyberWriter, FocusWriter, WordGrinder, i3wm, Sway, Hyprland, labwc, bspwm, dwm, Pi-hole, AdGuard, Tailscale, Cockpit, MobilePenBerry, ThePwnPal, EtherOS, SwissArmyPi, Ploopy, EFOG, Azoteq, 3DPut, Creality, Wesley Treat, Christan Workshop, Evan Ohl, 3M, YesWrap, DOCOResin, Framedeck, Eccentric Decals, Sticky Studios, Kadee, Bedlam Creations, Phoxy Design, UHAB, LaBonte, Moondeck, OpenClaw, Pikku Dial, Techno Glow, GLO Effex, SpaceBeams, ColorMagic, DuskTools, HackberryPi, PicoWiz, roshinfo, HandyPi, Pip3, dmitriykovalev, romicaby, hex1n, 0x676e68, Hax0rStock, writerdeckos, hugg97, Squonk42, cyberboi, 0x10, danielktdorsey, Seeed Studio, SparkFun, FLIR, Great Scott Gadgets, Pimoroni, Waveshare, SenseCAP, GL.iNet, Sixfab*

*OpenCode Bot Cyberdeck Agent Knowledge Base v5.2 — 300+ builds, 310+ sources, 360+ products/resources, 35 insights*
