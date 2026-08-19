"""
================================================================================
                    DRONE HUNTER 2D - AUDIO MANAGER & SOUND CACHE
================================================================================
Centralized audio controller with pre-cached procedural synth sounds, voice
throttling to prevent mixer distortion, and global volume controls.
"""

import pygame
from src.audio.sound_synth import (
    generate_laser_sound, generate_missile_sound, generate_beam_sound,
    generate_tesla_sound, generate_cluster_sound, generate_sniper_sound,
    generate_overdrive_sound, generate_explosion_sound, generate_hit_sound,
    generate_emp_sound, generate_powerup_sound, generate_roll_sound,
    generate_cloak_sound, generate_buy_sound
)

class AudioManager:
    def __init__(self, sound_enabled: bool = True):
        self.sound_enabled = sound_enabled
        self.mixer_initialized = False
        self._sound_cache = {}
        self._last_played_times = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            self.mixer_initialized = True
            self._preload_sounds()
        except Exception:
            self.mixer_initialized = False

    def _preload_sounds(self):
        if not self.mixer_initialized:
            return
        self._sound_cache["laser"] = generate_laser_sound()
        self._sound_cache["missile"] = generate_missile_sound()
        self._sound_cache["beam"] = generate_beam_sound()
        self._sound_cache["tesla"] = generate_tesla_sound()
        self._sound_cache["cluster"] = generate_cluster_sound()
        self._sound_cache["sniper"] = generate_sniper_sound()
        self._sound_cache["overdrive"] = generate_overdrive_sound()
        self._sound_cache["explosion"] = generate_explosion_sound()
        self._sound_cache["hit"] = generate_hit_sound()
        self._sound_cache["emp"] = generate_emp_sound()
        self._sound_cache["powerup"] = generate_powerup_sound()
        self._sound_cache["roll"] = generate_roll_sound()
        self._sound_cache["cloak"] = generate_cloak_sound()
        self._sound_cache["buy"] = generate_buy_sound()

    def _play_cached(self, sound_key: str, min_interval_ms: int = 40):
        if not self.sound_enabled or not self.mixer_initialized:
            return

        now = pygame.time.get_ticks()
        last_t = self._last_played_times.get(sound_key, 0)
        if now - last_t < min_interval_ms:
            return

        snd = self._sound_cache.get(sound_key)
        if snd is None:
            # Fallback lazy load
            self._preload_sounds()
            snd = self._sound_cache.get(sound_key)

        if snd:
            try:
                snd.play()
                self._last_played_times[sound_key] = now
            except Exception:
                pass

    def play_laser(self): self._play_cached("laser", 40)
    def play_missile(self): self._play_cached("missile", 80)
    def play_beam(self): self._play_cached("beam", 60)
    def play_tesla(self): self._play_cached("tesla", 60)
    def play_cluster(self): self._play_cached("cluster", 80)
    def play_sniper(self): self._play_cached("sniper", 80)
    def play_overdrive(self): self._play_cached("overdrive", 150)
    def play_explosion(self): self._play_cached("explosion", 50)
    def play_mine_explosion(self): self._play_cached("explosion", 50)
    def play_hit(self): self._play_cached("hit", 30)
    def play_player_hit(self): self._play_cached("hit", 30)
    def play_emp(self): self._play_cached("emp", 100)
    def play_powerup(self): self._play_cached("powerup", 60)
    def play_roll(self): self._play_cached("roll", 80)
    def play_whoosh(self): self._play_cached("roll", 80)
    def play_cloak(self): self._play_cached("cloak", 80)
    def play_buy(self): self._play_cached("buy", 60)
    def play_sector_ambient(self, sector_idx: int): pass
