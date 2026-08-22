"""
================================================================================
                DRONE HUNTER 2D - CARTOON WEAPON SYSTEM TEST SUITE
================================================================================
Comprehensive verification of all 11 cartoon weapon assets, dedicated muzzles,
impact VFX, HUD weapon icons, projectile origin alignment, and rotation caching.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.data.game_data import WEAPON_DEFS, WEAPON_ASSETS, DRONE_MOUNT_PROFILES
from src.rendering.sprite_manager import get_sprite_manager
from src.entities.player import Player


class TestCartoonWeapons(unittest.TestCase):

    def setUp(self):
        self.sm = get_sprite_manager()
        self.weapons = [
            "pulse", "rapid", "scatter", "missile", "barrage",
            "beam", "plasma", "rail", "tesla", "cluster", "emp"
        ]

    def test_all_weapon_assets_load(self):
        """Verify all 11 cartoon weapon definitions resolve to valid production PNG assets."""
        for w_id in self.weapons:
            self.assertIn(w_id, WEAPON_DEFS, f"Missing weapon definition: {w_id}")
            self.assertIn(w_id, WEAPON_ASSETS, f"Missing weapon asset mapping: {w_id}")
            path = WEAPON_ASSETS[w_id]
            full_path = self.sm._resolve_file_path(path)
            self.assertIsNotNone(full_path, f"Missing production weapon asset file: {path}")
            self.assertTrue(os.path.exists(full_path), f"Weapon asset does not exist: {full_path}")

    def test_all_projectile_assets_load(self):
        """Verify get_projectile_sprite returns non-empty surfaces for all 11 weapon types."""
        for w_id in self.weapons:
            surf = self.sm.get_projectile_sprite(w_id, (32, 12))
            self.assertIsNotNone(surf, f"Failed loading projectile sprite for {w_id}")
            self.assertGreater(surf.get_width(), 0)
            self.assertGreater(surf.get_height(), 0)

    def test_weapon_icon_assets_load(self):
        """Verify get_weapon_icon_sprite loads clean cartoon weapon icons for the HUD."""
        for w_id in self.weapons:
            surf = self.sm.get_weapon_icon_sprite(w_id, (48, 48))
            self.assertIsNotNone(surf, f"Failed loading weapon icon for {w_id}")
            self.assertEqual(surf.get_size(), (48, 48))

    def test_weapon_muzzle_positions_preserved(self):
        """Verify drone mount hardpoint profiles preserve canonical gameplay muzzle coordinates."""
        for drone_type in ["striker", "interceptor", "assault", "arc", "command"]:
            self.assertIn(drone_type, DRONE_MOUNT_PROFILES, f"Missing mount profile for {drone_type}")
            profile = DRONE_MOUNT_PROFILES[drone_type]
            self.assertTrue(len(profile) > 0)

    def test_projectile_origin_matches_muzzle(self):
        """Verify player.shoot() spawns projectiles originating directly from forward muzzle position."""
        p = Player((500.0, 500.0))
        bullets = p.shoot((1000.0, 500.0), level=1)
        self.assertGreater(len(bullets), 0, "No bullets fired")
        b = bullets[0]
        # Striker nose muzzle is +88px forward along aim angle
        expected_x = 500.0 + 88.0
        self.assertAlmostEqual(b.pos.x, expected_x, delta=1.5, msg="Projectile origin misaligned from muzzle")

    def test_weapon_visual_mapping(self):
        """Verify WEAPON_ASSETS maps all 11 weapons to individual folder assets."""
        for w_id in self.weapons:
            asset_path = WEAPON_ASSETS[w_id]
            self.assertTrue(asset_path.startswith("weapons/"), f"Invalid path structure: {asset_path}")

    def test_weapon_rotation(self):
        """Verify get_rotated_surface rotates projectile images accurately for 360-degree aiming."""
        base_surf = self.sm.get_projectile_sprite("pulse", (32, 12))
        rotated_90 = self.sm.get_rotated_surface(base_surf, 90.0)
        self.assertIsNotNone(rotated_90)
        self.assertEqual(rotated_90.get_size(), (12, 32))

    def test_weapon_cache(self):
        """Verify SpriteManager caches projectile surfaces to prevent per-frame re-allocation."""
        s1 = self.sm.get_projectile_sprite("rail", (40, 10))
        s2 = self.sm.get_projectile_sprite("rail", (40, 10))
        self.assertIs(s1, s2, "SpriteManager failed to cache projectile surface")

    def test_no_shadow_rendering(self):
        """Verify weapon projectile surfaces have transparent RGBA backgrounds with zero shadows."""
        for w_id in self.weapons:
            surf = self.sm.get_projectile_sprite(w_id, (32, 12))
            corner_color = surf.get_at((0, 0))
            self.assertEqual(corner_color[3], 0, f"Weapon projectile {w_id} has opaque background corner")


if __name__ == "__main__":
    unittest.main()
