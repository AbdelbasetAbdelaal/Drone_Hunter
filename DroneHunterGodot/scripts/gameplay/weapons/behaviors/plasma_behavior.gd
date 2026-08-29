class_name PlasmaBehavior
extends WeaponBehavior

var plasma_script = preload("res://scripts/gameplay/weapons/plasma_projectile.gd")
var base_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D, spawn_root: Node) -> void:
	if base_scene == null or spawn_root == null:
		return
		
	var proj = base_scene.instantiate() as Projectile
	if proj == null:
		return
		
	if plasma_script:
		proj.set_script(plasma_script)
		
	spawn_root.add_child(proj)
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	proj.setup(definition.speed, definition.damage, Hit.DamageType.EXPLOSION, source, definition.projectile_asset)
