"""
================================================================================
                DRONE HUNTER 2D - ENEMY AI BASE & CONTEXT
================================================================================
Defines the core interface and lightweight context for specialized enemy AI
controllers, abstracting state-machine transitions and tactical movement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import pygame

from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_STANDARD,
    TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE,
    TARGET_TYPE_CHASER, TARGET_TYPE_SWARM, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER
)


@dataclass
class EnemyAIContext:
    """Lightweight environmental context provided to enemy AI on each update frame."""
    player_pos: tuple[float, float] = (200.0, 360.0)
    player_vel: tuple[float, float] = (0.0, 0.0)
    player_obj: Any = None
    target_group: Any = None
    sector_idx: int = 0


class BaseEnemyAI(ABC):
    """Abstract base class for all enemy AI behavior controllers."""

    def __init__(self, enemy: Any):
        self.enemy = enemy
        self.ai_state: str = "approach"
        self.state_timer: float = 0.0

    @abstractmethod
    def update(self, dt: float, enemy: Any, context: EnemyAIContext) -> list[pygame.sprite.Sprite]:
        """Calculates tactical movement, updates state-machine, and returns spawned hostile bullets."""
        pass


def create_enemy_ai(enemy_type: str, enemy: Any) -> BaseEnemyAI:
    """Factory function instantiating the appropriate AI controller for a given enemy archetype."""
    from src.entities.ai.scout_ai import ScoutAI
    from src.entities.ai.shooter_ai import ShooterAI
    from src.entities.ai.heavy_ai import HeavyAI
    from src.entities.ai.sniper_ai import SniperAI
    from src.entities.ai.turret_ai import TurretAI
    from src.entities.ai.swarm_ai import SwarmAI
    from src.entities.ai.chaser_ai import ChaserAI
    from src.entities.ai.fast_ai import FastAI
    from src.entities.ai.shield_ai import ShieldDroneAI
    from src.entities.ai.standard_ai import StandardAI

    if enemy_type == TARGET_TYPE_SCOUT:
        return ScoutAI(enemy)
    elif enemy_type == TARGET_TYPE_SHOOTER:
        return ShooterAI(enemy)
    elif enemy_type in (TARGET_TYPE_HEAVY, TARGET_TYPE_ARMORED):
        return HeavyAI(enemy)
    elif enemy_type == TARGET_TYPE_SNIPER:
        return SniperAI(enemy)
    elif enemy_type == TARGET_TYPE_TURRET:
        return TurretAI(enemy)
    elif enemy_type == TARGET_TYPE_SWARM:
        return SwarmAI(enemy)
    elif enemy_type == TARGET_TYPE_CHASER:
        return ChaserAI(enemy)
    elif enemy_type == TARGET_TYPE_FAST:
        return FastAI(enemy)
    elif enemy_type == TARGET_TYPE_SHIELD_DRONE:
        return ShieldDroneAI(enemy)
    else:
        return StandardAI(enemy)
