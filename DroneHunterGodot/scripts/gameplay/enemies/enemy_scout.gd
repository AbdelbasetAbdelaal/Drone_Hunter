class_name EnemyScout
extends CharacterBody2D

signal died(enemy: EnemyScout)

# Stats sourced directly from Pygame game_data.py Scout specifications
@export var max_hp: float = 30.0        # SCOUT_HP = 30
@export var move_speed: float = 120.0    # SCOUT_SPEED = 210.0 (drift speed in arena)

var current_hp: float = 30.0
var _hit_flash_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

func _ready() -> void:
	add_to_group("enemies")
	current_hp = max_hp

func _physics_process(delta: float) -> void:
	if _hit_flash_timer > 0.0:
		_hit_flash_timer -= delta
		if _hit_flash_timer <= 0.0 and sprite:
			sprite.modulate = Color.WHITE

func take_damage(amount: float) -> void:
	current_hp -= amount
	
	# Visual hit feedback (hit flash)
	if sprite:
		sprite.modulate = Color(1.8, 0.4, 0.4)
		_hit_flash_timer = 0.08
		
	if current_hp <= 0.0:
		die()

func die() -> void:
	died.emit(self)
	queue_free()
