"""
================================================================================
            DRONE HUNTER 2D - 2D CYBER FACTORY ARENA BACKGROUND
================================================================================
Wraps the dedicated CyberFactoryEnvironment system to provide seamless
world-space factory floor rendering and screen-space menu backdrops.
"""

import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import SECTORS
from src.rendering.environment import (
    CyberFactoryEnvironment, FactoryFloor, PowerReactor, FactoryMachineryUnit, PipeNetwork
)

class CyberFactoryArenaBackground:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.current_sector = 0
        self.env = CyberFactoryEnvironment(world_w, world_h)

        # Expose components for direct access / testing
        self.reactor = self.env.reactor
        self.machinery = self.env.machinery
        self.floor = self.env.floor
        self.pipes = self.env.pipes

    def set_sector(self, sector_idx: int):
        self.current_sector = sector_idx % len(SECTORS)

    def update(self, dt: float):
        self.env.update(dt)

    def draw_menu_backdrop(self, surface: pygame.Surface):
        """Renders clean atmospheric background strictly for screen-space menus."""
        vw, vh = surface.get_size()
        surface.fill((10, 14, 23))
        # Subtle ambient grid
        for gy in range(0, vh, 80):
            pygame.draw.line(surface, (14, 20, 32), (0, gy), (vw, gy), 1)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders 2D Cyber Factory Arena in world space with camera viewport offset."""
        self.env.draw(surface, camera_offset)


ParallaxBackground = CyberFactoryArenaBackground
IndustrialReactor = PowerReactor
SolidMachineryBlock = FactoryMachineryUnit
