from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .esp32_handler import esp32_socket, pending_client

router = APIRouter()

@router.websocket("/v2/ws/client")
async def client_handler(websocket: WebSocket):
    global pending_client
    await websocket.accept()
    print("🧑 Client Connected")

    try:
        while True:
            message = await websocket.receive_text()
            if message == "capture" and esp32_socket:
                pending_client = websocket
                await esp32_socket.send_text("start")  # 👉 ESP32에게 요청 즉시 전달
                print("📤 capture 요청 → ESP32에게 start 전송")
            else:
                await websocket.send_json({"error": "ESP32 연결 안됨 또는 잘못된 요청"})
    except WebSocketDisconnect:
        print("👋 Client Disconnected")
        if pending_client == websocket:
            pending_client = None
