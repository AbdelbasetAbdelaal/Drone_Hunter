"""
================================================================================
                    DRONE HUNTER 2D - SCOUT ENEMY AI
================================================================================
Implements high-speed strafing and predictive telegraph diving melee interceptor AI:
approach -> strafe -> telegraph -> dive -> recover.
"""

import math
import random
import pygame

from src.data.game_data import (
    SCOUT_TELEGRAPH_TIME, SCOUT_DIVE_DURATION,
    SCOUT_RECOVER_TIME, SCOUT_STRAFE_DURATION
)
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class ScoutAI(BaseEnemyAI):
    """Tactical AI for high-speed interceptor Scout drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.ai_state: str = "approach"
        self.state_timer: float = 0.0
        self.dive_dir: pygame.Vector2 = pygame.Vector2(0, 0)
        self.dive_target: pygame.Vector2 = pygame.Vector2(0, 0)
        self.strafe_dir: float = random.choice([-1.0, 1.0])
        self.recover_dir: pygame.Vector2 = pygame.Vector2(0, 0)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        self.state_timer += dt
        player_pos = context.player_pos
        player_vel = context.player_vel

        to_player = pygame.Vector2(player_pos[0] - enemy.pos.x, player_pos[1] - enemy.pos.y)
        dist = to_player.length()
        norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

        pred_aim_x = player_pos[0] + player_vel[0] * 0.35
        pred_aim_y = player_pos[1] + player_vel[1] * 0.35

        if self.ai_state == "approach":
            move_dir = norm_to_player
            enemy.pos += move_dir * enemy.speed * dt
            enemy.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
            if dist <= 360.0 or self.state_timer >= 2.4:
                self.ai_state = "strafe"
                self.state_timer = 0.0
                self.strafe_dir = random.choice([-1.0, 1.0])

        elif self.ai_state == "strafe":
            lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
            radial_bias = 0.30 if dist > 300.0 else (-0.25 if dist < 200.0 else 0.0)
            move_vec = (lateral + norm_to_player * radial_bias)
            if move_vec.length() > 0.001:
                move_vec = move_vec.normalize()
            enemy.pos += move_vec * enemy.speed * dt
            enemy.heading_angle = math.degrees(math.atan2(move_vec.y, move_vec.x))

            if self.state_timer >= SCOUT_STRAFE_DURATION:
                self.ai_state = "telegraph"
                self.state_timer = 0.0
                self.dive_target = pygame.Vector2(pred_aim_x, pred_aim_y)
                dive_vec = self.dive_target - enemy.pos
                self.dive_dir = dive_vec.normalize() if dive_vec.length() > 0.001 else norm_to_player

        elif self.ai_state == "telegraph":
            enemy.pos += self.dive_dir * (enemy.speed * 0.12) * dt
            enemy.heading_angle = math.degrees(math.atan2(self.dive_dir.y, self.dive_dir.x))
            if self.state_timer >= SCOUT_TELEGRAPH_TIME:
                self.ai_state = "dive"
                self.state_timer = 0.0

        elif self.ai_state == "dive":
            enemy.pos += self.dive_dir * enemy.dive_speed * dt
            enemy.heading_angle = math.degrees(math.atan2(self.dive_dir.y, self.dive_dir.x))
            if self.state_timer >= SCOUT_DIVE_DURATION:
                self.ai_state = "recover"
                self.state_timer = 0.0
                away_vec = enemy.pos - pygame.Vector2(player_pos[0], player_pos[1])
                self.recover_dir = away_vec.normalize() if away_vec.length() > 0.001 else -self.dive_dir

        elif self.ai_state == "recover":
            enemy.pos += self.recover_dir * (enemy.speed * 0.85) * dt
            enemy.heading_angle = math.degrees(math.atan2(self.recover_dir.y, self.recover_dir.x))
            if self.state_timer >= SCOUT_RECOVER_TIME:
                self.ai_state = "strafe"
                self.state_timer = 0.0
                self.strafe_dir = random.choice([-1.0, 1.0])

        return []
