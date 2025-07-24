import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

# 핀 설정
pins = {
    14: '상승 밸브',
    15: '하강 밸브',
    18: '압력 스위치',
    23: '유압유 부족',
    24: '모터 과부하'
}

# MQTT 설정
client = mqtt.Client()
client.connect("localhost", 1883, 60)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.IN)

def publish_status():
    status = {}
    for pin, name in pins.items():
        state = GPIO.input(pin)
        status[name] = state
    client.publish("fishway/status", str(status))

try:
    while True:
        publish_status()
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
