extends Node

@export var obj1: RigidBody3D
@export var obj2: RigidBody3D

@export var pointPrefab: PackedScene

var currentPoint: Node3D = null

@export var ui: Control

func _ready() -> void:
	clear_selection()

func _input(_event: InputEvent) -> void:
	# raycast to egt object
	if _event is InputEventMouseButton and _event.button_index == MOUSE_BUTTON_LEFT and _event.pressed:
		var viewport = get_viewport()
		var camera = viewport.get_camera_3d()
		if camera:
			var from = camera.project_ray_origin(_event.position)
			var to = from + camera.project_ray_normal(_event.position) * 1000
			var space_state = camera.get_world_3d().direct_space_state
			var ray_params = PhysicsRayQueryParameters3D.new()
			ray_params.from = from
			ray_params.to = to
			var result = space_state.intersect_ray(ray_params)
			if result.has("collider") and result["collider"] is RigidBody3D:
				select_object(result["collider"], result.position)

func clear_selection() -> void:
	obj1 = null
	obj2 = null
	ui.find_child("Obj1").text = "None"
	ui.find_child("Obj2").text = "None"

	if currentPoint:
		currentPoint.queue_free()
		currentPoint = null

func select_object(node: RigidBody3D, hit_position: Vector3) -> void:
	if Input.is_key_pressed(KEY_SHIFT):
		if node.name == "Table":
			# instanciate a point at hit_position
			if currentPoint:
				currentPoint.queue_free()
			currentPoint = pointPrefab.instantiate()
			currentPoint.position = hit_position
			currentPoint.position.y -= 0.15
			currentPoint.scale = Vector3(0.3, 0.3, 0.3)
			add_child(currentPoint)
			ui.find_child("Obj2").text = "Point (x: " + str(snapped(hit_position.x, 0.01)) + ", y: " + str(snapped(hit_position.y, 0.01)) + ", z: " + str(snapped(hit_position.z, 0.01)) + ")"
			obj2 = currentPoint	
			return
		else:
			print("Obj2 selected: " + node.name)
				# Update UI
			ui.find_child("Obj2").text = node.name
			obj2 = node
	else:
		if node.name == "Table":
			return
		else:
			print("Obj1 selected: " + node.name)
				# Update UI
			ui.find_child("Obj1").text = node.name
			obj1 = node

func move_above() -> void:
	# obj1 and obj2 top must be empty (to do later)
	var node = obj1
	var target = obj2
	
	node.lock_rotation = true

	var targetPos = target.get_position()
	if target.name == "Donut Saucisse" || target.name == "DonutSaucisse":
		if target.has_node("HolePos"):
			var hole = target.get_node("HolePos")
			targetPos = hole.global_transform.origin
			print("Using HolePos for Donut Saucisse")
	var endPos = Vector3(targetPos.x, targetPos.y + 5, targetPos.z)
	var tween = create_tween()
	tween.tween_property(node, "position", endPos, 0.5)

	clear_selection()	

# pushes the object to make it fall
func put_down() -> void:
	var node = obj1
	
	node.lock_rotation = false
	
	node.apply_torque_impulse(Vector3(10, 0, 0))

	clear_selection()

# hard resets the object orientation
func get_up() -> void:
	var node = obj1
	
	node.lock_rotation = true
	
	var basis = node.global_transform.basis
	basis = Basis(Vector3(1, 0, 0), 0) * Basis(Vector3(0, 1, 0), 0) * Basis(Vector3(0, 0, 1), 0)
	node.global_transform.basis = basis

	clear_selection()
