class_name PiercingProjectile
extends Projectile

var hit_targets: Array[Node2D] = []

func _handle_hit(target: Node2D) -> void:
	if not is_instance_valid(target) or target == _source:
		return
	if target in hit_targets:
		return
		
	hit_targets.append(target)
	var valid_source: Object = _source if is_instance_valid(_source) else null
	
	# Penetrate and damage target without destroying projectile
	var receiver = target.get_node_or_null("DamageReceiver")
	if receiver != null and receiver.has_method("take_damage"):
		receiver.take_damage(Hit.new(damage, Hit.DamageType.ARMOR_PIERCING, valid_source, global_position))
	elif target.has_method("take_damage"):
		target.take_damage(damage)
		
	# Piercing continues through enemies up to max range
