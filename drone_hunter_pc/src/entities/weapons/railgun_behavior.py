"""
================================================================================
                DRONE HUNTER 2D - RAILGUN WEAPON BEHAVIOR
================================================================================
Fires hyper-velocity penetrating tungsten slug from rail front hardpoint.
"""

import pygame
from src.entities.bullet import RailgunSlug
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class RailgunBehavior(BaseWeaponBehavior):
    """Fires penetrating hyper-velocity railgun slug."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        m_pos = context.get_mount_pos_fn("rail_front")
        sprite = sm.get_projectile_sprite('rail', (64, 14))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(RailgunSlug(
            m_pos, t_pt,
            damage=context.damage, speed=context.speed,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
