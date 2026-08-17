"""
================================================================================
                    DRONE HUNTER 2D - PARALLAX BACKGROUNDS
================================================================================
Multi-layer dynamic 2D parallax backgrounds for all 5 sectors:
- Sector 0: Megacity Skyline (Cyberpunk skyscrapers & neon searchlights)
- Sector 1: Cyber Factory Core (Smokestacks & molten lava channels)
- Sector 2: Orbital Space Citadel (Nebulas, starfields, & orbital citadels)
- Sector 3: Stormy Ocean Battlescape (Ocean swells & lightning storms)
- Sector 4: Neon Sun Desert Wasteland (Sand dunes & cyber pyramids)
"""

import random
import math
import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.data.game_data import SECTORS

class CloudLayer:
    def __init__(self, count: int = 6):
        self.clouds = []
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(20, 220)
            speed = random.uniform(15, 35)
            w = random.randint(140, 280)
            h = random.randint(40, 80)
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            color = (255, 255, 255, 25)
            pygame.draw.ellipse(surf, color, (0, 0, w, h))
            self.clouds.append([x, y, speed, w, h, surf])

    def update(self, dt: float):
        for c in self.clouds:
            c[0] -= c[2] * dt
            if c[0] < -c[3]:
                c[0] = SCREEN_WIDTH + random.randint(20, 100)
                c[1] = random.randint(20, 220)

    def draw(self, surface: pygame.Surface):
        for c in self.clouds:
            surface.blit(c[5], (c[0], c[1]))


