"""
================================================================================
                    DRONE HUNTER 2D - 2D SMOOTH CAMERA
================================================================================
Target-following 2D camera providing smooth position interpolation (lerp),
dynamic viewport sizing, boundary clamping, and world/screen conversions.
"""

import pygame
import random
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT

class Camera2D:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT,
                 view_w: int = SCREEN_WIDTH, view_h: int = SCREEN_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.viewport_width = view_w
        self.viewport_height = view_h
        
        # Camera center position in world space
        self.center_x = float(world_w // 2)
        self.center_y = float(world_h // 2)
        
        # Current top-left scroll offset
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # Camera smoothness (higher = more responsive, lower = floatier)
        self.smooth_speed = 6.5
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def set_viewport_size(self, vw: int, vh: int):
        """Updates viewport dimensions when window is resized."""
        self.viewport_width = max(320, vw)
        self.viewport_height = max(240, vh)

    def update(self, target_pos: tuple[float, float], dt: float, shake_intensity: float = 0.0, shake_time: float = 0.0):
        """Smoothly interpolates camera toward target position, clamping to arena bounds."""
        tx, ty = target_pos
        
        # Apply screen shake offset
        if shake_time > 0.0 and shake_intensity > 0.0:
            shake_x = random.uniform(-shake_intensity, shake_intensity)
            shake_y = random.uniform(-shake_intensity, shake_intensity)
            tx += shake_x
            ty += shake_y
        
        # Lerp camera center toward target
        lerp_factor = min(1.0, self.smooth_speed * dt)
        self.center_x += (tx - self.center_x) * lerp_factor
        self.center_y += (ty - self.center_y) * lerp_factor
        
        # Calculate top-left offset
        half_vw = self.viewport_width / 2.0
        half_vh = self.viewport_height / 2.0
        
        target_ox = self.center_x - half_vw
        target_oy = self.center_y - half_vh
        
        # Clamp camera offset to world boundaries
        max_ox = max(0.0, float(self.world_width - self.viewport_width))
        max_oy = max(0.0, float(self.world_height - self.viewport_height))
        
        self.offset_x = max(0.0, min(max_ox, target_ox))
        self.offset_y = max(0.0, min(max_oy, target_oy))

    def get_offset(self) -> tuple[float, float]:
        """Returns current top-left camera world offset tuple."""
        return (self.offset_x, self.offset_y)

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        """Converts world coordinates to screen viewport coordinates."""
        return int(round(world_x - self.offset_x)), int(round(world_y - self.offset_y))

    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Converts screen coordinates to world coordinates."""
        return float(screen_x + self.offset_x), float(screen_y + self.offset_y)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Returns a new Rect translated by the camera offset."""
        return rect.move(-int(round(self.offset_x)), -int(round(self.offset_y)))
