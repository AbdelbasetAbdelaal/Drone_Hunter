class_name AbilityController
extends Node

@export var player: CharacterBody2D

var _roll_cooldown: float = 0.0
var _roll_timer: float = 0.0
var is_rolling: bool = false

var _emp_cooldown: float = 0.0
var _cloak_cooldown: float = 0.0
var _cloak_timer: float = 0.0
var is_cloaked: bool = false

var _overdrive_cooldown: float = 0.0
var _overdrive_timer: float = 0.0
var is_overdrive: bool = false

var _overclock_cooldown: float = 0.0
var _overclock_timer: float = 0.0
var is_overclock: bool = false

var current_ability_id: String = "roll"

func setup_ability(ability_id: String) -> void:
	current_ability_id = ability_id.to_lower()

var shockwave_tex = preload("res://assets/vfx/shockwave.png")

func _physics_process(delta: float) -> void:
	if _roll_cooldown > 0.0:
		_roll_cooldown -= delta
	if _emp_cooldown > 0.0:
		_emp_cooldown -= delta
	if _cloak_cooldown > 0.0:
		_cloak_cooldown -= delta
	if _overdrive_cooldown > 0.0:
		_overdrive_cooldown -= delta
	if _overclock_cooldown > 0.0:
		_overclock_cooldown -= delta
		
	if is_rolling:
		_roll_timer -= delta
		_spawn_ghost_trail()
		if _roll_timer <= 0.0:
			is_rolling = false
			if player and player.has_node("Sprite2D"):
				player.get_node("Sprite2D").modulate = Color.WHITE

	if is_cloaked:
		_cloak_timer -= delta
		if _cloak_timer <= 0.0:
			is_cloaked = false
			if player and player.has_node("Sprite2D"):
				player.get_node("Sprite2D").modulate.a = 1.0

	if is_overdrive:
		_overdrive_timer -= delta
		if _overdrive_timer <= 0.0:
			is_overdrive = false
			if player and player.has_node("Sprite2D"):
				player.get_node("Sprite2D").modulate = Color.WHITE

	if is_overclock:
		_overclock_timer -= delta
		if _overclock_timer <= 0.0:
			is_overclock = false
			if player and player.has_node("Sprite2D"):
				player.get_node("Sprite2D").modulate = Color.WHITE

func handle_input() -> void:
	var roll_pressed = (
		Input.is_action_just_pressed("roll") or
		Input.is_physical_key_pressed(KEY_SHIFT) or
		Input.is_key_pressed(KEY_SHIFT)
	)
	var emp_pressed = (
		Input.is_action_just_pressed("emp") or
		Input.is_physical_key_pressed(KEY_E) or
		Input.is_key_pressed(KEY_E)
	)
	var cloak_pressed = (
		Input.is_action_just_pressed("cloak") or
		Input.is_physical_key_pressed(KEY_C) or
		Input.is_key_pressed(KEY_C)
	)
	var overdrive_pressed = (
		Input.is_action_just_pressed("ultimate") or
		Input.is_physical_key_pressed(KEY_F) or
		Input.is_key_pressed(KEY_F) or
		Input.is_physical_key_pressed(KEY_Q) or
		Input.is_key_pressed(KEY_Q)
	)
	var overclock_pressed = (
		Input.is_physical_key_pressed(KEY_R) or
		Input.is_key_pressed(KEY_R)
	)

	if roll_pressed and _roll_cooldown <= 0.0:
		_start_roll()
	elif emp_pressed and _emp_cooldown <= 0.0:
		_start_emp()
	elif cloak_pressed and _cloak_cooldown <= 0.0:
		_start_cloak()
	elif overdrive_pressed and _overdrive_cooldown <= 0.0:
		_start_overdrive()
	elif overclock_pressed and _overclock_cooldown <= 0.0:
		_start_overclock()

func _start_roll() -> void:
	is_rolling = true
	_roll_timer = 0.28
	_roll_cooldown = 1.2
	if player:
		var dir = Vector2.RIGHT.rotated(player.global_rotation)
		player.velocity += dir * 750.0
		if player.has_node("Sprite2D"):
			player.get_node("Sprite2D").modulate = Color(0.6, 0.9, 1.5, 1.0)
		var cam = player.get_tree().get_first_node_in_group("camera")
		if cam and cam.has_method("add_trauma"):
			cam.add_trauma(0.15)

func _spawn_ghost_trail() -> void:
	if not player or not player.is_inside_tree():
		return
	var root = player.get_tree().current_scene
	if not root:
		return
	var ghost = Sprite2D.new()
	var player_sprite = player.get_node_or_null("Sprite2D") as Sprite2D
	if player_sprite and player_sprite.texture:
		ghost.texture = player_sprite.texture
		ghost.global_position = player.global_position
		ghost.global_rotation = player.global_rotation
		ghost.scale = player_sprite.scale
		ghost.modulate = Color(0.3, 0.8, 1.0, 0.4)
		root.add_child(ghost)
		var tween = ghost.create_tween()
		tween.tween_property(ghost, "modulate:a", 0.0, 0.25)
		tween.tween_callback(ghost.queue_free)

func _start_emp() -> void:
	_emp_cooldown = 12.0
	if not player or not player.is_inside_tree():
		return
		
	# Spawn expanding EMP shockwave ring
	var root = player.get_tree().current_scene
	if root and shockwave_tex:
		var emp_ring = Sprite2D.new()
		emp_ring.texture = shockwave_tex
		emp_ring.global_position = player.global_position
		emp_ring.scale = Vector2(0.1, 0.1)
		emp_ring.modulate = Color(0.2, 0.9, 1.5, 1.0)
		root.add_child(emp_ring)
		var tween = emp_ring.create_tween().set_parallel(true)
		tween.tween_property(emp_ring, "scale", Vector2(4.5, 4.5), 0.45).set_ease(Tween.EASE_OUT)
		tween.tween_property(emp_ring, "modulate:a", 0.0, 0.45)
		tween.chain().tween_callback(emp_ring.queue_free)
		
	# Stun nearby enemies in 650px radius
	var enemies = player.get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if e is Node2D and e.global_position.distance_to(player.global_position) <= 650.0:
			if e.has_method("apply_emp_stun"):
				e.apply_emp_stun(3.0)
				
	var cam = player.get_tree().get_first_node_in_group("camera")
	if cam and cam.has_method("add_trauma"):
		cam.add_trauma(0.35)

func _start_cloak() -> void:
	_cloak_cooldown = 10.0
	_cloak_timer = 5.0
	is_cloaked = true
	if player and player.has_node("Sprite2D"):
		player.get_node("Sprite2D").modulate = Color(1.0, 1.0, 1.0, 0.25)

func _start_overdrive() -> void:
	_overdrive_cooldown = 20.0
	_overdrive_timer = 6.0
	is_overdrive = true
	if player and player.has_node("Sprite2D"):
		player.get_node("Sprite2D").modulate = Color(1.8, 0.8, 0.3, 1.0)
	var cam = player.get_tree().get_first_node_in_group("camera")
	if cam and cam.has_method("add_trauma"):
		cam.add_trauma(0.25)

func _start_overclock() -> void:
	_overclock_cooldown = 15.0
	_overclock_timer = 5.0
	is_overclock = true
	if player:
		if "current_energy" in player and "max_energy" in player:
			player.current_energy = player.max_energy
		if player.has_node("Sprite2D"):
			player.get_node("Sprite2D").modulate = Color(0.3, 1.8, 1.8, 1.0)
	var cam = player.get_tree().get_first_node_in_group("camera")
	if cam and cam.has_method("add_trauma"):
		cam.add_trauma(0.18)
