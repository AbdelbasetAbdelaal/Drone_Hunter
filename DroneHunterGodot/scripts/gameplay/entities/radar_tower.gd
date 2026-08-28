class_name RadarTower
extends CharacterBody2D

signal destroyed()
signal alert_triggered()

@export var max_health: float = 140.0
@export var base_armor: float = 0.15
@export var scan_range: float = 800.0
@export var alert_cooldown: float = 8.0

var _alert_timer: float = 0.0

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

func _physics_process(delta: float) -> void:
	if _alert_timer > 0.0:
		_alert_timer -= delta
		return
		
	var player = get_tree().get_first_node_in_group("player") as Node2D
	if player and is_instance_valid(player):
		var dist = global_position.distance_to(player.global_position)
		if dist <= scan_range:
			_trigger_alert()
			_alert_timer = alert_cooldown

func _trigger_alert() -> void:
	alert_triggered.emit()
	var cd = get_tree().get_first_node_in_group("combat_director")
	if cd and cd.has_method("trigger_reinforcement_wave"):
		cd.trigger_reinforcement_wave(global_position)

func _on_death() -> void:
	destroyed.emit()
	_spawn_scrap()
	queue_free()

func _spawn_scrap() -> void:
	var p_scene = load("res://scenes/entities/Powerup.tscn")
	if p_scene:
		var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
		for i in range(4):
			var scrap = p_scene.instantiate() as Powerup
			root.add_child(scrap)
			scrap.global_position = global_position + Vector2(randf_range(-35, 35), randf_range(-35, 35))
			scrap.setup(Powerup.PowerupType.SCRAP, 50)
