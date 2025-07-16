from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
config = picam2.create_preview_configuration(
   main={"size": (1920, 1080), "format":"RGB888"},
        controls = {"FrameDurationLimits": (50000,50000)},
        buffer_count = 4
    )

picam2.configure(config)
picam2.start()
time.sleep(1)

while True:
    frame = picam2.capture_array()
    #rotated = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow("Rotated Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
