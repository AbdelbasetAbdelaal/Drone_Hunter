"""
================================================================================
                    DRONE HUNTER 2D - CORE GAME ENGINE
================================================================================
Main game orchestrator managing the primary loop, event dispatching, state
transitions, subsystem updates, and rendering pipelines.
"""

import sys
import math
import random
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, TITLE, COLOR_BG, COLOR_CYAN, COLOR_GOLD,
    COLOR_CRIMSON, COLOR_EMERALD, COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_SLOWMO,
    COLOR_COIN, COLOR_NEON_RED, COLOR_TESLA, COLOR_CLUSTER
)
from src.data.game_data import (
    SECTORS, DIFFICULTY_NAMES, DIFFICULTY_NIGHTMARE, WEAPON_DEFS, UPGRADES
)
from src.core.game_state import (
    GameState, STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_PLAYING,
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,
    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED,
    STATE_SETTINGS, STATE_DRONE_SELECT
)
from src.core.game_context import GameContext
from src.core.clock import GameClock
from src.entities.player import Player
from src.entities.bullet import ClusterTorpedo, HomingMissile
from src.entities.obstacle import EnvironmentalObstacle
from src.entities.hazard import LaserGridFence, GravityAnomaly
from src.systems.save_system import SaveSystem
from src.systems.progression_system import ProgressionSystem
from src.systems.spawn_system import Spawner, WaveManager
from src.systems.encounter_system import EncounterSystem, SCOUT_SHOOTER_HEAVY_ENCOUNTER
from src.systems.combat_director import CombatDirector
from src.systems.mission_system import MissionSystem
from src.systems.boss_system import BossSystem
from src.data.mission_data import get_mission_data, get_missions_for_sector
from src.systems.combat_system import CombatSystem
from src.rendering.camera import Camera2D
from src.rendering.background import ParallaxBackground
from src.rendering.particles import ParticleManager
from src.rendering.renderer import GameRenderer
from src.audio.audio_manager import AudioManager
from src.ui.hud import (
    draw_hud, draw_boss_health_bar, draw_radar_minimap, draw_combo_banner,
    draw_boss_intro_warning
)
from src.ui.menus import (
    draw_main_menu, draw_sector_select_ui, draw_pause_settings_ui,
    draw_mission_select_ui, draw_mission_briefing, draw_mission_complete,
    draw_mission_failed, draw_settings_menu_ui,
    draw_level_clear_ui, draw_game_over_ui, draw_campaign_victory_ui
)
from src.ui.drone_select import draw_drone_select_ui
from src.ui.hangar import draw_hangar_shop_ui

