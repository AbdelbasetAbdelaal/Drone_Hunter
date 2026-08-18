"""
================================================================================
        DRONE HUNTER 2D - PHASE 2A SCOUT ENEMY & ENCOUNTER TEST SUITE
================================================================================
Exhaustive verification tests covering:
1. Scout initialization
2. Scout stats (HP 30, speed 210, size 32, contact damage 22, score 150)
3. Scout state starts as APPROACH
4. Approach -> Strafe
5. Strafe -> Telegraph
6. Telegraph -> Dive
7. Dive -> Recover
8. Contact damage cooldown (1.0s)
9. Scout death
10. Scout score value
11. Encounter starts
12. Encounter spawns exactly 3 Scouts
13. Second Scout waits for first death
14. Third Scout waits for second death
15. Encounter reaches COMPLETE
16. Encounter reset works
17. Normal Spawner is suppressed during intro
18. Normal Spawner resumes after intro
19. Encounter does not award score itself
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

from src.data.settings import *
from src.data.game_data import *
from src.core.game_state import STATE_PLAYING, STATE_LEVEL_CLEAR, STATE_GAME_OVER
from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.enemy import Enemy, Scout
from src.entities.bullet import Bullet
from src.systems.combat_system import CombatSystem
from src.systems.encounter_system import EncounterSystem, SCOUT_INTRO_ENCOUNTER
from src.systems.spawn_system import Spawner

class TestPhase2AScoutAndEncounter(unittest.TestCase):

    # 1. Scout initialization
    def test_01_scout_initialization(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertIsNotNone(scout)
        self.assertEqual(scout.enemy_type, TARGET_TYPE_SCOUT)

    # 2. Scout stats
    def test_02_scout_stats(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.hp, 30)
        self.assertEqual(scout.max_hp, 30)
        self.assertEqual(scout.speed, 210.0)
        self.assertEqual(scout.size, 32)
        self.assertEqual(scout.contact_damage, 22.0)
        self.assertEqual(scout.score_value, 150)

    # 3. Scout state starts as APPROACH
    def test_03_scout_state_starts_as_approach(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.ai_state, "approach")

    # 4. Approach -> Strafe
    def test_04_scout_transition_approach_to_strafe(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1200, 400))
        scout.state_timer = 2.6
        scout.update(0.016, player_pos=(500, 400))
        self.assertEqual(scout.ai_state, "strafe")

    # 5. Strafe -> Telegraph
    def test_05_scout_transition_strafe_to_telegraph(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "strafe"
        scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        scout.update(0.016, player_pos=(500, 400))
        self.assertEqual(scout.ai_state, "telegraph")

    # 6. Telegraph -> Dive
    def test_06_scout_transition_telegraph_to_dive(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "telegraph"
        scout.state_timer = SCOUT_TELEGRAPH_TIME + 0.05
        scout.update(0.016, player_pos=(500, 400))
        self.assertEqual(scout.ai_state, "dive")

    # 7. Dive -> Recover
    def test_07_scout_transition_dive_to_recover(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        scout.ai_state = "dive"
        scout.state_timer = SCOUT_DIVE_DURATION + 0.05
        scout.update(0.016, player_pos=(500, 400))
        self.assertEqual(scout.ai_state, "recover")

    # 8. Contact damage cooldown
    def test_08_scout_contact_damage_cooldown(self):
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0 - 22.0)
        self.assertEqual(scout.contact_cooldown_timer, 1.0)

        # Immediate next frame should not re-damage
        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0 - 22.0)

    # 9. Scout death
    def test_09_scout_death(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        is_destroyed = scout.take_damage(35)
        self.assertTrue(is_destroyed)
        self.assertFalse(scout.alive)
        self.assertEqual(scout.hp, 0)

    # 10. Scout score value
    def test_10_scout_score_value(self):
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        self.assertEqual(scout.score_value, 150)

    # 11. Encounter starts
    def test_11_encounter_starts(self):
        encounter = EncounterSystem()
        encounter.start()
        self.assertEqual(encounter.state, "waiting")
        self.assertTrue(encounter.is_active)
        self.assertFalse(encounter.is_complete)

    # 12. Encounter spawns exactly 3 Scouts
    def test_12_encounter_spawns_exactly_3_scouts(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        # Scout 1
        encounter.update(1.3, ctx)
        self.assertEqual(encounter.spawned_count, 1)
        s1 = list(ctx.target_group)[0]
        s1.kill()
        encounter.update(0.016, ctx)

        # Scout 2
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.spawned_count, 2)
        s2 = [t for t in ctx.target_group if t != s1][0]
        s2.kill()
        encounter.update(0.016, ctx)

        # Scout 3
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.spawned_count, 3)
        s3 = [t for t in ctx.target_group if t not in (s1, s2)][0]
        s3.kill()
        encounter.update(0.016, ctx)

        self.assertEqual(encounter.spawned_count, 3)
        self.assertEqual(encounter.eliminated_count, 3)

    # 13. Second Scout waits for first death
    def test_13_second_scout_waits_for_first_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(len(ctx.target_group), 1)

        # Do NOT kill first Scout -> even after time passes, second Scout must not spawn
        encounter.update(5.0, ctx)
        self.assertEqual(len(ctx.target_group), 1)
        self.assertEqual(encounter.spawned_count, 1)

    # 14. Third Scout waits for second death
    def test_14_third_scout_waits_for_second_death(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        s1 = list(ctx.target_group)[0]
        s1.kill()
        encounter.update(0.016, ctx)

        encounter.update(1.1, ctx)
        self.assertEqual(len(ctx.target_group), 1) # Scout 2 active

        # Scout 2 still alive -> Scout 3 must not spawn
        encounter.update(5.0, ctx)
        self.assertEqual(encounter.spawned_count, 2)

    # 15. Encounter reaches COMPLETE
    def test_15_encounter_reaches_complete(self):
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

    # 16. Encounter reset works
    def test_16_encounter_reset_works(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()
        encounter.start()
        encounter.update(1.3, ctx)
        self.assertEqual(encounter.spawned_count, 1)

        encounter.reset()
        self.assertEqual(encounter.state, "waiting")
        self.assertEqual(encounter.spawned_count, 0)
        self.assertEqual(encounter.eliminated_count, 0)

    # 17. Normal Spawner is suppressed during intro
    def test_17_normal_spawner_is_suppressed_during_intro(self):
        encounter = EncounterSystem()
        encounter.start()
        self.assertTrue(encounter.is_suppressing_spawner)
        self.assertTrue(encounter.is_active)

    # 18. Normal Spawner resumes after intro
    def test_18_normal_spawner_resumes_after_intro(self):
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
        self.assertFalse(encounter.is_active)

    # 19. Encounter does not award score itself
    def test_19_encounter_does_not_award_score_itself(self):
        ctx = GameContext()
        ctx.player = Player((1200, 700))
        ctx.level_score = 0
        encounter = EncounterSystem()
        encounter.start()

        encounter.update(1.3, ctx)
        self.assertEqual(ctx.level_score, 0) # Zero score added by encounter directly


if __name__ == "__main__":
    unittest.main()
