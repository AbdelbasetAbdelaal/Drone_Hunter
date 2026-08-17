"""
================================================================================
                    DRONE HUNTER 2D - DIFFICULTY SYSTEM
================================================================================
Centralized difficulty controller managing stat modifiers across all systems.
"""

from src.data.game_data import (
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_NIGHTMARE,
    DIFFICULTY_NAMES, DIFFICULTY_MODIFIERS
)

class DifficultySystem:
    def __init__(self, current_mode: int = DIFFICULTY_NORMAL):
        self.mode = current_mode % 4

    def cycle(self) -> int:
        """Cycles to the next difficulty level."""
        self.mode = (self.mode + 1) % 4
        return self.mode

    def set_mode(self, mode_idx: int):
        self.mode = mode_idx % 4

    @property
    def current_data(self) -> dict:
        return DIFFICULTY_MODIFIERS.get(self.mode, DIFFICULTY_MODIFIERS[DIFFICULTY_NORMAL])

    @property
    def name(self) -> str:
        return DIFFICULTY_NAMES[self.mode]

    @property
    def hp_multiplier(self) -> float:
        return self.current_data["hp_mult"]

    @property
    def speed_multiplier(self) -> float:
        return self.current_data["speed_mult"]

    @property
    def damage_multiplier(self) -> float:
        return self.current_data["damage_mult"]

    @property
    def drop_rate(self) -> float:
        return self.current_data["powerup_drop_rate"]

    @property
    def score_multiplier(self) -> float:
        return self.current_data["score_mult"]
