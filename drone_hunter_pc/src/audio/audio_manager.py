"""
================================================================================
                    DRONE HUNTER 2D - AUDIO MANAGER & SOUND CACHE
================================================================================
Centralized audio controller with pre-cached procedural synth sounds, dedicated
priority channels (Boss, Player, Engine, UI, Weapons, SFX Pool), voice
throttling to prevent mixer distortion, dynamic engine modulation, and global
volume hierarchy.
"""

import math
import pygame
from src.audio.sound_synth import (
    generate_laser_sound, generate_rapid_sound, generate_scatter_sound, generate_missile_sound,
    generate_barrage_sound, generate_plasma_sound, generate_rail_sound,
    generate_beam_sound, generate_tesla_sound, generate_cluster_sound,
    generate_sniper_sound, generate_emp_sound,
    generate_hit_scout_sound, generate_hit_shooter_sound, generate_hit_heavy_sound,
    generate_hit_shield_sound, generate_hit_boss_sound, generate_hit_sound,
    generate_death_scout_sound, generate_death_shooter_sound, generate_death_heavy_sound,
    generate_death_shield_sound, generate_death_boss_sound, generate_explosion_sound,
    generate_player_hit_sound, generate_player_death_sound, generate_roll_sound,
    generate_engine_hum_sound, generate_overdrive_sound, generate_cloak_sound,
    generate_boss_alert_sound, generate_boss_attack_sound, generate_boss_phase_transition_sound,
    generate_ui_click_sound, generate_ui_hover_sound, generate_mission_start_sound,
    generate_mission_complete_sound, generate_game_over_sound, generate_victory_sound,
    generate_powerup_sound, generate_buy_sound
)

# Dedicated channel indices for strict priority management
CHANNEL_BOSS = 0
CHANNEL_PLAYER = 1
CHANNEL_ENGINE = 2
CHANNEL_UI = 3
CHANNELS_WEAPONS = [4, 5, 6, 7]
CHANNELS_SFX = list(range(8, 24))


