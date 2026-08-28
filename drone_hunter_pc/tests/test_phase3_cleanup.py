"""
===============================================================================
               DRONE HUNTER 2D - PHASE 3 CLEANUP TEST SUITE
===============================================================================
Verifies:
1. Complete 5 sectors x 5 missions campaign sequence (S1_M1 -> S5_M5 -> Victory).
2. CampaignState as sole authoritative runtime container for campaign progression.
3. Scrap economy exclusivity (no active runtime coins, coin powerups grant scrap).
4. Save loading compatibility at persistence boundary for historical save files.
5. GameplayController standardization on GameplayContext.
"""

import os
import sys
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
pygame.init()

from src.core.game_context import GameContext
from src.core.campaign_state import CampaignState
from src.systems.progression_system import ProgressionSystem
from src.systems.mission_system import MissionSystem, STATE_AVAILABLE, STATE_COMPLETED, STATE_LOCKED
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem
from src.systems.save_system import SaveSystem
from src.core.save_controller import SaveController
from src.core.gameplay_controller import GameplayController
from src.core.gameplay_context import GameplayContext
from src.entities.powerup import PowerupItem
from src.systems.combat_system import CombatSystem
from src.entities.player import Player


class TestPhase3CampaignProgression(unittest.TestCase):
    def test_five_sector_five_mission_sequence(self):
        """Verify progression cleanly iterates 5 missions per sector to 25 total missions."""
        cs = CampaignState()
        prog = ProgressionSystem(cs)

        current_sec = 0
        current_stg = 1

        for expected_sec in range(5):
            for expected_stg in range(1, 6):
                self.assertEqual(current_sec, expected_sec)
                self.assertEqual(current_stg, expected_stg)
                mission_id = f"S{expected_sec + 1}_M{expected_stg}"
                self.assertTrue(prog.is_stage_unlocked(expected_sec, expected_stg), f"{mission_id} should be unlocked")

                next_sec, next_stg, is_victory = prog.unlock_next_stage(current_sec, current_stg)

                if expected_sec == 4 and expected_stg == 5:
                    self.assertTrue(is_victory, "S5_M5 completion must trigger campaign victory")
                    self.assertTrue(cs.campaign_completed)
                else:
                    self.assertFalse(is_victory)
                    current_sec = next_sec
                    current_stg = next_stg

        self.assertEqual(len(cs.completed_missions), 25)
        self.assertEqual(len(cs.unlocked_sectors), 5)


class TestPhase3SingleAuthoritativeCampaignState(unittest.TestCase):
    def test_game_context_owns_sole_authoritative_campaign_state(self):
        ctx = GameContext()
        self.assertIsInstance(ctx.campaign_state, CampaignState)
        self.assertFalse(hasattr(ctx, "_missions_dict"))
        self.assertFalse(hasattr(ctx, "_sector_progress_dict"))

        # Properties forward directly
        ctx.current_sector_idx = 2
        ctx.current_sub_level = 3
        self.assertEqual(ctx.campaign_state.current_mission, "S3_M3")
        self.assertEqual(ctx.campaign_state.current_sector_idx, 2)
        self.assertEqual(ctx.campaign_state.current_sub_level, 3)

        ctx.campaign_completed = True
        self.assertTrue(ctx.campaign_state.campaign_completed)

        ctx.new_game_plus_count = 2
        self.assertEqual(ctx.campaign_state.new_game_plus_count, 2)

    def test_mission_system_uses_campaign_state(self):
        ctx = GameContext()
        ms = MissionSystem()
        director = CombatDirector(EncounterSystem())

        self.assertEqual(ms.get_mission_state(ctx, "S1_M1"), STATE_AVAILABLE)
        self.assertEqual(ms.get_mission_state(ctx, "S1_M2"), STATE_LOCKED)

        ms.start_mission(ctx, "S1_M1", director)
        ms._trigger_success(ctx)

        self.assertEqual(ms.get_mission_state(ctx, "S1_M1"), STATE_COMPLETED)
        self.assertEqual(ms.get_mission_state(ctx, "S1_M2"), STATE_AVAILABLE)
        self.assertIn("S1_M1", ctx.campaign_state.completed_missions)
        self.assertIn("S1_M2", ctx.campaign_state.unlocked_missions)


