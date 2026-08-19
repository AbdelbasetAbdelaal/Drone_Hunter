"""
================================================================================
            DRONE HUNTER 2D - DEDICATED PLAYER COMBAT DRONE RENDERER
================================================================================
Dedicated visual rendering layer for the player combat drone. Renders high-presence
faceted sci-fi armored hull (~70px combat silhouette), cockpit canopy, dual ion
thrusters with speed-reactive exhaust plumes, muzzle flashes, and shield auras.
"""

import math
import random
import pygame
from src.data.settings import (
    COLOR_CYAN, COLOR_GOLD, COLOR_WHITE, COLOR_SHIELD, COLOR_NEON_RED
)
from src.data.game_data import DRONE_SKINS

class PlayerRenderer:
    def __init__(self):
        self.idle_bob_timer = 0.0
        self._drone_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
        self._flash_overlay = pygame.Surface((128, 128), pygame.SRCALPHA)
        self._shield_surf = pygame.Surface((104, 104), pygame.SRCALPHA)
        self._od_surf = pygame.Surface((110, 110), pygame.SRCALPHA)

    def draw_player(self, canvas: pygame.Surface, player, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders high-presence combat drone with camera offset translation."""
        if not player.alive:
            return

        ox, oy = camera_offset
        screen_x = player.pos.x - ox
        screen_y = player.pos.y - oy

        skin_idx = max(0, min(len(DRONE_SKINS) - 1, player.skin_theme)) if isinstance(player.skin_theme, int) else 0
        skin = DRONE_SKINS[skin_idx]
        body_color = (36, 48, 68) if skin_idx == 0 else skin.get("body_color", (36, 48, 68))
        primary_color = skin.get("primary_color", (14, 165, 233))
        accent_color = skin.get("accent_color", (226, 232, 240))
        glow_color = skin.get("glow_color", (56, 189, 248))

        surf_size = 128
        half_s = surf_size // 2
        drone_surf = self._drone_surf
        drone_surf.fill((0, 0, 0, 0))

        current_speed = player.velocity.length()
        speed_ratio = min(1.0, current_speed / max(1.0, player.speed))
        is_accelerating = getattr(player, "is_accelerating", False)

        if is_accelerating:
            flame_len = 18.0 + (speed_ratio * 30.0) + random.uniform(-2.0, 3.0)
            core_len = flame_len * 0.65
        elif speed_ratio > 0.30:
            flame_len = 12.0 + (speed_ratio * 18.0)
            core_len = flame_len * 0.55
        else:
            flame_len = 6.0 + math.sin(pygame.time.get_ticks() * 0.01) * 2.0
            core_len = flame_len * 0.50

        flame_color = (255, 204, 21) if player.overdrive_timer > 0 else (
            (56, 189, 248) if speed_ratio > 0.4 else glow_color
        )

        for noz_y in [half_s - 12, half_s + 12]:
            outer_poly = [
                (half_s - 20, noz_y - 6),
                (half_s - 20, noz_y + 6),
                (half_s - 20 - flame_len, noz_y)
            ]
            pygame.draw.polygon(drone_surf, flame_color, outer_poly)
            inner_poly = [
                (half_s - 20, noz_y - 3),
                (half_s - 20, noz_y + 3),
                (half_s - 20 - core_len, noz_y)
            ]
            pygame.draw.polygon(drone_surf, COLOR_WHITE, inner_poly)

        chassis_points = [
            (half_s + 36, half_s),
            (half_s + 18, half_s - 16),
            (half_s - 8, half_s - 32),
            (half_s - 20, half_s - 22),
            (half_s - 16, half_s - 12),
            (half_s - 20, half_s),
            (half_s - 16, half_s + 12),
            (half_s - 20, half_s + 22),
            (half_s - 8, half_s + 32),
            (half_s + 18, half_s + 16),
        ]

        pygame.draw.polygon(drone_surf, body_color, chassis_points)
        pygame.draw.polygon(drone_surf, primary_color, chassis_points, 3)

        inner_plates = [
            (half_s + 16, half_s),
            (half_s - 2, half_s - 18),
            (half_s - 14, half_s - 12),
            (half_s - 8, half_s),
            (half_s - 14, half_s + 12),
            (half_s - 2, half_s + 18),
        ]
        pygame.draw.polygon(drone_surf, (22, 30, 44), inner_plates)
        pygame.draw.polygon(drone_surf, accent_color, inner_plates, 1)

        for canon_y in [half_s - 18, half_s + 18]:
            pygame.draw.line(drone_surf, (15, 23, 42), (half_s + 4, canon_y), (half_s + 28, canon_y), 5)
            pygame.draw.line(drone_surf, primary_color, (half_s + 4, canon_y), (half_s + 28, canon_y), 2)
            pygame.draw.circle(drone_surf, COLOR_WHITE, (half_s + 28, canon_y), 2)

        cockpit_points = [
            (half_s + 22, half_s),
            (half_s + 6, half_s - 8),
            (half_s - 6, half_s - 6),
            (half_s - 3, half_s),
            (half_s - 6, half_s + 6),
            (half_s + 6, half_s + 8),
        ]
        pygame.draw.polygon(drone_surf, (10, 15, 24), cockpit_points)
        pygame.draw.polygon(drone_surf, glow_color, cockpit_points, 2)
        pygame.draw.ellipse(drone_surf, COLOR_WHITE, (half_s + 8, half_s - 2, 8, 4))

        if player.muzzle_flash_timer > 0:
            flash_rad = int(10 + (player.muzzle_flash_timer * 40.0))
            for flash_y in [half_s - 18, half_s + 18]:
                pygame.draw.circle(drone_surf, (255, 255, 255, 240), (half_s + 30, flash_y), flash_rad)
                pygame.draw.circle(drone_surf, primary_color, (half_s + 30, flash_y), flash_rad + 3, 2)

        if player.damage_flash_timer > 0:
            self._flash_overlay.fill((255, 255, 255, 180))
            drone_surf.blit(self._flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        total_rot_deg = -math.degrees(player.aim_angle) + (getattr(player, "tilt_y", 0.0) * 0.35)
        rotated_surf = pygame.transform.rotate(drone_surf, total_rot_deg)
        rot_rect = rotated_surf.get_rect(center=(int(round(screen_x)), int(round(screen_y))))

        canvas.blit(rotated_surf, rot_rect)

        if player.shield_hits > 0:
            shield_r = 46
            shield_surf = self._shield_surf
            shield_surf.fill((0, 0, 0, 0))
            shimmer_alpha = int(120 + 45 * math.sin(pygame.time.get_ticks() * 0.008))
            pygame.draw.circle(shield_surf, (6, 182, 212, shimmer_alpha // 3), (shield_r + 3, shield_r + 3), shield_r)
            pygame.draw.circle(shield_surf, (56, 189, 248, shimmer_alpha), (shield_r + 3, shield_r + 3), shield_r, 2)
            pygame.draw.circle(shield_surf, (255, 255, 255, shimmer_alpha // 2), (shield_r + 3, shield_r + 3), shield_r - 4, 1)
            canvas.blit(shield_surf, (int(round(screen_x)) - shield_r - 3, int(round(screen_y)) - shield_r - 3))

        if player.overdrive_timer > 0:
            od_r = 52
            od_surf = self._od_surf
            od_surf.fill((0, 0, 0, 0))
            pulse_a = int(140 + 55 * math.cos(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(od_surf, (245, 158, 11, pulse_a // 3), (od_r + 3, od_r + 3), od_r)
            pygame.draw.circle(od_surf, (255, 204, 21, pulse_a), (od_r + 3, od_r + 3), od_r, 2)
            canvas.blit(od_surf, (int(round(screen_x)) - od_r - 3, int(round(screen_y)) - od_r - 3))
