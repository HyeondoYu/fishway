import paho.mqtt.client as mqtt

# MQTT broker settings
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'fishway/commands'

def send_command(command):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, command)
    client.disconnect()