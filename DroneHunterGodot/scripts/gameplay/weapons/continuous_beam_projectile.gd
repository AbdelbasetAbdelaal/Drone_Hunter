class_name ContinuousBeamProjectile
extends Node2D

@export var max_length: float = 1200.0
@export var damage_per_sec: float = 180.0

var source_node: Node2D = null
var is_active: bool = true
var _line: Line2D
var _ray: RayCast2D

func _ready() -> void:
	z_index = 20
	_line = Line2D.new()
	_line.width = 12.0
	_line.default_color = Color(0.2, 0.85, 1.0, 0.85)
	_line.add_point(Vector2.ZERO)
	_line.add_point(Vector2.RIGHT * max_length)
	add_child(_line)
	
	_ray = RayCast2D.new()
	_ray.target_position = Vector2.RIGHT * max_length
	_ray.collision_mask = 2 | 16 # Enemies (2) and Structures (16)
	_ray.enabled = true
	add_child(_ray)

func setup(p_source: Node2D, p_damage: float) -> void:
	source_node = p_source
	damage_per_sec = p_damage * 12.0

func _physics_process(delta: float) -> void:
	if not is_active:
		queue_free()
		return
		
	if source_node and is_instance_valid(source_node):
		var target_end = Vector2.RIGHT * max_length
		if _ray.is_colliding():
			var col_pt = _ray.get_collision_point()
			target_end = to_local(col_pt)
			var collider = _ray.get_collider()
			if collider and is_instance_valid(collider):
				var receiver = collider.get_node_or_null("DamageReceiver")
				if receiver and receiver.has_method("take_damage"):
					receiver.take_damage(Hit.new(damage_per_sec * delta, Hit.DamageType.NORMAL, source_node, col_pt))
					
		_line.set_point_position(1, target_end)
		
	# Fade out after brief duration if not renewed
	is_active = false
	var tween = create_tween()
	tween.tween_property(_line, "modulate:a", 0.0, 0.1)
	tween.tween_callback(queue_free)
