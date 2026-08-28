"""
================================================================================
                    DRONE HUNTER 2D - SNIPER ENEMY AI
================================================================================
Implements long-range precision Sniper AI with red laser telegraph and high-speed beam.
"""

import math
import random
import pygame

from src.entities.bullet import EnemySniperBeam
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class SniperAI(BaseEnemyAI):
    """Tactical AI for high-velocity sniper drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.sniper_aim_timer: float = random.uniform(1.5, 3.0)
        self.is_aiming: bool = False
        self.sniper_aim_target: pygame.Vector2 = pygame.Vector2(0, 0)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        new_bullets = []
        player_pos = context.player_pos
        player_vel = context.player_vel
        bullet_speed = 320.0 + context.sector_idx * 30.0

        pred_aim_x = player_pos[0] + player_vel[0] * 0.35
        pred_aim_y = player_pos[1] + player_vel[1] * 0.35
        pred_aim = (pred_aim_x, pred_aim_y)

        enemy.pos.x -= enemy.speed * dt
        self.sniper_aim_timer -= dt
        self.is_aiming = (self.sniper_aim_timer <= 0.8)

        if self.sniper_aim_timer <= 0.0:
            self.sniper_aim_timer = random.uniform(2.2, 3.2)
            self.is_aiming = False
            cx, cy = enemy.rect.center
            new_bullets.append(EnemySniperBeam((cx - 20, cy), pred_aim, speed=bullet_speed + 800))

        if self.is_aiming:
            self.sniper_aim_target = pygame.Vector2(pred_aim)
            enemy.sniper_aim_target = self.sniper_aim_target

        enemy.is_aiming = self.is_aiming
        return new_bullets
