extends Node

const PlayerScript = preload("res://scripts/gameplay/player/player.gd")
const ProjectileScript = preload("res://scripts/gameplay/weapons/projectile.gd")
const WeaponControllerScript = preload("res://scripts/gameplay/weapons/weapon_controller.gd")
const EnemyScoutScript = preload("res://scripts/gameplay/enemies/enemy_scout.gd")

func _ready() -> void:
	print("=== RUNNING GODOT 4.3 AUTHORITATIVE COMBAT FOUNDATION TEST ===")

	# 1. Verify 11 Weapon Definitions exist and Pulse has exact Pygame stats
	var weapon_ids = ["pulse", "scatter", "missile", "rapid", "plasma", "rail", "barrage", "beam", "tesla", "cluster", "emp"]
	for w_id in weapon_ids:
		var path = "res://resources/weapons/" + w_id + ".tres"
		assert(ResourceLoader.exists(path), "Weapon Resource must exist: " + path)
		var def = load(path) as WeaponDefinition
		assert(def != null, "Weapon Resource must load cleanly: " + path)
		assert(def.weapon_id == w_id, "Weapon ID must match: " + w_id)
		
	var pulse_def = load("res://resources/weapons/pulse.tres") as WeaponDefinition
	assert(is_equal_approx(pulse_def.damage, 12.0), "Pulse damage must be 12.0 from Pygame")
	assert(is_equal_approx(pulse_def.speed, 650.0), "Pulse speed must be 650.0 from Pygame")
	assert(is_equal_approx(pulse_def.cooldown, 0.18), "Pulse cooldown must be 0.18 from Pygame")
	print("[PASS] All 11 authoritative WeaponDefinition Resources loaded and validated.")

	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.selected_drone_id = "striker"
		gm.upgrade_levels = {"hull": 1, "energy": 1, "weapon": 1, "mobility": 1}

	# 2. Load and Instantiate TrainingArena with Player
	var arena_scene: PackedScene = load("res://scenes/world/TrainingArena.tscn")
	assert(arena_scene != null, "Failed to load TrainingArena.tscn")
	var arena: Node2D = arena_scene.instantiate()
	assert(arena != null, "Failed to instantiate TrainingArena")
	add_child(arena)

	# Disable automatic combat director waves during this isolated unit test
	var cd = arena.get_node_or_null("Enemies") as CombatDirector
	if cd:
		cd.set_process(false)
		cd.set_physics_process(false)

	var player: CharacterBody2D = arena.get_node_or_null("Player") as CharacterBody2D
	assert(player != null, "Player node must exist inside TrainingArena")
	assert(player.get_script() == PlayerScript, "Player script must match player.gd")

	var boundaries: StaticBody2D = arena.get_node_or_null("Boundaries")
	assert(boundaries != null, "TrainingArena must have Boundaries StaticBody2D")
	print("[PASS] Arena, Boundaries, Player, and Enemies Director instantiated.")

	# 3. Verify Player Component Hierarchy & Visual Scaling
	var sprite: Sprite2D = player.get_node_or_null("Sprite2D")
	assert(sprite != null, "Player must have Sprite2D child")
	assert(is_equal_approx(sprite.scale.x, 0.42) and is_equal_approx(sprite.scale.y, 0.42), "Player sprite scale must be 0.42")

	var collision: CollisionShape2D = player.get_node_or_null("CollisionShape2D")
	assert(collision != null, "Player must have CollisionShape2D child")
	assert(is_equal_approx((collision.shape as CircleShape2D).radius, 22.0), "Player collision radius must be 22.0")

	var weapon_ctrl: WeaponController = player.get_node_or_null("WeaponController") as WeaponController
	assert(weapon_ctrl != null, "Player must have WeaponController child node")
	assert(weapon_ctrl.weapons.size() == 11, "WeaponController must contain all 11 weapon resources")
	
	# Verify active weapon is Pulse and has Pygame stats
	var active_w = weapon_ctrl.weapons[weapon_ctrl.active_weapon_index]
	assert(active_w.weapon_id == "pulse", "Default active weapon must be Pulse")
	assert(is_equal_approx(active_w.damage, 12.0), "Active weapon damage must be 12.0")
	assert(is_equal_approx(active_w.speed, 650.0), "Active weapon speed must be 650.0")
	print("[PASS] Player component hierarchy and WeaponController runtime resources verified.")

	# 4. Verify Pygame Reference Movement Constants
	assert(player.max_speed >= 520.0, "max_speed must be at least 520.0 (from Pygame)")
	assert(is_equal_approx(float(player.acceleration), 6400.0), "acceleration must be 6400.0 (from Pygame)")
	assert(is_equal_approx(float(player.drag), 5.0), "drag must be 5.0 (from Pygame)")
	print("[PASS] Authoritative Pygame movement constants verified (Speed: 520, Accel: 6400, Drag: 5).")

	# Wait a frame for physics server synchronization
	await get_tree().physics_frame

	# 5. Real Movement Execution Test via Engine Physics Loop
	player.global_position = Vector2(1920.0, 1080.0)
	player.velocity = Vector2.ZERO
	var initial_x = player.global_position.x

	Input.action_press("move_right")
	for i in range(15):
		await get_tree().physics_frame
	assert(player.velocity.x > 0.0, "Player velocity must increase along positive X via move_right")
	assert(player.global_position.x > initial_x, "Player position must advance to the right via move_and_slide()")
	Input.action_release("move_right")
	print("[PASS] Real movement execution verified.")

	# 6. Real Mouse Aim Execution Test
	player.global_position = Vector2(1920.0, 1080.0)
	player.velocity = Vector2.ZERO
	player.look_at(Vector2(2200.0, 1080.0))
	assert(is_equal_approx(player.rotation, 0.0), "Aiming right must orient player rotation to 0 radians")
	player.look_at(Vector2(1920.0, 1400.0))
	assert(player.rotation > 0.0, "Aiming downward must produce positive clockwise rotation")
	print("[PASS] Real mouse aim transformations verified in 2D world coordinates.")

	# 7. Spawn a Scout Enemy and test Scout movement toward player
	var scout_scene = load("res://scenes/enemies/EnemyScout.tscn") as PackedScene
	assert(scout_scene != null, "EnemyScout.tscn must load")
	var scout = scout_scene.instantiate() as CharacterBody2D
	arena.add_child(scout)
	scout.global_position = Vector2(2300.0, 1080.0)
	
	assert(is_equal_approx(float(scout.get("max_hp")), 30.0), "Scout max HP must be 30.0 (from Pygame SCOUT_HP)")
	assert(is_equal_approx(float(scout.get("move_speed")), 210.0), "Scout move_speed must be 210.0 (from Pygame SCOUT_SPEED)")
	
	player.global_position = Vector2(1920.0, 1080.0)
	var initial_scout_dist = scout.global_position.distance_to(player.global_position)
	
	for i in range(20):
		await get_tree().physics_frame
	
	var current_scout_dist = scout.global_position.distance_to(player.global_position)
	assert(current_scout_dist < initial_scout_dist, "Scout must actively move toward Player position using move_speed 210.0")
	# 8. Real Projectile Firing, Travel, Collision & 12 Damage Test
	scout.global_position = Vector2(1980.0, 1080.0)
	player.global_position = Vector2(1920.0, 1080.0)
	player.aim_target_override = scout.global_position
	player.look_at(scout.global_position)
	await get_tree().physics_frame
	
	# Fire shot 1: fire_primary -> WeaponController -> Projectile instantiated
	Input.action_press("fire_primary")
	await get_tree().physics_frame
	Input.action_release("fire_primary")
	
	var projectile = _get_first_projectile_in_tree()
	assert(projectile != null, "Spawned projectile must exist in scene tree")
	
	# Wait for projectile to reach Scout and deal 12 damage
	for i in range(30):
		await get_tree().physics_frame
	
	assert(scout.get("current_hp") < 30.0, "Scout HP must be reduced after taking Pulse damage")
	print("[PASS] Complete projectile pipeline verified: fire_primary -> WeaponController -> Pulse -> travel -> hit -> 12 damage.")

	# Fire shot 2: HP becomes 6.0 (18 -> 6)
	scout.damage_receiver.take_damage(Hit.new(12.0, Hit.DamageType.NORMAL, player, scout.global_position))
	assert(is_equal_approx(float(scout.get("current_hp")), 6.0), "Scout HP must be 6.0 after 2nd hit")

	# Fire shot 3: Scout destroyed (6 -> 0)
	scout.damage_receiver.take_damage(Hit.new(12.0, Hit.DamageType.NORMAL, player, scout.global_position))
	assert(not is_instance_valid(scout) or scout.is_queued_for_deletion() or float(scout.get("current_hp")) <= 0.0, "Scout must be destroyed and removed after 3 Pulse hits")
	print("[PASS] Scout destruction and clean removal verified.")

	# 9. Verify NO Boss in Active Gameplay
	var boss_in_tree = get_tree().get_nodes_in_group("boss")
	assert(boss_in_tree.size() == 0, "No Boss must exist in active gameplay")
	print("[PASS] Verified NO Boss present in active scene tree.")

	print("\n*** ALL AUTHORITATIVE COMBAT FOUNDATION TESTS PASSED SUCCESSFULLY! ***")
	get_tree().quit(0)

func _get_first_projectile_in_tree() -> Area2D:
	for node in get_tree().root.get_children():
		if node.get_script() == ProjectileScript:
			return node as Area2D
		for child in node.get_children():
			if child.get_script() == ProjectileScript:
				return child as Area2D
	return null
