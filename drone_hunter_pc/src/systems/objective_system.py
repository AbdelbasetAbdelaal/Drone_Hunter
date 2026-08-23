"""
================================================================================
             DRONE HUNTER 2D - OBJECTIVE ASSAULT SYSTEM
================================================================================
Authoritative manager for Objective Assault missions:
- Spawns physical Ground Objectives in the destination zone
- Sets up multi-layer defense grids (Radar nodes, AA platforms, Shield generators)
- Manages radar detection telemetry, alert levels, and bounded reinforcement waves
- Orchestrates destruction VFX sequences and mission victory signaling
- Exposes runtime phases for HUD feedback
"""

import math
import random
import pygame
from typing import List, Optional, Tuple
import logging

from src.core.game_context import GameContext
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT, COLOR_GOLD, COLOR_CYAN, COLOR_CRIMSON, COLOR_EMERALD
from src.data.objective_data import (
    OBJECTIVE_TYPE_RADAR_COMMAND, get_objective_catalog_def,
    get_defense_level_config, DEFENSE_LEVEL_1, DEFENSE_LEVEL_5,
    RADAR_STATE_ALERT, AA_TYPE_LIGHT, AA_TYPE_HEAVY, AA_TYPE_MISSILE,
    AIRCRAFT_INTERCEPTOR, AIRCRAFT_ATTACK, get_mission_objective_config,
    PHASE_APPROACH, PHASE_DETECTED, PHASE_DEFENSE, PHASE_OBJECTIVE_ASSAULT,
    PHASE_OBJECTIVE_CRITICAL, PHASE_OBJECTIVE_DESTROYED,
    LAYER_OUTER, LAYER_MIDDLE, LAYER_INNER,
    get_phase_display_name, get_layer_position, get_defense_layer_positions
)
from src.entities.objective import (
    GroundObjective, RadarNode, AAPlatform, ShieldGenerator, CombatAircraft
)
from src.entities.enemy import Enemy, Scout, Shooter, Heavy


