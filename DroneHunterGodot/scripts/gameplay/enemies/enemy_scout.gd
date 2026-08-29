class_name EnemyScout
extends EnemyCore

enum State {
	APPROACH,
	STRAFE,
	TELEGRAPH,
	DIVE,
	RECOVER
}

var ai_state: State = State.APPROACH
var state_timer: float = 0.0
var dive_dir: Vector2 = Vector2.ZERO
var dive_target: Vector2 = Vector2.ZERO
var strafe_dir: float = 1.0
var recover_dir: Vector2 = Vector2.ZERO

const SCOUT_DIVE_SPEED: float = 410.0
const SCOUT_TELEGRAPH_TIME: float = 0.45
const SCOUT_DIVE_DURATION: float = 0.55
const SCOUT_RECOVER_TIME: float = 0.75
const SCOUT_STRAFE_DURATION: float = 1.40

func _ready() -> void:
	max_hp = 30.0
	base_speed = 210.0
	base_armor = 0.0
	contact_damage = 22.0
	score_value = 150
	strafe_dir = -1.0 if randf() < 0.5 else 1.0
	super._ready()

func _process_ai(delta: float) -> void:
	if not target or not is_instance_valid(target):
		return
		
	state_timer += delta
	var to_player = target.global_position - global_position
	var dist = to_player.length()
	var norm_to_player = to_player.normalized() if dist > 0.001 else Vector2.RIGHT
	
	match ai_state:
		State.APPROACH:
			velocity = norm_to_player * base_speed
			look_at(target.global_position)
			if dist <= 360.0 or state_timer >= 2.4:
				ai_state = State.STRAFE
				state_timer = 0.0
				strafe_dir = -1.0 if randf() < 0.5 else 1.0
				
		State.STRAFE:
			var lateral = Vector2(-norm_to_player.y, norm_to_player.x) * strafe_dir
			var radial_bias = 0.30 if dist > 300.0 else (-0.25 if dist < 200.0 else 0.0)
			var move_vec = (lateral + norm_to_player * radial_bias).normalized()
			velocity = move_vec * base_speed
			look_at(target.global_position)
			
			if state_timer >= SCOUT_STRAFE_DURATION:
				ai_state = State.TELEGRAPH
				state_timer = 0.0
				var player_vel = target.velocity if "velocity" in target else Vector2.ZERO
				dive_target = target.global_position + player_vel * 0.35
				var dive_vec = dive_target - global_position
				dive_dir = dive_vec.normalized() if dive_vec.length() > 0.001 else norm_to_player
				
		State.TELEGRAPH:
			velocity = dive_dir * (base_speed * 0.12)
			rotation = dive_dir.angle()
			if sprite:
				sprite.modulate = Color(1.8, 0.4, 0.4, 1.0)
			if state_timer >= SCOUT_TELEGRAPH_TIME:
				ai_state = State.DIVE
				state_timer = 0.0
				if sprite:
					sprite.modulate = Color.WHITE
					
		State.DIVE:
			velocity = dive_dir * SCOUT_DIVE_SPEED
			rotation = dive_dir.angle()
			if state_timer >= SCOUT_DIVE_DURATION:
				ai_state = State.RECOVER
				state_timer = 0.0
				var away_vec = global_position - target.global_position
				recover_dir = away_vec.normalized() if away_vec.length() > 0.001 else -dive_dir
				
		State.RECOVER:
			velocity = recover_dir * (base_speed * 0.85)
			rotation = recover_dir.angle()
			if state_timer >= SCOUT_RECOVER_TIME:
				ai_state = State.STRAFE
				state_timer = 0.0
				strafe_dir = -1.0 if randf() < 0.5 else 1.0
				
	move_and_slide()
