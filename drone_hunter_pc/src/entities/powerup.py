"""
================================================================================
                    DRONE HUNTER 2D - POWER-UP PICKUPS
================================================================================
Collectible items floating across the arena granting tactical combat boosts:
Battery, Shield, Overclock, SlowMo, Gold Scrap, Wingman Drone, Weapon Cycling.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_EMERALD, COLOR_SHIELD, COLOR_OVERCLOCK,
    COLOR_SLOWMO, COLOR_COIN, COLOR_CYAN, COLOR_GOLD, COLOR_WHITE
)

class PowerupItem(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], ptype: str = "battery"):
        super().__init__()
        self.p_type = ptype
        self.type = ptype
        self.width = 36
        self.height = 36
        self.pos = pygame.Vector2(pos)
        self.speed = 110.0
        self.time_accum = random.uniform(0.0, 5.0)

        if self.p_type == "shield": self.color = COLOR_SHIELD
        elif self.p_type == "overclock": self.color = COLOR_OVERCLOCK
        elif self.p_type == "slowmo": self.color = COLOR_SLOWMO
        elif self.p_type == "coin": self.color = COLOR_COIN
        elif self.p_type == "wingman": self.color = COLOR_CYAN
        elif self.p_type == "weapon": self.color = COLOR_GOLD
        else: self.color = COLOR_EMERALD

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = 18
        self._render_powerup()

    def update(self, dt: float):
        self.time_accum += dt
        self.pos.x -= self.speed * dt
        self.pos.y += math.sin(self.time_accum * 3.0) * 16.0 * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if self.rect.right < -40:
            self.kill()

    def _render_powerup(self):
        cx, cy = self.width // 2, self.height // 2
        # Diamond / Hexagon container
        pts = [(cx, 2), (self.width - 2, cy), (cx, self.height - 2), (2, cy)]
        pygame.draw.polygon(self.image, (15, 23, 42, 220), pts)
        pygame.draw.polygon(self.image, self.color, pts, 2)
        pygame.draw.circle(self.image, self.color, (cx, cy), 6)
        pygame.draw.circle(self.image, COLOR_WHITE, (cx, cy), 2)
