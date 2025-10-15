@tool
extends EditorPlugin

# Dock panel
var dock: VBoxContainer

# Workflow buttons with metadata
class WorkflowButton:
	var button: Button
	var number: int
	var label: String
	var is_completed: bool = false
	var allow_multiple_use: bool = false  # Some buttons can be used multiple times

	func _init(btn: Button, num: int, lbl: String, allow_reuse: bool = false):
		button = btn
		number = num
		label = lbl
		allow_multiple_use = allow_reuse
		button.text = lbl  # Just the label, no emojis

	func mark_complete():
		if is_completed:
			return
		# Change button color to green
		button.add_theme_color_override("font_color", Color(0.2, 0.8, 0.2))  # Green text
		button.modulate = Color(0.7, 1.0, 0.7)  # Light green tint
		# Only disable if it's not meant to be reused
		if not allow_multiple_use:
			button.disabled = true
		is_completed = true

	func reset():
		# Remove color overrides
		button.remove_theme_color_override("font_color")
		button.modulate = Color(1, 1, 1)  # Reset to white
		button.disabled = false
		is_completed = false

# All workflow buttons
var workflow_buttons: Array[WorkflowButton] = []

# Validation status labels
var snapped_label: Label
var collision_removed_label: Label

# Settings button (not part of numbered workflow)
var settings_button: Button

# Settings dialog
var settings_dialog: AcceptDialog
var base_terrain_option: OptionButton
var max_players_spinbox: SpinBox
var game_mode_option: OptionButton
var experience_mode_option: OptionButton
var experience_filename_input: LineEdit
var experience_suffix_input: LineEdit

# Plugin settings (saved to project settings)
var base_terrain: String = "MP_Tungsten"
var max_players: int = 32
var game_mode: String = "Conquest"
var experience_mode: String = "verified"  # "custom" or "verified"
var experience_filename_base: String = "1942_Revisited"
var experience_filename_suffix: String = ""  # Optional suffix like "_v1", "_WW2", etc.

# Undo/redo
var undo_redo: EditorUndoRedoManager

# Helper function to repeat strings (GDScript doesn't support "=" * 70)
func _repeat_string(s: String, count: int) -> String:
	var result = ""
	for i in range(count):
		result += s
	return result

func _enter_tree():
	# Get undo/redo manager
	undo_redo = get_undo_redo()

	# Load saved settings
	_load_settings()

	# Create dock panel
	dock = VBoxContainer.new()
	dock.name = "BF1942 Tools"

	# ==================== MAP SETUP SECTION ====================
	var setup_label = Label.new()
	setup_label.text = "Map Setup"
	setup_label.add_theme_font_size_override("font_size", 40)
	dock.add_child(setup_label)

	# Step 1: Generate .tscn (workflow step 1)
	var generate_btn = Button.new()
	generate_btn.text = "Generate .tscn"
	generate_btn.tooltip_text = "Regenerate current map from BF1942 source"
	generate_btn.pressed.connect(_on_regenerate_tscn)
	dock.add_child(generate_btn)
	workflow_buttons.append(WorkflowButton.new(generate_btn, 1, "Generate .tscn"))

	# Rotate Terrain - DISABLED (terrain rotation handled by portal_convert.py --rotate-terrain flag)
	# Keep the function for potential future Portal updates, but hide from UI
	# var rotate_btn = Button.new()
	# rotate_btn.text = "Rotate Terrain 90°"
	# rotate_btn.tooltip_text = "Rotate terrain and its children by 90 degrees around Y axis (optional, can use multiple times)"
	# rotate_btn.pressed.connect(_on_rotate_terrain_90)
	# dock.add_child(rotate_btn)

	# Step 2: Setup Terrain Collision (workflow step 2)
	var collision_btn = Button.new()
	collision_btn.text = "Setup Terrain Collision"
	collision_btn.tooltip_text = "Auto-setup trimesh collision for terrain (handles editable children)"
	collision_btn.pressed.connect(_on_setup_terrain_collision)
	dock.add_child(collision_btn)
	workflow_buttons.append(WorkflowButton.new(collision_btn, 2, "Setup Terrain Collision"))

	# Step 2.5: Snap ALL to Terrain (NEW - automated terrain snapping)
	var snap_all_btn = Button.new()
	snap_all_btn.text = "Snap ALL to Terrain"
	snap_all_btn.tooltip_text = "Automatically snap all objects (gameplay + static) to terrain height"
	snap_all_btn.pressed.connect(_on_snap_all_to_terrain)
	dock.add_child(snap_all_btn)
	workflow_buttons.append(WorkflowButton.new(snap_all_btn, 3, "Snap ALL to Terrain", true))  # Allow multiple uses

	# Step 4: Cull Out of Bounds (workflow step 4)
	var cull_btn = Button.new()
	cull_btn.text = "Cull Out of Bounds"
	cull_btn.tooltip_text = "Remove assets outside combat area or terrain bounds"
	cull_btn.pressed.connect(_on_cull_out_of_bounds)
	dock.add_child(cull_btn)
	workflow_buttons.append(WorkflowButton.new(cull_btn, 4, "Cull Out of Bounds"))

	# Workflow validation - automatic checks
	var run_checks_button = Button.new()
	run_checks_button.text = "🔍 Run Workflow Checks"
	run_checks_button.tooltip_text = "Verify assets are snapped and TerrainCollision removed"
	run_checks_button.pressed.connect(_on_run_workflow_checks)
	dock.add_child(run_checks_button)

	# Status labels for validation results
	snapped_label = Label.new()
	snapped_label.text = "❌ Assets snapped to terrain"
	snapped_label.add_theme_font_size_override("font_size", 23)
	snapped_label.add_theme_color_override("font_color", Color(0.9, 0.2, 0.2))  # Red text initially
	dock.add_child(snapped_label)

	collision_removed_label = Label.new()
	collision_removed_label.text = "❌ TerrainCollision deleted from scene"
	collision_removed_label.add_theme_font_size_override("font_size", 23)
	collision_removed_label.add_theme_color_override("font_color", Color(0.9, 0.2, 0.2))  # Red text initially
	dock.add_child(collision_removed_label)

	dock.add_child(HSeparator.new())

	# ==================== VALIDATION SECTION ====================
	var validation_label = Label.new()
	validation_label.text = "Validation"
	validation_label.add_theme_font_size_override("font_size", 40)
	dock.add_child(validation_label)

	# Validation buttons configuration (steps 5-7)
	var validation_configs = [
		{"label": "List Terrain Contents", "tooltip": "List all child nodes in terrain (helps identify built-in structures)", "callback": _on_list_terrain_contents},
		{"label": "Asset Report", "tooltip": "Show asset mapping statistics for current map", "callback": _on_asset_report},
		{"label": "Validate Portal Map", "tooltip": "Check for required Portal nodes and structure", "callback": _on_validate_map},
	]

	# Create Validation buttons (disabled until workflow checkboxes complete)
	for i in range(validation_configs.size()):
		var config = validation_configs[i]
		var btn = Button.new()
		btn.tooltip_text = config["tooltip"]
		btn.pressed.connect(config["callback"])
		btn.disabled = true  # Disabled until checkboxes are checked
		dock.add_child(btn)

		var workflow_btn = WorkflowButton.new(btn, i + 5, config["label"])
		workflow_buttons.append(workflow_btn)

	dock.add_child(HSeparator.new())

	# ==================== EXPORT SECTION ====================
	var export_label = Label.new()
	export_label.text = "Export"
	export_label.add_theme_font_size_override("font_size", 40)
	dock.add_child(export_label)

	# Export button (step 8)
	var export_btn = Button.new()
	export_btn.tooltip_text = "Export current map to spatial.json format"
	export_btn.pressed.connect(_on_export_spatial)
	export_btn.disabled = true
	dock.add_child(export_btn)
	var export_workflow = WorkflowButton.new(export_btn, 8, "Export Spatial.json")
	workflow_buttons.append(export_workflow)

	# Settings button (not part of numbered workflow)
	settings_button = Button.new()
	settings_button.text = "⚙️ Experience Settings"
	settings_button.tooltip_text = "Plugin settings (base terrain, player count, game mode)"
	settings_button.pressed.connect(_on_settings)
	settings_button.disabled = true
	dock.add_child(settings_button)

	# Create Multi-Map Experience button (step 9)
	var multi_exp_btn = Button.new()
	multi_exp_btn.tooltip_text = "Generate multi-map experience from registry"
	multi_exp_btn.pressed.connect(_on_create_multi_experience)
	multi_exp_btn.disabled = true
	dock.add_child(multi_exp_btn)
	var multi_exp_workflow = WorkflowButton.new(multi_exp_btn, 9, "Create Multi-Map Experience")
	workflow_buttons.append(multi_exp_workflow)

	dock.add_child(HSeparator.new())

	# ==================== RESET SECTION ====================
	var reset_label = Label.new()
	reset_label.text = "Reset Process"
	reset_label.add_theme_font_size_override("font_size", 40)
	dock.add_child(reset_label)

	# Reset button
	var reset_button = Button.new()
	reset_button.text = "🔄 Reset All Steps"
	reset_button.tooltip_text = "Reset all workflow steps and checkboxes"
	reset_button.pressed.connect(_on_reset_workflow)
	dock.add_child(reset_button)

	# Add dock to right sidebar
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, dock)

	# Create settings dialog
	_create_settings_dialog()