# Phase constant aliases for backward-compatible references
PHASE_CONSTANTS = [
    PHASE_APPROACH, PHASE_DETECTED, PHASE_DEFENSE,
    PHASE_OBJECTIVE_ASSAULT, PHASE_OBJECTIVE_CRITICAL, PHASE_OBJECTIVE_DESTROYED,
]


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
        self._radar_positions: List[Tuple[float, float]] = []
        self._aa_positions: List[Tuple[float, float]] = []
        self._aircraft_spawn_points: List[Tuple[float, float]] = []
        self._defense_layer_config: dict = {}
        self._entry_zone_x: float = 0.0
        self._combat_zone_x: float = 0.0
        self._defense_zone_x: float = 0.0
        self._objective_zone_x: float = 0.0

        # Phase tracking
        self._current_phase: str = PHASE_APPROACH

        # Deterministic encounter control
        self._rng: random.Random = random.Random()
        self._use_seed: bool = False

        # Radar strategic choice: destroying radars reduces reinforcement pressure
        self._radar_pressure_reduction: float = 0.0
        self._radars_destroyed_count: int = 0

        # Combat windows: brief periods of reduced fire after major attacks
        self._combat_window_timer: float = 0.0
        self._combat_window_active: bool = False

        # Objective position cache for phase/HUD calculations
        self._last_player_zone_x: float = 0.0
        self._was_radar_alert: bool = False
        self._last_alive_radar_count: int = 0
        self._objective_pos: Tuple[float, float] = (WORLD_WIDTH - 280.0, WORLD_HEIGHT // 2)

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
        self._radar_positions.clear()
        self._aa_positions.clear()
        self._aircraft_spawn_points.clear()
        self._defense_layer_config = {}
        self._entry_zone_x = 0.0
        self._combat_zone_x = 0.0
        self._defense_zone_x = 0.0
        self._objective_zone_x = 0.0
        self._current_phase = PHASE_APPROACH
        self._rng = random.Random()
        self._use_seed = False
        self._radar_pressure_reduction = 0.0
        self._radars_destroyed_count = 0
        self._combat_window_timer = 0.0
        self._combat_window_active = False
        self._last_player_zone_x = 0.0
        self._was_radar_alert = False
        self._last_alive_radar_count = 0
        self._objective_pos = (WORLD_WIDTH - 280.0, WORLD_HEIGHT // 2)

    @property
    def is_radar_alert_active(self) -> bool:
        """True if any active radar node has detected the player."""
        return any(r.alive and r.state == RADAR_STATE_ALERT for r in self.radar_nodes)

    @property
    def active_radar_count(self) -> int:
        return sum(1 for r in self.radar_nodes if r.alive)

    @property
    def total_radar_count(self) -> int:
        return len(self.radar_nodes)

    @property
    def active_shield_generators_count(self) -> int:
        return sum(1 for g in self.shield_generators if g.alive)

    @property
    def total_shield_generators_count(self) -> int:
        return len(self.shield_generators)

    @property
    def shield_state(self) -> str:
        """Returns 'SHIELDED' or 'EXPOSED' based on shield generator status."""
        return "SHIELDED" if self.active_shield_generators_count > 0 else "EXPOSED"

    @property
    def is_shielded(self) -> bool:
        return self.active_shield_generators_count > 0

    @property
    def current_phase(self) -> str:
        """Returns the current runtime phase of the objective assault."""
        return self._current_phase

    @property
    def phase_display_name(self) -> str:
        """Returns human-readable phase name for HUD display."""
        return get_phase_display_name(self._current_phase)

    @property
    def reinforcement_pressure(self) -> float:
        """Returns current reinforcement pressure multiplier (1.0 = normal, <1.0 = reduced)."""
        return 1.0 - self._radar_pressure_reduction

    @property
    def is_combat_window_active(self) -> bool:
        """True during brief combat windows of reduced fire after major attacks."""
        return self._combat_window_active

    def _update_phase(self, dt: float, player_pos: Tuple[float, float]):
        """Computes the current tactical phase based on player position and objective health."""
        if not self.active_objective:
            self._current_phase = PHASE_APPROACH
            return

        obj = self.active_objective
        px = player_pos[0] if player_pos else 0.0

        # Check for objective destruction first (highest priority)
        if not obj.alive:
            self._current_phase = PHASE_OBJECTIVE_DESTROYED
            return

        # Check critical health
        if obj.hp_percent <= 0.25:
            self._current_phase = PHASE_OBJECTIVE_CRITICAL
            return

        # Check if player is detected by radar (alert active)
        radar_detected = self.is_radar_alert_active

        # Check player proximity to objective zones
        if px >= self._objective_zone_x:
            if radar_detected or obj.hp_percent < 0.65:
                self._current_phase = PHASE_OBJECTIVE_ASSAULT
            elif self._was_radar_alert:
                self._current_phase = PHASE_DEFENSE
            else:
                self._current_phase = PHASE_OBJECTIVE_ASSAULT
        elif px >= self._defense_zone_x:
            if not radar_detected and not self._was_radar_alert:
                self._current_phase = PHASE_APPROACH
            elif radar_detected:
                self._current_phase = PHASE_DETECTED
            else:
                self._current_phase = PHASE_DEFENSE
        else:
            if radar_detected:
                self._current_phase = PHASE_DETECTED
            else:
                self._current_phase = PHASE_APPROACH

        self._was_radar_alert = radar_detected
        self._last_player_zone_x = px

    def start_objective_for_mission(self, mission_config: dict, ctx: GameContext, seed: Optional[int] = None) -> bool:
        """Initializes and spawns the physical objective and its defense perimeter for the mission.

        Accepts an optional ``seed`` parameter for deterministic reinforcement type
        selection and position jitter, enabling reproducible encounters.
        """
        self.reset()

        # Deterministic PRNG for reproducible encounters
        if seed is not None:
            self._rng = random.Random(seed)
            self._use_seed = True
        else:
            self._rng = random
            self._use_seed = False

        obj_type = mission_config.get("objective_type", OBJECTIVE_TYPE_RADAR_COMMAND)
        def_level = mission_config.get("defense_level", 1)
        mission_id = mission_config.get("id", "")
        self.defense_level = def_level
        def_cfg = get_defense_level_config(def_level)

        # 1. Load mission-specific objective config (position, reinforcement spawn points,
        #    defense geometry)
        mission_obj_cfg = get_mission_objective_config(mission_id)
        obj_pos = mission_obj_cfg.get("objective_position")
        if obj_pos is None:
            obj_pos = (WORLD_WIDTH - 280.0, WORLD_HEIGHT // 2 + self._rng.uniform(-100.0, 100.0))
        self._reinforcement_spawn_points = mission_obj_cfg.get("reinforcement_spawn_points", [(WORLD_WIDTH - 80.0, WORLD_HEIGHT // 2)])
        self._radar_positions = mission_obj_cfg.get("radar_positions", [])
        self._aa_positions = mission_obj_cfg.get("aa_positions", [])
        self._aircraft_spawn_points = mission_obj_cfg.get("aircraft_spawn_points", [])
        self._defense_layer_config = mission_obj_cfg.get("defense_layer_config", {})
        self._objective_pos = obj_pos

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

        # 3. Spawn Shield Generators (INNER layer — closest to objective)
        num_gens = def_cfg.get("shield_generators", 0)
        layer_positions = get_defense_layer_positions(obj_pos, self._defense_layer_config)
        inner_pos = layer_positions.get(LAYER_INNER)
        for i in range(num_gens):
            if inner_pos and num_gens > 1:
                angle = (2 * math.pi / num_gens) * i
                dist = 60.0
                gx = inner_pos[0] + math.cos(angle) * dist
                gy = inner_pos[1] + math.sin(angle) * dist
            else:
                angle = (2 * math.pi / max(1, num_gens)) * i
                dist = 140.0
                gx = obj_pos[0] + math.cos(angle) * dist
                gy = obj_pos[1] + math.sin(angle) * dist
            gen = ShieldGenerator(pos=(gx, gy), parent_objective=objective, defense_layer=LAYER_INNER)
            objective.register_shield_generator(gen)
            self.shield_generators.append(gen)
            ctx.target_group.add(gen)

        # 4. Spawn Radar Nodes — use mission-specific positions if available, else layer-based
        num_radars = def_cfg.get("radar_nodes", 0)
        radar_positions = self._radar_positions if len(self._radar_positions) >= num_radars else []
        middle_pos = layer_positions.get(LAYER_MIDDLE)
        for i in range(num_radars):
            if i < len(radar_positions):
                rx, ry = radar_positions[i]
            elif middle_pos:
                rx, ry = get_layer_position(obj_pos, LAYER_MIDDLE, jitter=40.0)
                ry += (i - (num_radars - 1) / 2.0) * 100.0
            else:
                offset_y = (i - (num_radars - 1) / 2.0) * 220.0
                rx = obj_pos[0] - 340.0 - (i * 60.0)
                ry = max(150.0, min(WORLD_HEIGHT - 150.0, obj_pos[1] + offset_y))
            radar = RadarNode(pos=(rx, ry), defense_layer=LAYER_MIDDLE)
            self.radar_nodes.append(radar)
            ctx.target_group.add(radar)

        # 5. Spawn AA Defense Platforms — use mission-specific positions if available, else layer-based
        aa_types = def_cfg.get("aa_types", [AA_TYPE_LIGHT])
        aa_positions = self._aa_positions if len(self._aa_positions) >= len(aa_types) else []
        inner_pos_aa = layer_positions.get(LAYER_INNER)
        for i, aa_type in enumerate(aa_types):
            if i < len(aa_positions):
                ax, ay = aa_positions[i]
            elif inner_pos_aa:
                ax, ay = get_layer_position(obj_pos, LAYER_INNER, jitter=30.0)
                ay += (i - (len(aa_types) - 1) / 2.0) * 80.0
            else:
                offset_y = (i - (len(aa_types) - 1) / 2.0) * 160.0
                ax = obj_pos[0] - 200.0 - (i % 2) * 80.0
                ay = max(120.0, min(WORLD_HEIGHT - 120.0, obj_pos[1] + offset_y))
            aa = AAPlatform(pos=(ax, ay), aa_type=aa_type, defense_layer=LAYER_INNER)
            self.aa_platforms.append(aa)
            ctx.target_group.add(aa)

        # 6. Spawn Combat Aircraft — use mission-specific positions if available, else layer-based
        num_aircraft = def_cfg.get("aircraft_count", 0)
        ac_positions = self._aircraft_spawn_points if len(self._aircraft_spawn_points) >= num_aircraft else []
        outer_pos = layer_positions.get(LAYER_OUTER)
        for i in range(num_aircraft):
            ac_type = AIRCRAFT_INTERCEPTOR if i % 2 == 0 else AIRCRAFT_ATTACK
            if i < len(ac_positions):
                ax, ay = ac_positions[i]
            elif outer_pos:
                ax, ay = get_layer_position(obj_pos, LAYER_OUTER, jitter=50.0)
                ay += self._rng.uniform(-120.0, 120.0)
            else:
                ax = obj_pos[0] - 400.0 - (i * 90.0)
                ay = obj_pos[1] + self._rng.uniform(-200.0, 200.0)
            aircraft = CombatAircraft(pos=(ax, ay), aircraft_type=ac_type, defense_layer=LAYER_OUTER)
            self.combat_aircraft.append(aircraft)
            ctx.target_group.add(aircraft)

        self.is_active = True
        self.is_completed = False
        self.reinforcement_timer = def_cfg.get("reinforcement_interval", 10.0)
        self._current_phase = PHASE_APPROACH
        self._radar_pressure_reduction = 0.0
        self._radars_destroyed_count = 0
        self._combat_window_timer = 0.0
        self._combat_window_active = False
        self._was_radar_alert = False
        self._last_alive_radar_count = self.active_radar_count

        logging.debug(f"ObjectiveSystem: Initialized {objective.name} with Defense Level {def_level}")
        return True

    def stop_for_player_death(self, ctx: GameContext):
        """Stops objective assault progression when the player dies.

        Prevents the world from continuing indefinitely — sets is_active to False
        so no further reinforcements, aircraft, or AA fire occurs.
        """
        self.is_active = False
        self._current_phase = PHASE_APPROACH

    def _update_reinforcement_interval(self, def_cfg: dict) -> float:
        """Returns the current reinforcement interval, reduced when radars are destroyed."""
        base_interval = def_cfg.get("reinforcement_interval", 9.0)
        # Each destroyed radar reduces pressure (longer intervals)
        pressure_mult = 1.0 - self._radar_pressure_reduction
        return base_interval / max(0.25, pressure_mult)

    def update(self, dt: float, ctx: GameContext) -> bool:
        """Updates objective, defensive radar, AA turrets, aircraft, and returns True on mission victory."""
        if not self.is_active:
            return False

        p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

        # 0. Update Combat Windows (brief periods of reduced fire after major attacks)
        if self._combat_window_active:
            self._combat_window_timer -= dt
            if self._combat_window_timer <= 0:
                self._combat_window_active = False

        # 1. Update Objective Phase
        self._update_phase(dt, p_pos)

        # Check if objective was recently hit → trigger combat window for tactical breather
        if self.active_objective and getattr(self.active_objective, "hit_effect_timer", 0.0) > 0:
            self.trigger_combat_window(2.5)

        # 2. Update Radar Nodes
        for r in list(self.radar_nodes):
            if r.alive:
                r.update(dt, player_pos=p_pos, ctx=ctx)

        # 2b. Radar strategic choice: detect destroyed radars and reduce pressure
        self._check_radar_destruction(ctx)

        # Freeze combat briefly during destruction sequence (pause AA, aircraft, reinforcements)
        combat_frozen = self.is_completed

        # 3. Update AA Platforms & Collect hostile bullets (skip during combat window or freeze)
        for aa in list(self.aa_platforms):
            if aa.alive:
                new_bullets = aa.update(dt, player_pos=p_pos, ctx=ctx)
                if combat_frozen or self._combat_window_active:
                    new_bullets.clear()
                for b in new_bullets:
                    ctx.enemy_bullet_group.add(b)

        # 4. Update Combat Aircraft (skip during combat window or freeze)
        for ac in list(self.combat_aircraft):
            if ac.alive:
                new_bullets = ac.update(dt, player_pos=p_pos,
                                         target_group=getattr(ctx, "target_group", None))
                if combat_frozen or self._combat_window_active:
                    new_bullets.clear()
                for b in new_bullets:
                    ctx.enemy_bullet_group.add(b)

        # 5. Clean and manage Bounded Reinforcements (skip when frozen)
        self.active_reinforcements = [e for e in self.active_reinforcements if getattr(e, "alive", False)]
        if not combat_frozen:
            def_cfg = get_defense_level_config(self.defense_level)
            max_reinf = def_cfg.get("reinforcement_max", 3)

            # Reinforcement pressure is reduced when radars are destroyed
            pressure_active = self.is_radar_alert_active and (self.reinforcement_pressure > 0.1)

            if pressure_active and len(self.active_reinforcements) < max_reinf:
                self.reinforcement_timer -= dt
                if self.reinforcement_timer <= 0:
                    cur_interval = self._update_reinforcement_interval(def_cfg)
                    self.reinforcement_timer = cur_interval

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

                    # Deterministic selection using RNG if seeded
                    reinf_type = self._rng.choice(zone_reinf_types)

                    # Use mission-defined reinforcement spawn point if available
                    spawn_pt = self._rng.choice(self._reinforcement_spawn_points) if self._reinforcement_spawn_points else (WORLD_WIDTH - 80.0, self._rng.uniform(200.0, WORLD_HEIGHT - 200.0))
                    rx, ry = spawn_pt
                    # Add small deterministic random offset so waves don't all stack at identical position
                    rx += self._rng.uniform(-30.0, 30.0)
                    ry += self._rng.uniform(-40.0, 40.0)
                    reinf = reinf_type(pos=(rx, ry))
                    self.active_reinforcements.append(reinf)
                    ctx.target_group.add(reinf)

        # 6. Check Objective Status
        if self.active_objective and not self.active_objective.alive:
            if not self.is_completed:
                self.is_completed = True
                self.destruction_timer = 2.0
                self._current_phase = PHASE_OBJECTIVE_DESTROYED

                # Objective-specific destruction sequence (NOT boss terminology)
                if ctx.particle_manager:
                    ctx.particle_manager.spawn_objective_destruction(self.active_objective.rect.center)
                    ctx.particle_manager.spawn_floating_text(
                        self.active_objective.rect.center,
                        f"OBJECTIVE DESTROYED! +{self.active_objective.score_value}",
                        COLOR_GOLD, 26
                    )
                ctx.trigger_shake(15.0, 0.6)
                if ctx.audio_manager:
                    ctx.audio_manager.play_objective_destruction()

                # Payout Score & Scrap
                ctx.add_score(self.active_objective.score_value)
                ctx.scrap += self.active_objective.scrap_reward

        if self.is_completed:
            self.destruction_timer -= dt
            if self.destruction_timer <= 0:
                return True

        return False

    def _check_radar_destruction(self, ctx: GameContext):
        """Detects newly destroyed radar nodes and applies strategic pressure reduction.

        When the player destroys radar nodes:
        - alert pressure decreases (reduce reinforcement frequency)
        - player receives short tactical feedback (floating text)
        """
        current_alive = self.active_radar_count
        if hasattr(self, "_last_alive_radar_count"):
            newly_destroyed = self._last_alive_radar_count - current_alive
        else:
            newly_destroyed = 0
        if newly_destroyed > 0:
            self._radars_destroyed_count += newly_destroyed
            # Each destroyed radar reduces pressure by 15%, capped at 60% reduction
            self._radar_pressure_reduction = min(0.6, self._radar_pressure_reduction + 0.15 * newly_destroyed)

            # Reset reinforcement timer to longer interval
            def_cfg = get_defense_level_config(self.defense_level)
            self.reinforcement_timer = self._update_reinforcement_interval(def_cfg)

            # Tactical feedback to player
            if ctx.particle_manager:
                ctx.particle_manager.spawn_floating_text(
                    ctx.player.rect.center if ctx.player else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2),
                    "RADAR DESTROYED - PRESSURE REDUCED",
                    COLOR_EMERALD, 18
                )
            if ctx.audio_manager:
                ctx.audio_manager.play_ui_click()
        self._last_alive_radar_count = current_alive

    def trigger_combat_window(self, duration: float = 3.0):
        """Activates a brief combat window of reduced fire pressure after major attacks.

        This gives players a tactical breather to make decisions after dealing
        significant damage to the objective.
        """
        if duration > self._combat_window_timer:
            self._combat_window_timer = duration
            self._combat_window_active = True
