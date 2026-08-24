"""
================================================================================
                    DRONE HUNTER 2D - 2D PROJECTILES & WEAPONS
================================================================================
Defines all player and enemy 2D projectile sprites with kinematic physics,
guidance tracking, cluster bomblet sub-munitions, and railgun beams.
Uses full 2D world-space bounds for 360-degree combat coverage.
"""

import math
import random
import pygame
from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_MISSILE, COLOR_BEAM, COLOR_TESLA, COLOR_CLUSTER, COLOR_WHITE,
    COLOR_NEON_RED
)

BULLET_SPEED = 900.0
ENEMY_BULLET_SPEED = 340.0

class Bullet(pygame.sprite.Sprite):
    """Primary Player Projectile bolt."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float],
                 angle_offset_deg: float = 0.0, color: tuple[int, int, int] = COLOR_CYAN,
                 speed: float = BULLET_SPEED, damage: int = 28, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "pulse"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.color = color
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            sz = (48, 16) if weapon_id == "rapid" else ((56, 24) if weapon_id == "scatter" else (64, 22))
            self.original_image = get_sprite_manager().get_projectile_sprite(self.weapon_id, sz)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        base_angle_rad = math.atan2(dy, dx)
        
        offset_rad = math.radians(angle_offset_deg)
        self.angle_rad = base_angle_rad + offset_rad
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 8

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class HomingMissile(pygame.sprite.Sprite):
    """Target-seeking guided missile tracking nearest hostile entity."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 65, speed: float = 680.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "missile"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.turn_rate = 7.5
        self.max_lifetime = 12.0
        self.lifetime = self.max_lifetime
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("missile", (72, 28))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 12

        self._cached_target = None
        self._last_rendered_angle = self.angle_rad
        self._angle_render_threshold = math.radians(2.5)

    def update(self, dt: float, target_group=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self._cached_target = None
            self.kill()
            return

        if target_group and len(target_group) > 0:
            # PERF: Reuse cached target if still alive and in group
            if self._cached_target is None or not self._cached_target.alive or self._cached_target not in target_group:
                # Full scan only when target is lost
                self._cached_target = min(target_group, key=lambda t: (t.rect.centerx - self.pos.x)**2 + (t.rect.centery - self.pos.y)**2)

            nearest = self._cached_target
            tx, ty = nearest.rect.center
            desired_ang = math.atan2(ty - self.pos.y, tx - self.pos.x)
            
            diff = (desired_ang - self.angle_rad + math.pi) % (2 * math.pi) - math.pi
            self.angle_rad += max(-self.turn_rate * dt, min(self.turn_rate * dt, diff))
            
            # PERF: Only rotate sprite when heading meaningfully changes
            if abs(self.angle_rad - self._last_rendered_angle) >= self._angle_render_threshold:
                self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
                self.rect = self.image.get_rect(center=self.rect.center)
                self._last_rendered_angle = self.angle_rad

        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self._cached_target = None
            self.kill()


class ContinuousBeam(pygame.sprite.Sprite):
    """Continuous plasma laser beam with piercing capability and high-voltage energy core."""
    def __init__(self, muzzle_pos: tuple[float, float], angle_rad: float, damage_per_second: float = 300.0,
                 image: pygame.Surface | None = None, owner: str = "player", weapon_id: str = "beam"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.damage_per_second = damage_per_second
        self.is_continuous = True
        self.is_piercing = True  # Visually and mechanically pierces targets until an obstacle
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("beam", (52, 16))
            
        self.angle_rad = angle_rad
        self.length = 2000.0
        self.muzzle_pos = pygame.Vector2(muzzle_pos)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=muzzle_pos)
        self.active = True

    def update_transform(self, muzzle_pos: tuple[float, float], angle_rad: float, length: float):
        self.muzzle_pos = pygame.Vector2(muzzle_pos)
        self.angle_rad = angle_rad
        self.length = max(16.0, length)
        
        # High-Fidelity Multi-Layered Plasma Cutter Beam Canvas
        beam_len = int(self.length)
        beam_h = 32
        raw_surf = pygame.Surface((beam_len, beam_h), pygame.SRCALPHA)
        
        # 1. Outer Plasma Halo (Cyan & Ultraviolet Ionization Glow)
        pulse_w = 16.0 + 4.0 * math.sin(pygame.time.get_ticks() * 0.035)
        cy = beam_h // 2
        pygame.draw.line(raw_surf, (14, 165, 233, 100), (0, cy), (beam_len, cy), int(pulse_w + 8))
        pygame.draw.line(raw_surf, (56, 189, 248, 190), (0, cy), (beam_len, cy), int(pulse_w))
        
        # 2. Inner High-Temperature Plasma Channel
        pygame.draw.line(raw_surf, (147, 197, 253, 230), (0, cy), (beam_len, cy), 8)
        
        # 3. Superheated White-Hot Fusion Core
        pygame.draw.line(raw_surf, (255, 255, 255, 255), (0, cy), (beam_len, cy), 3)
        
        # 4. Muzzle & Tip Searing Flare Nodes
        pygame.draw.circle(raw_surf, (56, 189, 248), (6, cy), 11)
        pygame.draw.circle(raw_surf, (255, 255, 255), (6, cy), 6)
        if beam_len > 16:
            pygame.draw.circle(raw_surf, (56, 189, 248), (beam_len - 6, cy), 13)
            pygame.draw.circle(raw_surf, (255, 255, 255), (beam_len - 6, cy), 7)
        
        # Rotate
        self.image = pygame.transform.rotate(raw_surf, math.degrees(-self.angle_rad))
        
        cx = self.muzzle_pos.x + math.cos(self.angle_rad) * (self.length / 2.0)
        cy_world = self.muzzle_pos.y + math.sin(self.angle_rad) * (self.length / 2.0)
        self.rect = self.image.get_rect(center=(int(round(cx)), int(round(cy_world))))

    def update(self, dt: float):
        if not self.active:
            self.kill()



class TeslaArcBeam(pygame.sprite.Sprite):
    """Electric arc bolt that zaps and branches to nearby targets."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 42, speed: float = 1100.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "tesla"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.chained_targets = set()
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("tesla", (64, 64))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 12

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class ClusterBomblet(pygame.sprite.Sprite):
    """Sub-munition created when a Cluster Torpedo detonates."""
    def __init__(self, pos: tuple[float, float], angle_rad: float, speed: float = 380.0, damage: int = 24, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "cluster"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(pos[0]), float(pos[1]))
        self.damage = damage
        self.speed = speed
        self.lifetime = random.uniform(0.65, 1.1)
        self.angle_rad = angle_rad
        
        if image is not None:
            self.image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.image = get_sprite_manager().get_projectile_sprite("cluster", (18, 18))
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=pos)
        self.radius = 6

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -40 or self.rect.left > WORLD_WIDTH + 40 or
            self.rect.bottom < -40 or self.rect.top > WORLD_HEIGHT + 40):
            self.kill()


class ClusterTorpedo(pygame.sprite.Sprite):
    """Heavy ballistic torpedo that splits into 6 bomblets."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 80, speed: float = 520.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "cluster"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.fuse_timer = 0.55
        self.detonated = False
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("cluster", (80, 36))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 14

    def update(self, dt: float) -> list[ClusterBomblet]:
        """Returns new bomblets if detonation occurs this frame."""
        self.fuse_timer -= dt
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()
            return []

        if self.fuse_timer <= 0 and not self.detonated:
            self.detonated = True
            self.kill()
            bomblets = []
            for i in range(6):
                ang = self.angle_rad + (i * (math.pi / 3.0)) + random.uniform(-0.2, 0.2)
                spd = random.uniform(320.0, 460.0)
                bomblets.append(ClusterBomblet(self.rect.center, ang, speed=spd, damage=self.damage // 3, owner=self.owner, weapon_id=self.weapon_id))
            return bomblets

        return []


class HeavyPlasmaOrb(pygame.sprite.Sprite):
    """Heavy concentrated plasma orb with high impact and energy trail."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 90, speed: float = 460.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "plasma"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.is_plasma = True
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("plasma", (72, 72))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 24

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class RailgunSlug(pygame.sprite.Sprite):
    """Supersonic precision kinetic railgun slug with high piercing capability."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 115, speed: float = 1800.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "rail"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.is_piercing = True
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("rail", (96, 24))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 12

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class BarrageMissile(HomingMissile):
    """High-agility guided micro-missile fired in staggered salvos."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], angle_offset_deg: float = 0.0, damage: int = 38, speed: float = 620.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "barrage"):
        if image is None:
            from src.rendering.sprite_manager import get_sprite_manager
            image = get_sprite_manager().get_projectile_sprite("barrage", (64, 24))
        super().__init__(start_pos, target_pos, damage=damage, speed=speed, image=image, owner=owner, weapon_id=weapon_id)
        self.turn_rate = 11.0
        self.angle_rad += math.radians(angle_offset_deg)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))


class EMPShockwave(pygame.sprite.Sprite):
    """Physically expanding shockwave that disables electronic systems."""
    def __init__(self, pos: tuple[float, float], max_radius: float = 400.0, lifetime: float = 1.2, owner: str = "player"):
        super().__init__()
        self.owner = owner
        self.pos = pygame.Vector2(pos)
        self.max_radius = max_radius
        self.lifetime_max = lifetime
        self.lifetime = lifetime
        self.radius = 10.0
        self.is_emp_shockwave = True
        self.damage = 30  # Base shockwave damage
        self.hit_targets = set()

        # Visuals: Pre-allocate bounding canvas for the shockwave
        d = max(40, int(self.max_radius * 2 + 20))
        self.image = pygame.Surface((d, d), pygame.SRCALPHA)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        
        # Expand radius linearly
        progress = 1.0 - (self.lifetime / self.lifetime_max)
        self.radius = max(10.0, self.max_radius * progress)
        
        # Redraw expanding shockwave ring
        d = self.image.get_width()
        self.image.fill((0, 0, 0, 0))
        alpha = int(220 * (self.lifetime / self.lifetime_max))
        c = d // 2
        r = int(self.radius)
        if r > 2:
            thickness = max(2, int(6 * (1.0 - progress * 0.5)))
            pygame.draw.circle(self.image, (6, 182, 212, alpha), (c, c), r, thickness)
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (c, c), max(1, r - 2), 1)
        self.rect.center = (int(self.pos.x), int(self.pos.y))


class EMPPulse(pygame.sprite.Sprite):
    """EMP projectile orb that travels and then detonates into a shockwave."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 30, speed: float = 1200.0, image: pygame.Surface | None = None,
                 owner: str = "player", weapon_id: str = "emp"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.is_emp_projectile = True
        self.lifetime = 1.2
        self.detonated = False
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("emp", (72, 72))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 12

    def detonate(self, ctx):
        if not self.detonated:
            self.detonated = True
            ctx.bullet_group.add(EMPShockwave(self.rect.center, max_radius=250.0, owner=self.owner))
            if ctx.particle_manager:
                ctx.particle_manager.spawn_emp_shockwave(self.rect.center)
            if ctx.audio_manager:
                ctx.audio_manager.play_emp()
            self.kill()

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    """Hostile enemy projectile with weapon-specific readable silhouettes and glowing cores."""
    _cached_sprites: dict[str, pygame.Surface] = {}
    _cached_default_image: pygame.Surface | None = None

    @classmethod
    def _get_enemy_projectile_sprite(cls, weapon_id: str) -> pygame.Surface:
        if weapon_id in cls._cached_sprites and cls._cached_sprites[weapon_id] is not None:
            return cls._cached_sprites[weapon_id]

        if weapon_id in ("aa_missile", "missile"):
            w, h = 40, 16
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Aerodynamic missile fuselage
            pygame.draw.polygon(surf, (220, 38, 38), [(w - 4, h // 2), (10, 2), (6, 4), (10, h - 2)])
            # Warhead tip
            pygame.draw.polygon(surf, (254, 240, 138), [(w, h // 2), (w - 6, 3), (w - 6, h - 3)])
            # Dark stabilizing fins
            pygame.draw.polygon(surf, (51, 65, 85), [(10, 2), (2, 0), (6, 6)])
            pygame.draw.polygon(surf, (51, 65, 85), [(10, h - 2), (2, h), (6, h - 6)])
            # Rocket exhaust glow
            pygame.draw.circle(surf, (245, 158, 11, 200), (4, h // 2), 5)
            pygame.draw.circle(surf, (255, 255, 255, 240), (4, h // 2), 2)
        elif weapon_id in ("aa_heavy", "enemy_heavy"):
            w, h = 36, 16
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Heavy kinetic plasma shell
            pygame.draw.ellipse(surf, (234, 88, 12), (0, 0, w, h))
            pygame.draw.ellipse(surf, (251, 146, 60), (4, 2, w - 8, h - 4))
            pygame.draw.ellipse(surf, (255, 255, 255), (10, 4, w - 16, h - 8))
        elif weapon_id in ("aa_light", "aa_flak"):
            w, h = 28, 12
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Fast flak tracer bolt (Cyan / Amber energy)
            pygame.draw.ellipse(surf, (6, 182, 212), (0, 0, w, h))
            pygame.draw.ellipse(surf, (224, 242, 254), (4, 2, w - 8, h - 4))
            pygame.draw.ellipse(surf, (255, 255, 255), (10, 4, w - 16, h - 8))
        elif weapon_id in ("enemy_aircraft", "aircraft_laser"):
            w, h = 30, 12
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Supersonic crimson fighter tracer
            pygame.draw.ellipse(surf, (244, 63, 94), (0, 0, w, h))
            pygame.draw.ellipse(surf, (254, 205, 211), (4, 2, w - 8, h - 4))
            pygame.draw.ellipse(surf, (255, 255, 255), (8, 4, w - 14, h - 8))
        else: # Default enemy laser (Shooter / Turret)
            w, h = 32, 14
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Searing orange/amber plasma bolt
            pygame.draw.ellipse(surf, (239, 68, 68), (0, 0, w, h))
            pygame.draw.ellipse(surf, (245, 158, 11), (3, 2, w - 6, h - 4))
            pygame.draw.ellipse(surf, (254, 240, 138), (8, 3, w - 14, h - 6))
            pygame.draw.ellipse(surf, (255, 255, 255), (14, 4, w - 22, h - 8))

        cls._cached_sprites[weapon_id] = surf
        if cls._cached_default_image is None:
            cls._cached_default_image = cls._cached_sprites.get("enemy_laser", surf)
        return surf

    @classmethod
    def _get_default_image(cls) -> pygame.Surface:
        if cls._cached_default_image is None:
            cls._cached_default_image = cls._get_enemy_projectile_sprite("enemy_laser")
        return cls._cached_default_image

    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float],
                 speed: float = ENEMY_BULLET_SPEED, angle_offset_deg: float = 0.0, damage: int = 20, image: pygame.Surface | None = None,
                 owner: str = "enemy", weapon_id: str = "enemy_laser"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.lifetime = 6.0
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = EnemyBullet._get_enemy_projectile_sprite(self.weapon_id)
            if EnemyBullet._cached_default_image is None:
                EnemyBullet._cached_default_image = self.original_image
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        base_angle_rad = math.atan2(dy, dx)
        
        offset_rad = math.radians(angle_offset_deg)
        self.angle_rad = base_angle_rad + offset_rad
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 8

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class EnemySniperBeam(pygame.sprite.Sprite):
    """Supersonic railgun beam fired by Sniper Drones."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], speed: float = 1200.0, damage: int = 35, image: pygame.Surface | None = None,
                 owner: str = "enemy", weapon_id: str = "sniper_beam"):
        super().__init__()
        self.owner = owner
        self.weapon_id = weapon_id
        self.spawn_pos = (float(start_pos[0]), float(start_pos[1]))
        self.damage = damage
        self.speed = speed
        self.lifetime = 3.0
        
        if image is not None:
            self.original_image = image
        else:
            from src.rendering.sprite_manager import get_sprite_manager
            self.original_image = get_sprite_manager().get_projectile_sprite("beam", (48, 12))
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 8

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()
