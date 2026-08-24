"""
================================================================================
                    DRONE HUNTER 2D - GAME DATA CATALOG
================================================================================
Authoritative specifications for weapons, enemies, bosses, sectors, upgrades,
difficulty presets, and player combat physics.
"""

from src.data.settings import (
    COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD, COLOR_CRIMSON, COLOR_MAGENTA,
    COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_SLOWMO, COLOR_BEAM,
    COLOR_MISSILE, COLOR_TESLA, COLOR_CLUSTER, COLOR_WHITE
)

# -----------------------------------------------------------------------------
# Player Physics & Combat Constants
# -----------------------------------------------------------------------------
HORIZONTAL_SPEED = 520.0
VERTICAL_SPEED = 460.0
ACCELERATION = 3800.0
FRICTION = 6.0

PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ENERGY = 100.0
ENERGY_REGEN_RATE = 14.0       # Energy per second
BOOST_DRAIN_RATE = 32.0

EMP_COOLDOWN_MAX = 14.0
ROLL_COOLDOWN = 1.2
ROLL_DURATION = 0.28
ROLL_SPEED_BOOST = 2.4

CLOAK_DURATION = 4.5
CLOAK_COOLDOWN_MAX = 10.0

OVERDRIVE_DURATION = 5.0
OVERDRIVE_COOLDOWN_MAX = 25.0

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Authoritative Weapon Definitions & Metadata Specification
# -----------------------------------------------------------------------------
WEAPON_PULSE = "pulse"
WEAPON_SCATTER = "scatter"
WEAPON_MISSILE = "missile"
WEAPON_RAPID = "rapid"
WEAPON_PLASMA = "plasma"
WEAPON_RAIL = "rail"
WEAPON_BARRAGE = "barrage"
WEAPON_BEAM = "beam"
WEAPON_TESLA = "tesla"
WEAPON_CLUSTER = "cluster"
WEAPON_EMP = "emp"

# -----------------------------------------------------------------------------
# Authoritative Production Asset Registries
# -----------------------------------------------------------------------------
WEAPON_ASSETS = {
    "pulse": "weapons/laser_pulse.png",
    "rapid": "weapons/laser_pulse.png",
    "scatter": "weapons/laser_scatter.png",
    "missile": "weapons/missile.png",
    "barrage": "weapons/missile.png",
    "beam": "weapons/laser_beam.png",
    "plasma": "weapons/laser_beam.png",
    "rail": "weapons/laser_beam.png",
    "tesla": "weapons/tesla_orb.png",
    "cluster": "weapons/cluster_torpedo.png",
    "emp": "weapons/tesla_orb.png",
}

VFX_ASSETS = {
    "explosion_small": "vfx/explosion_1.png",
    "explosion_1": "vfx/explosion_1.png",
    "explosion_heavy": "vfx/explosion_2.png",
    "explosion_2": "vfx/explosion_2.png",
    "shockwave": "vfx/shockwave.png",
    "shield": "vfx/shield_bubble.png",
    "shield_bubble": "vfx/shield_bubble.png",
    "engine": "vfx/engine_flame.png",
    "engine_flame": "vfx/engine_flame.png",
}

