class_name ObjectiveController
extends Node

signal objective_completed()
signal objective_failed()
signal progress_updated(text: String, percent: float)

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
	_emit_progress()

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
		if completed_encounters >= total_encounters:
			complete_objective()

func on_all_enemies_destroyed() -> void:
	if not is_active or is_finished:
		return
	if objective_type in ["destroy_all", "complete_encounters"]:
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
			desc = "WAVE %d / %d" % [completed_encounters, total_encounters]
			pct = clamp(float(completed_encounters) / float(total_encounters), 0.0, 1.0)
	progress_updated.emit(desc, pct)
