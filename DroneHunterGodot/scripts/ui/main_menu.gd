class_name MainMenu
extends Control

@onready var new_game_btn: Button = $Content/MenuButtons/NewGameBtn
@onready var continue_btn: Button = $Content/MenuButtons/ContinueBtn
@onready var save_select_btn: Button = $Content/MenuButtons/SaveSelectBtn
@onready var settings_btn: Button = $Content/MenuButtons/SettingsBtn
@onready var quit_btn: Button = $Content/MenuButtons/QuitBtn

func _ready() -> void:
	_update_continue_button()
	_connect_signals()

func _update_continue_button() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.save_manager:
		var has_any_save = gm.save_manager.has_save(0) or gm.save_manager.has_save(1) or gm.save_manager.has_save(2)
		continue_btn.disabled = not has_any_save
	else:
		continue_btn.disabled = true

func _connect_signals() -> void:
	new_game_btn.pressed.connect(_on_new_game)
	continue_btn.pressed.connect(_on_continue)
	save_select_btn.pressed.connect(_on_save_select)
	settings_btn.pressed.connect(_on_settings)
	quit_btn.pressed.connect(_on_quit)

func _on_new_game() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.campaign_state:
		gm.campaign_state.reset_campaign()
		gm.scrap = 500
		if gm.progression_manager:
			gm.progression_manager.reset()
		gm.save_game()
	get_tree().change_scene_to_file("res://scenes/ui/DroneSelect.tscn")

func _on_continue() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		# Find first active save slot or load current slot
		for s in [gm.current_slot, 0, 1, 2]:
			if gm.save_manager and gm.save_manager.has_save(s):
				gm.load_game(s)
				break
	get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn")

func _on_save_select() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/SaveSelect.tscn")

func _on_settings() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/Settings.tscn")

func _on_quit() -> void:
	get_tree().quit()
