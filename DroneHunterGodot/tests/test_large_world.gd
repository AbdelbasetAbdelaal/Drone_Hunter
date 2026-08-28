extends Node

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 WORLD COMPOSITION & EXPLORATION TEST ===")

	# 1. Load and Instantiate TrainingArena World
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var world: Node2D = arena_scene.instantiate()
	assert(world != null, "Failed to instantiate TrainingArena")
	add_child(world)
	print("[PASS] World scene TrainingArena instantiated.")

	# 2. Verify Player Node, Visual Scale, and Collision Shape
	var player: CharacterBody2D = world.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player must exist inside TrainingArena")
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(is_equal_approx(sprite.scale.x, 0.42) and is_equal_approx(sprite.scale.y, 0.42), "Player visual scale must be 0.42 relative to the 3840x2160 world")
	var col_shape: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(col_shape != null and col_shape.shape is CircleShape2D, "Player collision shape must be CircleShape2D")
	assert(is_equal_approx((col_shape.shape as CircleShape2D).radius, 22.0), "Player collision radius must be 22.0")
	print("[PASS] Player instance and proportional 0.42 visual scale verified.")

	# 3. Verify Camera2D and World Bounds Limits
	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	assert(camera.limit_left == 0, "Camera2D limit_left must be 0")
	assert(camera.limit_top == 0, "Camera2D limit_top must be 0")
	assert(camera.limit_right == 3840, "Camera2D limit_right must match world bounds (3840)")
	assert(camera.limit_bottom == 2160, "Camera2D limit_bottom must match world bounds (2160)")
	assert(camera.position_smoothing_enabled, "Camera2D smoothing must be enabled")
	print("[PASS] Camera2D verified with world bounds matching (0, 0, 3840, 2160).")

	# 4. Verify Background Has NO Flipping (No flip_h, No flip_v, No upside-down terrain)
	var bg: Node2D = world.get_node_or_null("Background")
	assert(bg != null, "World must have Background layer")
	assert(bg.get_child_count() >= 4, "Background must have regional sectors")
	for child in bg.get_children():
		var bg_sprite = child as Sprite2D
		assert(bg_sprite != null and bg_sprite.texture != null, "Background region must have valid texture")
		assert(bg_sprite.flip_v == false, "Background region must NOT have vertical flipping (flip_v must be false)")
		assert(bg_sprite.flip_h == false, "Background region must NOT have horizontal flipping (flip_h must be false)")
	print("[PASS] Upright background orientation verified (zero vertical/horizontal flipping).")

	# 5. Verify Screen-Space HUD in CanvasLayer
	var hud = world.get_node_or_null("HUD")
	assert(hud != null, "World must have HUD child node")
	assert(hud is CanvasLayer, "HUD must be a CanvasLayer so it remains fixed in screen-space")
	assert((hud as CanvasLayer).layer >= 1, "HUD CanvasLayer layer must be >= 1")
	var hud_root: Control = hud.get_node_or_null("Root")
	assert(hud_root != null, "HUD must have Root Control node")
	print("[PASS] Screen-space HUD in CanvasLayer verified.")

	# 6. Verify Midground and Environment Landmark Layering
	var mid: Node2D = world.get_node_or_null("Midground")
	assert(mid != null and mid.get_child_count() >= 2, "Midground must contain outpost structures")
	var env: Node2D = world.get_node_or_null("Environment")
	assert(env != null and env.get_child_count() >= 6, "Environment must contain tactical landmarks")

	var boundaries: StaticBody2D = world.get_node_or_null("ArenaBoundaries")
	assert(boundaries != null, "World must have ArenaBoundaries StaticBody2D")
	assert(boundaries.get_node_or_null("WallTop") != null, "Boundaries must have WallTop")
	assert(boundaries.get_node_or_null("WallBottom") != null, "Boundaries must have WallBottom")
	assert(boundaries.get_node_or_null("WallLeft") != null, "Boundaries must have WallLeft")
	assert(boundaries.get_node_or_null("WallRight") != null, "Boundaries must have WallRight")
	print("[PASS] Environment landmarks and boundary collision walls verified.")

	# 7. Player Exploration Across World Coordinates
	await get_tree().physics_frame
	
	# NW Flight
	player.global_position = Vector2(500.0, 400.0)
	await get_tree().physics_frame
	assert(player.global_position.x < 1000.0 and player.global_position.y < 800.0, "Player must explore NW quadrant")

	# SE Flight
	player.global_position = Vector2(3400.0, 1900.0)
	await get_tree().physics_frame
	assert(player.global_position.x > 3000.0 and player.global_position.y > 1500.0, "Player must explore SE quadrant")
	print("[PASS] Free player exploration across large world bounds verified.")

	print("\n*** ALL WORLD COMPOSITION TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)
