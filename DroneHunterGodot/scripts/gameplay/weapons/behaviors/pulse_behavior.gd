class_name PulseBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D = null, spawn_root: Node = null) -> void:
	if projectile_scene == null:
		return
		
	var root_node = spawn_root
	if root_node == null and controller != null:
		root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj == null:
		return
		
	root_node.add_child(proj)
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	var shooter = source if source != null else (controller.get_parent() if controller else null)
	proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, shooter, definition.projectile_asset)
