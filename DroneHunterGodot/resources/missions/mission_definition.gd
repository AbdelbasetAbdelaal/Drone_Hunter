class_name MissionDefinition
extends Resource

@export var mission_id: String = "S1_M1"
@export var sector_index: int = 1
@export var mission_index: int = 1
@export var title: String = "Desert Reconnaissance"
@export_multiline var description: String = "Scout the sandstone canyon perimeter and eliminate hostile vanguard scouts."
@export var sector_background: String = "backgrounds/sectors/sector_2_ref.png"
@export var total_waves: int = 3
@export var is_boss_mission: bool = false
@export var scrap_reward: int = 250
@export var target_score: int = 2500
