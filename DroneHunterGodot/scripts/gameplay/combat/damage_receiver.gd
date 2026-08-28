class_name DamageReceiver
extends Node

@export var health: Health

signal hit_received(hit: Hit)

func take_damage(hit: Hit) -> void:
	if health == null or health.is_dead:
		return
		
	hit_received.emit(hit)
	
	# Simple armor mitigation: armor value is a flat reduction, min 1 damage, except armor_piercing
	var effective_damage = hit.amount
	
	if hit.type != Hit.DamageType.ARMOR_PIERCING and hit.type != Hit.DamageType.TRUE_DAMAGE:
		if health.base_armor > 0.0:
			# Armor acts as a flat damage reducer or percentage, using flat for now 
			# In Pygame reference HEAVY_ARMOR = 0.20 (20% reduction)
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