WEAPON_DEFS = {
    WEAPON_PULSE: {
        "weapon_id": WEAPON_PULSE,
        "name": "Pulse Laser",
        "display_name": "Pulse Laser",
        "slot": 1,
        "cooldown": 0.18,
        "energy_cost": 0.0,
        "damage": 12,
        "speed": 650.0,
        "projectile_speed": 650.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "pulse",
        "projectile_asset": "weapons/laser_pulse.png",
        "muzzle_vfx": "muzzle_pulse",
        "impact_vfx": "impact_pulse",
        "audio_id": "laser",
        "mount_profile": "primary_front_center",
        "behavior_type": "linear_bolt",
        "color": COLOR_CYAN,
        "description": "Accurate high-velocity coherent energy bolt.",
        "icon": "⚡",
        "unlocked_default": True
    },
    WEAPON_SCATTER: {
        "weapon_id": WEAPON_SCATTER,
        "name": "Spread Cannon",
        "display_name": "Spread Cannon",
        "slot": 2,
        "cooldown": 0.75,
        "energy_cost": 0.0,
        "damage": 10,
        "speed": 500.0,
        "projectile_speed": 500.0,
        "projectiles_per_shot": 5,
        "spread_deg": 22.0,
        "projectile_type": "scatter",
        "projectile_asset": "weapons/laser_scatter.png",
        "muzzle_vfx": "muzzle_scatter",
        "impact_vfx": "impact_scatter",
        "audio_id": "scatter",
        "mount_profile": "dual_wing",
        "behavior_type": "shrapnel_burst",
        "color": COLOR_GOLD,
        "description": "Twin-emitter multi-shrapnel conical blast for close encounters.",
        "icon": "💥",
        "unlocked_default": True
    },
    WEAPON_MISSILE: {
        "weapon_id": WEAPON_MISSILE,
        "name": "Heavy Missile",
        "display_name": "Heavy Missile",
        "slot": 3,
        "cooldown": 2.5,
        "energy_cost": 0.0,
        "damage": 65,
        "speed": 260.0,
        "projectile_speed": 260.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "missile",
        "projectile_asset": "weapons/missile.png",
        "muzzle_vfx": "muzzle_missile",
        "impact_vfx": "impact_missile",
        "audio_id": "missile",
        "mount_profile": "missile_pod",
        "behavior_type": "guided_homing",
        "color": COLOR_MISSILE,
        "description": "Guided ordnance tracking targets with massive thermal payload.",
        "icon": "🚀",
        "unlocked_default": True
    },
    WEAPON_RAPID: {
        "weapon_id": WEAPON_RAPID,
        "name": "Rapid Autocannon",
        "display_name": "Rapid Autocannon",
        "slot": 2,
        "cooldown": 0.08,
        "energy_cost": 0.0,
        "damage": 8,
        "speed": 980.0,
        "projectile_speed": 980.0,
        "projectiles_per_shot": 1,
        "spread_deg": 3.0,
        "projectile_type": "rapid",
        "projectile_asset": "weapons/laser_pulse.png",
        "muzzle_vfx": "muzzle_rapid",
        "impact_vfx": "impact_rapid",
        "audio_id": "rapid",
        "mount_profile": "dual_front",
        "behavior_type": "cyclic_kinetic",
        "color": (250, 204, 21),
        "description": "High-cyclic kinetic rounds alternating from dual nose muzzles.",
        "icon": "🔥",
        "unlocked_default": True
    },
    WEAPON_PLASMA: {
        "weapon_id": WEAPON_PLASMA,
        "name": "Heavy Plasma Cannon",
        "display_name": "Heavy Plasma Cannon",
        "slot": 2,
        "cooldown": 0.85,
        "energy_cost": 0.0,
        "damage": 90,
        "speed": 460.0,
        "projectile_speed": 460.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "plasma",
        "projectile_asset": "weapons/laser_beam.png",
        "muzzle_vfx": "muzzle_plasma",
        "impact_vfx": "impact_plasma",
        "audio_id": "plasma",
        "mount_profile": "heavy_front_center",
        "behavior_type": "concentrated_plasma",
        "color": (168, 85, 247),
        "description": "Dense superheated plasma orb with massive splash disruption.",
        "icon": "🔮",
        "unlocked_default": True
    },
    WEAPON_RAIL: {
        "weapon_id": WEAPON_RAIL,
        "name": "Precision Railgun",
        "display_name": "Precision Railgun",
        "slot": 1,
        "cooldown": 1.10,
        "energy_cost": 0.0,
        "damage": 115,
        "speed": 1800.0,
        "projectile_speed": 1800.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "rail",
        "projectile_asset": "weapons/laser_beam.png",
        "muzzle_vfx": "muzzle_rail",
        "impact_vfx": "impact_rail",
        "audio_id": "rail",
        "mount_profile": "primary_front_center",
        "behavior_type": "supersonic_piercing",
        "color": (224, 242, 254),
        "description": "Hypersonic electromagnetic slug penetrating all armor plating.",
        "icon": "💠",
        "unlocked_default": True
    },
    WEAPON_BARRAGE: {
        "weapon_id": WEAPON_BARRAGE,
        "name": "Missile Barrage",
        "display_name": "Missile Barrage",
        "slot": 3,
        "cooldown": 2.2,
        "energy_cost": 0.0,
        "damage": 38,
        "speed": 620.0,
        "projectile_speed": 620.0,
        "projectiles_per_shot": 4,
        "spread_deg": 28.0,
        "projectile_type": "barrage",
        "projectile_asset": "weapons/missile.png",
        "muzzle_vfx": "muzzle_barrage",
        "impact_vfx": "impact_barrage",
        "audio_id": "barrage",
        "mount_profile": "multi_pod",
        "behavior_type": "salvo_homing",
        "color": COLOR_MISSILE,
        "description": "Four-missile salvo launched simultaneously from wing pods.",
        "icon": "🎯",
        "unlocked_default": True
    },
    WEAPON_BEAM: {
        "weapon_id": WEAPON_BEAM,
        "name": "Plasma Cutting Beam",
        "display_name": "Plasma Cutting Beam",
        "slot": 2,
        "cooldown": 0.08,
        "energy_cost": 0.0,
        "damage": 26,
        "speed": 1500.0,
        "projectile_speed": 1500.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "beam",
        "projectile_asset": "weapons/laser_beam.png",
        "muzzle_vfx": "muzzle_beam",
        "impact_vfx": "impact_beam",
        "audio_id": "beam",
        "mount_profile": "beam_emitter",
        "behavior_type": "continuous_beam",
        "color": COLOR_BEAM,
        "description": "Continuous ultra-dense plasma laser searing through chassis and vaporizing incoming ordnance.",
        "icon": "〰️",
        "unlocked_default": True
    },
    WEAPON_TESLA: {
        "weapon_id": WEAPON_TESLA,
        "name": "Tesla Arc",
        "display_name": "Tesla Arc",
        "slot": 2,
        "cooldown": 0.40,
        "energy_cost": 0.0,
        "damage": 44,
        "speed": 1100.0,
        "projectile_speed": 1100.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "tesla",
        "projectile_asset": "weapons/tesla_orb.png",
        "muzzle_vfx": "muzzle_tesla",
        "impact_vfx": "impact_tesla",
        "audio_id": "tesla",
        "mount_profile": "energy_emitter",
        "behavior_type": "chaining_lightning",
        "color": COLOR_TESLA,
        "description": "High-voltage electrical discharge jumping between targets.",
        "icon": "⚡",
        "unlocked_default": True
    },
    WEAPON_CLUSTER: {
        "weapon_id": WEAPON_CLUSTER,
        "name": "Cluster Torpedo",
        "display_name": "Cluster Torpedo",
        "slot": 4,
        "cooldown": 2.0,
        "energy_cost": 0.0,
        "damage": 85,
        "speed": 520.0,
        "projectile_speed": 520.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "cluster",
        "projectile_asset": "weapons/cluster_torpedo.png",
        "muzzle_vfx": "muzzle_cluster",
        "impact_vfx": "impact_cluster",
        "audio_id": "cluster",
        "mount_profile": "heavy_front_center",
        "behavior_type": "cluster_submunition",
        "color": COLOR_CLUSTER,
        "description": "Heavy ballistic torpedo splitting into 6 explosive sub-munitions.",
        "icon": "💣",
        "unlocked_default": True
    },
    WEAPON_EMP: {
        "weapon_id": WEAPON_EMP,
        "name": "EMP Shockwave Pulse",
        "display_name": "EMP Shockwave Pulse",
        "slot": 1,
        "cooldown": 0.50,
        "energy_cost": 0.0,
        "damage": 30,
        "speed": 1200.0,
        "projectile_speed": 1200.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_type": "emp",
        "projectile_asset": "weapons/tesla_orb.png",
        "muzzle_vfx": "muzzle_emp",
        "impact_vfx": "impact_emp",
        "audio_id": "emp",
        "mount_profile": "energy_center",
        "behavior_type": "emp_expanding_pulse",
        "color": (6, 182, 212),
        "description": "Electromagnetic shockwave disabling enemy subsystems.",
        "icon": "🌐",
        "unlocked_default": True
    }
}

