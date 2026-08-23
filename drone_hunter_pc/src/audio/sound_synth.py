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
    """Safely converts 16-bit PCM integer samples to a stereo/mono pygame Sound object."""
    try:
        init_params = pygame.mixer.get_init()
        if not init_params:
            return None
        channels = init_params[2] if len(init_params) > 2 else 2
        clamped = [max(-32767, min(32767, int(s))) for s in samples]
        if channels == 2:
            stereo_samples = []
            for s in clamped:
                stereo_samples.append(s)
                stereo_samples.append(s)
            buf = array.array("h", stereo_samples)
        else:
            buf = array.array("h", clamped)
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
# 3. REALISTIC PHYSICAL DESTRUCTION SFX GENERATORS (LOW-PASS FILTERED + SUB-BASS)
# =============================================================================

def generate_death_scout_sound() -> pygame.mixer.Sound | None:
    """Scout Destruction: Snappy kinetic pressure crack + high-velocity fragmentation."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 0.32
        num_samples = int(sr * duration)
        samples = []
        lp_state = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 1.3
            raw_noise = (((i * 982451653 + 12345) % 65536) - 32768) / 32768.0
            cutoff = 2400.0 * (1.0 - t / duration) ** 1.8 + 140.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp_state += alpha * (raw_noise - lp_state)

            snap = math.exp(-t * 95.0) * math.sin(2.0 * math.pi * 480.0 * t) * 0.85
            pitch = 140.0 * math.exp(-t * 9.0) + 55.0
            sub = math.sin(2.0 * math.pi * pitch * t) * 0.6 * math.exp(-t * 5.0)
            shrapnel = (((i * 73) % 2000 - 1000) / 1000.0) * 0.2 * math.exp(-t * 22.0)

            val = (snap + sub + lp_state * 0.55 + shrapnel) * 26000.0 * env
            samples.append(int(val))
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shooter_sound() -> pygame.mixer.Sound | None:
    """Shooter Destruction: Heavy explosive blast with low-pass fireball roar and rolling crackle."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 0.46
        num_samples = int(sr * duration)
        samples = []
        lp_state = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 1.15
            raw_noise = (((i * 15973347 + 654321) % 65536) - 32768) / 32768.0
            cutoff = 1900.0 * (1.0 - t / duration) ** 1.6 + 95.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp_state += alpha * (raw_noise - lp_state)

            snap = math.exp(-t * 80.0) * math.sin(2.0 * math.pi * 320.0 * t) * 0.95
            pitch = 110.0 * math.exp(-t * 7.0) + 42.0
            sub = math.sin(2.0 * math.pi * pitch * t) * 0.75 * math.exp(-t * 3.5)
            rumble = math.sin(2.0 * math.pi * 32.0 * t) * 0.3 * lp_state

            val = (snap + sub + lp_state * 0.65 + rumble) * 29000.0 * env
            samples.append(int(val))
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_heavy_sound() -> pygame.mixer.Sound | None:
    """Heavy Destruction: Massive armored chassis rupture, deep 35Hz sub-bass shockwave, cascading groan."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 0.68
        num_samples = int(sr * duration)
        samples = []
        lp1 = 0.0
        lp2 = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 0.9
            raw_noise = (((i * 87654321 + 112233) % 65536) - 32768) / 32768.0
            cutoff = 1400.0 * (1.0 - t / duration) ** 1.5 + 65.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp1 += alpha * (raw_noise - lp1)
            lp2 += alpha * (lp1 - lp2)  # 2-pole filtered deep bass body

            concussion = math.exp(-t * 60.0) * math.sin(2.0 * math.pi * 180.0 * t) * 1.1
            pitch = 85.0 * math.exp(-t * 5.0) + 34.0
            sub1 = math.sin(2.0 * math.pi * pitch * t) * 0.85 * math.exp(-t * 2.2)
            sub2 = math.sin(2.0 * math.pi * 24.0 * t) * 0.45 * math.exp(-t * 1.8)
            groan = math.sin(2.0 * math.pi * (160.0 * (1.0 - t / duration) + 50.0) * t) * 0.25 * lp1

            val = (concussion + sub1 + sub2 + lp2 * 0.8 + groan) * 31000.0 * env
            samples.append(int(val))
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_shield_sound() -> pygame.mixer.Sound | None:
    """Shield Elite Destruction: High-energy electromagnetic collapse, sizzle, and resonant bass release."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 0.52
        num_samples = int(sr * duration)
        samples = []
        lp_state = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 1.05
            raw_noise = (((i * 33445566 + 778899) % 65536) - 32768) / 32768.0
            cutoff = 2200.0 * (1.0 - t / duration) ** 1.7 + 90.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp_state += alpha * (raw_noise - lp_state)

            mod_freq = 750.0 * (1.0 - (t / duration) ** 1.5) + 80.0
            sizzle = math.sin(2.0 * math.pi * mod_freq * t) * math.sin(2.0 * math.pi * 55.0 * t) * 0.65
            sub = math.sin(2.0 * math.pi * (95.0 * (1.0 - t / duration) + 38.0) * t) * 0.7 * math.exp(-t * 3.0)

            val = (sizzle + sub + lp_state * 0.6) * 28000.0 * env
            samples.append(int(val))
        return _build_sound(samples)
    except Exception:
        return None


