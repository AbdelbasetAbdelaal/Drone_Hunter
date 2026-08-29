class_name EnemyShieldElite
extends EnemyCore

var fire_timer: float = 0.5
var fire_rate: float = 1.8
var protection_radius: float = 320.0
var bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _ready() -> void:
	max_hp = 100.0
	base_speed = 80.0
	base_armor = 0.15
	score_value = 350
	super._ready()

func _process_ai(delta: float) -> void:
	if not target or not is_instance_valid(target):
		return
		
	look_at(target.global_position)
	var dist = global_position.distance_to(target.global_position)
	var dir = (target.global_position - global_position).normalized()
	
	# Maintain 400px standoff distance
	if dist > 450.0:
		velocity = dir * base_speed
	elif dist < 350.0:
		velocity = -dir * base_speed * 0.8
	else:
		velocity = dir.orthogonal() * base_speed * 0.6
		
	move_and_slide()
	
	# Allied protection aura
	_protect_nearby_allies()
	
	fire_timer -= delta
	if fire_timer <= 0.0:
		_fire_pulse()
		fire_timer = fire_rate

func _protect_nearby_allies() -> void:
	var enemies = get_tree().get_nodes_in_group("enemy")
	for e in enemies:
		if e != self and is_instance_valid(e) and e is Node2D:
			var d = global_position.distance_to(e.global_position)
			if d <= protection_radius:
				# Provide protective shield buff to ally
				if "health" in e and e.health and e.health.current_shield < 25.0:
					e.health.current_shield = min(30.0, e.health.current_shield + 10.0 * get_physics_process_delta_time())

func _fire_pulse() -> void:
	if not bullet_scene or not is_inside_tree():
		return
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if not root:
		return
	var proj = bullet_scene.instantiate() as Projectile
	root.add_child(proj)
	proj.global_position = global_position + Vector2.RIGHT.rotated(global_rotation) * 35.0
	proj.global_rotation = global_rotation
	proj.setup(420.0, 14.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
