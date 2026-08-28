class_name WeaponController
extends Node2D

@export var muzzle_offset: Vector2 = Vector2(88.0, 0.0) # Player STRIKER primary mount profile

var weapons: Array[WeaponDefinition] = []
var active_weapon_index: int = 0
var behaviors: Array[WeaponBehavior] = []

var _cooldown_timer: float = 0.0

func _ready() -> void:
	_init_weapons()

func _init_weapons() -> void:
	# Define all 11 weapons based on Phase 2 requirements and game_data.py
	
	_add_weapon("pulse", "Pulse Laser", 1, 0.18, 25, 950, 1, 0.0, "projectiles/bullet_pulse.png", PulseBehavior)
	_add_weapon("rapid", "Rapid Autocannon", 2, 0.08, 8, 1100, 1, 3.0, "projectiles/bullet_pulse.png", RapidBehavior)
	_add_weapon("scatter", "Spread Cannon", 2, 0.75, 10, 600, 5, 22.0, "projectiles/bullet_scatter.png", ScatterBehavior)
	_add_weapon("missile", "Heavy Missile", 3, 2.5, 65, 320, 1, 0.0, "weapons/missile/projectile.png", MissileBehavior)
	_add_weapon("barrage", "Missile Barrage", 3, 2.2, 38, 650, 4, 28.0, "weapons/barrage/projectile.png", BarrageBehavior)
	_add_weapon("plasma", "Heavy Plasma Cannon", 2, 0.85, 90, 500, 1, 0.0, "weapons/plasma/projectile.png", PlasmaBehavior)
	_add_weapon("rail", "Precision Railgun", 1, 1.10, 115, 1800, 1, 0.0, "weapons/rail/projectile.png", RailgunBehavior)
	_add_weapon("beam", "Plasma Cutting Beam", 2, 0.08, 26, 1500, 1, 0.0, "weapons/beam/projectile.png", BeamBehavior)
	_add_weapon("tesla", "Tesla Arc", 2, 0.40, 44, 1100, 1, 0.0, "weapons/tesla/projectile.png", TeslaBehavior)
	_add_weapon("cluster", "Cluster Torpedo", 4, 2.0, 85, 550, 1, 0.0, "weapons/cluster/projectile.png", ClusterBehavior)
	_add_weapon("emp", "EMP Shockwave Pulse", 1, 0.50, 30, 1200, 1, 0.0, "weapons/emp/projectile.png", EMPBehavior)

func _add_weapon(id: String, display_name: String, slot: int, cooldown: float, damage: float, speed: float, count: int, spread: float, asset: String, behavior_class) -> void:
	var def: WeaponDefinition = WeaponDefinition.new()
	def.weapon_id = id
	def.display_name = display_name
	def.slot = slot
	def.cooldown = cooldown
	def.damage = damage
	def.speed = speed
	def.projectiles_per_shot = count
	def.spread_deg = spread
	def.projectile_asset = asset
	weapons.append(def)
	behaviors.append(behavior_class.new(def, self))

func _physics_process(delta: float) -> void:
	if _cooldown_timer > 0.0:
		_cooldown_timer = max(0.0, _cooldown_timer - delta)
		
	_handle_input()

func _handle_input() -> void:
	if Input.is_action_just_pressed("next_weapon") or Input.is_physical_key_pressed(KEY_TAB):
		cycle_weapon(1)
	elif Input.is_action_just_pressed("previous_weapon") or Input.is_physical_key_pressed(KEY_Q):
		cycle_weapon(-1)
		
	# Direct physical number keys 1-6
	var keys = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6]
	for i in range(keys.size()):
		if Input.is_physical_key_pressed(keys[i]) or Input.is_key_pressed(keys[i]) or Input.is_action_just_pressed("weapon_slot_" + str(i + 1)):
			for w_idx in range(weapons.size()):
				if weapons[w_idx].slot == (i + 1):
					active_weapon_index = w_idx
					break

func cycle_weapon(direction: int) -> void:
	if weapons.size() == 0:
		return
	active_weapon_index = (active_weapon_index + direction) % weapons.size()
	if active_weapon_index < 0:
		active_weapon_index = weapons.size() - 1

func can_fire_primary() -> bool:
	return _cooldown_timer <= 0.0

func try_fire_primary() -> bool:
	if not can_fire_primary() or behaviors.size() == 0:
		return false
	
	var active_def = weapons[active_weapon_index]
	var active_behavior = behaviors[active_weapon_index]
	
	var spawn_pos = global_position + muzzle_offset.rotated(global_rotation)
	var spawn_rot = global_rotation
	
	active_behavior.fire(spawn_pos, spawn_rot)
	
	_cooldown_timer = active_def.cooldown
	return true
