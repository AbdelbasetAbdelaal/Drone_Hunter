"""
================================================================================
                    DRONE HUNTER 2D - BOSS DREADNOUGHTS
================================================================================
Multi-phase boss encounters with distinct attack patterns, phase transitions,
invisibility cloaks, EMP shockwave wave jammers, and bullet hell salvos.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_MAGENTA, COLOR_PURPLE, COLOR_OVERCLOCK, COLOR_WHITE, COLOR_NEON_RED
)
from src.data.game_data import (
    TARGET_TYPE_BOSS, TARGET_TYPE_STEALTH_MIRAGE, TARGET_TYPE_EMP_DISRUPTER,
    TARGET_TYPE_TITAN_MECH, ENEMY_BULLET_SPEED
)
from src.entities.bullet import EnemyBullet
from src.entities.enemy import Enemy

class Boss(Enemy):
    """Base class for all Boss Dreadnoughts."""
    def __init__(self, boss_type: str, level: int = 1, sector_idx: int = 0,
                 hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__(enemy_type=boss_type, level=level, sector_idx=sector_idx,
                         hp_multiplier=hp_multiplier, speed_multiplier=speed_multiplier)
        self.is_boss = True
        self.rage_phase = False
        self.pos = pygame.Vector2(SCREEN_WIDTH + 140, SCREEN_HEIGHT // 2)
        self.target_anchor_x = SCREEN_WIDTH - 220.0
        self.rect = self.image.get_rect(center=self.pos)


class SkyDreadnoughtBoss(Boss):
    """Sector 1 Boss: Sky Fortress Dreadnought with 360-degree radial spiral salvos."""
    def __init__(self, level: int = 1, sector_idx: int = 0, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__(TARGET_TYPE_BOSS, level, sector_idx, hp_multiplier, speed_multiplier)
        sec_mult = 1.0 + (sector_idx * 0.35)
        self.hp = int((120 + (level - 1) * 50) * sec_mult * hp_multiplier)
        self.max_hp = self.hp
        self.points = 700 + sector_idx * 200
        self.size = 120
        self.speed = (75.0 + sector_idx * 15.0) * speed_multiplier
        self.color_outer = (225, 29, 72)
        self.color_inner = (250, 204, 21)
        self._render_sprite()

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        self.time_accum += dt
        new_bullets = []

        # Smooth entry into arena
        if self.pos.x > self.target_anchor_x:
            self.pos.x -= 120.0 * dt
        else:
            # Figure-eight hovering pattern
            self.pos.y = (SCREEN_HEIGHT // 2) + math.sin(self.time_accum * 1.8) * 180.0
            self.pos.x = self.target_anchor_x + math.cos(self.time_accum * 0.9) * 40.0

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Check Rage Phase
        if self.hp <= self.max_hp * 0.40 and not self.rage_phase:
            self.rage_phase = True
            self.color_outer = COLOR_NEON_RED
            self._render_sprite()

        # Shooting Salvors
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            cx, cy = self.rect.center
            bullet_speed = ENEMY_BULLET_SPEED + self.sector_idx * 50.0

            if self.rage_phase:
                self.shoot_timer = 1.1
                # 360-Degree Radial Spiral
                for ring_i in range(12):
                    ang_deg = ring_i * (360.0 / 12.0) + (self.time_accum * 45.0)
                    rad = math.radians(ang_deg)
                    tx = cx + math.cos(rad) * 300.0
                    ty = cy + math.sin(rad) * 300.0
                    new_bullets.append(EnemyBullet((cx, cy), (tx, ty), speed=bullet_speed + 80))
            else:
                self.shoot_timer = 1.6
                for offset in [-24.0, -12.0, 0.0, 12.0, 24.0]:
                    new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=bullet_speed + 60, angle_offset_deg=offset))

        return new_bullets


class StealthMirageBoss(Boss):
    """Sector 2 Boss: Tactical Invisibility & Holographic Clones."""
    def __init__(self, level: int = 1, sector_idx: int = 1, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__(TARGET_TYPE_STEALTH_MIRAGE, level, sector_idx, hp_multiplier, speed_multiplier)
        sec_mult = 1.0 + (sector_idx * 0.35)
        self.hp = int((140 + (level - 1) * 55) * sec_mult * hp_multiplier)
        self.max_hp = self.hp
        self.points = 900 + sector_idx * 250
        self.size = 110
        self.speed = (95.0 + sector_idx * 20.0) * speed_multiplier
        self.color_outer = COLOR_PURPLE
        self.color_inner = COLOR_CYAN
        
        self.is_cloaked = False
        self.cloak_timer = 0.0
        self.cloak_cooldown = 4.0
        self._render_sprite()

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        self.time_accum += dt
        new_bullets = []

        if self.pos.x > self.target_anchor_x:
            self.pos.x -= 140.0 * dt
        else:
            self.pos.y = (SCREEN_HEIGHT // 2) + math.sin(self.time_accum * 2.4) * 200.0

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Cloak State Cycling
        self.cloak_cooldown -= dt
        if self.cloak_cooldown <= 0 and not self.is_cloaked:
            self.is_cloaked = True
            self.cloak_timer = 3.0
            self.cloak_cooldown = 7.0
            self._render_sprite()

        if self.is_cloaked:
            self.cloak_timer -= dt
            if self.cloak_timer <= 0:
                self.is_cloaked = False
                self.pos.y = random.randint(100, SCREEN_HEIGHT - 100)
                self._render_sprite()

        # Shooting
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and not self.is_cloaked:
            self.shoot_timer = 1.3
            cx, cy = self.rect.center
            bullet_speed = ENEMY_BULLET_SPEED + 80.0
            for offset in [-16.0, -8.0, 8.0, 16.0]:
                new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=bullet_speed, angle_offset_deg=offset))

        return new_bullets


class EMPDisrupterBoss(Boss):
    """Sector 3 Boss: EMP Shockwave Disrupter that emits expanding wave jamming the player."""
    def __init__(self, level: int = 1, sector_idx: int = 2, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__(TARGET_TYPE_EMP_DISRUPTER, level, sector_idx, hp_multiplier, speed_multiplier)
        sec_mult = 1.0 + (sector_idx * 0.35)
        self.hp = int((170 + (level - 1) * 65) * sec_mult * hp_multiplier)
        self.max_hp = self.hp
        self.points = 1100 + sector_idx * 300
        self.size = 130
        self.speed = 65.0 * speed_multiplier
        self.color_outer = (99, 102, 241)
        self.color_inner = COLOR_GOLD
        
        self.emp_pulse_timer = 4.0
        self.emp_wave_radius = 0.0
        self.is_emp_expanding = False
        self._render_sprite()

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        self.time_accum += dt
        new_bullets = []

        if self.pos.x > self.target_anchor_x:
            self.pos.x -= 100.0 * dt
        else:
            self.pos.y = (SCREEN_HEIGHT // 2) + math.sin(self.time_accum * 1.4) * 150.0

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # EMP Expanding Wave Logic (Fixes Bug 4!)
        self.emp_pulse_timer -= dt
        if self.emp_pulse_timer <= 0.0:
            self.emp_pulse_timer = 6.0
            self.is_emp_expanding = True
            self.emp_wave_radius = 30.0

        if self.is_emp_expanding:
            self.emp_wave_radius += 280.0 * dt
            if player_obj and player_obj.alive:
                dist = math.hypot(player_obj.pos.x - self.pos.x, player_obj.pos.y - self.pos.y)
                if dist <= self.emp_wave_radius or abs(dist - self.emp_wave_radius) < 50.0:
                    player_obj.trigger_emp_jammed(3.0)

            if self.emp_wave_radius >= 750.0:
                self.is_emp_expanding = False

        # Shooting
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = 1.7
            cx, cy = self.rect.center
            bullet_speed = ENEMY_BULLET_SPEED + 60.0
            for offset in [-30.0, -15.0, 0.0, 15.0, 30.0]:
                new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=bullet_speed, angle_offset_deg=offset))

        return new_bullets


class ColossusTitanMechBoss(Boss):
    """Sector 5 Grand Final Boss: 3-Phase Overclock Berserk Titan Mech."""
    def __init__(self, level: int = 1, sector_idx: int = 4, hp_multiplier: float = 1.0, speed_multiplier: float = 1.0):
        super().__init__(TARGET_TYPE_TITAN_MECH, level, sector_idx, hp_multiplier, speed_multiplier)
        sec_mult = 1.0 + (sector_idx * 0.40)
        self.hp = int((260 + (level - 1) * 90) * sec_mult * hp_multiplier)
        self.max_hp = self.hp
        self.points = 2000
        self.size = 150
        self.speed = 55.0 * speed_multiplier
        self.color_outer = (190, 18, 60)
        self.color_inner = COLOR_OVERCLOCK
        self.boss_phase = 1
        self._render_sprite()

    def update(self, dt: float, player_pos: tuple[float, float] = (200, 360),
               player_vel: tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list[EnemyBullet]:
        self.time_accum += dt
        new_bullets = []

        if self.pos.x > self.target_anchor_x:
            self.pos.x -= 90.0 * dt
        else:
            self.pos.y = (SCREEN_HEIGHT // 2) + math.sin(self.time_accum * 1.2) * 160.0

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Dynamic Phase Transitions based on remaining HP
        hp_pct = self.hp / self.max_hp
        if hp_pct <= 0.35 and self.boss_phase != 3:
            self.boss_phase = 3
            self.color_outer = COLOR_NEON_RED
            self._render_sprite()
        elif hp_pct <= 0.70 and self.boss_phase == 1:
            self.boss_phase = 2
            self.color_outer = COLOR_OVERCLOCK
            self._render_sprite()

        # Firing Logic
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            cx, cy = self.rect.center
            bullet_speed = ENEMY_BULLET_SPEED + 90.0

            if self.boss_phase == 3: # Phase 3: OVERCLOCK BERSERK 16-bullet 360 ring
                self.shoot_timer = 0.75
                for ring_i in range(16):
                    ang_deg = ring_i * (360.0 / 16.0) + (self.time_accum * 30.0)
                    rad = math.radians(ang_deg)
                    tx = cx + math.cos(rad) * 400.0
                    ty = cy + math.sin(rad) * 400.0
                    new_bullets.append(EnemyBullet((cx, cy), (tx, ty), speed=bullet_speed + 120))

            elif self.boss_phase == 2: # Phase 2: Rapid quad salvos
                self.shoot_timer = 1.1
                for offset in [-24.0, -8.0, 8.0, 24.0]:
                    new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=bullet_speed + 70, angle_offset_deg=offset))

            else: # Phase 1: Heavy triple barrage
                self.shoot_timer = 1.6
                for offset in [-18.0, 0.0, 18.0]:
                    new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=bullet_speed, angle_offset_deg=offset))

        return new_bullets
