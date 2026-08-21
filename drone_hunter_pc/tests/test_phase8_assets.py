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
            'player/drone_chassis_0.png',
            'player/drone_chassis_1.png',
            'player/drone_chassis_2.png',
            'player/drone_chassis_3.png',
            'player/drone_chassis_4.png',
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
            'player/drone_chassis_0.png',
            'player/drone_chassis_1.png',
            'player/drone_chassis_2.png',
            'player/drone_chassis_3.png',
            'player/drone_chassis_4.png',
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
            self.assertGreater(transparent_count, 0, f'{rel_path} has no transparent pixels!')
            if 'shadow' not in rel_path:
                opaque_count = np.sum(alpha > 180)
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

    def test_scout_rotation_cache(self):
        s1 = self.sm.get_rotated_scout_sprite(state='idle', angle_deg=90.0, target_size=(52, 46))
        s2 = self.sm.get_rotated_scout_sprite(state='idle', angle_deg=90.0, target_size=(52, 46))
        self.assertIs(s1, s2)

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

    def test_shooter_assets_and_rotation_cache(self):
        s1 = self.sm.get_rotated_shooter_sprite(state='idle', angle_deg=45.0, target_size=(50, 46))
        s2 = self.sm.get_rotated_shooter_sprite(state='idle', angle_deg=45.0, target_size=(50, 46))
        self.assertIs(s1, s2)

        from src.entities.enemy import Enemy
        from src.data.game_data import TARGET_TYPE_SHOOTER
        shooter = Enemy(enemy_type=TARGET_TYPE_SHOOTER, pos=(400, 300))
        shooter.heading_angle = 60.0
        shooter._render_sprite()
        self.assertIsNotNone(shooter.image)

    def test_heavy_assets_and_rotation_cache(self):
        s1 = self.sm.get_rotated_heavy_sprite(state='idle', angle_deg=90.0, target_size=(62, 58))
        s2 = self.sm.get_rotated_heavy_sprite(state='idle', angle_deg=90.0, target_size=(62, 58))
        self.assertIs(s1, s2)

        from src.entities.enemy import Enemy
        from src.data.game_data import TARGET_TYPE_HEAVY
        heavy = Enemy(enemy_type=TARGET_TYPE_HEAVY, pos=(400, 300))
        heavy.heading_angle = 120.0
        heavy._render_sprite()
        self.assertIsNotNone(heavy.image)

    def test_shield_drone_assets_and_rotation_cache(self):
        s1 = self.sm.get_rotated_shield_drone_sprite(state='idle', angle_deg=180.0, target_size=(50, 46))
        s2 = self.sm.get_rotated_shield_drone_sprite(state='idle', angle_deg=180.0, target_size=(50, 46))
        self.assertIs(s1, s2)

        from src.entities.enemy import Enemy
        from src.data.game_data import TARGET_TYPE_SHIELD_DRONE
        shield_d = Enemy(enemy_type=TARGET_TYPE_SHIELD_DRONE, pos=(400, 300))
        shield_d._render_sprite()
        self.assertIsNotNone(shield_d.image)

    def test_all_five_bosses_assets_and_rendering(self):
        boss_keys = [
            'ASSEMBLY WARDEN',
            'CORE EXECUTOR',
            'REACTOR TITAN',
            'DEFENSE COMMANDER',
            'DRONE OVERLORD'
        ]
        for key in boss_keys:
            for phase in [1, 2, 3, 4]:
                b_surf = self.sm.get_boss_sprite(boss_key=key, phase=phase, target_size=(100, 100))
                self.assertIsNotNone(b_surf)
                self.assertEqual(b_surf.get_size(), (100, 100))

            rot1 = self.sm.get_rotated_boss_sprite(boss_key=key, angle_deg=30.0, phase=1, target_size=(100, 100))
            rot2 = self.sm.get_rotated_boss_sprite(boss_key=key, angle_deg=30.0, phase=1, target_size=(100, 100))
            self.assertIs(rot1, rot2)

    def test_projectiles_caching(self):
        for ptype in ['pulse', 'scatter', 'missile', 'enemy']:
            p1 = self.sm.get_projectile_sprite(ptype, (16, 16))
            p2 = self.sm.get_projectile_sprite(ptype, (16, 16))
            self.assertIs(p1, p2)

    def test_bounded_rotation_cache(self):
        self.sm.clear_rotation_cache()
        for deg in range(0, 1440, 2):
            self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=float(deg), target_size=(176, 152))
            self.sm.get_rotated_scout_sprite(state='idle', angle_deg=float(deg), target_size=(52, 46))
            self.sm.get_rotated_shooter_sprite(state='idle', angle_deg=float(deg), target_size=(52, 48))

        stats = self.sm.get_cache_stats()
        self.assertEqual(stats["max_rotation_capacity"], 120)
        self.assertLessEqual(stats["rotated_surfaces"], 120)
        self.assertEqual(stats["angle_step"], 6)

    def test_duplicate_state_cache_unification(self):
        s_idle = self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=32.0, target_size=(176, 152))
        s_move = self.sm.get_rotated_player_sprite(state='move', skin_idx=0, angle_deg=32.0, target_size=(176, 152))
        s_fire = self.sm.get_rotated_player_sprite(state='fire', skin_idx=0, angle_deg=32.0, target_size=(176, 152))
        s_bank_l = self.sm.get_rotated_player_sprite(state='bank_left', skin_idx=0, angle_deg=32.0, target_size=(176, 152))
        s_bank_r = self.sm.get_rotated_player_sprite(state='bank_right', skin_idx=0, angle_deg=32.0, target_size=(176, 152))

        self.assertIs(s_idle, s_move)
        self.assertIs(s_idle, s_fire)
        self.assertIs(s_idle, s_bank_l)
        self.assertIs(s_idle, s_bank_r)

    def test_player_large_gameplay_size(self):
        p_surf = self.sm.get_player_sprite(state='idle', skin_idx=0)
        self.assertEqual(p_surf.get_size(), (176, 152))
        p_rot = self.sm.get_rotated_player_sprite(state='idle', skin_idx=0, angle_deg=0.0)
        self.assertEqual(p_rot.get_size(), (176, 152))
        # Ensure gameplay hitbox radius is unchanged
        player = Player(pos=(400, 300))
        self.assertEqual(player.radius, 28)

    def test_shadow_apis_and_assets_completely_removed(self):
        shadow_methods = [
            'get_player_shadow',
            'get_scout_shadow',
            'get_shooter_shadow',
            'get_heavy_shadow',
            'get_shield_shadow',
            'get_boss_shadow',
        ]
        for m in shadow_methods:
            self.assertFalse(hasattr(self.sm, m), f'Obsolete shadow API {m} still present on SpriteManager!')

        for key in self.sm._canonical_cache.keys():
            self.assertNotIn('shadow', key.lower())

if __name__ == '__main__':
    unittest.main()

