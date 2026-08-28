class_name WeaponController
extends Node2D

@export var muzzle_offset: Vector2 = Vector2(88.0, 0.0) # Player STRIKER primary mount profile

var weapons: Array[WeaponDefinition] = []
var active_weapon_index: int = 0
var behaviors: Array[WeaponBehavior] = []

var _cooldown_timer: float = 0.0

func _ready() -> void:
	_init_weapons()

func _init_weapons() -> void:
	# Temporarily hardcode Pulse until full resource data setup
	var pulse_def = WeaponDefinition.new()
	pulse_def.weapon_id = "pulse"
	pulse_def.display_name = "Pulse Laser"
	pulse_def.cooldown = 0.18
	pulse_def.damage = 12.0
	pulse_def.speed = 650.0
	weapons.append(pulse_def)
	behaviors.append(PulseBehavior.new(pulse_def, self))

func _physics_process(delta: float) -> void:
	if _cooldown_timer > 0.0:
		_cooldown_timer = max(0.0, _cooldown_timer - delta)

func can_fire_primary() -> bool:
	return _cooldown_timer <= 0.0

func try_fire_primary() -> bool:
	if not can_fire_primary() or behaviors.size() == 0:
		return false
	
	var active_def = weapons[active_weapon_index]
	var active_behavior = behaviors[active_weapon_index]
	
	var spawn_pos = global_position + muzzle_offset.rotated(global_rotation)
	var spawn_rot = global_rotation
	
	active_behavior.fire(spawn_pos, spawn_rot)
	
	_cooldown_timer = active_def.cooldown
	return true