# -----------------------------------------------------------------------------
# Drone Specific Mount Profiles & Local-Space Hardpoints (Calibrated for 176x152)
# -----------------------------------------------------------------------------
DRONE_MOUNT_PROFILES = {
    "striker": {
        "primary_front_center": (88.0, 0.0),
        "primary": (88.0, 0.0),
        "left": (32.0, -56.0),
        "right": (32.0, 56.0),
        "wing_left": (32.0, -56.0),
        "wing_right": (32.0, 56.0),
        "missile_mount": (40.0, 0.0),
        "missile_left": (24.0, -58.0),
        "missile_right": (24.0, 58.0),
    },
    "interceptor": {
        "primary_front_center": (94.0, 0.0),
        "primary": (94.0, 0.0),
        "dual_left": (82.0, -18.0),
        "dual_right": (82.0, 18.0),
        "left": (28.0, -50.0),
        "right": (28.0, 50.0),
        "wing_left": (28.0, -50.0),
        "wing_right": (28.0, 50.0),
        "missile_mount": (36.0, 0.0),
        "missile_left": (20.0, -52.0),
        "missile_right": (20.0, 52.0),
    },
    "assault": {
        "heavy_front_center": (86.0, 0.0),
        "primary_front_center": (86.0, 0.0),
        "primary": (86.0, 0.0),
        "left": (36.0, -64.0),
        "right": (36.0, 64.0),
        "plasma_left": (36.0, -64.0),
        "plasma_right": (36.0, 64.0),
        "missile_left": (16.0, -68.0),
        "missile_right": (16.0, 68.0),
        "missile_mount": (20.0, 0.0),
    },
    "arc": {
        "energy_center": (88.0, 0.0),
        "primary_front_center": (88.0, 0.0),
        "primary": (88.0, 0.0),
        "beam_emitter": (88.0, 0.0),
        "energy_left": (32.0, -54.0),
        "energy_right": (32.0, 54.0),
        "left": (32.0, -54.0),
        "right": (32.0, 54.0),
    },
    "command": {
        "rail_front": (96.0, 0.0),
        "primary_front_center": (96.0, 0.0),
        "primary": (96.0, 0.0),
        "beam_emitter": (96.0, 0.0),
        "left": (24.0, -48.0),
        "right": (24.0, 48.0),
        "pod_left": (12.0, -72.0),
        "pod_right": (12.0, 72.0),
        "cluster_pod": (44.0, 0.0),
    }
}


