"""
================================================================================
                    DRONE HUNTER 2D - PARTICLE EFFECTS & WEATHER
================================================================================
High-performance 2D particle simulation, explosive shockwaves, lightning arcs,
floating combat text, and dynamic atmospheric weather with camera offset support.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_CRIMSON, COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK,
    COLOR_WHITE, COLOR_TESLA, COLOR_CLUSTER
)

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float],
                 color: tuple[int, int, int], radius: float, lifetime: float, is_spark: bool = False):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.color = color
        self.radius = radius
        self.start_radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.is_spark = is_spark

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        
        self.pos += self.vel * dt
        if not self.is_spark:
            self.vel *= (1.0 - 2.5 * dt)
        
        pct = self.lifetime / self.max_lifetime
        self.radius = max(1.0, self.start_radius * pct)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        r = int(self.radius)
        if r > 0:
            ox, oy = camera_offset
            px = int(round(self.pos.x - ox))
            py = int(round(self.pos.y - oy))
            pygame.draw.circle(surface, self.color, (px, py), r)


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float], text: str, color: tuple[int, int, int], font_size: int = 18):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(random.uniform(-15.0, 15.0), -65.0)
        self.color = color
        self.lifetime = 0.85
        self.max_lifetime = 0.85
        from src.ui.font_manager import safe_create_font
        self.font = safe_create_font("Consolas", font_size, bold=True)
        self.rendered_text = self.font.render(text, True, color)

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos += self.vel * dt
        self.vel.y += 20.0 * dt

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        pct = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        alpha = int(255 * pct)
        if alpha > 10:
            ox, oy = camera_offset
            surf = self.rendered_text.copy()
            surf.set_alpha(alpha)
            px = int(round(self.pos.x - ox - surf.get_width() // 2))
            py = int(round(self.pos.y - oy))
            surface.blit(surf, (px, py))


class LightningArc:
    def __init__(self, start_pos: tuple[float, float], end_pos: tuple[float, float], color: tuple[int, int, int] = COLOR_TESLA):
        self.start = pygame.Vector2(start_pos)
        self.end = pygame.Vector2(end_pos)
        self.color = color
        self.lifetime = 0.18
        self.max_lifetime = 0.18
        self.points = self._generate_points()

    def _generate_points(self) -> list[tuple[float, float]]:
        pts = [self.start]
        dist = (self.end - self.start).length()
        segs = max(3, int(dist / 28.0))
        for i in range(1, segs):
            pct = i / segs
            inter = self.start.lerp(self.end, pct)
            offset = pygame.Vector2(random.uniform(-14.0, 14.0), random.uniform(-14.0, 14.0))
            pts.append(inter + offset)
        pts.append(self.end)
        return pts

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        if len(self.points) > 1:
            ox, oy = camera_offset
            screen_pts = [(int(round(p.x - ox)), int(round(p.y - oy))) for p in self.points]
            pygame.draw.lines(surface, self.color, False, screen_pts, 3)
            pygame.draw.lines(surface, COLOR_WHITE, False, screen_pts, 1)


class ParticleManager:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()
        self.lightning_arcs: list[LightningArc] = []
        self.weather_particles = []

    def spawn_spark(self, pos: tuple[float, float], count: int = 8, color: tuple[int, int, int] = COLOR_CYAN):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(140.0, 360.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(1.5, 3.5)
            life = random.uniform(0.12, 0.28)
            self.particles.add(Particle(pos, vel, color, rad, life, is_spark=True))

    def spawn_explosion(self, pos: tuple[float, float], count: int = 24, color: tuple[int, int, int] = COLOR_GOLD):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, 320.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(3.0, 7.0)
            life = random.uniform(0.25, 0.55)
            self.particles.add(Particle(pos, vel, color, rad, life))

    def spawn_enemy_death(self, pos: tuple[float, float], color: tuple[int, int, int]):
        self.spawn_explosion(pos, count=28, color=color)
        self.spawn_spark(pos, count=16, color=COLOR_WHITE)

    def spawn_boss_explosion(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=55, color=COLOR_GOLD)
        self.spawn_explosion(pos, count=35, color=COLOR_CRIMSON)
        self.spawn_spark(pos, count=30, color=COLOR_WHITE)

    def spawn_drone_trail(self, pos: tuple[float, float]):
        vel = (random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0))
        self.particles.add(Particle(pos, vel, COLOR_CYAN, radius=3.5, lifetime=0.18))

    def spawn_lightning_arc(self, start_pos: tuple[float, float], end_pos: tuple[float, float], color: tuple[int, int, int] = COLOR_TESLA):
        self.lightning_arcs.append(LightningArc(start_pos, end_pos, color))

    def spawn_cluster_explosion(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=30, color=COLOR_CLUSTER)

    def spawn_emp_shockwave(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=45, color=COLOR_CYAN)

    def spawn_shockwave(self, pos: tuple[float, float], max_r: int = 500, color: tuple[int, int, int] = (250, 204, 21)):
        self.spawn_explosion(pos, count=35, color=color)

    def spawn_barrel_roll_rings(self, pos: tuple[float, float], radius: int = 40, color: tuple[int, int, int] = COLOR_CYAN):
        self.spawn_shockwave(pos, max_r=radius * 3, color=color)
        self.spawn_spark(pos, count=12, color=color)

    def spawn_floating_text(self, pos: tuple[float, float], text: str, color: tuple[int, int, int] = COLOR_GOLD, font_size: int = 18):
        self.floating_texts.add(FloatingText(pos, text, color, font_size))

    def spawn_weather(self, weather_type: str):
        if weather_type == "rain" and len(self.weather_particles) < 70:
            self.weather_particles.append([random.randint(0, SCREEN_WIDTH), 0, -random.uniform(60.0, 100.0), random.uniform(500.0, 750.0), (56, 189, 248)])
        elif weather_type == "sparks" and len(self.weather_particles) < 40:
            self.weather_particles.append([random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT, random.uniform(-40.0, 40.0), -random.uniform(120.0, 260.0), (250, 204, 21)])
        elif weather_type == "sandstorm" and len(self.weather_particles) < 80:
            self.weather_particles.append([SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT), -random.uniform(400.0, 650.0), random.uniform(-30.0, 30.0), (245, 158, 11)])

    def update(self, dt: float):
        self.particles.update(dt)
        self.floating_texts.update(dt)
        self.lightning_arcs = [arc for arc in self.lightning_arcs if arc.update(dt)]

        # Weather particles
        for p in self.weather_particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            if p[0] < -50 or p[0] > SCREEN_WIDTH + 50 or p[1] < -50 or p[1] > SCREEN_HEIGHT + 50:
                self.weather_particles.remove(p)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        # Weather particles in screen space
        for p in self.weather_particles:
            pygame.draw.circle(surface, p[4], (int(p[0]), int(p[1])), 2)

        # Particles & Text in World Space with Camera Offset
        for part in self.particles:
            part.draw(surface, camera_offset)

        for arc in self.lightning_arcs:
            arc.draw(surface, camera_offset)

        for txt in self.floating_texts:
            txt.draw(surface, camera_offset)
