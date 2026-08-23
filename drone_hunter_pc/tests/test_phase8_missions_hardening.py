"""
================================================================================
   DRONE HUNTER 2D -- PHASE 8 MISSION HARDENING AND REGRESSION TEST SUITE
================================================================================
Validates commit e979e1b: tactical multi-wave mission expansion.

Sections:
  1. Mission data structural integrity (5 sectors / 25 missions)
  2. Objective and encounter-sequence validity per mission
  3. All wave constant imports exist and contain valid enemy types
  4. Survive-mission duration contract
  5. Encounter system: sequential spawn, tracking, cleanup, completion
  6. High-density combat performance / bounded entity counts
"""

import os
import sys
import unittest
import pygame
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pygame.display.set_mode((1, 1))

from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE,
)
from src.data.mission_data import (
    MISSIONS, SECTORS_PHASE5,
    OBJECTIVE_DESTROY_ALL, OBJECTIVE_SURVIVE, OBJECTIVE_COMPLETE_ENCOUNTERS,
    OBJECTIVE_ASSAULT
)
from src.systems.encounter_system import (
    EncounterSystem,
    WAVE_SCOUTS_PATROL,
    WAVE_SCOUTS_ASSAULT,
    WAVE_SCOUTS_SWARM,
    WAVE_SHOOTERS_PAIR,
    WAVE_SHOOTERS_SQUAD,
    WAVE_HEAVY_ESCORT,
    WAVE_HEAVY_BATTLEGROUP,
    WAVE_SHIELD_VANGUARD,
    WAVE_ELITE_STRIKE_FORCE,
    SCOUT_SHOOTER_HEAVY_ENCOUNTER,
)
from src.systems.combat_director import CombatDirector
from src.systems.mission_system import MissionSystem, STATE_ACTIVE, STATE_COMPLETED
from src.entities.player import Player
from src.core.game_context import GameContext
from src.core.game_state import STATE_PLAYING

VALID_ENCOUNTER_TYPES = {TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE}
VALID_OBJECTIVES = {OBJECTIVE_DESTROY_ALL, OBJECTIVE_SURVIVE, OBJECTIVE_COMPLETE_ENCOUNTERS, OBJECTIVE_ASSAULT}

KNOWN_WAVE_CONSTANTS = [
    WAVE_SCOUTS_PATROL, WAVE_SCOUTS_ASSAULT, WAVE_SCOUTS_SWARM,
    WAVE_SHOOTERS_PAIR, WAVE_SHOOTERS_SQUAD,
    WAVE_HEAVY_ESCORT, WAVE_HEAVY_BATTLEGROUP,
    WAVE_SHIELD_VANGUARD, WAVE_ELITE_STRIKE_FORCE,
]

def _make_ctx():
    ctx = GameContext()
    ctx.state = STATE_PLAYING
    ctx.player = Player(pos=(1200.0, 700.0))
    return ctx

def _fast_forward(encounter, ctx, seconds):
    steps = int(seconds / 0.016)
    for _ in range(steps):
        encounter.update(0.016, ctx)

def _kill_all(encounter, ctx):
    for e in list(ctx.target_group):
        e.alive = False
        e.kill()
    encounter.update(0.016, ctx)


