class_name SectorMap
extends Control

signal mission_selected(mission_id: String)
signal back_to_menu_requested()

var selected_sector: int = 1
var selected_mission_id: String = "S1_M1"

var missions_data: Dictionary = {}

@onready var sector_title_label: Label = $Content/RightPanel/SectorTitle
@onready var mission_list_container: VBoxContainer = $Content/RightPanel/MissionList
@onready var mission_details_label: Label = $Content/RightPanel/MissionDetails
@onready var launch_btn: Button = $Footer/LaunchBtn
@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_load_all_missions()
	_setup_sector_buttons()
	_select_sector(1)
	
	launch_btn.pressed.connect(_on_launch_mission)
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/Hangar.tscn"))

func _load_all_missions() -> void:
	for s in range(1, 6):
		for m in range(1, 4):
			var m_id = "S%d_M%d" % [s, m]
			var p = "res://resources/missions/%s.tres" % m_id
			if ResourceLoader.exists(p):
				missions_data[m_id] = load(p) as MissionDefinition

func _setup_sector_buttons() -> void:
	var sector_btns_container = $Content/LeftPanel/SectorButtons
	for i in range(1, 6):
		var btn = sector_btns_container.get_node_or_null("Sector" + str(i)) as Button
		if btn:
			btn.pressed.connect(func(): _select_sector(i))

func _select_sector(sec_idx: int) -> void:
	selected_sector = sec_idx
	
	var names = ["Desert Canyon", "Cyber Factory", "Tropical Rainforest", "Orbital Station", "Core Nexus AI"]
	sector_title_label.text = "SECTOR %d: %s" % [sec_idx, names[sec_idx - 1]]
	
	# Clear old mission list items
	for child in mission_list_container.get_children():
		child.queue_free()
		
	# Populate missions for this sector
	for m in range(1, 4):
		var m_id = "S%d_M%d" % [sec_idx, m]
		var def: MissionDefinition = missions_data.get(m_id)
		if def:
			var btn = Button.new()
			btn.custom_minimum_size = Vector2(0, 44)
			btn.text = "MISSION %d: %s  [%d WAVES | +%d 🔩]" % [m, def.title, def.total_waves, def.scrap_reward]
			btn.pressed.connect(func(): _select_mission(m_id))
			mission_list_container.add_child(btn)
			
	_select_mission("S%d_M1" % sec_idx)

func _select_mission(m_id: String) -> void:
	selected_mission_id = m_id
	var def: MissionDefinition = missions_data.get(m_id)
	if def:
		mission_details_label.text = "%s\n\n%s\n\nTarget Score: %d | Waves: %d | Boss: %s" % [
			def.title.to_upper(),
			def.description,
			def.target_score,
			def.total_waves,
			"YES" if def.is_boss_mission else "NO"
		]

func _on_launch_mission() -> void:
	var def: MissionDefinition = missions_data.get(selected_mission_id)
	if def:
		# Save active mission to game manager
		var gm = get_tree().get_first_node_in_group("game_manager")
		if gm and gm.campaign_state:
			gm.campaign_state.current_mission = selected_mission_id
			
		get_tree().change_scene_to_file("res://scenes/world/TrainingArena.tscn")