func _exit_tree():
	# Save settings
	_save_settings()

	# Clean up dock
	if dock:
		remove_control_from_docks(dock)
		dock.queue_free()

	# Clean up settings dialog
	if settings_dialog:
		settings_dialog.queue_free()

func _load_settings():
	# Load plugin settings from project settings
	if ProjectSettings.has_setting("bf1942_tools/base_terrain"):
		base_terrain = ProjectSettings.get_setting("bf1942_tools/base_terrain")
	if ProjectSettings.has_setting("bf1942_tools/max_players"):
		max_players = ProjectSettings.get_setting("bf1942_tools/max_players")
	if ProjectSettings.has_setting("bf1942_tools/game_mode"):
		game_mode = ProjectSettings.get_setting("bf1942_tools/game_mode")
	if ProjectSettings.has_setting("bf1942_tools/experience_mode"):
		experience_mode = ProjectSettings.get_setting("bf1942_tools/experience_mode")
	if ProjectSettings.has_setting("bf1942_tools/experience_filename_base"):
		experience_filename_base = ProjectSettings.get_setting("bf1942_tools/experience_filename_base")
	if ProjectSettings.has_setting("bf1942_tools/experience_filename_suffix"):
		experience_filename_suffix = ProjectSettings.get_setting("bf1942_tools/experience_filename_suffix")

func _save_settings():
	# Save plugin settings to project settings
	ProjectSettings.set_setting("bf1942_tools/base_terrain", base_terrain)
	ProjectSettings.set_setting("bf1942_tools/max_players", max_players)
	ProjectSettings.set_setting("bf1942_tools/game_mode", game_mode)
	ProjectSettings.set_setting("bf1942_tools/experience_mode", experience_mode)
	ProjectSettings.set_setting("bf1942_tools/experience_filename_base", experience_filename_base)
	ProjectSettings.set_setting("bf1942_tools/experience_filename_suffix", experience_filename_suffix)
	ProjectSettings.save()

func _create_settings_dialog():
	# Create settings dialog UI
	settings_dialog = AcceptDialog.new()
	settings_dialog.title = "BF1942 Portal Tools - Settings"
	settings_dialog.size = Vector2i(500, 520)  # Increased size for filename settings

	var vbox = VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", 10)

	# Base Terrain setting
	var terrain_label = Label.new()
	terrain_label.text = "Base Terrain:"
	vbox.add_child(terrain_label)

	base_terrain_option = OptionButton.new()
	base_terrain_option.add_item("MP_Tungsten (Mirak Valley)", 0)
	base_terrain_option.add_item("MP_Battery (Iberian Offensive)", 1)
	base_terrain_option.add_item("MP_Firestorm (Operation Firestorm)", 2)
	base_terrain_option.add_item("MP_Limestone (Saint's Quarter)", 3)
	base_terrain_option.add_item("MP_Aftermath (Empire State)", 4)
	base_terrain_option.add_item("MP_Outskirts (New Sobek City)", 5)

	# Set current selection
	var terrain_index = ["MP_Tungsten", "MP_Battery", "MP_Firestorm", "MP_Limestone", "MP_Aftermath", "MP_Outskirts"].find(base_terrain)
	if terrain_index >= 0:
		base_terrain_option.select(terrain_index)

	vbox.add_child(base_terrain_option)

	# Max Players setting
	var players_label = Label.new()
	players_label.text = "Max Players Per Team:"
	vbox.add_child(players_label)

	max_players_spinbox = SpinBox.new()
	max_players_spinbox.min_value = 8
	max_players_spinbox.max_value = 128
	max_players_spinbox.step = 8
	max_players_spinbox.value = max_players
	vbox.add_child(max_players_spinbox)

	# Game Mode setting
	var mode_label = Label.new()
	mode_label.text = "Default Game Mode:"
	vbox.add_child(mode_label)

	game_mode_option = OptionButton.new()
	game_mode_option.add_item("Conquest", 0)
	game_mode_option.add_item("Breakthrough", 1)
	game_mode_option.add_item("Rush", 2)
	game_mode_option.add_item("Team Deathmatch", 3)

	var mode_index = ["Conquest", "Breakthrough", "Rush", "Team Deathmatch"].find(game_mode)
	if mode_index >= 0:
		game_mode_option.select(mode_index)

	vbox.add_child(game_mode_option)

	# Experience Mode setting
	var exp_mode_label = Label.new()
	exp_mode_label.text = "Experience Mode:"
	vbox.add_child(exp_mode_label)

	experience_mode_option = OptionButton.new()
	experience_mode_option.add_item("Verified (Publishable to Portal)", 0)
	experience_mode_option.add_item("Custom (Local Testing Only)", 1)

	var exp_mode_index = 0 if experience_mode == "verified" else 1
	experience_mode_option.select(exp_mode_index)

	vbox.add_child(experience_mode_option)

	# Add info label explaining experience modes
	var info_label = Label.new()
	info_label.text = "💡 Verified = Publishable online | Custom = Local testing only"
	info_label.add_theme_font_size_override("font_size", 9)
	info_label.modulate = Color(0.7, 0.7, 0.7)
	vbox.add_child(info_label)

	# Experience filename setting
	var filename_label = Label.new()
	filename_label.text = "Experience Filename Base:"
	vbox.add_child(filename_label)

	experience_filename_input = LineEdit.new()
	experience_filename_input.text = experience_filename_base
	experience_filename_input.placeholder_text = "e.g., 1942_Revisited"
	vbox.add_child(experience_filename_input)

	# Experience filename suffix setting
	var suffix_label = Label.new()
	suffix_label.text = "Experience Filename Suffix (optional):"
	vbox.add_child(suffix_label)

	experience_suffix_input = LineEdit.new()
	experience_suffix_input.text = experience_filename_suffix
	experience_suffix_input.placeholder_text = "e.g., _v1 or _WW2"
	vbox.add_child(experience_suffix_input)

	# Add info label for filename
	var filename_info_label = Label.new()
	filename_info_label.text = "💡 Final filename: <base><suffix>_Experience.json"
	filename_info_label.add_theme_font_size_override("font_size", 9)
	filename_info_label.modulate = Color(0.7, 0.7, 0.7)
	vbox.add_child(filename_info_label)

	settings_dialog.add_child(vbox)
	settings_dialog.confirmed.connect(_on_settings_confirmed)

	get_editor_interface().get_base_control().add_child(settings_dialog)

func _on_settings():
	# Show settings dialog
	settings_dialog.popup_centered()

func _on_settings_confirmed():
	# Save settings when dialog is confirmed
	var terrain_names = ["MP_Tungsten", "MP_Battery", "MP_Firestorm", "MP_Limestone", "MP_Aftermath", "MP_Outskirts"]
	base_terrain = terrain_names[base_terrain_option.selected]

	max_players = int(max_players_spinbox.value)

	var mode_names = ["Conquest", "Breakthrough", "Rush", "Team Deathmatch"]
	game_mode = mode_names[game_mode_option.selected]

	var exp_mode_names = ["verified", "custom"]
	experience_mode = exp_mode_names[experience_mode_option.selected]

	# Save filename settings
	experience_filename_base = experience_filename_input.text
	experience_filename_suffix = experience_suffix_input.text

	_save_settings()

	# Show final filename that will be generated
	var final_filename = experience_filename_base + experience_filename_suffix + "_Experience.json"
	print("✅ Settings saved: %s, %d players, %s, %s mode" % [base_terrain, max_players, game_mode, experience_mode])
	print("   📁 Multi-map filename: %s" % final_filename)

