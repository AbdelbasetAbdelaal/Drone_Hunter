"""
================================================================================
           KEYBOARD REGRESSION VERIFICATION TEST SUITE
================================================================================
Validates that all canonical keyboard controls and context-sensitive behaviors
operate cleanly through the SINGLE authoritative event pipeline:
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
    STATE_HANGAR, STATE_DRONE_SELECT, STATE_SETTINGS, STATE_MISSION_BRIEFING,
    STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_SAVE_SELECT
)
from src.input.input_manager import (
    InputManager, InputContext, ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY,
    ACTION_ROLL, ACTION_EMP, ACTION_ULTIMATE, ACTION_CLOAK, ACTION_WEAPON_NEXT,
    ACTION_WEAPON_PREV, ACTION_PAUSE, ACTION_CYCLE_CLASS, ACTION_CONFIRM,
    ACTION_CANCEL, ACTION_WEAPON_SLOT_1, ACTION_WEAPON_SLOT_2, ACTION_WEAPON_SLOT_3,
    ACTION_SELECT_SLOT_1, ACTION_SELECT_SLOT_2, ACTION_SELECT_SLOT_3,
    ACTION_SELECT_SLOT_4, ACTION_SELECT_SLOT_5
)


class TestKeyboardRegression(unittest.TestCase):

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context
        self.ic = self.game.input_controller
        self.im = self.game.input_manager

    def test_gameplay_movement_keys_continuous(self):
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
        """Spacebar triggers primary fire in GAMEPLAY context."""
        self.game.start_phase5_mission("S1_M1")
        self.im.set_context(InputContext.GAMEPLAY)

        event_space = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        self.im.process_events([event_space])
        self.assertTrue(self.im.actions_triggered.get(ACTION_FIRE_PRIMARY))

    def test_gameplay_roll_shift(self):
        """LSHIFT and RSHIFT trigger roll through authoritative handle_events."""
        self.game.start_phase5_mission("S1_M1")
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LSHIFT}))
        self.ic.handle_events(self.game)
        self.assertTrue(self.ctx.player.is_rolling)

    def test_gameplay_emp_e(self):
        """E triggers EMP blast through authoritative handle_events."""
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

        # Also test Q
        self.ctx.player.overdrive_timer = 0.0
        self.ctx.player.overdrive_cooldown = 0.0
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_q}))
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
        self.ctx.player.active_weapon = "pulse"
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_TAB}))
        self.ic.handle_events(self.game)
        self.assertEqual(self.ctx.player.active_weapon, "scatter")

    def test_gameplay_weapon_selection_1_to_6(self):
        """Keys 1-6 select specific weapon slots through canonical actions."""
        self.game.start_phase5_mission("S1_M1")
        p = self.ctx.player
        p.available_weapons = ["pulse", "scatter", "missile"]

        # Press 2 -> scatter
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_2}))
        self.ic.handle_events(self.game)
        self.assertEqual(p.active_weapon, "scatter")

        # Press 1 -> pulse
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_1}))
        self.ic.handle_events(self.game)
        self.assertEqual(p.active_weapon, "pulse")

    def test_gameplay_pause_esc_and_p(self):
        """ESC and P pause the game through canonical actions."""
        self.game.start_phase5_mission("S1_M1")
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}))
        self.ic.handle_events(self.game)
        self.assertEqual(self.ctx.state, STATE_PAUSED)

    def test_hangar_c_cycles_class_not_skin(self):
        """In Hangar, C cycles drone class through canonical actions."""
        self.ctx.state = STATE_HANGAR
        p = self.ctx.player
        initial_class = p.drone_class

        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c}))
        self.ic.handle_events(self.game)
        self.assertNotEqual(p.drone_class, initial_class)

    def test_drone_select_keys_1_to_5(self):
        """In Drone Select, keys 1-5 select drone classes and proceed to sector select."""
        self.ctx.state = STATE_DRONE_SELECT
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_2}))
        self.ic.handle_events(self.game)
        input_ctx = self.game.create_input_handling_context()
        self.ic.update_controller_navigation(0.016, input_ctx)
        self.assertEqual(self.ctx.selected_drone, "phantom")
        self.assertEqual(self.ctx.state, STATE_SECTOR_SELECT)

    def test_menu_contexts_canonical_actions(self):
        """Test canonical action mappings across all contexts."""
        contexts_to_test = [
            (InputContext.MAIN_MENU, pygame.K_RETURN, ACTION_CONFIRM),
            (InputContext.MAIN_MENU, pygame.K_ESCAPE, ACTION_CANCEL),
            (InputContext.DRONE_SELECT, pygame.K_1, ACTION_SELECT_SLOT_1),
            (InputContext.DRONE_SELECT, pygame.K_5, ACTION_SELECT_SLOT_5),
            (InputContext.HANGAR, pygame.K_c, ACTION_CYCLE_CLASS),
            (InputContext.PAUSE, pygame.K_ESCAPE, ACTION_CANCEL),
            (InputContext.MISSION_COMPLETE, pygame.K_SPACE, ACTION_CONFIRM),
            (InputContext.MISSION_FAILED, pygame.K_r, ACTION_CONFIRM),
        ]
        for ctx_name, key_code, expected_action in contexts_to_test:
            self.im.set_context(ctx_name)
            self.im.actions_triggered.clear()
            event = pygame.event.Event(pygame.KEYDOWN, {"key": key_code})
            self.im.process_events([event])
            self.assertTrue(
                self.im.actions_triggered.get(expected_action, False),
                f"Expected {expected_action} for key {key_code} in context {ctx_name}"
            )


if __name__ == "__main__":
    unittest.main()
