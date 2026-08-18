"""
================================================================================
            DRONE HUNTER 2D - CYBER FACTORY ENVIRONMENT SYSTEM
================================================================================
Dedicated 2D Environment Rendering System that transforms the arena into a
distinctive, heavy industrial Cyber Factory combat facility:
- Modular metallic steel floor plates, expansion seams, and hazard walkways
- Central High-Output Plasma Power Reactor with heavy magnetic blast pad
- Heavy industrial machinery units (Turbines, Smelters, Transformers, Cargo Stacks)
- Thick industrial pipe networks with metallic joints and conduit channels
- Clear tactical combat lanes (Central Core, North/South Belts, Flanking Lanes)
- 4 Border Spawn Airlocks with illuminated hazard strips
- Zero outer space stars; pure grounded dark industrial factory atmosphere
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE
)
from src.ui.font_manager import font_card

class FactoryFloor:
    """Pre-rendered / modular heavy steel industrial factory floor."""
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT, tile_size: int = 160):
        self.world_w = world_w
        self.world_h = world_h
        self.tile_size = tile_size

        # Pre-calculated structural floor zones
        self.walkway_stripes = [
            # Main East-West Assembly Belt
            (0, 680, world_w, 40),
            # North and South Transport Corridors
            (0, 320, world_w, 30),
            (0, 1040, world_w, 30),
        ]

        self.drain_grates = [
            (720, 520, 140, 50),
            (1540, 520, 140, 50),
            (720, 830, 140, 50),
            (1540, 830, 140, 50),
        ]

        self.floor_stencils = [
            ("SECTOR 01: ADVANCED FABRICATION FACILITY", (world_w // 2, 480)),
            ("CAUTION: HIGH-VOLTAGE PLASMA CONFINEMENT", (world_w // 2, 920)),
            ("<< CARGO INTAKE WEST", (480, 700)),
            ("LOGISTICS TERMINAL EAST >>", (1920, 700)),
        ]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float]):
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # 1. Base Dark Slate Foundation
        surface.fill((14, 18, 26))

        # 2. Modular Steel Floor Plating & Riveted Seams
        ts = self.tile_size
        start_x = int(ox // ts) * ts
        start_y = int(oy // ts) * ts
        end_x = start_x + vw + ts * 2
        end_y = start_y + vh + ts * 2

        seam_col = (20, 26, 38)
        rivet_col = (32, 44, 62)

        for gx in range(start_x, end_x, ts):
            for gy in range(start_y, end_y, ts):
                if 0 <= gx <= self.world_w and 0 <= gy <= self.world_h:
                    sx = int(round(gx - ox))
                    sy = int(round(gy - oy))
                    # Checker pattern of dark industrial metal tones
                    is_alt = ((gx // ts) + (gy // ts)) % 2 == 0
                    if is_alt:
                        pygame.draw.rect(surface, (17, 22, 32), (sx, sy, ts, ts))
                    pygame.draw.rect(surface, seam_col, (sx, sy, ts, ts), 1)
                    # Corner Bolt Rivets
                    pygame.draw.rect(surface, rivet_col, (sx - 2, sy - 2, 4, 4))

        # 3. Industrial Floor Walkway Hazard Stripes
        for wx, wy, ww, wh in self.walkway_stripes:
            wsx = int(round(wx - ox))
            wsy = int(round(wy - oy))
            if -ww <= wsx <= vw + ww and -wh <= wsy <= vh + wh:
                pygame.draw.rect(surface, (12, 16, 24), (wsx, wsy, ww, wh))
                pygame.draw.line(surface, (28, 38, 54), (wsx, wsy), (wsx + ww, wsy), 1)
                pygame.draw.line(surface, (28, 38, 54), (wsx, wsy + wh), (wsx + ww, wsy + wh), 1)
                # Subtle Hazard Chevrons
                for hx in range(max(0, wsx), min(vw, wsx + ww), 48):
                    pygame.draw.line(surface, (217, 119, 6), (hx, wsy + wh - 4), (hx + 12, wsy + 4), 2)

        # 4. Floor Drainage & Ventilation Grates (Recessed dark under-pits)
        for dx, dy, dw, dh in self.drain_grates:
            dsx = int(round(dx - ox))
            dsy = int(round(dy - oy))
            if -dw <= dsx <= vw + dw and -dh <= dsy <= vh + dh:
                pygame.draw.rect(surface, (6, 8, 12), (dsx, dsy, dw, dh), border_radius=3)
                pygame.draw.rect(surface, (30, 42, 60), (dsx, dsy, dw, dh), 2, border_radius=3)
                for gx in range(dsx + 6, dsx + dw - 6, 8):
                    pygame.draw.line(surface, (18, 25, 36), (gx, dsy + 4), (gx, dsy + dh - 4), 2)

        # 5. Stenciled Factory Floor Identification Signage
        for st_text, st_pos in self.floor_stencils:
            sx = int(round(st_pos[0] - ox))
            sy = int(round(st_pos[1] - oy))
            if -250 <= sx <= vw + 250 and -50 <= sy <= vh + 50:
                lbl = font_card.render(st_text, True, (40, 54, 76))
                surface.blit(lbl, lbl.get_rect(center=(sx, sy)))


class PowerReactor:
    """Central High-Output Industrial Plasma Super-Reactor."""
    def __init__(self, pos: tuple[float, float], size: int = 240):
        self.pos = pygame.Vector2(pos)
        self.size = size

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        cx = int(round(self.pos.x - ox))
        cy = int(round(self.pos.y - oy))
        r = self.size // 2

        if not (-r - 50 <= cx <= vw + r + 50 and -r - 50 <= cy <= vh + r + 50):
            return

        # 1. Reinforced Square Concrete Blast Foundation
        base_s = self.size + 40
        b_rect = pygame.Rect(cx - base_s // 2, cy - base_s // 2, base_s, base_s)
        pygame.draw.rect(surface, (10, 14, 20), b_rect, border_radius=8)
        pygame.draw.rect(surface, (28, 38, 54), b_rect, 2, border_radius=8)

        # Hazard Warning Border
        for hx in range(b_rect.left + 8, b_rect.right - 8, 24):
            pygame.draw.line(surface, (217, 119, 6), (hx, b_rect.top + 3), (hx + 8, b_rect.top + 9), 2)
            pygame.draw.line(surface, (217, 119, 6), (hx, b_rect.bottom - 3), (hx + 8, b_rect.bottom - 9), 2)

        # 2. Main Armored Octagonal Containment Vessel
        oct_pts = []
        for i in range(8):
            ang = i * (math.pi / 4.0) + (math.pi / 8.0)
            px = cx + int(math.cos(ang) * r)
            py = cy + int(math.sin(ang) * r)
            oct_pts.append((px, py))
        pygame.draw.polygon(surface, (22, 30, 44), oct_pts)
        pygame.draw.polygon(surface, (48, 66, 94), oct_pts, 3)

        # 3. Four Heavy Radial Magnetic Containment Pylons
        for ang_deg in [0, 90, 180, 270]:
            rad = math.radians(ang_deg)
            p1_x = cx + int(math.cos(rad) * (r * 0.42))
            p1_y = cy + int(math.sin(rad) * (r * 0.42))
            p2_x = cx + int(math.cos(rad) * (r + 16))
            p2_y = cy + int(math.sin(rad) * (r + 16))
            pygame.draw.line(surface, (14, 18, 28), (p1_x, p1_y), (p2_x, p2_y), 16)
            pygame.draw.line(surface, (14, 165, 233), (p1_x, p1_y), (p2_x, p2_y), 3)

        # 4. Circulating Plasma Chamber Core
        core_r = int(r * 0.50)
        pygame.draw.circle(surface, (8, 12, 18), (cx, cy), core_r)
        
        # Pulsating Energy Rings
        pulse_r = int(core_r * 0.78 + math.sin(time_accum * 4.5) * 4.0)
        glow_surf = pygame.Surface((core_r * 2 + 12, core_r * 2 + 12), pygame.SRCALPHA)
        pulse_a = int(170 + 50 * math.sin(time_accum * 5.0))
        pygame.draw.circle(glow_surf, (14, 165, 233, pulse_a // 3), (core_r + 6, core_r + 6), core_r)
        pygame.draw.circle(glow_surf, (56, 189, 248, pulse_a), (core_r + 6, core_r + 6), pulse_r, 3)
        pygame.draw.circle(glow_surf, (255, 255, 255, 230), (core_r + 6, core_r + 6), 10)
        surface.blit(glow_surf, (cx - core_r - 6, cy - core_r - 6))

        # 5. Stenciled Blast Pad Label
        lbl = font_card.render("REACTOR CORE 01", True, (60, 82, 112))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy + r + 14)))


class FactoryMachineryUnit:
    """Heavy industrial factory machinery with distinct physical silhouettes."""
    def __init__(self, rect: tuple[int, int, int, int], mtype: str = "turbine", label: str = "FAB-01"):
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

        # 1. Heavy Base Drop Shadow
        pygame.draw.rect(surface, (5, 7, 10), (sx + 8, sy + 8, bw, bh), border_radius=4)

        # 2. Main Solid Titanium-Alloy Heavy Machine Chassis
        pygame.draw.rect(surface, (22, 30, 42), (sx, sy, bw, bh), border_radius=4)
        pygame.draw.rect(surface, (45, 62, 88), (sx, sy, bw, bh), 2, border_radius=4)

        # 3. Silhouette-Specific Components
        if self.mtype == "turbine":
            # Circular Industrial Intake Fan Housing
            tur_r = min(bw, bh) // 2 - 12
            tcx = sx + bw // 2
            tcy = sy + bh // 2
            pygame.draw.circle(surface, (12, 16, 24), (tcx, tcy), tur_r)
            pygame.draw.circle(surface, (14, 165, 233), (tcx, tcy), tur_r, 2)
            # Spinning Turbine Blades
            blade_ang = time_accum * 6.0
            for b_i in range(6):
                b_rad = blade_ang + b_i * (math.pi / 3.0)
                bx = tcx + int(math.cos(b_rad) * (tur_r - 4))
                by = tcy + int(math.sin(b_rad) * (tur_r - 4))
                pygame.draw.line(surface, (48, 62, 82), (tcx, tcy), (bx, by), 3)
            pygame.draw.circle(surface, (28, 38, 54), (tcx, tcy), 8)
            pygame.draw.circle(surface, COLOR_CYAN, (tcx, tcy), 3)

        elif self.mtype == "smelter":
            # Recessed Glowing Molten Metal Vat
            vat_rect = pygame.Rect(sx + 14, sy + 14, bw - 28, bh - 28)
            pygame.draw.rect(surface, (10, 14, 20), vat_rect, border_radius=3)
            pygame.draw.rect(surface, (185, 28, 28), (vat_rect.left + 4, vat_rect.top + 4, vat_rect.width - 8, vat_rect.height - 8), border_radius=2)
            pygame.draw.rect(surface, (245, 158, 11), (vat_rect.left + 8, vat_rect.top + 8, vat_rect.width - 16, vat_rect.height - 16), border_radius=2)
            # Protective Heavy Grating
            for gx in range(vat_rect.left + 12, vat_rect.right - 12, 16):
                pygame.draw.line(surface, (18, 24, 34), (gx, vat_rect.top + 2), (gx, vat_rect.bottom - 2), 3)

        elif self.mtype == "transformer":
            # High-Voltage Ceramic Insulators on Top
            for ix in range(sx + 16, sx + bw - 16, 24):
                pygame.draw.circle(surface, (14, 165, 233), (ix, sy + 10), 5)
                pygame.draw.circle(surface, COLOR_WHITE, (ix, sy + 10), 2)
            # Recessed Heat Exhaust Vents
            for vy in range(sy + 26, sy + bh - 16, 12):
                pygame.draw.line(surface, (10, 14, 20), (sx + 14, vy), (sx + bw - 14, vy), 4)

        # 4. Corner Hazard Markings & Stencil Label
        pygame.draw.rect(surface, (217, 119, 6), (sx + 4, sy + bh - 8, 18, 4))
        lbl_txt = font_card.render(self.label, True, (75, 100, 134))
        surface.blit(lbl_txt, (sx + 8, sy + 6))


class PipeNetwork:
    """Heavy industrial steel pipe conduits interconnecting machinery hubs."""
    def __init__(self):
        self.pipes = [
            # Main Spine to Reactor
            ((180 + 80, 700), (1200 - 120, 700)),
            ((2060 + 80, 700), (1200 + 120, 700)),
            ((1200, 180 + 70), (1200, 700 - 120)),
            ((1200, 1080 + 70), (1200, 700 + 120)),
            # Corner Cross-Feeds
            ((480 + 140, 180 + 70), (900 + 70, 360 + 45)),
            ((1640 + 140, 180 + 70), (1360 + 70, 360 + 45)),
            ((480 + 140, 1080 + 70), (900 + 70, 950 + 45)),
            ((1640 + 140, 1080 + 70), (1360 + 70, 950 + 45)),
        ]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        pulse_alpha = int(120 + 50 * math.sin(time_accum * 3.2))
        conduit_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        conduit_glow = (14, 165, 233, pulse_alpha // 2)

        for p1, p2 in self.pipes:
            sp1 = (int(round(p1[0] - ox)), int(round(p1[1] - oy)))
            sp2 = (int(round(p2[0] - ox)), int(round(p2[1] - oy)))
            # Heavy 12px Conduit Trench & Steel Pipe
            pygame.draw.line(surface, (8, 12, 18), sp1, sp2, 12)
            pygame.draw.line(surface, (26, 36, 50), sp1, sp2, 8)
            pygame.draw.line(surface, (45, 60, 84), sp1, sp2, 2)
            # Glowing Core Line
            pygame.draw.line(conduit_surf, conduit_glow, sp1, sp2, 2)
        surface.blit(conduit_surf, (0, 0))


class CyberFactoryEnvironment:
    """Integrated 2D Cyber Factory Arena Environment Manager."""
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_w = world_w
        self.world_h = world_h
        self.time_accum = 0.0

        # 1. Floor System
        self.floor = FactoryFloor(world_w, world_h)

        # 2. Central Super-Reactor
        self.reactor = PowerReactor((world_w // 2, world_h // 2), size=240)

        # 3. Factory Machinery (Creating distinct tactical combat lanes)
        self.machinery = [
            # North Turbine District (Upper Combat Belt)
            FactoryMachineryUnit((480, 180, 280, 140), mtype="turbine", label="TURBINE-N1"),
            FactoryMachineryUnit((1640, 180, 280, 140), mtype="turbine", label="TURBINE-N2"),

            # South Heavy Smelter Array (Lower Combat Belt)
            FactoryMachineryUnit((480, 1080, 280, 140), mtype="smelter", label="SMELTER-S1"),
            FactoryMachineryUnit((1640, 1080, 280, 140), mtype="smelter", label="SMELTER-S2"),

            # West & East Transformer Substations (Flanking Lanes)
            FactoryMachineryUnit((180, 580, 160, 240), mtype="transformer", label="XFORM-WEST"),
            FactoryMachineryUnit((2060, 580, 160, 240), mtype="transformer", label="XFORM-EAST"),

            # Tactical Cover Bunkers (Midfield Dogfight Obstacles)
            FactoryMachineryUnit((900, 360, 140, 90), mtype="transformer", label="COV-01"),
            FactoryMachineryUnit((1360, 360, 140, 90), mtype="transformer", label="COV-02"),
            FactoryMachineryUnit((900, 950, 140, 90), mtype="transformer", label="COV-03"),
            FactoryMachineryUnit((1360, 950, 140, 90), mtype="transformer", label="COV-04"),
        ]

        # 4. Pipe Network
        self.pipes = PipeNetwork()

        # 5. Heavy Cargo Pallet Clusters (Industrial Detail)
        self.cargo_pallets = [
            (380, 460, 36, 32),
            (425, 470, 28, 28),
            (1980, 460, 36, 32),
            (2025, 470, 28, 28),
            (840, 230, 32, 28),
            (1520, 230, 32, 28),
            (840, 1130, 32, 28),
            (1520, 1130, 32, 28),
        ]

        # 6. Spawn Airlocks (4 Border Gates for future encounters)
        self.spawn_airlocks = [
            (world_w // 2 - 90, 30, 180, 26, "NORTH AIRLOCK"),
            (world_w // 2 - 90, world_h - 56, 180, 26, "SOUTH AIRLOCK"),
            (30, world_h // 2 - 90, 26, 180, "WEST AIRLOCK"),
            (world_w - 56, world_h // 2 - 90, 26, 180, "EAST AIRLOCK"),
        ]

    def update(self, dt: float):
        self.time_accum += dt

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders complete 2D Cyber Factory facility."""
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # 1. Industrial Steel Floor
        self.floor.draw(surface, camera_offset)

        # 2. Pipe & Conduit Network
        self.pipes.draw(surface, camera_offset, self.time_accum)

        # 3. Factory Machinery
        for m in self.machinery:
            m.draw(surface, camera_offset, self.time_accum)

        # 4. Central Power Reactor
        self.reactor.draw(surface, camera_offset, self.time_accum)

        # 5. Cargo Pallet Clusters
        for px, py, pw, ph in self.cargo_pallets:
            psx = int(round(px - ox))
            psy = int(round(py - oy))
            if -pw <= psx <= vw + pw and -ph <= psy <= vh + ph:
                pygame.draw.rect(surface, (5, 7, 10), (psx + 4, psy + 4, pw, ph), border_radius=2)
                pygame.draw.rect(surface, (26, 34, 48), (psx, psy, pw, ph), border_radius=2)
                pygame.draw.rect(surface, (48, 64, 90), (psx, psy, pw, ph), 1, border_radius=2)
                pygame.draw.line(surface, (217, 119, 6), (psx + 4, psy + ph // 2), (psx + pw - 4, psy + ph // 2), 2)

        # 6. Border Spawn Airlocks
        for ax, ay, aw, ah, alabel in self.spawn_airlocks:
            asx = int(round(ax - ox))
            asy = int(round(ay - oy))
            if -aw <= asx <= vw + aw and -ah <= asy <= vh + ah:
                pygame.draw.rect(surface, (10, 14, 20), (asx, asy, aw, ah), border_radius=4)
                pygame.draw.rect(surface, (239, 68, 68), (asx, asy, aw, ah), 2, border_radius=4)
                for zx in range(asx + 4, asx + aw - 8, 16):
                    pygame.draw.line(surface, (217, 119, 6), (zx, asy + ah - 4), (zx + 8, asy + 4), 2)

        # 7. Perimeter Security Barrier
        pad = 28.0
        bx1, by1 = int(round(pad - ox)), int(round(pad - oy))
        bx2, by2 = int(round((self.world_w - pad) - ox)), int(round((self.world_h - pad) - oy))

        b_alpha = int(140 + 40 * math.sin(self.time_accum * 4.0))
        barrier_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        b_col = (14, 165, 233, b_alpha)

        if 0 <= bx1 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx1, max(0, by1)), (bx1, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 32):
                pygame.draw.line(barrier_surf, (217, 119, 6, 160), (bx1 - 4, hy), (bx1 + 4, hy + 8), 1)

        if 0 <= bx2 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx2, max(0, by1)), (bx2, min(vh, by2)), 2)
            for hy in range(max(0, by1), min(vh, by2), 32):
                pygame.draw.line(barrier_surf, (217, 119, 6, 160), (bx2 - 4, hy), (bx2 + 4, hy + 8), 1)

        if 0 <= by1 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by1), (min(vw, bx2), by1), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 32):
                pygame.draw.line(barrier_surf, (217, 119, 6, 160), (hx, by1 - 4), (hx + 8, by1 + 4), 1)

        if 0 <= by2 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by2), (min(vw, bx2), by2), 2)
            for hx in range(max(0, bx1), min(vw, bx2), 32):
                pygame.draw.line(barrier_surf, (217, 119, 6, 160), (hx, by2 - 4), (hx + 8, by2 + 4), 1)

        surface.blit(barrier_surf, (0, 0))

        # Corner Defense Pylons
        for c_wx, c_wy in [(pad, pad), (self.world_w - pad, pad),
                           (pad, self.world_h - pad), (self.world_w - pad, self.world_h - pad)]:
            csx = int(round(c_wx - ox))
            csy = int(round(c_wy - oy))
            if -40 <= csx <= vw + 40 and -40 <= csy <= vh + 40:
                pygame.draw.circle(surface, (18, 24, 34), (csx, csy), 18)
                pygame.draw.circle(surface, (14, 165, 233), (csx, csy), 18, 2)
                pylon_blink = int(self.time_accum * 3.0) % 2 == 0
                pygame.draw.circle(surface, (239, 68, 68) if pylon_blink else (60, 20, 20), (csx, csy), 5)
