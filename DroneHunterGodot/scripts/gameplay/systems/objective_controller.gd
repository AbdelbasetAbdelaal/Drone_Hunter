class_name ObjectiveController
extends Node

signal objective_completed()
signal objective_failed()
signal progress_updated(text: String, percent: float)
signal target_status_updated(target_id: String, remaining: int, total: int)

var primary_objective: String = "destroy_all"
var objective_type: String = "destroy_all"
var objective_target: String = "radar_command"
var defense_level: int = 1

var target_duration: float = 0.0
var elapsed_time: float = 0.0
var is_active: bool = false
var is_finished: bool = false

var total_encounters: int = 1
var completed_encounters: int = 0

var active_targets: Array[Node] = []
var initial_target_count: int = 0

func setup_objective(mission_def: MissionDefinition) -> void:
	if not mission_def:
		return
	primary_objective = mission_def.primary_objective
	objective_type = mission_def.primary_objective
	objective_target = mission_def.objective_target
	defense_level = mission_def.defense_level
	target_duration = mission_def.duration
	total_encounters = max(1, mission_def.encounter_sequence.size())
	completed_encounters = 0
	elapsed_time = 0.0
	is_active = true
	is_finished = false
	active_targets.clear()
	initial_target_count = 0
	_emit_progress()

func register_target(target: Node) -> void:
	if not target or target in active_targets:
		return
	active_targets.append(target)
	initial_target_count = active_targets.size()
	if target.has_signal("target_destroyed"):
		target.target_destroyed.connect(_on_target_destroyed)
	_emit_progress()

func _on_target_destroyed(t_id: String) -> void:
	# Filter out destroyed targets
	var remaining: Array[Node] = []
	for t in active_targets:
		if is_instance_valid(t) and not t.is_queued_for_deletion():
			if not ("is_destroyed" in t and t.is_destroyed):
				remaining.append(t)
	active_targets = remaining
	
	print("ObjectiveController: Target [%s] destroyed. Remaining targets: %d" % [t_id, active_targets.size()])
	target_status_updated.emit(t_id, active_targets.size(), initial_target_count)
	_emit_progress()
	
	if active_targets.size() == 0 and initial_target_count > 0:
		if objective_type in ["destroy_target", "destroy_all", "complete_encounters"]:
			complete_objective()

func _physics_process(delta: float) -> void:
	if not is_active or is_finished:
		return
		
	if objective_type == "survive":
		elapsed_time += delta
		_emit_progress()
		if elapsed_time >= target_duration:
			complete_objective()

func on_encounter_cleared(encounter_index: int, total: int) -> void:
	if not is_active or is_finished:
		return
	completed_encounters = encounter_index
	total_encounters = total
	_emit_progress()
	
	if objective_type in ["complete_encounters", "destroy_all"]:
		# If mission has active ground targets, require them to be destroyed too
		if active_targets.size() == 0:
			if completed_encounters >= total_encounters:
				complete_objective()

func on_all_enemies_destroyed() -> void:
	if not is_active or is_finished:
		return
	if objective_type in ["destroy_all", "complete_encounters"]:
		if active_targets.size() == 0:
			if completed_encounters >= total_encounters:
				complete_objective()

func complete_objective() -> void:
	if is_finished:
		return
	is_finished = true
	is_active = false
	objective_completed.emit()
	print("ObjectiveController: Objective Completed (%s - %s)" % [primary_objective, objective_target])

func fail_objective() -> void:
	if is_finished:
		return
	is_finished = true
	is_active = false
	objective_failed.emit()
	print("ObjectiveController: Objective Failed (%s - %s)" % [primary_objective, objective_target])

func _emit_progress() -> void:
	var desc = ""
	var pct = 0.0
	match objective_type:
		"survive":
			var remain = max(0.0, target_duration - elapsed_time)
			desc = "SURVIVE: %02d:%02d" % [int(remain) / 60, int(remain) % 60]
			pct = clamp(elapsed_time / target_duration, 0.0, 1.0) if target_duration > 0.0 else 1.0
		"complete_encounters", "destroy_all":
			if active_targets.size() > 0:
				desc = "TARGET: %s [%d REMAINING]" % [objective_target.replace("_", " ").to_upper(), active_targets.size()]
				pct = clamp(1.0 - (float(active_targets.size()) / float(max(1, initial_target_count))), 0.0, 1.0)
			else:
				desc = "WAVE %d / %d" % [completed_encounters, total_encounters]
				pct = clamp(float(completed_encounters) / float(total_encounters), 0.0, 1.0)
		_:
			if active_targets.size() > 0:
				desc = "TARGET: %s [%d REMAINING]" % [objective_target.replace("_", " ").to_upper(), active_targets.size()]
			else:
				desc = "WAVE %d / %d" % [completed_encounters, total_encounters]
				
	progress_updated.emit(desc, pct)
