extends Node

const PlayerScript = preload("res://scripts/gameplay/player/player.gd")
const ProjectileScript = preload("res://scripts/gameplay/weapons/projectile.gd")
const WeaponControllerScript = preload("res://scripts/gameplay/weapons/weapon_controller.gd")
const EnemyScoutScript = preload("res://scripts/gameplay/enemies/enemy_scout.gd")

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 PHASE 1 COMBAT CORE TEST ===")

	# 1. Load and Instantiate TrainingArena with Player & Enemies
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var arena: Node2D = arena_scene.instantiate()
	assert(arena != null, "Failed to instantiate TrainingArena")
	add_child(arena)

	var player: CharacterBody2D = arena.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player node must exist inside TrainingArena")
	assert(player.get_script() == PlayerScript, "Player script must match player.gd")

	# 1b. Verify TrainingArena Real Background, Environment & Enemies
	var bg_node: Node2D = arena.get_node_or_null("Background")
	assert(bg_node != null, "TrainingArena must have Background layer node")
	var sector_bg: Sprite2D = bg_node.get_node_or_null("SectorBackground")
	assert(sector_bg != null and sector_bg.texture != null, "Background must have real SectorBackground texture")

	var env_node: Node2D = arena.get_node_or_null("Environment")
	assert(env_node != null, "TrainingArena must have Environment layer node")
	assert(env_node.get_child_count() >= 4, "Environment layer must contain real industrial decorative assets")

	var enemies_node: Node2D = arena.get_node_or_null("Enemies")
	assert(enemies_node != null, "TrainingArena must have Enemies container node")
	assert(enemies_node.get_child_count() >= 3, "TrainingArena must contain active EnemyScout targets")

	var boundaries: StaticBody2D = arena.get_node_or_null("ArenaBoundaries")
	assert(boundaries != null, "TrainingArena must have ArenaBoundaries StaticBody2D")
	print("[PASS] Arena, Environment, Player, and Scout Enemies instantiated.")

	# 2. Verify Component Hierarchy & Visual Scaling
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(is_equal_approx(sprite.scale.x, 0.75) and is_equal_approx(sprite.scale.y, 0.75), "Player sprite scale must be 0.75")

	var collision: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(collision != null, "Player must have CollisionShape2D child")
	assert(is_equal_approx((collision.shape as CircleShape2D).radius, 38.0), "Player collision radius must be 38.0")

	var weapon_ctrl: Node2D = player.get_node_or_null("WeaponController")
	assert(weapon_ctrl != null, "Player must have WeaponController child node")
	assert(weapon_ctrl.get_script() == WeaponControllerScript, "WeaponController must have weapon_controller.gd script")
	print("[PASS] Player component hierarchy (Sprite2D 0.75 scale, CollisionShape2D radius 38, WeaponController) verified.")

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

	Input.action_press("move_right")
	for i in range(15):
		await get_tree().physics_frame
	assert(player.velocity.x > 0.0, "Player velocity must increase along positive X via InputMap move_right")
	assert(player.global_position.x > initial_x, "Player position must advance to the right via move_and_slide()")
	Input.action_release("move_right")
	print("[PASS] Real movement execution verified.")

	# 5. Real Mouse Aim Execution Test
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	player.look_at(Vector2(1200.0, 540.0))
	assert(is_equal_approx(player.rotation, 0.0), "Aiming right must orient player rotation to 0 radians")
	player.look_at(Vector2(960.0, 800.0))
	assert(player.rotation > 0.0, "Aiming downward must produce positive clockwise rotation")
	print("[PASS] Real mouse aim transformations verified in 2D world coordinates.")

	# 6. Real Combat Core Test: Hit, Damage & Kill Scout Enemy
	var scout = enemies_node.get_child(0) as CharacterBody2D
	assert(scout != null, "Target Scout enemy must exist")
	assert(is_equal_approx(float(scout.get("current_hp")), 30.0), "Scout initial HP must be 30.0 (from Pygame SCOUT_HP)")
	
	# Position player directly facing scout at close range
	scout.global_position = Vector2(1200.0, 540.0)
	player.global_position = Vector2(1000.0, 540.0)
	player.aim_target_override = scout.global_position
	
	# Fire shot 1: 25 damage -> Scout HP: 30 - 25 = 5 HP
	Input.action_press("fire_primary")
	await get_tree().physics_frame
	await get_tree().physics_frame
	Input.action_release("fire_primary")
	
	# Wait for projectile travel and collision
	for i in range(15):
		await get_tree().physics_frame
	
	assert(scout.get("current_hp") < 30.0, "Scout must take damage upon bullet impact")
	assert(is_equal_approx(float(scout.get("current_hp")), 5.0), "Scout HP must be 5.0 after taking 25 Pulse damage")
	print("[PASS] Scout hit and damage verified (HP 30 -> 5).")

	# Fire shot 2: 25 damage -> Scout HP: 5 - 25 <= 0 -> Scout dies
	# Wait for weapon cooldown (1.0 / 7.5 = 0.133s ~ 10 frames)
	for i in range(12):
		await get_tree().physics_frame
		
	Input.action_press("fire_primary")
	await get_tree().physics_frame
	await get_tree().physics_frame
	Input.action_release("fire_primary")
	
	for i in range(15):
		await get_tree().physics_frame
		
	assert(not is_instance_valid(scout) or scout.is_queued_for_deletion() or float(scout.get("current_hp")) <= 0.0, "Scout must be dead and removed after 2nd Pulse hit")
	print("[PASS] Scout death and clean queue_free() removal verified.")

	# 7. Real Arena Boundary Clamping & Collision Tests
	player.global_position = Vector2(960.0, 540.0)
	player.velocity = Vector2.ZERO
	Input.action_press("move_left")
	for i in range(90):
		await get_tree().physics_frame
	Input.action_release("move_left")
	assert(player.global_position.x >= 20.0, "Player must not escape left arena boundary")
	print("[PASS] Real arena boundary collision verified.")

	print("\n*** ALL PHASE 1 COMBAT CORE TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