func _on_run_workflow_checks():
	"""Run automatic checks to validate workflow requirements."""
	print("🔍 Running workflow validation checks...")

	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	var all_checks_passed = true

	# Check 1: Assets snapped to terrain (sample objects and verify Y positions are reasonable)
	var assets_snapped = _check_assets_snapped(root)
	_update_label_visual(snapped_label, "Assets snapped to terrain", assets_snapped)
	if assets_snapped:
		print("   ✅ Assets are snapped to terrain")
	else:
		print("   ❌ Assets need to be snapped (select all, press Page Down)")
		all_checks_passed = false

	# Check 2: TerrainCollision removed
	var collision_removed = _check_terrain_collision_removed(root)
	_update_label_visual(collision_removed_label, "TerrainCollision deleted from scene", collision_removed)
	if collision_removed:
		print("   ✅ TerrainCollision has been removed")
	else:
		print("   ❌ TerrainCollision node still exists (delete it to avoid bloated exports)")
		all_checks_passed = false

	# Enable/disable validation and export sections based on results
	_update_workflow_sections(all_checks_passed)

	if all_checks_passed:
		print("✅ All workflow checks passed - Validation and Export sections unlocked!")
	else:
		print("⚠️  Fix the issues above and run checks again")

func _check_assets_snapped(root: Node) -> bool:
	"""Check if assets appear to be snapped to terrain."""
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		return false

	# Sample some assets and check if they have reasonable Y positions
	var sample_count = 0
	var suspicious_count = 0

	for child in static_layer.get_children():
		if child is Node3D and "Terrain" not in child.name:
			sample_count += 1
			var y = child.global_position.y

			# If Y is exactly 0 or very high/low, it's likely not snapped
			if abs(y) < 0.1 or abs(y) > 500:
				suspicious_count += 1

			if sample_count >= 20:  # Sample first 20 objects
				break

	# If more than 30% of sampled objects look unsnapped, fail the check
	if sample_count == 0:
		return true  # No assets to check

	return suspicious_count < (sample_count * 0.3)

func _check_combat_area_position_debug(root: Node) -> Dictionary:
	"""Check CombatArea position and return detailed debug info."""
	var result = {
		"valid": false,
		"combat_y": 0.0,
		"terrain_y": 0.0,
		"clearance": 0.0
	}

	var combat_area = root.find_child("CombatArea", true, false)
	if not combat_area:
		return result

	# Find the CollisionPolygon3D child
	var collision_poly = combat_area.find_child("CollisionPolygon3D", false, false)
	if not collision_poly:
		# Check alternate names
		for child in combat_area.get_children():
			if "Collision" in child.name or "Polygon" in child.name:
				collision_poly = child
				break

	if not collision_poly:
		return result

	var combat_area_y = collision_poly.global_position.y
	result["combat_y"] = combat_area_y

	# Find terrain and get its highest point
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		return result

	var highest_terrain_y = -INF

	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			# Find terrain mesh to get bounds
			var terrain_mesh = null
			for mesh_child in child.get_children():
				if mesh_child is MeshInstance3D:
					terrain_mesh = mesh_child
					break

			# Check nested instances
			if not terrain_mesh:
				for mesh_child in child.get_children():
					for grandchild in mesh_child.get_children():
						if grandchild is MeshInstance3D:
							terrain_mesh = grandchild
							break
					if terrain_mesh:
						break

			if terrain_mesh and terrain_mesh.mesh:
				# Get mesh AABB in local space
				var local_aabb = terrain_mesh.mesh.get_aabb()
				# Highest point in local space is AABB max Y
				var highest_local_y = local_aabb.position.y + local_aabb.size.y

				# Transform to global space - add terrain mesh's global Y position
				# This accounts for any terrain parent transforms
				highest_terrain_y = terrain_mesh.global_position.y + highest_local_y
				break
			break

	if highest_terrain_y == -INF:
		# No terrain found, fall back to simple check
		result["valid"] = combat_area_y >= 100.0
		result["terrain_y"] = 0.0
		result["clearance"] = combat_area_y
		return result

	# CombatArea should be at least 20m above highest terrain point
	var min_clearance = 20.0
	result["terrain_y"] = highest_terrain_y
	result["clearance"] = combat_area_y - highest_terrain_y
	result["valid"] = combat_area_y >= (highest_terrain_y + min_clearance)
	return result

func _check_combat_area_position(root: Node) -> bool:
	"""Check if CombatArea is positioned at least 20m above the highest terrain point."""
	var result = _check_combat_area_position_debug(root)
	return result["valid"]

func _check_terrain_collision_removed(root: Node) -> bool:
	"""Check if TerrainCollision has been removed from the scene."""
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		return true  # No static layer, so no collision to remove

	# Find terrain node
	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			# Check if this terrain has a TerrainCollision as direct child
			for terrain_child in child.get_children():
				if terrain_child is StaticBody3D or "TerrainCollision" in terrain_child.name or "Collision" in terrain_child.name:
					return false  # Found collision body - this is bad
			break

	return true  # No terrain collision found

func _update_workflow_sections(enabled: bool):
	"""Enable/disable validation and export sections based on workflow completion."""
	# Enable/disable buttons after step 4 (validation and export sections - steps 5-9)
	for i in range(4, workflow_buttons.size()):
		workflow_buttons[i].button.disabled = not enabled

	# Also control settings button
	settings_button.disabled = not enabled

func _update_label_visual(label: Label, text: String, is_valid: bool):
	"""Update label visual based on validation state."""
	if is_valid:
		label.text = "✅ " + text
		label.add_theme_color_override("font_color", Color(0.2, 0.8, 0.2))  # Green text
	else:
		label.text = "❌ " + text
		label.add_theme_color_override("font_color", Color(0.9, 0.2, 0.2))  # Red text

func _mark_button_complete_by_number(step_number: int):
	"""Mark a workflow button as completed by step number (1-9)."""
	for workflow_btn in workflow_buttons:
		if workflow_btn.number == step_number:
			workflow_btn.mark_complete()
			return

func _on_reset_workflow():
	"""Reset all workflow steps to their initial state."""
	print("🔄 Resetting workflow...")

	# Reset all workflow buttons
	for workflow_btn in workflow_buttons:
		workflow_btn.reset()

	# Reset validation labels to red X
	_update_label_visual(snapped_label, "Assets snapped to terrain", false)
	_update_label_visual(collision_removed_label, "TerrainCollision deleted from scene", false)

	# Disable validation/export buttons (steps 4-8) until checks pass again
	_update_workflow_sections(false)

	print("✅ Workflow reset complete - ready to start from Step 1!")
	print("   Run workflow checks again after completing Map Setup steps")

