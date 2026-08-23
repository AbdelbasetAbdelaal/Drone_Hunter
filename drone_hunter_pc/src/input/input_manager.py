"""
===============================================================================
                     DRONE HUNTER 2D - INPUT MANAGEMENT SYSTEM
===============================================================================
First-Class Unified Input System for Keyboard/Mouse, Xbox Controllers,
Generic Gamepads, and Joysticks. Converts device inputs into canonical actions
without altering underlying physics or gameplay contracts.
"""

import math
import pygame
from typing import Dict, Tuple, Optional, Any

from src.input.controller_mapping import (
    ControllerMappingManager,
)


# ------------------------------------------------------------------------------
# CANONICAL ACTIONS (backward-compatible, uppercase as used throughout codebase)
# ------------------------------------------------------------------------------
ACTION_MOVE_X = "MOVE_X"
ACTION_MOVE_Y = "MOVE_Y"
ACTION_AIM_ANGLE = "AIM_ANGLE"
ACTION_FIRE_PRIMARY = "FIRE_PRIMARY"
ACTION_FIRE_SECONDARY = "FIRE_SECONDARY"
ACTION_WEAPON_NEXT = "WEAPON_NEXT"
ACTION_WEAPON_PREV = "WEAPON_PREV"
ACTION_ROLL = "ROLL"
ACTION_EMP = "EMP"
ACTION_ULTIMATE = "ULTIMATE"
ACTION_SPECIAL = "SPECIAL"
ACTION_PAUSE = "PAUSE"
ACTION_CLOAK = "CLOAK"
ACTION_CONFIRM = "CONFIRM"
ACTION_CANCEL = "CANCEL"

DEVICE_KEYBOARD_MOUSE = "keyboard_mouse"
DEVICE_GAMEPAD = "gamepad"
DEVICE_JOYSTICK = "joystick"


# ------------------------------------------------------------------------------
# PROMPT LABELS (backward-compatible aliases)
# ------------------------------------------------------------------------------
PROMPT_MAP_KEYBOARD = {
    ACTION_ROLL: "LSHIFT",
    ACTION_EMP: "E",
    ACTION_ULTIMATE: "F",
    ACTION_SPECIAL: "B",
    ACTION_WEAPON_NEXT: "TAB",
    ACTION_WEAPON_PREV: "WHEEL-DN",
    ACTION_FIRE_PRIMARY: "LMB",
    ACTION_FIRE_SECONDARY: "RMB",
    ACTION_PAUSE: "ESC",
    ACTION_CLOAK: "C",
}

PROMPT_MAP_GAMEPAD = {
    ACTION_ROLL: "A",
    ACTION_EMP: "X",
    ACTION_ULTIMATE: "Y",
    ACTION_SPECIAL: "B",
    ACTION_WEAPON_NEXT: "RB",
    ACTION_WEAPON_PREV: "LB",
    ACTION_FIRE_PRIMARY: "RT",
    ACTION_FIRE_SECONDARY: "LT",
    ACTION_PAUSE: "START",
    ACTION_CLOAK: "R3",
}

# Backward-compatible button maps for tests and legacy code
XBOX_BUTTON_MAP = {
    0: ACTION_ROLL,
    1: ACTION_SPECIAL,
    2: ACTION_EMP,
    3: ACTION_ULTIMATE,
    4: ACTION_WEAPON_PREV,
    5: ACTION_WEAPON_NEXT,
    6: ACTION_CANCEL,
    7: ACTION_PAUSE,
    8: ACTION_SPECIAL,
    9: ACTION_CLOAK,
}

GENERIC_BUTTON_MAP = {
    0: ACTION_ROLL,
    1: ACTION_SPECIAL,
    2: ACTION_EMP,
    3: ACTION_ULTIMATE,
    4: ACTION_WEAPON_PREV,
    5: ACTION_WEAPON_NEXT,
    6: ACTION_CANCEL,
    7: ACTION_PAUSE,
}


# ------------------------------------------------------------------------------
# ACTION NAME TRANSLATION (uppercase <-> lowercase)
# ------------------------------------------------------------------------------
_ACTION_UPPER_TO_LOWER = {
    ACTION_FIRE_PRIMARY: "fire_primary",
    ACTION_FIRE_SECONDARY: "fire_secondary",
    ACTION_WEAPON_NEXT: "weapon_next",
    ACTION_WEAPON_PREV: "weapon_prev",
    ACTION_ROLL: "roll",
    ACTION_EMP: "emp",
    ACTION_ULTIMATE: "ultimate",
    ACTION_SPECIAL: "special",
    ACTION_PAUSE: "pause",
    ACTION_CLOAK: "cloak",
    ACTION_CONFIRM: "confirm",
    ACTION_CANCEL: "cancel",
}
_ACTION_LOWER_TO_UPPER = {v: k for k, v in _ACTION_UPPER_TO_LOWER.items()}


