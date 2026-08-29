class_name WeaponController
extends Node2D

@export var muzzle_offset: Vector2 = Vector2(88.0, 0.0) # Player STRIKER primary mount profile

var weapons: Array[WeaponDefinition] = []
var active_weapon_index: int = 0
var behaviors: Array[WeaponBehavior] = []

var _cooldown_timer: float = 0.0
var _active_beam: ContinuousBeamProjectile = null
var _beam_fired_this_frame: bool = false

var beam_script = preload("res://scripts/gameplay/weapons/continuous_beam_projectile.gd")

func _ready() -> void:
	_init_weapons()

func _init_weapons() -> void:
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
	
	# Beam lifecycle: if beam was not fired this physics frame, safely terminate it
	if _active_beam != null and is_instance_valid(_active_beam):
		if not _beam_fired_this_frame:
			_active_beam.stop_beam()
			_active_beam = null
			
	_beam_fired_this_frame = false

func _handle_input() -> void:
	if Input.is_action_just_pressed("next_weapon"):
		cycle_weapon(1)
		
	# Weapon slots 1 to 6
	for i in range(6):
		if Input.is_action_just_pressed("weapon_slot_" + str(i + 1)):
			for w_idx in range(weapons.size()):
				if weapons[w_idx].slot == (i + 1):
					set_active_weapon(w_idx)
					break

func set_active_weapon(idx: int) -> void:
	if idx == active_weapon_index:
		return
	if _active_beam != null and is_instance_valid(_active_beam):
		_active_beam.stop_beam()
		_active_beam = null
	active_weapon_index = clamp(idx, 0, max(0, weapons.size() - 1))

func cycle_weapon(direction: int) -> void:
	if weapons.size() == 0:
		return
	if _active_beam != null and is_instance_valid(_active_beam):
		_active_beam.stop_beam()
		_active_beam = null
	active_weapon_index = (active_weapon_index + direction) % weapons.size()
	if active_weapon_index < 0:
		active_weapon_index = weapons.size() - 1

func can_fire_primary() -> bool:
	if active_weapon_index < weapons.size() and weapons[active_weapon_index].weapon_id == "beam":
		return true
	return _cooldown_timer <= 0.0

func try_fire_primary() -> bool:
	if behaviors.size() == 0 or active_weapon_index >= behaviors.size():
		return false
		
	var active_def = weapons[active_weapon_index]
	var player = get_parent() as Player
	var is_overdrive = false
	
	if player and player.has_node("AbilityController"):
		var ac = player.get_node("AbilityController")
		if ac and "is_overdrive" in ac:
			is_overdrive = ac.is_overdrive

	var spawn_pos = global_position + muzzle_offset.rotated(global_rotation)
	var spawn_rot = global_rotation
	var root_node = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()

	# Persistent Beam Execution
	if active_def.weapon_id == "beam":
		var delta = get_physics_process_delta_time()
		if player and not is_overdrive and active_def.energy_cost > 0.0:
			var energy_needed = active_def.energy_cost * delta * 5.0
			if player.current_energy < energy_needed:
				return false
			player.current_energy = max(0.0, player.current_energy - energy_needed)
			
		if _active_beam == null or not is_instance_valid(_active_beam):
			_active_beam = ContinuousBeamProjectile.new()
			if root_node:
				root_node.add_child(_active_beam)
			_active_beam.setup(player, active_def.damage)
				
		if _active_beam != null and is_instance_valid(_active_beam):
			_active_beam.update_beam(spawn_pos, spawn_rot, delta)
			_beam_fired_this_frame = true
			
		var am = get_tree().get_first_node_in_group("audio_manager")
		if am and am.has_method("play_weapon") and not _beam_fired_this_frame:
			am.play_weapon("beam")
		return true

	# Discrete Projectile Weapons Execution
	if not can_fire_primary():
		return false
		
	if player and not is_overdrive and active_def.energy_cost > 0.0:
		if player.current_energy < active_def.energy_cost:
			return false
		player.current_energy -= active_def.energy_cost
		
	var active_behavior = behaviors[active_weapon_index]
	active_behavior.fire(spawn_pos, spawn_rot, player, root_node)
	
	var am = get_tree().get_first_node_in_group("audio_manager")
	if am and am.has_method("play_weapon"):
		am.play_weapon(active_def.weapon_id)
		
	var cd = active_def.cooldown
	if is_overdrive:
		cd *= 0.5
		
	_cooldown_timer = cd
	return true
