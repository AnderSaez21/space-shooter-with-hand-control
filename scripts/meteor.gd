extends Area2D
class_name meteor

@export var speed = -2
@onready var explosion_prefab = preload("res://prefabs/explosion.tscn")
signal meteor_killed

func _ready() -> void:
	pass # Replace with function body.

func _process(_delta):
	position.x += speed


func _on_area_entered(area):
	if area is laser:
		var explosion = explosion_prefab.instantiate()
		explosion.position = position
		get_parent().add_child(explosion)
		queue_free()
		area.queue_free()
		meteor_killed.emit()
