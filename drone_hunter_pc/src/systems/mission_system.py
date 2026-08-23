"""
===============================================================================
                     DRONE HUNTER 2D - MISSION SYSTEM
==============================================================================
Phase 5: Structured mission system driving content progression, objectives,
unlocks, and rewards across 5 sectors and 25 missions.
"""

from typing import Optional, Dict, Any, List
from src.core.game_context import GameContext
from src.systems.combat_director import CombatDirector
from src.data.mission_data import (
    get_mission_data, get_sector_data,
    OBJECTIVE_DESTROY_ALL, OBJECTIVE_SURVIVE, OBJECTIVE_COMPLETE_ENCOUNTERS,
    OBJECTIVE_ASSAULT, MISSION_REWARDS, SECTOR_BONUS, SIDE_OBJECTIVE_BONUS
)
import logging

STATE_LOCKED = "locked"
STATE_AVAILABLE = "available"
STATE_ACTIVE = "active"
STATE_COMPLETED = "completed"

SIDE_OBJ_DESCRIPTIONS = {
    "collect_data_cores": "Collect {} Data Cores",
    "no_damage_taken": "Take No Damage",
    "time_limit": "Complete within {} seconds",
    "precision_strikes": "{} Precision Strikes (critical hits)",
}

SIDE_OBJ_TYPE_NAMES = {
    "collect_data_cores": "Collect Data Cores",
    "no_damage_taken": "No Damage Taken",
    "time_limit": "Time Limit",
    "precision_strikes": "Precision Strikes",
}

