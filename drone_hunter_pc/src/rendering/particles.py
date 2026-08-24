"""
===============================================================================
                     DRONE HUNTER 2D - PARTICLE EFFECTS & WEATHER
===============================================================================
High-performance 2D particle simulation, explosive shockwaves, lightning arcs,
floating combat text, and dynamic atmospheric weather with camera offset support.

Phase 9 & Real Asset Integration:
- Authoritative VFX PNG pipeline for explosions and shockwaves (explosion_1, explosion_2, shockwave)
- Smooth scaling and alpha fading for explosion overlays
- Class-aware enemy destruction (Scout/Shooter -> explosion_1, Heavy/Elite -> explosion_2 + shockwave)
- Boss & Player destruction sequences with layered explosion_2 and shockwave PNGs
- Weapon-specific impact bursts with production VFX sprites
- Strict particle caps and finite lifetimes
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_CRIMSON, COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK,
    COLOR_WHITE, COLOR_TESLA, COLOR_CLUSTER, COLOR_MISSILE, COLOR_BEAM,
    COLOR_NEON_RED
)
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_ARMORED, TARGET_TYPE_SHIELD_DRONE
)

MAX_COMBAT_PARTICLES = 300
MAX_RING_PULSES = 6


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
    """Renders authoritative production VFX PNG assets (explosions, shockwaves) with smooth scale and alpha animation."""
    def __init__(self, pos: tuple[float, float], sprite: pygame.Surface | None = None, sprite_name: str = "explosion_1",
                 lifetime: float = 0.45, max_size: int = 80, start_size: int | None = None, is_shockwave: bool = False, rotation_deg: float = 0.0):
        self.pos = pygame.Vector2(pos)
        self.sprite = sprite
        self.asset_id = sprite_name
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.max_size = max_size
        self.start_size = start_size if start_size is not None else int(max_size * (0.15 if is_shockwave else 0.35))
        self.is_shockwave = is_shockwave
        self.rotation_deg = rotation_deg

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, camera_offset: tuple[float, float] = (0.0, 0.0)):
        if self.lifetime <= 0:
            return
        pct = max(0.0, min(1.0, 1.0 - (self.lifetime / self.max_lifetime)))
        # Smooth outward expansion
        scale_pct = math.sin(pct * math.pi * 0.5)
        current_sz = int(self.start_size + (self.max_size - self.start_size) * scale_pct)
        # Smooth alpha falloff
        alpha_pct = 1.0 - (pct ** 1.4)
        alpha = int(255 * max(0.0, min(1.0, alpha_pct)))

        if current_sz <= 0 or alpha < 8:
            return

        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        img = self.sprite if self.sprite else sm.get_vfx_sprite(self.asset_id, (current_sz, current_sz))

        if img is not None:
            if img.get_size() != (current_sz, current_sz):
                img = pygame.transform.smoothscale(img, (current_sz, current_sz))
            rendered = img.copy()
            rendered.set_alpha(alpha)
            if self.rotation_deg != 0.0:
                rendered = pygame.transform.rotate(rendered, self.rotation_deg)

            ox, oy = camera_offset
            rect = rendered.get_rect(center=(int(round(self.pos.x - ox)), int(round(self.pos.y - oy))))
            surface.blit(rendered, rect)
            sm.track_vfx_render(self.asset_id)


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

    def spawn_explosion(self, pos: tuple[float, float], count: int = 24, color: tuple[int, int, int] = COLOR_GOLD, sprite_name: str = 'explosion_1', max_size: int = 80):
        # 1. Primary visual: Real production explosion PNG overlay
        rot = random.uniform(0, 360.0)
        self.explosion_overlays.append(ExplosionOverlay(pos, sprite_name=sprite_name, lifetime=0.45, max_size=max_size, rotation_deg=rot))

        # 2. Secondary enhancement: Bounded ambient debris particles
        for _ in range(min(count, 20)):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, 300.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            rad = random.uniform(2.5, 5.5)
            life = random.uniform(0.20, 0.45)
            self.particles.add(Particle(pos, vel, color, rad, life))
        self._enforce_particle_cap()

    def spawn_enemy_death(self, pos: tuple[float, float], color: tuple[int, int, int], enemy_type: str = ""):
        if enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
            self.spawn_explosion(pos, count=24, color=color, sprite_name='explosion_2', max_size=110)
        elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
            self.spawn_explosion(pos, count=22, color=color, sprite_name='explosion_2', max_size=100)
        elif enemy_type == TARGET_TYPE_SCOUT:
            self.spawn_explosion(pos, count=18, color=color, sprite_name='explosion_1', max_size=78)
        else:
            self.spawn_explosion(pos, count=20, color=color, sprite_name='explosion_1', max_size=88)
        self.spawn_spark(pos, count=14, color=COLOR_WHITE)


    def spawn_objective_destruction(self, pos: tuple[float, float]):
        """Objective-specific destruction VFX (NOT boss terminology)."""
        self.spawn_explosion(pos, count=38, color=COLOR_GOLD, sprite_name='explosion_2', max_size=180)
        self.spawn_explosion(pos, count=25, color=COLOR_CRIMSON, sprite_name='explosion_1', max_size=140)
        self.spawn_shockwave(pos, max_r=220, color=COLOR_CYAN)
        self.spawn_spark(pos, count=30, color=COLOR_WHITE)
        self.spawn_spark(pos, count=18, color=COLOR_NEON_RED)

    def spawn_drone_trail(self, pos: tuple[float, float]):
        vel = (random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0))
        self.particles.add(Particle(pos, vel, COLOR_CYAN, radius=3.5, lifetime=0.18))
        self._enforce_particle_cap()

    def spawn_lightning_arc(self, start_pos: tuple[float, float], end_pos: tuple[float, float], color: tuple[int, int, int] = COLOR_TESLA):
        self.lightning_arcs.append(LightningArc(start_pos, end_pos, color))

    def spawn_cluster_explosion(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=20, color=COLOR_CLUSTER, sprite_name='explosion_1', max_size=75)
        self.spawn_shockwave(pos, max_r=90, color=COLOR_CLUSTER)

    def spawn_emp_shockwave(self, pos: tuple[float, float]):
        self.spawn_explosion(pos, count=25, color=COLOR_CYAN, sprite_name='explosion_2', max_size=110)
        self.spawn_shockwave(pos, max_r=130, color=COLOR_CYAN)

    def spawn_shockwave(self, pos: tuple[float, float], max_r: int = 160, color: tuple[int, int, int] = (250, 204, 21)):
        # Primary visual: Real shockwave PNG overlay originating at actual impact location
        self.explosion_overlays.append(ExplosionOverlay(pos, sprite_name='shockwave', lifetime=0.38, max_size=max_r, is_shockwave=True))
        for _ in range(12):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80.0, 220.0)
            vel = (math.cos(ang) * spd, math.sin(ang) * spd)
            self.particles.add(Particle(pos, vel, color, random.uniform(2.0, 4.0), 0.25, is_spark=True))
        self._enforce_particle_cap()

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
        elif weapon_type == "rapid":
            count = 4
            spd_min, spd_max = 160.0, 320.0
            rad_min, rad_max = 1.5, 2.5
            life_min, life_max = 0.02, 0.05
            col = (250, 204, 21)
        elif weapon_type == "scatter":
            count = 6
            spd_min, spd_max = 100.0, 240.0
            rad_min, rad_max = 2.0, 3.5
            life_min, life_max = 0.03, 0.07
            col = COLOR_GOLD
        elif weapon_type in ("missile", "light_missile", "heavy_missile"):
            count = 5
            spd_min, spd_max = 80.0, 200.0
            rad_min, rad_max = 2.5, 4.5
            life_min, life_max = 0.06, 0.12
            col = COLOR_MISSILE
        elif weapon_type in ("plasma", "heavy_cannon"):
            count = 7
            spd_min, spd_max = 60.0, 180.0
            rad_min, rad_max = 3.0, 5.5
            life_min, life_max = 0.05, 0.12
            col = (217, 70, 239)
        elif weapon_type in ("rail", "precision"):
            count = 8
            spd_min, spd_max = 220.0, 450.0
            rad_min, rad_max = 2.0, 4.0
            life_min, life_max = 0.04, 0.09
            col = (224, 242, 254)
        elif weapon_type in ("barrage", "missile_barrage"):
            count = 6
            spd_min, spd_max = 90.0, 220.0
            rad_min, rad_max = 2.0, 4.0
            life_min, life_max = 0.05, 0.10
            col = COLOR_MISSILE
        elif weapon_type in ("beam", "arc_beam"):
            count = 3
            spd_min, spd_max = 140.0, 260.0
            rad_min, rad_max = 1.5, 3.0
            life_min, life_max = 0.03, 0.06
            col = COLOR_BEAM
        elif weapon_type == "tesla":
            count = 5
            spd_min, spd_max = 120.0, 250.0
            rad_min, rad_max = 1.5, 3.0
            life_min, life_max = 0.04, 0.08
            col = COLOR_TESLA
        elif weapon_type == "cluster":
            count = 6
            spd_min, spd_max = 80.0, 190.0
            rad_min, rad_max = 2.5, 4.5
            life_min, life_max = 0.05, 0.10
            col = COLOR_CLUSTER
        elif weapon_type == "emp":
            count = 8
            spd_min, spd_max = 140.0, 300.0
            rad_min, rad_max = 2.0, 4.0
            life_min, life_max = 0.06, 0.14
            col = (6, 182, 212)
        else:
            count = 4
            spd_min, spd_max = 120.0, 260.0
            rad_min, rad_max = 1.5, 3.0
            life_min, life_max = 0.03, 0.07
            col = COLOR_CYAN

        base_x = cx + fwd_x * 12
        base_y = cy + fwd_y * 12
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

    def spawn_weapon_impact(self, pos: tuple[float, float], weapon_type: str):
        """Spawns weapon-specific visual impact burst using real explosion and shockwave PNGs."""
        if weapon_type in ("missile", "light_missile", "heavy_missile", "barrage"):
            self.spawn_explosion(pos, count=18, color=COLOR_MISSILE, sprite_name='explosion_2', max_size=85)
            if weapon_type == "heavy_missile":
                self.spawn_shockwave(pos, max_r=110, color=COLOR_MISSILE)
        elif weapon_type in ("plasma", "heavy_cannon"):
            self.spawn_explosion(pos, count=20, color=(217, 70, 239), sprite_name='explosion_2', max_size=95)
        elif weapon_type in ("rail", "precision"):
            self.spawn_explosion(pos, count=12, color=(224, 242, 254), sprite_name='explosion_1', max_size=55)
            self.spawn_spark(pos, count=14, color=(224, 242, 254))
        elif weapon_type == "tesla":
            self.spawn_explosion(pos, count=12, color=COLOR_TESLA, sprite_name='explosion_1', max_size=50)
            self.spawn_spark(pos, count=12, color=COLOR_TESLA)
        elif weapon_type == "cluster":
            self.spawn_cluster_explosion(pos)
        elif weapon_type == "emp":
            self.spawn_emp_shockwave(pos)
        elif weapon_type == "scatter":
            self.spawn_explosion(pos, count=10, color=COLOR_GOLD, sprite_name='explosion_1', max_size=45)
            self.spawn_spark(pos, count=10, color=COLOR_GOLD)
        else:
            self.spawn_explosion(pos, count=8, color=COLOR_CYAN, sprite_name='explosion_1', max_size=45)
            self.spawn_spark(pos, count=8, color=COLOR_CYAN)

    def spawn_cluster_burst(self, pos: tuple[float, float]):
        self.spawn_cluster_explosion(pos)

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

    def spawn_player_destruction(self, pos: tuple[float, float]):
        # Primary visual: Heavy explosion_2 and shockwave overlays
        self.spawn_explosion(pos, count=45, color=COLOR_GOLD, sprite_name='explosion_2', max_size=210)
        self.spawn_shockwave(pos, max_r=260, color=(56, 189, 248))
        self.spawn_spark(pos, count=35, color=COLOR_WHITE)
        self.spawn_spark(pos, count=25, color=COLOR_CRIMSON)

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

        # Explosion & shockwave overlays (real production PNG sprites)
        for overlay in self.explosion_overlays:
            overlay.draw(surface, camera_offset)

        # Particles & Text in World Space with Camera Offset
        for part in self.particles:
            part.draw(surface, camera_offset)

        for arc in self.lightning_arcs:
            arc.draw(surface, camera_offset)

        for txt in self.floating_texts:
            txt.draw(surface, camera_offset)
