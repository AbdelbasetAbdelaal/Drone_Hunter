class_name SettingsMenu
extends Control

@onready var fullscreen_check: CheckBox = $Content/SettingsCard/VBox/FullscreenRow/FullscreenCheck
@onready var master_slider: HSlider = $Content/SettingsCard/VBox/MasterRow/Slider
@onready var master_val_lbl: Label = $Content/SettingsCard/VBox/MasterRow/ValLbl

@onready var music_slider: HSlider = $Content/SettingsCard/VBox/MusicRow/Slider
@onready var music_val_lbl: Label = $Content/SettingsCard/VBox/MusicRow/ValLbl

@onready var sfx_slider: HSlider = $Content/SettingsCard/VBox/SFXRow/Slider
@onready var sfx_val_lbl: Label = $Content/SettingsCard/VBox/SFXRow/ValLbl

@onready var reset_btn: Button = $Content/SettingsCard/VBox/ResetRow/ResetBtn
@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_load_current_settings()
	_connect_signals()

func _load_current_settings() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		fullscreen_check.button_pressed = gm.is_fullscreen
		master_slider.value = gm.master_volume * 100.0
		music_slider.value = gm.music_volume * 100.0
		sfx_slider.value = gm.sfx_volume * 100.0
		
	_update_labels()

func _connect_signals() -> void:
	fullscreen_check.toggled.connect(_on_fullscreen_toggled)
	master_slider.value_changed.connect(_on_master_changed)
	music_slider.value_changed.connect(_on_music_changed)
	sfx_slider.value_changed.connect(_on_sfx_changed)
	
	reset_btn.pressed.connect(_on_reset_defaults)
	back_btn.pressed.connect(_on_back)

func _update_labels() -> void:
	master_val_lbl.text = "%d%%" % int(master_slider.value)
	music_val_lbl.text = "%d%%" % int(music_slider.value)
	sfx_val_lbl.text = "%d%%" % int(sfx_slider.value)

func _on_fullscreen_toggled(is_checked: bool) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.is_fullscreen = is_checked
		gm.apply_settings()

func _on_master_changed(val: float) -> void:
	_update_labels()
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.master_volume = val / 100.0
		gm.apply_settings()

func _on_music_changed(val: float) -> void:
	_update_labels()
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.music_volume = val / 100.0
		gm.apply_settings()

func _on_sfx_changed(val: float) -> void:
	_update_labels()
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.sfx_volume = val / 100.0
		gm.apply_settings()

func _on_reset_defaults() -> void:
	fullscreen_check.button_pressed = false
	master_slider.value = 100.0
	music_slider.value = 80.0
	sfx_slider.value = 85.0
	_update_labels()
	
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.is_fullscreen = false
		gm.master_volume = 1.0
		gm.music_volume = 0.8
		gm.sfx_volume = 0.85
		gm.apply_settings()

func _on_back() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.save_game()
	get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn")
