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
        self.is_diving = False
        self.shield_angle = 0.0
        self.shoot_timer = random.uniform(0.8, 2.2)
        self.sniper_aim_timer = random.uniform(1.5, 3.0)
        self.is_aiming = False

        self._base_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = self.size // 2

        # PERF: Sprite rebuild tracking — only rebuild when visual state changes
        self._last_heading_angle = None  # track last rendered angle
        self._last_ai_state = None       # track last rendered ai_state
        self._last_hit_flash = False     # track hit flash state
        self._last_is_aiming = False     # track sniper aim state
        self._cached_angle = None        # angle corresponding to cached rotation
        self._sprite_dirty = True        # force rebuild on first frame
        self._heading_threshold = 3.0   # degrees threshold before re-rotating
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

        self.rect.center = (round(self.pos.x), round(self.pos.y))

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
        s = self.size
        self._base_surf.fill((0, 0, 0, 0))
        surf = self._base_surf
        center = (s // 2, s // 2)

        if self.enemy_type == TARGET_TYPE_SCOUT:
            # High-speed aerodynamic delta-wing
            points = [
                (s - 2, s // 2),
                (2, 2),
                (8, s // 2),
                (2, s - 2)
            ]
            pygame.draw.polygon(surf, self.color_outer, points)
            pygame.draw.polygon(surf, self.color_inner, [
                (s - 8, s // 2),
                (6, 6),
                (10, s // 2),
                (6, s - 6)
            ])
            pygame.draw.circle(surf, COLOR_WHITE, (s // 2, s // 2), 3)

            if self.ai_state == "telegraph":
                alpha = int(140 + 100 * math.sin(self.state_timer * 22.0))
                glow_s = pygame.Surface((s + 12, s + 12), pygame.SRCALPHA)
                pygame.draw.circle(glow_s, (244, 63, 94, max(0, min(255, alpha))), ((s + 12) // 2, (s + 12) // 2), (s + 12) // 2, 2)
                surf.blit(glow_s, (-6, -6))

        elif self.enemy_type == TARGET_TYPE_SHOOTER:
            # Faceted angular ranged chassis with directional heavy barrel
            half = s // 2
            points = [
                (s - 2, half),
                (half + 4, 3),
                (3, 7),
                (7, half),
                (3, s - 7),
                (half + 4, s - 3)
            ]
            pygame.draw.polygon(surf, self.color_outer, points)
            # Inner armor plate & sensor optic
            pygame.draw.polygon(surf, (185, 28, 28), [
                (s - 8, half),
                (half + 2, 7),
                (8, 10),
                (10, half),
                (8, s - 10),
                (half + 2, s - 7)
            ])
            pygame.draw.circle(surf, self.color_inner, (half, half), 4)
            # Heavy forward collimator / gun muzzle
            pygame.draw.rect(surf, COLOR_WHITE, (s - 8, half - 2, 8, 4), border_radius=1)

            # World-space telegraph feedback: charging aura & forward aiming indicator
            if self.ai_state == "telegraph":
                charge_alpha = int(160 + 95 * math.sin(self.state_timer * 26.0))
                charge_r = max(2, int(6 * (self.state_timer / SHOOTER_TELEGRAPH_TIME)))
                pygame.draw.circle(surf, (255, 200, 50, max(0, min(255, charge_alpha))), (s - 4, half), charge_r, 2)

        elif self.enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            # Heavy Armored Juggernaut Chassis (58x58)
            half = s // 2
            # Outer Heavy Armor Hull (Reinforced Octagonal Bevel)
            oct_points = [
                (s - 4, half),
                (s - 12, 4),
                (12, 4),
                (4, half - 10),
                (4, half + 10),
                (12, s - 4),
                (s - 12, s - 4)
            ]
            pygame.draw.polygon(surf, (71, 85, 105), oct_points) # Dark Slate Armor
            pygame.draw.polygon(surf, (148, 163, 184), oct_points, 2) # Titanium Trim

            # Reinforced Front Ramming Wedge & Armor Mantlet
            wedge_points = [
                (s - 6, half),
                (s - 18, 12),
                (half - 2, 12),
                (half + 4, half),
                (half - 2, s - 12),
                (s - 18, s - 12)
            ]
            pygame.draw.polygon(surf, (51, 65, 85), wedge_points)
            pygame.draw.polygon(surf, (203, 213, 225), wedge_points, 2)

            # Hydraulic Side Thrusters / Heat Exhausts
            pygame.draw.rect(surf, (30, 41, 59), (8, 8, 8, 12), border_radius=2)
            pygame.draw.rect(surf, (30, 41, 59), (8, s - 20, 8, 12), border_radius=2)

            # Center Warning Reactor Core
            core_col = (245, 158, 11) if self.ai_state != "pressure" else (239, 68, 68)
            core_r = 7 if self.ai_state != "pressure" else int(8 + 2 * math.sin(self.state_timer * 18.0))
            pygame.draw.circle(surf, core_col, (half - 4, half), core_r)
            pygame.draw.circle(surf, COLOR_WHITE, (half - 4, half), 3)

            # Visual aggression telegraph in PRESSURE state
            if self.ai_state == "pressure":
                glow_alpha = int(150 + 90 * math.sin(self.state_timer * 20.0))
                p_surf = pygame.Surface((s + 12, s + 12), pygame.SRCALPHA)
                pygame.draw.circle(p_surf, (245, 158, 11, max(0, min(255, glow_alpha))), ((s + 12) // 2, (s + 12) // 2), (s + 12) // 2, 2)
                surf.blit(p_surf, (-6, -6))

        elif self.enemy_type == TARGET_TYPE_FAST:
            points = [(s, s // 2), (0, 0), (s // 3, s // 2), (0, s)]
            pygame.draw.polygon(surf, self.color_outer, points)
            pygame.draw.circle(surf, self.color_inner, center, 3)

        elif self.enemy_type == TARGET_TYPE_TURRET:
            pygame.draw.rect(surf, self.color_outer, (2, 2, s - 4, s - 4), border_radius=4)
            pygame.draw.circle(surf, self.color_inner, center, s // 3)
            pygame.draw.rect(surf, COLOR_WHITE, (s // 2 - 2, 0, 4, s // 2))

        elif self.enemy_type == TARGET_TYPE_VEHICLE:
            pygame.draw.rect(surf, self.color_outer, (0, 4, s, s - 8), border_radius=6)
            pygame.draw.circle(surf, self.color_inner, center, 5)

        elif self.enemy_type == TARGET_TYPE_CHASER:
            pygame.draw.polygon(surf, self.color_outer, [(s, s // 2), (0, 2), (0, s - 2)])
            pygame.draw.circle(surf, self.color_inner, (s // 3, s // 2), 4)

        elif self.enemy_type == TARGET_TYPE_SWARM:
            pygame.draw.circle(surf, self.color_outer, center, s // 2)
            pygame.draw.circle(surf, self.color_inner, center, s // 4)

        elif self.enemy_type == TARGET_TYPE_SHIELD_DRONE:
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_inner, center, 4)
            # Rotating energy shield arc
            arc_rect = pygame.Rect(0, 0, s, s)
            pygame.draw.arc(surf, COLOR_CYAN, arc_rect, self.shield_angle, self.shield_angle + 2.0, 3)

        elif self.enemy_type == TARGET_TYPE_SNIPER:
            pygame.draw.polygon(surf, self.color_outer, [(s, s // 2), (0, 4), (s // 4, s // 2), (0, s - 4)])
            if self.is_aiming:
                pygame.draw.circle(surf, COLOR_NEON_RED, center, 5)
            else:
                pygame.draw.circle(surf, self.color_inner, center, 3)

        else: # Standard
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_inner, center, s // 4)

        if self.hit_flash_timer > 0:
            surf.fill((255, 255, 255, 160), special_flags=pygame.BLEND_RGBA_ADD)

        # PERF: Only rotate when heading meaningfully changes
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
