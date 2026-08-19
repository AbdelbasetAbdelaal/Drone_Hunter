import unittest
import pygame
import os
import json

from src.core.game_context import GameContext
from src.systems.mission_system import MissionSystem, STATE_AVAILABLE, STATE_LOCKED, STATE_COMPLETED, STATE_ACTIVE
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem
from src.data.mission_data import SECTORS_PHASE5, MISSIONS
from src.data.game_data import TARGET_TYPE_SCOUT

class MockEncounterSystem:
    def __init__(self):
        self.is_complete = False
        self.state = "idle"
    def reset(self):
        self.is_complete = False
    def start(self, config):
        pass
    def update(self, dt, ctx):
        if self.is_complete:
            self.state = "idle"
        else:
            self.state = "encounter"

class TestPhase5Missions(unittest.TestCase):
    def setUp(self):
        pygame.init()
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.set_mode((1280, 720))
        
        self.ctx = GameContext()
        self.mission_sys = MissionSystem()
        self.enc_sys = EncounterSystem()
        self.director = CombatDirector(self.enc_sys)
        
    def tearDown(self):
        pygame.quit()

    def test_content_validation(self):
        # Verify 5 sectors and 25 missions exactly
        self.assertEqual(len(SECTORS_PHASE5), 5)
        self.assertEqual(len(MISSIONS), 25)
        
        # Verify correct distribution
        sector_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for m in MISSIONS:
            sector_counts[m["sector_id"]] += 1
        
        for k, v in sector_counts.items():
            self.assertEqual(v, 5)

        # Check for unique IDs
        ids = [m["id"] for m in MISSIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_initial_state(self):
        # Newly created GameContext should have default Phase 5 unlocks
        self.assertEqual(self.ctx.missions["current_sector"], 1)
        self.assertEqual(self.ctx.missions["unlocked"], ["S1_M1"])
        self.assertEqual(self.ctx.sector_progress["unlocked"], [1])
        self.assertEqual(self.ctx.missions["completed"], [])
        
        self.assertEqual(self.mission_sys.get_mission_state(self.ctx, "S1_M1"), STATE_AVAILABLE)
        self.assertEqual(self.mission_sys.get_mission_state(self.ctx, "S1_M2"), STATE_LOCKED)
        self.assertEqual(self.mission_sys.get_mission_state(self.ctx, "S2_M1"), STATE_LOCKED)

    def test_mission_progression_unlocks(self):
        # Complete S1_M1
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        self.assertEqual(self.mission_sys.active_mission_id, "S1_M1")
        self.assertEqual(self.mission_sys.state, STATE_ACTIVE)
        
        # Force complete
        self.mission_sys._trigger_success(self.ctx)
        
        self.assertEqual(self.mission_sys.state, STATE_COMPLETED)
        self.assertTrue(self.mission_sys.is_mission_success)
        self.assertIn("S1_M1", self.ctx.missions["completed"])
        self.assertEqual(self.mission_sys.get_mission_state(self.ctx, "S1_M1"), STATE_COMPLETED)
        
        # Should unlock M2
        self.assertIn("S1_M2", self.ctx.missions["unlocked"])
        self.assertEqual(self.mission_sys.get_mission_state(self.ctx, "S1_M2"), STATE_AVAILABLE)

    def test_sector_completion(self):
        # Complete up to S1_M4
        self.ctx.missions["unlocked"] = ["S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5"]
        self.ctx.missions["completed"] = ["S1_M1", "S1_M2", "S1_M3", "S1_M4"]
        
        self.assertEqual(self.ctx.scrap, 0)
        
        self.mission_sys.start_mission(self.ctx, "S1_M5", self.director)
        self.mission_sys._trigger_success(self.ctx)
        
        # M5 complete, Sector 1 complete
        self.assertIn("S1_M5", self.ctx.missions["completed"])
        self.assertIn(1, self.ctx.sector_progress["completed"])
        
        # Should unlock Sector 2 and S2_M1
        self.assertIn(2, self.ctx.sector_progress["unlocked"])
        self.assertIn("S2_M1", self.ctx.missions["unlocked"])
        
        # Check scrap rewards: M5 (Diff 3) = 400, Sector 1 Bonus = 500 => Total 900
        self.assertEqual(self.ctx.scrap, 900)

    def test_reward_duplication_protection(self):
        # Complete S1_M1 first time
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        self.mission_sys._trigger_success(self.ctx)
        
        # S1_M1 is diff 1 => 150 scrap
        self.assertEqual(self.ctx.scrap, 150)
        
        # Start it again
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        self.mission_sys._trigger_success(self.ctx)
        
        # Scrap should NOT increase from the mission reward
        self.assertEqual(self.ctx.scrap, 150)

    def test_survive_objective(self):
        self.mission_sys.start_mission(self.ctx, "S2_M4", self.director) # Survive for 45s
        
        self.assertEqual(self.mission_sys.survive_timer, 45.0)
        self.assertTrue(self.director.loop_encounters)
        
        completed = self.mission_sys.update(44.0, self.ctx, self.director)
        self.assertFalse(completed)
        self.assertEqual(self.mission_sys.state, STATE_ACTIVE)
        
        completed = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertTrue(completed)
        self.assertEqual(self.mission_sys.state, STATE_COMPLETED)

    def test_complete_encounters_objective(self):
        self.mission_sys.start_mission(self.ctx, "S1_M3", self.director)
        
        completed = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertFalse(completed)
        
        # Force combat director to finish
        self.director.state = "complete"
        completed = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertTrue(completed)

    def test_destroy_all_objective(self):
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        
        # Director is complete, but enemies still alive
        self.director.state = "complete"
        
        class DummyEnemy(pygame.sprite.Sprite):
            def __init__(self):
                super().__init__()
        
        enemy = DummyEnemy()
        self.ctx.target_group.add(enemy)
        
        completed = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertFalse(completed)
        
        # Kill enemy
        enemy.kill()
        
        completed = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertTrue(completed)

if __name__ == '__main__':
    unittest.main()
