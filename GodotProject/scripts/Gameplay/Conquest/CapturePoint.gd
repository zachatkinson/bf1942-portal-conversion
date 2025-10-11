@tool
class_name CapturePoint
extends Node3D

@export var Enabled = true

enum InitialOwner_selection {TeamNeutral, Team1, Team2, Team3, Team4, Team5, Team6, Team7, Team8, Team9, Team10, Team11, Team12, Team13, Team14, Team15, Team16, Team17, Team18, Team19, Team20, Team21, Team22, Team23, Team24, Team25, Team26, Team27, Team28, Team29, Team30, Team31, Team32, Team33, Team34, Team35, Team36, Team37, Team38, Team39, Team40, Team41, Team42, Team43, Team44, Team45, Team46, Team47, Team48, Team49, Team50, Team51, Team52, Team53, Team54, Team55, Team56, Team57, Team58, Team59, Team60, Team61, Team62, Team63, Team64, Team65, Team66, Team67, Team68, Team69, Team70, Team71, Team72, Team73, Team74, Team75, Team76, Team77, Team78, Team79, Team80, Team81, Team82, Team83, Team84, Team85, Team86, Team87, Team88, Team89, Team90, Team91, Team92, Team93, Team94, Team95, Team96, Team97, Team98, Team99, Team100, Team101, Team102, Team103, Team104, Team105, Team106, Team107, Team108, Team109, Team110, Team111, Team112, Team113, Team114, Team115, Team116, Team117, Team118, Team119, Team120, Team121, Team122, Team123, Team124, Team125, Team126, Team127, Team128, TeamIdCount}
@export var InitialOwner: InitialOwner_selection


enum FlagPoleSize_selection {Medium, Small, High, Payload, Interior}
@export var FlagPoleSize: FlagPoleSize_selection

@export var PipCamOffset = [40, 10, 0]
@export var ObjId = 0

enum OutlineSetting_selection {Projected, Flat, Disabled}
@export var OutlineSetting: OutlineSetting_selection

@export var OutlineOffsetY = 0
@export var OutlineHeightMultiplier = 1
@export var OutlineAbove16Points = false
@export var CameraRotationTypeRange = false
@export var CameraLookAtPosition = true
@export var CameraLookAngle = -30
@export var CameraRotationDirection = 0
@export var CameraRotatingRange = 30
@export var CameraLookAtDistanceTrim = 1
@export var CameraOffsetPosition = [15, 60, 15]
@export var CameraSpeed = 2
@export var CameraLookAtPositionOffset = [0, 0, 0]
@export var CameraFOV = 70
@export var CameraAutoFOV = true
@export var Spawning_ObjectiveMaxDistance = -1
@export var TacticalAdviceLandVehicleFriendly = true
@export var TacticalAdviceAirVehicleFriendly = false

enum TacticalAdvicePriorityLevel_Team1_selection {AICommanderWorldPriority_0, AICommanderWorldPriority_1, AICommanderWorldPriority_2}
@export var TacticalAdvicePriorityLevel_Team1: TacticalAdvicePriorityLevel_Team1_selection


enum TacticalAdvicePriorityLevel_Team2_selection {AICommanderWorldPriority_0, AICommanderWorldPriority_1, AICommanderWorldPriority_2}
@export var TacticalAdvicePriorityLevel_Team2: TacticalAdvicePriorityLevel_Team2_selection

@export var CaptureArea : PolygonVolume
@export var InfantrySpawnPoints_Team1 : Array[SpawnPoint]
@export var InfantrySpawnPoints_Team2 : Array[SpawnPoint]
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
