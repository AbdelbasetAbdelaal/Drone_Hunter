"""
================================================================================
                    DRONE HUNTER 2D - SAVE CONTROLLER
================================================================================
Coordinates high-level save slot selection, serialization, deserialization, and
state restoration across GameContext, AudioManager, InputManager, and Progression.
"""

import os
import logging
from typing import Optional, Dict, Any
from src.systems.save_system import SaveSystem
from src.core.campaign_state import CampaignState

logger = logging.getLogger(__name__)


class SaveController:
    """Orchestrates save slot loading, persistence, and subsystem configuration sync."""

    def __init__(self, save_system: Optional[SaveSystem] = None, initial_slot: int = 0):
        self.save_system: SaveSystem = save_system if save_system is not None else SaveSystem(slot_index=initial_slot)
        self.selected_save_slot: int = initial_slot

    def select_save_slot(self, slot_num: int, context, audio_manager=None,
                         input_manager=None, achievement_system=None) -> dict:
        """Selects a save slot (accepting 0-indexed or 1-indexed number) and loads it."""
        idx = (slot_num - 1) if (1 <= slot_num <= 3) else slot_num
        idx = max(0, min(2, idx))
        self.selected_save_slot = idx
        return self.load_slot(idx, context, audio_manager, input_manager, achievement_system)

    def load_slot(self, slot_index: int, context, audio_manager=None,
                  input_manager=None, achievement_system=None) -> dict:
        """Restores context and subsystems from the specified save slot."""
        self.selected_save_slot = slot_index
        self.save_system.set_slot(slot_index)

        saved_data = self.save_system.load()

        # Reconstruct authoritative campaign state from save data
        campaign_data = saved_data.get("campaign_state")
        if campaign_data is None:
            # Backward compatibility: reconstruct from legacy fields
            legacy_missions = saved_data.get("missions", {
                "current_sector": 1, "current_mission": 1, "completed": [], "unlocked": ["S1_M1"]
            })
            legacy_sector_progress = saved_data.get("sector_progress", {
                "completed": [], "unlocked": [1]
            })
            current_mission = f"S{legacy_missions.get('current_sector', 1)}_M{legacy_missions.get('current_mission', 1)}"
            campaign_data = {
                "current_mission": current_mission,
                "completed_missions": legacy_missions.get("completed", []),
                "unlocked_missions": legacy_missions.get("unlocked", ["S1_M1"]),
                "completed_sectors": legacy_sector_progress.get("completed", []),
                "unlocked_sectors": legacy_sector_progress.get("unlocked", [1]),
                "campaign_completed": saved_data.get("campaign_completed", False),
                "new_game_plus_count": saved_data.get("new_game_plus_count", 0),
            }
        context.campaign_state = CampaignState.deserialize(campaign_data)
        context._sync_from_campaign_state()

        # Progression & Resources
        context.scrap = saved_data.get("scrap", 0)
        context.coins = saved_data.get("coins", 0)
        context.highscore = saved_data.get("highscore", 0)
        context.upgrade_levels = saved_data.get("upgrades", {})
        context.show_crt = saved_data.get("show_crt", False)
        context.difficulty_mode = saved_data.get("difficulty_mode", 0)
        context.selected_drone = saved_data.get("selected_drone", "striker")
        context.weapon_upgrade_levels = saved_data.get("weapon_upgrades", {})
        context.unlocked_weapons = saved_data.get("unlocked_weapons", ["pulse", "scatter", "missile"])
        context.achievements = saved_data.get("achievements", [])

        if achievement_system:
            achievement_system.unlocked = set(context.achievements)

        if hasattr(context, "update_ng_plus_multipliers"):
            context.update_ng_plus_multipliers()

        # Audio Configuration
        audio = saved_data.get("audio_settings", {})
        if audio and audio_manager:
            audio_manager.set_sound_enabled(audio.get("sound_enabled", True))
            audio_manager.set_sfx_volume(audio.get("sfx_volume", 0.80))
            audio_manager.set_music_volume(audio.get("music_volume", 0.70))
            audio_manager.set_engine_volume(audio.get("engine_volume", 0.35))
            audio_manager.set_master_volume(audio.get("master_volume", 1.0))

        # Controller Configuration
        if input_manager:
            controller_settings = saved_data.get("controller_settings", {})
            if controller_settings and hasattr(input_manager, "update_settings"):
                input_manager.update_settings(controller_settings)

            controller_mappings = saved_data.get("controller_mappings", {})
            if controller_mappings and hasattr(input_manager, "mapping_manager"):
                for key, profile_data in controller_mappings.items():
                    try:
                        from src.input.controller_mapping import ControllerProfile
                        input_manager.mapping_manager.profiles[key] = ControllerProfile.from_dict(profile_data)
                    except Exception:
                        pass

        return saved_data

    def save_current_progress(self, context, audio_manager=None, input_manager=None,
                             achievement_system=None, selected_drone: str = "striker",
                             is_fullscreen: bool = False) -> bool:
        """Serializes current runtime game state and persists to active slot."""
        audio_data = {}
        if audio_manager:
            audio_data = {
                "sound_enabled": audio_manager.sound_enabled,
                "sfx_volume": audio_manager.sfx_volume,
                "music_volume": audio_manager.music_volume,
                "engine_volume": audio_manager.engine_volume,
                "master_volume": audio_manager.master_volume,
            }

        controller_settings = {}
        controller_mappings = {}
        if input_manager:
            if hasattr(input_manager, "get_settings_dict"):
                controller_settings = input_manager.get_settings_dict()
            else:
                controller_settings = {
                    "enabled": getattr(input_manager, "enabled", True),
                    "deadzone": getattr(input_manager, "deadzone", 0.12),
                    "move_sensitivity": getattr(input_manager, "move_sensitivity", 1.0),
                    "aim_sensitivity": getattr(input_manager, "aim_sensitivity", 1.0),
                    "vibration_enabled": getattr(input_manager, "vibration_enabled", True),
                }
            if hasattr(input_manager, "mapping_manager") and hasattr(input_manager.mapping_manager, "profiles"):
                controller_mappings = {
                    k: v.to_dict() for k, v in input_manager.mapping_manager.profiles.items()
                }

        achievements_list = context.achievements
        if achievement_system and hasattr(achievement_system, "unlocked"):
            achievements_list = list(achievement_system.unlocked)

        save_dict = {
            "scrap": getattr(context, "scrap", 0),
            "coins": getattr(context, "coins", 0),
            "highscore": getattr(context, "highscore", 0),
            "upgrades": getattr(context, "upgrade_levels", {}),
            "campaign_state": getattr(context, "campaign_state", CampaignState()).serialize(),
            "show_crt": getattr(context, "show_crt", False),
            "is_fullscreen": is_fullscreen,
            "difficulty_mode": getattr(context, "difficulty_mode", 0),
            "selected_drone": getattr(context, "selected_drone", selected_drone),
            "weapon_upgrades": getattr(context, "weapon_upgrade_levels", {}),
            "unlocked_weapons": getattr(context, "unlocked_weapons", ["pulse", "scatter", "missile"]),
            "achievements": achievements_list,
            "audio_settings": audio_data,
            "controller_settings": controller_settings,
            "controller_mappings": controller_mappings,
        }

        return self.save_system.save(save_dict)
