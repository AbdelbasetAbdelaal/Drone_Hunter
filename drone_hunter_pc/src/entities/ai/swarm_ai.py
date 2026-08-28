"""
================================================================================
                    DRONE HUNTER 2D - SWARM ENEMY AI
================================================================================
Implements erratic undulating Swarm AI with opportunistic altitude dives.
"""

import math
import pygame

from src.data.settings import SCREEN_WIDTH
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class SwarmAI(BaseEnemyAI):
    """Tactical AI for swarming lightweight drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.is_diving: bool = False

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        player_pos = context.player_pos

        enemy.pos.x -= enemy.speed * dt
        enemy.pos.y = enemy.base_y + math.sin(enemy.time_accum * 6.0) * 45.0

        if enemy.pos.x < SCREEN_WIDTH * 0.65 and not self.is_diving:
            if abs(enemy.pos.y - player_pos[1]) < 120.0:
                self.is_diving = True

        if self.is_diving:
            dy = player_pos[1] - enemy.pos.y
            enemy.pos.y += (1.0 if dy > 0 else -1.0) * enemy.speed * 0.8 * dt

        enemy.is_diving = self.is_diving
        return []
