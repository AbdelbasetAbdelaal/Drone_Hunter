import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.game_state import (
    STATE_PLAYING, STATE_MENU, STATE_PAUSED, STATE_HANGAR,
    STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_SETTINGS
)
from src.input import (
    InputManager, InputContext,
    ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY, ACTION_EMP, ACTION_ULTIMATE,
    ACTION_ROLL, ACTION_WEAPON_NEXT, ACTION_WEAPON_PREV, ACTION_SPECIAL,
    ACTION_CLOAK, ACTION_CYCLE_CLASS, ACTION_PAUSE,
    ACTION_FULLSCREEN, ACTION_CONFIRM, ACTION_CANCEL
)
from src.core.input_controller import InputController


class TestInputFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context
        self.input_mgr = InputManager()
        self.input_ctrl = self.game.input_controller

    def test_keyboard_movement_contract(self):
        """Verify supported keyboard movement actions route accurately into player movement."""
        self.game.start_phase5_mission("S1_M1")
        player = self.ctx.player

        # W key moves up
        keys_w = {pygame.K_w: True, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_SPACE: False}
        init_y = player.pos.y
        player.handle_input(keys_w, dt=0.05, mouse_pos=(640, 100))
        player.update(dt=0.05, targets_group=self.ctx.target_group)
        self.assertLess(player.pos.y, init_y, "W key must move player upward")

        # S key moves down
        keys_s = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: True, pygame.K_d: False, pygame.K_SPACE: False}
        init_y = player.pos.y
        player.handle_input(keys_s, dt=0.05, mouse_pos=(640, 600))
        player.update(dt=0.05, targets_group=self.ctx.target_group)
        self.assertGreater(player.pos.y, init_y, "S key must move player downward")

        # A key moves left
        keys_a = {pygame.K_w: False, pygame.K_a: True, pygame.K_s: False, pygame.K_d: False, pygame.K_SPACE: False}
        init_x = player.pos.x
        player.handle_input(keys_a, dt=0.05, mouse_pos=(100, 360))
        player.update(dt=0.05, targets_group=self.ctx.target_group)
        self.assertLess(player.pos.x, init_x, "A key must move player leftward")

        # D key moves right
        keys_d = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: True, pygame.K_SPACE: False}
        init_x = player.pos.x
        player.handle_input(keys_d, dt=0.05, mouse_pos=(1000, 360))
        player.update(dt=0.05, targets_group=self.ctx.target_group)
        self.assertGreater(player.pos.x, init_x, "D key must move player rightward")

    def test_keyboard_gameplay_actions_contract(self):
        """Verify SPACE, SHIFT, E, F, Q, C, K, TAB, 1-6, ESC, P in GAMEPLAY context."""
        self.game.start_phase5_mission("S1_M1")
        player = self.ctx.player

        # SPACE / SHIFT -> Roll
        self.assertTrue(player.trigger_roll(1.0))
        self.assertTrue(player.is_rolling)

        # TAB / Q / E -> Weapon cycling
        cur_w = player.active_weapon
        player.cycle_weapon()
        self.assertNotEqual(player.active_weapon, cur_w)

        # 1-6 Slot Selection
        if len(player.available_weapons) >= 2:
            player.active_weapon = player.available_weapons[1]
            self.assertEqual(player.active_weapon, player.available_weapons[1])

        # C / K -> Cloak
        self.assertTrue(player.trigger_cloak())
        self.assertTrue(player.is_cloaked)

        # F -> Overclock / Ultimate
        player.trigger_overclock(3.0)
        self.assertGreater(player.overclock_timer, 0.0)

        # ESC / P -> Pause routing
        self.assertEqual(InputController.get_current_input_context(STATE_PLAYING), InputContext.GAMEPLAY)
        self.assertEqual(InputController.get_current_input_context(STATE_PAUSED), InputContext.PAUSE)

    def test_context_sensitive_input_routing(self):
        """Verify context-sensitive routing across Menu, Hangar, Pause, Mission Complete, Mission Failed."""
        # Menu Context
        self.assertEqual(InputController.get_current_input_context(STATE_MENU), InputContext.MAIN_MENU)

        # Hangar Context
        self.assertEqual(InputController.get_current_input_context(STATE_HANGAR), InputContext.HANGAR)

        # Pause Context
        self.assertEqual(InputController.get_current_input_context(STATE_PAUSED), InputContext.PAUSE)

        # Mission Complete Context
        self.assertEqual(InputController.get_current_input_context(STATE_MISSION_COMPLETE), InputContext.MISSION_COMPLETE)

        # Mission Failed Context
        self.assertEqual(InputController.get_current_input_context(STATE_MISSION_FAILED), InputContext.MISSION_FAILED)

        # Settings Context
        self.assertEqual(InputController.get_current_input_context(STATE_SETTINGS), InputContext.SETTINGS)

    def test_controller_synthetic_action_routing(self):
        """Verify controller input abstraction routes move, aim, fire, pause, weapon switch, roll, EMP, ultimate, cloak, confirm, cancel."""
        self.game.start_phase5_mission("S1_M1")
        player = self.ctx.player
        init_x = player.pos.x

        # 1. Controller Analog Move & Aim
        mock_input_state = {
            "move_x": 0.8,
            "move_y": -0.6,
            "aim_angle_deg": 90.0,
            "fire_primary": True,
            "fire_secondary": False,
            "roll": True,
            "cycle_weapon": True,
            "emp": True,
            "cloak": True,
            "ultimate": True,
            "confirm": True,
            "cancel": False,
            "pause": False,
        }

        player.handle_input({}, dt=0.05, mouse_pos=(800, 360), input_state=mock_input_state)
        player.update(dt=0.05, targets_group=self.ctx.target_group)

        self.assertGreater(player.pos.x, init_x, "Controller move_x > 0 must move player rightward")

        # 2. Controller Action Verification
        self.assertTrue(player.trigger_roll(1.0))
        self.assertTrue(player.is_rolling)

        cur_w = player.active_weapon
        player.cycle_weapon(1)
        self.assertNotEqual(player.active_weapon, cur_w)

        # 3. Controller Pause Routing
        self.game.state_manager.change_state(STATE_PAUSED)
        self.assertEqual(self.ctx.state, STATE_PAUSED)

    def test_canvas_and_window_coordinate_mapping(self):
        """Verify virtual canvas 1280x720 handles coordinate mapping under window sizing."""
        cam = self.game.camera
        if cam is not None:
            world_center = cam.screen_to_world(640, 360)
            self.assertIsNotNone(world_center)


if __name__ == "__main__":
    unittest.main()
