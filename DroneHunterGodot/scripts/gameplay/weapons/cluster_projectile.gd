class_name ClusterProjectile
extends Projectile

var fuse_timer: float = 0.55
var has_split: bool = false
var submunition_scene: PackedScene = preload("res://scenes/weapons/GenericProjectile.tscn")

func _physics_process(delta: float) -> void:
	if has_split:
		return
	fuse_timer -= delta
	if fuse_timer <= 0.0:
		_split_and_detonate()
		return
	super._physics_process(delta)

func _handle_hit(target: Node2D) -> void:
	if has_split:
		return
	if not is_instance_valid(target) or target == _source:
		return
		
	var valid_source: Object = _source if is_instance_valid(_source) else null
	var receiver = target.get_node_or_null("DamageReceiver")
	if receiver != null and receiver.has_method("take_damage"):
		receiver.take_damage(Hit.new(damage, Hit.DamageType.EXPLOSION, valid_source, global_position))
	elif target.has_method("take_damage"):
		target.take_damage(damage)
		
	_split_and_detonate()

func _split_and_detonate() -> void:
	if has_split:
		return
	has_split = true
	
	var root = get_tree().current_scene if get_tree() and get_tree().current_scene else get_parent()
	if root and submunition_scene:
		# Spawn 6 submunition bomblets in 360 degree starburst
		for i in range(6):
			var sub = submunition_scene.instantiate() as Projectile
			if sub:
				root.add_child(sub)
				var angle = global_rotation + (i * (TAU / 6.0)) + randf_range(-0.15, 0.15)
				sub.global_position = global_position
				sub.global_rotation = angle
				sub.setup(speed * 0.75, damage * 0.35, Hit.DamageType.EXPLOSION, _source, "weapons/cluster_torpedo.png")
				
	_safe_destroy()
