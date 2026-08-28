"""
================================================================================
                DRONE HUNTER 2D - WEAPON BEHAVIORS PACKAGE
================================================================================
Exposes modular weapon behaviors and strategy registry for all combat loadouts.
"""

from typing import Dict
from src.data.game_data import (
    WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_BARRAGE, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BEAM,
    WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP
)
from src.entities.weapons.base_behavior import BaseWeaponBehavior, WeaponFireContext
from src.entities.weapons.pulse_behavior import PulseBehavior
from src.entities.weapons.rapid_behavior import RapidBehavior
from src.entities.weapons.scatter_behavior import ScatterBehavior
from src.entities.weapons.missile_behavior import MissileBehavior
from src.entities.weapons.barrage_behavior import BarrageBehavior
from src.entities.weapons.plasma_behavior import PlasmaBehavior
from src.entities.weapons.railgun_behavior import RailgunBehavior
from src.entities.weapons.beam_behavior import ContinuousBeamBehavior
from src.entities.weapons.tesla_behavior import TeslaBehavior
from src.entities.weapons.cluster_behavior import ClusterBehavior
from src.entities.weapons.emp_behavior import EMPBehavior


class WeaponRegistry:
    """Maintains instantiated weapon firing behaviors."""

    def __init__(self):
        self._behaviors: Dict[str, BaseWeaponBehavior] = {
            WEAPON_PULSE: PulseBehavior(),
            WEAPON_RAPID: RapidBehavior(),
            WEAPON_SCATTER: ScatterBehavior(),
            WEAPON_MISSILE: MissileBehavior(),
            WEAPON_BARRAGE: BarrageBehavior(),
            WEAPON_PLASMA: PlasmaBehavior(),
            WEAPON_RAIL: RailgunBehavior(),
            WEAPON_BEAM: ContinuousBeamBehavior(),
            WEAPON_TESLA: TeslaBehavior(),
            WEAPON_CLUSTER: ClusterBehavior(),
            WEAPON_EMP: EMPBehavior(),
        }

    def get_behavior(self, weapon_id: str) -> BaseWeaponBehavior:
        return self._behaviors.get(weapon_id, self._behaviors[WEAPON_PULSE])


_GLOBAL_REGISTRY: WeaponRegistry = WeaponRegistry()


def get_weapon_behavior(weapon_id: str) -> BaseWeaponBehavior:
    """Returns the dedicated weapon firing behavior for a weapon identifier."""
    return _GLOBAL_REGISTRY.get_behavior(weapon_id)


__all__ = [
    "BaseWeaponBehavior",
    "WeaponFireContext",
    "WeaponRegistry",
    "get_weapon_behavior",
    "PulseBehavior",
    "RapidBehavior",
    "ScatterBehavior",
    "MissileBehavior",
    "BarrageBehavior",
    "PlasmaBehavior",
    "RailgunBehavior",
    "ContinuousBeamBehavior",
    "TeslaBehavior",
    "ClusterBehavior",
    "EMPBehavior",
]
