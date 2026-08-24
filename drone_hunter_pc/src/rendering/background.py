"""
================================================================================
            DRONE HUNTER 2D - MULTI-SECTOR ARENA BACKGROUND
================================================================================
Wraps SectorEnvironmentManager and CyberFactoryEnvironment systems to provide
seamless world-space 2400x1400 cartoon environment rendering across Sectors 1-5,
dynamic stage variations, and screen-space menu backdrops.
"""

import pygame
from typing import Any
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import SECTORS
from src.rendering.environment import (
    SectorEnvironmentManager, CyberFactoryEnvironment, FactoryFloor, PowerReactor, FactoryMachineryUnit, PipeNetwork
)

class CyberFactoryArenaBackground:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.current_sector = 0
        self.current_stage = 1
        self.env = SectorEnvironmentManager(world_w, world_h)

        # Expose components for direct access / backward compatibility with tests
        self.reactor = self.env.cyber_factory_env.reactor
        self.machinery = self.env.cyber_factory_env.machinery
        self.floor = self.env.cyber_factory_env.floor
        self.pipes = self.env.cyber_factory_env.pipes

    def set_sector(self, sector_idx: int):
        self.current_sector = int(sector_idx) % len(SECTORS)
        self.env.set_sector(self.current_sector)

    def set_stage(self, stage_idx: int):
        self.current_stage = max(1, int(stage_idx))
        self.env.set_stage(self.current_stage)

    def set_mission(self, mission_id: str):
        try:
            sec_num = int(mission_id[1])
            m_num = int(mission_id[4])
            self.set_sector(sec_num - 1)
            self.set_stage(m_num)
        except Exception:
            pass

    def update(self, dt: float):
        self.env.update(dt)

    def draw_menu_backdrop(self, surface: pygame.Surface):
        """Renders clean atmospheric background strictly for screen-space menus."""
        vw, vh = surface.get_size()
        preview = self.env.get_sector_preview(self.current_sector)
        if preview:
            surface.blit(pygame.transform.smoothscale(preview, (vw, vh)), (0, 0))
            overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
            overlay.fill((10, 15, 26, 170))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill((10, 14, 23))
            for gy in range(0, vh, 80):
                pygame.draw.line(surface, (14, 20, 32), (0, gy), (vw, gy), 1)

    def draw(self, surface: pygame.Surface, camera_offset: Any = (0.0, 0.0)):
        """Renders 2D Sector Environment in world space with camera viewport offset."""
        if hasattr(camera_offset, "get_offset"):
            offset = camera_offset.get_offset()
        elif isinstance(camera_offset, (list, tuple)):
            offset = camera_offset
        else:
            offset = (0.0, 0.0)
        self.env.draw(surface, offset)


ParallaxBackground = CyberFactoryArenaBackground
IndustrialReactor = PowerReactor
SolidMachineryBlock = FactoryMachineryUnit

