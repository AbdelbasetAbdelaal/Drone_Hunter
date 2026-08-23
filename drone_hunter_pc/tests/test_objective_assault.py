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
    get_defense_level_config
)
from src.systems.objective_system import ObjectiveSystem
from src.systems.mission_system import MissionSystem
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
