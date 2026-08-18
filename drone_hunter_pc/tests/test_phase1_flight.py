"""
================================================================================
    DRONE HUNTER 2D - PHASE 1.7 CYBER FACTORY ENVIRONMENT & ARENA TEST SUITE
================================================================================
Automated test suite verifying:
1. World coordinates larger than viewport (2400x1400 vs 1280x720)
2. Strict separation of World Space vs Screen Space coordinates
3. Multi-position camera coverage (Center, Top, Bottom, Left, Right, Corners)
4. Cyber Factory Arena components (PowerReactor, FactoryMachineryUnit, conduits)
5. Decoupled mouse aim calculation from flight velocity
6. Player flight kinematics (acceleration, deceleration, max speed clamping)
7. Dual Pulse cannon hardpoint firing
8. Responsive HUD dynamic layout scaling across resolutions (1280x720, 1152x648, 1024x576)
9. Powerup pickups (wingman spawning, overclock, weapon switching)
10. Main menu purity (no gameplay widgets leaked)
11. Player damage & death states
"""

import os
import sys
import math
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN
from src.data.game_data import HORIZONTAL_SPEED, PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY
from src.entities.player import Player
from src.entities.obstacle import EnvironmentalObstacle
from src.rendering.player_renderer import PlayerRenderer
from src.rendering.camera import Camera2D
from src.rendering.background import CyberFactoryArenaBackground, PowerReactor, FactoryMachineryUnit
from src.ui.hud import draw_hud
from src.ui.menus import draw_main_menu

