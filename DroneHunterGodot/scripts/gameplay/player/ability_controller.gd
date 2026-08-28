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
	if Input.is_action_just_pressed("roll") and _roll_cooldown <= 0.0:
		_start_roll()
	elif Input.is_action_just_pressed("emp") and _emp_cooldown <= 0.0:
		_start_emp()
	elif Input.is_action_just_pressed("cloak") and _cloak_cooldown <= 0.0:
		_start_cloak()
	elif Input.is_action_just_pressed("ultimate") and _overdrive_cooldown <= 0.0:
		_start_overdrive()

func _start_roll() -> void:
	is_rolling = true
	_roll_timer = 0.28
	_roll_cooldown = 1.2
	if player and player.has_node("Sprite2D"):
		player.get_node("Sprite2D").modulate = Color(0.5, 0.5, 1.0)
	# Push velocity logic could be added here or in Player

func _start_emp() -> void:
	_emp_cooldown = 14.0
	print("EMP activated!")

func _start_cloak() -> void:
	_cloak_cooldown = 10.0
	print("Cloak activated!")

func _start_overdrive() -> void:
	_overdrive_cooldown = 25.0
	print("Overdrive activated!")
