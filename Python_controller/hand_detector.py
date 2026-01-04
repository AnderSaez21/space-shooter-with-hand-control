import cv2
import mediapipe as mp
import socket
import struct
import math

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_PORT = 4242
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- SENSITIVITY ZONE (MODIFIED) ---
# DEADZONE: Area where movement is ignored. Before 0.03, now 0.01 (Almost instant)
DEADZONE = 0.01 
# MAX_REACH: Distance required to reach max speed. Before 0.15, now 0.05
# This means moving the hand just 5% of the screen width makes the ship go full speed.
MAX_REACH = 0.12 

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# State variables
anchor_pos = None 

print("--- HIGH SENSITIVITY MODE ACTIVATED ---")
print("RIGHT HAND: Make a fist. Move VERY SLIGHTLY to go fast.")

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
            # Get handedness (Left vs Right)
            lbl = results.multi_handedness[idx].classification[0].label
            
            # --- RIGHT HAND (MOVEMENT) ---
            if lbl == "Right":
                right_hand_detected = True
                curr_x = hand_landmarks.landmark[9].x
                curr_y = hand_landmarks.landmark[9].y
                
                # Detect fist (Index tip vs knuckle)
                # If the tip (8) is lower (higher Y value) than the knuckle (6), it's a fist
                is_fist = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y

                if is_fist:
                    if anchor_pos is None:
                        anchor_pos = (curr_x, curr_y)
                    
                    # Calculate difference
                    diff_x = curr_x - anchor_pos[0]
                    diff_y = curr_y - anchor_pos[1]
                    
                    # Visual: Draw the joystick
                    h, w, c = frame.shape
                    cx, cy = int(anchor_pos[0] * w), int(anchor_pos[1] * h)
                    px, py = int(curr_x * w), int(curr_y * h)
                    
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1) # Anchor point (Blue)
                    cv2.line(frame, (cx, cy), (px, py), (0, 255, 255), 2) # Drag line (Yellow)
                    
                    # --- SENSITIVE VECTOR CALCULATION ---
                    # X Axis
                    if abs(diff_x) < DEADZONE: 
                        final_vector_x = 0.0
                    else: 
                        # Here is the magic: by dividing by a very small MAX_REACH,
                        # the result (force) increases very quickly.
                        val = (diff_x - math.copysign(DEADZONE, diff_x)) / (MAX_REACH - DEADZONE)
                        final_vector_x = max(-1.0, min(1.0, val))
                    
                    # Y Axis
                    if abs(diff_y) < DEADZONE: 
                        final_vector_y = 0.0
                    else: 
                        val = (diff_y - math.copysign(DEADZONE, diff_y)) / (MAX_REACH - DEADZONE)
                        final_vector_y = max(-1.0, min(1.0, val))

                else:
                    anchor_pos = None # Release the joystick if hand opens

            # --- LEFT HAND (SHOOTING) ---
            if lbl == "Left":
                # Check for fist/gesture to shoot
                if hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y:
                    shoot_command = 1.0
                    # Visual feedback for shooting
                    cv2.circle(frame, (50, 50), 20, (0, 255, 0), -1)

    if not right_hand_detected:
        anchor_pos = None

    try:
        # Pack data: 3 floats (vector x, vector y, shoot trigger)
        data = struct.pack('fff', final_vector_x, final_vector_y, shoot_command)
        sock.sendto(data, (UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)

    cv2.imshow('AI Joystick (High Sensitivity)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()