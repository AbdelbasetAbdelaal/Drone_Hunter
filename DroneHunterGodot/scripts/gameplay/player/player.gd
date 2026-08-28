class_name Player
extends CharacterBody2D

# Movement values sourced directly from Pygame MovementController (game_data.py & player_movement.py)
@export var max_speed: float = 520.0       # HORIZONTAL_SPEED = 520.0
@export var acceleration: float = 6400.0   # MovementController.acceleration = 6400.0
@export var drag: float = 5.0              # MovementController.drag = 5.0

var aim_target_override: Vector2 = Vector2.INF

@onready var sprite: Sprite2D = $Sprite2D
@onready var camera: Camera2D = $Camera2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var weapon_controller: Node2D = $WeaponController

func _ready() -> void:
	add_to_group("player")

func _physics_process(delta: float) -> void:
	_handle_movement(delta)
	_handle_aim()
	_handle_combat(delta)

func _handle_movement(delta: float) -> void:
	# 360-degree vector input mapped from Godot InputMap
	var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	
	if input_vector.length_squared() > 0.0:
		velocity += input_vector * acceleration * delta
	
	# Linear Inertial Drag & Smooth Deceleration (from Pygame: max(0.0, 1.0 - (drag * dt)))
	var drag_damping: float = max(0.0, 1.0 - (drag * delta))
	velocity *= drag_damping
	
	# Clamp Max Speed (from Pygame: velocity.scale_to_length(max_speed))
	if velocity.length() > max_speed:
		velocity = velocity.limit_length(max_speed)
	
	move_and_slide()

func _handle_aim() -> void:
	# World-space mouse aim (remains accurate during camera movement, scaling & resizing)
	var mouse_world_pos: Vector2 = aim_target_override if aim_target_override != Vector2.INF else get_global_mouse_position()
	look_at(mouse_world_pos)

func _handle_combat(_delta: float) -> void:
	if Input.is_action_pressed("fire_primary") and weapon_controller != null and weapon_controller.has_method("try_fire_primary"):
		weapon_controller.try_fire_primary()
