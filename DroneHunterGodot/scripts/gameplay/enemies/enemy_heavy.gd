class_name EnemyHeavy
extends EnemyCore

enum State {
	APPROACH,
	PRESSURE,
	RECOVER
}

var ai_state: State = State.APPROACH
var state_timer: float = 0.0
var fire_timer: float = 1.0
var strafe_dir: float = 1.0
var recover_dir: Vector2 = Vector2.ZERO

const HEAVY_PRESSURE_DISTANCE: float = 300.0
const HEAVY_FIRE_COOLDOWN: float = 2.40

var bullet_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _ready() -> void:
	max_hp = 180.0
	base_speed = 65.0
	base_armor = 0.20
	contact_damage = 30.0
	score_value = 500
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
			if dist <= HEAVY_PRESSURE_DISTANCE:
				ai_state = State.PRESSURE
				state_timer = 0.0
				
		State.PRESSURE:
			velocity = norm_to_player * (base_speed * 1.15)
			look_at(target.global_position)
			if state_timer >= 2.5 or dist > HEAVY_PRESSURE_DISTANCE + 120.0:
				ai_state = State.RECOVER
				state_timer = 0.0
				var lateral = Vector2(-norm_to_player.y, norm_to_player.x) * strafe_dir
				recover_dir = (norm_to_player * 0.4 + lateral * 0.6).normalized()
				
		State.RECOVER:
			velocity = recover_dir * (base_speed * 0.65)
			look_at(target.global_position)
			if state_timer >= 0.85:
				ai_state = State.APPROACH
				state_timer = 0.0
				strafe_dir = -1.0 if randf() < 0.5 else 1.0

	if fire_timer >= HEAVY_FIRE_COOLDOWN:
		_fire_salvo()
		fire_timer = 0.0
		
	move_and_slide()

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
