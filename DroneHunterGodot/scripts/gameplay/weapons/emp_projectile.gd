class_name EMPProjectile
extends Projectile

@export var emp_radius: float = 380.0
var shockwave_tex = preload("res://assets/vfx/shockwave.png")

func _handle_hit(target: Node2D) -> void:
	if _has_hit:
		return
	if not is_instance_valid(target) or target == _source:
		return
		
	_has_hit = true
	_detonate_emp()
	_safe_destroy()

func _detonate_emp() -> void:
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if root and shockwave_tex:
		var ring = Sprite2D.new()
		ring.texture = shockwave_tex
		ring.global_position = global_position
		ring.scale = Vector2(0.1, 0.1)
		ring.modulate = Color(0.2, 0.9, 1.8, 1.0)
		root.add_child(ring)
		var tween = ring.create_tween().set_parallel(true)
		tween.tween_property(ring, "scale", Vector2(3.5, 3.5), 0.4).set_ease(Tween.EASE_OUT)
		tween.tween_property(ring, "modulate:a", 0.0, 0.4)
		tween.chain().tween_callback(ring.queue_free)
		
	# Apply EMP damage, shield wipe, and 3.0s stun to all enemies in radius
	var valid_source: Object = _source if is_instance_valid(_source) else null
	var enemies = get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if is_instance_valid(e) and e is Node2D:
			var d = global_position.distance_to(e.global_position)
			if d <= emp_radius:
				var receiver = e.get_node_or_null("DamageReceiver")
				if receiver and receiver.has_method("take_damage"):
					receiver.take_damage(Hit.new(damage, Hit.DamageType.EMP, valid_source, e.global_position))
				if e.has_method("apply_emp_stun"):
					e.apply_emp_stun(3.0)
