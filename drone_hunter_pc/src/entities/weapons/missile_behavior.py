"""
================================================================================
                DRONE HUNTER 2D - MISSILE WEAPON BEHAVIOR
================================================================================
Homing micro-missiles launched from alternating left and right wing hardpoints.
"""

import pygame
from src.entities.bullet import HomingMissile
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class MissileBehavior(BaseWeaponBehavior):
    """Fires target-seeking micro-missiles."""

    def __init__(self):
        self._missile_side: int = 0

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        mount_key = "left" if self._missile_side == 0 else "right"
        self._missile_side = (self._missile_side + 1) % 2

        m_pos = context.get_mount_pos_fn(mount_key)
        sprite = sm.get_projectile_sprite('missile', (45, 16))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(HomingMissile(
            m_pos, t_pt,
            damage=context.damage, speed=context.speed,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
