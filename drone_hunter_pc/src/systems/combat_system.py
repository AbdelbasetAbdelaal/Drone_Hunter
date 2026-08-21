"""
================================================================================
                    DRONE HUNTER 2D - COMBAT & COLLISION PIPELINE
================================================================================
Centralized combat engine resolving 2D sprite collisions, damage formulas,
chain lightning reactions, cluster bomblets, shield hit absorption, and drops.
"""

import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_SLOWMO, COLOR_COIN,
    COLOR_NEON_RED, COLOR_TESLA
)
from src.data.game_data import (
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER,
    TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED, TARGET_TYPE_BOSS,
    REWARD_SCOUT, REWARD_SHOOTER, REWARD_HEAVY
)
from src.entities.bullet import TeslaArcBeam, ClusterTorpedo
from src.entities.powerup import PowerupItem
from src.core.game_state import STATE_GAME_OVER, STATE_MISSION_FAILED
from src.systems.combat_feedback import CombatFeedbackSystem

class CombatSystem:
    def __init__(self, context):
        self.context = context
        self.feedback = CombatFeedbackSystem(context)

    def execute_emp_blast(self):
        """Executes player EMP Shockwave, clearing all screen bullets and damaging enemies."""
        ctx = self.context
        player = ctx.player
        if player and player.trigger_emp():
            ctx.audio_manager.play_emp()
            ctx.trigger_shake(12.0, 0.45)
            ctx.particle_manager.spawn_emp_shockwave(player.pos)

            # Eliminate all enemy bullets
            for eb in list(ctx.enemy_bullet_group):
                eb.kill()
                ctx.particle_manager.spawn_spark(eb.rect.center, count=5, color=COLOR_CYAN)

            # Damage & destroy regular enemies
            for t in list(ctx.target_group):
                if getattr(t, "is_boss", False):
                    is_dead = t.take_damage(75, source="emp")
                    ctx.particle_manager.spawn_spark(t.rect.center, count=15, color=COLOR_CYAN)
                else:
                    pts = t.score_value
                    ctx.add_score(pts)
                    t.kill()
                    ctx.particle_manager.spawn_explosion(t.rect.center, count=25, color=COLOR_CYAN)
                    ctx.particle_manager.spawn_floating_text(t.rect.center, f"+{pts} EMP!", COLOR_CYAN, 22)

            for obs in list(ctx.obstacle_group):
                obs.kill()
                ctx.particle_manager.spawn_explosion(obs.rect.center, count=30, color=(239, 68, 68))

    def update_combat(self, dt: float):
        ctx = self.context
        player = ctx.player
        if not player or not player.alive:
            return

        # 1. Player Bullets vs Environmental Obstacles
        for b in list(ctx.bullet_group):
            hit_obs = pygame.sprite.spritecollide(b, ctx.obstacle_group, False, pygame.sprite.collide_circle)
            for obs in hit_obs:
                b.kill()
                if obs.take_damage(getattr(b, "damage", 35)):
                    obs.kill()
                    ctx.audio_manager.play_mine_explosion()
                    ctx.trigger_shake(9.0, 0.3)
                    ctx.particle_manager.spawn_explosion(obs.rect.center, count=35, color=(239, 68, 68))

        # 2. Player Bullets vs Hostile Enemies
        # PERF: Build shield-drone list once per frame, not once per bullet-hit
        shield_drones = [t for t in ctx.target_group if getattr(t, "enemy_type", "") == TARGET_TYPE_SHIELD_DRONE]

        for b in list(ctx.bullet_group):
            hits = pygame.sprite.spritecollide(b, ctx.target_group, False)
            for target in hits:
                dmg = getattr(b, "damage", 25)

                # PERF: Check shield protection using pre-built list (O(shield_drones) not O(all_targets))
                is_shielded = False
                for ally in shield_drones:
                    if ally != target and math.hypot(target.pos.x - ally.pos.x, target.pos.y - ally.pos.y) <= 160.0:
                        is_shielded = True
                        break
                if is_shielded:
                    dmg = max(4, dmg // 3)
                    if ctx.particle_manager: ctx.particle_manager.spawn_shield_ripple(target.rect.center)

                is_dead = target.take_damage(dmg, source="bullet")

                # Tesla Arc Lightning Chain Reaction
                if isinstance(b, TeslaArcBeam):
                    b.chained_targets.add(target)
                    if ctx.audio_manager: ctx.audio_manager.play_tesla()
                    available = [t for t in ctx.target_group if t not in b.chained_targets and t.alive]
                    if available:
                        nearest_chain = sorted(available, key=lambda t: math.hypot(t.pos.x - target.pos.x, t.pos.y - target.pos.y))[:2]
                        for chained_enemy in nearest_chain:
                            b.chained_targets.add(chained_enemy)
                            chained_dead = chained_enemy.take_damage(dmg // 2, source="tesla")
                            if ctx.particle_manager:
                                ctx.particle_manager.spawn_lightning_arc(target.rect.center, chained_enemy.rect.center, COLOR_TESLA)
                                ctx.particle_manager.spawn_spark(chained_enemy.rect.center, count=6, color=COLOR_TESLA)
                            if chained_dead:
                                if ctx.audio_manager: ctx.audio_manager.play_explosion()
                                earned = ctx.add_score(chained_enemy.score_value)
                                
                                if chained_enemy.enemy_type == TARGET_TYPE_SCOUT:
                                    ctx.scrap += REWARD_SCOUT
                                elif chained_enemy.enemy_type == TARGET_TYPE_SHOOTER:
                                    ctx.scrap += REWARD_SHOOTER
                                elif chained_enemy.enemy_type == TARGET_TYPE_HEAVY:
                                    ctx.scrap += REWARD_HEAVY

                                if ctx.particle_manager: ctx.particle_manager.spawn_floating_text(chained_enemy.rect.center, f"+{earned}", COLOR_GOLD, 20)

                if not getattr(b, "is_piercing", False):
                    b.kill()

                if ctx.particle_manager:
                    etype = getattr(target, "enemy_type", "")
                    if etype in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
                        ctx.particle_manager.spawn_heavy_impact(b.rect.center)
                    else:
                        ctx.particle_manager.spawn_enemy_hit_sparks(b.rect.center, etype, dmg)
                if ctx.audio_manager: ctx.audio_manager.play_hit()

                if is_dead:
                    if ctx.audio_manager: ctx.audio_manager.play_explosion()
                    shake_intensity = 3.0 if not getattr(target, "is_boss", False) else 4.0
                    ctx.trigger_shake(shake_intensity, 0.2)
                    earned_pts = ctx.add_score(target.score_value)
                    
                    if target.enemy_type == TARGET_TYPE_SCOUT:
                        ctx.scrap += REWARD_SCOUT
                    elif target.enemy_type == TARGET_TYPE_SHOOTER:
                        ctx.scrap += REWARD_SHOOTER
                    elif target.enemy_type == TARGET_TYPE_HEAVY:
                        ctx.scrap += REWARD_HEAVY


                    # Death Explosion Particles
                    if ctx.particle_manager:
                        if getattr(target, "is_boss", False):
                            ctx.particle_manager.spawn_boss_explosion(target.rect.center)
                        else:
                            ctx.particle_manager.spawn_enemy_death(target.rect.center, target.color)
                        ctx.particle_manager.spawn_floating_text(target.rect.center, f"+{earned_pts}", COLOR_GOLD, 20)

                    # Power-up drop roll with difficulty drop rate scaling
                    drop_rate = ctx.difficulty_data.get("powerup_drop_rate", 0.30)
                    if random.random() < drop_rate:
                        p_type = random.choice(["battery", "overclock", "shield", "slowmo", "coin", "wingman", "weapon"])
                        ctx.powerup_group.add(PowerupItem(target.rect.center, p_type))

        # 3. Enemy Bullets vs Player Drone
        if player.alive and not player.is_invulnerable and not player.is_cloaked:
            e_hits = pygame.sprite.spritecollide(player, ctx.enemy_bullet_group, True)
            for eb in e_hits:
                dmg = getattr(eb, "damage", 20)
                diff_dmg_mult = ctx.difficulty_data.get("damage_mult", 1.0)
                scaled_dmg = dmg * diff_dmg_mult

                had_shield = player.shield_hits > 0
                is_destroyed = player.take_damage(scaled_dmg)

                if had_shield:
                    if ctx.audio_manager: ctx.audio_manager.play_hit()
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=10, color=COLOR_SHIELD)
                else:
                    ctx.trigger_shake(4.0, 0.2)
                    ctx.damage_flash_timer = 0.18
                    if ctx.audio_manager: ctx.audio_manager.play_explosion()
                    if ctx.particle_manager: ctx.particle_manager.spawn_explosion(player.rect.center, count=20, color=COLOR_CRIMSON)

                if is_destroyed:
                    if ctx.particle_manager:
                        ctx.particle_manager.spawn_player_destruction(player.rect.center)
                    ctx.trigger_shake(5.0, 0.4)
                    if hasattr(ctx, "mission_system") and ctx.mission_system and ctx.mission_system.active_mission_id is not None:
                        ctx.mission_system.trigger_failure()
                        ctx.state = STATE_MISSION_FAILED
                    else:
                        ctx.state = STATE_GAME_OVER

        # 3B. Hostile Enemies vs Player Drone (Contact Damage with Cooldown)
        if player.alive and not player.is_invulnerable and not player.is_cloaked:
            c_hits = pygame.sprite.spritecollide(player, ctx.target_group, False)
            for enemy in c_hits:
                if getattr(enemy, "alive", True) and getattr(enemy, "contact_cooldown_timer", 0.0) <= 0.0:
                    c_dmg = getattr(enemy, "contact_damage", 20.0)
                    enemy.contact_cooldown_timer = 1.0 # 1.0s contact cooldown per enemy

                    had_shield = player.shield_hits > 0
                    is_destroyed = player.take_damage(c_dmg)

                    if had_shield:
                        if ctx.audio_manager: ctx.audio_manager.play_hit()
                        if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=12, color=COLOR_SHIELD)
                    else:
                        ctx.trigger_shake(4.0, 0.2)
                        ctx.damage_flash_timer = 0.18
                        if ctx.audio_manager: ctx.audio_manager.play_hit()
                        if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=15, color=COLOR_CRIMSON)

                    if is_destroyed:
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(5.0, 0.4)
                        if hasattr(ctx, "mission_system") and ctx.mission_system and ctx.mission_system.active_mission_id is not None:
                            ctx.mission_system.trigger_failure()
                            ctx.state = STATE_MISSION_FAILED
                        else:
                            ctx.state = STATE_GAME_OVER

        # 4. Hazards vs Player
        if player.alive and not player.is_cloaked:
            h_hits = pygame.sprite.spritecollide(player, ctx.hazard_group, False)
            for h in h_hits:
                if hasattr(h, "gap_y"): # LaserGridFence
                    is_destroyed = player.take_damage(35.0 * dt)
                    ctx.trigger_shake(4.0, 0.1)
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=4, color=COLOR_NEON_RED)
                    if is_destroyed:
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(5.0, 0.4)
                        if hasattr(ctx, "mission_system") and ctx.mission_system and ctx.mission_system.active_mission_id is not None:
                            ctx.mission_system.trigger_failure()
                            ctx.state = STATE_MISSION_FAILED
                        else:
                            ctx.state = STATE_GAME_OVER

        # 5. Player vs Power-up Items
        if player.alive:
            p_hits = pygame.sprite.spritecollide(player, ctx.powerup_group, True)
            for p in p_hits:
                if ctx.audio_manager: ctx.audio_manager.play_powerup()
                if p.p_type == "battery":
                    player.health = min(player.max_health, player.health + 35.0)
                    player.energy = min(player.max_energy, player.energy + 25.0)
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "+HULL REPAIR", COLOR_EMERALD, 18)
                elif p.p_type == "overclock":
                    player.trigger_overclock(6.0)
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "OVERCLOCK!", COLOR_OVERCLOCK, 22)
                elif p.p_type == "shield":
                    player.activate_shield(3)
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "SHIELD CHARGED", COLOR_SHIELD, 20)
                elif p.p_type == "slowmo": # Proper bullet-time slow motion (Bug 2)
                    ctx.trigger_slowmo(5.0)
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "TIME DILATION", COLOR_SLOWMO, 20)
                elif p.p_type == "coin":
                    ctx.coins += 50
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "+50 SCRAP", COLOR_COIN, 18)
                elif p.p_type == "wingman":
                    player.spawn_wingman()
                    ctx.particle_manager.spawn_floating_text(p.rect.center, "+WINGMAN DRONE", COLOR_CYAN, 20)
                elif p.p_type == "weapon":
                    player.cycle_weapon()
                    ctx.particle_manager.spawn_floating_text(p.rect.center, f"WPN: {player.active_weapon.upper()}", COLOR_GOLD, 22)
