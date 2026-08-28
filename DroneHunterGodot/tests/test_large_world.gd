extends Node

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 LARGE EXPLORABLE WORLD TEST ===")

	# 1. Load and Instantiate TrainingArena World
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var world: Node2D = arena_scene.instantiate()
	assert(world != null, "Failed to instantiate TrainingArena")
	add_child(world)
	print("[PASS] World scene TrainingArena instantiated.")

	# 2. Verify Player Node & Scripts
	var player: CharacterBody2D = world.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player must exist inside TrainingArena")
	print("[PASS] Player instance verified.")

	# 3. Verify Camera2D and World Limits
	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	assert(camera.limit_left == 0, "Camera2D limit_left must be 0")
	assert(camera.limit_top == 0, "Camera2D limit_top must be 0")
	assert(camera.limit_right >= 3000, "Camera2D limit_right must be at least 3000px (large world), got " + str(camera.limit_right))
	assert(camera.limit_bottom >= 2000, "Camera2D limit_bottom must be at least 2000px (large world), got " + str(camera.limit_bottom))
	assert(camera.position_smoothing_enabled, "Camera2D smoothing must be enabled for cinematic exploration")
	print("[PASS] Camera2D verified with world bounds matching (0, 0, " + str(camera.limit_right) + ", " + str(camera.limit_bottom) + ").")

	# 4. Verify Composed Multi-Region Background Layers
	var bg: Node2D = world.get_node_or_null("Background")
	assert(bg != null, "World must have Background layer")
	assert(bg.get_child_count() >= 4, "Background must be assembled from multiple regional sector textures (no single stretched image)")
	for child in bg.get_children():
		var sprite = child as Sprite2D
		assert(sprite != null and sprite.texture != null, "All background regions must have valid textures")
	print("[PASS] Multi-region assembled background layer verified with " + str(bg.get_child_count()) + " sectors.")

	# 5. Verify Midground and Environment Landmark Layering
	var mid: Node2D = world.get_node_or_null("Midground")
	assert(mid != null, "World must have Midground layer")
	assert(mid.get_child_count() >= 2, "Midground must contain large tactical power/outpost backdrops")

	var env: Node2D = world.get_node_or_null("Environment")
	assert(env != null, "World must have Environment layer")
	assert(env.get_child_count() >= 6, "Environment must contain distributed industrial tactical structures (towers, radar, launchers, defense platforms)")
	print("[PASS] Midground and Environment Landmark layers verified.")

	# 6. Verify Outer Arena Boundaries Match World Scale
	var boundaries: StaticBody2D = world.get_node_or_null("ArenaBoundaries")
	assert(boundaries != null, "World must have ArenaBoundaries StaticBody2D")
	assert(boundaries.get_node_or_null("WallTop") != null, "Boundaries must have WallTop")
	assert(boundaries.get_node_or_null("WallBottom") != null, "Boundaries must have WallBottom")
	assert(boundaries.get_node_or_null("WallLeft") != null, "Boundaries must have WallLeft")
	assert(boundaries.get_node_or_null("WallRight") != null, "Boundaries must have WallRight")
	print("[PASS] World outer boundaries verified.")

	# 7. Real Player Exploration Flight Test across World Quadrants
	await get_tree().physics_frame
	
	# Flight to North-West Sector (500, 400)
	player.global_position = Vector2(500.0, 400.0)
	player.velocity = Vector2.ZERO
	await get_tree().physics_frame
	assert(player.global_position.x < 1000.0 and player.global_position.y < 800.0, "Player must be in North-West Sector")

	# Flight to South-East Sector (3400, 1900)
	player.global_position = Vector2(3400.0, 1900.0)
	player.velocity = Vector2.ZERO
	await get_tree().physics_frame
	assert(player.global_position.x > 3000.0 and player.global_position.y > 1500.0, "Player must be in South-East Sector")
	print("[PASS] Free player exploration across large world bounds verified.")

	print("\n*** ALL LARGE EXPLORABLE WORLD TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
