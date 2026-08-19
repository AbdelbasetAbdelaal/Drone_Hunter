"""
================================================================================
                    DRONE HUNTER 2D - BOSS DATA (PHASE 6)
================================================================================
Data-driven specifications for all 5 Sector Bosses and the Final Boss encounter.
Defines multi-phase configurations, attack pattern rules, telegraphs, movement,
reinforcements, and rewards.
"""

from typing import List, Dict, Any, Optional

# Boss Identifiers
BOSS_ASSEMBLY_WARDEN = "assembly_warden"
BOSS_CORE_EXECUTOR = "core_executor"
BOSS_REACTOR_TITAN = "reactor_titan"
BOSS_DEFENSE_COMMANDER = "defense_commander"
BOSS_DRONE_OVERLORD = "drone_overlord"

# Reusable Attack Pattern Types
ATTACK_RADIAL_BURST = "radial_burst"
ATTACK_SPREAD_BARRAGE = "spread_barrage"
ATTACK_TARGETED_SHOT = "targeted_shot"
ATTACK_HOMING_VOLLEY = "homing_volley"
ATTACK_LASER_SWEEP = "laser_sweep"
ATTACK_ENERGY_WAVE = "energy_wave"
ATTACK_MISSILE_SALVO = "missile_salvo"
ATTACK_DRONE_DEPLOY = "drone_deploy"

# Boss Movement Modes
MOVE_PATROL_HORIZONTAL = "patrol_horizontal"
MOVE_PATROL_VERTICAL = "patrol_vertical"
MOVE_FIGURE_EIGHT = "figure_eight"
MOVE_HOVER_TRACK = "hover_track"
MOVE_AGGRESSIVE_SWEEP = "aggressive_sweep"


class BossAttackConfig:
    def __init__(self, attack_type: str, cooldown: float, telegraph_time: float = 0.5,
                 duration: float = 0.5, damage: int = 15, speed: float = 340.0,
                 count: int = 1, spread_deg: float = 0.0, extra: Optional[Dict[str, Any]] = None):
        self.attack_type = attack_type
        self.cooldown = cooldown
        self.telegraph_time = telegraph_time
        self.duration = duration
        self.damage = damage
        self.speed = speed
        self.count = count
        self.spread_deg = spread_deg
        self.extra = extra or {}


class BossPhaseConfig:
    def __init__(self, phase_index: int, hp_threshold: float, name: str,
                 movement_mode: str, speed: float, armor: float = 0.0,
                 has_shield: bool = False, shield_duration: float = 0.0,
                 attacks: Optional[List[BossAttackConfig]] = None,
                 reinforcements: Optional[Dict[str, Any]] = None):
        self.phase_index = phase_index
        self.hp_threshold = hp_threshold  # e.g. 1.0 (100%), 0.70 (70%), 0.35 (35%)
        self.name = name
        self.movement_mode = movement_mode
        self.speed = speed
        self.armor = armor
        self.has_shield = has_shield
        self.shield_duration = shield_duration
        self.attacks = attacks or []
        self.reinforcements = reinforcements  # {"enemy_types": [...], "interval": 10.0, "max_active": 2}


class BossDefinition:
    def __init__(self, id: str, name: str, sector_id: int, mission_id: str, role: str,
                 max_hp: int, contact_damage: float, size: int,
                 color_outer: tuple, color_inner: tuple,
                 phases: List[BossPhaseConfig],
                 reward_scrap: int, reward_score: int,
                 max_projectiles: int = 24, max_reinforcements: int = 3):
        self.id = id
        self.name = name
        self.sector_id = sector_id
        self.mission_id = mission_id
        self.role = role
        self.max_hp = max_hp
        self.contact_damage = contact_damage
        self.size = size
        self.color_outer = color_outer
        self.color_inner = color_inner
        self.phases = phases
        self.reward_scrap = reward_scrap
        self.reward_score = reward_score
        self.max_projectiles = max_projectiles
        self.max_reinforcements = max_reinforcements


