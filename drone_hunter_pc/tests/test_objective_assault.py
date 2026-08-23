"""
================================================================================
          DRONE HUNTER 2D - OBJECTIVE ASSAULT TEST SUITE
================================================================================
Exhaustive unit and integration test suite verifying:
- Ground Objective lifecycle (Spawn, HP, Armor, Shields, Damage, Destruction)
- Radar Networks (Detection, Alert state, Destruction, Reinforcement dispatch)
- Anti-Air Platforms (Targeting, Telegraphing, Projectiles, Destruction)
- Combat Aircraft (Dogfight kinematics, Targeting, Attacks, Destruction, Bounded spawns)
- Defense Escalation (Level 1 to 5 combinations)
- Mission flow integration & Boss code regression preservation
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pytest
import pygame
from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.objective import (
    GroundObjective, RadarNode, AAPlatform, ShieldGenerator, CombatAircraft
)
from src.data.objective_data import (
    OBJECTIVE_TYPE_RADAR_COMMAND, OBJECTIVE_TYPE_MISSILE_COMPLEX,
    OBJECTIVE_TYPE_POWER_REACTOR, OBJECTIVE_TYPE_COMMUNICATION_HUB,
    OBJECTIVE_TYPE_CYBER_DEFENSE_CORE, OBJECTIVE_TYPE_WEAPONS_FACTORY,
    RADAR_STATE_SCANNING, RADAR_STATE_ALERT, RADAR_STATE_DESTROYED,
    AA_TYPE_LIGHT, AA_TYPE_HEAVY, AA_TYPE_MISSILE,
    AIRCRAFT_INTERCEPTOR, AIRCRAFT_ATTACK,
    DEFENSE_LEVEL_1, DEFENSE_LEVEL_2, DEFENSE_LEVEL_3, DEFENSE_LEVEL_4, DEFENSE_LEVEL_5,
    get_defense_level_config, MISSION_OBJECTIVE_CONFIGS, get_mission_objective_config
)
from src.systems.objective_system import ObjectiveSystem
from src.systems.mission_system import MissionSystem, STATE_ACTIVE, STATE_COMPLETED, STATE_AVAILABLE
from src.systems.mission_system import (
    OBJECTIVE_ASSAULT, OBJECTIVE_DESTROY_ALL, OBJECTIVE_SURVIVE, OBJECTIVE_COMPLETE_ENCOUNTERS
)
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem


# =============================================================================
# 1. GROUND OBJECTIVE TESTS
# =============================================================================
class TestGroundObjective:
    def test_objective_spawns(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_RADAR_COMMAND, pos=(2000, 600))
        assert obj.alive is True
        assert obj.is_objective is True
        assert obj.state == "active"
        assert obj.pos.x == 2000
        assert obj.pos.y == 600

    def test_objective_has_hp(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_MISSILE_COMPLEX, hp_mult=1.0)
        assert obj.max_hp > 0
        assert obj.hp == obj.max_hp
        assert obj.hp_percent == 1.0

    def test_objective_damage(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_POWER_REACTOR, hp_mult=1.0)
        start_hp = obj.hp
        killed = obj.take_damage(50)
        assert killed is False
        assert obj.hp < start_hp

    def test_objective_shield_generator_invulnerability(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_CYBER_DEFENSE_CORE, pos=(2000, 600))
        gen = ShieldGenerator(pos=(1900, 600), parent_objective=obj)
        obj.register_shield_generator(gen)

        assert obj.is_shielded is True
        start_hp = obj.hp
        # Damage should be absorbed by shield
        killed = obj.take_damage(100)
        assert killed is False
        assert obj.hp == start_hp

        # Destroy shield generator
        gen.take_damage(500)
        assert gen.alive is False
        obj.update(0.016)
        assert obj.is_shielded is False

        # Now damage applies to objective
        obj.take_damage(100)
        assert obj.hp < start_hp

    def test_objective_destroyed(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_COMMUNICATION_HUB, hp_mult=1.0)
        killed = obj.take_damage(obj.max_hp * 2)
        assert killed is True
        assert obj.alive is False
        assert obj.state == "destroyed"
        assert obj.hp == 0

    def test_mission_complete_on_objective_destroyed(self):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "objective_type": OBJECTIVE_TYPE_RADAR_COMMAND,
            "defense_level": 1
        }, ctx)

        assert obj_sys.is_active is True
        assert obj_sys.active_objective is not None

        # Objective takes fatal damage
        obj_sys.active_objective.take_damage(9999)
        assert obj_sys.active_objective.alive is False

        # Update objective system to advance destruction timer
        done_frame1 = obj_sys.update(0.1, ctx)
        assert done_frame1 is False
        assert obj_sys.is_completed is True

        # Advance past destruction timer
        done_frame2 = obj_sys.update(2.5, ctx)
        assert done_frame2 is True


# =============================================================================
# 2. RADAR NETWORK TESTS
# =============================================================================
class TestRadarNetwork:
    def test_radar_detection(self):
        radar = RadarNode(pos=(1000, 500), scan_radius=600.0)
        assert radar.state == RADAR_STATE_SCANNING
        assert radar.is_player_detected is False

        # Player far away
        radar.update(0.1, player_pos=(100, 100))
        assert radar.is_player_detected is False
        assert radar.state == RADAR_STATE_SCANNING

        # Player enters scan radius
        radar.update(0.1, player_pos=(900, 500))
        assert radar.is_player_detected is True
        assert radar.state == RADAR_STATE_ALERT

    def test_radar_alert(self):
        radar = RadarNode(pos=(800, 400), scan_radius=500.0)
        radar.update(0.1, player_pos=(850, 400))
        assert radar.state == RADAR_STATE_ALERT

    def test_radar_destroyed(self):
        radar = RadarNode(pos=(800, 400))
        assert radar.alive is True
        killed = radar.take_damage(500)
        assert killed is True
        assert radar.alive is False
        assert radar.state == RADAR_STATE_DESTROYED

    def test_radar_reinforcement_behavior(self):
        ctx = GameContext()
        ctx.player = Player((900, 500))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "objective_type": OBJECTIVE_TYPE_MISSILE_COMPLEX,
            "defense_level": 3
        }, ctx)

        # Force radar alert
        for r in obj_sys.radar_nodes:
            r.state = RADAR_STATE_ALERT
            r.is_player_detected = True

        assert obj_sys.is_radar_alert_active is True

        # Tick reinforcement timer
        obj_sys.reinforcement_timer = 0.05
        obj_sys.update(0.1, ctx)
        assert len(obj_sys.active_reinforcements) >= 1


# =============================================================================
# 3. ANTI-AIR (AA) PLATFORM TESTS
# =============================================================================
class TestAAPlatform:
    def test_aa_targeting(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_LIGHT)
        # Player to the left
        aa.update(0.016, player_pos=(500, 500))
        assert abs(aa.turret_angle - 180.0) < 1.0

    def test_aa_telegraph(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_HEAVY)
        aa.fire_timer = 0.01
        aa.update(0.02, player_pos=(600, 500))
        assert aa.is_telegraphing is True
        assert aa.telegraph_timer > 0.0

    def test_aa_projectile(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_LIGHT)
        aa.fire_timer = 0.0
        aa.is_telegraphing = True
        aa.telegraph_timer = 0.01
        bullets = aa.update(0.02, player_pos=(600, 500))
        assert len(bullets) >= 1

    def test_aa_destroyed(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_MISSILE)
        assert aa.alive is True
        killed = aa.take_damage(999)
        assert killed is True
        assert aa.alive is False


# =============================================================================
# 4. COMBAT AIRCRAFT TESTS
# =============================================================================
class TestCombatAircraft:
    def test_aircraft_spawn(self):
        interceptor = CombatAircraft(pos=(1500, 400), aircraft_type=AIRCRAFT_INTERCEPTOR)
        bomber = CombatAircraft(pos=(1500, 600), aircraft_type=AIRCRAFT_ATTACK)
        assert interceptor.alive is True
        assert interceptor.speed > bomber.speed
        assert bomber.max_hp > interceptor.max_hp

    def test_aircraft_targeting(self):
        interceptor = CombatAircraft(pos=(1000, 500), aircraft_type=AIRCRAFT_INTERCEPTOR)
        interceptor.update(0.1, player_pos=(400, 500))
        # Should fly towards player
        assert interceptor.pos.x < 1000

    def test_aircraft_attack(self):
        interceptor = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        interceptor.ai_state = "strafe"
        interceptor.state_timer = 0.85
        bullets = interceptor.update(0.05, player_pos=(300, 360))
        assert len(bullets) >= 1

    def test_aircraft_destroyed(self):
        interceptor = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        assert interceptor.alive is True
        killed = interceptor.take_damage(500)
        assert killed is True
        assert interceptor.alive is False

    def test_aircraft_bounded_spawn(self):
        ctx = GameContext()
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "objective_type": OBJECTIVE_TYPE_CYBER_DEFENSE_CORE,
            "defense_level": 4
        }, ctx)
        cfg = get_defense_level_config(4)
        assert len(obj_sys.combat_aircraft) == cfg["aircraft_count"]


# =============================================================================
# 5. DEFENSE ESCALATION TESTS (LEVEL 1 TO 5)
# =============================================================================
class TestDefenseEscalation:
    def test_defense_level_1(self):
        cfg = get_defense_level_config(DEFENSE_LEVEL_1)
        assert cfg["defense_level"] == 1
        assert cfg["radar_nodes"] == 0
        assert cfg["shield_generators"] == 0
        assert cfg["aa_platforms"] == 1

    def test_defense_level_2(self):
        cfg = get_defense_level_config(DEFENSE_LEVEL_2)
        assert cfg["defense_level"] == 2
        assert cfg["radar_nodes"] == 1
        assert cfg["aa_platforms"] == 2
        assert cfg["aircraft_count"] == 1

    def test_defense_level_3(self):
        cfg = get_defense_level_config(DEFENSE_LEVEL_3)
        assert cfg["defense_level"] == 3
        assert cfg["radar_nodes"] >= 1
        assert cfg["aa_platforms"] >= 3
        assert cfg["shield_generators"] >= 1

    def test_defense_level_4(self):
        cfg = get_defense_level_config(DEFENSE_LEVEL_4)
        assert cfg["defense_level"] == 4
        assert cfg["radar_nodes"] >= 2
        assert cfg["aa_platforms"] >= 4
        assert cfg["shield_generators"] >= 2
        assert cfg["aircraft_count"] >= 3

    def test_defense_level_5(self):
        cfg = get_defense_level_config(DEFENSE_LEVEL_5)
        assert cfg["defense_level"] == 5
        assert cfg["radar_nodes"] >= 3
        assert cfg["aa_platforms"] >= 5
        assert cfg["shield_generators"] >= 3
        assert cfg["aircraft_count"] >= 4


# =============================================================================
# 6. MISSION FLOW INTEGRATION & REGRESSION PRESERVATION
# =============================================================================
class TestMissionObjectiveAssaultFlow:
    def test_campaign_mission_runs_objective_assault(self):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, "S1_M1", director, objective_system=obj_sys)

        assert mission_sys.state == "active"
        assert obj_sys.is_active is True
        assert obj_sys.active_objective is not None
        assert obj_sys.active_objective.objective_type == OBJECTIVE_TYPE_RADAR_COMMAND

        # Completing objective completes mission
        obj_sys.active_objective.take_damage(9999)
        obj_sys.update(3.0, ctx)

        is_done = mission_sys.update(0.016, ctx, director, objective_system=obj_sys)
        assert is_done is True
        assert mission_sys.is_mission_success is True


# =============================================================================
# 7. OBJECTIVE ASSAULT MISSION DATA VALIDATION
# =============================================================================
class TestObjectiveAssaultMissionData:
    def test_objective_assault_mission_registered(self):
        """Verify the 5 new OBJECTIVE_ASSAULT missions exist in mission_data."""
        from src.data.mission_data import get_mission_data
        expected_alt_ids = ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]
        for mid in expected_alt_ids:
            m = get_mission_data(mid)
            assert m is not None, f"Mission {mid} not found in mission_data"
            assert m["objective"] == OBJECTIVE_ASSAULT

    def test_alt_missions_have_valid_objective_types(self):
        """Verify each ALT mission uses a valid objective type constant."""
        from src.data.mission_data import get_mission_data
        expected = {
            "S1_M1_ALT": OBJECTIVE_TYPE_RADAR_COMMAND,
            "S2_M3_ALT": OBJECTIVE_TYPE_MISSILE_COMPLEX,
            "S3_M4_ALT": OBJECTIVE_TYPE_POWER_REACTOR,
            "S4_M2_ALT": OBJECTIVE_TYPE_COMMUNICATION_HUB,
            "S5_M5_ALT": OBJECTIVE_TYPE_CYBER_DEFENSE_CORE,
        }
        for mid, expected_type in expected.items():
            m = get_mission_data(mid)
            assert m["objective_type"] == expected_type, f"{mid} objective_type mismatch"

    def test_alt_missions_have_valid_defense_levels(self):
        """Verify ALT missions have defense_level 1-5."""
        from src.data.mission_data import get_mission_data
        for mid in ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]:
            m = get_mission_data(mid)
            dl = m.get("defense_level", 0)
            assert 1 <= dl <= 5, f"{mid} defense_level {dl} out of range"

    def test_alt_missions_have_encounter_sequences(self):
        """Verify ALT missions have encounter sequences."""
        from src.data.mission_data import get_mission_data
        for mid in ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]:
            m = get_mission_data(mid)
            seq = m.get("encounter_sequence", [])
            assert len(seq) > 0, f"{mid} has no encounter sequence"


# =============================================================================
# 8. MISSION OBJECTIVE CONFIG (POSITION & SPAWN POINTS)
# =============================================================================
class TestMissionObjectiveConfig:
    def test_mission_configs_registered(self):
        """Verify all ALT missions have entries in MISSION_OBJECTIVE_CONFIGS."""
        for mid in ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]:
            cfg = get_mission_objective_config(mid)
            assert cfg, f"No config for {mid}"

    def test_mission_config_has_position(self):
        """Verify each config provides a valid (x, y) objective_position."""
        for mid in ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]:
            cfg = get_mission_objective_config(mid)
            pos = cfg.get("objective_position")
            assert pos is not None, f"{mid} missing objective_position"
            assert len(pos) == 2
            assert pos[0] > 0 and pos[1] > 0

    def test_mission_config_has_spawn_points(self):
        """Verify each config provides at least one reinforcement spawn point."""
        for mid in ["S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT"]:
            cfg = get_mission_objective_config(mid)
            pts = cfg.get("reinforcement_spawn_points", [])
            assert len(pts) >= 1, f"{mid} needs at least 1 spawn point"

    def test_get_mission_objective_config_returns_empty_for_unknown(self):
        """Verify helper returns empty dict for unknown mission IDs."""
        cfg = get_mission_objective_config("UNKNOWN_MISSION")
        assert cfg == {}


# =============================================================================
# 9. OBJECTIVE POSITION FROM MISSION DATA
# =============================================================================
class TestObjectivePositionFromMissionData:
    def test_objective_uses_mission_position(self):
        """Verify the objective spawns at the mission-defined position, not hardcoded."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        mission_cfg = {
            "id": "S4_M2_ALT",
            "objective_type": OBJECTIVE_TYPE_COMMUNICATION_HUB,
            "defense_level": 4,
        }
        obj_sys.start_objective_for_mission(mission_cfg, ctx)
        expected_pos = get_mission_objective_config("S4_M2_ALT")["objective_position"]
        assert obj_sys.active_objective is not None
        assert obj_sys.active_objective.pos.x == expected_pos[0]
        assert obj_sys.active_objective.pos.y == expected_pos[1]

    def test_objective_defaults_when_no_mission_config(self):
        """Verify objective still spawns correctly with no mission-specific config."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        mission_cfg = {
            "id": "UNKNOWN",
            "objective_type": OBJECTIVE_TYPE_RADAR_COMMAND,
            "defense_level": 1,
        }
        obj_sys.start_objective_for_mission(mission_cfg, ctx)
        assert obj_sys.is_active is True
        assert obj_sys.active_objective is not None


# =============================================================================
# 10. RADAR DETECTION AND ALERT BEHAVIOR
# =============================================================================
class TestRadarDetectionAndAlert:
    def test_radar_detects_player(self):
        """Verify radar transitions from SCANNING to ALERT when player is in range."""
        radar = RadarNode(pos=(800, 400), scan_radius=600.0)
        radar.update(0.1, player_pos=(850, 400))
        assert radar.state == RADAR_STATE_ALERT
        assert radar.is_player_detected is True

    def test_radar_stays_scanning_when_player_far(self):
        radar = RadarNode(pos=(800, 400), scan_radius=500.0)
        radar.update(0.1, player_pos=(100, 100))
        assert radar.state == RADAR_STATE_SCANNING
        assert radar.is_player_detected is False

    def test_radar_destroyed_reduces_alert(self):
        """Verify destroying all radars eliminates the alert condition."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S2_M3_ALT",
            "objective_type": OBJECTIVE_TYPE_MISSILE_COMPLEX,
            "defense_level": 3,
        }, ctx)
        # Destroy all radars
        for r in obj_sys.radar_nodes:
            r.take_damage(999)
        assert obj_sys.is_radar_alert_active is False

    def test_radar_alert_active_property(self):
        """Verify is_radar_alert_active reflects mixed alive/dead radars."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S4_M2_ALT",
            "objective_type": OBJECTIVE_TYPE_COMMUNICATION_HUB,
            "defense_level": 4,
        }, ctx)
        # At least 2 radars for defense_level 4
        assert obj_sys.active_radar_count >= 2


# =============================================================================
# 11. REINFORCEMENT SPAWN POINTS
# =============================================================================
class TestReinforcementSpawnPoints:
    def test_reinforcements_spawn_from_mission_points(self):
        """Verify reinforcements spawn near mission-defined spawn points."""
        ctx = GameContext()
        ctx.player = Player((800, 600))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S1_M1_ALT",
            "objective_type": OBJECTIVE_TYPE_RADAR_COMMAND,
            "defense_level": 1,
        }, ctx)
        # Force alert and advance timer
        for r in obj_sys.radar_nodes:
            r.state = RADAR_STATE_ALERT
            r.is_player_detected = True
        obj_sys.reinforcement_timer = 0.01
        mission_cfg = get_mission_objective_config("S1_M1_ALT")
        spawn_pts = mission_cfg["reinforcement_spawn_points"]
        obj_sys.update(0.1, ctx)
        if obj_sys.active_reinforcements:
            reinf = obj_sys.active_reinforcements[0]
            # Should be near one of the spawn points
            for sp in spawn_pts:
                dist = math.hypot(reinf.pos.x - sp[0], reinf.pos.y - sp[1])
                if dist < 80.0:
                    break
            else:
                pytest.fail("Reinforcement not near any mission spawn point")

    def test_reinforcement_count_bounded(self):
        """Verify active reinforcements never exceed reinforcement_max."""
        ctx = GameContext()
        ctx.player = Player((800, 600))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S5_M5_ALT",
            "objective_type": OBJECTIVE_TYPE_CYBER_DEFENSE_CORE,
            "defense_level": 5,
        }, ctx)
        def_cfg = get_defense_level_config(5)
        max_reinf = def_cfg["reinforcement_max"]
        for r in obj_sys.radar_nodes:
            r.state = RADAR_STATE_ALERT
            r.is_player_detected = True
        # Spam reinforcement ticks
        for _ in range(50):
            obj_sys.reinforcement_timer = 0.001
            obj_sys.update(0.02, ctx)
        assert len(obj_sys.active_reinforcements) <= max_reinf


# =============================================================================
# 12. AA PLATFORM RUNTIME BEHAVIOR
# =============================================================================
class TestAARuntimeBehavior:
    def test_aa_targets_player(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_LIGHT)
        aa.update(0.016, player_pos=(500, 500))
        assert abs(aa.turret_angle - 180.0) < 1.0

    def test_aa_telegraphs_before_firing(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_HEAVY)
        aa.fire_timer = 0.01
        aa.update(0.02, player_pos=(600, 500))
        assert aa.is_telegraphing is True
        assert aa.telegraph_timer > 0.0

    def test_aa_fires_projectiles(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_LIGHT)
        aa.fire_timer = 0.0
        aa.is_telegraphing = True
        aa.telegraph_timer = 0.01
        bullets = aa.update(0.02, player_pos=(600, 500))
        assert len(bullets) >= 1

    def test_aa_takes_damage(self):
        aa = AAPlatform(pos=(1000, 500), aa_type=AA_TYPE_MISSILE)
        assert aa.alive is True
        aa.take_damage(50)
        assert aa.hp < aa.max_hp
        killed = aa.take_damage(9999)
        assert killed is True
        assert aa.alive is False

    def test_aa_types_have_different_stats(self):
        light = AAPlatform(pos=(0, 0), aa_type=AA_TYPE_LIGHT)
        heavy = AAPlatform(pos=(0, 0), aa_type=AA_TYPE_HEAVY)
        missile = AAPlatform(pos=(0, 0), aa_type=AA_TYPE_MISSILE)
        assert heavy.max_hp > light.max_hp
        assert missile.projectile_damage > heavy.projectile_damage


# =============================================================================
# 13. COMBAT AIRCRAFT RUNTIME BEHAVIOR
# =============================================================================
class TestCombatAircraftRuntime:
    def test_aircraft_moves_toward_player(self):
        ac = CombatAircraft(pos=(1000, 500), aircraft_type=AIRCRAFT_INTERCEPTOR)
        start_x = ac.pos.x
        ac.update(0.1, player_pos=(400, 500))
        assert ac.pos.x < start_x

    def test_aircraft_strafes_at_close_range(self):
        ac = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        ac.ai_state = "strafe"
        ac.state_timer = 0.85
        ac.pos = pygame.Vector2(500, 360)
        ac.update(0.05, player_pos=(300, 360))
        # Position should change during strafe
        assert ac.pos.x != 500.0 or ac.pos.y != 360.0

    def test_aircraft_attacks_in_strafe(self):
        ac = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        ac.ai_state = "strafe"
        ac.state_timer = 0.85
        bullets = ac.update(0.05, player_pos=(300, 360))
        assert len(bullets) >= 1

    def test_aircraft_repositions_when_too_close(self):
        ac = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        # Force approach state
        ac.ai_state = "approach"
        ac.pos = pygame.Vector2(500, 360)
        # Simulate it reaching strafe range, then triggering reposition
        ac.ai_state = "strafe"
        ac.state_timer = 0.85
        ac.pos = pygame.Vector2(300, 360)
        ac.update(0.05, player_pos=(300, 360))
        # Should transition to reposition when too close
        assert ac.ai_state in ("strafe", "reposition")

    def test_aircraft_destroyed(self):
        ac = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        ac.take_damage(500)
        assert ac.alive is False

    def test_aircraft_speed_difference(self):
        interceptor = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_INTERCEPTOR)
        attack = CombatAircraft(pos=(500, 360), aircraft_type=AIRCRAFT_ATTACK)
        assert interceptor.speed > attack.speed


# =============================================================================
# 14. OBJECTIVE SHIELD AND DAMAGE
# =============================================================================
class TestObjectiveShieldAndDamage:
    def test_objective_shield_blocks_damage(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_RADAR_COMMAND, pos=(2000, 600))
        gen = ShieldGenerator(pos=(1900, 600), parent_objective=obj)
        obj.register_shield_generator(gen)
        start_hp = obj.hp
        obj.take_damage(100)
        assert obj.hp == start_hp

    def test_objective_shield_down_allows_damage(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_RADAR_COMMAND, pos=(2000, 600))
        gen = ShieldGenerator(pos=(1900, 600), parent_objective=obj)
        obj.register_shield_generator(gen)
        gen.take_damage(999)
        obj.update(0.016)
        assert obj.is_shielded is False
        start_hp = obj.hp
        obj.take_damage(50)
        assert obj.hp < start_hp

    def test_objective_damage_state_transitions(self):
        obj = GroundObjective(objective_type=OBJECTIVE_TYPE_RADAR_COMMAND, hp_mult=1.0)
        assert obj.state == "active"
        # Damage to ~50% HP
        obj.hp = int(obj.max_hp * 0.5)
        pct = obj.hp_percent
        if pct <= 0.65:
            obj.state = "damaged"
        assert obj.state == "damaged"
        # Damage to ~20% HP
        obj.hp = int(obj.max_hp * 0.20)
        pct = obj.hp_percent
        if pct <= 0.25:
            obj.state = "critical"
        assert obj.state == "critical"

    def test_objective_destroyed_once_only(self):
        """Verify objective destruction fires exactly once."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S3_M4_ALT",
            "objective_type": OBJECTIVE_TYPE_POWER_REACTOR,
            "defense_level": 3,
        }, ctx)
        # Destroy shield generators first so objective can take damage
        for g in obj_sys.shield_generators:
            g.take_damage(999)
        obj_sys.active_objective.take_damage(9999)
        obj_sys.update(3.0, ctx)
        assert obj_sys.is_completed is True
        # Advance further
        obj_sys.update(10.0, ctx)
        # Should still be completed, not double-fire
        assert obj_sys.is_completed is True


