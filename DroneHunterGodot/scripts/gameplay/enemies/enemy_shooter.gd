class_name EnemyShooter
extends EnemyCore

enum State {
	APPROACH,
	POSITION,
	AIM,
	TELEGRAPH,
	FIRE,
	REPOSITION
}

var ai_state: State = State.APPROACH
var state_timer: float = 0.0
var fire_timer: float = 0.0
var strafe_dir: float = 1.0
var reposition_dir: Vector2 = Vector2.ZERO
var aim_target: Vector2 = Vector2.ZERO

const SHOOTER_PREFERRED_DISTANCE: float = 470.0
const SHOOTER_FIRE_COOLDOWN: float = 1.50
const SHOOTER_TELEGRAPH_TIME: float = 0.55
const SHOOTER_REPOSITION_TIME: float = 0.90
const SHOOTER_PROJECTILE_DAMAGE: float = 12.0
const SHOOTER_PROJECTILE_SPEED: float = 340.0

var bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _ready() -> void:
	max_hp = 55.0
	base_speed = 120.0
	base_armor = 0.0
	score_value = 250
	strafe_dir = -1.0 if randf() < 0.5 else 1.0
	super._ready()

func _process_ai(delta: float) -> void:
	if not target or not is_instance_valid(target):
		return
		
	state_timer += delta
	fire_timer += delta
	var to_player = target.global_position - global_position
	var dist = to_player.length()
	var norm_to_player = to_player.normalized() if dist > 0.001 else Vector2.RIGHT
	
	match ai_state:
		State.APPROACH:
			velocity = norm_to_player * base_speed
			look_at(target.global_position)
			if dist <= SHOOTER_PREFERRED_DISTANCE + 50.0:
				ai_state = State.POSITION
				state_timer = 0.0
				
		State.POSITION:
			var move_dir: Vector2 = Vector2.ZERO
			if dist > 550.0:
				move_dir = norm_to_player
			elif dist < 300.0:
				move_dir = -norm_to_player
			else:
				var lateral = Vector2(-norm_to_player.y, norm_to_player.x) * strafe_dir
				move_dir = lateral
				
			velocity = move_dir.normalized() * (base_speed * 0.75)
			look_at(target.global_position)
			
			if fire_timer >= SHOOTER_FIRE_COOLDOWN:
				ai_state = State.AIM
				state_timer = 0.0
				
		State.AIM:
			var player_vel = target.velocity if "velocity" in target else Vector2.ZERO
			aim_target = target.global_position + player_vel * 0.25
			var aim_vec = aim_target - global_position
			rotation = aim_vec.angle()
			ai_state = State.TELEGRAPH
			state_timer = 0.0
			
		State.TELEGRAPH:
			velocity = Vector2.ZERO
			var aim_vec = aim_target - global_position
			rotation = aim_vec.angle()
			if sprite:
				sprite.modulate = Color(1.8, 1.2, 0.4, 1.0)
			if state_timer >= SHOOTER_TELEGRAPH_TIME:
				ai_state = State.FIRE
				state_timer = 0.0
				if sprite:
					sprite.modulate = Color.WHITE
					
		State.FIRE:
			_fire_shot()
			fire_timer = 0.0
			ai_state = State.REPOSITION
			state_timer = 0.0
			if dist < 350.0:
				reposition_dir = -norm_to_player
			else:
				strafe_dir = -strafe_dir
				var lateral = Vector2(-norm_to_player.y, norm_to_player.x) * strafe_dir
				reposition_dir = lateral.normalized()
				
		State.REPOSITION:
			velocity = reposition_dir * base_speed
			look_at(target.global_position)
			if state_timer >= SHOOTER_REPOSITION_TIME:
				ai_state = State.POSITION
				state_timer = 0.0
				
	move_and_slide()

func _fire_shot() -> void:
	if not bullet_scene or not is_inside_tree():
		return
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if not root:
		return
	var proj = bullet_scene.instantiate() as Projectile
	root.add_child(proj)
	proj.global_position = global_position + Vector2.RIGHT.rotated(global_rotation) * 34.0
	proj.global_rotation = global_rotation
	proj.setup(SHOOTER_PROJECTILE_SPEED, SHOOTER_PROJECTILE_DAMAGE, Hit.DamageType.NORMAL, self, "projectiles/enemy_bullet.png")
