from flask import Flask, render_template, Response
import atexit
from camera import generate_frames, cleanup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/restart_stream')
def restart_stream():
    """스트림 재시작 엔드포인트"""
    from camera import get_streamer
    streamer = get_streamer()
    streamer.restart()
    return "Stream restarted"

# 애플리케이션 종료 시 정리
atexit.register(cleanup)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, threaded=True, debug=False)
    finally:
        cleanup()