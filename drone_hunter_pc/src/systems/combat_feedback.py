"""
================================================================================
            DRONE HUNTER 2D - COMBAT FEEDBACK & IMPACT EFFECTS
================================================================================
Centralized visual and tactile combat feedback system managing kinetic impact
sparks, enemy hit flashes, floating damage numbers, and camera micro-shakes.
"""

import math
import random
import pygame
from src.data.settings import COLOR_CYAN, COLOR_GOLD, COLOR_WHITE, COLOR_CRIMSON

class CombatFeedbackSystem:
    def __init__(self, context):
        self.context = context

    def on_projectile_hit_enemy(self, target, bullet, damage: int, is_dead: bool = False):
        """Dispatches rich audiovisual and particle feedback when a projectile hits an enemy."""
        ctx = self.context
        
        # 1. Trigger enemy hit flash
        if hasattr(target, "hit_flash_timer"):
            target.hit_flash_timer = 0.12

        # 2. Spawn Directional Kinetic Impact Sparks
        impact_pos = bullet.rect.center if hasattr(bullet, "rect") else target.rect.center
        spark_color = getattr(bullet, "color", COLOR_CYAN)
        ctx.particle_manager.spawn_spark(impact_pos, count=8, color=spark_color)
        
        # 3. Floating Combat Damage Text
        ctx.particle_manager.spawn_floating_text(
            (target.rect.centerx + random.randint(-12, 12), target.rect.top - 6),
            f"-{damage}",
            COLOR_WHITE,
            size=18
        )

        # 4. Subtle Camera Micro-Shake
        ctx.trigger_shake(3.0, 0.10)

        # 5. Play Hit Audio
        if ctx.audio_manager:
            ctx.audio_manager.play_hit()

        # 6. If eliminated, dispatch destruction feedback
        if is_dead:
            if getattr(target, "is_boss", False):
                ctx.particle_manager.spawn_boss_explosion(target.rect.center)
                ctx.trigger_shake(14.0, 0.55)
            else:
                target_color = getattr(target, "color", COLOR_CRIMSON)
                ctx.particle_manager.spawn_enemy_death(target.rect.center, target_color)
                ctx.trigger_shake(6.0, 0.20)

            if ctx.audio_manager:
                ctx.audio_manager.play_explosion()

    def on_player_hit(self, damage: int):
        """Dispatches player damage feedback."""
        ctx = self.context
        if ctx.player:
            ctx.player.damage_flash_timer = 0.18
            ctx.trigger_shake(8.0, 0.25)
            ctx.trigger_damage_flash()
            ctx.particle_manager.spawn_spark(ctx.player.rect.center, count=12, color=COLOR_CRIMSON)
            if ctx.audio_manager:
                ctx.audio_manager.play_player_hit()

    def on_boundary_impact(self, pos: tuple[float, float], normal_x: float, normal_y: float):
        """Spawns deflection sparks when drone grazes arena perimeter."""
        ctx = self.context
        ctx.particle_manager.spawn_spark(pos, count=3, color=COLOR_CYAN)
