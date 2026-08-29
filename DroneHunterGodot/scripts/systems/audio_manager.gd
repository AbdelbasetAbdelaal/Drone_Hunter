class_name AudioManagerNode
extends Node

var music_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []
var ui_players: Array[AudioStreamPlayer] = []
var sound_cache: Dictionary = {}

@export var music_volume: float = 0.8
@export var sfx_volume: float = 0.85
@export var ui_volume: float = 0.85

func _ready() -> void:
	add_to_group("audio_manager")
	
	music_player = AudioStreamPlayer.new()
	music_player.bus = "Music" if AudioServer.get_bus_index("Music") != -1 else "Master"
	add_child(music_player)

	for i in range(24):
		var p = AudioStreamPlayer.new()
		p.bus = "SFX" if AudioServer.get_bus_index("SFX") != -1 else "Master"
		add_child(p)
		sfx_players.append(p)
		
	for i in range(8):
		var u = AudioStreamPlayer.new()
		u.bus = "UI" if AudioServer.get_bus_index("UI") != -1 else "Master"
		add_child(u)
		ui_players.append(u)
		
	_preload_sounds()

func _preload_sounds() -> void:
	var sfx_names = [
		"pulse", "rapid", "scatter", "missile", "barrage",
		"plasma", "rail", "beam", "tesla", "cluster", "emp",
		"hit", "shield_hit", "pickup", "ui_click", "victory"
	]
	
	for s_name in sfx_names:
		var p = "res://assets/audio/sfx/" + s_name + ".wav"
		if ResourceLoader.exists(p):
			sound_cache[s_name] = load(p)

	# Explosions
	var exp_names = ["explosion_small", "explosion_medium", "explosion_heavy", "player_destroyed"]
	for e_name in exp_names:
		var p = "res://assets/audio/explosions/" + e_name + ".ogg"
		if ResourceLoader.exists(p):
			sound_cache[e_name] = load(p)

func play_sfx_name(s_name: String, volume_scale: float = 1.0) -> void:
	var stream = sound_cache.get(s_name) as AudioStream
	if stream:
		play_sfx(stream, volume_scale)

func play_sfx(stream: AudioStream, volume_scale: float = 1.0) -> void:
	if stream == null:
		return
	for p in sfx_players:
		if not p.playing:
			p.stream = stream
			p.volume_db = linear_to_db(clamp(sfx_volume * volume_scale, 0.01, 2.0))
			p.play()
			return

func play_ui_sound(stream: AudioStream, volume_scale: float = 1.0) -> void:
	if stream == null:
		return
	for p in ui_players:
		if not p.playing:
			p.stream = stream
			p.volume_db = linear_to_db(clamp(ui_volume * volume_scale, 0.01, 2.0))
			p.play()
			return

func play_weapon(w_id: String) -> void:
	play_sfx_name(w_id, 0.9)

func play_hit(is_shield: bool = false) -> void:
	if is_shield:
		play_sfx_name("shield_hit", 0.85)
	else:
		play_sfx_name("hit", 0.85)

func play_explosion(type: String = "medium") -> void:
	if type == "small":
		play_sfx_name("explosion_small", 0.9)
	elif type == "heavy":
		play_sfx_name("explosion_heavy", 1.1)
	else:
		play_sfx_name("explosion_medium", 1.0)

func play_pickup() -> void:
	play_sfx_name("pickup", 0.9)

func play_ui_click() -> void:
	var stream = sound_cache.get("ui_click") as AudioStream
	if stream:
		play_ui_sound(stream, 0.8)
	else:
		play_sfx_name("ui_click", 0.8)

func play_victory() -> void:
	play_sfx_name("victory", 1.0)

func play_music(stream: AudioStream, _loop: bool = true) -> void:
	if stream == null:
		return
	music_player.stream = stream
	music_player.volume_db = linear_to_db(music_volume)
	music_player.play()

func stop_music() -> void:
	music_player.stop()
