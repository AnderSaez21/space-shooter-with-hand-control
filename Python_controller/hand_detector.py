import cv2
import mediapipe as mp
import socket
import struct
import math

# --- CONFIGURACIÓN ---
UDP_IP = "127.0.0.1"
UDP_PORT = 4242
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- ZONA DE SENSIBILIDAD (MODIFICADO) ---
# DEADZONE: Zona muerta. Antes 0.03, ahora 0.01 (Casi instantáneo)
DEADZONE = 0.01   
# MAX_REACH: Distancia para velocidad tope. Antes 0.15, ahora 0.05
# Significa que con mover la mano un 5% de la pantalla, la nave ya va a tope.
MAX_REACH = 0.12 

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Variables de estado
anchor_pos = None 

print("--- MODO ALTA SENSIBILIDAD ACTIVADO ---")
print("MANO DERECHA: Cierra el puño. Mueve MUY POCO para ir rápido.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    final_vector_x = 0.0
    final_vector_y = 0.0
    shoot_command = 0.0
    
    right_hand_detected = False

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            lbl = results.multi_handedness[idx].classification[0].label
            
            # --- MANO DERECHA (MOVIMIENTO) ---
            if lbl == "Right":
                right_hand_detected = True
                curr_x = hand_landmarks.landmark[9].x
                curr_y = hand_landmarks.landmark[9].y
                
                # Detectar puño (Indice punta vs nudillo)
                is_fist = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y

                if is_fist:
                    if anchor_pos is None:
                        anchor_pos = (curr_x, curr_y)
                    
                    # Calcular diferencia
                    diff_x = curr_x - anchor_pos[0]
                    diff_y = curr_y - anchor_pos[1]
                    
                    # Visual: Dibujar
                    h, w, c = frame.shape
                    cx, cy = int(anchor_pos[0] * w), int(anchor_pos[1] * h)
                    px, py = int(curr_x * w), int(curr_y * h)
                    
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                    cv2.line(frame, (cx, cy), (px, py), (0, 255, 255), 2)
                    
                    # --- CÁLCULO VECTORIAL SENSIBLE ---
                    # Eje X
                    if abs(diff_x) < DEADZONE: 
                        final_vector_x = 0.0
                    else: 
                        # Aquí está la magia: al dividir por un MAX_REACH muy pequeño,
                        # el resultado (fuerza) sube muy rápido.
                        val = (diff_x - math.copysign(DEADZONE, diff_x)) / (MAX_REACH - DEADZONE)
                        final_vector_x = max(-1.0, min(1.0, val))
                    
                    # Eje Y
                    if abs(diff_y) < DEADZONE: 
                        final_vector_y = 0.0
                    else: 
                        val = (diff_y - math.copysign(DEADZONE, diff_y)) / (MAX_REACH - DEADZONE)
                        final_vector_y = max(-1.0, min(1.0, val))

                else:
                    anchor_pos = None # Soltamos el joystick

            # --- MANO IZQUIERDA (DISPARO) ---
            if lbl == "Left":
                if hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y:
                    shoot_command = 1.0
                    cv2.circle(frame, (50, 50), 20, (0, 255, 0), -1)

    if not right_hand_detected:
        anchor_pos = None

    try:
        data = struct.pack('fff', final_vector_x, final_vector_y, shoot_command)
        sock.sendto(data, (UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)

    cv2.imshow('Joystick IA (Alta Sensibilidad)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()