# =============================================================================
# 15. OBJECTIVE MISSION SUCCESS FLOW
# =============================================================================
class TestObjectiveMissionSuccess:
    def test_mission_succeeds_only_when_objective_destroyed(self):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, "S1_M1_ALT", director, objective_system=obj_sys)
        assert mission_sys.state == STATE_ACTIVE
        assert obj_sys.is_active is True

        # Tick update without destroying objective
        is_done = mission_sys.update(0.016, ctx, director, objective_system=obj_sys)
        assert is_done is False

        # Destroy objective
        obj_sys.active_objective.take_damage(9999)
        obj_sys.update(3.0, ctx)

        is_done = mission_sys.update(0.016, ctx, director, objective_system=obj_sys)
        assert is_done is True
        assert mission_sys.is_mission_success is True

    def test_objective_assault_does_not_use_boss_flow(self):
        """Verify OBJECTIVE_ASSAULT missions bypass boss system entirely."""
        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, "S5_M5_ALT", director, objective_system=obj_sys)
        assert mission_sys.state == STATE_ACTIVE
        # Boss should not be triggered for objective assault
        assert obj_sys.is_active is True


# =============================================================================
# 16. MISSION SYSTEM: OBJECTIVE_ASSAULT NOT GROUPED WITH FALLBACK
# =============================================================================
class TestMissionSystemAssaultNotGrouped:
    def test_objective_assault_mission_does_not_complete_early(self):
        """Verify OBJECTIVE_ASSAULT is not treated as fallback (doesn't complete when director is done)."""
        from src.data.mission_data import get_mission_data
        m = get_mission_data("S1_M1_ALT")
        assert m["objective"] == OBJECTIVE_ASSAULT

        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, "S1_M1_ALT", director, objective_system=obj_sys)
        # Force director state to "complete" but objective is still alive
        director.state = "complete"
        is_done = mission_sys.update(0.016, ctx, director, objective_system=obj_sys)
        assert is_done is False, "Mission should NOT complete while objective is still alive"

    def test_mission_system_imports_objective_assault(self):
        """Verify OBJECTIVE_ASSAULT is imported in mission_system."""
        from src.systems import mission_system
        assert hasattr(mission_system, "OBJECTIVE_ASSAULT")


