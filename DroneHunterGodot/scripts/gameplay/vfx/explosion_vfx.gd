class_name ExplosionVFX
extends Node2D

@onready var fireball: Sprite2D = $Fireball
@onready var shockwave: Sprite2D = $Shockwave

func _ready() -> void:
	z_index = 25
	_play_animation()

func _play_animation() -> void:
	# Randomize initial rotation
	rotation = randf_range(0, TAU)
	
	# Fireball burst
	fireball.scale = Vector2(0.3, 0.3)
	fireball.modulate = Color(1.5, 1.2, 0.8, 1.0)
	
	# Shockwave ring
	shockwave.scale = Vector2(0.1, 0.1)
	shockwave.modulate = Color(1.0, 0.7, 0.3, 0.9)
	
	var tween = create_tween().set_parallel(true)
	
	# Fireball expand & fade
	tween.tween_property(fireball, "scale", Vector2(1.2, 1.2), 0.35).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(fireball, "modulate:a", 0.0, 0.35).set_delay(0.1)
	
	# Shockwave expand & fade
	tween.tween_property(shockwave, "scale", Vector2(2.2, 2.2), 0.4).set_ease(Tween.EASE_OUT)
	tween.tween_property(shockwave, "modulate:a", 0.0, 0.38).set_delay(0.05)
	
	# Screen shake
	if is_inside_tree():
		var cam = get_tree().get_first_node_in_group("camera")
		if cam and cam.has_method("add_trauma"):
			cam.add_trauma(0.25)
			
	tween.chain().tween_callback(queue_free)
