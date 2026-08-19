"""
================================================================================
                DRONE HUNTER 2D - ENCOUNTER SYSTEM (PHASE 2A & 2B)
================================================================================
Lightweight data-driven encounter director managing structured combat tests
and sequential enemy wave introductions with safe world-space spawn placement.
Supports Scout Recon Encounter (Phase 2A) and Shooter Positioning Encounter (Phase 2B).
"""

import math
import random
import pygame
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    SCOUT_SCORE, SHOOTER_SCORE, HEAVY_SCORE
)
from src.entities.enemy import Enemy

# Default Phase 2A Scout Introduction Encounter
SCOUT_INTRO_ENCOUNTER = {
    "name": "Scout Recon Encounter",
    "enemy_type": TARGET_TYPE_SCOUT,
    "count": 3,
    "spawn_delay": 1.2,
    "respawn_delay": 1.0,
}

# Phase 2B Shooter Introduction Encounter
SHOOTER_INTRO_ENCOUNTER = {
    "name": "Shooter Positioning Encounter",
    "enemy_type": TARGET_TYPE_SHOOTER,
    "count": 1,
    "spawn_delay": 1.5,
    "respawn_delay": 1.0,
}

# Phase 2C Heavy Introduction Encounter
HEAVY_INTRO_ENCOUNTER = {
    "name": "Heavy Target Priority Encounter",
    "enemy_type": TARGET_TYPE_HEAVY,
    "count": 1,
    "spawn_delay": 1.5,
    "respawn_delay": 1.0,
}


class EncounterSystem:
    """Manages deterministic sequential encounters with spawn suppression."""
    def __init__(self, config: dict = None, enabled: bool = True):
        self.config = config if config is not None else SCOUT_INTRO_ENCOUNTER
        self.enabled = enabled
        self.state = "idle" # idle, waiting, active, complete
        self.total_count = self.config.get("count", 3)
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.timer = 0.0
        self.min_spawn_distance = 500.0

    def set_encounter(self, config: dict):
        """Swaps the active encounter configuration and resets state."""
        self.config = config
        self.total_count = self.config.get("count", 1)
        self.reset()

    def start(self, config: dict = None):
        """Explicitly starts the encounter into WAITING state."""
        if config is not None:
            self.config = config
            self.total_count = self.config.get("count", 1)
        self.state = "waiting"
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.timer = self.config.get("spawn_delay", 1.5)

    def reset(self):
        """Resets the encounter back to IDLE state."""
        self.state = "idle"
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.timer = 0.0

    @property
    def is_active(self) -> bool:
        """True while the encounter is actively running and not yet complete."""
        return self.enabled and (self.state in ("waiting", "active"))

    @property
    def is_complete(self) -> bool:
        """True when all encounter enemies have been eliminated."""
        return self.state == "complete"

    @property
    def is_suppressing_spawner(self) -> bool:
        """Suppresses legacy random spawns while encounter is active."""
        return self.is_active

    def _find_spawn_position(self, player_pos: tuple[float, float]) -> tuple[float, float]:
        """Calculates a safe spawn position >= min_spawn_distance from player within arena."""
        px, py = player_pos
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(self.min_spawn_distance, self.min_spawn_distance + 280.0)
            sx = px + math.cos(angle) * dist
            sy = py + math.sin(angle) * dist

            # Clamp to world borders with margin
            sx = max(80.0, min(WORLD_WIDTH - 80.0, sx))
            sy = max(80.0, min(WORLD_HEIGHT - 80.0, sy))

            actual_dist = math.hypot(sx - px, sy - py)
            if actual_dist >= self.min_spawn_distance:
                return (sx, sy)

        # Fallback to sector edge
        fallback_x = 120.0 if px > WORLD_WIDTH // 2 else WORLD_WIDTH - 120.0
        fallback_y = 120.0 if py > WORLD_HEIGHT // 2 else WORLD_HEIGHT - 120.0
        return (fallback_x, fallback_y)

    def update(self, dt: float, ctx) -> bool:
        """Updates encounter progression timer and triggers enemy spawns."""
        if not self.enabled or self.state not in ("waiting", "active"):
            return False

        p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

        if self.state == "waiting":
            self.timer -= dt
            if self.timer <= 0:
                if self.spawned_count < self.total_count:
                    # Spawn next enemy in sequence
                    spawn_pos = self._find_spawn_position(p_pos)
                    enemy_type = self.config.get("enemy_type", TARGET_TYPE_SHOOTER)
                    enemy = Enemy(enemy_type=enemy_type, pos=spawn_pos, sector_idx=ctx.current_sector_idx)
                    ctx.target_group.add(enemy)

                    self.active_enemy = enemy
                    self.spawned_count += 1
                    self.state = "active"
                else:
                    self.state = "complete"

        elif self.state == "active":
            # Check if current active enemy is eliminated
            if self.active_enemy is None or not self.active_enemy.alive or self.active_enemy not in ctx.target_group:
                self.eliminated_count += 1
                self.active_enemy = None

                if self.spawned_count < self.total_count:
                    self.state = "waiting"
                    self.timer = self.config.get("respawn_delay", 1.0)
                else:
                    self.state = "complete"

        return self.is_complete
