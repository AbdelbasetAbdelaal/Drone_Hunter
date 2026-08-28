class_name HUD
extends CanvasLayer

@onready var hull_bar: ProgressBar = $Root/TopLeft/VBox/HullBar
@onready var shield_bar: ProgressBar = $Root/TopLeft/VBox/ShieldBar
@onready var energy_bar: ProgressBar = $Root/TopLeft/VBox/EnergyBar
@onready var weapon_label: Label = $Root/TopLeft/VBox/WeaponLabel

@onready var wave_label: Label = $Root/TopCenter/WaveLabel
@onready var enemies_label: Label = $Root/TopCenter/EnemiesLabel

@onready var score_label: Label = $Root/TopRight/ScoreLabel
@onready var scrap_label: Label = $Root/TopRight/ScrapLabel

@onready var boss_container: VBoxContainer = $Root/BottomCenter/BossContainer
@onready var boss_bar: ProgressBar = $Root/BottomCenter/BossContainer/BossBar

# Overlays
@onready var victory_modal: Panel = $Root/VictoryModal
@onready var victory_score_lbl: Label = $Root/VictoryModal/VBox/ScoreLbl
@onready var victory_scrap_lbl: Label = $Root/VictoryModal/VBox/ScrapLbl
@onready var victory_continue_btn: Button = $Root/VictoryModal/VBox/ContinueBtn

@onready var defeat_modal: Panel = $Root/DefeatModal
@onready var defeat_retry_btn: Button = $Root/DefeatModal/VBox/RetryBtn
@onready var defeat_hangar_btn: Button = $Root/DefeatModal/VBox/HangarBtn

@onready var pause_modal: Panel = $Root/PauseModal
@onready var pause_resume_btn: Button = $Root/PauseModal/VBox/ResumeBtn
@onready var pause_hangar_btn: Button = $Root/PauseModal/VBox/HangarBtn

var is_paused: bool = false

func _ready() -> void:
	boss_container.visible = false
	victory_modal.visible = false
	defeat_modal.visible = false
	pause_modal.visible = false
	
	_connect_events()

func _connect_events() -> void:
	# Connect to Player
	var player = get_tree().get_first_node_in_group("player") as Player
	if player:
		player.health_changed.connect(_on_health_changed)
		player.shield_changed.connect(_on_shield_changed)
		player.energy_changed.connect(_on_energy_changed)
		if player.health:
			_on_health_changed(player.health.current_hp, player.health.max_hp)
			_on_shield_changed(player.health.current_shield, player.health.max_shield)

	# Connect to CombatDirector
	var cd = get_tree().get_first_node_in_group("combat_director") as CombatDirector
	if cd:
		cd.wave_started.connect(_on_wave_started)
		cd.mission_completed.connect(_on_mission_victory)
		cd.mission_failed.connect(_on_mission_failed)

	# Buttons
	victory_continue_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn"))
	defeat_retry_btn.pressed.connect(func(): get_tree().reload_current_scene())
	defeat_hangar_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/Hangar.tscn"))
	
	pause_resume_btn.pressed.connect(_toggle_pause)
	pause_hangar_btn.pressed.connect(func():
		get_tree().paused = false
		get_tree().change_scene_to_file("res://scenes/ui/Hangar.tscn")
	)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_toggle_pause()

func _toggle_pause() -> void:
	if victory_modal.visible or defeat_modal.visible:
		return
	is_paused = !is_paused
	get_tree().paused = is_paused
	pause_modal.visible = is_paused

func _process(_delta: float) -> void:
	# Update player weapon name
	var player = get_tree().get_first_node_in_group("player") as Player
	if player and player.weapon_controller:
		var wc = player.weapon_controller
		if wc.weapons.size() > wc.active_weapon_index:
			var active_def = wc.weapons[wc.active_weapon_index]
			weapon_label.text = "WEAPON: " + active_def.display_name.to_upper()
			
	# Update director stats
	var cd = get_tree().get_first_node_in_group("combat_director") as CombatDirector
	if cd:
		enemies_label.text = "ENEMIES: " + str(cd.enemies_remaining)
		score_label.text = "SCORE: " + str(cd.mission_score)
		
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		scrap_label.text = "SCRAP: " + str(gm.scrap) + " 🔩"
		
	# Check for boss
	var boss = get_tree().get_first_node_in_group("boss") as BossTitan
	if boss and is_instance_valid(boss):
		boss_container.visible = true
		if boss.health:
			boss_bar.max_value = boss.health.max_hp
			boss_bar.value = boss.health.current_hp
	else:
		boss_container.visible = false

func _on_health_changed(cur: float, max_val: float) -> void:
	hull_bar.max_value = max_val
	hull_bar.value = cur

func _on_shield_changed(cur: float, max_val: float) -> void:
	shield_bar.max_value = max_val
	shield_bar.value = cur

func _on_energy_changed(cur: float, max_val: float) -> void:
	energy_bar.max_value = max_val
	energy_bar.value = cur

func _on_wave_started(wave_idx: int, total_waves: int) -> void:
	wave_label.text = "WAVE %d / %d" % [wave_idx, total_waves]

func _on_mission_victory(score: int, scrap: int) -> void:
	victory_modal.visible = true
	victory_score_lbl.text = "FINAL SCORE: %d" % score
	victory_scrap_lbl.text = "SCRAP EARNED: +%d 🔩" % scrap

func _on_mission_failed() -> void:
	defeat_modal.visible = true
