"""
================================================================================
            DRONE HUNTER 2D - WEAPON BEHAVIOR BASE & CONTEXT
================================================================================
Defines the base strategy class and lightweight execution context for modular
player weapon firing behaviors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional, Any
import pygame


@dataclass
class WeaponFireContext:
    """Lightweight dataclass encapsulating the firing environment for a weapon."""
    weapon_id: str
    damage: int
    speed: float
    color: tuple[int, int, int]
    aim_angle: float
    target_pos: tuple[float, float]
    fwd_dx: float
    fwd_dy: float
    get_mount_pos_fn: Callable[[str], tuple[float, float]]
    overdrive_active: bool = False
    overclock_active: bool = False
    targets_group: Any = None
    particle_manager: Any = None
    controller: Any = None


class BaseWeaponBehavior(ABC):
    """Abstract base class for all weapon firing behaviors."""

    @abstractmethod
    def fire(self, context: WeaponFireContext) -> list[pygame.sprite.Sprite]:
        """Generates and returns projectiles originating from mount positions."""
        pass
