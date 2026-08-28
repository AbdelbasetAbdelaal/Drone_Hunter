import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.campaign_state import CampaignState
from src.core.game_state import STATE_VICTORY, STATE_PLAYING, STATE_MISSION_COMPLETE


class TestCampaignFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context
        self.ctx.campaign_state = CampaignState()

    def test_gameplay_driven_mission_progression(self):
        """Verify real gameplay loop drives mission completion and unlocks next mission."""
        self.game.start_phase5_mission("S1_M1")
        self.assertEqual(self.ctx.state, STATE_PLAYING)
        self.assertEqual(self.ctx.campaign_state.current_mission, "S1_M1")

        # Fulfill combat objective
        self.game.combat_director.state = "complete"
        self.ctx.target_group.empty()

        # Update gameplay loop
        self.game.update(0.016)

        self.assertEqual(self.ctx.state, STATE_MISSION_COMPLETE)
        self.assertIn("S1_M1", self.ctx.campaign_state.completed_missions)
        self.assertIn("S1_M2", self.ctx.campaign_state.unlocked_missions)

        # Launch newly unlocked S1_M2
        self.game.start_phase5_mission("S1_M2")
        self.assertEqual(self.ctx.state, STATE_PLAYING)
        self.assertEqual(self.ctx.campaign_state.current_mission, "S1_M2")

    def test_linear_sector1_progression(self):
        """Verify S1_M1 -> S1_M2 -> S1_M3 -> S1_M4 -> S1_M5 -> S2_M1 progression."""
        cs: CampaignState = self.ctx.campaign_state

        self.assertEqual(cs.current_mission, "S1_M1")
        self.assertIn("S1_M1", cs.unlocked_missions)
        self.assertIn(1, cs.unlocked_sectors)

        # Complete S1_M1 through S1_M4
        for m in range(1, 5):
            m_id = f"S1_M{m}"
            next_m_id = f"S1_M{m + 1}"
            cs.complete_mission(m_id)
            self.assertIn(m_id, cs.completed_missions)
            self.assertIn(next_m_id, cs.unlocked_missions)

        # Complete S1_M5 -> Sector 2 unlocks and S2_M1 unlocks
        cs.complete_mission("S1_M5")
        self.assertIn("S1_M5", cs.completed_missions)
        self.assertIn(1, cs.completed_sectors)
        self.assertIn(2, cs.unlocked_sectors)
        self.assertIn("S2_M1", cs.unlocked_missions)

    def test_full_campaign_completion_and_victory(self):
        """Verify completing all 25 missions completes campaign and allows victory."""
        cs: CampaignState = self.ctx.campaign_state

        # Complete all 5 sectors (5 missions each)
        for s in range(1, 6):
            for m in range(1, 6):
                cs.complete_mission(f"S{s}_M{m}")

        self.assertTrue(cs.campaign_completed)
        self.assertEqual(len(cs.completed_missions), 25)
        self.assertEqual(len(cs.completed_sectors), 5)

        # Set current mission to final mission S5_M5
        cs.set_current_mission("S5_M5")
        self.assertEqual(self.ctx.current_sector_idx, 4)
        self.assertEqual(self.ctx.current_sub_level, 5)

        # Launch next stage triggers Campaign Victory
        self.game.start_next_stage()
        self.assertEqual(self.ctx.state, STATE_VICTORY)

    def test_new_game_plus_cycle(self):
        """Verify starting New Game Plus resets mission tree and increments NG+ multipliers."""
        cs: CampaignState = self.ctx.campaign_state

        # Complete campaign
        for s in range(1, 6):
            for m in range(1, 6):
                cs.complete_mission(f"S{s}_M{m}")

        self.assertTrue(cs.campaign_completed)
        self.assertEqual(cs.new_game_plus_count, 0)

        # Start NG+
        self.game.start_new_game_plus()
        self.assertEqual(cs.new_game_plus_count, 1)
        self.assertEqual(cs.current_mission, "S1_M1")
        self.assertEqual(cs.completed_missions, [])
        self.assertEqual(cs.completed_sectors, [])
        self.assertGreater(self.ctx.ng_plus_enemy_hp_mult, 1.0)
        self.assertGreater(self.ctx.ng_plus_scrap_mult, 1.0)


if __name__ == "__main__":
    unittest.main()