# -----------------------------------------------------------------------------
# Five Drone Combat Classes & Deterministic Loadout Architecture
# -----------------------------------------------------------------------------
DRONE_CLASS_STRIKER = "striker"
DRONE_CLASS_INTERCEPTOR = "interceptor"
DRONE_CLASS_ASSAULT = "assault"
DRONE_CLASS_ARC = "arc"
DRONE_CLASS_COMMAND = "command"

# Authoritative Single Source of Truth for Drone Loadouts
DRONE_LOADOUTS = {
    DRONE_CLASS_INTERCEPTOR: {
        "primary": WEAPON_PULSE,
        "secondary": WEAPON_RAPID,
        "heavy": WEAPON_MISSILE,
    },
    DRONE_CLASS_STRIKER: {
        "primary": WEAPON_PULSE,
        "secondary": WEAPON_SCATTER,
        "heavy": WEAPON_MISSILE,
    },
    DRONE_CLASS_ASSAULT: {
        "primary": WEAPON_PULSE,
        "secondary": WEAPON_PLASMA,
        "heavy": WEAPON_MISSILE,
    },
    DRONE_CLASS_ARC: {
        "primary": WEAPON_EMP,
        "secondary": WEAPON_TESLA,
        "heavy": WEAPON_BEAM,
    },
    DRONE_CLASS_COMMAND: {
        "primary": WEAPON_RAIL,
        "secondary": WEAPON_BEAM,
        "heavy": WEAPON_BARRAGE,
        "special": WEAPON_CLUSTER,
    },
}

DRONE_CLASSES = {
    DRONE_CLASS_STRIKER: {
        "class_id": DRONE_CLASS_STRIKER,
        "name": "STRIKER",
        "title": "BALANCED FRONTLINE DRONE",
        "description": "Balanced combat chassis with precision forward weapons and versatile performance.",
        "speed_mult": 1.0,           # Baseline 420.0 px/s
        "accel_mult": 1.0,           # Baseline 3600.0 px/s²
        "max_health": 100,
        "armor": 0,
        "loadout": DRONE_LOADOUTS[DRONE_CLASS_STRIKER],
        "weapons": [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE],
        "mounts": {
            "primary": (88.0, 0.0),       # Front center nose
            "left": (32.0, -56.0),        # Left wing hardpoint
            "right": (32.0, 56.0),        # Right wing hardpoint
        },
        "role": "BALANCED / ACCURATE / VERSATILE"
    },

    DRONE_CLASS_INTERCEPTOR: {
        "class_id": DRONE_CLASS_INTERCEPTOR,
        "name": "INTERCEPTOR",
        "title": "FAST ATTACK / INTERCEPTION",
        "description": "High-mobility strike platform with extreme acceleration and rapid-fire armament.",
        "speed_mult": 1.35,          # 567 px/s (very fast & agile)
        "accel_mult": 1.35,          # 4860 px/s² (instant response)
        "max_health": 80,
        "armor": 0,
        "loadout": DRONE_LOADOUTS[DRONE_CLASS_INTERCEPTOR],
        "weapons": [WEAPON_PULSE, WEAPON_RAPID, WEAPON_MISSILE],
        "mounts": {
            "primary": (94.0, 0.0),       # Needle nose
            "left": (28.0, -50.0),
            "right": (28.0, 50.0),
            "dual_left": (82.0, -18.0),
            "dual_right": (82.0, 18.0),
        },
        "role": "FAST / AGILE / HIGH DPS / LOW SURVIVABILITY"
    },
    DRONE_CLASS_ASSAULT: {
        "class_id": DRONE_CLASS_ASSAULT,
        "name": "ASSAULT",
        "title": "HEAVY ATTACK DREADNOUGHT",
        "description": "Heavily armored juggernaut packing devastating heavy plasma ordnance and high durability.",
        "speed_mult": 0.90,          # 378 px/s (heavy tank)
        "accel_mult": 0.85,          # 3060 px/s²
        "max_health": 145,
        "armor": 6,
        "loadout": DRONE_LOADOUTS[DRONE_CLASS_ASSAULT],
        "weapons": [WEAPON_PULSE, WEAPON_PLASMA, WEAPON_MISSILE],
        "mounts": {
            "primary": (86.0, 0.0),
            "left": (36.0, -64.0),
            "right": (36.0, 64.0),
            "plasma_left": (36.0, -64.0),
            "plasma_right": (36.0, 64.0),
            "missile_left": (16.0, -68.0),
            "missile_right": (16.0, 68.0),
        },
        "role": "HEAVY / POWERFUL / HIGH DURABILITY"
    },
    DRONE_CLASS_ARC: {
        "class_id": DRONE_CLASS_ARC,
        "name": "ARC",
        "title": "ENERGY / AREA CONTROL",
        "description": "Specialized electromagnetic disruption platform with high-voltage chain arcs and EMP focus.",
        "speed_mult": 1.10,          # 462 px/s
        "accel_mult": 1.15,          # 4140 px/s²
        "max_health": 95,
        "armor": 2,
        "loadout": DRONE_LOADOUTS[DRONE_CLASS_ARC],
        "weapons": [WEAPON_EMP, WEAPON_TESLA, WEAPON_BEAM],
        "mounts": {
            "primary": (88.0, 0.0),
            "energy_center": (88.0, 0.0),
            "beam_emitter": (88.0, 0.0),
            "left": (32.0, -54.0),
            "right": (32.0, 54.0),
            "energy_left": (32.0, -54.0),
            "energy_right": (32.0, 54.0),
        },
        "role": "ENERGY / CONTROL / AREA DAMAGE"
    },
    DRONE_CLASS_COMMAND: {
        "class_id": DRONE_CLASS_COMMAND,
        "name": "COMMAND",
        "title": "ADVANCED ENDGAME PLATFORM",
        "description": "Endgame quad-thruster platform equipped with multi-pod missile barrages and precision rail slugs.",
        "speed_mult": 1.25,          # 525 px/s
        "accel_mult": 1.20,          # 4320 px/s²
        "max_health": 125,
        "armor": 4,
        "loadout": DRONE_LOADOUTS[DRONE_CLASS_COMMAND],
        "weapons": [WEAPON_RAIL, WEAPON_BEAM, WEAPON_BARRAGE, WEAPON_CLUSTER],
        "mounts": {
            "primary": (96.0, 0.0),
            "rail_front": (96.0, 0.0),
            "beam_emitter": (96.0, 0.0),
            "left": (24.0, -48.0),
            "right": (24.0, 48.0),
            "pod_left": (12.0, -72.0),
            "pod_right": (12.0, 72.0),
            "cluster_pod": (44.0, 0.0),
        },
        "role": "ADVANCED / PRECISION / HIGH FIREPOWER / ENDGAME"
    }
}


