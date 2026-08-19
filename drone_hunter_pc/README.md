# 🛸 Drone Hunter 2D — PC Edition (Phase 8)

**Drone Hunter 2D** is a high-performance industrial sci-fi tactical top-down drone combat game developed with Python and `pygame-ce`.

Fight through **5 distinct industrial sectors**, complete **25 combat missions**, engage **5 sector bosses** with multi-phase attack patterns, upgrade your drone in the Hangar, and defeat the **Drone Overlord** in the final endgame confrontation.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (tested on 3.10 / 3.11 / 3.12 / 3.13 / 3.14)
- `pip install -r requirements.txt`  (installs `pygame-ce>=2.5.0` and `pytest>=7.0.0`)

### 2. Launch the Game
From the project root:
```bash
python drone_hunter_pc/main.py
```
Or from inside `drone_hunter_pc/`:
```bash
python main.py
```

### 3. Run All Automated Tests (314 tests)
```bash
pytest drone_hunter_pc/tests
```

---

## 🕹️ Controls Reference

| Action | Primary Input | Alternate |
|:---|:---|:---|
| **Movement / Thrust** | `W`, `A`, `S`, `D` | Arrow Keys |
| **Aim** | Mouse Pointer | *(screen-mapped crosshair)* |
| **Primary Fire** | `Left Mouse Button` | — |
| **Weapon Selection** | `1` to `6` | `TAB` / Mouse Wheel |
| **EMP Blast** | `E` | `Right Mouse Button` |
| **Overdrive Mode** | `F` | `Q` / Middle Mouse |
| **Evasive Barrel Roll** | `Left Shift` | `Right Shift` |
| **Tactical Cloak** | `K` | — |
| **Cycle Drone Skin** | `C` | Hangar customizer |
| **Pause / Resume** | `ESC` | `P` |
| **Fullscreen Toggle** | `F11` | — |
| **Sector Map** | `M` | Menu button |
| **Hangar Bay** | `H` | Menu button |

---

## 🌌 Campaign — 5 Sectors × 5 Missions

| Sector | Name | Theme | Boss |
|---|---|---|---|
| 1 | **CYBER FACTORY** | Industrial drone production plant | Assembly Warden |
| 2 | **CORE SECTOR** | Heavily defended reactor core complex | Core Executor |
| 3 | **REACTOR ZONE** | Volatile energy conduits & plasma machinery | Reactor Titan |
| 4 | **DEFENSE GRID** | Fortified automated defense installations | Defense Commander |
| 5 | **DRONE COMMAND** | Enemy command infrastructure | Drone Overlord |

### Mission Roster (25 missions)

| ID | Name | Sector | Diff | Objective | Waves |
|---|---|---|---|---|---|
| S1_M1 | Perimeter Sweep | Cyber Factory | 1 | Destroy All | 2 |
| S1_M2 | Factory Approach | Cyber Factory | 1 | Destroy All | 3 |
| S1_M3 | Security Breach | Cyber Factory | 2 | Complete Encounters | 3 |
| S1_M4 | Production Line | Cyber Factory | 2 | Complete Encounters | 3 |
| S1_M5 | Perimeter Collapse | Cyber Factory | 3 | Complete Encounters | 3 |
| S2_M1 | Core Entry | Core Sector | 2 | Destroy All | 3 |
| S2_M2 | Assembly Lines | Core Sector | 2 | Complete Encounters | 3 |
| S2_M3 | Reactor Access | Core Sector | 3 | Complete Encounters | 3 |
| S2_M4 | Security Grid | Core Sector | 3 | **Survive 45 s** | 3 |
| S2_M5 | Core Breach | Core Sector | 4 | Complete Encounters | 3 |
| S3_M1 | Reactor Approach | Reactor Zone | 3 | Complete Encounters | 3 |
| S3_M2 | Cooling Network | Reactor Zone | 3 | **Survive 75 s** | 3 |
| S3_M3 | Power Junction | Reactor Zone | 4 | Complete Encounters | 4 |
| S3_M4 | Reactor Defense | Reactor Zone | 4 | Complete Encounters | 3 |
| S3_M5 | Critical Overload | Reactor Zone | 5 | Complete Encounters | 3 |
| S4_M1 | Outer Defense | Defense Grid | 4 | Complete Encounters | 3 |
| S4_M2 | Interceptor Grid | Defense Grid | 4 | **Survive 75 s** | 3 |
| S4_M3 | Defense Network | Defense Grid | 4 | Complete Encounters | 4 |
| S4_M4 | Central Firewall | Defense Grid | 5 | Complete Encounters | 3 |
| S4_M5 | Defense Collapse | Defense Grid | 5 | Complete Encounters | 3 |
| S5_M1 | Command Perimeter | Drone Command | 4 | Complete Encounters | 4 |
| S5_M2 | Tactical Network | Drone Command | 5 | **Survive 90 s** | 3 |
| S5_M3 | Command Core | Drone Command | 5 | Complete Encounters | 4 |
| S5_M4 | Final Defense | Drone Command | 5 | Complete Encounters | 4 |
| S5_M5 | Drone Command | Drone Command | 5 | Complete Encounters | 4 |

