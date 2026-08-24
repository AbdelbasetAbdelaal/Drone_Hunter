# 📜 Changelog — Drone Hunter 2D

All notable changes to the **Drone Hunter 2D** project are documented in this file.

---

## [Phase 15] — Player Survivability & Objective Defense Balance Pass (2026)

### Added & Tuned
- **Damage Resolution & Spike Prevention**:
  - Implemented configurable **Damage Grace Window (`damage_grace_duration = 0.25s`)** preventing multi-projectile frame deletions.
  - Sequenced bullet and hazard collisions in `CombatSystem` to honor temporary post-hit invulnerability and post-shield absorption windows.
  - Subdued camera shake and damage flash for clear tactical visibility on hit.
- **Objective Defense Staggering & Attack Windows**:
  - **Anti-Air Platforms (`AAPlatform`)**: Staggered fire cooldowns (`2.0s` Light, `3.0s` Heavy, `4.0s` Missile), balanced damages (`14`, `22`, `28`), and distinct charging telegraphs (`0.35s - 0.65s`).
  - **Combat Aircraft (`CombatAircraft`)**: Tuned kinematic flight paths (`300px/s` Interceptor, `240px/s` Bomber), reduced burst damages (`12`, `16`), and enforced `1.5s` disengagement repositioning.
  - **Radar & Strategic Suppression**: Radar destruction materially reduces reinforcement pressure by +50% per node; cloaked players suppress radar alerts, AA targeting, and aircraft runs.
- **Defensive Abilities & Armor**:
  - Verified Barrel Roll i-frames, Tactical Cloak detection suppression, and Overdrive invulnerability.
  - Meaningful armor reduction subtracting directly from projectile damage.
- **Comprehensive Survivability Test Suite**:
  - Added `TestPlayerSurvivabilityAndDefenseBalance` bringing total passing automated tests to **666 passed**.

---

## [Phase 14] — Objective Assault Gameplay Overhaul (2026)

### Added
- **Objective Assault Mission Model (`ObjectiveSystem` & `GroundObjective`)**:
  - Replaced traditional boss-at-end mission loops with deep, tactical Ground Target Objective Assaults across all 25 campaign missions.
  - Added physical in-world target fortresses: `Radar Command Center`, `Missile Silo Complex`, `Sub-Level Power Reactor`, `Tactical Communications Relay`, `Cyber Defense Core`, and `Munitions Foundry`.
  - Multi-tier damage states: `ACTIVE`, `SHIELDED`, `DAMAGED`, `CRITICAL`, `DESTROYED`.
- **Integrated Defense Networks**:
  - **Radar Nodes (`RadarNode`)**: Early warning sensors with real-time player detection, scan sweeps, alert states, and bounded reinforcement triggers.
  - **Anti-Air Platforms (`AAPlatform`)**: Directional flak cannons and missile turrets (`Light AA`, `Heavy AA`, `Missile Launcher`) with aiming, charge telegraphing, and destruction physics.
  - **Combat Aircraft (`CombatAircraft`)**: Fully airborne AI-controlled enemy aircraft (`Interceptor` dogfighters and `Attack` bombers) engaging player in dynamic aerial combat.
  - **Shield Generators (`ShieldGenerator`)**: Auxiliary defensive perimeter structures powering objective invulnerability shields until eliminated.
- **Dynamic Escalation & Tactical Telemetry**:
  - 5-tier defense configurations scaling defense density, attack patterns, and reinforcement pacing from early to late missions.
  - HUD direction navigation compass, objective HP bar, shield vulnerability state, range meter, and flashing Radar Alert warnings.
- **Automated Objective Test Suite**:
  - Added `test_objective_assault.py` with 25 unit and integration tests expanding the test suite to **604 passed tests**.

---

## [Phase 13] — Gameplay Mastery, Combat Depth & Adaptive Pacing Pass (2026)

### Added
- **Adaptive Intensity Layer in Combat Director (`CombatDirector`)**:
  - Implemented real-time dynamic intensity states: `CALM`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - Evaluates player health percentage, kill combos, live enemy count, encounter duration, and boss proximity without inflating raw enemy HP.
  - Dynamically modulates encounter spawn pacing and relief intervals (0.75s – 1.4s).
- **Deterministic Tactical Enemy Formations (`EncounterSystem`)**:
  - Structured tactical arrival formations: `FORMATION_V`, `FORMATION_WEDGE`, `FORMATION_LINE`, `FORMATION_STAGGERED`, `FORMATION_FLANK`, `FORMATION_ESCORT`.
  - Deterministic anchor offsets ensure readable, tactical fleet engagements per encounter archetype.