def get_drone_class_by_id(class_id: str) -> dict:
    """Returns the authoritative drone class configuration for a given class ID."""
    return DRONE_CLASSES.get(class_id, DRONE_CLASSES[DRONE_CLASS_STRIKER])


def get_drone_loadout(class_id_or_index: str | int) -> dict[str, str]:
    """Returns the authoritative deterministic loadout mapping for a drone class."""
    if isinstance(class_id_or_index, int):
        # Legacy fallback for old save files / tests
        mapping = {
            0: DRONE_CLASS_STRIKER,
            1: DRONE_CLASS_INTERCEPTOR,
            2: DRONE_CLASS_ASSAULT,
            3: DRONE_CLASS_ARC,
            4: DRONE_CLASS_COMMAND
        }
        class_id_or_index = mapping.get(class_id_or_index, DRONE_CLASS_STRIKER)
    return DRONE_LOADOUTS.get(class_id_or_index, DRONE_LOADOUTS[DRONE_CLASS_STRIKER])



# -----------------------------------------------------------------------------
# Enemy & Boss Type Identifiers
# -----------------------------------------------------------------------------
# Active Phase 8 combat entities (fully integrated with 2D sprite rendering & AI)
TARGET_TYPE_SCOUT = "scout"                       # Phase 2A Scout Drone (Mobile Melee Pressure)
TARGET_TYPE_SHOOTER = "shooter"                   # Phase 2B Shooter Drone (Positioning Pressure)
TARGET_TYPE_HEAVY = "heavy"                       # Phase 2C Heavy Drone (Target Prioritization Pressure)
TARGET_TYPE_SHIELD_DRONE = "shield_drone"         # Phase 2D Shield Support Drone (Defense Aura)

# Active Phase 6 Boss Identifiers (refer to boss_data.py for full specifications)
TARGET_TYPE_BOSS = "boss"                         # Sky Dreadnought / Assembly Warden (Sector 1)
TARGET_TYPE_STEALTH_MIRAGE = "stealth_mirage"     # Stealth Mirage / Core Executor (Sector 2)
TARGET_TYPE_EMP_DISRUPTER = "emp_disrupter"       # EMP Disrupter / Reactor Titan (Sector 3)
TARGET_TYPE_TITAN_MECH = "titan_mech"             # Colossus Titan Mech (Sector 5)

# Legacy enemy identifiers (preserved for backwards-compatibility)
TARGET_TYPE_STANDARD = "standard"
TARGET_TYPE_FAST = "fast"
TARGET_TYPE_ARMORED = "armored"
TARGET_TYPE_TURRET = "turret"
TARGET_TYPE_VEHICLE = "vehicle"
TARGET_TYPE_CHASER = "chaser"
TARGET_TYPE_SWARM = "swarm"
TARGET_TYPE_SNIPER = "sniper"

TARGET_SPEED = 140.0
ENEMY_BULLET_SPEED = 340.0

# -----------------------------------------------------------------------------
# Scout Drone Specifications (Phase 2A Baseline)
# -----------------------------------------------------------------------------
SCOUT_HP = 30
SCOUT_SPEED = 210.0
SCOUT_DIVE_SPEED = 410.0
SCOUT_CONTACT_DAMAGE = 22.0
SCOUT_SCORE = 150
SCOUT_SIZE = 32
SCOUT_TELEGRAPH_TIME = 0.45
SCOUT_DIVE_DURATION = 0.55
SCOUT_RECOVER_TIME = 0.75
SCOUT_STRAFE_DURATION = 1.40
SCOUT_CONTACT_COOLDOWN = 1.00

