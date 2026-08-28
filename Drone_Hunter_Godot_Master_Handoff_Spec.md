# Drone Hunter 2D — Master Handoff / Godot Rebuild Specification

**Purpose:** Single handoff reference for rebuilding or porting Drone Hunter from the current Python/Pygame implementation to Godot 4.x using Antigravity.

**Repository:** https://github.com/AbdelbasetAbdelaal/Drone_Hunter/tree/main/drone_hunter_pc

**Baseline references**
- Phase 1 baseline: `45209aa`
- Phase 2 baseline reviewed: `a769c8b`
- Latest reported test result: `725 passed`
- The current repository/README contains historical material. Do not treat every old README statement as a current product requirement.

---

## 1. PRODUCT IDENTITY

**Title:** Drone Hunter 2D

**Genre:** 2D top-down sci-fi tactical/combat action game.

**Current technology:** Python + `pygame-ce`.

**Target technology:** Godot 4.x.

**Platform:** Windows PC first.

**Core fantasy:** The player controls a combat drone flying through hostile industrial facilities, fighting enemy drone waves, completing tactical missions, earning Scrap, upgrading the drone, and progressing through a campaign.

**Design principles**
- Fast, responsive 2D combat.
- Clear enemy telegraphs.
- Strong weapon identity.
- Tactical movement and dodging.
- Mission-based progression.
- Upgrade loop between missions.
- Industrial sci-fi presentation.
- Keyboard/mouse first, controller support.
- Production-ready modular architecture.

---

## 2. EXPLICIT PRODUCT DECISIONS

These decisions supersede older code/README content when they conflict.

### Bosses are NOT part of the target game

Do not recreate:
- BossSystem
- boss battles
- boss-only campaign progression
- boss UI
- boss-specific save state
- boss-specific controls

Old save files may contain obsolete boss fields; they should be safely ignored.

### Drone skin switching is NOT part of the target game

Do not recreate:
- skin selection
- skin cycling
- skin inventory
- skin unlocks
- skin switching controls

The player uses one canonical drone appearance.

### No feature expansion during the rebuild foundation

First reproduce and stabilize the existing gameplay model. Do not invent new gameplay systems unless explicitly requested later.

---

## 3. CORE GAMEPLAY LOOP

```text
Launch
  ↓
Main Menu
  ↓
Save Slot / Continue
  ↓
Campaign / Sector / Mission Selection
  ↓
Mission Briefing
  ↓
Gameplay
  ↓
Fight enemy waves / complete objectives
  ↓
Earn Scrap / mission rewards
  ↓
Mission Result
  ↓
Hangar / upgrades
  ↓
Unlock next mission
  ↓
Repeat
```

---

## 4. CAMPAIGN STRUCTURE

Historical content defines:

**5 sectors × 5 missions = 25 missions**

Boss encounters are removed from the target product.

### Sector 1 — CYBER FACTORY
Industrial drone assembly plant.

### Sector 2 — CORE SECTOR
Fortified reactor/core complex.

### Sector 3 — REACTOR ZONE
Volatile energy conduits and plasma arrays.

### Sector 4 — DEFENSE GRID
Automated perimeter defense network.

### Sector 5 — DRONE COMMAND
Enemy command fortress.

The exact mission definitions should be read from the current repository during the rebuild rather than invented from this document.

---

## 5. MISSION OBJECTIVES

Existing objective concepts include:

### Destroy All
Eliminate all hostile waves in the mission area.

### Survive
Survive an aggressive assault for a defined duration. Historical durations included 45s, 75s, and 90s.

### Complete Encounters
Defeat a sequence of tactical combat encounters/waves.

Keep mission/objective definitions data-driven.

---

## 6. PLAYER DRONE CLASSES

Historical five classes:

| Class | Name | Archetype | Default Weapon | Trait |
|---|---|---|---|---|
| 0 | Striker | Balanced Generalist | Pulse Cannon | Balanced dual forward mounts |
| 1 | Phantom | High-Agility Interceptor | Rapid Autocannon | +15% speed / high fire rate |
| 2 | Titan | Heavy Armored Gunship | Heavy Plasma Orb | +50 max HP / +2 armor |
| 3 | Velocity | Advanced Speed Scout | Arc Lightning Tesla | +25% speed |
| 4 | Command | Dreadnought Destroyer | Railgun Accelerator | Maximum firepower / missile pod capability |

