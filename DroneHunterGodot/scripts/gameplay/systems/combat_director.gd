class_name CombatDirector
extends Node

signal encounter_started(encounter_index: int, total_encounters: int)
signal encounter_cleared(encounter_index: int)
signal mission_completed(score: int, scrap: int)
signal mission_failed()

# Compatibility alias
signal wave_started(wave_index: int, total_waves: int)
signal wave_cleared(wave_index: int)

@export var current_mission_def: MissionDefinition
@export var spawn_parent: Node2D

var total_encounters: int = 0
@export var max_waves: int:
	get: return total_encounters
	set(v): total_encounters = v

var current_encounter_index: int = 0
var enemies_remaining: int = 0
var mission_score: int = 0
var mission_scrap_earned: int = 0

var scout_scene: PackedScene = preload("res://scenes/enemies/EnemyScout.tscn")
var shooter_scene: PackedScene = preload("res://scenes/enemies/EnemyShooter.tscn")
var heavy_scene: PackedScene = preload("res://scenes/enemies/EnemyHeavy.tscn")
var shield_scene: PackedScene = preload("res://scenes/enemies/EnemyShieldElite.tscn")
var target_scene: PackedScene = preload("res://scenes/missions/GroundObjectiveTarget.tscn")

var objective_controller: ObjectiveController

func _ready() -> void:
	add_to_group("combat_director")
	if not spawn_parent:
		spawn_parent = get_parent() as Node2D if get_parent() is Node2D else get_tree().current_scene
		
	# Setup objective controller child
	if not objective_controller:
		objective_controller = ObjectiveController.new()
		add_child(objective_controller)
		objective_controller.objective_completed.connect(_on_objective_completed)
		objective_controller.objective_failed.connect(_on_objective_failed)
	
	# Connect to player death
	for p in get_tree().get_nodes_in_group("player"):
		if is_instance_valid(p) and not p.is_queued_for_deletion():
			if p.has_signal("player_died") and not p.player_died.is_connected(_on_player_died):
				p.player_died.connect(_on_player_died)
			break
		
	# If no mission definition was explicitly assigned, load default current mission
	if not current_mission_def:
		var gm = get_tree().get_first_node_in_group("game_manager")
		var m_id = gm.campaign_state.current_mission if (gm and gm.campaign_state) else "S1_M1"
		var path = "res://resources/missions/" + m_id + ".tres"
		if ResourceLoader.exists(path):
			current_mission_def = load(path) as MissionDefinition

	if current_mission_def:
		start_mission(current_mission_def)

func start_mission(mission_def: MissionDefinition) -> void:
	current_mission_def = mission_def
	current_encounter_index = 0
	mission_score = 0
	mission_scrap_earned = mission_def.scrap_reward
	total_encounters = max(1, mission_def.encounter_sequence.size())
	
	if objective_controller:
		objective_controller.setup_objective(mission_def)
		
	_spawn_mission_ground_targets()
	start_next_encounter()

func _spawn_mission_ground_targets() -> void:
	if not current_mission_def or current_mission_def.objective_target == "":
		return
	if not target_scene or not spawn_parent:
		return
		
	# Deterministic placement in the mission world
	var target_pos = Vector2(1920, 680)
	var t_inst = target_scene.instantiate()
	spawn_parent.add_child(t_inst)
	t_inst.global_position = target_pos
	t_inst.configure_target(current_mission_def.objective_target, current_mission_def.defense_level)
	
	if objective_controller:
		objective_controller.register_target(t_inst)

func start_next_encounter() -> void:
	current_encounter_index += 1
	var is_survive = (objective_controller and objective_controller.objective_type == "survive")
	
	if not is_survive and current_encounter_index > total_encounters:
		if objective_controller and objective_controller.objective_type in ["complete_encounters", "destroy_all"]:
			if objective_controller.active_targets.size() == 0:
				objective_controller.complete_objective()
		return
		
	var display_idx = ((current_encounter_index - 1) % total_encounters) + 1
	encounter_started.emit(display_idx, total_encounters)
	wave_started.emit(display_idx, total_encounters)
	print("Combat Director: Starting Encounter %d / %d" % [display_idx, total_encounters])
	
	if current_mission_def and current_mission_def.encounter_sequence.size() > 0:
		var seq_idx = (current_encounter_index - 1) % current_mission_def.encounter_sequence.size()
		var wave_list = current_mission_def.encounter_sequence[seq_idx]
		_spawn_encounter_wave(wave_list)
	else:
		_spawn_fallback_wave(current_encounter_index)

