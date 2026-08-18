"""
================================================================================
    DRONE HUNTER 2D - PHASE 2A DEDICATED SCOUT & ENCOUNTER TEST SUITE
================================================================================
Exhaustive verification of:
1. Scout Initialization, Stats & Initial State
2. Movement State Machine (Approach, Strafe, Telegraph, Dive, Recover)
3. Telegraph Timing & Predictive Aiming
4. Damage, Lethal Elimination & Score Integrity
5. Contact Damage & Contact Cooldown
6. Sequential 3-Scout Encounter Lifecycle & Pacing
7. Spawner Suppression & Seamless Post-Encounter Resumption
8. Encounter Reset & Duplicate Prevention
9. Full Headless Game Integration in Cyber Factory (Sector 1, Stage 1)
10. Difficulty Multiplier Scaling
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

    # --------------------------------------------------------------------------
    # SCOUT INITIALIZATION & STATS
    # --------------------------------------------------------------------------
    def test_scout_initialization(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertIsNotNone(scout)
        self.assertEqual(scout.enemy_type, TARGET_TYPE_SCOUT)

    def test_scout_stats(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.hp, SCOUT_HP)
        self.assertEqual(scout.max_hp, SCOUT_HP)
        self.assertEqual(scout.speed, SCOUT_SPEED)
        self.assertEqual(scout.points, SCOUT_SCORE)
        self.assertEqual(scout.size, SCOUT_SIZE)

    def test_scout_initial_state(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.ai_state, "approach")

    # --------------------------------------------------------------------------
    # MOVEMENT STATE MACHINE
    # --------------------------------------------------------------------------
    def test_scout_approach(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1000, 400))
        initial_dist = (scout.pos - pygame.Vector2(400, 400)).length()
        scout.update(0.1, player_pos=(400, 400))
        new_dist = (scout.pos - pygame.Vector2(400, 400)).length()
        self.assertLess(new_dist, initial_dist)

    def test_scout_enters_strafe(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1000, 400))
        scout.state_timer = 2.6
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "strafe")

    def test_scout_enters_telegraph(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "strafe"
        scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "telegraph")

    def test_scout_enters_dive(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "telegraph"
        scout.state_timer = SCOUT_TELEGRAPH_TIME + 0.05
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "dive")

    def test_scout_enters_recover(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "dive"
        scout.state_timer = SCOUT_DIVE_DURATION + 0.05
        scout.update(0.016, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "recover")

    # --------------------------------------------------------------------------
    # TELEGRAPH & PREDICTIVE AIMING
    # --------------------------------------------------------------------------
    def test_scout_telegraph_timer(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "telegraph"
        scout.state_timer = 0.1
        scout.update(0.1, player_pos=(400, 400))
        self.assertEqual(scout.ai_state, "telegraph") # still telegraphing until 0.45s

    def test_scout_dive_target_uses_player_velocity(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(800, 400))
        scout.ai_state = "strafe"
        scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        player_pos = (400, 400)
        player_vel = (300, 0)
        scout.update(0.016, player_pos=player_pos, player_vel=player_vel)
        self.assertEqual(scout.ai_state, "telegraph")
        # Dive target should lead ahead of player_pos.x
        self.assertGreater(scout.dive_target.x, player_pos[0])

    # --------------------------------------------------------------------------
    # DAMAGE & SCORE
    # --------------------------------------------------------------------------
    def test_scout_takes_damage(self):
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

    def test_scout_score_value(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        self.assertEqual(scout.score_value, SCOUT_SCORE)

    # --------------------------------------------------------------------------
    # CONTACT DAMAGE & COOLDOWN
    # --------------------------------------------------------------------------
    def test_scout_contact_damage(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0 - SCOUT_CONTACT_DAMAGE)

    def test_scout_contact_damage_cooldown(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        combat.update_combat(0.016)
        hp_after_hit = ctx.player.health
        self.assertEqual(scout.contact_cooldown_timer, 1.0)

        # 5 subsequent frames during cooldown must NOT re-apply damage
        for _ in range(5):
            combat.update_combat(0.016)
            self.assertEqual(ctx.player.health, hp_after_hit)

    # --------------------------------------------------------------------------
    # ENCOUNTER SYSTEM LIFECYCLE
    # --------------------------------------------------------------------------
    def test_encounter_start(self):
        encounter = EncounterSystem()
        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        self.assertTrue(encounter.is_active)
        self.assertFalse(encounter.is_complete)

    def test_encounter_initial_wait(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(0.5, ctx)
        self.assertEqual(encounter.state, "waiting")
        self.assertEqual(len(ctx.target_group), 0)

    def test_encounter_spawns_scout(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(list(ctx.target_group)[0].enemy_type, TARGET_TYPE_SCOUT)

    def test_encounter_spawns_exactly_three_scouts(self):
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

    def test_encounter_waits_for_active_scout(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(len(ctx.target_group), 1)

        # Passing time while Scout 1 is alive must NOT spawn Scout 2
        encounter.update(4.0, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(encounter.spawned_count, 1)

    def test_encounter_spawns_second_scout_after_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        s1 = list(ctx.target_group)[0]
        s1.kill()
        encounter.update(0.016, ctx)
        self.assertEqual(encounter.state, "waiting")

        encounter.update(1.1, ctx)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(encounter.spawned_count, 2)

    def test_encounter_spawns_third_scout_after_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        # S1
        encounter.update(1.3, ctx)
        list(ctx.target_group)[0].kill()
        encounter.update(0.016, ctx)

        # S2
        encounter.update(1.1, ctx)
        list(ctx.target_group)[0].kill()
        encounter.update(0.016, ctx)

        # S3
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.spawned_count, 3)
        self.assertEqual(encounter.state, "active")

    def test_encounter_completes(self):
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

    # --------------------------------------------------------------------------
    # SPAWNER SUPPRESSION & RESUMPTION
    # --------------------------------------------------------------------------
    def test_normal_spawner_suppressed_during_encounter(self):
        encounter = EncounterSystem()
        encounter.start()
        self.assertTrue(encounter.is_suppressing_spawner)

    def test_normal_spawner_resumes_after_encounter(self):
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

    # --------------------------------------------------------------------------
    # RESET
    # --------------------------------------------------------------------------
    def test_encounter_reset(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()
        encounter.update(1.3, ctx)

        encounter.reset()
        self.assertEqual(encounter.state, "waiting")
        self.assertEqual(encounter.spawned_count, 0)
        self.assertEqual(encounter.eliminated_count, 0)

    def test_no_duplicate_scouts_after_reset(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()
        encounter.update(1.3, ctx)
        self.assertEqual(len(ctx.target_group), 1)

        ctx.target_group.empty()
        encounter.reset()
        self.assertEqual(len(ctx.target_group), 0)
        encounter.update(0.5, ctx)
        self.assertEqual(len(ctx.target_group), 0)

    # --------------------------------------------------------------------------
    # DIFFICULTY & SCORING INTEGRATION
    # --------------------------------------------------------------------------
    def test_scout_difficulty_scaling(self):
        scout_easy = Scout(enemy_type=TARGET_TYPE_SCOUT, hp_multiplier=0.75, speed_multiplier=0.85)
        scout_nightmare = Scout(enemy_type=TARGET_TYPE_SCOUT, hp_multiplier=1.80, speed_multiplier=1.35)

        self.assertLess(scout_easy.hp, scout_nightmare.hp)
        self.assertLess(scout_easy.speed, scout_nightmare.speed)

    def test_combat_system_awards_exact_score(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((200, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)

        bullet = Bullet((400, 400), (1, 0), speed=900.0, damage=SCOUT_HP + 10)
        ctx.bullet_group.add(bullet)

        combat = CombatSystem(ctx)
        combat.update_combat(0.016)

        self.assertEqual(ctx.level_score, SCOUT_SCORE)

    # --------------------------------------------------------------------------
    # FULL HEADLESS GAME INTEGRATION IN CYBER FACTORY (SECTOR 1, STAGE 1)
    # --------------------------------------------------------------------------
    def test_game_headless_integration(self):
        """Creates Game() in headless mode, enters Cyber Factory Stage 1-1, and tests full encounter."""
        game = Game()
        ctx = game.context
        ctx.current_sector_idx = 1 # Cyber Factory
        ctx.current_sub_level = 1   # Stage 1: Assembly Perimeter
        game.reset_game()
        ctx.state = STATE_PLAYING

        # 1. Initial wait (1.2s = 75 frames at 60fps) -> Scout #1 spawns
        for _ in range(80):
            game.update(0.016)

        self.assertEqual(len(ctx.target_group), 1)
        scout_1 = list(ctx.target_group)[0]
        self.assertEqual(scout_1.enemy_type, TARGET_TYPE_SCOUT)

        # Eliminate Scout #1
        scout_1.alive = False
        scout_1.kill()

        # 2. Advance 1.1s (70 frames) -> Scout #2 spawns
        for _ in range(70):
            game.update(0.016)

        self.assertEqual(len(ctx.target_group), 1)
        scout_2 = list(ctx.target_group)[0]
        self.assertEqual(scout_2.enemy_type, TARGET_TYPE_SCOUT)

        # Eliminate Scout #2
        scout_2.alive = False
        scout_2.kill()

        # 3. Advance 1.1s (70 frames) -> Scout #3 spawns
        for _ in range(70):
            game.update(0.016)

        self.assertEqual(len(ctx.target_group), 1)
        scout_3 = list(ctx.target_group)[0]
        self.assertEqual(scout_3.enemy_type, TARGET_TYPE_SCOUT)

        # Eliminate Scout #3
        scout_3.alive = False
        scout_3.kill()

        # 4. Advance frame -> Encounter reaches complete
        game.update(0.016)
        self.assertTrue(game.encounter_system.is_complete)
        self.assertFalse(game.encounter_system.is_active)


if __name__ == "__main__":
    unittest.main()
