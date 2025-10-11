@tool
class_name VehicleSpawner
extends Node3D

@export var DisableRespawn = false
@export var ObjId = 0

enum VehicleType_selection {Abrams, Leopard, Cheetah, CV90, Gepard, UH60, Eurocopter, AH64, Vector, Quadbike, Flyer60, JAS39, F22, F16, M2Bradley, SU57}
@export var VehicleType: VehicleType_selection = VehicleType_selection.Abrams

@export var P_AutoSpawnEnabled = false
@export var P_DefaultRespawnTime = 0
@export var P_ApplyDamageToAbandonVehicle = true
@export var P_AbandonVehiclesOutOfCombatArea = true
@export var P_TimeUntilAbandon = 10
@export var P_KeepAliveAbandonRadius = 50
@export var P_KeepAliveSpawnerRadius = 50
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
