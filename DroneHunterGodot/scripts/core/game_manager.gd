class_name GameManagerNode
extends Node

const ProgressionManagerClass = preload("res://scripts/core/progression_manager.gd")
const CampaignStateClass = preload("res://scripts/core/campaign_state.gd")
const SaveManagerClass = preload("res://scripts/systems/save_manager.gd")
const GameStateManagerClass = preload("res://scripts/core/game_state_manager.gd")

const MAX_UPGRADE_LEVEL: int = 5

signal scrap_changed(new_amount: int)
signal drone_selected(drone_id: String)
signal upgrade_purchased(category: String, new_level: int)
signal settings_changed()

var state_manager: GameStateManagerClass
var campaign_state: CampaignStateClass
var progression_manager: ProgressionManagerClass
var save_manager: SaveManagerClass

var current_slot: int = 0
var selected_drone_id: String = "striker"
var scrap: int = 500
var total_score: int = 0
var difficulty_mode: int = 1

# Settings
var is_fullscreen: bool = false
var master_volume: float = 1.0
var music_volume: float = 0.8
var sfx_volume: float = 0.85
var ui_volume: float = 0.85

var unlocked_drones: Array[String] = ["striker"]

var last_mission_result: Dictionary = {}

const STATE_SCENES = {
	GameStateManager.State.MAIN_MENU: "res://scenes/ui/MainMenu.tscn",
	GameStateManager.State.SAVE_SELECT: "res://scenes/ui/SaveSelect.tscn",
	GameStateManager.State.DRONE_SELECT: "res://scenes/ui/DroneSelect.tscn",
	GameStateManager.State.CAMPAIGN_SELECT: "res://scenes/ui/SectorMap.tscn",
	GameStateManager.State.MISSION_BRIEFING: "res://scenes/ui/MissionBriefing.tscn",
	GameStateManager.State.GAMEPLAY: "res://scenes/world/TrainingArena.tscn",
	GameStateManager.State.HANGAR: "res://scenes/ui/Hangar.tscn",
	GameStateManager.State.SETTINGS: "res://scenes/ui/Settings.tscn",
	GameStateManager.State.MISSION_COMPLETE: "res://scenes/ui/MissionComplete.tscn",
	GameStateManager.State.MISSION_FAILED: "res://scenes/ui/MissionFailed.tscn"
}

var upgrade_levels: Dictionary:
	get: return progression_manager.to_dict() if progression_manager else {}
	set(v):
		if progression_manager:
			progression_manager.from_dict(v)

func _ready() -> void:
	add_to_group("game_manager")
	state_manager = GameStateManagerClass.new()
	campaign_state = CampaignStateClass.new()
	progression_manager = ProgressionManagerClass.new()
	save_manager = SaveManagerClass.new()
	
	load_game(current_slot)
	apply_settings()
	if state_manager and state_manager.has_signal("state_changed"):
		state_manager.state_changed.connect(_on_state_changed)

func navigate_to_state(target_state: GameStateManager.State) -> void:
	if state_manager:
		state_manager.change_state(target_state)
	var scene_path = STATE_SCENES.get(target_state, "")
	if scene_path != "" and is_inside_tree() and get_tree() != null:
		get_tree().change_scene_to_file(scene_path)

func add_scrap(amount: int) -> void:
	scrap += max(0, amount)
	scrap_changed.emit(scrap)
	save_game()

func select_drone(drone_id: String) -> void:
	if drone_id in unlocked_drones:
		selected_drone_id = drone_id
		drone_selected.emit(drone_id)
		save_game()

func get_upgrade_level(category: String) -> int:
	if progression_manager:
		return progression_manager.get_upgrade_level(category)
	return 0

func get_upgrade_cost(category: String) -> int:
	if progression_manager:
		return progression_manager.get_upgrade_cost(category)
	return -1

func purchase_upgrade(category: String) -> bool:
	if not progression_manager:
		return false
	var res = progression_manager.purchase_upgrade(category, scrap)
	if res["success"]:
		scrap = res["remaining_scrap"]
		scrap_changed.emit(scrap)
		upgrade_purchased.emit(category, res["new_level"])
		save_game()
		return true
	return false

