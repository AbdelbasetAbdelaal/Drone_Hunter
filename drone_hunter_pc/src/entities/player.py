"""
================================================================================
                    DRONE HUNTER 2D - PLAYER COMBAT DRONE
================================================================================
Player combat drone entity featuring 2D kinematic flight physics, multi-weapon
arsenal management, active tactical abilities (Overdrive, Cloak, EMP, Roll),
unified shield hit absorption, and dynamic skin themes.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_CRIMSON, COLOR_MAGENTA, COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK,
    COLOR_SLOWMO, COLOR_BEAM, COLOR_MISSILE, COLOR_TESLA, COLOR_CLUSTER, COLOR_WHITE
)
from src.data.game_data import (
    HORIZONTAL_SPEED, VERTICAL_SPEED, ACCELERATION, FRICTION,
    PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY, ENERGY_REGEN_RATE, BOOST_DRAIN_RATE,
    EMP_COOLDOWN_MAX, ROLL_COOLDOWN, ROLL_DURATION, ROLL_SPEED_BOOST,
    CLOAK_DURATION, CLOAK_COOLDOWN_MAX, OVERDRIVE_DURATION, OVERDRIVE_COOLDOWN_MAX,
    WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER,
    WEAPON_DEFS, DRONE_SKINS
)
from src.entities.bullet import (
    Bullet, HomingMissile, PlasmaLaserBeam, TeslaArcBeam, ClusterTorpedo
)

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
            bullets.append(Bullet((self.pos.x, self.pos.y), (tx, ty), speed=850.0, damage=16, color=COLOR_CYAN))

        return bullets

    def draw(self, canvas: pygame.Surface):
        px, py = int(self.pos.x), int(self.pos.y)
        pygame.draw.circle(canvas, (15, 23, 42), (px, py), 9)
        pygame.draw.circle(canvas, COLOR_CYAN, (px, py), 9, 2)
        pygame.draw.circle(canvas, COLOR_WHITE, (px, py), 4)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[float, float] = (200, 360)):
        super().__init__()
        
        # Position & Kinematics
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.facing_angle_deg = 0.0
        self.tilt_y = 0.0
        
        # Hull & Energy
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.energy = PLAYER_MAX_ENERGY
        self.max_energy = PLAYER_MAX_ENERGY
        self.alive = True

        # Shield Hit System (Unified authoritative integer hits)
        self.shield_hits = 0

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

        # EMP Jammed Mechanic (Fixes Bug 4)
        self.emp_jammed_timer = 0.0

        # Combat & Upgrades
        self.overclock_timer = 0.0
        self.shoot_timer = 0.0
        self.invulnerable_timer = 0.0
        self.agility_mult = 1.0
        self.cooldown_mult = 1.0

        # Weaponry
        self.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER]
        self.current_weapon_idx = 0
        self.active_weapon = WEAPON_PULSE

        # Wingmen Escort Squad
        self.wingmen: list[WingmanDrone] = []

        # Aesthetics
        self.skin_theme = 0
        self.base_image = pygame.Surface((64, 48), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.radius = 24
        
        self._render_drone_sprite()

    # --- Shield Property Aliases for Backwards Compatibility ---
    @property
    def shield_charge(self) -> int:
        return self.shield_hits * 50

    @shield_charge.setter
    def shield_charge(self, value: int):
        self.shield_hits = max(0, int(value // 50) if value > 0 else 0)

    @property
    def is_invulnerable(self) -> bool:
        return self.is_rolling or self.invulnerable_timer > 0.0 or self.overdrive_timer > 0.0

    @property
    def is_jammed(self) -> bool:
        return self.emp_jammed_timer > 0.0

    @property
    def speed(self) -> float:
        boost = 1.40 if self.overdrive_timer > 0.0 else 1.0
        return HORIZONTAL_SPEED * self.agility_mult * boost

    def activate_shield(self, hits: int = 3):
        """Activates defensive energy shield for given hit charges."""
        self.shield_hits = max(self.shield_hits, hits)

    def trigger_emp_jammed(self, duration: float = 3.0):
        """Jams player systems upon being hit by EMP Boss attack."""
        if not self.is_invulnerable:
            self.emp_jammed_timer = max(self.emp_jammed_timer, duration)

    def trigger_overdrive(self) -> bool:
        """Activates Overdrive Ultimate (hyper-fire mode, speed boost, invulnerability)."""
        if self.is_jammed:
            return False
        if self.overdrive_cooldown <= 0.0 and self.overdrive_timer <= 0.0:
            self.overdrive_timer = OVERDRIVE_DURATION
            self.overdrive_cooldown = OVERDRIVE_COOLDOWN_MAX
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
            self.velocity.x += dir_x * self.speed * ROLL_SPEED_BOOST
            return True
        return False

    def trigger_cloak(self) -> bool:
        """Activates tactical stealth cloak."""
        if self.is_jammed:
            return False
        if self.has_cloak_upgrade and self.cloak_cooldown <= 0.0 and not self.is_cloaked:
            self.is_cloaked = True
            self.cloak_timer = CLOAK_DURATION
            self.cloak_cooldown = CLOAK_COOLDOWN_MAX
            return True
        return False

    def trigger_emp(self) -> bool:
        """Charges and fires EMP blast."""
        if self.is_jammed:
            return False
        if self.emp_cooldown <= 0.0:
            self.emp_cooldown = self.emp_cooldown_max
            return True
        return False

    def trigger_overclock(self, duration: float = 6.0):
        self.overclock_timer = duration

    def cycle_weapon(self) -> str:
        if len(self.available_weapons) > 0:
            self.current_weapon_idx = (self.current_weapon_idx + 1) % len(self.available_weapons)
            self.active_weapon = self.available_weapons[self.current_weapon_idx]
        return self.active_weapon

    def select_weapon(self, idx: int) -> str:
        if 0 <= idx < len(self.available_weapons):
            self.current_weapon_idx = idx
            self.active_weapon = self.available_weapons[idx]
        return self.active_weapon

    def cycle_skin(self) -> int:
        self.skin_theme = (self.skin_theme + 1) % len(DRONE_SKINS)
        self._render_drone_sprite()
        return self.skin_theme

    def spawn_wingman(self):
        if len(self.wingmen) < 4:
            count = len(self.wingmen)
            offsets = [(-35, -35), (-35, 35), (-60, -55), (-60, 55)]
            ox, oy = offsets[count]
            self.wingmen.append(WingmanDrone(ox, oy))

    def apply_shop_upgrades(self, upgrade_levels: dict[str, int]):
        bat_lvl = upgrade_levels.get("battery", 0)
        spd_lvl = upgrade_levels.get("speed", 0)
        fr_lvl = upgrade_levels.get("fire_rate", 0)
        emp_lvl = upgrade_levels.get("emp_recharge", 0)
        wm_lvl = upgrade_levels.get("wingman", 0)
        cloak_lvl = upgrade_levels.get("cloak", 0)
        missile_lvl = upgrade_levels.get("missiles", 0)
        beam_lvl = upgrade_levels.get("beam", 0)
        tesla_lvl = upgrade_levels.get("tesla", 0)
        cluster_lvl = upgrade_levels.get("cluster", 0)

        self.max_health = 100 + (bat_lvl * 20)
        self.health = self.max_health
        self.agility_mult = 1.0 + (spd_lvl * 0.15)
        self.cooldown_mult = max(0.35, 1.0 - (fr_lvl * 0.12))
        self.emp_cooldown_max = max(6.0, EMP_COOLDOWN_MAX - (emp_lvl * 2.5))
        self.has_cloak_upgrade = (cloak_lvl > 0)

        self.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER]
        if missile_lvl > 0: self.available_weapons.append(WEAPON_MISSILE)
        if beam_lvl > 0: self.available_weapons.append(WEAPON_BEAM)
        if tesla_lvl > 0: self.available_weapons.append(WEAPON_TESLA)
        if cluster_lvl > 0: self.available_weapons.append(WEAPON_CLUSTER)

        self.wingmen.clear()
        for _ in range(min(4, wm_lvl)):
            self.spawn_wingman()

        self._render_drone_sprite()

    def take_damage(self, amount: float) -> bool:
        """Applies damage considering shields, rolling i-frames, and cloak. Returns True if destroyed."""
        if self.is_invulnerable:
            return False

        if self.shield_hits > 0:
            self.shield_hits -= 1
            return False

        self.energy = max(0.0, self.energy - float(amount))
        if self.energy <= 0.0:
            self.alive = False
            return True
        return False

    def can_shoot(self) -> bool:
        if self.is_jammed:
            return False
        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        cost = w_def.get("energy_cost", 2.0)
        return self.shoot_timer <= 0.0 and (self.energy >= cost or self.overdrive_timer > 0.0)

    def shoot(self, target_pos: tuple[float, float], level: int = 1, targets_group=None) -> list[pygame.sprite.Sprite]:
        """Fires projectiles based on active weapon definition."""
        if not self.can_shoot():
            return []

        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        base_cd = w_def.get("cooldown", 0.18)
        cost = w_def.get("energy_cost", 2.5)

        cd_scale = 0.50 if self.overdrive_timer > 0.0 else (0.65 if self.overclock_timer > 0.0 else 1.0)
        self.shoot_timer = base_cd * self.cooldown_mult * cd_scale

        if self.overdrive_timer <= 0.0:
            self.energy = max(0.0, self.energy - cost)

        bullets = []
        cx, cy = self.rect.center

        if self.active_weapon == WEAPON_PULSE:
            bullets.append(Bullet((cx, cy - 8), target_pos, speed=920.0, damage=28, color=COLOR_CYAN))
            bullets.append(Bullet((cx, cy + 8), target_pos, speed=920.0, damage=28, color=COLOR_CYAN))
            if self.overdrive_timer > 0.0:
                bullets.append(Bullet((cx, cy), target_pos, angle_offset_deg=-12.0, speed=980.0, damage=32, color=COLOR_GOLD))
                bullets.append(Bullet((cx, cy), target_pos, angle_offset_deg=12.0, speed=980.0, damage=32, color=COLOR_GOLD))

        elif self.active_weapon == WEAPON_SCATTER:
            spread_angles = [-16.0, -8.0, 0.0, 8.0, 16.0] if self.overdrive_timer > 0.0 else [-12.0, -4.0, 4.0, 12.0]
            for ang in spread_angles:
                bullets.append(Bullet((cx, cy), target_pos, angle_offset_deg=ang, speed=860.0, damage=18, color=COLOR_GOLD))

        elif self.active_weapon == WEAPON_MISSILE:
            bullets.append(HomingMissile((cx, cy - 12), target_pos, damage=65))
            bullets.append(HomingMissile((cx, cy + 12), target_pos, damage=65))

        elif self.active_weapon == WEAPON_BEAM:
            bullets.append(PlasmaLaserBeam((cx, cy), target_pos, damage=14))

        elif self.active_weapon == WEAPON_TESLA:
            bullets.append(TeslaArcBeam((cx, cy), target_pos, damage=42))
            if self.overdrive_timer > 0.0:
                bullets.append(TeslaArcBeam((cx, cy), target_pos, damage=42))

        elif self.active_weapon == WEAPON_CLUSTER:
            bullets.append(ClusterTorpedo((cx, cy), target_pos, damage=85))

        return bullets

    def handle_input(self, keys, dt: float):
        """Processes 2D flight control movement."""
        move_x = 0.0
        move_y = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]: move_y -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_y += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += 1.0

        target_vel_x = move_x * self.speed
        target_vel_y = move_y * (VERTICAL_SPEED * self.agility_mult)

        # Acceleration and friction
        self.velocity.x += (target_vel_x - self.velocity.x) * min(1.0, FRICTION * dt)
        self.velocity.y += (target_vel_y - self.velocity.y) * min(1.0, FRICTION * dt)

        # Tilt banking
        target_tilt = -18.0 if move_y < 0 else (18.0 if move_y > 0 else 0.0)
        self.tilt_y += (target_tilt - self.tilt_y) * 10.0 * dt

    def update(self, dt: float, targets_group=None) -> list[pygame.sprite.Sprite]:
        # Position Update & Clamping
        self.pos += self.velocity * dt
        self.pos.x = max(35.0, min(SCREEN_WIDTH - 35.0, self.pos.x))
        self.pos.y = max(35.0, min(SCREEN_HEIGHT - 35.0, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Energy Regeneration
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + ENERGY_REGEN_RATE * dt)

        # Timers
        if self.shoot_timer > 0: self.shoot_timer -= dt
        if self.invulnerable_timer > 0: self.invulnerable_timer -= dt
        if self.overclock_timer > 0: self.overclock_timer -= dt
        if self.emp_jammed_timer > 0: self.emp_jammed_timer = max(0.0, self.emp_jammed_timer - dt)
        if self.emp_cooldown > 0: self.emp_cooldown = max(0.0, self.emp_cooldown - dt)

        # Overdrive Timer
        if self.overdrive_timer > 0:
            self.overdrive_timer -= dt
            if self.overdrive_timer <= 0:
                self.overdrive_timer = 0.0

        if self.overdrive_cooldown > 0:
            self.overdrive_cooldown = max(0.0, self.overdrive_cooldown - dt)

        # Roll Timer
        if self.is_rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.is_rolling = False
        if self.roll_cooldown > 0:
            self.roll_cooldown = max(0.0, self.roll_cooldown - dt)

        # Cloak Timer
        if self.is_cloaked:
            self.cloak_timer -= dt
            if self.cloak_timer <= 0:
                self.is_cloaked = False
        if self.cloak_cooldown > 0:
            self.cloak_cooldown = max(0.0, self.cloak_cooldown - dt)

        # Update Wingmen
        wingman_bullets = []
        for wm in self.wingmen:
            wm_b = wm.update(dt, self.pos, targets_group=targets_group)
            wingman_bullets.extend(wm_b)

        return wingman_bullets

    def draw_wingmen(self, canvas: pygame.Surface):
        for wm in self.wingmen:
            wm.draw(canvas)

    def _render_drone_sprite(self):
        skin = DRONE_SKINS[self.skin_theme]
        body_col = skin["body_color"]
        prim_col = skin["primary_color"]
        glow_col = skin["glow_color"]

        w, h = 64, 48
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Quadcopter Arm Struts
        pygame.draw.line(surf, (45, 55, 72), (12, 10), (52, 38), 4)
        pygame.draw.line(surf, (45, 55, 72), (12, 38), (52, 10), 4)

        # Rotors
        for rx, ry in [(12, 10), (52, 10), (12, 38), (52, 38)]:
            pygame.draw.circle(surf, glow_col, (rx, ry), 7, 2)
            pygame.draw.circle(surf, COLOR_WHITE, (rx, ry), 3)

        # Central Chassis & Cockpit Dome
        chassis_points = [(18, 24), (28, 14), (46, 14), (56, 24), (46, 34), (28, 34)]
        pygame.draw.polygon(surf, body_col, chassis_points)
        pygame.draw.polygon(surf, prim_col, chassis_points, 2)

        # Glowing Neon Canopy
        pygame.draw.ellipse(surf, glow_col, (30, 20, 16, 8))
        pygame.draw.ellipse(surf, COLOR_WHITE, (34, 22, 8, 4))

        self.image = surf
