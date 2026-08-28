class_name EnemyCore
extends CharacterBody2D

@export var max_hp: float = 30.0
@export var base_speed: float = 210.0
@export var base_armor: float = 0.0
@export var score_value: int = 150

@onready var sprite: Sprite2D = $Sprite2D
@onready var health: Health = $Health
@onready var damage_receiver: DamageReceiver = $DamageReceiver

var target: Node2D

var current_hp: float:
	get:
		return health.current_hp if health != null else 0.0
	set(value):
		if health != null:
			health.current_hp = value

var move_speed: float:
	get: return base_speed
	set(v): base_speed = v

func _ready() -> void:
	add_to_group("enemy")
	
	if health:
		health.max_hp = max_hp
		health.base_armor = base_armor
		health.current_hp = max_hp
		health.died.connect(_on_death)
		
	if damage_receiver:
		damage_receiver.health = health
		
	# Find player
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		target = players[0]

func _on_death() -> void:
	queue_free()

func _physics_process(delta: float) -> void:
	_process_ai(delta)

func _process_ai(delta: float) -> void:
	# Virtual method to be overridden by AI controllers
	pass
