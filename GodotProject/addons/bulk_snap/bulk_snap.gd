@tool
extends EditorScript

# Bulk snap all selected nodes to terrain trimesh collision
# Usage: Select all objects, then run this script (File → Run)

func _run():
	var editor_selection = get_editor_interface().get_selection()
	var selected_nodes = editor_selection.get_selected_nodes()

	if selected_nodes.is_empty():
		print("❌ No nodes selected. Select objects to snap first!")
		return

	print("🎯 Snapping %d objects to terrain..." % selected_nodes.size())

	var space_state = get_scene().get_world_3d().direct_space_state
	var snapped_count = 0
	var failed_count = 0

	for node in selected_nodes:
		if node is Node3D:
			var origin = node.global_position

			# Raycast downward from object position
			var ray_start = Vector3(origin.x, 200, origin.z)  # Start high above
			var ray_end = Vector3(origin.x, -200, origin.z)   # End far below

			var query = PhysicsRayQueryParameters3D.create(ray_start, ray_end)
			query.collide_with_areas = false
			query.collide_with_bodies = true

			var result = space_state.intersect_ray(query)

			if result:
				# Hit terrain! Snap to hit point
				var new_y = result.position.y
				node.global_position = Vector3(origin.x, new_y, origin.z)
				snapped_count += 1
			else:
				print("   ⚠️  No terrain hit for: %s at (%.1f, %.1f)" % [node.name, origin.x, origin.z])
				failed_count += 1

	print("✅ Snapped %d objects" % snapped_count)
	if failed_count > 0:
		print("⚠️  Failed to snap %d objects (no terrain below)" % failed_count)
	print("Done!")
