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
@onready var pause_restart_btn: Button = $Root/PauseModal/VBox/RestartBtn
@onready var pause_settings_btn: Button = $Root/PauseModal/VBox/SettingsBtn
@onready var pause_hangar_btn: Button = $Root/PauseModal/VBox/HangarBtn

var is_paused: bool = false

func _ready() -> void:
	victory_modal.visible = false
	defeat_modal.visible = false
	pause_modal.visible = false
	
	_style_progress_bars()
	_connect_events()

func _style_progress_bars() -> void:
	# Hull Bar: Emerald Green
	_apply_bar_theme(hull_bar, Color(0.18, 0.85, 0.45), Color(0.04, 0.12, 0.07, 0.85))
	# Shield Bar: Electric Cyan
	_apply_bar_theme(shield_bar, Color(0.0, 0.85, 1.0), Color(0.02, 0.08, 0.18, 0.85))
	# Energy Bar: Amber Gold
	_apply_bar_theme(energy_bar, Color(1.0, 0.75, 0.1), Color(0.14, 0.09, 0.02, 0.85))

func _apply_bar_theme(bar: ProgressBar, fill_color: Color, bg_color: Color) -> void:
	if not bar:
		return
	var bg = StyleBoxFlat.new()
	bg.bg_color = bg_color
	bg.corner_radius_top_left = 3
	bg.corner_radius_top_right = 3
	bg.corner_radius_bottom_left = 3
	bg.corner_radius_bottom_right = 3
	bg.border_width_left = 1
	bg.border_width_top = 1
	bg.border_width_right = 1
	bg.border_width_bottom = 1
	bg.border_color = Color(0.3, 0.5, 0.7, 0.4)
	
	var fill = StyleBoxFlat.new()
	fill.bg_color = fill_color
	fill.corner_radius_top_left = 3
	fill.corner_radius_top_right = 3
	fill.corner_radius_bottom_left = 3
	fill.corner_radius_bottom_right = 3
	
	bar.add_theme_stylebox_override("background", bg)
	bar.add_theme_stylebox_override("fill", fill)

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
		cd.encounter_started.connect(_on_wave_started)
		cd.mission_completed.connect(_on_mission_victory)
		cd.mission_failed.connect(_on_mission_failed)
		if cd.objective_controller:
			cd.objective_controller.progress_updated.connect(_on_objective_progress)

	# Buttons
	victory_continue_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/SectorMap.tscn"))
	defeat_retry_btn.pressed.connect(func(): get_tree().reload_current_scene())
	defeat_hangar_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/Hangar.tscn"))
	
	pause_resume_btn.pressed.connect(_toggle_pause)
	if pause_restart_btn:
		pause_restart_btn.pressed.connect(func():
			get_tree().paused = false
			get_tree().reload_current_scene()
		)
	if pause_settings_btn:
		pause_settings_btn.pressed.connect(func():
			get_tree().paused = false
			get_tree().change_scene_to_file("res://scenes/ui/Settings.tscn")
		)
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
			weapon_label.text = "WEAPON: [SLOT %d] %s" % [active_def.slot, active_def.display_name.to_upper()]
			
	# Update director stats
	var cd = get_tree().get_first_node_in_group("combat_director") as CombatDirector
	if cd:
		var living_count = cd.get_living_enemy_count() if cd.has_method("get_living_enemy_count") else cd.enemies_remaining
		enemies_label.text = "HOSTILES: " + str(living_count)
		score_label.text = "SCORE: " + str(cd.mission_score)
		
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		scrap_label.text = "SCRAP: " + str(gm.scrap) + " 🔩"

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
	wave_label.text = "ENCOUNTER %d / %d" % [wave_idx, total_waves]

func _on_objective_progress(desc: String, _pct: float) -> void:
	if desc != "":
		wave_label.text = desc

func _on_mission_victory(score: int, scrap: int) -> void:
	victory_modal.visible = true
	victory_score_lbl.text = "FINAL SCORE: %d" % score
	victory_scrap_lbl.text = "SCRAP EARNED: +%d 🔩" % scrap

func _on_mission_failed() -> void:
	defeat_modal.visible = true
