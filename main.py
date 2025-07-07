# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ultralytics import YOLO
import cv2, time, os

app = FastAPI()

# ✅ CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ YOLO 모델 로딩 (1회만)
model = YOLO("yolov8n.pt")

# ✅ 정적 파일 mount (예: /static/index.html)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ✅ 루트(/) 접속 시 index.html 반환
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

# ✅ /count API (사람 수 추론)
@app.get("/count")
def count_people():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if not ret:
        return {"error": "캡처 실패"}

    start = time.time()
    results = model.predict(source=frame, conf=0.3, classes=[0], imgsz=416, verbose=False)
    end = time.time()

    count = (results[0].boxes.cls == 0).sum().item()
    return {"count": count, "inference_time": round(end - start, 3)}
