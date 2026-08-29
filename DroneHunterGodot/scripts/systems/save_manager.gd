class_name SaveManager
extends RefCounted

const SAVE_PATH_TEMPLATE = "user://save_slot_{slot}.json"
const CURRENT_SCHEMA_VERSION = 1
const VALID_SLOTS = [0, 1, 2]
const VALID_DRONES = ["striker", "interceptor", "assault", "arc", "command"]
const MAX_UPGRADE_LEVEL = 5

func get_save_path(slot: int) -> String:
	return SAVE_PATH_TEMPLATE.format({"slot": slot})

func has_save(slot: int) -> bool:
	if not (slot in VALID_SLOTS):
		return false
	return FileAccess.file_exists(get_save_path(slot))

func save_slot(slot: int, payload: Dictionary) -> bool:
	if not (slot in VALID_SLOTS):
		push_error("SaveManager: Invalid save slot: %d" % slot)
		return false
		
	payload["save_version"] = CURRENT_SCHEMA_VERSION
	var path = get_save_path(slot)
	var tmp_path = path + ".tmp"
	
	var file = FileAccess.open(tmp_path, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: Failed to open temp file for writing: " + tmp_path)
		return false
	file.store_string(JSON.stringify(payload, "\t"))
	file.flush()
	file.close()
	
	# Atomic replace
	var dir = DirAccess.open("user://")
	if dir:
		if dir.file_exists(path.get_file()):
			dir.remove(path.get_file())
		var err = dir.rename(tmp_path.get_file(), path.get_file())
		if err != OK:
			push_error("SaveManager: Failed to rename temp file.")
			return false
	else:
		return false
		
	return true

func load_slot(slot: int) -> Dictionary:
	if not (slot in VALID_SLOTS):
		return {}
	var path = get_save_path(slot)
	if not FileAccess.file_exists(path):
		return {}
		
	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {}
		
	var text = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var err = json.parse(text)
	if err != OK or not (json.data is Dictionary):
		push_warning("SaveManager: Malformed save file in slot %d. Recovering gracefully." % slot)
		return {}
		
	var data = json.data as Dictionary
	var validated_data = _validate_and_sanitize(data)
	if validated_data.is_empty():
		push_warning("SaveManager: Save data failed validation or is from future version in slot %d." % slot)
		return {}
		
	return validated_data

func delete_slot(slot: int) -> bool:
	if not (slot in VALID_SLOTS):
		return false
	var path = get_save_path(slot)
	if FileAccess.file_exists(path):
		return DirAccess.remove_absolute(path) == OK
	return true

func _validate_and_sanitize(payload: Dictionary) -> Dictionary:
	if payload.is_empty():
		return {}
		
	var ver = payload.get("save_version", 0)
	if ver > CURRENT_SCHEMA_VERSION:
		# Future version - reject safely
		return {}
		
	var sanitized = payload.duplicate(true)
	
	var scrap = int(sanitized.get("scrap", 0))
	if scrap < 0:
		scrap = 0
	sanitized["scrap"] = scrap
	
	var selected_drone = str(sanitized.get("selected_drone_id", "striker"))
	if not (selected_drone in VALID_DRONES):
		selected_drone = "striker"
	sanitized["selected_drone_id"] = selected_drone
	
	if sanitized.has("upgrade_levels") and sanitized["upgrade_levels"] is Dictionary:
		var upgrades = sanitized["upgrade_levels"] as Dictionary
		for cat in upgrades.keys():
			var lvl = int(upgrades[cat])
			upgrades[cat] = clamp(lvl, 0, MAX_UPGRADE_LEVEL)
	else:
		sanitized["upgrade_levels"] = {}
		
	if not (sanitized.has("unlocked_drones") and sanitized["unlocked_drones"] is Array):
		sanitized["unlocked_drones"] = ["striker", "interceptor", "assault", "arc", "command"]
		
	if not (sanitized.has("campaign") and sanitized["campaign"] is Dictionary):
		sanitized["campaign"] = {"unlocked_missions": ["S1_M1"], "completed_missions": [], "current_mission": "S1_M1"}
	
	return sanitized
