from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # 미리 로드

def infer_people_count(frame):
    results = model.predict(source=frame, conf=0.3, classes=[0], imgsz=416, verbose=False)
    return (results[0].boxes.cls == 0).sum().item()
