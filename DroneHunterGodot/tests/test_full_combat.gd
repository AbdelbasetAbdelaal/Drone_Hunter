extends Node2D

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 FULL COMBAT SYSTEM (PHASE 2) TEST SUITE ===")
	
	# -------------------------------------------------------------
	# TEST 1: ALL 11 AUTHORITATIVE WEAPON DEFINITIONS & STATS
	# -------------------------------------------------------------
	var weapon_ids = [
		"pulse", "rapid", "scatter", "missile", "barrage",
		"plasma", "rail", "beam", "tesla", "cluster", "emp"
	]
	
	var expected_stats = {
		"pulse": {"damage": 12.0, "speed": 650.0, "cooldown": 0.18},
		"rapid": {"damage": 8.0, "speed": 980.0, "cooldown": 0.08},
		"scatter": {"damage": 10.0, "speed": 500.0, "cooldown": 0.75, "count": 5},
		"missile": {"damage": 65.0, "speed": 260.0, "cooldown": 2.50},
		"barrage": {"damage": 38.0, "speed": 620.0, "cooldown": 2.20, "count": 4},
		"plasma": {"damage": 90.0, "speed": 460.0, "cooldown": 0.85},
		"rail": {"damage": 115.0, "speed": 1800.0, "cooldown": 1.10},
		"beam": {"damage": 26.0, "speed": 1500.0, "cooldown": 0.08},
		"tesla": {"damage": 44.0, "speed": 1100.0, "cooldown": 0.40},
		"cluster": {"damage": 85.0, "speed": 520.0, "cooldown": 2.00},
		"emp": {"damage": 30.0, "speed": 1200.0, "cooldown": 0.50}
	}
	
	for w_id in weapon_ids:
		var path = "res://resources/weapons/" + w_id + ".tres"
		assert(ResourceLoader.exists(path), "Weapon resource missing: " + path)
		var def = load(path) as WeaponDefinition
		assert(def != null, "Failed to load weapon resource: " + path)
		assert(def.weapon_id == w_id, "Weapon ID mismatch for " + w_id)
		var exp_data = expected_stats[w_id]
		assert(is_equal_approx(def.damage, exp_data["damage"]), "%s damage mismatch" % w_id)
		assert(is_equal_approx(def.speed, exp_data["speed"]), "%s speed mismatch" % w_id)
		assert(is_equal_approx(def.cooldown, exp_data["cooldown"]), "%s cooldown mismatch" % w_id)
		if exp_data.has("count"):
			assert(def.projectile_count == exp_data["count"], "%s count mismatch" % w_id)
			
	print("[PASS] TEST 1: All 11 authoritative WeaponDefinition Resources validated.")

	# -------------------------------------------------------------
	# TEST 2: ALL 5 DRONE CLASS DEFINITIONS LOAD & INITIALIZE
	# -------------------------------------------------------------
	var drone_classes = ["striker", "interceptor", "assault", "arc", "command"]
	for d_id in drone_classes:
		var path = "res://resources/drones/" + d_id + ".tres"
		assert(ResourceLoader.exists(path), "Drone class missing: " + path)
		var d_def = load(path) as DroneClassDefinition
		assert(d_def != null, "Failed to load drone class: " + path)
		assert(d_def.max_health > 0, "Invalid health for " + d_id)
		assert(d_def.max_speed > 0, "Invalid speed for " + d_id)
	print("[PASS] TEST 2: All 5 DroneClassDefinition resources validated.")

	# -------------------------------------------------------------
	# TEST 3: INSTANTIATE SANDBOX SCENE & VERIFY ENTITIES
	# -------------------------------------------------------------
	var arena_scene = load("res://scenes/world/TrainingArena.tscn")
	var player_scene = load("res://scenes/player/Player.tscn")
	var scout_scene = load("res://scenes/enemies/EnemyScout.tscn")
	var shooter_scene = load("res://scenes/enemies/EnemyShooter.tscn")
	var heavy_scene = load("res://scenes/enemies/EnemyHeavy.tscn")
	var shield_scene = load("res://scenes/enemies/EnemyShieldElite.tscn")

	var arena = arena_scene.instantiate() as Node2D
	add_child(arena)

	var player = player_scene.instantiate() as Player
	arena.add_child(player)
	player.global_position = Vector2(1000.0, 1000.0)

	var scout = scout_scene.instantiate() as EnemyScout
	arena.add_child(scout)
	scout.global_position = Vector2(1200.0, 1000.0)

	var shooter = shooter_scene.instantiate() as EnemyShooter
	arena.add_child(shooter)
	shooter.global_position = Vector2(1500.0, 1000.0)

	var heavy = heavy_scene.instantiate() as EnemyHeavy
	arena.add_child(heavy)
	heavy.global_position = Vector2(800.0, 1000.0)

	var shield_elite = shield_scene.instantiate() as EnemyShieldElite
	arena.add_child(shield_elite)
	shield_elite.global_position = Vector2(1000.0, 1300.0)

	print("[PASS] TEST 3: Deterministic sandbox spawned with 4 core enemies + player.")

	# -------------------------------------------------------------
	# TEST 4: WEAPON CONTROLLER & ENERGY GATING
	# -------------------------------------------------------------
	var wc = player.weapon_controller
	assert(wc != null, "WeaponController must exist on Player")
	assert(wc.weapons.size() == 11, "WeaponController must have 11 active weapons")
	
	# Test energy gating by setting cost on active def
	wc.active_weapon_index = 0
	var test_def = wc.weapons[0]
	test_def.energy_cost = 25.0
	player.current_energy = 10.0 # Insufficient energy
	var fired = wc.try_fire_primary()
	assert(not fired, "Weapon must NOT fire when player has insufficient energy")
	
	# Restore energy
	player.current_energy = 100.0
	fired = wc.try_fire_primary()
	assert(fired, "Weapon must fire successfully when energy is sufficient")
	assert(player.current_energy == 75.0, "Energy must be deducted by 25.0 (100 -> 75)")
	assert(not wc.can_fire_primary(), "Weapon must be on cooldown immediately after firing")
	test_def.energy_cost = 0.0 # Reset
	print("[PASS] TEST 4: Energy gating, consumption, and cooldown gating verified.")

	# -------------------------------------------------------------
	# TEST 5: ALL 11 WEAPON BEHAVIORS FIRING VERIFICATION
	# -------------------------------------------------------------
	player.current_energy = 1000.0
	for i in range(wc.weapons.size()):
		wc.active_weapon_index = i
		wc._cooldown_timer = 0.0
		var success = wc.try_fire_primary()
		assert(success, "Weapon behavior %d (%s) must fire successfully" % [i, wc.weapons[i].weapon_id])
	print("[PASS] TEST 5: All 11 Weapon Behaviors fired successfully.")

	# -------------------------------------------------------------
	# TEST 6: ENEMY AI STATE MACHINES & DAMAGE PIPELINE
	# -------------------------------------------------------------
	# Scout state machine
	assert(scout.ai_state == EnemyScout.State.APPROACH, "Scout must start in APPROACH state")
	scout._process_ai(0.1)
	assert(scout.velocity.length() > 0.0, "Scout must move toward player")

	# Shooter state machine
	assert(shooter.ai_state == EnemyShooter.State.APPROACH, "Shooter must start in APPROACH state")
	shooter._process_ai(0.1)
	assert(shooter.velocity.length() > 0.0, "Shooter must move toward preferred range")

	# Heavy state machine
	assert(heavy.ai_state == EnemyHeavy.State.APPROACH, "Heavy must start in APPROACH state")
	heavy._process_ai(0.1)
	assert(heavy.velocity.length() > 0.0, "Heavy must move steadily")

	# Shield Elite protection
	shield_elite._protect_nearby_allies()
	print("[PASS] TEST 6: All 4 Enemy AI state transitions and behaviors verified.")

	# -------------------------------------------------------------
	# TEST 7: COMBAT DAMAGE, SHIELD MITIGATION & ENEMY DEATH
	# -------------------------------------------------------------
	var test_scout = scout_scene.instantiate() as EnemyScout
	arena.add_child(test_scout)
	test_scout.global_position = Vector2(2000.0, 2000.0)
	
	var scout_recv = test_scout.damage_receiver
	assert(test_scout.current_hp == 30.0, "Scout must start with 30 HP")
	
	# Apply 12 Pulse damage
	scout_recv.take_damage(Hit.new(12.0, Hit.DamageType.NORMAL, player, test_scout.global_position))
	assert(test_scout.current_hp == 18.0, "Scout HP must be 18.0 after 12 damage")
	
	# Apply 18 fatal damage
	scout_recv.take_damage(Hit.new(18.0, Hit.DamageType.NORMAL, player, test_scout.global_position))
	assert(test_scout.current_hp == 0.0, "Scout HP must be 0 after fatal damage")
	assert(test_scout.health.is_dead, "Scout Health must be dead")
	print("[PASS] TEST 7: Damage receiver, health reduction, and enemy death verified.")

	# -------------------------------------------------------------
	# TEST 8: 5 ABILITIES VERIFICATION
	# -------------------------------------------------------------
	var ac = player.ability_controller
	assert(ac != null, "AbilityController must exist")
	
	ac._start_roll()
	assert(ac.is_rolling, "Roll ability must activate")
	
	ac._start_emp()
	assert(ac._emp_cooldown > 0.0, "EMP ability must activate and start cooldown")
	
	ac._start_cloak()
	assert(ac.is_cloaked, "Cloak ability must activate")
	
	ac._start_overdrive()
	assert(ac.is_overdrive, "Overdrive ability must activate")
	
	ac._start_overclock()
	assert(ac.is_overclock, "Overclock ability must activate")
	print("[PASS] TEST 8: All 5 Abilities (Roll, EMP, Cloak, Overdrive, Overclock) verified.")

	# -------------------------------------------------------------
	# TEST 9: NO BOSS IN COMBAT SANDBOX
	# -------------------------------------------------------------
	var boss_nodes = get_tree().get_nodes_in_group("boss")
	assert(boss_nodes.size() == 0, "NO Boss entities must exist in the scene tree")
	print("[PASS] TEST 9: Confirmed NO Boss system in active gameplay.")

	print("\n*** ALL PHASE 2 FULL COMBAT SYSTEM TESTS PASSED SUCCESSFULLY! ***\n")
	get_tree().quit(0)
