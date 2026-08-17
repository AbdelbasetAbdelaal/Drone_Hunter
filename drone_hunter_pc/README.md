# 🖥️ Drone Hunter (PC Edition)

Clean, high-performance, modular **2D Top-Down Drone Combat Game** built with Python & Pygame.

---

## 🎮 How to Run

From Command Prompt (`cmd`):
```cmd
cd /d d:\Drone_Hunter
python drone_hunter_pc/main.py
```

From PowerShell / Terminal:
```powershell
python drone_hunter_pc/main.py
```

Run Automated Test Suite:
```bash
python drone_hunter_pc/tests/test_game_systems.py
```

---

## 🏗️ Architecture Overview

```
drone_hunter_pc/
├── main.py                     # Minimal startup script (42 lines)
├── save_data_pc.json           # Atomic persistent progress data
├── tests/
│   └── test_game_systems.py    # Automated test suite (9 test suites)
└── src/
    ├── core/                   # Game engine, State Machine, Context, Clock
    │   ├── game.py
    │   ├── game_state.py
    │   ├── game_context.py
    │   └── clock.py
    ├── data/                   # Centralized settings & game data catalogs
    │   ├── settings.py
    │   └── game_data.py
    ├── entities/               # 2D Sprite Entities
    │   ├── player.py
    │   ├── enemy.py
    │   ├── boss.py
    │   ├── bullet.py
    │   ├── powerup.py
    │   ├── obstacle.py
    │   └── hazard.py
    ├── systems/                # Core Gameplay Systems
    │   ├── combat_system.py
    │   ├── spawn_system.py
    │   ├── progression_system.py
    │   ├── difficulty_system.py
    │   └── save_system.py
    ├── rendering/              # 2D Graphics & Visual Effects
    │   ├── renderer.py
    │   ├── background.py
    │   └── particles.py
    ├── ui/                     # Holographic HUD & Interfaces
    │   ├── hud.py
    │   ├── menus.py
    │   ├── hangar.py
    │   └── font_manager.py
    └── audio/                  # Procedural Sound Synthesizer & Caching
        ├── sound_synth.py
        └── audio_manager.py
```

---

## 🕹️ Controls Reference

- **Fly / Maneuver**: `W`, `A`, `S`, `D` or `Arrow Keys`
- **Aim & Shoot**: Mouse to aim, **Left Click** to fire
- **Select Weapon**: `1` - `6`, `TAB`, or **Mouse Wheel**
- **Overdrive Ultimate**: `F`, `Q`, or **Middle Click**
- **EMP Shockwave**: `E` or **Right Click**
- **Evasive Roll**: `Left Shift` / `Right Shift`
- **Tactical Cloak**: `K`
- **Change Skin**: `C`
- **CRT Scanlines**: `F2`
- **Pause / Menu**: `ESC` or `P`
