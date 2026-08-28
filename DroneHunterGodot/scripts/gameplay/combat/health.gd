class_name Health
extends Node

signal died
signal health_changed(old_value: float, new_value: float, max_health: float)
signal damage_taken(amount: float, current_health: float)

@export var max_hp: float = 100.0
@export var base_armor: float = 0.0
@export var max_shield: float = 0.0

var current_hp: float
var current_shield: float
var is_dead: bool = false

func _ready() -> void:
	current_hp = max_hp
	current_shield = max_shield

func apply_damage(amount: float) -> void:
	if is_dead:
		return
		
	var old_hp = current_hp
	current_hp -= amount
	
	if current_hp <= 0.0:
		current_hp = 0.0
		is_dead = true
		
	damage_taken.emit(amount, current_hp)
	health_changed.emit(old_hp, current_hp, max_hp)
	
	if is_dead:
		died.emit()

func heal(amount: float) -> void:
	if is_dead:
		return
		
	var old_hp = current_hp
	current_hp += amount
	if current_hp > max_hp:
		current_hp = max_hp
		
	health_changed.emit(old_hp, current_hp, max_hp)