# =============================================================================
# 1. SECTOR 1 BOSS: ASSEMBLY WARDEN (Industrial Defense Commander)
# =============================================================================
ASSEMBLY_WARDEN_CONFIG = BossDefinition(
    id=BOSS_ASSEMBLY_WARDEN,
    name="ASSEMBLY WARDEN",
    sector_id=1,
    mission_id="S1_M5",
    role="Industrial Defense Commander",
    max_hp=450,
    contact_damage=25.0,
    size=90,
    color_outer=(225, 29, 72),      # Rose Crimson
    color_inner=(250, 204, 21),     # Amber Gold
    phases=[
        BossPhaseConfig(
            phase_index=1,
            hp_threshold=1.0,
            name="PHASE 1",
            movement_mode=MOVE_PATROL_VERTICAL,
            speed=75.0,
            armor=0.0,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=2.0,
                    telegraph_time=0.4,
                    damage=14,
                    speed=360.0,
                    count=3,
                    spread_deg=24.0
                )
            ]
        ),
        BossPhaseConfig(
            phase_index=2,
            hp_threshold=0.70,
            name="PHASE 2",
            movement_mode=MOVE_FIGURE_EIGHT,
            speed=90.0,
            armor=0.05,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    damage=12,
                    speed=330.0,
                    count=8
                ),
                BossAttackConfig(
                    attack_type=ATTACK_TARGETED_SHOT,
                    cooldown=2.2,
                    telegraph_time=0.35,
                    damage=16,
                    speed=420.0,
                    count=2
                )
            ],
            reinforcements={
                "enemy_types": ["scout"],
                "interval": 8.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=3,
            hp_threshold=0.35,
            name="PHASE 3",
            movement_mode=MOVE_AGGRESSIVE_SWEEP,
            speed=110.0,
            armor=0.10,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=2.6,
                    telegraph_time=0.4,
                    damage=14,
                    speed=360.0,
                    count=10
                ),
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=1.8,
                    telegraph_time=0.3,
                    damage=16,
                    speed=400.0,
                    count=5,
                    spread_deg=35.0
                )
            ],
            reinforcements={
                "enemy_types": ["scout"],
                "interval": 6.5,
                "max_active": 2
            }
        )
    ],
    reward_scrap=300,
    reward_score=1500,
    max_projectiles=20,
    max_reinforcements=2
)


# =============================================================================
# 2. SECTOR 2 BOSS: CORE EXECUTOR (Heavy Industrial Platform)
# =============================================================================
CORE_EXECUTOR_CONFIG = BossDefinition(
    id=BOSS_CORE_EXECUTOR,
    name="CORE EXECUTOR",
    sector_id=2,
    mission_id="S2_M5",
    role="Heavy Industrial Combat Platform",
    max_hp=750,
    contact_damage=30.0,
    size=100,
    color_outer=(234, 88, 12),      # Industrial Orange
    color_inner=(255, 255, 255),    # White Core
    phases=[
        BossPhaseConfig(
            phase_index=1,
            hp_threshold=1.0,
            name="PHASE 1",
            movement_mode=MOVE_HOVER_TRACK,
            speed=60.0,
            armor=0.10,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_TARGETED_SHOT,
                    cooldown=2.0,
                    telegraph_time=0.4,
                    damage=20,
                    speed=380.0,
                    count=2
                ),
                BossAttackConfig(
                    attack_type=ATTACK_MISSILE_SALVO,
                    cooldown=4.0,
                    telegraph_time=0.6,
                    damage=35,
                    speed=280.0,
                    count=2
                )
            ]
        ),
        BossPhaseConfig(
            phase_index=2,
            hp_threshold=0.70,
            name="PHASE 2",
            movement_mode=MOVE_PATROL_HORIZONTAL,
            speed=80.0,
            armor=0.25,  # Reinforced Armor
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=2.4,
                    telegraph_time=0.45,
                    damage=18,
                    speed=360.0,
                    count=5,
                    spread_deg=30.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_HOMING_VOLLEY,
                    cooldown=4.5,
                    telegraph_time=0.6,
                    damage=30,
                    speed=320.0,
                    count=2
                )
            ],
            reinforcements={
                "enemy_types": ["shooter"],
                "interval": 9.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=3,
            hp_threshold=0.35,
            name="PHASE 3",
            movement_mode=MOVE_AGGRESSIVE_SWEEP,
            speed=100.0,
            armor=0.15,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_HOMING_VOLLEY,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    damage=30,
                    speed=340.0,
                    count=3
                ),
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=1.9,
                    telegraph_time=0.35,
                    damage=20,
                    speed=400.0,
                    count=5,
                    spread_deg=36.0
                )
            ],
            reinforcements={
                "enemy_types": ["shooter", "scout"],
                "interval": 7.0,
                "max_active": 2
            }
        )
    ],
    reward_scrap=500,
    reward_score=2500,
    max_projectiles=22,
    max_reinforcements=2
)


