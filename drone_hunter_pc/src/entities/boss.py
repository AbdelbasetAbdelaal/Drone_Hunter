"""
================================================================================
                    DRONE HUNTER 2D - SECTOR BOSS ENTITIES
================================================================================
Phase 6: Multi-phase Boss entities with data-driven attack patterns, movement,
telegraphed combat cues, shield barriers, and modular weapon systems.
Compatible with CombatSystem, EncounterSystem, and renderer.
"""

import math
import random
import pygame
from typing import List, Optional, Tuple

from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE, COLOR_SHIELD,
    COLOR_NEON_RED
)
from src.data.game_data import TARGET_TYPE_BOSS
from src.data.boss_data import (
    BossDefinition, BossPhaseConfig, BossAttackConfig,
    ATTACK_RADIAL_BURST, ATTACK_SPREAD_BARRAGE, ATTACK_TARGETED_SHOT,
    ATTACK_HOMING_VOLLEY, ATTACK_LASER_SWEEP, ATTACK_ENERGY_WAVE,
    ATTACK_MISSILE_SALVO,
    MOVE_PATROL_HORIZONTAL, MOVE_PATROL_VERTICAL, MOVE_FIGURE_EIGHT,
    MOVE_HOVER_TRACK, MOVE_AGGRESSIVE_SWEEP,
    BOSS_ASSEMBLY_WARDEN, BOSS_CORE_EXECUTOR, BOSS_REACTOR_TITAN,
    BOSS_DEFENSE_COMMANDER, BOSS_DRONE_OVERLORD
)
from src.entities.bullet import EnemyBullet


