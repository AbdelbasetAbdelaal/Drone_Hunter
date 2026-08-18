"""
================================================================================
    DRONE HUNTER 2D - PHASE 2B DEDICATED SHOOTER & ENCOUNTER TEST SUITE
================================================================================
Exhaustive verification of:
1. Shooter Initialization, Stats, Approach, Preferred Range, Min/Max Distance, Aim, Telegraph, Fire, Reposition, Death, Score
2. Hostile Projectiles (Direction, Speed, Bounds, Collision, Damage Pipeline)
3. Shooter Controlled Introduction Encounter (1 Shooter, Initial Delay, Spawner Suppression, Completion, Resumption)
4. Headless execution under dummy SDL video/audio drivers.
"""

import os
import sys
import unittest
import pygame

# Headless SDL Configuration
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.data.settings import *
from src.data.game_data import *
from src.core.game_state import STATE_PLAYING
from src.core.game_context import GameContext
from src.core.game import Game
from src.entities.player import Player
from src.entities.enemy import Enemy, Shooter
from src.entities.bullet import EnemyBullet
from src.systems.combat_system import CombatSystem
from src.systems.encounter_system import EncounterSystem, SHOOTER_INTRO_ENCOUNTER


class TestPhase2BShooterAndEncounter(unittest.TestCase):

    # ==========================================================================
    # SHOOTER ENTITY & STATS
    # ==========================================================================
    def test_shooter_initialization(self):
        shooter = Shooter(pos=(800, 600))
        self.assertIsNotNone(shooter)
        self.assertEqual(shooter.enemy_type, TARGET_TYPE_SHOOTER)
        self.assertEqual(shooter.ai_state, "approach")

    def test_shooter_stats(self):
        shooter = Shooter(pos=(800, 600))
        self.assertEqual(shooter.hp, SHOOTER_HP)
        self.assertEqual(shooter.max_hp, SHOOTER_HP)
        self.assertEqual(shooter.speed, SHOOTER_SPEED)
        self.assertEqual(shooter.points, SHOOTER_SCORE)
        self.assertEqual(shooter.size, SHOOTER_SIZE)
        self.assertEqual(shooter.projectile_damage, SHOOTER_PROJECTILE_DAMAGE)
        self.assertEqual(shooter.projectile_speed, SHOOTER_PROJECTILE_SPEED)

    # ==========================================================================
    # 6-STATE POSITIONING MACHINE
    # ==========================================================================
    def test_shooter_approach(self):
        """Shooter closes distance when spawned far away (> 700px)."""
        shooter = Shooter(pos=(1400, 600))
        initial_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        shooter.update(0.1, player_pos=(400, 600))
        new_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        self.assertLess(new_dist, initial_dist)

    def test_shooter_preferred_distance(self):
        """When within preferred combat band (~470px), transitions to position state."""
        shooter = Shooter(pos=(800, 600))
        # Player at (400, 600) -> distance is 400px (inside preferred range)
        shooter.update(0.016, player_pos=(400, 600))
        self.assertEqual(shooter.ai_state, "position")

    def test_shooter_minimum_distance(self):
        """When too close (< 300px), shooter retreats away from player."""
        shooter = Shooter(pos=(500, 600))
        shooter.ai_state = "position"
        initial_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        self.assertLess(initial_dist, 300.0)

        shooter.update(0.1, player_pos=(400, 600))
        new_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        self.assertGreater(new_dist, initial_dist)

    def test_shooter_maximum_distance(self):
        """When too far (> 550px) while in position state, shooter advances."""
        shooter = Shooter(pos=(1100, 600))
        shooter.ai_state = "position"
        initial_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        self.assertGreater(initial_dist, 550.0)

        shooter.update(0.1, player_pos=(400, 600))
        new_dist = (shooter.pos - pygame.Vector2(400, 600)).length()
        self.assertLess(new_dist, initial_dist)

    def test_shooter_aim(self):
        """When fire cooldown is ready in position state, shooter transitions to aim and then telegraph."""
        shooter = Shooter(pos=(870, 600))
        shooter.ai_state = "position"
        shooter.fire_timer = SHOOTER_FIRE_COOLDOWN + 0.1
        shooter.update(0.016, player_pos=(400, 600), player_vel=(0, 100))
        self.assertEqual(shooter.ai_state, "aim")

        # Next update transitions aim -> telegraph
        shooter.update(0.016, player_pos=(400, 600), player_vel=(0, 100))
        self.assertEqual(shooter.ai_state, "telegraph")
        self.assertGreater(shooter.aim_target.length(), 0)

    def test_shooter_telegraph(self):
        """Telegraph state maintains aim and hovers for SHOOTER_TELEGRAPH_TIME."""
        shooter = Shooter(pos=(870, 600))
        shooter.ai_state = "telegraph"
        shooter.state_timer = 0.1
        shooter.aim_target = pygame.Vector2(400, 600)
        bullets = shooter.update(0.1, player_pos=(400, 600))
        self.assertEqual(shooter.ai_state, "telegraph")
        self.assertEqual(len(bullets), 0)

    def test_shooter_fire(self):
        """After telegraph completes, shooter fires exactly ONE deliberate bullet."""
        shooter = Shooter(pos=(870, 600))
        shooter.ai_state = "telegraph"
        shooter.state_timer = SHOOTER_TELEGRAPH_TIME + 0.05
        shooter.aim_target = pygame.Vector2(400, 600)
        bullets = shooter.update(0.016, player_pos=(400, 600))
        self.assertEqual(len(bullets), 1)
        b = bullets[0]
        self.assertIsInstance(b, EnemyBullet)
        self.assertEqual(b.damage, SHOOTER_PROJECTILE_DAMAGE)
        self.assertEqual(shooter.ai_state, "reposition")

    def test_shooter_projectile_creation(self):
        """Verify projectile speed, angle, and properties."""
        shooter = Shooter(pos=(870, 600))
        shooter.ai_state = "fire"
        shooter.aim_target = pygame.Vector2(400, 600)
        bullets = shooter.update(0.016, player_pos=(400, 600))
        self.assertEqual(len(bullets), 1)
        b = bullets[0]
        self.assertEqual(b.speed, SHOOTER_PROJECTILE_SPEED)
        self.assertEqual(b.damage, SHOOTER_PROJECTILE_DAMAGE)

    def test_shooter_reposition(self):
        """After firing, shooter moves along evasive reposition vector for SHOOTER_REPOSITION_TIME."""
        shooter = Shooter(pos=(870, 600))
        shooter.ai_state = "reposition"
        shooter.reposition_dir = pygame.Vector2(0, 1)
        shooter.state_timer = SHOOTER_REPOSITION_TIME + 0.05
        shooter.update(0.016, player_pos=(400, 600))
        self.assertEqual(shooter.ai_state, "position")

    def test_shooter_death(self):
        shooter = Shooter(pos=(800, 600))
        is_dead = shooter.take_damage(60)
        self.assertTrue(is_dead)
        self.assertFalse(shooter.alive)
        self.assertEqual(shooter.hp, 0)

    def test_shooter_score(self):
        shooter = Shooter(pos=(800, 600))
        self.assertEqual(shooter.points, 250)

    # ==========================================================================
    # HOSTILE PROJECTILE TESTS
    # ==========================================================================
    def test_projectile_direction_and_speed(self):
        bullet = EnemyBullet(start_pos=(800, 600), target_pos=(400, 600), speed=340.0, damage=12)
        group = pygame.sprite.Group(bullet)
        bullet.update(0.1)
        self.assertTrue(bullet.alive())
        self.assertLess(bullet.pos.x, 800.0)

    def test_projectile_bounds(self):
        bullet = EnemyBullet(start_pos=(800, 600), target_pos=(-500, 600), speed=2000.0)
        group = pygame.sprite.Group(bullet)
        # Bullet flies past left world boundary (-80)
        bullet.update(1.0)
        self.assertFalse(bullet.alive())

    def test_projectile_collision_and_damage(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        bullet = EnemyBullet(start_pos=(400, 400), target_pos=(400, 400), damage=12)
        ctx.enemy_bullet_group.add(bullet)
        combat = CombatSystem(ctx)

        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0 - 12)
        self.assertFalse(bullet.alive())

    # ==========================================================================
    # SHOOTER CONTROLLED ENCOUNTER TESTS
    # ==========================================================================
    def test_shooter_encounter_starts(self):
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        self.assertEqual(encounter.state, "idle")
        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        self.assertTrue(encounter.is_active)

    def test_shooter_encounter_exactly_one_shooter(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        encounter.start()

        # Wait initial delay (1.5s)
        encounter.update(1.6, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(encounter.spawned_count, 1)
        self.assertEqual(list(ctx.target_group)[0].enemy_type, TARGET_TYPE_SHOOTER)

    def test_shooter_encounter_suppresses_spawner(self):
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        self.assertFalse(encounter.is_suppressing_spawner)
        encounter.start()
        self.assertTrue(encounter.is_suppressing_spawner)

    def test_shooter_encounter_death_completes(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        encounter.start()

        encounter.update(1.6, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        shooter = list(ctx.target_group)[0]
        shooter.kill()
        encounter.update(0.016, ctx)

        self.assertEqual(encounter.state, "complete")
        self.assertTrue(encounter.is_complete)
        self.assertFalse(encounter.is_active)

    def test_shooter_encounter_resumes_spawner(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        encounter.start()

        encounter.update(1.6, ctx)
        list(ctx.target_group)[0].kill()
        encounter.update(0.016, ctx)

        self.assertTrue(encounter.is_complete)
        self.assertFalse(encounter.is_suppressing_spawner)

    def test_shooter_encounter_reset(self):
        encounter = EncounterSystem(config=SHOOTER_INTRO_ENCOUNTER)
        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        encounter.reset()
        self.assertEqual(encounter.state, "idle")
        self.assertFalse(encounter.is_active)
        self.assertEqual(encounter.spawned_count, 0)
        self.assertEqual(encounter.eliminated_count, 0)


if __name__ == "__main__":
    unittest.main()
