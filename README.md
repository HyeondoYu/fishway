##파일 구조
```
project_root/
├── app.py                      # Flask 서버 실행 메인 파일
├── camera.py                   # 카메라 캡처 로직 (OpenCV)
├── control.py                  # 제어 신호 처리 로직
├── templates/
│   └── index.html              # Jinja2 템플릿: 영상 스트리밍 + 버튼 UI
├── static/
│   └── js/
│       └── socket.js           # SocketIO 클라이언트 스크립트
└── requirements.txt            # 설치 패키지 목록
```
