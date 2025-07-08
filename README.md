# 👥 SSCCounter - 동방 인원 확인 웹 페이지

**SSCCounter**는 숭실대학교 컴퓨터 동아리 **SSCC**의 동방(동아리방)에  
**현재 몇 명이 있는지 외부에서 간편하게 확인**할 수 있도록 만든 웹 기반 사람 수 카운팅 시스템입니다.

YOLOv8 모델을 활용하여 카메라로 촬영한 이미지를 실시간으로 분석하고,  
**사람 수를 빠르게 추론하여 웹 페이지에 표시**합니다.

---

## 📌 프로젝트 개요

- 🎯 동방 내부 인원을 외부에서 확인
- 🔐 보안을 위해 **사진 저장 없이 메모리 내 실시간 분석만 수행**
- 📸 버튼 클릭으로 카메라 한 장 촬영 후 YOLOv8로 추론
- 🌐 웹 UI + FastAPI API 구조로 누구나 쉽게 사용 가능

---

## 📁 프로젝트 구조

<pre>
SSCCounter/
├── main.py              # FastAPI 백엔드 서버 및 YOLOv8 추론
├── frontend/
│   └── index.html       # 사용자 인터페이스 (버튼 및 결과 표시)
├── yolov8n.pt           # 사전학습 모델 (최초 실행 시 자동 다운로드)
└── requirements.txt     # 설치해야 할 의존성 목록
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

* 웹 프론트: [http://localhost:8000/](http://localhost:8000/)
* API 테스트: [http://localhost:8000/count](http://localhost:8000/count)

---

## 💻 사용 방법

1. 웹에서 **"동방 인원 확인"** 버튼을 클릭
2. 카메라로 자동 촬영된 이미지에서 사람 감지
3. 인원 수와 처리 시간 화면에 표시

---

## 📦 기술 스택

| 구분     | 기술                      |
| ------ | ----------------------- |
| 백엔드    | FastAPI, Uvicorn        |
| 모델     | YOLOv8n (`ultralytics`) |
| 이미지 처리 | OpenCV                  |
| 프론트엔드  | HTML, JavaScript        |
| 기타     | Python 3.x, CORS 설정 포함  |

---

## 🔐 보안 관련 주의사항

* 이미지는 디스크에 저장하지 않습니다.
* 카메라에서 촬영된 프레임은 **즉시 메모리에서 처리 및 폐기**됩니다.
* 외부에 이미지가 남지 않도록 설계되었습니다.

---

## 🧪 API 예시 응답

```json
{
  "count": 3,
  "inference_time": 0.412
}
```

---

## 💡 향후 개선 방향

* 감지된 사람의 위치 시각화 (박스 렌더링)
* 추론 결과 이미지 클라이언트에 시각적으로 표시
* 자동 측정 및 시간별 인원 통계 저장
* 관리자용 대시보드 추가

---

## 👨‍💻 개발자 소개

* **권나현**
> - 숭실대학교 AI융합학부
> - SSCC(숭실대학교 컴퓨터 동아리) 41기 멤버
> - 컴퓨터비전, 임베디드 시스템, 실시간 AI 응용에 관심이 많습니다.

---

## 🏫 SSCC 소개
**SSCC (Soongsil Computer Club)**
> 숭실대학교의 대표적인 컴퓨터 동아리로,
> 개발 · 알고리즘 · AI · 임베디드 등 다양한 분야에 열정을 가진 학우들이 함께 공부하고 프로젝트를 진행합니다.

---

## 📄 라이선스

MIT License (또는 사용 목적에 맞게 자유롭게 설정하세요)

---

## 🙏 Special Thanks

* YOLOv8 by [Ultralytics](https://github.com/ultralytics/ultralytics)
* 숭실대학교 SSCC 멤버들
