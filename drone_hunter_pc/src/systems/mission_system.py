"""
================================================================================
                    DRONE HUNTER 2D - MISSION SYSTEM
================================================================================
Phase 5: Structured mission system driving content progression, objectives,
unlocks, and rewards across 5 sectors and 25 missions.
"""

from typing import Optional
from src.core.game_context import GameContext
from src.systems.combat_director import CombatDirector
from src.data.mission_data import (
    get_mission_data, get_sector_data,
    OBJECTIVE_DESTROY_ALL, OBJECTIVE_SURVIVE, OBJECTIVE_COMPLETE_ENCOUNTERS,
    MISSION_REWARDS, SECTOR_BONUS
)
import logging

STATE_LOCKED = "locked"
STATE_AVAILABLE = "available"
STATE_ACTIVE = "active"
STATE_COMPLETED = "completed"

class MissionSystem:
    def __init__(self):
        self.active_mission_id: Optional[str] = None
        self.active_mission_data: Optional[dict] = None
        self.survive_timer: float = 0.0
        self.state: str = STATE_AVAILABLE # state of the current mission tracking
        self.is_mission_success: bool = False

    def start_mission(self, ctx: GameContext, mission_id: str, director: CombatDirector, boss_system=None):
        """Initializes a mission, configuring the director and setting objectives."""
        self.active_mission_data = get_mission_data(mission_id)
        if not self.active_mission_data:
            logging.error(f"MissionSystem: Cannot start unknown mission {mission_id}")
            return
            
        self.active_mission_id = mission_id
        self.state = STATE_ACTIVE
        self.is_mission_success = False
        
        ctx.missions["current_sector"] = self.active_mission_data["sector_id"]
        ctx.missions["current_mission"] = self.active_mission_data["mission_number"]
        
        if boss_system:
            boss_system.reset()

        # Configure Objective
        obj = self.active_mission_data["objective"]
        if obj == OBJECTIVE_SURVIVE:
            self.survive_timer = float(self.active_mission_data.get("duration", 60.0))
            
        # Configure Director Sequence
        seq = self.active_mission_data.get("encounter_sequence", [])
        if obj == OBJECTIVE_SURVIVE:
            director.set_mission_sequence(seq, loop=True)
        else:
            director.set_mission_sequence(seq, loop=False)
            
        if ctx.audio_manager:
            ctx.audio_manager.play_mission_start()
            
        # Start the director
        director.start()

    def update(self, dt: float, ctx: GameContext, director: CombatDirector, boss_system=None) -> bool:
        """
        Updates mission progression and checks for victory.
        Returns True if the mission just concluded successfully.
        """
        if self.state != STATE_ACTIVE:
            return False
            
        # Check for Boss Mission Handling
        if boss_system and boss_system.has_boss_for_mission(self.active_mission_id):
            if boss_system.state == "idle":
                # Prelude encounters run first; when complete, trigger boss intro
                if director.state == "complete":
                    boss_system.start_boss_for_mission(self.active_mission_id, ctx)
            else:
                boss_done = boss_system.update(dt, ctx)
                if boss_done:
                    self._trigger_success(ctx)
                    return True
            return False
            
        obj = self.active_mission_data["objective"]
        
        if obj == OBJECTIVE_SURVIVE:
            self.survive_timer -= dt
            if self.survive_timer <= 0:
                self._trigger_success(ctx)
                return True
                
        elif obj == OBJECTIVE_COMPLETE_ENCOUNTERS:
            if director.state == "complete":
                self._trigger_success(ctx)
                return True
                
        elif obj == OBJECTIVE_DESTROY_ALL:
            if director.state == "complete" and len(ctx.target_group) == 0:
                self._trigger_success(ctx)
                return True
                
        return False

    def _trigger_success(self, ctx: GameContext):
        """Handles reward dispensing, unlock propagation, and marking complete."""
        self.state = STATE_COMPLETED
        self.is_mission_success = True
        
        m_id = self.active_mission_id
        m_data = self.active_mission_data
        
        # Check if first-time completion
        if m_id not in ctx.missions["completed"]:
            ctx.missions["completed"].append(m_id)
            
            # Award Mission Scrap
            diff = m_data.get("difficulty", 1)
            reward = MISSION_REWARDS.get(diff, 150)
            ctx.scrap += reward
            
            # Unlock next mission
            s_id = m_data["sector_id"]
            m_num = m_data["mission_number"]
            
            if m_num < 5:
                # Unlock next mission in same sector
                next_id = f"S{s_id}_M{m_num+1}"
                if next_id not in ctx.missions["unlocked"]:
                    ctx.missions["unlocked"].append(next_id)
            else:
                # Sector Complete!
                if s_id not in ctx.sector_progress["completed"]:
                    ctx.sector_progress["completed"].append(s_id)
                    s_bonus = SECTOR_BONUS.get(s_id, 0)
                    ctx.scrap += s_bonus
                    
                    if s_id < 5:
                        next_sector = s_id + 1
                        if next_sector not in ctx.sector_progress["unlocked"]:
                            ctx.sector_progress["unlocked"].append(next_sector)
                        next_mission = f"S{next_sector}_M1"
                        if next_mission not in ctx.missions["unlocked"]:
                            ctx.missions["unlocked"].append(next_mission)
                    else:
                        # Final Boss (Sector 5 Mission 5) defeated -> Campaign Complete!
                        ctx.campaign_completed = True

        if ctx.audio_manager:
            if getattr(ctx, "campaign_completed", False):
                ctx.audio_manager.play_victory()
            else:
                ctx.audio_manager.play_mission_complete()


    def trigger_failure(self):
        """Handles player death without granting completion rewards."""
        self.state = STATE_COMPLETED
        self.is_mission_success = False
        
    def get_mission_state(self, ctx: GameContext, mission_id: str) -> str:
        """Returns the LOCKED, AVAILABLE, or COMPLETED state for UI."""
        if mission_id in ctx.missions["completed"]:
            return STATE_COMPLETED
        elif mission_id in ctx.missions["unlocked"]:
            return STATE_AVAILABLE
        else:
            return STATE_LOCKED
