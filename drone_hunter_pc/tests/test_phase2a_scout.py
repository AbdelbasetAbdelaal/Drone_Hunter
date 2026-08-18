"""
================================================================================
        DRONE HUNTER 2D - PHASE 2A SCOUT ENEMY & ENCOUNTER TEST SUITE
================================================================================
Verification tests covering:
1. Scout Initialization & Authoritative Baseline Stats (HP, speed, score, size)
2. Scout 4-State Movement Machine (Approach, Strafe, Telegraph, Dive, Recover)
3. Scout Contact Damage Application and Contact Cooldown
4. Player Roll Invulnerability during Scout Contact
5. Weapon Damage, Death, and Single Score Award
6. EncounterSystem Lifecycle (Spawn delay, 1-by-1 progression, Completion)
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

class TestPhase2AScoutAndEncounter(unittest.TestCase):

    def test_scout_initialization_stats(self):
        """Verify Scout initializes with authoritative baseline specs."""
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(600, 400))
        self.assertEqual(scout.enemy_type, TARGET_TYPE_SCOUT)
        self.assertEqual(scout.hp, SCOUT_HP)
        self.assertEqual(scout.max_hp, SCOUT_HP)
        self.assertEqual(scout.score_value, SCOUT_SCORE)
        self.assertEqual(scout.size, SCOUT_SIZE)
        self.assertEqual(scout.speed, SCOUT_SPEED)
        self.assertEqual(scout.dive_speed, SCOUT_DIVE_SPEED)
        self.assertEqual(scout.contact_damage, SCOUT_CONTACT_DAMAGE)
        self.assertEqual(scout.ai_state, "approach")

    def test_scout_movement_state_transitions(self):
        """Verify Scout advances through Approach -> Strafe -> Telegraph -> Dive -> Recover."""
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(1200, 400))
        player_pos = (500, 400)

        # 1. Approach -> Strafe
        scout.state_timer = 2.6
        scout.update(0.016, player_pos=player_pos)
        self.assertEqual(scout.ai_state, "strafe")

        # 2. Strafe -> Telegraph
        scout.state_timer = SCOUT_STRAFE_DURATION + 0.1
        scout.update(0.016, player_pos=player_pos)
        self.assertEqual(scout.ai_state, "telegraph")

        # 3. Telegraph -> Dive
        scout.state_timer = SCOUT_TELEGRAPH_TIME + 0.05
        scout.update(0.016, player_pos=player_pos)
        self.assertEqual(scout.ai_state, "dive")

        # 4. Dive -> Recover
        scout.state_timer = SCOUT_DIVE_DURATION + 0.05
        scout.update(0.016, player_pos=player_pos)
        self.assertEqual(scout.ai_state, "recover")

        # 5. Recover -> Strafe
        scout.state_timer = SCOUT_RECOVER_TIME + 0.05
        scout.update(0.016, player_pos=player_pos)
        self.assertEqual(scout.ai_state, "strafe")

    def test_scout_contact_damage_and_cooldown(self):
        """Verify Scout inflicts contact damage with 1.0s per-enemy cooldown."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        initial_hp = ctx.player.health

        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        # Frame 1: Contact damage applied
        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, initial_hp - SCOUT_CONTACT_DAMAGE)
        self.assertEqual(scout.contact_cooldown_timer, 1.0)

        # Frame 2: Immediately following frame should NOT re-apply damage (cooldown active)
        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, initial_hp - SCOUT_CONTACT_DAMAGE)

    def test_player_roll_invulnerability_against_scout_contact(self):
        """Verify player taking evasive roll ignores Scout contact damage."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((400, 400))
        ctx.player.trigger_roll()
        self.assertTrue(ctx.player.is_invulnerable)

        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)
        combat = CombatSystem(ctx)

        combat.update_combat(0.016)
        self.assertEqual(ctx.player.health, 100.0)

    def test_pulse_laser_damages_and_eliminates_scout_once(self):
        """Verify Pulse Laser bullets destroy Scout and award score exactly once."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((200, 400))
        scout = Scout(enemy_type=TARGET_TYPE_SCOUT, pos=(400, 400))
        ctx.target_group.add(scout)

        bullet = Bullet((400, 400), (1, 0), speed=900.0, damage=SCOUT_HP + 10)
        ctx.bullet_group.add(bullet)

        combat = CombatSystem(ctx)
        combat.update_combat(0.016)

        self.assertFalse(scout.alive)
        self.assertEqual(ctx.level_score, SCOUT_SCORE)

    def test_encounter_system_three_scout_progression(self):
        """Verify EncounterSystem sequentially spawns 3 Scouts and marks completion."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((1200, 700))
        encounter = EncounterSystem()

        # Start encounter
        encounter.start()
        self.assertEqual(encounter.state, "waiting")

        # Elapse spawn delay -> Scout 1 spawns
        encounter.update(1.3, ctx)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(len(ctx.target_group), 1)
        scout_1 = list(ctx.target_group)[0]
        self.assertEqual(scout_1.enemy_type, TARGET_TYPE_SCOUT)

        # Eliminate Scout 1
        scout_1.kill()
        encounter.update(0.016, ctx)
        self.assertEqual(encounter.state, "waiting")

        # Elapse respawn delay -> Scout 2 spawns
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(len(ctx.target_group), 1)
        scout_2 = list(ctx.target_group)[0]

        # Eliminate Scout 2
        scout_2.kill()
        encounter.update(0.016, ctx)
        self.assertEqual(encounter.state, "waiting")

        # Elapse respawn delay -> Scout 3 spawns
        encounter.update(1.1, ctx)
        self.assertEqual(encounter.state, "active")
        self.assertEqual(len(ctx.target_group), 1)
        scout_3 = list(ctx.target_group)[0]

        # Eliminate Scout 3 -> Encounter Complete
        scout_3.kill()
        encounter.update(0.016, ctx)
        self.assertEqual(encounter.state, "complete")
        self.assertTrue(encounter.is_complete)


if __name__ == "__main__":
    unittest.main()
