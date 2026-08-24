"""
===============================================================================
                     DRONE HUNTER 2D - INPUT MANAGEMENT SYSTEM
===============================================================================
First-Class Unified Input System for Keyboard/Mouse, Xbox Controllers,
Generic Gamepads, and Joysticks. Converts device inputs into canonical actions
without altering underlying physics or gameplay contracts.
"""

import math
import logging
import pygame
from typing import Dict, Tuple, Optional, Any

from src.input.controller_mapping import (
    ControllerMappingManager,
)

logger = logging.getLogger(__name__)

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
ACTION_FULLSCREEN = "FULLSCREEN"
ACTION_CLOAK = "CLOAK"
ACTION_CONFIRM = "CONFIRM"
ACTION_CANCEL = "CANCEL"
ACTION_SECTOR_MAP = "SECTOR_MAP"
ACTION_HANGAR_BAY = "HANGAR_BAY"
ACTION_FRONT_TOP = "FRONT_TOP"
ACTION_FRONT_BOTTOM = "FRONT_BOTTOM"
ACTION_CYCLE_CLASS = "CYCLE_CLASS"

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
    ACTION_CONFIRM: "ENTER",
    ACTION_CANCEL: "ESC",
    ACTION_SECTOR_MAP: "M",
    ACTION_HANGAR_BAY: "H",
    ACTION_FRONT_TOP: "TAB",
    ACTION_FRONT_BOTTOM: "C",
    ACTION_CYCLE_CLASS: "V",
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
    ACTION_FULLSCREEN: "START (HOLD)",
    ACTION_CLOAK: "LB",
    ACTION_CONFIRM: "A",
    ACTION_CANCEL: "B",
    ACTION_SECTOR_MAP: "BACK",
    ACTION_HANGAR_BAY: "BACK",
    ACTION_FRONT_TOP: "RB",
    ACTION_FRONT_BOTTOM: "LB",
    ACTION_CYCLE_CLASS: "LB (HOLD)",
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

PROMPT_MAP_JOYSTICK = PROMPT_MAP_GAMEPAD

# ------------------------------------------------------------------------------
# INTERNAL NORMALIZED ACTION STRING MAPS
# ------------------------------------------------------------------------------
_ACTION_UPPER_TO_LOWER = {
    ACTION_FIRE_PRIMARY: "fire_primary",
    ACTION_FIRE_SECONDARY: "fire_secondary",
    ACTION_FRONT_TOP: "front_top",
    ACTION_FRONT_BOTTOM: "front_bottom",
    ACTION_WEAPON_NEXT: "weapon_next",
    ACTION_WEAPON_PREV: "weapon_prev",
    ACTION_ROLL: "roll",
    ACTION_EMP: "emp",
    ACTION_ULTIMATE: "ultimate",
    ACTION_SPECIAL: "special",
    ACTION_PAUSE: "pause",
    ACTION_FULLSCREEN: "fullscreen",
    ACTION_CLOAK: "cloak",
    ACTION_CYCLE_CLASS: "cycle_class",
    ACTION_CONFIRM: "confirm",
    ACTION_CANCEL: "cancel",
    ACTION_SECTOR_MAP: "sector_map",
    ACTION_HANGAR_BAY: "hangar_bay",
}
_ACTION_LOWER_TO_UPPER = {v: k for k, v in _ACTION_UPPER_TO_LOWER.items()}


# ------------------------------------------------------------------------------
# INPUT CONTEXTS (Canonical UI & Gameplay Semantic Resolution)
# ------------------------------------------------------------------------------
class InputContext:
    GAMEPLAY = "GAMEPLAY"
    MAIN_MENU = "MAIN_MENU"
    MISSION_SELECT = "MISSION_SELECT"
    DRONE_SELECT = "DRONE_SELECT"
    HANGAR = "HANGAR"
    WEAPON_MENU = "WEAPON_MENU"
    SETTINGS = "SETTINGS"
    PAUSE = "PAUSE"
    MAP = "MAP"
    MISSION_COMPLETE = "MISSION_COMPLETE"
    MISSION_FAILED = "MISSION_FAILED"


