class_name Arena
extends Node2D

@onready var ground_sprite: Sprite2D = $BaseTerrain/DesertGround
@onready var player: Player = $Player
@onready var enemies_director: CombatDirector = $Enemies

func _ready() -> void:
	_configure_mission_environment()

func _configure_mission_environment() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if not gm:
		return
		
	# 1. Apply selected drone class & upgrades to player
	if player:
		var drone_res_path = "res://resources/drones/" + gm.selected_drone_id + ".tres"
		if ResourceLoader.exists(drone_res_path):
			var drone_def = load(drone_res_path) as DroneClassDefinition
			if drone_def:
				player.apply_drone_class(drone_def)
		gm.apply_upgrades_to_player(player)

	# 2. Configure active mission
	var mission_id = gm.campaign_state.current_mission if gm.campaign_state else "S1_M1"
	var mission_path = "res://resources/missions/" + mission_id + ".tres"
	
	if ResourceLoader.exists(mission_path):
		var mission_def = load(mission_path) as MissionDefinition
		if mission_def:
			# Update background
			var bg_full = "res://assets/" + mission_def.sector_background
			if ResourceLoader.exists(bg_full) and ground_sprite:
				var tex = load(bg_full) as Texture2D
				if tex:
					ground_sprite.texture = tex
					
			# Update combat director parameters
			if enemies_director:
				enemies_director.max_waves = mission_def.total_waves
				enemies_director.is_boss_mission = mission_def.is_boss_mission
