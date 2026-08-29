class_name BeamBehavior
extends WeaponBehavior

var beam_script = preload("res://scripts/gameplay/weapons/continuous_beam_projectile.gd")

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D, spawn_root: Node) -> void:
	if spawn_root == null:
		return
		
	var beam = ContinuousBeamProjectile.new()
	spawn_root.add_child(beam)
	beam.global_position = muzzle_pos
	beam.global_rotation = muzzle_rot
	beam.setup(source, definition.damage)
	beam.update_beam(muzzle_pos, muzzle_rot, 0.016)
