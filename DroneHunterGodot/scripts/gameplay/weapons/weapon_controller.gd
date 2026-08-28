class_name WeaponController
extends Node2D

@export var primary_projectile_scene: PackedScene = preload("res://scenes/weapons/BulletPulse.tscn")
@export var fire_rate: float = 7.5  # Shots per second (from Pygame WEAPON_PULSE spec)
@export var muzzle_offset: Vector2 = Vector2(75.0, 0.0)

var _cooldown_timer: float = 0.0

func _physics_process(delta: float) -> void:
	if _cooldown_timer > 0.0:
		_cooldown_timer = max(0.0, _cooldown_timer - delta)

func can_fire_primary() -> bool:
	return _cooldown_timer <= 0.0

func try_fire_primary() -> bool:
	if not can_fire_primary():
		return false
	
	if primary_projectile_scene == null:
		return false
	
	var bullet = primary_projectile_scene.instantiate() as Area2D
	if bullet == null:
		return false
	
	var spawn_pos = global_position + muzzle_offset.rotated(global_rotation)
	var spawn_rot = global_rotation
	
	# Add to current scene root / world first
	var root_node = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if root_node:
		root_node.add_child(bullet)
	else:
		get_parent().add_child(bullet)
		
	# Apply global transform after entering tree
	bullet.global_position = spawn_pos
	bullet.global_rotation = spawn_rot
	
	# Only start cooldown after successful projectile creation and insertion
	_cooldown_timer = 1.0 / max(0.1, fire_rate)
	return true
