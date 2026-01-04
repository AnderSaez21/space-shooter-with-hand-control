extends GPUParticles2D

func _ready():
	# Forzamos que empiece la explosión nada más nacer
	emitting = true

# Conecta la señal "finished" desde la pestaña Nodos -> Señales a este script
func _on_finished():
	queue_free()