def generate_death_boss_sound() -> pygame.mixer.Sound | None:
    """Boss Destruction: Multi-stage catastrophic dreadnought detonation, seismic rumble, and rolling thunder."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 1.15
        num_samples = int(sr * duration)
        samples = []
        lp1 = 0.0
        lp2 = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 0.75
            raw_noise = (((i * 99887766 + 554433) % 65536) - 32768) / 32768.0
            cutoff = 1600.0 * (1.0 - t / duration) ** 1.3 + 55.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp1 += alpha * (raw_noise - lp1)
            lp2 += alpha * (lp1 - lp2)

            # Stage 1: Initial massive detonation wavefront
            blast1 = math.exp(-t * 40.0) * math.sin(2.0 * math.pi * 120.0 * t) * 1.2
            # Stage 2: Secondary internal breach explosions
            t_sub = max(0.0, t - 0.22)
            blast2 = math.exp(-t_sub * 25.0) * math.sin(2.0 * math.pi * 75.0 * t_sub) * 0.85 if t >= 0.22 else 0.0
            # Seismic sub-bass thunder (30Hz - 60Hz)
            sub = math.sin(2.0 * math.pi * 32.0 * t) * 0.9 * math.exp(-t * 1.2)
            sub_octave = math.sin(2.0 * math.pi * 20.0 * t) * 0.5 * math.exp(-t * 0.9)
            thunder_rumble = math.sin(2.0 * math.pi * 16.0 * t) * 0.35 * lp2

            val = (blast1 + blast2 + sub + sub_octave + lp2 * 0.9 + thunder_rumble) * 32000.0 * env
            samples.append(int(val))
        return _build_sound(samples)
    except Exception:
        return None


def generate_explosion_sound() -> pygame.mixer.Sound | None:
    """Generic Heavy Military Explosion."""
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
    """Player Destruction: Catastrophic core breach, explosive decompression, and low-frequency hull loss."""
    try:
        init_params = pygame.mixer.get_init()
        sr = init_params[0] if init_params else SAMPLE_RATE
        duration = 0.85
        num_samples = int(sr * duration)
        samples = []
        lp_state = 0.0
        for i in range(num_samples):
            t = i / sr
            env = (1.0 - t / duration) ** 0.85
            raw_noise = (((i * 6543219 + 789123) % 65536) - 32768) / 32768.0
            cutoff = 2000.0 * (1.0 - t / duration) ** 1.6 + 70.0
            alpha = min(1.0, 2.0 * math.pi * cutoff / sr)
            lp_state += alpha * (raw_noise - lp_state)

            if t < 0.10:
                whine = math.sin(2.0 * math.pi * (1600.0 * (1.0 - t / 0.10) + 200.0) * t) * 0.75
            else:
                whine = 0.0

            blast = math.exp(-t * 50.0) * math.sin(2.0 * math.pi * 140.0 * t) * 1.1
            sub = math.sin(2.0 * math.pi * 38.0 * t) * 0.85 * math.exp(-t * 1.8)

            val = (whine + blast + sub + lp_state * 0.75) * 30000.0 * env
            samples.append(int(val))
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


def generate_combo_sound() -> pygame.mixer.Sound | None:
    """Combo Streak escalation chime."""
    try:
        duration = 0.14
        num_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            env = 1.0 - (t / duration) ** 1.2
            f1 = 880.0 + 220.0 * (t / duration)
            f2 = 1100.0 + 330.0 * (t / duration)
            val = (math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 15000.0 * env
            samples.append(val)
        return _build_sound(samples)
    except Exception:
        return None

