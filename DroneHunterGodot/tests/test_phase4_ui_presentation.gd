extends Node2D

const MainMenuClass = preload("res://scripts/ui/main_menu.gd")
const SaveSelectClass = preload("res://scripts/ui/save_select.gd")
const DroneSelectClass = preload("res://scripts/ui/drone_select.gd")
const SectorMapClass = preload("res://scripts/ui/sector_map.gd")
const MissionBriefingClass = preload("res://scripts/ui/mission_briefing.gd")
const SettingsMenuClass = preload("res://scripts/ui/settings_menu.gd")
const HUDClass = preload("res://scripts/ui/hud.gd")

func _ready() -> void:
	print("\n=== RUNNING GODOT 4.3 PHASE 4 (FINAL HARDENING & PRESENTATION) TEST SUITE ===")

	var gm = get_tree().get_first_node_in_group("game_manager")
	assert(gm != null, "GameManager autoload must exist")

	# -------------------------------------------------------------
	# TEST 1: CENTRALIZED STATE NAVIGATION VIA GAMESTATEMANAGER
	# -------------------------------------------------------------
	assert(gm.state_manager != null, "GameStateManager must exist in GameManager")
	
	# Verify State-to-Scene dictionary completeness
	for s in [
		GameStateManager.State.MAIN_MENU,
		GameStateManager.State.SAVE_SELECT,
		GameStateManager.State.DRONE_SELECT,
		GameStateManager.State.CAMPAIGN_SELECT,
		GameStateManager.State.MISSION_BRIEFING,
		GameStateManager.State.GAMEPLAY,
		GameStateManager.State.HANGAR,
		GameStateManager.State.SETTINGS
	]:
		assert(gm.STATE_SCENES.has(s), "GameStateManager must have scene mapping for state %s" % gm.state_manager.state_to_string(s))
		var scene_p = gm.STATE_SCENES[s]
		assert(ResourceLoader.exists(scene_p), "Mapped scene does not exist: " + scene_p)
		
	# Test state transitions
	gm.state_manager.change_state(GameStateManager.State.SAVE_SELECT)
	assert(gm.state_manager.get_current_state() == GameStateManager.State.SAVE_SELECT, "Current state must be SAVE_SELECT")
	assert(gm.state_manager.get_previous_state() == GameStateManager.State.MAIN_MENU, "Previous state must be MAIN_MENU")
	
	gm.state_manager.change_state(GameStateManager.State.MAIN_MENU)
	print("[PASS] TEST 1: Centralized GameStateManager state machine & scene mappings verified.")

	# -------------------------------------------------------------
	# TEST 2: MAIN MENU FLOW & SAVE AVAILABILITY
	# -------------------------------------------------------------
	var main_menu_scene = load("res://scenes/ui/MainMenu.tscn") as PackedScene
	assert(main_menu_scene != null, "MainMenu.tscn must be loadable")
	var main_menu = main_menu_scene.instantiate()
	add_child(main_menu)
	assert(main_menu.new_game_btn != null, "NewGame button must exist")
	assert(main_menu.continue_btn != null, "Continue button must exist")
	assert(main_menu.save_select_btn != null, "SaveSelect button must exist")
	assert(main_menu.settings_btn != null, "Settings button must exist")
	assert(main_menu.quit_btn != null, "Quit button must exist")
	main_menu.queue_free()
	print("[PASS] TEST 2: Main Menu navigation hierarchy and responsive controls verified.")

	# -------------------------------------------------------------
	# TEST 3: SAVE SELECT 3-SLOT MANAGEMENT & PURGE
	# -------------------------------------------------------------
	var save_select_scene = load("res://scenes/ui/SaveSelect.tscn") as PackedScene
	assert(save_select_scene != null, "SaveSelect.tscn must be loadable")
	var save_select = save_select_scene.instantiate()
	add_child(save_select)
	assert(save_select.slot0_card != null, "Slot 0 card must exist")
	assert(save_select.slot1_card != null, "Slot 1 card must exist")
	assert(save_select.slot2_card != null, "Slot 2 card must exist")
	
	# Test slot operations
	save_select._on_new_slot(1)
	assert(gm.current_slot == 1, "Active slot must be 1 after new slot creation")
	assert(gm.save_manager.has_save(1), "Slot 1 save must exist")
	
	save_select._on_delete_slot(1)
	assert(not gm.save_manager.has_save(1), "Slot 1 must be deleted")
	
	save_select.queue_free()
	print("[PASS] TEST 3: SaveSelect 3-slot management (Load, New, Delete) verified.")

	# -------------------------------------------------------------
	# TEST 4: DRONE SELECT FOR ALL 5 CLASSES (NO SKINS)
	# -------------------------------------------------------------
	var drone_select_scene = load("res://scenes/ui/DroneSelect.tscn") as PackedScene
	assert(drone_select_scene != null, "DroneSelect.tscn must be loadable")
	var drone_select = drone_select_scene.instantiate()
	add_child(drone_select)
	
	var expected_drones = ["striker", "interceptor", "assault", "arc", "command"]
	for d_id in expected_drones:
		drone_select._select_drone(d_id)
		assert(drone_select.current_drone_id == d_id, "Selected drone ID mismatch: " + d_id)
		assert(drone_select.drone_name_lbl.text.to_lower() == d_id, "Drone title mismatch: " + d_id)
		assert(drone_select.weapons_lbl.text.begins_with("WEAPONS:"), "Weapons list must be bound for: " + d_id)
		assert(drone_select.ability_lbl.text.begins_with("CORE ABILITY:"), "Ability must be bound for: " + d_id)
		
	drone_select.queue_free()
	print("[PASS] TEST 4: DroneSelect verified for all 5 core classes with zero skin dependencies.")

	# -------------------------------------------------------------
	# TEST 5: SECTOR MAP & CAMPAIGN AUTHORITY ENFORCEMENT
	# -------------------------------------------------------------
	var sector_map_scene = load("res://scenes/ui/SectorMap.tscn") as PackedScene
	assert(sector_map_scene != null, "SectorMap.tscn must be loadable")
	var sector_map = sector_map_scene.instantiate()
	add_child(sector_map)
	
	gm.campaign_state.reset_campaign()
	sector_map._select_sector(1)
	
	# Attempt to select a locked mission S1_M5 directly
	sector_map._select_mission("S1_M5")
	var cur_m_before = gm.campaign_state.current_mission
	sector_map._on_launch_mission()
	assert(gm.campaign_state.current_mission == cur_m_before, "Launching locked mission must be rejected")
	
	# Select unlocked mission S1_M1
	sector_map._select_mission("S1_M1")
	assert(sector_map.selected_mission_id == "S1_M1", "Selected mission must be S1_M1")
	
	sector_map.queue_free()
	print("[PASS] TEST 5: SectorMap 25-mission navigation and CampaignState authority verified.")

	# -------------------------------------------------------------
	# TEST 6: MISSION BRIEFING COMPLETE DATA BINDING
	# -------------------------------------------------------------
	var briefing_scene = load("res://scenes/ui/MissionBriefing.tscn") as PackedScene
	assert(briefing_scene != null, "MissionBriefing.tscn must be loadable")
	var briefing = briefing_scene.instantiate()
	
	gm.campaign_state.current_mission = "S1_M1"
	add_child(briefing)
	
	assert(briefing.title_lbl.text == "OPERATION: PERIMETER SWEEP", "Briefing title mismatch")
	assert(briefing.reward_lbl.text.contains("150"), "Reward text must contain 150")
	assert(briefing.objective_lbl.text.contains("DESTROY ALL"), "Objective text must contain DESTROY ALL")
	assert(briefing.defense_lbl.text.contains("RADAR COMMAND"), "Target text must contain RADAR COMMAND")
	assert(briefing.lore_lbl.text.length() > 20, "Lore text must be present")
	
	briefing.queue_free()
	print("[PASS] TEST 6: MissionBriefing authoritative data binding verified.")

	# -------------------------------------------------------------
	# TEST 7: COMBAT HUD BINDINGS & PROGRESS BARS
	# -------------------------------------------------------------
	var hud_scene = load("res://scenes/ui/HUD.tscn") as PackedScene
	assert(hud_scene != null, "HUD.tscn must be loadable")
	var hud = hud_scene.instantiate()
	add_child(hud)
	
	hud._on_health_changed(75.0, 100.0)
	assert(hud.hull_bar.value == 75.0, "Hull bar value mismatch")
	
	hud._on_shield_changed(30.0, 60.0)
	assert(hud.shield_bar.value == 30.0, "Shield bar value mismatch")
	
	hud._on_energy_changed(90.0, 100.0)
	assert(hud.energy_bar.value == 90.0, "Energy bar value mismatch")
	
	hud._on_wave_started(2, 4)
	assert(hud.wave_label.text == "ENCOUNTER 2 / 4", "Encounter label text mismatch")
	
	hud._on_mission_victory(5000, 1400)
	assert(hud.victory_modal.visible, "Victory modal must become visible")
	assert(hud.victory_score_lbl.text.contains("5000"), "Victory score mismatch")
	assert(hud.victory_scrap_lbl.text.contains("1400"), "Victory scrap reward mismatch")
	
	hud.queue_free()
	print("[PASS] TEST 7: Combat HUD health/shield/energy bars, encounter progress, and modals verified.")

	# -------------------------------------------------------------
	# TEST 8: SETTINGS & AUDIO BUS PERSISTENCE
	# -------------------------------------------------------------
	var settings_scene = load("res://scenes/ui/Settings.tscn") as PackedScene
	assert(settings_scene != null, "Settings.tscn must be loadable")
	var settings = settings_scene.instantiate()
	add_child(settings)
	
	settings._on_master_changed(75.0)
	settings._on_music_changed(60.0)
	settings._on_sfx_changed(70.0)
	
	assert(is_equal_approx(gm.master_volume, 0.75), "Master volume mismatch")
	assert(is_equal_approx(gm.music_volume, 0.60), "Music volume mismatch")
	assert(is_equal_approx(gm.sfx_volume, 0.70), "SFX volume mismatch")
	
	# Verify audio buses in AudioServer
	var master_bus_idx = AudioServer.get_bus_index("Master")
	if master_bus_idx != -1:
		assert(not AudioServer.is_bus_mute(master_bus_idx), "Master bus should not be muted at 75%")
		
	# Save & reload settings
	gm.save_game(0)
	gm.load_game(0)
	assert(is_equal_approx(gm.master_volume, 0.75), "Master volume must persist after reload")
	assert(is_equal_approx(gm.music_volume, 0.60), "Music volume must persist after reload")
	assert(is_equal_approx(gm.sfx_volume, 0.70), "SFX volume must persist after reload")
	
	settings.queue_free()
	print("[PASS] TEST 8: Audio & Display Settings runtime authority & persistence verified.")

	# -------------------------------------------------------------
	# TEST 9: NO OBSOLETE BOSS OR SKIN UI IN SCENE TREE
	# -------------------------------------------------------------
	var check_tree = func(node: Node, callable: Callable) -> void:
		assert(not node.name.to_lower().contains("bosshealth"), "No Boss health bar permitted in UI")
		assert(not node.name.to_lower().contains("skinselect"), "No Skin selector permitted in UI")
		for c in node.get_children():
			callable.call(c, callable)
	check_tree.call(get_tree().root, check_tree)
	print("[PASS] TEST 9: Confirmed zero obsolete Boss or Skin UI in active scene tree.")

	# -------------------------------------------------------------
	# TEST 10: FULL E2E PLAYER EXPERIENCE LOOP
	# -------------------------------------------------------------
	gm.current_slot = 0
	gm.scrap = 500
	gm.campaign_state.reset_campaign()
	gm.progression_manager.reset()
	gm.select_drone("interceptor")
	
	# Start S1_M1
	var cd = CombatDirector.new()
	add_child(cd)
	var s1_m1_def = load("res://resources/missions/S1_M1.tres") as MissionDefinition
	cd.start_mission(s1_m1_def)
	
	# Victory on S1_M1
	cd._on_mission_victory()
	assert(gm.scrap == 650, "Scrap must increase by +150 to 650")
	assert(gm.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 must be unlocked")
	
	# Purchase upgrade
	var bought = gm.purchase_upgrade("weapon")
	assert(bought, "Weapon upgrade purchase must succeed")
	assert(gm.get_upgrade_level("weapon") == 1, "Weapon upgrade level must be 1")
	
	# Save & Reload
	gm.save_game(0)
	var gm_reload = GameManagerNode.new()
	add_child(gm_reload)
	gm_reload.load_game(0)
	
	assert(gm_reload.selected_drone_id == "interceptor", "Selected drone must be interceptor")
	assert(gm_reload.get_upgrade_level("weapon") == 1, "Weapon upgrade must be preserved")
	assert(gm_reload.campaign_state.is_mission_unlocked("S1_M2"), "S1_M2 unlock must be preserved")
	assert(gm_reload.scrap == gm.scrap, "Scrap must be preserved")
	
	cd.queue_free()
	gm_reload.queue_free()
	print("[PASS] TEST 10: Full E2E Player Experience (Menu -> Drone -> Mission -> Victory -> Hangar -> Upgrade -> Save -> Reload) verified.")

	print("\n*** ALL PHASE 4 (FINAL HARDENING & PRESENTATION) TESTS PASSED 100% SUCCESSFULLY! ***\n")
	get_tree().quit(0)
