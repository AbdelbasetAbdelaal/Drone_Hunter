"""
================================================================================
                    DRONE HUNTER 2D - SHOOTER ENEMY AI
================================================================================
Implements positional pressure drone AI with range keeping, deliberate aim,
telegraph charging, and single-shot projectile firing:
approach -> position -> aim -> telegraph -> fire -> reposition.
"""

import math
import random
import pygame

from src.data.game_data import (
    SHOOTER_PREFERRED_DISTANCE, SHOOTER_FIRE_COOLDOWN,
    SHOOTER_TELEGRAPH_TIME, SHOOTER_REPOSITION_TIME
)
from src.entities.bullet import EnemyBullet
from src.entities.ai.enemy_ai import BaseEnemyAI, EnemyAIContext


class ShooterAI(BaseEnemyAI):
    """Tactical AI for long-range positional pressure Shooter drones."""

    def __init__(self, enemy):
        super().__init__(enemy)
        self.ai_state: str = "approach"
        self.state_timer: float = 0.0
        self.fire_timer: float = 0.0
        self.strafe_dir: float = random.choice([-1.0, 1.0])
        self.reposition_dir: pygame.Vector2 = pygame.Vector2(0, 0)
        self.aim_target: pygame.Vector2 = pygame.Vector2(0, 0)

    def update(self, dt: float, enemy, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        self.state_timer += dt
        self.fire_timer += dt
        new_bullets = []
        player_pos = context.player_pos
        player_vel = context.player_vel

        to_player = pygame.Vector2(player_pos[0] - enemy.pos.x, player_pos[1] - enemy.pos.y)
        dist = to_player.length()
        norm_to_player = to_player / dist if dist > 0.001 else pygame.Vector2(1, 0)

        if self.ai_state == "approach":
            # Approach until inside preferred combat distance (~420-520px)
            move_dir = norm_to_player
            enemy.pos += move_dir * enemy.speed * dt
            enemy.heading_angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
            if dist <= SHOOTER_PREFERRED_DISTANCE + 50.0:
                self.ai_state = "position"
                self.state_timer = 0.0

        elif self.ai_state == "position":
            # Maintain preferred distance band (300-550px)
            if dist > 550.0:
                move_dir = norm_to_player
            elif dist < 300.0:
                move_dir = -norm_to_player
            else:
                # Gentle lateral orbit within tolerance band
                lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                move_dir = lateral

            if move_dir.length_squared() > 0.001:
                move_dir = move_dir.normalize()
            enemy.pos += move_dir * (enemy.speed * 0.75) * dt
            enemy.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            # When fire cooldown has elapsed, transition to AIM
            if self.fire_timer >= SHOOTER_FIRE_COOLDOWN:
                self.ai_state = "aim"
                self.state_timer = 0.0

        elif self.ai_state == "aim":
            # Calculate limited predictive target aim vector (0.25s lead)
            pred_x = player_pos[0] + player_vel[0] * 0.25
            pred_y = player_pos[1] + player_vel[1] * 0.25
            self.aim_target = pygame.Vector2(pred_x, pred_y)
            aim_vec = self.aim_target - enemy.pos
            if aim_vec.length() > 0.001:
                enemy.heading_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x))
            self.ai_state = "telegraph"
            self.state_timer = 0.0

        elif self.ai_state == "telegraph":
            # Steady hover with subtle world-space charging glow
            aim_vec = self.aim_target - enemy.pos
            if aim_vec.length() > 0.001:
                enemy.heading_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x))
            if self.state_timer >= SHOOTER_TELEGRAPH_TIME:
                ang_rad = math.radians(enemy.heading_angle)
                fwd_x = math.cos(ang_rad)
                fwd_y = math.sin(ang_rad)
                muz_x = enemy.pos.x + fwd_x * 34.0
                muz_y = enemy.pos.y + fwd_y * 34.0
                bullet = EnemyBullet(
                    (muz_x, muz_y), (self.aim_target.x, self.aim_target.y),
                    speed=enemy.projectile_speed, damage=enemy.projectile_damage,
                    weapon_id="enemy_laser"
                )
                new_bullets.append(bullet)
                self.fire_timer = 0.0
                self.ai_state = "reposition"
                self.state_timer = 0.0

                # Pick a tactical reposition direction
                if dist < 350.0:
                    self.reposition_dir = -norm_to_player
                else:
                    self.strafe_dir = -self.strafe_dir  # flip orbit direction
                    lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                    self.reposition_dir = lateral.normalize()

        elif self.ai_state == "fire":
            # Fire exactly ONE deliberate hostile projectile from muzzle
            ang_rad = math.radians(enemy.heading_angle)
            fwd_x = math.cos(ang_rad)
            fwd_y = math.sin(ang_rad)
            muz_x = enemy.pos.x + fwd_x * 34.0
            muz_y = enemy.pos.y + fwd_y * 34.0
            bullet = EnemyBullet(
                (muz_x, muz_y), (self.aim_target.x, self.aim_target.y),
                speed=enemy.projectile_speed, damage=enemy.projectile_damage,
                weapon_id="enemy_laser"
            )
            new_bullets.append(bullet)
            self.fire_timer = 0.0
            self.ai_state = "reposition"
            self.state_timer = 0.0

            # Pick a tactical reposition direction
            if dist < 350.0:
                self.reposition_dir = -norm_to_player
            else:
                self.strafe_dir = -self.strafe_dir  # flip orbit direction
                lateral = pygame.Vector2(-norm_to_player.y, norm_to_player.x) * self.strafe_dir
                self.reposition_dir = lateral.normalize()

        elif self.ai_state == "reposition":
            # Evasive repositioning
            enemy.pos += self.reposition_dir * enemy.speed * dt
            enemy.heading_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            if self.state_timer >= SHOOTER_REPOSITION_TIME:
                self.ai_state = "position"
                self.state_timer = 0.0

        return new_bullets
