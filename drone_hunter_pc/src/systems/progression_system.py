"""
================================================================================
                    DRONE HUNTER 2D - PROGRESSION SYSTEM
================================================================================
Tracks sector campaigns, sub-level stages, target scores, unlocks, and
campaign victory state transitions.
"""

from typing import Tuple, Optional
from src.data.game_data import SECTORS
from src.core.campaign_state import CampaignState


class ProgressionSystem:
    def __init__(self, campaign_state: Optional[CampaignState] = None):
        if campaign_state is None:
            campaign_state = CampaignState()
        self.campaign_state: CampaignState = campaign_state

    @property
    def unlocked_sectors(self) -> list:
        return self.campaign_state.unlocked_sectors

    @property
    def unlocked_missions(self) -> list:
        return self.campaign_state.unlocked_missions

    def get_current_stage_target_score(self, sector_idx: int, sub_level: int) -> int:
        """Retrieves target clear score for the active stage."""
        if 0 <= sector_idx < len(SECTORS):
            sec = SECTORS[sector_idx]
            stages = sec.get("stages", [])
            if 0 < sub_level <= len(stages):
                return stages[sub_level - 1]["score"]
            return sec.get("base_target_score", 5000)
        return 5000

    def is_stage_unlocked(self, sector_idx: int, sub_level: int) -> bool:
        mission_id = f"S{sector_idx + 1}_M{sub_level}"
        return self.campaign_state.is_mission_unlocked(mission_id)

    def is_sector_unlocked(self, sector_idx: int) -> bool:
        return self.campaign_state.is_sector_unlocked(sector_idx + 1)

    def unlock_next_stage(self, current_sector_idx: int, current_sub_level: int) -> Tuple[int, int, bool]:
        """
        Advances stage and sector upon clearing.
        Returns: (next_sector_idx, next_sub_level, is_campaign_victory)
        """
        current_mission = f"S{current_sector_idx + 1}_M{current_sub_level}"
        self.campaign_state.complete_mission(current_mission)

        next_sub_level = current_sub_level + 1
        next_sector_idx = current_sector_idx
        is_campaign_victory = False

        if next_sub_level > 5:
            next_sub_level = 1
            next_sector_idx += 1
            
            # Check Campaign Victory (Completed all 5 sectors)
            if next_sector_idx >= len(SECTORS):
                is_campaign_victory = True
                next_sector_idx = len(SECTORS) - 1
                self.campaign_state.mark_campaign_complete()
            else:
                self.campaign_state.unlock_sector(next_sector_idx + 1)

        if not is_campaign_victory:
            next_mission = f"S{next_sector_idx + 1}_M{next_sub_level}"
            self.campaign_state.unlock_mission(next_mission)

        return next_sector_idx, next_sub_level, is_campaign_victory

    # -------------------------------------------------------------------------
    # Phase 4 Player Progression
    # -------------------------------------------------------------------------
    def add_scrap(self, ctx, amount: int):
        """Adds scrap to the active context."""
        ctx.scrap += max(0, amount)

    def purchase_upgrade(self, ctx, category: str) -> bool:
        """Attempts to purchase an upgrade. Returns True if successful."""
        from src.data.game_data import UPGRADE_COSTS, MAX_UPGRADE_LEVEL
        
        current_level = ctx.upgrade_levels.get(category, 1)
        if current_level >= MAX_UPGRADE_LEVEL:
            return False
            
        cost = UPGRADE_COSTS.get(current_level, 999999)
        if ctx.scrap >= cost:
            ctx.scrap -= cost
            ctx.upgrade_levels[category] = current_level + 1
            return True
        return False

    def apply_to_player(self, ctx, player):
        """Applies Phase 4 upgrades to the player."""
        # 1. HULL
        # Level 1: 225, Level 2: 250, Level 3: 275, Level 4: 300, Level 5: 325
        hull_level = ctx.upgrade_levels.get("hull", 1)
        player.max_health = 225.0 + ((hull_level - 1) * 25.0)
        # Safely clamp current health so it doesn't exceed new max
        player.health = min(player.health, player.max_health)
        
        # 2. ENERGY
        # Level 1: 100, Level 2: 115, Level 3: 130, Level 4: 145, Level 5: 160
        energy_level = ctx.upgrade_levels.get("energy", 1)
        player.max_energy = 100.0 + ((energy_level - 1) * 15.0)
        player.energy = min(player.energy, player.max_energy)
        
        # 3. WEAPON SYSTEM (Multipliers applied when shooting)
        # Level 1: 1.0, Level 2: 1.05, Level 3: 1.10, Level 4: 1.15, Level 5: 1.20
        weapon_level = ctx.upgrade_levels.get("weapon", 1)
        player.weapon_effectiveness = 1.0 + ((weapon_level - 1) * 0.05)
        
        # 4. MOBILITY (Speed Multiplier)
        # Level 1: 1.0, Level 2: 1.05, Level 3: 1.10, Level 4: 1.15, Level 5: 1.20
        mobility_level = ctx.upgrade_levels.get("mobility", 1)
        player.max_speed = 220.0 * (1.0 + ((mobility_level - 1) * 0.05))
