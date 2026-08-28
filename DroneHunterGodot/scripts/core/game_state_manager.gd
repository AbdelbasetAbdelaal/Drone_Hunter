class_name GameStateManager
extends RefCounted

signal state_changed(old_state: State, new_state: State)

enum State {
	MAIN_MENU,
	SAVE_SELECT,
	DRONE_SELECT,
	CAMPAIGN_SELECT,
	MISSION_BRIEFING,
	GAMEPLAY,
	PAUSE,
	HANGAR,
	MISSION_COMPLETE,
	MISSION_FAILED,
	SETTINGS
}

var _current_state: State = State.MAIN_MENU
var _previous_state: State = State.MAIN_MENU

func get_current_state() -> State:
	return _current_state

func get_previous_state() -> State:
	return _previous_state

func change_state(new_state: State) -> void:
	if _current_state == new_state:
		return
	_previous_state = _current_state
	_current_state = new_state
	state_changed.emit(_previous_state, _current_state)

func state_to_string(state: State) -> String:
	match state:
		State.MAIN_MENU: return "MAIN_MENU"
		State.SAVE_SELECT: return "SAVE_SELECT"
		State.DRONE_SELECT: return "DRONE_SELECT"
		State.CAMPAIGN_SELECT: return "CAMPAIGN_SELECT"
		State.MISSION_BRIEFING: return "MISSION_BRIEFING"
		State.GAMEPLAY: return "GAMEPLAY"
		State.PAUSE: return "PAUSE"
		State.HANGAR: return "HANGAR"
		State.MISSION_COMPLETE: return "MISSION_COMPLETE"
		State.MISSION_FAILED: return "MISSION_FAILED"
		State.SETTINGS: return "SETTINGS"
		_: return "UNKNOWN"
