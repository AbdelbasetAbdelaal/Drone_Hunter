"""
================================================================================
          PHASE 10.5 — FAST-PACED COMBAT & WEAPON MOUNT OVERHAUL TESTS
================================================================================
Comprehensive test suite validating:
- Five distinct Drone Combat Classes and role profiles
- Local-space weapon mount coordinates & rotation accuracy
- Projectile arsenal expansion (Rapid, Plasma, Rail, Barrage, etc.)
- Procedural multi-harmonic audio synthesis & sound manager triggers
- Kinematic flight agility, acceleration, and precision braking
================================================================================
"""

import math
import os
import pygame
import pytest

from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT, COLOR_CYAN, COLOR_GOLD
from src.data.game_data import (
    DRONE_CLASSES, DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR,
    DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND,
    WEAPON_DEFS, WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_RAPID, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE,
    WEAPON_BEAM, WEAPON_TESLA, WEAPON_CLUSTER
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


class TestPhase105CombatOverhaul:
    """Test suite covering Phase 10.5 combat speed, mounts, classes, and audio."""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        yield
        pygame.quit()

    def test_five_drone_classes_catalogue(self):
        """Verify all 5 drone classes exist with distinct attributes."""
        assert len(DRONE_CLASSES) == 5
        classes_by_id = {v["class_id"]: v for v in DRONE_CLASSES.values()}

        assert DRONE_CLASS_STRIKER in classes_by_id
        assert DRONE_CLASS_INTERCEPTOR in classes_by_id
        assert DRONE_CLASS_ASSAULT in classes_by_id
        assert DRONE_CLASS_ARC in classes_by_id
        assert DRONE_CLASS_COMMAND in classes_by_id

        # Interceptor has highest speed multiplier
        assert classes_by_id[DRONE_CLASS_INTERCEPTOR]["speed_mult"] > classes_by_id[DRONE_CLASS_STRIKER]["speed_mult"]
        # Assault has highest armor / durability
        assert classes_by_id[DRONE_CLASS_ASSAULT]["armor"] >= 4
        assert classes_by_id[DRONE_CLASS_ASSAULT]["max_health"] >= 135

    def test_player_drone_class_switching(self):
        """Verify player dynamically reconfigures stats and loadout when switching class."""
        player = Player((400, 300))

        # Striker (Default)
        player.apply_drone_class(0)
        assert player.drone_class == DRONE_CLASS_STRIKER
        assert WEAPON_PULSE in player.available_weapons

        # Interceptor (Class 1)
        player.apply_drone_class(1)
        assert player.drone_class == DRONE_CLASS_INTERCEPTOR
        assert player.max_speed > 450.0
        assert WEAPON_RAPID in player.available_weapons

        # Assault (Class 2)
        player.apply_drone_class(2)
        assert player.drone_class == DRONE_CLASS_ASSAULT
        assert player.armor >= 4
        assert WEAPON_PLASMA in player.available_weapons

        # Command Platform (Class 4)
        player.apply_drone_class(4)
        assert player.drone_class == DRONE_CLASS_COMMAND
        assert WEAPON_BARRAGE in player.available_weapons

    def test_weapon_mount_world_space_rotation(self):
        """Verify local hardpoints rotate dynamically with player aiming angle."""
        player = Player((500.0, 500.0))
        player.apply_drone_class(0)  # Striker: primary=(38.0, 0.0), left=(16.0, -28.0), right=(16.0, 28.0)

        # Aiming straight right (angle = 0 rad)
        player.aim_angle = 0.0
        nose_pos = player.get_mount_world_pos("primary")
        assert nose_pos[0] == pytest.approx(538.0, abs=0.1)
        assert nose_pos[1] == pytest.approx(500.0, abs=0.1)

        left_pos = player.get_mount_world_pos("left")
        assert left_pos[0] == pytest.approx(516.0, abs=0.1)
        assert left_pos[1] == pytest.approx(472.0, abs=0.1)

        # Aiming straight down (angle = pi/2 rad = 90 deg)
        player.aim_angle = math.pi / 2.0
        nose_pos_down = player.get_mount_world_pos("primary")
        assert nose_pos_down[0] == pytest.approx(500.0, abs=0.1)
        assert nose_pos_down[1] == pytest.approx(538.0, abs=0.1)

    def test_rapid_autocannon_firing(self):
        """Verify Rapid Autocannon fires high-speed kinetic rounds alternating left/right mounts."""
        player = Player((200, 200))
        player.apply_drone_class(1)  # Interceptor
        player.set_weapon(WEAPON_RAPID)

        bullets_1 = player.shoot((400, 200))
        assert len(bullets_1) == 1
        assert isinstance(bullets_1[0], Bullet)
        assert bullets_1[0].speed >= 900.0

        player.weapon_cooldowns[WEAPON_RAPID] = 0.0
        bullets_2 = player.shoot((400, 200))
        assert len(bullets_2) == 1
        # Fired from dual mounts on alternating sides
        assert bullets_1[0].pos.y != bullets_2[0].pos.y

    def test_heavy_plasma_cannon_firing(self):
        """Verify Heavy Plasma Cannon fires heavy concentrated plasma orb."""
        player = Player((200, 200))
        player.apply_drone_class(2)  # Assault
        player.set_weapon(WEAPON_PLASMA)

        bullets = player.shoot((400, 200))
        assert len(bullets) == 1
        assert isinstance(bullets[0], HeavyPlasmaOrb)
        assert bullets[0].damage >= 80

    def test_precision_railgun_firing(self):
        """Verify Precision Railgun fires supersonic piercing slug."""
        player = Player((200, 200))
        player.apply_drone_class(4)  # Command Platform
        player.set_weapon(WEAPON_RAIL)

        bullets = player.shoot((400, 200))
        assert len(bullets) == 1
        assert isinstance(bullets[0], RailgunSlug)
        assert bullets[0].speed >= 1500.0

    def test_missile_barrage_salvo(self):
        """Verify Missile Barrage launches a multi-missile guided salvo."""
        player = Player((200, 200))
        player.apply_drone_class(4)  # Command Platform
        player.set_weapon(WEAPON_BARRAGE)

        bullets = player.shoot((400, 200))
        assert len(bullets) == 4
        for b in bullets:
            assert isinstance(b, BarrageMissile)

    def test_procedural_sound_generation(self):
        """Verify all synthesized sound wave generators construct valid pygame Sounds."""
        laser_snd = generate_laser_sound()
        assert laser_snd is not None

        rapid_snd = generate_rapid_sound()
        assert rapid_snd is not None

        scatter_snd = generate_scatter_sound()
        assert scatter_snd is not None

        plasma_snd = generate_plasma_sound()
        assert plasma_snd is not None

        rail_snd = generate_rail_sound()
        assert rail_snd is not None

        barrage_snd = generate_barrage_sound()
        assert barrage_snd is not None

        win_snd = generate_mission_complete_sound()
        assert win_snd is not None

        fail_snd = generate_game_over_sound()
        assert fail_snd is not None

    def test_audio_manager_weapon_dispatch(self):
        """Verify AudioManager handles all weapon identifiers without error."""
        audio = AudioManager(sound_enabled=True)
        assert audio.mixer_initialized

        for w_id in [
            WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
            WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BARRAGE, WEAPON_BEAM,
            WEAPON_TESLA, WEAPON_CLUSTER
        ]:
            audio.play_weapon(w_id)

    def test_kinematic_flight_responsiveness(self):
        """Verify kinematic acceleration is responsive and drag prevents runaway drift."""
        player = Player((300, 300))
        assert player.acceleration >= 3000.0
        assert player.drag >= 8.0

        # Simulate 1 frame of accelerating right
        dt = 0.016
        keys = {pygame.K_d: True, pygame.K_RIGHT: True}
        player.handle_input(keys, dt, mouse_pos=(600, 300))
        assert player.velocity.x > 0.0

        # Simulate letting go of keys (braking deceleration)
        keys_idle = {}
        initial_vx = player.velocity.x
        player.handle_input(keys_idle, dt, mouse_pos=(600, 300))
        assert player.velocity.x < initial_vx  # Decelerates cleanly
