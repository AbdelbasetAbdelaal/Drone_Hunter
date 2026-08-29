class_name MissionDefinition
extends Resource

@export var mission_id: String = "S1_M1"
@export var sector_index: int = 1
@export var mission_index: int = 1
@export var title: String = "Perimeter Sweep"
@export_multiline var description: String = "Allied recon drones picked up anomalous signals along the perimeter fence."
@export var difficulty: int = 1
@export var objective_type: String = "destroy_all" # "destroy_all", "survive", "complete_encounters"
@export var duration: float = 0.0 # Used when objective_type == "survive"
@export var encounter_sequence: Array = [] # Array of enemy type arrays: [["scout", "scout"], ["scout", "shooter"]]
@export var scrap_reward: int = 150
@export var target_score: int = 1500
@export var sector_background: String = "backgrounds/sectors/sector_1_ref.png"

# Backwards compatibility properties
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
