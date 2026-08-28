"""
================================================================================
                DRONE HUNTER 2D - PLAYER ABILITY CONTROLLER
================================================================================
Manages active tactical abilities (EMP Blast, Barrel Roll, Stealth Cloak,
Overdrive Ultimate, Overclock) and system jamming timers.
"""

from typing import Callable, Optional
from src.data.game_data import (
    EMP_COOLDOWN_MAX, ROLL_COOLDOWN, ROLL_DURATION, ROLL_SPEED_BOOST,
    CLOAK_DURATION, CLOAK_COOLDOWN_MAX, OVERDRIVE_DURATION, OVERDRIVE_COOLDOWN_MAX,
    HORIZONTAL_SPEED
)


class AbilityController:
    """Encapsulates ability activation, timers, and cooldown management."""

    def __init__(self):
        # EMP Ability
        self.emp_cooldown = 0.0
        self.emp_cooldown_max = EMP_COOLDOWN_MAX

        # Roll Ability
        self.roll_timer = 0.0
        self.roll_cooldown = 0.0
        self.is_rolling = False

        # Cloak Ability
        self.cloak_timer = 0.0
        self.cloak_cooldown = 0.0
        self.is_cloaked = False
        self.has_cloak_upgrade = False

        # Overdrive Ultimate
        self.overdrive_timer = 0.0
        self.overdrive_cooldown = 0.0
        self.overdrive_duration_max = OVERDRIVE_DURATION
        self.overdrive_cooldown_max = OVERDRIVE_COOLDOWN_MAX

        # Status Modifiers
        self.emp_jammed_timer = 0.0
        self.overclock_timer = 0.0

    @property
    def is_jammed(self) -> bool:
        return self.emp_jammed_timer > 0.0

    def trigger_emp(self) -> bool:
        """Triggers EMP blast if off cooldown and not jammed."""
        if self.is_jammed:
            return False
        if self.emp_cooldown <= 0.0:
            self.emp_cooldown = self.emp_cooldown_max
            return True
        return False

    def trigger_emp_jammed(self, duration: float = 3.0, is_invulnerable: bool = False):
        """Jams player systems after an EMP attack unless invulnerable."""
        if not is_invulnerable:
            self.emp_jammed_timer = max(self.emp_jammed_timer, duration)

    def trigger_overdrive(self, on_activate: Optional[Callable[[], None]] = None) -> bool:
        """Activates Overdrive Ultimate (hyper-fire mode, speed boost, invulnerability)."""
        if self.is_jammed:
            return False
        if self.overdrive_cooldown <= 0.0 and self.overdrive_timer <= 0.0:
            self.overdrive_timer = getattr(self, "overdrive_duration_max", OVERDRIVE_DURATION)
            self.overdrive_cooldown = getattr(self, "overdrive_cooldown_max", OVERDRIVE_COOLDOWN_MAX)
            if on_activate:
                on_activate()
            return True
        return False

    def trigger_roll(self, dir_x: float = 1.0, on_impulse: Optional[Callable[[float], None]] = None) -> bool:
        """Performs high-speed evasive barrel roll."""
        if self.is_jammed:
            return False
        if self.roll_cooldown <= 0.0 and not self.is_rolling:
            self.is_rolling = True
            self.roll_timer = ROLL_DURATION
            self.roll_cooldown = ROLL_COOLDOWN
            if on_impulse:
                on_impulse(dir_x * (HORIZONTAL_SPEED * ROLL_SPEED_BOOST))
            return True
        return False

    def trigger_cloak(self) -> bool:
        """Activates tactical stealth cloak."""
        if self.is_jammed:
            return False
        if self.cloak_cooldown <= 0.0 and not self.is_cloaked:
            self.is_cloaked = True
            self.cloak_timer = CLOAK_DURATION
            self.cloak_cooldown = CLOAK_COOLDOWN_MAX
            return True
        return False

    def trigger_overclock(self, duration: float = 6.0):
        """Triggers weapon overclock fire rate boost."""
        self.overclock_timer = max(self.overclock_timer, duration)

    def update(self, dt: float):
        """Updates all ability and status cooldown timers."""
        if self.emp_jammed_timer > 0:
            self.emp_jammed_timer = max(0.0, self.emp_jammed_timer - dt)
        if self.emp_cooldown > 0:
            self.emp_cooldown = max(0.0, self.emp_cooldown - dt)
        if self.overclock_timer > 0:
            self.overclock_timer = max(0.0, self.overclock_timer - dt)

        if self.overdrive_timer > 0:
            self.overdrive_timer = max(0.0, self.overdrive_timer - dt)
        if self.overdrive_cooldown > 0:
            self.overdrive_cooldown = max(0.0, self.overdrive_cooldown - dt)

        if self.is_rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.is_rolling = False
        if self.roll_cooldown > 0:
            self.roll_cooldown = max(0.0, self.roll_cooldown - dt)

        if self.is_cloaked:
            self.cloak_timer -= dt
            if self.cloak_timer <= 0:
                self.is_cloaked = False
        if self.cloak_cooldown > 0:
            self.cloak_cooldown = max(0.0, self.cloak_cooldown - dt)
