class_name GameManagerNode
extends Node

var state_manager: GameStateManager
var campaign_state: CampaignState

var selected_drone_id: String = "striker"
var scrap: int = 0
var highscore: int = 0
var difficulty_mode: int = 1
var is_fullscreen: bool = false

func _ready() -> void:
	state_manager = GameStateManager.new()
	campaign_state = CampaignState.new()
	state_manager.state_changed.connect(_on_state_changed)

func _on_state_changed(old_state: GameStateManager.State, new_state: GameStateManager.State) -> void:
	print("[GAME_MANAGER] State changed: ", state_manager.state_to_string(old_state), " -> ", state_manager.state_to_string(new_state))
