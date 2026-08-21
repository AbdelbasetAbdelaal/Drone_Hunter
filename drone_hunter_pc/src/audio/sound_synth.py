"""
================================================================================
                    DRONE HUNTER 2D - PROCEDURAL SYNTH GENERATOR
================================================================================
Pure Python procedural wave generators synthesizing futuristic 16-bit sound
effects for weapons, target-specific impacts, destructions, boss phases,
player events, engine hum, and UI interactions.
"""

import math
import array
import pygame

SAMPLE_RATE = 22050


def _build_sound(samples: list[int] | array.array) -> pygame.mixer.Sound | None:
    """Safely converts 16-bit PCM integer samples to a pygame Sound object."""
    try:
        if not pygame.mixer.get_init():
            return None
        buf = array.array("h", [max(-32767, min(32767, int(s))) for s in samples])
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


# =============================================================================
# 1. WEAPON SFX GENERATORS
# =============================================================================

def generate_laser_sound() -> pygame.mixer.Sound | None:
    """Pulse Laser: Sharp futuristic energy bolt (950Hz -> 140Hz downward chirp)."""
    try:
        duration = 0.10
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.5
            freq = 950.0 * (1.0 - (t / duration) ** 1.8) + 140.0
            val = math.sin(2.0 * math.pi * freq * t) * 16000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_scatter_sound() -> pygame.mixer.Sound | None:
    """Spread Cannon: Rapid multi-burst energy discharge."""
    try:
        duration = 0.14
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration)
            burst = (math.sin(2.0 * math.pi * 32.0 * t) + 1.0) * 0.5
            freq = 750.0 * (1.0 - t / duration) + 200.0
            val = math.sin(2.0 * math.pi * freq * t) * 14000.0 * env * (0.4 + 0.6 * burst)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_missile_sound() -> pygame.mixer.Sound | None:
    """Heavy Missile: Mechanical launch click + low-frequency rocket rumble."""
    try:
        duration = 0.24
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            freq = 180.0 + 90.0 * math.sin(2.0 * math.pi * 28.0 * t)
            noise = ((i * 73) % 2000 - 1000) / 1000.0 * 0.45
            tone = math.sin(2.0 * math.pi * freq * t) * 0.55
            val = (tone + noise) * 15000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_beam_sound() -> pygame.mixer.Sound | None:
    """Plasma Cutting Beam: High-frequency piercing laser hum."""
    try:
        duration = 0.09
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 2.0
            freq = 1450.0 + 350.0 * math.sin(2.0 * math.pi * 110.0 * t)
            val = math.sin(2.0 * math.pi * freq * t) * 12000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_tesla_sound() -> pygame.mixer.Sound | None:
    """Tesla Arc: Electric arc crackle and lightning zap."""
    try:
        duration = 0.16
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 620.0 + 480.0 * math.sin(2.0 * math.pi * 140.0 * t)
            noise = ((i % 19) - 9) / 9.0 * 0.5
            val = (math.sin(2.0 * math.pi * freq * t) * 0.5 + noise) * 16000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_cluster_sound() -> pygame.mixer.Sound | None:
    """Cluster Torpedo: Heavy ballistic launch + submunition ignition."""
    try:
        duration = 0.26
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 0.8
            freq = 220.0 * (1.0 - t / duration) + 60.0
            noise = ((i * 37) % 2000 - 1000) / 1000.0 * 0.55
            val = (math.sin(2.0 * math.pi * freq * t) * 0.45 + noise) * 17000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_sniper_sound() -> pygame.mixer.Sound | None:
    """Sniper Railgun: Supersonic railgun crack + tail."""
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.8
            freq = 1900.0 * (1.0 - (t / duration) ** 2.2) + 240.0
            val = math.sin(2.0 * math.pi * freq * t) * 21000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_emp_sound() -> pygame.mixer.Sound | None:
    """EMP Blast: Expanding electromagnetic shockwave surge."""
    try:
        duration = 0.42
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.7
            freq = 880.0 * math.sin(2.0 * math.pi * 14.0 * t) + 320.0
            val = math.sin(2.0 * math.pi * freq * t) * 22000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 2. TARGET-SPECIFIC IMPACT SFX GENERATORS
# =============================================================================

