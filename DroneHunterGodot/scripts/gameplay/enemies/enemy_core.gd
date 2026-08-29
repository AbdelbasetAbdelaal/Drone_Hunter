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
var _stun_timer: float = 0.0

var explosion_scene: PackedScene = preload("res://scenes/vfx/ExplosionVFX.tscn")

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

func apply_emp_stun(duration: float) -> void:
	_stun_timer = max(_stun_timer, duration)
	if sprite:
		sprite.modulate = Color(0.4, 0.9, 2.5, 1.0)

func _on_death() -> void:
	_spawn_explosion()
	_spawn_drops()
	queue_free()

func _spawn_explosion() -> void:
	if not is_inside_tree() or not explosion_scene:
		return
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if root:
		var exp_node = explosion_scene.instantiate() as Node2D
		root.add_child(exp_node)
		exp_node.global_position = global_position

func _spawn_drops() -> void:
	var powerup_scene = load("res://scenes/entities/Powerup.tscn")
	if not powerup_scene:
		return
		
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if not root:
		return
		
	# Always drop Scrap (type 4)
	var scrap = powerup_scene.instantiate() as Node2D
	if scrap:
		root.add_child(scrap)
		scrap.global_position = global_position + Vector2(randf_range(-15, 15), randf_range(-15, 15))
		if scrap.has_method("setup"):
			scrap.setup(4, int(score_value / 3))
	
	# Chance for tactical powerup (25%)
	if randf() < 0.25:
		var extra = powerup_scene.instantiate() as Node2D
		if extra:
			root.add_child(extra)
			extra.global_position = global_position + Vector2(randf_range(-20, 20), randf_range(-20, 20))
			var types = [0, 1, 2, 5] # BATTERY, SHIELD, OVERCLOCK, WINGMAN
			var chosen = types[randi() % types.size()]
			if extra.has_method("setup"):
				extra.setup(chosen)

func _physics_process(delta: float) -> void:
	if _stun_timer > 0.0:
		_stun_timer -= delta
		velocity = velocity.move_toward(Vector2.ZERO, 350.0 * delta)
		move_and_slide()
		if _stun_timer <= 0.0 and sprite:
			sprite.modulate = Color.WHITE
		return
		
	_process_ai(delta)

func _process_ai(_delta: float) -> void:
	# Virtual method to be overridden by AI controllers
	pass
