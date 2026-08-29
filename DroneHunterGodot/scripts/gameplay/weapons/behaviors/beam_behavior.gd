class_name BeamBehavior
extends WeaponBehavior

var beam_script = preload("res://scripts/gameplay/weapons/continuous_beam_projectile.gd")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D = null, spawn_root: Node = null) -> void:
	# Persistent beam lifecycle is coordinated through WeaponController.fire_beam()
	# This fire callback acts as fallback or direct invocation
	var root_node = spawn_root
	if root_node == null and controller != null:
		root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var beam = Node2D.new()
	if beam_script:
		beam.set_script(beam_script)
		
	root_node.add_child(beam)
	beam.global_position = muzzle_pos
	beam.global_rotation = muzzle_rot
	var shooter = source if source != null else (controller.get_parent() if controller else null)
	if beam.has_method("setup"):
		beam.setup(shooter, definition.damage)
	if beam.has_method("update_beam"):
		beam.update_beam(muzzle_pos, muzzle_rot, 0.016)
