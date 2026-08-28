"""
================================================================================
                    DRONE HUNTER 2D - HEAVY ENEMY AI
================================================================================
Implements heavy armored brawler AI with continuous pressure and recovery:
approach -> pressure -> recover.
"""

import math
import random
import pygame

from src.data.game_data import HEAVY_PRESSURE_DISTANCE
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class HeavyAI(BaseEnemyAI):
    """Tactical AI for heavy armored brawler drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.ai_state: str = "approach"
        self.state_timer: float = 0.0
        self.strafe_dir: float = random.choice([-1.0, 1.0])
        self.recover_dir: pygame.Vector2 = pygame.Vector2(0, 0)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        self.state_timer += dt
        player_pos = context.player_pos

        to_player = pygame.Vector2(player_pos[0] - enemy.pos.x, player_pos[1] - enemy.pos.y)
        dist = to_player.length()
        norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

        if self.ai_state == "approach":
            # Advance steadily and predictably toward player with heavy momentum
            move_dir = norm_to_player
            enemy.pos += move_dir * enemy.speed * dt
            enemy.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
            if dist <= HEAVY_PRESSURE_DISTANCE:
                self.ai_state = "pressure"
                self.state_timer = 0.0

        elif self.ai_state == "pressure":
            # Maintain relentless forward space pressure toward player
            move_dir = norm_to_player
            enemy.pos += move_dir * (enemy.speed * 1.15) * dt
            enemy.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))

            # After sustained pressure window or if player flees far
            if self.state_timer >= 2.5 or dist > HEAVY_PRESSURE_DISTANCE + 120.0:
                self.ai_state = "recover"
                self.state_timer = 0.0
                lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                self.recover_dir = (norm_to_player * 0.4 + lateral * 0.6).normalize()

        elif self.ai_state == "recover":
            # Brief stabilization / hydraulic vent venting period before re-engaging
            enemy.pos += self.recover_dir * (enemy.speed * 0.65) * dt
            enemy.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            if self.state_timer >= 0.85:
                self.ai_state = "approach"
                self.state_timer = 0.0
                self.strafe_dir = random.choice([-1.0, 1.0])

        return []
