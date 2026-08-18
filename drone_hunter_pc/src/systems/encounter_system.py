"""
================================================================================
                DRONE HUNTER 2D - ENCOUNTER SYSTEM (PHASE 2A)
================================================================================
Lightweight data-driven encounter director managing structured combat tests
and sequential enemy wave introductions with safe world-space spawn placement.
"""

import math
import random
import pygame
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import TARGET_TYPE_SCOUT, SCOUT_SCORE
from src.entities.enemy import Enemy

# Default Phase 2A Scout Introduction Encounter
SCOUT_INTRO_ENCOUNTER = {
    "name": "Scout Recon Encounter",
    "enemy_type": TARGET_TYPE_SCOUT,
    "count": 3,
    "spawn_delay": 1.2,
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

    def start(self):
        """Starts or resets the encounter to initial waiting state."""
        self.state = "waiting"
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.timer = self.config.get("spawn_delay", 1.2)

    def reset(self):
        self.start()

    @property
    def is_active(self) -> bool:
        """True while the encounter is actively running and not yet complete."""
        return self.enabled and (self.state in ("waiting", "active"))

    @property
    def is_complete(self) -> bool:
        """True once all encounter enemies have been spawned and eliminated."""
        return self.state == "complete"

    @property
    def is_suppressing_spawner(self) -> bool:
        """True during the encounter to prevent legacy random wave spawning."""
        return self.is_active

    def get_safe_spawn_pos(self, player_pos: tuple[float, float]) -> tuple[float, float]:
        """Calculates world-space spawn location along perimeter with minimum safe distance (>=500px)."""
        px, py = player_pos
        # Candidate edge spawn points around the arena perimeter
        candidates = [
            (random.uniform(200, WORLD_WIDTH - 200), 80.0),                  # North edge
            (random.uniform(200, WORLD_WIDTH - 200), WORLD_HEIGHT - 80.0),   # South edge
            (80.0, random.uniform(150, WORLD_HEIGHT - 150)),                 # West edge
            (WORLD_WIDTH - 80.0, random.uniform(150, WORLD_HEIGHT - 150)),  # East edge
        ]
        valid = [c for c in candidates if math.hypot(c[0] - px, c[1] - py) >= self.min_spawn_distance]
        if valid:
            return random.choice(valid)
        # Fallback to candidate furthest from player
        return max(candidates, key=lambda c: math.hypot(c[0] - px, c[1] - py))

    def update(self, dt: float, context):
        """Updates encounter progression, timing, and enemy lifecycle."""
        if not self.enabled:
            return

        if self.state == "idle":
            self.start()

        if self.state == "complete":
            return

        # Check status of currently active enemy
        if self.state == "active":
            if self.active_enemy is not None:
                if not self.active_enemy.alive or self.active_enemy not in context.target_group:
                    self.eliminated_count += 1
                    self.active_enemy = None
                    if self.eliminated_count >= self.total_count:
                        self.state = "complete"
                    else:
                        self.state = "waiting"
                        self.timer = self.config.get("respawn_delay", 1.0)
            else:
                self.state = "waiting"
                self.timer = self.config.get("respawn_delay", 1.0)

        elif self.state == "waiting":
            self.timer -= dt
            if self.timer <= 0.0:
                if self.spawned_count < self.total_count:
                    player_pos = (context.player.pos.x, context.player.pos.y) if context.player else (WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
                    spawn_pos = self.get_safe_spawn_pos(player_pos)
                    
                    e_type = self.config.get("enemy_type", TARGET_TYPE_SCOUT)
                    enemy = Enemy(enemy_type=e_type, pos=spawn_pos)
                    context.target_group.add(enemy)
                    
                    self.active_enemy = enemy
                    self.spawned_count += 1
                    self.state = "active"
                else:
                    if self.eliminated_count >= self.total_count:
                        self.state = "complete"
