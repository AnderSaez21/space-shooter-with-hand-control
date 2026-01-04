extends Node

var server := UDPServer.new()
const PORT = 4242

# --- VARIABLES PÚBLICAS (Esto es lo que el Player está buscando) ---
# Antes usábamos 'hand_position', ahora usamos 'input_vector' para el joystick
var input_vector := Vector2.ZERO  
var is_shooting := false

func _ready():
	server.listen(PORT)
	print("Servidor UDP Joystick listo en puerto: " + str(PORT))

func _process(delta):
	server.poll()
	if server.is_connection_available():
		var peer : PacketPeerUDP = server.take_connection()
		var packet = peer.get_packet()
		
		# Esperamos 12 bytes: Vector X (4) + Vector Y (4) + Disparo (4)
		if packet.size() >= 12:
			var x_vec = packet.decode_float(0)
			var y_vec = packet.decode_float(4)
			var shoot_val = packet.decode_float(8)
			
			# Actualizamos la variable que el Player está buscando
			input_vector = Vector2(x_vec, y_vec)
			
			# Actualizamos disparo
			is_shooting = (shoot_val > 0.5)
