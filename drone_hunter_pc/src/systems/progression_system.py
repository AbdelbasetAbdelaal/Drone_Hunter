"""
================================================================================
                    DRONE HUNTER 2D - PROGRESSION SYSTEM
================================================================================
Tracks sector campaigns, sub-level stages, target scores, unlocks, and
campaign victory state transitions.
"""

from typing import Tuple
from src.data.game_data import SECTORS

class ProgressionSystem:
    def __init__(self, unlocked_sectors: list[bool] = None, unlocked_stages: list[bool] = None):
        self.unlocked_sectors = unlocked_sectors if unlocked_sectors is not None else [True, False, False, False, False]
        self.unlocked_stages = unlocked_stages if unlocked_stages is not None else [True] + [False] * 14

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
        flat_idx = sector_idx * 3 + (sub_level - 1)
        if 0 <= flat_idx < len(self.unlocked_stages):
            return self.unlocked_stages[flat_idx]
        return False

    def is_sector_unlocked(self, sector_idx: int) -> bool:
        if 0 <= sector_idx < len(self.unlocked_sectors):
            return self.unlocked_sectors[sector_idx]
        return False

    def unlock_next_stage(self, current_sector_idx: int, current_sub_level: int) -> Tuple[int, int, bool]:
        """
        Advances stage and sector upon clearing.
        Returns: (next_sector_idx, next_sub_level, is_campaign_victory)
        """
        next_sub_level = current_sub_level + 1
        next_sector_idx = current_sector_idx
        is_campaign_victory = False

        if next_sub_level > 3:
            next_sub_level = 1
            next_sector_idx += 1
            
            # Check Campaign Victory (Completed all 5 sectors)
            if next_sector_idx >= len(SECTORS):
                is_campaign_victory = True
                # Clamp sector index to final sector
                next_sector_idx = len(SECTORS) - 1
            else:
                if next_sector_idx < len(self.unlocked_sectors):
                    self.unlocked_sectors[next_sector_idx] = True

        if not is_campaign_victory:
            flat_idx = next_sector_idx * 3 + (next_sub_level - 1)
            if flat_idx < len(self.unlocked_stages):
                self.unlocked_stages[flat_idx] = True

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

        # 5. VISUAL DRONE VARIANT (0: Striker, 1: Phantom, 2: Titan, 3: Velocity, 4: Aegis Quad)
        if getattr(ctx, "selected_skin_override", None) is not None:
            player.skin_theme = ctx.selected_skin_override
        else:
            avg_level = sum(ctx.upgrade_levels.values()) / max(1, len(ctx.upgrade_levels))
            overall_tier = getattr(ctx, "drone_tier", int(round(avg_level)))
            player.skin_theme = max(0, min(4, overall_tier - 1))