class Game:
    DEBUG_PROFILE = False

    def __init__(self, test_mode: bool = False):
        self._test_mode = test_mode
        pygame.init()
        pygame.font.init()
        try: pygame.joystick.init()
        except Exception: pass

        self.win_w, self.win_h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption(f"{TITLE} [PC EDITION]")

        self.clock = GameClock()
        self.context = GameContext()
        self.is_fullscreen = False
        self.renderer = GameRenderer()
        self.background = ParallaxBackground()
        self.particle_manager = ParticleManager()
        self.audio_manager = AudioManager()
        self.save_system = SaveSystem()
        self.spawner = Spawner()
        self.encounter_system = EncounterSystem()
        self.combat_director = CombatDirector(self.encounter_system, test_mode=self._test_mode)
        self.mission_system = MissionSystem()
        self.boss_system = BossSystem()
        self.pending_mission_id = 'S1_M1'
        self.previous_state = STATE_MENU
        self.ui_rects_cache = {}
        self.combat_system = CombatSystem(self.context)

        # Inject references
        self.context.particle_manager = self.particle_manager
        self.context.audio_manager = self.audio_manager
        self.context.save_system = self.save_system
        self.context.spawner = self.spawner
        self.context.background = self.background
        self.context.encounter_system = self.encounter_system
        self.context.combat_director = self.combat_director
        self.context.mission_system = self.mission_system
        self.context.boss_system = self.boss_system

        # Load Save Data
        saved_data = self.save_system.load()
        self.context.scrap = saved_data.get("scrap", 0)
        self.context.coins = saved_data.get("coins", 0)
        self.context.highscore = saved_data.get("highscore", 0)
        self.context.upgrade_levels = saved_data.get("upgrades", {})
        self.context.unlocked_sectors = saved_data.get("sectors", [])
        self.context.unlocked_stages = saved_data.get("stages", [])
        self.context.bosses_defeated = saved_data.get("bosses_defeated", [])
        self.context.campaign_completed = saved_data.get("campaign_completed", False)
        self.context.show_crt = saved_data.get("show_crt", False)
        self.context.difficulty_mode = saved_data.get("difficulty_mode", 0)
        self.context.missions = saved_data.get("missions", self.context.missions)
        self.context.sector_progress = saved_data.get("sector_progress", self.context.sector_progress)
        self.context.selected_drone = saved_data.get("selected_drone", "striker")
        self.context.selected_skin = saved_data.get("selected_skin", 0)
        self.context.selected_skin_override = self.context.selected_skin

        self.progression = ProgressionSystem(
            self.context.unlocked_sectors,
            self.context.unlocked_stages
        )

        self.camera = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        self.running = True
        self.reset_game()
        self.context.state = STATE_MENU
        self.previous_state = STATE_MENU

        if Game.DEBUG_PROFILE:
            self._prof = {
                "frames": 0,
                "fps_sum": 0.0,
                "frame_ms_sum": 0.0,
                "max_frame_ms": 0.0,
                "max_update_ms": 0.0,
                "max_render_ms": 0.0,
                "last_print": 0.0,
                "sections": {},
                "counts": {
                    "enemies": 0, "player_bullets": 0, "enemy_bullets": 0,
                    "particles": 0, "floating_text": 0, "lightning_arcs": 0,
                },
                "states": {
                    "mission_state": "", "director_state": "", "encounter_state": "",
                },
            }

    def start_phase5_mission(self, mission_id=None):
        if not mission_id:
            mission_id = getattr(self.mission_system, "active_mission_id", None) or getattr(self, "pending_mission_id", None) or "S1_M1"
        self.pending_mission_id = mission_id

        ctx = self.context
        ctx.state = STATE_PLAYING
        ctx.player_group.empty()
        ctx.target_group.empty()
        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.obstacle_group.empty()
        ctx.hazard_group.empty()
        ctx.powerup_group.empty()
        self.particle_manager.particles.empty()
        self.particle_manager.floating_texts.empty()
        
        ctx.combo_count = 1
        ctx.combo_timer = 0.0
        ctx.damage_flash_timer = 0.0
        ctx.shake_timer = 0.0
        ctx.level_score = 0

        # Update sector and stage telemetry based on mission_id
        try:
            sec_num = int(mission_id[1])
            m_num = int(mission_id[4])
            ctx.current_sector_idx = max(0, min(4, sec_num - 1))
            ctx.current_sub_level = m_num
            ctx.missions["current_sector"] = sec_num
            ctx.missions["current_mission"] = m_num
        except Exception:
            ctx.current_sector_idx = 0
            ctx.current_sub_level = 1

        if hasattr(self, "background") and self.background is not None:
            self.background.set_sector(ctx.current_sector_idx)

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
        self.progression.apply_to_player(ctx, p)
        p.health = p.max_health
        p.energy = p.max_energy
        ctx.player = p
        ctx.player_group.add(p)
        self.camera.center_x = float(p.pos.x)
        self.camera.center_y = float(p.pos.y)

        self.encounter_system.reset()
        self.combat_director.reset()
        self.mission_system.start_mission(ctx, mission_id, self.combat_director, self.boss_system)

    def reset_game(self):
        """Initializes or resets player, spawner, and stage wave tracking."""
        ctx = self.context
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
        self.particle_manager.particles.empty()
        self.particle_manager.floating_texts.empty()

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
        self.progression.apply_to_player(ctx, ctx.player)
        ctx.player_group.add(ctx.player)
        self.camera.center_x = float(ctx.player.pos.x)
        self.camera.center_y = float(ctx.player.pos.y)

        target_score = self.progression.get_current_stage_target_score(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        is_boss_stage = (ctx.current_sub_level == 3)
        ctx.wave_manager = WaveManager(target_score, is_boss_stage=is_boss_stage)
        if hasattr(self, "spawner") and self.spawner is not None:
            self.spawner.reset_for_stage(ctx.current_sector_idx * 3 + ctx.current_sub_level, ctx.current_sector_idx)
        if hasattr(self, "encounter_system") and self.encounter_system is not None:
            self.encounter_system.reset()
        if hasattr(self, "combat_director") and self.combat_director is not None:
            self.combat_director.reset()
        if hasattr(self, "background") and self.background is not None:
            self.background.set_sector(ctx.current_sector_idx)
        
        # Phase 2E Development Integration: Sector 1 (Cyber Factory internally is 1) Stage 1
        if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
            if hasattr(self, "combat_director") and self.combat_director is not None:
                self.combat_director.start()
            
        ctx.state = STATE_PLAYING


    def start_stage(self, sector_idx: int = None, stage_idx: int = None):
        """Prepares and launches a gameplay stage."""
        ctx = self.context
        if sector_idx is not None: ctx.current_sector_idx = sector_idx
        if stage_idx is not None: ctx.current_sub_level = stage_idx

        self.reset_game()
        
        # Phase 2E Development Integration: Sector 1 (Cyber Factory internally is 1) Stage 1
        if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
            self.combat_director.start()
            
        ctx.state = STATE_PLAYING

    def save_progress(self):
        ctx = self.context
        skin_idx = getattr(ctx.player, "skin_theme", 0) if ctx.player else getattr(ctx, "selected_skin", 0)
        drone_name = getattr(ctx.player, "drone_class", "striker") if ctx.player else getattr(ctx, "selected_drone", "striker")
        self.save_system.save(
            scrap=ctx.scrap,
            coins=ctx.coins,
            highscore=ctx.highscore,
            upgrades=ctx.upgrade_levels,
            sectors=ctx.unlocked_sectors,
            show_crt=ctx.show_crt,
            stages=ctx.unlocked_stages,
            difficulty_mode=ctx.difficulty_mode,
            missions=ctx.missions,
            sector_progress=ctx.sector_progress,
            bosses_defeated=getattr(ctx, "bosses_defeated", []),
            campaign_completed=getattr(ctx, "campaign_completed", False),
            selected_drone=drone_name,
            selected_skin=skin_idx
        )

    def start_next_stage(self):
        """Advances to next stage or triggers Campaign Victory."""
        ctx = self.context
        next_sec, next_stg, is_victory = self.progression.unlock_next_stage(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        self.save_progress()

        if is_victory:
            ctx.state = STATE_VICTORY
        else:
            self.start_stage(next_sec, next_stg)

    def get_next_mission_id(self) -> str | None:
        """Determines the next mission ID in campaign sequence."""
        current_id = self.mission_system.active_mission_id or getattr(self, "pending_mission_id", None) or "S1_M1"
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

    def buy_upgrade(self, upgrade_id: str) -> bool:
        ctx = self.context
        
        # Phase 4 Upgrades
        if upgrade_id in ("hull", "energy", "weapon", "mobility"):
            if self.progression.purchase_upgrade(ctx, upgrade_id):
                self.audio_manager.play_buy()
                self.save_progress()
                if ctx.player:
                    ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                    self.progression.apply_to_player(ctx, ctx.player)
                return True
            return False
            
        # Legacy Phase 1 Upgrades
        if upgrade_id not in UPGRADES:
            return False
        info = UPGRADES[upgrade_id]
        cur_lvl = ctx.upgrade_levels.get(upgrade_id, 0)
        cost = int(info["base_cost"] * (info["cost_mult"] ** cur_lvl))
        if cur_lvl < info["max_lvl"] and ctx.coins >= cost:
            ctx.coins -= cost
            ctx.upgrade_levels[upgrade_id] = cur_lvl + 1
            self.audio_manager.play_buy()
            self.save_progress()
            if ctx.player:
                ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
                self.progression.apply_to_player(ctx, ctx.player)
            return True
        return False

    def get_canvas_mouse_pos(self, screen_pos: tuple[int, int] = None) -> tuple[int, int]:
        """Maps window screen pixel coordinates to internal 1280x720 canvas coordinates."""
        if screen_pos is None:
            raw_x, raw_y = pygame.mouse.get_pos()
        else:
            raw_x, raw_y = screen_pos

        cur_w = getattr(self, "win_w", None)
        cur_h = getattr(self, "win_h", None)
        if not cur_w or not cur_h:
            if hasattr(self, "screen") and self.screen:
                cur_w, cur_h = self.screen.get_size()
                self.win_w, self.win_h = cur_w, cur_h
            else:
                cur_w, cur_h = SCREEN_WIDTH, SCREEN_HEIGHT

        scale_x = SCREEN_WIDTH / max(1, cur_w)
        scale_y = SCREEN_HEIGHT / max(1, cur_h)
        return (int(raw_x * scale_x), int(raw_y * scale_y))

    def toggle_fullscreen(self):
        """Toggles between fullscreen and resizable windowed mode reliably."""
        self.is_fullscreen = not getattr(self, "is_fullscreen", False)
        if self.is_fullscreen:
            self._saved_window_size = (getattr(self, "win_w", SCREEN_WIDTH), getattr(self, "win_h", SCREEN_HEIGHT))
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.win_w, self.win_h = self.screen.get_size()
        else:
            saved_w, saved_h = getattr(self, "_saved_window_size", (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.win_w, self.win_h = saved_w, saved_h
            self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)

    def handle_events(self):
        ctx = self.context
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                if not getattr(self, "is_fullscreen", False):
                    self.win_w, self.win_h = event.w, event.h
                    self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue
                elif event.key == pygame.K_F2:
                    ctx.show_crt = not ctx.show_crt
                    self.save_progress()
                    continue

                if ctx.state == STATE_MENU:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        ctx.state = STATE_DRONE_SELECT
                        self.audio_manager.play_powerup()
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_MENU
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_s:
                        self.previous_state = STATE_MENU
                        ctx.state = STATE_SETTINGS
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.running = False

                elif ctx.state == STATE_DRONE_SELECT:
                    if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                        ctx.state = STATE_MENU
                    elif event.key in (pygame.K_1, pygame.K_KP1): ctx.player.apply_drone_class(0); ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_2, pygame.K_KP2): ctx.player.apply_drone_class(1); ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_3, pygame.K_KP3): ctx.player.apply_drone_class(2); ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_4, pygame.K_KP4): ctx.player.apply_drone_class(3); ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_5, pygame.K_KP5): ctx.player.apply_drone_class(4); ctx.state = STATE_SECTOR_SELECT

                elif ctx.state == STATE_SETTINGS:
                    if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_RETURN):
                        ctx.state = self.previous_state if self.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

                elif ctx.state == STATE_SECTOR_SELECT:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        cur_sec = ctx.missions.get("current_sector", 1)
                        sec_missions = get_missions_for_sector(cur_sec)
                        target_m = None
                        for m in sec_missions:
                            if self.mission_system.get_mission_state(ctx, m["id"]) != "locked":
                                target_m = m["id"]
                                break
                        if target_m:
                            self.pending_mission_id = target_m
                            ctx.state = STATE_MISSION_BRIEFING
                        elif sec_missions:
                            self.pending_mission_id = sec_missions[0]["id"]
                            ctx.state = STATE_MISSION_BRIEFING
                    elif event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                        ctx.state = STATE_MENU
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_s:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_SETTINGS
                    elif event.key == pygame.K_q:
                        self.running = False

                elif ctx.state == STATE_MISSION_BRIEFING:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_phase5_mission(self.pending_mission_id)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE, pygame.K_m):
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_q:
                        self.running = False

                elif ctx.state == STATE_HANGAR:
                    if event.key in (pygame.K_1, pygame.K_KP1): self.buy_upgrade("hull")
                    elif event.key in (pygame.K_2, pygame.K_KP2): self.buy_upgrade("energy")
                    elif event.key in (pygame.K_3, pygame.K_KP3): self.buy_upgrade("weapon")
                    elif event.key in (pygame.K_4, pygame.K_KP4): self.buy_upgrade("mobility")
                    elif event.key == pygame.K_c and ctx.player:
                        ctx.player.cycle_drone_class()
                        ctx.selected_drone_override = ctx.player.drone_class_id
                    elif event.key == pygame.K_v and ctx.player:
                        ctx.player.cycle_skin()
                        ctx.selected_skin_override = ctx.player.skin_theme
                    elif event.key == pygame.K_s:
                        self.previous_state = STATE_HANGAR
                        ctx.state = STATE_SETTINGS
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_m, pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                        ctx.state = self.previous_state if self.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
                    elif event.key == pygame.K_q:
                        self.running = False

                elif ctx.state == STATE_PLAYING:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_SPACE):
                        ctx.state = STATE_PAUSED
                    elif event.key == pygame.K_e:
                        if self.combat_system:
                            self.combat_system.execute_emp_blast()
                    elif event.key in (pygame.K_f, pygame.K_q):
                        if ctx.player and ctx.player.trigger_overdrive():
                            self.audio_manager.play_overdrive()
                            ctx.trigger_shake(14.0, 0.5)
                            self.particle_manager.spawn_shockwave(ctx.player.pos, max_r=550, color=(250, 204, 21))
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        if ctx.player and ctx.player.trigger_roll(dir_x=1.0):
                            self.audio_manager.play_whoosh()
                            self.particle_manager.spawn_barrel_roll_rings(ctx.player.pos, radius=40, color=COLOR_CYAN)
                    elif event.key in (pygame.K_k, pygame.K_c, pygame.K_v):
                        if event.key == pygame.K_k and ctx.player:
                            ctx.player.cycle_drone_class()
                            ctx.selected_drone_override = ctx.player.drone_class_id
                            ctx.selected_skin_override = ctx.player.skin_theme
                            self.audio_manager.play_powerup()
                            self.particle_manager.spawn_shockwave(ctx.player.pos, max_r=80, color=COLOR_CYAN)
                        elif event.key == pygame.K_v and ctx.player:
                            ctx.player.cycle_skin()
                            ctx.selected_skin_override = ctx.player.skin_theme
                            self.audio_manager.play_powerup()
                        elif event.key == pygame.K_c and ctx.player:
                            if ctx.player.trigger_cloak():
                                self.audio_manager.play_cloak()
                                self.particle_manager.spawn_spark(ctx.player.pos, count=15, color=(147, 51, 234))
                    elif event.key in (pygame.K_1, pygame.K_KP1) and ctx.player: ctx.player.select_weapon(0)
                    elif event.key in (pygame.K_2, pygame.K_KP2) and ctx.player: ctx.player.select_weapon(1)
                    elif event.key in (pygame.K_3, pygame.K_KP3) and ctx.player: ctx.player.select_weapon(2)
                    elif event.key in (pygame.K_4, pygame.K_KP4) and ctx.player: ctx.player.select_weapon(3)
                    elif event.key in (pygame.K_5, pygame.K_KP5) and ctx.player: ctx.player.select_weapon(4)
                    elif event.key in (pygame.K_6, pygame.K_KP6) and ctx.player: ctx.player.select_weapon(5)
                    elif event.key == pygame.K_TAB and ctx.player:
                        ctx.player.cycle_weapon()
                        if self.audio_manager:
                            self.audio_manager.play_weapon_switch()

                elif ctx.state == STATE_PAUSED:
                    if event.key in (pygame.K_p, pygame.K_SPACE, pygame.K_ESCAPE):
                        ctx.state = STATE_PLAYING
                    elif event.key == pygame.K_m:
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_q:
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU

                elif ctx.state == STATE_VICTORY:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_m, pygame.K_ESCAPE, pygame.K_b):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_q:
                        self.running = False

                elif ctx.state == STATE_GAME_OVER:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if self.pending_mission_id:
                            self.start_phase5_mission(self.pending_mission_id)
                        else:
                            ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE, pygame.K_b):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_q:
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU

                elif ctx.state == STATE_LEVEL_CLEAR:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_next_stage()
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE, pygame.K_b):
                        ctx.state = STATE_SECTOR_SELECT

                elif ctx.state == STATE_MISSION_COMPLETE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        next_mid = self.get_next_mission_id()
                        if next_mid:
                            self.start_phase5_mission(next_mid)
                        else:
                            ctx.state = STATE_VICTORY
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE, pygame.K_b):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_q:
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU

                elif ctx.state == STATE_MISSION_FAILED:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_phase5_mission(self.mission_system.active_mission_id or self.pending_mission_id)
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE, pygame.K_b):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h:
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_q:
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU

            elif event.type == pygame.MOUSEWHEEL and ctx.state == STATE_PLAYING and ctx.player:
                if event.y > 0: ctx.player.cycle_weapon()
                elif event.y < 0:
                    prev_idx = (ctx.player.current_weapon_idx - 1) % len(ctx.player.available_weapons)
                    ctx.player.select_weapon(prev_idx)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = self.get_canvas_mouse_pos(getattr(event, "pos", None))
                cache = getattr(self, 'ui_rects_cache', {}) or {}

                if ctx.state == STATE_MENU:
                    if cache.get('play') and cache['play'].collidepoint(mx, my):
                        ctx.state = STATE_DRONE_SELECT
                        self.audio_manager.play_powerup()
                    elif cache.get('hangar') and cache['hangar'].collidepoint(mx, my):
                        self.previous_state = STATE_MENU
                        ctx.state = STATE_HANGAR
                    elif cache.get('settings') and cache['settings'].collidepoint(mx, my):
                        self.previous_state = STATE_MENU
                        ctx.state = STATE_SETTINGS
                    elif cache.get('exit') and cache['exit'].collidepoint(mx, my):
                        self.running = False

                elif ctx.state == STATE_DRONE_SELECT:
                    if cache.get('back') and cache['back'].collidepoint(mx, my):
                        ctx.state = STATE_MENU
                    elif 'drones' in cache:
                        for idx, rect in cache['drones'].items():
                            if rect.collidepoint(mx, my):
                                ctx.player.apply_drone_class(idx)
                                ctx.selected_drone_override = ctx.player.drone_class_id
                                ctx.selected_skin_override = ctx.player.skin_theme
                                self.audio_manager.play_powerup()
                                ctx.state = STATE_SECTOR_SELECT
                                break

                elif ctx.state == STATE_SETTINGS:
                    if cache.get('fullscreen') and cache['fullscreen'].collidepoint(mx, my):
                        self.toggle_fullscreen()
                    elif cache.get('crt') and cache['crt'].collidepoint(mx, my):
                        ctx.show_crt = not ctx.show_crt
                        self.save_progress()
                    elif cache.get('sfx') and cache['sfx'].collidepoint(mx, my):
                        self.audio_manager.sound_enabled = not self.audio_manager.sound_enabled
                    elif cache.get('diff') and cache['diff'].collidepoint(mx, my):
                        ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                        self.save_progress()
                    elif cache.get('reset') and cache['reset'].collidepoint(mx, my):
                        ctx.scrap = 0
                        ctx.upgrade_levels = {"hull": 1, "energy": 1, "weapon": 1, "mobility": 1}
                        ctx.missions["unlocked"] = ["S1_M1"]
                        ctx.missions["completed"] = []
                        ctx.sector_progress = {"unlocked": [1], "completed": []}
                        ctx.bosses_defeated = []
                        ctx.campaign_completed = False
                        self.save_progress()
                    elif cache.get('back') and cache['back'].collidepoint(mx, my):
                        ctx.state = self.previous_state if self.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

                elif ctx.state == STATE_SECTOR_SELECT:
                    if cache.get("back") and cache["back"].collidepoint(mx, my):
                        ctx.state = STATE_MENU
                    elif cache.get("hangar") and cache["hangar"].collidepoint(mx, my):
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif cache.get("settings") and cache["settings"].collidepoint(mx, my):
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_SETTINGS
                    elif cache.get("exit") and cache["exit"].collidepoint(mx, my):
                        self.running = False
                    elif cache.get("diff_rect") and cache["diff_rect"].collidepoint(mx, my):
                        ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                        self.save_progress()
                    elif "sectors" in cache and any(r.collidepoint(mx, my) for r in cache["sectors"].values()):
                        for s_id, rect in cache["sectors"].items():
                            if rect.collidepoint(mx, my):
                                ctx.missions["current_sector"] = s_id
                                break
                    elif "missions" in cache and any(r.collidepoint(mx, my) for r in cache["missions"].values()):
                        for m_id, rect in cache["missions"].items():
                            if rect.collidepoint(mx, my):
                                st = self.mission_system.get_mission_state(ctx, m_id)
                                if st != "locked":
                                    self.pending_mission_id = m_id
                                    ctx.state = STATE_MISSION_BRIEFING
                                    break

                elif ctx.state == STATE_MISSION_BRIEFING:
                    if cache.get("back") and cache["back"].collidepoint(mx, my):
                        ctx.state = STATE_SECTOR_SELECT
                    elif cache.get("start") and cache["start"].collidepoint(mx, my):
                        self.start_phase5_mission(self.pending_mission_id)
                    elif cache.get("exit") and cache["exit"].collidepoint(mx, my):
                        self.running = False

                elif ctx.state == STATE_HANGAR:
                    if cache.get("back") and cache["back"].collidepoint(mx, my):
                        ctx.state = self.previous_state if self.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
                    elif cache.get("skin") and cache["skin"].collidepoint(mx, my):
                        if ctx.player:
                            ctx.player.cycle_skin()
                            ctx.selected_skin_override = ctx.player.skin_theme
                    elif cache.get("settings") and cache["settings"].collidepoint(mx, my):
                        self.previous_state = STATE_HANGAR
                        ctx.state = STATE_SETTINGS
                    elif cache.get("exit") and cache["exit"].collidepoint(mx, my):
                        self.running = False
                    elif "upgrades" in cache:
                        for upg_id, upg_r in cache["upgrades"].items():
                            if upg_r.collidepoint(mx, my):
                                self.buy_upgrade(upg_id)
                                break

                elif ctx.state == STATE_PAUSED:
                    pause_btns = draw_pause_settings_ui(self.renderer.canvas, ctx.difficulty_mode, ctx.show_crt, self.audio_manager.sound_enabled)
                    if pause_btns["diff"].collidepoint(mx, my):
                        ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                    elif pause_btns["crt"].collidepoint(mx, my):
                        ctx.show_crt = not ctx.show_crt
                        self.save_progress()
                    elif pause_btns["sfx"].collidepoint(mx, my):
                        self.audio_manager.sound_enabled = not self.audio_manager.sound_enabled
                    elif pause_btns["resume"].collidepoint(mx, my):
                        ctx.state = STATE_PLAYING
                    elif pause_btns["hangar"].collidepoint(mx, my):
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif pause_btns["map"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif pause_btns["exit"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU

                elif ctx.state == STATE_MISSION_COMPLETE:
                    if cache.get("next") and cache["next"].collidepoint(mx, my):
                        next_mid = self.get_next_mission_id()
                        if next_mid:
                            self.start_phase5_mission(next_mid)
                        else:
                            ctx.state = STATE_VICTORY
                    elif cache.get("hangar") and cache["hangar"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif cache.get("map") and cache["map"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    else:
                        next_mid = self.get_next_mission_id()
                        if next_mid:
                            self.start_phase5_mission(next_mid)
                        else:
                            ctx.state = STATE_SECTOR_SELECT

                elif ctx.state == STATE_MISSION_FAILED:
                    if cache.get("retry") and cache["retry"].collidepoint(mx, my):
                        self.start_phase5_mission(self.mission_system.active_mission_id or self.pending_mission_id)
                    elif cache.get("map") and cache["map"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_SECTOR_SELECT
                    elif cache.get("exit") and cache["exit"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU
                    else:
                        self.start_phase5_mission(self.mission_system.active_mission_id or self.pending_mission_id)

                elif ctx.state == STATE_LEVEL_CLEAR:
                    if cache.get("next") and cache["next"].collidepoint(mx, my):
                        self.start_next_stage()
                    elif cache.get("hangar") and cache["hangar"].collidepoint(mx, my):
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif cache.get("map") and cache["map"].collidepoint(mx, my):
                        ctx.state = STATE_SECTOR_SELECT
                    else:
                        self.start_next_stage()

                elif ctx.state == STATE_VICTORY:
                    self.mission_system.active_mission_id = None
                    ctx.state = STATE_SECTOR_SELECT

                elif ctx.state == STATE_GAME_OVER:
                    if cache.get("retry") and cache["retry"].collidepoint(mx, my):
                        if self.pending_mission_id:
                            self.start_phase5_mission(self.pending_mission_id)
                        else:
                            self.start_stage(ctx.current_sector_idx, ctx.current_sub_level)
                    elif cache.get("hangar") and cache["hangar"].collidepoint(mx, my):
                        self.previous_state = STATE_SECTOR_SELECT
                        ctx.state = STATE_HANGAR
                    elif cache.get("menu") and cache["menu"].collidepoint(mx, my):
                        self.mission_system.active_mission_id = None
                        ctx.state = STATE_MENU
                    else:
                        if self.pending_mission_id:
                            self.start_phase5_mission(self.pending_mission_id)
                        else:
                            ctx.state = STATE_SECTOR_SELECT

                elif ctx.state == STATE_PLAYING:
                    if event.button == 1 and ctx.player and ctx.player.can_shoot():
                        canvas_mx, canvas_my = self.get_canvas_mouse_pos()
                        world_mx, world_my = self.camera.screen_to_world(canvas_mx, canvas_my)
                        fired_bullets = ctx.player.shoot((world_mx, world_my), level=ctx.current_sub_level, targets_group=ctx.target_group, particle_manager=self.particle_manager)
                        for b in fired_bullets: ctx.bullet_group.add(b)
                        if fired_bullets:
                            self.audio_manager.play_weapon(ctx.player.active_weapon)
                    elif event.button == 3: # Right click -> EMP
                        self.combat_system.execute_emp_blast()
                    elif event.button == 2 and ctx.player: # Middle click -> Overdrive
                        if ctx.player.trigger_overdrive():
                            self.audio_manager.play_overdrive()
                            ctx.trigger_shake(14.0, 0.5)
                            self.particle_manager.spawn_shockwave(ctx.player.pos, max_r=550, color=(250, 204, 21))
                            self.particle_manager.spawn_floating_text(ctx.player.pos, "⚡ OVERDRIVE!", (250, 204, 21), 26)

    def update(self, dt: float):
        ctx = self.context
        self.background.update(dt)
        ctx.update_timers(dt)

        if ctx.state in (STATE_PLAYING, STATE_VICTORY):
            sec_info = SECTORS[ctx.current_sector_idx]
            ctx.current_wave = ctx.wave_manager.update_wave(ctx.level_score)
            self.particle_manager.spawn_weather(sec_info.get("weather", "clear"))
            self.particle_manager.update(dt)

            if ctx.state == STATE_PLAYING:                # 1. Player Input & Update
                keys = pygame.key.get_pressed()
                if ctx.player:
                    if ctx.player.alive:
                        canvas_mx, canvas_my = self.get_canvas_mouse_pos()
                        world_mx, world_my = self.camera.screen_to_world(canvas_mx, canvas_my)
                        ctx.player.handle_input(keys, dt, mouse_pos=(world_mx, world_my))

                        # Spawn particle trail when accelerating or high velocity
                        if ctx.player.is_accelerating or ctx.player.velocity.length_squared() > 10000.0:
                            cos_a = math.cos(ctx.player.aim_angle)
                            sin_a = math.sin(ctx.player.aim_angle)
                            rear_x = ctx.player.pos.x - cos_a * 24.0
                            rear_y = ctx.player.pos.y - sin_a * 24.0
                            self.particle_manager.spawn_drone_trail((rear_x, rear_y))

                        wm_bullets = ctx.player.update(dt, targets_group=ctx.target_group)
                        for wb in wm_bullets: ctx.bullet_group.add(wb)

                        # Dynamic ion engine audio modulation
                        speed = ctx.player.velocity.length()
                        speed_ratio = speed / max(1.0, ctx.player.max_speed)
                        self.audio_manager.update_engine_sound(speed_ratio, ctx.player.is_accelerating)

                        # Player Weapon Shooting (Mouse Left Click or Spacebar)
                        mouse_pressed = pygame.mouse.get_pressed()
                        is_shooting = mouse_pressed[0] or (keys[pygame.K_SPACE] if isinstance(keys, (list, tuple, dict)) or hasattr(keys, '__getitem__') else False)
                        if is_shooting and ctx.player.can_shoot():
                            fired_bullets = ctx.player.shoot((world_mx, world_my), level=ctx.current_sub_level, targets_group=ctx.target_group, particle_manager=self.particle_manager)
                            for b in fired_bullets: ctx.bullet_group.add(b)
                            if fired_bullets and ctx.player.active_weapon != "beam":
                                self.audio_manager.play_weapon(ctx.player.active_weapon)
                                if ctx.player.active_weapon in ("rail", "plasma", "barrage"):
                                    ctx.trigger_shake(2.5, 0.10)
                                elif ctx.player.active_weapon in ("missile", "scatter"):
                                    ctx.trigger_shake(1.8, 0.08)
                                else:
                                    ctx.trigger_shake(1.2, 0.06)

                        # Beam Audio Looping & Termination
                        if getattr(ctx.player, "active_beam", None) and ctx.player.active_beam.alive():
                            self.audio_manager.start_beam_sound()
                        else:
                            self.audio_manager.stop_beam_sound()

                        # Smooth Camera Tracking
                        self.camera.update(
                            (ctx.player.pos.x, ctx.player.pos.y),
                            dt,
                            shake_intensity=ctx.screen_shake_intensity,
                            shake_time=ctx.screen_shake_time
                        )
                    else:
                        self.audio_manager.stop_engine_sound()
                        # Player is exploding: continue updating destruction timer and maintain camera focus
                        ctx.player.update(dt, targets_group=ctx.target_group)
                        self.camera.update((ctx.player.pos.x, ctx.player.pos.y), dt)

                # 2. Phase 5 & 6 Mission System & Boss Orchestration overrides Spawner
                if self.mission_system.active_mission_id is not None:
                    self.combat_director.update(dt, ctx)
                    mission_done = self.mission_system.update(dt, ctx, self.combat_director, self.boss_system)
                    if mission_done:
                        if self.mission_system.is_mission_success:
                            if getattr(ctx, "campaign_completed", False) and self.mission_system.active_mission_id == "S5_M5":
                                ctx.state = STATE_VICTORY
                                self.audio_manager.play_victory()
                            else:
                                ctx.state = STATE_MISSION_COMPLETE
                                self.audio_manager.play_mission_complete()
                        else:
                            ctx.state = STATE_MISSION_FAILED
                            self.audio_manager.play_game_over()
                    if ctx.state in (STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_VICTORY):
                        return
                else:
                    if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
                        if self.combat_director.state == "idle":
                            self.combat_director.start()
                        self.combat_director.update(dt, ctx)
                        if not self.combat_director.is_suppressing_spawner:
                            self.spawner.update(dt, ctx)
                    else:
                        self.spawner.update(dt, ctx)

                # 3. Enemies & Projectiles (Scaled by bullet-time slowmo factor)
                effective_enemy_dt = dt * ctx.time_scale

                # Expire screen shake and hit stop timers
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
                            self.particle_manager.spawn_boss_phase_transition(target.rect.center, target.current_phase_idx)

                for h in list(ctx.hazard_group):
                    if isinstance(h, GravityAnomaly): h.update(effective_enemy_dt, player=ctx.player)
                    else: h.update(effective_enemy_dt)

                ctx.obstacle_group.update(effective_enemy_dt)
                ctx.enemy_bullet_group.update(effective_enemy_dt)
                ctx.powerup_group.update(dt)

                # Update Player Bullets & Cluster Torpedo Detonations
                for b in list(ctx.bullet_group):
                    if isinstance(b, ClusterTorpedo):
                        bomblets = b.update(dt)
                        for bomb in bomblets: ctx.bullet_group.add(bomb)
                    elif isinstance(b, HomingMissile):
                        b.update(dt, target_group=ctx.target_group)
                        if self.particle_manager and random.random() < 0.5:
                            self.particle_manager.spawn_spark(b.rect.center, count=2, color=(255, 160, 40))
                    elif hasattr(b, "update") and "target_group" in b.update.__code__.co_varnames:
                        b.update(dt, target_group=ctx.target_group)
                    else:
                        b.update(dt)

                # 4. Combat & Collision Resolution
                # Apply hit-stop freeze for impactful feedback
                effective_combat_dt = dt
                if ctx.hit_stop_timer > 0.0:
                    effective_combat_dt = 0.0
                    ctx.hit_stop_timer = max(0.0, ctx.hit_stop_timer - dt)
                self.combat_system.update_combat(effective_combat_dt)

                # Check Player Death transition AFTER destruction animation finishes
                if ctx.player and getattr(ctx.player, "is_destroyed", False) and ctx.player.destruction_timer <= 0.0 and ctx.state == STATE_PLAYING:
                    if self.mission_system.active_mission_id is not None:
                        self.mission_system.trigger_failure()
                        ctx.state = STATE_MISSION_FAILED
                    else:
                        ctx.state = STATE_GAME_OVER
                    self.save_progress()
                    if ctx.state in (STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_GAME_OVER):
                        return

                # 5. Check Stage Completion (Only in legacy mode without active mission)
                if self.mission_system.active_mission_id is None:
                    living_enemies = [e for e in ctx.target_group if getattr(e, "alive", False) and not getattr(e, "is_obstacle", False)]
                    stage_complete = ctx.wave_manager.is_stage_complete(ctx.level_score, targets_group=ctx.target_group)
                    director_finished = (self.combat_director.state == "complete" and len(living_enemies) == 0 and ctx.level_score >= 1200)
                    
                    # Boss defeat hold: delay level clear to let boss explosion/audio play
                    boss_just_died = getattr(ctx, "boss_defeat_timer", 0.0) > 0.0
                    if boss_just_died:
                        ctx.boss_defeat_timer = max(0.0, ctx.boss_defeat_timer - dt)
                    
                    if (stage_complete or director_finished) and not boss_just_died:
                        ctx.state = STATE_LEVEL_CLEAR
                        self.audio_manager.play_mission_complete()
                        self.save_progress()
        else:
            self.audio_manager.stop_engine_sound()

    def render(self):

        ctx = self.context
        canvas = self.renderer.canvas
        canvas.fill(COLOR_BG)
        canvas_m_pos = self.get_canvas_mouse_pos()

        if ctx.state == STATE_MENU:
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_main_menu(canvas, mouse_pos=canvas_m_pos)

        elif ctx.state == STATE_SETTINGS:
            self.ui_rects_cache = draw_settings_menu_ui(
                canvas, ctx.difficulty_mode, ctx.show_crt,
                self.audio_manager.sound_enabled, mouse_pos=canvas_m_pos
            )

        elif ctx.state == STATE_SECTOR_SELECT:
            self.ui_rects_cache = draw_mission_select_ui(canvas, ctx, ctx.scrap, mouse_pos=canvas_m_pos)

        elif ctx.state == STATE_DRONE_SELECT:
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_drone_select_ui(canvas, canvas_m_pos, self.renderer.sprite_manager)

        elif ctx.state == STATE_MISSION_BRIEFING:
            self.ui_rects_cache = draw_mission_briefing(canvas, get_mission_data(self.pending_mission_id), ctx.scrap, mouse_pos=canvas_m_pos)

        elif ctx.state == STATE_HANGAR:
            self.ui_rects_cache = draw_hangar_shop_ui(canvas, ctx.scrap, ctx.current_sector_idx, ctx.upgrade_levels, mouse_pos=canvas_m_pos, player=ctx.player)

        elif ctx.state == STATE_VICTORY:
            draw_campaign_victory_ui(
                canvas,
                total_score=ctx.total_score,
                highscore=ctx.highscore,
                scrap=ctx.scrap,
                bosses_count=len(getattr(ctx, "bosses_defeated", [])),
                missions_count=len(ctx.missions.get("completed", []))
            )

        elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED):
            camera_offset = self.camera.get_offset()
            self.renderer.render_gameplay(ctx, self.background, self.particle_manager, camera_offset=camera_offset)
            
            # Draw Clean Minimal HUD
            draw_hud(
                canvas, ctx.player, ctx.current_sector_idx, ctx.level_score,
                ctx.total_score, ctx.scrap, DIFFICULTY_NAMES[ctx.difficulty_mode],
                combo_mult=ctx.combo_count, show_crt=ctx.show_crt,
                current_wave=ctx.current_wave, sub_level=ctx.current_sub_level,
                mission_id=getattr(self.mission_system, "active_mission_id", None)
            )
            
            draw_radar_minimap(canvas, ctx.player, ctx.target_group)

            # Boss Health Bar & Intro Warning
            if hasattr(self, "boss_system") and self.boss_system.is_intro_active and self.boss_system.active_boss_def:
                draw_boss_intro_warning(canvas, self.boss_system.active_boss_def.name, self.boss_system.intro_timer)

            boss_entity = next((t for t in ctx.target_group if getattr(t, "is_boss", False) and t.alive), None)
            if boss_entity:
                draw_boss_health_bar(canvas, boss_entity)

            if ctx.state == STATE_PLAYING:
                self.renderer.draw_crosshair(canvas_m_pos)
                
                # Boss defeated celebration overlay
                if getattr(ctx, "boss_defeat_timer", 0.0) > 0.0:
                    pct = max(0.0, min(1.0, ctx.boss_defeat_timer / 2.5))
                    alpha = int(200 * pct)
                    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 0))
                    txt = font_banner.render("BOSS DEFEATED", True, (16, 185, 129, alpha))
                    overlay.blit(txt, txt.get_rect(center=(vw // 2, vh // 2 - 40)))
                    sub = font_card.render("STAGE CLEAR INCOMING...", True, (226, 232, 240, alpha))
                    overlay.blit(sub, sub.get_rect(center=(vw // 2, vh // 2 + 10)))
                    canvas.blit(overlay, (0, 0))
            elif ctx.state == STATE_PAUSED:
                draw_pause_settings_ui(canvas, ctx.difficulty_mode, ctx.show_crt, self.audio_manager.sound_enabled, mouse_pos=canvas_m_pos)
            elif ctx.state == STATE_LEVEL_CLEAR:
                self.ui_rects_cache = draw_level_clear_ui(canvas, ctx.current_sector_idx, ctx.current_sub_level, ctx.level_score, getattr(ctx, "scrap", 0), mouse_pos=canvas_m_pos)
            elif ctx.state == STATE_GAME_OVER:
                self.ui_rects_cache = draw_game_over_ui(canvas, ctx.current_sector_idx, ctx.current_sub_level, ctx.level_score, mouse_pos=canvas_m_pos)
            elif ctx.state == STATE_MISSION_COMPLETE:
                is_sec = (self.mission_system.active_mission_data["mission_number"] == 5) if self.mission_system.active_mission_data else False
                self.ui_rects_cache = draw_mission_complete(canvas, self.mission_system.active_mission_data or {}, self.mission_system.is_mission_success, is_sec, mouse_pos=canvas_m_pos)
            elif ctx.state == STATE_MISSION_FAILED:
                self.ui_rects_cache = draw_mission_failed(canvas, ctx.scrap, mouse_pos=canvas_m_pos)

        self.renderer.present(self.screen, ctx, self.win_w, self.win_h)

    def run(self):
        """Starts main application loop."""
        import time as _time
        prof = getattr(self, "_prof", None)
        while self.running:
            dt = self.clock.tick()
            if prof:
                t0 = _time.perf_counter()
            self.handle_events()
            if prof:
                t1 = _time.perf_counter()
            self.update(dt)
            if prof:
                t2 = _time.perf_counter()
            self.render()
            if prof:
                t3 = _time.perf_counter()
                prof["frames"] += 1
                prof["fps_sum"] += self.clock.get_fps()
                frame_ms = self.clock.raw_dt * 1000.0
                prof["frame_ms_sum"] += frame_ms
                if frame_ms > prof["max_frame_ms"]:
                    prof["max_frame_ms"] = frame_ms
                update_ms = (t2 - t1) * 1000.0
                render_ms = (t3 - t2) * 1000.0
                if update_ms > prof["max_update_ms"]:
                    prof["max_update_ms"] = update_ms
                if render_ms > prof["max_render_ms"]:
                    prof["max_render_ms"] = render_ms
                prof["counts"]["enemies"] = max(prof["counts"]["enemies"], len(self.context.target_group))
                prof["counts"]["player_bullets"] = max(prof["counts"]["player_bullets"], len(self.context.bullet_group))
                prof["counts"]["enemy_bullets"] = max(prof["counts"]["enemy_bullets"], len(self.context.enemy_bullet_group))
                prof["counts"]["particles"] = max(prof["counts"]["particles"], len(self.particle_manager.particles))
                prof["counts"]["floating_text"] = max(prof["counts"]["floating_text"], len(self.particle_manager.floating_texts))
                prof["counts"]["lightning_arcs"] = max(prof["counts"]["lightning_arcs"], len(self.particle_manager.lightning_arcs))
                prof["states"]["mission_state"] = self.mission_system.state
                prof["states"]["director_state"] = self.combat_director.state
                prof["states"]["encounter_state"] = self.encounter_system.state
                for name, ms in [("handle_events", (t1-t0)*1000), ("update", update_ms), ("render", render_ms)]:
                    prof["sections"][name] = prof["sections"].get(name, 0.0) + ms
                if self.clock.raw_dt + prof["last_print"] >= 1.0:
                    prof["last_print"] = 0.0
                    fps = prof["fps_sum"] / max(1, prof["frames"])
                    frame_ms = prof["frame_ms_sum"] / max(1, prof["frames"])
                    boss_proj = len(self.boss_system.active_boss.active_projectiles) if (self.boss_system.active_boss and hasattr(self.boss_system.active_boss, 'active_projectiles')) else 0
                    boss_ph = self.boss_system.active_boss.current_phase_number if self.boss_system.active_boss else 0
                    print(f"[PROF] FPS:{fps:.1f} FRAME_MS:{frame_ms:.1f} MAX_FRAME_MS:{prof['max_frame_ms']:.1f} "
                          f"ENEMIES:{len(self.context.target_group)} BOSS_PROJECTILES:{boss_proj} "
                          f"ENEMY_PROJECTILES:{len(self.context.enemy_bullet_group)} PARTICLES:{len(self.particle_manager.particles)} "
                          f"FLOATING_TEXT:{len(self.particle_manager.floating_texts)} LIGHTNING_ARCS:{len(self.particle_manager.lightning_arcs)} "
                          f"BOSS_STATE:{self.boss_system.state} BOSS_PHASE:{boss_ph} MISSION_STATE:{self.mission_system.state}")
                    for name, total in prof["sections"].items():
                        print(f"  {name}: {total/prof['frames']:.2f}ms avg")
                else:
                    prof["last_print"] += self.clock.raw_dt

        self.save_progress()
        if prof and prof["frames"] > 0:
            fps = prof["fps_sum"] / prof["frames"]
            frame_ms = prof["frame_ms_sum"] / prof["frames"]
            print(f"[PROF FINAL] FPS:{fps:.1f} FRAME_MS:{frame_ms:.2f} "
                  f"MAX_FRAME_MS:{prof['max_frame_ms']:.2f} MAX_UPD:{prof['max_update_ms']:.2f} MAX_RND:{prof['max_render_ms']:.2f} "
                  f"ENEMIES:{prof['counts']['enemies']} PBULLETS:{prof['counts']['player_bullets']} "
                  f"EBULLETS:{prof['counts']['enemy_bullets']} PARTICLES:{prof['counts']['particles']}")
            for name, total in prof["sections"].items():
                print(f"  {name}: {total/prof['frames']:.2f}ms avg")
        pygame.quit()
        sys.exit()
