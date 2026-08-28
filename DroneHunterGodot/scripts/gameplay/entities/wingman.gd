class_name Wingman
extends Node2D

@export var formation_offset: Vector2 = Vector2(-42.0, -40.0)
@export var fire_rate: float = 0.45
@export var damage: float = 16.0
@export var projectile_speed: float = 850.0
@export var detection_range: float = 650.0

var target_player: Node2D = null
var _fire_timer: float = 0.0
var _bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	if not target_player:
		var players = get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			target_player = players[0]

func _physics_process(delta: float) -> void:
	if not target_player or not is_instance_valid(target_player):
		return
		
	# Follow formation position
	var desired_pos = target_player.global_position + formation_offset.rotated(target_player.global_rotation)
	global_position = global_position.lerp(desired_pos, delta * 12.0)
	
	# Find nearest enemy
	var nearest_enemy: Node2D = _find_nearest_enemy()
	if nearest_enemy:
		look_at(nearest_enemy.global_position)
		_fire_timer -= delta
		if _fire_timer <= 0.0:
			_fire_at(nearest_enemy.global_position)
			_fire_timer = fire_rate
	else:
		global_rotation = lerp_angle(global_rotation, target_player.global_rotation, delta * 8.0)

func _find_nearest_enemy() -> Node2D:
	var enemies = get_tree().get_nodes_in_group("enemy")
	var closest_dist: float = detection_range
	var closest_node: Node2D = null
	
	for enemy in enemies:
		if is_instance_valid(enemy) and enemy is Node2D:
			var dist = global_position.distance_to(enemy.global_position)
			if dist < closest_dist:
				closest_dist = dist
				closest_node = enemy
				
	return closest_node

func _fire_at(target_pos: Vector2) -> void:
	if not _bullet_scene:
		return
		
	var proj = _bullet_scene.instantiate() as Projectile
	if not proj:
		return
		
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	root.add_child(proj)
	
	proj.global_position = global_position
	proj.global_rotation = (target_pos - global_position).angle()
	proj.setup(projectile_speed, damage, Hit.DamageType.NORMAL, self, "projectiles/bullet_pulse.png")
