import cv2
import time
import threading
from queue import Queue
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RTSP_URL = "rtsp://192.168.0.71:8554/unicast"

class RTSPStreamer:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.frame_queue = Queue(maxsize=2)
        self.cap = None
        self.running = False
        self.capture_thread = None
        self.lock = threading.Lock()
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
    def connect_to_stream(self):
        """RTSP 스트림에 연결"""
        with self.lock:
            if self.cap:
                self.cap.release()
            
            logger.info(f"RTSP 연결 시도: {self.rtsp_url}")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # OpenCV 설정
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # 연결 테스트
            ret, _ = self.cap.read()
            if ret:
                logger.info("RTSP 연결 성공")
                self.connection_attempts = 0
                return True
            else:
                logger.warning("RTSP 연결 실패")
                self.cap.release()
                self.cap = None
                return False
    
    def start_capture(self):
        """별도 스레드에서 프레임 캡처"""
        self.running = True
        
        while self.running:
            # 연결이 없거나 실패한 경우 재연결 시도
            if not self.cap or not self.cap.isOpened():
                if self.connection_attempts < self.max_connection_attempts:
                    self.connection_attempts += 1
                    if not self.connect_to_stream():
                        logger.warning(f"재연결 실패 ({self.connection_attempts}/{self.max_connection_attempts})")
                        time.sleep(2)  # 2초 대기 후 재시도
                        continue
                else:
                    logger.error("최대 연결 시도 횟수 초과")
                    time.sleep(5)  # 5초 대기 후 다시 시도
                    self.connection_attempts = 0
                    continue
            
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("프레임 읽기 실패, 재연결 시도")
                self.cap.release()
                self.cap = None
                continue
                
            # 색상 보정
            corrected_frame = frame.copy()
            corrected_frame[:, :, 0] = frame[:, :, 0]
            corrected_frame[:, :, 1] = frame[:, :, 2] 
            corrected_frame[:, :, 2] = frame[:, :, 1]
            
            # 큐 관리
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
            try:
                self.frame_queue.put_nowait(corrected_frame)
            except:
                pass
    
    def get_latest_frame(self):
        """최신 프레임 가져오기"""
        if self.frame_queue.empty():
            return None
            
        frame = None
        while not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get_nowait()
            except:
                break
        return frame
    
    def start(self):
        """캡처 스레드 시작"""
        if self.capture_thread and self.capture_thread.is_alive():
            return  # 이미 실행 중
            
        self.capture_thread = threading.Thread(target=self.start_capture)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop(self):
        """캡처 중지"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
    
    def restart(self):
        """스트리머 재시작"""
        logger.info("스트리머 재시작")
        self.stop()
        time.sleep(1)
        self.start()

# 전역 스트리머 객체
streamer = None

def get_streamer():
    """스트리머 인스턴스 가져오기 (싱글톤 패턴)"""
    global streamer
    if streamer is None:
        streamer = RTSPStreamer(RTSP_URL)
        streamer.start()
    return streamer

def generate_frames():
    """웹 스트리밍용 프레임 생성"""
    jpeg_quality = [cv2.IMWRITE_JPEG_QUALITY, 85]
    frame_count = 0
    no_frame_count = 0
    max_no_frame = 150  # 5초간 프레임이 없으면 재시작 (30fps 기준)
    
    current_streamer = get_streamer()
    
    while True:
        frame = current_streamer.get_latest_frame()
        
        if frame is None:
            no_frame_count += 1
            if no_frame_count >= max_no_frame:
                logger.warning("장시간 프레임 없음, 스트리머 재시작")
                current_streamer.restart()
                no_frame_count = 0
            
            time.sleep(0.033)  # ~30fps
            continue
        
        no_frame_count = 0  # 프레임을 받았으므로 리셋
        frame_count += 1
        
        if frame_count % 300 == 0:  # 10초마다 로그
            logger.info(f"Frame {frame_count} streamed")
        
        # JPEG 인코딩
        ret, buffer = cv2.imencode('.jpg', frame, jpeg_quality)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# 정리 함수
def cleanup():
    """애플리케이션 종료 시 정리"""
    global streamer
    if streamer:
        streamer.stop()
        streamer = None