import os, sys, unittest, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.display.set_mode((1280, 720))
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import SECTORS
from src.data.mission_data import SECTORS_PHASE5
from src.rendering.environment import SectorEnvironmentManager, CyberFactoryEnvironment
from src.rendering.background import CyberFactoryArenaBackground, ParallaxBackground
from src.rendering.camera import Camera2D
class TestCartoonEnvironments(unittest.TestCase):
    def setUp(self):
        self.env_mgr = SectorEnvironmentManager(WORLD_WIDTH, WORLD_HEIGHT)
        self.bg = CyberFactoryArenaBackground(WORLD_WIDTH, WORLD_HEIGHT)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    def test_sectors_count_and_definitions(self):
        self.assertEqual(len(SECTORS), 5)
        self.assertEqual(len(SECTORS_PHASE5), 5)
        self.assertIn('Ocean', SECTORS[0]['name'])
        self.assertIn('Desert', SECTORS[1]['name'])
        self.assertIn('Jungle', SECTORS[2]['name'])
        self.assertIn('City', SECTORS[3]['name'])
        self.assertIn('Cyber Factory', SECTORS[4]['name'])
    def test_world_maps_file_integrity(self):
        asset_dir = self.env_mgr._resolve_background_dir()
        self.assertTrue(os.path.exists(asset_dir))
        for sec_id in range(1, 6):
            world_fp = os.path.join(asset_dir, f'sector_{sec_id}_world_2400.png')
            self.assertTrue(os.path.exists(world_fp))
            surf = self.env_mgr.get_sector_surface(sec_id - 1)
            self.assertEqual(surf.get_size(), (WORLD_WIDTH, WORLD_HEIGHT))
    def test_stage_variations_loading(self):
        for sec_idx in range(5):
            for stg in range(1, 4):
                surf = self.env_mgr.get_sector_surface(sec_idx, stg)
                self.assertIsNotNone(surf)
                self.assertEqual(surf.get_size(), (WORLD_WIDTH, WORLD_HEIGHT))
    def test_sector_switching_and_rendering(self):
        cam = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        test_positions = [(1200.0, 700.0), (0.0, 0.0), (2400.0, 1400.0), (1200.0, 0.0), (0.0, 700.0)]
        for sec_idx in range(5):
            self.bg.set_sector(sec_idx)
            self.assertEqual(self.bg.current_sector, sec_idx)
            for pos in test_positions:
                cam.update(pos, dt=10.0)
                offset = cam.get_offset()
                self.bg.draw(self.canvas, camera_offset=offset)
                self.assertEqual(self.canvas.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    def test_menu_backdrop_rendering(self):
        for sec_idx in range(5):
            self.bg.set_sector(sec_idx)
            self.bg.draw_menu_backdrop(self.canvas)
            self.assertEqual(self.canvas.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    def test_backward_compatibility_interfaces(self):
        self.assertIsNotNone(self.bg.reactor)
        self.assertIsNotNone(self.bg.machinery)
        self.assertIsNotNone(self.bg.floor)
        self.assertIsNotNone(self.bg.pipes)
        self.bg.update(0.016)
if __name__ == '__main__':
    unittest.main()
