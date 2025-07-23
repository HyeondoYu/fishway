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
document.getElementById('up-button').addEventListener('click', function () {
	alert('상승 명령이 전송되었습니다.');
	fetch('/control/up')
		.then(response => response.text())
		.then(result => console.log(result));
});

document.getElementById('down-button').addEventListener('click', function () {
	alert('하강 명령이 전송되었습니다.');
	fetch('/control/down')
		.then(response => response.text())
		.then(result => console.log(result));
});

// 토글 버튼들
const toggleButtons = ['pump-power', 'light-control', 'alarm-reset'];
toggleButtons.forEach(id => {
	document.getElementById(id).addEventListener('click', function () {
		if (this.classList.contains('active')) {
			this.classList.remove('active');
			this.classList.add('inactive');
			this.textContent = 'OFF';
		} else {
			this.classList.remove('inactive');
			this.classList.add('active');
			this.textContent = 'ON';
		}
	});
});

// 초기화
setInterval(updateTime, 1000);
setInterval(updateWaterLevel, 3000);
updateTime();
updateWaterLevel();