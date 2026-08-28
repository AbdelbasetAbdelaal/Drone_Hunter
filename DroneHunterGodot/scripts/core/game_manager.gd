class_name GameManagerNode
extends Node

const MAX_UPGRADE_LEVEL: int = 5
const UPGRADE_COSTS: Dictionary = {
	1: 150,
	2: 300,
	3: 600,
	4: 1200,
	5: 2500
}

signal scrap_changed(new_amount: int)
signal drone_selected(drone_id: String)
signal upgrade_purchased(category: String, new_level: int)

var state_manager: GameStateManager
var campaign_state: CampaignState

var selected_drone_id: String = "striker"
var scrap: int = 500
var total_score: int = 0
var difficulty_mode: int = 1
var is_fullscreen: bool = false

var unlocked_drones: Array[String] = ["striker", "interceptor", "assault", "arc", "command"]
var upgrade_levels: Dictionary = {
	"hull": 1,
	"energy": 1,
	"weapon": 1,
	"mobility": 1
}

func _ready() -> void:
	add_to_group("game_manager")
	state_manager = GameStateManager.new()
	campaign_state = CampaignState.new()
	state_manager.state_changed.connect(_on_state_changed)

func add_scrap(amount: int) -> void:
	scrap += max(0, amount)
	scrap_changed.emit(scrap)

func select_drone(drone_id: String) -> void:
	if drone_id in unlocked_drones:
		selected_drone_id = drone_id
		drone_selected.emit(drone_id)

func get_upgrade_cost(category: String) -> int:
	var lvl = upgrade_levels.get(category, 1)
	return UPGRADE_COSTS.get(lvl, 999999)

func purchase_upgrade(category: String) -> bool:
	var lvl = upgrade_levels.get(category, 1)
	if lvl >= MAX_UPGRADE_LEVEL:
		return false
		
	var cost = get_upgrade_cost(category)
	if scrap >= cost:
		scrap -= cost
		upgrade_levels[category] = lvl + 1
		scrap_changed.emit(scrap)
		upgrade_purchased.emit(category, lvl + 1)
		return true
	return false

func apply_upgrades_to_player(player: Player) -> void:
	if not player:
		return
		
	# 1. Hull (+25 HP per level)
	var hull_lvl = upgrade_levels.get("hull", 1)
	var base_hp = player.drone_class.max_health if player.drone_class else 100.0
	var new_max_hp = base_hp + ((hull_lvl - 1) * 25.0)
	if player.health:
		player.health.max_hp = new_max_hp
		player.health.current_hp = min(player.health.current_hp, new_max_hp)
		
	# 2. Energy (+15 NRG per level)
	var energy_lvl = upgrade_levels.get("energy", 1)
	var base_energy = player.drone_class.max_energy if player.drone_class else 100.0
	player.max_energy = base_energy + ((energy_lvl - 1) * 15.0)
	player.current_energy = min(player.current_energy, player.max_energy)
	
	# 3. Mobility (+5% Speed per level)
	var mobility_lvl = upgrade_levels.get("mobility", 1)
	var base_speed = player.drone_class.max_speed if player.drone_class else 520.0
	player.max_speed = base_speed * (1.0 + ((mobility_lvl - 1) * 0.05))

func _on_state_changed(old_state: GameStateManager.State, new_state: GameStateManager.State) -> void:
	print("[GAME_MANAGER] State changed: ", state_manager.state_to_string(old_state), " -> ", state_manager.state_to_string(new_state))
