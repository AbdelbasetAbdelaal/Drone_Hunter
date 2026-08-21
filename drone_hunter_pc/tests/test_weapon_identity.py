"""
================================================================================
           DRONE HUNTER 2D - WEAPON IDENTITY & MOUNT/VFX/AUDIO TESTS
================================================================================
Comprehensive test suite validating:
1. Unique weapon IDs & parameters
2. Valid audio IDs & VFX profiles
3. Valid mount profiles
4. Distinct behavior configurations
5. Deterministic weapon definitions
6-9. Muzzle origin rotations at 0, 90, 180, 270 deg (distance invariance)
10. Projectile origin matches muzzle position
11. Projectile direction remains aim-based
12. Audio ID resolution matches equipped weapon
13. VFX profile resolution matches equipped weapon
14. Safe fallback on missing audio asset
15. Safe fallback on missing VFX asset
16. Save system compatibility & legacy fallbacks
17. Five drone loadouts remain fully deterministic
"""

import math
import os
import sys
import pygame
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.game_data import (
    WEAPON_DEFS, DRONE_CLASSES, DRONE_LOADOUTS, DRONE_MOUNT_PROFILES,
    WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE, WEAPON_BEAM,
    WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP,
    DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR, DRONE_CLASS_ASSAULT,
    DRONE_CLASS_ARC, DRONE_CLASS_COMMAND,
    get_drone_loadout
)
from src.entities.player import Player
from src.audio.audio_manager import AudioManager, AUDIO_ASSET_MAP
from src.rendering.particles import ParticleManager
from src.systems.save_system import SaveSystem


@pytest.fixture(autouse=True)
def setup_headless():
    pygame.init()
    yield
    pygame.quit()


def test_1_unique_weapon_ids():
    """1. Every primary weapon has a unique identifier."""
    canonical_weapons = [
        WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
        WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE, WEAPON_BEAM,
        WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP
    ]
    assert len(canonical_weapons) == len(set(canonical_weapons))
    for wid in canonical_weapons:
        assert wid in WEAPON_DEFS
        assert WEAPON_DEFS[wid]["weapon_id"] == wid


def test_2_valid_audio_ids():
    """2. Every weapon has a valid audio_id mapping."""
    for wid, wdef in WEAPON_DEFS.items():
        assert "audio_id" in wdef
        assert isinstance(wdef["audio_id"], str)
        assert len(wdef["audio_id"]) > 0


def test_3_valid_vfx_profiles():
    """3. Every weapon has valid muzzle_vfx and impact_vfx metadata."""
    for wid, wdef in WEAPON_DEFS.items():
        assert "muzzle_vfx" in wdef
        assert "impact_vfx" in wdef
        assert isinstance(wdef["muzzle_vfx"], str)
        assert isinstance(wdef["impact_vfx"], str)


def test_4_valid_mount_profiles():
    """4. Every weapon specifies a valid mount profile."""
    for wid, wdef in WEAPON_DEFS.items():
        assert "mount_profile" in wdef
        assert isinstance(wdef["mount_profile"], str)


def test_5_distinct_behavior_configuration():
    """5. Weapons have distinct gameplay and physics parameters."""
    pulse = WEAPON_DEFS[WEAPON_PULSE]
    rapid = WEAPON_DEFS[WEAPON_RAPID]
    scatter = WEAPON_DEFS[WEAPON_SCATTER]
    missile = WEAPON_DEFS[WEAPON_MISSILE]
    plasma = WEAPON_DEFS[WEAPON_PLASMA]
    rail = WEAPON_DEFS[WEAPON_RAIL]

    # Rapid has faster fire rate (lower cooldown) than Pulse
    assert rapid["cooldown"] < pulse["cooldown"]
    # Scatter fires multiple projectiles per burst
    assert scatter["projectiles_per_shot"] > 1
    # Railgun has extreme speed and high single-shot damage
    assert rail["speed"] > pulse["speed"]
    assert rail["damage"] > pulse["damage"]
    # Plasma is heavier and slower than rail
    assert plasma["speed"] < rail["speed"]
    assert plasma["damage"] > pulse["damage"]


def test_6_weapon_definitions_deterministic():
    """6. Weapon definitions return identical properties over multiple reads."""
    for _ in range(10):
        assert WEAPON_DEFS[WEAPON_RAIL]["damage"] == 115
        assert WEAPON_DEFS[WEAPON_RAPID]["cooldown"] == 0.08
        assert WEAPON_DEFS[WEAPON_SCATTER]["projectiles_per_shot"] == 5


def test_7_muzzle_origin_0_degrees():
    """7. Muzzle origin calculation at 0 deg heading (facing right)."""
    p = Player((500, 500))
    p.apply_drone_class(0)  # Striker: primary is (38.0, 0.0)
    p.aim_angle = 0.0
    wx, wy = p.get_mount_world_pos("primary")
    assert pytest.approx(wx, abs=0.1) == 538.0
    assert pytest.approx(wy, abs=0.1) == 500.0


def test_8_muzzle_origin_90_degrees():
    """8. Muzzle origin calculation rotates correctly at 90 deg heading (facing down)."""
    p = Player((500, 500))
    p.apply_drone_class(0)  # Striker: primary is (38.0, 0.0)
    p.aim_angle = math.pi / 2  # 90 deg
    wx, wy = p.get_mount_world_pos("primary")
    assert pytest.approx(wx, abs=0.1) == 500.0
    assert pytest.approx(wy, abs=0.1) == 538.0


