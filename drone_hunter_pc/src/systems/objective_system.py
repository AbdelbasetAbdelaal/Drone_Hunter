"""
================================================================================
            DRONE HUNTER 2D - OBJECTIVE ASSAULT SYSTEM
================================================================================
Authoritative manager for Objective Assault missions:
- Spawns physical Ground Objectives in the destination zone
- Sets up multi-layer defense grids (Radar nodes, AA platforms, Shield generators)
- Manages radar detection telemetry, alert levels, and bounded reinforcement waves
- Orchestrates destruction VFX sequences and mission victory signaling
"""

import math
import random
import pygame
from typing import List, Optional, Tuple
import logging

from src.core.game_context import GameContext
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT, COLOR_GOLD, COLOR_CYAN, COLOR_CRIMSON
from src.data.objective_data import (
    OBJECTIVE_TYPE_RADAR_COMMAND, get_objective_catalog_def,
    get_defense_level_config, DEFENSE_LEVEL_1, DEFENSE_LEVEL_5,
    RADAR_STATE_ALERT, AA_TYPE_LIGHT, AA_TYPE_HEAVY, AA_TYPE_MISSILE,
    AIRCRAFT_INTERCEPTOR, AIRCRAFT_ATTACK, get_mission_objective_config
)
from src.entities.objective import (
    GroundObjective, RadarNode, AAPlatform, ShieldGenerator, CombatAircraft
)
from src.entities.enemy import Enemy, Scout, Shooter, Heavy


