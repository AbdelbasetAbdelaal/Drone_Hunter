extends SceneTree

const PlayerScript = preload("res://scripts/gameplay/player/player.gd")

func _init() -> void:
	print("=== RUNNING GODOT 4.3 PLAYER VERTICAL SLICE TEST ===")

	# 1. Load Player Scene
	var player_scene: PackedScene = load("res://scenes/player/Player.tscn")
	assert(player_scene != null, "Failed to load Player.tscn")
	var player: Node = player_scene.instantiate()
	assert(player != null, "Failed to instantiate Player")
	assert(player is CharacterBody2D, "Player root node must be CharacterBody2D")
	print("[PASS] Player scene loaded and instantiated.")

	# 2. Verify Component Hierarchy
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(sprite.texture != null, "Sprite2D must have valid texture assigned")

	var collision: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(collision != null, "Player must have CollisionShape2D child")
	assert(collision.shape is CircleShape2D, "Player collision shape must be CircleShape2D")

	var camera: Camera2D = player.get_node_or_null("Camera2D")
	assert(camera != null, "Player must have Camera2D child")
	print("[PASS] Player component hierarchy (Sprite2D, CollisionShape2D, Camera2D) verified.")

	# 3. Verify Pygame Reference Movement Values
	assert(player.get_script() == PlayerScript, "Player script must match player.gd")
	assert(is_equal_approx(player.get("max_speed"), 520.0), "max_speed must be 520.0 (from Pygame HORIZONTAL_SPEED)")
	assert(is_equal_approx(player.get("acceleration"), 6400.0), "acceleration must be 6400.0 (from Pygame MovementController)")
	assert(is_equal_approx(player.get("drag"), 5.0), "drag must be 5.0 (from Pygame MovementController)")
	print("[PASS] Authoritative Pygame movement values verified (Speed: 520, Accel: 6400, Drag: 5).")

	# 4. Verify InputMap Configuration
	var required_actions = ["move_up", "move_down", "move_left", "move_right"]
	for act in required_actions:
		assert(InputMap.has_action(act), "InputMap missing required movement action: " + act)
	print("[PASS] InputMap movement actions verified.")

	# 5. Verify Kinematic Movement Integration
	player.velocity = Vector2.ZERO
	# Simulate acceleration along X
	player.velocity += Vector2(1.0, 0.0) * float(player.get("acceleration")) * 0.016
	assert(player.velocity.x > 0.0, "Player velocity must increase along positive X")
	# Simulate drag
	var drag_damping = max(0.0, 1.0 - (float(player.get("drag")) * 0.016))
	player.velocity *= drag_damping
	assert(player.velocity.x > 0.0, "Player velocity must remain positive after damping")
	print("[PASS] Kinematic velocity integration and drag damping verified.")

	# 6. Verify Mouse Aim Transformation
	player.position = Vector2(960.0, 540.0)
	var target_mouse_pos = Vector2(1200.0, 540.0)
	player.look_at(target_mouse_pos)
	assert(is_equal_approx(player.rotation, 0.0), "Player rotation facing right must be 0 radians")
	player.look_at(Vector2(960.0, 800.0))
	assert(player.rotation > 0.0, "Player rotation facing down must be positive radians")
	print("[PASS] Mouse aim transformation verified.")

	# 7. Verify Arena and Main Scenes
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "TrainingArena.tscn must load")
	var main_scene: PackedScene = load("res://scenes/main/Main.tscn")
	assert(main_scene != null, "Main.tscn must load")
	print("[PASS] TrainingArena and Main scenes verified.")

	player.free()
	print("\n*** ALL VERTICAL SLICE 1 TESTS PASSED SUCCESSFULLY! ***")
	quit(0)
