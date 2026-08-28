class_name BossTitan
extends CharacterBody2D

signal boss_health_changed(current: float, max_val: float)
signal boss_defeated()

@export var max_health: float = 800.0
@export var base_armor: float = 0.25
@export var base_speed: float = 85.0

var current_phase: int = 1
var _attack_timer: float = 0.0
var _spawn_timer: float = 0.0
var _bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")
var _scout_scene: PackedScene = preload("res://scenes/enemies/EnemyScout.tscn")

var target: Node2D = null

@onready var health: Health = $Health
@onready var damage_receiver: DamageReceiver = $DamageReceiver
@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	add_to_group("enemy")
	add_to_group("boss")
	
	if health:
		health.max_hp = max_health
		health.current_hp = max_health
		health.base_armor = base_armor
		health.health_changed.connect(_on_health_changed)
		health.died.connect(_on_death)
		
	if damage_receiver:
		damage_receiver.health = health
		
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		target = players[0]

func _physics_process(delta: float) -> void:
	if not target or not is_instance_valid(target):
		var players = get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			target = players[0]
		return
		
	look_at(target.global_position)
	
	var dir = (target.global_position - global_position).normalized()
	var speed_mult = 1.6 if current_phase == 3 else 1.0
	velocity = dir * base_speed * speed_mult
	move_and_slide()
	
	_handle_phases(delta)

func _handle_phases(delta: float) -> void:
	if not health:
		return
		
	var hp_ratio = health.current_hp / health.max_hp
	if hp_ratio > 0.65:
		current_phase = 1
	elif hp_ratio > 0.30:
		current_phase = 2
	else:
		current_phase = 3
		
	_attack_timer -= delta
	if _attack_timer <= 0.0:
		_execute_attack()
		_attack_timer = 0.8 if current_phase == 3 else (1.2 if current_phase == 2 else 1.6)
		
	if current_phase >= 2:
		_spawn_timer -= delta
		if _spawn_timer <= 0.0:
			_spawn_escorts()
			_spawn_timer = 10.0

func _execute_attack() -> void:
	if not _bullet_scene or not target:
		return
		
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	var base_rot = global_rotation
	
	match current_phase:
		1:
			# Dual Plasma shot
			for offset_y in [-30.0, 30.0]:
				var proj = _bullet_scene.instantiate() as Projectile
				root.add_child(proj)
				proj.global_position = global_position + Vector2(40.0, offset_y).rotated(base_rot)
				proj.global_rotation = base_rot
				proj.setup(500.0, 20.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
		2:
			# 5-Way Missile Salvo
			for i in range(-2, 3):
				var spread_angle = base_rot + deg_to_rad(i * 15.0)
				var proj = _bullet_scene.instantiate() as Projectile
				root.add_child(proj)
				proj.global_position = global_position + Vector2.RIGHT.rotated(spread_angle) * 45.0
				proj.global_rotation = spread_angle
				proj.setup(550.0, 18.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
		3:
			# Berserk 8-Way Radial Spiral
			for i in range(8):
				var radial_angle = base_rot + (i * PI / 4.0)
				var proj = _bullet_scene.instantiate() as Projectile
				root.add_child(proj)
				proj.global_position = global_position + Vector2.RIGHT.rotated(radial_angle) * 45.0
				proj.global_rotation = radial_angle
				proj.setup(650.0, 16.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")

func _spawn_escorts() -> void:
	if not _scout_scene:
		return
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	for i in range(2):
		var scout = _scout_scene.instantiate() as Node2D
		root.add_child(scout)
		scout.global_position = global_position + Vector2(randf_range(-80, 80), randf_range(-80, 80))

func _on_health_changed(cur: float, max_val: float) -> void:
	boss_health_changed.emit(cur, max_val)

func _on_death() -> void:
	boss_defeated.emit()
	_spawn_loot()
	queue_free()

func _spawn_loot() -> void:
	var p_scene = load("res://scenes/entities/Powerup.tscn")
	if p_scene:
		var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
		if not root:
			return
		for i in range(10):
			var scrap = p_scene.instantiate() as Node2D
			if scrap:
				root.add_child(scrap)
				scrap.global_position = global_position + Vector2(randf_range(-60, 60), randf_range(-60, 60))
				if scrap.has_method("setup"):
					scrap.setup(4, 50) # 4 = SCRAP
		for t in [0, 1, 2]: # 0 = BATTERY, 1 = SHIELD, 2 = OVERCLOCK
			var powerup = p_scene.instantiate() as Node2D
			if powerup:
				root.add_child(powerup)
				powerup.global_position = global_position + Vector2(randf_range(-40, 40), randf_range(-40, 40))
				if powerup.has_method("setup"):
					powerup.setup(t)
