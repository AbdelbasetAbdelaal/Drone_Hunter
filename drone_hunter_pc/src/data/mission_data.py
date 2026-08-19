"""
================================================================================
                    DRONE HUNTER 2D - MISSION DATA (PHASE 5)
================================================================================
Definitions for all 25 playable missions across 5 sectors.
"""

from src.systems.encounter_system import (
    SCOUT_INTRO_ENCOUNTER,
    SHOOTER_INTRO_ENCOUNTER,
    HEAVY_INTRO_ENCOUNTER,
    SCOUT_SHOOTER_ENCOUNTER,
    SCOUT_HEAVY_ENCOUNTER,
    SHOOTER_HEAVY_ENCOUNTER,
    SCOUT_SHOOTER_HEAVY_ENCOUNTER,
    WAVE_SCOUTS_PATROL,
    WAVE_SCOUTS_ASSAULT,
    WAVE_SCOUTS_SWARM,
    WAVE_SHOOTERS_PAIR,
    WAVE_SHOOTERS_SQUAD,
    WAVE_HEAVY_ESCORT,
    WAVE_HEAVY_BATTLEGROUP,
    WAVE_SHIELD_VANGUARD,
    WAVE_ELITE_STRIKE_FORCE
)

# Objective Types
OBJECTIVE_DESTROY_ALL = "destroy_all"
OBJECTIVE_SURVIVE = "survive"
OBJECTIVE_COMPLETE_ENCOUNTERS = "complete_encounters"

# Scrap Rewards
MISSION_REWARDS = {
    1: 150,
    2: 250,
    3: 400,
    4: 600,
    5: 900
}

SECTOR_BONUS = {
    1: 500,
    2: 750,
    3: 1000,
    4: 1500,
    5: 2500
}

SECTORS_PHASE5 = [
    {
        "id": 1,
        "name": "CYBER FACTORY",
        "theme": "Industrial drone production plant."
    },
    {
        "id": 2,
        "name": "CORE SECTOR",
        "theme": "Heavily defended reactor core complex."
    },
    {
        "id": 3,
        "name": "REACTOR ZONE",
        "theme": "Volatile energy conduits and plasma machinery."
    },
    {
        "id": 4,
        "name": "DEFENSE GRID",
        "theme": "Fortified automated defense installations."
    },
    {
        "id": 5,
        "name": "DRONE COMMAND",
        "theme": "Enemy command infrastructure."
    }
]

MISSIONS = [
    # ---------------------------------------------------------
    # SECTOR 1 (CYBER FACTORY)
    # ---------------------------------------------------------
    {
        "id": "S1_M1", "sector_id": 1, "mission_number": 1,
        "name": "Perimeter Sweep", "difficulty": 1,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_PATROL, WAVE_SCOUTS_ASSAULT]
    },
    {
        "id": "S1_M2", "sector_id": 1, "mission_number": 2,
        "name": "Factory Approach", "difficulty": 1,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_PATROL, WAVE_SHOOTERS_PAIR, WAVE_SHOOTERS_SQUAD]
    },
    {
        "id": "S1_M3", "sector_id": 1, "mission_number": 3,
        "name": "Security Breach", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_ASSAULT, WAVE_SHOOTERS_PAIR, WAVE_HEAVY_ESCORT]
    },
    {
        "id": "S1_M4", "sector_id": 1, "mission_number": 4,
        "name": "Production Line", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_PAIR, WAVE_SCOUTS_SWARM, WAVE_HEAVY_ESCORT]
    },
    {
        "id": "S1_M5", "sector_id": 1, "mission_number": 5,
        "name": "Perimeter Collapse", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_ASSAULT, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT]
    },

    # ---------------------------------------------------------
    # SECTOR 2 (CORE SECTOR)
    # ---------------------------------------------------------
    {
        "id": "S2_M1", "sector_id": 2, "mission_number": 1,
        "name": "Core Entry", "difficulty": 2,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT]
    },
    {
        "id": "S2_M2", "sector_id": 2, "mission_number": 2,
        "name": "Assembly Lines", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_SQUAD, WAVE_SHIELD_VANGUARD, WAVE_HEAVY_ESCORT]
    },
    {
        "id": "S2_M3", "sector_id": 2, "mission_number": 3,
        "name": "Reactor Access", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S2_M4", "sector_id": 2, "mission_number": 4,
        "name": "Security Grid", "difficulty": 3,
        "objective": OBJECTIVE_SURVIVE, "duration": 45,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT]
    },
    {
        "id": "S2_M5", "sector_id": 2, "mission_number": 5,
        "name": "Core Breach", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_BATTLEGROUP]
    },

    # ---------------------------------------------------------
    # SECTOR 3 (REACTOR ZONE)
    # ---------------------------------------------------------
    {
        "id": "S3_M1", "sector_id": 3, "mission_number": 1,
        "name": "Reactor Approach", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_SHOOTERS_SQUAD]
    },
    {
        "id": "S3_M2", "sector_id": 3, "mission_number": 2,
        "name": "Cooling Network", "difficulty": 3,
        "objective": OBJECTIVE_SURVIVE, "duration": 75,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },
    {
        "id": "S3_M3", "sector_id": 3, "mission_number": 3,
        "name": "Power Junction", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S3_M4", "sector_id": 3, "mission_number": 4,
        "name": "Reactor Defense", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },
    {
        "id": "S3_M5", "sector_id": 3, "mission_number": 5,
        "name": "Critical Overload", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },

    # ---------------------------------------------------------
    # SECTOR 4 (DEFENSE GRID)
    # ---------------------------------------------------------
    {
        "id": "S4_M1", "sector_id": 4, "mission_number": 1,
        "name": "Outer Defense", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },
    {
        "id": "S4_M2", "sector_id": 4, "mission_number": 2,
        "name": "Interceptor Grid", "difficulty": 4,
        "objective": OBJECTIVE_SURVIVE, "duration": 75,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S4_M3", "sector_id": 4, "mission_number": 3,
        "name": "Defense Network", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S4_M4", "sector_id": 4, "mission_number": 4,
        "name": "Central Firewall", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },
    {
        "id": "S4_M5", "sector_id": 4, "mission_number": 5,
        "name": "Defense Collapse", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },

    # ---------------------------------------------------------
    # SECTOR 5 (DRONE COMMAND)
    # ---------------------------------------------------------
    {
        "id": "S5_M1", "sector_id": 5, "mission_number": 1,
        "name": "Command Perimeter", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S5_M2", "sector_id": 5, "mission_number": 2,
        "name": "Tactical Network", "difficulty": 5,
        "objective": OBJECTIVE_SURVIVE, "duration": 90,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_SHIELD_VANGUARD]
    },
    {
        "id": "S5_M3", "sector_id": 5, "mission_number": 3,
        "name": "Command Core", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]
    },
    {
        "id": "S5_M4", "sector_id": 5, "mission_number": 4,
        "name": "Final Defense", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    },
    {
        "id": "S5_M5", "sector_id": 5, "mission_number": 5,
        "name": "Drone Command", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP]
    }
]

def get_mission_data(mission_id: str) -> dict:
    for m in MISSIONS:
        if m["id"] == mission_id:
            return m
    return None

def get_sector_data(sector_id: int) -> dict:
    for s in SECTORS_PHASE5:
        if s["id"] == sector_id:
            return s
    return None

def get_missions_for_sector(sector_id: int) -> list:
    return [m for m in MISSIONS if m["sector_id"] == sector_id]