func _on_setup_terrain_collision():
	print("🗺️  Auto-detecting terrain in Static layer...")

	# Find the Static layer
	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		push_error("❌ No Static layer found! Make sure you have a map open.")
		return

	# Find terrain node (MP_Tungsten_Terrain, MP_Battery_Terrain, etc.)
	var terrain_parent = null
	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			terrain_parent = child
			print("   ✅ Found terrain parent: %s" % child.name)
			break

	if not terrain_parent:
		push_error("❌ No terrain found in Static layer! Looking for node like 'MP_Tungsten_Terrain'")
		return

	# Make terrain instance editable so we can access its children
	var scene_file = terrain_parent.scene_file_path
	if scene_file and scene_file != "":
		# Terrain is an instanced scene - make it editable
		root.set_editable_instance(terrain_parent, true)
		print("   ✅ Made terrain instance editable")
	else:
		# Terrain is a local node (not instanced) - already editable
		print("   ℹ️  Terrain is a local node (already editable)")

	# Find the actual mesh child (may be nested inside another instance)
	var terrain_mesh = null

	# First check direct children
	for child in terrain_parent.get_children():
		if child is MeshInstance3D:
			terrain_mesh = child
			print("   ✅ Found mesh child: %s" % child.name)
			break

	# If not found, check for nested instances (common with .glb imports)
	if not terrain_mesh:
		print("   🔍 Searching nested instances for MeshInstance3D...")
		for child in terrain_parent.get_children():
			# Make nested instances editable too
			if child.scene_file_path and child.scene_file_path != "":
				root.set_editable_instance(child, true)
				print("   ✅ Made nested instance editable: %s" % child.name)

			# Check this child's children
			for grandchild in child.get_children():
				if grandchild is MeshInstance3D:
					terrain_mesh = grandchild
					print("   ✅ Found mesh in nested instance: %s" % grandchild.name)
					break

			if terrain_mesh:
				break

	if not terrain_mesh:
		push_error("❌ No MeshInstance3D found in terrain hierarchy! Structure may be unexpected.")
		return

	print("🗺️  Setting up terrain collision for: %s" % terrain_mesh.name)

	# SIMPLE APPROACH: Create collision on mesh's parent node
	# This way collision automatically inherits correct transform hierarchy
	var mesh_parent = terrain_mesh.get_parent()
	if not mesh_parent:
		push_error("❌ Terrain mesh has no parent! Unexpected hierarchy.")
		return

	print("   ✅ Collision will be created on mesh parent: %s (Y=%.1f)" % [mesh_parent.name, mesh_parent.global_position.y])

	# Use undo/redo for this operation
	undo_redo.create_action("Setup Terrain Collision")

	# Check if StaticBody3D already exists
	var static_body = null
	for child in mesh_parent.get_children():
		if child is StaticBody3D:
			# Check if it already has a valid collision shape
			for grandchild in child.get_children():
				if grandchild is CollisionShape3D and grandchild.shape != null:
					print("   ℹ️  Terrain collision already exists with valid shape")
					undo_redo.commit_action()
					print("✅ Terrain collision already configured!")
					return
			static_body = child
			break

	if not static_body:
		# Create StaticBody3D
		static_body = StaticBody3D.new()
		static_body.name = "TerrainCollision"

		undo_redo.add_do_method(mesh_parent, "add_child", static_body)
		undo_redo.add_do_property(static_body, "owner", get_editor_interface().get_edited_scene_root())
		undo_redo.add_undo_method(mesh_parent, "remove_child", static_body)

		print("   ✅ Creating StaticBody3D on mesh parent")
	else:
		print("   ℹ️  StaticBody3D exists, will update collision shape")

	# Check if CollisionShape3D already exists
	var collision_shape = null
	if static_body:
		for child in static_body.get_children():
			if child is CollisionShape3D:
				collision_shape = child
				break

	if not collision_shape:
		# Create CollisionShape3D
		collision_shape = CollisionShape3D.new()
		collision_shape.name = "CollisionShape3D"

		undo_redo.add_do_method(static_body, "add_child", collision_shape)
		undo_redo.add_do_property(collision_shape, "owner", get_editor_interface().get_edited_scene_root())
		undo_redo.add_undo_method(static_body, "remove_child", collision_shape)

		print("   ✅ Creating CollisionShape3D")
	else:
		print("   ℹ️  CollisionShape3D already exists")

	# Create trimesh collision shape from mesh and position it to match mesh
	if terrain_mesh.mesh:
		var shape = terrain_mesh.mesh.create_trimesh_shape()
		var old_shape = collision_shape.shape
		var old_transform = collision_shape.transform

		undo_redo.add_do_property(collision_shape, "shape", shape)
		undo_redo.add_undo_property(collision_shape, "shape", old_shape)

		# CRITICAL: Position collision shape to match mesh's local transform
		undo_redo.add_do_property(collision_shape, "transform", terrain_mesh.transform)
		undo_redo.add_undo_property(collision_shape, "transform", old_transform)

		print("   ✅ Generating trimesh collision from mesh")
		print("   📊 Vertices: %d" % terrain_mesh.mesh.get_faces().size())
		print("   🔍 Collision shape positioned at local Y: %.1f" % terrain_mesh.transform.origin.y)
	else:
		push_error("   ❌ Terrain mesh has no mesh data!")
		undo_redo.commit_action()
		return

	undo_redo.commit_action()

	print("✅ Terrain collision setup complete!")
	print("   ⚠️  IMPORTANT: Wait 1-2 seconds before snapping!")
	print("   Physics needs time to update the collision shape.")
	print("   💡 Use Ctrl+Z to undo this operation if needed")

	# Mark button as complete
	_mark_button_complete_by_number(2)

func _on_validate_map():
	var root = get_editor_interface().get_edited_scene_root()

	if not root:
		push_error("❌ No scene open!")
		return

	print("🔍 Validating Portal map structure...")
	var errors = []
	var warnings = []

	# Check for Team HQs
	var team1_hq = root.find_child("TEAM_1_HQ", true, false)
	var team2_hq = root.find_child("TEAM_2_HQ", true, false)

	if not team1_hq:
		errors.append("Missing TEAM_1_HQ node")
	else:
		print("   ✅ TEAM_1_HQ found")
		# Check spawn points
		var spawns = 0
		for child in team1_hq.get_children():
			if "SpawnPoint" in child.name:
				spawns += 1
		if spawns < 4:
			warnings.append("TEAM_1_HQ has only %d spawn points (need at least 4)" % spawns)
		else:
			print("      ✅ %d spawn points" % spawns)

	if not team2_hq:
		errors.append("Missing TEAM_2_HQ node")
	else:
		print("   ✅ TEAM_2_HQ found")
		# Check spawn points
		var spawns = 0
		for child in team2_hq.get_children():
			if "SpawnPoint" in child.name:
				spawns += 1
		if spawns < 4:
			warnings.append("TEAM_2_HQ has only %d spawn points (need at least 4)" % spawns)
		else:
			print("      ✅ %d spawn points" % spawns)

	# Check for CombatArea
	var combat_area = root.find_child("CombatArea", true, false)
	if not combat_area:
		errors.append("Missing CombatArea node")
	else:
		print("   ✅ CombatArea found")
		# Check for CombatVolume
		var combat_volume = combat_area.find_child("CombatVolume", false, false)
		if not combat_volume:
			errors.append("CombatArea missing CombatVolume child")
		else:
			print("      ✅ CombatVolume configured")

	# Check for Static layer
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		warnings.append("Missing Static layer (for terrain and objects)")
	else:
		print("   ✅ Static layer found")
		var object_count = static_layer.get_child_count()
		print("      📦 %d static objects" % object_count)

	# Check if terrain collision will be exported (THIS IS BAD - bloats file to 200MB+)
	var terrain_found = false
	if static_layer:
		for child in static_layer.get_children():
			if "Terrain" in child.name and child is Node3D:
				terrain_found = true

				# Check if any collision bodies are DIRECT children (these WILL be exported)
				var collision_will_export = false
				for direct_child in child.get_children():
					if direct_child is StaticBody3D:
						collision_will_export = true
						errors.append("Terrain collision WILL BE EXPORTED! File will be 200MB+ instead of <1MB")
						print("      ❌ Terrain has StaticBody3D as direct child - WILL EXPORT")
						print("         This bloats .spatial.json from <1MB to 200MB+")
						print("         Delete collision or move it deeper (nested under Mesh)")
						break

				if not collision_will_export:
					# Check if collision exists somewhere (for informational purposes)
					var collision_body = child.find_child("TerrainCollision", true, false)
					if collision_body and collision_body is StaticBody3D:
						print("      ✅ Terrain collision exists but will NOT be exported")
						print("         Collision is nested safely (not a direct child)")
					else:
						print("      ✅ No terrain collision to export - file will be small")
						print("         (Collision optional - only needed for 'Snap to Floor')")
				break

	if not terrain_found:
		warnings.append("No terrain mesh found in Static layer")

	# Check HQs have protected areas (HQArea with PolygonVolume)
	print("\n   🔍 Checking HQ protected areas...")
	if team1_hq:
		# HQ_PlayerSpawner has HQArea property that references a PolygonVolume child
		var hq_area_child = team1_hq.find_child("HQ_Team1", false, false)
		if not hq_area_child:
			# Try alternate pattern
			for child in team1_hq.get_children():
				if "HQ" in child.name or "HQArea" in child.name:
					hq_area_child = child
					break

		if hq_area_child:
			print("      ✅ TEAM_1_HQ has protected area configured")
		else:
			warnings.append("TEAM_1_HQ missing HQArea child node (protected spawn zone)")

	if team2_hq:
		# HQ_PlayerSpawner has HQArea property that references a PolygonVolume child
		var hq_area_child = team2_hq.find_child("HQ_Team2", false, false)
		if not hq_area_child:
			# Try alternate pattern
			for child in team2_hq.get_children():
				if "HQ" in child.name or "HQArea" in child.name:
					hq_area_child = child
					break

		if hq_area_child:
			print("      ✅ TEAM_2_HQ has protected area configured")
		else:
			warnings.append("TEAM_2_HQ missing HQArea child node (protected spawn zone)")

	# Check for capture points and their capture areas
	print("\n   🔍 Checking capture points...")
	var capture_points = []
	for child in root.get_children():
		if "CapturePoint" in child.name or child.get_class() == "CapturePoint":
			capture_points.append(child)

	if capture_points.size() > 0:
		print("      Found %d capture point(s)" % capture_points.size())
		for cp in capture_points:
			# CapturePoints have a CaptureZone child node (PolygonVolume), not a property
			var capture_zone = cp.find_child("CaptureZone", false, false)
			if not capture_zone:
				# Try alternate naming patterns
				for child in cp.get_children():
					if "CaptureZone" in child.name or "Zone" in child.name:
						capture_zone = child
						break

			if capture_zone:
				print("         ✅ %s has capture zone configured" % cp.name)
			else:
				warnings.append("%s missing CaptureZone child node (capture area)" % cp.name)

			# Also check for spawn points
			var team1_spawns = cp.get("InfantrySpawnPoints_Team1") if cp.has_method("get") and "InfantrySpawnPoints_Team1" in cp else null
			var team2_spawns = cp.get("InfantrySpawnPoints_Team2") if cp.has_method("get") and "InfantrySpawnPoints_Team2" in cp else null

			if team1_spawns and team1_spawns is Array and team1_spawns.size() >= 3:
				print("         ✅ %s has %d Team 1 spawn points" % [cp.name, team1_spawns.size()])
			else:
				warnings.append("%s has insufficient Team 1 spawn points (need ≥3)" % cp.name)

			if team2_spawns and team2_spawns is Array and team2_spawns.size() >= 3:
				print("         ✅ %s has %d Team 2 spawn points" % [cp.name, team2_spawns.size()])
			else:
				warnings.append("%s has insufficient Team 2 spawn points (need ≥3)" % cp.name)
	else:
		print("      ℹ️  No capture points (OK for non-Conquest modes)")

	# Check if assets are snapped to terrain (sampling check)
	print("\n   🔍 Checking asset snapping...")
	if static_layer and terrain_found:
		# Sample some assets to check if they're at reasonable heights
		var sample_objects = []
		var count = 0
		for child in static_layer.get_children():
			if child is Node3D and "Terrain" not in child.name:
				sample_objects.append(child)
				count += 1
				if count >= 20:  # Sample first 20 objects
					break

		if sample_objects.size() > 0:
			var unsnapped_count = 0
			for obj in sample_objects:
				# Check if object is at default height (0) or very high/low
				var y = obj.global_position.y
				if abs(y) < 0.1 or abs(y) > 500:
					unsnapped_count += 1

			if unsnapped_count > sample_objects.size() / 2:
				warnings.append("Many assets may not be snapped to terrain (select all, then press Page Down)")
				print("      ⚠️  %d/%d sampled assets appear unsnapped" % [unsnapped_count, sample_objects.size()])
			else:
				print("      ✅ Assets appear to be snapped to terrain")
		else:
			print("      ℹ️  No assets to check for snapping")

	# Print summary
	var separator = _repeat_string("=", 70)
	print("\n" + separator)
	print("VALIDATION SUMMARY")
	print(separator)

	if errors.is_empty() and warnings.is_empty():
		print("✅ Map structure looks good!")
	else:
		if not errors.is_empty():
			print("❌ ERRORS (%d):" % errors.size())
			for error in errors:
				print("   - %s" % error)

		if not warnings.is_empty():
			print("⚠️  WARNINGS (%d):" % warnings.size())
			for warning in warnings:
				print("   - %s" % warning)

	print(separator)

	# Mark button as complete
	_mark_button_complete_by_number(7)

