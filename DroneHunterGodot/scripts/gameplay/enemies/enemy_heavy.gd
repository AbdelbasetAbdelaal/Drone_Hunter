class_name EnemyHeavy
extends EnemyCore

func _process_ai(_delta: float) -> void:
	if target and is_instance_valid(target):
		look_at(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		velocity = dir * base_speed
		move_and_slide()
