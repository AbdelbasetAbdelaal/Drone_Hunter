"""
================================================================================
                    DRONE HUNTER 2D - CORE GAME ENGINE
================================================================================
Master game orchestrator coordinating the main loop, state transitions,
save orchestration, gameplay lifecycle, input dispatching, and rendering pipeline.
Acts as the composition root for subsystems and controllers.
"""

import sys
import math
import random
import pygame
from typing import Optional, Tuple

from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, TITLE, COLOR_BG
)
from src.data.game_data import (
    SECTORS, DIFFICULTY_NAMES, DIFFICULTY_NIGHTMARE, DIFFICULTY_NORMAL,
    DIFFICULTY_CUSTOM, CUSTOM_DIFFICULTY_DEFAULTS
)
from src.core.game_state import (
    GameState, STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_PLAYING,
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,
    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED,
    STATE_SETTINGS, STATE_DRONE_SELECT, STATE_SAVE_SELECT, STATE_CUSTOM_DIFFICULTY,
    STATE_CONTROLLER_BINDING, STATE_CONTROLLER_TEST
)
from src.core.game_context import GameContext
from src.core.gameplay_context import GameplayContext, InputHandlingContext
from src.core.clock import GameClock
from src.core.game_state_manager import GameStateManager
from src.core.save_controller import SaveController
from src.core.gameplay_controller import GameplayController
from src.core.input_controller import InputController

from src.systems.save_system import SaveSystem
from src.systems.progression_system import ProgressionSystem
from src.systems.achievement_system import AchievementSystem
from src.systems.spawn_system import Spawner
from src.systems.encounter_system import EncounterSystem
from src.systems.combat_director import CombatDirector
from src.systems.mission_system import MissionSystem
from src.systems.objective_system import ObjectiveSystem
from src.systems.combat_system import CombatSystem

from src.rendering.camera import Camera2D
from src.rendering.background import ParallaxBackground
from src.rendering.particles import ParticleManager
from src.rendering.renderer import GameRenderer
from src.audio.audio_manager import AudioManager

from src.input import (
    InputManager,
    DEVICE_KEYBOARD_MOUSE, DEVICE_GAMEPAD, DEVICE_JOYSTICK
)

from src.ui.hud import draw_hud, draw_radar_minimap, draw_combo_banner, draw_wave_announcement
from src.ui.menus import (
    draw_main_menu, draw_sector_select_ui, draw_pause_settings_ui,
    draw_mission_select_ui, draw_mission_briefing, draw_mission_complete,
    draw_mission_failed, draw_settings_menu_ui,
    draw_level_clear_ui, draw_game_over_ui, draw_campaign_victory_ui,
    draw_save_slot_select_ui, draw_custom_difficulty_ui,
    draw_controller_binding_ui, draw_controller_test_ui
)
from src.ui.drone_select import draw_drone_select_ui
from src.ui.hangar import draw_hangar_shop_ui
from src.ui.font_manager import font_banner, font_card
from src.data.mission_data import get_mission_data