# ------------------------------------------------------------------------------
# INPUT MANAGER CLASS
# ------------------------------------------------------------------------------
class InputManager:
    """Centralized input abstraction orchestrating device detection, analog

    filtering, deadzone normalization, rumble feedback, and device-aware prompt

    dispatching.

    """

    def __init__(self, settings_manager=None):
        self.settings = settings_manager

        # Settings defaults
        self.enabled: bool = True
        self.deadzone: float = 0.12
        self.aim_sensitivity: float = 1.0
        self.move_sensitivity: float = 1.0
        self.vibration_enabled: bool = True

        # Active state tracking
        self.active_device: str = DEVICE_KEYBOARD_MOUSE
        self.connected_joysticks: Dict[int, pygame.joystick.Joystick] = {}
        self.active_joystick_id: Optional[int] = None

        # Processed action state for the current frame
        self.move_vector: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.aim_angle: Optional[float] = None
        self.aim_vector: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.actions_pressed: Dict[str, bool] = {}
        self.actions_triggered: Dict[str, bool] = {}

        # Last raw inputs for transition stability
        self._last_mouse_pos: Tuple[int, int] = (0, 0)
        self._trigger_threshold: float = 0.35

        # Controller mapping manager
        self.mapping_manager = ControllerMappingManager()

        # Initialize Pygame Joystick Subsystem safely
        self._init_joysticks()

    def _init_joysticks(self):
        """Safely initializes joystick subsystem and detects connected controllers."""
        try:
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            count = pygame.joystick.get_count()
            for i in range(count):
                self._add_joystick(i)
        except Exception:
            pass

    def _add_joystick(self, device_id: int):
        """Safely instantiates and registers a newly connected joystick."""
        try:
            js = pygame.joystick.Joystick(device_id)
            js.init()
            self.connected_joysticks[device_id] = js
            self.mapping_manager.get_or_create_profile(js)
            if self.active_joystick_id is None:
                self.active_joystick_id = device_id
        except Exception:
            pass

    def _remove_joystick(self, instance_id: int):
        """Safely unregisters a disconnected joystick."""
        target_key = None
        for key, js in list(self.connected_joysticks.items()):
            try:
                if js.get_instance_id() == instance_id or key == instance_id:
                    target_key = key
                    break
            except Exception:
                if key == instance_id:
                    target_key = key
                    break

        if target_key is not None:
            self.connected_joysticks.pop(target_key, None)
            if self.active_joystick_id == target_key:
                if self.connected_joysticks:
                    self.active_joystick_id = next(iter(self.connected_joysticks.keys()))
                else:
                    self.active_joystick_id = None
                    self.active_device = DEVICE_KEYBOARD_MOUSE

    @property
    def active_joystick(self) -> Optional[pygame.joystick.Joystick]:
        """Returns the currently active joystick instance if connected."""
        if self.active_joystick_id is not None and self.active_joystick_id in self.connected_joysticks:
            return self.connected_joysticks[self.active_joystick_id]
        return None

    def apply_deadzone_radial(self, raw_x: float, raw_y: float) -> Tuple[float, float, float]:
        """Applies radial deadzone and non-linear response curve to raw analog stick axes.

        Returns (scaled_x, scaled_y, magnitude).

        """
        mag = math.hypot(raw_x, raw_y)
        if mag < self.deadzone:
            return 0.0, 0.0, 0.0

        # Normalize magnitude beyond deadzone [0.0, 1.0]
        norm_mag = min(1.0, (mag - self.deadzone) / max(0.001, (1.0 - self.deadzone)))
        
        # Smooth non-linear response curve for fine precision at low tilt & full max speed at 100%
        scaled_mag = math.pow(norm_mag, 1.35) * self.move_sensitivity

        scaled_x = (raw_x / mag) * scaled_mag
        scaled_y = (raw_y / mag) * scaled_mag
        return scaled_x, scaled_y, scaled_mag

    def update_settings(self, settings_dict: dict):
        """Updates input settings dynamically from save file or settings menu."""
        if not settings_dict:
            return
        self.enabled = settings_dict.get("controller_enabled", True)
        self.deadzone = max(0.02, min(0.40, float(settings_dict.get("controller_deadzone", 0.12))))
        self.aim_sensitivity = max(0.2, min(3.0, float(settings_dict.get("controller_aim_sensitivity", 1.0))))
        self.move_sensitivity = max(0.2, min(2.0, float(settings_dict.get("controller_move_sensitivity", 1.0))))
        self.vibration_enabled = settings_dict.get("controller_vibration", True)

    def process_events(self, events: list):
        """Processes pygame event queue for hot-plugging, discrete actions, and device priority."""
        self.actions_triggered.clear()

        for event in events:
            # Hot-plugging events
            if event.type == pygame.JOYDEVICEADDED:
                device_id = getattr(event, "device_index", getattr(event, "which", 0))
                self._add_joystick(device_id)
            elif event.type == pygame.JOYDEVICEREMOVED:
                instance_id = getattr(event, "instance_id", getattr(event, "which", 0))
                self._remove_joystick(instance_id)

            # Detect mouse movement for device switching
            elif event.type == pygame.MOUSEMOTION:
                rel = event.rel
                if abs(rel[0]) > 2 or abs(rel[1]) > 2:
                    self.active_device = DEVICE_KEYBOARD_MOUSE

            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.active_device = DEVICE_KEYBOARD_MOUSE

            # Controller Button Down
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.enabled:
                    self.active_device = DEVICE_GAMEPAD
                    js = self.active_joystick
                    if js:
                        btn = event.button
                        profile = self.mapping_manager.get_profile_for_joystick(js)
                        if profile:
                            lower_action = profile.button_map.get(btn)
                            if lower_action:
                                upper_action = _ACTION_LOWER_TO_UPPER.get(lower_action, lower_action)
                                self.actions_triggered[upper_action] = True

            # Controller Axis Motion
            elif event.type == pygame.JOYAXISMOTION:
                if self.enabled and abs(event.value) > self.deadzone + 0.05:
                    self.active_device = DEVICE_GAMEPAD

    def poll_input(self, player_pos: Tuple[float, float], get_canvas_mouse_pos_func, world_mouse_pos: Optional[Tuple[float, float]] = None) -> dict:
        """Polls current hardware state (Keyboard, Mouse, Gamepad, Joystick)

        and produces a unified, normalized action state object for gameplay.

        """
        # Reset state frame buffers
        move_x, move_y = 0.0, 0.0
        aim_angle = None
        fire_primary = False
        fire_secondary = False

        # 1. KEYBOARD & MOUSE POLLING
        keys = pygame.key.get_pressed()
        m_buttons = pygame.mouse.get_pressed()
        canvas_m_pos = get_canvas_mouse_pos_func()

        kb_move_x = 0.0
        kb_move_y = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]: kb_move_y -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: kb_move_y += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: kb_move_x -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: kb_move_x += 1.0

        if kb_move_x != 0.0 or kb_move_y != 0.0:
            self.active_device = DEVICE_KEYBOARD_MOUSE
            move_x += kb_move_x
            move_y += kb_move_y

        if m_buttons[0]:
            fire_primary = True
            self.active_device = DEVICE_KEYBOARD_MOUSE
        if m_buttons[2]:
            fire_secondary = True
            self.active_device = DEVICE_KEYBOARD_MOUSE

        # Mouse Aim Angle - use world coordinates if available for correct 360-degree aiming
        if self.active_device == DEVICE_KEYBOARD_MOUSE and world_mouse_pos:
            dx = world_mouse_pos[0] - player_pos[0]
            dy = world_mouse_pos[1] - player_pos[1]
            aim_angle = math.atan2(dy, dx)
        elif self.active_device == DEVICE_KEYBOARD_MOUSE and canvas_m_pos:
            dx = canvas_m_pos[0] - player_pos[0]
            dy = canvas_m_pos[1] - player_pos[1]
            aim_angle = math.atan2(dy, dx)

        # 2. CONTROLLER / GAMEPAD POLLING
        js = self.active_joystick
        if self.enabled and js:
            try:
                profile = self.mapping_manager.get_profile_for_joystick(js)
                num_axes = js.get_numaxes()

                # Left Stick (Movement) - Axes 0 & 1
                if num_axes >= 2:
                    raw_lx = js.get_axis(0)
                    raw_ly = js.get_axis(1)
                    sx, sy, mag = self.apply_deadzone_radial(raw_lx, raw_ly)
                    if mag > 0.0:
                        self.active_device = DEVICE_GAMEPAD
                        move_x += sx
                        move_y += sy

                # D-pad override if active
                dpad = self.mapping_manager.get_dpad_input(js)
                if any(dpad.values()):
                    self.active_device = DEVICE_GAMEPAD
                    if dpad["up"]: move_y -= 1.0
                    if dpad["down"]: move_y += 1.0
                    if dpad["left"]: move_x -= 1.0
                    if dpad["right"]: move_x += 1.0

                # Right Stick (Aiming) - Axes 2/3 or 3/4 depending on driver
                raw_rx, raw_ry = 0.0, 0.0
                if num_axes >= 4:
                    raw_rx = js.get_axis(2)
                    raw_ry = js.get_axis(3)
                    # Handle some controllers where Right Stick Y is axis 4 and axis 2 is LT
                    if num_axes >= 5 and abs(raw_ry) < 0.05 and abs(js.get_axis(4)) > 0.1:
                        raw_ry = js.get_axis(4)

                rx, ry, rmag = self.apply_deadzone_radial(raw_rx, raw_ry)
                if rmag > 0.0:
                    self.active_device = DEVICE_GAMEPAD
                    aim_angle = math.atan2(ry, rx)

                # Triggers (RT / LT) - Usually Axes 4 & 5 or 2 & 5
                if num_axes >= 6:
                    rt_val = js.get_axis(5)
                    lt_val = js.get_axis(4)
                    if rt_val > self._trigger_threshold:
                        fire_primary = True
                        self.active_device = DEVICE_GAMEPAD
                    if lt_val > self._trigger_threshold:
                        fire_secondary = True
                        self.active_device = DEVICE_GAMEPAD
                elif num_axes >= 3:
                    # Triggers mapped to Axis 2 in standard XInput
                    trig_val = js.get_axis(2)
                    if trig_val < -self._trigger_threshold:
                        fire_primary = True
                        self.active_device = DEVICE_GAMEPAD
                    elif trig_val > self._trigger_threshold:
                        fire_secondary = True
                        self.active_device = DEVICE_GAMEPAD

                # Poll Buttons for continuous actions via mapping manager
                if profile:
                    num_buttons = js.get_numbuttons()
                    for btn_idx in range(num_buttons):
                        if js.get_button(btn_idx):
                            lower_action = profile.get_action_for_button(btn_idx)
                            if lower_action:
                                upper_action = _ACTION_LOWER_TO_UPPER.get(lower_action, lower_action)
                                if upper_action == ACTION_FIRE_PRIMARY:
                                    fire_primary = True
                                elif upper_action == ACTION_FIRE_SECONDARY:
                                    fire_secondary = True

            except Exception:
                pass

        # 3. COMBINE & NORMALIZE MOVEMENT VECTOR
        move_vec = pygame.Vector2(move_x, move_y)
        if move_vec.length_squared() > 1.0:
            move_vec = move_vec.normalize()

        self.move_vector = move_vec
        self.aim_angle = aim_angle

        # Assemble unified action state
        state = {
            "move_x": move_vec.x,
            "move_y": move_vec.y,
            "aim_angle": aim_angle,
            "fire_primary": fire_primary,
            "fire_secondary": fire_secondary,
            "active_device": self.active_device,
            "actions_triggered": self.actions_triggered.copy(),
        }
        return state

    def get_prompt_for_action(self, action_name: str) -> str:
        """Returns the appropriate UI text label for an action depending on active device."""
        lower_name = _ACTION_UPPER_TO_LOWER.get(action_name, action_name)
        if self.active_device in (DEVICE_GAMEPAD, DEVICE_JOYSTICK):
            js = self.active_joystick
            if js:
                prompt = self.mapping_manager.get_prompt_for_action(js, lower_name)
                if prompt and prompt != lower_name and not prompt.startswith("BTN-"):
                    return prompt
            return PROMPT_MAP_GAMEPAD.get(action_name, action_name)
        return PROMPT_MAP_KEYBOARD.get(action_name, action_name)

    def trigger_rumble(self, low_frequency: float = 0.5, high_frequency: float = 0.5, duration_ms: int = 150):
        """Safely triggers short, bounded vibration on active controller if supported."""
        if not self.vibration_enabled or not self.enabled:
            return
        js = self.active_joystick
        if not js:
            return
        try:
            if hasattr(js, "rumble"):
                js.rumble(float(low_frequency), float(high_frequency), int(duration_ms))
        except Exception:
            pass

    def stop_rumble(self):
        """Safely stops any active vibration."""
        js = self.active_joystick
        if not js:
            return
        try:
            if hasattr(js, "stop_rumble"):
                js.stop_rumble()
            elif hasattr(js, "rumble"):
                js.rumble(0.0, 0.0, 0)
        except Exception:
            pass
