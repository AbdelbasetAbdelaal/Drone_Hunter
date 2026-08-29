extends Node2D

const ProgressionManagerClass = preload("res://scripts/core/progression_manager.gd")
const CampaignStateClass = preload("res://scripts/core/campaign_state.gd")
const ObjectiveControllerClass = preload("res://scripts/gameplay/systems/objective_controller.gd")
const SaveManagerClass = preload("res://scripts/systems/save_manager.gd")

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 PHASE 3 (DATA FIDELITY & FULL GAME LOOP) TEST SUITE ===")
	
	# -------------------------------------------------------------
	# TEST 1: COMPLETE 25-MISSION REFERENCE DATA FIDELITY
	# -------------------------------------------------------------
	var expected_metadata = {
		"S1_M1": {"sec": 1, "num": 1, "diff": 1, "obj": "destroy_all", "target": "radar_command", "def": 1, "dur": 0.0, "rew": 150, "waves": 2},
		"S1_M2": {"sec": 1, "num": 2, "diff": 1, "obj": "destroy_all", "target": "communication_hub", "def": 1, "dur": 0.0, "rew": 250, "waves": 3},
		"S1_M3": {"sec": 1, "num": 3, "diff": 2, "obj": "complete_encounters", "target": "radar_command", "def": 2, "dur": 0.0, "rew": 400, "waves": 3},
		"S1_M4": {"sec": 1, "num": 4, "diff": 2, "obj": "complete_encounters", "target": "missile_complex", "def": 2, "dur": 0.0, "rew": 600, "waves": 3},
		"S1_M5": {"sec": 1, "num": 5, "diff": 3, "obj": "complete_encounters", "target": "power_reactor", "def": 3, "dur": 0.0, "rew": 900, "waves": 3},

		"S2_M1": {"sec": 2, "num": 1, "diff": 2, "obj": "destroy_all", "target": "missile_complex", "def": 2, "dur": 0.0, "rew": 150, "waves": 3},
		"S2_M2": {"sec": 2, "num": 2, "diff": 2, "obj": "complete_encounters", "target": "weapons_factory", "def": 2, "dur": 0.0, "rew": 250, "waves": 3},
		"S2_M3": {"sec": 2, "num": 3, "diff": 3, "obj": "complete_encounters", "target": "communication_hub", "def": 3, "dur": 0.0, "rew": 400, "waves": 3},
		"S2_M4": {"sec": 2, "num": 4, "diff": 3, "obj": "survive", "target": "radar_command", "def": 3, "dur": 45.0, "rew": 600, "waves": 3},
		"S2_M5": {"sec": 2, "num": 5, "diff": 4, "obj": "complete_encounters", "target": "power_reactor", "def": 3, "dur": 0.0, "rew": 900, "waves": 3},

		"S3_M1": {"sec": 3, "num": 1, "diff": 3, "obj": "complete_encounters", "target": "communication_hub", "def": 3, "dur": 0.0, "rew": 150, "waves": 3},
		"S3_M2": {"sec": 3, "num": 2, "diff": 3, "obj": "survive", "target": "power_reactor", "def": 3, "dur": 75.0, "rew": 250, "waves": 3},
		"S3_M3": {"sec": 3, "num": 3, "diff": 4, "obj": "complete_encounters", "target": "weapons_factory", "def": 4, "dur": 0.0, "rew": 400, "waves": 4},
		"S3_M4": {"sec": 3, "num": 4, "diff": 4, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 4, "dur": 0.0, "rew": 600, "waves": 3},
		"S3_M5": {"sec": 3, "num": 5, "diff": 5, "obj": "complete_encounters", "target": "power_reactor", "def": 4, "dur": 0.0, "rew": 900, "waves": 3},

		"S4_M1": {"sec": 4, "num": 1, "diff": 4, "obj": "complete_encounters", "target": "radar_command", "def": 4, "dur": 0.0, "rew": 150, "waves": 3},
		"S4_M2": {"sec": 4, "num": 2, "diff": 4, "obj": "survive", "target": "missile_complex", "def": 4, "dur": 75.0, "rew": 250, "waves": 3},
		"S4_M3": {"sec": 4, "num": 3, "diff": 4, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 4, "dur": 0.0, "rew": 400, "waves": 4},
		"S4_M4": {"sec": 4, "num": 4, "diff": 5, "obj": "complete_encounters", "target": "weapons_factory", "def": 5, "dur": 0.0, "rew": 600, "waves": 3},
		"S4_M5": {"sec": 4, "num": 5, "diff": 5, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 5, "dur": 0.0, "rew": 900, "waves": 3},

		"S5_M1": {"sec": 5, "num": 1, "diff": 4, "obj": "complete_encounters", "target": "radar_command", "def": 5, "dur": 0.0, "rew": 150, "waves": 4},
		"S5_M2": {"sec": 5, "num": 2, "diff": 5, "obj": "survive", "target": "missile_complex", "def": 5, "dur": 90.0, "rew": 250, "waves": 3},
		"S5_M3": {"sec": 5, "num": 3, "diff": 5, "obj": "complete_encounters", "target": "weapons_factory", "def": 5, "dur": 0.0, "rew": 400, "waves": 4},
		"S5_M4": {"sec": 5, "num": 4, "diff": 5, "obj": "complete_encounters", "target": "power_reactor", "def": 5, "dur": 0.0, "rew": 600, "waves": 4},
		"S5_M5": {"sec": 5, "num": 5, "diff": 5, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 5, "dur": 0.0, "rew": 900, "waves": 4}
	}
	
	for m_id in expected_metadata.keys():
		var p = "res://resources/missions/%s.tres" % m_id
		assert(ResourceLoader.exists(p), "Missing mission resource: " + p)
		var def = load(p) as MissionDefinition
		assert(def != null, "Failed to load mission: " + p)
		
		var exp_data = expected_metadata[m_id]
		assert(def.mission_id == m_id, "Mission ID mismatch: " + m_id)
		assert(def.sector_index == exp_data["sec"], "Sector mismatch for " + m_id)
		assert(def.mission_index == exp_data["num"], "Mission index mismatch for " + m_id)
		assert(def.difficulty == exp_data["diff"], "Difficulty mismatch for " + m_id)
		assert(def.primary_objective == exp_data["obj"], "Primary objective mismatch for " + m_id)
		assert(def.objective_target == exp_data["target"], "Objective target mismatch for " + m_id)
		assert(def.defense_level == exp_data["def"], "Defense level mismatch for " + m_id)
		assert(is_equal_approx(def.duration, exp_data["dur"]), "Duration mismatch for " + m_id)
		assert(def.scrap_reward == exp_data["rew"], "Scrap reward mismatch for " + m_id)
		assert(def.encounter_sequence.size() == exp_data["waves"], "Encounter sequence count mismatch for " + m_id)
		assert(def.lore.length() > 20, "Lore description must be present for " + m_id)
		assert(def.side_objectives.size() > 0, "Side objectives must be present for " + m_id)
		assert(def.is_boss_mission == false, "No mission must be a boss mission")
		
	print("[PASS] TEST 1: All 25 authoritative MissionDefinition resources validated with 100% reference fidelity.")

	# -------------------------------------------------------------
	# TEST 2: CAMPAIGN PROGRESSION & AUTHORITATIVE SECTOR REWARDS
	# -------------------------------------------------------------
	var camp = CampaignStateClass.new()
	assert(camp.is_mission_unlocked("S1_M1"), "S1_M1 must be unlocked by default")
	assert(not camp.is_mission_unlocked("S1_M2"), "S1_M2 must be locked initially")
	
	# Complete S1_M1 -> Unlocks S1_M2, +150 reward
	var res1 = camp.complete_mission("S1_M1")
	assert(res1["base_reward"] == 150 and res1["sector_bonus"] == 0 and res1["total_reward"] == 150, "S1_M1 reward must be 150")
	assert(camp.is_mission_unlocked("S1_M2"), "S1_M2 must be unlocked")
	
	camp.complete_mission("S1_M2")
	camp.complete_mission("S1_M3")
	camp.complete_mission("S1_M4")
	
	# Complete S1_M5 -> Base 900 + Sector 1 Bonus 500 = 1400
	var res1_5 = camp.complete_mission("S1_M5")
	assert(res1_5["base_reward"] == 900, "S1_M5 base reward must be 900")
	assert(res1_5["sector_bonus"] == 500, "Sector 1 bonus must be 500")
	assert(res1_5["total_reward"] == 1400, "S1_M5 total reward must be 1400 (900 + 500)")
	assert(camp.is_mission_unlocked("S2_M1"), "S2_M1 must be unlocked")
	assert(camp.is_sector_unlocked(2), "Sector 2 must be unlocked")
	
	# Repeated completion of S1_M5 must NOT award the one-time 500 sector bonus again
	var res1_5_repeat = camp.complete_mission("S1_M5")
	assert(res1_5_repeat["sector_bonus"] == 0, "Repeated sector completion must NOT grant sector bonus again")
	assert(res1_5_repeat["total_reward"] == 900, "Repeated S1_M5 payout must be base reward only (900)")
	
	# Progress through remaining sectors
	for s in range(2, 6):
		for m in range(1, 6):
			var m_id = "S%d_M%d" % [s, m]
			if not camp.is_mission_completed(m_id):
				var r = camp.complete_mission(m_id)
				if m == 5:
					var exp_sec_bonus = CampaignState.SECTOR_BONUSES[s]
					assert(r["sector_bonus"] == exp_sec_bonus, "Sector %d bonus mismatch" % s)
					assert(r["total_reward"] == 900 + exp_sec_bonus, "Total reward mismatch on S%d_M5" % s)
					
	assert(camp.campaign_completed, "Campaign must be marked complete after S5_M5")
	print("[PASS] TEST 2: Campaign progression and authoritative sector bonuses verified across all 5 sectors.")

	# -------------------------------------------------------------
	# TEST 3: SURVIVAL OBJECTIVE & DETERMINISTIC TIME TRACKING
	# -------------------------------------------------------------
	var obj_ctrl = ObjectiveControllerClass.new()
	add_child(obj_ctrl)
	
	var def_s2_m4 = load("res://resources/missions/S2_M4.tres") as MissionDefinition
	obj_ctrl.setup_objective(def_s2_m4)
	assert(obj_ctrl.objective_type == "survive", "Objective must be survive")
	assert(obj_ctrl.is_active, "ObjectiveController must be active")
	
	# Simulate 20 seconds of combat (should remain active)
	obj_ctrl._physics_process(20.0)
	assert(obj_ctrl.is_active and not obj_ctrl.is_finished, "Survival objective must remain active before 45s")
	
	# Simulate remaining 26 seconds (total 46s >= 45s target duration)
	obj_ctrl._physics_process(26.0)
	assert(obj_ctrl.is_finished, "Survival objective must complete when target duration is reached")
	
	obj_ctrl.queue_free()
	print("[PASS] TEST 3: Survive objective deterministic time tracking verified.")

	# -------------------------------------------------------------
	# TEST 4: UPGRADES & SCRAP ECONOMY
	# -------------------------------------------------------------
	var prog = ProgressionManagerClass.new()
	assert(prog.get_upgrade_level("hull") == 0, "Hull upgrade level must start at 0")
	var initial_cost = prog.get_upgrade_cost("hull")
	assert(initial_cost == 100, "Initial Hull upgrade cost must be 100")
	
	var fail_res = prog.purchase_upgrade("hull", 50)
	assert(not fail_res["success"], "Purchase must fail with insufficient scrap")
	
	var success_res = prog.purchase_upgrade("hull", 200)
	assert(success_res["success"], "Purchase must succeed with sufficient scrap")
	assert(success_res["new_level"] == 1, "New level must be 1")
	assert(success_res["remaining_scrap"] == 100, "Remaining scrap must be 100")
	
	for i in range(10):
		prog.purchase_upgrade("hull", 999999)
	assert(prog.get_upgrade_level("hull") == 5, "Upgrade must cap at level 5")
	assert(prog.get_upgrade_cost("hull") == -1, "Cost at max level must return -1")
	print("[PASS] TEST 4: ProgressionManager upgrades and Scrap economy verified.")

	# -------------------------------------------------------------
	# TEST 5: MULTI-SLOT SAVE SYSTEM & VALIDATION
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
		
		sm.delete_slot(slot)
		assert(not sm.has_save(slot), "delete_slot(%d) must remove save file" % slot)
		
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
	# TEST 7: EXTENDED HIGH-VALUE E2E GAMEPLAY LOOP SCENARIO
	# -------------------------------------------------------------
	var gm = get_tree().get_first_node_in_group("game_manager")
	assert(gm != null, "GameManager autoload must exist")
	gm.current_slot = 0
	gm.scrap = 500
	gm.campaign_state.reset_campaign()
	gm.progression_manager.reset()
	gm.select_drone("striker")
	
	# Start S1_M1
	var cd = CombatDirector.new()
	add_child(cd)
	
	var s1_m1_def = load("res://resources/missions/S1_M1.tres") as MissionDefinition
	cd.start_mission(s1_m1_def)
	
	assert(gm.campaign_state.is_mission_unlocked("S1_M1"), "S1_M1 must be unlocked initially")
	assert(not gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must be locked before completion")
	
	var scrap_start = gm.scrap
	cd._on_mission_victory()
	
	assert(gm.scrap == scrap_start + 150, "Scrap reward must be added to economy (+150)")
	assert(gm.campaign_state.is_mission_completed("S1_M1"), "S1_M1 must be completed")
	assert(gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must now be unlocked")
	
	# Purchase Hull upgrade
	var bought = gm.purchase_upgrade("hull")
	assert(bought, "Upgrade purchase must succeed")
	assert(gm.get_upgrade_level("hull") == 1, "Hull upgrade level must be 1")
	
	# Advance to S1_M5 and complete it to test Sector 1 bonus ($500)
	gm.campaign_state.complete_mission("S1_M2")
	gm.campaign_state.complete_mission("S1_M3")
	gm.campaign_state.complete_mission("S1_M4")
	
	var s1_m5_def = load("res://resources/missions/S1_M5.tres") as MissionDefinition
	cd.start_mission(s1_m5_def)
	
	var scrap_before_s1_m5 = gm.scrap
	cd._on_mission_victory()
	
	# Payout must be: Base 900 + Sector 1 Bonus 500 = 1400
	assert(gm.scrap == scrap_before_s1_m5 + 1400, "S1_M5 victory must award 1400 Scrap (900 base + 500 sector bonus)")
	assert(gm.campaign_state.is_mission_unlocked("S2_M1"), "S2_M1 must be unlocked after S1_M5")
	assert(gm.campaign_state.is_sector_unlocked(2), "Sector 2 must be unlocked")
	
	# Save Slot 0 and Reload in fresh instance
	gm.save_game(0)
	
	var gm_reloaded = GameManagerNode.new()
	add_child(gm_reloaded)
	var loaded_ok = gm_reloaded.load_game(0)
	assert(loaded_ok, "Reloading save slot 0 must succeed")
	assert(gm_reloaded.campaign_state.is_mission_unlocked("S2_M1"), "S2_M1 must remain unlocked after reload")
	assert(gm_reloaded.get_upgrade_level("hull") == 1, "Hull upgrade must be preserved after reload")
	assert(gm_reloaded.scrap == gm.scrap, "Scrap amount must be preserved after reload")
	
	# Clean up test save
	gm.delete_save(0)
	
	cd.queue_free()
	gm_reloaded.queue_free()
	print("[PASS] TEST 7: Extended E2E Loop (S1_M1 -> S1_M5 -> Sector 1 Bonus -> S2_M1 Unlock -> Upgrade -> Save -> Reload) verified.")

	print("\n*** ALL PHASE 3 FINAL DATA FIDELITY TESTS PASSED 100% SUCCESSFULLY! ***\n")
	get_tree().quit(0)
