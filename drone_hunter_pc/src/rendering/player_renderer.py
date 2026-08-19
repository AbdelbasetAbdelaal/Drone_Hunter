"""
================================================================================
            DRONE HUNTER 2D - DEDICATED PLAYER COMBAT DRONE RENDERER
================================================================================
Dedicated visual rendering layer for the player combat drone (Phase 8 2D Overhaul).
Renders physical mechanical sci-fi chassis texture, 2D drop shadow, speed-reactive
twin ion thrusters, banking roll frames, muzzle flashes, and shield auras.
"""

import math
import random
import pygame
from src.data.settings import (
    COLOR_CYAN, COLOR_GOLD, COLOR_WHITE, COLOR_SHIELD, COLOR_NEON_RED, COLOR_CRIMSON
)
from src.data.game_data import DRONE_SKINS
from src.rendering.sprite_manager import get_sprite_manager

class PlayerRenderer:
    def __init__(self):
        self.idle_bob_timer = 0.0
        self._drone_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
        self._flash_overlay = pygame.Surface((128, 128), pygame.SRCALPHA)
        self._shield_surf = pygame.Surface((104, 104), pygame.SRCALPHA)
        self._od_surf = pygame.Surface((110, 110), pygame.SRCALPHA)
        self.sprite_manager = get_sprite_manager()

    def draw_player(self, canvas: pygame.Surface, player, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders high-presence physical mechanical combat drone with shadow and VFX."""
        if not player.alive:
            return

        ox, oy = camera_offset
        screen_x = player.pos.x - ox
        screen_y = player.pos.y - oy

        skin_idx = max(0, min(len(DRONE_SKINS) - 1, player.skin_theme)) if isinstance(player.skin_theme, int) else 0
        skin = DRONE_SKINS[skin_idx]
        primary_color = skin.get("primary_color", COLOR_CYAN)
        glow_color = skin.get("glow_color", (56, 189, 248))

        surf_size = 128
        half_s = surf_size // 2
        drone_surf = self._drone_surf
        drone_surf.fill((0, 0, 0, 0))

        current_speed = player.velocity.length()
        speed_ratio = min(1.0, current_speed / max(1.0, getattr(player, "speed", 450.0)))
        is_accelerating = getattr(player, "is_accelerating", False)

        # 1. Determine Visual State
        tilt_y = getattr(player, "tilt_y", 0.0)
        if player.damage_flash_timer > 0:
            state = "hit"
        elif player.muzzle_flash_timer > 0:
            state = "fire"
        elif tilt_y < -6.0:
            state = "bank_left"
        elif tilt_y > 6.0:
            state = "bank_right"
        elif is_accelerating or speed_ratio > 0.25:
            state = "move"
        else:
            state = "idle"

        # 2. Speed-Reactive Ion Thruster Exhaust Plumes (Layer 1 on drone_surf)
        if is_accelerating:
            flame_len = 16.0 + (speed_ratio * 26.0) + random.uniform(-2.0, 2.0)
            core_len = flame_len * 0.60
        elif speed_ratio > 0.30:
            flame_len = 10.0 + (speed_ratio * 16.0)
            core_len = flame_len * 0.55
        else:
            flame_len = 5.0 + math.sin(pygame.time.get_ticks() * 0.012) * 2.0
            core_len = flame_len * 0.50

        flame_color = (255, 204, 21) if player.overdrive_timer > 0 else (
            (56, 189, 248) if speed_ratio > 0.4 else glow_color
        )

        for noz_y in [half_s - 14, half_s + 14]:
            outer_poly = [
                (half_s - 22, noz_y - 5),
                (half_s - 22, noz_y + 5),
                (half_s - 22 - flame_len, noz_y)
            ]
            pygame.draw.polygon(drone_surf, flame_color, outer_poly)
            inner_poly = [
                (half_s - 22, noz_y - 2),
                (half_s - 22, noz_y + 2),
                (half_s - 22 - core_len, noz_y)
            ]
            pygame.draw.polygon(drone_surf, COLOR_WHITE, inner_poly)

        # 3. High-Detail 2D Mechanical Drone Sprite (Layer 2 on drone_surf)
        drone_sprite = self.sprite_manager.get_player_sprite(state=state, skin_idx=skin_idx, target_size=(68, 58))
        sp_w, sp_h = drone_sprite.get_size()
        drone_surf.blit(drone_sprite, (half_s - sp_w // 2, half_s - sp_h // 2))

        # 4. Muzzle Flash Flare when Firing
        if player.muzzle_flash_timer > 0:
            flash_rad = int(8 + (player.muzzle_flash_timer * 35.0))
            for flash_y in [half_s - 18, half_s + 18]:
                pygame.draw.circle(drone_surf, (255, 255, 255, 240), (half_s + 26, flash_y), flash_rad)
                pygame.draw.circle(drone_surf, primary_color, (half_s + 26, flash_y), flash_rad + 2, 1)

        # 5. Low Health Warning Sparks / Smoke Indicator
        if player.health < player.max_health * 0.30:
            if random.random() < 0.25:
                spark_x = half_s + random.randint(-16, 16)
                spark_y = half_s + random.randint(-12, 12)
                pygame.draw.circle(drone_surf, (250, 204, 21), (spark_x, spark_y), random.randint(1, 3))

        # 6. Damage Flash Overlay
        if player.damage_flash_timer > 0:
            self._flash_overlay.fill((255, 255, 255, 175))
            drone_surf.blit(self._flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # 7. 2D Entity Drop Shadow (Grounded to World Environment)
        total_rot_deg = -math.degrees(player.aim_angle) + (tilt_y * 0.35)
        shadow_surf = self.sprite_manager.get_player_shadow(target_size=(64, 54))
        rot_shadow = pygame.transform.rotate(shadow_surf, total_rot_deg)
        shadow_rect = rot_shadow.get_rect(center=(int(round(screen_x + 8)), int(round(screen_y + 14))))
        canvas.blit(rot_shadow, shadow_rect)

        # 8. Render Rotated Drone Chassis
        rotated_drone = pygame.transform.rotate(drone_surf, total_rot_deg)
        rot_rect = rotated_drone.get_rect(center=(int(round(screen_x)), int(round(screen_y))))
        canvas.blit(rotated_drone, rot_rect)

        # 9. Active Shield Bubble Hit Overlay
        if player.shield_hits > 0:
            shield_r = 46
            shield_surf = self._shield_surf
            shield_surf.fill((0, 0, 0, 0))
            shimmer_alpha = int(120 + 45 * math.sin(pygame.time.get_ticks() * 0.008))
            pygame.draw.circle(shield_surf, (6, 182, 212, shimmer_alpha // 3), (shield_r + 3, shield_r + 3), shield_r)
            pygame.draw.circle(shield_surf, (56, 189, 248, shimmer_alpha), (shield_r + 3, shield_r + 3), shield_r, 2)
            pygame.draw.circle(shield_surf, (255, 255, 255, shimmer_alpha // 2), (shield_r + 3, shield_r + 3), shield_r - 4, 1)
            canvas.blit(shield_surf, (int(round(screen_x)) - shield_r - 3, int(round(screen_y)) - shield_r - 3))

        # 10. Overdrive Hyper-Aura
        if player.overdrive_timer > 0:
            od_r = 52
            od_surf = self._od_surf
            od_surf.fill((0, 0, 0, 0))
            pulse_a = int(140 + 55 * math.cos(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(od_surf, (245, 158, 11, pulse_a // 3), (od_r + 3, od_r + 3), od_r)
            pygame.draw.circle(od_surf, (255, 204, 21, pulse_a), (od_r + 3, od_r + 3), od_r, 2)
            canvas.blit(od_surf, (int(round(screen_x)) - od_r - 3, int(round(screen_y)) - od_r - 3))

