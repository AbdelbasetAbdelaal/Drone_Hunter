"""
================================================================================
          PHASE 1 ARCHITECTURE REGRESSION & CONTROLLER TESTS
================================================================================
Validates that GameStateManager, SaveController, GameplayController,
InputController, and Game orchestrate cleanly without circular imports or regressions.
"""

import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.core import (
    Game, GameStateManager, SaveController, GameplayController, InputController,
    GameState, STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_SECTOR_SELECT,
    STATE_SAVE_SELECT, STATE_SETTINGS
)
from src.core.game_context import GameContext
from src.systems.save_system import SaveSystem
from src.systems.progression_system import ProgressionSystem


class TestPhase1Architecture(unittest.TestCase):

    def setUp(self):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

    def test_no_circular_imports(self):
        """Verifies all core modules can be imported independently without circular dependencies."""
        import importlib
        import src.core.game_state_manager
        import src.core.save_controller
        import src.core.gameplay_controller
        import src.core.input_controller
        import src.core.game

        importlib.reload(src.core.game_state_manager)
        importlib.reload(src.core.save_controller)
        importlib.reload(src.core.gameplay_controller)
        importlib.reload(src.core.input_controller)
        importlib.reload(src.core.game)

    def test_game_initializes_and_orchestrates(self):
        """Verifies Game initializes as an orchestrator with all controller instances attached."""
        game = Game(test_mode=True)
        self.assertIsNotNone(game.state_manager)
        self.assertIsNotNone(game.save_controller)
        self.assertIsNotNone(game.gameplay_controller)
        self.assertIsNotNone(game.input_controller)
        self.assertIsNotNone(game.renderer)
        self.assertIsNotNone(game.audio_manager)
        self.assertIsNotNone(game.mission_system)
        self.assertIsNotNone(game.combat_director)
        self.assertIsNotNone(game.boss_system)
        self.assertIsNotNone(game.objective_system)
        self.assertIsNotNone(game.context)

    def test_game_state_manager_transitions(self):
        """Verifies GameStateManager transitions and queries."""
        sm = GameStateManager(initial_state=STATE_MENU)
        self.assertEqual(sm.current_state, STATE_MENU)
        self.assertTrue(sm.is_in_menu())
        self.assertFalse(sm.is_in_gameplay())

        transition_events = []
        sm.register_transition_listener(lambda old, new: transition_events.append((old, new)))

        success = sm.change_state(STATE_PLAYING)
        self.assertTrue(success)
        self.assertEqual(sm.current_state, STATE_PLAYING)
        self.assertEqual(sm.previous_state, STATE_MENU)
        self.assertTrue(sm.is_in_gameplay())
        self.assertFalse(sm.is_in_menu())
        self.assertEqual(len(transition_events), 1)
        self.assertEqual(transition_events[0], (STATE_MENU, STATE_PLAYING))

        sm.change_state(STATE_PAUSED)
        self.assertTrue(sm.is_paused())

    def test_save_controller_slot_management(self):
        """Verifies SaveController can load slots and save progress cleanly."""
        save_sys = SaveSystem(slot_index=0)
        sc = SaveController(save_system=save_sys, initial_slot=0)
        ctx = GameContext()

        data = sc.load_slot(0, ctx)
        self.assertIsInstance(data, dict)
        self.assertEqual(sc.selected_save_slot, 0)

        # Test select_save_slot (1-based to 0-based conversion)
        sc.select_save_slot(2, ctx)
        self.assertEqual(sc.selected_save_slot, 1)

        # Save progress
        ctx.scrap = 550
        saved = sc.save_current_progress(ctx)
        self.assertTrue(saved)

    def test_gameplay_controller_mission_and_upgrades(self):
        """Verifies GameplayController starts missions and processes upgrades."""
        prog = ProgressionSystem([True, False, False, False, False], [True] + [False] * 14)
        gc = GameplayController(progression_system=prog)
        ctx = GameContext()
        ctx.scrap = 10000

        # Upgrade purchase
        bought = gc.buy_upgrade("hull", ctx, prog)
        self.assertTrue(bought)
        self.assertGreater(ctx.upgrade_levels["hull"], 1)

        # Weapon purchase & unlock
        unlocked = gc.unlock_weapon("beam", ctx)
        self.assertTrue(unlocked)
        self.assertIn("beam", ctx.unlocked_weapons)

        # Next mission sequence
        next_m = gc.get_next_mission_id(None)
        self.assertIsNotNone(next_m)

    def test_input_controller_canvas_projection(self):
        """Verifies InputController properly scales coordinates from screen to 1280x720 canvas."""
        # 1:1 scale at 1280x720
        cx, cy = InputController.get_canvas_mouse_pos(1280, 720, screen_pos=(640, 360))
        self.assertEqual((cx, cy), (640, 360))

        # 2:1 scale at 2560x1440
        cx2, cy2 = InputController.get_canvas_mouse_pos(2560, 1440, screen_pos=(1280, 720))
        self.assertEqual((cx2, cy2), (640, 360))

    def test_game_backward_compatible_methods(self):
        """Verifies Game facades work identically for tests."""
        game = Game(test_mode=True)
        game.context.scrap = 5000
        game.context.upgrade_levels["hull"] = 1
        if "beam" in game.context.unlocked_weapons:
            game.context.unlocked_weapons.remove("beam")

        self.assertTrue(game.buy_upgrade("hull"))
        self.assertTrue(game.unlock_weapon("beam"))

        game.start_phase5_mission("S1_M1")
        self.assertEqual(game.context.state, STATE_PLAYING)
        self.assertIsNotNone(game.context.player)
        self.assertTrue(game.context.player.alive)

        # Update tick
        game.update(0.016)
        self.assertGreater(game.context.player.pos.x, 0)


if __name__ == "__main__":
    unittest.main()
