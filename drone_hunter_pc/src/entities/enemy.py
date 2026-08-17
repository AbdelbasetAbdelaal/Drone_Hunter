"""
================================================================================
                    DRONE HUNTER 2D - ENEMY & TARGET ENTITIES
================================================================================
Unified 2D hostile enemy sprites, behaviors, and spawner systems.
Includes: Standard, Fast, Armored, Shooter, Turret, Vehicle, Chaser, Swarm,
Shield Drone, and Sniper.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD, COLOR_NEON_RED, COLOR_WHITE,
    COLOR_TARGET, COLOR_TESLA
)
from src.data.game_data import (
    TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER,
    TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE, TARGET_TYPE_CHASER, TARGET_TYPE_SWARM,
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER, TARGET_SPEED, ENEMY_BULLET_SPEED
)
from src.entities.bullet import EnemyBullet, EnemySniperBeam

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type: str = TARGET_TYPE_STANDARD, speed_bonus: float = 0.0,
                 level: int = 1, sector_idx: int = 0, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.level = level
        self.sector_idx = sector_idx
        self.is_boss = False
        self.time_accum = random.uniform(0.0, 10.0)

        # Combat & Timers
        self.shoot_timer = random.uniform(0.4, 1.6)
        self.shield_angle = 0.0
        self.is_aiming = False
        self.sniper_aim_timer = 1.2
        self.is_diving = False

        sec_mult = 1.0 + (sector_idx * 0.30)

        if enemy_type == TARGET_TYPE_FAST:
            base_hp = int(18 * sec_mult * hp_multiplier)
            self.points = 150
            size = 32
            base_speed = (TARGET_SPEED * 1.55 + speed_bonus) * speed_multiplier
            self.color_outer = COLOR_GOLD
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_ARMORED:
            base_hp = int(60 * sec_mult * hp_multiplier)
            self.points = 250
            size = 46
            base_speed = (TARGET_SPEED * 0.75 + speed_bonus) * speed_multiplier
            self.color_outer = (120, 140, 170)
            self.color_inner = COLOR_CYAN

        elif enemy_type == TARGET_TYPE_SHOOTER:
            base_hp = int(28 * sec_mult * hp_multiplier)
            self.points = 200
            size = 38
            base_speed = (TARGET_SPEED * 0.90 + speed_bonus) * speed_multiplier
            self.color_outer = COLOR_CRIMSON
            self.color_inner = COLOR_GOLD

        elif enemy_type == TARGET_TYPE_TURRET:
            base_hp = int(50 * sec_mult * hp_multiplier)
            self.points = 300
            size = 44
            base_speed = (TARGET_SPEED * 0.40 + speed_bonus) * speed_multiplier
            self.color_outer = (180, 40, 40)
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_VEHICLE:
            base_hp = int(45 * sec_mult * hp_multiplier)
            self.points = 220
            size = 42
            base_speed = (TARGET_SPEED * 0.80 + speed_bonus) * speed_multiplier
            self.color_outer = (130, 90, 40)
            self.color_inner = COLOR_GOLD

        elif enemy_type == TARGET_TYPE_CHASER:
            base_hp = int(24 * sec_mult * hp_multiplier)
            self.points = 180
            size = 34
            base_speed = (TARGET_SPEED * 1.25 + speed_bonus) * speed_multiplier
            self.color_outer = (236, 72, 153)
            self.color_inner = COLOR_WHITE

        elif enemy_type == TARGET_TYPE_SWARM:
            base_hp = int(12 * sec_mult * hp_multiplier)
            self.points = 100
            size = 24
            base_speed = (TARGET_SPEED * 1.80 + speed_bonus) * speed_multiplier
            self.color_outer = (250, 204, 21)
            self.color_inner = (239, 68, 68)

        elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
            base_hp = int(40 * sec_mult * hp_multiplier)
            self.points = 260
            size = 40
            base_speed = (TARGET_SPEED * 0.85 + speed_bonus) * speed_multiplier
            self.color_outer = COLOR_SHIELD
            self.color_inner = (99, 102, 241)

        elif enemy_type == TARGET_TYPE_SNIPER:
            base_hp = int(32 * sec_mult * hp_multiplier)
            self.points = 280
            size = 36
            base_speed = (TARGET_SPEED * 0.70 + speed_bonus) * speed_multiplier
            self.color_outer = COLOR_NEON_RED
            self.color_inner = (15, 23, 42)

        else: # TARGET_TYPE_STANDARD
            base_hp = int(20 * sec_mult * hp_multiplier)
            self.points = 100
            size = 34
            base_speed = (TARGET_SPEED + speed_bonus) * speed_multiplier
            self.color_outer = COLOR_TARGET
            self.color_inner = (255, 200, 200)

        self.hp = max(1, base_hp)
        self.max_hp = self.hp
        self.size = size
        self.speed = base_speed
        self.alive = True

        # Position Initialization
        start_y = random.randint(60, SCREEN_HEIGHT - 60)
        self.pos = pygame.Vector2(SCREEN_WIDTH + size + 20, start_y)
        self.base_y = float(start_y)
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = size // 2
        
        self._render_sprite()

    # --- Unified Metadata Properties (Fixes Bug 5) ---
    @property
    def type(self) -> str:
        return self.enemy_type

    @property
    def target_type(self) -> str:
        return self.enemy_type

    @property
    def score_value(self) -> int:
        return self.points

    @property
    def color(self) -> tuple[int, int, int]:
        return self.color_outer

    def take_damage(self, dmg: float, source: str = "bullet") -> bool:
        """Applies damage to enemy and returns True if destroyed."""
        self.hp -= int(dmg)
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.kill()
            return True
        return False

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        self.time_accum += dt
        new_bullets = []

        pred_aim_x = player_pos[0] + player_vel[0] * 0.35
        pred_aim_y = player_pos[1] + player_vel[1] * 0.35
        pred_aim = (pred_aim_x, pred_aim_y)

        bullet_speed = ENEMY_BULLET_SPEED + self.sector_idx * 40.0

        # --- Movement Patterns ---
        if self.enemy_type == TARGET_TYPE_SWARM:
            self.pos.x -= self.speed * dt
            # Sine wave oscillation
            self.pos.y = self.base_y + math.sin(self.time_accum * 6.0) * 45.0
            # Dive towards player when close
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

        else: # Standard, Armored, Shooter, Turret, Vehicle
            self.pos.x -= self.speed * dt
            self.pos.y = self.base_y + math.sin(self.time_accum * 2.5) * 22.0

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # --- Shooting Behaviors ---
        if self.enemy_type in (TARGET_TYPE_SHOOTER, TARGET_TYPE_TURRET):
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                cx, cy = self.rect.center
                if self.enemy_type == TARGET_TYPE_TURRET:
                    self.shoot_timer = max(0.7, random.uniform(1.3, 1.9) - self.sector_idx * 0.15)
                    new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=-12.0))
                    new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 90, angle_offset_deg=0.0))
                    new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=12.0))
                elif self.enemy_type == TARGET_TYPE_SHOOTER:
                    self.shoot_timer = max(0.8, random.uniform(1.6, 2.3) - self.sector_idx * 0.20)
                    new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed, angle_offset_deg=-7.0))
                    new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed, angle_offset_deg=7.0))

        # Boundary Cleanup
        if self.rect.right < -80:
            self.kill()

        return new_bullets

    def _render_sprite(self):
        s = self.size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        center = (s // 2, s // 2)

        if self.enemy_type == TARGET_TYPE_SWARM:
            # Triangular dart
            pts = [(s, s // 2), (0, 2), (6, s // 2), (0, s - 2)]
            pygame.draw.polygon(surf, self.color_outer, pts)
            pygame.draw.polygon(surf, self.color_inner, [(s - 4, s // 2), (4, 6), (8, s // 2), (4, s - 6)])

        elif self.enemy_type == TARGET_TYPE_SHIELD_DRONE:
            # Hexagonal drone with orbiting shield nodes
            pygame.draw.circle(surf, (15, 23, 42), center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2, 2)
            pygame.draw.circle(surf, self.color_inner, center, 6)
            for i in range(3):
                ang = self.shield_angle + (i * 2.0944)
                nx = center[0] + int(math.cos(ang) * (s // 2 - 4))
                ny = center[1] + int(math.sin(ang) * (s // 2 - 4))
                pygame.draw.circle(surf, COLOR_WHITE, (nx, ny), 3)

        elif self.enemy_type == TARGET_TYPE_SNIPER:
            # Sleek railgun chassis with long barrel
            pygame.draw.rect(surf, (20, 25, 35), (8, 6, s - 16, s - 12), border_radius=4)
            pygame.draw.rect(surf, self.color_outer, (8, 6, s - 16, s - 12), 2, border_radius=4)
            pygame.draw.line(surf, COLOR_NEON_RED, (0, s // 2), (12, s // 2), 3)
            pygame.draw.circle(surf, COLOR_NEON_RED if self.is_aiming else (80, 20, 20), (s // 2 + 2, s // 2), 4)

        elif self.enemy_type == TARGET_TYPE_ARMORED:
            # Heavy faceted diamond
            pts = [(s // 2, 2), (s - 4, s // 2), (s // 2, s - 2), (4, s // 2)]
            pygame.draw.polygon(surf, self.color_outer, pts)
            pygame.draw.polygon(surf, (25, 35, 50), [(s // 2, 8), (s - 10, s // 2), (s // 2, s - 8), (10, s // 2)])
            pygame.draw.polygon(surf, self.color_inner, pts, 2)

        elif self.enemy_type == TARGET_TYPE_TURRET:
            # Octagon fortress turret
            pygame.draw.circle(surf, (20, 20, 30), center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2, 3)
            pygame.draw.line(surf, self.color_outer, (0, s // 2), (s // 2, s // 2), 4)
            pygame.draw.circle(surf, self.color_inner, center, 5)

        else: # Standard, Fast, Shooter, Vehicle
            pygame.draw.circle(surf, (15, 23, 42), center, s // 2 - 2)
            pygame.draw.circle(surf, self.color_outer, center, s // 2 - 2, 2)
            pygame.draw.circle(surf, self.color_inner, center, max(3, s // 4))

        self.image = surf
