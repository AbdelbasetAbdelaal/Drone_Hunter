class_name WeaponBehavior
extends RefCounted

var definition: WeaponDefinition
var controller: Node2D

func _init(def: WeaponDefinition, ctrl: Node2D = null) -> void:
	definition = def
	controller = ctrl

func fire(muzzle_pos: Vector2, muzzle_rot: float, source: Node2D = null, spawn_root: Node = null) -> void:
	push_error("WeaponBehavior.fire() must be overridden in child class.")
