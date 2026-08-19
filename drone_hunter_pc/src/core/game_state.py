"""
================================================================================
                    DRONE HUNTER 2D - GAME STATE MACHINE
================================================================================
Defines explicit states for the game loop state machine.
"""

from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = "menu"
    SECTOR_SELECT = "sector_select"
    HANGAR = "hangar"
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_CLEAR = "level_clear"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    # Phase 5 Additions
    MISSION_BRIEFING = "mission_briefing"
    MISSION_COMPLETE = "mission_complete"
    MISSION_FAILED = "mission_failed"
    SETTINGS = "settings"

# String constants for compatibility
STATE_MENU = GameState.MAIN_MENU.value
STATE_SECTOR_SELECT = GameState.SECTOR_SELECT.value
STATE_HANGAR = GameState.HANGAR.value
STATE_PLAYING = GameState.PLAYING.value
STATE_PAUSED = GameState.PAUSED.value
STATE_LEVEL_CLEAR = GameState.LEVEL_CLEAR.value
STATE_GAME_OVER = GameState.GAME_OVER.value
STATE_VICTORY = GameState.VICTORY.value
STATE_MISSION_BRIEFING = GameState.MISSION_BRIEFING.value
STATE_MISSION_COMPLETE = GameState.MISSION_COMPLETE.value
STATE_MISSION_FAILED = GameState.MISSION_FAILED.value
STATE_SETTINGS = GameState.SETTINGS.value
