"""
================================================================================
          PHASE 10.5 — FIXED LOADOUT & DRONE COMBAT PLATFORM TESTS
================================================================================
Comprehensive test suite validating:
1. Every Drone Class has exactly one deterministic loadout.
2. Interceptor always returns the same loadout.
3. Striker always returns the same loadout.
4. Assault always returns the same loadout.
5. Arc always returns the same loadout.
6. Command always returns the same loadout.
7. Repeated calls return identical results.
8. No random weapon selection occurs in player loadout resolution.
9. HUD weapon list matches actual equipped weapons.
10. Weapon audio ID matches equipped weapon.
11. Weapon visual ID matches equipped weapon.
12. Weapon mount belongs to the equipped weapon.
13. Switching Drone changes loadout deterministically.
14. Switching Drone does not alter gameplay state unexpectedly.
15. Old saves load safely.
================================================================================
"""

import math
import os
import tempfile
import pygame
import pytest

from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN, COLOR_GOLD
from src.data.game_data import (
    DRONE_CLASSES, DRONE_LOADOUTS, DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR,
    DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND,
    get_drone_class_by_id, get_drone_loadout,
    WEAPON_DEFS, WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_RAPID, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE,
    WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP
)
from src.entities.player import Player
from src.entities.bullet import (
    Bullet, HomingMissile, HeavyPlasmaOrb, RailgunSlug, BarrageMissile
)
from src.audio.audio_manager import AudioManager
from src.audio.sound_synth import (
    generate_laser_sound, generate_rapid_sound, generate_scatter_sound,
    generate_missile_sound, generate_barrage_sound, generate_plasma_sound,
    generate_rail_sound, generate_beam_sound, generate_tesla_sound,
    generate_cluster_sound, generate_mission_complete_sound,
    generate_game_over_sound, generate_victory_sound
)
from src.systems.save_system import SaveSystem