func apply_upgrades_to_player(player: Player) -> void:
	if progression_manager and player:
		progression_manager.apply_upgrades_to_player(player)

func save_game(slot: int = -1) -> bool:
	if not save_manager:
		return false
	var target_slot = current_slot if slot == -1 else slot
	var payload = {
		"scrap": scrap,
		"selected_drone_id": selected_drone_id,
		"upgrade_levels": progression_manager.to_dict() if progression_manager else {},
		"unlocked_drones": unlocked_drones.duplicate(),
		"campaign": campaign_state.to_dict() if campaign_state else {},
		"settings": {
			"is_fullscreen": is_fullscreen,
			"master_volume": master_volume,
			"music_volume": music_volume,
			"sfx_volume": sfx_volume,
			"ui_volume": ui_volume
		}
	}
	return save_manager.save_slot(target_slot, payload)

func load_game(slot: int = 0) -> bool:
	if not save_manager or not save_manager.has_save(slot):
		return false
	current_slot = slot
	var data = save_manager.load_slot(slot)
	if data.is_empty():
		return false
		
	scrap = int(data.get("scrap", 500))
	selected_drone_id = str(data.get("selected_drone_id", "striker"))
	
	if progression_manager and data.has("upgrade_levels"):
		progression_manager.from_dict(data.get("upgrade_levels", {}))
		
	if campaign_state and data.has("campaign"):
		campaign_state.from_dict(data.get("campaign", {}))
		
	var drones = data.get("unlocked_drones", [])
	if drones is Array and drones.size() > 0:
		unlocked_drones.clear()
		for d in drones:
			unlocked_drones.append(str(d))
			
	var sets = data.get("settings", {})
	if sets is Dictionary:
		is_fullscreen = bool(sets.get("is_fullscreen", false))
		master_volume = float(sets.get("master_volume", 1.0))
		music_volume = float(sets.get("music_volume", 0.8))
		sfx_volume = float(sets.get("sfx_volume", 0.85))
		ui_volume = float(sets.get("ui_volume", 0.85))
		apply_settings()
		
	scrap_changed.emit(scrap)
	drone_selected.emit(selected_drone_id)
	return true

func delete_save(slot: int) -> bool:
	if save_manager:
		return save_manager.delete_slot(slot)
	return false

func apply_settings() -> void:
	if is_fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		
	# Update Audio Buses in AudioServer
	var master_idx = AudioServer.get_bus_index("Master")
	if master_idx != -1:
		AudioServer.set_bus_volume_db(master_idx, linear_to_db(clamp(master_volume, 0.0001, 2.0)))
		AudioServer.set_bus_mute(master_idx, master_volume <= 0.001)
		
	var music_idx = AudioServer.get_bus_index("Music")
	if music_idx != -1:
		AudioServer.set_bus_volume_db(music_idx, linear_to_db(clamp(music_volume, 0.0001, 2.0)))
		AudioServer.set_bus_mute(music_idx, music_volume <= 0.001)
		
	var sfx_idx = AudioServer.get_bus_index("SFX")
	if sfx_idx != -1:
		AudioServer.set_bus_volume_db(sfx_idx, linear_to_db(clamp(sfx_volume, 0.0001, 2.0)))
		AudioServer.set_bus_mute(sfx_idx, sfx_volume <= 0.001)

	var ui_idx = AudioServer.get_bus_index("UI")
	if ui_idx != -1:
		AudioServer.set_bus_volume_db(ui_idx, linear_to_db(clamp(ui_volume, 0.0001, 2.0)))
		AudioServer.set_bus_mute(ui_idx, ui_volume <= 0.001)
		
	var am = get_tree().get_first_node_in_group("audio_manager")
	if am:
		if "music_volume" in am:
			am.music_volume = music_volume
		if "sfx_volume" in am:
			am.sfx_volume = sfx_volume
		if "ui_volume" in am:
			am.ui_volume = ui_volume
			
	settings_changed.emit()

func _on_state_changed(old_state, new_state) -> void:
	if new_state == GameStateManager.State.PAUSE:
		if get_tree():
			get_tree().paused = true
	elif old_state == GameStateManager.State.PAUSE and new_state != GameStateManager.State.PAUSE:
		if get_tree():
			get_tree().paused = false
