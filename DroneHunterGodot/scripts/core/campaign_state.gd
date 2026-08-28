class_name CampaignState
extends RefCounted

var current_mission: String = "S1_M1"
var completed_missions: Array[String] = []
var unlocked_missions: Array[String] = ["S1_M1"]
var completed_sectors: Array[int] = []
var unlocked_sectors: Array[int] = [1]
var campaign_completed: bool = false
var new_game_plus_count: int = 0

func _init() -> void:
	reset()

func reset() -> void:
	current_mission = "S1_M1"
	completed_missions.clear()
	unlocked_missions = ["S1_M1"]
	completed_sectors.clear()
	unlocked_sectors = [1]
	campaign_completed = false
	new_game_plus_count = 0

func to_dict() -> Dictionary:
	return {
		"current_mission": current_mission,
		"completed_missions": completed_missions.duplicate(),
		"unlocked_missions": unlocked_missions.duplicate(),
		"completed_sectors": completed_sectors.duplicate(),
		"unlocked_sectors": unlocked_sectors.duplicate(),
		"campaign_completed": campaign_completed,
		"new_game_plus_count": new_game_plus_count
	}

func from_dict(data: Dictionary) -> void:
	current_mission = data.get("current_mission", "S1_M1")
	completed_missions.clear()
	for m in data.get("completed_missions", []):
		completed_missions.append(str(m))
	unlocked_missions.clear()
	for u in data.get("unlocked_missions", ["S1_M1"]):
		unlocked_missions.append(str(u))
	completed_sectors.clear()
	for cs in data.get("completed_sectors", []):
		completed_sectors.append(int(cs))
	unlocked_sectors.clear()
	for us in data.get("unlocked_sectors", [1]):
		unlocked_sectors.append(int(us))
	campaign_completed = bool(data.get("campaign_completed", false))
	new_game_plus_count = int(data.get("new_game_plus_count", 0))

func is_valid() -> bool:
	return (
		current_mission != "" and
		unlocked_missions.size() > 0 and
		unlocked_sectors.size() > 0 and
		new_game_plus_count >= 0
	)
