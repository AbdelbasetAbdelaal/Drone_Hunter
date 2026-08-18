"""
================================================================================
            DRONE HUNTER 2D - CYBER FACTORY 2D COMBAT ARENA
================================================================================
Comprehensive 2D Cyber Factory industrial environment featuring:
- Solid steel modular floor plating with riveted seams and industrial hazard tracks
- Central High-Voltage Super-Reactor Hub with heavy containment blast ring
- Solid industrial machinery units (Turbines, Smelters, Transformers, Cargo Crates)
- Heavy dual-layer power pipes & recessed conduit channels
- Clear tactical combat lanes (Central Hub, North/South Belts, Flanking Lanes)
- Factory spawn gates (North/South airlocks, East/West conveyors)
- Zero space stars; replaced with subtle industrial factory floor lighting
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE
)
from src.data.game_data import SECTORS
from src.ui.font_manager import font_card

class IndustrialReactor:
    """Central High-Output Plasma Super-Reactor."""
    def __init__(self, pos: tuple[float, float], size: int = 240):
        self.pos = pygame.Vector2(pos)
        self.size = size

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        cx = int(round(self.pos.x - ox))
        cy = int(round(self.pos.y - oy))
        r = self.size // 2

        if not (-r - 40 <= cx <= vw + r + 40 and -r - 40 <= cy <= vh + r + 40):
            return

        # 1. Heavy Reinforced Concrete Blast Foundation (Square base)
        base_s = self.size + 40
        b_rect = pygame.Rect(cx - base_s // 2, cy - base_s // 2, base_s, base_s)
        pygame.draw.rect(surface, (12, 16, 24), b_rect, border_radius=8)
        pygame.draw.rect(surface, (28, 38, 54), b_rect, 2, border_radius=8)

        # Hazard Warning Border around reactor pad
        h_len = 16
        for hx in range(b_rect.left + 8, b_rect.right - 8, 24):
            pygame.draw.line(surface, (245, 158, 11), (hx, b_rect.top + 4), (hx + 8, b_rect.top + 10), 2)
            pygame.draw.line(surface, (245, 158, 11), (hx, b_rect.bottom - 4), (hx + 8, b_rect.bottom - 10), 2)

        # 2. Main Octagonal Armored Containment Vessel
        oct_pts = []
        for i in range(8):
            ang = i * (math.pi / 4.0) + (math.pi / 8.0)
            px = cx + int(math.cos(ang) * r)
            py = cy + int(math.sin(ang) * r)
            oct_pts.append((px, py))
        pygame.draw.polygon(surface, (22, 30, 44), oct_pts)
        pygame.draw.polygon(surface, (45, 64, 92), oct_pts, 3)

        # 3. Four Heavy Radial Magnetic Containment Pylons
        for ang_deg in [0, 90, 180, 270]:
            rad = math.radians(ang_deg)
            p1_x = cx + int(math.cos(rad) * (r * 0.45))
            p1_y = cy + int(math.sin(rad) * (r * 0.45))
            p2_x = cx + int(math.cos(rad) * (r + 18))
            p2_y = cy + int(math.sin(rad) * (r + 18))
            pygame.draw.line(surface, (15, 20, 30), (p1_x, p1_y), (p2_x, p2_y), 16)
            pygame.draw.line(surface, (56, 189, 248), (p1_x, p1_y), (p2_x, p2_y), 3)

        # 4. Circulating Plasma Chamber Core
        core_r = int(r * 0.50)
        pygame.draw.circle(surface, (10, 15, 24), (cx, cy), core_r)
        
        # Swirling Energy Rings
        pulse_r = int(core_r * 0.78 + math.sin(time_accum * 4.5) * 4.0)
        glow_surf = pygame.Surface((core_r * 2 + 12, core_r * 2 + 12), pygame.SRCALPHA)
        pulse_a = int(180 + 55 * math.sin(time_accum * 5.0))
        pygame.draw.circle(glow_surf, (14, 165, 233, pulse_a // 3), (core_r + 6, core_r + 6), core_r)
        pygame.draw.circle(glow_surf, (56, 189, 248, pulse_a), (core_r + 6, core_r + 6), pulse_r, 3)
        pygame.draw.circle(glow_surf, (255, 255, 255, 230), (core_r + 6, core_r + 6), 10)
        surface.blit(glow_surf, (cx - core_r - 6, cy - core_r - 6))

        # 5. Stenciled Core Label on blast pad
        lbl_core = font_card.render("REACTOR CORE 01", True, (60, 80, 110))
        surface.blit(lbl_core, lbl_core.get_rect(center=(cx, cy + r + 14)))


class SolidMachineryBlock:
    """Physical, chunky industrial factory structure with metallic plating."""
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

        # 1. Structural Drop Shadow
        pygame.draw.rect(surface, (5, 7, 12), (sx + 8, sy + 8, bw, bh), border_radius=4)

        # 2. Main Solid Titanium-Alloy Heavy Machine Chassis
        chassis_col = (24, 32, 46)
        border_col = (48, 66, 94)
        pygame.draw.rect(surface, chassis_col, (sx, sy, bw, bh), border_radius=4)
        pygame.draw.rect(surface, border_col, (sx, sy, bw, bh), 2, border_radius=4)

        # 3. Machine-specific physical components
        if self.mtype == "turbine":
            # Circular Industrial Intake Fan Housing
            tur_r = min(bw, bh) // 2 - 12
            tcx = sx + bw // 2
            tcy = sy + bh // 2
            pygame.draw.circle(surface, (14, 18, 28), (tcx, tcy), tur_r)
            pygame.draw.circle(surface, (14, 165, 233), (tcx, tcy), tur_r, 2)
            
            # Spinning Turbine Blades
            blade_ang = time_accum * 6.0
            for b_i in range(6):
                b_rad = blade_ang + b_i * (math.pi / 3.0)
                bx = tcx + int(math.cos(b_rad) * (tur_r - 4))
                by = tcy + int(math.sin(b_rad) * (tur_r - 4))
                pygame.draw.line(surface, (51, 65, 85), (tcx, tcy), (bx, by), 3)
            pygame.draw.circle(surface, (30, 41, 59), (tcx, tcy), 8)
            pygame.draw.circle(surface, COLOR_CYAN, (tcx, tcy), 3)

        elif self.mtype == "smelter":
            # Recessed Glowing Molten Metal Vat
            vat_rect = pygame.Rect(sx + 14, sy + 14, bw - 28, bh - 28)
            pygame.draw.rect(surface, (12, 16, 24), vat_rect, border_radius=3)
            # Molten Heat Surface
            m_glow = int(190 + 55 * math.sin(time_accum * 3.5 + sx * 0.01))
            pygame.draw.rect(surface, (185, 28, 28), (vat_rect.left + 4, vat_rect.top + 4, vat_rect.width - 8, vat_rect.height - 8), border_radius=2)
            pygame.draw.rect(surface, (245, 158, 11), (vat_rect.left + 8, vat_rect.top + 8, vat_rect.width - 16, vat_rect.height - 16), border_radius=2)
            # Protective Heavy Grating
            for gx in range(vat_rect.left + 12, vat_rect.right - 12, 16):
                pygame.draw.line(surface, (20, 26, 38), (gx, vat_rect.top + 2), (gx, vat_rect.bottom - 2), 3)

        elif self.mtype == "transformer":
            # High-Voltage Ceramic Insulators on Top
            for ix in range(sx + 16, sx + bw - 16, 24):
                pygame.draw.circle(surface, (14, 165, 233), (ix, sy + 10), 5)
                pygame.draw.circle(surface, COLOR_WHITE, (ix, sy + 10), 2)
            # Recessed Heat Exhaust Vents
            for vy in range(sy + 26, sy + bh - 16, 12):
                pygame.draw.line(surface, (10, 14, 22), (sx + 14, vy), (sx + bw - 14, vy), 4)

        # 4. Corner Hazard Markings & Stencil Label
        pygame.draw.rect(surface, (245, 158, 11), (sx + 4, sy + bh - 8, 18, 4))
        lbl_txt = font_card.render(self.label, True, (80, 105, 140))
        surface.blit(lbl_txt, (sx + 8, sy + 6))


class CyberFactoryArenaBackground:
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_width = world_w
        self.world_height = world_h
        self.current_sector = 0
        self.time_accum = 0.0

        # Central Super-Reactor Hub
        self.reactor = IndustrialReactor((world_w // 2, world_h // 2), size=240)

        # Solid Industrial Machinery Layout (Forming Distinct Combat Lanes)
        self.machinery = [
            # North Turbine District (Upper Combat Belt)
            SolidMachineryBlock((480, 180, 280, 140), mtype="turbine", label="TURBINE-N1"),
            SolidMachineryBlock((1640, 180, 280, 140), mtype="turbine", label="TURBINE-N2"),

            # South Heavy Smelter Array (Lower Combat Belt)
            SolidMachineryBlock((480, 1080, 280, 140), mtype="smelter", label="SMELTER-S1"),
            SolidMachineryBlock((1640, 1080, 280, 140), mtype="smelter", label="SMELTER-S2"),

            # West & East Transformer Substations (Flanking Lanes)
            SolidMachineryBlock((180, 580, 160, 240), mtype="transformer", label="XFORM-WEST"),
            SolidMachineryBlock((2060, 580, 160, 240), mtype="transformer", label="XFORM-EAST"),

            # Tactical Cover Bunkers (Midfield Dogfight Obstacles)
            SolidMachineryBlock((900, 360, 140, 90), mtype="transformer", label="COV-01"),
            SolidMachineryBlock((1360, 360, 140, 90), mtype="transformer", label="COV-02"),
            SolidMachineryBlock((900, 950, 140, 90), mtype="transformer", label="COV-03"),
            SolidMachineryBlock((1360, 950, 140, 90), mtype="transformer", label="COV-04"),
        ]

        # Industrial Heavy Pipe & Conduit Duct Network
        self.pipe_conduits = [
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

        # Industrial Stenciled Floor Signage & Markings (World Space)
        self.floor_stencils = [
            ("SECTOR 01: ADVANCED FABRICATION CORE", (1200, 480)),
            ("CAUTION: HIGH-VOLTAGE MAGNETIC CONFINEMENT", (1200, 920)),
            ("<< CARGO CORRIDOR WEST", (520, 700)),
            ("CARGO CORRIDOR EAST >>", (1880, 700)),
        ]

        # Floor Walkway Grates with Under-Pit Depth
        self.floor_grates = [
            (720, 560, 120, 60),
            (1560, 560, 120, 60),
            (720, 780, 120, 60),
            (1560, 780, 120, 60),
        ]

        # Heavy Cargo Pallets (Industrial Debris / Detail)
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

        # Future Enemy Spawn Airlocks (Spatial Entry Preparation)
        self.spawn_airlocks = [
            (1200 - 90, 30, 180, 26, "NORTH AIRLOCK"),
            (1200 - 90, 1400 - 56, 180, 26, "SOUTH AIRLOCK"),
            (30, 700 - 90, 26, 180, "WEST AIRLOCK"),
            (2400 - 56, 700 - 90, 26, 180, "EAST AIRLOCK"),
        ]

    def set_sector(self, sector_idx: int):
        self.current_sector = sector_idx % len(SECTORS)

    def update(self, dt: float):
        self.time_accum += dt

    def draw_menu_backdrop(self, surface: pygame.Surface):
        """Renders clean atmospheric background strictly for screen-space menus."""
        vw, vh = surface.get_size()
        surface.fill((10, 14, 23))
        # Subtle ambient grid
        for gy in range(0, vh, 80):
            pygame.draw.line(surface, (14, 20, 32), (0, gy), (vw, gy), 1)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders 2D Cyber Factory Arena in world space with camera viewport offset."""
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # =====================================================================
        # 1. SOLID INDUSTRIAL STEEL FACTORY FLOOR
        # =====================================================================
        surface.fill((14, 18, 28))

        # Modular Metallic Floor Plates (Alternating Tone Tiles)
        tile_size = 160
        start_x = int(ox // tile_size) * tile_size
        start_y = int(oy // tile_size) * tile_size
        end_x = start_x + vw + tile_size * 2
        end_y = start_y + vh + tile_size * 2

        seam_col = (20, 27, 40)
        rivet_col = (30, 42, 60)

        # Draw Alternating Subtle Plates & Seams
        for gx in range(start_x, end_x, tile_size):
            for gy in range(start_y, end_y, tile_size):
                if 0 <= gx <= self.world_width and 0 <= gy <= self.world_height:
                    sx = int(round(gx - ox))
                    sy = int(round(gy - oy))
                    # Checker pattern of steel tone
                    is_alt = ((gx // tile_size) + (gy // tile_size)) % 2 == 0
                    if is_alt:
                        pygame.draw.rect(surface, (16, 21, 32), (sx, sy, tile_size, tile_size))
                    pygame.draw.rect(surface, seam_col, (sx, sy, tile_size, tile_size), 1)
                    # Corner Bolt Rivets
                    pygame.draw.rect(surface, rivet_col, (sx - 2, sy - 2, 4, 4))

        # =====================================================================
        # 2. FLOOR VENTILATION GRATES (Recessed dark under-pits)
        # =====================================================================
        for rx, ry, rw, rh in self.floor_grates:
            rsx = int(round(rx - ox))
            rsy = int(round(ry - oy))
            if -rw <= rsx <= vw + rw and -rh <= rsy <= vh + rh:
                pygame.draw.rect(surface, (6, 9, 14), (rsx, rsy, rw, rh), border_radius=3)
                pygame.draw.rect(surface, (30, 42, 62), (rsx, rsy, rw, rh), 2, border_radius=3)
                for gx in range(rsx + 6, rsx + rw - 6, 8):
                    pygame.draw.line(surface, (18, 25, 38), (gx, rsy + 3), (gx, rsy + rh - 3), 2)

        # =====================================================================
        # 3. STENCILED INDUSTRIAL FACTORY FLOOR SIGNAGE
        # =====================================================================
        for st_text, st_pos in self.floor_stencils:
            sx = int(round(st_pos[0] - ox))
            sy = int(round(st_pos[1] - oy))
            if -200 <= sx <= vw + 200 and -50 <= sy <= vh + 50:
                lbl_st = font_card.render(st_text, True, (35, 48, 68))
                surface.blit(lbl_st, lbl_st.get_rect(center=(sx, sy)))

        # =====================================================================
        # 4. HEAVY INDUSTRIAL POWER PIPES & CONDUIT DUCTS
        # =====================================================================
        pulse_alpha = int(120 + 50 * math.sin(self.time_accum * 3.2))
        conduit_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        conduit_glow = (14, 165, 233, pulse_alpha // 2)

        for p1, p2 in self.pipe_conduits:
            sp1 = (int(round(p1[0] - ox)), int(round(p1[1] - oy)))
            sp2 = (int(round(p2[0] - ox)), int(round(p2[1] - oy)))
            # Heavy 12px Conduit Trench & Steel Pipe
            pygame.draw.line(surface, (8, 12, 18), sp1, sp2, 12)
            pygame.draw.line(surface, (28, 38, 54), sp1, sp2, 8)
            pygame.draw.line(surface, (45, 62, 88), sp1, sp2, 2)
            # Glowing Core Line
            pygame.draw.line(conduit_surf, conduit_glow, sp1, sp2, 2)
        surface.blit(conduit_surf, (0, 0))

        # =====================================================================
        # 5. SOLID MACHINERY UNITS & CENTRAL POWER REACTOR
        # =====================================================================
        # Render Factory Machinery Units
        for m in self.machinery:
            m.draw(surface, camera_offset, self.time_accum)

        # Render Central Super-Reactor
        self.reactor.draw(surface, camera_offset, self.time_accum)

        # Render Industrial Cargo Pallets
        for px, py, pw, ph in self.cargo_pallets:
            psx = int(round(px - ox))
            psy = int(round(py - oy))
            if -pw <= psx <= vw + pw and -ph <= psy <= vh + ph:
                pygame.draw.rect(surface, (6, 9, 14), (psx + 4, psy + 4, pw, ph), border_radius=2)
                pygame.draw.rect(surface, (28, 36, 52), (psx, psy, pw, ph), border_radius=2)
                pygame.draw.rect(surface, (50, 68, 96), (psx, psy, pw, ph), 1, border_radius=2)
                pygame.draw.line(surface, (245, 158, 11), (psx + 4, psy + ph // 2), (psx + pw - 4, psy + ph // 2), 2)

        # =====================================================================
        # 6. ENEMY SPAWN INTAKE AIRLOCKS (4 Border Gates)
        # =====================================================================
        for ax, ay, aw, ah, alabel in self.spawn_airlocks:
            asx = int(round(ax - ox))
            asy = int(round(ay - oy))
            if -aw <= asx <= vw + aw and -ah <= asy <= vh + ah:
                pygame.draw.rect(surface, (10, 14, 20), (asx, asy, aw, ah), border_radius=4)
                pygame.draw.rect(surface, (239, 68, 68), (asx, asy, aw, ah), 2, border_radius=4)
                # Diagonal Hazard Stripes
                for zx in range(asx + 4, asx + aw - 8, 16):
                    pygame.draw.line(surface, (245, 158, 11), (zx, asy + ah - 4), (zx + 8, asy + 4), 2)

        # =====================================================================
        # 7. PERIMETER HIGH-VOLTAGE LASER CONTAINMENT BARRIER
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


ParallaxBackground = CyberFactoryArenaBackground
PowerReactor = IndustrialReactor
FactoryMachineryUnit = SolidMachineryBlock