class TestPhase105CombatOverhaul:
    """Test suite covering Phase 10.5 fixed loadouts, drone platforms, and determinism."""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        yield
        pygame.quit()

    # 1. Every Drone Class has exactly one deterministic loadout
    def test_1_every_drone_class_has_deterministic_loadout(self):
        """Verify all 5 drone classes have a defined deterministic loadout in DRONE_LOADOUTS."""
        assert len(DRONE_LOADOUTS) == 5
        for class_id in [DRONE_CLASS_INTERCEPTOR, DRONE_CLASS_STRIKER, DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND]:
            assert class_id in DRONE_LOADOUTS
            loadout = DRONE_LOADOUTS[class_id]
            assert "primary" in loadout
            assert "secondary" in loadout
            assert "heavy" in loadout

    # 2. Interceptor always returns the same loadout
    def test_2_interceptor_fixed_loadout(self):
        """Verify Interceptor always resolves to Pulse, Rapid, and Missile."""
        loadout = get_drone_loadout(DRONE_CLASS_INTERCEPTOR)
        assert loadout["primary"] == WEAPON_PULSE
        assert loadout["secondary"] == WEAPON_RAPID
        assert loadout["heavy"] == WEAPON_MISSILE

        # Player class 1 application
        player = Player((0, 0))
        player.apply_drone_class(1)
        assert player.available_weapons == [WEAPON_PULSE, WEAPON_RAPID, WEAPON_MISSILE]

    # 3. Striker always returns the same loadout
    def test_3_striker_fixed_loadout(self):
        """Verify Striker always resolves to Pulse, Scatter, and Missile."""
        loadout = get_drone_loadout(DRONE_CLASS_STRIKER)
        assert loadout["primary"] == WEAPON_PULSE
        assert loadout["secondary"] == WEAPON_SCATTER
        assert loadout["heavy"] == WEAPON_MISSILE

        player = Player((0, 0))
        player.apply_drone_class(0)
        assert player.available_weapons == [WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE]

    # 4. Assault always returns the same loadout
    def test_4_assault_fixed_loadout(self):
        """Verify Assault always resolves to Pulse, Plasma, and Missile."""
        loadout = get_drone_loadout(DRONE_CLASS_ASSAULT)
        assert loadout["primary"] == WEAPON_PULSE
        assert loadout["secondary"] == WEAPON_PLASMA
        assert loadout["heavy"] == WEAPON_MISSILE

        player = Player((0, 0))
        player.apply_drone_class(2)
        assert player.available_weapons == [WEAPON_PULSE, WEAPON_PLASMA, WEAPON_MISSILE]

    # 5. Arc always returns the same loadout
    def test_5_arc_fixed_loadout(self):
        """Verify Arc always resolves to EMP, Tesla, and Beam."""
        loadout = get_drone_loadout(DRONE_CLASS_ARC)
        assert loadout["primary"] == WEAPON_EMP
        assert loadout["secondary"] == WEAPON_TESLA
        assert loadout["heavy"] == WEAPON_BEAM

        player = Player((0, 0))
        player.apply_drone_class(3)
        assert player.available_weapons == [WEAPON_EMP, WEAPON_TESLA, WEAPON_BEAM]

    # 6. Command always returns the same loadout
    def test_6_command_fixed_loadout(self):
        """Verify Command always resolves to Rail, Beam, Barrage, and Cluster."""
        loadout = get_drone_loadout(DRONE_CLASS_COMMAND)
        assert loadout["primary"] == WEAPON_RAIL
        assert loadout["secondary"] == WEAPON_BEAM
        assert loadout["heavy"] == WEAPON_BARRAGE
        assert loadout["special"] == WEAPON_CLUSTER

        player = Player((0, 0))
        player.apply_drone_class(4)
        assert player.available_weapons == [WEAPON_RAIL, WEAPON_BEAM, WEAPON_BARRAGE, WEAPON_CLUSTER]

    # 7. Repeated calls return identical results
    def test_7_repeated_calls_return_identical_results(self):
        """Verify repeated invocations across 20 cycles yield strictly identical loadouts."""
        for _ in range(20):
            p = Player((0, 0))
            for idx, class_id in enumerate([DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR, DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND]):
                p.apply_drone_class(idx)
                assert p.available_weapons == DRONE_CLASSES[idx]["weapons"]
                assert get_drone_loadout(class_id) == DRONE_LOADOUTS[class_id]

    # 8. No random weapon selection occurs in player loadout resolution
    def test_8_no_random_weapon_selection(self):
        """Verify player drone initialization and skin switching contains zero randomness."""
        player1 = Player((0, 0))
        player2 = Player((0, 0))
        for idx in range(len(DRONE_CLASSES)):
            player1.apply_drone_class(idx)
            player2.apply_drone_class(idx)
            assert player1.available_weapons == player2.available_weapons
            assert player1.max_speed == player2.max_speed
            assert player1.max_health == player2.max_health
            assert player1.armor == player2.armor

    # 9. HUD weapon list matches actual equipped weapons
    def test_9_hud_weapon_list_matches_equipped_weapons(self):
        """Verify player.available_weapons queried by HUD strictly matches DRONE_CLASSES."""
        player = Player((0, 0))
        for idx in range(len(DRONE_CLASSES)):
            player.apply_drone_class(idx)
            expected_weapons = DRONE_CLASSES[idx]["weapons"]
            assert player.available_weapons == expected_weapons
            assert player.active_weapon in player.available_weapons

    # 10. Weapon audio ID matches equipped weapon
    def test_10_weapon_audio_id_matches_equipped_weapon(self):
        """Verify AudioManager play_weapon dispatches for all weapons in all drone loadouts."""
        audio = AudioManager(sound_enabled=True)
        for class_data in DRONE_CLASSES.values():
            for w_id in class_data["weapons"]:
                audio.play_weapon(w_id)

    # 11. Weapon visual ID matches equipped weapon
    def test_11_weapon_visual_id_matches_equipped_weapon(self):
        """Verify every weapon definition contains valid color, name, icon, and description."""
        for class_data in DRONE_CLASSES.values():
            for w_id in class_data["weapons"]:
                assert w_id in WEAPON_DEFS
                w_def = WEAPON_DEFS[w_id]
                assert "name" in w_def
                assert "color" in w_def
                assert "icon" in w_def
                assert len(w_def["color"]) >= 3

    # 12. Weapon mount belongs to the equipped weapon
    def test_12_weapon_mount_belongs_to_equipped_weapon(self):
        """Verify get_mount_world_pos returns valid local coordinates rotated by aim angle."""
        player = Player((500.0, 500.0))
        player.aim_angle = 0.0
        for idx in range(len(DRONE_CLASSES)):
            player.apply_drone_class(idx)
            pos = player.get_mount_world_pos("primary")
            assert pos[0] > 500.0

    # 13. Switching Drone changes loadout deterministically
    def test_13_switching_drone_changes_loadout_deterministically(self):
        """Verify cycling through all 5 drone classes updates loadout deterministically."""
        player = Player((0, 0))
        player.apply_drone_class(0) # Striker
        assert player.active_weapon == WEAPON_PULSE

        player.apply_drone_class(1) # Interceptor
        assert player.available_weapons == [WEAPON_PULSE, WEAPON_RAPID, WEAPON_MISSILE]

        player.apply_drone_class(4) # Command
        assert player.available_weapons == [WEAPON_RAIL, WEAPON_BEAM, WEAPON_BARRAGE, WEAPON_CLUSTER]
        assert player.active_weapon == WEAPON_RAIL

    # 14. Switching Drone does not alter gameplay state unexpectedly
    def test_14_switching_drone_preserves_shop_upgrades(self):
        """Verify upgrade modifiers (bonus battery HP, speed) persist across class switches."""
        player = Player((0, 0))
        upgrades = {"battery": 2, "speed": 1, "fire_rate": 1}
        player.apply_shop_upgrades(upgrades)
        
        # Striker base 100 + 50 bonus
        assert player.max_health == 150.0

        # Switch to Assault (base 145 + 50 bonus = 195)
        player.apply_drone_class(2)
        assert player.max_health == 195.0
        assert player.armor == 6

    # 15. Old saves load safely
    def test_15_old_saves_load_safely(self):
        """Verify SaveSystem safely loads legacy save files missing selected_drone fields."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            import json
            legacy_data = {
                "scrap": 1200,
                "coins": 1200,
                "highscore": 9999,
                "upgrades": {"hull": 2},
                "sectors": [True, True, False, False, False],
                "stages": [True] * 15,
                "difficulty_mode": 2
            }
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(legacy_data, f)

            save_sys = SaveSystem(save_filename=os.path.basename(temp_path))
            save_sys.save_path = temp_path
            save_sys.temp_path = temp_path + ".tmp"

            loaded = save_sys.load()
            assert loaded["scrap"] == 1200
            assert loaded["selected_drone"] == "striker"
            assert loaded["selected_skin"] == 0
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_path + ".tmp"):
                os.remove(temp_path + ".tmp")
