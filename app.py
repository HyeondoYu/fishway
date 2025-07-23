from flask import Flask, render_template, Response
from control import send_command
from camera import generate_frames

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# MQTT for sending commands
@app.route('/control/<direction>', methods=['GET'])
def control(direction):
    if direction in ['up', 'down']:
        send_command(direction)
        return {'status': 'success', 'message': f'Command {direction.upper()} sent via MQTT.'}
    else:
        return {'status': 'error', 'message': 'Invalid command.'}, 400

# Route for video streaming
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=5000)
