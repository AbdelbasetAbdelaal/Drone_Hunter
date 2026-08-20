"""
================================================================================
                    DRONE HUNTER 2D - 2D ENEMY TARGET SPRITES
================================================================================
Defines hostile drone archetypes with specialized tactical AI:
- Scout: High-speed strafing and predictive telegraph diving melee interceptor (Phase 2A)
- Shooter: Positional pressure drone with range keeping, deliberate aim, telegraph, and single-shot firing (Phase 2B)
- Swarm, Chaser, Fast, Armored, Shield Drone, Sniper, Turret, Vehicle
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


class Enemy(pygame.sprite.Sprite):
    """Base and specialized 2D Hostile Target."""
    def __init__(self, enemy_type: str = TARGET_TYPE_STANDARD, pos: tuple[float, float] = None,
                 speed_multiplier: float = 1.0, hp_multiplier: float = 1.0, sector_idx: int = 0,
                 level: int = 1, **kwargs):
        super().__init__()
        self.enemy_type = enemy_type
        self.sector_idx = sector_idx
        self.level = level
        sec_mult = 1.0 + sector_idx * 0.25
        speed_bonus = sector_idx * 15.0

        self.ai_state = "approach"
        self.state_timer = 0.0
        self.dive_dir = pygame.Vector2(0, 0)
        self.dive_target = pygame.Vector2(0, 0)
        self.strafe_dir = random.choice([-1.0, 1.0])
        self.recover_dir = pygame.Vector2(0, 0)
        self.contact_cooldown_timer = 0.0
        self.heading_angle = 180.0
        self.fire_timer = 0.0
        self.reposition_dir = pygame.Vector2(0, 0)
        self.aim_target = pygame.Vector2(0, 0)
        self.armor = 0.0

        if enemy_type == TARGET_TYPE_SCOUT:
            base_hp = int(SCOUT_HP * sec_mult * hp_multiplier)
            self.points = SCOUT_SCORE
            size = SCOUT_SIZE
            base_speed = (SCOUT_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = (SCOUT_DIVE_SPEED + speed_bonus) * speed_multiplier
            self.contact_damage = SCOUT_CONTACT_DAMAGE
            self.color_outer = (244, 63, 94) # Neon Rose / Amber-Crimson
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
            self.color_outer = (239, 68, 68) # Industrial Crimson
            self.color_inner = COLOR_GOLD

        elif enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            base_hp = int(HEAVY_HP * sec_mult * hp_multiplier)
            self.points = HEAVY_SCORE
            size = HEAVY_SIZE
            base_speed = (HEAVY_SPEED + speed_bonus) * speed_multiplier
            self.dive_speed = base_speed
            self.contact_damage = HEAVY_CONTACT_DAMAGE
            self.armor = HEAVY_ARMOR
            self.color_outer = (100, 116, 139) # Armored Titanium / Slate
            self.color_inner = (245, 158, 11)  # Amber Warning Core

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

        else: # Standard
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
        self.is_diving = False
        self.shield_angle = 0.0
        self.shoot_timer = random.uniform(0.8, 2.2)
        self.sniper_aim_timer = random.uniform(1.5, 3.0)
        self.is_aiming = False

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

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list:
        """Executes tactical movement, state machine, and returns spawned hostile bullets."""
        if not self.alive:
            return []

        new_bullets = []
        self.time_accum += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.contact_cooldown_timer > 0:
            self.contact_cooldown_timer -= dt

        bullet_speed = 320.0 + self.sector_idx * 30.0
        pred_aim_x = player_pos[0] + player_vel[0] * 0.35
        pred_aim_y = player_pos[1] + player_vel[1] * 0.35
        pred_aim = (pred_aim_x, pred_aim_y)

        # ----------------------------------------------------------------------
        # SCOUT TACTICAL AI (Phase 2A Baseline)
        # ----------------------------------------------------------------------
        if self.enemy_type == TARGET_TYPE_SCOUT:
            self.state_timer += dt
            to_player = pygame.Vector2(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
            dist = to_player.length()
            norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

            if self.ai_state == "approach":
                move_dir = norm_to_player
                self.pos += move_dir * self.speed * dt
                self.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
                if dist <= 360.0 or self.state_timer >= 2.4:
                    self.ai_state = "strafe"
                    self.state_timer = 0.0
                    self.strafe_dir = random.choice([-1.0, 1.0])

            elif self.ai_state == "strafe":
                lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                radial_bias = 0.30 if dist > 300.0 else (-0.25 if dist < 200.0 else 0.0)
                move_vec = (lateral + norm_to_player * radial_bias)
                if move_vec.length() > 0.001:
                    move_vec = move_vec.normalize()
                self.pos += move_vec * self.speed * dt
                self.heading_angle = math.degrees(math.atan2(move_vec.y, move_vec.x))

                if self.state_timer >= SCOUT_STRAFE_DURATION:
                    self.ai_state = "telegraph"
                    self.state_timer = 0.0
                    self.dive_target = pygame.Vector2(pred_aim_x, pred_aim_y)
                    dive_vec = self.dive_target - self.pos
                    self.dive_dir = dive_vec.normalize() if dive_vec.length() > 0.001 else norm_to_player

            elif self.ai_state == "telegraph":
                self.pos += self.dive_dir * (self.speed * 0.12) * dt
                self.heading_angle = math.degrees(math.atan2(self.dive_dir.y, self.dive_dir.x))
                if self.state_timer >= SCOUT_TELEGRAPH_TIME:
                    self.ai_state = "dive"
                    self.state_timer = 0.0

            elif self.ai_state == "dive":
                self.pos += self.dive_dir * self.dive_speed * dt
                self.heading_angle = math.degrees(math.atan2(self.dive_dir.y, self.dive_dir.x))
                if self.state_timer >= SCOUT_DIVE_DURATION:
                    self.ai_state = "recover"
                    self.state_timer = 0.0
                    away_vec = self.pos - pygame.Vector2(player_pos[0], player_pos[1])
                    self.recover_dir = away_vec.normalize() if away_vec.length() > 0.001 else -self.dive_dir

            elif self.ai_state == "recover":
                self.pos += self.recover_dir * (self.speed * 0.85) * dt
                self.heading_angle = math.degrees(math.atan2(self.recover_dir.y, self.recover_dir.x))
                if self.state_timer >= SCOUT_RECOVER_TIME:
                    self.ai_state = "strafe"
                    self.state_timer = 0.0
                    self.strafe_dir = random.choice([-1.0, 1.0])

        # ----------------------------------------------------------------------
        # SHOOTER TACTICAL AI (Phase 2B Positioning Pressure)
        # ----------------------------------------------------------------------
        elif self.enemy_type == TARGET_TYPE_SHOOTER:
            self.state_timer += dt
            self.fire_timer += dt
            to_player = pygame.Vector2(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
            dist = to_player.length()
            norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

            if self.ai_state == "approach":
                # Approach until inside preferred combat distance (~420-520px)
                move_dir = norm_to_player
                self.pos += move_dir * self.speed * dt
                self.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
                if dist <= SHOOTER_PREFERRED_DISTANCE + 50.0:
                    self.ai_state = "position"
                    self.state_timer = 0.0

            elif self.ai_state == "position":
                # Maintain preferred distance band (300-550px)
                if dist > 550.0:
                    move_dir = norm_to_player
                elif dist < 300.0:
                    move_dir = -norm_to_player
                else:
                    # Gentle lateral orbit within tolerance band
                    lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                    move_dir = lateral

                if move_dir.length_squared() > 0.001:
                    move_dir = move_dir.normalize()
                self.pos += move_dir * (self.speed * 0.75) * dt
                self.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))

                # When fire cooldown has elapsed, transition to AIM
                if self.fire_timer >= SHOOTER_FIRE_COOLDOWN:
                    self.ai_state = "aim"
                    self.state_timer = 0.0

            elif self.ai_state == "aim":
                # Calculate limited predictive target aim vector (0.25s lead)
                pred_x = player_pos[0] + player_vel[0] * 0.25
                pred_y = player_pos[1] + player_vel[1] * 0.25
                self.aim_target = pygame.Vector2(pred_x, pred_y)
                aim_vec = self.aim_target - self.pos
                if aim_vec.length() > 0.001:
                    self.heading_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x))
                self.ai_state = "telegraph"
                self.state_timer = 0.0

            elif self.ai_state == "telegraph":
                # Steady hover with subtle world-space charging glow
                aim_vec = self.aim_target - self.pos
                if aim_vec.length() > 0.001:
                    self.heading_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x))
                if self.state_timer >= SHOOTER_TELEGRAPH_TIME:
                    cx, cy = self.rect.center
                    bullet = EnemyBullet(
                        (cx, cy), (self.aim_target.x, self.aim_target.y),
                        speed=self.projectile_speed, damage=self.projectile_damage
                    )
                    new_bullets.append(bullet)
                    self.fire_timer = 0.0
                    self.ai_state = "reposition"
                    self.state_timer = 0.0

                    # Pick a tactical reposition direction
                    if dist < 350.0:
                        self.reposition_dir = -norm_to_player
                    else:
                        self.strafe_dir = -self.strafe_dir # flip orbit direction
                        lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                        self.reposition_dir = lateral.normalize()

            elif self.ai_state == "fire":
                # Fire exactly ONE deliberate hostile projectile
                cx, cy = self.rect.center
                bullet = EnemyBullet(
                    (cx, cy), (self.aim_target.x, self.aim_target.y),
                    speed=self.projectile_speed, damage=self.projectile_damage
                )
                new_bullets.append(bullet)
                self.fire_timer = 0.0
                self.ai_state = "reposition"
                self.state_timer = 0.0

                # Pick a tactical reposition direction
                if dist < 350.0:
                    self.reposition_dir = -norm_to_player
                else:
                    self.strafe_dir = -self.strafe_dir # flip orbit direction
                    lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                    self.reposition_dir = lateral.normalize()

            elif self.ai_state == "reposition":
                # Evasive repositioning
                self.pos += self.reposition_dir * self.speed * dt
                self.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))
                if self.state_timer >= SHOOTER_REPOSITION_TIME:
                    self.ai_state = "position"
                    self.state_timer = 0.0

        # ----------------------------------------------------------------------
        # HEAVY TACTICAL AI (Phase 2C Target Prioritization Pressure)
        # ----------------------------------------------------------------------
        elif self.enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            self.state_timer += dt
            to_player = pygame.Vector2(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
            dist = to_player.length()
            norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

            if self.ai_state == "approach":
                # Advance steadily and predictably toward player with heavy momentum
                move_dir = norm_to_player
                self.pos += move_dir * self.speed * dt
                self.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
                if dist <= HEAVY_PRESSURE_DISTANCE:
                    self.ai_state = "pressure"
                    self.state_timer = 0.0

            elif self.ai_state == "pressure":
                # Maintain relentless forward space pressure toward player
                move_dir = norm_to_player
                self.pos += move_dir * (self.speed * 1.15) * dt
                self.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))

                # After sustained pressure window or if player flees far
                if self.state_timer >= 2.5 or dist > HEAVY_PRESSURE_DISTANCE + 120.0:
                    self.ai_state = "recover"
                    self.state_timer = 0.0
                    lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                    self.recover_dir = (norm_to_player * 0.4 + lateral * 0.6).normalize()

            elif self.ai_state == "recover":
                # Brief stabilization / hydraulic vent venting period before re-engaging
                self.pos += self.recover_dir * (self.speed * 0.65) * dt
                self.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))

                if self.state_timer >= 0.85:
                    self.ai_state = "approach"
                    self.state_timer = 0.0
                    self.strafe_dir = random.choice([-1.0, 1.0])

        # ----------------------------------------------------------------------
        # OTHER LEGACY TARGET TYPES
        # ----------------------------------------------------------------------
        elif self.enemy_type == TARGET_TYPE_SWARM:
            self.pos.x -= self.speed * dt
            self.pos.y = self.base_y + math.sin(self.time_accum * 6.0) * 45.0
            if self.pos.x < SCREEN_WIDTH * 0.65 and not self.is_diving:
                if abs(self.pos.y - player_pos[1]) < 120.0:
                    self.is_diving = True
            if self.is_diving:
                dy = player_pos[1] - self.pos.y
                self.pos.y += (1.0 if dy > 0 else -1.0) * self.speed * 0.8 * dt

        elif self.enemy_type == TARGET_TYPE_CHASER:
            self.pos.x -= self.speed * 0.85 * dt
            dy = player_pos[1] - self.pos.y
            self.pos.y += math.copysign(min(abs(dy), self.speed * 0.75 * dt), dy)

        elif self.enemy_type == TARGET_TYPE_FAST:
            self.pos.x -= self.speed * dt
            self.pos.y = self.base_y + math.sin(self.time_accum * 4.5) * 35.0

        elif self.enemy_type == TARGET_TYPE_SHIELD_DRONE:
            self.pos.x -= self.speed * dt
            self.pos.y = self.base_y + math.cos(self.time_accum * 2.0) * 30.0
            self.shield_angle = (self.shield_angle + 4.0 * dt) % 6.28318

        elif self.enemy_type == TARGET_TYPE_SNIPER:
            self.pos.x -= self.speed * dt
            self.sniper_aim_timer -= dt
            self.is_aiming = self.sniper_aim_timer <= 0.8
            if self.sniper_aim_timer <= 0.0:
                self.sniper_aim_timer = random.uniform(2.2, 3.2)
                self.is_aiming = False
                cx, cy = self.rect.center
                new_bullets.append(EnemySniperBeam((cx - 20, cy), pred_aim, speed=bullet_speed + 800))

        else: # Standard, Turret, Vehicle
            self.pos.x -= self.speed * dt
            self.pos.y = self.base_y + math.sin(self.time_accum * 2.5) * 22.0

        # Natural organic flight animation: hovering bob & thruster oscillation
        self.anim_timer += dt
        self.time_accum += dt
        hover_amp = 3.5 if self.enemy_type == TARGET_TYPE_SCOUT else (2.0 if self.enemy_type == TARGET_TYPE_SHOOTER else 1.2)
        hover_freq = 4.5 if self.enemy_type == TARGET_TYPE_SCOUT else 3.0
        self.hover_offset.y = math.sin(self.time_accum * hover_freq) * hover_amp
        self.hover_offset.x = math.cos(self.time_accum * (hover_freq * 0.7)) * (hover_amp * 0.5)

        self.rect.center = (round(self.pos.x + self.hover_offset.x), round(self.pos.y + self.hover_offset.y))

        # --- Shooting Behaviors for Turrets ---
        if self.enemy_type == TARGET_TYPE_TURRET:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                cx, cy = self.rect.center
                self.shoot_timer = max(0.7, random.uniform(1.3, 1.9) - self.sector_idx * 0.15)
                new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=-12.0))
                new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 90, angle_offset_deg=0.0))
                new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=12.0))

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

            # ── SCOUT IDENTITY VFX: Bright cyan/blue propulsion streak (fast/light identity) ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x
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
                self.image = surf  # reuse same _base_surf — preserves identity between redraws

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

            # ── SHOOTER IDENTITY VFX: Weapon-platform emitter glow at front hardpoints ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x

            if self.ai_state == "telegraph":
                charge_alpha = int(160 + 95 * math.sin(self.state_timer * 26.0))
                charge_r = max(3, int(10 * (self.state_timer / SHOOTER_TELEGRAPH_TIME)))
                # Central bright weapon muzzle charge glow
                muz_x = center[0] + fwd_x * 32
                muz_y = center[1] + fwd_y * 32
                pygame.draw.circle(surf, (255, 220, 60, max(0, min(255, charge_alpha))), (int(muz_x), int(muz_y)), charge_r + 2)
                pygame.draw.circle(surf, (255, 255, 255, max(0, min(255, charge_alpha))), (int(muz_x), int(muz_y)), max(1, charge_r - 1))
            else:
                # Subtle persistent weapon-emitter dot (readability in idle)
                muz_x = center[0] + fwd_x * 30
                muz_y = center[1] + fwd_y * 30
                emitter_alpha = int(80 + 50 * math.sin(self.time_accum * 6.0))
                pygame.draw.circle(surf, (255, 200, 80, max(0, min(255, emitter_alpha))), (int(muz_x), int(muz_y)), 4)
                # Side hardpoint dots
                for side in (-14.0, 14.0):
                    hx = center[0] + fwd_x * 22 + right_x * side
                    hy = center[1] + fwd_y * 22 + right_y * side
                    pygame.draw.circle(surf, (200, 160, 60, 90), (int(hx), int(hy)), 2)

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

            # ── HEAVY IDENTITY VFX: Hot orange engine exhaust + threat ring in pressure ──
            aim_rad = math.radians(-self.heading_angle)
            fwd_x = math.cos(aim_rad)
            fwd_y = math.sin(aim_rad)
            right_x = -fwd_y
            right_y = fwd_x

            # Dual hot engine plumes at rear (large, hot orange — armored threat identity)
            eng_intensity = int(190 + 60 * math.sin(self.time_accum * 8.0))
            for side in (-18.0, 18.0):
                ex = center[0] - fwd_x * 42 + right_x * side
                ey = center[1] - fwd_y * 42 + right_y * side
                plume_len = 16 + int(10 * abs(math.sin(self.time_accum * 7.5 + side)))
                tip_x = ex - fwd_x * plume_len
                tip_y = ey - fwd_y * plume_len
                # Outer orange plume
                pygame.draw.line(surf, (245, 120, 20, max(0, min(255, eng_intensity))), (int(ex), int(ey)), (int(tip_x), int(tip_y)), 4)
                # Inner hot yellow core
                pygame.draw.line(surf, (255, 210, 40, max(0, min(255, eng_intensity))), (int(ex), int(ey)), (int(ex - fwd_x * plume_len * 0.4), int(ey - fwd_y * plume_len * 0.4)), 2)

            if self.ai_state == "pressure":
                # Pressure mode: strong orange threat ring
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
            # Primary rotating arc (electric blue)
            arc_rect = pygame.Rect(8, 8, s - 16, s - 16)
            arc_alpha = int(200 + 55 * math.sin(self.time_accum * 5.0))
            pygame.draw.arc(surf, (56, 189, 248, max(0, min(255, arc_alpha))), arc_rect,
                            self.shield_angle, self.shield_angle + 1.9, 3)
            # Counter-rotating secondary arc (white)
            pygame.draw.arc(surf, (180, 230, 255, 130), arc_rect,
                            self.shield_angle + math.pi, self.shield_angle + math.pi + 1.2, 2)
            # Inner energy pulse dot at shield emitter center
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
            else:
                pygame.draw.circle(surf, self.color_inner, center, 4)

        else: # Standard
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_inner, center, s // 4)

        if self.enemy_type == TARGET_TYPE_SCOUT:
            pass  # handled above with identity-preserving logic
        elif self.enemy_type in (TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED, TARGET_TYPE_SHIELD_DRONE):
            pass  # handled above with identity-preserving logic
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
