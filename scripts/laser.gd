extends Area2D
class_name laser

@export var speed = 60

func _ready() -> void:
	pass # Replace with function body.

func _process(_delta):
	position.x += speed
