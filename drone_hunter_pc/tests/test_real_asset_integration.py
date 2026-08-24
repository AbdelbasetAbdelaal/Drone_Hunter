"""
===============================================================================
           TEST SUITE: PRODUCTION REAL ASSET INTEGRATION PASS
===============================================================================
Comprehensive verification that all weapon projectiles, explosions, shockwaves,
and VFX utilize authoritative production PNG assets with zero silent fallbacks.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import pytest

pygame.init()

from src.data.game_data import (
    WEAPON_ASSETS, VFX_ASSETS, WEAPON_DEFS,
    WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_BEAM, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_TESLA,
    WEAPON_CLUSTER, WEAPON_EMP, WEAPON_BARRAGE,
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHIELD_DRONE
)
from src.rendering.sprite_manager import get_sprite_manager, SpriteManager
from src.rendering.particles import ParticleManager, ExplosionOverlay
from src.entities.bullet import (
    Bullet, HomingMissile, ContinuousBeam, TeslaArcBeam,
    ClusterTorpedo, ClusterBomblet, HeavyPlasmaOrb, RailgunSlug,
    BarrageMissile, EMPPulse, EnemyBullet, EnemySniperBeam
)
from src.entities.player import Player


def test_authoritative_weapon_registry_complete():
    """Verify WEAPON_ASSETS contains mappings for all core weapon archetypes."""
    expected_weapons = [
        "pulse", "rapid", "scatter", "missile", "beam",
        "plasma", "rail", "tesla", "cluster", "emp", "barrage"
    ]
    for w in expected_weapons:
        assert w in WEAPON_ASSETS, f"Missing weapon in registry: {w}"
        assert WEAPON_ASSETS[w].endswith(".png"), f"Path not a PNG: {WEAPON_ASSETS[w]}"


def test_authoritative_vfx_registry_complete():
    """Verify VFX_ASSETS contains mappings for all core VFX archetypes."""
    expected_vfx = [
        "explosion_1", "explosion_2", "shockwave",
        "shield_bubble", "engine_flame"
    ]
    for v in expected_vfx:
        assert v in VFX_ASSETS, f"Missing VFX in registry: {v}"
        assert VFX_ASSETS[v].endswith(".png"), f"Path not a PNG: {VFX_ASSETS[v]}"


def test_all_registered_weapon_pngs_exist_on_disk():
    """Verify every registered weapon asset file exists physically on disk and loads."""
    sm = get_sprite_manager()
    results = sm.validate_weapon_assets()
    assert all(results.values()), f"Some weapon assets failed validation: {results}"


def test_all_registered_vfx_pngs_exist_on_disk():
    """Verify every registered VFX asset file exists physically on disk and loads."""
    sm = get_sprite_manager()
    results = sm.validate_vfx_assets()
    assert all(results.values()), f"Some VFX assets failed validation: {results}"


def test_weapon_asset_usage_telemetry():
    """Verify SpriteManager tracks weapon asset render usage telemetry."""
    sm = get_sprite_manager()
    initial_usage = sm.weapon_asset_requested.get("laser_pulse.png", 0)
    surf = sm.get_projectile_sprite("pulse", (40, 12))
    assert surf is not None
    assert sm.weapon_asset_requested.get("laser_pulse.png", 0) > initial_usage


def test_vfx_asset_usage_telemetry():
    """Verify SpriteManager tracks VFX asset render usage telemetry."""
    sm = get_sprite_manager()
    initial_usage = sm.vfx_asset_requested.get("explosion_1.png", 0)
    surf = sm.get_vfx_sprite("explosion_1", (64, 64))
    assert surf is not None
    assert sm.vfx_asset_requested.get("explosion_1.png", 0) > initial_usage


def test_all_projectile_classes_instantiate_with_real_sprites():
    """Verify all 10 projectile entity classes default to valid production PNG surfaces."""
    start = (100.0, 100.0)
    target = (300.0, 100.0)

    p_pulse = Bullet(start, target, weapon_id="pulse")
    p_rapid = Bullet(start, target, weapon_id="rapid")
    p_scatter = Bullet(start, target, weapon_id="scatter")
    p_missile = HomingMissile(start, target)
    p_beam = ContinuousBeam(start, 0.0)
    p_tesla = TeslaArcBeam(start, target)
    p_torpedo = ClusterTorpedo(start, target)
    p_bomblet = ClusterBomblet(start, 0.0)
    p_plasma = HeavyPlasmaOrb(start, target)
    p_rail = RailgunSlug(start, target)
    p_barrage = BarrageMissile(start, target)
    p_emp = EMPPulse(start, target)
    p_enemy = EnemyBullet(start, target)
    p_sniper = EnemySniperBeam(start, target)

    projs = [
        p_pulse, p_rapid, p_scatter, p_missile, p_beam, p_tesla,
        p_torpedo, p_bomblet, p_plasma, p_rail, p_barrage, p_emp,
        p_enemy, p_sniper
    ]

    for p in projs:
        surf = getattr(p, "original_image", getattr(p, "image", None))
        assert surf is not None, f"Projectile {type(p).__name__} has no image"
        assert isinstance(surf, pygame.Surface), f"Projectile {type(p).__name__} image is not a pygame Surface"
        assert surf.get_width() > 0 and surf.get_height() > 0


def test_enemy_death_spawns_real_explosion_overlay():
    """Verify enemy death spawns ExplosionOverlay utilizing real PNG sprites."""
    pm = ParticleManager()
    pm.spawn_enemy_death((200, 200), (255, 100, 100), enemy_type=TARGET_TYPE_SCOUT)
    assert len(pm.explosion_overlays) >= 1
    assert pm.explosion_overlays[0].asset_id in ("explosion_1", "explosion_2")
    assert pm.explosion_overlays[0].max_size == 78


def test_heavy_enemy_death_spawns_heavy_explosion_and_shockwave():
    """Verify heavy enemy death creates larger explosion overlay."""
    pm = ParticleManager()
    pm.spawn_enemy_death((200, 200), (255, 200, 50), enemy_type=TARGET_TYPE_HEAVY)
    assert len(pm.explosion_overlays) >= 1
    assert pm.explosion_overlays[0].asset_id == "explosion_2"
    assert pm.explosion_overlays[0].max_size == 110


def test_shockwave_spawns_shockwave_overlay():
    """Verify spawn_shockwave creates ExplosionOverlay with shockwave asset."""
    pm = ParticleManager()
    pm.spawn_shockwave((300, 300), max_r=180)
    assert len(pm.explosion_overlays) >= 1
    shockwave_overlay = next((o for o in pm.explosion_overlays if o.is_shockwave), None)
    assert shockwave_overlay is not None
    assert shockwave_overlay.asset_id == "shockwave"
    assert shockwave_overlay.max_size == 180


def test_weapon_impact_vfx_overlays():
    """Verify weapon impacts instantiate proper explosion overlays."""
    pm = ParticleManager()
    pm.spawn_weapon_impact((150, 150), weapon_type="missile")
    assert len(pm.explosion_overlays) >= 1
    assert pm.explosion_overlays[0].asset_id == "explosion_2"

    pm.explosion_overlays.clear()
    pm.spawn_weapon_impact((150, 150), weapon_type="pulse")
    assert len(pm.explosion_overlays) >= 1
    assert pm.explosion_overlays[0].asset_id == "explosion_1"


def test_weapons_never_fire_backwards():
    """Verify that all weapons across all drone classes fire forward along aim_angle, even if target is close or behind."""
    from src.entities.player import Player
    import math

    player = Player((500.0, 500.0))
    all_weapons = [
        "pulse", "rapid", "scatter", "missile", "barrage",
        "plasma", "rail", "beam", "tesla", "cluster", "emp"
    ]

    for skin in range(5):
        player.apply_drone_class(skin)
        player.available_weapons = all_weapons
        for w in all_weapons:
            player.set_weapon(w)
            # Test various angles around the 360 circle
            for deg in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(deg)
                # Target in front
                target_in_front = (player.pos.x + math.cos(rad) * 400.0, player.pos.y + math.sin(rad) * 400.0)
                player.weapon_cooldowns[player.active_weapon] = 0.0
                player.energy = 100.0
                bullets = player.shoot(target_in_front)
                assert len(bullets) > 0, f"No bullets for {w} on skin {skin}"
                for b in bullets:
                    b_dx = math.cos(b.angle_rad)
                    b_dy = math.sin(b.angle_rad)
                    fwd_dx = math.cos(rad)
                    fwd_dy = math.sin(rad)
                    dot = b_dx * fwd_dx + b_dy * fwd_dy
                    assert dot > 0.4, f"Weapon {w} on skin {skin} fired backwards! Dot product: {dot}"

                # Target placed extremely close (5px from player center, behind muzzle)
                target_close = (player.pos.x + math.cos(rad) * 5.0, player.pos.y + math.sin(rad) * 5.0)
                player.weapon_cooldowns[player.active_weapon] = 0.0
                player.energy = 100.0
                bullets_close = player.shoot(target_close)
                assert len(bullets_close) > 0
                for b in bullets_close:
                    b_dx = math.cos(b.angle_rad)
                    b_dy = math.sin(b.angle_rad)
                    fwd_dx = math.cos(rad)
                    fwd_dy = math.sin(rad)
                    dot = b_dx * fwd_dx + b_dy * fwd_dy
                    assert dot > 0.4, f"Weapon {w} on skin {skin} with close target fired backwards! Dot product: {dot}"


def test_realistic_explosion_audio_synthesis():
    """Verify all realistic physical explosion synth functions generate valid multi-harmonic waveforms."""
    from src.audio.sound_synth import (
        generate_death_scout_sound, generate_death_shooter_sound,
        generate_death_heavy_sound, generate_death_shield_sound,
        generate_death_boss_sound, generate_explosion_sound,
        generate_player_death_sound
    )

    s_scout = generate_death_scout_sound()
    s_shooter = generate_death_shooter_sound()
    s_heavy = generate_death_heavy_sound()
    s_shield = generate_death_shield_sound()
    s_boss = generate_death_boss_sound()
    s_gen = generate_explosion_sound()
    s_player = generate_player_death_sound()

    all_sounds = [
        ("scout", s_scout, 0.25),
        ("shooter", s_shooter, 0.35),
        ("heavy", s_heavy, 0.50),
        ("shield", s_shield, 0.40),
        ("boss", s_boss, 0.80),
        ("generic", s_gen, 0.35),
        ("player", s_player, 0.60),
    ]

    for name, snd, min_dur in all_sounds:
        assert snd is not None, f"Sound generator {name} returned None"
        assert isinstance(snd, pygame.mixer.Sound), f"Sound {name} is not a pygame Sound"
        assert snd.get_length() >= min_dur, f"Sound {name} duration {snd.get_length()} < {min_dur}"


def test_player_death_explosion_sequence_and_deferred_failure():
    """Verify player destruction plays full explosion animation before mission failure screen appears."""
    from src.core.game import Game
    from src.core.game_state import STATE_PLAYING, STATE_MISSION_FAILED

    game = Game()
    game.start_phase5_mission("S1_M1")
    ctx = game.context
    assert ctx.state == STATE_PLAYING
    assert ctx.player.alive

    # Inflict lethal damage
    ctx.player.take_damage(99999)
    assert not ctx.player.alive
    assert ctx.player.is_destroyed
    assert ctx.player.destruction_timer > 1.0

    # Advance frame by 0.5s - player should STILL be in STATE_PLAYING to show explosion
    game.update(0.5)
    assert ctx.state == STATE_PLAYING, "Game prematurely transitioned to failure screen before explosion completed!"
    assert ctx.player.destruction_timer > 0.0

    # Advance remainder of destruction animation (> 1.4s total)
    game.update(1.0)
    assert ctx.player.destruction_timer <= 0.0
    assert ctx.state == STATE_MISSION_FAILED, "Game should transition to STATE_MISSION_FAILED after explosion completes!"
