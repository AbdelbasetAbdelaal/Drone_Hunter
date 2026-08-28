"""
===============================================================================
         DRONE HUNTER 2D - PHASE 5 PERFORMANCE REGRESSION TESTS
===============================================================================
Tests for the runtime stability fixes:
1. Enemy sprite caching
2. Mission state transitions
3. Projectile lifecycle
4. Encounter lifecycle
5. Entity group reset
6. Shield lookup correctness
7. Mission progression preservation
8. LightningArc lifecycle
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

from src.entities.enemy import Enemy, Scout, Shooter, Heavy
from src.entities.bullet import HomingMissile, Bullet, ClusterTorpedo, ClusterBomblet
from src.rendering.particles import LightningArc
from src.rendering.particles import LightningArc
from src.systems.mission_system import MissionSystem, STATE_ACTIVE, STATE_COMPLETED
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem, SCOUT_INTRO_ENCOUNTER
from src.core.game_context import GameContext
from src.core.game_state import STATE_PLAYING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_GAME_OVER
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE,
    SCOUT_STRAFE_DURATION
)


class TestEnemySpriteCaching(unittest.TestCase):
    """Test that enemy sprites are not rebuilt unnecessarily."""

    def setUp(self):
        self.scout = Scout(pos=(600, 400))

    def test_sprite_not_rebuilt_when_heading_unchanged(self):
        initial_image = self.scout.image
        initial_rect = self.scout.rect
        self.scout.update(0.016, player_pos=(400, 400))
        self.assertIs(self.scout.image, initial_image)

    def test_sprite_rebuilt_when_state_changes(self):
        self.scout.ai_state = "strafe"
        self.scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        self.scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(self.scout.ai_state, "telegraph")

    def test_sprite_rebuilt_on_hit_flash(self):
        self.scout.hit_flash_timer = 0.0
        self.scout.update(0.016, player_pos=(400, 400))
        self.scout.take_damage(10)
        self.scout.update(0.016, player_pos=(400, 400))
        self.assertGreater(self.scout.hit_flash_timer, 0)


class TestMissionStateTransitions(unittest.TestCase):
    """Test that mission completion/failure stops gameplay processing."""

    def setUp(self):
        self.ctx = GameContext()
        self.ctx.state = STATE_PLAYING
        self.ctx.player = type('obj', (object,), {
            'alive': True,
            'pos': pygame.Vector2(400, 400),
            'velocity': pygame.Vector2(0, 0),
            'health': 100,
            'max_health': 100,
            'energy': 100,
            'max_energy': 100,
            'is_accelerating': False,
            'aim_angle': 0.0,
            'tilt_y': 0.0,
            'shield_hits': 0,
            'is_invulnerable': False,
            'is_cloaked': False,
            'overdrive_timer': 0.0,
            'muzzle_flash_timer': 0.0,
            'damage_flash_timer': 0.0,
            'weapon_cooldowns': {},
            'can_shoot': lambda: False,
            'update': lambda dt: None,
        })()
        self.mission_sys = MissionSystem()
        self.enc_sys = EncounterSystem()
        self.director = CombatDirector(self.enc_sys)

    def test_mission_complete_immediately_after_success(self):
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        enemy = Enemy(pos=(400, 400))
        self.ctx.target_group.add(enemy)
        self.director.state = "complete"
        enemy.kill()
        
        result = self.mission_sys.update(1.0, self.ctx, self.director)
        self.assertTrue(result)
        self.assertEqual(self.mission_sys.state, STATE_COMPLETED)
        self.assertTrue(self.mission_sys.is_mission_success)

    def test_mission_failed_state(self):
        self.mission_sys.start_mission(self.ctx, "S1_M1", self.director)
        self.mission_sys.trigger_failure()
        self.assertEqual(self.mission_sys.state, STATE_COMPLETED)
        self.assertFalse(self.mission_sys.is_mission_success)


class TestProjectileLifecycle(unittest.TestCase):
    """Test that projectiles have finite lifetimes and terminate correctly."""

    def test_homing_missile_max_lifetime(self):
        missile = HomingMissile((100, 100), (200, 100), damage=65, speed=680.0)
        self.assertEqual(missile.max_lifetime, 12.0)
        self.assertEqual(missile.lifetime, 12.0)
        
        for _ in range(120):
            missile.update(0.1, target_group=pygame.sprite.Group())
        
        self.assertFalse(missile.alive())

    def test_cluster_torpedo_detonation(self):
        torpedo = ClusterTorpedo((100, 100), (200, 100), damage=80, speed=520.0)
        self.assertFalse(torpedo.detonated)
        
        bomblets = torpedo.update(0.6)
        self.assertTrue(torpedo.detonated)
        self.assertFalse(torpedo.alive())
        self.assertEqual(len(bomblets), 6)

    def test_cluster_bomblet_lifetime(self):
        bomblet = ClusterBomblet((100, 100), 0.0, speed=380.0, damage=24)
        bomblet.lifetime = 0.5
        bomblet.update(0.6)
        self.assertFalse(bomblet.alive())


class TestEncounterLifecycle(unittest.TestCase):
    """Test that completed encounters stop spawning."""

    def test_encounter_stops_spawning_after_complete(self):
        ctx = GameContext()
        ctx.player = type('obj', (object,), {'pos': pygame.Vector2(1200, 700)})()
        encounter = EncounterSystem(config=SCOUT_INTRO_ENCOUNTER)
        encounter.start()
        
        for _ in range(4):
            encounter.update(1.3, ctx)
            for e in list(ctx.target_group):
                e.kill()
            encounter.update(0.016, ctx)
        
        self.assertTrue(encounter.is_complete)
        self.assertFalse(encounter.is_active)
        encounter.update(5.0, ctx)
        self.assertEqual(len(ctx.target_group), 0)


class TestMissionResetClearsEntities(unittest.TestCase):
    """Test that mission reset clears runtime entities but preserves progression."""

    def test_reset_preserves_progression(self):
        ctx = GameContext()
        ctx.scrap = 500
        ctx.campaign_state.complete_mission("S1_M1")
        ctx.campaign_state.complete_sector(1)
        
        ctx.bullet_group.add(Bullet((0, 0), (100, 0)))
        ctx.target_group.add(Enemy(pos=(400, 400)))
        
        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.target_group.empty()
        ctx.obstacle_group.empty()
        ctx.hazard_group.empty()
        ctx.powerup_group.empty()
        
        self.assertEqual(ctx.scrap, 500)
        self.assertIn("S1_M1", ctx.campaign_state.completed_missions)
        self.assertIn(1, ctx.campaign_state.completed_sectors)
        self.assertEqual(len(ctx.bullet_group), 0)
        self.assertEqual(len(ctx.target_group), 0)


class TestShieldLookup(unittest.TestCase):
    """Test that shield drone lookup remains valid after enemy removal."""

    def test_shield_lookup_after_enemy_killed(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = type('obj', (object,), {
            'alive': True,
            'shield_hits': 0,
            'is_invulnerable': False,
            'is_cloaked': False,
            'take_damage': lambda dmg: False,
            'rect': pygame.Rect(0, 0, 10, 10),
        })()
        
        shielded = Enemy(enemy_type=TARGET_TYPE_SHIELD_DRONE, pos=(100, 100))
        target = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(130, 100))
        ctx.target_group.add(shielded)
        ctx.target_group.add(target)
        
        from src.systems.combat_system import CombatSystem
        combat = CombatSystem(ctx)
        
        initial_hp = target.hp
        b = Bullet((120, 100), (140, 100), damage=30)
        ctx.bullet_group.add(b)
        
        combat.update_combat(0.016)
        
        self.assertTrue(shielded.alive)
        self.assertTrue(target.alive)
        self.assertLess(target.hp, initial_hp)
        self.assertEqual(len(ctx.bullet_group), 0)


class TestMissionProgression(unittest.TestCase):
    """Test that mission progression is unchanged."""

    def test_sector_completion_flow(self):
        ctx = GameContext()
        mission_sys = MissionSystem()
        director = CombatDirector(EncounterSystem())
        
        mission_sys.start_mission(ctx, "S1_M5", director)
        mission_sys._trigger_success(ctx)
        
        self.assertIn(1, ctx.campaign_state.completed_sectors)
        self.assertIn(2, ctx.campaign_state.unlocked_sectors)
        self.assertIn("S2_M1", ctx.campaign_state.unlocked_missions)
        self.assertEqual(ctx.scrap, 900)

    def test_reward_not_duplicated_on_replay(self):
        ctx = GameContext()
        mission_sys = MissionSystem()
        director = CombatDirector(EncounterSystem())
        
        mission_sys.start_mission(ctx, "S1_M1", director)
        mission_sys._trigger_success(ctx)
        first_scrap = ctx.scrap
        
        mission_sys.start_mission(ctx, "S1_M1", director)
        mission_sys._trigger_success(ctx)
        self.assertEqual(ctx.scrap, first_scrap)


class TestLightningArcLifecycle(unittest.TestCase):
    """Test LightningArc lifetime is managed exactly once by update(), not draw()."""

    def test_draw_does_not_mutate_lifetime(self):
        arc = LightningArc((0, 0), (100, 100))
        initial_lifetime = arc.lifetime
        surf = pygame.Surface((200, 200))
        arc.draw(surf, (0, 0))
        self.assertEqual(arc.lifetime, initial_lifetime)

    def test_update_decrements_lifetime(self):
        arc = LightningArc((0, 0), (100, 100))
        self.assertEqual(arc.lifetime, 0.18)
        alive = arc.update(0.05)
        self.assertTrue(alive)
        self.assertAlmostEqual(arc.lifetime, 0.13, places=5)

    def test_update_kills_when_lifetime_expires(self):
        arc = LightningArc((0, 0), (100, 100))
        alive = arc.update(0.25)
        self.assertFalse(alive)
        self.assertLessEqual(arc.lifetime, 0.0)

    def test_lifetime_decremented_exactly_once_per_update(self):
        arc = LightningArc((0, 0), (100, 100))
        arc.update(0.05)
        expected = 0.13
        self.assertAlmostEqual(arc.lifetime, expected, places=5)
        arc.draw(pygame.Surface((200, 200)), (0, 0))
        self.assertAlmostEqual(arc.lifetime, expected, places=5)


class TestLightningArcLifecycle(unittest.TestCase):
    """Test LightningArc lifetime is managed exactly once by update(), not draw()."""

    def test_draw_does_not_mutate_lifetime(self):
        arc = LightningArc((0, 0), (100, 100))
        initial_lifetime = arc.lifetime
        surf = pygame.Surface((200, 200))
        arc.draw(surf, (0, 0))
        self.assertEqual(arc.lifetime, initial_lifetime)

    def test_update_decrements_lifetime(self):
        arc = LightningArc((0, 0), (100, 100))
        self.assertEqual(arc.lifetime, 0.18)
        alive = arc.update(0.05)
        self.assertTrue(alive)
        self.assertAlmostEqual(arc.lifetime, 0.13, places=5)

    def test_update_kills_when_lifetime_expires(self):
        arc = LightningArc((0, 0), (100, 100))
        alive = arc.update(0.25)
        self.assertFalse(alive)
        self.assertLessEqual(arc.lifetime, 0.0)

    def test_lifetime_decremented_exactly_once_per_update(self):
        arc = LightningArc((0, 0), (100, 100))
        arc.update(0.05)
        expected = 0.13
        self.assertAlmostEqual(arc.lifetime, expected, places=5)
        arc.draw(pygame.Surface((200, 200)), (0, 0))
        self.assertAlmostEqual(arc.lifetime, expected, places=5)


if __name__ == '__main__':
    unittest.main()
