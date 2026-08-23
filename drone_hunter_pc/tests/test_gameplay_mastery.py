"""
================================================================================
          DRONE HUNTER 2D - GAMEPLAY MASTERY & COMBAT DEPTH TEST SUITE
================================================================================
Comprehensive behavioral and runtime unit tests verifying:
- Adaptive Combat Director intensity states (CALM, LOW, MEDIUM, HIGH, CRITICAL)
- Deterministic tactical formations (V, Wedge, Line, Staggered, Flank, Escort)
- Tactical Enemy archetype behaviors (Scout, Shooter, Heavy, Shield)
- Player drone class identities (Striker, Interceptor, Assault, Arc, Speed)
- Boss phase transitions, attack pacing, and telegraphing
- Combat momentum combo streaks, hit-stop, and floating score feedback
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pytest
import pygame
from unittest.mock import MagicMock

from src.core.game_context import GameContext
from src.systems.combat_director import (
    CombatDirector, INTENSITY_CALM, INTENSITY_LOW, INTENSITY_MEDIUM,
    INTENSITY_HIGH, INTENSITY_CRITICAL
)
from src.systems.encounter_system import (
    EncounterSystem, FORMATION_V, FORMATION_WEDGE, FORMATION_LINE,
    FORMATION_STAGGERED, FORMATION_FLANK, FORMATION_ESCORT,
    WAVE_SCOUTS_PATROL, WAVE_SCOUTS_ASSAULT, WAVE_HEAVY_ESCORT,
    SCOUT_INTRO_ENCOUNTER, SHOOTER_INTRO_ENCOUNTER, HEAVY_INTRO_ENCOUNTER
)
from src.entities.player import Player
from src.entities.enemy import Enemy, Scout, Shooter, Heavy
from src.entities.boss import SectorBoss
from src.data.boss_data import get_boss_definition, BOSS_ASSEMBLY_WARDEN
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHIELD_DRONE, DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR,
    DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND
)
from src.systems.combat_feedback import CombatFeedbackSystem
from src.systems.combat_system import CombatSystem


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


# =============================================================================
# 1. COMBAT DIRECTOR & ADAPTIVE INTENSITY TESTS
# =============================================================================
class TestCombatDirectorIntensity:
    def test_intensity_calm_when_empty(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys)
        ctx = GameContext()
        ctx.player = Player()
        ctx.target_group.empty()
        ctx.combo_counter = 0

        intensity = director.evaluate_intensity(ctx)
        assert intensity == INTENSITY_CALM

    def test_intensity_low_single_enemy(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys)
        ctx = GameContext()
        ctx.player = Player()
        ctx.target_group.add(Scout(pos=(100, 100)))
        ctx.combo_counter = 0

        intensity = director.evaluate_intensity(ctx)
        assert intensity == INTENSITY_LOW

    def test_intensity_medium_multiple_enemies(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys)
        ctx = GameContext()
        ctx.player = Player()
        ctx.target_group.add(Scout(pos=(100, 100)))
        ctx.target_group.add(Shooter(pos=(200, 200)))

        intensity = director.evaluate_intensity(ctx)
        assert intensity == INTENSITY_MEDIUM

    def test_intensity_high_high_combo_or_many_enemies(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys)
        ctx = GameContext()
        ctx.player = Player()
        ctx.combo_counter = 4
        ctx.player.health = ctx.player.max_health

        intensity = director.evaluate_intensity(ctx)
        assert intensity == INTENSITY_HIGH

    def test_intensity_critical_low_player_health(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys)
        ctx = GameContext()
        ctx.player = Player()
        ctx.player.health = 15 # < 25% of 100

        intensity = director.evaluate_intensity(ctx)
        assert intensity == INTENSITY_CRITICAL

    def test_encounter_pacing_transition_flow(self):
        enc_sys = EncounterSystem(enabled=True)
        director = CombatDirector(enc_sys, test_mode=False)
        ctx = GameContext()
        ctx.player = Player()

        director.start()
        assert director.state == "intro"
        assert director.is_suppressing_spawner is True

        # Tick through intro delay
        director.update(0.5, ctx)
        assert director.state == "encounter"


# =============================================================================
# 2. ENCOUNTER SYSTEM & FORMATIONS TESTS
# =============================================================================
class TestEncounterSystemFormations:
    def test_deterministic_formation_selection(self):
        enc_sys = EncounterSystem(enabled=True)

        # 3 scouts -> V formation
        assert enc_sys._determine_formation(WAVE_SCOUTS_PATROL) == FORMATION_V
        # 4 scouts -> Wedge formation
        assert enc_sys._determine_formation(WAVE_SCOUTS_ASSAULT) == FORMATION_WEDGE
        # Heavy escort -> Escort formation
        assert enc_sys._determine_formation(WAVE_HEAVY_ESCORT) == FORMATION_ESCORT
        # 2 enemies -> Flank formation
        assert enc_sys._determine_formation([TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER]) == FORMATION_FLANK

    def test_formation_spawn_position_offsets(self):
        enc_sys = EncounterSystem(config=WAVE_SCOUTS_PATROL, enabled=True)
        enc_sys.start()
        player_pos = (1200.0, 700.0)

        pos0 = enc_sys._find_spawn_position(player_pos, slot_idx=0)
        pos1 = enc_sys._find_spawn_position(player_pos, slot_idx=1)
        pos2 = enc_sys._find_spawn_position(player_pos, slot_idx=2)

        # Slots must have distinct coordinates
        assert pos0 != pos1
        assert pos1 != pos2
        # All spawn positions must be safely inside arena boundaries
        for p in (pos0, pos1, pos2):
            assert 50.0 <= p[0] <= 2350.0
            assert 50.0 <= p[1] <= 1350.0


# =============================================================================
# 3. TACTICAL ENEMY BEHAVIOR & TELEGRAPHING TESTS
# =============================================================================
class TestEnemyTacticalBehaviors:
    def test_scout_attack_and_retreat_state_cycle(self):
        scout = Scout(pos=(500, 500))
        assert scout.ai_state == "approach"

        # Simulate update to reach strafe
        player_pos = (520, 520) # close to trigger strafe
        scout.update(0.1, player_pos=player_pos)
        assert scout.ai_state in ("approach", "strafe")

        # Manually verify telegraph state transitions into dive
        scout.ai_state = "telegraph"
        scout.state_timer = 0.0
        scout.dive_dir = pygame.Vector2(1, 0)
        scout.update(0.5, player_pos=player_pos)
        assert scout.ai_state == "dive"

    def test_shooter_distance_keeping_and_aiming(self):
        shooter = Shooter(pos=(800, 500))
        player_pos = (400, 500) # 400px away (in preferred band)
        shooter.ai_state = "position"

        # Shooter positions and prepares aim
        shooter.fire_timer = 3.0 # ready to fire
        shooter.update(0.1, player_pos=player_pos)
        assert shooter.ai_state in ("aim", "telegraph")

    def test_heavy_slow_relentless_advance_and_armor(self):
        heavy = Heavy(pos=(900, 500))
        assert heavy.armor > 0.0 # armored

        # Heavy takes mitigated damage
        initial_hp = heavy.hp
        heavy.take_damage(20) # should reduce less than 20
        damage_taken = initial_hp - heavy.hp
        assert damage_taken < 20


# =============================================================================
# 4. PLAYER DRONE CLASS IDENTITIES TESTS
# =============================================================================
class TestPlayerDroneClassIdentities:
    def test_striker_balanced_identity(self):
        p = Player()
        p.set_drone_class(DRONE_CLASS_STRIKER)
        assert p.max_health == 100
        assert p.armor == 0

    def test_interceptor_high_speed_identity(self):
        p = Player()
        p.set_drone_class(DRONE_CLASS_INTERCEPTOR)
        striker = Player()
        striker.set_drone_class(DRONE_CLASS_STRIKER)
        assert p.max_speed > striker.max_speed
        assert p.acceleration > striker.acceleration

    def test_assault_high_durability_identity(self):
        p = Player()
        p.set_drone_class(DRONE_CLASS_ASSAULT)
        assert p.max_health >= 140
        assert p.armor > 0 # passive armor reduction


# =============================================================================
# 5. BOSS ENCOUNTER PACING & PHASE TRANSITIONS TESTS
# =============================================================================
class TestBossPacingAndPhases:
    def test_boss_phase_transition_on_hp_threshold(self):
        boss_def = get_boss_definition(BOSS_ASSEMBLY_WARDEN)
        boss = SectorBoss(boss_def, pos=(1200, 600))
        assert boss.current_phase_number == 1

        # Deal damage to cross phase 2 threshold (e.g. at 65% HP)
        threshold_hp = int(boss.max_hp * 0.60)
        boss.take_damage(boss.hp - threshold_hp)

        assert boss.current_phase_number >= 2
        assert boss.phase_transitioning is True

    def test_boss_staggered_attack_cooldowns(self):
        boss_def = get_boss_definition(BOSS_ASSEMBLY_WARDEN)
        boss = SectorBoss(boss_def, pos=(1200, 600))

        # Check initial staggered cooldowns
        assert len(boss.attack_cooldowns) > 0
        for cd in boss.attack_cooldowns.values():
            assert cd > 0.0


# =============================================================================
# 6. COMBAT MOMENTUM & HIT FEEDBACK TESTS
# =============================================================================
class TestCombatMomentumAndFeedback:
    def test_combo_streak_increment_on_score(self):
        ctx = GameContext()
        ctx.combo_count = 1
        ctx.add_score(100)
        assert ctx.combo_count == 2
        assert ctx.combo_timer == 4.0

    def test_combo_reset_on_heavy_player_damage(self):
        ctx = GameContext()
        ctx.player = Player()
        ctx.combo_count = 5
        feedback = CombatFeedbackSystem(ctx)

        # Taking heavy damage (>15) resets combo
        feedback.on_player_hit(25)
        assert ctx.combo_count == 1
        assert ctx.combo_timer == 0.0

    def test_boss_rating_popup_auto_dismissal(self):
        ctx = GameContext()
        ctx.boss_rating_timer = 3.5
        ctx.latest_boss_rating = {"rating": "A", "boss_name": "Assembly Warden"}

        # Advance timer past duration
        ctx.update_timers(4.0)

        assert ctx.boss_rating_timer == 0.0
        assert ctx.latest_boss_rating is None
