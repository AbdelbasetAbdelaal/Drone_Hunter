"""
================================================================================
                    DRONE HUNTER 2D - GAME RENDERER
================================================================================
Centralized 2D rendering pipeline managing layered scene drawing, 2D camera
translation, visual aura effects, CRT scanlines, and screen presentation.
"""

import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_NEON_RED, COLOR_SHIELD, COLOR_WHITE
)
from src.data.game_data import TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER, TARGET_TYPE_EMP_DISRUPTER
from src.core.game_state import STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER

class GameRenderer:
    def __init__(self):
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def render_gameplay(self, context, background, particle_manager, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders active 2D gameplay battlefield translated by Camera2D offset."""
        ox, oy = camera_offset
        vw, vh = self.canvas.get_size()

        # Layer 1: Cyber Factory Arena & Background
        background.draw(self.canvas, camera_offset)

        # Layer 2: Visual Auras (Shield Drones & Sniper Lasers in World Space)
        for t in context.target_group:
            if getattr(t, "enemy_type", "") == TARGET_TYPE_SHIELD_DRONE:
                aura_surf = pygame.Surface((340, 340), pygame.SRCALPHA)
                pygame.draw.circle(aura_surf, (99, 102, 241, 45), (170, 170), 160)
                pygame.draw.circle(aura_surf, (56, 189, 248, 110), (170, 170), 160, 2)
                self.canvas.blit(aura_surf, (t.rect.centerx - ox - 170, t.rect.centery - oy - 170))

            elif getattr(t, "enemy_type", "") == TARGET_TYPE_SNIPER and getattr(t, "is_aiming", False) and context.player:
                p_screen = (int(round(context.player.pos.x - ox)), int(round(context.player.pos.y - oy)))
                t_screen = (int(round(t.pos.x - ox)), int(round(t.pos.y - oy)))
                line_alpha = 180 if int(pygame.time.get_ticks() * 0.015) % 2 == 0 else 90
                laser_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
                pygame.draw.line(laser_surf, (239, 68, 68, line_alpha), t_screen, p_screen, 2)
                self.canvas.blit(laser_surf, (0, 0))

            elif getattr(t, "enemy_type", "") == TARGET_TYPE_EMP_DISRUPTER and getattr(t, "is_emp_expanding", False):
                emp_r = int(getattr(t, "emp_wave_radius", 0))
                if emp_r > 0:
                    t_screen = (int(round(t.pos.x - ox)), int(round(t.pos.y - oy)))
                    emp_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
                    pygame.draw.circle(emp_surf, (14, 165, 233, 110), t_screen, emp_r, 4)
                    pygame.draw.circle(emp_surf, (255, 255, 255, 180), t_screen, emp_r, 1)
                    self.canvas.blit(emp_surf, (0, 0))

        # Helper to blit sprite groups with camera offset
        def _draw_group_with_camera(group):
            for spr in group:
                sx = int(round(spr.rect.x - ox))
                sy = int(round(spr.rect.y - oy))
                if -spr.rect.width <= sx <= vw + spr.rect.width and -spr.rect.height <= sy <= vh + spr.rect.height:
                    self.canvas.blit(spr.image, (sx, sy))

        # Layer 3: Sprite Entities
        _draw_group_with_camera(context.target_group)
        _draw_group_with_camera(context.obstacle_group)
        _draw_group_with_camera(context.hazard_group)
        _draw_group_with_camera(context.bullet_group)
        _draw_group_with_camera(context.enemy_bullet_group)
        _draw_group_with_camera(context.powerup_group)

        # Layer 4: Player Combat Drone & Wingmen
        if context.player:
            context.player.draw(self.canvas, camera_offset)
            context.player.draw_wingmen(self.canvas, camera_offset)

        # Layer 5: Particles, Weather & Floating Combat Text
        particle_manager.draw(self.canvas, camera_offset)

        # Layer 6: Red Damage Flash
        if context.damage_flash_timer > 0:
            flash_alpha = int(110 * (context.damage_flash_timer / 0.18))
            flash_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
            flash_surf.fill((239, 68, 68, flash_alpha))
            self.canvas.blit(flash_surf, (0, 0))

    def draw_crosshair(self):
        """Draws animated tactical sci-fi crosshair at mouse position."""
        mx, my = pygame.mouse.get_pos()
        r = 12
        pygame.draw.circle(self.canvas, (14, 165, 233, 160), (mx, my), r, 1)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx - r - 4, my), (mx - 4, my), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx + 4, my), (mx + r + 4, my), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx, my - r - 4), (mx, my - 4), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx, my + 4), (mx, my + r + 4), 2)

    def draw_crt_scanlines(self):
        """Renders retro arcade CRT scanline overlay."""
        vw, vh = self.canvas.get_size()
        for y in range(0, vh, 4):
            pygame.draw.line(self.canvas, (0, 0, 0, 45), (0, y), (vw, y), 1)

    def present(self, target_screen: pygame.Surface, context, win_w: int, win_h: int):
        """Applies CRT filter, resizes to window, applies screen shake, and flips display."""
        if context.show_crt:
            self.draw_crt_scanlines()

        ox, oy = context.get_shake_offset()
        scaled = pygame.transform.smoothscale(self.canvas, (win_w, win_h))
        target_screen.blit(scaled, (ox, oy))
        pygame.display.flip()
