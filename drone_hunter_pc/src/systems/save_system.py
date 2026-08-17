"""
================================================================================
                    DRONE HUNTER 2D - ATOMIC SAVE SYSTEM
================================================================================
Robust, atomic JSON save & load persistence with data integrity validation,
safe fallback defaults, and error logging.
"""

import os
import json
import logging
from typing import Tuple, Dict, List
from src.data.settings import SAVE_FILE_NAME
from src.data.game_data import SECTORS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SaveSystem:
    def __init__(self, save_filename: str = SAVE_FILE_NAME):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.save_path = os.path.join(base_dir, save_filename)
        self.temp_path = self.save_path + ".tmp"

    def get_default_save_data(self) -> dict:
        return {
            "coins": 0,
            "highscore": 0,
            "upgrades": {
                "battery": 0, "speed": 0, "fire_rate": 0, "emp_recharge": 0,
                "wingman": 0, "cloak": 0, "missiles": 0, "beam": 0,
                "tesla": 0, "cluster": 0, "overdrive": 0
            },
            "sectors": [True, False, False, False, False],
            "stages": [True] + [False] * 14,
            "show_crt": False,
            "difficulty_mode": 1
        }

    def load(self) -> dict:
        """Loads and validates progress data from disk."""
        defaults = self.get_default_save_data()
        if not os.path.exists(self.save_path):
            logging.info(f"Save file not found at {self.save_path}. Using safe defaults.")
            return defaults

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            coins = max(0, int(data.get("coins", defaults["coins"])))
            highscore = max(0, int(data.get("highscore", defaults["highscore"])))
            
            # Merge upgrades dictionary with defaults
            upgrades = defaults["upgrades"].copy()
            loaded_upgrades = data.get("upgrades", {})
            if isinstance(loaded_upgrades, dict):
                for k, v in loaded_upgrades.items():
                    if k in upgrades:
                        try: upgrades[k] = max(0, int(v))
                        except (ValueError, TypeError): pass

            # Validate sectors list
            sectors = list(data.get("sectors", defaults["sectors"]))
            while len(sectors) < len(SECTORS):
                sectors.append(False)
            sectors[0] = True # First sector is always unlocked

            # Validate stages list (15 stages across 5 sectors)
            stages = list(data.get("stages", defaults["stages"]))
            while len(stages) < 15:
                stages.append(False)
            stages[0] = True # First stage is always unlocked

            show_crt = bool(data.get("show_crt", False))
            difficulty_mode = int(data.get("difficulty_mode", 1)) % 4

            return {
                "coins": coins,
                "highscore": highscore,
                "upgrades": upgrades,
                "sectors": sectors,
                "stages": stages,
                "show_crt": show_crt,
                "difficulty_mode": difficulty_mode
            }

        except json.JSONDecodeError as jde:
            logging.error(f"Save file {self.save_path} is corrupted ({jde}). Falling back to safe defaults.")
            return defaults
        except Exception as e:
            logging.error(f"Unexpected error loading save data: {e}. Using safe defaults.")
            return defaults

    def save(self, coins: int, highscore: int, upgrades: dict, sectors: list, show_crt: bool = False, stages: list = None, difficulty_mode: int = 1) -> bool:
        """Atomically saves game data using a temporary write & replace pattern."""
        if stages is None:
            stages = [True] + [False] * 14

        save_dict = {
            "coins": max(0, int(coins)),
            "highscore": max(0, int(highscore)),
            "upgrades": upgrades,
            "sectors": sectors,
            "stages": stages,
            "show_crt": bool(show_crt),
            "difficulty_mode": int(difficulty_mode)
        }

        try:
            # Step 1: Write to temporary file
            with open(self.temp_path, "w", encoding="utf-8") as f:
                json.dump(save_dict, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            # Step 2: Atomic replace
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
