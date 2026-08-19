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
HORIZONTAL_SPEED = 420.0
VERTICAL_SPEED = 360.0
ACCELERATION = 2600.0
FRICTION = 14.0

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
# Weapon Definitions
# -----------------------------------------------------------------------------
WEAPON_PULSE = "pulse"
WEAPON_SCATTER = "scatter"
WEAPON_MISSILE = "missile"
WEAPON_BEAM = "beam"
WEAPON_TESLA = "tesla"
WEAPON_CLUSTER = "cluster"

WEAPON_DEFS = {
    WEAPON_PULSE: {
        "name": "Pulse Laser",
        "cooldown": 0.18,
        "energy_cost": 2.5,
        "damage": 28,
        "speed": 920.0,
        "color": COLOR_CYAN,
        "description": "Rapid-fire dual plasma bolts.",
        "icon": "⚡",
        "unlocked_default": True
    },
    WEAPON_SCATTER: {
        "name": "Scatter Cannon",
        "cooldown": 0.38,
        "energy_cost": 6.0,
        "damage": 18,
        "speed": 860.0,
        "color": COLOR_GOLD,
        "description": "Short-range multi-pellet spread.",
        "icon": "💥",
        "unlocked_default": True
    },
    WEAPON_MISSILE: {
        "name": "Homing Missiles",
        "cooldown": 0.55,
        "energy_cost": 10.0,
        "damage": 65,
        "speed": 680.0,
        "color": COLOR_MISSILE,
        "description": "Target-seeking guided ordnance.",
        "icon": "🚀",
        "unlocked_default": False
    },
    WEAPON_BEAM: {
        "name": "Plasma Beam",
        "cooldown": 0.08,
        "energy_cost": 12.0,
        "damage": 14,
        "speed": 1500.0,
        "color": COLOR_BEAM,
        "description": "Continuous high-intensity cutting beam.",
        "icon": "⚡",
        "unlocked_default": False
    },
    WEAPON_TESLA: {
        "name": "Tesla Arc Cannon",
        "cooldown": 0.32,
        "energy_cost": 8.0,
        "damage": 42,
        "speed": 1100.0,
        "color": COLOR_TESLA,
        "description": "Electric bolt chaining to nearby hostiles.",
        "icon": "🌩️",
        "unlocked_default": False
    },
    WEAPON_CLUSTER: {
        "name": "Cluster Torpedo",
        "cooldown": 0.70,
        "energy_cost": 14.0,
        "damage": 80,
        "speed": 520.0,
        "color": COLOR_CLUSTER,
        "description": "Heavy torpedo splitting into 6 bomblets.",
        "icon": "💣",
        "unlocked_default": False
    }
}

# -----------------------------------------------------------------------------
# Enemy & Boss Type Identifiers
# -----------------------------------------------------------------------------
TARGET_TYPE_SCOUT = "scout"                       # Phase 2A Scout Drone (Mobile Melee Pressure)
TARGET_TYPE_SHOOTER = "shooter"                   # Phase 2B Shooter Drone (Positioning Pressure)
TARGET_TYPE_HEAVY = "heavy"                       # Phase 2C Heavy Drone (Target Prioritization Pressure)
TARGET_TYPE_STANDARD = "standard"
TARGET_TYPE_FAST = "fast"
TARGET_TYPE_ARMORED = "armored"
TARGET_TYPE_TURRET = "turret"
TARGET_TYPE_VEHICLE = "vehicle"
TARGET_TYPE_CHASER = "chaser"
TARGET_TYPE_SWARM = "swarm"
TARGET_TYPE_SHIELD_DRONE = "shield_drone"
TARGET_TYPE_SNIPER = "sniper"

