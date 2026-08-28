extends SceneTree

const GameStateManagerScript = preload("res://scripts/core/game_state_manager.gd")
const CampaignStateScript = preload("res://scripts/core/campaign_state.gd")
const SaveManagerScript = preload("res://scripts/systems/save_manager.gd")
const DroneClassDefScript = preload("res://resources/drones/drone_class_definition.gd")
const WeaponDefScript = preload("res://resources/weapons/weapon_definition.gd")
const EnemyDefScript = preload("res://resources/enemies/enemy_definition.gd")

func _init() -> void:
	print("=== RUNNING GODOT 4.3 FOUNDATION TEST ===")

	# 1. Test GameStateManager
	var sm = GameStateManagerScript.new()
	assert(sm.get_current_state() == GameStateManagerScript.State.MAIN_MENU, "Initial state must be MAIN_MENU")
	sm.change_state(GameStateManagerScript.State.GAMEPLAY)
	assert(sm.get_current_state() == GameStateManagerScript.State.GAMEPLAY, "State must transition to GAMEPLAY")
	print("[PASS] GameStateManager initialized and transitioned states.")

	# 2. Test CampaignState
	var cs = CampaignStateScript.new()
	assert(cs.current_mission == "S1_M1", "Default mission must be S1_M1")
	assert(cs.unlocked_sectors.has(1), "Sector 1 must be unlocked by default")
	var serialized = cs.to_dict()
	assert(serialized["current_mission"] == "S1_M1", "Serialization check failed")
	print("[PASS] CampaignState initialized and serialized.")

	# 3. Test SaveManager
	var save_mgr = SaveManagerScript.new()
	assert(save_mgr.get_save_path(0) == "user://save_slot_0.json", "Save path template mismatch")
	print("[PASS] SaveManager interface verified.")

	# 4. Test Resources
	var drone_res = DroneClassDefScript.new()
	assert(drone_res.id == "striker", "DroneClassDefinition default ID mismatch")
	var weapon_res = WeaponDefScript.new()
	assert(weapon_res.id == "pulse", "WeaponDefinition default ID mismatch")
	var enemy_res = EnemyDefScript.new()
	assert(enemy_res.id == "scout", "EnemyDefinition default ID mismatch")
	print("[PASS] Base Resource classes instantiated.")

	# 5. Test InputMap
	var required_actions = [
		"move_up", "move_down", "move_left", "move_right",
		"fire_primary", "fire_secondary", "roll", "emp",
		"ultimate", "cloak", "next_weapon", "previous_weapon",
		"pause", "confirm", "cancel", "fullscreen"
	]
	for act in required_actions:
		assert(InputMap.has_action(act), "Missing InputMap action: " + act)
	print("[PASS] All required InputMap actions verified in Godot runtime.")

	print("\n*** ALL GODOT 4.3 FOUNDATION TESTS PASSED SUCCESSFULLY! ***")
	quit(0)