class SectorBoss(pygame.sprite.Sprite):
    """
    Modular, data-driven Major Sector Boss entity.
    Drives multi-phase combat, deterministic phase transitions,
    telegraphed attacks, movement, and defensive barriers.
    """
    def __init__(self, definition: BossDefinition, pos: Optional[Tuple[float, float]] = None):
        super().__init__()
        self.definition = definition
        self.boss_id = definition.id
        self.boss_name = definition.name
        self.enemy_type = TARGET_TYPE_BOSS
        self.is_boss = True

        # Health & Stats
        self.max_hp = definition.max_hp
        self.hp = self.max_hp
        self.armor = 0.0
        self.contact_damage = definition.contact_damage
        self.contact_cooldown_timer = 0.0
        self.size = definition.size
        self.radius = self.size // 2
        self.score_value = definition.reward_score
        self.points = definition.reward_score
        self.alive = True
        self.hit_flash_timer = 0.0

        # Colors
        self.color_outer = definition.color_outer
        self.color_inner = definition.color_inner

        # Position & Movement
        if pos is None:
            self.pos = pygame.Vector2(WORLD_WIDTH - 250.0, WORLD_HEIGHT // 2)
        else:
            self.pos = pygame.Vector2(pos)

        self.spawn_anchor = pygame.Vector2(self.pos)
        self.base_y = self.pos.y
        self.time_accum = 0.0
        self.movement_speed = 70.0
        self.heading_angle = 180.0

        # Phase State Machine
        self.phases = definition.phases
        self.current_phase_idx = 0
        self.current_phase: BossPhaseConfig = self.phases[0]
        self.phase_transitioning = False
        self.phase_transition_timer = 0.0
        self.phase_transition_duration = 1.0

        # Attack State Tracking
        # attack_cooldowns: dict mapping attack_index -> float timer
        self.attack_cooldowns: dict[int, float] = {}
        self.attack_telegraph_timers: dict[int, float] = {}
        self.active_attacks: set[int] = set()
        self.active_projectiles: List[EnemyBullet] = []

        # Telegraph visual state
        self.telegraph_active = False
        self.telegraph_type = ""
        self.telegraph_timer = 0.0

        # Shield & Barriers
        self.is_shielded = False
        self.shield_timer = 0.0
        self.shield_angle = 0.0

        # Reinforcement spawn timer
        self.reinforcement_timer = 0.0

        # Sprite image & cache
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self._sprite_dirty = True
        self._cached_base_surf = None
        self._last_phase_rendered = -1
        self._last_shield_state = False

        # Apply initial phase
        self._apply_phase(0)
        self._render_sprite()

    def _apply_phase(self, phase_idx: int):
        """Swaps active phase rules, speed, armor, shield, and resets attack cooldowns."""
        if phase_idx >= len(self.phases):
            return
        self.current_phase_idx = phase_idx
        self.current_phase = self.phases[phase_idx]
        self.movement_speed = self.current_phase.speed
        self.armor = self.current_phase.armor
        self.is_shielded = self.current_phase.has_shield
        self.shield_timer = max(0.0, self.current_phase.shield_duration)

        # Reset attack timers with positive staggered delays to prevent burst spam
        self.attack_cooldowns.clear()
        self.attack_telegraph_timers.clear()
        self.active_attacks.clear()
        self.telegraph_active = False
        for a_idx, atk in enumerate(self.current_phase.attacks):
            # Stagger initial cooldowns safely
            self.attack_cooldowns[a_idx] = max(0.4, atk.cooldown * (0.35 + 0.3 * a_idx))

        # Reset reinforcement timer
        if self.current_phase.reinforcements:
            self.reinforcement_timer = self.current_phase.reinforcements.get("interval", 8.0) * 0.5
        else:
            self.reinforcement_timer = 999.0

        self._sprite_dirty = True

    @property
    def current_phase_number(self) -> int:
        return self.current_phase_idx + 1

    @property
    def boss_phase(self) -> int:
        return self.current_phase_idx + 1

    @property
    def total_phases(self) -> int:
        return len(self.phases)

    @property
    def current_phase_name(self) -> str:
        return self.current_phase.name

    def take_damage(self, amount: int, source: str = "bullet", **kwargs) -> bool:
        """Applies armor and shield mitigation. Returns True if boss dies."""
        if not self.alive:
            return False

        if self.is_shielded:
            # Shield fully or mostly deflects damage (minimum chip damage)
            self.hit_flash_timer = 0.08
            return False

        effective_damage = amount
        if self.armor > 0.0:
            effective_damage = max(1, int(round(amount * (1.0 - self.armor))))

        self.hp -= effective_damage
        self.hit_flash_timer = 0.12

        # Check for phase transitions (deterministic evaluation)
        self._check_phase_transitions()

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.kill()
            return True
        return False

    def _check_phase_transitions(self):
        """Checks if HP threshold for next phase has been reached."""
        if not self.alive:
            return

        hp_pct = self.hp / max(1, self.max_hp)
        next_phase_idx = self.current_phase_idx + 1

        if next_phase_idx < len(self.phases):
            next_phase_cfg = self.phases[next_phase_idx]
            if hp_pct <= next_phase_cfg.hp_threshold:
                # Trigger phase transition!
                self.phase_transitioning = True
                self.phase_transition_timer = self.phase_transition_duration
                self._apply_phase(next_phase_idx)

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        """Updates boss AI, movement, attacks, telegraphs, and returns spawned bullets."""
        if not self.alive:
            return []

        # Check phase transitions on update as well (e.g. when hp modified directly)
        self._check_phase_transitions()

        # Clean tracked active projectiles (only retain alive ones)
        self.active_projectiles = [b for b in self.active_projectiles if getattr(b, "alive", False)]

        self.time_accum += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.contact_cooldown_timer > 0:
            self.contact_cooldown_timer -= dt

        # EMP shockwave mechanic for EMP Disrupter / EMP bosses
        if getattr(self, "is_emp_expanding", False) and player_obj:
            dist = math.hypot(player_obj.pos.x - self.pos.x, player_obj.pos.y - self.pos.y)
            if dist <= getattr(self, "emp_wave_radius", 0.0):
                player_obj.emp_jammed_timer = max(player_obj.emp_jammed_timer, 3.0)

        # Shield timer update (temporary phase shields)
        if self.is_shielded and self.current_phase.shield_duration > 0:
            self.shield_timer -= dt
            self.shield_angle += 3.0 * dt
            if self.shield_timer <= 0:
                self.is_shielded = False
                self.shield_timer = 0.0

        # Phase transition grace period timer
        if self.phase_transitioning:
            self.phase_transition_timer -= dt
            if self.phase_transition_timer <= 0:
                self.phase_transitioning = False

        # ---------------------------------------------------------------------
        # 1. BOSS MOVEMENT AI
        # ---------------------------------------------------------------------
        self._update_movement(dt, player_pos)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # ---------------------------------------------------------------------
        # 2. BOSS ATTACKS & BULLET GENERATION
        # ---------------------------------------------------------------------
        new_bullets: List[EnemyBullet] = []
        if not self.phase_transitioning:
            new_bullets = self._update_attacks(dt, player_pos, player_vel)

        # ---------------------------------------------------------------------
        # 3. SPRITE DIRTY CHECK & REBUILD
        # ---------------------------------------------------------------------
        if self._sprite_dirty or (self.current_phase_idx != self._last_phase_rendered) or (self.is_shielded != self._last_shield_state):
            self._render_sprite()
            self._last_phase_rendered = self.current_phase_idx
            self._last_shield_state = self.is_shielded
            self._sprite_dirty = False

        return new_bullets

    def _update_movement(self, dt: float, player_pos: tuple[float, float]):
        """Executes configurable boss movement mode clamped to arena boundaries."""
        mode = self.current_phase.movement_mode
        spd = self.movement_speed
        arena_min_x = WORLD_WIDTH // 2 - 100.0
        arena_max_x = WORLD_WIDTH - 150.0
        arena_min_y = 120.0
        arena_max_y = WORLD_HEIGHT - 120.0

        if mode == MOVE_PATROL_VERTICAL:
            # Smooth up/down oscillation
            self.pos.y = (WORLD_HEIGHT // 2) + math.sin(self.time_accum * 1.5) * (WORLD_HEIGHT // 2 - 180.0)
            self.pos.x = self.spawn_anchor.x + math.cos(self.time_accum * 0.8) * 30.0

        elif mode == MOVE_PATROL_HORIZONTAL:
            # Left/right sweeps with vertical wave
            self.pos.x = (arena_min_x + arena_max_x) / 2.0 + math.sin(self.time_accum * 1.2) * 220.0
            self.pos.y = self.base_y + math.sin(self.time_accum * 2.0) * 80.0

        elif mode == MOVE_FIGURE_EIGHT:
            # Figure-eight orbital flight
            self.pos.x = self.spawn_anchor.x + math.cos(self.time_accum * 1.0) * 160.0
            self.pos.y = (WORLD_HEIGHT // 2) + math.sin(self.time_accum * 2.0) * 200.0

        elif mode == MOVE_HOVER_TRACK:
            # Standoff tracking of player vertical position
            target_y = max(arena_min_y, min(arena_max_y, player_pos[1]))
            dy = target_y - self.pos.y
            self.pos.y += math.copysign(min(abs(dy), spd * dt), dy)
            self.pos.x = self.spawn_anchor.x + math.sin(self.time_accum * 1.4) * 40.0

        elif mode == MOVE_AGGRESSIVE_SWEEP:
            # High speed sweeping pressure
            self.pos.y = (WORLD_HEIGHT // 2) + math.sin(self.time_accum * 2.2) * 260.0
            target_x = max(arena_min_x, min(arena_max_x, player_pos[0] + 400.0))
            dx = target_x - self.pos.x
            self.pos.x += math.copysign(min(abs(dx), spd * 1.2 * dt), dx)

        # Clamping to arena boundaries
        self.pos.x = max(arena_min_x, min(arena_max_x, self.pos.x))
        self.pos.y = max(arena_min_y, min(arena_max_y, self.pos.y))

    def _update_attacks(self, dt: float, player_pos: tuple[float, float], player_vel: tuple[float, float]) -> list[EnemyBullet]:
        """Ticking attack cooldowns, telegraphing, and executing attack patterns with active projectile caps."""
        spawned: List[EnemyBullet] = []
        cx, cy = self.rect.center
        pred_player = (
            player_pos[0] + player_vel[0] * 0.35,
            player_pos[1] + player_vel[1] * 0.35
        )

        max_cap = self.definition.max_projectiles
        available_capacity = max(0, max_cap - len(self.active_projectiles))

        for a_idx, atk in enumerate(self.current_phase.attacks):
            if a_idx not in self.attack_cooldowns:
                self.attack_cooldowns[a_idx] = atk.cooldown

            self.attack_cooldowns[a_idx] -= dt

            # Check if attack telegraph begins
            if self.attack_cooldowns[a_idx] <= atk.telegraph_time and a_idx not in self.active_attacks:
                self.telegraph_active = True
                self.telegraph_type = atk.attack_type
                self.telegraph_timer = atk.telegraph_time

            # Fire attack once when cooldown expires
            if self.attack_cooldowns[a_idx] <= 0:
                self.attack_cooldowns[a_idx] = atk.cooldown
                self.telegraph_active = False
                if available_capacity > 0:
                    fired_bullets = self._execute_attack_pattern(atk, (cx, cy), pred_player)
                    allowed = fired_bullets[:available_capacity]
                    self.active_projectiles.extend(allowed)
                    spawned.extend(allowed)
                    available_capacity -= len(allowed)

        return spawned

    def _execute_attack_pattern(self, atk: BossAttackConfig, origin: tuple[float, float], target: tuple[float, float]) -> list[EnemyBullet]:
        """Executes a specific reusable attack pattern."""
        ox, oy = origin
        bullets: List[EnemyBullet] = []
        atype = atk.attack_type

        if atype == ATTACK_SPREAD_BARRAGE:
            # SPREAD_BARRAGE: Fan of directional projectiles towards player
            count = atk.count
            spread = atk.spread_deg
            step = spread / max(1, count - 1) if count > 1 else 0.0
            start_off = -spread / 2.0 if count > 1 else 0.0
            for i in range(count):
                offset_deg = start_off + i * step
                bullets.append(EnemyBullet(
                    origin, target,
                    speed=atk.speed,
                    angle_offset_deg=offset_deg,
                    damage=atk.damage
                ))

        elif atype == ATTACK_RADIAL_BURST:
            # RADIAL_BURST: 360-degree projectile ring
            count = atk.count
            angle_step = 360.0 / max(1, count)
            base_rot = self.time_accum * 25.0
            for i in range(count):
                deg = i * angle_step + base_rot
                rad = math.radians(deg)
                tx = ox + math.cos(rad) * 400.0
                ty = oy + math.sin(rad) * 400.0
                bullets.append(EnemyBullet(
                    origin, (tx, ty),
                    speed=atk.speed,
                    damage=atk.damage
                ))

        elif atype == ATTACK_TARGETED_SHOT:
            # TARGETED_SHOT: Precise high-velocity aim at player position
            count = atk.count
            for i in range(count):
                bullets.append(EnemyBullet(
                    (ox, oy + (i - (count - 1) / 2.0) * 16.0),
                    target,
                    speed=atk.speed,
                    damage=atk.damage
                ))

        elif atype == ATTACK_HOMING_VOLLEY:
            # HOMING_VOLLEY: Staggered homing projectiles
            count = atk.count
            for i in range(count):
                bullets.append(EnemyBullet(
                    (ox, oy + (i - (count - 1) / 2.0) * 20.0),
                    target,
                    speed=atk.speed,
                    angle_offset_deg=random.uniform(-18.0, 18.0),
                    damage=atk.damage
                ))

        elif atype == ATTACK_ENERGY_WAVE:
            # ENERGY_WAVE: Wide arc expanding energy pulse
            count = atk.count
            spread = atk.spread_deg
            for i in range(count):
                pct = i / max(1, count - 1) if count > 1 else 0.5
                deg = -spread / 2.0 + pct * spread
                bullets.append(EnemyBullet(
                    origin, target,
                    speed=atk.speed + (math.sin(pct * math.pi) * 40.0),
                    angle_offset_deg=deg,
                    damage=atk.damage
                ))

        elif atype == ATTACK_LASER_SWEEP:
            # LASER_SWEEP: Fast cutting burst sweep
            count = atk.count
            spread = atk.spread_deg
            for i in range(count):
                deg = -spread / 2.0 + (i / max(1, count - 1)) * spread
                bullets.append(EnemyBullet(
                    origin, target,
                    speed=atk.speed + 60.0,
                    angle_offset_deg=deg,
                    damage=atk.damage
                ))

        elif atype == ATTACK_MISSILE_SALVO:
            # MISSILE_SALVO: Heavy ordnance barrage
            count = atk.count
            for i in range(count):
                bullets.append(EnemyBullet(
                    (ox, oy + (i - (count - 1) / 2.0) * 24.0),
                    target,
                    speed=atk.speed,
                    angle_offset_deg=random.uniform(-10.0, 10.0),
                    damage=atk.damage
                ))

        return bullets

    def should_spawn_reinforcements(self, dt: float, current_active_reinforcements: int) -> Optional[List[str]]:
        """Returns list of enemy types to spawn if reinforcement rules are met."""
        if not self.alive or self.phase_transitioning:
            return None

        reinf_cfg = self.current_phase.reinforcements
        if not reinf_cfg:
            return None

        max_active = min(reinf_cfg.get("max_active", 2), self.definition.max_reinforcements)
        if current_active_reinforcements >= max_active:
            return None

        self.reinforcement_timer -= dt
        if self.reinforcement_timer <= 0:
            self.reinforcement_timer = reinf_cfg.get("interval", 8.0)
            types_to_spawn = reinf_cfg.get("enemy_types", ["scout"])
            # Return bounded list
            available_slots = max_active - current_active_reinforcements
            return types_to_spawn[:available_slots]

        return None

    def _render_sprite(self):
        """Builds procedural sci-fi dreadnought visual for the boss."""
        s = self.size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        center = (s // 2, s // 2)
        half = s // 2

        # Draw Boss Specific Chassis
        if self.boss_id == BOSS_ASSEMBLY_WARDEN:
            # Heavy Delta-Warden Fortress
            pts = [
                (s - 6, half),
                (half - 10, 8),
                (8, 16),
                (18, half),
                (8, s - 16),
                (half - 10, s - 8)
            ]
            pygame.draw.polygon(surf, self.color_outer, pts)
            pygame.draw.polygon(surf, (71, 85, 105), pts, 3)
            # Core Reactor
            pygame.draw.circle(surf, self.color_inner, (half + 8, half), 14)
            pygame.draw.circle(surf, COLOR_WHITE, (half + 8, half), 6)
            # Side Gun Pods
            pygame.draw.rect(surf, (51, 65, 85), (half - 12, 14, 20, 8), border_radius=2)
            pygame.draw.rect(surf, (51, 65, 85), (half - 12, s - 22, 20, 8), border_radius=2)

        elif self.boss_id == BOSS_CORE_EXECUTOR:
            # Heavy Octagonal Core Platform
            oct_pts = [
                (s - 8, half),
                (s - 20, 10),
                (20, 10),
                (8, half),
                (20, s - 10),
                (s - 20, s - 10)
            ]
            pygame.draw.polygon(surf, self.color_outer, oct_pts)
            pygame.draw.polygon(surf, (148, 163, 184), oct_pts, 3)
            # Central Overclock Core
            core_col = (255, 255, 255) if not self.is_shielded else COLOR_CYAN
            pygame.draw.circle(surf, (30, 41, 59), (half, half), 20)
            pygame.draw.circle(surf, core_col, (half, half), 12)
            # Heavy Dual Forward Cannons
            pygame.draw.rect(surf, COLOR_WHITE, (s - 14, half - 10, 12, 6), border_radius=1)
            pygame.draw.rect(surf, COLOR_WHITE, (s - 14, half + 4, 12, 6), border_radius=1)

        elif self.boss_id == BOSS_REACTOR_TITAN:
            # Reactor Titan Plasma Machine
            hex_pts = [
                (s - 10, half),
                (s - 24, 12),
                (24, 12),
                (10, half),
                (24, s - 12),
                (s - 24, s - 12)
            ]
            pygame.draw.polygon(surf, self.color_outer, hex_pts)
            pygame.draw.polygon(surf, (192, 132, 252), hex_pts, 3)
            # Reactor Pulsing Core
            core_r = 16 if self.current_phase_idx < 2 else 20
            pygame.draw.circle(surf, self.color_inner, (half, half), core_r)
            pygame.draw.circle(surf, COLOR_WHITE, (half, half), 8)
            # Cooling Vents
            for y_off in [-20, 0, 20]:
                pygame.draw.line(surf, (51, 65, 85), (half - 15, half + y_off), (half - 5, half + y_off), 3)

        elif self.boss_id == BOSS_DEFENSE_COMMANDER:
            # Advanced Defense Grid Platform
            pts = [
                (s - 6, half),
                (half + 12, 14),
                (14, 20),
                (24, half),
                (14, s - 20),
                (half + 12, s - 14)
            ]
            pygame.draw.polygon(surf, self.color_outer, pts)
            pygame.draw.polygon(surf, (56, 189, 248), pts, 3)
            # Command Sensor Array
            pygame.draw.circle(surf, self.color_inner, (half + 6, half), 15)
            pygame.draw.circle(surf, COLOR_WHITE, (half + 6, half), 7)
            # Defense Grid Antennas
            pygame.draw.line(surf, (226, 232, 240), (half, 10), (half + 14, 2), 2)
            pygame.draw.line(surf, (226, 232, 240), (half, s - 10), (half + 14, s - 2), 2)

        else:  # DRONE OVERLORD (FINAL BOSS)
            # Supreme Heavy Command Dreadnought (130x130)
            pts = [
                (s - 4, half),
                (s - 26, 10),
                (half - 10, 10),
                (14, 26),
                (26, half),
                (14, s - 26),
                (half - 10, s - 10),
                (s - 26, s - 10)
            ]
            pygame.draw.polygon(surf, self.color_outer, pts)
            pygame.draw.polygon(surf, (239, 68, 68), pts, 4)
            # Overlord Menacing Core
            core_r = 18 if self.current_phase_idx < 3 else 24
            pygame.draw.circle(surf, self.color_inner, (half + 6, half), core_r)
            pygame.draw.circle(surf, COLOR_WHITE, (half + 6, half), 9)
            # Triple Forward Heavy Rail-Batteries
            pygame.draw.rect(surf, (239, 68, 68), (s - 16, half - 18, 14, 6), border_radius=1)
            pygame.draw.rect(surf, COLOR_WHITE, (s - 10, half - 3, 10, 6), border_radius=1)
            pygame.draw.rect(surf, (239, 68, 68), (s - 16, half + 12, 14, 6), border_radius=1)

        # Shield Bubble Aura if Shielded
        if self.is_shielded:
            pygame.draw.circle(surf, (56, 189, 248, 140), center, half - 2, 3)
            pygame.draw.circle(surf, (255, 255, 255, 100), center, half - 6, 1)

        # Hit Flash Overlay (Alpha-Safe Mask to preserve transparent background)
        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(surf)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            surf.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.image = surf
        self.rect = self.image.get_rect(center=self.rect.center)


# =============================================================================
# Legacy Compatibility Aliases (Phase 1-4)
# =============================================================================
from src.data.boss_data import (
    ASSEMBLY_WARDEN_CONFIG, CORE_EXECUTOR_CONFIG, REACTOR_TITAN_CONFIG,
    DEFENSE_COMMANDER_CONFIG, DRONE_OVERLORD_CONFIG
)

class Boss(SectorBoss):
    """Legacy Boss base class alias."""
    def __init__(self, boss_type: str = TARGET_TYPE_BOSS, level: int = 1, sector_idx: int = 0,
                 hp_multiplier: float = 1.0, speed_multiplier: float = 1.0, **kwargs):
        # Map to appropriate boss definition
        defs = [ASSEMBLY_WARDEN_CONFIG, CORE_EXECUTOR_CONFIG, REACTOR_TITAN_CONFIG, DEFENSE_COMMANDER_CONFIG, DRONE_OVERLORD_CONFIG]
        boss_def = defs[min(sector_idx, len(defs) - 1)]
        super().__init__(boss_def)


class SkyDreadnoughtBoss(Boss):
    def __init__(self, level: int = 1, sector_idx: int = 0, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0, **kwargs):
        super().__init__(sector_idx=0)


class StealthMirageBoss(Boss):
    def __init__(self, level: int = 1, sector_idx: int = 1, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0, **kwargs):
        super().__init__(sector_idx=1)


class EMPDisrupterBoss(Boss):
    def __init__(self, level: int = 1, sector_idx: int = 2, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0, **kwargs):
        super().__init__(sector_idx=2)


class ColossusTitanMechBoss(Boss):
    def __init__(self, level: int = 1, sector_idx: int = 4, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0, **kwargs):
        super().__init__(sector_idx=4)

