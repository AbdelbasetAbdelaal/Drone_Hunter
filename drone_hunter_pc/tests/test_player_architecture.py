import sys
import os
import unittest
import math
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.player import Player, WingmanDrone
from src.entities.player_movement import MovementController
from src.entities.player_abilities import AbilityController
from src.entities.player_defense import PlayerDefense
from src.entities.player_weapons import WeaponController
from src.entities.wingman import WingmanManager
from src.rendering.player_renderer import PlayerRenderer
from src.data.game_data import (
    DRONE_CLASSES, WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_RAPID, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE,
    WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP
)


class TestPlayerArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((100, 100), pygame.NOFRAME)

    def test_component_composition(self):
        """Verify Player properly instantiates and composes all specialized sub-components."""
        p = Player((500, 400))
        self.assertIsInstance(p.movement, MovementController)
        self.assertIsInstance(p.abilities, AbilityController)
        self.assertIsInstance(p.defense, PlayerDefense)
        self.assertIsInstance(p.weapons, WeaponController)
        self.assertIsInstance(p.wingman_manager, WingmanManager)
        self.assertIsInstance(p.renderer, PlayerRenderer)

    def test_movement_controller_physics(self):
        """Verify movement controller handles acceleration, drag, speed clamping, and arena bounds."""
        p = Player((500, 400))
        self.assertEqual(p.pos.x, 500)
        self.assertEqual(p.pos.y, 400)

        # Apply forward movement input
        keys = {pygame.K_d: True}
        p.handle_input(keys, 0.1)
        self.assertTrue(p.is_accelerating)
        self.assertGreater(p.velocity.x, 0)

        # Update position
        p.update(0.1)
        self.assertGreater(p.pos.x, 500)
        self.assertEqual(p.rect.centerx, int(round(p.pos.x)))

        # Arena boundary clamping
        p.pos = pygame.Vector2(-100, -100)
        p.update(0.016)
        self.assertGreaterEqual(p.pos.x, 36.0)
        self.assertGreaterEqual(p.pos.y, 36.0)

    def test_ability_controller_triggers_and_cooldowns(self):
        """Verify ability controller manages EMP, roll, cloak, overdrive, and jam status."""
        p = Player((640, 360))

        # EMP Blast
        self.assertTrue(p.trigger_emp())
        self.assertFalse(p.trigger_emp())  # on cooldown
        self.assertGreater(p.emp_cooldown, 0)
        p.emp_cooldown = 0
        self.assertTrue(p.trigger_emp())

        # Barrel Roll
        self.assertTrue(p.trigger_roll(1.0))
        self.assertTrue(p.is_rolling)
        self.assertTrue(p.is_invulnerable)

        # Update roll timer to completion
        p.update(0.5)
        self.assertFalse(p.is_rolling)

        # Tactical Cloak
        self.assertTrue(p.trigger_cloak())
        self.assertTrue(p.is_cloaked)
        p.update(5.0)
        self.assertFalse(p.is_cloaked)

        # Overdrive Ultimate
        self.assertTrue(p.trigger_overdrive())
        self.assertGreater(p.overdrive_timer, 0)
        self.assertEqual(p.shield_hits, 3)

        # EMP Jammed Mechanic
        p.overdrive_timer = 0.0
        p.trigger_emp_jammed(3.0)
        self.assertTrue(p.is_jammed)
        self.assertFalse(p.can_shoot())
        self.assertFalse(p.trigger_emp())

    def test_defense_shield_and_damage_resolution(self):
        """Verify defense component handles shield hits, armor mitigation, grace period, and destruction."""
        p = Player((640, 360))
        p.max_health = 100.0
        p.health = 100.0
        p.armor = 5
        p.activate_shield(2)

        # 1. Shield absorbs full hit without health loss
        destroyed = p.take_damage(50.0)
        self.assertFalse(destroyed)
        self.assertEqual(p.shield_hits, 1)
        self.assertEqual(p.health, 100.0)

        # 2. Second hit consumes shield
        p.take_damage(50.0)
        self.assertEqual(p.shield_hits, 0)
        self.assertEqual(p.health, 100.0)

        # 3. Direct hull hit reduced by armor (30 - 5 = 25 dmg)
        p.damage_grace_timer = 0.0  # bypass grace for test
        p.take_damage(30.0)
        self.assertEqual(p.health, 75.0)

        # 4. Lethal damage triggers destruction state
        p.damage_grace_timer = 0.0
        destroyed = p.take_damage(100.0)
        self.assertTrue(destroyed)
        self.assertFalse(p.alive)
        self.assertTrue(p.is_destroyed)

    def test_weapon_controller_cycling_and_firing(self):
        """Verify weapon controller handles weapon switching, cooldowns, and firing."""
        p = Player((640, 360))
        p.set_drone_class("striker")

        self.assertIn("pulse", p.available_weapons)
        self.assertEqual(p.active_weapon, "pulse")

        # Cycle weapon
        p.cycle_weapon(1)
        self.assertEqual(p.active_weapon, p.available_weapons[1])

        # Direct weapon selection
        p.select_weapon(0)
        self.assertEqual(p.active_weapon, p.available_weapons[0])

        # Direct weapon setter
        p.set_weapon("scatter")
        self.assertEqual(p.active_weapon, "scatter")

        # Firing weapon
        self.assertTrue(p.can_shoot())
        bullets = p.shoot((800, 360))
        self.assertGreater(len(bullets), 0)
        self.assertFalse(p.can_shoot())  # on cooldown

    def test_all_five_drone_classes_configure_correctly(self):
        """Verify all 5 drone classes configure stats, weapons, and sprites accurately."""
        p = Player((640, 360))
        classes = ["striker", "interceptor", "assault", "arc", "command"]

        for c_id in classes:
            p.set_drone_class(c_id)
            self.assertEqual(p.drone_class_id, c_id)
            self.assertEqual(p.drone_class, c_id)
            self.assertGreater(p.max_health, 0)
            self.assertGreater(p.max_speed, 0)
            self.assertGreater(len(p.available_weapons), 0)
            self.assertIn(p.active_weapon, p.available_weapons)

    def test_wingman_manager(self):
        """Verify wingman escort drones spawn up to maximum 2 and update."""
        p = Player((640, 360))
        self.assertEqual(len(p.wingmen), 0)

        p.spawn_wingman()
        self.assertEqual(len(p.wingmen), 1)

        p.spawn_wingman()
        self.assertEqual(len(p.wingmen), 2)

        # Cap at 2
        p.spawn_wingman()
        self.assertEqual(len(p.wingmen), 2)

        # Update wingmen
        bullets = p.update_wingmen(0.1)
        self.assertIsInstance(bullets, list)

    def test_renderer_delegation(self):
        """Verify PlayerRenderer draws player without exceptions."""
        p = Player((640, 360))
        canvas = pygame.Surface((1280, 720), pygame.SRCALPHA)
        p.draw(canvas, (0, 0))
        p.draw_wingmen(canvas, (0, 0))


if __name__ == "__main__":
    unittest.main()