- **Combat Momentum & Tiered Hit Feedback (`CombatFeedbackSystem`)**:
  - Streak-based combo multiplier system ($x1 \to x99$) with dynamic score popups.
  - Micro hit-stop ($0.04s$) on heavy hits and critical impacts.
  - Automatic momentum reset on heavy damage ($\ge 15$) or streak timeout.
- **Boss Performance Rating Card Auto-Dismissal**:
  - Connected `ctx.boss_rating_timer` directly to the active `GameContext.update_timers()` pipeline, resolving the issue where the post-boss rating card remained permanently frozen on screen.
  - Added clean auto-dismissal after 3.5 seconds and reset logic on mission restart.
- **Automated Mastery Test Suite**:
  - Added `test_gameplay_mastery.py` with 19 comprehensive behavioral unit tests expanding the test suite to **579 passed tests**.

---

## [Phase 12] — Full Generic & PS2/USB Controller Support, D-Pad Menu Navigation & Audio Polish (2026)

### Added
- **Full Generic USB / PS2-Style Gamepad Support**:
  - Integrated full support for Twin USB Gamepad and generic DirectInput/PS2-style controllers without replacing the existing input architecture.
  - Normalized paired front shoulder buttons (`FRONT_TOP` and `FRONT_BOTTOM`) into distinct tap/hold actions (Tap: Next Weapon / Hold: Previous Weapon; Tap: Cloak / Hold: Cycle Drone Class).
  - Configured hold thresholds (0.4s for weapons/drone cycling, 1.0s for fullscreen toggle) with strict mutual exclusivity.
- **Universal D-Pad Menu & Grid Navigation**:
  - Complete 2D grid navigation and luminous visual focus indicators across all screens:
    - **Drone Hangar & Upgrade Bay**: 2D grid navigation between 4 upgrade cards and 4 bottom utility buttons.
    - **Drone Chassis Select**: Horizontal carousel navigation across 5 combat chassis with quick back button access.
    - **Mission Failed & Game Over**: Vertical 1D navigation across Retry, Sector Map, and Main Menu buttons.
    - **Pause Menu & Settings**: Full controller toggle and configuration support.
    - **Mission Complete & Sector Complete**: Navigation between Next Stage / Sector Map and Hangar.
- **Contextual Semantic Action Resolution Architecture (`InputContext`)**:
  - Implemented strict context-based action resolution across `GAMEPLAY`, `MAIN_MENU`, `MISSION_SELECT`, `DRONE_SELECT`, `HANGAR`, `WEAPON_MENU`, `SETTINGS`, `PAUSE`, `MAP`, `MISSION_COMPLETE`, `MISSION_FAILED`.
  - Resolved physical button semantics without duplicate or conflicting dispatches:
    - **Cross**: `FIRE_PRIMARY` in Gameplay, `CONFIRM` in UI (0 duplicate events).
    - **Circle**: `EMP` in Gameplay, `CANCEL` in UI (0 duplicate events).
    - **Front Bottom**: `CLOAK` in Gameplay (0 accidental skin change), `CYCLE_SKIN` in Hangar (0 accidental cloak), hold $\ge 0.4s \rightarrow$ `CYCLE_CLASS` in customizer.
    - **Front Top**: Tap $\rightarrow$ `WEAPON_NEXT`, hold $\ge 0.4s \rightarrow$ `WEAPON_PREV` (strictly 1 action per physical press).
    - **Select**: `SECTOR_MAP` in Gameplay, `HANGAR_BAY` in Hangar menus (0 simultaneous dispatch).
    - **Start**: Tap $\rightarrow$ `PAUSE`, hold $\ge 1.0s \rightarrow$ `FULLSCREEN` (mutually exclusive).
  - Added full test suite verification expanding to **560 / 560 passed tests** with comprehensive event duplicate audits.
- **Boss-Grade Cataclysmic Player Death Audio**:
  - Enhanced player death sound to trigger epic multi-layered boss explosion audio (`death_boss` + `death_heavy` + `player_death`) upon drone destruction.
- **Dynamic HUD Level Telemetry**:
  - Connected combat HUD top-right telemetry dynamically to sector and mission metadata via `get_mission_data()`, updating current sector and stage in real-time.

### Fixed
- **Sector Complete Bonus Calculation**:
  - Resolved `TypeError: unsupported operand type(s) for +: 'int' and 'dict'` by correctly looking up sector bonuses from `SECTOR_BONUS[sector_id]`.
- **Missing Module Imports**:
  - Fixed `UPGRADE_COSTS` and `MAX_UPGRADE_LEVEL` imports in `src/core/game.py`.
- **UI Function Signatures**:
  - Standardized `selected_index` parameter across all UI rendering functions in `src/ui/menus.py` and `src/ui/drone_select.py`.
