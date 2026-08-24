"""
===============================================================================
                    DRONE HUNTER 2D - ACHIEVEMENT SYSTEM
===============================================================================
Tracks achievement progress, fires unlock events, and provides hooks for
persistence and UI notification.
"""


class AchievementSystem:
    ACHIEVEMENTS = {
        "first_kill": {
            "name": "First Blood",
            "description": "Get your first kill",
            "icon": "🎯",
        },
        "first_boss": {
            "name": "Boss Slayer",
            "description": "Defeat your first boss",
            "icon": "👑",
        },
        "combo_10": {
            "name": "Combo x10",
            "description": "Reach a 10x combo streak",
            "icon": "🔥",
        },
        "combo_25": {
            "name": "Combo x25",
            "description": "Reach a 25x combo streak",
            "icon": "💥",
        },
        "no_damage_mission": {
            "name": "Untouchable",
            "description": "Complete a mission without taking damage",
            "icon": "🛡️",
        },
        "speed_run": {
            "name": "Speed Demon",
            "description": "Complete a mission in under 2 minutes",
            "icon": "⚡",
        },
        "all_sectors_cleared": {
            "name": "Sector Clear",
            "description": "Clear all 5 sectors",
            "icon": "🌌",
        },
        "all_weapons_unlocked": {
            "name": "Arsenal Master",
            "description": "Unlock all weapons",
            "icon": "🔫",
        },
        "max_upgrades": {
            "name": "Fully Loaded",
            "description": "Max out all base upgrades",
            "icon": "⭐",
        },
        "first_emp_kill": {
            "name": "EMP Shock",
            "description": "Get a kill with an EMP blast",
            "icon": "💫",
        },
        "first_overdrive_kill": {
            "name": "Overdrive Kill",
            "description": "Get a kill while in Overdrive",
            "icon": "🚀",
        },
        "survivalist": {
            "name": "Survivalist",
            "description": "Complete a survival mission",
            "icon": "⏳",
        },
    }

    def __init__(self):
        self.unlocked = set()
        self._callbacks = []

    def register_callback(self, cb):
        """Register a callback fired when an achievement is unlocked."""
        self._callbacks.append(cb)

    def unlock(self, achievement_id):
        """Unlock an achievement and fire callbacks if newly unlocked."""
        if achievement_id not in self.ACHIEVEMENTS or achievement_id in self.unlocked:
            return False
        self.unlocked.add(achievement_id)
        for cb in self._callbacks:
            try:
                cb(achievement_id, self.ACHIEVEMENTS[achievement_id])
            except Exception:
                pass
        return True

    def check_all(self, ctx, game=None):
        """Evaluate all continuously trackable achievement conditions."""
        if not hasattr(ctx, "achievements"):
            return
        unlocked = ctx.achievements

        if "first_kill" not in unlocked and getattr(ctx, "total_kills", 0) >= 1:
            self.unlock("first_kill")

        if "first_boss" not in unlocked and len(getattr(ctx, "bosses_defeated", [])) > 0:
            self.unlock("first_boss")

        if "combo_10" not in unlocked and getattr(ctx, "combo_count", 1) >= 10:
            self.unlock("combo_10")

        if "combo_25" not in unlocked and getattr(ctx, "combo_count", 1) >= 25:
            self.unlock("combo_25")

        if "all_sectors_cleared" not in unlocked:
            if len(getattr(ctx, "sector_progress", {}).get("completed", [])) >= 5:
                self.unlock("all_sectors_cleared")

        if "all_weapons_unlocked" not in unlocked:
            all_wpn = set(
                [
                    "pulse", "scatter", "missile",
                    "rapid", "plasma", "rail", "barrage",
                    "beam", "tesla", "cluster", "emp",
                ]
            )
            if all_wpn.issubset(set(getattr(ctx, "unlocked_weapons", []))):
                self.unlock("all_weapons_unlocked")

        if "max_upgrades" not in unlocked:
            upg = getattr(ctx, "upgrade_levels", {})
            if upg and all(v >= 5 for v in upg.values()):
                self.unlock("max_upgrades")

        if "first_emp_kill" not in unlocked and getattr(ctx, "emp_kills", 0) >= 1:
            self.unlock("first_emp_kill")

        if "first_overdrive_kill" not in unlocked and getattr(ctx, "overdrive_kills", 0) >= 1:
            self.unlock("first_overdrive_kill")

    def check_mission_complete(self, ctx, game=None):
        """Evaluate mission-specific achievement conditions after success."""
        if not hasattr(ctx, "achievements"):
            return
        unlocked = ctx.achievements

        if (
            "no_damage_mission" not in unlocked
            and getattr(ctx, "mission_damage_taken", 0) == 0
            and getattr(ctx, "mission_start_time", 0) > 0
        ):
            self.unlock("no_damage_mission")

        if (
            "speed_run" not in unlocked
            and getattr(ctx, "mission_start_time", 0) > 0
            and getattr(ctx, "mission_elapsed_time", 0) < 120
        ):
            self.unlock("speed_run")

        if "survivalist" not in unlocked:
            try:
                from src.data.mission_data import get_mission_data
                missions = getattr(ctx, "missions", {})
                for m_id in missions.get("completed", []):
                    md = get_mission_data(m_id)
                    if md and md.get("objective") == "survive":
                        self.unlock("survivalist")
                        break
            except Exception:
                pass