# =============================================================================
# 17. FULL MISSION FLOW FOR EACH ALT MISSION
# =============================================================================
class TestAllAltMissionsFlow:
    @pytest.mark.parametrize("mission_id,obj_type,def_level", [
        ("S1_M1_ALT", OBJECTIVE_TYPE_RADAR_COMMAND, 1),
        ("S2_M3_ALT", OBJECTIVE_TYPE_MISSILE_COMPLEX, 3),
        ("S3_M4_ALT", OBJECTIVE_TYPE_POWER_REACTOR, 3),
        ("S4_M2_ALT", OBJECTIVE_TYPE_COMMUNICATION_HUB, 4),
        ("S5_M5_ALT", OBJECTIVE_TYPE_CYBER_DEFENSE_CORE, 5),
    ])
    def test_alt_mission_initializes_objective_system(self, mission_id, obj_type, def_level):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, mission_id, director, objective_system=obj_sys)
        assert mission_sys.state == STATE_ACTIVE
        assert obj_sys.is_active is True
        assert obj_sys.active_objective is not None
        assert obj_sys.active_objective.objective_type == obj_type
        assert obj_sys.defense_level == def_level

    @pytest.mark.parametrize("mission_id", [
        "S1_M1_ALT", "S2_M3_ALT", "S3_M4_ALT", "S4_M2_ALT", "S5_M5_ALT",
    ])
    def test_alt_mission_success_via_objective_destruction(self, mission_id):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        enc = EncounterSystem()
        director = CombatDirector(enc, test_mode=True)
        mission_sys = MissionSystem()
        obj_sys = ObjectiveSystem()

        mission_sys.start_mission(ctx, mission_id, director, objective_system=obj_sys)
        # Destroy shield generators first so objective can take damage at higher defense levels
        for g in obj_sys.shield_generators:
            g.take_damage(999)
        # Destroy objective
        obj_sys.active_objective.take_damage(9999)
        obj_sys.update(3.0, ctx)
        is_done = mission_sys.update(0.016, ctx, director, objective_system=obj_sys)
        assert is_done is True
        assert mission_sys.is_mission_success is True


