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
    def __init__(self, encounter_system: EncounterSystem, test_mode: bool = False):
        self.encounter_system = encounter_system
        self.test_mode = test_mode
        self.state = "idle" # idle, intro, encounter, relief, complete
        self.encounter_index = 0
        self.pressure_level = 0
        self.timer = 0.0
        
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
            self.encounter_system.start(config)
            self.state = "encounter"
        else:
            if self.loop_encounters:
                self.encounter_index = 0
                self._start_next_encounter()
            else:
                self.state = "complete"

    def update(self, dt: float, ctx):
        """Ticks pacing timers and delegates to EncounterSystem."""
        if self.state == "idle" or self.state == "complete":
            return
            
        if self.state == "intro":
            if self.test_mode:
                self._start_next_encounter()
            else:
                self.timer -= dt
                if self.timer <= 0:
                    self._start_next_encounter()
                
        elif self.state == "encounter":
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
                    self.timer = self.relief_after_encounter
                else:
                    self.state = "complete"
                    
        elif self.state == "relief":
            self.timer -= dt
            if self.timer <= 0:
                self._start_next_encounter()
