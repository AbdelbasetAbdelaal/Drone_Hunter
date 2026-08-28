"""
================================================================================
          PHASE 1 ARCHITECTURE REGRESSION & CONTROLLER TESTS
================================================================================
Validates that GameStateManager, SaveController, GameplayController,
InputController, and Game orchestrate cleanly without circular imports,
and verifies dependency decoupling: GameplayController & InputController
operate via explicit contexts (GameplayContext, InputHandlingContext)
and DO NOT require a Game instance.
"""

import os
import sys
import unittest
import inspect
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.core import (
    Game, GameStateManager, SaveController, GameplayController, InputController,
    GameplayContext, InputHandlingContext,
    GameState, STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_SECTOR_SELECT,
    STATE_SAVE_SELECT, STATE_SETTINGS, STATE_DRONE_SELECT
)
from src.core.game_context import GameContext
from src.systems.save_system import SaveSystem
from src.systems.progression_system import ProgressionSystem
from src.systems.combat_system import CombatSystem
from src.systems.mission_system import MissionSystem
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem
from src.systems.objective_system import ObjectiveSystem
from src.systems.achievement_system import AchievementSystem
from src.systems.spawn_system import Spawner
from src.rendering.particles import ParticleManager
from src.rendering.camera import Camera2D
from src.input.input_manager import InputManager


class TestPhase1Architecture(unittest.TestCase):

    def setUp(self):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

    def tearDown(self):
        for f in ["save_data.json", "save_slot_0.json", "save_slot_1.json", "save_slot_2.json", "save_slot_3.json"]:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass

    def test_no_circular_imports(self):
        """Verifies all core modules can be imported independently without circular dependencies."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", "import src.core.game_state_manager; import src.core.save_controller; import src.core.gameplay_controller; import src.core.input_controller; import src.core.gameplay_context; import src.core.game"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Import check failed with stderr: {result.stderr}")

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

    def test_gameplay_controller_does_not_require_game(self):
        """A. Proves GameplayController operates purely via GameplayContext without any Game instance."""
        ctx = GameContext()
        prog = ProgressionSystem(ctx.campaign_state)
        pm = ParticleManager()
        cam = Camera2D()
        enc = EncounterSystem()
        cd = CombatDirector(enc, test_mode=True)
        ms = MissionSystem()
        objs = ObjectiveSystem()
        cs = CombatSystem(ctx)
        spw = Spawner()
        ach = AchievementSystem()

        gp_ctx = GameplayContext(
            context=ctx, progression=prog, particle_manager=pm, camera=cam,
            spawner=spw, encounter_system=enc, combat_director=cd,
            mission_system=ms, objective_system=objs,
            combat_system=cs, achievement_system=ach
        )

        gc = GameplayController(progression_system=prog)
        gc.start_mission("S1_M1", gp_ctx=gp_ctx)

        self.assertEqual(ctx.state, STATE_PLAYING)
        self.assertIsNotNone(ctx.player)
        self.assertTrue(ctx.player.alive)

        # Upgrade through GameplayContext
        ctx.scrap = 5000
        ctx.upgrade_levels["hull"] = 1
        self.assertTrue(gc.buy_upgrade("hull", gp_ctx=gp_ctx))
        self.assertGreater(ctx.upgrade_levels["hull"], 1)

        # Run gameplay update loop tick without Game
        gc.update_gameplay(0.016, gp_ctx)
        self.assertGreater(ctx.player.pos.x, 0)

    def test_input_controller_does_not_require_game(self):
        """B. Proves InputController operates purely via InputHandlingContext without any Game instance."""
        ctx = GameContext()
        ctx.state = STATE_MENU
        im = InputManager()

        saved_flags = []
        started_missions = []

        input_ctx = InputHandlingContext(
            context=ctx,
            input_manager=im,
            ui_rects_cache={"start": pygame.Rect(100, 100, 200, 50)},
            save_callback=lambda: saved_flags.append(True),
            start_mission_callback=lambda m_id: started_missions.append(m_id),
        )

        ic = InputController()
        # Simulate click on start button
        ic._handle_mouse_click(150, 125, input_ctx)
        self.assertEqual(ctx.state, STATE_DRONE_SELECT)

        # Simulate keyboard back navigation
        event_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        ic._handle_keyboard_menu_navigation(event_esc, input_ctx)
        self.assertEqual(ctx.state, STATE_MENU)

    def test_controller_apis_use_explicit_contexts_not_positional_explosion(self):
        """9. Verifies controller APIs accept explicit context objects and avoid 15+ positional parameters."""
        sig = inspect.signature(GameplayController.update_gameplay)
        param_names = list(sig.parameters.keys())
        # First two parameters should be (self, dt, gp_ctx)
        self.assertEqual(param_names[0], "self")
        self.assertEqual(param_names[1], "dt")
        self.assertEqual(param_names[2], "gp_ctx")

    def test_game_composition_root_creates_contexts(self):
        """Verifies Game composition root creates valid GameplayContext and InputHandlingContext."""
        game = Game(test_mode=True)
        gp_ctx = game.create_gameplay_context()
        self.assertIsInstance(gp_ctx, GameplayContext)
        self.assertEqual(gp_ctx.context, game.context)
        self.assertEqual(gp_ctx.progression, game.progression)

        input_ctx = game.create_input_handling_context()
        self.assertIsInstance(input_ctx, InputHandlingContext)
        self.assertEqual(input_ctx.context, game.context)
        self.assertEqual(input_ctx.input_manager, game.input_manager)

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

        # Player class cycling
        p = game.context.player
        initial_class = p.drone_class
        next_class = p.cycle_drone_class()
        self.assertNotEqual(p.drone_class, initial_class)

        # Update tick
        game.update(0.016)
        self.assertGreater(game.context.player.pos.x, 0)


if __name__ == "__main__":
    unittest.main()
