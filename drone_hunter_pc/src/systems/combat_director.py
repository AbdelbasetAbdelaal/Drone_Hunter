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

class CombatDirector:
    """Controls the pacing, ordering, and escalation of encounters."""
    def __init__(self, encounter_system: EncounterSystem):
        self.encounter_system = encounter_system
        self.state = "idle" # idle, intro, encounter, relief, complete
        self.encounter_index = 0
        self.pressure_level = 0
        self.timer = 0.0
        
        # Phase 2E Development Sequence
        self.encounters = [
            SCOUT_INTRO_ENCOUNTER,
            SHOOTER_INTRO_ENCOUNTER,
            HEAVY_INTRO_ENCOUNTER,
            SCOUT_SHOOTER_ENCOUNTER,
            SCOUT_HEAVY_ENCOUNTER,
            SHOOTER_HEAVY_ENCOUNTER,
            SCOUT_SHOOTER_HEAVY_ENCOUNTER
        ]
        
        # Pacing Config
        self.intro_delay = 1.5
        self.relief_after_encounter = 2.5

    def reset(self):
        """Resets the director back to initial state."""
        self.state = "idle"
        self.encounter_index = 0
        self.pressure_level = 0
        self.timer = 0.0
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
        if self.encounter_index < len(self.encounters):
            self.pressure_level = self.encounter_index + 1
            config = self.encounters[self.encounter_index]
            self.encounter_system.start(config)
            self.state = "encounter"
        else:
            self.state = "complete"

    def update(self, dt: float, ctx):
        """Ticks pacing timers and delegates to EncounterSystem."""
        if self.state == "idle" or self.state == "complete":
            return
            
        if self.state == "intro":
            self.timer -= dt
            if self.timer <= 0:
                self._start_next_encounter()
                
        elif self.state == "encounter":
            # Delegate updating to the EncounterSystem
            self.encounter_system.update(dt, ctx)
            
            # Check for completion
            if self.encounter_system.is_complete:
                self.encounter_index += 1
                if self.encounter_index < len(self.encounters):
                    self.state = "relief"
                    self.timer = self.relief_after_encounter
                else:
                    self.state = "complete"
                    
        elif self.state == "relief":
            self.timer -= dt
            if self.timer <= 0:
                self._start_next_encounter()
