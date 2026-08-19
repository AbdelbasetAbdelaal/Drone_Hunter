# ðŸ›¸ Drone Hunter 2D â€” PC Edition (Phase 8)

**Drone Hunter 2D** is a high-performance industrial sci-fi tactical top-down drone combat game developed with Python and `pygame-ce`.

Fight through **5 distinct industrial sectors**, complete **25 combat missions**, engage **5 sector bosses** with multi-phase attack patterns, upgrade your drone in the Hangar, and defeat the **Drone Overlord** in the final endgame confrontation.

---

## ðŸš€ Quick Start

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

## ðŸ•¹ï¸ Controls Reference

| Action | Primary Input | Alternate |
|:---|:---|:---|
| **Movement / Thrust** | `W`, `A`, `S`, `D` | Arrow Keys |
| **Aim** | Mouse Pointer | *(screen-mapped crosshair)* |
| **Primary Fire** | `Left Mouse Button` | â€” |
| **Weapon Selection** | `1` to `6` | `TAB` / Mouse Wheel |
| **EMP Blast** | `E` | `Right Mouse Button` |
| **Overdrive Mode** | `F` | `Q` / Middle Mouse |
| **Evasive Barrel Roll** | `Left Shift` | `Right Shift` |
| **Tactical Cloak** | `K` | â€” |
| **Cycle Drone Skin** | `C` | Hangar customizer |
| **Pause / Resume** | `ESC` | `P` |
| **Fullscreen Toggle** | `F11` | â€” |
| **Sector Map** | `M` | Menu button |
| **Hangar Bay** | `H` | Menu button |

---

## ðŸŒŒ Campaign â€” 5 Sectors Ã— 5 Missions

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
| `WAVE_SCOUTS_PATROL` | 3Ã— Scout | 3 |
| `WAVE_SCOUTS_ASSAULT` | 4Ã— Scout | 4 |
| `WAVE_SCOUTS_SWARM` | 5Ã— Scout | 5 |
| `WAVE_SHOOTERS_PAIR` | Shooterâ€“Scoutâ€“Shooter | 3 |
| `WAVE_SHOOTERS_SQUAD` | Scoutâ€“Shooterâ€“Scoutâ€“Shooterâ€“Scout | 5 |
| `WAVE_HEAVY_ESCORT` | Scoutâ€“Heavyâ€“Scoutâ€“Shooter | 4 |
| `WAVE_HEAVY_BATTLEGROUP` | Scoutâ€“Heavyâ€“Shooterâ€“Heavyâ€“Scout | 5 |
| `WAVE_SHIELD_VANGUARD` | Scoutâ€“Shieldâ€“Shooterâ€“Scout | 4 |
| `WAVE_ELITE_STRIKE_FORCE` | Shieldâ€“Heavyâ€“Shooterâ€“Shooterâ€“Scout | 5 |

---

## ðŸ› ï¸ Drone Upgrades & Hangar

Earn **Scrap** from defeated enemies and mission rewards:

| Upgrade | Effect | Max Lv |
|---|---|---|
| ðŸ”‹ Battery Capacity | +20 max HP per level | 5 |
| ðŸš€ Thruster Agility | +15% speed per level | 5 |
| âš¡ Fire-Rate Overclock | âˆ’12% weapon cooldown per level | 5 |
| ðŸ’¥ EMP Quick-Charger | âˆ’2.5 s EMP recharge per level | 4 |
| ðŸ›¸ Wingman Escort Drone | Autonomous escort minidrone | 3 |
| ðŸ‘» Tactical Cloak Unit | Unlocks `K` cloak ability | 3 |
| ðŸš€ Homing Missiles | Unlocks missile weapon | 3 |
| âš¡ Plasma Laser Beam | Unlocks beam weapon | 3 |
| ðŸŒ©ï¸ Arc Lightning Tesla | Unlocks tesla weapon | 3 |
| ðŸ’£ Cluster Torpedo | Unlocks cluster weapon | 3 |
| âš¡ Overdrive Reactor | Enhances overdrive duration & recharge | 3 |

