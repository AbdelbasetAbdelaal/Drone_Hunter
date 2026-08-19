"""
================================================================================
            DRONE HUNTER 2D - PHASE 2C HEAVY & ENCOUNTER TESTS
================================================================================
Comprehensive headless test suite verifying:
- Heavy drone statistics, initialization, and armor properties
- Heavy 3-state AI state machine: APPROACH -> PRESSURE -> RECOVER -> APPROACH
- Deterministic Armor Damage Reduction (raw 100 -> ~80 received)
- Contact damage & 1.0s cooldown prevention
- Score pipeline (500 pts awarded once upon death)
- Phase 2C Controlled Single-Heavy Encounter lifecycle & Spawner suppression
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import pytest
import pygame

pygame.init()

from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from src.data.game_data import (
    TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED, HEAVY_HP, HEAVY_SPEED,
    HEAVY_SCORE, HEAVY_SIZE, HEAVY_CONTACT_DAMAGE, HEAVY_CONTACT_COOLDOWN,
    HEAVY_ARMOR, HEAVY_PRESSURE_DISTANCE, HEAVY_TELEGRAPH_TIME
)
from src.entities.enemy import Enemy, Heavy
from src.entities.player import Player
from src.systems.combat_system import CombatSystem
from src.systems.encounter_system import EncounterSystem, HEAVY_INTRO_ENCOUNTER
from src.core.game_context import GameContext
from src.core.game_state import STATE_PLAYING, STATE_MENU


class TestPhase2CHeavyAndEncounter:
    """Test suite for Phase 2C Heavy Drone, Armor, and Controlled Encounter."""

    def setup_method(self):
        self.context = GameContext()
        self.context.state = STATE_PLAYING
        self.player = Player(pos=(400.0, 400.0))
        self.context.player = self.player
        self.combat_system = CombatSystem(self.context)

    # --------------------------------------------------------------------------
    # 1. INITIALIZATION & STATS TESTS
    # --------------------------------------------------------------------------
    def test_heavy_initialization(self):
        heavy = Heavy(pos=(800.0, 400.0))
        assert heavy.enemy_type == TARGET_TYPE_HEAVY
        assert heavy.alive is True
        assert heavy.pos.x == 800.0
        assert heavy.pos.y == 400.0
        assert heavy.ai_state == "approach"

    def test_heavy_stats(self):
        heavy = Enemy(enemy_type=TARGET_TYPE_HEAVY, pos=(800.0, 400.0), sector_idx=0, hp_multiplier=1.0, speed_multiplier=1.0)
        assert heavy.hp == HEAVY_HP
        assert heavy.max_hp == HEAVY_HP
        assert heavy.speed == HEAVY_SPEED
        assert heavy.size == HEAVY_SIZE
        assert heavy.points == HEAVY_SCORE
        assert heavy.score_value == HEAVY_SCORE
        assert heavy.contact_damage == HEAVY_CONTACT_DAMAGE
        assert heavy.armor == HEAVY_ARMOR

    def test_heavy_subclass_matches_enemy_type(self):
        heavy = Heavy(pos=(600.0, 300.0))
        assert isinstance(heavy, Enemy)
        assert heavy.enemy_type == TARGET_TYPE_HEAVY
        assert heavy.hp == HEAVY_HP
        assert heavy.armor == HEAVY_ARMOR

    # --------------------------------------------------------------------------
    # 2. MOVEMENT & STATE MACHINE TESTS
    # --------------------------------------------------------------------------
    def test_heavy_approach_moves_toward_player(self):
        heavy = Heavy(pos=(800.0, 400.0))
        initial_x = heavy.pos.x
        # Player is at (400, 400), so heavy should move left
        heavy.update(0.10, player_pos=(400.0, 400.0), player_vel=(0.0, 0.0))
        assert heavy.pos.x < initial_x
        assert heavy.ai_state == "approach"

    def test_heavy_pressure_transition_at_pressure_distance(self):
        # Place heavy inside pressure distance (300px)
        heavy = Heavy(pos=(650.0, 400.0)) # dist = 250px < 300px
        heavy.update(0.016, player_pos=(400.0, 400.0), player_vel=(0.0, 0.0))
        assert heavy.ai_state == "pressure"

    def test_heavy_pressure_maintains_forward_thrust(self):
        heavy = Heavy(pos=(550.0, 400.0))
        heavy.ai_state = "pressure"
        heavy.state_timer = 0.0
        initial_x = heavy.pos.x
        heavy.update(0.10, player_pos=(400.0, 400.0), player_vel=(0.0, 0.0))
        # Forward thrust continues advancing toward player
        assert heavy.pos.x < initial_x

    def test_heavy_recovers_after_pressure_duration(self):
        heavy = Heavy(pos=(500.0, 400.0))
        heavy.ai_state = "pressure"
        heavy.state_timer = 2.6 # Exceeds 2.5s pressure duration
        heavy.update(0.016, player_pos=(400.0, 400.0), player_vel=(0.0, 0.0))
        assert heavy.ai_state == "recover"

    def test_heavy_recover_returns_to_approach(self):
        heavy = Heavy(pos=(500.0, 400.0))
        heavy.ai_state = "recover"
        heavy.state_timer = 0.90 # Exceeds 0.85s recover time
        heavy.update(0.016, player_pos=(400.0, 400.0), player_vel=(0.0, 0.0))
        assert heavy.ai_state == "approach"

    # --------------------------------------------------------------------------
    # 3. ARMOR & DAMAGE TESTS
    # --------------------------------------------------------------------------
    def test_heavy_deterministic_armor_damage_reduction(self):
        """Deterministic Armor Test: raw 100 damage -> ~80 received (20% reduction)."""
        heavy = Heavy(pos=(500.0, 400.0))
        initial_hp = heavy.hp
        raw_damage = 100
        heavy.take_damage(raw_damage, source="bullet")
        damage_taken = initial_hp - heavy.hp
        expected_damage = int(round(raw_damage * (1.0 - HEAVY_ARMOR))) # 80
        assert damage_taken == expected_damage
        assert damage_taken == 80

    def test_heavy_death_at_zero_hp(self):
        heavy = Heavy(pos=(500.0, 400.0))
        is_dead = heavy.take_damage(300, source="bullet")
        assert is_dead is True
        assert heavy.hp == 0
        assert heavy.alive is False

    def test_heavy_score_awarded_once_on_kill(self):
        heavy = Heavy(pos=(500.0, 400.0))
        self.context.target_group.add(heavy)
        assert self.context.level_score == 0

        # Destroy via direct bullet
        from src.entities.bullet import Bullet
        bullet = Bullet((498.0, 400.0), (1.0, 0.0), damage=300)
        self.context.bullet_group.add(bullet)

        self.combat_system.update_combat(0.016)
        assert self.context.level_score == HEAVY_SCORE
        assert not heavy.alive

        # Subsequent combat frame should not double award score
        self.combat_system.update_combat(0.016)
        assert self.context.level_score == HEAVY_SCORE

    # --------------------------------------------------------------------------
    # 4. CONTACT DAMAGE & COOLDOWN TESTS
    # --------------------------------------------------------------------------
    def test_heavy_contact_damage_and_cooldown(self):
        heavy = Heavy(pos=(400.0, 400.0)) # Directly overlapping player
        self.context.target_group.add(heavy)
        initial_player_health = self.player.health

        # First contact hit
        self.combat_system.update_combat(0.016)
        assert self.player.health < initial_player_health
        assert heavy.contact_cooldown_timer > 0.0

        health_after_first_hit = self.player.health
        # Immediate next frame while on cooldown should NOT deal damage
        self.combat_system.update_combat(0.016)
        assert self.player.health == health_after_first_hit

    # --------------------------------------------------------------------------
    # 5. CONTROLLED ENCOUNTER TESTS
    # --------------------------------------------------------------------------
    def test_heavy_encounter_initialization(self):
        encounter = EncounterSystem(config=HEAVY_INTRO_ENCOUNTER)
        assert encounter.state == "idle"
        assert encounter.total_count == 1
        assert encounter.config["enemy_type"] == TARGET_TYPE_HEAVY
        assert not encounter.is_active

    def test_heavy_encounter_starts_and_spawns_one_heavy(self):
        encounter = EncounterSystem(config=HEAVY_INTRO_ENCOUNTER)
        encounter.start()
        assert encounter.state == "waiting"
        assert encounter.is_active is True
        assert encounter.is_suppressing_spawner is True

        # Simulate delay elapse
        encounter.timer = 0.0
        encounter.update(0.016, self.context)
        assert encounter.state == "active"
        assert encounter.spawned_count == 1
        assert len(self.context.target_group) == 1
        spawned_enemy = list(self.context.target_group)[0]
        assert spawned_enemy.enemy_type == TARGET_TYPE_HEAVY

    def test_heavy_encounter_suppresses_and_resumes_spawner(self):
        encounter = EncounterSystem(config=HEAVY_INTRO_ENCOUNTER)
        encounter.start()
        encounter.timer = 0.0
        encounter.update(0.016, self.context)
        assert encounter.is_suppressing_spawner is True

        # Eliminate Heavy
        heavy = list(self.context.target_group)[0]
        heavy.alive = False
        heavy.kill()

        encounter.update(0.016, self.context)
        assert encounter.is_complete is True
        assert encounter.is_suppressing_spawner is False

    def test_heavy_encounter_reset(self):
        encounter = EncounterSystem(config=HEAVY_INTRO_ENCOUNTER)
        encounter.start()
        encounter.reset()
        assert encounter.state == "idle"
        assert encounter.spawned_count == 0
        assert encounter.eliminated_count == 0
        assert not encounter.is_active
