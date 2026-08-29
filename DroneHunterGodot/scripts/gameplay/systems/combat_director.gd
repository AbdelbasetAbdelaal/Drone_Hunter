class_name CombatDirector
extends Node

signal wave_started(wave_index: int, total_waves: int)
signal wave_cleared(wave_index: int)
signal mission_completed(score: int, scrap: int)
signal mission_failed()

@export var max_waves: int = 4
@export var is_boss_mission: bool = false
@export var spawn_parent: Node2D

var current_wave: int = 0
var enemies_remaining: int = 0
var mission_score: int = 0
var mission_scrap_earned: int = 0

var scout_scene: PackedScene = preload("res://scenes/enemies/EnemyScout.tscn")
var shooter_scene: PackedScene = preload("res://scenes/enemies/EnemyShooter.tscn")
var heavy_scene: PackedScene = preload("res://scenes/enemies/EnemyHeavy.tscn")
var shield_scene: PackedScene = preload("res://scenes/enemies/EnemyShieldElite.tscn")

func _ready() -> void:
	add_to_group("combat_director")
	if not spawn_parent:
		spawn_parent = get_parent() as Node2D if get_parent() is Node2D else get_tree().current_scene
		
	# Connect to player death if player exists
	var player = get_tree().get_first_node_in_group("player") as Player
	if player:
		player.player_died.connect(_on_player_died)
		
	start_next_wave()

func start_next_wave() -> void:
	current_wave += 1
	if current_wave > max_waves:
		_on_mission_victory()
		return
		
	wave_started.emit(current_wave, max_waves)
	print("Combat Director: Starting Wave ", current_wave, " / ", max_waves)
	_spawn_standard_wave(current_wave)

func _spawn_standard_wave(wave_num: int) -> void:
	var player = get_tree().get_first_node_in_group("player") as Node2D
	var base_pos = player.global_position if player else Vector2(1920, 1080)
	
	var num_scouts = 2 + wave_num * 2
	var num_shooters = 1 + wave_num
	var num_heavies = 1 if wave_num >= 2 else 0
	var num_shields = 1 if wave_num >= 3 else 0
	
	for i in range(num_scouts):
		_spawn_enemy(scout_scene, base_pos + _random_spawn_offset())
	for i in range(num_shooters):
		_spawn_enemy(shooter_scene, base_pos + _random_spawn_offset())
	for i in range(num_heavies):
		_spawn_enemy(heavy_scene, base_pos + _random_spawn_offset())
	for i in range(num_shields):
		_spawn_enemy(shield_scene, base_pos + _random_spawn_offset())

func trigger_reinforcement_wave(from_pos: Vector2) -> void:
	print("Combat Director: Reinforcements called!")
	for i in range(2):
		_spawn_enemy(scout_scene, from_pos + _random_spawn_offset())
	_spawn_enemy(shooter_scene, from_pos + _random_spawn_offset())

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

func _on_enemy_defeated() -> void:
	enemies_remaining = max(0, enemies_remaining - 1)
	mission_score += 150
	
	if enemies_remaining == 0:
		wave_cleared.emit(current_wave)
		if not is_inside_tree() or get_tree() == null:
			return
		# Delay 2.5s before next wave
		var timer = get_tree().create_timer(2.5)
		if timer:
			await timer.timeout
			if is_inside_tree():
				start_next_wave()

func _on_player_died() -> void:
	mission_failed.emit()
	print("Combat Director: Player died - Mission Failed.")

func _on_mission_victory() -> void:
	mission_scrap_earned = int(mission_score * 0.4)
	var am = get_tree().get_first_node_in_group("audio_manager")
	if am and am.has_method("play_victory"):
		am.play_victory()
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.has_method("add_scrap"):
		gm.add_scrap(mission_scrap_earned)
	mission_completed.emit(mission_score, mission_scrap_earned)
	print("Combat Director: Mission Victory! Score: ", mission_score, " Scrap: ", mission_scrap_earned)
