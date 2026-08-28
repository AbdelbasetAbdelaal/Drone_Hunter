class_name CombatDirector
extends Node

var scout_scene: PackedScene = preload("res://scenes/enemies/EnemyScout.tscn")
var shooter_scene: PackedScene = preload("res://scenes/enemies/EnemyShooter.tscn")
var heavy_scene: PackedScene = preload("res://scenes/enemies/EnemyHeavy.tscn")
var shield_scene: PackedScene = preload("res://scenes/enemies/EnemyShieldElite.tscn")

@export var spawn_parent: Node2D

func _ready() -> void:
	# Small delay to ensure player and world are loaded
	await get_tree().create_timer(0.5).timeout
	_spawn_initial_encounter()

func _spawn_initial_encounter() -> void:
	if not spawn_parent:
		spawn_parent = get_tree().current_scene
		
	var player = get_tree().get_first_node_in_group("player") as Node2D
	if not player:
		return
		
	var base_pos = player.global_position
	
	_spawn(scout_scene, base_pos + Vector2(600, -300))
	_spawn(shooter_scene, base_pos + Vector2(800, 200))
	_spawn(heavy_scene, base_pos + Vector2(-700, -100))
	_spawn(shield_scene, base_pos + Vector2(-600, 300))
	
	print("Combat Director: Spawned deterministic test encounter.")

func _spawn(scene: PackedScene, pos: Vector2) -> void:
	if scene == null:
		return
	var inst = scene.instantiate() as Node2D
	spawn_parent.add_child(inst)
	inst.global_position = pos
