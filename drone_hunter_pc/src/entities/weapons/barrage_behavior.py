"""
================================================================================
                DRONE HUNTER 2D - BARRAGE WEAPON BEHAVIOR
================================================================================
Quad missile salvo fired from dedicated left and right missile pods with precise angle offsets.
"""

import pygame
from src.entities.bullet import BarrageMissile
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext


class BarrageBehavior(BaseWeaponBehavior):
    """Fires quad-missile barrage salvo."""

    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        bullets = []
        sm = get_sprite_manager()

        pod_l = context.get_mount_pos_fn("pod_left")
        pod_r = context.get_mount_pos_fn("pod_right")
        sprite = sm.get_projectile_sprite('missile', (36, 12))

        t_pt_l = (pod_l[0] + context.fwd_dx, pod_l[1] + context.fwd_dy)
        t_pt_r = (pod_r[0] + context.fwd_dx, pod_r[1] + context.fwd_dy)

        bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-12.0, damage=context.damage, speed=context.speed, image=sprite, owner="player", weapon_id=context.weapon_id))
        bullets.append(BarrageMissile(pod_l, t_pt_l, angle_offset_deg=-4.0, damage=context.damage, speed=context.speed * 0.95, image=sprite, owner="player", weapon_id=context.weapon_id))
        bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=4.0, damage=context.damage, speed=context.speed * 0.95, image=sprite, owner="player", weapon_id=context.weapon_id))
        bullets.append(BarrageMissile(pod_r, t_pt_r, angle_offset_deg=12.0, damage=context.damage, speed=context.speed, image=sprite, owner="player", weapon_id=context.weapon_id))

        if context.particle_manager:
            context.particle_manager.spawn_muzzle_flash(pod_l, context.aim_angle, context.weapon_id)
            context.particle_manager.spawn_muzzle_flash(pod_r, context.aim_angle, context.weapon_id)

        return bullets