class TestMissionDataStructure(unittest.TestCase):
    def test_exactly_5_sectors(self):
        self.assertEqual(len(SECTORS_PHASE5), 5)

    def test_at_least_25_missions(self):
        self.assertGreaterEqual(len(MISSIONS), 25)

    def test_at_least_5_missions_per_sector(self):
        from collections import Counter
        counts = Counter(m["sector_id"] for m in MISSIONS)
        for sid in range(1, 6):
            self.assertGreaterEqual(counts[sid], 5, f"Sector {sid} must have at least 5 missions")

    def test_unique_mission_ids(self):
        ids = [m["id"] for m in MISSIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_valid_sector_ids(self):
        sector_ids = {s["id"] for s in SECTORS_PHASE5}
        for m in MISSIONS:
            self.assertIn(m["sector_id"], sector_ids)

    def test_mission_numbers_1_to_5_per_sector(self):
        from collections import defaultdict
        by_sector = defaultdict(list)
        for m in MISSIONS:
            by_sector[m["sector_id"]].append(m["mission_number"])
        for sid, nums in by_sector.items():
            base_nums = [n for n in nums if not str(n).endswith("_ALT")]
            self.assertEqual(sorted(set(base_nums)), [1, 2, 3, 4, 5],
                             f"Sector {sid} base missions must be numbered 1-5")

    def test_mission_id_format_matches_sector_and_number(self):
        for m in MISSIONS:
            mid = m["mission_number"]
            expected = f"S{m['sector_id']}_M{mid}"
            self.assertTrue(
                m["id"] == expected or m["id"].startswith(expected + "_"),
                f"Mission {m['id']} format mismatch"
            )

    def test_sector_names_correct(self):
        names = {s["id"]: s["name"] for s in SECTORS_PHASE5}
        self.assertEqual(names[1], "CYBER FACTORY")
        self.assertEqual(names[2], "CORE SECTOR")
        self.assertEqual(names[3], "REACTOR ZONE")
        self.assertEqual(names[4], "DEFENSE GRID")
        self.assertEqual(names[5], "DRONE COMMAND")

    def test_all_difficulty_values_in_range(self):
        for m in MISSIONS:
            self.assertIn(m.get("difficulty", 0), range(1, 6))


class TestMissionObjectivesAndSequences(unittest.TestCase):
    def test_every_mission_has_valid_objective(self):
        for m in MISSIONS:
            self.assertIn(m.get("objective"), VALID_OBJECTIVES,
                          f"Mission {m['id']} invalid objective")

    def test_every_mission_has_non_empty_encounter_sequence(self):
        for m in MISSIONS:
            seq = m.get("encounter_sequence", [])
            self.assertIsInstance(seq, list)
            self.assertGreater(len(seq), 0, f"Mission {m['id']} must have encounters")

    def test_every_encounter_composition_valid_enemy_types(self):
        for m in MISSIONS:
            for enc in m.get("encounter_sequence", []):
                if isinstance(enc, list):
                    for t in enc:
                        self.assertIn(t, VALID_ENCOUNTER_TYPES,
                                      f"Mission {m['id']}: invalid type '{t}'")
                elif isinstance(enc, dict):
                    t = enc.get("enemy_type")
                    if t:
                        self.assertIn(t, VALID_ENCOUNTER_TYPES)

    def test_survive_missions_have_duration(self):
        for m in MISSIONS:
            if m.get("objective") == OBJECTIVE_SURVIVE:
                self.assertIn("duration", m)
                self.assertGreater(m["duration"], 0)

    def test_all_wave_constants_non_empty(self):
        for wave in KNOWN_WAVE_CONSTANTS:
            self.assertIsInstance(wave, list)
            self.assertGreater(len(wave), 0)

    def test_all_wave_constants_valid_types(self):
        for wave in KNOWN_WAVE_CONSTANTS:
            for t in wave:
                self.assertIn(t, VALID_ENCOUNTER_TYPES)

    def test_no_none_in_encounter_sequences(self):
        for m in MISSIONS:
            for enc in m.get("encounter_sequence", []):
                self.assertIsNotNone(enc)


class TestSurviveMissionDurations(unittest.TestCase):
    def _dur(self, mid):
        for m in MISSIONS:
            if m["id"] == mid:
                return m.get("duration")
        self.fail(f"Mission {mid} not found")

    def test_s2_m4_is_45(self):
        self.assertEqual(self._dur("S2_M4"), 45)

    def test_s3_m2_is_75(self):
        self.assertEqual(self._dur("S3_M2"), 75)

    def test_s4_m2_is_75(self):
        self.assertEqual(self._dur("S4_M2"), 75)

    def test_s5_m2_is_90(self):
        self.assertEqual(self._dur("S5_M2"), 90)

    def test_mission_system_survive_timers(self):
        ctx = _make_ctx()
        enc_sys = EncounterSystem()
        director = CombatDirector(enc_sys)
        ms = MissionSystem()
        ms.start_mission(ctx, "S2_M4", director)
        self.assertAlmostEqual(ms.survive_timer, 45.0, places=3)
        ms.start_mission(ctx, "S3_M2", director)
        self.assertAlmostEqual(ms.survive_timer, 75.0, places=3)
        ms.start_mission(ctx, "S4_M2", director)
        self.assertAlmostEqual(ms.survive_timer, 75.0, places=3)
        ms.start_mission(ctx, "S5_M2", director)
        self.assertAlmostEqual(ms.survive_timer, 90.0, places=3)


WAVE_CASES = [
    ("WAVE_SCOUTS_PATROL",      WAVE_SCOUTS_PATROL,      3),
    ("WAVE_SCOUTS_ASSAULT",     WAVE_SCOUTS_ASSAULT,     4),
    ("WAVE_SCOUTS_SWARM",       WAVE_SCOUTS_SWARM,       5),
    ("WAVE_SHOOTERS_PAIR",      WAVE_SHOOTERS_PAIR,      3),
    ("WAVE_SHOOTERS_SQUAD",     WAVE_SHOOTERS_SQUAD,     5),
    ("WAVE_HEAVY_ESCORT",       WAVE_HEAVY_ESCORT,       4),
    ("WAVE_HEAVY_BATTLEGROUP",  WAVE_HEAVY_BATTLEGROUP,  5),
    ("WAVE_SHIELD_VANGUARD",    WAVE_SHIELD_VANGUARD,    4),
    ("WAVE_ELITE_STRIKE_FORCE", WAVE_ELITE_STRIKE_FORCE, 5),
]

def _make_wave_test(wave_name, wave_config, expected_count):
    class WaveTest(unittest.TestCase):
        def setUp(self):
            self.ctx = _make_ctx()
            self.enc = EncounterSystem(config=wave_config)

        def test_total_count_matches(self):
            self.assertEqual(self.enc.total_count, expected_count)

        def test_starts_idle(self):
            self.assertEqual(self.enc.state, "idle")

        def test_all_enemies_spawn(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 1.0 + expected_count * 1.15)
            self.assertEqual(self.enc.spawned_count, expected_count)
            self.assertEqual(len(self.enc.active_enemies), expected_count)
            self.assertEqual(len(self.ctx.target_group), expected_count)

        def test_spawner_suppressed(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 0.6)
            self.assertTrue(self.enc.is_suppressing_spawner)

        def test_no_extra_spawns(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 2.0 + expected_count * 1.5)
            self.assertEqual(self.enc.spawned_count, expected_count)

        def test_partial_kill_not_complete(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 1.0 + expected_count * 1.15)
            first = self.enc.active_enemies[0]
            first.kill()
            self.enc.update(0.016, self.ctx)
            self.assertFalse(self.enc.is_complete)
            self.assertEqual(len(self.enc.active_enemies), expected_count - 1)

        def test_no_duplicate_tracking(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 1.0 + expected_count * 1.15)
            ids = [id(e) for e in self.enc.active_enemies]
            self.assertEqual(len(ids), len(set(ids)))

        def test_all_killed_completes(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 1.0 + expected_count * 1.15)
            _kill_all(self.enc, self.ctx)
            self.assertTrue(self.enc.is_complete)
            self.assertEqual(len(self.enc.active_enemies), 0)
            self.assertEqual(self.enc.eliminated_count, expected_count)
            self.assertFalse(self.enc.is_suppressing_spawner)

        def test_reset_clears_state(self):
            self.enc.start()
            _fast_forward(self.enc, self.ctx, 1.0 + expected_count * 1.15)
            self.enc.reset()
            self.assertEqual(self.enc.state, "idle")
            self.assertEqual(self.enc.spawned_count, 0)
            self.assertEqual(self.enc.eliminated_count, 0)
            self.assertEqual(len(self.enc.active_enemies), 0)
            self.assertFalse(self.enc.is_active)

    WaveTest.__name__ = f"TestWave_{wave_name}"
    WaveTest.__qualname__ = f"TestWave_{wave_name}"
    return WaveTest

for _name, _cfg, _cnt in WAVE_CASES:
    _cls = _make_wave_test(_name, _cfg, _cnt)
    globals()[_cls.__name__] = _cls


class TestHighDensityStress(unittest.TestCase):
    def _full_cycle(self, wave_config, ctx):
        enc = EncounterSystem(config=wave_config)
        enc.start()
        _fast_forward(enc, ctx, 1.5 + len(wave_config) * 1.2)
        return enc

    def test_elite_bounded_entities(self):
        ctx = _make_ctx()
        enc = self._full_cycle(WAVE_ELITE_STRIKE_FORCE, ctx)
        self.assertLessEqual(len(ctx.target_group), len(WAVE_ELITE_STRIKE_FORCE))
        self.assertLessEqual(len(enc.active_enemies), len(WAVE_ELITE_STRIKE_FORCE))

    def test_elite_no_spawn_loop(self):
        ctx = _make_ctx()
        enc = EncounterSystem(config=WAVE_ELITE_STRIKE_FORCE)
        enc.start()
        _fast_forward(enc, ctx, 30.0)
        self.assertLessEqual(enc.spawned_count, len(WAVE_ELITE_STRIKE_FORCE))

    def test_sequential_waves_no_entity_leak(self):
        ctx = _make_ctx()
        for wave in [WAVE_ELITE_STRIKE_FORCE, WAVE_HEAVY_BATTLEGROUP, WAVE_ELITE_STRIKE_FORCE]:
            ctx.target_group.empty()
            enc = EncounterSystem(config=wave)
            enc.start()
            _fast_forward(enc, ctx, 1.5 + len(wave) * 1.2)
            _kill_all(enc, ctx)
            self.assertTrue(enc.is_complete)
            self.assertEqual(len(enc.active_enemies), 0)
        self.assertEqual(len(ctx.target_group), 0)

    def test_full_mission_s3_m3_completes(self):
        ctx = _make_ctx()
        enc_sys = EncounterSystem()
        director = CombatDirector(enc_sys)
        director.relief_after_encounter = 0.0  # instant relief for test speed
        ms = MissionSystem()
        ms.start_mission(ctx, "S3_M3", director)
        self.assertEqual(ms.state, STATE_ACTIVE)
        ticks = 0
        max_ticks = 10000
        while ms.state == STATE_ACTIVE and ticks < max_ticks:
            for e in list(ctx.target_group):
                e.alive = False
                e.kill()
            director.update(0.016, ctx)
            ms.update(0.016, ctx, director)
            ticks += 1
        self.assertLess(ticks, max_ticks, "S3_M3 must complete within virtual time budget")
        self.assertEqual(ms.state, STATE_COMPLETED)

    def test_full_mission_s5_m5_completes(self):
        ctx = _make_ctx()
        enc_sys = EncounterSystem()
        director = CombatDirector(enc_sys)
        director.relief_after_encounter = 0.0  # instant relief for test speed
        ms = MissionSystem()
        ms.start_mission(ctx, "S5_M5", director)
        self.assertEqual(ms.state, STATE_ACTIVE)
        ticks = 0
        max_ticks = 10000
        while ms.state == STATE_ACTIVE and ticks < max_ticks:
            for e in list(ctx.target_group):
                e.alive = False
                e.kill()
            director.update(0.016, ctx)
            ms.update(0.016, ctx, director)
            ticks += 1
        self.assertLess(ticks, max_ticks, "S5_M5 must complete within virtual time budget")
        self.assertEqual(ms.state, STATE_COMPLETED)

    def test_update_speed_300_ticks(self):
        ctx = _make_ctx()
        enc = EncounterSystem(config=WAVE_ELITE_STRIKE_FORCE)
        enc.start()
        t0 = time.perf_counter()
        for _ in range(300):
            enc.update(0.016, ctx)
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 2.0, f"300 ticks took {elapsed:.3f}s (budget 2.0s)")

    def test_active_enemies_bounded_every_tick(self):
        ctx = _make_ctx()
        enc = EncounterSystem(config=WAVE_ELITE_STRIKE_FORCE)
        max_count = len(WAVE_ELITE_STRIKE_FORCE)
        enc.start()
        for _ in range(500):
            enc.update(0.016, ctx)
            self.assertLessEqual(len(enc.active_enemies), max_count)

    def test_dead_enemy_removed_next_tick(self):
        ctx = _make_ctx()
        enc = EncounterSystem(config=WAVE_HEAVY_BATTLEGROUP)
        enc.start()
        _fast_forward(enc, ctx, 1.5 + len(WAVE_HEAVY_BATTLEGROUP) * 1.2)
        n = len(enc.active_enemies)
        self.assertEqual(n, len(WAVE_HEAVY_BATTLEGROUP))
        target = enc.active_enemies[0]
        target.alive = False
        target.kill()
        enc.update(0.016, ctx)
        self.assertEqual(len(enc.active_enemies), n - 1)


if __name__ == "__main__":
    unittest.main()
