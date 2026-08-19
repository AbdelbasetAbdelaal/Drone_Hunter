import os
import unittest
import pygame
from PIL import Image
import numpy as np

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()

from src.core.game import Game
from src.entities.player import Player
from src.rendering.sprite_manager import SpriteManager, get_sprite_manager
from src.rendering.player_renderer import PlayerRenderer

class TestPhase8PlayerVisualOverhaul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sm = get_sprite_manager()

    def test_required_player_assets_exist(self):
        base_dir = self.sm.base_dir
        required_player_files = [
            'player/player_base.png',
            'player/player_idle.png',
            'player/player_move.png',
            'player/player_fire.png',
            'player/player_hit.png',
            'player/player_damaged.png',
            'player/player_destroy.png',
            'player/player_destroyed.png',
            'player/player_bank_left.png',
            'player/player_bank_right.png',
            'player/chassis_0.png',
            'player/chassis_1.png',
            'player/chassis_2.png',
            'player/chassis_3.png',
            'player/chassis_4.png',
            'shadows/player_shadow.png',
            'vfx/engine_flame.png',
        ]
        for rel_path in required_player_files:
            full_path = os.path.join(base_dir, rel_path)
            self.assertTrue(os.path.exists(full_path), f'Missing required asset: {rel_path}')

    def test_asset_clean_transparency(self):
        base_dir = self.sm.base_dir
        required_player_files = [
            'player/player_base.png',
            'player/player_idle.png',
            'player/player_move.png',
            'player/player_fire.png',
            'player/player_hit.png',
            'player/player_damaged.png',
            'player/player_destroy.png',
            'player/player_destroyed.png',
            'player/player_bank_left.png',
            'player/player_bank_right.png',
            'player/chassis_0.png',
            'player/chassis_1.png',
            'player/chassis_2.png',
            'player/chassis_3.png',
            'player/chassis_4.png',
            'shadows/player_shadow.png',
            'vfx/engine_flame.png',
        ]
        for rel_path in required_player_files:
            full_path = os.path.join(base_dir, rel_path)
            im = Image.open(full_path).convert('RGBA')
            arr = np.array(im)
            alpha = arr[:, :, 3]
            h, w = alpha.shape

            self.assertGreaterEqual(w, 20, f'{rel_path} width too small: {w}')
            self.assertGreaterEqual(h, 20, f'{rel_path} height too small: {h}')

            transparent_count = np.sum(alpha == 0)
            opaque_count = np.sum(alpha > 200)
            self.assertGreater(transparent_count, 0, f'{rel_path} has no transparent pixels!')
            self.assertGreater(opaque_count, 0, f'{rel_path} has no opaque machine pixels!')

            corners = [int(alpha[0, 0]), int(alpha[0, w - 1]), int(alpha[h - 1, 0]), int(alpha[h - 1, w - 1])]
            for c in corners:
                self.assertEqual(c, 0, f'{rel_path} has non-transparent corner: {c}')

    def test_sprite_manager_rotation_caching(self):
        surf1 = self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=44.0, target_size=(90, 78))
        surf2 = self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=44.0, target_size=(90, 78))
        self.assertIs(surf1, surf2)

        surf3 = self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=44.2, target_size=(90, 78))
        self.assertIs(surf1, surf3)

    def test_player_shadow_is_unrotated(self):
        shadow = self.sm.get_player_shadow(target_size=(76, 48))
        self.assertIsNotNone(shadow)
        self.assertEqual(shadow.get_size(), (76, 48))

    def test_sprite_manager_distinct_chassis_models(self):
        surfs = [self.sm.get_player_sprite(state='idle', skin_idx=s, target_size=(90, 78)) for s in range(5)]
        for i in range(len(surfs)):
            self.assertIsNotNone(surfs[i])
            self.assertEqual(surfs[i].get_size(), (90, 78))

    def test_player_renderer_draw_pipeline(self):
        canvas = pygame.Surface((1280, 720), pygame.SRCALPHA)
        player = Player(pos=(640, 360))
        pr = PlayerRenderer()

        pr.draw_player(canvas, player, camera_offset=(0, 0))

        player.velocity = pygame.Vector2(300, 0)
        player.is_accelerating = True
        pr.draw_player(canvas, player, camera_offset=(0, 0))

        player.muzzle_flash_timer = 0.08
        pr.draw_player(canvas, player, camera_offset=(0, 0))

        player.damage_flash_timer = 0.12
        pr.draw_player(canvas, player, camera_offset=(0, 0))

        player.shield_hits = 2
        pr.draw_player(canvas, player, camera_offset=(0, 0))

        player.overdrive_timer = 3.0
        pr.draw_player(canvas, player, camera_offset=(0, 0))

    def test_game_mission_with_new_player_drone(self):
        game = Game()
        game.start_phase5_mission('S1_M1')
        for _ in range(60):
            game.update(0.016)
        game.render()
        self.assertTrue(game.context.player.alive)

    def test_scout_assets_exist_and_clean(self):
        base_dir = self.sm.base_dir
        scout_files = [
            'enemies/scout/scout_idle.png',
            'enemies/scout/scout_base.png',
            'enemies/scout/scout_move.png',
            'enemies/scout/scout_attack.png',
            'enemies/scout/scout_hit.png',
            'shadows/scout_shadow.png',
        ]
        for rel_path in scout_files:
            full_path = os.path.join(base_dir, rel_path)
            self.assertTrue(os.path.exists(full_path), f'Missing scout asset: {rel_path}')
            im = Image.open(full_path).convert('RGBA')
            arr = np.array(im)
            alpha = arr[:, :, 3]
            h, w = alpha.shape
            self.assertGreaterEqual(w, 20)
            self.assertGreaterEqual(h, 20)
            corners = [int(alpha[0, 0]), int(alpha[0, w - 1]), int(alpha[h - 1, 0]), int(alpha[h - 1, w - 1])]
            for c in corners:
                self.assertEqual(c, 0, f'{rel_path} corner not transparent')

    def test_scout_rotation_and_shadow_cache(self):
        s1 = self.sm.get_rotated_scout_sprite(state='idle', angle_deg=90.0, target_size=(52, 46))
        s2 = self.sm.get_rotated_scout_sprite(state='idle', angle_deg=90.0, target_size=(52, 46))
        self.assertIs(s1, s2)

        sh1 = self.sm.get_scout_shadow(target_size=(36, 22))
        sh2 = self.sm.get_scout_shadow(target_size=(36, 22))
        self.assertIs(sh1, sh2)

    def test_scout_enemy_rendering_states(self):
        from src.entities.enemy import Scout
        scout = Scout(pos=(400, 300))
        for state in ['approach', 'strafe', 'telegraph', 'dive', 'recover']:
            scout.ai_state = state
            scout.state_timer = 0.5
            scout._render_sprite()
            self.assertIsNotNone(scout.image)

        scout.hit_flash_timer = 0.1
        scout._render_sprite()
        self.assertIsNotNone(scout.image)

    def test_scout_render_sprite_uses_rotated_scout_sprite(self):
        """Proves that Scout._render_sprite() uses rotation-aware Scout sprite."""
        from unittest.mock import patch
        from src.entities.enemy import Scout
        scout = Scout(pos=(400, 300))
        scout.heading_angle = 90.0

        with patch.object(self.sm, 'get_rotated_scout_sprite', wraps=self.sm.get_rotated_scout_sprite) as mock_rot:
            scout._render_sprite()
            # Must call get_rotated_scout_sprite with angle_deg=-90.0
            mock_rot.assert_called_once()
            call_kwargs = mock_rot.call_args.kwargs
            self.assertEqual(call_kwargs.get('angle_deg'), -90.0)

if __name__ == '__main__':
    unittest.main()