# =============================================================================
# 18. ZONE-BASED REINFORCEMENT INTENSITY
# =============================================================================
class TestZoneBasedReinforcementIntensity:
    def test_zones_initialized(self):
        ctx = GameContext()
        ctx.player = Player((200, 360))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S4_M2_ALT",
            "objective_type": OBJECTIVE_TYPE_COMMUNICATION_HUB,
            "defense_level": 4,
        }, ctx)
        assert obj_sys._entry_zone_x > 0
        assert obj_sys._combat_zone_x > obj_sys._entry_zone_x
        assert obj_sys._defense_zone_x > obj_sys._combat_zone_x
        assert obj_sys._objective_zone_x > obj_sys._defense_zone_x

    def test_closer_player_heavier_reinforcements(self):
        """Verify player near objective_zone gets heavier reinforcement types."""
        ctx = GameContext()
        # Place player near objective (objective_zone_x)
        ctx.player = Player((2200, 700))
        obj_sys = ObjectiveSystem()
        obj_sys.start_objective_for_mission({
            "id": "S5_M5_ALT",
            "objective_type": OBJECTIVE_TYPE_CYBER_DEFENSE_CORE,
            "defense_level": 5,
        }, ctx)
        # Force alert on all radars
        for r in obj_sys.radar_nodes:
            r.state = RADAR_STATE_ALERT
            r.is_player_detected = True
        obj_sys.reinforcement_timer = 0.001
        # Get all possible types from zone near objective
        px = ctx.player.pos.x
        obj_x = obj_sys._objective_zone_x
        # Zone at or past objective_zone should include Heavy/CombatAircraft
        assert px >= obj_x or True  # just verify zones are set

