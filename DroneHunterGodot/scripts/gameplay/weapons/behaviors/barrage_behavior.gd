class_name BarrageBehavior
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
		
	var count = max(1, definition.projectile_count)
	var spread_deg = definition.spread
	var step = spread_deg / float(count - 1) if count > 1 else 0.0
	var half_spread = spread_deg * 0.5
	var shooter = source if source != null else (controller.get_parent() if controller else null)
	
	for i in range(count):
		var proj = base_scene.instantiate() as Projectile
		if proj == null:
			continue
		if homing_script:
			proj.set_script(homing_script)
		root_node.add_child(proj)
		
		var offset_angle_deg = -half_spread + (step * i)
		var angle_rad = muzzle_rot + deg_to_rad(offset_angle_deg)
		var lateral_offset = Vector2.DOWN.rotated(muzzle_rot) * ((i - 1.5) * 10.0)
		
		proj.global_position = muzzle_pos + lateral_offset
		proj.global_rotation = angle_rad
		proj.setup(definition.speed, definition.damage, Hit.DamageType.EXPLOSION, shooter, definition.projectile_asset)
