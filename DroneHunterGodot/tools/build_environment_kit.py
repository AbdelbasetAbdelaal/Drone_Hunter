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
    print(f"Saved: {dest_path} ({image.size[0]}x{image.size[1]})")

def copy_png(src_path, dest_path):
    ensure_dir(os.path.dirname(dest_path))
    im = Image.open(src_path)
    save_png(im, dest_path)

def build_kit():
    ensure_dir(KIT_DIR)
    for cat in CATEGORIES:
        ensure_dir(os.path.join(KIT_DIR, cat))

    records = []

    # 1. DIRECT ASSET TRANSFERS
    direct_mappings = [
        # Terrain
        ("assets/environment/cyber_factory/floor/floor_01.png", "terrain/cyber_floor_01.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_02.png", "terrain/cyber_floor_02.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_03.png", "terrain/cyber_floor_03.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_04.png", "terrain/cyber_floor_04.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_05.png", "terrain/cyber_floor_05.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_grate.png", "terrain/floor_grate.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_maintenance.png", "terrain/floor_maintenance.png", "terrain"),
        ("assets/environment/cyber_factory/floor/floor_panel.png", "terrain/floor_panel.png", "terrain"),
        # Industrial
        ("assets/environment/cyber_factory/machinery/generator_01.png", "industrial/generator_01.png", "industrial"),
        ("assets/environment/cyber_factory/machinery/turbine_01.png", "industrial/turbine_01.png", "industrial"),
        ("assets/environment/cyber_factory/reactors/reactor_01.png", "industrial/reactor_01.png", "industrial"),
        ("assets/environment/structures/critical_power_reactor.png", "industrial/critical_power_reactor.png", "industrial"),
        ("assets/environment/cyber_factory/pipes/pipe_straight.png", "industrial/pipe_straight.png", "industrial"),
        ("assets/environment/cyber_factory/pipes/pipe_corner.png", "industrial/pipe_corner.png", "industrial"),
        # Towers
        ("assets/environment/structures/radar_command_tower.png", "towers/radar_command_tower.png", "towers"),
        ("assets/environment/structures/aa_platform.png", "towers/aa_platform.png", "towers"),
        # Radar
        ("assets/environment/structures/radar_dish.png", "radar/radar_dish.png", "radar"),
        ("assets/environment/structures/shield_generator.png", "radar/shield_generator.png", "radar"),
        # Vehicles
        ("assets/environment/structures/missile_launcher.png", "vehicles/missile_launcher_platform.png", "vehicles"),
        # Containers
        ("assets/environment/cyber_factory/props/crate_01.png", "containers/crate_01.png", "containers"),
        # Props
        ("assets/environment/cyber_factory/hazards/hazard_stripe_01.png", "props/hazard_stripe_01.png", "props"),
        ("assets/environment/cyber_factory/barriers/energy_barrier_blue.png", "props/energy_barrier_blue.png", "props"),
        ("assets/environment/cyber_factory/structures/wall_01.png", "props/wall_01.png", "props"),
    ]

    for rel_src, rel_dest, category in direct_mappings:
        src_full = os.path.join(PROJECT_ROOT, rel_src)
        if os.path.exists(src_full):
            dest_full = os.path.join(KIT_DIR, rel_dest)
            copy_png(src_full, dest_full)
            records.append({
                "path": f"res://assets/environment_kit/{rel_dest.replace(chr(92), '/')}",
                "category": category,
                "source_asset": f"res://{rel_src.replace(chr(92), '/')}",
                "status": "READY"
            })

    # 2. EXTRACT MODULAR VISUAL ELEMENTS FROM SOURCE ARTWORK
    s1_path = os.path.join(PROJECT_ROOT, "assets/backgrounds/sectors/sector_1_ref.png")
    if os.path.exists(s1_path):
        s1 = Image.open(s1_path)
        desert_base = s1.crop((0, 0, 1024, 1024))
        p = os.path.join(KIT_DIR, "terrain/desert_ground_base.png")
        save_png(desert_base, p)
        records.append({
            "path": "res://assets/environment_kit/terrain/desert_ground_base.png",
            "category": "terrain",
            "source_asset": "res://assets/backgrounds/sectors/sector_1_ref.png",
            "status": "READY"
        })

        desert_plateau = s1.crop((1200, 400, 2600, 1400))
        p = os.path.join(KIT_DIR, "terrain/desert_plateau_terrain.png")
        save_png(desert_plateau, p)
        records.append({
            "path": "res://assets/environment_kit/terrain/desert_plateau_terrain.png",
            "category": "terrain",
            "source_asset": "res://assets/backgrounds/sectors/sector_1_ref.png",
            "status": "READY"
        })

        canyon_ridge = s1.crop((400, 200, 1400, 900))
        p = os.path.join(KIT_DIR, "cliffs/canyon_ridge_formation.png")
        save_png(canyon_ridge, p)
        records.append({
            "path": "res://assets/environment_kit/cliffs/canyon_ridge_formation.png",
            "category": "cliffs",
            "source_asset": "res://assets/backgrounds/sectors/sector_1_ref.png",
            "status": "READY"
        })

    s2_path = os.path.join(PROJECT_ROOT, "assets/backgrounds/sectors/sector_2_ref.png")
    if os.path.exists(s2_path):
        s2 = Image.open(s2_path)
        
        cliff_nw = s2.crop((0, 0, 836, 470))
        p = os.path.join(KIT_DIR, "cliffs/canyon_cliff_outcrop.png")
        save_png(cliff_nw, p)
        records.append({
            "path": "res://assets/environment_kit/cliffs/canyon_cliff_outcrop.png",
            "category": "cliffs",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        palm_grove = s2.crop((320, 140, 780, 460))
        p = os.path.join(KIT_DIR, "vegetation/palm_oasis_grove.png")
        save_png(palm_grove, p)
        records.append({
            "path": "res://assets/environment_kit/vegetation/palm_oasis_grove.png",
            "category": "vegetation",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        container_box = s2.crop((120, 0, 450, 200))
        p = os.path.join(KIT_DIR, "containers/cargo_container_outpost.png")
        save_png(container_box, p)
        records.append({
            "path": "res://assets/environment_kit/containers/cargo_container_outpost.png",
            "category": "containers",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        bridge_section = s2.crop((1080, 0, 1672, 360))
        p = os.path.join(KIT_DIR, "bridges/tactical_bridge_overpass.png")
        save_png(bridge_section, p)
        records.append({
            "path": "res://assets/environment_kit/bridges/tactical_bridge_overpass.png",
            "category": "bridges",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        recon_truck = s2.crop((950, 120, 1220, 310))
        p = os.path.join(KIT_DIR, "vehicles/armored_recon_truck.png")
        save_png(recon_truck, p)
        records.append({
            "path": "res://assets/environment_kit/vehicles/armored_recon_truck.png",
            "category": "vehicles",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        bridge_approach_road = s2.crop((836, 0, 1300, 470))
        p = os.path.join(KIT_DIR, "roads/canyon_approach_road.png")
        save_png(bridge_approach_road, p)
        records.append({
            "path": "res://assets/environment_kit/roads/canyon_approach_road.png",
            "category": "roads",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        river_canyon_water = s2.crop((1280, 0, 1672, 470))
        p = os.path.join(KIT_DIR, "water/canyon_river_waterway.png")
        save_png(river_canyon_water, p)
        records.append({
            "path": "res://assets/environment_kit/water/canyon_river_waterway.png",
            "category": "water",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        radar_complex = s2.crop((0, 520, 780, 941))
        p = os.path.join(KIT_DIR, "buildings/radar_facility_complex.png")
        save_png(radar_complex, p)
        records.append({
            "path": "res://assets/environment_kit/buildings/radar_facility_complex.png",
            "category": "buildings",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        radar_station_tower = s2.crop((0, 520, 280, 941))
        p = os.path.join(KIT_DIR, "towers/comm_mast_tower.png")
        save_png(radar_station_tower, p)
        records.append({
            "path": "res://assets/environment_kit/towers/comm_mast_tower.png",
            "category": "towers",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        dish_outpost = s2.crop((230, 680, 550, 941))
        p = os.path.join(KIT_DIR, "radar/radar_outpost_dish.png")
        save_png(dish_outpost, p)
        records.append({
            "path": "res://assets/environment_kit/radar/radar_outpost_dish.png",
            "category": "radar",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        river_valley_water = s2.crop((836, 470, 1672, 941))
        p = os.path.join(KIT_DIR, "water/desert_river_valley.png")
        save_png(river_valley_water, p)
        records.append({
            "path": "res://assets/environment_kit/water/desert_river_valley.png",
            "category": "water",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

        rock_spires = s2.crop((900, 470, 1400, 941))
        p = os.path.join(KIT_DIR, "rocks/canyon_rock_spires.png")
        save_png(rock_spires, p)
        records.append({
            "path": "res://assets/environment_kit/rocks/canyon_rock_spires.png",
            "category": "rocks",
            "source_asset": "res://assets/backgrounds/sectors/sector_2_ref.png",
            "status": "READY"
        })

    index_path = os.path.join(PROJECT_ROOT, "tools/environment_kit.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"\nIndexed {len(records)} environment kit assets in {index_path}")

if __name__ == "__main__":
    build_kit()
