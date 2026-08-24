"""
================================================================================
                  DRONE HUNTER 2D - GAMEPLAY CONTROLLER
================================================================================
Coordinates high-level gameplay session lifecycle, stage/mission transitions,
shop upgrades, weapon loadouts, and real-time combat simulation updates.
"""

import math
import random
import pygame
from typing import Optional, Dict, Any, List

from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
)
from src.data.game_data import (
    SECTORS, UPGRADES, WEAPON_UPGRADES, WEAPON_UNLOCK_COSTS
)
from src.core.game_state import (
    STATE_PLAYING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED,
    STATE_GAME_OVER, STATE_VICTORY, STATE_LEVEL_CLEAR
)
from src.data.mission_data import get_mission_data
from src.entities.player import Player
from src.entities.bullet import ClusterTorpedo, HomingMissile
from src.entities.hazard import GravityAnomaly
from src.systems.spawn_system import WaveManager


class GameplayController:
    """Orchestrates mission lifecycle, combat simulation, and upgrade progression."""

    def __init__(self, progression_system=None):
        self.progression = progression_system
        self.pending_mission_id: str = "S1_M1"
        self._current_objective_text: Optional[str] = None

    @property
    def current_objective_text(self) -> Optional[str]:
        return self._current_objective_text

    def start_mission(self, mission_id: Optional[str], context, progression,
                      particle_manager, camera, encounter_system, combat_director,
                      boss_system, objective_system, mission_system, background=None):
        """Prepares and launches a Phase 5/6 tactical mission."""
        if not mission_id:
            mission_id = getattr(mission_system, "active_mission_id", None) or self.pending_mission_id or "S1_M1"
        self.pending_mission_id = mission_id

        ctx = context
        ctx.state = STATE_PLAYING
        ctx.player_group.empty()
        ctx.target_group.empty()
        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.obstacle_group.empty()
        ctx.hazard_group.empty()
        ctx.powerup_group.empty()

        if particle_manager:
            particle_manager.particles.empty()
            particle_manager.floating_texts.empty()

        ctx.combo_count = 1
        ctx.combo_timer = 0.0
        ctx.damage_flash_timer = 0.0
        ctx.shake_timer = 0.0
        ctx.level_score = 0
        ctx.mission_damage_taken = 0.0
        ctx.mission_start_time = pygame.time.get_ticks() / 1000.0
        ctx.mission_elapsed_time = 0.0

        # Resolve sector and stage from mission_id
        m_data = get_mission_data(mission_id) if mission_id else None
        if m_data:
            sec_num = m_data.get("sector_id", 1)
            m_num = m_data.get("mission_number", 1)
            ctx.current_sector_idx = max(0, min(4, sec_num - 1))
            ctx.current_sub_level = m_num
            ctx.missions["current_sector"] = sec_num
            ctx.missions["current_mission"] = m_num
        else:
            try:
                digits = [int(c) for c in str(mission_id) if c.isdigit()]
                sec_num = digits[0] if len(digits) > 0 else 1
                m_num = digits[1] if len(digits) > 1 else 1
                ctx.current_sector_idx = max(0, min(4, sec_num - 1))
                ctx.current_sub_level = m_num
                ctx.missions["current_sector"] = sec_num
                ctx.missions["current_mission"] = m_num
            except Exception:
                ctx.current_sector_idx = 0
                ctx.current_sub_level = 1

        if background is not None:
            background.set_sector(ctx.current_sector_idx)
            if hasattr(background, "set_stage"):
                background.set_stage(ctx.current_sub_level)

        p = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        selected_skin = getattr(ctx, "selected_skin_override", None)
        if selected_skin is None:
            selected_skin = getattr(ctx, "selected_skin", 0)

        selected_drone = getattr(ctx, "selected_drone_override", None)
        if selected_drone is None:
            selected_drone = getattr(ctx, "selected_drone", "striker")

        p.set_drone_class(selected_drone)
        p.set_visual_skin(selected_skin)
        p.apply_shop_upgrades(ctx.upgrade_levels)
        if progression:
            progression.apply_to_player(ctx, p)
        p.health = p.max_health
        p.energy = p.max_energy
        ctx.player = p
        ctx.player_group.add(p)

        if camera:
            camera.center_x = float(p.pos.x)
            camera.center_y = float(p.pos.y)

        if encounter_system:
            encounter_system.reset()
        if combat_director:
            combat_director.reset()
        if mission_system:
            mission_system.start_mission(ctx, mission_id, combat_director, boss_system, objective_system)

    def reset_game(self, context, progression, particle_manager, camera,
                   spawner=None, encounter_system=None, combat_director=None, background=None):
        """Initializes or resets player, spawner, and stage wave tracking."""
        ctx = context
        ctx.level_score = 0
        ctx.combo_count = 1
        ctx.combo_timer = 0.0
        ctx.obstacle_timer = 0.0
        ctx.hazard_timer = 0.0
        ctx.slowmo_timer = 0.0
        ctx.time_scale = 1.0

        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.target_group.empty()
        ctx.obstacle_group.empty()
        ctx.hazard_group.empty()
        ctx.powerup_group.empty()

        if particle_manager:
            particle_manager.particles.empty()
            particle_manager.floating_texts.empty()

        ctx.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        selected_skin = getattr(ctx, "selected_skin_override", None)
        if selected_skin is None:
            selected_skin = getattr(ctx, "selected_skin", 0)

        selected_drone = getattr(ctx, "selected_drone_override", None)
        if selected_drone is None:
            selected_drone = getattr(ctx, "selected_drone", "striker")

        ctx.player.set_drone_class(selected_drone)
        ctx.player.set_visual_skin(selected_skin)
        ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
        ctx.player.apply_weapon_upgrades(ctx.weapon_upgrade_levels)
        if progression:
            progression.apply_to_player(ctx, ctx.player)
        ctx.player_group.add(ctx.player)

        if camera:
            camera.center_x = float(ctx.player.pos.x)
            camera.center_y = float(ctx.player.pos.y)

        target_score = 1000
        if progression:
            target_score = progression.get_current_stage_target_score(
                ctx.current_sector_idx, ctx.current_sub_level
            )
        is_boss_stage = (ctx.current_sub_level == 3)
        ctx.wave_manager = WaveManager(target_score, is_boss_stage=is_boss_stage)

        if spawner is not None:
            spawner.reset_for_stage(ctx.current_sector_idx * 3 + ctx.current_sub_level, ctx.current_sector_idx)
        if encounter_system is not None:
            encounter_system.reset()
        if combat_director is not None:
            combat_director.reset()
        if background is not None:
            background.set_sector(ctx.current_sector_idx)

        # Sector 1 Stage 1 dev director start
        if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1 and combat_director is not None:
            combat_director.start()

        ctx.state = STATE_PLAYING

    def start_stage(self, sector_idx: Optional[int], stage_idx: Optional[int],
                    context, progression, particle_manager, camera,
                    spawner=None, encounter_system=None, combat_director=None, background=None):
        """Prepares and launches a gameplay stage."""
        if sector_idx is not None: context.current_sector_idx = sector_idx
        if stage_idx is not None: context.current_sub_level = stage_idx

        self.reset_game(context, progression, particle_manager, camera,
                        spawner, encounter_system, combat_director, background)

    def start_next_stage(self, context, progression, save_callback, start_stage_callback):
        """Advances to next stage or triggers Campaign Victory."""
        ctx = context
        next_sec, next_stg, is_victory = progression.unlock_next_stage(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        if save_callback:
            save_callback()

        if is_victory:
            ctx.state = STATE_VICTORY
        else:
            if start_stage_callback:
                start_stage_callback(next_sec, next_stg)

    def start_new_game_plus(self, context, save_callback, start_mission_callback):
        """Increments NG+ count, applies difficulty multipliers, and launches S1_M1."""
        ctx = context
        ctx.new_game_plus_count += 1
        ctx.update_ng_plus_multipliers()
        ctx.campaign_completed = True
        ctx.missions["completed"] = []
        ctx.sector_progress["completed"] = []
        ctx.sector_progress["unlocked"] = [1]
        ctx.missions["current_sector"] = 1
        ctx.missions["current_mission"] = 1
        ctx.bosses_defeated = []
        if save_callback:
            save_callback()
        self.pending_mission_id = "S1_M1"
        if start_mission_callback:
            start_mission_callback("S1_M1")

    def get_next_mission_id(self, mission_system) -> Optional[str]:
        """Determines the next mission ID in campaign sequence."""
        current_id = getattr(mission_system, "active_mission_id", None) or self.pending_mission_id or "S1_M1"
        try:
            sec_num = int(current_id[1])
            m_num = int(current_id[4])
            if m_num < 5:
                return f"S{sec_num}_M{m_num + 1}"
            elif sec_num < 5:
                return f"S{sec_num + 1}_M1"
            else:
                return None
        except Exception:
            return "S1_M2"

    def buy_upgrade(self, upgrade_id: str, context, progression, audio_manager=None, save_callback=None) -> bool:
        ctx = context
        if upgrade_id in ("hull", "energy", "weapon", "mobility"):
            if progression and progression.purchase_upgrade(ctx, upgrade_id):
                if audio_manager: audio_manager.play_buy()
                if save_callback: save_callback()
                if ctx.player:
                    ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                    progression.apply_to_player(ctx, ctx.player)
                return True
            return False

        if upgrade_id not in UPGRADES:
            return False
        info = UPGRADES[upgrade_id]
        cur_lvl = ctx.upgrade_levels.get(upgrade_id, 0)
        cost = int(info["base_cost"] * (info["cost_mult"] ** cur_lvl))
        if cur_lvl < info["max_lvl"] and ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.upgrade_levels[upgrade_id] = cur_lvl + 1
            if audio_manager: audio_manager.play_buy()
            if save_callback: save_callback()
            if ctx.player:
                ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                if progression: progression.apply_to_player(ctx, ctx.player)
            return True
        return False

    def equip_weapon(self, slot_index: int, weapon_id: str, context, save_callback=None) -> bool:
        ctx = context
        if not ctx.player or weapon_id not in ctx.unlocked_weapons:
            return False
        weapons = ctx.player.available_weapons
        if slot_index < 0 or slot_index >= len(weapons):
            return False
        weapons[slot_index] = weapon_id
        if weapon_id not in ctx.player.weapon_cooldowns:
            ctx.player.weapon_cooldowns[weapon_id] = 0.0
        if ctx.player.active_weapon not in weapons:
            ctx.player.active_weapon = weapons[0]
            ctx.player.current_weapon_idx = 0
        if save_callback: save_callback()
        return True

    def buy_weapon_upgrade(self, weapon_id: str, context, audio_manager=None, save_callback=None) -> bool:
        ctx = context
        if weapon_id not in WEAPON_UPGRADES:
            return False
        info = WEAPON_UPGRADES[weapon_id]
        cur_lvl = ctx.weapon_upgrade_levels.get(weapon_id, 0)
        cost = int(info["cost_base"] * (info["cost_mult"] ** cur_lvl))
        if cur_lvl < info["max_level"] and ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.weapon_upgrade_levels[weapon_id] = cur_lvl + 1
            if audio_manager: audio_manager.play_buy()
            if save_callback: save_callback()
            if ctx.player:
                ctx.player.apply_weapon_upgrades(ctx.weapon_upgrade_levels)
            return True
        return False

    def unlock_weapon(self, weapon_id: str, context, audio_manager=None, save_callback=None) -> bool:
        ctx = context
        if weapon_id in ctx.unlocked_weapons or weapon_id not in WEAPON_UNLOCK_COSTS:
            return False
        cost = WEAPON_UNLOCK_COSTS[weapon_id]
        if ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.unlocked_weapons.append(weapon_id)
            if audio_manager: audio_manager.play_buy()
            if save_callback: save_callback()
            if ctx.player and weapon_id not in ctx.player.available_weapons:
                ctx.player.available_weapons.append(weapon_id)
                ctx.player.weapon_cooldowns[weapon_id] = 0.0
            return True
        return False

    def update_gameplay(self, dt: float, context, input_manager, audio_manager,
                        particle_manager, combat_system, combat_director, mission_system,
                        boss_system, objective_system, spawner, encounter_system,
                        achievement_system, camera, save_callback, get_canvas_mouse_pos_func, game_ref):
        """Simulates real-time combat, entities, hazards, projectiles, and mission objectives."""
        ctx = context
        sec_info = SECTORS[ctx.current_sector_idx]
        prev_wave = ctx.current_wave
        ctx.current_wave = ctx.wave_manager.update_wave(ctx.level_score)
        if ctx.current_wave > prev_wave:
            ctx.wave_announcement_timer = 2.0
            ctx.last_wave = ctx.current_wave
        if ctx.wave_announcement_timer > 0:
            ctx.wave_announcement_timer = max(0.0, ctx.wave_announcement_timer - dt)

        particle_manager.spawn_weather(sec_info.get("weather", "clear"))
        particle_manager.update(dt)

        # 1. Input Polling & Player Update
        canvas_mx, canvas_my = get_canvas_mouse_pos_func()
        world_mx, world_my = camera.screen_to_world(canvas_mx, canvas_my)
        input_state = input_manager.poll_input(
            player_pos=(ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (200, 360),
            get_canvas_mouse_pos_func=get_canvas_mouse_pos_func,
            world_mouse_pos=(world_mx, world_my)
        )
        ctx.input_state = input_state

        keys = pygame.key.get_pressed()
        if ctx.player:
            if ctx.player.alive:
                ctx.player.handle_input(keys, dt, mouse_pos=(world_mx, world_my), input_state=input_state)

                if ctx.player.is_accelerating or ctx.player.velocity.length_squared() > 10000.0:
                    cos_a = math.cos(ctx.player.aim_angle)
                    sin_a = math.sin(ctx.player.aim_angle)
                    rear_x = ctx.player.pos.x - cos_a * 24.0
                    rear_y = ctx.player.pos.y - sin_a * 24.0
                    particle_manager.spawn_drone_trail((rear_x, rear_y))

                wm_bullets = ctx.player.update(dt, targets_group=ctx.target_group)
                for wb in wm_bullets: ctx.bullet_group.add(wb)

                speed = ctx.player.velocity.length()
                speed_ratio = speed / max(1.0, ctx.player.max_speed)
                audio_manager.update_engine_sound(speed_ratio, ctx.player.is_accelerating)

                mouse_pressed = pygame.mouse.get_pressed()
                is_shooting = mouse_pressed[0] or input_state.get("fire_primary", False) or (keys[pygame.K_SPACE] if isinstance(keys, (list, tuple, dict)) or hasattr(keys, '__getitem__') else False)

                target_pos = (world_mx, world_my)
                if input_state.get("aim_angle") is not None:
                    aim_ang = input_state["aim_angle"]
                    target_pos = (ctx.player.pos.x + math.cos(aim_ang) * 1000.0, ctx.player.pos.y + math.sin(aim_ang) * 1000.0)

                if is_shooting and ctx.player.can_shoot():
                    fired_bullets = ctx.player.shoot(target_pos, level=ctx.current_sub_level, targets_group=ctx.target_group, particle_manager=particle_manager)
                    for b in fired_bullets: ctx.bullet_group.add(b)
                    if fired_bullets and ctx.player.active_weapon != "beam":
                        audio_manager.play_weapon(ctx.player.active_weapon)
                        input_manager.trigger_rumble(0.12, 0.25, 60)
                        if ctx.player.active_weapon in ("rail", "plasma", "barrage"):
                            ctx.trigger_shake(2.5, 0.10)
                        elif ctx.player.active_weapon in ("missile", "scatter"):
                            ctx.trigger_shake(1.8, 0.08)
                        else:
                            ctx.trigger_shake(1.2, 0.06)

                if getattr(ctx.player, "active_beam", None) and ctx.player.active_beam.alive():
                    audio_manager.start_beam_sound()
                else:
                    audio_manager.stop_beam_sound()

                camera.update(
                    (ctx.player.pos.x, ctx.player.pos.y),
                    dt,
                    shake_intensity=ctx.screen_shake_intensity,
                    shake_time=ctx.screen_shake_time
                )
            else:
                audio_manager.stop_engine_sound()
                ctx.player.update(dt, targets_group=ctx.target_group)
                camera.update((ctx.player.pos.x, ctx.player.pos.y), dt)

        # 2. Mission & Director Update
        if mission_system.active_mission_id is not None:
            combat_director.update(dt, ctx)
            mission_done = mission_system.update(dt, ctx, combat_director, boss_system, objective_system)
            if mission_done:
                if mission_system.is_mission_success:
                    ctx.mission_elapsed_time = pygame.time.get_ticks() / 1000.0 - ctx.mission_start_time
                    if getattr(ctx, "campaign_completed", False) and mission_system.active_mission_id == "S5_M5":
                        ctx.state = STATE_VICTORY
                        audio_manager.play_victory()
                    else:
                        ctx.state = STATE_MISSION_COMPLETE
                        audio_manager.play_mission_complete()
                    achievement_system.check_mission_complete(ctx, game_ref)
                    achievement_system.check_all(ctx, game_ref)
                else:
                    ctx.state = STATE_MISSION_FAILED
                    audio_manager.play_game_over()
            if ctx.state in (STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_VICTORY):
                return

            m_data = getattr(mission_system, "active_mission_data", None)
            if m_data:
                obj = m_data.get("objective", "")
                living_enemies = [e for e in ctx.target_group if getattr(e, "alive", False) and not getattr(e, "is_obstacle", False)]
                if obj == "survive":
                    remaining = max(0, int(getattr(mission_system, "survive_timer", 0.0)))
                    self._current_objective_text = f"SURVIVE: {remaining}s"
                elif obj == "destroy_all":
                    total = m_data.get("enemy_count", len(living_enemies))
                    remaining = len(living_enemies)
                    self._current_objective_text = f"DESTROY ALL: {total - remaining}/{total}"
                elif obj == "complete_encounters":
                    total = len(m_data.get("encounter_sequence", []))
                    completed = getattr(combat_director, "completed_encounters", 0)
                    self._current_objective_text = f"ENCOUNTERS: {completed}/{total}"
                else:
                    self._current_objective_text = None
            else:
                self._current_objective_text = None
        else:
            if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
                if combat_director.state == "idle":
                    combat_director.start()
                combat_director.update(dt, ctx)
                if not combat_director.is_suppressing_spawner:
                    spawner.update(dt, ctx)
            else:
                spawner.update(dt, ctx)

        # 3. Enemies & Projectiles Simulation
        effective_enemy_dt = dt * ctx.time_scale

        if ctx.screen_shake_time > 0.0:
            ctx.screen_shake_time = max(0.0, ctx.screen_shake_time - dt)
            if ctx.screen_shake_time <= 0.0:
                ctx.screen_shake_intensity = 0.0
        if ctx.hit_stop_timer > 0.0:
            ctx.hit_stop_timer = max(0.0, ctx.hit_stop_timer - dt)

        prev_boss_phase = {}
        for target in list(ctx.target_group):
            if getattr(target, "is_boss", False):
                prev_boss_phase[id(target)] = target.current_phase_idx
            p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (200, 360)
            p_vel = (ctx.player.velocity.x, ctx.player.velocity.y) if ctx.player else (0, 0)
            new_e_bullets = target.update(effective_enemy_dt, player_pos=p_pos, player_vel=p_vel, player_obj=ctx.player, target_group=ctx.target_group)
            for eb in new_e_bullets: ctx.enemy_bullet_group.add(eb)

        for target in list(ctx.target_group):
            if getattr(target, "is_boss", False) and id(target) in prev_boss_phase:
                if target.current_phase_idx != prev_boss_phase[id(target)]:
                    particle_manager.spawn_boss_phase_transition(target.rect.center, target.current_phase_idx)

        for h in list(ctx.hazard_group):
            if isinstance(h, GravityAnomaly): h.update(effective_enemy_dt, player=ctx.player)
            else: h.update(effective_enemy_dt)

        ctx.obstacle_group.update(effective_enemy_dt)
        ctx.enemy_bullet_group.update(effective_enemy_dt)
        ctx.powerup_group.update(dt)

        for b in list(ctx.bullet_group):
            if isinstance(b, ClusterTorpedo):
                bomblets = b.update(dt)
                for bomb in bomblets: ctx.bullet_group.add(bomb)
            elif isinstance(b, HomingMissile):
                b.update(dt, target_group=ctx.target_group)
                if particle_manager and random.random() < 0.5:
                    particle_manager.spawn_spark(b.rect.center, count=2, color=(255, 160, 40))
            elif hasattr(b, "update") and "target_group" in b.update.__code__.co_varnames:
                b.update(dt, target_group=ctx.target_group)
            else:
                b.update(dt)

        # 4. Combat & Collision Resolution
        effective_combat_dt = dt
        if ctx.hit_stop_timer > 0.0:
            effective_combat_dt = 0.0
            ctx.hit_stop_timer = max(0.0, ctx.hit_stop_timer - dt)
        combat_system.update_combat(effective_combat_dt)

        # Check Player Death transition
        if ctx.player and getattr(ctx.player, "is_destroyed", False) and ctx.player.destruction_timer <= 0.0 and ctx.state == STATE_PLAYING:
            if mission_system.active_mission_id is not None:
                mission_system.trigger_failure(objective_system=objective_system)
                ctx.state = STATE_MISSION_FAILED
            else:
                ctx.state = STATE_GAME_OVER
            if save_callback: save_callback()
            if ctx.state in (STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_GAME_OVER):
                return

        # 5. Legacy Stage Completion
        if mission_system.active_mission_id is None:
            living_enemies = [e for e in ctx.target_group if getattr(e, "alive", False) and not getattr(e, "is_obstacle", False)]
            stage_complete = ctx.wave_manager.is_stage_complete(ctx.level_score, targets_group=ctx.target_group)
            director_finished = (combat_director.state == "complete" and len(living_enemies) == 0 and ctx.level_score >= 1200)

            boss_just_died = getattr(ctx, "boss_defeat_timer", 0.0) > 0.0
            if boss_just_died:
                ctx.boss_defeat_timer = max(0.0, ctx.boss_defeat_timer - dt)
            if getattr(ctx, "boss_rating_timer", 0.0) > 0.0:
                ctx.boss_rating_timer = max(0.0, ctx.boss_rating_timer - dt)

            if (stage_complete or director_finished) and not boss_just_died:
                ctx.state = STATE_LEVEL_CLEAR
                audio_manager.play_mission_complete()
                if save_callback: save_callback()

        achievement_system.check_all(ctx, game_ref)
