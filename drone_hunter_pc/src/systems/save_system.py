"""
===============================================================================
                     DRONE HUNTER 2D - ATOMIC SAVE SYSTEM
===============================================================================
Robust, atomic JSON save & load persistence with data integrity validation,
safe fallback defaults, and error logging. Supports 3 save slots with backward
compatibility for the legacy single save file.
"""

import os
import json
import logging
import time
from typing import Tuple, Dict, List, Optional
from src.data.settings import SAVE_FILE_NAME
from src.data.game_data import SECTORS, DIFFICULTY_CUSTOM, CUSTOM_DIFFICULTY_DEFAULTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

LEGACY_SAVE_FILE = SAVE_FILE_NAME
NUM_SAVE_SLOTS = 3

class SaveSystem:
    def __init__(self, save_filename: str = None, slot_index: int = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir

        if slot_index is not None:
            self.save_path = os.path.join(base_dir, f"save_slot_{slot_index + 1}.json")
            self.slot_index = slot_index
        elif save_filename is not None:
            self.save_path = os.path.join(base_dir, save_filename)
            self.slot_index = None
        else:
            self.save_path = os.path.join(base_dir, "save_slot_1.json")
            self.slot_index = 0

        self.temp_path = self.save_path + ".tmp"

    def set_slot(self, slot_index: int):
        """Switches the active save slot and updates file paths."""
        self.slot_index = slot_index
        self.save_path = os.path.join(self.base_dir, f"save_slot_{slot_index + 1}.json")
        self.temp_path = self.save_path + ".tmp"

    def get_default_save_data(self) -> dict:
        return {
            "scrap": 0,
            "coins": 0,
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
            "sectors": [True, False, False, False, False],
            "stages": [True] + [False] * 14,
            "missions": {
                "current_sector": 1,
                "current_mission": 1,
                "completed": [],
                "unlocked": ["S1_M1"]
            },
            "sector_progress": {
                "completed": [],
                "unlocked": [1]
            },
            "campaign_completed": False,
            "achievements": [],
            "show_crt": False,
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

    def _get_slot_path(self, slot_index: int) -> str:
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
                    meta["play_time"] = int(data.get("play_time", 0))
                    meta["last_played"] = data.get("last_played")
                    missions = data.get("missions", {})
                    meta["sector"] = missions.get("current_sector", 1)
                    meta["difficulty_mode"] = int(data.get("difficulty_mode", 1))
                    meta["scrap"] = int(data.get("scrap", 0))
                    meta["highscore"] = int(data.get("highscore", 0))
                except Exception:
                    pass
            slots.append(meta)

        legacy_path = os.path.join(self.base_dir, LEGACY_SAVE_FILE)
        if os.path.exists(legacy_path):
            try:
                with open(legacy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                slots.append({
                    "slot_index": "legacy",
                    "filename": LEGACY_SAVE_FILE,
                    "exists": True,
                    "play_time": int(data.get("play_time", 0)),
                    "last_played": data.get("last_played"),
                    "sector": data.get("missions", {}).get("current_sector", 1),
                    "difficulty_mode": int(data.get("difficulty_mode", 1)),
                    "scrap": int(data.get("scrap", 0)),
                    "highscore": int(data.get("highscore", 0))
                })
            except Exception:
                pass

        return slots

    def delete_save_slot(self, slot_index: int) -> bool:
        """Deletes the specified save slot file."""
        if slot_index < 0 or slot_index >= NUM_SAVE_SLOTS:
            return False
        slot_path = self._get_slot_path(slot_index)
        try:
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
        """Loads and validates progress data from disk."""
        defaults = self.get_default_save_data()
        load_path = self.save_path

        if not os.path.exists(load_path):
            legacy_path = os.path.join(self.base_dir, LEGACY_SAVE_FILE)
            if os.path.exists(legacy_path) and self.slot_index is not None:
                load_path = legacy_path
            else:
                logging.info(f"Save file not found at {self.save_path}. Using safe defaults.")
                return defaults

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            legacy_coins = max(0, int(data.get("coins", 0)))
            raw_scrap = int(data.get("scrap", 0))
            scrap = max(0, raw_scrap if raw_scrap > 0 else (legacy_coins if legacy_coins > 0 else 0))
            highscore = max(0, int(data.get("highscore", defaults["highscore"])))
            play_time = max(0, int(data.get("play_time", 0)))
            last_played = data.get("last_played")

            upgrades = defaults["upgrades"].copy()
            loaded_upgrades = data.get("upgrades", {})
            if isinstance(loaded_upgrades, dict):
                for k, v in loaded_upgrades.items():
                    if k in upgrades:
                        try: upgrades[k] = max(0, int(v))
                        except (ValueError, TypeError): pass

            raw_sectors = data.get("sectors")
            sectors = list(raw_sectors) if raw_sectors is not None else list(defaults["sectors"])
            while len(sectors) < len(SECTORS):
                sectors.append(False)
            sectors[0] = True

            raw_stages = data.get("stages")
            stages = list(raw_stages) if raw_stages is not None else list(defaults["stages"])
            while len(stages) < 15:
                stages.append(False)
            stages[0] = True

            missions = data.get("missions", defaults["missions"])
            sector_progress = data.get("sector_progress", defaults["sector_progress"])

            campaign_completed = bool(data.get("campaign_completed", defaults["campaign_completed"]))
            achievements = list(data.get("achievements", defaults["achievements"]))
            if not isinstance(achievements, list):
                achievements = list(defaults["achievements"])
            else:
                achievements = [str(a) for a in achievements]

            show_crt = bool(data.get("show_crt", False))
            difficulty_mode = int(data.get("difficulty_mode", 1)) % 5
            selected_drone = str(data.get("selected_drone", "striker"))
            selected_skin = int(data.get("selected_skin", 0))

            custom_difficulty = data.get("custom_difficulty", defaults["custom_difficulty"])
            if not isinstance(custom_difficulty, dict):
                custom_difficulty = defaults["custom_difficulty"].copy()
            else:
                custom_difficulty = {k: float(v) if isinstance(v, (int, float)) else defaults["custom_difficulty"][k]
                                     for k, v in custom_difficulty.items()}

            weapon_upgrades = data.get("weapon_upgrades", defaults["weapon_upgrades"])
            if not isinstance(weapon_upgrades, dict):
                weapon_upgrades = defaults["weapon_upgrades"]
            else:
                weapon_upgrades = {str(k): max(0, int(v)) for k, v in weapon_upgrades.items()}

            unlocked_weapons = data.get("unlocked_weapons", defaults["unlocked_weapons"])
            if not isinstance(unlocked_weapons, list):
                unlocked_weapons = list(defaults["unlocked_weapons"])
            else:
                unlocked_weapons = [str(w) for w in unlocked_weapons]

            audio_settings = data.get("audio_settings", defaults["audio_settings"])
            if not isinstance(audio_settings, dict):
                audio_settings = defaults["audio_settings"]

            controller_settings = data.get("controller_settings", defaults["controller_settings"])
            if not isinstance(controller_settings, dict):
                controller_settings = defaults["controller_settings"].copy()
            else:
                controller_settings = {
                    "enabled": bool(controller_settings.get("enabled", True)),
                    "deadzone": max(0.02, min(0.40, float(controller_settings.get("deadzone", 0.12)))),
                    "aim_sensitivity": max(0.2, min(3.0, float(controller_settings.get("aim_sensitivity", 1.0)))),
                    "move_sensitivity": max(0.2, min(2.0, float(controller_settings.get("move_sensitivity", 1.0)))),
                    "vibration_enabled": bool(controller_settings.get("vibration_enabled", True)),
                }

            controller_mappings = data.get("controller_mappings", defaults["controller_mappings"])
            if not isinstance(controller_mappings, dict):
                controller_mappings = defaults["controller_mappings"].copy()

            return {
                "scrap": scrap,
                "coins": legacy_coins,
                "highscore": highscore,
                "play_time": play_time,
                "last_played": last_played,
                "upgrades": upgrades,
                "weapon_upgrades": weapon_upgrades,
                "unlocked_weapons": unlocked_weapons,
                "sectors": sectors,
                "stages": stages,
                "missions": missions,
                "sector_progress": sector_progress,
                "campaign_state": data.get("campaign_state"),
                "campaign_completed": campaign_completed,
                "achievements": achievements,
                "show_crt": show_crt,
                "difficulty_mode": difficulty_mode,
                "custom_difficulty": custom_difficulty,
                "selected_drone": selected_drone,
                "audio_settings": audio_settings,
                "controller_settings": controller_settings,
                "controller_mappings": controller_mappings
            }

        except json.JSONDecodeError as jde:
            logging.error(f"Save file {self.save_path} is corrupted ({jde}). Falling back to safe defaults.")
            return defaults
        except Exception as e:
            logging.error(f"Unexpected error loading save data: {e}. Using safe defaults.")
            return defaults

    def save(self, scrap: Any = 0, coins: int = 0, highscore: int = 0, upgrades: dict = None, sectors: list = None,
             show_crt: bool = False, stages: list = None, difficulty_mode: int = 1,
             missions: dict = None, sector_progress: dict = None,
             bosses_defeated: list = None, campaign_completed: bool = False,
             selected_drone: str = "striker", selected_skin: int = 0,
             weapon_upgrades: dict = None, unlocked_weapons: list = None,
             audio_settings: dict = None, custom_difficulty: dict = None,
             play_time: int = 0, last_played: str = None,
             achievements: list = None, controller_settings: dict = None,
             controller_mappings: dict = None) -> bool:
        """Atomically saves game data using a temporary write & replace pattern."""
        if isinstance(scrap, dict):
            d = scrap
            scrap = d.get("scrap", 0)
            coins = d.get("coins", 0)
            highscore = d.get("highscore", 0)
            upgrades = d.get("upgrades", {})
            sectors = d.get("sectors", [True, False, False, False, False])
            show_crt = d.get("show_crt", False)
            stages = d.get("stages", [True] + [False] * 14)
            difficulty_mode = d.get("difficulty_mode", 1)
            missions = d.get("missions", None)
            sector_progress = d.get("sector_progress", None)
            bosses_defeated = d.get("bosses_defeated", None)
            campaign_completed = d.get("campaign_completed", False)
            selected_drone = d.get("selected_drone", "striker")
            selected_skin = d.get("selected_skin", 0)
            weapon_upgrades = d.get("weapon_upgrades", None)
            unlocked_weapons = d.get("unlocked_weapons", None)
            audio_settings = d.get("audio_settings", None)
            custom_difficulty = d.get("custom_difficulty", None)
            play_time = d.get("play_time", 0)
            last_played = d.get("last_played", None)
            achievements = d.get("achievements", None)
            controller_settings = d.get("controller_settings", None)
            controller_mappings = d.get("controller_mappings", None)

        if stages is None:
            stages = [True] + [False] * 14

        defaults = self.get_default_save_data()
        if sectors is None: sectors = defaults["sectors"]
        if upgrades is None: upgrades = defaults["upgrades"]
        if missions is None: missions = defaults["missions"]
        if sector_progress is None: sector_progress = defaults["sector_progress"]
        if weapon_upgrades is None: weapon_upgrades = defaults["weapon_upgrades"]
        if unlocked_weapons is None: unlocked_weapons = defaults["unlocked_weapons"]
        if audio_settings is None: audio_settings = defaults["audio_settings"]
        if custom_difficulty is None: custom_difficulty = defaults["custom_difficulty"]
        if last_played is None: last_played = time.strftime("%Y-%m-%dT%H:%M:%S")
        if achievements is None: achievements = defaults["achievements"]
        if controller_settings is None: controller_settings = defaults["controller_settings"]
        if controller_mappings is None: controller_mappings = defaults["controller_mappings"]

        save_dict = {
            "scrap": max(0, int(scrap)),
            "coins": max(0, int(coins)),
            "highscore": max(0, int(highscore)),
            "play_time": max(0, int(play_time)),
            "last_played": last_played,
            "upgrades": upgrades,
            "weapon_upgrades": weapon_upgrades,
            "unlocked_weapons": unlocked_weapons,
            "sectors": sectors,
            "stages": stages,
            "missions": missions,
            "sector_progress": sector_progress,
            "campaign_completed": bool(campaign_completed),
            "achievements": list(achievements),
            "show_crt": bool(show_crt),
            "difficulty_mode": int(difficulty_mode) % 5,
            "custom_difficulty": custom_difficulty,
            "selected_drone": str(selected_drone),
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
            logging.error(f"Failed to atomically write save data: {e}")
            if os.path.exists(self.temp_path):
                try: os.remove(self.temp_path)
                except Exception: pass
            return False
