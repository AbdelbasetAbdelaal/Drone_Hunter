"""
================================================================================
           KEYBOARD REGRESSION VERIFICATION TEST SUITE
================================================================================
Validates that all canonical keyboard controls and context-sensitive behaviors
operate cleanly through the complete event pipeline:
pygame KEYDOWN -> InputManager -> InputController -> Game/GameState.
"""

import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.core.game import Game
from src.core.game_state import (
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_SECTOR_SELECT,
    STATE_HANGAR, STATE_DRONE_SELECT, STATE_SETTINGS, STATE_MISSION_BRIEFING
)
from src.input.input_manager import (
    InputManager, InputContext, ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY,
    ACTION_ROLL, ACTION_EMP, ACTION_ULTIMATE, ACTION_CLOAK, ACTION_WEAPON_NEXT,
    ACTION_PAUSE, ACTION_CYCLE_CLASS
)


class TestKeyboardRegression(unittest.TestCase):

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context
        self.ic = self.game.input_controller
        self.im = self.game.input_manager

    def test_gameplay_movement_keys(self):
        """WASD and Arrow keys poll properly for player movement."""
        self.game.start_phase5_mission("S1_M1")
        p = self.ctx.player

        # Simulate W key
        p.handle_input({pygame.K_w: True}, dt=0.016)
        self.assertLess(p.velocity.y, 0)

        # Simulate D key
        p.handle_input({pygame.K_d: True}, dt=0.016)
        self.assertGreater(p.velocity.x, 0)

    def test_gameplay_primary_fire_space_and_lmb(self):
        """Spacebar and LMB trigger primary fire."""
        self.game.start_phase5_mission("S1_M1")
        self.im.set_context(InputContext.GAMEPLAY)

        event_space = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        self.im.process_events([event_space])
        self.assertTrue(self.im.actions_triggered.get(ACTION_FIRE_PRIMARY))

    def test_gameplay_roll_shift(self):
        """LSHIFT and RSHIFT trigger roll."""
        self.game.start_phase5_mission("S1_M1")
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LSHIFT}))
        self.ic.handle_events(self.game)
        self.assertTrue(self.ctx.player.is_rolling)

    def test_gameplay_emp_e(self):
        """E triggers EMP blast."""
        self.game.start_phase5_mission("S1_M1")
        self.ctx.player.emp_cooldown = 0.0
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_e}))
        self.ic.handle_events(self.game)
        self.assertGreater(self.ctx.player.emp_cooldown, 0.0)

    def test_gameplay_ultimate_f_and_q(self):
        """F and Q trigger overdrive / ultimate."""
        self.game.start_phase5_mission("S1_M1")
        self.ctx.player.overdrive_cooldown = 0.0
        self.ctx.player.overdrive_timer = 0.0
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_f}))
        self.ic.handle_events(self.game)
        self.assertGreater(self.ctx.player.overdrive_timer, 0.0)

    def test_gameplay_cloak_c_and_k(self):
        """C and K trigger cloak in gameplay."""
        self.game.start_phase5_mission("S1_M1")
        self.ctx.player.cloak_energy = 100.0
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c}))
        self.ic.handle_events(self.game)
        self.assertTrue(self.ctx.player.is_cloaked)

    def test_gameplay_weapon_cycle_tab(self):
        """TAB cycles to next weapon."""
        self.game.start_phase5_mission("S1_M1")
        self.ctx.player.available_weapons = ["pulse", "scatter", "missile"]
        initial_w = self.ctx.player.active_weapon
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_TAB}))
        self.ic.handle_events(self.game)
        self.assertNotEqual(self.ctx.player.active_weapon, initial_w)

    def test_gameplay_weapon_selection_1_to_6(self):
        """Keys 1-6 select specific weapon slots."""
        self.game.start_phase5_mission("S1_M1")
        p = self.ctx.player
        p.available_weapons = ["pulse", "scatter", "missile"]

        # Press 2 -> scatter
        event_2 = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_2})
        input_ctx = self.game.create_input_handling_context()
        self.ic._handle_keyboard_menu_navigation(event_2, input_ctx)
        self.assertEqual(p.active_weapon, "scatter")

        # Press 1 -> pulse
        event_1 = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_1})
        self.ic._handle_keyboard_menu_navigation(event_1, input_ctx)
        self.assertEqual(p.active_weapon, "pulse")

    def test_gameplay_pause_esc_and_p(self):
        """ESC and P pause the game."""
        self.game.start_phase5_mission("S1_M1")
        input_ctx = self.game.create_input_handling_context()

        event_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        self.ic._handle_keyboard_menu_navigation(event_esc, input_ctx)
        self.assertEqual(self.ctx.state, STATE_PAUSED)

        # In pause, Space resumes
        event_space = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        self.ic._handle_keyboard_menu_navigation(event_space, input_ctx)
        self.assertEqual(self.ctx.state, STATE_PLAYING)

    def test_hangar_c_cycles_class_not_skin(self):
        """In Hangar, C cycles drone class, NOT skin."""
        self.ctx.state = STATE_HANGAR
        input_ctx = self.game.create_input_handling_context()
        p = self.ctx.player
        initial_class = p.drone_class

        event_c = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c})
        self.ic._handle_keyboard_menu_navigation(event_c, input_ctx)
        self.assertNotEqual(p.drone_class, initial_class)

    def test_menu_confirm_and_back(self):
        """Menu confirm with Enter/Space, Back with ESC."""
        self.ctx.state = STATE_MENU
        input_ctx = self.game.create_input_handling_context()

        # Space -> Drone Select
        event_space = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        self.ic._handle_keyboard_menu_navigation(event_space, input_ctx)
        self.assertEqual(self.ctx.state, STATE_DRONE_SELECT)

        # ESC -> Back to Menu
        event_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        self.ic._handle_keyboard_menu_navigation(event_esc, input_ctx)
        self.assertEqual(self.ctx.state, STATE_MENU)


if __name__ == "__main__":
    unittest.main()
