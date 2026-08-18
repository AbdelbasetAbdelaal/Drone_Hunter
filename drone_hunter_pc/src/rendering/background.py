"""
================================================================================
            DRONE HUNTER 2D - 2D COMBAT ARENA & PARALLAX BACKGROUND
================================================================================
Multi-layered 2D Cyber Factory Arena (2400x1400 world space) with industrial
machinery blocks, glowing power conduits, floor grates, structural pylons,
perimeter energy barriers, and camera-offset scrolling depth.
"""

import random
import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE
)
from src.data.game_data import SECTORS

class CyberFactoryArenaBackground:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.current_sector = 0
        self.time_accum = 0.0

        # Distant Parallax Dust Motes
        self.dust_particles = []
        for _ in range(60):
            self.dust_particles.append([
                random.uniform(0, world_w),
                random.uniform(0, world_h),
                random.uniform(0.15, 0.45), # Parallax factor
                random.choice([1, 2]),
                random.randint(70, 140)
            ])

        # Pre-generated Modular Machinery Blocks & Structural Props (Deterministic Placement)
        self.machinery_blocks = [
            (280, 220, 180, 110, "generator"),
            (740, 160, 220, 130, "vent_stack"),
            (1450, 200, 240, 120, "transformer"),
            (1920, 260, 200, 140, "generator"),
            (360, 920, 220, 130, "generator"),
            (900, 980, 260, 140, "transformer"),
            (1560, 940, 200, 120, "vent_stack"),
            (1100, 520, 160, 160, "core_reactor"),
        ]

        # Heavy Industrial Conduits connecting modules
        self.conduit_lines = [
            ((280 + 90, 220 + 55), (740 + 110, 160 + 65)),
            ((740 + 110, 160 + 65), (1100 + 80, 520 + 80)),
            ((1450 + 120, 200 + 60), (1100 + 80, 520 + 80)),
            ((1100 + 80, 520 + 80), (900 + 130, 980 + 70)),
            ((1100 + 80, 520 + 80), (1560 + 100, 940 + 60)),
            ((1920 + 100, 260 + 70), (1560 + 100, 940 + 60)),
            ((360 + 110, 920 + 65), (900 + 130, 980 + 70)),
        ]

    def set_sector(self, sector_idx: int):
        self.current_sector = sector_idx % len(SECTORS)

    def update(self, dt: float):
        self.time_accum += dt
        for d in self.dust_particles:
            d[0] = (d[0] - 12.0 * dt) % self.world_width
            d[1] = (d[1] + math.sin(self.time_accum * 1.5 + d[0] * 0.01) * 4.0 * dt) % self.world_height

    def draw_menu_backdrop(self, surface: pygame.Surface):
        """Renders clean atmospheric starfield backdrop strictly for screen-space menus."""
        vw, vh = surface.get_size()
        surface.fill((10, 14, 23))
        for d in self.dust_particles[:30]:
            sx = int(round(d[0])) % vw
            sy = int(round(d[1])) % vh
            pygame.draw.circle(surface, (d[4], d[4], int(d[4] * 1.1)), (sx, sy), d[3])

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders 2D Cyber Factory Arena in world space with camera viewport offset."""
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # 1. Base Atmospheric Sky / Deep Foundry Floor
        base_bg = (10, 14, 23)
        surface.fill(base_bg)

        # 2. Distant Parallax Dust Motes
        for d in self.dust_particles:
            sx = int(round(d[0] - ox * d[2])) % vw
            sy = int(round(d[1] - oy * d[2])) % vh
            col = (d[4], d[4], int(d[4] * 1.1)) if self.current_sector == 0 else (d[4], int(d[4] * 0.7), int(d[4] * 0.5))
            pygame.draw.circle(surface, col, (sx, sy), d[3])

        # 3. Modular Industrial Steel Floor Plating & Grid (World Space)
        tile_size = 120
        start_x = int(ox // tile_size) * tile_size
        start_y = int(oy // tile_size) * tile_size
        end_x = start_x + vw + tile_size * 2
        end_y = start_y + vh + tile_size * 2

        grid_col = (16, 22, 36)
        accent_seam = (20, 30, 48)
        
        for gx in range(start_x, end_x, tile_size):
            if 0 <= gx <= self.world_width:
                sx = int(round(gx - ox))
                pygame.draw.line(surface, grid_col, (sx, 0), (sx, vh), 1)
                for gy in range(start_y, end_y, tile_size):
                    if 0 <= gy <= self.world_height:
                        sy = int(round(gy - oy))
                        pygame.draw.rect(surface, accent_seam, (sx - 2, sy - 2, 4, 4))

        for gy in range(start_y, end_y, tile_size):
            if 0 <= gy <= self.world_height:
                sy = int(round(gy - oy))
                pygame.draw.line(surface, grid_col, (0, sy), (vw, sy), 1)

        # 4. Heavy Illuminated Power Conduits (World Space)
        pulse_alpha = int(100 + 45 * math.sin(self.time_accum * 3.0))
        conduit_core = (14, 165, 233, pulse_alpha // 2)
        conduit_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)

        for p1, p2 in self.conduit_lines:
            sp1 = (int(round(p1[0] - ox)), int(round(p1[1] - oy)))
            sp2 = (int(round(p2[0] - ox)), int(round(p2[1] - oy)))
            pygame.draw.line(surface, (20, 28, 42), sp1, sp2, 5)
            pygame.draw.line(conduit_surf, conduit_core, sp1, sp2, 2)
        surface.blit(conduit_surf, (0, 0))

        # 5. Industrial Machinery Platforms & Debris (World Space)
        for bx, by, bw, bh, mtype in self.machinery_blocks:
            sx = int(round(bx - ox))
            sy = int(round(by - oy))
            if -bw <= sx <= vw + bw and -bh <= sy <= vh + bh:
                # Platform Drop Shadow
                pygame.draw.rect(surface, (5, 8, 14), (sx + 6, sy + 6, bw, bh), border_radius=6)
                # Main Heavy Metal Housing
                pygame.draw.rect(surface, (16, 23, 36), (sx, sy, bw, bh), border_radius=6)
                pygame.draw.rect(surface, (30, 42, 64), (sx, sy, bw, bh), 1, border_radius=6)

                if mtype == "core_reactor":
                    core_r = 36
                    cx, cy = sx + bw // 2, sy + bh // 2
                    pygame.draw.circle(surface, (12, 18, 28), (cx, cy), core_r)
                    glow_r = int(core_r * 0.75 + math.sin(self.time_accum * 4.0) * 3.0)
                    pygame.draw.circle(surface, (14, 165, 233), (cx, cy), glow_r, 1)
                    pygame.draw.circle(surface, (56, 189, 248), (cx, cy), 8)
                elif mtype == "transformer":
                    for vy in range(sy + 16, sy + bh - 16, 16):
                        pygame.draw.line(surface, (14, 165, 233), (sx + 14, vy), (sx + bw - 14, vy), 1)
                elif mtype == "vent_stack":
                    for vx in range(sx + 18, sx + bw - 18, 18):
                        pygame.draw.rect(surface, (10, 14, 20), (vx, sy + 14, 8, bh - 28))
                        pygame.draw.rect(surface, (245, 158, 11), (vx + 1, sy + 16, 6, bh - 32), 1)

        # 6. High-Voltage Perimeter Energy Barrier (World Boundary)
        pad = 28.0
        bx1, by1 = int(round(pad - ox)), int(round(pad - oy))
        bx2, by2 = int(round((self.world_width - pad) - ox)), int(round((self.world_height - pad) - oy))

        b_alpha = int(140 + 45 * math.sin(self.time_accum * 4.5))
        barrier_col = (14, 165, 233, b_alpha)
        barrier_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)

        # Left Boundary
        if 0 <= bx1 <= vw:
            pygame.draw.line(barrier_surf, barrier_col, (bx1, max(0, by1)), (bx1, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 36):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (bx1 - 4, hy), (bx1 + 4, hy + 8), 1)

        # Right Boundary
        if 0 <= bx2 <= vw:
            pygame.draw.line(barrier_surf, barrier_col, (bx2, max(0, by1)), (bx2, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 36):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (bx2 - 4, hy), (bx2 + 4, hy + 8), 1)

        # Top Boundary
        if 0 <= by1 <= vh:
            pygame.draw.line(barrier_surf, barrier_col, (max(0, bx1), by1), (min(vw, bx2), by1), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 36):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (hx, by1 - 4), (hx + 8, by1 + 4), 1)

        # Bottom Boundary
        if 0 <= by2 <= vh:
            pygame.draw.line(barrier_surf, barrier_col, (max(0, bx1), by2), (min(vw, bx2), by2), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 36):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (hx, by2 - 4), (hx + 8, by2 + 4), 1)

        surface.blit(barrier_surf, (0, 0))

        # Corner Defense Pylons
        for c_wx, c_wy in [(pad, pad), (self.world_width - pad, pad),
                           (pad, self.world_height - pad), (self.world_width - pad, self.world_height - pad)]:
            csx = int(round(c_wx - ox))
            csy = int(round(c_wy - oy))
            if -40 <= csx <= vw + 40 and -40 <= csy <= vh + 40:
                pygame.draw.circle(surface, (20, 28, 44), (csx, csy), 16)
                pygame.draw.circle(surface, (14, 165, 233), (csx, csy), 16, 1)
                pygame.draw.circle(surface, (245, 158, 11), (csx, csy), 5)


ParallaxBackground = CyberFactoryArenaBackground
