"""
================================================================================
                    DRONE HUNTER 2D - CHASER ENEMY AI
================================================================================
Implements aggressive vertical homing Chaser AI.
"""

import math
import pygame

from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class ChaserAI(BaseEnemyAI):
    """Tactical AI for persistent chasing interceptors."""

    def __init__(self, enemy):
        super().__init__(enemy)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        player_pos = context.player_pos

        enemy.pos.x -= enemy.speed * 0.85 * dt
        dy = player_pos[1] - enemy.pos.y
        enemy.pos.y += math.copysign(min(abs(dy), enemy.speed * 0.75 * dt), dy)

        return []