func _on_regenerate_tscn():
	var root = get_editor_interface().get_edited_scene_root()

	if not root:
		push_error("❌ No scene open!")
		return

	# Get map name from scene root node name
	var map_name = root.name
	if map_name.begins_with("MP_"):
		# Strip terrain prefix if present
		map_name = map_name.replace("MP_Tungsten", "").replace("MP_Battery", "").replace("MP_", "")
		if map_name.is_empty():
			map_name = "Kursk"  # Default fallback

	# Skip confirmation dialog for now - just regenerate
	_perform_regeneration(map_name)

func _perform_regeneration(map_name: String):
	print("🔄 Regenerating %s.tscn from BF1942 source..." % map_name)

	# Save current scene first (in case user wants to revert)
	get_editor_interface().save_scene()

	# Run portal_convert.py to regenerate
	# Note: res:// points to GodotProject/, we need to go up one level
	# Example: /Users/zach/Downloads/PortalSDK/GodotProject/ -> /Users/zach/Downloads/PortalSDK/
	var godot_project_root = ProjectSettings.globalize_path("res://")
	# Remove trailing slash if present
	if godot_project_root.ends_with("/"):
		godot_project_root = godot_project_root.substr(0, godot_project_root.length() - 1)
	# Go up one directory
	var portal_sdk_root = godot_project_root.get_base_dir()

	print("   🔍 Debug paths:")
	print("      Godot project: %s" % godot_project_root)
	print("      Portal SDK: %s" % portal_sdk_root)
	print("      Script path: %s/tools/portal_convert.py" % portal_sdk_root)

	var output = []
	# IMPORTANT: Run from Portal SDK root directory so path detection works correctly
	# GDScript OS.execute() doesn't support cwd parameter, so we use shell command to cd first
	var command = "cd '%s' && python3 tools/portal_convert.py --map '%s' --base-terrain '%s'" % [portal_sdk_root, map_name, base_terrain]
	var exit_code = OS.execute("sh", ["-c", command], output, true)

	if exit_code == 0:
		print("✅ Regeneration complete!")
		print(output[0])

		# Reload the scene
		print("🔄 Reloading scene...")
		get_editor_interface().reload_scene_from_path("res://levels/%s.tscn" % map_name)
		print("✅ Scene reloaded!")

		# Wait a frame for scene to fully load
		await get_tree().process_frame

		print("✅ Scene reloaded! Map regeneration complete.")
		print("")
		print("💡 Next steps:")
		print("   1. Setup terrain collision: Click 'Setup Terrain Collision' button")
		print("   2. Wait 2 seconds for physics to update")
		print("   3. Select all assets (Ctrl+A in scene tree)")
		print("   4. Snap to terrain: Press Page Down")
		print("   5. Save scene: Ctrl+S")

		# Mark button as complete
		_mark_button_complete_by_number(1)
	else:
		push_error("❌ Regeneration failed: " + str(output))

func _on_asset_report():
	var root = get_editor_interface().get_edited_scene_root()

	if not root:
		push_error("❌ No scene open!")
		return

	print("📊 Generating asset report...")
	var separator = _repeat_string("=", 70)

	# Find Static layer
	var static_layer = root.find_child("Static", true, false)

	if not static_layer:
		push_error("❌ No Static layer found!")
		return

	# Count assets by type
	var asset_counts = {}
	var total_assets = 0
	var terrain_count = 0

	for child in static_layer.get_children():
		if child is Node3D:
			total_assets += 1

			if "Terrain" in child.name:
				terrain_count += 1
				continue

			# Get asset type from name
			var asset_type = child.name.split("_")[0] if "_" in child.name else child.name

			if asset_type in asset_counts:
				asset_counts[asset_type] += 1
			else:
				asset_counts[asset_type] = 1

	# Sort by count (descending) - manual bubble sort to avoid lambda
	var sorted_types = asset_counts.keys()
	for i in range(sorted_types.size()):
		for j in range(i + 1, sorted_types.size()):
			if asset_counts[sorted_types[i]] < asset_counts[sorted_types[j]]:
				var temp = sorted_types[i]
				sorted_types[i] = sorted_types[j]
				sorted_types[j] = temp

	# Print report
	print("ASSET REPORT")
	print(separator)
	print("Total Assets: %d" % total_assets)
	print("Terrain Meshes: %d" % terrain_count)
	print("Prop Assets: %d" % (total_assets - terrain_count))
	print("")
	print("Asset Breakdown:")
	var dash_line = _repeat_string("-", 70)
	print(dash_line)

	for asset_type in sorted_types:
		var count = asset_counts[asset_type]
		var percentage = (count * 100.0) / (total_assets - terrain_count)
		print("  %-30s %4d  (%5.1f%%)" % [asset_type, count, percentage])

	print(separator)

	# Check for unmapped assets (objects with "UNMAPPED" in name)
	var unmapped_assets = []
	for child in static_layer.get_children():
		if "UNMAPPED" in child.name or "Unknown" in child.name:
			unmapped_assets.append(child.name)

	if unmapped_assets.size() > 0:
		print("\n⚠️  UNMAPPED ASSETS (%d):" % unmapped_assets.size())
		for asset_name in unmapped_assets:
			print("   - %s" % asset_name)
		print("\nThese BF1942 assets have no Portal equivalents yet.")
		print("Check tools/asset_audit/bf1942_to_portal_mappings.json to add mappings.")
	else:
		print("\n✅ All assets successfully mapped!")

	print(separator)

	# Mark button as complete
	_mark_button_complete_by_number(6)