# -----------------------------------------------------------------------------
# Shooter Drone Specifications (Phase 2B Baseline)
# -----------------------------------------------------------------------------
SHOOTER_HP = 55
SHOOTER_SPEED = 120.0
SHOOTER_PREFERRED_DISTANCE = 470.0
SHOOTER_MIN_DISTANCE = 300.0
SHOOTER_MAX_DISTANCE = 700.0
SHOOTER_SCORE = 250
SHOOTER_SIZE = 38
SHOOTER_PROJECTILE_DAMAGE = 12
SHOOTER_PROJECTILE_SPEED = 340.0
SHOOTER_FIRE_COOLDOWN = 1.50
SHOOTER_TELEGRAPH_TIME = 0.55
SHOOTER_REPOSITION_TIME = 0.90

# -----------------------------------------------------------------------------
# Heavy Drone Specifications (Phase 2C Baseline)
# -----------------------------------------------------------------------------
HEAVY_HP = 180
HEAVY_SPEED = 65.0
HEAVY_SCORE = 500
HEAVY_SIZE = 58
HEAVY_CONTACT_DAMAGE = 30.0
HEAVY_CONTACT_COOLDOWN = 1.00
HEAVY_ARMOR = 0.20
HEAVY_PRESSURE_DISTANCE = 300.0
HEAVY_TELEGRAPH_TIME = 0.65

# -----------------------------------------------------------------------------
# Phase 4 Player Progression & Rewards
# -----------------------------------------------------------------------------
REWARD_SCOUT = 25
REWARD_SHOOTER = 40
REWARD_HEAVY = 75
REWARD_ENCOUNTER = 100
REWARD_COMPOSITION = 150

UPGRADE_COSTS = {
    1: 500,   # Level 1 -> 2
    2: 1000,  # Level 2 -> 3
    3: 1750,  # Level 3 -> 4
    4: 2750   # Level 4 -> 5
}
MAX_UPGRADE_LEVEL = 5

# -----------------------------------------------------------------------------
# Campaign Sectors & Stages (Legacy Stage-Based Mode)
# NOTE: The authoritative 25-mission Campaign is defined in src.data.mission_data
# (SECTORS_PHASE5 and MISSIONS). This catalog is retained for background/weather
# theme lookups and backward compatibility.
# -----------------------------------------------------------------------------
SECTORS = [
    {
        "id": 0,
        "name": "Tropical Ocean Battlescape",
        "desc": "Turquoise naval coastal waters with islands, docks, and coastal defense installations.",
        "theme_color": (14, 165, 233),
        "weather": "storm",
        "base_target_score": 5000,
        "stages": [
            {"num": 1, "name": "Coastal Recon", "score": 1500, "hazard": "sea_mines"},
            {"num": 2, "name": "Reef Skirmish", "score": 3200, "hazard": "debris"},
            {"num": 3, "name": "Dreadnought Intercept", "score": 5500, "hazard": "boss_dreadnought"}
        ]
    },
    {
        "id": 1,
        "name": "Desert Canyon Wasteland",
        "desc": "Scorching sandstone canyons and abandoned industrial mining outposts.",
        "theme_color": (245, 158, 11),
        "weather": "sandstorm",
        "base_target_score": 7500,
        "stages": [
            {"num": 1, "name": "Canyon Approach", "score": 2200, "hazard": "laser_grid"},
            {"num": 2, "name": "Mining Trench", "score": 4500, "hazard": "debris"},
            {"num": 3, "name": "Colossus Titan Showdown", "score": 7500, "hazard": "boss_titan"}
        ]
    },
    {
        "id": 2,
        "name": "Jungle River Basin",
        "desc": "Dense tropical rainforest with waterfalls, river bridges, and ancient monolith ruins.",
        "theme_color": (16, 185, 129),
        "weather": "rain",
        "base_target_score": 10000,
        "stages": [
            {"num": 1, "name": "River Run", "score": 3000, "hazard": "gravity_well"},
            {"num": 2, "name": "Waterfall Ruins", "score": 6200, "hazard": "debris"},
            {"num": 3, "name": "EMP Disrupter Bastion", "score": 10000, "hazard": "boss_emp"}
        ]
    },
    {
        "id": 3,
        "name": "Cyberpunk City Megastructure",
        "desc": "High-altitude neon skyscrapers, elevated highways, and air defense rooftops.",
        "theme_color": (168, 85, 247),
        "weather": "rain",
        "base_target_score": 13000,
        "stages": [
            {"num": 1, "name": "Rooftop Recon", "score": 4000, "hazard": "none"},
            {"num": 2, "name": "Neon Skyline", "score": 8000, "hazard": "storm_winds"},
            {"num": 3, "name": "Megastructure Clash", "score": 13000, "hazard": "boss_dreadnought"}
        ]
    },
    {
        "id": 4,
        "name": "Cyber Factory Core",
        "desc": "Automated industrial plant protected by reactors, machinery, and laser security grids.",
        "theme_color": (239, 68, 68),
        "weather": "sparks",
        "base_target_score": 17000,
        "stages": [
            {"num": 1, "name": "Assembly Perimeter", "score": 5000, "hazard": "laser_grid"},
            {"num": 2, "name": "Reactor Trench", "score": 10500, "hazard": "debris"},
            {"num": 3, "name": "Stealth Mirage Core", "score": 17000, "hazard": "boss_stealth"}
        ]
    }
]

