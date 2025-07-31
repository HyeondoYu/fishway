from flask import Flask, render_template, send_file, jsonify
import subprocess
import os
import threading
import time

app = Flask(__name__)

# HLS 파일 저장 디렉토리
HLS_DIR = '/tmp/hls'
RTSP_URL = "rtsp://192.168.0.69:8554/unicast"

# FFmpeg 프로세스를 저장할 변수
ffmpeg_process = None

def create_hls_directory():
    """HLS 파일을 저장할 디렉토리 생성"""
    if not os.path.exists(HLS_DIR):
        os.makedirs(HLS_DIR)

def start_ffmpeg():
    """FFmpeg로 RTSP를 HLS로 변환"""
    global ffmpeg_process
    
    create_hls_directory()
    
    # FFmpeg 명령어 (부드러운 스트리밍을 위한 최적화)
    cmd = [
        'ffmpeg',
        '-i', RTSP_URL,
        '-c:v', 'libx264',           # 비디오 코덱
        '-c:a', 'aac',               # 오디오 코덱
        '-preset', 'veryfast',       # 빠른 인코딩 (ultrafast보다 품질 좋음)
        '-tune', 'zerolatency',      # 낮은 지연시간
        '-vf', 'transpose=1',        # 90도 시계방향 회전
        '-g', '30',                  # GOP 크기 (키프레임 간격)
        '-keyint_min', '30',         # 최소 키프레임 간격
        '-sc_threshold', '0',        # 장면 변화 감지 비활성화
        '-f', 'hls',                 # HLS 포맷
        '-hls_time', '1',            # 세그먼트 길이를 1초로 단축
        '-hls_list_size', '5',       # 플레이리스트에 더 많은 세그먼트 유지
        '-hls_flags', 'delete_segments+independent_segments', # 독립적인 세그먼트
        '-hls_allow_cache', '0',     # 캐시 비활성화
        '-hls_segment_type', 'mpegts', # 세그먼트 타입
        '-force_key_frames', 'expr:gte(t,n_forced*1)', # 1초마다 강제 키프레임
        f'{HLS_DIR}/stream.m3u8',
        '-y'                         # 덮어쓰기 허용
    ]
    
    try:
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("FFmpeg HLS 변환 시작됨")
        return True
    except Exception as e:
        print(f"FFmpeg 시작 실패: {e}")
        return False

def stop_ffmpeg():
    """FFmpeg 프로세스 종료"""
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.terminate()
        ffmpeg_process.wait()
        ffmpeg_process = None
        print("FFmpeg 프로세스 종료됨")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream.m3u8')
def hls_playlist():
    """HLS 플레이리스트 파일 제공"""
    playlist_path = f'{HLS_DIR}/stream.m3u8'
    if os.path.exists(playlist_path):
        return send_file(playlist_path, mimetype='application/vnd.apple.mpegurl')
    else:
        return "Playlist not found", 404

@app.route('/stream<path:filename>')
def hls_segment(filename):
    """HLS 세그먼트 파일 제공"""
    segment_path = f'{HLS_DIR}/stream{filename}'
    if os.path.exists(segment_path):
        return send_file(segment_path, mimetype='video/mp2t')
    else:
        return "Segment not found", 404

@app.route('/api/stream/status')
def stream_status():
    """스트림 상태 확인"""
    playlist_exists = os.path.exists(f'{HLS_DIR}/stream.m3u8')
    return jsonify({
        'status': 'active' if playlist_exists else 'inactive',
        'ffmpeg_running': ffmpeg_process is not None and ffmpeg_process.poll() is None
    })

@app.route('/api/stream/start')
def start_stream():
    """스트림 시작"""
    if start_ffmpeg():
        return jsonify({'status': 'started'})
    else:
        return jsonify({'status': 'failed'}), 500

@app.route('/api/stream/stop')
def stop_stream():
    """스트림 중지"""
    stop_ffmpeg()
    return jsonify({'status': 'stopped'})

def monitor_ffmpeg():
    """FFmpeg 프로세스 모니터링 및 자동 재시작"""
    while True:
        time.sleep(10)  # 10초마다 체크
        if ffmpeg_process and ffmpeg_process.poll() is not None:
            print("FFmpeg 프로세스가 종료됨. 재시작 시도...")
            time.sleep(2)
            start_ffmpeg()

if __name__ == '__main__':
    # FFmpeg 시작
    start_ffmpeg()
    
    # FFmpeg 모니터링 스레드 시작
    monitor_thread = threading.Thread(target=monitor_ffmpeg, daemon=True)
    monitor_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # 애플리케이션 종료 시 FFmpeg 정리
        stop_ffmpeg()