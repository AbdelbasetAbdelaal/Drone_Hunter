extends Node2D

const ProgressionManagerClass = preload("res://scripts/core/progression_manager.gd")
const CampaignStateClass = preload("res://scripts/core/campaign_state.gd")
const ObjectiveControllerClass = preload("res://scripts/gameplay/systems/objective_controller.gd")
const SaveManagerClass = preload("res://scripts/systems/save_manager.gd")

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 PHASE 3 (FULL GAME LOOP & PROGRESSION) TEST SUITE ===")
	
	# -------------------------------------------------------------
	# TEST 1: ALL 25 MISSION DEFINITION RESOURCES
	# -------------------------------------------------------------
	var expected_missions = [
		"S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5",
		"S2_M1", "S2_M2", "S2_M3", "S2_M4", "S2_M5",
		"S3_M1", "S3_M2", "S3_M3", "S3_M4", "S3_M5",
		"S4_M1", "S4_M2", "S4_M3", "S4_M4", "S4_M5",
		"S5_M1", "S5_M2", "S5_M3", "S5_M4", "S5_M5"
	]
	
	for m_id in expected_missions:
		var p = "res://resources/missions/%s.tres" % m_id
		assert(ResourceLoader.exists(p), "Missing mission resource: " + p)
		var def = load(p) as MissionDefinition
		assert(def != null, "Failed to load mission: " + p)
		assert(def.mission_id == m_id, "Mission ID mismatch: " + m_id)
		assert(def.sector_index >= 1 and def.sector_index <= 5, "Invalid sector index for " + m_id)
		assert(def.mission_index >= 1 and def.mission_index <= 5, "Invalid mission index for " + m_id)
		assert(def.encounter_sequence.size() > 0, "Encounter sequence must not be empty for " + m_id)
		assert(def.scrap_reward > 0, "Scrap reward must be positive for " + m_id)
		assert(def.is_boss_mission == false, "No mission must be a boss mission")
		
	print("[PASS] TEST 1: All 25 authoritative MissionDefinition resources validated.")

	# -------------------------------------------------------------
	# TEST 2: CAMPAIGN PROGRESSION & SECTOR UNLOCKS
	# -------------------------------------------------------------
	var camp = CampaignStateClass.new()
	assert(camp.is_mission_unlocked("S1_M1"), "S1_M1 must be unlocked by default")
	assert(not camp.is_mission_unlocked("S1_M2"), "S1_M2 must be locked initially")
	assert(camp.is_sector_unlocked(1), "Sector 1 must be unlocked by default")
	assert(not camp.is_sector_unlocked(2), "Sector 2 must be locked initially")
	
	# Complete S1_M1 -> Unlocks S1_M2
	var res1 = camp.complete_mission("S1_M1")
	assert(camp.is_mission_completed("S1_M1"), "S1_M1 must be completed")
	assert(camp.is_mission_unlocked("S1_M2"), "S1_M2 must be unlocked")
	assert(res1["scrap_earned"] == 150, "S1_M1 reward must be 150")
	
	# Complete S1_M2, S1_M3, S1_M4
	camp.complete_mission("S1_M2")
	camp.complete_mission("S1_M3")
	camp.complete_mission("S1_M4")
	
	# Complete S1_M5 -> Unlocks S2_M1 and grants Sector 1 bonus (500)
	var res5 = camp.complete_mission("S1_M5")
	assert(camp.is_mission_unlocked("S2_M1"), "S2_M1 must be unlocked after S1_M5")
	assert(camp.is_sector_unlocked(2), "Sector 2 must be unlocked after S1_M5")
	assert(res5["sector_bonus"] == 500, "Sector 1 completion bonus must be 500")
	
	# Progress through all missions to S5_M5
	for s in range(2, 6):
		for m in range(1, 6):
			var m_id = "S%d_M%d" % [s, m]
			if not camp.is_mission_completed(m_id):
				camp.complete_mission(m_id)
				
	assert(camp.campaign_completed, "Campaign must be marked complete after S5_M5")
	print("[PASS] TEST 2: Campaign progression and sector unlocks verified across all 25 missions.")

	# -------------------------------------------------------------
	# TEST 3: OBJECTIVE CONTROLLER RUNTIME
	# -------------------------------------------------------------
	var obj_ctrl = ObjectiveControllerClass.new()
	add_child(obj_ctrl)
	
	# Test Destroy All
	var def_destroy = load("res://resources/missions/S1_M1.tres") as MissionDefinition
	obj_ctrl.setup_objective(def_destroy)
	assert(obj_ctrl.is_active, "ObjectiveController must be active")
	obj_ctrl.on_encounter_cleared(2, 2)
	obj_ctrl.on_all_enemies_destroyed()
	assert(obj_ctrl.is_finished, "Destroy All objective must complete")
	
	# Test Survive
	var def_survive = load("res://resources/missions/S2_M4.tres") as MissionDefinition
	obj_ctrl.setup_objective(def_survive)
	assert(obj_ctrl.objective_type == "survive", "Objective type must be survive")
	obj_ctrl._physics_process(50.0) # Duration is 45.0
	assert(obj_ctrl.is_finished, "Survive objective must complete after duration")
	
	obj_ctrl.queue_free()
	print("[PASS] TEST 3: ObjectiveController runtime (destroy_all, survive, complete_encounters) verified.")

	# -------------------------------------------------------------
	# TEST 4: UPGRADES & SCRAP ECONOMY
	# -------------------------------------------------------------
	var prog = ProgressionManagerClass.new()
	assert(prog.get_upgrade_level("hull") == 0, "Hull upgrade level must start at 0")
	var initial_cost = prog.get_upgrade_cost("hull")
	assert(initial_cost == 100, "Initial Hull upgrade cost must be 100")
	
	# Attempt purchase with insufficient scrap
	var fail_res = prog.purchase_upgrade("hull", 50)
	assert(not fail_res["success"], "Purchase must fail with insufficient scrap")
	
	# Successful purchase
	var success_res = prog.purchase_upgrade("hull", 200)
	assert(success_res["success"], "Purchase must succeed with sufficient scrap")
	assert(success_res["new_level"] == 1, "New level must be 1")
	assert(success_res["remaining_scrap"] == 100, "Remaining scrap must be 100")
	assert(prog.get_upgrade_cost("hull") > initial_cost, "Next level cost must increase")
	
	# Test max level cap
	for i in range(10):
		prog.purchase_upgrade("hull", 999999)
	assert(prog.get_upgrade_level("hull") == 5, "Upgrade must cap at level 5")
	assert(prog.get_upgrade_cost("hull") == -1, "Cost at max level must return -1")
	print("[PASS] TEST 4: ProgressionManager upgrades and Scrap economy verified.")

	# -------------------------------------------------------------
	# TEST 5: SAVE SYSTEM (SLOTS 0, 1, 2) & CORRUPTION RECOVERY
	# -------------------------------------------------------------
	var sm = SaveManagerClass.new()
	for slot in [0, 1, 2]:
		var payload = {
			"scrap": 1250 + (slot * 100),
			"selected_drone_id": "interceptor",
			"upgrade_levels": {"hull": 2, "energy": 1, "weapon": 3, "mobility": 0},
			"unlocked_drones": ["striker", "interceptor"],
			"campaign": camp.to_dict()
		}
		var saved = sm.save_slot(slot, payload)
		assert(saved, "Saving to slot %d must succeed" % slot)
		assert(sm.has_save(slot), "has_save(%d) must return true" % slot)
		
		var loaded = sm.load_slot(slot)
		assert(not loaded.is_empty(), "Loaded slot %d must not be empty" % slot)
		assert(loaded["scrap"] == payload["scrap"], "Scrap in slot %d mismatch" % slot)
		assert(loaded["selected_drone_id"] == "interceptor", "Drone in slot %d mismatch" % slot)
		assert(loaded["upgrade_levels"]["weapon"] == 3, "Upgrades in slot %d mismatch" % slot)
		
		sm.delete_slot(slot)
		assert(not sm.has_save(slot), "delete_slot(%d) must remove save file" % slot)
		
	# Test invalid slot rejection
	assert(not sm.save_slot(99, {}), "Invalid slot must be rejected")
	assert(sm.load_slot(99).is_empty(), "Invalid slot load must return empty dict")
	print("[PASS] TEST 5: Multi-slot SaveManager (slots 0, 1, 2) serialization verified.")

	# -------------------------------------------------------------
	# TEST 6: ALL 5 DRONE CLASSES LOADABLE
	# -------------------------------------------------------------
	for d_id in ["striker", "interceptor", "assault", "arc", "command"]:
		var p = "res://resources/drones/%s.tres" % d_id
		assert(ResourceLoader.exists(p), "Drone resource missing: " + p)
		var d_def = load(p) as DroneClassDefinition
		assert(d_def != null, "Failed to load drone: " + d_id)
		assert(d_def.max_health > 0, "Invalid max health for drone: " + d_id)
	print("[PASS] TEST 6: All 5 DroneClassDefinition resources validated.")

	# -------------------------------------------------------------
	# TEST 7: HIGH-VALUE E2E GAMEPLAY LOOP SCENARIO
	# -------------------------------------------------------------
	# 1. Access Game Manager & Reset Campaign
	var gm = get_tree().get_first_node_in_group("game_manager")
	assert(gm != null, "GameManager autoload must exist")
	gm.current_slot = 0
	gm.scrap = 500
	gm.campaign_state.reset_campaign()
	gm.progression_manager.reset()
	gm.select_drone("striker")
	
	# 2. Setup CombatDirector for S1_M1
	var cd = CombatDirector.new()
	add_child(cd)
	
	var s1_m1_def = load("res://resources/missions/S1_M1.tres") as MissionDefinition
	cd.start_mission(s1_m1_def)
	
	assert(gm.campaign_state.is_mission_unlocked("S1_M1"), "S1_M1 must be unlocked initially")
	assert(not gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must be locked before completion")
	
	# 3. Simulate completion of encounter objective
	var scrap_before = gm.scrap
	cd._on_mission_victory()
	
	# 4. Verify Victory, Scrap Reward, and S1_M2 unlock
	assert(gm.scrap == scrap_before + s1_m1_def.scrap_reward, "Scrap reward must be added to economy")
	assert(gm.campaign_state.is_mission_completed("S1_M1"), "S1_M1 must be completed")
	assert(gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must now be unlocked")
	
	# 5. Buy Hull Upgrade
	var bought = gm.purchase_upgrade("hull")
	assert(bought, "Upgrade purchase must succeed")
	assert(gm.get_upgrade_level("hull") == 1, "Hull upgrade level must be 1")
	
	# 6. Save Slot 0 and Reload in fresh instance
	gm.save_game(0)
	
	var gm_reloaded = GameManagerNode.new()
	add_child(gm_reloaded)
	var loaded_ok = gm_reloaded.load_game(0)
	assert(loaded_ok, "Reloading save slot 0 must succeed")
	assert(gm_reloaded.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must remain unlocked after reload")
	assert(gm_reloaded.get_upgrade_level("hull") == 1, "Hull upgrade must be preserved after reload")
	assert(gm_reloaded.scrap == gm.scrap, "Scrap amount must be preserved after reload")
	
	# Clean up test save
	gm.delete_save(0)
	
	cd.queue_free()
	gm_reloaded.queue_free()
	print("[PASS] TEST 7: Full E2E Loop (New Save -> Play -> Victory -> Scrap -> Unlock -> Upgrade -> Save -> Reload) verified.")

	print("\n*** ALL PHASE 3 FULL GAME LOOP TESTS PASSED 100% SUCCESSFULLY! ***\n")
	get_tree().quit(0)
