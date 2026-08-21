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
                 speed: float = BULLET_SPEED, damage: int = 28, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.color = color
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((22, 6), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, color, (0, 0, 22, 6), border_radius=3)
            pygame.draw.rect(self.original_image, COLOR_WHITE, (4, 1, 14, 4), border_radius=2)
        
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
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 65, speed: float = 680.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.turn_rate = 7.5
        self.max_lifetime = 12.0
        self.lifetime = self.max_lifetime
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((28, 10), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, COLOR_MISSILE, [(28, 5), (0, 0), (4, 5), (0, 10)])
            pygame.draw.rect(self.original_image, COLOR_WHITE, (14, 3, 10, 4))
        
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


class PlasmaLaserBeam(pygame.sprite.Sprite):
    """High-velocity cutting laser beam with piercing capability."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 14, speed: float = 1500.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.is_piercing = True
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((44, 8), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, COLOR_BEAM, (0, 0, 44, 8), border_radius=4)
            pygame.draw.rect(self.original_image, COLOR_WHITE, (6, 2, 32, 4), border_radius=2)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 10

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class TeslaArcBeam(pygame.sprite.Sprite):
    """Electric arc bolt that zaps and branches to nearby targets."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 42, speed: float = 1100.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.chained_targets = set()
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((32, 10), pygame.SRCALPHA)
            points = [(0, 5), (10, 0), (14, 4), (24, 1), (32, 5), (22, 9), (18, 5), (8, 10)]
            pygame.draw.polygon(self.original_image, COLOR_TESLA, points)
            pygame.draw.polygon(self.original_image, COLOR_WHITE, [(4, 5), (11, 2), (15, 5), (23, 3), (28, 5), (21, 7), (9, 7)])
        
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
    def __init__(self, pos: tuple[float, float], angle_rad: float, speed: float = 380.0, damage: int = 24, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.lifetime = random.uniform(0.65, 1.1)
        self.angle_rad = angle_rad
        
        if image is not None:
            self.image = image
        else:
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, COLOR_CLUSTER, (6, 6), 6)
            pygame.draw.circle(self.image, (255, 230, 100), (6, 6), 3)
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
    _cached_default_image = None

    @classmethod
    def _get_default_image(cls) -> pygame.Surface | None:
        if cls._cached_default_image is None:
            try:
                from src.rendering.sprite_manager import get_sprite_manager
                cls._cached_default_image = get_sprite_manager().get_projectile_sprite('cluster', (34, 14))
            except Exception:
                cls._cached_default_image = None
        return cls._cached_default_image

    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 80, speed: float = 520.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.fuse_timer = 0.55
        self.detonated = False
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = ClusterTorpedo._get_default_image()
            if self.original_image is None:
                self.original_image = pygame.Surface((34, 14), pygame.SRCALPHA)
                pygame.draw.ellipse(self.original_image, COLOR_CLUSTER, (0, 0, 34, 14))
                pygame.draw.ellipse(self.original_image, COLOR_WHITE, (10, 3, 14, 8))
                pygame.draw.rect(self.original_image, (239, 68, 68), (0, 4, 6, 6))
        
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
                bomblets.append(ClusterBomblet(self.rect.center, ang, speed=spd, damage=self.damage // 3))
            return bomblets

        return []


class HeavyPlasmaOrb(pygame.sprite.Sprite):
    """Heavy concentrated plasma orb with high impact and energy trail."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 90, speed: float = 460.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.is_plasma = True
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (168, 85, 247, 100), (14, 14), 14)
            pygame.draw.circle(self.original_image, (217, 70, 239), (14, 14), 10)
            pygame.draw.circle(self.original_image, COLOR_WHITE, (14, 14), 5)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 14

    def update(self, dt: float):
        self.pos.x += math.cos(self.angle_rad) * self.speed * dt
        self.pos.y += math.sin(self.angle_rad) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if (self.rect.right < -80 or self.rect.left > WORLD_WIDTH + 80 or
            self.rect.bottom < -80 or self.rect.top > WORLD_HEIGHT + 80):
            self.kill()


class RailgunSlug(pygame.sprite.Sprite):
    """Supersonic precision kinetic railgun slug with high piercing capability."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], damage: int = 115, speed: float = 1800.0, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.is_piercing = True
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = pygame.Surface((56, 8), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, (186, 230, 253), (0, 1, 56, 6), border_radius=3)
            pygame.draw.rect(self.original_image, COLOR_WHITE, (8, 2, 44, 4), border_radius=2)
            pygame.draw.circle(self.original_image, (56, 189, 248), (52, 4), 4)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle_rad = math.atan2(dy, dx)
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


class BarrageMissile(HomingMissile):
    """High-agility guided micro-missile fired in staggered salvos."""
    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], angle_offset_deg: float = 0.0, damage: int = 38, speed: float = 620.0, image: pygame.Surface | None = None):
        super().__init__(start_pos, target_pos, damage=damage, speed=speed, image=image)
        self.turn_rate = 11.0
        self.angle_rad += math.radians(angle_offset_deg)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.angle_rad))



class EnemyBullet(pygame.sprite.Sprite):
    """Hostile enemy projectile."""
    _cached_default_image = None

    @classmethod
    def _get_default_image(cls) -> pygame.Surface | None:
        if cls._cached_default_image is None:
            try:
                from src.rendering.sprite_manager import get_sprite_manager
                cls._cached_default_image = get_sprite_manager().get_projectile_sprite('enemy', (16, 6))
            except Exception:
                cls._cached_default_image = None
        return cls._cached_default_image

    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float],
                 speed: float = ENEMY_BULLET_SPEED, angle_offset_deg: float = 0.0, damage: int = 20, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.lifetime = 6.0
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = EnemyBullet._get_default_image()
            if self.original_image is None:
                self.original_image = pygame.Surface((16, 6), pygame.SRCALPHA)
                pygame.draw.rect(self.original_image, COLOR_CRIMSON, (0, 0, 16, 6), border_radius=3)
                pygame.draw.rect(self.original_image, (255, 200, 200), (3, 1, 10, 4), border_radius=2)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        base_angle_rad = math.atan2(dy, dx)
        
        offset_rad = math.radians(angle_offset_deg)
        self.angle_rad = base_angle_rad + offset_rad
        self.angle_deg = math.degrees(-self.angle_rad)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle_deg)
        self.pos = pygame.Vector2(start_pos)
        self.rect = self.image.get_rect(center=start_pos)
        self.radius = 7

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
    _cached_default_image = None

    @classmethod
    def _get_default_image(cls) -> pygame.Surface | None:
        if cls._cached_default_image is None:
            try:
                from src.rendering.sprite_manager import get_sprite_manager
                cls._cached_default_image = get_sprite_manager().get_projectile_sprite('beam', (36, 6))
            except Exception:
                cls._cached_default_image = None
        return cls._cached_default_image

    def __init__(self, start_pos: tuple[float, float], target_pos: tuple[float, float], speed: float = 1200.0, damage: int = 35, image: pygame.Surface | None = None):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.lifetime = 3.0
        
        if image is not None:
            self.original_image = image
        else:
            self.original_image = EnemySniperBeam._get_default_image()
            if self.original_image is None:
                self.original_image = pygame.Surface((36, 6), pygame.SRCALPHA)
                pygame.draw.rect(self.original_image, COLOR_NEON_RED, (0, 0, 36, 6), border_radius=3)
                pygame.draw.rect(self.original_image, COLOR_WHITE, (6, 1, 24, 4), border_radius=2)
        
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
