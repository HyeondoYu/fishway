// HLS 비디오 플레이어 초기화
let hls = null;
let video = document.getElementById('video-player');
let connectionStatus = document.getElementById('connection-status');

function initializeHLS() {
    if (Hls.isSupported()) {
        hls = new Hls({
            debug: false,
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 90
        });
        
        hls.loadSource('/stream.m3u8');
        hls.attachMedia(video);
        
        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            console.log('HLS manifest loaded');
            connectionStatus.textContent = '연결됨';
            connectionStatus.style.backgroundColor = 'rgba(40, 167, 69, 0.8)';
        });
        
        hls.on(Hls.Events.ERROR, function(event, data) {
            console.error('HLS error:', data);
            connectionStatus.textContent = '연결 오류';
            connectionStatus.style.backgroundColor = 'rgba(220, 53, 69, 0.8)';
            
            if (data.fatal) {
                switch(data.type) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        console.log('Network error - attempting to recover');
                        hls.startLoad();
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        console.log('Media error - attempting to recover');
                        hls.recoverMediaError();
                        break;
                    default:
                        console.log('Fatal error - cannot recover');
                        hls.destroy();
                        setTimeout(initializeHLS, 5000); // 5초 후 재시도
                        break;
                }
            }
        });
        
        hls.on(Hls.Events.FRAG_LOADED, function() {
            connectionStatus.textContent = '스트리밍 중';
            connectionStatus.style.backgroundColor = 'rgba(40, 167, 69, 0.8)';
        });
        
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari는 네이티브 HLS 지원
        video.src = '/stream.m3u8';
        video.addEventListener('loadedmetadata', function() {
            console.log('Native HLS loaded');
            connectionStatus.textContent = '연결됨';
            connectionStatus.style.backgroundColor = 'rgba(40, 167, 69, 0.8)';
        });
    } else {
        console.error('HLS is not supported');
        connectionStatus.textContent = 'HLS 미지원';
        connectionStatus.style.backgroundColor = 'rgba(220, 53, 69, 0.8)';
    }
}

// 스트림 상태 확인
async function checkStreamStatus() {
    try {
        const response = await fetch('/api/stream/status');
        const data = await response.json();
        
        const toggleButton = document.getElementById('stream-toggle');
        
        if (data.status === 'active' && data.ffmpeg_running) {
            toggleButton.textContent = '중지';
            toggleButton.classList.remove('inactive');
            toggleButton.classList.add('active');
        } else {
            toggleButton.textContent = '시작';
            toggleButton.classList.remove('active');
            toggleButton.classList.add('inactive');
        }
    } catch (error) {
        console.error('Failed to check stream status:', error);
    }
}

// 스트림 제어
document.getElementById('stream-toggle').addEventListener('click', async function() {
    const isActive = this.classList.contains('active');
    
    try {
        if (isActive) {
            // 스트림 중지
            await fetch('/api/stream/stop');
            if (hls) {
                hls.destroy();
                hls = null;
            }
            video.src = '';
            connectionStatus.textContent = '중지됨';
            connectionStatus.style.backgroundColor = 'rgba(108, 117, 125, 0.8)';
        } else {
            // 스트림 시작
            await fetch('/api/stream/start');
            setTimeout(() => {
                initializeHLS();
            }, 2000); // FFmpeg가 시작될 시간을 기다림
        }
        
        // 상태 업데이트
        setTimeout(checkStreamStatus, 1000);
        
    } catch (error) {
        console.error('Failed to control stream:', error);
    }
});

// 현재 시간 표시
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;
}

// 수위 게이지 업데이트 (데모용)
function updateWaterLevel() {
    const needle = document.getElementById('water-level-needle');
    const levels = [-67.5, -22.5, 22.5, 67.5];
    const randomLevel = levels[Math.floor(Math.random() * levels.length)];
    needle.style.transform = `translateX(-50%) rotate(${randomLevel}deg)`;
}

// 운전 선택 토글
document.getElementById('operation-selector').addEventListener('click', function () {
    const current = this.querySelector('span').textContent;
    if (current === '자동') {
        this.querySelector('span').textContent = '수동';
        this.style.background = 'conic-gradient(#ccc 0deg 180deg, #333 180deg 360deg)';
    } else {
        this.querySelector('span').textContent = '자동';
        this.style.background = 'conic-gradient(#333 0deg 180deg, #ccc 180deg 360deg)';
    }
});

// MQTT over WebSocket을 사용해서 실시간으로 명령을 전송하는 방법
const client = mqtt.connect('ws://192.168.0.69:9001');

client.on('connect', () => {
    console.log('MQTT connected!');
    client.subscribe("fishway/status");
});

client.on('message', (topic, message) => {
    try {
        const data = JSON.parse(message.toString().replace(/'/g, '"'));
        for (const key in data) {
            const isActive = data[key] === 1;
            const item = document.querySelector(`.status-item[data-key="${key}"] .status-icon`);
            if (item) {
                item.classList.toggle('active', isActive);
            }
        }
    } catch (e) {
        console.error("Failed to parse message:", e);
    }
});

document.getElementById('up-button').addEventListener('click', function () {
    alert('상승 명령이 전송되었습니다.');
    client.publish('fishway/commands', 'up');
});

document.getElementById('down-button').addEventListener('click', function () {
    alert('하강 명령이 전송되었습니다.');
    client.publish('fishway/commands', 'down');
});

document.getElementById('stop-button').addEventListener('click', function () {
    alert('정지 명령이 전송되었습니다.');
    client.publish('fishway/commands', 'stop');
});

// 초기화
setInterval(updateTime, 1000);
setInterval(updateWaterLevel, 3000);
setInterval(checkStreamStatus, 5000); // 5초마다 스트림 상태 확인

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    updateWaterLevel();
    checkStreamStatus();
    
    // 2초 후 HLS 초기화 (서버 시작 대기)
    setTimeout(() => {
        initializeHLS();
    }, 2000);
});

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    if (hls) {
        hls.destroy();
    }
});