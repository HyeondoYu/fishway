import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

LED_UP_PIN = 17  # GPIO pin for LED up
LED_DOWN_PIN = 2  # GPIO pin for LED down

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_UP_PIN, GPIO.OUT)
GPIO.setup(LED_DOWN_PIN, GPIO.OUT)
GPIO.output(LED_UP_PIN, GPIO.LOW)
GPIO.output(LED_DOWN_PIN, GPIO.LOW)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("fishway/commands")

def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"Received command: {command}")
    
    if command == "up":
        GPIO.output(LED_UP_PIN, GPIO.HIGH)
        GPIO.output(LED_DOWN_PIN, GPIO.LOW)
    elif command == "down":
        GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
        GPIO.output(LED_UP_PIN, GPIO.LOW)
    else:
        print("Unknown command")

# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()