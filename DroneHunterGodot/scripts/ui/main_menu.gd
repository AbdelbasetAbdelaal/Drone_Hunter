class_name MainMenu
extends Control

@onready var campaign_btn: Button = $Content/MenuButtons/CampaignBtn
@onready var hangar_btn: Button = $Content/MenuButtons/HangarBtn
@onready var settings_btn: Button = $Content/MenuButtons/SettingsBtn
@onready var quit_btn: Button = $Content/MenuButtons/QuitBtn

@onready var settings_modal: Panel = $SettingsModal
@onready var fullscreen_check: CheckBox = $SettingsModal/VBox/FullscreenCheck
@onready var close_settings_btn: Button = $SettingsModal/VBox/CloseBtn

func _ready() -> void:
	settings_modal.visible = false
	
	campaign_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn"))
	hangar_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/Hangar.tscn"))
	settings_btn.pressed.connect(func(): settings_modal.visible = true)
	quit_btn.pressed.connect(func(): get_tree().quit())
	
	fullscreen_check.toggled.connect(_on_fullscreen_toggled)
	close_settings_btn.pressed.connect(func(): settings_modal.visible = false)

func _on_fullscreen_toggled(is_checked: bool) -> void:
	if is_checked:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
