
![shooter_video](https://github.com/user-attachments/assets/6b241767-084f-4e9b-9174-b9d797c07d4b)

# Space Shooter with Gesture Control (Hand Tracking)

A spaceship game developed in **Godot** controlled via computer vision using **Python** and **MediaPipe**. Move your hand in front of the webcam to pilot the spaceship.

![Game Demo](LINK_TO_YOUR_GIF_HERE.gif)

## How it works
The system consists of two independent parts communicating via **UDP**:
1.  **Python:** Captures video, detects hand position, and sends `(x, y)` coordinates.
2.  **Godot:** Listens on a local port and translates coordinates into player movement.

## Requirements
* Python 3.8+
* Webcam
* Godot Engine 4.3 (to edit the game)

## Installation and Usage

### 1. Start the Controller
```bash
cd Python_Controller
pip install -r requirements.txt
python hand_detector.py
