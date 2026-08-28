"""
================================================================================
                DRONE HUNTER 2D - RAPID WEAPON BEHAVIOR
================================================================================
High-rate alternating dual cannon fire from dual_left and dual_right mounts.
"""

import pygame
from src.entities.bullet import Bullet
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class RapidBehavior(BaseWeaponBehavior):
    """Fires alternating rapid pulse bolts from wing hardpoints."""

    def __init__(self):
        self._rapid_side: int = 0

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        mount_key = "dual_left" if self._rapid_side == 0 else "dual_right"
        self._rapid_side = (self._rapid_side + 1) % 2
        if context.controller:
            context.controller._rapid_side = self._rapid_side

        m_pos = context.get_mount_pos_fn(mount_key)
        sprite = sm.get_projectile_sprite('pulse', (32, 10))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(Bullet(
            m_pos, t_pt,
            speed=context.speed, damage=context.damage, color=context.color,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
