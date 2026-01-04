extends Node2D

@onready var meteor_prefab = preload("res://prefabs/meteor.tscn")

var score = 0

func _ready() -> void:
	pass # Replace with function body.

func _process(_delta):
	pass

func _on_meteor_timer_timeout():
	var meteor = meteor_prefab.instantiate()
	var random_y = randi_range(30,610)
	meteor.position = Vector2(1000,random_y)
	meteor.meteor_killed.connect(_on_meteor_killed)
	add_child(meteor)
	
func _update_ui():
	$game_ui/score_label.text = "Score: " + str(score)
	
func _on_meteor_killed():
	score += 50
	_update_ui()


func _on_player_player_killed():
	$restart_timer.start()
	


func _on_restart_timer_timeout():
	get_tree().reload_current_scene()
