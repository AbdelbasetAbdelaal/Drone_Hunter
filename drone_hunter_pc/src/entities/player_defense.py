"""
================================================================================
                DRONE HUNTER 2D - PLAYER DEFENSE & HEALTH SYSTEM
================================================================================
Manages player drone hull integrity, defensive shield absorption, armor mitigation,
energy regeneration, damage grace timers, and destruction lifecycle.
"""

from src.data.game_data import (
    PLAYER_MAX_HEALTH, PLAYER_MAX_ENERGY, ENERGY_REGEN_RATE
)


class PlayerDefense:
    """Encapsulates health, armor, shields, energy, and damage resolution."""

    def __init__(self):
        self._upgrade_bonus_health = 0.0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.max_energy = PLAYER_MAX_ENERGY
        self.energy = PLAYER_MAX_ENERGY
        self.weapon_effectiveness = 1.0
        self.armor = 0
        self.alive = True

        # Shield Hit System
        self.shield_hits = 0
        self.damage_grace_timer = 0.0
        self.damage_grace_duration = 0.30

        # Visual Flash & Timers
        self.damage_flash_timer = 0.0
        self.invulnerable_timer = 0.0
        self.is_destroyed = False
        self.destruction_timer = 0.0

    @property
    def shield_charge(self) -> int:
        return self.shield_hits * 50

    @shield_charge.setter
    def shield_charge(self, value: int):
        self.shield_hits = max(0, int(value // 50) if value > 0 else 0)

    def configure_drone_class(self, class_data: dict):
        """Applies hull and armor configurations from drone class profile."""
        self.max_health = class_data.get("max_health", 100) + self._upgrade_bonus_health
        self.health = self.max_health
        self.armor = class_data.get("armor", 0)

    def activate_shield(self, hits: int = 3):
        """Activates defensive energy shield for given hit charges."""
        self.shield_hits = max(self.shield_hits, hits)

    def take_damage(self, amount: float, is_invulnerable: bool = False, source: str = "bullet", ignore_grace: bool = False) -> bool:
        """Applies damage to shields and health hull. Returns True if destruction is triggered."""
        if not ignore_grace and is_invulnerable:
            return False

        self.damage_flash_timer = 0.18

        if self.shield_hits > 0:
            self.shield_hits -= 1
            return False

        effective_damage = max(1.0, float(amount) - float(self.armor))
        self.health = max(0.0, self.health - effective_damage)
        self.damage_grace_timer = self.damage_grace_duration

        if self.health <= 0.0:
            if not self.is_destroyed:
                self.alive = False
                self.is_destroyed = True
                self.destruction_timer = 1.4
                return True
        return False

    def update(self, dt: float) -> bool:
        """Updates energy regeneration and timers. Returns True if destruction animation finished and entity should kill()."""
        # Energy Regeneration
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + ENERGY_REGEN_RATE * dt)

        # Timers
        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self.damage_grace_timer > 0:
            self.damage_grace_timer = max(0.0, self.damage_grace_timer - dt)
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        # Destruction Animation Timer
        if self.is_destroyed:
            self.destruction_timer = max(0.0, self.destruction_timer - dt)
            if self.destruction_timer <= 0:
                return True

        return False
