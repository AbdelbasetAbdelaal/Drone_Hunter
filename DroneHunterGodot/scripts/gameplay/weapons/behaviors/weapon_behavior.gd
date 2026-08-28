class_name WeaponBehavior
extends RefCounted

var definition: WeaponDefinition
var controller: Node2D # The WeaponController invoking this behavior

func _init(def: WeaponDefinition, ctrl: Node2D) -> void:
	definition = def
	controller = ctrl

func fire(muzzle_pos: Vector2, muzzle_rot: float) -> void:
	push_error("WeaponBehavior.fire() must be overridden in child class.")