class TestPhase3ScrapEconomy(unittest.TestCase):
    def test_powerup_coin_grants_scrap(self):
        ctx = GameContext()
        ctx.player = Player((640, 360))
        ctx.scrap = 100
        cs = CombatSystem(ctx)

        # Create coin powerup
        coin_powerup = PowerupItem((640, 360), "coin")
        ctx.powerup_group.add(coin_powerup)

        # Update combat system collisions
        cs.update_combat(0.016)

        # Should add 50 scrap
        self.assertEqual(ctx.scrap, 150)
        self.assertFalse(hasattr(ctx, "coins"))


class TestPhase3LegacySaveCompatibility(unittest.TestCase):
    def setUp(self):
        self.test_slot = 2
        self.save_system = SaveSystem(slot_index=self.test_slot)
        self.save_controller = SaveController(self.save_system, initial_slot=self.test_slot)
        if os.path.exists(self.save_system.save_path):
            try: os.remove(self.save_system.save_path)
            except Exception: pass

    def tearDown(self):
        if os.path.exists(self.save_system.save_path):
            try: os.remove(self.save_system.save_path)
            except Exception: pass
        if os.path.exists(self.save_system.temp_path):
            try: os.remove(self.save_system.temp_path)
            except Exception: pass

    def test_load_legacy_save_format(self):
        """Verify historical save data with legacy fields is mapped correctly."""
        legacy_data = {
            "coins": 450,
            "scrap": 0,
            "highscore": 12000,
            "missions": {
                "current_sector": 2,
                "current_mission": 3,
                "completed": ["S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5", "S2_M1", "S2_M2"],
                "unlocked": ["S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5", "S2_M1", "S2_M2", "S2_M3"],
            },
            "sector_progress": {
                "completed": [1],
                "unlocked": [1, 2],
            },
            "campaign_completed": False,
            "new_game_plus_count": 0,
            "upgrades": {"hull": 2, "energy": 2},
        }
        self.save_system.save(legacy_data)

        ctx = GameContext()
        self.save_controller.load_slot(self.test_slot, ctx)

        # Legacy coins should be mapped to scrap if scrap is 0
        self.assertEqual(ctx.scrap, 450)
        self.assertEqual(ctx.highscore, 12000)
        self.assertEqual(ctx.campaign_state.current_sector_idx, 1)
        self.assertEqual(ctx.campaign_state.current_sub_level, 3)
        self.assertEqual(ctx.campaign_state.current_mission, "S2_M3")
        self.assertIn("S2_M2", ctx.campaign_state.completed_missions)
        self.assertIn("S2_M3", ctx.campaign_state.unlocked_missions)
        self.assertIn(1, ctx.campaign_state.completed_sectors)
        self.assertIn(2, ctx.campaign_state.unlocked_sectors)


class TestPhase3GameplayControllerContext(unittest.TestCase):
    def test_gameplay_controller_methods_require_gameplay_context(self):
        controller = GameplayController()
        ctx = GameContext()
        gp_ctx = GameplayContext(context=ctx)

        # start_stage and start_mission require gp_ctx
        with self.assertRaises(ValueError):
            controller.start_mission()

        with self.assertRaises(ValueError):
            controller.start_stage()

        # Valid call with GameplayContext succeeds
        controller.start_stage(0, 1, gp_ctx=gp_ctx)
        self.assertEqual(ctx.current_sector_idx, 0)
        self.assertEqual(ctx.current_sub_level, 1)


if __name__ == "__main__":
    unittest.main()
