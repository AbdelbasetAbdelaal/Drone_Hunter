"""
===============================================================================
                    DRONE HUNTER 2D - COMBAT & COLLISION PIPELINE
===============================================================================
Centralized combat engine resolving 2D sprite collisions, damage formulas,
chain lightning reactions, cluster bomblets, shield hit absorption, and drops.
Optimized for high-density scalability with spatial broad-phase filtering,
squared-distance math, and zero-allocation nearest neighbor selection.
"""

import math
import random
import pygame
from typing import List, Optional
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

SHIELD_RADIUS_SQ = 160.0 * 160.0  # Exactly 160.0 radius squared (25600.0)


class CombatSystem:
    def __init__(self, context):
        self.context = context
        self.feedback = CombatFeedbackSystem(context)

    def execute_emp_blast(self):
        """Executes player EMP Shockwave, clearing all screen bullets and damaging enemies."""
        ctx = self.context
        player = ctx.player
        if player and player.trigger_emp():
            if ctx.audio_manager: ctx.audio_manager.play_emp()
            ctx.trigger_shake(12.0, 0.45)
            if ctx.particle_manager: ctx.particle_manager.spawn_emp_shockwave(player.pos)
            from src.entities.bullet import EMPShockwave
            ctx.bullet_group.add(EMPShockwave(player.rect.center, max_radius=1200.0, lifetime=1.5, owner="player"))

    def update_combat(self, dt: float):
        ctx = self.context
        player = ctx.player
        if not player or not player.alive:
            return

        # Snapshot active sprite collections once per frame
        bullets = ctx.bullet_group.sprites()
        targets = ctx.target_group.sprites()
        obstacles = ctx.obstacle_group.sprites()
        enemy_bullets = ctx.enemy_bullet_group.sprites()

        # 1. Player Bullets vs Environmental Obstacles
        for b in bullets:
            if not b.alive():
                continue
            hit_obs = pygame.sprite.spritecollide(b, ctx.obstacle_group, False, pygame.sprite.collide_circle)
            for obs in hit_obs:
                if getattr(b, "is_emp_projectile", False):
                    b.detonate(ctx)
                else:
                    b.kill()
                if obs.take_damage(getattr(b, "damage", 35)):
                    obs.kill()
                    if ctx.audio_manager: ctx.audio_manager.play_mine_explosion()
                    ctx.trigger_shake(9.0, 0.3)
                    if ctx.particle_manager: ctx.particle_manager.spawn_explosion(obs.rect.center, count=35, color=(239, 68, 68))

        # 2. Player Bullets vs Hostile Enemies
        # Build shield-drone positions list once per frame (O(shield_drones) checks)
        shield_drones = [
            (t, t.pos.x, t.pos.y) for t in targets
            if getattr(t, "enemy_type", "") == TARGET_TYPE_SHIELD_DRONE and getattr(t, "alive", False)
        ]

        for b in bullets:
            if not b.alive():
                continue

            if getattr(b, "is_continuous", False):
                # 1. Raycast against obstacles to find beam length
                start_x, start_y = b.muzzle_pos.x, b.muzzle_pos.y
                dx = math.cos(b.angle_rad)
                dy = math.sin(b.angle_rad)
                max_len = 2000.0
                closest_hit = max_len

                # Broad-phase bounding box for full potential ray
                ray_end_x = start_x + dx * max_len
                ray_end_y = start_y + dy * max_len
                broad_min_x = min(start_x, ray_end_x) - 64.0
                broad_max_x = max(start_x, ray_end_x) + 64.0
                broad_min_y = min(start_y, ray_end_y) - 64.0
                broad_max_y = max(start_y, ray_end_y) + 64.0

                # Check obstacles with AABB filtering
                for obs in obstacles:
                    if not obs.alive():
                        continue
                    cx, cy = obs.pos.x, obs.pos.y
                    if not (broad_min_x <= cx <= broad_max_x and broad_min_y <= cy <= broad_max_y):
                        continue

                    r = obs.radius
                    fx = start_x - cx
                    fy = start_y - cy
                    a = dx * dx + dy * dy
                    b_coef = 2 * (fx * dx + fy * dy)
                    c = (fx * fx + fy * fy) - r * r
                    disc = b_coef * b_coef - 4 * a * c
                    if disc >= 0:
                        t = (-b_coef - math.sqrt(disc)) / (2 * a)
                        if 0 <= t < closest_hit:
                            closest_hit = t
                            if ctx.particle_manager and random.random() < 0.4:
                                hit_pt = (start_x + dx * t, start_y + dy * t)
                                ctx.particle_manager.spawn_spark(hit_pt, count=random.randint(1, 3), color=(255, 140, 0))

                b.length = closest_hit

                # Tighten beam bounding box to actual length
                actual_end_x = start_x + dx * b.length
                actual_end_y = start_y + dy * b.length
                beam_min_x = min(start_x, actual_end_x) - 48.0
                beam_max_x = max(start_x, actual_end_x) + 48.0
                beam_min_y = min(start_y, actual_end_y) - 48.0
                beam_max_y = max(start_y, actual_end_y) + 48.0

                # 2. Damage enemies along the beam with broad-phase & squared-distance
                base_beam_damage = b.damage_per_second * dt
                for target in targets:
                    if not getattr(target, "alive", False):
                        continue
                    cx, cy = target.pos.x, target.pos.y
                    if not (beam_min_x <= cx <= beam_max_x and beam_min_y <= cy <= beam_max_y):
                        continue

                    # Distance from point to line segment
                    fx = cx - start_x
                    fy = cy - start_y
                    dot = fx * dx + fy * dy
                    t = max(0.0, min(b.length, dot))
                    proj_x = start_x + t * dx
                    proj_y = start_y + t * dy
                    dist_sq = (cx - proj_x) ** 2 + (cy - proj_y) ** 2
                    hit_radius = target.radius + 8.0

                    if dist_sq <= hit_radius * hit_radius:
                        # Enemy is hit by continuous beam
                        target_dmg = base_beam_damage
                        is_shielded = False
                        for ally, ax, ay in shield_drones:
                            if ally != target and ((cx - ax) ** 2 + (cy - ay) ** 2) <= SHIELD_RADIUS_SQ:
                                is_shielded = True
                                break
                        if is_shielded:
                            target_dmg = max(1.0, base_beam_damage / 3.0)
                            if ctx.particle_manager and random.random() < 0.15:
                                ctx.particle_manager.spawn_shield_ripple(target.rect.center)

                        target.take_damage(target_dmg, source="beam")
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark((proj_x, proj_y), count=random.randint(1, 3), color=(56, 189, 248))
                            if random.random() < 0.35:
                                ctx.particle_manager.spawn_enemy_hit_sparks((proj_x, proj_y), getattr(target, "enemy_type", ""), 10)

                # 3. Disintegrate incoming enemy projectiles caught in the plasma beam
                for eb in enemy_bullets:
                    if not eb.alive():
                        continue
                    ecx, ecy = eb.pos.x, eb.pos.y
                    if not (beam_min_x <= ecx <= beam_max_x and beam_min_y <= ecy <= beam_max_y):
                        continue

                    efx = ecx - start_x
                    efy = ecy - start_y
                    edot = efx * dx + efy * dy
                    et = max(0.0, min(b.length, edot))
                    eproj_x = start_x + et * dx
                    eproj_y = start_y + et * dy
                    edist_sq = (ecx - eproj_x) ** 2 + (ecy - eproj_y) ** 2
                    ehit_r = eb.radius + 14.0
                    if edist_sq <= ehit_r * ehit_r:
                        eb.kill()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark((eproj_x, eproj_y), count=2, color=(56, 189, 248))
                continue

            elif getattr(b, "is_emp_shockwave", False):
                b_pos_x, b_pos_y = b.pos.x, b.pos.y
                hit_targets_set = getattr(b, "hit_targets", None)
                if hit_targets_set is None:
                    b.hit_targets = set()
                    hit_targets_set = b.hit_targets

                for target in targets:
                    if not getattr(target, "alive", False) or target in hit_targets_set:
                        continue
                    combined_r = target.radius + b.radius
                    if ((target.pos.x - b_pos_x) ** 2 + (target.pos.y - b_pos_y) ** 2) <= combined_r * combined_r:
                        hit_targets_set.add(target)
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
                for eb in enemy_bullets:
                    if not eb.alive():
                        continue
                    comb_eb_r = eb.radius + b.radius
                    if ((eb.pos.x - b_pos_x) ** 2 + (eb.pos.y - b_pos_y) ** 2) <= comb_eb_r * comb_eb_r:
                        eb.kill()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_spark(eb.rect.center, count=3, color=COLOR_CYAN)

                for obs in obstacles:
                    if not obs.alive() or obs in hit_targets_set:
                        continue
                    comb_obs_r = obs.radius + b.radius
                    if ((obs.pos.x - b_pos_x) ** 2 + (obs.pos.y - b_pos_y) ** 2) <= comb_obs_r * comb_obs_r:
                        hit_targets_set.add(obs)
                        if obs.take_damage(b.damage):
                            obs.kill()
                            if ctx.particle_manager: ctx.particle_manager.spawn_explosion(obs.rect.center, 30, (239, 68, 68))
                continue

            hits = pygame.sprite.spritecollide(b, ctx.target_group, False)
            for target in hits:
                if not getattr(target, "alive", False):
                    continue

                dmg = getattr(b, "damage", 25)

                # PERF: Fast squared distance shield protection check
                is_shielded = False
                tx, ty = target.pos.x, target.pos.y
                for ally, ax, ay in shield_drones:
                    if ally != target and ((tx - ax) ** 2 + (ty - ay) ** 2) <= SHIELD_RADIUS_SQ:
                        is_shielded = True
                        break
                if is_shielded:
                    dmg = max(4, int(dmg // 3))
                    if ctx.particle_manager: ctx.particle_manager.spawn_shield_ripple(target.rect.center)

                is_dead = target.take_damage(dmg, source="bullet")

                if getattr(b, "is_emp_projectile", False):
                    b.detonate(ctx)
                    continue

                # Tesla Arc Lightning Chain Reaction (O(N) 2-nearest selection)
                if isinstance(b, TeslaArcBeam):
                    b.chained_targets.add(target)
                    if ctx.audio_manager: ctx.audio_manager.play_tesla()

                    nearest_1 = None
                    nearest_2 = None
                    d1_sq = float('inf')
                    d2_sq = float('inf')

                    for cand in targets:
                        if cand in b.chained_targets or not getattr(cand, "alive", False):
                            continue
                        cand_dist_sq = (cand.pos.x - tx) ** 2 + (cand.pos.y - ty) ** 2
                        if cand_dist_sq < d1_sq:
                            nearest_2, d2_sq = nearest_1, d1_sq
                            nearest_1, d1_sq = cand, cand_dist_sq
                        elif cand_dist_sq < d2_sq:
                            nearest_2, d2_sq = cand, cand_dist_sq

                    for chained_enemy in (nearest_1, nearest_2):
                        if chained_enemy is None:
                            continue
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
                if not player.alive or player.is_invulnerable or player.is_cloaked:
                    continue

                dmg = getattr(eb, "damage", 16)
                diff_dmg_mult = ctx.difficulty_data.get("damage_mult", 1.0)
                scaled_dmg = dmg * diff_dmg_mult

                had_shield = player.shield_hits > 0
                is_destroyed = player.take_damage(scaled_dmg)
                player.damage_grace_timer = player.damage_grace_duration

                if had_shield:
                    if ctx.audio_manager: ctx.audio_manager.play_hit_shield()
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=8, color=COLOR_SHIELD)
                else:
                    ctx.trigger_shake(2.5, 0.12)
                    ctx.damage_flash_timer = 0.14
                    if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                    if ctx.particle_manager: ctx.particle_manager.spawn_explosion(player.rect.center, count=12, color=COLOR_CRIMSON)
                    if ctx.mission_start_time > 0:
                        ctx.mission_damage_taken += scaled_dmg

                if is_destroyed:
                    if ctx.audio_manager: ctx.audio_manager.play_player_death()
                    if ctx.particle_manager:
                        ctx.particle_manager.spawn_player_destruction(player.rect.center)
                    ctx.trigger_shake(8.0, 0.6)
                    break

        # 3B. Hostile Enemies vs Player Drone (Contact Damage with Cooldown)
        if player.alive and not player.is_invulnerable and not player.is_cloaked:
            c_hits = pygame.sprite.spritecollide(player, ctx.target_group, False)
            for enemy in c_hits:
                if not player.alive or player.is_invulnerable or player.is_cloaked:
                    break
                if getattr(enemy, "alive", True) and getattr(enemy, "contact_cooldown_timer", 0.0) <= 0.0:
                    c_dmg = getattr(enemy, "contact_damage", 15.0)
                    enemy.contact_cooldown_timer = 1.0

                    had_shield = player.shield_hits > 0
                    is_destroyed = player.take_damage(c_dmg)
                    player.damage_grace_timer = player.damage_grace_duration

                    if had_shield:
                        if ctx.audio_manager: ctx.audio_manager.play_hit_shield()
                        if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=8, color=COLOR_SHIELD)
                    else:
                        ctx.trigger_shake(2.5, 0.12)
                        ctx.damage_flash_timer = 0.14
                        if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                        if ctx.particle_manager: ctx.particle_manager.spawn_explosion(player.rect.center, count=12, color=COLOR_CRIMSON)
                        if ctx.mission_start_time > 0:
                            ctx.mission_damage_taken += c_dmg

                    if is_destroyed:
                        if ctx.audio_manager: ctx.audio_manager.play_player_death()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(8.0, 0.6)
                        break

        # 4. Hazards vs Player
        if player.alive and not player.is_invulnerable and not player.is_cloaked:
            h_hits = pygame.sprite.spritecollide(player, ctx.hazard_group, False)
            for h in h_hits:
                if hasattr(h, "gap_y"):
                    is_destroyed = player.take_damage(20.0 * dt)
                    ctx.trigger_shake(2.0, 0.08)
                    if ctx.audio_manager: ctx.audio_manager.play_player_hit()
                    if ctx.particle_manager: ctx.particle_manager.spawn_spark(player.rect.center, count=4, color=COLOR_NEON_RED)
                    if ctx.mission_start_time > 0:
                        ctx.mission_damage_taken += 20.0 * dt
                    if is_destroyed:
                        if ctx.audio_manager: ctx.audio_manager.play_player_death()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_player_destruction(player.rect.center)
                        ctx.trigger_shake(8.0, 0.6)
                        break

        # 5. Player vs Power-up Items
        if player.alive:
            p_hits = pygame.sprite.spritecollide(player, ctx.powerup_group, True)
            for p in p_hits:
                if ctx.audio_manager: ctx.audio_manager.play_powerup()
                pm = ctx.particle_manager
                if p.p_type == "battery":
                    player.health = min(player.max_health, player.health + 35.0)
                    player.energy = min(player.max_energy, player.energy + 25.0)
                    if pm: pm.spawn_floating_text(p.rect.center, "+HULL REPAIR", COLOR_EMERALD, 18)
                elif p.p_type == "overclock":
                    player.trigger_overclock(6.0)
                    if pm: pm.spawn_floating_text(p.rect.center, "OVERCLOCK!", COLOR_OVERCLOCK, 22)
                elif p.p_type == "shield":
                    player.activate_shield(3)
                    if pm: pm.spawn_floating_text(p.rect.center, "SHIELD CHARGED", COLOR_SHIELD, 20)
                elif p.p_type == "slowmo":
                    ctx.trigger_slowmo(5.0)
                    if pm: pm.spawn_floating_text(p.rect.center, "TIME DILATION", COLOR_SLOWMO, 20)
                elif p.p_type == "coin":
                    ctx.scrap += 50
                    if pm: pm.spawn_floating_text(p.rect.center, "+50 SCRAP", COLOR_COIN, 18)
                elif p.p_type == "wingman":
                    player.spawn_wingman()
                    if pm: pm.spawn_floating_text(p.rect.center, "+WINGMAN DRONE", COLOR_CYAN, 20)
                elif p.p_type == "weapon":
                    player.cycle_weapon()
                    if pm: pm.spawn_floating_text(p.rect.center, f"WPN: {player.active_weapon.upper()}", COLOR_GOLD, 22)
