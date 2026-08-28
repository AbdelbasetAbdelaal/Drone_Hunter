"""
================================================================================
                DRONE HUNTER 2D - PLASMA WEAPON BEHAVIOR
================================================================================
Fires heavy, high-damage plasma projectile from heavy front center mount.
"""

import pygame
from src.entities.bullet import HeavyPlasmaOrb
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class PlasmaBehavior(BaseWeaponBehavior):
    """Fires heavy plasma orb."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        m_pos = context.get_mount_pos_fn("heavy_front_center")
        sprite = sm.get_projectile_sprite('plasma', (36, 36))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(HeavyPlasmaOrb(
            m_pos, t_pt,
            damage=context.damage, speed=context.speed,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
