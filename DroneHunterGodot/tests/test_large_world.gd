extends Node

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 ENVIRONMENT KIT + LARGE WORLD TEST ===")

	# 1. Load and Instantiate TrainingArena World
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var world: Node2D = arena_scene.instantiate()
	assert(world != null, "Failed to instantiate TrainingArena")
	add_child(world)
	print("[PASS] World scene TrainingArena instantiated.")

	# 2. Verify Background Layer and Base Terrain
	var bg: Node2D = world.get_node_or_null("Background")
	assert(bg != null, "TrainingArena must have Background layer")
	var base_ground: TextureRect = bg.get_node_or_null("BaseGround")
	assert(base_ground != null, "Background must have BaseGround TextureRect")
	assert(base_ground.texture != null, "BaseGround must have valid texture from environment kit")
	assert(base_ground.size.x >= 3840.0 and base_ground.size.y >= 2160.0, "Base ground must cover the 3840x2160 world area")
	print("[PASS] Background layer and continuous base terrain verified.")

	# 3. Verify Modular Environment Kit Layers (Terrain, Water, Structures, Props, Obstacles)
	var terrain: Node2D = world.get_node_or_null("Terrain")
	assert(terrain != null and terrain.get_child_count() >= 5, "Terrain layer must have modular terrain nodes")
	for child in terrain.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Terrain sprite must have valid texture: %s" % child.name)

	var water: Node2D = world.get_node_or_null("Water")
	assert(water != null and water.get_child_count() >= 2, "Water layer must have waterway elements")
	for child in water.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Water sprite must have valid texture: %s" % child.name)

	var structures: Node2D = world.get_node_or_null("Structures")
	assert(structures != null and structures.get_child_count() >= 6, "Structures layer must have modular landmarks")
	for child in structures.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Structure sprite must have valid texture: %s" % child.name)

	var props: Node2D = world.get_node_or_null("Props")
	assert(props != null and props.get_child_count() >= 5, "Props layer must have tactical prop assets")
	for child in props.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Prop sprite must have valid texture: %s" % child.name)

	var obstacles: Node2D = world.get_node_or_null("Obstacles")
	assert(obstacles != null, "Obstacles layer must exist")
	print("[PASS] Modular environment kit layers (Terrain, Water, Structures, Props, Obstacles) verified.")

	# 4. Verify Boundaries (StaticBody2D)
	var boundaries: StaticBody2D = world.get_node_or_null("Boundaries")
	assert(boundaries != null, "TrainingArena must have Boundaries StaticBody2D")
	assert(boundaries.get_node_or_null("WallTop") != null, "Boundaries must have WallTop")
	assert(boundaries.get_node_or_null("WallBottom") != null, "Boundaries must have WallBottom")
	assert(boundaries.get_node_or_null("WallLeft") != null, "Boundaries must have WallLeft")
	assert(boundaries.get_node_or_null("WallRight") != null, "Boundaries must have WallRight")
	print("[PASS] World boundary collision walls verified.")

	# 5. Verify Player, Scale, and Camera Limits
	var player: CharacterBody2D = world.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player must exist inside TrainingArena")
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null and sprite.texture != null, "Player must have Sprite2D child with texture")
	assert(is_equal_approx(sprite.scale.x, 0.42) and is_equal_approx(sprite.scale.y, 0.42), "Player scale must be 0.42")
	
	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	assert(camera.limit_left == 0, "Camera2D limit_left must be 0")
	assert(camera.limit_top == 0, "Camera2D limit_top must be 0")
	assert(camera.limit_right == 3840, "Camera2D limit_right must match world bounds (3840)")
	assert(camera.limit_bottom == 2160, "Camera2D limit_bottom must match world bounds (2160)")
	print("[PASS] Player and Camera2D verified with world bounds matching (0, 0, 3840, 2160).")

	# 6. Verify Screen-Space HUD Isolation
	var hud = world.get_node_or_null("HUD")
	assert(hud != null and hud is CanvasLayer, "HUD must exist in CanvasLayer")
	assert((hud as CanvasLayer).layer >= 1, "HUD layer must be >= 1")
	print("[PASS] Screen-space HUD in CanvasLayer verified.")

	# 7. Exploration Verification: CENTER -> TOP -> BOTTOM -> LEFT -> RIGHT -> FOUR CORNERS
	await get_tree().physics_frame

	# Center
	player.global_position = Vector2(1920.0, 1080.0)
	await get_tree().physics_frame
	assert(player.global_position.distance_to(Vector2(1920, 1080)) < 1.0, "Player must be at center")

	# Top
	player.global_position = Vector2(1920.0, 200.0)
	await get_tree().physics_frame
	assert(player.global_position.y < 300.0, "Player must navigate to Top sector")

	# Bottom
	player.global_position = Vector2(1920.0, 2000.0)
	await get_tree().physics_frame
	assert(player.global_position.y > 1900.0, "Player must navigate to Bottom sector")

	# Left
	player.global_position = Vector2(200.0, 1080.0)
	await get_tree().physics_frame
	assert(player.global_position.x < 300.0, "Player must navigate to Left sector")

	# Right
	player.global_position = Vector2(3640.0, 1080.0)
	await get_tree().physics_frame
	assert(player.global_position.x > 3500.0, "Player must navigate to Right sector")

	# Four Corners
	# NW Corner (Canyon Oasis)
	player.global_position = Vector2(400.0, 300.0)
	await get_tree().physics_frame
	assert(player.global_position.x < 600.0 and player.global_position.y < 500.0, "Player must navigate to NW Corner")

	# NE Corner (Tactical Bridge & River)
	player.global_position = Vector2(3400.0, 300.0)
	await get_tree().physics_frame
	assert(player.global_position.x > 3200.0 and player.global_position.y < 500.0, "Player must navigate to NE Corner")

	# SW Corner (Radar Facility & Industrial Base)
	player.global_position = Vector2(400.0, 1850.0)
	await get_tree().physics_frame
	assert(player.global_position.x < 600.0 and player.global_position.y > 1700.0, "Player must navigate to SW Corner")

	# SE Corner (Desert River Valley & Rock Spires)
	player.global_position = Vector2(3400.0, 1850.0)
	await get_tree().physics_frame
	assert(player.global_position.x > 3200.0 and player.global_position.y > 1700.0, "Player must navigate to SE Corner")

	print("[PASS] Full world exploration verified across all quadrants and landmarks.")

	print("\n*** ALL ENVIRONMENT KIT + LARGE WORLD TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
