"""
================================================================================
                DRONE HUNTER 2D - CLUSTER WEAPON BEHAVIOR
================================================================================
Fires heavy cluster torpedo that detonates into submunition bomblets on impact.
"""

import pygame
from src.entities.bullet import ClusterTorpedo
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class ClusterBehavior(BaseWeaponBehavior):
    """Fires submunition cluster torpedo."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []

        m_pos = context.get_mount_pos_fn("primary")
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(ClusterTorpedo(
            m_pos, t_pt,
            damage=context.damage, speed=context.speed,
            owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
