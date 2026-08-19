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

        total_rot_deg = -math.degrees(player.aim_angle) + (tilt_y * 0.35)

        # 2. 2D Entity Drop Shadow (Grounded to World Floor - Position/Scale Only, No Rotation)
        shadow_surf = self.sprite_manager.get_player_shadow(target_size=(58, 38))
        shadow_rect = shadow_surf.get_rect(center=(int(round(screen_x + 6)), int(round(screen_y + 12))))
        canvas.blit(shadow_surf, shadow_rect)

        # 3. Directional Ion Exhaust Flames (Speed/Acceleration Reactive)
        aim_rad = math.radians(-total_rot_deg)
        cos_a = math.cos(aim_rad)
        sin_a = math.sin(aim_rad)
        # Forward unit vector: (cos_a, sin_a), Perpendicular right unit vector: (-sin_a, cos_a)
        fwd_x, fwd_y = cos_a, sin_a
        right_x, right_y = -sin_a, cos_a

        if is_accelerating:
            flame_len = 16.0 + (speed_ratio * 24.0) + random.uniform(-2.0, 2.0)
            core_len = flame_len * 0.60
        elif speed_ratio > 0.30:
            flame_len = 9.0 + (speed_ratio * 14.0)
            core_len = flame_len * 0.55
        else:
            flame_len = 5.0 + math.sin(pygame.time.get_ticks() * 0.012) * 2.0
            core_len = flame_len * 0.50

        flame_color = (255, 204, 21) if player.overdrive_timer > 0 else (
            (56, 189, 248) if speed_ratio > 0.4 else glow_color
        )

        for side in [-13.0, 13.0]:
            # Nozzle origin position
            noz_x = screen_x - (fwd_x * 20.0) + (right_x * side)
            noz_y = screen_y - (fwd_y * 20.0) + (right_y * side)
            
            # Outer flame triangle
            tip_x = noz_x - (fwd_x * flame_len)
            tip_y = noz_y - (fwd_y * flame_len)
            base_l_x = noz_x + (right_x * 4.0)
            base_l_y = noz_y + (right_y * 4.0)
            base_r_x = noz_x - (right_x * 4.0)
            base_r_y = noz_y - (right_y * 4.0)
            pygame.draw.polygon(canvas, flame_color, [(base_l_x, base_l_y), (base_r_x, base_r_y), (tip_x, tip_y)])

            # Inner white flame core
            core_tip_x = noz_x - (fwd_x * core_len)
            core_tip_y = noz_y - (fwd_y * core_len)
            c_base_l_x = noz_x + (right_x * 2.0)
            c_base_l_y = noz_y + (right_y * 2.0)
            c_base_r_x = noz_x - (right_x * 2.0)
            c_base_r_y = noz_y - (right_y * 2.0)
            pygame.draw.polygon(canvas, COLOR_WHITE, [(c_base_l_x, c_base_l_y), (c_base_r_x, c_base_r_y), (core_tip_x, core_tip_y)])

        # 4. Render Pre-Cached Rotated Mechanical Drone Chassis (Zero Per-Frame Rotations)
        rotated_drone = self.sprite_manager.get_rotated_player_sprite(
            state=state, skin_idx=skin_idx, angle_deg=total_rot_deg, target_size=(68, 58)
        )
        rot_rect = rotated_drone.get_rect(center=(int(round(screen_x)), int(round(screen_y))))
        canvas.blit(rotated_drone, rot_rect)

        # 5. Muzzle Flash Flares at Dual Weapon Hardpoints
        if player.muzzle_flash_timer > 0:
            flash_rad = int(7 + (player.muzzle_flash_timer * 30.0))
            for side in [-16.0, 16.0]:
                gun_x = screen_x + (fwd_x * 24.0) + (right_x * side)
                gun_y = screen_y + (fwd_y * 24.0) + (right_y * side)
                pygame.draw.circle(canvas, (255, 255, 255), (int(gun_x), int(gun_y)), flash_rad)
                pygame.draw.circle(canvas, primary_color, (int(gun_x), int(gun_y)), flash_rad + 2, 1)

        # 6. Low Health Warning Sparks
        if player.health < player.max_health * 0.30:
            if random.random() < 0.25:
                sp_x = screen_x + random.randint(-14, 14)
                sp_y = screen_y + random.randint(-14, 14)
                pygame.draw.circle(canvas, (250, 204, 21), (int(sp_x), int(sp_y)), random.randint(1, 3))

        # 7. Active Shield Bubble Hit Overlay
        if player.shield_hits > 0:
            shield_r = 46
            shield_surf = self._shield_surf
            shield_surf.fill((0, 0, 0, 0))
            shimmer_alpha = int(120 + 45 * math.sin(pygame.time.get_ticks() * 0.008))
            pygame.draw.circle(shield_surf, (6, 182, 212, shimmer_alpha // 3), (shield_r + 3, shield_r + 3), shield_r)
            pygame.draw.circle(shield_surf, (56, 189, 248, shimmer_alpha), (shield_r + 3, shield_r + 3), shield_r, 2)
            pygame.draw.circle(shield_surf, (255, 255, 255, shimmer_alpha // 2), (shield_r + 3, shield_r + 3), shield_r - 4, 1)
            canvas.blit(shield_surf, (int(round(screen_x)) - shield_r - 3, int(round(screen_y)) - shield_r - 3))

        # 8. Overdrive Hyper-Aura
        if player.overdrive_timer > 0:
            od_r = 52
            od_surf = self._od_surf
            od_surf.fill((0, 0, 0, 0))
            pulse_a = int(140 + 55 * math.cos(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(od_surf, (245, 158, 11, pulse_a // 3), (od_r + 3, od_r + 3), od_r)
            pygame.draw.circle(od_surf, (255, 204, 21, pulse_a), (od_r + 3, od_r + 3), od_r, 2)
            canvas.blit(od_surf, (int(round(screen_x)) - od_r - 3, int(round(screen_y)) - od_r - 3))

