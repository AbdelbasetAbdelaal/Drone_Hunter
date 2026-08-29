class_name PlasmaBehavior
extends WeaponBehavior

var plasma_script = preload("res://scripts/gameplay/weapons/plasma_projectile.gd")
var base_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if base_scene == null or controller == null:
		return
		
	var proj = base_scene.instantiate() as Projectile
	if proj == null:
		return
		
	if plasma_script:
		proj.set_script(plasma_script)
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	root_node.add_child(proj)
	
	proj.global_position = muzzle_pos
	proj.global_rotation = muzzle_rot
	proj.setup(definition.speed, definition.damage, Hit.DamageType.EXPLOSION, controller.get_parent(), definition.projectile_asset)
