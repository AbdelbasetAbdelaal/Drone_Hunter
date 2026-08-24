
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pytest
import pygame
from src.ui.hangar import draw_hangar_shop_ui
from src.ui.menus import (draw_mission_briefing, draw_settings_menu_ui, draw_controller_test_ui, draw_controller_binding_ui)
from src.input.input_manager import InputManager, DEVICE_GAMEPAD, DEVICE_KEYBOARD_MOUSE
from src.input.controller_mapping import ControllerMappingManager
from src.entities.player import Player
from src.data.mission_data import get_mission_data


class TestUIUXPolishPass:
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

    def test_hangar_layout(self):
        for res in ((1280, 720), (1366, 768), (1920, 1080)):
            canvas = pygame.Surface(res, pygame.SRCALPHA)
            p = Player((200, 200))
            rects = draw_hangar_shop_ui(
                canvas, scrap=5000, current_sector_idx=1,
                upgrade_levels={'hull': 2, 'energy': 3, 'weapon': 1, 'mobility': 1},
                player=p
            )
            assert 'back' in rects
            assert 'skin' in rects
            assert 'settings' in rects
            assert 'exit' in rects
            assert len(rects['upgrades']) == 4
            for k in ('back', 'skin', 'settings', 'exit'):
                r = rects[k]
                assert r.bottom <= res[1]
                assert r.top >= 0
                assert r.left >= 0
                assert r.right <= res[0]

    def test_hangar_focus_navigation(self):
        canvas = pygame.Surface((1280, 720), pygame.SRCALPHA)
        p = Player((200, 200))
        for sel in range(8):
            rects = draw_hangar_shop_ui(
                canvas, scrap=5000, current_sector_idx=1,
                upgrade_levels={'hull': 1, 'energy': 1, 'weapon': 1, 'mobility': 1},
                player=p, selected_index=sel
            )
            assert rects is not None

    def test_controller_test_screen(self):
        canvas = pygame.Surface((1280, 720), pygame.SRCALPHA)
        mapping_mgr = ControllerMappingManager()
        rects = draw_controller_test_ui(canvas, joystick=None, mapping_manager=mapping_mgr)
        assert 'back' in rects

    def test_binding_wizard_layout(self):
        for res in ((1280, 720), (1366, 768), (1920, 1080)):
            canvas = pygame.Surface(res, pygame.SRCALPHA)
            mapping_mgr = ControllerMappingManager()
            rects = draw_controller_binding_ui(canvas, mapping_mgr, waiting=False)
            assert 'back' in rects
            assert 'reset' in rects
            assert 'action_rows' in rects
            assert len(rects['action_rows']) >= 8
            assert rects['back'].bottom <= res[1]
            assert rects['reset'].bottom <= res[1]

            # Test waiting state (pulsing banner)
            rects_waiting = draw_controller_binding_ui(
                canvas, mapping_mgr, binding_action="fire_primary", waiting=True
            )
            assert 'back' in rects_waiting
            assert 'reset' in rects_waiting

    def test_settings_navigation(self):
        for res in ((1280, 720), (1920, 1080)):
            canvas = pygame.Surface(res)
            rects = draw_settings_menu_ui(
                canvas, difficulty_mode=1, show_crt=False,
                sound_enabled=True, selected_index=0
            )
            assert 'fullscreen' in rects
            assert 'crt' in rects
            assert 'sfx' in rects
            assert 'diff' in rects
            assert 'controller' in rects
            assert 'back' in rects
            for k, r in rects.items():
                assert r.bottom <= res[1]
                assert r.top >= 0

    def test_mission_briefing_layout(self):
        for res in ((1280, 720), (1366, 768), (1920, 1080)):
            canvas = pygame.Surface(res, pygame.SRCALPHA)
            m_data = get_mission_data('S1_M1_ALT')
            rects = draw_mission_briefing(canvas, m_data, scrap=1200)
            assert 'back' in rects
            assert 'start' in rects
            assert 'exit' in rects
            assert rects['back'].bottom <= res[1]
            assert rects['start'].bottom <= res[1]
            assert rects['exit'].bottom <= res[1]

    def test_controller_prompts(self):
        im = InputManager()
        im.active_device = DEVICE_GAMEPAD
        assert len(im.get_prompt_for_action("ROLL")) > 0
        im.active_device = DEVICE_KEYBOARD_MOUSE
        assert im.get_prompt_for_action("ROLL") == "LSHIFT"

    def test_no_ui_element_overlap(self):
        canvas = pygame.Surface((1280, 720))
        p = Player((200, 200))
        rects = draw_hangar_shop_ui(
            canvas, scrap=5000, current_sector_idx=1,
            upgrade_levels={'hull': 1, 'energy': 1, 'weapon': 1, 'mobility': 1},
            player=p
        )
        f_btns = [rects['back'], rects['skin'], rects['settings'], rects['exit']]
        for i in range(len(f_btns)):
            for j in range(i + 1, len(f_btns)):
                assert not f_btns[i].colliderect(f_btns[j])
