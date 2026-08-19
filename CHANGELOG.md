# 📜 Changelog — Drone Hunter 2D

All notable changes to the **Drone Hunter 2D** project are documented in this file.

---

## [Phase 8] — 2D Visual Entity Overhaul & Mission Hardening (2026)

### Added
- **54 Production 2D PNG Sprites**: Extracted and integrated high-detail industrial sci-fi assets for Player, Scout, Shooter, Heavy, Shield Elite, 5 Bosses, Projectiles, Shadows, and VFX.
- **Dedicated SpriteManager**:
  - Quantized 2-degree rotation cache (180 angles per sprite state).
  - Unrotated ground drop shadows rendering on dedicated shadow layer (Layer 1).
  - Pre-cached hit flash masks eliminating runtime surface allocation overhead.
- **Expanded Tactical Wave Compositions**:
  - 9 structured wave compositions (WAVE_SCOUTS_PATROL, WAVE_SCOUTS_ASSAULT, WAVE_SCOUTS_SWARM, WAVE_SHOOTERS_PAIR, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT, WAVE_HEAVY_BATTLEGROUP, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE).
- **Comprehensive Hardening Test Suite**:
  - 	est_phase8_assets.py (186 sprite asset validation checks).
  - 	est_phase8_missions_hardening.py (128 mission regression, wave lifecycle, and stress tests).
  - Reached **314 / 314 tests passing (100%)**.

### Fixed
- Scout enemy rotation connected to SpriteManager.get_rotated_scout_sprite() using AI heading angles.
- Eliminated white bounding box artifacts during entity hit flash via alpha-safe mask tinting.
- Grounded unrotated drop shadows for all flying entities.
- Synchronized mission data objective strings and survive timers across all 25 missions.

---

## [Phase 7] — Release Polish, Scaling & Packaging

### Added
- Fullscreen mode with dynamic aspect ratio preservation (F11).
- Multi-resolution scaling support (1280x720 up to 4K).
- Robust schema-safe JSON save/load system (save_data_pc.json).
- PyInstaller standalone build configuration (DroneHunter.spec).

---

## [Phase 6] — Sector Bosses & Drone Overlord

### Added
- **5 Major Boss Encounters**:
  - Sector 1: **Assembly Warden** (Radial bursts & spread barrages).
  - Sector 2: **Core Executor** (Stealth relocation & laser sweeps).
  - Sector 3: **Reactor Titan** (Energy shockwaves & escort deployments).
  - Sector 4: **Defense Commander** (Targeted missile salvos & orbital charges).
  - Sector 5: **Drone Overlord** (4-Phase multi-stage endgame boss).
- Dedicated oss_system.py and oss_data.py data-driven configuration pipeline.

---

## [Phase 5] — 25-Mission Campaign & Performance Stabilization

### Added
- Full 5-Sector / 25-Mission Campaign architecture (mission_system.py, mission_data.py).
- 3 Distinct Objective types: destroy_all, survive, complete_encounters.
- Performance limits: projectile pooling, entity culling, particle lifecycle boundaries.

---

## [Phase 4] — Player Progression & Hangar Upgrades

### Added
- Scrap economy system: rewards per enemy elimination and mission completion.
- Hangar Store: 11 upgradable attributes (HP, Speed, Fire-Rate, EMP, Wingmen, Cloak, Weapons).
- 6 Customizable Drone Skins (PLATINUM VANGUARD, CYBERNEON PHANTOM, SOVEREIGN GOLD, CRIMSON WIDOW, VOID STEALTH, SOLAR FLARE).

---

## [Phase 3] — 6-Weapon Combat Arsenal

### Added
- 6 Distinct Weapon Systems:
  1. Pulse Cannon (Twin plasma bolts)
  2. Scatter Shotgun (Swarm-clearing spread)
  3. Homing Missiles (Target-tracking ordnance)
  4. Plasma Laser Beam (Continuous piercing beam)
  5. Arc Lightning Tesla (Chain lightning across groups)
  6. Cluster Torpedo (Multi-bomblet explosive warhead)

---

## [Phase 2] — Tactical Enemy AI Roster (Phases 2A–2D)

### Added
- **Scout Drone (2A)**: Strafe, telegraph, dive-bomb, and recover state machine.
- **Shooter Drone (2B)**: Preferred range management, targeting lead, dual plasma burst.
- **Heavy Drone (2C)**: 20% passive damage reduction armor, close-proximity bulldozer pressure.
- **Shield Drone (2D)**: Protective rotating barrier shielding adjacent allies.

---

## [Phase 1] — Core Flight Kinematics & Controls

### Added
- 360-degree top-down inertia flight with acceleration and friction damping.
- Mouse-aim crosshair integration.
- Tactical abilities: EMP blast, Overdrive hyper-fire, Evasive Barrel Roll.
