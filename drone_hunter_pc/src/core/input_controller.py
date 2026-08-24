"""
================================================================================
                   DRONE HUNTER 2D - INPUT CONTROLLER
================================================================================
Orchestrates event handling, mouse coordinate projection, context-aware input
routing, and controller D-pad menu navigation across all game screens.
"""

import math
import pygame
from typing import Optional, Dict, Any, Tuple

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
from src.input import (
    InputContext,
    ACTION_CONFIRM, ACTION_CANCEL, ACTION_SECTOR_MAP, ACTION_HANGAR_BAY,
    ACTION_CYCLE_SKIN, ACTION_FRONT_TOP, ACTION_FRONT_BOTTOM, ACTION_CYCLE_CLASS,
    ACTION_PAUSE, ACTION_FULLSCREEN, ACTION_FIRE_PRIMARY, ACTION_EMP,
    ACTION_ULTIMATE, ACTION_ROLL, ACTION_WEAPON_NEXT, ACTION_WEAPON_PREV,
    ACTION_CLOAK
)
from src.data.mission_data import get_missions_for_sector, get_mission_data


class InputController:
    """Coordinates event processing, input context routing, and UI navigation."""

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

    def handle_events(self, game) -> bool:
        """Processes all pending SDL/Pygame events and dispatches to appropriate handlers.
        Returns False if game should quit, True otherwise."""
        ctx = game.context
        game.input_manager.set_context(self.get_current_input_context(ctx.state))
        events = pygame.event.get()
        game.input_manager.process_events(events)

        for event in events:
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                if not getattr(game, "is_fullscreen", False):
                    game.win_w, game.win_h = event.w, event.h
                    game.screen = pygame.display.set_mode((game.win_w, game.win_h), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                    continue
                elif event.key == pygame.K_F2:
                    ctx.show_crt = not ctx.show_crt
                    game.save_progress()
                    continue

                if not self._handle_keyboard_menu_navigation(event, game):
                    return False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self.get_canvas_mouse_pos(game.win_w, game.win_h, screen_pos=event.pos)
                self._handle_mouse_click(mx, my, game)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.custom_difficulty_dragging = -1

            elif event.type == pygame.MOUSEMOTION:
                if self.custom_difficulty_dragging >= 0 and ctx.state == STATE_CUSTOM_DIFFICULTY:
                    mx, _ = self.get_canvas_mouse_pos(game.win_w, game.win_h, screen_pos=event.pos)
                    self._update_slider_drag(mx, game)

            elif event.type == pygame.JOYBUTTONDOWN:
                if not self._handle_controller_button_down(event, game):
                    return False

        return True

    def _handle_keyboard_menu_navigation(self, event, game) -> bool:
        """Handles keyboard shortcut and keydown events for menu screens."""
        ctx = game.context
        if ctx.state == STATE_MENU:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                ctx.state = STATE_DRONE_SELECT
                if game.audio_manager: game.audio_manager.play_powerup()
            elif event.key == pygame.K_h:
                game.previous_state = STATE_MENU
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_s:
                game.previous_state = STATE_MENU
                ctx.state = STATE_SETTINGS
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                return False

        elif ctx.state == STATE_SAVE_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return False
            elif event.key in (pygame.K_1, pygame.K_KP1):
                game.select_save_slot(0)
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_2, pygame.K_KP2):
                game.select_save_slot(1)
                ctx.state = STATE_MENU
            elif event.key in (pygame.K_3, pygame.K_KP3):
                game.select_save_slot(2)
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
                ctx.state = game.previous_state if game.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

        elif ctx.state == STATE_CUSTOM_DIFFICULTY:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_BACKSPACE):
                ctx.state = STATE_SETTINGS
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                ctx.state = STATE_SETTINGS
                game.save_progress()

        elif ctx.state == STATE_PAUSED:
            if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                ctx.state = STATE_PLAYING
            elif event.key == pygame.K_q:
                ctx.state = STATE_MENU

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                next_m = game.get_next_mission_id()
                if next_m:
                    game.pending_mission_id = next_m
                    game.start_phase5_mission(next_m)
                else:
                    ctx.state = STATE_SECTOR_SELECT
            elif event.key in (pygame.K_h, pygame.K_b):
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_ESCAPE:
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                game.start_phase5_mission(game.pending_mission_id)
            elif event.key == pygame.K_ESCAPE:
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state == STATE_HANGAR:
            if event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_q):
                ctx.state = game.previous_state if game.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
            elif event.key == pygame.K_s:
                game.previous_state = STATE_HANGAR
                ctx.state = STATE_SETTINGS

        elif ctx.state == STATE_SECTOR_SELECT:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                ctx.state = STATE_MENU
            elif event.key == pygame.K_h:
                game.previous_state = STATE_SECTOR_SELECT
                ctx.state = STATE_HANGAR
            elif event.key == pygame.K_s:
                game.previous_state = STATE_SECTOR_SELECT
                ctx.state = STATE_SETTINGS

        elif ctx.state == STATE_PLAYING:
            if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                ctx.state = STATE_PAUSED
                if game.audio_manager: game.audio_manager.stop_engine_sound()
            elif event.key == pygame.K_c:
                ctx.player.cycle_drone_class()
                ctx.selected_drone = ctx.player.drone_class
                game.save_progress()
            elif event.key == pygame.K_v:
                ctx.player.cycle_visual_skin()
                ctx.selected_skin = ctx.player.skin_id
                ctx.selected_skin_override = ctx.selected_skin
                game.save_progress()

        return True

    def _handle_mouse_click(self, mx: int, my: int, game):
        """Processes mouse clicks across UI screens."""
        ctx = game.context
        cache = game.ui_rects_cache
        if not cache:
            return

        if ctx.state == STATE_MENU:
            if "start" in cache and cache["start"].collidepoint(mx, my):
                ctx.state = STATE_DRONE_SELECT
                if game.audio_manager: game.audio_manager.play_powerup()
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                game.previous_state = STATE_MENU
                ctx.state = STATE_HANGAR
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                game.previous_state = STATE_MENU
                ctx.state = STATE_SETTINGS
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                game.running = False

        elif ctx.state == STATE_SAVE_SELECT:
            for i in range(3):
                key = f"slot_{i}"
                if key in cache and cache[key].collidepoint(mx, my):
                    game.select_save_slot(i)
                    ctx.state = STATE_MENU
                    return
            if "back" in cache and cache["back"].collidepoint(mx, my):
                game.running = False

        elif ctx.state == STATE_SECTOR_SELECT:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_MENU
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                game.previous_state = STATE_SECTOR_SELECT
                ctx.state = STATE_HANGAR
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                game.previous_state = STATE_SECTOR_SELECT
                ctx.state = STATE_SETTINGS
            elif "missions" in cache:
                for m_id, m_rect in cache["missions"].items():
                    if m_rect.collidepoint(mx, my):
                        game.pending_mission_id = m_id
                        ctx.state = STATE_MISSION_BRIEFING
                        return
            elif "sectors" in cache:
                for idx, s_rect in enumerate(cache["sectors"]):
                    if s_rect.collidepoint(mx, my) and ctx.unlocked_sectors[idx]:
                        ctx.current_sector_idx = idx
                        missions = get_missions_for_sector(idx + 1)
                        if missions:
                            game.pending_mission_id = missions[0]["id"]
                            ctx.state = STATE_MISSION_BRIEFING
                        return

        elif ctx.state == STATE_MISSION_BRIEFING:
            if "start" in cache and cache["start"].collidepoint(mx, my):
                game.start_phase5_mission(game.pending_mission_id)
            elif "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU

        elif ctx.state == STATE_HANGAR:
            if "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = game.previous_state if game.previous_state != STATE_HANGAR else STATE_SECTOR_SELECT
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                game.previous_state = STATE_HANGAR
                ctx.state = STATE_SETTINGS
            elif "exit" in cache and cache["exit"].collidepoint(mx, my):
                ctx.state = STATE_MENU
            elif "upgrades" in cache:
                for u_id, u_rect in cache["upgrades"].items():
                    if u_rect.collidepoint(mx, my):
                        game.buy_upgrade(u_id)
                        return
            if "drone" in cache and cache["drone"].collidepoint(mx, my):
                if ctx.player:
                    ctx.player.cycle_drone_class()
                    ctx.selected_drone = ctx.player.drone_class
                    game.save_progress()
            elif "skin" in cache and cache["skin"].collidepoint(mx, my):
                if ctx.player:
                    ctx.player.cycle_visual_skin()
                    ctx.selected_skin = ctx.player.skin_id
                    ctx.selected_skin_override = ctx.selected_skin
                    game.save_progress()
            elif "skins" in cache:
                skins_items = cache["skins"].items() if isinstance(cache["skins"], dict) else enumerate(cache["skins"])
                for skin_idx, s_rect in skins_items:
                    if hasattr(s_rect, "collidepoint") and s_rect.collidepoint(mx, my):
                        if ctx.player:
                            ctx.player.set_visual_skin(skin_idx)
                            ctx.selected_skin = skin_idx
                            ctx.selected_skin_override = skin_idx
                            game.save_progress()
                        return

        elif ctx.state == STATE_SETTINGS:
            if "fullscreen" in cache and cache["fullscreen"].collidepoint(mx, my):
                game.toggle_fullscreen()
            elif "crt" in cache and cache["crt"].collidepoint(mx, my):
                ctx.show_crt = not ctx.show_crt
                game.save_progress()
            elif "sfx" in cache and cache["sfx"].collidepoint(mx, my):
                if game.audio_manager:
                    game.audio_manager.set_sound_enabled(not game.audio_manager.sound_enabled)
                game.save_progress()
            elif "diff" in cache and cache["diff"].collidepoint(mx, my):
                ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 5
                game.save_progress()
            elif "controller" in cache and cache["controller"].collidepoint(mx, my):
                ctx.state = STATE_CONTROLLER_TEST
            elif "back" in cache and cache["back"].collidepoint(mx, my):
                ctx.state = game.previous_state if game.previous_state != STATE_SETTINGS else STATE_SECTOR_SELECT

        elif ctx.state == STATE_PAUSED:
            if "resume" in cache and cache["resume"].collidepoint(mx, my):
                ctx.state = STATE_PLAYING
            elif "settings" in cache and cache["settings"].collidepoint(mx, my):
                game.previous_state = STATE_PAUSED
                ctx.state = STATE_SETTINGS
            elif "restart" in cache and cache["restart"].collidepoint(mx, my):
                game.start_phase5_mission(game.pending_mission_id)
            elif "menu" in cache and cache["menu"].collidepoint(mx, my):
                ctx.state = STATE_MENU

        elif ctx.state in (STATE_MISSION_COMPLETE, STATE_LEVEL_CLEAR, STATE_VICTORY):
            if "next" in cache and cache["next"].collidepoint(mx, my):
                next_m = game.get_next_mission_id()
                if next_m:
                    game.pending_mission_id = next_m
                    game.start_phase5_mission(next_m)
                else:
                    ctx.state = STATE_SECTOR_SELECT
            elif "hangar" in cache and cache["hangar"].collidepoint(mx, my):
                ctx.state = STATE_HANGAR
            elif "menu" in cache and cache["menu"].collidepoint(mx, my):
                ctx.state = STATE_SECTOR_SELECT

        elif ctx.state in (STATE_MISSION_FAILED, STATE_GAME_OVER):
            if "retry" in cache and cache["retry"].collidepoint(mx, my):
                game.start_phase5_mission(game.pending_mission_id)
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

    def _update_slider_drag(self, mx: int, game):
        """Updates custom difficulty slider values when dragging."""
        cache = game.ui_rects_cache
        sliders = [("hp_mult", 0.5, 3.0), ("speed_mult", 0.5, 2.0),
                   ("rate_mult", 0.5, 2.5), ("dmg_mult", 0.5, 3.0),
                   ("scrap_mult", 0.25, 3.0)]
        if 0 <= self.custom_difficulty_dragging < len(sliders):
            key, min_v, max_v = sliders[self.custom_difficulty_dragging]
            if key in cache:
                rect = cache[key]
                norm = max(0.0, min(1.0, (mx - rect.left) / max(1.0, rect.width)))
                val = round(min_v + norm * (max_v - min_v), 2)
                game.context.custom_difficulty_settings[key] = val

    def _handle_controller_button_down(self, event, game) -> bool:
        """Processes raw controller button clicks for navigation and actions."""
        ctx = game.context
        js_id = getattr(event, "instance_id", 0)
        js = game.input_manager.connected_joysticks.get(js_id)
        if not js:
            return True

        btn = event.button
        mgr = getattr(game.input_manager, "mapping_manager", None)
        if not mgr:
            return True

        profile = mgr.get_or_create_profile(js)

        # Binding Wizard interception
        if ctx.state == STATE_CONTROLLER_BINDING and self.binding_waiting and self.binding_action:
            profile.set_button(self.binding_action, btn)
            mgr.save_profiles()
            self.binding_waiting = False
            self.binding_action = None
            if game.audio_manager: game.audio_manager.play_buy()
            return True

        if profile.is_action_button(btn, ACTION_FULLSCREEN):
            game.toggle_fullscreen()
            return True

        return True

    def update_controller_navigation(self, dt: float, game):
        """Updates D-pad cursor movement, slider tuning, and button triggers across all menus."""
        ctx = game.context
        if ctx.state == STATE_PLAYING:
            return

        im = game.input_manager
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
            if game.audio_manager: game.audio_manager.play_click()
