"""
================================================================================
                    DRONE HUNTER 2D - ENVIRONMENTAL HAZARDS
================================================================================
Dynamic sector hazards:
- LaserGridFence: Moving laser barricade requiring evasion.
- GravityAnomaly: Gravitational vortex applying pulling forces.
"""

import math
import random
import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_NEON_RED, COLOR_PURPLE, COLOR_CYAN, COLOR_WHITE

class LaserGridFence(pygame.sprite.Sprite):
    def __init__(self, start_x: float = SCREEN_WIDTH + 40):
        super().__init__()
        self.width = 16
        self.gap_h = 160
        self.gap_y = random.randint(80, SCREEN_HEIGHT - 80 - self.gap_h)
        self.pos_x = start_x
        self.speed = 150.0

        self.image = pygame.Surface((self.width, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.pos_x, 0))
        self._render_grid()

    def update(self, dt: float):
        self.pos_x -= self.speed * dt
        self.rect.x = round(self.pos_x)
        if self.rect.right < -40:
            self.kill()

    def _render_grid():
        pass # Rendered in draw or surface

    def _render_grid(self):
        # Top barrier segment
        if self.gap_y > 0:
            pygame.draw.rect(self.image, (255, 30, 60, 200), (0, 0, self.width, self.gap_y))
            pygame.draw.rect(self.image, COLOR_WHITE, (4, 0, 8, self.gap_y))
        
        # Bottom barrier segment
        bot_y = self.gap_y + self.gap_h
        if bot_y < SCREEN_HEIGHT:
            pygame.draw.rect(self.image, (255, 30, 60, 200), (0, bot_y, self.width, SCREEN_HEIGHT - bot_y))
            pygame.draw.rect(self.image, COLOR_WHITE, (4, bot_y, 8, SCREEN_HEIGHT - bot_y))


class GravityAnomaly(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 120.0
        self.pull_force = 220.0
        self.pos = pygame.Vector2(random.randint(SCREEN_WIDTH // 3, SCREEN_WIDTH - 150), random.randint(120, SCREEN_HEIGHT - 120))
        self.time_accum = 0.0
        self.lifetime = 12.0

        self.image = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self._render_vortex()

    def update(self, dt: float, player=None):
        self.time_accum += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        if player and player.alive and not player.is_cloaked:
            to_center = self.pos - player.pos
            dist = to_center.length()
            if 0 < dist < self.radius * 2.2:
                force = to_center.normalize() * (self.pull_force * (1.0 - (dist / (self.radius * 2.2))))
                player.velocity += force * dt

        self._render_vortex()

    def _render_vortex(self):
        self.image.fill((0, 0, 0, 0))
        c = int(self.radius)
        # Multi-ring pulsating vortex
        alpha1 = int(70 + 40 * math.sin(self.time_accum * 4.0))
        alpha2 = int(90 + 50 * math.cos(self.time_accum * 5.0))
        
        pygame.draw.circle(self.image, (168, 85, 247, alpha1), (c, c), int(self.radius))
        pygame.draw.circle(self.image, (14, 165, 233, alpha2), (c, c), int(self.radius * 0.65), 3)
        pygame.draw.circle(self.image, COLOR_WHITE, (c, c), 8)
