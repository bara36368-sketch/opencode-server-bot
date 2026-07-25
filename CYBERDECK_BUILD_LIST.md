# Cyberdeck Build List — Complete Knowledge Base
## Compiled from 9 Sources | July 2026
### Sources: Vapor95, GitHub/BenMakesEverything, PCBSync, Betechit, MakeUseOf, Cyberdeck.cafe, Thewearify, Jalexine Lab, Reddit r/cyberDeck

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

**Key Trend:** Young women driving cyberdeck movement on TikTok — turning purses, caboodles, and vintage cases into fully functional computers. WIRED called cyberdecks "the hottest anti-AI gadget" (Apr 2026). CNN covered the rise (Apr 2026). TechCrunch featured the movement (Jun 2026).

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
1. **Anti-AI movement**: Cyberdecks positioned as rejection of big tech surveillance — WIRED, CNN, TechCrunch coverage
2. **Female makers driving movement**: TikTok women turning purses and vintage cases into viral builds
3. **NVMe is standard**: Pi 5 PCIe lane + NVMe HAT = proper SSD speed, no more SD card bottleneck
4. **LoRa/Meshtastic**: Off-grid mesh networking is a major trend (dinodeck, therustyrobot)
5. **Modular design**: NATO rails, swappable modules, upgrade-friendly enclosures
6. **Commercial kits emerging**: ClockworkPi uConsole as off-the-shelf option
7. **RK3588 as Pi alternative**: 8K, 6 TOPS NPU, multiple M.2 — serious Pi 5 alternative for AI builds
8. **Vintage shell conversions**: Amstrad, BlackBerry, Motorola police terminals — retro shells with modern guts
9. **Open-source everything**: STL files, firmware, schematics all on GitHub — community collaboration
10. **Writerdecks mature**: Micro Journal series (4 gens), Penkesu, Chonky Palmtop — refined single-purpose machines

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

---

*Compiled from 15+ sources: Vapor95, GitHub/BenMakesEverything, PCBSync, Betechit, MakeUseOf, Cyberdeck.cafe, Thewearify, Jalexine Lab, Reddit r/cyberDeck, Hackaday, TikTok (@ubeboobey, @alexinexxx, @metamerd, @carternosko), SlashGear, Geeky Gadgets, Webman.tech, InsightArea, Raspberry Pi Blog, HowToGeek — July 2026*
*OpenCode Bot Cyberdeck Agent Knowledge Base v2.0*
