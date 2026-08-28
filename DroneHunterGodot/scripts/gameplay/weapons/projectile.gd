class_name Projectile
extends Area2D

@export var speed: float = 950.0
@export var damage: float = 25.0
@export var max_range: float = 1400.0

var _traveled_distance: float = 0.0

func _ready() -> void:
	top_level = true

func _physics_process(delta: float) -> void:
	var move_amount: float = speed * delta
	global_position += Vector2.RIGHT.rotated(global_rotation) * move_amount
	_traveled_distance += move_amount
	
	if _traveled_distance >= max_range:
		queue_free()
