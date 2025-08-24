# 👥 SSCCounter - 동방 인원 확인 시스템

**SSCCounter**는 숭실대학교 컴퓨터 동아리 **SSCC**의 동방(동아리방)에 **현재 몇 명이 있는지 외부에서 간편하게 확인**할 수 있도록 만든 웹 기반 사람 수 카운팅 시스템입니다.

ESP32-CAM 모듈에서 촬영한 이미지를 FastAPI 서버가 가져와,
YOLOv8 모델을 통해 **사람 수를 추론하고 웹 UI에 표시**합니다.

---

## 📌 주요 특징

 -📸 **ESP32-CAM 연동**: 카메라 모듈에서 `/capture` HTTP 서버로 사진 요청
- 🤖 **YOLOv8n 모델**로 경량·실시간 인원 수 추론
- 🌐 **웹 UI + FastAPI 백엔드** 구조
- 🕒 **실시간 WebSocket 통신**: 버튼 클릭 시 추론 요청 → 결과 반환
- 🗂 **로그 기록 및 시각화**: CSV 저장 + Chart.js 기반 그래프
- 🖼 선택적으로 **추론 오버레이 이미지 저장** (환경 변수로 on/off)

---

## 📁 프로젝트 구조

<pre>
SSCCounter/
├── app/
│   ├── esp32.py           # ESP32-CAM 캡처 이미지 요청
│   ├── inference.py       # YOLOv8 추론 로직
│   └── log_handler.py     # 로그 페이지 라우터
├── frontend/
│   ├── index.html         # 메인 UI (버튼/결과)
│   ├── logs.html          # 로그 시각화 UI (Chart.js)
│   ├── styles/            # CSS 파일들
│   └── scripts/           # JS 파일들
├── logs/
│   ├── count_log.csv      # 추론 로그 (timestamp, count, source, overlay_url)
│   └── overlays/          # 오버레이 저장 폴더
├── yolov8n.pt             # YOLOv8 모델 가중치
├── main.py                # FastAPI 서버 엔트리포인트
├── .env                   # 환경변수 설정
├── .env.example           # 환경변수 샘플
└── requirements.txt       # 의존성 패키지
</pre>

---

## ⚙️ 환경 변수 (.env)

`.env.example` 참고하여 `.env` 파일 작성:

<pre>
ESP32_URL=http://192.168.0.xxx/capture   # ESP32-CAM /capture 엔드포인트
MODEL_PATH=./yolov8n.pt                  # YOLO 모델 경로
CONF_THRES=0.5                           # confidence threshold
IMG_SIZE=640                             # 입력 이미지 크기

OVERLAY_SAVE=1                           # 1=저장, 0=저장 안함
OVERLAY_DIR=logs/overlays                # 오버레이 저장 경로
</pre>

---

## 🚀 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
````

### 2. 서버 실행

```bash
uvicorn main:app --reload
```

### 3. 접속 경로

* 웹 UI: [http://localhost:8000/](http://localhost:8000/)
* 로그 페이지: [http://localhost:8000/logs](http://localhost:8000/count)
* WebSocket 엔드포인트: `/v2/ws/client`
---

## 💻 사용 흐름

1. 사용자가 웹에서 "**동방 인원 확인**" 버튼 클릭
2. FE → BE WebSocket `"capture"` 전송
3. BE가 ESP32 `/capture` 호출 → JPEG 수신
4. YOLOv8으로 추론 → **사람 수 + 처리시간 반환**
5. 결과는 웹 UI에 즉시 표시
6. 로그는 CSV에 저장되고, `/logs`에서 Chart.js 그래프로 확인 가능
7. 옵션 활성화 시 **오버레이 이미지 저장/링크 제공**

---

## 📦 기술 스택

| 구분  | 기술                                |
| --- | --------------------------------- |
| 백엔드 | FastAPI, Uvicorn, httpx           |
| 모델  | YOLOv8n (`ultralytics`), PyTorch  |
| 이미지 | Pillow, OpenCV (headless)         |
| 데이터 | Pandas, CSV 기반 로깅                 |
| 프론트 | HTML, CSS, JavaScript, Chart.js   |
| 기타  | WebSocket, python-dotenv, CORS 설정 |

---

## 🧪 WebSocket 응답 예시

```json
{
  "count": 3,
  "inference_time": 0.412,
  "overlay_url": "/media/overlays/20250825_053921_count3.jpg"
}
```

---

## 💡 향후 개선 방향

* 관리자 대시보드 (사용자 관리, 통계 조회)
* DB(MariaDB/InfluxDB) 연동으로 장기 통계 관리
* 모바일 최적화 UI

---

## 👨‍💻 개발자 소개

* **권나현 (AI, BE, FE)**
> - 숭실대학교 AI융합학부
> - SSCC(숭실대학교 컴퓨터 동아리) 41기 멤버
> - 컴퓨터비전, 임베디드 시스템, 실시간 AI 응용에 관심이 많습니다.

* **원영진 (EM, BE)**
> - 숭실대학교 AI융합학부
> - SSCC(숭실대학교 컴퓨터 동아리) 40기 멤버
> -  임베디드 시스템, AIoT에 관심이 많습니다.

---

## 🏫 SSCC 소개
**SSCC (Soongsil Computer Club)**
> 숭실대학교의 대표적인 컴퓨터 동아리로,
> 개발 · 알고리즘 · AI · 임베디드 등 다양한 분야에 열정을 가진 학우들이 함께 공부하고 프로젝트를 진행합니다.

---

## 📄 라이선스

MIT License

---

## 🙏 Special Thanks

* YOLOv8 by [Ultralytics](https://github.com/ultralytics/ultralytics)
* 숭실대학교 SSCC 멤버들
