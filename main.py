from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ultralytics import YOLO
import cv2, time, os
from datetime import datetime
import csv

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

# ✅ 정적 파일 mount
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ✅ 루트(/) 접속 시 index.html 반환
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

# ✅ 로그 저장 함수
def log_result(count: int, inference_time: float):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/count_log.csv"
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # 헤더가 없으면 첫 줄에 추가
        if f.tell() == 0:
            writer.writerow(["timestamp", "count", "inference_time_sec"])
        writer.writerow([log_time, count, inference_time])

# ✅ /count API (사람 수 추론 + 로그 저장)
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
    inference_time = round(end - start, 3)

    log_result(count, inference_time)  # 🔥 로그 저장 호출

    return {"count": count, "inference_time": inference_time}
