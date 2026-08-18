"""
================================================================================
            DRONE HUNTER 2D - CYBER FACTORY ENVIRONMENT SYSTEM
================================================================================
Integrated 2D Cyber Factory Asset & Environment System (Phase 1.7C):
- Loads and caches authentic 2D Cyber Factory sprite assets:
  * Floor: floor/floor_01.png, floor/floor_grate.png
  * Reactor: reactors/reactor_01.png
  * Machinery: machinery/turbine_01.png, machinery/generator_01.png
  * Structures: structures/wall_01.png
  * Pipes: pipes/pipe_straight.png, pipes/pipe_corner.png
  * Barriers: barriers/energy_barrier_blue.png
  * Props: props/crate_01.png
  * Vents: vents/vent_01.png
  * Lights: lights/warning_beacon.png
  * Hazards: hazards/hazard_stripe_01.png
- Modular world-space layout across 2400x1400 arena
- Viewport frustum culling and high-performance surface caching
- Strict world-space coordinate translation
"""

import os
import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_WHITE
)
from src.ui.font_manager import font_card

class CyberFactoryAssetManager:
    """Cached loader for Cyber Factory 2D environment assets."""
    _instance = None

    def __init__(self):
        self._cache = {}
        self.asset_root = self._resolve_asset_dir()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _resolve_asset_dir(self) -> str:
        # Search possible asset paths
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "environment", "cyber_factory"),
            os.path.join(os.getcwd(), "drone_hunter_pc", "assets", "environment", "cyber_factory"),
            os.path.join(os.getcwd(), "assets", "environment", "cyber_factory"),
            os.path.join("d:", os.sep, "Drone_Hunter", "drone_hunter_pc", "assets", "environment", "cyber_factory"),
            os.path.join("d:", os.sep, "Drone_Hunter", "Drone_Hunter_Cyber_Factory_Assets_v01"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return candidates[0]

    def get_image(self, rel_path: str, fallback_size: tuple[int, int] = (64, 64)) -> pygame.Surface:
        """Retrieves cached image or generates safe fallback surface."""
        if rel_path in self._cache:
            return self._cache[rel_path]

        full_path = os.path.join(self.asset_root, rel_path)
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path).convert_alpha()
                self._cache[rel_path] = img
                return img
            except Exception:
                pass

        # Fallback procedural surface if image missing
        fb = pygame.Surface(fallback_size, pygame.SRCALPHA)
        pygame.draw.rect(fb, (25, 33, 48), (0, 0, fallback_size[0], fallback_size[1]), border_radius=4)
        pygame.draw.rect(fb, (45, 62, 90), (0, 0, fallback_size[0], fallback_size[1]), 2, border_radius=4)
        self._cache[rel_path] = fb
        return fb


