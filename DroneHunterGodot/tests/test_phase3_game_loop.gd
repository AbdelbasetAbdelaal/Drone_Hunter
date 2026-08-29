extends Node2D

const ProgressionManagerClass = preload("res://scripts/core/progression_manager.gd")
const CampaignStateClass = preload("res://scripts/core/campaign_state.gd")
const ObjectiveControllerClass = preload("res://scripts/gameplay/systems/objective_controller.gd")
const SaveManagerClass = preload("res://scripts/systems/save_manager.gd")

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 PHASE 3 (FINAL CORRECTNESS & DATA FIDELITY) TEST SUITE ===")
	
	# -------------------------------------------------------------
	# TEST 1: COMPLETE 25-MISSION EXACT CONTENT REFERENCE CHECK
	# -------------------------------------------------------------
	var PATROL = ["scout", "scout", "scout"]
	var ASSAULT = ["scout", "scout", "scout", "scout"]
	var SWARM = ["scout", "scout", "scout", "scout", "scout"]
	var SHOOTER_PAIR = ["shooter", "scout", "shooter"]
	var SHOOTER_SQUAD = ["scout", "shooter", "scout", "shooter", "scout"]
	var HEAVY_ESCORT = ["scout", "heavy", "scout", "shooter"]
	var HEAVY_BATTLE = ["scout", "heavy", "shooter", "heavy", "scout"]
	var SHIELD_VANGUARD = ["scout", "shield_elite", "shooter", "scout"]
	var ELITE_FORCE = ["shield_elite", "heavy", "shooter", "shooter", "scout"]

	var EXACT_MISSIONS = [
		# Sector 1
		{"id": "S1_M1", "sec": 1, "num": 1, "title": "Perimeter Sweep", "diff": 1, "obj": "destroy_all", "target": "radar_command", "def": 1, "dur": 0.0, "rew": 150,
		 "enc": [PATROL, ASSAULT], "lore": "Allied recon drones picked up anomalous signals along the outermost perimeter fence. A light scout sweep will confirm whether the factory grounds are as quiet as intel suggests.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S1_M2", "sec": 1, "num": 2, "title": "Factory Approach", "diff": 1, "obj": "destroy_all", "target": "communication_hub", "def": 1, "dur": 0.0, "rew": 250,
		 "enc": [PATROL, SHOOTER_PAIR, SHOOTER_SQUAD], "lore": "The main assembly approach is crawling with automated sentries. Advance carefully and eliminate all hostiles before they can radio for reinforcements.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "time_limit", "value": 120}]},
		{"id": "S1_M3", "sec": 1, "num": 3, "title": "Security Breach", "diff": 2, "obj": "complete_encounters", "target": "radar_command", "def": 2, "dur": 0.0, "rew": 400,
		 "enc": [ASSAULT, SHOOTER_PAIR, HEAVY_ESCORT], "lore": "A full security breach has been triggered in Sector 1's inner compound. Hostile drones are mobilizing in escalating waves. Hold the breach point until command gives the all-clear.",
		 "sides": [{"type": "precision_strikes", "value": 10}]},
		{"id": "S1_M4", "sec": 1, "num": 4, "title": "Production Line", "diff": 2, "obj": "complete_encounters", "target": "missile_complex", "def": 2, "dur": 0.0, "rew": 600,
		 "enc": [SHOOTER_PAIR, SWARM, HEAVY_ESCORT], "lore": "The autonomous production line has been reprogrammed to churn out hostile units at an alarming rate. Sabotage key assembly nodes while surviving the drone onslaught.",
		 "sides": [{"type": "collect_data_cores", "value": 3}, {"type": "time_limit", "value": 120}]},
		{"id": "S1_M5", "sec": 1, "num": 5, "title": "Perimeter Collapse", "diff": 3, "obj": "complete_encounters", "target": "power_reactor", "def": 3, "dur": 0.0, "rew": 900,
		 "enc": [ASSAULT, SHOOTER_SQUAD, HEAVY_ESCORT], "lore": "The outer perimeter has fully collapsed. What remains of the drone network is converging on your position. Crush the remaining resistance and claim the sector for the Alliance.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "precision_strikes", "value": 10}]},

		# Sector 2
		{"id": "S2_M1", "sec": 2, "num": 1, "title": "Core Entry", "diff": 2, "obj": "destroy_all", "target": "missile_complex", "def": 2, "dur": 0.0, "rew": 150,
		 "enc": [SWARM, SHOOTER_SQUAD, HEAVY_ESCORT], "lore": "You have breached the Core Sector boundary. Ancient mining drones have been repurposed as weapons — sweep the canyon entry and clear a path toward the reactor heart.",
		 "sides": [{"type": "collect_data_cores", "value": 3}, {"type": "precision_strikes", "value": 10}]},
		{"id": "S2_M2", "sec": 2, "num": 2, "title": "Assembly Lines", "diff": 2, "obj": "complete_encounters", "target": "weapons_factory", "def": 2, "dur": 0.0, "rew": 250,
		 "enc": [SHOOTER_SQUAD, SHIELD_VANGUARD, HEAVY_ESCORT], "lore": "Deep within the canyon, automated assembly lines still produce shielded drone chassis. Intercept the production flow and destroy every unit rolling off the line.",
		 "sides": [{"type": "no_damage_taken", "value": true}]},
		{"id": "S2_M3", "sec": 2, "num": 3, "title": "Reactor Access", "diff": 3, "obj": "complete_encounters", "target": "communication_hub", "def": 3, "dur": 0.0, "rew": 400,
		 "enc": [SWARM, SHIELD_VANGUARD, HEAVY_BATTLE], "lore": "The approach to the sector reactor is heavily fortified. Drone commanders have deployed shield vanguards and heavy battlegroups to protect the access corridor.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "time_limit", "value": 120}]},
		{"id": "S2_M4", "sec": 2, "num": 4, "title": "Security Grid", "diff": 3, "obj": "survive", "target": "radar_command", "def": 3, "dur": 45.0, "rew": 600,
		 "enc": [SWARM, SHOOTER_SQUAD, HEAVY_ESCORT], "lore": "The security grid has locked down and is flooding the sector with drones on a loop. Survive the 45-second onslaught until the grid overloads and resets.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S2_M5", "sec": 2, "num": 5, "title": "Core Breach", "diff": 4, "obj": "complete_encounters", "target": "power_reactor", "def": 3, "dur": 0.0, "rew": 900,
		 "enc": [SHIELD_VANGUARD, SHOOTER_SQUAD, HEAVY_BATTLE], "lore": "The reactor core itself is within reach. Elite drone formations guard the final approach. Shatter their lines and seize control of the Core Sector's power grid.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "no_damage_taken", "value": true}]},

		# Sector 3
		{"id": "S3_M1", "sec": 3, "num": 1, "title": "Reactor Approach", "diff": 3, "obj": "complete_encounters", "target": "communication_hub", "def": 3, "dur": 0.0, "rew": 150,
		 "enc": [SHIELD_VANGUARD, HEAVY_BATTLE, SHOOTER_SQUAD], "lore": "Dense rainforest canopy conceals the reactor approach. Shield drones and heavy units patrol the jungle floor — neutralize them before they can alert the main facility.",
		 "sides": [{"type": "time_limit", "value": 120}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S3_M2", "sec": 3, "num": 2, "title": "Cooling Network", "diff": 3, "obj": "survive", "target": "power_reactor", "def": 3, "dur": 75.0, "rew": 250,
		 "enc": [SHIELD_VANGUARD, HEAVY_BATTLE, ELITE_FORCE], "lore": "The cooling network has been weaponized — drones pour through the exhaust vents in a continuous 75-second deluge. Hold your position until the network's failsafe triggers.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "precision_strikes", "value": 10}]},
		{"id": "S3_M3", "sec": 3, "num": 3, "title": "Power Junction", "diff": 4, "obj": "complete_encounters", "target": "weapons_factory", "def": 4, "dur": 0.0, "rew": 400,
		 "enc": [SWARM, SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "The power junction distributes energy across the entire sector. Drone commanders have deployed their most elite strike teams here. Eliminate every hostile to restore Alliance control.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "time_limit", "value": 120}]},
		{"id": "S3_M4", "sec": 3, "num": 4, "title": "Reactor Defense", "diff": 4, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 4, "dur": 0.0, "rew": 600,
		 "enc": [SHOOTER_SQUAD, HEAVY_BATTLE, ELITE_FORCE], "lore": "The reactor's automated defense systems have gone rogue. Heavy battlegroups and elite units are coordinating a coordinated counter-strike. Overwhelm them before the reactor goes critical.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S3_M5", "sec": 3, "num": 5, "title": "Critical Overload", "diff": 5, "obj": "complete_encounters", "target": "power_reactor", "def": 4, "dur": 0.0, "rew": 900,
		 "enc": [SHIELD_VANGUARD, HEAVY_BATTLE, ELITE_FORCE], "lore": "The reactor is moments from critical overload. The entire drone network has converged on the core chamber in a last stand. End them and stabilize the sector's power grid.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},

		# Sector 4
		{"id": "S4_M1", "sec": 4, "num": 1, "title": "Outer Defense", "diff": 4, "obj": "complete_encounters", "target": "radar_command", "def": 4, "dur": 0.0, "rew": 150,
		 "enc": [SHIELD_VANGUARD, HEAVY_BATTLE, ELITE_FORCE], "lore": "Megacity outer defense drones have been weaponized by the enemy AI. Push through the shield vanguards and heavy battlegroups to reach the interceptor network.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "time_limit", "value": 120}]},
		{"id": "S4_M2", "sec": 4, "num": 2, "title": "Interceptor Grid", "diff": 4, "obj": "survive", "target": "missile_complex", "def": 4, "dur": 75.0, "rew": 250,
		 "enc": [SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "The interceptor grid has locked onto all Alliance signatures. Survive 75 seconds of relentless drone waves until your ECM countermeasures force the grid to stand down.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S4_M3", "sec": 4, "num": 3, "title": "Defense Network", "diff": 4, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 4, "dur": 0.0, "rew": 400,
		 "enc": [SWARM, SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "The integrated defense network coordinates every drone in the sector. Disrupt its command chain by destroying all units tied to its relay nodes before it can re-synchronize.",
		 "sides": [{"type": "precision_strikes", "value": 10}]},
		{"id": "S4_M4", "sec": 4, "num": 4, "title": "Central Firewall", "diff": 5, "obj": "complete_encounters", "target": "weapons_factory", "def": 5, "dur": 0.0, "rew": 600,
		 "enc": [ELITE_FORCE, HEAVY_BATTLE, ELITE_FORCE], "lore": "The central firewall is the brain of the megacity defense grid. Elite strike forces are converging to protect it. Breach the firewall and take down the sector's command node.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "time_limit", "value": 120}]},
		{"id": "S4_M5", "sec": 4, "num": 5, "title": "Defense Collapse", "diff": 5, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 5, "dur": 0.0, "rew": 900,
		 "enc": [SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "The entire megacity defense grid is collapsing around you. Every remaining drone unit is throwing itself at your position in a final, desperate defense. Survive and claim the sector.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},

		# Sector 5
		{"id": "S5_M1", "sec": 5, "num": 1, "title": "Command Perimeter", "diff": 4, "obj": "complete_encounters", "target": "radar_command", "def": 5, "dur": 0.0, "rew": 150,
		 "enc": [SWARM, SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "You have reached Drone Command's outermost perimeter. Swarm drones and shielded vanguards guard the approach. Push through and establish a foothold inside the production plant.",
		 "sides": [{"type": "collect_data_cores", "value": 3}, {"type": "time_limit", "value": 120}]},
		{"id": "S5_M2", "sec": 5, "num": 2, "title": "Tactical Network", "diff": 5, "obj": "survive", "target": "missile_complex", "def": 5, "dur": 90.0, "rew": 250,
		 "enc": [ELITE_FORCE, HEAVY_BATTLE, SHIELD_VANGUARD], "lore": "The tactical network has detected your intrusion and is launching a 90-second barrage of elite drones and heavy units. Survive until the network's central processor is overwhelmed.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "precision_strikes", "value": 10}]},
		{"id": "S5_M3", "sec": 5, "num": 3, "title": "Command Core", "diff": 5, "obj": "complete_encounters", "target": "weapons_factory", "def": 5, "dur": 0.0, "rew": 400,
		 "enc": [SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE, ELITE_FORCE], "lore": "Deep inside Drone Command, the core processor coordinates the entire enemy network. Elite guard rotations and heavy battlegroups stand between you and the command core terminal.",
		 "sides": [{"type": "precision_strikes", "value": 10}, {"type": "no_damage_taken", "value": true}, {"type": "collect_data_cores", "value": 3}]},
		{"id": "S5_M4", "sec": 5, "num": 4, "title": "Final Defense", "diff": 5, "obj": "complete_encounters", "target": "power_reactor", "def": 5, "dur": 0.0, "rew": 600,
		 "enc": [ELITE_FORCE, HEAVY_BATTLE, ELITE_FORCE, HEAVY_BATTLE], "lore": "The final defense line before the command core unleashes everything it has. Wave after wave of elite and heavy units pour into the chamber. Crush them and open the path to victory.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "precision_strikes", "value": 10}, {"type": "time_limit", "value": 120}]},
		{"id": "S5_M5", "sec": 5, "num": 5, "title": "Drone Command", "diff": 5, "obj": "complete_encounters", "target": "cyber_defense_core", "def": 5, "dur": 0.0, "rew": 900,
		 "enc": [SWARM, SHIELD_VANGUARD, ELITE_FORCE, HEAVY_BATTLE], "lore": "This is it — the Drone Command central processor. The AI controlling the entire enemy network stands before you. Destroy every hostile unit and shut down the command core forever.",
		 "sides": [{"type": "no_damage_taken", "value": true}, {"type": "precision_strikes", "value": 10}, {"type": "collect_data_cores", "value": 3}]}
	]

	for exp_m in EXACT_MISSIONS:
		var m_id = exp_m["id"]
		var p = "res://resources/missions/%s.tres" % m_id
		assert(ResourceLoader.exists(p), "Missing mission resource: " + p)
		var def = load(p) as MissionDefinition
		assert(def != null, "Failed to load mission: " + p)
		
		assert(def.mission_id == m_id, "ID mismatch: " + m_id)
		assert(def.sector_index == exp_m["sec"], "Sector mismatch: " + m_id)
		assert(def.mission_index == exp_m["num"], "Mission number mismatch: " + m_id)
		assert(def.title == exp_m["title"], "Title mismatch: " + m_id)
		assert(def.difficulty == exp_m["diff"], "Difficulty mismatch: " + m_id)
		assert(def.primary_objective == exp_m["obj"], "Primary objective mismatch: " + m_id)
		assert(def.objective_target == exp_m["target"], "Objective target mismatch: " + m_id)
		assert(def.defense_level == exp_m["def"], "Defense level mismatch: " + m_id)
		assert(is_equal_approx(def.duration, exp_m["dur"]), "Duration mismatch: " + m_id)
		assert(def.scrap_reward == exp_m["rew"], "Reward mismatch: " + m_id)
		assert(def.lore == exp_m["lore"], "Lore content mismatch: " + m_id)
		
		# Exact encounter sequence array content match
		assert(def.encounter_sequence.size() == exp_m["enc"].size(), "Encounter size mismatch: " + m_id)
		for w_i in range(def.encounter_sequence.size()):
			var actual_wave = def.encounter_sequence[w_i]
			var exp_wave = exp_m["enc"][w_i]
			assert(actual_wave == exp_wave, "Wave %d content mismatch in %s: %s vs %s" % [w_i, m_id, str(actual_wave), str(exp_wave)])
			
		# Exact side objectives array content match
		assert(def.side_objectives.size() == exp_m["sides"].size(), "Side objectives size mismatch: " + m_id)
		for s_i in range(def.side_objectives.size()):
			var actual_side = def.side_objectives[s_i]
			var exp_side = exp_m["sides"][s_i]
			assert(str(actual_side["type"]) == str(exp_side["type"]), "Side objective type mismatch in " + m_id)
			assert(str(actual_side["value"]) == str(exp_side["value"]), "Side objective value mismatch in " + m_id)
			
	print("[PASS] TEST 1: All 25 authoritative MissionDefinition resources validated with 100% exact field & array content parity.")

	# -------------------------------------------------------------
	# TEST 2: LOCKED MISSION REJECTION & CAMPAIGN PROGRESSION
	# -------------------------------------------------------------
	var camp = CampaignStateClass.new()
	assert(camp.is_mission_unlocked("S1_M1"), "S1_M1 must be unlocked by default")
	assert(not camp.is_mission_unlocked("S1_M2"), "S1_M2 must be locked initially")
	assert(not camp.is_mission_unlocked("S5_M5"), "S5_M5 must be locked initially")
	
	# Attempt to complete a locked mission (S5_M5) on a fresh campaign -> MUST FAIL
	var fail_res = camp.complete_mission("S5_M5")
	assert(not fail_res["success"], "Attempting to complete locked mission must fail")
	assert(fail_res["reason"] == "mission_locked", "Failure reason must be 'mission_locked'")
	assert(not camp.is_mission_completed("S5_M5"), "S5_M5 must NOT be marked completed")
	assert(not camp.is_mission_unlocked("S5_M5"), "S5_M5 must NOT be unlocked")
	
	# Legitimate completion of S1_M1
	var ok_s1_m1 = camp.complete_mission("S1_M1")
	assert(ok_s1_m1["success"], "Completing unlocked S1_M1 must succeed")
	assert(ok_s1_m1["base_reward"] == 150, "S1_M1 reward must be 150")
	assert(camp.is_mission_unlocked("S1_M2"), "S1_M2 must now be unlocked")
	
	camp.complete_mission("S1_M2")
	camp.complete_mission("S1_M3")
	camp.complete_mission("S1_M4")
	
	# Complete S1_M5 -> Base 900 + Sector 1 Bonus 500 = 1400
	var res1_5 = camp.complete_mission("S1_M5")
	assert(res1_5["success"], "Completing S1_M5 must succeed")
	assert(res1_5["base_reward"] == 900, "S1_M5 base reward must be 900")
	assert(res1_5["sector_bonus"] == 500, "Sector 1 bonus must be 500")
	assert(res1_5["total_reward"] == 1400, "S1_M5 total reward must be 1400")
	assert(camp.is_mission_unlocked("S2_M1"), "S2_M1 must be unlocked")
	assert(camp.is_sector_unlocked(2), "Sector 2 must be unlocked")
	
	# Repeated completion of S1_M5 must NOT grant the one-time 500 sector bonus again
	var res1_5_repeat = camp.complete_mission("S1_M5")
	assert(res1_5_repeat["success"], "Replaying S1_M5 must succeed")
	assert(res1_5_repeat["sector_bonus"] == 0, "Repeated sector completion must NOT grant sector bonus again")
	assert(res1_5_repeat["total_reward"] == 900, "Repeated S1_M5 payout must be 900")
	
	# Progress through remaining sectors to S5_M5
	for s in range(2, 6):
		for m in range(1, 6):
			var m_id = "S%d_M%d" % [s, m]
			if not camp.is_mission_completed(m_id):
				var r = camp.complete_mission(m_id)
				assert(r["success"], "Completing %s must succeed" % m_id)
				if m == 5:
					var exp_sec_bonus = CampaignState.SECTOR_BONUSES[s]
					assert(r["sector_bonus"] == exp_sec_bonus, "Sector %d bonus mismatch" % s)
					assert(r["total_reward"] == 900 + exp_sec_bonus, "Total reward mismatch on S%d_M5" % s)
					
	assert(camp.campaign_completed, "Campaign must be marked complete after S5_M5")
	print("[PASS] TEST 2: Locked mission rejection, campaign unlocks, and authoritative sector bonuses verified.")

	# -------------------------------------------------------------
	# TEST 3: SURVIVAL OBJECTIVE & METADATA PRESERVATION
	# -------------------------------------------------------------
	var obj_ctrl = ObjectiveControllerClass.new()
	add_child(obj_ctrl)
	
	var def_s2_m4 = load("res://resources/missions/S2_M4.tres") as MissionDefinition
	obj_ctrl.setup_objective(def_s2_m4)
	assert(obj_ctrl.primary_objective == "survive", "primary_objective must be preserved")
	assert(obj_ctrl.objective_target == "radar_command", "objective_target must be preserved")
	assert(obj_ctrl.defense_level == 3, "defense_level must be preserved")
	assert(obj_ctrl.is_active, "ObjectiveController must be active")
	
	# Simulate 20 seconds of combat (should remain active)
	obj_ctrl._physics_process(20.0)
	assert(obj_ctrl.is_active and not obj_ctrl.is_finished, "Survival objective must remain active before 45s")
	
	# Simulate remaining 26 seconds (total 46s >= 45s target duration)
	obj_ctrl._physics_process(26.0)
	assert(obj_ctrl.is_finished, "Survival objective must complete when target duration is reached")
	
	obj_ctrl.queue_free()
	print("[PASS] TEST 3: Objective metadata preservation and survive deterministic time tracking verified.")

	# -------------------------------------------------------------
	# TEST 4: UPGRADES & SCRAP ECONOMY
	# -------------------------------------------------------------
	var prog = ProgressionManagerClass.new()
	assert(prog.get_upgrade_level("hull") == 0, "Hull upgrade level must start at 0")
	var initial_cost = prog.get_upgrade_cost("hull")
	assert(initial_cost == 100, "Initial Hull upgrade cost must be 100")
	
	var fail_buy = prog.purchase_upgrade("hull", 50)
	assert(not fail_buy["success"], "Purchase must fail with insufficient scrap")
	
	var success_buy = prog.purchase_upgrade("hull", 200)
	assert(success_buy["success"], "Purchase must succeed with sufficient scrap")
	assert(success_buy["new_level"] == 1, "New level must be 1")
	assert(success_buy["remaining_scrap"] == 100, "Remaining scrap must be 100")
	
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

	print("\n*** ALL PHASE 3 FINAL CORRECTNESS & DATA FIDELITY TESTS PASSED 100% SUCCESSFULLY! ***\n")
	get_tree().quit(0)
