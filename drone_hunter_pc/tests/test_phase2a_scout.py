"""
================================================================================
    DRONE HUNTER 2D - PHASE 2A DEDICATED SCOUT & ENCOUNTER TEST SUITE
================================================================================
Exhaustive verification of:
1. Scout Initialization, Stats, Approach, Strafe, Telegraph, Dive, Recover, Damage, Death, Contact Cooldown
2. Encounter System Lifecycle:
   - reset returns IDLE
   - reset does NOT start encounter
   - explicit start works
   - initial delay works
   - 3 sequential Scouts with wait intervals
   - COMPLETE state after Scout #3
3. Game Integration & Sector Selection:
   - Sector 0 Stage 1 does NOT start Scout encounter (stays IDLE)
   - Sector 1 Stage 1 explicitly starts Scout encounter (starts WAITING)
   - Encounter suppresses normal Spawner during intro
   - Normal Spawner resumes after encounter completes
4. 360-degree projectile flight in 2D world space
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
from src.core.game_state import STATE_PLAYING, STATE_LEVEL_CLEAR, STATE_GAME_OVER
from src.core.game_context import GameContext
from src.core.game import Game
from src.entities.player import Player
from src.entities.enemy import Enemy, Scout
from src.entities.bullet import Bullet
from src.systems.combat_system import CombatSystem
from src.systems.encounter_system import EncounterSystem, SCOUT_INTRO_ENCOUNTER
from src.systems.spawn_system import Spawner

class TestPhase2AScoutAndEncounter(unittest.TestCase):

    # ==========================================================================
    # SCOUT TESTS
    # ==========================================================================
    def test_scout_initialization(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertIsNotNone(scout)
        self.assertEqual(scout.enemy_type, TARGET_TYPE_SCOUT)
        self.assertEqual(scout.ai_state, "approach")

    def test_scout_stats(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.hp, SCOUT_HP)
        self.assertEqual(scout.max_hp, SCOUT_HP)
        self.assertEqual(scout.speed, SCOUT_SPEED)
        self.assertEqual(scout.points, SCOUT_SCORE)
        self.assertEqual(scout.size, SCOUT_SIZE)
        self.assertEqual(scout.contact_damage, SCOUT_CONTACT_DAMAGE)

    def test_scout_approach(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1000, 400))
        initial_dist = (scout.pos - pygame.Vector2(400, 400)).length()
        scout.update(0.1, player_pos=(400, 400))
        new_dist = (scout.pos - pygame.Vector2(400, 400)).length()
        self.assertLess(new_dist, initial_dist)

    def test_scout_strafe(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1000, 400))
        scout.state_timer = 2.6
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "strafe")

    def test_scout_telegraph(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "strafe"
        scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "telegraph")

    def test_scout_dive(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "telegraph"
        scout.state_timer = SCOUT_TELEGRAPH_TIME + 0.05
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "dive")

    def test_scout_recover(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "dive"
        scout.state_timer = SCOUT_DIVE_DURATION + 0.05
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "recover")

    def test_scout_damage(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        scout.take_damage(14)
        self.assertEqual(scout.hp, SCOUT_HP - 14)
        self.assertTrue(scout.alive)
        self.assertGreater(scout.hit_flash_timer, 0.0)

    def test_scout_death(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        is_dead = scout.take_damage(35)
        self.assertTrue(is_dead)
        self.assertFalse(scout.alive)
        self.assertEqual(scout.hp, 0)

    def test_scout_contact_cooldown(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        # Hit 1
        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0 - SCOUT_CONTACT_DAMAGE)
        self.assertEqual(scout.contact_cooldown_timer, 1.0)

        # Repeated frames during cooldown must not re-damage
        for _ in range(5):
            combat.update_combat(0.016)
            self.assertEqual(ctx.player.health, 100.0 - SCOUT_CONTACT_DAMAGE)

    # ==========================================================================
    # ENCOUNTER SYSTEM LIFECYCLE TESTS
    # ==========================================================================
    def test_reset_does_not_start_encounter(self):
        encounter = EncounterSystem()
        encounter.reset()
        self.assertEqual(encounter.state, "idle")
        self.assertFalse(encounter.is_active)

    def test_encounter_reset_returns_idle(self):
        encounter = EncounterSystem()
        encounter.start()
        self.assertEqual(encounter.state, "waiting")

        encounter.reset()
        self.assertEqual(encounter.state, "idle")
        self.assertEqual(encounter.spawned_count, 0)
        self.assertEqual(encounter.eliminated_count, 0)
        self.assertIsNone(encounter.active_enemy)
        self.assertEqual(encounter.timer, 0.0)
        self.assertFalse(encounter.is_active)

    def test_encounter_explicit_start_works(self):
        encounter = EncounterSystem()
        self.assertEqual(encounter.state, "idle")
        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        self.assertTrue(encounter.is_active)

    def test_encounter_initial_delay_works(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        # Under initial delay (1.2s): no spawn
        encounter.update(0.6, ctx)
        self.assertEqual(len(ctx.target_group), 0)
        self.assertEqual(encounter.state, "waiting")

    def test_encounter_scout_1_spawns(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(encounter.spawned_count, 1)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(list(ctx.target_group)[0].enemy_type, TARGET_TYPE_SCOUT)

    def test_encounter_scout_2_waits_for_scout_1_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(len(ctx.target_group), 1)

        # Scout 1 stays alive -> Scout 2 does not spawn even if time passes
        encounter.update(4.0, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(encounter.spawned_count, 1)

    def test_encounter_scout_3_waits_for_scout_2_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        # S1 spawns and dies
        encounter.update(1.3, ctx)
        list(ctx.target_group)[0].kill()
        encounter.update(0.016, ctx)

        # S2 spawns
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.spawned_count, 2)
        self.assertEqual(len(ctx.target_group), 1)

        # S2 stays alive -> S3 does not spawn
        encounter.update(4.0, ctx)
        self.assertEqual(encounter.spawned_count, 2)

    def test_encounter_complete_after_scout_3(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        for _ in range(3):
            encounter.update(1.3, ctx)
            active = list(ctx.target_group)[-1]
            active.kill()
            encounter.update(0.016, ctx)

        self.assertEqual(encounter.state, "complete")
        self.assertTrue(encounter.is_complete)
        self.assertFalse(encounter.is_active)

    def test_encounter_exactly_three_scouts(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        for _ in range(3):
            encounter.update(1.3, ctx)
            active = list(ctx.target_group)[-1]
            active.kill()
            encounter.update(0.016, ctx)

        self.assertEqual(encounter.spawned_count, 3)
        self.assertEqual(encounter.eliminated_count, 3)

    # ==========================================================================
    # GAME INTEGRATION & SECTOR TRIGGER TESTS
    # ==========================================================================
    def test_reset_does_not_start_encounter(self):
        """Game.reset_game() must leave encounter in IDLE."""
        game = Game()
        game.reset_game()
        self.assertEqual(game.encounter_system.state, "idle")
        self.assertFalse(game.encounter_system.is_active)

    def test_sector_0_stage_1_does_not_start_scout_encounter(self):
        """Sector 0 Stage 1 should keep EncounterSystem in IDLE even after game updates."""
        game = Game()
        ctx = game.context
        ctx.current_sector_idx = 0
        ctx.current_sub_level = 1
        game.reset_game()
        self.assertEqual(game.encounter_system.state, "idle")

        ctx.state = STATE_PLAYING
        game.update(0.016)
        self.assertEqual(game.encounter_system.state, "idle")
        self.assertFalse(game.encounter_system.is_active)

    def test_sector_1_stage_1_does_start_scout_encounter(self):
        """Cyber Factory Sector 1 Stage 1 is IDLE after reset, and starts WAITING on game update."""
        game = Game()
        ctx = game.context
        ctx.current_sector_idx = 1
        ctx.current_sub_level = 1
        game.reset_game()

        # After reset_game, state must be IDLE
        self.assertEqual(game.encounter_system.state, "idle")
        self.assertFalse(game.encounter_system.is_active)

        # After Game update in STATE_PLAYING, Game explicitly starts it -> WAITING
        ctx.state = STATE_PLAYING
        game.update(0.016)
        self.assertEqual(game.encounter_system.state, "waiting")
        self.assertTrue(game.encounter_system.is_active)

    def test_sector_1_stage_1_starts_exactly_once(self):
        """Verify that repeated game updates do not re-trigger start()."""
        game = Game()
        ctx = game.context
        ctx.current_sector_idx = 1
        ctx.current_sub_level = 1
        game.reset_game()
        self.assertEqual(game.encounter_system.state, "idle")

        ctx.state = STATE_PLAYING
        game.update(0.016)
        self.assertEqual(game.encounter_system.state, "waiting")

        # Subsequent frames must continue timer rather than re-calling start()
        t_before = game.encounter_system.timer
        game.update(0.016)
        self.assertLess(game.encounter_system.timer, t_before)

    def test_encounter_suppresses_normal_spawner(self):
        """While encounter is WAITING or ACTIVE, is_suppressing_spawner is True."""
        encounter = EncounterSystem()
        self.assertEqual(encounter.state, "idle")
        self.assertFalse(encounter.is_suppressing_spawner)

        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        self.assertTrue(encounter.is_suppressing_spawner)

    def test_normal_spawner_resumes_after_complete(self):
        """Once encounter is COMPLETE, normal Spawner is no longer suppressed."""
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        for _ in range(3):
            encounter.update(1.3, ctx)
            active = list(ctx.target_group)[-1]
            active.kill()
            encounter.update(0.016, ctx)

        self.assertTrue(encounter.is_complete)
        self.assertFalse(encounter.is_suppressing_spawner)

    # ==========================================================================
    # 360-DEGREE PROJECTILE FLIGHT TEST
    # ==========================================================================
    def test_player_shooting_360_degrees_in_world_space(self):
        """Verify projectiles fired right, down, and across world space do not prematurely despawn."""
        player = Player((1200, 700))
        group = pygame.sprite.Group()

        # Fire Right (towards (2000, 700))
        bullets_right = player.shoot((2000, 700))
        self.assertGreater(len(bullets_right), 0)
        b_right = bullets_right[0]
        group.add(b_right)

        # Simulate 10 frames of motion to the right
        for _ in range(10):
            b_right.update(0.016)
        self.assertTrue(b_right.alive())
        self.assertGreater(b_right.pos.x, 1200.0)

        # Fire Down (towards (1200, 1300))
        player.shoot_timer = 0.0
        bullets_down = player.shoot((1200, 1300))
        self.assertGreater(len(bullets_down), 0)
        b_down = bullets_down[0]
        group.add(b_down)

        for _ in range(10):
            b_down.update(0.016)
        self.assertTrue(b_down.alive())
        self.assertGreater(b_down.pos.y, 700.0)


if __name__ == "__main__":
    unittest.main()
