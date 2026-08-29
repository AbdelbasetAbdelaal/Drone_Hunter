class_name MissileBehavior
extends WeaponBehavior

var homing_script = preload("res://scripts/gameplay/weapons/homing_projectile.gd")
var base_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D = null, spawn_root: Node = null) -> void:
	if base_scene == null:
		return
		
	var root_node = spawn_root
	if root_node == null and controller != null:
		root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var proj = base_scene.instantiate() as Projectile
	if proj == null:
		return
		
	if homing_script:
		proj.set_script(homing_script)
		
	root_node.add_child(proj)
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	var shooter = source if source != null else (controller.get_parent() if controller else null)
	proj.setup(definition.speed, definition.damage, Hit.DamageType.EXPLOSION, shooter, definition.projectile_asset)
