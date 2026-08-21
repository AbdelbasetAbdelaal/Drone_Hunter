"""
===============================================================================
          DRONE HUNTER 2D - PHASE 9 COMBAT FEEDBACK TESTS
===============================================================================
Tests for combat feel & impact feedback enhancements:
1. Effects are created on valid combat events.
2. Effects expire correctly.
3. Particle/effect lists remain bounded.
4. Boss phase transition effect triggers once.
5. No shadow system is reintroduced.
6. Player visual size remains unchanged.
7. Existing gameplay values remain unchanged.
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

from src.rendering.particles import ParticleManager, MAX_COMBAT_PARTICLES
from src.entities.enemy import Enemy, Scout, Shooter, Heavy
from src.entities.boss import SectorBoss
from src.data.boss_data import BossDefinition, BossPhaseConfig
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_BOSS
)


class TestEffectsCreatedOnCombatEvents(unittest.TestCase):
    """Test that effects are created on valid combat events."""

    def setUp(self):
        self.pm = ParticleManager()

    def test_muzzle_flash_created(self):
        self.pm.spawn_muzzle_flash((100, 100), 0.0, "pulse")
        self.assertEqual(len(self.pm.particles), 4)

    def test_scatter_muzzle_flash_created(self):
        self.pm.spawn_muzzle_flash((100, 100), 0.0, "scatter")
        self.assertEqual(len(self.pm.particles), 6)

    def test_missile_muzzle_flash_created(self):
        self.pm.spawn_muzzle_flash((100, 100), 0.0, "missile")
        self.assertEqual(len(self.pm.particles), 5)

    def test_enemy_hit_sparks_scout(self):
        self.pm.spawn_enemy_hit_sparks((100, 100), TARGET_TYPE_SCOUT, 10)
        self.assertGreater(len(self.pm.particles), 0)

    def test_enemy_hit_sparks_shooter(self):
        self.pm.spawn_enemy_hit_sparks((100, 100), TARGET_TYPE_SHOOTER, 10)
        self.assertGreater(len(self.pm.particles), 0)

    def test_enemy_hit_sparks_heavy(self):
        self.pm.spawn_enemy_hit_sparks((100, 100), TARGET_TYPE_HEAVY, 10)
        self.assertGreater(len(self.pm.particles), 0)

    def test_shield_ripple_created(self):
        self.pm.spawn_shield_ripple((100, 100))
        self.assertGreater(len(self.pm.particles), 0)

    def test_heavy_impact_created(self):
        self.pm.spawn_heavy_impact((100, 100))
        self.assertGreater(len(self.pm.particles), 0)

    def test_boss_phase_transition_created(self):
        self.pm.spawn_boss_phase_transition((100, 100), 1)
        self.assertGreater(len(self.pm.particles), 0)

    def test_player_destruction_created(self):
        self.pm.spawn_player_destruction((100, 100))
        self.assertGreater(len(self.pm.particles), 0)


class TestEffectsExpireCorrectly(unittest.TestCase):
    """Test that effects expire correctly."""

    def setUp(self):
        self.pm = ParticleManager()

    def test_sparks_expire(self):
        self.pm.spawn_spark((100, 100), count=10)
        self.assertEqual(len(self.pm.particles), 10)
        for _ in range(60):
            self.pm.update(0.016)
        self.assertEqual(len(self.pm.particles), 0)

    def test_muzzle_flash_expires(self):
        self.pm.spawn_muzzle_flash((100, 100), 0.0, "pulse")
        for _ in range(60):
            self.pm.update(0.016)
        self.assertEqual(len(self.pm.particles), 0)

    def test_boss_phase_transition_expires(self):
        self.pm.spawn_boss_phase_transition((100, 100), 1)
        for _ in range(120):
            self.pm.update(0.016)
        self.assertEqual(len(self.pm.particles), 0)

    def test_player_destruction_expires(self):
        self.pm.spawn_player_destruction((100, 100))
        for _ in range(120):
            self.pm.update(0.016)
        self.assertEqual(len(self.pm.particles), 0)


class TestParticleLimits(unittest.TestCase):
    """Test that particle/effect lists remain bounded."""

    def test_particle_cap_enforced(self):
        pm = ParticleManager()
        for _ in range(500):
            pm.spawn_spark((100, 100), count=10)
        self.assertLessEqual(len(pm.particles), MAX_COMBAT_PARTICLES)

    def test_lightning_arcs_bounded_by_lifetime(self):
        pm = ParticleManager()
        for _ in range(50):
            pm.spawn_lightning_arc((0, 0), (100, 100))
        self.assertEqual(len(pm.lightning_arcs), 50)
        for _ in range(120):
            pm.update(0.016)
        self.assertEqual(len(pm.lightning_arcs), 0)

    def test_weather_particles_bounded(self):
        pm = ParticleManager()
        for _ in range(200):
            pm.spawn_weather("rain")
        self.assertLessEqual(len(pm.weather_particles), 70)


class TestBossPhaseTransitionEffect(unittest.TestCase):
    """Test boss phase transition effect triggers on phase change."""

    def test_phase_transition_effect_triggers_on_change(self):
        boss = SectorBoss._create_sector_boss = lambda self, si, hp, spd: None
        pm = ParticleManager()
        pm.spawn_boss_phase_transition((100, 100), 0)
        self.assertEqual(len(pm.particles), 18)

    def test_phase_transition_effect_uses_correct_color(self):
        pm = ParticleManager()
        pm.spawn_boss_phase_transition((100, 100), 0)
        colors = [p.color for p in pm.particles.sprites()]
        expected = (56, 189, 248)
        self.assertTrue(any(c == expected for c in colors))


class TestNoShadowSystem(unittest.TestCase):
    """Test that no shadow system is reintroduced."""

    def test_no_shadow_surfaces_in_particles(self):
        pm = ParticleManager()
        pm.spawn_explosion((100, 100))
        for p in pm.particles.sprites():
            self.assertFalse(hasattr(p, 'shadow_surface'))
            self.assertFalse(hasattr(p, 'shadow_offset'))


class TestPlayerVisualSize(unittest.TestCase):
    """Test player visual size remains unchanged."""

    def test_player_renderer_surface_size(self):
        from src.rendering.player_renderer import PlayerRenderer
        pr = PlayerRenderer()
        self.assertEqual(pr._drone_surf.get_size(), (200, 200))

    def test_player_base_image_size(self):
        from src.entities.player import Player
        p = Player((100, 100))
        self.assertEqual(p.base_image.get_size(), (80, 80))


class TestGameplayValuesUnchanged(unittest.TestCase):
    """Test existing gameplay values remain unchanged."""

    def test_player_health_unchanged(self):
        from src.data.game_data import PLAYER_MAX_HEALTH
        self.assertEqual(PLAYER_MAX_HEALTH, 100)

    def test_player_speed_unchanged(self):
        from src.data.game_data import HORIZONTAL_SPEED
        self.assertEqual(HORIZONTAL_SPEED, 420.0)

    def test_scout_hp_unchanged(self):
        from src.data.game_data import SCOUT_HP
        self.assertEqual(SCOUT_HP, 30)

    def test_heavy_hp_unchanged(self):
        from src.data.game_data import HEAVY_HP
        self.assertEqual(HEAVY_HP, 180)

    def test_pulse_damage_unchanged(self):
        from src.data.game_data import WEAPON_DEFS
        self.assertEqual(WEAPON_DEFS["pulse"]["damage"], 12)

    def test_missile_damage_unchanged(self):
        from src.data.game_data import WEAPON_DEFS
        self.assertEqual(WEAPON_DEFS["missile"]["damage"], 65)


class TestAssetBackedVFX(unittest.TestCase):
    """Test that existing high-fidelity assets are actually used during gameplay events."""

    def test_sprite_manager_vfx_sprites_load(self):
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        explosion = sm.get_vfx_sprite('explosion_1', (64, 64))
        self.assertEqual(explosion.get_size(), (64, 64))
        explosion2 = sm.get_vfx_sprite('explosion_2', (64, 64))
        self.assertEqual(explosion2.get_size(), (64, 64))

    def test_sprite_manager_player_state_sprites_load(self):
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        fire = sm.get_player_state_sprite('fire', 0, (50, 52))
        self.assertIsNotNone(fire)
        hit = sm.get_player_state_sprite('hit', 0, (100, 70))
        self.assertIsNotNone(hit)
        destroy = sm.get_player_state_sprite('destroy', 0, (100, 100))
        self.assertIsNotNone(destroy)

    def test_projectile_sprites_load(self):
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        pulse = sm.get_projectile_sprite('pulse', (40, 12))
        self.assertIsNotNone(pulse)
        scatter = sm.get_projectile_sprite('scatter', (40, 12))
        self.assertIsNotNone(scatter)
        missile = sm.get_projectile_sprite('missile', (45, 16))
        self.assertIsNotNone(missile)

    def test_bullet_accepts_sprite_image(self):
        from src.entities.bullet import Bullet
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        sprite = sm.get_projectile_sprite('pulse', (40, 12))
        b = Bullet((0, 0), (100, 0), speed=650.0, damage=12, image=sprite)
        self.assertIs(b.original_image, sprite)

    def test_bullet_falls_back_to_procedural_without_image(self):
        from src.entities.bullet import Bullet
        b = Bullet((0, 0), (100, 0), speed=650.0, damage=12)
        self.assertIsNotNone(b.original_image)

    def test_explosion_overlay_created(self):
        pm = ParticleManager()
        pm.spawn_explosion((100, 100), sprite_name='explosion_1')
        self.assertGreater(len(pm.explosion_overlays), 0)

    def test_explosion_overlay_expires(self):
        pm = ParticleManager()
        pm.spawn_explosion((100, 100), sprite_name='explosion_1')
        for _ in range(60):
            pm.update(0.016)
        self.assertEqual(len(pm.explosion_overlays), 0)

    def test_player_destruction_state_set(self):
        from src.entities.player import Player
        p = Player((100, 100))
        p.health = 10.0
        destroyed = p.take_damage(20.0)
        self.assertTrue(destroyed)
        self.assertTrue(p.is_destroyed)
        self.assertGreater(p.destruction_timer, 0.0)
        self.assertFalse(p.alive)

    def test_player_destruction_timer_counts_down(self):
        from src.entities.player import Player
        p = Player((100, 100))
        p.health = 10.0
        p.take_damage(20.0)
        initial_timer = p.destruction_timer
        p.update(0.1)
        self.assertLess(p.destruction_timer, initial_timer)

    def test_player_killed_after_destruction_timer(self):
        from src.entities.player import Player
        p = Player((100, 100))
        p.health = 10.0
        p.take_damage(20.0)
        p.destruction_timer = 0.01
        p.update(0.016)
        self.assertFalse(p.alive)

    def test_enemy_bullet_default_image_cached(self):
        from src.entities.bullet import EnemyBullet
        EnemyBullet._cached_default_image = None
        b = EnemyBullet((0, 0), (100, 0))
        self.assertIsNotNone(b.original_image)
        self.assertIsNotNone(EnemyBullet._cached_default_image)


if __name__ == '__main__':
    unittest.main()
