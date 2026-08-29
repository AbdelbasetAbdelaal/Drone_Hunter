class_name EnemyHeavy
extends EnemyCore

var fire_timer: float = 1.0
var fire_rate: float = 2.4
var bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _process_ai(delta: float) -> void:
	if target and is_instance_valid(target):
		look_at(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		velocity = dir * base_speed
		move_and_slide()
		
		fire_timer -= delta
		if fire_timer <= 0.0:
			_fire_salvo()
			fire_timer = fire_rate

func _fire_salvo() -> void:
	if not bullet_scene or not is_inside_tree():
		return
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if not root:
		return
		
	var base_rot = global_rotation
	for offset_deg in [-15.0, 0.0, 15.0]:
		var proj = bullet_scene.instantiate() as Projectile
		root.add_child(proj)
		var spread_rot = base_rot + deg_to_rad(offset_deg)
		proj.global_position = global_position + Vector2.RIGHT.rotated(spread_rot) * 40.0
		proj.global_rotation = spread_rot
		proj.setup(380.0, 16.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
