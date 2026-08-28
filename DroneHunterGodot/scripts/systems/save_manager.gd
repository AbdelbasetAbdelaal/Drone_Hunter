class_name SaveManager
extends RefCounted

const SAVE_PATH_TEMPLATE = "user://save_slot_{slot}.json"
const CURRENT_SCHEMA_VERSION = 1

func get_save_path(slot: int) -> String:
	return SAVE_PATH_TEMPLATE.format({"slot": slot})

func has_save(slot: int) -> bool:
	return FileAccess.file_exists(get_save_path(slot))

func save_slot(slot: int, payload: Dictionary) -> bool:
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
		return {}
	return json.data

func delete_slot(slot: int) -> bool:
	var path = get_save_path(slot)
	if FileAccess.file_exists(path):
		return DirAccess.remove_absolute(path) == OK
	return true