Preserve these active class identities if they still exist in the current source.
Do not add new classes.
Do not implement skin customization.

---

## 7. PLAYER MOVEMENT

Primary keyboard controls:

`W A S D` and Arrow Keys.

Movement must be continuous while held.

Godot implementation should use InputMap actions and continuous input polling in the physics/gameplay loop.

---

## 8. AIMING

Mouse cursor controls aim direction.

Controller uses right-stick/analog aim.

Preserve the current cursor/crosshair direction model.

---

## 9. FIRE CONTROLS

Primary fire:
- `LMB`
- `Space`

Secondary fire:
- `RMB`

Weapon-specific behavior comes from the equipped weapon definition.

---

## 10. PLAYER ABILITIES

Historical abilities include:

### Barrel Roll / Dodge
- Left Shift / Right Shift

### EMP Shockwave
- `E`

### Tactical Overdrive
- `F` / `Q`

### Tactical Cloak
- `C` / `K`

Preserve the active gameplay contract from the current source.
Do not confuse cloak with drone skin switching.

---

## 11. WEAPON ARSENAL

Historical arsenal:

1. Pulse Cannon
2. Rapid Autocannon
3. Scatter Shotgun
4. Homing Missiles
5. Missile Barrage
6. Heavy Plasma Orb
7. Railgun Accelerator
8. Plasma Laser Beam
9. Arc Lightning Tesla
10. Cluster Torpedo
11. EMP Shockwave

### Weapon identities

**Pulse Cannon**
- Rapid twin plasma bolts.
- Dual forward mounts.

**Rapid Autocannon**
- Alternating high-cyclic kinetic fire.

**Scatter Shotgun**
- Five-pellet spread.
- Strong against swarms.

**Homing Missiles**
- Target-locking heavy ordnance.
- Rocket trail.

**Missile Barrage**
- Four-missile salvo.
- Dual wing pod concept.

**Heavy Plasma Orb**
- Slow, high-damage plasma projectile.
- Shockwave behavior.

**Railgun Accelerator**
- Very fast piercing projectile.

**Plasma Laser Beam**
- Continuous piercing directed-energy beam.

**Arc Lightning Tesla**
- Chain lightning between clustered enemies.

**Cluster Torpedo**
- Heavy projectile splitting into multiple explosive submunitions.

**EMP Shockwave**
- Radial electromagnetic pulse.

Numeric stats must be read from the current source rather than invented.

---

## 12. DATA-DRIVEN WEAPONS

Recommended Godot model:

```text
WeaponDefinition (Resource)
    id
    display_name
    damage
    cooldown
    energy_cost
    projectile_type
    projectile_speed
    spread
    lifetime
    targeting_mode
    special_behavior
    audio_event
    vfx_event
```

Avoid weapon-specific logic scattered through Player/Game/UI.

---

## 13. NORMAL ENEMY ROSTER

### Scout Drone
- Fast melee/dive bomber.
- Strafing.
- Telegraphs dive attacks.

### Shooter Drone
- Tactical ranged marksman.
- Maintains preferred range.
- Dual plasma attack pattern.

### Heavy Drone
- Armored bruiser.
- Passive damage reduction.
- High contact damage.

### Shield Elite
- Defensive support.
- Energy shield protecting nearby allies.

Boss enemies are NOT part of the target rebuild.

---

## 14. ENEMY AI ARCHITECTURE

Do not reproduce a giant monolithic enemy class.

Recommended:

```text
Enemy
 ├── stats
 ├── movement
 ├── weapon
 ├── health
 └── AI controller
```

AI controllers:

```text
EnemyAI
 ├── ScoutAI
 ├── ShooterAI
 ├── HeavyAI
 └── ShieldAI
```

Use explicit state machines for behavior where appropriate.

---

## 15. COMBAT SYSTEM

Core concepts:
- projectile collision
- damage resolution
- shields
- armor/damage reduction
- player damage
- enemy damage
- ability damage
- weapon special effects
- hit feedback
- death sequences

Recommended Godot structure:

```text
CombatSystem / CombatService
    apply_damage()
    resolve_hit()
    resolve_explosion()
    resolve_chain_lightning()
    resolve_emp()
```

Use collision layers/masks for filtering.

---

## 16. SPAWNING / ENCOUNTERS / PACING

