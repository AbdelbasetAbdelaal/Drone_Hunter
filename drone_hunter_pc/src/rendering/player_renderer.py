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
        self._drone_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        self._flash_overlay = pygame.Surface((200, 200), pygame.SRCALPHA)
        self._shield_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
        self._od_surf = pygame.Surface((190, 190), pygame.SRCALPHA)
        self.sprite_manager = get_sprite_manager()

    def draw_player(self, canvas: pygame.Surface, player, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders high-presence physical mechanical combat drone with shadow and VFX."""
        if not player.alive and not getattr(player, "is_destroyed", False):
            return

        ox, oy = camera_offset
        screen_x = player.pos.x - ox
        screen_y = player.pos.y - oy

        skin_idx = max(0, min(len(DRONE_SKINS) - 1, player.skin_theme)) if isinstance(player.skin_theme, int) else 0
        skin = DRONE_SKINS[skin_idx]
        primary_color = skin.get("primary_color", COLOR_CYAN)
        glow_color = skin.get("glow_color", (56, 189, 248))

        current_speed = player.velocity.length()
        speed_ratio = min(1.0, current_speed / max(1.0, getattr(player, "speed", 450.0)))
        is_accelerating = getattr(player, "is_accelerating", False)

        # 1. Determine Visual State
        tilt_y = getattr(player, "tilt_y", 0.0)
        if player.muzzle_flash_timer > 0:
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

        # Precalculate direction vectors (used by glow, flames, and all VFX)
        aim_rad = math.radians(-total_rot_deg)
        cos_a = math.cos(aim_rad)
        sin_a = math.sin(aim_rad)
        fwd_x, fwd_y = cos_a, sin_a
        right_x, right_y = -sin_a, cos_a

        # 2. Cyan Engine Core Glow (Player Identity: Blue/Cyan Technology)
        core_alpha = int(90 + 50 * math.sin(pygame.time.get_ticks() * 0.006))
        for side in [-28.0, 28.0]:
            cx_ = screen_x - (fwd_x * 40.0) + (right_x * side)
            cy_ = screen_y - (fwd_y * 40.0) + (right_y * side)
            pygame.draw.circle(canvas, (14, 165, 233, max(0, min(255, core_alpha))),
                               (int(cx_), int(cy_)), 6)
            pygame.draw.circle(canvas, (200, 240, 255, max(0, min(200, core_alpha + 40))),
                               (int(cx_), int(cy_)), 3)

        # 3. Directional Ion Exhaust Flames (Crisp, Controlled, Non-Obstructive)


        if is_accelerating:
            flame_len = 22.0 + (speed_ratio * 28.0) + random.uniform(-2.0, 2.0)
            core_len = flame_len * 0.55
        elif speed_ratio > 0.30:
            flame_len = 14.0 + (speed_ratio * 16.0)
            core_len = flame_len * 0.50
        else:
            flame_len = 7.0 + math.sin(pygame.time.get_ticks() * 0.012) * 2.8
            core_len = flame_len * 0.45

        flame_color = (255, 204, 21) if player.overdrive_timer > 0 else (
            (56, 189, 248) if speed_ratio > 0.4 else glow_color
        )

        for side in [-28.0, 28.0]:
            # Nozzle origin position strictly at rear exhaust port
            noz_x = screen_x - (fwd_x * 42.0) + (right_x * side)
            noz_y = screen_y - (fwd_y * 42.0) + (right_y * side)
            
            # Outer flame triangle
            tip_x = noz_x - (fwd_x * flame_len)
            tip_y = noz_y - (fwd_y * flame_len)
            base_l_x = noz_x + (right_x * 7.0)
            base_l_y = noz_y + (right_y * 7.0)
            base_r_x = noz_x - (right_x * 7.0)
            base_r_y = noz_y - (right_y * 7.0)
            pygame.draw.polygon(canvas, flame_color, [(base_l_x, base_l_y), (base_r_x, base_r_y), (tip_x, tip_y)])

            # Inner white flame core
            core_tip_x = noz_x - (fwd_x * core_len)
            core_tip_y = noz_y - (fwd_y * core_len)
            c_base_l_x = noz_x + (right_x * 3.5)
            c_base_l_y = noz_y + (right_y * 3.5)
            c_base_r_x = noz_x - (right_x * 3.5)
            c_base_r_y = noz_y - (right_y * 3.5)
            pygame.draw.polygon(canvas, COLOR_WHITE, [(c_base_l_x, c_base_l_y), (c_base_r_x, c_base_r_y), (core_tip_x, core_tip_y)])

        # 3. Render Pre-Cached Rotated Mechanical Drone Chassis (Primary Visual - Enlarged HD Scale 176x152)
        rotated_drone = self.sprite_manager.get_rotated_player_sprite(
            state=state, skin_idx=skin_idx, angle_deg=total_rot_deg, target_size=(176, 152)
        )
        
        # Stealth Cloak Visual Effect: Phantom Translucency + Cyan Phase Distortion
        if getattr(player, "is_cloaked", False):
            rotated_drone = rotated_drone.copy()
            # 30% opacity ghosting
            rotated_drone.set_alpha(75)
            # Draw pulsing stealth ring around drone
            shimmer_r = int(50 + 6 * math.sin(pygame.time.get_ticks() * 0.015))
            pygame.draw.circle(canvas, (147, 51, 234, 110), (int(screen_x), int(screen_y)), shimmer_r, 2)
            pygame.draw.circle(canvas, (56, 189, 248, 80), (int(screen_x), int(screen_y)), shimmer_r - 4, 1)

        rot_rect = rotated_drone.get_rect(center=(int(round(screen_x)), int(round(screen_y))))
        canvas.blit(rotated_drone, rot_rect)

        # 4. Developer Debug Mount Mode (Optional Visualization)
        if getattr(player, "debug_mounts", False):
            from src.data.game_data import get_drone_class_by_id, DRONE_MOUNT_PROFILES
            cam_ox, cam_oy = camera_offset if camera_offset else (0, 0)
            d_class = get_drone_class_by_id(getattr(player, "drone_class_id", "striker"))
            cid = d_class.get("class_id", "striker")
            mount_prof = DRONE_MOUNT_PROFILES.get(cid, {})
            for m_name, (f_off, l_off) in mount_prof.items():
                m_wx, m_wy = player.get_mount_world_pos(m_name)
                m_sx, m_sy = int(round(m_wx - cam_ox)), int(round(m_wy - cam_oy))
                # Color code mounts by type
                if "front" in m_name or "primary" in m_name or "rail" in m_name:
                    m_col = (34, 197, 94)    # Green
                elif "left" in m_name or "dual_left" in m_name:
                    m_col = (234, 179, 8)    # Yellow
                elif "right" in m_name or "dual_right" in m_name:
                    m_col = (249, 115, 22)   # Orange
                elif "missile" in m_name or "pod" in m_name:
                    m_col = (239, 68, 68)    # Red
                elif "beam" in m_name or "energy" in m_name:
                    m_col = (59, 130, 246)   # Blue
                else:
                    m_col = (168, 85, 247)   # Purple
                pygame.draw.circle(canvas, m_col, (m_sx, m_sy), 4)
                pygame.draw.circle(canvas, COLOR_WHITE, (m_sx, m_sy), 2)


        # 5. Low Health Warning Sparks (Subtle localized warning)
        if player.health < player.max_health * 0.30:
            if random.random() < 0.20:
                sp_x = screen_x + random.randint(-24, 24)
                sp_y = screen_y + random.randint(-24, 24)
                pygame.draw.circle(canvas, (250, 204, 21), (int(sp_x), int(sp_y)), random.randint(1, 3))

        # 6. Active Shield Bubble Hit Overlay (Translucent Perimeter Ring)
        if player.shield_hits > 0:
            shield_r = 86
            shield_surf = self._shield_surf
            shield_surf.fill((0, 0, 0, 0))
            shimmer_alpha = int(100 + 40 * math.sin(pygame.time.get_ticks() * 0.008))
            pygame.draw.circle(shield_surf, (6, 182, 212, shimmer_alpha // 4), (shield_r + 5, shield_r + 5), shield_r)
            pygame.draw.circle(shield_surf, (56, 189, 248, shimmer_alpha), (shield_r + 5, shield_r + 5), shield_r, 3)
            pygame.draw.circle(shield_surf, (255, 255, 255, shimmer_alpha // 2), (shield_r + 5, shield_r + 5), shield_r - 4, 1)
            canvas.blit(shield_surf, (int(round(screen_x)) - shield_r - 5, int(round(screen_y)) - shield_r - 5))

        # 7. Overdrive Hyper-Aura (Non-Obstructive Outer Ring)
        if player.overdrive_timer > 0:
            od_r = 96
            od_surf = self._od_surf
            od_surf.fill((0, 0, 0, 0))
            pulse_a = int(110 + 45 * math.cos(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(od_surf, (245, 158, 11, pulse_a // 4), (od_r + 5, od_r + 5), od_r)
            pygame.draw.circle(od_surf, (255, 204, 21, pulse_a), (od_r + 5, od_r + 5), od_r, 3)
            canvas.blit(od_surf, (int(round(screen_x)) - od_r - 5, int(round(screen_y)) - od_r - 5))

        # 8. Subtle Localized Hit Impact (Cyan/Blue Energy Burst — No Full-Sprite White Flash)
        if player.damage_flash_timer > 0:
            hit_pct = max(0.0, min(1.0, player.damage_flash_timer / 0.10))
            impact_alpha = int(90 * hit_pct)
            impact_radius = int(18 + 14 * hit_pct)
            pygame.draw.circle(canvas, (14, 165, 233, max(0, min(255, impact_alpha))),
                               (int(round(screen_x)), int(round(screen_y))), impact_radius)
            pygame.draw.circle(canvas, (200, 240, 255, max(0, min(255, impact_alpha // 2))),
                               (int(round(screen_x)), int(round(screen_y))), max(1, impact_radius // 3))

        # 9. Player Destruction Sequence (High-Fidelity Asset)
        if getattr(player, "is_destroyed", False) and player.destruction_timer > 0:
            progress = 1.0 - (player.destruction_timer / 1.4)
            destroy_alpha = int(255 * max(0.0, 1.0 - progress * 1.1))
            destroy_size = int(110 + progress * 95)
            destroy_sprite = self.sprite_manager.get_player_state_sprite('destroy', skin_idx, (destroy_size, destroy_size))
            destroy_surf = destroy_sprite.copy()
            destroy_surf.set_alpha(destroy_alpha)
            destroy_rect = destroy_surf.get_rect(center=(int(round(screen_x)), int(round(screen_y))))
            canvas.blit(destroy_surf, destroy_rect)

    render = draw_player