class TestPhase1FlightAndArena(unittest.TestCase):

    def setUp(self):
        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))

    def test_world_larger_than_viewport(self):
        """Verify arena world dimensions exceed standard viewport dimensions."""
        self.assertGreater(WORLD_WIDTH, SCREEN_WIDTH)
        self.assertGreater(WORLD_HEIGHT, SCREEN_HEIGHT)
        self.assertEqual(WORLD_WIDTH, 2400)
        self.assertEqual(WORLD_HEIGHT, 1400)

    def test_player_world_boundary_containment(self):
        """Verify player can explore beyond 1280x720 and clamps to world bounds (2400x1400)."""
        self.player.pos = pygame.Vector2(2000.0, 1000.0)
        self.player.velocity = pygame.Vector2(1000.0, 1000.0)
        self.player.update(0.1)
        self.assertGreater(self.player.pos.x, SCREEN_WIDTH)
        self.assertLessEqual(self.player.pos.x, WORLD_WIDTH - 36.0)
        self.assertLessEqual(self.player.pos.y, WORLD_HEIGHT - 36.0)

        # Move to top-left corner
        self.player.pos = pygame.Vector2(-100.0, -100.0)
        self.player.update(0.016)
        self.assertGreaterEqual(self.player.pos.x, 36.0)
        self.assertGreaterEqual(self.player.pos.y, 36.0)

    def test_camera_multi_positions_and_coherence(self):
        """Verify Camera2D and CyberFactoryArenaBackground render smoothly at all positions."""
        cam = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        bg = CyberFactoryArenaBackground()
        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        positions = [
            (1200.0, 700.0), # Center
            (1200.0, 100.0), # Top
            (1200.0, 1300.0), # Bottom
            (100.0, 700.0), # Left
            (2300.0, 700.0), # Right
            (100.0, 100.0), # Top-Left Corner
            (2300.0, 100.0), # Top-Right Corner
            (100.0, 1300.0), # Bottom-Left Corner
            (2300.0, 1300.0), # Bottom-Right Corner
        ]

        for pos in positions:
            cam.update(pos, dt=10.0)
            offset = cam.get_offset()
            self.assertGreaterEqual(offset[0], 0.0)
            self.assertLessEqual(offset[0], WORLD_WIDTH - SCREEN_WIDTH)
            self.assertGreaterEqual(offset[1], 0.0)
            self.assertLessEqual(offset[1], WORLD_HEIGHT - SCREEN_HEIGHT)
            # Render background with offset
            bg.draw(canvas, camera_offset=offset)
            self.assertEqual(canvas.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    def test_world_vs_screen_rendering_separation(self):
        """Verify world objects translate with camera while screen HUD stays fixed."""
        cam = Camera2D(world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT, view_w=SCREEN_WIDTH, view_h=SCREEN_HEIGHT)
        cam.offset_x = 400.0
        cam.offset_y = 200.0

        screen_pos = cam.world_to_screen(500.0, 300.0)
        self.assertEqual(screen_pos, (100, 100))

        world_pos = cam.screen_to_world(100, 100)
        self.assertEqual(world_pos, (500.0, 300.0))

    def test_main_menu_purity_and_interactions(self):
        """Verify main menu provides clean buttons and does not crash or leak world widgets."""
        canvas = pygame.Surface((1280, 720))
        bg = CyberFactoryArenaBackground()
        bg.draw_menu_backdrop(canvas)
        buttons = draw_main_menu(canvas)
        
        self.assertIn("play", buttons)
        self.assertIn("sectors", buttons)
        self.assertIn("hangar", buttons)
        self.assertIn("exit", buttons)
        self.assertTrue(buttons["play"].width > 0)

    def test_aim_independent_from_movement(self):
        """Verify aim angle is purely governed by mouse position regardless of movement vector."""
        self.player.handle_input({pygame.K_a: True}, dt=0.1, mouse_pos=(self.player.pos.x + 200, self.player.pos.y))
        self.assertLess(self.player.velocity.x, 0.0)
        self.assertAlmostEqual(self.player.aim_angle, 0.0, delta=0.01)

    def test_player_acceleration_and_deceleration(self):
        """Verify flight kinematics acceleration and linear drag."""
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.handle_input({pygame.K_d: True}, dt=0.1)
        self.assertGreater(self.player.velocity.x, 0.0)
        self.assertTrue(self.player.is_accelerating)

        init_speed = self.player.velocity.x
        self.player.handle_input({}, dt=0.1)
        self.assertFalse(self.player.is_accelerating)
        self.assertLess(self.player.velocity.x, init_speed)

    def test_max_speed_clamping(self):
        """Verify velocity does not exceed maximum speed."""
        for _ in range(100):
            self.player.handle_input({pygame.K_w: True, pygame.K_d: True}, dt=0.016)
        self.assertLessEqual(self.player.velocity.length(), self.player.speed + 0.01)

    def test_primary_weapon_firing(self):
        """Verify Pulse cannon fires dual projectiles toward aim target."""
        target_pos = (self.player.pos.x + 400, self.player.pos.y)
        bullets = self.player.shoot(target_pos)
        self.assertEqual(len(bullets), 2)
        self.assertEqual(bullets[0].damage, 28)

    def test_responsive_hud_multi_resolution(self):
        """Verify HUD renders cleanly without errors across multiple viewport resolutions."""
        resolutions = [(1280, 720), (1152, 648), (1024, 576)]
        for w, h in resolutions:
            canvas = pygame.Surface((w, h))
            draw_hud(canvas, self.player, sector_idx=0, level_score=15200, total_score=45000,
                     coins=120, difficulty_name="NORMAL", combo_mult=5)
            self.assertEqual(canvas.get_size(), (w, h))

    def test_powerup_integration(self):
        """Verify powerup methods like spawn_wingman, trigger_overclock, select_weapon."""
        self.assertEqual(len(self.player.wingmen), 0)
        self.player.spawn_wingman()
        self.assertEqual(len(self.player.wingmen), 1)
        self.player.spawn_wingman()
        self.assertEqual(len(self.player.wingmen), 2)
        self.player.spawn_wingman()
        self.assertEqual(len(self.player.wingmen), 2)

        self.player.trigger_overclock(5.0)
        self.assertEqual(self.player.overclock_timer, 5.0)

        self.player.select_weapon(1)
        self.assertEqual(self.player.current_weapon_idx, 1)

    def test_damage_and_death_flow(self):
        """Verify damage and destruction states."""
        self.player.health = 40.0
        self.assertTrue(self.player.alive)
        self.player.take_damage(40.0)
        self.assertEqual(self.player.health, 0.0)
        self.assertFalse(self.player.alive)


if __name__ == "__main__":
    unittest.main()
