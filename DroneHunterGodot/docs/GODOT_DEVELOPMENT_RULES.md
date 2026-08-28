# Drone Hunter 2D — Godot 4.3 Development Rules

This document defines the strict architectural principles, scope boundaries, and development rules for the **Drone Hunter 2D** Godot 4.3 project.

---

## 1. Core Principles

- **Engine Version**: Godot 4.3 (Strict).
- **Target Platform**: Windows Desktop (2D).
- **Base Resolution**: 1280 × 720 (Canvas Items scale mode, Aspect Keep).
- **Source of Truth**: The Pygame PC project (`drone_hunter_pc/`) is reference-only for gameplay behavior, formulas, and assets.
- **Independence**: Never create Python/Pygame runtime dependencies or reuse the old `DroneStrike` Godot project.

---

## 2. Strict Architectural Boundaries

- **No Boss Battles / Systems**: Boss encounters, Boss HUD, and Boss logic are strictly excluded from the active product.
- **No Drone Skin System**: Custom cosmetics/skin switching are excluded from the active product. The game features five distinct, fixed drone platform classes.
- **No God Objects**: Avoid monolithic scripts. Separate concerns across `GameManager`, `GameStateManager`, `CampaignState`, `AudioManager`, and specialized subsystem nodes.
- **Autoloads**: Use Autoloads sparingly only for true global composition roots (`GameManager`).
- **Data-Driven Architecture**: Use typed `Resource` classes (`DroneClassDefinition`, `WeaponDefinition`, `EnemyDefinition`, `MissionDefinition`, `UpgradeDefinition`, `DifficultyDefinition`) for all static game data.
- **Entities as Scenes**: Encapsulate reusable visual and physical entities as dedicated `.tscn` scenes.

---

## 3. Input & Controls

- Map all player actions through Godot's `InputMap`.
- Support both Keyboard/Mouse and Gamepad controls uniformly.
- Do not hardcode raw key codes in entity physics scripts.

---

## 4. Save & Persistence

- Save files must be stored in Godot's sandbox path (`user://`).
- Use atomic serialization with `save_version: 1`.
- Do not mirror Python file-system paths.
