"""
================================================================================
          DRONE HUNTER 2D - GROUND OBJECTIVE & DEFENSE ENTITIES
================================================================================
Defines physical in-world combat entities for the Objective Assault game mode:
- GroundObjective: Primary fortress/core to destroy for mission completion
- RadarNode: Detection and early warning radar units coordinating defenses
- AAPlatform: Directional anti-air flak cannons and missile turrets
- ShieldGenerator: Tactical perimeter structures powering objective shields
- CombatAircraft: Airborne enemy aircraft engaging player in dogfights
"""

import math
import random
import pygame
from typing import List, Optional, Tuple

from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_WHITE, COLOR_SHIELD, COLOR_NEON_RED
)
from src.data.objective_data import (
    OBJECTIVE_TYPE_RADAR_COMMAND, get_objective_catalog_def,
    RADAR_STATE_SCANNING, RADAR_STATE_ALERT, RADAR_STATE_DESTROYED,
    AA_TYPE_LIGHT, AA_TYPE_HEAVY, AA_TYPE_MISSILE,
    AIRCRAFT_INTERCEPTOR, AIRCRAFT_ATTACK
)
from src.entities.bullet import EnemyBullet, HomingMissile
from src.entities.enemy import Enemy


# -----------------------------------------------------------------------------
# SHIELD GENERATOR PERIMETER ENTITY
# -----------------------------------------------------------------------------
class ShieldGenerator(pygame.sprite.Sprite):
    """Auxiliary power structure providing invulnerability to the Ground Objective."""
    def __init__(self, pos: Tuple[float, float], parent_objective=None):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.parent_objective = parent_objective
        self.max_hp = 120
        self.hp = self.max_hp
        self.armor = 0.10
        self.size = 50
        self.radius = 24
        self.alive = True
        self.hit_flash_timer = 0.0
        self.time_accum = random.uniform(0.0, 5.0)

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self._render()

    def take_damage(self, amount: int, **kwargs) -> bool:
        if not self.alive:
            return False
        effective = max(1, int(round(amount * (1.0 - self.armor))))
        self.hp -= effective
        self.hit_flash_timer = 0.12
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.kill()
            return True
        return False

    def update(self, dt: float, *args, **kwargs) -> list:
        if not self.alive:
            return []
        self.time_accum += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        self._render()
        return []

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        # Outer chassis
        pygame.draw.circle(self.image, (30, 41, 59), (cx, cy), self.radius)
        pygame.draw.circle(self.image, COLOR_SHIELD, (cx, cy), self.radius, 2)
        
        # Rotating power core
        core_r = int(10 + 3 * math.sin(self.time_accum * 6.0))
        pygame.draw.circle(self.image, (56, 189, 248), (cx, cy), core_r)
        pygame.draw.circle(self.image, COLOR_WHITE, (cx, cy), max(2, core_r - 4))

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# -----------------------------------------------------------------------------
# RADAR NODE EARLY WARNING ENTITY
# -----------------------------------------------------------------------------
class RadarNode(pygame.sprite.Sprite):
    """Early-warning sensor dome that tracks player and alerts regional defenses."""
    def __init__(self, pos: Tuple[float, float], scan_radius: float = 950.0):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.scan_radius = scan_radius
        self.state = RADAR_STATE_SCANNING
        self.max_hp = 140
        self.hp = self.max_hp
        self.armor = 0.05
        self.size = 64
        self.radius = 28
        self.alive = True
        self.hit_flash_timer = 0.0
        
        self.sweep_angle = random.uniform(0.0, 360.0)
        self.sweep_speed = 120.0 # deg / sec
        self.is_player_detected = False
        self.alert_timer = 0.0

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self._render()

    def take_damage(self, amount: int, **kwargs) -> bool:
        if not self.alive:
            return False
        effective = max(1, int(round(amount * (1.0 - self.armor))))
        self.hp -= effective
        self.hit_flash_timer = 0.12
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.state = RADAR_STATE_DESTROYED
            self.kill()
            return True
        return False

    def update(self, dt: float, player_pos: Tuple[float, float] = (0, 0), *args, **kwargs) -> list:
        if not self.alive:
            return []
        
        self.sweep_angle = (self.sweep_angle + self.sweep_speed * dt) % 360.0
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # Distance check to player
        dist = math.hypot(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
        if dist <= self.scan_radius:
            self.is_player_detected = True
            self.state = RADAR_STATE_ALERT
            self.alert_timer = 2.0
        else:
            if self.alert_timer > 0:
                self.alert_timer -= dt
            else:
                self.is_player_detected = False
                self.state = RADAR_STATE_SCANNING

        self._render()
        return []

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        # Base platform
        pygame.draw.circle(self.image, (15, 23, 42), (cx, cy), self.radius)
        ring_col = COLOR_NEON_RED if self.state == RADAR_STATE_ALERT else COLOR_CYAN
        pygame.draw.circle(self.image, ring_col, (cx, cy), self.radius, 2)
        
        # Rotating radar antenna dish
        rad = math.radians(self.sweep_angle)
        dx = math.cos(rad) * (self.radius - 4)
        dy = math.sin(rad) * (self.radius - 4)
        pygame.draw.line(self.image, ring_col, (cx, cy), (cx + dx, cy + dy), 3)
        pygame.draw.circle(self.image, COLOR_WHITE, (int(round(cx + dx)), int(round(cy + dy))), 3)
        pygame.draw.circle(self.image, ring_col, (cx, cy), 6)

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# -----------------------------------------------------------------------------
# ANTI-AIR (AA) DEFENSE PLATFORM ENTITY
# -----------------------------------------------------------------------------
class AAPlatform(pygame.sprite.Sprite):
    """Directional defensive flak cannon or missile launcher platform."""
    def __init__(self, pos: Tuple[float, float], aa_type: str = AA_TYPE_LIGHT):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.aa_type = aa_type
        
        if aa_type == AA_TYPE_LIGHT:
            self.max_hp = 160
            self.fire_cooldown_max = 1.6
            self.range = 750.0
            self.projectile_speed = 460.0
            self.projectile_damage = 18
            self.color = COLOR_CYAN
            self.size = 56
        elif aa_type == AA_TYPE_HEAVY:
            self.max_hp = 260
            self.fire_cooldown_max = 2.4
            self.range = 850.0
            self.projectile_speed = 400.0
            self.projectile_damage = 32
            self.color = COLOR_GOLD
            self.size = 68
        else: # AA_TYPE_MISSILE
            self.max_hp = 220
            self.fire_cooldown_max = 3.2
            self.range = 950.0
            self.projectile_speed = 340.0
            self.projectile_damage = 40
            self.color = COLOR_CRIMSON
            self.size = 64

        self.hp = self.max_hp
        self.armor = 0.15
        self.radius = self.size // 2
        self.alive = True
        self.hit_flash_timer = 0.0
        
        self.fire_timer = random.uniform(0.5, self.fire_cooldown_max)
        self.turret_angle = 180.0
        self.is_telegraphing = False
        self.telegraph_timer = 0.0
        self.telegraph_duration = 0.40

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self._render()

    def take_damage(self, amount: int, **kwargs) -> bool:
        if not self.alive:
            return False
        effective = max(1, int(round(amount * (1.0 - self.armor))))
        self.hp -= effective
        self.hit_flash_timer = 0.12
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.kill()
            return True
        return False

    def update(self, dt: float, player_pos: Tuple[float, float] = (0, 0), *args, **kwargs) -> list:
        if not self.alive:
            return []
        
        new_bullets = []
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        to_player = pygame.Vector2(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
        dist = to_player.length()

        if dist <= self.range:
            # Aim towards player
            target_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            self.turret_angle = target_angle

            if not self.is_telegraphing:
                self.fire_timer -= dt
                if self.fire_timer <= 0:
                    self.is_telegraphing = True
                    self.telegraph_timer = self.telegraph_duration
            else:
                self.telegraph_timer -= dt
                if self.telegraph_timer <= 0:
                    # FIRE!
                    self.is_telegraphing = False
                    self.fire_timer = self.fire_cooldown_max
                    cx, cy = self.rect.center

                    if self.aa_type == AA_TYPE_LIGHT:
                        new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=self.projectile_speed,
                                                       damage=self.projectile_damage))
                    elif self.aa_type == AA_TYPE_HEAVY:
                        new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=self.projectile_speed,
                                                       damage=self.projectile_damage))
                        new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=self.projectile_speed * 0.95,
                                                       damage=self.projectile_damage // 2, angle_offset_deg=-14.0))
                        new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=self.projectile_speed * 0.95,
                                                       damage=self.projectile_damage // 2, angle_offset_deg=14.0))
                    else: # AA_TYPE_MISSILE
                        new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=self.projectile_speed,
                                                       damage=self.projectile_damage))
        else:
            self.is_telegraphing = False

        self._render()
        return new_bullets

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        # Heavy bunker base
        pygame.draw.rect(self.image, (30, 41, 59), (4, 4, self.size - 8, self.size - 8), border_radius=8)
        pygame.draw.rect(self.image, (71, 85, 105), (4, 4, self.size - 8, self.size - 8), 2, border_radius=8)
        
        # Rotating barrel
        rad = math.radians(self.turret_angle)
        bx = cx + math.cos(rad) * (self.radius - 2)
        by = cy + math.sin(rad) * (self.radius - 2)
        barrel_col = COLOR_NEON_RED if self.is_telegraphing else self.color
        pygame.draw.line(self.image, barrel_col, (cx, cy), (bx, by), 4)
        
        # Center turret hub
        pygame.draw.circle(self.image, (15, 23, 42), (cx, cy), 12)
        pygame.draw.circle(self.image, barrel_col, (cx, cy), 10)
        pygame.draw.circle(self.image, COLOR_WHITE, (cx, cy), 4)

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# -----------------------------------------------------------------------------
# COMBAT AIRCRAFT ENEMY ENTITY
# -----------------------------------------------------------------------------
class CombatAircraft(Enemy):
    """High-speed airborne hostile aircraft performing dogfight strafing runs."""
    def __init__(self, pos: Tuple[float, float], aircraft_type: str = AIRCRAFT_INTERCEPTOR, **kwargs):
        super().__init__(enemy_type=aircraft_type, pos=pos, **kwargs)
        self.aircraft_type = aircraft_type
        
        if aircraft_type == AIRCRAFT_INTERCEPTOR:
            self.max_hp = 35
            self.speed = 340.0
            self.points = 240
            self.color_outer = (239, 68, 68) # Red Jet
            self.color_inner = COLOR_GOLD
            self.size = 44
        else: # AIRCRAFT_ATTACK
            self.max_hp = 60
            self.speed = 260.0
            self.points = 320
            self.color_outer = (59, 130, 246) # Blue Bomber
            self.color_inner = COLOR_WHITE
            self.size = 52

        self.hp = self.max_hp
        self.score_value = self.points
        self.radius = self.size // 2
        self.strafe_angle = random.uniform(0.0, 360.0)

    def update(self, dt: float, player_pos: Tuple[float, float] = (200, 360),
               player_vel: Tuple[float, float] = (0, 0), player_obj=None, target_group=None) -> list:
        if not self.alive:
            return []
        
        new_bullets = []
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # High-speed fluid flight kinematics
        to_player = pygame.Vector2(player_pos[0] - self.pos.x, player_pos[1] - self.pos.y)
        dist = to_player.length()
        norm_to_p = to_player.normalize() if dist > 0.001 else pygame.Vector2(1, 0)

        if self.ai_state == "approach":
            self.pos += norm_to_p * self.speed * dt
            self.heading_angle = math.degrees(math.atan2(norm_to_p.y, norm_to_p.x))
            if dist <= 420.0:
                self.ai_state = "strafe"
                self.state_timer = 0.0
        elif self.ai_state == "strafe":
            self.state_timer += dt
            lateral = pygame.Vector2(-norm_to_p.y, norm_to_p.x) * self.strafe_dir
            move_vec = (lateral * 0.8 + norm_to_p * 0.2).normalize()
            self.pos += move_vec * self.speed * dt
            self.heading_angle = math.degrees(math.atan2(move_vec.y, move_vec.x))

            # Fire short burst
            if self.state_timer >= 0.8:
                self.state_timer = 0.0
                cx, cy = self.rect.center
                new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=380.0, damage=14))
                if dist < 280.0:
                    self.ai_state = "reposition"
        elif self.ai_state == "reposition":
            # Evasive breakaway
            away = -norm_to_p
            self.pos += away * self.speed * dt
            self.heading_angle = math.degrees(math.atan2(away.y, away.x))
            if dist > 550.0:
                self.ai_state = "approach"

        # Arena bounds clamping
        self.pos.x = max(60.0, min(float(WORLD_WIDTH - 60.0), self.pos.x))
        self.pos.y = max(60.0, min(float(WORLD_HEIGHT - 60.0), self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        self._render_aircraft_sprite()
        return new_bullets

    def _render_aircraft_sprite(self):
        s = self.size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        center = (s // 2, s // 2)
        
        # Aerodynamic jet fuselage
        pts = [(s, s // 2), (4, s // 4), (s // 3, s // 2), (4, s * 3 // 4)]
        pygame.draw.polygon(surf, self.color_outer, pts)
        pygame.draw.polygon(surf, (255, 255, 255, 200), pts, 2)
        pygame.draw.circle(surf, self.color_inner, center, 4)

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(surf)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            surf.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.image = pygame.transform.rotate(surf, -self.heading_angle)
        self.rect = self.image.get_rect(center=self.rect.center)


# -----------------------------------------------------------------------------
# GROUND OBJECTIVE MAIN ENTITY
# -----------------------------------------------------------------------------
class GroundObjective(pygame.sprite.Sprite):
    """Primary physical fortress or ground installation required for mission victory."""
    def __init__(self, objective_type: str = OBJECTIVE_TYPE_RADAR_COMMAND,
                 pos: Tuple[float, float] = (WORLD_WIDTH - 300.0, WORLD_HEIGHT // 2),
                 defense_level: int = 1, hp_mult: float = 1.0):
        super().__init__()
        self.objective_type = objective_type
        self.defense_level = defense_level
        self.catalog_data = get_objective_catalog_def(objective_type)
        
        self.name = self.catalog_data["name"]
        self.title = self.catalog_data["title"]
        self.max_hp = int(self.catalog_data["base_hp"] * hp_mult)
        self.hp = self.max_hp
        self.armor = self.catalog_data["armor"]
        self.size = self.catalog_data["size"]
        self.radius = self.size // 2
        self.score_value = self.catalog_data["reward_score"]
        self.scrap_reward = self.catalog_data["reward_scrap"]
        
        self.pos = pygame.Vector2(pos)
        self.alive = True
        self.is_objective = True
        self.hit_flash_timer = 0.0
        self.time_accum = 0.0

        # Shield & Generator Network
        self.shield_generators: List[ShieldGenerator] = []
        self.is_shielded = False

        # States: active, shielded, damaged, critical, destroyed
        self.state = "active"

        self.image = pygame.Surface((self.size + 40, self.size + 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self._render()

    @property
    def hp_percent(self) -> float:
        return max(0.0, min(1.0, self.hp / max(1, self.max_hp)))

    def register_shield_generator(self, generator: ShieldGenerator):
        """Connects a shield generator to the objective defense grid."""
        self.shield_generators.append(generator)
        self.is_shielded = True

    def take_damage(self, amount: int, source: str = "bullet", **kwargs) -> bool:
        if not self.alive:
            return False

        # Check shield generator network
        alive_gens = [g for g in self.shield_generators if getattr(g, "alive", False)]
        if len(alive_gens) > 0:
            self.is_shielded = True
            self.hit_flash_timer = 0.08
            return False
        else:
            self.is_shielded = False

        effective = max(1, int(round(amount * (1.0 - self.armor))))
        self.hp -= effective
        self.hit_flash_timer = 0.12

        pct = self.hp_percent
        if pct <= 0.0:
            self.hp = 0
            self.alive = False
            self.state = "destroyed"
            self.kill()
            return True
        elif pct <= 0.25:
            self.state = "critical"
        elif pct <= 0.65:
            self.state = "damaged"
        else:
            self.state = "active"

        return False

    def update(self, dt: float, *args, **kwargs) -> list:
        if not self.alive:
            return []

        self.time_accum += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # Update active shield state
        alive_gens = [g for g in self.shield_generators if getattr(g, "alive", False)]
        self.is_shielded = len(alive_gens) > 0

        self._render()
        return []

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        r = self.radius

        col_outer = self.catalog_data["color_outer"]
        col_inner = self.catalog_data["color_inner"]

        # Base reinforced fortification
        pygame.draw.rect(self.image, col_outer, (cx - r, cy - r, r * 2, r * 2), border_radius=16)
        pygame.draw.rect(self.image, (100, 116, 139), (cx - r, cy - r, r * 2, r * 2), 3, border_radius=16)

        # Internal glowing reactor / command core
        pulse = int(r * 0.45 + 4 * math.sin(self.time_accum * 4.0))
        pygame.draw.circle(self.image, col_inner, (cx, cy), pulse)
        pygame.draw.circle(self.image, COLOR_WHITE, (cx, cy), max(3, pulse - 8))

        # Protective energy shield barrier
        if self.is_shielded:
            shield_r = r + 14
            shield_alpha = int(180 + 60 * math.sin(self.time_accum * 6.0))
            pygame.draw.circle(self.image, (56, 189, 248, max(0, min(255, shield_alpha))), (cx, cy), shield_r, 4)
            pygame.draw.circle(self.image, (180, 230, 255, 120), (cx, cy), shield_r - 4, 1)

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
