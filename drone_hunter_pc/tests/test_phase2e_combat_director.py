import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import pytest
pygame.init()

from src.systems.combat_director import CombatDirector
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
from src.core.game_context import GameContext
from src.core.game_state import STATE_PLAYING

class TestPhase2ECombatDirector:

    def setup_method(self):
        self.ctx = GameContext()
        self.ctx.state = STATE_PLAYING
        self.encounter_system = EncounterSystem()
        self.director = CombatDirector(self.encounter_system)

    def _fast_forward(self, seconds: float):
        steps = int(seconds / 0.016)
        for _ in range(steps):
            self.director.update(0.016, self.ctx)

    def _kill_all_enemies(self):
        for enemy in list(self.ctx.target_group):
            enemy.alive = False
            enemy.kill()
        self.director.update(0.016, self.ctx)

    def test_initialization(self):
        assert self.director.state == "idle"
        assert self.director.encounter_index == 0
        assert self.director.pressure_level == 0
        assert self.director.timer == 0.0
        assert not self.director.is_suppressing_spawner

    def test_sequence_and_pacing(self):
        self.director.start()
        
        # 1. INTRO DELAY
        assert self.director.state == "intro"
        assert self.director.is_suppressing_spawner is True
        self._fast_forward(1.0)
        assert self.director.state == "intro" # still intro
        
        # Fast forward past intro
        self._fast_forward(0.6) # total 1.6s > 1.5s
        
        # 2. ENCOUNTER 1 (Scout)
        assert self.director.state == "encounter"
        assert self.director.pressure_level == 1
        assert self.director.encounter_index == 0
        assert self.director.is_suppressing_spawner is True
        
        # Wait for enemy to spawn (Scout Intro has 1.5s delay)
        self._fast_forward(1.6)
        assert len(self.ctx.target_group) == 1
        self._kill_all_enemies()
        # count=3 for scout intro
        self._fast_forward(1.1) # respawn delay
        assert len(self.ctx.target_group) == 1
        self._kill_all_enemies()
        self._fast_forward(1.1)
        assert len(self.ctx.target_group) == 1
        self._kill_all_enemies()
        
        # 3. RELIEF 1
        assert self.director.state == "relief"
        assert self.director.encounter_index == 1 # Advanced
        assert len(self.ctx.target_group) == 0
        
        # Wait halfway through relief
        self._fast_forward(1.0)
        assert self.director.state == "relief"
        assert self.director.is_suppressing_spawner is True
        assert self.encounter_system.state == "idle" or self.encounter_system.state == "complete" # Not active
        
        # Finish relief
        self._fast_forward(1.6) # total 2.6s > 2.5s
        
        # 4. ENCOUNTER 2 (Shooter)
        assert self.director.state == "encounter"
        assert self.director.pressure_level == 2
        
    def test_completion_and_reset(self):
        self.director.start()
        
        # Skip straight to end by modifying index
        self.director.encounter_index = len(self.director.encounters) - 1
        self.director.state = "relief"
        self.director.timer = 0.1
        
        # Trigger last encounter
        self._fast_forward(0.2)
        assert self.director.state == "encounter"
        assert self.director.pressure_level == 7
        
        # Fast forward through spawns for full comp
        self._fast_forward(4.0)
        assert len(self.ctx.target_group) == 3
        
        self._kill_all_enemies()
        assert self.director.state == "complete"
        assert self.director.is_suppressing_spawner is False
        
        # Reset
        self.director.reset()
        assert self.director.state == "idle"
        assert self.director.encounter_index == 0
        assert self.director.pressure_level == 0
        assert self.director.timer == 0.0
