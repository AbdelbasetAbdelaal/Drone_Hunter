"""
================================================================================
                    DRONE HUNTER 2D - INPUT CONTROLLER
================================================================================
Handles virtual canvas mouse coordinate projections, context-aware event routing,
menu button clicks, slider dragging, and controller D-pad navigation.
Receives dependencies explicitly through InputHandlingContext without coupling to Game.
"""

import pygame
from typing import Optional, Dict, Any, Tuple, Callable

from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from src.data.game_data import (
    DIFFICULTY_NORMAL, DIFFICULTY_CUSTOM, DIFFICULTY_NIGHTMARE, SECTORS, WEAPON_DEFS
)
from src.core.game_state import (
    GameState, STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_PLAYING,
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,
    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED,
    STATE_SETTINGS, STATE_DRONE_SELECT, STATE_SAVE_SELECT, STATE_CUSTOM_DIFFICULTY,
    STATE_CONTROLLER_BINDING, STATE_CONTROLLER_TEST
)
from src.core.gameplay_context import InputHandlingContext
from src.input import (
    InputManager, InputContext,
    ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY, ACTION_EMP, ACTION_ULTIMATE,
    ACTION_ROLL, ACTION_WEAPON_NEXT, ACTION_WEAPON_PREV, ACTION_SPECIAL,
    ACTION_CLOAK, ACTION_CYCLE_CLASS, ACTION_PAUSE,
    ACTION_FULLSCREEN, ACTION_CONFIRM, ACTION_CANCEL, ACTION_SECTOR_MAP,
    ACTION_HANGAR_BAY, ACTION_SETTINGS,
    ACTION_WEAPON_SLOT_1, ACTION_WEAPON_SLOT_2, ACTION_WEAPON_SLOT_3,
    ACTION_WEAPON_SLOT_4, ACTION_WEAPON_SLOT_5, ACTION_WEAPON_SLOT_6,
    ACTION_SELECT_SLOT_1, ACTION_SELECT_SLOT_2, ACTION_SELECT_SLOT_3,
    ACTION_SELECT_SLOT_4, ACTION_SELECT_SLOT_5,
    DEVICE_KEYBOARD_MOUSE
)
from src.data.mission_data import get_missions_for_sector