class ParallaxBackground:
    def __init__(self):
        self.current_sector = 0
        self.stars = []
        for _ in range(90):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, int(SCREEN_HEIGHT * 0.75))
            speed = random.uniform(20, 55)
            radius = random.choice([1, 1, 2, 2])
            brightness = random.randint(160, 255)
            self.stars.append([x, y, speed, radius, brightness])

        self.cloud_layer = CloudLayer(count=8)
        self.mountain_scroll = 0.0
        self.city_scroll = 0.0
        self.ground_scroll = 0.0
        self.time_accum = 0.0

    def set_sector(self, sector_idx: int):
        self.current_sector = sector_idx % len(SECTORS)

    def update(self, dt: float):
        self.time_accum += dt
        self.mountain_scroll = (self.mountain_scroll + 40.0 * dt) % SCREEN_WIDTH
        self.city_scroll = (self.city_scroll + 80.0 * dt) % SCREEN_WIDTH
        self.ground_scroll = (self.ground_scroll + 140.0 * dt) % SCREEN_WIDTH

        for s in self.stars:
            s[0] -= s[2] * dt
            if s[0] < 0:
                s[0] = SCREEN_WIDTH
                s[1] = random.randint(0, int(SCREEN_HEIGHT * 0.75))

        self.cloud_layer.update(dt)

    def draw(self, surface: pygame.Surface):
        # Base Sky Gradient
        if self.current_sector == 0:
            top_c = (15, 23, 42)
            bot_c = (30, 41, 59)
        elif self.current_sector == 1:
            top_c = (35, 15, 20)
            bot_c = (60, 25, 25)
        elif self.current_sector == 2:
            top_c = (8, 5, 20)
            bot_c = (25, 10, 40)
        elif self.current_sector == 3:
            top_c = (10, 25, 45)
            bot_c = (20, 45, 75)
        else: # Sector 4: Desert Wasteland
            top_c = (45, 20, 15)
            bot_c = (80, 35, 20)

        pygame.draw.rect(surface, top_c, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(surface, bot_c, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Stars & Nebulas
        for s in self.stars:
            col = (s[4], s[4], s[4]) if self.current_sector != 1 else (s[4], int(s[4] * 0.8), int(s[4] * 0.6))
            pygame.draw.circle(surface, col, (int(s[0]), int(s[1])), s[3])

        # Clouds
        if self.current_sector in (0, 3):
            self.cloud_layer.draw(surface)

        # Scrolling Midground Structures
        self._draw_midground(surface)

        # Ground Floor Layer
        self._draw_ground(surface)

    def _draw_midground(self, surface: pygame.Surface):
        offset = int(self.city_scroll)
        if self.current_sector == 0: # Megacity Buildings
            b_col = (20, 28, 48)
            for i in range(-1, int(SCREEN_WIDTH / 90) + 2):
                bx = i * 90 - (offset % 90)
                bh = 180 + (i * 37) % 140
                pygame.draw.rect(surface, b_col, (bx, SCREEN_HEIGHT - 90 - bh, 80, bh))
                # Glowing windows
                for wy in range(SCREEN_HEIGHT - 70 - bh, SCREEN_HEIGHT - 100, 24):
                    pygame.draw.rect(surface, (14, 165, 233, 180), (bx + 12, wy, 8, 12))
                    pygame.draw.rect(surface, (245, 158, 11, 180), (bx + 40, wy, 8, 12))

        elif self.current_sector == 1: # Factory Smokestacks
            f_col = (40, 30, 35)
            for i in range(-1, int(SCREEN_WIDTH / 110) + 2):
                fx = i * 110 - (offset % 110)
                fh = 160 + (i * 43) % 110
                pygame.draw.rect(surface, f_col, (fx, SCREEN_HEIGHT - 90 - fh, 65, fh))
                pygame.draw.rect(surface, (239, 68, 68), (fx + 10, SCREEN_HEIGHT - 85 - fh, 45, 6))

        elif self.current_sector == 2: # Space Citadel Spires
            c_col = (30, 20, 50)
            for i in range(-1, int(SCREEN_WIDTH / 140) + 2):
                cx = i * 140 - (offset % 140)
                ch = 220 + (i * 51) % 160
                pts = [(cx + 40, SCREEN_HEIGHT - 90 - ch), (cx + 80, SCREEN_HEIGHT - 90), (cx, SCREEN_HEIGHT - 90)]
                pygame.draw.polygon(surface, c_col, pts)
                pygame.draw.circle(surface, (217, 70, 239), (cx + 40, SCREEN_HEIGHT - 88 - ch), 6)

        elif self.current_sector == 3: # Ocean Waves
            wave_col = (15, 40, 70)
            for i in range(-1, int(SCREEN_WIDTH / 100) + 2):
                wx = i * 100 - (offset % 100)
                wy = SCREEN_HEIGHT - 160 + math.sin((wx + self.time_accum * 120.0) * 0.02) * 20.0
                pygame.draw.ellipse(surface, wave_col, (wx, wy, 120, 60))

        else: # Desert Cyber Pyramids
            p_col = (65, 30, 20)
            for i in range(-1, int(SCREEN_WIDTH / 160) + 2):
                px = i * 160 - (offset % 160)
                ph = 200 + (i * 61) % 130
                pts = [(px + 80, SCREEN_HEIGHT - 90 - ph), (px + 160, SCREEN_HEIGHT - 90), (px, SCREEN_HEIGHT - 90)]
                pygame.draw.polygon(surface, p_col, pts)
                pygame.draw.line(surface, (245, 158, 11), (px + 80, SCREEN_HEIGHT - 90 - ph), (px + 80, SCREEN_HEIGHT - 90), 2)

    def _draw_ground(self, surface: pygame.Surface):
        ground_h = 85
        gy = SCREEN_HEIGHT - ground_h
        if self.current_sector == 0: g_col = (15, 23, 42)
        elif self.current_sector == 1: g_col = (30, 20, 25)
        elif self.current_sector == 2: g_col = (20, 15, 35)
        elif self.current_sector == 3: g_col = (10, 30, 55)
        else: g_col = (45, 22, 15)

        pygame.draw.rect(surface, g_col, (0, gy, SCREEN_WIDTH, ground_h))
        pygame.draw.line(surface, (56, 189, 248) if self.current_sector != 4 else (245, 158, 11), (0, gy), (SCREEN_WIDTH, gy), 2)