class FactoryFloor:
    """Pre-rendered modular factory floor using 2D sprite tiles."""
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_w = world_w
        self.world_h = world_h
        self.assets = CyberFactoryAssetManager.get_instance()

        # Load tile assets
        self.tile_floor = self.assets.get_image("floor/floor_01.png", (90, 77))
        self.tile_grate = self.assets.get_image("floor/floor_grate.png", (90, 75))
        self.hazard_img = self.assets.get_image("hazards/hazard_stripe_01.png", (135, 70))

        self.tw, self.th = self.tile_floor.get_size()

        # Deterministic grate coordinates
        self.grate_zones = [
            (720, 520, 140, 60),
            (1540, 520, 140, 60),
            (720, 830, 140, 60),
            (1540, 830, 140, 60),
        ]

        # Industrial Hazard Strip Lines (Assembly Corridors)
        self.hazard_lines = [
            (480, 340), (620, 340), (1640, 340), (1780, 340),
            (480, 1020), (620, 1020), (1640, 1020), (1780, 1020),
            (220, 840), (2060, 840),
        ]

        # Industrial Stenciled Floor Text
        self.floor_stencils = [
            ("SECTOR 01: ADVANCED FABRICATION CORE", (world_w // 2, 480)),
            ("CAUTION: HIGH-VOLTAGE MAGNETIC CONFINEMENT", (world_w // 2, 920)),
            ("<< CARGO INTAKE WEST", (480, 700)),
            ("LOGISTICS TERMINAL EAST >>", (1920, 700)),
        ]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float]):
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # 1. Base Dark Slate Foundation
        surface.fill((14, 18, 26))

        # 2. Viewport-Culled Floor Sprite Tiling
        start_gx = int(max(0.0, ox) // self.tw) * self.tw
        start_gy = int(max(0.0, oy) // self.th) * self.th
        end_gx = min(self.world_w, int(ox + vw + self.tw))
        end_gy = min(self.world_h, int(oy + vh + self.th))

        for gx in range(start_gx, end_gx + self.tw, self.tw):
            for gy in range(start_gy, end_gy + self.th, self.th):
                if 0 <= gx < self.world_w and 0 <= gy < self.world_h:
                    sx = int(round(gx - ox))
                    sy = int(round(gy - oy))
                    # Deterministic grate pattern
                    is_grate = ((gx // self.tw) + (gy // self.th)) % 7 == 0
                    if is_grate:
                        surface.blit(self.tile_grate, (sx, sy))
                    else:
                        surface.blit(self.tile_floor, (sx, sy))

        # 3. Hazard Stripe Markings
        hw, hh = self.hazard_img.get_size()
        for hx, hy in self.hazard_lines:
            hsx = int(round(hx - ox))
            hsy = int(round(hy - oy))
            if -hw <= hsx <= vw + hw and -hh <= hsy <= vh + hh:
                surface.blit(self.hazard_img, (hsx, hsy))

        # 4. Stenciled Industrial Signage
        for st_text, st_pos in self.floor_stencils:
            sx = int(round(st_pos[0] - ox))
            sy = int(round(st_pos[1] - oy))
            if -250 <= sx <= vw + 250 and -50 <= sy <= vh + 50:
                lbl = font_card.render(st_text, True, (40, 54, 76))
                surface.blit(lbl, lbl.get_rect(center=(sx, sy)))


class PowerReactor:
    """Central High-Output Industrial Power Reactor using reactor_01.png."""
    def __init__(self, pos: tuple[float, float]):
        self.pos = pygame.Vector2(pos)
        self.assets = CyberFactoryAssetManager.get_instance()
        self.reactor_img = self.assets.get_image("reactors/reactor_01.png", (215, 245))
        self.beacon_img = self.assets.get_image("lights/warning_beacon.png", (100, 90))
        self.rw, self.rh = self.reactor_img.get_size()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        cx = int(round(self.pos.x - ox))
        cy = int(round(self.pos.y - oy))

        rx = cx - self.rw // 2
        ry = cy - self.rh // 2

        if not (-self.rw <= rx <= vw and -self.rh <= ry <= vh):
            return

        # 1. Reinforced Square Concrete Foundation Pad & Drop Shadow
        pad_w, pad_h = self.rw + 40, self.rh + 30
        pad_rect = pygame.Rect(cx - pad_w // 2, cy - pad_h // 2, pad_w, pad_h)
        pygame.draw.rect(surface, (10, 14, 20), pad_rect, border_radius=6)
        pygame.draw.rect(surface, (28, 38, 54), pad_rect, 2, border_radius=6)

        # 2. Main Reactor Sprite
        surface.blit(self.reactor_img, (rx, ry))

        # 3. Dynamic Cyan Energy Aura Shimmer (Subtle 2D Lighting)
        pulse_a = int(140 + 45 * math.sin(time_accum * 4.5))
        aura_r = 45
        aura_surf = pygame.Surface((aura_r * 2 + 10, aura_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (14, 165, 233, pulse_a // 3), (aura_r + 5, aura_r + 5), aura_r)
        pygame.draw.circle(aura_surf, (56, 189, 248, pulse_a), (aura_r + 5, aura_r + 5), int(aura_r * 0.75), 2)
        surface.blit(aura_surf, (cx - aura_r - 5, cy - aura_r - 5))

        # 4. Stenciled Reactor Blast Pad Signage
        lbl = font_card.render("REACTOR CORE 01", True, (60, 82, 112))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy + self.rh // 2 + 14)))


class FactoryMachineryUnit:
    """Industrial Factory Machinery (Turbine / Generator) using asset sprites."""
    def __init__(self, pos: tuple[float, float], mtype: str = "turbine", label: str = "FAB-01"):
        self.pos = pygame.Vector2(pos)
        self.mtype = mtype
        self.label = label
        self.assets = CyberFactoryAssetManager.get_instance()

        if self.mtype == "turbine":
            self.image = self.assets.get_image("machinery/turbine_01.png", (130, 127))
        else:
            self.image = self.assets.get_image("machinery/generator_01.png", (197, 127))

        self.vent_img = self.assets.get_image("vents/vent_01.png", (95, 90))
        self.beacon_img = self.assets.get_image("lights/warning_beacon.png", (100, 90))
        self.w, self.h = self.image.get_size()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        sx = int(round(self.pos.x - ox))
        sy = int(round(self.pos.y - oy))

        if not (-self.w <= sx <= vw and -self.h <= sy <= vh):
            return

        # 1. Structural Drop Shadow
        pygame.draw.rect(surface, (6, 8, 12), (sx + 6, sy + 6, self.w, self.h), border_radius=4)

        # 2. Main Machinery Sprite
        surface.blit(self.image, (sx, sy))

        # 3. Warning Beacon Light (Subtle blinking amber LED)
        is_lit = int((time_accum * 3.5) + sx) % 2 == 0
        b_col = (245, 158, 11) if is_lit else (60, 40, 10)
        pygame.draw.circle(surface, b_col, (sx + self.w - 12, sy + 12), 4)

        # 4. Stencil Machine Label
        lbl = font_card.render(self.label, True, (75, 100, 134))
        surface.blit(lbl, (sx + 8, sy - 18))


class WallStructure:
    """Physical industrial facility boundary wall using wall_01.png."""
    def __init__(self, pos: tuple[float, float]):
        self.pos = pygame.Vector2(pos)
        self.assets = CyberFactoryAssetManager.get_instance()
        self.image = self.assets.get_image("structures/wall_01.png", (157, 95))
        self.w, self.h = self.image.get_size()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float]):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        sx = int(round(self.pos.x - ox))
        sy = int(round(self.pos.y - oy))

        if -self.w <= sx <= vw and -self.h <= sy <= vh:
            pygame.draw.rect(surface, (6, 8, 12), (sx + 6, sy + 6, self.w, self.h), border_radius=3)
            surface.blit(self.image, (sx, sy))


class PipeNetwork:
    """Industrial Pipe & Conduit Network using pipe_straight.png and pipe_corner.png."""
    def __init__(self):
        self.assets = CyberFactoryAssetManager.get_instance()
        self.pipe_straight = self.assets.get_image("pipes/pipe_straight.png", (110, 85))
        self.pipe_corner = self.assets.get_image("pipes/pipe_corner.png", (125, 105))

        # Strategic pipe placements connecting machinery hubs to reactor
        self.pipe_positions = [
            (480 + 130, 240, False),
            (1640 - 110, 240, False),
            (480 + 130, 1140, False),
            (1640 - 110, 1140, False),
            (320, 680, False),
            (1940, 680, False),
            (1150, 420, True),
            (1150, 940, True),
        ]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        for px, py, is_corner in self.pipe_positions:
            psx = int(round(px - ox))
            psy = int(round(py - oy))
            img = self.pipe_corner if is_corner else self.pipe_straight
            pw, ph = img.get_size()
            if -pw <= psx <= vw and -ph <= psy <= vh:
                surface.blit(img, (psx, psy))


class EnergyBarrier:
    """High-tech blue energy barrier using energy_barrier_blue.png."""
    def __init__(self, pos: tuple[float, float]):
        self.pos = pygame.Vector2(pos)
        self.assets = CyberFactoryAssetManager.get_instance()
        self.image = self.assets.get_image("barriers/energy_barrier_blue.png", (160, 105))
        self.w, self.h = self.image.get_size()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float], time_accum: float):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        sx = int(round(self.pos.x - ox))
        sy = int(round(self.pos.y - oy))

        if -self.w <= sx <= vw and -self.h <= sy <= vh:
            surface.blit(self.image, (sx, sy))


class CrateCluster:
    """Industrial alloy shipping crates using crate_01.png."""
    def __init__(self):
        self.assets = CyberFactoryAssetManager.get_instance()
        self.crate_img = self.assets.get_image("props/crate_01.png", (90, 80))
        self.cw, self.ch = self.crate_img.get_size()

        self.positions = [
            (380, 460), (1980, 460),
            (840, 230), (1520, 230),
            (840, 1130), (1520, 1130),
        ]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float]):
        ox, oy = camera_offset
        vw, vh = surface.get_size()
        for cx, cy in self.positions:
            csx = int(round(cx - ox))
            csy = int(round(cy - oy))
            if -self.cw <= csx <= vw and -self.ch <= csy <= vh:
                surface.blit(self.crate_img, (csx, csy))


class CyberFactoryEnvironment:
    """Master Cyber Factory Environment Manager combining all integrated assets."""
    def __init__(self, world_w: int = WORLD_WIDTH, world_h: int = WORLD_HEIGHT):
        self.world_w = world_w
        self.world_h = world_h
        self.time_accum = 0.0

        # 1. Floor System
        self.floor = FactoryFloor(world_w, world_h)

        # 2. Central Power Reactor
        self.reactor = PowerReactor((world_w // 2, world_h // 2))

        # 3. Factory Machinery (Turbines and Generators)
        self.machinery = [
            # North Turbines (Upper Combat Belt)
            FactoryMachineryUnit((480, 180), mtype="turbine", label="TURBINE-N1"),
            FactoryMachineryUnit((1640, 180), mtype="turbine", label="TURBINE-N2"),

            # South Generators (Lower Combat Belt)
            FactoryMachineryUnit((480, 1080), mtype="generator", label="GEN-S1"),
            FactoryMachineryUnit((1640, 1080), mtype="generator", label="GEN-S2"),

            # Flanking Power Units
            FactoryMachineryUnit((180, 580), mtype="generator", label="GEN-WEST"),
            FactoryMachineryUnit((2060, 580), mtype="generator", label="GEN-EAST"),
        ]

        # 4. Structural Boundary Walls
        self.walls = [
            WallStructure((900, 360)),
            WallStructure((1360, 360)),
            WallStructure((900, 950)),
            WallStructure((1360, 950)),
        ]

        # 5. Pipe Network
        self.pipes = PipeNetwork()

        # 6. Tactical Energy Barriers
        self.barriers = [
            EnergyBarrier((740, 680)),
            EnergyBarrier((1500, 680)),
        ]

        # 7. Cargo Crates & Props
        self.crates = CrateCluster()

        # 8. Border Spawn Airlocks (4 Perimeter Gates)
        self.spawn_airlocks = [
            (world_w // 2 - 90, 24, 180, 26, "NORTH AIRLOCK"),
            (world_w // 2 - 90, world_h - 50, 180, 26, "SOUTH AIRLOCK"),
            (24, world_h // 2 - 90, 26, 180, "WEST AIRLOCK"),
            (world_w - 50, world_h // 2 - 90, 26, 180, "EAST AIRLOCK"),
        ]

    def update(self, dt: float):
        self.time_accum += dt

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        """Renders the complete 2D Cyber Factory facility with full camera translation."""
        ox, oy = camera_offset
        vw, vh = surface.get_size()

        # 1. Modular Floor Tiles & Hazard Markings
        self.floor.draw(surface, camera_offset)

        # 2. Pipe Network (Infrastructure layer)
        self.pipes.draw(surface, camera_offset, self.time_accum)

        # 3. Heavy Factory Machinery
        for m in self.machinery:
            m.draw(surface, camera_offset, self.time_accum)

        # 4. Structural Walls
        for w in self.walls:
            w.draw(surface, camera_offset)

        # 5. Tactical Energy Barriers
        for b in self.barriers:
            b.draw(surface, camera_offset, self.time_accum)

        # 6. Central Super-Reactor
        self.reactor.draw(surface, camera_offset, self.time_accum)

        # 7. Industrial Crates & Props
        self.crates.draw(surface, camera_offset)

        # 8. Border Spawn Airlocks
        for ax, ay, aw, ah, alabel in self.spawn_airlocks:
            asx = int(round(ax - ox))
            asy = int(round(ay - oy))
            if -aw <= asx <= vw + aw and -ah <= asy <= vh + ah:
                pygame.draw.rect(surface, (10, 14, 20), (asx, asy, aw, ah), border_radius=4)
                pygame.draw.rect(surface, (239, 68, 68), (asx, asy, aw, ah), 2, border_radius=4)
                for zx in range(asx + 4, asx + aw - 8, 16):
                    pygame.draw.line(surface, (217, 119, 6), (zx, asy + ah - 4), (zx + 8, asy + 4), 2)

        # 9. Perimeter Security Barrier
        pad = 24.0
        bx1, by1 = int(round(pad - ox)), int(round(pad - oy))
        bx2, by2 = int(round((self.world_w - pad) - ox)), int(round((self.world_h - pad) - oy))

        b_alpha = int(140 + 40 * math.sin(self.time_accum * 4.0))
        barrier_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
        b_col = (14, 165, 233, b_alpha)

        if 0 <= bx1 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx1, max(0, by1)), (bx1, min(vh, by2)), 2)
        if 0 <= bx2 <= vw:
            pygame.draw.line(barrier_surf, b_col, (bx2, max(0, by1)), (bx2, min(vh, by2)), 2)
        if 0 <= by1 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by1), (min(vw, bx2), by1), 2)
        if 0 <= by2 <= vh:
            pygame.draw.line(barrier_surf, b_col, (max(0, bx1), by2), (min(vw, bx2), by2), 2)

        surface.blit(barrier_surf, (0, 0))
