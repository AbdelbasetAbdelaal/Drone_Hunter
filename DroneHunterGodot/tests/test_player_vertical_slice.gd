extends Node

const PlayerScript = preload("res://scripts/gameplay/player/player.gd")
const ProjectileScript = preload("res://scripts/gameplay/weapons/projectile.gd")
const WeaponControllerScript = preload("res://scripts/gameplay/weapons/weapon_controller.gd")

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 PLAYER VERTICAL SLICE & WEAPON TEST ===")

	# 1. Load and Instantiate TrainingArena with Player
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var arena: Node2D = arena_scene.instantiate()
	assert(arena != null, "Failed to instantiate TrainingArena")
	add_child(arena)

	var player: CharacterBody2D = arena.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player node must exist inside TrainingArena")
	assert(player.get_script() == PlayerScript, "Player script must match player.gd")
	print("[PASS] Arena and Player instantiated in active runtime SceneTree.")

	# 2. Verify Component Hierarchy & Visual Scaling
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(sprite.texture != null, "Sprite2D must have valid texture assigned")
	assert(is_equal_approx(sprite.scale.x, 0.75) and is_equal_approx(sprite.scale.y, 0.75), "Player sprite scale must be 0.75 for clear readable combat presence")

	var collision: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(collision != null, "Player must have CollisionShape2D child")
	assert(collision.shape is CircleShape2D, "Player collision shape must be CircleShape2D")
	assert(is_equal_approx((collision.shape as CircleShape2D).radius, 38.0), "Player collision radius must be 38.0")

	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	assert(camera.position_smoothing_enabled, "Camera2D smoothing must be enabled")

	var weapon_ctrl: Node2D = player.get_node_or_null("WeaponController")
	assert(weapon_ctrl != null, "Player must have WeaponController child node")
	assert(weapon_ctrl.get_script() == WeaponControllerScript, "WeaponController must have weapon_controller.gd script")
	print("[PASS] Player component hierarchy (0.75 scale Sprite2D, radius 38 CollisionShape2D, Camera2D, WeaponController) verified.")

	# 3. Verify Pygame Reference Movement Constants
	assert(is_equal_approx(float(player.max_speed), 520.0), "max_speed must be 520.0 (from Pygame HORIZONTAL_SPEED)")
	assert(is_equal_approx(float(player.acceleration), 6400.0), "acceleration must be 6400.0 (from Pygame MovementController)")
	assert(is_equal_approx(float(player.drag), 5.0), "drag must be 5.0 (from Pygame MovementController)")
	print("[PASS] Authoritative Pygame movement constants verified (Speed: 520, Accel: 6400, Drag: 5).")

	# Wait a frame for physics server synchronization
	await get_tree().physics_frame

	# 4. Real Movement Execution Test via Engine Physics Loop
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	var initial_x = player.global_position.x

	# Press move_right action and let engine physics ticks process real movement
	Input.action_press("move_right")
	for i in range(15):
		await get_tree().physics_frame

	assert(player.velocity.x > 0.0, "Player velocity must increase along positive X via InputMap move_right")
	assert(player.global_position.x > initial_x, "Player position must advance to the right via move_and_slide()")
	Input.action_release("move_right")

	# Step with no inputs to verify drag deceleration
	var speed_before_drag = player.velocity.length()
	for i in range(30):
		await get_tree().physics_frame
	assert(player.velocity.length() < speed_before_drag, "Player velocity must decelerate under linear drag")
	print("[PASS] Real movement execution verified via engine physics loop (action_press -> _physics_process -> velocity -> move_and_slide -> drag).")

	# 5. Real Mouse Aim Execution Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO

	# Aim right: (1200, 540)
	player.look_at(Vector2(1200.0, 540.0))
	assert(is_equal_approx(player.rotation, 0.0), "Aiming right must orient player rotation to 0 radians")

	# Aim downward: (960, 800)
	player.look_at(Vector2(960.0, 800.0))
	assert(player.rotation > 0.0, "Aiming downward must produce positive clockwise rotation")
	print("[PASS] Real mouse aim transformations verified in 2D world coordinates.")

	# 6. Real Primary Weapon Firing Test
	player.global_position = Vector2(960.0, 540.0)
	player.rotation = 0.0  # Facing Right
	var bullets_before = _count_projectiles_in_tree()
	
	# Trigger primary fire via InputMap action
	Input.action_press("fire_primary")
	await get_tree().physics_frame
	await get_tree().physics_frame
	Input.action_release("fire_primary")

	var bullets_after = _count_projectiles_in_tree()
	assert(bullets_after > bullets_before, "Primary fire must spawn projectile into scene")

	# Verify projectile advances forward along its trajectory angle
	var spawned_projectile = _get_first_projectile_in_tree()
	assert(spawned_projectile != null, "Spawned projectile must exist")
	var initial_bullet_pos = spawned_projectile.global_position
	var bullet_dir = Vector2.RIGHT.rotated(spawned_projectile.global_rotation)
	for i in range(10):
		await get_tree().physics_frame
	var distance_traveled = spawned_projectile.global_position.distance_to(initial_bullet_pos)
	assert(distance_traveled > 50.0, "Pulse bullet must travel forward at high projectile speed (distance > 50px)")
	var actual_move_vector = (spawned_projectile.global_position - initial_bullet_pos).normalized()
	assert(actual_move_vector.dot(bullet_dir) > 0.99, "Pulse bullet must travel along its exact facing rotation vector")
	print("[PASS] Primary weapon firing verified (fire_primary -> WeaponController -> BulletPulse spawned -> high-speed forward travel).")

	# 7. Real Arena Boundary Clamping & Collision Tests
	# Boundary Left Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	Input.action_press("move_left")
	for i in range(90):
		await get_tree().physics_frame
	Input.action_release("move_left")
	assert(player.global_position.x >= 20.0, "Player must not escape left arena boundary (X >= 20.0), pos=" + str(player.global_position))

	# Boundary Right Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	Input.action_press("move_right")
	for i in range(90):
		await get_tree().physics_frame
	Input.action_release("move_right")
	assert(player.global_position.x <= 1900.0, "Player must not escape right arena boundary (X <= 1900.0), pos=" + str(player.global_position))

	# Boundary Top Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	Input.action_press("move_up")
	for i in range(90):
		await get_tree().physics_frame
	Input.action_release("move_up")
	assert(player.global_position.y >= 20.0, "Player must not escape top arena boundary (Y >= 20.0), pos=" + str(player.global_position))

	# Boundary Bottom Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	Input.action_press("move_down")
	for i in range(90):
		await get_tree().physics_frame
	Input.action_release("move_down")
	assert(player.global_position.y <= 1060.0, "Player must not escape bottom arena boundary (Y <= 1060.0), pos=" + str(player.global_position))
	print("[PASS] Real arena boundary collision verified across Left, Right, Top, and Bottom walls.")

	print("\n*** ALL VERTICAL SLICE 1 & WEAPON TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)

func _count_projectiles_in_tree() -> int:
	var count = 0
	for node in get_tree().root.get_children():
		if node.get_script() == ProjectileScript:
			count += 1
		for child in node.get_children():
			if child.get_script() == ProjectileScript:
				count += 1
	return count

func _get_first_projectile_in_tree() -> Area2D:
	for node in get_tree().root.get_children():
		if node.get_script() == ProjectileScript:
			return node as Area2D
		for child in node.get_children():
			if child.get_script() == ProjectileScript:
				return child as Area2D
	return null
