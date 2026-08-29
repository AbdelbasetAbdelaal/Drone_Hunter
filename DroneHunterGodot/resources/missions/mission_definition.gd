class_name MissionDefinition
extends Resource

@export var mission_id: String = "S1_M1"
@export var sector_index: int = 1
@export var mission_index: int = 1
@export var title: String = "Perimeter Sweep"
@export_multiline var description: String = "Allied recon drones picked up anomalous signals along the outermost perimeter fence."
@export_multiline var lore: String = ""
@export var difficulty: int = 1
@export var primary_objective: String = "destroy_all" # "destroy_all", "survive", "complete_encounters"
@export var objective_target: String = "radar_command" # "radar_command", "missile_complex", "power_reactor", "communication_hub", "cyber_defense_core", "weapons_factory"
@export var objective_target_position: Vector2 = Vector2(1920, 680)
@export var defense_level: int = 1
@export var duration: float = 0.0 # Used when primary_objective == "survive"
@export var encounter_sequence: Array = [] # Array of enemy type arrays
@export var side_objectives: Array = [] # Array of dicts e.g. [{"type": "precision_strikes", "value": 10}]
@export var scrap_reward: int = 150
@export var target_score: int = 1500
@export var sector_background: String = "backgrounds/sectors/sector_1_ref.png"

# Backwards compatibility properties
@export var objective_type: String:
	get: return primary_objective
	set(v): primary_objective = v

@export var id: String:
	get: return mission_id
	set(v): mission_id = v

@export var name: String:
	get: return title
	set(v): title = v

@export var sector_id: int:
	get: return sector_index
	set(v): sector_index = v

@export var mission_number: int:
	get: return mission_index
	set(v): mission_index = v

@export var total_waves: int:
	get: return max(1, encounter_sequence.size())
	set(v): pass

@export var is_boss_mission: bool:
	get: return false
	set(v): pass