func _on_export_spatial():
	var root = get_editor_interface().get_edited_scene_root()

	if not root:
		push_error("❌ No scene open!")
		return

	# Get map name from scene root node name
	var map_name = root.name
	if map_name.begins_with("MP_"):
		# Strip terrain prefix if present
		map_name = map_name.replace("MP_Tungsten", "").replace("MP_Battery", "").replace("MP_", "")
		if map_name.is_empty():
			map_name = "Kursk"  # Default fallback

	print("📦 Exporting %s to Portal format..." % map_name)

	# Save current scene first
	get_editor_interface().save_scene()

	# Run export_to_portal.py using shell command (same pattern as regenerate button)
	var godot_project_root = ProjectSettings.globalize_path("res://")
	if godot_project_root.ends_with("/"):
		godot_project_root = godot_project_root.substr(0, godot_project_root.length() - 1)
	var portal_sdk_root = godot_project_root.get_base_dir()

	var output = []
	var command = "cd '%s' && python3 tools/export_to_portal.py '%s' --spatial-only" % [portal_sdk_root, map_name]
	var exit_code = OS.execute("sh", ["-c", command], output, true)

	if exit_code == 0:
		print("✅ Export complete!")
		print(output[0])

		# Check file size and report it
		var spatial_path = portal_sdk_root + "/FbExportData/levels/%s.spatial.json" % map_name
		var file = FileAccess.open(spatial_path, FileAccess.READ)
		if file:
			var file_size_bytes = file.get_length()
			file.close()

			# Format file size nicely
			var file_size_str = ""
			if file_size_bytes < 1024:
				file_size_str = "%d B" % file_size_bytes
			elif file_size_bytes < 1024 * 1024:
				file_size_str = "%.1f KB" % (file_size_bytes / 1024.0)
			else:
				file_size_str = "%.1f MB" % (file_size_bytes / (1024.0 * 1024.0))

			print("   📦 File size: %s" % file_size_str)

			# Warn if file is too large (likely has terrain collision embedded)
			if file_size_bytes > 2 * 1024 * 1024:  # > 2 MB
				print("   ⚠️  WARNING: File is very large (>2MB)!")
				print("      This likely means terrain collision is embedded in the .tscn")
				print("      To fix: Delete the TerrainCollision node and re-export")
				print("      Expected size: <1MB")

		# Mark button as complete
		_mark_button_complete_by_number(8)
	else:
		push_error("❌ Export failed: " + str(output))

func _on_create_multi_experience():
	print("📦 Creating multi-map experience with settings...")
	print("   Game mode: %s" % game_mode)
	print("   Experience mode: %s" % experience_mode)
	print("   Max players: %d per team" % max_players)

	var godot_project_root = ProjectSettings.globalize_path("res://")
	# Remove trailing slash if present
	if godot_project_root.ends_with("/"):
		godot_project_root = godot_project_root.substr(0, godot_project_root.length() - 1)
	var portal_sdk_root = godot_project_root.get_base_dir()
	var output = []

	# Map game mode name to CLI format (handle spaces)
	var cli_game_mode = game_mode.replace(" ", "")  # "Team Deathmatch" -> "TeamDeathmatch"

	# Build experience name from base + suffix
	var experience_name = experience_filename_base
	if experience_filename_suffix != "":
		experience_name += experience_filename_suffix

	# Default to "My_Experience" if no name provided
	if experience_name == "":
		experience_name = "My_Experience"

	var final_filename = experience_name + "_Experience.json"
	print("   📁 Output filename: %s" % final_filename)

	# Build command with all settings including custom name
	var command = "cd '%s' && python3 tools/create_multi_map_experience.py --registry maps_registry.json --template all_maps_conquest --name '%s' --game-mode '%s' --max-players %d --mode %s" % [
		portal_sdk_root,
		experience_name,
		cli_game_mode,
		max_players,
		experience_mode
	]

	var exit_code = OS.execute("sh", ["-c", command], output, true)

	if exit_code == 0:
		print("✅ Multi-map experience created!")
		print(output[0])

		# Mark button as complete
		_mark_button_complete_by_number(9)
	else:
		push_error("❌ Creation failed: " + str(output))

func _on_cull_out_of_bounds():
	print("🗑️  Culling out-of-bounds assets...")

	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	# Find Static layer
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		push_error("❌ No Static layer found!")
		return

	# Find terrain and get its actual bounds
	var terrain_bounds_min = null
	var terrain_bounds_max = null

	for child in static_layer.get_children():
		if "Terrain" in child.name and child is Node3D:
			# Find the mesh to get actual terrain bounds
			var terrain_mesh = null
			for mesh_child in child.get_children():
				if mesh_child is MeshInstance3D:
					terrain_mesh = mesh_child
					break

			# Check nested instances
			if not terrain_mesh:
				for mesh_child in child.get_children():
					for grandchild in mesh_child.get_children():
						if grandchild is MeshInstance3D:
							terrain_mesh = grandchild
							break
					if terrain_mesh:
						break

			if terrain_mesh and terrain_mesh.mesh:
				# Get the mesh's local AABB
				var local_aabb = terrain_mesh.mesh.get_aabb()

				# Transform to global space
				var corners = [
					terrain_mesh.global_transform * local_aabb.position,
					terrain_mesh.global_transform * (local_aabb.position + Vector3(local_aabb.size.x, 0, 0)),
					terrain_mesh.global_transform * (local_aabb.position + Vector3(0, 0, local_aabb.size.z)),
					terrain_mesh.global_transform * (local_aabb.position + Vector3(local_aabb.size.x, 0, local_aabb.size.z)),
				]

				# Find min/max across all corners
				terrain_bounds_min = corners[0]
				terrain_bounds_max = corners[0]
				for corner in corners:
					terrain_bounds_min.x = min(terrain_bounds_min.x, corner.x)
					terrain_bounds_min.z = min(terrain_bounds_min.z, corner.z)
					terrain_bounds_max.x = max(terrain_bounds_max.x, corner.x)
					terrain_bounds_max.z = max(terrain_bounds_max.z, corner.z)

				print("   🗺️  Terrain bounds:")
				print("      X: [%.1f to %.1f]" % [terrain_bounds_min.x, terrain_bounds_max.x])
				print("      Z: [%.1f to %.1f]" % [terrain_bounds_min.z, terrain_bounds_max.z])
				break
			break

	if not terrain_bounds_min or not terrain_bounds_max:
		push_error("❌ Could not determine terrain bounds!")
		return

	# Collect objects to remove
	var objects_to_remove = []
	var total_objects = 0
	var debug_sample_count = 0
	var max_debug_samples = 5

	for child in static_layer.get_children():
		if child is Node3D and "Terrain" not in child.name:
			total_objects += 1
			var pos = child.global_position

			# Simple bounds check in XZ plane (ignore Y height)
			var inside_terrain = (
				pos.x >= terrain_bounds_min.x and pos.x <= terrain_bounds_max.x and
				pos.z >= terrain_bounds_min.z and pos.z <= terrain_bounds_max.z
			)

			# Debug output for first few objects
			if debug_sample_count < max_debug_samples:
				print("   🔍 Sample %d: %s" % [debug_sample_count + 1, child.name])
				print("      Position: (%.1f, %.1f, %.1f)" % [pos.x, pos.y, pos.z])
				print("      Inside terrain bounds: %s" % inside_terrain)
				debug_sample_count += 1

			# Remove if outside terrain bounds
			if not inside_terrain:
				objects_to_remove.append(child)

	if objects_to_remove.is_empty():
		print("✅ All assets are within bounds! (%d objects checked)" % total_objects)
		return

	print("   ⚠️  Found %d objects outside bounds (%.1f%%)" % [
		objects_to_remove.size(),
		(objects_to_remove.size() * 100.0) / total_objects
	])

	# Create undo/redo action
	undo_redo.create_action("Cull Out of Bounds Assets")

	for node in objects_to_remove:
		print("      🗑️  Removing: %s at (%.1f, %.1f, %.1f)" % [
			node.name,
			node.global_position.x,
			node.global_position.y,
			node.global_position.z
		])

		undo_redo.add_do_method(node.get_parent(), "remove_child", node)
		undo_redo.add_do_method(node, "queue_free")
		undo_redo.add_undo_method(node.get_parent(), "add_child", node)
		undo_redo.add_undo_property(node, "owner", node.owner)

	undo_redo.commit_action()

	var separator = _repeat_string("=", 70)
	print("\n" + separator)
	print("✅ CULLING COMPLETE")
	print(separator)
	print("Removed: %d objects" % objects_to_remove.size())
	print("Remaining: %d objects" % (total_objects - objects_to_remove.size()))
	print("   💡 Use Ctrl+Z to undo this operation if needed")
	print(separator)

	# Mark button as complete
	_mark_button_complete_by_number(4)

