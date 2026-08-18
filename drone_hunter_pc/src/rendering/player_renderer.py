"""
================================================================================
                DRONE HUNTER 2D - DEDICATED PLAYER DRONE RENDERER
================================================================================
Dedicated visual rendering layer for the player combat drone. Renders procedural
faceted sci-fi armored hull, cockpit canopy, dual ion thrusters, muzzle flashes,
energy shield aura, and damage flash states.
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
        self.thruster_flicker = 0.0
        self.cached_base_surfaces = {}

    def draw_player(self, canvas: pygame.Surface, player, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders player combat drone at world position converted with camera offset."""
        if not player.alive:
            return

        ox, oy = camera_offset
        screen_x = player.pos.x - ox
        screen_y = player.pos.y - oy

        skin_idx = max(0, min(len(DRONE_SKINS) - 1, player.skin_theme)) if isinstance(player.skin_theme, int) else 0
        skin = DRONE_SKINS[skin_idx]
        body_color = skin.get("body_color", (15, 23, 42))
        primary_color = skin.get("primary_color", COLOR_CYAN)
        glow_color = skin.get("glow_color", COLOR_CYAN)

        # 1. Calculate Drone Dimensions & Surface
        surf_size = 96
        half_s = surf_size // 2
        drone_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

        # Speed and acceleration calculation
        current_speed = player.velocity.length()
        speed_ratio = min(1.0, current_speed / max(1.0, player.max_speed))
        is_accelerating = player.is_accelerating

        # 2. Render Animated Rear Ion Thruster Flames
        flame_len = 10.0 + (speed_ratio * 18.0) + (random.uniform(-2, 3) if is_accelerating else 0)
        flame_color = (255, 200, 50) if player.overdrive_timer > 0 else (56, 189, 248) if speed_ratio > 0.6 else glow_color

        # Left Thruster Flame
        lt_poly = [
            (half_s - 14, half_s - 8),
            (half_s - 14, half_s + 8),
            (half_s - 14 - flame_len, half_s)
        ]
        pygame.draw.polygon(drone_surf, flame_color, lt_poly)
        pygame.draw.polygon(drone_surf, COLOR_WHITE, [
            (half_s - 14, half_s - 4),
            (half_s - 14, half_s + 4),
            (half_s - 14 - (flame_len * 0.6), half_s)
        ])

        # 3. Main Chassis Polygon (Aggressive Swept Delta-Wing Combat Drone)
        # Coordinates aligned facing RIGHT (0 degrees)
        chassis_points = [
            (half_s + 26, half_s),         # Forward nose tip
            (half_s + 12, half_s - 12),    # Front-right wing root
            (half_s - 6, half_s - 22),     # Right wingtip
            (half_s - 14, half_s - 16),    # Right wing trailing edge
            (half_s - 12, half_s - 8),     # Right thruster mount
            (half_s - 14, half_s),         # Rear center notch
            (half_s - 12, half_s + 8),     # Left thruster mount
            (half_s - 14, half_s + 16),    # Left wing trailing edge
            (half_s - 6, half_s + 22),     # Left wingtip
            (half_s + 12, half_s + 12),    # Front-left wing root
        ]

        # Draw Main Wing Armor
        pygame.draw.polygon(drone_surf, body_color, chassis_points)
        pygame.draw.polygon(drone_surf, primary_color, chassis_points, 2)

        # 4. Wing Hardpoint Weapon Cannons (Dual Pulse Barrels)
        # Top/Right Cannon
        pygame.draw.line(drone_surf, (51, 65, 85), (half_s + 2, half_s - 14), (half_s + 20, half_s - 14), 4)
        pygame.draw.line(drone_surf, primary_color, (half_s + 2, half_s - 14), (half_s + 20, half_s - 14), 2)
        # Bottom/Left Cannon
        pygame.draw.line(drone_surf, (51, 65, 85), (half_s + 2, half_s + 14), (half_s + 20, half_s + 14), 4)
        pygame.draw.line(drone_surf, primary_color, (half_s + 2, half_s + 14), (half_s + 20, half_s + 14), 2)

        # 5. Cockpit Visor & Tech Details
        cockpit_points = [
            (half_s + 16, half_s),
            (half_s + 4, half_s - 6),
            (half_s - 4, half_s - 5),
            (half_s - 2, half_s),
            (half_s - 4, half_s + 5),
            (half_s + 4, half_s + 6),
        ]
        pygame.draw.polygon(drone_surf, (10, 15, 26), cockpit_points)
        pygame.draw.polygon(drone_surf, glow_color, cockpit_points, 2)
        pygame.draw.circle(drone_surf, COLOR_WHITE, (half_s + 8, half_s), 2)

        # 6. Muzzle Flash Rendering
        if player.muzzle_flash_timer > 0:
            flash_rad = int(8 + (player.muzzle_flash_timer * 35.0))
            pygame.draw.circle(drone_surf, (255, 255, 255, 220), (half_s + 22, half_s - 14), flash_rad)
            pygame.draw.circle(drone_surf, (255, 255, 255, 220), (half_s + 22, half_s + 14), flash_rad)
            pygame.draw.circle(drone_surf, primary_color, (half_s + 22, half_s - 14), flash_rad + 3, 2)
            pygame.draw.circle(drone_surf, primary_color, (half_s + 22, half_s + 14), flash_rad + 3, 2)

        # 7. Apply Damage Flash (White/Red Overlay)
        if player.damage_flash_timer > 0:
            flash_overlay = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, 140))
            drone_surf.blit(flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # 8. Rotate Drone toward Aim Angle (in Degrees)
        # In Pygame, positive angles rotate counter-clockwise, so we negate degrees
        aim_deg = -math.degrees(player.aim_angle)
        rotated_surf = pygame.transform.rotate(drone_surf, aim_deg)
        rot_rect = rotated_surf.get_rect(center=(int(screen_x), int(screen_y)))

        # 9. Blit Rotated Drone Chassis
        canvas.blit(rotated_surf, rot_rect)

        # 10. Protective Energy Shield Bubble Shimmer
        if player.shield_hits > 0:
            shield_r = 38
            shield_surf = pygame.Surface((shield_r * 2 + 4, shield_r * 2 + 4), pygame.SRCALPHA)
            shimmer_alpha = int(120 + 40 * math.sin(pygame.time.get_ticks() * 0.008))
            pygame.draw.circle(shield_surf, (6, 182, 212, shimmer_alpha // 3), (shield_r + 2, shield_r + 2), shield_r)
            pygame.draw.circle(shield_surf, (56, 189, 248, shimmer_alpha), (shield_r + 2, shield_r + 2), shield_r, 2)
            pygame.draw.circle(shield_surf, (255, 255, 255, shimmer_alpha // 2), (shield_r + 2, shield_r + 2), shield_r - 4, 1)
            canvas.blit(shield_surf, (int(screen_x) - shield_r - 2, int(screen_y) - shield_r - 2))

        # 11. Overdrive Hyper-Aura
        if player.overdrive_timer > 0:
            od_r = 44
            od_surf = pygame.Surface((od_r * 2 + 4, od_r * 2 + 4), pygame.SRCALPHA)
            pulse_a = int(140 + 50 * math.cos(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(od_surf, (245, 158, 11, pulse_a // 3), (od_r + 2, od_r + 2), od_r)
            pygame.draw.circle(od_surf, (255, 204, 21, pulse_a), (od_r + 2, od_r + 2), od_r, 2)
            canvas.blit(od_surf, (int(screen_x) - od_r - 2, int(screen_y) - od_r - 2))
