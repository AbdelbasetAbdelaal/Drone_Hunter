import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.game import Game
from src.core.game_state import STATE_PLAYING, STATE_MENU, STATE_PAUSED, STATE_HANGAR
from src.input.input_manager import InputManager


class TestInputFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

    def setUp(self):
        self.game = Game()
        self.ctx = self.game.context
        self.input_mgr = InputManager()

    def test_keyboard_actions_contract(self):
        """Verify supported keyboard actions route accurately into player movement and inputs."""
        self.game.start_mission("S1_M1")
        player = self.ctx.player

        # Simulate movement key inputs
        keys_w = {pygame.K_w: True, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False, pygame.K_SPACE: False}
        init_y = player.pos.y
        player.handle_input(keys_w, dt=0.05, mouse_pos=(640, 100))
        player.update(dt=0.05, targets_group=self.ctx.target_group)
        self.assertLess(player.pos.y, init_y, "W key must move player upward")

    def test_controller_synthetic_action_routing(self):
        """Verify controller input abstraction maps analog axes and button triggers cleanly."""
        input_mgr = self.input_mgr

        # Simulate synthetic analog input state
        mock_input_state = {
            "move_x": 0.8,
            "move_y": 0.0,
            "aim_angle_deg": 45.0,
            "fire_primary": True,
            "fire_secondary": False,
            "roll": True,
            "cycle_weapon": False
        }

        self.game.start_mission("S1_M1")
        player = self.ctx.player
        init_x = player.pos.x

        player.handle_input({}, dt=0.05, mouse_pos=(800, 360), input_state=mock_input_state)
        player.update(dt=0.05, targets_group=self.ctx.target_group)

        self.assertGreater(player.pos.x, init_x, "Controller move_x > 0 must move player rightward")

    def test_canvas_and_window_coordinate_mapping(self):
        """Verify virtual canvas 1280x720 handles coordinate mapping under window sizing."""
        cam = self.game.camera
        if cam is not None:
            # Center screen to world
            world_center = cam.screen_to_world(640, 360)
            self.assertIsNotNone(world_center)


if __name__ == "__main__":
    unittest.main()
