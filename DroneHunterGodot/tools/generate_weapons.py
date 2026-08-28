import os

weapons = [
    {
        "weapon_id": "pulse",
        "display_name": "Pulse Laser",
        "slot": 1,
        "cooldown": 0.18,
        "energy_cost": 0.0,
        "damage": 12.0,
        "speed": 650.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "projectiles/bullet_pulse.png",
        "behavior_type": "linear_bolt",
        "description": "Accurate high-velocity coherent energy bolt."
    },
    {
        "weapon_id": "scatter",
        "display_name": "Spread Cannon",
        "slot": 2,
        "cooldown": 0.75,
        "energy_cost": 0.0,
        "damage": 10.0,
        "speed": 500.0,
        "projectiles_per_shot": 5,
        "spread_deg": 22.0,
        "projectile_asset": "projectiles/bullet_scatter.png",
        "behavior_type": "shrapnel_burst",
        "description": "Twin-emitter multi-shrapnel conical blast for close encounters."
    },
    {
        "weapon_id": "missile",
        "display_name": "Heavy Missile",
        "slot": 3,
        "cooldown": 2.5,
        "energy_cost": 0.0,
        "damage": 65.0,
        "speed": 260.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "projectiles/missile.png",
        "behavior_type": "guided_homing",
        "description": "Guided ordnance tracking targets with massive thermal payload."
    },
    {
        "weapon_id": "rapid",
        "display_name": "Rapid Autocannon",
        "slot": 2,
        "cooldown": 0.08,
        "energy_cost": 0.0,
        "damage": 8.0,
        "speed": 980.0,
        "projectiles_per_shot": 1,
        "spread_deg": 3.0,
        "projectile_asset": "projectiles/bullet_pulse.png",
        "behavior_type": "cyclic_kinetic",
        "description": "High-cyclic kinetic rounds alternating from dual nose muzzles."
    },
    {
        "weapon_id": "plasma",
        "display_name": "Heavy Plasma Cannon",
        "slot": 2,
        "cooldown": 0.85,
        "energy_cost": 0.0,
        "damage": 90.0,
        "speed": 460.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/plasma/projectile.png",
        "behavior_type": "concentrated_plasma",
        "description": "Dense superheated plasma orb with massive splash disruption."
    },
    {
        "weapon_id": "rail",
        "display_name": "Precision Railgun",
        "slot": 1,
        "cooldown": 1.10,
        "energy_cost": 0.0,
        "damage": 115.0,
        "speed": 1800.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/rail/projectile.png",
        "behavior_type": "supersonic_piercing",
        "description": "Hypersonic electromagnetic slug penetrating all armor plating."
    },
    {
        "weapon_id": "barrage",
        "display_name": "Missile Barrage",
        "slot": 3,
        "cooldown": 2.2,
        "energy_cost": 0.0,
        "damage": 38.0,
        "speed": 620.0,
        "projectiles_per_shot": 4,
        "spread_deg": 28.0,
        "projectile_asset": "weapons/barrage/projectile.png",
        "behavior_type": "salvo_homing",
        "description": "Four-missile salvo launched simultaneously from wing pods."
    },
    {
        "weapon_id": "beam",
        "display_name": "Plasma Cutting Beam",
        "slot": 2,
        "cooldown": 0.08,
        "energy_cost": 0.0,
        "damage": 26.0,
        "speed": 1500.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/beam/projectile.png",
        "behavior_type": "continuous_beam",
        "description": "Continuous ultra-dense plasma laser searing through chassis and vaporizing incoming ordnance."
    },
    {
        "weapon_id": "tesla",
        "display_name": "Tesla Arc",
        "slot": 2,
        "cooldown": 0.40,
        "energy_cost": 0.0,
        "damage": 44.0,
        "speed": 1100.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/tesla/projectile.png",
        "behavior_type": "chaining_lightning",
        "description": "High-voltage electrical discharge jumping between targets."
    },
    {
        "weapon_id": "cluster",
        "display_name": "Cluster Torpedo",
        "slot": 4,
        "cooldown": 2.0,
        "energy_cost": 0.0,
        "damage": 85.0,
        "speed": 520.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/cluster/projectile.png",
        "behavior_type": "cluster_submunition",
        "description": "Heavy ballistic torpedo splitting into 6 explosive sub-munitions."
    },
    {
        "weapon_id": "emp",
        "display_name": "EMP Shockwave Pulse",
        "slot": 1,
        "cooldown": 0.50,
        "energy_cost": 0.0,
        "damage": 30.0,
        "speed": 1200.0,
        "projectiles_per_shot": 1,
        "spread_deg": 0.0,
        "projectile_asset": "weapons/emp/projectile.png",
        "behavior_type": "emp_expanding_pulse",
        "description": "Electromagnetic shockwave disabling enemy subsystems."
    }
]

os.makedirs("D:/Drone_Hunter/DroneHunterGodot/resources/weapons", exist_ok=True)

for w in weapons:
    tres = f'''[gd_resource type="Resource" script_class="WeaponDefinition" load_steps=2 format=3]

[ext_resource type="Script" path="res://resources/weapons/weapon_definition.gd" id="1_script"]

[resource]
script = ExtResource("1_script")
weapon_id = "{w['weapon_id']}"
display_name = "{w['display_name']}"
slot = {w['slot']}
cooldown = {w['cooldown']}
energy_cost = {w['energy_cost']}
damage = {w['damage']}
speed = {w['speed']}
projectiles_per_shot = {w['projectiles_per_shot']}
spread_deg = {w['spread_deg']}
projectile_asset = "{w['projectile_asset']}"
behavior_type = "{w['behavior_type']}"
description = "{w['description']}"
'''
    path = f"D:/Drone_Hunter/DroneHunterGodot/resources/weapons/{w['weapon_id']}.tres"
    with open(path, "w") as f:
        f.write(tres)
    print("Created", path)
