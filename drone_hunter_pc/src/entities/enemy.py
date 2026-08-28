"""
================================================================================
                    DRONE HUNTER 2D - 2D ENEMY TARGET SPRITES
================================================================================
Defines hostile drone archetypes with modular AI architecture:
- Scout: High-speed strafing and predictive telegraph diving melee interceptor
- Shooter: Positional pressure drone with range keeping, deliberate aim, and telegraph firing
- Heavy: Armored brawler drone with sustained forward space pressure
- Swarm, Chaser, Fast, Armored, Shield Drone, Sniper, Turret, Vehicle, Standard
"""

import math
import random
import pygame
from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_WHITE, COLOR_CRIMSON,
    COLOR_NEON_RED
)
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_STANDARD,
    TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE,
    TARGET_TYPE_CHASER, TARGET_TYPE_SWARM, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER,
    TARGET_SPEED,
    SCOUT_HP, SCOUT_SPEED, SCOUT_DIVE_SPEED, SCOUT_CONTACT_DAMAGE,
    SCOUT_SCORE, SCOUT_SIZE, SCOUT_TELEGRAPH_TIME, SCOUT_DIVE_DURATION,
    SCOUT_RECOVER_TIME, SCOUT_STRAFE_DURATION, SCOUT_CONTACT_COOLDOWN,
    SHOOTER_HP, SHOOTER_SPEED, SHOOTER_PREFERRED_DISTANCE, SHOOTER_MIN_DISTANCE,
    SHOOTER_MAX_DISTANCE, SHOOTER_SCORE, SHOOTER_SIZE, SHOOTER_PROJECTILE_DAMAGE,
    SHOOTER_PROJECTILE_SPEED, SHOOTER_FIRE_COOLDOWN, SHOOTER_TELEGRAPH_TIME,
    SHOOTER_REPOSITION_TIME,
    HEAVY_HP, HEAVY_SPEED, HEAVY_SCORE, HEAVY_SIZE, HEAVY_CONTACT_DAMAGE,
    HEAVY_CONTACT_COOLDOWN, HEAVY_ARMOR, HEAVY_PRESSURE_DISTANCE, HEAVY_TELEGRAPH_TIME
)
from src.entities.bullet import EnemyBullet, EnemySniperBeam
from src.entities.ai import BaseEnemyAI, EnemyAIContext, create_enemy_ai


