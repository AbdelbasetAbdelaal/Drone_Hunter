"""
================================================================================
                    DRONE HUNTER 2D - GAME RENDERER
================================================================================
Centralized 2D rendering pipeline managing layered scene drawing, 2D camera
translation, visual aura effects, CRT scanlines, and screen presentation.
PERF FIX: Cached large SRCALPHA surfaces to eliminate per-frame allocations.
"""

import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_NEON_RED, COLOR_SHIELD, COLOR_WHITE, COLOR_EMERALD
)
from src.data.game_data import (
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER, TARGET_TYPE_EMP_DISRUPTER,
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED,
    TARGET_TYPE_BOSS
)
from src.core.game_state import STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER
from src.rendering.sprite_manager import get_sprite_manager

class GameRenderer:
    def __init__(self):
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.sprite_manager = get_sprite_manager()

        # PERF: Pre-allocated reusable surfaces to eliminate per-frame SRCALPHA allocations
        self._shield_aura_surf = pygame.Surface((340, 340), pygame.SRCALPHA)
        self._shield_aura_surf.fill((0, 0, 0, 0))
        pygame.draw.circle(self._shield_aura_surf, (99, 102, 241, 45), (170, 170), 160)
        pygame.draw.circle(self._shield_aura_surf, (56, 189, 248, 110), (170, 170), 160, 2)

        self._laser_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._emp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._last_flash_alpha = -1

    def render_gameplay(self, context, background, particle_manager, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders active 2D gameplay battlefield translated by Camera2D offset."""
        ox, oy = camera_offset
        vw, vh = self.canvas.get_size()

        # Layer 1: Cyber Factory Arena & Background
        background.draw(self.canvas, camera_offset)

        # Layer 1.5: Environment readability — subtle dimming overlay in combat zones
        # when an objective assault is active. Reduces background brightness/contrast
        # around combat entities WITHOUT blurring or adding artificial shadows.
        obj_sys = getattr(context, "objective_system", None)
        if obj_sys and getattr(obj_sys, "is_active", False) and getattr(obj_sys, "active_objective", None):
            if not getattr(self, "_combat_dim_surf", None) or self._combat_dim_surf.get_size() != (vw, vh):
                self._combat_dim_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
            dim_alpha = 35 if obj_sys.is_active else 0
            self._combat_dim_surf.fill((0, 0, 0, dim_alpha))
            self.canvas.blit(self._combat_dim_surf, (0, 0))

        # Layer 2: Visual Auras (Shield Drones & Sniper Lasers in World Space)
        for t in context.target_group:
            if getattr(t, "enemy_type", "") == TARGET_TYPE_SHIELD_DRONE:
                # PERF: Reuse pre-built aura surface (no new allocation per frame)
                self.canvas.blit(self._shield_aura_surf, (t.rect.centerx - ox - 170, t.rect.centery - oy - 170))

            elif getattr(t, "enemy_type", "") == TARGET_TYPE_SNIPER and getattr(t, "is_aiming", False) and context.player:
                t_screen = (int(round(t.pos.x - ox)), int(round(t.pos.y - oy)))
                if hasattr(t, "sniper_aim_target"):
                    p_screen = (int(round(t.sniper_aim_target.x - ox)), int(round(t.sniper_aim_target.y - oy)))
                else:
                    p_screen = (int(round(context.player.pos.x - ox)), int(round(context.player.pos.y - oy)))
                line_alpha = 180 if int(pygame.time.get_ticks() * 0.015) % 2 == 0 else 90
                self._laser_surf.fill((0, 0, 0, 0))
                pygame.draw.line(self._laser_surf, (239, 68, 68, line_alpha), t_screen, p_screen, 2)
                pygame.draw.line(self._laser_surf, (255, 200, 200, 120), t_screen, p_screen, 1)
                self.canvas.blit(self._laser_surf, (0, 0))

            elif getattr(t, "enemy_type", "") == TARGET_TYPE_EMP_DISRUPTER and getattr(t, "is_emp_expanding", False):
                emp_r = int(getattr(t, "emp_wave_radius", 0))
                if emp_r > 0:
                    t_screen = (int(round(t.pos.x - ox)), int(round(t.pos.y - oy)))
                    # PERF: Reuse emp_surf instead of allocating a new surface
                    self._emp_surf.fill((0, 0, 0, 0))
                    pygame.draw.circle(self._emp_surf, (14, 165, 233, 110), t_screen, emp_r, 4)
                    pygame.draw.circle(self._emp_surf, (255, 255, 255, 180), t_screen, emp_r, 1)
                    self.canvas.blit(self._emp_surf, (0, 0))

        # Layer 3: Entities and Objects (Direct High-Fidelity Rendering)

        # Helper to blit sprite groups with camera offset
        def _draw_group_with_camera(group):
            for spr in group:
                sx = int(round(spr.rect.x - ox))
                sy = int(round(spr.rect.y - oy))
                if -spr.rect.width <= sx <= vw + spr.rect.width and -spr.rect.height <= sy <= vh + spr.rect.height:
                    self.canvas.blit(spr.image, (sx, sy))
                    if hasattr(spr, "weapon_id"):
                        from src.data.game_data import WEAPON_ASSETS
                        asset_path = WEAPON_ASSETS.get(spr.weapon_id, spr.weapon_id)
                        self.sprite_manager.track_weapon_render(asset_path)

        # Layer 4: Sprite Entities
        _draw_group_with_camera(context.target_group)
        _draw_group_with_camera(context.obstacle_group)
        _draw_group_with_camera(context.hazard_group)
        _draw_group_with_camera(context.bullet_group)
        _draw_group_with_camera(context.enemy_bullet_group)
        _draw_group_with_camera(context.powerup_group)

        # Layer 4.5: Health Bars for Strong Enemies (Heavy, Armored, Shield Drone, Boss)
        for t in context.target_group:
            if not getattr(t, "alive", False):
                continue
            etype = getattr(t, "enemy_type", "")
            if etype not in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_BOSS):
                continue
            hp = getattr(t, "hp", 0)
            max_hp = getattr(t, "max_hp", 1)
            hp_pct = max(0.0, min(1.0, hp / max(1.0, max_hp)))
            bar_w = 40
            bar_h = 5
            tx = int(round(t.rect.centerx - ox))
            ty = int(round(t.rect.top - ox - 10))
            bg_rect = pygame.Rect(tx - bar_w // 2, ty, bar_w, bar_h)
            pygame.draw.rect(self.canvas, (15, 23, 42, 200), bg_rect, border_radius=2)
            if hp_pct > 0:
                fill_w = int(round(bar_w * hp_pct))
                bar_col = COLOR_CRIMSON if hp_pct <= 0.35 else (COLOR_GOLD if hp_pct <= 0.70 else COLOR_EMERALD)
                pygame.draw.rect(self.canvas, bar_col, (bg_rect.x, bg_rect.y, fill_w, bar_h), border_radius=2)
            pygame.draw.rect(self.canvas, (51, 65, 85), bg_rect, 1, border_radius=2)

        # Layer 4: Player Combat Drone & Wingmen
        if context.player:
            context.player.draw(self.canvas, camera_offset)
            context.player.draw_wingmen(self.canvas, camera_offset)

        # Layer 5: Particles, Weather & Floating Combat Text
        particle_manager.draw(self.canvas, camera_offset)

        # Layer 6: Red Damage Flash
        if context.damage_flash_timer > 0:
            flash_alpha = int(110 * (context.damage_flash_timer / 0.18))
            # PERF: Only rebuild flash surface when alpha meaningfully changes
            if abs(flash_alpha - self._last_flash_alpha) >= 4:
                self._flash_surf.fill((239, 68, 68, flash_alpha))
                self._last_flash_alpha = flash_alpha
            self.canvas.blit(self._flash_surf, (0, 0))
        else:
            self._last_flash_alpha = -1

    def draw_crosshair(self, mouse_pos: tuple[int, int] = None):
        """Draws animated tactical sci-fi crosshair at canvas mouse position."""
        if mouse_pos is None:
            mx, my = pygame.mouse.get_pos()
        else:
            mx, my = mouse_pos
        r = 12
        pygame.draw.circle(self.canvas, (14, 165, 233, 160), (mx, my), r, 1)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx - r - 4, my), (mx - 4, my), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx + 4, my), (mx + r + 4, my), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx, my - r - 4), (mx, my - 4), 2)
        pygame.draw.line(self.canvas, (14, 165, 233), (mx, my + 4), (mx, my + r + 4), 2)

    def present(self, screen, ctx, win_w, win_h):
        """Presents the canvas to the window, scaling if needed."""
        sw, sh = self.canvas.get_size()
        if (sw, sh) != (win_w, win_h):
            scaled = pygame.transform.scale(self.canvas, (win_w, win_h))
            screen.blit(scaled, (0, 0))
        else:
            screen.blit(self.canvas, (0, 0))
        pygame.display.flip()

    def set_viewport_size(self, w: int, h: int):
        """Resize the internal canvas when the window is resized."""
        pass  # Canvas stays fixed; scaling is done in present()

    def toggle_fullscreen(self):
        """Safe fallback to toggle fullscreen mode."""
        surf = pygame.display.get_surface()
        if surf:
            is_full = bool(surf.get_flags() & pygame.FULLSCREEN)
            if is_full:
                pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            else:
                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
