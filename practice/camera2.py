from picamera2 import Picamera2

picam2 = Picamera2()

video_modes = picam2.sensor_modes

for i, mode in enumerate(video_modes):
    print(f"[{i}] Resolution: {mode['size']}, Format: {mode['format']}, FPS: {mode['fps']}")