# -----------------------------------------------------------------------------
# Hangar Upgrades Catalog
# -----------------------------------------------------------------------------
UPGRADES = {
    "battery": {
        "name": "Battery Capacity",
        "desc": "Increases max drone integrity (+20 HP per lvl)",
        "base_cost": 50,
        "cost_mult": 1.5,
        "max_lvl": 5,
        "icon": "🔋"
    },
    "speed": {
        "name": "Thruster Agility",
        "desc": "Improves drone top flight speed and handling (+15% per lvl)",
        "base_cost": 45,
        "cost_mult": 1.5,
        "max_lvl": 5,
        "icon": "🚀"
    },
    "fire_rate": {
        "name": "Fire-Rate Overclock",
        "desc": "Decreases weapon cooldowns across all weapons (-12% per lvl)",
        "base_cost": 60,
        "cost_mult": 1.55,
        "max_lvl": 5,
        "icon": "⚡"
    },
    "emp_recharge": {
        "name": "EMP Quick-Charger",
        "desc": "Reduces EMP shockwave recharge time (-2.5s per lvl)",
        "base_cost": 75,
        "cost_mult": 1.6,
        "max_lvl": 4,
        "icon": "💥"
    },
    "wingman": {
        "name": "Wingman Escort Drone",
        "desc": "Deploys autonomous minidrones providing escort support",
        "base_cost": 150,
        "cost_mult": 1.8,
        "max_lvl": 3,
        "icon": "🛸"
    },
    "cloak": {
        "name": "Tactical Cloak Unit",
        "desc": "Equips tactical invisibility cloaking device [K]",
        "base_cost": 120,
        "cost_mult": 1.6,
        "max_lvl": 3,
        "icon": "👻"
    },
    "missiles": {
        "name": "Homing Missiles",
        "desc": "Unlocks and enhances seeking missile ordnance",
        "base_cost": 100,
        "cost_mult": 1.5,
        "max_lvl": 3,
        "icon": "🚀"
    },
    "beam": {
        "name": "Plasma Laser Beam",
        "desc": "Unlocks and boosts continuous laser cutting beam",
        "base_cost": 130,
        "cost_mult": 1.5,
        "max_lvl": 3,
        "icon": "⚡"
    },
    "tesla": {
        "name": "Arc Lightning Tesla",
        "desc": "Unlocks chain lightning electric cannon",
        "base_cost": 160,
        "cost_mult": 1.6,
        "max_lvl": 3,
        "icon": "🌩️"
    },
    "cluster": {
        "name": "Cluster Torpedo",
        "desc": "Unlocks heavy multi-bomblet cluster warhead",
        "base_cost": 180,
        "cost_mult": 1.65,
        "max_lvl": 3,
        "icon": "💣"
    },
    "overdrive": {
        "name": "Overdrive Reactor",
        "desc": "Enhances Overdrive duration and recharge speed",
        "base_cost": 200,
        "cost_mult": 1.7,
        "max_lvl": 3,
        "icon": "⚡"
    }
}

