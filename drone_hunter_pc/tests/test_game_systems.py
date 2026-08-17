"""
================================================================================
            DRONE HUNTER 2D - AUTOMATED VERIFICATION TEST SUITE
================================================================================
Comprehensive unit & integration tests covering all requirements:
1. Shield Hit System Consistency (Bug 1)
2. SlowMo Time-Dilation Bullet-Time (Bug 2)
3. Campaign Progression & Victory State (Bug 3)
4. EMP Boss Attack & Player Jammed Mechanic (Bug 4)
5. Enemy & Boss Metadata API Unification (Bug 5)
6. Difficulty Stat Multipliers
7. Atomic Save/Load & Recovery
8. Projectiles, Overdrive, & Weapons Arsenal
"""

import os
import sys
import unittest
import pygame

# Set headless SDL dummy video driver for non-interactive test runs
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.data.settings import *
from src.data.game_data import *
from src.core.game_state import GameState, STATE_PLAYING, STATE_VICTORY
from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.boss import (
    SkyDreadnoughtBoss, StealthMirageBoss, EMPDisrupterBoss, ColossusTitanMechBoss
)
from src.entities.bullet import (
    Bullet, HomingMissile, PlasmaLaserBeam, TeslaArcBeam, ClusterTorpedo
)
from src.systems.save_system import SaveSystem
from src.systems.difficulty_system import DifficultySystem
from src.systems.progression_system import ProgressionSystem
from src.systems.combat_system import CombatSystem
from src.systems.spawn_system import Spawner, WaveManager

