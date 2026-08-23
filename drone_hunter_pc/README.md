# 🛸 Drone Hunter 2D — PC Edition

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/engine-pygame--ce%202.5%2B-green.svg)](https://pyga.me/)
[![Tests](https://img.shields.io/badge/tests-604%20passing-brightgreen.svg)](#-automated-tests)
[![Controller](https://img.shields.io/badge/controller-Generic%20USB%20%7C%20Xbox%20%7C%20PS2%20Gamepad-purple.svg)](#-controls-reference)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)
[![Status](https://img.shields.io/badge/status-Production%20Asset%20Integrated-purple.svg)](#)

**Drone Hunter 2D** is a high-performance industrial sci-fi tactical top-down drone combat game built with Python and `pygame-ce`.

Fight through **5 industrial sectors**, complete **25 tactical combat missions**, defeat **5 sector dreadnought bosses** and the final **Drone Overlord**, upgrade your chassis in the Hangar, and master an arsenal of 11 weapons with physical audio, visual identities, and **first-class controller/gamepad support**.

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install pygame-ce>=2.5.0 pytest>=7.0.0
# or
pip install -r drone_hunter_pc/requirements.txt
```

### Launch the Game
```bash
python drone_hunter_pc/main.py
```

### Run All Tests (555 tests)
```bash
pytest drone_hunter_pc/tests
```

---

## 🎮 Controls Reference

| Action | Keyboard / Mouse | Generic USB / PS2 Joystick | Xbox Gamepad |
|:---|:---|:---|:---|
| **Flight Movement / Thrust** | `W A S D` / Arrow Keys | **D-Pad / Left Stick** | Left Analog Stick |
| **Aiming / Crosshair Direction** | Mouse Cursor Aim | **Right Analog Stick / Crosshair Aim** | Right Analog Stick |
| **Primary Weapon Fire** | `LMB` / `Spacebar` | **Cross / X** (Button 2) | **RT** (Right Trigger) |
| **Secondary Weapon Fire**| `RMB` | **Square / ▢** (Button 3) | **LT** (Left Trigger) |
| **Barrel Roll / Dodge** | `Left Shift` / `Right Shift` | **Triangle / △** (Button 0) | **A** Button |
| **EMP Shockwave Pulse** | `E` | **Circle / O** (Button 1) | **X** Button |
| **Next Weapon** | `TAB` / `1`–`6` | **Front Top (Tap)** (Buttons 4/5) | **RB** (Right Bumper) |
| **Previous Weapon** | `Mouse Wheel Down` | **Front Top (Hold $\ge 0.4s$)** | **LB** (Left Bumper) |
| **Tactical Cloak** | `C` / `K` | **Front Bottom (Tap)** (Buttons 6/7) | **R3** (Right Stick Click) |
| **Cycle Drone Class** | `C` (Hangar) | **Front Bottom (Hold $\ge 0.4s$)** | **L3** (Left Stick Click) |
| **Tactical Overdrive** | `F` / `Q` | **SELECT** (Button 8) | **Y** Button |
| **Pause / Resume** | `ESC` / `P` | **START (Tap)** (Button 9) | **START** / **MENU** Button |
| **Fullscreen Toggle** | `F11` | **START (Hold $\ge 1.0s$)** | — |
| **Menu D-Pad Navigation** | Arrow Keys / `W A S D` | **D-Pad (Up / Down / Left / Right)** | D-Pad |
| **Menu Confirm / Select** | `Enter` / `Spacebar` | **Cross / X** (Button 2) | **A** Button |
| **Menu Cancel / Back** | `ESC` | **Circle / O** (Button 1) | **B** Button |

---

## 🛸 Player Combat Drone Platforms

| Class | Platform | Archetype | Default Weapon | Special Trait |
|---|---|---|---|---|
| **Class 0** | **Striker** | Balanced Generalist | Pulse Cannon | Dual wing mounts, versatile kinetic profile |
| **Class 1** | **Phantom** | High-Agility Interceptor | Rapid Autocannon | +15% Speed, rapid fire-rate, tight turning |
| **Class 2** | **Titan** | Heavy Armored Gunship | Heavy Plasma Orb | +50 Max HP, +2 Armor, high recoil absorption |
| **Class 3** | **Velocity** | Advanced Speed Scout | Arc Lightning Tesla | +25% Speed, instantaneous engine response |
| **Class 4** | **Command** | Dreadnought Destroyer | Railgun Accelerator | Maximum firepower, dual missile pod bays |

---

## ⚡ Combat Arsenal & Real Production Assets

Every weapon utilizes canonical production PNG assets from `assets/sprites/weapons/` with custom projectile kinematics, muzzle flashes, and sound identities:

| # | Weapon | Asset | Behavior & Characteristics |
|---|---|---|---|
| 1 | **Pulse Cannon** | `laser_pulse.png` | Rapid twin plasma bolts from dual forward mounts |
| 2 | **Rapid Autocannon** | `laser_pulse.png` | Alternating high-cyclic kinetic fire |
| 3 | **Scatter Shotgun** | `laser_scatter.png` | 5-pellet wide spread burst for swarm suppression |
| 4 | **Homing Missiles** | `missile.png` | Target-locking heavy ordnance with rocket trail |
| 5 | **Missile Barrage** | `missile.png` | 4-missile salvo launched from dual wing pods |
| 6 | **Heavy Plasma Orb** | `laser_beam.png` | High-damage slow plasma sphere with area shockwave |
| 7 | **Railgun Accelerator**| `laser_beam.png` | Supersonic slug piercing through multiple targets |
| 8 | **Plasma Laser Beam** | `laser_beam.png` | Continuous piercing directed-energy beam |
| 9 | **Arc Lightning Tesla**| `tesla_orb.png` | Chain lightning arcing between clustered enemies |
| 10| **Cluster Torpedo** | `cluster_torpedo.png`| Heavy ordnance splitting into 6 explosive bomblets |
| 11| **EMP Shockwave** | `tesla_orb.png` | 360-degree electromagnetic pulse disabling enemy systems |

---

## 💥 Production VFX & Realistic Audio Synthesis

- **Real Production VFX Overlays (`assets/sprites/vfx/`)**:
  - `explosion_1.png`: Standard enemy death & light kinetic impacts (scale 78–88).
  - `explosion_2.png`: Heavy enemy death, boss destruction, player death, and heavy ordnance impacts (scale 110–210).
  - `shockwave.png`: Expanding blastwave overlays for heavy explosions and EMP blasts (radius up to 260px).
- **Physical Multi-Harmonic Sound Synthesis**:
  - Procedural sound generator using dynamic 1-pole and 2-pole low-pass filters (1.9kHz down to 65Hz) and deep sub-bass frequencies (20Hz–55Hz).
  - Full stereo interleaved 16-bit PCM buffer playback dynamically matching hardware mixer rates.
- **Deferred Player Destruction**:
  - Full 1.4-second cinematic explosion animation on player destruction with active camera tracking and continuous audio before displaying the Mission Failed screen.

---

## 👾 Enemy Roster & Boss Encounters

| Enemy | Role | Combat Behavior |
|---|---|---|
| **Scout Drone** | Melee Dive-Bomber | Fast strafing, telegraph indicator, and high-speed dive attacks |
| **Shooter Drone** | Tactical Marksman | Preferred distance management and dual plasma bursts |
| **Heavy Drone** | Armored Bulldozer | 20% passive armor damage reduction, high contact damage |
| **Shield Elite** | Defensive Barrier | Orbiting energy shield absorbing damage for nearby allies |
| **Assembly Warden** | Sector 1 Boss | Radial energy bursts and spread barrages |
| **Core Executor** | Sector 2 Boss | Stealth relocation and sweeping piercing laser beams |
| **Reactor Titan** | Sector 3 Boss | Expanding energy shockwaves and escort drone deployments |
| **Defense Commander**| Sector 4 Boss | Targeted missile salvos and aggressive high-speed charges |
| **Drone Overlord** | Final Sector 5 Boss| 4-phase endgame confrontation with escalating attack patterns |

---

## 🌌 Campaign — 5 Sectors × 5 Missions (25 Missions)

| Sector | Name | Environment | Boss |
|---|---|---|---|
| **Sector 1** | **CYBER FACTORY** | Industrial drone assembly plant | Assembly Warden |
| **Sector 2** | **CORE SECTOR** | Heavily fortified reactor core complex | Core Executor |
| **Sector 3** | **REACTOR ZONE** | Volatile energy conduits & plasma arrays | Reactor Titan |
| **Sector 4** | **DEFENSE GRID** | Automated perimeter defense network | Defense Commander |
| **Sector 5** | **DRONE COMMAND** | Overlord primary command fortress | Drone Overlord |

### Objective Types
- **Destroy All** — Eliminate all hostile waves in the sector zone.
- **Survive** — Endure aggressive swarm assault for a set duration (45s, 75s, 90s).
- **Complete Encounters** — Defeat multi-wave tactical combat encounters.

---

## 🛠️ Hangar Bay Upgrades & Economy

Earn **Scrap** by neutralizing enemy drones and completing sector missions. Invest in the Hangar:

| Upgrade | Effect |
|---|---|
| 🔋 **Battery Capacity** | +25 Max HP per level (max level 5) |
| 🚀 **Thruster Agility** | +5% Flight speed per level (max level 5) |
| ⚡ **Weapon Systems** | +5% Damage multiplier per level (max level 5) |
| 🛡️ **Hull Plating** | +25 Max HP per level (max level 5) |
| ⚡ **EMP Quick-Charger** | Reduced EMP cooldown duration |
| 🛸 **Wingman Escort** | Autonomous allied minidrone wingmen |
| 👻 **Tactical Cloak** | Stealth cloak ability (`K`) granting temporary invulnerability |

---

## 🧪 Automated Test Suite (435 Passing)

The project includes an exhaustive automated test suite with **435 tests passing with 100% success**:

```bash
pytest drone_hunter_pc/tests
```

```
======================= 435 passed in 74.66s (0:01:14) ========================
```

- `test_real_asset_integration.py` (15 tests): Production weapon and VFX PNG asset integrity, telemetry, forward aim math, and deferred death sequence.
- `test_phase10_audio.py` & `test_phase10_5_combat_overhaul.py` (27 tests): Audio manager priority channels, sound synthesis, and combat feedback.
- `test_weapon_identity.py` (25 tests): Weapon damage, fire-rates, and projectile behaviors.
- `test_phase9_combat_feedback.py` (49 tests): Combat VFX, overlays, and hit feedback.
- `test_phase8_assets.py` & `test_phase8_missions_hardening.py` (314 tests): Asset integrity, mission logic, and wave lifecycles.
- `test_game_systems.py`, `test_phase1_flight.py` – `test_phase7_release.py`: Core kinematics, progression, and bosses.