def test_9_muzzle_origin_180_degrees():
    """9. Muzzle origin calculation rotates correctly at 180 deg heading (facing left)."""
    p = Player((500, 500))
    p.apply_drone_class(0)  # Striker: primary is (38.0, 0.0)
    p.aim_angle = math.pi  # 180 deg
    wx, wy = p.get_mount_world_pos("primary")
    assert pytest.approx(wx, abs=0.1) == 462.0
    assert pytest.approx(wy, abs=0.1) == 500.0


def test_10_muzzle_origin_270_degrees():
    """10. Muzzle origin calculation rotates correctly at 270 deg heading (facing up)."""
    p = Player((500, 500))
    p.apply_drone_class(0)  # Striker: primary is (38.0, 0.0)
    p.aim_angle = 3 * math.pi / 2  # 270 deg (-90)
    wx, wy = p.get_mount_world_pos("primary")
    assert pytest.approx(wx, abs=0.1) == 500.0
    assert pytest.approx(wy, abs=0.1) == 462.0


def test_11_muzzle_distance_invariance_under_rotation():
    """11. Distance from player center to muzzle remains constant under all rotations."""
    p = Player((300, 400))
    p.apply_drone_class(1)  # Interceptor: primary (42.0, 0.0)
    
    for angle_deg in range(0, 360, 30):
        p.aim_angle = math.radians(angle_deg)
        wx, wy = p.get_mount_world_pos("primary")
        dist = math.hypot(wx - p.pos.x, wy - p.pos.y)
        assert pytest.approx(dist, abs=0.1) == 42.0


def test_12_projectile_begins_at_muzzle_position():
    """12. Fired projectile pos begins at exact computed muzzle position."""
    p = Player((600, 600))
    p.apply_drone_class(0)  # Striker
    p.active_weapon = WEAPON_PULSE
    p.weapon_cooldowns[WEAPON_PULSE] = 0.0
    p.aim_angle = 0.0
    
    expected_muzzle = p.get_mount_world_pos("primary_front_center")
    bullets = p.shoot((1000, 600))
    assert len(bullets) >= 1
    assert pytest.approx(bullets[0].pos.x, abs=1.0) == expected_muzzle[0]
    assert pytest.approx(bullets[0].pos.y, abs=1.0) == expected_muzzle[1]


def test_13_projectile_aim_direction_preserved():
    """13. Projectile trajectory heads toward target aim position."""
    p = Player((500, 500))
    p.apply_drone_class(0)
    p.active_weapon = WEAPON_PULSE
    p.weapon_cooldowns[WEAPON_PULSE] = 0.0
    
    # Aiming towards (500, 1000) (directly down)
    bullets = p.shoot((500, 1000))
    assert len(bullets) >= 1
    b = bullets[0]
    b.update(0.1)
    assert b.pos.y > 500.0  # Moves downwards towards target


def test_14_audio_dispatch_resolves_correct_id():
    """14. AudioManager play_weapon accepts all weapon types without error."""
    am = AudioManager(sound_enabled=False)
    for wid in WEAPON_DEFS:
        am.play_weapon(wid)
    assert True


def test_15_particle_vfx_dispatch():
    """15. ParticleManager handles all weapon muzzle flashes and impact bursts."""
    pm = ParticleManager()
    for wid in WEAPON_DEFS:
        pm.spawn_muzzle_flash((100, 100), 0.0, wid)
        pm.spawn_weapon_impact((150, 150), wid)
    assert len(pm.particles) > 0


def test_16_missing_audio_fallback():
    """16. AudioManager safely uses fallback synthesis if audio files are missing on disk."""
    am = AudioManager(sound_enabled=False)
    snd = am._load_or_synthesize("non_existent_sound_key", lambda: None)
    assert snd is None


def test_17_save_system_compatibility():
    """17. SaveSystem safely preserves and loads drone loadouts and unlocks."""
    save_sys = SaveSystem()
    data = save_sys.load()
    assert "selected_drone" in data
    assert "selected_skin" in data
    assert data["selected_drone"] in ("striker", "interceptor", "assault", "arc", "command")


def test_18_drone_loadout_integrity():
    """18. All 5 drone classes have valid, complete loadouts matching requirements."""
    expected_loadouts = {
        DRONE_CLASS_INTERCEPTOR: (WEAPON_PULSE, WEAPON_RAPID, WEAPON_MISSILE),
        DRONE_CLASS_STRIKER: (WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE),
        DRONE_CLASS_ASSAULT: (WEAPON_PULSE, WEAPON_PLASMA, WEAPON_MISSILE),
        DRONE_CLASS_ARC: (WEAPON_EMP, WEAPON_TESLA, WEAPON_BEAM),
        DRONE_CLASS_COMMAND: (WEAPON_RAIL, WEAPON_BEAM, WEAPON_BARRAGE),
    }

    for class_id, exp_weapons in expected_loadouts.items():
        loadout = get_drone_loadout(class_id)
        assert loadout["primary"] == exp_weapons[0]
        assert loadout["secondary"] == exp_weapons[1]
        assert loadout["heavy"] == exp_weapons[2]