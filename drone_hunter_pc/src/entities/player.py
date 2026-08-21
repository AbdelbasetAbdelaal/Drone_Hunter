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
    WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_DEFS, DRONE_SKINS
)
from src.entities.bullet import (
    Bullet, HomingMissile, PlasmaLaserBeam, TeslaArcBeam, ClusterTorpedo
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
            bullets.append(Bullet((self.pos.x, self.pos.y), (tx, ty), speed=850.0, damage=16, color=COLOR_CYAN))

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
        
        # Position & Kinematic Flight Physics
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 3200.0
        self.drag = 7.5
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
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.max_energy = PLAYER_MAX_ENERGY
        self.energy = PLAYER_MAX_ENERGY
        self.weapon_effectiveness = 1.0
        self.alive = True

        # Shield Hit System
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

        # Weaponry
        self.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE]
        self.current_weapon_idx = 0
        self.active_weapon = WEAPON_PULSE
        self.weapon_cooldowns = {w: 0.0 for w in self.available_weapons}

        # Wingmen Escort Squad
        self.wingmen: list[WingmanDrone] = []

        # Aesthetics
        self.skin_theme = 0
        self.base_image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(round(pos[0])), int(round(pos[1]))))
        self.radius = 28
        
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
        if self.has_cloak_upgrade and self.cloak_cooldown <= 0.0 and not self.is_cloaked:
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
        """Directly equips unlocked weapon by identifier."""
        if weapon_name in self.available_weapons:
            self.active_weapon = weapon_name
            self.current_weapon_idx = self.available_weapons.index(weapon_name)

    def spawn_wingman(self):
        """Spawns an escort wingman drone upon picking up a powerup (up to 2)."""
        if len(self.wingmen) == 0:
            self.wingmen.append(WingmanDrone(-42, -40))
        elif len(self.wingmen) == 1:
            self.wingmen.append(WingmanDrone(-42, 40))

    def trigger_overclock(self, duration: float = 6.0):
        """Triggers weapon overclock fire rate boost."""
        self.overclock_timer = max(self.overclock_timer, duration)

    def cycle_skin(self) -> int:
        """Cycles aesthetic drone chassis theme."""
        self.skin_theme = (self.skin_theme + 1) % len(DRONE_SKINS)
        self._render_drone_sprite()
        return self.skin_theme

    def set_skin(self, index: int):
        self.skin_theme = max(0, min(len(DRONE_SKINS) - 1, index))
        self._render_drone_sprite()

    def apply_shop_upgrades(self, upgrades: dict):
        """Applies persistent hangar upgrade statistics."""
        bat_lvl = upgrades.get("battery", 0)
        self.max_health = PLAYER_MAX_HEALTH + (bat_lvl * 25.0)
        self.health = self.max_health

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

        # Weapon unlocks (Phase 3 Development Mode: All 3 available by default)
        self.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE]
        if self.active_weapon not in self.available_weapons:
            self.active_weapon = WEAPON_PULSE
            self.current_weapon_idx = 0

        self._render_drone_sprite()

    def take_damage(self, amount: float, source: str = "bullet") -> bool:
        """Applies damage to shields and health hull. Returns True if destroyed."""
        if self.is_invulnerable:
            return False

        self.damage_flash_timer = 0.18

        if self.shield_hits > 0:
            self.shield_hits -= 1
            return False

        self.health = max(0.0, self.health - float(amount))
        if self.health <= 0.0:
            self.alive = False
            self.is_destroyed = True
            self.destruction_timer = 0.5
            return True
        return False

    def can_shoot(self) -> bool:
        if self.is_jammed:
            return False
        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        cost = w_def.get("energy_cost", 2.0)
        cooldown_ready = self.weapon_cooldowns.get(self.active_weapon, 0.0) <= 0.0
        return cooldown_ready and (self.energy >= cost or self.overdrive_timer > 0.0)

    def shoot(self, target_pos: tuple[float, float], level: int = 1, targets_group=None, particle_manager=None) -> list[pygame.sprite.Sprite]:
        """Fires projectiles toward world target position using authoritative balance values."""
        if not self.can_shoot():
            return []

        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        base_cd = w_def.get("cooldown", 0.18)
        cost = w_def.get("energy_cost", 0.0)
        dmg = int(w_def.get("damage", 12) * self.weapon_effectiveness)
        spd = float(w_def.get("speed", 650.0))
        col = w_def.get("color", COLOR_CYAN)
        proj_count = w_def.get("projectiles_per_shot", 1)
        spread_deg = w_def.get("spread_deg", 0.0)

        cd_scale = 0.50 if self.overdrive_timer > 0.0 else (0.65 if self.overclock_timer > 0.0 else 1.0)
        self.weapon_cooldowns[self.active_weapon] = base_cd * self.cooldown_mult * cd_scale

        if self.overdrive_timer <= 0.0:
            self.energy = max(0.0, self.energy - cost)

        # Update Aim Angle
        cx, cy = self.pos.x, self.pos.y
        self.aim_angle = math.atan2(target_pos[1] - cy, target_pos[0] - cx)
        self.muzzle_flash_timer = 0.08

        # Subtle Recoil Impulse
        recoil_kick = 26.0
        self.velocity.x -= math.cos(self.aim_angle) * recoil_kick
        self.velocity.y -= math.sin(self.aim_angle) * recoil_kick

        bullets = []
        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        
        # Muzzle Position (nose of the ship)
        m_x = cx + 24 * cos_a
        m_y = cy + 24 * sin_a

        sm = get_sprite_manager()

        if self.active_weapon == WEAPON_PULSE:
            sprite = sm.get_projectile_sprite('pulse', (40, 12))
            bullets.append(Bullet((m_x, m_y), target_pos, speed=spd, damage=dmg, color=col, image=sprite))
            if self.overdrive_timer > 0.0:
                od_dmg = int(dmg * 1.25)
                bullets.append(Bullet((m_x, m_y), target_pos, angle_offset_deg=-12.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite))
                bullets.append(Bullet((m_x, m_y), target_pos, angle_offset_deg=12.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite))

        elif self.active_weapon == WEAPON_SCATTER:
            # Deterministic spread: -11, -5.5, 0, 5.5, 11 degrees
            start_ang = -spread_deg / 2
            step = spread_deg / max(1, proj_count - 1) if proj_count > 1 else 0
            sprite = sm.get_projectile_sprite('scatter', (40, 12))
            
            for i in range(proj_count):
                ang = start_ang + step * i
                bullets.append(Bullet((m_x, m_y), target_pos, angle_offset_deg=ang, speed=spd, damage=dmg, color=col, image=sprite))

        elif self.active_weapon == WEAPON_MISSILE:
            # Use normal bullet but with larger visual representation later, or HomingMissile if it exists
            # We'll use HomingMissile but give it the correct stats.
            sprite = sm.get_projectile_sprite('missile', (45, 16))
            bullets.append(HomingMissile((m_x, m_y), target_pos, damage=dmg, speed=spd, image=sprite))

        if particle_manager:
            particle_manager.spawn_muzzle_flash((m_x, m_y), self.aim_angle, self.active_weapon)

        return bullets

    def handle_input(self, keys, dt: float, mouse_pos: tuple[float, float] = None):
        """Processes 360-degree vector flight kinematics, lateral banking, and mouse aiming."""
        move_x = 0.0
        move_y = 0.0

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

        # Update Aim Direction from Mouse (World Coordinates)
        if mouse_pos:
            self.aim_angle = math.atan2(mouse_pos[1] - self.pos.y, mouse_pos[0] - self.pos.x)

        # Smooth Lateral Velocity Banking relative to Aim Angle
        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        lateral_speed = (-sin_a * self.velocity.x) + (cos_a * self.velocity.y)
        target_tilt = max(-26.0, min(26.0, (lateral_speed / max(1.0, current_max)) * 32.0))
        self.tilt_y += (target_tilt - self.tilt_y) * min(1.0, 12.0 * dt)

    def update(self, dt: float, targets_group=None) -> list[pygame.sprite.Sprite]:
        """Updates drone physics position, boundary clamping, timers, and energy regeneration."""
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
