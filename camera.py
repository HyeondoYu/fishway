import cv2
import time

RTSP_URL = "rtsp://192.168.0.69:8554/unicast"

def generate_frames():
  cap = None

  while True:
    if cap is None or not cap.isOpened():
      print("Opening RTSP stream...")
      cap = cv2.VideoCapture(RTSP_URL)
      time.sleep(2)  # Wait before retrying
      if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        time.sleep(5)  # Wait before retrying
        continue
    #print("RTSP stream opened successfully.")

    success, frame = cap.read()
    if not success or frame is None:
      print("Failed to capture frame from RTSP stream. Reinitializing...")
      cap.release()
      cap = None
      time.sleep(1)  # Wait before retrying
      continue

    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
      continue

    frame_bytes = buffer.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
