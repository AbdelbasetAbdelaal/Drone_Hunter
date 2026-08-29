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
	
	# Safe replace with .bak
	var dir = DirAccess.open("user://")
	if dir:
		var target_file = path.get_file()
		var tmp_file = tmp_path.get_file()
		var bak_file = target_file + ".bak"
		
		if dir.file_exists(bak_file):
			dir.remove(bak_file)
			
		var has_target = dir.file_exists(target_file)
		if has_target:
			var err = dir.rename(target_file, bak_file)
			if err != OK:
				push_error("SaveManager: Failed to backup existing save.")
				dir.remove(tmp_file)
				return false
				
		var err = dir.rename(tmp_file, target_file)
		if err != OK:
			push_error("SaveManager: Failed to rename temp file. Restoring backup.")
			if has_target:
				dir.rename(bak_file, target_file)
			return false
			
		if has_target and dir.file_exists(bak_file):
			dir.remove(bak_file)
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
	if typeof(ver) != TYPE_INT or ver > CURRENT_SCHEMA_VERSION:
		return {}
		
	var sanitized = payload.duplicate(true)
	
	# Scrap
	var scrap_raw = sanitized.get("scrap", 0)
	if typeof(scrap_raw) != TYPE_INT and typeof(scrap_raw) != TYPE_FLOAT:
		scrap_raw = 0
	var scrap = int(scrap_raw)
	if scrap < 0:
		scrap = 0
	sanitized["scrap"] = scrap
	
	# Drone
	var selected_drone = sanitized.get("selected_drone_id", "striker")
	if typeof(selected_drone) != TYPE_STRING or not (selected_drone in VALID_DRONES):
		selected_drone = "striker"
	sanitized["selected_drone_id"] = selected_drone
	
	# Upgrades
	if sanitized.has("upgrade_levels") and typeof(sanitized["upgrade_levels"]) == TYPE_DICTIONARY:
		var upgrades = sanitized["upgrade_levels"] as Dictionary
		for cat in upgrades.keys():
			if typeof(upgrades[cat]) != TYPE_INT and typeof(upgrades[cat]) != TYPE_FLOAT:
				upgrades[cat] = 0
			var lvl = int(upgrades[cat])
			upgrades[cat] = clamp(lvl, 0, MAX_UPGRADE_LEVEL)
	else:
		sanitized["upgrade_levels"] = {}
		
	# Unlocked Drones
	var default_drones = ["striker"]
	if sanitized.has("unlocked_drones"):
		var raw_drones = sanitized["unlocked_drones"]
		if typeof(raw_drones) == TYPE_ARRAY:
			var valid_drones: Array[String] = []
			for d in raw_drones:
				if typeof(d) == TYPE_STRING and d in VALID_DRONES:
					valid_drones.append(d)
			if valid_drones.is_empty():
				sanitized["unlocked_drones"] = default_drones.duplicate()
			else:
				sanitized["unlocked_drones"] = valid_drones
		else:
			sanitized["unlocked_drones"] = default_drones.duplicate()
	else:
		sanitized["unlocked_drones"] = default_drones.duplicate()
		
	# Unlocked Weapons
	if sanitized.has("unlocked_weapons"):
		var raw_weapons = sanitized["unlocked_weapons"]
		if typeof(raw_weapons) == TYPE_ARRAY:
			var valid_weapons: Array[String] = []
			for w in raw_weapons:
				if typeof(w) == TYPE_STRING:
					valid_weapons.append(w)
			sanitized["unlocked_weapons"] = valid_weapons
		else:
			sanitized["unlocked_weapons"] = []
	else:
		sanitized["unlocked_weapons"] = []
		
	# Campaign
	if sanitized.has("campaign") and typeof(sanitized["campaign"]) == TYPE_DICTIONARY:
		# Just checking if valid dictionary
		pass
	else:
		sanitized["campaign"] = {"unlocked_missions": ["S1_M1"], "completed_missions": [], "current_mission": "S1_M1"}
	
	return sanitized
