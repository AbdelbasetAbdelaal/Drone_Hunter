"""
================================================================================
                    DRONE HUNTER 2D - WINGMAN ESCORT SYSTEM
================================================================================
Autonomous escort mini-drones providing supportive auto-fire and formation flight.
"""

import random
import pygame
from src.data.settings import COLOR_CYAN, COLOR_WHITE
from src.entities.bullet import Bullet


class WingmanDrone:
    """Autonomous escort mini-drone providing supportive auto-fire."""
    def __init__(self, offset_x: float, offset_y: float):
        self.offset = pygame.Vector2(offset_x, offset_y)
        self.pos = pygame.Vector2(0, 0)
        self.shoot_timer = random.uniform(0.1, 0.4)
        self.angle_deg = 0.0

    def update(self, dt: float, parent_pos: pygame.Vector2, targets_group=None) -> list[Bullet]:
        self.pos = parent_pos + self.offset
        self.shoot_timer -= dt
        bullets = []

        if self.shoot_timer <= 0 and targets_group and len(targets_group) > 0:
            self.shoot_timer = 0.45
            nearest = min(targets_group, key=lambda t: (t.rect.centerx - self.pos.x)**2 + (t.rect.centery - self.pos.y)**2)
            tx, ty = nearest.rect.center
            bullets.append(Bullet((self.pos.x, self.pos.y), (tx, ty), speed=850.0, damage=16, color=COLOR_CYAN, owner="wingman", weapon_id="wingman_pulse"))

        return bullets

    def draw(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        ox, oy = camera_offset
        px, py = int(round(self.pos.x - ox)), int(round(self.pos.y - oy))
        pygame.draw.circle(canvas, (15, 23, 42), (px, py), 10)
        pygame.draw.circle(canvas, COLOR_CYAN, (px, py), 10, 2)
        pygame.draw.circle(canvas, COLOR_WHITE, (px, py), 4)


class WingmanManager:
    """Manages escort wingman formation, updates, and rendering."""
    def __init__(self):
        self.wingmen: list[WingmanDrone] = []

    def clear(self):
        self.wingmen.clear()

    def spawn_wingman(self):
        """Spawns an escort wingman drone up to maximum formation of 2."""
        if len(self.wingmen) == 0:
            self.wingmen.append(WingmanDrone(-42, -40))
        elif len(self.wingmen) == 1:
            self.wingmen.append(WingmanDrone(-42, 40))

    def set_formation(self, count: int):
        """Sets the formation count directly from upgrades."""
        self.wingmen.clear()
        if count >= 1:
            self.wingmen.append(WingmanDrone(-42, -40))
        if count >= 2:
            self.wingmen.append(WingmanDrone(-42, 40))

    def update(self, dt: float, parent_pos: pygame.Vector2, targets_group=None) -> list[Bullet]:
        wingman_bullets = []
        for wm in self.wingmen:
            wm_b = wm.update(dt, parent_pos, targets_group=targets_group)
            wingman_bullets.extend(wm_b)
        return wingman_bullets

    def draw(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        for wm in self.wingmen:
            wm.draw(canvas, camera_offset)
