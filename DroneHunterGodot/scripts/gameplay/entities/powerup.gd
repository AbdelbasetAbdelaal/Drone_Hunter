class_name Powerup
extends Area2D

enum PowerupType {
	BATTERY = 0,
	SHIELD = 1,
	OVERCLOCK = 2,
	SLOWMO = 3,
	SCRAP = 4,
	WINGMAN = 5,
	WEAPON = 6
}

@export var powerup_type: int = PowerupType.BATTERY
@export var scrap_amount: int = 50

var _time_accum: float = 0.0
var _magnetic_range: float = 200.0
var _magnet_speed: float = 450.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var label: Label = $Label

func _ready() -> void:
	collision_layer = 32 # Effect / Pickup layer
	collision_mask = 1  # Player layer
	body_entered.connect(_on_body_entered)
	_setup_visuals()

func setup(type: int, amount: int = 50) -> void:
	powerup_type = type
	scrap_amount = amount
	_setup_visuals()

func _setup_visuals() -> void:
	if not is_inside_tree():
		return
		
	var color := Color.SPRING_GREEN
	var text_icon := "🔋"
	
	match powerup_type:
		PowerupType.BATTERY:
			color = Color(0.2, 0.9, 0.4)
			text_icon = "HP"
		PowerupType.SHIELD:
			color = Color(0.2, 0.6, 1.0)
			text_icon = "SHD"
		PowerupType.OVERCLOCK:
			color = Color(1.0, 0.3, 0.2)
			text_icon = "OVR"
		PowerupType.SLOWMO:
			color = Color(0.8, 0.4, 1.0)
			text_icon = "SLO"
		PowerupType.SCRAP:
			color = Color(1.0, 0.85, 0.2)
			text_icon = "$"
		PowerupType.WINGMAN:
			color = Color(0.2, 0.9, 0.9)
			text_icon = "WNG"
		PowerupType.WEAPON:
			color = Color(1.0, 0.6, 0.1)
			text_icon = "WPN"

	if sprite:
		sprite.modulate = color
	if label:
		label.text = text_icon
		label.modulate = color

func _physics_process(delta: float) -> void:
	_time_accum += delta
	# Floating bobbing
	position.y += sin(_time_accum * 4.0) * 12.0 * delta
	
	# Magnetic pull to player
	if not is_inside_tree():
		return
	var player = get_tree().get_first_node_in_group("player") as Node2D
	if player and is_instance_valid(player):
		var dist = global_position.distance_to(player.global_position)
		if dist <= _magnetic_range:
			var dir = (player.global_position - global_position).normalized()
			global_position += dir * _magnet_speed * delta

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_apply_to_player(body)
		queue_free()

func _apply_to_player(player: Node2D) -> void:
	var health = player.get_node_or_null("Health") as Health
	var ability = player.get_node_or_null("AbilityController")
	var weapons = player.get_node_or_null("WeaponController")
	
	match powerup_type:
		PowerupType.BATTERY:
			if health:
				health.heal(35.0)
		PowerupType.SHIELD:
			if health:
				health.current_shield = min(health.max_shield, health.current_shield + 40.0)
		PowerupType.OVERCLOCK:
			if ability and ability.has_method("_start_overdrive"):
				ability._start_overdrive()
		PowerupType.SCRAP:
			var game_mgr = get_tree().get_first_node_in_group("game_manager")
			if game_mgr and game_mgr.has_method("add_scrap"):
				game_mgr.add_scrap(scrap_amount)
		PowerupType.WINGMAN:
			var arena = get_tree().current_scene
			var wingman_scene = load("res://scenes/entities/Wingman.tscn")
			if arena and wingman_scene:
				var wm = wingman_scene.instantiate() as Node2D
				arena.add_child(wm)
				wm.global_position = player.global_position + Vector2(-50, -40)
		PowerupType.WEAPON:
			if weapons and weapons.has_method("cycle_weapon"):
				weapons.cycle_weapon(1)
