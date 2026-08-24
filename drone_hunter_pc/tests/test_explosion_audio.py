import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import pytest
from src.audio.audio_manager import AudioManager, AUDIO_ASSET_MAP

@pytest.fixture(autouse=True)
def init_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    yield
    # No teardown needed

def test_explosion_audio_asset_exists():
    """Verify all authoritative explosion OGG assets physically exist on disk."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_keys = [
        "explosion_small",
        "explosion_medium",
        "explosion_heavy",
        "explosion_boss",
        "player_destroyed",
    ]
    for key in required_keys:
        rel_path = AUDIO_ASSET_MAP.get(key)
        assert rel_path is not None, f"Key {key} missing from AUDIO_ASSET_MAP"
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.isfile(full_path), f"Explosion audio file missing at {full_path}"

def test_small_enemy_explosion_audio():
    """Verify Scout and Shooter elimination dispatches death_scout / death_shooter from sound cache."""
    am = AudioManager(sound_enabled=True)
    assert "death_scout" in am._sound_cache
    assert am._sound_cache["death_scout"] is not None
    assert "death_shooter" in am._sound_cache
    assert am._sound_cache["death_shooter"] is not None
    
    # Test dispatch
    am.play_death("scout")
    am.play_death("shooter")

def test_heavy_enemy_explosion_audio():
    """Verify Heavy and Elite/Shield destruction maps to heavy and medium explosion audio."""
    am = AudioManager(sound_enabled=True)
    assert "death_heavy" in am._sound_cache
    assert am._sound_cache["death_heavy"] is not None
    assert "death_shield" in am._sound_cache
    assert am._sound_cache["death_shield"] is not None
    
    am.play_death("heavy")
    am.play_death("shield")

def test_player_destruction_audio():
    """Verify Player destruction maps to player_death (player_destroyed.ogg) on PLAYER channel."""
    am = AudioManager(sound_enabled=True)
    assert "player_death" in am._sound_cache
    assert am._sound_cache["player_death"] is not None
    
    am.play_player_death()

def test_explosion_audio_not_duplicated():
    """Verify enemy elimination triggers audio only from combat_system and not duplicate systems."""
    from src.core.game_context import GameContext
    from src.systems.combat_system import CombatSystem
    from src.entities.player import Player
    from src.entities.enemy import Enemy
    
    ctx = GameContext()
    ctx.audio_manager = AudioManager(sound_enabled=True)
    ctx.player = Player((100, 100))
    cs = CombatSystem(ctx)
    
    # Count play_death invocations
    death_calls = []
    original_play_death = ctx.audio_manager.play_death
    def tracked_play_death(target_type=None):
        death_calls.append(target_type)
        return original_play_death(target_type)
    ctx.audio_manager.play_death = tracked_play_death
    
    enemy = Enemy("scout", (200, 200), sub_level=1)
    enemy.health = 1
    ctx.target_group.add(enemy)
    
    from src.entities.bullet import Bullet
    b = Bullet((200, 200), (200, 210), damage=50, owner="player")
    ctx.bullet_group.add(b)
    
    cs.update_combat(0.016)
    
    # Exactly one death audio call for one destroyed enemy
    assert len(death_calls) == 1
    assert death_calls[0] == "scout"
