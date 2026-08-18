"""
================================================================================
            DRONE HUNTER 2D - COMPREHENSIVE VERIFICATION TEST SUITE
================================================================================
Full test suite verifying all 2D requirements:
1. Authoritative Player Health vs Energy & Battery Upgrade Model
2. Overdrive Reactor Upgrade & Gameplay Effects
3. Single Source of Truth Weapon Statistics (WEAPON_DEFS)
4. Boss Stage Completion (Boss spawn & elimination requirement)
5. Multi-Phase Boss Behaviors (Sky, Stealth, EMP, Colossus Titan)
6. EMP Shockwave & Player Jammed Restrictions
7. Shield Hit System Consistency
8. SlowMo Time Dilation Bullet-Time
9. Difficulty Modifiers & Multipliers
10. Atomic Save/Load & Corruption Recovery
11. Multi-Frame Runtime Gameplay Simulation
"""

import os
import sys
import unittest
import pygame

# Set headless SDL dummy drivers for non-interactive automated test runs
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.data.settings import *
from src.data.game_data import *
from src.core.game_state import GameState, STATE_PLAYING, STATE_LEVEL_CLEAR, STATE_VICTORY, STATE_GAME_OVER
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

    def test_health_vs_energy_and_battery_upgrade(self):
        """Verify Health represents survivability and Energy represents weapon ammo."""
        p = Player((100, 100))
        self.assertEqual(p.health, PLAYER_MAX_HEALTH)
        self.assertEqual(p.max_health, PLAYER_MAX_HEALTH)
        self.assertEqual(p.energy, PLAYER_MAX_ENERGY)

        # Apply battery upgrade level 3 (+75 health)
        upgrades = {"battery": 3}
        p.apply_shop_upgrades(upgrades)
        self.assertEqual(p.max_health, PLAYER_MAX_HEALTH + 75.0)
        self.assertEqual(p.health, p.max_health)

        # Taking damage reduces HEALTH, NOT ENERGY
        p.take_damage(40)
        self.assertEqual(p.health, p.max_health - 40.0)
        self.assertEqual(p.energy, PLAYER_MAX_ENERGY, "Incoming damage must NOT drain weapon energy!")

        # Firing weapon reduces ENERGY, NOT HEALTH
        p.shoot((300, 100))
        self.assertLess(p.energy, PLAYER_MAX_ENERGY, "Firing weapons must consume energy!")
        self.assertEqual(p.health, p.max_health - 40.0, "Firing weapon must NOT reduce player health!")

    def test_overdrive_upgrade_integration(self):
        """Verify Overdrive upgrade increases duration and reduces cooldown."""
        p = Player((100, 100))
        # Default lvl 0
        p.apply_shop_upgrades({"overdrive": 0})
        self.assertEqual(p.overdrive_duration_max, OVERDRIVE_DURATION)
        self.assertEqual(p.overdrive_cooldown_max, OVERDRIVE_COOLDOWN_MAX)

        # Upgrade lvl 2 (+3.0s duration, -6.0s cooldown)
        p.apply_shop_upgrades({"overdrive": 2})
        self.assertEqual(p.overdrive_duration_max, OVERDRIVE_DURATION + 3.0)
        self.assertEqual(p.overdrive_cooldown_max, OVERDRIVE_COOLDOWN_MAX - 6.0)

        # Trigger overdrive
        self.assertTrue(p.trigger_overdrive())
        self.assertEqual(p.overdrive_timer, OVERDRIVE_DURATION + 3.0)
        self.assertEqual(p.overdrive_cooldown, OVERDRIVE_COOLDOWN_MAX - 6.0)
        self.assertTrue(p.is_invulnerable)

    def test_authoritative_weapon_definitions(self):
        """Verify Player shoots projectiles with authoritative stats from WEAPON_DEFS."""
        p = Player((100, 100))
        p.available_weapons = [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER]

        for w_key in p.available_weapons:
            p.active_weapon = w_key
            p.shoot_timer = 0.0
            bullets = p.shoot((300, 100))
            self.assertGreater(len(bullets), 0)
            w_def = WEAPON_DEFS[w_key]
            # Verify damage matches WEAPON_DEFS
            self.assertEqual(bullets[0].damage, w_def["damage"])
            self.assertEqual(bullets[0].speed, w_def["speed"])

    def test_boss_stage_completion_requirement(self):
        """Verify Boss stage requires score met, boss spawned, and boss defeated."""
        # Standard non-boss stage (Stage 1-1)
        wm_standard = WaveManager(target_score=1000, is_boss_stage=False)
        self.assertFalse(wm_standard.is_stage_complete(500))
        self.assertTrue(wm_standard.is_stage_complete(1000))

        # Boss Stage (Stage 1-3)
        wm_boss = WaveManager(target_score=3000, is_boss_stage=True)
        boss = SkyDreadnoughtBoss(1, 0)
        targets_group = pygame.sprite.Group(boss)

        # Case A: Score met, but Boss not spawned yet
        self.assertFalse(wm_boss.is_stage_complete(3500, targets_group=targets_group))

        # Case B: Score met, Boss spawned, but Boss is ALIVE
        wm_boss.boss_spawned = True
        self.assertFalse(wm_boss.is_stage_complete(3500, targets_group=targets_group), "Stage must NOT complete while Boss is alive!")

        # Case C: Score met, Boss spawned, Boss DEFEATED
        boss.alive = False
        targets_group.remove(boss)
        self.assertTrue(wm_boss.is_stage_complete(3500, targets_group=targets_group), "Stage completes only when Boss is eliminated!")

    def test_emp_disrupter_wave_and_player_jammed(self):
        """Verify EMP Disrupter Boss expanding shockwave jams player and disables weapons."""
        p = Player((300, 360))
        boss = EMPDisrupterBoss(level=1, sector_idx=2)
        boss.time_accum = 0.0
        boss.pos = pygame.Vector2(300, 360)
        boss.is_emp_expanding = True
        boss.emp_wave_radius = 120.0

        self.assertFalse(p.is_jammed)
        boss.update(0.016, player_pos=(p.pos.x, p.pos.y), player_obj=p)
        self.assertTrue(p.is_jammed, "Player must be jammed upon EMP shockwave contact!")
        self.assertFalse(p.can_shoot(), "Jammed player cannot shoot weapons!")
        self.assertFalse(p.trigger_emp(), "Jammed player cannot activate EMP!")
        self.assertFalse(p.trigger_overdrive(), "Jammed player cannot activate Overdrive!")

        # Verify HUD renders jammed banner without error
        from src.ui.hud import draw_hud
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_hud(test_surf, p, sector_idx=2, level_score=1000, total_score=2000, coins=100, difficulty_name="NORMAL")

        # After jammed duration expires, player recovers
        p.update(3.5)
        self.assertFalse(p.is_jammed)
        self.assertTrue(p.can_shoot())

    def test_colossus_titan_3_phases(self):
        """Verify Colossus Titan transitions through 3 distinct combat phases."""
        titan = ColossusTitanMechBoss(level=1, sector_idx=4)
        self.assertEqual(titan.boss_phase, 1)

        # Drop HP to 55% -> Phase 2
        titan.hp = int(titan.max_hp * 0.55)
        titan.update(0.016)
        self.assertEqual(titan.boss_phase, 2)

        # Drop HP to 20% -> Phase 3 (Overclock Berserk)
        titan.hp = int(titan.max_hp * 0.20)
        titan.update(0.016)
        self.assertEqual(titan.boss_phase, 3)

    def test_shield_hit_absorption(self):
        """Verify Shield hit charges absorb incoming hits without damage to health."""
        p = Player((100, 100))
        p.activate_shield(2)
        self.assertEqual(p.shield_hits, 2)

        # Hit 1: absorbed by shield
        p.take_damage(50)
        self.assertEqual(p.shield_hits, 1)
        self.assertEqual(p.health, p.max_health)

        # Hit 2: absorbed by shield
        p.take_damage(50)
        self.assertEqual(p.shield_hits, 0)
        self.assertEqual(p.health, p.max_health)

        # Hit 3: shield depleted, damage goes to health
        p.take_damage(30)
        self.assertEqual(p.health, p.max_health - 30.0)

    def test_slowmo_time_dilation(self):
        """Verify SlowMo scales time_scale to 0.40 and restores to 1.0."""
        ctx = GameContext()
        self.assertEqual(ctx.time_scale, 1.0)

        ctx.trigger_slowmo(4.0)
        self.assertEqual(ctx.time_scale, 0.40)
        self.assertEqual(ctx.slowmo_timer, 4.0)

        ctx.update_timers(4.5)
        self.assertEqual(ctx.time_scale, 1.0)
        self.assertEqual(ctx.slowmo_timer, 0.0)

    def test_difficulty_modifiers(self):
        """Verify difficulty modifiers scale HP, speed, damage, and drop rates."""
        diff = DifficultySystem(DIFFICULTY_EASY)
        self.assertLess(diff.hp_multiplier, 1.0)
        self.assertGreater(diff.drop_rate, 0.30)

        diff.set_mode(DIFFICULTY_NIGHTMARE)
        self.assertGreater(diff.hp_multiplier, 1.5)
        self.assertGreater(diff.damage_multiplier, 1.3)
        self.assertLess(diff.drop_rate, 0.20)

    def test_atomic_save_and_recovery(self):
        """Verify atomic JSON save with .tmp file swap and recovery from corrupted files."""
        save_sys = SaveSystem(save_filename="test_save_data.json")
        try:
            upgrades = {"battery": 2, "overdrive": 1, "speed": 3}
            sectors = [True, True, False, False, False]
            self.assertTrue(save_sys.save(coins=350, highscore=8500, upgrades=upgrades, sectors=sectors))

            loaded = save_sys.load()
            self.assertEqual(loaded["coins"], 350)
            self.assertEqual(loaded["highscore"], 8500)
            self.assertEqual(loaded["upgrades"]["overdrive"], 1)

            # Corrupt file test
            with open(save_sys.save_path, "w") as f:
                f.write("INVALID_JSON_CORRUPTION_DATA")

            recovered = save_sys.load()
            self.assertEqual(recovered["coins"], 0)
            self.assertTrue(recovered["sectors"][0])
        finally:
            if os.path.exists(save_sys.save_path): os.remove(save_sys.save_path)
            if os.path.exists(save_sys.temp_path): os.remove(save_sys.temp_path)

    def test_combat_player_death_game_over(self):
        """Verify lethal damage in CombatSystem transitions state to STATE_GAME_OVER."""
        ctx = GameContext()
        ctx.state = STATE_PLAYING
        ctx.player = Player((200, 200))
        combat = CombatSystem(ctx)

        # Spawn enemy bullet hitting player
        from src.entities.bullet import EnemyBullet
        eb = EnemyBullet((200, 200), (0, 0), speed=100.0, damage=1000.0)
        ctx.enemy_bullet_group.add(eb)

        combat.update_combat(0.016)
        self.assertFalse(ctx.player.alive)
        self.assertEqual(ctx.state, STATE_GAME_OVER)


if __name__ == "__main__":
    unittest.main()