# ------------------------------------------------------------------------------
# INPUT MANAGER CLASS
# ------------------------------------------------------------------------------
class InputManager:
    """Centralized input abstraction orchestrating device detection, analog
    filtering, deadzone normalization, rumble feedback, device-aware prompt
    dispatching, and contextual semantic action resolution.
    """

    def __init__(self, settings_manager=None):
        self.settings = settings_manager

        # Settings defaults
        self.enabled: bool = True
        self.deadzone: float = 0.12
        self.aim_sensitivity: float = 1.0
        self.move_sensitivity: float = 1.0
        self.vibration_enabled: bool = True

        # Current UI/Gameplay Context
        self.context: str = InputContext.GAMEPLAY

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
        # One-shot keyboard directions for menu navigation.  Kept separate
        # from movement so WASD can retain its gameplay meaning.
        self.navigation_triggered: Dict[str, bool] = {}

        # Last raw inputs for transition stability
        self._last_mouse_pos: Tuple[int, int] = (0, 0)
        self._trigger_threshold: float = 0.35

        # Configurable Hold Thresholds (in seconds)
        self.front_hold_threshold: float = 0.40
        self.start_hold_threshold: float = 1.00

        # Press/Hold tracking states
        self._start_hold_time: float = 0.0
        self._start_fullscreen_fired: bool = False

        self._front_top_hold_time: float = 0.0
        self._front_top_fired: bool = False

        self._front_bottom_hold_time: float = 0.0
        self._front_bottom_fired: bool = False

        # Controller mapping manager
        self.mapping_manager = ControllerMappingManager()

        # Initialize Pygame Joystick Subsystem safely
        self._init_joysticks()

    def set_context(self, context: str):
        """Sets current gameplay/UI context for contextual action resolution."""
        self.context = context

    def _init_joysticks(self):
        """Safely initializes joystick subsystem and detects connected controllers."""
        try:
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            count = pygame.joystick.get_count()
            for i in range(count):
                self._add_joystick(i)
        except Exception as e:
            logger.warning(f"Error initializing joystick subsystem: {e}")

    def _add_joystick(self, device_index: int):
        """Initializes and registers a connected joystick device."""
        try:
            js = pygame.joystick.Joystick(device_index)
            # Check if deprecated init needed for compatibility
            if hasattr(js, "init"):
                try:
                    js.init()
                except Exception:
                    pass
            instance_id = js.get_instance_id()
            self.connected_joysticks[instance_id] = js
            if self.active_joystick_id is None:
                self.active_joystick_id = instance_id
                logger.info(f"[INPUT] Active controller connected: {js.get_name()} (Instance {instance_id})")
        except Exception as e:
            logger.warning(f"Failed to add joystick device index {device_index}: {e}")

    def _remove_joystick(self, instance_id: int):
        """Removes a disconnected joystick and updates active controller device."""
        if instance_id in self.connected_joysticks:
            del self.connected_joysticks[instance_id]
            logger.info(f"[INPUT] Controller disconnected (Instance {instance_id})")
            if self.active_joystick_id == instance_id:
                if self.connected_joysticks:
                    self.active_joystick_id = next(iter(self.connected_joysticks.keys()))
                else:
                    self.active_joystick_id = None
                    self.active_device = DEVICE_KEYBOARD_MOUSE

    @property
    def active_joystick(self) -> Optional[pygame.joystick.Joystick]:
        """Returns the currently active pygame Joystick instance or None."""
        if self.active_joystick_id is not None:
            return self.connected_joysticks.get(self.active_joystick_id)
        return None

    def trigger_rumble(self, low_freq: float = 0.5, high_freq: float = 0.5, duration_ms: int = 150):
        """Triggers haptic vibration rumble feedback on the active controller if supported."""
        if not self.enabled or not self.vibration_enabled:
            return
        js = self.active_joystick
        if js and hasattr(js, "rumble"):
            try:
                js.rumble(low_freq, high_freq, duration_ms)
            except Exception:
                pass

    def apply_deadzone_radial(self, raw_x: float, raw_y: float) -> Tuple[float, float, float]:
        """Applies radial deadzone normalization with smooth remapped magnitude [0, 1]."""
        vec = pygame.Vector2(raw_x, raw_y)
        mag = vec.length()
        if mag <= self.deadzone:
            return 0.0, 0.0, 0.0
        # Remap [deadzone, 1.0] -> [0.0, 1.0]
        scaled_mag = min(1.0, (mag - self.deadzone) / (1.0 - self.deadzone))
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

    def process_events(self, events: list, dt: float = 0.016):
        """Processes pygame event queue for hot-plugging, discrete actions, and device priority."""
        self.actions_triggered.clear()
        self.navigation_triggered.clear()

        front_top_up = False
        front_bottom_up = False
        start_btn_up = False

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

            elif event.type == pygame.KEYDOWN:
                self.active_device = DEVICE_KEYBOARD_MOUSE

                # Gameplay shortcuts are edge-triggered actions. Continuous
                # actions such as movement and primary fire are handled by
                # ``poll_input`` so holding the key remains responsive.
                if self.context == InputContext.GAMEPLAY:
                    keyboard_actions = {
                        pygame.K_LSHIFT: ACTION_ROLL,
                        pygame.K_RSHIFT: ACTION_ROLL,
                        pygame.K_e: ACTION_EMP,
                        pygame.K_f: ACTION_ULTIMATE,
                        pygame.K_q: ACTION_ULTIMATE,
                        pygame.K_TAB: ACTION_WEAPON_NEXT,
                        pygame.K_b: ACTION_SPECIAL,
                        pygame.K_c: ACTION_CLOAK,
                        pygame.K_k: ACTION_CLOAK,
                        pygame.K_SPACE: ACTION_FIRE_PRIMARY,
                        pygame.K_ESCAPE: ACTION_PAUSE,
                        pygame.K_p: ACTION_PAUSE,
                    }
                    action = keyboard_actions.get(event.key)
                    if action:
                        self.actions_triggered[action] = True
                else:
                    navigation_keys = {
                        pygame.K_UP: "up", pygame.K_w: "up",
                        pygame.K_DOWN: "down", pygame.K_s: "down",
                        pygame.K_LEFT: "left", pygame.K_a: "left",
                        pygame.K_RIGHT: "right", pygame.K_d: "right",
                    }
                    direction = navigation_keys.get(event.key)
                    if direction:
                        self.navigation_triggered[direction] = True

                    menu_actions = {
                        pygame.K_RETURN: ACTION_CONFIRM,
                        pygame.K_SPACE: ACTION_CONFIRM,
                        pygame.K_ESCAPE: ACTION_CANCEL,
                        pygame.K_BACKSPACE: ACTION_CANCEL,
                        pygame.K_b: ACTION_CANCEL,
                        pygame.K_p: ACTION_PAUSE,
                        pygame.K_h: ACTION_HANGAR_BAY,
                    }
                    action = menu_actions.get(event.key)
                    if action:
                        self.actions_triggered[action] = True
                    if self.context == InputContext.HANGAR and event.key == pygame.K_c:
                        self.actions_triggered[ACTION_CYCLE_CLASS] = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.active_device = DEVICE_KEYBOARD_MOUSE
                if self.context == InputContext.GAMEPLAY:
                    if event.button == 4:
                        self.actions_triggered[ACTION_WEAPON_NEXT] = True
                    elif event.button == 5:
                        self.actions_triggered[ACTION_WEAPON_PREV] = True

            elif event.type == pygame.MOUSEWHEEL:
                self.active_device = DEVICE_KEYBOARD_MOUSE
                if self.context == InputContext.GAMEPLAY:
                    if event.y > 0:
                        self.actions_triggered[ACTION_WEAPON_NEXT] = True
                    elif event.y < 0:
                        self.actions_triggered[ACTION_WEAPON_PREV] = True

            # Controller Button Down
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.enabled:
                    self.active_device = DEVICE_GAMEPAD
                    js = self.active_joystick
                    if js:
                        btn = event.button
                        profile = self.mapping_manager.get_profile_for_joystick(js)
                        if profile:
                            controller_type = getattr(profile, "controller_type", "generic")
                            fire_btn = profile.button_map.get("fire_primary", -1)
                            confirm_btn = profile.button_map.get("confirm", -1)

                            # Primary fire and menu confirmation are distinct.
                            # On Xbox, RT is an axis and A is exclusively Roll.
                            if self.context == InputContext.GAMEPLAY and btn == fire_btn and fire_btn >= 0:
                                self.actions_triggered[ACTION_FIRE_PRIMARY] = True
                            elif self.context != InputContext.GAMEPLAY and btn == confirm_btn and confirm_btn >= 0:
                                self.actions_triggered[ACTION_CONFIRM] = True

                            # Xbox bumpers are immediate Next/Previous actions;
                            # the PS2-style tap/hold handling below remains for
                            # generic controllers with paired front buttons.
                            elif self.context == InputContext.GAMEPLAY and controller_type == "xbox" and btn == profile.button_map.get("weapon_next", -1):
                                self.actions_triggered[ACTION_WEAPON_NEXT] = True
                            elif self.context == InputContext.GAMEPLAY and controller_type == "xbox" and btn == profile.button_map.get("weapon_prev", -1):
                                self.actions_triggered[ACTION_WEAPON_PREV] = True
                            elif self.context == InputContext.GAMEPLAY and controller_type == "xbox" and btn == profile.button_map.get("cloak", -1):
                                self.actions_triggered[ACTION_CLOAK] = True

                            # 2. CIRCLE: EMP in GAMEPLAY, Cancel in UI
                            elif btn in (profile.button_map.get("emp", 1), profile.button_map.get("cancel", 1)):
                                if self.context == InputContext.GAMEPLAY:
                                    self.actions_triggered[ACTION_EMP] = True
                                else:
                                    self.actions_triggered[ACTION_CANCEL] = True

                            # 3. TRIANGLE: Ultimate/Overdrive in GAMEPLAY
                            elif btn == profile.button_map.get("ultimate", 0):
                                if self.context == InputContext.GAMEPLAY:
                                    self.actions_triggered[ACTION_ULTIMATE] = True

                            # 4. SQUARE: Roll in GAMEPLAY
                            elif btn == profile.button_map.get("roll", 3):
                                if self.context == InputContext.GAMEPLAY:
                                    self.actions_triggered[ACTION_ROLL] = True

                            # 5. SELECT: Sector Map in GAMEPLAY, Hangar in Hangar-relevant contexts
                            elif btn in (profile.button_map.get("sector_map", 8), profile.button_map.get("hangar_bay", 8)):
                                if self.context == InputContext.GAMEPLAY:
                                    self.actions_triggered[ACTION_SECTOR_MAP] = True
                                elif self.context in (InputContext.HANGAR, InputContext.MAIN_MENU, InputContext.DRONE_SELECT):
                                    self.actions_triggered[ACTION_HANGAR_BAY] = True
                                else:
                                    self.actions_triggered[ACTION_SECTOR_MAP] = True

            elif event.type == pygame.JOYBUTTONUP:
                if self.enabled and self.active_joystick:
                    btn = event.button
                    profile = self.mapping_manager.get_profile_for_joystick(self.active_joystick)
                    if profile and getattr(profile, "controller_type", "generic") != "xbox":
                        # Normalize physical button pairs:
                        # Upper front buttons (Buttons 4 & 5) -> FRONT_TOP
                        if btn in (4, 5) or btn == profile.button_map.get("front_top", 5) or btn == profile.button_map.get("weapon_next", 5):
                            front_top_up = True
                        # Lower front buttons (Buttons 6 & 7) -> FRONT_BOTTOM
                        elif btn in (6, 7) or btn == profile.button_map.get("front_bottom", 4) or btn == profile.button_map.get("cloak", 4):
                            front_bottom_up = True
                        elif btn == profile.button_map.get("pause", 9):
                            start_btn_up = True

            # Controller Axis Motion
            elif event.type == pygame.JOYAXISMOTION:
                if self.enabled and abs(event.value) > self.deadzone + 0.05:
                    self.active_device = DEVICE_GAMEPAD

        # Process Hold vs Tap logic for FRONT_TOP, FRONT_BOTTOM, and START
        if self.enabled and self.active_joystick:
            js = self.active_joystick
            profile = self.mapping_manager.get_profile_for_joystick(js)
            if profile and getattr(profile, "controller_type", "generic") != "xbox":
                num_buttons = js.get_numbuttons()
                def _is_pressed(btn_idx):
                    if 0 <= btn_idx < num_buttons:
                        try:
                            return bool(js.get_button(btn_idx))
                        except Exception:
                            return False
                    return False

                # 1. FRONT_TOP (Upper pair: physical buttons 4 or 5)
                # Short press -> WEAPON_NEXT; Hold >= 0.4s -> WEAPON_PREV (Strictly mutually exclusive)
                is_ft_pressed = _is_pressed(4) or _is_pressed(5) or _is_pressed(profile.button_map.get("front_top", 5)) or _is_pressed(profile.button_map.get("weapon_next", 5))
                if is_ft_pressed:
                    self._front_top_hold_time += dt
                    if self._front_top_hold_time >= self.front_hold_threshold and not self._front_top_fired:
                        self.actions_triggered[ACTION_WEAPON_PREV] = True
                        self._front_top_fired = True
                else:
                    if front_top_up and not self._front_top_fired and self._front_top_hold_time < self.front_hold_threshold:
                        self.actions_triggered[ACTION_WEAPON_NEXT] = True
                        self.actions_triggered[ACTION_FRONT_TOP] = True
                    self._front_top_hold_time = 0.0
                    self._front_top_fired = False

                # 2. FRONT_BOTTOM (Lower pair: physical buttons 6 or 7)
                # Short press activates cloak in gameplay; a held press cycles drone class in the hangar.
                is_fb_pressed = _is_pressed(6) or _is_pressed(7) or _is_pressed(profile.button_map.get("front_bottom", 4)) or _is_pressed(profile.button_map.get("cloak", 4))
                if is_ft_pressed and profile.button_map.get("front_bottom") in (4, 5):
                    is_fb_pressed = False

                if is_fb_pressed:
                    self._front_bottom_hold_time += dt
                    if self._front_bottom_hold_time >= self.front_hold_threshold and not self._front_bottom_fired:
                        if self.context in (InputContext.HANGAR, InputContext.DRONE_SELECT):
                            self.actions_triggered[ACTION_CYCLE_CLASS] = True
                            self._front_bottom_fired = True
                else:
                    if front_bottom_up and not self._front_bottom_fired and self._front_bottom_hold_time < self.front_hold_threshold:
                        if self.context == InputContext.GAMEPLAY:
                            self.actions_triggered[ACTION_CLOAK] = True
                        else:
                            self.actions_triggered[ACTION_FRONT_BOTTOM] = True
                    self._front_bottom_hold_time = 0.0
                    self._front_bottom_fired = False

                # 3. START (Pause on short press / Fullscreen on hold >= 1.0s)
                pause_btn = profile.button_map.get("pause", 9)
                is_start_pressed = _is_pressed(pause_btn)
                if is_start_pressed:
                    self._start_hold_time += dt
                    if self._start_hold_time >= self.start_hold_threshold and not self._start_fullscreen_fired:
                        self.actions_triggered[ACTION_FULLSCREEN] = True
                        self._start_fullscreen_fired = True
                else:
                    if start_btn_up and not self._start_fullscreen_fired and self._start_hold_time < self.start_hold_threshold:
                        self.actions_triggered[ACTION_PAUSE] = True
                    self._start_hold_time = 0.0
                    self._start_fullscreen_fired = False

    def poll_input(self, player_pos: Tuple[float, float], get_canvas_mouse_pos_func, world_mouse_pos: Optional[Tuple[float, float]] = None) -> dict:
        """Polls current hardware state (Keyboard, Mouse, Gamepad, Joystick)

        and produces a unified, normalized action state object for gameplay.

        """
        # Reset state frame buffers
        move_x, move_y = 0.0, 0.0
        aim_angle = None
        # Include edge-triggered primary fire so a short Spacebar tap is not
        # lost between SDL event processing and this hardware polling pass.
        fire_primary = self.actions_triggered.get(ACTION_FIRE_PRIMARY, False)
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

        if m_buttons[0] or keys[pygame.K_SPACE]:
            fire_primary = True
            self.active_device = DEVICE_KEYBOARD_MOUSE
        if m_buttons[2]:
            fire_secondary = True
            self.active_device = DEVICE_KEYBOARD_MOUSE

        # Mouse Aim Angle - use world coordinates if available for correct 360-degree aiming
        if world_mouse_pos:
            dx = world_mouse_pos[0] - player_pos[0]
            dy = world_mouse_pos[1] - player_pos[1]
            aim_angle = math.atan2(dy, dx)
        elif canvas_m_pos:
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
                sx, sy = 0.0, 0.0
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
                    dx = 0.0
                    dy = 0.0
                    if dpad["up"]: dy -= 1.0
                    if dpad["down"]: dy += 1.0
                    if dpad["left"]: dx -= 1.0
                    if dpad["right"]: dx += 1.0
                    if dx != 0.0 or dy != 0.0:
                        move_x = dx
                        move_y = dy

                # Clamp movement to unit circle
                move_x = max(-1.0, min(1.0, move_x))
                move_y = max(-1.0, min(1.0, move_y))

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
                elif self.active_device == DEVICE_GAMEPAD and (abs(sx) > 0.1 or abs(sy) > 0.1):
                    # Face direction of flight on 2-axis / D-pad controllers
                    aim_angle = math.atan2(sy, sx)

                # Triggers (RT / LT) - Usually Axes 4 & 5 or 2 & 5
                if self.context == InputContext.GAMEPLAY:
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
                if profile and self.context == InputContext.GAMEPLAY:
                    num_buttons = js.get_numbuttons()
                    for btn_idx in range(num_buttons):
                        if js.get_button(btn_idx):
                            for action_key, b_idx in profile.button_map.items():
                                if b_idx == btn_idx:
                                    upper_action = _ACTION_LOWER_TO_UPPER.get(action_key, action_key.upper())
                                    if upper_action == ACTION_FIRE_PRIMARY:
                                        fire_primary = True
                                        self.active_device = DEVICE_GAMEPAD
                                    elif upper_action == ACTION_FIRE_SECONDARY:
                                        fire_secondary = True
                                        self.active_device = DEVICE_GAMEPAD

            except Exception as e:
                logger.debug(f"[INPUT WARNING] Error polling joystick inputs: {e}")

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
        lower_name = _ACTION_UPPER_TO_LOWER.get(action_name, action_name.lower())
        if self.active_device in (DEVICE_GAMEPAD, DEVICE_JOYSTICK):
            js = self.active_joystick
            if js:
                prompt = self.mapping_manager.get_prompt_for_action(js, lower_name)
                if prompt and prompt != lower_name:
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
