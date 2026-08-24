"""
================================================================================
                    DRONE HUNTER 2D - GAME STATE MANAGER
================================================================================
Centralized state machine coordinator managing game state transitions, validation,
and lifecycle state queries across UI, menus, and combat.
"""

from typing import Optional, Callable, Dict, List
import logging
from src.core.game_state import (
    GameState, STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_PLAYING,
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,
    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED,
    STATE_SETTINGS, STATE_DRONE_SELECT, STATE_SAVE_SELECT, STATE_CUSTOM_DIFFICULTY,
    STATE_CONTROLLER_BINDING, STATE_CONTROLLER_TEST
)

logger = logging.getLogger(__name__)


class GameStateManager:
    """Manages game state transitions, history, and state lifecycle queries."""

    # Set of states representing active gameplay combat
    GAMEPLAY_STATES = {STATE_PLAYING}

    # Set of states representing modal pause or combat interruptions
    PAUSE_STATES = {STATE_PAUSED}

    # Set of states representing non-combat menus and UI screens
    MENU_STATES = {
        STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_DRONE_SELECT,
        STATE_SAVE_SELECT, STATE_SETTINGS, STATE_CUSTOM_DIFFICULTY,
        STATE_CONTROLLER_BINDING, STATE_CONTROLLER_TEST, STATE_MISSION_BRIEFING
    }

    # Set of states representing mission end conditions
    END_STATES = {
        STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,
        STATE_MISSION_COMPLETE, STATE_MISSION_FAILED
    }

    def __init__(self, initial_state: str = STATE_MENU):
        self._current_state: str = initial_state
        self._previous_state: str = initial_state
        self._transition_listeners: List[Callable[[str, str], None]] = []

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def previous_state(self) -> str:
        return self._previous_state

    @previous_state.setter
    def previous_state(self, state: str):
        self._previous_state = state

    def change_state(self, new_state: str) -> bool:
        """Transitions to a new game state and notifies registered listeners."""
        if not new_state:
            return False

        old_state = self._current_state
        if old_state == new_state:
            return True

        self._previous_state = old_state
        self._current_state = new_state

        for listener in self._transition_listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state transition listener: {e}")

        return True

    def register_transition_listener(self, listener: Callable[[str, str], None]):
        """Registers a callback to be invoked on state changes: fn(old_state, new_state)."""
        if listener not in self._transition_listeners:
            self._transition_listeners.append(listener)

    def unregister_transition_listener(self, listener: Callable[[str, str], None]):
        if listener in self._transition_listeners:
            self._transition_listeners.remove(listener)

    # --------------------------------------------------------------------------
    # State Queries
    # --------------------------------------------------------------------------
    def is_state(self, state: str) -> bool:
        return self._current_state == state

    def is_in_gameplay(self) -> bool:
        return self._current_state in self.GAMEPLAY_STATES

    def is_paused(self) -> bool:
        return self._current_state in self.PAUSE_STATES

    def is_in_menu(self) -> bool:
        return self._current_state in self.MENU_STATES

    def is_in_end_screen(self) -> bool:
        return self._current_state in self.END_STATES