### Drone Skins (`C` key to cycle)
`PLATINUM VANGUARD` Â· `CYBERNEON PHANTOM` Â· `SOVEREIGN GOLD` Â· `CRIMSON WIDOW` Â· `VOID STEALTH` Â· `SOLAR FLARE`

---

## ðŸŽ® Difficulty Modes

| Mode | Enemy HP | Enemy Speed | Enemy Damage | Score |
|---|---|---|---|---|
| EASY | Ã—0.75 | Ã—0.80 | Ã—0.70 | Ã—0.80 |
| NORMAL | Ã—1.00 | Ã—1.00 | Ã—1.00 | Ã—1.00 |
| HARD | Ã—1.35 | Ã—1.20 | Ã—1.30 | Ã—1.40 |
| NIGHTMARE | Ã—1.75 | Ã—1.40 | Ã—1.60 | Ã—2.00 |

---

## ðŸŽ¨ Phase 8 Visual Overhaul

All entities now render from **54 production PNG sprites** with clean alpha transparency:

| Asset Group | Files | States |
|---|---|---|
| Player | `player/` â€” 13 state PNGs + 4 chassis variants | idle, move, bank_l/r, fire, hit, damaged, destroy, destroyed |
| Scout | `enemies/scout/` â€” 5 PNGs | base, idle, move, attack, hit |
| Shooter | `enemies/shooter/` â€” 5 PNGs | base, idle, move, attack, hit |
| Heavy | `enemies/heavy/` â€” 5 PNGs | base, idle, move, attack, hit |
| Shield Elite | `enemies/shield_elite/` â€” 4 PNGs | base, idle, move, hit |
| Bosses | `bosses/` â€” 5 PNGs | assembly_warden, core_executor, reactor_titan, defense_commander, drone_overlord |
| Projectiles | `projectiles/` â€” 4 PNGs | bullet_pulse, bullet_scatter, enemy_bullet, missile |
| Shadows | `shadows/` â€” 6 PNGs | player, scout, shooter, heavy, shield, boss (unrotated) |
| VFX | `vfx/` â€” 1 PNG | engine_flame |

**SpriteManager pipeline:** all sprites loaded once at startup â†’ 2-degree quantized rotation cache â†’ no per-frame Surface allocations â†’ Layer 1 shadow / Layer 2 entity / Layer 3 VFX rendering.

---

## ðŸ§ª Automated Tests â€” 314 Passing

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
| `test_phase6_bosses` | 5 bosses Ã— phase transitions | ~35 |
| `test_phase7_release` | Save/load, fullscreen, resolution | ~22 |
| `test_phase8_assets` | 54 sprites Ã— 3 assertions each | ~186 |
| `test_phase8_missions_hardening` | 5-sector structure + 9 wave types lifecycle | ~128 |
| `test_runtime_smoke` | Headless game loop â€” no crash | ~6 |

---

## ðŸ’¾ Save & Progression Architecture

- Saved atomically to `save_data_pc.json` after every mission completion and upgrade purchase.
- Persisted state: scrap balance, upgrade levels (per stat), unlocked sectors & missions, completed missions, defeated bosses, active difficulty, campaign victory flag.
- Schema-safe: missing/corrupt keys fall back to defaults â€” absent or damaged save files never crash the game.

---

## ðŸ“¦ Building a Standalone Executable (Windows)

```bash
pip install pyinstaller
pyinstaller DroneHunter.spec
# Output: dist/DroneHunter/DroneHunter.exe
```

---

## ðŸ“‹ System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 / Linux / macOS | Windows 11 |
| Python | 3.10+ | 3.12+ |
| Resolution | 1280Ã—720 | 1920Ã—1080 |
| Audio | Any stereo device (auto fail-safe if absent) | â€” |