# -----------------------------------------------------------------------------
# Weapon Upgrade Catalog
# -----------------------------------------------------------------------------
WEAPON_UPGRADES = {
    "pulse": {
        "base_damage": 12,
        "base_cooldown": 0.18,
        "base_projectile_speed": 650.0,
        "upgrade_damage_per_lvl": 3,
        "upgrade_speed_per_lvl": 0.0,
        "upgrade_cooldown_per_lvl": -0.02,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "scatter": {
        "base_damage": 10,
        "base_cooldown": 0.75,
        "base_projectile_speed": 500.0,
        "upgrade_damage_per_lvl": 2,
        "upgrade_speed_per_lvl": 15.0,
        "upgrade_cooldown_per_lvl": -0.04,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "missile": {
        "base_damage": 65,
        "base_cooldown": 2.5,
        "base_projectile_speed": 260.0,
        "upgrade_damage_per_lvl": 15,
        "upgrade_speed_per_lvl": 20.0,
        "upgrade_cooldown_per_lvl": -0.15,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "rapid": {
        "base_damage": 8,
        "base_cooldown": 0.08,
        "base_projectile_speed": 980.0,
        "upgrade_damage_per_lvl": 2,
        "upgrade_speed_per_lvl": 0.0,
        "upgrade_cooldown_per_lvl": -0.005,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "plasma": {
        "base_damage": 90,
        "base_cooldown": 0.85,
        "base_projectile_speed": 460.0,
        "upgrade_damage_per_lvl": 20,
        "upgrade_speed_per_lvl": 15.0,
        "upgrade_cooldown_per_lvl": -0.06,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "rail": {
        "base_damage": 115,
        "base_cooldown": 1.10,
        "base_projectile_speed": 1800.0,
        "upgrade_damage_per_lvl": 25,
        "upgrade_speed_per_lvl": 0.0,
        "upgrade_cooldown_per_lvl": -0.08,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "barrage": {
        "base_damage": 38,
        "base_cooldown": 2.2,
        "base_projectile_speed": 620.0,
        "upgrade_damage_per_lvl": 8,
        "upgrade_speed_per_lvl": 20.0,
        "upgrade_cooldown_per_lvl": -0.12,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "beam": {
        "base_damage": 26,
        "base_cooldown": 0.08,
        "base_projectile_speed": 1500.0,
        "upgrade_damage_per_lvl": 6,
        "upgrade_speed_per_lvl": 0.0,
        "upgrade_cooldown_per_lvl": -0.005,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "tesla": {
        "base_damage": 44,
        "base_cooldown": 0.40,
        "base_projectile_speed": 1100.0,
        "upgrade_damage_per_lvl": 10,
        "upgrade_speed_per_lvl": 30.0,
        "upgrade_cooldown_per_lvl": -0.02,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "cluster": {
        "base_damage": 85,
        "base_cooldown": 2.0,
        "base_projectile_speed": 520.0,
        "upgrade_damage_per_lvl": 18,
        "upgrade_speed_per_lvl": 15.0,
        "upgrade_cooldown_per_lvl": -0.12,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    },
    "emp": {
        "base_damage": 30,
        "base_cooldown": 0.50,
        "base_projectile_speed": 1200.0,
        "upgrade_damage_per_lvl": 8,
        "upgrade_speed_per_lvl": 40.0,
        "upgrade_cooldown_per_lvl": -0.03,
        "max_level": 5,
        "cost_base": 200,
        "cost_mult": 1.6
    }
}

WEAPON_UNLOCK_COSTS = {
    "rapid": 300,
    "plasma": 400,
    "rail": 500,
    "barrage": 500,
    "beam": 400,
    "tesla": 600,
    "cluster": 700,
    "emp": 800
}

# -----------------------------------------------------------------------------
# Difficulty Modifiers & Presets
# -----------------------------------------------------------------------------
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NIGHTMARE = 3
DIFFICULTY_CUSTOM = 4

DIFFICULTY_NAMES = ["EASY", "NORMAL", "HARD", "NIGHTMARE", "CUSTOM"]

CUSTOM_DIFFICULTY_DEFAULTS = {
    "hp_mult": 1.0,
    "speed_mult": 1.0,
    "damage_mult": 1.0,
    "powerup_drop_rate": 0.30,
    "score_mult": 1.0
}

DIFFICULTY_MODIFIERS = {
    DIFFICULTY_EASY: {
        "name": "EASY",
        "hp_mult": 0.75,
        "speed_mult": 0.80,
        "damage_mult": 0.70,
        "powerup_drop_rate": 0.45,
        "score_mult": 0.80,
        "badge_color": COLOR_EMERALD
    },
    DIFFICULTY_NORMAL: {
        "name": "NORMAL",
        "hp_mult": 1.00,
        "speed_mult": 1.00,
        "damage_mult": 1.00,
        "powerup_drop_rate": 0.30,
        "score_mult": 1.00,
        "badge_color": COLOR_CYAN
    },
    DIFFICULTY_HARD: {
        "name": "HARD",
        "hp_mult": 1.35,
        "speed_mult": 1.20,
        "damage_mult": 1.30,
        "powerup_drop_rate": 0.20,
        "score_mult": 1.40,
        "badge_color": COLOR_GOLD
    },
    DIFFICULTY_NIGHTMARE: {
        "name": "NIGHTMARE",
        "hp_mult": 1.75,
        "speed_mult": 1.40,
        "damage_mult": 1.60,
        "powerup_drop_rate": 0.12,
        "score_mult": 2.00,
        "badge_color": COLOR_CRIMSON
    },
    DIFFICULTY_CUSTOM: {
        "name": "CUSTOM",
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "damage_mult": 1.0,
        "powerup_drop_rate": 0.30,
        "score_mult": 1.0,
        "badge_color": COLOR_MAGENTA
    }
}

def get_custom_difficulty(overrides: dict = None) -> dict:
    """Returns custom difficulty settings with optional overrides applied."""
    settings = CUSTOM_DIFFICULTY_DEFAULTS.copy()
    if overrides and isinstance(overrides, dict):
        for key, value in overrides.items():
            if key in settings:
                try:
                    settings[key] = max(0.5, min(3.0, float(value)))
                except (ValueError, TypeError):
                    pass
    return settings

