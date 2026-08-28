class_name AudioManagerNode
extends Node

var music_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []

@export var music_volume: float = 0.8
@export var sfx_volume: float = 0.8

func _ready() -> void:
	music_player = AudioStreamPlayer.new()
	music_player.bus = "Master"
	add_child(music_player)

	for i in range(16):
		var p = AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		sfx_players.append(p)

func play_sfx(stream: AudioStream, volume_scale: float = 1.0) -> void:
	if stream == null:
		return
	for p in sfx_players:
		if not p.playing:
			p.stream = stream
			p.volume_db = linear_to_db(sfx_volume * volume_scale)
			p.play()
			return

func play_music(stream: AudioStream, loop: bool = true) -> void:
	if stream == null:
		return
	music_player.stream = stream
	music_player.volume_db = linear_to_db(music_volume)
	music_player.play()

func stop_music() -> void:
	music_player.stop()
