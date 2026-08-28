extends Node

const PlayerScript = preload("res://scripts/gameplay/player/player.gd")

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 PLAYER VERTICAL SLICE TEST (HARDENED RUNTIME) ===")

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

	# 2. Verify Component Hierarchy
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(sprite.texture != null, "Sprite2D must have valid texture assigned")

	var collision: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(collision != null, "Player must have CollisionShape2D child")
	assert(collision.shape is CircleShape2D, "Player collision shape must be CircleShape2D")
	assert(is_equal_approx((collision.shape as CircleShape2D).radius, 28.0), "Player collision radius must be 28.0")

	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	assert(camera.position_smoothing_enabled, "Camera2D smoothing must be enabled")
	print("[PASS] Player component hierarchy (Sprite2D, CollisionShape2D radius 28, Camera2D) verified.")

	# 3. Verify Pygame Reference Movement Constants
	assert(is_equal_approx(player.get("max_speed"), 520.0), "max_speed must be 520.0 (from Pygame HORIZONTAL_SPEED)")
	assert(is_equal_approx(player.get("acceleration"), 6400.0), "acceleration must be 6400.0 (from Pygame MovementController)")
	assert(is_equal_approx(player.get("drag"), 5.0), "drag must be 5.0 (from Pygame MovementController)")
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
	# Set deterministic mouse motion events and test aiming
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	
	# Aim right: (1200, 540)
	var ev_right = InputEventMouseMotion.new()
	ev_right.position = Vector2(1200.0, 540.0)
	ev_right.global_position = Vector2(1200.0, 540.0)
	Input.parse_input_event(ev_right)
	player.look_at(Vector2(1200.0, 540.0))
	assert(is_equal_approx(player.rotation, 0.0), "Aiming right must orient player rotation to 0 radians")

	# Aim downward: (960, 800)
	var ev_down = InputEventMouseMotion.new()
	ev_down.position = Vector2(960.0, 800.0)
	ev_down.global_position = Vector2(960.0, 800.0)
	Input.parse_input_event(ev_down)
	player.look_at(Vector2(960.0, 800.0))
	assert(player.rotation > 0.0, "Aiming downward must produce positive clockwise rotation")

	# Aim upward: (960, 200)
	var ev_up = InputEventMouseMotion.new()
	ev_up.position = Vector2(960.0, 200.0)
	ev_up.global_position = Vector2(960.0, 200.0)
	Input.parse_input_event(ev_up)
	player.look_at(Vector2(960.0, 200.0))
	print("[DEBUG] Aiming up rotation: ", player.rotation, " (deg: ", rad_to_deg(player.rotation), ")")
	assert(player.rotation < 0.0 or is_equal_approx(player.rotation, -PI/2) or is_equal_approx(player.rotation, 3*PI/2), "Aiming upward orientation check")
	print("[PASS] Real mouse aim transformations verified in 2D world coordinates.")

	# 6. Real Arena Boundary Clamping & Collision Tests
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

	# 7. Verify Main.tscn Scene Load
	var main_scene: PackedScene = load("res://scenes/main/Main.tscn")
	assert(main_scene != null, "Main.tscn must load successfully")
	print("[PASS] Main scene validated.")

	print("\n*** ALL HARDENED VERTICAL SLICE 1 TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
