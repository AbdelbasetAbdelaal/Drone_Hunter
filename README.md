# ðŸ›¸ Drone Hunter 2D â€” PC Edition

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/engine-pygame--ce%202.5%2B-green.svg)](https://pyga.me/)
[![Tests](https://img.shields.io/badge/tests-314%20passing-brightgreen.svg)](#-automated-tests)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)
[![Phase](https://img.shields.io/badge/phase-8%20Visual%20Overhaul-purple.svg)](#-development-phases)

**Drone Hunter 2D** is a high-performance industrial sci-fi tactical top-down drone combat game built with Python and `pygame-ce`.  
Fight through **5 sectors**, complete **25 combat missions**, defeat **5 sector bosses** and the **Drone Overlord**, upgrade your drone in the Hangar, and master 6 weapons with 4 tactical abilities.

---

## ðŸš€ Quick Start

### Prerequisites
```bash
pip install pygame-ce>=2.5.0 pytest>=7.0.0
# or
pip install -r requirements.txt
```

### Launch the Game
```bash
python drone_hunter_pc/main.py
```

### Run All Tests (314 tests)
```bash
pytest drone_hunter_pc/tests
```

---

## ðŸ•¹ï¸ Controls Reference

| Action | Primary | Alternate |
|:---|:---|:---|
| **Movement** | `W A S D` | Arrow Keys |
| **Aim & Fire** | Mouse Aim + `LMB` | â€” |
| **Switch Weapon** | `1`â€“`6` | `TAB` / Mouse Wheel |
| **EMP Blast** | `E` | `RMB` |
| **Overdrive** | `F` | `Q` / Middle Mouse |
| **Barrel Roll** | `Left Shift` | `Right Shift` |
| **Tactical Cloak** | `K` | â€” |
| **Cycle Drone Skin** | `C` | Hangar menu |
| **Pause** | `ESC` | `P` |
| **Fullscreen** | `F11` | â€” |
| **Sector Map** | `M` | Menu button |
| **Hangar** | `H` | Menu button |

---

## âš¡ Arsenal â€” 6 Weapons

| # | Weapon | Behaviour |
|---|---|---|
| 1 | **Pulse Cannon** | Rapid twin plasma bolts â€” default loadout |
| 2 | **Scatter Shotgun** | 5-pellet spread burst for close-range swarm clearing |
| 3 | **Homing Missiles** | Lock-on ordnance that tracks the nearest target |
| 4 | **Plasma Laser Beam** | Continuous piercing beam through all targets in a line |
| 5 | **Arc Lightning Tesla** | Chain lightning arcing across enemy groups |
| 6 | **Cluster Torpedo** | Heavy warhead splitting into 6 explosive bomblets |

---

## ðŸ‘¾ Enemy Roster

| Enemy | Role | Phase |
|---|---|---|
| **Scout Drone** | Fast dive-bomb melee attacker | Phase 2A |
| **Shooter Drone** | Ranged dual-plasma marksman | Phase 2B |
| **Heavy Drone** | Armoured bulldozer, 20% damage reduction | Phase 2C |
| **Shield Elite** | Rotating forcefield protecting adjacent enemies | Phase 2D |
| **Assembly Warden** | Sector 1 boss â€” radial burst + spread barrage | Phase 6 |
| **Core Executor** | Sector 2 boss â€” homing volley + laser sweep | Phase 6 |
| **Reactor Titan** | Sector 3 boss â€” energy wave + drone deploy | Phase 6 |
| **Defense Commander** | Sector 4 boss â€” missile salvo + aggressive sweep | Phase 6 |
| **Drone Overlord** | Final boss â€” 4-phase endgame encounter | Phase 6 |

> **Phase 8 Visual Overhaul:** All enemies above now render from production-quality 2D industrial sci-fi sprites with per-state animation (idle / move / attack / hit), rotation-cached via `SpriteManager`, and unrotated drop shadows.

---

## ðŸŒŒ Campaign â€” 5 Sectors Ã— 5 Missions

| Sector | Name | Theme | Boss |
|---|---|---|---|
| 1 | **CYBER FACTORY** | Industrial drone production plant | Assembly Warden |
| 2 | **CORE SECTOR** | Heavily defended reactor core complex | Core Executor |
| 3 | **REACTOR ZONE** | Volatile energy conduits & plasma machinery | Reactor Titan |
| 4 | **DEFENSE GRID** | Fortified automated defense installations | Defense Commander |
| 5 | **DRONE COMMAND** | Enemy command infrastructure | Drone Overlord |

### Mission Objectives
- **Destroy All** â€” Clear every enemy wave in the encounter sequence.
- **Survive** â€” Endure relentless swarms for a fixed duration (45 / 75 / 90 s).
- **Complete Encounters** â€” Defeat every wave in the multi-wave encounter sequence.

### Wave Compositions (Phase 8 Expanded)
| Composition | Enemies | Count |
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

## ðŸ› ï¸ Hangar Upgrades

Earn **Scrap** by destroying enemies and completing missions. Spend it in the Hangar:

| Upgrade | Effect |
|---|---|
| ðŸ”‹ Battery Capacity | +20 max HP per level (max lv 5) |
| ðŸš€ Thruster Agility | +15% flight speed per level (max lv 5) |
| âš¡ Fire-Rate Overclock | âˆ’12% weapon cooldown per level (max lv 5) |
| ðŸ’¥ EMP Quick-Charger | âˆ’2.5 s EMP recharge per level (max lv 4) |
| ðŸ›¸ Wingman Escort Drone | Autonomous escort minidrone (max lv 3) |
| ðŸ‘» Tactical Cloak Unit | Unlocks cloak ability `K` (max lv 3) |
| ðŸš€ Homing Missiles | Unlocks missile weapon (max lv 3) |
| âš¡ Plasma Laser Beam | Unlocks beam weapon (max lv 3) |
| ðŸŒ©ï¸ Arc Lightning Tesla | Unlocks tesla weapon (max lv 3) |
| ðŸ’£ Cluster Torpedo | Unlocks cluster weapon (max lv 3) |
| âš¡ Overdrive Reactor | Enhances overdrive duration & recharge (max lv 3) |

### Drone Skins (cycle with `C`)
`PLATINUM VANGUARD` Â· `CYBERNEON PHANTOM` Â· `SOVEREIGN GOLD` Â· `CRIMSON WIDOW` Â· `VOID STEALTH` Â· `SOLAR FLARE`

---

## ðŸŽ® Difficulty Modes

| Mode | HP | Speed | Damage | Score |
|---|---|---|---|---|
| EASY | Ã—0.75 | Ã—0.80 | Ã—0.70 | Ã—0.80 |
| NORMAL | Ã—1.00 | Ã—1.00 | Ã—1.00 | Ã—1.00 |
| HARD | Ã—1.35 | Ã—1.20 | Ã—1.30 | Ã—1.40 |
| NIGHTMARE | Ã—1.75 | Ã—1.40 | Ã—1.60 | Ã—2.00 |

---

## ðŸ“ Project Structure

```
Drone_Hunter/
â”œâ”€â”€ README.md                          # â† You are here
â”œâ”€â”€ requirements.txt                   # pygame-ce>=2.5.0, pytest>=7.0.0
â”œâ”€â”€ DroneHunter.spec                   # PyInstaller build spec
â”œâ”€â”€ drone_hunter_pc/                   # PC Edition (primary codebase)
â”‚   â”œâ”€â”€ main.py                        # Entry point â€” init pygame & launch Game
â”‚   â”œâ”€â”€ save_data_pc.json              # Atomic save file (scrap, upgrades, missions)
â”‚   â”œâ”€â”€ assets/
â”‚   â”‚   â”œâ”€â”€ sprites/
â”‚   â”‚   â”‚   â”œâ”€â”€ player/                # 13 player state PNGs + 4 chassis variants
â”‚   â”‚   â”‚   â”œâ”€â”€ enemies/
â”‚   â”‚   â”‚   â”‚   â”œâ”€â”€ scout/             # 5 state PNGs (base/idle/move/attack/hit)
â”‚   â”‚   â”‚   â”‚   â”œâ”€â”€ shooter/           # 5 state PNGs
â”‚   â”‚   â”‚   â”‚   â”œâ”€â”€ heavy/             # 5 state PNGs
â”‚   â”‚   â”‚   â”‚   â””â”€â”€ shield_elite/      # 4 state PNGs
â”‚   â”‚   â”‚   â”œâ”€â”€ bosses/                # 5 boss PNGs (assembly_warden â€¦ drone_overlord)
â”‚   â”‚   â”‚   â”œâ”€â”€ projectiles/           # bullet_pulse, bullet_scatter, enemy_bullet, missile
â”‚   â”‚   â”‚   â”œâ”€â”€ shadows/               # 6 unrotated drop shadow PNGs
â”‚   â”‚   â”‚   â””â”€â”€ vfx/                   # engine_flame VFX
â”‚   â”‚   â””â”€â”€ environment/               # Parallax background layers
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”‚   â”œâ”€â”€ game.py                # Main game loop (844 lines) â€” input, update, render
â”‚   â”‚   â”‚   â”œâ”€â”€ game_context.py        # Central shared state container (GameContext)
â”‚   â”‚   â”‚   â”œâ”€â”€ game_state.py          # State machine constants
â”‚   â”‚   â”‚   â””â”€â”€ clock.py               # Delta-time clock
â”‚   â”‚   â”œâ”€â”€ data/
â”‚   â”‚   â”‚   â”œâ”€â”€ game_data.py           # Authoritative constants: weapons, enemies, upgrades, skins
â”‚   â”‚   â”‚   â”œâ”€â”€ mission_data.py        # 25 missions Ã— 5 sectors + wave compositions
â”‚   â”‚   â”‚   â”œâ”€â”€ boss_data.py           # 5 boss definitions with multi-phase configs
â”‚   â”‚   â”‚   â””â”€â”€ settings.py            # Resolution, world size, colour palette
â”‚   â”‚   â”œâ”€â”€ entities/
â”‚   â”‚   â”‚   â”œâ”€â”€ player.py              # Player drone (497 lines) â€” physics, weapons, abilities
â”‚   â”‚   â”‚   â”œâ”€â”€ enemy.py               # Scout, Shooter, Heavy, Shield (706 lines)
â”‚   â”‚   â”‚   â”œâ”€â”€ boss.py                # 5 boss entities with phase transitions (535 lines)
â”‚   â”‚   â”‚   â”œâ”€â”€ bullet.py              # Bullet, HomingMissile, ClusterTorpedo, BeamWeapon, Tesla
â”‚   â”‚   â”‚   â”œâ”€â”€ powerup.py             # Scrap pickup entity
â”‚   â”‚   â”‚   â”œâ”€â”€ hazard.py              # Environmental hazards
â”‚   â”‚   â”‚   â””â”€â”€ obstacle.py            # Environmental obstacles
â”‚   â”‚   â”œâ”€â”€ rendering/
â”‚   â”‚   â”‚   â”œâ”€â”€ sprite_manager.py      # SpriteManager â€” load, scale, rotation cache (455 lines)
â”‚   â”‚   â”‚   â”œâ”€â”€ player_renderer.py     # Dedicated player draw pipeline with VFX layers
â”‚   â”‚   â”‚   â”œâ”€â”€ renderer.py            # Main compositor: Layer 1 shadow â†’ Layer 2 entity â†’ Layer 3 VFX
â”‚   â”‚   â”‚   â”œâ”€â”€ particles.py           # Particle engine: explosions, sparks, LightningArc
â”‚   â”‚   â”‚   â”œâ”€â”€ environment.py         # Parallax layers, tile grid, environmental effects
â”‚   â”‚   â”‚   â”œâ”€â”€ camera.py              # World-to-screen transform with edge clamping
â”‚   â”‚   â”‚   â””â”€â”€ background.py          # Solid background fill
â”‚   â”‚   â”œâ”€â”€ systems/
â”‚   â”‚   â”‚   â”œâ”€â”€ encounter_system.py    # Wave lifecycle: spawn â†’ track â†’ clean â†’ complete
â”‚   â”‚   â”‚   â”œâ”€â”€ combat_director.py     # Multi-wave sequencer with inter-wave relief timer
â”‚   â”‚   â”‚   â”œâ”€â”€ combat_system.py       # Collision detection, damage resolution, hit VFX
â”‚   â”‚   â”‚   â”œâ”€â”€ combat_feedback.py     # Screen-space hit flash & damage numbers
â”‚   â”‚   â”‚   â”œâ”€â”€ mission_system.py      # Mission state machine: active â†’ completed/failed
â”‚   â”‚   â”‚   â”œâ”€â”€ boss_system.py         # Boss encounter controller with phase management
â”‚   â”‚   â”‚   â”œâ”€â”€ spawn_system.py        # Ambient enemy spawn scheduler
â”‚   â”‚   â”‚   â”œâ”€â”€ progression_system.py  # Scrap economy and upgrade application
â”‚   â”‚   â”‚   â”œâ”€â”€ save_system.py         # Atomic JSON load/save with schema migration
â”‚   â”‚   â”‚   â””â”€â”€ difficulty_system.py   # Difficulty modifier lookup
â”‚   â”‚   â”œâ”€â”€ ui/
â”‚   â”‚   â”‚   â”œâ”€â”€ hud.py                 # In-game HUD: health, energy, weapon, minimap (287 lines)
â”‚   â”‚   â”‚   â”œâ”€â”€ menus.py               # All menus: main, pause, sector map, mission select (488 lines)
â”‚   â”‚   â”‚   â”œâ”€â”€ hangar.py              # Upgrade store UI
â”‚   â”‚   â”‚   â””â”€â”€ font_manager.py        # System font fallback manager
â”‚   â”‚   â””â”€â”€ audio/
â”‚   â”‚       â”œâ”€â”€ audio_manager.py       # Sound playback with fail-safe no-audio fallback
â”‚   â”‚       â””â”€â”€ sound_synth.py         # Procedural audio synthesis (211 lines)
â”‚   â””â”€â”€ tests/                         # 314 automated tests across 16 test files
â”‚       â”œâ”€â”€ test_game_systems.py        # Core system integration
â”‚       â”œâ”€â”€ test_phase1_flight.py       # Player flight physics
â”‚       â”œâ”€â”€ test_phase2a_scout.py       # Scout AI behaviour
â”‚       â”œâ”€â”€ test_phase2b_shooter.py     # Shooter AI & positioning
â”‚       â”œâ”€â”€ test_phase2c_heavy.py       # Heavy AI & armour
â”‚       â”œâ”€â”€ test_phase2d_encounters.py  # Encounter lifecycle (all wave types)
â”‚       â”œâ”€â”€ test_phase2e_combat_director.py  # Multi-wave sequencer
â”‚       â”œâ”€â”€ test_phase3_weapons.py      # All 6 weapon classes
â”‚       â”œâ”€â”€ test_phase4_progression.py  # Scrap economy & upgrades
â”‚       â”œâ”€â”€ test_phase5_missions.py     # Mission system state machine
â”‚       â”œâ”€â”€ test_phase5_performance.py  # Performance regression & entity bounds
â”‚       â”œâ”€â”€ test_phase6_bosses.py       # 5 boss phase transitions & attacks
â”‚       â”œâ”€â”€ test_phase7_release.py      # Save/load, fullscreen, resolution scaling
â”‚       â”œâ”€â”€ test_phase8_assets.py       # Phase 8 sprite validation (186 sub-tests)
â”‚       â”œâ”€â”€ test_phase8_missions_hardening.py  # Mission regression + wave lifecycle (128 sub-tests)
â”‚       â””â”€â”€ test_runtime_smoke.py       # Full headless game loop smoke test
â””â”€â”€ drone_hunter_mobile/               # Mobile prototype (Kivy / Buildozer)
    â”œâ”€â”€ main.py
    â”œâ”€â”€ buildozer.spec
    â””â”€â”€ src/
```

---

## ðŸ§ª Automated Tests

**314 tests â€” 100% passing** (as of commit `93e582a`)

| Test File | Coverage Area | Tests |
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
| `test_phase8_assets` | 54 sprites Ã— 3 checks each | ~186 |
| `test_phase8_missions_hardening` | 5 sectors/25 missions + 9 wave types | ~128 |
| `test_runtime_smoke` | Headless game loop, no crash | ~6 |

---

## ðŸ’¾ Save Architecture

- Saved atomically to `save_data_pc.json` after every mission and upgrade.
- Stored: scrap balance, upgrade levels, unlocked sectors, completed missions, defeated bosses, difficulty setting, campaign victory flag.
- Schema-safe: missing keys fall back to defaults â€” corrupt or absent save files never crash the game.

---

## ðŸ—ï¸ Building a Standalone Executable

```bash
pip install pyinstaller
pyinstaller DroneHunter.spec
# Output: dist/DroneHunter/DroneHunter.exe
```

---

## ðŸ”– Development Phases

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Player flight physics & controls | âœ… Complete |
| Phase 2Aâ€“D | Scout / Shooter / Heavy / Shield enemies | âœ… Complete |
| Phase 3 | 6-weapon arsenal | âœ… Complete |
| Phase 4 | Scrap economy & hangar upgrades | âœ… Complete |
| Phase 5 | 25 campaign missions, 5 sectors, performance hardening | âœ… Complete |
| Phase 6 | 5 sector bosses + Drone Overlord (multi-phase) | âœ… Complete |
| Phase 7 | Release: save/load, fullscreen, resolution scaling | âœ… Complete |
| Phase 8 | 2D visual overhaul: 54 production sprites, rotation cache, shadows, expanded missions | âœ… Complete |

---

## ðŸ“œ License

Developed with Python & pygame-ce. Free to play, modify, and distribute.



[![Pygame](https://img.shields.io/badge/engine-Pygame--CE%20%2F%20Pygame-green.svg)](https://pyga.me/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-orange.svg)](#)

**Drone Hunter** is an action-packed 2D sci-fi arcade drone combat game featuring multi-weapon loadouts, tactical abilities (Overdrive, Cloak, EMP, Evasive Barrel Roll), dynamic boss encounters, wingman support drones, hangar customizations, and responsive flight kinematics.

---

## ðŸŽ® Quick Start & Running the Game

### Prerequisites
- Python 3.10 or higher
- `pygame` or `pygame-ce`

```bash
pip install pygame-ce
```

### Run PC Edition:
```bash
python drone_hunter_pc/main.py
```

### Run Mobile Touch Edition (Simulation):
```bash
python drone_hunter_mobile/main.py
```

### Run Automated Tests:
```bash
pytest drone_hunter_pc/tests
```

---

## ðŸ•¹ï¸ Controls & Keybindings

| Action | PC Controls | Description |
| :--- | :--- | :--- |
| **Flight Movement** | `W`, `A`, `S`, `D` or `Arrow Keys` | Full 360Â° thruster flight with inertia damping |
| **Aim & Shoot** | `Mouse Aim` + `Left Mouse Button` | Fire active weapon towards crosshair |
| **Switch Weapons** | `1` - `6`, `TAB`, or `Mouse Wheel` | Instant loadout swap across 6 unlocked weapons |
| **Overdrive Ultimate** | `F`, `Q`, or `Middle Mouse Click` | 5s hyper-fire mode, increased damage & invulnerability |
| **EMP Shockwave** | `E` or `Right Mouse Button` | Screen-clearing EMP blast that destroys projectiles |
| **Evasive Barrel Roll** | `Left Shift` / `Right Shift` | High-speed directional dash with i-frames |
| **Tactical Cloak** | `K` | Invisibility cloak against enemy target tracking |
| **Drone Skin Customizer** | `C` | Real-time drone chassis theme cycler (6 skins) |
| **Pause & Settings** | `ESC` or `P` | Access audio toggles, CRT filters, and difficulty |

---

## âš¡ Arsenal & Weapons

1. **Pulse Cannon (âš¡)**: High-speed twin plasma bolts with rapid fire.
2. **Scatter Shotgun (ðŸ’¥)**: Multi-pellet spread shot for clearing close-range drone swarms.
3. **Homing Missiles (ðŸš€)**: High-yield ordnance that locks on and tracks nearby hostile targets.
4. **Plasma Laser Beam (âš¡)**: Continuous piercing beam cutting through all targets in a line.
5. **Arc Lightning Tesla (ðŸŒ©ï¸)**: High-voltage electrical bolts that chain across groups of enemies.
6. **Cluster Torpedo (ðŸ’£)**: Heavy ballistic warhead that splits into 6 explosive bomblets.

---

## ðŸ‘¾ Enemy Drones & Boss Dreadnoughts

| Enemy Type | Behavior & Combat Role |
| :--- | :--- |
| **Standard Scout** | Basic patrol unit with horizontal sine flight |
| **Fast Interceptor** | Agile lightweight interceptor with sudden accelerations |
| **Armored Mech** | Heavy chassis unit requiring concentrated firepower |
| **Shooter Drone** | Fires dual plasma salvos toward player trajectory |
| **Ground Turret & Vehicle** | Heavy surface defense cannons with triple-spread firing |
| **Chaser Drone** | Aggressive interceptor that zig-zags and hunts the player |
| **Kamikaze Swarm Drone** | Fast delta-wing drone that dive-bombs player at close range |
| **Support Shield Drone** | Projects a rotating blue forcefield protecting adjacent enemies |
| **Sniper Railgun Drone** | Locks a red tracer laser before firing a supersonic piercing beam |
| **Sky Dreadnought Boss** | 360Â° radial spiral bullet rings & enrage phase |
| **Stealth Mirage Boss** | Cloaks invisibly and relocates across the battlescape |
| **EMP Disrupter Boss** | Emits expanding weapon-jamming EMP shockwave rings |
| **Colossus Titan Mech** | 3-Phase Overclock berserk titan with orbital satellite shields |

---

## ðŸŒŒ Campaign Sectors

- **Sector 1: Megacity Skyline** (Neon rooftop megacity with heavy rain & drone patrols)
- **Sector 2: Cyber Factory Core** (Automated foundry with molten hazards & defense grids)
- **Sector 3: Orbital Space Citadel** (Deep space fortress with asteroid fields & meteor showers)
- **Sector 4: Stormy Ocean Battlescape** (Raging tempest ocean with naval warship salvos)
- **Sector 5: Neon Sun Desert Wasteland** (Scorching dune wasteland guarded by the Colossus Titan)

---

## ðŸ“ Repository Structure

```
Drone_Hunter/
â”œâ”€â”€ README.md                     # Main project documentation
â”œâ”€â”€ drone_hunter_pc/              # PC Edition (Desktop-optimized)
â”‚   â”œâ”€â”€ main.py                   # Clean entry point
â”‚   â”œâ”€â”€ save_data_pc.json         # Persistent atomic save data (coins, unlocks, upgrades)
â”‚   â”œâ”€â”€ tests/                    # Automated unit, integration & runtime smoke tests
â”‚   â”‚   â”œâ”€â”€ test_game_systems.py
â”‚   â”‚   â”œâ”€â”€ test_phase1_flight.py
â”‚   â”‚   â”œâ”€â”€ test_phase2a_scout.py
â”‚   â”‚   â”œâ”€â”€ test_phase2b_shooter.py
â”‚   â”‚   â”œâ”€â”€ test_phase2c_heavy.py
â”‚   â”‚   â”œâ”€â”€ test_phase2d_encounters.py
â”‚   â”‚   â””â”€â”€ test_runtime_smoke.py
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ core/                 # Engine loop, State machine, Context container, Clock
â”‚       â”œâ”€â”€ data/                 # Display settings, authoritative weapon/sector catalogs
â”‚       â”œâ”€â”€ entities/             # 2D Player, enemies, bosses, bullets, powerups, obstacles, hazards
â”‚       â”œâ”€â”€ systems/              # Combat collisions, encounters, spawn/wave manager, save/load
â”‚       â”œâ”€â”€ rendering/            # Parallax backgrounds, particle engine, scanline renderer
â”‚       â”œâ”€â”€ ui/                   # HUD, minimap, hangar upgrade store, menus, font manager
â”‚       â””â”€â”€ audio/                # Sound synthesis & audio cache manager
â””â”€â”€ drone_hunter_mobile/          # Mobile Edition (Touch controls, Android APK build)
    â”œâ”€â”€ main.py                   # Mobile game loop with touch input overlay
    â”œâ”€â”€ buildozer.spec            # Android APK build configuration
    â””â”€â”€ src/                      # Mobile game logic modules
```

---

## ðŸ› ï¸ Upgrades & Customization in Hangar

Earn **Gold Scrap** by defeating enemies and clearing waves. Visit the **Hangar** between stages to upgrade:
- ðŸ”‹ **Max Battery Capacity**: Increases maximum drone hull integrity.
- ðŸš€ **Thruster Agility**: Enhances flight speed and acceleration.
- âš¡ **Cannon Fire-Rate**: Reduces cooldowns across all weapons.
- ðŸ’¥ **EMP Shockwave Charger**: Accelerates EMP recharge speed.
- ðŸ›¸ **Wingman Minidrones**: Deploys automated escort drones that auto-fire on targets.
- ðŸ‘» **Tactical Cloaking Unit**: Grants tactical invisibility.
- ðŸš€ **Missiles / Beam / Tesla / Cluster**: Unlock advanced heavy weapon ordnance.
- ðŸŽ¨ **Drone Skins**: Select from *Platinum, Cyberneon, Sovereign, Crimson, Void Stealth, and Solar Flare*.

---

## ðŸ“œ License
Developed with Python & Pygame. Free to play, modify, and distribute.
