"""
================================================================================
                    DRONE HUNTER 2D - ENVIRONMENTAL OBSTACLES
================================================================================
Destructible world obstacles rendered with 2D industrial Cyber Factory styling:
- Industrial Machinery Generator / Transformer Pod
- Heavy Plasma Fuel Canister (Explosive)
- Scrap Armor Slab / Reinforced Metallic Debris
- Asteroid & Sea Mine (Alternative Sectors)
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CRIMSON, COLOR_GOLD, COLOR_CYAN, COLOR_WHITE
)

class EnvironmentalObstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type: str = "machinery", sector_idx: int = 0):
        super().__init__()
        self.obs_type = obs_type
        self.sector_idx = sector_idx
        self.rot_speed = random.uniform(-25.0, 25.0)
        self.angle_deg = 0.0
        self.time_accum = 0.0

        if obs_type == "asteroid":
            self.hp = 70
            self.size = random.randint(46, 64)
            self.speed = random.uniform(90.0, 140.0)
            self.color = (130, 115, 105)
        elif obs_type == "sea_mine":
            self.hp = 40
            self.size = 40
            self.speed = 85.0
            self.color = (180, 50, 50)
        elif obs_type == "plasma_canister" or obs_type == "barrel":
            self.hp = 35
            self.size = 38
            self.speed = 100.0
            self.color = (220, 38, 38)
        else: # machinery_block / transformer
            self.hp = 90
            self.size = random.randint(50, 68)
            self.speed = 70.0
            self.color = (30, 41, 59)

        self.max_hp = self.hp
        # Spawn in world coordinates
        start_y = random.randint(100, WORLD_HEIGHT - 100)
        self.pos = pygame.Vector2(WORLD_WIDTH + self.size + 40, start_y)
        self.base_y = float(start_y)

        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._render_base()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.radius = self.size // 2

    def take_damage(self, dmg: float) -> bool:
        self.hp -= int(dmg)
        return self.hp <= 0

    def update(self, dt: float):
        self.time_accum += dt
        self.angle_deg += self.rot_speed * dt
        self.pos.x -= self.speed * dt
        self.pos.y = self.base_y + math.sin(self.time_accum * 1.5) * 14.0

        self.image = pygame.transform.rotate(self.base_image, self.angle_deg)
        self.rect = self.image.get_rect(center=(int(round(self.pos.x)), int(round(self.pos.y))))

        if self.rect.right < -100:
            self.kill()

    def _render_base(self):
        s = self.size
        c = s // 2

        if self.obs_type in ("machinery", "transformer"):
            # Hexagonal / Chamfered Industrial Machinery Pod
            pts = [
                (c, 2), (s - 6, 8), (s - 2, s - 10),
                (s - 12, s - 2), (8, s - 2), (2, s - 12), (2, 10)
            ]
            pygame.draw.polygon(self.base_image, (25, 33, 48), pts)
            pygame.draw.polygon(self.base_image, (51, 65, 85), pts, 2)
            # Glowing power core
            pygame.draw.circle(self.base_image, (15, 23, 42), (c, c), 10)
            pygame.draw.circle(self.base_image, COLOR_CYAN, (c, c), 6)
            pygame.draw.circle(self.base_image, COLOR_WHITE, (c, c), 2)

        elif self.obs_type in ("plasma_canister", "barrel"):
            # Cylindrical Plasma Fuel Canister with hazard stripe
            pygame.draw.rect(self.base_image, (185, 28, 28), (6, 4, s - 12, s - 8), border_radius=4)
            pygame.draw.rect(self.base_image, (245, 158, 11), (6, c - 4, s - 12, 8))
            pygame.draw.line(self.base_image, (15, 23, 42), (8, c - 4), (s - 8, c + 4), 2)
            pygame.draw.rect(self.base_image, (30, 41, 59), (6, 4, s - 12, s - 8), 2, border_radius=4)

        elif self.obs_type == "sea_mine":
            pygame.draw.circle(self.base_image, (35, 45, 58), (c, c), c - 6)
            pygame.draw.circle(self.base_image, self.color, (c, c), c - 6, 2)
            for spike_i in range(8):
                ang = spike_i * (math.pi / 4.0)
                sx = c + int(math.cos(ang) * (c - 3))
                sy = c + int(math.sin(ang) * (c - 3))
                pygame.draw.circle(self.base_image, COLOR_WHITE, (sx, sy), 2)

        else: # Asteroid / Scrap Rock
            pts = [(c, 3), (s - 6, c // 2), (s - 3, s - 8), (c, s - 3), (4, s - 10), (2, c // 2)]
            pygame.draw.polygon(self.base_image, self.color, pts)
            pygame.draw.polygon(self.base_image, (70, 60, 55), pts, 2)
