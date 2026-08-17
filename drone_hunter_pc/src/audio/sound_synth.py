"""
================================================================================
                    DRONE HUNTER 2D - PROCEDURAL SYNTH GENERATOR
================================================================================
Pure Python procedural wave generators synthesizing 8-bit / 16-bit sound effects.
"""

import math
import array
import pygame

SAMPLE_RATE = 22050

def generate_laser_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.12
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 900.0 * (1.0 - (t / duration) ** 1.8) + 120.0
            val = int(math.sin(2.0 * math.pi * freq * t) * 14000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_missile_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 240.0 + 80.0 * math.sin(2.0 * math.pi * 35.0 * t)
            noise = math.sin(i * 1337.0) * 0.3
            val = int((math.sin(2.0 * math.pi * freq * t) + noise) * 12000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_beam_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.08
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 1400.0 + 300.0 * math.sin(2.0 * math.pi * 90.0 * t)
            val = int(math.sin(2.0 * math.pi * freq * t) * 10000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_tesla_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.16
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 600.0 + 450.0 * math.sin(2.0 * math.pi * 120.0 * t)
            noise = ((i % 17) - 8) / 8.0 * 0.4
            val = int((math.sin(2.0 * math.pi * freq * t) + noise) * 15000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_cluster_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.28
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 180.0 * (1.0 - (t / duration)) + 50.0
            noise = ((i % 23) - 11) / 11.0 * 0.6
            val = int((math.sin(2.0 * math.pi * freq * t) + noise) * 18000.0 * (1.0 - (t / duration) ** 0.8))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_sniper_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.24
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 1800.0 * (1.0 - (t / duration) ** 2.2) + 200.0
            val = int(math.sin(2.0 * math.pi * freq * t) * 20000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_overdrive_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.35
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            f1 = 440.0 + 880.0 * (t / duration)
            f2 = 660.0 + 1320.0 * (t / duration)
            val = int((math.sin(2.0 * math.pi * f1 * t) * 0.5 + math.sin(2.0 * math.pi * f2 * t) * 0.5) * 18000.0 * (1.0 - (t / duration) ** 2.0))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_explosion_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.30
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            noise = ((i * 73) % 2000 - 1000) / 1000.0
            val = int(noise * 22000.0 * (1.0 - (t / duration) ** 0.6))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_hit_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.06
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            val = int(math.sin(2.0 * math.pi * 320.0 * t) * 12000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_emp_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.40
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 800.0 * math.sin(2.0 * math.pi * 15.0 * t) + 300.0
            val = int(math.sin(2.0 * math.pi * freq * t) * 20000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_powerup_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.18
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 520.0 + 800.0 * (t / duration)
            val = int(math.sin(2.0 * math.pi * freq * t) * 16000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_roll_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.20
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 280.0 + 350.0 * math.sin(math.pi * (t / duration))
            val = int(math.sin(2.0 * math.pi * freq * t) * 14000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_cloak_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.22
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 900.0 * (1.0 - (t / duration)) + 200.0
            val = int(math.sin(2.0 * math.pi * freq * t) * 13000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def generate_buy_sound() -> pygame.mixer.Sound | None:
    try:
        duration = 0.14
        num_samples = int(SAMPLE_RATE * duration)
        buf = array.array("h")
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 700.0 + 600.0 * (t / duration)
            val = int(math.sin(2.0 * math.pi * freq * t) * 15000.0 * (1.0 - t / duration))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None
