class_name ScatterBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null or controller == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var pellet_count = max(1, definition.projectile_count)
	var spread_deg = definition.spread
	var half_spread = spread_deg * 0.5
	var step = spread_deg / float(pellet_count - 1) if pellet_count > 1 else 0.0
	
	for i in range(pellet_count):
		var proj = projectile_scene.instantiate() as Projectile
		if proj == null:
			continue
		root_node.add_child(proj)
		
		var offset_angle_deg = -half_spread + (step * i)
		var angle_rad = muzzle_rot + deg_to_rad(offset_angle_deg)
		
		proj.global_position = muzzle_pos
		proj.global_rotation = angle_rad
		proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), definition.projectile_asset)
