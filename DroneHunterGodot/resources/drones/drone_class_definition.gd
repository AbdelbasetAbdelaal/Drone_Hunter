class_name DroneClassDefinition
extends Resource

@export var id: String = "striker"
@export var name: String = "Striker"
@export var role: String = "Balanced Interceptor"
@export var description: String = ""
@export var base_health: float = 100.0
@export var base_shields: float = 60.0
@export var base_energy: float = 100.0
@export var base_speed: float = 400.0
@export var agility: float = 1.0
@export var default_weapons: Array[String] = ["pulse", "scatter", "missile"]
@export var ability_id: String = "roll"
@export var sprite_texture: Texture2D = null
