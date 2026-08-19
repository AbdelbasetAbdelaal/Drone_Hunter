# 🛸 Drone Hunter 2D — PC Edition (v1.0.0)

**Drone Hunter 2D** is a fast-paced, high-performance tactical sci-fi 2D top-down drone combat game developed with Python and `pygame-ce`.

Fight through 5 distinct industrial sectors, complete 25 combat missions, engage 5 major command bosses with multi-phase attack patterns, upgrade your combat drone in the Hangar, and conquer the Drone Overlord in the final endgame confrontation.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13, 3.14)
- `pip install -r requirements.txt` (or `pip install pygame-ce pytest`)

### 2. Launch the Game
From the project root:
```bash
python drone_hunter_pc/main.py
```
Or from inside `drone_hunter_pc/`:
```bash
python main.py
```

### 3. Run Automated Tests
```bash
pytest drone_hunter_pc/tests
```

---

## 🕹️ Controls Reference

| Action | Primary Input | Secondary / Alternate |
| :--- | :--- | :--- |
| **Movement / Thrust** | `W`, `A`, `S`, `D` | `Arrow Keys` |
| **Aim** | `Mouse Pointer` | *(Screen-mapped crosshair)* |
| **Primary Fire** | `Left Mouse Button` | — |
| **Weapon Selection** | `1` to `6` | `TAB` / `Mouse Wheel` |
| **EMP Blast** | `E` | `Right Mouse Button` |
| **Overdrive Mode** | `F` | `Q` / `Middle Mouse Button` |
| **Evasive Barrel Roll** | `Left Shift` | `Right Shift` |
| **Tactical Cloak** | `K` | — |
| **Cycle Drone Skin** | `C` | *(Hangar Customizer)* |
| **Pause / Resume** | `ESC` | `P` / `SPACE` (in paused state) |
| **Fullscreen Toggle** | `F11` | — |
| **Sector Map** | `M` | *(Menu button)* |
| **Hangar Bay** | `H` | *(Menu button)* |
| **Quick Quit** | `Q` | *(Menu button)* |

---

## 🌌 Campaign & Mission Structure

The campaign spans **5 Sectors** and **25 Combat Missions**:

1. **Sector 1 — Assembly Perimeter** (Missions `S1_M1` to `S1_M5`)  
   *Boss: Assembly Warden*
2. **Sector 2 — Industrial Core** (Missions `S2_M1` to `S2_M5`)  
   *Boss: Core Executor*
3. **Sector 3 — Reactor District** (Missions `S3_M1` to `S3_M5`)  
   *Boss: Reactor Titan*
4. **Sector 4 — Defense Matrix** (Missions `S4_M1` to `S4_M5`)  
   *Boss: Defense Commander*
5. **Sector 5 — Command Citadel** (Missions `S5_M1` to `S5_M5`)  
   *Final Boss: Drone Overlord (4-Phase Endgame Encounter)*

### Mission Types:
- **Elimination**: Clear all hostile drone waves within the arena.
- **Survive**: Endure relentless enemy swarms for the required duration.
- **Target Priority**: Eliminate specific high-value enemy targets.
- **Data Recovery**: Collect operational scrap caches under active fire.
- **Boss Assassination**: Defeat the sector command unit.

---

## 🛠️ Drone Upgrades & Hangar

Earn **Scrap** from destroyed enemies and mission rewards to upgrade 4 core subsystems in the Hangar:
- **Hull Integrity**: Increases maximum drone HP.
- **Energy Core**: Increases maximum energy capacity for special abilities.
- **Weapon System**: Increases projectile damage across all weapon classes.
- **Mobility Thrusters**: Increases flight velocity and acceleration responsiveness.

---

## 💾 Save & Progression Architecture

- Progress is saved atomically to `save_data_pc.json` in the application directory.
- Upgrades, Scrap, unlocked sectors, mission clears, defeated bosses, and campaign victory states persist across sessions.
- Safe default fallbacks prevent data corruption or crashes if save files are modified or absent.

---

## 📦 Building Standalone Executable (Windows)

To build a standalone Windows `.exe` using PyInstaller:
```bash
pip install pyinstaller
pyinstaller --noconsole --name "DroneHunter" --add-data "drone_hunter_pc/assets;assets" drone_hunter_pc/main.py
```
The resulting executable will be located in `dist/DroneHunter/`.

---

## 📜 System Requirements

- **OS**: Windows 10/11 (or Linux / macOS with Python 3.10+)
- **Resolution**: 1280x720 (minimum), supports arbitrary window resizing and 1080p/1440p/4K fullscreen scaling.
- **Audio**: Any standard stereo output device (game features automatic fail-safe fallback if no audio device is found).
