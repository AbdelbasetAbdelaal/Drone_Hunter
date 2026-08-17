"""
================================================================================
                    DRONE HUNTER 2D - PROGRESSION SYSTEM
================================================================================
Tracks sector campaigns, sub-level stages, target scores, unlocks, and
campaign victory state transitions.
"""

from typing import Tuple
from src.data.game_data import SECTORS

class ProgressionSystem:
    def __init__(self, unlocked_sectors: list[bool] = None, unlocked_stages: list[bool] = None):
        self.unlocked_sectors = unlocked_sectors if unlocked_sectors is not None else [True, False, False, False, False]
        self.unlocked_stages = unlocked_stages if unlocked_stages is not None else [True] + [False] * 14

    def get_current_stage_target_score(self, sector_idx: int, sub_level: int) -> int:
        """Retrieves target clear score for the active stage."""
        if 0 <= sector_idx < len(SECTORS):
            sec = SECTORS[sector_idx]
            stages = sec.get("stages", [])
            if 0 < sub_level <= len(stages):
                return stages[sub_level - 1]["score"]
            return sec.get("base_target_score", 5000)
        return 5000

    def is_stage_unlocked(self, sector_idx: int, sub_level: int) -> bool:
        flat_idx = sector_idx * 3 + (sub_level - 1)
        if 0 <= flat_idx < len(self.unlocked_stages):
            return self.unlocked_stages[flat_idx]
        return False

    def is_sector_unlocked(self, sector_idx: int) -> bool:
        if 0 <= sector_idx < len(self.unlocked_sectors):
            return self.unlocked_sectors[sector_idx]
        return False

    def unlock_next_stage(self, current_sector_idx: int, current_sub_level: int) -> Tuple[int, int, bool]:
        """
        Advances stage and sector upon clearing.
        Returns: (next_sector_idx, next_sub_level, is_campaign_victory)
        """
        next_sub_level = current_sub_level + 1
        next_sector_idx = current_sector_idx
        is_campaign_victory = False

        if next_sub_level > 3:
            next_sub_level = 1
            next_sector_idx += 1
            
            # Check Campaign Victory (Completed all 5 sectors)
            if next_sector_idx >= len(SECTORS):
                is_campaign_victory = True
                # Clamp sector index to final sector
                next_sector_idx = len(SECTORS) - 1
            else:
                if next_sector_idx < len(self.unlocked_sectors):
                    self.unlocked_sectors[next_sector_idx] = True

        if not is_campaign_victory:
            flat_idx = next_sector_idx * 3 + (next_sub_level - 1)
            if flat_idx < len(self.unlocked_stages):
                self.unlocked_stages[flat_idx] = True

        return next_sector_idx, next_sub_level, is_campaign_victory
