class_name EnemyScout
extends CharacterBody2D

signal died(enemy: EnemyScout)

# Stats sourced directly from Pygame game_data.py Scout specifications
@export var max_hp: float = 30.0        # SCOUT_HP = 30
@export var move_speed: float = 210.0   # SCOUT_SPEED = 210.0

var current_hp: float = 30.0
var _hit_flash_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

func _ready() -> void:
	add_to_group("enemies")
	current_hp = max_hp

func _physics_process(delta: float) -> void:
	_handle_movement(delta)
	_handle_hit_flash(delta)

func _handle_movement(_delta: float) -> void:
	var player = get_tree().get_first_node_in_group("player") as Node2D
	if player != null and is_instance_valid(player):
		var dir = (player.global_position - global_position).normalized()
		velocity = dir * move_speed
		look_at(player.global_position)
		move_and_slide()
	else:
		velocity = Vector2.ZERO

func _handle_hit_flash(delta: float) -> void:
	if _hit_flash_timer > 0.0:
		_hit_flash_timer -= delta
		if _hit_flash_timer <= 0.0 and sprite:
			sprite.modulate = Color.WHITE

func take_damage(amount: float) -> void:
	current_hp -= amount
	
	if sprite:
		sprite.modulate = Color(1.8, 0.4, 0.4)
		_hit_flash_timer = 0.08
		
	if current_hp <= 0.0:
		die()

func die() -> void:
	died.emit(self)
	queue_free()
