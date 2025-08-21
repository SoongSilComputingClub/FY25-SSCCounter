from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np, cv2, time, asyncio
from app.services.yolo_inference import infer_people_count
from datetime import datetime
import os, csv

router = APIRouter()
esp32_socket = None
pending_client = None  # 현재 응답 대기 중인 사용자 WebSocket

@router.websocket("/v2/ws/esp32")
async def esp32_looped_handler(websocket: WebSocket):
    global esp32_socket, pending_client
    esp32_socket = websocket
    await websocket.accept()
    print("📡 ESP32 Connected")
   
    try:
        while True:
            msg = await websocket.receive_json()
            if msg.get("status") == "ready":
                print("📥 ESP32 ready")

                # "ready" 수신 후 무한 루프 진입
                while True:
                    if pending_client:
                        await esp32_socket.send_text("start")  # ESP32에게 사진 요청
                        print("📤 Sent start to ESP32")

                        # ESP32로부터 사진 수신
                        data = await esp32_socket.receive_bytes()
                        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

                        if frame is not None:
                            start = time.time()
                            count = infer_people_count(frame)
                            inference_time = round(time.time() - start, 3)

                            # ✅ 클라이언트 응답
                            await pending_client.send_json({
                                "count": count,
                                "inference_time": inference_time
                            })
                            print(f"✅ Inference sent to client: {count}명")

                            # ✅ 로그 저장
                            log_result(count, inference_time)

                        else:
                            await pending_client.send_json({"error": "이미지 디코딩 실패"})

                        pending_client = None

                    await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("❌ ESP32 Disconnected")
        esp32_socket = None


# ✅ 로그 저장 함수
def log_result(count: int, inference_time: float):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/count_log.csv"
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["timestamp", "count", "inference_time_sec"])
        writer.writerow([log_time, count, inference_time])