# =============================================================================
# 3. SECTOR 3 BOSS: REACTOR TITAN (Reactor-Powered Combat Machine)
# =============================================================================
REACTOR_TITAN_CONFIG = BossDefinition(
    id=BOSS_REACTOR_TITAN,
    name="REACTOR TITAN",
    sector_id=3,
    mission_id="S3_M5",
    role="Reactor Heavy Platform",
    max_hp=1100,
    contact_damage=35.0,
    size=110,
    color_outer=(168, 85, 247),     # Plasma Purple
    color_inner=(56, 189, 248),     # Cyan Core
    phases=[
        BossPhaseConfig(
            phase_index=1,
            hp_threshold=1.0,
            name="PHASE 1",
            movement_mode=MOVE_HOVER_TRACK,
            speed=55.0,
            armor=0.10,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_ENERGY_WAVE,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    damage=22,
                    speed=350.0,
                    count=6,
                    spread_deg=45.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_TARGETED_SHOT,
                    cooldown=1.8,
                    telegraph_time=0.35,
                    damage=18,
                    speed=420.0,
                    count=3
                )
            ]
        ),
        BossPhaseConfig(
            phase_index=2,
            hp_threshold=0.70,
            name="PHASE 2",
            movement_mode=MOVE_PATROL_VERTICAL,
            speed=75.0,
            armor=0.15,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_LASER_SWEEP,
                    cooldown=3.8,
                    telegraph_time=0.6,
                    duration=0.8,
                    damage=28,
                    speed=450.0,
                    count=4,
                    spread_deg=30.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=3.0,
                    telegraph_time=0.45,
                    damage=16,
                    speed=340.0,
                    count=12
                )
            ],
            reinforcements={
                "enemy_types": ["heavy"],
                "interval": 12.0,
                "max_active": 1
            }
        ),
        BossPhaseConfig(
            phase_index=3,
            hp_threshold=0.35,
            name="REACTOR OVERLOAD",
            movement_mode=MOVE_FIGURE_EIGHT,
            speed=95.0,
            armor=0.20,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_ENERGY_WAVE,
                    cooldown=2.5,
                    telegraph_time=0.4,
                    damage=25,
                    speed=380.0,
                    count=8,
                    spread_deg=60.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=2.0,
                    telegraph_time=0.3,
                    damage=20,
                    speed=420.0,
                    count=7,
                    spread_deg=45.0
                )
            ],
            reinforcements={
                "enemy_types": ["shooter", "scout"],
                "interval": 7.5,
                "max_active": 2
            }
        )
    ],
    reward_scrap=800,
    reward_score=4000,
    max_projectiles=26,
    max_reinforcements=3
)


