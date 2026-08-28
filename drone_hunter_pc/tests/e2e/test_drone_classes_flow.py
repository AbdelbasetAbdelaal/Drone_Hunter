import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.data.game_data import (
    DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR, DRONE_CLASS_ASSAULT,
    DRONE_CLASS_ARC, DRONE_CLASS_COMMAND, get_drone_loadout
)


class TestDroneClassesFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game(test_mode=True)
        self.ctx = self.game.context

    def test_all_five_drone_platforms_lifecycle(self):
        """Verify each of the 5 drone classes selects, spawns, renders, and shoots properly."""
        drone_classes = [
            DRONE_CLASS_STRIKER,
            DRONE_CLASS_INTERCEPTOR,
            DRONE_CLASS_ASSAULT,
            DRONE_CLASS_ARC,
            DRONE_CLASS_COMMAND,
        ]

        for d_class in drone_classes:
            # 1. Select drone
            self.ctx.selected_drone = d_class
            self.assertEqual(self.ctx.selected_drone, d_class)

            # 2. Launch Mission
            self.game.start_phase5_mission("S1_M1")
            player = self.ctx.player
            self.assertIsNotNone(player)
            self.assertTrue(player.alive)

            # 3. Check Loadout matches deterministic specification
            expected_loadout = get_drone_loadout(d_class)
            expected_weapons = list(expected_loadout.values()) if isinstance(expected_loadout, dict) else list(expected_loadout)
            self.assertEqual(player.available_weapons, expected_weapons)

            # 4. Fire weapon
            bullets = player.shoot((800.0, 360.0), level=1, targets_group=self.ctx.target_group)
            self.assertGreater(len(bullets), 0)

            # 5. Render frame
            self.game.update(0.016)
            self.game.render()

            # 6. Death sequence
            player.take_damage(9999)
            self.assertFalse(player.alive)


if __name__ == "__main__":
    unittest.main()
