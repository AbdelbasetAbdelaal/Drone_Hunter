class_name EnemyShieldElite
extends EnemyCore

func _process_ai(_delta: float) -> void:
	if target and is_instance_valid(target):
		var dir = (target.global_position - global_position).normalized()
		velocity = -dir * base_speed # Move away slowly
		move_and_slide()