class Game:
    """Master game engine orchestrator coordinating core subsystems and frame loop."""
    DEBUG_PROFILE = False

    def __init__(self, test_mode: bool = False):
        self._initialize_foundation(test_mode)
        self._initialize_systems()
        self._initialize_controllers()
        self._wire_context()
        self._initialize_save_state(test_mode)

    # --------------------------------------------------------------------------
    # Initialization Helpers (Composition Root)
    # --------------------------------------------------------------------------
    def _initialize_foundation(self, test_mode: bool):
        self._test_mode: bool = test_mode
        pygame.init()
        pygame.font.init()
        try:
            pygame.joystick.init()
        except Exception:
            pass

        self.win_w: int = SCREEN_WIDTH
        self.win_h: int = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption(f"{TITLE} [PC EDITION]")

        self.clock = GameClock()
        self.context = GameContext()
        self.is_fullscreen: bool = False
        self.running: bool = True
        self.ui_rects_cache: dict = {}
        self._last_dt: float = 0.016

    def _initialize_systems(self):
        self.renderer = GameRenderer()
        self.background = ParallaxBackground()
        self.particle_manager = ParticleManager()
        self.audio_manager = AudioManager()
        self.save_system = SaveSystem(slot_index=0)
        self.input_manager = InputManager()
        self.spawner = Spawner()
        self.encounter_system = EncounterSystem()
        self.combat_director = CombatDirector(self.encounter_system, test_mode=self._test_mode)
        self.mission_system = MissionSystem()
        self.objective_system = ObjectiveSystem()
        self.combat_system = CombatSystem(self.context)
        self.camera = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        self.progression = ProgressionSystem(self.context.campaign_state)
        self.achievement_system = AchievementSystem()
        self.achievement_system.register_callback(
            lambda ach_id, ach_data: self.context.achievement_popups.append({
                "id": ach_id,
                "name": ach_data["name"],
                "description": ach_data["description"],
                "icon": ach_data.get("icon", ""),
                "timer": 4.0
            })
        )

    def _initialize_controllers(self):
        self.state_manager = GameStateManager(initial_state=STATE_SAVE_SELECT)
        self.save_controller = SaveController(save_system=self.save_system, initial_slot=0)
        self.gameplay_controller = GameplayController(progression_system=self.progression)
        self.input_controller = InputController()

    def _wire_context(self):
        self.context.particle_manager = self.particle_manager
        self.context.audio_manager = self.audio_manager
        self.context.save_system = self.save_system
        self.context.input_manager = self.input_manager
        self.context.spawner = self.spawner
        self.context.background = self.background
        self.context.encounter_system = self.encounter_system
        self.context.combat_director = self.combat_director
        self.context.objective_system = self.objective_system
        self.context.mission_system = self.mission_system
        self.context.achievement_system = self.achievement_system

        self.context.state = STATE_SAVE_SELECT
        self.state_manager.register_transition_listener(self._on_state_changed)

    def _initialize_save_state(self, test_mode: bool):
        if not test_mode:
            self.save_controller.load_slot(
                0, self.context, self.audio_manager, self.input_manager, self.achievement_system
            )
            self.context._sync_from_campaign_state()
        self.reset_game()
        self.context.state = STATE_SAVE_SELECT

    def _on_state_changed(self, old_state: str, new_state: str):
        self.context.state = new_state

    # --------------------------------------------------------------------------
    # Context Factories
    # --------------------------------------------------------------------------
    def create_gameplay_context(self) -> GameplayContext:
        """Constructs explicit runtime context for GameplayController operations."""
        return GameplayContext(
            context=self.context,
            progression=self.progression,
            particle_manager=self.particle_manager,
            camera=self.camera,
            spawner=self.spawner,
            encounter_system=self.encounter_system,
            combat_director=self.combat_director,
            mission_system=self.mission_system,
            objective_system=self.objective_system,
            combat_system=self.combat_system,
            background=self.background,
            audio_manager=self.audio_manager,
            input_manager=self.input_manager,
            achievement_system=self.achievement_system,
            save_callback=self.save_progress,
            get_canvas_mouse_pos_func=self.get_canvas_mouse_pos,
            start_mission_callback=self.start_phase5_mission,
            start_stage_callback=self.start_stage,
        )

    def create_input_handling_context(self) -> InputHandlingContext:
        """Constructs explicit runtime context for InputController operations."""
        return InputHandlingContext(
            context=self.context,
            input_manager=self.input_manager,
            audio_manager=self.audio_manager,
            combat_system=self.combat_system,
            particle_manager=self.particle_manager,
            mission_system=self.mission_system,
            ui_rects_cache=self.ui_rects_cache,
            win_w=self.win_w,
            win_h=self.win_h,
            is_fullscreen=self.is_fullscreen,
            previous_state=self.previous_state,
            pending_mission_id=self.pending_mission_id,
            save_callback=self.save_progress,
            start_mission_callback=self.start_phase5_mission,
            start_next_stage_callback=self.start_next_stage,
            start_new_game_plus_callback=self.start_new_game_plus,
            select_save_slot_callback=self.select_save_slot,
            buy_upgrade_callback=self.buy_upgrade,
            toggle_fullscreen_callback=self.toggle_fullscreen,
            resize_window_callback=self._on_resize_window,
            get_next_mission_id_callback=self.get_next_mission_id,
            set_previous_state_callback=self._set_previous_state,
            set_pending_mission_id_callback=self._set_pending_mission_id,
            delete_save_slot_callback=self.delete_save_slot,
            reset_progress_callback=self.reset_all_progress,
            quit_callback=self._on_quit,
        )

    def delete_save_slot(self, slot_index: int) -> bool:
        """Deletes specified save slot file."""
        return self.save_system.delete_save_slot(slot_index) if self.save_system else False

    def reset_all_progress(self) -> bool:
        """Deletes all save slot files and resets progress."""
        if self.save_system:
            for i in range(3):
                self.save_system.delete_save_slot(i)
        return True

    def _on_resize_window(self, w: int, h: int):
        self.win_w, self.win_h = w, h
        self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)

    def _set_previous_state(self, state: str):
        self.previous_state = state

    def _set_pending_mission_id(self, mission_id: str):
        self.pending_mission_id = mission_id

    def _on_quit(self):
        self.running = False

    # --------------------------------------------------------------------------
    # Backward Compatibility Properties
    # --------------------------------------------------------------------------
    @property
    def pending_mission_id(self) -> str:
        return self.gameplay_controller.pending_mission_id

    @pending_mission_id.setter
    def pending_mission_id(self, val: str):
        self.gameplay_controller.pending_mission_id = val

    @property
    def previous_state(self) -> str:
        return self.state_manager.previous_state

    @previous_state.setter
    def previous_state(self, val: str):
        self.state_manager.previous_state = val

    @property
    def save_system(self):
        if hasattr(self, "save_controller") and self.save_controller is not None:
            return self.save_controller.save_system
        return getattr(self, "_save_system", None)

    @save_system.setter
    def save_system(self, val):
        self._save_system = val
        if hasattr(self, "save_controller") and self.save_controller is not None:
            self.save_controller.save_system = val
        if hasattr(self, "context") and self.context is not None:
            self.context.save_system = val

    @property
    def selected_save_slot(self) -> int:
        return self.save_controller.selected_save_slot

    @selected_save_slot.setter
    def selected_save_slot(self, val: int):
        self.save_controller.selected_save_slot = val

    @property
    def _menu_cursor(self) -> int:
        return self.input_controller.menu_cursor

    @_menu_cursor.setter
    def _menu_cursor(self, val: int):
        self.input_controller.menu_cursor = val

    @property
    def _binding_action(self) -> Optional[str]:
        return self.input_controller.binding_action

    @_binding_action.setter
    def _binding_action(self, val: Optional[str]):
        self.input_controller.binding_action = val

    @property
    def _binding_waiting(self) -> bool:
        return self.input_controller.binding_waiting

    @_binding_waiting.setter
    def _binding_waiting(self, val: bool):
        self.input_controller.binding_waiting = val

    @property
    def custom_difficulty_dragging(self) -> int:
        return self.input_controller.custom_difficulty_dragging

    @custom_difficulty_dragging.setter
    def custom_difficulty_dragging(self, val: int):
        self.input_controller.custom_difficulty_dragging = val

    @property
    def _current_objective_text(self) -> Optional[str]:
        return self.gameplay_controller.current_objective_text

    # --------------------------------------------------------------------------
    # Save / Load Orchestration
    # --------------------------------------------------------------------------
    def select_save_slot(self, slot_num: int):
        """Selects and loads save data by slot index (accepts 0-indexed or 1-indexed)."""
        self.save_controller.select_save_slot(
            slot_num, self.context, self.audio_manager, self.input_manager, self.achievement_system
        )

    def _load_slot_data(self, slot_index: int):
        """Loads data from specified save slot index."""
        self.save_controller.load_slot(
            slot_index, self.context, self.audio_manager, self.input_manager, self.achievement_system
        )

    def save_progress(self):
        """Persists current game progress and configuration to active save slot."""
        return self.save_controller.save_current_progress(
            self.context,
            audio_manager=self.audio_manager,
            input_manager=self.input_manager,
            achievement_system=self.achievement_system,
            selected_drone=getattr(self.context, "selected_drone", "striker"),
            is_fullscreen=self.is_fullscreen
        )

    # --------------------------------------------------------------------------
    # Gameplay Lifecycle Orchestration
    # --------------------------------------------------------------------------
    def start_phase5_mission(self, mission_id: Optional[str] = None):
        """Prepares and launches a tactical mission."""
        self.state_manager.change_state(STATE_PLAYING)
        self.gameplay_controller.start_mission(
            mission_id=mission_id,
            gp_ctx_or_context=self.create_gameplay_context()
        )
        self.context.state = STATE_PLAYING

    def reset_game(self):
        """Initializes or resets player, spawner, and stage wave tracking."""
        self.gameplay_controller.reset_game(
            gp_ctx_or_context=self.create_gameplay_context()
        )

    def start_stage(self, sector_idx: Optional[int] = None, stage_idx: Optional[int] = None):
        """Prepares and launches a gameplay stage."""
        self.state_manager.change_state(STATE_PLAYING)
        self.gameplay_controller.start_stage(
            sector_idx=sector_idx,
            stage_idx=stage_idx,
            gp_ctx_or_context=self.create_gameplay_context()
        )
        self.context.state = STATE_PLAYING

    def start_next_stage(self):
        """Advances to next stage or triggers Campaign Victory."""
        self.gameplay_controller.start_next_stage(
            gp_ctx_or_context=self.create_gameplay_context()
        )

    def start_new_game_plus(self):
        """Increments NG+ count, applies difficulty multipliers, and launches S1_M1."""
        self.gameplay_controller.start_new_game_plus(
            gp_ctx_or_context=self.create_gameplay_context()
        )

    def get_next_mission_id(self) -> Optional[str]:
        """Determines the next mission ID in campaign sequence."""
        return self.gameplay_controller.get_next_mission_id(self.mission_system)

    def buy_upgrade(self, upgrade_id: str) -> bool:
        return self.gameplay_controller.buy_upgrade(
            upgrade_id, gp_ctx_or_context=self.create_gameplay_context()
        )

    def equip_weapon(self, slot_index: int, weapon_id: str) -> bool:
        return self.gameplay_controller.equip_weapon(
            slot_index, weapon_id, gp_ctx_or_context=self.create_gameplay_context()
        )

    def buy_weapon_upgrade(self, weapon_id: str) -> bool:
        return self.gameplay_controller.buy_weapon_upgrade(
            weapon_id, gp_ctx_or_context=self.create_gameplay_context()
        )

    def unlock_weapon(self, weapon_id: str) -> bool:
        return self.gameplay_controller.unlock_weapon(
            weapon_id, gp_ctx_or_context=self.create_gameplay_context()
        )

    # --------------------------------------------------------------------------
    # Window / Presentation / Input Mapping
    # --------------------------------------------------------------------------
    def get_canvas_mouse_pos(self, screen_pos: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Maps window screen coordinates to virtual 1280x720 canvas coordinates."""
        return InputController.get_canvas_mouse_pos(
            self.win_w, self.win_h, SCREEN_WIDTH, SCREEN_HEIGHT, screen_pos=screen_pos
        )

    def toggle_fullscreen(self):
        """Toggles between bordered window and borderless/exclusive fullscreen."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            info = pygame.display.Info()
            self.win_w, self.win_h = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.FULLSCREEN)
        else:
            self.win_w, self.win_h = SCREEN_WIDTH, SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        self.save_progress()

    def _get_current_input_context(self) -> str:
        return InputController.get_current_input_context(self.context.state)

    def handle_events(self):
        """Dispatches input events to InputController."""
        input_ctx = self.create_input_handling_context()
        if not self.input_controller.handle_events(input_ctx):
            self.running = False

    def _update_controller_menu_navigation(self, dt: float):
        """Updates D-pad menu cursor navigation."""
        input_ctx = self.create_input_handling_context()
        self.input_controller.update_controller_navigation(dt, input_ctx)

    # --------------------------------------------------------------------------
    # Frame Update Loop
    # --------------------------------------------------------------------------
    def update(self, dt: float):
        """Updates background, achievement timers, controller navigation, and active combat."""
        ctx = self.context
        self.input_manager.set_context(self._get_current_input_context())
        self.background.update(dt)
        ctx.update_timers(dt)

        for popup in ctx.achievement_popups:
            popup["timer"] -= dt
        ctx.achievement_popups = [p for p in ctx.achievement_popups if p.get("timer", 0) > 0]

        self._update_controller_menu_navigation(dt)

        if ctx.state in (STATE_PLAYING, STATE_VICTORY):
            if ctx.state == STATE_PLAYING:
                gp_ctx = self.create_gameplay_context()
                self.gameplay_controller.update_gameplay(dt=dt, gp_ctx=gp_ctx)
            else:
                sec_info = SECTORS[ctx.current_sector_idx]
                self.particle_manager.spawn_weather(sec_info.get("weather", "clear"))
                self.particle_manager.update(dt)
        else:
            self.audio_manager.stop_engine_sound()

    # --------------------------------------------------------------------------
    # Rendering Pipeline
    # --------------------------------------------------------------------------
    def render(self):
        """Renders active state UI, backdrop, gameplay entities, HUD, and overlays."""
        ctx = self.context
        canvas = self.renderer.canvas
        canvas.fill(COLOR_BG)
        canvas_m_pos = self.get_canvas_mouse_pos()
        vw, vh = canvas.get_size()
        active_is_gamepad = self.input_manager.active_device in (
            DEVICE_GAMEPAD, DEVICE_JOYSTICK
        )

        if ctx.state == STATE_MENU:
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_main_menu(
                canvas, mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_SAVE_SELECT:
            self.ui_rects_cache = draw_save_slot_select_ui(
                canvas, self.save_system, mouse_pos=canvas_m_pos,
                input_manager=self.input_manager,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_SETTINGS:
            self.ui_rects_cache = draw_settings_menu_ui(
                canvas, ctx.difficulty_mode, ctx.show_crt,
                self.audio_manager.sound_enabled, mouse_pos=canvas_m_pos,
                input_manager=self.input_manager,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_CUSTOM_DIFFICULTY:
            self.ui_rects_cache = draw_custom_difficulty_ui(
                canvas, ctx.custom_difficulty_settings, mouse_pos=canvas_m_pos,
                dragging=self.custom_difficulty_dragging,
                input_manager=self.input_manager,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_CONTROLLER_BINDING:
            self.ui_rects_cache = draw_controller_binding_ui(
                canvas, getattr(self.input_manager, "mapping_manager", None), mouse_pos=canvas_m_pos,
                binding_action=self._binding_action,
                waiting=self._binding_waiting
            )

        elif ctx.state == STATE_CONTROLLER_TEST:
            self.ui_rects_cache = draw_controller_test_ui(
                canvas, self.input_manager.active_joystick, getattr(self.input_manager, "mapping_manager", None),
                mouse_pos=canvas_m_pos
            )

        elif ctx.state == STATE_DRONE_SELECT:
            from src.rendering.sprite_manager import get_sprite_manager
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_drone_select_ui(
                canvas, mouse_pos=canvas_m_pos,
                sprite_manager=get_sprite_manager(),
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_HANGAR:
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_hangar_shop_ui(
                canvas, ctx.scrap, ctx.current_sector_idx, ctx.upgrade_levels,
                mouse_pos=canvas_m_pos,
                player=ctx.player,
                weapon_upgrades=getattr(ctx, "weapon_upgrade_levels", {}),
                unlocked_weapons=getattr(ctx, "unlocked_weapons", ["pulse", "scatter", "missile"]),
                total_score=getattr(ctx, "total_score", 0),
                selected_index=self._menu_cursor if active_is_gamepad else None,
                input_manager=self.input_manager
            )

        elif ctx.state == STATE_SECTOR_SELECT:
            self.background.draw_menu_backdrop(canvas)
            self.ui_rects_cache = draw_mission_select_ui(
                canvas, ctx, ctx.scrap, mouse_pos=canvas_m_pos
            )

        elif ctx.state == STATE_MISSION_BRIEFING:
            self.background.draw_menu_backdrop(canvas)
            m_data = get_mission_data(self.pending_mission_id)
            self.ui_rects_cache = draw_mission_briefing(
                canvas, m_data, ctx.scrap, mouse_pos=canvas_m_pos,
                input_manager=self.input_manager
            )

        elif ctx.state == STATE_PLAYING:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            # HUD Overlay
            self.ui_rects_cache = draw_hud(
                canvas, ctx.player,
                sector_idx=ctx.current_sector_idx,
                level_score=ctx.level_score,
                total_score=ctx.total_score,
                scrap=ctx.scrap,
                difficulty_name=DIFFICULTY_NAMES[ctx.difficulty_mode] if 0 <= ctx.difficulty_mode < len(DIFFICULTY_NAMES) else "NORMAL",
                combo_mult=ctx.combo_count,
                show_crt=ctx.show_crt,
                current_wave=ctx.current_wave,
                sub_level=ctx.current_sub_level,
                mission_id=getattr(self.mission_system, "active_mission_id", None),
                input_manager=self.input_manager,
                objective_text=self._current_objective_text,
                objective_system=self.objective_system,
                camera_offset=self.camera.get_offset()
            )
            draw_radar_minimap(canvas, ctx.player, ctx.target_group)
            draw_combo_banner(canvas, ctx.combo_count, ctx.combo_timer)
            draw_wave_announcement(canvas, ctx.current_wave, getattr(ctx, "wave_announcement_timer", 0.0))

        elif ctx.state == STATE_PAUSED:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            self.ui_rects_cache = draw_pause_settings_ui(
                canvas, ctx.difficulty_mode, ctx.show_crt, self.audio_manager.sound_enabled,
                mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_MISSION_COMPLETE:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            m_data = getattr(self.mission_system, "active_mission_data", None) or get_mission_data(self.pending_mission_id)
            self.ui_rects_cache = draw_mission_complete(
                canvas, m_data,
                was_first_clear=getattr(self.mission_system, "is_first_clear", False),
                is_sector_clear=getattr(self.mission_system, "is_sector_clear", False),
                mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_MISSION_FAILED:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            self.ui_rects_cache = draw_mission_failed(
                canvas, ctx.scrap, mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_LEVEL_CLEAR:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            self.ui_rects_cache = draw_level_clear_ui(
                canvas, sector_idx=ctx.current_sector_idx, sub_level=ctx.current_sub_level,
                score=ctx.level_score, scrap=ctx.scrap, mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_GAME_OVER:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            self.ui_rects_cache = draw_game_over_ui(
                canvas, sector_idx=ctx.current_sector_idx, sub_level=ctx.current_sub_level,
                score=ctx.level_score, mouse_pos=canvas_m_pos,
                selected_index=self._menu_cursor if active_is_gamepad else None
            )

        elif ctx.state == STATE_VICTORY:
            self.renderer.render_gameplay(
                ctx, self.background, self.particle_manager,
                camera_offset=self.camera.get_offset()
            )
            self.ui_rects_cache = draw_campaign_victory_ui(
                canvas, total_score=getattr(ctx, "total_score", 0),
                highscore=ctx.highscore, scrap=ctx.scrap,
                ng_plus_count=getattr(ctx, "new_game_plus_count", 0)
            )

        # Draw Achievement Popups
        y_off = 20
        for popup in ctx.achievement_popups:
            alpha = min(255, int(popup["timer"] * 255))
            pop_surf = pygame.Surface((320, 60), pygame.SRCALPHA)
            pygame.draw.rect(pop_surf, (15, 23, 42, min(240, alpha)), (0, 0, 320, 60), border_radius=8)
            pygame.draw.rect(pop_surf, (245, 158, 11, alpha), (0, 0, 320, 60), 2, border_radius=8)

            t_title = font_card.render(f"ACHIEVEMENT UNLOCKED!", True, (245, 158, 11))
            t_name = font_card.render(f"{popup['icon']} {popup['name']}", True, (255, 255, 255))
            pop_surf.blit(t_title, (12, 8))
            pop_surf.blit(t_name, (12, 32))
            canvas.blit(pop_surf, (vw - 340, y_off))
            y_off += 70

        # Blit virtual canvas to presentation window
        if not self._test_mode:
            self.renderer.present(self.screen, ctx, self.win_w, self.win_h)

    # --------------------------------------------------------------------------
    # Main Game Execution Loop
    # --------------------------------------------------------------------------
    def run(self):
        """Executes the master variable-timestep game loop until termination."""
        while self.running:
            dt = self.clock.tick()
            self._last_dt = dt

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()
