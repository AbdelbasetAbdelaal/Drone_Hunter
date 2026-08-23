"""
================================================================================
            DRONE HUNTER 2D - OBJECTIVE ASSAULT DATA SPECIFICATIONS
================================================================================
Authoritative data definitions for Ground Objectives, Defense Levels,
Radar Networks, Anti-Air Platforms, Shield Generators, and Combat Aircraft.
"""

from src.data.settings import (
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_EMERALD, COLOR_WHITE,
    COLOR_SHIELD, COLOR_NEON_RED
)

# -----------------------------------------------------------------------------
# OBJECTIVE TYPES
# -----------------------------------------------------------------------------
OBJECTIVE_TYPE_RADAR_COMMAND    = "radar_command"
OBJECTIVE_TYPE_MISSILE_COMPLEX   = "missile_complex"
OBJECTIVE_TYPE_POWER_REACTOR     = "power_reactor"
OBJECTIVE_TYPE_COMMUNICATION_HUB = "communication_hub"
OBJECTIVE_TYPE_CYBER_DEFENSE_CORE= "cyber_defense_core"
OBJECTIVE_TYPE_WEAPONS_FACTORY   = "weapons_factory"

# -----------------------------------------------------------------------------
# DEFENSE LEVEL CONSTANTS
# -----------------------------------------------------------------------------
DEFENSE_LEVEL_1 = 1
DEFENSE_LEVEL_2 = 2
DEFENSE_LEVEL_3 = 3
DEFENSE_LEVEL_4 = 4
DEFENSE_LEVEL_5 = 5

# -----------------------------------------------------------------------------
# RADAR STATES & TYPES
# -----------------------------------------------------------------------------
RADAR_STATE_SCANNING  = "scanning"
RADAR_STATE_ALERT     = "alert"
RADAR_STATE_DESTROYED = "destroyed"

# -----------------------------------------------------------------------------
# AA PLATFORM TYPES
# -----------------------------------------------------------------------------
AA_TYPE_LIGHT   = "light_aa"
AA_TYPE_HEAVY   = "heavy_aa"
AA_TYPE_MISSILE = "missile_launcher"

# -----------------------------------------------------------------------------
# AIRCRAFT TYPES
# -----------------------------------------------------------------------------
AIRCRAFT_INTERCEPTOR = "aircraft_interceptor"
AIRCRAFT_ATTACK      = "aircraft_attack"

# -----------------------------------------------------------------------------
# OBJECTIVE CATALOG DEFINITIONS
# -----------------------------------------------------------------------------
OBJECTIVE_CATALOG = {
    OBJECTIVE_TYPE_RADAR_COMMAND: {
        "id": OBJECTIVE_TYPE_RADAR_COMMAND,
        "name": "Radar Command Center",
        "title": "PRIMARY RADAR COMMAND",
        "description": "Hardened early-warning array coordinating regional hostile air defense grids.",
        "base_hp": 320,
        "armor": 0.15,
        "size": 110,
        "color_outer": (30, 41, 59),
        "color_inner": COLOR_CYAN,
        "reward_score": 3500,
        "reward_scrap": 120,
    },
    OBJECTIVE_TYPE_MISSILE_COMPLEX: {
        "id": OBJECTIVE_TYPE_MISSILE_COMPLEX,
        "name": "Missile Silo Complex",
        "title": "TACTICAL MISSILE SILO",
        "description": "Reinforced underground missile launch complex threatening orbital transport corridors.",
        "base_hp": 420,
        "armor": 0.20,
        "size": 120,
        "color_outer": (51, 65, 85),
        "color_inner": COLOR_CRIMSON,
        "reward_score": 4200,
        "reward_scrap": 150,
    },
    OBJECTIVE_TYPE_POWER_REACTOR: {
        "id": OBJECTIVE_TYPE_POWER_REACTOR,
        "name": "Sub-Level Power Reactor",
        "title": "CRITICAL POWER REACTOR",
        "description": "High-output thermal reactor powering automated defense grids and factory foundries.",
        "base_hp": 500,
        "armor": 0.25,
        "size": 130,
        "color_outer": (15, 23, 42),
        "color_inner": COLOR_GOLD,
        "reward_score": 5000,
        "reward_scrap": 180,
    },
    OBJECTIVE_TYPE_COMMUNICATION_HUB: {
        "id": OBJECTIVE_TYPE_COMMUNICATION_HUB,
        "name": "Tactical Communications Relay",
        "title": "COMMUNICATION RELAY HUB",
        "description": "High-frequency neural transmitter transmitting telemetry to hostile drone squadrons.",
        "base_hp": 380,
        "armor": 0.18,
        "size": 115,
        "color_outer": (30, 58, 138),
        "color_inner": (56, 189, 248),
        "reward_score": 3800,
        "reward_scrap": 140,
    },
    OBJECTIVE_TYPE_CYBER_DEFENSE_CORE: {
        "id": OBJECTIVE_TYPE_CYBER_DEFENSE_CORE,
        "name": "Cyber Defense Core",
        "title": "AUTONOMOUS DEFENSE CORE",
        "description": "Central cybernetic processing nexus controlling regional automated war machines.",
        "base_hp": 600,
        "armor": 0.30,
        "size": 140,
        "color_outer": (88, 28, 135),
        "color_inner": (217, 70, 239),
        "reward_score": 6500,
        "reward_scrap": 240,
    },
    OBJECTIVE_TYPE_WEAPONS_FACTORY: {
        "id": OBJECTIVE_TYPE_WEAPONS_FACTORY,
        "name": "Munitions Foundry",
        "title": "WEAPONS FABRICATION CORE",
        "description": "Mass-production assembly facility constructing heavy armor plates and ordnance.",
        "base_hp": 460,
        "armor": 0.22,
        "size": 125,
        "color_outer": (68, 64, 60),
        "color_inner": (249, 115, 22),
        "reward_score": 4500,
        "reward_scrap": 160,
    },
}

