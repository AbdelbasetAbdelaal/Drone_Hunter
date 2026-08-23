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
            from src.entities.bullet import EMPShockwave
            # Huge shockwave for the ultimate ability (1200 radius = covers the screen over time)
            ctx.bullet_group.add(EMPShockwave(player.rect.center, max_radius=1200.0, lifetime=1.5, owner="player"))

    def update_combat(self, dt: float):
        ctx = self.context
        player = ctx.player
        if not player or not player.alive:
            return

        # 1. Player Bullets vs Environmental Obstacles
        for b in list(ctx.bullet_group):
            hit_obs = pygame.sprite.spritecollide(b, ctx.obstacle_group, False, pygame.sprite.collide_circle)
            for obs in hit_obs:
                if getattr(b, "is_emp_projectile", False):
                    b.detonate(ctx)
                else:
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
            if getattr(b, "is_continuous", False):
                # 1. Raycast against obstacles to find beam length
                start_x, start_y = b.muzzle_pos.x, b.muzzle_pos.y
                dx = math.cos(b.angle_rad)
                dy = math.sin(b.angle_rad)
                max_len = 2000.0
                closest_hit = max_len
                
                # Check obstacles
                for obs in list(ctx.obstacle_group):
                    # Simple ray-circle intersection
                    cx, cy = obs.pos.x, obs.pos.y
                    r = obs.radius
                    fx = start_x - cx
                    fy = start_y - cy
                    a = dx*dx + dy*dy
                    b_coef = 2 * (fx*dx + fy*dy)
                    c = (fx*fx + fy*fy) - r*r
                    disc = b_coef*b_coef - 4*a*c
                    if disc >= 0:
                        t = (-b_coef - math.sqrt(disc)) / (2*a)
                        if 0 <= t < closest_hit:
                            closest_hit = t
                            if ctx.particle_manager and random.random() < 0.4:
                                hit_pt = (start_x + dx*t, start_y + dy*t)
                                ctx.particle_manager.spawn_spark(hit_pt, count=random.randint(1, 3), color=(255, 140, 0))
                
                b.length = closest_hit

                # 2. Damage enemies along the beam
                dmg = b.damage_per_second * dt
                for target in list(ctx.target_group):
                    cx, cy = target.pos.x, target.pos.y
                    # Distance from point to line segment
                    fx = cx - start_x
                    fy = cy - start_y
                    dot = fx*dx + fy*dy
                    t = max(0.0, min(b.length, dot))
                    proj_x = start_x + t*dx
                    proj_y = start_y + t*dy
                    dist = math.hypot(cx - proj_x, cy - proj_y)
                    
                    if dist <= target.radius + 8.0:
                        if not getattr(target, "alive", False):
                            continue
                        # Enemy is hit by continuous beam
                        is_shielded = False
                        for ally in shield_drones:
                            if ally != target and math.hypot(target.pos.x - ally.pos.x, target.pos.y - ally.pos.y) <= 160.0:
                                is_shielded = True
                                break
                        if is_shielded:
                            dmg = max(1.0, dmg / 3.0)
                            if ctx.particle_manager and random.random() < 0.15:
                                ctx.particle_manager.spawn_shield_ripple(target.rect.center)
                        
                        target.take_damage(dmg, source="beam")
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark((proj_x, proj_y), count=random.randint(1, 3), color=(56, 189, 248))
                            if random.random() < 0.35:
                                ctx.particle_manager.spawn_enemy_hit_sparks((proj_x, proj_y), getattr(target, "enemy_type", ""), 10)

                # 3. Disintegrate incoming enemy projectiles caught in the plasma beam
                for eb in list(ctx.enemy_bullet_group):
                    ecx, ecy = eb.pos.x, eb.pos.y
                    efx = ecx - start_x
                    efy = ecy - start_y
                    edot = efx*dx + efy*dy
                    et = max(0.0, min(b.length, edot))
                    eproj_x = start_x + et*dx
                    eproj_y = start_y + et*dy
                    edist = math.hypot(ecx - eproj_x, ecy - eproj_y)
                    if edist <= eb.radius + 14.0:
                        eb.kill()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark((eproj_x, eproj_y), count=2, color=(56, 189, 248))
                continue

            elif getattr(b, "is_emp_shockwave", False):
                for target in list(ctx.target_group):
                    if target in getattr(b, "hit_targets", set()):
                        continue
                    dist = math.hypot(target.pos.x - b.pos.x, target.pos.y - b.pos.y)
                    if dist <= target.radius + b.radius:
                        if not getattr(target, "alive", False):
                            continue
                        b.hit_targets.add(target)
                        is_dead = target.take_damage(b.damage, source="emp")
                        if not getattr(target, "is_boss", False):
                            target.emp_jammed_timer = 3.0
                            if ctx.particle_manager:
                                ctx.particle_manager.spawn_spark(target.rect.center, 5, COLOR_CYAN)
                        if is_dead:
                            ctx.total_kills += 1
                            ctx.emp_kills += 1
                            ctx.add_score(target.score_value)
                            if ctx.particle_manager: ctx.particle_manager.spawn_explosion(target.rect.center, 25, COLOR_CYAN)

                # Wipe enemy bullets in radius
                for eb in list(ctx.enemy_bullet_group):
                    dist = math.hypot(eb.pos.x - b.pos.x, eb.pos.y - b.pos.y)
                    if dist <= eb.radius + b.radius:
                        eb.kill()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark(eb.rect.center, count=3, color=COLOR_CYAN)

                for obs in list(ctx.obstacle_group):
                    if obs in getattr(b, "hit_targets", set()):
                        continue
                    dist = math.hypot(obs.pos.x - b.pos.x, obs.pos.y - b.pos.y)
                    if dist <= obs.radius + b.radius:
                        b.hit_targets.add(obs)
                        if obs.take_damage(b.damage):
                            obs.kill()
                            if ctx.particle_manager: ctx.particle_manager.spawn_explosion(obs.rect.center, 30, (239, 68, 68))
                continue

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
                    dmg = max(4, int(dmg // 3))
                    if ctx.particle_manager: ctx.particle_manager.spawn_shield_ripple(target.rect.center)

                is_dead = target.take_damage(dmg, source="bullet")
                
                if getattr(b, "is_emp_projectile", False):
                    b.detonate(ctx)
                    continue

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
                                ctx.total_kills += 1
                                if ctx.player and getattr(ctx.player, "overdrive_timer", 0.0) > 0.0:
                                    ctx.overdrive_kills += 1
                                
                                if chained_enemy.enemy_type == TARGET_TYPE_SCOUT:
                                    ctx.scrap += int(REWARD_SCOUT * ctx.ng_plus_scrap_mult)
                                elif chained_enemy.enemy_type == TARGET_TYPE_SHOOTER:
                                    ctx.scrap += int(REWARD_SHOOTER * ctx.ng_plus_scrap_mult)
                                elif chained_enemy.enemy_type == TARGET_TYPE_HEAVY:
                                    ctx.scrap += int(REWARD_HEAVY * ctx.ng_plus_scrap_mult)

                                if ctx.particle_manager:
                                    score_col = getattr(chained_enemy, "color", COLOR_GOLD)
                                    ctx.particle_manager.spawn_floating_text(chained_enemy.rect.center, f"+{earned}", score_col, 20)

                if not getattr(b, "is_piercing", False):
                    b.kill()

                if ctx.particle_manager:
                    w_id = getattr(b, "weapon_id", "pulse")
                    ctx.particle_manager.spawn_weapon_impact(b.rect.center, w_id)
                    etype = getattr(target, "enemy_type", "")
                    if etype in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
                        ctx.particle_manager.spawn_heavy_impact(b.rect.center)
                    else:
                        ctx.particle_manager.spawn_enemy_hit_sparks(b.rect.center, etype, dmg)
                if ctx.audio_manager:
                    hit_target_type = getattr(target, "enemy_type", "")
                    if getattr(target, "is_boss", False):
                        hit_target_type = "boss"
                    elif is_shielded:
                        hit_target_type = "shield"
                    ctx.audio_manager.play_hit(hit_target_type)

                # Damage numbers on hit
                if ctx.particle_manager:
                    dmg_color = (255, 255, 255) if dmg >= 50 else ((255, 200, 50) if dmg >= 25 else (200, 220, 255))
                    ctx.particle_manager.spawn_floating_text(target.rect.center, f"-{int(dmg)}", dmg_color, 16)

                if is_dead:
                    ctx.total_kills += 1
                    if getattr(ctx.player, "overdrive_timer", 0.0) > 0.0:
                        ctx.overdrive_kills += 1
                    if ctx.audio_manager:
                        death_type = getattr(target, "enemy_type", "")
                        if getattr(target, "is_boss", False):
                            death_type = "boss"
                            ctx.boss_defeat_timer = 2.5
                        ctx.audio_manager.play_death(death_type)
                    shake_intensity = 5.5 if not getattr(target, "is_boss", False) else 8.0
                    ctx.trigger_shake(shake_intensity, 0.25)
                    if getattr(ctx, "hit_stop_timer", 0.0) <= 0.0:
                        ctx.trigger_hit_stop(0.06 if not getattr(target, "is_boss", False) else 0.10)
                    target_score = getattr(target, "score_value", 100)
                    target_etype = getattr(target, "enemy_type", "")
                    target_col = getattr(target, "color", getattr(target, "color_outer", COLOR_GOLD))
                    earned_pts = ctx.add_score(target_score)
                    
                    if target_etype == TARGET_TYPE_SCOUT:
                        ctx.scrap += int(REWARD_SCOUT * ctx.ng_plus_scrap_mult)
                    elif target_etype == TARGET_TYPE_SHOOTER:
                        ctx.scrap += int(REWARD_SHOOTER * ctx.ng_plus_scrap_mult)
                    elif target_etype == TARGET_TYPE_HEAVY:
                        ctx.scrap += int(REWARD_HEAVY * ctx.ng_plus_scrap_mult)
                    elif hasattr(target, "scrap_reward"):
                        ctx.scrap += int(target.scrap_reward * ctx.ng_plus_scrap_mult)

                    # Death Explosion Particles
                    if ctx.particle_manager:
                        if getattr(target, "is_boss", False):
                            ctx.particle_manager.spawn_boss_explosion(target.rect.center)
                        else:
                            ctx.particle_manager.spawn_enemy_death(target.rect.center, target_col, enemy_type=target_etype)
                        ctx.particle_manager.spawn_floating_text(target.rect.center, f"+{earned_pts}", target_col, 20)

                    # Power-up drop roll with difficulty drop rate scaling
                    drop_rate = 1.0 if getattr(target, "is_boss", False) else ctx.difficulty_data.get("powerup_drop_rate", 0.30)
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
                    if ctx.audio_manager: ctx.audio_manager.play_hit_shield()
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=10, color=COLOR_SHIELD)
                else:
                    ctx.trigger_shake(4.0, 0.2)
                    ctx.damage_flash_timer = 0.18
                    if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                    if ctx.particle_manager: ctx.particle_manager.spawn_explosion(player.rect.center, count=20, color=COLOR_CRIMSON)
                    if ctx.mission_start_time > 0:
                        ctx.mission_damage_taken += scaled_dmg

                if is_destroyed:
                    if ctx.audio_manager: ctx.audio_manager.play_player_death()
                    if ctx.particle_manager:
                        ctx.particle_manager.spawn_player_destruction(player.rect.center)
                    ctx.trigger_shake(10.0, 0.7)

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
                        if ctx.audio_manager: ctx.audio_manager.play_hit_shield()
                        if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=12, color=COLOR_SHIELD)
                    else:
                        ctx.trigger_shake(4.0, 0.2)
                        ctx.damage_flash_timer = 0.18
                        if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                        if ctx.particle_manager: ctx.particle_manager.spawn_explosion(player.rect.center, count=15, color=COLOR_CRIMSON)
                        if ctx.mission_start_time > 0:
                            ctx.mission_damage_taken += c_dmg

                    if is_destroyed:
                        if ctx.audio_manager: ctx.audio_manager.play_player_death()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(10.0, 0.7)

        # 4. Hazards vs Player
        if player.alive and not player.is_cloaked:
            h_hits = pygame.sprite.spritecollide(player, ctx.hazard_group, False)
            for h in h_hits:
                if hasattr(h, "gap_y"): # LaserGridFence
                    is_destroyed = player.take_damage(35.0 * dt)
                    ctx.trigger_shake(4.0, 0.1)
                    if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=4, color=COLOR_NEON_RED)
                    if ctx.mission_start_time > 0:
                        ctx.mission_damage_taken += 35.0 * dt
                    if is_destroyed:
                        if ctx.audio_manager: ctx.audio_manager.play_player_death()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(10.0, 0.7)


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
