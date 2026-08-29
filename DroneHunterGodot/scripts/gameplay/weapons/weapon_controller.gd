class_name WeaponController
extends Node2D

@export var muzzle_offset: Vector2 = Vector2(88.0, 0.0) # Player STRIKER primary mount profile

var weapons: Array[WeaponDefinition] = []
var active_weapon_index: int = 0
var behaviors: Array[WeaponBehavior] = []

var _cooldown_timer: float = 0.0
var _active_beam: ContinuousBeamProjectile = null
var _beam_fired_this_frame: bool = false

func _ready() -> void:
	if weapons.is_empty():
		_init_weapons()

func _init_weapons() -> void:
	var weapon_ids = [
		"pulse", "scatter", "missile", "rapid", "plasma",
		"rail", "barrage", "beam", "tesla", "cluster", "emp"
	]
	equip_weapons(weapon_ids)

func equip_weapons(weapon_ids: Array) -> void:
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
		var path = "res://resources/weapons/" + str(w_id).to_lower() + ".tres"
		if ResourceLoader.exists(path):
			var def = load(path) as WeaponDefinition
			if def:
				weapons.append(def)
				var b_class = behavior_map.get(str(w_id).to_lower(), PulseBehavior)
				behaviors.append(b_class.new(def))
				
	active_weapon_index = 0

func _physics_process(delta: float) -> void:
	if _cooldown_timer > 0.0:
		_cooldown_timer = max(0.0, _cooldown_timer - delta)
		
	_handle_input()
	
	# Beam lifecycle: if beam was not fired this physics frame, safely terminate it
	if _active_beam != null and is_instance_valid(_active_beam):
		if not _beam_fired_this_frame:
			_active_beam.stop_beam()
			_active_beam = null
			
	# Reset frame fire flag at the end of physics frame
	_beam_fired_this_frame = false

func _handle_input() -> void:
	if weapons.size() <= 1:
		return
		
	# Quick-switch numeric keys 1..6
	for i in range(min(6, weapons.size())):
		var key = KEY_1 + i
		if Input.is_key_pressed(key) or Input.is_physical_key_pressed(key):
			_switch_to(i)
			return
			
	# TAB cycle weapons
	if Input.is_action_just_pressed("next_weapon") or Input.is_physical_key_pressed(KEY_TAB):
		cycle_weapon(1)

func cycle_weapon(dir: int = 1) -> void:
	if weapons.size() == 0:
		return
	if _active_beam != null and is_instance_valid(_active_beam):
		_active_beam.stop_beam()
		_active_beam = null
	active_weapon_index = (active_weapon_index + dir + weapons.size()) % weapons.size()

func _switch_to(idx: int) -> void:
	if idx >= 0 and idx < weapons.size() and idx != active_weapon_index:
		if _active_beam != null and is_instance_valid(_active_beam):
			_active_beam.stop_beam()
			_active_beam = null
		active_weapon_index = idx

func set_active_weapon(idx: int) -> void:
	_switch_to(idx)

func try_fire_primary() -> bool:
	if weapons.size() == 0 or behaviors.size() == 0:
		return false
		
	var def = weapons[active_weapon_index]
	var behavior = behaviors[active_weapon_index]
	
	var player = get_parent() as Player
	if not player:
		return false
		
	# Energy check
	if def.energy_cost > 0.0:
		if player.current_energy < def.energy_cost:
			return false
			
	# Cooldown check
	if _cooldown_timer > 0.0:
		if def.id == "beam" and _active_beam != null and is_instance_valid(_active_beam):
			_beam_fired_this_frame = true
			var spawn_root = get_tree().current_scene if get_tree() else get_parent()
			behavior.fire(get_muzzle_pos(), get_muzzle_rot(), player, spawn_root)
			return true
		return false
		
	# Consume Energy
	if def.energy_cost > 0.0:
		player.current_energy -= def.energy_cost
		player.energy_changed.emit(player.current_energy, player.max_energy)
		
	# Set Cooldown
	_cooldown_timer = def.cooldown
	
	# Audio handling
	var am = get_tree().get_first_node_in_group("audio_manager")
	if def.id == "beam":
		if not _beam_fired_this_frame:
			if am and am.has_method("play_weapon"):
				am.play_weapon("beam")
		_beam_fired_this_frame = true
	else:
		if am and am.has_method("play_weapon"):
			am.play_weapon(def.id)
			
	var spawn_root = get_tree().current_scene if get_tree() else get_parent()
	if def.id == "beam":
		if _active_beam == null or not is_instance_valid(_active_beam):
			_active_beam = ContinuousBeamProjectile.new()
			spawn_root.add_child(_active_beam)
			_active_beam.setup(player, def.damage)
		_active_beam.update_beam(get_muzzle_pos(), get_muzzle_rot(), 0.016)
	else:
		behavior.fire(get_muzzle_pos(), get_muzzle_rot(), player, spawn_root)
	return true

func get_muzzle_pos() -> Vector2:
	return global_position + muzzle_offset.rotated(global_rotation)

func get_muzzle_rot() -> float:
	return global_rotation
