import os
import wave
import struct
import math

SAMPLE_RATE = 22050

def save_wav(filename: str, samples: list[float]):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        packed_frames = bytearray()
        for s in samples:
            clamped = max(-32767, min(32767, int(s * 32767.0)))
            packed_frames.extend(struct.pack('<h', clamped))
        wav_file.writeframes(packed_frames)
    print(f"Generated {filename} ({len(samples)} samples)")

def gen_pulse():
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.8
        freq = 1200.0 * (1.0 - (t / duration) ** 1.8) + 140.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.75
        sub = math.sin(2.0 * math.pi * 95.0 * t) * 0.35 * (1.0 - t / duration)
        noise = (((i * 47) % 2000 - 1000) / 1000.0) * 0.2 * math.exp(-t * 60.0)
        val = (tone + sub + noise) * 0.85 * env
        samples.append(val)
    return samples

def gen_rapid():
    duration = 0.08
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.4
        transient = (((i * 97) % 2000 - 1000) / 1000.0) * math.exp(-t * 120.0) * 0.4
        freq = 900.0 * (1.0 - t / duration) + 200.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.6
        val = (transient + tone) * 0.8 * env
        samples.append(val)
    return samples

def gen_scatter():
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.2
        noise = (((i * 31) % 2000 - 1000) / 1000.0) * 0.55
        sub = math.sin(2.0 * math.pi * (85.0 * (1.0 - t / duration) + 40.0) * t) * 0.5
        val = (noise + sub) * 0.9 * env
        samples.append(val)
    return samples

def gen_missile():
    duration = 0.35
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.1
        freq = 380.0 * (1.0 - t / duration) + 60.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.65
        noise = (((i * 53) % 2000 - 1000) / 1000.0) * 0.45
        val = (tone + noise) * 0.85 * env
        samples.append(val)
    return samples

def gen_plasma():
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.3
        freq = 550.0 * (1.0 - math.sqrt(t / duration)) + 75.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.85
        sub = math.sin(2.0 * math.pi * 55.0 * t) * 0.5
        val = (tone + sub) * 0.9 * env
        samples.append(val)
    return samples

def gen_rail():
    duration = 0.25
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 2.0
        freq = 2400.0 * (1.0 - t / duration) + 300.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.8
        crack = (((i * 89) % 2000 - 1000) / 1000.0) * math.exp(-t * 80.0) * 0.7
        val = (tone + crack) * 0.95 * env
        samples.append(val)
    return samples

def gen_beam():
    duration = 0.1
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = min(1.0, t * 40.0) * (1.0 - t / duration)
        freq = 880.0 + math.sin(2.0 * math.pi * 45.0 * t) * 60.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.7
        buzz = math.sin(2.0 * math.pi * (freq * 2.0) * t) * 0.3
        val = (tone + buzz) * 0.75 * env
        samples.append(val)
    return samples

def gen_tesla():
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.5
        noise = (((i * 127) % 2000 - 1000) / 1000.0) * 0.6
        zap = math.sin(2.0 * math.pi * (1400.0 + ((i % 17) * 80.0)) * t) * 0.5
        val = (noise + zap) * 0.85 * env
        samples.append(val)
    return samples

def gen_emp():
    duration = 0.4
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.2
        freq = 1800.0 * (1.0 - t / duration) ** 2.0 + 80.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.8
        sub = math.sin(2.0 * math.pi * 60.0 * t) * 0.5
        val = (tone + sub) * 0.9 * env
        samples.append(val)
    return samples

def gen_hit():
    duration = 0.09
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 2.5
        noise = (((i * 73) % 2000 - 1000) / 1000.0) * 0.8
        thump = math.sin(2.0 * math.pi * 160.0 * t) * 0.6
        val = (noise + thump) * 0.8 * env
        samples.append(val)
    return samples

def gen_shield_hit():
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 2.0
        freq = 800.0 * (1.0 - t / duration) + 350.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.7
        ping = math.sin(2.0 * math.pi * 1200.0 * t) * 0.4
        val = (tone + ping) * 0.8 * env
        samples.append(val)
    return samples

def gen_pickup():
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 1.5
        # Upward arpeggio / chime
        freq = 440.0 + (t / duration) * 880.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.7
        harm = math.sin(2.0 * math.pi * (freq * 1.5) * t) * 0.3
        val = (tone + harm) * 0.75 * env
        samples.append(val)
    return samples

def gen_ui_click():
    duration = 0.05
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 3.0
        freq = 1400.0 * (1.0 - t / duration) + 600.0
        tone = math.sin(2.0 * math.pi * freq * t) * 0.7
        val = tone * 0.6 * env
        samples.append(val)
    return samples

def gen_victory():
    duration = 1.2
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) ** 0.8
        # Triad fanfare notes (C5 -> E5 -> G5 -> C6)
        if t < 0.25:
            f = 523.25 # C5
        elif t < 0.5:
            f = 659.25 # E5
        elif t < 0.75:
            f = 783.99 # G5
        else:
            f = 1046.50 # C6
        tone = math.sin(2.0 * math.pi * f * t) * 0.6
        harm = math.sin(2.0 * math.pi * f * 2.0 * t) * 0.25
        val = (tone + harm) * 0.8 * env
        samples.append(val)
    return samples

out_dir = "D:/Drone_Hunter/DroneHunterGodot/assets/audio/sfx"

sfx_map = {
    "pulse": gen_pulse,
    "rapid": gen_rapid,
    "scatter": gen_scatter,
    "missile": gen_missile,
    "barrage": gen_missile,
    "plasma": gen_plasma,
    "rail": gen_rail,
    "beam": gen_beam,
    "tesla": gen_tesla,
    "cluster": gen_missile,
    "emp": gen_emp,
    "hit": gen_hit,
    "shield_hit": gen_shield_hit,
    "pickup": gen_pickup,
    "ui_click": gen_ui_click,
    "victory": gen_victory
}

for name, func in sfx_map.items():
    samples = func()
    save_wav(os.path.join(out_dir, f"{name}.wav"), samples)

print("All audio SFX generated successfully!")
