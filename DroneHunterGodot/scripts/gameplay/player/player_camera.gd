class_name PlayerCamera
extends Camera2D

@export var decay: float = 1.4 # Trauma decay per second
@export var max_offset: Vector2 = Vector2(16.0, 16.0) # Max pixel shake
@export var max_roll: float = 0.04 # Max rotation shake in radians

var trauma: float = 0.0 # Current trauma [0.0, 1.0]
var trauma_power: float = 2.0 # Non-linear trauma exponent
var _noise_y: float = 0.0

func _ready() -> void:
	add_to_group("camera")

func add_trauma(amount: float) -> void:
	trauma = clamp(trauma + amount, 0.0, 1.0)

func _process(delta: float) -> void:
	if trauma > 0.0:
		trauma = max(0.0, trauma - decay * delta)
		_noise_y += delta * 60.0
		
		var shake_amount = pow(trauma, trauma_power)
		rotation = max_roll * shake_amount * sin(_noise_y * 1.5)
		offset = Vector2(
			max_offset.x * shake_amount * sin(_noise_y * 2.1),
			max_offset.y * shake_amount * cos(_noise_y * 2.4)
		)
	else:
		rotation = 0.0
		offset = Vector2.ZERO
