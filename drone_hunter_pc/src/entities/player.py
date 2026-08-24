"""
================================================================================
                    DRONE HUNTER 2D - PLAYER COMBAT DRONE
================================================================================
Player combat drone entity featuring 2D kinematic flight physics, 360-degree
mouse aiming, dual hardpoint weapon firing, active tactical abilities (Overdrive,
Cloak, EMP, Roll), unified shield hit absorption, and dynamic skin themes.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN, COLOR_GOLD,
    COLOR_EMERALD, COLOR_CRIMSON, COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD,
    COLOR_OVERCLOCK, COLOR_SLOWMO, COLOR_BEAM, COLOR_MISSILE, COLOR_TESLA,
    COLOR_CLUSTER, COLOR_WHITE
)
from src.data.game_data import (
    HORIZONTAL_SPEED, VERTICAL_SPEED, ACCELERATION, FRICTION,
    PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY, ENERGY_REGEN_RATE, BOOST_DRAIN_RATE,
    EMP_COOLDOWN_MAX, ROLL_COOLDOWN, ROLL_DURATION, ROLL_SPEED_BOOST,
    CLOAK_DURATION, CLOAK_COOLDOWN_MAX, OVERDRIVE_DURATION, OVERDRIVE_COOLDOWN_MAX,
    WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, WEAPON_RAPID, WEAPON_PLASMA,
    WEAPON_RAIL, WEAPON_BARRAGE, WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP,
    WEAPON_DEFS, WEAPON_UPGRADES, DRONE_SKINS, DRONE_CLASSES, DRONE_CLASS_STRIKER
)
from src.entities.bullet import (
    Bullet, HomingMissile, ContinuousBeam, TeslaArcBeam, ClusterTorpedo,
    HeavyPlasmaOrb, RailgunSlug, BarrageMissile, EMPPulse
)
from src.rendering.player_renderer import PlayerRenderer
from src.rendering.sprite_manager import get_sprite_manager

class WingmanDrone:
    """Autonomous escort mini-drone providing supportive auto-fire."""
    def __init__(self, offset_x: float, offset_y: float):
        self.offset = pygame.Vector2(offset_x, offset_y)
        self.pos = pygame.Vector2(0, 0)
        self.shoot_timer = random.uniform(0.1, 0.4)
        self.angle_deg = 0.0

    def update(self, dt: float, parent_pos: pygame.Vector2, targets_group=None) -> list[Bullet]:
        self.pos = parent_pos + self.offset
        self.shoot_timer -= dt
        bullets = []

        if self.shoot_timer <= 0 and targets_group and len(targets_group) > 0:
            self.shoot_timer = 0.45
            nearest = min(targets_group, key=lambda t: (t.rect.centerx - self.pos.x)**2 + (t.rect.centery - self.pos.y)**2)
            tx, ty = nearest.rect.center
            bullets.append(Bullet((self.pos.x, self.pos.y), (tx, ty), speed=850.0, damage=16, color=COLOR_CYAN, owner="wingman", weapon_id="wingman_pulse"))

        return bullets

    def draw(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        ox, oy = camera_offset
        px, py = int(round(self.pos.x - ox)), int(round(self.pos.y - oy))
        pygame.draw.circle(canvas, (15, 23, 42), (px, py), 10)
        pygame.draw.circle(canvas, COLOR_CYAN, (px, py), 10, 2)
        pygame.draw.circle(canvas, COLOR_WHITE, (px, py), 4)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float] = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)):
        super().__init__()
        
        # Position & Kinematic Flight Physics (Fast-Paced, Highly Responsive)
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 6400.0
        self.drag = 5.0
        self.max_speed = HORIZONTAL_SPEED
        self.is_accelerating = False
        
        # Mouse Aiming & Orientation
        self.aim_angle = 0.0
        self.facing_angle_deg = 0.0
        self.tilt_y = 0.0
        
        # Arena Boundaries (2400x1400 World Arena)
        self.arena_width = float(WORLD_WIDTH)
        self.arena_height = float(WORLD_HEIGHT)
        
        # Visual & Combat Effects
        self.renderer = PlayerRenderer()
        self.muzzle_flash_timer = 0.0
        self.damage_flash_timer = 0.0
        self.is_destroyed = False
        self.destruction_timer = 0.0
        
        # Hull & Energy
        self._upgrade_bonus_health = 0.0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.max_energy = PLAYER_MAX_ENERGY
        self.energy = PLAYER_MAX_ENERGY
        self.weapon_effectiveness = 1.0
        self.armor = 0
        self.alive = True

        # Shield Hit System
        self.shield_hits = 0
        self.damage_grace_timer = 0.0
        self.damage_grace_duration = 0.30

        # Ability Timers & Cooldowns
        self.emp_cooldown = 0.0
        self.emp_cooldown_max = EMP_COOLDOWN_MAX
        self.roll_timer = 0.0
        self.roll_cooldown = 0.0
        self.is_rolling = False
        
        self.cloak_timer = 0.0
        self.cloak_cooldown = 0.0
        self.is_cloaked = False
        self.has_cloak_upgrade = False

        self.overdrive_timer = 0.0
        self.overdrive_cooldown = 0.0
        self.overdrive_duration_max = OVERDRIVE_DURATION
        self.overdrive_cooldown_max = OVERDRIVE_COOLDOWN_MAX

        # EMP Jammed Mechanic
        self.emp_jammed_timer = 0.0

        # Combat & Upgrades
        self.overclock_timer = 0.0
        self.shoot_timer = 0.0
        self.invulnerable_timer = 0.0
        self.agility_mult = 1.0
        self.cooldown_mult = 1.0

        # Weapon Mounts & State
        self._rapid_side = 0
        self._missile_side = 0
        self.skin_theme = 0
        self.drone_class = "striker"
        self.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE]
        self.current_weapon_idx = 0
        self.active_weapon = WEAPON_PULSE
        self.weapon_cooldowns = {w: 0.0 for w in WEAPON_DEFS}
        self.weapon_upgrade_levels: dict[str, int] = {}

        # Wingmen Escort Squad
        self.wingmen: list[WingmanDrone] = []

        # Aesthetics
        self.base_image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(round(pos[0])), int(round(pos[1]))))
        self.radius = 28
        
        # Apply initial drone class profile
        self.drone_class_id = DRONE_CLASS_STRIKER
        self.skin_theme = 0
        self.set_drone_class(DRONE_CLASS_STRIKER)

    def set_drone_class(self, class_id: str):
        """Configures player statistics, weapon loadout, and weapon mounts for the selected drone class."""
        self.drone_class_id = class_id
        from src.data.game_data import get_drone_class_by_id
        c_data = get_drone_class_by_id(self.drone_class_id)
        
        self.max_speed = HORIZONTAL_SPEED * c_data.get("speed_mult", 1.0)
        self.acceleration = 6400.0 * c_data.get("accel_mult", 1.0)
        self.drag = 5.0
        bonus_hp = getattr(self, "_upgrade_bonus_health", 0.0)
        self.max_health = c_data.get("max_health", 100) + bonus_hp
        self.health = self.max_health
        self.armor = c_data.get("armor", 0)
        self.available_weapons = list(c_data.get("weapons", []))
        if self.active_weapon not in self.available_weapons and self.available_weapons:
            self.active_weapon = self.available_weapons[0]
            self.current_weapon_idx = 0
        for w in self.available_weapons:
            if w not in self.weapon_cooldowns:
                self.weapon_cooldowns[w] = 0.0
        self._render_drone_sprite()

    def apply_drone_class(self, class_idx: int):
        """Legacy alias mapping int class_idx to set_drone_class for backward compatibility."""
        mapping = ["striker", "interceptor", "assault", "arc", "command"]
        idx = max(0, min(len(mapping) - 1, class_idx))
        self.set_drone_class(mapping[idx])
        self.set_visual_skin(idx)

    def set_visual_skin(self, skin_idx: int):
        """Sets the visual skin (color palette) for the drone."""
        from src.data.game_data import DRONE_SKINS
        self.skin_theme = max(0, min(len(DRONE_SKINS) - 1, skin_idx))
        self._render_drone_sprite()

    def get_mount_world_pos(self, mount_name: str = "primary") -> tuple[float, float]:
        """Calculates rotated world coordinates for a local-space weapon mount point."""
        from src.data.game_data import get_drone_class_by_id, DRONE_MOUNT_PROFILES
        drone_class = get_drone_class_by_id(self.drone_class_id)
        class_id = drone_class.get("class_id", "striker")
        
        profile = DRONE_MOUNT_PROFILES.get(class_id, drone_class.get("mounts", {}))
        
        # Check alias fallbacks
        fallback = profile.get("primary", (38.0, 0.0))
        fwd_off, lat_off = profile.get(mount_name, fallback)
        
        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        world_x = self.pos.x + (cos_a * fwd_off) + (-sin_a * lat_off)
        world_y = self.pos.y + (sin_a * fwd_off) + (cos_a * lat_off)
        return (world_x, world_y)

    # --- Shield Property Aliases for Backwards Compatibility ---
    @property
    def shield_charge(self) -> int:
        return self.shield_hits * 50

    @shield_charge.setter
    def shield_charge(self, value: int):
        self.shield_hits = max(0, int(value // 50) if value > 0 else 0)

    @property
    def is_invulnerable(self) -> bool:
        return self.is_rolling or self.invulnerable_timer > 0.0 or self.overdrive_timer > 0.0 or self.damage_grace_timer > 0.0

    @property
    def is_jammed(self) -> bool:
        return self.emp_jammed_timer > 0.0

    @property
    def speed(self) -> float:
        boost = 1.40 if self.overdrive_timer > 0.0 else 1.0
        return self.max_speed * self.agility_mult * boost

    def activate_shield(self, hits: int = 3):
        """Activates defensive energy shield for given hit charges."""
        self.shield_hits = max(self.shield_hits, hits)

    def trigger_emp(self) -> bool:
        """Triggers EMP blast if off cooldown and not jammed."""
        if self.is_jammed:
            return False
        if self.emp_cooldown <= 0.0:
            self.emp_cooldown = self.emp_cooldown_max
            return True
        return False

    def trigger_emp_jammed(self, duration: float = 3.0):
        """Jams player systems upon being hit by EMP Boss attack."""
        if not self.is_invulnerable:
            self.emp_jammed_timer = max(self.emp_jammed_timer, duration)

    def trigger_overdrive(self) -> bool:
        """Activates Overdrive Ultimate (hyper-fire mode, speed boost, invulnerability)."""
        if self.is_jammed:
            return False
        if self.overdrive_cooldown <= 0.0 and self.overdrive_timer <= 0.0:
            self.overdrive_timer = getattr(self, "overdrive_duration_max", OVERDRIVE_DURATION)
            self.overdrive_cooldown = getattr(self, "overdrive_cooldown_max", OVERDRIVE_COOLDOWN_MAX)
            self.activate_shield(3)
            self.energy = self.max_energy
            return True
        return False

    def trigger_roll(self, dir_x: float = 1.0) -> bool:
        """Performs high-speed evasive barrel roll."""
        if self.is_jammed:
            return False
        if self.roll_cooldown <= 0.0 and not self.is_rolling:
            self.is_rolling = True
            self.roll_timer = ROLL_DURATION
            self.roll_cooldown = ROLL_COOLDOWN
            self.velocity.x += dir_x * (HORIZONTAL_SPEED * ROLL_SPEED_BOOST)
            return True
        return False

    def trigger_cloak(self) -> bool:
        """Activates tactical stealth cloak."""
        if self.is_jammed:
            return False
        if self.cloak_cooldown <= 0.0 and not self.is_cloaked:
            self.is_cloaked = True
            self.cloak_timer = CLOAK_DURATION
            self.cloak_cooldown = CLOAK_COOLDOWN_MAX
            return True
        return False

    def cycle_weapon(self, direction: int = 1):
        """Switches active primary weapon."""
        if not self.available_weapons:
            return
        self.current_weapon_idx = (self.current_weapon_idx + direction) % len(self.available_weapons)
        self.active_weapon = self.available_weapons[self.current_weapon_idx]

    def select_weapon(self, index: int):
        """Selects unlocked weapon by index."""
        if self.available_weapons and 0 <= index < len(self.available_weapons):
            self.current_weapon_idx = index
            self.active_weapon = self.available_weapons[index]

    def set_weapon(self, weapon_name: str):
        """Directly equips weapon by identifier with fallback for test overrides."""
        if weapon_name in self.available_weapons:
            self.active_weapon = weapon_name
            self.current_weapon_idx = self.available_weapons.index(weapon_name)
        elif weapon_name in WEAPON_DEFS:
            self.available_weapons.append(weapon_name)
            self.active_weapon = weapon_name
            self.current_weapon_idx = len(self.available_weapons) - 1

    def spawn_wingman(self):
        """Spawns an escort wingman drone upon picking up a powerup (up to 2)."""
        if len(self.wingmen) == 0:
            self.wingmen.append(WingmanDrone(-42, -40))
        elif len(self.wingmen) == 1:
            self.wingmen.append(WingmanDrone(-42, 40))

    def trigger_overclock(self, duration: float = 6.0):
        """Triggers weapon overclock fire rate boost."""
        self.overclock_timer = max(self.overclock_timer, duration)

    def cycle_skin(self, step: int = 1) -> int:
        """Cycles aesthetic drone chassis theme."""
        from src.data.game_data import DRONE_SKINS
        next_skin = (self.skin_theme + step) % len(DRONE_SKINS)
        self.set_visual_skin(next_skin)
        return self.skin_theme

    def cycle_drone_class(self, step: int = 1) -> str:
        """Cycles through available drone combat classes and updates chassis aesthetics."""
        from src.data.game_data import DRONE_CLASSES
        class_ids = list(DRONE_CLASSES.keys())
        try:
            curr_idx = class_ids.index(self.drone_class_id)
        except ValueError:
            curr_idx = 0
        next_idx = (curr_idx + step) % len(class_ids)
        next_id = class_ids[next_idx]
        self.set_drone_class(next_id)
        self.set_visual_skin(next_idx)
        return self.drone_class_id

    def set_skin(self, index: int):
        self.set_visual_skin(index)

    def apply_shop_upgrades(self, upgrades: dict):
        """Applies persistent hangar upgrade statistics."""
        bat_lvl = upgrades.get("battery", 0)
        self._upgrade_bonus_health = bat_lvl * 25.0

        spd_lvl = upgrades.get("speed", 0)
        self.agility_mult = 1.0 + (spd_lvl * 0.12)

        fr_lvl = upgrades.get("fire_rate", 0)
        self.cooldown_mult = max(0.50, 1.0 - (fr_lvl * 0.08))

        emp_lvl = upgrades.get("emp_recharge", 0)
        self.emp_cooldown_max = max(6.0, EMP_COOLDOWN_MAX - (emp_lvl * 1.5))

        wm_lvl = upgrades.get("wingman", 0)
        self.wingmen.clear()
        if wm_lvl >= 1:
            self.wingmen.append(WingmanDrone(-42, -40))
        if wm_lvl >= 2:
            self.wingmen.append(WingmanDrone(-42, 40))

        clk_lvl = upgrades.get("cloak", 0)
        self.has_cloak_upgrade = (clk_lvl > 0)

        od_lvl = upgrades.get("overdrive", 0)
        self.overdrive_duration_max = OVERDRIVE_DURATION + (od_lvl * 1.5)
        self.overdrive_cooldown_max = max(12.0, OVERDRIVE_COOLDOWN_MAX - (od_lvl * 3.0))

        # Re-apply current drone class weapon loadout and upgrade bonuses
        self.set_drone_class(self.drone_class_id)

    def apply_weapon_upgrades(self, weapon_upgrades: dict):
        """Stores weapon-specific upgrade levels for per-weapon stat scaling."""
        self.weapon_upgrade_levels = {str(k): max(0, int(v)) for k, v in weapon_upgrades.items()}


    def take_damage(self, amount: float, source: str = "bullet", ignore_grace: bool = False) -> bool:
        """Applies damage to shields and health hull. Returns True if destroyed."""
        if not ignore_grace and self.is_invulnerable:
            return False

        self.damage_flash_timer = 0.18

        if self.shield_hits > 0:
            self.shield_hits -= 1
            return False

        effective_damage = max(1.0, float(amount) - float(self.armor))
        self.health = max(0.0, self.health - effective_damage)
        self.damage_grace_timer = self.damage_grace_duration

        if self.health <= 0.0:
            if not self.is_destroyed:
               self.alive = False
               self.is_destroyed = True
               self.destruction_timer = 1.4
               return True
        return False

    def can_shoot(self) -> bool:
        """Checks whether the currently equipped weapon is off cooldown and ready to fire."""
        if not self.alive or self.is_destroyed or self.is_jammed or self.is_rolling:
            return False
        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        cost = w_def.get("energy_cost", 0.0)
        if self.energy < cost and self.overdrive_timer <= 0.0:
            return False
        cd = self.weapon_cooldowns.get(self.active_weapon, 0.0)
        return cd <= 0.0

    def shoot(self, target_pos: tuple[float, float], level: int = 1, targets_group=None, particle_manager=None) -> list[pygame.sprite.Sprite]:
        """Fires projectiles originating from exact local-space weapon mount points."""
        if not self.can_shoot():
            return []

        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        w_upg = WEAPON_UPGRADES.get(self.active_weapon, {})
        base_cd = w_upg.get("base_cooldown", w_def.get("cooldown", 0.18))
        cost = w_def.get("energy_cost", 0.0)
        base_dmg = w_upg.get("base_damage", w_def.get("damage", 12))
        base_spd = w_upg.get("base_projectile_speed", w_def.get("speed", 650.0))
        w_lvl = self.weapon_upgrade_levels.get(self.active_weapon, 0)
        dmg = int((base_dmg + w_upg.get("upgrade_damage_per_lvl", 0) * w_lvl) * self.weapon_effectiveness)
        spd = float(base_spd + w_upg.get("upgrade_speed_per_lvl", 0.0) * w_lvl)
        col = w_def.get("color", COLOR_CYAN)
        proj_count = w_def.get("projectiles_per_shot", 1)
        spread_deg = w_def.get("spread_deg", 0.0)

        cd_scale = 0.50 if self.overdrive_timer > 0.0 else (0.65 if self.overclock_timer > 0.0 else 1.0)
        self.weapon_cooldowns[self.active_weapon] = max(0.05, base_cd + w_upg.get("upgrade_cooldown_per_lvl", 0.0) * w_lvl) * self.cooldown_mult * cd_scale

        if self.overdrive_timer <= 0.0:
            self.energy = max(0.0, self.energy - cost)

        # Update Aim Angle
        self.aim_angle = math.atan2(target_pos[1] - self.pos.y, target_pos[0] - self.pos.x)
        self.muzzle_flash_timer = 0.08

        # Subtle Recoil Impulse
        recoil_kick = 20.0
        self.velocity.x -= math.cos(self.aim_angle) * recoil_kick
        self.velocity.y -= math.sin(self.aim_angle) * recoil_kick

        bullets = []
        sm = get_sprite_manager()

        from src.entities.bullet import (
            Bullet, HomingMissile, ContinuousBeam, TeslaArcBeam, ClusterTorpedo,
            HeavyPlasmaOrb, RailgunSlug, BarrageMissile, EMPPulse
        )

        fwd_dx = math.cos(self.aim_angle) * 1500.0
        fwd_dy = math.sin(self.aim_angle) * 1500.0

        if self.active_weapon == WEAPON_PULSE:
            m_pos = self.get_mount_world_pos("primary_front_center")
            sprite = sm.get_projectile_sprite('pulse', (40, 12))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(Bullet(m_pos, t_pt, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if self.overdrive_timer > 0.0:
                od_dmg = int(dmg * 1.25)
                bullets.append(Bullet(m_pos, t_pt, angle_offset_deg=-10.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite, owner="player", weapon_id=self.active_weapon))
                bullets.append(Bullet(m_pos, t_pt, angle_offset_deg=10.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_RAPID:
            mount_key = "dual_left" if self._rapid_side == 0 else "dual_right"
            self._rapid_side = (self._rapid_side + 1) % 2
            m_pos = self.get_mount_world_pos(mount_key)
            sprite = sm.get_projectile_sprite('pulse', (32, 10))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(Bullet(m_pos, t_pt, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_SCATTER:
            # Multi-projectile spread originating from left and right weapon mounts
            left_pos = self.get_mount_world_pos("left")
            right_pos = self.get_mount_world_pos("right")
            sprite = sm.get_projectile_sprite('scatter', (40, 12))
            
            start_ang = -spread_deg / 2
            step = spread_deg / max(1, proj_count - 1) if proj_count > 1 else 0
            for i in range(proj_count):
                ang = start_ang + step * i
                origin = left_pos if i % 2 == 0 else right_pos
                t_pt = (origin[0] + fwd_dx, origin[1] + fwd_dy)
                bullets.append(Bullet(origin, t_pt, angle_offset_deg=ang, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(left_pos, self.aim_angle, self.active_weapon)
                particle_manager.spawn_muzzle_flash(right_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_MISSILE:
            mount_key = "left" if self._missile_side == 0 else "right"
            self._missile_side = (self._missile_side + 1) % 2
            m_pos = self.get_mount_world_pos(mount_key)
            sprite = sm.get_projectile_sprite('missile', (45, 16))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(HomingMissile(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_BARRAGE:
            pod_l = self.get_mount_world_pos("pod_left")
            pod_r = self.get_mount_world_pos("pod_right")
            sprite = sm.get_projectile_sprite('missile', (36, 12))
            t_pt_l = (pod_l[0] + fwd_dx, pod_l[1] + fwd_dy)
            t_pt_r = (pod_r[0] + fwd_dx, pod_r[1] + fwd_dy)
            bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-12.0, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-4.0, damage=dmg, speed=spd * 0.95, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=4.0, damage=dmg, speed=spd * 0.95, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=12.0, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(pod_l, self.aim_angle, self.active_weapon)
                particle_manager.spawn_muzzle_flash(pod_r, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_PLASMA:
            m_pos = self.get_mount_world_pos("heavy_front_center")
            sprite = sm.get_projectile_sprite('plasma', (36, 36))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(HeavyPlasmaOrb(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_RAIL:
            m_pos = self.get_mount_world_pos("rail_front")
            sprite = sm.get_projectile_sprite('rail', (64, 14))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(RailgunSlug(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_BEAM:
            self._fired_this_frame = True
            if getattr(self, "active_beam", None) is None or not self.active_beam.alive():
                m_pos = self.get_mount_world_pos("beam_emitter")
                sprite = sm.get_projectile_sprite('beam', (52, 16))
                from src.entities.bullet import ContinuousBeam
                # Convert per-shot damage to high continuous DPS
                dps = dmg * 24.0
                self.active_beam = ContinuousBeam(m_pos, self.aim_angle, damage_per_second=dps, image=sprite, owner="player", weapon_id=self.active_weapon)
                bullets.append(self.active_beam)
                if particle_manager:
                    particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_TESLA:
            m_pos = self.get_mount_world_pos("energy_center")
            sprite = sm.get_projectile_sprite('tesla', (34, 34))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(TeslaArcBeam(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_CLUSTER:
            m_pos = self.get_mount_world_pos("primary")
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(ClusterTorpedo(m_pos, t_pt, damage=dmg, speed=spd, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_EMP:
            m_pos = self.get_mount_world_pos("energy_center")
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(EMPPulse(m_pos, t_pt, damage=dmg, speed=spd, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, self.aim_angle, self.active_weapon)

        return bullets



    def handle_input(self, keys, dt: float, mouse_pos: tuple[float, float] = None, input_state: dict = None):
        """Processes 360-degree vector flight kinematics, lateral banking, and mouse/analog stick aiming."""
        move_x = 0.0
        move_y = 0.0

        if input_state:
            move_x = input_state.get("move_x", 0.0)
            move_y = input_state.get("move_y", 0.0)
            aim_angle_override = input_state.get("aim_angle", None)
            if aim_angle_override is not None:
                self.aim_angle = aim_angle_override
        else:
            def _is_pressed(k):
                if isinstance(keys, dict):
                    return keys.get(k, False)
                try:
                    return bool(keys[k])
                except (IndexError, KeyError):
                    return False

            if _is_pressed(pygame.K_w) or _is_pressed(pygame.K_UP): move_y -= 1.0
            if _is_pressed(pygame.K_s) or _is_pressed(pygame.K_DOWN): move_y += 1.0
            if _is_pressed(pygame.K_a) or _is_pressed(pygame.K_LEFT): move_x -= 1.0
            if _is_pressed(pygame.K_d) or _is_pressed(pygame.K_RIGHT): move_x += 1.0

        move_vec = pygame.Vector2(move_x, move_y)
        if move_vec.length_squared() > 0.0:
            if not input_state and move_vec.length_squared() > 1.0:
                move_vec = move_vec.normalize()
            self.is_accelerating = True
            self.velocity += move_vec * (self.acceleration * self.agility_mult) * dt
        else:
            self.is_accelerating = False

        # Linear Inertial Drag & Smooth Deceleration
        drag_damping = max(0.0, 1.0 - (self.drag * dt))
        self.velocity *= drag_damping

        # Clamp Max Speed
        current_max = self.speed
        if self.velocity.length() > current_max:
            self.velocity.scale_to_length(current_max)

        # Update Aim Direction from Mouse (World Coordinates) if right stick aim is inactive
        if mouse_pos and (not input_state or input_state.get("aim_angle") is None):
            self.aim_angle = math.atan2(mouse_pos[1] - self.pos.y, mouse_pos[0] - self.pos.x)

        # Smooth Lateral Velocity Banking relative to Aim Angle
        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        lateral_speed = (-sin_a * self.velocity.x) + (cos_a * self.velocity.y)
        target_tilt = max(-26.0, min(26.0, (lateral_speed / max(1.0, current_max)) * 32.0))
        self.tilt_y += (target_tilt - self.tilt_y) * min(1.0, 12.0 * dt)

    def update(self, dt: float, targets_group=None) -> list[pygame.sprite.Sprite]:
        """Updates drone physics position, boundary clamping, timers, and energy regeneration."""
        # Handle Continuous Beam Lifecycle
        if getattr(self, "active_beam", None) is not None and self.active_beam.alive():
            if not getattr(self, "_fired_this_frame", False) or self.active_weapon != WEAPON_BEAM:
                self.active_beam.active = False
                self.active_beam = None
            else:
                m_pos = self.get_mount_world_pos("beam_emitter")
                self.active_beam.update_transform(m_pos, self.aim_angle, self.active_beam.length)
        self._fired_this_frame = False

        # Position Update
        self.pos += self.velocity * dt
        
        # Smooth World Arena Boundary Clamping
        pad = 36.0
        self.pos.x = max(pad, min(self.arena_width - pad, self.pos.x))
        self.pos.y = max(pad, min(self.arena_height - pad, self.pos.y))
        self.rect.center = (int(round(self.pos.x)), int(round(self.pos.y)))

        # Energy Regeneration
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + ENERGY_REGEN_RATE * dt)

        # Visual Flash Timers
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer = max(0.0, self.muzzle_flash_timer - dt)
        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)

        # Destruction Animation Timer
        if self.is_destroyed:
            self.destruction_timer = max(0.0, self.destruction_timer - dt)
            if self.destruction_timer <= 0:
                self.kill()

        # Ability Timers
        for w in self.weapon_cooldowns:
            if self.weapon_cooldowns[w] > 0:
                self.weapon_cooldowns[w] -= dt
                
        if self.invulnerable_timer > 0: self.invulnerable_timer -= dt
        if self.damage_grace_timer > 0: self.damage_grace_timer = max(0.0, self.damage_grace_timer - dt)
        if self.overclock_timer > 0: self.overclock_timer -= dt
        if self.emp_jammed_timer > 0: self.emp_jammed_timer = max(0.0, self.emp_jammed_timer - dt)
        if self.emp_cooldown > 0: self.emp_cooldown = max(0.0, self.emp_cooldown - dt)

        if self.overdrive_timer > 0:
            self.overdrive_timer = max(0.0, self.overdrive_timer - dt)
        if self.overdrive_cooldown > 0:
            self.overdrive_cooldown = max(0.0, self.overdrive_cooldown - dt)

        if self.is_rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.is_rolling = False
        if self.roll_cooldown > 0:
            self.roll_cooldown = max(0.0, self.roll_cooldown - dt)

        if self.is_cloaked:
            self.cloak_timer -= dt
            if self.cloak_timer <= 0:
                self.is_cloaked = False
        if self.cloak_cooldown > 0:
            self.cloak_cooldown = max(0.0, self.cloak_cooldown - dt)

        # Update Wingmen
        return self.update_wingmen(dt, targets_group=targets_group)

    def update_wingmen(self, dt: float, targets_group=None) -> list[Bullet]:
        """Updates autonomous escort wingmen and returns fired supportive projectiles."""
        wingman_bullets = []
        for wm in self.wingmen:
            wm_b = wm.update(dt, self.pos, targets_group=targets_group)
            wingman_bullets.extend(wm_b)
        return wingman_bullets


    def draw_wingmen(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        for wm in self.wingmen:
            wm.draw(canvas, camera_offset)

    def draw(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        """Renders player combat drone using dedicated PlayerRenderer."""
        self.renderer.draw_player(canvas, self, camera_offset)

    def _render_drone_sprite(self):
        """Pre-renders base sprite for collision or group fallbacks."""
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        self.image = sm.get_player_sprite(state="idle", skin_idx=self.skin_theme, target_size=(68, 58))
