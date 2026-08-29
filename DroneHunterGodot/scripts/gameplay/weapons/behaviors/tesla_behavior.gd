class_name TeslaBehavior
extends WeaponBehavior

var projectile_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

const TESLA_RANGE: float = 600.0
const CHAIN_RANGE: float = 320.0
const MAX_CHAINS: int = 2

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D, spawn_root: Node) -> void:
	if spawn_root == null:
		return
		
	if projectile_scene:
		var proj = projectile_scene.instantiate() as Projectile
		if proj:
			spawn_root.add_child(proj)
			proj.global_position = muzzle_pos
			proj.global_rotation = muzzle_rot
			proj.setup(definition.speed, definition.damage, Hit.DamageType.NORMAL, source, definition.projectile_asset)
	
	var enemies: Array = []
	if spawn_root.is_inside_tree():
		enemies = spawn_root.get_tree().get_nodes_in_group("enemy")
		
	var aim_dir = Vector2.RIGHT.rotated(muzzle_rot)
	var primary_target: Node2D = null
	var best_score: float = -999999.0
	
	# Select best primary target aligned with aim direction within TESLA_RANGE
	for e in enemies:
		if is_instance_valid(e) and e is Node2D and not e.is_queued_for_deletion():
			var to_enemy = e.global_position - muzzle_pos
			var dist = to_enemy.length()
			if dist <= TESLA_RANGE and dist > 5.0:
				var dir_to_enemy = to_enemy.normalized()
				var dot = aim_dir.dot(dir_to_enemy)
				var score = (dot * 400.0) - dist
				if score > best_score:
					best_score = score
					primary_target = e
					
	if primary_target == null:
		return
		
	var hit_targets: Array[Node2D] = [primary_target]
	_draw_lightning(muzzle_pos, primary_target.global_position, spawn_root)
	
	var p_recv = primary_target.get_node_or_null("DamageReceiver")
	if p_recv and p_recv.has_method("take_damage"):
		p_recv.take_damage(Hit.new(definition.damage, Hit.DamageType.NORMAL, source, primary_target.global_position))
		
	# Select nearest valid chained targets from primary target
	var chained_count: int = 0
	var candidate_enemies = enemies.duplicate()
	candidate_enemies.sort_custom(func(a, b):
		if not is_instance_valid(a) or not is_instance_valid(b): return false
		var d_a = primary_target.global_position.distance_squared_to(a.global_position)
		var d_b = primary_target.global_position.distance_squared_to(b.global_position)
		return d_a < d_b
	)
	
	for e in candidate_enemies:
		if chained_count >= MAX_CHAINS:
			break
		if is_instance_valid(e) and e is Node2D and not e.is_queued_for_deletion():
			if not (e in hit_targets):
				var chain_dist = primary_target.global_position.distance_to(e.global_position)
				if chain_dist <= CHAIN_RANGE:
					hit_targets.append(e)
					_draw_lightning(primary_target.global_position, e.global_position, spawn_root)
					var c_recv = e.get_node_or_null("DamageReceiver")
					if c_recv and c_recv.has_method("take_damage"):
						c_recv.take_damage(Hit.new(definition.damage * 0.75, Hit.DamageType.NORMAL, source, e.global_position))
					chained_count += 1

func _draw_lightning(start: Vector2, end: Vector2, root: Node) -> void:
	if not root:
		return
	var line = Line2D.new()
	line.width = 4.0
	line.default_color = Color(0.4, 0.9, 1.8, 1.0)
	
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
