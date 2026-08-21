"""
================================================================================
                    DRONE HUNTER 2D - PHASE 10 AUDIO TEST SUITE
================================================================================
Unit test suite verifying Phase 10 Audio Architecture & Sound Design:
- AudioManager safe initialization in headless / dummy environments
- Complete procedural sound waveform generation and caching
- Channel boundedness and priority hierarchy
- Anti-spam throttling & rate limiting
- Weapon fire sound mapping (Pulse, Scatter, Missile, Beam, Tesla, Cluster, EMP)
- Target-specific impact sound dispatching (Scout, Shooter, Heavy, Shield, Boss)
- Target-specific destruction sound dispatching (Scout, Shooter, Heavy, Shield, Boss)
- Player damage & destruction audio sequences
- Boss warning alert, attack, and single-trigger phase transition audio
- UI sound triggers (Click, Hover, Mission Start, Complete, Game Over, Victory)
- Strict gameplay invariance (Zero balance, health, or combat mechanics altered)
"""

import os
import unittest
import pygame

# Initialize headless dummy audio for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.audio.audio_manager import (
    AudioManager, CHANNEL_BOSS, CHANNEL_PLAYER, CHANNEL_ENGINE, CHANNEL_UI,
    CHANNELS_WEAPONS, CHANNELS_SFX
)
from src.core.game_context import GameContext
from src.entities.player import Player
from src.entities.boss import SectorBoss
from src.data.boss_data import ASSEMBLY_WARDEN_CONFIG
from src.data.game_data import PLAYER_MAX_HEALTH, HORIZONTAL_SPEED
from src.systems.boss_system import BossSystem, STATE_ACTIVE


