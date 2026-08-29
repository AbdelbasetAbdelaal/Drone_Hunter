class_name GroundObjectiveTarget
extends StaticBody2D

signal target_damaged(current_hp: float, max_hp: float)
signal target_destroyed(target_id: String)

@export var target_id: String = "radar_command"
@export var display_name: String = "Radar Command Tower"
@export var max_health: float = 300.0

@onready var health: Health = $Health
@onready var damage_receiver: DamageReceiver = $DamageReceiver
@onready var sprite: Sprite2D = $Sprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var health_bar: ProgressBar = $HealthBar

var is_destroyed: bool = false

const TARGET_TEXTURES = {
	"radar_command": "res://assets/environment/structures/radar_command_tower.png",
	"communication_hub": "res://assets/environment/structures/radar_dish.png",
	"missile_complex": "res://assets/environment/structures/missile_launcher.png",
	"power_reactor": "res://assets/environment/structures/critical_power_reactor.png",
	"weapons_factory": "res://assets/environment/cyber_factory/machinery/generator_01.png",
	"cyber_defense_core": "res://assets/environment/structures/shield_generator.png"
}

func _ready() -> void:
	add_to_group("objective_targets")
	
	if not health:
		health = Health.new()
		health.name = "Health"
		add_child(health)
		
	health.max_hp = max_health
	health.current_hp = max_health
	health.max_shield = 0.0
	health.current_shield = 0.0
	health.health_changed.connect(_on_health_changed)
	health.died.connect(_on_died)
	
	if not damage_receiver:
		damage_receiver = DamageReceiver.new()
		damage_receiver.name = "DamageReceiver"
		add_child(damage_receiver)
		
	damage_receiver.health = health
	
	_setup_visuals()
	
	if health_bar:
		health_bar.max_value = max_health
		health_bar.value = max_health
		health_bar.visible = false

func configure_target(t_id: String, def_level: int = 1) -> void:
	target_id = t_id
	display_name = t_id.replace("_", " ").capitalize()
	max_health = 250.0 + (def_level * 50.0)
	if health:
		health.max_hp = max_health
		health.current_hp = max_health
	_setup_visuals()

func _setup_visuals() -> void:
	if sprite:
		var tex_path = TARGET_TEXTURES.get(target_id, "res://assets/environment/structures/radar_command_tower.png")
		if ResourceLoader.exists(tex_path):
			sprite.texture = load(tex_path)

func _on_health_changed(_old_v: float, cur: float, max_val: float) -> void:
	if is_destroyed:
		return
	target_damaged.emit(cur, max_val)
	if health_bar:
		health_bar.visible = true
		health_bar.max_value = max_val
		health_bar.value = cur

func _on_died() -> void:
	if is_destroyed:
		return
	is_destroyed = true
	print("GroundObjectiveTarget: Destroyed objective target [%s]" % target_id)
	
	var am = get_tree().get_first_node_in_group("audio_manager")
	if am and am.has_method("play_explosion"):
		am.play_explosion("heavy")
		
	target_destroyed.emit(target_id)
	
	# Spawn explosion VFX if available
	var exp_scene = load("res://scenes/vfx/ExplosionVFX.tscn") as PackedScene
	if exp_scene and get_parent():
		var exp_inst = exp_scene.instantiate() as Node2D
		get_parent().add_child(exp_inst)
		exp_inst.global_position = global_position
		
	queue_free()
