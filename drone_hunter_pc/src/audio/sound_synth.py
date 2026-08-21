"""
================================================================================
                    DRONE HUNTER 2D - PROCEDURAL SYNTH GENERATOR
================================================================================
Pure Python procedural multi-harmonic wave generators synthesizing realistic,
heavy industrial / military futuristic battlefield audio effects:
- High-energy kinetic transients and mechanical snaps
- Deep sub-bass explosive body (40Hz - 120Hz)
- Shaped noise-filtered fragmentation and debris
- Distinct weapon identities (Pulse, Rapid, Scatter, Missile, Barrage, Plasma, Rail, Beam, Tesla, Cluster, EMP)
- Dedicated Mission Victory Fanfare and Mission Defeat / Downed Drone sequences
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
# 1. REALISTIC WEAPON SFX GENERATORS
# =============================================================================

def generate_laser_sound() -> pygame.mixer.Sound | None:
    """Pulse Laser: Sharp military energy bolt (kinetic transient + downward chirp + low punch)."""
    try:
        duration = 0.11
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.8
            freq = 1100.0 * (1.0 - (t / duration) ** 2.0) + 160.0
            tone = math.sin(2.0 * math.pi * freq * t) * 0.75
            sub = math.sin(2.0 * math.pi * 95.0 * t) * 0.35 * (1.0 - t / duration)
            noise = (((i * 47) % 2000 - 1000) / 1000.0) * 0.25 * math.exp(-t * 60.0)
            val = (tone + sub + noise) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_rapid_sound() -> pygame.mixer.Sound | None:
    """Rapid Autocannon: High-cyclic kinetic round with mechanical chamber snap."""
    try:
        duration = 0.075
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.4
            transient = (((i * 97) % 2000 - 1000) / 1000.0) * math.exp(-t * 120.0) * 0.5
            freq = 820.0 * (1.0 - t / duration) + 240.0
            tone = math.sin(2.0 * math.pi * freq * t) * 0.6
            sub = math.sin(2.0 * math.pi * 140.0 * t) * 0.35
            val = (transient + tone + sub) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_scatter_sound() -> pygame.mixer.Sound | None:
    """Spread Cannon: Heavy shotgun energy blast with bass concussion."""
    try:
        duration = 0.18
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.2
            noise = (((i * 31) % 2000 - 1000) / 1000.0) * 0.6
            sub = math.sin(2.0 * math.pi * (85.0 * (1.0 - t / duration) + 35.0) * t) * 0.55
            crack = math.sin(2.0 * math.pi * (650.0 * (1.0 - t / duration) + 120.0) * t) * 0.35
            val = (noise + sub + crack) * 21000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_missile_sound() -> pygame.mixer.Sound | None:
    """Heavy Missile: Pneumatic launch click + solid rocket motor propulsion roar."""
    try:
        duration = 0.28
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.85
            thrust = ((i * 73) % 2000 - 1000) / 1000.0 * 0.5
            freq = 140.0 + 60.0 * math.sin(2.0 * math.pi * 24.0 * t)
            sub = math.sin(2.0 * math.pi * freq * t) * 0.55
            val = (thrust + sub) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_barrage_sound() -> pygame.mixer.Sound | None:
    """Missile Barrage: Multi-tube salvo hiss and rocket boost ignition."""
    try:
        duration = 0.32
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.9
            hiss = ((i * 89) % 2000 - 1000) / 1000.0 * 0.45 * (1.0 + math.sin(2.0 * math.pi * 18.0 * t))
            sub = math.sin(2.0 * math.pi * 160.0 * t) * 0.4
            val = (hiss + sub) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_plasma_sound() -> pygame.mixer.Sound | None:
    """Plasma Cannon: Deep magnetic containment discharge + heavy plasma ionization."""
    try:
        duration = 0.30
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.1
            f1 = 280.0 * (1.0 - (t / duration) * 0.6) + 45.0
            f2 = 560.0 * (1.0 - t / duration) + 90.0
            sub = math.sin(2.0 * math.pi * f1 * t) * 0.65
            harmonic = math.sin(2.0 * math.pi * f2 * t) * 0.35
            val = (sub + harmonic) * 23000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_rail_sound() -> pygame.mixer.Sound | None:
    """Precision Railgun: Supersonic kinetic snap + heavy thunderous sonic boom tail."""
    try:
        duration = 0.38
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.6
            crack = math.sin(2.0 * math.pi * (2400.0 * (1.0 - (t / 0.04) ** 2.0) + 300.0) * t) * math.exp(-t * 70.0) if t < 0.04 else 0.0
            boom = math.sin(2.0 * math.pi * (75.0 * (1.0 - t / duration) + 30.0) * t) * 0.7
            noise = (((i * 41) % 2000 - 1000) / 1000.0) * 0.35 * (1.0 - t / duration)
            val = (crack * 0.7 + boom + noise) * 26000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_sniper_sound() -> pygame.mixer.Sound | None:
    """Sniper Railgun alias."""
    return generate_rail_sound()



def generate_beam_sound() -> pygame.mixer.Sound | None:
    """Plasma Cutting Beam: High-frequency cutting laser resonance and sizzling hum."""
    try:
        duration = 0.10
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 2.0
            freq = 1550.0 + 380.0 * math.sin(2.0 * math.pi * 120.0 * t)
            noise = ((i * 13) % 2000 - 1000) / 1000.0 * 0.2
            val = (math.sin(2.0 * math.pi * freq * t) * 0.8 + noise) * 14000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_tesla_sound() -> pygame.mixer.Sound | None:
    """Tesla Arc: Violent high-voltage electric crackle and jagged discharge."""
    try:
        duration = 0.18
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 680.0 + 520.0 * math.sin(2.0 * math.pi * 160.0 * t)
            noise = ((i % 17) - 8) / 8.0 * 0.65
            val = (math.sin(2.0 * math.pi * freq * t) * 0.45 + noise) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_cluster_sound() -> pygame.mixer.Sound | None:
    """Cluster Torpedo: Heavy mortar tube thud + submunition dispersion."""
    try:
        duration = 0.28
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 0.8
            freq = 190.0 * (1.0 - t / duration) + 55.0
            noise = ((i * 37) % 2000 - 1000) / 1000.0 * 0.55
            val = (math.sin(2.0 * math.pi * freq * t) * 0.5 + noise) * 20000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_emp_sound() -> pygame.mixer.Sound | None:
    """EMP Blast: Expanding electromagnetic shockwave surge + high ring down."""
    try:
        duration = 0.45
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.75
            freq = 920.0 * math.sin(2.0 * math.pi * 12.0 * t) + 300.0
            sub = math.sin(2.0 * math.pi * 60.0 * t) * 0.45
            val = (math.sin(2.0 * math.pi * freq * t) * 0.65 + sub) * 24000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 2. TARGET-SPECIFIC IMPACT SFX GENERATORS
# =============================================================================

def generate_hit_scout_sound() -> pygame.mixer.Sound | None:
    """Scout Hit: Agile high-frequency metallic ping."""
    try:
        duration = 0.05
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            val = math.sin(2.0 * math.pi * 750.0 * t) * 12000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_shooter_sound() -> pygame.mixer.Sound | None:
    """Shooter Hit: Crisp armor ricochet / kinetic snap."""
    try:
        duration = 0.06
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            noise = ((i * 19) % 2000 - 1000) / 1000.0 * 0.35
            val = (math.sin(2.0 * math.pi * 520.0 * t) * 0.65 + noise) * 14000.0 * env
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
            freq = 220.0 * (1.0 - t / duration) + 80.0
            noise = ((i * 31) % 2000 - 1000) / 1000.0 * 0.45
            val = (math.sin(2.0 * math.pi * freq * t) * 0.6 + noise) * 18000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_shield_sound() -> pygame.mixer.Sound | None:
    """Shield Hit: High-tech energy absorption ripple sizzle."""
    try:
        duration = 0.08
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            freq = 1200.0 + 450.0 * math.sin(2.0 * math.pi * 50.0 * t)
            val = math.sin(2.0 * math.pi * freq * t) * 15000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_boss_sound() -> pygame.mixer.Sound | None:
    """Boss Hit: Deep dreadnought chassis reverberation / massive bass impact."""
    try:
        duration = 0.12
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.3
            freq = 140.0 * (1.0 - (t / duration) * 0.5) + 50.0
            noise = ((i * 47) % 2000 - 1000) / 1000.0 * 0.4
            val = (math.sin(2.0 * math.pi * freq * t) * 0.65 + noise) * 22000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_hit_sound() -> pygame.mixer.Sound | None:
    """Generic Hit Fallback."""
    return generate_hit_shooter_sound()


# =============================================================================
# 3. REALISTIC DESTRUCTION SFX GENERATORS
# =============================================================================

def generate_death_scout_sound() -> pygame.mixer.Sound | None:
    """Scout Destruction: Fast electronic pop + fragmentation."""
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 1.2
            noise = ((i * 61) % 2000 - 1000) / 1000.0
            freq = 550.0 * (1.0 - t / duration) + 140.0
            val = (noise * 0.65 + math.sin(2.0 * math.pi * freq * t) * 0.35) * 20000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shooter_sound() -> pygame.mixer.Sound | None:
    """Shooter Destruction: Metallic burst and fragmentation explosion."""
    try:
        duration = 0.28
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.95
            noise = ((i * 73) % 2000 - 1000) / 1000.0
            sub = math.sin(2.0 * math.pi * (140.0 * (1.0 - t / duration) + 50.0) * t) * 0.4
            val = (noise * 0.65 + sub) * 22000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_heavy_sound() -> pygame.mixer.Sound | None:
    """Heavy Destruction: Deep mechanical hull rupture + low sub-bass explosion."""
    try:
        duration = 0.42
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.7
            noise = ((i * 43) % 2000 - 1000) / 1000.0
            sub_bass = math.sin(2.0 * math.pi * (90.0 * (1.0 - t / duration) + 35.0) * t) * 0.65
            val = (noise * 0.45 + sub_bass) * 25000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shield_sound() -> pygame.mixer.Sound | None:
    """Shield Elite Destruction: Energy collapse implosion + dispersion zap."""
    try:
        duration = 0.32
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            freq = 900.0 * (1.0 - t / duration) + 160.0
            mod = math.sin(2.0 * math.pi * 55.0 * t)
            noise = ((i * 53) % 2000 - 1000) / 1000.0 * 0.35
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 * mod + noise) * 21000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_boss_sound() -> pygame.mixer.Sound | None:
    """Boss Destruction: Massive cinematic multi-layered dreadnought explosion."""
    try:
        duration = 0.75
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.6
            noise = ((i * 31) % 2000 - 1000) / 1000.0
            sub_bass = math.sin(2.0 * math.pi * (70.0 * (1.0 - (t / duration) * 0.7) + 25.0) * t) * 0.7
            val = (noise * 0.4 + sub_bass) * 28000.0 * env
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
    """Player Damage: Cockpit warning chirp + heavy hull impact."""
    try:
        duration = 0.14
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            alarm = math.sin(2.0 * math.pi * 920.0 * t) * 0.5
            impact = math.sin(2.0 * math.pi * 180.0 * t) * 0.55
            val = (alarm + impact) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_player_death_sound() -> pygame.mixer.Sound | None:
    """Player Destruction: Emergency power failure -> terminal catastrophic core breach."""
    try:
        duration = 0.65
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.65
            if t < 0.16:
                freq = 1300.0 * (1.0 - t / 0.16) + 180.0
                val = math.sin(2.0 * math.pi * freq * t) * 22000.0
            else:
                t_exp = t - 0.16
                noise = ((i * 41) % 2000 - 1000) / 1000.0
                sub = math.sin(2.0 * math.pi * 60.0 * t_exp) * 0.6
                val = (noise * 0.5 + sub) * 27000.0 * (1.0 - t_exp / 0.49)
            samples.append(val * env)
        return _build_sound(samples)
    except Exception:
        return None


def generate_roll_sound() -> pygame.mixer.Sound | None:
    """Tactical Barrel Roll: Aerodynamic whoosh / thruster boost surge."""
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = math.sin(math.pi * (t / duration))
            freq = 280.0 + 400.0 * math.sin(math.pi * (t / duration))
            noise = ((i * 17) % 2000 - 1000) / 1000.0 * 0.25
            val = (math.sin(2.0 * math.pi * freq * t) * 0.75 + noise) * 16000.0 * env
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
            h1 = math.sin(2.0 * math.pi * 110.0 * t) * 0.6
            h2 = math.sin(2.0 * math.pi * 220.0 * t) * 0.4
            val = (h1 + h2) * 6500.0
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
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 19000.0 * (1.0 - (t / duration) ** 2.0)
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
            val = math.sin(2.0 * math.pi * freq * t) * 14000.0 * (1.0 - t / duration)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 5. BOSS COMBAT SFX GENERATORS
# =============================================================================

def generate_boss_alert_sound() -> pygame.mixer.Sound | None:
    """Boss Warning Siren / Mechanical Dreadnought Activation Klaxon."""
    try:
        duration = 0.50
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.5
            freq = 380.0 + 140.0 * math.sin(2.0 * math.pi * 5.5 * t)
            sub = math.sin(2.0 * math.pi * 85.0 * t) * 0.45
            val = (math.sin(2.0 * math.pi * freq * t) * 0.6 + sub) * 24000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_boss_attack_sound() -> pygame.mixer.Sound | None:
    """Boss Heavy Attack Charge / Weapon Discharge."""
    try:
        duration = 0.30
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration)
            freq = 140.0 + 420.0 * (t / duration)
            noise = ((i * 29) % 2000 - 1000) / 1000.0 * 0.35
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 + noise) * 21000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_boss_phase_transition_sound(phase: int = 2) -> pygame.mixer.Sound | None:
    """Boss Phase Transition Energy Surge (P2 Amber, P3 Crimson, P4 Overload)."""
    try:
        duration = 0.48
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        base_freq = 280.0 * phase
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            freq = base_freq + 320.0 * math.sin(2.0 * math.pi * 12.0 * t)
            sub = math.sin(2.0 * math.pi * 60.0 * t) * 0.55
            val = (math.sin(2.0 * math.pi * freq * t) * 0.5 + sub) * 25000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


# =============================================================================
# 6. DEDICATED MISSION VICTORY & FAILURE THEMES
# =============================================================================

def generate_mission_complete_sound() -> pygame.mixer.Sound | None:
    """Mission Victory Fanfare: Triumphant futuristic brassy chord sequence."""
    try:
        duration = 0.60
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.3
            if t < 0.15:
                freq = 659.25
            elif t < 0.30:
                freq = 830.61
            elif t < 0.45:
                freq = 987.77
            else:
                freq = 1318.51
            lead = math.sin(2.0 * math.pi * freq * t) * 0.65
            sub = math.sin(2.0 * math.pi * (freq * 0.5) * t) * 0.35
            val = (lead + sub) * 19000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_victory_sound() -> pygame.mixer.Sound | None:
    """Grand Campaign Victory Fanfare: Powerful orchestral fanfare."""
    try:
        duration = 0.85
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.8
            f1 = 523.25 * (1.0 + 0.6 * (t / duration))
            f2 = 783.99 * (1.0 + 0.6 * (t / duration))
            f3 = 1046.50 * (1.0 + 0.6 * (t / duration))
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.4 + math.sin(2.0 * math.pi * f2 * t) * 0.35 + math.sin(2.0 * math.pi * f3 * t) * 0.25) * 22000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_game_over_sound() -> pygame.mixer.Sound | None:
    """Mission Failure Music: Dark, serious, descending drone power failure sequence."""
    try:
        duration = 0.70
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = (1.0 - t / duration) ** 0.9
            freq = 280.0 * (1.0 - (t / duration) ** 0.8) + 65.0
            drone = math.sin(2.0 * math.pi * freq * t) * 0.65
            sub = math.sin(2.0 * math.pi * (freq * 0.5) * t) * 0.35
            val = (drone + sub) * 20000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None


def generate_ui_click_sound() -> pygame.mixer.Sound | None:
    """UI Click: Crisp mechanical sci-fi switch click."""
    try:
        duration = 0.04
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - t / duration
            val = math.sin(2.0 * math.pi * 1200.0 * t) * 11000.0 * env
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
            val = math.sin(2.0 * math.pi * 820.0 * t) * 7000.0 * env
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
            f1 = 523.25
            f2 = 659.25
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 16000.0 * env
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
            val = math.sin(2.0 * math.pi * freq * t) * 17000.0 * (1.0 - t / duration)
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
            val = math.sin(2.0 * math.pi * freq * t) * 16000.0 * (1.0 - t / duration)
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None