def generate_hit_scout_sound() -> pygame.mixer.Sound | None:
    """Scout Hit: Light, agile electronic ping."""
    try:
        duration = 0.05
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 700.0 * (1.0 - t / duration) + 400.0
            val = math.sin(2.0 * math.pi * freq * t) * 11000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_shooter_sound() -> pygame.mixer.Sound | None:
    """Shooter Hit: Crisp metallic impact / deflection."""
    try:
        duration = 0.06
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 480.0 + 120.0 * math.sin(2.0 * math.pi * 60.0 * t)
            noise = ((i * 19) % 2000 - 1000) / 1000.0 * 0.3
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 + noise) * 13000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_heavy_sound() -> pygame.mixer.Sound | None:
    """Heavy Hit: Deep metallic armor clang with low-frequency resonance."""
    try:
        duration = 0.09
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.2
            freq = 240.0 * (1.0 - t / duration) + 90.0
            noise = ((i * 31) % 2000 - 1000) / 1000.0 * 0.4
            val = (math.sin(2.0 * math.pi * freq * t) * 0.6 + noise) * 17000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_shield_sound() -> pygame.mixer.Sound | None:
    """Shield Hit: High-tech energy absorption sizzle / pulse."""
    try:
        duration = 0.08
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 1100.0 + 400.0 * math.sin(2.0 * math.pi * 45.0 * t)
            val = math.sin(2.0 * math.pi * freq * t) * 14000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_boss_sound() -> pygame.mixer.Sound | None:
    """Boss Hit: Deep structural bass thud / massive armor reverberation."""
    try:
        duration = 0.12
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.3
            freq = 160.0 * (1.0 - (t / duration) * 0.5) + 60.0
            noise = ((i * 47) % 2000 - 1000) / 1000.0 * 0.35
            val = (math.sin(2.0 * math.pi * freq * t) * 0.65 + noise) * 20000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_sound() -> pygame.mixer.Sound | None:
    """Generic Hit Fallback."""
    return generate_hit_shooter_sound()


# =============================================================================
# 3. ENEMY & BOSS DESTRUCTION SFX GENERATORS
# =============================================================================

def generate_death_scout_sound() -> pygame.mixer.Sound | None:
    """Scout Destruction: Fast small electronic pop explosion."""
    try:
        duration = 0.20
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.2
            noise = ((i * 61) % 2000 - 1000) / 1000.0
            freq = 600.0 * (1.0 - t / duration) + 150.0
            val = (noise * 0.65 + math.sin(2.0 * math.pi * freq * t) * 0.35) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shooter_sound() -> pygame.mixer.Sound | None:
    """Shooter Destruction: Metallic burst and fragmentation explosion."""
    try:
        duration = 0.25
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.9
            noise = ((i * 73) % 2000 - 1000) / 1000.0
            freq = 360.0 * (1.0 - t / duration) + 120.0
            val = (noise * 0.7 + math.sin(2.0 * math.pi * freq * t) * 0.3) * 20000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_heavy_sound() -> pygame.mixer.Sound | None:
    """Heavy Destruction: Deep dual-stage explosion with heavy debris."""
    try:
        duration = 0.38
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.7
            noise = ((i * 43) % 2000 - 1000) / 1000.0
            sub_bass = math.sin(2.0 * math.pi * (110.0 * (1.0 - t / duration) + 40.0) * t) * 0.5
            val = (noise * 0.5 + sub_bass) * 23000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shield_sound() -> pygame.mixer.Sound | None:
    """Shield Elite Destruction: Energy discharge and electrical collapse."""
    try:
        duration = 0.30
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            freq = 800.0 * (1.0 - t / duration) + 180.0
            mod = math.sin(2.0 * math.pi * 50.0 * t)
            noise = ((i * 53) % 2000 - 1000) / 1000.0 * 0.3
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 * mod + noise) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_boss_sound() -> pygame.mixer.Sound | None:
    """Boss Destruction: Massive multi-layered cinematic dreadnought explosion."""
    try:
        duration = 0.65
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.6
            noise = ((i * 31) % 2000 - 1000) / 1000.0
            sub_bass = math.sin(2.0 * math.pi * (80.0 * (1.0 - (t / duration) * 0.7) + 30.0) * t) * 0.6
            val = (noise * 0.4 + sub_bass) * 26000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_explosion_sound() -> pygame.mixer.Sound | None:
    """Generic Explosion Fallback."""
    return generate_death_shooter_sound()


# =============================================================================
# 4. PLAYER AUDIO SFX GENERATORS
# =============================================================================

def generate_player_hit_sound() -> pygame.mixer.Sound | None:
    """Player Damage: Cockpit warning chirp + hull impact."""
    try:
        duration = 0.12
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            alarm = math.sin(2.0 * math.pi * 880.0 * t) * 0.5
            impact = math.sin(2.0 * math.pi * 200.0 * t) * 0.5
            val = (alarm + impact) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_player_death_sound() -> pygame.mixer.Sound | None:
    """Player Destruction: Emergency power failure -> terminal catastrophic explosion."""
    try:
        duration = 0.55
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.7
            if t < 0.15:
                # Descending system power failure whine
                freq = 1200.0 * (1.0 - t / 0.15) + 200.0
                val = math.sin(2.0 * math.pi * freq * t) * 20000.0
            else:
                # Core breach detonation
                t_exp = t - 0.15
                noise = ((i * 41) % 2000 - 1000) / 1000.0
                sub = math.sin(2.0 * math.pi * 70.0 * t_exp) * 0.5
                val = (noise * 0.5 + sub) * 25000.0 * (1.0 - t_exp / 0.40)
            samples.append(val * env)
        return _build_sound(samples)
    except Exception:
        return None


