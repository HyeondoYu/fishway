from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from camera import generate_frames
from control import handle_command
import RPi.GPIO as GPIO

app = Flask(__name__)

LED_UP_PIN = 17
LED_DOWN_PIN = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_UP_PIN, GPIO.OUT)
GPIO.setup(LED_DOWN_PIN, GPIO.OUT)
GPIO.output(LED_UP_PIN, GPIO.LOW)
GPIO.output(LED_DOWN_PIN, GPIO.LOW)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype = 'multipart/x-mixed-replace; boundary=fram')


@socketio.on('control')
def handle_control(command):
    handle_command(command)

@app.route('/led/up/on')
def led_up_on():
    GPIO.output(LED_DOWN_PIN, GPIO.LOW)
    GPIO.output(LED_UP_PIN, GPIO.HIGH)
    return 'LED UP ON'

@app.route('/led/up/off')
def led_up_off():
    GPIO.output(LED_UP_PIN, GPIO.LOW)
    return 'LED UP OFF'

@app.route('/led/down/on')
def led_down_on():
    GPIO.output(LED_UP_PIN, GPIO.LOW)
    GPIO.output(LED_DOWN_PIN, GPIO.HIGH)
    return 'LED DOWN ON'

@app.route('/led/down/off')
def led_down_off():
    GPIO.output(LED_DOWN_PIN, GPIO.LOW)
    return 'LED DOWN OFF'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
