"""
================================================================================
                DRONE HUNTER 2D - BEAM WEAPON BEHAVIOR
================================================================================
Continuous sustained laser beam emitter with dynamic real-time tracking.
"""

import pygame
from src.entities.bullet import ContinuousBeam
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class ContinuousBeamBehavior(BaseWeaponBehavior):
    """Fires and manages sustained laser beam emitter."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        if context.on_fired_this_frame:
            context.on_fired_this_frame()

        active_beam = context.active_beam
        if active_beam is None or not active_beam.alive():
            m_pos = context.get_mount_pos_fn("beam_emitter")
            sprite = sm.get_projectile_sprite('beam', (52, 16))
            dps = context.damage * 24.0
            new_beam = ContinuousBeam(
                m_pos, context.aim_angle,
                damage_per_second=dps, image=sprite,
                owner="player", weapon_id=context.weapon_id
            )
            if context.on_beam_created:
                context.on_beam_created(new_beam)
            bullets.append(new_beam)
            if context.particle_manager:
                context.particle_manager.spawn_muzzle_flash(m_pos, context.aim_angle, context.weapon_id)

        return bullets
