"""
Forwarding settings and game data for full compatibility.
"""
from src.data.settings import *
from src.data.game_data import *

# Legacy state constants for state machine
STATE_MENU = "menu"
STATE_SECTOR_SELECT = "sector_select"
STATE_HANGAR = "hangar"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_LEVEL_CLEAR = "level_clear"
STATE_VICTORY = "victory"
