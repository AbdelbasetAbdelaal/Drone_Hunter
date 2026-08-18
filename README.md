# 🛸 Drone Hunter: Sci-Fi Arcade Edition

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/engine-Pygame--CE%20%2F%20Pygame-green.svg)](https://pyga.me/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-orange.svg)](#)

**Drone Hunter** is an action-packed 2D sci-fi arcade drone combat game featuring multi-weapon loadouts, tactical abilities (Overdrive, Cloak, EMP, Evasive Barrel Roll), dynamic boss encounters, wingman support drones, hangar customizations, and responsive flight kinematics.

---

## 🎮 Quick Start & Running the Game

### Prerequisites
- Python 3.10 or higher
- `pygame` or `pygame-ce`

```bash
pip install pygame-ce
```

### Run from Command Prompt (`cmd` / Windows Terminal)
```cmd
cd /d d:\Drone_Hunter
python drone_hunter_pc/main.py
```

### Run Mobile Simulation (On-Screen Touch Joystick Edition)
```cmd
cd /d d:\Drone_Hunter
python drone_hunter_mobile/main.py
```

---

## 🕹️ Controls & Keybindings

| Action | PC Controls | Description |
| :--- | :--- | :--- |
| **Flight Movement** | `W`, `A`, `S`, `D` or `Arrow Keys` | Full 360° thruster flight with inertia damping |
| **Aim & Shoot** | `Mouse Aim` + `Left Mouse Button` | Fire active weapon towards crosshair |
| **Switch Weapons** | `1` - `6`, `TAB`, or `Mouse Wheel` | Instant loadout swap across 6 unlocked weapons |
| **Overdrive Ultimate** | `F`, `Q`, or `Middle Mouse Click` | 5s hyper-fire mode, increased damage & invulnerability |
| **EMP Shockwave** | `E` or `Right Mouse Button` | Screen-clearing EMP blast that destroys projectiles |
| **Evasive Barrel Roll** | `Left Shift` / `Right Shift` | High-speed directional dash with i-frames |
| **Tactical Cloak** | `K` | Invisibility cloak against enemy target tracking |
| **Drone Skin Customizer** | `C` | Real-time drone chassis theme cycler (6 skins) |
| **Pause & Settings** | `ESC` or `P` | Access audio toggles, CRT filters, and difficulty |

---

## ⚡ Arsenal & Weapons

1. **Pulse Cannon (⚡)**: High-speed twin plasma bolts with rapid fire.
2. **Scatter Shotgun (💥)**: Multi-pellet spread shot for clearing close-range drone swarms.
3. **Homing Missiles (🚀)**: High-yield ordnance that locks on and tracks nearby hostile targets.
4. **Plasma Laser Beam (⚡)**: Continuous piercing beam cutting through all targets in a line.
5. **Arc Lightning Tesla (🌩️)**: High-voltage electrical bolts that chain across groups of enemies.
6. **Cluster Torpedo (💣)**: Heavy ballistic warhead that splits into 6 explosive bomblets.

---

## 👾 Enemy Drones & Boss Dreadnoughts

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
| **Sky Dreadnought Boss** | 360° radial spiral bullet rings & enrage phase |
| **Stealth Mirage Boss** | Cloaks invisibly and relocates across the battlescape |
| **EMP Disrupter Boss** | Emits expanding weapon-jamming EMP shockwave rings |
| **Colossus Titan Mech** | 3-Phase Overclock berserk titan with orbital satellite shields |

---

## 🌌 Campaign Sectors

- **Sector 1: Megacity Skyline** (Neon rooftop megacity with heavy rain & drone patrols)
- **Sector 2: Cyber Factory Core** (Automated foundry with molten hazards & defense grids)
- **Sector 3: Orbital Space Citadel** (Deep space fortress with asteroid fields & meteor showers)
- **Sector 4: Stormy Ocean Battlescape** (Raging tempest ocean with naval warship salvos)
- **Sector 5: Neon Sun Desert Wasteland** (Scorching dune wasteland guarded by the Colossus Titan)

---

## 📁 Repository Structure

```
Drone_Hunter/
├── README.md                     # Main project documentation
├── drone_hunter_pc/              # PC Edition (Desktop-optimized)
│   ├── main.py                   # Clean entry point
│   ├── save_data_pc.json         # Persistent atomic save data (coins, unlocks, upgrades)
│   ├── tests/                    # Automated unit, integration & runtime smoke tests
│   │   ├── test_game_systems.py
│   │   └── test_runtime_smoke.py
│   └── src/
│       ├── core/                 # Engine loop, State machine, Context container, Clock
│       ├── data/                 # Display settings, authoritative weapon/sector catalogs
│       ├── entities/             # 2D Player, enemies, bosses, bullets, powerups, obstacles, hazards
│       ├── systems/              # Combat collisions, wave manager, save/load, difficulty, progression
│       ├── rendering/            # Parallax backgrounds, particle engine, scanline renderer
│       ├── ui/                   # HUD, minimap, hangar upgrade store, menus, font manager
│       └── audio/                # Sound synthesis & audio cache manager
└── drone_hunter_mobile/          # Mobile Edition (Touch controls, Android APK build)
    ├── main.py                   # Mobile game loop with touch input overlay
    ├── buildozer.spec            # Android APK build configuration
    └── src/                      # Mobile game logic modules
```

---

## 🛠️ Upgrades & Customization in Hangar

Earn **Gold Scrap** by defeating enemies and clearing waves. Visit the **Hangar** between stages to upgrade:
- 🔋 **Max Battery Capacity**: Increases maximum drone hull integrity.
- 🚀 **Thruster Agility**: Enhances flight speed and acceleration.
- ⚡ **Cannon Fire-Rate**: Reduces cooldowns across all weapons.
- 💥 **EMP Shockwave Charger**: Accelerates EMP recharge speed.
- 🛸 **Wingman Minidrones**: Deploys automated escort drones that auto-fire on targets.
- 👻 **Tactical Cloaking Unit**: Grants tactical invisibility.
- 🚀 **Missiles / Beam / Tesla / Cluster**: Unlock advanced heavy weapon ordnance.
- 🎨 **Drone Skins**: Select from *Platinum, Cyberneon, Sovereign, Crimson, Void Stealth, and Solar Flare*.

---

## 📜 License
Developed with Python & Pygame. Free to play, modify, and distribute.
