import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.game_state import (
    STATE_MENU, STATE_SAVE_SELECT, STATE_DRONE_SELECT, STATE_SECTOR_SELECT,
    STATE_MISSION_BRIEFING, STATE_PLAYING, STATE_PAUSED, STATE_HANGAR, STATE_MISSION_COMPLETE
)
from src.entities.enemy import Enemy
from src.data.game_data import TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER


class TestGameplayFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context
        self.ctx.upgrade_levels = {}
        self.ctx.scrap = 5000

    def test_full_player_journey_e2e(self):
        """Verify the complete player journey through public game transitions and mechanics."""
        game = self.game
        ctx = self.ctx

        # 1. Main Menu
        game.state_manager.change_state(STATE_MENU)
        game.update(0.016)
        game.render()
        self.assertEqual(ctx.state, STATE_MENU)

        # 2. Save Select
        game.state_manager.change_state(STATE_SAVE_SELECT)
        game.update(0.016)
        game.render()
        game.select_save_slot(0)
        ctx.upgrade_levels = {}
        ctx.scrap = 5000

        # 3. Drone Select
        game.state_manager.change_state(STATE_DRONE_SELECT)
        game.update(0.016)
        game.render()
        ctx.selected_drone = "interceptor"
        self.assertEqual(ctx.selected_drone, "interceptor")

        # 4. Sector / Mission Select & Briefing -> Start S1_M1
        game.state_manager.change_state(STATE_SECTOR_SELECT)
        game.update(0.016)
        game.render()

        game.state_manager.change_state(STATE_MISSION_BRIEFING)
        game.update(0.016)
        game.render()

        game.start_phase5_mission("S1_M1")
        self.assertEqual(ctx.state, STATE_PLAYING)
        self.assertEqual(ctx.campaign_state.current_mission, "S1_M1")

        # 5. In-game Combat Simulation
        # Player movement & Aim
        ctx.player.pos = pygame.Vector2(500.0, 360.0)
        bullets = ctx.player.shoot((800.0, 360.0), level=1, targets_group=ctx.target_group)
        for b in bullets:
            ctx.bullet_group.add(b)
        self.assertGreater(len(ctx.bullet_group), 0)

        # Weapon Switching
        initial_weapon = ctx.player.active_weapon
        ctx.player.cycle_weapon()
        self.assertNotEqual(ctx.player.active_weapon, initial_weapon)

        # Abilities Activation
        self.assertTrue(ctx.player.trigger_roll(1.0))
        self.assertTrue(ctx.player.trigger_cloak())
        ctx.player.trigger_overclock(4.0)
        self.assertGreater(ctx.player.overclock_timer, 0.0)

        # Spawn hostile targets and engage
        enemy = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(550.0, 360.0))
        ctx.target_group.add(enemy)

        # Update combat simulation
        game.combat_system.update_combat(0.016)
        game.update(0.016)
        game.render()

        # 6. Mission Complete through gameplay logic
        # Satisfy combat director & clear living enemies
        game.combat_director.state = "complete"
        ctx.target_group.empty()

        # Update triggers mission completion flow in MissionSystem & GameplayController
        game.update(0.016)
        self.assertEqual(ctx.state, STATE_MISSION_COMPLETE)
        self.assertIn("S1_M1", ctx.campaign_state.completed_missions)

        # 7. Transition to Hangar
        game.state_manager.change_state(STATE_HANGAR)
        game.update(0.016)
        game.render()
        self.assertEqual(ctx.state, STATE_HANGAR)

        # Buy upgrades in Hangar
        initial_battery = ctx.upgrade_levels.get("battery", 0)
        bought = game.buy_upgrade("battery")
        self.assertTrue(bought)
        self.assertGreater(ctx.upgrade_levels["battery"], initial_battery)

    def test_pause_and_resume_flow(self):
        """Verify that pausing freezes gameplay simulation and resuming continues correctly."""
        game = self.game
        ctx = self.ctx

        game.start_phase5_mission("S1_M1")
        self.assertEqual(ctx.state, STATE_PLAYING)

        initial_p_pos = pygame.Vector2(ctx.player.pos)

        # Pause game
        game.state_manager.change_state(STATE_PAUSED)
        game.update(0.1)  # 100ms in paused state
        game.render()

        # Position should not have moved by gameplay physics
        self.assertEqual(ctx.player.pos, initial_p_pos)

        # Resume game
        game.state_manager.change_state(STATE_PLAYING)
        game.update(0.016)
        game.render()
        self.assertEqual(ctx.state, STATE_PLAYING)


if __name__ == "__main__":
    unittest.main()
