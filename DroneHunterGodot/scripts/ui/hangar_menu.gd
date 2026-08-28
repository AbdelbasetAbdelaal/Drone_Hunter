class_name HangarMenu
extends Control

signal launch_requested(drone_id: String)
signal back_requested()

var current_drone_id: String = "striker"
var drone_definitions: Dictionary = {}

@onready var scrap_label: Label = $Header/ScrapLabel
@onready var drone_name_label: Label = $Content/RightCol/DronePanel/DroneName
@onready var drone_role_label: Label = $Content/RightCol/DronePanel/DroneRole
@onready var drone_desc_label: Label = $Content/RightCol/DronePanel/DroneDesc
@onready var drone_sprite: Sprite2D = $Content/RightCol/DronePanel/PreviewContainer/DroneSprite
@onready var stats_label: Label = $Content/RightCol/DronePanel/StatsLabel
@onready var weapons_label: Label = $Content/RightCol/DronePanel/WeaponsLabel

# Upgrade buttons & labels
@onready var hull_btn: Button = $Content/LeftCol/Upgrades/HullCard/BuyBtn
@onready var hull_lvl_lbl: Label = $Content/LeftCol/Upgrades/HullCard/LevelLbl

@onready var energy_btn: Button = $Content/LeftCol/Upgrades/EnergyCard/BuyBtn
@onready var energy_lvl_lbl: Label = $Content/LeftCol/Upgrades/EnergyCard/LevelLbl

@onready var weapon_btn: Button = $Content/LeftCol/Upgrades/WeaponCard/BuyBtn
@onready var weapon_lvl_lbl: Label = $Content/LeftCol/Upgrades/WeaponCard/LevelLbl

@onready var mobility_btn: Button = $Content/LeftCol/Upgrades/MobilityCard/BuyBtn
@onready var mobility_lvl_lbl: Label = $Content/LeftCol/Upgrades/MobilityCard/LevelLbl

@onready var launch_btn: Button = $Footer/LaunchBtn
@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_load_drone_definitions()
	_connect_signals()
	_update_ui()

func _load_drone_definitions() -> void:
	var drone_keys = ["striker", "interceptor", "assault", "arc", "command"]
	for k in drone_keys:
		var p = "res://resources/drones/" + k + ".tres"
		if ResourceLoader.exists(p):
			drone_definitions[k] = load(p) as DroneClassDefinition

func _connect_signals() -> void:
	hull_btn.pressed.connect(func(): _on_buy_upgrade("hull"))
	energy_btn.pressed.connect(func(): _on_buy_upgrade("energy"))
	weapon_btn.pressed.connect(func(): _on_buy_upgrade("weapon"))
	mobility_btn.pressed.connect(func(): _on_buy_upgrade("mobility"))
	
	launch_btn.pressed.connect(_on_launch)
	back_btn.pressed.connect(_on_back)
	
	# Drone selector buttons
	var selector_container = $Content/RightCol/DroneSelector
	for btn in selector_container.get_children():
		if btn is Button:
			btn.pressed.connect(func(): _select_drone(btn.name.to_lower()))

func _select_drone(drone_id: String) -> void:
	if drone_id in drone_definitions:
		current_drone_id = drone_id
		var gm = get_tree().get_first_node_in_group("game_manager")
		if gm and gm.has_method("select_drone"):
			gm.select_drone(drone_id)
		_update_drone_preview()

func _on_buy_upgrade(category: String) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.has_method("purchase_upgrade"):
		gm.purchase_upgrade(category)
	_update_ui()

func _update_ui() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	var scrap_val = gm.scrap if gm else 500
	scrap_label.text = "SCRAP: " + str(scrap_val) + " 🔩"
	
	_update_upgrade_card("hull", hull_lvl_lbl, hull_btn)
	_update_upgrade_card("energy", energy_lvl_lbl, energy_btn)
	_update_upgrade_card("weapon", weapon_lvl_lbl, weapon_btn)
	_update_upgrade_card("mobility", mobility_lvl_lbl, mobility_btn)
	
	_update_drone_preview()

func _update_upgrade_card(cat: String, lvl_lbl: Label, btn: Button) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	var lvl = gm.upgrade_levels.get(cat, 1) if gm else 1
	var cost = gm.get_upgrade_cost(cat) if gm else 150
	var scrap_val = gm.scrap if gm else 500
	
	lvl_lbl.text = "LEVEL " + str(lvl) + " / 5"
	if lvl >= 5:
		btn.text = "MAX"
		btn.disabled = true
	else:
		btn.text = str(cost) + " 🔩"
		btn.disabled = (scrap_val < cost)

func _update_drone_preview() -> void:
	var def: DroneClassDefinition = drone_definitions.get(current_drone_id)
	if not def:
		return
		
	drone_name_label.text = def.display_name
	drone_role_label.text = def.role
	drone_desc_label.text = def.description
	
	stats_label.text = "HULL: %d  |  SHIELD: %d  |  SPEED: %d  |  ARMOR: %d%%" % [
		int(def.max_health), int(def.max_shield), int(def.max_speed), int(def.base_armor * 100)
	]
	
	var weaps_str = ""
	for w in def.default_weapons:
		weaps_str += " • " + w.to_upper()
	weapons_label.text = "LOADOUT:" + weaps_str

func _on_launch() -> void:
	launch_requested.emit(current_drone_id)
	get_tree().change_scene_to_file("res://scenes/world/TrainingArena.tscn")

func _on_back() -> void:
	back_requested.emit()