The source contains dedicated concepts for:
- spawning
- encounter control
- combat pacing/director
- mission wave progression

Preserve these responsibilities.

Recommended:

```text
MissionController
    ↓
EncounterController
    ↓
Spawner
    ↓
Enemy instances
```

Do not put enemy spawning logic directly into the main scene everywhere.

---

## 17. CAMPAIGN STATE

The project was refactored toward a single authoritative campaign progression state.

Target conceptual structure:

```text
CampaignState
    current_mission
    completed_missions
    unlocked_missions
    completed_sectors
    unlocked_sectors
    campaign_completed
    new_game_plus_count
```

Only authoritative values should be stored.
Derived values should be calculated where practical.

Avoid duplicate mutable copies such as:

```text
Game.current_sector
MissionSystem.current_sector
ProgressionSystem.current_sector
```

all representing the same state.

---

## 18. CAMPAIGN STATE MUTATION

Prefer explicit domain operations:

```text
complete_mission()
unlock_mission()
complete_sector()
mark_campaign_complete()
start_new_game_plus()
```

Do not allow arbitrary systems to mutate campaign internals without control.

---

## 19. SCRAP ECONOMY

Core currency: **Scrap**.

Earned through:
- destroying enemy drones;
- completing missions;
- existing mission reward logic.

Historical upgrade categories:

| Upgrade | Historical Effect |
|---|---|
| Battery Capacity | +25 max HP per level |
| Thruster Agility | +5% flight speed per level |
| Weapon Systems | +5% damage multiplier per level |
| Hull Plating | +25 max HP per level |
| EMP Quick-Charger | Reduced EMP cooldown |
| Wingman Escort | Autonomous allied support drones |
| Tactical Cloak | Temporary defensive/stealth ability |

Use the current source as the authority for exact values.

---

## 20. WINGMAN SYSTEM

The game contains a concept of autonomous allied minidrones.

If active in the source, preserve:
- wingman spawning;
- support behavior;
- targeting/formation behavior;
- upgrade linkage.

Suggested Godot structure:

```text
Player
  └── WingmanManager
        ├── Wingman instances
        └── targeting/formation behavior
```

---

## 21. SAVE SYSTEM

Current project has:
- save slots;
- safe/atomic-style saving;
- corruption recovery;
- compatibility considerations;
- save/load orchestration.

Godot target:

```text
SaveController
    ↓
SaveStorage
```

Persist authoritative campaign/player/progression state, not duplicate derived state.

A JSON-style save format is acceptable.

Conceptual example:

```json
{
  "save_version": 1,
  "campaign": {},
  "player": {},
  "upgrades": {},
  "settings": {}
}
```

Do not invent unsupported fields.

---

## 22. INPUT ARCHITECTURE

Use Godot InputMap actions.

Recommended actions:

```text
move_up
move_down
move_left
move_right
fire_primary
fire_secondary
roll
emp
ultimate
next_weapon
previous_weapon
cloak
pause
confirm
cancel
fullscreen
```

Context matters:
- gameplay;
- menus;
- pause;
- mission result;
- settings.

Avoid ambiguous duplicate handling.

Historical keyboard contract:

```text
W/A/S/D or Arrows       movement
LMB / Space             primary fire
RMB                     secondary fire
Shift                   roll
E                       EMP
F / Q                   overdrive
C / K                   cloak
TAB                     next weapon
1-6                     weapon selection
ESC / P                 pause
F11                     fullscreen
Enter / Space           menu confirm
ESC                     menu back
```

Verify exact behavior against the current source during migration.

---

## 23. CONTROLLER SUPPORT

Historical support includes generic USB/PS2-style controllers and Xbox-style gamepads.

Godot should use abstract InputMap actions rather than hard-coding one controller family.

---

## 24. GAME STATES / SCREENS

Historical states include concepts around:
- main menu
- save selection
- drone selection
- sector selection
- mission briefing
- hangar
- settings
- custom difficulty
- controller binding/testing
- playing
- paused
- mission complete
- mission failed/game over
- victory

Boss-specific states are removed.

Recommended Godot scenes:

```text
Main.tscn
MainMenu.tscn
SaveSelect.tscn
CampaignSelect.tscn
MissionBriefing.tscn
Hangar.tscn
Gameplay.tscn
PauseMenu.tscn
MissionResult.tscn
Settings.tscn
```

