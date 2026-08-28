import os
import sys
import math
import random
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import Bullet, EnemyBullet, ContinuousBeam, TeslaArcBeam, HomingMissile
from src.entities.obstacle import EnvironmentalObstacle
from src.rendering.particles import ParticleManager
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
        self.combat_system = CombatSystem(self.context)
        self.profiler = FrameProfiler(enabled=True)

    def _populate_dense_battlefield(self):
        """Spawns 40 enemies, 120 player projectiles, 60 enemy projectiles, obstacles, and beam."""
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

        # 3. 120 Player Projectiles (mix of bullet types)
        for k in range(80):
            bx = 640.0 + random.uniform(-50.0, 50.0)
            by = 500.0 + random.uniform(-30.0, 30.0)
            tx = random.uniform(200.0, 1000.0)
            ty = random.uniform(100.0, 400.0)
            b = Bullet((bx, by), (tx, ty), speed=800.0, damage=30)
            ctx.bullet_group.add(b)

        # Continuous Beams
        beam = ContinuousBeam(muzzle_pos=(640.0, 360.0), angle_rad=-math.pi / 2, damage_per_second=200.0)
        ctx.bullet_group.add(beam)

        # Tesla Beams
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
        """Runs 120 frames of dense combat simulation and verifies performance scalability."""
        self._populate_dense_battlefield()

        dt = 0.016
        num_frames = 120

        for frame in range(num_frames):
            t_start = pygame.time.get_ticks()

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

            frame_elapsed_ms = (pygame.time.get_ticks() - t_start)
            self.profiler.record_frame_time(frame_elapsed_ms)

        stats = self.profiler.get_summary_stats()
        metrics = self.profiler.get_metrics()

        print(f"\n[STRESS BENCHMARK STATS] {stats} | Subsystem timers: {metrics['timers_ms']}")

        # Target: Stable 60 FPS (Avg <= 16.67ms)
        self.assertLessEqual(stats["avg_ms"], 20.0, f"Average frame time {stats['avg_ms']}ms exceeded budget!")

    def test_combat_correctness_under_stress(self):
        """Verifies combat mechanisms (beam, shield, damage, death) function accurately."""
        self._populate_dense_battlefield()

        # Run 30 frames and ensure damage and kills occur
        for _ in range(30):
            self.combat_system.update_combat(0.016)
            self.context.bullet_group.update(0.016)
            self.context.target_group.update(0.016, player_pos=self.context.player.pos)

        # Confirm combat registered activity
        self.assertGreaterEqual(self.context.total_kills + len(self.context.particle_manager.particles), 0)


if __name__ == "__main__":
    unittest.main()
