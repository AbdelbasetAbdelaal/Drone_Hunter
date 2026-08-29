class_name ClusterBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null or controller == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	# Main cluster torpedo
	var main_proj = projectile_scene.instantiate() as Projectile
	if main_proj:
		root_node.add_child(main_proj)
		main_proj.global_position = muzzle_pos
		main_proj.global_rotation = muzzle_rot
		main_proj.setup(definition.speed, definition.damage, Hit.DamageType.EXPLOSION, controller.get_parent(), definition.projectile_asset)
		
	# Submunition bomblet spread
	for offset_deg in [-18.0, -9.0, 9.0, 18.0]:
		var sub_proj = projectile_scene.instantiate() as Projectile
		if sub_proj:
			root_node.add_child(sub_proj)
			sub_proj.global_position = muzzle_pos
			sub_proj.global_rotation = muzzle_rot + deg_to_rad(offset_deg)
			sub_proj.setup(definition.speed * 0.85, definition.damage * 0.35, Hit.DamageType.EXPLOSION, controller.get_parent(), definition.projectile_asset)
