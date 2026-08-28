"""
================================================================================
                    DRONE HUNTER 2D - STANDARD / VEHICLE ENEMY AI
================================================================================
Implements baseline sinusoidal wave patrol AI for Standard and Vehicle enemy archetypes.
"""

import math
import pygame

from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class StandardAI(BaseEnemyAI):
    """Tactical AI for baseline combat targets and ground vehicles."""

    def __init__(self, enemy):
        super().__init__(enemy)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        enemy.pos.x -= enemy.speed * dt
        enemy.pos.y = enemy.base_y + math.sin(enemy.time_accum * 2.5) * 22.0
        return []
