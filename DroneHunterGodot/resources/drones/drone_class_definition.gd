class_name DroneClassDefinition
extends Resource

@export var class_id: String = "striker"
@export var display_name: String = "STRIKER"
@export var title: String = "BALANCED FRONTLINE DRONE"
@export var role: String = "BALANCED / ACCURATE / VERSATILE"
@export_multiline var description: String = "Balanced combat chassis with precision forward weapons and versatile performance."

@export var max_health: float = 100.0
@export var base_armor: float = 0.0
@export var max_shield: float = 60.0
@export var max_energy: float = 100.0

@export var max_speed: float = 520.0
@export var acceleration: float = 6400.0
@export var drag: float = 5.0

@export var default_weapons: Array[String] = ["pulse", "scatter", "missile"]
@export var ability_id: String = "roll"
@export var mount_offsets: Dictionary = {
	"primary": Vector2(88.0, 0.0),
	"left": Vector2(32.0, -56.0),
	"right": Vector2(32.0, 56.0)
}

# Compatibility aliases
@export var id: String:
	get: return class_id
	set(v): class_id = v

@export var name: String:
	get: return display_name
	set(v): display_name = v

@export var base_health: float:
	get: return max_health
	set(v): max_health = v

@export var base_speed: float:
	get: return max_speed
	set(v): max_speed = v
