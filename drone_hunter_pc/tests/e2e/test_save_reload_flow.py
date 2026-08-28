import os
import sys
import json
import shutil
import tempfile
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.game_context import GameContext
from src.core.campaign_state import CampaignState
from src.systems.save_system import SaveSystem
from src.core.save_controller import SaveController


class TestSaveReloadFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_persistence_lifecycle(self):
        """Verify full player persistence lifecycle across game destruction and re-instantiation."""
        save_sys = SaveSystem(slot_index=0)
        save_sys.base_dir = self.test_dir
        save_sys.set_slot(0)
        ctrl = SaveController(save_system=save_sys, initial_slot=0)

        # 1. Player starts new game and progresses
        ctx = GameContext()
        ctx.selected_drone = "interceptor"
        ctx.scrap = 3500
        ctx.highscore = 42000
        ctx.difficulty_mode = 2
        ctx.campaign_state.complete_mission("S1_M1")
        ctx.campaign_state.complete_mission("S1_M2")
        ctx.campaign_state.set_current_mission("S1_M3")
        ctx.upgrade_levels["battery"] = 3
        ctx.upgrade_levels["overdrive"] = 2
        ctx.unlocked_weapons = ["pulse", "scatter", "missile", "plasma"]
        ctx.weapon_upgrade_levels["plasma"] = 2

        # 2. Save progress to slot 0
        success = ctrl.save_current_progress(ctx)
        self.assertTrue(success)

        # 3. Completely destroy runtime objects and load from disk into new context
        new_save_sys = SaveSystem(slot_index=0)
        new_save_sys.base_dir = self.test_dir
        new_save_sys.set_slot(0)
        new_ctrl = SaveController(save_system=new_save_sys, initial_slot=0)

        fresh_ctx = GameContext()
        loaded_data = new_ctrl.load_slot(0, fresh_ctx)

        # 4. Verify all fields restored faithfully
        self.assertEqual(fresh_ctx.selected_drone, "interceptor")
        self.assertEqual(fresh_ctx.scrap, 3500)
        self.assertEqual(fresh_ctx.highscore, 42000)
        self.assertEqual(fresh_ctx.difficulty_mode, 2)
        self.assertEqual(fresh_ctx.campaign_state.current_mission, "S1_M3")
        self.assertIn("S1_M1", fresh_ctx.campaign_state.completed_missions)
        self.assertIn("S1_M2", fresh_ctx.campaign_state.completed_missions)
        self.assertEqual(fresh_ctx.upgrade_levels["battery"], 3)
        self.assertEqual(fresh_ctx.upgrade_levels["overdrive"], 2)
        self.assertIn("plasma", fresh_ctx.unlocked_weapons)
        self.assertEqual(fresh_ctx.weapon_upgrade_levels["plasma"], 2)

    def test_corrupted_and_future_version_recovery(self):
        """Verify corrupted JSON and unsupported future save_version do not crash and return safe defaults."""
        save_sys = SaveSystem(save_filename="future_corrupt.json")
        save_sys.base_dir = self.test_dir
        save_sys.save_path = os.path.join(self.test_dir, "future_corrupt.json")
        save_sys.temp_path = save_sys.save_path + ".tmp"

        # Case 1: Future save version
        with open(save_sys.save_path, "w", encoding="utf-8") as f:
            json.dump({"save_version": 9999, "scrap": 999999}, f)

        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 0)
        self.assertEqual(loaded["campaign_state"]["current_mission"], "S1_M1")

        # Case 2: Corrupted JSON data
        with open(save_sys.save_path, "w", encoding="utf-8") as f:
            f.write("CORRUPTED %%% JSON ### DATA")

        loaded = save_sys.load()
        self.assertEqual(loaded["scrap"], 0)
        self.assertEqual(loaded["campaign_state"]["current_mission"], "S1_M1")


if __name__ == "__main__":
    unittest.main()
