class_name PlasmaBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	root_node.add_child(proj)
	
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	
	proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), definition.projectile_asset)
	
	# TODO: Implement specific logic for PlasmaBehavior
