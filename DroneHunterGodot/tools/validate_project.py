#!/usr/bin/env python3
"""
Drone Hunter 2D - Godot 4.3 Project Foundation Validator
Verifies project structure, configuration, asset inventory, and architectural boundaries.
"""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_DIRS = [
    "scenes",
    "scenes/main",
    "scenes/player",
    "scenes/enemies",
    "scenes/weapons",
    "scenes/missions",
    "scenes/ui",
    "scenes/world",
    "scripts",
    "scripts/core",
    "scripts/systems",
    "resources",
    "resources/drones",
    "resources/weapons",
    "resources/enemies",
    "resources/missions",
    "resources/upgrades",
    "resources/difficulty",
    "assets",
    "assets/player",
    "assets/drones",
    "assets/enemies",
    "assets/projectiles",
    "assets/weapons",
    "assets/backgrounds",
    "assets/environment",
    "assets/vfx",
    "assets/audio",
    "docs",
    "tools"
]

REQUIRED_FILES = [
    "project.godot",
    "scenes/main/Main.tscn",
    "scripts/core/game_manager.gd",
    "scripts/core/game_state_manager.gd",
    "scripts/core/campaign_state.gd",
    "scripts/systems/audio_manager.gd",
    "scripts/systems/save_manager.gd",
    "resources/drones/drone_class_definition.gd",
    "resources/weapons/weapon_definition.gd",
    "resources/enemies/enemy_definition.gd",
    "resources/missions/mission_definition.gd",
    "resources/upgrades/upgrade_definition.gd",
    "resources/difficulty/difficulty_definition.gd",
    "tools/asset_inventory.json",
    "docs/GODOT_DEVELOPMENT_RULES.md",
    "README.md"
]

REQUIRED_INPUT_ACTIONS = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "fire_primary",
    "fire_secondary",
    "roll",
    "emp",
    "ultimate",
    "cloak",
    "next_weapon",
    "previous_weapon",
    "pause",
    "confirm",
    "cancel",
    "fullscreen"
]

def validate_project() -> bool:
    print(f"=== Validating Godot 4.3 Foundation at: {PROJECT_ROOT} ===")
    errors = []

    # 1. Check directories
    for d in REQUIRED_DIRS:
        dp = os.path.join(PROJECT_ROOT, d)
        if not os.path.isdir(dp):
            errors.append(f"Missing directory: {d}")

    # 2. Check files
    for f in REQUIRED_FILES:
        fp = os.path.join(PROJECT_ROOT, f)
        if not os.path.isfile(fp):
            errors.append(f"Missing file: {f}")

    # 3. Validate project.godot content & InputMap
    pg_path = os.path.join(PROJECT_ROOT, "project.godot")
    if os.path.isfile(pg_path):
        with open(pg_path, "r", encoding="utf-8") as pg_file:
            pg_content = pg_file.read()

        for action in REQUIRED_INPUT_ACTIONS:
            if f"{action}=" not in pg_content:
                errors.append(f"Missing InputMap action in project.godot: {action}")

        if "run/main_scene=\"res://scenes/main/Main.tscn\"" not in pg_content:
            errors.append("project.godot does not configure Main.tscn as main scene")

    # 4. Check asset_inventory.json
    inv_path = os.path.join(PROJECT_ROOT, "tools", "asset_inventory.json")
    if os.path.isfile(inv_path):
        try:
            with open(inv_path, "r", encoding="utf-8") as inv_file:
                inv_data = json.load(inv_file)
            if not isinstance(inv_data, list) or len(inv_data) == 0:
                errors.append("asset_inventory.json is empty or invalid format")
            else:
                print(f"[OK] asset_inventory.json validated ({len(inv_data)} entries)")
        except Exception as e:
            errors.append(f"Failed to parse asset_inventory.json: {e}")

    # 5. Check for accidental Boss / Skin runtime inclusion in active assets
    active_assets_dir = os.path.join(PROJECT_ROOT, "assets")
    for root, dirs, files in os.walk(active_assets_dir):
        for f in files:
            p_lower = f.lower()
            rel = os.path.relpath(os.path.join(root, f), active_assets_dir).lower()
            if "boss" in rel:
                errors.append(f"Forbidden Boss asset found in active assets: {rel}")
            if "skin" in rel:
                errors.append(f"Forbidden Skin asset found in active assets: {rel}")

    if errors:
        print("\n[FAILED] VALIDATION FAILED with errors:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("\n[SUCCESS] VALIDATION PASSED - All structural, asset, architectural, and input checks succeeded!")
    return True

if __name__ == "__main__":
    success = validate_project()
    sys.exit(0 if success else 1)