class InputController:
    """Encapsulates input event routing, canvas projections, and menu navigation."""

    def __init__(self):
        self.menu_cursor: int = 0
        self.dpad_repeat_timer: float = 0.0
        self.dpad_last_state: Dict[str, bool] = {"up": False, "down": False, "left": False, "right": False}
        self.custom_difficulty_dragging: int = -1
        self.binding_action: Optional[str] = None
        self.binding_waiting: bool = False

    @staticmethod
    def get_canvas_mouse_pos(win_w: int, win_h: int, view_w: int = SCREEN_WIDTH,
                             view_h: int = SCREEN_HEIGHT,
                             screen_pos: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Maps physical window mouse coordinates into virtual 1280x720 canvas coordinates."""
        if screen_pos is None:
            screen_pos = pygame.mouse.get_pos()

        sx, sy = screen_pos
        scale = min(win_w / view_w, win_h / view_h)
        scaled_w = view_w * scale
        scaled_h = view_h * scale
        offset_x = (win_w - scaled_w) / 2.0
        offset_y = (win_h - scaled_h) / 2.0

        canvas_x = (sx - offset_x) / scale if scale > 0 else 0.0
        canvas_y = (sy - offset_y) / scale if scale > 0 else 0.0
        return int(canvas_x), int(canvas_y)

    @staticmethod
    def get_current_input_context(state: str) -> str:
        """Determines the appropriate InputContext for the active GameState."""
        if state == STATE_PLAYING:
            return InputContext.GAMEPLAY
        elif state in (STATE_MENU, STATE_SAVE_SELECT):
            return InputContext.MAIN_MENU
        elif state in (STATE_SECTOR_SELECT, STATE_MISSION_BRIEFING):
            return InputContext.MISSION_SELECT
        elif state == STATE_DRONE_SELECT:
            return InputContext.DRONE_SELECT
        elif state == STATE_HANGAR:
            return InputContext.HANGAR
        elif state in (STATE_SETTINGS, STATE_CUSTOM_DIFFICULTY, STATE_CONTROLLER_TEST, STATE_CONTROLLER_BINDING):
            return InputContext.SETTINGS
        elif state == STATE_PAUSED:
            return InputContext.PAUSE
        elif state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            return InputContext.MISSION_COMPLETE
        elif state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            return InputContext.MISSION_FAILED
        return InputContext.GAMEPLAY

    def _resolve_input_context(self, input_ctx_or_game: Any, **kwargs) -> InputHandlingContext:
        """Helper to accept either an InputHandlingContext or duck-typed legacy container."""
        if isinstance(input_ctx_or_game, InputHandlingContext):
            return input_ctx_or_game

        g = input_ctx_or_game
        if hasattr(g, "context") and hasattr(g, "input_manager"):
            return InputHandlingContext(
                context=g.context,
                input_manager=g.input_manager,
                audio_manager=getattr(g, "audio_manager", None),
                combat_system=getattr(g, "combat_system", None),
                particle_manager=getattr(g, "particle_manager", None),
                mission_system=getattr(g, "mission_system", None),
                ui_rects_cache=getattr(g, "ui_rects_cache", {}),
                win_w=getattr(g, "win_w", SCREEN_WIDTH),
                win_h=getattr(g, "win_h", SCREEN_HEIGHT),
                is_fullscreen=getattr(g, "is_fullscreen", False),
                previous_state=getattr(g, "previous_state", None),
                pending_mission_id=getattr(g, "pending_mission_id", "S1_M1"),
                save_callback=getattr(g, "save_progress", None),
                start_mission_callback=getattr(g, "start_phase5_mission", None),
                select_save_slot_callback=getattr(g, "select_save_slot", None),
                buy_upgrade_callback=getattr(g, "buy_upgrade", None),
                toggle_fullscreen_callback=getattr(g, "toggle_fullscreen", None),
                resize_window_callback=lambda w, h: setattr(g, "win_w", w) or setattr(g, "win_h", h),
                get_next_mission_id_callback=getattr(g, "get_next_mission_id", None),
                set_previous_state_callback=lambda s: setattr(g, "previous_state", s),
                set_pending_mission_id_callback=lambda m: setattr(g, "pending_mission_id", m),
                quit_callback=lambda: setattr(g, "running", False),
            )

        return InputHandlingContext(
            context=input_ctx_or_game,
            input_manager=kwargs.get("input_manager"),
            audio_manager=kwargs.get("audio_manager"),
            combat_system=kwargs.get("combat_system"),
            particle_manager=kwargs.get("particle_manager"),
            mission_system=kwargs.get("mission_system"),
            ui_rects_cache=kwargs.get("ui_rects_cache", {}),
            win_w=kwargs.get("win_w", SCREEN_WIDTH),
            win_h=kwargs.get("win_h", SCREEN_HEIGHT),
            is_fullscreen=kwargs.get("is_fullscreen", False),
            previous_state=kwargs.get("previous_state"),
            pending_mission_id=kwargs.get("pending_mission_id", "S1_M1"),
            save_callback=kwargs.get("save_callback"),
            start_mission_callback=kwargs.get("start_mission_callback"),
            select_save_slot_callback=kwargs.get("select_save_slot_callback"),
            buy_upgrade_callback=kwargs.get("buy_upgrade_callback"),
            toggle_fullscreen_callback=kwargs.get("toggle_fullscreen_callback"),
            resize_window_callback=kwargs.get("resize_window_callback"),
            get_next_mission_id_callback=kwargs.get("get_next_mission_id_callback"),
            set_previous_state_callback=kwargs.get("set_previous_state_callback"),
            set_pending_mission_id_callback=kwargs.get("set_pending_mission_id_callback"),
            quit_callback=kwargs.get("quit_callback"),
        )

    def handle_events(self, input_ctx_or_game: Any) -> bool:
        """Processes all pending SDL/Pygame events and dispatches to appropriate handlers.
        Returns False if game should quit, True otherwise."""
        input_ctx = self._resolve_input_context(input_ctx_or_game)
        ctx = input_ctx.context
        im = input_ctx.input_manager

        if im is not None:
            im.set_context(self.get_current_input_context(ctx.state))
            events = pygame.event.get()
            im.process_events(events)
        else:
            events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                if input_ctx.quit_callback:
                    input_ctx.quit_callback()
                return False

            elif event.type == pygame.VIDEORESIZE:
                if not input_ctx.is_fullscreen:
                    input_ctx.win_w, input_ctx.win_h = event.w, event.h
                    if input_ctx.resize_window_callback:
                        input_ctx.resize_window_callback(event.w, event.h)
                    else:
                        pygame.display.set_mode((input_ctx.win_w, input_ctx.win_h), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if im is None:
                    if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT)):
                        if input_ctx.toggle_fullscreen_callback:
                            input_ctx.toggle_fullscreen_callback()
                        continue
                if event.key == pygame.K_F2:
                    ctx.show_crt = not ctx.show_crt
                    if input_ctx.save_callback:
                        input_ctx.save_callback()
                    continue

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self.get_canvas_mouse_pos(input_ctx.win_w, input_ctx.win_h, screen_pos=event.pos)
                self._handle_mouse_click(mx, my, input_ctx)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.custom_difficulty_dragging = -1

            elif event.type == pygame.MOUSEMOTION:
                if self.custom_difficulty_dragging >= 0 and ctx.state == STATE_CUSTOM_DIFFICULTY:
                    mx, _ = self.get_canvas_mouse_pos(input_ctx.win_w, input_ctx.win_h, screen_pos=event.pos)
                    self._update_slider_drag(mx, input_ctx)

            elif event.type == pygame.JOYBUTTONDOWN:
                if not self._handle_controller_button_down(event, input_ctx):
                    if input_ctx.quit_callback:
                        input_ctx.quit_callback()
                    return False

        # Process discrete action triggers (Single Authoritative Input Path)
        if im is not None:
            trig = getattr(im, "actions_triggered", {})

            # Fullscreen trigger (F11 / Alt+Enter / Gamepad Hold)
            if trig.get(ACTION_FULLSCREEN):
                trig[ACTION_FULLSCREEN] = False
                if input_ctx.toggle_fullscreen_callback:
                    input_ctx.toggle_fullscreen_callback()

            # Gameplay actions
            if ctx.state == STATE_PLAYING and ctx.player:
                if trig.get(ACTION_PAUSE):
                    trig[ACTION_PAUSE] = False
                    ctx.state = STATE_PAUSED
                elif trig.get(ACTION_SECTOR_MAP):
                    trig[ACTION_SECTOR_MAP] = False
                    self._set_previous_state(input_ctx, STATE_PLAYING)
                    ctx.state = STATE_SECTOR_SELECT
                elif trig.get(ACTION_ROLL):
                    if ctx.player.trigger_roll(dir_x=1.0):
                        if input_ctx.audio_manager:
                            input_ctx.audio_manager.play_roll()
                        if input_ctx.particle_manager:
                            input_ctx.particle_manager.spawn_barrel_roll_rings(ctx.player.pos, radius=40, color=(34, 211, 238))
                        im.trigger_rumble(0.2, 0.4, 100)
                elif trig.get(ACTION_EMP) and input_ctx.combat_system:
                    input_ctx.combat_system.execute_emp_blast()
                    im.trigger_rumble(0.6, 0.8, 200)
                elif trig.get(ACTION_ULTIMATE):
                    if ctx.player.trigger_overdrive():
                        if input_ctx.audio_manager:
                            input_ctx.audio_manager.play_overdrive()
                        ctx.trigger_shake(14.0, 0.5)
                        if input_ctx.particle_manager:
                            input_ctx.particle_manager.spawn_shockwave(ctx.player.pos, max_r=550, color=(250, 204, 21))
                        im.trigger_rumble(0.8, 1.0, 300)
                elif trig.get(ACTION_WEAPON_NEXT):
                    ctx.player.cycle_weapon(1)
                    if input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_PREV):
                    ctx.player.cycle_weapon(-1)
                    if input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_CLOAK) or trig.get(ACTION_SPECIAL):
                    if ctx.player.trigger_cloak():
                        if input_ctx.audio_manager:
                            input_ctx.audio_manager.play_cloak()
                        if input_ctx.particle_manager:
                            input_ctx.particle_manager.spawn_spark(ctx.player.pos, count=15, color=(147, 51, 234))
                elif trig.get(ACTION_CYCLE_CLASS):
                    ctx.player.cycle_drone_class(1)
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
                    if input_ctx.audio_manager:
                        input_ctx.audio_manager.play_powerup()
                elif trig.get(ACTION_WEAPON_SLOT_1):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(0)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_SLOT_2):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(1)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_SLOT_3):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(2)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_SLOT_4):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(3)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_SLOT_5):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(4)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()
                elif trig.get(ACTION_WEAPON_SLOT_6):
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(5)
                    if ctx.player.active_weapon != previous_weapon and input_ctx.audio_manager:
                        input_ctx.audio_manager.play_weapon_switch()

            elif ctx.state in (STATE_HANGAR, STATE_DRONE_SELECT) and ctx.player:
                if trig.get(ACTION_CYCLE_CLASS):
                    ctx.player.cycle_drone_class(1)
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
                    if input_ctx.audio_manager:
                        input_ctx.audio_manager.play_powerup()

        return True

    def _set_previous_state(self, input_ctx: InputHandlingContext, state: str):
        input_ctx.previous_state = state
        if input_ctx.set_previous_state_callback:
            input_ctx.set_previous_state_callback(state)

    def _set_pending_mission(self, input_ctx: InputHandlingContext, mission_id: str):
        input_ctx.pending_mission_id = mission_id
        if input_ctx.set_pending_mission_id_callback:
            input_ctx.set_pending_mission_id_callback(mission_id)

    def _handle_keyboard_menu_navigation(self, event, input_ctx: InputHandlingContext) -> bool:
        """Handles keyboard shortcut and keydown events for menu screens."""
        ctx = input_ctx.context
        am = input_ctx.audio_manager

        if ctx.state == STATE_MENU:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                ctx.state = STATE_DRONE_SELECT
                if am: am.play_powerup()
            elif event.key == pygame.K_h:
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_s:
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_SETTINGS
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                return False

        elif ctx.state == STATE_SAVE_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return False
            elif event.key in (pygame.K_1, pygame.K_KP1):
                if input_ctx.select_save_slot_callback: input_ctx.select_save_slot_callback(0)
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_2, pygame.K_KP2):
                if input_ctx.select_save_slot_callback: input_ctx.select_save_slot_callback(1)
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_3, pygame.K_KP3):
                if input_ctx.select_save_slot_callback: input_ctx.select_save_slot_callback(2)
                ctx.state = STATE_MENU

        elif ctx.state == STATE_DRONE_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_1, pygame.K_KP1) and ctx.player: ctx.player.apply_drone_class(0); ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_2, pygame.K_KP2) and ctx.player: ctx.player.apply_drone_class(1); ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_3, pygame.K_KP3) and ctx.player: ctx.player.apply_drone_class(2); ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_4, pygame.K_KP4) and ctx.player: ctx.player.apply_drone_class(3); ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_5, pygame.K_KP5) and ctx.player: ctx.player.apply_drone_class(4); ctx.state = STATE_SECTOR_SELECT

        elif ctx.state in (STATE_SETTINGS, STATE_CONTROLLER_BINDING, STATE_CONTROLLER_TEST):
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_RETURN):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

        elif ctx.state == STATE_CUSTOM_DIFFICULTY:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                ctx.state = STATE_SETTINGS
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                ctx.state = STATE_SETTINGS
                if input_ctx.save_callback: input_ctx.save_callback()

        elif ctx.state == STATE_PAUSED:
            if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                ctx.state = STATE_PLAYING
            elif event.key == pygame.K_q:
                ctx.state = STATE_MENU

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_cursor = (self.menu_cursor - 1) % 2
                if am: am.play_weapon_switch()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_cursor = (self.menu_cursor + 1) % 2
                if am: am.play_weapon_switch()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.menu_cursor == 0:
                    next_m = input_ctx.get_next_mission_id_callback() if input_ctx.get_next_mission_id_callback else None
                    if next_m:
                        self._set_pending_mission(input_ctx, next_m)
                        if input_ctx.start_mission_callback: input_ctx.start_mission_callback(next_m)
                    else:
                        ctx.state = STATE_SECTOR_SELECT
                elif self.menu_cursor == 1:
                    ctx.state = STATE_HANGAR
                    if am: am.play_click()
            elif event.key in (pygame.K_h, pygame.K_b):
                ctx.state = STATE_HANGAR
                if am: am.play_click()
            elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_cursor = (self.menu_cursor - 1) % 3
                if am: am.play_weapon_switch()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_cursor = (self.menu_cursor + 1) % 3
                if am: am.play_weapon_switch()
            elif event.key == pygame.K_r:
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.menu_cursor == 0:
                    if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
                elif self.menu_cursor == 1:
                    ctx.state = STATE_SECTOR_SELECT
                    if am: am.play_click()
                elif self.menu_cursor == 2:
                    ctx.state = STATE_MENU
                    if am: am.play_click()
            elif event.key == pygame.K_m:
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                ctx.state = STATE_MENU
                if am: am.play_click()

        elif ctx.state == STATE_HANGAR:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_q):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
            elif event.key == pygame.K_s:
                self._set_previous_state(input_ctx, STATE_HANGAR)
                ctx.state = STATE_SETTINGS
            elif event.key == pygame.K_c:
                if ctx.player:
                    ctx.player.cycle_drone_class()
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
                    if am: am.play_powerup()

        elif ctx.state == STATE_SECTOR_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                current_sector = ctx.campaign_state.current_sector_idx + 1
                sector_missions = get_missions_for_sector(current_sector)
                mission_system = input_ctx.mission_system
                selected_mission = next(
                    (
                        mission["id"] for mission in sector_missions
                        if (
                            mission_system
                            and hasattr(mission_system, "get_mission_state")
                            and mission_system.get_mission_state(ctx, mission["id"]) != "locked"
                        )
                        or (
                            (not mission_system or not hasattr(mission_system, "get_mission_state"))
                            and mission["id"] in ctx.campaign_state.unlocked_missions
                        )
                    ),
                    None,
                )
                if selected_mission:
                    self._set_pending_mission(input_ctx, selected_mission)
                    ctx.state = STATE_MISSION_BRIEFING
                    if am: am.play_powerup()
            elif event.key == pygame.K_h:
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_s:
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_SETTINGS

        elif ctx.state == STATE_MISSION_BRIEFING:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if input_ctx.start_mission_callback:
                    input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state == STATE_PLAYING:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
                if ctx.player:
                    slot_index = event.key - pygame.K_1
                    previous_weapon = ctx.player.active_weapon
                    ctx.player.select_weapon(slot_index)
                    if ctx.player.active_weapon != previous_weapon and am:
                        am.play_weapon_switch()
            elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                ctx.state = STATE_PAUSED
                if am: am.stop_engine_sound()

        return True

    def _handle_mouse_click(self, mx: int, my: int, input_ctx: InputHandlingContext):
        """Processes mouse clicks across UI screens."""
        ctx = input_ctx.context
        cache = input_ctx.ui_rects_cache
        am = input_ctx.audio_manager
        if not cache:
            return

        if ctx.state == STATE_MENU:
            if ("play" in cache and cache["play"].collidepoint(mx, my)) or ("start" in cache and cache["start"].collidepoint(mx, my)):
                ctx.state = STATE_DRONE_SELECT
                if am: am.play_powerup()
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_HANGAR
                if am: am.play_click()
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
            elif ("exit" in cache and cache["exit"].collidepoint(mx, my)) or ("quit" in cache and cache["quit"].collidepoint(mx, my)):
                if input_ctx.quit_callback: input_ctx.quit_callback()

        elif ctx.state == STATE_DRONE_SELECT:
            drone_keys = ["striker", "phantom", "titan", "specter", "tempest"]
            if "drones" in cache and isinstance(cache["drones"], dict):
                for idx, d_rect in cache["drones"].items():
                    if d_rect and d_rect.collidepoint(mx, my):
                        if idx < len(drone_keys):
                            ctx.selected_drone = drone_keys[idx]
                            if ctx.player:
                                ctx.player.apply_drone_class(idx)
                                ctx.selected_drone_override = ctx.player.drone_class_id
                            if am: am.play_powerup()
                            self.menu_cursor = 0
                            ctx.state = STATE_SECTOR_SELECT
                            return
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_MENU
                if am: am.play_click()

        elif ctx.state == STATE_SAVE_SELECT:
            for i in range(3):
                del_key = f"del_{i}"
                if del_key in cache and cache[del_key] and cache[del_key].collidepoint(mx, my):
                    if input_ctx.delete_save_slot_callback:
                        input_ctx.delete_save_slot_callback(i)
                    if am: am.play_click()
                    return
                slot_key = f"slot_{i}"
                if slot_key in cache and cache[slot_key] and cache[slot_key].collidepoint(mx, my):
                    if input_ctx.select_save_slot_callback:
                        input_ctx.select_save_slot_callback(i + 1)
                    ctx.state = STATE_MENU
                    if am: am.play_powerup()
                    return
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                if input_ctx.quit_callback: input_ctx.quit_callback()

        elif ctx.state == STATE_SECTOR_SELECT:
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_MENU
                if am: am.play_click()
                return
            if "hangar" in cache and cache["hangar"] and cache["hangar"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_HANGAR
                if am: am.play_click()
                return
            if "settings" in cache and cache["settings"] and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
                return
            if "exit" in cache and cache["exit"] and cache["exit"].collidepoint(mx, my):
                if input_ctx.quit_callback: input_ctx.quit_callback()
                return
            if "diff_rect" in cache and cache["diff_rect"] and cache["diff_rect"].collidepoint(mx, my):
                ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()
                return
            if "sectors" in cache and isinstance(cache["sectors"], dict):
                for s_id, s_rect in cache["sectors"].items():
                    if s_rect and s_rect.collidepoint(mx, my):
                        ctx.campaign_state.set_current_sector_and_stage(s_id - 1, ctx.current_sub_level)
                        if am: am.play_weapon_switch()
                        return
            if "missions" in cache and isinstance(cache["missions"], dict):
                for m_id, m_rect in cache["missions"].items():
                    if m_rect and m_rect.collidepoint(mx, my):
                        self._set_pending_mission(input_ctx, m_id)
                        ctx.state = STATE_MISSION_BRIEFING
                        if am: am.play_powerup()
                        return

        elif ctx.state == STATE_MISSION_BRIEFING:
            if ("start" in cache and cache["start"] and cache["start"].collidepoint(mx, my)) or \
               ("launch" in cache and cache["launch"] and cache["launch"].collidepoint(mx, my)) or \
               ("deploy" in cache and cache["deploy"] and cache["deploy"].collidepoint(mx, my)):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()
            elif "exit" in cache and cache["exit"] and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU
                if am: am.play_click()

        elif ctx.state == STATE_HANGAR:
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
                if am: am.play_click()
            elif "settings" in cache and cache["settings"] and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_HANGAR)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
            elif "exit" in cache and cache["exit"] and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU
                if am: am.play_click()
            elif "upgrades" in cache and isinstance(cache["upgrades"], dict):
                for u_id, u_rect in cache["upgrades"].items():
                    if u_rect and u_rect.collidepoint(mx, my):
                        if input_ctx.buy_upgrade_callback: input_ctx.buy_upgrade_callback(u_id)
                        return
            if ("drone" in cache and cache["drone"] and cache["drone"].collidepoint(mx, my)) or \
               ("chassis" in cache and cache["chassis"] and cache["chassis"].collidepoint(mx, my)) or \
               ("chassis_card" in cache and cache["chassis_card"] and cache["chassis_card"].collidepoint(mx, my)) or \
               ("preview_box" in cache and cache["preview_box"] and cache["preview_box"].collidepoint(mx, my)):
                if ctx.player:
                    ctx.player.cycle_drone_class()
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
                    if am: am.play_powerup()

        elif ctx.state == STATE_SETTINGS:
            if "fullscreen" in cache and cache["fullscreen"] and cache["fullscreen"].collidepoint(mx, my):
                if input_ctx.toggle_fullscreen_callback: input_ctx.toggle_fullscreen_callback()
            elif "crt" in cache and cache["crt"] and cache["crt"].collidepoint(mx, my):
                ctx.show_crt = not ctx.show_crt
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()
            elif "sfx" in cache and cache["sfx"] and cache["sfx"].collidepoint(mx, my):
                if am:
                    am.set_sound_enabled(not am.sound_enabled)
                if input_ctx.save_callback: input_ctx.save_callback()
            elif "diff" in cache and cache["diff"] and cache["diff"].collidepoint(mx, my):
                ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()
            elif "controller" in cache and cache["controller"] and cache["controller"].collidepoint(mx, my):
                ctx.state = STATE_CUSTOM_DIFFICULTY
                if am: am.play_click()
            elif "config" in cache and cache["config"] and cache["config"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_BINDING
                if am: am.play_click()
            elif "test" in cache and cache["test"] and cache["test"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_TEST
                if am: am.play_click()
            elif "reset" in cache and cache["reset"] and cache["reset"].collidepoint(mx, my):
                if input_ctx.reset_progress_callback:
                    input_ctx.reset_progress_callback()
                if am: am.play_click()
            elif "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT
                if am: am.play_click()

        elif ctx.state == STATE_PAUSED:
            if "resume" in cache and cache["resume"] and cache["resume"].collidepoint(mx, my):
                ctx.state = STATE_PLAYING
                if am: am.play_click()
            elif "diff" in cache and cache["diff"] and cache["diff"].collidepoint(mx, my):
                ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()
            elif "crt" in cache and cache["crt"] and cache["crt"].collidepoint(mx, my):
                ctx.show_crt = not ctx.show_crt
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()
            elif "sfx" in cache and cache["sfx"] and cache["sfx"].collidepoint(mx, my):
                if am:
                    am.set_sound_enabled(not am.sound_enabled)
                if input_ctx.save_callback: input_ctx.save_callback()
            elif "hangar" in cache and cache["hangar"] and cache["hangar"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_PAUSED)
                ctx.state = STATE_HANGAR
                if am: am.play_click()
            elif "map" in cache and cache["map"] and cache["map"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_PAUSED)
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()
            elif "settings" in cache and cache["settings"] and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_PAUSED)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
            elif "restart" in cache and cache["restart"] and cache["restart"].collidepoint(mx, my):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif ("exit" in cache and cache["exit"] and cache["exit"].collidepoint(mx, my)) or \
                 ("menu" in cache and cache["menu"] and cache["menu"].collidepoint(mx, my)) or \
                 ("quit" in cache and cache["quit"] and cache["quit"].collidepoint(mx, my)):
                ctx.state = STATE_MENU
                if am: am.play_click()

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if "next" in cache and cache["next"] and cache["next"].collidepoint(mx, my):
                next_m = input_ctx.get_next_mission_id_callback() if input_ctx.get_next_mission_id_callback else None
                if next_m:
                    self._set_pending_mission(input_ctx, next_m)
                    if input_ctx.start_mission_callback: input_ctx.start_mission_callback(next_m)
                else:
                    ctx.state = STATE_SECTOR_SELECT
            elif "hangar" in cache and cache["hangar"] and cache["hangar"].collidepoint(mx, my):
                ctx.state = STATE_HANGAR
                if am: am.play_click()
            elif ("menu" in cache and cache["menu"] and cache["menu"].collidepoint(mx, my)) or \
                 ("map" in cache and cache["map"] and cache["map"].collidepoint(mx, my)) or \
                 ("back" in cache and cache["back"] and cache["back"].collidepoint(mx, my)):
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if "retry" in cache and cache["retry"] and cache["retry"].collidepoint(mx, my):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif "map" in cache and cache["map"] and cache["map"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()
            elif "hangar" in cache and cache["hangar"] and cache["hangar"].collidepoint(mx, my):
                ctx.state = STATE_HANGAR
                if am: am.play_click()
            elif ("menu" in cache and cache["menu"] and cache["menu"].collidepoint(mx, my)) or \
                 ("back" in cache and cache["back"] and cache["back"].collidepoint(mx, my)) or \
                 ("exit" in cache and cache["exit"] and cache["exit"].collidepoint(mx, my)) or \
                 ("quit" in cache and cache["quit"] and cache["quit"].collidepoint(mx, my)):
                ctx.state = STATE_MENU
                if am: am.play_click()

        elif ctx.state == STATE_CUSTOM_DIFFICULTY:
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
            elif "reset" in cache and cache["reset"] and cache["reset"].collidepoint(mx, my):
                from src.data.game_data import DEFAULT_CUSTOM_DIFFICULTY
                ctx.custom_difficulty_settings = dict(DEFAULT_CUSTOM_DIFFICULTY)
                if input_ctx.save_callback: input_ctx.save_callback()
                if am: am.play_click()

        elif ctx.state == STATE_CONTROLLER_TEST:
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
            elif "bind" in cache and cache["bind"] and cache["bind"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_BINDING
                if am: am.play_click()

        elif ctx.state == STATE_CONTROLLER_BINDING:
            if "back" in cache and cache["back"] and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SETTINGS
                if am: am.play_click()

    def _update_slider_drag(self, mx: int, input_ctx: InputHandlingContext):
        """Updates custom difficulty slider values when dragging."""
        cache = input_ctx.ui_rects_cache
        sliders = [("hp_mult", 0.5, 3.0), ("speed_mult", 0.5, 2.0),
                   ("rate_mult", 0.5, 2.5), ("dmg_mult", 0.5, 3.0),
                   ("scrap_mult", 0.25, 3.0)]
        if 0 <= self.custom_difficulty_dragging < len(sliders):
            key, min_v, max_v = sliders[self.custom_difficulty_dragging]
            if key in cache:
                rect = cache[key]
                norm = max(0.0, min(1.0, (mx - rect.left) / max(1.0, rect.width)))
                val = round(min_v + norm * (max_v - min_v), 2)
                input_ctx.context.custom_difficulty_settings[key] = val

    def _handle_controller_button_down(self, event, input_ctx: InputHandlingContext) -> bool:
        """Processes raw controller button clicks for navigation and actions."""
        ctx = input_ctx.context
        im = input_ctx.input_manager
        if not im:
            return True

        js_id = getattr(event, "instance_id", 0)
        js = im.connected_joysticks.get(js_id)
        if not js:
            return True

        btn = event.button
        mgr = getattr(im, "mapping_manager", None)
        if not mgr:
            return True

        profile = mgr.get_or_create_profile(js)

        # Binding Wizard interception
        if ctx.state == STATE_CONTROLLER_BINDING and self.binding_waiting and self.binding_action:
            profile.set_button(self.binding_action, btn)
            mgr.save_profiles()
            self.binding_waiting = False
            self.binding_action = None
            if input_ctx.audio_manager: input_ctx.audio_manager.play_buy()
            return True

        is_fullscreen = False
        if hasattr(profile, "is_action_button"):
            is_fullscreen = profile.is_action_button(btn, ACTION_FULLSCREEN)
        elif hasattr(profile, "button_map") and isinstance(profile.button_map, dict):
            is_fullscreen = (profile.button_map.get(ACTION_FULLSCREEN) == btn)

        if is_fullscreen:
            if input_ctx.toggle_fullscreen_callback:
                input_ctx.toggle_fullscreen_callback()
            return True

        return True

    def update_controller_navigation(self, dt: float, input_ctx_or_game: Any):
        """Updates D-pad cursor movement, slider tuning, and button triggers across all menus."""
        input_ctx = self._resolve_input_context(input_ctx_or_game)
        ctx = input_ctx.context
        if ctx.state == STATE_PLAYING:
            return

        im = input_ctx.input_manager
        if not im:
            return
        js = im.active_joystick
        keyboard_navigation = im.active_device == DEVICE_KEYBOARD_MOUSE
        if (
            not keyboard_navigation
            and (not js or not im.mapping_manager or not getattr(im, "enabled", True))
        ):
            return

        trig = getattr(im, "actions_triggered", {})

        confirm = trig.get(ACTION_CONFIRM, False)
        cancel = trig.get(ACTION_CANCEL, False)
        pause = trig.get(ACTION_PAUSE, False)
        sec_map = trig.get(ACTION_SECTOR_MAP, False)
        hangar_bay = trig.get(ACTION_HANGAR_BAY, False)
        cycle_class = trig.get(ACTION_CYCLE_CLASS, False)
        weapon_next = trig.get(ACTION_WEAPON_NEXT, False)
        weapon_prev = trig.get(ACTION_WEAPON_PREV, False)

        d_up = False
        d_down = False
        d_left = False
        d_right = False

        if keyboard_navigation:
            nav = getattr(im, "navigation_triggered", {})
            d_up = nav.get("up", False)
            d_down = nav.get("down", False)
            d_left = nav.get("left", False)
            d_right = nav.get("right", False)
            self.dpad_repeat_timer = 0.0
            self.dpad_last_state = {"up": False, "down": False, "left": False, "right": False}
        else:
            dpad = im.mapping_manager.get_dpad_input(js)
            any_dir = dpad.get("up", False) or dpad.get("down", False) or dpad.get("left", False) or dpad.get("right", False)
            if any_dir:
                if not any(self.dpad_last_state.values()):
                    d_up = dpad.get("up", False)
                    d_down = dpad.get("down", False)
                    d_left = dpad.get("left", False)
                    d_right = dpad.get("right", False)
                    self.dpad_repeat_timer = 0.35
                else:
                    self.dpad_repeat_timer -= dt
                    if self.dpad_repeat_timer <= 0.0:
                        d_up = dpad.get("up", False)
                        d_down = dpad.get("down", False)
                        d_left = dpad.get("left", False)
                        d_right = dpad.get("right", False)
                        self.dpad_repeat_timer = 0.18
            else:
                self.dpad_repeat_timer = 0.0

            self.dpad_last_state = {"up": dpad.get("up", False), "down": dpad.get("down", False), "left": dpad.get("left", False), "right": dpad.get("right", False)}

        # STATE-SPECIFIC NAVIGATION
        am = input_ctx.audio_manager

        if ctx.state == STATE_SAVE_SELECT:
            if trig.get(ACTION_SELECT_SLOT_1):
                if input_ctx.select_save_slot_callback:
                    input_ctx.select_save_slot_callback(1)
                ctx.state = STATE_MENU
                self.menu_cursor = 0
                if am: am.play_powerup()
                return
            elif trig.get(ACTION_SELECT_SLOT_2):
                if input_ctx.select_save_slot_callback:
                    input_ctx.select_save_slot_callback(2)
                ctx.state = STATE_MENU
                self.menu_cursor = 0
                if am: am.play_powerup()
                return
            elif trig.get(ACTION_SELECT_SLOT_3):
                if input_ctx.select_save_slot_callback:
                    input_ctx.select_save_slot_callback(3)
                ctx.state = STATE_MENU
                self.menu_cursor = 0
                if am: am.play_powerup()
                return

            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 4
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 4
                if am: am.play_weapon_switch()

            if confirm or pause:
                if self.menu_cursor < 3:
                    slot_num = self.menu_cursor + 1
                    if input_ctx.select_save_slot_callback:
                        input_ctx.select_save_slot_callback(slot_num)
                    ctx.state = STATE_MENU
                    self.menu_cursor = 0
                    if am: am.play_powerup()
                else:
                    if input_ctx.quit_callback:
                        input_ctx.quit_callback()
            elif cancel:
                if input_ctx.quit_callback:
                    input_ctx.quit_callback()

        elif ctx.state == STATE_MENU:
            if trig.get(ACTION_SETTINGS):
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
                return

            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 4
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 4
                if am: am.play_weapon_switch()

            if confirm:
                if self.menu_cursor == 0:
                    ctx.state = STATE_DRONE_SELECT
                    if am: am.play_powerup()
                elif self.menu_cursor == 1:
                    self._set_previous_state(input_ctx, STATE_MENU)
                    ctx.state = STATE_HANGAR
                elif self.menu_cursor == 2:
                    self._set_previous_state(input_ctx, STATE_MENU)
                    ctx.state = STATE_SETTINGS
                elif self.menu_cursor == 3:
                    if input_ctx.quit_callback:
                        input_ctx.quit_callback()
            elif cancel:
                if input_ctx.quit_callback:
                    input_ctx.quit_callback()
            elif hangar_bay:
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_HANGAR

        elif ctx.state == STATE_DRONE_SELECT:
            drone_keys = ["striker", "phantom", "titan", "specter", "tempest"]
            for slot_idx, slot_act in enumerate([ACTION_SELECT_SLOT_1, ACTION_SELECT_SLOT_2, ACTION_SELECT_SLOT_3, ACTION_SELECT_SLOT_4, ACTION_SELECT_SLOT_5]):
                if trig.get(slot_act):
                    ctx.selected_drone = drone_keys[slot_idx]
                    if ctx.player:
                        ctx.player.apply_drone_class(slot_idx)
                        ctx.selected_drone_override = ctx.player.drone_class_id
                    if am: am.play_powerup()
                    self.menu_cursor = 0
                    ctx.state = STATE_SECTOR_SELECT
                    return

            if d_left or weapon_prev:
                if self.menu_cursor == 5:
                    self.menu_cursor = 0
                else:
                    self.menu_cursor = (self.menu_cursor - 1) % 5
                if am: am.play_weapon_switch()
            elif d_right or weapon_next:
                if self.menu_cursor == 5:
                    self.menu_cursor = 0
                else:
                    self.menu_cursor = (self.menu_cursor + 1) % 5
                if am: am.play_weapon_switch()
            elif d_down:
                if self.menu_cursor < 5:
                    self.menu_cursor = 5
                    if am: am.play_weapon_switch()
            elif d_up:
                if self.menu_cursor == 5:
                    self.menu_cursor = 0
                else:
                    self.menu_cursor = (self.menu_cursor - 1) % 5
                if am: am.play_weapon_switch()

            if self.menu_cursor < 5:
                ctx.selected_drone = drone_keys[self.menu_cursor]
                if ctx.player:
                    ctx.player.apply_drone_class(self.menu_cursor)
                    ctx.selected_drone_override = ctx.player.drone_class_id

            if confirm or pause:
                if self.menu_cursor < 5:
                    ctx.selected_drone = drone_keys[self.menu_cursor]
                    if ctx.player:
                        ctx.player.apply_drone_class(self.menu_cursor)
                        ctx.selected_drone_override = ctx.player.drone_class_id
                    if am: am.play_powerup()
                    self.menu_cursor = 0
                    ctx.state = STATE_SECTOR_SELECT
                else:
                    ctx.state = STATE_MENU
            elif cancel:
                ctx.state = STATE_MENU

        elif ctx.state == STATE_SECTOR_SELECT:
            if trig.get(ACTION_SETTINGS):
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
                return

            cur_sec = ctx.campaign_state.current_sector_idx + 1
            sec_missions = get_missions_for_sector(cur_sec)

            if d_left:
                ctx.campaign_state.set_current_sector_and_stage(max(0, cur_sec - 1), ctx.current_sub_level)
                if am: am.play_weapon_switch()
            elif d_right:
                ctx.campaign_state.set_current_sector_and_stage(min(4, cur_sec + 1), ctx.current_sub_level)
                if am: am.play_weapon_switch()

            if confirm:
                target_m = None
                ms = input_ctx.mission_system
                for m in sec_missions:
                    if ms and hasattr(ms, "get_mission_state"):
                        if ms.get_mission_state(ctx, m["id"]) != "locked":
                            target_m = m["id"]
                            break
                    elif m["id"] in ctx.campaign_state.unlocked_missions:
                        target_m = m["id"]
                        break
                if not target_m and sec_missions:
                    target_m = sec_missions[0]["id"]
                if target_m:
                    self._set_pending_mission(input_ctx, target_m)
                    ctx.state = STATE_MISSION_BRIEFING
                    if am: am.play_powerup()
            elif cancel:
                ctx.state = STATE_MENU
            elif hangar_bay:
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_HANGAR

        elif ctx.state == STATE_MISSION_BRIEFING:
            if confirm or pause:
                if input_ctx.start_mission_callback:
                    input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif cancel or sec_map:
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state == STATE_HANGAR:
            if trig.get(ACTION_SETTINGS):
                self._set_previous_state(input_ctx, STATE_HANGAR)
                ctx.state = STATE_SETTINGS
                if am: am.play_click()
                return
            if (cycle_class or trig.get(ACTION_CYCLE_CLASS)) and ctx.player:
                ctx.player.cycle_drone_class(1)
                if am: am.play_powerup()
            elif d_up:
                if self.menu_cursor in (0, 1):
                    self.menu_cursor = self.menu_cursor + 4
                elif self.menu_cursor in (2, 3):
                    self.menu_cursor -= 2
                else:
                    self.menu_cursor = 2 if self.menu_cursor in (4, 5) else 3
                if am: am.play_weapon_switch()
            elif d_down:
                if self.menu_cursor in (0, 1):
                    self.menu_cursor += 2
                elif self.menu_cursor in (2, 3):
                    self.menu_cursor = 4 if self.menu_cursor == 2 else 5
                else:
                    self.menu_cursor = 0 if self.menu_cursor in (4, 5) else 1
                if am: am.play_weapon_switch()
            elif d_left:
                if self.menu_cursor in (0, 1):
                    self.menu_cursor = 1 if self.menu_cursor == 0 else 0
                elif self.menu_cursor in (2, 3):
                    self.menu_cursor = 3 if self.menu_cursor == 2 else 2
                else:
                    self.menu_cursor = max(4, self.menu_cursor - 1)
                if am: am.play_weapon_switch()
            elif d_right:
                if self.menu_cursor in (0, 1):
                    self.menu_cursor = 1 if self.menu_cursor == 0 else 0
                elif self.menu_cursor in (2, 3):
                    self.menu_cursor = 3 if self.menu_cursor == 2 else 2
                else:
                    self.menu_cursor = min(7, self.menu_cursor + 1)
                if am: am.play_weapon_switch()
            elif confirm:
                if self.menu_cursor < 4:
                    categories = ["hull", "energy", "weapon", "mobility"]
                    cat = categories[self.menu_cursor]
                    if input_ctx.buy_upgrade_callback:
                        input_ctx.buy_upgrade_callback(cat)
                elif self.menu_cursor == 4:
                    ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
                elif self.menu_cursor == 5 and ctx.player:
                    ctx.player.cycle_drone_class(1)
                    if am: am.play_powerup()
                elif self.menu_cursor == 6:
                    self._set_previous_state(input_ctx, STATE_HANGAR)
                    ctx.state = STATE_SETTINGS
                elif self.menu_cursor == 7:
                    if input_ctx.quit_callback:
                        input_ctx.quit_callback()
            elif cancel or pause or hangar_bay:
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT

        elif ctx.state == STATE_SETTINGS:
            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 9
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 9
                if am: am.play_weapon_switch()
            elif d_left:
                if self.menu_cursor == 3:
                    ctx.difficulty_mode = (ctx.difficulty_mode - 1) % 5
                    if input_ctx.save_callback: input_ctx.save_callback()
            elif d_right:
                if self.menu_cursor == 3:
                    ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                    if input_ctx.save_callback: input_ctx.save_callback()

            if confirm:
                if self.menu_cursor == 0:
                    if input_ctx.toggle_fullscreen_callback:
                        input_ctx.toggle_fullscreen_callback()
                elif self.menu_cursor == 1:
                    ctx.show_crt = not ctx.show_crt
                    if input_ctx.save_callback: input_ctx.save_callback()
                elif self.menu_cursor == 2:
                    if am:
                        am.set_sound_enabled(not am.sound_enabled)
                    if input_ctx.save_callback: input_ctx.save_callback()
                elif self.menu_cursor == 3:
                    ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                    if input_ctx.save_callback: input_ctx.save_callback()
                elif self.menu_cursor == 4:
                    ctx.state = STATE_CUSTOM_DIFFICULTY
                elif self.menu_cursor == 5:
                    ctx.state = STATE_CONTROLLER_BINDING
                elif self.menu_cursor == 6:
                    ctx.state = STATE_CONTROLLER_TEST
                elif self.menu_cursor == 7:
                    # Reset
                    pass
                elif self.menu_cursor == 8:
                    ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT
            elif cancel or pause:
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

        elif ctx.state == STATE_PAUSED:
            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 5
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 5
                if am: am.play_weapon_switch()

            if confirm or pause:
                if self.menu_cursor == 0:
                    ctx.state = STATE_PLAYING
                elif self.menu_cursor == 1:
                    self._set_previous_state(input_ctx, STATE_PAUSED)
                    ctx.state = STATE_SETTINGS
                elif self.menu_cursor == 2:
                    if input_ctx.start_mission_callback:
                        input_ctx.start_mission_callback(input_ctx.pending_mission_id)
                elif self.menu_cursor == 3:
                    self._set_previous_state(input_ctx, STATE_PLAYING)
                    ctx.state = STATE_SECTOR_SELECT
                elif self.menu_cursor == 4:
                    ctx.state = STATE_MENU
            elif cancel:
                ctx.state = STATE_PLAYING

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 3
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 3
                if am: am.play_weapon_switch()

            if confirm:
                if self.menu_cursor == 0:
                    if ctx.state == STATE_VICTORY and input_ctx.start_new_game_plus_callback:
                        input_ctx.start_new_game_plus_callback()
                    elif ctx.state == STATE_LEVEL_CLEAR and input_ctx.start_next_stage_callback:
                        input_ctx.start_next_stage_callback()
                    else:
                        next_m = input_ctx.get_next_mission_id_callback() if input_ctx.get_next_mission_id_callback else None
                        if next_m:
                            self._set_pending_mission(input_ctx, next_m)
                            if input_ctx.start_mission_callback:
                                input_ctx.start_mission_callback(next_m)
                        else:
                            ctx.state = STATE_VICTORY
                elif self.menu_cursor == 1:
                    self._set_previous_state(input_ctx, ctx.state)
                    ctx.state = STATE_HANGAR
                elif self.menu_cursor == 2:
                    ctx.state = STATE_SECTOR_SELECT
            elif cancel:
                ctx.state = STATE_SECTOR_SELECT
            elif hangar_bay:
                self._set_previous_state(input_ctx, ctx.state)
                ctx.state = STATE_HANGAR

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if d_up:
                self.menu_cursor = (self.menu_cursor - 1) % 3
                if am: am.play_weapon_switch()
            elif d_down:
                self.menu_cursor = (self.menu_cursor + 1) % 3
                if am: am.play_weapon_switch()

            if confirm:
                if self.menu_cursor == 0:
                    if input_ctx.start_mission_callback:
                        input_ctx.start_mission_callback(input_ctx.pending_mission_id)
                elif self.menu_cursor == 1:
                    ctx.state = STATE_SECTOR_SELECT
                    if am: am.play_click()
                elif self.menu_cursor == 2:
                    ctx.state = STATE_MENU
                    if am: am.play_click()
            elif cancel:
                ctx.state = STATE_MENU
                if am: am.play_click()
            elif sec_map:
                ctx.state = STATE_SECTOR_SELECT
                if am: am.play_click()

        elif ctx.state in (STATE_CONTROLLER_TEST, STATE_CONTROLLER_BINDING):
            if cancel or pause:
                ctx.state = STATE_SETTINGS
