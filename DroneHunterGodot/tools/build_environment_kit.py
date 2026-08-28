import os
import shutil
import json
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
KIT_DIR = os.path.join(ASSETS_DIR, "environment_kit")

CATEGORIES = [
    "terrain",
    "cliffs",
    "rocks",
    "roads",
    "water",
    "buildings",
    "industrial",
    "towers",
    "radar",
    "bridges",
    "containers",
    "vehicles",
    "vegetation",
    "props"
]

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_png(image, dest_path):
    ensure_dir(os.path.dirname(dest_path))
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")
    image.save(dest_path, "PNG")

def copy_png(src_path, dest_path):
    ensure_dir(os.path.dirname(dest_path))
    im = Image.open(src_path)
    save_png(im, dest_path)

def build_kit():
    ensure_dir(KIT_DIR)
    for cat in CATEGORIES:
        ensure_dir(os.path.join(KIT_DIR, cat))

    records = []

    # 1. ACTIVE DESERT & INDUSTRIAL STANDALONE ASSETS
    active_mappings = [
        # Terrain / Base
        ("assets/backgrounds/sectors/sector_2_ref.png", "terrain/desert_sector_base.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_01.png", "terrain/cyber_floor_01.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_02.png", "terrain/cyber_floor_02.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_03.png", "terrain/cyber_floor_03.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_04.png", "terrain/cyber_floor_04.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_grate.png", "terrain/floor_grate.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_maintenance.png", "terrain/floor_maintenance.png", "terrain", "READY"),
        ("assets/environment/cyber_factory/floor/floor_panel.png", "terrain/floor_panel.png", "terrain", "READY"),
        # Industrial
        ("assets/environment/cyber_factory/machinery/generator_01.png", "industrial/generator_01.png", "industrial", "READY"),
        ("assets/environment/cyber_factory/machinery/turbine_01.png", "industrial/turbine_01.png", "industrial", "READY"),
        ("assets/environment/cyber_factory/reactors/reactor_01.png", "industrial/reactor_01.png", "industrial", "READY"),
        ("assets/environment/structures/critical_power_reactor.png", "industrial/critical_power_reactor.png", "industrial", "READY"),
        ("assets/environment/cyber_factory/pipes/pipe_straight.png", "industrial/pipe_straight.png", "industrial", "READY"),
        ("assets/environment/cyber_factory/pipes/pipe_corner.png", "industrial/pipe_corner.png", "industrial", "READY"),
        # Towers
        ("assets/environment/structures/radar_command_tower.png", "towers/radar_command_tower.png", "towers", "READY"),
        ("assets/environment/structures/aa_platform.png", "towers/aa_platform.png", "towers", "READY"),
        # Radar
        ("assets/environment/structures/radar_dish.png", "radar/radar_dish.png", "radar", "READY"),
        # Vehicles
        ("assets/environment/structures/missile_launcher.png", "vehicles/missile_launcher_platform.png", "vehicles", "READY"),
        # Containers
        ("assets/environment/cyber_factory/props/crate_01.png", "containers/crate_01.png", "containers", "READY"),
        # Props
        ("assets/environment/cyber_factory/hazards/hazard_stripe_01.png", "props/hazard_stripe_01.png", "props", "READY"),
        ("assets/environment/cyber_factory/barriers/energy_barrier_blue.png", "props/energy_barrier_blue.png", "props", "READY"),
        ("assets/environment/cyber_factory/structures/wall_01.png", "props/wall_01.png", "props", "READY"),
    ]

    for rel_src, rel_dest, category, status in active_mappings:
        src_full = os.path.join(PROJECT_ROOT, rel_src)
        if os.path.exists(src_full):
            dest_full = os.path.join(KIT_DIR, rel_dest)
            copy_png(src_full, dest_full)
            records.append({
                "path": f"res://assets/environment_kit/{rel_dest.replace(chr(92), '/')}",
                "category": category,
                "source_asset": f"res://{rel_src.replace(chr(92), '/')}",
                "status": status
            })

    # 2. INACTIVE / FUTURE USE ASSETS (Tropical / Ocean / Different Sectors)
    inactive_mappings = [
        ("assets/backgrounds/sectors/sector_1_ref.png", "terrain/tropical_sector_1_ref.png", "terrain", "INACTIVE - Tropical/Ocean (Reserved for Sector 1)"),
        ("assets/backgrounds/sectors/sector_3_ref.png", "terrain/forest_sector_3_ref.png", "terrain", "INACTIVE - Forest/Jungle (Reserved for Sector 3)"),
        ("assets/backgrounds/sectors/sector_4_ref.png", "terrain/space_sector_4_ref.png", "terrain", "INACTIVE - Deep Space (Reserved for Sector 4)"),
        ("assets/backgrounds/sectors/sector_5_ref.png", "terrain/cyber_sector_5_ref.png", "terrain", "INACTIVE - Cyber Void (Reserved for Sector 5)"),
    ]

    for rel_src, rel_dest, category, status in inactive_mappings:
        src_full = os.path.join(PROJECT_ROOT, rel_src)
        if os.path.exists(src_full):
            dest_full = os.path.join(KIT_DIR, rel_dest)
            copy_png(src_full, dest_full)
            records.append({
                "path": f"res://assets/environment_kit/{rel_dest.replace(chr(92), '/')}",
                "category": category,
                "source_asset": f"res://{rel_src.replace(chr(92), '/')}",
                "status": status
            })

    index_path = os.path.join(PROJECT_ROOT, "tools/environment_kit.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"\nSuccessfully built environment kit: {len(records)} entries in {index_path}")

if __name__ == "__main__":
    build_kit()
