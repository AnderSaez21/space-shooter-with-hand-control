extends Area2D # O CharacterBody2D, lo que uses

@export var hand_input : Node
@onready var laser_prefab = preload("res://prefabs/laser.tscn")
@onready var explosion_prefab = preload("res://prefabs/explosion.tscn")
signal player_killed

# VELOCIDAD
var speed = 600.0 # Píxeles por segundo (ajústalo)
var can_shoot = true
var shoot_cooldown = 0.3

func _physics_process(delta):
	# 1. OBTENER INPUT (Del Joystick Virtual)
	var direction = hand_input.input_vector
	
	# 2. MOVER LA NAVE
	# Posición = Posición + (Dirección * Velocidad * Tiempo)
	position += direction * speed * delta
	
	# 3. MANTENER DENTRO DE LA PANTALLA (Clamping)
	var screen_size = get_viewport_rect().size
	# Asumiendo que el sprite mide unos 50px, ponemos márgenes
	position.x = clamp(position.x, 20, screen_size.x - 20)
	position.y = clamp(position.y, 20, screen_size.y - 20)
		
	# 4. DISPARO (Igual que antes)
	if (hand_input.is_shooting or Input.is_action_pressed("player_shoot")) and can_shoot:
		shoot_laser()

func shoot_laser():
	# ... (Tu código de disparo se queda igual) ...
	var laser = laser_prefab.instantiate()
	laser.position = position
	get_parent().add_child(laser)
	can_shoot = false
	await get_tree().create_timer(shoot_cooldown).timeout
	can_shoot = true


func _on_area_entered(area: Area2D) -> void:
	if area is meteor:
		var explosion = explosion_prefab.instantiate()
		explosion.position = position
		get_parent().add_child(explosion)
		queue_free()
		player_killed.emit()
		
