"""
================================================================================
                    DRONE HUNTER 2D - TURRET ENEMY AI
================================================================================
Implements heavy stationary/slow flying Turret AI with 3-way spread bullet salvos.
"""

import math
import random
import pygame

from src.entities.bullet import EnemyBullet
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class TurretAI(BaseEnemyAI):
    """Tactical AI for armed turret platforms."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.shoot_timer: float = random.uniform(0.8, 2.2)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        new_bullets = []
        player_pos = context.player_pos
        player_vel = context.player_vel
        bullet_speed = 320.0 + context.sector_idx * 30.0

        pred_aim_x = player_pos[0] + player_vel[0] * 0.35
        pred_aim_y = player_pos[1] + player_vel[1] * 0.35
        pred_aim = (pred_aim_x, pred_aim_y)

        enemy.pos.x -= enemy.speed * dt
        enemy.pos.y = enemy.base_y + math.sin(enemy.time_accum * 2.5) * 22.0

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            cx, cy = enemy.rect.center
            self.shoot_timer = max(0.7, random.uniform(1.3, 1.9) - context.sector_idx * 0.15)
            new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=-12.0))
            new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 90, angle_offset_deg=0.0))
            new_bullets.append(EnemyBullet((cx, cy), pred_aim, speed=bullet_speed + 70, angle_offset_deg=12.0))

        return new_bullets
