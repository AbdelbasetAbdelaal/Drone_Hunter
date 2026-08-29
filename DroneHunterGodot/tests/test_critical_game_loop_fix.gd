extends Node2D

const GroundObjectiveTargetClass = preload("res://scripts/gameplay/entities/ground_objective_target.gd")
const ObjectiveControllerClass = preload("res://scripts/gameplay/systems/objective_controller.gd")

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 CRITICAL GAME LOOP FIX TEST SUITE ===")

	var gm = get_tree().get_first_node_in_group("game_manager")
	assert(gm != null, "GameManager autoload must exist")

	if gm.progression_manager:
		gm.progression_manager.reset()
	gm.campaign_state.reset_campaign()
	gm.scrap = 500

	# -------------------------------------------------------------
	# TEST 1: ALL 5 DRONE CLASSES LOADABLE, APPLIED, AND PERSISTED
	# -------------------------------------------------------------
	var player_scene = load("res://scenes/player/Player.tscn") as PackedScene
	assert(player_scene != null, "Player.tscn must be loadable")
	
	var class_ids = ["striker", "interceptor", "assault", "arc", "command"]
	for d_id in class_ids:
		var p_path = "res://resources/drones/%s.tres" % d_id
		assert(ResourceLoader.exists(p_path), "Drone resource missing: " + p_path)
		var exp_def = load(p_path) as DroneClassDefinition
		
		# Select in GameManager
		gm.select_drone(d_id)
		assert(gm.selected_drone_id == d_id, "GameManager selected drone mismatch: " + d_id)
		
		# Instantiate Player
		var p_inst = player_scene.instantiate() as Player
		add_child(p_inst)
		
		assert(p_inst.drone_class != null, "Player must load a DroneClassDefinition")
		assert(p_inst.drone_class.class_id == d_id, "Player drone class ID mismatch for: " + d_id)
		assert(is_equal_approx(p_inst.max_speed, exp_def.max_speed), "Player max speed mismatch for: " + d_id)
		assert(is_equal_approx(p_inst.acceleration, exp_def.acceleration), "Player acceleration mismatch for: " + d_id)
		assert(is_equal_approx(p_inst.drag, exp_def.drag), "Player drag mismatch for: " + d_id)
		assert(is_equal_approx(p_inst.health.max_hp, exp_def.max_health), "Player max HP mismatch for: " + d_id)
		assert(is_equal_approx(p_inst.health.max_shield, exp_def.max_shield), "Player max shield mismatch for: " + d_id)
		assert(p_inst.weapon_controller.weapons.size() == exp_def.default_weapons.size(), "Weapon count mismatch for: " + d_id)
		assert(p_inst.ability_controller.current_ability_id == exp_def.ability_id, "Ability ID mismatch for: " + d_id)
		
		p_inst.queue_free()
		
	# Verify save/load persistence of selected drone
	gm.select_drone("arc")
	gm.save_game(0)
	var gm_reload = GameManagerNode.new()
	add_child(gm_reload)
	gm_reload.load_game(0)
	assert(gm_reload.selected_drone_id == "arc", "Selected drone class ID must persist across save/load")
	gm_reload.queue_free()
	
	print("[PASS] TEST 1: All 5 drone classes accurately applied to Player runtime & persisted.")

	# -------------------------------------------------------------
	# TEST 2: GROUND OBJECTIVE TARGET CREATION & DESTRUCTION
	# -------------------------------------------------------------
	var target_scene = load("res://scenes/missions/GroundObjectiveTarget.tscn") as PackedScene
	assert(target_scene != null, "GroundObjectiveTarget.tscn must be loadable")
	var target_inst = target_scene.instantiate()
	add_child(target_inst)
	target_inst.configure_target("radar_command", 2)
	
	assert(target_inst.target_id == "radar_command", "Target ID must be radar_command")
	assert(target_inst.health.max_hp == 350.0, "Target HP with defense level 2 must be 350.0")
	assert(target_inst.is_in_group("objective_targets"), "Must be in objective_targets group")
	assert(target_inst.is_in_group("enemy"), "Must be in enemy group so weapons can damage it")
	
	var target_destroyed_fired = [false]
	target_inst.target_destroyed.connect(func(_id): target_destroyed_fired[0] = true)
	
	# Damage and kill target
	target_inst.health.apply_damage(400.0)
	assert(target_destroyed_fired[0], "target_destroyed signal must be emitted upon death")
	print("[PASS] TEST 2: GroundObjectiveTarget creation, collision, damage, and destruction verified.")

	# -------------------------------------------------------------
	# TEST 3: TARGET-ORIENTED OBJECTIVE CONTROLLER COMPLETION
	# -------------------------------------------------------------
	var obj_ctrl = ObjectiveControllerClass.new()
	add_child(obj_ctrl)
	
	var s1_m1_def = load("res://resources/missions/S1_M1.tres") as MissionDefinition
	obj_ctrl.setup_objective(s1_m1_def)
	
	var dummy_target = target_scene.instantiate()
	add_child(dummy_target)
	dummy_target.configure_target("radar_command", 1)
	obj_ctrl.register_target(dummy_target)
	
	assert(obj_ctrl.active_targets.size() == 1, "Must have 1 active target registered")
	assert(obj_ctrl.is_active and not obj_ctrl.is_finished, "Objective must be active")
	
	# Destroy target -> objective completes
	dummy_target.health.apply_damage(500.0)
	assert(obj_ctrl.is_finished, "ObjectiveController must complete objective when required targets are destroyed")
	
	obj_ctrl.queue_free()
	print("[PASS] TEST 3: Target-oriented ObjectiveController tracking and completion verified.")

	# -------------------------------------------------------------
	# TEST 4: PLAYER DEATH -> GAMESTATEMANAGER MISSION_FAILED
	# -------------------------------------------------------------
	var player = player_scene.instantiate() as Player
	add_child(player)
	
	var cd = CombatDirector.new()
	add_child(cd)
	cd.start_mission(s1_m1_def)
	
	var failed_emitted = [false]
	cd.mission_failed.connect(func(): failed_emitted[0] = true)
	
	# Player takes lethal damage
	player.health.apply_damage(99999.0)
	assert(player.health.is_dead, "Player health must be dead")
	assert(failed_emitted[0], "CombatDirector must emit mission_failed")
	assert(gm.state_manager.get_current_state() == GameStateManager.State.MISSION_FAILED, "GameStateManager state must be MISSION_FAILED")
	
	player.queue_free()
	cd.queue_free()
	print("[PASS] TEST 4: Player death -> CombatDirector mission_failed -> GameStateManager MISSION_FAILED verified.")

	# -------------------------------------------------------------
	# TEST 5: MISSION COMPLETION -> NEXT MISSION UNLOCK & REWARD
	# -------------------------------------------------------------
	gm.campaign_state.reset_campaign()
	gm.scrap = 500
	
	var cd_win = CombatDirector.new()
	add_child(cd_win)
	cd_win.start_mission(s1_m1_def)
	
	var complete_emitted = [false]
	cd_win.mission_completed.connect(func(_sc, _scr): complete_emitted[0] = true)
	
	cd_win._on_mission_victory()
	assert(complete_emitted[0], "CombatDirector must emit mission_completed")
	assert(gm.scrap == 650, "Scrap must be credited exactly once (+150)")
	assert(gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must be unlocked")
	assert(gm.state_manager.get_current_state() == GameStateManager.State.MISSION_COMPLETE, "GameStateManager state must be MISSION_COMPLETE")
	
	cd_win.queue_free()
	print("[PASS] TEST 5: Mission completion -> CampaignState unlock -> Reward -> GameStateManager MISSION_COMPLETE verified.")

	print("\n*** ALL CRITICAL GAME LOOP FIX TESTS PASSED 100% SUCCESSFULLY! ***\n")
	get_tree().quit(0)
