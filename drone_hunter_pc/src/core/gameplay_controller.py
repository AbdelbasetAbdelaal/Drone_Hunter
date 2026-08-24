"""
================================================================================
                  DRONE HUNTER 2D - GAMEPLAY CONTROLLER
================================================================================
Coordinates high-level gameplay session lifecycle, stage/mission transitions,
shop upgrades, weapon loadouts, and real-time combat simulation updates.
Receives dependencies explicitly through GameplayContext without coupling to Game.
"""

import math
import random
import pygame
from typing import Optional, Dict, Any, List, Tuple

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
from src.core.gameplay_context import GameplayContext
from src.core.game_context import GameContext
from src.data.mission_data import get_mission_data


class GameplayController:
    """Orchestrates mission lifecycle, combat simulation, and upgrade progression."""

    def __init__(self, progression_system=None):
        self.progression = progression_system
        self.pending_mission_id: str = "S1_M1"
        self._current_objective_text: Optional[str] = None

    @property
    def current_objective_text(self) -> Optional[str]:
        return self._current_objective_text

    def _resolve_gameplay_context(self, context_or_gp_ctx: Any = None, **kwargs) -> GameplayContext:
        """Helper to accept either a GameplayContext instance or individual legacy parameters."""
        gp_ctx_kwarg = kwargs.get("gp_ctx")
        if isinstance(gp_ctx_kwarg, GameplayContext):
            return gp_ctx_kwarg
        if isinstance(context_or_gp_ctx, GameplayContext):
            return context_or_gp_ctx
        ctx = context_or_gp_ctx if context_or_gp_ctx is not None else kwargs.get("context")
        if isinstance(ctx, GameplayContext):
            return ctx
        return GameplayContext(
            context=ctx,
            progression=kwargs.get("progression", self.progression),
            particle_manager=kwargs.get("particle_manager"),
            camera=kwargs.get("camera"),
            spawner=kwargs.get("spawner"),
            encounter_system=kwargs.get("encounter_system"),
            combat_director=kwargs.get("combat_director"),
            mission_system=kwargs.get("mission_system"),
            boss_system=kwargs.get("boss_system"),
            objective_system=kwargs.get("objective_system"),
            combat_system=kwargs.get("combat_system"),
            background=kwargs.get("background"),
            audio_manager=kwargs.get("audio_manager"),
            input_manager=kwargs.get("input_manager"),
            achievement_system=kwargs.get("achievement_system"),
            save_callback=kwargs.get("save_callback"),
            get_canvas_mouse_pos_func=kwargs.get("get_canvas_mouse_pos_func"),
            start_mission_callback=kwargs.get("start_mission_callback"),
            start_stage_callback=kwargs.get("start_stage_callback"),
        )

    def start_mission(self, mission_id: Optional[str] = None, gp_ctx_or_context: Optional[Any] = None,
                      gp_ctx: Optional[Any] = None, progression=None, particle_manager=None, camera=None,
                      encounter_system=None, combat_director=None, boss_system=None,
                      objective_system=None, mission_system=None, background=None, **kwargs):
        """Prepares and launches a Phase 5/6 tactical mission."""
        target_ctx = gp_ctx if gp_ctx is not None else gp_ctx_or_context
        if isinstance(mission_id, GameplayContext):
            resolved_ctx = mission_id
            mission_id = None
        elif isinstance(target_ctx, GameplayContext):
            resolved_ctx = target_ctx
        else:
            resolved_ctx = self._resolve_gameplay_context(
                target_ctx, progression=progression, particle_manager=particle_manager,
                camera=camera, encounter_system=encounter_system, combat_director=combat_director,
                boss_system=boss_system, objective_system=objective_system,
                mission_system=mission_system, background=background, **kwargs
            )

        ctx = resolved_ctx.context
        mission_sys = resolved_ctx.mission_system
        prog = resolved_ctx.progression or self.progression
        pm = resolved_ctx.particle_manager
        cam = resolved_ctx.camera
        enc = resolved_ctx.encounter_system
        cd = resolved_ctx.combat_director
        bs = resolved_ctx.boss_system
        objs = resolved_ctx.objective_system
        bg = resolved_ctx.background

        if not mission_id:
            mission_id = getattr(mission_sys, "active_mission_id", None) or self.pending_mission_id or "S1_M1"
        self.pending_mission_id = mission_id

        ctx.state = STATE_PLAYING
        ctx.player_group.empty()
        ctx.target_group.empty()
        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.obstacle_group.empty()
        ctx.hazard_group.empty()
        ctx.powerup_group.empty()

        if pm:
            pm.particles.empty()
            pm.floating_texts.empty()

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
            ctx.campaign_state.set_current_sector_and_stage(sec_num - 1, m_num)
        else:
            try:
                digits = [int(c) for c in str(mission_id) if c.isdigit()]
                sec_num = digits[0] if len(digits) > 0 else 1
                m_num = digits[1] if len(digits) > 1 else 1
                ctx.campaign_state.set_current_sector_and_stage(sec_num - 1, m_num)
            except Exception:
                ctx.campaign_state.set_current_sector_and_stage(0, 1)

        if bg is not None:
            bg.set_sector(ctx.current_sector_idx)
            if hasattr(bg, "set_stage"):
                bg.set_stage(ctx.current_sub_level)

        from src.entities.player import Player
        from src.systems.spawn_system import WaveManager

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
        if prog:
            prog.apply_to_player(ctx, p)
        p.health = p.max_health
        p.energy = p.max_energy
        ctx.player = p
        ctx.player_group.add(p)

        target_score = 1000
        if prog:
            target_score = prog.get_current_stage_target_score(
                ctx.current_sector_idx, ctx.current_sub_level
            )
        is_boss_stage = (ctx.current_sub_level == 3)
        ctx.wave_manager = WaveManager(target_score, is_boss_stage=is_boss_stage)

        if cam:
            cam.center_x = float(p.pos.x)
            cam.center_y = float(p.pos.y)

        if enc:
            enc.reset()
        if cd:
            cd.reset()
        if mission_sys:
            mission_sys.start_mission(ctx, mission_id, cd, bs, objs)

    def reset_game(self, gp_ctx_or_context=None, progression=None, particle_manager=None,
                   camera=None, spawner=None, encounter_system=None, combat_director=None,
                   background=None, **kwargs):
        """Initializes or resets player, spawner, and stage wave tracking."""
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, progression=progression, particle_manager=particle_manager,
                camera=camera, spawner=spawner, encounter_system=encounter_system,
                combat_director=combat_director, background=background, **kwargs
            )

        ctx = resolved_ctx.context
        prog = resolved_ctx.progression or self.progression
        pm = resolved_ctx.particle_manager
        cam = resolved_ctx.camera
        spw = resolved_ctx.spawner
        enc = resolved_ctx.encounter_system
        cd = resolved_ctx.combat_director
        bg = resolved_ctx.background

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

        if pm:
            pm.particles.empty()
            pm.floating_texts.empty()

        from src.entities.player import Player
        from src.systems.spawn_system import WaveManager

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
        if prog:
            prog.apply_to_player(ctx, ctx.player)
        ctx.player_group.add(ctx.player)

        if cam:
            cam.center_x = float(ctx.player.pos.x)
            cam.center_y = float(ctx.player.pos.y)

        target_score = 1000
        if prog:
            target_score = prog.get_current_stage_target_score(
                ctx.current_sector_idx, ctx.current_sub_level
            )
        is_boss_stage = (ctx.current_sub_level == 3)
        ctx.wave_manager = WaveManager(target_score, is_boss_stage=is_boss_stage)

        if spw is not None:
            spw.reset_for_stage(ctx.current_sector_idx * 3 + ctx.current_sub_level, ctx.current_sector_idx)
        if enc is not None:
            enc.reset()
        if cd is not None:
            cd.reset()
        if bg is not None:
            bg.set_sector(ctx.current_sector_idx)
        mission_sys = resolved_ctx.mission_system
        if mission_sys is not None:
            mission_sys.active_mission_id = None
            mission_sys.state = "idle"

    def start_stage(self, sector_idx: Optional[int] = None, stage_idx: Optional[int] = None,
                    gp_ctx_or_context=None, progression=None, particle_manager=None, camera=None,
                    spawner=None, encounter_system=None, combat_director=None, background=None, **kwargs):
        """Prepares and launches a gameplay stage."""
        if isinstance(sector_idx, GameplayContext):
            resolved_ctx = sector_idx
            sector_idx = None
            stage_idx = None
        elif isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, progression=progression, particle_manager=particle_manager,
                camera=camera, spawner=spawner, encounter_system=encounter_system,
                combat_director=combat_director, background=background, **kwargs
            )
        if sector_idx is not None: resolved_ctx.context.current_sector_idx = sector_idx
        if stage_idx is not None: resolved_ctx.context.current_sub_level = stage_idx

        self.reset_game(resolved_ctx)

    def start_next_stage(self, gp_ctx_or_context=None, progression=None, save_callback=None,
                         start_stage_callback=None, **kwargs):
        """Advances to next stage or triggers Campaign Victory."""
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, progression=progression, save_callback=save_callback,
                start_stage_callback=start_stage_callback, **kwargs
            )
        ctx = resolved_ctx.context
        prog = resolved_ctx.progression or self.progression
        save_cb = resolved_ctx.save_callback
        stage_cb = resolved_ctx.start_stage_callback

        next_sec, next_stg, is_victory = prog.unlock_next_stage(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        if save_cb:
            save_cb()

        if is_victory:
            ctx.state = STATE_VICTORY
        else:
            if stage_cb:
                stage_cb(next_sec, next_stg)

    def start_new_game_plus(self, gp_ctx_or_context=None, save_callback=None,
                           start_mission_callback=None, **kwargs):
        """Increments NG+ count, applies difficulty multipliers, and launches S1_M1."""
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, save_callback=save_callback,
                start_mission_callback=start_mission_callback, **kwargs
            )
        ctx = resolved_ctx.context
        save_cb = resolved_ctx.save_callback
        start_cb = resolved_ctx.start_mission_callback

        ctx.campaign_state.start_new_game_plus()
        ctx.update_ng_plus_multipliers()
        if save_cb:
            save_cb()
        self.pending_mission_id = "S1_M1"
        if start_cb:
            start_cb("S1_M1")

    def get_next_mission_id(self, mission_system=None) -> Optional[str]:
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

    def buy_upgrade(self, upgrade_id: str, gp_ctx_or_context=None, progression=None,
                    audio_manager=None, save_callback=None, **kwargs) -> bool:
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, progression=progression, audio_manager=audio_manager,
                save_callback=save_callback, **kwargs
            )
        ctx = resolved_ctx.context
        prog = resolved_ctx.progression or self.progression
        am = resolved_ctx.audio_manager
        save_cb = resolved_ctx.save_callback

        if upgrade_id in ("hull", "energy", "weapon", "mobility"):
            if prog and prog.purchase_upgrade(ctx, upgrade_id):
                if am: am.play_buy()
                if save_cb: save_cb()
                if ctx.player:
                    ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                    prog.apply_to_player(ctx, ctx.player)
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
            if am: am.play_buy()
            if save_cb: save_cb()
            if ctx.player:
                ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                if prog: prog.apply_to_player(ctx, ctx.player)
            return True
        return False

    def equip_weapon(self, slot_index: int, weapon_id: str, gp_ctx_or_context=None,
                     save_callback=None, **kwargs) -> bool:
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(gp_ctx_or_context, save_callback=save_callback, **kwargs)
        ctx = resolved_ctx.context
        save_cb = resolved_ctx.save_callback

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
        if save_cb: save_cb()
        return True

    def buy_weapon_upgrade(self, weapon_id: str, gp_ctx_or_context=None,
                           audio_manager=None, save_callback=None, **kwargs) -> bool:
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, audio_manager=audio_manager, save_callback=save_callback, **kwargs
            )
        ctx = resolved_ctx.context
        am = resolved_ctx.audio_manager
        save_cb = resolved_ctx.save_callback

        if weapon_id not in WEAPON_UPGRADES:
            return False
        info = WEAPON_UPGRADES[weapon_id]
        cur_lvl = ctx.weapon_upgrade_levels.get(weapon_id, 0)
        cost = int(info["cost_base"] * (info["cost_mult"] ** cur_lvl))
        if cur_lvl < info["max_level"] and ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.weapon_upgrade_levels[weapon_id] = cur_lvl + 1
            if am: am.play_buy()
            if save_cb: save_cb()
            if ctx.player:
                ctx.player.apply_weapon_upgrades(ctx.weapon_upgrade_levels)
            return True
        return False

    def unlock_weapon(self, weapon_id: str, gp_ctx_or_context=None,
                      audio_manager=None, save_callback=None, **kwargs) -> bool:
        if isinstance(gp_ctx_or_context, GameplayContext):
            resolved_ctx = gp_ctx_or_context
        else:
            resolved_ctx = self._resolve_gameplay_context(
                gp_ctx_or_context, audio_manager=audio_manager, save_callback=save_callback, **kwargs
            )
        ctx = resolved_ctx.context
        am = resolved_ctx.audio_manager
        save_cb = resolved_ctx.save_callback

        if weapon_id in ctx.unlocked_weapons or weapon_id not in WEAPON_UNLOCK_COSTS:
            return False
        cost = WEAPON_UNLOCK_COSTS[weapon_id]
        if ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.unlocked_weapons.append(weapon_id)
            if am: am.play_buy()
            if save_cb: save_cb()
            if ctx.player and weapon_id not in ctx.player.available_weapons:
                ctx.player.available_weapons.append(weapon_id)
                ctx.player.weapon_cooldowns[weapon_id] = 0.0
            return True
        return False

    def update_gameplay(self, dt: float = 0.016, gp_ctx: Any = None, *args, **kwargs):
        """Simulates real-time combat, entities, hazards, projectiles, and mission objectives.
        Accepts GameplayContext cleanly or handles legacy arguments gracefully."""
        if gp_ctx is None:
            gp_ctx = kwargs.get("gp_ctx_or_context") or kwargs.get("context")
        if isinstance(dt, GameplayContext):
            resolved_ctx = dt
            dt = 0.016
        elif isinstance(gp_ctx, GameplayContext):
            resolved_ctx = gp_ctx
        else:
            # Fallback for any legacy tests passing positional arguments
            context = gp_ctx
            input_mgr = args[0] if len(args) > 0 else kwargs.get("input_manager")
            audio_mgr = args[1] if len(args) > 1 else kwargs.get("audio_manager")
            particle_mgr = args[2] if len(args) > 2 else kwargs.get("particle_manager")
            combat_sys = args[3] if len(args) > 3 else kwargs.get("combat_system")
            combat_dir = args[4] if len(args) > 4 else kwargs.get("combat_director")
            mission_sys = args[5] if len(args) > 5 else kwargs.get("mission_system")
            boss_sys = args[6] if len(args) > 6 else kwargs.get("boss_system")
            obj_sys = args[7] if len(args) > 7 else kwargs.get("objective_system")
            spawner_sys = args[8] if len(args) > 8 else kwargs.get("spawner")
            enc_sys = args[9] if len(args) > 9 else kwargs.get("encounter_system")
            ach_sys = args[10] if len(args) > 10 else kwargs.get("achievement_system")
            cam_sys = args[11] if len(args) > 11 else kwargs.get("camera")
            save_cb = args[12] if len(args) > 12 else kwargs.get("save_callback")
            mouse_func = args[13] if len(args) > 13 else kwargs.get("get_canvas_mouse_pos_func")

            resolved_ctx = GameplayContext(
                context=context, input_manager=input_mgr, audio_manager=audio_mgr,
                particle_manager=particle_mgr, combat_system=combat_sys,
                combat_director=combat_dir, mission_system=mission_sys,
                boss_system=boss_sys, objective_system=obj_sys, spawner=spawner_sys,
                encounter_system=enc_sys, achievement_system=ach_sys, camera=cam_sys,
                save_callback=save_cb, get_canvas_mouse_pos_func=mouse_func
            )

        ctx = resolved_ctx.context
        input_manager = resolved_ctx.input_manager
        audio_manager = resolved_ctx.audio_manager
        particle_manager = resolved_ctx.particle_manager
        combat_system = resolved_ctx.combat_system
        combat_director = resolved_ctx.combat_director
        mission_system = resolved_ctx.mission_system
        boss_system = resolved_ctx.boss_system
        objective_system = resolved_ctx.objective_system
        spawner = resolved_ctx.spawner
        encounter_system = resolved_ctx.encounter_system
        camera = resolved_ctx.camera
        achievement_system = resolved_ctx.achievement_system
        save_callback = resolved_ctx.save_callback
        get_canvas_mouse_pos_func = resolved_ctx.get_canvas_mouse_pos_func

        sec_info = SECTORS[ctx.current_sector_idx]
        if getattr(ctx, "wave_manager", None) is not None:
            prev_wave = ctx.current_wave
            ctx.current_wave = ctx.wave_manager.update_wave(ctx.level_score)
            if ctx.current_wave > prev_wave:
                ctx.wave_announcement_timer = 2.0
                ctx.last_wave = ctx.current_wave
        if ctx.wave_announcement_timer > 0:
            ctx.wave_announcement_timer = max(0.0, ctx.wave_announcement_timer - dt)

        if particle_manager:
            particle_manager.spawn_weather(sec_info.get("weather", "clear"))
            particle_manager.update(dt)

        # 1. Player Input & Aim Update
        if ctx.player:
            if ctx.player.alive:
                keys = pygame.key.get_pressed()
                canvas_mouse = get_canvas_mouse_pos_func() if get_canvas_mouse_pos_func else (640, 360)
                world_mouse = camera.screen_to_world(canvas_mouse[0], canvas_mouse[1]) if camera else canvas_mouse

                input_state = None
                if input_manager is not None:
                    p_pos = (float(ctx.player.pos.x), float(ctx.player.pos.y))
                    mouse_func = get_canvas_mouse_pos_func or (lambda: (640, 360))
                    input_state = input_manager.poll_input(p_pos, mouse_func, world_mouse_pos=world_mouse)

                ctx.player.handle_input(keys, dt, mouse_pos=world_mouse, input_state=input_state)
                ctx.player.update(dt, targets_group=ctx.target_group)

                # Fire weapons if active
                is_firing = False
                if input_state:
                    is_firing = input_state.get("fire_primary", False) or input_state.get("fire_secondary", False)
                else:
                    m_btns = pygame.mouse.get_pressed()
                    is_firing = m_btns[0] or m_btns[2] or keys[pygame.K_SPACE]

                if is_firing:
                    active_weapon_name = getattr(ctx.player, "active_weapon", "pulse")
                    wpn_lvl = ctx.weapon_upgrade_levels.get(active_weapon_name, 0)
                    bullets = ctx.player.shoot(
                        world_mouse,
                        level=wpn_lvl,
                        targets_group=ctx.target_group,
                        particle_manager=particle_manager
                    )
                    for b in bullets:
                        ctx.bullet_group.add(b)
                    if bullets and audio_manager:
                        audio_manager.play_weapon(active_weapon_name)

                if audio_manager:
                    speed_ratio = ctx.player.velocity.length() / max(1.0, getattr(ctx.player, "max_speed", 300.0))
                    audio_manager.update_engine_sound(speed_ratio, ctx.player.is_accelerating)

                    if getattr(ctx.player, "active_beam", None) and ctx.player.active_beam.alive():
                        audio_manager.start_beam_sound()
                    else:
                        audio_manager.stop_beam_sound()

                if camera:
                    camera.update(
                        (ctx.player.pos.x, ctx.player.pos.y),
                        dt,
                        shake_intensity=ctx.screen_shake_intensity,
                        shake_time=ctx.screen_shake_time
                    )
            elif getattr(ctx.player, "is_destroyed", False):
                ctx.player.update(dt)

        # 2. Mission & Director Update
        if mission_system and mission_system.active_mission_id is not None:
            if combat_director: combat_director.update(dt, ctx)
            mission_done = mission_system.update(dt, ctx, combat_director, boss_system, objective_system)
            if mission_done:
                if mission_system.is_mission_success:
                    ctx.mission_elapsed_time = pygame.time.get_ticks() / 1000.0 - ctx.mission_start_time
                    if getattr(ctx, "campaign_completed", False) and mission_system.active_mission_id == "S5_M5":
                        ctx.state = STATE_VICTORY
                        if audio_manager: audio_manager.play_victory()
                    else:
                        ctx.state = STATE_MISSION_COMPLETE
                        if audio_manager: audio_manager.play_mission_complete()
                    if achievement_system:
                        achievement_system.check_mission_complete(ctx)
                        achievement_system.check_all(ctx)
                else:
                    ctx.state = STATE_MISSION_FAILED
                    if audio_manager: audio_manager.play_game_over()
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
                    completed = getattr(combat_director, "completed_encounters", 0) if combat_director else 0
                    self._current_objective_text = f"ENCOUNTERS: {completed}/{total}"
                else:
                    self._current_objective_text = None
            else:
                self._current_objective_text = None
        else:
            if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
                if combat_director:
                    if combat_director.state == "idle":
                        combat_director.start()
                    combat_director.update(dt, ctx)
                    if not combat_director.is_suppressing_spawner and spawner:
                        spawner.update(dt, ctx)
                elif encounter_system:
                    if encounter_system.state == "idle":
                        encounter_system.start()
                    encounter_system.update(dt, ctx)
                    if not encounter_system.is_suppressing_spawner and spawner:
                        spawner.update(dt, ctx)
            elif spawner:
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
                if target.current_phase_idx != prev_boss_phase[id(target)] and particle_manager:
                    particle_manager.spawn_boss_phase_transition(target.rect.center, target.current_phase_idx)

        from src.entities.hazard import GravityAnomaly
        from src.entities.bullet import ClusterTorpedo, HomingMissile

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
        if combat_system:
            combat_system.update_combat(effective_combat_dt)

        # Check Player Death transition
        if ctx.player and getattr(ctx.player, "is_destroyed", False) and ctx.player.destruction_timer <= 0.0 and ctx.state == STATE_PLAYING:
            if mission_system and mission_system.active_mission_id is not None:
                mission_system.trigger_failure(objective_system=objective_system)
                ctx.state = STATE_MISSION_FAILED
            else:
                ctx.state = STATE_GAME_OVER
            if save_callback: save_callback()
            if ctx.state in (STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_GAME_OVER):
                return

        # 5. Legacy Stage Completion
        if mission_system is None or mission_system.active_mission_id is None:
            living_enemies = [e for e in ctx.target_group if getattr(e, "alive", False) and not getattr(e, "is_obstacle", False)]
            stage_complete = ctx.wave_manager.is_stage_complete(ctx.level_score, targets_group=ctx.target_group) if getattr(ctx, "wave_manager", None) is not None else False
            director_finished = (combat_director and combat_director.state == "complete" and len(living_enemies) == 0 and ctx.level_score >= 1200)

            boss_just_died = getattr(ctx, "boss_defeat_timer", 0.0) > 0.0
            if boss_just_died:
                ctx.boss_defeat_timer = max(0.0, ctx.boss_defeat_timer - dt)
            if getattr(ctx, "boss_rating_timer", 0.0) > 0.0:
                ctx.boss_rating_timer = max(0.0, ctx.boss_rating_timer - dt)

            if (stage_complete or director_finished) and not boss_just_died:
                ctx.state = STATE_LEVEL_CLEAR
                if audio_manager: audio_manager.play_mission_complete()
                if save_callback: save_callback()

        if achievement_system:
            achievement_system.check_all(ctx)
