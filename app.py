from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from camera import generate_frames
from control import handle_command

app = Flask(__name__)
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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
