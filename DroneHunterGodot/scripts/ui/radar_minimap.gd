class_name RadarMinimap
extends Control

@export var world_size: Vector2 = Vector2(3840.0, 2160.0)

var _player: Node2D = null

func _ready() -> void:
	custom_minimum_size = Vector2(180, 105)

func _process(_delta: float) -> void:
	if not _player or not is_instance_valid(_player):
		_player = get_tree().get_first_node_in_group("player") as Node2D
	queue_redraw()

func _draw() -> void:
	var w = size.x
	var h = size.y
	
	# Background
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.05, 0.09, 0.75))
	
	# Grid lines
	draw_line(Vector2(w * 0.5, 0), Vector2(w * 0.5, h), Color(0.2, 0.5, 0.7, 0.25), 1.0)
	draw_line(Vector2(0, h * 0.5), Vector2(w, h * 0.5), Color(0.2, 0.5, 0.7, 0.25), 1.0)
	
	# Border
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.3, 0.8, 1.0, 0.6), false, 1.5)
	
	# Draw Powerups
	var powerups = get_tree().get_nodes_in_group("pickup")
	for p in powerups:
		if p is Node2D and is_instance_valid(p):
			var pos = _world_to_radar(p.global_position)
			draw_circle(pos, 2.0, Color(0.2, 1.0, 0.4, 0.85))
			
	# Draw Structures / Objectives
	var structures = get_tree().get_nodes_in_group("structure")
	for s in structures:
		if s is Node2D and is_instance_valid(s):
			var pos = _world_to_radar(s.global_position)
			draw_rect(Rect2(pos - Vector2(3, 3), Vector2(6, 6)), Color(1.0, 0.6, 0.2, 0.9), true)
			
	# Draw Enemies
	var enemies = get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if e is Node2D and is_instance_valid(e):
			var pos = _world_to_radar(e.global_position)
			draw_circle(pos, 2.8, Color(1.0, 0.2, 0.25, 0.95))
			
	# Draw Player
	if _player and is_instance_valid(_player):
		var p_pos = _world_to_radar(_player.global_position)
		var p_rot = _player.global_rotation
		var dir = Vector2.RIGHT.rotated(p_rot) * 5.0
		var left = Vector2.LEFT.rotated(p_rot + 0.8) * 3.5
		var right = Vector2.LEFT.rotated(p_rot - 0.8) * 3.5
		
		var points = PackedVector2Array([
			p_pos + dir,
			p_pos + left,
			p_pos,
			p_pos + right
		])
		draw_colored_polygon(points, Color(0.2, 0.9, 1.0, 1.0))

func _world_to_radar(world_pos: Vector2) -> Vector2:
	var nx = clamp(world_pos.x / world_size.x, 0.0, 1.0)
	var ny = clamp(world_pos.y / world_size.y, 0.0, 1.0)
	return Vector2(nx * size.x, ny * size.y)
