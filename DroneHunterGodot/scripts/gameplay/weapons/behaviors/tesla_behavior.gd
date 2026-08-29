class_name TeslaBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	if projectile_scene == null or controller == null:
		return
		
	var root_node = controller.get_tree().current_scene if controller.get_tree() and controller.get_tree().current_scene else controller.get_parent()
	if root_node == null:
		return
		
	var proj = projectile_scene.instantiate() as Projectile
	if proj:
		root_node.add_child(proj)
		proj.global_position = muzzle_pos
		proj.global_rotation = muzzle_rot
		proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), definition.projectile_asset)
	
	# Find primary target near aim direction
	var enemies = controller.get_tree().get_nodes_in_group("enemy")
	var primary_target: Node2D = null
	var min_dist: float = 600.0
	
	for e in enemies:
		if is_instance_valid(e) and e is Node2D:
			var d = muzzle_pos.distance_to(e.global_position)
			if d < min_dist:
				min_dist = d
				primary_target = e
				
	if primary_target:
		_draw_lightning(muzzle_pos, primary_target.global_position, root_node)
		var p_recv = primary_target.get_node_or_null("DamageReceiver")
		if p_recv and p_recv.has_method("take_damage"):
			p_recv.take_damage(Hit.new(definition.damage, Hit.DamageType.NORMAL, controller.get_parent(), primary_target.global_position))
			
		# Chain to 2 nearest adjacent enemies from primary target within 320px
		var chained_count: int = 0
		for e in enemies:
			if chained_count >= 2:
				break
			if e != primary_target and is_instance_valid(e) and e is Node2D:
				var chain_dist = primary_target.global_position.distance_to(e.global_position)
				if chain_dist <= 320.0:
					_draw_lightning(primary_target.global_position, e.global_position, root_node)
					var c_recv = e.get_node_or_null("DamageReceiver")
					if c_recv and c_recv.has_method("take_damage"):
						c_recv.take_damage(Hit.new(definition.damage * 0.75, Hit.DamageType.NORMAL, controller.get_parent(), e.global_position))
					chained_count += 1

func _draw_lightning(start: Vector2, end: Vector2, root: Node) -> void:
	var line = Line2D.new()
	line.width = 4.0
	line.default_color = Color(0.4, 0.9, 1.8, 1.0)
	
	# Jagged electric segments
	var count = 5
	line.add_point(start)
	for i in range(1, count):
		var t = float(i) / float(count)
		var p = start.lerp(end, t)
		var offset = Vector2(randf_range(-15, 15), randf_range(-15, 15))
		line.add_point(p + offset)
	line.add_point(end)
	
	root.add_child(line)
	var tween = line.create_tween()
	tween.tween_property(line, "modulate:a", 0.0, 0.18)
	tween.tween_callback(line.queue_free)
