from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (900, 1600), "format":"RGB888"},
        buffer_count = 4
    )
)
picam2.start()
time.sleep(1)

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

