"""
================================================================================
                DRONE HUNTER 2D - PULSE WEAPON BEHAVIOR
================================================================================
Standard concentrated energy pulse bolts with tri-spread burst in Overdrive mode.
"""

import pygame
from src.data.settings import COLOR_GOLD
from src.entities.bullet import Bullet
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class PulseBehavior(BaseWeaponBehavior):
    """Fires forward energy bolts from primary front center mount."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()
        m_pos = context.get_mount_pos_fn("primary_front_center")
        sprite = sm.get_projectile_sprite('pulse', (40, 12))
        t_pt = (m_pos[0] + context.fwd_dx, m_pos[1] + context.fwd_dy)

        bullets.append(Bullet(
            m_pos, t_pt,
            speed=context.speed, damage=context.damage, color=context.color,
            image=sprite, owner="player", weapon_id=context.weapon_id
        ))

        if context.overdrive_active:
            od_dmg = int(context.damage * 1.25)
            bullets.append(Bullet(
                m_pos, t_pt, angle_offset_deg=-10.0,
                speed=context.speed * 1.1, damage=od_dmg, color=COLOR_GOLD,
                image=sprite, owner="player", weapon_id=context.weapon_id
            ))
            bullets.append(Bullet(
                m_pos, t_pt, angle_offset_deg=10.0,
                speed=context.speed * 1.1, damage=od_dmg, color=COLOR_GOLD,
                image=sprite, owner="player", weapon_id=context.weapon_id
            ))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
