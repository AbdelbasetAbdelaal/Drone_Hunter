class_name SaveManager
extends RefCounted

const SAVE_PATH_TEMPLATE = "user://save_slot_{slot}.json"
const CURRENT_SCHEMA_VERSION = 1
const VALID_SLOTS = [0, 1, 2]

func get_save_path(slot: int) -> String:
	return SAVE_PATH_TEMPLATE.format({"slot": clamp(slot, 0, 2)})

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
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: Failed to open file for writing: " + path)
		return false
	file.store_string(JSON.stringify(payload, "\t"))
	file.close()
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
	if not is_save_valid(data):
		push_warning("SaveManager: Invalid save data payload in slot %d." % slot)
		return {}
		
	return data

func delete_slot(slot: int) -> bool:
	if not (slot in VALID_SLOTS):
		return false
	var path = get_save_path(slot)
	if FileAccess.file_exists(path):
		return DirAccess.remove_absolute(path) == OK
	return true

func is_save_valid(payload: Dictionary) -> bool:
	if payload.is_empty():
		return false
	var ver = payload.get("save_version", 0)
	if ver < 1:
		return false
	var scrap = payload.get("scrap", 0)
	if scrap < 0:
		return false
	return true
