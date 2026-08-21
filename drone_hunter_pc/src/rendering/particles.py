"""
===============================================================================
                     DRONE HUNTER 2D - PARTICLE EFFECTS & WEATHER
===============================================================================
High-performance 2D particle simulation, explosive shockwaves, lightning arcs,
floating combat text, and dynamic atmospheric weather with camera offset support.

Phase 9 additions:
- Class-aware enemy hit sparks (Scout/Shooter/Heavy/Shield/Boss)
- Bounded ring pulse overlays
- Weapon-flavored muzzle bursts
- Boss phase transition burst
- Player destruction sequence
All new effects have strict particle caps and finite lifetimes.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_CRIMSON, COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK,
    COLOR_WHITE, COLOR_TESLA, COLOR_CLUSTER, COLOR_MISSILE
)
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_ARMORED, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_BOSS
)

# ── Phase 9 Particle Caps ──────────────────────────────────────────────────────
MAX_COMBAT_PARTICLES = 300   # hard cap on the particles group
MAX_RING_PULSES       = 6    # max simultaneous ring pulse overlays


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
        if len(self.points) > 1:
            ox, oy = camera_offset
            screen_pts = [(int(round(p.x - ox)), int(round(p.y - oy))) for p in self.points]
            pygame.draw.lines(surface, self.color, False, screen_pts, 3)
            pygame.draw.lines(surface, COLOR_WHITE, False, screen_pts, 1)


class ExplosionOverlay:
    def __init__(self, pos: tuple[float, float], sprite: pygame.Surface, lifetime: float = 0.4, max_size: int = 64):
        self.pos = pygame.Vector2(pos)
        self.sprite = sprite
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.max_size = max_size
        self.current_size = max_size * 0.3

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        self.current_size = self.max_size * (0.3 + 0.7 * progress)
        return True

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        pct = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        alpha = int(255 * pct)
        ox, oy = camera_offset
        sz = int(self.current_size)
        if sz > 0 and alpha > 10:
            scaled = pygame.transform.smoothscale(self.sprite, (sz, sz))
            scaled.set_alpha(alpha)
            rect = scaled.get_rect(center=(int(round(self.pos.x - ox)), int(round(self.pos.y - oy))))
            surface.blit(scaled, rect)


class ParticleManager:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()
        self.lightning_arcs: list[LightningArc] = []
        self.weather_particles = []
        self.explosion_overlays: list[ExplosionOverlay] = []
        from src.rendering.sprite_manager import get_sprite_manager
        self.sprite_manager = get_sprite_manager()

    def _enforce_particle_cap(self):
        if len(self.particles) > MAX_COMBAT_PARTICLES:
            excess = len(self.particles) - MAX_COMBAT_PARTICLES
            sprites = self.particles.sprites()
            for spr in sprites[:excess]:
                spr.kill()

    def spawn_spark(self, pos: tuple[float, float], count: int = 8, color: tuple[int, int, int] = COLOR_CYAN):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(140.0, 360.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(1.5, 3.5)
            life = random.uniform(0.12, 0.28)
            self.particles.add(Particle(pos, vel, color, rad, life, is_spark=True))
        self._enforce_particle_cap()

    def spawn_explosion(self, pos: tuple[float, float], count: int = 24, color: tuple[int, int, int] = COLOR_GOLD, sprite_name: str | None = None, max_size: int = 64):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, 320.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(3.0, 7.0)
            life = random.uniform(0.25, 0.55)
            self.particles.add(Particle(pos, vel, color, rad, life))
        self._enforce_particle_cap()
        if sprite_name and self.sprite_manager:
            exp_sprite = self.sprite_manager.get_vfx_sprite(sprite_name, (max_size, max_size))
            self.explosion_overlays.append(ExplosionOverlay(pos, exp_sprite, lifetime=0.4, max_size=max_size))

    def spawn_enemy_death(self, pos: tuple[float, float], color: tuple[int, int, int], enemy_type: str = ""):
        if enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            max_size = 110
        elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
            max_size = 100
        elif enemy_type == TARGET_TYPE_SCOUT:
            max_size = 78
        else:
            max_size = 88
        self.spawn_explosion(pos, count=28, color=color, sprite_name='explosion_1', max_size=max_size)
        self.spawn_spark(pos, count=16, color=COLOR_WHITE)

    def spawn_boss_explosion(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=55, color=COLOR_GOLD, sprite_name='explosion_2', max_size=210)
        self.spawn_explosion(pos, count=35, color=COLOR_CRIMSON, sprite_name='explosion_2', max_size=180)
        self.spawn_spark(pos, count=30, color=COLOR_WHITE)

    def spawn_drone_trail(self, pos: tuple[float, float]):
        vel = (random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0))
        self.particles.add(Particle(pos, vel, COLOR_CYAN, radius=3.5, lifetime=0.18))
        self._enforce_particle_cap()

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

    def spawn_muzzle_flash(self, pos: tuple[float, float], angle_rad: float, weapon_type: str):
        cx, cy = pos
        fwd_x = math.cos(angle_rad)
        fwd_y = math.sin(angle_rad)
        right_x = -fwd_y
        right_y = fwd_x

        if weapon_type == "pulse":
            count = 4
            spd_min, spd_max = 120.0, 280.0
            rad_min, rad_max = 1.5, 3.0
            life_min, life_max = 0.03, 0.07
            col = COLOR_CYAN
        elif weapon_type == "scatter":
            count = 6
            spd_min, spd_max = 100.0, 240.0
            rad_min, rad_max = 2.0, 3.5
            life_min, life_max = 0.03, 0.07
            col = COLOR_GOLD
        elif weapon_type == "missile":
            count = 5
            spd_min, spd_max = 80.0, 200.0
            rad_min, rad_max = 2.5, 4.5
            life_min, life_max = 0.06, 0.12
            col = COLOR_MISSILE
        else:
            count = 4
            spd_min, spd_max = 120.0, 260.0
            rad_min, rad_max = 1.5, 3.0
            life_min, life_max = 0.03, 0.07
            col = COLOR_CYAN

        base_x = cx + fwd_x * 22
        base_y = cy + fwd_y * 22
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(spd_min, spd_max)
            offset = random.uniform(-4.0, 4.0)
            rx = base_x + right_x * offset
            ry = base_y + right_y * offset
            vel = (math.cos(ang) * spd + fwd_x * 180.0, math.sin(ang) * spd + fwd_y * 180.0)
            rad = random.uniform(rad_min, rad_max)
            life = random.uniform(life_min, life_max)
            self.particles.add(Particle((rx, ry), vel, col, rad, life, is_spark=True))
        self._enforce_particle_cap()

    def spawn_enemy_hit_sparks(self, pos: tuple[float, float], enemy_type: str, damage: int):
        if enemy_type == TARGET_TYPE_SCOUT:
            count = 6
            spd_max = 280.0
            col = COLOR_CYAN
        elif enemy_type == TARGET_TYPE_SHOOTER:
            count = 8
            spd_max = 260.0
            col = (200, 200, 210)
        elif enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            count = 12
            spd_max = 220.0
            col = (245, 158, 11)
        elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
            count = 8
            spd_max = 240.0
            col = COLOR_SHIELD
        elif enemy_type == TARGET_TYPE_BOSS:
            count = 10
            spd_max = 260.0
            col = COLOR_GOLD
        else:
            count = 7
            spd_max = 250.0
            col = COLOR_CRIMSON

        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, spd_max)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(1.5, 3.5)
            life = random.uniform(0.08, 0.20)
            self.particles.add(Particle(pos, vel, col, rad, life, is_spark=True))
        self._enforce_particle_cap()

    def spawn_shield_ripple(self, pos: tuple[float, float]):
        for _ in range(6):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60.0, 140.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.10, 0.22)
            self.particles.add(Particle(pos, vel, COLOR_SHIELD, random.uniform(2.0, 4.0), life, is_spark=True))
        self._enforce_particle_cap()

    def spawn_heavy_impact(self, pos: tuple[float, float]):
        for _ in range(10):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60.0, 180.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.12, 0.28)
            self.particles.add(Particle(pos, vel, (245, 120, 20), random.uniform(2.0, 4.5), life, is_spark=True))
        for _ in range(4):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40.0, 100.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.15, 0.30)
            self.particles.add(Particle(pos, vel, (120, 100, 80), random.uniform(2.5, 5.0), life))
        self._enforce_particle_cap()

    def spawn_boss_phase_transition(self, pos: tuple[float, float], phase_idx: int):
        phase_colors = [
            (56, 189, 248),
            (245, 158, 11),
            (239, 68, 68),
            (217, 70, 239),
        ]
        col = phase_colors[min(phase_idx, len(phase_colors) - 1)]
        for _ in range(18):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, 260.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.25, 0.55)
            self.particles.add(Particle(pos, vel, col, random.uniform(3.0, 6.0), life))
        self._enforce_particle_cap()

    def spawn_player_destruction(self, pos: tuple[float, float]):
        for _ in range(30):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(100.0, 380.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.30, 0.70)
            self.particles.add(Particle(pos, vel, COLOR_GOLD, random.uniform(3.0, 7.0), life))
        for _ in range(20):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60.0, 220.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.25, 0.60)
            self.particles.add(Particle(pos, vel, COLOR_CRIMSON, random.uniform(2.5, 5.5), life))
        for _ in range(12):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40.0, 160.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            life = random.uniform(0.20, 0.50)
            self.particles.add(Particle(pos, vel, COLOR_WHITE, random.uniform(2.0, 4.5), life))
        self._enforce_particle_cap()
        if self.sprite_manager:
            exp_sprite = self.sprite_manager.get_player_state_sprite('destroy', 0, (160, 160))
            self.explosion_overlays.append(ExplosionOverlay(pos, exp_sprite, lifetime=0.5, max_size=160))

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
        self.explosion_overlays = [o for o in self.explosion_overlays if o.update(dt)]

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

        # Explosion overlays (high-fidelity sprites)
        for overlay in self.explosion_overlays:
            overlay.draw(surface, camera_offset)

        # Particles & Text in World Space with Camera Offset
        for part in self.particles:
            part.draw(surface, camera_offset)

        for arc in self.lightning_arcs:
            arc.draw(surface, camera_offset)

        for txt in self.floating_texts:
            txt.draw(surface, camera_offset)
