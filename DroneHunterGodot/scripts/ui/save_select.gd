class_name SaveSelect
extends Control

@onready var slot0_card: Panel = $Content/SlotCards/Slot0
@onready var slot1_card: Panel = $Content/SlotCards/Slot1
@onready var slot2_card: Panel = $Content/SlotCards/Slot2

@onready var back_btn: Button = $Footer/BackBtn

func _ready() -> void:
	_refresh_slots()
	var gm = get_tree().get_first_node_in_group("game_manager")
	back_btn.pressed.connect(func():
		if gm:
			gm.navigate_to_state(GameStateManager.State.MAIN_MENU)
	)

func _refresh_slots() -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	var cards = [slot0_card, slot1_card, slot2_card]
	
	for slot_idx in range(3):
		var card = cards[slot_idx]
		if not card:
			continue
			
		var has_save = gm.save_manager.has_save(slot_idx) if (gm and gm.save_manager) else false
		var title_lbl: Label = card.get_node("VBox/Title")
		var info_lbl: Label = card.get_node("VBox/Info")
		var load_btn: Button = card.get_node("VBox/BtnRow/LoadBtn")
		var new_btn: Button = card.get_node("VBox/BtnRow/NewBtn")
		var del_btn: Button = card.get_node("VBox/BtnRow/DeleteBtn")
		
		title_lbl.text = "SLOT %d" % (slot_idx + 1)
		
		if has_save:
			var data = gm.save_manager.load_slot(slot_idx)
			var drone = str(data.get("selected_drone_id", "striker")).to_upper()
			var scr = int(data.get("scrap", 0))
			var camp_data = data.get("campaign", {})
			var cur_m = str(camp_data.get("current_mission", "S1_M1"))
			
			info_lbl.text = "MISSION: %s\nDRONE: %s\nSCRAP: %d 🔩" % [cur_m, drone, scr]
			load_btn.disabled = false
			del_btn.disabled = false
		else:
			info_lbl.text = "[EMPTY SAVE SLOT]\n\nClick NEW to start"
			load_btn.disabled = true
			del_btn.disabled = true
			
		if load_btn.pressed.is_connected(_on_load_slot):
			load_btn.pressed.disconnect(_on_load_slot)
		if new_btn.pressed.is_connected(_on_new_slot):
			new_btn.pressed.disconnect(_on_new_slot)
		if del_btn.pressed.is_connected(_on_delete_slot):
			del_btn.pressed.disconnect(_on_delete_slot)
			
		load_btn.pressed.connect(_on_load_slot.bind(slot_idx))
		new_btn.pressed.connect(_on_new_slot.bind(slot_idx))
		del_btn.pressed.connect(_on_delete_slot.bind(slot_idx))

func _on_load_slot(slot_idx: int) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.load_game(slot_idx)
		gm.navigate_to_state(GameStateManager.State.CAMPAIGN_SELECT)

func _on_new_slot(slot_idx: int) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.current_slot = slot_idx
		gm.scrap = 500
		if gm.campaign_state:
			gm.campaign_state.reset_campaign()
		if gm.progression_manager:
			gm.progression_manager.reset()
		gm.save_game(slot_idx)
		gm.navigate_to_state(GameStateManager.State.DRONE_SELECT)

func _on_delete_slot(slot_idx: int) -> void:
	var gm = get_tree().get_first_node_in_group("game_manager")
	if gm:
		gm.delete_save(slot_idx)
	_refresh_slots()