### Wave Compositions

| Constant | Composition | Enemies |
|---|---|---|
| `WAVE_SCOUTS_PATROL` | 3× Scout | 3 |
| `WAVE_SCOUTS_ASSAULT` | 4× Scout | 4 |
| `WAVE_SCOUTS_SWARM` | 5× Scout | 5 |
| `WAVE_SHOOTERS_PAIR` | Shooter–Scout–Shooter | 3 |
| `WAVE_SHOOTERS_SQUAD` | Scout–Shooter–Scout–Shooter–Scout | 5 |
| `WAVE_HEAVY_ESCORT` | Scout–Heavy–Scout–Shooter | 4 |
| `WAVE_HEAVY_BATTLEGROUP` | Scout–Heavy–Shooter–Heavy–Scout | 5 |
| `WAVE_SHIELD_VANGUARD` | Scout–Shield–Shooter–Scout | 4 |
| `WAVE_ELITE_STRIKE_FORCE` | Shield–Heavy–Shooter–Shooter–Scout | 5 |

---

## 🛠️ Drone Upgrades & Hangar

Earn **Scrap** from defeated enemies and mission rewards:

| Upgrade | Effect | Max Lv |
|---|---|---|
| 🔋 Battery Capacity | +20 max HP per level | 5 |
| 🚀 Thruster Agility | +15% speed per level | 5 |
| ⚡ Fire-Rate Overclock | −12% weapon cooldown per level | 5 |
| 💥 EMP Quick-Charger | −2.5 s EMP recharge per level | 4 |
| 🛸 Wingman Escort Drone | Autonomous escort minidrone | 3 |
| 👻 Tactical Cloak Unit | Unlocks `K` cloak ability | 3 |
| 🚀 Homing Missiles | Unlocks missile weapon | 3 |
| ⚡ Plasma Laser Beam | Unlocks beam weapon | 3 |
| 🌩️ Arc Lightning Tesla | Unlocks tesla weapon | 3 |
| 💣 Cluster Torpedo | Unlocks cluster weapon | 3 |
| ⚡ Overdrive Reactor | Enhances overdrive duration & recharge | 3 |

### Drone Skins (`C` key to cycle)
`PLATINUM VANGUARD` · `CYBERNEON PHANTOM` · `SOVEREIGN GOLD` · `CRIMSON WIDOW` · `VOID STEALTH` · `SOLAR FLARE`

---

## 🎮 Difficulty Modes

| Mode | Enemy HP | Enemy Speed | Enemy Damage | Score |
|---|---|---|---|---|
| EASY | ×0.75 | ×0.80 | ×0.70 | ×0.80 |
| NORMAL | ×1.00 | ×1.00 | ×1.00 | ×1.00 |
| HARD | ×1.35 | ×1.20 | ×1.30 | ×1.40 |
| NIGHTMARE | ×1.75 | ×1.40 | ×1.60 | ×2.00 |

---

## 🎨 Phase 8 Visual Overhaul

All entities now render from **54 production PNG sprites** with clean alpha transparency:

