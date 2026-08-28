"""
================================================================================
                DRONE HUNTER 2D - TESLA WEAPON BEHAVIOR
================================================================================
High-voltage electrical arc discharging from energy center hardpoint.
"""

import pygame
from src.entities.bullet import TeslaArcBeam
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class TeslaBehavior(BaseWeaponBehavior):
    """Fires chaining electrical arc beam."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        m_pos = context.get_mount_pos_fn("energy_center")
        sprite = sm.get_projectile_sprite('tesla', (34, 34))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(TeslaArcBeam(
            m_pos, t_pt,
            damage=context.damage, speed=context.speed,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
