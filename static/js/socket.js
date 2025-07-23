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

// 제어 버튼 이벤트
// HTTP fetch를 사용해서 flask 서버로 전송하는 방법
// document.getElementById('up-button').addEventListener('click', function () {
// 	alert('상승 명령이 전송되었습니다.');
// 	fetch('/control/up')
// 		.then(response => response.text())
// 		.then(result => console.log(result));
// });

// document.getElementById('down-button').addEventListener('click', function () {
// 	alert('하강 명령이 전송되었습니다.');
// 	fetch('/control/down')
// 		.then(response => response.text())
// 		.then(result => console.log(result));
// });

// document.getElementById('stop-button').addEventListener('click', function () {
// 	alert('정지 명령이 전송되었습니다.');
// 	fetch('/control/up')
// 		.then(response => response.text())
// 		.then(result => console.log(result));
// });

// MQTT over WebSocket을 사용해서 실시간으로 명령을 전송하는 방법
const client = MediaQueryListEvent.connect('ws://192.168.0.69:9001');

client.on('connect', () => {
	console.log('MQTT connected!');
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
updateTime();
updateWaterLevel();