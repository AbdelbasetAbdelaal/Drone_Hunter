"""
================================================================================
                    DRONE HUNTER 2D - SHARED GAME CONTEXT
================================================================================
Centralized state container storing active sprite groups, progression indices,
scores, combo counters, time scale, camera shake, and sound dispatchers.
"""

import random
import pygame
from typing import Optional, List, Dict
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.campaign_state import CampaignState
from src.data.game_data import (
    DIFFICULTY_NORMAL, DIFFICULTY_MODIFIERS, SECTORS, DIFFICULTY_CUSTOM,
    CUSTOM_DIFFICULTY_DEFAULTS
)
from src.core.game_state import GameState, STATE_PLAYING


class GameContext:
    def __init__(self):
        # State
        self.state: str = GameState.MAIN_MENU.value

        # Sprite Groups
        self.player_group = pygame.sprite.GroupSingle()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.target_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.hazard_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        # Managers & Systems (injected by Game)
        self.particle_manager = None
        self.audio_manager = None
        self.save_system = None
        self.spawner = None
        self.wave_manager = None
        self.background = None

        # Player reference
        self.player = None

        # Progression & Save Data
        self.scrap: int = 0
        self.highscore: int = 0
        self.upgrade_levels: Dict[str, int] = {
            "hull": 1, "energy": 1, "weapon": 1, "mobility": 1,
            "battery": 0, "speed": 0, "fire_rate": 0, "emp_recharge": 0,
            "wingman": 0, "cloak": 0, "missiles": 0, "beam": 0,
            "tesla": 0, "cluster": 0, "overdrive": 0
        }
        self.weapon_upgrade_levels: Dict[str, int] = {}
        self.unlocked_weapons: List[str] = ["pulse", "scatter", "missile"]
        
        # Authoritative campaign state
        self.campaign_state: CampaignState = CampaignState()
        
        # Achievement Tracking
        self.achievements: List[str] = []
        self.achievement_popups: List[dict] = []
        self.total_kills: int = 0
        self.emp_kills: int = 0
        self.overdrive_kills: int = 0
        self.mission_damage_taken: float = 0.0
        self.mission_start_time: float = 0.0
        self.mission_elapsed_time: float = 0.0

        # New Game+ State Multipliers
        self._ng_plus_scrap_mult: float = 1.0
        self._ng_plus_enemy_hp_mult: float = 1.0

        self.show_crt: bool = False

        # Gameplay & Difficulty State
        self.difficulty_mode: int = DIFFICULTY_NORMAL
        self.custom_difficulty_settings: dict = CUSTOM_DIFFICULTY_DEFAULTS.copy()
        self.current_wave: int = 1

        # Scores & Combo
        self.level_score: int = 0
        self.total_score: int = 0
        self.combo_count: int = 1
        self.combo_timer: float = 0.0

        # Wave Announcement
        self.wave_announcement_timer: float = 0.0
        self.last_wave: int = 1

        # Bullet-Time & Time-Scale Mechanism (Fixes Bug 2)
        self.slowmo_timer: float = 0.0
        self.time_scale: float = 1.0
        self.hit_stop_timer: float = 0.0
        self.hit_stop_duration: float = 0.0

        # Visual FX & Camera Shake
        self.damage_flash_timer: float = 0.0
        self.screen_shake_time: float = 0.0
        self.screen_shake_intensity: float = 0.0

        # Spawning Timers
        self.obstacle_timer: float = 0.0
        self.next_obstacle_spawn: float = random.uniform(3.5, 6.0)
        self.hazard_timer: float = 0.0
        self.next_hazard_spawn: float = random.uniform(6.0, 10.0)
        self.ambient_timer: float = 0.0

        # UI State
        self.is_diff_dropdown_open: bool = False

    # ------------------------------------------------------------------
    # Campaign state delegation properties (Derived / Forwarded)
    # ------------------------------------------------------------------
    @property
    def current_sector_idx(self) -> int:
        return self.campaign_state.current_sector_idx

    @current_sector_idx.setter
    def current_sector_idx(self, value: int):
        self.campaign_state.set_current_sector_and_stage(value, self.current_sub_level)

    @property
    def current_sub_level(self) -> int:
        return self.campaign_state.current_sub_level

    @current_sub_level.setter
    def current_sub_level(self, value: int):
        self.campaign_state.set_current_sector_and_stage(self.current_sector_idx, value)

    @property
    def campaign_completed(self) -> bool:
        return self.campaign_state.campaign_completed

    @campaign_completed.setter
    def campaign_completed(self, value: bool):
        if value:
            self.campaign_state.mark_campaign_complete()

    @property
    def new_game_plus_count(self) -> int:
        return self.campaign_state.new_game_plus_count

    @new_game_plus_count.setter
    def new_game_plus_count(self, value: int):
        self.campaign_state.new_game_plus_count = int(value)

    @property
    def unlocked_sectors(self) -> List[int]:
        return self.campaign_state.unlocked_sectors

    @property
    def difficulty_data(self) -> dict:
        if self.difficulty_mode == DIFFICULTY_CUSTOM:
            custom = CUSTOM_DIFFICULTY_DEFAULTS.copy()
            custom.update(self.custom_difficulty_settings)
            custom["name"] = "CUSTOM"
            return custom
        return DIFFICULTY_MODIFIERS.get(self.difficulty_mode, DIFFICULTY_MODIFIERS[DIFFICULTY_NORMAL])

    def trigger_shake(self, intensity: float = 6.0, duration: float = 0.25):
        """Triggers dynamic camera screen shake."""
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
        self.screen_shake_time = max(self.screen_shake_time, duration)

    def trigger_slowmo(self, duration: float = 5.0):
        """Activates bullet-time slow motion across enemy systems."""
        self.slowmo_timer = duration
        self.time_scale = 0.40

    def trigger_hit_stop(self, duration: float = 0.05):
        """Triggers a brief hit-stop freeze for impactful combat feedback."""
        self.hit_stop_timer = max(self.hit_stop_timer, duration)
        self.hit_stop_duration = max(self.hit_stop_duration, duration)

    def add_score(self, pts: int):
        """Adds points with combo multiplier and difficulty multiplier."""
        score_mult = self.difficulty_data.get("score_mult", 1.0)
        effective_pts = int(pts * self.combo_count * score_mult)

        self.level_score += effective_pts
        self.total_score += effective_pts
        self.combo_count = min(99, self.combo_count + 1)
        self.combo_timer = 4.0

        if self.total_score > self.highscore:
            self.highscore = self.total_score

        if self.combo_count > 1 and self.particle_manager and hasattr(self, 'audio_manager') and self.audio_manager:
            self.audio_manager.play_combo()

        return effective_pts

    def update_timers(self, dt: float):
        """Updates combo, slowmo, screen shake, and damage flash timers."""
        # Slow-Mo Time Scale
        if self.slowmo_timer > 0:
            self.slowmo_timer -= dt
            if self.slowmo_timer <= 0:
                self.slowmo_timer = 0.0
                self.time_scale = 1.0
        else:
            self.time_scale = 1.0

        # Combo Streak
        if self.combo_count > 1:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 1

        # Screen Shake
        if self.screen_shake_time > 0:
            self.screen_shake_time -= dt
            if self.screen_shake_time <= 0:
                self.screen_shake_time = 0.0
                self.screen_shake_intensity = 0.0

        # Damage Flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)

    def update_ng_plus_multipliers(self):
        self._ng_plus_scrap_mult = 1.0 + 0.10 * self.new_game_plus_count
        self._ng_plus_enemy_hp_mult = 1.0 + 0.25 * self.new_game_plus_count

    @property
    def ng_plus_scrap_mult(self) -> float:
        return self._ng_plus_scrap_mult

    @property
    def ng_plus_enemy_hp_mult(self) -> float:
        return self._ng_plus_enemy_hp_mult

    def get_shake_offset(self) -> tuple[int, int]:
        """Calculates randomized pixel offset during active screen shake."""
        if self.screen_shake_time > 0 and self.screen_shake_intensity > 0:
            ox = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            oy = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            return ox, oy
        return 0, 0
