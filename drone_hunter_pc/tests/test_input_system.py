"""
================================================================================
                    DRONE HUNTER 2D - INPUT SYSTEM TEST SUITE
================================================================================
Comprehensive verification of First-Class Controller, Gamepad, Joystick,
Keyboard/Mouse, Deadzone, Analog Normalization, Hot-Plugging, and Rumble Safety.
"""

import os
import sys
import math
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.input.input_manager import (
    InputManager,
    ACTION_MOVE_X, ACTION_MOVE_Y, ACTION_AIM_ANGLE,
    ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY,
    ACTION_WEAPON_NEXT, ACTION_WEAPON_PREV,
    ACTION_ROLL, ACTION_EMP, ACTION_ULTIMATE,
    ACTION_SPECIAL, ACTION_PAUSE, ACTION_CLOAK,
    DEVICE_KEYBOARD_MOUSE, DEVICE_GAMEPAD, DEVICE_JOYSTICK,
    PROMPT_MAP_KEYBOARD, PROMPT_MAP_GAMEPAD
)
from src.input.input_manager import InputContext
from src.core.game import Game
from src.core.game_state import (
    STATE_PLAYING, STATE_MENU, STATE_HANGAR, STATE_SECTOR_SELECT,
    STATE_MISSION_BRIEFING, STATE_MISSION_FAILED, STATE_MISSION_COMPLETE
)
from src.core.gameplay_context import InputHandlingContext
from src.core.input_controller import InputController
from src.core.game_context import GameContext
from src.entities.player import Player