---

## 25. CAMERA / RENDERING

Use Godot's:
- `Camera2D`
- `Sprite2D`
- `AnimatedSprite2D` where appropriate
- `CanvasLayer` for HUD
- particles/effects where appropriate

The source has a dedicated rendering layer and sprite caching concepts.
Do not build a custom software renderer in Godot.

---

## 26. UI

Existing UI concepts include:
- menus
- HUD
- health/resource display
- weapon display
- mission objectives
- mission results
- hangar upgrades
- settings
- save slots
- campaign navigation

Use:
- Control nodes;
- Containers;
- Theme resources;
- reusable UI scenes.

Do not create boss UI.
Do not create skin customization UI.

---

## 27. AUDIO

Existing concepts include:
- music
- SFX
- priority/volume management
- combat sound identity
- procedural sound generation

Godot target:
- `AudioStreamPlayer`
- audio buses
- centralized AudioManager
- `AudioStreamPlayer2D` where spatialization helps

Preserve weapon/enemy/UI/combat feedback identities.

---

## 28. VFX

Historical VFX concepts include:
- standard explosions;
- heavy explosions;
- shockwaves;
- hit feedback;
- player destruction effects.

Historical assets included:

```text
explosion_1.png
explosion_2.png
shockwave.png
```

Use the repository's actual assets as the import source.

---

## 29. PLAYER DEATH

Historical behavior included:
- approximately 1.4-second cinematic destruction;
- camera tracking;
- continuing audio;
- Mission Failed screen after destruction.

Preserve this feel if still active.

---

## 30. DIFFICULTY

Historical difficulty levels:

- Easy
- Normal
- Hard
- Nightmare

Keep difficulty data-driven.
Preserve current modifiers.
Do not invent additional levels.

---

## 31. ACHIEVEMENTS

An achievements/progression concept exists in the source.

Preserve active achievement behavior if it remains implemented.

Do not add new achievements during the port.

---

## 32. NEW GAME PLUS

An NG+ concept exists.

Preserve it if active in the current source.

CampaignState should own the authoritative NG+ count/state.

Do not create a second independent NG+ state.

---

## 33. REMOVED SYSTEMS

The final target must NOT contain:

```text
BossSystem
Boss battles
Boss health bars
Boss phases
Boss rewards
Boss-specific campaign progression

Drone skin selection
Drone skin switching
Skin cycling
Skin inventory
Skin unlocks
Skin-specific input
```

Stale save fields should be ignored safely.

---

## 34. TARGET GODOT ARCHITECTURE

Recommended:

```text
res://
├── project.godot
├── main/
│   └── main.tscn
│
├── core/
│   ├── game_state_manager.gd
│   ├── campaign_state.gd
│   ├── save_controller.gd
│   └── game_context.gd
│
├── gameplay/
│   ├── player/
│   ├── enemies/
│   ├── weapons/
│   ├── abilities/
│   ├── missions/
│   ├── encounters/
│   ├── spawning/
│   └── progression/
│
├── systems/
│   ├── combat/
│   ├── audio/
│   ├── save/
│   ├── input/
│   └── achievements/
│
├── ui/
│   ├── menus/
│   ├── hud/
│   ├── hangar/
│   ├── mission/
│   └── settings/
│
├── data/
│   ├── weapons/
│   ├── enemies/
│   ├── missions/
│   ├── drone_classes/
│   └── upgrades/
│
├── art/
├── audio/
├── vfx/
└── tests/
```

This is a target architecture, not a requirement to copy filenames exactly.

---

## 35. GODOT SCENE MODEL

Gameplay scene:

```text
Gameplay
 ├── World
 ├── Player
 ├── Enemies
 ├── Projectiles
 ├── Pickups
 ├── Effects
 ├── Camera2D
 └── HUD
```

Use scenes/resources for reusable entities and definitions.

---

## 36. ARCHITECTURAL PRINCIPLES

1. One source of truth for campaign progression.
2. Composition root creates concrete systems.
3. Controllers do not depend on the entire Game object.
4. Gameplay does not live inside UI scenes.
5. UI does not directly mutate progression internals.
6. Static definitions are data-driven.
7. Runtime state is explicit.
8. Avoid circular dependencies.
9. Prefer signals/events for decoupled notifications.
10. Avoid God Objects.
11. Keep systems testable.
12. Keep save data stable/migratable.
13. Do not over-engineer.

