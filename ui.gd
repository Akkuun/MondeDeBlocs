extends Control

var actions: Node

func _ready() -> void:
	actions = get_tree().current_scene.get_node(".")

func _on_button_button_down() -> void:
	actions.move_above()

func _on_button_remettre_debout() -> void:
	actions.get_up()

func _on_button_faire_tomber() -> void:
	actions.put_down()
