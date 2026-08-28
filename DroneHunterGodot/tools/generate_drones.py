import os

drones = {
    'striker': {
        'id': 'striker',
        'name': 'STRIKER',
        'title': 'BALANCED FRONTLINE DRONE',
        'role': 'BALANCED / ACCURATE / VERSATILE',
        'desc': 'Balanced combat chassis with precision forward weapons and versatile performance.',
        'hp': 100.0,
        'armor': 0.0,
        'shield': 60.0,
        'energy': 100.0,
        'speed': 520.0,
        'accel': 6400.0,
        'drag': 5.0,
        'weapons': ['pulse', 'scatter', 'missile'],
        'ability': 'roll'
    },
    'interceptor': {
        'id': 'interceptor',
        'name': 'INTERCEPTOR',
        'title': 'FAST ATTACK / INTERCEPTION',
        'role': 'FAST / AGILE / HIGH DPS / LOW SURVIVABILITY',
        'desc': 'High-mobility strike platform with extreme acceleration and rapid-fire armament.',
        'hp': 80.0,
        'armor': 0.0,
        'shield': 40.0,
        'energy': 120.0,
        'speed': 600.0,
        'accel': 7200.0,
        'drag': 4.5,
        'weapons': ['pulse', 'rapid', 'missile'],
        'ability': 'roll'
    },
    'assault': {
        'id': 'assault',
        'name': 'ASSAULT',
        'title': 'HEAVY ATTACK DREADNOUGHT',
        'role': 'HEAVY / POWERFUL / HIGH DURABILITY',
        'desc': 'Heavily armored juggernaut packing devastating heavy plasma ordnance and high durability.',
        'hp': 150.0,
        'armor': 0.20,
        'shield': 80.0,
        'energy': 80.0,
        'speed': 380.0,
        'accel': 4200.0,
        'drag': 6.0,
        'weapons': ['pulse', 'plasma', 'missile'],
        'ability': 'overdrive'
    },
    'arc': {
        'id': 'arc',
        'name': 'ARC',
        'title': 'ENERGY / AREA CONTROL',
        'role': 'ENERGY / CONTROL / AREA DAMAGE',
        'desc': 'Specialized electromagnetic disruption platform with high-voltage chain arcs and EMP focus.',
        'hp': 95.0,
        'armor': 0.05,
        'shield': 100.0,
        'energy': 160.0,
        'speed': 480.0,
        'accel': 5800.0,
        'drag': 5.0,
        'weapons': ['emp', 'tesla', 'beam'],
        'ability': 'emp'
    },
    'command': {
        'id': 'command',
        'name': 'COMMAND',
        'title': 'ADVANCED ENDGAME PLATFORM',
        'role': 'ENDGAME / LONG-RANGE / MULTI-POD',
        'desc': 'Endgame quad-thruster platform equipped with multi-pod missile barrages and precision rail slugs.',
        'hp': 130.0,
        'armor': 0.15,
        'shield': 90.0,
        'energy': 140.0,
        'speed': 520.0,
        'accel': 5200.0,
        'drag': 5.0,
        'weapons': ['rail', 'beam', 'barrage', 'cluster'],
        'ability': 'cloak'
    }
}

for k, v in drones.items():
    weaps_str = ', '.join([f'"{w}"' for w in v['weapons']])
    tres = f'''[gd_resource type="Resource" script_class="DroneClassDefinition" load_steps=2 format=3]

[ext_resource type="Script" path="res://resources/drones/drone_class_definition.gd" id="1_script"]

[resource]
script = ExtResource("1_script")
class_id = "{v['id']}"
display_name = "{v['name']}"
title = "{v['title']}"
role = "{v['role']}"
description = "{v['desc']}"
max_health = {v['hp']}
base_armor = {v['armor']}
max_shield = {v['shield']}
max_energy = {v['energy']}
max_speed = {v['speed']}
acceleration = {v['accel']}
drag = {v['drag']}
default_weapons = [{weaps_str}]
ability_id = "{v['ability']}"
'''
    path = f'D:/Drone_Hunter/DroneHunterGodot/resources/drones/{k}.tres'
    with open(path, 'w') as f:
        f.write(tres)
    print('Created', path)