class MissionSystem:
    def __init__(self):
        self.active_mission_id: Optional[str] = None
        self.active_mission_data: Optional[dict] = None
        self.survive_timer: float = 0.0
        self.state: str = STATE_AVAILABLE
        self.is_mission_success: bool = False
        self.side_objectives_progress: Dict[str, Any] = {}
        self._mission_elapsed: float = 0.0
        self._precision_strike_count: int = 0
        self._player_taken_damage: bool = False

    def start_mission(self, ctx: GameContext, mission_id: str, director: CombatDirector, boss_system=None, objective_system=None):
        """Initializes a mission, configuring the director and setting objectives."""
        self.active_mission_data = get_mission_data(mission_id)
        if not self.active_mission_data:
            logging.error(f"MissionSystem: Cannot start unknown mission {mission_id}")
            return

        self.active_mission_id = mission_id
        self.state = STATE_ACTIVE
        self.is_mission_success = False
        self._mission_elapsed = 0.0
        self._precision_strike_count = 0
        self._player_taken_damage = False

        ctx.missions["current_sector"] = self.active_mission_data["sector_id"]
        ctx.missions["current_mission"] = self.active_mission_data["mission_number"]
        ctx.boss_rating_timer = 0.0
        ctx.latest_boss_rating = None

        if boss_system:
            boss_system.reset()

        # Initialize Ground Objective Assault
        if objective_system:
            objective_system.start_objective_for_mission(self.active_mission_data, ctx)

        # Initialize side objectives progress tracking
        self.side_objectives_progress = {}
        side_objs = self.active_mission_data.get("side_objectives", [])
        for so in side_objs:
            so_type = so.get("type", "")
            so_value = so.get("value", 0)
            if so_type == "collect_data_cores":
                self.side_objectives_progress[so_type] = {"target": so_value, "current": 0, "completed": False}
            elif so_type == "no_damage_taken":
                self.side_objectives_progress[so_type] = {"target": so_value, "completed": True}
            elif so_type == "time_limit":
                self.side_objectives_progress[so_type] = {"target": so_value, "elapsed": 0.0, "completed": True}
            elif so_type == "precision_strikes":
                self.side_objectives_progress[so_type] = {"target": so_value, "current": 0, "completed": False}

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

        director.start()

    def update(self, dt: float, ctx: GameContext, director: CombatDirector, boss_system=None, objective_system=None) -> bool:
        """
        Updates mission progression and checks for victory.
        Returns True if the mission just concluded successfully.
        """
        if self.state != STATE_ACTIVE:
            return False

        self._mission_elapsed += dt

        # Track no_damage_taken
        if self._player_taken_damage:
            if "no_damage_taken" in self.side_objectives_progress:
                self.side_objectives_progress["no_damage_taken"]["completed"] = False

        # 1. Primary: Check Ground Objective Assault Progression
        if objective_system and objective_system.is_active:
            obj_done = objective_system.update(dt, ctx)
            if obj_done:
                self._check_side_objectives_on_success(ctx)
                self._trigger_success(ctx)
                return True

        # 2. Legacy / Boss Standalone Mode Handling (preserves BossSystem for optional/unit tests)
        elif boss_system and boss_system.has_boss_for_mission(self.active_mission_id):
            if boss_system.state == "idle":
                if director.state == "complete":
                    boss_system.start_boss_for_mission(self.active_mission_id, ctx)
            else:
                boss_done = boss_system.update(dt, ctx)
                if boss_done:
                    self._check_side_objectives_on_success(ctx)
                    self._trigger_success(ctx)
                    return True
            return False

        # 3. Fallback Objectives (Survive / Clear)
        obj = self.active_mission_data["objective"]
        living_enemies = [e for e in ctx.target_group if getattr(e, "alive", False) and not getattr(e, "is_obstacle", False)]

        if obj == OBJECTIVE_SURVIVE:
            self.survive_timer -= dt
            if self.survive_timer <= 0:
                self._check_side_objectives_on_success(ctx)
                self._trigger_success(ctx)
                return True

        elif obj in (OBJECTIVE_COMPLETE_ENCOUNTERS, OBJECTIVE_DESTROY_ALL, OBJECTIVE_ASSAULT):
            if director.state == "complete" and len(living_enemies) == 0:
                self._check_side_objectives_on_success(ctx)
                self._trigger_success(ctx)
                return True

        return False

    def _check_side_objectives_on_success(self, ctx: GameContext):
        """Award bonus scrap for any completed side objectives."""
        bonus_total = 0
        for so_type, progress in self.side_objectives_progress.items():
            if progress.get("completed", False):
                bonus = SIDE_OBJECTIVE_BONUS.get(so_type, 0)
                bonus_total += bonus
        if bonus_total > 0:
            ctx.scrap += bonus_total
            logging.debug(f"MissionSystem: Awarded {bonus_total} bonus scrap for side objectives")

    def record_player_damage(self):
        """Call when the player takes damage to update no_damage_taken objective."""
        self._player_taken_damage = True
        if "no_damage_taken" in self.side_objectives_progress:
            self.side_objectives_progress["no_damage_taken"]["completed"] = False

    def record_precision_strike(self):
        """Call when the player lands a precision/critical hit."""
        self._precision_strike_count += 1
        if "precision_strikes" in self.side_objectives_progress:
            prog = self.side_objectives_progress["precision_strikes"]
            prog["current"] = self._precision_strike_count
            if self._precision_strike_count >= prog["target"]:
                prog["completed"] = True

    def record_data_core_collected(self):
        """Call when the player collects a data core pickup."""
        if "collect_data_cores" in self.side_objectives_progress:
            prog = self.side_objectives_progress["collect_data_cores"]
            prog["current"] = prog.get("current", 0) + 1
            if prog["current"] >= prog["target"]:
                prog["completed"] = True

    def get_side_objective_status(self) -> List[Dict[str, Any]]:
        """Returns a list of side objective status dicts for UI rendering."""
        result = []
        side_objs = self.active_mission_data.get("side_objectives", []) if self.active_mission_data else []
        for so in side_objs:
            so_type = so.get("type", "")
            so_value = so.get("value", 0)
            prog = self.side_objectives_progress.get(so_type, {})
            if so_type == "collect_data_cores":
                current = prog.get("current", 0)
                completed = prog.get("completed", False)
                desc = SIDE_OBJ_DESCRIPTIONS["collect_data_cores"].format(so_value)
                result.append({
                    "type": so_type,
                    "description": desc,
                    "completed": completed,
                    "progress_text": f"{current} / {so_value}",
                })
            elif so_type == "no_damage_taken":
                completed = prog.get("completed", True)
                desc = SIDE_OBJ_DESCRIPTIONS["no_damage_taken"]
                result.append({
                    "type": so_type,
                    "description": desc,
                    "completed": completed,
                    "progress_text": "ACTIVE" if completed else "FAILED",
                })
            elif so_type == "time_limit":
                elapsed = prog.get("elapsed", 0.0)
                target = so_value
                completed = prog.get("completed", True)
                desc = SIDE_OBJ_DESCRIPTIONS["time_limit"].format(target)
                result.append({
                    "type": so_type,
                    "description": desc,
                    "completed": completed,
                    "progress_text": f"{int(elapsed)}s / {target}s",
                })
            elif so_type == "precision_strikes":
                current = prog.get("current", 0)
                completed = prog.get("completed", False)
                desc = SIDE_OBJ_DESCRIPTIONS["precision_strikes"].format(so_value)
                result.append({
                    "type": so_type,
                    "description": desc,
                    "completed": completed,
                    "progress_text": f"{current} / {so_value}",
                })
        return result

    def get_mission_summary(self) -> Dict[str, Any]:
        """Returns a full mission summary including side objective status for UI."""
        m_data = self.active_mission_data
        if not m_data:
            return {}
        side_status = self.get_side_objective_status()
        all_completed = all(s.get("completed", False) for s in side_status) if side_status else False
        return {
            "id": m_data.get("id"),
            "name": m_data.get("name"),
            "sector_id": m_data.get("sector_id"),
            "mission_number": m_data.get("mission_number"),
            "difficulty": m_data.get("difficulty", 1),
            "lore": m_data.get("lore", ""),
            "objective": m_data.get("objective"),
            "duration": m_data.get("duration"),
            "state": self.state,
            "is_success": self.is_mission_success,
            "side_objectives": side_status,
            "all_side_objectives_completed": all_completed,
            "side_objectives_progress": dict(self.side_objectives_progress),
        }

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
                next_id = f"S{s_id}_M{m_num+1}"
                if next_id not in ctx.missions["unlocked"]:
                    ctx.missions["unlocked"].append(next_id)
            else:
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
