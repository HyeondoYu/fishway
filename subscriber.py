import paho.mqtt.client as mqtt
import serial
import time

uart = serial.Serial('/dev/ttyAMA3', 9600, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize

MQTT_BROKER = "192.168.0.71"
MQTT_SUB_TOPIC = "fishway/commands"
MQTT_PUB_TOPIC = "fishway/status"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_SUB_TOPIC)

def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"Received command: {command}")
    
    if command == "up":
        uart.write(b'up\n')
        print("Sent command to move up")
    elif command == "down":
        uart.write(b'down\n')
        print("Sent command to move down")
    elif command == "stop":
        uart.write(b'stop\n')
        print("Sent command to stop")
    else:
        print("Unknown command")
    
    uart.flush()  # Ensure the command is sent immediately

def serial_listener():
    while True:
        if uart.in_waiting > 0:
            line = uart.readline().decode('utf-8').strip()
            print(f"Received from serial: {line}")
            client.publish(MQTT_PUB_TOPIC, line)
        else:
            print("No data in UART buffer, waiting...")

# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
    uart.close()
    client.disconnect()