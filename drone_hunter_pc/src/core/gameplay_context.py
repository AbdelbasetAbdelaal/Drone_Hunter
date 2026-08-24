"""
================================================================================
         DRONE HUNTER 2D - GAMEPLAY & INPUT HANDLING CONTEXTS
================================================================================
Lightweight runtime context containers that group subsystem dependencies and
callbacks explicitly, eliminating dependency explosion and decoupling controllers
from the monolithic Game root.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Dict, Tuple
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.game_context import GameContext


@dataclass
class GameplayContext:
    """Explicit runtime container for GameplayController dependencies."""
    context: GameContext
    progression: Optional[Any] = None
    particle_manager: Optional[Any] = None
    camera: Optional[Any] = None
    spawner: Optional[Any] = None
    encounter_system: Optional[Any] = None
    combat_director: Optional[Any] = None
    mission_system: Optional[Any] = None
    boss_system: Optional[Any] = None
    objective_system: Optional[Any] = None
    combat_system: Optional[Any] = None
    background: Optional[Any] = None
    audio_manager: Optional[Any] = None
    input_manager: Optional[Any] = None
    achievement_system: Optional[Any] = None
    # Narrow callbacks
    save_callback: Optional[Callable[[], Any]] = None
    get_canvas_mouse_pos_func: Optional[Callable[[], Tuple[int, int]]] = None
    start_mission_callback: Optional[Callable[[str], Any]] = None
    start_stage_callback: Optional[Callable[[int, int], Any]] = None

    def __post_init__(self):
        while isinstance(self.context, GameplayContext):
            self.context = self.context.context
        if self.context is None:
            self.context = GameContext()


@dataclass
class InputHandlingContext:
    """Explicit runtime container for InputController dependencies and callbacks."""
    context: GameContext
    input_manager: Any
    audio_manager: Optional[Any] = None
    ui_rects_cache: Dict[str, Any] = field(default_factory=dict)
    win_w: int = SCREEN_WIDTH
    win_h: int = SCREEN_HEIGHT
    is_fullscreen: bool = False
    previous_state: Optional[str] = None
    pending_mission_id: str = "S1_M1"
    # Narrow callbacks
    save_callback: Optional[Callable[[], Any]] = None
    start_mission_callback: Optional[Callable[[str], Any]] = None
    select_save_slot_callback: Optional[Callable[[int], Any]] = None
    buy_upgrade_callback: Optional[Callable[[str], Any]] = None
    toggle_fullscreen_callback: Optional[Callable[[], Any]] = None
    resize_window_callback: Optional[Callable[[int, int], Any]] = None
    get_next_mission_id_callback: Optional[Callable[[], Optional[str]]] = None
    set_previous_state_callback: Optional[Callable[[str], Any]] = None
    set_pending_mission_id_callback: Optional[Callable[[str], Any]] = None
    quit_callback: Optional[Callable[[], Any]] = None

    def __post_init__(self):
        while isinstance(self.context, (GameplayContext, InputHandlingContext)):
            self.context = self.context.context
        if self.context is None:
            self.context = GameContext()
