import sys
import os
import unittest
import math
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.enemy import Enemy, Scout, Shooter, Heavy
from src.entities.ai import (
    BaseEnemyAI, EnemyAIContext, create_enemy_ai,
    ScoutAI, ShooterAI, HeavyAI, SniperAI, TurretAI,
    SwarmAI, ChaserAI, FastAI, ShieldDroneAI, StandardAI
)
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_SNIPER, TARGET_TYPE_TURRET, TARGET_TYPE_SWARM,
    TARGET_TYPE_CHASER, TARGET_TYPE_FAST, TARGET_TYPE_SHIELD_DRONE,
    TARGET_TYPE_STANDARD, SCOUT_STRAFE_DURATION, SCOUT_TELEGRAPH_TIME,
    SCOUT_DIVE_DURATION, SCOUT_RECOVER_TIME, SHOOTER_FIRE_COOLDOWN,
    SHOOTER_TELEGRAPH_TIME, SHOOTER_REPOSITION_TIME
)
from src.entities.bullet import EnemyBullet, EnemySniperBeam


class TestEnemyAIArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((100, 100), pygame.NOFRAME)

    def test_factory_and_component_composition(self):
        """Verify each enemy archetype initializes with its dedicated AI controller."""
        scout = Enemy(TARGET_TYPE_SCOUT, (500, 300))
        self.assertIsInstance(scout.ai, ScoutAI)

        shooter = Enemy(TARGET_TYPE_SHOOTER, (500, 300))
        self.assertIsInstance(shooter.ai, ShooterAI)

        heavy = Enemy(TARGET_TYPE_HEAVY, (500, 300))
        self.assertIsInstance(heavy.ai, HeavyAI)

        sniper = Enemy(TARGET_TYPE_SNIPER, (500, 300))
        self.assertIsInstance(sniper.ai, SniperAI)

        turret = Enemy(TARGET_TYPE_TURRET, (500, 300))
        self.assertIsInstance(turret.ai, TurretAI)

        shield = Enemy(TARGET_TYPE_SHIELD_DRONE, (500, 300))
        self.assertIsInstance(shield.ai, ShieldDroneAI)

        swarm = Enemy(TARGET_TYPE_SWARM, (500, 300))
        self.assertIsInstance(swarm.ai, SwarmAI)

        chaser = Enemy(TARGET_TYPE_CHASER, (500, 300))
        self.assertIsInstance(chaser.ai, ChaserAI)

        fast = Enemy(TARGET_TYPE_FAST, (500, 300))
        self.assertIsInstance(fast.ai, FastAI)

        standard = Enemy(TARGET_TYPE_STANDARD, (500, 300))
        self.assertIsInstance(standard.ai, StandardAI)

    def test_scout_ai_state_machine_cycle(self):
        """Verify Scout AI progresses through approach -> strafe -> telegraph -> dive -> recover."""
        scout = Scout(pos=(1000, 360))
        self.assertEqual(scout.ai_state, "approach")

        # 1. Approach to Strafe
        scout.update(0.1, player_pos=(200, 360))
        scout.ai.state_timer = 2.5  # force approach completion
        scout.update(0.016, player_pos=(200, 360))
        self.assertEqual(scout.ai_state, "strafe")

        # 2. Strafe to Telegraph
        scout.ai.state_timer = SCOUT_STRAFE_DURATION + 0.1
        scout.update(0.016, player_pos=(200, 360), player_vel=(0, 0))
        self.assertEqual(scout.ai_state, "telegraph")

        # 3. Telegraph to Dive
        scout.ai.state_timer = SCOUT_TELEGRAPH_TIME + 0.1
        scout.update(0.016, player_pos=(200, 360))
        self.assertEqual(scout.ai_state, "dive")

        # 4. Dive to Recover
        scout.ai.state_timer = SCOUT_DIVE_DURATION + 0.1
        scout.update(0.016, player_pos=(200, 360))
        self.assertEqual(scout.ai_state, "recover")

        # 5. Recover back to Strafe
        scout.ai.state_timer = SCOUT_RECOVER_TIME + 0.1
        scout.update(0.016, player_pos=(200, 360))
        self.assertEqual(scout.ai_state, "strafe")

    def test_shooter_ai_state_machine_and_firing(self):
        """Verify Shooter AI positions, aims, telegraphs, fires projectile, and repositions."""
        shooter = Shooter(pos=(1000, 360))
        self.assertEqual(shooter.ai_state, "approach")

        # 1. Approach to Position
        shooter.update(0.1, player_pos=(600, 360))  # within 450px
        self.assertEqual(shooter.ai_state, "position")

        # 2. Position to Aim (when fire_timer elapses)
        shooter.ai.fire_timer = SHOOTER_FIRE_COOLDOWN + 0.1
        shooter.update(0.016, player_pos=(600, 360))
        self.assertEqual(shooter.ai_state, "aim")

        # 3. Aim to Telegraph
        shooter.update(0.016, player_pos=(600, 360))
        self.assertEqual(shooter.ai_state, "telegraph")

        # 4. Telegraph to Reposition and spawn projectile
        shooter.ai.state_timer = SHOOTER_TELEGRAPH_TIME + 0.1
        bullets = shooter.update(0.016, player_pos=(600, 360))
        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], EnemyBullet)
        self.assertEqual(shooter.ai_state, "reposition")

        # 5. Reposition back to Position
        shooter.ai.state_timer = SHOOTER_REPOSITION_TIME + 0.1
        shooter.update(0.016, player_pos=(600, 360))
        self.assertEqual(shooter.ai_state, "position")

    def test_heavy_ai_state_machine_cycle(self):
        """Verify Heavy AI progresses from approach -> pressure -> recover -> approach."""
        heavy = Heavy(pos=(500, 360))
        self.assertEqual(heavy.ai_state, "approach")

        # 1. Approach to Pressure (within 320px)
        heavy.update(0.1, player_pos=(250, 360))  # 250px distance
        self.assertEqual(heavy.ai_state, "pressure")

        # 2. Pressure to Recover (sustained pressure timer >= 2.5s)
        heavy.ai.state_timer = 2.6
        heavy.update(0.016, player_pos=(250, 360))
        self.assertEqual(heavy.ai_state, "recover")

        # 3. Recover to Approach
        heavy.ai.state_timer = 0.9
        heavy.update(0.016, player_pos=(250, 360))
        self.assertEqual(heavy.ai_state, "approach")

    def test_sniper_ai_targeting_and_beam_firing(self):
        """Verify Sniper AI aims with red laser telegraph and spawns EnemySniperBeam."""
        sniper = Enemy(TARGET_TYPE_SNIPER, (900, 360))
        sniper.ai.sniper_aim_timer = 0.5  # <= 0.8 triggers aiming telegraph
        sniper.update(0.1, player_pos=(200, 360))
        self.assertTrue(sniper.is_aiming)

        # Fire beam when aim timer expires
        sniper.ai.sniper_aim_timer = 0.0
        bullets = sniper.update(0.016, player_pos=(200, 360))
        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], EnemySniperBeam)
        self.assertFalse(sniper.is_aiming)

    def test_turret_ai_three_way_salvo(self):
        """Verify Turret AI fires 3-way spread bullet burst when shoot timer elapses."""
        turret = Enemy(TARGET_TYPE_TURRET, (800, 360))
        turret.ai.shoot_timer = 0.0
        bullets = turret.update(0.016, player_pos=(200, 360))
        self.assertEqual(len(bullets), 3)
        for b in bullets:
            self.assertIsInstance(b, EnemyBullet)

    def test_shield_drone_rotation(self):
        """Verify Shield Drone rotates its barrier angle."""
        shield = Enemy(TARGET_TYPE_SHIELD_DRONE, (800, 360))
        initial_angle = shield.shield_angle
        shield.update(0.1, player_pos=(200, 360))
        self.assertGreater(shield.shield_angle, initial_angle)

    def test_emp_jammed_behavior(self):
        """Verify EMP jammed state pauses AI advancement while decrementing timer."""
        scout = Scout(pos=(800, 360))
        scout.emp_jammed_timer = 2.0
        initial_pos = pygame.Vector2(scout.pos)

        bullets = scout.update(0.1, player_pos=(200, 360))
        self.assertEqual(len(bullets), 0)
        self.assertAlmostEqual(scout.emp_jammed_timer, 1.9, places=2)
        # Position did not advance due to jam
        self.assertEqual(scout.pos.x, initial_pos.x)

    def test_armor_damage_reduction_and_death(self):
        """Verify armor mitigates incoming damage and entity dies at 0 HP."""
        heavy = Heavy(pos=(500, 360))
        heavy.max_hp = 100
        heavy.hp = 100
        heavy.armor = 0.20  # 20% armor mitigation

        died = heavy.take_damage(50)
        self.assertFalse(died)
        # 50 * (1 - 0.20) = 40 damage taken
        self.assertEqual(heavy.hp, 60)

        # Fatal damage
        died = heavy.take_damage(100)
        self.assertTrue(died)
        self.assertFalse(heavy.alive)
        self.assertEqual(heavy.hp, 0)


if __name__ == "__main__":
    unittest.main()