# =============================================================================
# 4. SECTOR 4 BOSS: DEFENSE COMMANDER (Defense Grid Command Unit)
# =============================================================================
DEFENSE_COMMANDER_CONFIG = BossDefinition(
    id=BOSS_DEFENSE_COMMANDER,
    name="DEFENSE COMMANDER",
    sector_id=4,
    mission_id="S4_M5",
    role="Advanced Defense-Grid Command Unit",
    max_hp=1500,
    contact_damage=40.0,
    size=115,
    color_outer=(14, 165, 233),     # Electric Sky Blue
    color_inner=(239, 68, 68),      # Crimson Warning
    phases=[
        BossPhaseConfig(
            phase_index=1,
            hp_threshold=1.0,
            name="PHASE 1",
            movement_mode=MOVE_HOVER_TRACK,
            speed=65.0,
            armor=0.15,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_HOMING_VOLLEY,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    damage=26,
                    speed=330.0,
                    count=2
                ),
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=2.0,
                    telegraph_time=0.35,
                    damage=18,
                    speed=400.0,
                    count=5,
                    spread_deg=32.0
                )
            ],
            reinforcements={
                "enemy_types": ["shield_drone", "shooter"],
                "interval": 11.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=2,
            hp_threshold=0.70,
            name="PHASE 2 - SHIELD DEFENSE",
            movement_mode=MOVE_PATROL_HORIZONTAL,
            speed=80.0,
            armor=0.25,
            has_shield=True,
            shield_duration=4.0,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_TARGETED_SHOT,
                    cooldown=1.8,
                    telegraph_time=0.3,
                    damage=22,
                    speed=450.0,
                    count=3
                ),
                BossAttackConfig(
                    attack_type=ATTACK_MISSILE_SALVO,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    damage=35,
                    speed=320.0,
                    count=3
                )
            ],
            reinforcements={
                "enemy_types": ["shooter", "scout"],
                "interval": 8.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=3,
            hp_threshold=0.35,
            name="PHASE 3 - GRID OVERCLOCK",
            movement_mode=MOVE_AGGRESSIVE_SWEEP,
            speed=105.0,
            armor=0.20,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_LASER_SWEEP,
                    cooldown=3.4,
                    telegraph_time=0.5,
                    duration=0.7,
                    damage=30,
                    speed=460.0,
                    count=5,
                    spread_deg=35.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=2.8,
                    telegraph_time=0.4,
                    damage=18,
                    speed=360.0,
                    count=12
                )
            ],
            reinforcements={
                "enemy_types": ["heavy", "scout"],
                "interval": 9.0,
                "max_active": 2
            }
        )
    ],
    reward_scrap=1200,
    reward_score=6000,
    max_projectiles=28,
    max_reinforcements=3
)


