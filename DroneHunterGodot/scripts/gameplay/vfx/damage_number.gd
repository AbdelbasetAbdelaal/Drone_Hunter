class_name DamageNumber
extends Node2D

@onready var label: Label = $Label

func setup(amount: float, is_shield: bool = false, is_critical: bool = false) -> void:
	if not is_inside_tree():
		await ready
		
	var display_text = str(int(amount)) if amount >= 1.0 else "%.1f" % amount
	label.text = display_text
	
	if is_shield:
		label.modulate = Color(0.3, 0.8, 1.0, 1.0) # Cyan for shield hits
		label.text = "🛡 " + display_text
	elif is_critical or amount >= 50.0:
		label.modulate = Color(1.0, 0.85, 0.1, 1.0) # Gold for heavy hits
		label.text = "⚡ " + display_text
	else:
		label.modulate = Color(1.0, 0.35, 0.25, 1.0) # Red for normal hull hits

	# Dynamic pop animation
	scale = Vector2(0.6, 0.6)
	var tween = create_tween().set_parallel(true)
	tween.tween_property(self, "scale", Vector2(1.2, 1.2), 0.15).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tween.tween_property(self, "position:y", position.y - 35.0, 0.55).set_ease(Tween.EASE_OUT)
	tween.chain().tween_property(self, "scale", Vector2(0.8, 0.8), 0.2)
	tween.tween_property(self, "modulate:a", 0.0, 0.25).set_delay(0.3)
	tween.chain().tween_callback(queue_free)
