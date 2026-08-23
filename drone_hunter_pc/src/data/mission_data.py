"""
===============================================================================
                     DRONE HUNTER 2D - MISSION DATA (PHASE 5)
==============================================================================
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
        "theme": "Tropical coastal naval installations and island reef bases.",
        "environment": "ocean"
    },
    {
        "id": 2,
        "name": "CORE SECTOR",
        "theme": "Scorching sandstone canyons and industrial mining outposts.",
        "environment": "desert"
    },
    {
        "id": 3,
        "name": "REACTOR ZONE",
        "theme": "Dense tropical rainforest with river waterfalls and ruins.",
        "environment": "jungle"
    },
    {
        "id": 4,
        "name": "DEFENSE GRID",
        "theme": "Futuristic megacity skyline with neon rooftops and highways.",
        "environment": "city"
    },
    {
        "id": 5,
        "name": "DRONE COMMAND",
        "theme": "Automated industrial drone production plant and reactor core.",
        "environment": "cyber_factory"
    }
]

SIDE_OBJECTIVE_BONUS = {
    "collect_data_cores": 50,
    "no_damage_taken": 100,
    "time_limit": 75,
    "precision_strikes": 60,
}

MISSIONS = [
    # ---------------------------------------------------------
    # SECTOR 1 (CYBER FACTORY)
    # ---------------------------------------------------------
    {
        "id": "S1_M1", "sector_id": 1, "mission_number": 1,
        "name": "Perimeter Sweep", "difficulty": 1,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_PATROL, WAVE_SCOUTS_ASSAULT],
        "lore": "Allied recon drones picked up anomalous signals along the outermost perimeter fence. A light scout sweep will confirm whether the factory grounds are as quiet as intel suggests.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S1_M2", "sector_id": 1, "mission_number": 2,
        "name": "Factory Approach", "difficulty": 1,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_PATROL, WAVE_SHOOTERS_PAIR, WAVE_SHOOTERS_SQUAD],
        "lore": "The main assembly approach is crawling with automated sentries. Advance carefully and eliminate all hostiles before they can radio for reinforcements.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S1_M3", "sector_id": 1, "mission_number": 3,
        "name": "Security Breach", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_ASSAULT, WAVE_SHOOTERS_PAIR, WAVE_HEAVY_ESCORT],
        "lore": "A full security breach has been triggered in Sector 1's inner compound. Hostile drones are mobilizing in escalating waves. Hold the breach point until command gives the all-clear.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
        ]
    },
    {
        "id": "S1_M4", "sector_id": 1, "mission_number": 4,
        "name": "Production Line", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_PAIR, WAVE_SCOUTS_SWARM, WAVE_HEAVY_ESCORT],
        "lore": "The autonomous production line has been reprogrammed to churn out hostile units at an alarming rate. Sabotage key assembly nodes while surviving the drone onslaught.",
        "side_objectives": [
            {"type": "collect_data_cores", "value": 3},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S1_M5", "sector_id": 1, "mission_number": 5,
        "name": "Perimeter Collapse", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_ASSAULT, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT],
        "lore": "The outer perimeter has fully collapsed. What remains of the drone network is converging on your position. Crush the remaining resistance and claim the sector for the Alliance.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "precision_strikes", "value": 10},
        ]
    },

    # ---------------------------------------------------------
    # SECTOR 2 (CORE SECTOR)
    # ---------------------------------------------------------
    {
        "id": "S2_M1", "sector_id": 2, "mission_number": 1,
        "name": "Core Entry", "difficulty": 2,
        "objective": OBJECTIVE_DESTROY_ALL,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT],
        "lore": "You have breached the Core Sector boundary. Ancient mining drones have been repurposed as weapons — sweep the canyon entry and clear a path toward the reactor heart.",
        "side_objectives": [
            {"type": "collect_data_cores", "value": 3},
            {"type": "precision_strikes", "value": 10},
        ]
    },
    {
        "id": "S2_M2", "sector_id": 2, "mission_number": 2,
        "name": "Assembly Lines", "difficulty": 2,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_SQUAD, WAVE_SHIELD_VANGUARD, WAVE_HEAVY_ESCORT],
        "lore": "Deep within the canyon, automated assembly lines still produce shielded drone chassis. Intercept the production flow and destroy every unit rolling off the line.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
        ]
    },
    {
        "id": "S2_M3", "sector_id": 2, "mission_number": 3,
        "name": "Reactor Access", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The approach to the sector reactor is heavily fortified. Drone commanders have deployed shield vanguards and heavy battlegroups to protect the access corridor.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S2_M4", "sector_id": 2, "mission_number": 4,
        "name": "Security Grid", "difficulty": 3,
        "objective": OBJECTIVE_SURVIVE, "duration": 45,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_ESCORT],
        "lore": "The security grid has locked down and is flooding the sector with drones on a loop. Survive the 45-second onslaught until the grid overloads and resets.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S2_M5", "sector_id": 2, "mission_number": 5,
        "name": "Core Breach", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The reactor core itself is within reach. Elite drone formations guard the final approach. Shatter their lines and seize control of the Core Sector's power grid.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "no_damage_taken", "value": True},
        ]
    },

    # ---------------------------------------------------------
    # SECTOR 3 (REACTOR ZONE)
    # ---------------------------------------------------------
    {
        "id": "S3_M1", "sector_id": 3, "mission_number": 1,
        "name": "Reactor Approach", "difficulty": 3,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_SHOOTERS_SQUAD],
        "lore": "Dense rainforest canopy conceals the reactor approach. Shield drones and heavy units patrol the jungle floor — neutralize them before they can alert the main facility.",
        "side_objectives": [
            {"type": "time_limit", "value": 120},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S3_M2", "sector_id": 3, "mission_number": 2,
        "name": "Cooling Network", "difficulty": 3,
        "objective": OBJECTIVE_SURVIVE, "duration": 75,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "The cooling network has been weaponized — drones pour through the exhaust vents in a continuous 75-second deluge. Hold your position until the network's failsafe triggers.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "precision_strikes", "value": 10},
        ]
    },
    {
        "id": "S3_M3", "sector_id": 3, "mission_number": 3,
        "name": "Power Junction", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The power junction distributes energy across the entire sector. Drone commanders have deployed their most elite strike teams here. Eliminate every hostile to restore Alliance control.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S3_M4", "sector_id": 3, "mission_number": 4,
        "name": "Reactor Defense", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHOOTERS_SQUAD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "The reactor's automated defense systems have gone rogue. Heavy battlegroups and elite units are coordinating a coordinated counter-strike. Overwhelm them before the reactor goes critical.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S3_M5", "sector_id": 3, "mission_number": 5,
        "name": "Critical Overload", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "The reactor is moments from critical overload. The entire drone network has converged on the core chamber in a last stand. End them and stabilize the sector's power grid.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },

    # ---------------------------------------------------------
    # SECTOR 4 (DEFENSE GRID)
    # ---------------------------------------------------------
    {
        "id": "S4_M1", "sector_id": 4, "mission_number": 1,
        "name": "Outer Defense", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "Megacity outer defense drones have been weaponized by the enemy AI. Push through the shield vanguards and heavy battlegroups to reach the interceptor network.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S4_M2", "sector_id": 4, "mission_number": 2,
        "name": "Interceptor Grid", "difficulty": 4,
        "objective": OBJECTIVE_SURVIVE, "duration": 75,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The interceptor grid has locked onto all Alliance signatures. Survive 75 seconds of relentless drone waves until your ECM countermeasures force the grid to stand down.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S4_M3", "sector_id": 4, "mission_number": 3,
        "name": "Defense Network", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The integrated defense network coordinates every drone in the sector. Disrupt its command chain by destroying all units tied to its relay nodes before it can re-synchronize.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
        ]
    },
    {
        "id": "S4_M4", "sector_id": 4, "mission_number": 4,
        "name": "Central Firewall", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "The central firewall is the brain of the megacity defense grid. Elite strike forces are converging to protect it. Breach the firewall and take down the sector's command node.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S4_M5", "sector_id": 4, "mission_number": 5,
        "name": "Defense Collapse", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The entire megacity defense grid is collapsing around you. Every remaining drone unit is throwing itself at your position in a final, desperate defense. Survive and claim the sector.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },

    # ---------------------------------------------------------
    # SECTOR 5 (DRONE COMMAND)
    # ---------------------------------------------------------
    {
        "id": "S5_M1", "sector_id": 5, "mission_number": 1,
        "name": "Command Perimeter", "difficulty": 4,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "You have reached Drone Command's outermost perimeter. Swarm drones and shielded vanguards guard the approach. Push through and establish a foothold inside the production plant.",
        "side_objectives": [
            {"type": "collect_data_cores", "value": 3},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S5_M2", "sector_id": 5, "mission_number": 2,
        "name": "Tactical Network", "difficulty": 5,
        "objective": OBJECTIVE_SURVIVE, "duration": 90,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_SHIELD_VANGUARD],
        "lore": "The tactical network has detected your intrusion and is launching a 90-second barrage of elite drones and heavy units. Survive until the network's central processor is overwhelmed.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "precision_strikes", "value": 10},
        ]
    },
    {
        "id": "S5_M3", "sector_id": 5, "mission_number": 3,
        "name": "Command Core", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE],
        "lore": "Deep inside Drone Command, the core processor coordinates the entire enemy network. Elite guard rotations and heavy battlegroups stand between you and the command core terminal.",
        "side_objectives": [
            {"type": "precision_strikes", "value": 10},
            {"type": "no_damage_taken", "value": True},
            {"type": "collect_data_cores", "value": 3},
        ]
    },
    {
        "id": "S5_M4", "sector_id": 5, "mission_number": 4,
        "name": "Final Defense", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "The final defense line before the command core unleashes everything it has. Wave after wave of elite and heavy units pour into the chamber. Crush them and open the path to victory.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "precision_strikes", "value": 10},
            {"type": "time_limit", "value": 120},
        ]
    },
    {
        "id": "S5_M5", "sector_id": 5, "mission_number": 5,
        "name": "Drone Command", "difficulty": 5,
        "objective": OBJECTIVE_COMPLETE_ENCOUNTERS,
        "encounter_sequence": [WAVE_SCOUTS_SWARM, WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP],
        "lore": "This is it — the Drone Command central processor. The AI controlling the entire enemy network stands before you. Destroy every hostile unit and shut down the command core forever.",
        "side_objectives": [
            {"type": "no_damage_taken", "value": True},
            {"type": "precision_strikes", "value": 10},
            {"type": "collect_data_cores", "value": 3},
        ]
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
