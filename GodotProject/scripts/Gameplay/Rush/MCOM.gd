@tool
class_name MCOM
extends Node3D

@export var Enabled = true
@export var ObjId = 0
@export var TacticalAdviceLandVehicleFriendly = true
@export var TacticalAdviceAirVehicleFriendly = false

enum TacticalAdvicePriorityLevel_Team1_selection {AICommanderWorldPriority_0, AICommanderWorldPriority_1, AICommanderWorldPriority_2}
@export var TacticalAdvicePriorityLevel_Team1: TacticalAdvicePriorityLevel_Team1_selection


enum TacticalAdvicePriorityLevel_Team2_selection {AICommanderWorldPriority_0, AICommanderWorldPriority_1, AICommanderWorldPriority_2}
@export var TacticalAdvicePriorityLevel_Team2: TacticalAdvicePriorityLevel_Team2_selection

@export var id = ""

var global_name = self.get_script().get_global_name()

func _get_configuration_warnings() -> PackedStringArray:
	var scene_root = get_tree().edited_scene_root
	if get_node(".") == scene_root:
		return []
	if not LevelValidator.is_type_in_level(global_name, scene_root):
		var levels = LevelValidator.get_level_restrictions(global_name)
		var levels_str = "\n  - ".join(levels) if levels.size() > 0 else "Any"
		var msg = "%s is not usable in %s\nValid levels include:\n  - %s" % [global_name, scene_root.name, levels_str]
		return [msg]
	return []

func _validate_property(property: Dictionary):
	if property.name == "id":
		property.usage = PROPERTY_USAGE_NO_EDITOR