---

## 37. PERFORMANCE TARGET

Primary target:

**60 FPS at 1280×720 on a normal Windows PC.**

Stress-test:
- many enemies;
- many projectiles;
- explosions;
- particles;
- chain lightning;
- missiles;
- intense encounters.

Profile before optimizing.

---

## 38. TEN-STAGE PRODUCTION ROADMAP

The development roadmap is intentionally limited to these ten stages:

1. Refactor Game God Object.
2. Unify progression/state.
3. Remove legacy and duplicate systems.
4. Refactor Player responsibilities.
5. Refactor Enemy/AI responsibilities.
6. Consolidate Weapon/Ability architecture.
7. Harden Save System for production.
8. Performance and combat scalability.
9. Production QA / E2E testing.
10. Production build and release pipeline.

No feature expansion should happen before completing these ten stages.

---

## 39. CURRENT SOURCE STATUS

### Phase 1
Baseline: `45209aa`

Goal:
- reduce Game God Object;
- introduce orchestration/controllers;
- preserve gameplay.

Reported test result:
`725 passed`

### Phase 2
Commit reviewed: `a769c8b`

Goal:
- unify campaign/progression state.

During manual validation, keyboard regressions were noticed.

This means input must be validated behaviorally rather than relying only on automated tests.

### Pending targeted cleanup
The intended product direction includes removal of:
- Boss system;
- Drone skin switching.

---

## 40. MIGRATION STRATEGY TO GODOT

Do NOT translate Python line-for-line.

Instead:

```text
Pygame implementation
        ↓
Extract gameplay contracts
        ↓
Implement data definitions as Godot Resources
        ↓
Create Godot scenes/nodes
        ↓
Implement gameplay controllers/services
        ↓
Implement InputMap
        ↓
Implement SaveController
        ↓
Implement UI
        ↓
Run behavior regression
        ↓
Production hardening
```

The target is a clean Godot architecture, not a Python-shaped Godot project.

---

## 41. WHAT MUST BE PRESERVED

Preserve:
- top-down drone combat;
- responsive movement;
- mouse aiming;
- multiple drone classes;
- weapon diversity;
- mission-based campaign;
- enemy waves;
- tactical abilities;
- Scrap economy;
- Hangar upgrades;
- save slots;
- campaign progression;
- difficulty levels;
- controller support;
- combat VFX/SFX;
- player death sequence;
- mission results;
- NG+ if active.

---

## 42. WHAT MUST NOT BE PRESERVED

Do not reproduce:
- God Object structure;
- duplicated progression state;
- controller → entire Game dependency;
- obsolete legacy code;
- boss system;
- drone skins;
- scattered hard-coded weapon logic;
- unnecessary compatibility layers.

---

## 43. SOURCE-OF-TRUTH RULE

When this document and an old README conflict:

**This document wins for product direction.**

When this document omits a numeric or low-level implementation detail:

**The current source code wins.**

When both are unclear:

**Do not invent new gameplay.**

---

## 44. ANTIGRAVITY HANDOFF INSTRUCTION

Use this document as the product and architecture handoff.

Recommended instruction to Antigravity:

> Build a Godot 4.x version of Drone Hunter 2D from this specification and the existing repository assets/code as reference. Preserve gameplay contracts and content explicitly marked as active. Do not recreate bosses or drone skins. Do not copy the old Pygame architecture mechanically. Use Godot scenes, Resources, InputMap, signals, and modular controllers/services. When a numeric gameplay value is not specified here, inspect the current repository rather than inventing a value.

---

## 45. END STATE

The desired Godot product:

```text
Drone Hunter 2D
    ↓
Clean Godot architecture
    ↓
Data-driven content
    ↓
Responsive 2D combat
    ↓
25-mission campaign
    ↓
5 drone classes
    ↓
11-weapon historical arsenal
    ↓
Normal enemy roster
    ↓
Abilities
    ↓
Scrap + upgrades
    ↓
Save slots
    ↓
Controller support
    ↓
Production-quality UI/audio/VFX
    ↓
Windows release
```

with:

```text
NO BOSSES
NO DRONE SKINS
NO GOD OBJECT
NO DUPLICATED CAMPAIGN STATE
```

**Final instruction:** Rebuild the existing game faithfully first. Do not turn the migration into a feature-expansion project.
