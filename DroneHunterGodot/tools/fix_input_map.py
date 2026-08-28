import re

path = "D:/Drone_Hunter/DroneHunterGodot/project.godot"
with open(path, "r") as f:
    text = f.read()

# Map keycode to physical_keycode for ASCII letters, numbers, and space
def replacer(match):
    full = match.group(0)
    kc_match = re.search(r'"keycode":(\d+)', full)
    if kc_match:
        kc = int(kc_match.group(1))
        # Replace physical_keycode:0 with physical_keycode:kc
        full = re.sub(r'"physical_keycode":0', f'"physical_keycode":{kc}', full)
    return full

text = re.sub(r'Object\(InputEventKey,[^\)]+\)', replacer, text)

with open(path, "w") as f:
    f.write(text)

print("Updated project.godot input mapping with physical keycodes.")
