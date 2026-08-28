import os

missions = [
    # Sector 1: Desert Canyon
    ("S1_M1", 1, 1, "Canyon Vanguard", "Eliminate advancing scout patrols in the sandstone canyon.", "backgrounds/sectors/sector_2_ref.png", 3, False, 200, 2000),
    ("S1_M2", 1, 2, "Mining Outpost Raid", "Destroy hostile shooter units guarding the desert extraction facility.", "backgrounds/sectors/sector_2_ref.png", 3, False, 300, 3000),
    ("S1_M3", 1, 3, "Desert Titan Showdown", "Neutralize the Titan Carrier command fortress in the deep desert.", "backgrounds/sectors/sector_2_ref.png", 4, True, 500, 5000),
    
    # Sector 2: Industrial Cyber Factory
    ("S2_M1", 2, 1, "Factory Perimeter Breach", "Infiltrate the automated manufacturing complex outer ring.", "backgrounds/sectors/sector_1_ref.png", 3, False, 350, 3500),
    ("S2_M2", 2, 2, "Assembly Line Defense", "Repel armored enemy waves attempting to secure prototype drones.", "backgrounds/sectors/sector_1_ref.png", 4, False, 450, 4500),
    ("S2_M3", 2, 3, "Reactor Overload", "Assault the fortified industrial core and destroy its defense commander.", "backgrounds/sectors/sector_1_ref.png", 4, True, 750, 6500),
    
    # Sector 3: Tropical Forest
    ("S3_M1", 3, 1, "Rainforest Patrol", "Engage agile enemy formations navigating the canopy.", "backgrounds/sectors/sector_3_ref.png", 3, False, 500, 4500),
    ("S3_M2", 3, 2, "River Basin Ambush", "Survive heavy hostile swarms deployed along the river gorge.", "backgrounds/sectors/sector_3_ref.png", 4, False, 650, 6000),
    ("S3_M3", 3, 3, "Canopy Dreadnought", "Destroy the jungle sector boss commanding the coastal batteries.", "backgrounds/sectors/sector_3_ref.png", 4, True, 1000, 8000),
    
    # Sector 4: Orbital Space
    ("S4_M1", 4, 1, "Asteroid Belt Escort", "Clear orbital defense grids and floating missile batteries.", "backgrounds/sectors/sector_4_ref.png", 4, False, 750, 7000),
    ("S4_M2", 4, 2, "Station Breach", "Penetrate the orbital station heavily guarded by shield elites.", "backgrounds/sectors/sector_4_ref.png", 4, False, 900, 8500),
    ("S4_M3", 4, 3, "Orbital Flagship", "Engage the flagship carrier in low orbit before jump sequence.", "backgrounds/sectors/sector_4_ref.png", 5, True, 1500, 10000),
    
    # Sector 5: Cyber Core
    ("S5_M1", 5, 1, "Firewall Infiltration", "Breach the cyber defense core and eliminate rogue AI subroutines.", "backgrounds/sectors/sector_5_ref.png", 4, False, 1000, 9000),
    ("S5_M2", 5, 2, "Neural Network Defense", "Survive overwhelming elite strike forces inside the mainframe.", "backgrounds/sectors/sector_5_ref.png", 4, False, 1400, 12000),
    ("S5_M3", 5, 3, "Supreme AI Nexus", "Final campaign battle: Annihilate the core Nexus Titan to liberate all sectors.", "backgrounds/sectors/sector_5_ref.png", 5, True, 2500, 18000),
]

os.makedirs("D:/Drone_Hunter/DroneHunterGodot/resources/missions", exist_ok=True)

for m_id, s_idx, m_idx, title, desc, bg, waves, is_boss, scrap, score in missions:
    is_boss_str = "true" if is_boss else "false"
    tres = f'''[gd_resource type="Resource" script_class="MissionDefinition" load_steps=2 format=3]

[ext_resource type="Script" path="res://resources/missions/mission_definition.gd" id="1_script"]

[resource]
script = ExtResource("1_script")
mission_id = "{m_id}"
sector_index = {s_idx}
mission_index = {m_idx}
title = "{title}"
description = "{desc}"
sector_background = "{bg}"
total_waves = {waves}
is_boss_mission = {is_boss_str}
scrap_reward = {scrap}
target_score = {score}
'''
    path = f'D:/Drone_Hunter/DroneHunterGodot/resources/missions/{m_id}.tres'
    with open(path, 'w') as f:
        f.write(tres)
    print("Created", path)
