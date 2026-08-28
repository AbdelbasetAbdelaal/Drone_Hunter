class_name Hit
extends RefCounted

enum DamageType {
	NORMAL,
	ARMOR_PIERCING,
	SHIELD_PIERCING,
	EMP,
	CONTACT,
	EXPLOSION,
	TRUE_DAMAGE
}

var amount: float
var type: int = DamageType.NORMAL
var source: Node2D
var hit_position: Vector2

func _init(_amount: float, _type: int = DamageType.NORMAL, _source: Node2D = null, _hit_position: Vector2 = Vector2.ZERO) -> void:
	amount = _amount
	type = _type
	source = _source
	hit_position = _hit_position
