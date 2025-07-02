# 사진 저장 X + yolov8n 사용
# 4초대로 향상

from ultralytics import YOLO
import cv2
import time

model = YOLO("yolov8n.pt")  

def count_people(model):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if not ret:
        raise RuntimeError("카메라 캡처 실패")

    start = time.time()
    results = model.predict(source=frame, conf=0.3, classes=[0], verbose=False)
    boxes = results[0].boxes
    count = (boxes.cls == 0).sum().item()
    end = time.time()

    print(f"[RESULT] 사람 수: {count}명")
    print(f"[INFO] 추론 시간: {end - start:.3f}초")

count_people(model)
