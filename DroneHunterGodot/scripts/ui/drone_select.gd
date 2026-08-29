class_name DroneSelect
extends Control

var current_drone_id: String = "striker"
var drone_definitions: Dictionary = {}

@onready var drone_name_lbl: Label = $Content/RightCol/PreviewCard/DroneName
@onready var drone_role_lbl: Label = $Content/RightCol/PreviewCard/DroneRole
@onready var drone_desc_lbl: Label = $Content/RightCol/PreviewCard/DroneDesc
@onready var stats_lbl: Label = $Content/RightCol/PreviewCard/StatsLbl
@onready var weapons_lbl: Label = $Content/RightCol/PreviewCard/WeaponsLbl
@onready var ability_lbl: Label = $Content/RightCol/PreviewCard/AbilityLbl
@onready var drone_sprite: Sprite2D = $Content/RightCol/PreviewCard/SpriteContainer/DroneSprite

@onready var selector_container: VBoxContainer = $Content/LeftCol/DroneButtons
@onready var deploy_btn: Button = $Footer/DeployBtn
@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_load_drone_definitions()
	_setup_buttons()
	_select_drone("striker")
	
	deploy_btn.pressed.connect(_on_deploy)
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn"))

func _load_drone_definitions() -> void:
	var keys = ["striker", "interceptor", "assault", "arc", "command"]
	for k in keys:
		var p = "res://resources/drones/%s.tres" % k
		if ResourceLoader.exists(p):
			drone_definitions[k] = load(p) as DroneClassDefinition

func _setup_buttons() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	for child in selector_container.get_children():
		if child is Button:
			var d_id = child.name.to_lower()
			var is_unlocked = (d_id in gm.unlocked_drones) if gm else true
			child.disabled = not is_unlocked
			child.pressed.connect(func(): _select_drone(d_id))

func _select_drone(drone_id: String) -> void:
	if not (drone_id in drone_definitions):
		return
	current_drone_id = drone_id
	var def: DroneClassDefinition = drone_definitions[drone_id]
	
	drone_name_lbl.text = def.display_name
	drone_role_lbl.text = def.role
	drone_desc_lbl.text = def.description
	
	stats_lbl.text = "HULL: %d  |  SHIELD: %d  |  ENERGY: %d  |  SPEED: %d  |  ARMOR: %d%%" % [
		int(def.max_health), int(def.max_shield), int(def.max_energy), int(def.max_speed), int(def.base_armor * 100)
	]
	
	var weaps_str = ""
	for w in def.default_weapons:
		weaps_str += " • " + w.to_upper()
	weapons_lbl.text = "WEAPONS:" + weaps_str
	ability_lbl.text = "CORE ABILITY: " + def.ability_id.to_upper()
	
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm and gm.has_method("select_drone"):
		gm.select_drone(drone_id)

func _on_deploy() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn")