class Enemy(pygame.sprite.Sprite):
    """Base and specialized 2D Hostile Target orchestrating stats, state, and modular AI."""

    def __init__(self, enemy_type: str = TARGET_TYPE_STANDARD, pos: tuple[float, float] = None,
                 speed_multiplier: float = 1.0, hp_multiplier: float = 1.0, sector_idx: int = 0,
                 level: int = 1, **kwargs):
        super().__init__()
        self.enemy_type = enemy_type
        self.sector_idx = sector_idx
        self.level = level
        sec_mult = 1.0 + sector_idx * 0.25
        speed_bonus = sector_idx * 15.0

        self.contact_cooldown_timer = 0.0
        self.heading_angle = 180.0
        self.armor = 0.0

        if enemy_type == TARGET_TYPE_SCOUT:
            base_hp = int(SCOUT_HP * sec_mult * hp_multiplier)
            self.points = SCOUT_SCORE
            size = SCOUT_SIZE
            base_speed = (SCOUT_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = (SCOUT_DIVE_SPEED + speed_bonus) * speed_multiplier
            self.contact_damage = SCOUT_CONTACT_DAMAGE
            self.color_outer = (244, 63, 94)  # Neon Rose / Amber-Crimson
            self.color_inner = COLOR_GOLD

        elif enemy_type == TARGET_TYPE_SHOOTER:
            base_hp = int(SHOOTER_HP * sec_mult * hp_multiplier)
            self.points = SHOOTER_SCORE
            size = SHOOTER_SIZE
            base_speed = (SHOOTER_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.projectile_speed = SHOOTER_PROJECTILE_SPEED
            self.projectile_damage = SHOOTER_PROJECTILE_DAMAGE
            self.contact_damage = 0.0
            self.color_outer = (239, 68, 68)  # Industrial Crimson
            self.color_inner = COLOR_GOLD

        elif enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            base_hp = int(HEAVY_HP * sec_mult * hp_multiplier)
            self.points = HEAVY_SCORE
            size = HEAVY_SIZE
            base_speed = (HEAVY_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = HEAVY_CONTACT_DAMAGE
            self.armor = HEAVY_ARMOR
            self.color_outer = (100, 116, 139)  # Armored Titanium / Slate
            self.color_inner = (245, 158, 11)   # Amber Warning Core

        elif enemy_type == TARGET_TYPE_FAST:
            base_hp = int(18 * sec_mult * hp_multiplier)
            self.points = 150
            size = 32
            base_speed = (TARGET_SPEED * 1.55 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed * 1.5
            self.contact_damage = 15.0
            self.color_outer = COLOR_GOLD
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_TURRET:
            base_hp = int(50 * sec_mult * hp_multiplier)
            self.points = 300
            size = 44
            base_speed = (TARGET_SPEED * 0.40 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = 25.0
            self.color_outer = (180, 40, 40)
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_VEHICLE:
            base_hp = int(45 * sec_mult * hp_multiplier)
            self.points = 220
            size = 42
            base_speed = (TARGET_SPEED * 0.80 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = 25.0
            self.color_outer = (130, 90, 40)
            self.color_inner = COLOR_GOLD

        elif enemy_type == TARGET_TYPE_CHASER:
            base_hp = int(24 * sec_mult * hp_multiplier)
            self.points = 180
            size = 34
            base_speed = (TARGET_SPEED * 1.25 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed * 1.4
            self.contact_damage = 20.0
            self.color_outer = (236, 72, 153)
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_SWARM:
            base_hp = int(12 * sec_mult * hp_multiplier)
            self.points = 100
            size = 24
            base_speed = (TARGET_SPEED * 1.80 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed * 1.3
            self.contact_damage = 12.0
            self.color_outer = (250, 204, 21)
            self.color_inner = (239, 68, 68)

        elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
            base_hp = int(40 * sec_mult * hp_multiplier)
            self.points = 280
            size = 40
            base_speed = (TARGET_SPEED * 0.70 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = 20.0
            self.color_outer = (59, 130, 246)
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_SNIPER:
            base_hp = int(20 * sec_mult * hp_multiplier)
            self.points = 260
            size = 36
            base_speed = (TARGET_SPEED * 0.60 + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = 15.0
            self.color_outer = (168, 85, 247)
            self.color_inner = COLOR_WHITE

        else:  # Standard
            base_hp = int(25 * sec_mult * hp_multiplier)
            self.points = 100
            size = 36
            base_speed = (TARGET_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = 20.0
            self.color_outer = COLOR_CRIMSON
            self.color_inner = COLOR_GOLD

        self.size = size
        self.speed = base_speed
        self.max_hp = max(1, base_hp)
        self.hp = self.max_hp
        self.score_value = self.points
        self.color = self.color_outer
        self.alive = True
        self.hit_flash_timer = 0.0
        self.emp_jammed_timer = 0.0

        if pos is None:
            spawn_x = random.randint(WORLD_WIDTH + 40, WORLD_WIDTH + 140)
            spawn_y = random.randint(80, WORLD_HEIGHT - 80)
            self.pos = pygame.Vector2(spawn_x, spawn_y)
        else:
            self.pos = pygame.Vector2(pos)

        self.base_y = self.pos.y
        self.time_accum = random.uniform(0.0, 10.0)
        self.anim_timer = random.uniform(0.0, 5.0)
        self.anim_frame = 0
        self.hover_offset = pygame.Vector2(0.0, 0.0)

        # Specialized AI Controller
        self.ai = create_enemy_ai(self.enemy_type, self)

        surf_size = 90 if enemy_type == TARGET_TYPE_SCOUT else (
            96 if enemy_type == TARGET_TYPE_SHOOTER else (
                120 if enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED) else (
                    100 if enemy_type == TARGET_TYPE_SHIELD_DRONE else max(self.size, 80)
                )
            )
        )
        self._base_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = self.size // 2

        # PERF: Sprite rebuild tracking — rebuilds with anim/angle/flash/hover
        self._last_heading_angle = self.heading_angle
        self._last_ai_state = self.ai_state
        self._last_hit_flash = False
        self._last_is_aiming = False
        self._last_anim_frame = 0
        self._cached_angle = self.heading_angle
        self._sprite_dirty = False
        self._heading_threshold = 2.5
        self._render_sprite()

    # -------------------------------------------------------------------------
    # AI State Delegation Properties
    # -------------------------------------------------------------------------
    @property
    def ai_state(self) -> str:
        return getattr(self.ai, "ai_state", "approach")

    @ai_state.setter
    def ai_state(self, val: str):
        if hasattr(self, "ai"):
            self.ai.ai_state = val

    @property
    def state_timer(self) -> float:
        return getattr(self.ai, "state_timer", 0.0)

    @state_timer.setter
    def state_timer(self, val: float):
        if hasattr(self, "ai"):
            self.ai.state_timer = float(val)

    @property
    def dive_dir(self) -> pygame.Vector2:
        return getattr(self.ai, "dive_dir", pygame.Vector2(0, 0))

    @dive_dir.setter
    def dive_dir(self, val: pygame.Vector2):
        if hasattr(self, "ai"):
            self.ai.dive_dir = pygame.Vector2(val)

    @property
    def dive_target(self) -> pygame.Vector2:
        return getattr(self.ai, "dive_target", pygame.Vector2(0, 0))

    @dive_target.setter
    def dive_target(self, val: pygame.Vector2):
        if hasattr(self, "ai"):
            self.ai.dive_target = pygame.Vector2(val)

    @property
    def strafe_dir(self) -> float:
        return getattr(self.ai, "strafe_dir", 1.0)

    @strafe_dir.setter
    def strafe_dir(self, val: float):
        if hasattr(self, "ai"):
            self.ai.strafe_dir = float(val)

    @property
    def recover_dir(self) -> pygame.Vector2:
        return getattr(self.ai, "recover_dir", pygame.Vector2(0, 0))

    @recover_dir.setter
    def recover_dir(self, val: pygame.Vector2):
        if hasattr(self, "ai"):
            self.ai.recover_dir = pygame.Vector2(val)

    @property
    def fire_timer(self) -> float:
        return getattr(self.ai, "fire_timer", 0.0)

    @fire_timer.setter
    def fire_timer(self, val: float):
        if hasattr(self, "ai"):
            self.ai.fire_timer = float(val)

    @property
    def reposition_dir(self) -> pygame.Vector2:
        return getattr(self.ai, "reposition_dir", pygame.Vector2(0, 0))

    @reposition_dir.setter
    def reposition_dir(self, val: pygame.Vector2):
        if hasattr(self, "ai"):
            self.ai.reposition_dir = pygame.Vector2(val)

    @property
    def aim_target(self) -> pygame.Vector2:
        return getattr(self.ai, "aim_target", pygame.Vector2(0, 0))

    @aim_target.setter
    def aim_target(self, val: pygame.Vector2):
        if hasattr(self, "ai"):
            self.ai.aim_target = pygame.Vector2(val)

    @property
    def is_aiming(self) -> bool:
        return getattr(self.ai, "is_aiming", False)

    @is_aiming.setter
    def is_aiming(self, val: bool):
        if hasattr(self, "ai"):
            self.ai.is_aiming = bool(val)

    @property
    def is_diving(self) -> bool:
        return getattr(self.ai, "is_diving", False)

    @is_diving.setter
    def is_diving(self, val: bool):
        if hasattr(self, "ai"):
            self.ai.is_diving = bool(val)

    @property
    def shield_angle(self) -> float:
        return getattr(self.ai, "shield_angle", 0.0)

    @shield_angle.setter
    def shield_angle(self, val: float):
        if hasattr(self, "ai"):
            self.ai.shield_angle = float(val)

    @property
    def shoot_timer(self) -> float:
        return getattr(self.ai, "shoot_timer", 0.0)

    @shoot_timer.setter
    def shoot_timer(self, val: float):
        if hasattr(self, "ai"):
            self.ai.shoot_timer = float(val)

    @property
    def sniper_aim_timer(self) -> float:
        return getattr(self.ai, "sniper_aim_timer", 0.0)

    @sniper_aim_timer.setter
    def sniper_aim_timer(self, val: float):
        if hasattr(self, "ai"):
            self.ai.sniper_aim_timer = float(val)

    @property
    def score_value(self) -> int:
        return getattr(self, "points", 100)

    @score_value.setter
    def score_value(self, val: int):
        self.points = val

    @property
    def color(self) -> tuple[int, int, int]:
        return getattr(self, "color_outer", (239, 68, 68))

    @color.setter
    def color(self, val: tuple[int, int, int]):
        self.color_outer = val

    # -------------------------------------------------------------------------
    # Combat & Damage Resolution
    # -------------------------------------------------------------------------
    def take_damage(self, amount: int, source: str = "bullet", **kwargs) -> bool:
        """Applies armor-mitigated damage and returns True if entity dies."""
        effective_damage = amount
        if getattr(self, "armor", 0.0) > 0.0:
            effective_damage = max(1, int(round(amount * (1.0 - self.armor))))
        self.hp -= effective_damage
        self.hit_flash_timer = 0.12 if getattr(self, "armor", 0.0) > 0.0 else 0.10
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.kill()
            return True
        return False

    # -------------------------------------------------------------------------
    # Update Cycle & Boundary Clamping
    # -------------------------------------------------------------------------
    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list:
        """Executes tactical movement, updates AI, and returns spawned hostile bullets."""
        if not self.alive:
            return []

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.contact_cooldown_timer > 0:
            self.contact_cooldown_timer -= dt

        if self.emp_jammed_timer > 0:
            self.emp_jammed_timer -= dt
            self._render_sprite()
            return []

        self.time_accum += dt
        self.anim_timer += dt

        context = EnemyAIContext(
            player_pos=player_pos,
            player_vel=player_vel,
            player_obj=player_obj,
            target_group=target_group,
            sector_idx=self.sector_idx
        )

        new_bullets = self.ai.update(dt, self, context)

        # Arena boundary clamping so enemies never escape or drift outside the battlefield
        self.pos.x = max(60.0, min(float(WORLD_WIDTH - 60.0), self.pos.x))
        self.pos.y = max(60.0, min(float(WORLD_HEIGHT - 60.0), self.pos.y))
        self.rect.center = (round(self.pos.x + self.hover_offset.x), round(self.pos.y + self.hover_offset.y))

        # PERF: Determine if sprite needs rebuild
        current_hit = self.hit_flash_timer > 0
        heading_changed = (
            self._last_heading_angle is None or
            abs(self.heading_angle - self._last_heading_angle) >= self._heading_threshold
        )
        state_changed = self.ai_state != self._last_ai_state
        flash_changed = current_hit != self._last_hit_flash
        aim_changed = self.is_aiming != self._last_is_aiming

        if self._sprite_dirty or state_changed or flash_changed or aim_changed or heading_changed:
            self._render_sprite()
            self._last_heading_angle = self.heading_angle
            self._last_ai_state = self.ai_state
            self._last_hit_flash = current_hit
            self._last_is_aiming = self.is_aiming
            self._sprite_dirty = False

        return new_bullets

    # -------------------------------------------------------------------------
    # Sprite Rendering
    # -------------------------------------------------------------------------
    def _render_sprite(self):
        s = 90 if self.enemy_type == TARGET_TYPE_SCOUT else (
            96 if self.enemy_type == TARGET_TYPE_SHOOTER else (
                120 if self.enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED) else (
                    100 if self.enemy_type == TARGET_TYPE_SHIELD_DRONE else max(self.size, 80)
                )
            )
        )
        self._base_surf.fill((0, 0, 0, 0))
        surf = self._base_surf
        center = (s // 2, s // 2)

        if self.enemy_type == TARGET_TYPE_SCOUT:
            from src.rendering.sprite_manager import get_sprite_manager
            sm = get_sprite_manager()

            if self.hit_flash_timer > 0:
                state = "hit"
            elif self.ai_state == "dive":
                state = "attack"
            elif self.ai_state in ("approach", "strafe", "recover"):
                state = "move"
            else:
                state = "idle"

            rotated_scout = sm.get_rotated_scout_sprite(state=state, angle_deg=-self.heading_angle, target_size=(78, 70))
            rot_rect = rotated_scout.get_rect(center=center)

            if self.ai_state == "telegraph":
                surf.blit(rotated_scout, rot_rect)
                alpha = int(140 + 100 * math.sin(self.state_timer * 22.0))
                pygame.draw.circle(surf, (244, 63, 94, max(0, min(255, alpha))), center, 36, 3)
            else:
                surf.blit(rotated_scout, rot_rect)

            # ── SCOUT IDENTITY VFX: Forward interceptor needle cannon + propulsion streaks ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x

            # Forward kinetic needle cannon mount
            nx_base = center[0] + fwd_x * 8
            ny_base = center[1] + fwd_y * 8
            nx_tip = center[0] + fwd_x * 36
            ny_tip = center[1] + fwd_y * 36
            pygame.draw.line(surf, (51, 65, 85), (int(nx_base), int(ny_base)), (int(nx_tip), int(ny_tip)), 4)
            pygame.draw.line(surf, (148, 163, 184), (int(nx_base), int(ny_base)), (int(nx_tip - fwd_x * 3), int(ny_tip - fwd_y * 3)), 2)
            # Needle ionization muzzle tip
            tip_col = (244, 63, 94) if self.ai_state != "dive" else (255, 255, 255)
            pygame.draw.circle(surf, tip_col, (int(nx_tip), int(ny_tip)), 4 if self.ai_state == "dive" else 2)

            # Two narrow propulsion bursts at rear
            thruster_intensity = int(160 + 80 * math.sin(self.time_accum * 12.0))
            for side in (-12.0, 12.0):
                rx = center[0] - fwd_x * 30 + right_x * side
                ry = center[1] - fwd_y * 30 + right_y * side
                streak_len = 14 + int(8 * math.sin(self.time_accum * 15.0 + side))
                tip_x = rx - fwd_x * streak_len
                tip_y = ry - fwd_y * streak_len
                b_col = (56, 189, 248, max(0, min(255, thruster_intensity)))
                pygame.draw.line(surf, b_col, (int(rx), int(ry)), (int(tip_x), int(tip_y)), 2)
                # Inner bright white core
                white_tip_x = rx - fwd_x * (streak_len * 0.45)
                white_tip_y = ry - fwd_y * (streak_len * 0.45)
                pygame.draw.line(surf, (200, 230, 255, 180), (int(rx), int(ry)), (int(white_tip_x), int(white_tip_y)), 1)

            # Hit flash: copy+overlay so base surf stays clean
            if self.hit_flash_timer > 0:
                flash_copy = surf.copy()
                mask = pygame.mask.from_surface(flash_copy)
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
                flash_copy.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_copy
            else:
                self.image = surf

            self._cached_angle = self.heading_angle
            self._sprite_dirty = False

        elif self.enemy_type == TARGET_TYPE_SHOOTER:
            from src.rendering.sprite_manager import get_sprite_manager
            sm = get_sprite_manager()

            if self.hit_flash_timer > 0:
                state = "hit"
            elif self.ai_state == "telegraph":
                state = "attack"
            elif self.ai_state in ("approach", "reposition", "strafe"):
                state = "move"
            else:
                state = "idle"

            rotated_shooter = sm.get_rotated_shooter_sprite(state=state, angle_deg=-self.heading_angle, target_size=(88, 80))
            rot_rect = rotated_shooter.get_rect(center=center)
            surf.blit(rotated_shooter, rot_rect)

            # ── SHOOTER IDENTITY: Physical Heavy Rail Cannon Assembly + Muzzle Flares ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x

            # 1. Main Forward Heavy Cannon Barrel
            c_base_x = center[0] + fwd_x * 8
            c_base_y = center[1] + fwd_y * 8
            c_tip_x = center[0] + fwd_x * 34
            c_tip_y = center[1] + fwd_y * 34
            pygame.draw.line(surf, (30, 41, 59), (int(c_base_x), int(c_base_y)), (int(c_tip_x), int(c_tip_y)), 7)
            pygame.draw.line(surf, (71, 85, 105), (int(c_base_x), int(c_base_y)), (int(c_tip_x - fwd_x * 4), int(c_tip_y - fwd_y * 4)), 4)
            pygame.draw.line(surf, (245, 158, 11), (int(c_base_x), int(c_base_y)), (int(c_tip_x - fwd_x * 2), int(c_tip_y - fwd_y * 2)), 2)

            # 2. Side Stabilizer Pylons
            for side in (-14.0, 14.0):
                p_base_x = center[0] + fwd_x * 12 + right_x * side
                p_base_y = center[1] + fwd_y * 12 + right_y * side
                p_tip_x = center[0] + fwd_x * 26 + right_x * side
                p_tip_y = center[1] + fwd_y * 26 + right_y * side
                pygame.draw.line(surf, (51, 65, 85), (int(p_base_x), int(p_base_y)), (int(p_tip_x), int(p_tip_y)), 3)
                pygame.draw.circle(surf, (245, 158, 11, 180), (int(p_tip_x), int(p_tip_y)), 2)

            # 3. Telegraph Muzzle Flash & Charging Burst
            muz_x = center[0] + fwd_x * 34
            muz_y = center[1] + fwd_y * 34
            if self.ai_state == "telegraph":
                charge_alpha = int(180 + 75 * math.sin(self.state_timer * 28.0))
                charge_r = max(5, int(14 * (self.state_timer / SHOOTER_TELEGRAPH_TIME)))
                pygame.draw.circle(surf, (239, 68, 68, max(0, min(255, charge_alpha))), (int(muz_x), int(muz_y)), charge_r + 4)
                pygame.draw.circle(surf, (245, 158, 11, 230), (int(muz_x), int(muz_y)), charge_r + 1)
                pygame.draw.circle(surf, (255, 255, 255, 255), (int(muz_x), int(muz_y)), max(2, charge_r - 2))
            else:
                emitter_alpha = int(90 + 50 * math.sin(self.time_accum * 6.0))
                pygame.draw.circle(surf, (245, 158, 11, max(0, min(255, emitter_alpha))), (int(muz_x), int(muz_y)), 4)
                pygame.draw.circle(surf, (255, 255, 255, 200), (int(muz_x), int(muz_y)), 2)

            if self.hit_flash_timer > 0:
                flash_copy = surf.copy()
                mask = pygame.mask.from_surface(flash_copy)
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
                flash_copy.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_copy
            else:
                self.image = surf

            self._cached_angle = self.heading_angle
            self._sprite_dirty = False

        elif self.enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            from src.rendering.sprite_manager import get_sprite_manager
            sm = get_sprite_manager()

            if self.hit_flash_timer > 0:
                state = "hit"
            elif self.ai_state == "pressure":
                state = "attack"
            elif self.ai_state in ("approach", "strafe", "advance"):
                state = "move"
            else:
                state = "idle"

            rotated_heavy = sm.get_rotated_heavy_sprite(state=state, angle_deg=-self.heading_angle, target_size=(110, 102))
            rot_rect = rotated_heavy.get_rect(center=center)
            surf.blit(rotated_heavy, rot_rect)

            # ── HEAVY IDENTITY: Twin Wing Autocannon Sponsons + Hot Exhaust ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x

            # Twin Heavy Autocannons on Port & Starboard
            for side in (-26.0, 26.0):
                h_base_x = center[0] + fwd_x * 6 + right_x * side
                h_base_y = center[1] + fwd_y * 6 + right_y * side
                h_tip_x = center[0] + fwd_x * 40 + right_x * side
                h_tip_y = center[1] + fwd_y * 40 + right_y * side
                pygame.draw.line(surf, (30, 41, 59), (int(h_base_x), int(h_base_y)), (int(h_tip_x), int(h_tip_y)), 6)
                pygame.draw.line(surf, (71, 85, 105), (int(h_base_x), int(h_base_y)), (int(h_tip_x - fwd_x * 3), int(h_tip_y - fwd_y * 3)), 3)
                pygame.draw.line(surf, (245, 120, 20), (int(h_base_x), int(h_base_y)), (int(h_tip_x - fwd_x * 5), int(h_tip_y - fwd_y * 5)), 2)
                pygame.draw.circle(surf, (15, 23, 42), (int(h_tip_x), int(h_tip_y)), 3)
                if self.ai_state == "pressure":
                    pygame.draw.circle(surf, (245, 158, 11, 220), (int(h_tip_x), int(h_tip_y)), 5)
                    pygame.draw.circle(surf, (255, 255, 255, 255), (int(h_tip_x), int(h_tip_y)), 2)

            # Dual hot engine plumes at rear
            eng_intensity = int(190 + 60 * math.sin(self.time_accum * 8.0))
            for side in (-18.0, 18.0):
                ex = center[0] - fwd_x * 42 + right_x * side
                ey = center[1] - fwd_y * 42 + right_y * side
                plume_len = 16 + int(10 * abs(math.sin(self.time_accum * 7.5 + side)))
                tip_x = ex - fwd_x * plume_len
                tip_y = ey - fwd_y * plume_len
                pygame.draw.line(surf, (245, 120, 20, max(0, min(255, eng_intensity))), (int(ex), int(ey)), (int(tip_x), int(tip_y)), 4)
                pygame.draw.line(surf, (255, 210, 40, max(0, min(255, eng_intensity))), (int(ex), int(ey)), (int(ex - fwd_x * plume_len * 0.4), int(ey - fwd_y * plume_len * 0.4)), 2)

            if self.ai_state == "pressure":
                glow_alpha = int(150 + 90 * math.sin(self.state_timer * 20.0))
                pygame.draw.circle(surf, (245, 100, 11, max(0, min(255, glow_alpha))), center, s // 2 - 4, 3)

            if self.hit_flash_timer > 0:
                flash_copy = surf.copy()
                mask = pygame.mask.from_surface(flash_copy)
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
                flash_copy.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_copy
            else:
                self.image = surf

            self._cached_angle = self.heading_angle
            self._sprite_dirty = False

        elif self.enemy_type == TARGET_TYPE_SHIELD_DRONE:
            from src.rendering.sprite_manager import get_sprite_manager
            sm = get_sprite_manager()

            state = "hit" if self.hit_flash_timer > 0 else "idle"
            rotated_shield = sm.get_rotated_shield_drone_sprite(state=state, angle_deg=-self.heading_angle, target_size=(90, 82))
            rot_rect = rotated_shield.get_rect(center=center)
            surf.blit(rotated_shield, rot_rect)

            # ── SHIELD ELITE IDENTITY VFX: Dual rotating energy arcs + inner pulse ──
            arc_rect = pygame.Rect(8, 8, s - 16, s - 16)
            arc_alpha = int(200 + 55 * math.sin(self.time_accum * 5.0))
            pygame.draw.arc(surf, (56, 189, 248, max(0, min(255, arc_alpha))), arc_rect,
                            self.shield_angle, self.shield_angle + 1.9, 3)
            pygame.draw.arc(surf, (180, 230, 255, 130), arc_rect,
                            self.shield_angle + math.pi, self.shield_angle + math.pi + 1.2, 2)
            pulse_r = int(4 + 2 * math.sin(self.time_accum * 8.0))
            pygame.draw.circle(surf, (56, 189, 248, 220), center, pulse_r)
            pygame.draw.circle(surf, (255, 255, 255, 160), center, max(1, pulse_r - 2))

            if self.hit_flash_timer > 0:
                flash_copy = surf.copy()
                mask = pygame.mask.from_surface(flash_copy)
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
                flash_copy.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_copy
            else:
                self.image = surf

            self._cached_angle = self.heading_angle
            self._sprite_dirty = False

        elif self.enemy_type == TARGET_TYPE_SNIPER:
            pygame.draw.polygon(surf, self.color_outer, [(s, s // 2), (0, 4), (s // 4, s // 2), (0, s - 4)])
            if self.is_aiming:
                pygame.draw.circle(surf, COLOR_NEON_RED, center, 6)
                if hasattr(self, "sniper_aim_target"):
                    aim_target = self.sniper_aim_target
                    start_pos = self.rect.center
                    end_pos = (int(round(aim_target.x)), int(round(aim_target.y)))
                    pygame.draw.line(surf, (239, 68, 68, 180), start_pos, end_pos, 2)
                    pygame.draw.line(surf, (255, 200, 200, 120), start_pos, end_pos, 1)
            else:
                pygame.draw.circle(surf, self.color_inner, center, 4)

        else:  # Standard
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_inner, center, s // 4)

        if self.enemy_type == TARGET_TYPE_SCOUT:
            pass
        elif self.enemy_type in (TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED, TARGET_TYPE_SHIELD_DRONE):
            pass
        else:
            if self.hit_flash_timer > 0:
                mask = pygame.mask.from_surface(surf)
                flash_surf = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
                surf.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            angle_changed = (
                self._cached_angle is None or
                abs(self.heading_angle - self._cached_angle) >= self._heading_threshold
            )

            if angle_changed or self._sprite_dirty:
                self.image = pygame.transform.rotate(self._base_surf, -self.heading_angle)
                self._cached_angle = self.heading_angle
                self._sprite_dirty = False

        self.rect = self.image.get_rect(center=self.rect.center)


class Scout(Enemy):
    """Convenience alias/subclass for Phase 2A Scout Drone."""
    def __init__(self, pos: tuple[float, float] = None, enemy_type: str = TARGET_TYPE_SCOUT, **kwargs):
        super().__init__(enemy_type=enemy_type, pos=pos, **kwargs)


class Shooter(Enemy):
    """Convenience alias/subclass for Phase 2B Shooter Drone."""
    def __init__(self, pos: tuple[float, float] = None, enemy_type: str = TARGET_TYPE_SHOOTER, **kwargs):
        super().__init__(enemy_type=enemy_type, pos=pos, **kwargs)


class Heavy(Enemy):
    """Convenience alias/subclass for Phase 2C Heavy Drone."""
    def __init__(self, pos: tuple[float, float] = None, enemy_type: str = TARGET_TYPE_HEAVY, **kwargs):
        super().__init__(enemy_type=enemy_type, pos=pos, **kwargs)