func _spawn_encounter_wave(enemy_types: Array) -> void:
	var player = get_tree().get_first_node_in_group("player") as Node2D
	var base_pos = player.global_position if player else Vector2(1920, 1080)
	
	var type_map = {
		"scout": scout_scene,
		"shooter": shooter_scene,
		"heavy": heavy_scene,
		"shield_elite": shield_scene,
		"shield_drone": shield_scene
	}
	
	for e_type in enemy_types:
		var type_key = str(e_type).to_lower()
		if not type_map.has(type_key):
			push_error("CombatDirector: Unknown enemy type '%s' in encounter sequence. Failing safely." % str(e_type))
			continue
		var scene = type_map[type_key]
		_spawn_enemy(scene, base_pos + _random_spawn_offset())

func _spawn_fallback_wave(wave_num: int) -> void:
	var player = get_tree().get_first_node_in_group("player") as Node2D
	var base_pos = player.global_position if player else Vector2(1920, 1080)
	for i in range(2 + wave_num):
		_spawn_enemy(scout_scene, base_pos + _random_spawn_offset())

func _random_spawn_offset() -> Vector2:
	var angle = randf_range(0, TAU)
	var dist = randf_range(650.0, 950.0)
	return Vector2(cos(angle) * dist, sin(angle) * dist)

func _spawn_enemy(scene: PackedScene, pos: Vector2) -> void:
	if not scene or not spawn_parent:
		return
	var inst = scene.instantiate() as CharacterBody2D
	spawn_parent.add_child(inst)
	inst.global_position = pos
	enemies_remaining += 1
	inst.tree_exited.connect(_on_enemy_defeated)

func get_living_enemy_count() -> int:
	if not is_inside_tree() or get_tree() == null:
		return enemies_remaining
	var list = get_tree().get_nodes_in_group("enemy")
	var count = 0
	for e in list:
		if is_instance_valid(e) and not e.is_queued_for_deletion():
			if "health" in e and e.health and not e.health.is_dead:
				count += 1
			elif not ("health" in e):
				count += 1
	return count

func _on_enemy_defeated() -> void:
	enemies_remaining = get_living_enemy_count()
	mission_score += 150
	
	if enemies_remaining == 0:
		var is_survive = (objective_controller and objective_controller.objective_type == "survive")
		encounter_cleared.emit(current_encounter_index)
		wave_cleared.emit(current_encounter_index)
		
		if objective_controller:
			objective_controller.on_encounter_cleared(current_encounter_index, total_encounters)
			
		if is_survive:
			if not objective_controller.is_finished:
				var timer = get_tree().create_timer(1.5)
				if timer:
					await timer.timeout
					if is_inside_tree() and not objective_controller.is_finished:
						start_next_encounter()
		else:
			if current_encounter_index < total_encounters:
				var timer = get_tree().create_timer(2.0)
				if timer:
					await timer.timeout
					if is_inside_tree():
						start_next_encounter()
			else:
				if objective_controller:
					objective_controller.on_all_enemies_destroyed()

func _on_objective_completed() -> void:
	_on_mission_victory()

func _on_objective_failed() -> void:
	_on_player_died()

func _on_player_died() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.state_manager:
		gm.state_manager.change_state(GameStateManager.State.MISSION_FAILED)
	mission_failed.emit()
	print("Combat Director: Player died - Mission Failed.")

func _on_mission_victory() -> void:
	var total_scrap_payout = current_mission_def.scrap_reward if current_mission_def else 150
	
	var am = get_tree().get_first_node_in_group("audio_manager")
	if am and am.has_method("play_victory"):
		am.play_victory()
		
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.campaign_state and current_mission_def:
		var comp_res = gm.campaign_state.complete_mission(current_mission_def.mission_id)
		total_scrap_payout = comp_res.get("total_reward", total_scrap_payout)
		if gm.has_method("add_scrap"):
			gm.add_scrap(total_scrap_payout)
		if gm.has_method("save_game"):
			gm.save_game()
		if gm.state_manager:
			gm.state_manager.change_state(GameStateManager.State.MISSION_COMPLETE)
	elif gm and gm.has_method("add_scrap"):
		gm.add_scrap(total_scrap_payout)
			
	mission_completed.emit(mission_score, total_scrap_payout)
	print("Combat Director: Mission Victory! Score: %d, Total Scrap Payout: %d" % [mission_score, total_scrap_payout])
