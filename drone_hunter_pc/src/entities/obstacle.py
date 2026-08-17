"""
================================================================================
                    DRONE HUNTER 2D - ENVIRONMENTAL OBSTACLES
================================================================================
Destructible sector-specific obstacles:
- Asteroid (Deep Space Sector)
- Floating Sea Mine (Ocean Sector)
- Explosive Fuel Barrel (Industrial / Megacity Sector)
"""

import math
import random
import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CRIMSON, COLOR_GOLD, COLOR_WHITE

class EnvironmentalObstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type: str = "barrel", sector_idx: int = 0):
        super().__init__()
        self.obs_type = obs_type
        self.sector_idx = sector_idx
        self.rot_speed = random.uniform(-45.0, 45.0)
        self.angle_deg = 0.0
        self.time_accum = 0.0

        if obs_type == "asteroid":
            self.hp = 70
            self.size = random.randint(40, 60)
            self.speed = random.uniform(90.0, 140.0)
            self.color = (140, 120, 110)
        elif obs_type == "sea_mine":
            self.hp = 40
            self.size = 38
            self.speed = 85.0
            self.color = (180, 50, 50)
        else: # barrel
            self.hp = 30
            self.size = 34
            self.speed = 110.0
            self.color = (239, 68, 68)

        self.max_hp = self.hp
        start_y = random.randint(70, SCREEN_HEIGHT - 70)
        self.pos = pygame.Vector2(SCREEN_WIDTH + self.size + 20, start_y)
        self.base_y = float(start_y)

        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._render_base()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = self.size // 2

    def take_damage(self, dmg: float) -> bool:
        self.hp -= int(dmg)
        return self.hp <= 0

    def update(self, dt: float):
        self.time_accum += dt
        self.angle_deg += self.rot_speed * dt
        self.pos.x -= self.speed * dt
        self.pos.y = self.base_y + math.sin(self.time_accum * 2.0) * 18.0

        self.image = pygame.transform.rotate(self.base_image, self.angle_deg)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

        if self.rect.right < -60:
            self.kill()

    def _render_base(self):
        s = self.size
        c = s // 2
        if self.obs_type == "asteroid":
            # Jagged polygon
            pts = [(c, 2), (s - 4, c // 2), (s - 2, s - 6), (c, s - 2), (4, s - 8), (2, c // 2)]
            pygame.draw.polygon(self.base_image, self.color, pts)
            pygame.draw.polygon(self.base_image, (80, 70, 65), pts, 2)
        elif self.obs_type == "sea_mine":
            pygame.draw.circle(self.base_image, (40, 45, 55), (c, c), c - 4)
            pygame.draw.circle(self.base_image, self.color, (c, c), c - 4, 3)
            for spike_i in range(8):
                ang = spike_i * (math.pi / 4.0)
                sx = c + int(math.cos(ang) * (c - 2))
                sy = c + int(math.sin(ang) * (c - 2))
                pygame.draw.circle(self.base_image, COLOR_WHITE, (sx, sy), 2)
        else: # explosive barrel
            pygame.draw.rect(self.base_image, self.color, (4, 2, s - 8, s - 4), border_radius=4)
            pygame.draw.line(self.base_image, (250, 204, 21), (6, s // 2), (s - 6, s // 2), 3)
            pygame.draw.rect(self.base_image, (20, 20, 30), (4, 2, s - 8, s - 4), 2, border_radius=4)
