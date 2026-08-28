class_name AbilityController
extends Node

@export var player: CharacterBody2D

var _roll_cooldown: float = 0.0
var _roll_timer: float = 0.0
var is_rolling: bool = false

var _emp_cooldown: float = 0.0
var _cloak_cooldown: float = 0.0
var _overdrive_cooldown: float = 0.0

func _physics_process(delta: float) -> void:
	if _roll_cooldown > 0.0:
		_roll_cooldown -= delta
	if _emp_cooldown > 0.0:
		_emp_cooldown -= delta
	if _cloak_cooldown > 0.0:
		_cloak_cooldown -= delta
	if _overdrive_cooldown > 0.0:
		_overdrive_cooldown -= delta
		
	if is_rolling:
		_roll_timer -= delta
		if _roll_timer <= 0.0:
			is_rolling = false
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
		Input.is_key_pressed(KEY_F)
	)

	if roll_pressed and _roll_cooldown <= 0.0:
		_start_roll()
	elif emp_pressed and _emp_cooldown <= 0.0:
		_start_emp()
	elif cloak_pressed and _cloak_cooldown <= 0.0:
		_start_cloak()
	elif overdrive_pressed and _overdrive_cooldown <= 0.0:
		_start_overdrive()

func _start_roll() -> void:
	is_rolling = true
	_roll_timer = 0.28
	_roll_cooldown = 1.2
	if player and player.has_node("Sprite2D"):
		player.get_node("Sprite2D").modulate = Color(0.5, 0.5, 1.0)

func _start_emp() -> void:
	_emp_cooldown = 14.0
	print("EMP activated!")

func _start_cloak() -> void:
	_cloak_cooldown = 10.0
	print("Cloak activated!")

func _start_overdrive() -> void:
	_overdrive_cooldown = 25.0
	print("Overdrive activated!")
