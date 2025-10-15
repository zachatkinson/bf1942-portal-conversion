@tool
extends EditorPlugin

var toolbar: HBoxContainer
var test_button: Button

func _enter_tree():
	print("BF1942 Tools: Plugin loading...")

	# Create simple toolbar
	toolbar = HBoxContainer.new()

	# Add one test button
	test_button = Button.new()
	test_button.text = "Test"
	test_button.pressed.connect(_on_test)
	toolbar.add_child(test_button)

	# Add to editor
	add_control_to_container(CONTAINER_SPATIAL_EDITOR_MENU, toolbar)
	print("BF1942 Tools: Plugin loaded successfully!")

func _exit_tree():
	if toolbar:
		remove_control_from_container(CONTAINER_SPATIAL_EDITOR_MENU, toolbar)
		toolbar.queue_free()
	print("BF1942 Tools: Plugin unloaded")

func _on_test():
	print("Test button clicked!")
