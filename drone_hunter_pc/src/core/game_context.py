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
from src.data.game_data import DIFFICULTY_NORMAL, DIFFICULTY_MODIFIERS, SECTORS
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
        self.coins: int = 0 # Legacy
        self.highscore: int = 0
        self.upgrade_levels: Dict[str, int] = {
            "hull": 1, "energy": 1, "weapon": 1, "mobility": 1,
            "battery": 0, "speed": 0, "fire_rate": 0, "emp_recharge": 0,
            "wingman": 0, "cloak": 0, "missiles": 0, "beam": 0,
            "tesla": 0, "cluster": 0, "overdrive": 0
        }
        self.unlocked_sectors: List[bool] = [True, False, False, False, False]
        self.unlocked_stages: List[bool] = [True] + [False] * 14
        
        # Phase 5 progression
        self.missions = {
            "current_sector": 1,
            "current_mission": 1,
            "completed": [],
            "unlocked": ["S1_M1"]
        }
        self.sector_progress = {
            "completed": [],
            "unlocked": [1]
        }
        
        # Phase 6 Boss & Endgame State
        self.bosses_defeated: List[str] = []
        self.campaign_completed: bool = False
        
        self.show_crt: bool = False

        # Gameplay & Difficulty State
        self.difficulty_mode: int = DIFFICULTY_NORMAL
        self.current_sector_idx: int = 0
        self.current_sub_level: int = 1
        self.current_wave: int = 1

        # Scores & Combo
        self.level_score: int = 0
        self.total_score: int = 0
        self.combo_count: int = 1
        self.combo_timer: float = 0.0

        # Bullet-Time & Time-Scale Mechanism (Fixes Bug 2)
        self.slowmo_timer: float = 0.0
        self.time_scale: float = 1.0
        self.hit_stop_timer: float = 0.0
        self.hit_stop_duration: float = 0.0

        # Visual FX & Camera Shake
        self.damage_flash_timer: float = 0.0
        self.screen_shake_time: float = 0.0
        self.screen_shake_intensity: float = 0.0
        self.boss_defeat_timer: float = 0.0

        # Spawning Timers
        self.obstacle_timer: float = 0.0
        self.next_obstacle_spawn: float = random.uniform(3.5, 6.0)
        self.hazard_timer: float = 0.0
        self.next_hazard_spawn: float = random.uniform(6.0, 10.0)
        self.ambient_timer: float = 0.0

        # UI State
        self.is_diff_dropdown_open: bool = False

    @property
    def difficulty_data(self) -> dict:
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
        earned_coins = max(1, effective_pts // 20)

        self.level_score += effective_pts
        self.total_score += effective_pts
        self.coins += earned_coins
        self.combo_count = min(99, self.combo_count + 1)
        self.combo_timer = 4.0

        if self.total_score > self.highscore:
            self.highscore = self.total_score

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

    def get_shake_offset(self) -> tuple[int, int]:
        """Calculates randomized pixel offset during active screen shake."""
        if self.screen_shake_time > 0 and self.screen_shake_intensity > 0:
            ox = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            oy = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            return ox, oy
        return 0, 0
