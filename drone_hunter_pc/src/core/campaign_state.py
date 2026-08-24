"""
===============================================================================
                     DRONE HUNTER 2D - CAMPAIGN STATE
===============================================================================
Authoritative single source of truth for campaign progression.

Owns:
    - current_mission
    - completed_missions
    - unlocked_missions
    - completed_sectors
    - unlocked_sectors
    - bosses_defeated
    - campaign_completed
    - new_game_plus_count

Derives:
    - current_sector_idx  (from current_mission)
    - current_sub_level   (from current_mission)
"""

from typing import List, Optional


class CampaignState:
    """Authoritative campaign progression state."""

    def __init__(self):
        self._current_mission: str = "S1_M1"
        self._completed_missions: List[str] = []
        self._unlocked_missions: List[str] = ["S1_M1"]
        self._completed_sectors: List[int] = []
        self._unlocked_sectors: List[int] = [1]
        self._bosses_defeated: List[str] = []
        self._campaign_completed: bool = False
        self._new_game_plus_count: int = 0

    # ------------------------------------------------------------------
    # Authoritative properties
    # ------------------------------------------------------------------
    @property
    def current_mission(self) -> str:
        return self._current_mission

    @property
    def completed_missions(self) -> List[str]:
        return list(self._completed_missions)

    @property
    def unlocked_missions(self) -> List[str]:
        return list(self._unlocked_missions)

    @property
    def completed_sectors(self) -> List[int]:
        return list(self._completed_sectors)

    @property
    def unlocked_sectors(self) -> List[int]:
        return list(self._unlocked_sectors)

    @property
    def bosses_defeated(self) -> List[str]:
        return list(self._bosses_defeated)

    @property
    def campaign_completed(self) -> bool:
        return self._campaign_completed

    @property
    def new_game_plus_count(self) -> int:
        return self._new_game_plus_count

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------
    @property
    def current_sector_idx(self) -> int:
        try:
            parts = self._current_mission.split("_")
            return int(parts[0][1:]) - 1
        except (IndexError, ValueError):
            return 0

    @property
    def current_sub_level(self) -> int:
        try:
            parts = self._current_mission.split("_")
            return int(parts[1][1:])
        except (IndexError, ValueError):
            return 1

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------
    def set_current_mission(self, mission_id: str) -> None:
        self._current_mission = mission_id

    def set_current_sector_and_stage(self, sector_idx: int, sub_level: int) -> None:
        self._current_mission = f"S{sector_idx + 1}_M{sub_level}"

    def complete_mission(self, mission_id: str) -> None:
        if mission_id not in self._completed_missions:
            self._completed_missions.append(mission_id)
        self._unlock_next_mission(mission_id)

    def unlock_mission(self, mission_id: str) -> None:
        if mission_id not in self._unlocked_missions:
            self._unlocked_missions.append(mission_id)

    def complete_sector(self, sector_id: int) -> None:
        if sector_id not in self._completed_sectors:
            self._completed_sectors.append(sector_id)
        if sector_id < 5 and (sector_id + 1) not in self._unlocked_sectors:
            self._unlocked_sectors.append(sector_id + 1)
            self._unlock_sector_first_mission(sector_id + 1)

    def unlock_sector(self, sector_id: int) -> None:
        if sector_id not in self._unlocked_sectors:
            self._unlocked_sectors.append(sector_id)

    def record_boss_defeat(self, boss_id: str) -> None:
        if boss_id not in self._bosses_defeated:
            self._bosses_defeated.append(boss_id)

    def mark_campaign_complete(self) -> None:
        self._campaign_completed = True

    def start_new_game_plus(self) -> None:
        self._new_game_plus_count += 1
        self._completed_missions.clear()
        self._completed_sectors.clear()
        self._unlocked_sectors = [1]
        self._unlocked_missions = ["S1_M1"]
        self._bosses_defeated.clear()
        self._campaign_completed = False
        self._current_mission = "S1_M1"

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def is_mission_completed(self, mission_id: str) -> bool:
        return mission_id in self._completed_missions

    def is_mission_unlocked(self, mission_id: str) -> bool:
        return mission_id in self._unlocked_missions

    def is_sector_completed(self, sector_id: int) -> bool:
        return sector_id in self._completed_sectors

    def is_sector_unlocked(self, sector_id: int) -> bool:
        return sector_id in self._unlocked_sectors

    def is_boss_defeated(self, boss_id: str) -> bool:
        return boss_id in self._bosses_defeated

    def get_next_mission(self, current_mission_id: str) -> Optional[str]:
        try:
            parts = current_mission_id.split("_")
            sector = int(parts[0][1:])
            mission = int(parts[1][1:])
        except (IndexError, ValueError):
            return None

        if mission < 5:
            next_id = f"S{sector}_M{mission + 1}"
            if self.is_mission_unlocked(next_id):
                return next_id
        elif sector < 5:
            next_sector = sector + 1
            if self.is_sector_unlocked(next_sector):
                return f"S{next_sector}_M1"
        return None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self) -> List[str]:
        errors = []
        for m_id in self._completed_missions:
            if m_id not in self._unlocked_missions:
                errors.append(f"Completed mission {m_id} is not unlocked")
        for s_id in self._completed_sectors:
            if s_id not in self._unlocked_sectors:
                errors.append(f"Completed sector {s_id} is not unlocked")
        return errors

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def serialize(self) -> dict:
        return {
            "current_mission": self._current_mission,
            "completed_missions": list(self._completed_missions),
            "unlocked_missions": list(self._unlocked_missions),
            "completed_sectors": list(self._completed_sectors),
            "unlocked_sectors": list(self._unlocked_sectors),
            "bosses_defeated": list(self._bosses_defeated),
            "campaign_completed": self._campaign_completed,
            "new_game_plus_count": self._new_game_plus_count,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "CampaignState":
        state = cls()
        state._current_mission = data.get("current_mission", "S1_M1")
        state._completed_missions = list(data.get("completed_missions", []))
        state._unlocked_missions = list(data.get("unlocked_missions", ["S1_M1"]))
        state._completed_sectors = list(data.get("completed_sectors", []))
        state._unlocked_sectors = list(data.get("unlocked_sectors", [1]))
        state._bosses_defeated = list(data.get("bosses_defeated", []))
        state._campaign_completed = bool(data.get("campaign_completed", False))
        state._new_game_plus_count = int(data.get("new_game_plus_count", 0))
        return state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _unlock_next_mission(self, mission_id: str) -> None:
        try:
            parts = mission_id.split("_")
            sector = int(parts[0][1:])
            mission = int(parts[1][1:])
        except (IndexError, ValueError):
            return

        if mission < 5:
            next_id = f"S{sector}_M{mission + 1}"
            if next_id not in self._unlocked_missions:
                self._unlocked_missions.append(next_id)
        else:
            if sector not in self._completed_sectors:
                self._completed_sectors.append(sector)
            if sector < 5:
                next_sector = sector + 1
                if next_sector not in self._unlocked_sectors:
                    self._unlocked_sectors.append(next_sector)
                next_mission = f"S{next_sector}_M1"
                if next_mission not in self._unlocked_missions:
                    self._unlocked_missions.append(next_mission)
            else:
                self._campaign_completed = True

    def _unlock_sector_first_mission(self, sector_id: int) -> None:
        first_mission = f"S{sector_id}_M1"
        if first_mission not in self._unlocked_missions:
            self._unlocked_missions.append(first_mission)
