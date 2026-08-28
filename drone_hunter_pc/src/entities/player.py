"""
================================================================================
                    DRONE HUNTER 2D - PLAYER COMBAT DRONE
================================================================================
Player combat drone entity acting as the central orchestrator and public facade.
Decomposes flight kinematics, tactical abilities, defense/health, weapon systems,
and escort wingmen into dedicated, single-responsibility components.
"""

import math
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
    WEAPON_DEFS, WEAPON_UPGRADES, DRONE_CLASSES, DRONE_CLASS_STRIKER,
    get_drone_class_by_id
)
from src.entities.bullet import (
    Bullet, HomingMissile, ContinuousBeam, TeslaArcBeam, ClusterTorpedo,
    HeavyPlasmaOrb, RailgunSlug, BarrageMissile, EMPPulse
)
from src.entities.wingman import WingmanDrone, WingmanManager
from src.entities.player_movement import MovementController
from src.entities.player_abilities import AbilityController
from src.entities.player_defense import PlayerDefense
from src.entities.player_weapons import WeaponController
from src.rendering.player_renderer import PlayerRenderer
from src.rendering.sprite_manager import get_sprite_manager


class Player(pygame.sprite.Sprite):
    """Orchestrates player drone systems via focused sub-components."""

    def __init__(self, pos: tuple[float, float] = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)):
        super().__init__()

        # Specialized Sub-Components
        self.movement = MovementController(pos)
        self.abilities = AbilityController()
        self.defense = PlayerDefense()
        self.weapons = WeaponController()
        self.wingman_manager = WingmanManager()
        self.renderer = PlayerRenderer()

        # Global Upgrades & Modifiers
        self.agility_mult = 1.0
        self.drone_class_id = DRONE_CLASS_STRIKER

        # Sprite Visual & Collision Rect
        self.base_image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(round(pos[0])), int(round(pos[1]))))
        self.radius = 28

        # Apply initial drone class profile
        self.set_drone_class(DRONE_CLASS_STRIKER)

    # -------------------------------------------------------------------------
    # Movement & Kinematics Properties
    # -------------------------------------------------------------------------
    @property
    def pos(self) -> pygame.Vector2:
        return self.movement.pos

    @pos.setter
    def pos(self, val: pygame.Vector2):
        self.movement.pos = pygame.Vector2(val)
        self.rect.center = (int(round(self.movement.pos.x)), int(round(self.movement.pos.y)))

    @property
    def velocity(self) -> pygame.Vector2:
        return self.movement.velocity

    @velocity.setter
    def velocity(self, val: pygame.Vector2):
        self.movement.velocity = pygame.Vector2(val)

    @property
    def acceleration(self) -> float:
        return self.movement.acceleration

    @acceleration.setter
    def acceleration(self, val: float):
        self.movement.acceleration = float(val)

    @property
    def drag(self) -> float:
        return self.movement.drag

    @drag.setter
    def drag(self, val: float):
        self.movement.drag = float(val)

    @property
    def max_speed(self) -> float:
        return self.movement.max_speed

    @max_speed.setter
    def max_speed(self, val: float):
        self.movement.max_speed = float(val)

    @property
    def is_accelerating(self) -> bool:
        return self.movement.is_accelerating

    @is_accelerating.setter
    def is_accelerating(self, val: bool):
        self.movement.is_accelerating = bool(val)

    @property
    def aim_angle(self) -> float:
        return self.movement.aim_angle

    @aim_angle.setter
    def aim_angle(self, val: float):
        self.movement.aim_angle = float(val)

    @property
    def facing_angle_deg(self) -> float:
        return self.movement.facing_angle_deg

    @facing_angle_deg.setter
    def facing_angle_deg(self, val: float):
        self.movement.facing_angle_deg = float(val)

    @property
    def tilt_y(self) -> float:
        return self.movement.tilt_y

    @tilt_y.setter
    def tilt_y(self, val: float):
        self.movement.tilt_y = float(val)

    @property
    def arena_width(self) -> float:
        return self.movement.arena_width

    @arena_width.setter
    def arena_width(self, val: float):
        self.movement.arena_width = float(val)

    @property
    def arena_height(self) -> float:
        return self.movement.arena_height

    @arena_height.setter
    def arena_height(self, val: float):
        self.movement.arena_height = float(val)

    @property
    def speed(self) -> float:
        boost = 1.40 if self.overdrive_timer > 0.0 else 1.0
        return self.max_speed * self.agility_mult * boost

    # -------------------------------------------------------------------------
    # Defense & Health Properties
    # -------------------------------------------------------------------------
    @property
    def health(self) -> float:
        return self.defense.health

    @health.setter
    def health(self, val: float):
        self.defense.health = float(val)

    @property
    def max_health(self) -> float:
        return self.defense.max_health

    @max_health.setter
    def max_health(self, val: float):
        self.defense.max_health = float(val)

    @property
    def _upgrade_bonus_health(self) -> float:
        return self.defense._upgrade_bonus_health

    @_upgrade_bonus_health.setter
    def _upgrade_bonus_health(self, val: float):
        self.defense._upgrade_bonus_health = float(val)

    @property
    def energy(self) -> float:
        return self.defense.energy

    @energy.setter
    def energy(self, val: float):
        self.defense.energy = float(val)

    @property
    def max_energy(self) -> float:
        return self.defense.max_energy

    @max_energy.setter
    def max_energy(self, val: float):
        self.defense.max_energy = float(val)

    @property
    def armor(self) -> int:
        return self.defense.armor

    @armor.setter
    def armor(self, val: int):
        self.defense.armor = int(val)

    @property
    def weapon_effectiveness(self) -> float:
        return self.defense.weapon_effectiveness

    @weapon_effectiveness.setter
    def weapon_effectiveness(self, val: float):
        self.defense.weapon_effectiveness = float(val)

    @property
    def alive(self) -> bool:
        return self.defense.alive

    @alive.setter
    def alive(self, val: bool):
        self.defense.alive = bool(val)

    @property
    def is_destroyed(self) -> bool:
        return self.defense.is_destroyed

    @is_destroyed.setter
    def is_destroyed(self, val: bool):
        self.defense.is_destroyed = bool(val)

    @property
    def destruction_timer(self) -> float:
        return self.defense.destruction_timer

    @destruction_timer.setter
    def destruction_timer(self, val: float):
        self.defense.destruction_timer = float(val)

    @property
    def shield_hits(self) -> int:
        return self.defense.shield_hits

    @shield_hits.setter
    def shield_hits(self, val: int):
        self.defense.shield_hits = int(val)

    @property
    def shield_charge(self) -> int:
        return self.defense.shield_charge

    @shield_charge.setter
    def shield_charge(self, val: int):
        self.defense.shield_charge = int(val)

    @property
    def damage_grace_timer(self) -> float:
        return self.defense.damage_grace_timer

    @damage_grace_timer.setter
    def damage_grace_timer(self, val: float):
        self.defense.damage_grace_timer = float(val)

    @property
    def damage_grace_duration(self) -> float:
        return self.defense.damage_grace_duration

    @damage_grace_duration.setter
    def damage_grace_duration(self, val: float):
        self.defense.damage_grace_duration = float(val)

    @property
    def damage_flash_timer(self) -> float:
        return self.defense.damage_flash_timer

    @damage_flash_timer.setter
    def damage_flash_timer(self, val: float):
        self.defense.damage_flash_timer = float(val)

    @property
    def invulnerable_timer(self) -> float:
        return self.defense.invulnerable_timer

    @invulnerable_timer.setter
    def invulnerable_timer(self, val: float):
        self.defense.invulnerable_timer = float(val)

    @property
    def is_invulnerable(self) -> bool:
        return self.is_rolling or self.invulnerable_timer > 0.0 or self.overdrive_timer > 0.0 or self.damage_grace_timer > 0.0

    # -------------------------------------------------------------------------
    # Tactical Abilities Properties
    # -------------------------------------------------------------------------
    @property
    def emp_cooldown(self) -> float:
        return self.abilities.emp_cooldown

    @emp_cooldown.setter
    def emp_cooldown(self, val: float):
        self.abilities.emp_cooldown = float(val)

    @property
    def emp_cooldown_max(self) -> float:
        return self.abilities.emp_cooldown_max

    @emp_cooldown_max.setter
    def emp_cooldown_max(self, val: float):
        self.abilities.emp_cooldown_max = float(val)

    @property
    def roll_timer(self) -> float:
        return self.abilities.roll_timer

    @roll_timer.setter
    def roll_timer(self, val: float):
        self.abilities.roll_timer = float(val)

    @property
    def roll_cooldown(self) -> float:
        return self.abilities.roll_cooldown

    @roll_cooldown.setter
    def roll_cooldown(self, val: float):
        self.abilities.roll_cooldown = float(val)

    @property
    def is_rolling(self) -> bool:
        return self.abilities.is_rolling

    @is_rolling.setter
    def is_rolling(self, val: bool):
        self.abilities.is_rolling = bool(val)

    @property
    def cloak_timer(self) -> float:
        return self.abilities.cloak_timer

    @cloak_timer.setter
    def cloak_timer(self, val: float):
        self.abilities.cloak_timer = float(val)

    @property
    def cloak_cooldown(self) -> float:
        return self.abilities.cloak_cooldown

    @cloak_cooldown.setter
    def cloak_cooldown(self, val: float):
        self.abilities.cloak_cooldown = float(val)

    @property
    def is_cloaked(self) -> bool:
        return self.abilities.is_cloaked

    @is_cloaked.setter
    def is_cloaked(self, val: bool):
        self.abilities.is_cloaked = bool(val)

    @property
    def has_cloak_upgrade(self) -> bool:
        return self.abilities.has_cloak_upgrade

    @has_cloak_upgrade.setter
    def has_cloak_upgrade(self, val: bool):
        self.abilities.has_cloak_upgrade = bool(val)

    @property
    def overdrive_timer(self) -> float:
        return self.abilities.overdrive_timer

    @overdrive_timer.setter
    def overdrive_timer(self, val: float):
        self.abilities.overdrive_timer = float(val)

    @property
    def overdrive_cooldown(self) -> float:
        return self.abilities.overdrive_cooldown

    @overdrive_cooldown.setter
    def overdrive_cooldown(self, val: float):
        self.abilities.overdrive_cooldown = float(val)

    @property
    def overdrive_duration_max(self) -> float:
        return self.abilities.overdrive_duration_max

    @overdrive_duration_max.setter
    def overdrive_duration_max(self, val: float):
        self.abilities.overdrive_duration_max = float(val)

    @property
    def overdrive_cooldown_max(self) -> float:
        return self.abilities.overdrive_cooldown_max

    @overdrive_cooldown_max.setter
    def overdrive_cooldown_max(self, val: float):
        self.abilities.overdrive_cooldown_max = float(val)

    @property
    def emp_jammed_timer(self) -> float:
        return self.abilities.emp_jammed_timer

    @emp_jammed_timer.setter
    def emp_jammed_timer(self, val: float):
        self.abilities.emp_jammed_timer = float(val)

    @property
    def is_jammed(self) -> bool:
        return self.abilities.is_jammed

    @property
    def overclock_timer(self) -> float:
        return self.abilities.overclock_timer

    @overclock_timer.setter
    def overclock_timer(self, val: float):
        self.abilities.overclock_timer = float(val)

    # -------------------------------------------------------------------------
    # Weapons Properties
    # -------------------------------------------------------------------------
    @property
    def available_weapons(self) -> list[str]:
        return self.weapons.available_weapons

    @available_weapons.setter
    def available_weapons(self, val: list[str]):
        self.weapons.available_weapons = list(val)

    @property
    def current_weapon_idx(self) -> int:
        return self.weapons.current_weapon_idx

    @current_weapon_idx.setter
    def current_weapon_idx(self, val: int):
        self.weapons.current_weapon_idx = int(val)

    @property
    def active_weapon(self) -> str:
        return self.weapons.active_weapon

    @active_weapon.setter
    def active_weapon(self, val: str):
        self.weapons.active_weapon = str(val)

    @property
    def weapon_cooldowns(self) -> dict[str, float]:
        return self.weapons.weapon_cooldowns

    @weapon_cooldowns.setter
    def weapon_cooldowns(self, val: dict[str, float]):
        self.weapons.weapon_cooldowns = dict(val)

    @property
    def weapon_upgrade_levels(self) -> dict[str, int]:
        return self.weapons.weapon_upgrade_levels

    @weapon_upgrade_levels.setter
    def weapon_upgrade_levels(self, val: dict[str, int]):
        self.weapons.weapon_upgrade_levels = dict(val)

    @property
    def cooldown_mult(self) -> float:
        return self.weapons.cooldown_mult

    @cooldown_mult.setter
    def cooldown_mult(self, val: float):
        self.weapons.cooldown_mult = float(val)

    @property
    def muzzle_flash_timer(self) -> float:
        return self.weapons.muzzle_flash_timer

    @muzzle_flash_timer.setter
    def muzzle_flash_timer(self, val: float):
        self.weapons.muzzle_flash_timer = float(val)

    @property
    def active_beam(self):
        return self.weapons.active_beam

    @active_beam.setter
    def active_beam(self, val):
        self.weapons.active_beam = val

    @property
    def _fired_this_frame(self) -> bool:
        return self.weapons._fired_this_frame

    @_fired_this_frame.setter
    def _fired_this_frame(self, val: bool):
        self.weapons._fired_this_frame = bool(val)

    @property
    def _rapid_side(self) -> int:
        return self.weapons._rapid_side

    @_rapid_side.setter
    def _rapid_side(self, val: int):
        self.weapons._rapid_side = int(val)

    @property
    def _missile_side(self) -> int:
        return self.weapons._missile_side

    @_missile_side.setter
    def _missile_side(self, val: int):
        self.weapons._missile_side = int(val)

    # -------------------------------------------------------------------------
    # Wingman Properties
    # -------------------------------------------------------------------------
    @property
    def wingmen(self) -> list[WingmanDrone]:
        return self.wingman_manager.wingmen

    @wingmen.setter
    def wingmen(self, val: list[WingmanDrone]):
        self.wingman_manager.wingmen = list(val)

    # -------------------------------------------------------------------------
    # Drone Class Configuration
    # -------------------------------------------------------------------------
    def set_drone_class(self, class_id: str):
        """Configures player statistics, weapon loadout, and weapon mounts for the selected drone class."""
        self.drone_class_id = class_id
        c_data = get_drone_class_by_id(self.drone_class_id)

        self.movement.configure_drone_class(c_data)
        self.defense.configure_drone_class(c_data)
        self.weapons.configure_drone_class(c_data)
        self._render_drone_sprite()

    def apply_drone_class(self, class_idx: int):
        """Legacy alias mapping int class_idx to set_drone_class for backward compatibility."""
        mapping = ["striker", "interceptor", "assault", "arc", "command"]
        idx = max(0, min(len(mapping) - 1, class_idx))
        self.set_drone_class(mapping[idx])

    @property
    def drone_class(self) -> str:
        return self.drone_class_id

    @drone_class.setter
    def drone_class(self, val: str):
        self.set_drone_class(val)

    def cycle_drone_class(self, step: int = 1) -> str:
        """Cycles through available drone combat classes and updates chassis aesthetics."""
        class_ids = list(DRONE_CLASSES.keys())
        try:
            curr_idx = class_ids.index(self.drone_class_id)
        except ValueError:
            curr_idx = 0
        next_idx = (curr_idx + step) % len(class_ids)
        next_id = class_ids[next_idx]
        self.set_drone_class(next_id)
        return self.drone_class_id

    def get_mount_world_pos(self, mount_name: str = "primary") -> tuple[float, float]:
        """Calculates rotated world coordinates for a local-space weapon mount point."""
        return self.movement.get_mount_world_pos(self.drone_class_id, mount_name)

    # -------------------------------------------------------------------------
    # Action Delegations
    # -------------------------------------------------------------------------
    def activate_shield(self, hits: int = 3):
        self.defense.activate_shield(hits)

    def trigger_emp(self) -> bool:
        return self.abilities.trigger_emp()

    def trigger_emp_jammed(self, duration: float = 3.0):
        self.abilities.trigger_emp_jammed(duration, is_invulnerable=self.is_invulnerable)

    def trigger_overdrive(self) -> bool:
        def on_activate():
            self.defense.activate_shield(3)
            self.defense.energy = self.defense.max_energy
        return self.abilities.trigger_overdrive(on_activate=on_activate)

    def trigger_roll(self, dir_x: float = 1.0) -> bool:
        def on_impulse(impulse_x: float):
            self.movement.velocity.x += impulse_x
        return self.abilities.trigger_roll(dir_x=dir_x, on_impulse=on_impulse)

    def trigger_cloak(self) -> bool:
        return self.abilities.trigger_cloak()

    def trigger_overclock(self, duration: float = 6.0):
        self.abilities.trigger_overclock(duration)

    def cycle_weapon(self, direction: int = 1):
        self.weapons.cycle_weapon(direction)

    def select_weapon(self, index: int):
        self.weapons.select_weapon(index)

    def set_weapon(self, weapon_name: str):
        self.weapons.set_weapon(weapon_name)

    def spawn_wingman(self):
        self.wingman_manager.spawn_wingman()

    def apply_shop_upgrades(self, upgrades: dict):
        """Applies persistent hangar upgrade statistics."""
        bat_lvl = upgrades.get("battery", 0)
        self.defense._upgrade_bonus_health = bat_lvl * 25.0

        spd_lvl = upgrades.get("speed", 0)
        self.agility_mult = 1.0 + (spd_lvl * 0.12)

        fr_lvl = upgrades.get("fire_rate", 0)
        self.weapons.cooldown_mult = max(0.50, 1.0 - (fr_lvl * 0.08))

        emp_lvl = upgrades.get("emp_recharge", 0)
        self.abilities.emp_cooldown_max = max(6.0, EMP_COOLDOWN_MAX - (emp_lvl * 1.5))

        wm_lvl = upgrades.get("wingman", 0)
        self.wingman_manager.set_formation(wm_lvl)

        clk_lvl = upgrades.get("cloak", 0)
        self.abilities.has_cloak_upgrade = (clk_lvl > 0)

        od_lvl = upgrades.get("overdrive", 0)
        self.abilities.overdrive_duration_max = OVERDRIVE_DURATION + (od_lvl * 1.5)
        self.abilities.overdrive_cooldown_max = max(12.0, OVERDRIVE_COOLDOWN_MAX - (od_lvl * 3.0))

        # Re-apply current drone class weapon loadout and upgrade bonuses
        self.set_drone_class(self.drone_class_id)

    def apply_weapon_upgrades(self, weapon_upgrades: dict):
        self.weapons.apply_weapon_upgrades(weapon_upgrades)

    def take_damage(self, amount: float, source: str = "bullet", ignore_grace: bool = False) -> bool:
        return self.defense.take_damage(
            amount=amount,
            is_invulnerable=self.is_invulnerable,
            source=source,
            ignore_grace=ignore_grace
        )

    def can_shoot(self) -> bool:
        return self.weapons.can_shoot(
            alive=self.defense.alive,
            is_destroyed=self.defense.is_destroyed,
            is_jammed=self.abilities.is_jammed,
            is_rolling=self.abilities.is_rolling,
            energy=self.defense.energy,
            overdrive_active=(self.abilities.overdrive_timer > 0.0)
        )

    def shoot(self, target_pos: tuple[float, float], level: int = 1, targets_group=None, particle_manager=None) -> list[pygame.sprite.Sprite]:
        if not self.can_shoot():
            return []

        # Aim angle updated on shoot
        self.movement.aim_angle = math.atan2(target_pos[1] - self.movement.pos.y, target_pos[0] - self.movement.pos.x)

        def on_recoil(rx: float, ry: float):
            self.movement.velocity.x += rx
            self.movement.velocity.y += ry

        def on_energy_deduct(cost: float):
            self.defense.energy = max(0.0, self.defense.energy - cost)

        return self.weapons.shoot(
            player_pos=self.movement.pos,
            aim_angle=self.movement.aim_angle,
            target_pos=target_pos,
            energy=self.defense.energy,
            overdrive_active=(self.abilities.overdrive_timer > 0.0),
            overclock_active=(self.abilities.overclock_timer > 0.0),
            weapon_effectiveness=self.defense.weapon_effectiveness,
            get_mount_pos_fn=self.get_mount_world_pos,
            on_recoil=on_recoil,
            on_energy_deduct=on_energy_deduct,
            targets_group=targets_group,
            particle_manager=particle_manager
        )

    def handle_input(self, keys, dt: float, mouse_pos: tuple[float, float] = None, input_state: dict = None):
        self.movement.handle_input(
            keys=keys,
            dt=dt,
            mouse_pos=mouse_pos,
            input_state=input_state,
            agility_mult=self.agility_mult,
            current_max_speed=self.speed
        )

    def update(self, dt: float, targets_group=None) -> list[pygame.sprite.Sprite]:
        """Coordinates component updates."""
        # 1. Weapons update (beam transform, cooldowns, muzzle flash)
        self.weapons.update(
            dt=dt,
            get_mount_pos_fn=self.get_mount_world_pos,
            aim_angle=self.movement.aim_angle
        )

        # 2. Movement update
        self.movement.update(dt)
        self.rect.center = (int(round(self.movement.pos.x)), int(round(self.movement.pos.y)))

        # 3. Defense update
        should_kill = self.defense.update(dt)
        if should_kill:
            self.kill()

        # 4. Abilities update
        self.abilities.update(dt)

        # 5. Escort Wingmen update
        return self.wingman_manager.update(dt, self.movement.pos, targets_group=targets_group)

    def update_wingmen(self, dt: float, targets_group=None) -> list[Bullet]:
        return self.wingman_manager.update(dt, self.movement.pos, targets_group=targets_group)

    def draw_wingmen(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        self.wingman_manager.draw(canvas, camera_offset)

    def draw(self, canvas: pygame.Surface, camera_offset: tuple[float, float] = (0, 0)):
        self.renderer.draw_player(canvas, self, camera_offset)

    def _render_drone_sprite(self):
        """Pre-renders base sprite for collision or group fallbacks."""
        sm = get_sprite_manager()
        class_idx_map = {
            "striker": 0, "01_striker": 0,
            "interceptor": 1, "phantom": 1, "02_phantom": 1,
            "assault": 2, "titan": 2, "03_titan": 2,
            "arc": 3, "specter": 3, "velocity": 3, "04_velocity": 3,
            "command": 4, "tempest": 4, "aegis_quad": 4, "05_aegis_quad": 4,
        }
        skin_idx = class_idx_map.get(getattr(self, "drone_class_id", "striker"), 0)
        self.image = sm.get_player_sprite(state="idle", skin_idx=skin_idx, target_size=(68, 58))
