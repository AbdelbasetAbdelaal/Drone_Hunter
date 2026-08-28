class_name EnemyShooter
extends EnemyCore

@export var preferred_distance: float = 470.0

var fire_timer: float = 0.0
var fire_rate: float = 1.5
var bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _process_ai(delta: float) -> void:
	if target and is_instance_valid(target):
		look_at(target.global_position)
		var dist = global_position.distance_to(target.global_position)
		var dir = (target.global_position - global_position).normalized()
		
		# Keep distance
		if dist > preferred_distance + 50:
			velocity = dir * base_speed
		elif dist < preferred_distance - 50:
			velocity = -dir * base_speed
		else:
			velocity = Vector2.ZERO
			
		move_and_slide()
		
		fire_timer -= delta
		if fire_timer <= 0.0:
			_fire()
			fire_timer = fire_rate

func _fire() -> void:
	if bullet_scene:
		var proj = bullet_scene.instantiate() as Projectile
		var root_node = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
		root_node.add_child(proj)
		proj.global_position = global_position + Vector2.RIGHT.rotated(global_rotation) * 30.0
		proj.global_rotation = global_rotation
		proj.setup(340.0, 12.0, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