class AudioManager:
    """
    Centralized event-driven audio system managing pre-cached sound synthesis,
    prioritized channels, engine audio modulation, and anti-spam throttling.
    """
    def __init__(self, sound_enabled: bool = True):
        self.sound_enabled = sound_enabled
        self.mixer_initialized = False
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}
        self._last_played_times: dict[str, int] = {}
        self._engine_channel: pygame.mixer.Channel | None = None
        self._weapon_channel_idx = 0
        self._sfx_channel_idx = 0
        
        # Volume hierarchy (0.0 to 1.0)
        self.master_volume = 1.0
        self.sfx_volume = 0.85
        self.music_volume = 0.60
        self.engine_volume = 0.35

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            self.mixer_initialized = True
            self._preload_sounds()
        except Exception:
            self.mixer_initialized = False

    def _preload_sounds(self):
        """Pre-caches all procedural waveforms at initialization for zero runtime disk I/O / synthesis."""
        if not self.mixer_initialized:
            return

        # Weapons
        self._sound_cache["laser"] = generate_laser_sound()
        self._sound_cache["rapid"] = generate_rapid_sound()
        self._sound_cache["scatter"] = generate_scatter_sound()
        self._sound_cache["missile"] = generate_missile_sound()
        self._sound_cache["barrage"] = generate_barrage_sound()
        self._sound_cache["plasma"] = generate_plasma_sound()
        self._sound_cache["rail"] = generate_rail_sound()
        self._sound_cache["beam"] = generate_beam_sound()
        self._sound_cache["tesla"] = generate_tesla_sound()
        self._sound_cache["cluster"] = generate_cluster_sound()
        self._sound_cache["sniper"] = generate_sniper_sound()
        self._sound_cache["emp"] = generate_emp_sound()

        # Impacts
        self._sound_cache["hit_scout"] = generate_hit_scout_sound()
        self._sound_cache["hit_shooter"] = generate_hit_shooter_sound()
        self._sound_cache["hit_heavy"] = generate_hit_heavy_sound()
        self._sound_cache["hit_shield"] = generate_hit_shield_sound()
        self._sound_cache["hit_boss"] = generate_hit_boss_sound()
        self._sound_cache["hit"] = generate_hit_sound()

        # Destructions
        self._sound_cache["death_scout"] = generate_death_scout_sound()
        self._sound_cache["death_shooter"] = generate_death_shooter_sound()
        self._sound_cache["death_heavy"] = generate_death_heavy_sound()
        self._sound_cache["death_shield"] = generate_death_shield_sound()
        self._sound_cache["death_boss"] = generate_death_boss_sound()
        self._sound_cache["explosion"] = generate_explosion_sound()

        # Player
        self._sound_cache["player_hit"] = generate_player_hit_sound()
        self._sound_cache["player_death"] = generate_player_death_sound()
        self._sound_cache["roll"] = generate_roll_sound()
        self._sound_cache["engine_hum"] = generate_engine_hum_sound()
        self._sound_cache["overdrive"] = generate_overdrive_sound()
        self._sound_cache["cloak"] = generate_cloak_sound()
        self._sound_cache["powerup"] = generate_powerup_sound()

        # Boss
        self._sound_cache["boss_alert"] = generate_boss_alert_sound()
        self._sound_cache["boss_attack"] = generate_boss_attack_sound()
        self._sound_cache["boss_phase_2"] = generate_boss_phase_transition_sound(2)
        self._sound_cache["boss_phase_3"] = generate_boss_phase_transition_sound(3)
        self._sound_cache["boss_phase_4"] = generate_boss_phase_transition_sound(4)

        # UI
        self._sound_cache["ui_click"] = generate_ui_click_sound()
        self._sound_cache["ui_hover"] = generate_ui_hover_sound()
        self._sound_cache["mission_start"] = generate_mission_start_sound()
        self._sound_cache["mission_complete"] = generate_mission_complete_sound()
        self._sound_cache["game_over"] = generate_game_over_sound()
        self._sound_cache["victory"] = generate_victory_sound()
        self._sound_cache["buy"] = generate_buy_sound()

    def _play_cached(self, sound_key: str, min_interval_ms: int = 40, channel_id: int | None = None, volume_scale: float = 1.0):
        """Plays a pre-cached sound with anti-spam rate limiting and channel assignment."""
        if not self.sound_enabled or not self.mixer_initialized:
            return

        now = pygame.time.get_ticks()
        last_t = self._last_played_times.get(sound_key, 0)
        if now - last_t < min_interval_ms:
            return

        snd = self._sound_cache.get(sound_key)
        if snd is None:
            return

        try:
            effective_vol = max(0.0, min(1.0, self.master_volume * self.sfx_volume * volume_scale))
            snd.set_volume(effective_vol)

            if channel_id is not None:
                ch = pygame.mixer.Channel(channel_id)
                ch.play(snd)
            else:
                # Use rotating SFX pool
                ch_idx = CHANNELS_SFX[self._sfx_channel_idx]
                self._sfx_channel_idx = (self._sfx_channel_idx + 1) % len(CHANNELS_SFX)
                ch = pygame.mixer.Channel(ch_idx)
                ch.play(snd)

            self._last_played_times[sound_key] = now
        except Exception:
            pass

    # =========================================================================
    # WEAPON AUDIO METHODS
    # =========================================================================
    def play_weapon(self, weapon_type: str):
        """Dispatches audio for any given weapon identifier."""
        if weapon_type in ("pulse", "laser"):
            self.play_laser()
        elif weapon_type == "rapid":
            self.play_rapid()
        elif weapon_type == "scatter":
            self.play_scatter()
        elif weapon_type == "missile":
            self.play_missile()
        elif weapon_type == "barrage":
            self.play_barrage()
        elif weapon_type == "plasma":
            self.play_plasma()
        elif weapon_type in ("rail", "sniper"):
            self.play_rail()
        elif weapon_type == "beam":
            self.play_beam()
        elif weapon_type == "tesla":
            self.play_tesla()
        elif weapon_type == "cluster":
            self.play_cluster()
        elif weapon_type == "emp":
            self.play_emp()
        else:
            self.play_laser()

    def play_laser(self):
        """Pulse Laser fire sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("laser", min_interval_ms=45, channel_id=ch_idx, volume_scale=0.85)

    def play_rapid(self):
        """Rapid Autocannon fire sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("rapid", min_interval_ms=30, channel_id=ch_idx, volume_scale=0.80)

    def play_scatter(self):
        """Spread Cannon fire sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("scatter", min_interval_ms=50, channel_id=ch_idx, volume_scale=0.90)

    def play_missile(self):
        """Heavy Missile launch sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("missile", min_interval_ms=75, channel_id=ch_idx, volume_scale=0.95)

    def play_barrage(self):
        """Missile Barrage salvo sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("barrage", min_interval_ms=80, channel_id=ch_idx, volume_scale=0.95)

    def play_plasma(self):
        """Plasma Cannon fire sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("plasma", min_interval_ms=80, channel_id=ch_idx, volume_scale=1.0)

    def play_rail(self):
        """Precision Railgun fire sound."""
        ch_idx = CHANNELS_WEAPONS[self._weapon_channel_idx]
        self._weapon_channel_idx = (self._weapon_channel_idx + 1) % len(CHANNELS_WEAPONS)
        self._play_cached("rail", min_interval_ms=80, channel_id=ch_idx, volume_scale=1.0)

    def play_beam(self):
        """Plasma Cutting Laser fire sound."""
        self._play_cached("beam", min_interval_ms=60, volume_scale=0.80)

    def play_tesla(self):
        """Tesla Arc lightning sound."""
        self._play_cached("tesla", min_interval_ms=60, volume_scale=0.90)

    def play_cluster(self):
        """Cluster Torpedo fire sound."""
        self._play_cached("cluster", min_interval_ms=80, volume_scale=0.95)

    def play_sniper(self):
        """Railgun Sniper beam fire sound."""
        self.play_rail()

    def play_emp(self):
        """EMP blast wave sound."""
        self._play_cached("emp", min_interval_ms=120, channel_id=CHANNEL_PLAYER, volume_scale=1.0)


    # =========================================================================
    # TARGET-SPECIFIC IMPACT METHODS
    # =========================================================================
    def play_hit(self, target_type: str | None = None):
        """Dispatches target-specific impact audio."""
        if target_type == "scout":
            self.play_hit_scout()
        elif target_type == "shooter":
            self.play_hit_shooter()
        elif target_type in ("heavy", "armored"):
            self.play_hit_heavy()
        elif target_type in ("shield", "shield_elite", "shield_drone"):
            self.play_hit_shield()
        elif target_type == "boss":
            self.play_hit_boss()
        else:
            self._play_cached("hit", min_interval_ms=30, volume_scale=0.75)

    def play_hit_scout(self):
        """Scout impact audio."""
        self._play_cached("hit_scout", min_interval_ms=30, volume_scale=0.70)

    def play_hit_shooter(self):
        """Shooter metallic impact audio."""
        self._play_cached("hit_shooter", min_interval_ms=30, volume_scale=0.80)

    def play_hit_heavy(self):
        """Heavy armor clang audio."""
        self._play_cached("hit_heavy", min_interval_ms=35, volume_scale=0.95)

    def play_hit_shield(self):
        """Shield energy pulse impact audio."""
        self._play_cached("hit_shield", min_interval_ms=35, volume_scale=0.85)

    def play_hit_boss(self):
        """Boss structural impact audio."""
        self._play_cached("hit_boss", min_interval_ms=40, channel_id=CHANNEL_BOSS, volume_scale=1.0)

    # =========================================================================
    # TARGET-SPECIFIC DESTRUCTION METHODS
    # =========================================================================
    def play_death(self, target_type: str | None = None):
        """Dispatches target-specific destruction audio."""
        if target_type == "scout":
            self.play_death_scout()
        elif target_type == "shooter":
            self.play_death_shooter()
        elif target_type in ("heavy", "armored"):
            self.play_death_heavy()
        elif target_type in ("shield", "shield_elite", "shield_drone"):
            self.play_death_shield()
        elif target_type == "boss":
            self.play_boss_death()
        else:
            self.play_explosion()

    def play_death_scout(self):
        """Scout destruction burst."""
        self._play_cached("death_scout", min_interval_ms=45, volume_scale=0.80)

    def play_death_shooter(self):
        """Shooter metallic destruction."""
        self._play_cached("death_shooter", min_interval_ms=45, volume_scale=0.85)

    def play_death_heavy(self):
        """Heavy deep explosion."""
        self._play_cached("death_heavy", min_interval_ms=50, volume_scale=1.0)

    def play_death_shield(self):
        """Shield drone energy collapse."""
        self._play_cached("death_shield", min_interval_ms=50, volume_scale=0.90)

    def play_explosion(self):
        """Generic explosion sound."""
        self._play_cached("explosion", min_interval_ms=45, volume_scale=0.85)

    def play_mine_explosion(self):
        """Environmental mine detonation."""
        self._play_cached("explosion", min_interval_ms=45, volume_scale=0.90)

    # =========================================================================
    # PLAYER AUDIO METHODS
    # =========================================================================
    def play_player_hit(self):
        """Player takes damage warning sound."""
        self._play_cached("player_hit", min_interval_ms=50, channel_id=CHANNEL_PLAYER, volume_scale=1.0)

    def play_player_death(self):
        """Player destruction terminal sound."""
        self._play_cached("player_death", min_interval_ms=200, channel_id=CHANNEL_PLAYER, volume_scale=1.0)

    def play_roll(self):
        """Player barrel roll whoosh."""
        self._play_cached("roll", min_interval_ms=80, channel_id=CHANNEL_PLAYER, volume_scale=0.85)

    def play_whoosh(self):
        """Legacy whoosh alias."""
        self.play_roll()

    def play_overdrive(self):
        """Tactical Overdrive activation."""
        self._play_cached("overdrive", min_interval_ms=150, channel_id=CHANNEL_PLAYER, volume_scale=1.0)

    def play_cloak(self):
        """Tactical Cloak activation."""
        self._play_cached("cloak", min_interval_ms=100, channel_id=CHANNEL_PLAYER, volume_scale=0.85)

    def play_powerup(self):
        """Power-up collected chime."""
        self._play_cached("powerup", min_interval_ms=50, channel_id=CHANNEL_UI, volume_scale=0.85)

    def update_engine_sound(self, speed_ratio: float, is_accelerating: bool):
        """Modulates dynamic looping ion engine sound based on player movement velocity."""
        if not self.sound_enabled or not self.mixer_initialized:
            return

        try:
            if self._engine_channel is None:
                self._engine_channel = pygame.mixer.Channel(CHANNEL_ENGINE)

            snd = self._sound_cache.get("engine_hum")
            if snd is None:
                return

            if not self._engine_channel.get_busy():
                self._engine_channel.play(snd, loops=-1)

            # Modulate volume: 0.12 at idle, up to 0.45 under boost/full thrust
            base_vol = 0.12 if not is_accelerating else 0.25
            dynamic_vol = base_vol + 0.20 * min(1.0, max(0.0, speed_ratio))
            effective_vol = max(0.0, min(1.0, self.master_volume * self.engine_volume * dynamic_vol))
            self._engine_channel.set_volume(effective_vol)
        except Exception:
            pass

    def stop_engine_sound(self):
        """Stops the looping engine channel cleanly."""
        if self._engine_channel:
            try:
                self._engine_channel.stop()
            except Exception:
                pass

    # =========================================================================
    # BOSS AUDIO METHODS
    # =========================================================================
    def play_boss_alert(self):
        """Boss spawn siren / intro alert."""
        self._play_cached("boss_alert", min_interval_ms=200, channel_id=CHANNEL_BOSS, volume_scale=1.0)

    def play_boss_attack(self):
        """Boss attack telegraph / fire."""
        self._play_cached("boss_attack", min_interval_ms=80, channel_id=CHANNEL_BOSS, volume_scale=0.95)

    def play_boss_phase(self, phase: int):
        """Plays one-shot phase transition energy surge."""
        key = f"boss_phase_{min(4, max(2, phase))}"
        self._play_cached(key, min_interval_ms=200, channel_id=CHANNEL_BOSS, volume_scale=1.0)

    def play_boss_death(self):
        """Boss destruction major sequence."""
        self._play_cached("death_boss", min_interval_ms=200, channel_id=CHANNEL_BOSS, volume_scale=1.0)

    # =========================================================================
    # UI & PROGRESSION AUDIO METHODS
    # =========================================================================
    def play_ui_click(self):
        """Button click."""
        self._play_cached("ui_click", min_interval_ms=25, channel_id=CHANNEL_UI, volume_scale=0.70)

    def play_ui_hover(self):
        """Button hover."""
        self._play_cached("ui_hover", min_interval_ms=20, channel_id=CHANNEL_UI, volume_scale=0.45)

    def play_mission_start(self):
        """Mission deployment."""
        self._play_cached("mission_start", min_interval_ms=100, channel_id=CHANNEL_UI, volume_scale=0.85)

    def play_mission_complete(self):
        """Mission victory."""
        self._play_cached("mission_complete", min_interval_ms=150, channel_id=CHANNEL_UI, volume_scale=0.95)

    def play_game_over(self):
        """Mission failed tone."""
        self._play_cached("game_over", min_interval_ms=200, channel_id=CHANNEL_UI, volume_scale=1.0)

    def play_victory(self):
        """Campaign victory fanfare."""
        self._play_cached("victory", min_interval_ms=200, channel_id=CHANNEL_UI, volume_scale=1.0)

    def play_buy(self):
        """Upgrade purchase."""
        self._play_cached("buy", min_interval_ms=50, channel_id=CHANNEL_UI, volume_scale=0.80)

    def play_upgrade(self):
        """Upgrade alias."""
        self.play_buy()

    def play_warning(self):
        """Low health warning."""
        self._play_cached("player_hit", min_interval_ms=120, channel_id=CHANNEL_PLAYER, volume_scale=0.85)

    def play_sector_ambient(self, sector_idx: int):
        """Ambient audio placeholder."""
        pass
