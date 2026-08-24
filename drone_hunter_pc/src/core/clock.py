"""
================================================================================
                    DRONE HUNTER 2D - GAME CLOCK
================================================================================
Precision delta-time clock supporting FPS capping and frame delta clamping.
"""

import pygame
from src.data.settings import FPS

class GameClock:
    def __init__(self, target_fps: int = FPS):
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.raw_dt = 0.0
        self.dt = 0.0

    def tick(self) -> float:
        """Ticks the clock and returns clamped delta time in seconds."""
        delta_ms = self.clock.tick(self.target_fps)
        self.raw_dt = delta_ms / 1000.0
        # Clamp dt to avoid huge physics jumps during frame lag or window drags
        self.dt = min(self.raw_dt, 0.05)
        return self.dt

    def get_delta_time(self) -> float:
        """Ticks the clock and returns delta time in seconds."""
        return self.tick()

    def get_fps(self) -> float:
        return self.clock.get_fps()