class ObjectiveSystem:
    """Central manager orchestrating Objective Assault missions and defense perimeters."""
    def __init__(self):
        self.active_objective: Optional[GroundObjective] = None
        self.radar_nodes: List[RadarNode] = []
        self.aa_platforms: List[AAPlatform] = []
        self.shield_generators: List[ShieldGenerator] = []
        self.combat_aircraft: List[CombatAircraft] = []
        self.active_reinforcements: List[Enemy] = []

        self.defense_level = 1
        self.is_active = False
        self.is_completed = False
        self.destruction_timer = 0.0
        self.reinforcement_timer = 0.0
        self._reinforcement_spawn_points: List[Tuple[float, float]] = []
        self._entry_zone_x: float = 0.0
        self._combat_zone_x: float = 0.0
        self._defense_zone_x: float = 0.0
        self._objective_zone_x: float = 0.0

    def reset(self):
        """Cleans up all active objective structures and state."""
        self.active_objective = None
        self.radar_nodes.clear()
        self.aa_platforms.clear()
        self.shield_generators.clear()
        self.combat_aircraft.clear()
        self.active_reinforcements.clear()
        self.defense_level = 1
        self.is_active = False
        self.is_completed = False
        self.destruction_timer = 0.0
        self.reinforcement_timer = 0.0
        self._reinforcement_spawn_points.clear()
        self._entry_zone_x = 0.0
        self._combat_zone_x = 0.0
        self._defense_zone_x = 0.0
        self._objective_zone_x = 0.0

    @property
    def is_radar_alert_active(self) -> bool:
        """True if any active radar node has detected the player."""
        return any(r.alive and r.state == RADAR_STATE_ALERT for r in self.radar_nodes)

    @property
    def active_radar_count(self) -> int:
        return sum(1 for r in self.radar_nodes if r.alive)

    @property
    def active_shield_generators_count(self) -> int:
        return sum(1 for g in self.shield_generators if g.alive)

    def start_objective_for_mission(self, mission_config: dict, ctx: GameContext) -> bool:
        """Initializes and spawns the physical objective and its defense perimeter for the mission."""
        self.reset()
        
        obj_type = mission_config.get("objective_type", OBJECTIVE_TYPE_RADAR_COMMAND)
        def_level = mission_config.get("defense_level", 1)
        mission_id = mission_config.get("id", "")
        self.defense_level = def_level
        def_cfg = get_defense_level_config(def_level)

        # 1. Load mission-specific objective config (position, reinforcement spawn points)
        mission_obj_cfg = get_mission_objective_config(mission_id)
        obj_pos = mission_obj_cfg.get("objective_position")
        if obj_pos is None:
            obj_pos = (WORLD_WIDTH - 280.0, WORLD_HEIGHT // 2 + random.uniform(-100.0, 100.0))
        self._reinforcement_spawn_points = mission_obj_cfg.get("reinforcement_spawn_points", [(WORLD_WIDTH - 80.0, WORLD_HEIGHT // 2)])

        # Zone definitions for reinforcement intensity scaling
        # entry_zone: far left, player entering sector (lighter defenses)
        # combat_zone: mid-field, player approaching objective (normal)
        # defense_zone: near objective, outer perimeter (heavy)
        # objective_zone: at objective itself (max)
        ox, oy = obj_pos
        self._entry_zone_x    = WORLD_WIDTH * 0.15
        self._combat_zone_x   = WORLD_WIDTH * 0.45
        self._defense_zone_x  = ox - 300.0
        self._objective_zone_x = ox - 120.0

        logging.debug(
            f"ObjectiveSystem: Zones for '{mission_id}' - "
            f"entry={self._entry_zone_x:.0f} combat={self._combat_zone_x:.0f} "
            f"defense={self._defense_zone_x:.0f} objective={self._objective_zone_x:.0f}"
        )

        # 2. Spawn Ground Objective at end of route
        objective = GroundObjective(
            objective_type=obj_type,
            pos=obj_pos,
            defense_level=def_level,
            hp_mult=def_cfg["hp_mult"] * getattr(ctx, "ng_plus_enemy_hp_mult", 1.0)
        )
        self.active_objective = objective
        ctx.target_group.add(objective)

        # 2. Spawn Shield Generators (if specified)
        num_gens = def_cfg.get("shield_generators", 0)
        for i in range(num_gens):
            angle = (2 * math.pi / max(1, num_gens)) * i
            dist = 140.0
            gx = obj_pos[0] + math.cos(angle) * dist
            gy = obj_pos[1] + math.sin(angle) * dist
            gen = ShieldGenerator(pos=(gx, gy), parent_objective=objective)
            objective.register_shield_generator(gen)
            self.shield_generators.append(gen)
            ctx.target_group.add(gen)

        # 3. Spawn Radar Nodes
        num_radars = def_cfg.get("radar_nodes", 0)
        for i in range(num_radars):
            offset_y = (i - (num_radars - 1) / 2.0) * 220.0
            rx = obj_pos[0] - 340.0 - (i * 60.0)
            ry = max(150.0, min(WORLD_HEIGHT - 150.0, obj_pos[1] + offset_y))
            radar = RadarNode(pos=(rx, ry))
            self.radar_nodes.append(radar)
            ctx.target_group.add(radar)

        # 4. Spawn AA Defense Platforms
        aa_types = def_cfg.get("aa_types", [AA_TYPE_LIGHT])
        for i, aa_type in enumerate(aa_types):
            offset_y = (i - (len(aa_types) - 1) / 2.0) * 160.0
            ax = obj_pos[0] - 200.0 - (i % 2) * 80.0
            ay = max(120.0, min(WORLD_HEIGHT - 120.0, obj_pos[1] + offset_y))
            aa = AAPlatform(pos=(ax, ay), aa_type=aa_type)
            self.aa_platforms.append(aa)
            ctx.target_group.add(aa)

        # 5. Spawn Combat Aircraft
        num_aircraft = def_cfg.get("aircraft_count", 0)
        for i in range(num_aircraft):
            ac_type = AIRCRAFT_INTERCEPTOR if i % 2 == 0 else AIRCRAFT_ATTACK
            ax = obj_pos[0] - 400.0 - (i * 90.0)
            ay = obj_pos[1] + random.uniform(-200.0, 200.0)
            aircraft = CombatAircraft(pos=(ax, ay), aircraft_type=ac_type)
            self.combat_aircraft.append(aircraft)
            ctx.target_group.add(aircraft)

        self.is_active = True
        self.is_completed = False
        self.reinforcement_timer = def_cfg.get("reinforcement_interval", 10.0)
        
        logging.debug(f"ObjectiveSystem: Initialized {objective.name} with Defense Level {def_level}")
        return True

    def update(self, dt: float, ctx: GameContext) -> bool:
        """Updates objective, defensive radar, AA turrets, aircraft, and returns True on mission victory."""
        if not self.is_active:
            return False

        p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

        # 1. Update Radar Nodes
        for r in list(self.radar_nodes):
            if r.alive:
                r.update(dt, player_pos=p_pos, ctx=ctx)

        # 2. Update AA Platforms & Collect hostile bullets
        for aa in list(self.aa_platforms):
            if aa.alive:
                new_bullets = aa.update(dt, player_pos=p_pos, ctx=ctx)
                for b in new_bullets:
                    ctx.enemy_bullet_group.add(b)

        # 3. Clean and manage Bounded Reinforcements
        self.active_reinforcements = [e for e in self.active_reinforcements if getattr(e, "alive", False)]
        def_cfg = get_defense_level_config(self.defense_level)
        max_reinf = def_cfg.get("reinforcement_max", 3)

        if self.is_radar_alert_active and len(self.active_reinforcements) < max_reinf:
            self.reinforcement_timer -= dt
            if self.reinforcement_timer <= 0:
                self.reinforcement_timer = def_cfg.get("reinforcement_interval", 9.0)

                # Zone-based reinforcement intensity: closer to objective = heavier units
                px = p_pos[0] if p_pos else (WORLD_WIDTH // 2)
                if px >= self._objective_zone_x:
                    zone_reinf_types = [Shooter, Heavy, CombatAircraft]
                elif px >= self._defense_zone_x:
                    zone_reinf_types = [Shooter, Heavy] if self.defense_level >= 3 else [Scout, Shooter]
                elif px >= self._combat_zone_x:
                    zone_reinf_types = [Scout, Shooter]
                else:
                    zone_reinf_types = [Scout]

                reinf_type = random.choice(zone_reinf_types)

                # Use mission-defined reinforcement spawn point if available
                spawn_pt = random.choice(self._reinforcement_spawn_points) if self._reinforcement_spawn_points else (WORLD_WIDTH - 80.0, random.uniform(200.0, WORLD_HEIGHT - 200.0))
                rx, ry = spawn_pt
                # Add small random offset so waves don't all stack at identical position
                rx += random.uniform(-30.0, 30.0)
                ry += random.uniform(-40.0, 40.0)
                reinf = reinf_type(pos=(rx, ry))
                self.active_reinforcements.append(reinf)
                ctx.target_group.add(reinf)

        # 4. Check Objective Status
        if self.active_objective and not self.active_objective.alive:
            if not self.is_completed:
                self.is_completed = True
                self.destruction_timer = 2.0
                
                # Big celebratory destruction sequence
                if ctx.particle_manager:
                    ctx.particle_manager.spawn_boss_explosion(self.active_objective.rect.center)
                    ctx.particle_manager.spawn_floating_text(
                        self.active_objective.rect.center,
                        f"OBJECTIVE DESTROYED! +{self.active_objective.score_value}",
                        COLOR_GOLD, 26
                    )
                ctx.trigger_shake(15.0, 0.6)
                if ctx.audio_manager:
                    ctx.audio_manager.play_boss_death()

                # Payout Score & Scrap
                ctx.add_score(self.active_objective.score_value)
                ctx.scrap += self.active_objective.scrap_reward

        if self.is_completed:
            self.destruction_timer -= dt
            if self.destruction_timer <= 0:
                return True

        return False
