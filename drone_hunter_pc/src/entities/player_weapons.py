"""
================================================================================
                DRONE HUNTER 2D - PLAYER WEAPON CONTROLLER
================================================================================
Manages player weapon loadout, weapon switching, cooldown tracking, energy costs,
and projectile generation from physical mount hardpoints.
"""

import math
from typing import Callable, Optional
import pygame

from src.data.settings import (
    COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD, COLOR_CRIMSON, COLOR_MAGENTA,
    COLOR_PURPLE, COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_SLOWMO, COLOR_BEAM,
    COLOR_MISSILE, COLOR_TESLA, COLOR_CLUSTER, COLOR_WHITE
)
from src.data.game_data import (
    WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, WEAPON_RAPID, WEAPON_PLASMA,
    WEAPON_RAIL, WEAPON_BARRAGE, WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP,
    WEAPON_DEFS, WEAPON_UPGRADES
)
from src.entities.bullet import (
    Bullet, HomingMissile, ContinuousBeam, TeslaArcBeam, ClusterTorpedo,
    HeavyPlasmaOrb, RailgunSlug, BarrageMissile, EMPPulse
)
from src.rendering.sprite_manager import get_sprite_manager


class WeaponController:
    """Encapsulates player weapon selection, cooldowns, upgrades, and projectile firing."""

    def __init__(self):
        self.available_weapons: list[str] = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE]
        self.current_weapon_idx: int = 0
        self.active_weapon: str = WEAPON_PULSE
        self.weapon_cooldowns: dict[str, float] = {w: 0.0 for w in WEAPON_DEFS}
        self.weapon_upgrade_levels: dict[str, int] = {}
        self.cooldown_mult: float = 1.0

        # Hardpoint Alternating Mount State
        self._rapid_side: int = 0
        self._missile_side: int = 0

        # Visual Flash & Continuous Beam State
        self.muzzle_flash_timer: float = 0.0
        self.active_beam = None
        self._fired_this_frame: bool = False

    def configure_drone_class(self, class_data: dict):
        """Applies weapon loadout for the selected drone class."""
        self.available_weapons = list(class_data.get("weapons", []))
        if self.active_weapon not in self.available_weapons and self.available_weapons:
            self.active_weapon = self.available_weapons[0]
            self.current_weapon_idx = 0
        for w in self.available_weapons:
            if w not in self.weapon_cooldowns:
                self.weapon_cooldowns[w] = 0.0

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

    def apply_weapon_upgrades(self, weapon_upgrades: dict):
        """Stores weapon-specific upgrade levels for per-weapon stat scaling."""
        self.weapon_upgrade_levels = {str(k): max(0, int(v)) for k, v in weapon_upgrades.items()}

    def can_shoot(self, alive: bool, is_destroyed: bool, is_jammed: bool, is_rolling: bool, energy: float, overdrive_active: bool) -> bool:
        """Checks whether the currently equipped weapon is off cooldown and ready to fire."""
        if not alive or is_destroyed or is_jammed or is_rolling:
            return False
        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        cost = w_def.get("energy_cost", 0.0)
        if energy < cost and not overdrive_active:
            return False
        cd = self.weapon_cooldowns.get(self.active_weapon, 0.0)
        return cd <= 0.0

    def shoot(
        self,
        player_pos: pygame.Vector2,
        aim_angle: float,
        target_pos: tuple[float, float],
        energy: float,
        overdrive_active: bool,
        overclock_active: bool,
        weapon_effectiveness: float,
        get_mount_pos_fn: Callable[[str], tuple[float, float]],
        on_recoil: Optional[Callable[[float, float], None]] = None,
        on_energy_deduct: Optional[Callable[[float], None]] = None,
        targets_group=None,
        particle_manager=None
    ) -> list[pygame.sprite.Sprite]:
        """Fires projectiles originating from exact local-space weapon mount points."""
        w_def = WEAPON_DEFS.get(self.active_weapon, {})
        w_upg = WEAPON_UPGRADES.get(self.active_weapon, {})
        base_cd = w_upg.get("base_cooldown", w_def.get("cooldown", 0.18))
        cost = w_def.get("energy_cost", 0.0)
        base_dmg = w_upg.get("base_damage", w_def.get("damage", 12))
        base_spd = w_upg.get("base_projectile_speed", w_def.get("speed", 650.0))
        w_lvl = self.weapon_upgrade_levels.get(self.active_weapon, 0)
        dmg = int((base_dmg + w_upg.get("upgrade_damage_per_lvl", 0) * w_lvl) * weapon_effectiveness)
        spd = float(base_spd + w_upg.get("upgrade_speed_per_lvl", 0.0) * w_lvl)
        col = w_def.get("color", COLOR_CYAN)
        proj_count = w_def.get("projectiles_per_shot", 1)
        spread_deg = w_def.get("spread_deg", 0.0)

        cd_scale = 0.50 if overdrive_active else (0.65 if overclock_active else 1.0)
        self.weapon_cooldowns[self.active_weapon] = max(0.05, base_cd + w_upg.get("upgrade_cooldown_per_lvl", 0.0) * w_lvl) * self.cooldown_mult * cd_scale

        if not overdrive_active and on_energy_deduct:
            on_energy_deduct(cost)

        self.muzzle_flash_timer = 0.08

        # Recoil Impulse
        if on_recoil:
            recoil_kick = 20.0
            on_recoil(-math.cos(aim_angle) * recoil_kick, -math.sin(aim_angle) * recoil_kick)

        bullets = []
        sm = get_sprite_manager()

        fwd_dx = math.cos(aim_angle) * 1500.0
        fwd_dy = math.sin(aim_angle) * 1500.0

        if self.active_weapon == WEAPON_PULSE:
            m_pos = get_mount_pos_fn("primary_front_center")
            sprite = sm.get_projectile_sprite('pulse', (40, 12))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(Bullet(m_pos, t_pt, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if overdrive_active:
                od_dmg = int(dmg * 1.25)
                bullets.append(Bullet(m_pos, t_pt, angle_offset_deg=-10.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite, owner="player", weapon_id=self.active_weapon))
                bullets.append(Bullet(m_pos, t_pt, angle_offset_deg=10.0, speed=spd * 1.1, damage=od_dmg, color=COLOR_GOLD, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_RAPID:
            mount_key = "dual_left" if self._rapid_side == 0 else "dual_right"
            self._rapid_side = (self._rapid_side + 1) % 2
            m_pos = get_mount_pos_fn(mount_key)
            sprite = sm.get_projectile_sprite('pulse', (32, 10))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(Bullet(m_pos, t_pt, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_SCATTER:
            left_pos = get_mount_pos_fn("left")
            right_pos = get_mount_pos_fn("right")
            sprite = sm.get_projectile_sprite('scatter', (40, 12))

            start_ang = -spread_deg / 2
            step = spread_deg / max(1, proj_count - 1) if proj_count > 1 else 0
            for i in range(proj_count):
                ang = start_ang + step * i
                origin = left_pos if i % 2 == 0 else right_pos
                t_pt = (origin[0] + fwd_dx, origin[1] + fwd_dy)
                bullets.append(Bullet(origin, t_pt, angle_offset_deg=ang, speed=spd, damage=dmg, color=col, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(left_pos, aim_angle, self.active_weapon)
                particle_manager.spawn_muzzle_flash(right_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_MISSILE:
            mount_key = "left" if self._missile_side == 0 else "right"
            self._missile_side = (self._missile_side + 1) % 2
            m_pos = get_mount_pos_fn(mount_key)
            sprite = sm.get_projectile_sprite('missile', (45, 16))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(HomingMissile(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_BARRAGE:
            pod_l = get_mount_pos_fn("pod_left")
            pod_r = get_mount_pos_fn("pod_right")
            sprite = sm.get_projectile_sprite('missile', (36, 12))
            t_pt_l = (pod_l[0] + fwd_dx, pod_l[1] + fwd_dy)
            t_pt_r = (pod_r[0] + fwd_dx, pod_r[1] + fwd_dy)
            bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-12.0, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-4.0, damage=dmg, speed=spd * 0.95, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=4.0, damage=dmg, speed=spd * 0.95, image=sprite, owner="player", weapon_id=self.active_weapon))
            bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=12.0, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(pod_l, aim_angle, self.active_weapon)
                particle_manager.spawn_muzzle_flash(pod_r, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_PLASMA:
            m_pos = get_mount_pos_fn("heavy_front_center")
            sprite = sm.get_projectile_sprite('plasma', (36, 36))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(HeavyPlasmaOrb(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_RAIL:
            m_pos = get_mount_pos_fn("rail_front")
            sprite = sm.get_projectile_sprite('rail', (64, 14))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(RailgunSlug(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_BEAM:
            self._fired_this_frame = True
            if getattr(self, "active_beam", None) is None or not self.active_beam.alive():
                m_pos = get_mount_pos_fn("beam_emitter")
                sprite = sm.get_projectile_sprite('beam', (52, 16))
                dps = dmg * 24.0
                self.active_beam = ContinuousBeam(m_pos, aim_angle, damage_per_second=dps, image=sprite, owner="player", weapon_id=self.active_weapon)
                bullets.append(self.active_beam)
                if particle_manager:
                    particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_TESLA:
            m_pos = get_mount_pos_fn("energy_center")
            sprite = sm.get_projectile_sprite('tesla', (34, 34))
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(TeslaArcBeam(m_pos, t_pt, damage=dmg, speed=spd, image=sprite, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_CLUSTER:
            m_pos = get_mount_pos_fn("primary")
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(ClusterTorpedo(m_pos, t_pt, damage=dmg, speed=spd, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        elif self.active_weapon == WEAPON_EMP:
            m_pos = get_mount_pos_fn("energy_center")
            t_pt = (m_pos[0] + fwd_dx, m_pos[1] + fwd_dy)
            bullets.append(EMPPulse(m_pos, t_pt, damage=dmg, speed=spd, owner="player", weapon_id=self.active_weapon))
            if particle_manager:
                particle_manager.spawn_muzzle_flash(m_pos, aim_angle, self.active_weapon)

        return bullets

    def update(self, dt: float, get_mount_pos_fn: Callable[[str], tuple[float, float]], aim_angle: float):
        """Updates continuous beam tracking, weapon cooldowns, and muzzle flash timer."""
        # Handle Continuous Beam Lifecycle
        if getattr(self, "active_beam", None) is not None and self.active_beam.alive():
            if not getattr(self, "_fired_this_frame", False) or self.active_weapon != WEAPON_BEAM:
                self.active_beam.active = False
                self.active_beam = None
            else:
                m_pos = get_mount_pos_fn("beam_emitter")
                self.active_beam.update_transform(m_pos, aim_angle, self.active_beam.length)
        self._fired_this_frame = False

        # Visual Flash Timers
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer = max(0.0, self.muzzle_flash_timer - dt)

        # Cooldown Timers
        for w in self.weapon_cooldowns:
            if self.weapon_cooldowns[w] > 0:
                self.weapon_cooldowns[w] = max(0.0, self.weapon_cooldowns[w] - dt)
