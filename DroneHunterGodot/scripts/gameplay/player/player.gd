class_name Player
extends CharacterBody2D

signal health_changed(current: float, max_val: float)
signal shield_changed(current: float, max_val: float)
signal energy_changed(current: float, max_val: float)
signal weapon_switched(weapon_name: String)
signal player_died()

@export var drone_class: DroneClassDefinition

@export var max_speed: float = 520.0
@export var acceleration: float = 6400.0
@export var drag: float = 5.0

var max_energy: float = 100.0
var current_energy: float = 100.0
var energy_regen: float = 15.0

var aim_target_override: Vector2 = Vector2.INF

@onready var sprite: Sprite2D = $Sprite2D
@onready var engine_flame: Sprite2D = $EngineFlame
@onready var shield_bubble: Sprite2D = $ShieldBubble
@onready var camera: Camera2D = $Camera2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var weapon_controller: WeaponController = $WeaponController
@onready var ability_controller: AbilityController = $AbilityController
@onready var health: Health = $Health
@onready var damage_receiver: DamageReceiver = $DamageReceiver

func _ready() -> void:
	add_to_group("player")
	if drone_class:
		apply_drone_class(drone_class)
	elif ResourceLoader.exists("res://resources/drones/striker.tres"):
		var default_class = load("res://resources/drones/striker.tres") as DroneClassDefinition
		if default_class:
			apply_drone_class(default_class)

	if health:
		health.health_changed.connect(_on_health_changed)
		health.died.connect(_on_death)

func apply_drone_class(def: DroneClassDefinition) -> void:
	drone_class = def
	max_speed = def.max_speed
	acceleration = def.acceleration
	drag = def.drag
	max_energy = def.max_energy
	current_energy = max_energy
	
	if health:
		health.max_hp = def.max_health
		health.current_hp = def.max_health
		health.max_shield = def.max_shield
		health.current_shield = def.max_shield
		health.base_armor = def.base_armor
		health_changed.emit(health.current_hp, health.max_hp)
		shield_changed.emit(health.current_shield, health.max_shield)

func _physics_process(delta: float) -> void:
	_handle_movement(delta)
	_handle_aim()
	_handle_combat(delta)
	_handle_energy(delta)
	_handle_vfx(delta)
	
	if ability_controller and ability_controller.has_method("handle_input"):
		ability_controller.handle_input()

func _handle_energy(delta: float) -> void:
	if current_energy < max_energy:
		current_energy = min(max_energy, current_energy + energy_regen * delta)
		energy_changed.emit(current_energy, max_energy)

func _handle_movement(delta: float) -> void:
	# Primary InputMap vector
	var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	
	# Full physical & virtual fallback (covers all keyboard layouts including Arabic/AZERTY)
	if input_vector.length_squared() == 0.0:
		var x: float = 0.0
		var y: float = 0.0
		if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
			x -= 1.0
		if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
			x += 1.0
		if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
			y -= 1.0
		if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
			y += 1.0
		input_vector = Vector2(x, y).normalized()
	
	if input_vector.length_squared() > 0.0:
		velocity += input_vector * acceleration * delta
	
	var drag_damping: float = max(0.0, 1.0 - (drag * delta))
	velocity *= drag_damping
	
	if velocity.length() > max_speed:
		velocity = velocity.limit_length(max_speed)
	
	move_and_slide()

func _handle_aim() -> void:
	var mouse_world_pos: Vector2 = aim_target_override if aim_target_override != Vector2.INF else get_global_mouse_position()
	look_at(mouse_world_pos)

func _handle_combat(_delta: float) -> void:
	var is_firing = (
		Input.is_action_pressed("fire_primary") or
		Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or
		Input.is_physical_key_pressed(KEY_SPACE) or
		Input.is_key_pressed(KEY_SPACE)
	)
	if is_firing and weapon_controller != null:
		weapon_controller.try_fire_primary()

func _handle_vfx(_delta: float) -> void:
	# Engine Flame Dynamics
	if engine_flame:
		var speed_ratio = velocity.length() / max_speed
		if speed_ratio > 0.05:
			engine_flame.visible = true
			var flame_scale = lerp(0.2, 0.45, speed_ratio) + randf_range(-0.03, 0.03)
			engine_flame.scale = Vector2(flame_scale, flame_scale * 1.2)
			engine_flame.modulate.a = clamp(speed_ratio * 1.2, 0.4, 1.0)
		else:
			engine_flame.visible = false

	# Shield Bubble visual update
	if shield_bubble and health:
		if health.current_shield > 0.0:
			shield_bubble.visible = true
			var pulse = (sin(Time.get_ticks_msec() * 0.005) + 1.0) * 0.5
			shield_bubble.modulate = Color(0.3, 0.8, 1.0, lerp(0.15, 0.35, pulse))
		else:
			shield_bubble.visible = false

func _on_health_changed(_old_val: float, new_val: float, max_val: float) -> void:
	health_changed.emit(new_val, max_val)

func _on_death() -> void:
	player_died.emit()
	print("Player destroyed!")