| Asset Group | Files | States |
|---|---|---|
| Player | `player/` — 13 state PNGs + 4 chassis variants | idle, move, bank_l/r, fire, hit, damaged, destroy, destroyed |
| Scout | `enemies/scout/` — 5 PNGs | base, idle, move, attack, hit |
| Shooter | `enemies/shooter/` — 5 PNGs | base, idle, move, attack, hit |
| Heavy | `enemies/heavy/` — 5 PNGs | base, idle, move, attack, hit |
| Shield Elite | `enemies/shield_elite/` — 4 PNGs | base, idle, move, hit |
| Bosses | `bosses/` — 5 PNGs | assembly_warden, core_executor, reactor_titan, defense_commander, drone_overlord |
| Projectiles | `projectiles/` — 4 PNGs | bullet_pulse, bullet_scatter, enemy_bullet, missile |
| Shadows | `shadows/` — 6 PNGs | player, scout, shooter, heavy, shield, boss (unrotated) |
| VFX | `vfx/` — 1 PNG | engine_flame |

**SpriteManager pipeline:** all sprites loaded once at startup → 2-degree quantized rotation cache → no per-frame Surface allocations → Layer 1 shadow / Layer 2 entity / Layer 3 VFX rendering.

---

## 🧪 Automated Tests — 314 Passing

```bash
pytest drone_hunter_pc/tests        # Run all 314 tests
pytest drone_hunter_pc/tests -v     # Verbose per-test output
```

| File | Area | Tests |
|---|---|---|
| `test_game_systems` | Core loop, context, state machine | ~20 |
| `test_phase1_flight` | Player physics, acceleration, roll | ~18 |
| `test_phase2a_scout` | Scout AI: strafe, dive, recover | ~25 |
| `test_phase2b_shooter` | Shooter: telegraph, fire, reposition | ~22 |
| `test_phase2c_heavy` | Heavy: armour, pressure AI | ~20 |
| `test_phase2d_encounters` | Wave lifecycle, spawn sequencing | ~18 |
| `test_phase2e_combat_director` | Multi-wave relief, sequencing | ~8 |
| `test_phase3_weapons` | 6 weapon classes, projectile lifecycle | ~14 |
| `test_phase4_progression` | Scrap rewards, upgrade costs | ~12 |
| `test_phase5_missions` | Mission state machine, survive timer | ~14 |
| `test_phase5_performance` | Sprite caching, projectile bounds | ~16 |
| `test_phase6_bosses` | 5 bosses × phase transitions | ~35 |
| `test_phase7_release` | Save/load, fullscreen, resolution | ~22 |
| `test_phase8_assets` | 54 sprites × 3 assertions each | ~186 |
| `test_phase8_missions_hardening` | 5-sector structure + 9 wave types lifecycle | ~128 |
| `test_runtime_smoke` | Headless game loop — no crash | ~6 |

---

## 💾 Save & Progression Architecture

- Saved atomically to `save_data_pc.json` after every mission completion and upgrade purchase.
- Persisted state: scrap balance, upgrade levels (per stat), unlocked sectors & missions, completed missions, defeated bosses, active difficulty, campaign victory flag.
- Schema-safe: missing/corrupt keys fall back to defaults — absent or damaged save files never crash the game.

---

## 📦 Building a Standalone Executable (Windows)

```bash
pip install pyinstaller
pyinstaller DroneHunter.spec
# Output: dist/DroneHunter/DroneHunter.exe
```

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 / Linux / macOS | Windows 11 |
| Python | 3.10+ | 3.12+ |
| Resolution | 1280×720 | 1920×1080 |
| Audio | Any stereo device (auto fail-safe if absent) | — |


**Drone Hunter 2D** is a fast-paced, high-performance tactical sci-fi 2D top-down drone combat game developed with Python and `pygame-ce`.

Fight through 5 distinct industrial sectors, complete 25 combat missions, engage 5 major command bosses with multi-phase attack patterns, upgrade your combat drone in the Hangar, and conquer the Drone Overlord in the final endgame confrontation.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13, 3.14)
- `pip install -r requirements.txt` (or `pip install pygame-ce pytest`)

