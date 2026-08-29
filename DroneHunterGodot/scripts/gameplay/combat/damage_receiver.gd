class_name DamageReceiver
extends Node

@export var health: Health

signal hit_received(hit: Hit)

var damage_number_scene: PackedScene = preload("res://scenes/vfx/DamageNumber.tscn")

func take_damage(hit: Hit) -> void:
	if health == null or health.is_dead:
		return
		
	hit_received.emit(hit)
	
	var is_shield_hit = health.current_shield > 0.0
	var effective_damage = hit.amount
	
	if hit.type != Hit.DamageType.ARMOR_PIERCING and hit.type != Hit.DamageType.TRUE_DAMAGE:
		if health.base_armor > 0.0:
			effective_damage *= (1.0 - health.base_armor)
			
	# Process Shield
	if health.current_shield > 0.0 and hit.type != Hit.DamageType.SHIELD_PIERCING and hit.type != Hit.DamageType.TRUE_DAMAGE:
		if effective_damage > health.current_shield:
			effective_damage -= health.current_shield
			health.current_shield = 0.0
		else:
			health.current_shield -= effective_damage
			effective_damage = 0.0
			
	if effective_damage > 0.0:
		health.apply_damage(effective_damage)
		
	_trigger_hit_feedback(hit, is_shield_hit)

func _trigger_hit_feedback(hit: Hit, is_shield: bool) -> void:
	var parent_node = get_parent() as Node2D
	if not parent_node or not parent_node.is_inside_tree():
		return
		
	# 1. Sprite Hit Flash
	var sprite = parent_node.get_node_or_null("Sprite2D") as Sprite2D
	if sprite:
		var orig_mod = sprite.modulate
		sprite.modulate = Color(3.0, 3.0, 3.0, 1.0) if not is_shield else Color(0.5, 1.5, 3.0, 1.0)
		var tween = parent_node.create_tween()
		tween.tween_property(sprite, "modulate", orig_mod, 0.08)
		
	# 2. Spawn Floating Damage Number
	if damage_number_scene:
		var root = parent_node.get_tree().current_scene if parent_node.get_tree() else null
		if root:
			var dmg_num = damage_number_scene.instantiate()
			root.add_child(dmg_num)
			var offset = Vector2(randf_range(-12, 12), randf_range(-25, -15))
			dmg_num.global_position = parent_node.global_position + offset
			if dmg_num.has_method("setup"):
				dmg_num.setup(hit.amount, is_shield, hit.amount >= 50.0)
			
	# 3. Audio feedback
	var am = parent_node.get_tree().get_first_node_in_group("audio_manager")
	if am and am.has_method("play_hit"):
		am.play_hit(is_shield)
		
	# 4. If Parent is Player, trigger screen shake trauma
	if parent_node.is_in_group("player"):
		var cam = parent_node.get_tree().get_first_node_in_group("camera")
		if cam and cam.has_method("add_trauma"):
			cam.add_trauma(0.35)
