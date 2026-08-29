class_name HomingProjectile
extends Projectile

@export var turn_speed: float = 4.5 # Radians per second
var homing_target: Node2D = null

func _ready() -> void:
	super._ready()
	_acquire_target()

func _acquire_target() -> void:
	if not is_inside_tree():
		return
	var enemies = get_tree().get_nodes_in_group("enemy")
	enemies.append_array(get_tree().get_nodes_in_group("objective_targets"))
	var best_dist: float = 1200.0
	for e in enemies:
		if is_instance_valid(e) and e is Node2D:
			var d = global_position.distance_to(e.global_position)
			if d < best_dist:
				best_dist = d
				homing_target = e

func _physics_process(delta: float) -> void:
	if _has_hit:
		return
		
	if homing_target and is_instance_valid(homing_target):
		var target_angle = (homing_target.global_position - global_position).angle()
		global_rotation = rotate_toward(global_rotation, target_angle, turn_speed * delta)
	else:
		_acquire_target()
		
	super._physics_process(delta)
