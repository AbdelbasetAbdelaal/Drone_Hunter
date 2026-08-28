"""
================================================================================
                DRONE HUNTER 2D - SCATTER WEAPON BEHAVIOR
================================================================================
Wide multi-projectile spread burst originating from alternating left and right mounts.
"""

import pygame
from src.entities.bullet import Bullet
from src.rendering.sprite_manager import get_sprite_manager
from src.data.game_data import WEAPON_DEFS, WEAPON_SCATTER
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class ScatterBehavior(BaseWeaponBehavior):
    """Fires wide spread fan of energy projectiles."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        left_pos = context.get_mount_pos_fn("left")
        right_pos = context.get_mount_pos_fn("right")
        sprite = sm.get_projectile_sprite('scatter', (40, 12))

        w_def = WEAPON_DEFS.get(context.weapon_id, {})
        proj_count = w_def.get("projectiles_per_shot", 5)
        spread_deg = w_def.get("spread_deg", 36.0)

        start_ang = -spread_deg / 2
        step = spread_deg / max(1, proj_count - 1) if proj_count > 1 else 0

        for i in range(proj_count):
            ang = start_ang + step * i
            origin = left_pos if i % 2 == 0 else right_pos
            t_pt = (origin[0] + context.fwd_dx, origin[1] + context.fwd_dy)
            bullets.append(Bullet(
                origin, t_pt, angle_offset_deg=ang,
                speed=context.speed, damage=context.damage, color=context.color,
                image=sprite, owner="player", weapon_id=context.weapon_id
            ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(left_pos, context.aim_angle, context.weapon_id)
            context.particle_manager.spawn_muzzle_flash(right_pos, context.aim_angle, context.weapon_id)

        return bullets
