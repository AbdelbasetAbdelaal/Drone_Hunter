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
    InputManager, InputContext, ACTION_FULLSCREEN
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
                if event.key == pygame.K_F11:
                    if input_ctx.toggle_fullscreen_callback:
                        input_ctx.toggle_fullscreen_callback()
                    continue
                elif event.key == pygame.K_F2:
                    ctx.show_crt = not ctx.show_crt
                    if input_ctx.save_callback:
                        input_ctx.save_callback()
                    continue

                if not self._handle_keyboard_menu_navigation(event, input_ctx):
                    if input_ctx.quit_callback:
                        input_ctx.quit_callback()
                    return False

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
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                next_m = input_ctx.get_next_mission_id_callback() if input_ctx.get_next_mission_id_callback else None
                if next_m:
                    self._set_pending_mission(input_ctx, next_m)
                    if input_ctx.start_mission_callback: input_ctx.start_mission_callback(next_m)
                else:
                    ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_h, pygame.K_b):
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_ESCAPE:
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif event.key == pygame.K_ESCAPE:
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state == STATE_HANGAR:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_q):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
            elif event.key == pygame.K_s:
                self._set_previous_state(input_ctx, STATE_HANGAR)
                ctx.state = STATE_SETTINGS

        elif ctx.state == STATE_SECTOR_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                ctx.state = STATE_MENU
            elif event.key == pygame.K_h:
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_s:
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_SETTINGS

        elif ctx.state == STATE_PLAYING:
            if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                ctx.state = STATE_PAUSED
                if am: am.stop_engine_sound()
            elif event.key == pygame.K_c:
                if ctx.player:
                    ctx.player.cycle_drone_class()
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
            elif event.key == pygame.K_v:
                if ctx.player:
                    ctx.player.cycle_visual_skin()
                    ctx.selected_skin = ctx.player.skin_id
                    ctx.selected_skin_override = ctx.selected_skin
                    if input_ctx.save_callback: input_ctx.save_callback()

        return True

    def _handle_mouse_click(self, mx: int, my: int, input_ctx: InputHandlingContext):
        """Processes mouse clicks across UI screens."""
        ctx = input_ctx.context
        cache = input_ctx.ui_rects_cache
        am = input_ctx.audio_manager
        if not cache:
            return

        if ctx.state == STATE_MENU:
            if "start" in cache and cache["start"].collidepoint(mx, my):
                ctx.state = STATE_DRONE_SELECT
                if am: am.play_powerup()
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_HANGAR
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_MENU)
                ctx.state = STATE_SETTINGS
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                if input_ctx.quit_callback: input_ctx.quit_callback()

        elif ctx.state == STATE_SAVE_SELECT:
            for i in range(3):
                key = f"slot_{i}"
                if key in cache and cache[key].collidepoint(mx, my):
                    if input_ctx.select_save_slot_callback: input_ctx.select_save_slot_callback(i)
                    ctx.state = STATE_MENU
                    return
            if "back" in cache and cache["back"].collidepoint(mx, my):
                if input_ctx.quit_callback: input_ctx.quit_callback()

        elif ctx.state == STATE_SECTOR_SELECT:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_MENU
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_HANGAR
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_SECTOR_SELECT)
                ctx.state = STATE_SETTINGS
            elif "missions" in cache:
                for m_id, m_rect in cache["missions"].items():
                    if m_rect.collidepoint(mx, my):
                        self._set_pending_mission(input_ctx, m_id)
                        ctx.state = STATE_MISSION_BRIEFING
                        return
            elif "sectors" in cache:
                for idx, s_rect in enumerate(cache["sectors"]):
                    if s_rect.collidepoint(mx, my) and ctx.unlocked_sectors[idx]:
                        ctx.current_sector_idx = idx
                        missions = get_missions_for_sector(idx + 1)
                        if missions:
                            self._set_pending_mission(input_ctx, missions[0]["id"])
                            ctx.state = STATE_MISSION_BRIEFING
                        return

        elif ctx.state == STATE_MISSION_BRIEFING:
            if "start" in cache and cache["start"].collidepoint(mx, my):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU

        elif ctx.state == STATE_HANGAR:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_HANGAR)
                ctx.state = STATE_SETTINGS
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU
            elif "upgrades" in cache:
                for u_id, u_rect in cache["upgrades"].items():
                    if u_rect.collidepoint(mx, my):
                        if input_ctx.buy_upgrade_callback: input_ctx.buy_upgrade_callback(u_id)
                        return
            if "drone" in cache and cache["drone"].collidepoint(mx, my):
                if ctx.player:
                    ctx.player.cycle_drone_class()
                    ctx.selected_drone = ctx.player.drone_class
                    if input_ctx.save_callback: input_ctx.save_callback()
            elif "skin" in cache and cache["skin"].collidepoint(mx, my):
                if ctx.player:
                    ctx.player.cycle_visual_skin()
                    ctx.selected_skin = ctx.player.skin_id
                    ctx.selected_skin_override = ctx.selected_skin
                    if input_ctx.save_callback: input_ctx.save_callback()
            elif "skins" in cache:
                skins_items = cache["skins"].items() if isinstance(cache["skins"], dict) else enumerate(cache["skins"])
                for skin_idx, s_rect in skins_items:
                    if hasattr(s_rect, "collidepoint") and s_rect.collidepoint(mx, my):
                        if ctx.player:
                            ctx.player.set_visual_skin(skin_idx)
                            ctx.selected_skin = skin_idx
                            ctx.selected_skin_override = skin_idx
                            if input_ctx.save_callback: input_ctx.save_callback()
                        return

        elif ctx.state == STATE_SETTINGS:
            if "fullscreen" in cache and cache["fullscreen"].collidepoint(mx, my):
                if input_ctx.toggle_fullscreen_callback: input_ctx.toggle_fullscreen_callback()
            elif "crt" in cache and cache["crt"].collidepoint(mx, my):
                ctx.show_crt = not ctx.show_crt
                if input_ctx.save_callback: input_ctx.save_callback()
            elif "sfx" in cache and cache["sfx"].collidepoint(mx, my):
                if am:
                    am.set_sound_enabled(not am.sound_enabled)
                if input_ctx.save_callback: input_ctx.save_callback()
            elif "diff" in cache and cache["diff"].collidepoint(mx, my):
                ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                if input_ctx.save_callback: input_ctx.save_callback()
            elif "controller" in cache and cache["controller"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_TEST
            elif "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = input_ctx.previous_state if input_ctx.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

        elif ctx.state == STATE_PAUSED:
            if "resume" in cache and cache["resume"].collidepoint(mx, my):
                ctx.state = STATE_PLAYING
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                self._set_previous_state(input_ctx, STATE_PAUSED)
                ctx.state = STATE_SETTINGS
            elif "restart" in cache and cache["restart"].collidepoint(mx, my):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif "menu" in cache and cache["menu"].collidepoint(mx, my):
                ctx.state = STATE_MENU

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if "next" in cache and cache["next"].collidepoint(mx, my):
                next_m = input_ctx.get_next_mission_id_callback() if input_ctx.get_next_mission_id_callback else None
                if next_m:
                    self._set_pending_mission(input_ctx, next_m)
                    if input_ctx.start_mission_callback: input_ctx.start_mission_callback(next_m)
                else:
                    ctx.state = STATE_SECTOR_SELECT
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                ctx.state = STATE_HANGAR
            elif "menu" in cache and cache["menu"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if "retry" in cache and cache["retry"].collidepoint(mx, my):
                if input_ctx.start_mission_callback: input_ctx.start_mission_callback(input_ctx.pending_mission_id)
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                ctx.state = STATE_HANGAR
            elif "menu" in cache and cache["menu"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state == STATE_CONTROLLER_TEST:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SETTINGS
            elif "bind" in cache and cache["bind"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_BINDING

        elif ctx.state == STATE_CONTROLLER_BINDING:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SETTINGS

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
        if not js or not im.mapping_manager:
            return

        profile = im.mapping_manager.get_or_create_profile(js)
        dpad = im.mapping_manager.get_dpad_input(js)

        # D-Pad repeat timer
        up_pressed = dpad.get("up", False)
        down_pressed = dpad.get("down", False)
        left_pressed = dpad.get("left", False)
        right_pressed = dpad.get("right", False)

        any_dir = up_pressed or down_pressed or left_pressed or right_pressed
        if not any_dir:
            self.dpad_repeat_timer = 0.0
            self.dpad_last_state = {"up": False, "down": False, "left": False, "right": False}
            return

        self.dpad_repeat_timer -= dt
        triggered_dir = None
        if not self.dpad_last_state.get("up") and up_pressed: triggered_dir = "up"
        elif not self.dpad_last_state.get("down") and down_pressed: triggered_dir = "down"
        elif not self.dpad_last_state.get("left") and left_pressed: triggered_dir = "left"
        elif not self.dpad_last_state.get("right") and right_pressed: triggered_dir = "right"
        elif self.dpad_repeat_timer <= 0.0:
            if up_pressed: triggered_dir = "up"
            elif down_pressed: triggered_dir = "down"
            elif left_pressed: triggered_dir = "left"
            elif right_pressed: triggered_dir = "right"
            self.dpad_repeat_timer = 0.22

        self.dpad_last_state = {"up": up_pressed, "down": down_pressed, "left": left_pressed, "right": right_pressed}

        if triggered_dir:
            if triggered_dir == "up": self.menu_cursor = max(0, self.menu_cursor - 1)
            elif triggered_dir == "down": self.menu_cursor += 1
            if input_ctx.audio_manager: input_ctx.audio_manager.play_click()
