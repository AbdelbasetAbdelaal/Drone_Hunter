"""
===============================================================================
            DRONE HUNTER 2D - ACHIEVEMENT SYSTEM TEST SUITE
===============================================================================
"""

import os
import sys
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.core.game_context import GameContext
from src.entities.player import Player
from src.systems.achievement_system import AchievementSystem
from src.systems.save_system import SaveSystem
from src.data.mission_data import get_mission_data


class MockEnemy(pygame.sprite.Sprite):
    def __init__(self, e_type, hp, is_boss=False):
        super().__init__()
        self.enemy_type = e_type
        self.health = hp
        self.alive = True
        self.score_value = 100
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.pos = pygame.Vector2(0, 0)
        self.is_boss = is_boss
        self.contact_cooldown_timer = 0.0
        self.contact_damage = 20.0

    def take_damage(self, dmg, source=""):
        self.health -= dmg
        if self.health <= 0:
            self.alive = False
            return True
        return False


class TestAchievementSystem(unittest.TestCase):

    def setUp(self):
        self.ctx = GameContext()
        self.ctx.player = Player((640, 360))
        self.ach = AchievementSystem()

    def test_achievement_definitions(self):
        """Verify all required achievements are defined."""
        required = [
            "first_kill", "combo_10", "combo_25",
            "no_damage_mission", "speed_run", "all_sectors_cleared",
            "all_weapons_unlocked", "max_upgrades",
            "first_emp_kill", "first_overdrive_kill", "survivalist",
        ]
        for ach_id in required:
            self.assertIn(ach_id, AchievementSystem.ACHIEVEMENTS)
            self.assertIn("name", AchievementSystem.ACHIEVEMENTS[ach_id])
            self.assertIn("description", AchievementSystem.ACHIEVEMENTS[ach_id])

    def test_first_kill(self):
        """Verify first_kill unlocks after first enemy death."""
        self.ctx.total_kills = 0
        self.ach.check_all(self.ctx)
        self.assertNotIn("first_kill", self.ach.unlocked)

        self.ctx.total_kills = 1
        self.ach.check_all(self.ctx)
        self.assertIn("first_kill", self.ach.unlocked)

    def test_combo_achievements(self):
        """Verify combo achievements unlock at correct thresholds."""
        self.ctx.combo_count = 5
        self.ach.check_all(self.ctx)
        self.assertNotIn("combo_10", self.ach.unlocked)
        self.assertNotIn("combo_25", self.ach.unlocked)

        self.ctx.combo_count = 10
        self.ach.check_all(self.ctx)
        self.assertIn("combo_10", self.ach.unlocked)
        self.assertNotIn("combo_25", self.ach.unlocked)

        self.ctx.combo_count = 25
        self.ach.check_all(self.ctx)
        self.assertIn("combo_25", self.ach.unlocked)

    def test_first_emp_kill(self):
        """Verify first_emp_kill unlocks after an EMP kill."""
        self.ctx.emp_kills = 0
        self.ach.check_all(self.ctx)
        self.assertNotIn("first_emp_kill", self.ach.unlocked)

        self.ctx.emp_kills = 1
        self.ach.check_all(self.ctx)
        self.assertIn("first_emp_kill", self.ach.unlocked)

    def test_first_overdrive_kill(self):
        """Verify first_overdrive_kill unlocks during overdrive."""
        self.ctx.overdrive_kills = 0
        self.ach.check_all(self.ctx)
        self.assertNotIn("first_overdrive_kill", self.ach.unlocked)

        self.ctx.overdrive_kills = 1
        self.ach.check_all(self.ctx)
        self.assertIn("first_overdrive_kill", self.ach.unlocked)

    def test_all_sectors_cleared(self):
        """Verify all_sectors_cleared unlocks when all 5 sectors are completed."""
        self.ctx.campaign_state._completed_sectors = [1, 2, 3, 4]
        self.ach.check_all(self.ctx)
        self.assertNotIn("all_sectors_cleared", self.ach.unlocked)

        self.ctx.campaign_state._completed_sectors = [1, 2, 3, 4, 5]
        self.ach.check_all(self.ctx)
        self.assertIn("all_sectors_cleared", self.ach.unlocked)

    def test_all_weapons_unlocked(self):
        """Verify all_weapons_unlocked when all weapons are in unlocked_weapons."""
        self.ctx.unlocked_weapons = ["pulse", "scatter", "missile"]
        self.ach.check_all(self.ctx)
        self.assertNotIn("all_weapons_unlocked", self.ach.unlocked)

        all_wpn = ["pulse", "scatter", "missile", "rapid", "plasma", "rail",
                    "barrage", "beam", "tesla", "cluster", "emp"]
        self.ctx.unlocked_weapons = all_wpn[:]
        self.ach.check_all(self.ctx)
        self.assertIn("all_weapons_unlocked", self.ach.unlocked)

    def test_max_upgrades(self):
        """Verify max_upgrades unlocks when all base upgrades reach level 5."""
        self.ctx.upgrade_levels = {
            "hull": 5, "energy": 5, "weapon": 5, "mobility": 5,
            "battery": 5, "speed": 5, "fire_rate": 5, "emp_recharge": 5,
            "wingman": 5, "cloak": 5, "missiles": 5, "beam": 5,
            "tesla": 5, "cluster": 5, "overdrive": 5
        }
        self.ach.check_all(self.ctx)
        self.assertIn("max_upgrades", self.ach.unlocked)

        self.ctx.upgrade_levels["hull"] = 4
        self.ach.unlocked.discard("max_upgrades")
        self.ach.check_all(self.ctx)
        self.assertNotIn("max_upgrades", self.ach.unlocked)

    def test_no_damage_mission(self):
        """Verify no_damage_mission unlocks when mission completes with zero damage."""
        self.ctx.mission_damage_taken = 10.0
        self.ctx.mission_start_time = 1.0
        self.ctx.campaign_state.complete_mission("S1_M1")
        self.ach.check_mission_complete(self.ctx)
        self.assertNotIn("no_damage_mission", self.ach.unlocked)

        self.ctx.mission_damage_taken = 0.0
        self.ach.check_mission_complete(self.ctx)
        self.assertIn("no_damage_mission", self.ach.unlocked)

    def test_speed_run(self):
        """Verify speed_run unlocks when mission completes in under 2 minutes."""
        self.ctx.mission_start_time = 1.0
        self.ctx.mission_elapsed_time = 130.0
        self.ctx.campaign_state.complete_mission("S1_M1")
        self.ach.check_mission_complete(self.ctx)
        self.assertNotIn("speed_run", self.ach.unlocked)

        self.ctx.mission_elapsed_time = 90.0
        self.ach.check_mission_complete(self.ctx)
        self.assertIn("speed_run", self.ach.unlocked)

    def test_survivalist(self):
        """Verify survivalist unlocks after completing a survival mission."""
        md = get_mission_data("S1_M2")
        if md and md.get("objective") == "survive":
            self.ctx.campaign_state.complete_mission("S1_M2")
            self.ach.check_mission_complete(self.ctx, game=None)
            self.assertIn("survivalist", self.ach.unlocked)

    def test_unlock_callback(self):
        """Verify callbacks fire when achievements are unlocked."""
        events = []

        def on_unlock(ach_id, ach_data):
            events.append((ach_id, ach_data["name"]))

        self.ach.register_callback(on_unlock)
        self.ach.unlock("first_kill")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0], "first_kill")
        self.assertEqual(events[0][1], "First Blood")

        # Duplicate unlock should not fire callback again
        self.ach.unlock("first_kill")
        self.assertEqual(len(events), 1)

    def test_save_load_achievements(self):
        """Verify achievements persist through save/load."""
        test_path = "test_achievement_save.json"
        try:
            save_sys = SaveSystem(save_filename=test_path)
            save_sys.save(
                scrap=0, coins=0, highscore=0,
                upgrades={"hull": 1, "energy": 1, "weapon": 1, "mobility": 1},
                sectors=[True, False, False, False, False],
                achievements=["first_kill", "combo_10"]
            )
            loaded = save_sys.load()
            self.assertIn("achievements", loaded)
            self.assertEqual(loaded["achievements"], ["first_kill", "combo_10"])
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)
            tmp = test_path + ".tmp"
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_achievement_popups_in_context(self):
        """Verify achievement popups are added to GameContext."""
        popups = []

        def on_unlock(ach_id, ach_data):
            popups.append({
                "id": ach_id,
                "name": ach_data["name"],
                "description": ach_data["description"],
                "icon": ach_data.get("icon", ""),
                "timer": 4.0
            })

        self.ach.register_callback(on_unlock)
        self.ach.unlock("first_kill")
        self.assertEqual(len(popups), 1)
        self.assertEqual(popups[0]["name"], "First Blood")
        self.assertEqual(popups[0]["timer"], 4.0)


if __name__ == "__main__":
    unittest.main()