TARGET_TYPE_BOSS = "boss"                         # Sky Dreadnought (Sector 1)
TARGET_TYPE_STEALTH_MIRAGE = "stealth_mirage"     # Stealth Mirage (Sector 2)
TARGET_TYPE_EMP_DISRUPTER = "emp_disrupter"       # EMP Disrupter (Sector 3)
TARGET_TYPE_TITAN_MECH = "titan_mech"             # Colossus Titan Mech (Sector 5)

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
# Campaign Sectors & Stages
# -----------------------------------------------------------------------------
SECTORS = [
    {
        "id": 0,
        "name": "Megacity Skyline",
        "desc": "High-altitude cyberpunk skyscrapers amidst neon downpours.",
        "theme_color": COLOR_CYAN,
        "weather": "rain",
        "base_target_score": 5000,
        "stages": [
            {"num": 1, "name": "Rooftop Recon", "score": 1500, "hazard": "none"},
            {"num": 2, "name": "Skyline Skirmish", "score": 3200, "hazard": "debris"},
            {"num": 3, "name": "Dreadnought Intercept", "score": 5500, "hazard": "boss_dreadnought"}
        ]
    },
    {
        "id": 1,
        "name": "Cyber Factory Core",
        "desc": "Automated molten foundry protected by laser defense grids.",
        "theme_color": COLOR_GOLD,
        "weather": "sparks",
        "base_target_score": 7500,
        "stages": [
            {"num": 1, "name": "Assembly Perimeter", "score": 2200, "hazard": "laser_grid"},
            {"num": 2, "name": "Smelting Chambers", "score": 4500, "hazard": "debris"},
            {"num": 3, "name": "Stealth Mirage Core", "score": 7500, "hazard": "boss_stealth"}
        ]
    },
    {
        "id": 2,
        "name": "Orbital Space Citadel",
        "desc": "Deep space fortress surrounded by asteroid belts and gravitational anomalies.",
        "theme_color": COLOR_MAGENTA,
        "weather": "meteor",
        "base_target_score": 10000,
        "stages": [
            {"num": 1, "name": "Citadel Approach", "score": 3000, "hazard": "gravity_well"},
            {"num": 2, "name": "Orbital Trench", "score": 6200, "hazard": "debris"},
            {"num": 3, "name": "EMP Disrupter Bastion", "score": 10000, "hazard": "boss_emp"}
        ]
    },
    {
        "id": 3,
        "name": "Stormy Ocean Battlescape",
        "desc": "Raging naval sea trench with explosive floating mines.",
        "theme_color": (14, 165, 233),
        "weather": "storm",
        "base_target_score": 13000,
        "stages": [
            {"num": 1, "name": "Reef Recon", "score": 4000, "hazard": "sea_mines"},
            {"num": 2, "name": "Typhoon Assault", "score": 8000, "hazard": "storm_winds"},
            {"num": 3, "name": "Naval Dreadnought Clash", "score": 13000, "hazard": "boss_dreadnought"}
        ]
    },
    {
        "id": 4,
        "name": "Neon Sun Wasteland",
        "desc": "Scorching desert wasteland guarded by the supreme Colossus Titan Mech.",
        "theme_color": (239, 68, 68),
        "weather": "sandstorm",
        "base_target_score": 17000,
        "stages": [
            {"num": 1, "name": "Dune Outpost", "score": 5000, "hazard": "gravity_well"},
            {"num": 2, "name": "Scorched Trench", "score": 10500, "hazard": "laser_grid"},
            {"num": 3, "name": "Colossus Titan Showdown", "score": 17000, "hazard": "boss_titan"}
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
# Difficulty Modifiers & Presets
# -----------------------------------------------------------------------------
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NIGHTMARE = 3

DIFFICULTY_NAMES = ["EASY", "NORMAL", "HARD", "NIGHTMARE"]

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
    }
}

# -----------------------------------------------------------------------------
# Drone Skins Catalog
# -----------------------------------------------------------------------------
DRONE_SKINS = [
    {
        "id": 0,
        "name": "PLATINUM VANGUARD",
        "body_color": (30, 41, 59),
        "primary_color": (14, 165, 233),
        "accent_color": (226, 232, 240),
        "glow_color": (56, 189, 248)
    },
    {
        "id": 1,
        "name": "CYBERNEON PHANTOM",
        "body_color": (20, 10, 35),
        "primary_color": (217, 70, 239),
        "accent_color": (6, 182, 212),
        "glow_color": (236, 72, 153)
    },
    {
        "id": 2,
        "name": "SOVEREIGN GOLD",
        "body_color": (35, 28, 10),
        "primary_color": (245, 158, 11),
        "accent_color": (250, 204, 21),
        "glow_color": (253, 224, 71)
    },
    {
        "id": 3,
        "name": "CRIMSON WIDOW",
        "body_color": (35, 10, 15),
        "primary_color": (225, 29, 72),
        "accent_color": (244, 63, 94),
        "glow_color": (255, 30, 60)
    },
    {
        "id": 4,
        "name": "VOID STEALTH",
        "body_color": (10, 15, 20),
        "primary_color": (139, 92, 246),
        "accent_color": (99, 102, 241),
        "glow_color": (168, 85, 247)
    },
    {
        "id": 5,
        "name": "SOLAR FLARE",
        "body_color": (30, 20, 10),
        "primary_color": (255, 107, 0),
        "accent_color": (255, 180, 0),
        "glow_color": (255, 140, 0)
    }
]
