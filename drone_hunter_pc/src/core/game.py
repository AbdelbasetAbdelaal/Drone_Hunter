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
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY
)
from src.core.game_context import GameContext
from src.core.clock import GameClock
from src.entities.player import Player
from src.entities.bullet import ClusterTorpedo
from src.entities.obstacle import EnvironmentalObstacle
from src.entities.hazard import LaserGridFence, GravityAnomaly
from src.systems.save_system import SaveSystem
from src.systems.progression_system import ProgressionSystem
from src.systems.spawn_system import Spawner, WaveManager
from src.systems.encounter_system import EncounterSystem
from src.systems.combat_system import CombatSystem
from src.rendering.camera import Camera2D
from src.rendering.background import ParallaxBackground
from src.rendering.particles import ParticleManager
from src.rendering.renderer import GameRenderer
from src.audio.audio_manager import AudioManager
from src.ui.hud import (
    draw_hud, draw_boss_health_bar, draw_radar_minimap, draw_combo_banner
)
from src.ui.menus import (
    draw_main_menu, draw_sector_select_ui, draw_pause_settings_ui,
    draw_level_clear_ui, draw_game_over_ui, draw_campaign_victory_ui
)
from src.ui.hangar import draw_hangar_shop_ui

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        try: pygame.joystick.init()
        except Exception: pass

        self.win_w, self.win_h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption(f"{TITLE} [PC EDITION]")

        self.clock = GameClock()
        self.context = GameContext()
        self.renderer = GameRenderer()
        self.background = ParallaxBackground()
        self.particle_manager = ParticleManager()
        self.audio_manager = AudioManager()
        self.save_system = SaveSystem()
        self.spawner = Spawner()
        self.encounter_system = EncounterSystem()
        self.combat_system = CombatSystem(self.context)

        # Inject references
        self.context.particle_manager = self.particle_manager
        self.context.audio_manager = self.audio_manager
        self.context.save_system = self.save_system
        self.context.background = self.background
        self.context.encounter_system = self.encounter_system

        # Load Save Data
        saved_data = self.save_system.load()
        self.context.coins = saved_data["coins"]
        self.context.highscore = saved_data["highscore"]
        self.context.upgrade_levels = saved_data["upgrades"]
        self.context.unlocked_sectors = saved_data["sectors"]
        self.context.unlocked_stages = saved_data["stages"]
        self.context.show_crt = saved_data["show_crt"]
        self.context.difficulty_mode = saved_data["difficulty_mode"]

        self.progression = ProgressionSystem(
            self.context.unlocked_sectors,
            self.context.unlocked_stages
        )

        self.camera = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        self.running = True
        self.reset_game()

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
        ctx.player.apply_shop_upgrades(ctx.upgrade_levels)
        ctx.player_group.add(ctx.player)
        self.camera.center_x = float(ctx.player.pos.x)
        self.camera.center_y = float(ctx.player.pos.y)

        target_score = self.progression.get_current_stage_target_score(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        is_boss_stage = (ctx.current_sub_level == 3)
        ctx.wave_manager = WaveManager(target_score, is_boss_stage=is_boss_stage)
        self.spawner.reset_for_stage(ctx.current_sector_idx * 3 + ctx.current_sub_level, ctx.current_sector_idx)
        self.encounter_system.reset()
        self.background.set_sector(ctx.current_sector_idx)

    def save_progress(self):
        ctx = self.context
        self.save_system.save(
            coins=ctx.coins,
            highscore=ctx.highscore,
            upgrades=ctx.upgrade_levels,
            sectors=ctx.unlocked_sectors,
            show_crt=ctx.show_crt,
            stages=ctx.unlocked_stages,
            difficulty_mode=ctx.difficulty_mode
        )

    def start_next_stage(self):
        """Advances to next stage or triggers Campaign Victory (Bug 3)."""
        ctx = self.context
        next_sec, next_stg, is_victory = self.progression.unlock_next_stage(
            ctx.current_sector_idx, ctx.current_sub_level
        )
        ctx.current_sector_idx = next_sec
        ctx.current_sub_level = next_stg

        self.save_progress()

        if is_victory:
            ctx.state = STATE_VICTORY
        else:
            self.reset_game()
            ctx.state = STATE_PLAYING

    def buy_upgrade(self, upgrade_id: str) -> bool:
        ctx = self.context
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
            return True
        return False

    def handle_events(self):
        ctx = self.context
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.win_w, self.win_h = event.w, event.h
                self.camera.set_viewport_size(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    ctx.show_crt = not ctx.show_crt
                    self.save_progress()

                if event.key == pygame.K_q and ctx.state in (STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_VICTORY):
                    self.running = False

                if ctx.state == STATE_MENU:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        ctx.state = STATE_PLAYING
                    elif event.key == pygame.K_m:
                        ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h:
                        ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_q:
                        self.running = False

                elif ctx.state == STATE_SECTOR_SELECT:
                    if event.key == pygame.K_d:
                        ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                    elif event.key in (pygame.K_1, pygame.K_KP1) and self.progression.is_stage_unlocked(0, 1):
                        ctx.current_sector_idx, ctx.current_sub_level = 0, 1; self.reset_game(); ctx.state = STATE_PLAYING
                    elif event.key in (pygame.K_2, pygame.K_KP2) and self.progression.is_stage_unlocked(1, 1):
                        ctx.current_sector_idx, ctx.current_sub_level = 1, 1; self.reset_game(); ctx.state = STATE_PLAYING
                    elif event.key in (pygame.K_3, pygame.K_KP3) and self.progression.is_stage_unlocked(2, 1):
                        ctx.current_sector_idx, ctx.current_sub_level = 2, 1; self.reset_game(); ctx.state = STATE_PLAYING
                    elif event.key in (pygame.K_4, pygame.K_KP4) and self.progression.is_stage_unlocked(3, 1):
                        ctx.current_sector_idx, ctx.current_sub_level = 3, 1; self.reset_game(); ctx.state = STATE_PLAYING
                    elif event.key in (pygame.K_5, pygame.K_KP5) and self.progression.is_stage_unlocked(4, 1):
                        ctx.current_sector_idx, ctx.current_sub_level = 4, 1; self.reset_game(); ctx.state = STATE_PLAYING
                    elif event.key in (pygame.K_SPACE, pygame.K_h):
                        ctx.state = STATE_HANGAR

                elif ctx.state == STATE_HANGAR:
                    if event.key == pygame.K_1: self.buy_upgrade("battery")
                    elif event.key == pygame.K_2: self.buy_upgrade("speed")
                    elif event.key == pygame.K_3: self.buy_upgrade("fire_rate")
                    elif event.key == pygame.K_4: self.buy_upgrade("emp_recharge")
                    elif event.key == pygame.K_5: self.buy_upgrade("wingman")
                    elif event.key == pygame.K_6: self.buy_upgrade("cloak")
                    elif event.key == pygame.K_7: self.buy_upgrade("missiles")
                    elif event.key == pygame.K_8: self.buy_upgrade("beam")
                    elif event.key == pygame.K_9: self.buy_upgrade("tesla")
                    elif event.key in (pygame.K_0, pygame.K_KP0): self.buy_upgrade("cluster")
                    elif event.key in (pygame.K_u, pygame.K_o): self.buy_upgrade("overdrive")
                    elif event.key == pygame.K_c and ctx.player: ctx.player.cycle_skin()
                    elif event.key == pygame.K_m: ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        ctx.state = STATE_PLAYING

                elif ctx.state == STATE_PLAYING:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        ctx.state = STATE_PAUSED
                    elif event.key == pygame.K_e:
                        self.combat_system.execute_emp_blast()
                    elif event.key in (pygame.K_f, pygame.K_q):
                        if ctx.player and ctx.player.trigger_overdrive():
                            self.audio_manager.play_overdrive()
                            ctx.trigger_shake(14.0, 0.5)
                            self.particle_manager.spawn_shockwave(ctx.player.pos, max_r=550, color=(250, 204, 21))
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        if ctx.player and ctx.player.trigger_roll(dir_x=1.0):
                            self.audio_manager.play_roll()
                            ctx.trigger_shake(4.0, 0.18)
                    elif event.key in (pygame.K_k, pygame.K_c):
                        if event.key == pygame.K_c and ctx.player:
                            ctx.player.cycle_skin()
                        elif event.key == pygame.K_k and ctx.player:
                            if ctx.player.trigger_cloak():
                                self.audio_manager.play_cloak()
                    elif event.key in (pygame.K_1, pygame.K_KP1) and ctx.player: ctx.player.select_weapon(0)
                    elif event.key in (pygame.K_2, pygame.K_KP2) and ctx.player: ctx.player.select_weapon(1)
                    elif event.key in (pygame.K_3, pygame.K_KP3) and ctx.player: ctx.player.select_weapon(2)
                    elif event.key in (pygame.K_4, pygame.K_KP4) and ctx.player: ctx.player.select_weapon(3)
                    elif event.key in (pygame.K_5, pygame.K_KP5) and ctx.player: ctx.player.select_weapon(4)
                    elif event.key in (pygame.K_6, pygame.K_KP6) and ctx.player: ctx.player.select_weapon(5)
                    elif event.key == pygame.K_TAB and ctx.player: ctx.player.cycle_weapon()

                elif ctx.state == STATE_PAUSED:
                    if event.key in (pygame.K_p, pygame.K_SPACE): ctx.state = STATE_PLAYING
                    elif event.key == pygame.K_d: ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                    elif event.key == pygame.K_s: self.audio_manager.sound_enabled = not self.audio_manager.sound_enabled
                    elif event.key == pygame.K_h: ctx.state = STATE_HANGAR
                    elif event.key == pygame.K_m: ctx.state = STATE_SECTOR_SELECT
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE): self.running = False

                elif ctx.state == STATE_VICTORY:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        ctx.difficulty_mode = DIFFICULTY_NIGHTMARE
                        ctx.current_sector_idx, ctx.current_sub_level = 4, 3
                        self.reset_game()
                        ctx.state = STATE_PLAYING
                    elif event.key == pygame.K_m: ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_h: ctx.state = STATE_HANGAR

                elif ctx.state in (STATE_GAME_OVER, STATE_LEVEL_CLEAR):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if ctx.state == STATE_LEVEL_CLEAR: self.start_next_stage()
                        else: self.reset_game(); ctx.state = STATE_PLAYING

            elif event.type == pygame.MOUSEWHEEL and ctx.state == STATE_PLAYING and ctx.player:
                if event.y > 0: ctx.player.cycle_weapon()
                elif event.y < 0:
                    prev_idx = (ctx.player.current_weapon_idx - 1) % len(ctx.player.available_weapons)
                    ctx.player.select_weapon(prev_idx)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if ctx.state == STATE_MENU:
                    btn_w, btn_h = 240, 44
                    cx = self.win_w // 2 - btn_w // 2
                    btn_y_start = self.win_h // 2 - 10
                    gap = 14
                    
                    r_play = pygame.Rect(cx, btn_y_start, btn_w, btn_h)
                    r_sec = pygame.Rect(cx, btn_y_start + (btn_h + gap), btn_w, btn_h)
                    r_hangar = pygame.Rect(cx, btn_y_start + 2 * (btn_h + gap), btn_w, btn_h)
                    r_exit = pygame.Rect(cx, btn_y_start + 3 * (btn_h + gap), btn_w, btn_h)
                    
                    if r_play.collidepoint(mx, my):
                        self.reset_game()
                        ctx.state = STATE_PLAYING
                    elif r_sec.collidepoint(mx, my):
                        ctx.state = STATE_SECTOR_SELECT
                    elif r_hangar.collidepoint(mx, my):
                        ctx.state = STATE_HANGAR
                    elif r_exit.collidepoint(mx, my):
                        self.running = False

                elif ctx.state == STATE_SECTOR_SELECT:
                    exit_r = pygame.Rect(self.win_w - 140, self.win_h - 55, 120, 40)
                    if exit_r.collidepoint(mx, my): self.running = False
                    diff_rect = pygame.Rect(480, 28, 220, 36)
                    if diff_rect.collidepoint(mx, my):
                        ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4

                    card_w = 226
                    start_x = 44
                    gap = 18
                    for idx in range(len(SECTORS)):
                        cx = start_x + idx * (card_w + gap)
                        stage_y_start = 390
                        for stg_i in range(3):
                            stg_r = pygame.Rect(cx + 10, stage_y_start + stg_i * 38, card_w - 20, 34)
                            if stg_r.collidepoint(mx, my) and self.progression.is_stage_unlocked(idx, stg_i + 1):
                                ctx.current_sector_idx, ctx.current_sub_level = idx, stg_i + 1
                                self.reset_game()
                                ctx.state = STATE_PLAYING
                                break

                elif ctx.state == STATE_HANGAR:
                    exit_r, skin_r, item_rects = draw_hangar_shop_ui(self.renderer.canvas, ctx.coins, ctx.current_sector_idx, ctx.upgrade_levels)
                    if skin_r.collidepoint(mx, my) and ctx.player:
                        ctx.player.cycle_skin()
                    for upg_id, upg_r in item_rects.items():
                        if upg_r.collidepoint(mx, my):
                            self.buy_upgrade(upg_id)
                            break

                elif ctx.state == STATE_PAUSED:
                    pause_btns = draw_pause_settings_ui(self.renderer.canvas, ctx.difficulty_mode, ctx.show_crt, self.audio_manager.sound_enabled)
                    if pause_btns["diff"].collidepoint(mx, my): ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                    elif pause_btns["crt"].collidepoint(mx, my): ctx.show_crt = not ctx.show_crt; self.save_progress()
                    elif pause_btns["sfx"].collidepoint(mx, my): self.audio_manager.sound_enabled = not self.audio_manager.sound_enabled
                    elif pause_btns["resume"].collidepoint(mx, my): ctx.state = STATE_PLAYING
                    elif pause_btns["hangar"].collidepoint(mx, my): ctx.state = STATE_HANGAR
                    elif pause_btns["map"].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                    elif pause_btns["exit"].collidepoint(mx, my): self.running = False

                elif ctx.state == STATE_PLAYING:
                    if event.button == 3: # Right click -> EMP
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

            if ctx.state == STATE_PLAYING:
                # 1. Player Input & Update
                keys = pygame.key.get_pressed()
                if ctx.player and ctx.player.alive:
                    mx, my = pygame.mouse.get_pos()
                    world_mx, world_my = self.camera.screen_to_world(mx, my)
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

                    # Player Weapon Shooting
                    mouse_pressed = pygame.mouse.get_pressed()
                    if mouse_pressed[0] and ctx.player.can_shoot():
                        fired_bullets = ctx.player.shoot((world_mx, world_my), level=ctx.current_sub_level, targets_group=ctx.target_group)
                        for b in fired_bullets: ctx.bullet_group.add(b)
                        
                        if ctx.player.active_weapon == "pulse": self.audio_manager.play_laser()
                        elif ctx.player.active_weapon == "scatter": self.audio_manager.play_laser()
                        elif ctx.player.active_weapon == "missile": self.audio_manager.play_missile()
                        elif ctx.player.active_weapon == "beam": self.audio_manager.play_beam()
                        elif ctx.player.active_weapon == "tesla": self.audio_manager.play_tesla()
                        elif ctx.player.active_weapon == "cluster": self.audio_manager.play_cluster()

                    # Smooth Camera Tracking
                    self.camera.update((ctx.player.pos.x, ctx.player.pos.y), dt)

                # 2. Spawner / Controlled Encounter System Update
                if ctx.current_sector_idx == 0 and ctx.current_sub_level == 1 and self.encounter_system.is_active:
                    # Suppress legacy random wave spawning during intro Scout encounter
                    self.encounter_system.update(dt, ctx)
                else:
                    # Normal spawner runs once encounter completes or in other stages
                    self.spawner.update(dt, ctx)

                # 3. Enemies & Projectiles (Scaled by bullet-time slowmo factor)
                effective_enemy_dt = dt * ctx.time_scale

                for target in list(ctx.target_group):
                    p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (200, 360)
                    p_vel = (ctx.player.velocity.x, ctx.player.velocity.y) if ctx.player else (0, 0)
                    new_e_bullets = target.update(effective_enemy_dt, player_pos=p_pos, player_vel=p_vel, player_obj=ctx.player, target_group=ctx.target_group)
                    for eb in new_e_bullets: ctx.enemy_bullet_group.add(eb)

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
                        if bomblets:
                            self.audio_manager.play_cluster()
                            self.particle_manager.spawn_cluster_explosion(b.pos)
                            ctx.trigger_shake(8.0, 0.25)
                            for bb in bomblets: ctx.bullet_group.add(bb)
                    else:
                        b.update(dt)

                # 4. Combat & Collision Resolution
                self.combat_system.update_combat(dt)

                # Check Player Death
                if ctx.player and not ctx.player.alive and ctx.state == STATE_PLAYING:
                    ctx.state = STATE_GAME_OVER

                # 5. Check Stage Completion (Respects Wave Target Score & Boss Elimination)
                if ctx.wave_manager.is_stage_complete(ctx.level_score, targets_group=ctx.target_group):
                    ctx.state = STATE_LEVEL_CLEAR
                    self.audio_manager.play_powerup()
                    self.save_progress()

    def render(self):
        ctx = self.context
        canvas = self.renderer.canvas
        canvas.fill(COLOR_BG)

        if ctx.state == STATE_MENU:
            self.background.draw_menu_backdrop(canvas)
            draw_main_menu(canvas)

        elif ctx.state == STATE_SECTOR_SELECT:
            draw_sector_select_ui(canvas, ctx.unlocked_sectors, ctx.coins, ctx.difficulty_mode, ctx.unlocked_stages)

        elif ctx.state == STATE_HANGAR:
            draw_hangar_shop_ui(canvas, ctx.coins, ctx.current_sector_idx, ctx.upgrade_levels)

        elif ctx.state == STATE_VICTORY:
            draw_campaign_victory_ui(canvas, ctx.total_score, ctx.highscore, ctx.coins)

        elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER):
            camera_offset = self.camera.get_offset()
            self.renderer.render_gameplay(ctx, self.background, self.particle_manager, camera_offset=camera_offset)
            
            # Draw Clean Minimal HUD
            draw_hud(
                canvas, ctx.player, ctx.current_sector_idx, ctx.level_score,
                ctx.total_score, ctx.coins, DIFFICULTY_NAMES[ctx.difficulty_mode],
                combo_mult=ctx.combo_count, show_crt=ctx.show_crt,
                current_wave=ctx.current_wave, sub_level=ctx.current_sub_level
            )

            # Boss Health Bar
            boss_entity = next((t for t in ctx.target_group if getattr(t, "is_boss", False) and t.alive), None)
            if boss_entity:
                draw_boss_health_bar(canvas, boss_entity)

            if ctx.state == STATE_PLAYING:
                self.renderer.draw_crosshair()
            elif ctx.state == STATE_PAUSED:
                draw_pause_settings_ui(canvas, ctx.difficulty_mode, ctx.show_crt, self.audio_manager.sound_enabled)
            elif ctx.state == STATE_LEVEL_CLEAR:
                draw_level_clear_ui(canvas, ctx.current_sector_idx, ctx.current_sub_level)
            elif ctx.state == STATE_GAME_OVER:
                draw_game_over_ui(canvas, ctx.total_score, ctx.highscore)

        self.renderer.present(self.screen, ctx, self.win_w, self.win_h)

    def run(self):
        """Starts main application loop."""
        while self.running:
            dt = self.clock.tick()
            self.handle_events()
            self.update(dt)
            self.render()

        self.save_progress()
        pygame.quit()
        sys.exit()
