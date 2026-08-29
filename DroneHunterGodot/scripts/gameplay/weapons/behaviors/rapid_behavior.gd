class_name RapidBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")
var _mount_side: int = 0

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null or controller == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	root_node.add_child(proj)
	
	# Alternate left/right wing mounts
	var offset_dist = -14.0 if _mount_side == 0 else 14.0
	_mount_side = 1 - _mount_side
	var lateral_offset = Vector2.DOWN.rotated(muzzle_rot) * offset_dist
	
	proj.global_position = muzzle_pos + lateral_offset
	# Slight spread angle
	var spread_rad = deg_to_rad(randf_range(-definition.spread * 0.5, definition.spread * 0.5))
	proj.global_rotation = muzzle_rot + spread_rad
	proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), definition.projectile_asset)
