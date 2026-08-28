class_name Projectile
extends Area2D

@export var speed: float = 950.0
@export var damage: float = 25.0
@export var max_range: float = 1400.0

var _traveled_distance: float = 0.0

func _ready() -> void:
	top_level = true
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(delta: float) -> void:
	var move_amount: float = speed * delta
	global_position += Vector2.RIGHT.rotated(global_rotation) * move_amount
	_traveled_distance += move_amount
	
	if _traveled_distance >= max_range:
		queue_free()

func _on_body_entered(body: Node2D) -> void:
	_handle_hit(body)

func _on_area_entered(area: Area2D) -> void:
	_handle_hit(area)

func _handle_hit(target: Node2D) -> void:
	if target == self or target is Player or target.is_in_group("player"):
		return
	
	if target.has_method("take_damage"):
		target.take_damage(damage)
	
	# Cleanly remove projectile upon hitting either an enemy or arena boundary/environment body
	queue_free()
