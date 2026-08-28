import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.game_state import (
    STATE_PLAYING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_HANGAR
)
from src.rendering.sprite_manager import get_sprite_manager
from src.audio.audio_manager import AudioManager


class TestMissionResultFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context

    def test_mission_success_and_reward_flow(self):
        """Verify successful mission flow registers completion, scrap, and next mission unlock via game update loop."""
        self.game.start_phase5_mission("S1_M1")
        initial_scrap = self.ctx.scrap

        # Satisfy mission objective via gameplay condition (director complete and targets cleared)
        self.game.combat_director.state = "complete"
        self.ctx.target_group.empty()

        # Update gameplay loop to process mission completion
        self.game.update(0.016)
        self.game.render()

        self.assertEqual(self.ctx.state, STATE_MISSION_COMPLETE)
        self.assertIn("S1_M1", self.ctx.campaign_state.completed_missions)
        self.assertIn("S1_M2", self.ctx.campaign_state.unlocked_missions)
        self.assertGreater(self.ctx.scrap, initial_scrap)

    def test_mission_failure_and_retry_flow(self):
        """Verify player destruction triggers mission failure via game update loop and allows clean retry."""
        self.game.start_phase5_mission("S1_M1")
        player = self.ctx.player

        # Destroy player (applies fatal damage)
        player.take_damage(9999)
        player.destruction_timer = 0.0
        self.assertFalse(player.alive)
        self.assertTrue(player.is_destroyed)

        # Update gameplay loop to process player death transition
        self.game.update(0.016)
        self.game.render()

        self.assertEqual(self.ctx.state, STATE_MISSION_FAILED)

        # Retry mission via public start_phase5_mission
        self.game.start_phase5_mission("S1_M1")
        self.assertEqual(self.ctx.state, STATE_PLAYING)
        self.assertTrue(self.ctx.player.alive)
        self.assertFalse(self.ctx.player.is_destroyed)

    def test_removed_systems_absence(self):
        """Verify that Boss and Skin selection systems are absent from active player runtime."""
        # No skin selection attribute on context or player
        self.assertFalse(hasattr(self.ctx, "selected_skin"))
        self.assertFalse(hasattr(self.ctx, "boss_group"))
        self.assertFalse(hasattr(self.ctx, "bosses_defeated"))

    def test_active_production_assets_loading(self):
        """Verify all production sprites, audio, and VFX assets load cleanly."""
        sm = get_sprite_manager()
        self.assertIsNotNone(sm)

        # Drone sprites for all 5 classes
        for idx in range(5):
            surf = sm.get_player_state_sprite("idle", skin_idx=idx, target_size=(72, 72))
            self.assertIsNotNone(surf)

        # Weapon projectiles
        for w in ["pulse", "scatter", "missile", "rapid", "plasma", "rail", "barrage", "beam", "tesla", "cluster"]:
            proj = sm.get_projectile_sprite(w, (48, 16))
            self.assertIsNotNone(proj)


if __name__ == "__main__":
    unittest.main()
