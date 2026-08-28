class_name AAPlatform
extends CharacterBody2D

signal destroyed()

@export var max_health: float = 160.0
@export var base_armor: float = 0.20
@export var fire_range: float = 750.0
@export var fire_rate: float = 1.2
@export var damage: float = 18.0

var _fire_timer: float = 0.0
var _bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

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
	var player = get_tree().get_first_node_in_group("player") as Node2D
	if not player or not is_instance_valid(player):
		return
		
	var dist = global_position.distance_to(player.global_position)
	if dist <= fire_range:
		look_at(player.global_position)
		_fire_timer -= delta
		if _fire_timer <= 0.0:
			_fire_burst(player.global_position)
			_fire_timer = fire_rate

func _fire_burst(target_pos: Vector2) -> void:
	if not _bullet_scene:
		return
		
	var proj = _bullet_scene.instantiate() as Projectile
	if not proj:
		return
		
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	root.add_child(proj)
	
	proj.global_position = global_position + Vector2.RIGHT.rotated(global_rotation) * 35.0
	proj.global_rotation = (target_pos - global_position).angle()
	proj.setup(600.0, damage, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")

func _on_death() -> void:
	destroyed.emit()
	_spawn_scrap()
	queue_free()

func _spawn_scrap() -> void:
	var p_scene = load("res://scenes/entities/Powerup.tscn")
	if p_scene:
		var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
		for i in range(5):
			var scrap = p_scene.instantiate() as Powerup
			root.add_child(scrap)
			scrap.global_position = global_position + Vector2(randf_range(-35, 35), randf_range(-35, 35))
			scrap.setup(Powerup.PowerupType.SCRAP, 50)
