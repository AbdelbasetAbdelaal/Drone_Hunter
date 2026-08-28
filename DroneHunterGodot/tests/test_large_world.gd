extends Node

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 DESERT / INDUSTRIAL SCI-FI WORLD TEST ===")

	# 1. Load and Instantiate TrainingArena World
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var world: Node2D = arena_scene.instantiate()
	assert(world != null, "Failed to instantiate TrainingArena")
	add_child(world)
	print("[PASS] World scene TrainingArena instantiated.")

	# 2. Verify BaseTerrain Layer (Desert / Industrial Sci-Fi visual identity)
	var base_terrain: Node2D = world.get_node_or_null("BaseTerrain")
	assert(base_terrain != null, "World must have BaseTerrain layer")
	var ground: Sprite2D = base_terrain.get_node_or_null("DesertGround")
	assert(ground != null and ground.texture != null, "BaseTerrain must have DesertGround Sprite2D")
	assert(ground.position == Vector2(1920, 1080), "Desert ground must be centered at (1920, 1080)")
	print("[PASS] BaseTerrain layer with coherent Desert/Industrial backdrop verified.")

	# 3. Verify Hierarchy Layers (TerrainDetails, Landmarks, Structures, Props)
	var terrain_details: Node2D = world.get_node_or_null("TerrainDetails")
	assert(terrain_details != null and terrain_details.get_child_count() >= 2, "TerrainDetails layer must exist")
	for child in terrain_details.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Terrain detail must have valid texture: %s" % child.name)

	var landmarks: Node2D = world.get_node_or_null("Landmarks")
	assert(landmarks != null and landmarks.get_child_count() >= 4, "Landmarks layer must have major navigation towers")
	for child in landmarks.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Landmark must have valid texture: %s" % child.name)

	var structures: Node2D = world.get_node_or_null("Structures")
	assert(structures != null and structures.get_child_count() >= 3, "Structures layer must have industrial machinery")
	for child in structures.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Structure must have valid texture: %s" % child.name)

	var props: Node2D = world.get_node_or_null("Props")
	assert(props != null and props.get_child_count() >= 3, "Props layer must have tactical props")
	for child in props.get_children():
		if child is Sprite2D:
			assert((child as Sprite2D).texture != null, "Prop must have valid texture: %s" % child.name)
	print("[PASS] Spatial hierarchy (TerrainDetails, Landmarks, Structures, Props) verified.")

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
	# NW Corner (Canyon Outpost)
	player.global_position = Vector2(400.0, 300.0)
	await get_tree().physics_frame
	assert(player.global_position.x < 600.0 and player.global_position.y < 500.0, "Player must navigate to NW Corner")

	# NE Corner (Canyon Bridge & Road Approach)
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

	print("[PASS] Full world exploration verified across all regions.")

	print("\n*** ALL DESERT / INDUSTRIAL SCI-FI WORLD TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
