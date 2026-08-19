import os
import unittest
import pygame

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

    def test_sprite_manager_player_states_loaded(self):
        for state in ['idle', 'move', 'fire', 'hit', 'destroy', 'bank_left', 'bank_right']:
            surf = self.sm.get_player_sprite(state=state, skin_idx=0, target_size=(68, 58))
            self.assertIsNotNone(surf)
            self.assertEqual(surf.get_size(), (68, 58))

    def test_sprite_manager_player_shadow(self):
        shadow = self.sm.get_player_shadow(target_size=(64, 54))
        self.assertIsNotNone(shadow)
        self.assertEqual(shadow.get_size(), (64, 54))

    def test_sprite_manager_skin_variations(self):
        for s_idx in range(4):
            surf = self.sm.get_player_sprite(state='idle', skin_idx=s_idx, target_size=(68, 58))
            self.assertIsNotNone(surf)
            self.assertEqual(surf.get_size(), (68, 58))

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

if __name__ == '__main__':
    unittest.main()