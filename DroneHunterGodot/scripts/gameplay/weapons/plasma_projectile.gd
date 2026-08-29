class_name PlasmaProjectile
extends Projectile

@export var splash_radius: float = 140.0

func _handle_hit(target: Node2D) -> void:
	if _has_hit:
		return
	if not is_instance_valid(target) or target == _source:
		return
		
	_has_hit = true
	var valid_source: Object = _source if is_instance_valid(_source) else null
	
	# Primary Target Hit
	var receiver = target.get_node_or_null("DamageReceiver")
	if receiver != null and receiver.has_method("take_damage"):
		receiver.take_damage(Hit.new(damage, damage_type, valid_source, global_position))
	elif target.has_method("take_damage"):
		target.take_damage(damage)
		
	# Area Splash Damage to nearby hostiles
	var enemies = get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if e != target and is_instance_valid(e) and e is Node2D:
			var d = global_position.distance_to(e.global_position)
			if d <= splash_radius:
				var splash_recv = e.get_node_or_null("DamageReceiver")
				if splash_recv and splash_recv.has_method("take_damage"):
					var splash_dmg = damage * (1.0 - (d / splash_radius) * 0.5)
					splash_recv.take_damage(Hit.new(splash_dmg, Hit.DamageType.EXPLOSION, valid_source, e.global_position))
					
	_safe_destroy()
