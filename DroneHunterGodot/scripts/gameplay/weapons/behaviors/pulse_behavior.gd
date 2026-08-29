class_name PulseBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D, spawn_root: Node) -> void:
	if projectile_scene == null or spawn_root == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj == null:
		return
		
	spawn_root.add_child(proj)
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, source, definition.projectile_asset)
