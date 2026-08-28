"""
===============================================================================
                     DRONE HUNTER 2D - ATOMIC SAVE SYSTEM
===============================================================================
Robust, atomic JSON save & load persistence with data integrity validation,
schema versioning ("save_version": 1), safe fallback defaults, and error logging.
Supports 3 save slots with full backward compatibility for legacy unversioned saves.
"""

import os
import json
import logging
import time
from typing import Tuple, Dict, List, Optional, Any
from src.data.settings import SAVE_FILE_NAME
from src.data.game_data import SECTORS, DIFFICULTY_CUSTOM, CUSTOM_DIFFICULTY_DEFAULTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CURRENT_SAVE_VERSION = 1
LEGACY_SAVE_FILE = SAVE_FILE_NAME
NUM_SAVE_SLOTS = 3
VALID_DRONE_CLASSES = {"striker", "interceptor", "assault", "arc", "command"}


class SaveSystem:
    """Handles atomic serialization, schema validation, and slot management for game saves."""

    def __init__(self, save_filename: str = None, slot_index: int = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir

        if slot_index is not None:
            if not isinstance(slot_index, int) or slot_index < 0 or slot_index >= NUM_SAVE_SLOTS:
                raise ValueError(f"Invalid slot_index: {slot_index}. Must be 0 <= slot_index < {NUM_SAVE_SLOTS}")
            self.slot_index = slot_index
            self.save_path = os.path.join(base_dir, f"save_slot_{slot_index + 1}.json")
        elif save_filename is not None:
            # Prevent directory traversal in custom filename
            safe_filename = os.path.basename(save_filename)
            self.save_path = os.path.join(base_dir, safe_filename)
            self.slot_index = None
        else:
            self.slot_index = 0
            self.save_path = os.path.join(base_dir, "save_slot_1.json")

        self.temp_path = self.save_path + ".tmp"

    def set_slot(self, slot_index: int):
        """Switches the active save slot with strict slot range validation (0..2)."""
        if not isinstance(slot_index, int) or slot_index < 0 or slot_index >= NUM_SAVE_SLOTS:
            raise ValueError(f"Invalid slot_index: {slot_index}. Must be 0 <= slot_index < {NUM_SAVE_SLOTS}")
        self.slot_index = slot_index
        self.save_path = os.path.join(self.base_dir, f"save_slot_{slot_index + 1}.json")
        self.temp_path = self.save_path + ".tmp"

    def get_default_save_data(self) -> dict:
        """Returns ONLY the current authoritative save data schema without legacy fields."""
        return {
            "save_version": CURRENT_SAVE_VERSION,
            "scrap": 0,
            "highscore": 0,
            "play_time": 0,
            "last_played": None,
            "upgrades": {
                "hull": 1, "energy": 1, "weapon": 1, "mobility": 1,
                "battery": 0, "speed": 0, "fire_rate": 0, "emp_recharge": 0,
                "wingman": 0, "cloak": 0, "missiles": 0, "beam": 0,
                "tesla": 0, "cluster": 0, "overdrive": 0
            },
            "weapon_upgrades": {},
            "unlocked_weapons": ["pulse", "scatter", "missile"],
            "campaign_state": {
                "current_mission": "S1_M1",
                "completed_missions": [],
                "unlocked_missions": ["S1_M1"],
                "completed_sectors": [],
                "unlocked_sectors": [1],
                "campaign_completed": False,
                "new_game_plus_count": 0
            },
            "achievements": [],
            "show_crt": False,
            "is_fullscreen": False,
            "difficulty_mode": 1,
            "custom_difficulty": CUSTOM_DIFFICULTY_DEFAULTS.copy(),
            "selected_drone": "striker",
            "audio_settings": {
                "sound_enabled": True,
                "sfx_volume": 0.80,
                "music_volume": 0.70,
                "engine_volume": 0.35,
                "master_volume": 1.0
            },
            "controller_settings": {
                "enabled": True,
                "deadzone": 0.12,
                "aim_sensitivity": 1.0,
                "move_sensitivity": 1.0,
                "vibration_enabled": True
            },
            "controller_mappings": {}
        }

    def _create_normalized_defaults(self) -> dict:
        """Helper to create defaults with backward-compatibility query aliases."""
        res = self.get_default_save_data()
        res["coins"] = 0
        res["campaign_completed"] = False
        res["sectors"] = [True, False, False, False, False]
        res["stages"] = [True] + [False] * 14
        return res

    def _get_slot_path(self, slot_index: int) -> str:
        if not isinstance(slot_index, int) or slot_index < 0 or slot_index >= NUM_SAVE_SLOTS:
            raise ValueError(f"Invalid slot_index: {slot_index}. Must be 0 <= slot_index < {NUM_SAVE_SLOTS}")
        return os.path.join(self.base_dir, f"save_slot_{slot_index + 1}.json")

    def get_save_slot_list(self) -> List[Dict]:
        """Returns metadata for all 3 save slots plus legacy save if it exists."""
        slots = []
        for i in range(NUM_SAVE_SLOTS):
            slot_path = self._get_slot_path(i)
            meta = {
                "slot_index": i,
                "filename": os.path.basename(slot_path),
                "exists": os.path.exists(slot_path),
                "play_time": 0,
                "last_played": None,
                "sector": 1,
                "difficulty_mode": 1,
                "scrap": 0,
                "highscore": 0
            }
            if os.path.exists(slot_path):
                try:
                    with open(slot_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    meta["play_time"] = max(0, int(data.get("play_time", 0)))
                    meta["last_played"] = data.get("last_played")
                    camp = data.get("campaign_state", {})
                    if isinstance(camp, dict) and "current_mission" in camp:
                        cur_m = camp.get("current_mission", "S1_M1")
                        try:
                            meta["sector"] = int(cur_m.split("_")[0].replace("S", ""))
                        except Exception:
                            meta["sector"] = 1
                    else:
                        missions = data.get("missions", {})
                        meta["sector"] = missions.get("current_sector", 1) if isinstance(missions, dict) else 1

                    meta["difficulty_mode"] = int(data.get("difficulty_mode", 1)) % 5
                    meta["scrap"] = max(0, int(data.get("scrap", data.get("coins", 0))))
                    meta["highscore"] = max(0, int(data.get("highscore", 0)))
                except Exception:
                    pass
            slots.append(meta)

        legacy_path = os.path.join(self.base_dir, LEGACY_SAVE_FILE)
        if os.path.exists(legacy_path):
            try:
                with open(legacy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                camp = data.get("campaign_state", {})
                if isinstance(camp, dict) and "current_mission" in camp:
                    cur_m = camp.get("current_mission", "S1_M1")
                    try:
                        sec = int(cur_m.split("_")[0].replace("S", ""))
                    except Exception:
                        sec = 1
                else:
                    missions = data.get("missions", {})
                    sec = missions.get("current_sector", 1) if isinstance(missions, dict) else 1

                slots.append({
                    "slot_index": "legacy",
                    "filename": LEGACY_SAVE_FILE,
                    "exists": True,
                    "play_time": max(0, int(data.get("play_time", 0))),
                    "last_played": data.get("last_played"),
                    "sector": sec,
                    "difficulty_mode": int(data.get("difficulty_mode", 1)) % 5,
                    "scrap": max(0, int(data.get("scrap", data.get("coins", 0)))),
                    "highscore": max(0, int(data.get("highscore", 0)))
                })
            except Exception:
                pass

        return slots

    def delete_save_slot(self, slot_index: int) -> bool:
        """Deletes the specified save slot file."""
        if not isinstance(slot_index, int) or slot_index < 0 or slot_index >= NUM_SAVE_SLOTS:
            return False
        try:
            slot_path = self._get_slot_path(slot_index)
            if os.path.exists(slot_path):
                os.remove(slot_path)
            temp_path = slot_path + ".tmp"
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return True
        except Exception as e:
            logging.error(f"Failed to delete save slot {slot_index}: {e}")
            return False

    def load(self) -> dict:
        """Loads and normalizes save data, supporting both versioned and legacy unversioned files."""
        load_path = self.save_path

        if not os.path.exists(load_path):
            legacy_path = os.path.join(self.base_dir, LEGACY_SAVE_FILE)
            if os.path.exists(legacy_path) and self.slot_index is not None:
                load_path = legacy_path
            else:
                logging.info(f"Save file not found at {self.save_path}. Using safe defaults.")
                return self._create_normalized_defaults()

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                logging.warning(f"Save data at {load_path} is not a valid JSON object. Falling back to defaults.")
                return self._create_normalized_defaults()

            # Schema version detection & validation
            raw_version = data.get("save_version")
            if raw_version is not None and isinstance(raw_version, (int, float)):
                save_version = int(raw_version)
                if save_version > CURRENT_SAVE_VERSION:
                    logging.warning(
                        f"Unsupported future save_version {save_version} in {load_path} "
                        f"(current version is {CURRENT_SAVE_VERSION}). Falling back to safe defaults."
                    )
                    return self._create_normalized_defaults()
            else:
                save_version = 0  # Legacy / unversioned

            defaults = self.get_default_save_data()

            # Core Resources & Stats Normalization
            legacy_coins = max(0, int(data.get("coins", 0))) if isinstance(data.get("coins"), (int, float)) else 0
            raw_scrap = int(data.get("scrap", 0)) if isinstance(data.get("scrap"), (int, float)) else 0
            scrap = max(0, raw_scrap if raw_scrap > 0 else (legacy_coins if legacy_coins > 0 else 0))

            raw_highscore = data.get("highscore", defaults["highscore"])
            highscore = max(0, int(raw_highscore)) if isinstance(raw_highscore, (int, float)) else defaults["highscore"]

            raw_play_time = data.get("play_time", 0)
            play_time = max(0, int(raw_play_time)) if isinstance(raw_play_time, (int, float)) else 0
            last_played = str(data.get("last_played")) if data.get("last_played") is not None else None

            # Upgrades Normalization
            upgrades = defaults["upgrades"].copy()
            loaded_upgrades = data.get("upgrades", {})
            if isinstance(loaded_upgrades, dict):
                for k, v in loaded_upgrades.items():
                    if k in upgrades:
                        try:
                            upgrades[k] = max(0, int(v))
                        except (ValueError, TypeError):
                            pass

            weapon_upgrades = {}
            loaded_w_upg = data.get("weapon_upgrades", {})
            if isinstance(loaded_w_upg, dict):
                for k, v in loaded_w_upg.items():
                    try:
                        weapon_upgrades[str(k)] = max(0, int(v))
                    except (ValueError, TypeError):
                        pass

            # Unlocked Weapons Normalization
            unlocked_weapons = defaults["unlocked_weapons"].copy()
            loaded_unlocked_w = data.get("unlocked_weapons")
            if isinstance(loaded_unlocked_w, list) and loaded_unlocked_w:
                unlocked_weapons = [str(w) for w in loaded_unlocked_w if isinstance(w, (str, int))]

            # Campaign State Normalization & Legacy Reconstruction
            campaign_state = data.get("campaign_state")
            if not isinstance(campaign_state, dict) or "current_mission" not in campaign_state:
                # Legacy save fallback: reconstruct CampaignState dictionary from old fields
                legacy_missions = data.get("missions", {}) if isinstance(data.get("missions"), dict) else {}
                legacy_sector_prog = data.get("sector_progress", {}) if isinstance(data.get("sector_progress"), dict) else {}
                sec = legacy_missions.get("current_sector", 1)
                mis = legacy_missions.get("current_mission", 1)
                cur_mission = f"S{sec}_M{mis}"
                completed_m = legacy_missions.get("completed", [])
                unlocked_m = legacy_missions.get("unlocked", ["S1_M1"])
                completed_s = legacy_sector_prog.get("completed", [])
                unlocked_s = legacy_sector_prog.get("unlocked", [1])
                camp_completed = bool(data.get("campaign_completed", False))

                campaign_state = {
                    "current_mission": cur_mission,
                    "completed_missions": completed_m if isinstance(completed_m, list) else [],
                    "unlocked_missions": unlocked_m if isinstance(unlocked_m, list) else ["S1_M1"],
                    "completed_sectors": completed_s if isinstance(completed_s, list) else [],
                    "unlocked_sectors": unlocked_s if isinstance(unlocked_s, list) else [1],
                    "campaign_completed": camp_completed,
                    "new_game_plus_count": max(0, int(data.get("new_game_plus_count", 0)))
                }

            # Achievements Normalization
            achievements = []
            loaded_achievements = data.get("achievements")
            if isinstance(loaded_achievements, list):
                achievements = [str(a) for a in loaded_achievements]

            # System & Gameplay Settings Normalization
            show_crt = bool(data.get("show_crt", False))
            is_fullscreen = bool(data.get("is_fullscreen", False))
            raw_diff = data.get("difficulty_mode", 1)
            difficulty_mode = int(raw_diff) % 5 if isinstance(raw_diff, (int, float)) else 1

            raw_drone = str(data.get("selected_drone", "striker"))
            selected_drone = raw_drone if raw_drone in VALID_DRONE_CLASSES else "striker"

            custom_difficulty = defaults["custom_difficulty"].copy()
            loaded_cd = data.get("custom_difficulty")
            if isinstance(loaded_cd, dict):
                for k, v in loaded_cd.items():
                    if k in custom_difficulty and isinstance(v, (int, float)):
                        custom_difficulty[k] = float(v)

            # Audio Settings Normalization
            audio_settings = defaults["audio_settings"].copy()
            loaded_audio = data.get("audio_settings")
            if isinstance(loaded_audio, dict):
                audio_settings["sound_enabled"] = bool(loaded_audio.get("sound_enabled", True))
                for vol_k in ("sfx_volume", "music_volume", "engine_volume", "master_volume"):
                    if vol_k in loaded_audio and isinstance(loaded_audio[vol_k], (int, float)):
                        audio_settings[vol_k] = max(0.0, min(1.0, float(loaded_audio[vol_k])))

            # Controller Settings Normalization
            controller_settings = defaults["controller_settings"].copy()
            loaded_ctrl = data.get("controller_settings")
            if isinstance(loaded_ctrl, dict):
                controller_settings["enabled"] = bool(loaded_ctrl.get("enabled", True))
                controller_settings["vibration_enabled"] = bool(loaded_ctrl.get("vibration_enabled", True))
                if "deadzone" in loaded_ctrl and isinstance(loaded_ctrl["deadzone"], (int, float)):
                    controller_settings["deadzone"] = max(0.02, min(0.40, float(loaded_ctrl["deadzone"])))
                if "aim_sensitivity" in loaded_ctrl and isinstance(loaded_ctrl["aim_sensitivity"], (int, float)):
                    controller_settings["aim_sensitivity"] = max(0.2, min(3.0, float(loaded_ctrl["aim_sensitivity"])))
                if "move_sensitivity" in loaded_ctrl and isinstance(loaded_ctrl["move_sensitivity"], (int, float)):
                    controller_settings["move_sensitivity"] = max(0.2, min(2.0, float(loaded_ctrl["move_sensitivity"])))

            controller_mappings = {}
            loaded_maps = data.get("controller_mappings")
            if isinstance(loaded_maps, dict):
                controller_mappings = loaded_maps.copy()

            # Construct normalized runtime payload
            result = {
                "save_version": CURRENT_SAVE_VERSION,
                "scrap": scrap,
                "highscore": highscore,
                "play_time": play_time,
                "last_played": last_played,
                "upgrades": upgrades,
                "weapon_upgrades": weapon_upgrades,
                "unlocked_weapons": unlocked_weapons,
                "campaign_state": campaign_state,
                "achievements": achievements,
                "show_crt": show_crt,
                "is_fullscreen": is_fullscreen,
                "difficulty_mode": difficulty_mode,
                "custom_difficulty": custom_difficulty,
                "selected_drone": selected_drone,
                "audio_settings": audio_settings,
                "controller_settings": controller_settings,
                "controller_mappings": controller_mappings
            }

            # Optional compatibility fields for legacy callers querying old keys
            result["coins"] = scrap
            result["campaign_completed"] = bool(campaign_state.get("campaign_completed", False))
            result["sectors"] = [True, False, False, False, False]
            result["stages"] = [True] + [False] * 14

            return result

        except json.JSONDecodeError as jde:
            logging.error(f"Save file {self.save_path} is corrupted ({jde}). Falling back to safe defaults.")
            return self._create_normalized_defaults()
        except Exception as e:
            logging.error(f"Unexpected error loading save data from {load_path}: {e}. Using safe defaults.")
            return self._create_normalized_defaults()

    def save(self, data_or_scrap: Any = None, **kwargs) -> bool:
        """Atomically saves game data using a temporary write & replace pattern with schema version 1."""
        defaults = self.get_default_save_data()

        # Consolidate payload from dictionary or kwargs
        if isinstance(data_or_scrap, dict):
            payload = data_or_scrap.copy()
            payload.update(kwargs)
        elif data_or_scrap is not None:
            payload = {"scrap": data_or_scrap}
            payload.update(kwargs)
        else:
            payload = kwargs.copy()

        # Normalization and Validation
        raw_scrap = int(payload.get("scrap", 0)) if isinstance(payload.get("scrap"), (int, float)) else 0
        raw_coins = int(payload.get("coins", 0)) if isinstance(payload.get("coins"), (int, float)) else 0
        scrap = max(0, raw_scrap if raw_scrap > 0 else (raw_coins if raw_coins > 0 else 0))

        highscore = max(0, int(payload.get("highscore", 0)))
        play_time = max(0, int(payload.get("play_time", 0)))
        last_played = payload.get("last_played")
        if last_played is None:
            last_played = time.strftime("%Y-%m-%dT%H:%M:%S")

        upgrades = payload.get("upgrades")
        if not isinstance(upgrades, dict):
            upgrades = defaults["upgrades"].copy()

        weapon_upgrades = payload.get("weapon_upgrades")
        if not isinstance(weapon_upgrades, dict):
            weapon_upgrades = defaults["weapon_upgrades"].copy()

        unlocked_weapons = payload.get("unlocked_weapons")
        if not isinstance(unlocked_weapons, list):
            unlocked_weapons = defaults["unlocked_weapons"].copy()
        else:
            unlocked_weapons = [str(w) for w in unlocked_weapons]

        campaign_state = payload.get("campaign_state")
        if not isinstance(campaign_state, dict) or "current_mission" not in campaign_state:
            legacy_missions = payload.get("missions", {}) if isinstance(payload.get("missions"), dict) else {}
            legacy_sector_prog = payload.get("sector_progress", {}) if isinstance(payload.get("sector_progress"), dict) else {}
            sec = legacy_missions.get("current_sector", 1)
            mis = legacy_missions.get("current_mission", 1)
            cur_mission = f"S{sec}_M{mis}"
            completed_m = legacy_missions.get("completed", [])
            unlocked_m = legacy_missions.get("unlocked", ["S1_M1"])
            completed_s = legacy_sector_prog.get("completed", [])
            unlocked_s = legacy_sector_prog.get("unlocked", [1])
            camp_completed = bool(payload.get("campaign_completed", False))

            campaign_state = {
                "current_mission": cur_mission,
                "completed_missions": completed_m if isinstance(completed_m, list) else [],
                "unlocked_missions": unlocked_m if isinstance(unlocked_m, list) else ["S1_M1"],
                "completed_sectors": completed_s if isinstance(completed_s, list) else [],
                "unlocked_sectors": unlocked_s if isinstance(unlocked_s, list) else [1],
                "campaign_completed": camp_completed,
                "new_game_plus_count": max(0, int(payload.get("new_game_plus_count", 0)))
            }

        achievements = payload.get("achievements")
        if not isinstance(achievements, list):
            achievements = defaults["achievements"].copy()
        else:
            achievements = [str(a) for a in achievements]

        show_crt = bool(payload.get("show_crt", False))
        is_fullscreen = bool(payload.get("is_fullscreen", False))
        difficulty_mode = int(payload.get("difficulty_mode", 1)) % 5

        raw_drone = str(payload.get("selected_drone", "striker"))
        selected_drone = raw_drone if raw_drone in VALID_DRONE_CLASSES else "striker"

        custom_difficulty = payload.get("custom_difficulty")
        if not isinstance(custom_difficulty, dict):
            custom_difficulty = defaults["custom_difficulty"].copy()

        audio_settings = payload.get("audio_settings")
        if not isinstance(audio_settings, dict):
            audio_settings = defaults["audio_settings"].copy()

        controller_settings = payload.get("controller_settings")
        if not isinstance(controller_settings, dict):
            controller_settings = defaults["controller_settings"].copy()

        controller_mappings = payload.get("controller_mappings")
        if not isinstance(controller_mappings, dict):
            controller_mappings = defaults["controller_mappings"].copy()

        # Pure versioned save dictionary — NO coins, stages, bosses_defeated, selected_skin, or duplicate missions trees
        save_dict = {
            "save_version": CURRENT_SAVE_VERSION,
            "scrap": scrap,
            "highscore": highscore,
            "play_time": play_time,
            "last_played": last_played,
            "upgrades": upgrades,
            "weapon_upgrades": weapon_upgrades,
            "unlocked_weapons": unlocked_weapons,
            "campaign_state": campaign_state,
            "achievements": achievements,
            "show_crt": show_crt,
            "is_fullscreen": is_fullscreen,
            "difficulty_mode": difficulty_mode,
            "custom_difficulty": custom_difficulty,
            "selected_drone": selected_drone,
            "audio_settings": audio_settings,
            "controller_settings": controller_settings,
            "controller_mappings": controller_mappings
        }

        try:
            with open(self.temp_path, "w", encoding="utf-8") as f:
                json.dump(save_dict, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            if os.path.exists(self.save_path):
                os.replace(self.temp_path, self.save_path)
            else:
                os.rename(self.temp_path, self.save_path)

            return True

        except Exception as e:
            logging.error(f"Failed to atomically write save data to {self.save_path}: {e}")
            if os.path.exists(self.temp_path):
                try:
                    os.remove(self.temp_path)
                except Exception:
                    pass
            return False
