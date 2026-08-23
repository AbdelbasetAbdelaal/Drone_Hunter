import pygame
from src.systems.encounter_system import (
    EncounterSystem,
    SCOUT_INTRO_ENCOUNTER,
    SHOOTER_INTRO_ENCOUNTER,
    HEAVY_INTRO_ENCOUNTER,
    SCOUT_SHOOTER_ENCOUNTER,
    SCOUT_HEAVY_ENCOUNTER,
    SHOOTER_HEAVY_ENCOUNTER,
    SCOUT_SHOOTER_HEAVY_ENCOUNTER
)

# -----------------------------------------------------------------------------
# ADAPTIVE INTENSITY LEVELS
# -----------------------------------------------------------------------------
INTENSITY_CALM = "CALM"
INTENSITY_LOW = "LOW"
INTENSITY_MEDIUM = "MEDIUM"
INTENSITY_HIGH = "HIGH"
INTENSITY_CRITICAL = "CRITICAL"


class CombatDirector:
    """Controls the pacing, ordering, escalation, and adaptive intensity of encounters."""
    def __init__(self, encounter_system: EncounterSystem, test_mode: bool = False):
        self.encounter_system = encounter_system
        self.test_mode = test_mode
        self.state = "idle" # idle, intro, encounter, relief, complete
        self.encounter_index = 0
        self.pressure_level = 0
        self.timer = 0.0
        self.encounter_elapsed_time = 0.0
        self.current_intensity = INTENSITY_MEDIUM
        
        # Default sequence (Legacy Phase 2E compatibility)
        self.encounters = [
            SCOUT_INTRO_ENCOUNTER,
            SHOOTER_INTRO_ENCOUNTER,
            HEAVY_INTRO_ENCOUNTER,
            SCOUT_SHOOTER_ENCOUNTER,
            SCOUT_HEAVY_ENCOUNTER,
            SHOOTER_HEAVY_ENCOUNTER,
            SCOUT_SHOOTER_HEAVY_ENCOUNTER
        ]
        self.loop_encounters = False
        
        # Pacing Config (Snappy Fast-Paced Combat Transitions)
        self.intro_delay = 0.4
        self.relief_after_encounter = 1.0

    def evaluate_intensity(self, ctx) -> str:
        """Evaluates live combat telemetry (health, kills/combo, enemy count, time, boss)

        and determines the active adaptive intensity level without altering raw base HP.
        """
        player = getattr(ctx, "player", None)
        player_hp_pct = (player.health / player.max_health) if player and player.max_health > 0 else 1.0
        active_enemies = len(getattr(ctx, "target_group", []))
        combo = getattr(ctx, "combo_counter", 0)
        is_boss_active = getattr(ctx, "boss_active", False) or (getattr(ctx, "boss", None) is not None and getattr(ctx.boss, "alive", False))

        if player_hp_pct < 0.25:
            intensity = INTENSITY_CRITICAL
        elif is_boss_active or active_enemies >= 5:
            intensity = INTENSITY_HIGH
        elif combo >= 3 and player_hp_pct >= 0.75:
            intensity = INTENSITY_HIGH
        elif active_enemies >= 2 or combo >= 1:
            intensity = INTENSITY_MEDIUM
        elif active_enemies == 1:
            intensity = INTENSITY_LOW
        else:
            intensity = INTENSITY_CALM

        self.current_intensity = intensity
        return intensity

    def set_mission_sequence(self, sequence: list, loop: bool = False):
        """Phase 5: Sets the exact sequence to run, and whether to loop it."""
        self.encounters = sequence
        self.loop_encounters = loop
        self.reset()

    def reset(self):
        """Resets the director back to initial state."""
        self.state = "idle"
        self.encounter_index = 0
        self.pressure_level = 0
        self.timer = 0.0
        self.encounter_elapsed_time = 0.0
        self.current_intensity = INTENSITY_MEDIUM
        self.encounter_system.reset()

    def start(self):
        """Starts the combat direction sequence."""
        self.reset()
        self.state = "intro"
        self.timer = self.intro_delay

    @property
    def is_suppressing_spawner(self) -> bool:
        """Suppresses normal waves during intro, encounter, and relief."""
        return self.state in ("intro", "encounter", "relief")

    def _start_next_encounter(self):
        """Advances sequence and pushes config to EncounterSystem."""
        if len(self.encounters) == 0:
            self.state = "complete"
            return
            
        if self.encounter_index < len(self.encounters):
            self.pressure_level = self.encounter_index + 1
            config = self.encounters[self.encounter_index]
            self.encounter_elapsed_time = 0.0
            self.encounter_system.start(config)
            self.state = "encounter"
        else:
            if self.loop_encounters:
                self.encounter_index = 0
                self._start_next_encounter()
            else:
                self.state = "complete"

    def update(self, dt: float, ctx):
        """Ticks pacing timers, evaluates intensity, and delegates to EncounterSystem."""
        if self.state == "idle" or self.state == "complete":
            return

        self.evaluate_intensity(ctx)
            
        if self.state == "intro":
            if self.test_mode:
                self._start_next_encounter()
            else:
                self.timer -= dt
                if self.timer <= 0:
                    self._start_next_encounter()
                
        elif self.state == "encounter":
            self.encounter_elapsed_time += dt
            # Delegate updating to the EncounterSystem
            self.encounter_system.update(dt, ctx)
            
            # Check for completion
            if self.encounter_system.is_complete:
                # Award progression scrap for completing an encounter
                from src.data.game_data import REWARD_ENCOUNTER, REWARD_COMPOSITION
                is_full_composition = (self.encounters[self.encounter_index] == SCOUT_SHOOTER_HEAVY_ENCOUNTER)
                ctx.scrap += REWARD_COMPOSITION if is_full_composition else REWARD_ENCOUNTER
                
                self.encounter_index += 1
                if self.encounter_index < len(self.encounters) or self.loop_encounters:
                    self.state = "relief"
                    # Adaptive relief pacing: provide slightly more breathing room on critical health
                    if self.current_intensity == INTENSITY_CRITICAL:
                        self.timer = min(1.4, self.relief_after_encounter * 1.25)
                    elif self.current_intensity == INTENSITY_HIGH:
                        self.timer = max(0.75, self.relief_after_encounter * 0.85)
                    else:
                        self.timer = self.relief_after_encounter
                else:
                    self.state = "complete"
                    
        elif self.state == "relief":
            self.timer -= dt
            if self.timer <= 0:
                self._start_next_encounter()