class TestInputSystem(unittest.TestCase):

    def setUp(self):
        self.input_mgr = InputManager()
        self.input_mgr.connected_joysticks.clear()
        self.input_mgr.active_joystick_id = None

    def test_input_manager_initialization(self):
        """Verify InputManager initializes cleanly with zero controllers connected without crashing."""
        self.assertIsNotNone(self.input_mgr)
        self.assertEqual(self.input_mgr.active_device, DEVICE_KEYBOARD_MOUSE)
        self.assertEqual(self.input_mgr.deadzone, 0.12)
        self.assertTrue(self.input_mgr.enabled)
        self.assertTrue(self.input_mgr.vibration_enabled)

    def test_no_controller_game_start(self):
        """Verify the game initializes and launches cleanly with zero controllers attached."""
        game = Game(test_mode=True)
        self.assertIsNotNone(game.input_manager)
        self.assertEqual(game.input_manager.active_device, DEVICE_KEYBOARD_MOUSE)

    def test_keyboard_input_actions(self):
        """Verify keyboard inputs properly map to canonical action prompts."""
        prompt_roll = self.input_mgr.get_prompt_for_action("ROLL")
        prompt_emp = self.input_mgr.get_prompt_for_action("EMP")
        prompt_ult = self.input_mgr.get_prompt_for_action("ULTIMATE")
        
        self.assertEqual(prompt_roll, "LSHIFT")
        self.assertEqual(prompt_emp, "E")
        self.assertEqual(prompt_ult, "F")

    def test_keyboard_gameplay_shortcuts_trigger_canonical_actions(self):
        """Documented gameplay shortcuts must reach the shared action layer."""
        self.input_mgr.set_context(InputContext.GAMEPLAY)
        events = [
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LSHIFT}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_e}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_f}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_TAB}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_b}),
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 5}),
        ]
        self.input_mgr.process_events(events)

        self.assertTrue(self.input_mgr.actions_triggered[ACTION_ROLL])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_EMP])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_ULTIMATE])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_WEAPON_NEXT])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_WEAPON_PREV])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_CLOAK])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_SPECIAL])
        self.assertTrue(self.input_mgr.actions_triggered[ACTION_FIRE_PRIMARY])

    def test_number_keys_select_available_weapon_slots(self):
        """Gameplay number shortcuts select only an available weapon slot."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((500, 360))
        ctx.player.available_weapons = ["pulse", "scatter", "missile"]
        input_ctx = InputHandlingContext(context=ctx, input_manager=self.input_mgr)

        InputController()._handle_keyboard_menu_navigation(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_2}), input_ctx
        )

        self.assertEqual(ctx.player.active_weapon, "scatter")

    def test_sector_confirm_opens_briefing_and_briefing_confirm_starts(self):
        """Enter/Space must work as menu confirmation outside the main menu."""
        ctx = GameContext()
        ctx.state = STATE_SECTOR_SELECT
        started = []
        input_ctx = InputHandlingContext(
            context=ctx,
            input_manager=self.input_mgr,
            start_mission_callback=started.append,
        )
        controller = InputController()

        controller._handle_keyboard_menu_navigation(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN}), input_ctx
        )
        self.assertEqual(ctx.state, STATE_MISSION_BRIEFING)
        self.assertEqual(input_ctx.pending_mission_id, "S1_M1")

        controller._handle_keyboard_menu_navigation(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}), input_ctx
        )
        self.assertEqual(started, ["S1_M1"])

    def test_keyboard_menu_navigation_uses_wasd_and_confirm(self):
        """Keyboard navigation must use the same cursor semantics as a gamepad."""
        ctx = GameContext()
        ctx.state = STATE_MENU
        controller = InputController()
        input_ctx = InputHandlingContext(context=ctx, input_manager=self.input_mgr)
        self.input_mgr.set_context(InputContext.MAIN_MENU)

        self.input_mgr.process_events([pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_s})])
        controller.update_controller_navigation(0.016, input_ctx)
        self.assertEqual(controller.menu_cursor, 1)

        self.input_mgr.process_events([pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})])
        controller.update_controller_navigation(0.016, input_ctx)
        self.assertEqual(ctx.state, STATE_HANGAR)

    def test_controller_input_actions(self):
        """Verify gamepad active device switches action prompts to Xbox labels."""
        self.input_mgr.active_device = DEVICE_GAMEPAD
        
        prompt_roll = self.input_mgr.get_prompt_for_action("ROLL")
        prompt_emp = self.input_mgr.get_prompt_for_action("EMP")
        prompt_ult = self.input_mgr.get_prompt_for_action("ULTIMATE")
        prompt_fire = self.input_mgr.get_prompt_for_action("FIRE_PRIMARY")

        self.assertEqual(prompt_roll, "A")
        self.assertEqual(prompt_emp, "X")
        self.assertEqual(prompt_ult, "Y")
        self.assertEqual(prompt_fire, "RT")

    def test_joystick_input_actions(self):
        """Verify joystick device returns valid button prompts."""
        self.input_mgr.active_device = DEVICE_JOYSTICK
        self.assertEqual(self.input_mgr.get_prompt_for_action("ROLL"), "A")

    def test_axis_deadzone(self):
        """Verify raw stick deflections below deadzone output zero vector."""
        # Raw deflection within deadzone (0.05 < 0.12)
        sx, sy, mag = self.input_mgr.apply_deadzone_radial(0.05, 0.05)
        self.assertEqual(sx, 0.0)
        self.assertEqual(sy, 0.0)
        self.assertEqual(mag, 0.0)

    def test_zero_input(self):
        """Verify zero stick deflection produces zero output."""
        sx, sy, mag = self.input_mgr.apply_deadzone_radial(0.0, 0.0)
        self.assertEqual(sx, 0.0)
        self.assertEqual(sy, 0.0)
        self.assertEqual(mag, 0.0)

    def test_full_input(self):
        """Verify full stick deflection produces full normalized output."""
        sx, sy, mag = self.input_mgr.apply_deadzone_radial(1.0, 0.0)
        self.assertAlmostEqual(sx, 1.0, places=2)
        self.assertAlmostEqual(sy, 0.0, places=2)
        self.assertAlmostEqual(mag, 1.0, places=2)

    def test_axis_normalization(self):
        """Verify diagonal full stick deflection normalizes magnitude correctly."""
        raw_x = 1.0 / math.sqrt(2)
        raw_y = 1.0 / math.sqrt(2)
        sx, sy, mag = self.input_mgr.apply_deadzone_radial(raw_x, raw_y)
        self.assertAlmostEqual(mag, 1.0, places=2)
        out_length = math.hypot(sx, sy)
        self.assertAlmostEqual(out_length, 1.0, places=2)

    def test_axis_response_curve(self):
        """Verify non-linear response curve produces smooth precision at low deflection."""
        # 50% deflection beyond deadzone
        sx_mid, sy_mid, mag_mid = self.input_mgr.apply_deadzone_radial(0.5, 0.0)
        self.assertGreater(mag_mid, 0.0)
        self.assertLess(mag_mid, 0.5) # Curve ensures precise micro-adjustments at low tilt

    def test_action_mapping(self):
        """Verify Xbox action mapping constants match specifications."""
        from src.input.input_manager import XBOX_BUTTON_MAP
        self.assertEqual(XBOX_BUTTON_MAP[0], ACTION_ROLL)       # A -> ROLL
        self.assertEqual(XBOX_BUTTON_MAP[2], ACTION_EMP)        # X -> EMP
        self.assertEqual(XBOX_BUTTON_MAP[3], ACTION_ULTIMATE)   # Y -> ULTIMATE
        self.assertEqual(XBOX_BUTTON_MAP[5], ACTION_WEAPON_NEXT)# RB -> WEAPON_NEXT
        self.assertEqual(XBOX_BUTTON_MAP[4], ACTION_WEAPON_PREV)# LB -> WEAPON_PREV
        self.assertEqual(XBOX_BUTTON_MAP[7], ACTION_PAUSE)      # START -> PAUSE

    def test_hot_plug(self):
        """Verify adding and removing joysticks updates internal connection registry safely."""
        self.input_mgr.connected_joysticks.clear()
        self.input_mgr.active_joystick_id = None

        fake_js = MagicMock()
        fake_js.get_instance_id.return_value = 99
        self.input_mgr.connected_joysticks[99] = fake_js
        self.input_mgr.active_joystick_id = 99
        
        self.assertEqual(len(self.input_mgr.connected_joysticks), 1)
        self.assertEqual(self.input_mgr.active_joystick, fake_js)

        # Simulate disconnect
        self.input_mgr._remove_joystick(99)
        self.assertEqual(len(self.input_mgr.connected_joysticks), 0)
        self.assertIsNone(self.input_mgr.active_joystick)

    def test_rumble_supported(self):
        """Verify rumble invocation on supported joystick executes safely without error."""
        fake_js = MagicMock()
        fake_js.rumble = MagicMock()
        self.input_mgr.connected_joysticks[0] = fake_js
        self.input_mgr.active_joystick_id = 0
        
        self.input_mgr.trigger_rumble(0.5, 0.5, 100)
        fake_js.rumble.assert_called_once_with(0.5, 0.5, 100)

    def test_rumble_unsupported(self):
        """Verify rumble invocation on joystick lacking rumble method degrades silently without crashing."""
        fake_js = object() # No rumble method
        self.input_mgr.connected_joysticks[0] = fake_js
        self.input_mgr.active_joystick_id = 0
        
        # Should execute silently without exception
        self.input_mgr.trigger_rumble(0.5, 0.5, 100)

    def test_rumble_disconnect_safety(self):
        """Verify triggering rumble when no active joystick exists degrades silently."""
        self.input_mgr.active_joystick_id = None
        self.input_mgr.trigger_rumble(0.5, 0.5, 100)
        self.input_mgr.stop_rumble()

    def test_rumble_duration_bounded(self):
        """Verify rumble duration parameters are cleanly passed to device driver."""
        fake_js = MagicMock()
        self.input_mgr.connected_joysticks[0] = fake_js
        self.input_mgr.active_joystick_id = 0
        
        self.input_mgr.trigger_rumble(0.2, 0.3, 150)
        fake_js.rumble.assert_called_with(0.2, 0.3, 150)


    def test_sector_select_mouse_interaction(self):
        """Verify mouse clicking on sector cards switches the active sector."""
        from src.ui.menus import draw_mission_select_ui
        ctx = GameContext()
        ctx.state = STATE_SECTOR_SELECT
        # Unlock sector 2
        ctx.campaign_state.unlock_sector(2)
        
        canvas = pygame.Surface((1280, 720))
        cache = draw_mission_select_ui(canvas, ctx, 500, (0, 0))
        
        controller = InputController()
        input_ctx = InputHandlingContext(
            context=ctx,
            ui_rects_cache=cache,
            input_manager=self.input_mgr
        )
        
        # Click on Sector 2 card
        s2_rect = cache["sectors"][2]
        click_pos = s2_rect.center
        controller._handle_mouse_click(click_pos[0], click_pos[1], input_ctx)
        
        self.assertEqual(ctx.campaign_state.current_sector_idx, 1)

    def test_sector_select_completed_mission_clickable(self):
        """Verify completed missions are interactive and clickable with the mouse."""
        from src.ui.menus import draw_mission_select_ui
        ctx = GameContext()
        ctx.state = STATE_SECTOR_SELECT
        # Complete S1_M1
        ctx.campaign_state.complete_mission("S1_M1")
        
        canvas = pygame.Surface((1280, 720))
        cache = draw_mission_select_ui(canvas, ctx, 500, (0, 0))
        
        # S1_M1 must be present in interactive mission rects
        self.assertIn("S1_M1", cache["missions"])
        
        controller = InputController()
        input_ctx = InputHandlingContext(
            context=ctx,
            ui_rects_cache=cache,
            input_manager=self.input_mgr
        )
        
        # Click on completed S1_M1 mission card
        m1_rect = cache["missions"]["S1_M1"]
        controller._handle_mouse_click(m1_rect.centerx, m1_rect.centery, input_ctx)
        
    def test_mission_failed_mouse_interaction(self):
        """Verify clicking buttons in MISSION FAILED screen activates retry, sector map, and exit."""
        from src.ui.menus import draw_mission_failed
        ctx = GameContext()
        ctx.state = STATE_MISSION_FAILED
        canvas = pygame.Surface((1280, 720))
        cache = draw_mission_failed(canvas, 100, (0, 0))

        self.assertIn("retry", cache)
        self.assertIn("map", cache)
        self.assertIn("exit", cache)

        controller = InputController()
        started_missions = []
        input_ctx = InputHandlingContext(
            context=ctx,
            ui_rects_cache=cache,
            input_manager=self.input_mgr,
            start_mission_callback=lambda m: started_missions.append(m),
            pending_mission_id="S1_M1"
        )

        # 1. Click Retry
        controller._handle_mouse_click(cache["retry"].centerx, cache["retry"].centery, input_ctx)
        self.assertEqual(started_missions, ["S1_M1"])

        # 2. Click Sector Map
        ctx.state = STATE_MISSION_FAILED
        controller._handle_mouse_click(cache["map"].centerx, cache["map"].centery, input_ctx)
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

        # 3. Click Quit to Menu
        ctx.state = STATE_MISSION_FAILED
        controller._handle_mouse_click(cache["exit"].centerx, cache["exit"].centery, input_ctx)
        self.assertEqual(ctx.state, STATE_MENU)

    def test_mission_failed_keyboard_navigation(self):
        """Verify arrow keys, WASD, M, Q, and Space work in MISSION FAILED screen."""
        ctx = GameContext()
        ctx.state = STATE_MISSION_FAILED
        controller = InputController()
        controller.menu_cursor = 0
        started_missions = []
        input_ctx = InputHandlingContext(
            context=ctx,
            input_manager=self.input_mgr,
            start_mission_callback=lambda m: started_missions.append(m),
            pending_mission_id="S1_M2"
        )

        # Navigate down with Down Arrow / S
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        controller._handle_keyboard_menu_navigation(event_down, input_ctx)
        self.assertEqual(controller.menu_cursor, 1)

        # Press Return on Sector Map
        event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        controller._handle_keyboard_menu_navigation(event_enter, input_ctx)
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

        # M shortcut to Sector Map
        ctx.state = STATE_MISSION_FAILED
        event_m = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
        controller._handle_keyboard_menu_navigation(event_m, input_ctx)
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

        # Q shortcut to Main Menu
        ctx.state = STATE_MISSION_FAILED
        event_q = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)
        controller._handle_keyboard_menu_navigation(event_q, input_ctx)
        self.assertEqual(ctx.state, STATE_MENU)


if __name__ == "__main__":
    unittest.main()
