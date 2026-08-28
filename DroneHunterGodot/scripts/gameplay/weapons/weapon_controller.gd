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
	# Load authoritative WeaponDefinition Resources
	var weapon_ids = [
		"pulse", "scatter", "missile", "rapid", "plasma",
		"rail", "barrage", "beam", "tesla", "cluster", "emp"
	]
	
	var behavior_map = {
		"pulse": PulseBehavior,
		"scatter": ScatterBehavior,
		"missile": MissileBehavior,
		"rapid": RapidBehavior,
		"plasma": PlasmaBehavior,
		"rail": RailgunBehavior,
		"barrage": BarrageBehavior,
		"beam": BeamBehavior,
		"tesla": TeslaBehavior,
		"cluster": ClusterBehavior,
		"emp": EMPBehavior
	}
	
	weapons.clear()
	behaviors.clear()
	
	for w_id in weapon_ids:
		var path = "res://resources/weapons/" + w_id + ".tres"
		if ResourceLoader.exists(path):
			var def = load(path) as WeaponDefinition
			if def:
				weapons.append(def)
				var b_class = behavior_map.get(w_id, PulseBehavior)
				behaviors.append(b_class.new(def, self))

func _physics_process(delta: float) -> void:
	if _cooldown_timer > 0.0:
		_cooldown_timer = max(0.0, _cooldown_timer - delta)
		
	_handle_input()

func _handle_input() -> void:
	if Input.is_action_just_pressed("next_weapon") or Input.is_physical_key_pressed(KEY_TAB):
		cycle_weapon(1)
	elif Input.is_action_just_pressed("previous_weapon") or Input.is_physical_key_pressed(KEY_Q):
		cycle_weapon(-1)
		
	# Direct physical number keys 1-6
	var keys = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6]
	for i in range(keys.size()):
		if Input.is_physical_key_pressed(keys[i]) or Input.is_key_pressed(keys[i]) or Input.is_action_just_pressed("weapon_slot_" + str(i + 1)):
			for w_idx in range(weapons.size()):
				if weapons[w_idx].slot == (i + 1):
					active_weapon_index = w_idx
					break

func cycle_weapon(direction: int) -> void:
	if weapons.size() == 0:
		return
	active_weapon_index = (active_weapon_index + direction) % weapons.size()
	if active_weapon_index < 0:
		active_weapon_index = weapons.size() - 1

func can_fire_primary() -> bool:
	return _cooldown_timer <= 0.0

func try_fire_primary() -> bool:
	if not can_fire_primary() or behaviors.size() == 0 or active_weapon_index >= behaviors.size():
		return false
	
	var active_def = weapons[active_weapon_index]
	var active_behavior = behaviors[active_weapon_index]
	
	var spawn_pos = global_position + muzzle_offset.rotated(global_rotation)
	var spawn_rot = global_rotation
	
	active_behavior.fire(spawn_pos, spawn_rot)
	
	_cooldown_timer = active_def.cooldown
	return true