# =============================================================================
# 5. SECTOR 5 BOSS: DRONE OVERLORD (FINAL BOSS - Supreme Commander)
# =============================================================================
DRONE_OVERLORD_CONFIG = BossDefinition(
    id=BOSS_DRONE_OVERLORD,
    name="DRONE OVERLORD",
    sector_id=5,
    mission_id="S5_M5",
    role="Supreme Enemy Commander",
    max_hp=2200,
    contact_damage=45.0,
    size=130,
    color_outer=(15, 23, 42),       # Dark Slate Onyx
    color_inner=(239, 68, 68),      # Menacing Neon Crimson
    phases=[
        BossPhaseConfig(
            phase_index=1,
            hp_threshold=1.0,
            name="PHASE 1 - COMMAND ONLINE",
            movement_mode=MOVE_HOVER_TRACK,
            speed=70.0,
            armor=0.15,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=2.2,
                    telegraph_time=0.4,
                    damage=22,
                    speed=400.0,
                    count=7,
                    spread_deg=40.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_TARGETED_SHOT,
                    cooldown=1.8,
                    telegraph_time=0.3,
                    damage=24,
                    speed=460.0,
                    count=3
                )
            ],
            reinforcements={
                "enemy_types": ["scout", "shooter"],
                "interval": 10.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=2,
            hp_threshold=0.75,
            name="PHASE 2 - FLEET COORDINATION",
            movement_mode=MOVE_FIGURE_EIGHT,
            speed=90.0,
            armor=0.20,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_HOMING_VOLLEY,
                    cooldown=3.5,
                    telegraph_time=0.5,
                    damage=32,
                    speed=350.0,
                    count=4
                ),
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=2.8,
                    telegraph_time=0.4,
                    damage=20,
                    speed=380.0,
                    count=12
                )
            ],
            reinforcements={
                "enemy_types": ["shield_drone", "heavy"],
                "interval": 10.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=3,
            hp_threshold=0.50,
            name="PHASE 3 - QUANTUM SHIELD",
            movement_mode=MOVE_PATROL_VERTICAL,
            speed=100.0,
            armor=0.30,
            has_shield=True,
            shield_duration=4.5,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_LASER_SWEEP,
                    cooldown=3.2,
                    telegraph_time=0.5,
                    duration=0.8,
                    damage=34,
                    speed=480.0,
                    count=6,
                    spread_deg=40.0
                ),
                BossAttackConfig(
                    attack_type=ATTACK_ENERGY_WAVE,
                    cooldown=2.6,
                    telegraph_time=0.4,
                    damage=26,
                    speed=400.0,
                    count=8,
                    spread_deg=60.0
                )
            ],
            reinforcements={
                "enemy_types": ["shooter", "scout"],
                "interval": 8.0,
                "max_active": 2
            }
        ),
        BossPhaseConfig(
            phase_index=4,
            hp_threshold=0.25,
            name="FINAL DESPERATION PHASE",
            movement_mode=MOVE_AGGRESSIVE_SWEEP,
            speed=125.0,
            armor=0.20,
            attacks=[
                BossAttackConfig(
                    attack_type=ATTACK_RADIAL_BURST,
                    cooldown=2.2,
                    telegraph_time=0.35,
                    damage=22,
                    speed=400.0,
                    count=16
                ),
                BossAttackConfig(
                    attack_type=ATTACK_MISSILE_SALVO,
                    cooldown=2.8,
                    telegraph_time=0.4,
                    damage=38,
                    speed=340.0,
                    count=4
                ),
                BossAttackConfig(
                    attack_type=ATTACK_SPREAD_BARRAGE,
                    cooldown=1.7,
                    telegraph_time=0.25,
                    damage=24,
                    speed=440.0,
                    count=9,
                    spread_deg=50.0
                )
            ],
            reinforcements={
                "enemy_types": ["scout", "shooter"],
                "interval": 6.0,
                "max_active": 3
            }
        )
    ],
    reward_scrap=2000,
    reward_score=10000,
    max_projectiles=32,
    max_reinforcements=3
)


# Master Boss Lookup Catalog
BOSS_REGISTRY: Dict[str, BossDefinition] = {
    BOSS_ASSEMBLY_WARDEN: ASSEMBLY_WARDEN_CONFIG,
    BOSS_CORE_EXECUTOR: CORE_EXECUTOR_CONFIG,
    BOSS_REACTOR_TITAN: REACTOR_TITAN_CONFIG,
    BOSS_DEFENSE_COMMANDER: DEFENSE_COMMANDER_CONFIG,
    BOSS_DRONE_OVERLORD: DRONE_OVERLORD_CONFIG,
}

# Mission to Boss Mapping
MISSION_BOSS_MAP: Dict[str, str] = {
    "S1_M5": BOSS_ASSEMBLY_WARDEN,
    "S2_M5": BOSS_CORE_EXECUTOR,
    "S3_M5": BOSS_REACTOR_TITAN,
    "S4_M5": BOSS_DEFENSE_COMMANDER,
    "S5_M5": BOSS_DRONE_OVERLORD,
}


def get_boss_definition(boss_id: str) -> Optional[BossDefinition]:
    """Retrieves BossDefinition by boss_id."""
    return BOSS_REGISTRY.get(boss_id)


def get_boss_for_mission(mission_id: str) -> Optional[BossDefinition]:
    """Retrieves BossDefinition for a mission if one is assigned."""
    boss_id = MISSION_BOSS_MAP.get(mission_id)
    if boss_id:
        return BOSS_REGISTRY.get(boss_id)
    return None
