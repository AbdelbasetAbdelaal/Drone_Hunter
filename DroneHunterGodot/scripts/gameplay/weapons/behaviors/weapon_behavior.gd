class_name WeaponBehavior
extends RefCounted

var definition: WeaponDefinition

func _init(def: WeaponDefinition) -> void:
	definition = def

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D, spawn_root: Node) -> void:
	push_error("WeaponBehavior.fire() must be overridden in child class.")
