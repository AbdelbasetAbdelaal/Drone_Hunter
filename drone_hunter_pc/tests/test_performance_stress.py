import os
import sys
import time
import math
import random
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import Bullet, EnemyBullet, ContinuousBeam, TeslaArcBeam
from src.entities.obstacle import EnvironmentalObstacle
from src.rendering.particles import ParticleManager
from src.audio.audio_manager import AudioManager
from src.systems.combat_system import CombatSystem
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE
)
from src.utils.profiler import FrameProfiler


class TestPerformanceStress(unittest.TestCase):
    """Deterministic dense combat benchmark and performance regression tests."""

    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.display.set_mode((1280, 720))

    def setUp(self):
        random.seed(42)  # Deterministic seed for reproducible stress benchmark
        self.context = GameContext()
        self.context.player = Player((640.0, 360.0))
        self.context.player_group.add(self.context.player)
        self.context.particle_manager = ParticleManager()
        self.context.audio_manager = AudioManager()
        self.combat_system = CombatSystem(self.context)
        self.profiler = FrameProfiler(enabled=True)

    def _populate_dense_battlefield(self):
        """Spawns exactly 40 enemies, 120 player projectiles, 60 enemy projectiles, obstacles, and beam."""
        ctx = self.context

        # 1. 40 Diverse Enemies (including Shield Drones)
        enemy_types = [
            TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE
        ]
        for i in range(40):
            etype = enemy_types[i % len(enemy_types)]
            x = 200.0 + (i % 8) * 120.0 + random.uniform(-20.0, 20.0)
            y = 100.0 + (i // 8) * 100.0 + random.uniform(-20.0, 20.0)
            e = Enemy(enemy_type=etype, pos=(x, y))
            ctx.target_group.add(e)

        # 2. Obstacles
        for j in range(6):
            obs = EnvironmentalObstacle(obs_type="asteroid")
            obs.pos = pygame.Vector2(300.0 + j * 140.0, 250.0 + (j % 2) * 200.0)
            obs.rect.center = (int(obs.pos.x), int(obs.pos.y))
            ctx.obstacle_group.add(obs)

        # 3. 120 Player Projectiles Total:
        #    - 104 standard/rapid bullets
        #    - 1 continuous beam
        #    - 15 Tesla arc beams
        for k in range(104):
            bx = 640.0 + random.uniform(-50.0, 50.0)
            by = 500.0 + random.uniform(-30.0, 30.0)
            tx = random.uniform(200.0, 1000.0)
            ty = random.uniform(100.0, 400.0)
            b = Bullet((bx, by), (tx, ty), speed=800.0, damage=30)
            ctx.bullet_group.add(b)

        # 1 Continuous Beam
        beam = ContinuousBeam(muzzle_pos=(640.0, 360.0), angle_rad=-math.pi / 2, damage_per_second=200.0)
        ctx.bullet_group.add(beam)

        # 15 Tesla Beams
        for t_idx in range(15):
            bx = 640.0
            by = 360.0
            tx = 300.0 + t_idx * 40.0
            ty = 200.0
            tb = TeslaArcBeam((bx, by), (tx, ty), damage=35)
            ctx.bullet_group.add(tb)

        # 4. 60 Enemy Projectiles
        for m in range(60):
            ex = random.uniform(200.0, 1000.0)
            ey = random.uniform(100.0, 300.0)
            px = 640.0 + random.uniform(-40.0, 40.0)
            py = 360.0 + random.uniform(-40.0, 40.0)
            eb = EnemyBullet((ex, ey), (px, py), speed=320.0, damage=15)
            ctx.enemy_bullet_group.add(eb)

    def test_deterministic_stress_benchmark(self):
        """Runs 120 frames of dense combat simulation and verifies 60 FPS performance thresholds."""
        self._populate_dense_battlefield()

        dt = 0.016
        num_frames = 120

        for frame in range(num_frames):
            t_start = time.perf_counter()

            # Record profiler entities
            self.profiler.record_entities(
                enemies=len(self.context.target_group),
                player_bullets=len(self.context.bullet_group),
                enemy_bullets=len(self.context.enemy_bullet_group),
                obstacles=len(self.context.obstacle_group),
                particles=len(self.context.particle_manager.particles)
            )

            # 1. Update entities
            self.profiler.start_timer("combat_update")
            self.combat_system.update_combat(dt)
            self.profiler.stop_timer("combat_update")

            # 2. Update projectiles
            self.profiler.start_timer("projectile_update")
            self.context.bullet_group.update(dt)
            self.context.enemy_bullet_group.update(dt)
            self.profiler.stop_timer("projectile_update")

            # 3. Update enemies
            self.profiler.start_timer("enemy_update")
            self.context.target_group.update(dt, player_pos=self.context.player.pos)
            self.profiler.stop_timer("enemy_update")

            # 4. Update particles
            self.profiler.start_timer("particle_update")
            self.context.particle_manager.update(dt)
            self.profiler.stop_timer("particle_update")

            frame_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            self.profiler.record_frame_time(frame_elapsed_ms)

        stats = self.profiler.get_summary_stats()
        metrics = self.profiler.get_metrics()

        print(f"\n[STRESS BENCHMARK STATS] {stats} | Subsystem timers (total ms): {metrics['timers_ms']}")

        # Strict 60 FPS Acceptance Thresholds:
        # Average frame time <= 16.67 ms (60 FPS)
        # P95 frame time <= 20.0 ms
        self.assertLessEqual(stats["avg_ms"], 16.67, f"Average frame time {stats['avg_ms']}ms exceeded 16.67ms budget!")
        self.assertLessEqual(stats["p95_ms"], 20.0, f"P95 frame time {stats['p95_ms']}ms exceeded 20.0ms threshold!")

    def test_continuous_beam_shielded_and_unshielded_damage_in_same_frame(self):
        """Verify shielded target gets reduced damage and unshielded target gets full damage in the same frame."""
        ctx = self.context
        ctx.target_group.empty()
        ctx.bullet_group.empty()

        # Place beam along vertical line x=640 pointing straight up (y from 600 down to 0)
        beam = ContinuousBeam(muzzle_pos=(640.0, 600.0), angle_rad=-math.pi / 2, damage_per_second=300.0)
        ctx.bullet_group.add(beam)

        # Place Shield Drone at (640, 450)
        shield_drone = Enemy(enemy_type=TARGET_TYPE_SHIELD_DRONE, pos=(640.0, 450.0))
        ctx.target_group.add(shield_drone)

        # Target 1: Shielded Scout near shield drone at (640, 420) (distance 30 <= 160)
        shielded_target = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(640.0, 420.0))
        initial_hp_shielded = shielded_target.hp
        ctx.target_group.add(shielded_target)

        # Target 2: Unshielded Scout far away along beam at (640, 100) (distance 350 > 160)
        unshielded_target = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(640.0, 100.0))
        initial_hp_unshielded = unshielded_target.hp
        ctx.target_group.add(unshielded_target)

        dt = 0.1  # 100ms
        self.combat_system.update_combat(dt)

        base_expected = 300.0 * dt  # 30.0 damage
        shielded_expected = base_expected / 3.0  # 10.0 damage

        shielded_dmg_taken = initial_hp_shielded - shielded_target.hp
        unshielded_dmg_taken = initial_hp_unshielded - unshielded_target.hp

        # Assert shielded target took 1/3 damage and unshielded target took full damage in the SAME frame
        self.assertAlmostEqual(shielded_dmg_taken, shielded_expected, delta=0.5)
        self.assertAlmostEqual(unshielded_dmg_taken, base_expected, delta=0.5)
        self.assertEqual(unshielded_dmg_taken, shielded_dmg_taken * 3)

    def test_combat_correctness_under_stress(self):
        """Verifies beam, Tesla, shields, enemy projectiles, and death mechanics function accurately."""
        ctx = self.context
        ctx.target_group.empty()
        ctx.bullet_group.empty()
        ctx.enemy_bullet_group.empty()
        ctx.obstacle_group.empty()

        # 1. Spawn targets and a Tesla beam hitting primary target directly
        t1 = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(600.0, 300.0))
        t2 = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(650.0, 300.0))
        t1_hp = t1.hp
        t2_hp = t2.hp
        ctx.target_group.add(t1, t2)

        tb = TeslaArcBeam((600.0, 300.0), (600.0, 200.0), damage=20)
        ctx.bullet_group.add(tb)

        # 2. Spawn enemy bullet in beam path to test disintegration
        eb = EnemyBullet((600.0, 200.0), (600.0, 400.0), speed=100.0, damage=10)
        ctx.enemy_bullet_group.add(eb)

        beam = ContinuousBeam(muzzle_pos=(600.0, 500.0), angle_rad=-math.pi / 2, damage_per_second=200.0)
        ctx.bullet_group.add(beam)

        # Run 1 frame
        self.combat_system.update_combat(0.05)

        # 1. Verify Tesla beam damaged primary and chained target
        self.assertLess(t1.hp, t1_hp, "Tesla beam must damage primary target")
        self.assertLess(t2.hp, t2_hp, "Tesla beam must damage chained target")

        # 2. Verify enemy bullet in beam path was destroyed
        self.assertFalse(eb.alive(), "Enemy projectile caught in continuous beam must be destroyed")

        # 3. Verify kill recording when lethal damage is applied to an alive enemy
        t3 = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(700.0, 300.0))
        ctx.target_group.add(t3)
        lethal_bullet = Bullet((700.0, 300.0), (700.0, 300.0), speed=100.0, damage=999)
        ctx.bullet_group.add(lethal_bullet)
        prev_kills = ctx.total_kills
        self.combat_system.update_combat(0.016)
        self.assertGreater(ctx.total_kills, prev_kills, "Enemy death must register kill in context")


if __name__ == "__main__":
    unittest.main()