class TestPhase10Audio(unittest.TestCase):

    def setUp(self):
        self.audio = AudioManager(sound_enabled=True)
        self.ctx = GameContext()
        self.ctx.audio_manager = self.audio
        self.player = Player((500, 360))
        self.ctx.player = self.player

    def test_audio_manager_initializes_safely(self):
        """Verify AudioManager initializes without crashing even in dummy driver environments."""
        am = AudioManager(sound_enabled=True)
        self.assertTrue(hasattr(am, "sound_enabled"))
        self.assertTrue(hasattr(am, "master_volume"))
        self.assertTrue(hasattr(am, "sfx_volume"))
        self.assertTrue(hasattr(am, "music_volume"))
        self.assertTrue(hasattr(am, "engine_volume"))

    def test_all_sounds_preloaded_and_cached(self):
        """Verify all essential sound waveforms are cached at startup."""
        expected_keys = [
            "laser", "scatter", "missile", "beam", "tesla", "cluster", "sniper", "emp",
            "hit_scout", "hit_shooter", "hit_heavy", "hit_shield", "hit_boss", "hit",
            "death_scout", "death_shooter", "death_heavy", "death_shield", "death_boss", "explosion",
            "player_hit", "player_death", "roll", "engine_hum", "overdrive", "cloak", "powerup",
            "boss_alert", "boss_attack", "boss_phase_2", "boss_phase_3", "boss_phase_4",
            "ui_click", "ui_hover", "mission_start", "mission_complete", "game_over", "victory", "buy"
        ]
        for key in expected_keys:
            self.assertIn(key, self.audio._sound_cache, f"Sound key '{key}' must be pre-cached")

    def test_audio_channels_bounded(self):
        """Verify mixer channels are strictly bounded to 24 priority channels."""
        self.assertEqual(CHANNEL_BOSS, 0)
        self.assertEqual(CHANNEL_PLAYER, 1)
        self.assertEqual(CHANNEL_ENGINE, 2)
        self.assertEqual(CHANNEL_UI, 3)
        self.assertEqual(len(CHANNELS_WEAPONS), 4)
        self.assertEqual(len(CHANNELS_SFX), 16)
        total_channels = 1 + 1 + 1 + 1 + len(CHANNELS_WEAPONS) + len(CHANNELS_SFX)
        self.assertEqual(total_channels, 24)

    def test_weapon_sound_dispatch(self):
        """Verify all weapon types have working dedicated play methods."""
        weapons = [
            self.audio.play_laser, self.audio.play_scatter, self.audio.play_missile,
            self.audio.play_beam, self.audio.play_tesla, self.audio.play_cluster,
            self.audio.play_sniper, self.audio.play_emp
        ]
        for w_func in weapons:
            try:
                w_func()
            except Exception as e:
                self.fail(f"Weapon audio method {w_func.__name__} raised exception: {e}")

    def test_target_specific_impact_dispatch(self):
        """Verify impact audio functions correctly for all enemy categories."""
        impact_methods = [
            self.audio.play_hit_scout, self.audio.play_hit_shooter,
            self.audio.play_hit_heavy, self.audio.play_hit_shield,
            self.audio.play_hit_boss, self.audio.play_hit
        ]
        for hit_func in impact_methods:
            try:
                hit_func()
            except Exception as e:
                self.fail(f"Impact audio method {hit_func.__name__} raised exception: {e}")

    def test_target_specific_destruction_dispatch(self):
        """Verify destruction audio functions correctly for all enemy categories."""
        death_methods = [
            self.audio.play_death_scout, self.audio.play_death_shooter,
            self.audio.play_death_heavy, self.audio.play_death_shield,
            self.audio.play_boss_death, self.audio.play_death
        ]
        for death_func in death_methods:
            try:
                death_func()
            except Exception as e:
                self.fail(f"Destruction audio method {death_func.__name__} raised exception: {e}")

    def test_player_events_audio(self):
        """Verify player hit, death, roll, overdrive, cloak, and powerup audio methods work safely."""
        player_methods = [
            self.audio.play_player_hit, self.audio.play_player_death,
            self.audio.play_roll, self.audio.play_overdrive,
            self.audio.play_cloak, self.audio.play_powerup
        ]
        for p_func in player_methods:
            try:
                p_func()
            except Exception as e:
                self.fail(f"Player audio method {p_func.__name__} raised exception: {e}")

    def test_engine_sound_modulation(self):
        """Verify engine sound loop modulates volume cleanly and stops without error."""
        try:
            self.audio.update_engine_sound(0.0, False)
            self.audio.update_engine_sound(0.5, True)
            self.audio.update_engine_sound(1.0, True)
            self.audio.stop_engine_sound()
        except Exception as e:
            self.fail(f"Engine audio modulation raised exception: {e}")

    def test_boss_phase_transition_fires_once(self):
        """Verify Boss Phase Transition audio triggers exactly once per phase transition."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG, pos=(500, 400))
        self.ctx.target_group.add(boss)
        
        boss_sys = BossSystem()
        boss_sys.active_boss = boss
        boss_sys.active_boss_def = ASSEMBLY_WARDEN_CONFIG
        boss_sys.state = STATE_ACTIVE

        # Initially Phase 1 -> phase_audio_pending is 0
        self.assertEqual(getattr(boss, "phase_audio_pending", 0), 0)

        # Transition to Phase 2
        boss._apply_phase(1)
        self.assertEqual(boss.phase_audio_pending, 2)

        # BossSystem update consumes the pending audio
        boss_sys.update(0.016, self.ctx)
        self.assertEqual(boss.phase_audio_pending, 0)

        # Subsequent frames do NOT re-trigger audio
        boss_sys.update(0.016, self.ctx)
        self.assertEqual(boss.phase_audio_pending, 0)

    def test_ui_audio_methods(self):
        """Verify all UI audio methods function without error."""
        ui_methods = [
            self.audio.play_ui_click, self.audio.play_ui_hover,
            self.audio.play_mission_start, self.audio.play_mission_complete,
            self.audio.play_game_over, self.audio.play_victory,
            self.audio.play_buy, self.audio.play_upgrade, self.audio.play_warning
        ]
        for ui_func in ui_methods:
            try:
                ui_func()
            except Exception as e:
                self.fail(f"UI audio method {ui_func.__name__} raised exception: {e}")

    def test_sound_spam_protection_throttles(self):
        """Verify rapid repeated calls are throttled by min_interval_ms."""
        # Record time
        self.audio._last_played_times["laser"] = pygame.time.get_ticks()
        # Immediate subsequent call should be ignored by rate limiter
        last_t = self.audio._last_played_times["laser"]
        self.audio._play_cached("laser", min_interval_ms=1000)
        # Timestamp must not have updated
        self.assertEqual(self.audio._last_played_times["laser"], last_t)

    def test_gameplay_mechanics_locked(self):
        """Verify player stats, speeds, and max health remain strictly unaltered."""
        p = Player((500, 360))
        self.assertEqual(p.max_health, PLAYER_MAX_HEALTH)
        self.assertEqual(p.max_speed, HORIZONTAL_SPEED)


if __name__ == "__main__":
    unittest.main()

