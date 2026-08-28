# Drone Hunter 2D — Godot 4.3 Engine Project

**Drone Hunter 2D** is a fast-paced sci-fi tactical arcade space shooter built with Godot 4.3.

---

## Key Characteristics

- **Engine Version**: Godot 4.3 Stable
- **Target Platform**: Windows Desktop
- **Perspective**: Top-down / 2D Tactical Space Combat
- **Resolution**: 1280 × 720 Virtual Viewport
- **Reference**: Pygame Reference Project (`drone_hunter_pc/`)

---

## Architectural Exclusions

- **Boss Battles Excluded**: Boss systems and encounters are completely excluded from active gameplay.
- **Drone Skins Excluded**: Cosmetic skin switching is excluded. The game features 5 distinct drone platform classes:
  1. Striker (Balanced Interceptor)
  2. Interceptor / Phantom (High Agility & Speed)
  3. Assault / Titan (Heavy Armor & Firepower)
  4. Arc / Velocity (Energy Weapons & Shielding)
  5. Command (Escort Drone Tactics)

---

## Project Structure

```text
DroneHunterGodot/
├── project.godot
├── scenes/
│   ├── main/          # Application entry point
│   ├── player/        # Player drone scenes
│   ├── enemies/       # Enemy archetypes
│   ├── weapons/       # Projectiles & weapons
│   ├── missions/      # Mission arenas & objectives
│   ├── ui/            # HUD and menus
│   └── world/         # Parallax backgrounds & obstacles
├── scripts/
│   ├── core/          # Game & State managers, Campaign state
│   └── systems/       # Audio, Save, Combat subsystems
├── resources/         # Typed Resource definitions
├── assets/            # Active production art & audio assets
├── docs/              # Architectural rules & specifications
└── tools/             # Validation & migration utilities
```

---

## Validating the Project

Run the validator:

```bash
python tools/validate_project.py
```
