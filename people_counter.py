# people_counter.py

import torch
import cv2
import uuid
import os

# 1. YOLOv5n 모델 로드 (사람 클래스만 검출)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model.conf = 0.3  # 신뢰도 threshold
model.classes = [0]  # class 0: person

# 2. 사진 저장 디렉토리 만들기
os.makedirs("images", exist_ok=True)
img_path = f"images/{uuid.uuid4().hex}.jpg"

# 3. 카메라로 한 장 찍기
cam = cv2.VideoCapture(0)

cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 수동 노출
cam.set(cv2.CAP_PROP_EXPOSURE, -4)         # 노출값: -1이 밝고 -8이 어두움

if not cam.isOpened():
    raise RuntimeError("카메라 열기 실패")
ret, frame = cam.read()
cam.release()

if not ret:
    raise RuntimeError("프레임 캡처 실패")
cv2.imwrite(img_path, frame)
print(f"[INFO] 이미지 저장됨: {img_path}")

# 4. YOLOv5로 사람 수 검출
results = model(img_path)
people = results.pred[0]  # tensor [x1, y1, x2, y2, conf, class]
count = (people[:, 5] == 0).sum().item()

# 5. 결과 출력
print(f"[RESULT] 사람 수: {count}명")