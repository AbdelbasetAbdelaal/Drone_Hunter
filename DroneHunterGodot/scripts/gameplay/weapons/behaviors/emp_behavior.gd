class_name EMPBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null or controller == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	root_node.add_child(proj)
	
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	proj.setup(definition.speed, definition.damage, Hit.DamageType.EMP, controller.get_parent(), definition.projectile_asset)
	
	# EMP stun effect on nearby hostiles in 300px radius
	var enemies = controller.get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if is_instance_valid(e) and e is Node2D:
			var d = muzzle_pos.distance_to(e.global_position)
			if d <= 300.0:
				if e.has_method("apply_emp_stun"):
					e.apply_emp_stun(2.5)
