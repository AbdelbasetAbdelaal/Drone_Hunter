class_name SectorMap
extends Control

var selected_sector: int = 1
var selected_mission_id: String = "S1_M1"
var missions_data: Dictionary = {}

@onready var sector_title_label: Label = $Content/RightPanel/SectorTitle
@onready var mission_list_container: VBoxContainer = $Content/RightPanel/MissionList
@onready var mission_details_lbl: Label = $Content/RightPanel/MissionDetails

@onready var launch_btn: Button = $Footer/LaunchBtn
@onready var back_btn: Button = $Footer/BackBtn

const SECTOR_NAMES = [
	"CYBER FACTORY",
	"CORE SECTOR",
	"REACTOR ZONE",
	"DEFENSE GRID",
	"DRONE COMMAND"
]

func _ready() -> void:
	_load_all_missions()
	_setup_sector_buttons()
	_select_sector(1)
	
	var gm = get_tree().get_first_node_in_group("game_manager")
	launch_btn.pressed.connect(_on_launch_mission)
	back_btn.pressed.connect(func():
		if gm:
			gm.navigate_to_state(GameStateManager.State.HANGAR)
	)

func _load_all_missions() -> void:
	for s in range(1, 6):
		for m in range(1, 6):
			var m_id = "S%d_M%d" % [s, m]
			var p = "res://resources/missions/%s.tres" % m_id
			if ResourceLoader.exists(p):
				missions_data[m_id] = load(p) as MissionDefinition

func _setup_sector_buttons() -> void:
	var sector_btns_container = $Content/LeftPanel/SectorButtons
	var gm = get_tree().get_first_node_in_group("game_manager")
	var cs = gm.campaign_state if gm else null
	
	for i in range(1, 6):
		var btn = sector_btns_container.get_node_or_null("Sector" + str(i)) as Button
		if btn:
			btn.text = "SECTOR %d: %s" % [i, SECTOR_NAMES[i - 1]]
			var sec_unlocked = cs.is_sector_unlocked(i) if cs else (i == 1)
			btn.disabled = not sec_unlocked
			btn.pressed.connect(func(): _select_sector(i))

func _select_sector(sec_idx: int) -> void:
	selected_sector = sec_idx
	sector_title_label.text = "SECTOR %d: %s" % [sec_idx, SECTOR_NAMES[sec_idx - 1]]
	
	for child in mission_list_container.get_children():
		child.queue_free()
		
	var gm = get_tree().get_first_node_in_group("game_manager")
	var cs = gm.campaign_state if gm else null
	
	for m_idx in range(1, 6):
		var m_id = "S%d_M%d" % [sec_idx, m_idx]
		var def: MissionDefinition = missions_data.get(m_id)
		if not def:
			continue
			
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(0, 44)
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		
		var is_unlocked = cs.is_mission_unlocked(m_id) if cs else (sec_idx == 1 and m_idx == 1)
		var is_completed = cs.is_mission_completed(m_id) if cs else false
		
		var tag = ""
		if not is_unlocked:
			tag = "[LOCKED] "
			btn.disabled = true
		elif is_completed:
			tag = "[COMPLETED] "
		elif m_id == (cs.current_mission if cs else "S1_M1"):
			tag = "[ACTIVE] "
			
		btn.text = "%sMISSION %d: %s [+%d 🔩]" % [tag, m_idx, def.title, def.scrap_reward]
		btn.pressed.connect(func(): _select_mission(m_id))
		mission_list_container.add_child(btn)
		
	var default_m = "S%d_M1" % sec_idx
	_select_mission(default_m)

func _select_mission(m_id: String) -> void:
	selected_mission_id = m_id
	var def: MissionDefinition = missions_data.get(m_id)
	if not def:
		return
		
	if mission_details_lbl:
		mission_details_lbl.text = "%s\n\n%s\n\nOBJECTIVE: %s\nDIFFICULTY: Level %d\nREWARD: +%d 🔩 Scrap" % [
			def.title.to_upper(),
			def.lore if def.lore != "" else def.description,
			def.primary_objective.replace("_", " ").capitalize(),
			def.difficulty,
			def.scrap_reward
		]

func _on_launch_mission() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	var cs = gm.campaign_state if gm else null
	
	if cs and not cs.is_mission_unlocked(selected_mission_id):
		return # Enforce campaign authority: do not launch locked mission
		
	if gm and cs:
		cs.current_mission = selected_mission_id
		gm.navigate_to_state(GameStateManager.State.MISSION_BRIEFING)
