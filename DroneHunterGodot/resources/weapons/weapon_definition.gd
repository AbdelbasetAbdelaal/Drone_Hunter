class_name WeaponDefinition
extends Resource

@export var weapon_id: String = "pulse"
@export var display_name: String = "Pulse Cannon"
@export var slot: int = 1
@export var cooldown: float = 0.18
@export var energy_cost: float = 5.0
@export var damage: float = 25.0
@export var speed: float = 950.0
@export var projectiles_per_shot: int = 1
@export var spread_deg: float = 0.0
@export var projectile_asset: String = "projectiles/bullet_pulse.png"
@export var behavior_type: String = "pulse"
@export var color: Color = Color.WHITE
@export var description: String = ""

# Backwards compatibility properties
@export var id: String:
	get: return weapon_id
	set(v): weapon_id = v

@export var name: String:
	get: return display_name
	set(v): display_name = v

@export var base_damage: float:
	get: return damage
	set(v): damage = v

@export var projectile_speed: float:
	get: return speed
	set(v): speed = v

@export var projectile_count: int:
	get: return projectiles_per_shot
	set(v): projectiles_per_shot = v

@export var spread: float:
	get: return spread_deg
	set(v): spread_deg = v
