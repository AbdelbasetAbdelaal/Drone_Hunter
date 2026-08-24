"""
===============================================================================
                     DRONE HUNTER 2D - CONTROLLER MAPPING SYSTEM
===============================================================================
Device-aware controller mapping with auto-detection, per-profile button/axis
resolution, D-pad hat/button fallback, and save/load support.
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# LOGICAL ACTIONS
# ------------------------------------------------------------------------------
ACTION_MOVE_UP = "move_up"
ACTION_MOVE_DOWN = "move_down"
ACTION_MOVE_LEFT = "move_left"
ACTION_MOVE_RIGHT = "move_right"
ACTION_FIRE_PRIMARY = "fire_primary"
ACTION_FIRE_SECONDARY = "fire_secondary"
ACTION_WEAPON_NEXT = "weapon_next"
ACTION_WEAPON_PREV = "weapon_prev"
ACTION_ULTIMATE = "ultimate"
ACTION_EMP = "emp"
ACTION_SPECIAL = "special"
ACTION_CLOAK = "cloak"
ACTION_PAUSE = "pause"
ACTION_FULLSCREEN = "fullscreen"
ACTION_CONFIRM = "confirm"
ACTION_CANCEL = "cancel"
ACTION_ROLL = "roll"
ACTION_SECTOR_MAP = "sector_map"
ACTION_HANGAR_BAY = "hangar_bay"
ACTION_CYCLE_SKIN = "cycle_skin"

ACTION_FRONT_TOP = "front_top"
ACTION_FRONT_BOTTOM = "front_bottom"
ACTION_CYCLE_CLASS = "cycle_class"

DPAD_ACTIONS = (ACTION_MOVE_UP, ACTION_MOVE_DOWN, ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT)

# ------------------------------------------------------------------------------
# CANONICAL PHYSICAL BUTTON NAMES
# ------------------------------------------------------------------------------
PHYSICAL_BUTTON_NAMES_PS = {
    0: "TRIANGLE",
    1: "CIRCLE",
    2: "CROSS",
    3: "SQUARE",
    4: "FRONT BOTTOM (L1)",
    5: "FRONT TOP (R1)",
    6: "L2 TRIGGER",
    7: "R2 TRIGGER",
    8: "SELECT",
    9: "START",
    10: "L3",
    11: "R3",
}

PHYSICAL_BUTTON_NAMES_XBOX = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "LB",
    5: "RB",
    6: "BACK",
    7: "START",
    8: "LS",
    9: "RS",
}

def get_physical_button_name(btn_idx: int, controller_type: str = "generic_ps2") -> str:
    """Returns canonical physical button name for a raw button index."""
    if btn_idx < 0:
        return "NONE"
    if controller_type == "xbox":
        return PHYSICAL_BUTTON_NAMES_XBOX.get(btn_idx, f"BTN {btn_idx}")
    return PHYSICAL_BUTTON_NAMES_PS.get(btn_idx, f"BTN {btn_idx}")


# ------------------------------------------------------------------------------
# CATEGORIZED ACTIONS
# ------------------------------------------------------------------------------
GAMEPLAY_ACTIONS = [
    ACTION_FIRE_PRIMARY,
    ACTION_EMP,
    ACTION_ULTIMATE,
    ACTION_ROLL,
    ACTION_WEAPON_NEXT,
    ACTION_CLOAK,
]

MENU_ACTIONS = [
    ACTION_CONFIRM,
    ACTION_CANCEL,
    ACTION_PAUSE,
    ACTION_SECTOR_MAP,
    ACTION_HANGAR_BAY,
]

CONTEXTUAL_ACTIONS = [
    ACTION_WEAPON_PREV,
    ACTION_CYCLE_CLASS,
    ACTION_CYCLE_SKIN,
    ACTION_FULLSCREEN,
]


# ------------------------------------------------------------------------------
# DEFAULT BUTTON MAPPINGS PER CONTROLLER TYPE (SINGLE SOURCE OF TRUTH)
# ------------------------------------------------------------------------------
DEFAULT_MAPPINGS = {
    ACTION_FIRE_PRIMARY:   {"xbox": 0, "playstation": 0, "generic": 0, "generic_ps2": 2},
    ACTION_FIRE_SECONDARY: {"xbox": 1, "playstation": 1, "generic": 1, "generic_ps2": 1},
    ACTION_FRONT_TOP:      {"xbox": 5, "playstation": 2, "generic": 2, "generic_ps2": 5},
    ACTION_FRONT_BOTTOM:   {"xbox": 4, "playstation": 3, "generic": 3, "generic_ps2": 4},
    ACTION_WEAPON_NEXT:    {"xbox": 5, "playstation": 2, "generic": 2, "generic_ps2": 5},
    ACTION_WEAPON_PREV:    {"xbox": 4, "playstation": 3, "generic": 3, "generic_ps2": 4},
    ACTION_ULTIMATE:       {"xbox": 3, "playstation": 3, "generic": 3, "generic_ps2": 0},
    ACTION_EMP:            {"xbox": 2, "playstation": 2, "generic": 2, "generic_ps2": 1},
    ACTION_SPECIAL:        {"xbox": 1, "playstation": 4, "generic": 4, "generic_ps2": 4},
    ACTION_CLOAK:          {"xbox": 1, "playstation": 4, "generic": 4, "generic_ps2": 4},
    ACTION_CYCLE_CLASS:    {"xbox": 4, "playstation": 3, "generic": 3, "generic_ps2": 4},
    ACTION_PAUSE:          {"xbox": 7, "playstation": 5, "generic": 5, "generic_ps2": 9},
    ACTION_FULLSCREEN:     {"xbox": 7, "playstation": 5, "generic": 5, "generic_ps2": 9},
    ACTION_CONFIRM:        {"xbox": 0, "playstation": 0, "generic": 0, "generic_ps2": 2},
    ACTION_CANCEL:         {"xbox": 1, "playstation": 1, "generic": 1, "generic_ps2": 1},
    ACTION_ROLL:           {"xbox": 0, "playstation": 0, "generic": 0, "generic_ps2": 3},
    ACTION_SECTOR_MAP:     {"xbox": 6, "playstation": 8, "generic": 8, "generic_ps2": 8},
    ACTION_HANGAR_BAY:     {"xbox": 6, "playstation": 8, "generic": 8, "generic_ps2": 8},
    ACTION_CYCLE_SKIN:     {"xbox": 4, "playstation": 4, "generic": 4, "generic_ps2": 4},
}

# ------------------------------------------------------------------------------
# PROMPT LABELS PER CONTROLLER TYPE
# ------------------------------------------------------------------------------
PROMPT_LABELS = {
    "xbox": {
        ACTION_FIRE_PRIMARY: "A",
        ACTION_FIRE_SECONDARY: "B",
        ACTION_FRONT_TOP: "RB / LB",
        ACTION_FRONT_BOTTOM: "RT / LT",
        ACTION_WEAPON_NEXT: "RB",
        ACTION_WEAPON_PREV: "LB",
        ACTION_ULTIMATE: "Y",
        ACTION_EMP: "X",
        ACTION_SPECIAL: "B",
        ACTION_CLOAK: "LB",
        ACTION_CYCLE_CLASS: "LB (HOLD)",
        ACTION_PAUSE: "START",
        ACTION_FULLSCREEN: "START (HOLD)",
        ACTION_CONFIRM: "A",
        ACTION_CANCEL: "B",
        ACTION_ROLL: "A",
        ACTION_SECTOR_MAP: "BACK",
        ACTION_HANGAR_BAY: "BACK",
        ACTION_CYCLE_SKIN: "LB",
    },
    "playstation": {
        ACTION_FIRE_PRIMARY: "X",
        ACTION_FIRE_SECONDARY: "O",
        ACTION_FRONT_TOP: "R1 / L1",
        ACTION_FRONT_BOTTOM: "R2 / L2",
        ACTION_WEAPON_NEXT: "□",
        ACTION_WEAPON_PREV: "△",
        ACTION_ULTIMATE: "△",
        ACTION_EMP: "□",
        ACTION_SPECIAL: "SELECT",
        ACTION_CLOAK: "SELECT",
        ACTION_CYCLE_CLASS: "L1 (HOLD)",
        ACTION_PAUSE: "START",
        ACTION_FULLSCREEN: "START (HOLD)",
        ACTION_CONFIRM: "X",
        ACTION_CANCEL: "O",
        ACTION_ROLL: "X",
        ACTION_SECTOR_MAP: "SELECT",
        ACTION_HANGAR_BAY: "SELECT",
        ACTION_CYCLE_SKIN: "SELECT",
    },
    "generic_ps2": {
        ACTION_FIRE_PRIMARY: "[X] FIRE",
        ACTION_FIRE_SECONDARY: "[O] EMP",
        ACTION_FRONT_TOP: "[FRONT TOP] WEAPON",
        ACTION_FRONT_BOTTOM: "[FRONT BTM] CLOAK",
        ACTION_WEAPON_NEXT: "[R FRONT] WEAPON",
        ACTION_WEAPON_PREV: "[L FRONT] PREV",
        ACTION_ULTIMATE: "[△] OVERDRIVE",
        ACTION_EMP: "[O] EMP",
        ACTION_SPECIAL: "[L FRONT] CLOAK",
        ACTION_CLOAK: "[L FRONT] CLOAK",
        ACTION_CYCLE_CLASS: "[FRONT BTM HOLD] DRONE",
        ACTION_PAUSE: "[START] PAUSE",
        ACTION_FULLSCREEN: "[START HOLD] FULLSCREEN",
        ACTION_CONFIRM: "[X] CONFIRM",
        ACTION_CANCEL: "[O] BACK",
        ACTION_ROLL: "[□] ROLL",
        ACTION_SECTOR_MAP: "[SELECT] MAP",
        ACTION_HANGAR_BAY: "[SELECT] HANGAR",
        ACTION_CYCLE_SKIN: "[L FRONT] SKIN",
    },
    "generic": {
        ACTION_FIRE_PRIMARY: "BTN-0",
        ACTION_FIRE_SECONDARY: "BTN-1",
        ACTION_FRONT_TOP: "BTN-4/5",
        ACTION_FRONT_BOTTOM: "BTN-6/7",
        ACTION_WEAPON_NEXT: "BTN-2",
        ACTION_WEAPON_PREV: "BTN-3",
        ACTION_ULTIMATE: "BTN-3",
        ACTION_EMP: "BTN-2",
        ACTION_SPECIAL: "BTN-4",
        ACTION_CLOAK: "BTN-4",
        ACTION_CYCLE_CLASS: "BTN-4 (HOLD)",
        ACTION_PAUSE: "BTN-5",
        ACTION_FULLSCREEN: "BTN-5",
        ACTION_CONFIRM: "BTN-0",
        ACTION_CANCEL: "BTN-1",
        ACTION_ROLL: "BTN-0",
        ACTION_SECTOR_MAP: "BTN-8",
        ACTION_HANGAR_BAY: "BTN-8",
        ACTION_CYCLE_SKIN: "BTN-4",
    },
}


# ------------------------------------------------------------------------------
# CONTROLLER PROFILE
# ------------------------------------------------------------------------------
class ControllerProfile:
    """Stores resolved button/axis mappings for a specific controller instance."""

    def __init__(self, device_name: str, device_guid: str, instance_id: int,
                 controller_type: str = "unknown"):
        self.device_name = device_name
        self.device_guid = device_guid
        self.instance_id = instance_id
        self.controller_type = controller_type
        self.is_xbox_style = controller_type == "xbox"
        self.is_ps_style = controller_type in ("playstation", "generic_ps2")

        self.button_map: Dict[str, int] = {}
        self.axis_map: Dict[str, Tuple[int, int]] = {}
        self.prompt_labels: Dict[str, str] = {}
        self._build_defaults()

    def _build_defaults(self):
        ctype = self.controller_type if self.controller_type in ("xbox", "playstation", "generic_ps2", "generic") else "generic"
        for action, mapping in DEFAULT_MAPPINGS.items():
            if mapping.get(ctype) is not None:
                self.button_map[action] = mapping[ctype]
        labels = PROMPT_LABELS.get(ctype, PROMPT_LABELS["generic"])
        self.prompt_labels = dict(labels)

    def set_button(self, action: str, button_index: int):
        self.button_map[action] = button_index

    def get_action_for_button(self, button_index: int) -> Optional[str]:
        for action, btn_idx in self.button_map.items():
            if btn_idx == button_index:
                return action
        return None

    def set_axis(self, action: str, axis_index: int, direction: int = 1):
        self.axis_map[action] = (axis_index, direction)

    def get_prompt(self, action: str) -> str:
        return self.prompt_labels.get(action, action)

    def to_dict(self) -> dict:
        return {
            "device_name": self.device_name,
            "device_guid": self.device_guid,
            "instance_id": self.instance_id,
            "controller_type": self.controller_type,
            "button_map": dict(self.button_map),
            "axis_map": {k: list(v) for k, v in self.axis_map.items()},
            "prompt_labels": dict(self.prompt_labels),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ControllerProfile":
        profile = cls(
            data.get("device_name", "Unknown"),
            data.get("device_guid", ""),
            data.get("instance_id", 0),
            data.get("controller_type", "generic"),
        )
        profile.button_map = {str(k): int(v) for k, v in data.get("button_map", {}).items()}
        profile.axis_map = {str(k): (int(v[0]), int(v[1])) for k, v in data.get("axis_map", {}).items()}
        profile.prompt_labels = {str(k): str(v) for k, v in data.get("prompt_labels", {}).items()}
        return profile


# ------------------------------------------------------------------------------
# CONTROLLER MAPPING MANAGER
# ------------------------------------------------------------------------------
class ControllerMappingManager:
    """Manages controller profiles, auto-detection, save/load, and D-pad resolution."""

    def __init__(self, mappings_path: str = None):
        if mappings_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            mappings_path = os.path.join(base_dir, "controller_mappings.json")
        self.mappings_path = mappings_path
        self.profiles: Dict[str, ControllerProfile] = {}
        self._load_mappings()

    # ------------------------------------------------------------------
    # Profile Management
    # ------------------------------------------------------------------
    def _profile_key(self, joystick) -> str:
        try:
            guid = joystick.get_guid()
        except Exception:
            guid = ""
        try:
            name = joystick.get_name()
        except Exception:
            name = "Unknown"
        return f"{guid}|{name}"

    def get_or_create_profile(self, joystick) -> ControllerProfile:
        key = self._profile_key(joystick)
        if key in self.profiles:
            return self.profiles[key]

        ctype = self._detect_controller_type(joystick)
        try:
            name = joystick.get_name()
            guid = joystick.get_guid()
            instance_id = joystick.get_instance_id()
        except Exception:
            name = "Unknown"
            guid = key
            instance_id = 0

        profile = ControllerProfile(name, guid, instance_id, ctype)
        self.profiles[key] = profile
        return profile

    def get_profile_for_joystick(self, joystick) -> Optional[ControllerProfile]:
        if joystick is None:
            return None
        key = self._profile_key(joystick)
        if key in self.profiles:
            return self.profiles[key]
        return self.get_or_create_profile(joystick)

    # ------------------------------------------------------------------
    # Controller Type Detection
    # ------------------------------------------------------------------
    def _detect_controller_type(self, joystick) -> str:
        try:
            name = joystick.get_name().lower()
        except Exception:
            name = ""
        if "xbox" in name or "xinput" in name:
            return "xbox"
        elif any(x in name for x in ["playstation", "dualshock", "dualsense", "ps4", "ps5", "ps3"]):
            return "playstation"
        elif any(x in name for x in ["twin", "usb gamepad", "ps2", "dragonrise", "generic_ps2"]):
            return "generic_ps2"
        elif "generic" in name or "directinput" in name or "gamepad" in name:
            return "generic"
        return "generic"

    # ------------------------------------------------------------------
    # D-Pad Resolution
    # ------------------------------------------------------------------
    def get_dpad_input(self, joystick) -> dict:
        result = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }
        try:
            num_hats = joystick.get_numhats()
            if num_hats > 0:
                hat_value = joystick.get_hat(0)
                if hat_value[1] > 0: result["up"] = True
                if hat_value[1] < 0: result["down"] = True
                if hat_value[0] < 0: result["left"] = True
                if hat_value[0] > 0: result["right"] = True
                if any(result.values()):
                    return result
        except Exception:
            pass

        # Check analog axes (Axes 0 & 1 for D-Pad on 2-axis gamepads)
        try:
            num_axes = joystick.get_numaxes()
            if num_axes >= 2:
                ax0 = joystick.get_axis(0)
                ax1 = joystick.get_axis(1)
                if ax1 < -0.30: result["up"] = True
                if ax1 > 0.30: result["down"] = True
                if ax0 < -0.30: result["left"] = True
                if ax0 > 0.30: result["right"] = True
                if any(result.values()):
                    return result
        except Exception:
            pass

        profile = self.get_profile_for_joystick(joystick)
        if profile is None:
            return result

        btn_map = profile.button_map
        try:
            num_buttons = joystick.get_numbuttons()
            def _safe_get(idx):
                if 0 <= idx < num_buttons:
                    return joystick.get_button(idx)
                return False

            if _safe_get(btn_map.get("dpad_up", 12)): result["up"] = True
            if _safe_get(btn_map.get("dpad_down", 13)): result["down"] = True
            if _safe_get(btn_map.get("dpad_left", 14)): result["left"] = True
            if _safe_get(btn_map.get("dpad_right", 15)): result["right"] = True
        except Exception:
            pass
        return result

    # ------------------------------------------------------------------
    # Button Resolution
    # ------------------------------------------------------------------
    def get_action_button(self, joystick, action: str) -> Optional[int]:
        profile = self.get_profile_for_joystick(joystick)
        if profile is None:
            return None
        return profile.button_map.get(action)

    def is_action_pressed(self, joystick, action: str) -> bool:
        btn_idx = self.get_action_button(joystick, action)
        if btn_idx is None:
            return False
        try:
            num_buttons = joystick.get_numbuttons()
            if 0 <= btn_idx < num_buttons:
                return bool(joystick.get_button(btn_idx))
        except Exception:
            pass
        return False

    # ------------------------------------------------------------------
    # Prompt Labels
    # ------------------------------------------------------------------
    def get_prompt_for_action(self, joystick, action: str) -> str:
        profile = self.get_profile_for_joystick(joystick)
        if profile is None:
            ctype = self._detect_controller_type(joystick)
            labels = PROMPT_LABELS.get(ctype, PROMPT_LABELS["generic"])
            return labels.get(action, action)
        return profile.get_prompt(action)

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------
    def save_mappings(self):
        try:
            data = {k: v.to_dict() for k, v in self.profiles.items()}
            with open(self.mappings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save controller mappings: {e}")

    def load_mappings(self):
        try:
            if not os.path.exists(self.mappings_path):
                return
            with open(self.mappings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, profile_data in data.items():
                try:
                    self.profiles[key] = ControllerProfile.from_dict(profile_data)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Failed to load controller mappings: {e}")

    def _load_mappings(self):
        self.load_mappings()

    def reset_to_defaults(self, joystick) -> ControllerProfile:
        key = self._profile_key(joystick)
        if key in self.profiles:
            del self.profiles[key]
        profile = self.get_or_create_profile(joystick)
        self.save_mappings()
        return profile

    # ------------------------------------------------------------------
    # Binding Wizard Helpers
    # ------------------------------------------------------------------
    def record_binding(self, joystick, action: str, event_type: str,
                       button_index: int = -1, hat_value: tuple = None,
                       axis_index: int = -1, axis_direction: int = 0) -> bool:
        """Records a new binding for an action. Returns True if successful."""
        profile = self.get_or_create_profile(joystick)
        if event_type == "button":
            if button_index < 0:
                return False
            profile.set_button(action, button_index)
        elif event_type == "hat":
            profile.set_button(action, -1)  # Hat actions stored as special sentinel
        elif event_type == "axis":
            if axis_index < 0 or axis_direction == 0:
                return False
            profile.set_axis(action, axis_index, axis_direction)
        else:
            return False
        self.save_mappings()
        return True

    def check_duplicate_binding(self, joystick, action: str, event_type: str,
                                button_index: int = -1) -> bool:
        """Returns True if the given raw input is already bound to a different action."""
        profile = self.get_profile_for_joystick(joystick)
        if profile is None:
            return False
        if event_type != "button":
            return False
        for existing_action, existing_btn in profile.button_map.items():
            if existing_action != action and existing_btn == button_index:
                return True
        return False

    def get_all_actions(self) -> list:
        return list(DEFAULT_MAPPINGS.keys())