# Helper function to check if point is inside polygon (2D)
func _is_point_in_polygon(point: Vector2, polygon: PackedVector2Array) -> bool:
	# Ray casting algorithm for point-in-polygon test
	var inside = false
	var j = polygon.size() - 1

	for i in range(polygon.size()):
		var pi = polygon[i]
		var pj = polygon[j]

		if ((pi.y > point.y) != (pj.y > point.y)) and \
		   (point.x < (pj.x - pi.x) * (point.y - pi.y) / (pj.y - pi.y) + pi.x):
			inside = not inside

		j = i

	return inside

func _on_rotate_terrain_90():
	print("🔄 Rotating terrain by 90 degrees and recentering...")

	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	# Find Static layer
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		push_error("❌ No Static layer found!")
		return

	# Find terrain node (MP_Tungsten_Terrain, MP_Battery_Terrain, etc.)
	var terrain_parent = null
	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			terrain_parent = child
			print("   ✅ Found terrain: %s" % child.name)
			break

	if not terrain_parent:
		push_error("❌ No terrain found in Static layer!")
		return

	# Find terrain mesh to get mesh center coordinates
	var terrain_mesh = null
	for child in terrain_parent.get_children():
		if child is MeshInstance3D:
			terrain_mesh = child
			break

	# Check nested instances
	if not terrain_mesh:
		for child in terrain_parent.get_children():
			for grandchild in child.get_children():
				if grandchild is MeshInstance3D:
					terrain_mesh = grandchild
					break
			if terrain_mesh:
				break

	if not terrain_mesh or not terrain_mesh.mesh:
		push_error("❌ No terrain mesh found!")
		return

	# Get mesh center from AABB (same logic as Python TerrainProvider)
	var mesh_aabb = terrain_mesh.mesh.get_aabb()
	var mesh_center_local = mesh_aabb.get_center()
	var mesh_center_x = mesh_center_local.x
	var mesh_center_z = mesh_center_local.z
	var mesh_y_baseline = mesh_aabb.position.y  # Y baseline

	print("   📐 Original mesh center: (%.1f, %.1f)" % [mesh_center_x, mesh_center_z])
	print("   📐 Mesh Y baseline: %.1f" % mesh_y_baseline)

	# Get current rotation and transform
	var old_rotation = terrain_parent.rotation
	var old_transform = terrain_parent.transform
	var old_position = terrain_parent.position

	# Calculate new rotation (add 90 degrees around Y axis)
	var new_rotation = old_rotation
	new_rotation.y += PI / 2.0  # 90 degrees in radians
	var total_rotation_deg = rad_to_deg(new_rotation.y)

	print("   🔍 Current rotation: (%.2f, %.2f, %.2f) degrees" % [
		rad_to_deg(old_rotation.x),
		rad_to_deg(old_rotation.y),
		rad_to_deg(old_rotation.z)
	])
	print("   🔍 New rotation: (%.2f, %.2f, %.2f) degrees" % [
		rad_to_deg(new_rotation.x),
		rad_to_deg(new_rotation.y),
		rad_to_deg(new_rotation.z)
	])

	# Calculate rotated centering offsets (same logic as Python CenteringService)
	# When terrain rotates around Y-axis, mesh center coordinates also rotate
	var rotation_rad = new_rotation.y
	var cos_r = cos(rotation_rad)
	var sin_r = sin(rotation_rad)

	# Apply Y-axis rotation to mesh center coordinates
	var rotated_center_x = cos_r * mesh_center_x + sin_r * mesh_center_z
	var rotated_center_z = -sin_r * mesh_center_x + cos_r * mesh_center_z

	# Negate rotated coordinates to center at origin
	# Y offset brings terrain's lowest point to Y=0 (Portal ground plane)
	var new_position = Vector3(-rotated_center_x, -mesh_y_baseline, -rotated_center_z)

	print("   📐 Rotated mesh center: (%.1f, %.1f)" % [rotated_center_x, rotated_center_z])
	print("   📐 New terrain position: (%.1f, %.1f, %.1f)" % [new_position.x, new_position.y, new_position.z])

	# Build new transform with rotation + position
	# We need to construct Transform3D manually to combine rotation and translation
	var new_basis = Basis()
	new_basis = new_basis.rotated(Vector3.UP, new_rotation.y)
	var new_transform = Transform3D(new_basis, new_position)

	# Apply rotation and position using undo/redo
	undo_redo.create_action("Rotate Terrain 90° and Recenter")
	undo_redo.add_do_property(terrain_parent, "transform", new_transform)
	undo_redo.add_undo_property(terrain_parent, "transform", old_transform)
	undo_redo.commit_action()

	# Also rotate CombatArea to match terrain
	print("\n   🔄 Rotating CombatArea to match terrain...")
	var combat_area = root.find_child("CombatArea", true, false)
	if combat_area:
		var old_combat_transform = combat_area.transform
		var old_combat_position = combat_area.position

		# CombatArea rotates same as terrain, stays centered at origin (0, Y, 0)
		var combat_basis = Basis()
		combat_basis = combat_basis.rotated(Vector3.UP, new_rotation.y)
		var combat_position = Vector3(0, old_combat_position.y, 0)  # Keep Y height, zero XZ
		var new_combat_transform = Transform3D(combat_basis, combat_position)

		undo_redo.create_action("Rotate CombatArea with Terrain")
		undo_redo.add_do_property(combat_area, "transform", new_combat_transform)
		undo_redo.add_undo_property(combat_area, "transform", old_combat_transform)
		undo_redo.commit_action()

		print("   ✅ CombatArea rotated to match terrain")
	else:
		print("   ⚠️  No CombatArea found to rotate")

	var separator = _repeat_string("=", 70)
	print("\n" + separator)
	print("✅ TERRAIN ROTATED AND RECENTERED")
	print(separator)
	print("Terrain: %s" % terrain_parent.name)
	print("Y rotation: %.1f° → %.1f°" % [
		rad_to_deg(old_rotation.y),
		total_rotation_deg
	])
	print("Position: (%.1f, %.1f, %.1f) → (%.1f, %.1f, %.1f)" % [
		old_position.x, old_position.y, old_position.z,
		new_position.x, new_position.y, new_position.z
	])
	print("   💡 Use Ctrl+Z to undo this operation if needed")
	print("   💡 All children (mesh, collision) rotate automatically")
	print("   💡 CombatArea also rotated to stay aligned with terrain")
	print(separator)

	# Note: Rotate Terrain is optional utility, not part of workflow, so we don't mark it complete

