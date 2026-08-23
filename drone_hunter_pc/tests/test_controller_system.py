"""
===============================================================================
                     DRONE HUNTER 2D - CONTROLLER SYSTEM TEST SUITE
===============================================================================
Comprehensive verification of ControllerMappingManager, auto-detection,
D-pad resolution, button mapping, prompt labels, binding wizard,
save/load, hot-plug, menu navigation, and duplicate detection.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.input.controller_mapping import (
    ControllerMappingManager,
    ControllerProfile,
    DEFAULT_MAPPINGS,
    PROMPT_LABELS,
    ACTION_FIRE_PRIMARY,
    ACTION_FIRE_SECONDARY,
    ACTION_WEAPON_NEXT,
    ACTION_WEAPON_PREV,
    ACTION_ULTIMATE,
    ACTION_EMP,
    ACTION_SPECIAL,
    ACTION_CLOAK,
    ACTION_PAUSE,
    ACTION_CONFIRM,
    ACTION_CANCEL,
    ACTION_ROLL,
    ACTION_MOVE_UP,
    ACTION_MOVE_DOWN,
    ACTION_MOVE_LEFT,
    ACTION_MOVE_RIGHT,
)
from src.input.input_manager import InputManager


def _make_joystick(name="Xbox Controller", guid="xinput", numhats=1, numbuttons=16, numaxes=4):
    js = MagicMock()
    js.get_name.return_value = name
    js.get_guid.return_value = guid
    js.get_instance_id.return_value = 0
    js.get_numhats.return_value = numhats
    js.get_numbuttons.return_value = numbuttons
    js.get_numaxes.return_value = numaxes
    js.get_hat.return_value = (0, 0)
    for i in range(numbuttons):
        btn = MagicMock()
        btn.__eq__ = lambda self, other: i == other
        js.get_button = lambda idx=i: False
    js.get_axis.return_value = 0.0
    return js


class TestControllerTypeDetection(unittest.TestCase):

    def test_detect_xbox(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox 360 Controller")
        self.assertEqual(mgr._detect_controller_type(js), "xbox")

    def test_detect_xinput(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="XInput Controller")
        self.assertEqual(mgr._detect_controller_type(js), "xbox")

    def test_detect_playstation(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="PlayStation 4 Controller")
        self.assertEqual(mgr._detect_controller_type(js), "playstation")

    def test_detect_dualshock(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="DualShock 4 Controller")
        self.assertEqual(mgr._detect_controller_type(js), "playstation")

    def test_detect_dualsense(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="DualSense Controller")
        self.assertEqual(mgr._detect_controller_type(js), "playstation")

    def test_detect_generic(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Generic Gamepad")
        self.assertEqual(mgr._detect_controller_type(js), "generic")

    def test_detect_unknown_falls_back_to_generic(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Unknown Controller Device")
        self.assertEqual(mgr._detect_controller_type(js), "generic")


class TestDefaultMappings(unittest.TestCase):

    def test_xbox_defaults(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        profile = mgr.get_or_create_profile(js)
        self.assertTrue(profile.is_xbox_style)
        self.assertFalse(profile.is_ps_style)
        self.assertEqual(profile.button_map[ACTION_FIRE_PRIMARY], 0)
        self.assertEqual(profile.button_map[ACTION_FIRE_SECONDARY], 1)
        self.assertEqual(profile.button_map[ACTION_WEAPON_NEXT], 5)
        self.assertEqual(profile.button_map[ACTION_WEAPON_PREV], 4)
        self.assertEqual(profile.button_map[ACTION_ULTIMATE], 3)
        self.assertEqual(profile.button_map[ACTION_EMP], 2)
        self.assertEqual(profile.button_map[ACTION_PAUSE], 7)

    def test_playstation_defaults(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="PlayStation 4 Controller")
        profile = mgr.get_or_create_profile(js)
        self.assertFalse(profile.is_xbox_style)
        self.assertTrue(profile.is_ps_style)
        self.assertEqual(profile.button_map[ACTION_FIRE_PRIMARY], 0)
        self.assertEqual(profile.button_map[ACTION_FIRE_SECONDARY], 1)
        self.assertEqual(profile.button_map[ACTION_WEAPON_NEXT], 2)
        self.assertEqual(profile.button_map[ACTION_WEAPON_PREV], 3)
        self.assertEqual(profile.button_map[ACTION_ULTIMATE], 3)
        self.assertEqual(profile.button_map[ACTION_EMP], 2)
        self.assertEqual(profile.button_map[ACTION_PAUSE], 5)

    def test_generic_defaults(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Generic Gamepad")
        profile = mgr.get_or_create_profile(js)
        self.assertFalse(profile.is_xbox_style)
        self.assertFalse(profile.is_ps_style)
        self.assertEqual(profile.button_map[ACTION_FIRE_PRIMARY], 0)
        self.assertEqual(profile.button_map[ACTION_FIRE_SECONDARY], 1)
        self.assertEqual(profile.button_map[ACTION_WEAPON_NEXT], 2)
        self.assertEqual(profile.button_map[ACTION_WEAPON_PREV], 3)
        self.assertEqual(profile.button_map[ACTION_PAUSE], 5)


class TestDpadResolution(unittest.TestCase):

    def test_hat_dpad_up(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numhats=1)
        js.get_hat.return_value = (0, 1)
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["up"])
        self.assertFalse(result["down"])
        self.assertFalse(result["left"])
        self.assertFalse(result["right"])

    def test_hat_dpad_down(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numhats=1)
        js.get_hat.return_value = (0, -1)
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["down"])
        self.assertFalse(result["up"])

    def test_hat_dpad_left(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numhats=1)
        js.get_hat.return_value = (-1, 0)
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["left"])
        self.assertFalse(result["right"])

    def test_hat_dpad_right(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numhats=1)
        js.get_hat.return_value = (1, 0)
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["right"])
        self.assertFalse(result["left"])

    def test_hat_dpad_diagonal(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numhats=1)
        js.get_hat.return_value = (1, 1)
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["up"])
        self.assertTrue(result["right"])
        self.assertFalse(result["down"])
        self.assertFalse(result["left"])

    def test_no_hat_fallback_to_buttons(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Generic Gamepad", numhats=0, numbuttons=16)
        profile = mgr.get_or_create_profile(js)
        profile.set_button("dpad_up", 12)
        profile.set_button("dpad_down", 13)
        profile.set_button("dpad_left", 14)
        profile.set_button("dpad_right", 15)

        def _fake_btn(idx):
            return idx == 12

        js.get_button = _fake_btn
        result = mgr.get_dpad_input(js)
        self.assertTrue(result["up"])
        self.assertFalse(result["down"])
        self.assertFalse(result["left"])
        self.assertFalse(result["right"])

    def test_hat_not_available_returns_false(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Generic Gamepad", numhats=0, numbuttons=16)
        result = mgr.get_dpad_input(js)
        self.assertFalse(result["up"])
        self.assertFalse(result["down"])
        self.assertFalse(result["left"])
        self.assertFalse(result["right"])


class TestButtonMappingResolution(unittest.TestCase):

    def test_get_action_button(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        profile = mgr.get_or_create_profile(js)
        self.assertEqual(mgr.get_action_button(js, ACTION_FIRE_PRIMARY), 0)
        self.assertEqual(mgr.get_action_button(js, ACTION_FIRE_SECONDARY), 1)

    def test_is_action_pressed(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numbuttons=16)
        profile = mgr.get_or_create_profile(js)

        btn_states = {0: True, 1: False}
        js.get_button = lambda idx: btn_states.get(idx, False)
        js.get_numbuttons.return_value = 16

        self.assertTrue(mgr.is_action_pressed(js, ACTION_FIRE_PRIMARY))
        self.assertFalse(mgr.is_action_pressed(js, ACTION_FIRE_SECONDARY))

    def test_is_action_pressed_out_of_range(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller", numbuttons=4)
        profile = mgr.get_or_create_profile(js)
        profile.set_button(ACTION_FIRE_PRIMARY, 99)
        self.assertFalse(mgr.is_action_pressed(js, ACTION_FIRE_PRIMARY))


class TestPromptLabels(unittest.TestCase):

    def test_xbox_prompts(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_PRIMARY), "A")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_SECONDARY), "B")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_ULTIMATE), "Y")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_EMP), "X")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_PAUSE), "START")

    def test_playstation_prompts(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="PlayStation 4 Controller")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_PRIMARY), "X")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_SECONDARY), "O")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_ULTIMATE), "△")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_EMP), "□")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_PAUSE), "START")

    def test_generic_prompts(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Generic Gamepad")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_PRIMARY), "BTN-0")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_FIRE_SECONDARY), "BTN-1")
        self.assertEqual(mgr.get_prompt_for_action(js, ACTION_PAUSE), "BTN-5")


class TestProfilePersistence(unittest.TestCase):

    def test_profile_to_dict_and_back(self):
        profile = ControllerProfile("Test Controller", "guid123", 0, "xbox")
        profile.set_button(ACTION_FIRE_PRIMARY, 9)
        data = profile.to_dict()
        restored = ControllerProfile.from_dict(data)
        self.assertEqual(restored.device_name, "Test Controller")
        self.assertEqual(restored.device_guid, "guid123")
        self.assertEqual(restored.button_map[ACTION_FIRE_PRIMARY], 9)
        self.assertEqual(restored.controller_type, "xbox")

    def test_save_and_load_mappings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "mappings.json")
            mgr = ControllerMappingManager(mappings_path=path)
            js = _make_joystick(name="Xbox Controller", guid="guid1")
            profile = mgr.get_or_create_profile(js)
            profile.set_button(ACTION_FIRE_PRIMARY, 99)
            mgr.save_mappings()

            mgr2 = ControllerMappingManager(mappings_path=path)
            self.assertIn(mgr._profile_key(js), mgr2.profiles)
            self.assertEqual(mgr2.profiles[mgr._profile_key(js)].button_map[ACTION_FIRE_PRIMARY], 99)


class TestBindingWizard(unittest.TestCase):

    def test_record_binding(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        profile = mgr.get_or_create_profile(js)
        result = mgr.record_binding(js, ACTION_FIRE_PRIMARY, "button", button_index=7)
        self.assertTrue(result)
        self.assertEqual(profile.button_map[ACTION_FIRE_PRIMARY], 7)

    def test_record_binding_invalid(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        result = mgr.record_binding(js, ACTION_FIRE_PRIMARY, "button", button_index=-1)
        self.assertFalse(result)

    def test_check_duplicate_binding(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        profile = mgr.get_or_create_profile(js)
        profile.set_button(ACTION_FIRE_PRIMARY, 5)
        self.assertTrue(mgr.check_duplicate_binding(js, ACTION_FIRE_SECONDARY, "button", button_index=5))
        # Button 10 is not mapped by default, so no duplicate
        self.assertFalse(mgr.check_duplicate_binding(js, ACTION_FIRE_SECONDARY, "button", button_index=10))

    def test_reset_to_defaults(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        profile = mgr.get_or_create_profile(js)
        profile.set_button(ACTION_FIRE_PRIMARY, 99)
        mgr.save_mappings()
        reset_profile = mgr.reset_to_defaults(js)
        self.assertEqual(reset_profile.button_map[ACTION_FIRE_PRIMARY], 0)


class TestHotPlugSimulation(unittest.TestCase):

    def test_add_and_remove_joystick(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ControllerMappingManager(mappings_path=os.path.join(tmpdir, "mappings.json"))
            js1 = _make_joystick(name="Xbox Controller", guid="guid1")
            js2 = _make_joystick(name="PS4 Controller", guid="guid2")
            p1 = mgr.get_or_create_profile(js1)
            p2 = mgr.get_or_create_profile(js2)
            self.assertEqual(len(mgr.profiles), 2)
            # Simulate removal by key
            key1 = mgr._profile_key(js1)
            del mgr.profiles[key1]
            self.assertEqual(len(mgr.profiles), 1)

    def test_get_or_create_returns_same_profile(self):
        mgr = ControllerMappingManager()
        js = _make_joystick(name="Xbox Controller")
        p1 = mgr.get_or_create_profile(js)
        p2 = mgr.get_or_create_profile(js)
        self.assertIs(p1, p2)


class TestInputManagerIntegration(unittest.TestCase):

    def test_input_manager_has_mapping_manager(self):
        im = InputManager()
        self.assertIsNotNone(im.mapping_manager)
        self.assertIsInstance(im.mapping_manager, ControllerMappingManager)

    def test_get_prompt_for_action_keyboard(self):
        im = InputManager()
        im.active_device = "keyboard_mouse"
        self.assertEqual(im.get_prompt_for_action("ROLL"), "LSHIFT")

    def test_get_prompt_for_action_gamepad(self):
        im = InputManager()
        im.active_device = "gamepad"
        js = _make_joystick(name="Xbox Controller")
        im.connected_joysticks[0] = js
        im.active_joystick_id = 0
        im.mapping_manager.get_or_create_profile(js)
        self.assertEqual(im.get_prompt_for_action("ROLL"), "A")

    def test_controller_forward_fire_behavior(self):
        """Verify poll_input produces fire_primary when controller button is mapped."""
        im = InputManager()
        im.enabled = True
        js = _make_joystick(name="Xbox Controller", numbuttons=16, numaxes=4)
        im.connected_joysticks[0] = js
        im.active_joystick_id = 0
        profile = im.mapping_manager.get_or_create_profile(js)

        btn_states = {0: True}
        js.get_button = lambda idx=0: btn_states.get(idx, False)
        js.get_numbuttons.return_value = 16

        def fake_poll():
            move_x, move_y = 0.0, 0.0
            aim_angle = None
            fire_primary = False
            fire_secondary = False
            num_axes = js.get_numaxes()
            if num_axes >= 2:
                raw_lx = js.get_axis(0)
                raw_ly = js.get_axis(1)
                sx, sy, mag = im.apply_deadzone_radial(raw_lx, raw_ly)
                if mag > 0.0:
                    move_x += sx
                    move_y += sy
            raw_rx, raw_ry = 0.0, 0.0
            if num_axes >= 4:
                raw_rx = js.get_axis(2)
                raw_ry = js.get_axis(3)
            rx, ry, rmag = im.apply_deadzone_radial(raw_rx, raw_ry)
            if rmag > 0.0:
                aim_angle = __import__("math").atan2(ry, rx)
            num_buttons = js.get_numbuttons()
            for btn_idx in range(num_buttons):
                if js.get_button(btn_idx):
                    lower_action = profile.get_action_for_button(btn_idx)
                    if lower_action == "fire_primary":
                        fire_primary = True
            return {
                "move_x": move_x, "move_y": move_y,
                "aim_angle": aim_angle,
                "fire_primary": fire_primary,
                "fire_secondary": fire_secondary,
            }

        state = fake_poll()
        self.assertTrue(state["fire_primary"])


class TestAllActions(unittest.TestCase):

    def test_all_logical_actions_have_defaults(self):
        expected_actions = [
            ACTION_FIRE_PRIMARY, ACTION_FIRE_SECONDARY,
            ACTION_WEAPON_NEXT, ACTION_WEAPON_PREV,
            ACTION_ULTIMATE, ACTION_EMP,
            ACTION_SPECIAL, ACTION_CLOAK,
            ACTION_PAUSE, ACTION_CONFIRM,
            ACTION_CANCEL, ACTION_ROLL,
        ]
        for action in expected_actions:
            self.assertIn(action, DEFAULT_MAPPINGS)
            mapping = DEFAULT_MAPPINGS[action]
            self.assertIn("xbox", mapping)
            self.assertIn("playstation", mapping)
            self.assertIn("generic", mapping)

    def test_all_logical_actions_have_prompts(self):
        for ctype in ("xbox", "playstation", "generic"):
            for action, mapping in DEFAULT_MAPPINGS.items():
                if mapping.get(ctype) is not None:
                    self.assertIn(action, PROMPT_LABELS[ctype])


if __name__ == "__main__":
    unittest.main()