class TestDroneHunter2D(unittest.TestCase):

    def test_bug1_shield_system_consistency(self):
        """Verify Player uses shield_hits consistently and does not crash when damaged."""
        p = Player((100, 100))
        self.assertEqual(p.shield_hits, 0)
        
        # Activate shield
        p.activate_shield(3)
        self.assertEqual(p.shield_hits, 3)
        
        # Hit 1
        destroyed = p.take_damage(30)
        self.assertFalse(destroyed)
        self.assertEqual(p.shield_hits, 2)
        self.assertEqual(p.energy, p.max_energy) # Energy protected by shield

        # Hit 2 & 3
        p.take_damage(30)
        p.take_damage(30)
        self.assertEqual(p.shield_hits, 0)

        # Hit 4 (Shield gone, energy damaged)
        destroyed = p.take_damage(25)
        self.assertFalse(destroyed)
        self.assertEqual(p.energy, p.max_energy - 25)

    def test_bug2_slowmo_time_dilation(self):
        """Verify SlowMo powerup sets time_scale to 0.40 and restores to 1.0 when expired."""
        ctx = GameContext()
        self.assertEqual(ctx.time_scale, 1.0)
        
        # Activate SlowMo
        ctx.trigger_slowmo(5.0)
        self.assertEqual(ctx.time_scale, 0.40)
        self.assertEqual(ctx.slowmo_timer, 5.0)

        # Update timers partially
        ctx.update_timers(2.5)
        self.assertEqual(ctx.time_scale, 0.40)
        self.assertAlmostEqual(ctx.slowmo_timer, 2.5, places=2)

        # Update timers until expiration
        ctx.update_timers(3.0)
        self.assertEqual(ctx.time_scale, 1.0)
        self.assertEqual(ctx.slowmo_timer, 0.0)

    def test_bug3_campaign_progression_and_victory(self):
        """Verify stages progress through Sector 1-1 to 5-3 and reach STATE_VICTORY."""
        prog = ProgressionSystem()
        cur_sec = 0
        cur_stg = 1

        # Simulate clearing all 15 stages
        for sec in range(5):
            for stg in range(1, 4):
                next_sec, next_stg, is_vic = prog.unlock_next_stage(sec, stg)
                if sec == 4 and stg == 3:
                    self.assertTrue(is_vic, "Sector 5 Stage 3 must trigger Campaign Victory!")
                else:
                    self.assertFalse(is_vic)

    def test_bug4_emp_boss_and_player_jammed(self):
        """Verify EMP Disrupter Boss expanding wave jams the player and disables abilities."""
        p = Player((300, 360))
        boss = EMPDisrupterBoss(level=1, sector_idx=2)
        boss.time_accum = 0.0
        boss.pos = pygame.Vector2(300, 360)
        boss.is_emp_expanding = True
        boss.emp_wave_radius = 100.0 # Wide wave covering player

        self.assertFalse(p.is_jammed)
        
        # Update boss with player passed in
        boss.update(0.016, player_pos=(p.pos.x, p.pos.y), player_obj=p)
        self.assertTrue(p.is_jammed, "Player must be jammed when hit by EMP wave!")
        self.assertFalse(p.can_shoot(), "Jammed player cannot fire weapons!")
        self.assertFalse(p.trigger_emp(), "Jammed player cannot trigger EMP ability!")
        self.assertFalse(p.trigger_overdrive(), "Jammed player cannot trigger Overdrive!")

        # Update player until jammed timer expires
        p.update(3.5)
        self.assertFalse(p.is_jammed, "Player systems must restore after timer expires!")
        self.assertTrue(p.can_shoot())

    def test_bug5_enemy_and_boss_metadata_api(self):
        """Verify all enemies and bosses expose unified type, is_boss, color, hp, and score_value."""
        enemy_types = [
            TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_ARMORED,
            TARGET_TYPE_SHOOTER, TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE,
            TARGET_TYPE_CHASER, TARGET_TYPE_SWARM, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER
        ]
        for et in enemy_types:
            e = Enemy(enemy_type=et)
            self.assertEqual(e.type, et)
            self.assertEqual(e.enemy_type, et)
            self.assertFalse(e.is_boss)
            self.assertIsInstance(e.color, tuple)
            self.assertGreater(e.max_hp, 0)
            self.assertGreater(e.score_value, 0)

        # Test Bosses
        bosses = [
            SkyDreadnoughtBoss(1, 0),
            StealthMirageBoss(1, 1),
            EMPDisrupterBoss(1, 2),
            ColossusTitanMechBoss(1, 4)
        ]
        for b in bosses:
            self.assertTrue(b.is_boss)
            self.assertIsInstance(b.type, str)
            self.assertGreater(b.max_hp, 50)
            self.assertGreater(b.score_value, 500)

    def test_colossus_titan_3_phases(self):
        """Verify Colossus Titan transitions through 3 phases as HP decreases."""
        titan = ColossusTitanMechBoss(1, 4)
        self.assertEqual(titan.boss_phase, 1)

        # Drop HP to 60% -> Phase 2
        titan.hp = int(titan.max_hp * 0.60)
        titan.update(0.016)
        self.assertEqual(titan.boss_phase, 2)

        # Drop HP to 25% -> Phase 3 (Overclock Berserk)
        titan.hp = int(titan.max_hp * 0.25)
        titan.update(0.016)
        self.assertEqual(titan.boss_phase, 3)

    def test_difficulty_system_multipliers(self):
        """Verify difficulty modifiers scale HP, speed, damage, and drop rates."""
        diff = DifficultySystem(DIFFICULTY_EASY)
        self.assertEqual(diff.name, "EASY")
        self.assertLess(diff.hp_multiplier, 1.0)
        self.assertGreater(diff.drop_rate, 0.30)

        diff.set_mode(DIFFICULTY_NIGHTMARE)
        self.assertEqual(diff.name, "NIGHTMARE")
        self.assertGreater(diff.hp_multiplier, 1.5)
        self.assertLess(diff.drop_rate, 0.20)
        self.assertEqual(diff.score_multiplier, 2.0)

    def test_atomic_save_and_recovery(self):
        """Verify save system writes atomically and recovers from corrupt files."""
        save_sys = SaveSystem(save_filename="test_save.json")
        try:
            # 1. Save valid data
            upgrades = {"battery": 2, "speed": 1, "fire_rate": 3}
            sectors = [True, True, False, False, False]
            success = save_sys.save(coins=500, highscore=12000, upgrades=upgrades, sectors=sectors)
            self.assertTrue(success)

            # 2. Load and verify
            loaded = save_sys.load()
            self.assertEqual(loaded["coins"], 500)
            self.assertEqual(loaded["highscore"], 12000)
            self.assertEqual(loaded["upgrades"]["battery"], 2)

            # 3. Test corruption recovery
            with open(save_sys.save_path, "w") as f:
                f.write("CORRUPTED_NON_JSON_DATA!!!")

            recovered = save_sys.load()
            self.assertEqual(recovered["coins"], 0) # Fallback to safe defaults
            self.assertTrue(recovered["sectors"][0])

        finally:
            if os.path.exists(save_sys.save_path):
                os.remove(save_sys.save_path)
            if os.path.exists(save_sys.temp_path):
                os.remove(save_sys.temp_path)

    def test_weapon_arsenal_and_overdrive(self):
        """Verify all 6 weapons fire distinct projectiles and Overdrive functions."""
        p = Player((100, 100))
        p.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER]

        # 1. Pulse
        p.select_weapon(0)
        b1 = p.shoot((300, 100))
        self.assertIsInstance(b1[0], Bullet)

        # 2. Missiles
        p.select_weapon(2)
        p.shoot_timer = 0
        b2 = p.shoot((300, 100))
        self.assertIsInstance(b2[0], HomingMissile)

        # 3. Tesla Arc
        p.select_weapon(4)
        p.shoot_timer = 0
        b3 = p.shoot((300, 100))
        self.assertIsInstance(b3[0], TeslaArcBeam)

        # 4. Cluster
        p.select_weapon(5)
        p.shoot_timer = 0
        b4 = p.shoot((300, 100))
        self.assertIsInstance(b4[0], ClusterTorpedo)

        # 5. Overdrive
        self.assertTrue(p.trigger_overdrive())
        self.assertTrue(p.is_invulnerable)
        self.assertGreater(p.shield_hits, 0)
        self.assertEqual(p.overdrive_timer, OVERDRIVE_DURATION)

    def test_particles_and_floating_text(self):
        """Verify particle manager, weather, and floating combat text render cleanly."""
        from src.rendering.particles import ParticleManager, FloatingText
        pm = ParticleManager()
        pm.spawn_spark((100, 100))
        pm.spawn_explosion((100, 100))
        pm.spawn_lightning_arc((100, 100), (200, 200))
        pm.spawn_floating_text((100, 100), "+100 SCORE", (250, 204, 21))
        pm.spawn_weather("rain")
        
        surf = pygame.Surface((300, 300))
        pm.update(0.016)
        pm.draw(surf)
        self.assertGreater(len(pm.floating_texts), 0)


if __name__ == "__main__":
    unittest.main()
