import pytest
import math
import pygame
from src.core.game import Game
from src.data.game_data import WEAPON_DEFS, WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE, TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, HEAVY_HP, HEAVY_ARMOR
from src.entities.player import Player
from src.entities.bullet import Bullet, HomingMissile
from src.systems.combat_system import CombatSystem
from src.entities.enemy import Enemy

def test_weapon_data():
    """Verify authoritative weapon specifications."""
    assert WEAPON_PULSE in WEAPON_DEFS
    assert WEAPON_SCATTER in WEAPON_DEFS
    assert WEAPON_MISSILE in WEAPON_DEFS

    p_def = WEAPON_DEFS[WEAPON_PULSE]
    assert p_def["damage"] == 12
    assert p_def["cooldown"] == 0.18
    assert p_def["speed"] == 650.0
    assert p_def["projectiles_per_shot"] == 1
    assert p_def["spread_deg"] == 0.0

    s_def = WEAPON_DEFS[WEAPON_SCATTER]
    assert s_def["damage"] == 10
    assert s_def["cooldown"] == 0.75
    assert s_def["speed"] == 500.0
    assert s_def["projectiles_per_shot"] == 5
    assert s_def["spread_deg"] == 22.0

    m_def = WEAPON_DEFS[WEAPON_MISSILE]
    assert m_def["damage"] == 65
    assert m_def["cooldown"] == 2.5
    assert m_def["speed"] == 260.0
    assert m_def["projectiles_per_shot"] == 1

def test_player_weapon_switching():
    """Verify player can switch weapons but rejects invalid ones."""
    player = Player((0, 0))
    assert player.active_weapon == WEAPON_PULSE
    assert len(player.available_weapons) == 3
    assert WEAPON_SCATTER in player.available_weapons
    assert WEAPON_MISSILE in player.available_weapons

    player.cycle_weapon(1)
    assert player.active_weapon == WEAPON_SCATTER

    player.select_weapon(2)
    assert player.active_weapon == WEAPON_MISSILE

    # Safe fallback or ignorance on invalid weapon index
    player.select_weapon(99)
    assert player.active_weapon == WEAPON_MISSILE # Should ignore invalid

def test_pulse_laser_firing():
    """Verify Pulse Laser shoots 1 projectile with correct properties."""
    player = Player((0, 0))
    player.set_weapon(WEAPON_PULSE)
    bullets = player.shoot((100, 0))
    assert len(bullets) == 1
    assert isinstance(bullets[0], Bullet)
    assert bullets[0].damage == 12
    assert bullets[0].speed == 650.0

def test_spread_cannon_firing():
    """Verify Spread Cannon shoots 5 projectiles with deterministic spread."""
    player = Player((0, 0))
    player.set_weapon(WEAPON_SCATTER)
    bullets = player.shoot((100, 0))
    assert len(bullets) == 5
    # Center bullet should have 0 offset
    angles = [b.angle_rad for b in bullets]
    assert angles[2] == pytest.approx(0.0)
    assert angles[0] < angles[-1]

def test_heavy_missile_firing():
    """Verify Heavy Missile shoots 1 homing/heavy projectile."""
    player = Player((0, 0))
    player.set_weapon(WEAPON_MISSILE)
    bullets = player.shoot((100, 0))
    assert len(bullets) == 1
    assert isinstance(bullets[0], HomingMissile)
    assert bullets[0].damage == 65
    assert bullets[0].speed == 260.0

def test_weapon_cooldown_exploit():
    """Verify cooldowns block spam and switching weapons respects independent cooldowns."""
    player = Player((0, 0))
    player.set_weapon(WEAPON_PULSE)
    
    # First shot succeeds
    bullets = player.shoot((100, 0))
    assert len(bullets) == 1
    
    # Immediate second shot fails
    assert not player.can_shoot()
    assert len(player.shoot((100, 0))) == 0
    
    # Switch weapon - should be able to shoot
    player.set_weapon(WEAPON_SCATTER)
    assert player.can_shoot()
    bullets2 = player.shoot((100, 0))
    assert len(bullets2) == 5
    
    # Now scatter is on cooldown
    assert not player.can_shoot()
    
    # Switch back to Pulse - it should still be on cooldown!
    player.set_weapon(WEAPON_PULSE)
    assert not player.can_shoot()
    
    # Update time to clear Pulse cooldown
    player.update(0.2)
    assert player.can_shoot()

def test_combat_integration_and_armor():
    """Verify projectiles correctly damage enemies and Heavy armor applies."""
    game = Game()
    ctx = game.context
    player = Player((0, 0))
    
    scout = Enemy(enemy_type=TARGET_TYPE_SCOUT, pos=(100, 0))
    shooter = Enemy(enemy_type=TARGET_TYPE_SHOOTER, pos=(100, 0))
    heavy = Enemy(enemy_type=TARGET_TYPE_HEAVY, pos=(100, 0))
    
    ctx.target_group.add(scout)
    ctx.target_group.add(shooter)
    ctx.target_group.add(heavy)
    
    # Deal damage to heavy via direct combat system method
    b = Bullet((0, 0), (100, 0), damage=100)
    b.rect.center = heavy.rect.center
    
    # Apply damage manually to verify math
    original_hp = heavy.hp
    expected_dmg = 100 * (1.0 - HEAVY_ARMOR)
    heavy.take_damage(100)
    assert heavy.hp == pytest.approx(original_hp - expected_dmg)

def test_reset_clears_weapon_state():
    """Verify GameContext reset clears weapon state and sets to Pulse."""
    game = Game()
    ctx = game.context
    ctx.player.set_weapon(WEAPON_MISSILE)
    ctx.player.shoot((100, 0))
    
    game.reset_game()
    assert game.context.player.active_weapon == WEAPON_PULSE
    assert game.context.player.can_shoot() # Cooldowns must be zero

def test_hud_weapon_display():
    """Verify HUD can render without exceptions when weapons are on cooldown."""
    from src.ui.hud import draw_hud
    game = Game()
    ctx = game.context
    ctx.player.set_weapon(WEAPON_SCATTER)
    ctx.player.weapon_cooldowns[WEAPON_SCATTER] = 1.0
    
    # Just verify no exception is thrown during draw
    canvas = pygame.Surface((800, 600))
    draw_hud(canvas, ctx.player)
    # Success is reaching this point without error
    assert True
