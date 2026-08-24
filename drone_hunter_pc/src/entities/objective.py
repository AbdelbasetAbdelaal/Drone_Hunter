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
    AIRCRAFT_INTERCEPTOR, AIRCRAFT_ATTACK,
    PHASE_OBJECTIVE_CRITICAL, PHASE_OBJECTIVE_DESTROYED,
    LAYER_OUTER, LAYER_MIDDLE, LAYER_INNER
)
from src.entities.bullet import EnemyBullet, HomingMissile
from src.entities.enemy import Enemy


# -----------------------------------------------------------------------------
# SHIELD GENERATOR PERIMETER ENTITY
# -----------------------------------------------------------------------------
class ShieldGenerator(pygame.sprite.Sprite):
    """Auxiliary power structure providing invulnerability to the Ground Objective."""
    def __init__(self, pos: Tuple[float, float], parent_objective=None, defense_layer: str = LAYER_INNER):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.parent_objective = parent_objective
        self.defense_layer = defense_layer
        self.max_hp = 120
        self.hp = self.max_hp
        self.armor = 0.10
        self.size = 50
        self.radius = 24
        self.enemy_type = "shield_generator"
        self.score_value = 150
        self.color = COLOR_SHIELD
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
    def __init__(self, pos: Tuple[float, float], scan_radius: float = 950.0, defense_layer: str = LAYER_MIDDLE):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.scan_radius = scan_radius
        self.defense_layer = defense_layer
        self.state = RADAR_STATE_SCANNING
        self.max_hp = 140
        self.hp = self.max_hp
        self.armor = 0.05
        self.size = 64
        self.radius = 28
        self.enemy_type = "radar"
        self.score_value = 200
        self.color = COLOR_CYAN
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

    def update(self, dt: float, player_pos: Tuple[float, float] = (0, 0), player_obj=None, *args, **kwargs) -> list:
        if not self.alive:
            return []
        
        self.sweep_angle = (self.sweep_angle + self.sweep_speed * dt) % 360.0
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if player_obj and getattr(player_obj, "is_cloaked", False):
            self.is_player_detected = False
            self.state = RADAR_STATE_SCANNING
            self._render()
            return []

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
    def __init__(self, pos: Tuple[float, float], aa_type: str = AA_TYPE_LIGHT, defense_layer: str = LAYER_INNER):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.aa_type = aa_type
        self.defense_layer = defense_layer
        
        if aa_type == AA_TYPE_LIGHT:
            self.max_hp = 160
            self.fire_cooldown_max = 2.0
            self.range = 700.0
            self.projectile_speed = 420.0
            self.projectile_damage = 14
            self.color = COLOR_CYAN
            self.size = 56
            self.telegraph_duration = 0.35
        elif aa_type == AA_TYPE_HEAVY:
            self.max_hp = 260
            self.fire_cooldown_max = 3.0
            self.range = 800.0
            self.projectile_speed = 360.0
            self.projectile_damage = 22
            self.color = COLOR_GOLD
            self.size = 68
            self.telegraph_duration = 0.50
        else: # AA_TYPE_MISSILE
            self.max_hp = 220
            self.fire_cooldown_max = 4.0
            self.range = 900.0
            self.projectile_speed = 300.0
            self.projectile_damage = 28
            self.color = COLOR_CRIMSON
            self.size = 64
            self.telegraph_duration = 0.65

        self.hp = self.max_hp
        self.armor = 0.15
        self.radius = self.size // 2
        self.enemy_type = "aa_platform"
        self.score_value = 250
        self.alive = True
        self.hit_flash_timer = 0.0
        
        self.fire_timer = random.uniform(0.8, self.fire_cooldown_max)
        # Stagger fire timers so nearby AAs don't create unreadable projectile walls
        self.fire_timer += random.uniform(0.0, self.fire_cooldown_max * 0.5)
        self.fire_cooldown_jitter = random.uniform(-0.1, 0.2)
        self.turret_angle = 180.0
        self.is_telegraphing = False
        self.telegraph_timer = 0.0

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

    def update(self, dt: float, player_pos: Tuple[float, float] = (0, 0), player_obj=None, *args, **kwargs) -> list:
        if not self.alive:
            return []
        
        new_bullets = []
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if player_obj and getattr(player_obj, "is_cloaked", False):
            self.is_telegraphing = False
            self._render()
            return []

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
                    self.fire_timer = self.fire_cooldown_max + self.fire_cooldown_jitter
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

        # Telegraph charge flare at barrel tip
        if self.is_telegraphing:
            charge_r = int(5 + 3 * math.sin(pygame.time.get_ticks() * 0.02)) if pygame.get_init() else 6
            pygame.draw.circle(self.image, (255, 200, 50), (int(round(bx)), int(round(by))), charge_r)
            pygame.draw.circle(self.image, COLOR_WHITE, (int(round(bx)), int(round(by))), max(2, charge_r - 3))

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 160), unsetcolor=(0, 0, 0, 0))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# -----------------------------------------------------------------------------
# COMBAT AIRCRAFT ENEMY ENTITY
# -----------------------------------------------------------------------------
class CombatAircraft(Enemy):
    """High-speed airborne hostile aircraft performing dogfight strafing runs."""
    def __init__(self, pos: Tuple[float, float], aircraft_type: str = AIRCRAFT_INTERCEPTOR, defense_layer: str = LAYER_INNER, **kwargs):
        super().__init__(enemy_type=aircraft_type, pos=pos, **kwargs)
        self.aircraft_type = aircraft_type
        self.defense_layer = defense_layer
        
        if aircraft_type == AIRCRAFT_INTERCEPTOR:
            self.max_hp = 35
            self.speed = 300.0
            self.points = 240
            self.color_outer = (239, 68, 68) # Red Jet
            self.color_inner = COLOR_GOLD
            self.size = 44
            self.burst_cooldown = 0.80
            self.projectile_damage = 12
        else: # AIRCRAFT_ATTACK
            self.max_hp = 60
            self.speed = 240.0
            self.points = 320
            self.color_outer = (59, 130, 246) # Blue Bomber
            self.color_inner = COLOR_WHITE
            self.size = 52
            self.burst_cooldown = 1.20
            self.projectile_damage = 16

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

        # Suppress attacks and break away if player is cloaked
        if player_obj and getattr(player_obj, "is_cloaked", False):
            self.ai_state = "reposition"
            self._render_aircraft_sprite()
            return []

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

            # Fire short readable burst
            if self.state_timer >= getattr(self, "burst_cooldown", 1.2):
                self.state_timer = 0.0
                cx, cy = self.rect.center
                new_bullets.append(EnemyBullet((cx, cy), player_pos, speed=360.0, damage=self.projectile_damage))
                if dist < 280.0:
                    self.ai_state = "reposition"
                    self.state_timer = 0.0
        elif self.ai_state == "reposition":
            # Evasive breakaway — fly perpendicular and away from player vector for breathing room
            self.state_timer += dt
            perp = pygame.Vector2(-norm_to_p.y, norm_to_p.x) * self.strafe_dir
            away = -norm_to_p
            move_vec = (perp * 0.6 + away * 0.4).normalize()
            self.pos += move_vec * self.speed * dt
            self.heading_angle = math.degrees(math.atan2(move_vec.y, move_vec.x))
            # Circle back after a 1.5s disengage, never hover over player
            if self.state_timer >= 1.5 or dist > 650.0:
                self.ai_state = "approach"
                self.state_timer = 0.0

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
        self.enemy_type = "objective"
        self.score_value = self.catalog_data["reward_score"]
        self.scrap_reward = self.catalog_data["reward_scrap"]
        self.color = self.catalog_data["color_inner"]
        
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

        # Visual polish: beacon, outline glow, damage effects
        self.beacon_timer = 0.0
        self.outline_glow_timer = 0.0
        self.last_hit_time = 0.0
        self.hit_effect_timer = 0.0
        self.crack_intensity = 0.0
        self.damage_flash_timer = 0.0
        self.destruction_sequence_active = False
        self.destruction_timer = 0.0
        self._spark_offsets: List[Tuple[float, float, float]] = []

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
        self.hit_effect_timer = 0.15
        self.damage_flash_timer = 0.10
        self.last_hit_time = self.time_accum

        # Spawn localized hit sparks at random points on the objective rim
        for _ in range(4):
            ang = random.uniform(0, math.tau)
            sd = self.radius * 0.7
            self._spark_offsets.append((
                math.cos(ang) * sd,
                math.sin(ang) * sd,
                random.uniform(0.1, 0.3),
            ))

        pct = self.hp_percent
        if pct <= 0.0:
            self.hp = 0
            self.alive = False
            self.state = "destroyed"
            self.kill()
            return True
        elif pct <= 0.25:
            self.state = "critical"
            self.crack_intensity = max(self.crack_intensity, 1.0)
        elif pct <= 0.50:
            self.state = "damaged"
            self.crack_intensity = max(self.crack_intensity, 0.5)
        else:
            self.state = "active"

        return False

    def update(self, dt: float, *args, **kwargs) -> list:
        if not self.alive:
            return []

        self.time_accum += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.hit_effect_timer > 0:
            self.hit_effect_timer -= dt
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
        if self.beacon_timer <= 0:
            self.beacon_timer += dt
        self.outline_glow_timer += dt

        # Update spark offsets (fade out)
        updated_sparks = []
        for sx, sy, life in self._spark_offsets:
            life -= dt
            if life > 0:
                updated_sparks.append((sx, sy, life))
        self._spark_offsets = updated_sparks

        # Update active shield state
        alive_gens = [g for g in self.shield_generators if getattr(g, "alive", False)]
        self.is_shielded = len(alive_gens) > 0

        self._render()
        return []

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        ix, iy = self.image.get_width() // 2, self.image.get_height() // 2
        r = self.radius
        cx = ix
        cy = iy

        col_outer = self.catalog_data["color_outer"]
        col_inner = self.catalog_data["color_inner"]

        # --- Damage Discoloration Overlay ---
        # At 50% HP: surface cracks pattern; at CRITICAL (25%): deeper discoloration + more cracks
        damage_pct = self.hp_percent
        is_critical = damage_pct <= 0.25
        is_damaged = damage_pct <= 0.50

        # Pulsing outline glow (always visible, intensity scales with phase)
        glow_alpha = int(40 + 25 * math.sin(self.outline_glow_timer * 5.0) + 15 * math.sin(self.outline_glow_timer * 2.3))
        glow_r = r + 18 + (6 if is_critical else (3 if is_damaged else 0))
        if is_critical:
            glow_col = COLOR_NEON_RED
            glow_alpha = int(60 + 50 * math.sin(self.outline_glow_timer * 8.0))
        elif is_damaged:
            glow_col = COLOR_CRIMSON
        else:
            glow_col = COLOR_SHIELD

        # Draw multiple concentric glow rings for a "halo" effect
        for ring_i in range(3):
            ring_r = glow_r + ring_i * 6
            ring_a = max(0, glow_alpha - ring_i * 45)
            pygame.draw.circle(self.image, (*glow_col, ring_a), (cx, cy), ring_r, 3)

        # Base reinforced fortification
        pygame.draw.rect(self.image, col_outer, (cx - r, cy - r, r * 2, r * 2), border_radius=16)
        pygame.draw.rect(self.image, (100, 116, 139), (cx - r, cy - r, r * 2, r * 2), 3, border_radius=16)

        # Damage crack overlay (visible at 50% and below)
        if is_damaged or is_critical:
            crack_phase = self.time_accum * 3.0
            crack_alpha = int(140 + 60 * math.sin(crack_phase))
            crack_color = (180, 180, 190, min(255, crack_alpha))
            crack_density = 6 if is_critical else 3
            for ci in range(crack_density):
                angle = (math.tau / max(1, crack_density)) * ci + self.time_accum * 0.5
                ex = cx + math.cos(angle) * r * 0.7
                ey = cy + math.sin(angle) * r * 0.7
                pygame.draw.line(self.image, crack_color, (cx, cy), (ex, ey), 2)
                # Branch cracks
                branch_ang = angle + 0.4
                bx = cx + math.cos(branch_ang) * r * 0.5
                by = cy + math.sin(branch_ang) * r * 0.5
                pygame.draw.line(self.image, crack_color, (ex, ey), (bx, by), 1)

        # Critical discoloration (reddish wash)
        if is_critical:
            flash_a = int(40 + 30 * math.sin(self.time_accum * 12.0))
            flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((*COLOR_CRIMSON[:3], flash_a))
            self.image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Internal glowing reactor / command core
        pulse = int(r * 0.45 + 4 * math.sin(self.time_accum * 4.0))
        if is_critical:
            pulse = int(r * 0.30 + 2 * math.sin(self.time_accum * 10.0))  # erratic pulse
        elif is_damaged:
            pulse = int(r * 0.38 + 3 * math.sin(self.time_accum * 6.0))
        core_col = col_inner if not is_critical else COLOR_NEON_RED
        pygame.draw.circle(self.image, core_col, (cx, cy), pulse)
        pygame.draw.circle(self.image, COLOR_WHITE, (cx, cy), max(3, pulse - 8))

        # Hit flash on damage
        if self.damage_flash_timer > 0 or self.hit_flash_timer > 0:
            mask_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(mask_surf, (255, 255, 255, 140), (cx, cy), r + 10)
            self.image.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Protective energy shield barrier
        if self.is_shielded:
            shield_r = r + 14
            shield_alpha = int(180 + 60 * math.sin(self.time_accum * 6.0))
            pygame.draw.circle(self.image, (56, 189, 248, max(0, min(255, shield_alpha))), (cx, cy), shield_r, 4)
            pygame.draw.circle(self.image, (180, 230, 255, 120), (cx, cy), shield_r - 4, 1)

        # Beacon effect: rotating light above the objective
        beacon_y = cy - r - 28
        beacon_angle = self.time_accum * 4.0
        beacon_r = 14
        beacon_alpha = int(170 + 80 * math.sin(self.time_accum * 6.0))
        bx = cx + math.cos(beacon_angle) * (beacon_r + 4)
        by = beacon_y + math.sin(beacon_angle) * (beacon_r + 4)
        pygame.draw.circle(self.image, (*COLOR_SHIELD, beacon_alpha), (int(bx), int(by)), beacon_r)
        pygame.draw.circle(self.image, COLOR_WHITE, (int(bx), int(by)), max(3, beacon_r - 6))
        # Beacon vertical beam
        pygame.draw.line(self.image, (*COLOR_SHIELD, 80), (cx, beacon_y + beacon_r), (cx, beacon_y - 10), 2)

        # --- HP / Shield bar directly below objective ---
        bar_w = int(r * 1.6)
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy + r + 18
        # Background
        pygame.draw.rect(self.image, (15, 23, 42, 200), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        # HP fill
        hp_pct = self.hp_percent
        fill_w = max(0, int(bar_w * hp_pct))
        hp_col = COLOR_SHIELD if self.is_shielded else (COLOR_CRIMSON if hp_pct < 0.3 else COLOR_GOLD)
        if fill_w > 0:
            pygame.draw.rect(self.image, hp_col, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        # Shield overlay bar (if shielded)
        if self.is_shielded:
            sh_fill = max(0, int(bar_w * 1.0))
            pygame.draw.rect(self.image, (*COLOR_SHIELD, 120), (bar_x, bar_y, sh_fill, bar_h), 1, border_radius=3)
        pygame.draw.rect(self.image, (51, 65, 85), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        # Hit spark effects (localized on impact)
        if self._spark_offsets:
            for sx, sy, life in self._spark_offsets:
                alpha = int(min(255, 200 * life))
                spark_r = int(max(1, 4 * life))
                pygame.draw.circle(self.image, (*COLOR_NEON_RED, alpha),
                                   (int(cx + sx), int(cy + sy)), spark_r)

    def draw_health_bar_world(self, canvas: pygame.Surface, camera_offset: tuple[float, float]):
        """Draws a large, readable HP/shield bar in world space below the objective.

        Called by the renderer for screen-space priority readouts.
        """
        if not self.alive:
            return
        ox, oy = camera_offset
        cx = int(round(self.pos.x - ox))
        cy = int(round(self.pos.y - oy))
        hp_bar_w = 120
        hp_bar_h = 10
        bx = cx - hp_bar_w // 2
        by = cy + self.radius + 20
        # Background
        pygame.draw.rect(canvas, (15, 23, 42, 220), (bx, by, hp_bar_w, hp_bar_h), border_radius=4)
        # HP fill
        hp_pct = self.hp_percent
        fill_w = max(0, int(hp_bar_w * hp_pct))
        hp_col = COLOR_SHIELD if self.is_shielded else (COLOR_CRIMSON if hp_pct < 0.3 else COLOR_GOLD)
        if fill_w > 0:
            pygame.draw.rect(canvas, hp_col, (bx, by, fill_w, hp_bar_h), border_radius=4)
        # Shield indicator overlay
        if self.is_shielded:
            pygame.draw.rect(canvas, COLOR_SHIELD, (bx, by, hp_bar_w, hp_bar_h), 2, border_radius=4)
        pygame.draw.rect(canvas, (51, 65, 85), (bx, by, hp_bar_w, hp_bar_h), 1, border_radius=4)
