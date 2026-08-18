"""
================================================================================
                    DRONE HUNTER 2D - 2D SMOOTH CAMERA
================================================================================
Target-following 2D camera providing smooth position interpolation (lerp),
viewport offset calculations, coordinate conversions, and screen shake.
"""

import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera2D:
    def __init__(self, world_w: int = 1920, world_h: int = 1080):
        self.world_width = world_w
        self.world_height = world_h
        self.viewport_width = SCREEN_WIDTH
        self.viewport_height = SCREEN_HEIGHT
        
        # Camera center position in world space
        self.center_x = float(world_w // 2)
        self.center_y = float(world_h // 2)
        
        # Current top-left scroll offset
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # Camera smoothness (0.0 = instant, higher = smoother)
        self.smooth_speed = 8.0

    def update(self, target_pos: tuple[float, float], dt: float):
        """Smoothly interpolates camera toward target position, clamping to arena bounds."""
        tx, ty = target_pos
        
        # Lerp camera center toward target
        lerp_factor = min(1.0, self.smooth_speed * dt)
        self.center_x += (tx - self.center_x) * lerp_factor
        self.center_y += (ty - self.center_y) * lerp_factor
        
        # Calculate top-left offset
        half_vw = self.viewport_width / 2.0
        half_vh = self.viewport_height / 2.0
        
        target_ox = self.center_x - half_vw
        target_oy = self.center_y - half_vh
        
        # Clamp camera to arena boundaries
        max_ox = max(0.0, self.world_width - self.viewport_width)
        max_oy = max(0.0, self.world_height - self.viewport_height)
        
        self.offset_x = max(0.0, min(max_ox, target_ox))
        self.offset_y = max(0.0, min(max_oy, target_oy))

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        """Converts world coordinates to screen viewport coordinates."""
        return int(world_x - self.offset_x), int(world_y - self.offset_y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Converts screen coordinates to world coordinates."""
        return float(screen_x + self.offset_x), float(screen_y + self.offset_y)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Returns a new Rect translated by the camera offset."""
        return rect.move(-int(self.offset_x), -int(self.offset_y))
