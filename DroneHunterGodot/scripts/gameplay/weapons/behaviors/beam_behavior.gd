class_name BeamBehavior
extends WeaponBehavior

var beam_script = preload("res://scripts/gameplay/weapons/continuous_beam_projectile.gd")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if controller == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var beam = Node2D.new()
	if beam_script:
		beam.set_script(beam_script)
		
	root_node.add_child(beam)
	beam.global_position = muzzle_pos
	beam.global_rotation = muzzle_rot
	if beam.has_method("setup"):
		beam.setup(controller.get_parent(), definition.damage)
