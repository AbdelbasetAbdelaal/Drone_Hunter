"""
================================================================================
            DRONE HUNTER 2D - PHASE 2D ENCOUNTER COMPOSITION TESTS
================================================================================
Comprehensive headless test suite verifying:
- Simultaneous and sequential composed encounters
- Scout + Shooter
- Scout + Heavy
- Shooter + Heavy
- Scout + Shooter + Heavy (Full Composition)
- Spawner suppression and resumption
- Encounter Reset behavior
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import pytest
pygame.init()

from src.data.game_data import TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY
from src.entities.player import Player
from src.systems.combat_system import CombatSystem
from src.core.game_context import GameContext
from src.core.game_state import STATE_PLAYING
from src.systems.encounter_system import (
    EncounterSystem,
    SCOUT_SHOOTER_ENCOUNTER,
    SCOUT_HEAVY_ENCOUNTER,
    SHOOTER_HEAVY_ENCOUNTER,
    SCOUT_SHOOTER_HEAVY_ENCOUNTER,
    WAVE_SCOUTS_PATROL,
    WAVE_SCOUTS_ASSAULT,
    WAVE_SCOUTS_SWARM,
    WAVE_SHOOTERS_PAIR,
    WAVE_SHOOTERS_SQUAD,
    WAVE_HEAVY_ESCORT,
    WAVE_HEAVY_BATTLEGROUP,
    WAVE_SHIELD_VANGUARD,
    WAVE_ELITE_STRIKE_FORCE
)

class TestPhase2DEncounters:
    """Test suite for Phase 2D Composed Encounters."""

    def setup_method(self):
        self.ctx = GameContext()
        self.ctx.state = STATE_PLAYING
        self.player = Player(pos=(400.0, 400.0))
        self.ctx.player = self.player
        self.combat_system = CombatSystem(self.ctx)

    def _fast_forward(self, encounter, seconds: float):
        steps = int(seconds / 0.016)
        for _ in range(steps):
            encounter.update(0.016, self.ctx)

    def _kill_all_enemies(self, encounter):
        for enemy in list(self.ctx.target_group):
            enemy.alive = False
            enemy.kill()
        encounter.update(0.016, self.ctx)

    # --------------------------------------------------------------------------
    # 1. SCOUT + SHOOTER
    # --------------------------------------------------------------------------
    def test_scout_shooter_encounter(self):
        encounter = EncounterSystem(config=SCOUT_SHOOTER_ENCOUNTER)
        encounter.start()
        
        # Advance time to spawn both (1.5s delay + 1.5s delay)
        self._fast_forward(encounter, 3.5)
        
        assert len(self.ctx.target_group) == 2
        assert len(encounter.active_enemies) == 2
        
        types = {e.enemy_type for e in encounter.active_enemies}
        assert TARGET_TYPE_SCOUT in types
        assert TARGET_TYPE_SHOOTER in types
        
        # Eliminate both
        self._kill_all_enemies(encounter)
        assert encounter.is_complete is True

    # --------------------------------------------------------------------------
    # 2. SCOUT + HEAVY
    # --------------------------------------------------------------------------
    def test_scout_heavy_encounter(self):
        encounter = EncounterSystem(config=SCOUT_HEAVY_ENCOUNTER)
        encounter.start()
        self._fast_forward(encounter, 3.5)
        
        assert len(self.ctx.target_group) == 2
        assert len(encounter.active_enemies) == 2
        
        types = {e.enemy_type for e in encounter.active_enemies}
        assert TARGET_TYPE_SCOUT in types
        assert TARGET_TYPE_HEAVY in types
        
        self._kill_all_enemies(encounter)
        assert encounter.is_complete is True

    # --------------------------------------------------------------------------
    # 3. SHOOTER + HEAVY
    # --------------------------------------------------------------------------
    def test_shooter_heavy_encounter(self):
        encounter = EncounterSystem(config=SHOOTER_HEAVY_ENCOUNTER)
        encounter.start()
        self._fast_forward(encounter, 3.5)
        
        assert len(self.ctx.target_group) == 2
        assert len(encounter.active_enemies) == 2
        
        types = {e.enemy_type for e in encounter.active_enemies}
        assert TARGET_TYPE_SHOOTER in types
        assert TARGET_TYPE_HEAVY in types
        
        self._kill_all_enemies(encounter)
        assert encounter.is_complete is True

    # --------------------------------------------------------------------------
    # 4. FULL COMPOSITION (HEAVY + SHOOTER + SCOUT)
    # --------------------------------------------------------------------------
    def test_full_composition_encounter(self):
        encounter = EncounterSystem(config=SCOUT_SHOOTER_HEAVY_ENCOUNTER)
        encounter.start()
        
        # 1.5 + 1.0 + 1.0 = 3.5s total time for all spawns
        self._fast_forward(encounter, 4.0)
        
        assert len(self.ctx.target_group) == 3
        assert len(encounter.active_enemies) == 3
        
        types = {e.enemy_type for e in encounter.active_enemies}
        assert TARGET_TYPE_HEAVY in types
        assert TARGET_TYPE_SHOOTER in types
        assert TARGET_TYPE_SCOUT in types
        
        # Verify no 4th enemy spawns
        self._fast_forward(encounter, 5.0)
        assert len(encounter.active_enemies) == 3
        
        self._kill_all_enemies(encounter)
        assert encounter.is_complete is True

    # --------------------------------------------------------------------------
    # 5. SPAWNER SUPPRESSION
    # --------------------------------------------------------------------------
    def test_spawner_suppression(self):
        encounter = EncounterSystem(config=SCOUT_SHOOTER_HEAVY_ENCOUNTER)
        encounter.start()
        self._fast_forward(encounter, 1.0)
        
        assert encounter.is_suppressing_spawner is True
        
        self._fast_forward(encounter, 4.0)
        assert encounter.is_suppressing_spawner is True
        
        self._kill_all_enemies(encounter)
        assert encounter.is_suppressing_spawner is False

    # --------------------------------------------------------------------------
    # 6. RESET
    # --------------------------------------------------------------------------
    def test_encounter_reset(self):
        encounter = EncounterSystem(config=SCOUT_SHOOTER_HEAVY_ENCOUNTER)
        encounter.start()
        self._fast_forward(encounter, 4.0)
        
        assert encounter.spawned_count == 3
        assert encounter.state == "active"
        
        encounter.reset()
        assert encounter.state == "idle"
        assert encounter.spawned_count == 0
        assert len(encounter.active_enemies) == 0
        assert not encounter.is_active

    # --------------------------------------------------------------------------
    # 7. ALL PHASE 8 TACTICAL WAVE COMPOSITION LIFECYCLE TESTS
    # --------------------------------------------------------------------------
    @pytest.mark.parametrize("wave_config, expected_count", [
        (WAVE_SCOUTS_PATROL, 3),
        (WAVE_SCOUTS_ASSAULT, 4),
        (WAVE_SCOUTS_SWARM, 5),
        (WAVE_SHOOTERS_PAIR, 3),
        (WAVE_SHOOTERS_SQUAD, 5),
        (WAVE_HEAVY_ESCORT, 4),
        (WAVE_HEAVY_BATTLEGROUP, 5),
        (WAVE_SHIELD_VANGUARD, 4),
        (WAVE_ELITE_STRIKE_FORCE, 5),
    ])
    def test_all_wave_compositions_lifecycle(self, wave_config, expected_count):
        """Verify spawn count, tracking, dead enemy cleanup, and completion."""
        self.ctx.target_group.empty()
        encounter = EncounterSystem(config=wave_config)
        assert encounter.total_count == expected_count
        encounter.start()
        assert encounter.state == "waiting"

        # Advance sufficient time for all sequential spawns (0.5s + (count-1)*1.0s + 0.5s)
        total_time = 1.0 + (expected_count * 1.1)
        self._fast_forward(encounter, total_time)

        assert encounter.spawned_count == expected_count
        assert len(encounter.active_enemies) == expected_count
        assert len(self.ctx.target_group) == expected_count
        assert encounter.state == "active"
        assert not encounter.is_complete

        # Kill 1 enemy -> verify removed from active_enemies but encounter still active
        first_enemy = encounter.active_enemies[0]
        first_enemy.kill()
        encounter.update(0.016, self.ctx)
        assert len(encounter.active_enemies) == expected_count - 1
        assert encounter.eliminated_count == 1
        assert not encounter.is_complete

        # Kill remaining enemies -> verify complete
        self._kill_all_enemies(encounter)
        assert encounter.is_complete is True
        assert encounter.state == "complete"
        assert len(encounter.active_enemies) == 0
        assert encounter.eliminated_count == expected_count

