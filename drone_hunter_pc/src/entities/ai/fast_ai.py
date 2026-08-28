"""
================================================================================
                    DRONE HUNTER 2D - FAST ENEMY AI
================================================================================
Implements high-velocity sinusoidal flight Fast AI.
"""

import math
import pygame

from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class FastAI(BaseEnemyAI):
    """Tactical AI for rapid flanking drones."""

    def __init__(self, enemy):
        super().__init__(enemy)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        enemy.pos.x -= enemy.speed * dt
        enemy.pos.y = enemy.base_y + math.sin(enemy.time_accum * 4.5) * 35.0
        return []