### 2. Launch the Game
From the project root:
```bash
python drone_hunter_pc/main.py
```
Or from inside `drone_hunter_pc/`:
```bash
python main.py
```

### 3. Run Automated Tests
```bash
pytest drone_hunter_pc/tests
```

---

## 🕹️ Controls Reference

| Action | Primary Input | Secondary / Alternate |
| :--- | :--- | :--- |
| **Movement / Thrust** | `W`, `A`, `S`, `D` | `Arrow Keys` |
| **Aim** | `Mouse Pointer` | *(Screen-mapped crosshair)* |
| **Primary Fire** | `Left Mouse Button` | — |
| **Weapon Selection** | `1` to `6` | `TAB` / `Mouse Wheel` |
| **EMP Blast** | `E` | `Right Mouse Button` |
| **Overdrive Mode** | `F` | `Q` / `Middle Mouse Button` |
| **Evasive Barrel Roll** | `Left Shift` | `Right Shift` |
| **Tactical Cloak** | `K` | — |
| **Cycle Drone Skin** | `C` | *(Hangar Customizer)* |
| **Pause / Resume** | `ESC` | `P` / `SPACE` (in paused state) |
| **Fullscreen Toggle** | `F11` | — |
| **Sector Map** | `M` | *(Menu button)* |
| **Hangar Bay** | `H` | *(Menu button)* |
| **Quick Quit** | `Q` | *(Menu button)* |

---

## 🌌 Campaign & Mission Structure

The campaign spans **5 Sectors** and **25 Combat Missions**:

1. **Sector 1 — Assembly Perimeter** (Missions `S1_M1` to `S1_M5`)  
   *Boss: Assembly Warden*
2. **Sector 2 — Industrial Core** (Missions `S2_M1` to `S2_M5`)  
   *Boss: Core Executor*
3. **Sector 3 — Reactor District** (Missions `S3_M1` to `S3_M5`)  
   *Boss: Reactor Titan*
4. **Sector 4 — Defense Matrix** (Missions `S4_M1` to `S4_M5`)  
   *Boss: Defense Commander*
5. **Sector 5 — Command Citadel** (Missions `S5_M1` to `S5_M5`)  
   *Final Boss: Drone Overlord (4-Phase Endgame Encounter)*

### Mission Types:
- **Elimination**: Clear all hostile drone waves within the arena.
- **Survive**: Endure relentless enemy swarms for the required duration.
- **Target Priority**: Eliminate specific high-value enemy targets.
- **Data Recovery**: Collect operational scrap caches under active fire.
- **Boss Assassination**: Defeat the sector command unit.

---

## 🛠️ Drone Upgrades & Hangar

Earn **Scrap** from destroyed enemies and mission rewards to upgrade 4 core subsystems in the Hangar:
- **Hull Integrity**: Increases maximum drone HP.
- **Energy Core**: Increases maximum energy capacity for special abilities.
- **Weapon System**: Increases projectile damage across all weapon classes.
- **Mobility Thrusters**: Increases flight velocity and acceleration responsiveness.

---

## 💾 Save & Progression Architecture

- Progress is saved atomically to `save_data_pc.json` in the application directory.
- Upgrades, Scrap, unlocked sectors, mission clears, defeated bosses, and campaign victory states persist across sessions.
- Safe default fallbacks prevent data corruption or crashes if save files are modified or absent.

---

## 📦 Building Standalone Executable (Windows)

To build a standalone Windows `.exe` using PyInstaller:
```bash
pip install pyinstaller
pyinstaller --noconsole --name "DroneHunter" --add-data "drone_hunter_pc/assets;assets" drone_hunter_pc/main.py
```
The resulting executable will be located in `dist/DroneHunter/`.

---

## 📜 System Requirements

- **OS**: Windows 10/11 (or Linux / macOS with Python 3.10+)
- **Resolution**: 1280x720 (minimum), supports arbitrary window resizing and 1080p/1440p/4K fullscreen scaling.
- **Audio**: Any standard stereo output device (game features automatic fail-safe fallback if no audio device is found).
