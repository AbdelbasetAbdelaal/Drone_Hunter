class_name CampaignState
extends RefCounted

signal mission_unlocked(mission_id: String)
signal sector_unlocked_signal(sector_id: int)
signal campaign_finished()

var current_mission: String = "S1_M1"
var completed_missions: Array[String] = []
var unlocked_missions: Array[String] = ["S1_M1"]
var completed_sectors: Array[int] = []
var unlocked_sectors: Array[int] = [1]
var campaign_completed: bool = false
var new_game_plus_count: int = 0

const ALL_MISSIONS_ORDERED = [
	"S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5",
	"S2_M1", "S2_M2", "S2_M3", "S2_M4", "S2_M5",
	"S3_M1", "S3_M2", "S3_M3", "S3_M4", "S3_M5",
	"S4_M1", "S4_M2", "S4_M3", "S4_M4", "S4_M5",
	"S5_M1", "S5_M2", "S5_M3", "S5_M4", "S5_M5"
]

const SECTOR_BONUSES = {
	1: 500,
	2: 750,
	3: 1000,
	4: 1500,
	5: 2500
}

const MISSION_REWARDS = {
	1: 150,
	2: 250,
	3: 400,
	4: 600,
	5: 900
}

func _init() -> void:
	reset_campaign()

func reset_campaign() -> void:
	current_mission = "S1_M1"
	completed_missions.clear()
	unlocked_missions = ["S1_M1"]
	completed_sectors.clear()
	unlocked_sectors = [1]
	campaign_completed = false
	new_game_plus_count = 0

func is_mission_unlocked(m_id: String) -> bool:
	return m_id in unlocked_missions

func is_mission_completed(m_id: String) -> bool:
	return m_id in completed_missions

func is_sector_unlocked(sec_id: int) -> bool:
	return sec_id in unlocked_sectors

func is_sector_completed(sec_id: int) -> bool:
	return sec_id in completed_sectors

func complete_mission(m_id: String) -> Dictionary:
	var result = {
		"success": false,
		"reason": "",
		"mission_id": m_id,
		"already_completed": m_id in completed_missions,
		"base_reward": 0,
		"sector_bonus": 0,
		"total_reward": 0,
		"next_mission_unlocked": "",
		"sector_unlocked": 0,
		"campaign_completed": false
	}
	
	# Enforce campaign unlock rule: cannot complete a locked mission
	if not is_mission_unlocked(m_id):
		result["success"] = false
		result["reason"] = "mission_locked"
		push_warning("CampaignState: Attempted to complete locked mission '%s'." % m_id)
		return result
		
	result["success"] = true
	var is_first_time = not (m_id in completed_missions)
	if is_first_time:
		completed_missions.append(m_id)
		
	var num = _get_mission_number(m_id)
	var base_rew = MISSION_REWARDS.get(num, 150)
	result["base_reward"] = base_rew
	
	var sec_bonus = 0
	var cur_sec = _get_sector_id(m_id)
	
	var idx = ALL_MISSIONS_ORDERED.find(m_id)
	if idx != -1:
		if idx + 1 < ALL_MISSIONS_ORDERED.size():
			var next_m = ALL_MISSIONS_ORDERED[idx + 1]
			if not (next_m in unlocked_missions):
				unlocked_missions.append(next_m)
				result["next_mission_unlocked"] = next_m
				mission_unlocked.emit(next_m)
			current_mission = next_m
			
			var next_sec = _get_sector_id(next_m)
			if next_sec > cur_sec:
				if not (cur_sec in completed_sectors):
					completed_sectors.append(cur_sec)
					sec_bonus = SECTOR_BONUSES.get(cur_sec, 500)
					result["sector_bonus"] = sec_bonus
				if not (next_sec in unlocked_sectors):
					unlocked_sectors.append(next_sec)
					result["sector_unlocked"] = next_sec
					sector_unlocked_signal.emit(next_sec)
		else:
			if not (cur_sec in completed_sectors):
				completed_sectors.append(cur_sec)
				sec_bonus = SECTOR_BONUSES.get(cur_sec, 2500)
				result["sector_bonus"] = sec_bonus
			campaign_completed = true
			result["campaign_completed"] = true
			campaign_finished.emit()
			
	result["total_reward"] = base_rew + sec_bonus
	return result

func unlock_next_mission(current_id: String) -> String:
	var idx = ALL_MISSIONS_ORDERED.find(current_id)
	if idx != -1 and idx + 1 < ALL_MISSIONS_ORDERED.size():
		var next_m = ALL_MISSIONS_ORDERED[idx + 1]
		if not (next_m in unlocked_missions):
			unlocked_missions.append(next_m)
			mission_unlocked.emit(next_m)
		return next_m
	return ""

func complete_sector(sec_id: int) -> void:
	if not (sec_id in completed_sectors):
		completed_sectors.append(sec_id)
	if sec_id + 1 <= 5 and not ((sec_id + 1) in unlocked_sectors):
		unlocked_sectors.append(sec_id + 1)
		sector_unlocked_signal.emit(sec_id + 1)

func advance_to_next_mission() -> void:
	var idx = ALL_MISSIONS_ORDERED.find(current_mission)
	if idx != -1 and idx + 1 < ALL_MISSIONS_ORDERED.size():
		current_mission = ALL_MISSIONS_ORDERED[idx + 1]

func _get_sector_id(m_id: String) -> int:
	if m_id.begins_with("S") and m_id.length() >= 2:
		return int(m_id.substr(1, 1))
	return 1

func _get_mission_number(m_id: String) -> int:
	var parts = m_id.split("_M")
	if parts.size() > 1:
		return int(parts[1])
	return 1

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
		current_mission in ALL_MISSIONS_ORDERED and
		unlocked_missions.size() > 0 and
		unlocked_sectors.size() > 0 and
		new_game_plus_count >= 0
	)