def generate_roll_sound() -> pygame.mixer.Sound | None:
    """Tactical Barrel Roll: Aerodynamic whoosh / thruster surge."""
    try:
        duration = 0.20
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = math.sin(math.pi * (t / duration))
            freq = 260.0 + 380.0 * math.sin(math.pi * (t / duration))
            noise = ((i * 17) % 2000 - 1000) / 1000.0 * 0.25
            val = (math.sin(2.0 * math.pi * freq * t) * 0.75 + noise) * 15000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_engine_hum_sound() -> pygame.mixer.Sound | None:
    """Player Engine Loop: Seamless subtle futuristic ion drive hum (0.5s loop)."""
    try:
        duration = 0.50
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Dual harmonic hum with subtle pulse
            h1 = math.sin(2.0 * math.pi * 110.0 * t) * 0.6
            h2 = math.sin(2.0 * math.pi * 220.0 * t) * 0.4
            val = (h1 + h2) * 6000.0
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_overdrive_sound() -> pygame.mixer.Sound | None:
    """Tactical Overdrive: Ascending power overload surge."""
    try:
        duration = 0.35
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            f1 = 440.0 + 880.0 * (t / duration)
            f2 = 660.0 + 1320.0 * (t / duration)
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 18000.0 * (1.0 - (t / duration) ** 2.0)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_cloak_sound() -> pygame.mixer.Sound | None:
    """Cloak: Phase shifting frequency fade."""
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 900.0 * (1.0 - (t / duration)) + 200.0
            val = math.sin(2.0 * math.pi * freq * t) * 13000.0 * (1.0 - t / duration)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 5. BOSS COMBAT SFX GENERATORS
# =============================================================================

def generate_boss_alert_sound() -> pygame.mixer.Sound | None:
    """Boss Warning Siren / Mechanical Activation Klaxon."""
    try:
        duration = 0.45
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.5
            freq = 380.0 + 120.0 * math.sin(2.0 * math.pi * 6.0 * t)
            sub = math.sin(2.0 * math.pi * 95.0 * t) * 0.4
            val = (math.sin(2.0 * math.pi * freq * t) * 0.6 + sub) * 22000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_boss_attack_sound() -> pygame.mixer.Sound | None:
    """Boss Attack Charge / Weapon Discharge."""
    try:
        duration = 0.28
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration)
            freq = 150.0 + 400.0 * (t / duration)
            noise = ((i * 29) % 2000 - 1000) / 1000.0 * 0.3
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 + noise) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_boss_phase_transition_sound(phase: int = 2) -> pygame.mixer.Sound | None:
    """Boss Phase Transition Energy Surge (P2 Amber, P3 Crimson, P4 Overload)."""
    try:
        duration = 0.45
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        base_freq = 300.0 * phase
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            freq = base_freq + 300.0 * math.sin(2.0 * math.pi * 12.0 * t)
            sub = math.sin(2.0 * math.pi * 65.0 * t) * 0.5
            val = (math.sin(2.0 * math.pi * freq * t) * 0.5 + sub) * 24000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 6. UI & PROGRESSION SFX GENERATORS
# =============================================================================

def generate_ui_click_sound() -> pygame.mixer.Sound | None:
    """UI Click: Crisp mechanical sci-fi switch click."""
    try:
        duration = 0.04
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            val = math.sin(2.0 * math.pi * 1200.0 * t) * 10000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_ui_hover_sound() -> pygame.mixer.Sound | None:
    """UI Hover: Soft tactical blip."""
    try:
        duration = 0.025
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            val = math.sin(2.0 * math.pi * 800.0 * t) * 6000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_mission_start_sound() -> pygame.mixer.Sound | None:
    """Mission Deploy Chime."""
    try:
        duration = 0.32
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.4
            f1 = 523.25 # C5
            f2 = 659.25 # E5
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 15000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_mission_complete_sound() -> pygame.mixer.Sound | None:
    """Mission Complete Fanfare."""
    try:
        duration = 0.45
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.2
            freq = 659.25 if t < 0.15 else (783.99 if t < 0.30 else 1046.50) # E5 -> G5 -> C6
            val = math.sin(2.0 * math.pi * freq * t) * 16000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_game_over_sound() -> pygame.mixer.Sound | None:
    """Mission Failed / Game Over Tone."""
    try:
        duration = 0.50
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 320.0 * (1.0 - (t / duration) * 0.6) + 80.0
            val = math.sin(2.0 * math.pi * freq * t) * 17000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_victory_sound() -> pygame.mixer.Sound | None:
    """Grand Campaign Victory Fanfare."""
    try:
        duration = 0.70
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            f1 = 523.25 * (1.0 + 0.5 * (t / duration))
            f2 = 783.99 * (1.0 + 0.5 * (t / duration))
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_powerup_sound() -> pygame.mixer.Sound | None:
    """Power-up Collected."""
    try:
        duration = 0.18
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 520.0 + 800.0 * (t / duration)
            val = math.sin(2.0 * math.pi * freq * t) * 16000.0 * (1.0 - t / duration)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_buy_sound() -> pygame.mixer.Sound | None:
    """Upgrade Purchased / Transaction Sound."""
    try:
        duration = 0.14
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 700.0 + 600.0 * (t / duration)
            val = math.sin(2.0 * math.pi * freq * t) * 15000.0 * (1.0 - t / duration)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None

