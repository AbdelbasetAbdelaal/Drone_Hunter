class_name ShieldGenerator
extends CharacterBody2D

signal destroyed()

@export var max_health: float = 120.0
@export var base_armor: float = 0.10
@export var score_value: int = 150

@onready var health: Health = $Health
@onready var damage_receiver: DamageReceiver = $DamageReceiver
@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	add_to_group("enemy")
	add_to_group("objective")
	
	if health:
		health.max_hp = max_health
		health.current_hp = max_health
		health.base_armor = base_armor
		health.died.connect(_on_death)
		
	if damage_receiver:
		damage_receiver.health = health

func _on_death() -> void:
	destroyed.emit()
	_spawn_scrap()
	queue_free()

func _spawn_scrap() -> void:
	var p_scene = load("res://scenes/entities/Powerup.tscn")
	if p_scene:
		var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
		for i in range(3):
			var scrap = p_scene.instantiate() as Powerup
			root.add_child(scrap)
			scrap.global_position = global_position + Vector2(randf_range(-30, 30), randf_range(-30, 30))
			scrap.setup(Powerup.PowerupType.SCRAP, 50)
