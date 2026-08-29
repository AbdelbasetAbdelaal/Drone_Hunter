class_name MissionBriefing
extends Control

var mission_def: MissionDefinition

@onready var title_lbl: Label = $Content/Card/VBox/Header/Title
@onready var meta_lbl: Label = $Content/Card/VBox/Header/Meta
@onready var lore_lbl: Label = $Content/Card/VBox/Lore
@onready var objective_lbl: Label = $Content/Card/VBox/Objective
@onready var defense_lbl: Label = $Content/Card/VBox/Defense
@onready var reward_lbl: Label = $Content/Card/VBox/Reward
@onready var side_obj_lbl: Label = $Content/Card/VBox/SideObjectives

@onready var launch_btn: Button = $Footer/LaunchBtn
@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_load_mission_data()
	launch_btn.pressed.connect(_on_launch)
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn"))

func _load_mission_data() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	var m_id = gm.campaign_state.current_mission if (gm and gm.campaign_state) else "S1_M1"
	var p = "res://resources/missions/%s.tres" % m_id
	if ResourceLoader.exists(p):
		mission_def = load(p) as MissionDefinition
		
	if not mission_def:
		return
		
	var sec_names = ["CYBER FACTORY", "CORE SECTOR", "REACTOR ZONE", "DEFENSE GRID", "DRONE COMMAND"]
	var sec_name = sec_names[clamp(mission_def.sector_index - 1, 0, 4)]
	
	title_lbl.text = "OPERATION: %s" % mission_def.title.to_upper()
	meta_lbl.text = "SECTOR %d: %s  |  MISSION %d  |  DIFFICULTY: LEVEL %d" % [
		mission_def.sector_index, sec_name, mission_def.mission_index, mission_def.difficulty
	]
	
	lore_lbl.text = mission_def.lore
	
	var obj_text = "PRIMARY OBJECTIVE: " + mission_def.primary_objective.replace("_", " ").to_upper()
	if mission_def.primary_objective == "survive":
		obj_text += " (%d SECONDS)" % int(mission_def.duration)
	elif mission_def.primary_objective == "complete_encounters":
		obj_text += " (%d WAVE ENCOUNTERS)" % mission_def.encounter_sequence.size()
	objective_lbl.text = obj_text
	
	defense_lbl.text = "OBJECTIVE TARGET: %s  |  DEFENSE RATING: LEVEL %d" % [
		mission_def.objective_target.replace("_", " ").to_upper(), mission_def.defense_level
	]
	
	reward_lbl.text = "MISSION COMPLETION REWARD: +%d 🔩 SCRAP" % mission_def.scrap_reward
	
	var side_text = "SIDE OBJECTIVES:"
	if mission_def.side_objectives.size() == 0:
		side_text += " None"
	else:
		for s in mission_def.side_objectives:
			var s_type = str(s.get("type", "")).replace("_", " ").to_upper()
			var s_val = str(s.get("value", ""))
			side_text += "\n • %s: %s" % [s_type, s_val]
	side_obj_lbl.text = side_text

func _on_launch() -> void:
	get_tree().change_scene_to_file("res://scenes/world/TrainingArena.tscn")
