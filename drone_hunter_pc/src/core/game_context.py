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

class _SyncedDict(dict):
    """Dict that syncs mutations back to a callback."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sync_callback = None

    def set_sync_callback(self, callback):
        self._sync_callback = callback

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self._sync_callback:
            self._sync_callback(key, value)

    def update(self, *args, **kwargs):
        if args:
            other = args[0]
            if hasattr(other, 'items'):
                for k, v in other.items():
                    self[k] = v
            else:
                for k, v in other:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v


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
        self.weapon_upgrade_levels: Dict[str, int] = {}
        self.unlocked_weapons: List[str] = ["pulse", "scatter", "missile"]
        
        # Authoritative campaign state
        self.campaign_state: CampaignState = CampaignState()
        
        # Legacy compatibility views (synced from campaign_state)
        self._missions_dict = _SyncedDict({
            "current_sector": 1,
            "current_mission": 1,
            "completed": self.campaign_state._completed_missions,
            "unlocked": self.campaign_state._unlocked_missions,
        })
        self._missions_dict.set_sync_callback(self._on_missions_sync)

        self._sector_progress_dict = _SyncedDict({
            "completed": self.campaign_state._completed_sectors,
            "unlocked": self.campaign_state._unlocked_sectors,
        })
        self._sector_progress_dict.set_sync_callback(self._on_sector_progress_sync)
        
        self.campaign_completed: bool = self.campaign_state._campaign_completed
        
        # Achievement Tracking
        self.achievements: List[str] = []
        self.achievement_popups: List[dict] = []
        self.total_kills: int = 0
        self.emp_kills: int = 0
        self.overdrive_kills: int = 0
        self.mission_damage_taken: float = 0.0
        self.mission_start_time: float = 0.0
        self.mission_elapsed_time: float = 0.0

        # New Game+ State
        self.new_game_plus_count: int = self.campaign_state._new_game_plus_count
        self._ng_plus_scrap_mult: float = 1.0
        self._ng_plus_enemy_hp_mult: float = 1.0

        self.show_crt: bool = False

        # Gameplay & Difficulty State
        self.difficulty_mode: int = DIFFICULTY_NORMAL
        self.custom_difficulty_settings: dict = CUSTOM_DIFFICULTY_DEFAULTS.copy()
        self.current_sector_idx: int = 0
        self.current_sub_level: int = 1
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

    def _on_missions_sync(self, key, value):
        cs = self.campaign_state
        md = self._missions_dict
        if "current_sector" in md and "current_mission" in md:
            try:
                cs.set_current_sector_and_stage(md["current_sector"] - 1, md["current_mission"])
            except Exception:
                pass
        if "completed" in md:
            cs._completed_missions = list(md["completed"]) if isinstance(md["completed"], list) else []
        if "unlocked" in md:
            cs._unlocked_missions = list(md["unlocked"]) if isinstance(md["unlocked"], list) else []
        # Share list references so mutations are visible through both paths
        dict.__setitem__(md, "completed", cs._completed_missions)
        dict.__setitem__(md, "unlocked", cs._unlocked_missions)

    def _on_sector_progress_sync(self, key, value):
        cs = self.campaign_state
        sp = self._sector_progress_dict
        if "completed" in sp:
            cs._completed_sectors = list(sp["completed"]) if isinstance(sp["completed"], list) else []
        if "unlocked" in sp:
            cs._unlocked_sectors = list(sp["unlocked"]) if isinstance(sp["unlocked"], list) else []
        dict.__setitem__(sp, "completed", cs._completed_sectors)
        dict.__setitem__(sp, "unlocked", cs._unlocked_sectors)

    def _sync_from_campaign_state(self) -> None:
        """Sync legacy fields from authoritative campaign_state."""
        cs = self.campaign_state
        self.current_sector_idx = cs.current_sector_idx
        self.current_sub_level = cs.current_sub_level
        self.campaign_completed = cs.campaign_completed
        self.new_game_plus_count = cs.new_game_plus_count
        self._missions_dict = _SyncedDict({
            "current_sector": cs.current_sector_idx + 1,
            "current_mission": cs.current_sub_level,
            "completed": cs._completed_missions,
            "unlocked": cs._unlocked_missions,
        })
        self._missions_dict.set_sync_callback(self._on_missions_sync)
        self._sector_progress_dict = _SyncedDict({
            "completed": cs._completed_sectors,
            "unlocked": cs._unlocked_sectors,
        })
        self._sector_progress_dict.set_sync_callback(self._on_sector_progress_sync)

    def _sync_to_campaign_state(self) -> None:
        """Sync legacy mutations back to campaign_state."""
        cs = self.campaign_state
        md = self._missions_dict
        sp = self._sector_progress_dict
        if "current_sector" in md and "current_mission" in md:
            cs.set_current_sector_and_stage(md["current_sector"] - 1, md["current_mission"])
        for m_id in md.get("completed", []):
            cs.complete_mission(m_id)
        for m_id in md.get("unlocked", []):
            cs.unlock_mission(m_id)
        for s_id in sp.get("completed", []):
            cs.complete_sector(s_id)
        for s_id in sp.get("unlocked", []):
            cs.unlock_sector(s_id)
        if self.campaign_completed:
            cs.mark_campaign_complete()
        cs._new_game_plus_count = self.new_game_plus_count

    @property
    def missions(self) -> dict:
        return self._missions_dict

    @missions.setter
    def missions(self, value: dict):
        if not isinstance(value, dict):
            return
        self._missions_dict.clear()
        self._missions_dict.update(value)
        self._on_missions_sync(None, None)

    @property
    def sector_progress(self) -> dict:
        return self._sector_progress_dict

    @sector_progress.setter
    def sector_progress(self, value: dict):
        if not isinstance(value, dict):
            return
        self._sector_progress_dict.clear()
        self._sector_progress_dict.update(value)
        self._on_sector_progress_sync(None, None)

    # ------------------------------------------------------------------
    # Campaign state delegation properties
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
        return self.campaign_state._new_game_plus_count

    @new_game_plus_count.setter
    def new_game_plus_count(self, value: int):
        self.campaign_state._new_game_plus_count = int(value)

    @property
    def unlocked_sectors(self) -> List[bool]:
        cs = self.campaign_state
        return [i in cs._unlocked_sectors for i in range(1, 6)]

    @unlocked_sectors.setter
    def unlocked_sectors(self, value: List[bool]):
        cs = self.campaign_state
        cs._unlocked_sectors = [i + 1 for i, v in enumerate(value) if v]

    @property
    def unlocked_stages(self) -> List[bool]:
        cs = self.campaign_state
        result = [True] + [False] * 14
        for idx in range(15):
            sector = idx // 3
            stage = (idx % 3) + 1
            mission_id = f"S{sector + 1}_M{stage}"
            result[idx] = mission_id in cs._unlocked_missions
        return result

    @unlocked_stages.setter
    def unlocked_stages(self, value: List[bool]):
        cs = self.campaign_state
        for idx, unlocked in enumerate(value):
            if unlocked:
                sector = idx // 3
                stage = (idx % 3) + 1
                mission_id = f"S{sector + 1}_M{stage}"
                if mission_id not in cs._unlocked_missions:
                    cs._unlocked_missions.append(mission_id)

    @property
    def missions(self) -> dict:
        cs = self.campaign_state
        return {
            "current_sector": cs.current_sector_idx + 1,
            "current_mission": cs.current_sub_level,
            "completed": cs._completed_missions,
            "unlocked": cs._unlocked_missions,
        }

    @missions.setter
    def missions(self, value: dict):
        if not isinstance(value, dict):
            return
        cs = self.campaign_state
        if "current_sector" in value and "current_mission" in value:
            cs.set_current_sector_and_stage(value["current_sector"] - 1, value["current_mission"])
        if "completed" in value:
            cs._completed_missions = list(value["completed"])
        if "unlocked" in value:
            cs._unlocked_missions = list(value["unlocked"])

    @property
    def sector_progress(self) -> dict:
        cs = self.campaign_state
        return {
            "completed": cs._completed_sectors,
            "unlocked": cs._unlocked_sectors,
        }

    @sector_progress.setter
    def sector_progress(self, value: dict):
        if not isinstance(value, dict):
            return
        cs = self.campaign_state
        if "completed" in value:
            cs._completed_sectors = list(value["completed"])
        if "unlocked" in value:
            cs._unlocked_sectors = list(value["unlocked"])

    @property
    def missions(self) -> dict:
        return self._missions_dict

    @missions.setter
    def missions(self, value: dict):
        if not isinstance(value, dict):
            return
        self._missions_dict.clear()
        self._missions_dict.update(value)
        self._on_missions_sync(None, None)

    @property
    def sector_progress(self) -> dict:
        return self._sector_progress_dict

    @sector_progress.setter
    def sector_progress(self, value: dict):
        if not isinstance(value, dict):
            return
        self._sector_progress_dict.clear()
        self._sector_progress_dict.update(value)
        self._on_sector_progress_sync(None, None)

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
        earned_coins = max(1, effective_pts // 20)

        self.level_score += effective_pts
        self.total_score += effective_pts
        self.coins += earned_coins
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
