class_name TeslaBehavior
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
	proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), definition.projectile_asset)
	
	# Chain lightning damage to nearby enemies within 320px
	var enemies = controller.get_tree().get_nodes_in_group("enemy")
	var chained_count: int = 0
	for e in enemies:
		if chained_count >= 2:
			break
		if is_instance_valid(e) and e is Node2D:
			var d = muzzle_pos.distance_to(e.global_position)
			if d <= 320.0 and d > 30.0:
				var receiver = e.get_node_or_null("DamageReceiver")
				if receiver and receiver.has_method("take_damage"):
					receiver.take_damage(Hit.new(definition.damage * 0.75, Hit.DamageType.NORMAL, controller.get_parent(), e.global_position))
					chained_count += 1
