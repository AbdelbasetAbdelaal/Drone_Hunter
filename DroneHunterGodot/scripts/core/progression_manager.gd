class_name ProgressionManager
extends RefCounted

signal upgrade_purchased(category: String, new_level: int)

var upgrade_levels: Dictionary = {
	"hull": 0,
	"energy": 0,
	"weapon": 0,
	"mobility": 0
}

const MAX_UPGRADE_LEVEL = 5

const UPGRADE_BASE_COSTS = {
	"hull": 100,
	"energy": 100,
	"weapon": 150,
	"mobility": 120
}

const UPGRADE_COST_MULTIPLIER = {
	"hull": 1.5,
	"energy": 1.5,
	"weapon": 1.6,
	"mobility": 1.5
}

func reset() -> void:
	upgrade_levels = {
		"hull": 0,
		"energy": 0,
		"weapon": 0,
		"mobility": 0
	}

func get_upgrade_level(category: String) -> int:
	return int(upgrade_levels.get(category, 0))

func get_upgrade_cost(category: String) -> int:
	var lvl = get_upgrade_level(category)
	if lvl >= MAX_UPGRADE_LEVEL:
		return -1 # Max level reached
	var base = UPGRADE_BASE_COSTS.get(category, 100)
	var mult = UPGRADE_COST_MULTIPLIER.get(category, 1.5)
	return int(base * pow(mult, lvl))

func can_upgrade(category: String, current_scrap: int) -> bool:
	var lvl = get_upgrade_level(category)
	if lvl >= MAX_UPGRADE_LEVEL:
		return false
	var cost = get_upgrade_cost(category)
	return current_scrap >= cost

func purchase_upgrade(category: String, current_scrap: int) -> Dictionary:
	var result = {
		"success": false,
		"new_level": get_upgrade_level(category),
		"cost": 0,
		"remaining_scrap": current_scrap
	}
	
	if not can_upgrade(category, current_scrap):
		return result
		
	var cost = get_upgrade_cost(category)
	upgrade_levels[category] = get_upgrade_level(category) + 1
	result["success"] = true
	result["new_level"] = upgrade_levels[category]
	result["cost"] = cost
	result["remaining_scrap"] = current_scrap - cost
	
	upgrade_purchased.emit(category, result["new_level"])
	return result

func apply_upgrades_to_player(player: Node2D) -> void:
	if not player:
		return
		
	var hull_lvl = get_upgrade_level("hull")
	var energy_lvl = get_upgrade_level("energy")
	var weapon_lvl = get_upgrade_level("weapon")
	var mob_lvl = get_upgrade_level("mobility")
	
	if "health" in player and player.health:
		player.health.max_hp = 100.0 + (hull_lvl * 20.0)
		player.health.current_hp = player.health.max_hp
		
	if "max_energy" in player:
		player.max_energy = 100.0 + (energy_lvl * 20.0)
		player.current_energy = player.max_energy
		
	if "move_speed" in player:
		player.move_speed = 520.0 * (1.0 + mob_lvl * 0.08)

func to_dict() -> Dictionary:
	return upgrade_levels.duplicate()

func from_dict(data: Dictionary) -> void:
	for cat in ["hull", "energy", "weapon", "mobility"]:
		upgrade_levels[cat] = clamp(int(data.get(cat, 0)), 0, MAX_UPGRADE_LEVEL)
