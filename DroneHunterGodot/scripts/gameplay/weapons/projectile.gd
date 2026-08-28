class_name Projectile
extends Area2D

@export var speed: float = 950.0
@export var damage: float = 25.0
@export var max_range: float = 1400.0
@export var damage_type: int = Hit.DamageType.NORMAL

var _traveled_distance: float = 0.0
var _source: Node2D = null

func setup(p_speed: float, p_damage: float, p_damage_type: int, p_source: Node2D, p_asset_path: String = "") -> void:
	speed = p_speed
	damage = p_damage
	damage_type = p_damage_type
	_source = p_source
	
	if p_asset_path != "":
		var full_path = "res://assets/" + p_asset_path
		if ResourceLoader.exists(full_path):
			var tex = load(full_path)
			var sprite = get_node_or_null("Sprite2D") as Sprite2D
			if sprite and tex:
				sprite.texture = tex
				var max_dim: float = max(tex.get_width(), tex.get_height())
				if max_dim > 200.0:
					var target_size: float = 48.0
					var s: float = target_size / max_dim
					sprite.scale = Vector2(s, s)
				else:
					sprite.scale = Vector2(0.7, 0.7)

func _ready() -> void:
	top_level = true
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(delta: float) -> void:
	var move_amount: float = speed * delta
	global_position += Vector2.RIGHT.rotated(global_rotation) * move_amount
	_traveled_distance += move_amount
	
	if _traveled_distance >= max_range:
		queue_free()

func _on_body_entered(body: Node2D) -> void:
	_handle_hit(body)

func _on_area_entered(area: Area2D) -> void:
	_handle_hit(area)

func _handle_hit(target: Node2D) -> void:
	# Avoid hitting self source
	if target == _source:
		return
		
	# Find damage receiver
	var receiver: DamageReceiver = null
	if target.has_node("DamageReceiver"):
		receiver = target.get_node("DamageReceiver") as DamageReceiver
		
	if receiver != null:
		var hit = Hit.new(damage, damage_type, _source, global_position)
		receiver.take_damage(hit)
	elif target.has_method("take_damage"):
		target.take_damage(damage) # Fallback for old tests
	
	queue_free()
