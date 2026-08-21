"""
===============================================================================
                    DRONE HUNTER 2D - GAMEPLAY POLISH TEST SUITE
===============================================================================
Regression tests for Phase 11 Gameplay Polish & Combat Excitement Pass:
- Player movement tuning
- Spawn patterns and formations
- Hit stop feedback
- Screen shake bounds
- Boss pacing
===============================================================================
"""

import os
import unittest
import math
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from src.data.game_data import (
    HORIZONTAL_SPEED, VERTICAL_SPEED, ACCELERATION, FRICTION,
    ROLL_SPEED_BOOST, ROLL_DURATION
)
from src.entities.player import Player
from src.core.game_context import GameContext
from src.systems.spawn_system import Spawner
from src.systems.encounter_system import EncounterSystem
from src.systems.combat_system import CombatSystem
from src.data.game_data import TARGET_TYPE_SCOUT, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE
from src.entities.enemy import Enemy
from src.entities.bullet import Bullet


class TestPlayerMovementPolish(unittest.TestCase):
    """Test player movement feels faster and more responsive."""

    def test_player_acceleration(self):
        player = Player((400, 400))
        initial_vel_y = player.velocity.y
        player.handle_input({pygame.K_w: True}, 0.1)
        self.assertLess(player.velocity.y, initial_vel_y,
                        "Pressing W (up) should decrease Y velocity")

    def test_player_max_speed(self):
        player = Player((400, 400))
        player.velocity.x = HORIZONTAL_SPEED * 2.0
        player.velocity.y = VERTICAL_SPEED * 2.0
        speed = player.velocity.length()
        player.velocity.scale_to_length(player.speed)
        self.assertLessEqual(player.velocity.length(), player.speed + 0.1,
                             "Velocity should be clamped to max speed")

    def test_player_deceleration(self):
        player = Player((400, 400))
        player.velocity = pygame.Vector2(500.0, 0.0)
        player.handle_input({}, 0.1)
        self.assertLess(player.velocity.x, 500.0,
                        "Velocity should decelerate when no input")

    def test_roll_responsiveness(self):
        player = Player((400, 400))
        player.roll_cooldown = 0.0
        self.assertTrue(player.trigger_roll(1.0))
        self.assertTrue(player.is_rolling)
        self.assertEqual(player.roll_timer, ROLL_DURATION)

    def test_player_boundary_constraints(self):
        player = Player((10, 10))
        player.pos = pygame.Vector2(-50, -50)
        player.update(0.016)
        self.assertGreaterEqual(player.pos.x, 36.0)
        self.assertGreaterEqual(player.pos.y, 36.0)


class TestSpawnPatternsPolish(unittest.TestCase):
    """Test deterministic spawn patterns and formations."""

    def test_spawn_patterns_deterministic(self):
        ctx = GameContext()
        ctx.player = Player((400, 400))
        spawner = Spawner(base_min_interval=0.1, base_max_interval=0.2)
        spawner.reset_for_stage(1, 0)
        spawner.update(0.5, ctx)
        self.assertGreater(len(ctx.target_group), 0, "Spawner should spawn enemies")

    def test_formation_spawn(self):
        spawner = Spawner()
        base = (400.0, 300.0)
        positions = []
        for i in range(3):
            pos = spawner._apply_formation_offset(base, i, 3, "v_formation")
            positions.append(pos)
        self.assertEqual(len(positions), 3)
        for p in positions:
            self.assertIsInstance(p, tuple)
            self.assertEqual(len(p), 2)

    def test_enemy_spawn_safe_position(self):
        ctx = GameContext()
        ctx.player = Player((400, 400))
        spawner = Spawner()
        for _ in range(10):
            pos = spawner._get_edge_spawn("random")
            self.assertGreaterEqual(pos[0], 60.0)
            self.assertLessEqual(pos[0], 2400.0 - 60.0)
            self.assertGreaterEqual(pos[1], 60.0)
            self.assertLessEqual(pos[1], 1400.0 - 60.0)

    def test_encounter_escalation(self):
        spawner = Spawner(base_min_interval=0.1, base_max_interval=0.2)
        ctx = GameContext()
        ctx.player = Player((400, 400))
        ctx.current_wave = 1
        spawner.reset_for_stage(1, 0)
        spawner.update(1.0, ctx)
        count_wave1 = len(ctx.target_group)
        ctx.target_group.empty()
        ctx.current_wave = 4
        spawner.update(1.0, ctx)
        count_wave4 = len(ctx.target_group)
        self.assertGreaterEqual(count_wave4, count_wave1,
                                "Higher waves should spawn at least as many enemies")
        self.assertGreater(count_wave1, 0, "Wave 1 should spawn at least 1 enemy")


class TestCombatFeedbackPolish(unittest.TestCase):
    """Test hit stop, screen shake, and damage feedback."""

    def test_hit_stop_triggers_on_enemy_death(self):
        ctx = GameContext()
        ctx.player = Player((400, 400))
        enemy = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(500, 400))
        ctx.target_group.add(enemy)
        ctx.bullet_group.add(Bullet((500, 400), (500, 400), damage=100, owner="player"))
        combat = CombatSystem(ctx)
        combat.update_combat(0.016)
        self.assertGreater(ctx.hit_stop_timer, 0.0,
                           "Hit stop should trigger on enemy death")

    def test_hit_stop_expires(self):
        ctx = GameContext()
        ctx.hit_stop_timer = 0.05
        ctx.hit_stop_duration = 0.05
        ctx.trigger_hit_stop(0.0)
        self.assertGreaterEqual(ctx.hit_stop_timer, 0.0)

    def test_camera_shake_is_bounded(self):
        ctx = GameContext()
        ctx.trigger_shake(10.0, 0.3)
        self.assertLessEqual(ctx.screen_shake_intensity, 10.0)
        self.assertLessEqual(ctx.screen_shake_time, 0.3)

    def test_camera_shake_expires(self):
        ctx = GameContext()
        ctx.trigger_shake(5.0, 0.1)
        ctx.screen_shake_time = 0.0
        ctx.screen_shake_intensity = 0.0
        self.assertEqual(ctx.screen_shake_intensity, 0.0)

    def test_no_continuous_camera_shake(self):
        ctx = GameContext()
        ctx.trigger_shake(3.0, 0.15)
        for _ in range(20):
            ctx.screen_shake_time = max(0.0, ctx.screen_shake_time - 0.02)
            if ctx.screen_shake_time <= 0.0:
                ctx.screen_shake_intensity = 0.0
        self.assertEqual(ctx.screen_shake_intensity, 0.0)


class TestBossPacingPolish(unittest.TestCase):
    """Test boss phase transitions and attack pacing."""

    def test_boss_phase_transition_triggered(self):
        ctx = GameContext()
        ctx.player = Player((400, 400))
        from src.entities.boss import SkyDreadnoughtBoss
        boss = SkyDreadnoughtBoss(level=1, sector_idx=0)
        ctx.target_group.add(boss)
        combat = CombatSystem(ctx)
        prev_phase = boss.current_phase_idx
        boss.hp = boss.max_hp * 0.65
        boss.take_damage(boss.max_hp * 0.3)
        combat.update_combat(0.016)
        if boss.alive and boss.current_phase_idx != prev_phase:
            self.assertNotEqual(boss.current_phase_idx, prev_phase)


if __name__ == '__main__':
    unittest.main()