- **Comprehensive Codebase Audit**:
  - Verified 100% health across all 51 Python modules, 17 game states, 17 UI screens, and **555 / 555 automated tests passing (100% green)**.

---

## [Phase 11] — First-Class Controller, Gamepad & Joystick Support (2026)

### Added
- **Centralized Input Management Architecture (`InputManager`)**:
  - Centralized input layer in `src/input/input_manager.py` converting hardware events into canonical game actions (`MOVE_X`, `MOVE_Y`, `AIM_ANGLE`, `FIRE_PRIMARY`, `FIRE_SECONDARY`, `WEAPON_NEXT`, `WEAPON_PREV`, `ROLL`, `EMP`, `ULTIMATE`, `SPECIAL`, `PAUSE`, `CLOAK`).
- **First-Class Xbox, Gamepad & Joystick Support**:
  - Full support for Xbox 360/One/Series controllers, XInput-compatible gamepads, generic USB gamepads, and joysticks.
  - Dual analog stick controls: Left stick smooth flight movement, Right stick 360-degree aiming.
  - Triggers for RT Primary Fire and LT Secondary Fire.
- **Analog Radial Deadzone & Response Curve**:
  - Radial deadzone (`0.12` default) preventing stick drift.
  - Non-linear response curve $f(m) = m^{1.35}$ for micro-precision steering and 100% deflection max speed.
- **Safe Bounded Vibration / Rumble**:
  - Multi-stage vibration feedback on player damage, firing heavy weapons, EMP blasts, Overdrive activation, and boss encounters. Failsafe fallback if unsupported.
- **Hot-Plugging & Device-Aware UI Prompts**:
  - Dynamic `JOYDEVICEADDED` / `JOYDEVICEREMOVED` hot-plugging. Safe 0-controller startup.
  - Dynamic HUD action badges displaying `[SHIFT]` / `[E]` / `[F]` on Keyboard vs `[A]` / `[X]` / `[Y]` / `[RT]` on Gamepad.
- **Dedicated Input Test Suite**:
  - Created `test_input_system.py` (16 unit tests). Total project test suite expanded to **481 / 481 tests passing (100% green)**.

---

## [Phase 10] — Real Production Asset Integration, Audio Synthesis & Combat Polish (2026)

### Added
- **Authoritative Real Production PNG Asset Integration**:
  - Integrated canonical production weapon projectile sprites (`laser_pulse.png`, `laser_scatter.png`, `missile.png`, `laser_beam.png`, `tesla_orb.png`, `cluster_torpedo.png`) across all 11 weapon systems.
  - Integrated canonical production VFX overlays (`explosion_1.png`, `explosion_2.png`, `shockwave.png`, `shield_bubble.png`, `engine_flame.png`) for all enemy destructions, boss explosions, player destruction, and weapon impacts.
  - Added startup validation and live render telemetry (`weapon_asset_usage`, `vfx_asset_usage`) in `SpriteManager`.
- **Physical Multi-Harmonic Explosion Audio Synthesis**:
  - Re-synthesized explosion audio in `sound_synth.py` with continuous dynamic low-pass filters (1.9kHz down to 65Hz) and chest-punching sub-bass harmonics (20Hz–55Hz).
  - Multi-stage dreadnought boss detonations, metallic scout ruptures, heavy armored hull groans, and catastrophic core breaches.
  - Full stereo interleaved 16-bit PCM buffer compatibility dynamically adapting to mixer initialization.
- **Dedicated Real Asset Integration Test Suite**:
  - Created `test_real_asset_integration.py` (15 unit tests covering asset validation, telemetry, forward firing vectors, explosion overlays, and deferred death sequences).
  - Total project test suite expanded to **435 / 435 tests passing (100% green)**.

### Fixed
- **Weapon Forward Trajectory & Aim Math**:
  - Resolved backward-firing bug across all weapon types by projecting forward target points strictly along `aim_angle` from individual mount locations.
  - Synchronized `MOUSEBUTTONDOWN` window coordinates through `get_canvas_mouse_pos()` and `screen_to_world()`.
- **Deferred Player Destruction Sequence**:
  - Eliminated premature Mission Failure popup; player death now executes a full 1.4-second explosion sequence with shockwaves, fiery shrapnel, camera tracking, and uninterrupted audio before displaying the failure UI.
- **Arena Enemy Boundary Constraint**:
  - Clamped all enemy movement inside world boundaries to prevent enemies from flying off-map.

---

## [Phase 9] — Combat Feedback, Audio Hierarchy & Weapon Identity
- Implemented distinct visual and audio identities for all 11 primary and secondary weapons.
- Added localized muzzle flashes and weapon recoil impulses.
- Connected multi-channel audio priority manager with voice throttling.

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