# -----------------------------------------------------------------------------
# DEFENSE LEVEL PRESETS
# -----------------------------------------------------------------------------
DEFENSE_LEVEL_CONFIGS = {
    DEFENSE_LEVEL_1: {
        "defense_level": 1,
        "radar_nodes": 0,
        "aa_platforms": 1,
        "aa_types": [AA_TYPE_LIGHT],
        "shield_generators": 0,
        "aircraft_count": 0,
        "reinforcement_max": 2,
        "reinforcement_interval": 12.0,
        "hp_mult": 1.0,
    },
    DEFENSE_LEVEL_2: {
        "defense_level": 2,
        "radar_nodes": 1,
        "aa_platforms": 2,
        "aa_types": [AA_TYPE_LIGHT, AA_TYPE_LIGHT],
        "shield_generators": 0,
        "aircraft_count": 1,
        "reinforcement_max": 3,
        "reinforcement_interval": 10.0,
        "hp_mult": 1.15,
    },
    DEFENSE_LEVEL_3: {
        "defense_level": 3,
        "radar_nodes": 1,
        "aa_platforms": 3,
        "aa_types": [AA_TYPE_LIGHT, AA_TYPE_HEAVY, AA_TYPE_MISSILE],
        "shield_generators": 1,
        "aircraft_count": 2,
        "reinforcement_max": 4,
        "reinforcement_interval": 8.5,
        "hp_mult": 1.30,
    },
    DEFENSE_LEVEL_4: {
        "defense_level": 4,
        "radar_nodes": 2,
        "aa_platforms": 4,
        "aa_types": [AA_TYPE_HEAVY, AA_TYPE_HEAVY, AA_TYPE_MISSILE, AA_TYPE_LIGHT],
        "shield_generators": 2,
        "aircraft_count": 3,
        "reinforcement_max": 5,
        "reinforcement_interval": 7.0,
        "hp_mult": 1.50,
    },
    DEFENSE_LEVEL_5: {
        "defense_level": 5,
        "radar_nodes": 3,
        "aa_platforms": 5,
        "aa_types": [AA_TYPE_HEAVY, AA_TYPE_HEAVY, AA_TYPE_MISSILE, AA_TYPE_MISSILE, AA_TYPE_LIGHT],
        "shield_generators": 3,
        "aircraft_count": 4,
        "reinforcement_max": 6,
        "reinforcement_interval": 6.0,
        "hp_mult": 1.75,
    },
}

def get_objective_catalog_def(obj_type: str) -> dict:
    """Returns definition dictionary for given objective archetype."""
    return OBJECTIVE_CATALOG.get(obj_type, OBJECTIVE_CATALOG[OBJECTIVE_TYPE_RADAR_COMMAND])

def get_defense_level_config(level: int) -> dict:
    """Returns defense configuration corresponding to level 1-5."""
    return DEFENSE_LEVEL_CONFIGS.get(level, DEFENSE_LEVEL_CONFIGS[DEFENSE_LEVEL_1])
