"""
================================================================================
            DRONE HUNTER 2D - CYBER FACTORY 2D COMBAT ARENA
================================================================================
Distinctive 2D Cyber Factory industrial environment featuring:
- Layered metallic floor plates, maintenance hatches, and hazard floor tracks
- Central High-Voltage Power Reactor with pulsating plasma core
- Heavy machinery units, coolant transformer banks, and steam exhaust grates
- Structural pipe conduits and cable networks connecting factory zones
- Clear tactical combat lanes (Central Hub, Flanking Belts, Corridors)
- Designated industrial spawn intake zones with warning beacons
- High-contrast 2D lighting hierarchy (Dark Graphite, Cyan Tech, Amber Hazard)
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE
)
from src.data.game_data import SECTORS

class PowerReactor:
    """Central 2D Industrial High-Energy Power Core."""
    def __init__(self, pos: tuple[float, float], size: int = 180):
        self.pos = pygame.Vector2(pos)
        self.size = size

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        cx = int(round(self.pos.x - ox))
        cy = int(round(self.pos.y - oy))
        r = self.size // 2

        # Culling check
        if not (-r <= cx <= vw + r and -r <= cy <= vh + r):
            return

        # 1. Outer Hexagonal Structural Foundation
        pts = []
        for i in range(8):
            ang = i * (math.pi / 4.0) + (math.pi / 8.0)
            px = cx + int(math.cos(ang) * (r + 16))
            py = cy + int(math.sin(ang) * (r + 16))
            pts.append((px, py))
        pygame.draw.polygon(surface, (8, 12, 20), pts)
        pygame.draw.polygon(surface, (28, 40, 60), pts, 2)

        # 2. Main Armored Housing Octagon
        inner_pts = []
        for i in range(8):
            ang = i * (math.pi / 4.0) + (math.pi / 8.0)
            px = cx + int(math.cos(ang) * r)
            py = cy + int(math.sin(ang) * r)
            inner_pts.append((px, py))
        pygame.draw.polygon(surface, (18, 25, 38), inner_pts)
        pygame.draw.polygon(surface, (45, 62, 90), inner_pts, 3)

        # 3. Radiating Cooling Fin Spokes
        for i in range(8):
            ang = i * (math.pi / 4.0)
            fx1 = cx + int(math.cos(ang) * (r * 0.45))
            fy1 = cy + int(math.sin(ang) * (r * 0.45))
            fx2 = cx + int(math.cos(ang) * (r * 0.95))
            fy2 = cy + int(math.sin(ang) * (r * 0.95))
            pygame.draw.line(surface, (12, 18, 28), (fx1, fy1), (fx2, fy2), 8)
            pygame.draw.line(surface, (56, 189, 248), (fx1, fy1), (fx2, fy2), 2)

        # 4. Central Circulating Plasma Core
        core_r = int(r * 0.42)
        pygame.draw.circle(surface, (10, 15, 24), (cx, cy), core_r)
        
        # Pulsating Core Auras
        pulse_r = int(core_r * 0.75 + math.sin(time_accum * 4.0) * 4.0)
        core_alpha = int(180 + 55 * math.sin(time_accum * 5.0))
        glow_surf = pygame.Surface((core_r * 2 + 10, core_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (14, 165, 233, core_alpha // 3), (core_r + 5, core_r + 5), core_r)
        pygame.draw.circle(glow_surf, (56, 189, 248, core_alpha), (core_r + 5, core_r + 5), pulse_r, 2)
        pygame.draw.circle(glow_surf, (255, 255, 255, 220), (core_r + 5, core_r + 5), 8)
        surface.blit(glow_surf, (cx - core_r - 5, cy - core_r - 5))

        # 5. Perimeter Blinking Amber Safety Beacons
        for i in range(4):
            b_ang = i * (math.pi / 2.0) + (math.pi / 4.0)
            bx = cx + int(math.cos(b_ang) * (r + 10))
            by = cy + int(math.sin(b_ang) * (r + 10))
            is_lit = int((time_accum * 3.0) + i) % 2 == 0
            pygame.draw.circle(surface, (245, 158, 11) if is_lit else (60, 40, 10), (bx, by), 4)


class FactoryMachineryUnit:
    """Heavy industrial fabrication block / transformer unit."""
    def __init__(self, rect: tuple[int, int, int, int], mtype: str = "transformer", label: str = "FAB-01"):
        self.rect = pygame.Rect(rect)
        self.mtype = mtype
        self.label = label

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        sx = int(round(self.rect.x - ox))
        sy = int(round(self.rect.y - oy))
        bw, bh = self.rect.width, self.rect.height

        if not (-bw <= sx <= vw + bw and -bh <= sy <= vh + bh):
            return

        # 1. Structural Base Shadow & Foundation Slab
        pygame.draw.rect(surface, (6, 9, 15), (sx + 8, sy + 8, bw, bh), border_radius=6)
        pygame.draw.rect(surface, (15, 22, 34), (sx, sy, bw, bh), border_radius=6)
        pygame.draw.rect(surface, (32, 45, 68), (sx, sy, bw, bh), 2, border_radius=6)

        # 2. Chamfered Corner Reinforcements
        c_len = 16
        pygame.draw.line(surface, (56, 189, 248), (sx, sy + c_len), (sx + c_len, sy), 2)
        pygame.draw.line(surface, (56, 189, 248), (sx + bw - c_len, sy), (sx + bw, sy + c_len), 2)

        # 3. Internal Components based on machine type
        if self.mtype == "transformer":
            # Cooling Vents & Heat Coils
            for vy in range(sy + 18, sy + bh - 18, 14):
                pygame.draw.line(surface, (8, 12, 20), (sx + 16, vy), (sx + bw - 16, vy), 4)
                pygame.draw.line(surface, (14, 165, 233), (sx + 18, vy), (sx + bw - 18, vy), 1)
            # Amber Power Gauge
            p_fill = int((bw - 32) * (0.6 + 0.3 * math.sin(time_accum * 2.0 + sx * 0.01)))
            pygame.draw.rect(surface, (10, 14, 20), (sx + 16, sy + 8, bw - 32, 5), border_radius=2)
            pygame.draw.rect(surface, (245, 158, 11), (sx + 16, sy + 8, p_fill, 5), border_radius=2)

        elif self.mtype == "smelter":
            # Molten Heat Chamber Grate
            m_glow = int(160 + 60 * math.sin(time_accum * 3.5 + sy * 0.01))
            grate_rect = pygame.Rect(sx + 18, sy + 18, bw - 36, bh - 36)
            pygame.draw.rect(surface, (10, 14, 20), grate_rect, border_radius=4)
            pygame.draw.rect(surface, (245, 158, 11, m_glow), grate_rect, 2, border_radius=4)
            for gy in range(grate_rect.top + 8, grate_rect.bottom - 6, 12):
                pygame.draw.line(surface, (239, 68, 68), (grate_rect.left + 6, gy), (grate_rect.right - 6, gy), 2)

        elif self.mtype == "conveyor":
            # Assembly Line Rollers
            for rx in range(sx + 14, sx + bw - 14, 20):
                pygame.draw.rect(surface, (10, 14, 22), (rx, sy + 10, 10, bh - 20), border_radius=3)
                pygame.draw.line(surface, (51, 65, 85), (rx + 5, sy + 12), (rx + 5, sy + bh - 12), 2)
            # Directional Transport Chevrons
            c_offset = int((time_accum * 40.0) % 24)
            for cx in range(sx + 18, sx + bw - 18, 24):
                tx = cx + c_offset
                if sx + 12 < tx < sx + bw - 12:
                    pygame.draw.line(surface, (245, 158, 11), (tx, sy + bh // 2 - 6), (tx + 6, sy + bh // 2), 2)
                    pygame.draw.line(surface, (245, 158, 11), (tx + 6, sy + bh // 2), (tx, sy + bh // 2 + 6), 2)

        # 4. Status Indicator LED
        led_blink = int(time_accum * 4.0 + sx) % 2 == 0
        pygame.draw.circle(surface, (16, 185, 129) if led_blink else (6, 78, 59), (sx + bw - 12, sy + 12), 3)


class CyberFactoryArenaBackground:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.current_sector = 0
        self.time_accum = 0.0

        # Central Power Reactor (Hub of the Arena)
        self.reactor = PowerReactor((world_w // 2, world_h // 2), size=190)

        # Tactical Factory Machinery Layout (Creating distinct combat lanes)
        self.machinery = [
            # North Fabrication District (Combat Lane Top)
            FactoryMachineryUnit((500, 200, 260, 130), mtype="transformer", label="FAB-N1"),
            FactoryMachineryUnit((1640, 200, 260, 130), mtype="transformer", label="FAB-N2"),
            
            # South Heavy Foundry & Smelting Belt (Combat Lane Bottom)
            FactoryMachineryUnit((500, 1070, 260, 130), mtype="smelter", label="SMLT-S1"),
            FactoryMachineryUnit((1640, 1070, 260, 130), mtype="smelter", label="SMLT-S2"),
            
            # West Conveyor Intake Depot (Combat Lane Left)
            FactoryMachineryUnit((200, 580, 160, 240), mtype="conveyor", label="CONV-W"),
            
            # East Logistics Station (Combat Lane Right)
            FactoryMachineryUnit((2040, 580, 160, 240), mtype="conveyor", label="CONV-E"),

            # Secondary Tactical Cover Barriers
            FactoryMachineryUnit((920, 360, 140, 90), mtype="transformer", label="COV-1"),
            FactoryMachineryUnit((1340, 360, 140, 90), mtype="transformer", label="COV-2"),
            FactoryMachineryUnit((920, 950, 140, 90), mtype="transformer", label="COV-3"),
            FactoryMachineryUnit((1340, 950, 140, 90), mtype="transformer", label="COV-4"),
        ]

        # Industrial Heavy Pipe & Conduit Network (Interconnecting Hubs)
        self.conduit_network = [
            # Main Spine to Reactor
            ((200 + 80, 700), (1200 - 95, 700)),
            ((2040 + 80, 700), (1200 + 95, 700)),
            ((1200, 200 + 65), (1200, 700 - 95)),
            ((1200, 1070 + 65), (1200, 700 + 95)),
            # Corner Cross-Feeds
            ((500 + 130, 200 + 65), (920 + 70, 360 + 45)),
            ((1640 + 130, 200 + 65), (1340 + 70, 360 + 45)),
            ((500 + 130, 1070 + 65), (920 + 70, 950 + 45)),
            ((1640 + 130, 1070 + 65), (1340 + 70, 950 + 45)),
        ]

        # Floor Maintenance Areas & Access Hatches (World Space)
        self.floor_hatches = [
            (750, 600, 90, 90),
            (1560, 600, 90, 90),
            (750, 800, 90, 90),
            (1560, 800, 90, 90),
            (1200 - 45, 420, 90, 60),
            (1200 - 45, 920, 90, 60),
        ]

        # Industrial Debris & Crates (Subtle World Scatter)
        self.debris_props = [
            (420, 480, 28, 28),
            (440, 515, 24, 24),
            (1940, 480, 28, 28),
            (1960, 515, 24, 24),
            (880, 240, 32, 22),
            (1480, 240, 32, 22),
            (880, 1140, 32, 22),
            (1480, 1140, 32, 22),
        ]

        # Future Enemy Spawn Gates (Spatial Visual Preparation)
        self.spawn_gates = [
            # Top Gate
            (1200 - 80, 32, 160, 24, "NORTH AIRLOCK"),
            # Bottom Gate
            (1200 - 80, 1400 - 56, 160, 24, "SOUTH AIRLOCK"),
            # West Gate
            (32, 700 - 80, 24, 160, "WEST CONVEYOR"),
            # East Gate
            (2400 - 56, 700 - 80, 24, 160, "EAST CONVEYOR"),
        ]

        # Parallax atmospheric dust particles (low count for clean readability)
        self.dust_particles = []
        for _ in range(35):
            self.dust_particles.append([
                random.uniform(0, world_w),
                random.uniform(0, world_h),
                random.uniform(0.12, 0.35),
                random.choice([1, 2]),
                random.randint(60, 120)
            ])

    def set_sector(self, sector_idx: int):
        self.current_sector = sector_idx % len(SECTORS)

    def update(self, dt: float):
        self.time_accum += dt
        for d in self.dust_particles:
            d[0] = (d[0] - 10.0 * dt) % self.world_width
            d[1] = (d[1] + math.sin(self.time_accum * 1.2 + d[0] * 0.01) * 3.0 * dt) % self.world_height

    def draw_menu_backdrop(self, surface: pygame.Surface):
        """Renders clean atmospheric background strictly for screen-space menus."""
        vw, vh = surface.get_size()
        surface.fill((10, 14, 23))
        # Subtle ambient grid & dust motes
        for gy in range(0, vh, 80):
            pygame.draw.line(surface, (14, 20, 32), (0, gy), (vw, gy), 1)
        for d in self.dust_particles[:20]:
            sx = int(round(d[0])) % vw
            sy = int(round(d[1])) % vh
            pygame.draw.circle(surface, (d[4], d[4], int(d[4] * 1.1)), (sx, sy), d[3])

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders 2D Cyber Factory Arena in world space with camera viewport offset."""
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # =====================================================================
        # 1. LAYER 1: BASE GRAPHITE FACTORY FOUNDATION
        # =====================================================================
        surface.fill((10, 14, 22))

        # =====================================================================
        # 2. LAYER 2: INDUSTRIAL METALLIC FLOOR PLATES & SEAMS (World Space)
        # =====================================================================
        tile_size = 160
        start_x = int(ox // tile_size) * tile_size
        start_y = int(oy // tile_size) * tile_size
        end_x = start_x + vw + tile_size * 2
        end_y = start_y + vh + tile_size * 2

        seam_col = (16, 23, 35)
        rivet_col = (26, 36, 54)

        # Seam Lines
        for gx in range(start_x, end_x, tile_size):
            if 0 <= gx <= self.world_width:
                sx = int(round(gx - ox))
                pygame.draw.line(surface, seam_col, (sx, 0), (sx, vh), 1)
                for gy in range(start_y, end_y, tile_size):
                    if 0 <= gy <= self.world_height:
                        sy = int(round(gy - oy))
                        # Corner Bolt Rivets
                        pygame.draw.rect(surface, rivet_col, (sx - 2, sy - 2, 4, 4))

        for gy in range(start_y, end_y, tile_size):
            if 0 <= gy <= self.world_height:
                sy = int(round(gy - oy))
                pygame.draw.line(surface, seam_col, (0, sy), (vw, sy), 1)

        # Floor Maintenance Access Hatches
        for hx, hy, hw, hh in self.floor_hatches:
            hsx = int(round(hx - ox))
            hsy = int(round(hy - oy))
            if -hw <= hsx <= vw + hw and -hh <= hsy <= vh + hh:
                pygame.draw.rect(surface, (14, 20, 30), (hsx, hsy, hw, hh), border_radius=4)
                pygame.draw.rect(surface, (28, 40, 58), (hsx, hsy, hw, hh), 1, border_radius=4)
                # Hatch Cross Brace
                pygame.draw.line(surface, (20, 28, 42), (hsx + 8, hsy + 8), (hsx + hw - 8, hsy + hh - 8), 1)
                pygame.draw.line(surface, (20, 28, 42), (hsx + hw - 8, hsy + 8), (hsx + 8, hsy + hh - 8), 1)

        # =====================================================================
        # 3. LAYER 3: HEAVY PIPE & POWER CONDUIT NETWORK (World Space)
        # =====================================================================
        pulse_alpha = int(120 + 50 * math.sin(self.time_accum * 3.2))
        conduit_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        conduit_core = (14, 165, 233, pulse_alpha // 2)

        for p1, p2 in self.conduit_network:
            sp1 = (int(round(p1[0] - ox)), int(round(p1[1] - oy)))
            sp2 = (int(round(p2[0] - ox)), int(round(p2[1] - oy)))
            # Outer Metal Duct
            pygame.draw.line(surface, (18, 25, 38), sp1, sp2, 6)
            pygame.draw.line(surface, (32, 44, 66), sp1, sp2, 2)
            # Glowing Core Pulse
            pygame.draw.line(conduit_surf, conduit_core, sp1, sp2, 2)
        surface.blit(conduit_surf, (0, 0))

        # =====================================================================
        # 4. LAYER 4: INDUSTRIAL FACTORY MACHINERY & CENTRAL REACTOR (World Space)
        # =====================================================================
        # Draw Machinery Units
        for m in self.machinery:
            m.draw(surface, camera_offset, self.time_accum)

        # Draw Central Power Reactor
        self.reactor.draw(surface, camera_offset, self.time_accum)

        # Draw Industrial Debris / Crates
        for dx, dy, dw, dh in self.debris_props:
            dsx = int(round(dx - ox))
            dsy = int(round(dy - oy))
            if -dw <= dsx <= vw + dw and -dh <= dsy <= vh + dh:
                pygame.draw.rect(surface, (8, 12, 18), (dsx + 3, dsy + 3, dw, dh), border_radius=3)
                pygame.draw.rect(surface, (20, 28, 42), (dsx, dsy, dw, dh), border_radius=3)
                pygame.draw.rect(surface, (40, 55, 80), (dsx, dsy, dw, dh), 1, border_radius=3)
                pygame.draw.line(surface, (245, 158, 11), (dsx + 4, dsy + dh // 2), (dsx + dw - 4, dsy + dh // 2), 1)

        # =====================================================================
        # 5. LAYER 5: DESIGNATED ENEMY SPAWN ZONES / AIRLOCKS
        # =====================================================================
        for gx, gy, gw, gh, glabel in self.spawn_gates:
            gsx = int(round(gx - ox))
            gsy = int(round(gy - oy))
            if -gw <= gsx <= vw + gw and -gh <= gsy <= vh + gh:
                # Airlock Frame
                pygame.draw.rect(surface, (14, 20, 30), (gsx, gsy, gw, gh), border_radius=4)
                pygame.draw.rect(surface, (239, 68, 68), (gsx, gsy, gw, gh), 1, border_radius=4)
                # Warning Hazard Stripes
                for zx in range(gsx + 4, gsx + gw - 8, 16):
                    pygame.draw.line(surface, (245, 158, 11), (zx, gsy + gh - 4), (zx + 8, gsy + 4), 2)

        # =====================================================================
        # 6. LAYER 6: ARENA PERIMETER ENERGY BARRIER & DEFENSE PYLONS
        # =====================================================================
        pad = 28.0
        bx1, by1 = int(round(pad - ox)), int(round(pad - oy))
        bx2, by2 = int(round((self.world_width - pad) - ox)), int(round((self.world_height - pad) - oy))

        b_alpha = int(140 + 40 * math.sin(self.time_accum * 4.0))
        barrier_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        b_col = (14, 165, 233, b_alpha)

        # Left Boundary
        if 0 <= bx1 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx1, max(0, by1)), (bx1, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 32):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (bx1 - 4, hy), (bx1 + 4, hy + 8), 1)

        # Right Boundary
        if 0 <= bx2 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx2, max(0, by1)), (bx2, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 32):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (bx2 - 4, hy), (bx2 + 4, hy + 8), 1)

        # Top Boundary
        if 0 <= by1 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by1), (min(vw, bx2), by1), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 32):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (hx, by1 - 4), (hx + 8, by1 + 4), 1)

        # Bottom Boundary
        if 0 <= by2 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by2), (min(vw, bx2), by2), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 32):
                pygame.draw.line(barrier_surf, (245, 158, 11, 160), (hx, by2 - 4), (hx + 8, by2 + 4), 1)

        surface.blit(barrier_surf, (0, 0))

        # Corner Defense Pylons
        for c_wx, c_wy in [(pad, pad), (self.world_width - pad, pad),
                           (pad, self.world_height - pad), (self.world_width - pad, self.world_height - pad)]:
            csx = int(round(c_wx - ox))
            csy = int(round(c_wy - oy))
            if -40 <= csx <= vw + 40 and -40 <= csy <= vh + 40:
                pygame.draw.circle(surface, (18, 25, 38), (csx, csy), 18)
                pygame.draw.circle(surface, (14, 165, 233), (csx, csy), 18, 2)
                pylon_blink = int(self.time_accum * 3.0) % 2 == 0
                pygame.draw.circle(surface, (239, 68, 68) if pylon_blink else (60, 20, 20), (csx, csy), 5)

        # =====================================================================
        # 7. LAYER 7: SUBTLE AMBIENT DUST MOTES
        # =====================================================================
        for d in self.dust_particles:
            dsx = int(round(d[0] - ox * d[2])) % vw
            dsy = int(round(d[1] - oy * d[2])) % vh
            pygame.draw.circle(surface, (d[4], d[4], int(d[4] * 1.1)), (dsx, dsy), d[3])


ParallaxBackground = CyberFactoryArenaBackground
