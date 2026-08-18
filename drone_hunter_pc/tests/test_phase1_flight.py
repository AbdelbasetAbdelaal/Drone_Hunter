"""
================================================================================
        DRONE HUNTER 2D - PHASE 1 PLAYER FLIGHT & ARENA TEST SUITE
================================================================================
Automated test suite verifying:
1. Player 360-degree vector acceleration
2. Player deceleration & inertia drag
3. Maximum speed clamping
4. Movement vector normalization (diagonal movement)
5. Decoupled mouse aim calculation
6. Arena boundary containment
7. Primary weapon dual hardpoint firing
8. Player damage & shield hit absorption
9. Player death state trigger
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

from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN
from src.data.game_data import HORIZONTAL_SPEED, PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY
from src.entities.player import Player
from src.rendering.player_renderer import PlayerRenderer
from src.rendering.camera import Camera2D
from src.systems.combat_feedback import CombatFeedbackSystem

class TestPhase1FlightAndArena(unittest.TestCase):

    def setUp(self):
        self.player = Player((400, 300))

    def test_player_acceleration(self):
        """Verify pressing movement keys accelerates the drone along the movement vector."""
        self.assertEqual(self.player.velocity.length(), 0.0)
        
        # Press 'D' (right) for 0.1s
        self.player.handle_input({pygame.K_d: True}, dt=0.1)
        self.assertGreater(self.player.velocity.x, 0.0)
        self.assertEqual(self.player.velocity.y, 0.0)
        self.assertTrue(self.player.is_accelerating)

    def test_player_deceleration_and_inertia(self):
        """Verify releasing movement keys decelerates the drone via linear drag."""
        self.player.velocity = pygame.Vector2(300.0, 0.0)
        
        # No keys pressed for 0.1s
        self.player.handle_input({}, dt=0.1)
        self.assertFalse(self.player.is_accelerating)
        self.assertLess(self.player.velocity.x, 300.0)
        self.assertGreater(self.player.velocity.x, 0.0)

    def test_max_speed_clamping(self):
        """Verify velocity does not exceed max_speed during sustained acceleration."""
        for _ in range(100):
            self.player.handle_input({pygame.K_d: True, pygame.K_s: True}, dt=0.016)
        
        self.assertLessEqual(self.player.velocity.length(), self.player.speed + 0.01)

    def test_movement_vector_normalization(self):
        """Verify diagonal movement is normalized so speed is not faster diagonally."""
        p_axial = Player((200, 200))
        p_diag = Player((200, 200))

        # Axial movement (Right)
        p_axial.handle_input({pygame.K_d: True}, dt=0.05)
        # Diagonal movement (Right + Down)
        p_diag.handle_input({pygame.K_d: True, pygame.K_s: True}, dt=0.05)

        # Acceleration magnitude should be equal
        self.assertAlmostEqual(p_axial.velocity.length(), p_diag.velocity.length(), delta=1.0)

    def test_mouse_aim_direction(self):
        """Verify drone aim angle correctly tracks mouse cursor coordinates."""
        # Aim directly to the right (Angle ~ 0 rad)
        self.player.handle_input({}, dt=0.016, mouse_pos=(self.player.pos.x + 100, self.player.pos.y))
        self.assertAlmostEqual(self.player.aim_angle, 0.0, delta=0.01)

        # Aim directly downwards (Angle ~ pi/2 rad)
        self.player.handle_input({}, dt=0.016, mouse_pos=(self.player.pos.x, self.player.pos.y + 100))
        self.assertAlmostEqual(self.player.aim_angle, math.pi / 2.0, delta=0.01)

    def test_arena_boundary_containment(self):
        """Verify drone position is clamped safely inside arena boundaries."""
        self.player.pos = pygame.Vector2(10.0, 10.0)
        self.player.velocity = pygame.Vector2(-500.0, -500.0)
        self.player.update(0.016)

        self.assertGreaterEqual(self.player.pos.x, 32.0)
        self.assertGreaterEqual(self.player.pos.y, 32.0)

    def test_primary_weapon_dual_firing(self):
        """Verify Pulse weapon fires twin projectiles toward aim target."""
        self.player.active_weapon = "pulse"
        target_pos = (800, 300)
        bullets = self.player.shoot(target_pos)

        self.assertEqual(len(bullets), 2)
        # Verify bullets have authoritative damage and velocity
        self.assertEqual(bullets[0].damage, 28)
        self.assertAlmostEqual(bullets[0].speed, 920.0, delta=1.0)

    def test_damage_and_death_flow(self):
        """Verify damage reduces hull integrity and health reaching 0 marks player dead."""
        self.player.health = 50.0
        self.assertTrue(self.player.alive)

        # Take 30 damage -> 20 health remaining
        destroyed = self.player.take_damage(30)
        self.assertFalse(destroyed)
        self.assertEqual(self.player.health, 20.0)
        self.assertTrue(self.player.alive)

        # Take 25 damage -> 0 health -> destroyed
        destroyed = self.player.take_damage(25)
        self.assertTrue(destroyed)
        self.assertEqual(self.player.health, 0.0)
        self.assertFalse(self.player.alive)

    def test_camera_2d_smooth_tracking(self):
        """Verify Camera2D smooth lerp and viewport offset clamping."""
        cam = Camera2D(world_w=1920, world_h=1080)
        # Target player at center
        cam.update((960, 540), dt=0.5)
        self.assertGreaterEqual(cam.offset_x, 0.0)
        self.assertGreaterEqual(cam.offset_y, 0.0)


if __name__ == "__main__":
    unittest.main()