func _on_list_terrain_contents():
	print("📋 Listing terrain contents...")

	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	# Find Static layer
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		push_error("❌ No Static layer found!")
		return

	# Find terrain node
	var terrain_parent = null
	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			terrain_parent = child
			break

	if not terrain_parent:
		push_error("❌ No terrain found in Static layer!")
		return

	print("✅ Found terrain: %s" % terrain_parent.name)
	print("   Scene file: %s" % terrain_parent.scene_file_path)

	# Make terrain editable to see children
	var was_editable = false
	if terrain_parent.scene_file_path and terrain_parent.scene_file_path != "":
		was_editable = root.is_editable_instance(terrain_parent)
		if not was_editable:
			root.set_editable_instance(terrain_parent, true)
			print("   ✅ Made terrain editable to inspect children")

	var separator = _repeat_string("=", 70)
	print("\n" + separator)
	print("TERRAIN CHILD NODES")
	print(separator)

	# Recursively list all children
	_list_children_recursive(terrain_parent, 1)

	print(separator)
	print("\n💡 To remove unwanted structures:")
	print("   1. Open res://static/%s.tscn in Godot" % terrain_parent.name)
	print("   2. Select the terrain's 'Mesh' node")
	print("   3. Right-click → 'Editable Children' (to see GLB contents)")
	print("   4. Delete unwanted nodes (buildings, towers, etc.)")
	print("   5. Save as: res://static/%s_Clean.tscn" % terrain_parent.name.replace("_Terrain", "_Terrain"))
	print("   6. Update Kursk.tscn to use the clean version")

	# Restore editable state
	if not was_editable and terrain_parent.scene_file_path != "":
		root.set_editable_instance(terrain_parent, false)

	# Mark button as complete
	_mark_button_complete_by_number(5)

func _on_snap_all_to_terrain():
	"""Automatically snap all objects to terrain using physics raycasting."""
	print("🔧 Snapping ALL objects to terrain...")

	var root = get_editor_interface().get_edited_scene_root()
	if not root:
		push_error("❌ No scene open!")
		return

	# Find Static layer and terrain
	var static_layer = root.find_child("Static", true, false)
	if not static_layer:
		push_error("❌ No Static layer found!")
		return

	var terrain_node = null
	for child in static_layer.get_children():
		if "Terrain" in child.name and "_Terrain" in child.name:
			terrain_node = child
			break

	if not terrain_node:
		push_error("❌ No terrain found in Static layer!")
		return

	print("🌍 Found terrain: %s" % terrain_node.name)

	# Find the terrain collision body - we ONLY want to raycast against this
	var terrain_collision_rid = null
	var terrain_collision_body = terrain_node.find_child("TerrainCollision", true, false)
	if terrain_collision_body and terrain_collision_body is StaticBody3D:
		terrain_collision_rid = terrain_collision_body.get_rid()
		print("   ✅ Found terrain collision body (RID: %s)" % terrain_collision_rid)
	else:
		push_error("❌ No terrain collision found! Run 'Setup Terrain Collision' first.")
		return

	# Get physics space for raycasting
	var space_state = root.get_world_3d().direct_space_state
	if not space_state:
		push_error("❌ No physics space available!")
		return

	var separator = _repeat_string("=", 70)
	print(separator)

	var total_snapped = 0
	const RAYCAST_HEIGHT = 1000.0
	const RAYCAST_DEPTH = 2000.0

	# Start undo/redo action for all snapping
	undo_redo.create_action("Snap All Objects to Terrain")

	# 1. Snap gameplay objects at root level
	print("\n📍 GAMEPLAY OBJECTS (Root Level)")
	print(_repeat_string("-", 70))

	for child in root.get_children():
		if child == static_layer or not child is Node3D:
			continue

		# Check if this is a gameplay object
		var is_gameplay = ("HQ" in child.name or "CapturePoint" in child.name or
		                   "VehicleSpawner" in child.name or "StationaryEmplacement" in child.name)

		if is_gameplay:
			# Snap the parent object
			if _snap_node_to_terrain_with_undo(child, space_state, root, RAYCAST_HEIGHT, RAYCAST_DEPTH, terrain_collision_rid):
				total_snapped += 1

			# Snap all spawn point children
			for spawn in child.get_children():
				if "Spawn" in spawn.name and spawn is Node3D:
					if _snap_node_to_terrain_with_undo(spawn, space_state, child, RAYCAST_HEIGHT, RAYCAST_DEPTH, terrain_collision_rid):
						total_snapped += 1

	# 2. Snap all static objects
	print("\n🏗️  STATIC OBJECTS (Visual Assets)")
	print(_repeat_string("-", 70))

	for child in static_layer.get_children():
		if not child is Node3D:
			continue

		# Skip terrain itself
		if "Terrain" in child.name or "Assets" in child.name:
			continue

		if _snap_node_to_terrain_with_undo(child, space_state, static_layer, RAYCAST_HEIGHT, RAYCAST_DEPTH, terrain_collision_rid):
			total_snapped += 1

	# Commit all changes as one undo action
	undo_redo.commit_action()

	print("\n" + separator)
	print("✅ Snapped %d objects to terrain!" % total_snapped)
	print("   💡 Use Ctrl+Z to undo all changes if needed")
	print(separator)

	# Mark button as complete
	_mark_button_complete_by_number(3)


func _snap_node_to_terrain_with_undo(node: Node3D, space_state: PhysicsDirectSpaceState3D,
                                       parent: Node3D, ray_height: float, ray_depth: float, terrain_rid: RID) -> bool:
	"""Snap a single node to terrain and record in undo/redo. Returns true if snapped."""
	var world_pos = node.global_position

	# Cast ray from high above to terrain below
	var ray_start = world_pos + Vector3(0, ray_height, 0)
	var ray_end = world_pos - Vector3(0, ray_depth, 0)

	var query = PhysicsRayQueryParameters3D.create(ray_start, ray_end)
	query.collide_with_areas = false
	query.collide_with_bodies = true

	var result = space_state.intersect_ray(query)

	# CRITICAL FIX: Verify we hit the TERRAIN, not another object
	# If we hit something else (like the object itself), ignore it and keep trying
	while result and result.has("rid") and result["rid"] != terrain_rid:
		# Hit something else (e.g., the object itself) - start ray BELOW this hit point
		ray_start = result["position"] - Vector3(0, 0.1, 0)  # Start slightly below the hit
		query = PhysicsRayQueryParameters3D.create(ray_start, ray_end)
		query.collide_with_areas = false
		query.collide_with_bodies = true
		result = space_state.intersect_ray(query)

	if result and result["rid"] == terrain_rid:
		# Hit terrain! Calculate new position
		var hit_point = result["position"]
		var new_local_pos = parent.to_local(hit_point)

		# Preserve X and Z, only update Y
		new_local_pos.x = node.position.x
		new_local_pos.z = node.position.z

		var old_y = node.position.y
		var delta_y = new_local_pos.y - old_y

		# Only snap if there's a meaningful difference (> 0.01m)
		if abs(delta_y) > 0.01:
			# Record old and new positions in undo/redo
			var old_pos = node.position
			undo_redo.add_do_property(node, "position", new_local_pos)
			undo_redo.add_undo_property(node, "position", old_pos)

			var emoji = "✓" if abs(delta_y) < 0.1 else "📐"
			print("  %s %s: Y %.2f → %.2f (Δ%.2f)" % [emoji, node.name, old_y, new_local_pos.y, delta_y])
			return true
	else:
		print("  ⚠️  %s: No terrain hit (outside bounds?)" % node.name)

	return false


func _list_children_recursive(node: Node, depth: int):
	"""Recursively list all child nodes with indentation."""
	for child in node.get_children():
		var indent = ""
		for i in range(depth):
			indent += "  "

		var node_type = child.get_class()
		var node_name = child.name

		# Highlight potential structures to remove
		var marker = ""
		if "Electric" in node_name or "Tower" in node_name or "Power" in node_name:
			marker = " [⚡ ELECTRIC TOWER?]"
		elif "Apartment" in node_name or "Building" in node_name or "House" in node_name:
			marker = " [🏢 BUILDING?]"
		elif "Industrial" in node_name or "Factory" in node_name:
			marker = " [🏭 INDUSTRIAL?]"
		elif node_type == "MeshInstance3D":
			marker = " [🗺️  TERRAIN MESH - KEEP]"

		print("%s├─ %s (%s)%s" % [indent, node_name, node_type, marker])

		# Recurse if node has children
		if child.get_child_count() > 0:
			_list_children_recursive(child, depth + 1)
