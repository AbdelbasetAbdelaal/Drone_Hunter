"""
================================================================================
                    DRONE HUNTER 2D - SHIELD DRONE AI
================================================================================
Implements heavy armored Shield Drone AI with active rotating energy barrier.
"""

import math
import pygame

from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class ShieldDroneAI(BaseEnemyAI):
    """Tactical AI for escort shield drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.shield_angle: float = 0.0

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        enemy.pos.x -= enemy.speed * dt
        enemy.pos.y = enemy.base_y + math.cos(enemy.time_accum * 2.0) * 30.0
        self.shield_angle = (self.shield_angle + 4.0 * dt) % 6.28318
        enemy.shield_angle = self.shield_angle
        return []
