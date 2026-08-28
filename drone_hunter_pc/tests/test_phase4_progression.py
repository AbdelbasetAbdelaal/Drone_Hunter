import sys
import unittest
import pygame
import json
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.game_context import GameContext
from src.entities.player import Player
from src.systems.progression_system import ProgressionSystem
from src.systems.save_system import SaveSystem
from src.systems.combat_system import CombatSystem
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem, SCOUT_INTRO_ENCOUNTER, SCOUT_SHOOTER_HEAVY_ENCOUNTER
from src.data.game_data import TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY

class MockEnemy(pygame.sprite.Sprite):
    def __init__(self, e_type, hp):
        super().__init__()
        self.enemy_type = e_type
        self.health = hp
        self.alive = True
        self.score_value = 100
        self.rect = pygame.Rect(0,0,10,10)
        self.pos = pygame.Vector2(0,0)
    
    def take_damage(self, dmg, source=""):
        self.health -= dmg
        if self.health <= 0:
            self.alive = False
            return True
        return False

class MockBullet(pygame.sprite.Sprite):
    def __init__(self, dmg):
        super().__init__()
        self.damage = dmg
        self.rect = pygame.Rect(0,0,10,10)
        self.is_piercing = False
    def kill(self):
        pass

class MockEncounterSystem:
    def __init__(self):
        self.is_complete = False
    def reset(self):
        self.is_complete = False
    def start(self, config):
        pass
    def update(self, dt, ctx):
        pass

class TestPhase4Progression(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Set dummy video driver for headless testing
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.set_mode((1280, 720))
        
        self.ctx = GameContext()
        self.ctx.player = Player((640, 360))
        self.progression = ProgressionSystem()
        
        self.test_save_path = "test_phase4_save.json"
        self.save_system = SaveSystem(save_filename=self.test_save_path)

    def tearDown(self):
        if os.path.exists(self.test_save_path):
            os.remove(self.test_save_path)
        pygame.quit()

    def test_progression_system_scrap(self):
        self.assertEqual(self.ctx.scrap, 0)
        self.progression.add_scrap(self.ctx, 1500)
        self.assertEqual(self.ctx.scrap, 1500)
        
        # Test purchasing
        self.assertTrue(self.progression.purchase_upgrade(self.ctx, "hull"))
        # Cost from Level 1 -> 2 is 500
        self.assertEqual(self.ctx.scrap, 1000)
        self.assertEqual(self.ctx.upgrade_levels["hull"], 2)
        
        # Insufficient funds
        self.ctx.scrap = 0
        self.assertFalse(self.progression.purchase_upgrade(self.ctx, "energy"))
        self.progression.add_scrap(self.ctx, 500) # Now 500
        
        # Buy level 2
        self.assertTrue(self.progression.purchase_upgrade(self.ctx, "energy"))
        self.assertEqual(self.ctx.scrap, 0)
        
        # Buy up to max
        self.progression.add_scrap(self.ctx, 10000)
        self.assertTrue(self.progression.purchase_upgrade(self.ctx, "energy")) # Lvl 3 (1000)
        self.assertTrue(self.progression.purchase_upgrade(self.ctx, "energy")) # Lvl 4 (1750)
        self.assertTrue(self.progression.purchase_upgrade(self.ctx, "energy")) # Lvl 5 (2750)
        self.assertEqual(self.ctx.upgrade_levels["energy"], 5)
        
        # Cannot buy past max
        self.assertFalse(self.progression.purchase_upgrade(self.ctx, "energy"))

    def test_apply_to_player(self):
        # Level 1 values
        self.progression.apply_to_player(self.ctx, self.ctx.player)
        self.assertEqual(self.ctx.player.max_health, 225.0)
        self.assertEqual(self.ctx.player.max_energy, 100.0)
        self.assertEqual(self.ctx.player.weapon_effectiveness, 1.0)
        self.assertEqual(self.ctx.player.max_speed, 220.0)
        
        # Set to max
        self.ctx.upgrade_levels["hull"] = 5
        self.ctx.upgrade_levels["energy"] = 5
        self.ctx.upgrade_levels["weapon"] = 5
        self.ctx.upgrade_levels["mobility"] = 5
        
        self.progression.apply_to_player(self.ctx, self.ctx.player)
        
        # Assert Level 5 values
        self.assertEqual(self.ctx.player.max_health, 325.0)
        self.assertEqual(self.ctx.player.max_energy, 160.0)
        self.assertAlmostEqual(self.ctx.player.weapon_effectiveness, 1.20)
        self.assertAlmostEqual(self.ctx.player.max_speed, 220.0 * 1.20)

    def test_save_load_progression(self):
        self.ctx.scrap = 8750
        self.ctx.upgrade_levels["hull"] = 3
        self.ctx.upgrade_levels["weapon"] = 4
        
        self.save_system.save(
            scrap=self.ctx.scrap,
            highscore=self.ctx.highscore,
            upgrades=self.ctx.upgrade_levels,
            show_crt=self.ctx.show_crt,
            difficulty_mode=self.ctx.difficulty_mode
        )
        
        loaded = self.save_system.load()
        self.assertEqual(loaded["scrap"], 8750)
        self.assertEqual(loaded["upgrades"]["hull"], 3)
        self.assertEqual(loaded["upgrades"]["weapon"], 4)
        self.assertEqual(loaded["upgrades"]["energy"], 1)

    def test_combat_system_rewards(self):
        combat = CombatSystem(self.ctx)
        enemy = MockEnemy(TARGET_TYPE_HEAVY, 10)
        self.ctx.target_group.add(enemy)
        
        b = MockBullet(20)
        self.ctx.bullet_group.add(b)
        
        self.assertEqual(self.ctx.scrap, 0)
        combat.update_combat(0.016)
        
        # Heavy rewards 75 scrap
        self.assertEqual(self.ctx.scrap, 75)

    def test_director_rewards(self):
        enc_sys = MockEncounterSystem()
        director = CombatDirector(enc_sys)
        
        self.assertEqual(self.ctx.scrap, 0)
        
        # Start and instantly finish a regular encounter
        director.start()
        # Intro state
        director.update(2.0, self.ctx)
        
        # Force encounter completion
        enc_sys.is_complete = True
        director.update(0.1, self.ctx)
        
        # 100 for encounter
        self.assertEqual(self.ctx.scrap, 100)
        
        # Set to Composition Encounter
        director.encounter_index = 6 # SCOUT_SHOOTER_HEAVY_ENCOUNTER
        director.state = "encounter"
        enc_sys.is_complete = True
        director.update(0.1, self.ctx)
        
        # +150 for composition
        self.assertEqual(self.ctx.scrap, 250)

if __name__ == '__main__':
    unittest.main()
