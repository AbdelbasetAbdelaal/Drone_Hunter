"""
===============================================================================
                     DRONE HUNTER 2D - CAMPAIGN STATE TESTS
===============================================================================
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.core.campaign_state import CampaignState


class TestCampaignStateCreation(unittest.TestCase):
    def test_default_initial_state(self):
        cs = CampaignState()
        self.assertEqual(cs.current_mission, "S1_M1")
        self.assertEqual(cs.current_sector_idx, 0)
        self.assertEqual(cs.current_sub_level, 1)
        self.assertEqual(cs.completed_missions, [])
        self.assertEqual(cs.unlocked_missions, ["S1_M1"])
        self.assertEqual(cs.completed_sectors, [])
        self.assertEqual(cs.unlocked_sectors, [1])
        self.assertFalse(cs.campaign_completed)
        self.assertEqual(cs.new_game_plus_count, 0)

    def test_set_current_mission(self):
        cs = CampaignState()
        cs.set_current_mission("S3_M2")
        self.assertEqual(cs.current_mission, "S3_M2")
        self.assertEqual(cs.current_sector_idx, 2)
        self.assertEqual(cs.current_sub_level, 2)

    def test_set_current_sector_and_stage(self):
        cs = CampaignState()
        cs.set_current_sector_and_stage(4, 3)
        self.assertEqual(cs.current_mission, "S5_M3")
        self.assertEqual(cs.current_sector_idx, 4)
        self.assertEqual(cs.current_sub_level, 3)


class TestCampaignStateMissionCompletion(unittest.TestCase):
    def test_complete_mission_adds_to_completed(self):
        cs = CampaignState()
        cs.complete_mission("S1_M1")
        self.assertTrue(cs.is_mission_completed("S1_M1"))
        self.assertIn("S1_M1", cs.completed_missions)

    def test_complete_mission_unlocks_next(self):
        cs = CampaignState()
        cs.complete_mission("S1_M1")
        self.assertIn("S1_M2", cs.unlocked_missions)

    def test_complete_mission_does_not_duplicate(self):
        cs = CampaignState()
        cs.complete_mission("S1_M1")
        cs.complete_mission("S1_M1")
        self.assertEqual(cs.completed_missions.count("S1_M1"), 1)

    def test_complete_sector_5_unlocks_next_sector(self):
        cs = CampaignState()
        cs.unlock_mission("S1_M1")
        cs.unlock_mission("S1_M2")
        cs.unlock_mission("S1_M3")
        cs.unlock_mission("S1_M4")
        cs.unlock_mission("S1_M5")
        cs.complete_mission("S1_M1")
        cs.complete_mission("S1_M2")
        cs.complete_mission("S1_M3")
        cs.complete_mission("S1_M4")
        cs.complete_mission("S1_M5")
        self.assertTrue(cs.is_sector_completed(1))
        self.assertIn(2, cs.unlocked_sectors)
        self.assertIn("S2_M1", cs.unlocked_missions)

    def test_complete_final_sector_marks_campaign_complete(self):
        cs = CampaignState()
        for m in range(1, 6):
            cs.unlock_mission(f"S5_M{m}")
            cs.complete_mission(f"S5_M{m}")
        self.assertTrue(cs.campaign_completed)


class TestCampaignStateUnlocking(unittest.TestCase):
    def test_unlock_mission(self):
        cs = CampaignState()
        cs.unlock_mission("S2_M1")
        self.assertTrue(cs.is_mission_unlocked("S2_M1"))
        self.assertIn("S2_M1", cs.unlocked_missions)

    def test_unlock_sector(self):
        cs = CampaignState()
        cs.unlock_sector(3)
        self.assertTrue(cs.is_sector_unlocked(3))
        self.assertIn(3, cs.unlocked_sectors)


class TestCampaignStateNGPlus(unittest.TestCase):
    def test_start_new_game_plus(self):
        cs = CampaignState()
        cs.complete_mission("S1_M1")
        cs.complete_mission("S1_M2")
        cs.mark_campaign_complete()
        cs.set_current_mission("S5_M5")

        cs.start_new_game_plus()

        self.assertEqual(cs.new_game_plus_count, 1)
        self.assertEqual(cs.completed_missions, [])
        self.assertEqual(cs.completed_sectors, [])
        self.assertEqual(cs.unlocked_sectors, [1])
        self.assertEqual(cs.unlocked_missions, ["S1_M1"])
        self.assertFalse(cs.campaign_completed)
        self.assertEqual(cs.current_mission, "S1_M1")


class TestCampaignStateNextMission(unittest.TestCase):
    def test_next_mission_within_sector(self):
        cs = CampaignState()
        cs.unlock_mission("S1_M1")
        cs.unlock_mission("S1_M2")
        next_id = cs.get_next_mission("S1_M1")
        self.assertEqual(next_id, "S1_M2")

    def test_next_mission_cross_sector(self):
        cs = CampaignState()
        cs.unlock_mission("S1_M1")
        cs.unlock_mission("S1_M2")
        cs.unlock_mission("S1_M3")
        cs.unlock_mission("S1_M4")
        cs.unlock_mission("S1_M5")
        cs.complete_mission("S1_M1")
        cs.complete_mission("S1_M2")
        cs.complete_mission("S1_M3")
        cs.complete_mission("S1_M4")
        cs.complete_mission("S1_M5")
        next_id = cs.get_next_mission("S1_M5")
        self.assertEqual(next_id, "S2_M1")

    def test_next_mission_none_at_end(self):
        cs = CampaignState()
        cs.unlock_mission("S5_M5")
        cs.complete_mission("S5_M1")
        cs.complete_mission("S5_M2")
        cs.complete_mission("S5_M3")
        cs.complete_mission("S5_M4")
        cs.complete_mission("S5_M5")
        next_id = cs.get_next_mission("S5_M5")
        self.assertIsNone(next_id)


class TestCampaignStateValidation(unittest.TestCase):
    def test_valid_state_passes(self):
        cs = CampaignState()
        cs.unlock_mission("S1_M1")
        cs.complete_mission("S1_M1")
        errors = cs.validate()
        self.assertEqual(errors, [])

    def test_completed_mission_not_unlocked_detected(self):
        cs = CampaignState()
        cs._completed_missions.append("S2_M1")
        errors = cs.validate()
        self.assertTrue(any("not unlocked" in e for e in errors))


class TestCampaignStateSerialization(unittest.TestCase):
    def test_round_trip(self):
        cs = CampaignState()
        cs.set_current_mission("S3_M2")
        cs.complete_mission("S1_M1")
        cs.complete_mission("S1_M2")
        cs.unlock_sector(2)
        cs.mark_campaign_complete()
        cs._new_game_plus_count = 2

        data = cs.serialize()
        cs2 = CampaignState.deserialize(data)

        self.assertEqual(cs2.current_mission, "S3_M2")
        self.assertEqual(cs2.current_sector_idx, 2)
        self.assertEqual(cs2.current_sub_level, 2)
        self.assertEqual(cs2.completed_missions, ["S1_M1", "S1_M2"])
        self.assertEqual(cs2.unlocked_sectors, [1, 2])
        self.assertTrue(cs2.campaign_completed)
        self.assertEqual(cs2.new_game_plus_count, 2)

    def test_deserialize_missing_fields(self):
        data = {}
        cs = CampaignState.deserialize(data)
        self.assertEqual(cs.current_mission, "S1_M1")
        self.assertEqual(cs.unlocked_missions, ["S1_M1"])
        self.assertFalse(cs.campaign_completed)


class TestGameContextCampaignStateIntegration(unittest.TestCase):
    def test_context_delegates_to_campaign_state(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        self.assertIsInstance(ctx.campaign_state, CampaignState)
        self.assertEqual(ctx.current_sector_idx, 0)
        self.assertEqual(ctx.current_sub_level, 1)

    def test_context_current_sector_setter_updates_campaign_state(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        ctx.current_sector_idx = 3
        self.assertEqual(ctx.campaign_state.current_sector_idx, 3)

    def test_context_current_sub_level_setter_updates_campaign_state(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        ctx.current_sub_level = 4
        self.assertEqual(ctx.campaign_state.current_sub_level, 4)

    def test_context_unlocked_sectors_property(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        self.assertEqual(ctx.unlocked_sectors, [1])
        ctx.campaign_state.unlock_sector(2)
        self.assertEqual(ctx.unlocked_sectors, [1, 2])

    def test_context_campaign_completed_setter(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        ctx.campaign_completed = True
        self.assertTrue(ctx.campaign_state.campaign_completed)

    def test_context_new_game_plus_count_setter(self):
        from src.core.game_context import GameContext
        ctx = GameContext()
        ctx.new_game_plus_count = 3
        self.assertEqual(ctx.campaign_state.new_game_plus_count, 3)


if __name__ == "__main__":
    unittest.main()
